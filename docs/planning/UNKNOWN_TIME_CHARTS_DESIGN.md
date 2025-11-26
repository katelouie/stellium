# Unknown Birth Time Charts - Design Document

Created: November 25, 2025
Status: Ready for Implementation

## Overview

Many people know their birth date and location but not their exact birth time. This feature allows Stellium to generate meaningful charts for these users, clearly indicating what is known vs unknown.

## What We Know Without Birth Time

**Accurate (noon calculation is fine):**
- Sun position (~1°/day movement, ±0.5° error)
- Mercury, Venus, Mars positions
- Jupiter, Saturn, Uranus, Neptune, Pluto positions (slow movers)
- Nodes, Chiron, Lilith positions
- All inter-planet aspects

**Unknown:**
- Ascendant / Descendant
- MC / IC
- All house cusps
- Exact Moon position (Moon moves ~12-14° per day!)

**Moon Special Case:**
- Moon could be in one of TWO signs depending on birth time
- Need to calculate and display the full range
- Flag if sign change occurs during the day

## Architecture

### 1. Native Class Update

```python
class Native:
    def __init__(
        self,
        datetime_input,
        location_input,
        *,
        name: str | None = None,
        time_unknown: bool = False
    ):
        self.name = name
        self.time_unknown = time_unknown

        if time_unknown:
            # Force time to noon for calculation
            # Store just the date portion
            self._normalize_to_noon(datetime_input)
```

### 2. ChartBuilder Update

```python
class ChartBuilder:
    def __init__(self):
        # ... existing fields ...
        self._time_unknown: bool = False

    def with_unknown_time(self) -> "ChartBuilder":
        """
        Mark this chart as having unknown birth time.

        Effects:
        - Time set to noon for planet calculations
        - Houses and angles will not be calculated
        - Moon will include range (start/end of day positions)

        Returns:
            Self for chaining
        """
        self._time_unknown = True
        return self

    def calculate(self) -> CalculatedChart:
        if self._time_unknown or (self._native and self._native.time_unknown):
            return self._calculate_unknown_time_chart()
        return self._calculate_normal_chart()
```

### 3. UnknownTimeChart Class

```python
@dataclass
class MoonRange:
    """Moon position range for unknown time charts."""
    start_longitude: float  # Position at 00:00:00
    end_longitude: float    # Position at 23:59:59
    noon_longitude: float   # Position at 12:00:00 (displayed position)
    start_sign: str
    end_sign: str
    crosses_sign_boundary: bool

    @property
    def arc_size(self) -> float:
        """Size of the arc in degrees."""
        # Handle wrap-around at 0°/360°
        if self.end_longitude < self.start_longitude:
            return (360 - self.start_longitude) + self.end_longitude
        return self.end_longitude - self.start_longitude


class UnknownTimeChart(CalculatedChart):
    """
    A natal chart calculated without known birth time.

    Inherits from CalculatedChart for compatibility, but:
    - houses is None (or empty)
    - angles is None (or empty)
    - moon_range provides the Moon's possible positions
    """
    moon_range: MoonRange

    # Override to return None/empty
    @property
    def houses(self) -> None:
        return None

    @property
    def angles(self) -> None:
        return None

    def get_house(self, house_number: int) -> None:
        """Houses are not available for unknown time charts."""
        return None
```

### 4. Visualization Updates

**layers.py - New MoonRangeLayer:**
```python
class MoonRangeLayer:
    """
    Draws shaded arc showing Moon's possible range.

    Visual: Semi-transparent wedge from start to end longitude,
    with Moon glyph positioned at noon longitude.
    """
    def draw(self, ctx, config, chart):
        if not isinstance(chart, UnknownTimeChart):
            return

        moon_range = chart.moon_range
        # Draw shaded arc from start to end
        # Use theme's moon color with alpha
        # Position moon glyph at noon_longitude
```

**layer_factory.py updates:**
- Skip HouseLayer for UnknownTimeChart
- Skip AngleLayer for UnknownTimeChart
- Add MoonRangeLayer for UnknownTimeChart
- PlanetLayer still works, but Moon gets special handling

**ChartInfoLayer updates:**
- Show "Time Unknown" instead of time
- Optionally show Moon range: "Moon: ♏︎ Scorpio 3° - 15°" or "Moon: ♏︎ Scorpio - ♐︎ Sagittarius"

## API Usage

```python
from stellium import ChartBuilder, Native

# Option 1: Flag on Native
native = Native("1994-01-06", "Palo Alto, CA", time_unknown=True)
chart = ChartBuilder.from_native(native).calculate()

# Option 2: Builder method
chart = (ChartBuilder
    .from_details("1994-01-06", "Palo Alto, CA", name="Kate")
    .with_unknown_time()
    .calculate())

# Option 3: Just date string (no time component)
# Could auto-detect? Or require explicit flag?

# Chart is an UnknownTimeChart
assert isinstance(chart, UnknownTimeChart)
assert chart.houses is None
assert chart.moon_range.crosses_sign_boundary == False

# Visualization just works
chart.draw("unknown_time_chart.svg").save()

# Reports handle it gracefully
(ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()  # Shows "Time Unknown"
    .with_planet_positions()  # Shows Moon range
    .render(format="typst", file="report.pdf"))
```

## Implementation Steps

### Phase 1: Core (20-30 min)
1. Add `time_unknown` flag to `Native`
2. Add `with_unknown_time()` to `ChartBuilder`
3. Create `MoonRange` dataclass
4. Create `UnknownTimeChart` class
5. Implement `_calculate_unknown_time_chart()` in builder

### Phase 2: Visualization (20-30 min)
1. Create `MoonRangeLayer` for the shaded arc
2. Update `layer_factory.py` to skip houses/angles for UnknownTimeChart
3. Update `ChartInfoLayer` to show "Time Unknown"
4. Test rendering

### Phase 3: Reports (10 min)
1. Update `ChartOverviewSection` to handle unknown time
2. Update `PlanetPositionSection` to show Moon range
3. Test PDF output

### Phase 4: Tests (15 min)
1. Test moon range calculation (including sign boundary crossing)
2. Test chart creation with both API styles
3. Test visualization output
4. Test report generation

## Visual Design

```
                    Normal Chart              Unknown Time Chart
                    ────────────              ──────────────────
Houses:             12 house lines            None
Angles:             Asc/MC/Dsc/IC marked      None
Moon:               Single glyph + info       Glyph at noon + shaded arc
Chart Info:         "11:47 AM"                "Time Unknown"
Planet positions:   All shown                 All shown (Moon has range)
Aspects:            All calculated            All calculated (using noon Moon)
```

**Moon Arc Visual:**
- Semi-transparent fill in Moon's color (or theme accent)
- Arc spans from day-start longitude to day-end longitude
- Moon glyph sits at noon position
- If sign boundary crossed, maybe two-tone arc?

## Edge Cases

1. **Moon crosses sign boundary** - Flag it clearly, show both signs
2. **Moon crosses 0° Aries** - Handle wrap-around in arc drawing
3. **Polar locations** - Day length varies, but Moon calculation still works
4. **Timezone ambiguity** - Use location's timezone, calculate for local midnight-to-midnight

## Notes for Future-Me

- The noon calculation is standard practice in astrology for unknown times
- Some astrologers use "solar chart" (Sun on Ascendant) as alternative - could add later
- Whole sign houses from Sun is another option - could add as variant
- The shaded arc is the key visual innovation here - make it look good!

---

Ready to build! 🌙
