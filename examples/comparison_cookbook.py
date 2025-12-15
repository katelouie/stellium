#!/usr/bin/env python3
"""
Comparison Charts Cookbook - Synastry, Transits & Bi-Wheels

This cookbook demonstrates how to create and visualize comparison charts
in Stellium, including synastry (relationship), transit, and progression charts.

Run this script to generate example comparison charts in examples/comparisons/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/comparison_cookbook.py

For full documentation, see docs/CHART_TYPES.md
"""

import os
from datetime import datetime
from pathlib import Path

from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder
from stellium.core.config import AspectConfig
from stellium.engines.aspects import CrossChartAspectEngine
from stellium.engines.orbs import SimpleOrbEngine

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "comparisons"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC SYNASTRY
# =============================================================================


def example_1_simple_synastry():
    """
    Example 1: Simple Synastry Chart

    The most basic synastry - compare two people's charts.
    """
    section_header("Example 1: Simple Synastry")

    # Calculate individual charts
    person1 = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

    # Create synastry comparison using MultiChartBuilder
    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Albert Einstein", label2="Marie Curie"
        )
        .with_cross_aspects()
        .calculate()
    )

    # Display cross-chart aspects
    all_aspects = synastry.get_all_cross_aspects()
    print(f"Cross-chart aspects found: {len(all_aspects)}")
    print("\nTop 5 aspects (by orb):")
    for asp in sorted(all_aspects, key=lambda a: a.orb)[:5]:
        print(
            f"  {asp.object1.name} {asp.aspect_name} {asp.object2.name} "
            f"(orb: {asp.orb:.2f}°)"
        )

    # Draw bi-wheel chart
    output = OUTPUT_DIR / "01_simple_synastry.svg"
    synastry.draw(str(output)).save()
    print(f"\nCreated: {output}")


def example_2_synastry_with_styling():
    """
    Example 2: Styled Synastry Chart

    Add themes, colors, and styling to your synastry chart.
    """
    section_header("Example 2: Styled Synastry")

    person1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="John Lennon", label2="Yoko Ono"
        )
        .with_cross_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "02_styled_synastry.svg"

    (
        synastry.draw(str(output))
        .with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .save()
    )

    print(f"Created: {output}")


def example_3_synastry_with_tables():
    """
    Example 3: Synastry with Position Tables

    Show side-by-side position tables for both charts.
    """
    section_header("Example 3: Synastry with Tables")

    person1 = ChartBuilder.from_notable("Prince William").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Kate Middleton").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Prince William", label2="Kate Middleton"
        )
        .with_cross_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "03_synastry_tables.svg"

    synastry.draw(str(output)).with_theme("midnight").with_tables().save()

    print(f"Created: {output}")


# =============================================================================
# PART 2: SYNASTRY ANALYSIS
# =============================================================================


def example_4_house_overlays():
    """
    Example 4: House Overlays

    See where one person's planets fall in the other's houses.
    """
    section_header("Example 4: House Overlays")

    person1 = ChartBuilder.from_notable("Barack Obama").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Michelle Obama").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(person1, person2, label1="Barack", label2="Michelle")
        .with_cross_aspects()
        .with_house_overlays()
        .calculate()
    )

    # Get house overlays for the pair (0, 1)
    house_overlays = synastry.house_overlays.get((0, 1), [])
    print(f"House overlays calculated: {len(house_overlays)}")

    print("\nBarack's planets in Michelle's houses:")
    for overlay in house_overlays:
        if overlay.planet_owner == 0 and overlay.house_owner == 1:
            print(f"  {overlay.planet_name} in house {overlay.falls_in_house}")

    print("\nMichelle's planets in Barack's houses:")
    for overlay in house_overlays:
        if overlay.planet_owner == 1 and overlay.house_owner == 0:
            print(f"  {overlay.planet_name} in house {overlay.falls_in_house}")

    output = OUTPUT_DIR / "04_house_overlays.svg"
    synastry.draw(str(output)).with_theme("dark").save()
    print(f"\nCreated: {output}")


def example_5_compatibility_score():
    """
    Example 5: Compatibility Scoring

    Calculate a simple compatibility score from aspects.
    """
    section_header("Example 5: Compatibility Score")

    person1 = ChartBuilder.from_notable("Brad Pitt").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Angelina Jolie").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Brad Pitt", label2="Angelina Jolie"
        )
        .with_cross_aspects()
        .calculate()
    )

    # Calculate compatibility score
    score = synastry.calculate_compatibility_score()
    print(f"Compatibility score: {score:.1f}/100")

    # Aspect breakdown
    aspect_counts = {}
    for asp in synastry.get_all_cross_aspects():
        aspect_counts[asp.aspect_name] = aspect_counts.get(asp.aspect_name, 0) + 1

    print("\nAspect breakdown:")
    for name, count in sorted(aspect_counts.items()):
        print(f"  {name}: {count}")


def example_6_query_aspects():
    """
    Example 6: Query Specific Aspects

    Find aspects involving specific planets.
    """
    section_header("Example 6: Query Aspects")

    person1 = ChartBuilder.from_notable("Elizabeth Taylor").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Richard Burton").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Elizabeth", label2="Richard"
        )
        .with_cross_aspects()
        .calculate()
    )

    # Get Venus aspects (relationship planet)
    print("Elizabeth's Venus aspects to Richard's chart:")
    venus_aspects = synastry.get_object_aspects("Venus", chart=0)
    for asp in venus_aspects:
        print(f"  Venus {asp.aspect_name} {asp.object2.name}")

    # Get Moon aspects (emotional connection)
    print("\nRichard's Moon aspects to Elizabeth's chart:")
    moon_aspects = synastry.get_object_aspects("Moon", chart=1)
    for asp in moon_aspects:
        print(f"  Moon {asp.aspect_name} {asp.object1.name}")


# =============================================================================
# PART 3: TRANSIT CHARTS
# =============================================================================


def example_7_current_transits():
    """
    Example 7: Current Transits

    See how current planets aspect a natal chart.
    """
    section_header("Example 7: Current Transits")

    # Natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Transit time
    transit_time = datetime(2025, 6, 21, 12, 0)  # Summer solstice 2025

    # Create transit chart at natal location
    transit_chart = (
        ChartBuilder.from_details(
            transit_time,
            (natal.location.latitude, natal.location.longitude),
        )
        .with_aspects()
        .calculate()
    )

    # Compare using MultiChartBuilder.transit()
    transits = (
        MultiChartBuilder.transit(
            natal, transit_chart, natal_label="Natal", transit_label="Transits"
        )
        .with_cross_aspects()
        .calculate()
    )

    all_transits = transits.get_all_cross_aspects()
    print(f"Transit aspects found: {len(all_transits)}")
    print("\nTransits to natal Sun:")
    sun_transits = [asp for asp in all_transits if asp.object1.name == "Sun"]
    for asp in sun_transits[:5]:
        applying = "applying" if asp.is_applying else "separating"
        print(
            f"  Transit {asp.object2.name} {asp.aspect_name} Sun "
            f"(orb: {asp.orb:.2f}°, {applying})"
        )

    output = OUTPUT_DIR / "07_current_transits.svg"
    transits.draw(str(output)).with_theme("midnight").save()
    print(f"\nCreated: {output}")


def example_8_transit_with_tight_orbs():
    """
    Example 8: Transits with Tight Orbs

    Use tighter orbs for more precise transit timing.
    """
    section_header("Example 8: Tight Orb Transits")

    natal = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

    transit_time = datetime(2025, 3, 20, 0, 0)  # Spring equinox 2025

    transit_chart = (
        ChartBuilder.from_details(
            transit_time,
            (natal.location.latitude, natal.location.longitude),
        )
        .with_aspects()
        .calculate()
    )

    # Use very tight orbs (2°/1°)
    tight_orbs = SimpleOrbEngine(
        orb_map={
            "Conjunction": 2.0,
            "Sextile": 1.0,
            "Square": 2.0,
            "Trine": 2.0,
            "Opposition": 2.0,
        }
    )

    transits = (
        MultiChartBuilder.transit(
            natal, transit_chart, natal_label="Natal", transit_label="Transits"
        )
        .with_cross_aspects()
        .with_orb_engine(tight_orbs)
        .calculate()
    )

    all_transits = transits.get_all_cross_aspects()
    print(f"Exact transits (2° orb): {len(all_transits)}")
    for asp in all_transits[:5]:
        print(
            f"  {asp.object2.name} {asp.aspect_name} {asp.object1.name} "
            f"(orb: {asp.orb:.2f}°)"
        )


# =============================================================================
# PART 4: ADVANCED CONFIGURATION
# =============================================================================


def example_9_custom_aspect_types():
    """
    Example 9: Custom Aspect Types

    Calculate only specific aspect types.
    """
    section_header("Example 9: Custom Aspect Types")

    person1 = ChartBuilder.from_notable("Nikola Tesla").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Thomas Edison").with_aspects().calculate()

    # Only hard aspects
    hard_aspects_config = AspectConfig(
        aspects=["Conjunction", "Square", "Opposition"],
        include_angles=True,
        include_asteroids=False,
    )

    hard_engine = CrossChartAspectEngine(config=hard_aspects_config)

    synastry = (
        MultiChartBuilder.synastry(person1, person2, label1="Tesla", label2="Edison")
        .with_cross_aspects()
        .with_aspect_engine(hard_engine)
        .calculate()
    )

    all_aspects = synastry.get_all_cross_aspects()
    print(f"Hard aspects only: {len(all_aspects)}")

    aspect_counts = {}
    for asp in all_aspects:
        aspect_counts[asp.aspect_name] = aspect_counts.get(asp.aspect_name, 0) + 1

    for name, count in sorted(aspect_counts.items()):
        print(f"  {name}: {count}")


def example_10_no_house_overlays():
    """
    Example 10: Skip House Overlays

    Calculate only aspects (faster for quick analysis).
    """
    section_header("Example 10: Aspects Only (No Overlays)")

    person1 = ChartBuilder.from_notable("Leonardo da Vinci").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Michelangelo").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Leonardo", label2="Michelangelo"
        )
        .with_cross_aspects()
        # No .with_house_overlays() - skip house overlay calculation
        .calculate()
    )

    all_aspects = synastry.get_all_cross_aspects()
    print(f"Aspects calculated: {len(all_aspects)}")
    overlays = synastry.get_house_overlays(0, 1)
    print(f"House overlays: {len(overlays)} (skipped)")


# =============================================================================
# PART 5: COMPARISON REPORTS
# =============================================================================


def example_11_synastry_pdf_report():
    """
    Example 11: Synastry PDF Report

    Generate a complete synastry report with PDF output.
    """
    section_header("Example 11: Synastry PDF Report")

    person1 = ChartBuilder.from_notable("Paul McCartney").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()

    synastry = (
        MultiChartBuilder.synastry(
            person1, person2, label1="Paul McCartney", label2="John Lennon"
        )
        .with_cross_aspects()
        .calculate()
    )

    # Generate biwheel
    svg_path = OUTPUT_DIR / "11_beatles_biwheel.svg"
    synastry.draw(str(svg_path)).with_theme("celestial").save()
    print(f"Created biwheel: {svg_path}")

    # Generate PDF report
    pdf_path = OUTPUT_DIR / "11_beatles_synastry.pdf"
    (
        ReportBuilder()
        .from_chart(synastry)
        .preset_synastry()
        .with_title("Paul McCartney & John Lennon - Synastry")
        .with_chart_image(str(svg_path))
        .render(format="pdf", file=str(pdf_path), show=False)
    )
    print(f"Created PDF: {pdf_path}")


def example_12_transit_pdf_report():
    """
    Example 12: Transit PDF Report

    Generate a transit report with PDF output.
    """
    section_header("Example 12: Transit PDF Report")

    natal = ChartBuilder.from_notable("Oprah Winfrey").with_aspects().calculate()

    transit_time = datetime(2025, 1, 1, 0, 0)

    transit_chart = (
        ChartBuilder.from_details(
            transit_time,
            (natal.location.latitude, natal.location.longitude),
        )
        .with_aspects()
        .calculate()
    )

    transits = (
        MultiChartBuilder.transit(
            natal, transit_chart, natal_label="Natal", transit_label="Transits 2025"
        )
        .with_cross_aspects()
        .calculate()
    )

    pdf_path = OUTPUT_DIR / "12_oprah_transits.pdf"
    (
        ReportBuilder()
        .from_chart(transits)
        .preset_transit()
        .with_title("Oprah Winfrey - Transits for 2025")
        .render(format="pdf", file=str(pdf_path), show=False)
    )
    print(f"Created: {pdf_path}")


# =============================================================================
# PART 6: BATCH COMPARISONS
# =============================================================================


def example_13_batch_synastry():
    """
    Example 13: Batch Synastry Charts

    Generate synastry charts for multiple couples.
    """
    section_header("Example 13: Batch Synastry")

    couples = [
        ("Albert Einstein", "Marie Curie", "scientific"),
        ("John Lennon", "Yoko Ono", "artistic"),
        ("Barack Obama", "Michelle Obama", "political"),
    ]

    for name1, name2, category in couples:
        chart1 = ChartBuilder.from_notable(name1).with_aspects().calculate()
        chart2 = ChartBuilder.from_notable(name2).with_aspects().calculate()

        synastry = (
            MultiChartBuilder.synastry(
                chart1, chart2, label1=name1.split()[0], label2=name2.split()[0]
            )
            .with_cross_aspects()
            .calculate()
        )

        filename = f"13_{category}_couple.svg"
        output = OUTPUT_DIR / filename

        synastry.draw(str(output)).with_theme("midnight").save()

        print(f"Created: {output} ({len(synastry.get_all_cross_aspects())} aspects)")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run selected examples."""
    print("\n" + "=" * 60)
    print("  STELLIUM COMPARISON CHARTS COOKBOOK")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}\n")

    # --- Part 1: Basic Synastry ---
    example_1_simple_synastry()
    example_2_synastry_with_styling()
    example_3_synastry_with_tables()

    # --- Part 2: Synastry Analysis ---
    example_4_house_overlays()
    example_5_compatibility_score()
    example_6_query_aspects()

    # --- Part 3: Transit Charts ---
    example_7_current_transits()
    example_8_transit_with_tight_orbs()

    # --- Part 4: Advanced Configuration ---
    example_9_custom_aspect_types()
    example_10_no_house_overlays()

    # --- Part 5: Reports ---
    # Note: PDF reports for MultiChart are not yet supported.
    # These examples will be enabled once the presentation layer
    # is updated to handle MultiChart objects.
    # example_11_synastry_pdf_report()
    # example_12_transit_pdf_report()

    # --- Part 6: Batch ---
    example_13_batch_synastry()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files are in: {OUTPUT_DIR}")
    print("See docs/CHART_TYPES.md for full documentation.\n")


if __name__ == "__main__":
    main()
