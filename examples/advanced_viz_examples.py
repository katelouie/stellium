"""
Advanced Visualization Examples for Stellium

Demonstrates new visualization features including:
- Adaptive zodiac glyph coloring
- Theme and palette comparison grids
- HTML color reference sheets
- Multiple palettes and themes

Run this script to generate example charts:
    source ~/.zshrc && pyenv activate stellium && python examples/advanced_viz_examples.py
"""

from stellium import ChartBuilder
from stellium.visualization import (
    AspectPalette,
    ChartTheme,
    PlanetGlyphPalette,
    ZodiacPalette,
    draw_chart,
    draw_chart_grid,
    draw_palette_comparison,
    draw_theme_comparison,
    generate_html_reference,
)

# Create a sample chart
print("Creating sample chart...")
chart = ChartBuilder.from_notable("Albert Einstein").calculate()


def example_1_adaptive_zodiac_glyphs():
    """Example 1: Adaptive zodiac glyph coloring with bright palettes."""
    print("\n=== Example 1: Adaptive Zodiac Glyph Coloring ===")

    # Without adaptive coloring - glyphs may blend into bright backgrounds
    print("  - Drawing Viridis palette WITHOUT adaptive glyph colors...")
    draw_chart(
        chart,
        filename="examples/chart_examples/viridis_no_adaptive.svg",
        theme=ChartTheme.VIRIDIS,
        zodiac_palette=ZodiacPalette.VIRIDIS,
        color_zodiac_glyphs=False,  # Default
    )

    # With adaptive coloring - glyphs automatically adjust for contrast
    print("  - Drawing Viridis palette WITH adaptive glyph colors...")
    draw_chart(
        chart,
        filename="examples/chart_examples/viridis_adaptive.svg",
        theme=ChartTheme.VIRIDIS,
        zodiac_palette=ZodiacPalette.VIRIDIS,
        color_zodiac_glyphs=True,  # Enable adaptive coloring
    )

    # Compare multiple bright palettes with adaptive coloring
    print("  - Drawing Plasma palette with adaptive coloring...")
    draw_chart(
        chart,
        filename="examples/chart_examples/plasma_adaptive.svg",
        theme=ChartTheme.PLASMA,
        zodiac_palette=ZodiacPalette.PLASMA,
        color_zodiac_glyphs=True,
    )

    print("  - Drawing Inferno palette with adaptive coloring...")
    draw_chart(
        chart,
        filename="examples/chart_examples/inferno_adaptive.svg",
        theme=ChartTheme.INFERNO,
        zodiac_palette=ZodiacPalette.INFERNO,
        color_zodiac_glyphs=True,
    )


def example_2_theme_grid():
    """Example 2: Grid comparison of all themes."""
    print("\n=== Example 2: Theme Comparison Grid ===")
    print("  - Creating grid of all themes...")

    draw_theme_comparison(
        chart,
        filename="examples/chart_examples/all_themes_grid.svg",
        chart_size=250,
    )
    print("  - Saved to examples/chart_examples/all_themes_grid.svg")


def example_3_palette_grid():
    """Example 3: Grid comparison of zodiac palettes."""
    print("\n=== Example 3: Zodiac Palette Comparison Grid ===")
    print("  - Creating grid of popular palettes...")

    draw_palette_comparison(
        chart,
        filename="examples/chart_examples/palettes_grid.svg",
        theme=ChartTheme.DARK,  # Dark theme works well with colorful palettes
        chart_size=250,
        color_zodiac_glyphs=True,  # Enable adaptive coloring
    )
    print("  - Saved to examples/chart_examples/palettes_grid.svg")


def example_4_custom_grid():
    """Example 4: Custom grid with mixed configurations."""
    print("\n=== Example 4: Custom Mixed Grid ===")
    print("  - Creating custom grid with different themes and palettes...")

    draw_chart_grid(
        charts=[chart] * 6,
        filename="examples/chart_examples/custom_grid.svg",
        labels=[
            "Classic + Rainbow",
            "Dark + Elemental",
            "Midnight + Celestial",
            "Neon + Viridis",
            "Sepia + Cardinality",
            "Plasma + Plasma",
        ],
        themes=[
            ChartTheme.CLASSIC,
            ChartTheme.DARK,
            ChartTheme.MIDNIGHT,
            ChartTheme.NEON,
            ChartTheme.SEPIA,
            ChartTheme.PLASMA,
        ],
        zodiac_palettes=[
            ZodiacPalette.RAINBOW,
            ZodiacPalette.ELEMENTAL,
            ZodiacPalette.RAINBOW_CELESTIAL,
            ZodiacPalette.VIRIDIS,
            ZodiacPalette.CARDINALITY,
            ZodiacPalette.PLASMA,
        ],
        rows=2,
        cols=3,
        chart_size=300,
        color_zodiac_glyphs=True,
    )
    print("  - Saved to examples/chart_examples/custom_grid.svg")


def example_5_html_reference():
    """Example 5: Generate HTML color reference sheets."""
    print("\n=== Example 5: HTML Color Reference Sheets ===")

    # Generate comprehensive reference
    print("  - Generating complete color reference...")
    generate_html_reference(
        filename="examples/chart_examples/stellium_colors.html",
    )
    print("  - Saved to examples/chart_examples/stellium_colors.html")

    # You can also generate separate references:
    # from stellium.visualization import (
    #     generate_zodiac_palette_reference,
    #     generate_aspect_palette_reference,
    #     generate_theme_reference,
    # )
    #
    # generate_zodiac_palette_reference("zodiac_only.html")
    # generate_aspect_palette_reference("aspects_only.html")
    # generate_theme_reference("themes_only.html")


def example_6_all_palettes():
    """Example 6: Showcase of coordinated theme palettes."""
    print("\n=== Example 6: Coordinated Theme Palettes ===")

    # Dark theme with coordinated palettes
    print("  - Dark theme with rainbow_dark palette...")
    draw_chart(
        chart,
        filename="examples/chart_examples/dark_rainbow.svg",
        theme=ChartTheme.DARK,
        zodiac_palette=ZodiacPalette.RAINBOW_DARK,
        aspect_palette=AspectPalette.DARK,
        planet_glyph_palette=PlanetGlyphPalette.DEFAULT,
        color_sign_info=True,
        color_zodiac_glyphs=True,
    )

    # Midnight theme with coordinated palettes
    print("  - Midnight theme with rainbow_midnight palette...")
    draw_chart(
        chart,
        filename="examples/chart_examples/midnight_rainbow.svg",
        theme=ChartTheme.MIDNIGHT,
        zodiac_palette=ZodiacPalette.RAINBOW_MIDNIGHT,
        aspect_palette=AspectPalette.MIDNIGHT,
        color_sign_info=True,
        color_zodiac_glyphs=True,
    )

    # Neon theme with neon palettes
    print("  - Neon theme with rainbow_neon palette...")
    draw_chart(
        chart,
        filename="examples/chart_examples/neon_rainbow.svg",
        theme=ChartTheme.NEON,
        zodiac_palette=ZodiacPalette.RAINBOW_NEON,
        aspect_palette=AspectPalette.NEON,
        planet_glyph_palette=PlanetGlyphPalette.RAINBOW,
        color_sign_info=True,
        color_zodiac_glyphs=True,
    )

    # Celestial theme
    print("  - Celestial theme with celestial palette...")
    draw_chart(
        chart,
        filename="examples/chart_examples/celestial_rainbow.svg",
        theme=ChartTheme.CELESTIAL,
        zodiac_palette=ZodiacPalette.RAINBOW_CELESTIAL,
        aspect_palette=AspectPalette.CELESTIAL,
        color_sign_info=True,
        color_zodiac_glyphs=True,
    )


def example_7_data_science_palettes():
    """Example 7: Data science colormap palettes."""
    print("\n=== Example 7: Data Science Colormaps ===")

    palettes = [
        ("Viridis", ZodiacPalette.VIRIDIS, ChartTheme.VIRIDIS),
        ("Plasma", ZodiacPalette.PLASMA, ChartTheme.PLASMA),
        ("Inferno", ZodiacPalette.INFERNO, ChartTheme.INFERNO),
        ("Magma", ZodiacPalette.MAGMA, ChartTheme.MAGMA),
        ("Cividis", ZodiacPalette.CIVIDIS, ChartTheme.CIVIDIS),
        ("Turbo", ZodiacPalette.TURBO, ChartTheme.TURBO),
    ]

    for name, palette, theme in palettes:
        print(f"  - Drawing {name} palette...")
        draw_chart(
            chart,
            filename=f"examples/chart_examples/{name.lower()}_theme.svg",
            theme=theme,
            zodiac_palette=palette,
            color_zodiac_glyphs=True,  # Essential for these bright palettes
            color_sign_info=True,
        )


def example_8_planet_glyph_palettes():
    """Example 8: Planet glyph palette variations."""
    print("\n=== Example 8: Planet Glyph Palettes ===")

    glyph_palettes = [
        ("Element", PlanetGlyphPalette.ELEMENT),
        ("Sign Ruler", PlanetGlyphPalette.SIGN_RULER),
        ("Planet Type", PlanetGlyphPalette.PLANET_TYPE),
        ("Chakra", PlanetGlyphPalette.CHAKRA),
        ("Rainbow", PlanetGlyphPalette.RAINBOW),
    ]

    charts_for_grid = [chart] * len(glyph_palettes)
    labels = [name for name, _ in glyph_palettes]
    palettes = [pal for _, pal in glyph_palettes]

    draw_chart_grid(
        charts=charts_for_grid,
        filename="examples/chart_examples/planet_glyph_palettes.svg",
        labels=labels,
        themes=[ChartTheme.DARK] * len(glyph_palettes),
        planet_glyph_palettes=palettes,
        chart_size=250,
        cols=3,
    )
    print("  - Saved to examples/chart_examples/planet_glyph_palettes.svg")


if __name__ == "__main__":
    print("🌟 Stellium Advanced Visualization Examples")
    print("=" * 60)

    # Run all examples
    example_1_adaptive_zodiac_glyphs()
    example_2_theme_grid()
    example_3_palette_grid()
    example_4_custom_grid()
    example_5_html_reference()
    example_6_all_palettes()
    example_7_data_science_palettes()
    example_8_planet_glyph_palettes()

    print("\n" + "=" * 60)
    print("✅ All examples generated successfully!")
    print("\nGenerated files:")
    print("  - Individual charts: examples/chart_examples/*.svg")
    print("  - Color reference: examples/chart_examples/stellium_colors.html")
    print("\nOpen the HTML file in a browser to see all available colors!")
