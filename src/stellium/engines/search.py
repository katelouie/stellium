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

# Sign boundaries in longitude (0° of each sign)
SIGN_BOUNDARIES = {
    "Aries": 0.0,
    "Taurus": 30.0,
    "Gemini": 60.0,
    "Cancer": 90.0,
    "Leo": 120.0,
    "Virgo": 150.0,
    "Libra": 180.0,
    "Scorpio": 210.0,
    "Sagittarius": 240.0,
    "Capricorn": 270.0,
    "Aquarius": 300.0,
    "Pisces": 330.0,
}

SIGN_ORDER = list(SIGN_BOUNDARIES.keys())


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


@dataclass(frozen=True)
class SignIngress:
    """Result of a sign ingress search.

    Attributes:
        julian_day: Julian day of the ingress
        datetime_utc: UTC datetime of the ingress
        object_name: Name of the celestial object
        sign: Sign being entered
        from_sign: Sign being left
        longitude: Exact longitude at ingress (should be very close to 0° of sign)
        speed: Longitude speed at ingress (degrees/day, negative = retrograde)
        is_retrograde: True if object was moving retrograde at ingress
    """

    julian_day: float
    datetime_utc: datetime
    object_name: str
    sign: str
    from_sign: str
    longitude: float
    speed: float
    is_retrograde: bool

    @property
    def is_direct(self) -> bool:
        """True if object was moving direct (not retrograde) at ingress."""
        return not self.is_retrograde

    def __str__(self) -> str:
        direction = "Rx" if self.is_retrograde else ""
        return (
            f"{self.object_name} {direction}enters {self.sign} "
            f"on {self.datetime_utc.strftime('%Y-%m-%d %H:%M')}"
        )


@dataclass(frozen=True)
class Station:
    """Result of a planetary station search.

    A station occurs when a planet's apparent motion changes direction -
    either from direct to retrograde, or retrograde to direct.

    Attributes:
        julian_day: Julian day of the station
        datetime_utc: UTC datetime of the station
        object_name: Name of the celestial object
        station_type: "retrograde" (turning Rx) or "direct" (turning D)
        longitude: Longitude at the station (planet "hovers" here)
        sign: Zodiac sign of the station
    """

    julian_day: float
    datetime_utc: datetime
    object_name: str
    station_type: Literal["retrograde", "direct"]
    longitude: float
    sign: str

    @property
    def is_turning_retrograde(self) -> bool:
        """True if planet is turning retrograde (was direct, now Rx)."""
        return self.station_type == "retrograde"

    @property
    def is_turning_direct(self) -> bool:
        """True if planet is turning direct (was Rx, now direct)."""
        return self.station_type == "direct"

    @property
    def degree_in_sign(self) -> float:
        """Degree within the sign (0-30)."""
        return self.longitude % 30

    def __str__(self) -> str:
        degree = int(self.degree_in_sign)
        minute = int((self.degree_in_sign - degree) * 60)
        return (
            f"{self.object_name} stations {self.station_type} "
            f"at {degree}°{minute:02d}' {self.sign} "
            f"on {self.datetime_utc.strftime('%Y-%m-%d %H:%M')}"
        )


# Aspect angle to name mapping
ASPECT_ANGLES = {
    0.0: "conjunction",
    60.0: "sextile",
    90.0: "square",
    120.0: "trine",
    180.0: "opposition",
}


@dataclass(frozen=True)
class AspectExact:
    """Result of an aspect exactitude search.

    Represents the exact moment when two celestial objects form a precise
    aspect (conjunction, sextile, square, trine, or opposition).

    Attributes:
        julian_day: Julian day when aspect is exact
        datetime_utc: UTC datetime when aspect is exact
        object1_name: First object name
        object2_name: Second object name
        aspect_angle: The aspect angle (0=conjunction, 60=sextile, etc.)
        aspect_name: Human name ("conjunction", "trine", etc.)
        object1_longitude: First object's longitude at exact
        object2_longitude: Second object's longitude at exact
        is_applying_before: True if aspect was applying before exact
    """

    julian_day: float
    datetime_utc: datetime
    object1_name: str
    object2_name: str
    aspect_angle: float
    aspect_name: str
    object1_longitude: float
    object2_longitude: float
    is_applying_before: bool

    @property
    def separation(self) -> float:
        """Angular separation between the two objects (should be ~aspect_angle)."""
        diff = abs(self.object2_longitude - self.object1_longitude)
        if diff > 180:
            diff = 360 - diff
        return diff

    def __str__(self) -> str:
        return (
            f"{self.object1_name} {self.aspect_name} {self.object2_name} exact "
            f"on {self.datetime_utc.strftime('%Y-%m-%d %H:%M')}"
        )


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


# =============================================================================
# Sign Ingress Search Functions
# =============================================================================


def _get_sign_from_longitude(longitude: float) -> str:
    """Get the zodiac sign for a given longitude."""
    sign_index = int(longitude // 30) % 12
    return SIGN_ORDER[sign_index]


def _get_previous_sign(sign: str) -> str:
    """Get the sign before the given sign."""
    index = SIGN_ORDER.index(sign)
    return SIGN_ORDER[(index - 1) % 12]


def find_ingress(
    object_name: str,
    sign: str,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 730.0,
) -> SignIngress | None:
    """Find when a celestial object next enters a specific zodiac sign.

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        sign: Target zodiac sign (e.g., "Aries", "Taurus")
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 730 = ~2 years)

    Returns:
        SignIngress with exact time of ingress, or None if not found

    Example:
        >>> # When does Mars next enter Aries?
        >>> result = find_ingress("Mars", "Aries", datetime(2024, 1, 1))
        >>> print(result)  # Mars enters Aries on 2024-04-30 12:34
    """
    if sign not in SIGN_BOUNDARIES:
        raise ValueError(
            f"Unknown sign: {sign}. Must be one of {list(SIGN_BOUNDARIES.keys())}"
        )

    target_longitude = SIGN_BOUNDARIES[sign]

    crossing = find_longitude_crossing(
        object_name,
        target_longitude,
        start,
        direction=direction,
        max_days=max_days,
    )

    if crossing is None:
        return None

    from_sign = _get_previous_sign(sign)

    return SignIngress(
        julian_day=crossing.julian_day,
        datetime_utc=crossing.datetime_utc,
        object_name=object_name,
        sign=sign,
        from_sign=from_sign,
        longitude=crossing.longitude,
        speed=crossing.speed,
        is_retrograde=crossing.is_retrograde,
    )


def find_all_ingresses(
    object_name: str,
    sign: str,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 50,
) -> list[SignIngress]:
    """Find all times a celestial object enters a specific sign in a date range.

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        sign: Target zodiac sign (e.g., "Aries", "Taurus")
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results (default 50)

    Returns:
        List of SignIngress objects, chronologically ordered

    Example:
        >>> # Find all Mars ingresses to Aries in the next 10 years
        >>> results = find_all_ingresses(
        ...     "Mars", "Aries",
        ...     datetime(2024, 1, 1),
        ...     datetime(2034, 1, 1)
        ... )
        >>> print(f"Mars enters Aries {len(results)} times")
    """
    if sign not in SIGN_BOUNDARIES:
        raise ValueError(
            f"Unknown sign: {sign}. Must be one of {list(SIGN_BOUNDARIES.keys())}"
        )

    target_longitude = SIGN_BOUNDARIES[sign]
    from_sign = _get_previous_sign(sign)

    crossings = find_all_longitude_crossings(
        object_name,
        target_longitude,
        start,
        end,
        max_results=max_results,
    )

    return [
        SignIngress(
            julian_day=c.julian_day,
            datetime_utc=c.datetime_utc,
            object_name=object_name,
            sign=sign,
            from_sign=from_sign,
            longitude=c.longitude,
            speed=c.speed,
            is_retrograde=c.is_retrograde,
        )
        for c in crossings
    ]


def find_next_sign_change(
    object_name: str,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 60.0,
) -> SignIngress | None:
    """Find when a celestial object next changes signs (enters any sign).

    This is useful for questions like "when does this transit end?" where
    you don't care which sign is entered, just when the object leaves
    its current sign.

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 60)

    Returns:
        SignIngress with exact time of sign change, or None if not found

    Example:
        >>> # When does Mars leave its current sign?
        >>> result = find_next_sign_change("Mars", datetime(2024, 1, 15))
        >>> print(f"Mars enters {result.sign} on {result.datetime_utc}")
    """
    _set_ephemeris_path()

    if object_name not in SWISS_EPHEMERIS_IDS:
        raise ValueError(f"Unknown object: {object_name}")

    # Get current position to find current sign
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    object_id = SWISS_EPHEMERIS_IDS[object_name]
    current_lon, _ = _get_position_and_speed(object_id, start_jd)
    current_sign = _get_sign_from_longitude(current_lon)

    # Determine which sign boundary to search for
    if direction == "forward":
        # Next sign
        next_sign_index = (SIGN_ORDER.index(current_sign) + 1) % 12
        target_sign = SIGN_ORDER[next_sign_index]
    else:
        # Previous sign boundary (entering current sign from before)
        target_sign = current_sign

    return find_ingress(
        object_name,
        target_sign,
        start,
        direction=direction,
        max_days=max_days,
    )


def find_all_sign_changes(
    object_name: str,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 100,
) -> list[SignIngress]:
    """Find all sign changes for a celestial object in a date range.

    Args:
        object_name: Name of celestial object (e.g., "Sun", "Mars", "Moon")
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results (default 100)

    Returns:
        List of SignIngress objects, chronologically ordered

    Example:
        >>> # Find all Mercury sign changes in 2024
        >>> results = find_all_sign_changes(
        ...     "Mercury",
        ...     datetime(2024, 1, 1),
        ...     datetime(2024, 12, 31)
        ... )
        >>> for r in results:
        ...     print(f"{r.datetime_utc.date()}: Mercury enters {r.sign}")
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
        # Find next sign change
        ingress = find_next_sign_change(
            object_name,
            current_jd,
            direction="forward",
            max_days=end_jd - current_jd + 1,
        )

        if ingress is None or ingress.julian_day > end_jd:
            break

        results.append(ingress)

        # Move past this ingress
        current_jd = ingress.julian_day + 0.1

    return results


# =============================================================================
# Planetary Station Search Functions
# =============================================================================


def _bracket_station(
    object_id: int,
    start_jd: float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 400.0,
    step_days: float = 1.0,
) -> tuple[float, float, str] | None:
    """Find an interval containing a planetary station.

    Sweeps through time looking for when the planet's speed changes sign.

    Args:
        object_id: Swiss Ephemeris object ID
        start_jd: Julian day to start search from
        direction: "forward" (future) or "backward" (past)
        max_days: Maximum days to search
        step_days: Step size for initial sweep

    Returns:
        Tuple (jd1, jd2, station_type) bracketing the station, or None if not found.
        station_type is "retrograde" if speed goes + to -, "direct" if - to +
    """
    step = step_days if direction == "forward" else -step_days
    end_jd = start_jd + (max_days if direction == "forward" else -max_days)

    current_jd = start_jd
    _, current_speed = _get_position_and_speed(object_id, current_jd)

    while (direction == "forward" and current_jd < end_jd) or (
        direction == "backward" and current_jd > end_jd
    ):
        next_jd = current_jd + step
        _, next_speed = _get_position_and_speed(object_id, next_jd)

        # Check for sign change in speed
        if current_speed * next_speed < 0:
            # Determine station type based on direction of speed change
            if current_speed > 0 and next_speed < 0:
                station_type = "retrograde"  # Turning Rx
            else:
                station_type = "direct"  # Turning D

            # Return interval in chronological order
            if direction == "forward":
                return (current_jd, next_jd, station_type)
            else:
                return (next_jd, current_jd, station_type)

        current_jd = next_jd
        current_speed = next_speed

    return None


def _refine_station(
    object_id: int,
    jd1: float,
    jd2: float,
    tolerance: float = 0.0001,
    max_iterations: int = 50,
) -> tuple[float, float]:
    """Refine a station time using bisection.

    Args:
        object_id: Swiss Ephemeris object ID
        jd1: Lower bound of bracket
        jd2: Upper bound of bracket
        tolerance: Convergence tolerance in degrees/day
        max_iterations: Maximum iterations

    Returns:
        Tuple of (julian_day, longitude) at the station
    """
    for _ in range(max_iterations):
        mid_jd = (jd1 + jd2) / 2
        lon, speed = _get_position_and_speed(object_id, mid_jd)

        # Check convergence (speed very close to zero)
        if abs(speed) < tolerance:
            return mid_jd, lon

        # Get speeds at boundaries to determine which half contains the zero
        _, speed1 = _get_position_and_speed(object_id, jd1)

        # If speed1 and mid_speed have same sign, zero is in upper half
        if speed1 * speed > 0:
            jd1 = mid_jd
        else:
            jd2 = mid_jd

    # Return best estimate
    mid_jd = (jd1 + jd2) / 2
    lon, _ = _get_position_and_speed(object_id, mid_jd)
    return mid_jd, lon


def find_station(
    object_name: str,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 400.0,
) -> Station | None:
    """Find the next planetary station (retrograde or direct).

    A station occurs when a planet appears to stop moving and reverse
    direction. This is an important timing point in astrology.

    Note: Sun and Moon do not have stations (they don't go retrograde).

    Args:
        object_name: Name of celestial object (e.g., "Mercury", "Mars")
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 400, > 1 year for outer planets)

    Returns:
        Station with exact time and details, or None if not found

    Example:
        >>> # When does Mercury next station?
        >>> result = find_station("Mercury", datetime(2024, 1, 1))
        >>> print(result)  # Mercury stations retrograde at 4°51' Capricorn on 2024-04-01
    """
    _set_ephemeris_path()

    if object_name not in SWISS_EPHEMERIS_IDS:
        raise ValueError(f"Unknown object: {object_name}")

    # Sun and Moon don't station
    if object_name in ("Sun", "Moon"):
        raise ValueError(
            f"{object_name} does not have stations (never goes retrograde)"
        )

    object_id = SWISS_EPHEMERIS_IDS[object_name]

    # Convert start to Julian day if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    # Phase 1: Bracket the station
    bracket = _bracket_station(object_id, start_jd, direction, max_days)

    if bracket is None:
        return None

    jd1, jd2, station_type = bracket

    # Phase 2: Refine with bisection
    station_jd, longitude = _refine_station(object_id, jd1, jd2)

    sign = _get_sign_from_longitude(longitude)

    return Station(
        julian_day=station_jd,
        datetime_utc=_julian_day_to_datetime(station_jd),
        object_name=object_name,
        station_type=station_type,
        longitude=longitude,
        sign=sign,
    )


def find_all_stations(
    object_name: str,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 50,
) -> list[Station]:
    """Find all planetary stations in a date range.

    Args:
        object_name: Name of celestial object (e.g., "Mercury", "Mars")
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results (default 50)

    Returns:
        List of Station objects, chronologically ordered

    Example:
        >>> # Find all Mercury stations in 2024
        >>> results = find_all_stations(
        ...     "Mercury",
        ...     datetime(2024, 1, 1),
        ...     datetime(2024, 12, 31)
        ... )
        >>> for r in results:
        ...     print(r)
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
        station = find_station(
            object_name,
            current_jd,
            direction="forward",
            max_days=end_jd - current_jd + 1,
        )

        if station is None or station.julian_day > end_jd:
            break

        results.append(station)

        # Move past this station (use larger step since stations are months apart)
        current_jd = station.julian_day + 5.0

    return results


# =============================================================================
# Aspect Exactitude Search Functions
# =============================================================================


def _get_aspect_separation(
    obj1_id: int, obj2_id: int, julian_day: float
) -> tuple[float, float, float, float, float]:
    """Get angular separation and speeds for two objects.

    Args:
        obj1_id: Swiss Ephemeris ID for first object
        obj2_id: Swiss Ephemeris ID for second object
        julian_day: Julian day number

    Returns:
        Tuple of (separation, obj1_lon, obj2_lon, obj1_speed, obj2_speed)
        Separation is in range [0, 180]
    """
    lon1, speed1 = _get_position_and_speed(obj1_id, julian_day)
    lon2, speed2 = _get_position_and_speed(obj2_id, julian_day)

    # Calculate separation (always positive, 0-180)
    diff = (lon2 - lon1) % 360
    if diff > 180:
        diff = 360 - diff

    return diff, lon1, lon2, speed1, speed2


def _bracket_aspect(
    obj1_id: int,
    obj2_id: int,
    aspect_angle: float,
    start_jd: float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 366.0,
    step_days: float = 0.5,
) -> tuple[float, float] | None:
    """Find an interval containing an aspect exactitude.

    Sweeps through time looking for when the angular separation equals the aspect angle.

    Args:
        obj1_id: Swiss Ephemeris ID for first object
        obj2_id: Swiss Ephemeris ID for second object
        aspect_angle: Target aspect angle (0, 60, 90, 120, 180)
        start_jd: Julian day to start search from
        direction: "forward" (future) or "backward" (past)
        max_days: Maximum days to search
        step_days: Step size for initial sweep

    Returns:
        Tuple (jd1, jd2) bracketing the aspect exactitude, or None if not found
    """
    step = step_days if direction == "forward" else -step_days
    end_jd = start_jd + (max_days if direction == "forward" else -max_days)

    current_jd = start_jd
    sep, _, _, _, _ = _get_aspect_separation(obj1_id, obj2_id, current_jd)

    # For aspects, we need to handle both directions of approach
    # e.g., for a trine (120°), separation could approach from below or above
    # Use signed error relative to target
    current_error = _normalize_angle_error(sep - aspect_angle)

    # Track previous values for local minimum detection (needed for conjunctions)
    prev_jd = None
    prev_error = None

    while (direction == "forward" and current_jd < end_jd) or (
        direction == "backward" and current_jd > end_jd
    ):
        next_jd = current_jd + step
        sep, _, _, _, _ = _get_aspect_separation(obj1_id, obj2_id, next_jd)
        next_error = _normalize_angle_error(sep - aspect_angle)

        # Check for sign change (potential crossing)
        if current_error * next_error < 0:
            # Verify this is a real crossing, not a 180° wraparound artifact
            if abs(current_error) < 90 and abs(next_error) < 90:
                # Real crossing - return interval in chronological order
                if direction == "forward":
                    return (current_jd, next_jd)
                else:
                    return (next_jd, current_jd)

        # For conjunctions (aspect_angle ≈ 0), separation is always positive [0, 180]
        # so we need to detect local minima instead of sign changes
        # A local minimum occurs when: prev_error > current_error and current_error < next_error
        if aspect_angle < 1.0 and prev_error is not None:
            # Using abs() since for 0° aspect, error = separation which is non-negative
            if abs(prev_error) > abs(current_error) < abs(next_error):
                # Found local minimum at current_jd, bracket it
                if direction == "forward":
                    return (prev_jd, next_jd)
                else:
                    return (next_jd, prev_jd)

        # Also check if we're very close (within tolerance)
        if abs(next_error) < 0.01:
            return (next_jd - 0.1, next_jd + 0.1)

        prev_jd = current_jd
        prev_error = current_error
        current_jd = next_jd
        current_error = next_error

    return None


def find_aspect_exact(
    object1_name: str,
    object2_name: str,
    aspect_angle: float,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 366.0,
    tolerance: float = 0.0001,
    max_iterations: int = 50,
) -> AspectExact | None:
    """Find when two objects form an exact aspect.

    Uses a hybrid Newton-Raphson / bisection algorithm to find the precise
    moment when two celestial objects reach a specific angular separation.

    Args:
        object1_name: First object (e.g., "Moon", "Sun", "Mars")
        object2_name: Second object (e.g., "Jupiter", "Venus")
        aspect_angle: Target angle in degrees (0=conjunction, 60=sextile,
            90=square, 120=trine, 180=opposition)
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 366 = just over a year)
        tolerance: Convergence tolerance in degrees (default 0.0001 ≈ 0.36 arcsec)
        max_iterations: Maximum refinement iterations

    Returns:
        AspectExact with exact timing, or None if not found

    Example:
        >>> # Find next exact Moon trine Jupiter
        >>> result = find_aspect_exact("Moon", "Jupiter", 120.0, datetime(2024, 1, 1))
        >>> print(f"Exact trine at {result.datetime_utc}")

        >>> # Find next Mercury-Venus conjunction
        >>> result = find_aspect_exact("Mercury", "Venus", 0.0, datetime(2024, 1, 1))
        >>> print(result)
    """
    _set_ephemeris_path()

    # Get object IDs
    if object1_name not in SWISS_EPHEMERIS_IDS:
        raise ValueError(f"Unknown object: {object1_name}")
    if object2_name not in SWISS_EPHEMERIS_IDS:
        raise ValueError(f"Unknown object: {object2_name}")

    obj1_id = SWISS_EPHEMERIS_IDS[object1_name]
    obj2_id = SWISS_EPHEMERIS_IDS[object2_name]

    # Convert start to Julian day if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    # Normalize aspect angle
    aspect_angle = aspect_angle % 180  # Aspects are symmetric

    # Get aspect name
    aspect_name = ASPECT_ANGLES.get(aspect_angle, f"{aspect_angle}°")

    # Phase 1: Bracket the aspect exactitude
    bracket = _bracket_aspect(
        obj1_id, obj2_id, aspect_angle, start_jd, direction, max_days
    )

    if bracket is None:
        return None

    t1, t2 = bracket

    # Check if aspect was applying before exact (for the result)
    sep_before, _, _, speed1_before, speed2_before = _get_aspect_separation(
        obj1_id, obj2_id, t1
    )
    relative_speed_before = speed2_before - speed1_before
    # If obj2 is moving faster, separation is increasing (separating) if positive
    # For applying, we want separation decreasing toward exact
    error_before = _normalize_angle_error(sep_before - aspect_angle)
    is_applying_before = (error_before < 0 and relative_speed_before > 0) or (
        error_before > 0 and relative_speed_before < 0
    )

    # Phase 2: Refine with Newton-Raphson + bisection/golden section fallback
    # For conjunctions (aspect_angle ≈ 0), we search for minimum separation
    # For other aspects, we search for zero crossing
    use_minimum_search = aspect_angle < 1.0

    t = (t1 + t2) / 2

    for _ in range(max_iterations):
        sep, lon1, lon2, speed1, speed2 = _get_aspect_separation(obj1_id, obj2_id, t)
        error = _normalize_angle_error(sep - aspect_angle)

        # Check convergence
        if abs(error) < tolerance:
            return AspectExact(
                julian_day=t,
                datetime_utc=_julian_day_to_datetime(t),
                object1_name=object1_name,
                object2_name=object2_name,
                aspect_angle=aspect_angle,
                aspect_name=aspect_name,
                object1_longitude=lon1,
                object2_longitude=lon2,
                is_applying_before=is_applying_before,
            )

        # Calculate relative speed for Newton-Raphson
        # The derivative of separation w.r.t. time is approximately (speed2 - speed1)
        # but we need to account for the sign of the error
        relative_speed = speed2 - speed1

        # Adjust sign based on how separation relates to error
        # When separation > aspect_angle, error > 0
        # We want to move in direction that decreases error
        if abs(relative_speed) > 0.01:
            newton_step = -error / relative_speed
            # Clamp step to avoid huge jumps
            newton_step = max(-10, min(10, newton_step))
            t_new = t + newton_step

            # Keep within bracket
            t_new = max(t1, min(t2, t_new))
        else:
            # Bisection/golden section fallback when relative speed is very small
            t_new = (t1 + t2) / 2

        # Update bracket
        if use_minimum_search:
            # For conjunctions, use golden section search for minimum
            # Compare errors at bracket endpoints and midpoint to narrow
            sep1, _, _, _, _ = _get_aspect_separation(obj1_id, obj2_id, t1)
            sep2, _, _, _, _ = _get_aspect_separation(obj1_id, obj2_id, t2)
            error1 = abs(sep1 - aspect_angle)
            error2 = abs(sep2 - aspect_angle)

            # Shrink bracket toward the side with smaller error
            if error1 < error2:
                t2 = t  # Keep t1, shrink from right
            else:
                t1 = t  # Keep t2, shrink from left
        else:
            # For other aspects, use bisection based on error sign
            if error > 0:
                t2 = t
            else:
                t1 = t

        t = t_new

    # Failed to converge - return best estimate
    sep, lon1, lon2, _, _ = _get_aspect_separation(obj1_id, obj2_id, t)
    return AspectExact(
        julian_day=t,
        datetime_utc=_julian_day_to_datetime(t),
        object1_name=object1_name,
        object2_name=object2_name,
        aspect_angle=aspect_angle,
        aspect_name=aspect_name,
        object1_longitude=lon1,
        object2_longitude=lon2,
        is_applying_before=is_applying_before,
    )


def find_all_aspect_exacts(
    object1_name: str,
    object2_name: str,
    aspect_angle: float,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 100,
) -> list[AspectExact]:
    """Find all exact aspects between two objects in a date range.

    Useful for:
    - Finding all Moon-Jupiter trines in a year
    - Tracking Mercury-Venus aspects for relationship timing
    - Building aspect timelines

    Args:
        object1_name: First object (e.g., "Moon", "Sun", "Mars")
        object2_name: Second object (e.g., "Jupiter", "Venus")
        aspect_angle: Target angle in degrees (0, 60, 90, 120, 180)
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results (default 100)

    Returns:
        List of AspectExact objects, chronologically ordered

    Example:
        >>> # Find all Moon trine Jupiter in 2024
        >>> results = find_all_aspect_exacts(
        ...     "Moon", "Jupiter", 120.0,
        ...     datetime(2024, 1, 1),
        ...     datetime(2024, 12, 31)
        ... )
        >>> print(f"Found {len(results)} exact trines")
        >>> for r in results[:5]:
        ...     print(r)
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
        result = find_aspect_exact(
            object1_name,
            object2_name,
            aspect_angle,
            current_jd,
            direction="forward",
            max_days=end_jd - current_jd + 1,
        )

        if result is None or result.julian_day > end_jd:
            break

        results.append(result)

        # Move past this aspect (small step to avoid finding same one)
        # For Moon aspects, they recur ~monthly, so 1 day is safe
        current_jd = result.julian_day + 1.0

    return results


# =============================================================================
# Angle Crossing Search Functions
# =============================================================================

# Angle name to index mapping for ascmc array from swe.houses_ex()
ANGLE_INDICES = {
    "ASC": 0,
    "Ascendant": 0,
    "MC": 1,
    "Midheaven": 1,
    "DSC": 0,  # DSC = ASC + 180°
    "Descendant": 0,
    "IC": 1,  # IC = MC + 180°
    "Imum Coeli": 1,
}

# Angles that need 180° offset
OPPOSITE_ANGLES = {"DSC", "Descendant", "IC", "Imum Coeli"}


def _get_angle_longitude(
    julian_day: float, latitude: float, longitude: float, angle: str
) -> float:
    """Get the longitude of a chart angle at a given time.

    Args:
        julian_day: Julian day number
        latitude: Geographic latitude
        longitude: Geographic longitude (negative = West)
        angle: Angle name ("ASC", "MC", "DSC", "IC", or full names)

    Returns:
        Longitude of the angle in degrees (0-360)
    """
    from stellium.data.paths import initialize_ephemeris

    initialize_ephemeris()

    _, ascmc = swe.houses_ex(julian_day, latitude, longitude, hsys=b"P")

    angle_upper = angle.upper() if angle in ("ASC", "MC", "DSC", "IC") else angle
    if angle_upper not in ANGLE_INDICES and angle not in ANGLE_INDICES:
        raise ValueError(
            f"Unknown angle: {angle}. Must be one of ASC, MC, DSC, IC "
            "(or Ascendant, Midheaven, Descendant, Imum Coeli)"
        )

    idx = ANGLE_INDICES.get(angle_upper, ANGLE_INDICES.get(angle))
    angle_lon = ascmc[idx]

    # Apply 180° offset for opposite angles
    if angle_upper in OPPOSITE_ANGLES or angle in OPPOSITE_ANGLES:
        angle_lon = (angle_lon + 180) % 360

    return angle_lon


@dataclass(frozen=True)
class AngleCrossing:
    """Result of an angle crossing search.

    Represents the moment when a chart angle (ASC, MC, DSC, IC) reaches
    a specific zodiac longitude.

    Attributes:
        julian_day: Julian day when angle reaches the longitude
        datetime_utc: UTC datetime of the crossing
        angle_name: Which angle ("ASC", "MC", "DSC", "IC")
        target_longitude: The target longitude that was crossed
        actual_longitude: The actual angle longitude at crossing
        latitude: Geographic latitude used
        longitude: Geographic longitude used
    """

    julian_day: float
    datetime_utc: datetime
    angle_name: str
    target_longitude: float
    actual_longitude: float
    latitude: float
    longitude: float

    def __str__(self) -> str:
        sign_idx = int(self.target_longitude // 30)
        signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        degree = self.target_longitude % 30
        return (
            f"{self.angle_name} at {degree:.1f}° {signs[sign_idx]} "
            f"on {self.datetime_utc.strftime('%Y-%m-%d %H:%M')}"
        )


def find_angle_crossing(
    target_longitude: float,
    latitude: float,
    longitude: float,
    angle: str,
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    max_days: float = 2.0,
    tolerance: float = 0.001,
    max_iterations: int = 50,
) -> AngleCrossing | None:
    """Find when a chart angle crosses a specific longitude.

    Since angles rotate with Earth's rotation (~1° every 4 minutes),
    any given longitude will be crossed roughly once per sidereal day
    (~23h 56m) by each angle.

    Args:
        target_longitude: Target longitude in degrees (0-360)
        latitude: Geographic latitude
        longitude: Geographic longitude (negative = West)
        angle: Which angle to track ("ASC", "MC", "DSC", "IC")
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        max_days: Maximum days to search (default 2, since crossings are daily)
        tolerance: Convergence tolerance in degrees
        max_iterations: Maximum refinement iterations

    Returns:
        AngleCrossing with exact timing, or None if not found

    Example:
        >>> # Find when ASC reaches 0° Leo in NYC
        >>> result = find_angle_crossing(120.0, 40.7, -74.0, "ASC", datetime.now())
        >>> print(f"ASC at 0° Leo: {result.datetime_utc}")
    """
    from stellium.data.paths import initialize_ephemeris

    initialize_ephemeris()

    # Convert start to Julian day if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    # Normalize target longitude
    target_longitude = target_longitude % 360

    # Angles move ~360° per day, so we need small steps for bracketing
    step_hours = 0.5  # 30 minutes
    step_jd = step_hours / 24

    step = step_jd if direction == "forward" else -step_jd
    end_jd = start_jd + (max_days if direction == "forward" else -max_days)

    current_jd = start_jd
    current_angle = _get_angle_longitude(current_jd, latitude, longitude, angle)
    current_error = _normalize_angle_error(current_angle - target_longitude)

    # Bracket the crossing
    bracket_start = None
    bracket_end = None

    while (direction == "forward" and current_jd < end_jd) or (
        direction == "backward" and current_jd > end_jd
    ):
        next_jd = current_jd + step
        next_angle = _get_angle_longitude(next_jd, latitude, longitude, angle)
        next_error = _normalize_angle_error(next_angle - target_longitude)

        # Check for sign change (crossing)
        if current_error * next_error < 0:
            # Verify it's a real crossing (not a 180° wraparound artifact)
            if abs(current_error) < 90 and abs(next_error) < 90:
                bracket_start = current_jd
                bracket_end = next_jd
                break

        # Also check if we're very close
        if abs(next_error) < tolerance:
            return AngleCrossing(
                julian_day=next_jd,
                datetime_utc=_julian_day_to_datetime(next_jd),
                angle_name=angle.upper() if angle.upper() in ANGLE_INDICES else angle,
                target_longitude=target_longitude,
                actual_longitude=next_angle,
                latitude=latitude,
                longitude=longitude,
            )

        current_jd = next_jd
        current_error = next_error

    if bracket_start is None:
        return None

    # Refine with bisection (Newton-Raphson is tricky here due to discontinuities)
    t1, t2 = bracket_start, bracket_end

    for _ in range(max_iterations):
        mid_jd = (t1 + t2) / 2
        mid_angle = _get_angle_longitude(mid_jd, latitude, longitude, angle)
        mid_error = _normalize_angle_error(mid_angle - target_longitude)

        if abs(mid_error) < tolerance:
            return AngleCrossing(
                julian_day=mid_jd,
                datetime_utc=_julian_day_to_datetime(mid_jd),
                angle_name=angle.upper() if angle.upper() in ANGLE_INDICES else angle,
                target_longitude=target_longitude,
                actual_longitude=mid_angle,
                latitude=latitude,
                longitude=longitude,
            )

        # Determine which half contains the crossing
        t1_angle = _get_angle_longitude(t1, latitude, longitude, angle)
        t1_error = _normalize_angle_error(t1_angle - target_longitude)

        if t1_error * mid_error < 0:
            t2 = mid_jd
        else:
            t1 = mid_jd

    # Return best estimate
    final_jd = (t1 + t2) / 2
    final_angle = _get_angle_longitude(final_jd, latitude, longitude, angle)
    return AngleCrossing(
        julian_day=final_jd,
        datetime_utc=_julian_day_to_datetime(final_jd),
        angle_name=angle.upper() if angle.upper() in ANGLE_INDICES else angle,
        target_longitude=target_longitude,
        actual_longitude=final_angle,
        latitude=latitude,
        longitude=longitude,
    )


def find_all_angle_crossings(
    target_longitude: float,
    latitude: float,
    longitude: float,
    angle: str,
    start: datetime | float,
    end: datetime | float,
    max_results: int = 100,
) -> list[AngleCrossing]:
    """Find all times a chart angle crosses a specific longitude in a date range.

    Args:
        target_longitude: Target longitude in degrees (0-360)
        latitude: Geographic latitude
        longitude: Geographic longitude (negative = West)
        angle: Which angle to track ("ASC", "MC", "DSC", "IC")
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        max_results: Safety limit on number of results

    Returns:
        List of AngleCrossing objects, chronologically ordered

    Example:
        >>> # Find all times ASC crosses 0° Aries in January 2025
        >>> results = find_all_angle_crossings(
        ...     0.0, 40.7, -74.0, "ASC",
        ...     datetime(2025, 1, 1), datetime(2025, 2, 1)
        ... )
        >>> print(f"Found {len(results)} crossings")  # ~31 (once per day)
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
        result = find_angle_crossing(
            target_longitude,
            latitude,
            longitude,
            angle,
            current_jd,
            direction="forward",
            max_days=end_jd - current_jd + 1,
        )

        if result is None or result.julian_day > end_jd:
            break

        results.append(result)

        # Move past this crossing
        # Angles cross a given longitude roughly once per sidereal day (~23h 56m)
        # Use 20 hours to be safe
        current_jd = result.julian_day + 20 / 24

    return results


# =============================================================================
# Eclipse Search Functions
# =============================================================================

# Maximum orb from node for an eclipse to occur
# Solar eclipses can occur up to ~18° from node, lunar up to ~12°
SOLAR_ECLIPSE_MAX_ORB = 18.5
LUNAR_ECLIPSE_MAX_ORB = 12.5

# Approximate orb thresholds for eclipse types (rough guidelines)
# These vary based on lunar distance, parallax, etc. - simplified here
TOTAL_SOLAR_ORB = 10.0  # Likely total/annular if within this
PARTIAL_SOLAR_ORB = 18.5  # Partial possible up to this
TOTAL_LUNAR_ORB = 6.0  # Likely total lunar if within this
PARTIAL_LUNAR_ORB = 12.5  # Partial lunar up to this


@dataclass(frozen=True)
class Eclipse:
    """Result of an eclipse search.

    Attributes:
        julian_day: Julian day of the eclipse (exact Sun-Moon conjunction/opposition)
        datetime_utc: UTC datetime of the eclipse
        eclipse_type: "solar" or "lunar"
        sun_longitude: Sun's longitude at eclipse
        moon_longitude: Moon's longitude at eclipse
        node_longitude: True Node longitude at eclipse
        orb_to_node: Distance from Sun/Moon to nearest node (degrees)
        nearest_node: Which node is involved ("north" or "south")
        sign: Zodiac sign of the eclipse
        classification: "total", "annular", "partial", or "penumbral"
    """

    julian_day: float
    datetime_utc: datetime
    eclipse_type: Literal["solar", "lunar"]
    sun_longitude: float
    moon_longitude: float
    node_longitude: float
    orb_to_node: float
    nearest_node: Literal["north", "south"]
    sign: str
    classification: str

    @property
    def is_solar(self) -> bool:
        """True if this is a solar eclipse."""
        return self.eclipse_type == "solar"

    @property
    def is_lunar(self) -> bool:
        """True if this is a lunar eclipse."""
        return self.eclipse_type == "lunar"

    @property
    def degree_in_sign(self) -> float:
        """Degree within the sign (0-30)."""
        return self.sun_longitude % 30

    def __str__(self) -> str:
        degree = int(self.degree_in_sign)
        minute = int((self.degree_in_sign - degree) * 60)
        node_abbrev = "NN" if self.nearest_node == "north" else "SN"
        return (
            f"{self.classification.capitalize()} {self.eclipse_type} eclipse "
            f"at {degree}°{minute:02d}' {self.sign} ({node_abbrev}) "
            f"on {self.datetime_utc.strftime('%Y-%m-%d %H:%M')}"
        )


def _get_sun_moon_separation(julian_day: float) -> tuple[float, float, float, float]:
    """Get Sun-Moon separation and positions at a given time.

    Args:
        julian_day: Julian day number

    Returns:
        Tuple of (separation, sun_longitude, moon_longitude, moon_speed)
        Separation is normalized to [-180, +180]
    """
    sun_lon, _ = _get_position_and_speed(swe.SUN, julian_day)
    moon_lon, moon_speed = _get_position_and_speed(swe.MOON, julian_day)
    separation = _normalize_angle_error(moon_lon - sun_lon)
    return separation, sun_lon, moon_lon, moon_speed


def _find_lunation(
    start_jd: float,
    lunation_type: Literal["new", "full"],
    max_days: float = 32.0,
) -> tuple[float, float, float] | None:
    """Find the next New Moon or Full Moon.

    Uses Newton-Raphson on Sun-Moon separation.

    Args:
        start_jd: Julian day to start search from
        lunation_type: "new" (conjunction) or "full" (opposition)
        max_days: Maximum days to search

    Returns:
        Tuple of (julian_day, sun_longitude, moon_longitude) or None
    """
    # Start with a sweep to bracket the lunation
    current_jd = start_jd
    end_jd = start_jd + max_days
    step = 1.0  # Day step for initial sweep

    sep, _, _, _ = _get_sun_moon_separation(current_jd)
    # Adjust for target
    if lunation_type == "full":
        current_error = _normalize_angle_error(sep - 180.0)
    else:
        current_error = sep  # Already normalized around 0

    # Find bracket
    bracket_start = None
    bracket_end = None

    while current_jd < end_jd:
        next_jd = current_jd + step
        sep, _, _, _ = _get_sun_moon_separation(next_jd)

        if lunation_type == "full":
            next_error = _normalize_angle_error(sep - 180.0)
        else:
            next_error = sep

        # Check for sign change AND that both errors are reasonably small
        # This avoids false positives from wraparound (e.g., +174° to -171°)
        # A real zero crossing will have |error| < 90° on both sides
        if current_error * next_error < 0:
            if abs(current_error) < 90 and abs(next_error) < 90:
                bracket_start = current_jd
                bracket_end = next_jd
                break

        current_jd = next_jd
        current_error = next_error

    if bracket_start is None:
        return None

    # Refine with Newton-Raphson / bisection
    t = (bracket_start + bracket_end) / 2
    for _ in range(50):
        sep, sun_lon, moon_lon, moon_speed = _get_sun_moon_separation(t)

        if lunation_type == "full":
            error = _normalize_angle_error(sep - 180.0)
        else:
            error = sep

        if abs(error) < 0.0001:  # ~0.36 arcseconds
            return t, sun_lon, moon_lon

        # Moon moves ~13°/day relative to Sun (~12°/day faster than Sun)
        # Use this as derivative estimate
        relative_speed = moon_speed - 1.0  # Sun moves ~1°/day
        if abs(relative_speed) > 0.1:
            newton_step = -error / relative_speed
            newton_step = max(-2, min(2, newton_step))  # Clamp
            t_new = t + newton_step
            t_new = max(bracket_start, min(bracket_end, t_new))
        else:
            t_new = (bracket_start + bracket_end) / 2

        # Update bracket
        if error > 0:
            bracket_end = t
        else:
            bracket_start = t

        t = t_new

    # Return best estimate
    sep, sun_lon, moon_lon, _ = _get_sun_moon_separation(t)
    return t, sun_lon, moon_lon


def _classify_eclipse(
    eclipse_type: Literal["solar", "lunar"],
    orb_to_node: float,
) -> str:
    """Classify an eclipse based on type and orb to node.

    Args:
        eclipse_type: "solar" or "lunar"
        orb_to_node: Distance from eclipse to nearest node

    Returns:
        Classification: "total", "annular", "partial", or "penumbral"
    """
    if eclipse_type == "solar":
        if orb_to_node <= TOTAL_SOLAR_ORB:
            # Could be total or annular depending on Moon's distance
            # Simplified: just call it "total" for tight orbs
            return "total"
        else:
            return "partial"
    else:  # lunar
        if orb_to_node <= TOTAL_LUNAR_ORB:
            return "total"
        elif orb_to_node <= PARTIAL_LUNAR_ORB * 0.7:
            return "partial"
        else:
            return "penumbral"


def find_eclipse(
    start: datetime | float,
    direction: Literal["forward", "backward"] = "forward",
    eclipse_types: Literal["both", "solar", "lunar"] = "both",
    max_days: float = 200.0,
) -> Eclipse | None:
    """Find the next eclipse from a starting date.

    Args:
        start: Starting datetime (UTC) or Julian day
        direction: "forward" to search future, "backward" to search past
        eclipse_types: Which types to find ("both", "solar", "lunar")
        max_days: Maximum days to search (default 200 = ~6 months)

    Returns:
        Eclipse with details, or None if not found

    Example:
        >>> # Find next eclipse from now
        >>> eclipse = find_eclipse(datetime(2024, 1, 1))
        >>> print(eclipse)
        Partial lunar eclipse at 5°07' Leo (NN) on 2024-03-25 07:00
    """
    _set_ephemeris_path()

    if isinstance(start, datetime):
        start_jd = _datetime_to_julian_day(start)
    else:
        start_jd = start

    if direction == "backward":
        # For backward search, we'd need to modify the logic
        # For now, only support forward
        raise NotImplementedError("Backward eclipse search not yet implemented")

    current_jd = start_jd
    end_jd = start_jd + max_days

    while current_jd < end_jd:
        # Find BOTH next New Moon and next Full Moon
        # Then check which (if any) is an eclipse, returning the earlier one
        solar_eclipse = None
        lunar_eclipse = None
        new_moon_jd = None
        full_moon_jd = None

        # Find next New Moon (potential solar eclipse)
        if eclipse_types in ("both", "solar"):
            new_moon = _find_lunation(current_jd, "new", max_days=35)
            if new_moon and new_moon[0] <= end_jd:
                jd, sun_lon, moon_lon = new_moon
                new_moon_jd = jd

                # Get node position
                node_lon, _ = _get_position_and_speed(
                    SWISS_EPHEMERIS_IDS["True Node"], jd
                )
                south_node_lon = (node_lon + 180) % 360

                # Check distance to nodes
                dist_to_nn = abs(_normalize_angle_error(sun_lon - node_lon))
                dist_to_sn = abs(_normalize_angle_error(sun_lon - south_node_lon))

                orb = min(dist_to_nn, dist_to_sn)
                nearest = "north" if dist_to_nn < dist_to_sn else "south"

                if orb <= SOLAR_ECLIPSE_MAX_ORB:
                    solar_eclipse = Eclipse(
                        julian_day=jd,
                        datetime_utc=_julian_day_to_datetime(jd),
                        eclipse_type="solar",
                        sun_longitude=sun_lon,
                        moon_longitude=moon_lon,
                        node_longitude=node_lon,
                        orb_to_node=orb,
                        nearest_node=nearest,
                        sign=_get_sign_from_longitude(sun_lon),
                        classification=_classify_eclipse("solar", orb),
                    )

        # Find next Full Moon (potential lunar eclipse)
        if eclipse_types in ("both", "lunar"):
            full_moon = _find_lunation(current_jd, "full", max_days=35)
            if full_moon and full_moon[0] <= end_jd:
                jd, sun_lon, moon_lon = full_moon
                full_moon_jd = jd

                # Get node position
                node_lon, _ = _get_position_and_speed(
                    SWISS_EPHEMERIS_IDS["True Node"], jd
                )
                south_node_lon = (node_lon + 180) % 360

                # For lunar eclipse, check Moon's distance to nodes
                dist_to_nn = abs(_normalize_angle_error(moon_lon - node_lon))
                dist_to_sn = abs(_normalize_angle_error(moon_lon - south_node_lon))

                orb = min(dist_to_nn, dist_to_sn)
                nearest = "north" if dist_to_nn < dist_to_sn else "south"

                if orb <= LUNAR_ECLIPSE_MAX_ORB:
                    lunar_eclipse = Eclipse(
                        julian_day=jd,
                        datetime_utc=_julian_day_to_datetime(jd),
                        eclipse_type="lunar",
                        sun_longitude=sun_lon,
                        moon_longitude=moon_lon,
                        node_longitude=node_lon,
                        orb_to_node=orb,
                        nearest_node=nearest,
                        sign=_get_sign_from_longitude(moon_lon),
                        classification=_classify_eclipse("lunar", orb),
                    )

        # Return the earlier eclipse if we found any
        if solar_eclipse and lunar_eclipse:
            # Return whichever comes first
            if solar_eclipse.julian_day <= lunar_eclipse.julian_day:
                return solar_eclipse
            else:
                return lunar_eclipse
        elif solar_eclipse:
            return solar_eclipse
        elif lunar_eclipse:
            return lunar_eclipse

        # No eclipse found, move past whichever lunation we found
        if new_moon_jd and full_moon_jd:
            current_jd = min(new_moon_jd, full_moon_jd) + 1.0
        elif new_moon_jd:
            current_jd = new_moon_jd + 1.0
        elif full_moon_jd:
            current_jd = full_moon_jd + 1.0
        else:
            current_jd += 15.0  # Half a lunar cycle

    return None


def find_all_eclipses(
    start: datetime | float,
    end: datetime | float,
    eclipse_types: Literal["both", "solar", "lunar"] = "both",
    max_results: int = 20,
) -> list[Eclipse]:
    """Find all eclipses in a date range.

    Args:
        start: Start datetime (UTC) or Julian day
        end: End datetime (UTC) or Julian day
        eclipse_types: Which types to find ("both", "solar", "lunar")
        max_results: Safety limit on number of results (default 20)

    Returns:
        List of Eclipse objects, chronologically ordered

    Example:
        >>> # Find all eclipses in 2024
        >>> eclipses = find_all_eclipses(
        ...     datetime(2024, 1, 1),
        ...     datetime(2024, 12, 31)
        ... )
        >>> for e in eclipses:
        ...     print(e)
    """
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
        eclipse = find_eclipse(
            current_jd,
            direction="forward",
            eclipse_types=eclipse_types,
            max_days=end_jd - current_jd + 1,
        )

        if eclipse is None or eclipse.julian_day > end_jd:
            break

        results.append(eclipse)

        # Move past this eclipse - but not too far!
        # Eclipse seasons have ~2 eclipses ~2 weeks apart
        # Step only 12 days to catch both solar and lunar in same season
        current_jd = eclipse.julian_day + 12.0

    return results
