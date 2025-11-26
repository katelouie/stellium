# 🌟 Stellium Architecture Refactor: Ground-Up Rebuild Guide

**Timeline**: 2 weeks
**Goal**: Transform Stellium into a composable, component-based astrology platform
**Approach**: Clean slate - we're building the foundation right this time

---

## Table of Contents

- [Philosophy & Principles](#philosophy--principles)
- [Week 1: Core Architecture](#week-1-core-architecture)
  - [Day 1: Project Structure & Data Model](#day-1-project-structure--data-model)
  - [Day 2: Core Protocols](#day-2-core-protocols)
  - [Day 3: Ephemeris Engine](#day-3-ephemeris-engine)
  - [Day 4: House Systems](#day-4-house-systems)
  - [Day 5: Chart Builder](#day-5-chart-builder)
- [Week 2: Components & Validation](#week-2-components--validation)
  - [Day 6: Aspect Engine](#day-6-aspect-engine)
  - [Day 7: Dignity Calculator](#day-7-dignity-calculator)
  - [Day 8: Test & Validate](#day-8-test--validate)
  - [Day 9: Migration Tools](#day-9-migration-tools)
  - [Day 10: Documentation](#day-10-documentation)

---

## Philosophy & Principles

### The React Analogy

```jsx
// React: Composable UI components
<App>
  <Header />
  <ChartDisplay chart={data} />
  <AspectTable aspects={aspects} />
</App>
```

```python
# Stellium: Composable astrological components
chart = ChartBuilder(datetime, location) \
    .with_ephemeris(SwissEphemeris()) \
    .with_houses(PlacidusHouses()) \
    .with_aspects(ModernAspects()) \
    .calculate()
```

### Core Principles

1. **Separation of Concerns**: Each component has ONE job
2. **Dependency Injection**: Components don't create their dependencies
3. **Immutability**: Data objects are read-only after creation
4. **Protocols Over Inheritance**: Use Python protocols for interfaces
5. **Explicit Over Implicit**: No magic, no hidden state

### What We're Building

```
stellium/
├── core/
│   ├── protocols.py       # Interface definitions
│   ├── models.py          # Immutable data classes
│   └── builder.py         # ChartBuilder
├── engines/
│   ├── ephemeris.py       # SwissEphemerisEngine
│   ├── houses.py          # House system engines
│   ├── aspects.py         # Aspect calculation engines
│   └── dignities.py       # Dignity calculation engines
├── components/
│   ├── arabic_parts.py    # Arabic parts calculator
│   ├── midpoints.py       # Midpoint calculator
│   └── patterns.py        # Pattern detection (future)
└── utils/
    ├── cache.py           # Keep existing cache
    └── coordinates.py     # Location/timezone utilities
```

---

# Week 1: Core Architecture

## Day 1: Project Structure & Data Model

### Step 1.1: Create New Directory Structure

```bash
# Create new architecture directories
mkdir -p src/stellium/core
mkdir -p src/stellium/engines
mkdir -p src/stellium/components
mkdir -p src/stellium/utils

# Create __init__.py files
touch src/stellium/core/__init__.py
touch src/stellium/engines/__init__.py
touch src/stellium/components/__init__.py
touch src/stellium/utils/__init__.py
```

### Step 1.2: Create Immutable Data Models

**File**: `src/stellium/core/models.py`

```python
"""
Immutable data models for astrological calculations.

These are pure data containers - no business logic, no calculations.
They represent the OUTPUT of calculations, not the process.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ObjectType(Enum):
    """Type of astrological object."""
    PLANET = "planet"
    ANGLE = "angle"
    ASTEROID = "asteroid"
    ARABIC_PART = "arabic_part"
    MIDPOINT = "midpoint"
    FIXED_STAR = "fixed_star"


@dataclass(frozen=True)
class ChartLocation:
    """Immutable location data for chart calculation."""
    latitude: float
    longitude: float
    name: str = ""
    timezone: str = ""

    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class ChartDateTime:
    """Immutable datetime data for chart calculation."""
    utc_datetime: datetime
    julian_day: float
    local_datetime: Optional[datetime] = None

    def __post_init__(self):
        """Ensure datetime is timezone-aware."""
        if self.utc_datetime.tzinfo is None:
            raise ValueError("DateTime must be timezone-aware")


@dataclass(frozen=True)
class CelestialPosition:
    """
    Immutable representation of a celestial object's position.

    This is the OUTPUT of ephemeris calculations.
    """
    # Identity
    name: str
    object_type: ObjectType

    # Positional data
    longitude: float  # 0-360 degrees
    latitude: float = 0.0
    distance: float = 0.0

    # Velocity data
    speed_longitude: float = 0.0
    speed_latitude: float = 0.0
    speed_distance: float = 0.0

    # Derived data (calculated from longitude)
    sign: str = field(init=False)
    sign_degree: float = field(init=False)

    # Optional metadata
    house: Optional[int] = None
    is_retrograde: bool = field(init=False)

    def __post_init__(self):
        """Calculate derived fields."""
        # Use object.__setattr__ because the dataclass is frozen
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

        object.__setattr__(self, 'sign', signs[int(self.longitude // 30)])
        object.__setattr__(self, 'sign_degree', self.longitude % 30)
        object.__setattr__(self, 'is_retrograde', self.speed_longitude < 0)

    @property
    def sign_position(self) -> str:
        """Human-readable sign position (e.g., '15°23' Aries')."""
        degrees = int(self.sign_degree)
        minutes = int((self.sign_degree % 1) * 60)
        return f"{degrees}°{minutes:02d}' {self.sign}"


@dataclass(frozen=True)
class HouseCusps:
    """Immutable house cusp data."""
    system: str
    cusps: tuple[float, ...]  # 12 cusps, 0-360 degrees

    def __post_init__(self):
        """Validate cusp count."""
        if len(self.cusps) != 12:
            raise ValueError(f"Expected 12 cusps, got {len(self.cusps)}")

    def get_cusp(self, house_number: int) -> float:
        """Get cusp for a specific house (1-12)."""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        return self.cusps[house_number - 1]


@dataclass(frozen=True)
class Aspect:
    """Immutable aspect between two objects."""
    object1: CelestialPosition
    object2: CelestialPosition
    aspect_name: str
    aspect_degree: int  # 0, 60, 90, 120, 180, etc.
    orb: float  # Actual orb in degrees
    is_applying: Optional[bool] = None

    @property
    def description(self) -> str:
        """Human-readable aspect description."""
        applying = " (applying)" if self.is_applying else " (separating)" if self.is_applying is not None else ""
        return f"{self.object1.name} {self.aspect_name} {self.object2.name} (orb: {self.orb:.2f}°){applying}"


@dataclass(frozen=True)
class CalculatedChart:
    """
    Complete calculated chart - the final output.

    This is what a ChartBuilder returns. It's immutable and contains
    everything you need to analyze or visualize the chart.
    """
    # Input parameters
    datetime: ChartDateTime
    location: ChartLocation

    # Calculated data
    positions: tuple[CelestialPosition, ...]
    houses: HouseCusps
    aspects: tuple[Aspect, ...] = ()

    # Metadata
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_object(self, name: str) -> Optional[CelestialPosition]:
        """Get a celestial object by name."""
        for obj in self.positions:
            if obj.name == name:
                return obj
        return None

    def get_planets(self) -> List[CelestialPosition]:
        """Get all planetary objects."""
        return [p for p in self.positions if p.object_type == ObjectType.PLANET]

    def get_angles(self) -> List[CelestialPosition]:
        """Get all chart angles."""
        return [p for p in self.positions if p.object_type == ObjectType.ANGLE]

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        This enables web API integration, storage, etc.
        """
        return {
            'datetime': {
                'utc': self.datetime.utc_datetime.isoformat(),
                'julian_day': self.datetime.julian_day,
            },
            'location': {
                'latitude': self.location.latitude,
                'longitude': self.location.longitude,
                'name': self.location.name,
            },
            'houses': {
                'system': self.houses.system,
                'cusps': list(self.houses.cusps),
            },
            'positions': [
                {
                    'name': p.name,
                    'type': p.object_type.value,
                    'longitude': p.longitude,
                    'latitude': p.latitude,
                    'sign': p.sign,
                    'sign_degree': p.sign_degree,
                    'house': p.house,
                    'is_retrograde': p.is_retrograde,
                }
                for p in self.positions
            ],
            'aspects': [
                {
                    'object1': a.object1.name,
                    'object2': a.object2.name,
                    'aspect': a.aspect_name,
                    'orb': a.orb,
                }
                for a in self.aspects
            ],
        }
```

**Why This Matters:**
- Immutable data = no hidden state changes
- Clear separation: data vs. calculation logic
- Easy to serialize (for JSON export, caching)
- Type-safe with dataclasses

### Step 1.3: Test the Data Models

**File**: `tests/test_core_models.py`

```python
"""Test core data models."""

import pytest
from datetime import datetime
import pytz
from stellium.core.models import (
    ChartLocation,
    ChartDateTime,
    CelestialPosition,
    ObjectType,
    HouseCusps,
)


def test_chart_location_validation():
    """Test location coordinate validation."""
    # Valid location
    loc = ChartLocation(latitude=37.7749, longitude=-122.4194, name="San Francisco")
    assert loc.latitude == 37.7749

    # Invalid latitude
    with pytest.raises(ValueError):
        ChartLocation(latitude=91.0, longitude=0.0)

    # Invalid longitude
    with pytest.raises(ValueError):
        ChartLocation(latitude=0.0, longitude=181.0)


def test_celestial_position_immutability():
    """Test that CelestialPosition is immutable."""
    pos = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=45.5,
        speed_longitude=0.98,
    )

    # Verify calculated fields
    assert pos.sign == "Taurus"  # 45° is in Taurus (30-60)
    assert abs(pos.sign_degree - 15.5) < 0.01
    assert pos.is_retrograde == False

    # Verify immutability
    with pytest.raises(Exception):  # Will raise AttributeError or FrozenInstanceError
        pos.longitude = 50.0


def test_house_cusps_validation():
    """Test house cusp validation."""
    cusps = tuple(i * 30 for i in range(12))  # Simple 30° houses
    houses = HouseCusps(system="Equal", cusps=cusps)

    assert houses.get_cusp(1) == 0.0
    assert houses.get_cusp(12) == 330.0

    # Invalid house number
    with pytest.raises(ValueError):
        houses.get_cusp(13)


def test_sign_position_formatting():
    """Test human-readable sign position."""
    pos = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=95.75,  # 5.75° Cancer
    )

    assert pos.sign == "Cancer"
    assert "5°45'" in pos.sign_position
    assert "Cancer" in pos.sign_position


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run the tests:**

```bash
source ~/.zshrc && pyenv activate stellium && python tests/test_core_models.py
```

---

## Day 2: Core Protocols

### Step 2.1: Define Protocol Interfaces

**File**: `src/stellium/core/protocols.py`

```python
"""
Protocol definitions for Stellium components.

Protocols define INTERFACES - what methods a component must implement.
They don't provide implementation - that's in the engine classes.

Think of these as contracts: "If you want to be an EphemerisEngine,
you must implement these methods with these signatures."
"""

from typing import Protocol, List, Tuple, Optional, Dict, Any
from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    CelestialPosition,
    HouseCusps,
    Aspect,
)


class EphemerisEngine(Protocol):
    """
    Protocol for planetary position calculation engines.

    Different implementations might use:
    - Swiss Ephemeris (our default)
    - JPL ephemeris
    - Custom calculation algorithms
    - Mock data for testing
    """

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: Optional[List[str]] = None,
    ) -> List[CelestialPosition]:
        """
        Calculate positions for celestial objects.

        Args:
            datetime: When to calculate positions
            location: Where to calculate from (for topocentric)
            objects: Which objects to calculate (None = all standard objects)

        Returns:
            List of CelestialPosition objects
        """
        ...


class HouseSystemEngine(Protocol):
    """
    Protocol for house system calculation engines.

    Different implementations for different house systems:
    - Placidus
    - Koch
    - Whole Sign
    - Equal House
    - etc.
    """

    @property
    def system_name(self) -> str:
        """Name of this house system (e.g., 'Placidus')."""
        ...

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        """
        Calculate house cusps for this system.

        Args:
            datetime: Chart datetime
            location: Chart location

        Returns:
            HouseCusps object with 12 cusp positions
        """
        ...

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> List[CelestialPosition]:
        """
        Assign house numbers to celestial positions.

        Args:
            positions: Celestial objects to assign houses to
            cusps: House cusps to use for assignment

        Returns:
            New list of CelestialPosition objects with house assignments
        """
        ...


class AspectEngine(Protocol):
    """
    Protocol for aspect calculation engines.

    Different implementations might use:
    - Traditional aspects (Ptolemaic)
    - Modern aspects (including minor aspects)
    - Harmonic aspects
    - Vedic aspects (completely different system)
    """

    def calculate_aspects(
        self,
        positions: List[CelestialPosition],
        orb_config: Optional[Dict[str, float]] = None,
    ) -> List[Aspect]:
        """
        Calculate aspects between celestial objects.

        Args:
            positions: Objects to find aspects between
            orb_config: Optional custom orb settings

        Returns:
            List of Aspect objects
        """
        ...


class DignityCalculator(Protocol):
    """
    Protocol for dignity/debility calculation.

    Different implementations:
    - Traditional essential dignities
    - Modern rulerships
    - Vedic dignity system
    """

    def calculate_dignities(
        self,
        position: CelestialPosition,
    ) -> Dict[str, Any]:
        """
        Calculate dignities for a celestial position.

        Args:
            position: Position to calculate dignities for

        Returns:
            Dictionary with dignity information
        """
        ...


class ChartComponent(Protocol):
    """
    Base protocol for chart calculation components.

    Components can be:
    - Arabic part calculators
    - Midpoint finders
    - Pattern detectors (Grand Trine, T-Square, etc.)
    - Fixed star calculators
    - Harmonic charts
    """

    @property
    def component_name(self) -> str:
        """Name of this component."""
        ...

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: List[CelestialPosition],
        houses: HouseCusps,
    ) -> List[CelestialPosition]:
        """
        Calculate additional chart objects.

        Args:
            datetime: Chart datetime
            location: Chart location
            positions: Already calculated positions
            houses: House cusps

        Returns:
            List of additional CelestialPosition objects
        """
        ...
```

**Why Protocols?**
- More Pythonic than abstract base classes
- Duck typing with type checking
- Easier to test (mock implementations)
- No inheritance baggage

### Step 2.2: Create Configuration Models

**File**: `src/stellium/core/config.py`

```python
"""Configuration models for chart calculation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AspectConfig:
    """Configuration for aspect calculations."""

    # Which aspects to calculate
    aspects: Dict[str, int] = field(default_factory=lambda: {
        'Conjunction': 0,
        'Sextile': 60,
        'Square': 90,
        'Trine': 120,
        'Opposition': 180,
    })

    # Orb allowances for each aspect
    orbs: Dict[str, float] = field(default_factory=lambda: {
        'Conjunction': 8.0,
        'Sextile': 6.0,
        'Square': 8.0,
        'Trine': 8.0,
        'Opposition': 8.0,
    })

    # Which objects to include in aspect calculations
    include_angles: bool = True
    include_asteroids: bool = True

    @classmethod
    def tight(cls) -> 'AspectConfig':
        """Tight orb configuration."""
        config = cls()
        config.orbs = {k: v * 0.75 for k, v in config.orbs.items()}
        return config

    @classmethod
    def wide(cls) -> 'AspectConfig':
        """Wide orb configuration."""
        config = cls()
        config.orbs = {k: v * 1.25 for k, v in config.orbs.items()}
        return config


@dataclass
class CalculationConfig:
    """Overall configuration for chart calculations."""

    # Which objects to calculate
    include_planets: List[str] = field(default_factory=lambda: [
        'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
        'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
    ])
    include_nodes: bool = True
    include_chiron: bool = True
    include_asteroids: List[str] = field(default_factory=lambda: [
        'Chiron', 'Pholus', 'Ceres', 'Pallas', 'Juno', 'Vesta'
    ])

    # Aspect configuration
    aspect_config: AspectConfig = field(default_factory=AspectConfig)

    # House system
    house_system: str = "Placidus"

    @classmethod
    def minimal(cls) -> 'CalculationConfig':
        """Minimal calculation - planets only."""
        return cls(
            include_nodes=False,
            include_chiron=False,
            include_asteroids=[],
        )

    @classmethod
    def comprehensive(cls) -> 'CalculationConfig':
        """Comprehensive calculation - everything."""
        return cls(
            include_nodes=True,
            include_chiron=True,
            include_asteroids=['Chiron', 'Pholus', 'Ceres', 'Pallas', 'Juno', 'Vesta'],
        )
```

---

## Day 3: Ephemeris Engine

### Step 3.1: Create Swiss Ephemeris Engine

**File**: `src/stellium/engines/ephemeris.py`

```python
"""Ephemeris calculation engines."""

import os
from typing import List, Optional, Dict
import swisseph as swe

from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    CelestialPosition,
    ObjectType,
)
from stellium.cache import cached


def _set_ephemeris_path():
    """Set the path to Swiss Ephemeris data files."""
    path_lib = os.path.dirname(os.path.dirname(__file__))
    path_project = os.path.dirname(path_lib)
    path_data = os.path.join(path_project, "data", "swisseph", "ephe") + os.sep
    swe.set_ephe_path(path_data)


# Swiss Ephemeris object IDs
SWISS_EPHEMERIS_IDS = {
    'Sun': 0,
    'Moon': 1,
    'Mercury': 2,
    'Venus': 3,
    'Mars': 4,
    'Jupiter': 5,
    'Saturn': 6,
    'Uranus': 7,
    'Neptune': 8,
    'Pluto': 9,
    'Mean Node': 10,
    'True Node': 11,
    'Mean Apogee': 12,  # Mean Lilith
    'True Apogee': 13,  # True Lilith
    'Chiron': 15,
    'Pholus': 16,
    'Ceres': 17,
    'Pallas': 18,
    'Juno': 19,
    'Vesta': 20,
}


class SwissEphemerisEngine:
    """
    Swiss Ephemeris calculation engine.

    This is our default, high-precision ephemeris calculator.
    Uses the pyswisseph library for accurate planetary positions.
    """

    def __init__(self):
        """Initialize Swiss Ephemeris."""
        _set_ephemeris_path()
        self._object_ids = SWISS_EPHEMERIS_IDS.copy()

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: Optional[List[str]] = None,
    ) -> List[CelestialPosition]:
        """
        Calculate positions using Swiss Ephemeris.

        Args:
            datetime: When to calculate
            location: Where to calculate from
            objects: Which objects to calculate (None = all standard)

        Returns:
            List of CelestialPosition objects
        """
        # Default to all major objects
        if objects is None:
            objects = [
                'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
                'True Node', 'Chiron',
            ]

        positions = []

        for obj_name in objects:
            if obj_name not in self._object_ids:
                continue

            obj_id = self._object_ids[obj_name]
            position = self._calculate_single_position(
                datetime.julian_day,
                obj_id,
                obj_name,
            )
            positions.append(position)

        # Add South Node (opposite of True Node)
        if 'True Node' in objects:
            north_node = next(p for p in positions if p.name == 'True Node')
            south_node = CelestialPosition(
                name='South Node',
                object_type=ObjectType.PLANET,
                longitude=(north_node.longitude + 180) % 360,
                latitude=-north_node.latitude,
                speed_longitude=-north_node.speed_longitude,
                speed_latitude=-north_node.speed_latitude,
            )
            positions.append(south_node)

        return positions

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_single_position(
        self,
        julian_day: float,
        object_id: int,
        object_name: str,
    ) -> CelestialPosition:
        """
        Calculate position for a single object (cached).

        Args:
            julian_day: Julian day number
            object_id: Swiss Ephemeris object ID
            object_name: Name of the object

        Returns:
            CelestialPosition
        """
        try:
            result = swe.calc_ut(julian_day, object_id)

            return CelestialPosition(
                name=object_name,
                object_type=ObjectType.PLANET,
                longitude=result[0][0],
                latitude=result[0][1],
                distance=result[0][2],
                speed_longitude=result[0][3],
                speed_latitude=result[0][4],
                speed_distance=result[0][5],
            )
        except swe.Error as e:
            raise RuntimeError(f"Failed to calculate {object_name}: {e}")


class MockEphemerisEngine:
    """
    Mock ephemeris engine for testing.

    Returns fixed positions instead of calculating them.
    Useful for:
    - Unit tests
    - Development
    - Benchmarking other components
    """

    def __init__(self, mock_data: Optional[Dict[str, float]] = None):
        """
        Initialize mock engine.

        Args:
            mock_data: Optional dict of {object_name: longitude}
        """
        self._mock_data = mock_data or {
            'Sun': 0.0,  # 0° Aries
            'Moon': 90.0,  # 0° Cancer
            'Mercury': 30.0,  # 0° Taurus
            'Venus': 60.0,  # 0° Gemini
            'Mars': 120.0,  # 0° Leo
        }

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: Optional[List[str]] = None,
    ) -> List[CelestialPosition]:
        """Return mock positions."""
        if objects is None:
            objects = list(self._mock_data.keys())

        positions = []
        for obj_name in objects:
            if obj_name in self._mock_data:
                positions.append(CelestialPosition(
                    name=obj_name,
                    object_type=ObjectType.PLANET,
                    longitude=self._mock_data[obj_name],
                    speed_longitude=1.0,  # Direct motion
                ))

        return positions
```

### Step 3.2: Test the Ephemeris Engine

**File**: `tests/test_ephemeris_engine.py`

```python
"""Test ephemeris engines."""

import pytest
from datetime import datetime
import pytz

from stellium.core.models import ChartDateTime, ChartLocation
from stellium.engines.ephemeris import SwissEphemerisEngine, MockEphemerisEngine


def test_mock_ephemeris_engine():
    """Test the mock ephemeris engine."""
    engine = MockEphemerisEngine()

    dt = ChartDateTime(
        utc_datetime=datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC),
        julian_day=2451545.0,
    )
    loc = ChartLocation(latitude=0, longitude=0)

    positions = engine.calculate_positions(dt, loc, objects=['Sun', 'Moon'])

    assert len(positions) == 2
    sun = next(p for p in positions if p.name == 'Sun')
    assert sun.longitude == 0.0
    assert sun.sign == 'Aries'


def test_swiss_ephemeris_engine():
    """Test Swiss Ephemeris calculation."""
    engine = SwissEphemerisEngine()

    # Einstein's birth date
    dt = ChartDateTime(
        utc_datetime=datetime(1879, 3, 14, 11, 30, tzinfo=pytz.UTC),
        julian_day=2407452.9791666665,
    )
    loc = ChartLocation(latitude=48.5333, longitude=7.5833, name="Ulm, Germany")

    positions = engine.calculate_positions(dt, loc, objects=['Sun', 'Moon'])

    assert len(positions) == 2

    sun = next(p for p in positions if p.name == 'Sun')
    assert sun.sign == 'Pisces'  # Sun in Pisces for mid-March
    assert sun.is_retrograde == False

    moon = next(p for p in positions if p.name == 'Moon')
    assert moon.name == 'Moon'
    assert 0 <= moon.longitude < 360


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Day 4: House Systems

### Step 4.1: Create House System Engines

**File**: `src/stellium/engines/houses.py`

```python
"""House system calculation engines."""

from typing import List
import swisseph as swe
from dataclasses import replace

from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    CelestialPosition,
)
from stellium.cache import cached


# Swiss Ephemeris house system codes
HOUSE_SYSTEM_CODES = {
    "Placidus": b"P",
    "Koch": b"K",
    "Porphyry": b"O",
    "Regiomontanus": b"R",
    "Campanus": b"C",
    "Equal": b"A",
    "Equal (MC)": b"D",
    "Vehlow Equal": b"V",
    "Whole Sign": b"W",
    "Alcabitius": b"B",
    "Topocentric": b"T",
    "Morinus": b"M",
}


class PlacidusHouses:
    """Placidus house system engine."""

    @property
    def system_name(self) -> str:
        return "Placidus"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        """Calculate Placidus house cusps."""
        cusps_list, _ = self._calculate_swiss_houses(
            datetime.julian_day,
            location.latitude,
            location.longitude,
            HOUSE_SYSTEM_CODES["Placidus"]
        )

        return HouseCusps(
            system=self.system_name,
            cusps=tuple(cusps_list),
        )

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> List[CelestialPosition]:
        """Assign house numbers to positions."""
        result = []

        for pos in positions:
            house_num = self._find_house(pos.longitude, cusps.cusps)
            # Create new position with house assigned
            new_pos = replace(pos, house=house_num)
            result.append(new_pos)

        return result

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_swiss_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        system_code: bytes,
    ):
        """Cached Swiss Ephemeris house calculation."""
        return swe.houses(julian_day, latitude, longitude, hsys=system_code)

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Find which house a longitude falls in."""
        cusp_list = list(cusps)

        for i in range(12):
            cusp1 = cusp_list[i]
            cusp2 = cusp_list[(i + 1) % 12]

            # Handle wrapping around 360°
            if cusp2 < cusp1:
                cusp2 += 360
                test_long = longitude if longitude >= cusp1 else longitude + 360
            else:
                test_long = longitude

            if cusp1 <= test_long < cusp2:
                return i + 1

        return 1  # Fallback


class WholeSignHouses:
    """Whole Sign house system engine."""

    @property
    def system_name(self) -> str:
        return "Whole Sign"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        """
        Calculate Whole Sign house cusps.

        In Whole Sign houses, each house = one whole sign.
        The 1st house cusp is the Ascendant's sign start.
        """
        # Get the Ascendant using Placidus (we need it for whole sign too)
        swiss_cusps, angles = swe.houses(
            datetime.julian_day,
            location.latitude,
            location.longitude,
            hsys=b"P"
        )

        asc = angles[0]  # Ascendant
        asc_sign = int(asc // 30)  # Which sign is ASC in?

        # Each house starts at the beginning of the next sign
        cusps = []
        for i in range(12):
            sign = (asc_sign + i) % 12
            cusp = sign * 30.0
            cusps.append(cusp)

        return HouseCusps(
            system=self.system_name,
            cusps=tuple(cusps),
        )

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> List[CelestialPosition]:
        """Assign houses in whole sign system."""
        result = []

        for pos in positions:
            # In whole sign, the sign determines the house directly
            sign_num = int(pos.longitude // 30)
            cusp0_sign = int(cusps.cusps[0] // 30)
            house_num = ((sign_num - cusp0_sign) % 12) + 1

            new_pos = replace(pos, house=house_num)
            result.append(new_pos)

        return result


class EqualHouses:
    """Equal house system engine (from Ascendant)."""

    @property
    def system_name(self) -> str:
        return "Equal"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        """Calculate Equal house cusps."""
        # Get Ascendant
        _, angles = swe.houses(
            datetime.julian_day,
            location.latitude,
            location.longitude,
            hsys=b"P"
        )
        asc = angles[0]

        # Each house is exactly 30° from the Ascendant
        cusps = [(asc + i * 30) % 360 for i in range(12)]

        return HouseCusps(
            system=self.system_name,
            cusps=tuple(cusps),
        )

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> List[CelestialPosition]:
        """Assign houses."""
        # Same logic as Placidus
        placidus = PlacidusHouses()
        return placidus.assign_houses(positions, cusps)
```

**Why Multiple House Systems?**
- Different astrological traditions use different systems
- Each has different calculation logic
- Clean separation makes it easy to add new ones
- Users can choose which to use

---

## Day 5: Chart Builder

### Step 5.1: Create the ChartBuilder

**File**: `src/stellium/core/builder.py`

```python
"""
ChartBuilder - The main API for creating charts.

This is the fluent interface that users interact with.
It orchestrates all the engines and components to build a complete chart.
"""

from datetime import datetime
from typing import Optional, List
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim

from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    CalculatedChart,
    CelestialPosition,
    ObjectType,
)
from stellium.core.config import CalculationConfig
from stellium.engines.ephemeris import SwissEphemerisEngine
from stellium.engines.houses import PlacidusHouses
from stellium.cache import cached


class ChartBuilder:
    """
    Fluent builder for creating astrological charts.

    Usage:
        chart = ChartBuilder.from_datetime(dt, location) \\
            .with_ephemeris(SwissEphemeris()) \\
            .with_houses(PlacidusHouses()) \\
            .calculate()
    """

    def __init__(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ):
        """
        Initialize builder with required data.

        Args:
            datetime: Chart datetime
            location: Chart location
        """
        self._datetime = datetime
        self._location = location

        # Default engines (can be overridden)
        self._ephemeris = SwissEphemerisEngine()
        self._houses = PlacidusHouses()
        self._aspect_engine = None  # Optional

        # Configuration
        self._config = CalculationConfig()

        # Additional components
        self._components = []

    @classmethod
    def from_datetime(
        cls,
        dt: datetime,
        location: ChartLocation,
    ) -> 'ChartBuilder':
        """
        Create builder from a datetime.

        Args:
            dt: Datetime (must be timezone-aware)
            location: Chart location

        Returns:
            ChartBuilder instance
        """
        # Ensure UTC
        if dt.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware")
        utc_dt = dt.astimezone(pytz.UTC)

        # Calculate Julian day
        hour_decimal = utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        julian_day = swe.date_conversion(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + hour_decimal,
        )[1]

        chart_dt = ChartDateTime(
            utc_datetime=utc_dt,
            julian_day=julian_day,
        )

        return cls(chart_dt, location)

    @classmethod
    def from_location_name(
        cls,
        dt: datetime,
        location_name: str,
    ) -> 'ChartBuilder':
        """
        Create builder from a location name (geocoded).

        Args:
            dt: Datetime
            location_name: Name to geocode (e.g., "San Francisco, CA")

        Returns:
            ChartBuilder instance
        """
        location_data = _cached_geocode(location_name)

        if not location_data:
            raise ValueError(f"Could not geocode location: {location_name}")

        location = ChartLocation(
            latitude=location_data['latitude'],
            longitude=location_data['longitude'],
            name=location_data['address'],
        )

        return cls.from_datetime(dt, location)

    # Fluent configuration methods

    def with_ephemeris(self, engine) -> 'ChartBuilder':
        """Set the ephemeris engine."""
        self._ephemeris = engine
        return self

    def with_houses(self, engine) -> 'ChartBuilder':
        """Set the house system engine."""
        self._houses = engine
        return self

    def with_aspects(self, engine) -> 'ChartBuilder':
        """Set the aspect calculation engine."""
        self._aspect_engine = engine
        return self

    def with_config(self, config: CalculationConfig) -> 'ChartBuilder':
        """Set the calculation configuration."""
        self._config = config
        return self

    def add_component(self, component) -> 'ChartBuilder':
        """Add an additional calculation component."""
        self._components.append(component)
        return self

    # Calculation

    def calculate(self) -> CalculatedChart:
        """
        Execute all calculations and return the final chart.

        Returns:
            CalculatedChart with all calculated data
        """
        # Step 1: Calculate planetary positions
        objects_to_calculate = self._get_objects_list()
        positions = self._ephemeris.calculate_positions(
            self._datetime,
            self._location,
            objects_to_calculate,
        )

        # Step 2: Calculate house cusps
        houses = self._houses.calculate_cusps(self._datetime, self._location)

        # Step 3: Assign houses to positions
        positions = self._houses.assign_houses(positions, houses)

        # Step 4: Add chart angles as positions
        positions.extend(self._calculate_angles(houses))

        # Step 5: Run additional components (Arabic parts, etc.)
        for component in self._components:
            additional = component.calculate(
                self._datetime,
                self._location,
                positions,
                houses,
            )
            positions.extend(additional)

        # Step 6: Calculate aspects (if engine provided)
        aspects = []
        if self._aspect_engine:
            aspects = self._aspect_engine.calculate_aspects(
                positions,
                orb_config=self._config.aspect_config.orbs,
            )

        # Step 7: Build final chart
        return CalculatedChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            houses=houses,
            aspects=tuple(aspects),
        )

    def _get_objects_list(self) -> List[str]:
        """Get list of objects to calculate based on config."""
        objects = self._config.include_planets.copy()

        if self._config.include_nodes:
            objects.append('True Node')

        if self._config.include_chiron:
            objects.append('Chiron')

        objects.extend(self._config.include_asteroids)

        return objects

    def _calculate_angles(self, houses) -> List[CelestialPosition]:
        """Calculate chart angles from house cusps."""
        asc = houses.get_cusp(1)
        mc = houses.get_cusp(10)

        angles = [
            CelestialPosition(
                name='ASC',
                object_type=ObjectType.ANGLE,
                longitude=asc,
            ),
            CelestialPosition(
                name='MC',
                object_type=ObjectType.ANGLE,
                longitude=mc,
            ),
            CelestialPosition(
                name='DSC',
                object_type=ObjectType.ANGLE,
                longitude=(asc + 180) % 360,
            ),
            CelestialPosition(
                name='IC',
                object_type=ObjectType.ANGLE,
                longitude=(mc + 180) % 360,
            ),
        ]

        return angles


@cached(cache_type="geocoding", max_age_seconds=604800)
def _cached_geocode(location_name: str) -> dict:
    """Cached geocoding."""
    try:
        geolocator = Nominatim(user_agent="stellium_geocoder")
        location = geolocator.geocode(location_name)

        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": str(location),
            }
        return {}
    except Exception as e:
        print(f"Geocoding error: {e}")
        return {}
```

### Step 5.2: Test the ChartBuilder

**File**: `tests/test_chart_builder.py`

```python
"""Test ChartBuilder."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.ephemeris import MockEphemerisEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses


def test_basic_chart_building():
    """Test basic chart construction."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_ephemeris(MockEphemerisEngine()) \
        .calculate()

    assert chart.datetime.utc_datetime == dt
    assert chart.location.name == "SF"
    assert len(chart.positions) > 0


def test_house_system_swapping():
    """Test that we can easily swap house systems."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)

    # Placidus
    chart1 = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .calculate()

    # Whole Sign
    chart2 = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()) \
        .calculate()

    assert chart1.houses.system == "Placidus"
    assert chart2.houses.system == "Whole Sign"
    # Cusps should be different
    assert chart1.houses.cusps != chart2.houses.cusps


def test_from_location_name():
    """Test geocoding integration."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)

    try:
        chart = ChartBuilder.from_location_name(dt, "San Francisco, CA") \
            .calculate()

        assert "San Francisco" in chart.location.name
        assert 37 < chart.location.latitude < 38
        assert -123 < chart.location.longitude < -122
    except ValueError:
        # Geocoding might fail in test environment
        pytest.skip("Geocoding not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run all tests:**

```bash
source ~/.zshrc && pyenv activate stellium && python -m pytest tests/ -v
```

---

## End of Week 1 Checkpoint

At this point, you should have:

✅ Clean, immutable data models
✅ Protocol-based interfaces
✅ Working ephemeris engine
✅ Multiple house system engines
✅ Fluent ChartBuilder API
✅ All tests passing

**Test it end-to-end:**

```python
# Create a quick test script: test_week1.py
from datetime import datetime
import pytz
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.houses import WholeSignHouses

dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="San Francisco")

chart = ChartBuilder.from_datetime(dt, location) \
    .with_houses(WholeSignHouses()) \
    .calculate()

print(f"Chart calculated for {chart.datetime.utc_datetime}")
print(f"Location: {chart.location.name}")
print(f"House system: {chart.houses.system}")
print(f"\nPositions calculated: {len(chart.positions)}")

for pos in chart.get_planets()[:5]:
    print(f"  {pos.name}: {pos.sign_position} (House {pos.house})")

print("\n✨ Week 1 Complete! Architecture is solid.")
```

Run it:
```bash
source ~/.zshrc && pyenv activate stellium && python test_week1.py
```

---

# Week 2: Components & Validation

## Day 6: Aspect Engine

### Step 6.1: Create Aspect Engine

**File**: `src/stellium/engines/aspects.py`

```python
"""Aspect calculation engines."""

from typing import List, Dict, Optional
import math

from stellium.core.models import CelestialPosition, Aspect, ObjectType


class ModernAspectEngine:
    """
    Modern aspect calculation engine.

    Calculates Ptolemaic aspects (major aspects) with configurable orbs.
    """

    def __init__(self, aspect_definitions: Optional[Dict[str, int]] = None):
        """
        Initialize aspect engine.

        Args:
            aspect_definitions: Optional custom aspect angles
        """
        self._aspects = aspect_definitions or {
            'Conjunction': 0,
            'Sextile': 60,
            'Square': 90,
            'Trine': 120,
            'Opposition': 180,
        }

    def calculate_aspects(
        self,
        positions: List[CelestialPosition],
        orb_config: Optional[Dict[str, float]] = None,
    ) -> List[Aspect]:
        """
        Calculate aspects between celestial objects.

        Args:
            positions: Objects to find aspects between
            orb_config: Optional custom orb allowances

        Returns:
            List of Aspect objects
        """
        # Default orbs
        orbs = orb_config or {
            'Conjunction': 8.0,
            'Sextile': 6.0,
            'Square': 8.0,
            'Trine': 8.0,
            'Opposition': 8.0,
        }

        aspects = []

        # Only aspect planets and angles (not Arabic parts, midpoints, etc.)
        valid_types = {ObjectType.PLANET, ObjectType.ANGLE}
        valid_objects = [p for p in positions if p.object_type in valid_types]

        # Check each pair
        for i, obj1 in enumerate(valid_objects):
            for obj2 in valid_objects[i + 1:]:
                # Calculate angular distance
                distance = self._angular_distance(obj1.longitude, obj2.longitude)

                # Check each aspect type
                for aspect_name, aspect_angle in self._aspects.items():
                    orb_allowance = orbs.get(aspect_name, 8.0)
                    actual_orb = abs(distance - aspect_angle)

                    if actual_orb <= orb_allowance:
                        # Calculate if applying or separating
                        is_applying = self._is_applying(obj1, obj2, aspect_angle)

                        aspect = Aspect(
                            object1=obj1,
                            object2=obj2,
                            aspect_name=aspect_name,
                            aspect_degree=aspect_angle,
                            orb=actual_orb,
                            is_applying=is_applying,
                        )
                        aspects.append(aspect)
                        break  # Only one aspect per pair

        return aspects

    def _angular_distance(self, long1: float, long2: float) -> float:
        """Calculate shortest angular distance between two longitudes."""
        diff = abs(long1 - long2)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _is_applying(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_angle: float,
    ) -> Optional[bool]:
        """
        Determine if aspect is applying or separating.

        Returns:
            True if applying, False if separating, None if can't determine
        """
        # Need speed data
        if obj1.speed_longitude == 0 or obj2.speed_longitude == 0:
            return None

        # Calculate current distance
        current_dist = abs(obj1.longitude - obj2.longitude)
        if current_dist > 180:
            current_dist = 360 - current_dist

        # Calculate where they'll be in 1 day
        future_long1 = (obj1.longitude + obj1.speed_longitude) % 360
        future_long2 = (obj2.longitude + obj2.speed_longitude) % 360
        future_dist = abs(future_long1 - future_long2)
        if future_dist > 180:
            future_dist = 360 - future_dist

        # Applying = getting closer to exact aspect
        current_orb = abs(current_dist - aspect_angle)
        future_orb = abs(future_dist - aspect_angle)

        return future_orb < current_orb


class HarmonicAspectEngine:
    """
    Harmonic aspect engine.

    Calculates aspects based on harmonic divisions of the circle.
    For example, harmonic 7 = 360/7 = 51.43° aspects.
    """

    def __init__(self, harmonic: int = 7, orb: float = 2.0):
        """
        Initialize harmonic aspect engine.

        Args:
            harmonic: Harmonic number (e.g., 7 for septile, 9 for novile)
            orb: Orb allowance for harmonic aspects
        """
        self.harmonic = harmonic
        self.orb = orb
        self.aspect_angle = 360 / harmonic

    def calculate_aspects(
        self,
        positions: List[CelestialPosition],
        orb_config: Optional[Dict[str, float]] = None,
    ) -> List[Aspect]:
        """Calculate harmonic aspects."""
        aspects = []

        valid_types = {ObjectType.PLANET, ObjectType.ANGLE}
        valid_objects = [p for p in positions if p.object_type in valid_types]

        for i, obj1 in enumerate(valid_objects):
            for obj2 in valid_objects[i + 1:]:
                distance = self._angular_distance(obj1.longitude, obj2.longitude)

                # Check if distance is a multiple of the harmonic angle
                for multiplier in range(1, self.harmonic):
                    target_angle = self.aspect_angle * multiplier
                    actual_orb = abs(distance - target_angle)

                    if actual_orb <= self.orb:
                        aspect_name = f"H{self.harmonic}/{multiplier}"
                        aspect = Aspect(
                            object1=obj1,
                            object2=obj2,
                            aspect_name=aspect_name,
                            aspect_degree=int(target_angle),
                            orb=actual_orb,
                        )
                        aspects.append(aspect)
                        break

        return aspects

    def _angular_distance(self, long1: float, long2: float) -> float:
        """Calculate shortest angular distance."""
        diff = abs(long1 - long2)
        if diff > 180:
            diff = 360 - diff
        return diff
```

### Step 6.2: Test Aspect Engine

**File**: `tests/test_aspect_engine.py`

```python
"""Test aspect engines."""

import pytest
from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine


def test_conjunction_detection():
    """Test conjunction aspect detection."""
    engine = ModernAspectEngine()

    # Two planets in conjunction (within 8°)
    sun = CelestialPosition(
        name='Sun',
        object_type=ObjectType.PLANET,
        longitude=30.0,
        speed_longitude=1.0,
    )
    mercury = CelestialPosition(
        name='Mercury',
        object_type=ObjectType.PLANET,
        longitude=35.0,  # 5° from Sun
        speed_longitude=1.2,
    )

    aspects = engine.calculate_aspects([sun, mercury])

    assert len(aspects) == 1
    assert aspects[0].aspect_name == 'Conjunction'
    assert aspects[0].orb == 5.0


def test_trine_detection():
    """Test trine aspect detection."""
    engine = ModernAspectEngine()

    sun = CelestialPosition(
        name='Sun',
        object_type=ObjectType.PLANET,
        longitude=0.0,
        speed_longitude=1.0,
    )
    moon = CelestialPosition(
        name='Moon',
        object_type=ObjectType.PLANET,
        longitude=122.0,  # 122° from Sun, within orb of 120° trine
        speed_longitude=13.0,
    )

    aspects = engine.calculate_aspects([sun, moon])

    assert len(aspects) == 1
    assert aspects[0].aspect_name == 'Trine'
    assert aspects[0].orb == 2.0


def test_harmonic_aspects():
    """Test harmonic aspect engine."""
    engine = HarmonicAspectEngine(harmonic=7, orb=2.0)

    # Septile = 360/7 = 51.43°
    obj1 = CelestialPosition(
        name='Sun',
        object_type=ObjectType.PLANET,
        longitude=0.0,
    )
    obj2 = CelestialPosition(
        name='Moon',
        object_type=ObjectType.PLANET,
        longitude=51.0,  # Close to 1st harmonic
    )

    aspects = engine.calculate_aspects([obj1, obj2])

    assert len(aspects) > 0
    assert aspects[0].aspect_name.startswith('H7/')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Day 7: Dignity Calculator

**File**: `src/stellium/engines/dignities.py`

```python
"""Dignity calculation engines."""

from typing import Dict, Any, List
from stellium.core.models import CelestialPosition


# Traditional essential dignities data
TRADITIONAL_DIGNITIES = {
    "Aries": {
        "ruler": "Mars",
        "exaltation": "Sun",
        "detriment": "Venus",
        "fall": "Saturn",
    },
    "Taurus": {
        "ruler": "Venus",
        "exaltation": "Moon",
        "detriment": "Mars",
        "fall": None,
    },
    # ... (rest of the signs - copy from your signs.py DIGNITIES)
}


class TraditionalDignityCalculator:
    """Traditional essential dignities calculator."""

    def calculate_dignities(
        self,
        position: CelestialPosition,
    ) -> Dict[str, Any]:
        """
        Calculate traditional dignities for a position.

        Args:
            position: CelestialPosition to analyze

        Returns:
            Dictionary with dignity information
        """
        if position.name not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            return {}  # Only traditional planets have dignities

        sign_data = TRADITIONAL_DIGNITIES.get(position.sign, {})

        dignities = []
        score = 0

        # Rulership (+5)
        if sign_data.get('ruler') == position.name:
            dignities.append('ruler')
            score += 5

        # Exaltation (+4)
        if sign_data.get('exaltation') == position.name:
            dignities.append('exaltation')
            score += 4

        # Detriment (-5)
        if sign_data.get('detriment') == position.name:
            dignities.append('detriment')
            score -= 5

        # Fall (-4)
        if sign_data.get('fall') == position.name:
            dignities.append('fall')
            score -= 4

        return {
            'planet': position.name,
            'sign': position.sign,
            'dignities': dignities,
            'score': score,
        }
```

---

## Day 8: Test & Validate

### Step 8.1: Create Integration Tests

**File**: `tests/test_integration.py`

```python
"""Integration tests for complete chart calculation."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.aspects import ModernAspectEngine


def test_einstein_chart():
    """Test calculating Einstein's birth chart."""
    dt = datetime(1879, 3, 14, 11, 30, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=48.5333,
        longitude=7.5833,
        name="Ulm, Germany"
    )

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    # Verify chart was calculated
    assert chart.datetime.utc_datetime == dt
    assert chart.location.name == "Ulm, Germany"

    # Verify positions
    assert len(chart.positions) > 10

    # Sun should be in Pisces (mid-March)
    sun = chart.get_object('Sun')
    assert sun is not None
    assert sun.sign == 'Pisces'

    # Verify houses
    assert chart.houses.system == 'Placidus'
    assert len(chart.houses.cusps) == 12

    # Verify aspects calculated
    assert len(chart.aspects) > 0


def test_chart_to_dict():
    """Test chart serialization to dictionary."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0, name="Test")

    chart = ChartBuilder.from_datetime(dt, location).calculate()

    data = chart.to_dict()

    assert 'datetime' in data
    assert 'location' in data
    assert 'houses' in data
    assert 'positions' in data

    # Verify structure
    assert data['location']['name'] == 'Test'
    assert len(data['positions']) > 0
    assert len(data['houses']['cusps']) == 12


def test_different_house_systems():
    """Test that different house systems produce different results."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=40, longitude=-74)

    placidus_chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .calculate()

    whole_sign_chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()) \
        .calculate()

    # Different systems, different cusps
    assert placidus_chart.houses.cusps != whole_sign_chart.houses.cusps

    # But same planetary positions
    p_sun = placidus_chart.get_object('Sun')
    w_sun = whole_sign_chart.get_object('Sun')
    assert p_sun.longitude == w_sun.longitude


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Step 8.2: Performance Benchmarks

**File**: `tests/benchmark_performance.py`

```python
"""Performance benchmarks."""

import time
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.aspects import ModernAspectEngine


def benchmark_chart_calculation():
    """Benchmark basic chart calculation."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)

    iterations = 100
    start = time.time()

    for _ in range(iterations):
        chart = ChartBuilder.from_datetime(dt, location) \
            .with_aspects(ModernAspectEngine()) \
            .calculate()

    elapsed = time.time() - start
    per_chart = elapsed / iterations

    print(f"\n📊 Performance Benchmark")
    print(f"{'='*50}")
    print(f"Charts calculated: {iterations}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Per chart: {per_chart*1000:.2f}ms")
    print(f"Charts/second: {iterations/elapsed:.1f}")
    print(f"{'='*50}\n")

    assert per_chart < 0.5, "Chart calculation should be under 500ms"


if __name__ == "__main__":
    benchmark_chart_calculation()
```

Run it:
```bash
source ~/.zshrc && pyenv activate stellium && python tests/benchmark_performance.py
```

---

## Day 9: Migration Tools

### Step 9.1: Create Migration Guide

**File**: `docs/development/MIGRATION.md`

```markdown
# Migration from Old to New Architecture

## For Users

### Old API (will be deprecated)
```python
from stellium.chart import Chart

chart = Chart(
    datetime_utc=datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC),
    houses='Placidus',
    loc_name="San Francisco, CA",
)

for planet in chart.planets:
    print(f"{planet.name}: {planet.sign}")
```

### New API
```python
from stellium.core.builder import ChartBuilder

chart = ChartBuilder.from_location_name(
    datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC),
    "San Francisco, CA"
).calculate()

for planet in chart.get_planets():
    print(f"{planet.name}: {planet.sign}")
```

## Key Differences

1. **ChartBuilder instead of Chart constructor**
2. **Immutable results** - can't modify after calculation
3. **Explicit configuration** - use `.with_*()` methods
4. **Type safety** - better IDE support

## Advanced Features

### Custom House Systems
```python
from stellium.engines.houses import WholeSignHouses

chart = ChartBuilder.from_location_name(dt, location) \
    .with_houses(WholeSignHouses()) \
    .calculate()
```

### Custom Aspects
```python
from stellium.engines.aspects import HarmonicAspectEngine

chart = ChartBuilder.from_datetime(dt, location) \
    .with_aspects(HarmonicAspectEngine(harmonic=7)) \
    .calculate()
```

### JSON Export
```python
chart_data = chart.to_dict()
# Now you can serialize to JSON, save to database, etc.
```
```

### Step 9.2: Create Compatibility Wrapper (Optional)

If you want to keep old code working temporarily:

**File**: `src/stellium/legacy.py`

```python
"""
Compatibility wrapper for old Chart API.

This allows existing code to keep working while migrating.
Will be removed in version 2.0.
"""

import warnings
from datetime import datetime
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation


class Chart:
    """
    Legacy Chart class - DEPRECATED.

    Use ChartBuilder instead.
    """

    def __init__(
        self,
        datetime_utc: datetime,
        houses: str,
        loc=None,
        loc_name: str = "",
        time_known: bool = True,
    ):
        warnings.warn(
            "Chart class is deprecated. Use ChartBuilder instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Convert to new API
        if loc_name:
            self._chart = ChartBuilder.from_location_name(
                datetime_utc,
                loc_name,
            ).calculate()
        elif loc:
            location = ChartLocation(latitude=loc[0], longitude=loc[1])
            self._chart = ChartBuilder.from_datetime(
                datetime_utc,
                location,
            ).calculate()
        else:
            raise ValueError("Need location")

        # Expose old-style properties
        self.planets = list(self._chart.get_planets())
        self.angles = list(self._chart.get_angles())
        self.cusps = list(self._chart.houses.cusps)
```

---

## Day 10: Documentation

### Step 10.1: Create User Guide

**File**: `docs/USER_GUIDE.md`

```markdown
# Stellium User Guide

## Installation

```bash
pip install stellium  # Once published
```

## Quick Start

### Calculate a Natal Chart

```python
from datetime import datetime
import pytz
from stellium.core.builder import ChartBuilder

# Create a chart
chart = ChartBuilder.from_location_name(
    datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC),
    "San Francisco, CA"
).calculate()

# Access planetary positions
for planet in chart.get_planets():
    print(f"{planet.name}: {planet.sign_position} in House {planet.house}")

# Access aspects
for aspect in chart.aspects:
    print(aspect.description)
```

### Custom House Systems

```python
from stellium.engines.houses import WholeSignHouses

chart = ChartBuilder.from_location_name(dt, "London, UK") \
    .with_houses(WholeSignHouses()) \
    .calculate()

print(f"Using {chart.houses.system} houses")
```

### Export to JSON

```python
import json

data = chart.to_dict()
with open('chart.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Advanced Usage

### Custom Aspect Calculations

```python
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine

# Traditional aspects
chart = ChartBuilder.from_datetime(dt, location) \
    .with_aspects(ModernAspectEngine()) \
    .calculate()

# Harmonic aspects (septiles, noviles, etc.)
chart = ChartBuilder.from_datetime(dt, location) \
    .with_aspects(HarmonicAspectEngine(harmonic=7, orb=2.0)) \
    .calculate()
```

### Configuration Presets

```python
from stellium.core.config import CalculationConfig

# Minimal calculation (faster)
config = CalculationConfig.minimal()

chart = ChartBuilder.from_datetime(dt, location) \
    .with_config(config) \
    .calculate()
```

## Working with Results

### Finding Specific Objects

```python
sun = chart.get_object('Sun')
print(f"Sun: {sun.longitude}° {sun.sign}")
print(f"Retrograde: {sun.is_retrograde}")
```

### Filtering by Type

```python
# Just planets
planets = chart.get_planets()

# Just angles
angles = chart.get_angles()
```

## Next Steps

- See [API Reference](API_REFERENCE.md) for complete documentation
- See [Examples](../examples/) for more use cases
- See [Developer Guide](development/DEVELOPER_GUIDE.md) to extend Stellium
```

---

## End of Week 2 Checkpoint

At this point, you should have:

✅ Complete component-based architecture
✅ Aspect calculation engine
✅ Dignity calculator
✅ Comprehensive tests
✅ Migration guide
✅ User documentation

### Final Validation Test

Create `test_week2_complete.py`:

```python
"""Final validation - everything working together."""

from datetime import datetime
import pytz
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine

def main():
    print("🌟 Stellium Architecture Refactor - Final Test")
    print("="*60)

    # Einstein's chart
    dt = datetime(1879, 3, 14, 11, 30, tzinfo=pytz.UTC)
    location = ChartLocation(48.5333, 7.5833, "Ulm, Germany")

    # Test 1: Basic calculation
    print("\n1️⃣  Basic Chart Calculation")
    chart = ChartBuilder.from_datetime(dt, location).calculate()
    print(f"   ✓ Calculated {len(chart.positions)} positions")
    print(f"   ✓ Sun in {chart.get_object('Sun').sign}")

    # Test 2: Different house systems
    print("\n2️⃣  House System Flexibility")
    placidus = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()).calculate()
    whole_sign = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()).calculate()
    print(f"   ✓ Placidus: {placidus.houses.system}")
    print(f"   ✓ Whole Sign: {whole_sign.houses.system}")

    # Test 3: Aspect calculations
    print("\n3️⃣  Aspect Engines")
    modern = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()).calculate()
    harmonic = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(HarmonicAspectEngine(harmonic=7)).calculate()
    print(f"   ✓ Modern aspects: {len(modern.aspects)}")
    print(f"   ✓ Harmonic 7 aspects: {len(harmonic.aspects)}")

    # Test 4: JSON export
    print("\n4️⃣  Data Export")
    data = chart.to_dict()
    print(f"   ✓ Exported {len(data.keys())} data sections")
    print(f"   ✓ JSON serializable: {type(data) == dict}")

    # Test 5: Immutability
    print("\n5️⃣  Immutability")
    try:
        chart.positions[0].longitude = 999
        print("   ✗ Data is mutable (BAD)")
    except:
        print("   ✓ Data is immutable (GOOD)")

    print("\n" + "="*60)
    print("✨ All systems operational! Refactor complete.")
    print("="*60)

if __name__ == "__main__":
    main()
```

Run it:
```bash
source ~/.zshrc && pyenv activate stellium && python test_week2_complete.py
```

---

## What's Next?

### Immediate Next Steps (Week 3)

1. **Update drawing.py** to work with new data model
2. **Add Arabic Parts component** using the new architecture
3. **Add Midpoints component**
4. **Create example scripts** for the new API
5. **Update README** with new usage examples

### Future Enhancements (Month 2+)

- Synastry calculations (compare two charts)
- Transit calculations
- Progression engines
- Pattern detection (Grand Trine, T-Square, etc.)
- Plugin system for community extensions

---

## Success Criteria

You'll know the refactor is successful when:

✅ All old functionality works with new architecture
✅ Tests pass and have >80% coverage
✅ Adding a new house system takes <30 minutes
✅ Adding a new aspect type takes <30 minutes
✅ The API feels intuitive and discoverable
✅ You can explain the architecture to someone in 5 minutes

---

## Getting Help

If you get stuck:

1. Check the tests - they show how to use everything
2. Re-read the protocols - they define the contracts
3. Look at existing engines - follow the patterns
4. Remember: **Simple > Complex**, **Explicit > Implicit**

---

**You're building something genuinely innovative. Take your time, test thoroughly, and enjoy the process!** 🌟
