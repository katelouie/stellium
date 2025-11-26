# Documentation Images

This directory contains SVG chart examples used in Stellium's documentation.

## Directory Structure

- **`gallery/`** - Theme and palette gallery examples
  - Theme showcases (all 13 themes with recommended palettes)
  - Palette showcases (all 24+ palettes)
  - Comparison examples

- **`examples/`** - Additional code examples
  - Advanced customization examples
  - Feature demonstrations
  - Tutorial step-by-step examples

- **Root** - Quick start and main documentation examples
  - README.md examples
  - VISUALIZATION.md quick start examples

## Naming Convention

### Gallery Images

Theme examples:
- `gallery/classic_grey.svg` - Classic theme with Grey palette
- `gallery/midnight_rainbow_midnight.svg` - Midnight theme with Rainbow Midnight palette
- etc.

Palette examples:
- `gallery/zodiac_grey.svg` - Grey zodiac palette (on default theme)
- `gallery/zodiac_viridis.svg` - Viridis zodiac palette
- `gallery/planet_glyphs_element.svg` - Element planet glyph palette
- etc.

### Quick Start Images

- `readme_einstein.svg` - Basic first chart example
- `viz_minimal.svg` - Minimal preset
- `viz_standard.svg` - Standard preset
- `viz_detailed.svg` - Detailed preset
- `viz_midnight.svg` - Midnight theme example
- `viz_celestial.svg` - Celestial theme example
- `viz_neon.svg` - Neon theme example
- `viz_celestial_more.svg` - Full customization example

## Generating Images

All images are generated using Albert Einstein's natal chart for consistency:

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").with_angles().calculate()

# Generate examples
chart.draw("readme_einstein.svg").save()
chart.draw("viz_minimal.svg").preset_minimal().save()
chart.draw("viz_standard.svg").preset_standard().save()
chart.draw("viz_detailed.svg").preset_detailed().save()

# Themes
chart.draw("viz_midnight.svg").with_theme("midnight").save()
chart.draw("viz_celestial.svg").with_theme("celestial").save()
chart.draw("viz_neon.svg").with_theme("neon").save()

# Gallery - Themes
chart.draw("gallery/classic_grey.svg") \
    .with_theme("classic") \
    .with_zodiac_palette("grey") \
    .save()

chart.draw("gallery/midnight_rainbow_midnight.svg") \
    .with_theme("midnight") \
    .with_zodiac_palette("rainbow_midnight") \
    .save()

# Gallery - Palettes
chart.draw("gallery/zodiac_viridis.svg") \
    .with_zodiac_palette("viridis") \
    .save()
```

## Batch Generation Script

See `examples/generate_gallery_images.py` for automated generation of all gallery images.

## Notes

- All images use 600px size (default) unless otherwise specified
- SVG format ensures scalability without quality loss
- File sizes typically 40-60KB per chart
- All images should use Albert Einstein's chart for consistency
