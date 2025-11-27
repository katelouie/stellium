#!/usr/bin/env python3
"""
Chart Visualization Cookbook - Examples for Stellium Chart Drawing

This cookbook demonstrates all the ways to create beautiful natal chart
visualizations with Stellium, from simple wheels to fully-featured charts
with tables, multiple house systems, and custom styling.

Run this script to generate example charts in examples/charts/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/chart_cookbook.py

For full documentation, see docs/VISUALIZATION.md
"""

import os
from pathlib import Path

from stellium import ChartBuilder
from stellium.engines import KochHouses, PlacidusHouses, WholeSignHouses

# Output directory for generated charts
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC CHARTS
# =============================================================================


def example_1_simplest_chart():
    """
    Example 1: The Simplest Possible Chart

    Just call .draw() and .save() - that's it!
    """
    section_header("Example 1: Simplest Chart")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    output = OUTPUT_DIR / "01_simplest.svg"
    chart.draw(str(output)).save()

    print(f"Created: {output}")


def example_2_with_size():
    """
    Example 2: Custom Size

    Specify the chart size in pixels.
    """
    section_header("Example 2: Custom Size")

    chart = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

    # Small chart (400px)
    small = OUTPUT_DIR / "02_small.svg"
    chart.draw(str(small)).with_size(400).save()
    print(f"Created: {small} (400px)")

    # Large chart (1200px)
    large = OUTPUT_DIR / "02_large.svg"
    chart.draw(str(large)).with_size(1200).save()
    print(f"Created: {large} (1200px)")


def example_3_presets():
    """
    Example 3: Using Presets

    Presets bundle common configurations for quick setup.
    """
    section_header("Example 3: Presets")

    chart = ChartBuilder.from_notable("Nikola Tesla").with_aspects().calculate()

    # Minimal preset - just the wheel
    minimal = OUTPUT_DIR / "03_preset_minimal.svg"
    chart.draw(str(minimal)).preset_minimal().save()
    print(f"Created: {minimal} (minimal)")

    # Standard preset - wheel + info corners
    standard = OUTPUT_DIR / "03_preset_standard.svg"
    chart.draw(str(standard)).preset_standard().save()
    print(f"Created: {standard} (standard)")

    # Detailed preset - everything
    detailed = OUTPUT_DIR / "03_preset_detailed.svg"
    chart.draw(str(detailed)).preset_detailed().save()
    print(f"Created: {detailed} (detailed)")


# =============================================================================
# PART 2: THEMES
# =============================================================================


def example_4_themes():
    """
    Example 4: Visual Themes

    Themes control the overall color scheme of your chart.
    """
    section_header("Example 4: Themes")

    chart = ChartBuilder.from_notable("Frida Kahlo").with_aspects().calculate()

    themes = ["classic", "dark", "midnight", "celestial", "neon", "sepia", "pastel"]

    for theme in themes:
        output = OUTPUT_DIR / f"04_theme_{theme}.svg"
        chart.draw(str(output)).with_theme(theme).save()
        print(f"Created: {output}")


def example_5_scientific_themes():
    """
    Example 5: Scientific Colormap Themes

    Themes based on matplotlib's perceptually uniform colormaps.
    """
    section_header("Example 5: Scientific Themes")

    chart = ChartBuilder.from_notable("Carl Sagan").with_aspects().calculate()

    themes = ["viridis", "plasma", "inferno", "magma", "cividis", "turbo"]

    for theme in themes:
        output = OUTPUT_DIR / f"05_theme_{theme}.svg"
        chart.draw(str(output)).with_theme(theme).save()
        print(f"Created: {output}")


# =============================================================================
# PART 3: ZODIAC PALETTES
# =============================================================================


def example_6_zodiac_palettes():
    """
    Example 6: Zodiac Ring Palettes

    Control the colors of the zodiac signs in the outer ring.
    """
    section_header("Example 6: Zodiac Palettes")

    chart = ChartBuilder.from_notable("Leonardo da Vinci").with_aspects().calculate()

    palettes = [
        "grey",  # Monochrome
        "rainbow",  # Classic rainbow
        "elemental",  # Fire/Earth/Air/Water
        "cardinality",  # Cardinal/Fixed/Mutable
    ]

    for palette in palettes:
        output = OUTPUT_DIR / f"06_palette_{palette}.svg"
        chart.draw(str(output)).with_zodiac_palette(palette).save()
        print(f"Created: {output}")


def example_7_theme_matched_palettes():
    """
    Example 7: Theme-Matched Zodiac Palettes

    Each theme has a matching rainbow palette variant.
    """
    section_header("Example 7: Theme-Matched Palettes")

    chart = ChartBuilder.from_notable("Mozart").with_aspects().calculate()

    combos = [
        ("dark", "rainbow_dark"),
        ("midnight", "rainbow_midnight"),
        ("celestial", "rainbow_celestial"),
        ("neon", "rainbow_neon"),
        ("sepia", "rainbow_sepia"),
    ]

    for theme, palette in combos:
        output = OUTPUT_DIR / f"07_{theme}_{palette}.svg"
        chart.draw(str(output)).with_theme(theme).with_zodiac_palette(palette).save()
        print(f"Created: {output}")


# =============================================================================
# PART 4: INFO CORNERS
# =============================================================================


def example_8_chart_info():
    """
    Example 8: Chart Info Corner

    Display birth data in a corner of the chart.
    """
    section_header("Example 8: Chart Info")

    chart = (
        ChartBuilder.from_notable("Queen of the United Kingdom Victoria")
        .with_aspects()
        .calculate()
    )

    positions = ["top-left", "top-right", "bottom-left", "bottom-right"]

    for pos in positions:
        output = OUTPUT_DIR / f"08_info_{pos.replace('-', '_')}.svg"
        chart.draw(str(output)).with_chart_info(position=pos).save()
        print(f"Created: {output}")


def example_9_moon_phase():
    """
    Example 9: Moon Phase Display

    Show the moon phase at the time of the chart.
    """
    section_header("Example 9: Moon Phase")

    chart = (
        ChartBuilder.from_notable("Princess of Wales Diana").with_aspects().calculate()
    )

    # Moon phase with label
    with_label = OUTPUT_DIR / "09_moon_labeled.svg"
    chart.draw(str(with_label)).with_moon_phase(
        position="bottom-left", show_label=True
    ).save()
    print(f"Created: {with_label}")

    # Moon phase without label
    no_label = OUTPUT_DIR / "09_moon_no_label.svg"
    chart.draw(str(no_label)).with_moon_phase(
        position="bottom-right", show_label=False
    ).save()
    print(f"Created: {no_label}")


def example_10_multiple_corners():
    """
    Example 10: Multiple Info Corners

    Combine chart info, moon phase, aspect counts, etc.
    """
    section_header("Example 10: Multiple Corners")

    chart = ChartBuilder.from_notable("Marilyn Monroe").with_aspects().calculate()

    output = OUTPUT_DIR / "10_all_corners.svg"

    (
        chart.draw(str(output))
        .with_theme("celestial")
        .with_chart_info(position="top-left")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_aspect_counts(position="top-right")
        .with_element_modality_table(position="bottom-right")
        .save()
    )

    print(f"Created: {output}")


# =============================================================================
# PART 5: MULTIPLE HOUSE SYSTEMS
# =============================================================================


def example_11_multi_house():
    """
    Example 11: Multiple House Systems

    Display more than one house system on the same chart.
    """
    section_header("Example 11: Multiple House Systems")

    chart = (
        ChartBuilder.from_notable("Carl Jung")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "11_multi_house.svg"

    # Show all house systems
    chart.draw(str(output)).with_house_systems("all").save()

    print(f"Created: {output}")
    print("Primary system shown solid, secondary shown dashed.")


def example_12_three_house_systems():
    """
    Example 12: Three House Systems

    You can show even more house systems.
    """
    section_header("Example 12: Three House Systems")

    chart = (
        ChartBuilder.from_notable("Sigmund Freud")
        .with_house_systems([PlacidusHouses(), WholeSignHouses(), KochHouses()])
        .with_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "12_three_houses.svg"
    chart.draw(str(output)).with_house_systems("all").with_theme("midnight").save()

    print(f"Created: {output}")


# =============================================================================
# PART 6: TABLES (EXTENDED CHARTS)
# =============================================================================


def example_13_tables_right():
    """
    Example 13: Tables on the Right

    Add position and aspectarian tables to the right of the wheel.
    """
    section_header("Example 13: Tables (Right)")

    chart = ChartBuilder.from_notable("Vincent van Gogh").with_aspects().calculate()

    output = OUTPUT_DIR / "13_tables_right.svg"
    chart.draw(str(output)).with_tables("right").save()

    print(f"Created: {output}")


def example_14_tables_left():
    """
    Example 14: Tables on the Left

    Tables can also go on the left side.
    """
    section_header("Example 14: Tables (Left)")

    chart = ChartBuilder.from_notable("Claude Monet").with_aspects().calculate()

    output = OUTPUT_DIR / "14_tables_left.svg"
    chart.draw(str(output)).with_tables("left").with_theme("sepia").save()

    print(f"Created: {output}")


def example_15_tables_below():
    """
    Example 15: Tables Below

    Position tables below the chart wheel.
    """
    section_header("Example 15: Tables (Below)")

    chart = ChartBuilder.from_notable("Pablo Picasso").with_aspects().calculate()

    output = OUTPUT_DIR / "15_tables_below.svg"
    chart.draw(str(output)).with_tables("below").save()

    print(f"Created: {output}")


def example_16_selective_tables():
    """
    Example 16: Selective Tables

    Choose which tables to display.
    """
    section_header("Example 16: Selective Tables")

    chart = ChartBuilder.from_notable("Georgia O'Keeffe").with_aspects().calculate()

    # Only positions, no aspectarian
    pos_only = OUTPUT_DIR / "16_positions_only.svg"
    chart.draw(str(pos_only)).with_tables(show_aspectarian=False).save()
    print(f"Created: {pos_only}")

    # Only aspectarian, no positions
    asp_only = OUTPUT_DIR / "16_aspectarian_only.svg"
    chart.draw(str(asp_only)).with_tables(show_position_table=False).save()
    print(f"Created: {asp_only}")


def example_17_detailed_aspectarian():
    """
    Example 17: Detailed Aspectarian

    Show orbs and applying/separating in the aspectarian grid.
    """
    section_header("Example 17: Detailed Aspectarian")

    chart = ChartBuilder.from_notable("Salvador Dali").with_aspects().calculate()

    output = OUTPUT_DIR / "17_detailed_aspectarian.svg"
    chart.draw(str(output)).with_tables(aspectarian_detailed=True).with_theme(
        "midnight"
    ).save()

    print(f"Created: {output}")


# =============================================================================
# PART 7: HEADERS
# =============================================================================


def example_18_with_header():
    """
    Example 18: Header with Name

    Add a header section with the chart name.
    """
    section_header("Example 18: Header")

    chart = ChartBuilder.from_notable("Abraham Lincoln").with_aspects().calculate()

    output = OUTPUT_DIR / "18_with_header.svg"
    chart.draw(str(output)).with_header().with_theme("classic").save()

    print(f"Created: {output}")


# =============================================================================
# PART 8: FULL FEATURED EXAMPLES
# =============================================================================


def example_19_professional_natal():
    """
    Example 19: Professional Natal Chart

    A publication-ready natal chart with all features.
    """
    section_header("Example 19: Professional Natal Chart")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "19_professional.svg"

    (
        chart.draw(str(output))
        .with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .with_header()
        .with_chart_info(position="top-left")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_aspect_counts(position="top-right")
        .with_house_systems("all")
        .with_tables(aspectarian_detailed=True)
        .save()
    )

    print(f"Created: {output}")


def example_20_dark_professional():
    """
    Example 20: Dark Professional Chart

    A professional chart with dark theme.
    """
    section_header("Example 20: Dark Professional Chart")

    chart = (
        ChartBuilder.from_notable("Oprah Winfrey")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )

    output = OUTPUT_DIR / "20_dark_professional.svg"

    (
        chart.draw(str(output))
        .with_theme("midnight")
        .with_zodiac_palette("rainbow_midnight")
        .with_header()
        .with_chart_info(position="top-left")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_house_systems("all")
        .with_tables()
        .save()
    )

    print(f"Created: {output}")


# =============================================================================
# PART 9: BATCH PROCESSING
# =============================================================================


def example_21_batch_charts():
    """
    Example 21: Batch Chart Generation

    Generate charts for multiple people at once.
    """
    section_header("Example 21: Batch Generation")

    artists = [
        ("Vincent van Gogh", "classic", "elemental"),
        ("Frida Kahlo", "celestial", "rainbow_celestial"),
        ("Pablo Picasso", "midnight", "rainbow_midnight"),
        ("Georgia O'Keeffe", "sepia", "rainbow_sepia"),
        ("Salvador Dali", "neon", "rainbow_neon"),
    ]

    print("Generating charts for famous artists...\n")

    for name, theme, palette in artists:
        chart = ChartBuilder.from_notable(name).with_aspects().calculate()

        filename = name.lower().replace(" ", "_").replace("'", "")
        output = OUTPUT_DIR / f"21_{filename}.svg"

        (
            chart.draw(str(output))
            .with_theme(theme)
            .with_zodiac_palette(palette)
            .with_chart_info(position="top-left")
            .with_moon_phase(position="bottom-left")
            .save()
        )

        print(f"  Created: {output}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run selected examples."""
    print("\n" + "=" * 60)
    print("  STELLIUM CHART VISUALIZATION COOKBOOK")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}\n")

    # Uncomment the examples you want to run:

    # --- Part 1: Basic Charts ---
    example_1_simplest_chart()
    example_2_with_size()
    example_3_presets()

    # --- Part 2: Themes ---
    example_4_themes()
    example_5_scientific_themes()

    # --- Part 3: Zodiac Palettes ---
    example_6_zodiac_palettes()
    example_7_theme_matched_palettes()

    # --- Part 4: Info Corners ---
    example_8_chart_info()
    example_9_moon_phase()
    example_10_multiple_corners()

    # --- Part 5: Multiple House Systems ---
    example_11_multi_house()
    example_12_three_house_systems()

    # --- Part 6: Tables ---
    example_13_tables_right()
    example_14_tables_left()
    example_15_tables_below()
    example_16_selective_tables()
    example_17_detailed_aspectarian()

    # --- Part 7: Headers ---
    example_18_with_header()

    # --- Part 8: Full Featured ---
    example_19_professional_natal()
    example_20_dark_professional()

    # --- Part 9: Batch ---
    example_21_batch_charts()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files are in: {OUTPUT_DIR}")
    print("See docs/VISUALIZATION.md for full documentation.\n")


if __name__ == "__main__":
    main()
