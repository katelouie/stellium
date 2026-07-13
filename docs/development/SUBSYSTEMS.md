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
`.year(...)`/`.date_range(...)`, front matter (`with_natal_chart()`,
`with_solar_return()`, `with_profections()`, `with_zr_timeline(...)`,
`with_graphic_ephemeris(...)`), daily content (`include_natal_transits(...)`,
`include_moon_phases()`, `include_voc(...)`, `include_ingresses(...)`,
`include_stations(...)`), layout (`page_size(...)`, `week_starts_on(...)`),
then `.generate("planner.pdf")` (Typst). Events gathered by
`planner/events.py::DailyEventCollector`.

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
