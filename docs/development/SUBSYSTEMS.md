# Other Subsystems (Pointers)

> 🤖 **Primarily for coding agents. Hello, Claude!** Read this before
> re-deriving the API from source. If it disagrees with the code, the code wins
> — please update the doc.

> Part of the [developer docs](./README.md). These are lighter pointers — entry
> points + the file to read. For deep coverage of the core path see
> [CHART_BUILDING](./CHART_BUILDING.md), [ENGINES](./ENGINES.md),
> [VISUALIZATION_INTERNALS](./VISUALIZATION_INTERNALS.md),
> [PRESENTATION_INTERNALS](./PRESENTATION_INTERNALS.md).

---

## Multi-chart: comparison / synastry / transits / synthesis
Source: `core/comparison.py`, `core/multichart.py`, `core/multiwheel.py`,
`core/synthesis.py`.

- **`MultiChartBuilder`** (preferred) builds a frozen **`MultiChart`** of 2–4
  charts with relationships, cross-aspects, and house overlays. Access via
  `mc[0]`/`mc.inner`/`mc.outer`/`mc.natal`, `get_cross_aspects(i, j)`,
  `calculate_compatibility_score()`, `draw()`.
- **`Comparison`/`ComparisonBuilder`** and **`MultiWheel`/`MultiWheelBuilder`**
  are the older two-chart / biwheel APIs — **deprecated in favor of MultiChart**
  but still exported. Prefer `MultiChart` in new code.
- **`SynthesisBuilder` → `SynthesisChart`** computes composite (midpoint) and
  Davison (midpoint time+place) charts; `SynthesisChart` subclasses
  `CalculatedChart`, so all chart methods work.

## Returns (solar / lunar / planetary)
Source: `returns/builder.py`. **`ReturnBuilder`** factories:
`ReturnBuilder.solar(natal, year=, location=)`,
`ReturnBuilder.lunar(natal, near_date=|occurrence=)`,
`ReturnBuilder.planetary(natal, "Saturn", occurrence=|near_date=)`. Delegates
configuration to an internal `ChartBuilder`; `.calculate()` → `CalculatedChart`
with return metadata (`return_jd`, `return_datetime`, `natal_longitude`,
`return_number`).

## Sect rectification (compare-hypothesis workbench)
Source: `rectification/`. An honest, human-in-the-loop **sect** (day/night)
analysis for charts whose birth *time* is uncertain. It does **not** invert time
(the empirical study found minute-level rectification is an ill-posed inverse —
see [specs/rectification/RECTIFICATION_REPORT.md](./specs/rectification/RECTIFICATION_REPORT.md)); it recovers
the one recoverable bit — sect — at ~70% and lays out both hypotheses for
adjudication. Public API:
- **`analyze_sect(chart, *, events=None, temperament=None)`** → frozen
  `SectAnalysis`: daylight prior, calibrated `p_day` (a **baked** 2-feature
  logistic frozen from the 63-chart corpus fit — `model.BAKED_SECT_MODEL`), both
  day/night `Hypothesis` structures (sect light / out-of-sect malefic / in-sect
  benefic with dignity), Moon-band flag, event evidence (`hardship`/`fortune`
  tallies + `firdaria_convergence`), soft temperament signals, `technique_votes()`.
- **`convergence_matrix(chart, *, events=None)`** → frozen `ConvergenceMatrix`
  (heavy, ~3–10 s): the two-lens Tebbs display — Lens A structural band (distinct
  charts × solar-arc/transits/profection, from `timing.py`) + Lens B event-hook
  histogram. Whisper-level, never summed; a display, not a verdict.
- Events/temperament auto-resolve for notables via the biography API
  (`chart.metadata["name"]`); pass explicitly for anyone, or `events=()` for a
  geometry-only read. Daylight fraction is geometric (Sun declination × latitude),
  so the fast path needs no sweep. Report sections: `with_sect_rectification()`,
  `with_sect_convergence_matrix()` (see [PRESENTATION_INTERNALS](./PRESENTATION_INTERNALS.md)).

## Electional (time search)
Source: `electional/` + `engines/search.py`. **`ElectionalSearch`** (exported)
finds times satisfying conditions. Building blocks:
- `electional/predicates.py` — composable `Condition` factories
  (`is_waxing()`, `moon_phase([...])`, `not_voc()`, `sign_in(...)`,
  `is_retrograde(...)`, `is_dignified(...)`, `aspect_applying(...)`,
  `in_planetary_hour(...)`, …). Predicates can carry speed hints + window
  generators for fast hierarchical search.
- `electional/intervals.py` — `TimeWindow` + window generators
  (`waxing_windows`, `moon_sign_windows`, `retrograde_windows`, `voc_windows`,
  `aspect_exact_windows`, …) with set ops (`intersect/union/invert_windows`).
- `electional/planetary_hours.py` — Chaldean-order planetary hours
  (`get_planetary_hours_for_day`, `get_planetary_hour`).

## Planner (personalized PDF)
Source: `planner/`. **`PlannerBuilder.for_native(native)`** →
`.year(...)`/`.date_range(...)`, `.theme(...)`, front matter (`with_natal_chart()`,
`with_solar_return()`, `with_profections()`, `with_zr_timeline(...)`,
`with_graphic_ephemeris(...)`), daily content (`include_natal_transits(...)`,
`include_moon_phases()`, `include_voc(...)`, `include_ingresses(...)`,
`include_stations(...)`), layout (`page_size(...)`, `binding_margin(...)`,
`week_starts_on(...)`), then `.generate("planner.pdf")`.

**Rendering is data-driven**, like the report: `planner/contract.py::
build_planner_data` serialises to a JSON contract, and `planner/renderer.py`
compiles `typst_theme/planner.typ` with `sys_inputs={theme, data}` and the
packaged fonts. The planner reuses the report's section *kinds* (`compound`,
`key_value`, `table`, `planet_positions`, `svg`) via `engine.typ::body-of`; only
`year_overview` and `glyph_key` are planner-native, and only three components are
new Typst (`typst_theme/planner_components.typ`: `month-grid`, `week-page`,
`year-overview`). All five themes apply.

**Calendar events carry an `event_class`** (`natal` / `notable` / `mundane` /
`lunar`), set at collection time, and renderers key a colour off it from the
theme's `event-colors` palette. This is the difference between a scannable day and
a wall of glyphs. Note the palette is **semantic, not structural**: it does NOT
reuse `accent`/`ink`, because those are neighbouring dark tones in several themes
(ΔE 5.9 in *house*) — see `tests/test_typst_theme_palettes.py`, which enforces that
the four classes stay ≥15 ΔE apart and ≥3:1 against the page in every theme.

**The Moon is quieted by default.** The transiting Moon aspects every natal planet
every month — 68% of all natal transit lines, measured — so it contributes
**conjunctions only** unless you pass `moon_natal_aspects` / `moon_aspects`. The
same rule applies to mundane transits.

**Two data layers, by scope:**
- `planner/events.py::DailyEventCollector` — *day*-scoped. Transits, ingresses,
  stations, Moon phases, VOC, eclipses → `DailyEvent` per day. Its glyph maps are
  derived from `CELESTIAL_REGISTRY` / `ASPECT_REGISTRY` / `DIGNITIES`. Note
  `ASPECT_GLYPHS` is angle-keyed and **excludes declination aspects** (Parallel is
  0°, Contraparallel 180°, so they would collide with Conjunction/Opposition);
  use `ASPECT_GLYPHS_BY_NAME` when you have a name.
- `planner/almanac.py::build_year_almanac` — *year*-scoped, feeding the front
  matter's reference pages: `YearAlmanac` (profection + Lord of the Year, solar
  return, eclipses **with the natal house each falls in**, retrograde windows
  clipped to the year, the progressed Moon and its dated natal aspects,
  year-defining outer transits, ZR periods active this year, plus the sky-event
  pages: `ingresses`, `stations`, `lunations`). Requires a chart built with
  `ZodiacalReleasingAnalyzer` for the ZR part (it reads analyzer metadata;
  otherwise it returns `[]`).

  The organizing idea: **every sky event carries what it touches in the chart**.
  `natal_contacts_at(chart, jd)` reads transiting longitudes straight from the
  ephemeris (a chart build per event would dominate runtime) and is what lets a
  lunation say *"…and it squares your natal Saturn"*. Stations also carry the
  **retrograde shadow**, which is computed by *pairing* stations: a planet enters
  shadow when it first crosses the degree it will later station **direct** at, and
  leaves it when it climbs back to the degree it stationed **retrograde** at. Using
  a station's own degree trivially returns the station's own date.

  `find_chart_condition(chart)` gives the traditional condition (sect; domicile,
  exaltation, bound, triplicity and decan lords per planet). It stops short of
  bonification/maltreatment, which Stellium does not model.

`TransitHit` / `find_natal_transits()` is the shared primitive behind both — run
it once and pass the result into `build_year_almanac(transits=...)` so the
longitude-crossing search doesn't happen twice.

**Design note.** The front matter is a *reference section*, not an overture: a
report is a portrait (read once), a planner is an instrument (consulted daily).
It is ordered "this year → your chart → how to read it", the natal chart leads
with a **positions table** rather than the wheel, and it is curated on by default
(opt out with `.without_*()`).

## Chinese astrology (BaZi / Four Pillars)
Source: `chinese/`. Reach it via **`chart.bazi()`** or
**`ChartBuilder...bazi()`**, or directly with `BaZiEngine(timezone_offset_hours)
.calculate(birth_datetime) -> BaZiChart`.
- Primitives (`chinese/core.py`): `Polarity`, `Element` (Wu Xing + generation/
  control cycles), `HeavenlyStem` (10), `EarthlyBranch` (12, with hidden stems).
- Models (`chinese/bazi/models.py`): `Pillar`, `BaZiChart` (`year/month/day/hour`,
  `day_master`, `element_counts(include_hidden=)`, `to_dict()`, `display()`).
- Analysis: `chinese/bazi/analysis.py` (`TenGod`, `analyze_ten_gods`),
  `chinese/bazi/strength.py` (`DayMasterStrength`).
- Calendar (`chinese/calendar.py`): `SolarTerm`, `SolarTermEngine` (BaZi year
  starts at Li Chun 315°, not Jan 1).
- Render: `chinese/bazi/renderers.py::BaziRichRenderer`.
- **Zi Wei Dou Shu** (`chinese/ziwei/`) is **planned / not yet implemented**.

> BaZi gotcha: `BaZiEngine` takes **local** birth time and applies the timezone
> offset as a negative value (PST = −8). Month is determined by solar term, not
> the lunar month; hidden stems drive strength analysis.

## CLI
Source: `cli/`. Entry point `stellium = "stellium.cli:cli"` (`pyproject.toml`).
- `stellium chart from-registry NAME [--output PATH --house-system ... --format svg|terminal|json]`
- `stellium ephemeris download [--years START-END --force --quiet]`;
  `stellium ephemeris download-asteroid <ids>|--tnos [--list --force]`
- `stellium cache ...` (cache management; see
  [COMPONENTS_AND_ANALYSIS](./COMPONENTS_AND_ANALYSIS.md#4-caching-utilscachepy))

## Progressions & directions
- Secondary/tertiary/minor progressions: `utils/progressions.py` (+
  `chart` helpers). Arc directions: `engines/directions.py`. Zodiacal releasing:
  `engines/releasing.py` via `chart.zodiacal_releasing(...)`.
