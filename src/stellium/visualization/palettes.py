"""
Zodiac Color Palettes (stellium.visualization.palettes)

Defines color schemes for the zodiac wheel visualization, aspect lines,
planet glyphs, and color utilities for adaptive theming.
"""

import colorsys
from enum import Enum
from functools import lru_cache


class ZodiacPalette(str, Enum):
    """Available color palettes for the zodiac wheel."""

    # Base palettes
    GREY = "grey"
    RAINBOW = "rainbow"
    ELEMENTAL = "elemental"
    CARDINALITY = "cardinality"

    # Theme-coordinated rainbow variants
    RAINBOW_DARK = "rainbow_dark"
    RAINBOW_MIDNIGHT = "rainbow_midnight"
    RAINBOW_NEON = "rainbow_neon"
    RAINBOW_SEPIA = "rainbow_sepia"
    RAINBOW_CELESTIAL = "rainbow_celestial"

    # Theme-coordinated elemental variants
    ELEMENTAL_DARK = "elemental_dark"
    ELEMENTAL_MIDNIGHT = "elemental_midnight"
    ELEMENTAL_NEON = "elemental_neon"
    ELEMENTAL_SEPIA = "elemental_sepia"

    # Data science palettes
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    TURBO = "turbo"
    COOLWARM = "coolwarm"
    SPECTRAL = "spectral"


# Zodiac sign properties for palette mapping
SIGN_ELEMENTS = {
    0: "fire",  # Aries
    1: "earth",  # Taurus
    2: "air",  # Gemini
    3: "water",  # Cancer
    4: "fire",  # Leo
    5: "earth",  # Virgo
    6: "air",  # Libra
    7: "water",  # Scorpio
    8: "fire",  # Sagittarius
    9: "earth",  # Capricorn
    10: "air",  # Aquarius
    11: "water",  # Pisces
}

SIGN_MODALITIES = {
    0: "cardinal",  # Aries
    1: "fixed",  # Taurus
    2: "mutable",  # Gemini
    3: "cardinal",  # Cancer
    4: "fixed",  # Leo
    5: "mutable",  # Virgo
    6: "cardinal",  # Libra
    7: "fixed",  # Scorpio
    8: "mutable",  # Sagittarius
    9: "cardinal",  # Capricorn
    10: "fixed",  # Aquarius
    11: "mutable",  # Pisces
}


@lru_cache(maxsize=128)
def get_palette_colors(palette: ZodiacPalette | str) -> list[str]:
    """
    Get the color list for a zodiac wheel palette.

    Returns a list of 12 colors (one per sign, starting with Aries).
    Results are cached in memory for performance.

    Special case: If palette is a string starting with "single_color:",
    extracts the hex color and returns 12 copies of it for a monochrome wheel.

    Args:
        palette: The palette to use (ZodiacPalette enum or "single_color:#RRGGBB" string)

    Returns:
        List of 12 hex color strings
    """
    # Handle dynamic single-color palettes
    if isinstance(palette, str) and palette.startswith("single_color:"):
        # Extract hex color from "single_color:#RRGGBB"
        color = palette.split(":", 1)[1]
        return [color] * 12

    # Convert string to enum if needed (for backwards compatibility)
    if isinstance(palette, str):
        palette = ZodiacPalette(palette)

    if palette == ZodiacPalette.GREY:
        # All signs same color (classic grey)
        return ["#EEEEEE"] * 12

    elif palette == ZodiacPalette.RAINBOW:
        # Tasteful rainbow: soft, desaturated colors progressing through hue wheel
        # Starting with Aries (red) and progressing through the spectrum
        return [
            "#E8B4B8",  # Aries - soft red
            "#E8C4B8",  # Taurus - soft orange
            "#E8D8B8",  # Gemini - soft yellow-orange
            "#E8E8B8",  # Cancer - soft yellow
            "#D8E8B8",  # Leo - soft yellow-green
            "#C4E8B8",  # Virgo - soft green
            "#B8E8C4",  # Libra - soft cyan-green
            "#B8E8D8",  # Scorpio - soft cyan
            "#B8D8E8",  # Sagittarius - soft blue
            "#B8C4E8",  # Capricorn - soft indigo
            "#C4B8E8",  # Aquarius - soft violet
            "#D8B8E8",  # Pisces - soft magenta
        ]

    elif palette == ZodiacPalette.ELEMENTAL:
        # 4-color elemental palette
        element_colors = {
            "fire": "#F4D4D4",  # Soft warm red
            "earth": "#D4E4D4",  # Soft green
            "air": "#D4E4F4",  # Soft blue
            "water": "#E4D4F4",  # Soft purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.CARDINALITY:
        # 3-color cardinality/modality palette
        modality_colors = {
            "cardinal": "#F4E4D4",  # Soft peach (initiating)
            "fixed": "#D4E4E4",  # Soft teal (sustaining)
            "mutable": "#E4D4E4",  # Soft lavender (adapting)
        }
        return [modality_colors[SIGN_MODALITIES[i]] for i in range(12)]

    # ========================================================================
    # Theme-coordinated rainbow variants
    # ========================================================================

    elif palette == ZodiacPalette.RAINBOW_DARK:
        # Dark theme: Muted, darker rainbow colors
        return [
            "#B88B8F",  # Aries - muted red
            "#B89B8F",  # Taurus - muted orange
            "#B8AB8F",  # Gemini - muted yellow-orange
            "#B8B88F",  # Cancer - muted yellow
            "#ABB88F",  # Leo - muted yellow-green
            "#9BB88F",  # Virgo - muted green
            "#8FB89B",  # Libra - muted cyan-green
            "#8FB8AB",  # Scorpio - muted cyan
            "#8FABB8",  # Sagittarius - muted blue
            "#8F9BB8",  # Capricorn - muted indigo
            "#9B8FB8",  # Aquarius - muted violet
            "#AB8FB8",  # Pisces - muted magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_MIDNIGHT:
        # Midnight theme: Cool, deep blues and purples
        return [
            "#4A5A7C",  # Aries - deep blue-grey
            "#3A6A8C",  # Taurus - deep cyan-blue
            "#3A7A9C",  # Gemini - deep cyan
            "#3A8AAC",  # Cancer - deep sky blue
            "#3A8A9C",  # Leo - deep teal
            "#3A9A8C",  # Virgo - deep blue-green
            "#3A9A7C",  # Libra - deep sea green
            "#3A8A6C",  # Scorpio - deep forest green
            "#4A6A7C",  # Sagittarius - deep blue
            "#5A5A8C",  # Capricorn - deep indigo
            "#6A4A8C",  # Aquarius - deep purple
            "#7A3A8C",  # Pisces - deep magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_NEON:
        # Neon theme: Super bright, saturated neon colors
        return [
            "#FF00AA",  # Aries - hot pink
            "#FF3300",  # Taurus - neon orange-red
            "#FF6600",  # Gemini - neon orange
            "#FFFF00",  # Cancer - electric yellow
            "#AAFF00",  # Leo - neon lime
            "#00FF00",  # Virgo - electric green
            "#00FFAA",  # Libra - neon cyan-green
            "#00FFFF",  # Scorpio - electric cyan
            "#0088FF",  # Sagittarius - neon blue
            "#0000FF",  # Capricorn - electric blue
            "#AA00FF",  # Aquarius - neon violet
            "#FF00FF",  # Pisces - electric magenta
        ]

    elif palette == ZodiacPalette.RAINBOW_SEPIA:
        # Sepia theme: Warm browns, oranges, and earth tones
        return [
            "#C4A090",  # Aries - terracotta
            "#C4AA90",  # Taurus - warm tan
            "#C4B490",  # Gemini - sandy brown
            "#C4BE90",  # Cancer - wheat
            "#B4C490",  # Leo - sage
            "#AAC490",  # Virgo - olive
            "#90C4AA",  # Libra - sea foam brown
            "#90C4B4",  # Scorpio - sage blue
            "#90B4C4",  # Sagittarius - dusty blue
            "#90AAC4",  # Capricorn - slate blue
            "#A090C4",  # Aquarius - dusty purple
            "#AA90C4",  # Pisces - mauve
        ]

    elif palette == ZodiacPalette.RAINBOW_CELESTIAL:
        # Celestial theme: Deep cosmic purples, blues, and golds
        return [
            "#9B4FA3",  # Aries - cosmic purple
            "#8B5FAF",  # Taurus - deep lavender
            "#7B6FAF",  # Gemini - periwinkle
            "#6B7FAF",  # Cancer - cosmic blue
            "#5B8FAF",  # Leo - stellar blue
            "#4B9FAF",  # Virgo - galaxy cyan
            "#4BAFAF",  # Libra - nebula teal
            "#4BAFAF",  # Scorpio - deep teal
            "#5B9FAF",  # Sagittarius - space blue
            "#6B8FAF",  # Capricorn - cosmic indigo
            "#7B7FAF",  # Aquarius - deep violet
            "#8B6FAF",  # Pisces - stellar purple
        ]

    # ========================================================================
    # Theme-coordinated elemental variants
    # ========================================================================

    elif palette == ZodiacPalette.ELEMENTAL_DARK:
        # Dark theme: Darker, muted elemental colors
        element_colors = {
            "fire": "#B88080",  # Darker warm red
            "earth": "#80A880",  # Darker green
            "air": "#8080B8",  # Darker blue
            "water": "#A880B8",  # Darker purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_MIDNIGHT:
        # Midnight theme: Cool-toned elements
        element_colors = {
            "fire": "#5A6A8C",  # Cool blue-grey (fire as stellium)
            "earth": "#4A7A7C",  # Deep teal (earth as ocean)
            "air": "#6A7AAC",  # Deep sky blue
            "water": "#5A5A8C",  # Deep indigo
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_NEON:
        # Neon theme: Electric bright elements
        element_colors = {
            "fire": "#FF0066",  # Electric magenta
            "earth": "#00FF66",  # Neon green
            "air": "#00CCFF",  # Electric cyan
            "water": "#CC00FF",  # Neon purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    elif palette == ZodiacPalette.ELEMENTAL_SEPIA:
        # Sepia theme: Warm-toned elements
        element_colors = {
            "fire": "#C49080",  # Terracotta
            "earth": "#A0B490",  # Olive
            "air": "#90A8C4",  # Dusty blue
            "water": "#A490B4",  # Dusty purple
        }
        return [element_colors[SIGN_ELEMENTS[i]] for i in range(12)]

    # ========================================================================
    # Data Science Palettes (12-color samples from matplotlib colormaps)
    # ========================================================================

    elif palette == ZodiacPalette.VIRIDIS:
        # Viridis: perceptually uniform, colorblind-friendly (purple → green → yellow)
        return [
            "#440154",
            "#482475",
            "#414487",
            "#355F8D",
            "#2A788E",
            "#21918C",
            "#22A884",
            "#42BE71",
            "#7AD151",
            "#BBDF27",
            "#FDE724",
            "#FDE724",
        ]

    elif palette == ZodiacPalette.PLASMA:
        # Plasma: vibrant (dark blue → purple → orange → yellow)
        return [
            "#0D0887",
            "#41049D",
            "#6A00A8",
            "#8F0DA4",
            "#B12A90",
            "#CC4778",
            "#E16462",
            "#F1844B",
            "#FCA636",
            "#FCCE25",
            "#F0F921",
            "#F0F921",
        ]

    elif palette == ZodiacPalette.INFERNO:
        # Inferno: dramatic (black → red → orange → yellow → white)
        return [
            "#000004",
            "#1B0C41",
            "#4A0C6B",
            "#781C6D",
            "#A52C60",
            "#CF4446",
            "#ED6925",
            "#FB9A06",
            "#F7D03C",
            "#FCFFA4",
            "#FCFFA4",
            "#FCFFA4",
        ]

    elif palette == ZodiacPalette.MAGMA:
        # Magma: subtle (black → purple → pink → yellow → white)
        return [
            "#000004",
            "#0B0924",
            "#231151",
            "#410F75",
            "#5F187F",
            "#7B2382",
            "#982D80",
            "#B73779",
            "#D3436E",
            "#EB5760",
            "#F8765C",
            "#FCFDBF",
        ]

    elif palette == ZodiacPalette.CIVIDIS:
        # Cividis: optimized for color vision deficiency (blue → yellow)
        return [
            "#00204C",
            "#00306E",
            "#00447A",
            "#25567B",
            "#4E6B7C",
            "#73807D",
            "#9B9680",
            "#C5AC83",
            "#E5C482",
            "#FDDC7D",
            "#FEE883",
            "#FFEA46",
        ]

    elif palette == ZodiacPalette.TURBO:
        # Turbo: Google's improved rainbow (blue → cyan → green → yellow → red)
        return [
            "#30123B",
            "#4662D7",
            "#1FAAD2",
            "#1AE4B6",
            "#72FE5E",
            "#C8EF34",
            "#FABA39",
            "#F66B19",
            "#CA2A04",
            "#7A0403",
            "#7A0403",
            "#7A0403",
        ]

    elif palette == ZodiacPalette.COOLWARM:
        # Coolwarm: diverging (blue → white → red)
        return [
            "#3B4CC0",
            "#5E6EC5",
            "#7F91CB",
            "#A1B4D0",
            "#C3D7D6",
            "#E5E5E5",
            "#F1D4D0",
            "#F3B6AF",
            "#EC8C88",
            "#DD5C5C",
            "#C73333",
            "#B40426",
        ]

    elif palette == ZodiacPalette.SPECTRAL:
        # Spectral: diverging (red → yellow → green → blue → purple)
        return [
            "#9E0142",
            "#D53E4F",
            "#F46D43",
            "#FDAE61",
            "#FEE08B",
            "#FFFFBF",
            "#E6F598",
            "#ABDDA4",
            "#66C2A5",
            "#3288BD",
            "#5E4FA2",
            "#5E4FA2",
        ]

    else:
        # Fallback to grey
        return ["#EEEEEE"] * 12


def get_palette_description(palette: ZodiacPalette) -> str:
    """
    Get a human-readable description of a palette.

    Args:
        palette: The palette to describe

    Returns:
        Description string
    """
    descriptions = {
        # Base palettes
        ZodiacPalette.GREY: "Classic grey wheel (no color)",
        ZodiacPalette.RAINBOW: "Rainbow spectrum (12 soft colors)",
        ZodiacPalette.ELEMENTAL: "4-color elemental (Fire/Earth/Air/Water)",
        ZodiacPalette.CARDINALITY: "3-color modality (Cardinal/Fixed/Mutable)",
        # Rainbow variants
        ZodiacPalette.RAINBOW_DARK: "Dark rainbow (muted, darker spectrum)",
        ZodiacPalette.RAINBOW_MIDNIGHT: "Midnight rainbow (cool blues and purples)",
        ZodiacPalette.RAINBOW_NEON: "Neon rainbow (super bright electric colors)",
        ZodiacPalette.RAINBOW_SEPIA: "Sepia rainbow (warm browns and earth tones)",
        ZodiacPalette.RAINBOW_CELESTIAL: "Celestial rainbow (cosmic purples and blues)",
        # Elemental variants
        ZodiacPalette.ELEMENTAL_DARK: "Dark elemental (muted element colors)",
        ZodiacPalette.ELEMENTAL_MIDNIGHT: "Midnight elemental (cool-toned elements)",
        ZodiacPalette.ELEMENTAL_NEON: "Neon elemental (electric element colors)",
        ZodiacPalette.ELEMENTAL_SEPIA: "Sepia elemental (warm-toned elements)",
        # Data science palettes
        ZodiacPalette.VIRIDIS: "Viridis (purple→green→yellow, colorblind-friendly)",
        ZodiacPalette.PLASMA: "Plasma (blue→purple→orange→yellow, vibrant)",
        ZodiacPalette.INFERNO: "Inferno (black→red→orange→yellow, dramatic)",
        ZodiacPalette.MAGMA: "Magma (black→purple→pink→yellow, subtle)",
        ZodiacPalette.CIVIDIS: "Cividis (blue→yellow, CVD-optimized)",
        ZodiacPalette.TURBO: "Turbo (rainbow, improved Google palette)",
        ZodiacPalette.COOLWARM: "Coolwarm (blue→white→red, diverging)",
        ZodiacPalette.SPECTRAL: "Spectral (red→yellow→green→blue, diverging)",
    }
    return descriptions.get(palette, "Unknown palette")


# ============================================================================
# ASPECT PALETTES
# ============================================================================


class AspectPalette(str, Enum):
    """Available color palettes for aspect lines."""

    # Base/theme palettes
    CLASSIC = "classic"
    DARK = "dark"
    MIDNIGHT = "midnight"
    NEON = "neon"
    SEPIA = "sepia"
    PASTEL = "pastel"
    CELESTIAL = "celestial"

    # Monochromatic variants
    GREYSCALE = "greyscale"
    BLUES = "blues"
    PURPLES = "purples"
    EARTH_TONES = "earth_tones"

    # Data science palettes
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    TURBO = "turbo"


@lru_cache(maxsize=128)
def get_aspect_palette_colors(palette: AspectPalette) -> dict[str, str]:
    """
    Get aspect colors for a given palette.

    Returns a dictionary mapping aspect names to hex colors.
    Includes Conjunction, Sextile, Square, Trine, Opposition,
    and minor aspects (Semisextile, Semisquare, Sesquisquare, Quincunx).
    Results are cached in memory for performance.

    Args:
        palette: The aspect palette to use

    Returns:
        Dictionary mapping aspect names to hex color strings
    """
    if palette == AspectPalette.CLASSIC:
        # Registry defaults (from core/registry.py)
        return {
            "Conjunction": "#34495E",
            "Sextile": "#27AE60",
            "Square": "#F39C12",
            "Trine": "#3498DB",
            "Opposition": "#E74C3C",
            "Semisextile": "#95A5A6",
            "Semisquare": "#E67E22",
            "Sesquisquare": "#D68910",
            "Quincunx": "#9B59B6",
        }

    elif palette == AspectPalette.DARK:
        # Dark theme: bright accents on dark backgrounds
        return {
            "Conjunction": "#FFD700",
            "Sextile": "#95E1D3",
            "Square": "#FF6B9D",
            "Trine": "#4ECDC4",
            "Opposition": "#FF6B6B",
            "Semisextile": "#888888",
            "Semisquare": "#FF9999",
            "Sesquisquare": "#FFAA99",
            "Quincunx": "#BB88CC",
        }

    elif palette == AspectPalette.MIDNIGHT:
        # Midnight theme: gold and distinct blues/cyans for clarity
        return {
            "Conjunction": "#FFD700",  # Gold (bright, stands out)
            "Sextile": "#00CED1",  # Dark turquoise (distinct from other blues)
            "Square": "#FFA500",  # Orange (contrast to blues)
            "Trine": "#4169E1",  # Royal blue (distinct from cyan)
            "Opposition": "#DC143C",  # Crimson (distinct from other colors)
            "Semisextile": "#7B8FA0",  # Slate gray
            "Semisquare": "#FF8C00",  # Dark orange
            "Sesquisquare": "#FFB347",  # Light orange
            "Quincunx": "#9370DB",  # Medium purple
        }

    elif palette == AspectPalette.NEON:
        # Neon theme: cyberpunk bright colors
        return {
            "Conjunction": "#FFFF00",
            "Sextile": "#39FF14",
            "Square": "#FF1493",
            "Trine": "#00FFFF",
            "Opposition": "#FF00FF",
            "Semisextile": "#00FF88",
            "Semisquare": "#FF6600",
            "Sesquisquare": "#FF9900",
            "Quincunx": "#CC00FF",
        }

    elif palette == AspectPalette.SEPIA:
        # Sepia theme: warm browns with more contrast
        return {
            "Conjunction": "#654321",  # Dark brown (distinct)
            "Sextile": "#D2691E",  # Chocolate (orange-brown, distinct)
            "Square": "#8B4513",  # Saddle brown (medium)
            "Trine": "#CD853F",  # Peru (lighter tan)
            "Opposition": "#A0522D",  # Sienna (reddish brown)
            "Semisextile": "#C4A582",  # Tan
            "Semisquare": "#DEB887",  # Burlywood
            "Sesquisquare": "#F4A460",  # Sandy brown
            "Quincunx": "#BC8F8F",  # Rosy brown
        }

    elif palette == AspectPalette.PASTEL:
        # Pastel theme: soft but distinct colors
        return {
            "Conjunction": "#B39EB5",  # Pastel purple (distinct)
            "Sextile": "#77DD77",  # Pastel green (bright enough to see)
            "Square": "#FFB347",  # Pastel orange (warm, stands out)
            "Trine": "#779ECB",  # Pastel blue (cool, distinct)
            "Opposition": "#FF6961",  # Pastel red (distinct warm)
            "Semisextile": "#CFCFC4",  # Pastel gray
            "Semisquare": "#FDFD96",  # Pastel yellow
            "Sesquisquare": "#FFD1DC",  # Pastel pink
            "Quincunx": "#C5A3FF",  # Pastel lavender
        }

    elif palette == AspectPalette.CELESTIAL:
        # Celestial theme: cosmic purples and gold
        return {
            "Conjunction": "#FFD700",
            "Sextile": "#DDA0DD",
            "Square": "#BA55D3",
            "Trine": "#9370DB",
            "Opposition": "#DA70D6",
            "Semisextile": "#B8A0C0",
            "Semisquare": "#C888D0",
            "Sesquisquare": "#B878C0",
            "Quincunx": "#A868B0",
        }

    elif palette == AspectPalette.GREYSCALE:
        # Monochromatic greyscale
        return {
            "Conjunction": "#333333",
            "Sextile": "#666666",
            "Square": "#555555",
            "Trine": "#777777",
            "Opposition": "#444444",
            "Semisextile": "#999999",
            "Semisquare": "#888888",
            "Sesquisquare": "#888888",
            "Quincunx": "#888888",
        }

    elif palette == AspectPalette.BLUES:
        # Monochromatic blues
        return {
            "Conjunction": "#1A3A52",
            "Sextile": "#5B9BD5",
            "Square": "#2E5F8F",
            "Trine": "#70ADE3",
            "Opposition": "#1F4E78",
            "Semisextile": "#8BBDEA",
            "Semisquare": "#4A7EAD",
            "Sesquisquare": "#3D6A99",
            "Quincunx": "#6098C7",
        }

    elif palette == AspectPalette.PURPLES:
        # Monochromatic purples
        return {
            "Conjunction": "#5B2C6F",
            "Sextile": "#9B59B6",
            "Square": "#7D3C98",
            "Trine": "#A569BD",
            "Opposition": "#6C3483",
            "Semisextile": "#BB8FCE",
            "Semisquare": "#8E44AD",
            "Sesquisquare": "#7D3C98",
            "Quincunx": "#9B59B6",
        }

    elif palette == AspectPalette.EARTH_TONES:
        # Warm earth tones
        return {
            "Conjunction": "#8B4513",
            "Sextile": "#6B8E23",
            "Square": "#CD853F",
            "Trine": "#8FBC8F",
            "Opposition": "#D2691E",
            "Semisextile": "#BDB76B",
            "Semisquare": "#BC8F5F",
            "Sesquisquare": "#A0753F",
            "Quincunx": "#9A7B4F",
        }

    elif palette == AspectPalette.VIRIDIS:
        # Viridis: purple → green → yellow
        return {
            "Conjunction": "#440154",
            "Sextile": "#22A884",
            "Square": "#414487",
            "Trine": "#7AD151",
            "Opposition": "#FDE724",
            "Semisextile": "#2A788E",
            "Semisquare": "#5DC863",
            "Sesquisquare": "#B8DE29",
            "Quincunx": "#482475",
        }

    elif palette == AspectPalette.PLASMA:
        # Plasma: blue → purple → orange → yellow
        return {
            "Conjunction": "#0D0887",
            "Sextile": "#B12A90",
            "Square": "#6A00A8",
            "Trine": "#FCA636",
            "Opposition": "#F0F921",
            "Semisextile": "#8F0DA4",
            "Semisquare": "#E16462",
            "Sesquisquare": "#FCCE25",
            "Quincunx": "#41049D",
        }

    elif palette == AspectPalette.INFERNO:
        # Inferno: black → red → orange → yellow
        return {
            "Conjunction": "#000004",
            "Sextile": "#CF4446",
            "Square": "#781C6D",
            "Trine": "#FB9A06",
            "Opposition": "#FCFFA4",
            "Semisextile": "#A52C60",
            "Semisquare": "#ED6925",
            "Sesquisquare": "#F7D03C",
            "Quincunx": "#4A0C6B",
        }

    elif palette == AspectPalette.MAGMA:
        # Magma: black → purple → pink → yellow
        return {
            "Conjunction": "#000004",
            "Sextile": "#982D80",
            "Square": "#5F187F",
            "Trine": "#EB5760",
            "Opposition": "#FCFDBF",
            "Semisextile": "#7B2382",
            "Semisquare": "#D3436E",
            "Sesquisquare": "#F8765C",
            "Quincunx": "#410F75",
        }

    elif palette == AspectPalette.CIVIDIS:
        # Cividis: blue → yellow (CVD-friendly)
        return {
            "Conjunction": "#00204C",
            "Sextile": "#73807D",
            "Square": "#00447A",
            "Trine": "#C5AC83",
            "Opposition": "#FFEA46",
            "Semisextile": "#4E6B7C",
            "Semisquare": "#9B9680",
            "Sesquisquare": "#E5C482",
            "Quincunx": "#25567B",
        }

    elif palette == AspectPalette.TURBO:
        # Turbo: rainbow (blue → cyan → green → yellow → red)
        return {
            "Conjunction": "#30123B",
            "Sextile": "#72FE5E",
            "Square": "#1FAAD2",
            "Trine": "#FABA39",
            "Opposition": "#CA2A04",
            "Semisextile": "#1AE4B6",
            "Semisquare": "#C8EF34",
            "Sesquisquare": "#F66B19",
            "Quincunx": "#4662D7",
        }

    else:
        # Fallback to classic
        return get_aspect_palette_colors(AspectPalette.CLASSIC)


def build_aspect_styles_from_palette(palette: AspectPalette | str) -> dict[str, dict]:
    """
    Build complete aspect styling dict with palette colors + registry line styles.

    This merges palette colors with the ASPECT_REGISTRY's line_width and dash_pattern,
    ensuring themes only change colors while preserving the registry's line styling.

    Args:
        palette: The aspect palette to use for colors

    Returns:
        Dictionary mapping aspect names to style dicts with "color", "width", "dash" keys
    """
    from stellium.core.registry import ASPECT_REGISTRY

    # Get colors from palette
    if isinstance(palette, str):
        palette = AspectPalette(palette)
    colors = get_aspect_palette_colors(palette)

    # Build styles using registry metadata for width/dash
    styles = {}
    for aspect_info in ASPECT_REGISTRY.values():
        if aspect_info.category in ["Major", "Minor"]:
            color = colors.get(aspect_info.name, aspect_info.color)
            styles[aspect_info.name] = {
                "color": color,
                "width": aspect_info.metadata.get("line_width", 1.5),
                "dash": aspect_info.metadata.get("dash_pattern", "1,0"),
            }

    return styles


def get_aspect_palette_description(palette: AspectPalette) -> str:
    """
    Get a human-readable description of an aspect palette.

    Args:
        palette: The palette to describe

    Returns:
        Description string
    """
    descriptions = {
        AspectPalette.CLASSIC: "Classic (registry defaults)",
        AspectPalette.DARK: "Dark (bright accents for dark backgrounds)",
        AspectPalette.MIDNIGHT: "Midnight (gold and cool blues)",
        AspectPalette.NEON: "Neon (cyberpunk bright colors)",
        AspectPalette.SEPIA: "Sepia (warm browns)",
        AspectPalette.PASTEL: "Pastel (soft gentle colors)",
        AspectPalette.CELESTIAL: "Celestial (cosmic purples and gold)",
        AspectPalette.GREYSCALE: "Greyscale (monochromatic greys)",
        AspectPalette.BLUES: "Blues (monochromatic blue tones)",
        AspectPalette.PURPLES: "Purples (monochromatic purple tones)",
        AspectPalette.EARTH_TONES: "Earth Tones (warm natural colors)",
        AspectPalette.VIRIDIS: "Viridis (purple→green→yellow, perceptually uniform)",
        AspectPalette.PLASMA: "Plasma (blue→purple→orange→yellow)",
        AspectPalette.INFERNO: "Inferno (black→red→orange→yellow)",
        AspectPalette.MAGMA: "Magma (black→purple→pink→yellow)",
        AspectPalette.CIVIDIS: "Cividis (blue→yellow, CVD-optimized)",
        AspectPalette.TURBO: "Turbo (improved rainbow)",
    }
    return descriptions.get(palette, "Unknown palette")


# ============================================================================
# PLANET GLYPH PALETTES
# ============================================================================


class PlanetGlyphPalette(str, Enum):
    """Available color palettes for planet glyphs."""

    # Monochromatic (theme-based)
    DEFAULT = "default"  # Uses theme's planet glyph color

    # Astrological categorization
    ELEMENT = "element"  # Color by element (fire/earth/air/water)
    SIGN_RULER = "sign_ruler"  # Color by traditional rulership
    PLANET_TYPE = "planet_type"  # Traditional vs Modern vs Asteroids
    LUMINARIES = "luminaries"  # Sun/Moon special, others neutral

    # Vibrant categorical
    RAINBOW = "rainbow"  # Each planet gets a different color
    CHAKRA = "chakra"  # Based on chakra correspondences

    # Data science palettes
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    TURBO = "turbo"


# Planet categorizations for palette mapping
PLANET_ELEMENTS = {
    "Sun": "fire",
    "Moon": "water",
    "Mercury": "air",
    "Venus": "earth",
    "Mars": "fire",
    "Jupiter": "fire",
    "Saturn": "earth",
    "Uranus": "air",
    "Neptune": "water",
    "Pluto": "water",
}

PLANET_TYPES = {
    "Sun": "luminary",
    "Moon": "luminary",
    "Mercury": "traditional",
    "Venus": "traditional",
    "Mars": "traditional",
    "Jupiter": "traditional",
    "Saturn": "traditional",
    "Uranus": "modern",
    "Neptune": "modern",
    "Pluto": "modern",
    "Chiron": "centaur",
    "Ceres": "asteroid",
    "Pallas": "asteroid",
    "Juno": "asteroid",
    "Vesta": "asteroid",
    "True Node": "node",
    "Mean Node": "node",
    "South Node": "node",
    "Mean Apogee": "point",
    "True Apogee": "point",
}


def get_planet_glyph_color(
    planet_name: str,
    palette: PlanetGlyphPalette,
    theme_default_color: str = "#222222",
) -> str:
    """
    Get the color for a planet glyph based on palette.

    Args:
        planet_name: Name of the planet/object
        palette: The palette to use
        theme_default_color: Default color from theme (used for DEFAULT palette)

    Returns:
        Hex color string
    """
    if palette == PlanetGlyphPalette.DEFAULT:
        return theme_default_color

    elif palette == PlanetGlyphPalette.ELEMENT:
        # Color by element
        element_colors = {
            "fire": "#E74C3C",  # Red
            "earth": "#27AE60",  # Green
            "air": "#3498DB",  # Blue
            "water": "#9B59B6",  # Purple
        }
        element = PLANET_ELEMENTS.get(planet_name)
        return element_colors.get(element, theme_default_color)

    elif palette == PlanetGlyphPalette.SIGN_RULER:
        # Color by traditional rulership (simplified)
        ruler_colors = {
            "Sun": "#FFD700",  # Gold
            "Moon": "#C0C0C0",  # Silver
            "Mercury": "#FFA500",  # Orange
            "Venus": "#FF69B4",  # Pink
            "Mars": "#DC143C",  # Crimson
            "Jupiter": "#4169E1",  # Royal Blue
            "Saturn": "#2F4F4F",  # Dark Slate
            "Uranus": "#00CED1",  # Dark Turquoise
            "Neptune": "#7B68EE",  # Medium Slate Blue
            "Pluto": "#8B0000",  # Dark Red
        }
        return ruler_colors.get(planet_name, theme_default_color)

    elif palette == PlanetGlyphPalette.PLANET_TYPE:
        # Color by planet type
        type_colors = {
            "luminary": "#FFD700",  # Gold
            "traditional": "#4169E1",  # Royal Blue
            "modern": "#9370DB",  # Medium Purple
            "centaur": "#20B2AA",  # Light Sea Green
            "asteroid": "#CD853F",  # Peru
            "node": "#A9A9A9",  # Dark Grey
            "point": "#DDA0DD",  # Plum
        }
        planet_type = PLANET_TYPES.get(planet_name)
        return type_colors.get(planet_type, theme_default_color)

    elif palette == PlanetGlyphPalette.LUMINARIES:
        # Sun and Moon special, others neutral
        if planet_name == "Sun":
            return "#FFD700"  # Gold
        elif planet_name == "Moon":
            return "#C0C0C0"  # Silver
        else:
            return theme_default_color

    elif palette == PlanetGlyphPalette.RAINBOW:
        # Each planet gets a different rainbow color
        rainbow_colors = {
            "Sun": "#FF0000",  # Red
            "Moon": "#FF7F00",  # Orange
            "Mercury": "#FFFF00",  # Yellow
            "Venus": "#00FF00",  # Green
            "Mars": "#0000FF",  # Blue
            "Jupiter": "#4B0082",  # Indigo
            "Saturn": "#9400D3",  # Violet
            "Uranus": "#FF1493",  # Deep Pink
            "Neptune": "#00CED1",  # Dark Turquoise
            "Pluto": "#8B4513",  # Saddle Brown
        }
        return rainbow_colors.get(planet_name, theme_default_color)

    elif palette == PlanetGlyphPalette.CHAKRA:
        # Based on planetary chakra correspondences
        chakra_colors = {
            "Sun": "#FDB827",  # Solar Plexus - Yellow
            "Moon": "#C77DFF",  # Crown - Violet/White
            "Mercury": "#00BBF9",  # Throat - Blue
            "Venus": "#06D6A0",  # Heart - Green
            "Mars": "#E63946",  # Root - Red
            "Jupiter": "#9B59B6",  # Third Eye - Indigo
            "Saturn": "#495057",  # Root (grounding) - Dark
            "Uranus": "#00F5FF",  # Higher Throat - Cyan
            "Neptune": "#DA70D6",  # Crown - Orchid
            "Pluto": "#8B0000",  # Root (transformation) - Dark Red
        }
        return chakra_colors.get(planet_name, theme_default_color)

    elif palette == PlanetGlyphPalette.VIRIDIS:
        # Viridis colormap - 10 colors for major planets
        viridis_10 = [
            "#440154",
            "#482475",
            "#414487",
            "#2A788E",
            "#22A884",
            "#42BE71",
            "#7AD151",
            "#BBDF27",
            "#FDE724",
            "#FDE724",
        ]
        planet_order = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]
        if planet_name in planet_order:
            return viridis_10[planet_order.index(planet_name)]
        return theme_default_color

    elif palette == PlanetGlyphPalette.PLASMA:
        # Plasma colormap - 10 colors
        plasma_10 = [
            "#0D0887",
            "#5302A3",
            "#8B0AA5",
            "#B83289",
            "#DB5C68",
            "#F48849",
            "#FEBC2A",
            "#F0F921",
            "#F0F921",
            "#F0F921",
        ]
        planet_order = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]
        if planet_name in planet_order:
            return plasma_10[planet_order.index(planet_name)]
        return theme_default_color

    elif palette == PlanetGlyphPalette.INFERNO:
        # Inferno colormap - 10 colors
        inferno_10 = [
            "#000004",
            "#320A5A",
            "#781C6D",
            "#BB3754",
            "#ED6925",
            "#FB9A06",
            "#F7D03C",
            "#FCFFA4",
            "#FCFFA4",
            "#FCFFA4",
        ]
        planet_order = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]
        if planet_name in planet_order:
            return inferno_10[planet_order.index(planet_name)]
        return theme_default_color

    elif palette == PlanetGlyphPalette.TURBO:
        # Turbo colormap - 10 colors
        turbo_10 = [
            "#30123B",
            "#4662D7",
            "#1AE4B6",
            "#72FE5E",
            "#C8EF34",
            "#FABA39",
            "#F66B19",
            "#CA2A04",
            "#7A0403",
            "#7A0403",
        ]
        planet_order = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]
        if planet_name in planet_order:
            return turbo_10[planet_order.index(planet_name)]
        return theme_default_color

    else:
        return theme_default_color


def get_planet_glyph_palette_description(palette: PlanetGlyphPalette) -> str:
    """
    Get a human-readable description of a planet glyph palette.

    Args:
        palette: The palette to describe

    Returns:
        Description string
    """
    descriptions = {
        PlanetGlyphPalette.DEFAULT: "Default (theme color)",
        PlanetGlyphPalette.ELEMENT: "Element (fire/earth/air/water)",
        PlanetGlyphPalette.SIGN_RULER: "Rulership (traditional planetary colors)",
        PlanetGlyphPalette.PLANET_TYPE: "Planet Type (luminary/traditional/modern/etc.)",
        PlanetGlyphPalette.LUMINARIES: "Luminaries (Sun/Moon special, others neutral)",
        PlanetGlyphPalette.RAINBOW: "Rainbow (each planet different color)",
        PlanetGlyphPalette.CHAKRA: "Chakra (planetary-chakra correspondences)",
        PlanetGlyphPalette.VIRIDIS: "Viridis (perceptually uniform)",
        PlanetGlyphPalette.PLASMA: "Plasma (vibrant gradient)",
        PlanetGlyphPalette.INFERNO: "Inferno (dramatic gradient)",
        PlanetGlyphPalette.TURBO: "Turbo (improved rainbow)",
    }
    return descriptions.get(palette, "Unknown palette")


# ============================================================================
# COLOR UTILITIES FOR ADAPTIVE/CONTRAST-AWARE COLORING
# ============================================================================


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF00AA" or "FF00AA")

    Returns:
        RGB tuple (r, g, b) where each value is 0-255
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color string.

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        Hex color string (e.g., "#FF00AA")
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def get_luminance(hex_color: str) -> float:
    """
    Calculate the relative luminance of a color.

    Uses WCAG formula for luminance calculation.

    Args:
        hex_color: Hex color string

    Returns:
        Relative luminance (0.0 = black, 1.0 = white)
    """
    r, g, b = hex_to_rgb(hex_color)

    # Convert to 0-1 range
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # Apply gamma correction
    def gamma_correct(val):
        if val <= 0.03928:
            return val / 12.92
        else:
            return ((val + 0.055) / 1.055) ** 2.4

    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)

    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate the contrast ratio between two colors.

    Args:
        color1: First hex color
        color2: Second hex color

    Returns:
        Contrast ratio (1.0 = no contrast, 21.0 = maximum)
    """
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)

    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    return (lighter + 0.05) / (darker + 0.05)


def adjust_color_for_contrast(
    original_color: str,
    background_color: str,
    min_contrast: float = 4.5,
    max_iterations: int = 20,
) -> str:
    """
    Adjust a color to ensure minimum contrast against a background.

    This algorithm:
    1. Checks if original color already has sufficient contrast
    2. If not, determines if background is light or dark
    3. Adjusts the color's lightness/darkness in the opposite direction
    4. Iterates until minimum contrast is achieved

    Args:
        original_color: The color to adjust (hex)
        background_color: The background color (hex)
        min_contrast: Minimum WCAG contrast ratio (default 4.5 = WCAG AA)
        max_iterations: Maximum adjustment iterations

    Returns:
        Adjusted hex color that meets minimum contrast
    """
    # Check if original already has enough contrast
    if get_contrast_ratio(original_color, background_color) >= min_contrast:
        return original_color

    # Determine if background is light or dark
    bg_luminance = get_luminance(background_color)
    bg_is_light = bg_luminance > 0.5

    # Convert original color to HSL for easier lightness manipulation
    r, g, b = hex_to_rgb(original_color)
    h, lightness, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    # Adjust lightness iteratively
    step = 0.05
    for _ in range(max_iterations):
        # If background is light, make color darker; if dark, make color lighter
        if bg_is_light:
            lightness = max(0.0, lightness - step)
        else:
            lightness = min(1.0, lightness + step)

        # Convert back to RGB then hex
        r_adj, g_adj, b_adj = colorsys.hls_to_rgb(h, lightness, s)
        adjusted_hex = rgb_to_hex(int(r_adj * 255), int(g_adj * 255), int(b_adj * 255))

        # Check if we've achieved minimum contrast
        if get_contrast_ratio(adjusted_hex, background_color) >= min_contrast:
            return adjusted_hex

        # If we've hit the extreme (pure black or white), stop
        if lightness <= 0.0 or lightness >= 1.0:
            break

    # If we couldn't achieve the desired contrast, return pure black or white
    return "#000000" if bg_is_light else "#FFFFFF"


def get_sign_info_color(
    sign_index: int,
    zodiac_palette: ZodiacPalette,
    background_color: str,
    min_contrast: float = 4.5,
) -> str:
    """
    Get an adaptive color for sign glyph in planet info stack.

    This function:
    1. Gets the sign's zodiac wheel color from the palette
    2. Adjusts it for contrast against the background
    3. Returns a color that's readable while maintaining zodiac color story

    Args:
        sign_index: Zodiac sign index (0=Aries, 1=Taurus, etc.)
        zodiac_palette: The active zodiac palette
        background_color: Background color of the planet/info area
        min_contrast: Minimum WCAG contrast ratio

    Returns:
        Hex color for the sign glyph that contrasts with background
    """
    # Get the zodiac wheel colors
    zodiac_colors = get_palette_colors(zodiac_palette)
    sign_color = zodiac_colors[sign_index]

    # Adjust for contrast against background
    return adjust_color_for_contrast(sign_color, background_color, min_contrast)
