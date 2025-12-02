# MultiWheel Chart System Implementation Plan

## Overview

Build a unified MultiWheel chart system for Stellium that supports 2, 3, or 4 charts rendered concentrically **INSIDE** the zodiac ring. This replaces and unifies the current biwheel implementation.

**Key Design Decisions:**
- **Unify with Comparison**: `Comparison.draw()` will internally use the new MultiWheel rendering system
- **All charts inside zodiac**: Breaking change - both old biwheels and new multiwheels render inside
- **Compact info stacks**: Show only degree (e.g., "15°") without sign glyph or speed
- **No aspect lines**: Center is minimal; use aspectarian table instead

## Ring Order (center → out)

```
┌─────────────────────────────────────────┐
│            ZODIAC RING (outer)          │
│  ┌───────────────────────────────────┐  │
│  │     Chart N ring (houses+obj)     │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   ...middle charts...       │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │ Chart 1 (houses+obj)  │  │  │  │
│  │  │  │  ┌─────────────────┐  │  │  │  │
│  │  │  │  │  (tiny center)  │  │  │  │  │
│  │  │  │  └─────────────────┘  │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

Each chart ring includes:
- Alternating house fills (theme-colored per chart)
- House divider lines (full ring width)
- Planet glyphs with compact info (degree only)
- Position ticks on ring's inner rim

---

## API Design

```python
from stellium import ChartBuilder, MultiWheelBuilder

# Calculate charts
natal = ChartBuilder.from_notable("Albert Einstein").calculate()
transit = ChartBuilder.from_details("2025-01-06 12:00", natal.location).calculate()
progressed = ChartBuilder.from_details("1926-03-14 12:00", natal.location).calculate()

# Create multiwheel (2-4 charts)
multiwheel = (MultiWheelBuilder
    .from_charts([natal, transit, progressed])
    .with_labels(["Natal", "Transit", "Progressed"])
    .calculate())

# Draw
multiwheel.draw("triwheel.svg").preset_multiwheel().save()

# Existing Comparison also uses new system internally
synastry = ComparisonBuilder.synastry(chart1, chart2).calculate()
synastry.draw("synastry.svg").save()  # Now renders both inside zodiac
```

---

## Implementation Phases

### Phase 1: Core Data Structure

**New File**: `src/stellium/core/multiwheel.py`

```python
@dataclass(frozen=True)
class MultiWheel:
    """Multi-chart comparison supporting 2-4 charts rendered concentrically."""
    charts: tuple[CalculatedChart, ...]  # 2-4 charts
    labels: tuple[str, ...] = ()
    cross_aspects: dict[tuple[int, int], tuple[ComparisonAspect, ...]] = field(default_factory=dict)

    @property
    def chart_count(self) -> int:
        return len(self.charts)

    def draw(self, filename: str = "multiwheel.svg") -> "ChartDrawBuilder":
        from stellium.visualization.builder import ChartDrawBuilder
        return ChartDrawBuilder(self).with_filename(filename)


class MultiWheelBuilder:
    """Fluent builder for MultiWheel objects."""

    @classmethod
    def from_charts(cls, charts: list[CalculatedChart]) -> "MultiWheelBuilder": ...

    def with_labels(self, labels: list[str]) -> "MultiWheelBuilder": ...
    def with_cross_aspects(self) -> "MultiWheelBuilder": ...
    def calculate(self) -> MultiWheel: ...
```

### Phase 2: Configuration - Hard-Set Radii

**File**: `src/stellium/visualization/config.py`

Add multiwheel radii configurations (proportions of wheel_size):

```python
multiwheel_2_radii: dict[str, float] = {
    # Zodiac ring (outermost)
    "zodiac_ring_outer": 0.50,
    "zodiac_ring_inner": 0.42,
    # Chart 2 ring
    "chart2_ring_outer": 0.42,
    "chart2_ring_inner": 0.28,
    "chart2_planet_ring": 0.35,
    "chart2_house_number": 0.30,
    # Chart 1 ring (innermost)
    "chart1_ring_outer": 0.28,
    "chart1_ring_inner": 0.14,
    "chart1_planet_ring": 0.21,
    "chart1_house_number": 0.16,
    # Aspect center (minimal)
    "aspect_ring_inner": 0.08,
}

multiwheel_3_radii: dict[str, float] = { ... }  # Tighter spacing
multiwheel_4_radii: dict[str, float] = { ... }  # Tightest spacing
```

### Phase 3: Theme Colors

**File**: `src/stellium/visualization/themes.py`

Add to each theme:

```python
"planets": {
    "chart1_color": "#222222",   # Inner (default)
    "chart2_color": "#4A90E2",   # Blue
    "chart3_color": "#27AE60",   # Green
    "chart4_color": "#9B59B6",   # Purple
},
"houses": {
    "chart1_fill_1": "#F5F5F5",
    "chart1_fill_2": "#FFFFFF",
    "chart2_fill_1": "#E8F4FC",
    "chart2_fill_2": "#F5FAFD",
    "chart3_fill_1": "#E8F8EE",
    "chart3_fill_2": "#F5FBF7",
    "chart4_fill_1": "#F3EBF8",
    "chart4_fill_2": "#FAF6FC",
}
```

### Phase 4: Unified Layer Architecture

**File**: `src/stellium/visualization/layers.py`

Refactor `HouseCuspLayer` with `wheel_index` parameter (replacing separate `OuterHouseCuspLayer`):

```python
class HouseCuspLayer:
    def __init__(
        self,
        house_system_name: str,
        wheel_index: int = 0,  # Which chart ring (0=innermost)
        chart: CalculatedChart | None = None,
    ):
        self.wheel_index = wheel_index
        # ...

    def render(self, renderer, dwg, chart):
        # Get radii for this wheel
        prefix = f"chart{self.wheel_index + 1}"
        ring_outer = renderer.radii[f"{prefix}_ring_outer"]
        ring_inner = renderer.radii[f"{prefix}_ring_inner"]

        # Get fill colors for this wheel
        fill_1 = renderer.style["houses"][f"{prefix}_fill_1"]
        fill_2 = renderer.style["houses"][f"{prefix}_fill_2"]

        # Draw alternating fills spanning ring_inner → ring_outer
        # Draw house dividers spanning ring_inner → ring_outer
        # Draw house numbers at house_number radius
```

Similarly update `PlanetLayer` and `AngleLayer` with `wheel_index`.

### Phase 5: Layer Factory

**File**: `src/stellium/visualization/layer_factory.py`

```python
def create_layers(self, chart: CalculatedChart | Comparison | MultiWheel, ...):
    is_multiwheel = isinstance(chart, MultiWheel)
    is_comparison = isinstance(chart, Comparison)

    # For Comparison, treat as 2-chart MultiWheel
    if is_comparison:
        charts = [chart.chart1, chart.chart2]
        chart_count = 2
    elif is_multiwheel:
        charts = list(chart.charts)
        chart_count = chart.chart_count
    else:
        charts = [chart]
        chart_count = 1

    layers = []

    # Zodiac (always outermost)
    layers.append(ZodiacLayer(...))

    # For multi-chart: render rings from outer to inner
    if chart_count > 1:
        for i in range(chart_count - 1, -1, -1):  # Reverse order
            layers.append(HouseCuspLayer(wheel_index=i, chart=charts[i], ...))
            layers.append(AngleLayer(wheel_index=i, chart=charts[i]))
            layers.append(PlanetLayer(
                wheel_index=i,
                planet_set=self._get_planets(charts[i]),
                glyph_color=self._get_chart_color(i),
                info_mode="compact",  # Degree only
            ))

    # No AspectLayer for multiwheel (too cluttered)

    return layers
```

### Phase 6: Layout Engine

**File**: `src/stellium/visualization/layout/engine.py`

```python
def _calculate_wheel_radii(self, wheel_size: int, chart) -> dict[str, float]:
    if isinstance(chart, MultiWheel):
        radii_config = {
            2: self.config.wheel.multiwheel_2_radii,
            3: self.config.wheel.multiwheel_3_radii,
            4: self.config.wheel.multiwheel_4_radii,
        }[chart.chart_count]
    elif isinstance(chart, Comparison):
        radii_config = self.config.wheel.multiwheel_2_radii  # Use new system!
    else:
        radii_config = self.config.wheel.single_radii

    return {key: wheel_size * mult for key, mult in radii_config.items()}
```

### Phase 7: Canvas & Glyph Scaling

```python
# In layout engine - grow canvas
if isinstance(chart, MultiWheel):
    scale = 1.0 + (chart.chart_count - 2) * 0.15  # 1.0, 1.15, 1.30
    wheel_size = int(base_wheel_size * scale)

# In PlanetLayer - shrink glyphs
glyph_scale = {1: 1.0, 2: 0.85, 3: 0.70, 4: 0.60}.get(chart_count, 0.60)
```

### Phase 8: Compact Info Stacks

**File**: `src/stellium/visualization/layers.py` (PlanetLayer)

Add `info_mode` parameter:
- `"full"`: Degree + sign glyph + speed (current behavior)
- `"compact"`: Degree only (e.g., "15°")
- `"none"`: No info stack

For multiwheel, default to `"compact"`.

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/stellium/core/multiwheel.py` | NEW: MultiWheel, MultiWheelBuilder |
| `src/stellium/core/__init__.py` | Export MultiWheel, MultiWheelBuilder |
| `src/stellium/__init__.py` | Export MultiWheel, MultiWheelBuilder |
| `src/stellium/visualization/config.py` | Add multiwheel_2/3/4_radii |
| `src/stellium/visualization/themes.py` | Add chart1-4 colors to all themes |
| `src/stellium/visualization/layers.py` | Add wheel_index to layers, compact info mode |
| `src/stellium/visualization/layer_factory.py` | Handle MultiWheel, loop over charts |
| `src/stellium/visualization/layout/engine.py` | Select radii, scale canvas |
| `src/stellium/visualization/builder.py` | Add preset_multiwheel() |

## Files to Delete/Deprecate

| File/Code | Action |
|-----------|--------|
| `OuterHouseCuspLayer` | Replace with HouseCuspLayer(wheel_index=1) |
| `OuterAngleLayer` | Replace with AngleLayer(wheel_index=1) |
| `OuterBorderLayer` | May no longer be needed |
| `biwheel_radii` in config | Replace with multiwheel_2_radii |

---

## Testing Strategy

1. **Unit Tests** (`tests/test_multiwheel.py`):
   - MultiWheel creation with 2, 3, 4 charts
   - Validation (rejects 1 or 5+ charts)
   - Labels auto-generation

2. **Integration Tests**:
   - Generate SVGs for 2, 3, 4 chart multiwheels
   - Verify all rings inside zodiac
   - Verify existing Comparison.draw() still works (now uses new system)

3. **Visual Verification**:
   - Render example multiwheels with different themes
   - Check glyph readability at each chart count
   - Verify house fills and dividers per ring

---

## Breaking Changes

1. **Biwheels now render inside zodiac** - existing synastry/transit charts will look different
2. **OuterHouseCuspLayer deprecated** - code using it directly will break
3. **biwheel_radii replaced** - code referencing these keys needs update

---

## Implementation Order

1. Create `MultiWheel` and `MultiWheelBuilder` classes
2. Add multiwheel radii configs
3. Add theme colors for chart1-4
4. Refactor HouseCuspLayer with wheel_index
5. Refactor PlanetLayer with wheel_index and compact info
6. Refactor AngleLayer with wheel_index
7. Update LayerFactory to handle MultiWheel
8. Update LayoutEngine for radii selection and canvas scaling
9. Update Comparison.draw() to use new system
10. Remove OuterHouseCuspLayer, OuterAngleLayer
11. Add preset_multiwheel() to builder
12. Write tests
13. Update exports
