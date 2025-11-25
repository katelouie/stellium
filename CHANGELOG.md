# Changelog

All notable changes to Starlight will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Core Architecture & Models

- Added core dataclass models in `core/models.py`: ObjectType, ChartLocation, ChartDateTime, CelestialPosition, HouseCusps, Aspect, CalculatedChart
- Added `MidpointPosition` subclass of `CelestialPosition` with `object1`, `object2`, and `is_indirect` attributes for type-safe midpoint handling
- Added 4 tests for core dataclass models
- Added Protocol definitions: EphemerisEngine, HouseSystemEngine, AspectEngine, OrbEngine, DignityCalculator, ChartComponent, ReportRenderer, ReportSection
- Added configuration models: AspectConfig, CalculationConfig

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

### Removed

- Removed duplicate aspect definitions across multiple files (consolidated into aspect registry)
- Removed duplicate celestial object metadata (consolidated into celestial registry)
- Removed ASPECT_GLYPHS dict from visualization/core.py (now uses aspect registry)
- Removed ASPECT_COLORS dict from presentation.py (now uses aspect registry)

### Changed

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

### Fixed

- Fixed multi-house system chart rendering (Whole Sign fills no longer cover Placidus lines)
- Fixed Rich renderer ANSI code leakage into file output (terminal gets colors, files get plain text)
- Fixed planet collision detection to maintain degree order while spacing (6-planet stelliums now correctly ordered)
- Fixed aspect sorting to use astrological angle order instead of alphabetical
- Fixed midpoint component access via direct object references instead of fragile string parsing

## [0.1.0]

- Initial version of `starlight`
