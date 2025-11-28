"""Test core data models."""

import pytest

from stellium.core.models import (
    CelestialPosition,
    ChartLocation,
    HouseCusps,
    ObjectType,
)


def test_chart_location_validation():
    """Test location coordinate validation."""
    # Valid location
    loc = ChartLocation(latitude=37.7749, longitude=-122.4194, name="San Francisco")
    assert loc.latitude == 37.7749

    # Invalid latitude
    with pytest.raises(ValueError):
        ChartLocation(latitude=91.0, longitude=0.0)

    # Invalid longitude
    with pytest.raises(ValueError):
        ChartLocation(latitude=0.0, longitude=181.0)


def test_celestial_position_immutability():
    """Test that CelestialPosition is immutable."""
    pos = CelestialPosition(
        name="Sun", object_type=ObjectType.PLANET, longitude=45.5, speed_longitude=0.98
    )

    # Verify calculated fields
    assert pos.sign == "Taurus"  # 45° is in Taurus (30-60)
    assert abs(pos.sign_degree - 15.5) < 0.01
    assert not pos.is_retrograde

    # Verify immutability
    with pytest.raises(Exception) as _e:
        # Will raise AttributeError or FrozenInstanceError
        pos.longitude = 50.0  # type: ignore


def test_house_cusps_validation():
    """Test house cusp validation."""
    cusps = tuple(i * 30 for i in range(12))  # Simple 30 degree houses
    houses = HouseCusps(system="Equal", cusps=cusps)

    assert houses.get_cusp(1) == 0.0
    assert houses.get_cusp(12) == 330.0

    # Invalid house number
    with pytest.raises(ValueError):
        houses.get_cusp(13)


def test_sign_position_formatting():
    """Test human-readable sign position."""
    pos = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=95.75,  # 5.75° Cancer
    )

    assert pos.sign == "Cancer"
    assert "5°45'" in pos.sign_position
    assert "Cancer" in pos.sign_position


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
