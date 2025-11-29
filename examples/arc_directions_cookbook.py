#!/usr/bin/env python3
"""
Arc Directions Cookbook - Primary Directions & Symbolic Timing

This cookbook demonstrates how to calculate and analyze arc directions
in Stellium. Arc directions move ALL chart points by the same angular
distance, preserving natal relationships.

Key difference from progressions:
- Progressions: Each planet moves at its own rate (1 day = 1 year)
- Arc Directions: ALL points move by the SAME arc (unified motion)

Arc types available:
- Solar Arc: Arc = progressed Sun - natal Sun (~1°/year, most popular)
- Naibod: Arc = 0.9856° × years (mean solar motion, consistent)
- Lunar Arc: Arc = progressed Moon - natal Moon (~12-13°/year)
- Chart Ruler: Arc based on ruler of Ascendant sign (personalized)
- Sect: Day charts use solar arc, night charts use lunar arc
- Any Planet: Mars arc, Venus arc, Jupiter arc, Saturn arc, etc.

Run this script to generate example arc direction charts in examples/arc_directions/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/arc_directions_cookbook.py

For full documentation, see docs/CHART_TYPES.md
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ComparisonBuilder

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "arc_directions"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: SOLAR ARC DIRECTIONS (Most Popular)
# =============================================================================


def example_1_solar_arc_by_age():
    """
    Example 1: Solar Arc Directions by Age

    Solar arc is the most widely used arc direction method.
    The arc equals the distance the progressed Sun has moved from natal.
    Approximately 1 degree per year of life.
    """
    section_header("Example 1: Solar Arc Directions by Age")

    # Create natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print(f"Natal Sun: {natal.get_object('Sun').longitude:.2f}° {natal.get_object('Sun').sign}")
    print(f"Natal Moon: {natal.get_object('Moon').longitude:.2f}° {natal.get_object('Moon').sign}")
    print(f"Natal MC: {natal.get_object('MC').longitude:.2f}° {natal.get_object('MC').sign}")

    # Calculate solar arc directions for age 26 (1905 - Einstein's "Miracle Year")
    directed = ComparisonBuilder.arc_direction(
        natal, age=26, arc_type="solar_arc"
    ).calculate()

    # Access the arc value from metadata
    arc = directed.chart2.metadata.get("arc_degrees", 0)
    print(f"\nSolar Arc at Age 26: {arc:.2f}°")

    print("\nDirected Positions (all moved by same arc):")
    print(f"  Directed Sun: {directed.chart2.get_object('Sun').longitude:.2f}° {directed.chart2.get_object('Sun').sign}")
    print(f"  Directed Moon: {directed.chart2.get_object('Moon').longitude:.2f}° {directed.chart2.get_object('Moon').sign}")
    print(f"  Directed MC: {directed.chart2.get_object('MC').longitude:.2f}° {directed.chart2.get_object('MC').sign}")

    # Show cross-aspects between directed and natal
    print(f"\nDirected-to-Natal Aspects: {len(directed.cross_aspects)}")
    for asp in sorted(directed.cross_aspects, key=lambda a: a.orb)[:5]:
        print(f"  D.{asp.object2.name} {asp.aspect_name} N.{asp.object1.name} (orb: {asp.orb:.2f}°)")

    # Save chart
    output_file = OUTPUT_DIR / "01_solar_arc_age26.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


def example_2_solar_arc_by_date():
    """
    Example 2: Solar Arc Directions to a Specific Date

    Calculate directions for a specific target date rather than age.
    Useful for analyzing life events.
    """
    section_header("Example 2: Solar Arc Directions to a Specific Date")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()

    print(f"Natal chart for: Steve Jobs")
    print(f"Natal Sun: {natal.get_object('Sun').longitude:.2f}° {natal.get_object('Sun').sign}")

    # Calculate directions to a specific date
    directed = ComparisonBuilder.arc_direction(
        natal, target_date="2025-06-15", arc_type="solar_arc"
    ).calculate()

    arc = directed.chart2.metadata.get("arc_degrees", 0)
    years = directed.chart2.metadata.get("years_elapsed", 0)

    print(f"\nDirections to June 15, 2025:")
    print(f"  Years elapsed: {years:.2f}")
    print(f"  Solar arc: {arc:.2f}°")

    print("\nDirected Positions:")
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
        pos = directed.chart2.get_object(planet)
        if pos:
            print(f"  Directed {planet}: {pos.longitude:.2f}° {pos.sign}")

    # Save chart
    output_file = OUTPUT_DIR / "02_solar_arc_date.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


# =============================================================================
# PART 2: NAIBOD ARC DIRECTIONS
# =============================================================================


def example_3_naibod_arc():
    """
    Example 3: Naibod Arc Directions

    Naibod uses the mean solar motion (59'08" per year = 0.9856°/year).
    Unlike solar arc which uses actual Sun motion, Naibod is mathematically
    consistent and predictable.
    """
    section_header("Example 3: Naibod Arc Directions")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Compare solar arc vs naibod at the same age
    age = 30

    solar = ComparisonBuilder.arc_direction(natal, age=age, arc_type="solar_arc").calculate()
    naibod = ComparisonBuilder.arc_direction(natal, age=age, arc_type="naibod").calculate()

    solar_arc = solar.chart2.metadata.get("arc_degrees", 0)
    naibod_arc = naibod.chart2.metadata.get("arc_degrees", 0)

    print(f"Comparing arcs at age {age}:")
    print(f"  Solar Arc: {solar_arc:.4f}° (actual Sun motion)")
    print(f"  Naibod Arc: {naibod_arc:.4f}° (mean Sun: 0.9856°/year × {age})")
    print(f"  Difference: {abs(solar_arc - naibod_arc):.4f}°")

    print("\nNaibod is useful when:")
    print("  - You want consistent, predictable timing")
    print("  - Calculating far into the future")
    print("  - Using traditional primary directions")

    # Save naibod chart
    output_file = OUTPUT_DIR / "03_naibod_arc.svg"
    naibod.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


# =============================================================================
# PART 3: LUNAR ARC DIRECTIONS
# =============================================================================


def example_4_lunar_arc():
    """
    Example 4: Lunar Arc Directions

    Lunar arc uses the Moon's progressed motion (~12-13°/year).
    Much faster than solar arc, so events unfold more quickly.
    Useful for emotional/domestic timing and short-term forecasting.
    """
    section_header("Example 4: Lunar Arc Directions")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()

    # Lunar arc at age 5 (comparable distance to solar arc at age ~60!)
    directed = ComparisonBuilder.arc_direction(
        natal, age=5, arc_type="lunar"
    ).calculate()

    arc = directed.chart2.metadata.get("arc_degrees", 0)

    print(f"Lunar Arc at Age 5: {arc:.2f}°")
    print("(The Moon moves ~12-13° per year in progressions)")

    # Compare to solar arc at same age
    solar = ComparisonBuilder.arc_direction(natal, age=5, arc_type="solar_arc").calculate()
    solar_arc = solar.chart2.metadata.get("arc_degrees", 0)

    print(f"\nComparison at age 5:")
    print(f"  Lunar arc: {arc:.2f}°")
    print(f"  Solar arc: {solar_arc:.2f}°")
    print(f"  Lunar is {arc/solar_arc:.1f}x faster!")

    print("\nLunar arc is useful for:")
    print("  - Emotional/domestic events")
    print("  - Short-term timing (monthly/yearly)")
    print("  - Night chart natives (Moon is sect light)")

    # Save lunar arc chart
    output_file = OUTPUT_DIR / "04_lunar_arc.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


# =============================================================================
# PART 4: SECT-BASED ARC DIRECTIONS
# =============================================================================


def example_5_sect_arc():
    """
    Example 5: Sect-Based Arc Directions

    Sect arc automatically chooses:
    - Solar arc for day charts (Sun above horizon)
    - Lunar arc for night charts (Sun below horizon)

    This honors the traditional concept of sect - the "team" your chart belongs to.
    """
    section_header("Example 5: Sect-Based Arc Directions")

    # Einstein was born during the day (11:30 AM)
    einstein = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Check if day or night chart
    sun = einstein.get_object("Sun")
    asc = einstein.get_object("ASC")
    print(f"Einstein's Chart:")
    print(f"  Sun: {sun.longitude:.2f}° {sun.sign}")
    print(f"  ASC: {asc.longitude:.2f}° {asc.sign}")

    # Calculate sect-based arc
    directed = ComparisonBuilder.arc_direction(
        einstein, age=26, arc_type="sect"
    ).calculate()

    effective_type = directed.chart2.metadata.get("effective_arc_type", "unknown")
    arc = directed.chart2.metadata.get("arc_degrees", 0)

    print(f"\nSect Arc at Age 26:")
    print(f"  Effective type: {effective_type}")
    print(f"  Arc: {arc:.2f}°")

    if effective_type == "solar_arc":
        print("  → Day chart detected, using Solar Arc")
    else:
        print("  → Night chart detected, using Lunar Arc")

    # Save chart
    output_file = OUTPUT_DIR / "05_sect_arc.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


# =============================================================================
# PART 5: CHART RULER ARC DIRECTIONS
# =============================================================================


def example_6_chart_ruler_arc_traditional():
    """
    Example 6: Chart Ruler Arc (Traditional Rulerships)

    Chart ruler arc uses the planet ruling the Ascendant sign.
    This personalizes the arc to the native's chart.

    Traditional rulerships:
    - Aries/Scorpio: Mars
    - Taurus/Libra: Venus
    - Gemini/Virgo: Mercury
    - Cancer: Moon
    - Leo: Sun
    - Sagittarius/Pisces: Jupiter
    - Capricorn/Aquarius: Saturn
    """
    section_header("Example 6: Chart Ruler Arc (Traditional)")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()

    asc = natal.get_object("ASC")
    print(f"Ascendant: {asc.longitude:.2f}° {asc.sign}")

    # Calculate chart ruler arc with traditional rulerships
    directed = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="chart_ruler", rulership_system="traditional"
    ).calculate()

    effective_type = directed.chart2.metadata.get("effective_arc_type", "unknown")
    arc = directed.chart2.metadata.get("arc_degrees", 0)

    print(f"\nChart Ruler Arc (Traditional) at Age 30:")
    print(f"  Chart ruler: {effective_type.title()}")
    print(f"  Arc: {arc:.2f}°")

    # Compare to solar arc
    solar = ComparisonBuilder.arc_direction(natal, age=30, arc_type="solar_arc").calculate()
    solar_arc = solar.chart2.metadata.get("arc_degrees", 0)

    print(f"\nComparison:")
    print(f"  Chart ruler arc: {arc:.2f}°")
    print(f"  Solar arc: {solar_arc:.2f}°")

    # Save chart
    output_file = OUTPUT_DIR / "06_chart_ruler_traditional.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


def example_7_chart_ruler_arc_modern():
    """
    Example 7: Chart Ruler Arc (Modern Rulerships)

    Modern rulerships include outer planets:
    - Scorpio: Pluto (not Mars)
    - Aquarius: Uranus (not Saturn)
    - Pisces: Neptune (not Jupiter)
    """
    section_header("Example 7: Chart Ruler Arc (Modern)")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    asc = natal.get_object("ASC")
    print(f"Einstein's Ascendant: {asc.longitude:.2f}° {asc.sign}")

    # Compare traditional vs modern chart ruler
    trad = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="chart_ruler", rulership_system="traditional"
    ).calculate()

    modern = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="chart_ruler", rulership_system="modern"
    ).calculate()

    trad_ruler = trad.chart2.metadata.get("effective_arc_type", "unknown")
    modern_ruler = modern.chart2.metadata.get("effective_arc_type", "unknown")
    trad_arc = trad.chart2.metadata.get("arc_degrees", 0)
    modern_arc = modern.chart2.metadata.get("arc_degrees", 0)

    print(f"\nChart Ruler at Age 30:")
    print(f"  Traditional: {trad_ruler.title()} → arc: {trad_arc:.2f}°")
    print(f"  Modern: {modern_ruler.title()} → arc: {modern_arc:.2f}°")

    if trad_ruler != modern_ruler:
        print(f"\n  Note: Different rulers give different arcs!")

    # Save chart
    output_file = OUTPUT_DIR / "07_chart_ruler_modern.svg"
    modern.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


# =============================================================================
# PART 6: PLANETARY ARC DIRECTIONS
# =============================================================================


def example_8_mars_arc():
    """
    Example 8: Mars Arc Directions

    You can use any planet's motion as the arc.
    Mars arc is useful for timing action, conflict, and energy.
    """
    section_header("Example 8: Mars Arc Directions")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Calculate Mars arc
    directed = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="Mars"
    ).calculate()

    arc = directed.chart2.metadata.get("arc_degrees", 0)

    print(f"Mars Arc at Age 30: {arc:.2f}°")

    # Compare different planetary arcs at same age
    print("\nAll Planetary Arcs at Age 30:")
    for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        try:
            d = ComparisonBuilder.arc_direction(natal, age=30, arc_type=planet).calculate()
            p_arc = d.chart2.metadata.get("arc_degrees", 0)
            print(f"  {planet:10} arc: {p_arc:7.2f}°")
        except ValueError:
            pass

    # Save chart
    output_file = OUTPUT_DIR / "08_mars_arc.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


def example_9_venus_arc():
    """
    Example 9: Venus Arc Directions

    Venus arc is useful for timing relationships, art, and values.
    """
    section_header("Example 9: Venus Arc Directions")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()

    # Calculate Venus arc
    directed = ComparisonBuilder.arc_direction(
        natal, age=25, arc_type="Venus"
    ).calculate()

    arc = directed.chart2.metadata.get("arc_degrees", 0)

    print(f"Venus Arc at Age 25: {arc:.2f}°")

    # Show directed Venus aspects to natal chart
    venus_aspects = [
        asp for asp in directed.cross_aspects
        if asp.object2.name == "Venus"
    ]

    print(f"\nDirected Venus aspects to natal chart:")
    for asp in sorted(venus_aspects, key=lambda a: a.orb)[:5]:
        print(f"  D.Venus {asp.aspect_name} N.{asp.object1.name} (orb: {asp.orb:.2f}°)")

    # Save chart
    output_file = OUTPUT_DIR / "09_venus_arc.svg"
    directed.draw().with_header().save(str(output_file))
    print(f"\nSaved: {output_file}")


def example_10_jupiter_saturn_arcs():
    """
    Example 10: Jupiter and Saturn Arcs

    Jupiter arc: Expansion, growth, opportunities
    Saturn arc: Structure, lessons, career milestones

    The outer planets move slowly, so their arcs are smaller.
    """
    section_header("Example 10: Jupiter and Saturn Arcs")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    age = 30

    # Calculate both arcs
    jupiter = ComparisonBuilder.arc_direction(natal, age=age, arc_type="Jupiter").calculate()
    saturn = ComparisonBuilder.arc_direction(natal, age=age, arc_type="Saturn").calculate()

    jup_arc = jupiter.chart2.metadata.get("arc_degrees", 0)
    sat_arc = saturn.chart2.metadata.get("arc_degrees", 0)

    # Compare to solar arc
    solar = ComparisonBuilder.arc_direction(natal, age=age, arc_type="solar_arc").calculate()
    solar_arc = solar.chart2.metadata.get("arc_degrees", 0)

    print(f"Arcs at Age {age}:")
    print(f"  Solar arc:   {solar_arc:.2f}°")
    print(f"  Jupiter arc: {jup_arc:.2f}°")
    print(f"  Saturn arc:  {sat_arc:.2f}°")

    print("\nInterpretation:")
    print("  - Slow arcs (Jupiter, Saturn) = subtle, gradual unfoldment")
    print("  - Fast arcs (Moon) = rapid development, short cycles")
    print("  - Solar arc = balanced, standard timing measure")


# =============================================================================
# PART 7: ANALYZING ARC DIRECTION ASPECTS
# =============================================================================


def example_11_finding_exact_aspects():
    """
    Example 11: Finding Exact Directed Aspects

    Key technique: Find when directed planets make exact aspects to natal points.
    These are significant timing markers.
    """
    section_header("Example 11: Finding Exact Directed Aspects")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print("Scanning for tight directed-to-natal aspects (orb < 1°)...")
    print("(Using solar arc directions)")

    tight_aspects = []

    # Scan ages 20-40
    for age in range(20, 41):
        directed = ComparisonBuilder.arc_direction(
            natal, age=age, arc_type="solar_arc"
        ).calculate()

        for asp in directed.cross_aspects:
            if asp.orb < 1.0:
                tight_aspects.append((age, asp))

    # Show results
    print(f"\nFound {len(tight_aspects)} tight aspects:")
    for age, asp in sorted(tight_aspects, key=lambda x: x[1].orb)[:10]:
        print(f"  Age {age}: D.{asp.object2.name} {asp.aspect_name} N.{asp.object1.name} ({asp.orb:.2f}°)")


def example_12_comparing_arc_types():
    """
    Example 12: Comparing Multiple Arc Types

    Side-by-side comparison of different arc methods at the same age.
    """
    section_header("Example 12: Comparing Arc Types")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()
    age = 30

    arc_types = ["solar_arc", "naibod", "lunar", "chart_ruler", "sect"]

    print(f"All Arc Types at Age {age}:")
    print("-" * 50)

    for arc_type in arc_types:
        try:
            directed = ComparisonBuilder.arc_direction(
                natal, age=age, arc_type=arc_type
            ).calculate()

            arc = directed.chart2.metadata.get("arc_degrees", 0)
            effective = directed.chart2.metadata.get("effective_arc_type", arc_type)

            print(f"  {arc_type:15} → {arc:7.2f}° (effective: {effective})")
        except Exception as e:
            print(f"  {arc_type:15} → Error: {e}")


# =============================================================================
# PART 8: VISUALIZATION OPTIONS
# =============================================================================


def example_13_styled_arc_chart():
    """
    Example 13: Styled Arc Direction Chart

    Arc direction charts support all the same styling as other biwheels.
    """
    section_header("Example 13: Styled Arc Direction Chart")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    directed = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="solar_arc"
    ).calculate()

    # Apply styling
    output_file = OUTPUT_DIR / "13_styled_arc.svg"
    (
        directed.draw()
        .with_header()
        .with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .save(str(output_file))
    )

    print(f"Styled arc direction chart saved: {output_file}")


def example_14_arc_with_tables():
    """
    Example 14: Arc Directions with Position Tables

    Show the directed positions alongside the chart.
    """
    section_header("Example 14: Arc Directions with Tables")

    natal = ChartBuilder.from_notable("Steve Jobs").with_aspects().calculate()

    directed = ComparisonBuilder.arc_direction(
        natal, age=30, arc_type="solar_arc"
    ).calculate()

    # Save with tables
    output_file = OUTPUT_DIR / "14_arc_with_tables.svg"
    (
        directed.draw()
        .with_header()
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save(str(output_file))
    )

    print(f"Arc chart with tables saved: {output_file}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all arc direction examples."""
    print("\n" + "=" * 60)
    print("  ARC DIRECTIONS COOKBOOK")
    print("  Demonstrating all arc direction methods in Stellium")
    print("=" * 60)

    # Part 1: Solar Arc
    example_1_solar_arc_by_age()
    example_2_solar_arc_by_date()

    # Part 2: Naibod
    example_3_naibod_arc()

    # Part 3: Lunar Arc
    example_4_lunar_arc()

    # Part 4: Sect-Based
    example_5_sect_arc()

    # Part 5: Chart Ruler
    example_6_chart_ruler_arc_traditional()
    example_7_chart_ruler_arc_modern()

    # Part 6: Planetary Arcs
    example_8_mars_arc()
    example_9_venus_arc()
    example_10_jupiter_saturn_arcs()

    # Part 7: Analysis
    example_11_finding_exact_aspects()
    example_12_comparing_arc_types()

    # Part 8: Visualization
    example_13_styled_arc_chart()
    example_14_arc_with_tables()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
