"""
Core data structures and building blocks.

Exports the fundamental classes for working with charts:
- ChartBuilder: Main API for creating charts
- Native: Handles messy datetime/location inputs
- Notable: Curated famous births/events
- All data models (CalculatedChart, CelestialPosition, etc.)
- Chart type utilities (is_multichart, get_all_charts, etc.)
"""

from stellium.core.builder import ChartBuilder
from stellium.core.chart_utils import (
    chart_count,
    get_all_charts,
    get_chart_at_index,
    get_chart_label_at_index,
    get_chart_labels,
    get_primary_chart,
    is_comparison,
    is_multichart,
    is_multiwheel,
    is_single_chart,
    is_unknown_time_chart,
)
from stellium.core.comparison import Comparison, ComparisonBuilder
from stellium.core.config import CalculationConfig
from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    MidpointPosition,
    ObjectType,
    PhaseData,
)
from stellium.core.multichart import MultiChart, MultiChartBuilder
from stellium.core.multiwheel import MultiWheel, MultiWheelBuilder
from stellium.core.native import Native, Notable
from stellium.core.protocols import ChartLike, ChartType
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    get_aspect_by_alias,
    get_aspect_info,
    get_by_alias,
    get_object_info,
)

__all__ = [
    # Builders
    "ChartBuilder",
    "MultiChartBuilder",
    "MultiWheelBuilder",
    "ComparisonBuilder",
    "Native",
    "Notable",
    # Models
    "CalculatedChart",
    "MultiChart",
    "MultiWheel",
    "Comparison",
    "CelestialPosition",
    "MidpointPosition",
    "ChartLocation",
    "ChartDateTime",
    "Aspect",
    "HouseCusps",
    "PhaseData",
    "ObjectType",
    # Protocols & Type Aliases
    "ChartLike",
    "ChartType",
    # Chart Type Utilities
    "is_single_chart",
    "is_unknown_time_chart",
    "is_multichart",
    "is_comparison",
    "is_multiwheel",
    "get_primary_chart",
    "get_all_charts",
    "get_chart_labels",
    "get_chart_at_index",
    "get_chart_label_at_index",
    "chart_count",
    # Registries
    "CELESTIAL_REGISTRY",
    "ASPECT_REGISTRY",
    "get_object_info",
    "get_aspect_info",
    "get_by_alias",
    "get_aspect_by_alias",
    # Config
    "CalculationConfig",
]
