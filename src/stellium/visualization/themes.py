"""
Chart Themes (stellium.visualization.themes)

Defines complete visual themes for chart rendering, including colors,
line styles, and default zodiac palettes.
"""

from enum import Enum
from typing import Any

from stellium.core.registry import ASPECT_REGISTRY

from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    build_aspect_styles_from_palette,
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
    ATLAS = "atlas"

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
    ChartTheme.ATLAS: ZodiacPalette.RAINBOW,
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
    ChartTheme.ATLAS: AspectPalette.CLASSIC,
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
    ChartTheme.ATLAS: PlanetGlyphPalette.DEFAULT,
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
    elif theme == ChartTheme.ATLAS:
        return _get_atlas_theme()
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
            "secondary_color": "#3498DB",  # Blue for secondary house system overlay
            "chart1_fill_1": "#F5F5F5",
            "chart1_fill_2": "#FFFFFF",
            "chart2_fill_1": "#E8F4FC",
            "chart2_fill_2": "#F5FAFD",
            "chart3_fill_1": "#E8F8EE",
            "chart3_fill_2": "#F5FBF7",
            "chart4_fill_1": "#F3EBF8",
            "chart4_fill_2": "#FAF6FC",
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
            "chart1_color": "#222222",
            "chart2_color": "#4A90E2",
            "chart3_color": "#27AE60",
            "chart4_color": "#9B59B6",
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
            "secondary_color": "#4ECDC4",  # Teal for secondary house system overlay
            "chart1_fill_1": "#252525",
            "chart1_fill_2": "#1E1E1E",
            "chart2_fill_1": "#1E2A2A",
            "chart2_fill_2": "#1A2525",
            "chart3_fill_1": "#1E2A1E",
            "chart3_fill_2": "#1A251A",
            "chart4_fill_1": "#2A1E2A",
            "chart4_fill_2": "#251A25",
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
            "chart1_color": "#EEEEEE",
            "chart2_color": "#95E1D3",
            "chart3_color": "#98D982",
            "chart4_color": "#D98CE3",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.DARK),
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
            "secondary_color": "#87CEEB",  # Sky blue for secondary house system overlay
            "chart1_fill_1": "#0E223D",
            "chart1_fill_2": "#0A1628",
            "chart2_fill_1": "#0E2835",
            "chart2_fill_2": "#0A1E2A",
            "chart3_fill_1": "#0E2D28",
            "chart3_fill_2": "#0A2420",
            "chart4_fill_1": "#1A1E35",
            "chart4_fill_2": "#14182A",
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
            "chart1_color": "#FFD700",
            "chart2_color": "#87CEEB",
            "chart3_color": "#98FB98",
            "chart4_color": "#DDA0DD",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.MIDNIGHT),
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
            "secondary_color": "#FF00FF",  # Magenta for secondary house system overlay
            "chart1_fill_1": "#1A0A1A",
            "chart1_fill_2": "#0D0D0D",
            "chart2_fill_1": "#0A1A1A",
            "chart2_fill_2": "#0D1515",
            "chart3_fill_1": "#0A1A0A",
            "chart3_fill_2": "#0D150D",
            "chart4_fill_1": "#1A0A1A",
            "chart4_fill_2": "#150D15",
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
            "chart1_color": "#00FFFF",
            "chart2_color": "#FF00FF",
            "chart3_color": "#39FF14",
            "chart4_color": "#FFFF00",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.NEON),
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
            "secondary_color": "#8B4513",  # Saddle brown for secondary house system overlay
            "chart1_fill_1": "#EDE4D0",
            "chart1_fill_2": "#F4ECD8",
            "chart2_fill_1": "#E8DCC8",
            "chart2_fill_2": "#EFE5D2",
            "chart3_fill_1": "#E4D8C4",
            "chart3_fill_2": "#EBE2CE",
            "chart4_fill_1": "#E0D4C0",
            "chart4_fill_2": "#E7DECA",
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
            "chart1_color": "#4A3728",
            "chart2_color": "#6B5744",
            "chart3_color": "#8B7355",
            "chart4_color": "#A68B6B",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.SEPIA),
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
            "secondary_color": "#B4A7D6",  # Soft lavender for secondary house system overlay
            "chart1_fill_1": "#F5F5F5",
            "chart1_fill_2": "#FAFAFA",
            "chart2_fill_1": "#E8F0F8",
            "chart2_fill_2": "#F0F5FA",
            "chart3_fill_1": "#E8F8E8",
            "chart3_fill_2": "#F0FAF0",
            "chart4_fill_1": "#F0E8F8",
            "chart4_fill_2": "#F5F0FA",
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
            "chart1_color": "#555555",
            "chart2_color": "#7A9EC2",
            "chart3_color": "#7AC27A",
            "chart4_color": "#B4A7D6",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.PASTEL),
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
            "secondary_color": "#DA70D6",  # Orchid for secondary house system overlay
            "chart1_fill_1": "#241540",
            "chart1_fill_2": "#1A0F2E",
            "chart2_fill_1": "#1E1840",
            "chart2_fill_2": "#161230",
            "chart3_fill_1": "#182040",
            "chart3_fill_2": "#121830",
            "chart4_fill_1": "#281540",
            "chart4_fill_2": "#1E1030",
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
            "chart1_color": "#FFD700",
            "chart2_color": "#DA70D6",
            "chart3_color": "#87CEEB",
            "chart4_color": "#98FB98",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.CELESTIAL),
            "default": {"color": "#7B5FAF", "width": 0.5, "dash": "2,2"},
            "line_color": "#6B4FA3",
            "background_color": "#1A0F2E",
        },
    }


def _get_atlas_theme() -> dict[str, Any]:
    """Atlas theme - cream background with purple/gold accents, designed for PDF atlases."""
    return {
        "background_color": "#FAF8F5",  # Cream
        "border_color": "#6B4D6E",  # Secondary purple
        "border_width": 1,
        "font_family_glyphs": '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
        "font_family_text": '"Arial", "Helvetica", sans-serif',
        "zodiac": {
            "ring_color": "#F0EBE6",  # Slightly darker cream
            "line_color": "#8E6B8A",  # Accent purple
            "glyph_color": "#4A3353",  # Primary purple
            "glyph_size": "20px",
        },
        "houses": {
            "line_color": "#C4B5A0",  # Warm grey-brown
            "line_width": 0.8,
            "number_color": "#8E6B8A",  # Accent purple
            "number_size": "11px",
            "fill_alternate": True,
            "fill_color_1": "#F5F0EB",  # Slightly darker cream
            "fill_color_2": "#FAF8F5",  # Cream
            "secondary_color": "#B8953D",  # Gold for secondary house system overlay
            "chart1_fill_1": "#F5F0EB",
            "chart1_fill_2": "#FAF8F5",
            "chart2_fill_1": "#F0EBE8",
            "chart2_fill_2": "#F8F5F2",
            "chart3_fill_1": "#EBF0EB",
            "chart3_fill_2": "#F5F8F5",
            "chart4_fill_1": "#F0EBF0",
            "chart4_fill_2": "#F8F5F8",
        },
        "angles": {
            "line_color": "#4A3353",  # Primary purple
            "line_width": 2.5,
            "glyph_color": "#2D2330",  # Text dark
            "glyph_size": "12px",
        },
        "outer_wheel_angles": {
            "line_color": "#6B4D6E",  # Secondary purple
            "line_width": 1.8,
            "glyph_color": "#4A3353",  # Primary purple
            "glyph_size": "11px",
        },
        "planets": {
            "glyph_color": "#2D2330",  # Text dark
            "glyph_size": "32px",
            "info_color": "#4A3353",  # Primary purple
            "info_size": "10px",
            "retro_color": "#B8953D",  # Gold for retrograde
            "outer_wheel_planet_color": "#6B4D6E",  # Secondary purple for outer wheel
            "chart1_color": "#2D2330",
            "chart2_color": "#4A3353",
            "chart3_color": "#6B4D6E",
            "chart4_color": "#8E6B8A",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.CLASSIC),
            "default": {"color": "#C4B5A0", "width": 0.5, "dash": "2,2"},
            "line_color": "#8E6B8A",
            "background_color": "#FAF8F5",
        },
    }


# ============================================================================
# Data Science Themes
# ============================================================================


def _get_viridis_theme() -> dict[str, Any]:
    """Viridis theme - perceptually uniform purple→green→yellow palette."""
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
            "secondary_color": "#7AD151",  # Yellow-green for secondary house system overlay
            "chart1_fill_1": "#222222",
            "chart1_fill_2": "#1C1C1C",
            "chart2_fill_1": "#1C2228",
            "chart2_fill_2": "#181E22",
            "chart3_fill_1": "#1C2822",
            "chart3_fill_2": "#18221E",
            "chart4_fill_1": "#22281C",
            "chart4_fill_2": "#1E2218",
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
            "chart1_color": "#22A884",
            "chart2_color": "#414487",
            "chart3_color": "#7AD151",
            "chart4_color": "#FDE724",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.VIRIDIS),
            "default": {"color": "#414487", "width": 0.5, "dash": "2,2"},
            "line_color": "#2A788E",
            "background_color": "#1C1C1C",
        },
    }


def _get_plasma_theme() -> dict[str, Any]:
    """Plasma theme - vibrant blue→purple→orange→yellow palette."""
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
            "secondary_color": "#E16462",  # Orange-red for secondary house system overlay
            "chart1_fill_1": "#150A5F",
            "chart1_fill_2": "#0D0887",
            "chart2_fill_1": "#200A55",
            "chart2_fill_2": "#180878",
            "chart3_fill_1": "#2A0A4A",
            "chart3_fill_2": "#220868",
            "chart4_fill_1": "#350A40",
            "chart4_fill_2": "#2C0858",
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
            "chart1_color": "#E16462",
            "chart2_color": "#B12A90",
            "chart3_color": "#FCA636",
            "chart4_color": "#F0F921",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.PLASMA),
            "default": {"color": "#8F0DA4", "width": 0.5, "dash": "2,2"},
            "line_color": "#B12A90",
            "background_color": "#0D0887",
        },
    }


def _get_inferno_theme() -> dict[str, Any]:
    """Inferno theme - dramatic black→red→orange→yellow palette."""
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
            "secondary_color": "#ED6925",  # Orange for secondary house system overlay
            "chart1_fill_1": "#1B0C41",
            "chart1_fill_2": "#000004",
            "chart2_fill_1": "#280C35",
            "chart2_fill_2": "#100004",
            "chart3_fill_1": "#350C28",
            "chart3_fill_2": "#200004",
            "chart4_fill_1": "#420C1C",
            "chart4_fill_2": "#300004",
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
            "chart1_color": "#ED6925",
            "chart2_color": "#A52C60",
            "chart3_color": "#FB9A06",
            "chart4_color": "#FCFFA4",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.INFERNO),
            "default": {"color": "#781C6D", "width": 0.5, "dash": "2,2"},
            "line_color": "#A52C60",
            "background_color": "#000004",
        },
    }


def _get_magma_theme() -> dict[str, Any]:
    """Magma theme - subtle black→purple→pink→yellow palette."""
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
            "secondary_color": "#D3436E",  # Pink for secondary house system overlay
            "chart1_fill_1": "#0B0924",
            "chart1_fill_2": "#000004",
            "chart2_fill_1": "#150920",
            "chart2_fill_2": "#080004",
            "chart3_fill_1": "#1F091C",
            "chart3_fill_2": "#100004",
            "chart4_fill_1": "#290918",
            "chart4_fill_2": "#180004",
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
            "chart1_color": "#D3436E",
            "chart2_color": "#7B2382",
            "chart3_color": "#EB5760",
            "chart4_color": "#FCFDBF",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.MAGMA),
            "default": {"color": "#5F187F", "width": 0.5, "dash": "2,2"},
            "line_color": "#7B2382",
            "background_color": "#000004",
        },
    }


def _get_cividis_theme() -> dict[str, Any]:
    """Cividis theme - CVD-optimized blue→yellow palette."""
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
            "secondary_color": "#E5C482",  # Gold/tan for secondary house system overlay
            "chart1_fill_1": "#00306E",
            "chart1_fill_2": "#00204C",
            "chart2_fill_1": "#0A3868",
            "chart2_fill_2": "#052850",
            "chart3_fill_1": "#144062",
            "chart3_fill_2": "#0A3054",
            "chart4_fill_1": "#1E485C",
            "chart4_fill_2": "#0F3858",
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
            "chart1_color": "#9B9680",
            "chart2_color": "#4E6B7C",
            "chart3_color": "#C5AC83",
            "chart4_color": "#FFEA46",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.CIVIDIS),
            "default": {"color": "#4E6B7C", "width": 0.5, "dash": "2,2"},
            "line_color": "#73807D",
            "background_color": "#00204C",
        },
    }


def _get_turbo_theme() -> dict[str, Any]:
    """Turbo theme - Google's improved rainbow palette."""
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
            "secondary_color": "#1AE4B6",  # Turquoise for secondary house system overlay
            "chart1_fill_1": "#242438",
            "chart1_fill_2": "#1A1A2E",
            "chart2_fill_1": "#1E2838",
            "chart2_fill_2": "#161C2E",
            "chart3_fill_1": "#1E3830",
            "chart3_fill_2": "#162E26",
            "chart4_fill_1": "#283820",
            "chart4_fill_2": "#1E2E18",
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
            "chart1_color": "#72FE5E",
            "chart2_color": "#4662D7",
            "chart3_color": "#1AE4B6",
            "chart4_color": "#FABA39",
        },
        "aspects": {
            **build_aspect_styles_from_palette(AspectPalette.TURBO),
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
        ChartTheme.ATLAS: "Atlas - Cream background with purple/gold accents for PDF atlases",
        # Data science themes
        ChartTheme.VIRIDIS: "Viridis - Perceptually uniform purple→green→yellow (colorblind-friendly)",
        ChartTheme.PLASMA: "Plasma - Vibrant blue→purple→orange→yellow gradient",
        ChartTheme.INFERNO: "Inferno - Dramatic black→red→orange→yellow fire palette",
        ChartTheme.MAGMA: "Magma - Subtle black→purple→pink→yellow volcanic palette",
        ChartTheme.CIVIDIS: "Cividis - Blue→yellow palette optimized for color vision deficiency",
        ChartTheme.TURBO: "Turbo - Google's improved rainbow (high contrast)",
    }
    return descriptions.get(theme, "Unknown theme")
