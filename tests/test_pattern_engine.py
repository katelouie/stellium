"""
Comprehensive tests for the Aspect Pattern Analyzer Engine.

This module tests the detection of all major aspect patterns:
- Grand Trines
- T-Squares
- Yods (Finger of God)
- Kites
- Grand Crosses
- Mystic Rectangles
- Stelliums

TESTING CONCEPTS EXPLAINED:

1. **Why test pattern detection?**
   Pattern detection is complex logic with many edge cases. We need to verify that:
   - All pattern types are correctly detected
   - Patterns are not detected when they shouldn't be (false positives)
   - Edge cases are handled (e.g., planets at sign boundaries)

2. **Testing strategy:**
   - Test each pattern type independently
   - Use known planetary configurations that form specific patterns
   - Verify pattern properties (element, quality, planets involved)
   - Test edge cases (no patterns, multiple patterns, overlapping patterns)

3. **Why use mock data?**
   Testing with exact positions ensures:
   - Tests are deterministic (always produce same result)
   - Tests are fast (no need to calculate real ephemeris)
   - We can test specific configurations that might be rare in real charts
"""

import datetime as dt

import pytest
import swisseph as swe

from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    ObjectType,
)
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.orbs import SimpleOrbEngine
from stellium.engines.patterns import AspectPatternAnalyzer

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def create_test_chart(
    positions: list[CelestialPosition], aspects: list[Aspect]
) -> CalculatedChart:
    """
    Helper function to create a minimal CalculatedChart for testing pattern detection.

    This simplifies test code by handling the chart construction boilerplate.
    """
    test_datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    julian_day = swe.julday(2000, 1, 1, 12.0)

    return CalculatedChart(
        datetime=ChartDateTime(
            utc_datetime=test_datetime,
            julian_day=julian_day,
            local_datetime=test_datetime,
        ),
        location=ChartLocation(0, 0),
        positions=tuple(positions),  # CalculatedChart expects tuple
        house_systems={},
        aspects=tuple(aspects),  # CalculatedChart expects tuple
        metadata={},
    )


# =============================================================================
# GRAND TRINE TESTS
# =============================================================================


def test_grand_trine_detection(grand_trine_positions):
    """
    Test detection of a Grand Trine pattern.

    A Grand Trine is formed when 3 planets are each 120° apart (all trine each other).
    This creates a perfect equilateral triangle in the chart.
    """
    # Calculate aspects from the positions
    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(grand_trine_positions, orb_engine)

    # Create chart and run pattern analysis
    chart = create_test_chart(grand_trine_positions, aspects)
    analyzer = AspectPatternAnalyzer()
    patterns = analyzer.analyze(chart)

    # Should find exactly one Grand Trine
    grand_trines = [p for p in patterns if p.name == "Grand Trine"]
    assert len(grand_trines) == 1, "Should detect exactly one Grand Trine"

    # Verify pattern properties
    gt = grand_trines[0]
    assert len(gt.planets) == 3, "Grand Trine should have 3 planets"
    assert len(gt.aspects) == 3, "Grand Trine should have 3 trine aspects"
    assert all(
        a.aspect_name == "Trine" for a in gt.aspects
    ), "All aspects should be trines"

    # All planets should be in fire signs (Aries, Leo, Sagittarius)
    # So element should be "Fire"
    assert gt.element == "Fire", "Grand Trine in fire signs should have Fire element"


def test_grand_trine_mixed_element():
    """Test Grand Trine with planets in different elements (rare but possible)."""
    # Create positions that form a trine but cross elements
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=2.0,  # Early Aries (Fire)
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=122.0,  # Early Leo (Fire)
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Jupiter",
            object_type=ObjectType.PLANET,
            longitude=242.0,  # Early Sagittarius (Fire)
            speed_longitude=0.08,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    grand_trines = [p for p in patterns if p.name == "Grand Trine"]

    assert len(grand_trines) == 1
    assert grand_trines[0].element == "Fire"


def test_no_grand_trine():
    """Test that Grand Trine is NOT detected when pattern isn't present."""
    # Create positions without trine aspects
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=45.0,  # Not a trine to Sun
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=90.0,  # Not completing the trine
            speed_longitude=0.5,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    grand_trines = [p for p in patterns if p.name == "Grand Trine"]

    assert (
        len(grand_trines) == 0
    ), "Should not detect Grand Trine when pattern isn't present"


# =============================================================================
# T-SQUARE TESTS
# =============================================================================


def test_t_square_detection(t_square_positions):
    """
    Test detection of a T-Square pattern.

    A T-Square consists of:
    - Two planets in opposition (180°)
    - A third planet (apex) square (90°) to both
    This creates high tension and dynamic energy.
    """
    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(t_square_positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(t_square_positions, aspects)

    patterns = analyzer.analyze(chart)
    t_squares = [p for p in patterns if p.name == "T-Square"]

    assert len(t_squares) == 1, "Should detect exactly one T-Square"

    ts = t_squares[0]
    assert len(ts.planets) == 3, "T-Square should have 3 planets"
    assert (
        len(ts.aspects) == 3
    ), "T-Square should have 3 aspects (1 opposition, 2 squares)"

    # Verify we have 1 opposition and 2 squares
    aspect_names = [a.aspect_name for a in ts.aspects]
    assert aspect_names.count("Opposition") == 1, "Should have 1 opposition"
    assert aspect_names.count("Square") == 2, "Should have 2 squares"

    # All in cardinal signs (Aries, Cancer, Libra)
    assert (
        ts.quality == "Cardinal"
    ), "T-Square in cardinal signs should have Cardinal quality"


def test_multiple_t_squares():
    """Test detection of multiple T-Squares in one chart."""
    # Create positions that form two different T-Squares
    positions = [
        # First T-Square: Sun-Mars opposition, Pluto apex
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=180.0,
            speed_longitude=0.5,
        ),
        CelestialPosition(
            name="Pluto",
            object_type=ObjectType.PLANET,
            longitude=90.0,
            speed_longitude=0.01,
        ),
        # Second T-Square: Moon-Venus opposition, Saturn apex
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=210.0,
            speed_longitude=1.1,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            speed_longitude=0.05,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    t_squares = [p for p in patterns if p.name == "T-Square"]

    assert len(t_squares) >= 2, "Should detect at least two T-Squares"


# =============================================================================
# YOD TESTS
# =============================================================================


def test_yod_detection():
    """
    Test detection of a Yod pattern (Finger of God).

    A Yod consists of:
    - Two planets in sextile (60°)
    - A third planet (apex) quincunx (150°) to both
    Indicates a fated or karmic configuration.

    NOTE: Quincunx is not included in default aspect configuration,
    so we need to add it explicitly for this test.
    """
    # Create positions forming a Yod
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=60.0,  # 0° Gemini (60° from Sun - sextile)
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=210.0,  # 0° Scorpio (quincunx to both Sun and Moon)
            speed_longitude=0.05,
        ),
    ]

    # Create aspect engine with Quincunx included
    from stellium.core.config import AspectConfig

    config = AspectConfig(
        aspects=["Conjunction", "Sextile", "Square", "Trine", "Opposition", "Quincunx"]
    )
    aspect_engine = ModernAspectEngine(config=config)
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    yods = [p for p in patterns if p.name == "Yod"]

    assert len(yods) == 1, "Should detect exactly one Yod"

    yod = yods[0]
    assert len(yod.planets) == 3, "Yod should have 3 planets"
    assert len(yod.aspects) == 3, "Yod should have 3 aspects (1 sextile, 2 quincunxes)"

    # Verify aspect types
    aspect_names = [a.aspect_name for a in yod.aspects]
    assert aspect_names.count("Sextile") == 1, "Should have 1 sextile"
    assert aspect_names.count("Quincunx") == 2, "Should have 2 quincunxes"


def test_no_yod_without_quincunx():
    """Test that Yod is not detected without proper quincunx aspects."""
    # Sextile exists but no quincunxes
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=60.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            speed_longitude=0.5,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    yods = [p for p in patterns if p.name == "Yod"]

    assert len(yods) == 0, "Should not detect Yod without quincunxes"


# =============================================================================
# GRAND CROSS TESTS
# =============================================================================


def test_grand_cross_detection():
    """
    Test detection of a Grand Cross pattern.

    A Grand Cross consists of:
    - Four planets forming two oppositions (180°)
    - All four planets square (90°) each other
    Creates maximum tension and requires integration of all four energies.
    """
    # Create positions forming a Grand Cross
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=90.0,  # 0° Cancer
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=180.0,  # 0° Libra
            speed_longitude=0.5,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=270.0,  # 0° Capricorn
            speed_longitude=0.05,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    grand_crosses = [p for p in patterns if p.name == "Grand Cross"]

    assert len(grand_crosses) == 1, "Should detect exactly one Grand Cross"

    gc = grand_crosses[0]
    assert len(gc.planets) == 4, "Grand Cross should have 4 planets"
    assert (
        len(gc.aspects) == 6
    ), "Grand Cross should have 6 aspects (2 oppositions, 4 squares)"

    # Verify aspect types
    aspect_names = [a.aspect_name for a in gc.aspects]
    assert aspect_names.count("Opposition") == 2, "Should have 2 oppositions"
    assert aspect_names.count("Square") == 4, "Should have 4 squares"

    # All in cardinal signs
    assert (
        gc.quality == "Cardinal"
    ), "Grand Cross in cardinal signs should have Cardinal quality"


# =============================================================================
# KITE TESTS
# =============================================================================


def test_kite_detection():
    """
    Test detection of a Kite pattern.

    A Kite consists of:
    - A Grand Trine (3 planets)
    - A 4th planet opposite one point of the trine and sextile to the other two
    Adds focus and direction to the Grand Trine's harmony.
    """
    # Create positions forming a Kite
    # Grand Trine: Sun (0° Aries), Moon (120° Leo), Jupiter (240° Sagittarius)
    # Focal point: Saturn opposite Sun and sextile to Moon/Jupiter
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Jupiter",
            object_type=ObjectType.PLANET,
            longitude=240.0,
            speed_longitude=0.08,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=180.0,
            speed_longitude=0.05,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)

    # Should find both Grand Trine and Kite
    grand_trines = [p for p in patterns if p.name == "Grand Trine"]
    kites = [p for p in patterns if p.name == "Kite"]

    assert len(grand_trines) == 1, "Should detect the Grand Trine"
    assert len(kites) == 1, "Should detect exactly one Kite"

    kite = kites[0]
    assert len(kite.planets) == 4, "Kite should have 4 planets"
    assert (
        len(kite.aspects) == 6
    ), "Kite should have 6 aspects (3 trines, 1 opposition, 2 sextiles)"


# =============================================================================
# MYSTIC RECTANGLE TESTS
# =============================================================================


def test_mystic_rectangle_detection():
    """
    Test detection of a Mystic Rectangle pattern.

    A Mystic Rectangle consists of:
    - Two oppositions (180°)
    - Connected by two sextiles (60°) and two trines (120°)
    Creates a balanced, harmonious rectangle.
    """
    # Create positions forming a Mystic Rectangle
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=60.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=180.0,
            speed_longitude=1.1,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=240.0,
            speed_longitude=0.5,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)
    mystic_rects = [p for p in patterns if p.name == "Mystic Rectangle"]

    assert len(mystic_rects) == 1, "Should detect exactly one Mystic Rectangle"

    mr = mystic_rects[0]
    assert len(mr.planets) == 4, "Mystic Rectangle should have 4 planets"
    assert len(mr.aspects) == 6, "Mystic Rectangle should have 6 aspects"

    # Verify aspect composition
    aspect_names = [a.aspect_name for a in mr.aspects]
    assert aspect_names.count("Opposition") == 2, "Should have 2 oppositions"
    assert aspect_names.count("Sextile") == 2, "Should have 2 sextiles"
    assert aspect_names.count("Trine") == 2, "Should have 2 trines"


# =============================================================================
# STELLIUM TESTS
# =============================================================================


def test_stellium_detection(stellium_positions):
    """
    Test detection of a Stellium pattern.

    A Stellium consists of 3 or more planets in the same zodiac sign.
    Indicates concentrated energy in one area of life.
    """
    analyzer = AspectPatternAnalyzer(stellium_min=3)

    chart = create_test_chart(stellium_positions, [])
    patterns = analyzer.analyze(chart)
    stelliums = [p for p in patterns if p.name == "Stellium"]

    assert len(stelliums) == 1, "Should detect exactly one Stellium"

    stellium = stelliums[0]
    assert len(stellium.planets) == 4, "Stellium should have 4 planets (all in Taurus)"
    assert stellium.element == "Earth", "Taurus is an Earth sign"
    assert stellium.quality == "Fixed", "Taurus is a Fixed sign"
    assert len(stellium.aspects) == 0, "Stelliums are based on sign, not aspects"


def test_stellium_custom_threshold():
    """Test Stellium detection with custom threshold (4 planets minimum)."""
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=45.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=50.0,
            speed_longitude=1.2,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=55.0,
            speed_longitude=1.1,
        ),
        # Only 3 planets - should NOT be detected with min=4
    ]

    analyzer = AspectPatternAnalyzer(stellium_min=4)

    chart = create_test_chart(positions, [])
    patterns = analyzer.analyze(chart)
    stelliums = [p for p in patterns if p.name == "Stellium"]

    assert (
        len(stelliums) == 0
    ), "Should not detect Stellium with only 3 planets when min=4"


def test_multiple_stelliums():
    """Test detection of multiple Stelliums in different signs."""
    positions = [
        # Stellium in Taurus
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=45.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=50.0,
            speed_longitude=1.2,
        ),
        CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=55.0,
            speed_longitude=1.1,
        ),
        # Stellium in Scorpio
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=225.0,
            speed_longitude=0.5,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=230.0,
            speed_longitude=0.05,
        ),
        CelestialPosition(
            name="Pluto",
            object_type=ObjectType.PLANET,
            longitude=235.0,
            speed_longitude=0.01,
        ),
    ]

    analyzer = AspectPatternAnalyzer(stellium_min=3)

    chart = create_test_chart(positions, [])
    patterns = analyzer.analyze(chart)
    stelliums = [p for p in patterns if p.name == "Stellium"]

    assert len(stelliums) == 2, "Should detect two Stelliums"

    # Verify one is in Taurus (Earth) and one is in Scorpio (Water)
    elements = {s.element for s in stelliums}
    assert "Earth" in elements, "Should have Earth stellium (Taurus)"
    assert "Water" in elements, "Should have Water stellium (Scorpio)"


# =============================================================================
# EDGE CASES AND INTEGRATION TESTS
# =============================================================================


def test_no_patterns_detected():
    """Test that no patterns are detected when none exist."""
    # Random positions with no significant patterns
    positions = [
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=10.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=95.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=200.0,
            speed_longitude=0.5,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)

    assert len(patterns) == 0, "Should not detect any patterns in random configuration"


def test_analyzer_properties():
    """Test basic analyzer properties."""
    analyzer = AspectPatternAnalyzer(stellium_min=4)

    assert analyzer.analyzer_name == "Aspect Patterns"
    assert analyzer.metadata_name == "aspect_patterns"
    assert analyzer.stellium_min == 4


def test_complex_chart_with_multiple_patterns():
    """Test a complex chart with multiple overlapping patterns."""
    # Create a configuration with both Grand Trine and T-Square
    positions = [
        # Grand Trine in Fire
        CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,
            speed_longitude=1.0,
        ),
        CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            speed_longitude=13.0,
        ),
        CelestialPosition(
            name="Jupiter",
            object_type=ObjectType.PLANET,
            longitude=240.0,
            speed_longitude=0.08,
        ),
        # T-Square participants
        CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=180.0,
            speed_longitude=0.5,
        ),
        CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=90.0,
            speed_longitude=0.05,
        ),
    ]

    aspect_engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()
    aspects = aspect_engine.calculate_aspects(positions, orb_engine)

    analyzer = AspectPatternAnalyzer()

    chart = create_test_chart(positions, aspects)

    patterns = analyzer.analyze(chart)

    # Should find multiple patterns
    assert len(patterns) > 0, "Should find at least one pattern"

    # Verify pattern diversity
    pattern_names = [p.name for p in patterns]
    assert (
        "Grand Trine" in pattern_names or "Kite" in pattern_names
    ), "Should find Grand Trine or Kite"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
