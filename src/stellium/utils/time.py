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

    # swe.julday() converts calendar date/time to Julian Day number.
    # Since we're giving it UTC, the result is JD(UT) - Universal Time.
    # Both swe.calc_ut() and swe.houses_ex() expect JD(UT), so no
    # Delta T adjustment is needed.
    julian_day_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour_decimal,
    )

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


# ---------------------------------------------------------------------------
# Old Style / New Style — the Julian calendar
# ---------------------------------------------------------------------------

# Britain and its colonies kept the Julian calendar until September 1752; Catholic
# Europe switched in October 1582; Russia not until 1918. So "which calendar is this
# date in?" is a property of the *record*, not of the year — which is why a notable
# born before this backstop must declare it rather than inherit a default.
GREGORIAN_ADOPTION_BACKSTOP = 1753


def julian_to_gregorian(datetime_obj: dt.datetime) -> dt.datetime:
    """Reinterpret an Old Style (Julian calendar) date as its Gregorian equivalent.

    Historical sources give Old Style dates and often do not say so. William Lilly's
    birth is recorded — by Gadbury, by Lilly's own letter to Ashmole, by AstroDatabank
    — as **1 May 1602**. That is a *Julian* date. Handed to an ephemeris as though it
    were Gregorian it computes a chart for a day ten days earlier: Lilly's Sun comes
    out at 10° Taurus instead of 19°, and his Moon lands in **Virgo** rather than
    Capricorn. That is not a rounding error, it is a different chart.

    The conversion is Swiss Ephemeris's own — `julday` in the Julian calendar, `revjul`
    back out in the Gregorian — so we are not maintaining calendar arithmetic. It
    handles the two things that trip hand-rolled versions: the offset is not a constant
    ten days (it is 9 in the 1400s, 7 in the 1200s), and the conversion can roll the
    **year** — Kepler's 27 December 1571 (OS) is 6 January *1572*.

    Example:
        >>> julian_to_gregorian(dt.datetime(1602, 5, 1, 2, 0))
        datetime.datetime(1602, 5, 11, 2, 0)
    """
    hours = (
        datetime_obj.hour
        + datetime_obj.minute / 60
        + datetime_obj.second / 3600
        + datetime_obj.microsecond / 3_600_000_000
    )
    jd = swe.julday(
        datetime_obj.year, datetime_obj.month, datetime_obj.day, hours, swe.JUL_CAL
    )
    year, month, day, _hour = swe.revjul(jd, swe.GREG_CAL)

    # Only the *date* shifts. Carry the clock time through untouched rather than
    # rebuilding it from revjul's float hour, which would introduce rounding into a
    # value that was exact.
    return datetime_obj.replace(year=year, month=month, day=day)


def to_gregorian(datetime_obj: dt.datetime, calendar: str | None = None) -> dt.datetime:
    """Normalise a datetime to the Gregorian calendar the rest of the stack assumes.

    `calendar` is ``"julian"``, ``"gregorian"``, or ``None``. ``None`` means Gregorian
    — the right default for the modern dates that are nearly all of any dataset, and a
    dangerous one for a 17th-century record, which is why the notables loader *requires*
    an early birth to declare which it means instead of inheriting this default.
    """
    if calendar is None or calendar == "gregorian":
        return datetime_obj
    if calendar == "julian":
        return julian_to_gregorian(datetime_obj)
    raise ValueError(
        f"unknown calendar {calendar!r} — expected 'julian', 'gregorian', or None"
    )
