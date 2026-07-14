"""Tests for the structured diagnostics system (warnings + logging).

Covers the migration that replaced bare ``print()`` across the package
(``docs/development/specs/STRUCTURED_LOGGING_SPEC.md``):

- **Infrastructure** — the ``stellium`` logger (silent ``NullHandler`` by
  default, ``get_logger``, ``configure_logging``) and the ``StelliumWarning``
  hierarchy / public API surface.
- **Warnings** — caller-facing diagnostics now emit typed, filterable warnings
  (CSV/DataFrame/AAF imports, the notable registry, orb config).
- **Logging** — internal operational diagnostics go to the ``stellium`` logger
  (cache-write failure), never to stdout.
- **CLI** — the Click-based CLI writes via ``click.echo``; the redundant
  ``utils/cache_utils`` display module was removed.

The web app's warnings-capture wiring lives in ``web/tests/test_logging.py``
(separate suite: it imports the NiceGUI ``main`` module).
"""

import io
import logging
import tempfile
import warnings
from pathlib import Path

import pytest
from click.testing import CliRunner

import stellium
from stellium._logging import configure_logging, get_logger
from stellium.cli import cli
from stellium.exceptions import (
    ConfigurationWarning,
    DataQualityWarning,
    GeocodingWarning,
    MissingEphemerisWarning,
    StelliumWarning,
)

_ROOT = "stellium"


# =============================================================================
# Fixtures
# =============================================================================


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


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# =============================================================================
# Infrastructure — logger scaffolding
# =============================================================================


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


# =============================================================================
# Infrastructure — warning hierarchy & public API
# =============================================================================


def _all_warning_classes():
    """Every warning the library defines — *discovered*, not hand-listed.

    Both MissingGlyphWarning and TimeZoneWarning were raised at users while being
    absent from the hand-written list here **and** from `stellium.__all__`, so they
    could not be filtered: `warnings.filterwarnings(category=stellium.TimeZoneWarning)`
    raised AttributeError. A typed warning you cannot import is not a typed warning.
    Enumerate the module, and a new one is covered the moment it exists.
    """
    import inspect

    from stellium import exceptions

    return [
        cls
        for _name, cls in inspect.getmembers(exceptions, inspect.isclass)
        if issubclass(cls, StelliumWarning) and cls is not StelliumWarning
    ]


@pytest.mark.parametrize("cls", _all_warning_classes(), ids=lambda c: c.__name__)
def test_warning_subclasses_derive_from_base(cls):
    assert issubclass(cls, StelliumWarning)
    assert issubclass(cls, UserWarning)


@pytest.mark.parametrize("cls", _all_warning_classes(), ids=lambda c: c.__name__)
def test_every_warning_is_importable_from_the_package(cls):
    """A caller filters by class, so every warning we raise must be reachable as
    `stellium.<Name>` and be in `__all__`. Two were not."""
    assert hasattr(stellium, cls.__name__), (
        f"{cls.__name__} is raised at users but not exported — they cannot filter it"
    )
    assert cls.__name__ in stellium.__all__


def test_base_warning_filter_silences_all_subclasses():
    """Filtering StelliumWarning silences every subclass in one line."""
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


# =============================================================================
# Warnings — caller-facing diagnostics (Phase 1)
# =============================================================================
#
# Site coverage spans DataQualityWarning (CSV/DataFrame/AAF imports, notable
# registry) and ConfigurationWarning (orb config). The remaining converted
# sites share these categories: core/native.py geocoding (GeocodingWarning;
# its site-test is blocked by conftest's session-wide geocoding mock, so
# filterability is proven above and behavior verified manually),
# components/arabic_parts.py (DataQualityWarning), and
# visualization/layers/houses.py (ConfigurationWarning). The ruff T20 lint
# guard is the regression backstop against any print() creeping back.


def test_csv_skipped_rows_warn():
    from stellium.io import parse_csv

    csv_content = (
        "name,date,time,latitude,longitude\n"
        "Kate Louie,1994-01-06,11:47,37.3861,-122.0839\n"
        "Invalid Row,bad date,bad time,not a lat,not a lon\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    try:
        with pytest.warns(DataQualityWarning, match="Skipped 1 row"):
            natives = parse_csv(temp_path, skip_errors=True)
        assert len(natives) == 1
    finally:
        Path(temp_path).unlink()


def test_dataframe_skipped_rows_warn():
    pd = pytest.importorskip("pandas")
    from stellium.io import parse_dataframe

    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Bad Row"],
            "date": ["1994-01-06", "not-a-date"],
            "time": ["11:47", "nope"],
            "latitude": [37.3861, 0.0],
            "longitude": [-122.0839, 0.0],
        }
    )
    with pytest.warns(DataQualityWarning, match="Skipped 1 row"):
        natives = parse_dataframe(df, skip_errors=True)
    assert len(natives) == 1


def test_aaf_malformed_record_warns():
    from stellium.io import parse_aaf

    # A valid header line followed by a malformed A93/B93 pair.
    aaf_content = "#A93: garbage-not-a-real-a93-line\n#B93: also-garbage\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".aaf", delete=False) as f:
        f.write(aaf_content)
        temp_path = f.name
    try:
        with pytest.warns(DataQualityWarning):
            parse_aaf(temp_path)
    finally:
        Path(temp_path).unlink()


def test_registry_unreadable_yaml_warns(tmp_path, monkeypatch):
    from stellium.data import registry as reg_mod

    births = tmp_path / "births"
    births.mkdir()
    # Invalid YAML (unclosed flow sequence) -> yaml.safe_load raises.
    (births / "broken.yaml").write_text("name: [unclosed bracket\n")

    monkeypatch.setattr(
        reg_mod.NotableRegistry,
        "_get_notables_path",
        lambda self: tmp_path,
    )

    with pytest.warns(DataQualityWarning, match="Failed to read"):
        reg_mod.NotableRegistry()


def test_orb_invalid_by_pair_key_warns():
    from stellium.engines.orbs import ComplexOrbEngine

    engine = ComplexOrbEngine({"by_pair": {"Sun": {"default": 8.0}}})  # no dash
    with pytest.warns(ConfigurationWarning, match="Invalid 'by_pair' key"):
        engine._normalize_pair_keys()


# =============================================================================
# Logging — internal operational diagnostics (Phase 2)
# =============================================================================
#
# utils/cache.py cache-write failure is tested here. data/paths.py sites
# (ephemeris copy/init) share the same channel but mutate global swisseph path
# state, so they're covered via the channel tests above plus review.


def test_cache_write_failure_logs_warning(tmp_path, caplog):
    from stellium.utils.cache import Cache

    cache = Cache(cache_dir=str(tmp_path / "cache"))

    # A lambda cannot be pickled, so the write raises inside set() -- the cache
    # must swallow it and log a warning, not crash or print.
    with caplog.at_level(logging.WARNING, logger="stellium"):
        cache.set("general", "unpicklable", lambda x: x)

    records = [r for r in caplog.records if r.name == "stellium.utils.cache"]
    assert records, "expected a log record on the stellium.utils.cache logger"
    assert records[0].levelno == logging.WARNING
    assert "Could not write to cache" in records[0].getMessage()


def test_cache_write_failure_does_not_print(tmp_path, capsys):
    """The failure is logged, never printed to stdout/stderr."""
    from stellium.utils.cache import Cache

    cache = Cache(cache_dir=str(tmp_path / "cache"))
    cache.set("general", "unpicklable", lambda x: x)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# =============================================================================
# CLI — output via click.echo (Phase 3)
# =============================================================================


def test_download_file_skip_uses_click_echo(tmp_path, capsys):
    """download_file echoes progress via click.echo (no network on the skip path)."""
    from stellium.cli.ephemeris_download import download_file

    existing = tmp_path / "sepl_18.se1"
    existing.write_text("already here")

    # File exists and force=False -> returns immediately, echoing "Skipping".
    result = download_file("https://example.invalid/x", existing)

    assert result is True
    assert "Skipping" in capsys.readouterr().out


def test_download_file_quiet_suppresses_output(tmp_path, capsys):
    from stellium.cli.ephemeris_download import download_file

    existing = tmp_path / "sepl_18.se1"
    existing.write_text("already here")

    download_file("https://example.invalid/x", existing, quiet=True)

    assert capsys.readouterr().out == ""


def test_cli_ephemeris_group_help(runner):
    """The ephemeris CLI group loads and renders help via click (hermetic)."""
    result = runner.invoke(cli, ["ephemeris", "--help"])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cli_cache_group_help(runner):
    """The cache CLI group loads and renders help via click (hermetic)."""
    result = runner.invoke(cli, ["cache", "--help"])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cache_utils_module_removed():
    """The redundant display module is gone and no longer a public export."""
    import stellium.utils as utils

    assert not hasattr(utils, "print_cache_info")
    with pytest.raises(ImportError):
        from stellium.utils import cache_utils  # noqa: F401
