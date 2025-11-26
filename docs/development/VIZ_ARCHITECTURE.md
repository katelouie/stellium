# Stellium Visualization Architecture

**Version**: 2.0
**Status**: Refactor in Progress
**Last Updated**: November 20, 2025

---

## Table of Contents

1. [Vision & Philosophy](#vision--philosophy)
2. [Design Principles](#design-principles)
3. [Component Overview](#component-overview)
4. [Detailed Specification](#detailed-specification)
5. [Table Layout System](#table-layout-system)
6. [Implementation Status](#implementation-status)
7. [Extension Points](#extension-points)

---

# Part 1: Vision & Philosophy

## What We're Building

A **flexible, config-driven chart visualization system** that can render:

- **Single natal charts** - One person's birth chart
- **Biwheel charts** - Two charts overlaid (synastry, transits, progressions)
- **With or without tables** - Position tables, house cusps, aspectarian grids
- **Variable content** - Different numbers of objects, house systems, aspects
- **Flexible layouts** - Tables positioned right, left, or below the wheel
- **Beautiful theming** - 13+ themes, 24+ color palettes
- **Composable for future** - Grid layouts with multiple chart wheels (like matplotlib subplots)

All through a clean, discoverable fluent API:

```python
# Simple
chart.draw("chart.svg").preset_standard().save()

# Customized
chart.draw("chart.svg") \
    .with_theme("midnight") \
    .with_tables("right") \
    .with_moon_phase(position="center") \
    .save()

# Biwheel
comparison.draw("synastry.svg").preset_synastry().save()
```

## Core Philosophy

### 1. Configuration Over Hardcoding

**BAD (old way)**:
```python
# Hardcoded magic numbers everywhere
if extended_canvas == "right":
    canvas_width = size + 450  # WHY 450?
    table_x = size + 30        # WHY 30?
    aspectarian_y = 300        # WHY 300?
```

**GOOD (new way)**:
```python
# Config-driven, calculated dimensions
config = ChartVisualizationConfig(
    base_size=600,
    tables=TableConfig(
        padding=30,
        gap_between_tables=20,
        column_widths={"object": 120, "position": 100}
    )
)

# Layout engine CALCULATES positions based on config
layout = layout_engine.calculate_layout(chart, config)
# layout.tables["positions"].position = Position(x=630, y=30)  # Calculated!
```

### 2. Measure → Layout → Render Pipeline

**Three distinct phases**:

1. **MEASURE**: Calculate content dimensions BEFORE positioning
   - How many rows in position table? (depends on object count)
   - How wide is the aspectarian? (depends on triangle vs square, object count)
   - How tall are the tables when stacked?

2. **LAYOUT**: Calculate positions and sizes based on measurements
   - Where does the wheel go? (centered, accounting for tables)
   - How big should the wheel be? (auto-grow to fill space)
   - Where does each table go? (stacked with gaps, positioned relative to wheel)

3. **RENDER**: Draw everything using calculated layout
   - Create SVG canvas (calculated size)
   - Position wheel (calculated position, calculated radii)
   - Position tables (calculated positions)
   - Render layers (zodiac, houses, planets, aspects)

**Why this matters**:
- Can't position things without knowing their size
- Can't know size without measuring content first
- Separation allows testing each phase independently

### 3. Immutable Configuration

All config objects are **frozen dataclasses** - once created, they don't change:

```python
@dataclass(frozen=True)
class TableConfig:
    enabled: bool
    placement: "right" | "left" | "below"
    padding: int
    gap_between_tables: int
    # ...
```

**Benefits**:
- No spooky action at a distance (config can't change mid-render)
- Easy to test (same config = same output, always)
- Easy to reason about (if it's broken, config is wrong, not mutated)

### 4. Protocol-Based Extensibility

Components communicate through **protocols**, not concrete classes:

```python
class IRenderLayer(Protocol):
    def render(self, renderer: ChartRenderer, dwg: Drawing, chart: CalculatedChart) -> None:
        """Render this layer to the SVG drawing."""
        ...
```

**Benefits**:
- Easy to add new layers (just implement protocol)
- Easy to test (mock the protocol)
- Loose coupling (layers don't know about each other)

### 5. Separation of Concerns

Each component has ONE job:

| Component | Responsibility | What It Does | What It Doesn't Do |
|-----------|----------------|--------------|-------------------|
| **Config** | Data models | Holds configuration values | Calculate anything |
| **Measurer** | Content sizing | "This table will be 300x400px" | Position anything |
| **LayoutEngine** | Positioning | "Put table at (630, 30)" | Measure or render |
| **Composer** | Orchestration | "Call measurer, then layout, then render" | Layout logic |
| **Renderer** | Coordinates | "Convert 15° Aries to (x, y)" | Layout or measure |
| **Layers** | Drawing | "Draw zodiac wedge as SVG path" | Position or measure |

**Why this matters**:
- Each component is testable in isolation
- Changes in one don't break others
- Easy to understand (each file has ONE purpose)

---

# Part 2: Design Principles

## Principle 1: Progressive Disclosure

Users start simple, complexity revealed gradually:

```python
# Beginner: Just works
chart.draw().save()  # Uses all defaults

# Intermediate: Presets
chart.draw().preset_detailed().save()  # Chart + info corners + moon

# Advanced: Full control
chart.draw() \
    .with_theme("midnight") \
    .with_zodiac_palette("rainbow_midnight") \
    .with_tables("right") \
    .with_moon_phase(position="top-left", size=35) \
    .save()
```

## Principle 2: Sensible Defaults

Every config parameter has a good default:

- **Single chart**: Moon in center (if no aspects), bottom-right (if aspects present)
- **Tables**: Auto-sized columns, adequate padding, sensible gaps
- **Wheel size**: Auto-grows to fill canvas (unless disabled)
- **Radii**: Calculated from base size with sensible multipliers

Users only specify what they want to CHANGE.

## Principle 3: Composability

The system is built from composable pieces:

```python
# Each piece works independently
measurer = ContentMeasurer(config)
dimensions = measurer.measure_position_table(chart)

# Pieces compose to form pipeline
composer = ChartComposer(config)
composer.compose(chart)  # measure → layout → render
```

**Future composability** (not yet implemented):
```python
# Grid of chart wheels (like matplotlib subplots)
grid = ChartGrid(rows=2, cols=2)
grid[0, 0] = natal_chart.draw().preset_minimal()
grid[0, 1] = progression_chart.draw().preset_minimal()
grid[1, 0] = transit_chart.draw().preset_minimal()
grid[1, 1] = solar_return_chart.draw().preset_minimal()
grid.save("life_overview.svg")
```

## Principle 4: Testability

Every component can be tested independently:

```python
# Test measurer
measurer = ContentMeasurer(config)
dims = measurer.measure_position_table(chart)
assert dims.width == expected_width
assert dims.height == expected_height

# Test layout engine
layout = LayoutEngine(config).calculate_layout(chart)
assert layout.wheel_position.x == expected_x
assert layout.tables["positions"].dimensions.width == expected_width

# Test rendering (compare SVG output)
composer = ChartComposer(config)
svg_content = composer.compose(chart)
assert_svg_matches_expected(svg_content)
```

## Principle 5: Debuggability

When something's wrong, it should be OBVIOUS where:

- **Config wrong?** Check `ChartVisualizationConfig` values
- **Sizing wrong?** Check `ContentMeasurer` calculations
- **Positioning wrong?** Check `LayoutEngine` calculations
- **Rendering wrong?** Check layer `render()` methods
- **Wiring wrong?** Check `ChartComposer` orchestration

Each phase outputs a data structure you can inspect:

```python
# Debug pipeline
config = ChartVisualizationConfig(...)
composer = ChartComposer(config)

# Add breakpoint in composer.compose():
measurements = measurer.measure_all_elements(chart)
# Inspect: print(measurements)

layout = layout_engine.calculate_layout(chart)
# Inspect: print(layout.tables["positions"].position)

# Now you know EXACTLY where the problem is
```

---

# Part 3: Component Overview

## The Pipeline

```
User Code:
  chart.draw("chart.svg").with_tables("right").save()
    ↓
ChartDrawBuilder (builder.py):
  - Collects user options via fluent API
  - Converts to ChartVisualizationConfig
  - Creates ChartComposer
  - Calls composer.compose(chart)
    ↓
ChartComposer (composer.py):
  - Orchestrates the pipeline
  - Calls ContentMeasurer → LayoutEngine → Render
    ↓
ContentMeasurer (layout/measurer.py):
  - Measures table dimensions (rows × columns)
  - Measures corner element sizes
  - Returns Measurements object
    ↓
LayoutEngine (layout/engine.py):
  - Calculates canvas size (base + tables)
  - Calculates wheel size (auto-grow if enabled)
  - Positions wheel (centered, accounting for tables)
  - Calculates wheel radii (biwheel vs single)
  - Positions tables (stacked with gaps)
  - Positions corner elements
  - Returns LayoutResult object
    ↓
ChartComposer (render phase):
  - Creates SVG canvas (layout.canvas_dimensions)
  - Creates ChartRenderer (layout.wheel_radii)
  - Creates layers via LayerFactory
  - Renders each layer
  - Renders tables (via extended_canvas layers)
  - Saves SVG file
```

## Component Details

### ChartVisualizationConfig (config.py)

**Purpose**: Immutable configuration for entire visualization

**Structure**:
```python
@dataclass(frozen=True)
class ChartVisualizationConfig:
    filename: str                      # Output SVG filename
    base_size: int                     # Base wheel size (600px default)

    wheel: ChartWheelConfig           # Wheel-specific config
    corners: InfoCornerConfig         # Corner elements config
    tables: TableConfig               # Table config

    auto_center: bool                 # Center wheel accounting for tables
    auto_grow_wheel: bool             # Grow wheel to fill available space
    min_margin: int                   # Minimum margin around wheel
```

**Sub-configs**:

```python
@dataclass(frozen=True)
class ChartWheelConfig:
    chart_type: "single" | "biwheel"         # Single or comparison chart
    radii_multipliers: dict[str, float]      # Tweakable radii (zodiac_outer: 0.47, etc.)
    theme: ChartTheme | None                 # Midnight, celestial, etc.
    zodiac_palette: str | None               # Color palette for zodiac
    aspect_palette: str | None               # Color palette for aspects
    planet_glyph_palette: str | None         # Color palette for planet glyphs
    rotation: float                          # Rotation angle
    color_sign_info: bool                    # Color tiny zodiac glyphs in info stacks
    shrink_to_fit: bool                      # Shrink wheel if needed

@dataclass(frozen=True)
class TableConfig:
    enabled: bool                            # Show tables at all?
    placement: "right" | "left" | "below"    # Where to put tables

    show_positions: bool                     # Show position table
    show_houses: bool                        # Show house cusp table
    show_aspectarian: bool                   # Show aspect grid

    padding: int                             # Padding around tables
    gap_between_tables: int                  # Vertical gap when stacking

    # Column widths (for position table)
    column_widths: dict[str, int]            # {"object": 120, "position": 100, ...}

    # Object types to include
    object_types: list[str]                  # ["planets", "angles", "nodes", ...]

@dataclass(frozen=True)
class InfoCornerConfig:
    show_chart_info: bool                    # Chart name, date, location
    show_moon_phase: bool                    # Moon phase visualization
    show_aspect_counts: bool                 # Aspect count breakdown
    show_element_modality: bool              # Element/modality table
    show_chart_shape: bool                   # Chart shape (bowl, bundle, etc.)

    # Positioning
    chart_info_position: str | None          # "top-left", "top-right", etc.
    moon_phase_position: str | None          # Smart default: center or bottom-right
    aspect_counts_position: str | None
    element_modality_position: str | None
    chart_shape_position: str | None

    # Sizing
    moon_phase_size: int | None              # Smart default: 60 center, 28 corners
    moon_phase_label_size: int | None        # Smart default: 14 center, 11 corners
```

**Key insight**: Config is DATA ONLY. No logic, no calculations. Just values.

### ContentMeasurer (layout/measurer.py)

**Purpose**: Calculate dimensions of content BEFORE layout

**Key methods**:

```python
class ContentMeasurer:
    def __init__(self, config: ChartVisualizationConfig):
        self.config = config

    def measure_all_elements(self, chart: CalculatedChart | Comparison) -> Measurements:
        """Measure everything, return dimensions."""
        measurements = {}

        if self.config.tables.show_positions:
            measurements["positions"] = self.measure_position_table(chart)

        if self.config.tables.show_houses:
            measurements["houses"] = self.measure_house_table(chart)

        if self.config.tables.show_aspectarian:
            measurements["aspectarian"] = self.measure_aspectarian(chart)

        # Measure corner elements
        measurements["corners"] = self.measure_corner_elements(chart)

        return Measurements(measurements)

    def measure_position_table(self, chart) -> Dimensions:
        """Calculate position table dimensions based on object count."""
        # Count objects (planets, angles, nodes, etc.)
        num_objects = self._count_objects(chart)

        # Calculate rows (objects + header + footer)
        num_rows = num_objects + 2

        # Calculate columns (Object, Sign, Longitude, House, Speed, ...)
        num_cols = len(self.config.tables.column_widths)

        # Calculate dimensions
        row_height = 20  # pixels per row
        col_widths = self.config.tables.column_widths.values()

        width = sum(col_widths) + self.config.tables.padding * 2
        height = num_rows * row_height + self.config.tables.padding * 2

        return Dimensions(width=width, height=height)

    def measure_aspectarian(self, chart) -> Dimensions:
        """Calculate aspectarian grid size based on chart type and object count."""
        num_objects = self._count_aspectable_objects(chart)

        if isinstance(chart, Comparison):
            # Square grid for biwheel (chart1 × chart2)
            grid_size = num_objects  # Full square
        else:
            # Triangle grid for single chart (n × n / 2)
            grid_size = num_objects

        cell_size = 25  # pixels per cell
        width = grid_size * cell_size + self.config.tables.padding * 2
        height = grid_size * cell_size + self.config.tables.padding * 2

        return Dimensions(width=width, height=height)
```

**Key insight**: Measurer NEVER positions anything. It just calculates "how big?"

### LayoutEngine (layout/engine.py)

**Purpose**: Calculate positions and sizes based on measurements

**Key methods**:

```python
class LayoutEngine:
    def __init__(self, config: ChartVisualizationConfig):
        self.config = config
        self.measurer = ContentMeasurer(config)

    def calculate_layout(self, chart) -> LayoutResult:
        """Calculate complete layout for chart visualization."""

        # Phase 1: Measure everything
        measurements = self.measurer.measure_all_elements(chart)

        # Phase 2: Calculate table layout
        table_layout = self._calculate_table_layout(measurements)

        # Phase 3: Calculate canvas size
        canvas_dims = self._calculate_canvas_size(table_layout, measurements)

        # Phase 4: Calculate wheel size (auto-grow if enabled)
        wheel_size = self._calculate_wheel_size(canvas_dims, table_layout)

        # Phase 5: Position wheel (centered, accounting for tables)
        wheel_pos = self._position_wheel(canvas_dims, wheel_size, table_layout)

        # Phase 6: Calculate wheel radii
        wheel_radii = self._calculate_wheel_radii(wheel_size, chart)

        # Phase 7: Position corner elements
        corners = self._position_info_corners(wheel_pos, wheel_size, measurements)

        # Phase 8: Finalize table positions (absolute coordinates)
        tables = self._finalize_table_positions(table_layout, wheel_pos, wheel_size)

        return LayoutResult(
            canvas_dimensions=canvas_dims,
            wheel_position=wheel_pos,
            wheel_size=wheel_size,
            wheel_radii=wheel_radii,
            corner_positions=corners,
            table_positions=tables,
        )
```

**Key calculations**:

```python
def _calculate_canvas_size(self, table_layout, measurements) -> Dimensions:
    """Calculate total canvas size (wheel + tables)."""
    base_size = self.config.base_size

    if not self.config.tables.enabled:
        # No tables: canvas = base_size
        return Dimensions(width=base_size, height=base_size)

    if self.config.tables.placement == "right":
        # Canvas width = base + table_width
        table_width = table_layout.total_width
        return Dimensions(
            width=base_size + table_width,
            height=max(base_size, table_layout.total_height)
        )

    elif self.config.tables.placement == "left":
        # Same as right, but wheel shifted
        table_width = table_layout.total_width
        return Dimensions(
            width=base_size + table_width,
            height=max(base_size, table_layout.total_height)
        )

    elif self.config.tables.placement == "below":
        # Canvas height = base + table_height
        table_height = table_layout.total_height
        return Dimensions(
            width=max(base_size, table_layout.total_width),
            height=base_size + table_height
        )

def _calculate_wheel_radii(self, wheel_size, chart) -> dict[str, float]:
    """Calculate wheel radii from base size and config multipliers."""
    multipliers = self.config.wheel.radii_multipliers
    is_biwheel = isinstance(chart, Comparison)

    radii = {}

    if is_biwheel:
        # Biwheel: Two concentric rings
        radii["outer_border"] = wheel_size * multipliers["outer_border"]
        radii["zodiac_ring_outer"] = wheel_size * multipliers["zodiac_outer"]
        radii["zodiac_ring_inner"] = wheel_size * multipliers["zodiac_inner"]
        radii["outer_planet_ring"] = wheel_size * multipliers["outer_planets"]
        radii["house_ring"] = wheel_size * multipliers["houses"]
        radii["inner_planet_ring"] = wheel_size * multipliers["inner_planets"]
        radii["aspect_ring_outer"] = wheel_size * multipliers["aspects_outer"]
        radii["aspect_ring_inner"] = wheel_size * multipliers["aspects_inner"]
    else:
        # Single chart: One ring
        radii["outer_border"] = wheel_size * multipliers["outer_border"]
        radii["zodiac_ring_outer"] = wheel_size * multipliers["zodiac_outer"]
        radii["zodiac_ring_inner"] = wheel_size * multipliers["zodiac_inner"]
        radii["planet_ring"] = wheel_size * multipliers["planets"]
        radii["house_ring"] = wheel_size * multipliers["houses"]
        radii["aspect_ring_outer"] = wheel_size * multipliers["aspects_outer"]
        radii["aspect_ring_inner"] = wheel_size * multipliers["aspects_inner"]

    return radii
```

**Key insight**: LayoutEngine outputs ABSOLUTE positions (x, y in pixels), not relative offsets.

### ChartComposer (composer.py)

**Purpose**: Orchestrate the entire rendering pipeline

**Structure**:

```python
class ChartComposer:
    def __init__(self, config: ChartVisualizationConfig):
        self.config = config
        self.layout_engine = LayoutEngine(config)
        self.layer_factory = LayerFactory(config)

    def compose(self, chart: CalculatedChart | Comparison) -> str:
        """Compose chart visualization, return SVG content."""

        # Step 1: Calculate layout
        layout = self.layout_engine.calculate_layout(chart)

        # Step 2: Create canvas
        canvas = self._create_canvas(layout)

        # Step 3: Create renderer
        renderer = self._create_renderer(layout, chart)

        # Step 4: Create layers
        layers = self.layer_factory.create_layers(chart, layout)

        # Step 5: Render layers (wheel)
        for layer in layers:
            layer.render(renderer, canvas, chart)

        # Step 6: Render tables (if enabled)
        if self.config.tables.enabled:
            self._render_tables(canvas, renderer, chart, layout)

        # Step 7: Save and return
        canvas.saveas(self.config.filename)
        return canvas.tostring()
```

**Adapter pattern for tables**:

```python
def _render_tables(self, canvas, renderer, chart, layout):
    """Render tables using calculated positions."""

    # Render position table
    if self.config.tables.show_positions and "positions" in layout.table_positions:
        bbox = layout.table_positions["positions"]

        # OLD table layer expects x_offset, y_offset in constructor
        # NEW layout engine provides Position(x, y)
        # ADAPTER: Convert new to old
        position_layer = PositionTableLayer(
            x_offset=int(bbox.position.x),  # Convert new → old
            y_offset=int(bbox.position.y),
            object_types=self.config.tables.object_types,
        )
        position_layer.render(renderer, canvas, chart)

    # Similar for houses, aspectarian...
```

**Key insight**: Composer is THIN. It delegates to specialists (layout engine, layer factory), doesn't contain logic itself.

### ChartRenderer (core.py)

**Purpose**: Coordinate system and theme integration

**Key methods**:

```python
class ChartRenderer:
    def __init__(self, size: int, radii: dict[str, float], theme: ChartTheme, ...):
        self.size = size
        self.center = size // 2
        self.radii = radii  # From LayoutEngine!
        self.theme_style = get_theme_style(theme)
        self.rotation = rotation

    def polar_to_cartesian(self, angle: float, radius: float) -> tuple[float, float]:
        """Convert astrological coordinates to SVG (x, y)."""
        # Astrology: 0° Aries at 9 o'clock, increases counterclockwise
        # SVG: 0° at 3 o'clock, increases clockwise

        adjusted_angle = (90 - angle - self.rotation) % 360
        radians = math.radians(adjusted_angle)

        x = self.center + radius * math.cos(radians)
        y = self.center - radius * math.sin(radians)

        return (x, y)

    def create_svg_drawing(self, filename: str, width: int, height: int):
        """Create SVG drawing with background."""
        dwg = svgwrite.Drawing(filename, size=(width, height))

        # Background rect
        bg_color = self.theme_style["background_color"]
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=bg_color))

        return dwg
```

**Key insight**: Renderer is a HELPER, not an orchestrator. It provides coordinate conversion and theme colors, doesn't control flow.

### Layers (layers.py, extended_canvas.py)

**Purpose**: Draw specific chart elements

**Protocol**:

```python
class IRenderLayer(Protocol):
    def render(self, renderer: ChartRenderer, dwg: Drawing, chart: CalculatedChart) -> None:
        """Render this layer to the SVG drawing."""
        ...
```

**Example layer**:

```python
class ZodiacLayer:
    def __init__(self, palette: str, style_override: dict = None):
        self.palette = palette
        self.style = style_override or {}

    def render(self, renderer, dwg, chart):
        """Draw 12 zodiac wedges."""
        colors = get_palette_colors(self.palette)

        for sign_index in range(12):
            start_angle = sign_index * 30
            end_angle = start_angle + 30

            # Get color for this sign
            color = colors[sign_index]

            # Calculate path using renderer's radii
            outer_radius = renderer.radii["zodiac_ring_outer"]
            inner_radius = renderer.radii["zodiac_ring_inner"]

            # Draw wedge
            path = self._create_wedge_path(
                renderer, start_angle, end_angle, inner_radius, outer_radius
            )
            dwg.add(dwg.path(d=path, fill=color, stroke="#000", stroke_width=1))

            # Draw zodiac glyph
            glyph_angle = start_angle + 15  # Center of sign
            glyph_radius = (outer_radius + inner_radius) / 2
            x, y = renderer.polar_to_cartesian(glyph_angle, glyph_radius)

            glyph = ZODIAC_GLYPHS[sign_index]
            dwg.add(dwg.text(glyph, insert=(x, y), ...))
```

**Key insight**: Layers are PURE rendering. They receive positions/sizes from layout, don't calculate them.

---

# Part 4: Detailed Specification

## Data Flow: chart.draw() → SVG

Let's trace a complete rendering from user code to saved file:

### User Code
```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").calculate()

chart.draw("einstein.svg") \
    .with_theme("midnight") \
    .with_tables("right") \
    .with_moon_phase(position="center") \
    .save()
```

### Step 1: Builder Collects Options

**File**: `builder.py`

```python
class ChartDrawBuilder:
    def __init__(self, chart: CalculatedChart):
        self._chart = chart
        self._filename = "chart.svg"
        self._size = 600
        self._theme = None
        self._tables_placement = None
        # ... more options

    def with_theme(self, theme: str):
        self._theme = theme
        return self

    def with_tables(self, placement: str):
        self._tables_placement = placement
        self._tables_enabled = True
        return self

    def with_moon_phase(self, position: str):
        self._moon_phase_enabled = True
        self._moon_phase_position = position
        return self
```

After chaining, builder has:
- `_filename = "einstein.svg"`
- `_theme = "midnight"`
- `_tables_placement = "right"`
- `_tables_enabled = True`
- `_moon_phase_enabled = True`
- `_moon_phase_position = "center"`

### Step 2: Builder Converts to Config

**File**: `builder.py` (in `save()` method)

```python
def save(self):
    # Convert builder options → config
    config = ChartVisualizationConfig(
        filename=self._filename,
        base_size=self._size,

        wheel=ChartWheelConfig(
            chart_type="single",  # Not a comparison
            radii_multipliers=DEFAULT_RADII_MULTIPLIERS,
            theme=ChartTheme(self._theme) if self._theme else None,
            zodiac_palette=self._zodiac_palette,
            # ...
        ),

        corners=InfoCornerConfig(
            show_moon_phase=self._moon_phase_enabled,
            moon_phase_position=self._moon_phase_position,
            # ...
        ),

        tables=TableConfig(
            enabled=self._tables_enabled,
            placement=self._tables_placement,
            show_positions=True,  # Default
            show_houses=True,     # Default
            show_aspectarian=True,  # Default
            padding=30,
            gap_between_tables=20,
            column_widths=DEFAULT_COLUMN_WIDTHS,
            # ...
        ),

        auto_center=True,
        auto_grow_wheel=True,
        min_margin=30,
    )

    # Create composer
    composer = ChartComposer(config)

    # Run pipeline
    return composer.compose(self._chart)
```

Now we have an immutable `ChartVisualizationConfig` object.

### Step 3: Composer Initiates Pipeline

**File**: `composer.py`

```python
class ChartComposer:
    def compose(self, chart):
        # Step 1: Calculate layout
        layout = self.layout_engine.calculate_layout(chart)

        # ... continue to render
```

Composer delegates to `LayoutEngine`.

### Step 4: Layout Engine Measures

**File**: `layout/engine.py`

```python
def calculate_layout(self, chart):
    # Measure all elements
    measurements = self.measurer.measure_all_elements(chart)
```

**File**: `layout/measurer.py`

```python
def measure_all_elements(self, chart):
    measurements = {}

    # Measure position table
    if self.config.tables.show_positions:
        # Einstein chart has 10 planets + 4 angles + 2 nodes = 16 objects
        # Table: 16 rows + header + footer = 18 rows
        # Columns: Object (120px) + Sign (80px) + Position (100px) + House (60px) + Speed (80px)
        # Width: 120 + 80 + 100 + 60 + 80 + padding*2 = 440 + 60 = 500px
        # Height: 18 rows * 20px + padding*2 = 360 + 60 = 420px
        measurements["positions"] = Dimensions(width=500, height=420)

    # Measure house table
    if self.config.tables.show_houses:
        # 12 houses + header = 13 rows
        # Columns: House (80px) + Cusp (100px) + Sign (80px)
        # Width: 80 + 100 + 80 + padding*2 = 260 + 60 = 320px
        # Height: 13 * 20 + padding*2 = 260 + 60 = 320px
        measurements["houses"] = Dimensions(width=320, height=320)

    # Measure aspectarian
    if self.config.tables.show_aspectarian:
        # 16 objects, triangle grid
        # 16 * 16 / 2 = 128 cells, but arranged as 16x16 triangle
        # Width: 16 * 25 + padding*2 = 400 + 60 = 460px
        # Height: Same
        measurements["aspectarian"] = Dimensions(width=460, height=460)

    return Measurements(measurements)
```

Measurer returns:
```python
{
    "positions": Dimensions(width=500, height=420),
    "houses": Dimensions(width=320, height=320),
    "aspectarian": Dimensions(width=460, height=460),
}
```

### Step 5: Layout Engine Calculates Table Layout

**File**: `layout/engine.py`

```python
def _calculate_table_layout(self, measurements):
    # Tables placement: "right"
    # Stack vertically: positions, houses, aspectarian

    gap = self.config.tables.gap_between_tables  # 20px

    # Total width: max of all table widths
    total_width = max(
        measurements["positions"].width,    # 500
        measurements["houses"].width,       # 320
        measurements["aspectarian"].width,  # 460
    )  # = 500px

    # Total height: sum of heights + gaps
    total_height = (
        measurements["positions"].height +     # 420
        gap +                                  # 20
        measurements["houses"].height +        # 320
        gap +                                  # 20
        measurements["aspectarian"].height     # 460
    )  # = 1240px

    return TableLayout(
        total_width=500,
        total_height=1240,
        arrangement=[
            ("positions", RelativePosition(x=0, y=0)),
            ("houses", RelativePosition(x=0, y=440)),     # 420 + 20 gap
            ("aspectarian", RelativePosition(x=0, y=780)),  # 420 + 20 + 320 + 20
        ]
    )
```

### Step 6: Layout Engine Calculates Canvas Size

**File**: `layout/engine.py`

```python
def _calculate_canvas_size(self, table_layout, measurements):
    base_size = self.config.base_size  # 600px

    # Tables on right: canvas_width = base + table_width
    canvas_width = base_size + table_layout.total_width
    # = 600 + 500 = 1100px

    # Canvas height: max of wheel and tables
    canvas_height = max(base_size, table_layout.total_height)
    # = max(600, 1240) = 1240px

    return Dimensions(width=1100, height=1240)
```

### Step 7: Layout Engine Calculates Wheel Size & Position

**File**: `layout/engine.py`

```python
def _calculate_wheel_size(self, canvas_dims, table_layout):
    if not self.config.auto_grow_wheel:
        return self.config.base_size  # 600px

    # Auto-grow: wheel can expand to fill vertical space
    available_height = canvas_dims.height - 2 * self.config.min_margin
    # = 1240 - 2*30 = 1180px

    # Wheel is square, so wheel_size = min(available_width, available_height)
    available_width = self.config.base_size  # Wheel area only, not table area

    # Actually, let's be smarter: wheel fills its allocated area
    # Allocated area: base_size × canvas_height
    available_width = self.config.base_size - 2 * self.config.min_margin
    # = 600 - 60 = 540px

    wheel_size = min(available_width, available_height)
    # = min(540, 1180) = 540px

    return wheel_size

def _position_wheel(self, canvas_dims, wheel_size, table_layout):
    if self.config.tables.placement == "right":
        # Wheel in left area, centered vertically
        x = (self.config.base_size - wheel_size) // 2
        # = (600 - 540) // 2 = 30px

        y = (canvas_dims.height - wheel_size) // 2
        # = (1240 - 540) // 2 = 350px

        return Position(x=30, y=350)
```

### Step 8: Layout Engine Calculates Wheel Radii

**File**: `layout/engine.py`

```python
def _calculate_wheel_radii(self, wheel_size, chart):
    multipliers = self.config.wheel.radii_multipliers
    # DEFAULT_RADII_MULTIPLIERS = {
    #     "outer_border": 0.48,
    #     "zodiac_outer": 0.47,
    #     "zodiac_inner": 0.40,
    #     "planets": 0.32,
    #     "houses": 0.28,
    #     "aspects_outer": 0.26,
    #     "aspects_inner": 0.08,
    # }

    radii = {}
    radii["outer_border"] = wheel_size * multipliers["outer_border"]
    # = 540 * 0.48 = 259.2px

    radii["zodiac_ring_outer"] = wheel_size * multipliers["zodiac_outer"]
    # = 540 * 0.47 = 253.8px

    radii["zodiac_ring_inner"] = wheel_size * multipliers["zodiac_inner"]
    # = 540 * 0.40 = 216px

    radii["planet_ring"] = wheel_size * multipliers["planets"]
    # = 540 * 0.32 = 172.8px

    # ... etc

    return radii
```

### Step 9: Layout Engine Finalizes Table Positions

**File**: `layout/engine.py`

```python
def _finalize_table_positions(self, table_layout, wheel_pos, wheel_size):
    # Tables are on the right
    # Table area starts at: wheel_area_width (base_size)
    table_x_start = self.config.base_size
    # = 600px

    tables = {}

    for table_name, relative_pos in table_layout.arrangement:
        # Convert relative position to absolute
        absolute_x = table_x_start + relative_pos.x
        absolute_y = relative_pos.y

        # "positions" table
        if table_name == "positions":
            # relative_pos = (0, 0)
            # absolute = (600, 0)
            bbox = BoundingBox(
                position=Position(x=600, y=0),
                dimensions=measurements["positions"]  # (500, 420)
            )
            tables["positions"] = bbox

        # "houses" table
        elif table_name == "houses":
            # relative_pos = (0, 440)
            # absolute = (600, 440)
            bbox = BoundingBox(
                position=Position(x=600, y=440),
                dimensions=measurements["houses"]  # (320, 320)
            )
            tables["houses"] = bbox

        # ... etc

    return tables
```

### Step 10: Layout Complete, Return to Composer

**File**: `layout/engine.py`

```python
return LayoutResult(
    canvas_dimensions=Dimensions(width=1100, height=1240),
    wheel_position=Position(x=30, y=350),
    wheel_size=540,
    wheel_radii={
        "outer_border": 259.2,
        "zodiac_ring_outer": 253.8,
        "zodiac_ring_inner": 216,
        "planet_ring": 172.8,
        # ...
    },
    corner_positions={
        "moon_phase": BoundingBox(position=Position(x=270, y=620), dimensions=...),
        # ... center position for moon
    },
    table_positions={
        "positions": BoundingBox(position=Position(x=600, y=0), dimensions=(500, 420)),
        "houses": BoundingBox(position=Position(x=600, y=440), dimensions=(320, 320)),
        "aspectarian": BoundingBox(position=Position(x=600, y=780), dimensions=(460, 460)),
    },
)
```

### Step 11: Composer Creates Canvas

**File**: `composer.py`

```python
def _create_canvas(self, layout):
    # Create SVG drawing with calculated dimensions
    dwg = svgwrite.Drawing(
        self.config.filename,  # "einstein.svg"
        size=(layout.canvas_dimensions.width, layout.canvas_dimensions.height)
        # size=(1100, 1240)
    )

    # Add background
    bg_color = get_theme_style(self.config.wheel.theme)["background_color"]
    # midnight theme: "#0A1628"

    dwg.add(dwg.rect(
        insert=(0, 0),
        size=(1100, 1240),
        fill="#0A1628"
    ))

    return dwg
```

### Step 12: Composer Creates Renderer

**File**: `composer.py`

```python
def _create_renderer(self, layout, chart):
    return ChartRenderer(
        size=layout.wheel_size,          # 540
        radii=layout.wheel_radii,        # Calculated radii dict
        rotation=self.config.wheel.rotation,  # 0.0
        theme=self.config.wheel.theme,   # ChartTheme.MIDNIGHT
        offset_x=layout.wheel_position.x,  # 30
        offset_y=layout.wheel_position.y,  # 350
    )
```

**Important**: Renderer needs offset so `polar_to_cartesian()` positions things relative to wheel position, not canvas origin.

Actually, let's check the current implementation... this might need updating!

### Step 13: Composer Creates Layers

**File**: `composer.py`

```python
layers = self.layer_factory.create_layers(chart, layout)
```

**File**: `layer_factory.py`

```python
def create_layers(self, chart, layout):
    layers = []

    # Zodiac layer
    zodiac_palette = self.config.wheel.zodiac_palette or "grey"
    layers.append(ZodiacLayer(palette=zodiac_palette))

    # House cusp layer
    layers.append(HouseCuspLayer(house_system=chart.default_house_system))

    # Aspect layer
    if chart.aspects:
        aspect_palette = self.config.wheel.aspect_palette or "default"
        layers.append(AspectLayer(
            aspects=chart.aspects,
            palette=aspect_palette,
            opacity=0.6
        ))

    # Planet layer
    planet_palette = self.config.wheel.planet_glyph_palette or "default"
    layers.append(PlanetLayer(
        positions=chart.positions,
        palette=planet_palette
    ))

    # Corner layers
    if self.config.corners.show_moon_phase:
        bbox = layout.corner_positions.get("moon_phase")
        layers.append(MoonPhaseLayer(
            chart=chart,
            position=bbox.position if bbox else Position(x=270, y=620),
            size=self.config.corners.moon_phase_size or 60
        ))

    # ... other corner layers

    return layers
```

### Step 14: Composer Renders Layers

**File**: `composer.py`

```python
for layer in layers:
    layer.render(renderer, canvas, chart)
```

Each layer draws its SVG elements to the canvas.

**Example: ZodiacLayer renders**

**File**: `layers.py`

```python
def render(self, renderer, dwg, chart):
    colors = get_palette_colors(self.palette)  # Midnight theme colors

    for sign_index in range(12):
        start_angle = sign_index * 30  # Aries=0°, Taurus=30°, ...
        end_angle = start_angle + 30

        color = colors[sign_index]

        # Draw wedge using renderer's radii
        outer_r = renderer.radii["zodiac_ring_outer"]  # 253.8
        inner_r = renderer.radii["zodiac_ring_inner"]  # 216

        # Create path (complex SVG arc)
        path = self._create_wedge_path(renderer, start_angle, end_angle, inner_r, outer_r)

        # Add to drawing
        dwg.add(dwg.path(d=path, fill=color, stroke="#000", stroke_width=0.5))
```

### Step 15: Composer Renders Tables

**File**: `composer.py`

```python
def _render_tables(self, canvas, renderer, chart, layout):
    # Position table
    if self.config.tables.show_positions and "positions" in layout.table_positions:
        bbox = layout.table_positions["positions"]
        # bbox.position = Position(x=600, y=0)
        # bbox.dimensions = Dimensions(width=500, height=420)

        # Create layer with calculated position
        position_layer = PositionTableLayer(
            x_offset=int(bbox.position.x),  # 600
            y_offset=int(bbox.position.y),  # 0
            object_types=self.config.tables.object_types,
        )

        position_layer.render(renderer, canvas, chart)

    # Similar for houses, aspectarian...
```

**File**: `extended_canvas.py`

```python
class PositionTableLayer:
    def __init__(self, x_offset, y_offset, object_types):
        self.x_offset = x_offset  # 600
        self.y_offset = y_offset  # 0
        self.object_types = object_types

    def render(self, renderer, dwg, chart):
        # Draw table at (x_offset, y_offset)

        # Header row
        y = self.y_offset + 20
        dwg.add(dwg.text("Object", insert=(self.x_offset + 10, y), ...))
        dwg.add(dwg.text("Sign", insert=(self.x_offset + 130, y), ...))
        # ... etc

        # Data rows
        for obj in chart.positions:
            y += 20
            dwg.add(dwg.text(obj.name, insert=(self.x_offset + 10, y), ...))
            # ... etc
```

### Step 16: Save SVG

**File**: `composer.py`

```python
canvas.saveas(self.config.filename)  # "einstein.svg"
return canvas.tostring()
```

Done! SVG file written to disk.

---

## Config Parameter Propagation

Let's trace how each config value flows through the system:

### Example: `tables.padding`

**User Code**:
```python
chart.draw().with_tables("right").save()
```

**Builder** (uses default):
```python
# builder.py, save() method
tables=TableConfig(
    padding=30,  # DEFAULT
    # ...
)
```

**Measurer** (uses config.tables.padding):
```python
# layout/measurer.py
def measure_position_table(self, chart):
    # ...
    width = sum(col_widths) + self.config.tables.padding * 2
    #                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    height = num_rows * row_height + self.config.tables.padding * 2
    #                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**Result**: Tables get 30px padding on all sides.

---

### Example: `wheel.radii_multipliers`

**User Code**:
```python
# User wants custom radii for biwheel
custom_radii = {
    "outer_border": 0.48,
    "zodiac_outer": 0.46,  # Slightly smaller
    "outer_planets": 0.38,
    "inner_planets": 0.22,
    # ...
}

# How do they set this? Builder needs method!
chart.draw().with_custom_radii(custom_radii).save()
```

**Builder** (needs implementation):
```python
class ChartDrawBuilder:
    def with_custom_radii(self, radii: dict[str, float]):
        self._radii_multipliers = radii
        return self

    def save(self):
        config = ChartVisualizationConfig(
            wheel=ChartWheelConfig(
                radii_multipliers=self._radii_multipliers or DEFAULT_RADII_MULTIPLIERS,
                #                 ^^^^^^^^^^^^^^^^^^^^^^^
            ),
            # ...
        )
```

**LayoutEngine** (uses config.wheel.radii_multipliers):
```python
# layout/engine.py
def _calculate_wheel_radii(self, wheel_size, chart):
    multipliers = self.config.wheel.radii_multipliers
    #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    radii["outer_border"] = wheel_size * multipliers["outer_border"]
    radii["zodiac_ring_outer"] = wheel_size * multipliers["zodiac_outer"]
    # ...
```

**Renderer** (receives calculated radii):
```python
# composer.py
renderer = ChartRenderer(
    radii=layout.wheel_radii,  # Calculated values, not multipliers
    # ...
)
```

**Layers** (use renderer.radii):
```python
# layers.py
def render(self, renderer, dwg, chart):
    outer_r = renderer.radii["zodiac_ring_outer"]
    #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

---

### Example: `tables.column_widths`

**User Code**:
```python
# User wants wider position column
custom_widths = {
    "object": 150,  # Default 120
    "position": 120,  # Default 100
    "house": 80,  # Default 60
}

chart.draw().with_table_column_widths(custom_widths).save()
```

**Builder** (needs implementation):
```python
class ChartDrawBuilder:
    def with_table_column_widths(self, widths: dict[str, int]):
        self._table_column_widths = widths
        return self

    def save(self):
        config = ChartVisualizationConfig(
            tables=TableConfig(
                column_widths=self._table_column_widths or DEFAULT_COLUMN_WIDTHS,
                #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
            ),
            # ...
        )
```

**Measurer** (uses config.tables.column_widths):
```python
# layout/measurer.py
def measure_position_table(self, chart):
    col_widths = self.config.tables.column_widths.values()
    #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    width = sum(col_widths) + padding * 2
```

**Table Layer** (uses config.tables.column_widths):
```python
# extended_canvas.py
class PositionTableLayer:
    def render(self, renderer, dwg, chart):
        widths = renderer.config.tables.column_widths
        #        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # Wait, renderer doesn't have config!
        # This is a problem - table layer needs config too!
```

**ISSUE FOUND**: Table layers need access to config for column widths, but currently only receive x_offset/y_offset.

**Fix needed**: Pass config to table layers:

```python
# composer.py
position_layer = PositionTableLayer(
    x_offset=int(bbox.position.x),
    y_offset=int(bbox.position.y),
    config=self.config,  # NEW: Pass entire config
)
```

```python
# extended_canvas.py
class PositionTableLayer:
    def __init__(self, x_offset, y_offset, config):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.config = config  # Store config

    def render(self, renderer, dwg, chart):
        # Now can access column widths!
        widths = self.config.tables.column_widths
```

---

## Config Wiring Issues (To Fix)

Based on Kate's report that "multiple config values weren't passing through":

### Issue 1: Table layers don't receive config

**Current**: Table layers only get `x_offset, y_offset`
**Problem**: Can't access `column_widths`, `padding`, `gap_between_tables`
**Fix**: Pass entire `config` to table layer constructors

### Issue 2: Wheel margins not applied

**Possible cause**: ChartRenderer doesn't know about `min_margin`
**Fix**: LayoutEngine should account for min_margin when calculating wheel size/position

### Issue 3: Info corner margins not applied

**Possible cause**: Corner layers don't receive config
**Fix**: Pass config to corner layers (or just the relevant subset)

### Issue 4: Table gap not used

**Possible cause**: `_calculate_table_layout()` might use hardcoded gap
**Fix**: Ensure it uses `self.config.tables.gap_between_tables`

---

# Part 5: Table Layout System

## The Dev/Testing Tool

Kate wants to explore different table arrangements before settling on defaults. This is a DEV TOOL, not exposed to end users (at least initially).

### Current Table Placement Options

**User-facing** (in builder):
- `"right"` - All tables stacked vertically to the right of wheel
- `"left"` - All tables stacked vertically to the left of wheel
- `"below"` - All tables stacked horizontally below wheel

### What Kate Wants to Test

**Different arrangements**:
- Position table next to house table (side-by-side)
- Position table above aspectarian (vertically)
- House table in corner, aspectarian below wheel
- Arbitrary grid layout (2×2, 3×1, etc.)

### Design: Table Layout DSL

**Internal config** (not exposed via builder yet):

```python
@dataclass(frozen=True)
class TableLayoutConfig:
    mode: "preset" | "custom"

    # If mode == "preset"
    preset: "right" | "left" | "below" | None

    # If mode == "custom"
    arrangement: list[TableArrangement] | None

@dataclass(frozen=True)
class TableArrangement:
    table_name: str  # "positions", "houses", "aspectarian"
    position: "right" | "left" | "below" | "grid"
    grid_cell: tuple[int, int] | None  # (row, col) if position == "grid"
```

**Example usage** (dev tool):

```python
# Test arrangement 1: Position and houses side-by-side on right
config = ChartVisualizationConfig(
    tables=TableConfig(
        layout=TableLayoutConfig(
            mode="custom",
            arrangement=[
                TableArrangement(table_name="positions", position="grid", grid_cell=(0, 0)),
                TableArrangement(table_name="houses", position="grid", grid_cell=(0, 1)),
                TableArrangement(table_name="aspectarian", position="grid", grid_cell=(1, 0)),
            ]
        )
    )
)
```

**LayoutEngine would**:
1. Measure each table
2. Calculate grid cell sizes (largest table in each row/col)
3. Position tables in grid
4. Calculate total table area dimensions
5. Position wheel and tables

### Implementation Strategy

**Phase 1** (Current): Preset layouts only
- "right", "left", "below" work as expected
- Simple stacking logic

**Phase 2** (Future): Custom grid layouts
- Add `TableLayoutConfig` to config models
- Update `_calculate_table_layout()` to handle grid mode
- Kate can test different arrangements

**Phase 3** (Maybe): Expose to users
- Add builder methods like `.with_table_grid(...)`
- Or keep internal and just ship good presets

---

# Part 6: Implementation Status

## What's Complete ✅

### Config System
- ✅ `ChartVisualizationConfig` - Immutable frozen dataclass
- ✅ `ChartWheelConfig` - Radii multipliers, theme, palettes
- ✅ `TableConfig` - Placement, padding, gaps, column widths
- ✅ `InfoCornerConfig` - Corner element configuration

### Measurement System
- ✅ `ContentMeasurer` - Measures table dimensions
- ✅ `measure_position_table()` - Variable object counts
- ✅ `measure_house_table()` - 12 houses
- ✅ `measure_aspectarian()` - Triangle vs square grids

### Layout System
- ✅ `LayoutEngine` - Complete pipeline
- ✅ `_measure_all_elements()` - Delegates to measurer
- ✅ `_calculate_table_layout()` - Stacks tables with gaps
- ✅ `_calculate_canvas_size()` - Adds wheel + tables
- ✅ `_calculate_wheel_size()` - Auto-grow logic
- ✅ `_position_wheel()` - Centers accounting for tables
- ⚠️ `_calculate_wheel_radii()` - Works but has return bug
- ✅ `_position_info_corners()` - Corner element positioning
- ✅ `_finalize_table_positions()` - Absolute coordinates

### Rendering System
- ✅ `ChartComposer` - Orchestrator pipeline
- ✅ `LayerFactory` - Creates correct layers for single/biwheel
- ✅ `ChartRenderer` - Coordinate system, polar→cartesian
- ✅ Core layers (ZodiacLayer, HouseCuspLayer, AspectLayer, PlanetLayer)
- ✅ Table layers (PositionTableLayer, HouseCuspTableLayer, AspectarianLayer)
- ✅ Adapter pattern in `_render_tables()`

### Builder API
- ✅ `ChartDrawBuilder` - Fluent API
- ✅ Wired to ChartComposer (not old draw_chart)
- ✅ Preset methods (preset_standard, preset_detailed, etc.)
- ✅ Theme/palette methods
- ✅ Table methods (.with_tables())

## What Needs Fixing ⚠️

### Critical Bugs
1. **`_calculate_wheel_radii()` return statement** (line 381-382)
   - Returns None for biwheels
   - Fix: Unindent return statement

### Config Wiring Issues
2. **Table layers don't receive config**
   - Can't access column_widths, padding, gaps
   - Fix: Pass config to table layer constructors

3. **Wheel margin not applied**
   - min_margin might not be used correctly
   - Fix: Verify LayoutEngine uses min_margin in calculations

4. **Corner element margins**
   - Corner layers might need config for sizing
   - Fix: Pass relevant config subset to corner layers

5. **Table gap might be hardcoded**
   - Fix: Ensure `_calculate_table_layout()` uses `config.tables.gap_between_tables`

### Missing Builder Methods
6. **`.with_custom_radii()`** - For custom radii multipliers
7. **`.with_table_column_widths()`** - For custom column widths
8. **`.with_wheel_margin()`** - For custom min_margin

## What's Missing 🚧

### Table Layout System
- Custom grid layouts (dev tool)
- More preset arrangements (Kate can add after testing)

### Testing
- Comprehensive test suite for layout engine
- Visual regression tests (compare SVG output)
- Edge case tests (0 aspects, 50 planets, etc.)

### Documentation
- User-facing docs for new builder API
- Internal docs for config system
- Examples showing table layouts

### Deprecation
- Mark old `draw_chart()` as deprecated
- Keep for backward compat
- Update all examples to use builder

---

# Part 7: Extension Points

## Where New Features Plug In

### Adding a New Layer

**Example**: Add a `GridLayer` to show degree grid lines

1. Create new layer class:
```python
# layers.py
class GridLayer:
    def __init__(self, interval: int = 10, color: str = "#333"):
        self.interval = interval
        self.color = color

    def render(self, renderer, dwg, chart):
        # Draw lines at 0°, 10°, 20°, ... 350°
        for angle in range(0, 360, self.interval):
            inner = renderer.radii["aspect_ring_inner"]
            outer = renderer.radii["outer_border"]

            x1, y1 = renderer.polar_to_cartesian(angle, inner)
            x2, y2 = renderer.polar_to_cartesian(angle, outer)

            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=self.color))
```

2. Add to LayerFactory:
```python
# layer_factory.py
def create_layers(self, chart, layout):
    layers = []

    # ... existing layers

    if self.config.wheel.show_grid:  # New config option
        layers.append(GridLayer(interval=10))

    return layers
```

3. Add config option:
```python
# config.py
@dataclass(frozen=True)
class ChartWheelConfig:
    # ... existing fields
    show_grid: bool = False
    grid_interval: int = 10
```

4. Add builder method:
```python
# builder.py
class ChartDrawBuilder:
    def with_grid(self, interval: int = 10):
        self._show_grid = True
        self._grid_interval = interval
        return self
```

Done! New layer integrated cleanly.

### Adding a New Table

**Example**: Add a `DignityTableLayer` for essential dignities

1. Create new layer class:
```python
# extended_canvas.py
class DignityTableLayer:
    def __init__(self, x_offset, y_offset, config):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.config = config

    def render(self, renderer, dwg, chart):
        # Draw table of planet dignities
        # ... SVG rendering code
```

2. Add to ContentMeasurer:
```python
# layout/measurer.py
def measure_dignity_table(self, chart):
    num_planets = len(chart.positions)
    num_cols = 6  # Planet, Domicile, Exaltation, Triplicity, etc.

    width = num_cols * 100 + padding * 2
    height = num_planets * 20 + padding * 2

    return Dimensions(width=width, height=height)
```

3. Add to LayoutEngine:
```python
# layout/engine.py
def _measure_all_elements(self, chart):
    measurements = {}

    # ... existing tables

    if self.config.tables.show_dignities:
        measurements["dignities"] = self.measurer.measure_dignity_table(chart)

    return measurements
```

4. Add to Composer:
```python
# composer.py
def _render_tables(self, canvas, renderer, chart, layout):
    # ... existing tables

    if self.config.tables.show_dignities and "dignities" in layout.table_positions:
        bbox = layout.table_positions["dignities"]
        dignity_layer = DignityTableLayer(
            x_offset=int(bbox.position.x),
            y_offset=int(bbox.position.y),
            config=self.config
        )
        dignity_layer.render(renderer, canvas, chart)
```

5. Add config option:
```python
# config.py
@dataclass(frozen=True)
class TableConfig:
    # ... existing fields
    show_dignities: bool = False
```

6. Add builder method:
```python
# builder.py
class ChartDrawBuilder:
    def with_dignity_table(self, enabled: bool = True):
        self._show_dignities = enabled
        return self
```

Done! New table integrated cleanly.

### Adding a New Theme

**Example**: Add a "forest" theme (green tones)

1. Add theme to registry:
```python
# themes.py
class ChartTheme(str, Enum):
    # ... existing themes
    FOREST = "forest"
```

2. Add theme style:
```python
# themes.py
THEME_STYLES = {
    # ... existing themes
    ChartTheme.FOREST: {
        "background_color": "#1A2F1A",  # Dark forest green
        "text_color": "#E8F5E8",  # Light green
        "zodiac": {
            "ring_color": "#2D5F2D",
            "glyph_color": "#A8D5A8",
        },
        "houses": {
            "line_color": "#4A7C4A",
        },
        "planets": {
            "glyph_color": "#D4E8D4",
        },
        "aspects": {
            "conjunction": "#76B476",
            "opposition": "#C44747",
            # ... more aspects
        },
    },
}
```

3. Add default palette:
```python
# themes.py
THEME_DEFAULT_PALETTES = {
    # ... existing themes
    ChartTheme.FOREST: ZodiacPalette.RAINBOW_FOREST,  # Create this too
}
```

4. Create matching zodiac palette:
```python
# palettes.py
class ZodiacPalette(str, Enum):
    # ... existing palettes
    RAINBOW_FOREST = "rainbow_forest"

PALETTE_COLORS = {
    # ... existing palettes
    ZodiacPalette.RAINBOW_FOREST: [
        "#2D5F2D",  # Aries - dark green
        "#3D7F3D",  # Taurus - medium green
        "#4D9F4D",  # Gemini - bright green
        # ... 12 colors total
    ],
}
```

Done! New theme available via `.with_theme("forest")`.

---

## Summary: The Vision

We're building a **flexible, config-driven, composable chart visualization system** that:

1. **Separates concerns** - Measure → Layout → Render pipeline
2. **Uses immutable config** - Frozen dataclasses, no spooky mutations
3. **Calculates, not hardcodes** - Dimensions based on content, not magic numbers
4. **Composes cleanly** - Each component has ONE job, testable in isolation
5. **Extends easily** - New layers, tables, themes plug in via clear interfaces
6. **Exposes beautifully** - Fluent builder API with progressive disclosure

**When we're done**, Kate will have a visualization system that:
- Handles single and biwheel charts
- Adapts to variable content (any number of objects, houses, aspects)
- Supports flexible table layouts
- Maintains beautiful theming
- Can compose into grid layouts (future)
- Is testable, debuggable, and maintainable

**The code will be clean.** The architecture will be sound. And Kate will never have to write another 1100-line monolithic rendering function again.

💙🦝✨

---

*End of Architecture Document*
