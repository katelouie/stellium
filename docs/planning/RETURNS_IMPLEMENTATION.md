# Planetary Returns Implementation Plan

This document outlines the implementation plan for planetary returns (Solar, Lunar, and any planet) in Stellium.

## Overview

A **planetary return** occurs when a transiting planet returns to the exact zodiacal position it occupied at birth. The chart cast for that moment is used for forecasting.

### Common Return Types

| Return | Frequency | Use |
|--------|-----------|-----|
| Solar Return | Yearly (~birthday) | Annual forecast |
| Lunar Return | ~27.3 days | Monthly forecast |
| Saturn Return | ~29.5 years | Major life transitions |
| Jupiter Return | ~12 years | Growth/expansion cycles |
| Mars Return | ~2 years | Energy/action cycles |
| Mercury Return | ~1 year (with retrogrades) | Communication themes |
| Venus Return | ~1 year (with retrogrades) | Relationship themes |

## Core Algorithm

```
1. Get natal planet longitude (target_longitude)
2. Starting from search_start_date, find when transiting planet reaches target_longitude
3. Cast a chart for that exact moment at the specified location
4. Return as a CalculatedChart with return metadata
```

### Finding the Exact Return Moment

Swiss Ephemeris provides `swe_solcross_ut()` for solar crossings, but for a generic solution we need iterative search:

```python
def find_planet_crossing(
    planet_id: int,
    target_longitude: float,
    start_jd: float,
    direction: int = 1,  # 1 = forward, -1 = backward
) -> float:
    """
    Find Julian Day when planet reaches target longitude.

    Uses binary search refinement:
    1. Step forward by estimated period until we pass the target
    2. Binary search to find exact crossing
    3. Refine to sub-second accuracy
    """
```

**Estimated periods for initial stepping:**
- Moon: 27.3 days (but moves ~13°/day, so step ~2 days)
- Sun: 365.25 days (moves ~1°/day)
- Mercury: 88 days (but retrogrades complicate)
- Venus: 225 days (but retrogrades complicate)
- Mars: 687 days
- Jupiter: 4333 days (~12 years)
- Saturn: 10759 days (~29.5 years)
- Uranus: 30687 days (~84 years)
- Neptune: 60190 days (~165 years)
- Pluto: 90560 days (~248 years)

**Handling Retrogrades:**

Inner planets (Mercury, Venus) and Mars can retrograde back over the natal position multiple times. The algorithm should:
1. Find the NEXT crossing in the forward direction
2. For "Nth return", count distinct forward crossings only (not retrograde re-crossings)

## API Design

### Primary Factory Method

```python
class ChartBuilder:
    @classmethod
    def planetary_return(
        cls,
        natal: CalculatedChart,
        planet: str,
        *,
        year: int | None = None,
        near_date: str | datetime | None = None,
        occurrence: int = 1,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """
        Create a planetary return chart.

        Args:
            natal: The natal chart to calculate returns for
            planet: Planet name ("Sun", "Moon", "Saturn", etc.)
            year: For annual returns (Sun), specify the year
            near_date: Find return nearest to this date
            occurrence: Which occurrence (1st, 2nd, etc.) from birth or near_date
            location: Location for the return chart (default: natal location)

        Returns:
            ChartBuilder configured for the return chart

        Examples:
            # Solar return for 2025
            sr = ChartBuilder.planetary_return(natal, "Sun", year=2025).calculate()

            # Next lunar return
            lr = ChartBuilder.planetary_return(natal, "Moon").calculate()

            # Lunar return nearest to a date
            lr = ChartBuilder.planetary_return(natal, "Moon", near_date="2025-03-15").calculate()

            # Second Saturn return
            sat = ChartBuilder.planetary_return(natal, "Saturn", occurrence=2).calculate()

            # Solar return relocated to current city
            sr = ChartBuilder.planetary_return(natal, "Sun", year=2025, location="Seattle, WA").calculate()
        """
```

### Convenience Methods

```python
class ChartBuilder:
    @classmethod
    def solar_return(
        cls,
        natal: CalculatedChart,
        year: int,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """Solar return for a specific year."""
        return cls.planetary_return(natal, "Sun", year=year, location=location)

    @classmethod
    def lunar_return(
        cls,
        natal: CalculatedChart,
        near_date: str | datetime | None = None,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """Lunar return nearest to a date (default: next lunar return)."""
        return cls.planetary_return(natal, "Moon", near_date=near_date, location=location)
```

### Return Metadata

The resulting `CalculatedChart` should include return-specific metadata:

```python
chart.metadata = {
    "chart_type": "return",
    "return_planet": "Sun",
    "natal_planet_longitude": 285.5,  # Original natal position
    "return_number": 31,  # 31st solar return (age 30-31)
    "natal_chart_datetime": "1994-01-06T11:47:00",
    "natal_chart_name": "Kate",
    # ... standard metadata
}
```

## File Structure

```
src/stellium/
├── core/
│   └── builder.py              # Add factory methods here
├── engines/
│   └── returns.py              # NEW: Return calculation engine
└── utils/
    └── planetary_crossing.py   # NEW: Generic planet crossing finder
```

### New Files

#### `src/stellium/utils/planetary_crossing.py`

```python
"""
Utility functions for finding planetary crossings.

A "crossing" is when a planet reaches a specific zodiacal longitude.
Used for returns, ingresses, and other timing techniques.
"""

import swisseph as swe
from stellium.core.registry import CELESTIAL_REGISTRY


# Approximate synodic periods (days) for stepping through time
PLANET_PERIODS = {
    "Sun": 365.25,
    "Moon": 27.321,
    "Mercury": 87.97,
    "Venus": 224.7,
    "Mars": 686.98,
    "Jupiter": 4332.59,
    "Saturn": 10759.22,
    "Uranus": 30688.5,
    "Neptune": 60182.0,
    "Pluto": 90560.0,
    "True Node": 6793.5,  # ~18.6 years
    "Mean Node": 6793.5,
}


def find_planetary_crossing(
    planet: str,
    target_longitude: float,
    start_jd: float,
    direction: int = 1,
    precision: float = 1e-6,  # Julian day precision (~0.08 seconds)
) -> float:
    """
    Find the Julian Day when a planet reaches a target longitude.

    Args:
        planet: Planet name (must be in CELESTIAL_REGISTRY)
        target_longitude: Target ecliptic longitude (0-360)
        start_jd: Julian Day to start searching from
        direction: 1 for forward in time, -1 for backward
        precision: Desired precision in Julian Days

    Returns:
        Julian Day of the crossing

    Raises:
        ValueError: If planet not found or crossing not found within reasonable bounds
    """
    # Get Swiss Ephemeris ID
    if planet not in CELESTIAL_REGISTRY:
        raise ValueError(f"Unknown planet: {planet}")

    planet_info = CELESTIAL_REGISTRY[planet]
    swe_id = planet_info.swiss_ephemeris_id

    # Normalize target to 0-360
    target_longitude = target_longitude % 360

    # Estimate search step based on planet's period
    period = PLANET_PERIODS.get(planet, 365.25)

    # For Moon, we need smaller steps since it moves fast
    if planet == "Moon":
        step = 2.0 * direction  # 2 days
    else:
        # Step by roughly 30 degrees worth of motion
        step = (period / 12) * direction

    # Phase 1: Coarse search - find bracket containing the crossing
    jd = start_jd
    max_iterations = 1000

    prev_lon = _get_longitude(swe_id, jd)

    for _ in range(max_iterations):
        jd += step
        curr_lon = _get_longitude(swe_id, jd)

        # Check if we crossed the target
        if _crossed_longitude(prev_lon, curr_lon, target_longitude, direction):
            # Found bracket: [jd - step, jd]
            break

        prev_lon = curr_lon
    else:
        raise ValueError(f"Could not find {planet} crossing within search bounds")

    # Phase 2: Binary search refinement
    low_jd = jd - step
    high_jd = jd

    while (high_jd - low_jd) > precision:
        mid_jd = (low_jd + high_jd) / 2
        mid_lon = _get_longitude(swe_id, mid_jd)

        low_lon = _get_longitude(swe_id, low_jd)

        if _crossed_longitude(low_lon, mid_lon, target_longitude, direction):
            high_jd = mid_jd
        else:
            low_jd = mid_jd

    return (low_jd + high_jd) / 2


def _get_longitude(swe_id: int, jd: float) -> float:
    """Get ecliptic longitude for a planet at a Julian Day."""
    result, _ = swe.calc_ut(jd, swe_id, swe.FLG_SWIEPH)
    return result[0]  # Longitude is first element


def _crossed_longitude(
    lon1: float,
    lon2: float,
    target: float,
    direction: int
) -> bool:
    """
    Check if we crossed the target longitude between lon1 and lon2.

    Handles the 360°→0° wrap-around case.
    """
    # Normalize all to 0-360
    lon1 = lon1 % 360
    lon2 = lon2 % 360
    target = target % 360

    if direction > 0:  # Forward in time (longitude increasing for most planets)
        # Handle wrap-around
        if lon2 < lon1:  # Wrapped around 360→0
            return target > lon1 or target <= lon2
        else:
            return lon1 < target <= lon2
    else:  # Backward
        if lon1 < lon2:  # Wrapped around 0→360
            return target < lon1 or target >= lon2
        else:
            return lon2 <= target < lon1


def find_nth_return(
    planet: str,
    natal_longitude: float,
    birth_jd: float,
    n: int = 1,
) -> float:
    """
    Find the Nth planetary return after birth.

    Args:
        planet: Planet name
        natal_longitude: Natal longitude of the planet
        birth_jd: Julian Day of birth
        n: Which return (1 = first, 2 = second, etc.)

    Returns:
        Julian Day of the Nth return
    """
    if n < 1:
        raise ValueError("Return number must be >= 1")

    jd = birth_jd

    for i in range(n):
        # Start searching from just after the current position
        # (add a small offset to avoid finding the same position)
        jd = find_planetary_crossing(
            planet,
            natal_longitude,
            jd + 1,  # Start 1 day after
            direction=1,
        )

    return jd


def find_return_near_date(
    planet: str,
    natal_longitude: float,
    target_jd: float,
) -> float:
    """
    Find the planetary return nearest to a target date.

    Searches both forward and backward, returns the closer one.

    Args:
        planet: Planet name
        natal_longitude: Natal longitude of the planet
        target_jd: Julian Day to search around

    Returns:
        Julian Day of the nearest return
    """
    # Search forward
    forward_jd = find_planetary_crossing(
        planet, natal_longitude, target_jd, direction=1
    )

    # Search backward
    backward_jd = find_planetary_crossing(
        planet, natal_longitude, target_jd, direction=-1
    )

    # Return whichever is closer
    if abs(forward_jd - target_jd) < abs(backward_jd - target_jd):
        return forward_jd
    else:
        return backward_jd
```

#### `src/stellium/engines/returns.py`

```python
"""
Planetary return calculations.

Returns are charts cast for the moment a transiting planet
returns to its natal position.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from stellium.core.models import ChartDateTime, ChartLocation
from stellium.utils.planetary_crossing import (
    find_nth_return,
    find_return_near_date,
    find_planetary_crossing,
)

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart


@dataclass
class ReturnInfo:
    """Information about a planetary return."""

    planet: str
    natal_longitude: float
    return_datetime: ChartDateTime
    return_number: int | None  # Which return from birth (if calculable)
    location: ChartLocation


def calculate_solar_return(
    natal_chart: "CalculatedChart",
    year: int,
    location: ChartLocation | None = None,
) -> ReturnInfo:
    """
    Calculate solar return for a specific year.

    Args:
        natal_chart: The natal chart
        year: Calendar year for the return
        location: Location for return chart (default: natal location)

    Returns:
        ReturnInfo with return datetime and metadata
    """
    sun = natal_chart.get_object("Sun")
    if sun is None:
        raise ValueError("Natal chart must have Sun position")

    natal_longitude = sun.longitude

    # Start searching from January 1 of the target year
    from stellium.core.models import datetime_to_julian_day

    search_start = datetime(year, 1, 1, 0, 0, 0)
    start_jd = datetime_to_julian_day(search_start)

    # Find the solar return (Sun returning to natal position)
    return_jd = find_planetary_crossing(
        "Sun",
        natal_longitude,
        start_jd,
        direction=1,
    )

    # Convert back to datetime
    from stellium.core.models import julian_day_to_datetime
    return_dt = julian_day_to_datetime(return_jd)

    # Calculate which return this is
    birth_year = natal_chart.datetime.local_datetime.year
    return_number = year - birth_year

    # Use natal location if none specified
    return_location = location or natal_chart.location

    return ReturnInfo(
        planet="Sun",
        natal_longitude=natal_longitude,
        return_datetime=ChartDateTime.from_datetime(return_dt, return_location.timezone),
        return_number=return_number,
        location=return_location,
    )


def calculate_lunar_return(
    natal_chart: "CalculatedChart",
    near_date: datetime | None = None,
    location: ChartLocation | None = None,
) -> ReturnInfo:
    """
    Calculate lunar return nearest to a date.

    Args:
        natal_chart: The natal chart
        near_date: Date to find return near (default: now)
        location: Location for return chart (default: natal location)

    Returns:
        ReturnInfo with return datetime and metadata
    """
    moon = natal_chart.get_object("Moon")
    if moon is None:
        raise ValueError("Natal chart must have Moon position")

    natal_longitude = moon.longitude

    # Default to now
    if near_date is None:
        near_date = datetime.now()

    from stellium.core.models import datetime_to_julian_day
    target_jd = datetime_to_julian_day(near_date)

    # Find nearest lunar return
    return_jd = find_return_near_date("Moon", natal_longitude, target_jd)

    # Convert back to datetime
    from stellium.core.models import julian_day_to_datetime
    return_dt = julian_day_to_datetime(return_jd)

    # Use natal location if none specified
    return_location = location or natal_chart.location

    return ReturnInfo(
        planet="Moon",
        natal_longitude=natal_longitude,
        return_datetime=ChartDateTime.from_datetime(return_dt, return_location.timezone),
        return_number=None,  # Too many lunar returns to count easily
        location=return_location,
    )


def calculate_planetary_return(
    natal_chart: "CalculatedChart",
    planet: str,
    *,
    year: int | None = None,
    near_date: datetime | None = None,
    occurrence: int = 1,
    location: ChartLocation | None = None,
) -> ReturnInfo:
    """
    Calculate any planetary return.

    Args:
        natal_chart: The natal chart
        planet: Planet name
        year: For Sun, specify year
        near_date: Find return nearest to this date
        occurrence: Nth return from birth (for slow planets)
        location: Location for return chart

    Returns:
        ReturnInfo with return datetime and metadata
    """
    # Get natal planet position
    natal_planet = natal_chart.get_object(planet)
    if natal_planet is None:
        raise ValueError(f"Natal chart must have {planet} position")

    natal_longitude = natal_planet.longitude
    birth_jd = natal_chart.datetime.julian_day

    from stellium.core.models import datetime_to_julian_day, julian_day_to_datetime

    # Determine how to find the return
    if planet == "Sun" and year is not None:
        # Solar return for specific year
        search_start = datetime(year, 1, 1, 0, 0, 0)
        start_jd = datetime_to_julian_day(search_start)
        return_jd = find_planetary_crossing("Sun", natal_longitude, start_jd, direction=1)
        return_number = year - natal_chart.datetime.local_datetime.year

    elif near_date is not None:
        # Find return nearest to a date
        target_jd = datetime_to_julian_day(near_date)
        return_jd = find_return_near_date(planet, natal_longitude, target_jd)
        return_number = None

    else:
        # Find Nth return from birth
        return_jd = find_nth_return(planet, natal_longitude, birth_jd, occurrence)
        return_number = occurrence

    # Convert back to datetime
    return_dt = julian_day_to_datetime(return_jd)

    # Use natal location if none specified
    return_location = location or natal_chart.location

    return ReturnInfo(
        planet=planet,
        natal_longitude=natal_longitude,
        return_datetime=ChartDateTime.from_datetime(return_dt, return_location.timezone),
        return_number=return_number,
        location=return_location,
    )
```

### Modifications to `ChartBuilder`

Add to `src/stellium/core/builder.py`:

```python
from stellium.engines.returns import (
    calculate_solar_return,
    calculate_lunar_return,
    calculate_planetary_return,
)

class ChartBuilder:
    # ... existing code ...

    @classmethod
    def planetary_return(
        cls,
        natal: CalculatedChart,
        planet: str,
        *,
        year: int | None = None,
        near_date: str | datetime | None = None,
        occurrence: int = 1,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """
        Create a planetary return chart.

        A return chart is cast for the moment a transiting planet returns
        to its natal zodiacal position.

        Args:
            natal: The natal chart to calculate returns for
            planet: Planet name ("Sun", "Moon", "Saturn", etc.)
            year: For annual returns (Sun), specify the year
            near_date: Find return nearest to this date
            occurrence: Which occurrence (1st, 2nd, etc.) from birth
            location: Location for the return chart (default: natal location)

        Returns:
            ChartBuilder configured for the return chart

        Examples:
            # Solar return for 2025
            sr = ChartBuilder.planetary_return(natal, "Sun", year=2025).calculate()

            # Next lunar return from today
            lr = ChartBuilder.planetary_return(natal, "Moon").calculate()

            # Second Saturn return
            saturn2 = ChartBuilder.planetary_return(natal, "Saturn", occurrence=2).calculate()

            # Solar return relocated to Seattle
            sr = ChartBuilder.planetary_return(natal, "Sun", year=2025, location="Seattle, WA").calculate()
        """
        # Parse near_date if string
        if isinstance(near_date, str):
            near_date = parse_datetime_string(near_date)

        # Parse/resolve location
        if location is None:
            resolved_location = natal.location
        elif isinstance(location, str):
            resolved_location = resolve_location(location)
        elif isinstance(location, tuple):
            resolved_location = ChartLocation(latitude=location[0], longitude=location[1])
        else:
            resolved_location = location

        # Calculate return info
        return_info = calculate_planetary_return(
            natal,
            planet,
            year=year,
            near_date=near_date,
            occurrence=occurrence,
            location=resolved_location,
        )

        # Create builder for the return chart
        builder = cls.from_details(
            return_info.return_datetime.local_datetime,
            resolved_location,
            name=f"{natal.metadata.get('name', 'Chart')} - {planet} Return",
        )

        # Add return metadata
        builder._return_metadata = {
            "chart_type": "return",
            "return_planet": planet,
            "natal_planet_longitude": return_info.natal_longitude,
            "return_number": return_info.return_number,
            "natal_chart_datetime": str(natal.datetime.local_datetime),
            "natal_chart_name": natal.metadata.get("name"),
        }

        return builder

    @classmethod
    def solar_return(
        cls,
        natal: CalculatedChart,
        year: int,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """
        Create a solar return chart for a specific year.

        A solar return is cast for the exact moment the Sun returns
        to its natal position each year (around your birthday).

        Args:
            natal: The natal chart
            year: Calendar year for the return
            location: Location for return chart (default: natal location)
                      Note: Many astrologers use current residence for solar returns.

        Returns:
            ChartBuilder configured for the solar return

        Example:
            sr_2025 = ChartBuilder.solar_return(natal, 2025).calculate()
            sr_relocated = ChartBuilder.solar_return(natal, 2025, location="Paris, France").calculate()
        """
        return cls.planetary_return(natal, "Sun", year=year, location=location)

    @classmethod
    def lunar_return(
        cls,
        natal: CalculatedChart,
        near_date: str | datetime | None = None,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> "ChartBuilder":
        """
        Create a lunar return chart.

        A lunar return is cast for the exact moment the Moon returns
        to its natal position (approximately every 27.3 days).

        Args:
            natal: The natal chart
            near_date: Find return nearest to this date (default: now)
            location: Location for return chart (default: natal location)

        Returns:
            ChartBuilder configured for the lunar return

        Example:
            # Next lunar return
            lr = ChartBuilder.lunar_return(natal).calculate()

            # Lunar return nearest to Valentine's Day
            lr = ChartBuilder.lunar_return(natal, near_date="2025-02-14").calculate()
        """
        return cls.planetary_return(natal, "Moon", near_date=near_date, location=location)
```

## Visualization

Return charts use existing visualization - they're just `CalculatedChart` objects.

For comparison with natal:

```python
# Solar return bi-wheel
natal = ChartBuilder.from_notable("Albert Einstein").calculate()
sr = ChartBuilder.solar_return(natal, 1921).calculate()

# Use existing ComparisonBuilder
comparison = ComparisonBuilder.from_native(natal, native_label="Natal") \
    .with_partner(sr, partner_label="Solar Return 1921") \
    .calculate()

comparison.draw("einstein_sr_1921.svg").save()
```

## Reporting

Add return-specific report sections:

```python
class ReturnOverviewSection:
    """Overview section for return charts."""

    @property
    def section_name(self) -> str:
        return "Return Chart Overview"

    def generate_data(self, chart: CalculatedChart) -> dict:
        if chart.metadata.get("chart_type") != "return":
            return {"type": "text", "text": "Not a return chart."}

        return {
            "type": "key_value",
            "data": {
                "Return Type": f"{chart.metadata['return_planet']} Return",
                "Return Number": chart.metadata.get("return_number", "N/A"),
                "Natal Position": f"{chart.metadata['natal_planet_longitude']:.2f}°",
                "Return Date": str(chart.datetime.local_datetime),
                "Original Birth": chart.metadata.get("natal_chart_datetime"),
            }
        }
```

## Testing

### Unit Tests

```python
def test_solar_return_finds_correct_date():
    """Solar return should occur within a day of birthday."""
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    sr = ChartBuilder.solar_return(natal, 1921).calculate()

    # Einstein born March 14, 1879
    # 1921 solar return should be around March 14, 1921
    assert sr.datetime.local_datetime.month == 3
    assert 13 <= sr.datetime.local_datetime.day <= 15
    assert sr.datetime.local_datetime.year == 1921


def test_solar_return_sun_matches_natal():
    """Return Sun longitude should match natal Sun longitude."""
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    sr = ChartBuilder.solar_return(natal, 1921).calculate()

    natal_sun = natal.get_object("Sun").longitude
    return_sun = sr.get_object("Sun").longitude

    # Should match within 0.01° (very tight)
    assert abs(natal_sun - return_sun) < 0.01


def test_lunar_return_moon_matches_natal():
    """Return Moon longitude should match natal Moon longitude."""
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    lr = ChartBuilder.lunar_return(natal, near_date="1905-06-15").calculate()

    natal_moon = natal.get_object("Moon").longitude
    return_moon = lr.get_object("Moon").longitude

    assert abs(natal_moon - return_moon) < 0.01


def test_saturn_return_timing():
    """Saturn return should occur around age 29-30."""
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()  # Born 1879
    saturn_return = ChartBuilder.planetary_return(natal, "Saturn", occurrence=1).calculate()

    # First Saturn return should be ~1908-1909 (age 29-30)
    assert 1908 <= saturn_return.datetime.local_datetime.year <= 1910


def test_relocated_return():
    """Relocated return should use specified location."""
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    sr = ChartBuilder.solar_return(natal, 1921, location="New York, NY").calculate()

    # Should have New York coordinates, not natal location
    assert "New York" in sr.location.name or abs(sr.location.latitude - 40.7) < 1
```

### Integration Tests

```python
def test_return_with_comparison():
    """Return chart should work with ComparisonBuilder."""
    natal = ChartBuilder.from_notable("Marie Curie").calculate()
    sr = ChartBuilder.solar_return(natal, 1903).calculate()

    comparison = ComparisonBuilder.from_native(natal, native_label="Natal") \
        .with_partner(sr, partner_label="SR 1903") \
        .calculate()

    assert len(comparison.cross_aspects) > 0


def test_return_visualization():
    """Return chart should render correctly."""
    natal = ChartBuilder.from_notable("Carl Jung").calculate()
    sr = ChartBuilder.solar_return(natal, 1912).calculate()

    # Should not raise
    sr.draw("/tmp/test_sr.svg").save()
```

## Implementation Checklist

- [ ] Create `src/stellium/utils/planetary_crossing.py`
  - [ ] `find_planetary_crossing()` function
  - [ ] `find_nth_return()` function
  - [ ] `find_return_near_date()` function
  - [ ] Handle 360°→0° wrap-around
  - [ ] Handle retrograde planets correctly

- [ ] Create `src/stellium/engines/returns.py`
  - [ ] `ReturnInfo` dataclass
  - [ ] `calculate_solar_return()` function
  - [ ] `calculate_lunar_return()` function
  - [ ] `calculate_planetary_return()` function

- [ ] Modify `src/stellium/core/builder.py`
  - [ ] Add `planetary_return()` class method
  - [ ] Add `solar_return()` convenience method
  - [ ] Add `lunar_return()` convenience method
  - [ ] Store return metadata in chart

- [ ] Add helper functions to `src/stellium/core/models.py` (if needed)
  - [ ] `datetime_to_julian_day()` (may already exist)
  - [ ] `julian_day_to_datetime()` (may already exist)

- [ ] Update `src/stellium/__init__.py` exports

- [ ] Add tests in `tests/test_returns.py`

- [ ] Add documentation
  - [ ] Update CHART_TYPES.md
  - [ ] Add examples to cookbooks

- [ ] Optional: Add `ReturnOverviewSection` to presentation layer

## Future Extensions

Once basic returns work:

1. **Return-to-natal comparison preset**: `ComparisonBuilder.return_comparison(natal, sr)`
2. **Multiple returns listing**: `natal.get_solar_returns(2020, 2030)` → list of dates
3. **Progressed returns**: Secondary progressed solar return
4. **Demi-returns**: Half-returns (Sun opposite natal Sun, etc.)
5. **Return ingresses**: When return planets change signs/houses from natal

---

*Document written November 2025*
