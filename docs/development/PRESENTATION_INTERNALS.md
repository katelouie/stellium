# Presentation / Reports Internals

> 🤖 **Primarily for coding agents. Hello, Claude!** Read this before
> re-deriving the API from source. If it disagrees with the code, the code wins
> — please update the doc.

> Part of the [developer docs](./README.md). User-facing guide: [`docs/REPORTS.md`](../REPORTS.md). To add a section: [EXTENDING](./EXTENDING.md).

`ReportBuilder` assembles **sections** (data dicts) and hands them to a
**renderer** (rich/plain/markdown/html/pdf/prose). Source:
`src/stellium/presentation/`.

---

## `ReportBuilder` (fluent)

`ReportBuilder().from_chart(chart)` then chain section methods, then `.render(...)`.
Accepts `CalculatedChart`, `Comparison`, or `MultiChart` and adapts output.

**Section methods** (selection — all return `self`):
- Core: `with_chart_overview()`, `with_planet_positions(include_speed=, include_house=, house_systems=)`, `with_house_cusps(systems=)`.
- Aspects: `with_aspects(mode="all|major|minor|harmonic", include_aspectarian=, ...)`, `with_cross_aspects(...)`, `with_aspect_patterns(...)`, `with_declination_aspects(...)`.
- Midpoints: `with_midpoints(...)`, `with_midpoint_aspects(...)`, `with_midpoint_trees(...)`.
- Dignities: `with_dignities(essential="both|traditional|modern|none", ...)`, `with_dispositors(...)`, `with_fixed_stars(...)`.
- Points: `with_arabic_parts(...)`, `with_declinations()`, `with_moon_phase()`.
- Timing: `with_profections(...)`, `with_profections_wheel(...)`, `with_zodiacal_releasing(...)`, `with_zr_visualization(...)`.
- Sect rectification: `with_sect_rectification(events=, temperament=)` (fast, validated compare-hypothesis section — anchor + day/night structures + evidence); `with_sect_convergence_matrix(events=)` (heavy ~3–10 s two-lens time matrix, exploratory). Events/temperament auto-looked-up for notables (by `chart.metadata["name"]`) via the biography API; pass `events=()` for a geometry-only analysis. Backed by `stellium.rectification` (see [SUBSYSTEMS](./SUBSYSTEMS.md)).
- Transit calendar: `with_stations(end, ...)`, `with_ingresses(end, ...)`, `with_eclipses(end, ...)`.
- Meta/custom: `with_chart_image(path=None)`, `with_title(title)`, `with_section(custom_section)`.

**Presets:** `preset_minimal()`, `preset_standard()`, `preset_detailed()`,
`preset_full()`, `preset_positions_only()`, `preset_aspects_only()`,
`preset_synastry()`, `preset_transit()`, `preset_transit_calendar(end, ...)`.

**Render:**
```python
report.render(format="rich_table", file=None, show=None)
# format ∈ {rich_table, plain_table, text, prose, markdown, html, pdf}
```
`show` defaults to True for terminal formats, False for file formats.

```python
from stellium import ReportBuilder
(ReportBuilder().from_chart(chart)
    .preset_detailed()
    .render(format="markdown", file="report.md"))
```

---

## `ReportSection` protocol

```python
@property
def section_name(self) -> str: ...
def generate_data(self, chart) -> SectionData: ...
```

`generate_data` returns a `SectionData` (typed union defined in
`presentation/section_types.py`). The `"type"` key selects the shape:

| Type | Payload keys | TypedDict |
|---|---|---|
| `"table"` | `headers`, `rows` | `TableData` |
| `"key_value"` | `data` (dict) | `KeyValueData` |
| `"text"` | `text` (str) | `TextData` |
| `"svg"` | `content` (str) | `SvgData` |
| `"side_by_side_tables"` | `tables` (list) | `SideBySideTablesData` |
| `"compound"` | `sections` (list of (name, SectionData)) | `CompoundData` |

**Important:** text-type sections use the `"text"` key (not `"content"`).
The `"content"` key is reserved for SVG data. Renderers accept both as a
fallback, but new sections should use `"text"`.

**Section classes** live in `presentation/sections/` (core, aspects, dignities,
midpoints, midpoint_tree, timing, transits, misc, profection_visualization,
zr_visualization). Examples: `ChartOverviewSection`, `PlanetPositionSection`,
`AspectSection`, `AspectPatternSection`, `DignitySection`, `DispositorSection`,
`MidpointSection`, `ProfectionSection`, `ZodiacalReleasingSection`,
`StationSection`, `IngressSection`, `EclipseSection`, `MoonPhaseSection`,
`ArabicPartsSection`, `FixedStarsSection`, `SectRectificationSection`,
`SectConvergenceMatrixSection` (in `sections/rectification.py`).

Shared helpers in `sections/_utils.py`: `get_object_display`, `get_sign_glyph`,
`get_aspect_display`, `get_object_sort_key`, `get_aspect_sort_key`,
`abbreviate_house_system`.

---

## Renderers (`renderers.py`)

| Renderer | Format key | Notes |
|---|---|---|
| `RichTableRenderer` | `rich_table` | ANSI terminal; `print_report` (stdout) vs `render_report` (ANSI-stripped string) |
| `PlainTextRenderer` | `plain_table` / `text` | ASCII; no deps |
| `MarkdownRenderer` | `markdown` | GFM tables; **omits SVG sections** |
| `HTMLRenderer` | `html` | self-contained; embeds chart SVG; Noto Sans Symbols |
| `TypstRenderer` | `pdf` | Typst typesetting → bytes; requires `typst` |
| `ProseRenderer` | `prose` | natural-language; good for pasting into chat / LLM context |

---

## Gotchas
- **`side_by_side_tables` is medium-dependent.** True horizontal layout only in
  Rich terminal (`rich.columns.Columns`), Typst/PDF (`#grid`), and HTML (CSS flex,
  responsive). Markdown / plain / prose **stack vertically** — the honest rendering
  for linear-text formats. Nested inside `compound`, side-by-side is dispatched by
  the HTML and prose renderers; markdown/plain/rich compound handlers stack or fall
  through. For a *row-by-row* comparison prefer a single multi-column `"table"` — it
  renders identically everywhere.
- Sections that need a component/analyzer (patterns, dignities, fixed stars,
  Arabic Parts, midpoints, ZR) **degrade gracefully** with a setup hint if the
  required `add_component`/`add_analyzer` wasn't called on the chart.
- For Comparison/MultiChart, many sections emit `"compound"`/`"side_by_side_tables"`.
- Use absolute paths for `with_chart_image()` when targeting PDF/HTML.
- For LLM-facing text prefer `chart.to_prompt_text(...)` or `format="prose"`.
