"""Test Arabic Parts calculation."""

import datetime as dt

import pytest

from stellium.components.arabic_parts import (
    ArabicPartsCalculator,
)
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.core.native import Native


def test_part_of_fortune_day_chart():
    """Test Part of Fortune calculation for day chart."""
    # Day chart: Sun above horizon
    birthday = dt.datetime(2000, 6, 21, 12, 0, tzinfo=dt.UTC)
    # Summer, noon
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"]))
        .calculate()
    )

    # Should have Part of Fortune
    fortune = chart.get_object("Part of Fortune")

    assert fortune is not None
    assert fortune.object_type == ObjectType.ARABIC_PART
    assert 0 <= fortune.longitude < 360
    assert chart.get_house("Part of Fortune") is not None


def test_part_of_fortune_night_chart():
    """Test Part of Fortune calculation for night chart."""
    # Night chart: Sun below horizon (here: midnight)
    birthday = dt.datetime(2000, 6, 21, 0, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(ArabicPartsCalculator(["Part of Fortune"]))
        .calculate()
    )
    fortune = chart.get_object("Part of Fortune")
    assert fortune is not None

    # Night formula is reversed from day formula
    # Can't check exact value without knowing positions,
    # but can verify it was calculated
    assert fortune.sign is not None


def test_all_arabic_parts():
    """Test calculation of all Arabic Parts."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(ArabicPartsCalculator())
        .calculate()
    )

    # Check that parts were calculated
    arabic_parts = [
        p for p in chart.positions if p.object_type == ObjectType.ARABIC_PART
    ]

    # Should have calculated multiple parts
    assert len(arabic_parts) > 0

    # Check a few specific ones
    assert chart.get_object("Part of Fortune") is not None
    assert chart.get_object("Part of Spirit") is not None
    assert chart.get_object("Part of Eros (Love)") is not None

    # All should have house assignments
    for part in arabic_parts:
        assert chart.get_house(part.name) is not None
        assert 1 <= chart.get_house(part.name) <= 12


def test_custom_arabic_part():
    """Test defining a custom Arabic Part."""
    custom_parts = {
        "Part of Cats": {
            "points": ["ASC", "Moon", "Venus"],
            "sect_flip": False,
            "description": "Relationship with feline companions",
        }
    }

    calculator = ArabicPartsCalculator(custom_parts=custom_parts)
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = ChartBuilder.from_native(native).add_component(calculator).calculate()

    # Should have our custom part
    cat_part = chart.get_object("Part of Cats")
    assert cat_part is not None
    assert cat_part.object_type == ObjectType.ARABIC_PART


def test_arabic_part_in_json_export():
    """Test that Arabic Parts appear in JSON export."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(ArabicPartsCalculator())
        .calculate()
    )

    data = chart.to_dict()

    # Find Arabic Parts in positions
    arabic_parts = [p for p in data["positions"] if p["type"] == "arabic_part"]

    assert len(arabic_parts) > 0

    # Check structure
    for part in arabic_parts:
        assert "name" in part
        assert "longitude" in part
        assert "sign" in part


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
