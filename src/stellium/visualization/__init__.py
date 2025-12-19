"""Visualization system for Stellium charts."""

from .atlas import AtlasBuilder
from .builder import ChartDrawBuilder
from .core import ChartRenderer
from .ephemeris import EXTENDED_PLANETS, GraphicEphemeris
from .extended_canvas import (
    AspectarianLayer,
    HouseCuspTableLayer,
    PositionTableLayer,
    generate_aspectarian_svg,
    get_aspectarian_dimensions,
)
from .grid import (
    draw_chart_grid,
    draw_palette_comparison,
    draw_theme_comparison,
)
from .layers import (
    AngleLayer,
    AspectCountsLayer,
    AspectLayer,
    ChartInfoLayer,
    ChartShapeLayer,
    ElementModalityTableLayer,
    HouseCuspLayer,
    OuterHouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from .moon_phase import MoonPhaseLayer
from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    get_aspect_palette_colors,
    get_aspect_palette_description,
    get_palette_colors,
    get_palette_description,
    get_planet_glyph_color,
    get_planet_glyph_palette_description,
)
from .reference_sheet import (
    generate_aspect_palette_reference,
    generate_html_reference,
    generate_theme_reference,
    generate_zodiac_palette_reference,
)
from .themes import (
    ChartTheme,
    get_theme_default_aspect_palette,
    get_theme_default_palette,
    get_theme_default_planet_palette,
    get_theme_description,
    get_theme_style,
)

__all__ = [
    # Core rendering
    "ChartRenderer",
    "ChartDrawBuilder",
    # Atlas
    "AtlasBuilder",
    # Layers
    "ZodiacLayer",
    "HouseCuspLayer",
    "OuterHouseCuspLayer",
    "AngleLayer",
    "PlanetLayer",
    "AspectLayer",
    "AspectCountsLayer",
    "AspectarianLayer",
    "ChartInfoLayer",
    "ChartShapeLayer",
    "ElementModalityTableLayer",
    "MoonPhaseLayer",
    "PositionTableLayer",
    "HouseCuspTableLayer",
    # Standalone aspectarian generator
    "generate_aspectarian_svg",
    "get_aspectarian_dimensions",
    # Palettes
    "ZodiacPalette",
    "AspectPalette",
    "PlanetGlyphPalette",
    "get_palette_colors",
    "get_palette_description",
    "get_aspect_palette_colors",
    "get_aspect_palette_description",
    "get_planet_glyph_color",
    "get_planet_glyph_palette_description",
    # Themes
    "ChartTheme",
    "get_theme_style",
    "get_theme_default_palette",
    "get_theme_default_aspect_palette",
    "get_theme_default_planet_palette",
    "get_theme_description",
    # Reference sheets
    "generate_html_reference",
    "generate_zodiac_palette_reference",
    "generate_aspect_palette_reference",
    "generate_theme_reference",
    # Grid layouts
    "draw_chart_grid",
    "draw_theme_comparison",
    "draw_palette_comparison",
    # Graphic ephemeris
    "GraphicEphemeris",
    "EXTENDED_PLANETS",
]
