"""Phase 1: converted library diagnostics emit typed warnings, not prints.

Covers the migration of bare ``print("Warning: ...")`` calls to
``warnings.warn(..., <StelliumWarning subclass>)`` across the library
(``docs/development/specs/STRUCTURED_LOGGING_SPEC.md`` Phase 1).

Site coverage here spans ``DataQualityWarning`` (CSV/DataFrame/AAF imports,
notable registry) and ``ConfigurationWarning`` (orb config). The remaining
converted sites share these categories: ``core/native.py`` geocoding
(``GeocodingWarning``, filterability proven in test_logging_infra; its
site-test is blocked by conftest's session-wide geocoding mock),
``components/arabic_parts.py`` (``DataQualityWarning``), and
``visualization/layers/houses.py`` (``ConfigurationWarning``). The Phase 4
lint guard is the regression backstop against any print() creeping back.
"""

import tempfile
from pathlib import Path

import pytest

from stellium.exceptions import (
    ConfigurationWarning,
    DataQualityWarning,
)

# === DataQualityWarning: I/O imports ========================================


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


# === ConfigurationWarning: orb config =======================================


def test_orb_invalid_by_pair_key_warns():
    from stellium.engines.orbs import ComplexOrbEngine

    engine = ComplexOrbEngine({"by_pair": {"Sun": {"default": 8.0}}})  # no dash
    with pytest.warns(ConfigurationWarning, match="Invalid 'by_pair' key"):
        engine._normalize_pair_keys()


# === DataQualityWarning: notable registry ==================================


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
