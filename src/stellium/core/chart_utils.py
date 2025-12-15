"""Utility functions for chart type handling.

This module provides centralized utilities for working with different chart types
(CalculatedChart, MultiChart, Comparison) without requiring direct imports that
could cause circular dependencies.

The functions use duck-typing (hasattr checks) where necessary to avoid importing
MultiChart or Comparison directly, which helps prevent circular import issues.

Example usage:
    from stellium.core.chart_utils import get_all_charts, get_chart_labels

    def process_chart(chart):
        charts = get_all_charts(chart)
        labels = get_chart_labels(chart)
        for c, label in zip(charts, labels):
            print(f"{label}: {c.datetime}")
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart


def is_single_chart(chart: Any) -> bool:
    """Check if chart is a single CalculatedChart (not UnknownTimeChart or multi-chart).

    Args:
        chart: Any chart-like object

    Returns:
        True if chart is a single CalculatedChart (not UnknownTimeChart)
    """
    # Import here to avoid circular imports
    from stellium.core.models import CalculatedChart, UnknownTimeChart

    return isinstance(chart, CalculatedChart) and not isinstance(
        chart, UnknownTimeChart
    )


def is_unknown_time_chart(chart: Any) -> bool:
    """Check if chart is an UnknownTimeChart.

    Args:
        chart: Any chart-like object

    Returns:
        True if chart is an UnknownTimeChart
    """
    from stellium.core.models import UnknownTimeChart

    return isinstance(chart, UnknownTimeChart)


def is_multichart(chart: Any) -> bool:
    """Check if chart is a MultiChart.

    Uses duck-typing to avoid circular imports.

    Args:
        chart: Any chart-like object

    Returns:
        True if chart has MultiChart attributes (charts, chart_count, get_cross_aspects)
    """
    return (
        hasattr(chart, "charts")
        and hasattr(chart, "chart_count")
        and hasattr(chart, "get_cross_aspects")
    )


def is_comparison(chart: Any) -> bool:
    """Check if chart is a Comparison (deprecated type).

    Uses duck-typing to avoid circular imports.

    Args:
        chart: Any chart-like object

    Returns:
        True if chart has Comparison attributes (comparison_type, chart1, chart2)
    """
    return (
        hasattr(chart, "comparison_type")
        and hasattr(chart, "chart1")
        and hasattr(chart, "chart2")
    )


def is_multiwheel(chart: Any) -> bool:
    """Check if chart is a MultiWheel (deprecated type).

    Uses duck-typing to avoid circular imports.

    Args:
        chart: Any chart-like object

    Returns:
        True if chart has MultiWheel attributes but not MultiChart attributes
    """
    # MultiWheel has charts but not get_cross_aspects (that's MultiChart)
    return (
        hasattr(chart, "charts")
        and hasattr(chart, "chart_count")
        and not hasattr(chart, "get_cross_aspects")
    )


def get_primary_chart(chart: Any) -> CalculatedChart:
    """Extract the primary (first) chart from any chart type.

    For single charts, returns the chart itself.
    For MultiChart/MultiWheel, returns charts[0].
    For Comparison, returns chart1.

    Args:
        chart: Any chart-like object

    Returns:
        The primary CalculatedChart
    """
    if is_multichart(chart) or is_multiwheel(chart):
        return chart.charts[0]
    if is_comparison(chart):
        return chart.chart1
    return chart


def get_all_charts(chart: Any) -> list[CalculatedChart]:
    """Get all charts as a list.

    For single charts, returns [chart].
    For MultiChart/MultiWheel, returns list(charts).
    For Comparison, returns [chart1, chart2].

    Args:
        chart: Any chart-like object

    Returns:
        List of CalculatedChart objects
    """
    if is_multichart(chart) or is_multiwheel(chart):
        return list(chart.charts)
    if is_comparison(chart):
        return [chart.chart1, chart.chart2]
    return [chart]


def get_chart_labels(chart: Any) -> list[str]:
    """Get labels for all charts.

    Generates default labels ("Chart 1", "Chart 2", etc.) if none are set.

    Args:
        chart: Any chart-like object

    Returns:
        List of label strings, one per chart
    """
    if is_multichart(chart):
        if chart.labels:
            return list(chart.labels)
        return [f"Chart {i + 1}" for i in range(chart.chart_count)]

    if is_multiwheel(chart):
        if hasattr(chart, "labels") and chart.labels:
            return list(chart.labels)
        return [f"Chart {i + 1}" for i in range(chart.chart_count)]

    if is_comparison(chart):
        label1 = getattr(chart, "label1", None) or "Chart 1"
        label2 = getattr(chart, "label2", None) or "Chart 2"
        return [label1, label2]

    return ["Chart"]


def chart_count(chart: Any) -> int:
    """Get the number of charts.

    Args:
        chart: Any chart-like object

    Returns:
        Number of charts (1 for single chart, 2+ for multi-chart types)
    """
    if is_multichart(chart) or is_multiwheel(chart):
        return chart.chart_count
    if is_comparison(chart):
        return 2
    return 1


def get_chart_at_index(chart: Any, index: int) -> CalculatedChart:
    """Get a specific chart by index.

    Args:
        chart: Any chart-like object
        index: 0-based index of the chart to retrieve

    Returns:
        The CalculatedChart at the specified index

    Raises:
        IndexError: If index is out of range
    """
    charts = get_all_charts(chart)
    if index < 0 or index >= len(charts):
        raise IndexError(
            f"Chart index {index} out of range (have {len(charts)} charts)"
        )
    return charts[index]


def get_chart_label_at_index(chart: Any, index: int) -> str:
    """Get the label for a specific chart by index.

    Args:
        chart: Any chart-like object
        index: 0-based index of the chart

    Returns:
        The label string for the chart at the specified index

    Raises:
        IndexError: If index is out of range
    """
    labels = get_chart_labels(chart)
    if index < 0 or index >= len(labels):
        raise IndexError(
            f"Chart index {index} out of range (have {len(labels)} charts)"
        )
    return labels[index]
