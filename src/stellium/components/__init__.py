"""
Component system for optional chart calculations.

Components calculate additional objects based on:
- Chart datetime/location
- Already-calculated planetary positions
- House cusps

They return CelestialPosition (or metadata) objects that integrate seamlessly
with the rest of the chart.
"""

from stellium.components.antiscia import AntisciaCalculator, AntisciaConjunction
from stellium.components.arabic_parts import ArabicPartsCalculator
from stellium.components.dignity import (
    AccidentalDignityComponent,
    DignityComponent,
)
from stellium.components.fixed_stars import FixedStarsComponent
from stellium.components.midpoints import MidpointCalculator
from stellium.core.protocols import ChartComponent

__all__ = [
    # Protocol
    "ChartComponent",
    # Components
    "AntisciaCalculator",
    "AntisciaConjunction",
    "ArabicPartsCalculator",
    "MidpointCalculator",
    "DignityComponent",
    "AccidentalDignityComponent",
    "FixedStarsComponent",
]
