#!/usr/bin/env python3
"""
Primary Directions Cookbook - Classical Predictive Technique

This cookbook demonstrates how to use Stellium's primary directions engine.
Primary directions are the oldest and most powerful predictive technique in
Western astrology, tracking when planets "direct" to sensitive points via
the Earth's daily rotation.

Key concepts:
- Promissor: The moving point (planet)
- Significator: The target point (angle, planet)
- Arc: The angular distance in degrees
- Time Key: Conversion rate from arc to years (Ptolemy: 1°=1yr, Naibod: slower)
- Methods: Zodiacal (2D) vs Mundane/Placidus (3D)

Run this script to see primary directions examples in action.

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/directions_cookbook.py

References:
    - https://morinus-astrology.com/placidus-direction/
    - https://sevenstarsastrology.com/astrological-predictive-techniques-primary-directions-2-software-calculation/
"""

import datetime as dt
import os
from pathlib import Path

from stellium import ChartBuilder
from stellium.engines.directions import (
    DirectionsEngine,
    DistributionsCalculator,
    NaibodKey,
    PtolemyKey,
)

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "directions"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC PRIMARY DIRECTIONS
# =============================================================================


def example_1_simple_direction():
    """
    Example 1: Simple Primary Direction

    Calculate when a planet will "direct" to an angle.
    The result includes the arc (degrees), age, and date.
    """
    section_header("Example 1: Simple Primary Direction")

    # Create a chart (Prince Charles)
    birth = dt.datetime(1948, 11, 14, 21, 14)
    chart = ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

    print("Chart: Prince Charles")
    print(f"Birth: {birth}")
    print("Location: London (51.5°N)")

    # Create the directions engine
    engine = DirectionsEngine(chart)

    # Direct Sun to Ascendant
    result = engine.direct("Sun", "ASC")

    print("\nSun directed to ASC:")
    print(f"  Arc: {result.arc.arc_degrees:.2f}°")
    print(f"  Age: {result.age:.1f} years")
    print(f"  Date: {result.date.strftime('%Y-%m-%d') if result.date else 'N/A'}")
    print(f"  Method: {result.arc.method}")


def example_2_multiple_directions():
    """
    Example 2: Direct Multiple Planets to One Point

    Find all planets directing to the Ascendant, sorted by age.
    """
    section_header("Example 2: Multiple Planets to ASC")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DirectionsEngine(chart)

    print("Einstein - All planets directing to ASC:\n")
    print(f"{'Planet':<12} {'Arc':<12} {'Age':<12}")
    print("-" * 36)

    # Use the convenience method
    results = engine.direct_all_to("ASC")

    for result in results:
        if result.age and 0 < result.age < 100:
            print(
                f"{result.arc.promissor:<12} "
                f"{result.arc.arc_degrees:>8.2f}° "
                f"{result.age:>8.1f} yrs"
            )


def example_3_planet_to_all_angles():
    """
    Example 3: Direct One Planet to All Angles

    See when a planet reaches ASC, MC, DSC, and IC.
    """
    section_header("Example 3: Sun to All Angles")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DirectionsEngine(chart)

    print("Einstein - Sun directing to all angles:\n")

    results = engine.direct_to_angles("Sun")

    for angle, result in results.items():
        if result.age and 0 < result.age < 100:
            print(
                f"  Sun to {angle}: {result.arc.arc_degrees:.2f}° = "
                f"age {result.age:.1f}"
            )


# =============================================================================
# PART 2: DIRECTION METHODS
# =============================================================================


def example_4_zodiacal_method():
    """
    Example 4: Zodiacal Directions (Default)

    Zodiacal directions project planets onto the ecliptic plane.
    This is the "2D" or Regiomontanus-style method.
    """
    section_header("Example 4: Zodiacal Directions")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Zodiacal is the default
    engine = DirectionsEngine(chart, method="zodiacal")

    print(f"Method: {engine._method.method_name}")
    print("This projects promissors onto the ecliptic plane (2D).\n")

    result = engine.direct("Mars", "ASC")
    print(
        f"Mars to ASC (zodiacal): {result.arc.arc_degrees:.2f}° = age {result.age:.1f}"
    )


def example_5_mundane_method():
    """
    Example 5: Mundane (Placidus) Directions

    Mundane directions use house-space proportions.
    This is the "3D" or Placidus method.
    """
    section_header("Example 5: Mundane (Placidus) Directions")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Use mundane method
    engine = DirectionsEngine(chart, method="mundane")

    print(f"Method: {engine._method.method_name}")
    print("This uses semi-arc proportions (3D/Placidus).\n")

    result = engine.direct("Mars", "ASC")
    print(
        f"Mars to ASC (mundane): {result.arc.arc_degrees:.2f}° = age {result.age:.1f}"
    )


def example_6_compare_methods():
    """
    Example 6: Compare Zodiacal vs Mundane

    The two methods can produce different arcs, especially for
    planets with significant declination.
    """
    section_header("Example 6: Zodiacal vs Mundane Comparison")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    zodiacal = DirectionsEngine(chart, method="zodiacal")
    mundane = DirectionsEngine(chart, method="mundane")

    print("Comparing direction methods:\n")
    print(f"{'Direction':<20} {'Zodiacal':<15} {'Mundane':<15} {'Diff':<10}")
    print("-" * 60)

    planets = ["Sun", "Moon", "Mars", "Saturn"]
    for planet in planets:
        z_result = zodiacal.direct(planet, "ASC")
        m_result = mundane.direct(planet, "ASC")

        diff = abs(z_result.arc.arc_degrees - m_result.arc.arc_degrees)

        print(
            f"{planet} to ASC{'':<10} "
            f"{z_result.arc.arc_degrees:>8.2f}° "
            f"{m_result.arc.arc_degrees:>11.2f}° "
            f"{diff:>8.2f}°"
        )


# =============================================================================
# PART 3: TIME KEYS
# =============================================================================


def example_7_ptolemy_key():
    """
    Example 7: Ptolemy Time Key (1° = 1 year)

    The classical key attributed to Ptolemy.
    Simple: 30° arc = 30 years.
    """
    section_header("Example 7: Ptolemy Time Key")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    engine = DirectionsEngine(chart, time_key="ptolemy")

    print(f"Time Key: {engine._time_key.key_name}")
    print("Conversion: 1° = 1 year\n")

    result = engine.direct("Sun", "ASC")
    print(f"Sun to ASC: {result.arc.arc_degrees:.2f}° = {result.age:.2f} years")


def example_8_naibod_key():
    """
    Example 8: Naibod Time Key (~1° = 1.0146 years)

    Based on the Sun's mean daily motion.
    More precise but slower than Ptolemy.
    """
    section_header("Example 8: Naibod Time Key")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    engine = DirectionsEngine(chart, time_key="naibod")

    print(f"Time Key: {engine._time_key.key_name}")
    print("Conversion: 1° = ~1.0146 years (based on solar motion)\n")

    result = engine.direct("Sun", "ASC")
    print(f"Sun to ASC: {result.arc.arc_degrees:.2f}° = {result.age:.2f} years")


def example_9_compare_keys():
    """
    Example 9: Compare Time Keys

    See how the same arc produces different ages.
    """
    section_header("Example 9: Time Key Comparison")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    ptolemy_engine = DirectionsEngine(chart, time_key="ptolemy")
    naibod_engine = DirectionsEngine(chart, time_key="naibod")

    print("Same arc, different time keys:\n")
    print(f"{'Direction':<20} {'Arc':<10} {'Ptolemy':<12} {'Naibod':<12}")
    print("-" * 54)

    planets = ["Sun", "Moon", "Mars", "Jupiter"]
    for planet in planets:
        p_result = ptolemy_engine.direct(planet, "ASC")
        n_result = naibod_engine.direct(planet, "ASC")

        print(
            f"{planet} to ASC{'':<10} "
            f"{p_result.arc.arc_degrees:>6.2f}° "
            f"{p_result.age:>8.1f} yrs "
            f"{n_result.age:>8.1f} yrs"
        )


def example_10_time_key_standalone():
    """
    Example 10: Using Time Keys Directly

    You can use time keys independently for arc-to-time conversion.
    """
    section_header("Example 10: Standalone Time Key Usage")

    ptolemy = PtolemyKey()
    naibod = NaibodKey()

    birth = dt.datetime(1990, 1, 1, 12, 0)
    arc = 30.0  # degrees

    print(f"Converting {arc}° arc from birth {birth.date()}:\n")

    p_years = ptolemy.arc_to_years(arc)
    p_date = ptolemy.arc_to_date(arc, birth)
    print(f"Ptolemy: {p_years:.2f} years → {p_date.date()}")

    n_years = naibod.arc_to_years(arc)
    n_date = naibod.arc_to_date(arc, birth)
    print(f"Naibod:  {n_years:.2f} years → {n_date.date()}")


# =============================================================================
# PART 4: TERM DISTRIBUTIONS
# =============================================================================


def example_11_basic_distributions():
    """
    Example 11: Term Distributions (Life Chapters)

    Distributions track which planetary term the directed Ascendant
    occupies. Each term is ruled by a planet, creating "life chapters".
    """
    section_header("Example 11: Term Distributions")

    birth = dt.datetime(1948, 11, 14, 21, 14)
    chart = ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

    calc = DistributionsCalculator(chart)
    periods = calc.calculate(years=50)

    print("Prince Charles - Life Chapters (Term Distributions):\n")
    print(f"{'Age':<8} {'Date':<14} {'Sign':<12} {'Ruler':<10}")
    print("-" * 46)

    for period in periods:
        print(
            f"{period.start_age:>5.1f}   "
            f"{period.start_date.strftime('%Y-%m-%d')}   "
            f"{period.sign:<12} "
            f"{period.ruler:<10}"
        )


def example_12_distributions_ptolemy():
    """
    Example 12: Distributions with Ptolemy Key

    Use the Ptolemy time key for distributions instead of Naibod.
    """
    section_header("Example 12: Distributions (Ptolemy Key)")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    calc = DistributionsCalculator(chart, time_key="ptolemy")
    periods = calc.calculate(years=40)

    print("Einstein - Life Chapters (Ptolemy Key):\n")

    for period in periods:
        print(f"Age {period.start_age:>5.1f}: " f"{period.sign} term of {period.ruler}")


def example_13_compare_distribution_keys():
    """
    Example 13: Compare Distribution Time Keys

    See how Ptolemy vs Naibod affects distribution timing.
    """
    section_header("Example 13: Distribution Key Comparison")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    ptolemy_calc = DistributionsCalculator(chart, time_key="ptolemy")
    naibod_calc = DistributionsCalculator(chart, time_key="naibod")

    p_periods = ptolemy_calc.calculate(years=30)
    n_periods = naibod_calc.calculate(years=30)

    print("Comparing distribution timing:\n")
    print("Ptolemy Key:")
    for p in p_periods[:5]:
        print(f"  Age {p.start_age:>5.1f}: {p.ruler}")

    print("\nNaibod Key:")
    for n in n_periods[:5]:
        print(f"  Age {n.start_age:>5.1f}: {n.ruler}")


# =============================================================================
# PART 5: REAL WORLD EXAMPLES
# =============================================================================


def example_14_life_events():
    """
    Example 14: Directions and Life Events

    Look for directions that might correlate with significant ages.
    """
    section_header("Example 14: Significant Life Directions")

    # Einstein published special relativity at age 26
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DirectionsEngine(chart)

    print("Einstein - Directions perfecting around age 26:\n")

    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    angles = ["ASC", "MC"]

    relevant = []
    for planet in planets:
        for angle in angles:
            result = engine.direct(planet, angle)
            if result.age and 20 < result.age < 35:
                relevant.append(result)

    relevant.sort(key=lambda r: r.age or 0)

    for r in relevant:
        print(
            f"  {r.arc.promissor} to {r.arc.significator}: "
            f"age {r.age:.1f} ({r.arc.arc_degrees:.2f}°)"
        )


def example_15_future_directions():
    """
    Example 15: Future Directions

    Calculate upcoming directions for planning.
    """
    section_header("Example 15: Future Directions")

    # Use a more recent birth
    birth = dt.datetime(1990, 6, 15, 14, 30)
    chart = ChartBuilder.from_details(birth, (40.7128, -74.0060)).calculate()

    engine = DirectionsEngine(chart)

    print(f"Birth: {birth.date()}")
    print(f"Current age: ~{(dt.datetime.now() - birth).days / 365.25:.0f}\n")

    print("Upcoming directions (next 10 years):\n")

    current_age = (dt.datetime.now() - birth).days / 365.25
    max_age = current_age + 10

    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    upcoming = []

    for planet in planets:
        result = engine.direct(planet, "ASC")
        if result.age and current_age < result.age < max_age:
            upcoming.append(result)

        result = engine.direct(planet, "MC")
        if result.age and current_age < result.age < max_age:
            upcoming.append(result)

    upcoming.sort(key=lambda r: r.age or 0)

    for r in upcoming[:10]:
        print(
            f"  {r.arc.promissor} to {r.arc.significator}: "
            f"age {r.age:.1f} ({r.date.strftime('%Y-%m') if r.date else 'N/A'})"
        )


# =============================================================================
# PART 6: ADVANCED USAGE
# =============================================================================


def example_16_custom_significator():
    """
    Example 16: Direct to Any Point

    You can direct to any chart object, not just angles.
    """
    section_header("Example 16: Custom Significators")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DirectionsEngine(chart)

    print("Directing planets to Venus:\n")

    for planet in ["Sun", "Moon", "Mars", "Jupiter"]:
        if planet != "Venus":
            result = engine.direct(planet, "Venus")
            if result.age and 0 < result.age < 100:
                print(f"  {planet} to Venus: age {result.age:.1f}")


def example_17_full_analysis():
    """
    Example 17: Full Direction Analysis

    Comprehensive direction analysis for a chart.
    """
    section_header("Example 17: Full Direction Analysis")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    print("EINSTEIN - COMPREHENSIVE PRIMARY DIRECTIONS ANALYSIS")
    print("=" * 55)

    # Part 1: Zodiacal Directions to ASC
    print("\n1. Zodiacal Directions to ASC (sorted by age):")
    z_engine = DirectionsEngine(chart, method="zodiacal")
    results = z_engine.direct_all_to("ASC")
    for r in results[:5]:
        print(f"   {r.arc.promissor}: age {r.age:.1f}")

    # Part 2: Mundane Directions to ASC
    print("\n2. Mundane Directions to ASC:")
    m_engine = DirectionsEngine(chart, method="mundane")
    results = m_engine.direct_all_to("ASC")
    for r in results[:5]:
        print(f"   {r.arc.promissor}: age {r.age:.1f}")

    # Part 3: Life Chapters
    print("\n3. Life Chapters (first 5):")
    calc = DistributionsCalculator(chart)
    periods = calc.calculate(years=40)
    for p in periods[:5]:
        print(f"   Age {p.start_age:>5.1f}: {p.sign} - {p.ruler}")


def example_18_save_analysis():
    """
    Example 18: Save Analysis to File

    Export a complete directions analysis.
    """
    section_header("Example 18: Export Analysis")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    output_file = OUTPUT_DIR / "einstein_directions.txt"

    with open(output_file, "w") as f:
        f.write("ALBERT EINSTEIN - PRIMARY DIRECTIONS ANALYSIS\n")
        f.write("=" * 50 + "\n\n")

        # Directions
        f.write("DIRECTIONS TO ASCENDANT (Zodiacal, Naibod)\n")
        f.write("-" * 50 + "\n")

        engine = DirectionsEngine(chart)
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
            result = engine.direct(planet, "ASC")
            f.write(
                f"{planet:<10} {result.arc.arc_degrees:>8.2f}° "
                f"{result.age:>8.1f} years\n"
            )

        # Distributions
        f.write("\n\nLIFE CHAPTERS (Term Distributions)\n")
        f.write("-" * 50 + "\n")

        calc = DistributionsCalculator(chart)
        periods = calc.calculate(years=80)
        for p in periods:
            f.write(f"Age {p.start_age:>5.1f}: {p.sign:<12} {p.ruler:<10}\n")

    print(f"Analysis saved to: {output_file}")


# =============================================================================
# PART 7: CONFIGURATION OPTIONS SUMMARY
# =============================================================================


def example_19_all_options():
    """
    Example 19: All Configuration Options

    Summary of all available options for the directions engine.
    """
    section_header("Example 19: Configuration Summary")

    print("DirectionsEngine Options:")
    print("-" * 40)
    print("\nMethods:")
    print("  'zodiacal' - 2D ecliptic projection (default)")
    print("  'mundane'  - 3D Placidus semi-arc proportions")
    print("\nTime Keys:")
    print("  'naibod'   - Solar motion rate, ~1.0146 yrs/deg (default)")
    print("  'ptolemy'  - Classical rate, 1 yr/deg")

    print("\n\nDistributionsCalculator Options:")
    print("-" * 40)
    print("\nTime Keys:")
    print("  'naibod'   - (default)")
    print("  'ptolemy'")
    print("\nBound Systems:")
    print("  'egypt'    - Egyptian bounds (default)")

    print("\n\nExample Configurations:")
    print("-" * 40)
    print("\n# Default (zodiacal + naibod):")
    print("engine = DirectionsEngine(chart)")
    print("\n# Mundane directions:")
    print("engine = DirectionsEngine(chart, method='mundane')")
    print("\n# Ptolemy time key:")
    print("engine = DirectionsEngine(chart, time_key='ptolemy')")
    print("\n# Both customized:")
    print("engine = DirectionsEngine(chart, method='mundane', time_key='ptolemy')")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all primary directions examples."""
    print("\n" + "=" * 60)
    print("  STELLIUM PRIMARY DIRECTIONS COOKBOOK")
    print("  Classical Predictive Technique")
    print("=" * 60)

    # Part 1: Basic Directions
    example_1_simple_direction()
    example_2_multiple_directions()
    example_3_planet_to_all_angles()

    # Part 2: Direction Methods
    example_4_zodiacal_method()
    example_5_mundane_method()
    example_6_compare_methods()

    # Part 3: Time Keys
    example_7_ptolemy_key()
    example_8_naibod_key()
    example_9_compare_keys()
    example_10_time_key_standalone()

    # Part 4: Distributions
    example_11_basic_distributions()
    example_12_distributions_ptolemy()
    example_13_compare_distribution_keys()

    # Part 5: Real World Examples
    example_14_life_events()
    example_15_future_directions()

    # Part 6: Advanced
    example_16_custom_significator()
    example_17_full_analysis()
    example_18_save_analysis()

    # Part 7: Summary
    example_19_all_options()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE!")
    print(f"  Output files in: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
