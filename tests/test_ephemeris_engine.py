"""Test ephemeris engines."""

import datetime as dt
import warnings

import pytest
import pytz

from stellium.core.models import ChartDateTime, ChartLocation
from stellium.engines.ephemeris import (
    MissingEphemerisWarning,
    MockEphemerisEngine,
    SwissEphemerisEngine,
)


def test_missing_ephemeris_emits_capturable_warning():
    """A missing ephemeris file must warn via the warnings module.

    Previously this was a bare print to stderr -- not capturable or
    suppressible. It now emits a MissingEphemerisWarning that callers can
    catch, filter, or silence, and it dedups per object per session.
    """
    engine = SwissEphemerisEngine()
    SwissEphemerisEngine._warned_missing_ephemeris.discard("Eris")

    err = "SwissEph file 'se136199.se1' not found in PATH '/x'"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", MissingEphemerisWarning)
        engine._warn_missing_ephemeris("Eris", 10000 + 136199, err)
        # Second identical call is deduped (once per object per session).
        engine._warn_missing_ephemeris("Eris", 10000 + 136199, err)

    warns = [w for w in caught if issubclass(w.category, MissingEphemerisWarning)]
    assert len(warns) == 1
    assert "Eris" in str(warns[0].message)
    assert "download-asteroid" in str(warns[0].message)


def test_missing_ephemeris_warning_can_be_silenced():
    """MissingEphemerisWarning must be suppressible via a filter."""
    engine = SwissEphemerisEngine()
    SwissEphemerisEngine._warned_missing_ephemeris.discard("Chiron")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("ignore", MissingEphemerisWarning)
        engine._warn_missing_ephemeris(
            "Chiron", 15, "SwissEph file 'seas_12.se1' not found in PATH '/x'"
        )

    assert not caught


def test_mock_ephemeris_engine():
    """Test the mock ephemeris engine."""
    engine = MockEphemerisEngine()

    datetime = ChartDateTime(
        utc_datetime=dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC),
        julian_day=2451545.0,
    )
    location = ChartLocation(latitude=0, longitude=0)

    positions = engine.calculate_positions(datetime, location, objects=["Sun", "Moon"])

    assert len(positions) == 2
    sun = next(p for p in positions if p.name == "Sun")
    assert sun.longitude == 0.0
    assert sun.sign == "Aries"


def test_swiss_ephemeris_engine():
    """Test Swiss Ephemeris calculation."""
    engine = SwissEphemerisEngine()

    # Einstein's birth date
    datetime = ChartDateTime(
        utc_datetime=dt.datetime(
            1879, 3, 14, 11, 30, tzinfo=pytz.timezone("Europe/Berlin")
        ),
        julian_day=2407422.9791667,
    )
    location = ChartLocation(latitude=48.3984, longitude=9.9916, name="Ulm, Germany")

    positions = engine.calculate_positions(datetime, location, objects=["Sun", "Moon"])

    assert len(positions) == 2

    sun = next(p for p in positions if p.name == "Sun")
    assert sun.sign == "Pisces"  # Sun in Pisces for mid-March
    assert not sun.is_retrograde

    moon = next(p for p in positions if p.name == "Moon")
    assert moon.name == "Moon"
    assert 0 <= moon.longitude < 360


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
