"""
Longitude search engine for finding when celestial objects reach specific positions.

This module provides efficient search functions for finding exact times when
planets and other celestial objects cross specific zodiac degrees. Uses a hybrid
Newton-Raphson / bisection algorithm for fast, reliable convergence.

Key features:
- Fast convergence using planetary speed from Swiss Ephemeris
- Handles retrograde motion and stations gracefully
- Proper 360°/0° wraparound handling
- Forward and backward search directions
- Find single crossing or all crossings in a date range
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import swisseph as swe

from stellium.engines.ephemeris import SWISS_EPHEMERIS_IDS, _set_ephemeris_path


@dataclass(frozen=True)
class LongitudeCrossing:
    """Result of a longitude search.

    Attributes:
        julian_day: Julian day of the crossing
        datetime_utc: UTC datetime of the crossing
        longitude: Exact longitude at crossing (should be very close to target)
        speed: Longitude speed at crossing (degrees/day, negative = retrograde)
        is_retrograde: True if object was moving retrograde at crossing
        object_name: Name of the celestial object
    """

    julian_day: float
    datetime_utc: datetime
    longitude: float
    speed: float
    is_retrograde: bool
    object_name: str

    @property
    def is_direct(self) -> bool:
        """True if object was moving direct (not retrograde) at crossing."""
        return not self.is_retrograde


def _normalize_angle_error(angle: float) -> float:
    """Normalize angle difference to range [-180, +180].

    This handles the 360°/0° wraparound properly. For example:
    - 359° to 1° is a difference of +2°, not -358°
    - 1° to 359° is a difference of -2°, not +358°

    Args:
        angle: Angle difference in degrees

    Returns:
        Normalized difference in range [-180, +180]
    """
    return ((angle + 180) % 360) - 180


def _get_position_and_speed(object_id: int, julian_day: float) -> tuple[float, float]:
    """Get longitude and speed for an object at a specific time.

    Args:
        object_id: Swiss Ephemeris object ID
        julian_day: Julian day number

    Returns:
        Tuple of (longitude, speed_longitude) in degrees and degrees/day
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = swe.calc_ut(julian_day, object_id, flags)
    return result[0][0], result[0][3]


def _julian_day_to_datetime(jd: float) -> datetime:
    """Convert Julian day to UTC datetime.

    Args:
        jd: Julian day number

    Returns:
        UTC datetime
    """
    year, month, day, hour = swe.revjul(jd)
    # hour is a float, convert to hours, minutes, seconds
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)
    microseconds = int((((hour - hours) * 60 - minutes) * 60 - seconds) * 1_000_000)

    return datetime(year, month, day, hours, minutes, seconds, microseconds)


def _datetime_to_julian_day(dt: datetime) -> float:
    """Convert datetime to Julian day.

    Args:
        dt: Datetime (assumed UTC)

    Returns:
        Julian day number
    """
    hour = dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond / 3_600_000_000
    return swe.julday(dt.year, dt.month, dt.day, hour)


def _bracket_crossing(
    object_id: int,
    target_longitude: float,
    start_jd: float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 366.0,
    step_days: float = 1.0,
) -> tuple[float, float] | None:
    """Find an interval containing a longitude crossing.

    Sweeps through time looking for when the object crosses the target degree.
    Uses careful handling to avoid false positives at target+180° due to
    the angle normalization.

    Args:
        object_id: Swiss Ephemeris object ID
        target_longitude: Target longitude in degrees (0-360)
        start_jd: Julian day to start search from
        direction: "forward" (future) or "backward" (past)
        max_days: Maximum days to search
        step_days: Step size for initial sweep

    Returns:
        Tuple (jd1, jd2) bracketing the crossing, or None if not found
    """
    step = step_days if direction == "forward" else -step_days
    end_jd = start_jd + (max_days if direction == "forward" else -max_days)

    current_jd = start_jd
    current_lon, _ = _get_position_and_speed(object_id, current_jd)
    current_error = _normalize_angle_error(current_lon - target_longitude)

    while (direction == "forward" and current_jd < end_jd) or (
        direction == "backward" and current_jd > end_jd
    ):
        next_jd = current_jd + step
        next_lon, _ = _get_position_and_speed(object_id, next_jd)
        next_error = _normalize_angle_error(next_lon - target_longitude)

        # Check for sign change (potential crossing)
        if current_error * next_error < 0:
            # Verify this is a real crossing at target, not at target+180°
            # A real crossing will have errors that are both small (< 90°)
            # A false crossing at +180° will have errors near ±180°
            if abs(current_error) < 90 and abs(next_error) < 90:
                # Real crossing - return interval in chronological order
                if direction == "forward":
                    return (current_jd, next_jd)
                else:
                    return (next_jd, current_jd)
            # Otherwise it's a false positive from crossing target+180°, skip it

        # Also check if we're very close (within tolerance)
        if abs(next_error) < 0.001:
            # Return a small bracket around this point
            return (next_jd - 0.01, next_jd + 0.01)

        current_jd = next_jd
        current_error = next_error

    return None


def find_longitude_crossing(
    object_name: str,
    target_longitude: float,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 366.0,
    tolerance: float = 0.0001,
    max_iterations: int = 50,
) -> LongitudeCrossing | None:
    """Find when a celestial object crosses a specific longitude.

    Uses a hybrid Newton-Raphson / bisection algorithm:
    1. First brackets the crossing with a coarse sweep
    2. Then refines with Newton-Raphson (fast when speed is good)
    3. Falls back to bisection near stations (speed ≈ 0)

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        target_longitude: Target longitude in degrees (0-360)
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 366 = just over a year)
        tolerance: Convergence tolerance in degrees (default 0.0001 ≈ 0.36 arcsec)
        max_iterations: Maximum refinement iterations

    Returns:
        LongitudeCrossing with exact time, or None if not found

    Example:
        >>> # When does the Sun reach 0° Aries (vernal equinox) after Jan 1, 2024?
        >>> result = find_longitude_crossing("Sun", 0.0, datetime(2024, 1, 1))
        >>> print(result.datetime_utc)  # ~March 20, 2024
    """
    # Ensure ephemeris path is set
    _set_ephemeris_path()

    # Get object ID
    if object_name not in SWISS_EPHEMERIS_IDS:
        raise ValueError(f"Unknown object: {object_name}")
    object_id = SWISS_EPHEMERIS_IDS[object_name]

    # Convert start to Julian day if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    # Normalize target longitude
    target_longitude = target_longitude % 360

    # Phase 1: Bracket the crossing
    bracket = _bracket_crossing(
        object_id, target_longitude, start_jd, direction, max_days
    )

    if bracket is None:
        return None

    t1, t2 = bracket

    # Phase 2: Refine with Newton-Raphson + bisection fallback
    t = (t1 + t2) / 2

    for _ in range(max_iterations):
        lon, speed = _get_position_and_speed(object_id, t)
        error = _normalize_angle_error(lon - target_longitude)

        # Check convergence
        if abs(error) < tolerance:
            return LongitudeCrossing(
                julian_day=t,
                datetime_utc=_julian_day_to_datetime(t),
                longitude=lon,
                speed=speed,
                is_retrograde=speed < 0,
                object_name=object_name,
            )

        # Try Newton-Raphson step if speed is reasonable
        if abs(speed) > 0.01:
            newton_step = -error / speed
            # Clamp step to avoid huge jumps
            newton_step = max(-15, min(15, newton_step))
            t_new = t + newton_step

            # Keep within bracket
            t_new = max(t1, min(t2, t_new))
        else:
            # Bisection fallback when near station
            t_new = (t1 + t2) / 2

        # Update bracket based on error sign
        if error > 0:
            t2 = t
        else:
            t1 = t

        t = t_new

    # Failed to converge - return best estimate
    lon, speed = _get_position_and_speed(object_id, t)
    return LongitudeCrossing(
        julian_day=t,
        datetime_utc=_julian_day_to_datetime(t),
        longitude=lon,
        speed=speed,
        is_retrograde=speed < 0,
        object_name=object_name,
    )


def find_all_longitude_crossings(
    object_name: str,
    target_longitude: float,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 100,
) -> list[LongitudeCrossing]:
    """Find all times a celestial object crosses a specific longitude in a date range.

    Useful for:
    - Finding all Moon transits over a degree (roughly monthly)
    - Finding multiple Mercury crossings during retrograde (up to 3)
    - Building transit timelines

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        target_longitude: Target longitude in degrees (0-360)
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results (default 100)

    Returns:
        List of LongitudeCrossing objects, chronologically ordered

    Example:
        >>> # Find all times Moon crosses 15° Taurus in 2024
        >>> results = find_all_longitude_crossings(
        ...     "Moon", 45.0,  # 15° Taurus
        ...     datetime(2024, 1, 1),
        ...     datetime(2024, 12, 31)
        ... )
        >>> print(f"Moon crosses 15° Taurus {len(results)} times in 2024")
    """
    # Convert to Julian days if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    if isinstance(end, datetime):
        end_jd = _datetime_to_julian_day(end)
    else:
        end_jd = end

    results = []
    current_jd = start_jd

    while current_jd < end_jd and len(results) < max_results:
        # Search forward from current position
        result = find_longitude_crossing(
            object_name,
            target_longitude,
            current_jd,
            direction="forward",
            max_days=end_jd - current_jd + 1,
        )

        if result is None or result.julian_day > end_jd:
            break

        results.append(result)

        # Move past this crossing (small step to avoid finding same one)
        current_jd = result.julian_day + 0.1

    return results
