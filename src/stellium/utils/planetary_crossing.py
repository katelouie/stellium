"""
Utility functions for finding planetary crossings.

A "crossing" is when a planet reaches a specific zodiacal longitude.
Used for returns, ingresses, and other timing techniques.
"""

import swisseph as swe

from stellium.core.registry import CELESTIAL_REGISTRY

# Approximate orbital periods (days) for stepping through time
# These are used for initial coarse search before binary refinement
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
    "Chiron": 18263.0,  # ~50 years
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

    Uses a two-phase algorithm:
    1. Coarse search: Step forward/backward until we bracket the crossing
    2. Binary search: Refine to sub-second precision

    Args:
        planet: Planet name (must be in CELESTIAL_REGISTRY)
        target_longitude: Target ecliptic longitude (0-360)
        start_jd: Julian Day to start searching from
        direction: 1 for forward in time, -1 for backward
        precision: Desired precision in Julian Days (default ~0.08 seconds)

    Returns:
        Julian Day of the crossing

    Raises:
        ValueError: If planet not found or crossing not found within bounds

    Example:
        >>> # Find when Sun reaches 15° Capricorn after Jan 1, 2025
        >>> from stellium.utils.time import datetime_to_julian_day
        >>> from datetime import datetime
        >>> start = datetime_to_julian_day(datetime(2025, 1, 1))
        >>> jd = find_planetary_crossing("Sun", 285.0, start)  # 285° = 15° Cap
    """
    # Get Swiss Ephemeris ID from registry
    if planet not in CELESTIAL_REGISTRY:
        raise ValueError(f"Unknown planet: {planet}")

    planet_info = CELESTIAL_REGISTRY[planet]
    swe_id = planet_info.swiss_ephemeris_id

    if swe_id is None:
        raise ValueError(f"Planet {planet} has no Swiss Ephemeris ID")

    # Normalize target to 0-360
    target_longitude = target_longitude % 360

    # Calculate step size for coarse search
    # Goal: step by roughly 10-15 degrees of planetary motion
    # This keeps steps small enough that we don't miss crossings due to
    # retrograde motion or wrapping around 360°
    period = PLANET_PERIODS.get(planet, 365.25)

    # Days per degree of motion (on average)
    days_per_degree = period / 360.0

    # Step by ~10 degrees worth of motion (conservative to handle retrograde)
    # Minimum step of 1 day, maximum step of 30 days
    step = max(1.0, min(30.0, days_per_degree * 10.0)) * direction

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
    low_jd = jd - step if direction > 0 else jd
    high_jd = jd if direction > 0 else jd - step

    # Ensure low < high
    if low_jd > high_jd:
        low_jd, high_jd = high_jd, low_jd

    while (high_jd - low_jd) > precision:
        mid_jd = (low_jd + high_jd) / 2
        mid_lon = _get_longitude(swe_id, mid_jd)
        low_lon = _get_longitude(swe_id, low_jd)

        if _crossed_longitude(low_lon, mid_lon, target_longitude, 1):
            high_jd = mid_jd
        else:
            low_jd = mid_jd

    return (low_jd + high_jd) / 2


def _get_longitude(swe_id: int, jd: float) -> float:
    """Get ecliptic longitude for a planet at a Julian Day."""
    result = swe.calc_ut(jd, swe_id, swe.FLG_SWIEPH)
    return result[0][0]  # Longitude is first element


def _crossed_longitude(
    lon1: float,
    lon2: float,
    target: float,
    direction: int,
) -> bool:
    """
    Check if we crossed the target longitude between lon1 and lon2.

    For RETURN calculations, we only want crossings in DIRECT motion
    (longitude increasing). Retrograde crossings are ignored.

    Handles the 360°→0° wrap-around case correctly.

    Args:
        lon1: Longitude at earlier time
        lon2: Longitude at later time
        target: Target longitude to check crossing
        direction: 1 for forward search, -1 for backward search in time

    Returns:
        True if target was crossed between lon1 and lon2 during DIRECT motion
    """
    # Normalize all to 0-360
    lon1 = lon1 % 360
    lon2 = lon2 % 360
    target = target % 360

    if direction > 0:  # Searching forward in time
        # Calculate the angular motion
        # If lon2 > lon1, planet moved forward
        # If lon2 < lon1, either wrapped around 360→0 OR retrograde
        delta = lon2 - lon1

        # Normalize delta to [-180, 180] to determine direction of motion
        if delta > 180:
            delta -= 360  # Wrapped backward (retrograde near 0°)
        elif delta < -180:
            delta += 360  # Wrapped forward (direct near 360°)

        # Only count crossings during direct motion (delta > 0)
        if delta <= 0:
            return False  # Retrograde - skip this crossing

        # Now check if target is between lon1 and lon2 (direct motion)
        # Handle wrap-around
        if lon1 <= lon2:  # Normal case (no wrap)
            return lon1 < target <= lon2
        else:  # Wrapped around 360→0 during direct motion
            return target > lon1 or target <= lon2

    else:  # Searching backward in time
        # For backward search, we still want direct motion crossings
        # but we're looking in the opposite temporal direction
        delta = lon1 - lon2  # lon1 is at later time when searching backward

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        if delta <= 0:
            return False  # Would be retrograde in forward time

        if lon2 <= lon1:
            return lon2 < target <= lon1
        else:
            return target > lon2 or target <= lon1


def find_nth_return(
    planet: str,
    natal_longitude: float,
    birth_jd: float,
    n: int = 1,
) -> float:
    """
    Find the Nth planetary return after birth.

    A "return" is when a transiting planet returns to its natal position.

    Args:
        planet: Planet name
        natal_longitude: Natal longitude of the planet (0-360)
        birth_jd: Julian Day of birth
        n: Which return (1 = first, 2 = second, etc.)

    Returns:
        Julian Day of the Nth return

    Raises:
        ValueError: If n < 1 or planet not found

    Example:
        >>> # Find first Saturn return (~age 29)
        >>> birth_jd = 2449718.0  # Jan 6, 1994
        >>> natal_saturn = 330.5  # Saturn's natal position
        >>> sr1 = find_nth_return("Saturn", natal_saturn, birth_jd, n=1)
    """
    if n < 1:
        raise ValueError("Return number must be >= 1")

    jd = birth_jd

    for _ in range(n):
        # Start searching from just after the current position
        # Add 1 day offset to avoid finding the same position
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
    Note: For retrograde planets, this may return a retrograde crossing.

    Args:
        planet: Planet name
        natal_longitude: Natal longitude of the planet (0-360)
        target_jd: Julian Day to search around

    Returns:
        Julian Day of the nearest return

    Example:
        >>> # Find lunar return nearest to March 15, 2025
        >>> from stellium.utils.time import datetime_to_julian_day
        >>> from datetime import datetime
        >>> target = datetime_to_julian_day(datetime(2025, 3, 15))
        >>> natal_moon = 105.5
        >>> lr = find_return_near_date("Moon", natal_moon, target)
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
