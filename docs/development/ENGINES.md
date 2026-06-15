# Engines Reference

> Part of the [developer docs](./README.md). See also [CHART_BUILDING](./CHART_BUILDING.md), [EXTENDING](./EXTENDING.md).

Engines are the calculation layer. They implement Protocols from
`core/protocols.py` and are injected via `ChartBuilder.with_*()`. Import from
`stellium.engines`. Source: `src/stellium/engines/`.

---

## Protocols these implement

| Protocol | Key method | Implemented by |
|---|---|---|
| `EphemerisEngine` | `calculate_positions(datetime, location, objects, config)` | `SwissEphemerisEngine`, `MockEphemerisEngine` |
| `HouseSystemEngine` | `system_name`, `calculate_house_data(...)`, `assign_houses(...)` | `PlacidusHouses`, `WholeSignHouses`, … (18+) |
| `OrbEngine` | `get_orb_allowance(obj1, obj2, aspect_name)` | `SimpleOrbEngine`, `LuminariesOrbEngine`, `ComplexOrbEngine`, `MoietyOrbEngine` |
| `AspectEngine` | `calculate_aspects(positions, orb_engine)` | `ModernAspectEngine`, `HarmonicAspectEngine`, `DeclinationAspectEngine` |
| `CrossChartAspectEngine` | `calculate_cross_aspects(p1, p2, orb_engine)` | `CrossChartAspectEngine` |
| `DignityCalculator` | `calculate_dignities(position, sect=...)` | `TraditionalDignityCalculator` |
| `ChartAnalyzer` | `analyzer_name`, `analyze(chart)` | `AspectPatternAnalyzer`, ZR analyzer, … |

---

## Ephemeris — `ephemeris.py`
- **`SwissEphemerisEngine(ephe_path=None)`** — wraps `pyswisseph`. Computes
  ecliptic + equatorial (declination) + phase data; handles sidereal mode and
  missing-ephemeris warnings; adds South Node (opposite True Node) and Aries
  Point on request. `SWISS_EPHEMERIS_IDS` maps names→swe ids (TNOs via offset).
- **`MockEphemerisEngine`** — fixed positions for fast tests/benchmarks.

## Houses — `houses.py`
Base `SwissHouseSystemBase` (cached `swe.houses_ex`). Concrete:
`PlacidusHouses` (default), `WholeSignHouses`, `KochHouses`, `EqualHouses`,
`PorphyryHouses`, `RegiomontanusHouses`, `CampanusHouses`, `EqualMCHouses`,
`VehlowEqualHouses`, `AlcabitiusHouses`, `TopocentricHouses`, `MorinusHouses`,
`EqualVertexHouses`, `GauquelinHouses`, `HorizontalHouses`, `KrusinskiHouses`,
`AxialRotationHouses`, `APCHouses`. `calculate_house_data` returns
`(HouseCusps, [angles])` where angles are ASC, MC, DSC, IC, Vertex.

## Aspects — `aspects.py`
- **`ModernAspectEngine(config=AspectConfig)`** — pairwise; `is_applying`
  determined analytically from relative velocity; skips axis pairs.
- **`HarmonicAspectEngine(harmonic)`** — e.g. `harmonic=7` for septiles; names
  aspects `"H7"`.
- **`CrossChartAspectEngine`** — chart1 × chart2 only.
- **`DeclinationAspectEngine`** — fixed tight orb (default 1.0°); parallels
  (same hemisphere) / contraparallels (opposite).

## Orbs — `orbs.py`
- **`SimpleOrbEngine(orb_map=None, fallback_orb=2.0)`** — default; uses each
  aspect's `default_orb`.
- **`LuminariesOrbEngine`** — wider orbs for Sun/Moon.
- **`ComplexOrbEngine`** — cascading by_pair → by_planet → by_aspect → default.
- **`MoietyOrbEngine`** — traditional moiety (`"lilly"`/`"ptolemy"`), effective
  orb = mean of the two planets' full orbs; optional `minor_aspect_multiplier`.

## Dignities — `dignities.py`
- **`TraditionalDignityCalculator(decans="chaldean"|"triplicity")`** →
  `calculate_dignities(position, sect)`. Scoring: domicile +5, exaltation +4
  (+1 within 5° of exact), triplicity +3, term +2, face +1, detriment −5,
  fall −4, peregrine 0. The `DIGNITIES` dict holds rulers/exaltations/bounds/
  triplicities/decans per sign.

## Patterns — `patterns.py`
**`AspectPatternAnalyzer(stellium_min=3)`** (a `ChartAnalyzer`) →
`analyze(chart) -> list[AspectPattern]`: grand trines, T-squares, yods, grand
crosses, mystic rectangles, kites, stelliums. Results land in `metadata` and
surface via the patterns report section.

## Dispositors — `dispositors.py`
**`DispositorEngine(chart, rulership_system="traditional"|"modern", house_system=None)`**:
`planetary()` and `house_based()` → `DispositorResult` (edges, chains,
`final_dispositor`, `mutual_receptions`).

## Profections — `profections.py`
**`ProfectionEngine(chart, house_system=None, rulership="traditional"|"modern")`**
(prefers Whole Sign). Core `profect(point, units, unit_type="year")`;
convenience `annual(age, point="ASC")`, `lord_of_year(age)`,
`monthly(age, month, point)`, `multi(age, points)`, `multi_for_date(date, …)`,
`timeline(start_age, end_age, point)`. Models: `ProfectionResult`,
`MultiProfectionResult`, `ProfectionTimeline` (all re-exported from
`stellium`). Usually reached via `chart.profection(...)`.

## Fixed Stars — `fixed_stars.py`
**`SwissEphemerisFixedStarsEngine(registry=None)`**: `calculate_stars(jd, stars=None)`,
`calculate_royal_stars(jd)`, `calculate_stars_by_tier(jd, tier)` →
`list[FixedStarPosition]`. (For chart integration use the
[`FixedStarsComponent`](./COMPONENTS_AND_ANALYSIS.md).)

## Other engines
- **`directions.py`** — arc directions (solar arc, etc.).
- **`releasing.py`** — zodiacal releasing timeline (reached via
  `chart.zodiacal_releasing(...)`).
- **`voc.py`** — `calculate_voc_moon(chart, aspects="traditional"|"modern")` →
  void-of-course result (reached via `chart.voc_moon()`).
- **`search.py`** — time/longitude search primitives (crossings, ingresses,
  stations, exact aspects, angle crossings); foundation for the
  [electional](./SUBSYSTEMS.md) module and the planner.

---

## Gotchas
- House systems return **angles alongside cusps** — the builder appends those
  angles to the chart's positions.
- `DeclinationAspectEngine` ignores the `OrbEngine` (uses its own fixed orb).
- Profections default to Whole Sign even when the chart's primary system is
  Placidus — pass `house_system` to override.

See [EXTENDING.md](./EXTENDING.md) to add a new house system / orb engine /
aspect engine / analyzer.
