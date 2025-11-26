# Stellium Astrology Library - Architecture Documentation

**Version:** 1.0
**Last Updated:** 2025-11-16

## Table of Contents

- [Executive Summary](#executive-summary)
- [Directory Structure](#directory-structure)
- [Core Data Models](#core-data-models)
- [Protocols (Interfaces)](#protocols-interfaces)
- [Builder API](#builder-api)
- [Registries](#registries)
- [Calculation Engines](#calculation-engines)
- [Components](#components)
- [Visualization System](#visualization-system)
- [Presentation & Reporting](#presentation--reporting)
- [Comparison Charts](#comparison-charts)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)
- [Configuration Options](#configuration-options)
- [Common Patterns & Conventions](#common-patterns--conventions)
- [Quick Reference](#quick-reference)

---

## Executive Summary

Stellium is a modern, protocol-driven Python astrology library built on Swiss Ephemeris for NASA-grade astronomical calculations. The architecture follows three core design principles:

### Core Principles

1. **Protocols over Inheritance**: Uses Python protocols (structural typing) instead of class inheritance, allowing flexible composition without coupling
2. **Immutability**: All data models are frozen dataclasses that cannot be modified after creation
3. **Composability**: Features are composed through builder patterns and pluggable engines

### Key Features

- Fluent Builder API for chart construction
- Multiple house system support (23+ systems)
- Comprehensive aspect calculation with customizable orbs
- Essential dignity calculations (traditional & modern)
- Aspect pattern detection (Grand Trines, T-Squares, Yods, etc.)
- Arabic parts and midpoints
- SVG chart rendering with layer system
- Rich terminal report generation
- Synastry and transit comparisons
- Full caching system for performance

---

## Directory Structure

```
src/stellium/
├── __init__.py                  # Main package exports
│
├── core/                        # Core abstractions and data models
│   ├── __init__.py
│   ├── models.py                # Immutable dataclasses (ChartLocation, CelestialPosition, etc.)
│   ├── protocols.py             # Protocol definitions (interfaces)
│   ├── builder.py               # ChartBuilder (fluent API)
│   ├── native.py                # Native & Notable (input parsing)
│   ├── config.py                # Configuration classes
│   ├── registry.py              # Celestial object & aspect metadata registries
│   └── comparison.py            # Synastry/transit comparison system
│
├── engines/                     # Calculation engines
│   ├── __init__.py
│   ├── ephemeris.py             # Planet position calculation (Swiss Ephemeris)
│   ├── houses.py                # House system engines (23+ systems)
│   ├── aspects.py               # Aspect calculation engines
│   ├── orbs.py                  # Orb calculation strategies
│   ├── dignities.py             # Essential dignity calculators
│   └── patterns.py              # Aspect pattern detection
│
├── components/                  # Optional add-on components
│   ├── __init__.py
│   ├── arabic_parts.py          # Arabic parts calculator (25+ lots)
│   ├── midpoints.py             # Midpoint calculator
│   └── dignity.py               # Dignity component wrapper
│
├── visualization/               # SVG chart rendering
│   ├── __init__.py
│   ├── core.py                  # ChartRenderer class
│   ├── drawing.py               # High-level drawing functions
│   ├── layers.py                # Layer system (ZodiacLayer, PlanetLayer, etc.)
│   └── moon_phase.py            # Moon phase visualization
│
├── presentation/                # Report generation
│   ├── __init__.py
│   ├── builder.py               # ReportBuilder (fluent API)
│   ├── sections.py              # Report sections (positions, aspects, etc.)
│   └── renderers.py             # Output renderers (Rich, plain text)
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── cache.py                 # Caching system
│   └── cache_utils.py           # Cache helpers
│
├── data/                        # Data access layer
│   ├── __init__.py
│   └── registry.py              # Notable births registry
│
└── cli/                         # Command-line interface
    ├── __init__.py
    ├── chart.py                 # Chart CLI commands
    ├── ephemeris.py             # Ephemeris management
    └── cache.py                 # Cache management

tests/                           # Test suite
├── test_chart_generation.py    # Chart drawing tests
├── test_core_models.py          # Data model tests
├── test_chart_builder.py        # Builder API tests
├── test_ephemeris_engine.py    # Ephemeris calculations
├── test_aspect_engine.py        # Aspect detection
├── test_integration.py          # End-to-end flows
└── test_notables.py             # Notable registry

examples/                        # Usage examples
└── usage.py                     # Basic usage examples

docs/                            # Documentation
├── ARCHITECTURE.md              # This file
└── planning/                    # Feature planning documents
```

---

## Core Data Models

All models are **frozen dataclasses** (immutable). They live in `core/models.py`.

### Input Models

#### ChartLocation

Represents a geographic location for chart calculation.

```python
@dataclass(frozen=True)
class ChartLocation:
    latitude: float          # -90 to 90 (north positive)
    longitude: float         # -180 to 180 (east positive)
    name: str = ""          # Optional location name
    timezone: str = ""      # Optional timezone identifier
```

**Example:**
```python
location = ChartLocation(
    latitude=47.6062,
    longitude=-122.3321,
    name="Seattle, WA",
    timezone="America/Los_Angeles"
)
```

#### ChartDateTime

Represents a date/time for chart calculation. Always stores UTC internally.

```python
@dataclass(frozen=True)
class ChartDateTime:
    utc_datetime: dt.datetime      # Timezone-aware datetime (UTC)
    julian_day: float              # Julian day for Swiss Ephemeris
    local_datetime: dt.datetime | None = None  # Optional local time
```

**Example:**
```python
from datetime import datetime, timezone

chart_dt = ChartDateTime(
    utc_datetime=datetime(2000, 1, 6, 20, 0, tzinfo=timezone.utc),
    julian_day=2451550.3333333,
    local_datetime=datetime(2000, 1, 6, 12, 0)  # PST
)
```

### Positional Data Models

#### ObjectType (Enum)

Categorizes celestial objects.

```python
class ObjectType(Enum):
    PLANET = "planet"
    ANGLE = "angle"              # ASC, MC, DSC, IC
    ASTEROID = "asteroid"
    POINT = "point"              # Lilith, etc.
    NODE = "node"                # North/South Node
    ARABIC_PART = "arabic_part"
    MIDPOINT = "midpoint"
    FIXED_STAR = "fixed_star"
```

#### CelestialPosition

The fundamental positional data structure for all celestial objects.

```python
@dataclass(frozen=True)
class CelestialPosition:
    # Identity
    name: str                         # "Sun", "Moon", "Ascendant", etc.
    object_type: ObjectType

    # Positional data (ecliptic coordinates)
    longitude: float                  # 0-360 degrees
    latitude: float = 0.0             # Degrees north/south of ecliptic
    distance: float = 0.0             # AU from Earth

    # Velocity (degrees per day)
    speed_longitude: float = 0.0
    speed_latitude: float = 0.0
    speed_distance: float = 0.0

    # Derived fields (auto-calculated in __post_init__)
    sign: str = field(init=False)              # "Aries", "Taurus", etc.
    sign_degree: float = field(init=False)     # 0-30 (degree within sign)
    is_retrograde: bool = field(init=False)    # True if speed_longitude < 0

    # Optional phase data (for Moon/planets)
    phase: PhaseData | None = None
```

**Key Properties:**

- `sign_position`: Human-readable string (e.g., "15°23' Aries")
- `sign`: Automatically calculated from longitude
- `sign_degree`: Automatically calculated from longitude
- `is_retrograde`: Automatically determined from speed_longitude

**Example:**
```python
sun = CelestialPosition(
    name="Sun",
    object_type=ObjectType.PLANET,
    longitude=285.5,           # 15°30' Capricorn
    speed_longitude=1.0
)

print(sun.sign)           # "Capricorn"
print(sun.sign_degree)    # 15.5
print(sun.sign_position)  # "15°30' Capricorn"
print(sun.is_retrograde)  # False
```

#### MidpointPosition

Extends `CelestialPosition` for midpoints between two objects.

```python
@dataclass(frozen=True)
class MidpointPosition(CelestialPosition):
    object1: CelestialPosition      # First component planet
    object2: CelestialPosition      # Second component planet
    is_indirect: bool = False       # True for indirect (far) midpoint
```

**Example:**
```python
# Sun/Moon midpoint at 150°
midpoint = MidpointPosition(
    name="Sun/Moon",
    object_type=ObjectType.MIDPOINT,
    longitude=150.0,
    object1=sun_position,
    object2=moon_position,
    is_indirect=False
)
```

#### PhaseData

Stores phase information for the Moon or planets.

```python
@dataclass(frozen=True)
class PhaseData:
    phase_angle: float              # 0-360° (angle from Sun)
    illuminated_fraction: float     # 0.0-1.0 (0% to 100%)
    elongation: float               # Angular distance from Sun
    apparent_diameter: float        # arc seconds
    apparent_magnitude: float       # visual magnitude
    geocentric_parallax: float = 0.0
```

**Key Properties:**

- `is_waxing`: Whether illumination is increasing
- `phase_name`: "New", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full", "Waning Gibbous", "Last Quarter", "Waning Crescent"

**Example:**
```python
moon_phase = PhaseData(
    phase_angle=95.0,
    illuminated_fraction=0.42,
    elongation=95.0,
    apparent_diameter=1800.0,
    apparent_magnitude=-10.5
)

print(moon_phase.phase_name)  # "Waxing Gibbous"
print(moon_phase.is_waxing)   # True
```

### House Data Models

#### HouseCusps

Stores house cusps for a specific house system.

```python
@dataclass(frozen=True)
class HouseCusps:
    system: str                    # "Placidus", "Whole Sign", "Koch", etc.
    cusps: tuple[float, ...]       # 12 cusps as longitudes (0-360°)
```

**Key Methods:**

- `get_cusp(house_number: int) -> float`: Get cusp longitude for house 1-12
- `get_sign(house_number: int) -> str`: Get zodiac sign on cusp
- `get_description(house_number: int) -> str`: Human-readable description

**Example:**
```python
placidus = HouseCusps(
    system="Placidus",
    cusps=(15.0, 45.0, 72.0, 105.0, 138.0, 165.0,
           195.0, 225.0, 252.0, 285.0, 318.0, 345.0)
)

print(placidus.get_cusp(1))         # 15.0
print(placidus.get_sign(1))         # "Aries"
print(placidus.get_description(1))  # "House 1 (Placidus): 15°00' Aries"
```

### Aspect Data Models

#### Aspect

Represents an aspect between two celestial objects.

```python
@dataclass(frozen=True)
class Aspect:
    object1: CelestialPosition
    object2: CelestialPosition
    aspect_name: str               # "Conjunction", "Trine", "Square", etc.
    aspect_degree: int             # 0, 60, 90, 120, 180, etc.
    orb: float                     # Actual orb in degrees (always positive)
    is_applying: bool | None = None  # True if orb decreasing, False if increasing
```

**Key Properties:**

- `description`: Human-readable string (e.g., "Sun Trine Moon (orb: 2.3°)")

**Example:**
```python
aspect = Aspect(
    object1=sun_position,
    object2=moon_position,
    aspect_name="Trine",
    aspect_degree=120,
    orb=2.3,
    is_applying=True
)

print(aspect.description)  # "Sun Trine Moon (orb: 2.3°, applying)"
```

#### ComparisonAspect

Extends `Aspect` for synastry/transit aspects between two different charts.

```python
@dataclass(frozen=True)
class ComparisonAspect(Aspect):
    chart1_object: CelestialPosition    # Object from chart 1
    chart2_object: CelestialPosition    # Object from chart 2
```

#### AspectPattern

Represents a geometric aspect pattern (Grand Trine, T-Square, etc.).

```python
@dataclass(frozen=True)
class AspectPattern:
    name: str                      # "Grand Trine", "T-Square", "Yod", etc.
    planets: list[CelestialPosition]
    aspects: list[Aspect]
    element: str | None = None     # "Fire", "Earth", "Air", "Water"
    quality: str | None = None     # "Cardinal", "Fixed", "Mutable"
```

**Key Properties:**

- `focal_planet`: For patterns with an apex (T-Square, Yod)

**Example:**
```python
grand_trine = AspectPattern(
    name="Grand Trine",
    planets=[sun, mars, jupiter],
    aspects=[sun_trine_mars, mars_trine_jupiter, jupiter_trine_sun],
    element="Fire"
)
```

### Chart Output Models

#### CalculatedChart

The main output of chart calculation. Contains all calculated data.

```python
@dataclass(frozen=True)
class CalculatedChart:
    # Input data
    datetime: ChartDateTime
    location: ChartLocation

    # Calculated data
    positions: tuple[CelestialPosition, ...]
    house_systems: dict[str, HouseCusps]           # {"Placidus": HouseCusps, ...}
    house_placements: dict[str, dict[str, int]]    # {"Placidus": {"Sun": 10, ...}}
    aspects: tuple[Aspect, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    calculation_timestamp: dt.datetime = field(default_factory=...)
```

**Key Query Methods:**

Object Queries:
```python
chart.get_object(name: str) -> CelestialPosition | None
chart.get_planets() -> list[CelestialPosition]
chart.get_angles() -> list[CelestialPosition]  # ASC, MC, DSC, IC, Vertex
chart.get_points() -> list[CelestialPosition]  # Lilith, etc.
chart.get_nodes() -> list[CelestialPosition]   # North/South Node
```

House Queries:
```python
chart.get_house(object_name: str, system_name: str = "Placidus") -> int
chart.get_houses(system_name: str = "Placidus") -> HouseCusps
```

Dignity Queries:
```python
chart.get_dignities(system: str = "traditional") -> dict
chart.get_planet_dignity(planet_name: str, system: str) -> dict
chart.get_mutual_receptions(system: str) -> list
chart.get_accidental_dignities(system: str = "Placidus") -> dict
chart.get_strongest_planet(system: str) -> str  # Almuten
chart.get_planet_total_score(planet, essential_system, accidental_system) -> float
```

Utility Methods:
```python
chart.sect() -> str  # "day" or "night"
chart.to_dict() -> dict  # JSON-serializable
```

**Example:**
```python
# Query objects
sun = chart.get_object("Sun")
print(f"{sun.name} is at {sun.sign_position}")

# Get house placement
sun_house = chart.get_house("Sun", "Placidus")
print(f"Sun is in house {sun_house}")

# Get dignities
sun_dignity = chart.get_planet_dignity("Sun", "traditional")
print(f"Sun dignity: {sun_dignity}")

# Check sect
print(f"Chart sect: {chart.sect()}")  # "day" or "night"
```

#### Comparison

Represents a comparison between two charts (synastry or transits).

```python
@dataclass(frozen=True)
class Comparison:
    comparison_type: ComparisonType          # SYNASTRY or TRANSIT
    chart1: CalculatedChart                  # Native/inner chart
    chart2: CalculatedChart                  # Partner/transit/outer chart
    cross_aspects: tuple[ComparisonAspect, ...]
    house_overlays: tuple[HouseOverlay, ...]
    chart1_label: str = "Native"
    chart2_label: str = "Other"
```

**Example:**
```python
synastry = create_synastry(native1, native2)

# Access cross-chart aspects
for aspect in synastry.cross_aspects:
    print(f"{aspect.chart1_object.name} {aspect.aspect_name} {aspect.chart2_object.name}")

# Check house overlays
for overlay in synastry.house_overlays:
    print(f"{overlay.planet_name} falls in partner's house {overlay.house_number}")
```

---

## Protocols (Interfaces)

Protocols define **structural interfaces** without requiring inheritance. Any class that matches the protocol's signature can be used.

All protocols are defined in `core/protocols.py`.

### Calculation Engine Protocols

#### EphemerisEngine

Calculates planetary positions.

```python
class EphemerisEngine(Protocol):
    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None
    ) -> list[CelestialPosition]:
        """Calculate positions for requested objects."""
        ...
```

**Implementations:**
- `SwissEphemerisEngine` (default, in `engines/ephemeris.py`)
- `MockEphemerisEngine` (for testing)

**Example Implementation:**
```python
class CustomEphemerisEngine:
    def calculate_positions(self, datetime, location, objects=None):
        # Your calculation logic here
        return [CelestialPosition(...), ...]

# Use it
chart = ChartBuilder.from_native(native).with_ephemeris(CustomEphemerisEngine()).calculate()
```

#### HouseSystemEngine

Calculates house cusps and angles.

```python
class HouseSystemEngine(Protocol):
    @property
    def system_name(self) -> str:
        """Name of the house system (e.g., 'Placidus')."""
        ...

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """
        Calculate house cusps and angles.

        Returns:
            (HouseCusps, [ASC, MC, DSC, IC, Vertex])
        """
        ...

    def assign_houses(
        self,
        positions: list[CelestialPosition],
        cusps: HouseCusps
    ) -> dict[str, int]:
        """
        Assign house numbers to positions.

        Returns:
            {object_name: house_number}
        """
        ...
```

**Implementations (in `engines/houses.py`):**
- `PlacidusHouses` (default)
- `WholeSignHouses`
- `KochHouses`
- `EqualHouses`
- Plus 20+ more via Swiss Ephemeris

**Example:**
```python
chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .calculate()
)

# Access different systems
placidus_sun_house = chart.get_house("Sun", "Placidus")
whole_sign_sun_house = chart.get_house("Sun", "Whole Sign")
```

#### AspectEngine

Finds aspects between celestial objects.

```python
class AspectEngine(Protocol):
    def calculate_aspects(
        self,
        positions: list[CelestialPosition],
        orb_engine: OrbEngine
    ) -> list[Aspect]:
        """Calculate aspects between positions using orb engine."""
        ...
```

**Implementations (in `engines/aspects.py`):**
- `ModernAspectEngine`: Configurable major/minor aspects
- `HarmonicAspectEngine`: Harmonic aspects (H5, H7, H9, etc.)

**Example:**
```python
from stellium.engines import ModernAspectEngine
from stellium.core.config import AspectConfig

config = AspectConfig(
    aspects=["Conjunction", "Trine", "Square", "Opposition"],
    include_angles=True
)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine(config))
    .calculate()
)

for aspect in chart.aspects:
    print(aspect.description)
```

#### OrbEngine

Determines orb allowances for aspects.

```python
class OrbEngine(Protocol):
    def get_orb_allowance(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str
    ) -> float:
        """Return maximum orb in degrees for this aspect."""
        ...
```

**Implementations (in `engines/orbs.py`):**
- `SimpleOrbEngine`: One orb per aspect type
- `LuminariesOrbEngine`: Wider orbs for Sun/Moon
- `ComplexOrbEngine`: Cascading priority matrix

**Example:**
```python
from stellium.engines import LuminariesOrbEngine

orb_engine = LuminariesOrbEngine(
    luminary_orbs={"Conjunction": 10.0, "Trine": 8.0},
    default_orbs={"Conjunction": 8.0, "Trine": 6.0}
)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .with_orbs(orb_engine)
    .calculate()
)
```

### Component Protocols

#### ChartComponent

Adds new calculated positions to a chart (Arabic parts, midpoints, etc.).

```python
class ChartComponent(Protocol):
    @property
    def component_name(self) -> str:
        """Name of the component."""
        ...

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]]
    ) -> list[CelestialPosition]:
        """
        Calculate additional positions.

        Returns:
            New positions to add to the chart
        """
        ...
```

**Implementations:**
- `ArabicPartsCalculator` (in `components/arabic_parts.py`)
- `MidpointCalculator` (in `components/midpoints.py`)
- `DignityComponent` (in `components/dignity.py`)
- `AccidentalDignityComponent` (in `components/dignity.py`)

**Example:**
```python
from stellium.components import ArabicPartsCalculator

chart = (
    ChartBuilder.from_native(native)
    .add_component(ArabicPartsCalculator())
    .calculate()
)

# Access calculated Arabic parts
lot_of_fortune = chart.get_object("Lot of Fortune")
print(f"Lot of Fortune: {lot_of_fortune.sign_position}")
```

#### ChartAnalyzer

Analyzes a chart and stores findings in metadata.

```python
class ChartAnalyzer(Protocol):
    @property
    def analyzer_name(self) -> str:
        """Name of the analyzer."""
        ...

    @property
    def metadata_name(self) -> str:
        """Key to use in chart.metadata."""
        ...

    def analyze(self, chart: CalculatedChart) -> list | dict:
        """
        Analyze the chart.

        Returns:
            Analysis results (stored in chart.metadata[metadata_name])
        """
        ...
```

**Implementations:**
- `AspectPatternAnalyzer` (in `engines/patterns.py`)

**Example:**
```python
from stellium.engines import AspectPatternAnalyzer

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .add_analyzer(AspectPatternAnalyzer())
    .calculate()
)

# Access detected patterns
patterns = chart.metadata.get('aspect_patterns', [])
for pattern in patterns:
    print(f"Found {pattern.name}: {[p.name for p in pattern.planets]}")
```

### Presentation Protocols

#### ReportSection

Generates data for a report section.

```python
class ReportSection(Protocol):
    @property
    def section_name(self) -> str:
        """Name of the section."""
        ...

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate section data.

        Returns:
            Dictionary with 'type', 'headers', 'rows', etc.
        """
        ...
```

**Implementations (in `presentation/sections.py`):**
- `ChartOverviewSection`
- `PlanetPositionSection`
- `AspectSection`
- `MidpointSection`

#### ReportRenderer

Renders report sections to output format.

```python
class ReportRenderer(Protocol):
    def render_section(self, section_name: str, section_data: dict) -> str:
        """Render a single section."""
        ...

    def render_report(self, sections: list[tuple[str, dict]]) -> str:
        """Render complete report from sections."""
        ...
```

**Implementations (in `presentation/renderers.py`):**
- `RichTableRenderer`: Rich terminal output
- `PlainTextRenderer`: Plain text tables

---

## Builder API

The Builder API provides a fluent interface for constructing charts.

### Native (Input Parser)

`Native` handles flexible input formats and produces clean, immutable data.

**Location:** `core/native.py`

```python
class Native:
    datetime: ChartDateTime
    location: ChartLocation

    def __init__(
        self,
        datetime_input: dt.datetime | ChartDateTime | dict,
        location_input: str | ChartLocation | tuple | dict
    ):
        """
        Create a Native from flexible inputs.

        datetime_input can be:
        - datetime object (naive or aware)
        - ChartDateTime object
        - dict with datetime info

        location_input can be:
        - Location name string (geocoded automatically)
        - (latitude, longitude) tuple
        - ChartLocation object
        - dict with lat/lon
        """
```

**Features:**
- Accepts naive/aware datetimes
- Geocodes location names to coordinates
- Finds timezones automatically
- Converts everything to UTC for calculations
- Immutable output (ChartDateTime, ChartLocation)

**Examples:**

Simple:
```python
from datetime import datetime
from stellium.core.native import Native

# Naive datetime + location name
native = Native(
    datetime(2000, 1, 6, 12, 0),
    "Seattle, WA"
)
```

Explicit:
```python
from datetime import datetime, timezone

# Aware datetime + coordinates
native = Native(
    datetime(2000, 1, 6, 20, 0, tzinfo=timezone.utc),
    (47.6062, -122.3321)
)
```

With timezone:
```python
import pytz

# Local timezone + location name
pacific = pytz.timezone('America/Los_Angeles')
native = Native(
    pacific.localize(datetime(2000, 1, 6, 12, 0)),
    "Seattle, WA"
)
```

### Notable (Named Births Registry)

Quick access to notable birth charts.

**Location:** `core/native.py`

```python
class Notable:
    @staticmethod
    def get(name: str) -> Native:
        """Get a notable person's birth data by name."""
        ...

    @staticmethod
    def list_all() -> list[str]:
        """List all available notable names."""
        ...

    @staticmethod
    def search(query: str) -> list[str]:
        """Search for notables by name."""
        ...
```

**Example:**
```python
from stellium.core.native import Notable

# Get Einstein's chart
einstein = Notable.get("Albert Einstein")

# List all notables
all_notables = Notable.list_all()

# Search
physicists = Notable.search("Einstein")
```

### ChartBuilder

The main entry point for creating charts. Provides a fluent API.

**Location:** `core/builder.py`

```python
class ChartBuilder:
    def __init__(self, datetime: ChartDateTime, location: ChartLocation):
        """Create builder from datetime and location."""
        ...
```

#### Factory Methods

```python
@classmethod
def from_native(cls, native: Native) -> "ChartBuilder":
    """Create from Native object."""
    ...

@classmethod
def from_notable(cls, name: str) -> "ChartBuilder":
    """Create from notable person's name."""
    ...
```

#### Configuration Methods (Fluent)

```python
# Engines
def with_ephemeris(self, engine: EphemerisEngine) -> "ChartBuilder":
    """Set ephemeris engine."""
    ...

def with_house_systems(self, engines: list[HouseSystemEngine]) -> "ChartBuilder":
    """Set house system engines (replaces all)."""
    ...

def add_house_system(self, engine: HouseSystemEngine) -> "ChartBuilder":
    """Add a house system engine."""
    ...

def with_aspects(self, engine: AspectEngine | None) -> "ChartBuilder":
    """Set aspect engine (None to disable)."""
    ...

def with_orbs(self, engine: OrbEngine) -> "ChartBuilder":
    """Set orb engine."""
    ...

# Configuration
def with_config(self, config: CalculationConfig) -> "ChartBuilder":
    """Set calculation config (which objects to calculate)."""
    ...

# Components & Analyzers
def add_component(self, component: ChartComponent) -> "ChartBuilder":
    """Add a chart component (Arabic parts, midpoints, etc.)."""
    ...

def add_analyzer(self, analyzer: ChartAnalyzer) -> "ChartBuilder":
    """Add a chart analyzer (pattern detection, etc.)."""
    ...

# Caching
def with_cache(
    self,
    cache: Cache | None,
    cache_chart: bool = False,
    cache_key_prefix: str = ""
) -> "ChartBuilder":
    """Configure caching."""
    ...
```

#### Execution

```python
def calculate(self) -> CalculatedChart:
    """
    Execute calculation and return immutable chart.

    Execution order:
    1. Calculate planetary positions (ephemeris)
    2. Calculate house systems and angles
    3. Assign house placements for all systems
    4. Run components (Arabic parts, etc.)
    5. Calculate aspects (if engine provided)
    6. Run analyzers (patterns, etc.)
    7. Return frozen CalculatedChart
    """
    ...
```

#### Default Configuration

If you don't specify engines/config, these defaults are used:

- Ephemeris: `SwissEphemerisEngine()`
- Houses: `[PlacidusHouses()]`
- Aspects: `None` (no aspects calculated)
- Orbs: `SimpleOrbEngine()`
- Config: `CalculationConfig()` (standard planets)

#### Usage Examples

**Simple (using defaults):**
```python
from stellium.core.builder import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").calculate()
```

**With aspects:**
```python
from stellium.engines import ModernAspectEngine

chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects(ModernAspectEngine())
    .calculate()
)
```

**Multiple house systems:**
```python
from stellium.engines import PlacidusHouses, WholeSignHouses, KochHouses

chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses(), KochHouses()])
    .calculate()
)

# Access different systems
print(chart.get_house("Sun", "Placidus"))
print(chart.get_house("Sun", "Whole Sign"))
print(chart.get_house("Sun", "Koch"))
```

**With components:**
```python
from stellium.components import ArabicPartsCalculator, MidpointCalculator

chart = (
    ChartBuilder.from_native(native)
    .add_component(ArabicPartsCalculator())
    .add_component(MidpointCalculator())
    .calculate()
)

# Access calculated data
lot_of_fortune = chart.get_object("Lot of Fortune")
sun_moon_midpoint = chart.get_object("Sun/Moon")
```

**Full customization:**
```python
from stellium.core.builder import ChartBuilder
from stellium.core.config import CalculationConfig, AspectConfig
from stellium.engines import (
    PlacidusHouses,
    WholeSignHouses,
    ModernAspectEngine,
    LuminariesOrbEngine,
    AspectPatternAnalyzer
)
from stellium.components import ArabicPartsCalculator, DignityComponent

# Configure what to calculate
calc_config = CalculationConfig(
    include_planets=["Sun", "Moon", "Mercury", "Venus", "Mars",
                     "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
    include_nodes=True,
    include_chiron=True,
    include_asteroids=["Ceres", "Pallas", "Juno", "Vesta"]
)

# Configure aspects
aspect_config = AspectConfig(
    aspects=["Conjunction", "Sextile", "Square", "Trine", "Opposition"],
    include_angles=True,
    include_nodes=True
)

# Build chart
chart = (
    ChartBuilder.from_native(native)
    .with_config(calc_config)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine(aspect_config))
    .with_orbs(LuminariesOrbEngine())
    .add_component(ArabicPartsCalculator())
    .add_component(DignityComponent())
    .add_analyzer(AspectPatternAnalyzer())
    .calculate()
)
```

---

## Registries

Registries provide comprehensive metadata for celestial objects and aspects.

### Celestial Object Registry

**Location:** `core/registry.py`

Stores metadata for all supported celestial objects.

#### CelestialObjectInfo

```python
@dataclass(frozen=True)
class CelestialObjectInfo:
    name: str                        # "Mean Apogee"
    display_name: str                # "Black Moon Lilith"
    object_type: ObjectType
    glyph: str                       # Unicode symbol (☉, ☽, etc.)
    glyph_svg_path: str | None       # Custom SVG path for rendering
    swiss_ephemeris_id: int | None   # Swiss Ephemeris object ID
    category: str | None             # "Centaur", "TNO", "Big Four", etc.
    aliases: list[str]               # Alternative names
    description: str
    metadata: dict[str, Any]         # Additional data
```

#### Registry Contents

**Traditional Planets (7):**
- Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn

**Modern Planets (3):**
- Uranus, Neptune, Pluto

**Lunar Nodes:**
- North Node (True & Mean)
- South Node (True & Mean)

**Calculated Points:**
- Mean Apogee (Black Moon Lilith)
- True Apogee
- Vertex

**Big Four Asteroids:**
- Ceres, Pallas, Juno, Vesta

**Centaurs:**
- Chiron, Pholus, Nessus, Chariklo, Asbolus

**Trans-Neptunian Objects (TNOs):**
- Eris, Sedna, Makemake, Haumea, Quaoar, Orcus

**Uranian/Hamburg Planets:**
- Cupido, Hades, Zeus, Kronos, Apollon, Admetos, Vulcanus, Poseidon

**Fixed Stars:**
- Regulus, Aldebaran, Antares, Fomalhaut (Royal Stars)

#### Helper Functions

```python
def get_object_info(name: str) -> CelestialObjectInfo:
    """Get info by exact name."""
    ...

def get_by_alias(alias: str) -> CelestialObjectInfo | None:
    """Get info by alias."""
    ...

def get_all_by_type(object_type: ObjectType) -> list[CelestialObjectInfo]:
    """Get all objects of a type."""
    ...

def get_all_by_category(category: str) -> list[CelestialObjectInfo]:
    """Get all objects in a category."""
    ...

def search_objects(query: str) -> list[CelestialObjectInfo]:
    """Search by name/alias/description."""
    ...
```

**Example:**
```python
from stellium.core.registry import get_object_info, get_all_by_type

# Get info
lilith_info = get_object_info("Mean Apogee")
print(f"{lilith_info.display_name}: {lilith_info.glyph}")

# Get all asteroids
asteroids = get_all_by_type(ObjectType.ASTEROID)
for asteroid in asteroids:
    print(f"{asteroid.name} ({asteroid.category})")
```

### Aspect Registry

**Location:** `core/registry.py`

Stores metadata for all aspect types.

#### AspectInfo

```python
@dataclass(frozen=True)
class AspectInfo:
    name: str                        # "Conjunction"
    angle: float                     # 0.0, 60.0, 90.0, 120.0, 180.0, etc.
    category: str                    # "Major", "Minor", "Harmonic"
    family: str | None               # "Ptolemaic", "Quintile Series", etc.
    glyph: str                       # Unicode symbol (☌, ⚹, □, △, ☍)
    color: str                       # Hex color for rendering
    default_orb: float               # Default orb in degrees
    aliases: list[str]
    description: str
    metadata: dict[str, Any]         # line_width, dash_pattern, etc.
```

#### Registry Contents

**Major Aspects (Ptolemaic):**
- Conjunction (0°) - orb 8°
- Sextile (60°) - orb 6°
- Square (90°) - orb 7°
- Trine (120°) - orb 8°
- Opposition (180°) - orb 8°

**Minor Aspects:**
- Semisextile (30°) - orb 2°
- Semisquare (45°) - orb 2°
- Sesquisquare (135°) - orb 2°
- Quincunx (150°) - orb 3°

**Quintile Family (H5):**
- Quintile (72°) - orb 2°
- Biquintile (144°) - orb 2°

**Septile Family (H7):**
- Septile (51.43°) - orb 1°
- Biseptile (102.86°) - orb 1°
- Triseptile (154.29°) - orb 1°

**Novile Family (H9):**
- Novile (40°) - orb 1°
- Binovile (80°) - orb 1°
- Quadnovile (160°) - orb 1°

#### Helper Functions

```python
def get_aspect_info(name: str) -> AspectInfo:
    """Get aspect info by name."""
    ...

def get_aspect_by_alias(alias: str) -> AspectInfo | None:
    """Get aspect info by alias."""
    ...

def get_aspects_by_category(category: str) -> list[AspectInfo]:
    """Get all aspects in category."""
    ...

def get_aspects_by_family(family: str) -> list[AspectInfo]:
    """Get all aspects in family."""
    ...

def search_aspects(query: str) -> list[AspectInfo]:
    """Search aspects."""
    ...
```

**Example:**
```python
from stellium.core.registry import get_aspect_info, get_aspects_by_category

# Get info
trine_info = get_aspect_info("Trine")
print(f"{trine_info.name}: {trine_info.angle}° (orb: {trine_info.default_orb}°)")
print(f"Glyph: {trine_info.glyph}, Color: {trine_info.color}")

# Get all major aspects
major = get_aspects_by_category("Major")
for aspect in major:
    print(f"{aspect.name}: {aspect.angle}°")
```

---

## Calculation Engines

Engines perform the core astronomical calculations.

### Ephemeris Engine

**Location:** `engines/ephemeris.py`

#### SwissEphemerisEngine

The default engine using Swiss Ephemeris library.

```python
class SwissEphemerisEngine:
    def __init__(self, ephemeris_path: str | None = None):
        """
        Initialize with optional custom ephemeris data path.

        Args:
            ephemeris_path: Path to Swiss Ephemeris data files
                           (defaults to package data/swisseph/ephe/)
        """
        ...
```

**Key Methods:**

```python
def calculate_positions(
    self,
    datetime: ChartDateTime,
    location: ChartLocation,
    objects: list[str] | None = None
) -> list[CelestialPosition]:
    """
    Calculate positions for all requested objects.

    Args:
        datetime: When to calculate
        location: Where to calculate (for topocentric)
        objects: List of object names (None = use defaults)

    Returns:
        List of CelestialPosition objects
    """
    ...

@cached(cache_type="ephemeris", max_age_seconds=86400)
def _calculate_single_position(
    self,
    julian_day: float,
    object_id: int,
    object_name: str
) -> CelestialPosition:
    """
    Calculate single position (cached).

    Uses:
    - swe.calc_ut() for position
    - swe.pheno_ut() for phase data (Moon/planets)
    """
    ...
```

**Features:**
- Caches individual position calculations
- Automatically calculates phase data for Moon/planets
- Derives South Node from North Node
- Uses registry for object metadata
- Topocentric positions (location-specific)

**Example:**
```python
from stellium.engines import SwissEphemerisEngine

# Use custom ephemeris path
engine = SwissEphemerisEngine(ephemeris_path="/path/to/ephe")

chart = (
    ChartBuilder.from_native(native)
    .with_ephemeris(engine)
    .calculate()
)
```

#### MockEphemerisEngine

For testing without Swiss Ephemeris.

```python
class MockEphemerisEngine:
    def __init__(self, positions: dict[str, float]):
        """
        Create mock engine with fixed positions.

        Args:
            positions: {object_name: longitude}
        """
        ...
```

**Example:**
```python
from stellium.engines.ephemeris import MockEphemerisEngine

mock = MockEphemerisEngine({
    "Sun": 285.5,      # 15° Capricorn
    "Moon": 120.0,     # 0° Leo
    "Mercury": 275.0   # 5° Capricorn
})

chart = ChartBuilder.from_native(native).with_ephemeris(mock).calculate()
```

### House System Engines

**Location:** `engines/houses.py`

All house engines extend `SwissHouseSystemBase`.

#### Base Class

```python
class SwissHouseSystemBase:
    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_swiss_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        system_code: bytes
    ) -> tuple:
        """Call swe.houses() with caching."""
        return swe.houses(julian_day, latitude, longitude, system_code)

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """
        Calculate cusps and angles.

        Returns:
            (HouseCusps, [ASC, MC, DSC, IC, Vertex])
        """
        ...

    def assign_houses(
        self,
        positions: list[CelestialPosition],
        cusps: HouseCusps
    ) -> dict[str, int]:
        """
        Assign house numbers to positions.

        Returns:
            {object_name: house_number}
        """
        ...
```

#### Supported Systems

**Quadrant Systems:**
- `PlacidusHouses` (default) - Most popular in Western astrology
- `KochHouses` - Koch houses
- `RegiomontanusHouses` - Regiomontanus
- `CampanusHouses` - Campanus
- `TopocentricHouses` - Topocentric
- `AlcabitiusHouses` - Alcabitius

**Equal Systems:**
- `EqualHouses` - Equal from Ascendant
- `EqualMCHouses` - Equal from MC
- `VehlowEqualHouses` - Vehlow equal
- `WholeSignHouses` - Whole sign

**Other:**
- `PorphyryHouses` - Porphyry (space division)
- `MorinusHouses` - Morinus (equatorial)
- Plus 15+ more via Swiss Ephemeris

**Example:**
```python
from stellium.engines import PlacidusHouses, WholeSignHouses

chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .calculate()
)

# Compare systems
print(f"Placidus: Sun in house {chart.get_house('Sun', 'Placidus')}")
print(f"Whole Sign: Sun in house {chart.get_house('Sun', 'Whole Sign')}")

# Get cusps for each system
placidus_cusps = chart.get_houses("Placidus")
whole_sign_cusps = chart.get_houses("Whole Sign")
```

### Aspect Engines

**Location:** `engines/aspects.py`

#### ModernAspectEngine

Configurable aspect engine using `AspectConfig`.

```python
class ModernAspectEngine:
    def __init__(self, config: AspectConfig | None = None):
        """
        Create aspect engine.

        Args:
            config: AspectConfig or None (uses defaults)
        """
        ...

    def calculate_aspects(
        self,
        positions: list[CelestialPosition],
        orb_engine: OrbEngine
    ) -> list[Aspect]:
        """
        Find all aspects within orb.

        Process:
        1. Filter positions by config
        2. Check all pairs
        3. For each configured aspect:
           - Calculate angular distance
           - Ask orb_engine for allowance
           - Check if within orb
           - Determine applying/separating
        """
        ...
```

**Key Helper:**
```python
def _is_applying(
    obj1: CelestialPosition,
    obj2: CelestialPosition,
    aspect_angle: float,
    current_distance: float
) -> bool | None:
    """
    Determine if aspect is applying or separating.

    Uses 1-minute interval to check if orb is decreasing.

    Returns:
        True: applying (getting tighter)
        False: separating (getting wider)
        None: unable to determine
    """
    ...
```

**Example:**
```python
from stellium.engines import ModernAspectEngine
from stellium.core.config import AspectConfig

# Custom config
config = AspectConfig(
    aspects=["Conjunction", "Trine", "Square", "Opposition"],
    include_angles=True,
    include_nodes=True,
    include_asteroids=False
)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine(config))
    .calculate()
)

# Check aspects
for aspect in chart.aspects:
    applying = "applying" if aspect.is_applying else "separating"
    print(f"{aspect.description} ({applying})")
```

#### HarmonicAspectEngine

Calculates harmonic aspects (septiles, noviles, etc.).

```python
class HarmonicAspectEngine:
    def __init__(self, harmonic: int):
        """
        Create harmonic aspect engine.

        Args:
            harmonic: Harmonic number (5, 7, 9, 11, etc.)

        Examples:
            5: Quintile series (72°, 144°)
            7: Septile series (51.43°, 102.86°, 154.29°)
            9: Novile series (40°, 80°, 160°)
        """
        ...
```

**Example:**
```python
from stellium.engines import HarmonicAspectEngine

# Septile aspects
septile_engine = HarmonicAspectEngine(harmonic=7)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(septile_engine)
    .calculate()
)

# Aspects will be H7-1, H7-2, H7-3 (septile, biseptile, triseptile)
```

### Orb Engines

**Location:** `engines/orbs.py`

#### SimpleOrbEngine

One orb value per aspect type.

```python
class SimpleOrbEngine:
    def __init__(
        self,
        orb_map: dict[str, float] | None = None,
        fallback_orb: int = 2
    ):
        """
        Create simple orb engine.

        Args:
            orb_map: {aspect_name: orb_degrees} or None (uses registry defaults)
            fallback_orb: Default for unknown aspects
        """
        ...
```

**Example:**
```python
from stellium.engines import SimpleOrbEngine

orbs = SimpleOrbEngine(
    orb_map={
        "Conjunction": 10.0,
        "Trine": 8.0,
        "Square": 7.0,
        "Sextile": 6.0,
        "Opposition": 8.0
    },
    fallback_orb=2.0
)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .with_orbs(orbs)
    .calculate()
)
```

#### LuminariesOrbEngine

Wider orbs when Sun or Moon is involved.

```python
class LuminariesOrbEngine:
    def __init__(
        self,
        luminary_orbs: dict[str, float] | None = None,
        default_orbs: dict[str, float] | None = None,
        fallback_orb: float = 2.0
    ):
        """
        Create luminaries orb engine.

        Args:
            luminary_orbs: Orbs when Sun/Moon involved
            default_orbs: Orbs for other planets
            fallback_orb: Final fallback
        """
        ...
```

**Example:**
```python
from stellium.engines import LuminariesOrbEngine

orbs = LuminariesOrbEngine(
    luminary_orbs={
        "Conjunction": 10.0,
        "Trine": 8.0,
        "Square": 8.0
    },
    default_orbs={
        "Conjunction": 8.0,
        "Trine": 6.0,
        "Square": 6.0
    }
)

# Sun-Moon conjunction: 10° orb
# Mars-Venus conjunction: 8° orb
```

#### ComplexOrbEngine

Cascading priority matrix with multiple rule types.

```python
class ComplexOrbEngine:
    def __init__(self, config: dict[str, Any]):
        """
        Create complex orb engine.

        Config structure:
        {
            "by_pair": {
                "Moon-Sun": {"Square": 10.0, "default": 8.0},
                "Venus-Mars": {"default": 5.0}
            },
            "by_planet": {
                "Sun": {"Conjunction": 10.0, "default": 8.0},
                "Moon": {"default": 8.0}
            },
            "by_aspect": {
                "Conjunction": 8.0,
                "Trine": 6.0
            },
            "default": 3.0
        }

        Priority order:
        1. Specific pair + specific aspect
        2. Specific pair default
        3. Single planet rules (highest priority wins)
        4. Aspect default
        5. Global default
        """
        ...
```

**Example:**
```python
from stellium.engines import ComplexOrbEngine

config = {
    "by_pair": {
        "Moon-Sun": {"Square": 10.0, "default": 8.0}
    },
    "by_planet": {
        "Sun": {"default": 8.0},
        "Moon": {"default": 8.0}
    },
    "by_aspect": {
        "Square": 7.0,
        "Trine": 6.0
    },
    "default": 3.0
}

orbs = ComplexOrbEngine(config)

# Moon-Sun square: 10.0° (by_pair specific)
# Sun-Mars square: 8.0° (Sun's by_planet default)
# Venus-Mars square: 7.0° (by_aspect)
# Venus-Jupiter quintile: 3.0° (global default)
```

### Dignity Engines

**Location:** `engines/dignities.py`

#### TraditionalDignityCalculator

Traditional essential dignities scoring.

**Scores:**
- Ruler: +5
- Exaltation: +4
- Triplicity: +3
- Term (Bound): +2
- Face (Decan): +1
- Detriment: -5
- Fall: -4
- Peregrine: 0 (no dignity)

```python
class TraditionalDignityCalculator:
    def calculate_dignity(
        self,
        planet: CelestialPosition,
        decan_system: str = "triplicity"
    ) -> dict:
        """
        Calculate traditional essential dignities.

        Args:
            planet: Planet position
            decan_system: "triplicity", "chaldean", or "egyptian"

        Returns:
            {
                'ruler': bool,
                'exaltation': bool,
                'triplicity': bool,
                'term': bool,
                'face': bool,
                'detriment': bool,
                'fall': bool,
                'score': int,
                'state': str  # "Ruler", "Exalted", "Detriment", etc.
            }
        """
        ...
```

**Example:**
```python
from stellium.engines import TraditionalDignityCalculator

calc = TraditionalDignityCalculator()

sun = chart.get_object("Sun")
dignity = calc.calculate_dignity(sun)

print(f"Sun dignity: {dignity['state']}")
print(f"Score: {dignity['score']}")
```

#### ModernDignityCalculator

Uses modern rulerships (Uranus rules Aquarius, Neptune rules Pisces, Pluto rules Scorpio).

```python
class ModernDignityCalculator:
    def calculate_dignity(
        self,
        planet: CelestialPosition,
        decan_system: str = "triplicity"
    ) -> dict:
        """Same interface as TraditionalDignityCalculator."""
        ...
```

#### MutualReceptionAnalyzer

Finds mutual receptions (planets in each other's signs).

```python
class MutualReceptionAnalyzer:
    def find_mutual_receptions(
        self,
        positions: list[CelestialPosition],
        rulership_system: str = "traditional"
    ) -> list[dict]:
        """
        Find mutual receptions.

        Args:
            positions: Planet positions
            rulership_system: "traditional" or "modern"

        Returns:
            [
                {
                    'planet1': str,
                    'planet2': str,
                    'type': 'rulership' or 'exaltation',
                    'sign1': str,
                    'sign2': str
                },
                ...
            ]
        """
        ...
```

**Example:**
```python
from stellium.engines import MutualReceptionAnalyzer

analyzer = MutualReceptionAnalyzer()
positions = chart.get_planets()

receptions = analyzer.find_mutual_receptions(positions, "traditional")

for reception in receptions:
    print(f"{reception['planet1']} in {reception['sign1']} and "
          f"{reception['planet2']} in {reception['sign2']} "
          f"({reception['type']} reception)")
```

### Pattern Analyzer

**Location:** `engines/patterns.py`

#### AspectPatternAnalyzer

Detects geometric aspect patterns.

**Detected Patterns:**
- **Grand Trine**: 3 planets, 3 trines (all same element)
- **T-Square**: Opposition + 2 squares to apex
- **Yod** (Finger of God): 2 sextiles + 2 quincunxes to apex
- **Grand Cross**: 4 planets, 2 oppositions, 4 squares
- **Stellium**: 3+ planets within 8° orb
- **Mystic Rectangle**: 2 oppositions, 4 sextiles/trines
- **Kite**: Grand trine + opposition to one point

```python
class AspectPatternAnalyzer:
    @property
    def analyzer_name(self) -> str:
        return "Aspect Pattern Analyzer"

    @property
    def metadata_name(self) -> str:
        return "aspect_patterns"

    def analyze(self, chart: CalculatedChart) -> list[AspectPattern]:
        """
        Detect all patterns in chart.

        Returns:
            List of AspectPattern objects
        """
        ...
```

**Example:**
```python
from stellium.engines import AspectPatternAnalyzer, ModernAspectEngine

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .add_analyzer(AspectPatternAnalyzer())
    .calculate()
)

patterns = chart.metadata.get('aspect_patterns', [])

for pattern in patterns:
    planets = ", ".join([p.name for p in pattern.planets])
    print(f"\n{pattern.name}")
    print(f"Planets: {planets}")
    if pattern.element:
        print(f"Element: {pattern.element}")
    if pattern.focal_planet:
        print(f"Focal planet: {pattern.focal_planet.name}")
```

---

## Components

Components add new calculated positions (or metadata) to charts.

### Arabic Parts Calculator

**Location:** `components/arabic_parts.py`

Calculates 25+ Arabic lots (Hermetic lots).

```python
class ArabicPartsCalculator:
    @property
    def component_name(self) -> str:
        return "Arabic Parts"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]]
    ) -> list[CelestialPosition]:
        """
        Calculate Arabic parts.

        Returns:
            List of new CelestialPosition objects (type=ARABIC_PART)
        """
        ...
```

**Features:**
- Sect-aware formulas (day/night chart detection)
- Hermetic core lots
- Family and life topic lots
- All lots have ObjectType.ARABIC_PART

**Calculated Lots:**

**Core Hermetic Lots:**
- Lot of Fortune (sect-aware)
- Lot of Spirit (sect-aware)
- Lot of Eros (sect-aware)
- Lot of Necessity (sect-aware)
- Lot of Courage (sect-aware)
- Lot of Victory (sect-aware)

**Family Lots:**
- Father, Mother, Children, Marriage, Siblings

**Life Topic Lots:**
- Action, Illness, Death, Travel, Friends
- Exaltation, Basis, Love, Increase, Goods

**Formula Format:**
- Day: ASC + Point1 - Point2
- Night: ASC + Point2 - Point1 (reversed)

**Example:**
```python
from stellium.components import ArabicPartsCalculator

chart = (
    ChartBuilder.from_native(native)
    .add_component(ArabicPartsCalculator())
    .calculate()
)

# Access lots
lot_of_fortune = chart.get_object("Lot of Fortune")
lot_of_spirit = chart.get_object("Lot of Spirit")

print(f"Lot of Fortune: {lot_of_fortune.sign_position}")
print(f"In house: {chart.get_house('Lot of Fortune')}")
```

### Midpoint Calculator

**Location:** `components/midpoints.py`

Calculates midpoints between planets.

```python
class MidpointCalculator:
    @property
    def component_name(self) -> str:
        return "Midpoints"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]]
    ) -> list[CelestialPosition]:
        """
        Calculate all midpoints.

        Returns:
            List of MidpointPosition objects
        """
        ...
```

**Features:**
- Calculates both direct and indirect midpoints
- Only for major planets (Sun through Pluto)
- Creates MidpointPosition objects
- Named as "Planet1/Planet2"

**Example:**
```python
from stellium.components import MidpointCalculator

chart = (
    ChartBuilder.from_native(native)
    .add_component(MidpointCalculator())
    .calculate()
)

# Access midpoints
sun_moon = chart.get_object("Sun/Moon")
print(f"Sun/Moon midpoint: {sun_moon.sign_position}")

# Get all midpoints
midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]
for mp in midpoints:
    print(f"{mp.name}: {mp.sign_position}")
```

### Dignity Components

**Location:** `components/dignity.py`

#### DignityComponent

Calculates essential dignities and stores in metadata.

```python
class DignityComponent:
    def __init__(
        self,
        traditional: bool = True,
        modern: bool = True,
        receptions: bool = True,
        decan_system: str = "triplicity"
    ):
        """
        Create dignity component.

        Args:
            traditional: Calculate traditional dignities
            modern: Calculate modern dignities
            receptions: Find mutual receptions
            decan_system: "triplicity", "chaldean", or "egyptian"
        """
        ...

    def calculate(self, ...) -> list[CelestialPosition]:
        """
        Calculate dignities (stores in metadata, returns empty list).

        Stores in chart.metadata['dignities']:
        {
            'sect': 'day' | 'night',
            'planet_dignities': {
                'Sun': {
                    'traditional': {...},
                    'modern': {...}
                },
                ...
            },
            'mutual_receptions': {
                'traditional': [...],
                'modern': [...]
            }
        }
        """
        ...
```

**Example:**
```python
from stellium.components import DignityComponent

chart = (
    ChartBuilder.from_native(native)
    .add_component(DignityComponent())
    .calculate()
)

# Access via helper methods
sun_dignity = chart.get_planet_dignity("Sun", "traditional")
print(f"Sun state: {sun_dignity['state']}")
print(f"Sun score: {sun_dignity['score']}")

# Get all dignities
all_dignities = chart.get_dignities("traditional")

# Find mutual receptions
receptions = chart.get_mutual_receptions("traditional")
for rec in receptions:
    print(f"{rec['planet1']} and {rec['planet2']}: {rec['type']} reception")
```

#### AccidentalDignityComponent

Calculates accidental (house-based) dignities.

**Scores:**
- Angular houses (1, 4, 7, 10): +5
- Succedent houses (2, 5, 8, 11): +3
- Cadent houses (3, 6, 9, 12): +1
- House joys (traditional): +2

**House Joys:**
- Mercury: House 1
- Moon: House 3
- Venus: House 5
- Mars: House 6
- Sun: House 9
- Jupiter: House 11
- Saturn: House 12

```python
class AccidentalDignityComponent:
    def __init__(
        self,
        house_system: str = "Placidus",
        include_joys: bool = True
    ):
        """
        Create accidental dignity component.

        Args:
            house_system: Which house system to use
            include_joys: Include traditional house joys
        """
        ...
```

**Example:**
```python
from stellium.components import AccidentalDignityComponent

chart = (
    ChartBuilder.from_native(native)
    .add_component(AccidentalDignityComponent())
    .calculate()
)

# Access via helper
acc_dignities = chart.get_accidental_dignities("Placidus")

for planet, data in acc_dignities.items():
    print(f"{planet}: house {data['house']}, score {data['score']}")
```

---

## Visualization System

The visualization system renders charts to SVG using a composable layer architecture.

**Location:** `visualization/`

### Layer Architecture

Charts are built by stacking layers from bottom to top. Each layer is independent and composable.

#### IRenderLayer Protocol

```python
class IRenderLayer(Protocol):
    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart
    ) -> None:
        """Render this layer onto the SVG drawing."""
        ...
```

#### Available Layers

**Location:** `visualization/layers.py`

- `ZodiacLayer`: Zodiac wheel with signs and symbols
- `HouseCuspLayer`: House cusp lines
- `AngleLayer`: ASC, MC markers
- `PlanetLayer`: Planet symbols and degree markers
- `AspectLayer`: Aspect lines between planets
- `MoonPhaseLayer`: Moon phase visualization

**Example:**
```python
from stellium.visualization import ChartRenderer
from stellium.visualization.layers import (
    ZodiacLayer,
    HouseCuspLayer,
    PlanetLayer,
    AspectLayer
)

renderer = ChartRenderer(size=800)
dwg = renderer.create_svg_drawing("chart.svg")

# Render layers in order
ZodiacLayer().render(renderer, dwg, chart)
HouseCuspLayer().render(renderer, dwg, chart)
PlanetLayer().render(renderer, dwg, chart)
AspectLayer().render(renderer, dwg, chart)

dwg.save()
```

### ChartRenderer

**Location:** `visualization/core.py`

The core rendering engine with coordinate helpers.

```python
class ChartRenderer:
    def __init__(self, size: int = 800, rotation: float = 0):
        """
        Create renderer.

        Args:
            size: Canvas size in pixels (square)
            rotation: Rotation in degrees (0 = Aries at 9 o'clock)
        """
        self.size = size
        self.rotation = rotation
        self.center = size / 2
```

**Key Methods:**

```python
def create_svg_drawing(self, filename: str) -> svgwrite.Drawing:
    """Create SVG drawing with viewbox."""
    ...

def polar_to_cartesian(
    self,
    degrees: float,
    radius: float
) -> tuple[float, float]:
    """
    Convert polar to Cartesian coordinates.

    Args:
        degrees: 0-360 (0 = right, 90 = top)
        radius: Distance from center

    Returns:
        (x, y) coordinates
    """
    ...

def get_chart_rotation(self, chart: CalculatedChart) -> float:
    """Get rotation to place Ascendant at 9 o'clock."""
    ...
```

**Example:**
```python
from stellium.visualization import ChartRenderer

renderer = ChartRenderer(size=1000, rotation=0)

# Convert degrees to coordinates
x, y = renderer.polar_to_cartesian(degrees=0, radius=200)  # Right side
x, y = renderer.polar_to_cartesian(degrees=90, radius=200)  # Top
```

### High-Level Drawing Functions

**Location:** `visualization/drawing.py`

Convenience functions for common chart types.

```python
def draw_chart(
    chart: CalculatedChart,
    filename: str,
    size: int = 800,
    house_system: str | None = None
) -> None:
    """
    Draw a standard natal chart.

    Args:
        chart: Calculated chart
        filename: Output SVG filename
        size: Canvas size
        house_system: Which system to use (None = first available)

    Renders:
        - Zodiac wheel
        - House cusps
        - Angles (ASC, MC)
        - Planets
        - Aspects
        - Moon phase (if Moon present)
    """
    ...

def draw_chart_with_multiple_houses(
    chart: CalculatedChart,
    filename: str,
    size: int = 800
) -> None:
    """
    Draw chart with overlaid house systems.

    Shows multiple house systems in different colors.
    """
    ...
```

**Example:**
```python
from stellium.visualization import draw_chart

chart = ChartBuilder.from_notable("Albert Einstein").calculate()

draw_chart(
    chart,
    "einstein_chart.svg",
    size=1000,
    house_system="Placidus"
)
```

### Moon Phase Visualization

**Location:** `visualization/moon_phase.py`

Renders realistic Moon phase appearance.

```python
def draw_moon_phase(
    phase_data: PhaseData,
    center_x: float,
    center_y: float,
    radius: float,
    dwg: svgwrite.Drawing
) -> None:
    """
    Draw Moon phase.

    Args:
        phase_data: PhaseData from Moon position
        center_x, center_y: Center coordinates
        radius: Moon circle radius
        dwg: SVG drawing

    Renders:
        - Full circle (Moon outline)
        - Illuminated portion (accurate shape)
    """
    ...
```

**Example:**
```python
from stellium.visualization.moon_phase import draw_moon_phase

moon = chart.get_object("Moon")
if moon and moon.phase:
    draw_moon_phase(
        moon.phase,
        center_x=400,
        center_y=400,
        radius=30,
        dwg=dwg
    )
```

---

## Presentation & Reporting

The presentation system generates human-readable reports.

**Location:** `presentation/`

### ReportBuilder

**Location:** `presentation/builder.py`

Fluent API for building reports.

```python
class ReportBuilder:
    def __init__(self):
        """Create empty report builder."""
        ...

    def from_chart(self, chart: CalculatedChart) -> "ReportBuilder":
        """Set the chart to report on."""
        ...
```

**Section Methods:**

```python
def with_chart_overview(self) -> "ReportBuilder":
    """Add chart overview section."""
    ...

def with_planet_positions(
    self,
    include_speed: bool = False
) -> "ReportBuilder":
    """Add planet positions table."""
    ...

def with_aspects(
    self,
    mode: str = "major",
    orbs: bool = False
) -> "ReportBuilder":
    """
    Add aspects section.

    Args:
        mode: "major", "all"
        orbs: Include orb values
    """
    ...

def with_house_positions(
    self,
    house_system: str = "Placidus"
) -> "ReportBuilder":
    """Add house positions table."""
    ...

def with_midpoints(
    self,
    mode: str = "core"
) -> "ReportBuilder":
    """
    Add midpoints section.

    Args:
        mode: "core" (major planets) or "all"
    """
    ...

def with_dignities(
    self,
    system: str = "traditional"
) -> "ReportBuilder":
    """Add essential dignities table."""
    ...

def with_aspect_patterns(self) -> "ReportBuilder":
    """Add aspect patterns section."""
    ...
```

**Rendering:**

```python
def render(
    self,
    format: str = "rich_table",
    file: str | None = None
) -> str:
    """
    Render report.

    Args:
        format: "rich_table" or "plain_text"
        file: Optional file to write to

    Returns:
        Rendered report string
    """
    ...
```

**Example:**
```python
from stellium.presentation import ReportBuilder

chart = ChartBuilder.from_notable("Albert Einstein").calculate()

report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions(include_speed=True)
    .with_aspects(mode="major", orbs=True)
    .with_dignities(system="traditional")
    .render(format="rich_table")
)

print(report)

# Save to file
report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .render(format="plain_text", file="report.txt")
)
```

### Report Sections

**Location:** `presentation/sections.py`

Each section generates structured data.

**Section Data Format:**

```python
{
    "type": "table" | "text" | "key_value",
    "headers": [...],        # For tables
    "rows": [[...], ...],    # For tables
    "text": "...",           # For text blocks
    "data": {...}            # For key-value pairs
}
```

**Available Sections:**

- `ChartOverviewSection`: Date, time, location, chart type
- `PlanetPositionSection`: Planet positions table
- `AspectSection`: Aspects table
- `HousePositionSection`: House placements table
- `MidpointSection`: Midpoints table
- `DignitySection`: Essential dignities table
- `AspectPatternSection`: Detected patterns

### Report Renderers

**Location:** `presentation/renderers.py`

#### RichTableRenderer

Beautiful terminal output using Rich library.

```python
class RichTableRenderer:
    def render_section(
        self,
        section_name: str,
        section_data: dict
    ) -> str:
        """Render section with Rich formatting."""
        ...

    def render_report(
        self,
        sections: list[tuple[str, dict]]
    ) -> str:
        """Render complete report."""
        ...
```

**Features:**
- Color-coded tables
- Unicode symbols (glyphs)
- Aligned columns
- Section headers

#### PlainTextRenderer

Simple text tables for files.

```python
class PlainTextRenderer:
    def render_section(
        self,
        section_name: str,
        section_data: dict
    ) -> str:
        """Render section as plain text."""
        ...

    def render_report(
        self,
        sections: list[tuple[str, dict]]
    ) -> str:
        """Render complete report."""
        ...
```

**Features:**
- ASCII tables
- No color/formatting
- File-friendly output

---

## Comparison Charts

Synastry and transit comparisons between two charts.

**Location:** `core/comparison.py`

### ComparisonBuilder

```python
class ComparisonBuilder:
    @classmethod
    def from_natives(
        cls,
        native1: Native,
        native2: Native,
        comparison_type: ComparisonType = ComparisonType.SYNASTRY
    ) -> "ComparisonBuilder":
        """
        Create comparison builder.

        Args:
            native1: Native/inner chart
            native2: Partner/transit/outer chart
            comparison_type: SYNASTRY or TRANSIT
        """
        ...

    @classmethod
    def from_charts(
        cls,
        chart1: CalculatedChart,
        chart2: CalculatedChart,
        comparison_type: ComparisonType = ComparisonType.SYNASTRY
    ) -> "ComparisonBuilder":
        """Create from pre-calculated charts."""
        ...
```

**Configuration Methods:**

```python
def with_aspect_engine(
    self,
    engine: AspectEngine
) -> "ComparisonBuilder":
    """Set aspect engine for cross-chart aspects."""
    ...

def with_orb_engine(
    self,
    engine: OrbEngine
) -> "ComparisonBuilder":
    """Set orb engine."""
    ...

def with_labels(
    self,
    chart1_label: str,
    chart2_label: str
) -> "ComparisonBuilder":
    """Set chart labels for display."""
    ...
```

**Execution:**

```python
def calculate(self) -> Comparison:
    """
    Calculate comparison.

    Process:
    1. Calculate both charts (if not already calculated)
    2. Combine all positions
    3. Calculate cross-chart aspects
    4. Calculate house overlays
    5. Return Comparison object
    """
    ...
```

### Convenience Functions

```python
def create_synastry(
    native1: Native,
    native2: Native
) -> Comparison:
    """Quick synastry comparison."""
    ...

def create_transits(
    native: Native,
    transit_datetime: dt.datetime
) -> Comparison:
    """
    Quick transit comparison.

    Args:
        native: Birth chart
        transit_datetime: Transit time (uses birth location)
    """
    ...
```

### Comparison Data Models

#### ComparisonType (Enum)

```python
class ComparisonType(Enum):
    SYNASTRY = "synastry"
    TRANSIT = "transit"
```

#### HouseOverlay

```python
@dataclass(frozen=True)
class HouseOverlay:
    planet_name: str              # Name of planet
    planet_owner: str             # "chart1" or "chart2"
    house_number: int             # House it falls in
    house_owner: str              # "chart1" or "chart2"
    cusp_longitude: float
```

**Example:**
```python
# "Partner's Venus falls in your 7th house"
overlay = HouseOverlay(
    planet_name="Venus",
    planet_owner="chart2",
    house_number=7,
    house_owner="chart1",
    cusp_longitude=195.0
)
```

### Usage Examples

**Synastry:**

```python
from stellium.core.native import Native
from stellium.core.comparison import create_synastry

native1 = Native(datetime(1990, 1, 1, 12, 0), "New York, NY")
native2 = Native(datetime(1992, 5, 15, 8, 30), "Los Angeles, CA")

synastry = create_synastry(native1, native2)

# Check cross-aspects
for aspect in synastry.cross_aspects:
    print(f"{aspect.chart1_object.name} {aspect.aspect_name} "
          f"{aspect.chart2_object.name} (orb: {aspect.orb:.2f}°)")

# Check house overlays
for overlay in synastry.house_overlays:
    owner = "Partner's" if overlay.planet_owner == "chart2" else "Your"
    house_owner = "your" if overlay.house_owner == "chart1" else "partner's"
    print(f"{owner} {overlay.planet_name} falls in {house_owner} house {overlay.house_number}")
```

**Transits:**

```python
from datetime import datetime
from stellium.core.native import Native
from stellium.core.comparison import create_transits

# Birth chart
native = Native(datetime(1990, 1, 1, 12, 0), "New York, NY")

# Current transits
transits = create_transits(native, datetime.now())

# Check transit aspects
for aspect in transits.cross_aspects:
    print(f"Transit {aspect.chart2_object.name} {aspect.aspect_name} "
          f"Natal {aspect.chart1_object.name}")
```

**Custom Configuration:**

```python
from stellium.core.comparison import ComparisonBuilder
from stellium.engines import ModernAspectEngine, SimpleOrbEngine
from stellium.core.config import AspectConfig

# Tight orbs for transits
orb_engine = SimpleOrbEngine(
    orb_map={
        "Conjunction": 1.0,
        "Square": 1.0,
        "Trine": 1.0,
        "Opposition": 1.0
    }
)

aspect_config = AspectConfig(
    aspects=["Conjunction", "Square", "Opposition"],
    include_angles=False
)

comparison = (
    ComparisonBuilder.from_natives(native, transit_native)
    .with_aspect_engine(ModernAspectEngine(aspect_config))
    .with_orb_engine(orb_engine)
    .with_labels("Natal", "Transit")
    .calculate()
)
```

---

## Data Flow

Understanding how data flows through the system helps with debugging and extension.

### Chart Calculation Flow

```
User Input
    ↓
┌─────────────────────┐
│ Native              │  Parses flexible inputs
│ - Geocode location  │  Converts to UTC
│ - Find timezone     │  Creates immutable data
└─────────────────────┘
    ↓
┌─────────────────────┐
│ ChartBuilder        │  Fluent API
│ .from_native()      │  Configuration methods
│ .with_aspects()     │  .add_component()
│ .with_houses()      │  etc.
└─────────────────────┘
    ↓
┌─────────────────────┐
│ .calculate()        │  Orchestrates calculation
└─────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ CALCULATION STEPS (in order):       │
│                                     │
│ 1. Ephemeris Engine                 │
│    → Calculate planetary positions  │
│                                     │
│ 2. House System Engines             │
│    → Calculate cusps for each       │
│    → Calculate angles (ASC/MC/etc)  │
│                                     │
│ 3. House Assignments                │
│    → Assign house # to each planet  │
│    → For each house system          │
│                                     │
│ 4. Components (in order added)      │
│    → Add Arabic parts               │
│    → Add midpoints                  │
│    → Calculate dignities            │
│    → (Each gets current state)      │
│                                     │
│ 5. Aspect Engine (if configured)    │
│    → Find aspects between all       │
│    → Use orb engine for allowances  │
│    → Determine applying/separating  │
│                                     │
│ 6. Analyzers (in order added)       │
│    → Detect patterns                │
│    → Store in metadata              │
│                                     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────┐
│ CalculatedChart     │  Immutable, frozen
│ (frozen dataclass)  │  All data included
└─────────────────────┘
```

### Dependency Graph

**What Depends on What:**

```
Positions (ephemeris)
    │
    ├─→ House Cusps (houses)
    │       │
    │       └─→ House Placements
    │               │
    │               └─→ Components (can use houses)
    │                       │
    │                       └─→ Aspects (uses all positions)
    │                               │
    │                               └─→ Analyzers (uses complete chart)
    │
    └─→ Aspects (uses positions)
            │
            └─→ Analyzers
```

**Key Points:**

1. **Positions are calculated first** - Everything depends on them
2. **Houses need positions** - Can't calculate without ephemeris
3. **Components run after houses** - Get access to house placements
4. **Aspects need all positions** - Including component-added ones
5. **Analyzers run last** - Have access to complete chart

### Configuration Propagation

**How Configuration Flows:**

```
CalculationConfig
    ↓
ChartBuilder
    ↓
Ephemeris Engine
    ↓
(determines which objects to calculate)
```

```
AspectConfig
    ↓
AspectEngine
    ↓
(determines which aspects to find)
```

```
OrbEngine
    ↓
AspectEngine.calculate_aspects()
    ↓
(determines if aspects are within orb)
```

---

## Extension Points

How to add new functionality to Stellium.

### Adding New Celestial Objects

**Use Case:** Calculate positions for a new asteroid, fixed star, or calculated point.

**Steps:**

**1. Check if Swiss Ephemeris supports it**

Find the Swiss Ephemeris ID (MPC number for asteroids, etc.):
- Asteroids: Use MPC number
- Fixed stars: Use star name
- See: https://www.astro.com/swisseph/

**2. Add to Swiss Ephemeris ID mapping**

In `engines/ephemeris.py`:

```python
SWISS_EPHEMERIS_IDS = {
    # ... existing objects ...
    "YourObject": 12345  # MPC number or Swiss Eph ID
}
```

**3. Add to celestial registry**

In `core/registry.py`:

```python
CELESTIAL_REGISTRY["YourObject"] = CelestialObjectInfo(
    name="YourObject",
    display_name="Your Object",
    object_type=ObjectType.ASTEROID,  # or POINT, FIXED_STAR, etc.
    glyph="⚷",  # Unicode symbol
    glyph_svg_path=None,  # or custom SVG path
    swiss_ephemeris_id=12345,
    category="YourCategory",
    aliases=["Alias1", "Alias2"],
    description="Description of your object",
    metadata={}
)
```

**4. Include in calculation config**

```python
from stellium.core.config import CalculationConfig

config = CalculationConfig(
    include_asteroids=["YourObject"]  # or include_points
)

chart = ChartBuilder.from_native(native).with_config(config).calculate()

# Access your object
your_object = chart.get_object("YourObject")
print(f"YourObject: {your_object.sign_position}")
```

### Creating Custom House Systems

**Use Case:** Implement a house system not supported by Swiss Ephemeris.

**Steps:**

**1. Implement the protocol**

```python
from stellium.core.protocols import HouseSystemEngine
from stellium.core.models import HouseCusps, CelestialPosition, ObjectType

class CustomHouses:
    @property
    def system_name(self) -> str:
        return "Custom System"

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """
        Calculate house cusps and angles.

        Returns:
            (HouseCusps, [ASC, MC, DSC, IC, Vertex])
        """
        # Your calculation logic here
        cusps = [...]  # 12 cusp longitudes

        # Calculate angles
        asc = CelestialPosition(name="Ascendant", object_type=ObjectType.ANGLE, longitude=cusps[0])
        mc = CelestialPosition(name="Midheaven", object_type=ObjectType.ANGLE, longitude=cusps[9])
        dsc = CelestialPosition(name="Descendant", object_type=ObjectType.ANGLE, longitude=(cusps[0] + 180) % 360)
        ic = CelestialPosition(name="Imum Coeli", object_type=ObjectType.ANGLE, longitude=(cusps[9] + 180) % 360)
        vertex = CelestialPosition(name="Vertex", object_type=ObjectType.ANGLE, longitude=...)

        return (
            HouseCusps("Custom System", tuple(cusps)),
            [asc, mc, dsc, ic, vertex]
        )

    def assign_houses(
        self,
        positions: list[CelestialPosition],
        cusps: HouseCusps
    ) -> dict[str, int]:
        """
        Assign house numbers to positions.

        Returns:
            {object_name: house_number}
        """
        placements = {}

        for pos in positions:
            # Your assignment logic
            house_num = self._find_house(pos.longitude, cusps.cusps)
            placements[pos.name] = house_num

        return placements

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Helper to find which house a longitude falls in."""
        # Your logic here
        return house_number
```

**2. Use it**

```python
chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([CustomHouses()])
    .calculate()
)

# Access
sun_house = chart.get_house("Sun", "Custom System")
```

### Creating Custom Aspect Types

**Use Case:** Add new aspect angles (e.g., undecile, quindecile).

**Steps:**

**1. Add to aspect registry**

In `core/registry.py`:

```python
ASPECT_REGISTRY["MyAspect"] = AspectInfo(
    name="MyAspect",
    angle=77.0,  # Your angle
    category="Custom",
    family="My Family",
    glyph="◊",  # Unicode symbol
    color="#FF5733",  # Hex color
    default_orb=2.0,
    aliases=["Alias"],
    description="Description of my aspect",
    metadata={
        "line_width": 1,
        "dash_pattern": [5, 5]
    }
)
```

**2. Include in aspect config**

```python
from stellium.core.config import AspectConfig
from stellium.engines import ModernAspectEngine

config = AspectConfig(
    aspects=["Conjunction", "MyAspect"],
    include_angles=True
)

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine(config))
    .calculate()
)

# Aspects will include MyAspect
for aspect in chart.aspects:
    if aspect.aspect_name == "MyAspect":
        print(f"Found {aspect.description}")
```

### Creating Custom Components

**Use Case:** Add new calculated points (e.g., custom lots, harmonic positions).

**Steps:**

**1. Implement the protocol**

```python
from stellium.core.protocols import ChartComponent
from stellium.core.models import CelestialPosition, ObjectType

class MyComponent:
    @property
    def component_name(self) -> str:
        return "My Feature"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]]
    ) -> list[CelestialPosition]:
        """
        Calculate new positions.

        Returns:
            List of new CelestialPosition objects
        """
        new_positions = []

        # Your calculation logic
        # Example: Calculate a custom point
        sun = next((p for p in positions if p.name == "Sun"), None)
        moon = next((p for p in positions if p.name == "Moon"), None)

        if sun and moon:
            # Custom formula
            custom_longitude = (sun.longitude + moon.longitude * 2) % 360

            custom_point = CelestialPosition(
                name="My Custom Point",
                object_type=ObjectType.POINT,
                longitude=custom_longitude
            )

            new_positions.append(custom_point)

        return new_positions
```

**2. Use it**

```python
chart = (
    ChartBuilder.from_native(native)
    .add_component(MyComponent())
    .calculate()
)

# Access
custom_point = chart.get_object("My Custom Point")
print(f"My Custom Point: {custom_point.sign_position}")
```

**Alternative: Store in Metadata**

If your component analyzes rather than calculates positions:

```python
class MyAnalysisComponent:
    @property
    def component_name(self) -> str:
        return "My Analysis"

    def calculate(self, ...) -> list[CelestialPosition]:
        # Analyze chart
        analysis_results = {...}

        # Store in metadata (won't work directly from component)
        # Better to use ChartAnalyzer protocol for this

        return []  # No new positions
```

### Creating Custom Orb Engines

**Use Case:** Implement custom orb allowance logic.

**Steps:**

**1. Implement the protocol**

```python
from stellium.core.protocols import OrbEngine
from stellium.core.models import CelestialPosition

class MyOrbEngine:
    def get_orb_allowance(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str
    ) -> float:
        """
        Calculate orb allowance for this aspect.

        Returns:
            Maximum orb in degrees
        """
        # Your logic here

        # Example: Wider orbs in angular houses
        # (would need access to house placements - use ComplexOrbEngine pattern)

        # Simple example: Based on planet type
        if obj1.name == "Sun" or obj2.name == "Sun":
            return 10.0
        elif obj1.object_type == ObjectType.ANGLE or obj2.object_type == ObjectType.ANGLE:
            return 2.0
        else:
            return 5.0
```

**2. Use it**

```python
from stellium.engines import ModernAspectEngine

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .with_orbs(MyOrbEngine())
    .calculate()
)
```

### Creating Custom Analyzers

**Use Case:** Analyze charts and store findings in metadata.

**Steps:**

**1. Implement the protocol**

```python
from stellium.core.protocols import ChartAnalyzer
from stellium.core.models import CalculatedChart

class MyAnalyzer:
    @property
    def analyzer_name(self) -> str:
        return "My Analysis"

    @property
    def metadata_name(self) -> str:
        return "my_analysis"  # Key in chart.metadata

    def analyze(self, chart: CalculatedChart) -> dict:
        """
        Analyze the chart.

        Returns:
            Analysis results (stored in chart.metadata[metadata_name])
        """
        findings = {}

        # Example: Count retrograde planets
        retrogrades = [
            p for p in chart.get_planets()
            if p.is_retrograde
        ]

        findings['retrograde_count'] = len(retrogrades)
        findings['retrograde_planets'] = [p.name for p in retrogrades]

        # Example: Check element balance
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        for planet in chart.get_planets():
            element = self._get_element(planet.sign)
            elements[element] += 1

        findings['element_balance'] = elements

        return findings

    def _get_element(self, sign: str) -> str:
        """Helper to get element from sign."""
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        earth_signs = ["Taurus", "Virgo", "Capricorn"]
        air_signs = ["Gemini", "Libra", "Aquarius"]
        water_signs = ["Cancer", "Scorpio", "Pisces"]

        if sign in fire_signs:
            return "Fire"
        elif sign in earth_signs:
            return "Earth"
        elif sign in air_signs:
            return "Air"
        else:
            return "Water"
```

**2. Use it**

```python
chart = (
    ChartBuilder.from_native(native)
    .add_analyzer(MyAnalyzer())
    .calculate()
)

# Access findings
findings = chart.metadata['my_analysis']
print(f"Retrograde planets: {findings['retrograde_planets']}")
print(f"Element balance: {findings['element_balance']}")
```

### Creating Custom Report Sections

**Use Case:** Add custom sections to reports.

**Steps:**

**1. Implement the protocol**

```python
from stellium.core.protocols import ReportSection
from stellium.core.models import CalculatedChart

class MySection:
    @property
    def section_name(self) -> str:
        return "My Custom Section"

    def generate_data(self, chart: CalculatedChart) -> dict:
        """
        Generate section data.

        Returns:
            {
                "type": "table" | "text" | "key_value",
                "headers": [...],  # for tables
                "rows": [...],     # for tables
                "text": "...",     # for text
                "data": {...}      # for key-value
            }
        """
        # Example: Table of retrograde planets
        retrogrades = [p for p in chart.get_planets() if p.is_retrograde]

        return {
            "type": "table",
            "headers": ["Planet", "Position", "Speed"],
            "rows": [
                [p.name, p.sign_position, f"{p.speed_longitude:.4f}"]
                for p in retrogrades
            ]
        }
```

**2. Use it**

```python
from stellium.presentation import ReportBuilder

# Create custom builder
builder = ReportBuilder()
builder.from_chart(chart)

# Add custom section manually
builder._sections.append(MySection())

# Render
report = builder.render()
print(report)
```

**Better: Extend ReportBuilder**

```python
class CustomReportBuilder(ReportBuilder):
    def with_my_section(self) -> "CustomReportBuilder":
        """Add my custom section."""
        self._sections.append(MySection())
        return self

# Use it
report = (
    CustomReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_my_section()
    .render()
)
```

---

## Configuration Options

Comprehensive configuration reference.

### Calculation Configuration

**Location:** `core/config.py`

#### CalculationConfig

Controls which celestial objects are calculated.

```python
@dataclass
class CalculationConfig:
    include_planets: list[str]       # Planet names
    include_nodes: bool = True       # North/South Node
    include_chiron: bool = True      # Chiron
    include_points: list[str]        # Calculated points (Lilith, etc.)
    include_asteroids: list[str]     # Asteroid names
```

**Defaults:**
```python
include_planets = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
]
include_nodes = True
include_chiron = True
include_points = ["Mean Apogee"]  # Black Moon Lilith
include_asteroids = []
```

**Presets:**

```python
# Minimal (planets only)
CalculationConfig.minimal()

# Comprehensive (everything)
CalculationConfig.comprehensive()
```

**Example:**
```python
from stellium.core.config import CalculationConfig

# Custom config
config = CalculationConfig(
    include_planets=["Sun", "Moon", "Mercury", "Venus", "Mars"],
    include_nodes=False,
    include_chiron=True,
    include_points=["Mean Apogee", "True Apogee"],
    include_asteroids=["Ceres", "Pallas", "Juno", "Vesta"]
)

chart = ChartBuilder.from_native(native).with_config(config).calculate()
```

#### AspectConfig

Controls which aspects are calculated.

```python
@dataclass
class AspectConfig:
    aspects: list[str]               # Aspect names
    include_angles: bool = True      # Include ASC, MC, etc.
    include_nodes: bool = True       # Include Nodes
    include_asteroids: bool = True   # Include asteroids
```

**Defaults:**
```python
aspects = [
    "Conjunction", "Sextile", "Square", "Trine", "Opposition"
]  # Ptolemaic 5
```

**Example:**
```python
from stellium.core.config import AspectConfig

# Only major aspects, no asteroids
config = AspectConfig(
    aspects=["Conjunction", "Square", "Opposition"],
    include_angles=True,
    include_nodes=True,
    include_asteroids=False
)
```

### Engine Configuration

Each engine can be configured independently.

#### Ephemeris Path

```python
from stellium.engines import SwissEphemerisEngine

engine = SwissEphemerisEngine(
    ephemeris_path="/custom/path/to/ephe"
)

chart = ChartBuilder.from_native(native).with_ephemeris(engine).calculate()
```

#### House Systems

```python
from stellium.engines import PlacidusHouses, WholeSignHouses, KochHouses

# Multiple systems
chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([
        PlacidusHouses(),
        WholeSignHouses(),
        KochHouses()
    ])
    .calculate()
)

# Access each
print(chart.get_house("Sun", "Placidus"))
print(chart.get_house("Sun", "Whole Sign"))
print(chart.get_house("Sun", "Koch"))
```

#### Orb Configuration

See [Orb Engines](#orb-engines) section for full details.

```python
from stellium.engines import SimpleOrbEngine, LuminariesOrbEngine, ComplexOrbEngine

# Simple
simple = SimpleOrbEngine(
    orb_map={"Conjunction": 8.0, "Trine": 6.0},
    fallback_orb=2.0
)

# Luminaries
luminaries = LuminariesOrbEngine(
    luminary_orbs={"Conjunction": 10.0},
    default_orbs={"Conjunction": 8.0}
)

# Complex
complex_config = {
    "by_pair": {"Moon-Sun": {"default": 10.0}},
    "by_planet": {"Sun": {"default": 8.0}},
    "by_aspect": {"Conjunction": 8.0},
    "default": 3.0
}
complex_orbs = ComplexOrbEngine(complex_config)
```

### Component Configuration

Components have their own configuration options.

#### Arabic Parts

```python
from stellium.components import ArabicPartsCalculator

# Default (all lots)
arabic_parts = ArabicPartsCalculator()

chart = (
    ChartBuilder.from_native(native)
    .add_component(arabic_parts)
    .calculate()
)
```

#### Dignities

```python
from stellium.components import DignityComponent

dignity = DignityComponent(
    traditional=True,              # Calculate traditional
    modern=True,                   # Calculate modern
    receptions=True,               # Find mutual receptions
    decan_system="triplicity"      # "triplicity", "chaldean", "egyptian"
)

chart = (
    ChartBuilder.from_native(native)
    .add_component(dignity)
    .calculate()
)
```

#### Accidental Dignities

```python
from stellium.components import AccidentalDignityComponent

acc_dignity = AccidentalDignityComponent(
    house_system="Placidus",       # Which house system to use
    include_joys=True              # Include traditional house joys
)

chart = (
    ChartBuilder.from_native(native)
    .add_component(acc_dignity)
    .calculate()
)
```

### Caching Configuration

```python
from stellium.utils.cache import Cache

# Custom cache
cache = Cache(
    cache_dir="/tmp/my_cache",
    max_age_seconds=3600,          # 1 hour
    enabled=True
)

chart = (
    ChartBuilder.from_native(native)
    .with_cache(
        cache=cache,
        cache_chart=True,          # Cache entire chart
        cache_key_prefix="myapp_"  # Prefix for cache keys
    )
    .calculate()
)

# Disable caching
chart = ChartBuilder.from_native(native).with_cache(cache=None).calculate()
```

### Visualization Configuration

```python
from stellium.visualization import ChartRenderer, draw_chart

# Custom renderer
renderer = ChartRenderer(
    size=1000,        # Canvas size
    rotation=0        # Rotation in degrees
)

# High-level function
draw_chart(
    chart,
    "output.svg",
    size=1200,
    house_system="Whole Sign"
)
```

---

## Common Patterns & Conventions

### Immutability

All data models are frozen dataclasses. To "modify":

```python
from dataclasses import replace

old_pos = chart.get_object("Sun")
new_pos = replace(old_pos, longitude=45.0)

# old_pos is unchanged
```

### Protocol-Based Design

No inheritance required. Just match the signature:

```python
# This is valid - no inheritance needed
class MyEngine:
    def calculate_positions(self, datetime, location, objects=None):
        return [...]

# Use it
chart = ChartBuilder.from_native(native).with_ephemeris(MyEngine()).calculate()
```

### Error Handling

**Common Exceptions:**

- `ValueError`: Invalid input (coordinates out of range, invalid dates)
- `RuntimeError`: Calculation failures (Swiss Ephemeris errors)
- `KeyError`: Missing data in configs or registries

**Example:**
```python
try:
    chart = ChartBuilder.from_native(native).calculate()
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Calculation failed: {e}")
```

### Type Hints

Stellium is fully typed. Use mypy for type checking:

```bash
mypy src/stellium
```

**Example typed usage:**
```python
from stellium.core.native import Native
from stellium.core.models import CalculatedChart
from stellium.core.builder import ChartBuilder

native: Native = Native(datetime(2000, 1, 1), "New York")
builder: ChartBuilder = ChartBuilder.from_native(native)
chart: CalculatedChart = builder.calculate()
```

### Querying Charts

**Always use helper methods:**

```python
# Good
sun = chart.get_object("Sun")

# Bad (can fail if Sun not in positions)
sun = next(p for p in chart.positions if p.name == "Sun")
```

**Safe querying:**
```python
sun = chart.get_object("Sun")
if sun:
    print(f"Sun: {sun.sign_position}")
else:
    print("Sun not calculated")
```

### Working with Houses

**Always specify system name:**

```python
# Good
sun_house = chart.get_house("Sun", "Placidus")

# Bad (uses first available, may not be what you want)
sun_house = chart.get_house("Sun")
```

### Fluent API Style

**Chain methods for readability:**

```python
# Good
chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .calculate()
)

# Also OK but less readable
builder = ChartBuilder.from_native(native)
builder = builder.with_house_systems([PlacidusHouses()])
builder = builder.with_aspects(ModernAspectEngine())
chart = builder.calculate()
```

### Avoiding Common Mistakes

**1. Don't calculate charts without aspects if you need them:**

```python
# Wrong - no aspects calculated
chart = ChartBuilder.from_native(native).calculate()
aspects = chart.aspects  # Empty tuple!

# Right
chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .calculate()
)
```

**2. Don't forget to activate pyenv environment:**

```bash
# Wrong
python examples/usage.py  # May fail!

# Right
source ~/.zshrc && pyenv activate stellium && python examples/usage.py
```

**3. Don't modify frozen dataclasses:**

```python
# Wrong
sun = chart.get_object("Sun")
sun.longitude = 45.0  # ERROR: frozen!

# Right
from dataclasses import replace
sun = chart.get_object("Sun")
new_sun = replace(sun, longitude=45.0)
```

---

## Quick Reference

### Key Classes by Module

| Class | Module | Purpose |
|-------|--------|---------|
| **Core Models** |||
| `ChartLocation` | `core.models` | Geographic location |
| `ChartDateTime` | `core.models` | Date/time with Julian day |
| `CelestialPosition` | `core.models` | Object position data |
| `MidpointPosition` | `core.models` | Midpoint position |
| `PhaseData` | `core.models` | Moon/planet phase |
| `HouseCusps` | `core.models` | House cusps data |
| `Aspect` | `core.models` | Aspect between objects |
| `ComparisonAspect` | `core.models` | Cross-chart aspect |
| `AspectPattern` | `core.models` | Aspect pattern |
| `CalculatedChart` | `core.models` | Complete chart data |
| `Comparison` | `core.models` | Synastry/transit comparison |
| **Builders** |||
| `Native` | `core.native` | Input parser |
| `Notable` | `core.native` | Notable births registry |
| `ChartBuilder` | `core.builder` | Chart builder (fluent API) |
| `ComparisonBuilder` | `core.comparison` | Comparison builder |
| `ReportBuilder` | `presentation.builder` | Report builder |
| **Configuration** |||
| `CalculationConfig` | `core.config` | What to calculate |
| `AspectConfig` | `core.config` | Which aspects |
| **Engines** |||
| `SwissEphemerisEngine` | `engines.ephemeris` | Planet positions |
| `PlacidusHouses` | `engines.houses` | Placidus houses |
| `WholeSignHouses` | `engines.houses` | Whole sign houses |
| `KochHouses` | `engines.houses` | Koch houses |
| `EqualHouses` | `engines.houses` | Equal houses |
| `ModernAspectEngine` | `engines.aspects` | Modern aspects |
| `HarmonicAspectEngine` | `engines.aspects` | Harmonic aspects |
| `SimpleOrbEngine` | `engines.orbs` | Simple orbs |
| `LuminariesOrbEngine` | `engines.orbs` | Luminary orbs |
| `ComplexOrbEngine` | `engines.orbs` | Complex orb rules |
| `TraditionalDignityCalculator` | `engines.dignities` | Traditional dignities |
| `ModernDignityCalculator` | `engines.dignities` | Modern dignities |
| `MutualReceptionAnalyzer` | `engines.dignities` | Mutual receptions |
| `AspectPatternAnalyzer` | `engines.patterns` | Pattern detection |
| **Components** |||
| `ArabicPartsCalculator` | `components.arabic_parts` | Arabic parts |
| `MidpointCalculator` | `components.midpoints` | Midpoints |
| `DignityComponent` | `components.dignity` | Essential dignities |
| `AccidentalDignityComponent` | `components.dignity` | Accidental dignities |
| **Visualization** |||
| `ChartRenderer` | `visualization.core` | SVG renderer |
| `ZodiacLayer` | `visualization.layers` | Zodiac wheel |
| `HouseCuspLayer` | `visualization.layers` | House cusps |
| `PlanetLayer` | `visualization.layers` | Planets |
| `AspectLayer` | `visualization.layers` | Aspect lines |
| `draw_chart` | `visualization.drawing` | High-level drawing |

### Common Import Patterns

```python
# Essential imports
from datetime import datetime
from stellium.core.native import Native
from stellium.core.builder import ChartBuilder

# Models
from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    Aspect,
    ObjectType
)

# Configuration
from stellium.core.config import CalculationConfig, AspectConfig

# Engines
from stellium.engines import (
    PlacidusHouses,
    WholeSignHouses,
    ModernAspectEngine,
    SimpleOrbEngine
)

# Components
from stellium.components import (
    ArabicPartsCalculator,
    MidpointCalculator,
    DignityComponent
)

# Visualization
from stellium.visualization import draw_chart

# Reporting
from stellium.presentation import ReportBuilder
```

### Quick Usage Examples

**Minimal chart:**
```python
chart = ChartBuilder.from_notable("Albert Einstein").calculate()
```

**With aspects:**
```python
from stellium.engines import ModernAspectEngine

chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects(ModernAspectEngine())
    .calculate()
)
```

**Full featured:**
```python
from stellium.engines import PlacidusHouses, ModernAspectEngine, AspectPatternAnalyzer
from stellium.components import ArabicPartsCalculator, DignityComponent

chart = (
    ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .add_component(DignityComponent())
    .add_analyzer(AspectPatternAnalyzer())
    .calculate()
)
```

**Generate report:**
```python
from stellium.presentation import ReportBuilder

report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .with_aspects()
    .render()
)
print(report)
```

**Draw chart:**
```python
from stellium.visualization import draw_chart

draw_chart(chart, "output.svg", size=1000)
```

### File Locations

**Core abstractions:** `src/stellium/core/`
**Calculation engines:** `src/stellium/engines/`
**Add-on components:** `src/stellium/components/`
**Chart rendering:** `src/stellium/visualization/`
**Report generation:** `src/stellium/presentation/`
**Tests:** `tests/`
**Examples:** `examples/`
**Documentation:** `docs/`

---

## Appendix: Swiss Ephemeris Setup

Stellium requires Swiss Ephemeris data files. These are included in `data/swisseph/ephe/`.

**Default path:** `src/stellium/data/swisseph/ephe/`

**Custom path:**
```python
from stellium.engines import SwissEphemerisEngine

engine = SwissEphemerisEngine(ephemeris_path="/path/to/ephe")
chart = ChartBuilder.from_native(native).with_ephemeris(engine).calculate()
```

**Environment setup (from CLAUDE.md):**

Always activate the pyenv environment before running:

```bash
source ~/.zshrc && pyenv activate stellium && python your_script.py
```

---

**End of Architecture Documentation**
