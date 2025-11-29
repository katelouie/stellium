# Changelog

All notable changes to Stellium will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Notables Database

- Added 40 births and 6 events.

### Changed

### Fixed

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
