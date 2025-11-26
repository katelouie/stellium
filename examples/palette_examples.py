"""
Example: Zodiac Color Palettes

This example demonstrates the different color palettes available for
the zodiac wheel visualization.
"""

from datetime import datetime

from stellium import ChartBuilder, Native
from stellium.visualization import ZodiacPalette

# Create a sample chart
native = Native(datetime(1994, 1, 6, 11, 47), "Seattle, WA")
chart = ChartBuilder.from_native(native).calculate()

# Generate charts with each palette
palettes = [
    (ZodiacPalette.GREY, "Grey (classic)"),
    (ZodiacPalette.RAINBOW, "Rainbow"),
    (ZodiacPalette.ELEMENTAL, "Elemental"),
    (ZodiacPalette.CARDINALITY, "Cardinality"),
]

print("Generating charts with different zodiac palettes...\n")

for palette, description in palettes:
    filename = f"examples/chart_examples/palette_{palette.value}.svg"
    chart.draw(filename).with_zodiac_palette(palette.value).save()
    print(f"✓ {description:20s} → {filename}")

print("\nAll charts generated successfully!")
print("\nPalette descriptions:")
print("  • Grey:        Classic monochrome grey wheel")
print("  • Rainbow:     Soft 12-color spectrum (Aries=red → Pisces=magenta)")
print("  • Elemental:   4 colors by element (Fire, Earth, Air, Water)")
print("  • Cardinality: 3 colors by modality (Cardinal, Fixed, Mutable)")
