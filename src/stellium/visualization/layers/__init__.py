"""
Concrete Render Layers (stellium.visualization.layers)

These are the concrete implementations of the IRenderLayer protocol.
Each class knows how to draw one specific part of a chart,
reading its data from the CalculatedChart object.

This package is organized into submodules by layer type:
- chart_frame: Header, borders, and ring boundaries
- zodiac: Zodiac ring with signs and degrees
- houses: House cusp rendering (inner and outer)
- angles: Angle markers (ASC, MC, DSC, IC)
- planets: Planet glyphs and positions
- aspects: Aspect lines and patterns
- info_corners: Chart info, aspect counts, element/modality tables

All layers are re-exported from this __init__ for backward compatibility.
"""

# Chart frame layers
# Angle layers
from stellium.visualization.layers.angles import (
    AngleLayer,
    OuterAngleLayer,
)

# Aspect layers
from stellium.visualization.layers.aspects import (
    AspectLayer,
    ChartShapeLayer,
    MultiWheelAspectLayer,
)
from stellium.visualization.layers.chart_frame import (
    HeaderLayer,
    OuterBorderLayer,
    RingBoundaryLayer,
)

# House layers
from stellium.visualization.layers.houses import (
    HouseCuspLayer,
    OuterHouseCuspLayer,
)

# Info corner layers
from stellium.visualization.layers.info_corners import (
    AspectCountsLayer,
    ChartInfoLayer,
    ElementModalityTableLayer,
)

# Planet layers
from stellium.visualization.layers.planets import (
    MoonRangeLayer,
    PlanetLayer,
)

# Zodiac layer
from stellium.visualization.layers.zodiac import ZodiacLayer

__all__ = [
    # Chart frame
    "HeaderLayer",
    "OuterBorderLayer",
    "RingBoundaryLayer",
    # Zodiac
    "ZodiacLayer",
    # Houses
    "HouseCuspLayer",
    "OuterHouseCuspLayer",
    # Angles
    "AngleLayer",
    "OuterAngleLayer",
    # Planets
    "PlanetLayer",
    "MoonRangeLayer",
    # Aspects
    "AspectLayer",
    "ChartShapeLayer",
    "MultiWheelAspectLayer",
    # Info corners
    "ChartInfoLayer",
    "AspectCountsLayer",
    "ElementModalityTableLayer",
]
