"""
Report section implementations.

Each section extracts specific data from a CalculatedChart and formats it
into a standardized structure that renderers can consume.

This package contains domain-organized section modules:
- core: Basic chart info (ChartOverview, PlanetPosition, HouseCusps)
- aspects: Aspect-related (AspectSection, AspectPatternSection, CrossChartAspectSection)
- dignities: Dignity analysis (DignitySection, DispositorSection)
- midpoints: Midpoint analysis (MidpointSection, MidpointAspectsSection)
- timing: Time lord techniques (ZodiacalReleasingSection, ProfectionSection)
- misc: Other sections (MoonPhase, Declination, FixedStars, ArabicParts, etc.)
"""

# Utility functions (for external use)
from ._utils import (
    abbreviate_house_system,
    get_aspect_display,
    get_aspect_sort_key,
    get_object_display,
    get_object_sort_key,
    get_sign_glyph,
)

# Aspect sections
from .aspects import (
    AspectPatternSection,
    AspectSection,
    CrossChartAspectSection,
)

# Core sections
from .core import (
    ChartOverviewSection,
    HouseCuspsSection,
    PlanetPositionSection,
)

# Dignity sections
from .dignities import (
    DignitySection,
    DispositorSection,
)

# Midpoint sections
from .midpoints import (
    MidpointAspectsSection,
    MidpointSection,
)

# Miscellaneous sections
from .misc import (
    ArabicPartsSection,
    CacheInfoSection,
    DeclinationAspectSection,
    DeclinationSection,
    FixedStarsSection,
    MoonPhaseSection,
)

# Timing technique sections
from .timing import (
    ProfectionSection,
    ZodiacalReleasingSection,
)

# Transit calendar sections
from .transits import (
    EclipseSection,
    IngressSection,
    StationSection,
)

__all__ = [
    # Utility functions
    "get_object_display",
    "get_sign_glyph",
    "get_aspect_display",
    "get_object_sort_key",
    "get_aspect_sort_key",
    "abbreviate_house_system",
    # Core sections
    "ChartOverviewSection",
    "PlanetPositionSection",
    "HouseCuspsSection",
    # Aspect sections
    "AspectSection",
    "AspectPatternSection",
    "CrossChartAspectSection",
    # Dignity sections
    "DignitySection",
    "DispositorSection",
    # Midpoint sections
    "MidpointSection",
    "MidpointAspectsSection",
    # Timing sections
    "ZodiacalReleasingSection",
    "ProfectionSection",
    # Miscellaneous sections
    "CacheInfoSection",
    "MoonPhaseSection",
    "DeclinationSection",
    "DeclinationAspectSection",
    "FixedStarsSection",
    "ArabicPartsSection",
    # Transit calendar sections
    "EclipseSection",
    "IngressSection",
    "StationSection",
]
