#!/usr/bin/env python3
"""
Planetary Returns Cookbook - Solar, Lunar & Saturn Returns

This cookbook demonstrates how to calculate and visualize planetary return
charts in Stellium. Returns are charts cast for the exact moment a planet
returns to its natal position.

Common return types:
- Solar Return: When the Sun returns to its natal position (~birthday)
- Lunar Return: When the Moon returns to its natal position (~monthly)
- Saturn Return: When Saturn returns to its natal position (~age 29, 58)

Run this script to generate example returns in examples/returns/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/returns_cookbook.py

For full documentation, see docs/CHART_TYPES.md
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ReportBuilder, ReturnBuilder
from stellium.engines import PlacidusHouses, WholeSignHouses

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "returns"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: SOLAR RETURNS
# =============================================================================


def example_1_simple_solar_return():
    """
    Example 1: Simple Solar Return

    Calculate a Solar Return for a specific year.
    The Sun will be at its exact natal position.
    """
    section_header("Example 1: Simple Solar Return")

    # First, create the natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print(
        f"Natal Sun: {natal.get_object('Sun').longitude:.4f}° {natal.get_object('Sun').sign}"
    )

    # Calculate 1905 Solar Return (Einstein's "Miracle Year"!)
    sr_1905 = ReturnBuilder.solar(natal, 1905).calculate()

    print("\n1905 Solar Return:")
    print(f"  Date: {sr_1905.datetime.utc_datetime}")
    print(f"  Sun: {sr_1905.get_object('Sun').longitude:.4f}°")
    print(f"  Chart type: {sr_1905.metadata.get('chart_type')}")

    # Draw the chart
    output = OUTPUT_DIR / "01_solar_return_einstein_1905.svg"
    sr_1905.draw(str(output)).with_header().save()
    print(f"\nCreated: {output}")


def example_2_multiple_solar_returns():
    """
    Example 2: Multiple Solar Returns Over Time

    Calculate several years of Solar Returns to see planetary movement.
    """
    section_header("Example 2: Multiple Solar Returns")

    natal = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA", name="Kate")
        .with_aspects()
        .calculate()
    )

    print("Natal chart created for Kate")
    print(
        f"Natal Sun: {natal.get_object('Sun').longitude:.4f}° {natal.get_object('Sun').sign}"
    )

    # Calculate Solar Returns for several years
    years = [2020, 2023, 2025, 2030]

    for year in years:
        sr = ReturnBuilder.solar(natal, year).calculate()

        asc = sr.get_object("ASC")
        print(f"\n{year} Solar Return:")
        print(f"  Date: {sr.datetime.utc_datetime.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Sun: {sr.get_object('Sun').longitude:.4f}°")
        print(
            f"  Moon: {sr.get_object('Moon').sign} ({sr.get_object('Moon').longitude:.1f}°)"
        )
        print(f"  Ascendant: {asc.sign if asc else 'N/A'}")

        output = OUTPUT_DIR / f"02_solar_return_{year}.svg"
        sr.draw(str(output)).with_header().save()
        print(f"  Chart: {output}")


def example_3_relocated_solar_return():
    """
    Example 3: Relocated Solar Return

    A relocated Solar Return uses a different location than the natal chart.
    This is useful for seeing how your birthday chart changes based on
    where you spend your birthday.

    The Sun position stays the same (it's returning to natal), but the
    houses and angles change based on the new location.

    Location can be specified as:
    - Coordinates tuple: (latitude, longitude) - most reliable
    - String: "Paris, France" - requires geocoding service
    """
    section_header("Example 3: Relocated Solar Return")

    natal = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

    # Calculate 1903 Solar Return in two locations
    # Paris (where she lived) - using coordinates for reliability
    sr_paris = ReturnBuilder.solar(natal, 1903, location=(48.8566, 2.3522)).calculate()

    # New York (hypothetical relocation)
    sr_ny = ReturnBuilder.solar(natal, 1903, location=(40.7128, -74.0060)).calculate()

    print("1903 Solar Return comparison:")
    print("\nParis:")
    print(
        f"  Location: {sr_paris.location.latitude:.2f}°N, {sr_paris.location.longitude:.2f}°E"
    )
    print(f"  Ascendant: {sr_paris.get_object('ASC').sign}")
    print(f"  MC: {sr_paris.get_object('MC').sign}")

    print("\nNew York:")
    print(
        f"  Location: {sr_ny.location.latitude:.2f}°N, {sr_ny.location.longitude:.2f}°W"
    )
    print(f"  Ascendant: {sr_ny.get_object('ASC').sign}")
    print(f"  MC: {sr_ny.get_object('MC').sign}")

    # Note: Sun position is identical in both!
    print("\nSun position (same in both):")
    print(f"  Paris: {sr_paris.get_object('Sun').longitude:.4f}°")
    print(f"  NY: {sr_ny.get_object('Sun').longitude:.4f}°")

    # Save charts
    sr_paris.draw(str(OUTPUT_DIR / "03_relocated_paris.svg")).with_header().save()
    sr_ny.draw(str(OUTPUT_DIR / "03_relocated_newyork.svg")).with_header().save()
    print("\nCreated: 03_relocated_paris.svg, 03_relocated_newyork.svg")


# =============================================================================
# PART 2: LUNAR RETURNS
# =============================================================================


def example_4_lunar_return_near_date():
    """
    Example 4: Lunar Return Near a Specific Date

    Lunar Returns happen approximately every 27.3 days (the Moon's sidereal period).
    You can find the return nearest to a specific date.
    """
    section_header("Example 4: Lunar Return Near Date")

    natal = ChartBuilder.from_notable("Frida Kahlo").with_aspects().calculate()

    print(
        f"Natal Moon: {natal.get_object('Moon').longitude:.4f}° {natal.get_object('Moon').sign}"
    )

    # Find Lunar Return nearest to a significant date
    # (July 13, 1954 - date of her last public appearance)
    lr = ReturnBuilder.lunar(natal, near_date="1954-07-13").calculate()

    asc = lr.get_object("ASC")
    print("\nLunar Return nearest to July 13, 1954:")
    print(f"  Date: {lr.datetime.utc_datetime}")
    print(f"  Moon: {lr.get_object('Moon').longitude:.4f}°")
    print(f"  Ascendant: {asc.sign if asc else 'N/A'}")

    output = OUTPUT_DIR / "04_lunar_return.svg"
    lr.draw(str(output)).with_header().save()
    print(f"\nCreated: {output}")


def example_5_lunar_return_by_occurrence():
    """
    Example 5: Nth Lunar Return

    Find the Nth Lunar Return after birth. Useful for tracking
    monthly patterns or finding specific returns.
    """
    section_header("Example 5: Nth Lunar Return")

    natal = (
        ChartBuilder.from_details(
            "2000-06-15 10:30", "Seattle, WA", name="Sample Native"
        )
        .with_aspects()
        .calculate()
    )

    print("Calculating first 5 Lunar Returns after birth...")

    for n in range(1, 6):
        lr = ReturnBuilder.lunar(natal, occurrence=n).calculate()

        # Calculate days since birth
        days = lr.datetime.julian_day - natal.datetime.julian_day

        print(f"\n  Lunar Return #{n}:")
        print(f"    Date: {lr.datetime.utc_datetime.strftime('%Y-%m-%d')}")
        print(f"    Days since birth: {days:.1f}")
        print(f"    Moon: {lr.get_object('Moon').sign}")


def example_6_lunar_return_default():
    """
    Example 6: Lunar Return Defaults to Now

    If you don't specify a date or occurrence, the Lunar Return
    defaults to the return nearest to the current moment.
    """
    section_header("Example 6: Lunar Return (Default to Now)")

    natal = ChartBuilder.from_notable("Nikola Tesla").with_aspects().calculate()

    # No date specified - finds return nearest to NOW
    lr_now = ReturnBuilder.lunar(natal).calculate()

    print("Current Lunar Return for Tesla's chart:")
    print(f"  Date: {lr_now.datetime.utc_datetime}")
    print(
        f"  Moon: {lr_now.get_object('Moon').longitude:.4f}° {lr_now.get_object('Moon').sign}"
    )


# =============================================================================
# PART 3: PLANETARY RETURNS (SATURN, JUPITER, ETC.)
# =============================================================================


def example_7_saturn_return():
    """
    Example 7: Saturn Return

    The Saturn Return is one of the most significant astrological transits,
    occurring around ages 29-30, 58-60, and 87-90. It marks major life
    transitions and maturation.
    """
    section_header("Example 7: Saturn Return")

    natal = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA", name="Kate")
        .with_aspects()
        .calculate()
    )

    print(
        f"Natal Saturn: {natal.get_object('Saturn').longitude:.4f}° {natal.get_object('Saturn').sign}"
    )

    # First Saturn Return (~age 29)
    sr1 = ReturnBuilder.planetary(natal, "Saturn", occurrence=1).calculate()

    # Calculate age at return
    years = (sr1.datetime.julian_day - natal.datetime.julian_day) / 365.25

    print("\nFirst Saturn Return:")
    print(f"  Date: {sr1.datetime.utc_datetime.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Age: {years:.1f} years")
    print(f"  Saturn: {sr1.get_object('Saturn').longitude:.4f}°")
    print(f"  Return number: {sr1.metadata.get('return_number')}")

    output = OUTPUT_DIR / "07_saturn_return.svg"
    sr1.draw(str(output)).with_header().save()
    print(f"\nCreated: {output}")


def example_8_jupiter_return():
    """
    Example 8: Jupiter Return

    Jupiter Returns occur approximately every 12 years, marking periods
    of growth, opportunity, and expansion.
    """
    section_header("Example 8: Jupiter Return")

    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print(
        f"Natal Jupiter: {natal.get_object('Jupiter').longitude:.4f}° {natal.get_object('Jupiter').sign}"
    )

    # First three Jupiter Returns
    for n in range(1, 4):
        jr = ReturnBuilder.planetary(natal, "Jupiter", occurrence=n).calculate()
        years = (jr.datetime.julian_day - natal.datetime.julian_day) / 365.25

        print(f"\nJupiter Return #{n}:")
        print(f"  Date: {jr.datetime.utc_datetime.strftime('%Y-%m-%d')}")
        print(f"  Age: {years:.1f} years")


def example_9_mars_return():
    """
    Example 9: Mars Return

    Mars Returns occur approximately every 2 years, marking new cycles
    of energy, assertion, and action.
    """
    section_header("Example 9: Mars Return")

    natal = ChartBuilder.from_notable("Muhammad Ali").with_aspects().calculate()

    # Mars Return near his famous "Rumble in the Jungle" fight (Oct 30, 1974)
    mr = ReturnBuilder.planetary(natal, "Mars", near_date="1974-10-30").calculate()

    print(
        f"Natal Mars: {natal.get_object('Mars').longitude:.4f}° {natal.get_object('Mars').sign}"
    )
    print("\nMars Return near Oct 30, 1974:")
    print(f"  Date: {mr.datetime.utc_datetime.strftime('%Y-%m-%d')}")
    print(f"  Mars: {mr.get_object('Mars').longitude:.4f}°")

    output = OUTPUT_DIR / "09_mars_return.svg"
    mr.draw(str(output)).with_header().save()
    print(f"\nCreated: {output}")


# =============================================================================
# PART 4: ADVANCED CONFIGURATION
# =============================================================================


def example_10_return_with_house_systems():
    """
    Example 10: Return Chart with Multiple House Systems

    ReturnBuilder supports all the same configuration options as ChartBuilder.
    """
    section_header("Example 10: Multiple House Systems")

    natal = ChartBuilder.from_notable("Carl Jung").with_aspects().calculate()

    # Solar Return with both Placidus and Whole Sign houses
    sr = (
        ReturnBuilder.solar(natal, 1912)
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )

    print("1912 Solar Return with multiple house systems:")
    print("\nPlacidus houses:")
    for i, cusp in enumerate(sr.house_systems["Placidus"].cusps[:6], 1):
        print(f"  House {i}: {cusp:.1f}°")

    print("\nWhole Sign houses:")
    for i, cusp in enumerate(sr.house_systems["Whole Sign"].cusps[:6], 1):
        print(f"  House {i}: {cusp:.1f}°")

    output = OUTPUT_DIR / "10_multiple_houses.svg"
    sr.draw(str(output)).with_house_systems("all").with_header().save()
    print(f"\nCreated: {output}")


def example_11_return_with_components():
    """
    Example 11: Return Chart with Additional Components

    Add midpoints, Arabic parts, dignities, etc. to your return chart.
    """
    section_header("Example 11: Return with Components")

    from stellium.components import ArabicPartsCalculator, MidpointCalculator

    natal = ChartBuilder.from_notable("Queen Elizabeth II").with_aspects().calculate()

    # 1952 Solar Return (year she became Queen)
    sr = (
        ReturnBuilder.solar(natal, 1952)
        .with_aspects()
        .add_component(MidpointCalculator())
        .add_component(ArabicPartsCalculator())
        .calculate()
    )

    print("1952 Solar Return (Coronation Year):")
    print(f"  Date: {sr.datetime.utc_datetime.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Sun: {sr.get_object('Sun').sign}")
    print(f"  Ascendant: {sr.get_object('ASC').sign}")

    # Check for Part of Fortune
    if "arabic_parts" in sr.metadata:
        pof = sr.metadata["arabic_parts"].get("Part of Fortune")
        if pof:
            print(f"  Part of Fortune: {pof['longitude']:.1f}°")

    output = OUTPUT_DIR / "11_return_components.svg"
    sr.draw(str(output)).with_header().save()
    print(f"\nCreated: {output}")


def example_12_return_report():
    """
    Example 12: Return Chart Report

    Generate a full report for a return chart.
    """
    section_header("Example 12: Return Report")

    natal = (
        ChartBuilder.from_details(
            "1990-05-20 14:30", "Los Angeles, CA", name="Sample Native"
        )
        .with_aspects()
        .calculate()
    )

    # 2025 Solar Return
    sr = ReturnBuilder.solar(natal, 2025).calculate()

    # Build a report
    report = (
        ReportBuilder()
        .from_chart(sr)
        .with_chart_overview()
        .with_planet_positions()
        .with_aspects(mode="major")
    )

    # Print to terminal
    print("Solar Return Report:")
    report.render(format="rich_table")

    # Save as PDF
    output = OUTPUT_DIR / "12_return_report.pdf"
    report.render(format="pdf", file=str(output))
    print(f"\nCreated: {output}")


# =============================================================================
# PART 5: METADATA AND PRECISION
# =============================================================================


def example_13_return_metadata():
    """
    Example 13: Accessing Return Metadata

    Return charts include special metadata about the return calculation.
    """
    section_header("Example 13: Return Metadata")

    natal = ChartBuilder.from_notable("Vincent van Gogh").with_aspects().calculate()

    sr = ReturnBuilder.solar(natal, 1888).calculate()

    print("1888 Solar Return metadata:")
    print(f"  chart_type: {sr.metadata.get('chart_type')}")
    print(f"  return_planet: {sr.metadata.get('return_planet')}")
    print(f"  natal_planet_longitude: {sr.metadata.get('natal_planet_longitude'):.4f}°")
    print(f"  return_julian_day: {sr.metadata.get('return_julian_day'):.6f}")

    # Verify precision
    natal_sun = natal.get_object("Sun").longitude
    return_sun = sr.get_object("Sun").longitude
    diff = abs(return_sun - natal_sun)

    print("\nPrecision check:")
    print(f"  Natal Sun: {natal_sun:.6f}°")
    print(f"  Return Sun: {return_sun:.6f}°")
    print(f"  Difference: {diff:.6f}° (should be < 0.001°)")


def example_14_precision_demonstration():
    """
    Example 14: Sub-Arcsecond Precision

    Stellium's return calculations achieve sub-arcsecond precision
    using binary search refinement.
    """
    section_header("Example 14: Precision Demonstration")

    natal = (
        ChartBuilder.from_details("1985-07-04 09:15", "Boston, MA", name="Test")
        .with_aspects()
        .calculate()
    )

    planets = ["Sun", "Moon", "Mars", "Jupiter", "Saturn"]

    print("Return precision for various planets:\n")
    print(f"{'Planet':<10} {'Natal Pos':<15} {'Return Pos':<15} {'Diff (arcsec)':<15}")
    print("-" * 55)

    for planet in planets:
        natal_pos = natal.get_object(planet).longitude

        if planet == "Sun":
            ret = ReturnBuilder.solar(natal, 2025).calculate()
        elif planet == "Moon":
            ret = ReturnBuilder.lunar(natal, near_date="2025-06-01").calculate()
        else:
            ret = ReturnBuilder.planetary(
                natal, planet, near_date="2025-01-01"
            ).calculate()

        return_pos = ret.get_object(planet).longitude
        diff_deg = abs(return_pos - natal_pos)
        diff_arcsec = diff_deg * 3600  # Convert to arcseconds

        print(
            f"{planet:<10} {natal_pos:<15.4f} {return_pos:<15.4f} {diff_arcsec:<15.2f}"
        )


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================


def main():
    """Run all examples in sequence."""
    print("\n" + "=" * 60)
    print("  STELLIUM PLANETARY RETURNS COOKBOOK")
    print("=" * 60)

    # Part 1: Solar Returns
    example_1_simple_solar_return()
    example_2_multiple_solar_returns()
    example_3_relocated_solar_return()

    # Part 2: Lunar Returns
    example_4_lunar_return_near_date()
    example_5_lunar_return_by_occurrence()
    example_6_lunar_return_default()

    # Part 3: Planetary Returns
    example_7_saturn_return()
    example_8_jupiter_return()
    example_9_mars_return()

    # Part 4: Advanced Configuration
    example_10_return_with_house_systems()
    example_11_return_with_components()
    example_12_return_report()

    # Part 5: Metadata and Precision
    example_13_return_metadata()
    example_14_precision_demonstration()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE!")
    print(f"  Charts saved to: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
