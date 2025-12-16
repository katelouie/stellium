"""
Parser for CSV files containing birth data.

CSV files are a common format for batch chart data. This module provides
flexible parsing with configurable column mapping to accommodate different
CSV formats and naming conventions.

Example CSV formats supported:

    # Standard format (auto-detected):
    name,date,time,location
    Kate Louie,1994-01-06,11:47,Mountain View CA

    # Combined datetime:
    name,datetime,place
    Kate,1994-01-06 11:47,37.3861,-122.0839

    # Separate date components:
    first_name,last_name,year,month,day,hour,minute,latitude,longitude
    Kate,Louie,1994,1,6,11,47,37.3861,-122.0839

    # With timezone:
    Name,Birth Date,Birth Time,City,Timezone
    Kate Louie,01/06/1994,11:47 AM,Mountain View CA,America/Los_Angeles
"""

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stellium.core.models import ChartLocation
from stellium.core.native import Native


@dataclass
class CSVColumnMapping:
    """
    Configuration for mapping CSV columns to Native fields.

    This allows flexible handling of different CSV formats. All column names
    are case-insensitive and support multiple aliases.

    Attributes:
        name: Column(s) for person/event name. Can be a single column name
              or a tuple for (first_name, last_name) to combine.
        datetime: Column for combined datetime string (e.g., "1994-01-06 11:47")
        date: Column for date only (when datetime is split)
        time: Column for time only (when datetime is split)
        year: Column for year (when date is split into components)
        month: Column for month
        day: Column for day
        hour: Column for hour (when time is split into components)
        minute: Column for minute
        second: Column for second
        location: Column for location string (geocoded if no lat/lon, or used
                  as display name if lat/lon are provided)
        latitude: Column for latitude (when using coordinates)
        longitude: Column for longitude (when using coordinates)
        timezone: Column for timezone name (e.g., "America/Los_Angeles")
        time_unknown: Column indicating if birth time is unknown (bool/flag)

    Location handling:
        - If latitude + longitude are provided: Uses coordinates directly.
          If location is also provided, it's used as the display name.
        - If only location is provided (no lat/lon): Geocodes the string.
    """

    # Name field(s)
    name: str | tuple[str, str] | None = None

    # Datetime options (in order of precedence)
    datetime: str | None = None  # Combined datetime
    date: str | None = None  # Date only
    time: str | None = None  # Time only

    # Date components (used if date column not found)
    year: str | None = None
    month: str | None = None
    day: str | None = None

    # Time components (used if time column not found)
    hour: str | None = None
    minute: str | None = None
    second: str | None = None

    # Location options
    location: str | None = None  # String to geocode, or display name with coords
    latitude: str | None = None  # Numeric latitude
    longitude: str | None = None  # Numeric longitude

    # Optional fields
    timezone: str | None = None  # Timezone name
    time_unknown: str | None = None  # Flag for unknown birth time

    # Date/time format hints
    date_format: str | None = None  # e.g., "%m/%d/%Y" or "%d.%m.%Y"
    time_format: str | None = None  # e.g., "%I:%M %p" (12-hour with AM/PM)
    datetime_format: str | None = None  # e.g., "%Y-%m-%d %H:%M"


# Default column name aliases (case-insensitive)
DEFAULT_ALIASES: dict[str, list[str]] = {
    "name": ["name", "full_name", "fullname", "person", "subject", "native"],
    "first_name": ["first_name", "firstname", "first", "given_name", "givenname"],
    "last_name": ["last_name", "lastname", "last", "surname", "family_name"],
    "datetime": ["datetime", "date_time", "birth_datetime", "birthdatetime", "dob"],
    "date": ["date", "birth_date", "birthdate", "dob", "birthday"],
    "time": ["time", "birth_time", "birthtime", "tob", "time_of_birth"],
    "year": ["year", "birth_year", "yr"],
    "month": ["month", "birth_month", "mon", "mo"],
    "day": ["day", "birth_day", "dy"],
    "hour": ["hour", "hr", "hours"],
    "minute": ["minute", "min", "minutes"],
    "second": ["second", "sec", "seconds"],
    "location": [
        "location",
        "place",
        "birthplace",
        "birth_place",
        "city",
        "address",
        "pob",
        "location_name",
        "place_name",
        "city_name",
        "birth_city",
        "birth_location",
    ],
    "latitude": ["latitude", "lat", "birth_latitude"],
    "longitude": ["longitude", "lon", "lng", "long", "birth_longitude"],
    "timezone": ["timezone", "tz", "time_zone", "tzname"],
    "time_unknown": [
        "time_unknown",
        "unknown_time",
        "no_time",
        "time_uncertain",
        "approximate_time",
    ],
}


def _find_column(
    headers: list[str], target: str, aliases: dict[str, list[str]] | None = None
) -> str | None:
    """
    Find a column name in headers using aliases.

    Args:
        headers: List of CSV column headers
        target: The field we're looking for (e.g., "name", "date")
        aliases: Optional custom aliases dict

    Returns:
        The matching header name, or None if not found
    """
    aliases = aliases or DEFAULT_ALIASES
    target_aliases = aliases.get(target, [target])

    # Normalize headers for case-insensitive matching
    header_map = {h.lower().strip(): h for h in headers}

    for alias in target_aliases:
        if alias.lower() in header_map:
            return header_map[alias.lower()]

    return None


def _auto_detect_mapping(headers: list[str]) -> CSVColumnMapping:
    """
    Auto-detect column mapping from CSV headers.

    Args:
        headers: List of CSV column headers

    Returns:
        CSVColumnMapping with detected column names
    """
    mapping = CSVColumnMapping()

    # Try to find name column
    name_col = _find_column(headers, "name")
    if name_col:
        mapping.name = name_col
    else:
        # Try first_name + last_name
        first = _find_column(headers, "first_name")
        last = _find_column(headers, "last_name")
        if first and last:
            mapping.name = (first, last)
        elif first:
            mapping.name = first

    # Datetime detection
    mapping.datetime = _find_column(headers, "datetime")
    mapping.date = _find_column(headers, "date")
    mapping.time = _find_column(headers, "time")

    # Date components
    mapping.year = _find_column(headers, "year")
    mapping.month = _find_column(headers, "month")
    mapping.day = _find_column(headers, "day")

    # Time components
    mapping.hour = _find_column(headers, "hour")
    mapping.minute = _find_column(headers, "minute")
    mapping.second = _find_column(headers, "second")

    # Location
    mapping.location = _find_column(headers, "location")
    mapping.latitude = _find_column(headers, "latitude")
    mapping.longitude = _find_column(headers, "longitude")

    # Optional
    mapping.timezone = _find_column(headers, "timezone")
    mapping.time_unknown = _find_column(headers, "time_unknown")

    return mapping


def _parse_date_string(
    date_str: str, format_hint: str | None = None
) -> tuple[int, int, int]:
    """
    Parse a date string into (year, month, day).

    Supports various common formats:
    - ISO: 1994-01-06
    - US: 01/06/1994, 1/6/1994
    - EU: 06.01.1994, 6.1.1994
    - Text: January 6, 1994

    Args:
        date_str: The date string to parse
        format_hint: Optional strptime format string

    Returns:
        Tuple of (year, month, day)
    """
    date_str = date_str.strip()

    # Try explicit format first
    if format_hint:
        try:
            parsed = dt.datetime.strptime(date_str, format_hint)
            return (parsed.year, parsed.month, parsed.day)
        except ValueError:
            pass  # Fall through to auto-detection

    # Common formats to try
    formats = [
        "%Y-%m-%d",  # ISO: 1994-01-06
        "%Y/%m/%d",  # 1994/01/06
        "%m/%d/%Y",  # US: 01/06/1994
        "%m-%d-%Y",  # US: 01-06-1994
        "%d/%m/%Y",  # EU: 06/01/1994
        "%d-%m-%Y",  # EU: 06-01-1994
        "%d.%m.%Y",  # EU: 06.01.1994
        "%B %d, %Y",  # January 6, 1994
        "%b %d, %Y",  # Jan 6, 1994
        "%d %B %Y",  # 6 January 1994
        "%d %b %Y",  # 6 Jan 1994
    ]

    for fmt in formats:
        try:
            parsed = dt.datetime.strptime(date_str, fmt)
            return (parsed.year, parsed.month, parsed.day)
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {date_str}")


def _parse_time_string(
    time_str: str, format_hint: str | None = None
) -> tuple[int, int, int]:
    """
    Parse a time string into (hour, minute, second).

    Supports:
    - 24-hour: 11:47, 11:47:30
    - 12-hour: 11:47 AM, 11:47:30 PM

    Args:
        time_str: The time string to parse
        format_hint: Optional strptime format string

    Returns:
        Tuple of (hour, minute, second)
    """
    time_str = time_str.strip()

    # Try explicit format first
    if format_hint:
        try:
            parsed = dt.datetime.strptime(time_str, format_hint)
            return (parsed.hour, parsed.minute, parsed.second)
        except ValueError:
            pass

    # Common formats to try
    formats = [
        "%H:%M:%S",  # 11:47:30
        "%H:%M",  # 11:47
        "%I:%M:%S %p",  # 11:47:30 AM
        "%I:%M %p",  # 11:47 AM
        "%I:%M:%S%p",  # 11:47:30AM (no space)
        "%I:%M%p",  # 11:47AM
    ]

    for fmt in formats:
        try:
            parsed = dt.datetime.strptime(time_str, fmt)
            return (parsed.hour, parsed.minute, parsed.second)
        except ValueError:
            continue

    raise ValueError(f"Could not parse time: {time_str}")


def _parse_datetime_string(
    datetime_str: str, format_hint: str | None = None
) -> dt.datetime:
    """
    Parse a combined datetime string.

    Args:
        datetime_str: The datetime string to parse
        format_hint: Optional strptime format string

    Returns:
        datetime object
    """
    datetime_str = datetime_str.strip()

    # Try explicit format first
    if format_hint:
        try:
            return dt.datetime.strptime(datetime_str, format_hint)
        except ValueError:
            pass

    # Common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",  # ISO with T
        "%Y-%m-%dT%H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    ]

    for fmt in formats:
        try:
            return dt.datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Could not parse datetime: {datetime_str}")


def _get_value(row: dict[str, str], col: str | None) -> str | None:
    """Get a value from a row, handling missing columns gracefully."""
    if col is None:
        return None
    return row.get(col, "").strip() or None


def _parse_bool(value: str | None) -> bool:
    """Parse a boolean value from various string representations."""
    if value is None:
        return False
    value = value.lower().strip()
    return value in ("true", "yes", "1", "y", "t", "x", "unknown")


def _row_to_native(row: dict[str, str], mapping: CSVColumnMapping) -> Native:
    """
    Convert a CSV row to a Native object using the column mapping.

    Args:
        row: Dictionary of column_name -> value
        mapping: The column mapping configuration

    Returns:
        Native object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # === Parse Name ===
    name = None
    if mapping.name:
        if isinstance(mapping.name, tuple):
            first = _get_value(row, mapping.name[0]) or ""
            last = _get_value(row, mapping.name[1]) or ""
            name = f"{first} {last}".strip() or None
        else:
            name = _get_value(row, mapping.name)

    # === Parse DateTime ===
    datetime_obj: dt.datetime | None = None

    # Option 1: Combined datetime column
    if mapping.datetime:
        datetime_str = _get_value(row, mapping.datetime)
        if datetime_str:
            datetime_obj = _parse_datetime_string(datetime_str, mapping.datetime_format)

    # Option 2: Separate date and time columns
    if datetime_obj is None and mapping.date:
        date_str = _get_value(row, mapping.date)
        if date_str:
            year, month, day = _parse_date_string(date_str, mapping.date_format)

            # Get time
            hour, minute, second = 12, 0, 0  # Default to noon
            if mapping.time:
                time_str = _get_value(row, mapping.time)
                if time_str:
                    hour, minute, second = _parse_time_string(
                        time_str, mapping.time_format
                    )

            datetime_obj = dt.datetime(year, month, day, hour, minute, second)

    # Option 3: Individual date/time components
    if datetime_obj is None and mapping.year:
        year_str = _get_value(row, mapping.year)
        month_str = _get_value(row, mapping.month)
        day_str = _get_value(row, mapping.day)

        if year_str and month_str and day_str:
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)

            # Get time components
            hour = int(_get_value(row, mapping.hour) or 12)
            minute = int(_get_value(row, mapping.minute) or 0)
            second = int(_get_value(row, mapping.second) or 0)

            datetime_obj = dt.datetime(year, month, day, hour, minute, second)

    if datetime_obj is None:
        raise ValueError("Could not determine datetime from row")

    # === Parse Location ===
    location_input: Any = None

    # Get location name (used as display name or for geocoding)
    location_str = _get_value(row, mapping.location) if mapping.location else None

    # Option 1: Latitude and longitude columns
    lat_str = _get_value(row, mapping.latitude)
    lon_str = _get_value(row, mapping.longitude)
    if lat_str and lon_str:
        latitude = float(lat_str)
        longitude = float(lon_str)

        # If we also have a location name, create a ChartLocation with it
        if location_str:
            # Use timezonefinder to get timezone from coordinates
            from timezonefinder import TimezoneFinder

            tf = TimezoneFinder()
            timezone_name = tf.timezone_at(lat=latitude, lng=longitude) or "UTC"

            location_input = ChartLocation(
                latitude=latitude,
                longitude=longitude,
                name=location_str,
                timezone=timezone_name,
            )
        else:
            # Just use coordinates tuple (Native will handle timezone lookup)
            location_input = (latitude, longitude)

    # Option 2: Location string to geocode (no coordinates)
    elif location_str:
        location_input = location_str

    if location_input is None:
        raise ValueError("Could not determine location from row")

    # === Parse Optional Fields ===
    time_unknown = False
    if mapping.time_unknown:
        time_unknown = _parse_bool(_get_value(row, mapping.time_unknown))

    # If no time column was found/provided, mark as unknown
    if not time_unknown:
        has_time = bool(
            mapping.time
            or mapping.hour
            or (mapping.datetime and ":" in str(_get_value(row, mapping.datetime)))
        )
        if not has_time:
            time_unknown = True

    # Create and return Native
    return Native(
        datetime_input=datetime_obj,
        location_input=location_input,
        name=name,
        time_unknown=time_unknown,
    )


def parse_csv(
    path: str | Path,
    mapping: CSVColumnMapping | None = None,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    skip_errors: bool = True,
) -> list[Native]:
    """
    Parse a CSV file containing birth data into Native objects.

    This function supports flexible CSV formats through column mapping.
    If no mapping is provided, it will auto-detect columns based on
    common naming conventions.

    Args:
        path: Path to the CSV file
        mapping: Optional column mapping configuration. If None, auto-detects
                 columns from headers.
        delimiter: CSV delimiter character (default: comma)
        encoding: File encoding (default: utf-8)
        skip_errors: If True, skip rows that fail to parse and continue.
                     If False, raise an exception on the first error.

    Returns:
        List of Native objects, one per valid row in the CSV

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing or skip_errors=False and
                    a row fails to parse

    Example:
        # Auto-detect columns
        >>> natives = parse_csv("birth_data.csv")

        # Custom column mapping
        >>> mapping = CSVColumnMapping(
        ...     name="Full Name",
        ...     date="DOB",
        ...     time="Birth Time",
        ...     location="Birth Place",
        ... )
        >>> natives = parse_csv("birth_data.csv", mapping=mapping)

        # With date format hint for ambiguous dates
        >>> mapping = CSVColumnMapping(
        ...     date="date",
        ...     date_format="%d/%m/%Y",  # European format
        ... )
        >>> natives = parse_csv("european_data.csv", mapping=mapping)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    natives: list[Native] = []
    errors: list[tuple[int, str]] = []

    with open(path, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no headers")

        headers = list(reader.fieldnames)

        # Auto-detect mapping if not provided
        if mapping is None:
            mapping = _auto_detect_mapping(headers)
        else:
            # Validate that mapped columns exist
            # (User-provided mapping should use actual column names)
            pass

        for i, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                native = _row_to_native(row, mapping)
                natives.append(native)
            except Exception as e:
                if skip_errors:
                    errors.append((i, str(e)))
                else:
                    raise ValueError(f"Error parsing row {i}: {e}") from e

    if errors:
        print(f"Warning: Skipped {len(errors)} row(s) with errors:")
        for row_num, error in errors[:5]:  # Show first 5 errors
            print(f"  Row {row_num}: {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    return natives


# Convenience function for simple usage
def read_csv(
    path: str | Path,
    *,
    name: str | tuple[str, str] | None = None,
    datetime: str | None = None,
    date: str | None = None,
    time: str | None = None,
    location: str | None = None,
    latitude: str | None = None,
    longitude: str | None = None,
    date_format: str | None = None,
    time_format: str | None = None,
) -> list[Native]:
    """
    Simple interface for reading CSV files with common column configurations.

    This is a convenience wrapper around parse_csv() that allows specifying
    column names as keyword arguments.

    Args:
        path: Path to the CSV file
        name: Column name for person/event name, or tuple of (first, last)
        datetime: Column name for combined datetime
        date: Column name for date
        time: Column name for time
        location: Column name for location string
        latitude: Column name for latitude
        longitude: Column name for longitude
        date_format: strptime format for dates (e.g., "%d/%m/%Y")
        time_format: strptime format for times (e.g., "%I:%M %p")

    Returns:
        List of Native objects

    Example:
        # Simple auto-detection
        >>> natives = read_csv("data.csv")

        # Specify key columns
        >>> natives = read_csv(
        ...     "data.csv",
        ...     name="Full Name",
        ...     date="DOB",
        ...     time="Birth Time",
        ...     location="City",
        ... )

        # Combined first/last name
        >>> natives = read_csv(
        ...     "data.csv",
        ...     name=("First Name", "Last Name"),
        ...     datetime="Birth DateTime",
        ...     latitude="Lat",
        ...     longitude="Long",
        ... )
    """
    mapping = CSVColumnMapping(
        name=name,
        datetime=datetime,
        date=date,
        time=time,
        location=location,
        latitude=latitude,
        longitude=longitude,
        date_format=date_format,
        time_format=time_format,
    )

    # If all mapping fields are None, use auto-detection
    has_explicit_mapping = any(
        [name, datetime, date, time, location, latitude, longitude]
    )

    return parse_csv(path, mapping if has_explicit_mapping else None)
