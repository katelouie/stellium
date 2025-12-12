"""
Parser for AAF (Astrodienst Astrological Format) files.

AAF is the export format used by astro.com (Astrodienst). It contains
birth data in a structured text format with two lines per record:
- #A93: Human-readable data (name, date, time, location)
- #B93: Computed data (Julian day, coordinates, timezone)

Example AAF record:
    #A93:Louie,Kate,f,6.1.1994,11:47,Mountain View (Santa Clara County),CA (US)
    #B93:2449359.32431,37n23,122w05,8hw00,0
"""

import re
from pathlib import Path

from stellium.core.models import ChartLocation
from stellium.core.native import Native


def _parse_coordinate(coord_str: str) -> float:
    """
    Parse AAF coordinate format to decimal degrees.

    Format: DDdMM where d is direction (n/s for lat, e/w for lon)
    Examples: "37n23" -> 37.383333, "122w05" -> -122.083333

    Args:
        coord_str: Coordinate string like "37n23" or "122w05"

    Returns:
        Decimal degrees (negative for S/W)
    """
    # Match pattern: digits, direction letter, digits
    match = re.match(r"(\d+)([nsewNSEW])(\d+)", coord_str)
    if not match:
        raise ValueError(f"Invalid coordinate format: {coord_str}")

    degrees = int(match.group(1))
    direction = match.group(2).lower()
    minutes = int(match.group(3))

    decimal = degrees + (minutes / 60.0)

    # South and West are negative
    if direction in ("s", "w"):
        decimal = -decimal

    return decimal


def _parse_timezone_offset(tz_str: str) -> float:
    """
    Parse AAF timezone format to hours offset from UTC.

    Format: Hh[ew]MM where H is hours, e/w is direction, MM is minutes
    Examples: "8hw00" -> -8.0 (UTC-8), "2he00" -> 2.0 (UTC+2)

    Args:
        tz_str: Timezone string like "8hw00" or "5he30"

    Returns:
        Hours offset from UTC (negative for west)
    """
    # Match pattern: digits, h, direction, digits
    match = re.match(r"(\d+)h([ewEW])(\d+)", tz_str)
    if not match:
        raise ValueError(f"Invalid timezone format: {tz_str}")

    hours = int(match.group(1))
    direction = match.group(2).lower()
    minutes = int(match.group(3))

    offset = hours + (minutes / 60.0)

    # West is negative (behind UTC)
    if direction == "w":
        offset = -offset

    return offset


def _parse_a93_line(line: str) -> dict:
    """
    Parse an #A93 line into its components.

    Format: #A93:LastName,FirstName,Gender,DD.MM.YYYY,HH:MM[:SS],City,Region (Country)

    Args:
        line: The #A93 line (without the #A93: prefix)

    Returns:
        Dict with parsed components
    """
    parts = line.split(",")

    if len(parts) < 7:
        raise ValueError(f"Invalid #A93 line (expected 7+ parts): {line}")

    last_name = parts[0].strip()
    first_name = parts[1].strip()
    # gender = parts[2].strip()  # We're ignoring this
    date_str = parts[3].strip()
    time_str = parts[4].strip()

    # Location is everything after the time, rejoined (city might have commas)
    location_parts = parts[5:]
    location_str = ", ".join(p.strip() for p in location_parts)

    # Parse date (DD.MM.YYYY)
    date_match = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", date_str)
    if not date_match:
        raise ValueError(f"Invalid date format: {date_str}")

    day = int(date_match.group(1))
    month = int(date_match.group(2))
    year = int(date_match.group(3))

    # Parse time (HH:MM or HH:MM:SS or HH:MM:SS.ss)
    time_match = re.match(r"(\d{1,2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?", time_str)
    if not time_match:
        raise ValueError(f"Invalid time format: {time_str}")

    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    second = int(time_match.group(3)) if time_match.group(3) else 0

    # Build name
    if last_name and last_name != "*":
        name = f"{first_name} {last_name}".strip()
    else:
        name = first_name.strip()

    return {
        "name": name if name else None,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "location_str": location_str,
    }


def _parse_b93_line(line: str) -> dict:
    """
    Parse a #B93 line into its components.

    Format: #B93:JulianDay,Lat,Lon,Timezone,DST_flag

    Args:
        line: The #B93 line (without the #B93: prefix)

    Returns:
        Dict with parsed components
    """
    parts = line.split(",")

    if len(parts) < 5:
        raise ValueError(f"Invalid #B93 line (expected 5 parts): {line}")

    julian_day = float(parts[0].strip())
    latitude = _parse_coordinate(parts[1].strip())
    longitude = _parse_coordinate(parts[2].strip())
    tz_offset = _parse_timezone_offset(parts[3].strip())
    dst_flag = int(parts[4].strip())

    return {
        "julian_day": julian_day,
        "latitude": latitude,
        "longitude": longitude,
        "tz_offset": tz_offset,
        "dst_flag": dst_flag,
    }


def parse_aaf(path: str | Path) -> list[Native]:
    """
    Parse an AAF (Astrodienst Astrological Format) file into Native objects.

    AAF is the export format from astro.com. Each chart record consists of
    two lines: #A93 (human-readable data) and #B93 (computed values).

    Args:
        path: Path to the AAF file

    Returns:
        List of Native objects, one per chart in the file

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid

    Example:
        >>> natives = parse_aaf("my_charts.aaf")
        >>> len(natives)
        20
        >>> natives[0].name
        'Kate Louie'
        >>> chart = ChartBuilder.from_native(natives[0]).calculate()
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"AAF file not found: {path}")

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    natives = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith("#:"):
            i += 1
            continue

        # Look for #A93 line
        if line.startswith("#A93:"):
            a93_content = line[5:]  # Remove "#A93:" prefix

            # Next non-comment line should be #B93
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith("#B93:"):
                    b93_content = next_line[5:]  # Remove "#B93:" prefix
                    break
                elif next_line.startswith("#:"):
                    # Skip comment lines
                    i += 1
                    continue
                else:
                    raise ValueError(f"Expected #B93 line after #A93, got: {next_line}")
            else:
                raise ValueError("Unexpected end of file: missing #B93 line")

            # Parse both lines
            try:
                a93_data = _parse_a93_line(a93_content)
                b93_data = _parse_b93_line(b93_content)
            except ValueError as e:
                # Log warning and skip this record
                print(f"Warning: Skipping malformed record: {e}")
                i += 1
                continue

            # Create Native using coordinates from B93 and datetime from A93
            # We use the pre-computed coordinates but let Native handle
            # the datetime/timezone processing
            import datetime as dt

            from timezonefinder import TimezoneFinder

            # Find timezone name from coordinates
            tf = TimezoneFinder()
            timezone_name = tf.timezone_at(
                lat=b93_data["latitude"], lng=b93_data["longitude"]
            )
            if not timezone_name:
                timezone_name = "UTC"

            # Create location with pre-computed coordinates
            location = ChartLocation(
                latitude=b93_data["latitude"],
                longitude=b93_data["longitude"],
                name=a93_data["location_str"],
                timezone=timezone_name,
            )

            # Create naive datetime from A93 data
            local_dt = dt.datetime(
                year=a93_data["year"],
                month=a93_data["month"],
                day=a93_data["day"],
                hour=a93_data["hour"],
                minute=a93_data["minute"],
                second=a93_data["second"],
            )

            # Create Native
            native = Native(
                datetime_input=local_dt,
                location_input=location,
                name=a93_data["name"],
            )

            natives.append(native)

        i += 1

    return natives
