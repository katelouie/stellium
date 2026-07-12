"""
Angle layers - ASC, MC, DSC, IC angle rendering.
"""

import math
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

        cx = renderer.x_offset + renderer.center
        cy = renderer.y_offset + renderer.center

        # Inlaid angle-label styling (falls back to the theme's angle colours).
        abbr_color = style.get("glyph_color", "#2b2b2b")
        degree_color = style.get("degree_color", style.get("line_color", "#555555"))
        label_size = style.get("label_size", style.get("degree_size", "11px"))
        half_gap = style.get("label_gap", 22)  # half the notch width along the line
        label_inset = style.get("label_inset", 16)  # how far into the zodiac band
        # Optical centering: nudge the label along its own up/down axis (perpendicular
        # to the line) so the axis bisects the text vertically. Positive = "down" in
        # the text's own frame (away from the reading side).
        label_perp = style.get("label_perp", 2.5)
        font_family = renderer.style["font_family_text"]

        # Extend the axis line out to the zodiac ring's outer edge (single wheel).
        zodiac_outer = renderer.radii.get("zodiac_ring_outer")
        line_outer = (
            zodiac_outer if (self.wheel_index == 0 and zodiac_outer) else ring_outer
        )

        for angle in angles:
            if angle.name not in ANGLE_GLYPHS:
                continue

            is_axis = angle.name in ("ASC", "MC")
            line_width = style["line_width"] if is_axis else style["line_width"] * 0.7
            line_color = (
                style["line_color"]
                if is_axis
                else renderer.style["houses"]["line_color"]
            )

            if angle.name not in ("ASC", "MC", "DSC", "IC"):
                # Non-axis points (e.g. Vertex): a simple centred glyph, no line.
                gx, gy = renderer.polar_to_cartesian(angle.longitude, ring_outer - 10)
                dwg.add(
                    dwg.text(
                        ANGLE_GLYPHS[angle.name],
                        insert=(gx, gy),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=style["glyph_size"],
                        fill=style["glyph_color"],
                        font_family=font_family,
                        font_weight="bold",
                    )
                )
                continue

            # The inlaid label sits in the zodiac band, near its inner edge.
            label_radius = ring_outer + label_inset
            lx, ly = renderer.polar_to_cartesian(angle.longitude, label_radius)

            # Axis line drawn in two pieces, leaving a notch around the label.
            if line_outer > label_radius + half_gap:
                xo1, yo1 = renderer.polar_to_cartesian(angle.longitude, line_outer)
                xo2, yo2 = renderer.polar_to_cartesian(
                    angle.longitude, label_radius + half_gap
                )
                dwg.add(
                    dwg.line(
                        start=(xo1, yo1),
                        end=(xo2, yo2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )
            if label_radius - half_gap > ring_inner:
                xi1, yi1 = renderer.polar_to_cartesian(
                    angle.longitude, label_radius - half_gap
                )
                xi2, yi2 = renderer.polar_to_cartesian(angle.longitude, ring_inner)
                dwg.add(
                    dwg.line(
                        start=(xi1, yi1),
                        end=(xi2, yi2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )

            # Rotate the label along the axis, flipped to stay upright/readable.
            rot = math.degrees(math.atan2(ly - cy, lx - cx))
            if rot > 90 or rot < -90:
                rot += 180

            deg_int = int(angle.longitude % 30)
            grp = dwg.g(transform=f"rotate({rot:.2f},{lx:.2f},{ly:.2f})")
            txt = dwg.text(
                "",
                insert=(lx, ly + label_perp),
                text_anchor="middle",
                dominant_baseline="central",
                font_family=font_family,
                font_size=label_size,
            )
            txt.add(
                dwg.tspan(
                    f"{ANGLE_GLYPHS[angle.name]} ",
                    **{
                        "font-weight": "bold",
                        "fill": abbr_color,
                        "letter-spacing": "0.5",
                    },
                )
            )
            txt.add(
                dwg.tspan(
                    f"{deg_int}°",
                    **{"font-weight": "normal", "fill": degree_color},
                )
            )
            grp.add(txt)
            dwg.add(grp)


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
