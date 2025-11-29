#!/usr/bin/env python3
"""
Profections Cookbook - Hellenistic Annual Timing Technique

This cookbook demonstrates how to use Stellium's profection engine.
Profections are a Hellenistic timing technique where the Ascendant
(and other points) move forward one sign per year of life.

Key concepts:
- Annual Profection: Which house/sign is activated for this year of life?
- Lord of the Year: The planet ruling the profected sign
- Monthly Profections: Subdivide the year using solar ingress
- Multi-Point: Profect ASC, Sun, Moon, MC simultaneously

Run this script to see profection examples in action.

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/profections_cookbook.py

For full documentation, see docs/development/profections.md
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ProfectionEngine
from stellium.engines import PlacidusHouses, WholeSignHouses

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "profections"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC ANNUAL PROFECTIONS
# =============================================================================


def example_1_simple_annual_profection():
    """
    Example 1: Simple Annual Profection

    Calculate which house and sign are activated for a given age,
    and who the Lord of the Year is.
    """
    section_header("Example 1: Simple Annual Profection")

    # Create the natal chart (Einstein had Cancer Rising)
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()

    print(f"Einstein's Ascendant: {natal.get_object('ASC').sign}")
    print(f"  at {natal.get_object('ASC').longitude:.2f}°")

    # Create profection engine
    engine = ProfectionEngine(natal)

    # Age 26 - Einstein's "Miracle Year" (1905)
    result = engine.annual(26)

    print("\nAge 26 Profection (1905 - Miracle Year):")
    print(f"  Profected House: {result.profected_house}")
    print(f"  Profected Sign: {result.profected_sign}")
    print(f"  Lord of the Year: {result.ruler}")

    # Where is the Lord natally?
    if result.ruler_position:
        print(f"\n  {result.ruler} natally:")
        print(f"    Position: {result.ruler_position.longitude:.2f}° {result.ruler_position.sign}")
        print(f"    House: {result.ruler_house}")


def example_2_profection_cycle():
    """
    Example 2: The 12-Year Profection Cycle

    Profections repeat every 12 years. Let's see the pattern.
    """
    section_header("Example 2: The 12-Year Profection Cycle")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).with_house_systems([WholeSignHouses()]).calculate()

    engine = ProfectionEngine(natal)

    print("Kate's 12-year profection cycle:\n")
    print(f"{'Age':<6} {'House':<8} {'Sign':<14} {'Lord':<10}")
    print("-" * 42)

    for age in range(12):
        result = engine.annual(age)
        print(f"{age:<6} {result.profected_house:<8} {result.profected_sign:<14} {result.ruler:<10}")

    print("\n(This pattern repeats at ages 12-23, 24-35, etc.)")


def example_3_lord_of_year():
    """
    Example 3: Quick Lord of the Year Access

    Sometimes you just need the Lord, not all the details.
    """
    section_header("Example 3: Quick Lord of the Year Access")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    ages = [25, 30, 35, 40]
    print("Lords of the Year for key ages:\n")

    for age in ages:
        lord = engine.lord_of_year(age)
        print(f"  Age {age}: {lord}")


def example_4_chart_convenience_methods():
    """
    Example 4: Using Chart Convenience Methods

    CalculatedChart has profection methods built in for quick access.
    """
    section_header("Example 4: Chart Convenience Methods")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Direct methods on chart
    print("Using chart convenience methods:\n")

    # Simple lord access
    lord = chart.lord_of_year(26)
    print(f"Einstein's Lord at age 26: {lord}")

    # Full profection result
    result = chart.profection(age=26, include_monthly=False)
    print("\nFull profection details:")
    print(f"  House: {result.profected_house}")
    print(f"  Sign: {result.profected_sign}")
    print(f"  Lord: {result.ruler}")


# =============================================================================
# PART 2: PROFECTION DETAILS
# =============================================================================


def example_5_planets_in_profected_house():
    """
    Example 5: Finding Planets in the Profected House

    When natal planets are in the activated house, they become
    especially important for that year.
    """
    section_header("Example 5: Planets in Profected House")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    print("Scanning for years with natal planets in profected house:\n")

    for age in range(36):
        result = engine.annual(age)
        if result.planets_in_house:
            planets = ", ".join(p.name for p in result.planets_in_house)
            print(f"Age {age}: House {result.profected_house} ({result.profected_sign})")
            print(f"         Planets present: {planets}")
            print()


def example_6_ruler_details():
    """
    Example 6: Full Ruler Analysis

    Get complete details about the Lord of the Year's natal placement.
    """
    section_header("Example 6: Full Ruler Analysis")

    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = ProfectionEngine(natal)

    result = engine.annual(26)

    print(f"Age 26: House {result.profected_house} ({result.profected_sign}) Year")
    print(f"Lord of the Year: {result.ruler}\n")

    if result.ruler_position:
        pos = result.ruler_position
        print(f"{result.ruler}'s natal condition:")
        print(f"  Longitude: {pos.longitude:.4f}°")
        print(f"  Sign: {pos.sign} ({pos.sign_degree:.2f}°)")
        print(f"  House: {result.ruler_house}")
        print(f"  Speed: {pos.speed_longitude:.4f}°/day")
        print(f"  Retrograde: {pos.is_retrograde}")

    # Modern ruler if different
    if result.ruler_modern:
        print(f"\n  (Modern ruler: {result.ruler_modern})")


# =============================================================================
# PART 3: TRADITIONAL VS MODERN RULERS
# =============================================================================


def example_7_traditional_vs_modern():
    """
    Example 7: Traditional vs Modern Rulership

    Traditional astrology uses only the classical planets (Sun-Saturn).
    Modern astrology assigns Uranus, Neptune, Pluto as co-rulers.
    """
    section_header("Example 7: Traditional vs Modern Rulers")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    # Traditional engine (default)
    trad = ProfectionEngine(natal, rulership="traditional")

    # Modern engine
    modern = ProfectionEngine(natal, rulership="modern")

    print("Comparing rulership systems:\n")
    print(f"{'Age':<6} {'Sign':<14} {'Traditional':<12} {'Modern':<12}")
    print("-" * 48)

    for age in range(12):
        trad_result = trad.annual(age)
        mod_result = modern.annual(age)

        # Only show when they differ
        if trad_result.ruler != mod_result.ruler:
            marker = " *"
        else:
            marker = ""

        print(f"{age:<6} {trad_result.profected_sign:<14} "
              f"{trad_result.ruler:<12} {mod_result.ruler:<12}{marker}")

    print("\n* = different rulers (Scorpio, Aquarius, Pisces)")


# =============================================================================
# PART 4: MONTHLY PROFECTIONS
# =============================================================================


def example_8_monthly_profections():
    """
    Example 8: Monthly Profections

    Each year can be subdivided into 12 months, advancing one
    sign per month.
    """
    section_header("Example 8: Monthly Profections")

    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = ProfectionEngine(natal)

    print("Einstein at age 26, monthly breakdown:\n")
    print(f"{'Month':<8} {'House':<8} {'Sign':<14} {'Lord':<10}")
    print("-" * 42)

    for month in range(12):
        result = engine.monthly(26, month)
        print(f"{month:<8} {result.profected_house:<8} "
              f"{result.profected_sign:<14} {result.ruler:<10}")


def example_9_solar_ingress_monthly():
    """
    Example 9: Date-Based Profections (Solar Ingress)

    When you specify a date, monthly profections use the solar
    ingress method - each month starts when the Sun enters a new sign.
    """
    section_header("Example 9: Date-Based Profections")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).with_house_systems([WholeSignHouses()]).calculate()

    engine = ProfectionEngine(natal)

    # Get profections for a specific date
    annual, monthly = engine.for_date("2025-06-15")

    print("Profections for June 15, 2025:\n")
    print("Annual profection:")
    print(f"  Age: {annual.units}")
    print(f"  House: {annual.profected_house} ({annual.profected_sign})")
    print(f"  Lord of Year: {annual.ruler}")

    print("\nMonthly profection:")
    print(f"  Month: {monthly.units - annual.units}")
    print(f"  House: {monthly.profected_house} ({monthly.profected_sign})")
    print(f"  Lord of Month: {monthly.ruler}")


def example_10_chart_for_date():
    """
    Example 10: Chart Convenience - Profection by Date

    Use the chart's built-in method to get profections for any date.
    """
    section_header("Example 10: Chart Convenience - By Date")

    chart = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    # Get both annual and monthly
    annual, monthly = chart.profection(date="2025-06-15")

    print("Profections for June 15, 2025:")
    print(f"\n  Annual Lord: {annual.ruler}")
    print(f"  Monthly Lord: {monthly.ruler}")

    # Just annual (skip monthly calculation)
    just_annual = chart.profection(date="2025-06-15", include_monthly=False)
    print(f"\n  Or just annual: {just_annual.ruler}")


# =============================================================================
# PART 5: MULTI-POINT PROFECTIONS
# =============================================================================


def example_11_multi_point():
    """
    Example 11: Multi-Point Profections

    Profect ASC, Sun, Moon, and MC all at once to see which
    planets are activated from multiple perspectives.
    """
    section_header("Example 11: Multi-Point Profections")

    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = ProfectionEngine(natal)

    result = engine.multi(26)

    print("Age 26 - All Lords at a Glance:\n")
    for point, lord in result.lords.items():
        print(f"  {point:>5} Lord: {lord}")

    print("\nActivated Houses:")
    for point, house in result.activated_houses.items():
        print(f"  {point:>5}: House {house}")


def example_12_custom_points():
    """
    Example 12: Custom Points to Profect

    You can profect any point - not just the defaults.
    """
    section_header("Example 12: Custom Points")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    # Profect Venus and Mars specifically
    custom_points = ["ASC", "Venus", "Mars", "Saturn"]
    result = engine.multi(30, points=custom_points)

    print("Custom profection at age 30:\n")
    for point, lord in result.lords.items():
        print(f"  {point:>8} → Lord: {lord}")


def example_13_chart_multi():
    """
    Example 13: Chart Convenience - Multi-Point

    Use the chart's built-in method for multi-point profections.
    """
    section_header("Example 13: Chart Multi-Point")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    result = chart.profections(age=26)

    print("Einstein at age 26:\n")
    print(f"  Lords: {result.lords}")


# =============================================================================
# PART 6: PROFECTION TIMELINES
# =============================================================================


def example_14_timeline():
    """
    Example 14: Profection Timeline

    Generate profections for a range of ages to see the sequence
    of Lords through time.
    """
    section_header("Example 14: Profection Timeline")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    timeline = engine.timeline(25, 40)

    print("Kate's profection timeline (ages 25-40):\n")
    print(f"{'Age':<6} {'House':<8} {'Sign':<14} {'Lord':<10}")
    print("-" * 42)

    for entry in timeline.entries:
        print(f"{entry.units:<6} {entry.profected_house:<8} "
              f"{entry.profected_sign:<14} {entry.ruler:<10}")


def example_15_find_lord_years():
    """
    Example 15: Find Years by Lord

    Find all the years when a specific planet is Lord of the Year.
    """
    section_header("Example 15: Find Years by Lord")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    timeline = engine.timeline(0, 48)  # First 48 years

    # Find all Saturn years
    saturn_years = timeline.find_by_lord("Saturn")

    print("Saturn Years in first 48 years of life:\n")
    for entry in saturn_years:
        print(f"  Age {entry.units}: House {entry.profected_house} ({entry.profected_sign})")


def example_16_lords_sequence():
    """
    Example 16: Sequence of Lords

    Get just the sequence of Lords for visualization or analysis.
    """
    section_header("Example 16: Lords Sequence")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    timeline = engine.timeline(0, 11)
    lords = timeline.lords_sequence()

    print("12-year Lord sequence:\n")
    print(" → ".join(lords))


def example_17_chart_timeline():
    """
    Example 17: Chart Convenience - Timeline

    Use the chart's built-in method for timeline generation.
    """
    section_header("Example 17: Chart Timeline")

    chart = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    timeline = chart.profection_timeline(25, 35)

    print("Kate's timeline (chart convenience method):")
    print(f"\n  Point: {timeline.point}")
    print(f"  Ages: {timeline.start_age} to {timeline.end_age}")
    print(f"  Lords: {' → '.join(timeline.lords_sequence())}")


# =============================================================================
# PART 7: HOUSE SYSTEM OPTIONS
# =============================================================================


def example_18_whole_sign_default():
    """
    Example 18: Whole Sign Houses (Traditional Default)

    Profections traditionally use Whole Sign houses. The engine
    prefers Whole Sign if available in the chart.
    """
    section_header("Example 18: Whole Sign Houses")

    # Build chart with Whole Sign houses
    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).with_house_systems(
        [WholeSignHouses()]
    ).calculate()

    engine = ProfectionEngine(natal)

    print(f"House system used: {engine.house_system}\n")

    result = engine.annual(30)
    print("Age 30:")
    print(f"  House {result.profected_house}: {result.profected_sign}")
    print(f"  Lord: {result.ruler}")


def example_19_explicit_house_system():
    """
    Example 19: Explicit House System

    You can specify any house system for profections,
    though Whole Sign is traditional.
    """
    section_header("Example 19: Explicit House System")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).with_house_systems(
        [PlacidusHouses(), WholeSignHouses()]
    ).calculate()

    # Force Placidus (non-traditional but possible)
    engine = ProfectionEngine(natal, house_system="Placidus")

    print(f"House system used: {engine.house_system}\n")

    result = engine.annual(30)
    print("Age 30 (Placidus):")
    print(f"  House {result.profected_house}: {result.profected_sign}")
    print(f"  Lord: {result.ruler}")


# =============================================================================
# PART 8: PROFECTING OTHER POINTS
# =============================================================================


def example_20_profecting_sun():
    """
    Example 20: Profecting the Sun

    The Sun's profected position shows which area of life
    illuminates your vitality and purpose for the year.
    """
    section_header("Example 20: Profecting the Sun")

    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = ProfectionEngine(natal)

    # Profect the Sun instead of ASC
    result = engine.annual(26, point="Sun")

    print("Einstein's Sun profection at age 26:")
    print(f"\n  Source: {result.source_point}")
    print(f"  Source sign: {result.source_sign}")
    print(f"  Source house: {result.source_house}")
    print(f"\n  Profected to House: {result.profected_house}")
    print(f"  Profected sign: {result.profected_sign}")
    print(f"  Solar Lord of Year: {result.ruler}")


def example_21_profecting_moon():
    """
    Example 21: Profecting the Moon

    The Moon's profection shows emotional themes and needs.
    """
    section_header("Example 21: Profecting the Moon")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()
    engine = ProfectionEngine(natal)

    result = engine.annual(30, point="Moon")

    print("Kate's Moon profection at age 30:")
    print(f"\n  Moon is natally in: {result.source_sign}")
    print(f"  Profected to: {result.profected_sign}")
    print(f"  Lunar Lord of Year: {result.ruler}")


def example_22_profecting_mc():
    """
    Example 22: Profecting the MC

    The MC's profection shows career and public life themes.
    """
    section_header("Example 22: Profecting the MC")

    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = ProfectionEngine(natal)

    result = engine.annual(26, point="MC")

    print("Einstein's MC profection at age 26:")
    print(f"\n  MC is natally in: {result.source_sign}")
    print(f"  Profected to: {result.profected_sign}")
    print(f"  Career Lord of Year: {result.ruler}")


# =============================================================================
# PART 9: PUTTING IT ALL TOGETHER
# =============================================================================


def example_23_comprehensive_reading():
    """
    Example 23: Comprehensive Annual Profection Reading

    Combine multiple techniques for a full profection analysis.
    """
    section_header("Example 23: Comprehensive Reading")

    natal = ChartBuilder.from_notable("Albert Einstein").with_house_systems(
        [WholeSignHouses()]
    ).calculate()

    age = 26
    engine = ProfectionEngine(natal)

    print(f"EINSTEIN AGE {age} - COMPREHENSIVE PROFECTION ANALYSIS")
    print("=" * 50)

    # Multi-point profection
    multi = engine.multi(age)
    print(f"\nAll Lords at Age {age}:")
    for point, lord in multi.lords.items():
        print(f"  {point:>5}: {lord}")

    # Detailed ASC profection
    result = engine.annual(age)
    print("\nASC Profection Details:")
    print(f"  Activated House: {result.profected_house}")
    print(f"  Activated Sign: {result.profected_sign}")
    print(f"  Lord of Year: {result.ruler}")

    if result.ruler_position:
        print("\n  Lord's Natal Condition:")
        print(f"    Sign: {result.ruler_position.sign}")
        print(f"    House: {result.ruler_house}")

    if result.planets_in_house:
        planets = ", ".join(p.name for p in result.planets_in_house)
        print(f"\n  Natal Planets in House {result.profected_house}: {planets}")

    # Monthly
    print(f"\n\nMonthly Lords (Age {age}):")
    for month in range(12):
        monthly = engine.monthly(age, month)
        print(f"  Month {month:>2}: {monthly.ruler} ({monthly.profected_sign})")


def example_24_output_file():
    """
    Example 24: Save Profection Analysis to File

    Generate a complete profection analysis and save it.
    """
    section_header("Example 24: Save to File")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).with_house_systems(
        [WholeSignHouses()]
    ).calculate()

    engine = ProfectionEngine(natal)

    output_file = OUTPUT_DIR / "kate_profections.txt"

    with open(output_file, "w") as f:
        f.write("KATE'S PROFECTION TIMELINE\n")
        f.write("=" * 40 + "\n\n")

        timeline = engine.timeline(25, 40)
        for entry in timeline.entries:
            f.write(f"Age {entry.units}: House {entry.profected_house} ")
            f.write(f"({entry.profected_sign}) - Lord: {entry.ruler}\n")

        f.write("\n\nLORD YEARS\n")
        f.write("-" * 40 + "\n")

        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            years = timeline.find_by_lord(planet)
            if years:
                ages = [str(e.units) for e in years]
                f.write(f"{planet}: ages {', '.join(ages)}\n")

    print(f"Created: {output_file}")


# =============================================================================
# PART 10: REPORT BUILDER INTEGRATION
# =============================================================================


def example_25_basic_profection_report():
    """
    Example 25: Basic Profection Report

    Use ReportBuilder to generate formatted profection output.
    """
    section_header("Example 25: Basic Profection Report")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Create report with profections section
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_profections(age=26)
    )

    # Display in terminal
    report.render(format="rich_table")


def example_26_profection_report_with_timeline():
    """
    Example 26: Profection Report with Timeline

    Include a timeline showing Lords across multiple years.
    """
    section_header("Example 26: Report with Timeline")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    # Include timeline with custom range
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_profections(
            age=30,
            include_timeline=True,
            timeline_range=(25, 40),  # Show ages 25-40
        )
    )

    report.render(format="rich_table")


def example_27_profection_report_by_date():
    """
    Example 27: Profection Report by Date

    Get both annual and monthly profections for a specific date.
    """
    section_header("Example 27: Report by Date")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    # Use date instead of age - gets annual AND monthly
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_profections(
            date="2025-06-15",
            include_monthly=True,
            include_multi_point=True,
        )
    )

    report.render(format="rich_table")


def example_28_profection_report_custom_points():
    """
    Example 28: Custom Points in Report

    Specify which points to include in multi-point analysis.
    """
    section_header("Example 28: Custom Points Report")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Custom points for multi-point analysis
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_profections(
            age=26,
            points=["ASC", "Sun", "Moon", "MC", "Venus", "Mars"],
            include_timeline=False,
        )
    )

    report.render(format="rich_table")


def example_29_profection_report_modern_rulers():
    """
    Example 29: Modern Rulership in Report

    Use modern rulers (Uranus, Neptune, Pluto) instead of traditional.
    """
    section_header("Example 29: Modern Rulers Report")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate"
    ).calculate()

    # Use modern rulership
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_profections(
            age=30,
            rulership="modern",  # Scorpio=Pluto, Aquarius=Uranus, Pisces=Neptune
            include_multi_point=True,
        )
    )

    report.render(format="rich_table")


def example_30_save_profection_report():
    """
    Example 30: Save Profection Report to File

    Save the formatted report to a text file.
    """
    section_header("Example 30: Save Report to File")

    from stellium import ReportBuilder

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    output_file = OUTPUT_DIR / "einstein_profection_report.txt"

    # Create comprehensive profection report
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_profections(
            age=26,
            include_timeline=True,
            timeline_range=(20, 35),
        )
    )

    # Save to file (plain text format)
    report.render(format="plain_table", file=str(output_file), show=False)

    print(f"Created: {output_file}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all profection examples."""
    print("\n" + "=" * 60)
    print("  STELLIUM PROFECTIONS COOKBOOK")
    print("  Hellenistic Annual Timing Technique")
    print("=" * 60)

    # Part 1: Basic Annual Profections
    example_1_simple_annual_profection()
    example_2_profection_cycle()
    example_3_lord_of_year()
    example_4_chart_convenience_methods()

    # Part 2: Profection Details
    example_5_planets_in_profected_house()
    example_6_ruler_details()

    # Part 3: Traditional vs Modern
    example_7_traditional_vs_modern()

    # Part 4: Monthly Profections
    example_8_monthly_profections()
    example_9_solar_ingress_monthly()
    example_10_chart_for_date()

    # Part 5: Multi-Point
    example_11_multi_point()
    example_12_custom_points()
    example_13_chart_multi()

    # Part 6: Timelines
    example_14_timeline()
    example_15_find_lord_years()
    example_16_lords_sequence()
    example_17_chart_timeline()

    # Part 7: House Systems
    example_18_whole_sign_default()
    example_19_explicit_house_system()

    # Part 8: Other Points
    example_20_profecting_sun()
    example_21_profecting_moon()
    example_22_profecting_mc()

    # Part 9: Putting It Together
    example_23_comprehensive_reading()
    example_24_output_file()

    # Part 10: Report Builder Integration
    example_25_basic_profection_report()
    example_26_profection_report_with_timeline()
    example_27_profection_report_by_date()
    example_28_profection_report_custom_points()
    example_29_profection_report_modern_rulers()
    example_30_save_profection_report()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE!")
    print(f"  Output files in: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
