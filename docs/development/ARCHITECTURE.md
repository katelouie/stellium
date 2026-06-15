# Architecture (Agent Orientation)

> Part of the [developer docs](./README.md). Hub: [`/CLAUDE.md`](../../CLAUDE.md) · Index: [`docs/DOCS_INDEX.md`](../DOCS_INDEX.md)

This is the map an agent should read first. It explains *how the pieces fit*
so you can find the right file fast. For per-subsystem API detail, follow the
links to the other spokes.

---

## The one-paragraph mental model

Stellium turns birth data into an **immutable result object** and then renders
it. You configure a **`ChartBuilder`** (fluent, lazy), call `.calculate()`, and
get back a frozen **`CalculatedChart`**. Calculation is performed by pluggable
**engines** (ephemeris, houses, aspects, orbs) selected via Protocols;
optional **components** and **analyzers** add extra data (Arabic Parts,
midpoints, dignities, patterns). The chart then feeds **visualization**
(`chart.draw(...)` → SVG), **presentation** (`ReportBuilder` → terminal /
markdown / PDF), **export** (`to_dict`, analysis DataFrames), and **timing
transforms** (profections, zodiacal releasing, returns, progressions).

```
Native/Notable ─► ChartBuilder ──.calculate()──► CalculatedChart ─┬─► chart.draw(...)      (SVG)
   (birth data)   (config, lazy)   (engines +     (frozen)        ├─► ReportBuilder        (report)
                                    components +                    ├─► chart.to_dict()      (JSON)
                                    analyzers)                      ├─► analysis.* / io.*    (DataFrames)
                                                                    └─► profection()/zodiacal_releasing()/returns
```

---

## Three principles (these are load-bearing, not slogans)

1. **Protocols over inheritance.** Engines/components implement a `Protocol`
   from `core/protocols.py` by matching method signatures — no base class. To
   add behavior you write a class with the right methods and inject it.
2. **Immutability.** Every result model is a `@dataclass(frozen=True)`. Mutate
   with `dataclasses.replace(obj, field=...)`, never in place.
3. **Composability + lazy evaluation.** `ChartBuilder.with_*()/add_*()` just
   record config and return `self`. Nothing is computed until `.calculate()`.

## Dependency direction (do not violate)

```
core/   ─► (depends on nothing internal)
engines/, components/, electional/, returns/, io/, analysis/, chinese/  ─► core
presentation/, visualization/, planner/  ─► core, engines, components
```

`core/` must **never** import from `engines/`, `components/`, etc.
`core/chart_utils.py` deliberately uses duck-typing to inspect chart types
without importing the higher layers — follow that pattern if you need it.

---

## Layer-by-layer (where to look)

| Layer | Package | What lives here | Deep-dive doc |
|---|---|---|---|
| **Core models** | `core/models.py` | Frozen dataclasses: `CelestialPosition`, `HouseCusps`, `Aspect`, `AspectPattern`, `CalculatedChart`, `UnknownTimeChart`, `MultiChart`, `FixedStarPosition` | [CHART_BUILDING](./CHART_BUILDING.md) |
| **Interfaces** | `core/protocols.py` | All `Protocol`s: `EphemerisEngine`, `HouseSystemEngine`, `AspectEngine`, `OrbEngine`, `ChartComponent`, `ChartAnalyzer`, `ReportSection`, `IRenderLayer`, … | [EXTENDING](./EXTENDING.md) |
| **Builder / API** | `core/builder.py` | `ChartBuilder` (the main entry point) | [CHART_BUILDING](./CHART_BUILDING.md) |
| **Birth data** | `core/native.py` | `Native`, `Notable` (parsing, geocoding, timezone) | [CHART_BUILDING](./CHART_BUILDING.md) |
| **Config** | `core/config.py`, `core/ayanamsa.py` | `CalculationConfig`, `AspectConfig`, `ZodiacType`, ayanamsa registry | [CHART_BUILDING](./CHART_BUILDING.md) |
| **Registries** | `core/registry.py` | `CELESTIAL_REGISTRY`, `ASPECT_REGISTRY`, `FIXED_STARS_REGISTRY` | [CHART_BUILDING](./CHART_BUILDING.md) |
| **Multi-chart** | `core/comparison.py`, `core/multichart.py`, `core/multiwheel.py`, `core/synthesis.py` | Synastry/transits/composite/Davison containers | [SUBSYSTEMS](./SUBSYSTEMS.md) |
| **Engines** | `engines/` | Calculation: ephemeris, houses, aspects, orbs, dignities, patterns, dispositors, profections, releasing, directions, voc, fixed_stars, search | [ENGINES](./ENGINES.md) |
| **Components** | `components/` | Optional add-ons: arabic_parts, midpoints, dignity, fixed_stars, antiscia | [COMPONENTS_AND_ANALYSIS](./COMPONENTS_AND_ANALYSIS.md) |
| **Analysis / IO** | `analysis/`, `io/` | Batch, DataFrames, stats, queries, vectors; CSV/AAF/DataFrame import | [COMPONENTS_AND_ANALYSIS](./COMPONENTS_AND_ANALYSIS.md) |
| **Timing** | `returns/`, `electional/`, `engines/profections.py`, `engines/releasing.py`, `utils/progressions.py` | Returns, electional search, profections, ZR, progressions | [SUBSYSTEMS](./SUBSYSTEMS.md) |
| **Visualization** | `visualization/` | SVG: builder→composer→layers; themes/palettes; dial, vedic, atlas | [VISUALIZATION_INTERNALS](./VISUALIZATION_INTERNALS.md) |
| **Presentation** | `presentation/` | `ReportBuilder`, sections, renderers (rich/markdown/html/pdf/prose) | [PRESENTATION_INTERNALS](./PRESENTATION_INTERNALS.md) |
| **Planner** | `planner/` | Personalized PDF planners (Typst) | [SUBSYSTEMS](./SUBSYSTEMS.md) |
| **Chinese** | `chinese/` | BaZi (Four Pillars); Zi Wei (planned) | [SUBSYSTEMS](./SUBSYSTEMS.md) |
| **CLI** | `cli/` | `stellium` command (`chart`, `ephemeris`, `cache`) | [SUBSYSTEMS](./SUBSYSTEMS.md) |
| **Utils** | `utils/` | Caching, time/JD, chart shape, chart ruler, progressions, crossings | [COMPONENTS_AND_ANALYSIS](./COMPONENTS_AND_ANALYSIS.md) |

---

## What `.calculate()` actually does

Reading this once saves you from guessing why a field is empty. From
`core/builder.py::calculate()`:

1. Resolve the object list from `CalculationConfig` (heliocentric mode removes
   Sun/nodes/apogees and adds Earth).
2. Ephemeris → `list[CelestialPosition]` (ecliptic + equatorial for declination
   + phase data).
3. For each configured house system: compute cusps **and** angles
   (ASC/MC/DSC/IC/Vertex). Angles are appended to the positions list.
4. Assign house placements for every system.
5. Run **components** in order — each returns extra `CelestialPosition`s that
   are appended (or writes to `metadata`).
6. Compute aspects, then declination aspects (if enabled).
7. Run **analyzers** against a provisional chart — they populate `metadata`
   (e.g. aspect patterns, zodiacal releasing).
8. Build the final frozen `CalculatedChart` (with component manifest, ayanamsa
   value if sidereal, tags).

Implications:
- **Components add positions; analyzers add metadata.** Access them via
  `chart.get_component_result(name)` and the dedicated getters.
- Unknown-time charts (`with_unknown_time()`) skip houses/angles and return an
  `UnknownTimeChart` with a `moon_range` instead.

---

## Conventions worth memorizing

- **Longitudes are 0–360°**, always normalized; wraparound at 0°/360° is
  handled explicitly (see `utils/houses.py::find_house_for_longitude`).
- **All internal time is UTC Julian Day**; convert to local only at display.
  Helpers in `utils/time.py`.
- **Retrograde** = `speed_longitude < 0`; |speed| below a small epsilon is
  treated as stationary (no applying/separating verdict).
- **Sect-aware** logic (Arabic Parts, some dignities) flips by day/night chart;
  see `chart.sect` and `components/dignity.py::determine_sect`.
- **One aspect per pair**; axis pairs (ASC/DSC, MC/IC, Node/South Node) are
  excluded from normal aspects.
- **Whole Sign is preferred** for profections; **Placidus** is the default
  house system everywhere else.

See [EXTENDING.md](./EXTENDING.md) for how to plug in new engines, components,
analyzers, layers, themes, palettes, and report sections.
