"""
Uranian/Hamburg School Dial Visualization.

This module provides 90°, 45°, and 360° dial chart visualizations
used in Uranian astrology. The dial compresses the zodiac to reveal
hard aspects (conjunctions, squares, oppositions appear as conjunctions
on the 90° dial).

Example:
    # Basic 90° dial
    chart.draw_dial("dial.svg").save()

    # With theme
    chart.draw_dial("dial.svg").with_theme("midnight").save()

    # With transits on outer ring
    chart.draw_dial("dial.svg", degrees=90) \\
        .with_outer_ring(transit_chart.get_planets(), label="Transits") \\
        .save()

    # 360° dial with pointer
    chart.draw_dial("dial.svg", degrees=360) \\
        .with_pointer(pointing_to="Sun") \\
        .save()
"""

from stellium.visualization.dial.builder import DialDrawBuilder
from stellium.visualization.dial.config import DialConfig, DialStyle
from stellium.visualization.dial.layers import (
    DialBackgroundLayer,
    DialCardinalLayer,
    DialGraduationLayer,
    DialMidpointLayer,
    DialModalityLayer,
    DialOuterRingLayer,
    DialPlanetLayer,
    DialPointerLayer,
)
from stellium.visualization.dial.renderer import DialRenderer

__all__ = [
    # Builder (main API)
    "DialDrawBuilder",
    # Config
    "DialConfig",
    "DialStyle",
    # Renderer
    "DialRenderer",
    # Layers (for advanced customization)
    "DialBackgroundLayer",
    "DialCardinalLayer",
    "DialGraduationLayer",
    "DialMidpointLayer",
    "DialModalityLayer",
    "DialOuterRingLayer",
    "DialPlanetLayer",
    "DialPointerLayer",
]
