"""
File I/O utilities for importing and exporting astrological data.

This module provides parsers for common astrology software file formats,
allowing users to import their existing chart collections into Stellium.

Supported formats:
- AAF (Astrodienst Astrological Format): Export format from astro.com
- CSV: Flexible CSV parsing with auto-detection and custom column mapping
- DataFrame: Direct parsing from pandas DataFrames (requires pandas)

Example:
    >>> from stellium.io import parse_aaf, parse_csv, read_csv
    >>>
    >>> # Import from astro.com export
    >>> natives = parse_aaf("my_charts.aaf")
    >>>
    >>> # Import from CSV with auto-detection
    >>> natives = parse_csv("birth_data.csv")
    >>>
    >>> # Import from CSV with custom columns
    >>> natives = read_csv(
    ...     "data.csv",
    ...     name="Full Name",
    ...     date="DOB",
    ...     time="Birth Time",
    ...     location="City",
    ... )
    >>>
    >>> # Import from pandas DataFrame (requires pandas)
    >>> import pandas as pd
    >>> from stellium.io import parse_dataframe
    >>> df = pd.read_excel("birth_data.xlsx")
    >>> natives = parse_dataframe(df)
    >>>
    >>> for native in natives:
    ...     chart = ChartBuilder.from_native(native).calculate()
"""

from stellium.io.aaf import parse_aaf
from stellium.io.csv import CSVColumnMapping, parse_csv, read_csv
from stellium.io.dataframe import (
    dataframe_from_natives,
    parse_dataframe,
    read_dataframe,
)

__all__ = [
    "parse_aaf",
    "parse_csv",
    "read_csv",
    "CSVColumnMapping",
    "parse_dataframe",
    "read_dataframe",
    "dataframe_from_natives",
]
