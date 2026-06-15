# Chart Building Reference

> Part of the [developer docs](./README.md). See also [ARCHITECTURE](./ARCHITECTURE.md), [ENGINES](./ENGINES.md), [COMPONENTS_AND_ANALYSIS](./COMPONENTS_AND_ANALYSIS.md).

The spine of the library: `Native`/`Notable` → `ChartBuilder` → `CalculatedChart`.
Source: `core/native.py`, `core/builder.py`, `core/models.py`, `core/config.py`,
`core/ayanamsa.py`, `core/registry.py`.

---

## 1. Birth data: `Native` / `Notable`

```python
from stellium import Native
Native(datetime_input, location_input, name=None, time_unknown=False)
```

- `datetime_input`: string (many formats), `datetime`, or dict.
- `location_input`: place-name string (geocoded), `(lat, lon)` tuple, or dict.
- Timezone is auto-detected via `timezonefinder`; naive datetimes are localized.
- Geocoding uses a **bundled cache** first, falling back to Nominatim
  (`geopy`). Network calls only happen on cache miss.

`Notable(name, event_type, year, month, day, hour, minute, location, category, …)`
extends `Native` for curated DB records. Adds `data_quality` (Rodden rating),
`verified`, `sources`, `category`, `is_birth`/`is_event`. Loaded from
`data/notables/**/*.yaml`; access via `get_notable_registry()`.

---

## 2. `ChartBuilder` (fluent, lazy)

Source: `core/builder.py`. Every `with_*`/`add_*` returns `self`; nothing
computes until `.calculate()`.

### Constructors
| Method | Use |
|---|---|
| `ChartBuilder.from_native(native)` | Primary path |
| `ChartBuilder.from_details(datetime_str, location_str, name=None, time_unknown=False)` | String shortcut (builds a `Native` for you) |
| `ChartBuilder.from_notable(name)` | Curated registry lookup, e.g. `"Albert Einstein"` |

### Configuration
| Method | Effect / default |
|---|---|
| `with_ephemeris(engine)` | default `SwissEphemerisEngine` |
| `with_house_systems([engines])` | replace all; default `[PlacidusHouses()]` |
| `add_house_system(engine)` | append one |
| `with_aspects(engine=None)` | enable aspects; default `ModernAspectEngine` |
| `with_orbs(engine=None)` | default `SimpleOrbEngine` |
| `with_config(CalculationConfig)` | objects/zodiac config (see §4) |
| `with_name(name)` | label the chart |
| `with_tnos()` / `with_uranian()` | add TNOs / Uranian points |
| `with_sidereal(ayanamsa="lahiri")` / `with_tropical()` | zodiac mode |
| `with_heliocentric()` | Sun→Earth swap, drop nodes/apogees |
| `with_declination_aspects(orb=1.0, include_types=None)` | parallels/contraparallels |
| `with_unknown_time()` | normalize time to noon → returns `UnknownTimeChart` |
| `add_component(component)` | optional positions (Arabic Parts, midpoints, …) |
| `add_analyzer(analyzer)` | optional metadata (patterns, ZR, …) |
| `with_cache(cache=None, enabled=True, cache_dir=..., max_age_seconds=...)` | caching |

### Execution
- `calculate() -> CalculatedChart | UnknownTimeChart`
- `bazi()` — skip the Western pipeline and compute a `BaZiChart` directly
  (see [SUBSYSTEMS](./SUBSYSTEMS.md)).

```python
from stellium import ChartBuilder, Native
from stellium.engines import PlacidusHouses, WholeSignHouses, ModernAspectEngine
from stellium.components import ArabicPartsCalculator, MidpointCalculator

native = Native("1994-01-06 11:47", "Palo Alto, CA")
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .add_component(MidpointCalculator())
    .calculate())
```

---

## 3. Result models (`core/models.py`, all frozen)

### `CelestialPosition`
Identity: `name`, `object_type` (`ObjectType` enum: PLANET, ANGLE, ASTEROID,
POINT, NODE, ARABIC_PART, MIDPOINT, FIXED_STAR, TECHNICAL, ANTISCION).
Ecliptic: `longitude`, `latitude`, `distance`. Velocity: `speed_longitude`,
`speed_latitude`, `speed_distance`. Equatorial: `declination`,
`right_ascension`. Optional: `phase` (`PhaseData`), `phase_angle`,
`illuminated_fraction`.
Computed: `sign`, `sign_degree`, `sign_position`, `is_retrograde`,
`is_out_of_bounds`, `declination_direction`.

### `HouseCusps`
`system_name`, 12 `cusps`. Derived: `houses`, `signs`, `sign_degrees`.
Methods: `get_cusp(h)`, `get_sign(h)`, `get_sign_degree(h)`, `get_description(h)`.

### `Aspect`
`object1`, `object2`, `aspect_name`, `aspect_degree`, `orb`,
`is_applying` (`bool | None`).

### `AspectPattern`
`name`, `planets`, `aspects`, `element`, `quality`; computed `focal_planet`.

### `CalculatedChart` — the central output
Inputs: `datetime` (`ChartDateTime`), `location` (`ChartLocation`).
Data: `positions`, `house_systems` (dict name→`HouseCusps`), `house_placements`,
`aspects`, `declination_aspects`, `metadata` (zodiac_type, ayanamsa,
calculation_timestamp, chart_tags, plus analyzer/component output).

Key methods (verified against source):
- **Lookup:** `get_object(name)`, `get_planets()`, `get_angles()`,
  `get_points()`, `get_nodes()`, `get_houses(system=None)`,
  `get_house(name, system=None)`, `default_house_system`.
- **Declination:** `get_declination_aspects(type=None)`, `get_parallels()`,
  `get_contraparallels()`.
- **Dignities:** `get_dignities(system="traditional")`,
  `get_planet_dignity(...)`, `get_mutual_receptions(...)`,
  `get_accidental_dignities(system=None)`, `get_strongest_planet()`,
  `get_planet_total_score(...)`; `sect` property.
- **Components:** `get_component_result(name)`, `available_components()`.
- **Timing transforms:** `profection(...)`, `profections(...)`,
  `profection_timeline(...)`, `lord_of_year(...)`, `draconic()`,
  `voc_moon(...)`, `zodiacal_releasing(lot=...)`, `zr_at_date(...)`,
  `zr_at_age(...)`.
- **Render/export:** `draw(filename="chart.svg")` →
  [`ChartDrawBuilder`](./VISUALIZATION_INTERNALS.md), `draw_vedic(...)`,
  `draw_dial(...)`, `to_prompt_text(...)`, `to_dict()`, `bazi()`.

### `UnknownTimeChart`
Subclass for unknown birth times. No houses/angles; adds `moon_range`
(`MoonRange`). `get_house`/`get_houses` return `None`.

### `MultiChart`
2–4 chart container (synastry/transits/triwheel). Indexing `mc[0]`,
`mc.chart1`/`.inner`/`.outer`/`.natal`; `get_cross_aspects(i, j)`,
`get_house_overlays(...)`, `calculate_compatibility_score()`, `draw()`. See
[SUBSYSTEMS](./SUBSYSTEMS.md).

---

## 4. Configuration (`core/config.py`, `core/ayanamsa.py`)

- `CalculationConfig`: `include_planets` (Sun–Pluto default), `include_nodes`,
  `include_chiron`, `include_points`, `include_asteroids`, `zodiac_type`
  (`ZodiacType.TROPICAL | SIDEREAL`), `ayanamsa`, `heliocentric`. Presets:
  `CalculationConfig.minimal()`, `CalculationConfig.comprehensive()`.
- `AspectConfig`: which aspects + whether to include angles/nodes/asteroids.
- Ayanamsa registry keys: `lahiri`, `fagan_bradley`, `raman`, `krishnamurti`,
  `yukteshwar`, `jn_bhasin`, `true_citra`, `true_revati`, `deluce`. Access via
  `get_ayanamsa(name)`, `list_ayanamsas()`.

---

## 5. Registries (`core/registry.py`)

| Registry | Holds | Accessors |
|---|---|---|
| `CELESTIAL_REGISTRY` | 60+ objects (planets, asteroids, nodes, TNOs, Uranian) with glyph, swe id, motion, category, aliases | `get_object_info(name)`, `get_by_alias`, `get_all_by_type`, `get_all_by_category`, `search_objects` |
| `ASPECT_REGISTRY` | ~30 aspects (major/minor/harmonic/declination) with angle, glyph, color, default_orb | `get_aspect_info(name)`, `get_aspect_by_alias`, `get_aspects_by_category`, `get_aspects_by_family` |
| `FIXED_STARS_REGISTRY` | ~25 stars in tiers (Royal/Major/Extended) | `get_fixed_star_info(name)`, `get_royal_stars()`, `get_stars_by_tier(tier)` |

---

## Gotchas

- `.with_aspects()` is **optional** — call it (or a preset that does) or
  `chart.aspects` is empty.
- Components run in registration order; some Arabic Parts depend on earlier
  ones being calculated first (the calculator handles ordering internally).
- Sidereal `ayanamsa_value` is only populated when `zodiac_type` is SIDEREAL.
- To "modify" a frozen result, use `dataclasses.replace(...)`.
