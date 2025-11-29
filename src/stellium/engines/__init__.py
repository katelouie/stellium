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
]
