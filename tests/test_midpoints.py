"""Test midpoint calculations."""

import datetime as dt

import pytest

from stellium.components.midpoints import MidpointCalculator
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.core.native import Native


def test_basic_midpoint_calculation():
    """Test basic midpoint calculation."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(MidpointCalculator(pairs=[("Sun", "Moon")]))
        .calculate()
    )

    # Should have Sun/Moon midpoint
    midpoint = chart.get_object("Midpoint:Sun/Moon")
    assert midpoint is not None
    assert midpoint.object_type == ObjectType.MIDPOINT
    assert 0 <= midpoint.longitude <= 360


def test_default_midpoints():
    """Test calculation of default midpoint pairs."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(MidpointCalculator()).calculate()
    )

    # Should have default midpoints
    midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

    assert len(midpoints) > 0

    # Check some common ones
    assert chart.get_object("Midpoint:Sun/Moon") is not None
    assert chart.get_object("Midpoint:ASC/MC") is not None
    assert chart.get_object("Midpoint:Venus/Mars") is not None


def test_all_midpoints():
    """Test calculating all possible midpoint pairs."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(MidpointCalculator(calculate_all=True))
        .calculate()
    )

    midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

    # Should have many midpoints (all planet pairs)
    assert len(midpoints) > 40  # At least so many


def test_indirect_midpoints():
    """Test indirect midpoint calculation."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(MidpointCalculator(pairs=[("Sun", "Moon")], indirect=True))
        .calculate()
    )

    # Should have both direct and indirect
    direct = chart.get_object("Midpoint:Sun/Moon")
    indirect = chart.get_object("Midpoint:Sun/Moon (indirect)")

    assert direct is not None
    assert indirect is not None

    # Indirect should be 180 degrees from direct
    expected_indirect = (direct.longitude + 180) % 360
    assert abs(indirect.longitude - expected_indirect) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
