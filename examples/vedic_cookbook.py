"""
Vedic Chart Cookbook
====================

This cookbook demonstrates Stellium's Vedic chart rendering system,
featuring both North Indian (diamond) and South Indian (grid) styles.

Key features:
- Two traditional Vedic chart formats
- Three color themes: classic, dark, traditional
- Four label styles: abbreviation, glyph, full, number
- Degree + minutes display
- Automatic sidereal conversion with configurable ayanamsa
- Full native info display (name, date/time, location)

Run this script to generate example charts:

    source ~/.zshrc && pyenv activate starlight
    python examples/vedic_cookbook.py
"""

from pathlib import Path

from stellium import ChartBuilder
from stellium.visualization.vedic import NorthIndianRenderer, SouthIndianRenderer

# Output directory
OUTPUT_DIR = Path(__file__).parent / "vedic_charts"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# Example 1: Basic South Indian Chart
# =============================================================================


def example_1_south_indian_basic():
    """
    Basic South Indian chart with abbreviation labels.

    The South Indian chart is a 4×4 grid where signs are FIXED
    (Aries is always in the same cell). Planets are placed by sign.
    House numbers indicate which house each sign represents for this
    particular ascendant.
    """
    print("\n=== Example 1: South Indian Basic ===\n")

    # Use sidereal zodiac for Vedic charts
    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    renderer = SouthIndianRenderer(
        size=500,
        theme="classic",
        show_degrees=True,
        label_style="abbreviation",
    )
    renderer.render_to_file(chart, str(OUTPUT_DIR / "south_indian_basic.svg"))
    print(f"Saved: {OUTPUT_DIR / 'south_indian_basic.svg'}")


# =============================================================================
# Example 2: Basic North Indian Chart
# =============================================================================


def example_2_north_indian_basic():
    """
    Basic North Indian chart with traditional number labels.

    The North Indian chart is a square with inner diamond and X diagonals,
    creating 12 triangular houses. Houses are FIXED (house 1 is always
    the top diamond). Signs rotate based on the ascendant.

    Traditional North Indian charts use sign numbers (1=Aries, 2=Taurus, etc.)
    instead of sign names — the "number" label style.
    """
    print("\n=== Example 2: North Indian Basic ===\n")

    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    renderer = NorthIndianRenderer(
        size=500,
        theme="classic",
        show_degrees=True,
        label_style="number",
    )
    renderer.render_to_file(chart, str(OUTPUT_DIR / "north_indian_basic.svg"))
    print(f"Saved: {OUTPUT_DIR / 'north_indian_basic.svg'}")


# =============================================================================
# Example 3: Theme Comparison
# =============================================================================


def example_3_themes():
    """
    Generate the same chart in all three themes.

    - classic: White background, clean modern look
    - dark: Dark navy background, for dark-mode UIs
    - traditional: Saffron/parchment, temple-inspired aesthetic
    """
    print("\n=== Example 3: Theme Comparison ===\n")

    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    for theme in ["classic", "dark", "traditional"]:
        for style_name, Renderer in [
            ("south", SouthIndianRenderer),
            ("north", NorthIndianRenderer),
        ]:
            r = Renderer(size=500, theme=theme, show_degrees=True)
            filename = f"{style_name}_indian_{theme}.svg"
            r.render_to_file(chart, str(OUTPUT_DIR / filename))
            print(f"Saved: {filename}")


# =============================================================================
# Example 4: Label Styles
# =============================================================================


def example_4_label_styles():
    """
    Compare all four label styles.

    - "abbreviation": Ari, Tau, Su, Mo — traditional Vedic shorthand
    - "number": 1, 2, 3 — traditional North Indian sign numbers
    - "glyph": ♈, ♉, ☉, ☽ — Unicode symbols (Western-familiar)
    - "full": Aries, Taurus, Sun, Moon — spelled out for beginners
    """
    print("\n=== Example 4: Label Styles ===\n")

    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    for style in ["abbreviation", "number", "glyph", "full"]:
        r = NorthIndianRenderer(
            size=500,
            theme="classic",
            show_degrees=True,
            label_style=style,
        )
        filename = f"north_indian_labels_{style}.svg"
        r.render_to_file(chart, str(OUTPUT_DIR / filename))
        print(f"Saved: {filename}")


# =============================================================================
# Example 5: Custom Chart (Your Own Birth Data)
# =============================================================================


def example_5_custom_chart():
    """
    Generate a Vedic chart from custom birth data.

    Stellium handles geocoding and timezone automatically.
    Use .with_sidereal() to set the ayanamsa — "lahiri" is the
    most common for Vedic/Jyotish astrology.
    """
    print("\n=== Example 5: Custom Chart ===\n")

    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .with_sidereal("lahiri")
        .calculate()
    )

    NorthIndianRenderer(
        size=500,
        theme="traditional",
        show_degrees=True,
        label_style="abbreviation",
    ).render_to_file(chart, str(OUTPUT_DIR / "custom_north.svg"))

    SouthIndianRenderer(
        size=500,
        theme="traditional",
        show_degrees=True,
        label_style="abbreviation",
    ).render_to_file(chart, str(OUTPUT_DIR / "custom_south.svg"))

    print("Saved: custom_north.svg, custom_south.svg")


# =============================================================================
# Example 6: Different Ayanamsas
# =============================================================================


def example_6_ayanamsas():
    """
    Compare charts using different ayanamsa systems.

    Different ayanamsas produce slightly different sign placements.
    The most common are:
    - lahiri: Official Indian government standard
    - raman: B.V. Raman's system
    - krishnamurti: K.S. Krishnamurti's system
    """
    print("\n=== Example 6: Ayanamsa Comparison ===\n")

    for ayanamsa in ["lahiri", "raman", "krishnamurti"]:
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_sidereal(ayanamsa)
            .calculate()
        )

        sun = chart.get_object("Sun")
        print(f"  {ayanamsa}: Sun at {sun.longitude:.2f}° ({sun.sign})")

        NorthIndianRenderer(
            size=400,
            theme="classic",
            show_degrees=True,
            label_style="number",
        ).render_to_file(chart, str(OUTPUT_DIR / f"north_{ayanamsa}.svg"))

    print(f"  Saved 3 charts to {OUTPUT_DIR}")


# =============================================================================
# Example 7: Convenience Method (draw_vedic)
# =============================================================================


def example_7_convenience_method():
    """
    The easiest way to generate Vedic charts — one line!

    chart.draw_vedic() is a convenience method on CalculatedChart that
    handles renderer creation internally. It returns self for chaining,
    so you can generate multiple styles in one expression.
    """
    print("\n=== Example 7: Convenience Method ===\n")

    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    # One-liner: just specify filename and style
    chart.draw_vedic(str(OUTPUT_DIR / "quick_north.svg"), style="north_indian")
    chart.draw_vedic(str(OUTPUT_DIR / "quick_south.svg"), style="south_indian")
    print("Saved: quick_north.svg, quick_south.svg")

    # With customization
    chart.draw_vedic(
        str(OUTPUT_DIR / "quick_traditional.svg"),
        style="north_indian",
        theme="traditional",
        label_style="number",
        show_degrees=True,
    )
    print("Saved: quick_traditional.svg")

    # Chaining — generate both styles in one expression
    (
        chart.draw_vedic(
            str(OUTPUT_DIR / "chained_north.svg"), style="north_indian"
        ).draw_vedic(str(OUTPUT_DIR / "chained_south.svg"), style="south_indian")
    )
    print("Saved: chained_north.svg, chained_south.svg (via chaining)")

    # Mix with Western chart output
    chart.draw("western.svg").preset_standard().save()
    chart.draw_vedic(str(OUTPUT_DIR / "vedic.svg"), style="north_indian")
    print("Saved: western.svg + vedic.svg — same chart, two traditions!")


# =============================================================================
# Example 8: Generate README Images
# =============================================================================


def generate_readme_images():
    """Generate Vedic chart images for the README."""
    chart = (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )

    images_dir = Path(__file__).parent.parent / "images"

    NorthIndianRenderer(
        theme="classic",
        show_degrees=True,
        label_style="number",
    ).render_to_file(chart, str(images_dir / "vedic_north_indian_classic.svg"))

    SouthIndianRenderer(
        theme="classic",
        show_degrees=True,
        label_style="abbreviation",
    ).render_to_file(chart, str(images_dir / "vedic_south_indian_classic.svg"))

    print(f"README images saved to {images_dir}")


# =============================================================================
# Run all examples
# =============================================================================

if __name__ == "__main__":
    example_1_south_indian_basic()
    example_2_north_indian_basic()
    example_3_themes()
    example_4_label_styles()
    example_5_custom_chart()
    example_6_ayanamsas()
    example_7_convenience_method()
    generate_readme_images()
    print("\n✅ All Vedic chart examples complete!")
