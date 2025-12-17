"""
Calculation engines for ephemeris, houses, aspects, orbs, dignities, and fixed stars.

Common engines:
    >>> from stellium.engines import PlacidusHouses, WholeSignHouses
    >>> from stellium.engines import ModernAspectEngine, TraditionalAspectEngine
    >>> from stellium.engines import SimpleOrbEngine, LuminariesOrbEngine
    >>> from stellium.engines import SwissEphemerisFixedStarsEngine
"""

# Ephemeris
# Aspects
from stellium.engines.aspects import (
    DeclinationAspectEngine,
    HarmonicAspectEngine,
    ModernAspectEngine,
)

# Dignities
from stellium.engines.dignities import (
    ModernDignityCalculator,
    TraditionalDignityCalculator,
)

# Primary Directions
from stellium.engines.directions import (
    DirectionArc,
    DirectionResult,
    DirectionsEngine,
    DistributionsCalculator,
    MundaneDirections,
    NaibodKey,
    PtolemyKey,
    TimeLordPeriod,
    ZodiacalDirections,
)

# Dispositors
from stellium.engines.dispositors import (
    DispositorEngine,
    DispositorResult,
    MutualReception,
    render_both_dispositors,
    render_dispositor_graph,
)
from stellium.engines.ephemeris import SwissEphemerisEngine

# Fixed Stars
from stellium.engines.fixed_stars import SwissEphemerisFixedStarsEngine

# House Systems
from stellium.engines.houses import (
    EqualHouses,
    KochHouses,
    PlacidusHouses,
    WholeSignHouses,
)

# Orbs
from stellium.engines.orbs import (
    ComplexOrbEngine,
    LuminariesOrbEngine,
    SimpleOrbEngine,
)

# Profections
from stellium.engines.profections import (
    MultiProfectionResult,
    ProfectionEngine,
    ProfectionResult,
    ProfectionTimeline,
)

# Longitude Search, Ingresses, Stations, Eclipses, Aspect Exactitude, and Angle Crossings
from stellium.engines.search import (
    AngleCrossing,
    AspectExact,
    Eclipse,
    LongitudeCrossing,
    SignIngress,
    Station,
    find_all_angle_crossings,
    find_all_aspect_exacts,
    find_all_eclipses,
    find_all_ingresses,
    find_all_longitude_crossings,
    find_all_sign_changes,
    find_all_stations,
    find_angle_crossing,
    find_aspect_exact,
    find_eclipse,
    find_ingress,
    find_longitude_crossing,
    find_next_sign_change,
    find_station,
)

# Void of Course Moon
from stellium.engines.voc import (
    VOCMoonResult,
    calculate_voc_moon,
)

__all__ = [
    # Ephemeris
    "SwissEphemerisEngine",
    # Houses
    "PlacidusHouses",
    "WholeSignHouses",
    "KochHouses",
    "EqualHouses",
    # Aspects
    "ModernAspectEngine",
    "HarmonicAspectEngine",
    "DeclinationAspectEngine",
    # Orbs
    "SimpleOrbEngine",
    "LuminariesOrbEngine",
    "ComplexOrbEngine",
    # Dignities
    "TraditionalDignityCalculator",
    "ModernDignityCalculator",
    # Fixed Stars
    "SwissEphemerisFixedStarsEngine",
    # Profections
    "ProfectionEngine",
    "ProfectionResult",
    "MultiProfectionResult",
    "ProfectionTimeline",
    # Dispositors
    "DispositorEngine",
    "DispositorResult",
    "MutualReception",
    "render_dispositor_graph",
    "render_both_dispositors",
    # Longitude Search, Ingresses, Stations, Eclipses, & Aspect Exactitude
    "find_longitude_crossing",
    "find_all_longitude_crossings",
    "LongitudeCrossing",
    "find_ingress",
    "find_all_ingresses",
    "find_next_sign_change",
    "find_all_sign_changes",
    "SignIngress",
    "find_station",
    "find_all_stations",
    "Station",
    "find_eclipse",
    "find_all_eclipses",
    "Eclipse",
    "find_aspect_exact",
    "find_all_aspect_exacts",
    "AspectExact",
    "find_angle_crossing",
    "find_all_angle_crossings",
    "AngleCrossing",
    # Primary Directions
    "DirectionsEngine",
    "DirectionResult",
    "DirectionArc",
    "DistributionsCalculator",
    "TimeLordPeriod",
    "ZodiacalDirections",
    "MundaneDirections",
    "PtolemyKey",
    "NaibodKey",
    # Void of Course Moon
    "VOCMoonResult",
    "calculate_voc_moon",
]
