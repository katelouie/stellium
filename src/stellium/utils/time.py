"""Time and Julian Day conversion utilities.

These utilities handle conversion between Python datetime objects and
Julian Day numbers, which are used internally by Swiss Ephemeris for
all astronomical calculations.
"""

import datetime as dt
from math import floor

import pytz
import swisseph as swe


def datetime_to_julian_day(datetime_obj: dt.datetime) -> float:
    """
    Convert a Python datetime to Julian Day (UT).

    Args:
        datetime_obj: A timezone-aware datetime object. If naive (no timezone),
                     UTC is assumed.

    Returns:
        Julian Day number (Universal Time)

    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> dt = datetime(2025, 1, 6, 12, 0, 0, tzinfo=pytz.UTC)
        >>> jd = datetime_to_julian_day(dt)
        >>> print(f"{jd:.6f}")  # ~2460682.0
    """
    # Ensure we have UTC
    if datetime_obj.tzinfo is None:
        utc_dt = pytz.UTC.localize(datetime_obj)
    elif datetime_obj.tzinfo != pytz.UTC:
        utc_dt = datetime_obj.astimezone(pytz.UTC)
    else:
        utc_dt = datetime_obj

    # Calculate decimal hour
    hour_decimal = (
        utc_dt.hour
        + (utc_dt.minute / 60.0)
        + (utc_dt.second / 3600.0)
        + (utc_dt.microsecond / 3600000000.0)
    )

    # swe.julday returns Ephemeris Time (ET)
    julian_day_et = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour_decimal,
    )

    # Convert to Universal Time (UT) by subtracting Delta T
    # Delta T is the difference between ET and UT
    delta_t = swe.deltat(julian_day_et)
    julian_day_ut = julian_day_et - delta_t

    return julian_day_ut


def julian_day_to_datetime(jd: float, timezone: str = "UTC") -> dt.datetime:
    """
    Convert Julian Day to Python datetime.

    Args:
        jd: Julian day number (Universal Time)
        timezone: Target timezone string (default UTC). The datetime is first
                 calculated in UTC, then converted to the target timezone.

    Returns:
        Timezone-aware datetime object

    Example:
        >>> jd = 2460682.0  # Noon on Jan 6, 2025
        >>> dt_obj = julian_day_to_datetime(jd)
        >>> print(dt_obj.strftime("%Y-%m-%d %H:%M"))
        2025-01-06 12:00
    """
    # swe.revjul returns (year, month, day, hour_as_float)
    year, month, day, h_float = swe.revjul(jd)

    # Extract hours, minutes, seconds from the float hour
    hour = floor(h_float)
    h_float = (h_float - hour) * 60
    minute = floor(h_float)
    h_float = (h_float - minute) * 60
    second = int(round(h_float))

    # Handle edge cases where rounding pushes values over
    if second == 60:
        minute += 1
        second = 0
    if minute == 60:
        hour += 1
        minute = 0
    if hour == 24:
        # Need to advance the day - let datetime handle it
        base_dt = dt.datetime(year, month, day, 0, 0, 0)
        base_dt = base_dt + dt.timedelta(days=1)
        year, month, day = base_dt.year, base_dt.month, base_dt.day
        hour = 0

    # Create datetime in UTC (Julian days are in UT)
    utc_dt = dt.datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)

    # Convert to target timezone if not UTC
    if timezone != "UTC":
        tz = pytz.timezone(timezone)
        return utc_dt.astimezone(tz)

    return utc_dt


def offset_julian_day(jd: float, days: float) -> float:
    """
    Offset a Julian Day by a number of days.

    Args:
        jd: Starting Julian Day number
        days: Number of days to add (can be negative)

    Returns:
        New Julian Day number

    Example:
        >>> jd = 2460682.0  # Jan 6, 2025
        >>> jd_tomorrow = offset_julian_day(jd, 1.0)
        >>> jd_yesterday = offset_julian_day(jd, -1.0)
    """
    return jd + days
