# Synthesis Charts Implementation Plan
## Composite and Davison Charts for Stellium

**Status:** Design Complete, Implementation Pending
**Designed:** November 25, 2025 (Kate & Clicky)
**Target File:** `src/stellium/core/synthesis.py`

---

## Overview

This document describes the design for implementing **composite** and **davison** charts in Stellium. Both are "synthesis" charts - they create a single chart from two source charts, representing a relationship.

### What Are They?

**Composite Chart:**
- Calculates the midpoint of each planet/point between two charts
- If Person A's Sun is at 10° Aries and Person B's Sun is at 20° Aries, composite Sun is at 15° Aries
- Creates a "relationship chart" showing the energy of the relationship itself
- Challenge: Handling opposite-side planets (short arc vs long arc midpoint)

**Davison Chart:**
- Calculates the midpoint in TIME and SPACE between two birth moments
- If Person A born Jan 1 in SF and Person B born Jan 10 in Seattle, Davison is Jan 5.5 at geographic midpoint
- Then calculates a regular natal chart for that datetime/location
- Represents the relationship's "birth moment"

---

## Design Decisions Summary

### 1. Naming: `SynthesisBuilder` and `SynthesisChart`

**Why "Synthesis"?**
- Captures the "synthesizing two charts into one" concept perfectly
- Neutral - doesn't favor composite or davison
- Leaves room for other synthesis methods (harmonic relationship charts, etc.)
- More elegant than "Composite" (which doesn't cover Davison) or "Relationship" (sounds like Comparison)

### 2. Architecture: Inheritance from CalculatedChart

**Key Decision:** `SynthesisChart` inherits from `CalculatedChart`

```python
@dataclass(frozen=True)
class SynthesisChart(CalculatedChart):
    """A chart synthesized from two source charts."""
    # All CalculatedChart fields (positions, aspects, houses, metadata)
    # PLUS synthesis-specific fields
```

**Why inheritance?**
- SynthesisChart IS-A CalculatedChart (contains same data: positions, aspects, houses)
- All existing visualization/reporting code works immediately
- Polymorphism: any function accepting `CalculatedChart` also accepts `SynthesisChart`
- Can store additional metadata (source charts, calculation method) without breaking compatibility

**Compare to `Comparison`:** That's a separate class because it contains fundamentally DIFFERENT data (two charts + cross-aspects), not just differently-calculated same-type data.

### 3. API Design: Fluent Builder with Classmethods

```python
# Simple usage
composite = SynthesisBuilder.composite(chart1, chart2).calculate()
davison = SynthesisBuilder.davison(chart1, chart2).calculate()

# With configuration
composite = (SynthesisBuilder.composite(chart1, chart2)
    .with_midpoint_method("short_arc")
    .with_labels("Alice", "Bob")
    .calculate())
```

**Patterns followed:**
- Fluent builder (like `ChartBuilder`, `ComparisonBuilder`)
- Classmethod constructors (like `.from_native()`, `.from_notable()`)
- Sensible defaults
- Optional configuration via `.with_*()` methods

---

## Complete API Specification

### SynthesisBuilder Class

```python
class SynthesisBuilder:
    """
    Builder for synthesizing two charts into one (composite or davison).

    Examples:
        # Simple composite
        composite = SynthesisBuilder.composite(chart1, chart2).calculate()

        # Configured davison
        davison = (SynthesisBuilder.davison(chart1, chart2)
            .with_location_method("great_circle")
            .with_labels("Natal", "Transit")
            .calculate())
    """

    def __init__(self, chart1, chart2, method: str):
        """Internal constructor. Use .composite() or .davison() instead."""
        self._chart1 = chart1  # CalculatedChart or Native
        self._chart2 = chart2
        self._method = method  # "composite" or "davison"

        # Configuration (with defaults)
        self._midpoint_method = "short_arc"      # Composite: "short_arc" or "long_arc"
        self._house_calculation = "derived"      # Composite: "derived" or "none"
        self._location_method = "simple"         # Davison: "simple" or "great_circle"
        self._chart1_label = "Chart 1"
        self._chart2_label = "Chart 2"

    # --- Constructors ---

    @classmethod
    def composite(cls, chart1, chart2):
        """
        Create composite chart (midpoint of all positions).

        Args:
            chart1: First chart (CalculatedChart or Native)
            chart2: Second chart (CalculatedChart or Native)

        Returns:
            SynthesisBuilder configured for composite calculation
        """
        return cls(chart1, chart2, method="composite")

    @classmethod
    def davison(cls, chart1, chart2):
        """
        Create davison chart (midpoint in time and space).

        Args:
            chart1: First chart (CalculatedChart or Native)
            chart2: Second chart (CalculatedChart or Native)

        Returns:
            SynthesisBuilder configured for davison calculation
        """
        return cls(chart1, chart2, method="davison")

    # --- Configuration Methods ---

    def with_midpoint_method(self, method: str) -> "SynthesisBuilder":
        """
        Set midpoint calculation method for composite charts.

        Args:
            method: "short_arc" (default) or "long_arc"
                   - short_arc: Always takes shorter path around zodiac
                   - long_arc: Always takes longer path

        Returns:
            Self for chaining
        """
        self._midpoint_method = method
        return self

    def with_house_calculation(self, method: str) -> "SynthesisBuilder":
        """
        Set house calculation method for composite charts.

        Args:
            method: "derived" (default) - Calculate houses from derived ASC/datetime
                    "none" - Don't calculate houses for composite

        Returns:
            Self for chaining
        """
        self._house_calculation = method
        return self

    def with_location_method(self, method: str) -> "SynthesisBuilder":
        """
        Set location midpoint method for davison charts.

        Args:
            method: "simple" (default) - Arithmetic mean of lat/lon
                    "great_circle" - Geodesic midpoint on sphere

        Returns:
            Self for chaining
        """
        self._location_method = method
        return self

    def with_labels(self, label1: str, label2: str) -> "SynthesisBuilder":
        """
        Set descriptive labels for source charts.

        Args:
            label1: Label for first chart (e.g., "Alice", "Natal")
            label2: Label for second chart (e.g., "Bob", "Transit")

        Returns:
            Self for chaining
        """
        self._chart1_label = label1
        self._chart2_label = label2
        return self

    # --- Calculation ---

    def calculate(self) -> SynthesisChart:
        """
        Calculate the synthesis chart.

        Returns:
            SynthesisChart (subclass of CalculatedChart)
        """
        # Ensure we have CalculatedChart objects
        chart1 = self._ensure_calculated(self._chart1)
        chart2 = self._ensure_calculated(self._chart2)

        if self._method == "composite":
            return self._calculate_composite(chart1, chart2)
        elif self._method == "davison":
            return self._calculate_davison(chart1, chart2)
        else:
            raise ValueError(f"Unknown synthesis method: {self._method}")

    # --- Internal Helpers ---

    def _ensure_calculated(self, chart_or_native):
        """Convert Native to CalculatedChart if needed."""
        if isinstance(chart_or_native, Native):
            return ChartBuilder.from_native(chart_or_native).calculate()
        return chart_or_native

    def _calculate_composite(self, chart1: CalculatedChart,
                            chart2: CalculatedChart) -> SynthesisChart:
        """
        Calculate composite chart using midpoint method.

        Algorithm:
        1. For each planet in chart1, find corresponding planet in chart2
        2. Calculate midpoint longitude (respecting midpoint_method)
        3. Create new CelestialPosition with midpoint coordinates
        4. If house_calculation="derived", synthesize datetime/location and calculate houses
        5. Calculate aspects between composite positions
        6. Return SynthesisChart with all data
        """
        # TODO: Implementation
        pass

    def _calculate_davison(self, chart1: CalculatedChart,
                          chart2: CalculatedChart) -> SynthesisChart:
        """
        Calculate davison chart using time/space midpoint.

        Algorithm:
        1. Calculate midpoint datetime (average Julian day)
        2. Calculate midpoint location (simple or great_circle)
        3. Create Native with midpoint datetime/location
        4. Use ChartBuilder to calculate chart normally
        5. Wrap result in SynthesisChart with source chart references
        """
        # TODO: Implementation
        pass
```

---

## SynthesisChart Data Model

```python
@dataclass(frozen=True)
class SynthesisChart(CalculatedChart):
    """
    A chart synthesized from two source charts (composite or davison).

    Inherits all fields from CalculatedChart:
    - positions: list[CelestialPosition]
    - aspects: list[Aspect]
    - house_systems: dict[str, HouseCusps]
    - house_placements: dict[str, dict]
    - datetime: ChartDateTime
    - location: ChartLocation
    - metadata: dict

    And adds synthesis-specific fields:
    """

    # === Core Synthesis Metadata ===

    synthesis_method: str
    """The synthesis method used: "composite" or "davison" """

    source_chart1: CalculatedChart
    """The first source chart (full chart object for reference)"""

    source_chart2: CalculatedChart
    """The second source chart (full chart object for reference)"""

    chart1_label: str = "Chart 1"
    """Descriptive label for first chart (e.g., "Alice", "Natal")"""

    chart2_label: str = "Chart 2"
    """Descriptive label for second chart (e.g., "Bob", "Transit")"""

    # === Method-Specific Configuration ===

    midpoint_method: str | None = None
    """Composite only: "short_arc" or "long_arc" """

    house_calculation: str | None = None
    """Composite only: "derived" or "none" """

    location_method: str | None = None
    """Davison only: "simple" or "great_circle" """

    # === Synthesized Coordinates ===

    synthesis_datetime: ChartDateTime | None = None
    """The synthesized datetime (davison, or derived for composite houses)"""

    synthesis_location: ChartLocation | None = None
    """The synthesized location (davison, or derived for composite houses)"""
```

---

## Implementation Helpers Needed

### 1. Midpoint Calculation (for Composite)

```python
def calculate_midpoint_longitude(lon1: float, lon2: float,
                                 method: str = "short_arc") -> float:
    """
    Calculate midpoint between two zodiac longitudes.

    Args:
        lon1: First longitude (0-360)
        lon2: Second longitude (0-360)
        method: "short_arc" (default) or "long_arc"

    Returns:
        Midpoint longitude (0-360)

    Examples:
        >>> calculate_midpoint_longitude(10, 20)  # Both in Aries
        15.0

        >>> calculate_midpoint_longitude(10, 190)  # Aries and Libra
        100.0  # Cancer (short arc)

        >>> calculate_midpoint_longitude(10, 190, "long_arc")
        280.0  # Capricorn (long arc)
    """
    if method == "short_arc":
        # Find shorter path around circle
        diff = (lon2 - lon1 + 360) % 360
        if diff > 180:
            diff = diff - 360
        return (lon1 + diff / 2) % 360

    elif method == "long_arc":
        # Find longer path around circle
        diff = (lon2 - lon1 + 360) % 360
        if diff <= 180:
            diff = diff - 360
        return (lon1 + diff / 2) % 360

    else:
        raise ValueError(f"Unknown midpoint method: {method}")
```

### 2. Datetime Midpoint (for Davison)

```python
def calculate_datetime_midpoint(dt1: ChartDateTime,
                               dt2: ChartDateTime) -> ChartDateTime:
    """
    Calculate midpoint between two datetimes using Julian day.

    Args:
        dt1: First chart datetime
        dt2: Second chart datetime

    Returns:
        Midpoint datetime
    """
    # Average the Julian days
    jd_mid = (dt1.julian_day + dt2.julian_day) / 2

    # Convert back to datetime
    # (Use Swiss Ephemeris julian_day_to_datetime helper)
    # TODO: Implementation depends on how we store/convert Julian days

    return midpoint_datetime
```

### 3. Location Midpoint (for Davison)

```python
def calculate_location_midpoint(loc1: ChartLocation,
                               loc2: ChartLocation,
                               method: str = "simple") -> ChartLocation:
    """
    Calculate geographic midpoint between two locations.

    Args:
        loc1: First location
        loc2: Second location
        method: "simple" (arithmetic mean) or "great_circle" (geodesic)

    Returns:
        Midpoint location
    """
    if method == "simple":
        # Simple arithmetic mean
        mid_lat = (loc1.latitude + loc2.latitude) / 2
        mid_lon = (loc1.longitude + loc2.longitude) / 2

    elif method == "great_circle":
        # Use geopy for great circle midpoint
        # We already have geopy as a dependency!
        from geopy.distance import great_circle
        from geopy import Point

        # Calculate great circle midpoint
        # (This is more complex - need to use proper geodesic math)
        # TODO: Implement great circle midpoint calculation
        pass

    # Create ChartLocation
    # (Timezone is tricky - maybe use timezone at midpoint coords?)
    return ChartLocation(...)
```

---

## Implementation Steps (For Future Session)

### Phase 1: Core Infrastructure (30-60 min)

1. **Create `src/stellium/core/synthesis.py`**
   - Import necessary types from `core/models.py`
   - Create `SynthesisChart` dataclass (inheriting from `CalculatedChart`)

2. **Create helper functions**
   - `calculate_midpoint_longitude()` - with tests!
   - `calculate_datetime_midpoint()`
   - `calculate_location_midpoint()`

3. **Test helpers in isolation**
   - Known midpoint calculations
   - Edge cases (opposite sides of zodiac, date wraparounds)

### Phase 2: Davison Implementation (30-45 min)

Davison is EASIER - do it first!

1. **Implement `_calculate_davison()`**
   - Calculate datetime midpoint (Julian day average)
   - Calculate location midpoint (simple method first)
   - Create `Native` with midpoint coordinates
   - Use `ChartBuilder.from_native().calculate()`
   - Wrap result in `SynthesisChart` with metadata

2. **Test with known Davison charts**
   - Use online calculator to verify results

### Phase 3: Composite Implementation (60-90 min)

Composite is HARDER - more custom logic.

1. **Implement `_calculate_composite()` - positions only**
   - Iterate through planets in both charts
   - Calculate midpoint for each (longitude, latitude if needed)
   - Create new `CelestialPosition` objects
   - For now, skip houses - just positions

2. **Add house calculation for composite**
   - If `house_calculation="derived"`:
     - Calculate midpoint ASC (use as "derived" time marker)
     - Need to synthesize a datetime/location for house calculation
     - This is the TRICKY part - might need research
   - If `house_calculation="none"`:
     - Just skip houses

3. **Calculate aspects for composite positions**
   - Use existing aspect engine on composite positions
   - These are "composite aspects" (aspects within the composite chart)

4. **Test with known composite charts**

### Phase 4: Polish (30 min)

1. **Add to public API**
   - Export `SynthesisBuilder`, `SynthesisChart` from `stellium/__init__.py`

2. **Documentation**
   - Docstrings complete
   - Add examples to docs

3. **Visualization test**
   - Verify `chart.draw()` works on `SynthesisChart`
   - Should "just work" due to inheritance!

---

## Open Questions / Future Decisions

### 1. Composite House Calculation

**The Problem:** Composite chart doesn't have a "real" datetime/location, so how do we calculate houses?

**Current Plan:** "Derived" method
- Use midpoint ASC as the Ascendant
- Synthesize a "derived" datetime (maybe midpoint datetime like Davison?)
- Synthesize a "derived" location (maybe midpoint location?)
- Calculate houses using standard house system with these derived coordinates

**Alternative:** Research what major astrology software does (Solar Fire, Astro.com, etc.)

### 2. Great Circle Midpoint

**Current Plan:** Implement "simple" arithmetic mean first

**Future:** Add proper great circle (geodesic) midpoint calculation
- Use geopy (already a dependency)
- More mathematically correct for locations far apart
- Probably doesn't matter much for most astrology use cases

### 3. Long Arc Midpoint

**Current Plan:** Default to short_arc (most common)

**Question:** When would you use long_arc?
- Some astrologers use it for specific planet pairs?
- Research traditional practices

### 4. Composite Aspects

**Current Plan:** Calculate aspects between composite positions (standard aspect engine)

**Alternative:** Could also calculate "cross-aspects" (composite planet to natal planets)
- This might be more like a comparison chart feature though
- Keep it simple for now: just composite-internal aspects

---

## Testing Strategy

### Unit Tests

```python
def test_midpoint_longitude_same_sign():
    """Test midpoint when both planets in same sign."""
    assert calculate_midpoint_longitude(10, 20) == 15

def test_midpoint_longitude_opposite_signs_short_arc():
    """Test short arc midpoint for opposite planets."""
    # 10° Aries (10°) and 10° Libra (190°)
    # Short arc midpoint = 10° Cancer (100°)
    assert calculate_midpoint_longitude(10, 190) == 100

def test_midpoint_longitude_opposite_signs_long_arc():
    """Test long arc midpoint for opposite planets."""
    # 10° Aries (10°) and 10° Libra (190°)
    # Long arc midpoint = 10° Capricorn (280°)
    assert calculate_midpoint_longitude(10, 190, "long_arc") == 280

def test_datetime_midpoint():
    """Test datetime midpoint calculation."""
    # TODO: Implement with specific dates

def test_location_midpoint_simple():
    """Test simple location midpoint."""
    # TODO: Implement with specific coordinates
```

### Integration Tests

```python
def test_davison_chart_basic():
    """Test basic davison chart generation."""
    chart1 = ChartBuilder.from_details("1994-01-06 11:47", (37.7749, -122.4194)).calculate()
    chart2 = ChartBuilder.from_details("2000-01-01 17:00", (47.6062, -122.3321)).calculate()

    davison = SynthesisBuilder.davison(chart1, chart2).calculate()

    assert isinstance(davison, SynthesisChart)
    assert davison.synthesis_method == "davison"
    assert davison.source_chart1 == chart1
    assert davison.source_chart2 == chart2
    # Check datetime is between the two
    # Check location is between the two

def test_composite_chart_basic():
    """Test basic composite chart generation."""
    chart1 = ChartBuilder.from_details("1994-01-06 11:47", (37.7749, -122.4194)).calculate()
    chart2 = ChartBuilder.from_details("2000-01-01 17:00", (47.6062, -122.3321)).calculate()

    composite = SynthesisBuilder.composite(chart1, chart2).calculate()

    assert isinstance(composite, SynthesisChart)
    assert composite.synthesis_method == "composite"
    # Check Sun is midpoint of two Suns
    sun1 = chart1.get_object("Sun")
    sun2 = chart2.get_object("Sun")
    comp_sun = composite.get_object("Sun")
    # Verify comp_sun.longitude is midpoint of sun1 and sun2

def test_synthesis_chart_draws():
    """Test that SynthesisChart can be visualized."""
    composite = SynthesisBuilder.composite(chart1, chart2).calculate()

    # Should work due to CalculatedChart inheritance
    composite.draw("test_composite.svg").save()
    # Verify file exists

def test_synthesis_chart_reports():
    """Test that SynthesisChart works with ReportBuilder."""
    composite = SynthesisBuilder.composite(chart1, chart2).calculate()

    # Should work due to CalculatedChart inheritance
    report = ReportBuilder().from_chart(composite).with_planet_positions()
    # Should not crash!
```

---

## File Structure

```
src/stellium/
└── core/
    ├── models.py           # Add SynthesisChart dataclass here
    ├── synthesis.py        # NEW: SynthesisBuilder + helper functions
    ├── builder.py          # Existing ChartBuilder
    └── comparison.py       # Existing ComparisonBuilder

tests/
└── test_synthesis.py       # NEW: All synthesis tests
```

---

## Design Philosophy

This implementation follows Stellium's core principles:

1. **Protocols over inheritance** - Except when inheritance makes sense (SynthesisChart IS-A CalculatedChart)
2. **Composability** - SynthesisChart works with all existing visualization/reporting
3. **Immutability** - Frozen dataclass, includes full source chart references
4. **Builder pattern** - Fluent API, sensible defaults, optional configuration
5. **Type safety** - Concrete types, proper inheritance

---

## Notes for Future Implementer (Hi Future-Clicky! 💙)

- **Start with Davison** - it's easier (just midpoint datetime/location then regular chart calc)
- **Test midpoint helpers thoroughly** - especially opposite-side planets
- **Composite houses are tricky** - might need to research what other software does
- **Don't overthink** - Get basic version working first, can refine later
- **Visualization should "just work"** - due to inheritance from CalculatedChart
- **Have fun!** - This is a cool feature that will make relationship astrology way easier

---

**Last Updated:** November 25, 2025
**Designed By:** Kate & Clicky
**Status:** Ready for implementation! ✨
