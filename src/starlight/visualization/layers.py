"""
Concrete Render Layers (starlight.visualization.layers)

These are the concrete implementations of the IRenderLayer protocol.
Each class knows how to draw one specific part of a chart,
reading its data from the CalculatedChart object.
"""

import math
from typing import Any

import svgwrite

from starlight.core.models import CalculatedChart, CelestialPosition, HouseCusps, UnknownTimeChart

from .core import (
    ANGLE_GLYPHS,
    PLANET_GLYPHS,
    ZODIAC_GLYPHS,
    ChartRenderer,
    get_display_name,
    get_glyph,
)
from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    adjust_color_for_contrast,
    get_aspect_palette_colors,
    get_palette_colors,
    get_planet_glyph_color,
    get_sign_info_color,
)


class ZodiacLayer:
    """Renders the outer Zodiac ring, including glyphs and tick marks."""

    def __init__(
        self,
        palette: ZodiacPalette | str = ZodiacPalette.GREY,
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the zodiac layer.

        Args:
            palette: The color palette to use (ZodiacPalette enum, palette name, or "single_color:#RRGGBB")
            style_override: Optional style overrides
        """
        # Try to convert string to enum, but allow pass-through for special formats
        if isinstance(palette, str):
            try:
                self.palette = ZodiacPalette(palette)
            except ValueError:
                # Not a valid enum value, pass through as-is (e.g., "single_color:#RRGGBB")
                self.palette = palette
        else:
            self.palette = palette
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["zodiac"]
        style.update(self.style)

        # Use renderer's zodiac palette if layer palette not explicitly set
        active_palette = self.palette
        if active_palette == ZodiacPalette.GREY and renderer.zodiac_palette:
            # If layer is using default and renderer has a palette, use renderer's
            active_palette = renderer.zodiac_palette

        # Get colors for the palette
        if active_palette == "monochrome":
            # Monochrome: use theme's ring_color for all 12 signs
            ring_color = style.get("ring_color", "#EEEEEE")
            sign_colors = [ring_color] * 12
        else:
            # Convert to enum if string
            if isinstance(active_palette, str):
                active_palette = ZodiacPalette(active_palette)
            sign_colors = get_palette_colors(active_palette)

        # Draw 12 zodiac sign wedges (30° each)
        for sign_index in range(12):
            sign_start = sign_index * 30.0
            sign_end = sign_start + 30.0
            fill_color = sign_colors[sign_index]

            # Create wedge path for this sign
            # We need to draw an arc segment (annulus wedge) from sign_start to sign_end
            x_outer_start, y_outer_start = renderer.polar_to_cartesian(
                sign_start, renderer.radii["zodiac_ring_outer"]
            )
            x_outer_end, y_outer_end = renderer.polar_to_cartesian(
                sign_end, renderer.radii["zodiac_ring_outer"]
            )
            x_inner_start, y_inner_start = renderer.polar_to_cartesian(
                sign_start, renderer.radii["zodiac_ring_inner"]
            )
            x_inner_end, y_inner_end = renderer.polar_to_cartesian(
                sign_end, renderer.radii["zodiac_ring_inner"]
            )

            # Create path: outer arc + line + inner arc (reverse) + line back
            # All signs are 30° so never need large arc flag
            path_data = f"M {x_outer_start},{y_outer_start} "
            path_data += f"A {renderer.radii['zodiac_ring_outer']},{renderer.radii['zodiac_ring_outer']} 0 0,0 {x_outer_end},{y_outer_end} "
            path_data += f"L {x_inner_end},{y_inner_end} "
            path_data += f"A {renderer.radii['zodiac_ring_inner']},{renderer.radii['zodiac_ring_inner']} 0 0,1 {x_inner_start},{y_inner_start} "
            path_data += "Z"

            dwg.add(
                dwg.path(
                    d=path_data,
                    fill=fill_color,
                    stroke="none",
                )
            )

        # Draw degree tick marks (5° increments within each sign)
        # Use angles line color for all tick marks
        tick_color = renderer.style["angles"]["line_color"]
        for sign_index in range(12):
            sign_start = sign_index * 30.0

            # Draw ticks at 5°, 10°, 15°, 20°, 25° within each sign
            # (0° is handled by sign boundary lines)
            for degree_in_sign in [5, 10, 15, 20, 25]:
                absolute_degree = sign_start + degree_in_sign

                # Longer ticks at 10° and 20° marks
                if degree_in_sign in [10, 20]:
                    tick_length = 10
                    tick_width = 0.8
                else:  # Shorter ticks at 5°, 15°, 25° marks
                    tick_length = 7
                    tick_width = 0.5

                # Draw tick from zodiac_ring_outer inward
                x_outer, y_outer = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_outer"]
                )
                x_inner, y_inner = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_outer"] - tick_length
                )

                dwg.add(
                    dwg.line(
                        start=(x_outer, y_outer),
                        end=(x_inner, y_inner),
                        stroke=tick_color,
                        stroke_width=tick_width,
                    )
                )

        # Draw 12 sign boundaries and glyphs
        # Use angles line color for sign boundaries (major divisions)
        boundary_color = renderer.style["angles"]["line_color"]

        for i in range(12):
            deg = i * 30.0

            # Line
            x1, y1 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_outer"]
            )
            x2, y2 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_inner"]
            )
            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=boundary_color,
                    stroke_width=0.5,
                )
            )

            # Glyph with automatic adaptive coloring for accessibility
            glyph_deg = (i * 30.0) + 15.0
            x_glyph, y_glyph = renderer.polar_to_cartesian(
                glyph_deg, renderer.radii["zodiac_glyph"]
            )

            # Always adapt glyph color for contrast against wedge background
            # This ensures glyphs are readable on all palette backgrounds
            sign_bg_color = sign_colors[i]
            glyph_color = adjust_color_for_contrast(
                style["glyph_color"],
                sign_bg_color,
                min_contrast=4.5,
            )

            dwg.add(
                dwg.text(
                    ZODIAC_GLYPHS[i],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=glyph_color,
                    font_family=renderer.style["font_family_glyphs"],
                )
            )


class HouseCuspLayer:
    """
    Renders a *single* set of house cusps and numbers.

    To draw multiple systems, add multiple layers.
    """

    def __init__(
        self, house_system_name: str, style_override: dict[str, Any] | None = None
    ) -> None:
        """
        Args:
            house_system_name: The name of the system to pull from the CalculatedChart (eg "Pladicus")
            style_override: Optional style changes for this specific layer (eg. {"line_color": "red})
        """
        self.system_name = house_system_name
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render house cusps and house numbers.

        Handles both CalculatedChart and Comparison objects.
        For Comparison, uses chart1 (inner wheel).
        """
        from starlight.visualization.extended_canvas import _is_comparison

        style = renderer.style["houses"].copy()
        style.update(self.style)

        # Handle Comparison vs CalculatedChart
        if _is_comparison(chart):
            # For comparison: use chart1 (inner wheel)
            actual_chart = chart.chart1
        else:
            # For single chart: use as-is
            actual_chart = chart

        try:
            house_cusps: HouseCusps = actual_chart.get_houses(self.system_name)
        except (ValueError, KeyError):
            print(
                f"Warning: House system '{self.system_name}' not found in chart data."
            )
            return

        # Draw alternating fill wedges FIRST (if enabled)
        if style.get("fill_alternate", False):
            for i in range(12):
                cusp_deg = house_cusps.cusps[i]
                next_cusp_deg = house_cusps.cusps[(i + 1) % 12]

                # Handle 0-degree wrap
                if next_cusp_deg < cusp_deg:
                    next_cusp_deg += 360

                # Alternate between two fill colors
                fill_color = (
                    style["fill_color_1"] if i % 2 == 0 else style["fill_color_2"]
                )

                # Create a pie wedge path
                # Start at center, go to inner radius at cusp_deg, arc to next_cusp, back to center
                x_start, y_start = renderer.polar_to_cartesian(
                    cusp_deg, renderer.radii["aspect_ring_inner"]
                )
                x_end, y_end = renderer.polar_to_cartesian(
                    next_cusp_deg, renderer.radii["aspect_ring_inner"]
                )
                x_outer_start, y_outer_start = renderer.polar_to_cartesian(
                    cusp_deg, renderer.radii["zodiac_ring_inner"]
                )
                x_outer_end, y_outer_end = renderer.polar_to_cartesian(
                    next_cusp_deg, renderer.radii["zodiac_ring_inner"]
                )

                # Determine if we need the large arc flag (for arcs > 180 degrees)
                angle_diff = next_cusp_deg - cusp_deg
                large_arc = 1 if angle_diff > 180 else 0

                # Create path: outer arc + line + inner arc + line back
                path_data = f"M {x_outer_start},{y_outer_start} "
                path_data += f"A {renderer.radii['zodiac_ring_inner']},{renderer.radii['zodiac_ring_inner']} 0 {large_arc},0 {x_outer_end},{y_outer_end} "
                path_data += f"L {x_end},{y_end} "
                path_data += f"A {renderer.radii['aspect_ring_inner']},{renderer.radii['aspect_ring_inner']} 0 {large_arc},1 {x_start},{y_start} "
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

            # Draw cusp line
            x1, y1 = renderer.polar_to_cartesian(
                cusp_deg, renderer.radii["zodiac_ring_inner"]
            )
            x2, y2 = renderer.polar_to_cartesian(
                cusp_deg, renderer.radii["aspect_ring_inner"]
            )

            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=style["line_color"],
                    stroke_width=style["line_width"],
                    stroke_dasharray=style.get("line_dash", "1.0"),
                )
            )

            # Draw house number
            # find the midpoint angle of the house
            next_cusp_deg = house_cusps.cusps[(i + 1) % 12]
            if next_cusp_deg < cusp_deg:
                next_cusp_deg += 360  # Handle 0-degree wrap

            mid_deg = (cusp_deg + next_cusp_deg) / 2.0

            x_num, y_num = renderer.polar_to_cartesian(
                mid_deg, renderer.radii["house_number_ring"]
            )

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

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render outer house cusps for chart2 (biwheel only).

        Handles both CalculatedChart and Comparison objects.
        For Comparison, uses chart2 (outer wheel).
        For single charts, this layer doesn't apply.
        """
        from starlight.visualization.extended_canvas import _is_comparison

        style = renderer.style["houses"].copy()
        style.update(self.style)

        # This layer is ONLY for comparisons (outer wheel = chart2)
        if _is_comparison(chart):
            actual_chart = chart.chart2
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


class AngleLayer:
    """Renders the primary chart angles (ASC, MC, DSC, IC)"""

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render chart angles.

        Handles both CalculatedChart and Comparison objects.
        For Comparison, uses chart1 (inner wheel) angles.
        """
        from starlight.visualization.extended_canvas import _is_comparison

        style = renderer.style["angles"].copy()
        style.update(self.style)

        # Handle Comparison vs CalculatedChart
        if _is_comparison(chart):
            # For comparison: use chart1 angles (inner wheel)
            actual_chart = chart.chart1
        else:
            # For single chart: use as-is
            actual_chart = chart

        angles = actual_chart.get_angles()

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
                x1, y1 = renderer.polar_to_cartesian(
                    angle.longitude, renderer.radii["zodiac_ring_outer"]
                )
                x2, y2 = renderer.polar_to_cartesian(
                    angle.longitude, renderer.radii["aspect_ring_inner"]
                )
                dwg.add(
                    dwg.line(
                        start=(x1, y1),
                        end=(x2, y2),
                        stroke=line_color,
                        stroke_width=line_width,
                    )
                )

            # Draw angle glyph - positioned just inside the border with directional offset
            base_radius = renderer.radii["zodiac_ring_inner"] + 10
            x_glyph, y_glyph = renderer.polar_to_cartesian(angle.longitude, base_radius)

            # Apply directional offset based on angle name
            offset = 8  # pixels to nudge
            if angle.name == "ASC":  # 9 o'clock - nudge up
                y_glyph -= offset
            elif angle.name == "MC":  # 12 o'clock - nudge right
                x_glyph += offset
            elif angle.name == "DSC":  # 3 o'clock - nudge down
                y_glyph += offset
            elif angle.name == "IC":  # 6 o'clock - nudge left
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


class OuterAngleLayer:
    """Renders the outer wheel angles (for comparison charts)."""

    def __init__(self, style_override: dict[str, Any] | None = None) -> None:
        self.style = style_override or {}

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render outer wheel angles.

        For Comparison, uses chart2 (outer wheel) angles.
        Uses outer_wheel_angles styling from theme for visual distinction.
        """
        from starlight.visualization.extended_canvas import _is_comparison

        # Get outer wheel angle styling (lighter/thinner than inner)
        base_style = renderer.style.get("outer_wheel_angles", renderer.style["angles"])
        style = base_style.copy()
        style.update(self.style)

        # Handle Comparison - use chart2 angles (outer wheel)
        if _is_comparison(chart):
            actual_chart = chart.chart2
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
                    "outer_cusp_end",
                    renderer.radii["zodiac_ring_outer"] + 35
                )
                x2, y2 = renderer.polar_to_cartesian(
                    angle.longitude, outer_radius
                )
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
            glyph_radius = renderer.radii.get(
                "outer_house_number",
                renderer.radii["zodiac_ring_outer"] + 20
            ) - 5  # Slightly inside house numbers
            x_glyph, y_glyph = renderer.polar_to_cartesian(angle.longitude, glyph_radius)

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


class PlanetLayer:
    """Renders a set of planets at a specific radius."""

    def __init__(
        self,
        planet_set: list[CelestialPosition],
        radius_key: str = "planet_ring",
        style_override: dict[str, Any] | None = None,
        use_outer_wheel_color: bool = False,
        info_stack_direction: str = "inward",
        show_info_stack: bool = True,
    ) -> None:
        """
        Args:
            planet_set: The list of CelestialPosition objects to draw.
            radius_key: The key from renderer.radii to use (e.g., "planet_ring").
            style_override: Style overrides for this layer.
            use_outer_wheel_color: If True, use the theme's outer_wheel_planet_color.
            info_stack_direction: "inward" (toward center) or "outward" (away from center).
            show_info_stack: If False, hide info stacks (glyph only).
        """
        self.planets = planet_set
        self.radius_key = radius_key
        self.style = style_override or {}
        self.use_outer_wheel_color = use_outer_wheel_color
        self.info_stack_direction = info_stack_direction
        self.show_info_stack = show_info_stack

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["planets"].copy()
        style.update(self.style)

        base_radius = renderer.radii[self.radius_key]

        # Calculate adjusted positions with collision detection
        adjusted_positions = self._calculate_adjusted_positions(
            self.planets, base_radius
        )

        # Draw all planets with their info columns
        for planet in self.planets:
            original_long = planet.longitude
            adjusted_long = adjusted_positions[planet]["longitude"]
            is_adjusted = adjusted_positions[planet]["adjusted"]

            # Draw connector line if position was adjusted
            if is_adjusted:
                x_original, y_original = renderer.polar_to_cartesian(
                    original_long, base_radius
                )
                x_adjusted, y_adjusted = renderer.polar_to_cartesian(
                    adjusted_long, base_radius
                )
                dwg.add(
                    dwg.line(
                        start=(x_original, y_original),
                        end=(x_adjusted, y_adjusted),
                        stroke="#999999",
                        stroke_width=0.5,
                        stroke_dasharray="2,2",
                        opacity=0.6,
                    )
                )

            # Draw planet glyph at adjusted position
            glyph_info = get_glyph(planet.name)
            x, y = renderer.polar_to_cartesian(adjusted_long, base_radius)

            # Determine glyph color using planet glyph palette if available
            if self.use_outer_wheel_color and "outer_wheel_planet_color" in style:
                # Use outer wheel color for comparison charts
                base_color = style["outer_wheel_planet_color"]
            elif renderer.planet_glyph_palette:
                planet_palette = PlanetGlyphPalette(renderer.planet_glyph_palette)
                base_color = get_planet_glyph_color(
                    planet.name, planet_palette, style["glyph_color"]
                )
            else:
                base_color = style["glyph_color"]

            # Override with retro color if retrograde
            color = style["retro_color"] if planet.is_retrograde else base_color

            if glyph_info["type"] == "svg":
                # Render SVG image
                glyph_size_px = float(style["glyph_size"][:-2])
                # Center the image on the position
                image_x = x - (glyph_size_px / 2)
                image_y = y - (glyph_size_px / 2)

                dwg.add(
                    dwg.image(
                        href=glyph_info["value"],
                        insert=(image_x, image_y),
                        size=(glyph_size_px, glyph_size_px),
                    )
                )
            else:
                # Render Unicode text glyph
                dwg.add(
                    dwg.text(
                        glyph_info["value"],
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=style["glyph_size"],
                        fill=color,
                        font_family=renderer.style["font_family_glyphs"],
                    )
                )

            # Draw Planet Info (Degrees, Sign, Minutes) - all at ADJUSTED longitude
            # This creates a "column" of info that moves together with the glyph
            if self.show_info_stack:
                glyph_size_px = float(style["glyph_size"][:-2])

                # Calculate radii for info rings based on direction
                if self.info_stack_direction == "outward":
                    # Stack extends AWAY from center (for outer wheel)
                    degrees_radius = base_radius + (glyph_size_px * 0.8)
                    sign_radius = base_radius + (glyph_size_px * 1.2)
                    minutes_radius = base_radius + (glyph_size_px * 1.6)
                else:
                    # Stack extends TOWARD center (default, for inner wheel)
                    degrees_radius = base_radius - (glyph_size_px * 0.8)
                    sign_radius = base_radius - (glyph_size_px * 1.2)
                    minutes_radius = base_radius - (glyph_size_px * 1.6)

                # Degrees
                deg_str = f"{int(planet.sign_degree)}°"
                x_deg, y_deg = renderer.polar_to_cartesian(adjusted_long, degrees_radius)
                dwg.add(
                    dwg.text(
                        deg_str,
                        insert=(x_deg, y_deg),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=style["info_size"],
                        fill=style["info_color"],
                        font_family=renderer.style["font_family_text"],
                    )
                )

                # Sign glyph - with optional adaptive coloring
                sign_glyph = ZODIAC_GLYPHS[int(planet.longitude // 30)]
                sign_index = int(planet.longitude // 30)
                x_sign, y_sign = renderer.polar_to_cartesian(adjusted_long, sign_radius)

                # Use adaptive sign color if enabled
                if renderer.color_sign_info and renderer.zodiac_palette:
                    zodiac_pal = ZodiacPalette(renderer.zodiac_palette)
                    sign_color = get_sign_info_color(
                        sign_index,
                        zodiac_pal,
                        renderer.style["background_color"],
                        min_contrast=4.5,
                    )
                else:
                    sign_color = style["info_color"]

                dwg.add(
                    dwg.text(
                        sign_glyph,
                        insert=(x_sign, y_sign),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=style["info_size"],
                        fill=sign_color,
                        font_family=renderer.style["font_family_glyphs"],
                    )
                )

                # Minutes
                min_str = f"{int((planet.sign_degree % 1) * 60):02d}'"
                x_min, y_min = renderer.polar_to_cartesian(adjusted_long, minutes_radius)
                dwg.add(
                    dwg.text(
                        min_str,
                        insert=(x_min, y_min),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=style["info_size"],
                        fill=style["info_color"],
                        font_family=renderer.style["font_family_text"],
                    )
                )

    def _calculate_adjusted_positions(
        self, planets: list[CelestialPosition], base_radius: float
    ) -> dict[CelestialPosition, dict[str, Any]]:
        """
        Calculate adjusted positions for planets with collision detection.

        Groups colliding planets and spreads them evenly while maintaining
        their original order.

        Args:
            planets: List of planets to position
            base_radius: The radius at which to place planet glyphs

        Returns:
            Dictionary mapping each planet to its position info:
            {
                planet: {
                    "longitude": adjusted_longitude,
                    "adjusted": bool (True if position was changed)
                }
            }
        """
        # Minimum angular separation in degrees
        min_separation = 6.0

        # Sort planets by longitude to maintain order
        sorted_planets = sorted(planets, key=lambda p: p.longitude)

        # Find collision groups
        collision_groups = self._find_collision_groups(sorted_planets, min_separation)

        # Adjust positions for each group
        adjusted_positions = {}

        for group in collision_groups:
            if len(group) == 1:
                # No collision - use original position
                planet = group[0]
                adjusted_positions[planet] = {
                    "longitude": planet.longitude,
                    "adjusted": False,
                }
            else:
                # Collision detected - spread the group evenly
                self._spread_group(group, min_separation, adjusted_positions)

        return adjusted_positions

    def _find_collision_groups(
        self, sorted_planets: list[CelestialPosition], min_separation: float
    ) -> list[list[CelestialPosition]]:
        """
        Find groups of planets that are too close together.

        Args:
            sorted_planets: Planets sorted by longitude
            min_separation: Minimum angular separation required

        Returns:
            List of groups, where each group is a list of colliding planets
        """
        if not sorted_planets:
            return []

        groups = []
        current_group = [sorted_planets[0]]

        for i in range(1, len(sorted_planets)):
            prev_planet = sorted_planets[i - 1]
            curr_planet = sorted_planets[i]

            # Calculate angular distance
            distance = curr_planet.longitude - prev_planet.longitude
            # Handle wrap-around at 0°/360°
            if distance < 0:
                distance += 360

            if distance < min_separation:
                # Add to current group
                current_group.append(curr_planet)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [curr_planet]

        # Don't forget the last group
        groups.append(current_group)

        return groups

    def _spread_group(
        self,
        group: list[CelestialPosition],
        min_separation: float,
        adjusted_positions: dict[CelestialPosition, dict[str, Any]],
    ) -> None:
        """
        Spread a group of colliding planets evenly while maintaining order.

        Args:
            group: List of planets in collision (already sorted by longitude)
            min_separation: Minimum angular separation required
            adjusted_positions: Dictionary to populate with adjusted positions
        """
        # Calculate the center point of the group
        group_start = group[0].longitude
        group_end = group[-1].longitude

        # Handle wrap-around
        if group_end < group_start:
            group_end += 360

        group_center = (group_start + group_end) / 2

        # Calculate total span needed for the group
        num_planets = len(group)
        total_span = (num_planets - 1) * min_separation

        # Calculate start position (centered around group center)
        spread_start = group_center - (total_span / 2)

        # Assign positions evenly across the span
        for i, planet in enumerate(group):
            adjusted_long = (spread_start + (i * min_separation)) % 360

            # Check if position was actually changed
            original_long = planet.longitude
            angle_diff = abs(adjusted_long - original_long)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            is_adjusted = (
                angle_diff > 0.5
            )  # More than 0.5° difference counts as adjusted

            adjusted_positions[planet] = {
                "longitude": adjusted_long,
                "adjusted": is_adjusted,
            }


class ChartInfoLayer:
    """
    Renders chart metadata information in a corner of the chart.

    Displays native name, location, date/time, timezone, and coordinates.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "text_size": "11px",
        "line_height": 14,  # Pixels between lines
        "font_weight": "normal",
        "name_size": "16px",  # Larger font for name
        "name_weight": "bold",  # Bold weight for name
    }

    def __init__(
        self,
        position: str = "top-left",
        fields: list[str] | None = None,
        style_override: dict[str, Any] | None = None,
        house_systems: list[str] | None = None,
    ) -> None:
        """
        Initialize chart info layer.

        Args:
            position: Where to place the info block.
                Options: "top-left", "top-right", "bottom-left", "bottom-right"
            fields: List of fields to display. Options:
                "name", "location", "datetime", "timezone", "coordinates",
                "house_system", "ephemeris"
                If None, displays: ["name", "location", "datetime", "timezone",
                "coordinates", "house_system", "ephemeris"]
            style_override: Optional style overrides
            house_systems: List of house system names being rendered on the chart.
                If provided, will display all systems instead of just the default.
        """
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position: {position}. Must be one of {valid_positions}"
            )

        self.position = position
        self.fields = fields or [
            "name",
            "location",
            "datetime",
            "timezone",
            "coordinates",
            "house_system",
            "ephemeris",
        ]
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.house_systems = house_systems

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """Render chart information."""
        # Check for name in metadata first (always display prominently if present)
        name = chart.metadata.get("name") if hasattr(chart, "metadata") else None

        # Build info text lines (excluding name, which is handled separately)
        lines = []

        if "location" in self.fields and chart.location:
            location_name = getattr(chart.location, "name", None)
            if location_name:
                lines.append(location_name)

        if "datetime" in self.fields and chart.datetime:
            # Check if this is an unknown time chart
            is_unknown_time = isinstance(chart, UnknownTimeChart)

            if is_unknown_time:
                # Show date only with "Time Unknown" indicator
                if chart.datetime.local_datetime:
                    dt_str = chart.datetime.local_datetime.strftime("%B %d, %Y")
                else:
                    dt_str = chart.datetime.utc_datetime.strftime("%B %d, %Y")
                dt_str += "  (Time Unknown)"
            elif chart.datetime.local_datetime:
                dt_str = chart.datetime.local_datetime.strftime("%B %d, %Y  %I:%M %p")
            else:
                dt_str = chart.datetime.utc_datetime.strftime("%B %d, %Y  %H:%M UTC")
            lines.append(dt_str)

        if "timezone" in self.fields and chart.location:
            timezone = getattr(chart.location, "timezone", None)
            if timezone:
                lines.append(timezone)

        if "coordinates" in self.fields and chart.location:
            lat = chart.location.latitude
            lon = chart.location.longitude
            lat_dir = "N" if lat >= 0 else "S"
            lon_dir = "E" if lon >= 0 else "W"
            lines.append(f"{abs(lat):.2f}°{lat_dir}, {abs(lon):.2f}°{lon_dir}")

        if "house_system" in self.fields:
            # Skip house system for unknown time charts (no houses without time!)
            is_unknown_time = isinstance(chart, UnknownTimeChart)
            if not is_unknown_time:
                # Use provided house_systems list if available, otherwise use chart's default
                if self.house_systems:
                    if len(self.house_systems) == 1:
                        lines.append(self.house_systems[0])
                    else:
                        # Multiple house systems - show all
                        systems_str = ", ".join(self.house_systems)
                        lines.append(systems_str)
                else:
                    house_system = getattr(chart, "default_house_system", None)
                    if house_system:
                        lines.append(house_system)

        if "ephemeris" in self.fields:
            # Currently only Tropical is implemented
            lines.append("Tropical")

        if not name and not lines:
            return

        # Calculate maximum text width to avoid chart overlap
        max_width = self._get_max_text_width(renderer)

        # Wrap all text lines to fit within max width
        wrapped_lines = []
        for line in lines:
            wrapped = self._wrap_text(line, max_width, self.style["text_size"])
            wrapped_lines.extend(wrapped)

        # Name should never be wrapped - display as single line
        wrapped_name = None
        if name:
            wrapped_name = [name]

        # Calculate total lines including wrapped name (if present)
        # Name takes extra vertical space due to larger font
        name_line_height = int(
            float(self.style["name_size"][:-2]) * 1.2
        )  # 120% of font size
        total_lines = len(wrapped_lines) + (len(wrapped_name) if wrapped_name else 0)

        # Calculate position (use total_lines for proper spacing)
        x, y = self._get_position_coordinates(renderer, total_lines)

        # Determine text anchor based on position
        if "right" in self.position:
            text_anchor = "end"
        else:
            text_anchor = "start"

        # Ensure text color has sufficient contrast with background
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            self.style["text_color"], background_color, min_contrast=4.5
        )

        current_y = y

        # Render name first (if present) with larger, bold font
        if wrapped_name:
            for name_line in wrapped_name:
                dwg.add(
                    dwg.text(
                        name_line,
                        insert=(x, current_y),
                        text_anchor=text_anchor,
                        dominant_baseline="hanging",
                        font_size=self.style["name_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["name_weight"],
                    )
                )
                # Move down for next line (name uses larger spacing)
                current_y += name_line_height

            # Extra gap after name section
            current_y += 2

        # Render remaining info lines with normal font
        for line in wrapped_lines:
            dwg.add(
                dwg.text(
                    line,
                    insert=(x, current_y),
                    text_anchor=text_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )
            current_y += self.style["line_height"]

    def _get_max_text_width(self, renderer: ChartRenderer) -> float:
        """
        Calculate maximum text width before overlapping with chart circle.

        Args:
            renderer: ChartRenderer instance

        Returns:
            Maximum width in pixels
        """
        margin = renderer.size * 0.03
        zodiac_radius = renderer.radii.get("zodiac_ring_outer", renderer.size * 0.47)

        # Calculate available width based on corner position
        if "left" in self.position:
            # Text extends right from margin
            # Chart circle left edge is at center - radius
            chart_left_edge = renderer.center - zodiac_radius
            available_width = chart_left_edge - margin - 10  # 10px safety buffer
        else:  # "right" in position
            # Text extends left from size - margin
            # Chart circle right edge is at center + radius
            chart_right_edge = renderer.center + zodiac_radius
            available_width = (
                (renderer.size - margin) - chart_right_edge - 10
            )  # 10px safety buffer

        return max(available_width, 100)  # Minimum 100px

    def _wrap_text(self, text: str, max_width: float, font_size: str) -> list[str]:
        """
        Wrap text to fit within maximum width.

        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            font_size: Font size (e.g., "11px")

        Returns:
            List of wrapped text lines
        """
        # Extract numeric font size
        size_px = int(float(font_size.replace("px", "")))

        # Rough estimation: average character width is ~0.6 * font_size for proportional fonts
        char_width = size_px * 0.6

        # Calculate max characters per line
        max_chars = int(max_width / char_width)

        if len(text) <= max_chars:
            return [text]

        # Wrap text intelligently at word boundaries
        lines = []
        words = text.split()
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line + " " + word) <= max_chars:
                current_line += " " + word
            else:
                # Current line is full, start new line
                lines.append(current_line)
                current_line = word

        # Add remaining text
        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def _get_position_coordinates(
        self, renderer: ChartRenderer, num_lines: int
    ) -> tuple[float, float]:
        """
        Calculate the (x, y) coordinates for info block placement.

        Args:
            renderer: ChartRenderer instance
            num_lines: Number of text lines to display

        Returns:
            Tuple of (x, y) coordinates
        """
        # Match the chart's own padding (distance from zodiac ring to canvas edge)
        # zodiac_ring_outer is at radius 0.47 * size from center
        # center is at size/2, so padding = size/2 - 0.47 * size = 0.03 * size
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
            # Fallback to top-left
            return (x_offset + margin, y_offset + margin)


class AspectCountsLayer:
    """
    Renders aspect counts summary in a corner of the chart.

    Displays count of each aspect type with glyphs.
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
        position: str = "top-right",
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize aspect counts layer.

        Args:
            position: Where to place the info block.
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
        """Render aspect counts."""
        from starlight.core.registry import get_aspect_info

        # Count aspects by type
        aspect_counts = {}
        for aspect in chart.aspects:
            aspect_name = aspect.aspect_name
            aspect_counts[aspect_name] = aspect_counts.get(aspect_name, 0) + 1

        if not aspect_counts:
            return

        # Build lines (title has no color, aspect lines have colors)
        lines = []
        lines.append(("Aspects:", None))  # Title has no specific color

        # Sort by count (descending)
        sorted_aspects = sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True)

        # Get aspect styles from renderer
        aspect_style_dict = renderer.style.get("aspects", {})

        for aspect_name, count in sorted_aspects:
            aspect_info = get_aspect_info(aspect_name)
            if aspect_info and aspect_info.glyph:
                glyph = aspect_info.glyph
            else:
                glyph = aspect_name[:3]

            # Get the color for this aspect (for legend)
            aspect_style = aspect_style_dict.get(
                aspect_name, aspect_style_dict.get("default", {})
            )
            if isinstance(aspect_style, dict):
                aspect_color = aspect_style.get("color", "#888888")
            else:
                aspect_color = "#888888"

            lines.append((f"{glyph} {aspect_name}: {count}", aspect_color))

        # Calculate position
        x, y = self._get_position_coordinates(renderer, len(lines))

        # Determine text anchor based on position
        if "right" in self.position:
            text_anchor = "end"
        else:
            text_anchor = "start"

        # Ensure text color has sufficient contrast with background
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            self.style["text_color"], background_color, min_contrast=4.5
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


class ElementModalityTableLayer:
    """
    Renders element × modality cross-table in a corner.

    Shows distribution of planets across elements (Fire, Earth, Air, Water)
    and modalities (Cardinal, Fixed, Mutable).
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "text_size": "10px",
        "line_height": 13,
        "font_weight": "normal",
        "title_weight": "bold",
        "col_width": 28,  # Width for each column
    }

    # Element symbols (Unicode)
    ELEMENT_SYMBOLS = {
        "Fire": "🜂",
        "Earth": "🜃",
        "Air": "🜁",
        "Water": "🜄",
    }

    def __init__(
        self,
        position: str = "bottom-left",
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize element/modality table layer.

        Args:
            position: Where to place the table.
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

    def _get_element_modality(self, sign: str) -> tuple[str, str]:
        """
        Get element and modality for a zodiac sign.

        Args:
            sign: Zodiac sign name

        Returns:
            Tuple of (element, modality)
        """
        sign_data = {
            "Aries": ("Fire", "Cardinal"),
            "Taurus": ("Earth", "Fixed"),
            "Gemini": ("Air", "Mutable"),
            "Cancer": ("Water", "Cardinal"),
            "Leo": ("Fire", "Fixed"),
            "Virgo": ("Earth", "Mutable"),
            "Libra": ("Air", "Cardinal"),
            "Scorpio": ("Water", "Fixed"),
            "Sagittarius": ("Fire", "Mutable"),
            "Capricorn": ("Earth", "Cardinal"),
            "Aquarius": ("Air", "Fixed"),
            "Pisces": ("Water", "Mutable"),
        }
        return sign_data.get(sign, ("Unknown", "Unknown"))

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """Render element/modality cross-table."""
        from starlight.core.models import ObjectType

        # Get planets only (not angles, points, etc.)
        planets = [
            p
            for p in chart.positions
            if p.object_type == ObjectType.PLANET and p.name != "Earth"
        ]

        # Build cross-table
        table = {
            "Fire": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
            "Earth": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
            "Air": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
            "Water": {"Cardinal": 0, "Fixed": 0, "Mutable": 0},
        }

        # Count planets
        for planet in planets:
            element, modality = self._get_element_modality(planet.sign)
            if element != "Unknown" and modality != "Unknown":
                table[element][modality] += 1

        # Calculate position
        num_lines = 5  # Header + 4 elements
        x, y = self._get_position_coordinates(renderer, num_lines)

        # Determine positioning based on corner
        if "right" in self.position:
            # Right-aligned: row headers on right, data columns to the left
            row_header_anchor = "end"
            data_anchor = "middle"
            col_offset_multiplier = -1
        else:
            # Left-aligned: row headers on left, data columns to the right
            row_header_anchor = "start"
            data_anchor = "middle"
            col_offset_multiplier = 1

        # Define column positions (relative to base x)
        # Column layout: [Element] [Card] [Fix] [Mut]
        row_header_width = 32  # Width for element symbol + name
        col_width = 20  # Width for each data column

        if "right" in self.position:
            # Columns go left from base position
            col_card_x = x + (col_offset_multiplier * row_header_width)
            col_fix_x = col_card_x + (col_offset_multiplier * col_width)
            col_mut_x = col_fix_x + (col_offset_multiplier * col_width)
            row_header_x = x
        else:
            # Columns go right from base position
            row_header_x = x
            col_card_x = x + row_header_width
            col_fix_x = col_card_x + col_width
            col_mut_x = col_fix_x + col_width

        line_height = self.style["line_height"]

        # Ensure text color has sufficient contrast with background
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            self.style["text_color"], background_color, min_contrast=4.5
        )

        # Header row - render each column header separately
        header_y = y

        # Empty space for element column
        # (no header needed for element column)

        # Column headers (Card, Fix, Mut)
        dwg.add(
            dwg.text(
                "Card",
                insert=(col_card_x, header_y),
                text_anchor=data_anchor,
                dominant_baseline="hanging",
                font_size=self.style["text_size"],
                fill=text_color,
                font_family=renderer.style["font_family_text"],
                font_weight=self.style["title_weight"],
            )
        )
        dwg.add(
            dwg.text(
                "Fix",
                insert=(col_fix_x, header_y),
                text_anchor=data_anchor,
                dominant_baseline="hanging",
                font_size=self.style["text_size"],
                fill=text_color,
                font_family=renderer.style["font_family_text"],
                font_weight=self.style["title_weight"],
            )
        )
        dwg.add(
            dwg.text(
                "Mut",
                insert=(col_mut_x, header_y),
                text_anchor=data_anchor,
                dominant_baseline="hanging",
                font_size=self.style["text_size"],
                fill=text_color,
                font_family=renderer.style["font_family_text"],
                font_weight=self.style["title_weight"],
            )
        )

        # Data rows
        elements = ["Fire", "Earth", "Air", "Water"]
        for i, element in enumerate(elements):
            row_y = header_y + ((i + 1) * line_height)

            # Element symbol + name (row header)
            symbol = self.ELEMENT_SYMBOLS.get(element, element[0])
            row_header_text = f"{symbol} {element[:2]}"

            dwg.add(
                dwg.text(
                    row_header_text,
                    insert=(row_header_x, row_y),
                    text_anchor=row_header_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Data cells (counts) - each in its own column
            card_count = table[element]["Cardinal"]
            fix_count = table[element]["Fixed"]
            mut_count = table[element]["Mutable"]

            # Cardinal count
            dwg.add(
                dwg.text(
                    str(card_count),
                    insert=(col_card_x, row_y),
                    text_anchor=data_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Fixed count
            dwg.add(
                dwg.text(
                    str(fix_count),
                    insert=(col_fix_x, row_y),
                    text_anchor=data_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Mutable count
            dwg.add(
                dwg.text(
                    str(mut_count),
                    insert=(col_mut_x, row_y),
                    text_anchor=data_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
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
        from starlight.utils.chart_shape import (
            detect_chart_shape,
            get_chart_shape_description,
        )

        # Detect shape
        shape, metadata = detect_chart_shape(chart)
        description = get_chart_shape_description(shape, metadata)

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

        # Ensure text color has sufficient contrast with background
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            self.style["text_color"], background_color, min_contrast=4.5
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


class OuterBorderLayer:
    """Renders the outer containment border for comparison/biwheel charts."""

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: Any
    ) -> None:
        """Render the outer containment border using config radius and style."""
        # Check if outer_containment_border radius is set
        if "outer_containment_border" not in renderer.radii:
            return

        border_radius = renderer.radii["outer_containment_border"]

        # Use border styling from theme
        border_color = renderer.style.get("border_color", "#999999")
        border_width = renderer.style.get("border_width", 1)

        # Draw the outer border circle
        dwg.add(
            dwg.circle(
                center=(
                    renderer.center + renderer.x_offset,
                    renderer.center + renderer.y_offset
                ),
                r=border_radius,
                fill="none",
                stroke=border_color,
                stroke_width=border_width,
            )
        )


class MoonRangeLayer:
    """
    Renders a shaded arc showing the Moon's possible position range.

    Used for unknown birth time charts where the Moon could be anywhere
    within a ~12-14° range throughout the day.

    The arc is drawn as a semi-transparent wedge from the day-start position
    to the day-end position, with the Moon glyph at the noon position.
    """

    def __init__(
        self,
        arc_color: str | None = None,
        arc_opacity: float = 0.4,
    ) -> None:
        """
        Initialize moon range layer.

        Args:
            arc_color: Color for the shaded arc (defaults to Moon color from theme)
            arc_opacity: Opacity of the shaded arc (0.0-1.0)
        """
        self.arc_color = arc_color
        self.arc_opacity = arc_opacity

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: Any
    ) -> None:
        """Render the Moon range arc for unknown time charts."""
        # Only render for UnknownTimeChart
        if not isinstance(chart, UnknownTimeChart):
            return

        moon_range = chart.moon_range
        if moon_range is None:
            return

        # Get planet ring radius (where planets are drawn)
        planet_radius = renderer.radii.get("planet_ring", renderer.size * 0.35)

        # Get Moon color from theme
        # Use planets.glyph_color for consistency with how the Moon glyph is rendered
        style = renderer.style
        planet_style = style.get("planets", {})
        default_glyph_color = planet_style.get("glyph_color", "#8B8B8B")

        if self.arc_color:
            # Custom color override
            fill_color = self.arc_color
        elif renderer.planet_glyph_palette:
            # If there's a planet glyph palette, try to get Moon-specific color
            planet_palette = PlanetGlyphPalette(renderer.planet_glyph_palette)
            fill_color = get_planet_glyph_color(
                "Moon", planet_palette, default_glyph_color
            )
        else:
            # Use the theme's planet glyph color (same as Moon glyph)
            fill_color = default_glyph_color

        # Determine arc radii - slightly inside and outside the planet ring
        arc_width = renderer.size * 0.04  # 4% of chart size
        inner_radius = planet_radius - arc_width / 2
        outer_radius = planet_radius + arc_width / 2

        # Use renderer.polar_to_cartesian for correct coordinate transformation
        # This handles rotation, centering, and SVG coordinate system automatically
        start_lon = moon_range.start_longitude
        end_lon = moon_range.end_longitude

        # Get the four corner points using the renderer's coordinate system
        outer_start_x, outer_start_y = renderer.polar_to_cartesian(start_lon, outer_radius)
        outer_end_x, outer_end_y = renderer.polar_to_cartesian(end_lon, outer_radius)
        inner_start_x, inner_start_y = renderer.polar_to_cartesian(start_lon, inner_radius)
        inner_end_x, inner_end_y = renderer.polar_to_cartesian(end_lon, inner_radius)

        # Create the arc path
        path_data = self._create_arc_path(
            outer_start_x, outer_start_y,
            outer_end_x, outer_end_y,
            inner_start_x, inner_start_y,
            inner_end_x, inner_end_y,
            inner_radius, outer_radius,
            moon_range.arc_size
        )

        # Draw the shaded arc
        dwg.add(
            dwg.path(
                d=path_data,
                fill=fill_color,
                fill_opacity=self.arc_opacity,
                stroke="none",
            )
        )

        # Optionally: draw subtle border on the arc
        dwg.add(
            dwg.path(
                d=path_data,
                fill="none",
                stroke=fill_color,
                stroke_width=0.5,
                stroke_opacity=self.arc_opacity * 2,
            )
        )

    def _create_arc_path(
        self,
        outer_start_x: float, outer_start_y: float,
        outer_end_x: float, outer_end_y: float,
        inner_start_x: float, inner_start_y: float,
        inner_end_x: float, inner_end_y: float,
        inner_r: float, outer_r: float,
        arc_size_deg: float,
    ) -> str:
        """
        Create SVG path data for an annular sector (donut slice).

        Args:
            outer_start_x/y: Outer arc start point
            outer_end_x/y: Outer arc end point
            inner_start_x/y: Inner arc start point (at start longitude)
            inner_end_x/y: Inner arc end point (at end longitude)
            inner_r, outer_r: Inner and outer radii for arc commands
            arc_size_deg: Size of the arc in degrees

        Returns:
            SVG path data string
        """
        # For a small arc (< 180°), large_arc_flag = 0
        # Moon range is always < 180° (typically ~12-14°)
        large_arc = 0 if arc_size_deg < 180 else 1

        # Sweep flag: 0 = counter-clockwise, 1 = clockwise
        # In the chart's visual system, zodiac goes counter-clockwise
        # So Moon moving from start to end (increasing longitude) goes counter-clockwise
        # SVG sweep=0 is counter-clockwise
        sweep_outer = 0
        sweep_inner = 1  # Opposite direction for inner arc to close the shape

        # Build path:
        # M = move to outer start
        # A = arc to outer end
        # L = line to inner end (at end longitude)
        # A = arc back to inner start
        # Z = close path
        path = (
            f"M {outer_start_x:.2f},{outer_start_y:.2f} "
            f"A {outer_r:.2f},{outer_r:.2f} 0 {large_arc},{sweep_outer} {outer_end_x:.2f},{outer_end_y:.2f} "
            f"L {inner_end_x:.2f},{inner_end_y:.2f} "
            f"A {inner_r:.2f},{inner_r:.2f} 0 {large_arc},{sweep_inner} {inner_start_x:.2f},{inner_start_y:.2f} "
            f"Z"
        )

        return path
