#!/usr/bin/env python3
"""
Secondary Progressions Cookbook - Internal Development & Symbolic Timing

This cookbook demonstrates how to calculate and analyze secondary progressions
in Stellium. Progressions use the symbolic equation "1 day = 1 year" to show
internal psychological development and unfolding potential.

The "predictive trinity" in astrology:
- Transits: External events happening TO you
- Returns: Annual/periodic themes
- Progressions: Internal development - you BECOMING who you're meant to be

Key progressed events to watch:
- Progressed Moon changing signs (~2.5 years): emotional tone shifts
- Progressed Sun changing signs (~30 years): identity evolution
- Progressed planets aspecting natal: developmental milestones

Run this script to generate example progressions in examples/progressions/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/progressions_cookbook.py

For full documentation, see docs/CHART_TYPES.md
"""

import os
from datetime import datetime
from pathlib import Path

from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder
from stellium.core.models import ComparisonType

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "progressions"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC PROGRESSIONS BY AGE
# =============================================================================


def example_1_simple_progression_by_age():
    """
    Example 1: Simple Progression by Age

    The easiest way to get progressions - just specify the age!
    """
    section_header("Example 1: Simple Progression by Age")

    # Create natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print(f"Natal Sun: {natal.get_object('Sun').longitude:.2f}° {natal.get_object('Sun').sign}")
    print(f"Natal Moon: {natal.get_object('Moon').longitude:.2f}° {natal.get_object('Moon').sign}")
    print(f"Natal ASC: {natal.get_object('ASC').longitude:.2f}° {natal.get_object('ASC').sign}")

    # Calculate progressions for age 26 (when Einstein published special relativity!)
    prog = ComparisonBuilder.progression(natal, age=26).calculate()

    print(f"\nProgressions at Age 26 (1905 - 'Miracle Year'):")
    print(f"  Progressed Sun: {prog.chart2.get_object('Sun').longitude:.2f}° {prog.chart2.get_object('Sun').sign}")
    print(f"  Progressed Moon: {prog.chart2.get_object('Moon').longitude:.2f}° {prog.chart2.get_object('Moon').sign}")
    print(f"  Progressed ASC: {prog.chart2.get_object('ASC').longitude:.2f}° {prog.chart2.get_object('ASC').sign}")

    # Show cross-aspects between progressed and natal
    print(f"\nProgressed-to-Natal Aspects: {len(prog.cross_aspects)}")
    for asp in sorted(prog.cross_aspects, key=lambda a: a.orb)[:5]:
        print(f"  P.{asp.object2.name} {asp.aspect_name} N.{asp.object1.name} (orb: {asp.orb:.2f}°)")


def example_2_progressed_sun_motion():
    """
    Example 2: Track Progressed Sun Motion Over Time

    The progressed Sun moves ~1° per year. Watch it change signs!
    """
    section_header("Example 2: Progressed Sun Motion (~1°/year)")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),  # Palo Alto coordinates
        name="Kate"
    ).with_aspects().calculate()

    print(f"Natal Sun: {natal.get_object('Sun').longitude:.2f}° {natal.get_object('Sun').sign}")

    # Track Sun motion at different ages
    ages = [0, 10, 20, 30, 40]

    print("\nProgressed Sun at different ages:")
    print("-" * 50)

    prev_sun = natal.get_object('Sun').longitude
    for age in ages:
        if age == 0:
            sun = natal.get_object('Sun')
            motion = 0
        else:
            prog = ComparisonBuilder.progression(natal, age=age).calculate()
            sun = prog.chart2.get_object('Sun')
            motion = sun.longitude - prev_sun
            if motion < 0:
                motion += 360

        print(f"  Age {age:2d}: {sun.longitude:6.2f}° {sun.sign:12s} (moved {motion:.1f}° from prev)")
        prev_sun = sun.longitude


def example_3_progressed_moon_cycle():
    """
    Example 3: The Progressed Moon Cycle (~27 year cycle)

    The progressed Moon moves ~12-13° per year, completing the zodiac
    in about 27-28 years. Each sign change marks an emotional shift.
    """
    section_header("Example 3: Progressed Moon Cycle (~12°/year)")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    print(f"Natal Moon: {natal.get_object('Moon').longitude:.2f}° {natal.get_object('Moon').sign}")

    # Track Moon through approximate sign changes (~2.5 years per sign)
    print("\nProgressed Moon sign changes (approximate):")
    print("-" * 50)

    current_sign = natal.get_object('Moon').sign

    for age in range(0, 31, 3):
        if age == 0:
            moon = natal.get_object('Moon')
        else:
            prog = ComparisonBuilder.progression(natal, age=age).calculate()
            moon = prog.chart2.get_object('Moon')

        sign_change = "← SIGN CHANGE" if moon.sign != current_sign else ""
        print(f"  Age {age:2d}: {moon.longitude:6.2f}° {moon.sign:12s} {sign_change}")
        current_sign = moon.sign


# =============================================================================
# PART 2: PROGRESSIONS BY TARGET DATE
# =============================================================================


def example_4_progression_by_target_date():
    """
    Example 4: Progression to a Specific Target Date

    Calculate progressions for a specific date instead of age.
    Useful for analyzing specific life events.
    """
    section_header("Example 4: Progression by Target Date")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Progressions for when Einstein received the Nobel Prize (1921)
    prog = ComparisonBuilder.progression(
        natal,
        target_date="1921-11-09"  # Nobel Prize announcement
    ).calculate()

    print("Progressions for November 9, 1921 (Nobel Prize)")
    print(f"  Progressed Sun: {prog.chart2.get_object('Sun').longitude:.2f}°")
    print(f"  Progressed Moon: {prog.chart2.get_object('Moon').longitude:.2f}°")
    print(f"  Progressed Mercury: {prog.chart2.get_object('Mercury').longitude:.2f}°")

    # Calculate how old he was
    birth_year = 1879
    event_year = 1921
    print(f"\n  (Einstein was {event_year - birth_year} years old)")


def example_5_current_progressions():
    """
    Example 5: Current Progressions (No Date = Now)

    If you don't specify age or target_date, progressions
    default to the current moment.
    """
    section_header("Example 5: Current Progressions")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    # Progressions for NOW
    prog = ComparisonBuilder.progression(natal).calculate()

    # Calculate current age
    birth_dt = natal.datetime.local_datetime
    now = datetime.now()
    current_age = (now - birth_dt).days / 365.25

    print(f"Current progressions (age ~{current_age:.1f}):")
    print(f"  Progressed Sun: {prog.chart2.get_object('Sun').longitude:.2f}° {prog.chart2.get_object('Sun').sign}")
    print(f"  Progressed Moon: {prog.chart2.get_object('Moon').longitude:.2f}° {prog.chart2.get_object('Moon').sign}")
    print(f"  Progressed Venus: {prog.chart2.get_object('Venus').longitude:.2f}° {prog.chart2.get_object('Venus').sign}")


# =============================================================================
# PART 3: ANGLE PROGRESSION METHODS
# =============================================================================


def example_6_quotidian_angles():
    """
    Example 6: Quotidian Angle Progression (Default)

    Quotidian uses the actual daily motion from Swiss Ephemeris.
    The angles (ASC, MC) move at their natural rate based on
    the progressed chart's actual sky positions.
    """
    section_header("Example 6: Quotidian Angles (Default)")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    # Quotidian is the default (most accurate method)
    prog = ComparisonBuilder.progression(
        natal,
        age=30,
        angle_method="quotidian"  # This is the default
    ).calculate()

    print("Quotidian Angles (actual ephemeris motion):")
    print(f"  Natal ASC: {natal.get_object('ASC').longitude:.2f}° {natal.get_object('ASC').sign}")
    print(f"  Progressed ASC: {prog.chart2.get_object('ASC').longitude:.2f}° {prog.chart2.get_object('ASC').sign}")
    print(f"  Natal MC: {natal.get_object('MC').longitude:.2f}° {natal.get_object('MC').sign}")
    print(f"  Progressed MC: {prog.chart2.get_object('MC').longitude:.2f}° {prog.chart2.get_object('MC').sign}")


def example_7_solar_arc_angles():
    """
    Example 7: Solar Arc Angle Progression

    In Solar Arc, ALL angles progress at the same rate as the
    progressed Sun. If the Sun moved 30°, so do ASC and MC.

    This method is popular because it's predictable and symbolic.
    """
    section_header("Example 7: Solar Arc Angles")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    prog = ComparisonBuilder.progression(
        natal,
        age=30,
        angle_method="solar_arc"
    ).calculate()

    # Calculate the solar arc
    natal_sun = natal.get_object('Sun').longitude
    prog_sun = prog.chart2.get_object('Sun').longitude
    solar_arc = prog_sun - natal_sun
    if solar_arc < 0:
        solar_arc += 360

    print(f"Solar Arc Method:")
    print(f"  Solar Arc: {solar_arc:.2f}° (Sun's motion in 30 years)")
    print(f"\n  Natal ASC: {natal.get_object('ASC').longitude:.2f}°")
    print(f"  Progressed ASC: {prog.chart2.get_object('ASC').longitude:.2f}° (natal + {solar_arc:.2f}°)")
    print(f"\n  Natal MC: {natal.get_object('MC').longitude:.2f}°")
    print(f"  Progressed MC: {prog.chart2.get_object('MC').longitude:.2f}° (natal + {solar_arc:.2f}°)")

    # Verify the metadata
    print(f"\n  Metadata: angle_method = {prog.chart2.metadata.get('angle_method')}")
    print(f"  Metadata: angle_arc = {prog.chart2.metadata.get('angle_arc', 0):.2f}°")


def example_8_naibod_angles():
    """
    Example 8: Naibod Angle Progression

    Naibod uses the Sun's MEAN daily motion (59'08" per year)
    rather than its actual motion. This gives a consistent,
    predictable rate regardless of where the Sun is in its orbit.

    Naibod rate: ~0.9856° per year
    """
    section_header("Example 8: Naibod Angles")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    prog = ComparisonBuilder.progression(
        natal,
        age=30,
        angle_method="naibod"
    ).calculate()

    # Calculate expected Naibod arc
    naibod_rate = 59.1333 / 60  # degrees per year
    expected_arc = 30 * naibod_rate

    print(f"Naibod Method (mean Sun rate: 59'08\"/year):")
    print(f"  Expected arc for 30 years: {expected_arc:.2f}°")
    print(f"\n  Natal ASC: {natal.get_object('ASC').longitude:.2f}°")
    print(f"  Progressed ASC: {prog.chart2.get_object('ASC').longitude:.2f}° (natal + {expected_arc:.2f}°)")

    # Verify the metadata
    actual_arc = prog.chart2.metadata.get('angle_arc', 0)
    print(f"\n  Metadata: angle_arc = {actual_arc:.2f}°")


def example_9_compare_angle_methods():
    """
    Example 9: Compare All Three Angle Methods

    See how the different methods produce different angle positions.
    """
    section_header("Example 9: Compare Angle Methods")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    natal_asc = natal.get_object('ASC').longitude

    print(f"Natal ASC: {natal_asc:.2f}°\n")
    print(f"{'Method':<12} {'Progressed ASC':>15} {'Difference':>12}")
    print("-" * 42)

    for method in ["quotidian", "solar_arc", "naibod"]:
        prog = ComparisonBuilder.progression(
            natal,
            age=30,
            angle_method=method
        ).calculate()

        prog_asc = prog.chart2.get_object('ASC').longitude
        diff = prog_asc - natal_asc
        if diff < 0:
            diff += 360

        print(f"{method:<12} {prog_asc:>15.2f}° {diff:>11.2f}°")


# =============================================================================
# PART 4: ANALYZING PROGRESSIONS
# =============================================================================


def example_10_progressed_aspects_to_natal():
    """
    Example 10: Find Progressed Aspects to Natal

    The most common use of progressions - finding when progressed
    planets aspect natal positions.
    """
    section_header("Example 10: Progressed-to-Natal Aspects")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    prog = ComparisonBuilder.progression(natal, age=26).calculate()

    print("Progressed-to-Natal Aspects at Age 26:")
    print("-" * 50)

    if prog.cross_aspects:
        for asp in sorted(prog.cross_aspects, key=lambda a: a.orb):
            # In progressions, object2 is progressed, object1 is natal
            print(
                f"  P.{asp.object2.name:<8} {asp.aspect_name:<12} "
                f"N.{asp.object1.name:<8} (orb: {asp.orb:.3f}°)"
            )
    else:
        print("  No aspects within 1° orb (progressions use tight orbs!)")


def example_11_house_overlays():
    """
    Example 11: Progressed Planets in Natal Houses

    See which natal houses your progressed planets fall in.
    """
    section_header("Example 11: Progressed Planets in Natal Houses")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    prog = ComparisonBuilder.progression(natal, age=30).calculate()

    print("Progressed Planets in Natal Houses:")
    print("-" * 50)

    # House overlays show where each chart's planets fall in the other's houses
    # Filter for progressed planets in natal houses (planet_owner="chart2")
    prog_in_natal = [h for h in prog.house_overlays if h.planet_owner == "chart2"]

    for overlay in prog_in_natal[:10]:  # Show first 10
        print(f"  P.{overlay.planet_name:<8} in Natal House {overlay.falls_in_house}")


# =============================================================================
# PART 5: BACKWARDS COMPATIBILITY
# =============================================================================


def example_12_legacy_explicit_chart():
    """
    Example 12: Legacy API with Explicit Progressed Chart

    The old way still works - pass a pre-calculated progressed chart.
    """
    section_header("Example 12: Legacy API (Explicit Chart)")

    from datetime import timedelta

    # Create natal chart
    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    # Manually calculate progressed datetime (30 days = 30 years)
    natal_dt = natal.datetime.local_datetime
    progressed_dt = natal_dt + timedelta(days=30)

    # Manually create progressed chart
    progressed = ChartBuilder.from_details(
        progressed_dt,
        natal.location,
        name="Kate - Progressed (manual)"
    ).calculate()

    # Legacy API: pass both charts explicitly
    prog = ComparisonBuilder.progression(natal, progressed).calculate()

    print("Legacy API works!")
    print(f"  Comparison type: {prog.comparison_type}")
    print(f"  Cross aspects: {len(prog.cross_aspects)}")


def example_13_tuple_format():
    """
    Example 13: Using Tuple Format (datetime, location)

    Both natal and progressed can be specified as tuples.
    """
    section_header("Example 13: Tuple Format")

    # Both charts as tuples
    prog = ComparisonBuilder.progression(
        ("1994-01-06 11:47", "Palo Alto, CA"),
        ("1994-02-05 11:47", "Palo Alto, CA"),  # 30 days later = age 30
    ).calculate()

    print("Tuple format works!")
    print(f"  Comparison type: {prog.comparison_type}")
    print(f"  Days between: {prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day:.1f}")


# =============================================================================
# PART 6: VISUALIZATION
# =============================================================================


def example_14_draw_progression_biwheel():
    """
    Example 14: Draw Progression Bi-Wheel

    Create a bi-wheel chart with natal (inner) and progressed (outer).
    """
    section_header("Example 14: Progression Bi-Wheel Chart")

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Kate"
    ).with_aspects().calculate()

    prog = ComparisonBuilder.progression(
        natal,
        age=30,
        natal_label="Natal",
        progressed_label="Progressed Age 30"
    ).calculate()

    # Draw the bi-wheel
    output = OUTPUT_DIR / "14_progression_biwheel.svg"
    prog.draw(str(output)).save()

    print(f"Created progression bi-wheel: {output}")
    print(f"  Inner ring: Natal chart")
    print(f"  Outer ring: Progressed (age 30)")


def example_15_progression_with_solar_arc_biwheel():
    """
    Example 15: Solar Arc Progression Bi-Wheel

    Draw a bi-wheel using solar arc angles.
    """
    section_header("Example 15: Solar Arc Progression Bi-Wheel")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    prog = ComparisonBuilder.progression(
        natal,
        age=26,
        angle_method="solar_arc",
        natal_label="Einstein Natal",
        progressed_label="Progressed 1905"
    ).calculate()

    output = OUTPUT_DIR / "15_einstein_1905_solar_arc.svg"
    prog.draw(str(output)).save()

    print(f"Created: {output}")
    print(f"  Solar arc used for angle progression")


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================


def main():
    """Run all progression cookbook examples."""
    print("\n" + "=" * 60)
    print("  SECONDARY PROGRESSIONS COOKBOOK")
    print("  Stellium - Computational Astrology Library")
    print("=" * 60)

    # Part 1: Basic Progressions by Age
    example_1_simple_progression_by_age()
    example_2_progressed_sun_motion()
    example_3_progressed_moon_cycle()

    # Part 2: Progressions by Target Date
    example_4_progression_by_target_date()
    example_5_current_progressions()

    # Part 3: Angle Progression Methods
    example_6_quotidian_angles()
    example_7_solar_arc_angles()
    example_8_naibod_angles()
    example_9_compare_angle_methods()

    # Part 4: Analyzing Progressions
    example_10_progressed_aspects_to_natal()
    example_11_house_overlays()

    # Part 5: Backwards Compatibility
    example_12_legacy_explicit_chart()
    example_13_tuple_format()

    # Part 6: Visualization
    example_14_draw_progression_biwheel()
    example_15_progression_with_solar_arc_biwheel()

    print("\n" + "=" * 60)
    print("  All examples complete!")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
