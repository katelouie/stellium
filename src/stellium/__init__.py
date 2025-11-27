"""
Stellium - Computational Astrology Library

Quick Start:
    >>> from stellium import ChartBuilder
    >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    >>> chart.draw("einstein.svg").save()

For more control:
    >>> from stellium import ChartBuilder, Native, ReportBuilder
    >>> from stellium.engines import PlacidusHouses, ModernAspectEngine
    >>> native = Native(datetime_input=..., location_input=...)
    >>> chart = ChartBuilder.from_native(native).calculate()
"""

__version__ = "0.3.0"

# === Core Building Blocks (Most Common) ===
# === Convenience Re-exports ===
# Allow: from stellium.engines import PlacidusHouses
from stellium import components, engines, presentation, visualization
from stellium.core.builder import ChartBuilder
from stellium.core.comparison import (
    Comparison,
    ComparisonAspect,
    ComparisonBuilder,
    ComparisonType,
    HouseOverlay,
)
from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    FixedStarPosition,
    HouseCusps,
    PhaseData,
)
from stellium.core.native import Native, Notable
from stellium.core.synthesis import SynthesisBuilder, SynthesisChart

# === Returns (Solar, Lunar, Planetary) ===
from stellium.returns import ReturnBuilder

# === Registry Access ===
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    FIXED_STARS_REGISTRY,
    get_aspect_info,
    get_fixed_star_info,
    get_object_info,
    get_royal_stars,
    get_stars_by_tier,
)

# === Data (Notable Births) ===
from stellium.data import get_notable_registry

# === Presentation (Reports) ===
from stellium.presentation import ReportBuilder

# === Visualization (High-Level) ===
from stellium.visualization import ChartRenderer

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
    "FixedStarPosition",
    "ChartLocation",
    "ChartDateTime",
    "Aspect",
    "HouseCusps",
    "PhaseData",
    # Registries
    "CELESTIAL_REGISTRY",
    "ASPECT_REGISTRY",
    "FIXED_STARS_REGISTRY",
    "get_object_info",
    "get_aspect_info",
    "get_fixed_star_info",
    "get_royal_stars",
    "get_stars_by_tier",
    # Visualization
    "ChartRenderer",
    # Presentation
    "ReportBuilder",
    # Data
    "get_notable_registry",
    # Submodules (for from stellium.engines import ...)
    "engines",
    "components",
    "visualization",
    "presentation",
    "Comparison",
    "ComparisonBuilder",
    "ComparisonType",
    "ComparisonAspect",
    "HouseOverlay",
    # Synthesis Charts
    "SynthesisBuilder",
    "SynthesisChart",
    # Returns
    "ReturnBuilder",
]
