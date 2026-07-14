"""
Progression calculation utilities.

Supports multiple progression types, each using a different time key:

- **Secondary** (day-for-a-year): 1 day of motion = 1 year of life.
  The most common type. To find progressions at age 30, look at day 30.
- **Tertiary** (day-for-a-lunar-month): 1 day of motion = 1 lunar month (~27.3 days).
  Faster-moving, useful for timing within a year.
- **Minor** (lunar-month-for-a-year): 1 lunar month of motion = 1 year of life.
  Intermediate rate between secondary and tertiary.

This module provides:

- Progressed datetime calculation for all three types
- Angle adjustment methods (Solar Arc, Naibod)
"""

from dataclasses import replace
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from stellium.core.models import CelestialPosition

# Naibod rate: 59'08" per year = 0.9855... degrees per year
# This is the mean daily motion of the Sun
NAIBOD_RATE_DEGREES_PER_YEAR = 59.1333 / 60  # ~0.9856 degrees

# Mean synodic month (New Moon to New Moon) = 29.530588853 days
# Mean sidereal month (Moon returns to same star) = 27.321661 days
# Tertiary progressions traditionally use the sidereal month
LUNAR_MONTH_DAYS = 27.321661


def calculate_progressed_datetime(
    natal_datetime: datetime,
    target_date: datetime,
    progression_type: Literal["secondary", "tertiary", "minor"] = "secondary",
) -> datetime:
    """
    Calculate progressed datetime using the appropriate time key.

    Each progression type maps real elapsed time to symbolic chart time
    at a different rate:

    - **Secondary** (day-for-a-year): 1 real year → 1 progressed day.
      At age 30, look at day 30 after birth.
    - **Tertiary** (day-for-a-lunar-month): 1 real lunar month → 1 progressed day.
      Moves ~13.4x faster than secondary.
    - **Minor** (lunar-month-for-a-year): 1 real year → 1 progressed lunar month.
      Moves ~27.3x faster than secondary.

    Args:
        natal_datetime: Birth datetime
        target_date: The date you want to progress TO (e.g., "2025-06-15")
        progression_type: "secondary" (default), "tertiary", or "minor"

    Returns:
        The datetime to cast the progressed chart for

    Example:
        >>> from datetime import datetime
        >>> birth = datetime(1994, 1, 6, 11, 47)
        >>> target = datetime(2024, 1, 6)  # 30th birthday
        >>> # Secondary: ~30 days after birth
        >>> progressed = calculate_progressed_datetime(birth, target)
        >>> # Tertiary: ~401 days after birth (30 years × 13.4 lunar months/year)
        >>> progressed = calculate_progressed_datetime(birth, target, "tertiary")
    """
    # Normalize timezones - if one is aware and one is naive, make both naive
    natal_dt = natal_datetime
    target_dt = target_date
    if natal_dt.tzinfo is not None and target_dt.tzinfo is None:
        natal_dt = natal_dt.replace(tzinfo=None)
    elif natal_dt.tzinfo is None and target_dt.tzinfo is not None:
        target_dt = target_dt.replace(tzinfo=None)

    days_elapsed = (target_dt - natal_dt).days

    if progression_type == "secondary":
        # 1 day of real time = 1 year of life → 1 year = 1 progressed day
        years_of_life = days_elapsed / 365.25
        progressed_days = years_of_life

    elif progression_type == "tertiary":
        # 1 day of real time = 1 lunar month of life → 1 lunar month = 1 progressed day
        lunar_months_of_life = days_elapsed / LUNAR_MONTH_DAYS
        progressed_days = lunar_months_of_life

    elif progression_type == "minor":
        # 1 lunar month of real time = 1 year of life → 1 year = 1 progressed lunar month
        years_of_life = days_elapsed / 365.25
        progressed_days = years_of_life * LUNAR_MONTH_DAYS

    else:
        raise ValueError(
            f"Unknown progression_type '{progression_type}'. "
            f"Use 'secondary', 'tertiary', or 'minor'."
        )

    return natal_datetime + timedelta(days=progressed_days)


def calculate_years_elapsed(
    natal_datetime: datetime,
    target_date: datetime,
) -> float:
    """
    Calculate years elapsed between natal date and target date.

    Args:
        natal_datetime: Birth datetime
        target_date: Target date

    Returns:
        Years elapsed as a float (e.g., 30.5 for 30 years 6 months)
    """
    # Normalize timezones - if one is aware and one is naive, make both naive
    natal_dt = natal_datetime
    target_dt = target_date
    if natal_dt.tzinfo is not None and target_dt.tzinfo is None:
        natal_dt = natal_dt.replace(tzinfo=None)
    elif natal_dt.tzinfo is None and target_dt.tzinfo is not None:
        target_dt = target_dt.replace(tzinfo=None)

    days_elapsed = (target_dt - natal_dt).days
    return days_elapsed / 365.25


def calculate_solar_arc(
    natal_sun_longitude: float,
    progressed_sun_longitude: float,
) -> float:
    """
    Calculate solar arc (difference between progressed Sun and natal Sun).

    Solar arc is used to progress angles (ASC, MC) at the same rate
    as the progressed Sun moves.

    Args:
        natal_sun_longitude: Natal Sun position in degrees
        progressed_sun_longitude: Progressed Sun position in degrees

    Returns:
        Solar arc in degrees (always positive, 0-360)

    Example:
        >>> arc = calculate_solar_arc(285.5, 315.2)  # Sun moved ~30°
        >>> print(f"Solar arc: {arc:.2f}°")
    """
    arc = progressed_sun_longitude - natal_sun_longitude

    # Normalize to 0-360 range
    # Handle case where progressed crosses 0° Aries
    while arc < 0:
        arc += 360
    while arc >= 360:
        arc -= 360

    return arc


def calculate_naibod_arc(years_elapsed: float) -> float:
    """
    Calculate Naibod arc (mean Sun rate: 59'08" per year).

    Naibod uses the Sun's average daily motion to progress angles,
    rather than the actual progressed Sun position. This gives a
    consistent, predictable rate of angle progression.

    Args:
        years_elapsed: Years since birth

    Returns:
        Naibod arc in degrees

    Example:
        >>> arc = calculate_naibod_arc(30)  # At age 30
        >>> print(f"Naibod arc: {arc:.2f}°")  # ~29.57°
    """
    return years_elapsed * NAIBOD_RATE_DEGREES_PER_YEAR


def adjust_angles_by_arc(
    positions: tuple["CelestialPosition", ...],
    arc: float,
) -> tuple["CelestialPosition", ...]:
    """
    Adjust angle positions (ASC, MC, etc.) by a given arc.

    Used for Solar Arc and Naibod angle progressions. In these methods,
    angles are moved forward by the calculated arc rather than using
    their natural (quotidian) progressed positions.

    Args:
        positions: Tuple of celestial positions from progressed chart
        arc: Arc in degrees to add to angle positions

    Returns:
        New tuple with adjusted angle positions
    """
    from stellium.core.models import ObjectType

    adjusted = []
    for pos in positions:
        if pos.object_type == ObjectType.ANGLE:
            # Adjust angle longitude by arc
            new_lon = (pos.longitude + arc) % 360
            adjusted.append(replace(pos, longitude=new_lon))
        else:
            # Non-angles pass through unchanged
            adjusted.append(pos)

    return tuple(adjusted)


def normalize_arc(arc: float) -> float:
    """
    Normalize an arc to the range 0-360 degrees.

    Args:
        arc: Arc in degrees (can be negative or > 360)

    Returns:
        Normalized arc in 0-360 range
    """
    while arc < 0:
        arc += 360
    while arc >= 360:
        arc -= 360
    return arc


def calculate_lunar_arc(
    natal_moon_longitude: float,
    progressed_moon_longitude: float,
) -> float:
    """
    Calculate lunar arc (difference between progressed Moon and natal Moon).

    Lunar arc directions move all points at the rate the progressed Moon moves.
    The Moon moves ~12-13 degrees per year in progressions.

    Args:
        natal_moon_longitude: Natal Moon position in degrees
        progressed_moon_longitude: Progressed Moon position in degrees

    Returns:
        Lunar arc in degrees (normalized to 0-360)

    Example:
        >>> arc = calculate_lunar_arc(150.0, 280.0)  # Moon moved ~130°
        >>> print(f"Lunar arc: {arc:.2f}°")
    """
    arc = progressed_moon_longitude - natal_moon_longitude
    return normalize_arc(arc)


def calculate_planetary_arc(
    natal_planet_longitude: float,
    progressed_planet_longitude: float,
) -> float:
    """
    Calculate arc based on any planet's motion.

    This generic function supports Mars arc, Venus arc, Jupiter arc, etc.
    Used for custom planetary arcs and chart ruler arcs.

    Args:
        natal_planet_longitude: Natal planet position in degrees
        progressed_planet_longitude: Progressed planet position in degrees

    Returns:
        Planetary arc in degrees (normalized to 0-360)

    Example:
        >>> arc = calculate_planetary_arc(45.0, 75.0)  # Planet moved ~30°
        >>> print(f"Planet arc: {arc:.2f}°")
    """
    arc = progressed_planet_longitude - natal_planet_longitude
    return normalize_arc(arc)
