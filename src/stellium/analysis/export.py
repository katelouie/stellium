"""
Export utilities for chart collections.

Provides functions to export charts to CSV, JSON, and other formats
for external analysis tools.
"""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from stellium.analysis.frames import (
    _require_pandas,
    aspects_to_dataframe,
    charts_to_dataframe,
    positions_to_dataframe,
)
from stellium.core.models import CalculatedChart


def export_csv(
    charts: Sequence[CalculatedChart],
    path: str | Path,
    schema: Literal["charts", "positions", "aspects"] = "charts",
    **kwargs,
) -> None:
    """
    Export charts to a CSV file.

    Requires pandas: pip install stellium[analysis]

    Args:
        charts: Sequence of CalculatedChart objects
        path: Output file path
        schema: Data schema to use:
            - "charts": One row per chart (default)
            - "positions": One row per celestial position
            - "aspects": One row per aspect
        **kwargs: Additional arguments passed to DataFrame.to_csv()

    Example::

        from stellium.analysis import BatchCalculator, export_csv

        charts = BatchCalculator.from_registry(category="artist").calculate_all()

        # Export chart-level data
        export_csv(charts, "artists.csv")

        # Export all positions
        export_csv(charts, "artists_positions.csv", schema="positions")

        # Export aspects
        export_csv(charts, "artists_aspects.csv", schema="aspects")
    """
    _require_pandas()

    # Convert to DataFrame based on schema
    if schema == "charts":
        df = charts_to_dataframe(charts)
    elif schema == "positions":
        df = positions_to_dataframe(charts)
    elif schema == "aspects":
        df = aspects_to_dataframe(charts)
    else:
        raise ValueError(
            f"Unknown schema: {schema}. Use 'charts', 'positions', or 'aspects'."
        )

    # Set default index behavior
    if "index" not in kwargs:
        kwargs["index"] = False

    # Export to CSV
    df.to_csv(path, **kwargs)


def export_json(
    charts: Sequence[CalculatedChart],
    path: str | Path,
    indent: int | None = 2,
    lines: bool = False,
) -> None:
    """
    Export charts to JSON format.

    Args:
        charts: Sequence of CalculatedChart objects
        path: Output file path
        indent: JSON indentation (None for compact)
        lines: If True, write JSON Lines format (one object per line)

    Example::

        from stellium.analysis import BatchCalculator, export_json

        charts = BatchCalculator.from_registry(category="artist").calculate_all()

        # Standard JSON array
        export_json(charts, "artists.json")

        # JSON Lines (for streaming/large datasets)
        export_json(charts, "artists.jsonl", lines=True)
    """
    path = Path(path)

    if lines:
        # JSON Lines format (one object per line, no indent)
        with open(path, "w") as f:
            for chart in charts:
                f.write(json.dumps(chart.to_dict()) + "\n")
    else:
        # Standard JSON array
        data = [chart.to_dict() for chart in charts]
        with open(path, "w") as f:
            json.dump(data, f, indent=indent, default=str)


def export_parquet(
    charts: Sequence[CalculatedChart],
    path: str | Path,
    schema: Literal["charts", "positions", "aspects"] = "charts",
) -> None:
    """
    Export charts to Parquet format (columnar, efficient for big data).

    Requires pandas and pyarrow: pip install stellium[analysis] pyarrow

    Args:
        charts: Sequence of CalculatedChart objects
        path: Output file path
        schema: Data schema (same as export_csv)

    Example::

        from stellium.analysis import BatchCalculator, export_parquet

        charts = BatchCalculator.from_registry().calculate_all()
        export_parquet(charts, "all_charts.parquet")
    """
    _require_pandas()

    try:
        import pyarrow  # noqa: F401
    except ImportError as err:
        raise ImportError(
            "pyarrow is required for Parquet export. "
            "Install with: pip install pyarrow"
        ) from err

    # Convert to DataFrame based on schema
    if schema == "charts":
        df = charts_to_dataframe(charts)
    elif schema == "positions":
        df = positions_to_dataframe(charts)
    elif schema == "aspects":
        df = aspects_to_dataframe(charts)
    else:
        raise ValueError(f"Unknown schema: {schema}")

    df.to_parquet(path, index=False)


# Convenience aliases
to_csv = export_csv
to_json = export_json
to_parquet = export_parquet
