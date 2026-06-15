# Visualization Internals

> 🤖 **Primarily for coding agents. Hello, Claude!** Read this before
> re-deriving the API from source. If it disagrees with the code, the code wins
> — please update the doc.

> Part of the [developer docs](./README.md). User-facing guide: [`docs/VISUALIZATION.md`](../VISUALIZATION.md), galleries: [`docs/THEME_GALLERY.md`](../THEME_GALLERY.md) / [`docs/PALETTE_GALLERY.md`](../PALETTE_GALLERY.md). To add layers/themes: [EXTENDING](./EXTENDING.md).

How SVG rendering actually works, for agents modifying it. Source:
`src/stellium/visualization/`.

---

## Pipeline

`chart.draw(filename)` → **`ChartDrawBuilder`** (fluent config) →
`.save()` → **`ChartComposer.compose()`**:

1. `LayoutEngine.calculate_layout(chart)` → radii + canvas dims.
2. Create SVG canvas (`svgwrite`).
3. Create **`ChartRenderer`** (coordinate context with computed radii).
4. `LayerFactory.create_layers(chart, layout)` → ordered `IRenderLayer` list.
5. Render each layer; then extended tables if enabled.
6. Save file or return SVG string.

Files: `builder.py` (ChartDrawBuilder), `composer.py` (ChartComposer),
`core.py` (ChartRenderer + `IRenderLayer`), `config.py`
(`ChartVisualizationConfig`), `layer_factory.py`, `layout/engine.py`,
`layout/measurer.py`.

---

## `ChartDrawBuilder` (the public knobs)

All return `self`; finish with `.save(to_string=False) -> str`.

- **Sizing/theme:** `with_size(int)`, `with_theme(name)`, `with_margin(int)`.
- **Palettes:** `with_zodiac_palette(name|bool)`, `with_aspect_palette(name)`,
  `with_planet_glyph_palette(name)`, `with_adaptive_colors(bool)`.
- **Detail:** `with_degree_ticks(bool)`, `with_planet_ticks(bool)`,
  `with_house_systems(str|list)`.
- **Decorations:** `with_header(height)`/`without_header()`,
  `with_moon_phase(position, show_label, size, label_size)`/`without_moon_phase()`,
  `with_chart_info(position, fields)`, `with_aspect_counts(position)`,
  `with_element_modality_table(position)`, `with_chart_shape(position)`.
- **Extended canvas/tables:** `with_tables(position, show_position_table,
  show_aspectarian, ...)`.
- **Presets:** `preset_minimal()`, `preset_standard()`, `preset_detailed()`,
  `preset_synastry()`.

```python
(chart.draw("natal.svg")
    .with_theme("midnight")
    .with_zodiac_palette("rainbow")
    .preset_detailed()
    .save())
```

---

## `ChartRenderer` — the coordinate system (read before touching geometry)

```python
ChartRenderer(size=600, rotation=0.0, theme=None, style_config=None,
              zodiac_palette=None, aspect_palette=None,
              planet_glyph_palette=None, color_sign_info=False)
```

- **Astrological 0° = Aries**; the chart is drawn with **0° Aries at 9 o'clock**
  and rotates **counter-clockwise**.
- `rotation` = the ASC longitude (set by the composer) so ASC lands on the left.
- Convert with `astrological_to_svg_angle(deg)` and
  `polar_to_cartesian(astro_deg, radius)` — the latter accounts for
  `x_offset`/`y_offset` (extended canvas) and `header_height`.
- `radii: dict[str,float]` (set by `LayoutEngine`), `style: dict` (theme-derived
  colors/fonts/line widths).

---

## `IRenderLayer` and the built-in layers

```python
class IRenderLayer(Protocol):
    def render(self, renderer, dwg, chart) -> None: ...
```

`LayerFactory` builds the list and renders **bottom→top**: Header → Zodiac →
Houses (+ overlays) → Ring boundaries (multiwheel) → Angles → Aspects →
Planets → Moon range/phase → Info corners → Outer border.

Layer classes (in `layers/`): `ZodiacLayer`, `HouseCuspLayer` /
`OuterHouseCuspLayer`, `AngleLayer` / `OuterAngleLayer`, `AspectLayer` /
`MultiWheelAspectLayer`, `PlanetLayer` (with collision detection),
`MoonPhaseLayer`, `MoonRangeLayer`, `ChartInfoLayer`, `AspectCountsLayer`,
`ElementModalityTableLayer`, `ChartShapeLayer`, `HeaderLayer`,
`OuterBorderLayer`, `RingBoundaryLayer`, plus extended-canvas tables
(`PositionTableLayer`, `HouseCuspTableLayer`, `AspectarianLayer`).

---

## Themes & palettes

- **Themes** (`themes.py`, `ChartTheme` enum): classic (default), dark,
  midnight, neon, sepia, pastel, celestial, atlas, plus data-science maps
  viridis/plasma/inferno/magma/cividis/turbo. `get_theme_style(theme)` returns
  the full style dict; `get_theme_default_palette/_aspect_palette/_planet_palette`
  give defaults.
- **Zodiac palettes** (`palettes.py`, `ZodiacPalette`): grey, rainbow (+ theme
  variants), elemental (+ variants), cardinality, and the data-science maps;
  also `"single_color:#RRGGBB"`. `get_palette_colors(palette)` → 12 hex colors.
- **Aspect palettes** (`AspectPalette`): `get_aspect_palette_colors()` →
  `{aspect_name: hex}`.
- **Planet glyph palettes** (`PlanetGlyphPalette`): default/element/chakra/
  rainbow + data-science; `get_planet_glyph_color(palette, name)`.

---

## Specialized renderers

| What | Entry point | Files |
|---|---|---|
| **Dial** (90°/45°/360°) | `chart.draw_dial(filename, degrees=90)` → `DialBuilder` | `dial/` |
| **Vedic** | `chart.draw_vedic(filename, style="north_indian"\|"south_indian")` | `vedic/north_indian.py`, `vedic/south_indian.py` |
| **Atlas (multi-chart PDF)** | `AtlasBuilder(entries, config).render_pdf()` (Typst) | `atlas/` |
| **Graphic ephemeris** | `EphemerisLayer` | `ephemeris.py` |
| **Moon phase / reference sheet** | layers | `moon_phase.py`, `reference_sheet.py` |
| **Multiwheel** | `multichart.draw(...)` / `comparison.draw(...)` | layers + composer |

Vedic note: North Indian fixes **houses** (House 1 at top diamond) and rotates
signs; South Indian fixes **signs** in a 4×4 grid and places planets by sign.

---

## Gotchas
- Multiwheel auto-scales canvas (bi 1.0× / tri 1.15× / quad 1.3×) and shrinks
  glyphs per chart count.
- `PlanetLayer` displaces colliding glyphs outward with a connector to the true
  position tick.
- Markdown report output omits SVG sections; HTML/PDF embed them and assume the
  Noto Sans Symbols font for glyphs.
- Unknown-time charts render a `MoonRangeLayer` arc instead of houses/angles.
- Extended-canvas tables render **after** wheel layers via the composer, not in
  the normal layer loop.
