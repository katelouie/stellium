# Components, Analysis, IO & Caching

> Part of the [developer docs](./README.md). See also [CHART_BUILDING](./CHART_BUILDING.md), [ENGINES](./ENGINES.md).

Covers optional chart **components**, the **analysis** toolkit (DataFrames,
stats, queries, vectors), **file IO** (import natives), and the **caching**
system + utils.

---

## 1. Components (`components/`)

Components implement the `ChartComponent` protocol (`component_name` +
`calculate(...)`). Add with `ChartBuilder.add_component(...)`. Results are
either appended `CelestialPosition`s (read via `chart.get_component_result(name)`)
or written to `chart.metadata`.

| Component | `component_name` | Returns / where to read | Notable args |
|---|---|---|---|
| `ArabicPartsCalculator` | `"Arabic Parts"` | `CelestialPosition` (type `ARABIC_PART`) | `parts_to_calculate=[...]`; sect-aware formula |
| `MidpointCalculator` | `"Midpoints"` | `MidpointPosition` list (`object1`, `object2`, `is_indirect`) | `pairs=[...]`, `calculate_all=True`, `indirect=True` |
| `DignityComponent` | `"Essential Dignities"` | `metadata["dignities"]` (`planet_dignities`, `mutual_receptions`, `sect`) | `traditional`, `modern`, `receptions`, `decans` |
| `AccidentalDignityComponent` | `"Accidental Dignities"` | metadata (angular/joy/retro/cazimi scoring) | — |
| `FixedStarsComponent` | `"Fixed Stars"` | `FixedStarPosition` list | `stars=[...]`, `tier=1|2|3`, `royal_only=True` |
| `AntisciaCalculator` | `"Antiscia"` | positions (`ANTISCION`/`CONTRA_ANTISCION`) + `metadata["antiscia"]` | `orb=1.5`, `include_contra=True` |

`components/dignity.py::determine_sect(positions) -> "day"|"night"` is the sect
helper (Sun above/below horizon). Arabic Parts use day: `ASC + P2 − P1`,
night: `ASC + P1 − P2`.

```python
from stellium.components import ArabicPartsCalculator, MidpointCalculator
chart = (ChartBuilder.from_native(native)
    .add_component(ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"]))
    .add_component(MidpointCalculator(calculate_all=True))
    .calculate())
fortune = chart.get_component_result("Arabic Parts")
```

---

## 2. Analysis (`analysis/`) — requires `pandas` (`pip install -e ".[analysis]"`)

Bulk/statistical work over many charts.

- **`BatchCalculator`** (`batch.py`) — calculate many charts efficiently.
  Factories: `from_registry(category=..., verified=..., data_quality=...)`,
  `from_natives(list)`, `from_iterable(stream)`. Fluent
  `.with_house_systems(...)`, `.with_aspects()`, `.add_analyzer(...)`,
  `.with_progress(cb)`. Run `.calculate()` (generator) or `.calculate_all()`.
- **`frames.py`** — `charts_to_dataframe(charts)`, `positions_to_dataframe(charts)`,
  `aspects_to_dataframe(charts, include_declination=False)`.
- **`stats.py`** — `ChartStats(charts)`: `.element_distribution()`,
  `.sign_distribution("Sun")`, `.aspect_frequency()`, `.retrograde_frequency()`,
  `.pattern_frequency()`, `.cross_tab(a, b)`, `.summary()`.
- **`queries.py`** — `ChartQuery(charts)`: chainable `.where_sun(sign=...)`,
  `.where_moon(phase=...)`, `.where_planet(name, retrograde=...)`,
  `.where_aspect(a, b, kind, orb_max=...)`, `.where_pattern(...)`,
  `.where_element_dominant(...)`, `.where_sect(...)` → `.results()`/`.count()`/
  `.first()`/`.to_dataframe()`.
- **`vector.py`** — `ChartVectorizer().encode(chart) -> np.ndarray`,
  `similarity(a, b)` (cosine).
- **`export.py`** — `export_csv/json/parquet(charts, path, schema="charts"|"positions"|"aspects")`.

---

## 3. File IO (`io/`)

Parse external sources into `list[Native]` (re-exported from `stellium`):

- **CSV** — `parse_csv(path, mapping=None, delimiter=",")`,
  `read_csv(path, name=..., date=..., location=...)`, `CSVColumnMapping` for
  explicit column mapping. Auto-detects common headers if no mapping.
- **AAF** — `parse_aaf(path)` (Astrodienst Astrological Format).
- **DataFrame** — `parse_dataframe(df)`, `read_dataframe(df, ...)`,
  `dataframe_from_natives(natives)`.

---

## 4. Caching (`utils/cache.py`, `utils/cache_utils.py`)

File-based pickle cache with subdirs `ephemeris`, `geocoding`, `general`.

```python
from stellium.utils.cache import cached

@cached(cache_type="ephemeris")          # cache_type ∈ {"ephemeris","geocoding","general"}
def expensive(...): ...
```

- `Cache`: `.get/.set/.clear(cache_type)`, `.size()`, `.get_stats()`; default
  expiry 24h.
- Management helpers (`cache_utils.py`): `print_cache_info()`,
  `clear_ephemeris_cache()`, `clear_geocoding_cache()`, `clear_all_cache()`,
  `get_cache_stats()`. Also exposed via `stellium cache` CLI.

---

## 5. Other utils (`utils/`)

- `time.py` — `datetime_to_julian_day`, `julian_day_to_datetime`,
  `offset_julian_day`.
- `houses.py` — `find_house_for_longitude(longitude, cusps)` (handles 0/360 wrap).
- `chart_ruler.py` — `get_sign_ruler`, `get_chart_ruler`,
  `get_chart_ruler_from_chart`.
- `chart_shape.py` — `detect_chart_shape(chart)` → (Bundle/Bowl/Bucket/
  Locomotive/Seesaw/Splay/Splash, metadata).
- `progressions.py` — `calculate_progressed_datetime(natal, target, type=...)`
  (secondary/tertiary/minor), solar arc / Naibod helpers.
- `planetary_crossing.py` — `find_planetary_crossing`, `find_return_near_date`,
  `find_nth_return` (used by [returns](./SUBSYSTEMS.md)).

---

## Gotchas
- Components that store data in `metadata` return an **empty** list from
  `get_component_result` — read `chart.metadata[...]` (or the dedicated getter
  like `chart.get_dignities()`).
- Analysis/IO need optional deps (`pandas`, and `scipy` for some stats).
- Cache keys are derived from args; changing a function's signature can
  invalidate cached values — clear with `clear_all_cache()` when in doubt.
