# Components, Analysis, IO & Caching

> 🤖 **Primarily for coding agents. Hello, Claude!** Read this before
> re-deriving the API from source. If it disagrees with the code, the code wins
> — please update the doc.

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

File-based pickle cache. **In practice this now means geocoding only.**

> ⚠️ **Do not disk-cache the ephemeris.** A `swe.calc_ut` takes microseconds; a
> pickle round-trip does not. Caching positions to disk measured **13× slower**
> than recomputing them (2.4 ms/chart → 0.21 ms/chart when removed). `@cached` is
> for calls that are slow because they *leave the process* — a network request.
> Before adding it, check that the thing you are caching is slower than a file read.

> ⚠️ **Never put `@cached` on a method.** `self` becomes `args[0]`, and its default
> repr contains its **memory address** — so the key changes every run and the entry
> can never be found again. Every call then misses, writes a new file, and reads
> nothing back. That is precisely what happened: **18.5 million files** accumulated
> in one directory. `_make_key` now raises `UnstableCacheKey` for such an argument,
> and `@cached` degrades to an uncached call with a `RuntimeWarning` rather than
> silently poisoning the key. Cache a **module-level function of plain values**.

```python
from stellium.utils.cache import cached

@cached(cache_type="geocoding", max_age_seconds=604800)
def _cached_geocode(location_name: str) -> dict: ...   # ✅ plain args, network-bound
```

- **Location** — `default_cache_dir()` → `~/.stellium/cache/`, **beside**
  `~/.stellium/ephe/`, overridable with `STELLIUM_CACHE_DIR` exactly as the
  ephemeris is with `STELLIUM_EPHE_PATH` (both resolved in `data/paths.py`). One
  Stellium home, one convention — a portable install (Windows embedded Python on a
  `D:` drive) redirects *one* place, not two unrelated platform directories. That is
  why this is deliberately **not** `XDG_CACHE_HOME` / `LOCALAPPDATA` /
  `~/Library/Caches`.

  It used to default to the *relative* `".cache"`, which `Path.mkdir()` resolves
  against the **current working directory** — so the cache materialised wherever
  Python happened to be launched. Eight of them accumulated across the repo, one
  145 MB *inside the package itself*.
- **Lazily created** — directories are made on first *write*. The default instance
  is built by `get_default_cache()`, not at import. **Importing a library must not
  touch the disk** (`_default_cache = Cache()` at module scope did exactly that).
- `Cache`: `.get/.set/.clear(cache_type)`, `.size()`, `.get_stats()`; default
  expiry 24h. Subdirs `ephemeris`, `geocoding`, `general` (the first is now unused).
- Management helpers (`cache_utils.py`): `print_cache_info()`,
  `clear_ephemeris_cache()`, `clear_geocoding_cache()`, `clear_all_cache()`,
  `get_cache_stats()`. Also exposed via `stellium cache` CLI.
- `ChartBuilder.with_cache()` is **deprecated and a no-op** — it never had an
  effect (`_get_cache()` was never called by anything, and the engines used the
  global cache regardless, so `with_cache(enabled=False)` disabled nothing).

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
