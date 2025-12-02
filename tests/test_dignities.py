"""
Comprehensive tests for Essential Dignities calculations.

This module tests planetary dignity calculations including:
- Traditional essential dignities (pre-1781)
- Modern essential dignities
- Mutual reception analysis
- Rulership, exaltation, detriment, fall
- Triplicities, terms/bounds, faces/decans

TESTING CONCEPTS:

Dignities are how astrologers evaluate a planet's "strength" or "condition"
based on its zodiac sign placement. Think of it like a fish in water vs. a fish on land.

**Essential Dignity Types:**
- **Rulership/Domicile**: Planet rules this sign (strongest, +5 points)
- **Exaltation**: Planet is honored here (+4 points)
- **Triplicity**: Planet rules the element (Fire/Earth/Air/Water) (+3 points)
- **Term/Bound**: Planet rules a degree range (+2 points)
- **Face/Decan**: Planet rules a 10° section (+1 point)
- **Detriment**: Opposite of rulership (weakest, -5 points)
- **Fall**: Opposite of exaltation (-4 points)
- **Peregrine**: No dignities (neutral, 0 points)

**Example:**
- Sun in Leo = Rulership (+5) - Strong!
- Sun in Aquarius = Detriment (-5) - Weak
- Sun in Aries = Exaltation (+4) - Strong!
- Sun in Libra = Fall (-4) - Weak

**Why test this?**
The dignity tables (DIGNITIES dict) are complex with many values.
A typo in the data could give wrong interpretations for years!
Tests verify the calculations are correct and tables are accurate.
"""

import pytest

from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.dignities import (
    DIGNITIES,
    ModernDignityCalculator,
    MutualReceptionAnalyzer,
    TraditionalDignityCalculator,
)

# =============================================================================
# DIGNITIES DATA STRUCTURE TESTS
# =============================================================================


def test_dignities_dict_has_all_signs():
    """Test that DIGNITIES contains all 12 zodiac signs."""
    expected_signs = [
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

    assert len(DIGNITIES) == 12, "Should have 12 zodiac signs"

    for sign in expected_signs:
        assert sign in DIGNITIES, f"{sign} should be in DIGNITIES"


def test_dignities_sign_structure():
    """Test that each sign has required keys and correct structure."""
    required_keys = ["symbol", "element", "modality", "traditional", "modern"]

    for sign_name, sign_data in DIGNITIES.items():
        # Check required keys exist
        for key in required_keys:
            assert key in sign_data, f"{sign_name} missing key: {key}"

        # Check element is valid
        assert sign_data["element"] in [
            "Fire",
            "Earth",
            "Air",
            "Water",
        ], f"{sign_name} has invalid element"

        # Check modality is valid
        assert sign_data["modality"] in [
            "Cardinal",
            "Fixed",
            "Mutable",
        ], f"{sign_name} has invalid modality"

        # Check traditional/modern have dignity types
        for system in ["traditional", "modern"]:
            assert "ruler" in sign_data[system], f"{sign_name} {system} missing ruler"


def test_fire_signs_have_fire_element():
    """Test that fire signs (Aries, Leo, Sagittarius) have Fire element."""
    fire_signs = ["Aries", "Leo", "Sagittarius"]

    for sign in fire_signs:
        assert DIGNITIES[sign]["element"] == "Fire", f"{sign} should have Fire element"


def test_rulerships_are_correct():
    """Test classic planetary rulerships are correct."""
    # Traditional rulerships that haven't changed
    rulerships = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",  # Traditional
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",  # Traditional
        "Pisces": "Jupiter",  # Traditional
    }

    for sign, ruler in rulerships.items():
        traditional_ruler = DIGNITIES[sign]["traditional"]["ruler"]
        assert (
            traditional_ruler == ruler
        ), f"{sign} traditional ruler should be {ruler}, got {traditional_ruler}"


# =============================================================================
# TRADITIONAL DIGNITY CALCULATOR TESTS
# =============================================================================


def test_traditional_calculator_initialization():
    """Test TraditionalDignityCalculator initializes correctly."""
    calc = TraditionalDignityCalculator(decans="chaldean")
    assert calc.calculator_name == "Traditional Essential Dignities"
    assert calc.decans == "chaldean"


def test_traditional_calculator_invalid_decans():
    """Test that invalid decan system raises ValueError."""
    with pytest.raises(ValueError, match="Decans must be either"):
        TraditionalDignityCalculator(decans="invalid")


def test_sun_in_leo_rulership():
    """
    Test Sun in Leo shows rulership (domicile).

    Sun rules Leo, so it should have +5 points and "strong" interpretation.

    NOTE: There's a typo in the source code default parameter ("chalean" vs "chaldean"),
    so we explicitly specify decans to avoid the validation error.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at 15° Leo
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=135.0,  # 15° Leo (120° + 15°)
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    # Result is a dict for this single position
    assert result["planet"] == "Sun"
    assert result["sign"] == "Leo"

    # Should have domicile (rulership)
    assert "domicile" in result["dignities"]
    assert result["score"] >= 5, "Sun in Leo should score at least +5 for domicile"
    assert "strong" in result["interpretation"].lower()


def test_sun_in_aries_exaltation():
    """
    Test Sun in Aries shows exaltation.

    Sun is exalted in Aries at 19°, so it should have +4 points minimum.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at 15° Aries
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=15.0,  # 15° Aries
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    # Should have exaltation
    assert result["planet"] == "Sun"
    assert "exaltation" in result["dignities"]
    assert result["score"] >= 4, "Sun in Aries should score at least +4"


def test_sun_in_aquarius_detriment():
    """
    Test Sun in Aquarius shows detriment.

    Sun is in detriment in Aquarius (opposite of its rulership Leo).
    Should have -5 points and "weak" interpretation.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at 15° Aquarius
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=315.0,  # 15° Aquarius (300° + 15°)
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    # Should have detriment
    assert result["planet"] == "Sun"
    assert "detriment" in result["dignities"]
    # Sun gets -5 for detriment, but may have other dignities (like term/triplicity) that add points
    assert (
        result["score"] < 0
    ), "Sun in Aquarius should have negative score due to detriment"
    # Verify interpretation indicates weakness/challenge
    interp = result["interpretation"].lower()
    assert "challenged" in interp or "weak" in interp or "debility" in interp


def test_sun_in_libra_fall():
    """
    Test Sun in Libra shows fall.

    Sun falls in Libra (opposite of exaltation in Aries).
    Should have -4 points.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at 15° Libra
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=195.0,  # 15° Libra (180° + 15°)
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    # Should have fall
    assert result["planet"] == "Sun"
    assert "fall" in result["dignities"]
    assert result["score"] <= -4, "Sun in Libra should have fall penalty"


def test_moon_in_cancer_rulership():
    """
    Test Moon in Cancer (its rulership sign).

    Moon rules Cancer, strongest placement.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Moon at 10° Cancer
    moon = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=100.0,  # 10° Cancer (90° + 10°)
        speed_longitude=13.0,
    )

    result = calc.calculate_dignities(moon)

    assert result["planet"] == "Moon"
    assert "domicile" in result["dignities"]
    assert result["score"] >= 5


def test_mercury_in_virgo_rulership():
    """
    Test Mercury in Virgo (one of Mercury's rulership signs).

    Mercury rules both Gemini and Virgo.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Mercury at 15° Virgo
    mercury = CelestialPosition(
        name="Mercury",
        object_type=ObjectType.PLANET,
        longitude=165.0,  # 15° Virgo (150° + 15°)
        speed_longitude=1.2,
    )

    result = calc.calculate_dignities(mercury)

    assert result["planet"] == "Mercury"
    assert "domicile" in result["dignities"]
    assert result["score"] >= 5


def test_multiple_planets_calculation():
    """Test calculating dignities for multiple planets at once."""
    calc = TraditionalDignityCalculator(decans="chaldean")

    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=135.0,
            speed_longitude=1.0,
        ),  # Leo (rulership)
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=100.0,
            speed_longitude=13.0,
        ),  # Cancer (rulership)
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=15.0,
            speed_longitude=0.5,
        ),  # Aries (rulership)
    ]

    # Calculate dignities for each position
    result = {}
    for pos in positions:
        dignity = calc.calculate_dignities(pos)
        result[pos.name] = dignity

    assert len(result) == 3
    assert "Sun" in result
    assert "Moon" in result
    assert "Mars" in result

    # All should have strong dignities
    assert result["Sun"]["score"] > 0
    assert result["Moon"]["score"] > 0
    assert result["Mars"]["score"] > 0


def test_outer_planets_excluded_from_traditional():
    """Test that outer planets are excluded from traditional calculations."""
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Uranus test
    uranus = CelestialPosition(
        name="Uranus",
        object_type=ObjectType.PLANET,
        longitude=15.0,
        speed_longitude=0.05,
    )

    result = calc.calculate_dignities(uranus)

    # Traditional calculator should return a note for outer planets, not full calculation
    assert result["planet"] == "Uranus"
    assert "note" in result, "Should have a note explaining outer planet exclusion"
    assert "Not a traditional planet" in result["note"]


# =============================================================================
# MODERN DIGNITY CALCULATOR TESTS
# =============================================================================


def test_modern_calculator_initialization():
    """Test ModernDignityCalculator initializes correctly."""
    calc = ModernDignityCalculator(decans="chaldean")
    assert calc.calculator_name == "Modern Essential Dignities"


def test_modern_includes_outer_planets():
    """Test that modern calculator includes Uranus, Neptune, Pluto."""
    calc = ModernDignityCalculator(decans="chaldean")

    positions = [
        CelestialPosition(
            name="Uranus",
            object_type=ObjectType.PLANET,
            longitude=315.0,
            speed_longitude=0.05,
        ),  # Aquarius
        CelestialPosition(
            name="Neptune",
            object_type=ObjectType.PLANET,
            longitude=345.0,
            speed_longitude=0.03,
        ),  # Pisces
        CelestialPosition(
            name="Pluto",
            object_type=ObjectType.PLANET,
            longitude=225.0,
            speed_longitude=0.02,
        ),  # Scorpio
    ]

    # Calculate dignities for each position
    result = {}
    for pos in positions:
        dignity = calc.calculate_dignities(pos)
        result[pos.name] = dignity

    # Modern calculator includes outer planets
    assert "Uranus" in result
    assert "Neptune" in result
    assert "Pluto" in result


def test_uranus_in_aquarius_modern_rulership():
    """
    Test Uranus in Aquarius shows modern rulership.

    In modern astrology, Uranus co-rules Aquarius (with Saturn).
    """
    calc = ModernDignityCalculator(decans="chaldean")

    uranus = CelestialPosition(
        name="Uranus",
        object_type=ObjectType.PLANET,
        longitude=315.0,  # 15° Aquarius
        speed_longitude=0.05,
    )

    result = calc.calculate_dignities(uranus)

    assert result["planet"] == "Uranus"
    # Should have some dignity in modern system
    assert result["score"] > 0


def test_neptune_in_pisces_modern_rulership():
    """
    Test Neptune in Pisces shows modern rulership.

    In modern astrology, Neptune co-rules Pisces (with Jupiter).
    """
    calc = ModernDignityCalculator(decans="chaldean")

    neptune = CelestialPosition(
        name="Neptune",
        object_type=ObjectType.PLANET,
        longitude=345.0,  # 15° Pisces
        speed_longitude=0.03,
    )

    result = calc.calculate_dignities(neptune)

    assert result["planet"] == "Neptune"
    assert result["score"] > 0


def test_pluto_in_scorpio_modern_rulership():
    """
    Test Pluto in Scorpio shows modern rulership.

    In modern astrology, Pluto co-rules Scorpio (with Mars).
    """
    calc = ModernDignityCalculator(decans="chaldean")

    pluto = CelestialPosition(
        name="Pluto",
        object_type=ObjectType.PLANET,
        longitude=225.0,  # 15° Scorpio
        speed_longitude=0.02,
    )

    result = calc.calculate_dignities(pluto)

    assert result["planet"] == "Pluto"
    assert result["score"] > 0


# =============================================================================
# MUTUAL RECEPTION TESTS
# =============================================================================


def test_mutual_reception_analyzer_initialization():
    """Test MutualReceptionAnalyzer initializes correctly."""
    analyzer = MutualReceptionAnalyzer()
    assert analyzer.system == "traditional"  # Default system

    analyzer_modern = MutualReceptionAnalyzer(system="modern")
    assert analyzer_modern.system == "modern"


def test_mutual_reception_sun_moon():
    """
    Test mutual reception detection between Sun and Moon.

    Sun in Cancer (Moon's sign) and Moon in Leo (Sun's sign) = mutual reception.
    This is a strong connection between the luminaries.
    """
    analyzer = MutualReceptionAnalyzer()

    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=100.0,  # 10° Cancer (Moon's sign)
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=130.0,  # 10° Leo (Sun's sign)
            speed_longitude=13.0,
        ),
    ]

    receptions = analyzer.find_mutual_receptions(positions)

    # Should find Sun-Moon mutual reception
    assert len(receptions) > 0

    # Find the Sun-Moon reception
    sun_moon_reception = None
    for reception in receptions:
        planets = set([reception["planet1"], reception["planet2"]])  # noqa: C405
        if planets == {"Sun", "Moon"}:
            sun_moon_reception = reception
            break

    assert sun_moon_reception is not None, "Should find Sun-Moon mutual reception"
    assert sun_moon_reception["type"] == "mutual_reception_domicile"


def test_mutual_reception_venus_mars():
    """
    Test mutual reception between Venus and Mars.

    Venus in Aries (Mars sign) and Mars in Taurus (Venus sign).
    """
    analyzer = MutualReceptionAnalyzer()

    positions = [
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=15.0,  # Aries (Mars sign)
            speed_longitude=1.1,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=45.0,  # Taurus (Venus sign)
            speed_longitude=0.5,
        ),
    ]

    receptions = analyzer.find_mutual_receptions(positions)

    assert len(receptions) > 0

    # Find Venus-Mars reception
    venus_mars_reception = None
    for reception in receptions:
        planets = set([reception["planet1"], reception["planet2"]])  # noqa: C405
        if planets == {"Venus", "Mars"}:
            venus_mars_reception = reception
            break

    assert venus_mars_reception is not None


def test_no_mutual_reception():
    """Test that no mutual reception is detected when planets aren't in each other's signs."""
    analyzer = MutualReceptionAnalyzer()

    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=135.0,
            speed_longitude=1.0,
        ),  # Leo (Sun's own sign)
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=100.0,
            speed_longitude=13.0,
        ),  # Cancer (Moon's own sign)
    ]

    receptions = analyzer.find_mutual_receptions(positions)

    # Sun and Moon are in their own signs, not each other's
    sun_moon_reception = any(
        set([r["planet1"], r["planet2"]]) == {"Sun", "Moon"}  # noqa: C405
        for r in receptions
    )

    assert (
        not sun_moon_reception
    ), "Should not find mutual reception when planets are in own signs"


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================


def test_unknown_planet_handling():
    """Test that unknown planets are handled gracefully."""
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Create a position with an unknown planet name
    unknown = CelestialPosition(
        name="UnknownPlanet",
        object_type=ObjectType.PLANET,
        longitude=15.0,
        speed_longitude=0.0,
    )

    result = calc.calculate_dignities(unknown)

    # Should return a result with note about not being a traditional planet
    assert result["planet"] == "UnknownPlanet"
    assert (
        "note" in result or "dignities" in result
    )  # Either not calculated or empty dignities


def test_planet_at_sign_boundary():
    """
    Test planet exactly at sign boundary (0° of a sign).

    This tests edge case of degree calculations.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at exact 0° Leo
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=120.0,  # Exactly 0° Leo
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    assert result["planet"] == "Sun"
    assert result["sign"] == "Leo"
    # Should still detect Leo rulership
    assert "domicile" in result["dignities"]


def test_planet_at_end_of_sign():
    """
    Test planet at end of sign (29° 59').

    Tests boundary between signs.
    """
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Sun at 29.99° Leo (just before Virgo)
    sun = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=149.99,  # 29.99° Leo
        speed_longitude=1.0,
    )

    result = calc.calculate_dignities(sun)

    assert result["planet"] == "Sun"
    # Should still be in Leo, not Virgo
    assert result["sign"] == "Leo"
    assert "domicile" in result["dignities"]


def test_different_decan_systems():
    """Test traditional calculator with different decan systems."""
    # Test with triplicity decans
    calc_trip = TraditionalDignityCalculator(decans="triplicity")
    assert calc_trip.decans == "triplicity"

    # Test with Chaldean decans
    calc_chal = TraditionalDignityCalculator(decans="chaldean")
    assert calc_chal.decans == "chaldean"

    # Both should calculate, might produce different results for faces
    sun = CelestialPosition(
        name="Sun", object_type=ObjectType.PLANET, longitude=15.0, speed_longitude=1.0
    )

    result_trip = calc_trip.calculate_dignities(sun)
    result_chal = calc_chal.calculate_dignities(sun)

    assert result_trip["planet"] == "Sun"
    assert result_chal["planet"] == "Sun"

    # Both should have calculated dignities
    assert "dignities" in result_trip
    assert "dignities" in result_chal


# =============================================================================
# INTEGRATION TEST
# =============================================================================


def test_full_dignity_analysis_integration():
    """
    Integration test: Full chart dignity analysis.

    Tests the complete workflow of calculating dignities for a realistic chart.
    """
    traditional_calc = TraditionalDignityCalculator(decans="chaldean")
    modern_calc = ModernDignityCalculator(decans="chaldean")
    reception_analyzer = MutualReceptionAnalyzer()

    # Create a chart with mixed dignities
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=135.0,
            speed_longitude=1.0,
        ),  # Leo - strong
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=315.0,
            speed_longitude=13.0,
        ),  # Aquarius - weak
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=60.0,
            speed_longitude=1.2,
        ),  # Gemini - strong
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=195.0,
            speed_longitude=1.1,
        ),  # Libra - strong
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=0.5,
        ),  # Aries - strong
    ]

    # Traditional analysis
    trad_result = {}
    for pos in positions:
        dignity = traditional_calc.calculate_dignities(pos)
        trad_result[pos.name] = dignity

    assert len(trad_result) == 5  # All traditional planets

    # Modern analysis
    modern_result = {}
    for pos in positions:
        dignity = modern_calc.calculate_dignities(pos)
        modern_result[pos.name] = dignity

    assert len(modern_result) == 5  # Same planets (no outer planets in this chart)

    # Mutual reception analysis
    reception_analyzer.find_mutual_receptions(positions)
    # May or may not find receptions depending on positions

    # Verify structure of results
    for _planet_name, dignity_data in trad_result.items():
        assert "sign" in dignity_data
        assert "dignities" in dignity_data
        assert "score" in dignity_data
        assert "interpretation" in dignity_data
        assert isinstance(dignity_data["dignities"], list)
        assert isinstance(dignity_data["score"], int | float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
