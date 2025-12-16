"""
Parser for pandas DataFrames containing birth data.

This module provides the same flexible parsing as the CSV module,
but works directly with in-memory pandas DataFrames. This is useful
when data comes from databases, Excel files, or other pandas-compatible
sources.

Example usage:
    >>> import pandas as pd
    >>> from stellium.io import parse_dataframe, read_dataframe
    >>>
    >>> # Load data from any source
    >>> df = pd.read_excel("birth_data.xlsx")
    >>> # Or: df = pd.read_sql("SELECT * FROM births", connection)
    >>> # Or: df = pd.read_parquet("data.parquet")
    >>>
    >>> # Auto-detect columns
    >>> natives = parse_dataframe(df)
    >>>
    >>> # Or specify columns explicitly
    >>> natives = read_dataframe(
    ...     df,
    ...     name="Full Name",
    ...     date="DOB",
    ...     time="Birth Time",
    ...     latitude="Lat",
    ...     longitude="Long",
    ... )
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from stellium.core.native import Native
from stellium.io.csv import (
    CSVColumnMapping,
    _auto_detect_mapping,
    _row_to_native,
)

if TYPE_CHECKING:
    import pandas as pd


def _check_pandas_available() -> None:
    """Check if pandas is available, raise helpful error if not."""
    try:
        import pandas  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "pandas is required for DataFrame parsing. "
            "Install it with: pip install pandas"
        ) from e


def parse_dataframe(
    df: pd.DataFrame,
    mapping: CSVColumnMapping | None = None,
    *,
    skip_errors: bool = True,
) -> list[Native]:
    """
    Parse a pandas DataFrame containing birth data into Native objects.

    This function supports flexible DataFrame formats through column mapping.
    If no mapping is provided, it will auto-detect columns based on
    common naming conventions.

    Args:
        df: pandas DataFrame with birth data
        mapping: Optional column mapping configuration. If None, auto-detects
                 columns from DataFrame column names.
        skip_errors: If True, skip rows that fail to parse and continue.
                     If False, raise an exception on the first error.

    Returns:
        List of Native objects, one per valid row in the DataFrame

    Raises:
        ImportError: If pandas is not installed
        ValueError: If required columns are missing or skip_errors=False and
                    a row fails to parse

    Example:
        >>> import pandas as pd
        >>> from stellium.io import parse_dataframe
        >>>
        >>> df = pd.DataFrame({
        ...     "name": ["Kate Louie", "Albert Einstein"],
        ...     "date": ["1994-01-06", "1879-03-14"],
        ...     "time": ["11:47", "11:30"],
        ...     "latitude": [37.3861, 48.4011],
        ...     "longitude": [-122.0839, 9.9876],
        ... })
        >>> natives = parse_dataframe(df)
        >>> len(natives)
        2

        >>> # With custom column mapping
        >>> mapping = CSVColumnMapping(
        ...     name="Full Name",
        ...     date="DOB",
        ...     latitude="Lat",
        ...     longitude="Lon",
        ... )
        >>> natives = parse_dataframe(df, mapping=mapping)
    """
    _check_pandas_available()

    natives: list[Native] = []
    errors: list[tuple[int, str]] = []

    # Get column names as list
    headers = list(df.columns)

    # Auto-detect mapping if not provided
    if mapping is None:
        mapping = _auto_detect_mapping(headers)

    # Iterate over DataFrame rows
    for idx, row in df.iterrows():
        # Convert row to dict (handling both string and non-string values)
        row_dict = {
            col: str(val) if val is not None else "" for col, val in row.items()
        }

        try:
            native = _row_to_native(row_dict, mapping)
            natives.append(native)
        except Exception as e:
            if skip_errors:
                errors.append((idx, str(e)))
            else:
                raise ValueError(f"Error parsing row {idx}: {e}") from e

    if errors:
        print(f"Warning: Skipped {len(errors)} row(s) with errors:")
        for row_idx, error in errors[:5]:  # Show first 5 errors
            print(f"  Row {row_idx}: {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    return natives


def read_dataframe(
    df: pd.DataFrame,
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
    Simple interface for reading pandas DataFrames with common column configurations.

    This is a convenience wrapper around parse_dataframe() that allows specifying
    column names as keyword arguments.

    Args:
        df: pandas DataFrame with birth data
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
        >>> import pandas as pd
        >>> from stellium.io import read_dataframe
        >>>
        >>> df = pd.DataFrame({
        ...     "Person": ["Kate Louie"],
        ...     "Birthday": ["1994-01-06"],
        ...     "Birth Time": ["11:47"],
        ...     "Lat": [37.3861],
        ...     "Long": [-122.0839],
        ... })
        >>>
        >>> natives = read_dataframe(
        ...     df,
        ...     name="Person",
        ...     date="Birthday",
        ...     time="Birth Time",
        ...     latitude="Lat",
        ...     longitude="Long",
        ... )
    """
    _check_pandas_available()

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

    return parse_dataframe(df, mapping if has_explicit_mapping else None)


def dataframe_from_natives(
    natives: list[Native],
    *,
    include_coords: bool = True,
    include_timezone: bool = False,
) -> pd.DataFrame:
    """
    Convert a list of Native objects back to a pandas DataFrame.

    This is useful for exporting processed data or for round-trip operations.

    Args:
        natives: List of Native objects to convert
        include_coords: Include latitude/longitude columns (default: True)
        include_timezone: Include timezone column (default: False)

    Returns:
        pandas DataFrame with birth data

    Example:
        >>> from stellium.io import parse_csv, dataframe_from_natives
        >>>
        >>> natives = parse_csv("birth_data.csv")
        >>> df = dataframe_from_natives(natives)
        >>> df.to_excel("birth_data.xlsx")  # Export to Excel
    """
    _check_pandas_available()
    import pandas as pd

    rows = []
    for native in natives:
        row = {
            "name": native.name or "",
            "date": native.datetime.utc_datetime.strftime("%Y-%m-%d"),
            "time": native.datetime.utc_datetime.strftime("%H:%M:%S"),
            "location": native.location.name or "",
        }

        if include_coords:
            row["latitude"] = native.location.latitude
            row["longitude"] = native.location.longitude

        if include_timezone:
            row["timezone"] = native.location.timezone

        rows.append(row)

    return pd.DataFrame(rows)
