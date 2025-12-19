"""
House cusp layers - inner and outer house cusp rendering.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    HouseCusps,
)
from stellium.visualization.core import (
    ChartRenderer,
)

__all__ = ["HouseCuspLayer", "OuterHouseCuspLayer"]


class HouseCuspLayer:
    """
    Renders a *single* set of house cusps and numbers.

    To draw multiple systems, add multiple layers.

    For multiwheel charts, use wheel_index to specify which chart ring to render:
    - wheel_index=0: Chart 1 (innermost)
    - wheel_index=1: Chart 2
    - wheel_index=2: Chart 3
    - wheel_index=3: Chart 4 (outermost, just inside zodiac)

    The layer will look up radii from the renderer using keys like:
    - chart{N}_ring_outer, chart{N}_ring_inner (ring bounds)
    - chart{N}_house_number (number placement)

    And fill colors from theme:
    - chart{N}_fill_1, chart{N}_fill_2 (alternating fills)
    """

    def __init__(
        self,
        house_system_name: str,
        style_override: dict[str, Any] | None = None,
        wheel_index: int = 0,
        chart: "CalculatedChart | None" = None,
    ) -> None:
        """
        Args:
            house_system_name: The name of the system to pull from the CalculatedChart (eg "Placidus")
            style_override: Optional style changes for this specific layer (eg. {"line_color": "red})
            wheel_index: Which chart ring to render (0=innermost, used for multiwheel)
            chart: Optional chart to render (for multiwheel, each layer gets its own chart)
        """
        self.system_name = house_system_name
        self.style = style_override or {}
        self.wheel_index = wheel_index
        self._chart = (
            chart  # Explicit chart for multiwheel; if None, derives from passed chart
        )

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render house cusps and house numbers.

        Handles CalculatedChart, Comparison, MultiWheel, and MultiChart objects.
        Uses wheel_index to determine which chart ring to render and which radii to use.
        """
        from stellium.core.chart_utils import is_comparison, is_multichart
        from stellium.core.multiwheel import MultiWheel

        style = renderer.style["houses"].copy()
        style.update(self.style)

        # Determine the actual chart to render
        if self._chart is not None:
            # Explicit chart provided (multiwheel mode)
            actual_chart = self._chart
        elif isinstance(chart, MultiWheel) or is_multichart(chart):
            # MultiWheel/MultiChart: use chart at wheel_index
            if self.wheel_index < len(chart.charts):
                actual_chart = chart.charts[self.wheel_index]
            else:
                return  # wheel_index out of range
        elif is_comparison(chart):
            # Legacy Comparison: wheel_index 0 = chart1 (inner), 1 = chart2 (outer)
            actual_chart = chart.chart1 if self.wheel_index == 0 else chart.chart2
        else:
            # Single chart: use as-is
            actual_chart = chart

        try:
            house_cusps: HouseCusps = actual_chart.get_houses(self.system_name)
        except (ValueError, KeyError):
            print(
                f"Warning: House system '{self.system_name}' not found in chart data."
            )
            return

        # Determine radii based on wheel_index
        # For multiwheel: use chart{N}_ring_outer, chart{N}_ring_inner, chart{N}_house_number
        # For single/legacy: fall back to zodiac_ring_inner, aspect_ring_inner, house_number_ring
        chart_num = self.wheel_index + 1  # wheel_index 0 -> chart1, etc.
        ring_outer_key = f"chart{chart_num}_ring_outer"
        ring_inner_key = f"chart{chart_num}_ring_inner"
        house_number_key = f"chart{chart_num}_house_number"

        # Get radii with fallbacks for backward compatibility
        ring_outer = renderer.radii.get(
            ring_outer_key, renderer.radii.get("zodiac_ring_inner")
        )
        ring_inner = renderer.radii.get(
            ring_inner_key, renderer.radii.get("aspect_ring_inner")
        )
        house_number_radius = renderer.radii.get(
            house_number_key, renderer.radii.get("house_number_ring")
        )

        # Determine fill colors based on wheel_index
        fill_1_key = f"chart{chart_num}_fill_1"
        fill_2_key = f"chart{chart_num}_fill_2"
        fill_color_1 = style.get(fill_1_key, style.get("fill_color_1", "#F5F5F5"))
        fill_color_2 = style.get(fill_2_key, style.get("fill_color_2", "#FFFFFF"))

        # Draw alternating fill wedges FIRST (if enabled)
        if style.get("fill_alternate", False):
            for i in range(12):
                cusp_deg = house_cusps.cusps[i]
                next_cusp_deg = house_cusps.cusps[(i + 1) % 12]

                # Handle 0-degree wrap
                if next_cusp_deg < cusp_deg:
                    next_cusp_deg += 360

                # Alternate between two fill colors
                fill_color = fill_color_1 if i % 2 == 0 else fill_color_2

                # Create a pie wedge path from ring_inner to ring_outer
                x_start, y_start = renderer.polar_to_cartesian(cusp_deg, ring_inner)
                x_end, y_end = renderer.polar_to_cartesian(next_cusp_deg, ring_inner)
                x_outer_start, y_outer_start = renderer.polar_to_cartesian(
                    cusp_deg, ring_outer
                )
                x_outer_end, y_outer_end = renderer.polar_to_cartesian(
                    next_cusp_deg, ring_outer
                )

                # Determine if we need the large arc flag (for arcs > 180 degrees)
                angle_diff = next_cusp_deg - cusp_deg
                large_arc = 1 if angle_diff > 180 else 0

                # Create path: outer arc + line + inner arc + line back
                path_data = f"M {x_outer_start},{y_outer_start} "
                path_data += f"A {ring_outer},{ring_outer} 0 {large_arc},0 {x_outer_end},{y_outer_end} "
                path_data += f"L {x_end},{y_end} "
                path_data += (
                    f"A {ring_inner},{ring_inner} 0 {large_arc},1 {x_start},{y_start} "
                )
                path_data += "Z"

                dwg.add(
                    dwg.path(
                        d=path_data,
                        fill=fill_color,
                        stroke="none",
                    )
                )

        for i, cusp_deg in enumerate(house_cusps.cusps):
            house_num = i + 1

            # Draw cusp line from ring_outer to ring_inner
            x1, y1 = renderer.polar_to_cartesian(cusp_deg, ring_outer)
            x2, y2 = renderer.polar_to_cartesian(cusp_deg, ring_inner)

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=style["line_color"],
                    stroke_width=style["line_width"],
                    stroke_dasharray=style.get("line_dash", "1.0"),
                )
            )

            # Draw house number at midpoint of house
            next_cusp_deg = house_cusps.cusps[(i + 1) % 12]
            if next_cusp_deg < cusp_deg:
                next_cusp_deg += 360  # Handle 0-degree wrap

            mid_deg = (cusp_deg + next_cusp_deg) / 2.0

            x_num, y_num = renderer.polar_to_cartesian(mid_deg, house_number_radius)

            dwg.add(
                dwg.text(
                    str(house_num),
                    insert=(x_num, y_num),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["number_size"],
                    fill=style["number_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )


class OuterHouseCuspLayer:
    """
    Renders house cusps for the OUTER wheel (chart2 in comparisons).

    This draws house cusp lines and numbers outside the zodiac ring,
    with a distinct visual style from the inner chart's houses.

    .. deprecated::
        Use HouseCuspLayer(wheel_index=1) instead. This class renders outside
        the zodiac ring (legacy biwheel style), while the new multiwheel system
        renders all charts inside the zodiac ring.
    """

    def __init__(
        self, house_system_name: str, style_override: dict[str, Any] | None = None
    ) -> None:
        """
        Args:
            house_system_name: The name of the system to pull from the chart
            style_override: Optional style changes for this layer
        """
        self.system_name = house_system_name
        self.style = style_override or {}

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render outer house cusps for chart2 (biwheel only).

        Handles both CalculatedChart and Comparison/MultiChart objects.
        For Comparison/MultiChart, uses chart2 (outer wheel).
        For single charts, this layer doesn't apply.
        """
        from stellium.core.chart_utils import is_comparison, is_multichart

        style = renderer.style["houses"].copy()
        style.update(self.style)

        # This layer is ONLY for comparisons/multicharts (outer wheel = chart2)
        if is_comparison(chart):
            actual_chart = chart.chart2
        elif is_multichart(chart) and chart.chart_count >= 2:
            actual_chart = chart.charts[1]  # outer wheel
        else:
            # For single charts, this layer doesn't make sense - skip it
            return

        try:
            house_cusps: HouseCusps = actual_chart.get_houses(self.system_name)
        except (ValueError, KeyError):
            print(
                f"Warning: House system '{self.system_name}' not found in chart data."
            )
            return

        # Define outer radii - beyond the zodiac ring
        # Use config values if available, otherwise fall back to pixel offsets
        outer_cusp_start = renderer.radii.get(
            "outer_cusp_start", renderer.radii["zodiac_ring_outer"] + 5
        )
        outer_cusp_end = renderer.radii.get(
            "outer_cusp_end", renderer.radii["zodiac_ring_outer"] + 35
        )
        outer_number_radius = renderer.radii.get(
            "outer_house_number", renderer.radii["zodiac_ring_outer"] + 20
        )

        for i, cusp_deg in enumerate(house_cusps.cusps):
            house_num = i + 1

            # Draw cusp line extending outward from zodiac ring
            x1, y1 = renderer.polar_to_cartesian(cusp_deg, outer_cusp_start)
            x2, y2 = renderer.polar_to_cartesian(cusp_deg, outer_cusp_end)

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=style["line_color"],
                    stroke_width=style["line_width"],
                    stroke_dasharray=style.get("line_dash", "3,3"),  # Default dashed
                )
            )

            # Draw house number
            # find the midpoint angle of the house
            next_cusp_deg = house_cusps.cusps[(i + 1) % 12]
            if next_cusp_deg < cusp_deg:
                next_cusp_deg += 360  # Handle 0-degree wrap

            mid_deg = (cusp_deg + next_cusp_deg) / 2.0

            x_num, y_num = renderer.polar_to_cartesian(mid_deg, outer_number_radius)

            dwg.add(
                dwg.text(
                    str(house_num),
                    insert=(x_num, y_num),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style.get("number_size", "10px"),
                    fill=style["number_color"],
                    font_family=renderer.style["font_family_text"],
                )
            )
