"""
Angle layers - ASC, MC, DSC, IC angle rendering.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
)
from stellium.visualization.core import (
    ANGLE_GLYPHS,
    ChartRenderer,
)

__all__ = ["AngleLayer", "OuterAngleLayer"]


class AngleLayer:
    """Renders the primary chart angles (ASC, MC, DSC, IC).

    For multiwheel charts, use wheel_index to specify which chart's angles to render.
    Typically only wheel_index=0 (innermost chart) has meaningful angles since
    transit/progressed charts use the natal houses.
    """

    def __init__(
        self,
        style_override: dict[str, Any] | None = None,
        wheel_index: int = 0,
        chart: "CalculatedChart | None" = None,
    ) -> None:
        """
        Args:
            style_override: Style overrides for this layer.
            wheel_index: Which chart's angles to render (0=innermost).
            chart: Optional explicit chart (for multiwheel).
        """
        self.style = style_override or {}
        self.wheel_index = wheel_index
        self._chart = chart

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render chart angles.

        Handles CalculatedChart, Comparison, MultiWheel, and MultiChart objects.
        Uses wheel_index to determine which chart's angles to render.
        """
        from stellium.core.chart_utils import is_comparison, is_multichart
        from stellium.core.multiwheel import MultiWheel

        style = renderer.style["angles"].copy()
        style.update(self.style)

        # Determine the actual chart to render
        if self._chart is not None:
            actual_chart = self._chart
        elif isinstance(chart, MultiWheel) or is_multichart(chart):
            if self.wheel_index < len(chart.charts):
                actual_chart = chart.charts[self.wheel_index]
            else:
                return
        elif is_comparison(chart):
            actual_chart = chart.chart1 if self.wheel_index == 0 else chart.chart2
        else:
            actual_chart = chart

        angles = actual_chart.get_angles()

        # Determine radii based on wheel_index
        chart_num = self.wheel_index + 1
        ring_outer_key = f"chart{chart_num}_ring_outer"
        ring_inner_key = f"chart{chart_num}_ring_inner"

        # Get radii with fallbacks for backward compatibility
        ring_outer = renderer.radii.get(
            ring_outer_key, renderer.radii.get("zodiac_ring_inner")
        )
        ring_inner = renderer.radii.get(
            ring_inner_key, renderer.radii.get("aspect_ring_inner")
        )

        for angle in angles:
            if angle.name not in ANGLE_GLYPHS:
                continue

            # Draw angle line (ASC/MC axis is the strongest)
            is_axis = angle.name in ("ASC", "MC")
            line_width = style["line_width"] if is_axis else style["line_width"] * 0.7
            line_color = (
                style["line_color"]
                if is_axis
                else renderer.style["houses"]["line_color"]
            )

            if angle.name in ("ASC", "MC", "DSC", "IC"):
                # Line spans from ring_outer to ring_inner
                x1, y1 = renderer.polar_to_cartesian(angle.longitude, ring_outer)
                x2, y2 = renderer.polar_to_cartesian(angle.longitude, ring_inner)
                dwg.add(
                    dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )

            # Draw angle glyph - positioned just inside the ring outer edge
            glyph_radius = ring_outer - 10
            x_glyph, y_glyph = renderer.polar_to_cartesian(
                angle.longitude, glyph_radius
            )

            # Apply directional offset based on angle name
            # Glyph goes one direction, degree text goes the opposite
            offset = 8  # pixels to nudge
            degree_offset = 10  # pixels to nudge degree text (opposite direction)

            x_degree, y_degree = x_glyph, y_glyph  # Start at same position

            if angle.name == "ASC":  # 9 o'clock - glyph up, degree down
                y_glyph -= offset
                y_degree += degree_offset
            elif angle.name == "MC":  # 12 o'clock - glyph right, degree left
                x_glyph += offset
                x_degree -= degree_offset
            elif angle.name == "DSC":  # 3 o'clock - glyph down, degree up
                y_glyph += offset
                y_degree -= degree_offset
            elif angle.name == "IC":  # 6 o'clock - glyph left, degree right
                x_glyph -= offset
                x_degree += degree_offset

            # Draw the angle label (ASC, MC, etc.)
            dwg.add(
                dwg.text(
                    ANGLE_GLYPHS[angle.name],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=style["glyph_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight="bold",
                )
            )

            # Draw the degree text (e.g., "15°32'")
            degree_in_sign = angle.longitude % 30
            deg_int = int(degree_in_sign)
            min_int = int((degree_in_sign % 1) * 60)
            degree_str = f"{deg_int}°{min_int:02d}'"

            # Use smaller font for degree text
            degree_font_size = style.get("degree_size", "10px")

            dwg.add(
                dwg.text(
                    degree_str,
                    insert=(x_degree, y_degree),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=degree_font_size,
                    fill=style["glyph_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )


class OuterAngleLayer:
    """Renders the outer wheel angles (for comparison charts).

    .. deprecated::
        Use AngleLayer(wheel_index=1) instead. This class renders outside
        the zodiac ring (legacy biwheel style), while the new multiwheel system
        renders all charts inside the zodiac ring.
    """

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        self.style = style_override or {}

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render outer wheel angles.

        For Comparison/MultiChart, uses chart2 (outer wheel) angles.
        Uses outer_wheel_angles styling from theme for visual distinction.
        """
        from stellium.core.chart_utils import is_comparison, is_multichart

        # Get outer wheel angle styling (lighter/thinner than inner)
        base_style = renderer.style.get("outer_wheel_angles", renderer.style["angles"])
        style = base_style.copy()
        style.update(self.style)

        # Handle Comparison/MultiChart - use chart2 angles (outer wheel)
        if is_comparison(chart):
            actual_chart = chart.chart2
        elif is_multichart(chart) and chart.chart_count >= 2:
            actual_chart = chart.charts[1]  # outer wheel
        else:
            # Shouldn't be called for single charts, but handle gracefully
            return

        angles = actual_chart.get_angles()

        for angle in angles:
            if angle.name not in ANGLE_GLYPHS:
                continue

            # Draw angle line extending OUTWARD from zodiac ring
            is_axis = angle.name in ("ASC", "MC")
            line_width = style["line_width"] if is_axis else style["line_width"] * 0.7
            line_color = (
                style["line_color"]
                if is_axis
                else renderer.style["houses"]["line_color"]
            )

            if angle.name in ("ASC", "MC", "DSC", "IC"):
                # Start at zodiac ring outer, extend outward
                x1, y1 = renderer.polar_to_cartesian(
                    angle.longitude, renderer.radii["zodiac_ring_outer"]
                )
                # Extend to just past outer planets
                # Use outer_cusp_end as a good stopping point
                outer_radius = renderer.radii.get(
                    "outer_cusp_end", renderer.radii["zodiac_ring_outer"] + 35
                )
                x2, y2 = renderer.polar_to_cartesian(angle.longitude, outer_radius)
                dwg.add(
                    dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )

            # Draw angle glyph - positioned outside zodiac ring
            # Position near the outer house numbers
            glyph_radius = (
                renderer.radii.get(
                    "outer_house_number", renderer.radii["zodiac_ring_outer"] + 20
                )
                - 5
            )  # Slightly inside house numbers
            x_glyph, y_glyph = renderer.polar_to_cartesian(
                angle.longitude, glyph_radius
            )

            # Apply directional offset based on angle name
            offset = 6  # Smaller offset than inner angles
            if angle.name == "ASC":
                y_glyph -= offset
            elif angle.name == "MC":
                x_glyph += offset
            elif angle.name == "DSC":
                y_glyph += offset
            elif angle.name == "IC":
                x_glyph -= offset

            dwg.add(
                dwg.text(
                    ANGLE_GLYPHS[angle.name],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=style["glyph_color"],
                    font_family=renderer.style["font_family_text"],
                    font_weight="bold",
                )
            )
