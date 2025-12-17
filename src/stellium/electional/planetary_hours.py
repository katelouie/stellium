"""
Planetary Hours calculation for electional astrology.

Planetary hours are a traditional timing system where each hour of the day
is ruled by one of the seven classical planets in the Chaldean order.

The day is divided into 12 "hours" from sunrise to sunset (variable length),
and night into 12 "hours" from sunset to sunrise. The first hour of each day
is ruled by the planet that rules that weekday.

Chaldean order (from slowest to fastest): Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon

Day rulers:
- Sunday: Sun
- Monday: Moon
- Tuesday: Mars
- Wednesday: Mercury
- Thursday: Jupiter
- Friday: Venus
- Saturday: Saturn

Example usage:
    >>> from stellium.electional.planetary_hours import get_planetary_hour, get_planetary_hours_for_day
    >>> hour = get_planetary_hour(datetime.now(), latitude=37.7, longitude=-122.4)
    >>> print(f"Current planetary hour: {hour.ruler}")

    >>> hours = get_planetary_hours_for_day(datetime(2025, 1, 1), latitude=37.7, longitude=-122.4)
    >>> for h in hours[:3]:
    ...     print(f"{h.ruler}: {h.start_local} - {h.end_local}")
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import swisseph as swe

from stellium.data.paths import initialize_ephemeris

# Chaldean order of planets (slowest to fastest)
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Day rulers (first hour of each day)
DAY_RULERS = {
    0: "Moon",  # Monday
    1: "Mars",  # Tuesday
    2: "Mercury",  # Wednesday
    3: "Jupiter",  # Thursday
    4: "Venus",  # Friday
    5: "Saturn",  # Saturday
    6: "Sun",  # Sunday
}


@dataclass(frozen=True)
class PlanetaryHour:
    """A single planetary hour.

    Attributes:
        ruler: The planet ruling this hour
        hour_number: Hour number (1-12 for day, 13-24 for night)
        is_day_hour: True if this is a day hour (sunrise to sunset)
        start_jd: Start time as Julian day
        end_jd: End time as Julian day
        start_utc: Start time as UTC datetime
        end_utc: End time as UTC datetime
    """

    ruler: str
    hour_number: int
    is_day_hour: bool
    start_jd: float
    end_jd: float
    start_utc: datetime
    end_utc: datetime

    @property
    def duration_minutes(self) -> float:
        """Duration of this hour in clock minutes."""
        return (self.end_jd - self.start_jd) * 24 * 60

    def __str__(self) -> str:
        period = "day" if self.is_day_hour else "night"
        return (
            f"{self.ruler} hour ({period} #{self.hour_number % 12 or 12}) "
            f"{self.start_utc.strftime('%H:%M')}-{self.end_utc.strftime('%H:%M')} UTC"
        )


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian day to datetime."""
    result = swe.jdut1_to_utc(jd)
    return datetime(
        int(result[0]),
        int(result[1]),
        int(result[2]),
        int(result[3]),
        int(result[4]),
        int(result[5]),
    )


def _datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian day."""
    return swe.utc_to_jd(
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, swe.GREG_CAL
    )[1]


def get_sunrise_sunset(
    date: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> tuple[float, float]:
    """Get sunrise and sunset times for a given LOCAL date and location.

    The "date" is interpreted as the local calendar date at the given longitude.
    For example, if date is Jan 1, 2025 and longitude is -122° (San Francisco),
    this returns the sunrise/sunset that occur on Jan 1 in Pacific time.

    Args:
        date: The LOCAL date (time component is ignored)
        latitude: Geographic latitude (positive = North)
        longitude: Geographic longitude (positive = East, negative = West)
        altitude: Altitude in meters above sea level

    Returns:
        Tuple of (sunrise_jd, sunset_jd) as Julian day numbers
    """
    initialize_ephemeris()

    # Approximate local midnight in UTC
    # Longitude -122° = UTC-8, so local midnight ≈ 08:00 UTC
    # We use longitude/15 to get approximate timezone offset in hours
    tz_offset_hours = longitude / 15  # Rough approximation
    local_midnight_utc = datetime(date.year, date.month, date.day, 0, 0)

    # Convert to JD and adjust for timezone
    jd_local_midnight = _datetime_to_jd(local_midnight_utc) - tz_offset_hours / 24

    # Start search from before local midnight to catch sunrise
    jd_start = jd_local_midnight - 0.5

    # Note: swisseph uses (longitude, latitude, altitude) order
    geopos = (longitude, latitude, altitude)

    # Find sunrise after jd_start
    res, tret = swe.rise_trans(jd_start, 0, swe.CALC_RISE, geopos)
    if res == -2:
        raise ValueError(f"Sun is circumpolar at latitude {latitude} on {date}")
    sunrise_jd = tret[0]

    # Find sunset after sunrise
    res, tret = swe.rise_trans(sunrise_jd, 0, swe.CALC_SET, geopos)
    if res == -2:
        raise ValueError(f"Sun is circumpolar at latitude {latitude} on {date}")
    sunset_jd = tret[0]

    return sunrise_jd, sunset_jd


def get_day_ruler(date: datetime) -> str:
    """Get the planetary ruler of a given day.

    Args:
        date: The date

    Returns:
        Name of the ruling planet
    """
    weekday = date.weekday()
    return DAY_RULERS[weekday]


def get_hour_ruler(day_ruler: str, hour_number: int) -> str:
    """Get the planetary ruler of a specific hour.

    Args:
        day_ruler: The planet ruling the first hour of the day
        hour_number: Hour number (1-24, where 1-12 are day hours, 13-24 are night)

    Returns:
        Name of the ruling planet for that hour
    """
    # Find starting position in Chaldean order
    start_idx = CHALDEAN_ORDER.index(day_ruler)

    # Move through the sequence (hour 1 = day ruler, hour 2 = next in sequence, etc.)
    ruler_idx = (start_idx + hour_number - 1) % 7

    return CHALDEAN_ORDER[ruler_idx]


def get_planetary_hours_for_day(
    date: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> list[PlanetaryHour]:
    """Get all 24 planetary hours for a given day.

    Returns hours from sunrise of the given date to sunrise of the next date.

    Args:
        date: The date
        latitude: Geographic latitude
        longitude: Geographic longitude
        altitude: Altitude in meters

    Returns:
        List of 24 PlanetaryHour objects (12 day + 12 night)
    """
    # Get sunrise/sunset for this day
    sunrise_jd, sunset_jd = get_sunrise_sunset(date, latitude, longitude, altitude)

    # Get next sunrise for night hours
    next_date = date + timedelta(days=1)
    next_sunrise_jd, _ = get_sunrise_sunset(next_date, latitude, longitude, altitude)

    # Calculate hour lengths
    day_length = sunset_jd - sunrise_jd
    night_length = next_sunrise_jd - sunset_jd
    day_hour_length = day_length / 12
    night_hour_length = night_length / 12

    # Get day ruler
    day_ruler = get_day_ruler(date)

    hours = []

    # Day hours (1-12)
    for i in range(12):
        hour_num = i + 1
        start_jd = sunrise_jd + i * day_hour_length
        end_jd = sunrise_jd + (i + 1) * day_hour_length
        ruler = get_hour_ruler(day_ruler, hour_num)

        hours.append(
            PlanetaryHour(
                ruler=ruler,
                hour_number=hour_num,
                is_day_hour=True,
                start_jd=start_jd,
                end_jd=end_jd,
                start_utc=_jd_to_datetime(start_jd),
                end_utc=_jd_to_datetime(end_jd),
            )
        )

    # Night hours (13-24, but we'll number them 1-12 for night)
    for i in range(12):
        hour_num = i + 13  # Internal numbering for ruler calculation
        start_jd = sunset_jd + i * night_hour_length
        end_jd = sunset_jd + (i + 1) * night_hour_length
        ruler = get_hour_ruler(day_ruler, hour_num)

        hours.append(
            PlanetaryHour(
                ruler=ruler,
                hour_number=hour_num,
                is_day_hour=False,
                start_jd=start_jd,
                end_jd=end_jd,
                start_utc=_jd_to_datetime(start_jd),
                end_utc=_jd_to_datetime(end_jd),
            )
        )

    return hours


def get_planetary_hour(
    dt: datetime,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> PlanetaryHour:
    """Get the planetary hour for a specific datetime.

    Args:
        dt: The datetime (UTC)
        latitude: Geographic latitude
        longitude: Geographic longitude
        altitude: Altitude in meters

    Returns:
        The PlanetaryHour active at the given time
    """
    jd = _datetime_to_jd(dt)

    # Try today first
    hours = get_planetary_hours_for_day(dt, latitude, longitude, altitude)
    for hour in hours:
        if hour.start_jd <= jd < hour.end_jd:
            return hour

    # If not found, might be before today's sunrise - check yesterday's night hours
    yesterday = dt - timedelta(days=1)
    hours = get_planetary_hours_for_day(yesterday, latitude, longitude, altitude)
    for hour in hours:
        if hour.start_jd <= jd < hour.end_jd:
            return hour

    # If still not found, might be after today's night ends - check tomorrow
    tomorrow = dt + timedelta(days=1)
    hours = get_planetary_hours_for_day(tomorrow, latitude, longitude, altitude)
    for hour in hours:
        if hour.start_jd <= jd < hour.end_jd:
            return hour

    raise ValueError(f"Could not determine planetary hour for {dt}")


def get_planetary_hour_at_jd(
    jd: float,
    latitude: float,
    longitude: float,
    altitude: float = 0.0,
) -> PlanetaryHour:
    """Get the planetary hour for a specific Julian day.

    Args:
        jd: Julian day number
        latitude: Geographic latitude
        longitude: Geographic longitude
        altitude: Altitude in meters

    Returns:
        The PlanetaryHour active at the given time
    """
    dt = _jd_to_datetime(jd)
    return get_planetary_hour(dt, latitude, longitude, altitude)


def planetary_hour_windows(
    planet: str,
    latitude: float,
    longitude: float,
    start: datetime | float,
    end: datetime | float,
) -> list[tuple[float, float]]:
    """Get all windows when a specific planet rules the planetary hour.

    Args:
        planet: Planet name ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        latitude: Geographic latitude
        longitude: Geographic longitude
        start: Start of search range (datetime or Julian day)
        end: End of search range (datetime or Julian day)

    Returns:
        List of (start_jd, end_jd) tuples for each planetary hour of that planet
    """
    if planet not in CHALDEAN_ORDER:
        raise ValueError(f"Unknown planet: {planet}. Must be one of {CHALDEAN_ORDER}")

    # Convert to JD if needed
    if isinstance(start, datetime):
        start_jd = _datetime_to_jd(start)
    else:
        start_jd = start

    if isinstance(end, datetime):
        end_jd = _datetime_to_jd(end)
    else:
        end_jd = end

    windows = []

    # Get the date range we need to cover
    start_dt = _jd_to_datetime(start_jd)

    # Iterate through each day
    current_date = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    while _datetime_to_jd(current_date) < end_jd + 1:
        try:
            hours = get_planetary_hours_for_day(current_date, latitude, longitude)

            for hour in hours:
                if hour.ruler == planet:
                    # Check if this hour overlaps with our search range
                    window_start = max(hour.start_jd, start_jd)
                    window_end = min(hour.end_jd, end_jd)

                    if window_start < window_end:
                        windows.append((window_start, window_end))

        except ValueError:
            # Skip days with circumpolar sun
            pass

        current_date = current_date + timedelta(days=1)

    return windows


__all__ = [
    "PlanetaryHour",
    "CHALDEAN_ORDER",
    "DAY_RULERS",
    "get_sunrise_sunset",
    "get_day_ruler",
    "get_hour_ruler",
    "get_planetary_hours_for_day",
    "get_planetary_hour",
    "get_planetary_hour_at_jd",
    "planetary_hour_windows",
]
