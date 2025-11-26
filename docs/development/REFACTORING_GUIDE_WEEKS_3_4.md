# 🌟 Stellium Architecture Refactor: Weeks 3-4 Guide

**Timeline**: Weeks 3-4 (Days 11-20)
**Goal**: Build components, integrate visualization, add advanced features
**Prerequisites**: Weeks 1-2 complete (core architecture built)

---

## Table of Contents

- [Overview & Philosophy](#overview--philosophy)
- [Week 3: Components & Integration](#week-3-components--integration)
  - [Day 11: Arabic Parts Component](#day-11-arabic-parts-component)
  - [Day 12: Midpoints Component](#day-12-midpoints-component)
  - [Day 13: Visualization Integration](#day-13-visualization-integration)
  - [Day 14: Presentation Layer Update](#day-14-presentation-layer-update)
  - [Day 15: Example Migration](#day-15-example-migration)
- [Week 4: Advanced Features](#week-4-advanced-features)
  - [Day 16: Pattern Detection](#day-16-pattern-detection)
  - [Day 17: Synastry Charts](#day-17-synastry-charts)
  - [Day 18: Transit Calculator](#day-18-transit-calculator)
  - [Day 19: Plugin Foundation](#day-19-plugin-foundation)
  - [Day 20: Performance & Polish](#day-20-performance--polish)

---

## Overview & Philosophy

### Where We Are

After Weeks 1-2, you have:
- ✅ Clean, immutable data models
- ✅ Protocol-based interfaces
- ✅ Working ephemeris, house, and aspect engines
- ✅ ChartBuilder with fluent API
- ✅ Comprehensive test suite

### Where We're Going

Weeks 3-4 focus on:
1. **Component System** - Extensible calculations (Arabic parts, midpoints)
2. **Integration** - Connect new architecture to visualization
3. **Advanced Features** - Synastry, transits, patterns
4. **Plugin Foundation** - Groundwork for future extensions

### Why This Order?

```
Week 3: Integration & Components
├─ Arabic Parts/Midpoints → Prove component pattern works
├─ Visualization → Validate data model is complete
└─ Presentation → Ensure output is usable

Week 4: Advanced Features
├─ Pattern Detection → Add analysis capabilities
├─ Synastry → Multi-chart calculations
├─ Transits → Time-based features
└─ Plugin Foundation → Enable future growth
```

**Key Principle**: Each feature validates and strengthens the architecture.

---

# Week 3: Components & Integration

## Day 11: Arabic Parts Component

### Why Start With Arabic Parts?

Arabic Parts are perfect for testing the component system because:
1. They **depend on existing calculations** (need Sun, Moon, ASC)
2. They're **optional additions** (not core like planets)
3. They have **interesting logic** (sect-dependent formulas)
4. They **prove the architecture** works for extensions

### Step 11.1: Design the Component Interface

**File**: `src/stellium/components/__init__.py`

```python
"""
Component system for optional chart calculations.

Components calculate additional objects based on:
- Chart datetime/location
- Already-calculated planetary positions
- House cusps

They return CelestialPosition objects that integrate seamlessly
with the rest of the chart.
"""

from stellium.core.protocols import ChartComponent

__all__ = ['ChartComponent']
```

**Why this design?**
- Components receive **complete context** (datetime, location, positions, houses)
- They return **standard CelestialPosition** objects (no special types needed)
- They're **composable** (can chain multiple components)

### Step 11.2: Create Arabic Parts Component

**File**: `src/stellium/components/arabic_parts.py`

```python
"""
Arabic Parts calculator component.

Arabic Parts (also called Lots) are calculated points based on
the distances between three chart objects. They represent themes
or areas of life.

Formula: Lot = Asc + Point2 - Point1

Many lots are "sect-aware" - they flip the formula for day vs night charts:
- Day Chart: Asc + Point2 - Point1
- Night Chart: Asc + Point1 - Point2
"""

from typing import List, Optional, Dict
from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    CelestialPosition,
    HouseCusps,
    ObjectType,
)


# Arabic Parts catalog
# Each entry defines: which points to use, whether to flip for sect
ARABIC_PARTS_CATALOG = {
    "Part of Fortune": {
        "points": ["ASC", "Moon", "Sun"],
        "sect_flip": True,
        "description": "Material wellbeing, body, health",
    },
    "Part of Spirit": {
        "points": ["ASC", "Sun", "Moon"],
        "sect_flip": True,
        "description": "Spiritual purpose, inner life",
    },
    "Part of Love": {
        "points": ["ASC", "Venus", "Sun"],
        "sect_flip": False,
        "description": "Romantic love, desire",
    },
    "Part of Marriage": {
        "points": ["ASC", "Venus", "Jupiter"],
        "sect_flip": False,
        "description": "Partnership, committed relationships",
    },
    "Part of Eros": {
        "points": ["ASC", "Venus", "Mars"],
        "sect_flip": False,
        "description": "Passion, sexual attraction",
    },
    "Part of Children": {
        "points": ["ASC", "Jupiter", "Moon"],
        "sect_flip": False,
        "description": "Fertility, relationship with children",
    },
    "Part of Father": {
        "points": ["ASC", "Sun", "Saturn"],
        "sect_flip": False,
        "description": "Relationship with father figure",
    },
    "Part of Mother": {
        "points": ["ASC", "Venus", "Moon"],
        "sect_flip": False,
        "description": "Relationship with mother figure",
    },
    "Part of Profession": {
        "points": ["ASC", "MC", "Sun"],
        "sect_flip": False,
        "description": "Career, vocation, public standing",
    },
    "Part of Death": {
        "points": ["ASC", "Saturn", "Moon"],
        "sect_flip": False,
        "description": "Transformation, endings, legacy",
    },
}


class ArabicPartsCalculator:
    """
    Calculate Arabic Parts (Lots) for a chart.

    Arabic Parts are sensitive points calculated from the distances
    between three chart objects. They represent specific life themes.
    """

    def __init__(
        self,
        parts_to_calculate: Optional[List[str]] = None,
        custom_parts: Optional[Dict] = None,
    ):
        """
        Initialize Arabic Parts calculator.

        Args:
            parts_to_calculate: Which parts to calculate (None = all)
            custom_parts: Additional custom part definitions
        """
        self._catalog = ARABIC_PARTS_CATALOG.copy()
        if custom_parts:
            self._catalog.update(custom_parts)

        self._parts_to_calculate = parts_to_calculate

    @property
    def component_name(self) -> str:
        return "Arabic Parts"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: List[CelestialPosition],
        houses: HouseCusps,
    ) -> List[CelestialPosition]:
        """
        Calculate Arabic Parts.

        Args:
            datetime: Chart datetime (unused but required by protocol)
            location: Chart location (unused but required by protocol)
            positions: Already calculated positions
            houses: House cusps

        Returns:
            List of CelestialPosition objects for each part
        """
        # Build position lookup
        pos_dict = {p.name: p for p in positions}

        # Determine chart sect (day or night)
        sect = self._determine_sect(pos_dict)

        # Calculate each part
        parts = []
        catalog_to_use = (
            {k: v for k, v in self._catalog.items() if k in self._parts_to_calculate}
            if self._parts_to_calculate
            else self._catalog
        )

        for part_name, part_config in catalog_to_use.items():
            try:
                part_position = self._calculate_single_part(
                    part_name,
                    part_config,
                    pos_dict,
                    sect,
                    houses,
                )
                parts.append(part_position)
            except KeyError as e:
                # Missing required position
                print(f"Warning: Could not calculate {part_name}: missing {e}")
                continue

        return parts

    def _determine_sect(self, positions: Dict[str, CelestialPosition]) -> str:
        """
        Determine if chart is a day or night chart.

        Day chart = Sun above horizon (between ASC and DSC through MC)
        Night chart = Sun below horizon

        Args:
            positions: Position lookup dictionary

        Returns:
            "Day" or "Night"
        """
        asc = positions['ASC']
        sun = positions['Sun']

        # Calculate descendant
        desc_long = (asc.longitude + 180) % 360

        # Check if Sun is above horizon
        # Above horizon = between ASC and DSC going through MC
        if asc.longitude < desc_long:
            # Normal case: ASC at 0°, DSC at 180°
            is_day = asc.longitude <= sun.longitude < desc_long
        else:
            # Wrapped case: ASC at 270°, DSC at 90°
            is_day = sun.longitude >= desc_long or sun.longitude < asc.longitude

        return "Day" if is_day else "Night"

    def _calculate_single_part(
        self,
        part_name: str,
        part_config: Dict,
        positions: Dict[str, CelestialPosition],
        sect: str,
        houses: HouseCusps,
    ) -> CelestialPosition:
        """
        Calculate a single Arabic Part.

        Args:
            part_name: Name of the part
            part_config: Configuration (points, sect_flip)
            positions: Position lookup
            sect: Chart sect ("Day" or "Night")
            houses: House cusps for house assignment

        Returns:
            CelestialPosition for the calculated part
        """
        point_names = part_config["points"]
        sect_flip = part_config["sect_flip"]

        # Get the three points
        asc = positions[point_names[0]]
        point2 = positions[point_names[1]]
        point3 = positions[point_names[2]]

        # Calculate longitude based on formula and sect
        if sect == "Day" or not sect_flip:
            # Day formula: ASC + Point2 - Point3
            longitude = (asc.longitude + point2.longitude - point3.longitude) % 360
        else:
            # Night formula (flipped): ASC + Point3 - Point2
            longitude = (asc.longitude + point3.longitude - point2.longitude) % 360

        # Determine which house it falls in
        house = self._find_house(longitude, houses.cusps)

        # Create CelestialPosition for this part
        return CelestialPosition(
            name=part_name,
            object_type=ObjectType.ARABIC_PART,
            longitude=longitude,
            house=house,
        )

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


class PartOfFortuneCalculator:
    """
    Simplified calculator for just Part of Fortune.

    This is useful when you only need Fortune and don't want
    to calculate all Arabic Parts.
    """

    @property
    def component_name(self) -> str:
        return "Part of Fortune"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: List[CelestialPosition],
        houses: HouseCusps,
    ) -> List[CelestialPosition]:
        """Calculate only Part of Fortune."""
        calculator = ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"])
        return calculator.calculate(datetime, location, positions, houses)
```

**Why this design?**

1. **Flexible Catalog**: Easy to add new parts without changing code
2. **Sect Awareness**: Automatic day/night chart handling
3. **House Integration**: Parts get house assignments automatically
4. **Selective Calculation**: Can calculate just some parts for performance
5. **Custom Parts**: Users can define their own parts

### Step 11.3: Integrate with ChartBuilder

**Update**: `src/stellium/core/builder.py`

Add to the `calculate()` method:

```python
# In ChartBuilder.calculate() method, after Step 4:

# Step 5: Run additional components (Arabic parts, midpoints, etc.)
for component in self._components:
    additional = component.calculate(
        self._datetime,
        self._location,
        positions,
        houses,
    )
    positions.extend(additional)
```

**Why this integration?**
- Components run **after** core calculations (they need positions)
- They **extend** the positions list (seamless integration)
- Order matters (later components can use earlier results)

### Step 11.4: Test Arabic Parts

**File**: `tests/test_arabic_parts.py`

```python
"""Test Arabic Parts calculation."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.components.arabic_parts import ArabicPartsCalculator, ARABIC_PARTS_CATALOG


def test_part_of_fortune_day_chart():
    """Test Part of Fortune calculation for day chart."""
    # Day chart: Sun above horizon
    dt = datetime(2000, 6, 21, 12, 0, tzinfo=pytz.UTC)  # Summer, noon
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"])) \
        .calculate()

    # Should have Part of Fortune
    fortune = chart.get_object("Part of Fortune")
    assert fortune is not None
    assert fortune.object_type == ObjectType.ARABIC_PART
    assert 0 <= fortune.longitude < 360
    assert fortune.house is not None


def test_part_of_fortune_night_chart():
    """Test Part of Fortune calculation for night chart."""
    # Night chart: Sun below horizon
    dt = datetime(2000, 6, 21, 0, 0, tzinfo=pytz.UTC)  # Midnight
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"])) \
        .calculate()

    fortune = chart.get_object("Part of Fortune")
    assert fortune is not None

    # Night formula is reversed from day formula
    # Can't check exact value without knowing positions,
    # but can verify it was calculated
    assert fortune.sign is not None


def test_all_arabic_parts():
    """Test calculation of all Arabic Parts."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=40.7128, longitude=-74.0060)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator()) \
        .calculate()

    # Check that parts were calculated
    arabic_parts = [p for p in chart.positions if p.object_type == ObjectType.ARABIC_PART]

    # Should have calculated multiple parts
    assert len(arabic_parts) > 0

    # Check a few specific ones
    assert chart.get_object("Part of Fortune") is not None
    assert chart.get_object("Part of Spirit") is not None
    assert chart.get_object("Part of Love") is not None

    # All should have house assignments
    for part in arabic_parts:
        assert part.house is not None
        assert 1 <= part.house <= 12


def test_custom_arabic_part():
    """Test defining a custom Arabic Part."""
    custom_parts = {
        "Part of Cats": {
            "points": ["ASC", "Moon", "Venus"],
            "sect_flip": False,
            "description": "Relationship with feline companions",
        }
    }

    calculator = ArabicPartsCalculator(custom_parts=custom_parts)
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(calculator) \
        .calculate()

    # Should have our custom part
    cat_part = chart.get_object("Part of Cats")
    assert cat_part is not None
    assert cat_part.object_type == ObjectType.ARABIC_PART


def test_arabic_parts_in_json_export():
    """Test that Arabic Parts appear in JSON export."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator()) \
        .calculate()

    data = chart.to_dict()

    # Find Arabic Parts in positions
    arabic_parts = [
        p for p in data['positions']
        if p['type'] == 'arabic_part'
    ]

    assert len(arabic_parts) > 0

    # Check structure
    for part in arabic_parts:
        assert 'name' in part
        assert 'longitude' in part
        assert 'sign' in part
        assert 'house' in part


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Why these tests?**

1. **Day/Night Sect**: Verify formula flipping works
2. **All Parts**: Test complete catalog
3. **Custom Parts**: Prove extensibility
4. **JSON Export**: Validate integration with serialization
5. **House Assignment**: Ensure complete integration

---

## Day 12: Midpoints Component

### Why Midpoints?

Midpoints test different aspects of the component system:
1. They calculate **relationships between objects** (not formulas like Arabic Parts)
2. They create **multiple objects** (many midpoint pairs)
3. They're **optional** (not everyone uses midpoints)
4. They prove components can **work together** (aspects to midpoints)

### Step 12.1: Create Midpoints Component

**File**: `src/stellium/components/midpoints.py`

```python
"""
Midpoint calculator component.

Midpoints are the halfway point between two celestial objects.
They represent the synthesis or blend of two planetary energies.

In midpoint astrology:
- Direct midpoint: Shortest arc between two points
- Indirect midpoint: Opposite point (180° from direct)

Both are significant, but direct midpoint is more commonly used.
"""

from typing import List, Optional, Set, Tuple
from stellium.core.models import (
    ChartDateTime,
    ChartLocation,
    CelestialPosition,
    HouseCusps,
    ObjectType,
)


class MidpointCalculator:
    """
    Calculate midpoints between celestial objects.

    Midpoints reveal how two planetary energies blend or interact.
    They're used extensively in Uranian astrology and some modern approaches.
    """

    # Common midpoint pairs used in traditional interpretation
    DEFAULT_PAIRS = [
        ("Sun", "Moon"),  # Conscious/unconscious integration
        ("ASC", "MC"),  # Personal identity/public role synthesis
        ("Venus", "Mars"),  # Desire/action blend
        ("Mercury", "Uranus"),  # Communication/innovation
        ("Jupiter", "Saturn"),  # Expansion/contraction balance
        ("Moon", "Venus"),  # Emotional/relational needs
        ("Moon", "Mars"),  # Emotional/assertive drives
        ("Sun", "Mercury"),  # Identity/communication
        ("Sun", "Venus"),  # Identity/values
        ("Moon", "Mercury"),  # Emotion/thought
    ]

    def __init__(
        self,
        pairs: Optional[List[Tuple[str, str]]] = None,
        calculate_all: bool = False,
        include_indirect: bool = False,
    ):
        """
        Initialize midpoint calculator.

        Args:
            pairs: Specific pairs to calculate (None = use defaults)
            calculate_all: Calculate all planet pairs (overrides pairs)
            include_indirect: Also calculate indirect midpoints (180° opposite)
        """
        self._pairs = pairs or self.DEFAULT_PAIRS
        self._calculate_all = calculate_all
        self._include_indirect = include_indirect

    @property
    def component_name(self) -> str:
        return "Midpoints"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: List[CelestialPosition],
        houses: HouseCusps,
    ) -> List[CelestialPosition]:
        """
        Calculate midpoints.

        Args:
            datetime: Chart datetime (unused)
            location: Chart location (unused)
            positions: Already calculated positions
            houses: House cusps for house assignment

        Returns:
            List of CelestialPosition objects for midpoints
        """
        # Build position lookup
        pos_dict = {p.name: p for p in positions}

        # Determine which pairs to calculate
        if self._calculate_all:
            # All planet-to-planet pairs
            planets = [p for p in positions if p.object_type == ObjectType.PLANET]
            pairs = [
                (p1.name, p2.name)
                for i, p1 in enumerate(planets)
                for p2 in planets[i + 1:]
            ]
        else:
            pairs = self._pairs

        midpoints = []

        for obj1_name, obj2_name in pairs:
            if obj1_name not in pos_dict or obj2_name not in pos_dict:
                continue

            obj1 = pos_dict[obj1_name]
            obj2 = pos_dict[obj2_name]

            # Calculate direct midpoint
            direct_mid = self._calculate_direct_midpoint(obj1, obj2, houses)
            midpoints.append(direct_mid)

            # Calculate indirect midpoint if requested
            if self._include_indirect:
                indirect_mid = self._calculate_indirect_midpoint(obj1, obj2, houses)
                midpoints.append(indirect_mid)

        return midpoints

    def _calculate_direct_midpoint(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        houses: HouseCusps,
    ) -> CelestialPosition:
        """
        Calculate direct midpoint (shortest arc).

        Args:
            obj1: First object
            obj2: Second object
            houses: House cusps

        Returns:
            CelestialPosition for the midpoint
        """
        # Calculate shortest arc midpoint
        long1, long2 = obj1.longitude, obj2.longitude

        # Calculate angular distance
        diff = abs(long2 - long1)

        if diff <= 180:
            # Direct arc
            midpoint_long = (long1 + long2) / 2
        else:
            # Shorter arc goes the other way
            midpoint_long = ((long1 + long2) / 2 + 180) % 360

        # Find house
        house = self._find_house(midpoint_long, houses.cusps)

        # Create position
        return CelestialPosition(
            name=f"{obj1.name}/{obj2.name}",
            object_type=ObjectType.MIDPOINT,
            longitude=midpoint_long,
            house=house,
        )

    def _calculate_indirect_midpoint(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        houses: HouseCusps,
    ) -> CelestialPosition:
        """
        Calculate indirect midpoint (opposite of direct).

        Args:
            obj1: First object
            obj2: Second object
            houses: House cusps

        Returns:
            CelestialPosition for the indirect midpoint
        """
        # Get direct midpoint
        direct = self._calculate_direct_midpoint(obj1, obj2, houses)

        # Indirect is 180° opposite
        indirect_long = (direct.longitude + 180) % 360

        # Find house
        house = self._find_house(indirect_long, houses.cusps)

        return CelestialPosition(
            name=f"{obj1.name}/{obj2.name} (indirect)",
            object_type=ObjectType.MIDPOINT,
            longitude=indirect_long,
            house=house,
        )

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Find which house a longitude falls in."""
        cusp_list = list(cusps)

        for i in range(12):
            cusp1 = cusp_list[i]
            cusp2 = cusp_list[(i + 1) % 12]

            if cusp2 < cusp1:
                cusp2 += 360
                test_long = longitude if longitude >= cusp1 else longitude + 360
            else:
                test_long = longitude

            if cusp1 <= test_long < cusp2:
                return i + 1

        return 1
```

**Why this design?**

1. **Flexible Pairs**: Default common pairs, but can specify any
2. **All Pairs Option**: For research or comprehensive analysis
3. **Indirect Midpoints**: Optional advanced feature
4. **Clear Naming**: Names like "Sun/Moon" are self-explanatory
5. **Standard Integration**: Returns CelestialPosition objects

### Step 12.2: Test Midpoints

**File**: `tests/test_midpoints.py`

```python
"""Test midpoint calculations."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, CelestialPosition, ObjectType
from stellium.components.midpoints import MidpointCalculator


def test_basic_midpoint_calculation():
    """Test basic midpoint calculation."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(MidpointCalculator(pairs=[("Sun", "Moon")])) \
        .calculate()

    # Should have Sun/Moon midpoint
    midpoint = chart.get_object("Sun/Moon")
    assert midpoint is not None
    assert midpoint.object_type == ObjectType.MIDPOINT
    assert 0 <= midpoint.longitude < 360


def test_default_midpoints():
    """Test calculation of default midpoint pairs."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=40, longitude=-74)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(MidpointCalculator()) \
        .calculate()

    # Should have default midpoints
    midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

    assert len(midpoints) > 0

    # Check some common ones
    assert chart.get_object("Sun/Moon") is not None
    assert chart.get_object("ASC/MC") is not None
    assert chart.get_object("Venus/Mars") is not None


def test_all_midpoints():
    """Test calculating all possible midpoint pairs."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(MidpointCalculator(calculate_all=True)) \
        .calculate()

    midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

    # Should have many midpoints (all planet pairs)
    # 12 planets = 12*11/2 = 66 pairs
    assert len(midpoints) > 40  # At least many pairs


def test_indirect_midpoints():
    """Test indirect midpoint calculation."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0)

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(
            MidpointCalculator(
                pairs=[("Sun", "Moon")],
                include_indirect=True
            )
        ) \
        .calculate()

    # Should have both direct and indirect
    direct = chart.get_object("Sun/Moon")
    indirect = chart.get_object("Sun/Moon (indirect)")

    assert direct is not None
    assert indirect is not None

    # Indirect should be 180° from direct
    expected_indirect = (direct.longitude + 180) % 360
    assert abs(indirect.longitude - expected_indirect) < 0.01


def test_midpoint_shortest_arc():
    """Test that midpoint uses shortest arc."""
    # Create mock positions with known longitudes
    from stellium.core.models import HouseCusps

    houses = HouseCusps(
        system="Equal",
        cusps=tuple(i * 30 for i in range(12))
    )

    calculator = MidpointCalculator()

    # Test case 1: Simple case (0° and 60°)
    obj1 = CelestialPosition(
        name="Test1",
        object_type=ObjectType.PLANET,
        longitude=0.0,
    )
    obj2 = CelestialPosition(
        name="Test2",
        object_type=ObjectType.PLANET,
        longitude=60.0,
    )

    midpoint = calculator._calculate_direct_midpoint(obj1, obj2, houses)
    assert abs(midpoint.longitude - 30.0) < 0.01  # 30° is midpoint

    # Test case 2: Across 0° (350° and 10°)
    obj1 = CelestialPosition(
        name="Test1",
        object_type=ObjectType.PLANET,
        longitude=350.0,
    )
    obj2 = CelestialPosition(
        name="Test2",
        object_type=ObjectType.PLANET,
        longitude=10.0,
    )

    midpoint = calculator._calculate_direct_midpoint(obj1, obj2, houses)
    # Shortest arc is 350→360→0→10, midpoint at 0°
    assert abs(midpoint.longitude - 0.0) < 0.01 or abs(midpoint.longitude - 360.0) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Why these tests?**

1. **Basic Functionality**: Single midpoint calculation
2. **Default Pairs**: Test common use case
3. **All Pairs**: Test comprehensive calculation
4. **Indirect Midpoints**: Test optional feature
5. **Shortest Arc**: Verify correct formula (important edge case)

---

## Day 13: Visualization Integration

### Why Visualization Now?

We need to update `drawing.py` to work with the new data model:
1. **Validate** that our data model is complete
2. **Prove** that existing features still work
3. **Discover** any missing pieces in the architecture

### Step 13.1: Create Drawing Adapter

Instead of rewriting drawing.py entirely, create an adapter that converts between old and new formats.

**File**: `src/stellium/adapters/drawing_adapter.py`

```python
"""
Adapter to connect new chart architecture with existing drawing code.

This provides a bridge between:
- New: CalculatedChart (immutable, protocol-based)
- Old: drawing.py expectations

This is a temporary adapter. Eventually, drawing.py will be
updated to use the new models directly.
"""

from typing import List, Dict, Any
from stellium.core.models import CalculatedChart, CelestialPosition, ObjectType


class LegacyChartAdapter:
    """
    Adapt CalculatedChart to format expected by drawing.py.

    This creates a "fake" old-style chart object that drawing.py can use.
    """

    def __init__(self, chart: CalculatedChart):
        """
        Initialize adapter.

        Args:
            chart: CalculatedChart to adapt
        """
        self._chart = chart

        # Create properties that drawing.py expects
        self.planets = self._create_planet_list()
        self.angles = self._create_angle_list()
        self.cusps = list(chart.houses.cusps)
        self.objects_dict = {p.name: p for p in chart.positions}
        self.house_system = chart.houses.system

        # Date/time info
        self.datetime_utc = chart.datetime.utc_datetime
        self.julian = chart.datetime.julian_day
        self.loc = (chart.location.latitude, chart.location.longitude)
        self.loc_name = chart.location.name

    def _create_planet_list(self) -> List:
        """Create list of planet-like objects for drawing."""
        planets = []

        for pos in self._chart.positions:
            if pos.object_type in (ObjectType.PLANET, ObjectType.ASTEROID):
                # Create object with properties drawing.py expects
                planet_obj = self._create_drawable_object(pos)
                planets.append(planet_obj)

        return planets

    def _create_angle_list(self) -> List:
        """Create list of angle objects for drawing."""
        angles = []

        for pos in self._chart.positions:
            if pos.object_type == ObjectType.ANGLE:
                angle_obj = self._create_drawable_object(pos)
                angles.append(angle_obj)

        return angles

    def _create_drawable_object(self, position: CelestialPosition):
        """
        Create an object that drawing.py can use.

        Drawing.py expects objects with specific attributes.
        We create a simple namespace object with those attributes.
        """
        from types import SimpleNamespace

        obj = SimpleNamespace()
        obj.name = position.name
        obj.long = position.longitude
        obj.lat = position.latitude
        obj.speed_long = position.speed_longitude
        obj.sign = position.sign
        obj.sign_deg = position.sign_degree
        obj.house = position.house
        obj.is_retro = position.is_retrograde

        # For compatibility with old Swiss Ephemeris IDs
        obj.swe = self._get_swe_id(position.name)

        return obj

    def _get_swe_id(self, name: str) -> int:
        """Get Swiss Ephemeris ID for a celestial object."""
        swe_ids = {
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
            'True Node': 11,
            'South Node': -1,
            'Chiron': 15,
            'Pholus': 16,
            'Ceres': 17,
            'Pallas': 18,
            'Juno': 19,
            'Vesta': 20,
        }
        return swe_ids.get(name, -99)

    def get_all_aspects(self) -> List[Dict[str, Any]]:
        """
        Convert aspects to format expected by drawing.py.

        Returns:
            List of aspect dictionaries
        """
        aspects = []

        for aspect in self._chart.aspects:
            aspects.append({
                'planet1': self._find_drawable_object(aspect.object1.name),
                'planet2': self._find_drawable_object(aspect.object2.name),
                'aspect_name': aspect.aspect_name,
                'orb': aspect.orb,
                'distance': abs(aspect.object1.longitude - aspect.object2.longitude),
                'movement': 'Applying' if aspect.is_applying else 'Separating' if aspect.is_applying is not None else None,
            })

        return aspects

    def _find_drawable_object(self, name: str):
        """Find drawable object by name."""
        # Check planets first
        for planet in self.planets:
            if planet.name == name:
                return planet

        # Then angles
        for angle in self.angles:
            if angle.name == name:
                return angle

        # Fallback: create on the fly
        pos = self._chart.get_object(name)
        if pos:
            return self._create_drawable_object(pos)

        return None
```

**Why an adapter?**

1. **Don't break existing code**: drawing.py keeps working
2. **Gradual migration**: Can update drawing.py later
3. **Validates data model**: If adapter works, our model is complete
4. **Temporary solution**: Clear that this will be replaced

### Step 13.2: Create Drawing Helper Function

**File**: `src/stellium/visualization.py`

```python
"""
High-level visualization API.

This provides a clean interface for chart visualization,
hiding the adapter complexity.
"""

from stellium.core.models import CalculatedChart
from stellium.adapters.drawing_adapter import LegacyChartAdapter
from stellium.drawing import draw_chart as legacy_draw_chart


def draw_chart(chart: CalculatedChart, filename: str, size: int = 600) -> str:
    """
    Draw a chart using the new architecture.

    Args:
        chart: CalculatedChart to visualize
        filename: Output SVG filename
        size: Chart size in pixels

    Returns:
        Path to created SVG file
    """
    # Adapt to legacy format
    adapted_chart = LegacyChartAdapter(chart)

    # Use existing drawing code
    return legacy_draw_chart(adapted_chart, filename, size)
```

**Why this helper?**

- **Clean API**: Users don't see the adapter
- **Future-proof**: When we update drawing.py, this function stays the same
- **Simple**: One function to draw any chart

### Step 13.3: Test Visualization

**File**: `tests/test_visualization.py`

```python
"""Test chart visualization with new architecture."""

import pytest
import os
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.visualization import draw_chart
from stellium.engines.aspects import ModernAspectEngine


def test_basic_chart_drawing():
    """Test that we can draw a chart with new architecture."""
    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=37.7749,
        longitude=-122.4194,
        name="San Francisco, CA"
    )

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    # Draw the chart
    output_file = "tests/output/test_new_architecture_chart.svg"
    os.makedirs("tests/output", exist_ok=True)

    result = draw_chart(chart, output_file, size=600)

    # Verify file was created
    assert os.path.exists(result)
    assert os.path.getsize(result) > 1000  # Should be substantial SVG


def test_chart_with_components():
    """Test drawing chart with Arabic parts and midpoints."""
    from stellium.components.arabic_parts import ArabicPartsCalculator
    from stellium.components.midpoints import MidpointCalculator

    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=40, longitude=-74, name="New York")

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator()) \
        .add_component(MidpointCalculator()) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    output_file = "tests/output/test_with_components_chart.svg"
    result = draw_chart(chart, output_file)

    assert os.path.exists(result)


def test_different_house_systems_visualize():
    """Test that different house systems both visualize."""
    from stellium.engines.houses import PlacidusHouses, WholeSignHouses

    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=51.5074, longitude=-0.1278, name="London")

    placidus_chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .calculate()

    whole_sign_chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()) \
        .calculate()

    # Draw both
    draw_chart(placidus_chart, "tests/output/placidus_test.svg")
    draw_chart(whole_sign_chart, "tests/output/whole_sign_test.svg")

    # Both should exist
    assert os.path.exists("tests/output/placidus_test.svg")
    assert os.path.exists("tests/output/whole_sign_test.svg")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:
```bash
source ~/.zshrc && pyenv activate stellium && python -m pytest tests/test_visualization.py -v
```

---

## Day 14: Presentation Layer Update

### Why Update Presentation?

The `presentation.py` module creates text tables. We need to update it to work with new data models while improving the output format.

### Step 14.1: Create Modern Presentation Module

**File**: `src/stellium/presentation/modern.py`

```python
"""
Modern presentation layer for chart data.

Provides clean, formatted output using the new architecture.
Uses Rich library for beautiful terminal output.
"""

from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from stellium.core.models import CalculatedChart, CelestialPosition, Aspect, ObjectType


def print_chart_summary(chart: CalculatedChart, console: Console = None):
    """
    Print a comprehensive chart summary.

    Args:
        chart: Chart to display
        console: Rich console (creates one if None)
    """
    if console is None:
        console = Console()

    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Astrological Chart[/bold cyan]\n"
        f"{chart.datetime.utc_datetime.strftime('%B %d, %Y at %H:%M UTC')}\n"
        f"{chart.location.name or f'{chart.location.latitude}°, {chart.location.longitude}°'}\n"
        f"House System: {chart.houses.system}",
        border_style="cyan"
    ))

    # Planetary positions
    console.print(create_positions_table(chart))
    console.print()

    # Aspects
    if chart.aspects:
        console.print(create_aspects_table(chart))
        console.print()

    # Arabic Parts (if any)
    arabic_parts = [p for p in chart.positions if p.object_type == ObjectType.ARABIC_PART]
    if arabic_parts:
        console.print(create_arabic_parts_table(arabic_parts))
        console.print()


def create_positions_table(chart: CalculatedChart) -> Table:
    """
    Create a table of planetary positions.

    Args:
        chart: Chart with positions

    Returns:
        Rich Table
    """
    table = Table(title="Planetary Positions", show_header=True)

    table.add_column("Planet", style="bold cyan")
    table.add_column("Sign", style="yellow")
    table.add_column("Position", justify="right")
    table.add_column("House", justify="center")
    table.add_column("Retro", justify="center")

    # Get planets (excluding angles and other types)
    planets = [
        p for p in chart.positions
        if p.object_type in (ObjectType.PLANET, ObjectType.ASTEROID)
    ]

    # Sort by traditional order
    planet_order = [
        'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
        'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
        'True Node', 'South Node', 'Chiron'
    ]

    def sort_key(pos):
        try:
            return planet_order.index(pos.name)
        except ValueError:
            return 999

    planets.sort(key=sort_key)

    for planet in planets:
        # Format position
        degrees = int(planet.sign_degree)
        minutes = int((planet.sign_degree % 1) * 60)
        position = f"{degrees}°{minutes:02d}'"

        # Retrograde indicator
        retro = "℞" if planet.is_retrograde else ""

        # Color for retrograde
        retro_style = "red" if planet.is_retrograde else "white"

        table.add_row(
            planet.name,
            planet.sign,
            position,
            str(planet.house) if planet.house else "—",
            f"[{retro_style}]{retro}[/{retro_style}]"
        )

    return table


def create_aspects_table(chart: CalculatedChart, max_orb: float = None) -> Table:
    """
    Create a table of aspects.

    Args:
        chart: Chart with aspects
        max_orb: Optional maximum orb to display

    Returns:
        Rich Table
    """
    table = Table(title="Aspects", show_header=True)

    table.add_column("Planet 1", style="cyan")
    table.add_column("Aspect", justify="center")
    table.add_column("Planet 2", style="cyan")
    table.add_column("Orb", justify="right")
    table.add_column("Type", justify="center")

    # Aspect colors
    aspect_colors = {
        'Conjunction': 'white',
        'Sextile': 'green',
        'Square': 'red',
        'Trine': 'blue',
        'Opposition': 'red',
    }

    # Filter and sort aspects
    aspects = chart.aspects
    if max_orb:
        aspects = [a for a in aspects if a.orb <= max_orb]

    # Sort by orb (tightest first)
    aspects = sorted(aspects, key=lambda a: a.orb)

    for aspect in aspects:
        color = aspect_colors.get(aspect.aspect_name, 'white')

        # Applying/separating
        movement = ""
        if aspect.is_applying is True:
            movement = "→"
        elif aspect.is_applying is False:
            movement = "←"

        table.add_row(
            aspect.object1.name,
            f"[{color}]{aspect.aspect_name}[/{color}]",
            aspect.object2.name,
            f"{aspect.orb:.1f}°",
            movement
        )

    return table


def create_arabic_parts_table(parts: List[CelestialPosition]) -> Table:
    """
    Create a table of Arabic Parts.

    Args:
        parts: List of Arabic Part positions

    Returns:
        Rich Table
    """
    table = Table(title="Arabic Parts", show_header=True)

    table.add_column("Part", style="bold magenta")
    table.add_column("Sign", style="yellow")
    table.add_column("Position", justify="right")
    table.add_column("House", justify="center")

    for part in parts:
        degrees = int(part.sign_degree)
        minutes = int((part.sign_degree % 1) * 60)
        position = f"{degrees}°{minutes:02d}'"

        table.add_row(
            part.name,
            part.sign,
            position,
            str(part.house) if part.house else "—"
        )

    return table


def create_houses_table(chart: CalculatedChart) -> Table:
    """
    Create a table of house cusps.

    Args:
        chart: Chart with house data

    Returns:
        Rich Table
    """
    table = Table(title=f"House Cusps ({chart.houses.system})", show_header=True)

    table.add_column("House", justify="center", style="bold")
    table.add_column("Sign", style="yellow")
    table.add_column("Cusp", justify="right")

    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    for i, cusp in enumerate(chart.houses.cusps):
        house_num = i + 1
        sign = signs[int(cusp // 30)]
        degrees = int(cusp % 30)
        minutes = int(((cusp % 30) % 1) * 60)

        table.add_row(
            str(house_num),
            sign,
            f"{degrees}°{minutes:02d}'"
        )

    return table


def print_aspect_summary(chart: CalculatedChart, tight_orb: float = 3.0):
    """
    Print aspect summary with tight/wide separation.

    Args:
        chart: Chart with aspects
        tight_orb: Orb threshold for "tight" aspects
    """
    console = Console()

    tight_aspects = [a for a in chart.aspects if a.orb <= tight_orb]
    wide_aspects = [a for a in chart.aspects if a.orb > tight_orb]

    console.print(f"\n[bold]Aspect Summary[/bold]")
    console.print(f"Total: {len(chart.aspects)} aspects")
    console.print(f"Tight (≤{tight_orb}°): {len(tight_aspects)}")
    console.print(f"Wide (>{tight_orb}°): {len(wide_aspects)}")

    if tight_aspects:
        console.print(f"\n[bold cyan]Tight Aspects[/bold cyan]")
        for aspect in sorted(tight_aspects, key=lambda a: a.orb):
            console.print(
                f"  {aspect.object1.name} {aspect.aspect_name} "
                f"{aspect.object2.name} (orb: {aspect.orb:.1f}°)"
            )
```

**Why this design?**

1. **Rich Tables**: Beautiful terminal output
2. **Modular Functions**: Each creates one table
3. **Flexible**: Can combine tables as needed
4. **Modern**: Uses new data models directly
5. **Colorful**: Visual distinction for different elements

### Step 14.2: Create Simple Text Format

For cases where Rich isn't available:

**File**: `src/stellium/presentation/simple.py`

```python
"""
Simple text presentation (no Rich dependency).

For environments where Rich isn't available or desired.
"""

from stellium.core.models import CalculatedChart, ObjectType


def format_chart_text(chart: CalculatedChart) -> str:
    """
    Format chart as plain text.

    Args:
        chart: Chart to format

    Returns:
        Multi-line string
    """
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append(f"ASTROLOGICAL CHART")
    lines.append(f"{chart.datetime.utc_datetime.strftime('%B %d, %Y at %H:%M UTC')}")
    lines.append(f"Location: {chart.location.name or f'{chart.location.latitude}, {chart.location.longitude}'}")
    lines.append(f"House System: {chart.houses.system}")
    lines.append("=" * 70)
    lines.append("")

    # Planets
    lines.append("PLANETARY POSITIONS")
    lines.append("-" * 70)
    lines.append(f"{'Planet':<15} {'Sign':<12} {'Position':<12} {'House':<8} {'Retro'}")
    lines.append("-" * 70)

    planets = [p for p in chart.positions if p.object_type in (ObjectType.PLANET, ObjectType.ASTEROID)]
    for planet in planets:
        degrees = int(planet.sign_degree)
        minutes = int((planet.sign_degree % 1) * 60)
        position = f"{degrees}°{minutes:02d}'"
        retro = "℞" if planet.is_retrograde else ""

        lines.append(
            f"{planet.name:<15} {planet.sign:<12} {position:<12} "
            f"{str(planet.house) if planet.house else '—':<8} {retro}"
        )

    lines.append("")

    # Aspects
    if chart.aspects:
        lines.append("ASPECTS")
        lines.append("-" * 70)
        for aspect in sorted(chart.aspects, key=lambda a: a.orb):
            lines.append(
                f"{aspect.object1.name:<12} {aspect.aspect_name:<12} "
                f"{aspect.object2.name:<12} (orb: {aspect.orb:.1f}°)"
            )
        lines.append("")

    # House Cusps
    lines.append("HOUSE CUSPS")
    lines.append("-" * 40)
    for i, cusp in enumerate(chart.houses.cusps):
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign = signs[int(cusp // 30)]
        degrees = int(cusp % 30)
        minutes = int(((cusp % 30) % 1) * 60)

        lines.append(f"House {i+1:2d}: {sign:<12} {degrees:2d}°{minutes:02d}'")

    return "\n".join(lines)
```

---

## Day 15: Example Migration

### Why Migrate Examples?

Examples serve as:
1. **Documentation** for users
2. **Integration tests** (do they still work?)
3. **Showcase** for new features

### Step 15.1: Create Modern Example

**File**: `examples/modern_usage.py`

```python
"""
Modern Stellium usage examples.

Demonstrates the new architecture and its capabilities.
"""

from datetime import datetime
import pytz
from rich.console import Console

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine
from stellium.components.arabic_parts import ArabicPartsCalculator
from stellium.components.midpoints import MidpointCalculator
from stellium.presentation.modern import (
    print_chart_summary,
    create_houses_table,
    print_aspect_summary
)
from stellium.visualization import draw_chart


def example_1_basic_chart():
    """Example 1: Calculate a basic natal chart."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Natal Chart")
    print("="*70)

    # Create a chart for a specific date/time/location
    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=37.7749,
        longitude=-122.4194,
        name="San Francisco, CA"
    )

    chart = ChartBuilder.from_datetime(dt, location).calculate()

    # Display the chart
    console = Console()
    print_chart_summary(chart, console)


def example_2_different_house_systems():
    """Example 2: Compare different house systems."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Different House Systems")
    print("="*70)

    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=51.5074, longitude=-0.1278, name="London, UK")

    console = Console()

    # Placidus
    placidus = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .calculate()

    console.print("\n[bold cyan]Placidus Houses[/bold cyan]")
    console.print(create_houses_table(placidus))

    # Whole Sign
    whole_sign = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()) \
        .calculate()

    console.print("\n[bold cyan]Whole Sign Houses[/bold cyan]")
    console.print(create_houses_table(whole_sign))


def example_3_aspects():
    """Example 3: Calculate aspects."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Aspect Calculation")
    print("="*70)

    dt = datetime(1879, 3, 14, 11, 30, tzinfo=pytz.UTC)
    location = ChartLocation(48.5333, 7.5833, "Ulm, Germany")

    # Calculate with aspects
    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    console = Console()
    print_aspect_summary(chart, tight_orb=3.0)


def example_4_components():
    """Example 4: Use components (Arabic parts, midpoints)."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Components (Arabic Parts & Midpoints)")
    print("="*70)

    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40.7128, -74.0060, "New York, NY")

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator()) \
        .add_component(MidpointCalculator()) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    console = Console()
    print_chart_summary(chart, console)


def example_5_harmonic_aspects():
    """Example 5: Harmonic aspects."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Harmonic Aspects (Septiles)")
    print("="*70)

    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(37.7749, -122.4194, "San Francisco, CA")

    # Calculate with harmonic 7 aspects
    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(HarmonicAspectEngine(harmonic=7, orb=2.0)) \
        .calculate()

    console = Console()
    console.print("\n[bold]Harmonic 7 Aspects (Septiles)[/bold]")

    for aspect in chart.aspects:
        console.print(
            f"  {aspect.object1.name} {aspect.aspect_name} "
            f"{aspect.object2.name} (orb: {aspect.orb:.1f}°)"
        )


def example_6_visualization():
    """Example 6: Create chart visualization."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Chart Visualization")
    print("="*70)

    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(37.7749, -122.4194, "San Francisco, CA")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .add_component(ArabicPartsCalculator()) \
        .calculate()

    # Draw the chart
    output_file = "examples/output/modern_example_chart.svg"
    import os
    os.makedirs("examples/output", exist_ok=True)

    draw_chart(chart, output_file, size=600)

    print(f"\n✅ Chart saved to: {output_file}")


def example_7_json_export():
    """Example 7: Export chart to JSON."""
    print("\n" + "="*70)
    print("EXAMPLE 7: JSON Export")
    print("="*70)

    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(0, 0, "Test Location")

    chart = ChartBuilder.from_datetime(dt, location).calculate()

    # Export to dictionary (can be JSON serialized)
    data = chart.to_dict()

    import json
    print("\n" + json.dumps(data, indent=2, default=str)[:500] + "...")
    print(f"\n✅ Chart data can be serialized to JSON")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_chart()
    example_2_different_house_systems()
    example_3_aspects()
    example_4_components()
    example_5_harmonic_aspects()
    example_6_visualization()
    example_7_json_export()

    print("\n" + "="*70)
    print("✨ All examples complete!")
    print("="*70 + "\n")
```

Run it:
```bash
source ~/.zshrc && pyenv activate stellium && python examples/modern_usage.py
```

---

## End of Week 3 Checkpoint

At this point you should have:

✅ Arabic Parts component working
✅ Midpoints component working
✅ Visualization integrated (adapter pattern)
✅ Modern presentation layer
✅ Comprehensive examples

**Test everything:**
```bash
source ~/.zshrc && pyenv activate stellium && python -m pytest tests/ -v
source ~/.zshrc && pyenv activate stellium && python examples/modern_usage.py
```

---

# Week 4: Advanced Features

## Day 16: Pattern Detection

### Why Pattern Detection?

Aspect patterns reveal deeper chart dynamics:
1. **Grand Trine** - Harmonious flow of energy
2. **T-Square** - Dynamic tension and motivation
3. **Yod** - Finger of God, destiny patterns
4. **Grand Cross** - Major life challenges
5. **Stellium** - Concentrated planetary energy
6. **Kite** - Talent and opportunity

These patterns are **emergent** - they arise from aspects but represent something more than the sum of their parts.

### Step 16.1: Design Pattern Detection System

**File**: `src/stellium/analysis/__init__.py`

```python
"""
Chart analysis components.

Pattern detection, dignity analysis, and other interpretive tools.
"""

from typing import Protocol, List
from stellium.core.models import CalculatedChart


class ChartAnalyzer(Protocol):
    """
    Protocol for chart analysis components.

    Analyzers examine a calculated chart and return findings.
    """

    @property
    def analyzer_name(self) -> str:
        """Name of this analyzer."""
        ...

    def analyze(self, chart: CalculatedChart) -> List:
        """
        Analyze the chart.

        Args:
            chart: Chart to analyze

        Returns:
            List of findings (type depends on analyzer)
        """
        ...
```

### Step 16.2: Create Pattern Detection Models

**File**: `src/stellium/analysis/models.py`

```python
"""
Data models for chart analysis results.
"""

from dataclasses import dataclass
from typing import List
from stellium.core.models import CelestialPosition, Aspect


@dataclass(frozen=True)
class AspectPattern:
    """
    Represents a detected aspect pattern in a chart.

    Examples: Grand Trine, T-Square, Yod, etc.
    """

    pattern_type: str
    planets: List[CelestialPosition]
    aspects: List[Aspect]
    element: str = None  # For elemental patterns (Grand Trine in Fire)
    quality: str = None  # For quality patterns (Cardinal T-Square)
    strength: float = 0.0  # Pattern strength (0-1)

    def __str__(self) -> str:
        """String representation of pattern."""
        planets_str = ", ".join(p.name for p in self.planets)

        if self.element:
            return f"{self.pattern_type} in {self.element} ({planets_str})"
        elif self.quality:
            return f"{self.quality} {self.pattern_type} ({planets_str})"
        else:
            return f"{self.pattern_type} ({planets_str})"


@dataclass(frozen=True)
class Stellium:
    """
    Multiple planets in the same sign or house.
    """

    location_type: str  # "sign" or "house"
    location: str  # Sign name or house number
    planets: List[CelestialPosition]
    orb_span: float  # Degrees from first to last planet

    def __str__(self) -> str:
        planets_str = ", ".join(p.name for p in self.planets)
        return f"Stellium in {self.location} ({planets_str})"
```

### Step 16.3: Implement Pattern Detector

**File**: `src/stellium/analysis/patterns.py`

```python
"""
Aspect pattern detection.

Identifies significant geometric configurations in natal charts.
"""

from typing import List, Set, Tuple
from itertools import combinations

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    Aspect,
    ObjectType,
)
from stellium.analysis.models import AspectPattern, Stellium


class PatternDetector:
    """
    Detect aspect patterns in charts.

    Identifies Grand Trines, T-Squares, Yods, Grand Crosses, and other
    geometric configurations.
    """

    def __init__(self, orb_tolerance: float = 3.0):
        """
        Initialize pattern detector.

        Args:
            orb_tolerance: Additional orb allowed for pattern aspects
        """
        self._orb_tolerance = orb_tolerance

    @property
    def analyzer_name(self) -> str:
        return "Pattern Detector"

    def analyze(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Detect all patterns in chart.

        Args:
            chart: Chart to analyze

        Returns:
            List of detected patterns
        """
        patterns = []

        # Detect each pattern type
        patterns.extend(self._find_grand_trines(chart))
        patterns.extend(self._find_t_squares(chart))
        patterns.extend(self._find_yods(chart))
        patterns.extend(self._find_grand_crosses(chart))
        patterns.extend(self._find_kites(chart))

        return patterns

    def _find_grand_trines(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Find Grand Trines (3 planets in trine, forming triangle).

        Grand Trine = 3 trines forming a closed loop.
        Usually in same element (Fire, Earth, Air, Water).
        """
        patterns = []

        # Get all trine aspects
        trines = [a for a in chart.aspects if a.aspect_name == "Trine"]

        # Get major planets (exclude angles for patterns)
        planets = [
            p for p in chart.positions
            if p.object_type == ObjectType.PLANET
        ]

        # Check each combination of 3 planets
        for p1, p2, p3 in combinations(planets, 3):
            # Check if all three are in trine to each other
            has_12 = self._has_aspect(trines, p1, p2)
            has_23 = self._has_aspect(trines, p2, p3)
            has_31 = self._has_aspect(trines, p3, p1)

            if has_12 and has_23 and has_31:
                # Grand Trine found!
                involved_aspects = [
                    a for a in [has_12, has_23, has_31] if a
                ]

                # Determine element
                element = self._determine_element([p1, p2, p3])

                # Calculate strength (tighter orbs = stronger)
                avg_orb = sum(a.orb for a in involved_aspects) / len(involved_aspects)
                strength = max(0, 1 - (avg_orb / 8.0))  # 8° = max orb

                patterns.append(AspectPattern(
                    pattern_type="Grand Trine",
                    planets=[p1, p2, p3],
                    aspects=involved_aspects,
                    element=element,
                    strength=strength,
                ))

        return patterns

    def _find_t_squares(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Find T-Squares (2 planets in opposition, both square a 3rd planet).

        T-Square = Opposition + 2 squares forming a "T" shape.
        Often in same quality (Cardinal, Fixed, Mutable).
        """
        patterns = []

        oppositions = [a for a in chart.aspects if a.aspect_name == "Opposition"]
        squares = [a for a in chart.aspects if a.aspect_name == "Square"]

        planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]

        # For each opposition
        for opp in oppositions:
            p1 = opp.object1
            p2 = opp.object2

            # Find planets that square both ends of the opposition
            for p3 in planets:
                if p3 in (p1, p2):
                    continue

                square_p1 = self._has_aspect(squares, p3, p1)
                square_p2 = self._has_aspect(squares, p3, p2)

                if square_p1 and square_p2:
                    # T-Square found!
                    involved_aspects = [opp, square_p1, square_p2]

                    # Determine quality
                    quality = self._determine_quality([p1, p2, p3])

                    # Strength
                    avg_orb = sum(a.orb for a in involved_aspects) / 3
                    strength = max(0, 1 - (avg_orb / 8.0))

                    patterns.append(AspectPattern(
                        pattern_type="T-Square",
                        planets=[p1, p2, p3],
                        aspects=involved_aspects,
                        quality=quality,
                        strength=strength,
                    ))

        return patterns

    def _find_yods(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Find Yods (2 planets in sextile, both quincunx a 3rd planet).

        Yod = Sextile + 2 quincunxes forming "Finger of God".
        """
        patterns = []

        sextiles = [a for a in chart.aspects if a.aspect_name == "Sextile"]
        quincunxes = [a for a in chart.aspects if a.aspect_name == "Quincunx"]

        planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]

        # For each sextile
        for sext in sextiles:
            p1 = sext.object1
            p2 = sext.object2

            # Find planets that are quincunx to both
            for p3 in planets:
                if p3 in (p1, p2):
                    continue

                quin_p1 = self._has_aspect(quincunxes, p3, p1)
                quin_p2 = self._has_aspect(quincunxes, p3, p2)

                if quin_p1 and quin_p2:
                    # Yod found!
                    involved_aspects = [sext, quin_p1, quin_p2]

                    avg_orb = sum(a.orb for a in involved_aspects) / 3
                    strength = max(0, 1 - (avg_orb / 6.0))  # Tighter orb for Yods

                    patterns.append(AspectPattern(
                        pattern_type="Yod",
                        planets=[p1, p2, p3],
                        aspects=involved_aspects,
                        strength=strength,
                    ))

        return patterns

    def _find_grand_crosses(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Find Grand Crosses (4 planets, 2 oppositions, 4 squares).

        Grand Cross = 2 oppositions perpendicular to each other.
        Forms a cross/square shape.
        """
        patterns = []

        oppositions = [a for a in chart.aspects if a.aspect_name == "Opposition"]
        squares = [a for a in chart.aspects if a.aspect_name == "Square"]

        # Need at least 2 oppositions
        if len(oppositions) < 2:
            return patterns

        # Check pairs of oppositions
        for opp1, opp2 in combinations(oppositions, 2):
            # Get the 4 planets
            planets_set = {
                opp1.object1, opp1.object2,
                opp2.object1, opp2.object2
            }

            # Must be exactly 4 planets
            if len(planets_set) != 4:
                continue

            planets_list = list(planets_set)

            # Check if all 4 planets are connected by squares
            # Should have 4 square aspects total
            square_count = 0
            involved_squares = []

            for p1, p2 in combinations(planets_list, 2):
                if self._has_aspect([opp1, opp2], p1, p2):
                    continue  # Already counted as opposition

                sq = self._has_aspect(squares, p1, p2)
                if sq:
                    square_count += 1
                    involved_squares.append(sq)

            if square_count == 4:
                # Grand Cross found!
                all_aspects = [opp1, opp2] + involved_squares

                quality = self._determine_quality(planets_list)

                avg_orb = sum(a.orb for a in all_aspects) / len(all_aspects)
                strength = max(0, 1 - (avg_orb / 8.0))

                patterns.append(AspectPattern(
                    pattern_type="Grand Cross",
                    planets=planets_list,
                    aspects=all_aspects,
                    quality=quality,
                    strength=strength,
                ))

        return patterns

    def _find_kites(self, chart: CalculatedChart) -> List[AspectPattern]:
        """
        Find Kites (Grand Trine + opposition from one point).

        Kite = Grand Trine with one planet opposed by a 4th planet
        that sextiles the other two trine points.
        """
        patterns = []

        # First find all grand trines
        grand_trines = self._find_grand_trines(chart)

        oppositions = [a for a in chart.aspects if a.aspect_name == "Opposition"]
        sextiles = [a for a in chart.aspects if a.aspect_name == "Sextile"]

        planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]

        # For each Grand Trine
        for gt in grand_trines:
            gt_planets = gt.planets

            # Try each point of the trine as potential opposition point
            for i, trine_planet in enumerate(gt_planets):
                other_trine_planets = [p for j, p in enumerate(gt_planets) if j != i]

                # Find planets opposed to this trine point
                for apex in planets:
                    if apex in gt_planets:
                        continue

                    opp = self._has_aspect(oppositions, apex, trine_planet)
                    if not opp:
                        continue

                    # Check if apex sextiles the other two trine points
                    sext1 = self._has_aspect(sextiles, apex, other_trine_planets[0])
                    sext2 = self._has_aspect(sextiles, apex, other_trine_planets[1])

                    if sext1 and sext2:
                        # Kite found!
                        kite_planets = gt_planets + [apex]
                        kite_aspects = gt.aspects + [opp, sext1, sext2]

                        avg_orb = sum(a.orb for a in kite_aspects) / len(kite_aspects)
                        strength = max(0, 1 - (avg_orb / 8.0))

                        patterns.append(AspectPattern(
                            pattern_type="Kite",
                            planets=kite_planets,
                            aspects=kite_aspects,
                            element=gt.element,
                            strength=strength,
                        ))

        return patterns

    def _has_aspect(
        self,
        aspects: List[Aspect],
        p1: CelestialPosition,
        p2: CelestialPosition
    ) -> Aspect:
        """Check if two planets have a specific aspect."""
        for aspect in aspects:
            if (aspect.object1 == p1 and aspect.object2 == p2) or \
               (aspect.object1 == p2 and aspect.object2 == p1):
                return aspect
        return None

    def _determine_element(self, planets: List[CelestialPosition]) -> str:
        """Determine predominant element in a planet set."""
        elements = {
            'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
            'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
            'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
            'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
        }

        element_counts = {}
        for planet in planets:
            elem = elements.get(planet.sign, 'Unknown')
            element_counts[elem] = element_counts.get(elem, 0) + 1

        if not element_counts:
            return "Mixed"

        most_common = max(element_counts.items(), key=lambda x: x[1])
        return most_common[0] if most_common[1] >= 2 else "Mixed"

    def _determine_quality(self, planets: List[CelestialPosition]) -> str:
        """Determine predominant quality (modality) in a planet set."""
        qualities = {
            'Aries': 'Cardinal', 'Cancer': 'Cardinal', 'Libra': 'Cardinal', 'Capricorn': 'Cardinal',
            'Taurus': 'Fixed', 'Leo': 'Fixed', 'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
            'Gemini': 'Mutable', 'Virgo': 'Mutable', 'Sagittarius': 'Mutable', 'Pisces': 'Mutable',
        }

        quality_counts = {}
        for planet in planets:
            qual = qualities.get(planet.sign, 'Unknown')
            quality_counts[qual] = quality_counts.get(qual, 0) + 1

        if not quality_counts:
            return "Mixed"

        most_common = max(quality_counts.items(), key=lambda x: x[1])
        return most_common[0] if most_common[1] >= 2 else "Mixed"


class StelliumDetector:
    """
    Detect stelliums (concentrations of planets).

    A stellium is typically 3+ planets in the same sign or house,
    within a certain orb span.
    """

    def __init__(self, min_planets: int = 3, max_orb_span: float = 10.0):
        """
        Initialize stellium detector.

        Args:
            min_planets: Minimum planets for a stellium
            max_orb_span: Maximum orb span (in degrees) for sign stelliums
        """
        self._min_planets = min_planets
        self._max_orb_span = max_orb_span

    @property
    def analyzer_name(self) -> str:
        return "Stellium Detector"

    def analyze(self, chart: CalculatedChart) -> List[Stellium]:
        """
        Detect stelliums in chart.

        Args:
            chart: Chart to analyze

        Returns:
            List of detected stelliums
        """
        stelliums = []

        # Find sign stelliums
        stelliums.extend(self._find_sign_stelliums(chart))

        # Find house stelliums
        stelliums.extend(self._find_house_stelliums(chart))

        return stelliums

    def _find_sign_stelliums(self, chart: CalculatedChart) -> List[Stellium]:
        """Find stelliums by sign."""
        stelliums = []

        # Get planets only (not angles, parts, etc.)
        planets = [
            p for p in chart.positions
            if p.object_type in (ObjectType.PLANET, ObjectType.ASTEROID)
        ]

        # Group by sign
        by_sign = {}
        for planet in planets:
            if planet.sign not in by_sign:
                by_sign[planet.sign] = []
            by_sign[planet.sign].append(planet)

        # Check each sign
        for sign, sign_planets in by_sign.items():
            if len(sign_planets) >= self._min_planets:
                # Check orb span
                longitudes = [p.longitude for p in sign_planets]
                orb_span = max(longitudes) - min(longitudes)

                if orb_span <= self._max_orb_span:
                    stelliums.append(Stellium(
                        location_type="sign",
                        location=sign,
                        planets=sign_planets,
                        orb_span=orb_span,
                    ))

        return stelliums

    def _find_house_stelliums(self, chart: CalculatedChart) -> List[Stellium]:
        """Find stelliums by house."""
        stelliums = []

        # Get planets with house assignments
        planets = [
            p for p in chart.positions
            if p.object_type in (ObjectType.PLANET, ObjectType.ASTEROID)
            and p.house is not None
        ]

        # Group by house
        by_house = {}
        for planet in planets:
            house_num = planet.house
            if house_num not in by_house:
                by_house[house_num] = []
            by_house[house_num].append(planet)

        # Check each house
        for house_num, house_planets in by_house.items():
            if len(house_planets) >= self._min_planets:
                # Calculate orb span
                longitudes = [p.longitude for p in house_planets]
                orb_span = max(longitudes) - min(longitudes)

                stelliums.append(Stellium(
                    location_type="house",
                    location=f"House {house_num}",
                    planets=house_planets,
                    orb_span=orb_span,
                ))

        return stelliums
```

**Why this design?**

1. **Geometric Accuracy**: Patterns use actual aspect calculations
2. **Quality Metrics**: Strength ratings based on orb tightness
3. **Element/Quality Awareness**: Patterns classified by element/modality
4. **Comprehensive**: Covers major pattern types
5. **Extensible**: Easy to add new pattern types

### Step 16.4: Test Pattern Detection

**File**: `tests/test_pattern_detection.py`

```python
"""Test aspect pattern detection."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.aspects import ModernAspectEngine
from stellium.analysis.patterns import PatternDetector, StelliumDetector


def test_grand_trine_detection():
    """Test Grand Trine detection."""
    # Charts with known Grand Trines can be tested
    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(37.7749, -122.4194, "San Francisco")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    detector = PatternDetector()
    patterns = detector.analyze(chart)

    grand_trines = [p for p in patterns if p.pattern_type == "Grand Trine"]

    # May or may not have grand trines - just verify it doesn't crash
    assert isinstance(grand_trines, list)

    for gt in grand_trines:
        assert len(gt.planets) == 3
        assert len(gt.aspects) == 3
        assert gt.element in ('Fire', 'Earth', 'Air', 'Water', 'Mixed')


def test_t_square_detection():
    """Test T-Square detection."""
    dt = datetime(1879, 3, 14, 11, 30, tzinfo=pytz.UTC)
    location = ChartLocation(48.5333, 7.5833, "Ulm")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    detector = PatternDetector()
    patterns = detector.analyze(chart)

    t_squares = [p for p in patterns if p.pattern_type == "T-Square"]

    for ts in t_squares:
        assert len(ts.planets) == 3
        assert len(ts.aspects) == 3  # 1 opposition + 2 squares
        assert ts.quality in ('Cardinal', 'Fixed', 'Mutable', 'Mixed')


def test_yod_detection():
    """Test Yod detection."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(0, 0, "Test")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    detector = PatternDetector()
    patterns = detector.analyze(chart)

    yods = [p for p in patterns if p.pattern_type == "Yod"]

    for yod in yods:
        assert len(yod.planets) == 3
        assert len(yod.aspects) == 3  # 1 sextile + 2 quincunxes


def test_stellium_detection():
    """Test stellium detection."""
    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(37.7749, -122.4194, "San Francisco")

    chart = ChartBuilder.from_datetime(dt, location).calculate()

    detector = StelliumDetector(min_planets=3)
    stelliums = detector.analyze(chart)

    # Should detect any stelliums
    for stellium in stelliums:
        assert len(stellium.planets) >= 3
        assert stellium.location_type in ('sign', 'house')


def test_pattern_strength():
    """Test that pattern strength is calculated."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    detector = PatternDetector()
    patterns = detector.analyze(chart)

    for pattern in patterns:
        assert 0 <= pattern.strength <= 1
        # Tighter orbs should give higher strength
        assert pattern.strength >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Day 17: Synastry Charts

### Why Synastry?

Synastry compares two charts to understand relationship dynamics:
1. **Relationship astrology** - How two people interact
2. **Multi-chart calculations** - Aspects between charts
3. **Composite charts** - Midpoint chart of two people
4. **Data model validation** - Tests chart comparison capabilities

### Step 17.1: Create Synastry Models

**File**: `src/stellium/synastry/models.py`

```python
"""
Data models for synastry analysis.
"""

from dataclasses import dataclass
from typing import List
from stellium.core.models import CalculatedChart, CelestialPosition, Aspect


@dataclass(frozen=True)
class SynastryAspect:
    """
    Aspect between planets in two different charts.

    Unlike regular aspects (planet to planet in same chart),
    these are inter-chart aspects.
    """

    person1_object: CelestialPosition
    person2_object: CelestialPosition
    aspect_name: str
    orb: float
    person1_name: str = "Person 1"
    person2_name: str = "Person 2"

    def __str__(self) -> str:
        return (
            f"{self.person1_name}'s {self.person1_object.name} "
            f"{self.aspect_name} "
            f"{self.person2_name}'s {self.person2_object.name} "
            f"(orb: {self.orb:.1f}°)"
        )


@dataclass(frozen=True)
class SynastryChart:
    """
    Complete synastry analysis between two charts.
    """

    chart1: CalculatedChart
    chart2: CalculatedChart
    person1_name: str
    person2_name: str
    inter_aspects: List[SynastryAspect]

    def get_aspects_to_object(self, object_name: str, chart_num: int = 1) -> List[SynastryAspect]:
        """
        Get all inter-chart aspects to a specific object.

        Args:
            object_name: Name of the object
            chart_num: Which chart (1 or 2)

        Returns:
            List of aspects to this object
        """
        if chart_num == 1:
            return [
                a for a in self.inter_aspects
                if a.person1_object.name == object_name
            ]
        else:
            return [
                a for a in self.inter_aspects
                if a.person2_object.name == object_name
            ]
```

### Step 17.2: Create Synastry Calculator

**File**: `src/stellium/synastry/calculator.py`

```python
"""
Synastry calculation between two natal charts.
"""

from typing import List, Dict, Optional
from stellium.core.models import CalculatedChart, CelestialPosition, ObjectType
from stellium.synastry.models import SynastryAspect, SynastryChart


class SynastryCalculator:
    """
    Calculate synastry between two natal charts.

    Finds aspects between planets in different charts to understand
    relationship dynamics.
    """

    # Standard aspect angles
    ASPECT_DEFINITIONS = {
        'Conjunction': (0, 8),
        'Sextile': (60, 6),
        'Square': (90, 7),
        'Trine': (120, 8),
        'Opposition': (180, 8),
        'Quincunx': (150, 3),
    }

    def __init__(
        self,
        aspects: Optional[Dict[str, tuple]] = None,
        orb_reduction: float = 0.8,
    ):
        """
        Initialize synastry calculator.

        Args:
            aspects: Custom aspect definitions (angle, orb)
            orb_reduction: Reduce orbs by this factor (synastry orbs are typically tighter)
        """
        self._aspects = aspects or self.ASPECT_DEFINITIONS
        self._orb_reduction = orb_reduction

    def calculate(
        self,
        chart1: CalculatedChart,
        chart2: CalculatedChart,
        person1_name: str = "Person 1",
        person2_name: str = "Person 2",
    ) -> SynastryChart:
        """
        Calculate synastry between two charts.

        Args:
            chart1: First person's natal chart
            chart2: Second person's natal chart
            person1_name: Name for first person
            person2_name: Name for second person

        Returns:
            SynastryChart with inter-chart aspects
        """
        # Get planet positions from both charts
        planets1 = self._get_synastry_objects(chart1)
        planets2 = self._get_synastry_objects(chart2)

        # Calculate inter-chart aspects
        inter_aspects = []

        for p1 in planets1:
            for p2 in planets2:
                aspect = self._calculate_aspect(p1, p2, person1_name, person2_name)
                if aspect:
                    inter_aspects.append(aspect)

        return SynastryChart(
            chart1=chart1,
            chart2=chart2,
            person1_name=person1_name,
            person2_name=person2_name,
            inter_aspects=inter_aspects,
        )

    def _get_synastry_objects(self, chart: CalculatedChart) -> List[CelestialPosition]:
        """Get objects to use in synastry (planets + angles)."""
        return [
            p for p in chart.positions
            if p.object_type in (ObjectType.PLANET, ObjectType.ANGLE, ObjectType.ASTEROID)
        ]

    def _calculate_aspect(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        person1_name: str,
        person2_name: str,
    ) -> Optional[SynastryAspect]:
        """
        Calculate aspect between two objects from different charts.

        Args:
            obj1: Object from chart 1
            obj2: Object from chart 2
            person1_name: First person's name
            person2_name: Second person's name

        Returns:
            SynastryAspect if aspect found, None otherwise
        """
        # Calculate angular distance
        distance = abs(obj1.longitude - obj2.longitude)
        if distance > 180:
            distance = 360 - distance

        # Check each aspect type
        for aspect_name, (angle, base_orb) in self._aspects.items():
            orb = base_orb * self._orb_reduction
            diff = abs(distance - angle)

            if diff <= orb:
                return SynastryAspect(
                    person1_object=obj1,
                    person2_object=obj2,
                    aspect_name=aspect_name,
                    orb=diff,
                    person1_name=person1_name,
                    person2_name=person2_name,
                )

        return None
```

### Step 17.3: Create Composite Chart Calculator

**File**: `src/stellium/synastry/composite.py`

```python
"""
Composite chart calculation.

A composite chart is created by finding the midpoints between
corresponding planets in two natal charts.
"""

from datetime import datetime, timedelta
import pytz
from typing import List

from stellium.core.models import (
    CalculatedChart,
    ChartDateTime,
    ChartLocation,
    CelestialPosition,
    HouseCusps,
    ObjectType,
)
from stellium.core.builder import ChartBuilder


class CompositeChartCalculator:
    """
    Calculate composite charts.

    A composite chart represents the "third entity" of a relationship,
    calculated as the midpoints between planets in two charts.
    """

    def calculate(
        self,
        chart1: CalculatedChart,
        chart2: CalculatedChart,
    ) -> CalculatedChart:
        """
        Calculate composite chart from two natal charts.

        Args:
            chart1: First person's chart
            chart2: Second person's chart

        Returns:
            Composite chart
        """
        # Calculate midpoint datetime
        composite_dt = self._calculate_midpoint_datetime(
            chart1.datetime.utc_datetime,
            chart2.datetime.utc_datetime,
        )

        # Calculate midpoint location
        composite_loc = ChartLocation(
            latitude=(chart1.location.latitude + chart2.location.latitude) / 2,
            longitude=(chart1.location.longitude + chart2.location.longitude) / 2,
            name="Composite Location",
        )

        # Build composite chart
        composite = ChartBuilder.from_datetime(composite_dt, composite_loc).calculate()

        return composite

    def _calculate_midpoint_datetime(self, dt1: datetime, dt2: datetime) -> datetime:
        """Calculate midpoint between two datetimes."""
        # Convert to timestamps
        ts1 = dt1.timestamp()
        ts2 = dt2.timestamp()

        # Find midpoint
        mid_ts = (ts1 + ts2) / 2

        # Convert back to datetime
        mid_dt = datetime.fromtimestamp(mid_ts, tz=pytz.UTC)

        return mid_dt
```

### Step 17.4: Test Synastry

**File**: `tests/test_synastry.py`

```python
"""Test synastry calculations."""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.synastry.calculator import SynastryCalculator
from stellium.synastry.composite import CompositeChartCalculator


def test_basic_synastry():
    """Test basic synastry calculation."""
    # Two sample charts
    dt1 = datetime(1990, 1, 1, 12, 0, tzinfo=pytz.UTC)
    dt2 = datetime(1992, 6, 15, 18, 30, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    chart1 = ChartBuilder.from_datetime(dt1, location).calculate()
    chart2 = ChartBuilder.from_datetime(dt2, location).calculate()

    calculator = SynastryCalculator()
    synastry = calculator.calculate(chart1, chart2, "Alice", "Bob")

    assert synastry.person1_name == "Alice"
    assert synastry.person2_name == "Bob"
    assert synastry.chart1 == chart1
    assert synastry.chart2 == chart2

    # Should have some inter-aspects
    assert len(synastry.inter_aspects) > 0

    # Check aspect structure
    for aspect in synastry.inter_aspects:
        assert aspect.person1_object is not None
        assert aspect.person2_object is not None
        assert aspect.aspect_name in SynastryCalculator.ASPECT_DEFINITIONS
        assert aspect.orb >= 0


def test_synastry_sun_contacts():
    """Test finding aspects to Sun."""
    dt1 = datetime(1990, 1, 1, 12, 0, tzinfo=pytz.UTC)
    dt2 = datetime(1990, 1, 5, 12, 0, tzinfo=pytz.UTC)  # Close dates = close Suns
    location = ChartLocation(0, 0, "Test")

    chart1 = ChartBuilder.from_datetime(dt1, location).calculate()
    chart2 = ChartBuilder.from_datetime(dt2, location).calculate()

    calculator = SynastryCalculator()
    synastry = calculator.calculate(chart1, chart2)

    # Get aspects to Person 1's Sun
    sun_aspects = synastry.get_aspects_to_object("Sun", chart_num=1)

    # Should have at least conjunction to Person 2's Sun
    assert len(sun_aspects) > 0


def test_composite_chart():
    """Test composite chart calculation."""
    dt1 = datetime(1990, 1, 1, 12, 0, tzinfo=pytz.UTC)
    dt2 = datetime(1992, 6, 15, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    chart1 = ChartBuilder.from_datetime(dt1, location).calculate()
    chart2 = ChartBuilder.from_datetime(dt2, location).calculate()

    calculator = CompositeChartCalculator()
    composite = calculator.calculate(chart1, chart2)

    # Should be a valid chart
    assert composite is not None
    assert len(composite.positions) > 0

    # Datetime should be between the two charts
    assert chart1.datetime.utc_datetime < composite.datetime.utc_datetime < chart2.datetime.utc_datetime


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Day 18: Transit Calculator

### Why Transits?

Transits show current planetary positions relative to natal positions:
1. **Timing** - When will events happen?
2. **Time-based features** - Test datetime handling
3. **Practical utility** - Users want to know transits
4. **API design** - Time-range queries

### Step 18.1: Create Transit Models

**File**: `src/stellium/transits/models.py`

```python
"""
Data models for transit calculations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
from stellium.core.models import CelestialPosition


@dataclass(frozen=True)
class Transit:
    """
    A transit aspect between a moving planet and a natal planet.
    """

    transit_datetime: datetime
    transiting_object: CelestialPosition
    natal_object: CelestialPosition
    aspect_name: str
    orb: float
    is_exact: bool = False  # True if orb < 0.1°

    def __str__(self) -> str:
        exact_marker = " [EXACT]" if self.is_exact else ""
        return (
            f"Transit {self.transiting_object.name} "
            f"{self.aspect_name} "
            f"Natal {self.natal_object.name} "
            f"(orb: {self.orb:.2f}°){exact_marker}"
        )


@dataclass(frozen=True)
class TransitSet:
    """
    Collection of transits for a specific time period.
    """

    natal_chart: 'CalculatedChart'
    start_date: datetime
    end_date: datetime
    transits: List[Transit]

    def get_transits_by_planet(self, planet_name: str) -> List[Transit]:
        """Get all transits for a specific transiting planet."""
        return [
            t for t in self.transits
            if t.transiting_object.name == planet_name
        ]

    def get_transits_to_natal_object(self, object_name: str) -> List[Transit]:
        """Get all transits aspecting a specific natal object."""
        return [
            t for t in self.transits
            if t.natal_object.name == object_name
        ]

    def get_exact_transits(self) -> List[Transit]:
        """Get only exact transits (orb < 0.1°)."""
        return [t for t in self.transits if t.is_exact]
```

### Step 18.2: Create Transit Calculator

**File**: `src/stellium/transits/calculator.py`

```python
"""
Transit calculator.

Calculates when transiting planets aspect natal planets.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz

from stellium.core.models import CalculatedChart, CelestialPosition, ChartLocation
from stellium.core.builder import ChartBuilder
from stellium.transits.models import Transit, TransitSet


class TransitCalculator:
    """
    Calculate transits to a natal chart.

    Finds when current/future planetary positions aspect natal positions.
    """

    ASPECT_DEFINITIONS = {
        'Conjunction': (0, 1.0),
        'Sextile': (60, 1.0),
        'Square': (90, 1.0),
        'Trine': (120, 1.0),
        'Opposition': (180, 1.0),
    }

    def __init__(
        self,
        aspects: Optional[Dict[str, tuple]] = None,
    ):
        """
        Initialize transit calculator.

        Args:
            aspects: Aspect definitions (angle, orb)
        """
        self._aspects = aspects or self.ASPECT_DEFINITIONS

    def calculate_transits(
        self,
        natal_chart: CalculatedChart,
        start_date: datetime,
        end_date: datetime,
        step_days: float = 1.0,
    ) -> TransitSet:
        """
        Calculate all transits in a date range.

        Args:
            natal_chart: Natal chart to transit
            start_date: Start of period
            end_date: End of period
            step_days: Days between calculations

        Returns:
            TransitSet with all found transits
        """
        transits = []

        # Get natal positions
        natal_positions = self._get_transit_positions(natal_chart)

        # Step through time
        current = start_date
        step = timedelta(days=step_days)

        while current <= end_date:
            # Calculate transit chart for this moment
            transit_chart = ChartBuilder.from_datetime(
                current,
                natal_chart.location
            ).calculate()

            transit_positions = self._get_transit_positions(transit_chart)

            # Find aspects
            for transit_obj in transit_positions:
                for natal_obj in natal_positions:
                    aspect = self._find_aspect(transit_obj, natal_obj)
                    if aspect:
                        transits.append(Transit(
                            transit_datetime=current,
                            transiting_object=transit_obj,
                            natal_object=natal_obj,
                            aspect_name=aspect[0],
                            orb=aspect[1],
                            is_exact=(aspect[1] < 0.1),
                        ))

            current += step

        return TransitSet(
            natal_chart=natal_chart,
            start_date=start_date,
            end_date=end_date,
            transits=transits,
        )

    def calculate_current_transits(
        self,
        natal_chart: CalculatedChart,
        orb: float = 1.0,
    ) -> List[Transit]:
        """
        Calculate transits happening right now.

        Args:
            natal_chart: Natal chart
            orb: Orb to use for all aspects

        Returns:
            List of current transits
        """
        now = datetime.now(pytz.UTC)

        # Calculate one moment
        transit_set = self.calculate_transits(
            natal_chart,
            now,
            now,
            step_days=1,
        )

        return transit_set.transits

    def _get_transit_positions(self, chart: CalculatedChart) -> List[CelestialPosition]:
        """Get positions to use in transit calculations."""
        from stellium.core.models import ObjectType
        return [
            p for p in chart.positions
            if p.object_type == ObjectType.PLANET
        ]

    def _find_aspect(
        self,
        transit_obj: CelestialPosition,
        natal_obj: CelestialPosition,
    ) -> Optional[tuple]:
        """
        Find aspect between transiting and natal object.

        Returns:
            (aspect_name, orb) or None
        """
        distance = abs(transit_obj.longitude - natal_obj.longitude)
        if distance > 180:
            distance = 360 - distance

        for aspect_name, (angle, max_orb) in self._aspects.items():
            orb = abs(distance - angle)
            if orb <= max_orb:
                return (aspect_name, orb)

        return None
```

### Step 18.3: Test Transits

**File**: `tests/test_transits.py`

```python
"""Test transit calculations."""

import pytest
from datetime import datetime, timedelta
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.transits.calculator import TransitCalculator


def test_current_transits():
    """Test calculating current transits."""
    # Create a natal chart
    natal_dt = datetime(1990, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")
    natal_chart = ChartBuilder.from_datetime(natal_dt, location).calculate()

    calculator = TransitCalculator()
    transits = calculator.calculate_current_transits(natal_chart, orb=2.0)

    # Should find some transits
    assert isinstance(transits, list)

    # Each transit should be valid
    for transit in transits:
        assert transit.transiting_object is not None
        assert transit.natal_object is not None
        assert transit.aspect_name in TransitCalculator.ASPECT_DEFINITIONS
        assert transit.orb >= 0


def test_transit_period():
    """Test calculating transits over a period."""
    natal_dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(0, 0, "Test")
    natal_chart = ChartBuilder.from_datetime(natal_dt, location).calculate()

    # Calculate transits for 30 days
    start = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end = start + timedelta(days=30)

    calculator = TransitCalculator()
    transit_set = calculator.calculate_transits(
        natal_chart,
        start,
        end,
        step_days=1.0,
    )

    assert transit_set.start_date == start
    assert transit_set.end_date == end
    assert len(transit_set.transits) > 0


def test_exact_transits():
    """Test filtering exact transits."""
    natal_dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")
    natal_chart = ChartBuilder.from_datetime(natal_dt, location).calculate()

    start = datetime(2025, 1, 1, tzinfo=pytz.UTC)
    end = start + timedelta(days=7)

    calculator = TransitCalculator()
    transit_set = calculator.calculate_transits(natal_chart, start, end)

    exact = transit_set.get_exact_transits()

    # All exact transits should have very small orbs
    for transit in exact:
        assert transit.orb < 0.1
        assert transit.is_exact


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Day 19: Plugin Foundation

### Why Plugin System?

A plugin system enables:
1. **Extensibility** - Users can add features
2. **Third-party development** - Community contributions
3. **Clean architecture** - Proves our protocols work
4. **Future growth** - Easy to add new features

### Step 19.1: Design Plugin Protocol

**File**: `src/stellium/plugins/__init__.py`

```python
"""
Plugin system for Stellium.

Allows third-party extensions for:
- Custom components (new calculations)
- Custom engines (alternative implementations)
- Custom analyzers (interpretation systems)
- Custom exporters (output formats)
"""

from typing import Protocol, List, Any
from stellium.core.models import CalculatedChart


class StelliumPlugin(Protocol):
    """
    Base protocol for all Stellium plugins.

    All plugins must implement this interface.
    """

    @property
    def plugin_name(self) -> str:
        """Unique name for this plugin."""
        ...

    @property
    def plugin_version(self) -> str:
        """Version string (semver recommended)."""
        ...

    @property
    def plugin_type(self) -> str:
        """
        Type of plugin.

        Valid types: "component", "engine", "analyzer", "exporter"
        """
        ...

    def initialize(self) -> None:
        """
        Initialize the plugin.

        Called once when plugin is loaded.
        """
        ...


class ExporterPlugin(StelliumPlugin, Protocol):
    """
    Plugin that exports charts to different formats.

    Examples: PDF, HTML, PNG, JSON schema, database, etc.
    """

    def export(self, chart: CalculatedChart, **kwargs) -> Any:
        """
        Export a chart.

        Args:
            chart: Chart to export
            **kwargs: Format-specific options

        Returns:
            Exported data (format-dependent)
        """
        ...
```

### Step 19.2: Create Plugin Registry

**File**: `src/stellium/plugins/registry.py`

```python
"""
Plugin registry and discovery system.
"""

from typing import Dict, List, Type, Optional
import importlib
import pkgutil


class PluginRegistry:
    """
    Central registry for Stellium plugins.

    Handles plugin discovery, registration, and retrieval.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._plugins: Dict[str, object] = {}
        self._plugins_by_type: Dict[str, List[object]] = {
            'component': [],
            'engine': [],
            'analyzer': [],
            'exporter': [],
        }

    def register(self, plugin: object) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance implementing StelliumPlugin protocol
        """
        # Validate plugin
        if not hasattr(plugin, 'plugin_name'):
            raise ValueError("Plugin must have plugin_name property")
        if not hasattr(plugin, 'plugin_type'):
            raise ValueError("Plugin must have plugin_type property")

        # Initialize plugin
        if hasattr(plugin, 'initialize'):
            plugin.initialize()

        # Register
        name = plugin.plugin_name
        plugin_type = plugin.plugin_type

        self._plugins[name] = plugin

        if plugin_type in self._plugins_by_type:
            self._plugins_by_type[plugin_type].append(plugin)

    def get_plugin(self, name: str) -> Optional[object]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)

    def get_plugins_by_type(self, plugin_type: str) -> List[object]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: Type ("component", "engine", etc.)

        Returns:
            List of plugin instances
        """
        return self._plugins_by_type.get(plugin_type, [])

    def list_plugins(self) -> List[tuple]:
        """
        List all registered plugins.

        Returns:
            List of (name, type, version) tuples
        """
        result = []
        for name, plugin in self._plugins.items():
            version = getattr(plugin, 'plugin_version', 'unknown')
            plugin_type = getattr(plugin, 'plugin_type', 'unknown')
            result.append((name, plugin_type, version))
        return result


# Global registry instance
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    return _registry
```

### Step 19.3: Create Example Plugin

**File**: `examples/sample_plugin.py`

```python
"""
Sample plugin demonstrating how to extend Stellium.

This plugin exports charts to a simple HTML format.
"""

from stellium.core.models import CalculatedChart, ObjectType
from stellium.plugins import ExporterPlugin


class HTMLExporterPlugin:
    """
    Export charts to HTML format.

    Demonstrates the ExporterPlugin protocol.
    """

    @property
    def plugin_name(self) -> str:
        return "html-exporter"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    @property
    def plugin_type(self) -> str:
        return "exporter"

    def initialize(self) -> None:
        """Initialize the plugin."""
        print(f"Initializing {self.plugin_name} v{self.plugin_version}")

    def export(self, chart: CalculatedChart, filename: str = None) -> str:
        """
        Export chart to HTML.

        Args:
            chart: Chart to export
            filename: Optional output filename

        Returns:
            HTML string
        """
        html_parts = []

        # Header
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html>")
        html_parts.append("<head>")
        html_parts.append("  <title>Astrological Chart</title>")
        html_parts.append("  <style>")
        html_parts.append("    body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("    table { border-collapse: collapse; width: 100%; }")
        html_parts.append("    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html_parts.append("    th { background-color: #4CAF50; color: white; }")
        html_parts.append("  </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")

        # Chart info
        html_parts.append(f"  <h1>Astrological Chart</h1>")
        html_parts.append(f"  <p><strong>Date:</strong> {chart.datetime.utc_datetime}</p>")
        html_parts.append(f"  <p><strong>Location:</strong> {chart.location.name or 'Unknown'}</p>")

        # Planets table
        html_parts.append("  <h2>Planetary Positions</h2>")
        html_parts.append("  <table>")
        html_parts.append("    <tr><th>Planet</th><th>Sign</th><th>Position</th><th>House</th></tr>")

        planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]
        for planet in planets:
            degrees = int(planet.sign_degree)
            minutes = int((planet.sign_degree % 1) * 60)
            html_parts.append(f"    <tr>")
            html_parts.append(f"      <td>{planet.name}</td>")
            html_parts.append(f"      <td>{planet.sign}</td>")
            html_parts.append(f"      <td>{degrees}°{minutes:02d}'</td>")
            html_parts.append(f"      <td>{planet.house or '—'}</td>")
            html_parts.append(f"    </tr>")

        html_parts.append("  </table>")

        # Aspects table
        if chart.aspects:
            html_parts.append("  <h2>Aspects</h2>")
            html_parts.append("  <table>")
            html_parts.append("    <tr><th>Planet 1</th><th>Aspect</th><th>Planet 2</th><th>Orb</th></tr>")

            for aspect in chart.aspects:
                html_parts.append(f"    <tr>")
                html_parts.append(f"      <td>{aspect.object1.name}</td>")
                html_parts.append(f"      <td>{aspect.aspect_name}</td>")
                html_parts.append(f"      <td>{aspect.object2.name}</td>")
                html_parts.append(f"      <td>{aspect.orb:.1f}°</td>")
                html_parts.append(f"    </tr>")

            html_parts.append("  </table>")

        # Footer
        html_parts.append("</body>")
        html_parts.append("</html>")

        html = "\n".join(html_parts)

        # Write to file if specified
        if filename:
            with open(filename, 'w') as f:
                f.write(html)

        return html


# Example usage
if __name__ == "__main__":
    from datetime import datetime
    import pytz
    from stellium.core.builder import ChartBuilder
    from stellium.core.models import ChartLocation
    from stellium.plugins.registry import get_registry

    # Register the plugin
    plugin = HTMLExporterPlugin()
    registry = get_registry()
    registry.register(plugin)

    # Create a chart
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(0, 0, "Test Location")
    chart = ChartBuilder.from_datetime(dt, location).calculate()

    # Export using plugin
    html = plugin.export(chart, "examples/output/chart.html")
    print(f"✅ Chart exported to HTML ({len(html)} characters)")
```

### Step 19.4: Document Plugin System

**File**: `docs/development/PLUGIN_GUIDE.md`

```markdown
# Stellium Plugin Development Guide

## Overview

Stellium's plugin system allows you to extend the library with custom functionality.

## Plugin Types

### 1. Component Plugins

Add new calculations to charts:

```python
class MyCustomComponent:
    @property
    def component_name(self) -> str:
        return "My Component"

    def calculate(self, datetime, location, positions, houses):
        # Your calculation logic
        return [...]  # Return CelestialPosition objects
```

### 2. Engine Plugins

Replace core engines (houses, aspects, ephemeris):

```python
class MyHouseSystem:
    @property
    def system_name(self) -> str:
        return "My Houses"

    def calculate_houses(self, julian_day, lat, lon):
        # Your house calculation
        return HouseCusps(...)
```

### 3. Analyzer Plugins

Add interpretation/analysis:

```python
class MyAnalyzer:
    @property
    def analyzer_name(self) -> str:
        return "My Analyzer"

    def analyze(self, chart):
        # Your analysis logic
        return [...]  # Return findings
```

### 4. Exporter Plugins

Export to new formats:

```python
class MyExporter:
    @property
    def plugin_type(self) -> str:
        return "exporter"

    def export(self, chart, **kwargs):
        # Export logic
        return exported_data
```

## Registration

```python
from stellium.plugins.registry import get_registry

plugin = MyPlugin()
registry = get_registry()
registry.register(plugin)
```

## Best Practices

1. **Follow protocols** - Implement all required methods
2. **Document well** - Clear docstrings and examples
3. **Test thoroughly** - Include comprehensive tests
4. **Version properly** - Use semantic versioning
5. **Handle errors** - Graceful failure, clear messages

## Example: Custom Component

See `examples/sample_plugin.py` for a complete working example.
```

---

## Day 20: Performance & Polish

### Why Performance Matters?

Before releasing the refactored architecture:
1. **Benchmark** - Ensure it's not slower than old code
2. **Optimize** - Fix bottlenecks
3. **Cache effectively** - Expensive calculations
4. **Document** - Complete guide for users
5. **Testing** - Comprehensive coverage

### Step 20.1: Create Performance Benchmarks

**File**: `tests/benchmarks/benchmark_charts.py`

```python
"""
Performance benchmarks for chart calculations.

Measures performance of the new architecture.
"""

import time
from datetime import datetime
import pytz
from typing import Callable

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.aspects import ModernAspectEngine
from stellium.components.arabic_parts import ArabicPartsCalculator
from stellium.components.midpoints import MidpointCalculator


class Benchmark:
    """Simple benchmark runner."""

    @staticmethod
    def measure(func: Callable, iterations: int = 100) -> float:
        """
        Measure average execution time.

        Args:
            func: Function to benchmark
            iterations: Number of iterations

        Returns:
            Average time in milliseconds
        """
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        return sum(times) / len(times)


def benchmark_basic_chart():
    """Benchmark: Basic chart calculation."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    def calc():
        ChartBuilder.from_datetime(dt, location).calculate()

    avg_time = Benchmark.measure(calc, iterations=50)
    print(f"Basic chart calculation: {avg_time:.2f} ms")
    return avg_time


def benchmark_with_aspects():
    """Benchmark: Chart with aspects."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    def calc():
        ChartBuilder.from_datetime(dt, location) \
            .with_aspects(ModernAspectEngine()) \
            .calculate()

    avg_time = Benchmark.measure(calc, iterations=50)
    print(f"Chart with aspects: {avg_time:.2f} ms")
    return avg_time


def benchmark_with_components():
    """Benchmark: Chart with all components."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    def calc():
        ChartBuilder.from_datetime(dt, location) \
            .add_component(ArabicPartsCalculator()) \
            .add_component(MidpointCalculator()) \
            .with_aspects(ModernAspectEngine()) \
            .calculate()

    avg_time = Benchmark.measure(calc, iterations=50)
    print(f"Chart with components: {avg_time:.2f} ms")
    return avg_time


def benchmark_serialization():
    """Benchmark: JSON serialization."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(40, -74, "New York")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    def serialize():
        chart.to_dict()

    avg_time = Benchmark.measure(serialize, iterations=100)
    print(f"JSON serialization: {avg_time:.2f} ms")
    return avg_time


if __name__ == "__main__":
    print("=" * 60)
    print("STARLIGHT PERFORMANCE BENCHMARKS")
    print("=" * 60)
    print()

    benchmark_basic_chart()
    benchmark_with_aspects()
    benchmark_with_components()
    benchmark_serialization()

    print()
    print("=" * 60)
    print("✅ Benchmarks complete!")
    print("=" * 60)
```

Run benchmarks:
```bash
source ~/.zshrc && pyenv activate stellium && python tests/benchmarks/benchmark_charts.py
```

### Step 20.2: Add Caching Optimization

**File**: `src/stellium/core/cache_integration.py`

```python
"""
Cache integration for expensive operations.

Enhances performance by caching:
- Ephemeris calculations
- House calculations
- Aspect calculations
"""

from functools import lru_cache
from typing import Tuple
from stellium.core.models import CelestialPosition, HouseCusps


# Use LRU cache for frequently accessed calculations
@lru_cache(maxsize=1000)
def cache_key_for_datetime_location(julian_day: float, lat: float, lon: float) -> str:
    """Create cache key for datetime/location combination."""
    return f"{julian_day:.6f}_{lat:.6f}_{lon:.6f}"


class CachedEphemerisEngine:
    """
    Wrapper for ephemeris engine with caching.

    Caches planetary positions by datetime to avoid recalculation.
    """

    def __init__(self, engine):
        """
        Initialize cached engine.

        Args:
            engine: Underlying ephemeris engine
        """
        self._engine = engine
        self._cache = {}

    @property
    def engine_name(self) -> str:
        return f"Cached {self._engine.engine_name}"

    def calculate_positions(
        self,
        julian_day: float,
        objects: list,
    ) -> list:
        """Calculate with caching."""
        # Create cache key
        objects_key = tuple(sorted(objects))
        cache_key = (julian_day, objects_key)

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Calculate
        result = self._engine.calculate_positions(julian_day, objects)

        # Store in cache
        self._cache[cache_key] = result

        return result

    def clear_cache(self):
        """Clear the cache."""
        self._cache.clear()
```

### Step 20.3: Create Comprehensive Test Suite

**File**: `tests/test_full_integration.py`

```python
"""
Full integration tests for the new architecture.

Tests complete workflows from start to finish.
"""

import pytest
from datetime import datetime
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.aspects import ModernAspectEngine, HarmonicAspectEngine
from stellium.components.arabic_parts import ArabicPartsCalculator
from stellium.components.midpoints import MidpointCalculator
from stellium.analysis.patterns import PatternDetector, StelliumDetector
from stellium.presentation.modern import print_chart_summary
from stellium.visualization import draw_chart


def test_complete_workflow():
    """Test complete workflow: build, calculate, analyze, display, export."""
    # Step 1: Build chart
    dt = datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC)
    location = ChartLocation(37.7749, -122.4194, "San Francisco, CA")

    chart = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .with_aspects(ModernAspectEngine()) \
        .add_component(ArabicPartsCalculator()) \
        .calculate()

    # Step 2: Verify structure
    assert chart is not None
    assert len(chart.positions) > 0
    assert chart.houses is not None
    assert len(chart.aspects) > 0

    # Step 3: Analyze patterns
    pattern_detector = PatternDetector()
    patterns = pattern_detector.analyze(chart)
    assert isinstance(patterns, list)

    # Step 4: Export to dict
    data = chart.to_dict()
    assert 'positions' in data
    assert 'houses' in data
    assert 'aspects' in data

    # Step 5: Visualize (just verify it doesn't crash)
    import os
    os.makedirs("tests/output/integration", exist_ok=True)
    draw_chart(chart, "tests/output/integration/complete_workflow.svg")

    print("✅ Complete workflow successful!")


def test_multiple_house_systems():
    """Test that multiple house systems work correctly."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(51.5074, -0.1278, "London, UK")

    # Placidus
    placidus = ChartBuilder.from_datetime(dt, location) \
        .with_houses(PlacidusHouses()) \
        .calculate()

    # Whole Sign
    whole_sign = ChartBuilder.from_datetime(dt, location) \
        .with_houses(WholeSignHouses()) \
        .calculate()

    # Both should be valid
    assert placidus.houses.system == "Placidus"
    assert whole_sign.houses.system == "Whole Sign"

    # Houses should be different
    assert placidus.houses.cusps != whole_sign.houses.cusps

    print("✅ Multiple house systems work correctly!")


def test_all_components_together():
    """Test that all components can work together."""
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(0, 0, "Test")

    chart = ChartBuilder.from_datetime(dt, location) \
        .add_component(ArabicPartsCalculator()) \
        .add_component(MidpointCalculator()) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    # Should have positions from all components
    from stellium.core.models import ObjectType

    planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]
    arabic_parts = [p for p in chart.positions if p.object_type == ObjectType.ARABIC_PART]
    midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

    assert len(planets) > 0
    assert len(arabic_parts) > 0
    assert len(midpoints) > 0

    print("✅ All components work together!")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # North pole
    north_pole = ChartLocation(90, 0, "North Pole")
    dt = datetime(2000, 6, 21, 12, 0, tzinfo=pytz.UTC)  # Summer solstice

    chart_north = ChartBuilder.from_datetime(dt, north_pole).calculate()
    assert chart_north is not None

    # South pole
    south_pole = ChartLocation(-90, 0, "South Pole")
    chart_south = ChartBuilder.from_datetime(dt, south_pole).calculate()
    assert chart_south is not None

    # Date line
    dateline = ChartLocation(0, 180, "Date Line")
    chart_dateline = ChartBuilder.from_datetime(dt, dateline).calculate()
    assert chart_dateline is not None

    print("✅ Edge cases handled correctly!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Step 20.4: Create Migration Guide

**File**: `docs/MIGRATION_GUIDE.md`

```markdown
# Migration Guide: Old API → New Architecture

## Overview

This guide helps you migrate from the old `Chart` class to the new builder-based architecture.

## Basic Chart Creation

### Old Way
```python
from stellium.chart import Chart

chart = Chart(
    datetime_utc,
    latitude,
    longitude,
    location_name="New York"
)
```

### New Way
```python
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation

location = ChartLocation(latitude, longitude, "New York")
chart = ChartBuilder.from_datetime(datetime_utc, location).calculate()
```

## With House Systems

### Old Way
```python
chart = Chart(datetime_utc, lat, lon, house_system='W')  # W = Whole Sign
```

### New Way
```python
from stellium.engines.houses import WholeSignHouses

chart = ChartBuilder.from_datetime(dt, location) \
    .with_houses(WholeSignHouses()) \
    .calculate()
```

## With Aspects

### Old Way
```python
chart = Chart(datetime_utc, lat, lon)
aspects = chart.calculate_aspects()
```

### New Way
```python
from stellium.engines.aspects import ModernAspectEngine

chart = ChartBuilder.from_datetime(dt, location) \
    .with_aspects(ModernAspectEngine()) \
    .calculate()

aspects = chart.aspects
```

## Accessing Data

### Old Way
```python
sun = chart.sun
moon = chart.moon
planets = chart.planets
```

### New Way
```python
sun = chart.get_object("Sun")
moon = chart.get_object("Moon")
planets = [p for p in chart.positions if p.object_type == ObjectType.PLANET]
```

## Drawing Charts

### Old Way
```python
from stellium.drawing import draw_chart

draw_chart(chart, "output.svg")
```

### New Way
```python
from stellium.visualization import draw_chart

draw_chart(chart, "output.svg")
```

## Why the New Way is Better

1. **Clearer intent** - Builder pattern shows what you're building
2. **Type safety** - Catch errors at development time
3. **Flexibility** - Easy to swap engines and add components
4. **Immutability** - Charts can't be accidentally modified
5. **Testability** - Mock engines for testing
6. **Documentation** - Self-documenting code

## Need Help?

See `examples/modern_usage.py` for complete working examples.
```

### Step 20.5: Run Complete Test Suite

Create a test runner script:

**File**: `scripts/run_all_tests.sh`

```bash
#!/bin/bash

echo "======================================================================"
echo "STARLIGHT COMPLETE TEST SUITE"
echo "======================================================================"
echo ""

# Activate environment
source ~/.zshrc
pyenv activate stellium

# Run all tests
echo "Running unit tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "Running benchmarks..."
python tests/benchmarks/benchmark_charts.py

echo ""
echo "Running integration tests..."
python tests/test_full_integration.py

echo ""
echo "Running examples..."
python examples/modern_usage.py

echo ""
echo "======================================================================"
echo "✅ ALL TESTS COMPLETE!"
echo "======================================================================"
```

Make it executable:
```bash
chmod +x scripts/run_all_tests.sh
```

---

## End of Week 4 Checkpoint

At this point you should have:

✅ Pattern detection (Grand Trines, T-Squares, Yods, etc.)
✅ Synastry calculations (relationship astrology)
✅ Transit calculator (time-based features)
✅ Plugin foundation (extensibility system)
✅ Performance benchmarks and optimization
✅ Complete test suite
✅ Migration guide for users

**Final validation:**

```bash
# Run everything
source ~/.zshrc && pyenv activate stellium && ./scripts/run_all_tests.sh

# Or run tests individually
source ~/.zshrc && pyenv activate stellium && python -m pytest tests/ -v
source ~/.zshrc && pyenv activate stellium && python examples/modern_usage.py
source ~/.zshrc && pyenv activate stellium && python tests/benchmarks/benchmark_charts.py
```

---

## Final Checklist

Before considering the refactor complete:

### Code Quality
- [ ] All tests passing
- [ ] Type hints on all public APIs
- [ ] Docstrings on all modules/classes/functions
- [ ] No hardcoded magic numbers
- [ ] Error handling implemented
- [ ] Logging added where appropriate

### Documentation
- [ ] README updated
- [ ] API reference complete
- [ ] Migration guide written
- [ ] Example code working
- [ ] Plugin guide complete

### Performance
- [ ] Benchmarks run
- [ ] No performance regression vs old code
- [ ] Caching implemented for expensive operations
- [ ] Memory usage acceptable

### Architecture
- [ ] All protocols implemented correctly
- [ ] Immutability enforced
- [ ] Component system working
- [ ] Engines swappable
- [ ] Clean separation of concerns

### Testing
- [ ] Unit tests for all components
- [ ] Integration tests for workflows
- [ ] Edge case tests
- [ ] Example code runs successfully

---

## Congratulations! 🎉

You've completed the 4-week architectural refactoring of Stellium!

### What You've Built

1. **Clean Architecture** - Protocol-based, immutable, testable
2. **Flexible Foundation** - Swappable engines, pluggable components
3. **Advanced Features** - Synastry, transits, patterns, Arabic parts
4. **Professional Quality** - Documented, tested, performant
5. **Future-Ready** - Plugin system for extensions

### Next Steps

1. **Migrate existing code** - Use the migration guide
2. **Write documentation** - User-facing docs and tutorials
3. **Publish v1.0** - Release the new architecture
4. **Build plugins** - Extend with community contributions
5. **Gather feedback** - Iterate based on real usage

### Key Achievements

- ✨ **Rock-solid foundations** - Clean, maintainable codebase
- 🔌 **Extensible** - Easy to add new features
- 📊 **Complete feature set** - Everything users need
- 🚀 **Production ready** - Tested, documented, optimized
- 🎯 **User-friendly** - Intuitive API, great DX

**You did it!** The library is now everything you wanted it to be. 🌟
