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

__version__ = "0.22.0"

# === Core Building Blocks (Most Common) ===
# === Convenience Re-exports ===
# Allow: from stellium.engines import PlacidusHouses
from stellium import components, engines, presentation, visualization

# === Diagnostics (Logging & Warnings) ===
from stellium._logging import configure_logging
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
    FirdariaPeriod,
    FirdariaTimeline,
    FixedStarPosition,
    HouseCusps,
    HylegResult,
    LengthOfLifeResult,
    PhaseData,
    YearModifier,
)
from stellium.core.multichart import MultiChart, MultiChartBuilder
from stellium.core.multiwheel import MultiWheel, MultiWheelBuilder
from stellium.core.native import Native, Notable

# === Registry Access ===
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    DECLINATION_ASPECT_REGISTRY,
    ECLIPTIC_ASPECT_REGISTRY,
    FIXED_STARS_REGISTRY,
    get_aspect_info,
    get_fixed_star_info,
    get_object_info,
    get_royal_stars,
    get_stars_by_tier,
)
from stellium.core.synthesis import SynthesisBuilder, SynthesisChart

# === Data (Notable Births) ===
from stellium.data import (
    LifeEvent,
    Temperament,
    get_notable_life_events,
    get_notable_registry,
    get_notable_temperament,
)

# === Electional Astrology (Time Search) ===
from stellium.electional import ElectionalSearch

# === Profections (Hellenistic Timing) ===
from stellium.engines.profections import (
    MultiProfectionResult,
    ProfectionEngine,
    ProfectionResult,
    ProfectionTimeline,
)
from stellium.exceptions import (
    ConfigurationWarning,
    DataQualityWarning,
    GeocodingWarning,
    MissingEphemerisWarning,
    MissingGlyphWarning,
    StelliumWarning,
    TimeZoneWarning,
)

# === File I/O (Import/Export) ===
from stellium.io import (
    CSVColumnMapping,
    dataframe_from_natives,
    parse_aaf,
    parse_csv,
    parse_dataframe,
    read_csv,
    read_dataframe,
)

# === Planner (PDF Generation) ===
from stellium.planner import PlannerBuilder

# === Presentation (Reports) ===
from stellium.presentation import ReportBuilder

# === Sect Rectification (compare-hypothesis workbench) ===
from stellium.rectification import SectAnalysis, analyze_sect, convergence_matrix

# === Returns (Solar, Lunar, Planetary) ===
from stellium.returns import ReturnBuilder

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
    "DECLINATION_ASPECT_REGISTRY",
    "ECLIPTIC_ASPECT_REGISTRY",
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
    "get_notable_life_events",
    "get_notable_temperament",
    "LifeEvent",
    "Temperament",
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
    # MultiChart (unified replacement for Comparison + MultiWheel)
    "MultiChart",
    "MultiChartBuilder",
    # MultiWheel (deprecated, use MultiChart)
    "MultiWheel",
    "MultiWheelBuilder",
    # Synthesis Charts
    "SynthesisBuilder",
    "SynthesisChart",
    # Returns
    "ReturnBuilder",
    # Sect rectification
    "analyze_sect",
    "SectAnalysis",
    "convergence_matrix",
    # Profections
    "ProfectionEngine",
    "ProfectionResult",
    "MultiProfectionResult",
    "ProfectionTimeline",
    # Firdaria (Persian time-lord)
    "FirdariaTimeline",
    "FirdariaPeriod",
    # Length of life (hyleg / alcocoden / years-table)
    "HylegResult",
    "LengthOfLifeResult",
    "YearModifier",
    # File I/O
    "parse_aaf",
    "parse_csv",
    "read_csv",
    "parse_dataframe",
    "read_dataframe",
    "dataframe_from_natives",
    "CSVColumnMapping",
    # Electional Astrology
    "ElectionalSearch",
    # Planner
    "PlannerBuilder",
    # Diagnostics (Logging & Warnings)
    "configure_logging",
    "StelliumWarning",
    "DataQualityWarning",
    "GeocodingWarning",
    "ConfigurationWarning",
    "MissingEphemerisWarning",
    "MissingGlyphWarning",
    "TimeZoneWarning",
]
