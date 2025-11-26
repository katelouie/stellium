"""
Calculation engines for ephemeris, houses, aspects, orbs, and dignities.

Common engines:
    >>> from stellium.engines import PlacidusHouses, WholeSignHouses
    >>> from stellium.engines import ModernAspectEngine, TraditionalAspectEngine
    >>> from stellium.engines import SimpleOrbEngine, LuminariesOrbEngine
"""

# Ephemeris
# Aspects
from stellium.engines.aspects import (
    HarmonicAspectEngine,
    ModernAspectEngine,
)

# Dignities
from stellium.engines.dignities import (
    ModernDignityCalculator,
    TraditionalDignityCalculator,
)
from stellium.engines.ephemeris import SwissEphemerisEngine

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
    # Orbs
    "SimpleOrbEngine",
    "LuminariesOrbEngine",
    "ComplexOrbEngine",
    # Dignities
    "TraditionalDignityCalculator",
    "ModernDignityCalculator",
]
