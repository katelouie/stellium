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
