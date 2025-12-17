"""
Time window generation and set operations for electional search optimization.

Instead of checking every time point, we pre-compute windows where conditions
are true and intersect them. This transforms O(N) point-checks into fast
set intersection math.

Example:
    >>> from stellium.electional.intervals import waxing_windows, intersect_windows
    >>> from datetime import datetime
    >>>
    >>> # Get all waxing moon windows in 2025
    >>> windows = waxing_windows(datetime(2025, 1, 1), datetime(2025, 12, 31))
    >>> print(f"Found {len(windows)} waxing periods")
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import swisseph as swe

from stellium.engines.ephemeris import _set_ephemeris_path
from stellium.engines.search import (
    _datetime_to_julian_day,
    _julian_day_to_datetime,
    find_all_sign_changes,
    find_all_stations,
)

# =============================================================================
# Core Data Types
# =============================================================================


@dataclass(frozen=True)
class TimeWindow:
    """A time interval where a condition is true.

    TimeWindow stores times as Julian Day numbers, which are UTC-based.
    This is intentional for astronomical correctness and clean interval math.

    Note:
        The ``start_datetime`` and ``end_datetime`` properties return naive
        datetimes in UTC. If you need local time, convert using pytz::

            import pytz
            local_tz = pytz.timezone("America/Los_Angeles")
            local_start = window.start_datetime.replace(tzinfo=pytz.UTC).astimezone(local_tz)

    See Also:
        ElectionWindow: User-facing result type that stores local datetimes.

    Attributes:
        start_jd: Start of window as Julian Day (UTC-based)
        end_jd: End of window as Julian Day (UTC-based)
    """

    start_jd: float
    end_jd: float

    @property
    def duration_days(self) -> float:
        """Duration of the window in days."""
        return self.end_jd - self.start_jd

    @property
    def duration_hours(self) -> float:
        """Duration of the window in hours."""
        return self.duration_days * 24

    @property
    def start_datetime(self) -> datetime:
        """Start as datetime (UTC)."""
        return _julian_day_to_datetime(self.start_jd)

    @property
    def end_datetime(self) -> datetime:
        """End as datetime (UTC)."""
        return _julian_day_to_datetime(self.end_jd)

    def __str__(self) -> str:
        start = self.start_datetime.strftime("%Y-%m-%d %H:%M")
        end = self.end_datetime.strftime("%Y-%m-%d %H:%M")
        hours = self.duration_hours
        return f"{start} - {end} ({hours:.1f}h)"

    def __repr__(self) -> str:
        return f"TimeWindow({self.start_jd:.4f}, {self.end_jd:.4f})"


# =============================================================================
# Set Operations
# =============================================================================


def intersect_windows(
    windows_a: list[TimeWindow],
    windows_b: list[TimeWindow],
) -> list[TimeWindow]:
    """Compute intersection of two sorted window lists.

    For each overlapping pair, emits the overlap:
    (max(start_a, start_b), min(end_a, end_b))

    Args:
        windows_a: First list of windows (must be sorted by start_jd)
        windows_b: Second list of windows (must be sorted by start_jd)

    Returns:
        List of windows representing the intersection
    """
    result: list[TimeWindow] = []

    i, j = 0, 0
    while i < len(windows_a) and j < len(windows_b):
        a = windows_a[i]
        b = windows_b[j]

        # Check for overlap
        start = max(a.start_jd, b.start_jd)
        end = min(a.end_jd, b.end_jd)

        if start < end:
            result.append(TimeWindow(start, end))

        # Advance the one that ends first
        if a.end_jd < b.end_jd:
            i += 1
        else:
            j += 1

    return result


def union_windows(
    windows_a: list[TimeWindow],
    windows_b: list[TimeWindow],
) -> list[TimeWindow]:
    """Merge two window lists, combining overlapping windows.

    Args:
        windows_a: First list of windows (must be sorted by start_jd)
        windows_b: Second list of windows (must be sorted by start_jd)

    Returns:
        List of merged windows
    """
    # Merge the two sorted lists
    merged = []
    i, j = 0, 0
    while i < len(windows_a) and j < len(windows_b):
        if windows_a[i].start_jd <= windows_b[j].start_jd:
            merged.append(windows_a[i])
            i += 1
        else:
            merged.append(windows_b[j])
            j += 1
    merged.extend(windows_a[i:])
    merged.extend(windows_b[j:])

    if not merged:
        return []

    # Combine overlapping windows
    result = [merged[0]]
    for window in merged[1:]:
        last = result[-1]
        if window.start_jd <= last.end_jd:
            # Overlapping - extend the last window
            result[-1] = TimeWindow(last.start_jd, max(last.end_jd, window.end_jd))
        else:
            result.append(window)

    return result


def invert_windows(
    windows: list[TimeWindow],
    start_jd: float,
    end_jd: float,
) -> list[TimeWindow]:
    """Get complement windows (gaps between the given windows).

    Args:
        windows: List of windows to invert (must be sorted by start_jd)
        start_jd: Start of the range to consider
        end_jd: End of the range to consider

    Returns:
        List of windows representing the gaps
    """
    result: list[TimeWindow] = []
    current = start_jd

    for window in windows:
        # Clip to our range
        w_start = max(window.start_jd, start_jd)
        w_end = min(window.end_jd, end_jd)

        if w_start > current:
            result.append(TimeWindow(current, w_start))

        current = max(current, w_end)

    # Add final gap if any
    if current < end_jd:
        result.append(TimeWindow(current, end_jd))

    return result


# =============================================================================
# Lunation Helpers (adapted from search.py)
# =============================================================================


def _get_sun_moon_positions(jd: float) -> tuple[float, float]:
    """Get Sun and Moon longitudes at a given Julian Day."""
    _set_ephemeris_path()
    flags = swe.FLG_SWIEPH
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    return sun_result[0][0], moon_result[0][0]


def _normalize_angle(angle: float) -> float:
    """Normalize angle to range [-180, +180]."""
    return ((angle + 180) % 360) - 180


def _find_next_lunation(
    start_jd: float,
    lunation_type: Literal["new", "full"],
    max_days: float = 32.0,
) -> float | None:
    """Find the next New Moon or Full Moon after start_jd.

    Args:
        start_jd: Julian Day to start searching from
        lunation_type: "new" for New Moon, "full" for Full Moon
        max_days: Maximum days to search

    Returns:
        Julian Day of the lunation, or None if not found
    """
    _set_ephemeris_path()

    # Target separation: 0° for new moon, 180° for full moon
    target = 180.0 if lunation_type == "full" else 0.0

    # Sweep to find bracket
    current_jd = start_jd
    end_jd = start_jd + max_days
    step = 1.0

    sun_lon, moon_lon = _get_sun_moon_positions(current_jd)
    current_sep = _normalize_angle(moon_lon - sun_lon - target)

    while current_jd < end_jd:
        next_jd = current_jd + step
        sun_lon, moon_lon = _get_sun_moon_positions(next_jd)
        next_sep = _normalize_angle(moon_lon - sun_lon - target)

        # Check for sign change (crossing target)
        if current_sep * next_sep < 0 and abs(current_sep) < 90 and abs(next_sep) < 90:
            # Refine with bisection
            lo, hi = current_jd, next_jd
            for _ in range(30):
                mid = (lo + hi) / 2
                sun_lon, moon_lon = _get_sun_moon_positions(mid)
                mid_sep = _normalize_angle(moon_lon - sun_lon - target)

                if abs(mid_sep) < 0.0001:
                    return mid

                if current_sep * mid_sep < 0:
                    hi = mid
                else:
                    lo = mid
                    current_sep = mid_sep

            return (lo + hi) / 2

        current_jd = next_jd
        current_sep = next_sep

    return None


def _find_all_lunations(
    start_jd: float,
    end_jd: float,
    lunation_type: Literal["new", "full"],
) -> list[float]:
    """Find all New Moons or Full Moons in a date range.

    Returns:
        List of Julian Days for each lunation
    """
    results = []
    current_jd = start_jd

    while current_jd < end_jd:
        jd = _find_next_lunation(
            current_jd, lunation_type, max_days=end_jd - current_jd + 1
        )
        if jd is None or jd > end_jd:
            break
        results.append(jd)
        current_jd = jd + 1.0  # Skip ahead past this lunation

    return results


# =============================================================================
# Interval Generators
# =============================================================================


def waxing_windows(
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when Moon is waxing (from New Moon to Full Moon).

    Args:
        start: Start of search range (datetime or Julian Day)
        end: End of search range (datetime or Julian Day)

    Returns:
        List of TimeWindow objects for waxing periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    # Find all new moons and full moons
    # Need to search beyond end_jd for full moons to capture windows that start
    # before end_jd but end after it
    new_moons = _find_all_lunations(start_jd - 30, end_jd, "new")
    full_moons = _find_all_lunations(start_jd - 30, end_jd + 30, "full")

    # Build windows from new moon to following full moon
    windows = []
    for new_jd in new_moons:
        # Find the next full moon after this new moon
        for full_jd in full_moons:
            if full_jd > new_jd:
                # Clip to our search range
                w_start = max(new_jd, start_jd)
                w_end = min(full_jd, end_jd)
                if w_start < w_end:
                    windows.append(TimeWindow(w_start, w_end))
                break

    return windows


def waning_windows(
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when Moon is waning (from Full Moon to New Moon).

    Args:
        start: Start of search range (datetime or Julian Day)
        end: End of search range (datetime or Julian Day)

    Returns:
        List of TimeWindow objects for waning periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    # Waning is the complement of waxing
    waxing = waxing_windows(start_jd, end_jd)
    return invert_windows(waxing, start_jd, end_jd)


def moon_sign_windows(
    signs: list[str],
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when Moon is in specified signs.

    Args:
        signs: List of sign names (e.g., ["Taurus", "Cancer"])
        start: Start of search range
        end: End of search range

    Returns:
        List of TimeWindow objects
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)
    start_dt = start if isinstance(start, datetime) else _julian_day_to_datetime(start)
    end_dt = end if isinstance(end, datetime) else _julian_day_to_datetime(end)

    # Normalize sign names
    signs_normalized = [s.capitalize() for s in signs]

    # Get all Moon sign changes in range (with buffer for edge cases)
    from datetime import timedelta

    ingresses = find_all_sign_changes("Moon", start_dt - timedelta(days=3), end_dt)

    if not ingresses:
        return []

    # Build windows for each sign period that's in our target signs
    windows = []

    for i, ingress in enumerate(ingresses):
        if ingress.sign not in signs_normalized:
            continue

        # Window starts at this ingress
        w_start = ingress.julian_day

        # Window ends at next ingress (or end of range)
        if i + 1 < len(ingresses):
            w_end = ingresses[i + 1].julian_day
        else:
            w_end = end_jd

        # Clip to search range
        w_start = max(w_start, start_jd)
        w_end = min(w_end, end_jd)

        if w_start < w_end:
            windows.append(TimeWindow(w_start, w_end))

    return windows


def moon_sign_not_in_windows(
    signs: list[str],
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when Moon is NOT in specified signs.

    Args:
        signs: List of sign names to avoid
        start: Start of search range
        end: End of search range

    Returns:
        List of TimeWindow objects
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    # Get windows where Moon IS in those signs, then invert
    in_signs = moon_sign_windows(signs, start_jd, end_jd)
    return invert_windows(in_signs, start_jd, end_jd)


def retrograde_windows(
    planet: str,
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when a planet is retrograde.

    Args:
        planet: Planet name (e.g., "Mercury", "Venus", "Mars")
        start: Start of search range
        end: End of search range

    Returns:
        List of TimeWindow objects for retrograde periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)
    start_dt = start if isinstance(start, datetime) else _julian_day_to_datetime(start)
    end_dt = end if isinstance(end, datetime) else _julian_day_to_datetime(end)

    # Get all stations with buffer for edge cases
    from datetime import timedelta

    stations = find_all_stations(
        planet, start_dt - timedelta(days=30), end_dt + timedelta(days=30)
    )

    if not stations:
        return []

    # Build windows from retrograde stations to direct stations
    windows = []
    in_retrograde = False
    rx_start = None

    for station in stations:
        if station.station_type == "retrograde":
            in_retrograde = True
            rx_start = station.julian_day
        elif (
            station.station_type == "direct" and in_retrograde and rx_start is not None
        ):
            # Rx period ends at this direct station
            w_start = max(rx_start, start_jd)
            w_end = min(station.julian_day, end_jd)
            if w_start < w_end:
                windows.append(TimeWindow(w_start, w_end))
            in_retrograde = False
            rx_start = None

    return windows


def direct_windows(
    planet: str,
    start: datetime | float,
    end: datetime | float,
) -> list[TimeWindow]:
    """Get windows when a planet is direct (not retrograde).

    Args:
        planet: Planet name (e.g., "Mercury", "Venus", "Mars")
        start: Start of search range
        end: End of search range

    Returns:
        List of TimeWindow objects for direct periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    rx = retrograde_windows(planet, start_jd, end_jd)
    return invert_windows(rx, start_jd, end_jd)


# =============================================================================
# Void of Course Moon
# =============================================================================

# Ptolemaic aspects to check for VOC
PTOLEMAIC_ASPECTS = [0, 60, 90, 120, 180]

# Planet sets for VOC modes
TRADITIONAL_PLANETS = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
MODERN_PLANETS = TRADITIONAL_PLANETS + ["Uranus", "Neptune", "Pluto"]


def _get_planet_position(jd: float, planet_name: str) -> float:
    """Get planet longitude at a given Julian Day."""
    _set_ephemeris_path()

    # Map planet names to Swiss Ephemeris constants
    planet_map = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO,
    }

    planet_id = planet_map.get(planet_name)
    if planet_id is None:
        raise ValueError(f"Unknown planet: {planet_name}")

    result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH)
    return result[0][0]


def _find_voc_transition_in_sign(
    sign_start_jd: float,
    ingress_jd: float,
    mode: Literal["traditional", "modern"],
) -> float | None:
    """Find when VOC period starts within a Moon sign period.

    Uses the actual VOC calculation engine for accuracy. Performs a binary
    search to find the transition from "not VOC" to "VOC".

    Args:
        sign_start_jd: JD when Moon entered the current sign
        ingress_jd: JD when Moon will leave the sign
        mode: "traditional" or "modern" aspect mode

    Returns:
        Julian Day when VOC period starts, or None if entire period is VOC
    """
    from stellium import ChartBuilder, Native

    _set_ephemeris_path()

    # Helper to check VOC status at a given JD
    def is_voc_at(jd: float) -> bool:
        dt = _julian_day_to_datetime(jd)
        # Use a neutral location for VOC calculation (doesn't matter for Moon aspects)
        native = Native(dt, (0.0, 0.0))  # (latitude, longitude) tuple
        chart = ChartBuilder.from_native(native).calculate()
        result = chart.voc_moon(aspects=mode)
        return result.is_void

    # Check endpoints
    start_is_voc = is_voc_at(sign_start_jd + 0.001)  # Slightly after ingress
    end_is_voc = is_voc_at(ingress_jd - 0.001)  # Slightly before next ingress

    # If entire period is VOC, return None (caller handles this)
    if start_is_voc and end_is_voc:
        return None

    # If entire period is NOT VOC, there's no VOC window in this sign
    # This shouldn't happen since Moon always goes VOC before leaving sign
    # But return ingress_jd to indicate VOC starts at the very end
    if not start_is_voc and not end_is_voc:
        # Check if there's a brief VOC period we missed
        # The Moon goes VOC after its last aspect, so check near the end
        return ingress_jd

    # If start is not VOC but end is VOC, find the transition
    if not start_is_voc and end_is_voc:
        # Binary search for the transition point
        lo, hi = sign_start_jd, ingress_jd

        # Tolerance: ~1 minute in JD for accuracy
        # This requires ~10-11 iterations per sign period
        tolerance = 1.0 / (24 * 60)

        while hi - lo > tolerance:
            mid = (lo + hi) / 2
            if is_voc_at(mid):
                hi = mid  # VOC, look earlier
            else:
                lo = mid  # Not VOC, look later

        return hi  # Return the point where VOC starts

    # If start is VOC but end is not VOC, something weird is happening
    # (Moon can't go from VOC back to not-VOC without changing signs)
    # Return the start as the VOC transition
    return sign_start_jd


def voc_windows(
    start: datetime | float,
    end: datetime | float,
    mode: Literal["traditional", "modern"] = "traditional",
) -> list[TimeWindow]:
    """Get windows when Moon is void of course.

    A void of course Moon has made its last major Ptolemaic aspect
    (conjunction, sextile, square, trine, opposition) before leaving
    its current sign.

    This implementation uses the actual VOC calculation engine for
    accuracy, with binary search to find VOC transition times.

    Args:
        start: Start of search range
        end: End of search range
        mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)

    Returns:
        List of TimeWindow objects for VOC periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)
    start_dt = start if isinstance(start, datetime) else _julian_day_to_datetime(start)
    end_dt = end if isinstance(end, datetime) else _julian_day_to_datetime(end)

    # Get all Moon sign ingresses with buffer
    from datetime import timedelta

    ingresses = find_all_sign_changes(
        "Moon", start_dt - timedelta(days=3), end_dt + timedelta(days=1)
    )

    if not ingresses:
        return []

    windows: list[TimeWindow] = []

    # Process each Moon sign period
    for i, ingress in enumerate(ingresses):
        # Sign period: from this ingress to the next
        sign_start_jd = ingress.julian_day

        if i + 1 < len(ingresses):
            next_ingress_jd = ingresses[i + 1].julian_day
        else:
            # Last ingress - find the next one
            next_ingress = find_all_sign_changes(
                "Moon",
                _julian_day_to_datetime(ingress.julian_day),
                _julian_day_to_datetime(ingress.julian_day + 3),
            )
            if len(next_ingress) > 1:
                next_ingress_jd = next_ingress[1].julian_day
            else:
                # Estimate ~2.5 days
                next_ingress_jd = ingress.julian_day + 2.5

        # Skip if this sign period is entirely outside our range
        if next_ingress_jd <= start_jd or sign_start_jd >= end_jd:
            continue

        # Find when VOC starts in this sign period
        voc_start_jd = _find_voc_transition_in_sign(
            sign_start_jd, next_ingress_jd, mode
        )

        if voc_start_jd is None:
            # Entire sign period is VOC (rare, but possible)
            voc_start = sign_start_jd
        else:
            voc_start = voc_start_jd

        voc_end = next_ingress_jd

        # Clip to our search range
        voc_start = max(voc_start, start_jd)
        voc_end = min(voc_end, end_jd)

        if voc_start < voc_end:
            windows.append(TimeWindow(voc_start, voc_end))

    return windows


def not_voc_windows(
    start: datetime | float,
    end: datetime | float,
    mode: Literal["traditional", "modern"] = "traditional",
) -> list[TimeWindow]:
    """Get windows when Moon is NOT void of course.

    Args:
        start: Start of search range
        end: End of search range
        mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)

    Returns:
        List of TimeWindow objects for non-VOC periods
    """
    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    voc = voc_windows(start_jd, end_jd, mode)
    return invert_windows(voc, start_jd, end_jd)


# =============================================================================
# Aspect Exactitude Windows
# =============================================================================


def aspect_exact_windows(
    object1: str,
    object2: str,
    aspect_angle: float,
    start: datetime | float,
    end: datetime | float,
    orb: float = 3.0,
) -> list[TimeWindow]:
    """Get windows when two objects are within orb of exact aspect.

    For each exact aspect in the range, computes the window where the
    aspect is within the specified orb. Uses the relative speed of
    the objects to calculate how long before and after exact the
    aspect stays within orb.

    Args:
        object1: First object name (e.g., "Moon")
        object2: Second object name (e.g., "Jupiter")
        aspect_angle: Target angle (0=conjunction, 60=sextile, 90=square,
            120=trine, 180=opposition)
        start: Start of search range (datetime or Julian day)
        end: End of search range (datetime or Julian day)
        orb: Maximum orb in degrees (default 3°)

    Returns:
        List of TimeWindow objects where aspect is within orb

    Example:
        >>> # Get windows when Moon is within 2° of exact trine to Jupiter
        >>> windows = aspect_exact_windows("Moon", "Jupiter", 120.0,
        ...     datetime(2025, 1, 1), datetime(2025, 2, 1), orb=2.0)
        >>> for w in windows:
        ...     print(f"{w.start_datetime} - {w.end_datetime}")
    """
    from stellium.engines.ephemeris import SWISS_EPHEMERIS_IDS
    from stellium.engines.search import _get_position_and_speed, find_all_aspect_exacts

    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    # Find all exact aspects in range
    exacts = find_all_aspect_exacts(object1, object2, aspect_angle, start_jd, end_jd)

    if not exacts:
        return []

    # Get object IDs for speed calculation
    obj1_id = SWISS_EPHEMERIS_IDS[object1]
    obj2_id = SWISS_EPHEMERIS_IDS[object2]

    windows = []

    for exact in exacts:
        # Get speeds at exact time to calculate window duration
        _, speed1 = _get_position_and_speed(obj1_id, exact.julian_day)
        _, speed2 = _get_position_and_speed(obj2_id, exact.julian_day)

        # Relative speed (how fast the separation is changing)
        relative_speed = abs(speed2 - speed1)

        if relative_speed < 0.01:
            # Very slow relative motion - use a default window
            # This can happen with outer planet conjunctions
            duration_days = orb * 2  # Rough estimate
        else:
            # Time to move through orb = orb / speed
            duration_days = orb / relative_speed

        # Window extends before and after exact
        window_start = exact.julian_day - duration_days
        window_end = exact.julian_day + duration_days

        # Clip to search range
        window_start = max(window_start, start_jd)
        window_end = min(window_end, end_jd)

        if window_start < window_end:
            windows.append(TimeWindow(window_start, window_end))

    # Merge overlapping windows (can happen with slow-moving planets)
    return union_windows(windows, [])


# =============================================================================
# Angle Crossing Windows
# =============================================================================


def angle_at_longitude_windows(
    target_longitude: float,
    latitude: float,
    longitude: float,
    angle: str,
    start: datetime | float,
    end: datetime | float,
    orb: float = 1.0,
) -> list[TimeWindow]:
    """Get windows when a chart angle is within orb of a specific longitude.

    Since angles rotate with Earth's rotation (~1° every 4 minutes), the
    window duration depends on the orb:
    - 1° orb → ~8 minute window
    - 3° orb → ~24 minute window

    Args:
        target_longitude: Target longitude in degrees (0-360)
        latitude: Geographic latitude
        longitude: Geographic longitude (negative = West)
        angle: Which angle ("ASC", "MC", "DSC", "IC")
        start: Start of search range (datetime or Julian day)
        end: End of search range (datetime or Julian day)
        orb: Maximum orb in degrees (default 1°)

    Returns:
        List of TimeWindow objects where angle is within orb of target

    Example:
        >>> # Get windows when MC is within 1° of 0° Aries
        >>> windows = angle_at_longitude_windows(
        ...     0.0, 40.7, -74.0, "MC",
        ...     datetime(2025, 1, 1), datetime(2025, 1, 8), orb=1.0
        ... )
        >>> for w in windows:
        ...     print(f"{w.start_datetime} - {w.end_datetime}")
    """
    from stellium.engines.search import find_all_angle_crossings

    start_jd = start if isinstance(start, float) else _datetime_to_julian_day(start)
    end_jd = end if isinstance(end, float) else _datetime_to_julian_day(end)

    # Find all exact crossings in range
    crossings = find_all_angle_crossings(
        target_longitude, latitude, longitude, angle, start_jd, end_jd
    )

    if not crossings:
        return []

    # Angles move ~360° per sidereal day = ~15°/hour = ~0.25°/minute
    # Time for orb = orb / 0.25 minutes = orb * 4 minutes
    # In JD: orb * 4 / (24 * 60) = orb / 360
    orb_duration_jd = orb / 360

    windows = []
    for crossing in crossings:
        window_start = crossing.julian_day - orb_duration_jd
        window_end = crossing.julian_day + orb_duration_jd

        # Clip to search range
        window_start = max(window_start, start_jd)
        window_end = min(window_end, end_jd)

        if window_start < window_end:
            windows.append(TimeWindow(window_start, window_end))

    return windows


__all__ = [
    # Core types
    "TimeWindow",
    # Set operations
    "intersect_windows",
    "union_windows",
    "invert_windows",
    # Interval generators
    "waxing_windows",
    "waning_windows",
    "moon_sign_windows",
    "moon_sign_not_in_windows",
    "retrograde_windows",
    "direct_windows",
    "voc_windows",
    "not_voc_windows",
    "aspect_exact_windows",
    "angle_at_longitude_windows",
]
