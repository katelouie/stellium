"""
Example: Chart Themes

This example demonstrates the different visual themes available for
chart rendering.

Each theme provides a cohesive visual style including:
- Background and border colors
- Zodiac ring styling
- House, angle, and planet colors
- Aspect line colors
- Default zodiac palette (can be overridden)
"""

from datetime import datetime

from stellium import ChartBuilder
from stellium.visualization import ChartTheme
from stellium.visualization.themes import get_theme_description

# Create a sample chart (Kate Louie's birth data)
chart = ChartBuilder.from_native(
    datetime(1994, 1, 6, 11, 47), "Palo Alto, CA"
).calculate()

print("Generating charts with different themes...\n")

# Generate chart for each theme
for theme in ChartTheme:
    filename = f"examples/chart_examples/theme_{theme.value}.svg"
    description = get_theme_description(theme)

    # Draw chart with theme (uses theme's default zodiac palette)
    chart.draw(filename).with_theme(theme.value).save()

    print(f"✓ {description}")
    print(f"  → {filename}\n")

print("\nAll theme charts generated successfully!")

# ============================================================================
# Advanced: Theme-Coordinated Palette Combinations
# ============================================================================

print("\n" + "=" * 70)
print("Advanced Examples: Theme-Coordinated Palettes")
print("=" * 70 + "\n")

print("Each theme now has coordinated palette variants that harmonize")
print("with its color story:\n")

# Dark theme with coordinated palettes
(
    chart.draw("examples/chart_examples/dark_rainbow_dark.svg")
    .with_theme("dark")
    .with_zodiac_palette("rainbow_dark")
    .save()
)
print("✓ Dark theme + Rainbow Dark palette → dark_rainbow_dark.svg")

(
    chart.draw("examples/chart_examples/dark_elemental_dark.svg")
    .with_theme("dark")
    .with_zodiac_palette("elemental_dark")
    .save()
)
print("✓ Dark theme + Elemental Dark palette → dark_elemental_dark.svg")

# Midnight theme with coordinated palettes
(
    chart.draw("examples/chart_examples/midnight_rainbow_midnight.svg")
    .with_theme("midnight")
    .with_zodiac_palette("rainbow_midnight")
    .save()
)
print("✓ Midnight theme + Rainbow Midnight palette → midnight_rainbow_midnight.svg")

(
    chart.draw("examples/chart_examples/midnight_elemental_midnight.svg")
    .with_theme("midnight")
    .with_zodiac_palette("elemental_midnight")
    .save()
)
print("✓ Midnight theme + Elemental Midnight palette → midnight_elemental_midnight.svg")

# Neon theme with coordinated palettes
(
    chart.draw("examples/chart_examples/neon_rainbow_neon.svg")
    .with_theme("neon")
    .with_zodiac_palette("rainbow_neon")
    .save()
)
print("✓ Neon theme + Rainbow Neon palette → neon_rainbow_neon.svg")

(
    chart.draw("examples/chart_examples/neon_elemental_neon.svg")
    .with_theme("neon")
    .with_zodiac_palette("elemental_neon")
    .save()
)
print("✓ Neon theme + Elemental Neon palette → neon_elemental_neon.svg")

# Sepia theme with coordinated palettes
(
    chart.draw("examples/chart_examples/sepia_rainbow_sepia.svg")
    .with_theme("sepia")
    .with_zodiac_palette("rainbow_sepia")
    .save()
)
print("✓ Sepia theme + Rainbow Sepia palette → sepia_rainbow_sepia.svg")

(
    chart.draw("examples/chart_examples/sepia_elemental_sepia.svg")
    .with_theme("sepia")
    .with_zodiac_palette("elemental_sepia")
    .save()
)
print("✓ Sepia theme + Elemental Sepia palette → sepia_elemental_sepia.svg")

# Celestial theme with coordinated palette
(
    chart.draw("examples/chart_examples/celestial_rainbow_celestial.svg")
    .with_theme("celestial")
    .with_zodiac_palette("rainbow_celestial")
    .save()
)
print("✓ Celestial theme + Rainbow Celestial palette → celestial_rainbow_celestial.svg")

print("\n" + "=" * 70)
print("Mix & Match: Custom Combinations")
print("=" * 70 + "\n")

# You can also mix and match any theme with any palette
(
    chart.draw("examples/chart_examples/dark_rainbow_base.svg")
    .with_theme("dark")
    .with_zodiac_palette("rainbow")
    .save()
)
print("✓ Dark theme + Base Rainbow palette → dark_rainbow_base.svg")

(
    chart.draw("examples/chart_examples/midnight_elemental_base.svg")
    .with_theme("midnight")
    .with_zodiac_palette("elemental")
    .save()
)
print("✓ Midnight theme + Base Elemental palette → midnight_elemental_base.svg")

# Example with custom style overrides
draw_chart(
    chart,
    filename="examples/chart_examples/custom_styled.svg",
    theme="celestial",
    zodiac_palette="rainbow_celestial",
    style_config={
        "planets": {
            "glyph_color": "#FFFFFF",  # Override planet color to pure white
            "glyph_size": "36px",  # Make planets larger
        }
    },
)
print("✓ Celestial + Rainbow Celestial + Custom styles → custom_styled.svg")

print("\nDone! Check examples/chart_examples/ for all generated charts.")

# ============================================================================
# Theme Reference Guide
# ============================================================================

print("\n" + "=" * 70)
print("Theme Reference")
print("=" * 70 + "\n")

print("CLASSIC - Professional grey/neutral (default)")
print("  • Best for: Professional reports, printing")
print("  • Default palette: Grey")
print()

print("DARK - Dark grey background with light text")
print("  • Best for: Dark mode UIs, screens")
print("  • Default palette: Grey")
print()

print("MIDNIGHT - Elegant night sky with deep navy and white/gold")
print("  • Best for: Beautiful presentations, romantic aesthetic")
print("  • Default palette: Grey (light colors)")
print()

print("NEON - Cyberpunk aesthetic with bright neon colors")
print("  • Best for: Fun, modern, attention-grabbing")
print("  • Default palette: Rainbow (neon version)")
print()

print("SEPIA - Vintage aged paper with warm browns")
print("  • Best for: Historical charts, classical feel")
print("  • Default palette: Grey (brown tones)")
print()

print("PASTEL - Soft gentle colors, light and airy")
print("  • Best for: Gentle aesthetic, wellness contexts")
print("  • Default palette: Rainbow (pastel version)")
print()

print("CELESTIAL - Cosmic galaxy with deep purples and gold")
print("  • Best for: Mystical, spiritual contexts")
print("  • Default palette: Grey (purple/gold tones)")
