# Changelog

All notable changes to Stellium will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [0.14.0] - 2025-12-18

### Added

#### Chart Atlas PDF Generation

New `AtlasBuilder` for generating multi-page PDF documents with one chart per page, like an old-school astrologer's chart atlas.

**Features:**

- Generate PDFs with multiple charts from Native objects or notable lookups
- Support for both natal wheel charts and Uranian dial charts
- Configurable headers, themes, and page sizes
- Optional title page
- Uses Typst for beautiful PDF rendering

**Usage:**

```python
from stellium.visualization.atlas import AtlasBuilder

# Basic atlas from notables
(AtlasBuilder()
    .add_notable("Albert Einstein")
    .add_notable("Marie Curie")
    .add_notable("Isaac Newton")
    .with_title_page("Famous Scientists")
    .with_header()
    .with_theme("midnight")
    .save("scientists_atlas.pdf"))

# Dial atlas
(AtlasBuilder()
    .add_natives([native1, native2, native3])
    .with_chart_type("dial", degrees=90)
    .save("uranian_atlas.pdf"))

# Complete atlas from all notables
AtlasBuilder.from_all_notables().with_title_page("Complete Atlas").save("all_notables.pdf")

# Filter by category
AtlasBuilder.from_all_notables(category="scientist", sort_by="date").save("scientists.pdf")

# Mixed chart types
(AtlasBuilder()
    .add_entry(native1, chart_type="wheel")
    .add_entry(native2, chart_type="dial", degrees=90)
    .save("mixed_atlas.pdf"))
```

Requires: `pip install typst`

#### Atlas Theme

New "atlas" chart theme designed to match the PDF atlas styling with a cream background and purple/gold accents.

**Features:**

- Cream background (`#FAF8F5`) that blends seamlessly with PDF pages
- Purple primary/secondary/accent colors matching Typst document styling
- Gold accents for retrograde markers and secondary overlays
- Default theme for AtlasBuilder (uses rainbow zodiac palette)

**Usage:**

```python
# Atlas theme is now the default for AtlasBuilder
AtlasBuilder().add_notable("Albert Einstein").save("atlas.pdf")

# Can also be used standalone for any chart
chart.draw("chart.svg").with_theme("atlas").save()
```

#### Atlas Info Corners

Atlas charts now include info corners by default for maximum detail:

- **Aspect counts** (top-right): Summary of aspect types and counts
- **Element/modality table** (bottom-left): Cross-table showing planet distribution

**Usage:**

```python
# Info corners are enabled by default
AtlasBuilder().add_notable("Albert Einstein").save("atlas.pdf")

# Disable one or both
AtlasBuilder().add_notable("Albert Einstein").without_aspect_counts().save("atlas.pdf")
AtlasBuilder().add_notable("Albert Einstein").without_element_modality().save("atlas.pdf")
AtlasBuilder().add_notable("Albert Einstein").without_info_corners().save("atlas.pdf")
```

### Fixed

#### Extended Tables Symbol Rendering

Fixed an issue where astrological symbols (Chiron ⚷, Black Moon Lilith ⚸, Vertex 🜊, and retrograde ℞) in extended tables were rendering as question mark boxes in PDF output.

**The fix:**

- Symbols and text are now rendered as separate SVG elements with appropriate fonts
- Glyphs use the Symbola/Noto Sans Symbols font family
- Text labels use Arial/Helvetica
- Vertical alignment adjusted for proper baseline matching
- ASC and MC entries skip redundant glyph rendering (their "symbols" are just the same text)

#### Info Corner Symbol Rendering

Fixed the same font rendering issue in the AspectCountsLayer and ElementModalityTableLayer info corners. Aspect glyphs (☌, △, □, etc.) and element symbols (🜂, 🜃, 🜁, 🜄) now render correctly in PDF output.

#### Dial Chart Header Support

Added header support to dial chart visualization, displaying native's name, birth location, and datetime at the top of the dial.

**Usage:**

```python
# Generate a dial with header
chart.draw_dial("dial.svg").with_header().save()

# Header is disabled by default
chart.draw_dial("dial.svg").save()  # No header
```

The header uses the same elegant styling as the main chart header (Baskerville italic-semibold for name, standard font for details).

#### Antiscia and Contra-Antiscia Calculator

New `AntisciaCalculator` component for calculating antiscia (solstice axis reflections) and contra-antiscia (equinox axis reflections) points.

**Features:**

- Calculates antiscia and contra-antiscia points for all configured planets
- Detects "hidden conjunctions" when one planet's antiscion is conjunct another planet
- New `ObjectType.ANTISCION` and `ObjectType.CONTRA_ANTISCION` types (filtered from chart wheel display)
- Configurable orb for conjunction detection (default 1.5°)
- Configurable planet list (defaults to classical 7 + modern outers + True Node)
- New `AntisciaSection` for presentation reports

```python
from stellium import ChartBuilder, Native
from stellium.components import AntisciaCalculator
from stellium.presentation.sections import AntisciaSection

chart = (
    ChartBuilder.from_native(native)
    .add_component(AntisciaCalculator(orb=2.0))
    .calculate()
)

# Access antiscia conjunction data
antiscia_data = chart.metadata.get("antiscia", {})
conjunctions = antiscia_data.get("conjunctions", [])
for conj in conjunctions:
    print(conj.description)  # "Sun in antiscia with Moon (applying, orb 1.2°)"

# Or use in a report
from stellium.presentation import ReportBuilder

report = ReportBuilder().from_chart(chart).with_section(AntisciaSection())
report.render(format="rich_table")
```

#### Improved Planet Glyph Collision Detection

Rewrote the collision detection algorithm for planet glyphs on chart wheels. The previous algorithm used a fixed 6° minimum separation regardless of ring radius, causing glyphs to overlap badly on inner rings of bi-wheel and tri-wheel charts.

**Key improvements:**

- **Radius-aware spacing**: Minimum separation now calculated from glyph size and ring circumference. Inner rings (smaller radius) automatically get more angular separation than outer rings.
- **Iterative force-based spreading**: Uses a physics-inspired algorithm that pushes overlapping glyphs apart over multiple iterations until stable.
- **Proper wrap-around handling**: Correctly detects and resolves collisions at the 0°/360° boundary (e.g., planets at 358° and 2° are properly recognized as only 4° apart).
- **Maximum displacement limit**: Glyphs won't move more than 20° from their true position, balancing visual clarity with positional accuracy.

This fix significantly improves the readability of multiwheel charts, especially when planets are tightly clustered.

---

## [0.13.0] - 2025-12-17

### Added

#### PDF Planner Generator

New `PlannerBuilder` class for generating beautiful personalized astrological planners as PDF files.

**Features:**

- **Front matter pages**: Natal chart, progressed chart, solar return, annual profection info, graphic ephemeris
- **Monthly calendar grids**: Full-page calendar view with all events displayed in each day cell
- **Weekly detail pages**: 7-day spreads with compact event listings per day
- **Rainbow zodiac palette**: All charts use colorful zodiac sign backgrounds
- **Configurable week start**: Sunday (US) or Monday (European) calendar style
- **Multiple page sizes**: A4, Letter, or half-letter with optional binding margins

```python
from stellium import Native, PlannerBuilder

native = Native("1990-05-15 14:30", "San Francisco, CA")

planner = (
    PlannerBuilder.for_native(native)
    .year(2025)
    .timezone("America/Los_Angeles")
    .with_natal_chart()
    .with_progressed_chart()
    .with_solar_return()
    .with_profections()
    .with_graphic_ephemeris(harmonic=90)
    .include_natal_transits()  # All planets + Node + Chiron
    .include_moon_phases()
    .include_voc(mode="traditional")
    .include_ingresses(["Sun", "Moon", "Mercury", "Venus", "Mars"])
    .include_stations()
    .week_starts_on("sunday")
    .generate("my_planner.pdf")
)
```

**Daily Events Tracked:**

- Transit-to-natal aspects (all 10 planets + True Node + Chiron)
- Moon phases (New Moon, Full Moon)
- Void of Course Moon periods (traditional or modern calculation)
- Planet ingresses (sign changes)
- Planetary stations (retrograde/direct)
- Eclipses (solar and lunar)

**Event Collection** (`stellium.planner.events`):

- `DailyEventCollector` class for gathering astrological events
- Configurable transit planets and aspect orbs
- Timezone-aware event times
- Priority-based event sorting

See `examples/planner_cookbook.py` for detailed recipes and usage patterns.

---

## [0.12.0] - 2025-12-17

### Added

#### Electional Astrology Search Engine

New `ElectionalSearch` class for finding auspicious times matching astrological conditions. This is a complete electional astrology toolkit with interval-based optimization for fast searches over long date ranges.

**Core Features:**

- **Fluent search API**: Chain conditions with `.where()` method
- **Multiple output formats**: `find_moments()`, `find_windows()`, `find_first()`, `iter_moments()`, `count()`
- **Condition composition**: `all_of()`, `any_of()`, `not_()` for combining conditions
- **Lambda support**: Use inline lambdas or helper predicates interchangeably
- **Hierarchical optimization**: Day-level filtering skips entire days that can't match
- **Interval algebra**: Pre-computes windows for fast set intersection (100x+ speedup for supported conditions)

```python
from stellium.electional import (
    ElectionalSearch, is_waxing, not_voc, sign_not_in,
    on_angle, no_hard_aspect, not_retrograde
)

# Find auspicious election windows
results = (ElectionalSearch("2025-01-01", "2025-06-30", "San Francisco, CA")
    .where(is_waxing())
    .where(not_voc())
    .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
    .where(on_angle("Jupiter"))
    .where(no_hard_aspect("Moon"))
    .where(not_retrograde("Mercury"))
    .find_windows())

for window in results:
    print(f"{window.start} - {window.end} ({window.duration})")
```

**30+ Helper Predicates:**

- Moon phase: `is_waxing()`, `is_waning()`, `moon_phase()`
- VOC Moon: `is_voc()`, `not_voc()` (traditional or modern)
- Signs: `sign_in()`, `sign_not_in()`
- Houses: `in_house()`, `on_angle()`, `succedent()`, `cadent()`, `not_in_house()`
- Retrograde: `is_retrograde()`, `not_retrograde()`
- Dignity: `is_dignified()`, `is_debilitated()`, `not_debilitated()`
- Aspects: `has_aspect()`, `no_aspect()`, `aspect_applying()`, `aspect_separating()`, `no_hard_aspect()`, `no_malefic_aspect()`
- Combust: `is_combust()`, `not_combust()`
- Out of bounds: `is_out_of_bounds()`, `not_out_of_bounds()`
- Aspect exactitude: `aspect_exact_within()`
- Angles: `angle_at_degree()`, `star_on_angle()`
- Planetary hours: `in_planetary_hour()`

**Interval Generators** (`stellium.electional.intervals`):

Pre-compute time windows for fast set intersection:

- `waxing_windows()`, `waning_windows()` - Lunar phase windows
- `moon_sign_windows()`, `moon_sign_not_in_windows()` - Moon sign ingresses
- `retrograde_windows()`, `direct_windows()` - Planetary station periods
- `voc_windows()`, `not_voc_windows()` - Void of course periods
- `aspect_exact_windows()` - Windows around aspect exactitude
- `angle_at_longitude_windows()` - When angles reach specific degrees

**Set Operations:**

- `intersect_windows()` - AND of window sets
- `union_windows()` - OR of window sets
- `invert_windows()` - NOT (complement) of windows

#### Planetary Hours

Complete planetary hours calculation system for traditional timing.

```python
from stellium.electional import (
    get_planetary_hour, get_planetary_hours_for_day,
    get_day_ruler, get_sunrise_sunset, in_planetary_hour,
    CHALDEAN_ORDER, DAY_RULERS, PlanetaryHour
)

# Get current planetary hour
hour = get_planetary_hour(datetime.now(), latitude=37.7, longitude=-122.4)
print(f"Current hour: {hour.ruler} ({'day' if hour.is_day_hour else 'night'} hour #{hour.hour_number})")

# Get all 24 planetary hours for a day
hours = get_planetary_hours_for_day(datetime(2025, 1, 15), latitude=37.7, longitude=-122.4)
for h in hours:
    print(f"{h.ruler}: {h.start_utc.strftime('%H:%M')} - {h.end_utc.strftime('%H:%M')}")

# Use in electional search
search = ElectionalSearch("2025-01-01", "2025-01-31", "San Francisco, CA")
results = search.where(in_planetary_hour("Jupiter")).find_moments()
```

Features:

- Variable-length hours based on actual sunrise/sunset times
- Chaldean order planet sequence (Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon)
- Day rulers for each weekday
- Support for any geographic location

#### Aspect Exactitude Search Functions

New functions in `stellium.engines.search` for finding exact aspect times:

```python
from stellium.engines.search import (
    find_aspect_exact, find_all_aspect_exacts, AspectExact
)

# Find next exact Moon trine Jupiter
result = find_aspect_exact("Moon", "Jupiter", 120.0, datetime(2025, 1, 1))
print(f"Exact trine: {result.datetime_utc}, orb at exact: {result.separation - 120:.6f}°")

# Find all Sun-Moon conjunctions (New Moons) in a year
new_moons = find_all_aspect_exacts("Sun", "Moon", 0.0,
    datetime(2025, 1, 1), datetime(2025, 12, 31))
for nm in new_moons:
    print(f"New Moon: {nm.datetime_utc}")
```

- `AspectExact` dataclass with timing, positions, and applying/separating info
- `find_aspect_exact()` - Find next/previous exact aspect
- `find_all_aspect_exacts()` - Find all exact aspects in date range
- Uses Newton-Raphson refinement for sub-arcsecond precision
- Supports all aspect angles (0°, 60°, 90°, 120°, 180°, or custom)

#### Angle Crossing Search Functions

New functions for finding when chart angles (ASC, MC, DSC, IC) reach specific longitudes:

```python
from stellium.engines.search import (
    find_angle_crossing, find_all_angle_crossings, AngleCrossing
)

# Find when 0° Aries rises (Aries Ascendant)
crossing = find_angle_crossing(0.0, latitude=40.7, longitude=-74.0,
    angle="ASC", start=datetime(2025, 1, 1))
print(f"Aries rising: {crossing.datetime_utc}")

# Find all MC crossings of a fixed star longitude
regulus_lon = 150.0  # Approximate
crossings = find_all_angle_crossings(regulus_lon, 37.7, -122.4, "MC",
    datetime(2025, 1, 1), datetime(2025, 1, 7))
# ~7 crossings (once per sidereal day)
```

- `AngleCrossing` dataclass with exact timing and angle value
- `find_angle_crossing()` - Find next/previous angle crossing
- `find_all_angle_crossings()` - Find all crossings in date range
- Supports ASC, MC, DSC, IC angles
- ~Once per sidereal day for each angle/longitude combination

#### Electional Cookbook Examples

New `examples/electional_cookbook.py` with 43 comprehensive examples covering:

1. Basic searches (waxing moon, not VOC, sign filtering)
2. House placements and angular planets
3. Retrograde avoidance
4. Dignity considerations
5. Aspect conditions (applying, separating, exact)
6. Combust and out-of-bounds
7. Complex multi-condition elections
8. Lambda vs predicate syntax
9. Aspect exactitude searches
10. Fixed stars and angle crossings
11. Planetary hours
12. Performance optimization techniques

### Changed

### Fixed

#### Conjunction Detection in Aspect Search

Fixed a bug where `find_aspect_exact()` couldn't find 0° aspects (conjunctions). The bracketing algorithm relied on sign changes in the error function, but for conjunctions the angular separation is always positive (range [0, 180°]), so the error never changes sign.

**The fix:**

- Added local minimum detection for conjunctions using a 3-point test
- Implemented golden section search for refinement (instead of sign-based bisection)
- Now correctly finds Sun-Moon conjunctions (New Moons) and other conjunctions

#### Timezone Handling in Electional Search

Fixed timezone conversion for interval-based window calculations in `ElectionalSearch`. The search now properly converts local datetimes to Julian Day using the location's timezone, ensuring window generators receive correct UTC-based times.

**What was fixed:**

- `_get_valid_windows()` now uses `_local_datetime_to_jd()` for proper timezone conversion
- `_is_in_valid_windows()` converts query times correctly before comparison
- `_count_steps_in_windows()` uses consistent timezone handling

#### Planetary Hours Date Calculation

Fixed `get_sunrise_sunset()` to interpret the date parameter as local date rather than UTC date. Previously, searching for planetary hours on "January 15" in San Francisco would return sunrise/sunset for the wrong day due to UTC offset.

**The fix:**

- Adjusted start time using longitude-based timezone approximation
- Added fallback checks for edge cases (times before today's sunrise or after today's night)

#### Moon Phase No Longer Always Waxing

Moon phase attribute `is_waxing` was being calculated incorrectly so that it was always true. I've added in the sun's longitude so we can get the angular distance from the Moon and properly determine its phase.

#### RAMC No Longer Displayed on Chart Wheels

RAMC (Right Ascension of MC) was incorrectly appearing as a planet/point on chart wheel visualizations. This technical calculation value is now properly categorized as `ObjectType.TECHNICAL` and excluded from chart rendering.

#### CI Test Failures with Geocoding

Fixed test failures in GitHub Actions CI where module-scoped test fixtures (in `test_multiwheel.py` and `test_zodiacal_releasing.py`) were attempting geocoding before the mock was applied. The geocoding mock is now session-scoped to ensure it's active before any fixtures run.

#### VOC Window Calculation Accuracy

Fixed a discrepancy where `ElectionalSearch` with `not_voc()` could return different results between optimized and unoptimized modes. The issue was in `voc_windows()` which uses binary search to find VOC transition times.

**Root cause:**

The binary search tolerance was 5 minutes, which could overshoot the actual VOC transition by up to 5 minutes. For example, on Jan 5, 2025:

- Actual VOC start: 11:58:30 UTC
- Computed VOC start: 12:00:09 UTC (with 5-min tolerance)

This caused edge cases where a time like 12:00:00 UTC was incorrectly classified as "not VOC" by the optimized path (using pre-computed windows) but correctly as "VOC" by the unoptimized path (using live `chart.voc_moon()` checks).

**The fix:**

- Reduced binary search tolerance from 5 minutes to 1 minute in `_find_voc_transition_in_sign()`
- This adds ~2-3 iterations to the binary search but ensures optimized and unoptimized results match

#### Waxing Moon Window Calculation

Fixed `waxing_windows()` not finding all waxing periods when the Full Moon occurred after the search end date. The function now searches for Full Moons up to 30 days beyond the end date to ensure complete coverage.

#### Window Endpoint Inclusion

Fixed off-by-one errors in `_is_in_valid_windows()` and `_count_steps_in_windows()` where window endpoints were being excluded. Changed boundary comparisons from `<` to `<=` for consistent endpoint inclusion across the codebase.

## [0.11.1] - 2025-12-15

### Fixed

#### Notables Data Quality

Fixed missing required fields in several notable entries that caused them to be skipped during registry loading:

- Added missing `hour`/`minute` fields to 9 birth entries (using 12:00 noon for unknown birth times)
- Added missing `category` fields to 5 historical events

The registry now loads all 196 entries (175 births, 21 events) without warnings.

---

## [0.11.0] - 2025-12-15

### Fixed

#### Package Data Now Works When Installed from PyPI

Fixed a critical issue where the notables registry returned 0 entries when stellium was installed from PyPI. The root cause was that data files (notables YAML, ephemeris files) were stored outside the package directory and weren't included in the distribution.

**What changed:**

- Notables data moved into `src/stellium/data/notables/` (now bundled with package)
- Essential ephemeris files (~4MB) moved into `src/stellium/data/swisseph/ephe/`
- New user data directory at `~/.stellium/ephe/` for ephemeris files
- On first use, bundled ephemeris files are automatically copied to user directory
- Users can still download additional asteroid/date-range files via CLI

**New behavior:**

```python
# First time running stellium after install:
# "Stellium: Initialized 7 ephemeris files in /Users/you/.stellium/ephe"

from stellium.data import get_notable_registry
registry = get_notable_registry()
print(len(registry))  # Now correctly shows ~170 entries
```

**For users who download additional ephemeris files:**

```bash
# Files now download to ~/.stellium/ephe/ instead of project root
stellium ephemeris download-asteroid eris
stellium ephemeris download --years "1000-1800"
```

### Added

#### ProseRenderer for Natural Language Output (December 12, 2025)

New `ProseRenderer` that converts chart data to clean, readable prose - perfect for pasting into conversations with AI friends or anywhere you want text without tables.

- **Natural language format**: Chart info as flowing sentences and bullet points
- **All section types supported**: Overview, positions, aspects, dignities, Arabic parts, transit calendar, and more
- **Clean output**: No tables, no formatting codes, just readable text
- **File output**: Save to `.txt` files with `render(format='prose', file='chart.txt')`

```python
from stellium import ChartBuilder, Native, ReportBuilder
from stellium.engines.aspects import ModernAspectEngine

chart = (ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .calculate())

report = (ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .with_aspects(mode='major', include_aspectarian=False))

# Print to terminal
report.render(format='prose')

# Save to file
report.render(format='prose', file='my_chart.txt')
```

Example output:

```txt
Jane Doe was born on January 10, 1995 at 12:00 PM in San Francisco, CA.
This is a day chart with Aries rising. The chart ruler is Mars.

Planet Positions:
• ☉ Sun is at ♑︎ Capricorn 16°16' in the 10th house
• ☽ Moon is at ♏︎ Scorpio 10°10' in the 7th house
...

Major Aspects:
• ♀ Venus ☌ Conjunction ♂ Mars (orb 0.30°, separating)
• ♃ Jupiter ☌ Conjunction ☽ Moon (orb 0.45°, applying)
...
```

#### Graphic Ephemeris Visualization (December 11, 2025)

New `GraphicEphemeris` class for visualizing planetary positions over time.

- **Three harmonic modes**: 360° (full zodiac), 90° (hard aspects), 45° (8th harmonic)
- **Station markers**: Retrograde and direct station points with legend
- **Aspect markers**: Shows conjunction (☌), square (□), opposition (☍) at line crossings
- **Natal chart overlay**: Pass a `CalculatedChart` to show transit-to-natal aspects
  - Horizontal dashed lines for natal positions
  - Transit planets on left, natal planets on right
  - Natal chart info (name, datetime, location) in header
- **Planet selection**: Default planets, `EXTENDED_PLANETS` (with Chiron/Node), or custom list
- **Customizable**: Width, height, title, show/hide features

```python
from stellium.visualization import GraphicEphemeris, EXTENDED_PLANETS
from stellium import ChartBuilder

# Basic ephemeris
eph = GraphicEphemeris(
    start_date="2025-01-01",
    end_date="2025-12-31",
    harmonic=90,
)
eph.draw("ephemeris_2025.svg")

# With natal chart overlay
natal = ChartBuilder.from_notable("Albert Einstein").calculate()
eph = GraphicEphemeris(
    start_date="2025-01-01",
    end_date="2025-12-31",
    harmonic=90,
    natal_chart=natal,
)
eph.draw("transits_2025.svg")

# Extended planets (includes Chiron and North Node)
eph = GraphicEphemeris(
    start_date="2025-01-01",
    end_date="2025-12-31",
    planets=EXTENDED_PLANETS,
)
eph.draw("extended_2025.svg")
```

See `examples/ephemeris_cookbook.py` for comprehensive usage examples.

#### File I/O Module (December 11, 2025)

New `stellium.io` module for importing data from external astrology software.

- **`parse_aaf(path)`**: Parse AAF (Astrodienst Astrological Format) files
  - AAF is the export format from astro.com
  - Returns `list[Native]` for easy integration with ChartBuilder
  - Parses date/time from #A93 lines (human-readable format)
  - Uses pre-computed coordinates from #B93 lines (trusted values)
  - Handles timezone lookup via coordinates

Example usage:

```python
from stellium import parse_aaf, ChartBuilder

# Import charts from astro.com export
natives = parse_aaf("my_charts.aaf")

# Calculate a chart
chart = ChartBuilder.from_native(natives[0]).calculate()

# Or batch calculate all of them
from stellium.analysis import BatchCalculator
charts = BatchCalculator.from_natives(natives).calculate_all()
```

#### Notables Database

- Added more births and events (~40 births, ~5 events)

### Changed

### Fixed

## [0.10.0] - 2025-12-11

### Added

#### Data Analysis Module (December 11, 2025)

New `stellium.analysis` package for large-scale astrological data analysis. Requires optional dependency: `pip install stellium[analysis]`

- **BatchCalculator**: Efficiently calculate 100s-1000s of charts at once
  - Factory methods: `from_registry()` (with filters), `from_natives()`, `from_iterable()`
  - Fluent configuration: `.with_house_systems()`, `.with_aspects()`, `.add_analyzer()`
  - Generator-based `.calculate()` for memory efficiency or `.calculate_all()` for convenience
  - Progress tracking via `.with_progress(callback)`

- **DataFrame Builders**: Convert charts to pandas DataFrames in three schemas
  - `charts_to_dataframe()`: One row per chart (sun/moon signs, element counts, patterns, etc.)
  - `positions_to_dataframe()`: One row per celestial position (for position distribution analysis)
  - `aspects_to_dataframe()`: One row per aspect (for aspect frequency analysis)

- **ChartQuery**: Fluent interface for filtering chart collections by astrological criteria
  - Position filters: `where_sun()`, `where_moon()`, `where_planet()`, `where_angle()`
  - Aspect filters: `where_aspect(obj1, obj2, aspect=, orb_max=)`
  - Pattern filters: `where_pattern("Grand Trine")`
  - Element/modality: `where_element_dominant()`, `where_modality_dominant()`
  - Custom predicates: `where_custom(lambda chart: ...)`
  - Results: `.results()`, `.count()`, `.first()`, `.to_dataframe()`

- **ChartStats**: Statistical aggregation across chart collections
  - Distributions: `element_distribution()`, `modality_distribution()`, `sign_distribution()`
  - Frequencies: `aspect_frequency()`, `pattern_frequency()`, `retrograde_frequency()`
  - Cross-tabulation: `cross_tab("sun_sign", "moon_sign")` returns pandas contingency table
  - Summary: `summary()` returns comprehensive statistics dict

- **Export Utilities**: Save chart data to files
  - `export_csv(charts, path, schema="charts"|"positions"|"aspects")`
  - `export_json(charts, path, lines=False)` - standard JSON or JSON Lines
  - `export_parquet(charts, path, schema=...)` - columnar format for big data

- **36 comprehensive tests** in `tests/test_analysis.py`

- **Interactive Jupyter Notebook Cookbook**: `examples/analysis_cookbook.ipynb`
  - BatchCalculator usage patterns
  - DataFrame conversion examples with pandas
  - ChartQuery filtering examples
  - ChartStats statistical analysis
  - Export utilities
  - Full workflow examples (element distribution in scientists vs artists, etc.)

Example usage:

```python
from stellium.analysis import BatchCalculator, ChartQuery, ChartStats, charts_to_dataframe

# Calculate charts for all scientists in the registry
charts = (BatchCalculator
    .from_registry(category="scientist", verified=True)
    .with_aspects()
    .calculate_all())

# Convert to DataFrame
df = charts_to_dataframe(charts)
print(df['sun_sign'].value_counts())

# Query for specific criteria
grand_trines = ChartQuery(charts).where_pattern("Grand Trine").results()

# Statistical analysis
stats = ChartStats(charts)
print(stats.element_distribution())
print(stats.sign_distribution("Sun"))
```

### Changed

### Fixed

## [0.9.0] - 2025-12-11

### Added

#### Unified MultiChart Architecture (December 11, 2025)

- **MultiChart**: New unified class that replaces both `Comparison` and `MultiWheel`
  - Supports 2-4 charts (biwheels, triwheels, quadwheels)
  - **Dual access pattern**: Indexed (`mc[0]`, `mc[1]`) AND named properties (`mc.chart1`, `mc.natal`)
  - **Semantic aliases**: `.inner`, `.outer`, `.natal` for intuitive access
  - **Per-pair relationship types**: Store relationship (synastry, transit, progression) for each chart pair
  - **Cross-aspects as dict**: `{(0,1): aspects, (0,2): aspects}` for flexible multi-chart aspect storage
  - **House overlays**: Support for cross-chart house placements
  - **Compatibility scoring**: `calculate_compatibility_score(pair=(0,1))` for synastry analysis
  - Full serialization via `.to_dict()` and visualization via `.draw()`

- **MultiChartBuilder**: Fluent builder with all Comparison/MultiWheel features unified
  - **Convenience constructors**: `.synastry()`, `.transit()`, `.progression()`, `.arc_direction()`
  - **Generic constructors**: `.from_charts()`, `.from_chart()`
  - **Add methods for 3-4 charts**: `.add_chart()`, `.add_transit()`, `.add_progression()`, `.add_arc_direction()`
  - **Cross-aspect config**: `.with_cross_aspects("to_primary")` (default), `"all"`, `"adjacent"`, or explicit pairs
  - **House overlay config**: `.with_house_overlays()`, `.without_house_overlays()`
  - Auto-calculates progressions and arc directions like ComparisonBuilder did

- **Visualization support**: All visualization layers updated to handle MultiChart
  - `ChartDrawBuilder`, `ChartComposer`, `LayerFactory` accept MultiChart
  - `LayoutEngine` and `ContentMeasurer` handle MultiChart ring layouts
  - New `_create_multichart_layers()` method in LayerFactory

- **Presentation support**: Report builder and sections updated for MultiChart
  - `ReportBuilder.from_chart()` accepts MultiChart
  - `CrossChartAspectSection` handles MultiChart's dict-based cross_aspects
  - `ChartOverviewSection` displays multi-chart info (type, relationships, all chart details)

- **51 comprehensive tests** in `tests/test_multichart.py`

Example usage:

```python
from stellium import MultiChartBuilder

# Synastry (replaces ComparisonBuilder.synastry)
mc = MultiChartBuilder.synastry(chart1, chart2, label1="Kate", label2="Partner").calculate()

# Triwheel: Natal + Progressed + Transit
mc = (MultiChartBuilder.from_chart(natal, "Natal")
    .add_progression(age=30, label="Progressed")
    .add_transit("2025-06-15", label="Transit")
    .calculate())

# Access charts
print(mc.chart1.get_object("Sun"))  # Named access
print(mc[1].get_object("Moon"))     # Indexed access
print(mc.natal.get_object("Venus")) # Semantic alias

# Cross-aspects
aspects = mc.get_cross_aspects(0, 1)  # Aspects between charts 0 and 1

# Visualization and reports
mc.draw("triwheel.svg").save()
report = ReportBuilder().from_chart(mc).with_chart_overview().with_cross_aspects().render()
```

### Deprecated

- **Comparison** and **ComparisonBuilder**: Now emit `DeprecationWarning`, use `MultiChart` and `MultiChartBuilder` instead
- **MultiWheel** and **MultiWheelBuilder**: Now emit `DeprecationWarning`, use `MultiChart` and `MultiChartBuilder` instead

#### IngressSection Report (December 11, 2025)

- **IngressSection**: Report section showing when planets enter new zodiac signs
  - Same pattern as `StationSection` - date-range based, not chart-analysis
  - Default planets: Sun through Pluto
  - Optional `include_moon=True` for Moon ingresses (frequent, ~2.5 days/sign)
  - Optional `include_minor=True` for Chiron
  - Shows retrograde ingresses with "Rx" indicator
  - Table columns: Date, Time, Planet, From, To (with sign glyphs)
  - Built on existing `find_all_sign_changes()` from search engine

- **ReportBuilder.with_ingresses()**: Builder method for ingress section
  - `end` parameter required
  - `start` defaults to chart date if not provided
  - Full API: `with_ingresses(end, start=None, planets=None, include_moon=False, include_minor=False)`

#### Eclipse Search and Section (December 11, 2025)

- **Eclipse dataclass**: Result object for eclipse searches
  - `eclipse_type`: "solar" or "lunar"
  - `classification`: "total", "partial", "penumbral", or "annular"
  - `nearest_node`: Which node the eclipse is near ("north" or "south")
  - `orb_to_node`: Distance from lunation to node
  - Nice `__str__`: "Total solar eclipse at 19°24' Aries (NN) on 2024-04-08"

- **`find_eclipse(start, eclipse_types="both")`**: Find next eclipse from a date
  - Searches for New/Full Moons, checks node proximity
  - Solar eclipses within 18.5° of node, lunar within 12.5°

- **`find_all_eclipses(start, end, eclipse_types="both")`**: All eclipses in a range
  - Returns chronologically sorted list
  - Properly finds both eclipses in eclipse seasons (solar + lunar ~2 weeks apart)

- **EclipseSection**: Report section showing eclipses in a date range
  - Same pattern as StationSection and IngressSection
  - Table columns: Date, Time, Type, Position, Sign, Node

- **ReportBuilder.with_eclipses()**: Builder method for eclipse section
  - Full API: `with_eclipses(end, start=None, eclipse_types="both")`

- **ReportBuilder.preset_transit_calendar()**: Convenience preset bundling all sky events
  - Combines stations, ingresses, and eclipses in one call
  - Full API: `preset_transit_calendar(end, start=None, include_minor_planets=False)`
  - First parameterized preset (date range is user-specified, not defaulted)

### Changed

### Fixed

## [0.8.0] - 2025-12-09

### Added

#### Primary Directions Engine (December 9, 2025)

- **DirectionsEngine**: Complete primary directions calculation engine
  - **Two direction methods** (swappable):
    - `"zodiacal"` (default): 2D ecliptic projection using oblique ascension
    - `"mundane"`: 3D Placidus semi-arc proportions
  - **Two time keys** (swappable):
    - `"naibod"` (default): Mean solar motion rate (~1.0146 years/degree)
    - `"ptolemy"`: Classic 1 degree = 1 year
  - **API methods**:
    - `engine.direct("Sun", "ASC")` - Direct promissor to significator
    - `engine.direct_to_angles("Sun")` - Direct to all 4 angles
    - `engine.direct_all_to("ASC")` - Direct all planets to one point

- **DistributionsCalculator**: Separate class for term/bound distributions
  - Tracks "life chapters" based on planetary terms (Egyptian bounds)
  - Directed Ascendant through zodiacal bounds
  - Configurable time key and year limit
  - `calc.calculate(years=80)` - Returns list of TimeLordPeriod

- **Data models** (all frozen dataclasses):
  - `EquatorialPoint`: RA/Dec coordinate point
  - `MundanePosition`: Point with house-space context (semi-arcs, meridian distance)
  - `DirectionArc`: Result of direction calculation
  - `DirectionResult`: Complete result with date and age
  - `TimeLordPeriod`: Term ruler period with sign
  - `TermBoundary`: Term boundary position

- **Spherical math functions** (pure, module-level):
  - `ascensional_difference()` - Calculate AD from declination and pole
  - `semi_arcs()` - Calculate diurnal and nocturnal semi-arcs
  - `meridian_distance()` - Distance from MC with wraparound
  - `oblique_ascension()` - RA adjusted for pole
  - `ecliptic_to_equatorial()` - Coordinate conversion
  - `get_obliquity()` - True obliquity from Swiss Ephemeris

- **Protocols** (no @runtime_checkable, Stellium pattern):
  - `DirectionMethod` - Interface for direction calculation methods
  - `TimeKey` - Interface for arc-to-time conversion

- **67 tests** in `tests/test_directions.py`:
  - Spherical math functions (23 tests)
  - Time keys with Churchill example validation (8 tests)
  - Data models (10 tests)
  - Direction methods (6 tests)
  - DirectionsEngine API (12 tests)
  - DistributionsCalculator (8 tests)
  - Integration and edge cases (varies)

- **Cookbook** (`examples/directions_cookbook.py`): 19 examples covering:
  - Basic directions, multiple planets, all angles
  - Zodiacal vs Mundane method comparison
  - Ptolemy vs Naibod time key comparison
  - Term distributions (life chapters)
  - Real-world examples (life events, future directions)
  - Full analysis export

- **Exports** in `engines/__init__.py`:
  - `DirectionsEngine`, `DirectionResult`, `DirectionArc`
  - `DistributionsCalculator`, `TimeLordPeriod`
  - `ZodiacalDirections`, `MundaneDirections`
  - `PtolemyKey`, `NaibodKey`

Example usage:

```python
from stellium.engines.directions import DirectionsEngine, DistributionsCalculator

# Basic direction
engine = DirectionsEngine(chart)
result = engine.direct("Sun", "ASC")
print(f"Sun to ASC: age {result.age:.1f}")

# Compare methods
z = DirectionsEngine(chart, method="zodiacal").direct("Sun", "ASC")
m = DirectionsEngine(chart, method="mundane").direct("Sun", "ASC")

# Life chapters
periods = DistributionsCalculator(chart).calculate(years=80)
```

#### Draconic Charts (December 9, 2025)

- **`chart.draconic()`**: Transform any chart to its draconic equivalent
  - Rotates all positions so North Node is at 0° Aries
  - Returns a new `CalculatedChart` with all longitudes transformed
  - House cusps are also rotated
  - Handles both "True Node" and "North Node" naming

- **`chart_tags` field**: New field on `CalculatedChart` for tracking transformations
  - Empty tuple `()` by default for natal charts
  - Transformations append tags: `("draconic",)`, `("progressed",)`, etc.
  - Tags accumulate when chaining: `chart.draconic().progressed()` → `("draconic", "progressed")`
  - Serialized in `to_dict()` output

Example usage:

```python
# Create draconic chart
draconic = chart.draconic()
print(draconic.get_object("Sun").sign_position)  # Sun in draconic position
print(draconic.chart_tags)  # ('draconic',)

# North Node is now at 0° Aries
print(draconic.get_object("True Node").longitude)  # 0.0

# Draw and save
draconic.draw("draconic_chart.svg").save()
```

#### Heliocentric Charts (December 9, 2025)

- **`.with_heliocentric()` on ChartBuilder**: Calculate Sun-centered charts
  - Positions calculated as seen from the Sun, not Earth
  - **Earth** appears as a planet (replaces Sun)
  - **Sun** is removed (it's the center point)
  - **Lunar nodes and apogees** are removed (Earth-relative concepts)
  - **Moon** is kept (still has heliocentric position)
  - **Houses and angles** are skipped (Earth-horizon concepts)
  - Adds `"heliocentric"` to `chart_tags`

- **Use cases**:
  - Financial astrology (market timing)
  - Scientific/astronomical contexts
  - Some modern experimental techniques

Example usage:

```python
# Create heliocentric chart
chart = ChartBuilder.from_native(native).with_heliocentric().calculate()

# Earth is now a planet
earth = chart.get_object("Earth")
print(earth.sign_position)  # Earth's position as seen from Sun

# No houses in heliocentric
print(len(chart.house_systems))  # 0

# Chart knows it's heliocentric
print(chart.chart_tags)  # ('heliocentric',)
```

#### Transit Report Sections (December 11, 2025)

- **`StationSection`**: New report section for planetary stations
  - Shows retrograde/direct stations in a date range
  - Beautiful Rich table output with date, time, planet, station type, position, sign
  - Located in new `presentation/sections/transits.py` module

- **`ReportBuilder.with_stations()`**: Builder method for station reports
  - `end` required, `start` defaults to chart date
  - `planets` list customizable (default: Mercury through Pluto)
  - `include_minor` option for Chiron

Example usage:

```python
from datetime import datetime
from stellium import ReportBuilder

report = (ReportBuilder()
    .from_chart(chart)
    .with_stations(
        start=datetime(2024, 1, 1),
        end=datetime(2024, 12, 31)
    )
    .render(format='rich_table'))
```

#### Planetary Station Search (December 11, 2025)

- **`find_station(planet, start)`**: Find next planetary station (retrograde or direct)
  - Returns `Station` with datetime, station_type, longitude, sign
  - Uses bisection algorithm to find precise moment when speed = 0
  - Rejects Sun/Moon (they don't go retrograde)

- **`find_all_stations(planet, start, end)`**: Find all stations in date range
  - Great for retrograde calendars and transit planning

- **`Station` dataclass**: Rich result object with:
  - `station_type`: "retrograde" (turning Rx) or "direct" (turning D)
  - `longitude` and `sign`: Where the planet stations
  - `is_turning_retrograde` / `is_turning_direct`: Convenience properties
  - Nice `__str__`: "Mercury stations retrograde at 27°13' Aries on 2024-04-01"

Example usage:

```python
from stellium.engines import find_station, find_all_stations

# When does Mercury next station?
station = find_station("Mercury", datetime(2024, 1, 1))
print(station)  # Mercury stations direct at 22°10' Sagittarius on 2024-01-02

# All Mercury stations in 2024
stations = find_all_stations("Mercury", datetime(2024, 1, 1), datetime(2024, 12, 31))
for s in stations:
    print(f"{s.datetime_utc.date()}: {s.station_type} at {s.sign}")
```

#### Sign Ingress Search (December 9, 2025)

- **`find_ingress(planet, sign, start)`**: Find next ingress to a specific sign
  - Returns `SignIngress` with datetime, sign, from_sign, speed, retrograde status
  - Supports forward and backward search

- **`find_all_ingresses(planet, sign, start, end)`**: Find all ingresses to a sign in range
  - Useful for finding all vernal equinoxes, Mars returns, etc.

- **`find_next_sign_change(planet, start)`**: Find when planet next changes signs
  - Answers "when does this transit end?" without caring which sign is entered

- **`find_all_sign_changes(planet, start, end)`**: Find all sign changes in range
  - Great for transit calendars and ephemeris generation

- **`SignIngress` dataclass**: Rich result object with:
  - `sign`: Sign being entered
  - `from_sign`: Sign being left
  - `is_retrograde`: Whether planet was retrograde at ingress
  - Nice `__str__` for display

Example usage:

```python
from stellium.engines import find_ingress, find_all_sign_changes

# When does Mars next enter Aries?
ingress = find_ingress("Mars", "Aries", datetime(2024, 1, 1))
print(ingress)  # Mars enters Aries on 2024-04-30 15:32

# All Mercury sign changes in 2024
changes = find_all_sign_changes("Mercury", datetime(2024, 1, 1), datetime(2025, 1, 1))
for c in changes:
    print(f"{c.datetime_utc.date()}: {c.from_sign} -> {c.sign}")
```

#### Void of Course Moon (December 9, 2025)

- **`chart.voc_moon()`**: Check if the Moon is void of course
  - Returns `VOCMoonResult` with detailed timing information
  - Uses longitude search engine for exact datetime calculations
  - **Aspect modes**:
    - `"traditional"` (default): Sun through Saturn (visible planets)
    - `"modern"`: Includes Uranus, Neptune, Pluto
  - Checks all Ptolemaic aspects (conjunction, sextile, square, trine, opposition)

- **`VOCMoonResult` dataclass**: Rich result object with:
  - `is_void`: Whether Moon is currently void of course
  - `void_until`: Exact datetime when void period ends
  - `ends_by`: How void ends - `"aspect"` or `"ingress"`
  - `next_aspect`: Description of next aspect (e.g., "trine Jupiter")
  - `next_sign`: Sign Moon will enter next
  - `ingress_time`: Exact datetime of sign ingress

- **Engine module** (`engines/voc.py`): Standalone calculation function
  - `calculate_voc_moon(chart, aspects="traditional")` for direct use
  - Exported from `stellium.engines`

Example usage:

```python
voc = chart.voc_moon()
if voc.is_void:
    print(f"Moon is VOC until {voc.void_until}")
    print(f"Will enter {voc.next_sign}")
else:
    print(f"Moon will {voc.next_aspect}")
    print(f"Aspect perfects at {voc.void_until}")

# Use modern planets
voc_modern = chart.voc_moon(aspects="modern")
```

### Changed

- **House system engines now return RAMC as the 6th angle**: The `calculate_house_data()` method returns 6 angles (ASC, MC, DSC, IC, Vertex, RAMC) instead of 5, enabling primary directions calculations

### Fixed

- **Timezone handling in progression calculations**: Fixed `calculate_progressed_datetime()` and `calculate_years_elapsed()` in `utils/progressions.py` to handle mixed timezone-aware and timezone-naive datetime comparisons gracefully

## [0.7.0] - 2025-12-03

### Added

#### Arabic Parts Report Section (December 3, 2025)

- **ArabicPartsSection**: New report section for displaying Arabic Parts (Lots)
  - Columns: Part name, Position (degree°Sign minute'), House, Formula (optional), Description (optional)
  - **Modes** for filtering:
    - `mode="all"` - All calculated parts (default)
    - `mode="core"` - 7 Hermetic Lots (Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis)
    - `mode="family"` - Family & Relationship Lots (Father, Mother, Marriage, Children, Siblings)
    - `mode="life"` - Life Topic Lots (Action, Profession, Passion, Illness, Death, etc.)
    - `mode="planetary"` - Planetary Exaltation Lots (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn)
  - **Formula column** (on by default): Shows calculation formula with `*` indicator for sect-aware parts
  - **Description column** (off by default): Shows part meaning/interpretation
  - **Multi-house system support**: Shows abbreviated column headers (Plac, WS, Eq, etc.) when multiple house systems are calculated

- **ReportBuilder method**: `.with_arabic_parts(mode="all", show_formula=True, show_description=False)`

- 23 tests added in `tests/test_presentation_sections.py`

#### MultiWheel Visualization Improvements (December 3, 2025)

- **Automatic canvas scaling for multiwheels**: Charts with more rings automatically get larger canvases for better readability
  - Biwheel (2 charts): 1.0× base size (same as single chart)
  - Triwheel (3 charts): 1.15× base size (15% larger)
  - Quadwheel (4 charts): 1.3× base size (30% larger)
  - Configurable via `multiwheel_canvas_scales` in `ChartWheelConfig`
  - Works with `auto_grow_wheel` - canvas scaling applies first, then auto-grow can expand further if tables extend the canvas

- **RingBoundaryLayer**: New layer that draws circular boundary lines between chart rings
  - Draws at each `chart{N}_ring_outer` radius and at `zodiac_ring_inner`
  - Uses theme's `ring_border` styling (falls back to `border_color` if not set)
  - Automatically added to all multiwheel charts (2, 3, or 4 wheels)

- **PlanetLayer new parameters** for better multiwheel rendering:
  - `info_stack_distance` (default 0.8): Controls distance between glyph and info stack (degree/sign/minute). Smaller values move info closer to glyph.
  - `glyph_size_override` (default None): Override theme's glyph size for smaller rings

- **Automatic scaling for tri/quad wheels** via LayerFactory:
  - Biwheel (2 charts): Normal glyph size (32px), normal info distance (0.8)
  - Triwheel (3 charts): 85% glyph size (27px), tighter info distance (0.6)
  - Quadwheel (4 charts): 75% glyph size (24px), even tighter info distance (0.5)

- **Cross-chart aspects for biwheels**: 2-chart multiwheels now display cross-chart aspects in the center
  - Uses existing `CrossChartAspectEngine` for aspect calculation
  - Enable via `MultiWheelBuilder.from_charts([...]).with_cross_aspects().calculate()`
  - Tri/quad wheels omit aspect lines (too cluttered) - use aspectarian table instead
  - New `MultiWheelAspectLayer` handles rendering

- **New `info_mode="no_sign"`** for PlanetLayer: Shows degree + minutes without sign glyph (e.g., "15°32'")
  - Useful for multiwheels where sign is already visible from zodiac position
  - Tighter 2-row stack (degree + minutes) vs 3-row (degree + sign + minutes)
  - All multiwheel charts now use `no_sign` mode by default

- **AngleLayer degree display**: ASC/MC/DSC/IC now show their degree position (e.g., "15°32'")
  - Degree text appears on opposite side of angle label for visual balance
  - ASC label nudged up, degree nudged down (and vice versa for each angle)

- **Angles on all multiwheel charts**: All charts in a multiwheel now display their angles
  - Previously only innermost chart showed ASC/MC/DSC/IC
  - Now each ring shows its own angles, useful for seeing transit/progressed angles vs natal houses

- **Improved multiwheel headers**: Headers now show detailed info for each chart
  - Biwheels: Side-by-side layout with name, location, date/time for each chart
  - Tri/quad wheels: Compact horizontal columns with label, location, date/time
  - Times now included in tri/quad wheel headers

- **Equalized quadwheel radii**: Chart rings 2/3/4 now have equal width (0.09), with chart 1 slightly larger (0.11)

#### Longitude Search Engine (December 3, 2025)

- **New `engines/search.py`**: Find when celestial objects reach specific longitudes
  - `find_longitude_crossing()`: Find exact time when object crosses a degree
    - Hybrid Newton-Raphson / bisection algorithm for fast, reliable convergence
    - Uses planetary speed from Swiss Ephemeris for quick iteration
    - Handles retrograde motion and stations gracefully (bisection fallback when speed ≈ 0)
    - Proper 360°/0° wraparound handling
    - Forward or backward search direction
  - `find_all_longitude_crossings()`: Find ALL crossings in a date range
    - Useful for Moon transits (~monthly), Mercury retrograde crossings (up to 3)
  - `LongitudeCrossing`: Rich result dataclass with datetime, longitude, speed, is_retrograde

- **Use cases enabled**:
  - Persona charts (when Sun first reaches each natal planet position after birth)
  - Transit searches ("when does Mars hit my natal Venus?")
  - Ingress calculations (equinoxes, solstices, sign ingresses)
  - Transit timeline generation

- **39 tests added** in `tests/test_search.py` covering:
  - Angle normalization helper for 360°/0° wraparound
  - `LongitudeCrossing` dataclass properties and immutability
  - Single crossing search (Sun equinoxes/solstices, Moon, Mars, Mercury)
  - Multiple crossing search (Moon ~13/year, Mercury retrograde multiples)
  - Integration tests with known astronomical events (2024 equinoxes/solstices)
  - Edge cases (longitude normalization, slow outer planets like Chiron)

### Changed

### Fixed

#### Webapp

- Make all page functions async to be able to use NiceGUI >= 3.0.0

## [0.6.0] - 2025-12-02

### Added

#### Uranian Dial Charts (December 1, 2025)

- **Complete Dial Chart Visualization**: Full implementation of Uranian/Hamburg school dial charts
  - **90-degree dial**: Most common, compresses zodiac by 4x - conjunctions, squares, and oppositions all appear as conjunctions
  - **45-degree dial**: Compresses by 8x - also shows semi-squares and sesquiquadrates
  - **360-degree dial**: Full zodiac with rotatable pointer for aspect analysis

- **DialDrawBuilder**: Fluent API for dial chart configuration
  - `chart.draw_dial("dial.svg")` - Basic 90° dial
  - `chart.draw_dial("dial.svg", degrees=45)` - 45° dial
  - `chart.draw_dial("dial.svg", degrees=360)` - 360° dial with pointer
  - `.with_size(800)` - Custom size in pixels
  - `.with_theme("midnight")` - Theme inheritance from main chart themes
  - `.with_rotation(15.0)` - Rotate dial by degrees

- **Dial Layers**:
  - **Background Layer**: Outer border circle
  - **Graduation Layer**: Tick marks every 1° with labels every 5° (or 10° for 360° dial)
  - **Cardinal Points Layer**: 0°/Cardinal, 15°/Fixed, 22.5°/Mutable markers
  - **Modality Wheel**: Inner wheel divided into 3 sectors with zodiac glyphs
  - **Planet Layer**: Natal planet glyphs with collision detection and connector lines
  - **Midpoint Layer**: Midpoints on outer ring (enabled by default) with tick/full notation options
  - **Outer Ring Layer**: For transits, directions, etc. with borders and collision detection
  - **Pointer Layer**: Rotatable pointer for 360° dial analysis

- **Collision Detection**: Adapted from main chart visualization, scaled for dial compression
  - Planets displaced to avoid overlap, with dashed connector lines to true position
  - Midpoints and outer ring positions also use collision detection

- **Midpoint Configuration**:
  - `.with_midpoints(notation="full")` - Show both planet glyphs (e.g., "☉/☽")
  - `.with_midpoints(notation="tick")` - Clean tick marks only
  - `.without_midpoints()` - Hide midpoints

- **Outer Rings for Transits**:
  - `.with_outer_ring(transit.get_planets(), label="Transits")` - Add transit planets
  - Supports multiple outer rings: `ring="outer_ring_1"`, `"outer_ring_2"`, etc.
  - Border circles with tick marks and connector lines

- **360° Dial Pointer**:
  - `.with_pointer("Sun")` - Point to a planet's position
  - `.with_pointer(45.0)` - Point to a specific degree
  - `.without_pointer()` - Hide pointer

- **16-Example Cookbook**: `examples/dial_cookbook.py` demonstrating all dial features
  - Basic dials, dial sizes, themes, midpoints, pointers, transits, outer rings
  - Professional Uranian and Cosmobiology style examples

- 65 tests added in `tests/test_dial_charts.py`

#### TNO and Uranian Planet Support (December 1, 2025)

- **ChartBuilder Methods**:
  - `.with_tnos()` - Include Trans-Neptunian Objects: Eris, Sedna, Makemake, Haumea, Orcus, Quaoar
  - `.with_uranian()` - Include Hamburg hypothetical planets + Aries Point: Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulkanus, Poseidon, Aries Point

- **Aries Point**: Added to the celestial registry as a fundamental Uranian reference point
  - Fixed at 0° Aries (0° longitude)
  - Represents worldly manifestation and the intersection of personal and collective
  - Aliases: AP, Aries 0, Vernal Point, Spring Equinox

- **DialDrawBuilder Methods**:
  - `.with_tnos()` / `.without_tnos()` - Toggle TNOs on dial (default: on)
  - `.with_uranian()` / `.without_uranian()` - Toggle Hamburg planets + Aries Point on dial (default: on)

- **Dial Planet Layer**: Automatically includes TNOs, Hamburg planets, and Aries Point if present in chart

#### Graceful Ephemeris File Handling (December 1, 2025)

- **SwissEphemerisEngine**: Now gracefully handles missing asteroid ephemeris files
  - Returns `None` instead of raising error when `.se1` file is missing
  - Prints helpful warning message with download instructions (once per object per session)
  - Chart calculation continues with available objects
  - Properly handles `AST_OFFSET` (10000) for asteroid MPC numbers

- **Warning Message Format**:

  ```sh
  ⚠️  Missing ephemeris file for Eris (skipping)
     To download, run: stellium ephemeris download-asteroid 136199
     Or manually download from: ast136/ folder
  ```

#### Asteroid Ephemeris Download CLI (December 1, 2025)

- **New CLI Command**: `stellium ephemeris download-asteroid`
  - Download individual asteroids: `stellium ephemeris download-asteroid 136199`
  - Download by name: `stellium ephemeris download-asteroid eris`
  - Download multiple: `stellium ephemeris download-asteroid 136199,90377,50000`
  - Download all common TNOs: `stellium ephemeris download-asteroid --tnos`
  - List available asteroids: `stellium ephemeris download-asteroid --list`

- **Supported Asteroids**:
  - Eris (#136199), Sedna (#90377), Makemake (#136472)
  - Haumea (#136108), Orcus (#90482), Quaoar (#50000)

- **Download Source**: Uses <https://ephe.scryr.io/ephe2/> for long-range asteroid files (6000 year coverage)

- **Download Functions** (in `cli/ephemeris_download.py`):
  - `get_asteroid_filename(number)` - Generate `.se1` filename (long-range format)
  - `get_asteroid_folder(number)` - Determine `ast{n}/` folder
  - `download_asteroid_file(number)` - Download single asteroid with validation
  - `download_common_asteroids()` - Download all common TNOs
  - `resolve_asteroid_input(input)` - Parse numbers, names, or "tnos"

- **File Validation**: Downloads are verified to contain binary ephemeris data, not HTML error pages

#### MultiWheel Charts - Phase 1 (December 1, 2025)

- **MultiWheel dataclass**: Core data structure for 2-4 chart comparisons
  - Holds tuple of `CalculatedChart` objects
  - Auto-generated or custom labels per chart
  - Optional cross-chart aspects between any pair of charts
  - Convenience properties: `chart_count`, `chart1`, `chart2`, `chart3`, `chart4`

- **MultiWheelBuilder**: Fluent API for creating MultiWheel objects
  - `MultiWheelBuilder.from_charts([chart1, chart2, chart3])`
  - `.with_labels(["Natal", "Transit", "Progressed"])`
  - `.with_cross_aspects()` - enables cross-chart aspect calculation
  - `.calculate()` - returns configured MultiWheel

- **Exports**: Available from `stellium` and `stellium.core`

- **Design Plan**: Full implementation plan at `docs/development/multiwheel.md`
  - Phases 2-13 will add visualization support for tri/quad-wheel charts
  - All charts will render INSIDE the zodiac ring (not outside)
  - Each ring gets alternating house fills, dividers, and compact planet info

*Note: The `.draw()` method exists but visualization support is not yet implemented.*

#### Zodiacal Releasing (November 29, 2025)

- **ZodiacalReleasingEngine**: Full implementation of the Hellenistic predictive timing technique
  - Calculates multi-level periods (L1-L4) based on traditional planetary periods
  - L1 (Major): Life chapters lasting years to decades
  - L2 (Sub): Sub-periods within each L1
  - L3/L4: Finer timing divisions (weeks/days)
  - Uses traditional planetary periods: Moon (25), Mercury (20), Venus (8), Sun (19), Mars (15), Jupiter (12), Saturn (27)
  - 208-year full cycle through all 12 signs
  - **NEW: Valens method is now the default** (traditional method with proper loosing of the bond)
    - L1: Years (sign_period × 365.25)
    - L2: Months (sign_period × 30.437)
    - L3: Days (sign_period × 1.0146)
    - L4: Hours (sign_period × 0.0417)

- **Peak and Angular Detection**:
  - Identifies angular signs (1st, 4th, 7th, 10th from Lot)
  - Marks Peak periods (10th from Lot) - times of heightened visibility
  - Detects Loosing of the Bond at L2+ for angular signs

- **NEW: Qualitative Period Analysis**:
  - **Sect-Based Scoring**: Periods evaluated based on chart sect (day/night)
  - **Ruler Roles**: Each period's ruler analyzed for its role in the chart
    - Sect benefic (+2): Jupiter (day) or Venus (night)
    - Contrary benefic (+1): Venus (day) or Jupiter (night)
    - Sect malefic (-1): Saturn (day) or Mars (night) - constructive difficulty
    - Contrary malefic (-2): Mars (day) or Saturn (night) - destructive difficulty
    - Sect light (+1): Sun (day) or Moon (night)
    - Contrary light (0): Moon (day) or Sun (night)
  - **Tenant Roles**: Planets present in the period's sign add their influence
  - **Period Scoring**: Combined score from ruler + tenants (scale: +3 to -3)
    - Peak periods amplify scores (good becomes better, difficult becomes harder)
  - **Sentiment Property**: Quick classification (positive/neutral/challenging)
  - `ZRPeriod` fields: `ruler_role`, `tenant_roles`, `score`, `sentiment`

- **Data Models** (in `core/models.py`):
  - `ZRPeriod`: Individual period at any level with sign, ruler, dates, and status flags
  - `ZRSnapshot`: Complete ZR state at a moment (all active levels)
  - `ZRTimeline`: Full life timeline with query methods

- **ZodiacalReleasingAnalyzer**: Analyzer for ChartBuilder integration
  - Configure multiple lots: `["Part of Fortune", "Part of Spirit"]`
  - Configurable max_level (1-4) and lifespan

- **CalculatedChart convenience methods**:
  - `chart.zodiacal_releasing(lot)` - Get full timeline
  - `chart.zr_at_date(date, lot)` - Get snapshot at specific date
  - `chart.zr_at_age(age, lot)` - Get snapshot at specific age

- **ReportBuilder integration**:
  - `.with_zodiacal_releasing()` - Add ZR section to reports
  - Supports multiple lots (single, list, or all calculated)
  - Three display modes: "snapshot", "timeline", or "both" (default)
  - Query by date or age (defaults to current time)
  - Configurable L3/L4 context window (default ±2 periods)
  - Status indicators: ★ (Peak), ◆ (Angular), ⚡ (Current), LB (Loosing of Bond)
  - **NEW: Quality column** displays score, sentiment icons (✓/—/✗), and ruler roles
  - Legend includes quality score explanation (+/- = Quality Score)

- **Updated `preset_full()`** to include ZR for Part of Fortune and Part of Spirit

- **68 comprehensive tests** covering engine, data models, timeline queries, and integration

- **Cookbook**: `examples/zodiacal_releasing_cookbook.py` with 19 examples
  - **NEW Examples 15-19**: Qualitative analysis demonstrations
  - Example 15: Period quality scoring with ruler roles and tenants
  - Example 16: Timeline with quality scores
  - Example 17: Finding best periods by score
  - Example 18: Sect-based analysis (day vs night charts)
  - Example 19: Valens method details

#### Web App Code Preview for All Pages (December 1, 2025)

- **Python code preview now available on all pages**:
  - Natal Chart page: Already had code preview, updated to use new API
  - Relationships page: New code preview for synastry, composite, and davison charts
  - Timing page: New code preview for transits, progressions, and returns

- **Refactored `code_preview.py` component**:
  - `generate_natal_code()`: Generates Python code for natal charts with full visualization options
  - `generate_relationships_code()`: Generates code for ComparisonBuilder (synastry) and SynthesisBuilder (composite/davison)
  - `generate_timing_code()`: Generates code for transits, progressions, solar/lunar/planetary returns
  - All generated code uses the new `with_chart_image()` and `with_title()` API

- **Working "Copy to Clipboard" button** in code preview dialogs

#### ReportBuilder API Improvements (December 1, 2025)

- **New `with_chart_image(path=None)` method**:
  - Include a chart wheel image in PDF/HTML reports
  - Called without arguments: auto-generates chart SVG alongside the output file
  - With path argument: uses an existing SVG file
  - Auto-generated charts use `preset_standard()` styling
  - SVG saved as `{output_name}_chart.svg` in same directory as PDF

- **New `with_title(title)` method**:
  - Set a custom title for the report cover page
  - If not set, defaults to `"{chart_name} — Natal Chart"` or `"Natal Chart Report"`

- **Simplified `render()` method**:
  - Removed `chart_svg_path` and `title` parameters (use builder methods instead)
  - Smart `show` defaults: `True` for terminal formats, `False` for PDF/HTML
  - Cleaner API reduces boilerplate for PDF generation

- **Before/After comparison**:

  ```python
  # Before (verbose)
  chart.draw("chart.svg").with_theme("celestial").save()
  ReportBuilder().from_chart(chart).preset_full().render(
      format="pdf", file="report.pdf", chart_svg_path="chart.svg",
      title="My Report", show=False
  )

  # After (clean)
  ReportBuilder().from_chart(chart).preset_full()
      .with_chart_image().with_title("My Report")
      .render(format="pdf", file="report.pdf")
  ```

- **Updated cookbook examples** to use new API (9 examples simplified)

#### TypstRenderer Compound Section Support (December 1, 2025)

- **Fixed "unknown section type: compound" in PDF reports**:
  - Added `_render_compound()` method to TypstRenderer
  - Handles nested compound sections with level-3 headings
  - Recursively processes tables, key-value, text, side-by-side tables, and SVGs

- **Added `_render_svg_section()` method**:
  - Saves inline SVG content to temp file for Typst embedding
  - Styled box with gold border matching report theme

- **Affected sections now render correctly in PDFs**:
  - Aspectarian (SVG + table compound)
  - Annual Profections timeline
  - Dispositor section
  - Zodiacal Releasing timeline and snapshot

#### Standalone Aspectarian Generator (November 29, 2025)

- **`generate_aspectarian_svg()`**: Generate standalone aspectarian SVG files
  - Triangle grid for single charts, square grid for comparison/synastry charts
  - Returns SVG string or saves to file
  - Configurable cell size, padding, theme, and aspect palette
  - Optional detailed mode showing orb and applying/separating indicators
  - Uses `ContentMeasurer` for consistent dimension calculations

- **`get_aspectarian_dimensions()`**: Calculate aspectarian dimensions without rendering

- **AspectSection integration**:
  - `.with_aspects()` now includes aspectarian SVG by default (`include_aspectarian=True`)
  - New parameters: `aspectarian_detailed`, `aspectarian_cell_size`, `aspectarian_theme`
  - Returns compound section with aspectarian SVG + aspect table
  - Terminal output shows placeholder with dimensions; HTML/PDF renders the SVG

- **SVG type support in Rich renderer**:
  - New `_render_svg()` and `_print_svg()` methods
  - Terminal shows `[SVG: WxHpx - use HTML/PDF output to view]` placeholder
  - SVG content preserved in data for HTML/PDF rendering

#### Notables Database

- Added 78 births and 12 events.
- Added indexing script and INDEX.md of all entries in the database.

### Changed

### Fixed

- **ZodiacalReleasingEngine**: Fixed sign index wrapping at position 12 (was causing IndexError)
- **Rich Renderer**: Added recursive handling for nested compound sections
- **Asteroid ID Offset**: Fixed `SWISS_EPHEMERIS_IDS` to include `AST_OFFSET` (10000) for TNO asteroid numbers - Swiss Ephemeris requires this offset for MPC-numbered asteroids
- **Ephemeris Download Path**: Fixed `get_data_directory()` in CLI to download to `data/swisseph/ephe/` at project root instead of inside `src/stellium/`
- **SVG Glyph Rendering**: Fixed inline SVG glyph rendering for objects with custom SVG glyphs (e.g., Eris)
  - Previously, SVG glyphs were rendered as `<image>` references which don't work across all browsers
  - Now embeds SVG content inline as nested `<svg>` elements with proper path data
  - Uses `debug=False` to bypass svgwrite's strict path validation for complex path commands
  - Updated `get_glyph()` to return SVG content string instead of file path
  - Added `embed_svg_glyph()` helper function in `visualization/core.py` for parsing and embedding
  - Fixed in both dial charts (`dial/layers.py`) and normal charts (`layers.py`)

## [0.5.0] - 2025-11-28

### Added

#### Dispositor Graphs (November 28, 2025)

- **DispositorEngine**: Calculate planetary and house-based dispositor chains
  - **Planetary Dispositors**: Traditional planet-rules-planet chain analysis
    - Each planet is "disposed" by the ruler of the sign it occupies
    - Find final dispositor: the planet that rules its own sign (e.g., Mars in Aries)
    - Detect mutual receptions: when two planets rule each other's signs
  - **House-Based Dispositors** (Kate's innovation): Life-area flow analysis
    - Traces "what planet rules this house's cusp, and what house is THAT planet in?"
    - Shows how areas of life flow into and support each other
    - Find final dispositor house: the life area that feeds the others
    - Mutual receptions between houses (with ruling planet info)

- **Graphviz rendering** for beautiful SVG output:
  - `render_dispositor_graph()` - Single graph (planetary OR house)
  - `render_both_dispositors()` - Both as labeled subgraphs in one SVG
  - Stellium palette: cream background, warm beige nodes, purple edges
  - Gold highlighting for final dispositor(s)
  - Purple tinting for mutual reception nodes
  - Bidirectional arrows for mutual receptions
  - Planet glyphs (☉♀♂♃♄) for planetary mode

- **ReportBuilder integration**:
  - `.with_dispositors(mode="both")` - Add dispositor analysis to reports
  - Mode options: "planetary", "house", or "both"
  - Shows final dispositor, mutual receptions, and full disposition chains
  - Text output with planet glyphs for CLI

- **26 comprehensive tests** covering engine, rendering, and integration

#### Arc Directions (November 28, 2025)

- **ComparisonBuilder.arc_direction()**: Create arc direction comparisons (natal vs directed chart)
  - Arc directions move ALL points by the same angular distance, preserving natal relationships
  - Supports multiple arc types:
    - `solar_arc`: Progressed Sun - natal Sun (~1°/year actual)
    - `naibod`: Mean solar motion (0.9856°/year)
    - `lunar`: Progressed Moon - natal Moon (~12-13°/year)
    - `chart_ruler`: Uses planet ruling the Ascendant sign
    - `sect`: Day charts use solar arc, night charts use lunar arc
    - Any traditional planet: `"Mars"`, `"Venus"`, `"Jupiter"`, `"Saturn"`, `"Mercury"`
  - Traditional and modern rulership system options for chart_ruler
  - Full biwheel chart support with cross-chart aspects

- **New ComparisonType.ARC_DIRECTION** enum value

- **Arc calculation utilities** in `utils/progressions.py`:
  - `calculate_lunar_arc()`: Arc from Moon's progressed motion
  - `calculate_planetary_arc()`: Arc from any planet's motion

- **18 comprehensive tests** covering all arc types and edge cases

#### Declination Aspects (November 28, 2025)

- **DeclinationAspectEngine**: Calculate Parallel and Contraparallel aspects
  - Parallel: Two bodies at the same declination (same hemisphere) - interpreted like a conjunction
  - Contraparallel: Two bodies at equal declination but opposite hemispheres - interpreted like an opposition
  - Configurable orb (default 1.0°, traditional range 1.0-1.5°)
  - Configurable ObjectTypes to include (default: PLANET, NODE)

- **ChartBuilder integration**:
  - `.with_declination_aspects(orb=1.0)` - Enable declination aspect calculation
  - Results stored in separate `chart.declination_aspects` field

- **CalculatedChart convenience methods**:
  - `chart.get_declination_aspects()` - Get all declination aspects
  - `chart.get_parallels()` - Get only parallel aspects
  - `chart.get_contraparallels()` - Get only contraparallel aspects

- **Registry entries**: Added "Parallel" (∥) and "Contraparallel" (⋕) to ASPECT_REGISTRY with appropriate glyphs and colors

- **ReportBuilder integration**:
  - `.with_declination_aspects()` - Add declination aspects table to reports
  - Shows Planet 1, Aspect (with glyph), Planet 2, Orb, and OOB status
  - Filterable by mode: "all", "parallel", or "contraparallel"

- **19 tests** covering engine, integration, and registry

#### Profections Engine (November 28, 2025)

- **ProfectionEngine**: Comprehensive Hellenistic timing technique implementation
  - Annual profections: Calculate activated house and Lord of Year for any age
  - Monthly profections: Solar ingress method for monthly timing within profection years
  - Multi-point profections: Profect ASC, Sun, Moon, MC, or any point simultaneously
  - Timeline generation: View sequence of Lords across a range of ages
  - Supports Whole Sign (traditional default) or any house system
  - Traditional and modern rulership options

- **CalculatedChart convenience methods**:
  - `chart.profection(age=30)` - Quick annual profection
  - `chart.profection(date="2025-06-15")` - Get annual and monthly for a date
  - `chart.profections(age=30)` - Multi-point profection
  - `chart.profection_timeline(25, 35)` - Generate timeline
  - `chart.lord_of_year(30)` - Quick Lord of Year access

- **Data Models**:
  - `ProfectionResult`: Full details including source, profected house/sign, ruler, ruler position, planets in house
  - `MultiProfectionResult`: Multiple points profected at once with `.lords` property
  - `ProfectionTimeline`: Range of profections with `.lords_sequence()` and `.find_by_lord()` methods

- **46 comprehensive tests** covering all profection functionality

- Added Profections report section (detailed in cookbook file)

### Changed

### Fixed

## [0.4.0] - 2025-11-28

### Added

#### Stellium Web Application (November 27, 2025)

- **Complete NiceGUI Web Application**: Full-featured web interface for Stellium (`web/` module, 5,600+ lines)
  - **5 Pages**: Home, Natal, Relationships, Timing, Explore
  - **11 Reusable Components**: Birth input, chart display, chart options, code preview, header, location input, notable selector, PDF options, report options, time input, unified birth input
  - Built with NiceGUI for reactive, modern UI
  - Beautiful design with Crimson Pro and Cinzel fonts

- **Home Page** (`web/pages/home.py`): Landing page with navigation and introduction

- **Natal Chart Page** (`web/pages/natal.py`): Interactive natal chart builder
  - Birth data input with date/time/location
  - Notable person selector from registry
  - Full chart visualization options (themes, palettes, house systems)
  - PDF report generation with customizable sections
  - Live code preview showing equivalent Python code

- **Relationships Page** (`web/pages/relationships.py`): Relationship chart analysis
  - Support for synastry, composite, and Davison charts
  - Dual chart input with swappable inner/outer positions
  - Cross-aspect analysis
  - Relationship-specific visualization options

- **Timing Page** (`web/pages/timing.py`): Predictive astrology charts
  - Solar, lunar, and planetary returns
  - Secondary progressions with angle methods (quotidian, solar arc, naibod)
  - Transits analysis
  - Transit-to-natal cross-aspects

- **Explore Page** (`web/pages/explore.py`): Notable births browser
  - Search and filter through notables database
  - Quick chart generation from any notable

- **Railway Deployment Configuration**: Production-ready deployment setup
  - `requirements.txt` with all dependencies
  - `Procfile` for Railway/Heroku
  - `railway.json` with healthcheck and restart policy
  - Dynamic PORT binding for cloud deployment
  - Production mode detection via `RAILWAY_ENVIRONMENT`

#### Extended Test Coverage (November 27, 2025)

- **242 New Tests** across 6 test files for improved code coverage:

- **CLI Tests** (`tests/test_cli.py`, 46 tests):
  - Main CLI group and version command
  - Cache management commands (info, clear, size)
  - Chart generation from registry
  - Ephemeris download commands (download, list)
  - File pattern matching and size calculation
  - Error handling for invalid inputs

- **Visualization Layers Tests** (`tests/test_visualization_layers.py`, 29 tests):
  - HeaderLayer initialization and custom values
  - Location parsing (US addresses, international, short, empty, None)
  - Header rendering for single charts, comparisons, and unknown time charts
  - Layer integration tests (zodiac band, planet glyphs, aspects, house cusps)
  - Theme variations (default, dark, classic, sepia)
  - Palette changes (zodiac, planet glyph, aspect)

- **Extended Canvas Tests** (`tests/test_visualization_extended_canvas.py`, 37 tests):
  - `_is_comparison()` helper function validation
  - `_filter_objects_for_tables()` filtering logic
  - PositionTableLayer initialization and style merging
  - HouseCuspTableLayer rendering
  - AspectarianLayer modes and configurations
  - Table layer rendering with different chart types

- **ChartBuilder Extended Tests** (`tests/test_chart_builder_extended.py`, 38 tests):
  - `from_notable()` factory method
  - Sidereal zodiac with various ayanamsas
  - `with_name()` method
  - `with_house_systems()` validation and errors
  - `add_house_system()` incremental building
  - Unknown time chart calculation
  - Cache configuration
  - Component and analyzer integration

- **Comparison Extended Tests** (`tests/test_comparison_extended.py`, 55 tests):
  - Comparison dataclass properties
  - ComparisonBuilder configuration methods
  - Progression auto-calculation (by age, by target date)
  - Angle methods (quotidian, solar arc, naibod)
  - House overlay queries
  - Compatibility scoring
  - `to_dict()` serialization
  - `draw()` visualization integration

- **Returns Builder Tests** (`tests/test_returns_builder.py`, 37 tests):
  - Solar return factory and calculation
  - Lunar return by date and occurrence
  - Planetary returns (Saturn, Jupiter, Mars)
  - Deferred configuration delegation
  - Relocated returns
  - Return moment precision
  - Error handling for invalid inputs

### Changed

### Fixed

## [0.3.0] - 2025-11-27

**The Predictive Astrology Release** - Completes the "predictive trinity" with Returns, Progressions, and a massive performance improvement.

### Added

#### Secondary Progressions Auto-Calculation (November 27, 2025)

- **Enhanced `ComparisonBuilder.progression()`**: Now supports automatic progressed chart calculation
  - **By age**: `ComparisonBuilder.progression(natal, age=30)` - Calculate progressions for age 30
  - **By target date**: `ComparisonBuilder.progression(natal, target_date="2025-06-15")` - Progressed to specific date
  - **Legacy support**: `ComparisonBuilder.progression(natal, progressed_chart)` - Explicit chart still works

- **Three Angle Progression Methods**:
  - `angle_method="quotidian"` (default): Actual daily motion from Swiss Ephemeris - most accurate
  - `angle_method="solar_arc"`: Angles progress at rate of progressed Sun
  - `angle_method="naibod"`: Angles progress at mean Sun rate (59'08"/year)

- **Progression Utilities** (`src/stellium/utils/progressions.py`):
  - `calculate_progressed_datetime(natal_dt, target_dt)` - Core 1 day = 1 year calculation
  - `calculate_solar_arc(natal_sun, progressed_sun)` - Solar arc calculation
  - `calculate_naibod_arc(years)` - Naibod arc calculation
  - `adjust_angles_by_arc(positions, arc)` - Apply arc to angle positions

- **Angle Method Metadata**: Progressed charts include angle adjustment info
  - `angle_method` - Which method was used
  - `angle_arc` - Calculated arc in degrees

- **21 Comprehensive Tests** (`tests/test_progressions.py`):
  - Progression by age and target date
  - All three angle methods verified
  - Progressed Sun (~1°/year) and Moon (~12°/year) motion
  - Backwards compatibility with legacy API
  - Edge cases: negative age, fractional age, large ages

- **Progressions Cookbook** (`examples/progressions_cookbook.py`): 15 comprehensive examples covering all progression types, angle methods, and analysis techniques

Example usage:

```python
from stellium import ComparisonBuilder, ChartBuilder

natal = ChartBuilder.from_notable("Albert Einstein").calculate()

# Progressions for age 30
prog = ComparisonBuilder.progression(natal, age=30).calculate()

# Progressions to a specific date
prog = ComparisonBuilder.progression(natal, target_date="2025-06-15").calculate()

# With solar arc angles
prog = ComparisonBuilder.progression(
    natal, age=30, angle_method="solar_arc"
).calculate()

# Access results
for aspect in prog.cross_aspects:
    print(f"Progressed {aspect.object2.name} {aspect.aspect_name} Natal {aspect.object1.name}")
```

#### Planetary Returns Support (November 27, 2025)

- **ReturnBuilder**: New fluent builder for calculating planetary return charts
  - **Solar Returns**: `ReturnBuilder.solar(natal, year)` - Annual birthday charts
  - **Lunar Returns**: `ReturnBuilder.lunar(natal, near_date=...)` - Monthly Moon returns
  - **Planetary Returns**: `ReturnBuilder.planetary(natal, planet, occurrence=N)` - Saturn, Jupiter, Mars, etc.
  - Composition-based design: wraps ChartBuilder rather than inheriting
  - Full configuration delegation: `.with_house_systems()`, `.with_aspects()`, etc.
  - Relocated returns: `ReturnBuilder.solar(natal, 2025, location="Tokyo, Japan")`

- **Return Chart Metadata**: Charts include return-specific information
  - `chart_type: "return"` - Identifies chart as a return
  - `return_planet` - Which planet returned (Sun, Moon, Saturn, etc.)
  - `natal_planet_longitude` - Original natal position
  - `return_number` - Which occurrence (for Nth return queries)
  - `return_julian_day` - Exact moment of return

- **Julian Day Utilities** (`src/stellium/utils/time.py`):
  - `datetime_to_julian_day(dt)` - Convert Python datetime to Julian Day UT
  - `julian_day_to_datetime(jd, timezone)` - Convert JD back to datetime
  - `offset_julian_day(jd, days)` - Simple offset helper
  - Handles timezone conversion, delta_t correction, edge cases

- **Planetary Crossing Algorithm** (`src/stellium/utils/planetary_crossing.py`):
  - `find_planetary_crossing(planet, target_longitude, start_jd, direction)` - Binary search
  - `find_nth_return(planet, natal_longitude, birth_jd, n)` - Find Nth return
  - `find_return_near_date(planet, natal_longitude, target_jd)` - Find nearest
  - Sub-arcsecond precision (~0.0001°)
  - Correctly handles retrograde motion (only counts direct-motion crossings)
  - Handles 360°→0° wrap-around edge case

- **ChartBuilder Extension Hook**: `_extra_metadata` attribute support
  - Allows wrapper classes (like ReturnBuilder) to inject metadata
  - Duck-typing approach: `if hasattr(self, "_extra_metadata"): ...`
  - Enables extension without modifying ChartBuilder

- **20 Comprehensive Tests** (`tests/test_returns.py`):
  - Solar return precision and timing tests
  - Lunar return by date and by occurrence
  - Saturn return timing (~29 years) and precision
  - Jupiter return (~12 years), Mars return (~2 years)
  - Configuration delegation tests
  - Relocated return tests
  - Edge cases: invalid planets, 360° boundary

- **Clean API Export**: `from stellium import ReturnBuilder`

- **Returns Cookbook** (`examples/returns_cookbook.py`): 14 comprehensive examples demonstrating all return types, configurations, and precision verification

Example usage:

```python
from stellium import ReturnBuilder, ChartBuilder

natal = ChartBuilder.from_notable("Albert Einstein").calculate()

# 2025 Solar Return
sr = ReturnBuilder.solar(natal, 2025).calculate()

# Lunar Return nearest to a date
lr = ReturnBuilder.lunar(natal, near_date="2025-03-15").calculate()

# First Saturn Return (~age 29)
saturn = ReturnBuilder.planetary(natal, "Saturn", occurrence=1).calculate()

# Relocated Solar Return
sr_tokyo = ReturnBuilder.solar(natal, 2025, location="Tokyo, Japan").calculate()
```

#### Sidereal Zodiac Support (November 26, 2025)

- **Full Sidereal Zodiac System**: Stellium now supports both tropical (Western) and sidereal (Vedic) zodiac calculations
  - **Ayanamsa Registry**: Support for 9 common ayanamsa systems (Lahiri, Fagan-Bradley, Raman, Krishnamurti, Yukteshwar, J.N. Bhasin, True Chitrapaksha, True Revati, De Luce)
  - **ZodiacType Enum**: Clean distinction between `TROPICAL` and `SIDEREAL` zodiac types
  - **Smart Defaults**: Tropical is default, sidereal automatically uses Lahiri if no ayanamsa specified

- **ChartBuilder API**: New fluent methods for zodiac selection
  - `.with_sidereal(ayanamsa="lahiri")` - Calculate chart using sidereal zodiac with specified ayanamsa
  - `.with_tropical()` - Explicitly use tropical zodiac (default behavior, useful for overriding)
  - Examples: `.with_sidereal("fagan_bradley")`, `.with_sidereal("raman")`
  - Comprehensive docstrings with usage examples for all ayanamsa systems

- **Chart Metadata**: CalculatedChart now tracks zodiac system information
  - `zodiac_type` - ZodiacType enum (TROPICAL or SIDEREAL)
  - `ayanamsa` - Name of ayanamsa system used (e.g., "lahiri", "fagan_bradley")
  - `ayanamsa_value` - Actual ayanamsa offset in degrees at chart time (e.g., 24.123°)
  - Enables future tropical vs sidereal biwheel comparisons of same native

- **Report Display**: ChartOverviewSection shows zodiac system information
  - Displays zodiac type: "Tropical" or "Sidereal (Lahiri)"
  - Shows ayanamsa offset for sidereal charts: "Ayanamsa: 24°07'48""
  - Formatted as degrees°minutes'seconds" for readability

- **Ayanamsa Utilities**: Helper functions for working with ayanamsa systems
  - `get_ayanamsa(name)` - Get AyanamsaInfo by name (case-insensitive)
  - `get_ayanamsa_value(julian_day, ayanamsa)` - Calculate offset for specific date
  - `list_ayanamsas()` - Get all available ayanamsa names
  - AyanamsaInfo dataclass with name, Swiss Ephemeris constant, description, and tradition

#### Notables Database

- Added ~50 births and 4 events to the database of varying quality

#### Fixed Stars Implementation (November 26, 2025)

- **Complete Fixed Stars System**: Calculate and integrate fixed star positions into charts using Swiss Ephemeris
  - **26 Stars in Registry**: 4 Royal Stars (Aldebaran, Regulus, Antares, Fomalhaut), 11 Major Stars (Sirius, Algol, Spica, etc.), 11 Extended Stars
  - **Tiered System**: Stars organized by astrological importance (Tier 1=Royal, Tier 2=Major, Tier 3=Extended)
  - **Swiss Ephemeris Integration**: Uses `swe.fixstar_ut()` for precise calculations with automatic precession handling

- **FixedStarPosition Model**: New dataclass extending `CelestialPosition` with star-specific fields
  - `constellation` - Traditional constellation (e.g., "Leo", "Scorpio")
  - `bayer` - Bayer designation (e.g., "Alpha Leonis")
  - `tier` - Importance tier (1, 2, or 3)
  - `is_royal` - Boolean for Royal Stars of Persia
  - `magnitude` - Apparent visual magnitude
  - `nature` - Traditional planetary nature (e.g., "Mars/Jupiter")
  - `keywords` - Interpretive keywords tuple

- **FixedStarsComponent**: ChartBuilder component for adding fixed stars to charts
  - `FixedStarsComponent()` - Calculate all 26 registered stars
  - `FixedStarsComponent(royal_only=True)` - Just the four Royal Stars
  - `FixedStarsComponent(stars=["Regulus", "Sirius"])` - Specific stars by name
  - `FixedStarsComponent(tier=2, include_higher_tiers=True)` - Filter by tier

- **SwissEphemerisFixedStarsEngine**: Engine for star position calculations
  - `calculate_stars(julian_day, stars=None)` - Main calculation method
  - `calculate_royal_stars(julian_day)` - Convenience method for Royal Stars
  - `calculate_stars_by_tier(julian_day, tier)` - Filter by tier level
  - Automatic ephemeris path configuration for `sefstars.txt`

- **Registry Functions**: Helper functions for working with star metadata
  - `get_fixed_star_info(name)` - Look up star by name
  - `get_royal_stars()` - Get all four Royal Stars
  - `get_stars_by_tier(tier)` - Filter stars by tier
  - `FIXED_STARS_REGISTRY` - Direct registry access

- **22 Comprehensive Tests**: Full test coverage for registry, engine, component, and integration

- **FixedStarsSection for Reports**: New report section to display fixed stars
  - `.with_fixed_stars()` method on ReportBuilder
  - Tier filtering: `tier=1` for Royal Stars only, `tier=2` for Major, etc.
  - Sort options: `sort_by="longitude"` (zodiacal order), `"magnitude"` (brightest first), `"tier"` (royal first)
  - Includes star name with crown (♔) for Royal Stars, position, constellation, magnitude, nature, keywords
  - Graceful fallback message if FixedStarsComponent not added to chart

- **Report Cookbook Examples**: Four new examples demonstrating fixed stars in reports
  - Example 9b: Full fixed stars report
  - Example 9c: Royal Stars only
  - Example 9d: Fixed stars PDF with chart wheel

- **MidpointAspectsSection for Reports**: New report section showing planets that aspect midpoints
  - `.with_midpoint_aspects()` method on ReportBuilder
  - This is the most useful way to interpret midpoints - which planets activate them?
  - Mode options: `"conjunction"` (default, most important), `"hard"`, or `"all"`
  - Configurable orb (default 1.5°, tighter than regular aspects)
  - Filter to core midpoints (Sun/Moon/ASC/MC) with `midpoint_filter="core"`
  - Sort by `"orb"` (tightest first), `"planet"`, or `"midpoint"`
  - Does NOT calculate midpoint-to-midpoint aspects (only planet-to-midpoint)
  - Example 7b added to report_cookbook.py

### Changed

- **PDF Report Table Headers**: Changed table header color from `primary` to `secondary` purple
  - Section headers use `primary` (`#4a3353` - deep warm purple)
  - Table headers now use `secondary` (`#6b4d6e` - medium warm purple)
  - Creates visual hierarchy where section banners are more prominent than table headers

- **SwissEphemerisEngine**: Updated to support sidereal calculations
  - Now accepts `CalculationConfig` parameter in `calculate_positions()`
  - Sets sidereal mode via `swe.set_sid_mode()` when config specifies sidereal
  - Adds `FLG_SIDEREAL` flag to Swiss Ephemeris calculations automatically
  - All longitude values returned are already sidereal-adjusted (no post-processing needed)

- **House Calculations**: Migrated from `swe.houses()` to `swe.houses_ex()` for sidereal support
  - All house system engines (Placidus, Whole Sign, Koch, etc.) now use `houses_ex()` with flags
  - Accepts `CalculationConfig` parameter in `calculate_house_data()`
  - Properly sets sidereal mode and flags for house cusp calculations
  - Backwards compatible - tropical calculations unchanged

- **CalculationConfig**: Extended with zodiac system fields
  - Added `zodiac_type: ZodiacType = ZodiacType.TROPICAL` (default)
  - Added `ayanamsa: str | None = None` (only used for sidereal)
  - Smart `__post_init__` validation: defaults to "lahiri" if sidereal but no ayanamsa specified

### Fixed

#### Major Performance Improvement (November 27, 2025)

- **60x Faster Chart Calculations**: Removed expensive `get_stats()` call from `ChartBuilder.calculate()`
  - **Root cause**: `get_stats()` was scanning 100,000+ cache files with `rglob("*.pickle")` on EVERY chart calculation
  - **Impact**: Each chart was taking ~1000ms instead of ~10ms
  - **Fix**: Removed automatic cache stats from chart metadata (rarely needed, now available via `stellium.utils.cache.get_cache_stats()`)
  - **Result**: Full test suite dropped from ~5 minutes to ~5 seconds

### Technical Notes

- **No Breaking Changes**: All existing tropical calculations work unchanged (tropical is default)
- **Data Flow**: Sidereal positions flow through aspect/midpoint calculations unchanged (angular separation is zodiac-agnostic)
- **Future-Ready**: Architecture supports tropical vs sidereal biwheel comparisons (validation to be implemented)
- **Swiss Ephemeris Integration**: Clean integration with pyswisseph global state management
- **Thread Safety**: Sidereal mode set before each calculation batch (global state concern acknowledged)

#### Declination Support (November 26, 2025)

- **Equatorial Coordinates**: Full support for declination and right ascension alongside ecliptic coordinates
  - **Dual Coordinate Systems**: Each CelestialPosition now has BOTH ecliptic (longitude/latitude) AND equatorial (right ascension/declination) coordinates
  - **Automatic Calculation**: SwissEphemerisEngine makes two `calc_ut()` calls per planet (one standard, one with `FLG_EQUATORIAL`)
  - **Efficient Caching**: Both coordinate systems are cached separately for performance
  - **Clean Data Model**: Clear separation between ecliptic latitude (distance from ecliptic) and declination (distance from celestial equator)

- **CelestialPosition Extensions**: New fields and properties for equatorial coordinates
  - `declination: float | None` - Distance from celestial equator in degrees (-90° to +90°)
  - `right_ascension: float | None` - Equatorial equivalent of longitude (0° to 360°)
  - `is_out_of_bounds: bool` - Property detecting when declination exceeds Sun's maximum (~23°27')
  - `declination_direction: str` - Returns "north", "south", or "none"

- **Out-of-Bounds Detection**: Identifies planets with extreme declinations
  - Maximum solar declination is ~23.4367° (Tropic of Cancer/Capricorn)
  - Moon, Mercury, Mars, and Venus can go out-of-bounds
  - Jupiter, Saturn, and outer planets rarely or never exceed these bounds
  - Out-of-bounds planets considered to have extra intensity or unconventional expression

- **Declination Report Section**: New `DeclinationSection` displays declination data
  - Shows all planets with their declination values formatted as degrees°minutes'
  - Indicates north/south direction for each planet
  - Highlights out-of-bounds planets with "OOB ⚠" marker
  - Filters out asteroids and minor points for cleaner display
  - Accessed via `.with_declinations()` builder method

- **Future Capabilities**: Foundation for advanced declination techniques
  - Architecture ready for parallel/contraparallel aspect detection
  - Enables traditional declination-based astrological techniques
  - Complete equatorial coordinate system available for custom analysis

## [0.2.0] - 2025-11-26

### Added

#### Report Section Enhancements (November 26, 2025)

- **Multi-House System Planet Positions**: `PlanetPositionSection` now shows house placements for ALL calculated house systems
  - Changed API from `house_system` (singular) to `house_systems` (plural/flexible)
  - New defaults: `house_systems="all"` shows all calculated systems (Placidus, Whole Sign, Koch, etc.)
  - Can specify: `house_systems=["Placidus", "Whole Sign"]` for specific systems, or `house_systems=None` for default only
  - Dynamic column headers with abbreviated system names: "House (Pl)", "House (WS)", "House (Ko)"
  - One column per house system - finally exposes the multi-system data that was already calculated!

- **House Cusps Section**: New `HouseCuspsSection` displays cusp degrees for all house systems
  - Shows all 12 houses with degree + sign + minute formatting ("15° ♈︎ 23'")
  - API: `systems="all"` (default) or list of specific systems
  - Uses same abbreviation system as planet positions for consistency
  - Accessed via `.with_house_cusps(systems="all")` builder method

- **Dignity Section**: New `DignitySection` displays essential dignities with graceful error handling
  - Supports traditional, modern, or both dignity systems: `essential="both"` (default)
  - Two display modes: `show_details=False` shows scores (+9, -5), `show_details=True` shows dignity names
  - Graceful handling: if `DignityComponent()` not added, shows helpful message instead of erroring
  - Message includes example code showing how to add the component
  - Accessed via `.with_dignities(essential="both", show_details=False)` builder method

- **Aspect Pattern Section**: New `AspectPatternSection` displays detected patterns (Grand Trines, T-Squares, Yods, etc.)
  - Shows pattern type, involved planets (with glyphs), element/quality, and focal planet (if applicable)
  - Supports filtering: `pattern_types="all"` (default) or list of specific pattern types
  - Sorting options: `sort_by="type"` (default), `"element"`, or `"count"`
  - Graceful handling: if `AspectPatternAnalyzer()` not added, shows helpful message with example
  - Accessed via `.with_aspect_patterns(pattern_types="all", sort_by="type")` builder method

- **House System Abbreviation Helper**: Added `abbreviate_house_system()` utility function
  - Maps full house system names to 2-4 character codes (e.g., "Placidus" → "Pl", "Whole Sign" → "WS")
  - Used consistently across all report sections for compact, readable column headers
  - Supports 10 common house systems with fallback to first 4 characters

- **ReportBuilder API Updates**: Three new builder methods for enhanced reports
  - `.with_house_cusps(systems="all")` - add house cusps table
  - `.with_dignities(essential="both", show_details=False)` - add dignities table
  - `.with_aspect_patterns(pattern_types="all", sort_by="type")` - add aspect patterns table
  - Updated `.with_planet_positions(house_systems="all")` signature (minor breaking change: `house_system` → `house_systems`)

#### Multi-House System Visualization (November 25, 2025)

- Fixed `with_house_systems("all")` to actually render multiple house systems on the chart wheel
- Secondary house systems render as dashed lines with distinct colors for visual differentiation
- Added `secondary_color` to all 13 themes for theme-aware overlay styling
- `LayerFactory` now properly reads `config.wheel.house_systems` and creates overlay layers
- Info corner displays all rendered house systems (e.g., "Placidus, Whole Sign")
- Supports rendering 2+ house systems with automatic color cycling for additional overlays

#### Aspect Line Style Preservation (November 25, 2025)

- Fixed aspect line dash patterns being lost when using themes other than Classic
- Added `build_aspect_styles_from_palette()` helper that merges palette colors with registry line styles
- All themes now use this helper to preserve ASPECT_REGISTRY's `dash_pattern` and `line_width` metadata
- Themes only override colors, not line styles (solid for major aspects, dashed patterns for minors)

#### Unknown Birth Time Charts (November 25, 2025)

- Added `UnknownTimeChart` model for charts with known date but unknown birth time
- Added `MoonRange` dataclass tracking Moon's daily arc (start/end longitude, sign crossing detection)
- Added `time_unknown` parameter to `Native` class - auto-normalizes to noon
- Added `ChartBuilder.with_unknown_time()` fluent method
- Added `MoonRangeLayer` visualization - semi-transparent arc showing Moon's possible positions
- Unknown time charts skip houses and angles (can't calculate without exact time)
- Theme-aware Moon arc colors using `style["planets"]["glyph_color"]`

#### Chart Header Band (November 25, 2025)

- Added `HeaderLayer` for prominent native info display at top of chart
- Added `HeaderConfig` with customizable height, fonts, and coordinate precision
- Three header modes:
  - **Single chart**: Name (Cinzel font), short location + coordinates, datetime + timezone
  - **Biwheel**: Two-column layout - inner chart left-aligned, outer chart right-aligned
  - **Synthesis**: "Davison: Name1 & Name2" with midpoint coordinates
- Added smart location parsing - extracts "City, State" from verbose geopy strings
- Canvas grows taller (rectangle) when header enabled
- `.with_header()` / `.without_header()` builder methods (header ON by default)
- `ChartInfoLayer` simplified to just house system + ephemeris when header enabled

#### API Convenience Methods (November 24, 2025)

- Added datetime string parsing to `Native` class:
  - Supports ISO 8601: `"1994-01-06 11:47"`, `"1994-01-06T11:47:00"`
  - Supports US format: `"01/06/1994 11:47 AM"`
  - Supports European format: `"06-01-1994 11:47"`
  - Supports date-only: `"1994-01-06"` (defaults to noon)
- Added `ChartBuilder.from_details(datetime, location, *, name=None, time_unknown=False)` convenience method
- Added `ComparisonBuilder` convenience methods:
  - `.synastry(data1, data2)` - for relationship analysis
  - `.transit(natal_data, transit_data)` - for timing analysis
  - `.progression(natal_data, progressed_data)` - for symbolic timing
  - `.compare(data1, data2, comparison_type)` - for programmatic use
- All convenience methods accept tuples `(datetime, location)` or `(datetime, location, name)`

#### Outer Wheel Visualization Improvements (November 24, 2025)

- Added `OuterAngleLayer` for outer wheel angles in biwheel charts
  - Extends outward from zodiac ring
  - Lighter colors and thinner lines than inner angles
- Added `OuterBorderLayer` for visual containment of outer planets
- Added `outer_wheel_angles` styling to all 13 themes
- Inner wheel angles now always display in comparison charts

#### Core Architecture & Models

- Added core dataclass models in `core/models.py`: ObjectType, ChartLocation, ChartDateTime, CelestialPosition, HouseCusps, Aspect, CalculatedChart
- Added `MidpointPosition` subclass of `CelestialPosition` with `object1`, `object2`, and `is_indirect` attributes for type-safe midpoint handling
- Added 4 tests for core dataclass models
- Added Protocol definitions: EphemerisEngine, HouseSystemEngine, AspectEngine, OrbEngine, DignityCalculator, ChartComponent, ReportRenderer, ReportSection
- Added configuration models: AspectConfig, CalculationConfig
- Renamed from `stellium` to `stellium` (entire package).

#### Registries

- Added comprehensive celestial object registry (`core/registry.py`) with 61 objects:
  - All 10 planets (Sun through Pluto + Earth for heliocentric)
  - 3 Lunar Nodes (True Node, Mean Node, South Node)
  - 3 Calculated Points (Mean Apogee/Black Moon Lilith, True Apogee, Vertex)
  - 4 Main Belt Asteroids (Ceres, Pallas, Juno, Vesta)
  - 4 Centaurs (Chiron, Pholus, Nessus, Chariklo)
  - 6 Trans-Neptunian Objects/Dwarf Planets (Eris, Sedna, Orcus, Haumea, Makemake, Quaoar)
  - 8 Uranian/Hamburg School hypothetical planets
  - 8 Notable Fixed Stars (4 Royal Stars + others)
  - Earth (for heliocentric charts)
- Added `CelestialObjectInfo` dataclass with fields: name, display_name, object_type, glyph, glyph_svg_path, swiss_ephemeris_id, category, aliases, description, metadata
- Added registry helper functions: `get_object_info()`, `get_by_alias()`, `get_all_by_type()`, `get_all_by_category()`, `search_objects()`
- Added comprehensive aspect registry with 17 aspects:
  - 5 Major/Ptolemaic aspects (Conjunction, Sextile, Square, Trine, Opposition)
  - 4 Minor aspects (Semisextile, Semisquare, Sesquisquare, Quincunx)
  - 2 Quintile family (Quintile, Biquintile)
  - 3 Septile family (Septile, Biseptile, Triseptile)
  - 3 Novile family (Novile, Binovile, Quadnovile)
- Added `AspectInfo` dataclass with fields: name, angle, category, family, glyph, color, default_orb, aliases, description, metadata
- Added aspect registry helper functions: `get_aspect_info()`, `get_aspect_by_alias()`, `get_aspects_by_category()`, `get_aspects_by_family()`, `search_aspects()`
- Added 80 comprehensive tests for both registries (celestial objects + aspects)
- Added Notables registry for notable births and events
- Added tests for Notables and optimized their usage to use pre-known timezones

#### Engines & Calculators

- Added SwissEphemerisEngine and MockEphemerisEngine with 2 tests
- Added House System engines: PlacidusHouses, WholeSignHouses, KochHouses, EqualHouses with SwissHouseSystemBase helper
- Added multiple OrbEngine implementations: SimpleOrbEngine, LuminariesOrbEngine, ComplexOrbEngine
- Added AspectEngine implementations: ModernAspectEngine, HarmonicAspectEngine with 3 tests
- Added comprehensive Traditional Dignity engine (`engines/dignities/traditional.py`):
  - Essential dignities: Rulership, Exaltation, Triplicity (Day/Night), Terms, Face/Decan
  - Peregrine and mutual reception detection
  - Egyptian bounds support
  - Cooperant triplicity ruler (Dorotheus/Lilly system)
  - Detailed dignity metadata in chart results
- Added Modern Dignity engine (`engines/dignities/modern.py`):
  - Modern rulerships (including outer planets)
  - Sign dispositor chains and final dispositor detection
  - Mutual reception (modern rulerships)
  - Sect-aware chart analysis (Day/Night chart detection)
- Added MidpointCalculator component (`components/midpoints.py`):
  - Direct midpoint calculation (shortest arc)
  - Indirect midpoint calculation (opposite point)
  - Creates `MidpointPosition` instances with component object references
- Added PhaseData data model, and added phase data to relevant planets and asteroids under CelestialPosition.phase during ephemeris engine call.
- Added Comparison charts for transits, synastry and progressions.
- Added Synthesis charts for relationship astrology (`core/synthesis.py`):
  - **Davison charts**: `.davison(chart1, chart2)` - midpoint in time and space, then regular chart calculation
  - **Composite charts**: `.composite(chart1, chart2)` - midpoint of each planet/point position
  - `SynthesisChart` inheriting from `CalculatedChart` for full polymorphism (visualization/reports just work!)
  - `SynthesisBuilder` fluent API with configuration options:
    - `.with_labels("Alice", "Bob")` - custom chart labels
    - `.with_location_method("great_circle" | "simple")` - geographic midpoint calculation (Davison)
    - `.with_houses(True | False | "place")` - house calculation method (Composite)
    - `.with_midpoint_method("short_arc" | "long_arc")` - zodiac midpoint direction (Composite)
  - Great circle (geodesic) geographic midpoint as default - follows Earth's curvature
  - Full source chart storage in result for traceability
  - Helper functions: `calculate_midpoint_longitude()`, `calculate_datetime_midpoint()`, `calculate_location_midpoint()`, `julian_day_to_datetime()`
  - 59 tests covering helpers, Davison, Composite, and visualization inheritance

#### Chart Building & Calculation

- Added Native class for processing datetime and location inputs
- Added ChartBuilder class with 2 tests
- Added builder pattern for composable chart calculation
- Added support for multiple simultaneous house systems per chart
- Added house placement calculations (which house each planet occupies)
- Added chart angle detection (ASC, MC, DSC, IC) with proper ObjectType.ANGLE classification

#### Visualization

- Added comprehensive SVG chart renderer (`visualization/core.py`, 1300+ lines):
  - Multi-house system support with visual differentiation
  - Collision detection and smart planet spreading (6° spacing algorithm)
  - Degree tick marks (5°, 10°, 15°, 20°, 25° marks)
  - Aspect line rendering with configurable styles (color, width, dash patterns)
  - Moon phase visualization in center
  - SVG image glyph support for objects without Unicode glyphs
  - Angle label positioning (ASC, MC, DSC, IC nudged off lines)
  - Customizable styles via style dictionaries
  - Chart inversion support
  - Automatic zodiac ring, house cusps, planet positions, and aspect grid rendering
  - Added moon phase visualization to the chart (center and corners)
  - Added chart corner information layers
  - Added initial version of extended canvas with position tables and aspectarian

#### Presentation & Reporting

- Added complete presentation/report builder system (`presentation/` module):
  - `ReportBuilder` with fluent API for progressive report construction
  - `.from_chart()`, `.with_chart_overview()`, `.with_planet_positions()`, `.with_aspects()`, `.with_midpoints()`, `.with_section()` chainable methods
  - `.render(format, file, show)` unified rendering method supporting terminal display and file output
- Added report sections (`presentation/sections.py`):
  - `ChartOverviewSection` - birth data, location, timezone, house system, sect
  - `PlanetPositionSection` - planet positions with optional house, speed, retrograde status
  - `AspectSection` - aspect tables with filtering (all/major/minor/harmonic), sorting (orb/aspect_type/planet), and orb display
  - `MidpointSection` - midpoint tables with core/all filtering and threshold limiting
  - Extensible via custom sections implementing `ReportSection` protocol
- Added report renderers (`presentation/renderers.py`):
  - `RichTableRenderer` - beautiful terminal output with colors, boxes, and formatting (requires Rich library)
  - `PlainTextRenderer` - ASCII tables with no dependencies
  - Dual-mode rendering: `.print_report()` for terminal (preserves ANSI), `.render_report()` for files (strips ANSI)
- Added comprehensive sorting utilities (`presentation/sections.py`):
  - `get_object_sort_key()` - sorts by type → registry order → swe_id → alphabetical
  - `get_aspect_sort_key()` - sorts by angle (registry order) → angle value → alphabetical
  - Applied to all sections for consistent astrological ordering
- Added typst PDF reporting.

### Removed

- Removed duplicate aspect definitions across multiple files (consolidated into aspect registry)
- Removed duplicate celestial object metadata (consolidated into celestial registry)
- Removed ASPECT_GLYPHS dict from visualization/core.py (now uses aspect registry)
- Removed ASPECT_COLORS dict from presentation.py (now uses aspect registry)

### Changed

#### Architecture & Config Refactors (November 24-25, 2025)

- Refactored `ChartDrawBuilder` to delegate ALL defaults to config classes (single source of truth)
- Split `radii_multipliers` into `single_radii` and `biwheel_radii` for clean chart-type separation
- Config keys now directly match renderer keys (no mapping required)
- Simplified `_calculate_wheel_radii()` from 54 lines to 26 lines
- All zodiac tick marks now use angles line color for consistent visual hierarchy
- `MoonPhaseLayer` now properly wired into `LayerFactory` (was missing!)

#### Other Changes

- Complete restructuring of the package to composable protocol-based design
- Pivoted on houses: Chart supports multiple house systems simultaneously, data models updated
- Changed protocol HouseSystemEngine to output both cusps and chart angles
- Changed aspect configuration from `dict[str, int]` (angles) to `list[str]` (names), with angles retrieved from registry
- Changed orb engines to use aspect registry default orbs instead of hardcoded values
- Changed visualization to build aspect styles from registry metadata (colors, line widths, dash patterns)
- Changed planet position ordering from random/alphabetical to astrological (registry order: Sun → Moon → Mercury → Venus → Mars → Jupiter → Saturn → Uranus → Neptune → Pluto → Nodes → Points)
- Changed aspect ordering in reports from alphabetical to astrological (Conjunction → Sextile → Square → Trine → Opposition by angle)
- Changed midpoint creation from `CelestialPosition` to `MidpointPosition` subclass with component object references
- Changed midpoint sorting from alphabetical by name to registry order by component objects
- Updated display names: "Mean Apogee" → "Black Moon Lilith", "True Node" → "North Node" (using registry display_name field)
- Migrated 7 files to use aspect registry as single source of truth
- Updated ReportBuilder API: consolidated `.render()` and `.to_file()` into single `.render(format, file, show)` method

### Changed

#### November 26, 2025

- **PDF Rendering Now Uses Typst**: Changed `format="pdf"` to use Typst renderer instead of WeasyPrint
  - Typst produces superior output with beautiful typography (Cinzel Decorative, Crimson Pro fonts)
  - Better SVG embedding and star dividers
  - Faster compilation and smaller file sizes
  - WeasyPrint `_to_pdf()` method remains in codebase but is no longer used
  - Migration: `format="typst"` → `format="pdf"` (old format string no longer needed)

### Fixed

#### November 26, 2025

- **MockEphemerisEngine Protocol Mismatch**: Fixed `MockEphemerisEngine.calculate_positions()` to accept optional `config` parameter
  - `SwissEphemerisEngine` accepts `config: CalculationConfig | None` but Mock didn't
  - `ChartBuilder` was passing config to engine, causing `TypeError: takes 4 positional arguments but 5 were given`
  - Also updated `EphemerisEngine` protocol to include optional `config` parameter for consistency

- **Presentation Test API Mismatches**: Fixed tests to match updated `PlanetPositionSection` API
  - Changed `house_system` (singular) to `house_systems` (plural) in tests
  - Updated assertions for `_house_systems_mode` instead of `_house_systems` for "all" mode
  - Fixed assertions to account for glyphs in planet names (`"☉ Sun"` not `"Sun"`)
  - Fixed assertions for aspect names with glyphs (`"△ Trine"` not `"Trine"`)
  - Fixed assertions for house column headers (`"House (Pl)"` not `"House"`)

- **AspectSection mode="all" Returned Empty Table**: Fixed bug where `mode="all"` filtered out all aspects
  - `get_aspects_by_category("All")` returns empty list (not a valid category)
  - Now skips filtering entirely when `mode="all"` to show all calculated aspects

- **DignityComponent Protocol Signature**: Fixed `DignityComponent.calculate()` to match updated `ChartComponent` protocol
  - Added missing `house_placements_map: dict[str, dict[str, int]]` parameter
  - Protocol was updated to include house placements but component wasn't updated
  - Caused `TypeError: takes 5 positional arguments but 6 were given`

- **String Formatting in Error Messages**: Fixed Python syntax errors in graceful error message strings
  - Changed multi-line strings with embedded newlines/quotes to use string concatenation with parentheses
  - Affected `DignitySection` and `AspectPatternSection` helpful messages
  - Prevents parser confusion with mixed quote types and escape sequences

#### November 24-25, 2025

- Fixed `MoonPhaseLayer` not appearing (wasn't wired into `LayerFactory`)
- Fixed moon phase label positioning when header enabled (label_y clamping now accounts for y_offset)
- Fixed `ChartInfoLayer` positioning when header enabled (removed double-counting of header_height)
- Fixed synthesis chart header showing "davison Chart" instead of "Davison: Name1 & Name2" (was using wrong attribute names)
- Fixed biwheel header columns overlapping (added 45%/10%/45% column layout with proper spacing)

#### Earlier Fixes

- Fixed multi-house system chart rendering (Whole Sign fills no longer cover Placidus lines)
- Fixed Rich renderer ANSI code leakage into file output (terminal gets colors, files get plain text)
- Fixed planet collision detection to maintain degree order while spacing (6-planet stelliums now correctly ordered)
- Fixed aspect sorting to use astrological angle order instead of alphabetical
- Fixed midpoint component access via direct object references instead of fragile string parsing

## [0.1.0]

- Initial version of `stellium`
