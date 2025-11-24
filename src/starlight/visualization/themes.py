"""
Chart Themes (starlight.visualization.themes)

Defines complete visual themes for chart rendering, including colors,
line styles, and default zodiac palettes.
"""

from enum import Enum
from typing import Any

from starlight.core.registry import ASPECT_REGISTRY

from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    get_aspect_palette_colors,
)


class ChartTheme(str, Enum):
    """Available visual themes for chart rendering."""

    CLASSIC = "classic"
    DARK = "dark"
    MIDNIGHT = "midnight"
    NEON = "neon"
    SEPIA = "sepia"
    PASTEL = "pastel"
    CELESTIAL = "celestial"

    # Data science themes
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    TURBO = "turbo"


# Default zodiac palette for each theme
THEME_DEFAULT_PALETTES = {
    ChartTheme.CLASSIC: ZodiacPalette.GREY,
    ChartTheme.DARK: ZodiacPalette.GREY,
    ChartTheme.MIDNIGHT: ZodiacPalette.RAINBOW_MIDNIGHT,
    ChartTheme.NEON: ZodiacPalette.RAINBOW_NEON,
    ChartTheme.SEPIA: ZodiacPalette.RAINBOW_SEPIA,
    ChartTheme.PASTEL: ZodiacPalette.RAINBOW,
    ChartTheme.CELESTIAL: ZodiacPalette.RAINBOW_CELESTIAL,
    # Data science themes
    ChartTheme.VIRIDIS: ZodiacPalette.VIRIDIS,
    ChartTheme.PLASMA: ZodiacPalette.PLASMA,
    ChartTheme.INFERNO: ZodiacPalette.INFERNO,
    ChartTheme.MAGMA: ZodiacPalette.MAGMA,
    ChartTheme.CIVIDIS: ZodiacPalette.CIVIDIS,
    ChartTheme.TURBO: ZodiacPalette.TURBO,
}

# Default aspect palette for each theme
THEME_DEFAULT_ASPECT_PALETTES = {
    ChartTheme.CLASSIC: AspectPalette.CLASSIC,
    ChartTheme.DARK: AspectPalette.DARK,
    ChartTheme.MIDNIGHT: AspectPalette.MIDNIGHT,
    ChartTheme.NEON: AspectPalette.NEON,
    ChartTheme.SEPIA: AspectPalette.SEPIA,
    ChartTheme.PASTEL: AspectPalette.PASTEL,
    ChartTheme.CELESTIAL: AspectPalette.CELESTIAL,
    # Data science themes
    ChartTheme.VIRIDIS: AspectPalette.VIRIDIS,
    ChartTheme.PLASMA: AspectPalette.PLASMA,
    ChartTheme.INFERNO: AspectPalette.INFERNO,
    ChartTheme.MAGMA: AspectPalette.MAGMA,
    ChartTheme.CIVIDIS: AspectPalette.CIVIDIS,
    ChartTheme.TURBO: AspectPalette.TURBO,
}

# Default planet glyph palette for each theme
THEME_DEFAULT_PLANET_PALETTES = {
    ChartTheme.CLASSIC: PlanetGlyphPalette.DEFAULT,
    ChartTheme.DARK: PlanetGlyphPalette.DEFAULT,
    ChartTheme.MIDNIGHT: PlanetGlyphPalette.DEFAULT,
    ChartTheme.NEON: PlanetGlyphPalette.RAINBOW,
    ChartTheme.SEPIA: PlanetGlyphPalette.DEFAULT,
    ChartTheme.PASTEL: PlanetGlyphPalette.DEFAULT,
    ChartTheme.CELESTIAL: PlanetGlyphPalette.DEFAULT,
    # Data science themes
    ChartTheme.VIRIDIS: PlanetGlyphPalette.VIRIDIS,
    ChartTheme.PLASMA: PlanetGlyphPalette.PLASMA,
    ChartTheme.INFERNO: PlanetGlyphPalette.INFERNO,
    ChartTheme.MAGMA: PlanetGlyphPalette.INFERNO,  # Magma similar to Inferno
    ChartTheme.CIVIDIS: PlanetGlyphPalette.VIRIDIS,  # Cividis similar to Viridis
    ChartTheme.TURBO: PlanetGlyphPalette.TURBO,
}


def get_theme_style(theme: ChartTheme) -> dict[str, Any]:
    """
    Get the complete style configuration for a theme.

    Args:
        theme: The theme to use

    Returns:
        Complete style dictionary for ChartRenderer
    """
    if theme == ChartTheme.CLASSIC:
        return _get_classic_theme()
    elif theme == ChartTheme.DARK:
        return _get_dark_theme()
    elif theme == ChartTheme.MIDNIGHT:
        return _get_midnight_theme()
    elif theme == ChartTheme.NEON:
        return _get_neon_theme()
    elif theme == ChartTheme.SEPIA:
        return _get_sepia_theme()
    elif theme == ChartTheme.PASTEL:
        return _get_pastel_theme()
    elif theme == ChartTheme.CELESTIAL:
        return _get_celestial_theme()
    elif theme == ChartTheme.VIRIDIS:
        return _get_viridis_theme()
    elif theme == ChartTheme.PLASMA:
        return _get_plasma_theme()
    elif theme == ChartTheme.INFERNO:
        return _get_inferno_theme()
    elif theme == ChartTheme.MAGMA:
        return _get_magma_theme()
    elif theme == ChartTheme.CIVIDIS:
        return _get_cividis_theme()
    elif theme == ChartTheme.TURBO:
        return _get_turbo_theme()
    else:
        return _get_classic_theme()


def get_theme_default_palette(theme: ChartTheme) -> ZodiacPalette:
    """
    Get the default zodiac palette for a theme.

    Args:
        theme: The theme

    Returns:
        Default ZodiacPalette for this theme
    """
    return THEME_DEFAULT_PALETTES.get(theme, ZodiacPalette.GREY)


def get_theme_default_aspect_palette(theme: ChartTheme) -> AspectPalette:
    """
    Get the default aspect palette for a theme.

    Args:
        theme: The theme

    Returns:
        Default AspectPalette for this theme
    """
    return THEME_DEFAULT_ASPECT_PALETTES.get(theme, AspectPalette.CLASSIC)


def get_theme_default_planet_palette(theme: ChartTheme) -> PlanetGlyphPalette:
    """
    Get the default planet glyph palette for a theme.

    Args:
        theme: The theme

    Returns:
        Default PlanetGlyphPalette for this theme
    """
    return THEME_DEFAULT_PLANET_PALETTES.get(theme, PlanetGlyphPalette.DEFAULT)


# ============================================================================
# Theme Definitions
# ============================================================================


def _get_classic_theme() -> dict[str, Any]:
    """Classic theme - current default styling (grey, professional)."""
    return {
        "background_color": "#FFFFFF",
        "border_color": "#999999",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#EEEEEE",
            "line_color": "#BBBBBB",
            "glyph_color": "#555555",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#CCCCCC",
            "line_width": 0.8,
            "number_color": "#AAAAAA",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#F5F5F5",
            "fill_color_2": "#FFFFFF",
        },
        "angles": {
            "line_color": "#555555",
            "line_width": 2.5,
            "glyph_color": "#333333",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#888888",  # Lighter grey
            "line_width": 1.8,
            "glyph_color": "#666666",
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#222222",
            "glyph_size": "32px",
            "info_color": "#444444",
            "info_size": "10px",
            "retro_color": "#E74C3C",
            "outer_wheel_planet_color": "#4A90E2",  # Softer blue for outer wheel
        },
        "aspects": {
            **{
                aspect_info.name: {
                    "color": aspect_info.color,
                    "width": aspect_info.metadata.get("line_width", 1.5),
                    "dash": aspect_info.metadata.get("dash_pattern", "1,0"),
                }
                for aspect_info in ASPECT_REGISTRY.values()
                if aspect_info.category in ["Major", "Minor"]
            },
            "default": {"color": "#BDC3C7", "width": 0.5, "dash": "2,2"},
            "line_color": "#BBBBBB",
            "background_color": "#FFFFFF",
        },
    }


def _get_dark_theme() -> dict[str, Any]:
    """Dark theme - dark grey background with light text."""
    return {
        "background_color": "#1E1E1E",
        "border_color": "#555555",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#2D2D2D",
            "line_color": "#666666",
            "glyph_color": "#CCCCCC",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#555555",
            "line_width": 0.8,
            "number_color": "#888888",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#252525",
            "fill_color_2": "#1E1E1E",
        },
        "angles": {
            "line_color": "#AAAAAA",
            "line_width": 2.5,
            "glyph_color": "#DDDDDD",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#888888",  # Softer grey
            "line_width": 1.8,
            "glyph_color": "#BBBBBB",
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#EEEEEE",
            "glyph_size": "32px",
            "info_color": "#BBBBBB",
            "info_size": "10px",
            "retro_color": "#FF6B6B",
            "outer_wheel_planet_color": "#95E1D3",  # Cyan for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#FF6B6B", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#4ECDC4", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#FF6B9D", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#95E1D3", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#666666", "width": 0.5, "dash": "2,2"},
            "line_color": "#555555",
            "background_color": "#1E1E1E",
        },
    }


def _get_midnight_theme() -> dict[str, Any]:
    """Midnight theme - elegant night sky with deep navy and white/gold accents."""
    return {
        "background_color": "#0A1628",
        "border_color": "#3A5A7C",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#0D1F3C",
            "line_color": "#4A6FA5",
            "glyph_color": "#E8E8E8",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#4A6FA5",
            "line_width": 0.8,
            "number_color": "#A8C5E8",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#0E223D",
            "fill_color_2": "#0A1628",
        },
        "angles": {
            "line_color": "#E8E8E8",
            "line_width": 2.5,
            "glyph_color": "#FFFFFF",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#A8C5E8",  # Lighter blue-grey
            "line_width": 1.8,
            "glyph_color": "#C8D5E8",  # Even lighter
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#FFD700",
            "glyph_size": "32px",
            "info_color": "#E8E8E8",
            "info_size": "10px",
            "retro_color": "#FFA07A",
            "outer_wheel_planet_color": "#87CEEB",  # Sky blue for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#87CEEB", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#98D8E8", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#B0C4DE", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#ADD8E6", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#4A6FA5", "width": 0.5, "dash": "2,2"},
            "line_color": "#3A5A7C",
            "background_color": "#0A1628",
        },
    }


def _get_neon_theme() -> dict[str, Any]:
    """Neon theme - cyberpunk aesthetic with black background and bright neon colors."""
    return {
        "background_color": "#0D0D0D",
        "border_color": "#00FFFF",
        "border_width": 1.5,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#1A1A1A",
            "line_color": "#00FFFF",
            "glyph_color": "#FF00FF",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#00FFFF",
            "line_width": 1.0,
            "number_color": "#39FF14",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#1A0A1A",
            "fill_color_2": "#0D0D0D",
        },
        "angles": {
            "line_color": "#FF00FF",
            "line_width": 3.0,
            "glyph_color": "#FFFF00",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#00FFFF",  # Cyan instead of magenta
            "line_width": 2.0,
            "glyph_color": "#39FF14",  # Neon green
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#00FFFF",
            "glyph_size": "32px",
            "info_color": "#FF00FF",
            "info_size": "10px",
            "retro_color": "#FF1493",
            "outer_wheel_planet_color": "#39FF14",  # Neon green for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#FFFF00", "width": 2.5, "dash": "1,0"},
            "Opposition": {"color": "#FF00FF", "width": 2.0, "dash": "1,0"},
            "Trine": {"color": "#00FFFF", "width": 2.0, "dash": "1,0"},
            "Square": {"color": "#FF1493", "width": 2.0, "dash": "1,0"},
            "Sextile": {"color": "#39FF14", "width": 1.5, "dash": "1,0"},
            "default": {"color": "#00FF88", "width": 0.8, "dash": "2,2"},
            "line_color": "#00FFFF",
            "background_color": "#0D0D0D",
        },
    }


def _get_sepia_theme() -> dict[str, Any]:
    """Sepia theme - vintage/aged paper aesthetic with warm browns."""
    return {
        "background_color": "#F4ECD8",
        "border_color": "#8B7355",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Georgia", "Times New Roman", serif',
        "zodiac": {
            "ring_color": "#E8DCC4",
            "line_color": "#A68B6B",
            "glyph_color": "#5D4E37",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#A68B6B",
            "line_width": 0.8,
            "number_color": "#8B7355",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#EDE4D0",
            "fill_color_2": "#F4ECD8",
        },
        "angles": {
            "line_color": "#5D4E37",
            "line_width": 2.5,
            "glyph_color": "#3E2F1F",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#8B7355",  # Lighter warm brown
            "line_width": 1.8,
            "glyph_color": "#A68B6B",
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#4A3728",
            "glyph_size": "32px",
            "info_color": "#6B5744",
            "info_size": "10px",
            "retro_color": "#A0522D",
            "outer_wheel_planet_color": "#8B7355",  # Lighter brown for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#8B4513", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#A0522D", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#9B7653", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#8B7355", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#A68B6B", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#C4A582", "width": 0.5, "dash": "2,2"},
            "line_color": "#A68B6B",
            "background_color": "#F4ECD8",
        },
    }


def _get_pastel_theme() -> dict[str, Any]:
    """Pastel theme - soft, gentle colors with light and airy feel."""
    return {
        "background_color": "#FAFAFA",
        "border_color": "#C4C4C4",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#F0F0F0",
            "line_color": "#D4D4D4",
            "glyph_color": "#888888",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#D4D4D4",
            "line_width": 0.8,
            "number_color": "#A0A0A0",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#F5F5F5",
            "fill_color_2": "#FAFAFA",
        },
        "angles": {
            "line_color": "#888888",
            "line_width": 2.5,
            "glyph_color": "#666666",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#AAAAAA",  # Softer grey
            "line_width": 1.8,
            "glyph_color": "#999999",
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#555555",
            "glyph_size": "32px",
            "info_color": "#777777",
            "info_size": "10px",
            "retro_color": "#FF9999",
            "outer_wheel_planet_color": "#B4A7D6",  # Soft lavender for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#FFD4A3", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#FFB3BA", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#BAE1FF", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#FFDFBA", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#BAFFC9", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#E0E0E0", "width": 0.5, "dash": "2,2"},
            "line_color": "#D4D4D4",
            "background_color": "#FAFAFA",
        },
    }


def _get_celestial_theme() -> dict[str, Any]:
    """Celestial theme - cosmic/galaxy aesthetic with deep purples and gold stars."""
    return {
        "background_color": "#1A0F2E",
        "border_color": "#6B4FA3",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#2A1A4A",
            "line_color": "#7B5FAF",
            "glyph_color": "#E8D4FF",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#7B5FAF",
            "line_width": 0.8,
            "number_color": "#C4A4E8",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#241540",
            "fill_color_2": "#1A0F2E",
        },
        "angles": {
            "line_color": "#FFD700",
            "line_width": 2.5,
            "glyph_color": "#FFF4D4",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#DA70D6",  # Orchid/purple
            "line_width": 1.8,
            "glyph_color": "#E8D4FF",  # Soft lavender
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#FFD700",
            "glyph_size": "32px",
            "info_color": "#E8D4FF",
            "info_size": "10px",
            "retro_color": "#FF69B4",
            "outer_wheel_planet_color": "#DA70D6",  # Orchid for outer wheel
        },
        "aspects": {
            "Conjunction": {"color": "#FFD700", "width": 2.0, "dash": "1,0"},
            "Opposition": {"color": "#DA70D6", "width": 1.5, "dash": "1,0"},
            "Trine": {"color": "#9370DB", "width": 1.5, "dash": "1,0"},
            "Square": {"color": "#BA55D3", "width": 1.5, "dash": "1,0"},
            "Sextile": {"color": "#DDA0DD", "width": 1.2, "dash": "1,0"},
            "default": {"color": "#7B5FAF", "width": 0.5, "dash": "2,2"},
            "line_color": "#6B4FA3",
            "background_color": "#1A0F2E",
        },
    }


# ============================================================================
# Data Science Themes
# ============================================================================


def _get_viridis_theme() -> dict[str, Any]:
    """Viridis theme - perceptually uniform purple→green→yellow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.VIRIDIS)
    return {
        "background_color": "#1C1C1C",
        "border_color": "#414487",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#262626",
            "line_color": "#414487",
            "glyph_color": "#FDE724",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#2A788E",
            "line_width": 0.8,
            "number_color": "#22A884",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#222222",
            "fill_color_2": "#1C1C1C",
        },
        "angles": {
            "line_color": "#7AD151",
            "line_width": 2.5,
            "glyph_color": "#FDE724",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#22A884",  # Teal (mid viridis)
            "line_width": 1.8,
            "glyph_color": "#7AD151",  # Yellow-green
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#22A884",
            "glyph_size": "32px",
            "info_color": "#7AD151",
            "info_size": "10px",
            "retro_color": "#BBDF27",
            "outer_wheel_planet_color": "#414487",  # Purple for outer wheel (viridis low end)
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#414487", "width": 0.5, "dash": "2,2"},
            "line_color": "#2A788E",
            "background_color": "#1C1C1C",
        },
    }


def _get_plasma_theme() -> dict[str, Any]:
    """Plasma theme - vibrant blue→purple→orange→yellow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.PLASMA)
    return {
        "background_color": "#0D0887",
        "border_color": "#6A00A8",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#180C4E",
            "line_color": "#B12A90",
            "glyph_color": "#F0F921",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#CC4778",
            "line_width": 0.8,
            "number_color": "#FCA636",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#150A5F",
            "fill_color_2": "#0D0887",
        },
        "angles": {
            "line_color": "#FCCE25",
            "line_width": 2.5,
            "glyph_color": "#F0F921",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#E16462",  # Orange-red (mid plasma)
            "line_width": 1.8,
            "glyph_color": "#FCA636",  # Orange
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#E16462",
            "glyph_size": "32px",
            "info_color": "#FCA636",
            "info_size": "10px",
            "retro_color": "#F1844B",
            "outer_wheel_planet_color": "#B12A90",  # Deep magenta for outer wheel
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#8F0DA4", "width": 0.5, "dash": "2,2"},
            "line_color": "#B12A90",
            "background_color": "#0D0887",
        },
    }


def _get_inferno_theme() -> dict[str, Any]:
    """Inferno theme - dramatic black→red→orange→yellow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.INFERNO)
    return {
        "background_color": "#000004",
        "border_color": "#781C6D",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#1B0C41",
            "line_color": "#A52C60",
            "glyph_color": "#FCFFA4",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#CF4446",
            "line_width": 0.8,
            "number_color": "#FB9A06",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#1B0C41",
            "fill_color_2": "#000004",
        },
        "angles": {
            "line_color": "#F7D03C",
            "line_width": 2.5,
            "glyph_color": "#FCFFA4",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#ED6925",  # Orange (mid inferno)
            "line_width": 1.8,
            "glyph_color": "#FB9A06",  # Lighter orange
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#ED6925",
            "glyph_size": "32px",
            "info_color": "#FB9A06",
            "info_size": "10px",
            "retro_color": "#F7D03C",
            "outer_wheel_planet_color": "#A52C60",  # Deep red for outer wheel
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#781C6D", "width": 0.5, "dash": "2,2"},
            "line_color": "#A52C60",
            "background_color": "#000004",
        },
    }


def _get_magma_theme() -> dict[str, Any]:
    """Magma theme - subtle black→purple→pink→yellow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.MAGMA)
    return {
        "background_color": "#000004",
        "border_color": "#5F187F",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#0B0924",
            "line_color": "#7B2382",
            "glyph_color": "#FCFDBF",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#982D80",
            "line_width": 0.8,
            "number_color": "#EB5760",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#0B0924",
            "fill_color_2": "#000004",
        },
        "angles": {
            "line_color": "#F8765C",
            "line_width": 2.5,
            "glyph_color": "#FCFDBF",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#D3436E",  # Pink (mid magma)
            "line_width": 1.8,
            "glyph_color": "#EB5760",  # Lighter pink
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#D3436E",
            "glyph_size": "32px",
            "info_color": "#EB5760",
            "info_size": "10px",
            "retro_color": "#F8765C",
            "outer_wheel_planet_color": "#7B2382",  # Deep purple for outer wheel
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#5F187F", "width": 0.5, "dash": "2,2"},
            "line_color": "#7B2382",
            "background_color": "#000004",
        },
    }


def _get_cividis_theme() -> dict[str, Any]:
    """Cividis theme - CVD-optimized blue→yellow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.CIVIDIS)
    return {
        "background_color": "#00204C",
        "border_color": "#25567B",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#00306E",
            "line_color": "#4E6B7C",
            "glyph_color": "#FFEA46",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#73807D",
            "line_width": 0.8,
            "number_color": "#C5AC83",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#00306E",
            "fill_color_2": "#00204C",
        },
        "angles": {
            "line_color": "#E5C482",
            "line_width": 2.5,
            "glyph_color": "#FFEA46",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#9B9680",  # Grey-tan (mid cividis)
            "line_width": 1.8,
            "glyph_color": "#C5AC83",  # Lighter tan
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#9B9680",
            "glyph_size": "32px",
            "info_color": "#C5AC83",
            "info_size": "10px",
            "retro_color": "#E5C482",
            "outer_wheel_planet_color": "#4E6B7C",  # Blue-grey for outer wheel
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#4E6B7C", "width": 0.5, "dash": "2,2"},
            "line_color": "#73807D",
            "background_color": "#00204C",
        },
    }


def _get_turbo_theme() -> dict[str, Any]:
    """Turbo theme - Google's improved rainbow palette."""
    aspect_colors = get_aspect_palette_colors(AspectPalette.TURBO)
    return {
        "background_color": "#1A1A2E",
        "border_color": "#4662D7",
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#242438",
            "line_color": "#1AE4B6",
            "glyph_color": "#FABA39",
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#72FE5E",
            "line_width": 0.8,
            "number_color": "#C8EF34",
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#242438",
            "fill_color_2": "#1A1A2E",
        },
        "angles": {
            "line_color": "#FABA39",
            "line_width": 2.5,
            "glyph_color": "#FABA39",
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#1AE4B6",  # Turquoise (turbo palette)
            "line_width": 1.8,
            "glyph_color": "#72FE5E",  # Bright green
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#72FE5E",
            "glyph_size": "32px",
            "info_color": "#C8EF34",
            "info_size": "10px",
            "retro_color": "#F66B19",
            "outer_wheel_planet_color": "#1AE4B6",  # Turquoise for outer wheel
        },
        "aspects": {
            **{
                name: {"color": color, "width": 1.5, "dash": "1,0"}
                for name, color in aspect_colors.items()
            },
            "default": {"color": "#4662D7", "width": 0.5, "dash": "2,2"},
            "line_color": "#1AE4B6",
            "background_color": "#1A1A2E",
        },
    }


def get_theme_description(theme: ChartTheme) -> str:
    """
    Get a human-readable description of a theme.

    Args:
        theme: The theme to describe

    Returns:
        Description string
    """
    descriptions = {
        ChartTheme.CLASSIC: "Classic - Professional grey/neutral (default)",
        ChartTheme.DARK: "Dark - Dark grey background with light text",
        ChartTheme.MIDNIGHT: "Midnight - Elegant night sky with deep navy and white/gold",
        ChartTheme.NEON: "Neon - Cyberpunk aesthetic with bright neon colors",
        ChartTheme.SEPIA: "Sepia - Vintage aged paper with warm browns",
        ChartTheme.PASTEL: "Pastel - Soft gentle colors, light and airy",
        ChartTheme.CELESTIAL: "Celestial - Cosmic galaxy with deep purples and gold",
        # Data science themes
        ChartTheme.VIRIDIS: "Viridis - Perceptually uniform purple→green→yellow (colorblind-friendly)",
        ChartTheme.PLASMA: "Plasma - Vibrant blue→purple→orange→yellow gradient",
        ChartTheme.INFERNO: "Inferno - Dramatic black→red→orange→yellow fire palette",
        ChartTheme.MAGMA: "Magma - Subtle black→purple→pink→yellow volcanic palette",
        ChartTheme.CIVIDIS: "Cividis - Blue→yellow palette optimized for color vision deficiency",
        ChartTheme.TURBO: "Turbo - Google's improved rainbow (high contrast)",
    }
    return descriptions.get(theme, "Unknown theme")
