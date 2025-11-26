# Implementation Plan: Transits, Synastry, and Composites

## Overview

This document outlines the implementation strategy for three major chart types in Stellium:

1. **Transits** - Current planetary positions compared to a natal chart
2. **Synastry** - Comparing two charts for relationship compatibility
3. **Composites** - Creating a midpoint chart between two people

---

## Current Architecture Analysis

### Strengths We Can Leverage

1. **Protocol-driven design** - Easy to add new chart types without modifying existing code
2. **Immutable data models** - `CalculatedChart` is thread-safe and cacheable
3. **Builder pattern** - Already supports composable configuration
4. **Multiple house systems** - Infrastructure exists for calculating different systems
5. **Aspect engine** - Can be reused for inter-chart aspects
6. **Component system** - Can add transit/synastry-specific components

### Current Limitations

1. **Single-chart assumption** - `CalculatedChart` represents one chart only
2. **No relationship models** - No data structure for chart comparisons
3. **Aspect engine** - Currently only calculates intra-chart aspects
4. **Visualization** - Designed for single charts (but has layer system for extension)

---

## Design Philosophy

Following Stellium's core principles:

1. **Protocols over Inheritance** - Create new protocols for comparison engines
2. **Composability** - Reuse existing engines where possible
3. **Immutability** - New chart types should be frozen dataclasses
4. **Extensibility** - Make it easy to add new comparison types later

---

## PART 1: TRANSITS

### What Are Transits?

Transits show current (or future/past) planetary positions compared to a natal chart. They reveal timing and activation of natal potentials.

### Design Approach

#### Option A: Transits as Two Separate Charts (Simpler)

```python
natal = ChartBuilder.from_native(native).calculate()
transit_native = Native(datetime.now(), natal.location)
transits = ChartBuilder.from_native(transit_native).calculate()

# User manually compares
transit_aspects = find_aspects_between_charts(natal, transits)
```

**Pros:**

- Minimal new code
- Reuses all existing infrastructure
- User has full flexibility

**Cons:**

- Manual comparison is tedious
- No helper methods
- Doesn't feel integrated

#### Option B: Transit Chart Type (Better)

```python
natal = ChartBuilder.from_native(native).calculate()

# Create a specialized transit chart
transit_chart = TransitBuilder(natal) \
    .for_date(datetime.now()) \
    .with_orbs(TransitOrbEngine()) \  # Tighter orbs for transits
    .calculate()

# Access transit-specific data
print(transit_chart.transit_aspects)  # Transiting planets → natal planets
print(transit_chart.natal_aspects)    # Original natal aspects
print(transit_chart.active_transits)  # Transits within orb
```

**Pros:**

- Clean, purpose-built API
- Can calculate transit-specific features (progressions, returns, etc.)
- Follows builder pattern
- Easy to extend

**Cons:**

- More code to write
- New builder class

### Recommended: Option B - Transit Chart Type

#### New Data Models

```python
@dataclass(frozen=True)
class TransitChart:
    """
    A transit chart comparing current positions to a natal chart.
    """
    natal_chart: CalculatedChart
    transit_chart: CalculatedChart

    # Transit-specific aspects (transiting → natal)
    transit_to_natal_aspects: tuple[Aspect, ...]

    # Metadata
    transit_datetime: ChartDateTime
    calculation_timestamp: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.UTC))

    def get_active_transits(self, orb_threshold: float = 1.0) -> list[Aspect]:
        """Get only tight transits within threshold."""
        return [a for a in self.transit_to_natal_aspects if a.orb <= orb_threshold]

    def get_transits_to_planet(self, natal_planet: str) -> list[Aspect]:
        """Get all transits to a specific natal planet."""
        return [a for a in self.transit_to_natal_aspects if a.object2.name == natal_planet]

    def get_transits_by_transiting_planet(self, transiting_planet: str) -> list[Aspect]:
        """Get all transits from a specific transiting planet."""
        return [a for a in self.transit_to_natal_aspects if a.object1.name == transiting_planet]
```

#### New Builder

```python
class TransitBuilder:
    """Build transit charts comparing current positions to natal."""

    def __init__(self, natal_chart: CalculatedChart):
        self._natal = natal_chart
        self._transit_datetime: ChartDateTime | None = None
        self._orb_engine: OrbEngine = TransitOrbEngine()  # Tighter orbs
        self._aspect_engine: AspectEngine | None = None

    def for_date(self, dt: datetime) -> "TransitBuilder":
        """Set the transit date."""
        # Process datetime same way as Native
        pass

    def with_orbs(self, engine: OrbEngine) -> "TransitBuilder":
        """Custom orb engine for transits."""
        self._orb_engine = engine
        return self

    def calculate(self) -> TransitChart:
        """Calculate transit chart."""
        # 1. Calculate transit positions (same location as natal)
        transit_native = Native(self._transit_datetime, self._natal.location)
        transit_chart = ChartBuilder.from_native(transit_native).calculate()

        # 2. Calculate aspects between transit → natal
        transit_aspects = self._calculate_cross_chart_aspects(
            transit_chart.positions,
            self._natal.positions
        )

        # 3. Return TransitChart
        return TransitChart(
            natal_chart=self._natal,
            transit_chart=transit_chart,
            transit_to_natal_aspects=tuple(transit_aspects),
            transit_datetime=self._transit_datetime
        )
```

#### Supporting Classes

```python
class TransitOrbEngine:
    """Tighter orbs for transits (typically 1-2° for slow planets)."""

    def get_orb(self, aspect_name: str, object1: str, object2: str) -> float:
        # Tighter orbs for transits
        # Outer planets: 1-2°
        # Inner planets: 0.5-1°
        pass
```

### Files to Create/Modify

**New files:**

- `src/stellium/transits/__init__.py`
- `src/stellium/transits/builder.py` - `TransitBuilder`
- `src/stellium/transits/models.py` - `TransitChart`
- `src/stellium/transits/orbs.py` - `TransitOrbEngine`
- `tests/test_transits.py`

**Modified files:**

- `src/stellium/__init__.py` - Export `TransitBuilder`, `TransitChart`
- `src/stellium/visualization/` - Add transit visualization layers (optional)

### Usage Example

```python
from stellium import ChartBuilder, Native, TransitBuilder
from datetime import datetime

# Create natal chart
native = Native(datetime(1994, 1, 6, 11, 47), "San Francisco, CA")
natal = ChartBuilder.from_native(native).calculate()

# Create transit chart for today
transit_chart = TransitBuilder(natal).for_date(datetime.now()).calculate()

# Get active transits
for aspect in transit_chart.get_active_transits(orb_threshold=1.0):
    print(aspect.description)

# Get all Saturn transits
saturn_transits = transit_chart.get_transits_by_transiting_planet("Saturn")
for transit in saturn_transits:
    print(f"Saturn {transit.aspect_name} natal {transit.object2.name}")
```

---

## PART 2: SYNASTRY

### What Is Synastry?

Synastry compares two natal charts to assess relationship dynamics, compatibility, and interaction patterns.

### Design Approach

#### New Data Models

```python
@dataclass(frozen=True)
class SynastryChart:
    """
    A synastry chart comparing two natal charts.

    Chart1 (person1) aspects → Chart2 (person2)
    Chart2 (person2) aspects → Chart1 (person1)
    """
    chart1: CalculatedChart
    chart2: CalculatedChart
    chart1_name: str = "Person 1"
    chart2_name: str = "Person 2"

    # Cross-chart aspects
    chart1_to_chart2_aspects: tuple[Aspect, ...]  # Person 1 → Person 2
    chart2_to_chart1_aspects: tuple[Aspect, ...]  # Person 2 → Person 1

    # Combined (all cross-chart aspects)
    all_synastry_aspects: tuple[Aspect, ...] = field(init=False)

    def __post_init__(self):
        # Combine aspects from both directions
        all_aspects = list(self.chart1_to_chart2_aspects) + list(self.chart2_to_chart1_aspects)
        object.__setattr__(self, 'all_synastry_aspects', tuple(all_aspects))

    def get_aspects_between(self, planet1: str, planet2: str) -> list[Aspect]:
        """Get aspects between specific planets (both directions)."""
        return [
            a for a in self.all_synastry_aspects
            if (a.object1.name == planet1 and a.object2.name == planet2)
            or (a.object1.name == planet2 and a.object2.name == planet1)
        ]

    def get_chart1_aspects_to_planet(self, chart2_planet: str) -> list[Aspect]:
        """Get all of person1's planets aspecting a specific planet of person2."""
        return [a for a in self.chart1_to_chart2_aspects if a.object2.name == chart2_planet]

    def get_strongest_aspects(self, limit: int = 10) -> list[Aspect]:
        """Get strongest aspects by orb."""
        return sorted(self.all_synastry_aspects, key=lambda a: a.orb)[:limit]

    def get_aspect_score(self) -> dict:
        """
        Calculate overall compatibility score based on aspects.

        Returns:
            Dict with harmonious/challenging counts and overall score
        """
        harmonious = ['Trine', 'Sextile', 'Conjunction']  # Simplified
        challenging = ['Square', 'Opposition']

        harmonious_count = sum(1 for a in self.all_synastry_aspects if a.aspect_name in harmonious)
        challenging_count = sum(1 for a in self.all_synastry_aspects if a.aspect_name in challenging)

        return {
            'harmonious': harmonious_count,
            'challenging': challenging_count,
            'total': len(self.all_synastry_aspects),
            'harmony_ratio': harmonious_count / len(self.all_synastry_aspects) if self.all_synastry_aspects else 0
        }
```

#### New Builder

```python
class SynastryBuilder:
    """Build synastry charts comparing two natal charts."""

    def __init__(self, chart1: CalculatedChart, chart2: CalculatedChart):
        self._chart1 = chart1
        self._chart2 = chart2
        self._chart1_name = "Person 1"
        self._chart2_name = "Person 2"
        self._aspect_engine: AspectEngine = ModernAspectEngine()
        self._orb_engine: OrbEngine = SynastryOrbEngine()

    def with_names(self, name1: str, name2: str) -> "SynastryBuilder":
        """Set names for the two people."""
        self._chart1_name = name1
        self._chart2_name = name2
        return self

    def with_aspects(self, engine: AspectEngine) -> "SynastryBuilder":
        """Custom aspect engine."""
        self._aspect_engine = engine
        return self

    def with_orbs(self, engine: OrbEngine) -> "SynastryBuilder":
        """Custom orb engine."""
        self._orb_engine = engine
        return self

    def calculate(self) -> SynastryChart:
        """Calculate synastry chart."""
        # Calculate aspects: chart1 → chart2
        aspects_1_to_2 = self._calculate_cross_chart_aspects(
            self._chart1.positions,
            self._chart2.positions
        )

        # Calculate aspects: chart2 → chart1
        aspects_2_to_1 = self._calculate_cross_chart_aspects(
            self._chart2.positions,
            self._chart1.positions
        )

        return SynastryChart(
            chart1=self._chart1,
            chart2=self._chart2,
            chart1_name=self._chart1_name,
            chart2_name=self._chart2_name,
            chart1_to_chart2_aspects=tuple(aspects_1_to_2),
            chart2_to_chart1_aspects=tuple(aspects_2_to_1)
        )

    def _calculate_cross_chart_aspects(
        self,
        positions1: tuple[CelestialPosition, ...],
        positions2: tuple[CelestialPosition, ...]
    ) -> list[Aspect]:
        """Calculate aspects between two sets of positions."""
        aspects = []

        for pos1 in positions1:
            for pos2 in positions2:
                # Calculate angle between positions
                angle = abs(pos1.longitude - pos2.longitude)
                if angle > 180:
                    angle = 360 - angle

                # Check each aspect type
                for aspect_info in self._aspect_engine.get_aspect_types():
                    orb = self._orb_engine.get_orb(aspect_info.name, pos1.name, pos2.name)
                    deviation = abs(angle - aspect_info.angle)

                    if deviation <= orb:
                        aspects.append(Aspect(
                            object1=pos1,
                            object2=pos2,
                            aspect_name=aspect_info.name,
                            aspect_degree=aspect_info.angle,
                            orb=deviation
                        ))

        return aspects
```

### Files to Create/Modify

**New files:**

- `src/stellium/synastry/__init__.py`
- `src/stellium/synastry/builder.py` - `SynastryBuilder`
- `src/stellium/synastry/models.py` - `SynastryChart`
- `src/stellium/synastry/orbs.py` - `SynastryOrbEngine`
- `src/stellium/synastry/analysis.py` - Compatibility scoring, etc.
- `tests/test_synastry.py`

**Modified files:**

- `src/stellium/__init__.py` - Export `SynastryBuilder`, `SynastryChart`
- `src/stellium/visualization/drawing.py` - Add `draw_synastry_chart()` for bi-wheel
- `src/stellium/presentation/sections.py` - Add synastry report sections

### Usage Example

```python
from stellium import ChartBuilder, Native, SynastryBuilder

# Create two natal charts
person1 = Native(datetime(1990, 5, 20, 14, 30), "London, UK")
chart1 = ChartBuilder.from_native(person1).calculate()

person2 = Native(datetime(1992, 11, 10, 6, 15), "New York, NY")
chart2 = ChartBuilder.from_native(person2).calculate()

# Create synastry chart
synastry = (SynastryBuilder(chart1, chart2)
    .with_names("Alice", "Bob")
    .calculate())

# Analyze compatibility
score = synastry.get_aspect_score()
print(f"Harmonious aspects: {score['harmonious']}")
print(f"Challenging aspects: {score['challenging']}")

# Find specific aspects
sun_moon_aspects = synastry.get_aspects_between("Sun", "Moon")
for aspect in sun_moon_aspects:
    print(aspect.description)

# Get strongest connections
for aspect in synastry.get_strongest_aspects(limit=5):
    print(aspect.description)
```

---

## PART 3: COMPOSITE

### What Is a Composite Chart?

A composite chart creates a new chart from the midpoints between two people's planetary positions. It represents the relationship itself as an entity.

### Design Approach

#### New Data Models

```python
@dataclass(frozen=True)
class CompositeChart:
    """
    A composite chart created from midpoints of two natal charts.

    The composite represents the relationship itself as an entity,
    calculated by finding the midpoint of each planetary pair.
    """
    chart1: CalculatedChart
    chart2: CalculatedChart
    composite_chart: CalculatedChart  # The midpoint chart
    chart1_name: str = "Person 1"
    chart2_name: str = "Person 2"

    # Location used for composite (usually midpoint, but configurable)
    composite_location: ChartLocation
    composite_datetime: ChartDateTime

    def get_midpoint_for_planet(self, planet_name: str) -> CelestialPosition | None:
        """Get the composite position for a specific planet."""
        return self.composite_chart.get_object(planet_name)

    def compare_to_natal(self, chart_number: int = 1) -> list[tuple[str, float]]:
        """
        Compare composite positions to one of the natal charts.

        Returns list of (planet_name, angular_distance)
        """
        natal = self.chart1 if chart_number == 1 else self.chart2
        comparisons = []

        for planet in self.composite_chart.get_planets():
            natal_planet = natal.get_object(planet.name)
            if natal_planet:
                distance = abs(planet.longitude - natal_planet.longitude)
                if distance > 180:
                    distance = 360 - distance
                comparisons.append((planet.name, distance))

        return comparisons
```

#### New Builder

```python
class CompositeBuilder:
    """Build composite charts from two natal charts."""

    def __init__(self, chart1: CalculatedChart, chart2: CalculatedChart):
        self._chart1 = chart1
        self._chart2 = chart2
        self._chart1_name = "Person 1"
        self._chart2_name = "Person 2"
        self._house_engines: list[HouseSystemEngine] = [PlacidusHouses()]
        self._aspect_engine: AspectEngine | None = None
        self._use_midpoint_location = True  # Calculate geographic midpoint

    def with_names(self, name1: str, name2: str) -> "CompositeBuilder":
        """Set names for the two people."""
        self._chart1_name = name1
        self._chart2_name = name2
        return self

    def with_location(self, location: ChartLocation) -> "CompositeBuilder":
        """Use a specific location instead of geographic midpoint."""
        self._composite_location = location
        self._use_midpoint_location = False
        return self

    def with_house_systems(self, engines: list[HouseSystemEngine]) -> "CompositeBuilder":
        """Set house systems for composite chart."""
        self._house_engines = engines
        return self

    def calculate(self) -> CompositeChart:
        """Calculate composite chart."""
        # 1. Calculate midpoint positions
        composite_positions = []

        for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                       'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
            pos1 = self._chart1.get_object(planet)
            pos2 = self._chart2.get_object(planet)

            if pos1 and pos2:
                midpoint_long = self._calculate_midpoint_longitude(
                    pos1.longitude,
                    pos2.longitude
                )

                # Create midpoint position
                composite_positions.append(CelestialPosition(
                    name=planet,
                    object_type=pos1.object_type,
                    longitude=midpoint_long,
                    # Average other values
                    latitude=(pos1.latitude + pos2.latitude) / 2,
                    distance=(pos1.distance + pos2.distance) / 2,
                ))

        # 2. Calculate composite datetime (midpoint in time)
        jd1 = self._chart1.datetime.julian_day
        jd2 = self._chart2.datetime.julian_day
        composite_jd = (jd1 + jd2) / 2

        # Convert back to datetime
        composite_dt = swe.jdut1_to_utc(composite_jd)
        composite_datetime = ChartDateTime(
            utc_datetime=datetime(*composite_dt[:6], tzinfo=pytz.UTC),
            julian_day=composite_jd
        )

        # 3. Calculate composite location
        if self._use_midpoint_location:
            composite_location = self._calculate_midpoint_location(
                self._chart1.location,
                self._chart2.location
            )
        else:
            composite_location = self._composite_location

        # 4. Calculate houses for composite
        # (Use ChartBuilder with the composite positions)
        # This is a bit tricky - we need to build a full chart from our midpoint positions

        # 5. Calculate aspects within the composite
        if self._aspect_engine:
            aspects = self._aspect_engine.calculate_aspects(composite_positions)
        else:
            aspects = ()

        # 6. Build the composite CalculatedChart
        composite_chart = CalculatedChart(
            datetime=composite_datetime,
            location=composite_location,
            positions=tuple(composite_positions),
            aspects=aspects
        )

        return CompositeChart(
            chart1=self._chart1,
            chart2=self._chart2,
            composite_chart=composite_chart,
            chart1_name=self._chart1_name,
            chart2_name=self._chart2_name,
            composite_location=composite_location,
            composite_datetime=composite_datetime
        )

    def _calculate_midpoint_longitude(self, long1: float, long2: float) -> float:
        """Calculate midpoint between two longitudes (shorter arc)."""
        diff = abs(long1 - long2)

        if diff <= 180:
            # Shorter arc
            return (long1 + long2) / 2
        else:
            # Longer arc - need to cross 0°
            midpoint = ((long1 + long2) / 2 + 180) % 360
            return midpoint

    def _calculate_midpoint_location(
        self,
        loc1: ChartLocation,
        loc2: ChartLocation
    ) -> ChartLocation:
        """Calculate geographic midpoint between two locations."""
        # Simple average (not great-circle distance, but good enough for astrology)
        mid_lat = (loc1.latitude + loc2.latitude) / 2
        mid_long = (loc1.longitude + loc2.longitude) / 2

        return ChartLocation(
            latitude=mid_lat,
            longitude=mid_long,
            name=f"{loc1.name} / {loc2.name}",
            timezone=""  # Composite doesn't need timezone
        )
```

### Files to Create/Modify

**New files:**

- `src/stellium/composite/__init__.py`
- `src/stellium/composite/builder.py` - `CompositeBuilder`
- `src/stellium/composite/models.py` - `CompositeChart`
- `tests/test_composite.py`

**Modified files:**

- `src/stellium/__init__.py` - Export `CompositeBuilder`, `CompositeChart`

### Usage Example

```python
from stellium import ChartBuilder, Native, CompositeBuilder

# Create two natal charts
person1 = Native(datetime(1990, 5, 20, 14, 30), "London, UK")
chart1 = ChartBuilder.from_native(person1).calculate()

person2 = Native(datetime(1992, 11, 10, 6, 15), "New York, NY")
chart2 = ChartBuilder.from_native(person2).calculate()

# Create composite chart
composite = (CompositeBuilder(chart1, chart2)
    .with_names("Alice", "Bob")
    .calculate())

# Access composite positions
composite_sun = composite.get_midpoint_for_planet("Sun")
print(f"Composite Sun: {composite_sun.sign_position}")

# Analyze composite chart
for aspect in composite.composite_chart.aspects:
    print(aspect.description)
```

---

## Implementation Order & Dependencies

### Phase 1: Transits (Recommended First)

**Why first:**

- Simplest to implement
- Only involves comparing one chart to current positions
- Introduces cross-chart aspect calculation (needed for synastry)
- High user value

**Estimated complexity:** Medium
**Estimated time:** 3-5 days

### Phase 2: Synastry

**Why second:**

- Builds on cross-chart aspects from transits
- More complex than transits (two complete charts)
- Requires more sophisticated analysis tools

**Estimated complexity:** Medium-High
**Estimated time:** 5-7 days

### Phase 3: Composite

**Why last:**

- Most complex conceptually
- Requires creating synthetic positions
- Depends on understanding from transit/synastry work

**Estimated complexity:** High
**Estimated time:** 7-10 days

---

## Shared Infrastructure Needed

### 1. Cross-Chart Aspect Calculator

This is needed for both transits and synastry:

```python
# src/stellium/engines/aspects.py

def calculate_aspects_between_charts(
    positions1: tuple[CelestialPosition, ...],
    positions2: tuple[CelestialPosition, ...],
    aspect_engine: AspectEngine,
    orb_engine: OrbEngine
) -> list[Aspect]:
    """
    Calculate aspects between two sets of positions.

    Args:
        positions1: First set of positions (e.g., natal)
        positions2: Second set of positions (e.g., transits)
        aspect_engine: Engine defining which aspects to calculate
        orb_engine: Engine defining orb allowances

    Returns:
        List of aspects from positions1 to positions2
    """
    aspects = []

    for pos1 in positions1:
        for pos2 in positions2:
            angle = calculate_angular_separation(pos1.longitude, pos2.longitude)

            # Check each aspect type
            aspect_infos = ASPECT_REGISTRY.get_aspects_by_category(...)
            for aspect_info in aspect_infos:
                orb = orb_engine.get_orb(aspect_info.name, pos1.name, pos2.name)
                deviation = abs(angle - aspect_info.angle)

                if deviation <= orb:
                    aspects.append(Aspect(
                        object1=pos1,
                        object2=pos2,
                        aspect_name=aspect_info.name,
                        aspect_degree=aspect_info.angle,
                        orb=deviation
                    ))

    return aspects
```

### 2. Specialized Orb Engines

Different orbs for different chart types:

```python
class TransitOrbEngine:
    """Tighter orbs for transits (1-2°)."""
    pass

class SynastryOrbEngine:
    """Moderate orbs for synastry (5-8°)."""
    pass
```

### 3. Visualization Extensions

```python
# src/stellium/visualization/drawing.py

def draw_transit_chart(natal: CalculatedChart, transit: TransitChart, filename: str):
    """Draw natal chart with transit positions in outer ring."""
    pass

def draw_synastry_chart(synastry: SynastryChart, filename: str):
    """Draw bi-wheel synastry chart."""
    pass
```

---

## Testing Strategy

### Unit Tests

- Midpoint calculations (exact vs. longer arc)
- Cross-chart aspect detection
- Orb calculations
- Geographic midpoint calculations

### Integration Tests

- Full transit chart generation
- Full synastry chart generation
- Full composite chart generation
- Cross-chart aspect accuracy

### Example-Based Tests

- Use notable births for reproducible tests
- Compare against astro.com calculations
- Test edge cases (retrograde transits, tight orbs, etc.)

---

## Questions for Discussion

1. **Transits:**
   - Should transits support date ranges (e.g., "all Saturn transits in 2024")?
   - Should we support secondary progressions in the transit module?

2. **Synastry:**
   - Do we want automatic compatibility scoring, or leave that to user?
   - Should synastry include house overlays (person1's planets in person2's houses)?

3. **Composite:**
   - Should we support Davison charts (space-time midpoint) as well as composite?
   - Should composite use derived ASC from midpoint datetime/location, or calculate based on other method?

4. **General:**
   - Should these be separate submodules (`stellium.transits`, `stellium.synastry`) or part of core?
   - Do we want CLI support for these chart types?
   - Priority on visualization or calculation first?

---

## Next Steps

1. **Discuss this plan** - Get feedback and alignment
2. **Choose implementation order** - Transits → Synastry → Composite recommended
3. **Create feature branches** - One per chart type
4. **Write tests first** - TDD approach for complex calculations
5. **Implement incrementally** - Small PRs, continuous integration

Let's discuss! What are your thoughts on this approach?
