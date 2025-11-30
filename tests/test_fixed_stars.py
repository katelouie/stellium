"""Test fixed star calculations."""

import datetime as dt

import pytest

from stellium.components.fixed_stars import FixedStarsComponent
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, FixedStarPosition, ObjectType
from stellium.core.native import Native
from stellium.core.registry import (
    FIXED_STARS_REGISTRY,
    get_fixed_star_info,
    get_royal_stars,
    get_stars_by_tier,
)
from stellium.engines.fixed_stars import SwissEphemerisFixedStarsEngine

# =============================================================================
# Registry Tests
# =============================================================================


def test_fixed_stars_registry_exists():
    """Test that the registry is populated."""
    assert len(FIXED_STARS_REGISTRY) > 0
    assert "Regulus" in FIXED_STARS_REGISTRY
    assert "Aldebaran" in FIXED_STARS_REGISTRY
    assert "Sirius" in FIXED_STARS_REGISTRY


def test_get_fixed_star_info():
    """Test looking up star info by name."""
    regulus = get_fixed_star_info("Regulus")
    assert regulus is not None
    assert regulus.name == "Regulus"
    assert regulus.constellation == "Leo"
    assert regulus.is_royal is True
    assert regulus.tier == 1


def test_get_fixed_star_info_not_found():
    """Test looking up non-existent star."""
    result = get_fixed_star_info("NotARealStar")
    assert result is None


def test_get_royal_stars():
    """Test getting the four royal stars."""
    royal = get_royal_stars()
    assert len(royal) == 4

    names = {s.name for s in royal}
    assert "Aldebaran" in names
    assert "Regulus" in names
    assert "Antares" in names
    assert "Fomalhaut" in names


def test_get_stars_by_tier():
    """Test filtering stars by tier."""
    tier1 = get_stars_by_tier(1)
    tier2 = get_stars_by_tier(2)
    tier3 = get_stars_by_tier(3)

    # All tier 1 should be royal
    assert all(s.is_royal for s in tier1)
    assert len(tier1) == 4

    # Tier 2 should have Sirius, Spica, etc.
    tier2_names = {s.name for s in tier2}
    assert "Sirius" in tier2_names
    assert "Spica" in tier2_names

    # Tier 3 should have some but not royal stars
    assert len(tier3) > 0
    assert not any(s.is_royal for s in tier3)


def test_fixed_star_info_dataclass():
    """Test FixedStarInfo dataclass properties."""
    algol = get_fixed_star_info("Algol")
    assert algol is not None
    assert algol.name == "Algol"
    assert algol.swe_name == "Algol"
    assert algol.constellation == "Perseus"
    assert algol.tier == 2
    assert algol.is_royal is False
    assert algol.magnitude > 0
    assert "transformation" in algol.keywords or "intensity" in algol.keywords


# =============================================================================
# Engine Tests
# =============================================================================


def test_engine_calculate_all_stars():
    """Test calculating all stars in registry."""
    engine = SwissEphemerisFixedStarsEngine()
    # J2000.0 epoch
    jd = 2451545.0

    stars = engine.calculate_stars(jd)

    assert len(stars) == len(FIXED_STARS_REGISTRY)
    assert all(isinstance(s, FixedStarPosition) for s in stars)
    assert all(s.object_type == ObjectType.FIXED_STAR for s in stars)


def test_engine_calculate_specific_stars():
    """Test calculating specific stars."""
    engine = SwissEphemerisFixedStarsEngine()
    jd = 2451545.0

    stars = engine.calculate_stars(jd, stars=["Regulus", "Sirius"])

    assert len(stars) == 2
    names = {s.name for s in stars}
    assert "Regulus" in names
    assert "Sirius" in names


def test_engine_calculate_royal_stars():
    """Test convenience method for royal stars."""
    engine = SwissEphemerisFixedStarsEngine()
    jd = 2451545.0

    stars = engine.calculate_royal_stars(jd)

    assert len(stars) == 4
    assert all(s.is_royal for s in stars)


def test_engine_calculate_by_tier():
    """Test calculating stars by tier."""
    engine = SwissEphemerisFixedStarsEngine()
    jd = 2451545.0

    tier1 = engine.calculate_stars_by_tier(jd, tier=1)
    tier2 = engine.calculate_stars_by_tier(jd, tier=2)

    assert len(tier1) == 4  # Royal stars
    assert len(tier2) > 5  # Major stars


def test_engine_star_not_found():
    """Test error when star not in registry."""
    engine = SwissEphemerisFixedStarsEngine()
    jd = 2451545.0

    with pytest.raises(ValueError, match="not found in registry"):
        engine.calculate_stars(jd, stars=["NotARealStar"])


def test_fixed_star_position_properties():
    """Test FixedStarPosition properties."""
    engine = SwissEphemerisFixedStarsEngine()
    jd = 2451545.0

    stars = engine.calculate_stars(jd, stars=["Regulus"])
    regulus = stars[0]

    # Check position data
    assert 0 <= regulus.longitude <= 360
    assert -90 <= regulus.latitude <= 90

    # Check sign calculation (inherited from CelestialPosition)
    assert regulus.sign in [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    assert 0 <= regulus.sign_degree < 30

    # Check star-specific fields
    assert regulus.constellation == "Leo"
    assert regulus.is_royal is True
    assert regulus.tier == 1
    assert regulus.magnitude > 0


def test_regulus_position_around_2000():
    """Test Regulus is approximately at expected position for J2000."""
    engine = SwissEphemerisFixedStarsEngine()
    # J2000.0 = Jan 1, 2000, 12:00 TT
    jd = 2451545.0

    stars = engine.calculate_stars(jd, stars=["Regulus"])
    regulus = stars[0]

    # Regulus was at approximately 29°50' Leo around 2000
    # (~149.83° absolute longitude)
    assert 148 < regulus.longitude < 151
    assert regulus.sign == "Leo"


def test_precession_changes_position():
    """Test that star positions change over time due to precession."""
    engine = SwissEphemerisFixedStarsEngine()

    # J2000.0
    jd_2000 = 2451545.0
    # Approximately year 2100
    jd_2100 = jd_2000 + (100 * 365.25)

    stars_2000 = engine.calculate_stars(jd_2000, stars=["Regulus"])
    stars_2100 = engine.calculate_stars(jd_2100, stars=["Regulus"])

    regulus_2000 = stars_2000[0]
    regulus_2100 = stars_2100[0]

    # Precession is about 1° per 72 years, so ~1.4° in 100 years
    # Position should increase (move forward through zodiac)
    diff = regulus_2100.longitude - regulus_2000.longitude
    assert 1.0 < diff < 2.0


# =============================================================================
# Component Tests
# =============================================================================


def test_component_all_stars():
    """Test FixedStarsComponent with all stars."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent())
        .calculate()
    )

    # Should have fixed stars in positions
    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]
    assert len(fixed_stars) == len(FIXED_STARS_REGISTRY)


def test_component_royal_only():
    """Test FixedStarsComponent with royal stars only."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(royal_only=True))
        .calculate()
    )

    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]
    assert len(fixed_stars) == 4

    names = {s.name for s in fixed_stars}
    assert "Aldebaran" in names
    assert "Regulus" in names
    assert "Antares" in names
    assert "Fomalhaut" in names


def test_component_specific_stars():
    """Test FixedStarsComponent with specific stars."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(stars=["Sirius", "Algol"]))
        .calculate()
    )

    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]
    assert len(fixed_stars) == 2

    names = {s.name for s in fixed_stars}
    assert "Sirius" in names
    assert "Algol" in names


def test_component_by_tier():
    """Test FixedStarsComponent filtering by tier."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    # Tier 2 only
    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(tier=2))
        .calculate()
    )

    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]

    # Should only have tier 2 stars
    assert all(isinstance(s, FixedStarPosition) and s.tier == 2 for s in fixed_stars)


def test_component_tier_with_higher():
    """Test FixedStarsComponent with include_higher_tiers."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    # Tier 2 and all higher (1)
    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(tier=2, include_higher_tiers=True))
        .calculate()
    )

    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]

    # Should have tier 1 and tier 2
    tiers = {s.tier for s in fixed_stars if isinstance(s, FixedStarPosition)}
    assert 1 in tiers
    assert 2 in tiers
    assert 3 not in tiers


def test_component_integrates_with_chart():
    """Test that fixed stars integrate properly with chart output."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=51.5074, longitude=-0.1278)  # London
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(stars=["Regulus"]))
        .calculate()
    )

    # Can retrieve via get_object
    regulus = chart.get_object("Regulus")
    assert regulus is not None
    assert isinstance(regulus, FixedStarPosition)

    # Has expected properties
    assert regulus.sign == "Leo"
    assert regulus.constellation == "Leo"


# =============================================================================
# Integration Tests
# =============================================================================


def test_fixed_stars_with_notable():
    """Test fixed stars calculation with a notable person."""
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(FixedStarsComponent(royal_only=True))
        .calculate()
    )

    fixed_stars = [p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR]
    assert len(fixed_stars) == 4


def test_fixed_stars_to_dict():
    """Test that fixed stars serialize properly to dict."""
    birth = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0)
    native = Native(birth, location)

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent(stars=["Regulus"]))
        .calculate()
    )

    data = chart.to_dict()

    # Find Regulus in positions
    regulus_data = next((p for p in data["positions"] if p["name"] == "Regulus"), None)
    assert regulus_data is not None
    assert regulus_data["type"] == "fixed_star"
    assert 0 <= regulus_data["longitude"] <= 360


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
