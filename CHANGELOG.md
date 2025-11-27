# Changelog

All notable changes to Stellium will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

### Changed

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
