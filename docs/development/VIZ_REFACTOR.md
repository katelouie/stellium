# Visualization Refactor

## Architecture Diagram

```python
┌─────────────────────────────────────────────────────────────┐
│                      ChartComposer                          │
│  (orchestrates everything, the main entry point)            │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──> ConfigurationResolver
             │    (resolves all options, handles defaults)
             │
             ├──> LayoutEngine
             │    (calculates ALL positions before rendering)
             │    │
             │    ├──> ChartWheelLayout
             │    │    (manages wheel radii, handles single/biwheel)
             │    │
             │    ├──> InfoCornerLayout
             │    │    (positions 4 corner elements, collision detection)
             │    │
             │    ├──> TableLayout
             │    │    (positions tables, handles variable sizing)
             │    │
             │    └──> CanvasLayout
             │         (calculates final canvas size, centers everything)
             │
             ├──> ContentMeasurer
             │    (measures table dimensions before layout)
             │
             └──> LayerFactory + Renderer
                  (creates and renders layers)
```

### File Structure

```python
stellium_viz_refactor/
├── config.py          # All configuration dataclasses
├── layout/
│   ├── __init__.py
│   ├── engine.py      # Main layout calculation engine
│   ├── measurer.py    # Measures elements before layout
│   ├── wheel.py       # Wheel layout calculations
│   ├── tables.py      # Table layout calculations
│   └── corners.py     # Corner element positioning
├── composer.py        # Main orchestrator (public API)
├── renderer.py        # Rendering engine (uses layout)
└── examples/
    ├── basic_natal.py
    ├── synastry.py
    └── custom_config.py
```

# Stellium Visualization Refactor - Complete Implementation Plan

## Executive Summary

This document outlines the complete plan for finishing the visualization refactor, showing how the new config-driven architecture will integrate with the existing API while maintaining backward compatibility.

---

## 1. Current State & Architecture

### What Exists Now

```
✅ Complete:
- config.py - Configuration dataclasses
- layers.py - All rendering layers (ZodiacLayer, PlanetLayer, etc.)
- layer_factory.py - Creates layers from config
- builder.py - Fluent API for users
- themes.py - Theme system
- palettes.py - Color palette system

⚠️ Partially Complete:
- composer.py - Orchestrator (scaffold exists, missing helpers)
- layout/engine.py - Layout calculations (framework exists, methods stubbed)
- layout/measurer.py - Content measurement (estimates, needs refinement)

❌ Missing:
- Integration with existing draw_chart() API
- Table rendering in new system
- Complete layout calculations
```

### File Structure (Current & Planned)

```
stellium/visualization/
├── __init__.py                 # Public API exports
├── builder.py                  # ✅ ChartDrawBuilder (fluent API)
├── composer.py                 # ⚠️ ChartComposer (needs completion)
├── config.py                   # ✅ Configuration dataclasses
├── core.py                     # ✅ ChartRenderer (low-level renderer)
├── drawing.py                  # 🔄 draw_chart() - WILL BE REFACTORED
├── extended_canvas.py          # 🔄 Table layers - WILL BE ADAPTED
├── layer_factory.py            # ✅ Creates layers from config
├── layers.py                   # ✅ All core layers
├── moon_phase.py              # ✅ Moon phase layer
├── palettes.py                # ✅ Color palettes
├── themes.py                  # ✅ Theme system
├── grid.py                    # ✅ Grid layouts
├── reference_sheet.py         # ✅ Reference generation
│
├── layout/                    # ⚠️ Layout engine
│   ├── __init__.py
│   ├── engine.py              # Main layout orchestrator
│   └── measurer.py            # Content measurement
│
└── legacy/                    # 📦 (New - optional)
    └── old_drawing.py         # Backup of original code
```

---

## 2. The Finished Architecture

### Data Flow Diagram

```
User Code
    ↓
┌─────────────────────────────────────────────┐
│  ChartDrawBuilder (Fluent API)              │
│  chart.draw("out.svg").preset_standard()    │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  draw_chart(chart, **options)               │
│  • Converts builder options to config      │
│  • Calls ChartComposer                     │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  ChartComposer(config)                      │
│  1. Calculate layout                        │
│  2. Create canvas                           │
│  3. Create renderer                         │
│  4. Create layers                           │
│  5. Render layers                           │
│  6. Save file                               │
└──────────────────┬──────────────────────────┘
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
┌───────────────┐    ┌─────────────────┐
│ LayoutEngine  │    │ LayerFactory    │
│               │    │                 │
│ • Measure all │    │ • ZodiacLayer   │
│ • Calculate   │    │ • HouseLayer    │
│   positions   │    │ • PlanetLayer   │
│ • Size canvas │    │ • AspectLayer   │
│               │    │ • InfoLayers    │
└───────────────┘    └─────────────────┘
        ↓                     ↓
┌─────────────────────────────────────────────┐
│  ChartRenderer (low-level drawing)          │
│  • SVG primitives                           │
│  • Polar coordinates                        │
│  • Radii management                         │
└─────────────────────────────────────────────┘
        ↓
     chart.svg
```

---

## 3. Integration Strategy

### Phase 1: Complete the Layout Engine (First Priority)

**Goal**: Make `ChartComposer` fully functional

**Files to Complete**:

1. **layout/engine.py** - Implement missing methods:

   ```python
   class LayoutEngine:
       def _calculate_canvas_size(...)       # NEW
       def _position_wheel(...)              # NEW
       def _calculate_table_layout(...)      # NEW
       def _finalize_table_positions(...)    # NEW
       def _calculate_margins(...)           # NEW
   ```

2. **layout/measurer.py** - Improve measurements:

   ```python
   class ContentMeasurer:
       def measure_position_table(...)       # IMPROVE
       def measure_house_table(...)          # IMPROVE
       def measure_aspectarian(...)          # IMPROVE
       def measure_corner_element(...)       # IMPROVE
   ```

### Phase 2: Adapt Table Rendering

**Goal**: Make table layers work with new layout system

**Options**:

**Option A: Adapt Existing Tables** (Faster)

- Take `PositionTableLayer`, `HouseCuspTableLayer`, `AspectarianLayer` from `extended_canvas.py`
- Modify to accept layout positions from `LayoutEngine`
- Keep all the working table rendering logic

**Option B: Rewrite Tables** (Cleaner)

- Create new table layers that follow pure layer pattern
- Use layout engine for positioning
- Simplifies code but more work

**Recommendation**: Option A - adapt existing tables

### Phase 3: Wire Up to Existing API

**Goal**: Make `draw_chart()` use the new system internally

**Changes to drawing.py**:

```python
# drawing.py - BEFORE (current)
def draw_chart(chart, **options):
    # 300+ lines of layout logic
    # Mixed concerns
    # Hard to test
    ...

# drawing.py - AFTER (new)
def draw_chart(chart, **options):
    """
    Public API - converts options to config and delegates to composer.

    Maintains backward compatibility with existing code.
    """
    # 1. Convert legacy options to ChartVisualizationConfig
    config = _options_to_config(chart, options)

    # 2. Delegate to composer
    composer = ChartComposer(config)
    return composer.compose(chart)


def _options_to_config(chart, options) -> ChartVisualizationConfig:
    """Convert legacy draw_chart options to new config format."""
    # Map old option names to new config structure
    return ChartVisualizationConfig(
        filename=options.get('filename', 'chart.svg'),
        base_size=options.get('size', 600),
        wheel=ChartWheelConfig(
            chart_type='single',
            theme=options.get('theme'),
            zodiac_palette=options.get('zodiac_palette'),
            # ... etc
        ),
        corners=InfoCornerConfig(
            chart_info=options.get('chart_info', False),
            aspect_counts=options.get('aspect_counts', False),
            # ... etc
        ),
        tables=TableConfig(
            enabled=options.get('extended_canvas') is not None,
            placement=options.get('extended_canvas', 'right'),
            # ... etc
        ),
    )
```

---

## 4. Complete File Implementation Details

### 4.1 Completed composer.py

```python
# composer.py
class ChartComposer:
    """Main orchestrator - complete implementation."""

    def __init__(self, config: ChartVisualizationConfig):
        self.config = config
        self.layout_engine = LayoutEngine(config)
        self.layer_factory = LayerFactory(config)

    def compose(self, chart: CalculatedChart | Comparison) -> str:
        """Complete pipeline."""
        # 1. Calculate layout
        layout = self.layout_engine.calculate_layout(chart)

        # 2. Create canvas
        canvas = self._create_canvas(layout)

        # 3. Create renderer
        renderer = self._create_renderer(layout, chart)

        # 4. Create layers
        layers = self.layer_factory.create_layers(chart, layout)

        # 5. Render all layers
        for layer in layers:
            layer.render(renderer, canvas, chart)

        # 6. Render tables (if enabled)
        if self.config.tables.enabled:
            self._render_tables(canvas, renderer, chart, layout)

        # 7. Save
        canvas.save()
        return self.config.filename

    def _create_canvas(self, layout: LayoutResult) -> svgwrite.Drawing:
        """Create SVG with calculated dimensions."""
        dims = layout.canvas_dimensions
        dwg = svgwrite.Drawing(
            filename=self.config.filename,
            size=(f"{dims.width}px", f"{dims.height}px"),
            viewBox=f"0 0 {dims.width} {dims.height}",
        )
        # Add background
        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(dims.width, dims.height),
            fill=self._get_background_color(),
        ))
        return dwg

    def _create_renderer(self, layout: LayoutResult, chart) -> ChartRenderer:
        """Create renderer with calculated radii and position."""
        renderer = ChartRenderer(
            size=layout.wheel_size,
            rotation=self._get_rotation_angle(chart),
            theme=self.config.wheel.theme,
            zodiac_palette=self.config.wheel.zodiac_palette,
            aspect_palette=self.config.wheel.aspect_palette,
            planet_glyph_palette=self.config.wheel.planet_glyph_palette,
        )
        # Apply calculated values
        renderer.radii = layout.wheel_radii
        renderer.x_offset = int(layout.wheel_position.x)
        renderer.y_offset = int(layout.wheel_position.y)
        return renderer

    def _render_tables(self, canvas, renderer, chart, layout):
        """Render table layers using layout positions."""
        # Import table layers
        from stellium.visualization.extended_canvas import (
            PositionTableLayer,
            HouseCuspTableLayer,
            AspectarianLayer,
        )

        # Create and render each enabled table
        if self.config.tables.show_positions:
            table_layout = layout.tables['positions']
            layer = PositionTableLayer(
                x_offset=table_layout.position.x,
                y_offset=table_layout.position.y,
                # ... other params from config
            )
            layer.render(renderer, canvas, chart)

        # ... similar for other tables

    def _get_background_color(self) -> str:
        """Get background color from theme or default."""
        if self.config.wheel.theme:
            from stellium.visualization.themes import get_theme_style
            style = get_theme_style(self.config.wheel.theme)
            return style.get('background_color', '#FFFFFF')
        return '#FFFFFF'

    def _get_rotation_angle(self, chart) -> float:
        """Calculate chart rotation based on ASC."""
        angles = chart.get_angles() if hasattr(chart, 'get_angles') else []
        asc = next((a for a in angles if a.name == 'ASC'), None)
        return asc.longitude if asc else 0.0
```

### 4.2 Completed layout/engine.py

Key missing methods to implement:

```python
# layout/engine.py

class LayoutEngine:

    def _calculate_canvas_size(
        self,
        base_wheel_size: int,
        table_layout: TableLayoutSpec,
        measurements: dict[str, Dimensions],
    ) -> Dimensions:
        """
        Calculate required canvas size based on wheel + tables + corners.

        Logic:
        1. Start with base wheel size
        2. Add table dimensions (if placement is right/left/below)
        3. Add padding
        4. Ensure minimum space for corner elements
        """
        width = base_wheel_size
        height = base_wheel_size
        padding = self.config.min_margin * 2

        if self.config.tables.enabled:
            if self.config.tables.placement == 'right':
                width += table_layout.total_width + self.config.tables.padding
            elif self.config.tables.placement == 'left':
                width += table_layout.total_width + self.config.tables.padding
            elif self.config.tables.placement == 'below':
                height += table_layout.total_height + self.config.tables.padding

        # Add padding
        width += padding
        height += padding

        return Dimensions(width, height)

    def _position_wheel(
        self,
        canvas_dims: Dimensions,
        wheel_size: int,
        table_layout: TableLayoutSpec,
    ) -> Position:
        """
        Calculate wheel position within canvas.

        Centers the wheel, accounting for table placement.
        """
        if not self.config.tables.enabled or not self.config.auto_center:
            # Simple centering
            x = (canvas_dims.width - wheel_size) / 2
            y = (canvas_dims.height - wheel_size) / 2
            return Position(x, y)

        # Adjust for table placement
        if self.config.tables.placement == 'right':
            # Shift wheel left to center in available space
            available_width = canvas_dims.width - table_layout.total_width
            x = (available_width - wheel_size) / 2
            y = (canvas_dims.height - wheel_size) / 2
        elif self.config.tables.placement == 'left':
            # Shift wheel right
            x = table_layout.total_width + ((canvas_dims.width - table_layout.total_width - wheel_size) / 2)
            y = (canvas_dims.height - wheel_size) / 2
        elif self.config.tables.placement == 'below':
            # Shift wheel up
            x = (canvas_dims.width - wheel_size) / 2
            y = (canvas_dims.height - table_layout.total_height - wheel_size) / 2
        else:
            x = (canvas_dims.width - wheel_size) / 2
            y = (canvas_dims.height - wheel_size) / 2

        return Position(x, y)

    # ... other methods follow similar pattern
```

---

## 5. Migration Path & Backward Compatibility

### Phase-by-Phase Migration

**Phase 1: Internal Refactor (Week 1)**

- Complete layout engine
- Wire composer to draw_chart()
- **Result**: draw_chart() works exactly as before, but uses new internals
- **User Impact**: NONE - fully backward compatible

**Phase 2: Soft Launch New API (Week 2)**

- Promote ChartComposer and config system
- Add examples
- **Result**: Users can opt into new API
- **User Impact**: New features available, old code still works

**Phase 3: Deprecation (Week 3-4)**

- Add deprecation warnings to old patterns
- Update all examples to use new API
- **Result**: Gradual migration
- **User Impact**: Warnings in console, clear migration path

**Phase 4: Cleanup (Future)**

- Remove old code paths
- Simplify codebase
- **Result**: Clean, maintainable architecture

### Compatibility Matrix

| API Pattern | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------------|---------|---------|---------|---------|
| `chart.draw().save()` | ✅ | ✅ | ✅ | ✅ |
| `draw_chart(chart, **opts)` | ✅ | ✅ | ⚠️ Deprecated | ❌ Removed |
| `ChartComposer(config)` | ❌ | ✅ | ✅ | ✅ |
| Direct layer usage | ✅ | ✅ | ✅ | ✅ |

---

## 6. Usage Examples (Final State)

### Example 1: Simple Natal Chart (Backward Compatible)

```python
from stellium import Chart

# Old API - still works!
chart = Chart("1990-01-15 14:30", "New York, NY")
chart.draw("natal.svg").preset_standard().save()
```

### Example 2: Advanced Configuration (New API)

```python
from stellium import Chart
from stellium.visualization import ChartComposer, ChartVisualizationConfig
from stellium.visualization.config import ChartWheelConfig, TableConfig

chart = Chart("1990-01-15 14:30", "New York, NY")

# Create custom configuration
config = ChartVisualizationConfig(
    filename="custom.svg",
    base_size=800,
    wheel=ChartWheelConfig(
        chart_type='single',
        theme='midnight',
        zodiac_palette='rainbow_midnight',
        radii_multipliers={
            'planets': 0.30,  # Adjust planet ring
            'houses_numbers': 0.22,
        }
    ),
    tables=TableConfig(
        enabled=True,
        placement='right',
        show_positions=True,
        position_col_widths={
            'planet': 90,  # Custom column widths
            'degree': 70,
        }
    ),
    auto_center=True,
    auto_grow_wheel=True,
)

# Use composer directly
composer = ChartComposer(config)
composer.compose(chart.calculated)
```

### Example 3: Programmatic Layer Composition (Advanced)

```python
from stellium import Chart
from stellium.visualization import ChartRenderer
from stellium.visualization.layers import (
    ZodiacLayer, PlanetLayer, AspectLayer
)

chart = Chart("1990-01-15 14:30", "New York, NY")

# Manual layer composition
renderer = ChartRenderer(size=600, theme='classic')
dwg = svgwrite.Drawing('custom.svg', size=('600px', '600px'))

# Add custom layers
ZodiacLayer(palette='rainbow').render(renderer, dwg, chart.calculated)
PlanetLayer(chart.calculated.positions).render(renderer, dwg, chart.calculated)
AspectLayer().render(renderer, dwg, chart.calculated)

dwg.save()
```

---

## 7. Implementation Checklist

### Must Complete (Critical Path)

- [ ] **Complete layout/engine.py methods**
  - [ ] `_calculate_canvas_size()`
  - [ ] `_position_wheel()`
  - [ ] `_calculate_table_layout()`
  - [ ] `_finalize_table_positions()`
  - [ ] `_calculate_margins()`
  - [ ] Create `TableLayoutSpec` dataclass

- [ ] **Complete composer.py methods**
  - [ ] `_render_tables()`
  - [ ] `_get_background_color()`
  - [ ] `_get_rotation_angle()`

- [ ] **Adapt table layers**
  - [ ] Modify `PositionTableLayer` to accept layout positions
  - [ ] Modify `HouseCuspTableLayer` to accept layout positions
  - [ ] Modify `AspectarianLayer` to accept layout positions

- [ ] **Wire up drawing.py**
  - [ ] Create `_options_to_config()` converter
  - [ ] Refactor `draw_chart()` to use composer
  - [ ] Refactor `draw_comparison_chart()` to use composer

### Should Complete (Polish)

- [ ] **Improve measurer.py**
  - [ ] More accurate table measurements
  - [ ] Account for font metrics

- [ ] **Add tests**
  - [ ] Layout engine unit tests
  - [ ] Integration tests for composer
  - [ ] Regression tests for old API

- [ ] **Documentation**
  - [ ] Migration guide
  - [ ] New API examples
  - [ ] Architecture documentation

### Nice to Have (Future)

- [ ] Layout visualization tool (debug mode)
- [ ] Config validation with helpful errors
- [ ] Performance benchmarks
- [ ] Export layout as JSON

---

## 8. Success Criteria

### Phase 1 Complete When

- [ ] All existing tests pass
- [ ] `draw_chart()` produces identical output to before
- [ ] No breaking changes to public API
- [ ] Layout engine has 100% test coverage

### Phase 2 Complete When

- [ ] `ChartComposer` can be used standalone
- [ ] Documentation includes new API examples
- [ ] Config system is fully documented
- [ ] At least 3 example scripts using new API

### Phase 3 Complete When

- [ ] All examples use new API
- [ ] Deprecation warnings in place
- [ ] Migration guide published
- [ ] Old code paths clearly marked

---

## 9. Timeline Estimate

**Optimistic (Focused Work)**: 2-3 days

- Day 1: Complete layout engine
- Day 2: Wire up integration
- Day 3: Testing and polish

**Realistic (With Interruptions)**: 1 week

- Mon-Tue: Layout engine completion
- Wed-Thu: Integration and adapter code
- Fri: Testing, bug fixes, documentation

**Conservative (Part-Time)**: 2 weeks

- Week 1: Core implementation
- Week 2: Testing, refinement, docs

---

## 10. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Layout calculations wrong | Medium | High | Extensive visual tests, side-by-side comparison |
| Table rendering breaks | Low | Medium | Adapt existing code, don't rewrite |
| Performance regression | Low | Low | Benchmark before/after |
| Breaking changes | Low | High | Extensive backward compat testing |
| Scope creep | High | Medium | Stick to plan, defer nice-to-haves |

---

## 11. Decision Points

### Decision 1: Table Layer Strategy

**Options**:

- A) Adapt existing table layers (faster, safer)
- B) Rewrite table layers from scratch (cleaner, more work)

**Recommendation**: Option A
**Rationale**: Working code is valuable, cleaner architecture can come later

### Decision 2: Backward Compatibility

**Options**:

- A) Full backward compatibility (users don't notice)
- B) Breaking changes with migration guide

**Recommendation**: Option A
**Rationale**: You're the only user, but muscle memory matters

### Decision 3: Implementation Order

**Options**:

- A) Bottom-up (layout engine → composer → integration)
- B) Top-down (integration → stub missing pieces → fill in)

**Recommendation**: Option A
**Rationale**: Can test each layer independently

---

## Conclusion

This refactor will transform your visualization system from a monolithic, imperative renderer into a clean, declarative, config-driven architecture that's:

- ✅ **Testable** - Each component is pure and isolated
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Extensible** - Easy to add new features
- ✅ **Backward Compatible** - Existing code keeps working
- ✅ **Well-Documented** - Clear architecture and usage patterns

The path forward is clear, the foundation is solid, and the benefits are significant. Let's build it! 🚀
