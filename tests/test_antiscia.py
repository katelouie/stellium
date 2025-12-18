"""Test Antiscia and Contra-Antiscia calculation."""

import datetime as dt

import pytest

from stellium.components.antiscia import (
    AntisciaCalculator,
    AntisciaConjunction,
)
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.core.native import Native

# =============================================================================
# Antiscia Formula Tests
# =============================================================================


def test_antiscia_formula():
    """Test that antiscia are calculated correctly.

    Antiscia formula: antiscion = (180 - longitude) % 360

    Example mappings (reflecting across Cancer-Capricorn axis):
    - 0° Aries (0°) -> 0° Virgo (150°)  ... wait, let me recalculate
    - Actually: (180 - 0) % 360 = 180° = 0° Libra

    The solstice axis reflection means:
    - Points at equal distance from 0° Cancer (90°) are antiscia
    - 15° Gemini (75°) <-> 15° Cancer (105°): both 15° from 0° Cancer
    """
    birth = dt.datetime(2000, 6, 21, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    # Get Sun position and its antiscion
    sun = chart.get_object("Sun")
    sun_antiscion = chart.get_object("Sun Antiscion")

    assert sun is not None
    assert sun_antiscion is not None
    assert sun_antiscion.object_type == ObjectType.ANTISCION

    # Verify the formula: antiscion = (180 - longitude) % 360
    expected_antiscion = (180.0 - sun.longitude) % 360.0
    assert abs(sun_antiscion.longitude - expected_antiscion) < 0.001


def test_contra_antiscia_formula():
    """Test that contra-antiscia are calculated correctly.

    Contra-antiscia formula: contra = (360 - longitude) % 360

    This reflects across the Aries-Libra (equinox) axis.
    """
    birth = dt.datetime(2000, 6, 21, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(include_contra=True))
        .calculate()
    )

    # Get Moon position and its contra-antiscion
    moon = chart.get_object("Moon")
    moon_contra = chart.get_object("Moon Contra-Antiscion")

    assert moon is not None
    assert moon_contra is not None
    assert moon_contra.object_type == ObjectType.CONTRA_ANTISCION

    # Verify the formula: contra = (360 - longitude) % 360
    expected_contra = (360.0 - moon.longitude) % 360.0
    assert abs(moon_contra.longitude - expected_contra) < 0.001


# =============================================================================
# Point Generation Tests
# =============================================================================


def test_antiscia_points_generated():
    """Test that antiscia points are added to chart positions."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    # Get antiscia points
    antiscia_pts = [p for p in chart.positions if p.object_type == ObjectType.ANTISCION]

    # Should have antiscia for each planet in default list
    # Default: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
    #          Uranus, Neptune, Pluto, True Node = 11 planets
    assert len(antiscia_pts) == 11

    # Each should have a valid longitude
    for pt in antiscia_pts:
        assert 0 <= pt.longitude < 360
        assert pt.name.endswith(" Antiscion")


def test_contra_antiscia_points_generated():
    """Test that contra-antiscia points are generated when enabled."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(include_contra=True))
        .calculate()
    )

    contra_pts = [
        p for p in chart.positions if p.object_type == ObjectType.CONTRA_ANTISCION
    ]

    assert len(contra_pts) == 11

    for pt in contra_pts:
        assert 0 <= pt.longitude < 360
        assert pt.name.endswith(" Contra-Antiscion")


def test_no_contra_antiscia_when_disabled():
    """Test that contra-antiscia are not generated when disabled."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(include_contra=False))
        .calculate()
    )

    contra_pts = [
        p for p in chart.positions if p.object_type == ObjectType.CONTRA_ANTISCION
    ]

    assert len(contra_pts) == 0


# =============================================================================
# Custom Planet List Tests
# =============================================================================


def test_custom_planet_list():
    """Test using a custom list of planets."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    # Only calculate for classical planets
    classical_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    chart = (
        ChartBuilder.from_native(native)
        .add_component(
            AntisciaCalculator(planets=classical_planets, include_contra=False)
        )
        .calculate()
    )

    antiscia_pts = [p for p in chart.positions if p.object_type == ObjectType.ANTISCION]

    assert len(antiscia_pts) == 7

    # Should not have outer planets
    names = [p.name for p in antiscia_pts]
    assert "Uranus Antiscion" not in names
    assert "Neptune Antiscion" not in names
    assert "Pluto Antiscion" not in names


# =============================================================================
# Conjunction Detection Tests
# =============================================================================


def test_conjunction_detection():
    """Test that antiscia conjunctions are detected and stored in metadata."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(orb=3.0))  # Wider orb for testing
        .calculate()
    )

    # Check metadata
    antiscia_data = chart.metadata.get("antiscia", {})

    assert "conjunctions" in antiscia_data
    assert "contra_conjunctions" in antiscia_data
    assert "orb" in antiscia_data
    assert antiscia_data["orb"] == 3.0


def test_conjunction_dataclass():
    """Test the AntisciaConjunction dataclass."""
    conj = AntisciaConjunction(
        planet1="Sun",
        planet2="Moon",
        orb=1.5,
        is_applying=True,
        antiscion_longitude=120.0,
        planet2_longitude=121.5,
    )

    assert conj.planet1 == "Sun"
    assert conj.planet2 == "Moon"
    assert conj.orb == 1.5
    assert conj.is_applying is True

    # Test description property
    desc = conj.description
    assert "Sun" in desc
    assert "Moon" in desc
    assert "applying" in desc
    assert "1.5°" in desc


def test_conjunction_orb_filtering():
    """Test that conjunctions outside orb are not included."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)
    native = Native(birth, location)

    # Very tight orb - should find fewer conjunctions
    chart_tight = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(orb=0.5))
        .calculate()
    )

    # Wider orb - should find more conjunctions
    chart_wide = (
        ChartBuilder.from_native(native)
        .add_component(AntisciaCalculator(orb=5.0))
        .calculate()
    )

    tight_conjs = chart_tight.metadata.get("antiscia", {}).get("conjunctions", [])
    wide_conjs = chart_wide.metadata.get("antiscia", {}).get("conjunctions", [])

    # Wider orb should find at least as many (usually more)
    assert len(wide_conjs) >= len(tight_conjs)

    # All tight conjunctions should have orb <= 0.5
    for conj in tight_conjs:
        assert conj.orb <= 0.5


# =============================================================================
# Chart Wheel Filtering Tests
# =============================================================================


def test_antiscia_not_in_planetary_objects():
    """Test that antiscia points are NOT included in get_planets()."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    # get_planets() should NOT include antiscia
    planets = chart.get_planets()
    planet_names = [p.name for p in planets]

    assert not any("Antiscion" in name for name in planet_names)
    assert not any("Contra-Antiscion" in name for name in planet_names)


def test_antiscia_object_types_distinct():
    """Test that antiscia use distinct ObjectTypes."""
    assert ObjectType.ANTISCION != ObjectType.POINT
    assert ObjectType.ANTISCION != ObjectType.PLANET
    assert ObjectType.CONTRA_ANTISCION != ObjectType.POINT
    assert ObjectType.CONTRA_ANTISCION != ObjectType.PLANET
    assert ObjectType.ANTISCION != ObjectType.CONTRA_ANTISCION


# =============================================================================
# Edge Cases
# =============================================================================


def test_antiscia_at_zero_degrees():
    """Test antiscia calculation at 0° longitude."""
    # At 0° Aries, antiscion should be at 180° (0° Libra)
    # Formula: (180 - 0) % 360 = 180
    birth = dt.datetime(2000, 3, 20, 12, 0, tzinfo=dt.UTC)  # Near vernal equinox
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    sun = chart.get_object("Sun")
    sun_antiscion = chart.get_object("Sun Antiscion")

    assert sun is not None
    assert sun_antiscion is not None

    # Verify formula works at/near 0°
    expected = (180.0 - sun.longitude) % 360.0
    assert abs(sun_antiscion.longitude - expected) < 0.001


def test_antiscia_at_180_degrees():
    """Test antiscia calculation at 180° longitude."""
    # At 180° (0° Libra), antiscion should be at 0° (0° Aries)
    # Formula: (180 - 180) % 360 = 0
    birth = dt.datetime(2000, 9, 22, 12, 0, tzinfo=dt.UTC)  # Near autumnal equinox
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    sun = chart.get_object("Sun")
    sun_antiscion = chart.get_object("Sun Antiscion")

    assert sun is not None
    assert sun_antiscion is not None

    # At exactly 180°, antiscion would be at 0°
    expected = (180.0 - sun.longitude) % 360.0
    assert abs(sun_antiscion.longitude - expected) < 0.001


def test_antiscia_json_export():
    """Test that antiscia points appear correctly in JSON export."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native).add_component(AntisciaCalculator()).calculate()
    )

    data = chart.to_dict()

    # Find antiscia in positions
    antiscia_positions = [p for p in data["positions"] if p["type"] == "antiscion"]

    assert len(antiscia_positions) > 0

    # Check structure
    for pt in antiscia_positions:
        assert "name" in pt
        assert "longitude" in pt
        assert "sign" in pt
        assert pt["type"] == "antiscion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
