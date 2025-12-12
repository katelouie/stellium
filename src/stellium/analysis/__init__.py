"""
Data analysis tools for Stellium.

This module provides tools for large-scale astrological data analysis:

- **BatchCalculator**: Efficiently calculate many charts at once
- **DataFrame builders**: Convert charts to pandas DataFrames
- **ChartQuery**: Filter charts by astrological criteria
- **ChartStats**: Aggregate statistics across chart collections
- **Export utilities**: Save to CSV, JSON, Parquet

Requires pandas for DataFrame features: pip install stellium[analysis]

Example::

    from stellium.analysis import BatchCalculator, ChartStats, charts_to_dataframe

    # Calculate charts for all scientists in the registry
    charts = (BatchCalculator
        .from_registry(category="scientist", verified=True)
        .with_aspects()
        .calculate_all())

    # Convert to DataFrame for analysis
    df = charts_to_dataframe(charts)

    # Compute statistics
    stats = ChartStats(charts)
    print(stats.element_distribution())
    print(stats.sign_distribution("Sun"))
"""

from stellium.analysis.batch import BatchCalculator
from stellium.analysis.export import export_csv, export_json, export_parquet
from stellium.analysis.frames import (
    aspects_to_dataframe,
    charts_to_dataframe,
    positions_to_dataframe,
)
from stellium.analysis.queries import ChartQuery
from stellium.analysis.stats import ChartStats

__all__ = [
    # Batch calculation
    "BatchCalculator",
    # DataFrame conversion
    "charts_to_dataframe",
    "positions_to_dataframe",
    "aspects_to_dataframe",
    # Query interface
    "ChartQuery",
    # Statistics
    "ChartStats",
    # Export utilities
    "export_csv",
    "export_json",
    "export_parquet",
]
