"""
Base imports and utilities for render layers.

This module provides shared imports and utilities used across all layer modules.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    HouseCusps,
    UnknownTimeChart,
)
from stellium.visualization.core import (
    ANGLE_GLYPHS,
    ZODIAC_GLYPHS,
    ChartRenderer,
    embed_svg_glyph,
    get_glyph,
)
from stellium.visualization.palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    adjust_color_for_contrast,
    get_aspect_palette_colors,
    get_palette_colors,
    get_planet_glyph_color,
    get_sign_info_color,
)

__all__ = [
    # Types
    "Any",
    "svgwrite",
    # Core models
    "CalculatedChart",
    "CelestialPosition",
    "HouseCusps",
    "UnknownTimeChart",
    # Visualization core
    "ANGLE_GLYPHS",
    "ZODIAC_GLYPHS",
    "ChartRenderer",
    "embed_svg_glyph",
    "get_glyph",
    # Palettes
    "AspectPalette",
    "PlanetGlyphPalette",
    "ZodiacPalette",
    "adjust_color_for_contrast",
    "get_aspect_palette_colors",
    "get_palette_colors",
    "get_planet_glyph_color",
    "get_sign_info_color",
]
