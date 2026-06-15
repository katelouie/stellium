"""
Tests for Swiss Ephemeris path resolution.

Covers the precedence rules for picking the ephemeris directory:

    explicit argument > STELLIUM_EPHE_PATH env var > ~/.stellium/ephe/

and the behavior of ``SwissEphemerisEngine(ephe_path=...)``.

These tests mutate process-global state (the ``swe.set_ephe_path``
global and ``stellium.data.paths._ephe_initialized``). The
``reset_ephemeris_state`` fixture snapshots and restores both so the
rest of the test session is unaffected.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import swisseph as swe

from stellium.data import paths as ephe_paths
from stellium.data.paths import (
    ENV_EPHE_PATH,
    USER_EPHE_DIR,
    get_ephe_dir,
    has_ephe_file,
    initialize_ephemeris,
    reset_ephe_initialization,
)
from stellium.engines.ephemeris import SwissEphemerisEngine


@pytest.fixture
def reset_ephemeris_state(monkeypatch):
    """Save and restore ephemeris global state around a single test."""
    saved_initialized = ephe_paths._ephe_initialized
    saved_active = ephe_paths._active_ephe_dir
    monkeypatch.delenv(ENV_EPHE_PATH, raising=False)
    reset_ephe_initialization()
    try:
        yield
    finally:
        ephe_paths._ephe_initialized = saved_initialized
        ephe_paths._active_ephe_dir = saved_active
        # Restore the default Swiss Ephemeris path so subsequent tests that
        # rely on the standard directory still work.
        swe.set_ephe_path(str(USER_EPHE_DIR) + os.sep)


def _populate_minimal_ephe(directory: Path) -> None:
    """Copy just enough bundled files into ``directory`` to satisfy a chart.

    We only need to pretend this is a real ephemeris folder; the actual
    presence of the core ``.se1`` files is what matters for
    ``has_ephe_file`` assertions.
    """
    for filename in ephe_paths.ESSENTIAL_EPHE_FILES:
        src = USER_EPHE_DIR / filename
        if src.exists():
            (directory / filename).write_bytes(src.read_bytes())


# ---------------------------------------------------------------------------
# initialize_ephemeris resolution rules
# ---------------------------------------------------------------------------


def test_default_initialization_uses_user_ephe_dir(reset_ephemeris_state):
    """With no overrides the default ~/.stellium/ephe/ is used."""
    result = initialize_ephemeris()
    assert result == USER_EPHE_DIR
    assert get_ephe_dir() == USER_EPHE_DIR


def test_explicit_path_overrides_default(reset_ephemeris_state, tmp_path):
    """An explicit ephe_path argument wins over the default."""
    custom = tmp_path / "my_ephe"
    custom.mkdir()

    result = initialize_ephemeris(custom)

    assert result == custom
    assert get_ephe_dir() == custom


def test_env_var_overrides_default(reset_ephemeris_state, tmp_path, monkeypatch):
    """STELLIUM_EPHE_PATH is honored when no explicit arg is given."""
    custom = tmp_path / "env_ephe"
    custom.mkdir()
    monkeypatch.setenv(ENV_EPHE_PATH, str(custom))

    result = initialize_ephemeris()

    assert result == custom
    assert get_ephe_dir() == custom


def test_explicit_path_beats_env_var(reset_ephemeris_state, tmp_path, monkeypatch):
    """Explicit argument takes precedence over STELLIUM_EPHE_PATH."""
    from_arg = tmp_path / "arg_ephe"
    from_env = tmp_path / "env_ephe"
    from_arg.mkdir()
    from_env.mkdir()
    monkeypatch.setenv(ENV_EPHE_PATH, str(from_env))

    result = initialize_ephemeris(from_arg)

    assert result == from_arg
    assert get_ephe_dir() == from_arg


def test_custom_path_expands_user(reset_ephemeris_state, tmp_path, monkeypatch):
    """~ in a custom path is expanded via Path.expanduser()."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    # Set HOME for Unix and USERPROFILE for Windows
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))

    result = initialize_ephemeris("~/custom_ephe")

    assert result == fake_home / "custom_ephe"


def test_custom_path_does_not_create_directory(reset_ephemeris_state, tmp_path):
    """Custom paths are used as-is; Stellium must not create or populate them."""
    nonexistent = tmp_path / "not_there_yet"
    # The directory should stay missing; only a warning is emitted.
    result = initialize_ephemeris(nonexistent)

    assert result == nonexistent
    assert not nonexistent.exists()


def test_custom_path_does_not_copy_bundled_files(reset_ephemeris_state, tmp_path):
    """Custom directories are left untouched — no bundled file copying."""
    custom = tmp_path / "clean_ephe"
    custom.mkdir()

    initialize_ephemeris(custom)

    # None of the bundled essentials should have been copied in.
    for filename in ephe_paths.ESSENTIAL_EPHE_FILES:
        assert not (custom / filename).exists(), (
            f"{filename} was unexpectedly copied into custom path"
        )


def test_reinitialization_with_different_path(reset_ephemeris_state, tmp_path):
    """Calling initialize_ephemeris twice with different paths switches."""
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()

    initialize_ephemeris(first)
    assert get_ephe_dir() == first

    initialize_ephemeris(second)
    assert get_ephe_dir() == second


def test_reinitialization_with_same_path_is_noop(reset_ephemeris_state, tmp_path):
    """Re-initializing with the same path is a cheap no-op."""
    custom = tmp_path / "stable"
    custom.mkdir()

    first = initialize_ephemeris(custom)
    second = initialize_ephemeris(custom)

    assert first == second == custom


# ---------------------------------------------------------------------------
# has_ephe_file respects the active directory
# ---------------------------------------------------------------------------


def test_has_ephe_file_checks_active_directory(reset_ephemeris_state, tmp_path):
    """has_ephe_file should query the directory we're currently pointed at."""
    custom = tmp_path / "has_ephe"
    custom.mkdir()
    (custom / "se136199.se1").write_bytes(b"")

    initialize_ephemeris(custom)

    assert has_ephe_file("se136199.se1") is True
    assert has_ephe_file("does_not_exist.se1") is False


# ---------------------------------------------------------------------------
# SwissEphemerisEngine plumbing
# ---------------------------------------------------------------------------


def test_engine_accepts_explicit_path(reset_ephemeris_state, tmp_path):
    """SwissEphemerisEngine(ephe_path=...) routes through initialize_ephemeris."""
    custom = tmp_path / "engine_ephe"
    custom.mkdir()
    _populate_minimal_ephe(custom)

    engine = SwissEphemerisEngine(ephe_path=custom)

    assert engine._ephe_path == custom
    assert get_ephe_dir() == custom


def test_engine_respects_env_var(reset_ephemeris_state, tmp_path, monkeypatch):
    """SwissEphemerisEngine() honors STELLIUM_EPHE_PATH when no arg is given."""
    custom = tmp_path / "env_engine_ephe"
    custom.mkdir()
    _populate_minimal_ephe(custom)
    monkeypatch.setenv(ENV_EPHE_PATH, str(custom))

    SwissEphemerisEngine()

    assert get_ephe_dir() == custom


def test_engine_calculates_against_custom_path(reset_ephemeris_state, tmp_path):
    """End-to-end: a chart calculated against a populated custom path works."""
    from datetime import UTC, datetime

    from stellium.core.builder import ChartBuilder
    from stellium.core.models import ChartLocation
    from stellium.core.native import Native

    custom = tmp_path / "live_ephe"
    custom.mkdir()
    _populate_minimal_ephe(custom)

    native = Native(
        datetime(2000, 1, 1, 12, 0, tzinfo=UTC),
        ChartLocation(latitude=0.0, longitude=0.0, name="Null Island"),
    )
    chart = (
        ChartBuilder.from_native(native)
        .with_ephemeris(SwissEphemerisEngine(ephe_path=custom))
        .calculate()
    )

    sun = chart.get_object("Sun")
    assert sun is not None
    # Sun should be in Capricorn (around 280°) on Jan 1 2000 at noon UTC
    assert 270.0 <= sun.longitude <= 290.0
