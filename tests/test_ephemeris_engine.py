"""Test ephemeris engines."""

import datetime as dt

import pytest
import pytz

from stellium.core.models import ChartDateTime, ChartLocation
from stellium.engines.ephemeris import MockEphemerisEngine, SwissEphemerisEngine


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
