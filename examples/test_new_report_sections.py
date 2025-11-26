"""
Test script for new report sections.

Tests:
1. Multi-house-system planet positions
2. House cusps section
3. Dignity section (with and without dignity data)
4. Aspect pattern section (with and without pattern data)
"""

from datetime import datetime

from stellium import ChartBuilder, ReportBuilder
from stellium.components.dignity import DignityComponent
from stellium.engines.houses import PlacidusHouses, WholeSignHouses, KochHouses
from stellium.engines.patterns import AspectPatternAnalyzer


def test_multi_house_systems():
    """Test planet positions with multiple house systems."""
    print("\n" + "=" * 80)
    print("TEST 1: Multi-House System Planet Positions")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .with_house_systems([PlacidusHouses(), WholeSignHouses(), KochHouses()])
        .with_aspects()
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_planet_positions(house_systems="all")  # Should show all 3 systems
    )

    report.render(format="rich_table")


def test_house_cusps():
    """Test house cusps section."""
    print("\n" + "=" * 80)
    print("TEST 2: House Cusps Section")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_house_cusps(systems="all")  # Should show both systems
    )

    report.render(format="rich_table")


def test_dignities_with_data():
    """Test dignity section WITH dignity data."""
    print("\n" + "=" * 80)
    print("TEST 3: Dignities Section (WITH data)")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .add_component(DignityComponent())  # Add dignity calculations
        .with_aspects()
        .calculate()
    )

    # Test score display
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_dignities(essential="both", show_details=False)
    )

    report.render(format="rich_table")

    # Test details display
    print("\n" + "-" * 80)
    print("Same chart, but showing dignity names instead of scores:")
    print("-" * 80)

    report2 = (
        ReportBuilder()
        .from_chart(chart)
        .with_dignities(essential="both", show_details=True)
    )

    report2.render(format="rich_table")


def test_dignities_without_data():
    """Test dignity section WITHOUT dignity data (graceful handling)."""
    print("\n" + "=" * 80)
    print("TEST 4: Dignities Section (WITHOUT data - should show helpful message)")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        # NOT adding DignityComponent
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_dignities()
    )

    report.render(format="rich_table")


def test_aspect_patterns_with_data():
    """Test aspect pattern section WITH pattern data."""
    print("\n" + "=" * 80)
    print("TEST 5: Aspect Patterns Section (WITH data)")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .add_analyzer(AspectPatternAnalyzer())  # Add pattern detection
        .with_aspects()
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_aspect_patterns()
    )

    report.render(format="rich_table")


def test_aspect_patterns_without_data():
    """Test aspect pattern section WITHOUT pattern data (graceful handling)."""
    print("\n" + "=" * 80)
    print("TEST 6: Aspect Patterns Section (WITHOUT data - should show helpful message)")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        # NOT adding AspectPatternAnalyzer
        .with_aspects()
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_aspect_patterns()
    )

    report.render(format="rich_table")


def test_comprehensive_report():
    """Test a comprehensive report with ALL new sections."""
    print("\n" + "=" * 80)
    print("TEST 7: Comprehensive Report (ALL sections)")
    print("=" * 80)

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA", name="Kate Louie")
        .with_house_systems([PlacidusHouses(), WholeSignHouses(), KochHouses()])
        .add_component(DignityComponent())
        .add_analyzer(AspectPatternAnalyzer())
        .with_aspects()
        .calculate()
    )

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_planet_positions(house_systems="all")
        .with_house_cusps(systems="all")
        .with_dignities(essential="both")
        .with_aspect_patterns()
        .with_aspects(mode="major")
    )

    report.render(format="rich_table")


if __name__ == "__main__":
    print("Testing new report sections...")

    test_multi_house_systems()
    test_house_cusps()
    test_dignities_with_data()
    test_dignities_without_data()
    test_aspect_patterns_with_data()
    test_aspect_patterns_without_data()
    test_comprehensive_report()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE!")
    print("=" * 80)
