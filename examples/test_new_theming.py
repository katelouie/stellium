"""
Test script for new theming features.

Tests:
1. Data science themes (viridis, plasma, inferno, magma, cividis, turbo)
2. Mix-and-match palettes
3. Adaptive sign info coloring
4. Planet glyph palettes
"""

from datetime import datetime

from stellium import ChartBuilder
from stellium.core.native import Native
from stellium.visualization.layers import AspectLayer, PlanetLayer, ZodiacLayer


def test_data_science_themes():
    """Test all data science chart themes."""
    print("Testing data science themes...")

    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    themes = ["viridis", "plasma", "inferno", "magma", "cividis", "turbo"]

    for theme in themes:
        print(f"  - Generating chart with {theme} theme...")
        output_file = f"examples/chart_examples/test_{theme}_theme.svg"
        chart.draw(output_file).with_theme(theme).save()

    print("  ✓ All data science themes generated successfully!")


def test_mix_and_match_palettes():
    """Test mix-and-match palette combinations."""
    print("\nTesting mix-and-match palettes...")

    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    # Test: Classic theme with rainbow zodiac and viridis aspects
    print("  - Classic theme + rainbow zodiac + viridis aspects...")
    (
        chart.draw("examples/chart_examples/test_mix_classic_rainbow_viridis.svg")
        .with_theme("classic")
        .with_zodiac_palette("rainbow")
        .with_aspect_palette("viridis")
        .save()
    )

    # Test: Dark theme with elemental zodiac and plasma aspects
    print("  - Dark theme + elemental zodiac + plasma aspects...")
    (
        chart.draw("examples/chart_examples/test_mix_dark_elemental_plasma.svg")
        .with_theme("dark")
        .with_zodiac_palette("elemental")
        .with_aspect_palette("plasma")
        .save()
    )

    # Test: Midnight theme with viridis zodiac and blues aspects
    print("  - Midnight theme + viridis zodiac + blues aspects...")
    (
        chart.draw("examples/chart_examples/test_mix_midnight_viridis_blues.svg")
        .with_theme("midnight")
        .with_zodiac_palette("viridis")
        .with_aspect_palette("blues")
        .save()
    )

    print("  ✓ Mix-and-match palettes tested successfully!")


def test_planet_glyph_palettes():
    """Test planet glyph coloring palettes."""
    print("\nTesting planet glyph palettes...")

    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    palettes = ["element", "sign_ruler", "planet_type", "chakra", "rainbow"]

    for palette in palettes:
        print(f"  - Generating chart with {palette} planet palette...")
        (
            chart.draw(f"examples/chart_examples/test_planet_{palette}.svg")
            .with_theme("dark")
            .with_planet_glyph_palette(palette)
            .save()
        )

    print("  ✓ Planet glyph palettes tested successfully!")


def test_adaptive_sign_coloring():
    """Test adaptive sign info coloring."""
    print("\nTesting adaptive sign info coloring...")

    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    # Test with viridis theme and adaptive coloring enabled
    print("  - Viridis theme with adaptive sign coloring...")
    (
        chart.draw("examples/chart_examples/test_adaptive_sign_coloring.svg")
        .with_theme("viridis")
        .with_adaptive_colors(sign_info=True)
        .save()
    )

    print("  ✓ Adaptive sign coloring tested successfully!")


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING NEW THEMING FEATURES")
    print("=" * 60)

    test_data_science_themes()
    test_mix_and_match_palettes()
    test_planet_glyph_palettes()
    test_adaptive_sign_coloring()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nGenerated charts can be found in: examples/chart_examples/")


if __name__ == "__main__":
    main()
