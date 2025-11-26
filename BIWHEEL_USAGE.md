# Bi-Wheel Comparison Chart Usage Guide

This guide demonstrates how to use the new bi-wheel chart drawing functionality for synastry, transits, and progression charts.

## Quick Start

The simplest way to create a bi-wheel comparison chart:

```python
from stellium import ChartBuilder, ComparisonBuilder

# Create two charts
chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
chart2 = ChartBuilder.from_notable("Marie Curie").calculate()

# Create synastry comparison
synastry = ComparisonBuilder.from_native(chart1, "Einstein") \
    .with_partner(chart2, "Curie") \
    .calculate()

# Draw bi-wheel chart with preset
synastry.draw("synastry.svg").preset_synastry().save()
```

## Features

### Bi-Wheel Layout

- **Inner wheel**: chart1 (native/person1) planets at reduced radius
- **Outer wheel**: chart2 (partner/transit/progressed) planets outside zodiac ring
- **House cusps**: Both charts' cusps displayed (inner solid, outer dashed)
- **Cross-chart aspects**: Drawn in central aspect ring
- **Extended canvas**: Position tables and aspectarian with interleaved data

### Visual Distinctions

- Outer wheel planets use theme-specific colors (from `outer_wheel_planet_color`)
- Chart indicators (①②) in position tables and aspectarian
- House cusps: chart1 solid lines, chart2 dashed lines
- Each theme has harmonious color story for inner and outer wheels

## API Methods

### 1. Comparison.draw()

The `Comparison` class has a `.draw()` method that returns a `ChartDrawBuilder`:

```python
synastry.draw("filename.svg")
    .with_theme("midnight")
    .with_tables(position="right")
    .save()
```

### 2. ChartDrawBuilder.with_tables()

Configure extended canvas with position table and aspectarian:

```python
builder.with_tables(
    position="right",              # "right", "left", or "below"
    show_position_table=True,      # Show position table
    show_aspectarian=True,         # Show aspectarian grid
    aspectarian_mode="cross_chart" # "cross_chart", "all", "chart1", "chart2"
)
```

**Table Options:**

| Option | Values | Description |
|--------|--------|-------------|
| `position` | "right", "left", "below" | Where to place extended canvas |
| `show_position_table` | True/False | Display interleaved position table |
| `show_aspectarian` | True/False | Display aspectarian grid |
| `aspectarian_mode` | "cross_chart", "all", "chart1", "chart2" | Which aspects to show |

### 3. preset_synastry()

Auto-configures bi-wheel layout for Comparison objects:

```python
# For Comparison objects, automatically enables:
# - Bi-wheel layout (inner/outer wheels)
# - Extended canvas with tables on right
# - Chart info and aspect counts
# - Moon phase in corner
synastry.draw("synastry.svg").preset_synastry().save()
```

For standard natal charts, `preset_synastry()` works as before.

## Examples

### Example 1: Basic Synastry with Default Settings

```python
synastry = ComparisonBuilder.from_native(chart1, "Person A") \
    .with_partner(chart2, "Person B") \
    .calculate()

# Auto bi-wheel with tables
synastry.draw("basic_synastry.svg").preset_synastry().save()
```

### Example 2: Custom Theme

```python
synastry.draw("celestial_synastry.svg") \
    .with_theme("celestial") \
    .with_tables(position="right") \
    .save()
```

### Example 3: Position Table Only

```python
synastry.draw("positions_only.svg") \
    .with_theme("dark") \
    .with_tables(
        position="right",
        show_aspectarian=False  # Hide aspectarian
    ) \
    .save()
```

### Example 4: Aspectarian Only

```python
synastry.draw("aspects_only.svg") \
    .with_theme("classic") \
    .with_tables(
        position="right",
        show_position_table=False  # Hide position table
    ) \
    .save()
```

### Example 5: Tables on Left

```python
synastry.draw("tables_left.svg") \
    .with_theme("midnight") \
    .with_tables(position="left") \
    .save()
```

### Example 6: Tables Below

```python
synastry.draw("tables_below.svg") \
    .with_theme("pastel") \
    .with_tables(position="below") \
    .save()
```

### Example 7: All Aspect Grids (Experimental)

```python
# Show chart1 internal, chart2 internal, AND cross-chart aspects
synastry.draw("all_aspects.svg") \
    .with_tables(
        position="right",
        aspectarian_mode="all"  # Show all three grids
    ) \
    .save()
```

### Example 8: Custom Configuration

```python
synastry.draw("custom.svg") \
    .with_size(800) \
    .with_theme("neon") \
    .with_tables(position="right") \
    .with_chart_info(position="top-left") \
    .with_aspect_counts(position="top-right") \
    .without_moon_phase() \
    .save()
```

### Example 9: Transits

```python
from datetime import datetime
import datetime as dt

# Natal chart
natal = ChartBuilder.from_notable("Albert Einstein").calculate()

# Current transits
transits = ComparisonBuilder.from_native(natal, "Natal") \
    .with_transit(datetime(2025, 11, 19, 12, 0, tzinfo=dt.UTC)) \
    .calculate()

# Draw transit bi-wheel
transits.draw("transits.svg") \
    .with_theme("dark") \
    .with_tables(position="right") \
    .save()
```

### Example 10: Without Tables

```python
# Bi-wheel chart without extended canvas
synastry.draw("minimal_biwheel.svg") \
    .with_theme("classic") \
    .without_tables() \
    .save()
```

## Direct Function Call

You can also use `draw_comparison_chart()` directly:

```python
from stellium import draw_comparison_chart

draw_comparison_chart(
    synastry,
    filename="synastry.svg",
    size=700,
    theme="midnight",
    extended_canvas="right",
    show_position_table=True,
    show_aspectarian=True,
    aspectarian_mode="cross_chart"
)
```

## Position Table Format

The position table for comparison charts shows interleaved positions from both charts:

```
Planet          Sign        Degree   House
☉ Sun ①        Pisces      16°23'    12
☉ Sun ②        Scorpio     7°52'     5
☽ Moon ①       Sagittarius 14°31'    7
☽ Moon ②       Aquarius    18°08'    9
...
```

- `①` = chart1 (inner wheel)
- `②` = chart2 (outer wheel)

## Aspectarian Format

For comparison charts, the aspectarian shows a rectangular grid:

```
        ☉②  ☽②  ☿②  ♀②  ♂②  ...
☉①      △   □   ☌   ⚹   ☍
☽①      ⚹   ☌   △   □   ⚹
☿①      □   ⚹   ☍   △   ☌
...
```

- Rows: chart1 objects (inner wheel)
- Columns: chart2 objects (outer wheel)
- Shows cross-chart aspects (chart1 ↔ chart2)
- Includes Asc and MC from both charts

## Aspectarian Modes

| Mode | Description |
|------|-------------|
| `"cross_chart"` | Only cross-chart aspects (chart1 ↔ chart2) - Default |
| `"all"` | All three grids: chart1 internal, chart2 internal, cross-chart |
| `"chart1"` | Only chart1 internal aspects |
| `"chart2"` | Only chart2 internal aspects |

Note: Currently only `"cross_chart"` mode is fully implemented.

## Themes

All 13 themes support bi-wheel charts with harmonious outer wheel colors:

- **classic**: Softer blue (#4A90E2)
- **dark**: Cyan (#95E1D3)
- **midnight**: Sky blue (#87CEEB)
- **neon**: Neon green (#39FF14)
- **sepia**: Lighter brown (#8B7355)
- **pastel**: Soft lavender (#B4A7D6)
- **celestial**: Orchid (#DA70D6)
- **viridis**: Purple (#414487)
- **plasma**: Deep magenta (#B12A90)
- **inferno**: Deep red (#A52C60)
- **magma**: Deep purple (#7B2382)
- **cividis**: Blue-grey (#4E6B7C)
- **turbo**: Turquoise (#1AE4B6)

## Backward Compatibility

Standard natal charts continue to work with all builder methods:

```python
# Natal chart with tables
chart.draw("natal.svg").with_tables(position="right").save()

# preset_synastry() on natal charts works as before
chart.draw("natal_synastry.svg").preset_synastry().save()
```

## Testing

Run the comprehensive test suite:

```bash
python3 examples/test_comparison_integration.py
```

This tests:
- Comparison.draw() method
- ChartDrawBuilder.with_tables()
- preset_synastry() auto-configuration
- Various table layouts and options
- Backward compatibility

## Architecture

The implementation follows Stellium's core principles:

- **Protocols**: Extended existing protocols (no breaking changes)
- **Immutability**: All Comparison data is frozen
- **Composability**: Layers work independently
- **Builder pattern**: Fluent API for configuration
- **Type safety**: Full type hints throughout

## Files Modified

- `visualization/builder.py`: Added with_tables(), updated preset_synastry() and save()
- `visualization/drawing.py`: Added draw_comparison_chart()
- `visualization/layers.py`: Added OuterHouseCuspLayer, enhanced PlanetLayer
- `visualization/extended_canvas.py`: Updated for Comparison objects
- `visualization/themes.py`: Added outer_wheel_planet_color to all themes

## Examples Generated

Run `examples/test_comparison_integration.py` to generate:

1. `synastry_draw_method.svg` - Using .draw() method
2. `synastry_preset_auto.svg` - Using preset_synastry()
3. `synastry_position_table_only.svg` - Position table only
4. `synastry_aspectarian_only.svg` - Aspectarian only
5. `synastry_tables_left.svg` - Tables on left
6. `synastry_tables_below.svg` - Tables below
7. `synastry_custom.svg` - Custom configuration
8. `natal_with_tables.svg` - Natal chart compatibility

---

For more information, see the main documentation and CLAUDE.md development guide.
