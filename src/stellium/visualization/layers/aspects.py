"""
Aspect layers - aspect lines, patterns, and multiwheel aspects.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
)
from stellium.visualization.core import (
    ChartRenderer,
)
from stellium.visualization.palettes import (
    AspectPalette,
    adjust_color_for_contrast,
    get_aspect_palette_colors,
)

__all__ = ["AspectLayer", "MultiWheelAspectLayer", "ChartShapeLayer"]


class AspectLayer:
    """Renders the aspect lines within the chart."""

    def __init__(self, style_override: dict[str, Any] | None = None):
        self.style = style_override or {}

    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        style = renderer.style["aspects"].copy()
        style.update(self.style)

        # Use renderer's aspect palette if available
        if renderer.aspect_palette:
            aspect_palette = AspectPalette(renderer.aspect_palette)
            aspect_colors = get_aspect_palette_colors(aspect_palette)

            # Update style with palette colors, PRESERVING line width and dash from registry
            for aspect_name, color in aspect_colors.items():
                if aspect_name not in style:
                    # If not in style (shouldn't happen), create with defaults
                    style[aspect_name] = {"color": color, "width": 1.5, "dash": "1,0"}
                elif isinstance(style[aspect_name], dict):
                    # Preserve existing width and dash, only update color
                    style[aspect_name]["color"] = color
                else:
                    # Fallback case
                    style[aspect_name] = {"color": color, "width": 1.5, "dash": "1,0"}

        radius = renderer.radii["aspect_ring_inner"]

        dwg.add(
            dwg.circle(
                center=(
                    renderer.center + renderer.x_offset,
                    renderer.center + renderer.y_offset,
                ),
                r=radius,
                fill=style["background_color"],
                stroke=style["line_color"],
            )
        )

        for aspect in chart.aspects:
            # Get style, falling back to default
            aspect_style = style.get(aspect.aspect_name, style["default"])

            # Get positions on the inner aspect ring
            x1, y1 = renderer.polar_to_cartesian(aspect.object1.longitude, radius)
            x2, y2 = renderer.polar_to_cartesian(aspect.object2.longitude, radius)

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=aspect_style["color"],
                    stroke_width=aspect_style["width"],
                    stroke_dasharray=aspect_style["dash"],
                    opacity=0.6,  # Make aspect lines semi-transparent to reduce visual clutter
                )
            )


class MultiWheelAspectLayer:
    """
    Renders cross-chart aspect lines for MultiWheel charts.

    Only used for 2-chart multiwheels (biwheels), where showing aspects between
    the two charts is useful and not too cluttered. For 3-4 chart multiwheels,
    aspect lines are omitted due to visual complexity.
    """

    def __init__(self, style_override: dict[str, Any] | None = None):
        self.style = style_override or {}

    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: Any,  # MultiWheel or MultiChart
    ) -> None:
        from stellium.core.chart_utils import is_multichart
        from stellium.core.multiwheel import MultiWheel

        # Handle both MultiWheel and MultiChart
        if not isinstance(chart, MultiWheel) and not is_multichart(chart):
            return

        # Only draw aspects for 2-chart multiwheels
        if chart.chart_count != 2:
            return

        # Get cross-aspects between chart 0 and chart 1
        cross_aspects = chart.cross_aspects.get((0, 1), ())
        if not cross_aspects:
            return

        style = renderer.style["aspects"].copy()
        style.update(self.style)

        # Use renderer's aspect palette if available
        if renderer.aspect_palette:
            aspect_palette = AspectPalette(renderer.aspect_palette)
            aspect_colors = get_aspect_palette_colors(aspect_palette)

            for aspect_name, color in aspect_colors.items():
                if aspect_name not in style:
                    style[aspect_name] = {"color": color, "width": 1.5, "dash": "1,0"}
                elif isinstance(style[aspect_name], dict):
                    style[aspect_name]["color"] = color
                else:
                    style[aspect_name] = {"color": color, "width": 1.5, "dash": "1,0"}

        radius = renderer.radii.get(
            "aspect_ring_inner", renderer.radii.get("chart1_ring_inner", 0.14)
        )

        # Draw central aspect circle
        dwg.add(
            dwg.circle(
                center=(
                    renderer.center + renderer.x_offset,
                    renderer.center + renderer.y_offset,
                ),
                r=radius,
                fill=style["background_color"],
                stroke=style["line_color"],
            )
        )

        # Draw aspect lines
        for aspect in cross_aspects:
            aspect_style = style.get(aspect.aspect_name, style["default"])

            # Get positions on the inner aspect ring
            x1, y1 = renderer.polar_to_cartesian(aspect.object1.longitude, radius)
            x2, y2 = renderer.polar_to_cartesian(aspect.object2.longitude, radius)

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=aspect_style["color"],
                    stroke_width=aspect_style["width"],
                    stroke_dasharray=aspect_style["dash"],
                    opacity=0.6,
                )
            )


class ChartShapeLayer:
    """
    Renders chart shape information in a corner.

    Displays the overall pattern/distribution of planets (Bundle, Bowl, Bucket, etc.).
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "text_size": "11px",
        "line_height": 14,
        "font_weight": "normal",
        "title_weight": "bold",
    }

    def __init__(
        self,
        position: str = "bottom-right",
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize chart shape layer.

        Args:
            position: Where to place the info.
                Options: "top-left", "top-right", "bottom-left", "bottom-right"
            style_override: Optional style overrides
        """
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position: {position}. Must be one of {valid_positions}"
            )

        self.position = position
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """Render chart shape information."""
        from stellium.utils.chart_shape import (
            detect_chart_shape,
        )

        # Detect shape
        shape, metadata = detect_chart_shape(chart)

        # Build lines
        lines = []
        lines.append("Chart Shape:")
        lines.append(shape)

        # Add key metadata
        if shape == "Bundle" and "leading_planet" in metadata:
            lines.append(f"Led by {metadata['leading_planet']}")
        elif shape == "Bowl" and "leading_planet" in metadata:
            lines.append(f"Led by {metadata['leading_planet']}")
        elif shape == "Bucket" and "handle" in metadata:
            lines.append(f"Handle: {metadata['handle']}")
        elif shape == "Locomotive" and "leading_planet" in metadata:
            lines.append(f"Led by {metadata['leading_planet']}")

        # Calculate position
        x, y = self._get_position_coordinates(renderer, len(lines))

        # Determine text anchor
        if "right" in self.position:
            text_anchor = "end"
        else:
            text_anchor = "start"

        # Get theme-aware text color from planets info_color
        theme_text_color = renderer.style.get("planets", {}).get(
            "info_color", self.style["text_color"]
        )
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            theme_text_color, background_color, min_contrast=4.5
        )

        # Render each line
        for i, line_data in enumerate(lines):
            # Unpack line text and optional color
            if isinstance(line_data, tuple):
                line_text, line_color = line_data
            else:
                # Single string (backwards compatibility)
                line_text, line_color = line_data, None

            line_y = y + (i * self.style["line_height"])
            font_weight = (
                self.style["title_weight"] if i == 0 else self.style["font_weight"]
            )

            # Use line-specific color if available, otherwise default text color
            fill_color = line_color if line_color else text_color

            dwg.add(
                dwg.text(
                    line_text,
                    insert=(x, line_y),
                    text_anchor=text_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=fill_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=font_weight,
                )
            )

    def _get_position_coordinates(
        self, renderer: ChartRenderer, num_lines: int
    ) -> tuple[float, float]:
        """Calculate position coordinates."""
        # Match the chart's own padding
        margin = renderer.size * 0.03
        total_height = num_lines * self.style["line_height"]

        # Get offsets for extended canvas positioning
        x_offset = getattr(renderer, "x_offset", 0)
        y_offset = getattr(renderer, "y_offset", 0)

        if self.position == "top-left":
            return (x_offset + margin, y_offset + margin)
        elif self.position == "top-right":
            return (x_offset + renderer.size - margin, y_offset + margin)
        elif self.position == "bottom-left":
            return (x_offset + margin, y_offset + renderer.size - margin - total_height)
        elif self.position == "bottom-right":
            return (
                x_offset + renderer.size - margin,
                y_offset + renderer.size - margin - total_height,
            )
        else:
            return (x_offset + margin, y_offset + margin)
