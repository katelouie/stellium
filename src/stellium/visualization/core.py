"""
Core Chart Drawing Engine (stellium.visualization.core)

This module provides the core, refactored drawing system.
It is based on a "Layer" strategy pattern.

- ChartRenderer: The main "canvas" and coordinate system.
- IRenderLayer: The protocol (interface) that all drawable layers must follow.
"""

import math
from typing import Any, Protocol

import svgwrite

from stellium.core.models import CalculatedChart
from stellium.core.registry import (
    ASPECT_REGISTRY,
    get_aspect_by_alias,
    get_aspect_info,
    get_object_info,
)

# Legacy glyph dictionaries - kept for backwards compatibility
# Prefer using the registry via get_glyph() helper function
PLANET_GLYPHS = {
    # === Traditional Planets (The Septenary) ===
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    # === Modern Planets ===
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    # === Chart Points & Nodes ===
    "Earth": "♁",
    "True Node": "☊",  # Also called the North Node
    "South Node": "☋",
    "Black Moon Lilith": "⚸",
    "Part of Fortune": "⊗",  # A common glyph, U+2297
    # === Asteroids (The "Big Four") ===
    "Ceres": "⚳",
    "Pallas": "⚴",
    "Juno": "⚵",
    "Vesta": "⚶",
    # === Centaurs ===
    "Chiron": "⚷",
    "Pholus": "⬰",  # (U+2B30) This is the correct glyph
    # === Uranian / Witte School Planets ===
    # These are very niche, but have standard glyphs
    "Cupido": "Cup",  # (U+2BD3)
    "Hades": "Had",  # (U+2BD4)
    "Zeus": "Zeu",  # (U+2BD5)
    "Kronos": "Kro",  # (U+2BD6)
    "Apollon": "Apo",  # (U+2BD7)
    "Admetos": "Adm",  # (U+2BD8)
    "Vulcanus": "Vul",  # (U+2BD9)
    "Poseidon": "Pos",  # (U+2BDA)
}

ZODIAC_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

ANGLE_GLYPHS = {
    "ASC": "Asc",
    "MC": "MC",
    "DSC": "Dsc",
    "IC": "IC",
    "Vertex": "Vx",
}


def get_glyph(object_name: str) -> dict[str, str]:
    """
    Get the glyph for a celestial object, with registry lookup and fallback.

    Args:
        object_name: Name of the object (e.g., "Sun", "Mean Apogee", "ASC")

    Returns:
        Dictionary with:
        - "type": "unicode" or "svg"
        - "value": glyph string (unicode) or SVG content string (for inline embedding)
    """
    from pathlib import Path

    # Try registry first
    obj_info = get_object_info(object_name)
    if obj_info:
        # Check if there's an SVG path
        if obj_info.glyph_svg_path:
            # Resolve to absolute path for SVG reading
            # The path is relative to project root
            svg_path = Path(obj_info.glyph_svg_path)
            if not svg_path.is_absolute():
                # Go up from visualization/core.py to project root
                # visualization/ -> stellium/ -> src/ -> project_root/
                project_root = Path(__file__).parent.parent.parent.parent
                svg_path = project_root / obj_info.glyph_svg_path
            if svg_path.exists():
                # Read SVG content for inline embedding
                svg_content = svg_path.read_text()
                return {"type": "svg", "value": svg_content}
            # Fall back to unicode glyph if SVG doesn't exist
            return {"type": "unicode", "value": obj_info.glyph}
        return {"type": "unicode", "value": obj_info.glyph}

    # Fall back to legacy dictionaries (always unicode)
    if object_name in PLANET_GLYPHS:
        return {"type": "unicode", "value": PLANET_GLYPHS[object_name]}
    if object_name in ANGLE_GLYPHS:
        return {"type": "unicode", "value": ANGLE_GLYPHS[object_name]}

    # Final fallback: use first 2-3 characters
    return {"type": "unicode", "value": object_name[:3]}


def embed_svg_glyph(
    dwg: svgwrite.Drawing,
    svg_content: str,
    x: float,
    y: float,
    size: float,
    fill_color: str | None = None,
) -> None:
    """
    Embed an SVG glyph inline as a nested SVG element.

    This function parses SVG content and embeds it directly into the drawing
    as a nested <svg> element with proper positioning and scaling. This approach
    works across all browsers and SVG viewers, unlike external image references.

    Args:
        dwg: The svgwrite Drawing to add the element to
        svg_content: The raw SVG content string (from get_glyph())
        x: Center x coordinate for the glyph
        y: Center y coordinate for the glyph
        size: Desired size (width and height) in pixels
        fill_color: Optional color to override stroke/fill (for theming)
    """
    import re

    from svgwrite.path import Path as SvgPath

    # Extract viewBox from the SVG content using regex
    viewbox_match = re.search(r'viewBox="([^"]+)"', svg_content)
    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 16 16"

    # Calculate position (center the glyph)
    svg_x = x - size / 2
    svg_y = y - size / 2

    # Create nested SVG element with proper positioning
    nested_svg = dwg.svg(
        insert=(svg_x, svg_y),
        size=(size, size),
        viewBox=viewbox,
    )

    # Extract path data using regex (handles namespaced SVGs)
    # Find all path elements
    path_elements = re.findall(r"<path[^>]+/>", svg_content)

    for path_elem in path_elements:
        # Extract d attribute
        d_match = re.search(r'd="([^"]+)"', path_elem)
        path_d = d_match.group(1) if d_match else ""

        # Extract style attribute
        style_match = re.search(r'style="([^"]+)"', path_elem)
        style = style_match.group(1) if style_match else ""

        if not path_d:
            continue

        # Parse style into attributes
        stroke = fill_color or "#000"
        stroke_width = 0.6
        fill = "none"

        if "stroke-width:" in style:
            sw_match = re.search(r"stroke-width:([^;]+)", style)
            if sw_match:
                try:
                    stroke_width = float(sw_match.group(1).strip())
                except ValueError:
                    pass

        if "fill:" in style:
            fill_match = re.search(r"fill:([^;]+)", style)
            if fill_match:
                fill = fill_match.group(1).strip()

        # Create the path using svgwrite with debug mode disabled
        # to bypass the strict path validation
        path = SvgPath(
            d=path_d,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            debug=False,
        )
        path["stroke-linecap"] = "round"
        path["stroke-linejoin"] = "round"

        nested_svg.add(path)

    dwg.add(nested_svg)


def get_display_name(object_name: str) -> str:
    """
    Get the display name for a celestial object.

    Args:
        object_name: Technical name (e.g., "Mean Apogee")

    Returns:
        Display name (e.g., "Black Moon Lilith") or original name if not in registry
    """
    obj_info = get_object_info(object_name)
    if obj_info:
        return obj_info.display_name
    return object_name


def get_aspect_glyph(aspect_name: str) -> str:
    """
    Get the glyph for an astrological aspect.

    Args:
        aspect_name: Aspect name (e.g., "Conjunction", "Trine", "Conjunct")

    Returns:
        Unicode glyph string or abbreviation if not found
    """
    # Try exact name first
    aspect_info = get_aspect_info(aspect_name)
    if aspect_info and aspect_info.glyph:
        return aspect_info.glyph

    # Try as alias (e.g., "Conjunct" → "Conjunction")
    aspect_info = get_aspect_by_alias(aspect_name)
    if aspect_info and aspect_info.glyph:
        return aspect_info.glyph

    # Fallback: use first 3 characters
    return aspect_name[:3]


class ChartRenderer:
    """
    The core chart drawing canvas and coordinate system.

    This class holds the SVG drawing object and provides the geometric
    utilities for layers to draw themselves. It acts as the "Context"
    in the strategy pattern.
    """

    def __init__(
        self,
        size: int = 600,
        rotation: float = 0.0,
        theme: str | None = None,
        style_config: dict[str, Any] | None = None,
        zodiac_palette: str | None = None,
        aspect_palette: str | None = None,
        planet_glyph_palette: str | None = None,
        color_sign_info: bool = False,
    ) -> None:
        """
        Initialize the chart renderer.

        Args:
            size: The canvas size in pixels.
            rotation: The astrological longitude (in degrees) to fix
                      at the 9 o'clock position. Defaults to 0 (Aries).
            theme: Optional theme name (e.g., "dark", "midnight", "neon").
                   If provided, loads theme styling. Can still be overridden by style_config.
            style_config: Optional style overrides.
            zodiac_palette: Optional zodiac palette override (e.g., "viridis", "rainbow").
            aspect_palette: Optional aspect palette override (e.g., "plasma", "blues").
            planet_glyph_palette: Optional planet glyph palette override (e.g., "element", "chakra").
            color_sign_info: If True, color sign glyphs in info stack based on zodiac palette.
        """
        self.size = size
        self.center = size // 2
        self.rotation = rotation

        # Initialize offsets (set by extended canvas mode in drawing.py)
        self.x_offset = 0
        self.y_offset = 0

        # Store palette configurations
        self.zodiac_palette = zodiac_palette
        self.aspect_palette = aspect_palette
        self.planet_glyph_palette = planet_glyph_palette
        self.color_sign_info = color_sign_info

        # Legacy fallback radii for old drawing.py system
        # NOTE: In new config-driven system, these get overwritten by LayoutEngine
        # which uses ChartWheelConfig.single_radii or .biwheel_radii
        self.radii = {
            "outer_border": size * 0.48,
            "zodiac_ring_outer": size * 0.47,
            "zodiac_glyph": size * 0.42,
            "zodiac_ring_inner": size * 0.37,
            "planet_ring": size * 0.32,
            "house_number_ring": size * 0.20,
            "aspect_ring_inner": size * 0.18,
            # Obsolete synastry keys (unused in new system)
            "synastry_planet_ring_inner": size * 0.25,
            "synastry_planet_ring_outer": size * 0.35,
        }

        # Load theme if specified, otherwise use default
        if theme:
            from .themes import (
                ChartTheme,
                get_theme_default_aspect_palette,
                get_theme_default_palette,
                get_theme_default_planet_palette,
                get_theme_style,
            )

            theme_enum = ChartTheme(theme) if isinstance(theme, str) else theme
            self.style = get_theme_style(theme_enum)

            # Set default palettes from theme if not explicitly provided
            if self.zodiac_palette is None:
                # None means "use theme's colorful default"
                self.zodiac_palette = get_theme_default_palette(theme_enum).value
            elif self.zodiac_palette == "monochrome":
                # Keep as "monochrome" - ZodiacLayer will use theme's ring_color
                pass
            # Otherwise use the specific palette name provided

            if self.aspect_palette is None:
                self.aspect_palette = get_theme_default_aspect_palette(theme_enum).value
            if self.planet_glyph_palette is None:
                self.planet_glyph_palette = get_theme_default_planet_palette(
                    theme_enum
                ).value
        else:
            self.style = self._get_default_style()

            # Set default palettes if not explicitly provided
            if self.zodiac_palette is None:
                self.zodiac_palette = "grey"
            elif self.zodiac_palette == "monochrome":
                # For no-theme case, monochrome uses grey
                self.zodiac_palette = "grey"

            if self.aspect_palette is None:
                self.aspect_palette = "classic"
            if self.planet_glyph_palette is None:
                self.planet_glyph_palette = "default"

        # Apply style overrides
        if style_config:
            # Deep merge dictionaries
            for key, value in style_config.items():
                if isinstance(value, dict):
                    self.style[key].update(value)
                else:
                    self.style[key] = value

    def _get_default_style(self) -> dict[str, Any]:
        """Provides the base styling configuration."""
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
                "line_color": "#888888",  # Lighter than inner angles
                "line_width": 1.8,  # Thinner than inner angles
                "glyph_color": "#666666",  # Lighter glyph
                "glyph_size": "11px",  # Slightly smaller
            },
            "planets": {
                "glyph_color": "#222222",
                "glyph_size": "32px",
                "info_color": "#444444",
                "info_size": "10px",
                "retro_color": "#E74C3C",
            },
            "aspects": {
                **{
                    aspect_info.name: {
                        "color": aspect_info.color,
                        "width": aspect_info.metadata.get("line_width", 1.5),
                        "dash": aspect_info.metadata.get("dash_pattern", "1,0"),
                    }
                    for aspect_info in ASPECT_REGISTRY.values()
                    if aspect_info.category
                    in ["Major", "Minor"]  # Only visualize major/minor
                },
                "default": {"color": "#BDC3C7", "width": 0.5, "dash": "2,2"},
                "line_color": "#BBBBBB",
                "background_color": "#FFFFFF",
            },
        }

    def astrological_to_svg_angle(self, astro_deg: float) -> float:
        """
        Converts astrological degrees (0° = Aries) to SVG degrees
        (0° = 3 o'clock), appling the chart's rotation.

        Our system: 0° Aries is at 9 o'clock (180° SVG).
        Rotation is COUNTER-CLOCKWISE.
        """
        # Get the degree relative to the rotation point
        # if Sun is 15 Leo (135) and Asc (rotation) is 15 Cancer (105)
        # then relative degree is 30
        relative_deg = (astro_deg - self.rotation + 360) % 360

        # Apply the standard formula to the relative degree
        # (180 - relative degree) places 0 deg at 9 o clock (180)
        # and makes the chart rotate counter-clockwise
        svg_angle = (180 + relative_deg - 360) % 360

        return svg_angle

    def polar_to_cartesian(
        self, astro_deg: float, radius: float
    ) -> tuple[float, float]:
        """
        Converts an astrological degree (0 degrees Aries) and radius to an (x,y) coordinate.
        Accounts for extended canvas offsets when present.
        """
        svg_angle_rad = math.radians(self.astrological_to_svg_angle(astro_deg))

        # SVG Y is inverted (positive is down)
        # Add offsets for extended canvas positioning
        x = self.x_offset + self.center + radius * math.cos(svg_angle_rad)
        y = self.y_offset + self.center - radius * math.sin(svg_angle_rad)

        return x, y

    # NOTE: create_svg_drawing() was removed as it was unused legacy code.
    # All SVG rendering now goes through ChartComposer and the layer system.
    # Background, borders, and all chart elements are rendered as layers.


class IRenderLayer(Protocol):
    """
    Protocol (interface) for all drawable chart layers.

    Each layer is a self-contained drawing strategy.
    """

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """
        The main drawing method for the layer.

        Args:
            renderer: ChartRenderer instance, used to access coordinate methods
            (.polar_to_cartesian) and style/radius definitions.
            dwg: The svgwrite.Drawing object to add elements to.
            chart: The full CalculatedChart data object.
        """
        ...
