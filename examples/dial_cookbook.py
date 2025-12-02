#!/usr/bin/env python3
"""
Uranian Dial Cookbook - Examples for Stellium Dial Chart Visualization

This cookbook demonstrates how to create Uranian/Hamburg school dial charts
with Stellium. Dial charts compress the zodiac to reveal hard aspects - on a
90-degree dial, conjunctions, squares, and oppositions all appear as conjunctions.

Dial Types:
- 90-degree dial: Most common, compresses zodiac by 4x
- 45-degree dial: Compresses by 8x (includes semi-squares, sesquiquadrates)
- 360-degree dial: Full zodiac with rotatable pointer

Uranian Astrology Objects:
- TNOs (Trans-Neptunian Objects): Eris, Sedna, Makemake, Haumea, Orcus, Quaoar
  Enable with: ChartBuilder.from_native(...).with_tnos()

- Hamburg Hypothetical Planets: Cupido, Hades, Zeus, Kronos, Apollon, Admetos,
  Vulkanus, Poseidon
  Enable with: ChartBuilder.from_native(...).with_uranian()

Run this script to generate example charts in examples/dials/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/dial_cookbook.py

For full documentation, see docs/VISUALIZATION.md
"""

import os
from datetime import datetime
from pathlib import Path

from stellium import ChartBuilder
from stellium.core.native import Native

# Output directory for generated charts
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "dials"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC DIAL CHARTS
# =============================================================================


def example_1_simplest_dial():
    """
    Example 1: The Simplest 90-Degree Dial

    Just call .draw_dial() and .save() - that's it!
    The 90-degree dial compresses the zodiac so that all cardinal signs
    (Aries, Cancer, Libra, Capricorn) appear at 0 degrees.

    For full Uranian astrology support, use:
    - .with_tnos() to include Trans-Neptunian Objects (Eris, Sedna, etc.)
    - .with_uranian() to include Hamburg hypothetical planets (Cupido, Hades,
      Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon)

    Note: These require the appropriate Swiss Ephemeris files to be installed.
    """
    section_header("Example 1: Simplest 90-Degree Dial")

    # Use both .with_tnos() and .with_uranian() for full Uranian astrology support
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_tnos()
        .with_uranian()
        .calculate()
    )

    output = OUTPUT_DIR / "01_simplest_90.svg"
    chart.draw_dial(str(output)).save()

    print(f"Created: {output}")
    print("Notice how planets in square or opposition appear close together!")


def example_2_different_dial_sizes():
    """
    Example 2: Different Dial Sizes (90, 45, 360)

    Each dial size reveals different aspects:
    - 90-degree: Shows conjunctions, squares (90), and oppositions (180)
    - 45-degree: Also shows semi-squares (45) and sesquiquadrates (135)
    - 360-degree: Full zodiac with rotatable pointer for aspect analysis

    This example uses .with_uranian() to include Hamburg hypothetical planets.
    """
    section_header("Example 2: Different Dial Sizes")

    chart = ChartBuilder.from_notable("Nikola Tesla").with_uranian().calculate()

    # 90-degree dial (default)
    output_90 = OUTPUT_DIR / "02_dial_90.svg"
    chart.draw_dial(str(output_90), degrees=90).save()
    print(f"Created: {output_90} (90-degree)")

    # 45-degree dial
    output_45 = OUTPUT_DIR / "02_dial_45.svg"
    chart.draw_dial(str(output_45), degrees=45).save()
    print(f"Created: {output_45} (45-degree)")

    # 360-degree dial
    output_360 = OUTPUT_DIR / "02_dial_360.svg"
    chart.draw_dial(str(output_360), degrees=360).save()
    print(f"Created: {output_360} (360-degree)")


def example_3_with_size():
    """
    Example 3: Custom Size

    Specify the dial size in pixels using .with_size().
    Default is 600px. Larger sizes show more detail.

    This example includes both TNOs and Uranian planets for a complete chart.
    """
    section_header("Example 3: Custom Size")

    chart = (
        ChartBuilder.from_notable("Marie Curie").with_tnos().with_uranian().calculate()
    )

    # Small dial (400px)
    small = OUTPUT_DIR / "03_small.svg"
    chart.draw_dial(str(small)).with_size(400).save()
    print(f"Created: {small} (400px)")

    # Large dial (900px)
    large = OUTPUT_DIR / "03_large.svg"
    chart.draw_dial(str(large)).with_size(900).save()
    print(f"Created: {large} (900px)")


# =============================================================================
# PART 2: THEMES
# =============================================================================


def example_4_themes():
    """
    Example 4: Visual Themes

    Dial charts use the same themes as regular charts.
    All colors are derived from the theme for consistency.

    Available themes: classic, dark, midnight, celestial, neon, sepia, pastel
    Scientific themes: viridis, plasma, inferno, magma, cividis, turbo

    This example includes Uranian planets for Hamburg school analysis.
    """
    section_header("Example 4: Themes")

    chart = ChartBuilder.from_notable("Frida Kahlo").with_uranian().calculate()

    themes = ["classic", "dark", "midnight", "celestial", "neon", "sepia"]

    for theme in themes:
        output = OUTPUT_DIR / f"04_theme_{theme}.svg"
        chart.draw_dial(str(output)).with_theme(theme).save()
        print(f"Created: {output}")


def example_5_scientific_themes():
    """
    Example 5: Scientific Colormap Themes

    Themes based on matplotlib's perceptually uniform colormaps.
    Great for presentations and publications.

    These themes provide excellent contrast and are colorblind-friendly.
    Includes Uranian planets for complete Hamburg school charts.
    """
    section_header("Example 5: Scientific Themes")

    chart = ChartBuilder.from_notable("Carl Sagan").with_uranian().calculate()

    themes = ["viridis", "plasma", "inferno", "turbo"]

    for theme in themes:
        output = OUTPUT_DIR / f"05_theme_{theme}.svg"
        chart.draw_dial(str(output)).with_theme(theme).save()
        print(f"Created: {output}")


# =============================================================================
# PART 3: MIDPOINTS
# =============================================================================


def example_6_with_midpoints():
    """
    Example 6: Midpoints

    Midpoints are enabled by default on dial charts. They appear on the
    outer ring and show the halfway point between two planets.

    In Uranian astrology, midpoints are considered as significant as
    planetary positions. The Hamburg school pioneered midpoint analysis.

    Includes Uranian planets (Cupido, Hades, Zeus, etc.) for full analysis.
    """
    section_header("Example 6: Midpoints")

    chart = ChartBuilder.from_notable("Carl Jung").with_uranian().calculate()

    # Default - midpoints shown
    with_mp = OUTPUT_DIR / "06_with_midpoints.svg"
    chart.draw_dial(str(with_mp)).with_theme("midnight").save()
    print(f"Created: {with_mp} (with midpoints)")

    # Without midpoints
    without_mp = OUTPUT_DIR / "06_without_midpoints.svg"
    chart.draw_dial(str(without_mp)).with_theme("midnight").without_midpoints().save()
    print(f"Created: {without_mp} (without midpoints)")


def example_7_midpoint_notation():
    """
    Example 7: Midpoint Notation Styles

    Choose how midpoints are displayed:
    - "full": Shows both planet glyphs (e.g., "Sun/Moon")
    - "abbreviated": Shortened notation
    - "tick": Just a tick mark (cleanest, best for crowded charts)

    Full Uranian setup with both TNOs and Hamburg planets.
    """
    section_header("Example 7: Midpoint Notation")

    chart = (
        ChartBuilder.from_notable("Sigmund Freud")
        .with_tnos()
        .with_uranian()
        .calculate()
    )

    # Full notation (default)
    full = OUTPUT_DIR / "07_midpoint_full.svg"
    chart.draw_dial(str(full)).with_midpoints(notation="full").save()
    print(f"Created: {full} (full notation)")

    # Tick marks only
    tick = OUTPUT_DIR / "07_midpoint_tick.svg"
    chart.draw_dial(str(tick)).with_midpoints(notation="tick").save()
    print(f"Created: {tick} (tick only)")


# =============================================================================
# PART 4: 360-DEGREE DIAL WITH POINTER
# =============================================================================


def example_8_pointer_to_planet():
    """
    Example 8: 360-Degree Dial with Pointer

    The 360-degree dial includes a pointer that can be set to point
    at any planet. This is useful for analyzing aspects to a specific point.

    Point to a planet by name (e.g., "Sun", "Moon", "Cupido") or by degree.
    Includes Uranian planets for complete Hamburg school analysis.
    """
    section_header("Example 8: Pointer to Planet")

    chart = ChartBuilder.from_notable("Albert Einstein").with_uranian().calculate()

    # Pointer to Sun
    sun = OUTPUT_DIR / "08_pointer_sun.svg"
    chart.draw_dial(str(sun), degrees=360).with_pointer("Sun").with_theme(
        "celestial"
    ).save()
    print(f"Created: {sun} (pointer to Sun)")

    # Pointer to Moon
    moon = OUTPUT_DIR / "08_pointer_moon.svg"
    chart.draw_dial(str(moon), degrees=360).with_pointer("Moon").with_theme(
        "celestial"
    ).save()
    print(f"Created: {moon} (pointer to Moon)")

    # Pointer to MC
    mc = OUTPUT_DIR / "08_pointer_mc.svg"
    chart.draw_dial(str(mc), degrees=360).with_pointer("MC").with_theme(
        "celestial"
    ).save()
    print(f"Created: {mc} (pointer to MC)")


def example_9_pointer_to_degree():
    """
    Example 9: Pointer to Specific Degree

    You can also point to a specific degree value (0-360).
    Useful for analyzing sensitive points like the Aries Point (0 degrees).

    Includes Uranian planets for Hamburg school midpoint analysis.
    """
    section_header("Example 9: Pointer to Degree")

    chart = ChartBuilder.from_notable("Nikola Tesla").with_uranian().calculate()

    # Pointer to 0 degrees (Aries point)
    aries = OUTPUT_DIR / "09_pointer_0.svg"
    chart.draw_dial(str(aries), degrees=360).with_pointer(0.0).with_theme("dark").save()
    print(f"Created: {aries} (pointer to 0 degrees / Aries point)")

    # Pointer to 90 degrees
    cancer = OUTPUT_DIR / "09_pointer_90.svg"
    chart.draw_dial(str(cancer), degrees=360).with_pointer(90.0).with_theme(
        "dark"
    ).save()
    print(f"Created: {cancer} (pointer to 90 degrees)")


# =============================================================================
# PART 5: TRANSITS AND OUTER RINGS
# =============================================================================


def example_10_with_transits():
    """
    Example 10: Dial with Transit Planets

    Add transit planets on an outer ring to see how they
    aspect the natal chart. Essential for timing analysis.

    Both natal and transit charts include Uranian planets for
    complete Hamburg school transit analysis.
    """
    section_header("Example 10: Transits on Outer Ring")

    # Natal chart with Uranian planets
    natal = ChartBuilder.from_notable("Albert Einstein").with_uranian().calculate()

    # Transit chart for today with Uranian planets
    transit_native = Native(datetime.now(), "Zurich, Switzerland")
    transit = ChartBuilder.from_native(transit_native).with_uranian().calculate()

    output = OUTPUT_DIR / "10_with_transits.svg"
    (
        natal.draw_dial(str(output))
        .with_theme("midnight")
        .with_outer_ring(transit.get_planets(), label="Transits")
        .save()
    )

    print(f"Created: {output}")
    print("Transit planets appear on the outer ring")


def example_11_multiple_outer_rings():
    """
    Example 11: Multiple Outer Rings

    You can add multiple outer rings for different timing techniques:
    - Transits for different dates
    - Solar arc directions
    - Progressed positions

    All charts include Uranian planets for complete analysis.
    """
    section_header("Example 11: Multiple Outer Rings")

    # Natal chart with Uranian planets
    natal = ChartBuilder.from_notable("Albert Einstein").with_uranian().calculate()

    # Two different transit dates with Uranian planets
    transit1_native = Native(datetime(2024, 3, 14, 12, 0), "Princeton, NJ")
    transit1 = ChartBuilder.from_native(transit1_native).with_uranian().calculate()

    transit2_native = Native(datetime(2025, 3, 14, 12, 0), "Princeton, NJ")
    transit2 = ChartBuilder.from_native(transit2_native).with_uranian().calculate()

    output = OUTPUT_DIR / "11_multiple_rings.svg"
    (
        natal.draw_dial(str(output))
        .with_theme("celestial")
        .with_outer_ring(transit1.get_planets(), ring="outer_ring_1", label="2024")
        .with_outer_ring(transit2.get_planets(), ring="outer_ring_2", label="2025")
        .without_midpoints()  # Remove midpoints to reduce clutter
        .save()
    )

    print(f"Created: {output}")


# =============================================================================
# PART 6: LAYER CUSTOMIZATION
# =============================================================================


def example_12_minimal_dial():
    """
    Example 12: Minimal Dial

    Remove layers for a cleaner look using:
    - .without_midpoints() - removes midpoint markers
    - .without_cardinal_points() - removes cardinal point labels
    - .without_modality_wheel() - removes inner zodiac wheel
    - .without_tnos() - excludes Trans-Neptunian Objects
    - .without_uranian() - excludes Hamburg hypothetical planets

    This example shows traditional planets only.
    """
    section_header("Example 12: Minimal Dial")

    # Traditional planets only (no TNOs or Uranian)
    chart = ChartBuilder.from_notable("Leonardo da Vinci").calculate()

    output = OUTPUT_DIR / "12_minimal.svg"
    (
        chart.draw_dial(str(output))
        .without_midpoints()
        .without_cardinal_points()
        .without_tnos()
        .without_uranian()
        .with_theme("sepia")
        .save()
    )

    print(f"Created: {output}")


def example_13_no_modality_wheel():
    """
    Example 13: Without Modality Wheel

    Remove the inner modality wheel for a simpler look.
    The modality wheel shows cardinal/fixed/mutable groupings.

    Includes Uranian planets but removes the inner wheel.
    """
    section_header("Example 13: No Modality Wheel")

    chart = ChartBuilder.from_notable("Isaac Newton").with_uranian().calculate()

    output = OUTPUT_DIR / "13_no_modality.svg"
    (chart.draw_dial(str(output)).without_modality_wheel().with_theme("dark").save())

    print(f"Created: {output}")


# =============================================================================
# PART 7: PROFESSIONAL EXAMPLES
# =============================================================================


def example_14_uranian_analysis():
    """
    Example 14: Professional Uranian Analysis Chart

    A complete dial chart suitable for professional Uranian astrology work.
    Includes all Hamburg hypothetical planets and full midpoint analysis.

    The Hamburg School (founded by Alfred Witte) uses:
    - 90-degree dial for aspect analysis
    - Midpoints as primary interpretive tool
    - 8 hypothetical planets (Cupido through Poseidon)
    """
    section_header("Example 14: Professional Uranian Analysis")

    chart = (
        ChartBuilder.from_notable("Carl Jung").with_tnos().with_uranian().calculate()
    )

    output = OUTPUT_DIR / "14_professional_uranian.svg"
    (
        chart.draw_dial(str(output))
        .with_size(800)
        .with_theme("midnight")
        .with_midpoints(notation="full")
        .save()
    )

    print(f"Created: {output}")
    print("Complete dial with midpoints for Uranian analysis")


def example_15_cosmobiology_style():
    """
    Example 15: Cosmobiology Style

    A 90-degree dial in the style used in Cosmobiology (Reinhold Ebertin).
    Clean and minimal for focused analysis with tick-mark midpoints.

    Cosmobiology emphasizes:
    - 90-degree dial
    - Midpoint structures
    - Planetary pictures (three-planet combinations)

    Includes Uranian planets for complete analysis.
    """
    section_header("Example 15: Cosmobiology Style")

    chart = ChartBuilder.from_notable("Sigmund Freud").with_uranian().calculate()

    output = OUTPUT_DIR / "15_cosmobiology.svg"
    (
        chart.draw_dial(str(output))
        .with_size(700)
        .with_theme("classic")
        .with_midpoints(notation="tick")  # Clean tick marks
        .save()
    )

    print(f"Created: {output}")


def example_16_transit_analysis():
    """
    Example 16: Transit Analysis with 360 Dial

    Use a 360-degree dial to analyze specific transit aspects.
    Point to the transiting planet to see what it aspects.

    This technique is used to analyze how a transiting planet
    activates natal positions and midpoints.

    Both charts include Uranian planets for complete Hamburg analysis.
    """
    section_header("Example 16: Transit Analysis")

    natal = ChartBuilder.from_notable("Albert Einstein").with_uranian().calculate()

    # Current transits with Uranian planets
    transit_native = Native(datetime.now(), "Zurich, Switzerland")
    transit = ChartBuilder.from_native(transit_native).with_uranian().calculate()

    # Get current Saturn position and point to it
    saturn = transit.get_object("Saturn")
    saturn_deg = saturn.longitude if saturn else 0

    output = OUTPUT_DIR / "16_transit_analysis.svg"
    (
        natal.draw_dial(str(output), degrees=360)
        .with_theme("celestial")
        .with_pointer(saturn_deg)  # Point to transiting Saturn
        .with_outer_ring(transit.get_planets(), label="Current Transits")
        .without_midpoints()
        .save()
    )

    print(f"Created: {output}")
    print(f"Pointer set to Saturn at {saturn_deg:.1f} degrees")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("  URANIAN DIAL COOKBOOK")
    print("  Generating example dial charts...")
    print("=" * 60)

    # Part 1: Basic Dials
    example_1_simplest_dial()
    example_2_different_dial_sizes()
    example_3_with_size()

    # Part 2: Themes
    example_4_themes()
    example_5_scientific_themes()

    # Part 3: Midpoints
    example_6_with_midpoints()
    example_7_midpoint_notation()

    # Part 4: Pointer
    example_8_pointer_to_planet()
    example_9_pointer_to_degree()

    # Part 5: Transits
    example_10_with_transits()
    example_11_multiple_outer_rings()

    # Part 6: Customization
    example_12_minimal_dial()
    example_13_no_modality_wheel()

    # Part 7: Professional
    example_14_uranian_analysis()
    example_15_cosmobiology_style()
    example_16_transit_analysis()

    print("\n" + "=" * 60)
    print(f"  All examples generated in: {OUTPUT_DIR}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
