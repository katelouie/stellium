"""Phase 0 infrastructure tests for the diagnostics/logging system.

Covers the logging scaffolding and warning hierarchy added in
``docs/development/specs/STRUCTURED_LOGGING_SPEC.md`` Phase 0 -- no behavior
change to existing diagnostics yet, just the plumbing they will migrate onto.
"""

import logging

import pytest

import stellium
from stellium._logging import configure_logging, get_logger
from stellium.exceptions import (
    ConfigurationWarning,
    DataQualityWarning,
    GeocodingWarning,
    MissingEphemerisWarning,
    StelliumWarning,
)

_ROOT = "stellium"


@pytest.fixture
def restore_stellium_logger():
    """Snapshot and restore the ``stellium`` logger's handlers/level.

    ``configure_logging`` mutates global logging state; without this, one test
    would leak a StreamHandler into every later test.
    """
    root = logging.getLogger(_ROOT)
    handlers = list(root.handlers)
    level = root.level
    yield root
    root.handlers = handlers
    root.setLevel(level)


# === Logger scaffolding =====================================================


def test_root_logger_has_null_handler():
    """The package attaches a NullHandler so it is silent by default."""
    handlers = logging.getLogger(_ROOT).handlers
    assert any(isinstance(h, logging.NullHandler) for h in handlers)


def test_get_logger_returns_root_and_children():
    assert get_logger() is logging.getLogger("stellium")
    assert get_logger("") is logging.getLogger("stellium")
    assert get_logger("utils.cache") is logging.getLogger("stellium.utils.cache")
    # A child propagates to the stellium root.
    assert get_logger("io.csv").name == "stellium.io.csv"


def test_configure_logging_attaches_handler_and_level(restore_stellium_logger):
    root = restore_stellium_logger
    before = len(root.handlers)

    returned = configure_logging("DEBUG")

    assert returned is root
    assert root.level == logging.DEBUG
    assert len(root.handlers) == before + 1
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)


def test_configure_logging_accepts_numeric_level_and_stream(
    restore_stellium_logger,
):
    import io

    buf = io.StringIO()
    configure_logging(logging.WARNING, stream=buf)

    get_logger("test.emit").warning("hello %s", "world")

    assert "hello world" in buf.getvalue()


def test_logs_are_silent_without_configuration(restore_stellium_logger, capsys):
    """With only the NullHandler, emitting a record produces no output."""
    # Ensure no stray stream handlers (fixture restores afterward).
    logging.getLogger(_ROOT).handlers = [logging.NullHandler()]

    get_logger("utils.cache").warning("should not appear")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# === Warning hierarchy ======================================================


@pytest.mark.parametrize(
    "cls",
    [
        DataQualityWarning,
        GeocodingWarning,
        ConfigurationWarning,
        MissingEphemerisWarning,
    ],
)
def test_warning_subclasses_derive_from_base(cls):
    assert issubclass(cls, StelliumWarning)
    assert issubclass(cls, UserWarning)


def test_base_warning_filter_silences_all_subclasses():
    """Filtering StelliumWarning silences every subclass in one line."""
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=StelliumWarning)
        for cls in (
            DataQualityWarning,
            GeocodingWarning,
            ConfigurationWarning,
            MissingEphemerisWarning,
        ):
            with pytest.raises(cls):
                warnings.warn("boom", cls, stacklevel=2)


def test_missing_ephemeris_warning_backcompat():
    """The engines re-export is the same object as the canonical one."""
    from stellium.engines import MissingEphemerisWarning as from_engines

    assert from_engines is MissingEphemerisWarning
    assert issubclass(from_engines, StelliumWarning)


# === Public API surface =====================================================


@pytest.mark.parametrize(
    "name",
    [
        "configure_logging",
        "StelliumWarning",
        "DataQualityWarning",
        "GeocodingWarning",
        "ConfigurationWarning",
        "MissingEphemerisWarning",
    ],
)
def test_public_exports(name):
    assert hasattr(stellium, name)
    assert name in stellium.__all__
