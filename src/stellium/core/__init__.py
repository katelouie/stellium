"""
Core data structures and building blocks.

Exports the fundamental classes for working with charts:
- ChartBuilder: Main API for creating charts
- Native: Handles messy datetime/location inputs
- Notable: Curated famous births/events
- All data models (CalculatedChart, CelestialPosition, etc.)
"""

from stellium.core.builder import ChartBuilder
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
    "Native",
    "Notable",
    # Models
    "CalculatedChart",
    "MultiChart",
    "MultiWheel",
    "CelestialPosition",
    "MidpointPosition",
    "ChartLocation",
    "ChartDateTime",
    "Aspect",
    "HouseCusps",
    "PhaseData",
    "ObjectType",
    # Registries
    "CELESTIAL_REGISTRY",
    "ASPECT_REGISTRY",
    "get_object_info",
    "get_aspect_info",
    "get_object_by_alias",
    "get_aspect_by_alias",
    # Config
    "CalculationConfig",
]
