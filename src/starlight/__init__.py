"""
Starlight - Computational Astrology Library

Quick Start:
    >>> from starlight import ChartBuilder, draw_chart
    >>> chart = ChartBuilder.from_notable("Albert Einstein").build()
    >>> draw_chart(chart, "einstein.svg")

For more control:
    >>> from starlight import ChartBuilder, Native, ReportBuilder
    >>> from starlight.engines import PlacidusHouses, ModernAspectEngine
    >>> native = Native(datetime_input=..., location_input=...)
    >>> chart = ChartBuilder.from_native(native).build()
"""

__version__ = "0.2.0"

# === Core Building Blocks (Most Common) ===
# === Convenience Re-exports ===
# Allow: from starlight.engines import PlacidusHouses
from starlight import components, engines, presentation, visualization
from starlight.core.builder import ChartBuilder
from starlight.core.comparison import (
    Comparison,
    ComparisonAspect,
    ComparisonBuilder,
    ComparisonType,
    HouseOverlay,
)
from starlight.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    PhaseData,
)
from starlight.core.native import Native, Notable

# === Registry Access ===
from starlight.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    get_aspect_info,
    get_object_info,
)

# === Data (Notable Births) ===
from starlight.data import get_notable_registry

# === Presentation (Reports) ===
from starlight.presentation import ReportBuilder

# === Visualization (High-Level) ===
from starlight.visualization import ChartRenderer
# draw_chart and draw_comparison_chart don't exist

__all__ = [
    # Version
    "__version__",
    # Core API - Chart Building
    "ChartBuilder",
    "Native",
    "Notable",
    # Core Models
    "CalculatedChart",
    "CelestialPosition",
    "ChartLocation",
    "ChartDateTime",
    "Aspect",
    "HouseCusps",
    "PhaseData",
    # Registries
    "CELESTIAL_REGISTRY",
    "ASPECT_REGISTRY",
    "get_object_info",
    "get_aspect_info",
    # Visualization
    # "draw_chart",  # Doesn't exist
    # "draw_comparison_chart",  # Doesn't exist
    "ChartRenderer",
    # Presentation
    "ReportBuilder",
    # Data
    "get_notable_registry",
    # Submodules (for from starlight.engines import ...)
    "engines",
    "components",
    "visualization",
    "presentation",
    "Comparison",
    "ComparisonBuilder",
    "ComparisonType",
    "ComparisonAspect",
    "HouseOverlay",
]
