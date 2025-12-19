"""
Planet layers - planet glyphs, positions, and moon range.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    UnknownTimeChart,
)
from stellium.visualization.core import (
    ZODIAC_GLYPHS,
    ChartRenderer,
    embed_svg_glyph,
    get_glyph,
)
from stellium.visualization.palettes import (
    PlanetGlyphPalette,
    ZodiacPalette,
    get_planet_glyph_color,
    get_sign_info_color,
)

__all__ = ["PlanetLayer", "MoonRangeLayer"]


class PlanetLayer:
    """Renders a set of planets at a specific radius.

    For multiwheel charts, use wheel_index to specify which chart ring to render:
    - wheel_index=0: Chart 1 (innermost)
    - wheel_index=1: Chart 2
    - wheel_index=2: Chart 3
    - wheel_index=3: Chart 4 (outermost, just inside zodiac)

    The info_mode parameter controls how much detail to show:
    - "full": Degree + sign glyph + minutes (default for single charts)
    - "compact": Degree only, e.g. "15°" (good for multiwheel)
    - "no_sign": Degree + minutes, no sign glyph, e.g. "15°32'"
    - "none": No info stack, glyph only
    """

    def __init__(
        self,
        planet_set: list[CelestialPosition],
        radius_key: str = "planet_ring",
        style_override: dict[str, Any] | None = None,
        use_outer_wheel_color: bool = False,
        info_stack_direction: str = "inward",
        show_info_stack: bool = True,
        show_position_ticks: bool = False,
        wheel_index: int = 0,
        info_mode: str = "full",
        info_stack_distance: float = 0.8,
        glyph_size_override: str | None = None,
    ) -> None:
        """
        Args:
            planet_set: The list of CelestialPosition objects to draw.
            radius_key: The key from renderer.radii to use (e.g., "planet_ring").
                        For multiwheel, this is auto-derived from wheel_index if not specified.
            style_override: Style overrides for this layer.
            use_outer_wheel_color: If True, use the theme's outer_wheel_planet_color (legacy).
            info_stack_direction: "inward" (toward center) or "outward" (away from center).
            show_info_stack: If False, hide info stacks (glyph only). Deprecated, use info_mode.
            show_position_ticks: If True, draw colored tick marks at true planet positions
                                 on the zodiac ring inner edge.
            wheel_index: Which chart ring to render (0=innermost, used for multiwheel).
            info_mode: "full" (degree+sign+minutes), "compact" (degree only),
                        "no_sign" (degree+minutes), "none" (glyph only).
            info_stack_distance: Multiplier for distance between glyph and info stack (default 0.8).
                                Smaller values move the info stack closer to the glyph.
            glyph_size_override: If set, overrides the theme's glyph_size (e.g., "24px" for smaller).
        """
        self.planets = planet_set
        self.radius_key = radius_key
        self.style = style_override or {}
        self.use_outer_wheel_color = use_outer_wheel_color
        self.info_stack_direction = info_stack_direction
        self.show_info_stack = show_info_stack
        self.show_position_ticks = show_position_ticks
        self.wheel_index = wheel_index
        self.info_mode = info_mode
        self.info_stack_distance = info_stack_distance
        self.glyph_size_override = glyph_size_override

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["planets"].copy()
        style.update(self.style)

        # Determine glyph size (use override if provided)
        glyph_size_str = self.glyph_size_override or style["glyph_size"]
        glyph_size_px = float(glyph_size_str[:-2])  # Remove "px" suffix

        # Determine radius based on wheel_index or explicit radius_key
        chart_num = self.wheel_index + 1
        planet_ring_key = f"chart{chart_num}_planet_ring"

        # Use multiwheel radius if available, otherwise fall back to legacy
        if planet_ring_key in renderer.radii:
            base_radius = renderer.radii[planet_ring_key]
        else:
            base_radius = renderer.radii.get(
                self.radius_key, renderer.radii.get("planet_ring")
            )

        # Calculate adjusted positions with collision detection
        adjusted_positions = self._calculate_adjusted_positions(
            self.planets, base_radius, glyph_size_px
        )

        # Determine effective info mode (handle legacy show_info_stack)
        effective_info_mode = self.info_mode
        if not self.show_info_stack and self.info_mode == "full":
            effective_info_mode = "none"  # Legacy compatibility

        # Draw all planets with their info columns
        for planet in self.planets:
            original_long = planet.longitude
            adjusted_long = adjusted_positions[planet]["longitude"]
            is_adjusted = adjusted_positions[planet]["adjusted"]

            # Determine glyph color using wheel_index-based colors for multiwheel
            chart_color_key = f"chart{chart_num}_color"
            if chart_color_key in style:
                # Use multiwheel chart-specific color
                base_color = style[chart_color_key]
            elif self.use_outer_wheel_color and "outer_wheel_planet_color" in style:
                # Legacy: use outer wheel color for comparison charts
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

            # Draw position tick at true position, extending inward from zodiac ring
            if self.show_position_ticks:
                tick_radius_outer = renderer.radii["zodiac_ring_inner"]
                tick_length = 6
                x_tick_outer, y_tick_outer = renderer.polar_to_cartesian(
                    original_long, tick_radius_outer
                )
                x_tick_inner, y_tick_inner = renderer.polar_to_cartesian(
                    original_long, tick_radius_outer - tick_length
                )
                dwg.add(
                    dwg.line(
                        start=(x_tick_outer, y_tick_outer),
                        end=(x_tick_inner, y_tick_inner),
                        stroke=color,
                        stroke_width=1.5,
                    )
                )

            # Draw connector line if position was adjusted
            if is_adjusted:
                # Glyph is at adjusted position on planet ring
                x_glyph, y_glyph = renderer.polar_to_cartesian(
                    adjusted_long, base_radius
                )

                if self.show_position_ticks:
                    # Connect to the position tick on zodiac ring inner edge
                    x_target, y_target = renderer.polar_to_cartesian(
                        original_long, renderer.radii["zodiac_ring_inner"]
                    )
                else:
                    # Original behavior: connect to true position on planet ring
                    x_target, y_target = renderer.polar_to_cartesian(
                        original_long, base_radius
                    )

                dwg.add(
                    dwg.line(
                        start=(x_glyph, y_glyph),
                        end=(x_target, y_target),
                        stroke="#999999",
                        stroke_width=0.5,
                        stroke_dasharray="2,2",
                        opacity=0.6,
                    )
                )

            # Draw planet glyph at adjusted position
            glyph_info = get_glyph(planet.name)
            x, y = renderer.polar_to_cartesian(adjusted_long, base_radius)

            if glyph_info["type"] == "svg":
                # Render inline SVG glyph (works across all browsers)
                embed_svg_glyph(
                    dwg,
                    glyph_info["value"],
                    x,
                    y,
                    glyph_size_px,
                    fill_color=color,
                )
            else:
                # Render Unicode text glyph
                dwg.add(
                    dwg.text(
                        glyph_info["value"],
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="central",
                        font_size=glyph_size_str,
                        fill=color,
                        font_family=renderer.style["font_family_glyphs"],
                    )
                )

            # Draw Planet Info based on info_mode
            # - "full": Degree + Sign glyph + Minutes (3-row stack)
            # - "compact": Degree only (single value, e.g., "15°")
            # - "no_sign": Degree + Minutes (2-row stack, no sign glyph)
            # - "none": No info stack
            if effective_info_mode != "none":
                # Calculate radii for info rings based on direction
                # Use info_stack_distance multiplier (default 0.8, smaller = closer to glyph)
                dist = self.info_stack_distance
                if self.info_stack_direction == "outward":
                    # Stack extends AWAY from center (for outer wheel)
                    degrees_radius = base_radius + (glyph_size_px * dist)
                    sign_radius = base_radius + (glyph_size_px * (dist + 0.4))
                    # For no_sign mode, use 0.55 spacing for better readability with small glyphs
                    if effective_info_mode == "no_sign":
                        minutes_radius = base_radius + (glyph_size_px * (dist + 0.55))
                    else:
                        minutes_radius = base_radius + (glyph_size_px * (dist + 0.8))
                else:
                    # Stack extends TOWARD center (default, for inner wheel)
                    degrees_radius = base_radius - (glyph_size_px * dist)
                    sign_radius = base_radius - (glyph_size_px * (dist + 0.4))
                    # For no_sign mode, use 0.55 spacing for better readability with small glyphs
                    if effective_info_mode == "no_sign":
                        minutes_radius = base_radius - (glyph_size_px * (dist + 0.55))
                    else:
                        minutes_radius = base_radius - (glyph_size_px * (dist + 0.8))

                # Degrees (shown in both "full" and "compact" modes)
                deg_str = f"{int(planet.sign_degree)}°"
                x_deg, y_deg = renderer.polar_to_cartesian(
                    adjusted_long, degrees_radius
                )
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

                # Sign glyph only in "full" mode
                if effective_info_mode == "full":
                    # Sign glyph - with optional adaptive coloring
                    sign_glyph = ZODIAC_GLYPHS[int(planet.longitude // 30)]
                    sign_index = int(planet.longitude // 30)
                    x_sign, y_sign = renderer.polar_to_cartesian(
                        adjusted_long, sign_radius
                    )

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

                # Minutes in "full" and "no_sign" modes
                if effective_info_mode in ("full", "no_sign"):
                    min_str = f"{int((planet.sign_degree % 1) * 60):02d}'"
                    x_min, y_min = renderer.polar_to_cartesian(
                        adjusted_long, minutes_radius
                    )
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
        self,
        planets: list[CelestialPosition],
        base_radius: float,
        glyph_size_px: float = 32.0,
    ) -> dict[CelestialPosition, dict[str, Any]]:
        """
        Calculate adjusted positions for planets with radius-aware collision detection.

        Uses an iterative force-based algorithm that:
        1. Calculates minimum angular separation based on glyph size and ring radius
        2. Iteratively pushes colliding glyphs apart until stable
        3. Properly handles wrap-around at the 0°/360° boundary
        4. Limits maximum displacement to keep glyphs near their true positions

        Args:
            planets: List of planets to position
            base_radius: The radius at which to place planet glyphs (in pixels)
            glyph_size_px: The glyph font size in pixels (default 32.0)

        Returns:
            Dictionary mapping each planet to its position info:
            {
                planet: {
                    "longitude": adjusted_longitude,
                    "adjusted": bool (True if position was changed)
                }
            }
        """
        import math

        if not planets:
            return {}

        # Calculate radius-aware minimum separation
        # Glyph width is approximately the font size
        # We need enough angular space for the glyph plus a small buffer
        glyph_width_px = glyph_size_px
        buffer_factor = 1.3  # 30% extra space for visual clarity

        # Arc length formula: arc = (angle/360) * 2*pi*r
        # Solving for angle: angle = (arc * 360) / (2*pi*r)
        circumference = 2 * math.pi * base_radius
        min_separation = (glyph_width_px * buffer_factor * 360) / circumference

        # Ensure a reasonable minimum (at least 4°) and maximum (at most 15°)
        min_separation = max(4.0, min(15.0, min_separation))

        # Initialize display positions to true positions
        display_positions = {p: p.longitude for p in planets}

        # Iterative force-based spreading
        max_iterations = 50
        convergence_threshold = 0.1  # Stop when max movement < this

        for _iteration in range(max_iterations):
            max_movement = 0.0

            # Sort planets by current display position for efficient neighbor checks
            sorted_planets = sorted(planets, key=lambda p: display_positions[p])
            n = len(sorted_planets)

            # Calculate forces on each planet
            forces = dict.fromkeys(planets, 0.0)

            # Check each adjacent pair (including wrap-around from last to first)
            for i in range(n):
                curr_planet = sorted_planets[i]
                next_planet = sorted_planets[(i + 1) % n]  # Wrap around

                curr_pos = display_positions[curr_planet]
                next_pos = display_positions[next_planet]

                # Calculate the forward (clockwise) distance from curr to next
                forward_dist = (next_pos - curr_pos) % 360

                # If forward distance > 180, the "short" path is backward
                # We want the short path distance for collision detection
                if forward_dist > 180:
                    # The short path is backward (counter-clockwise)
                    short_dist = 360 - forward_dist
                else:
                    # The short path is forward (clockwise)
                    short_dist = forward_dist

                if short_dist < min_separation:
                    # Collision detected - push them apart
                    overlap = min_separation - short_dist
                    push = overlap * 0.5

                    # Determine which direction to push
                    # Push curr backward and next forward along the SHORT path
                    if forward_dist <= 180:
                        # Short path is forward: curr should go backward, next forward
                        forces[curr_planet] -= push
                        forces[next_planet] += push
                    else:
                        # Short path is backward: curr should go forward, next backward
                        forces[curr_planet] += push
                        forces[next_planet] -= push

            # Apply forces with damping and limits
            for planet in planets:
                force = forces[planet]
                if abs(force) > 0.01:  # Only apply meaningful forces
                    # Limit max movement per iteration for stability
                    movement = max(-2.0, min(2.0, force))

                    # Calculate new position
                    new_pos = (display_positions[planet] + movement) % 360

                    # Limit max displacement from true position (max 20°)
                    true_pos = planet.longitude
                    displacement = self._signed_circular_distance(true_pos, new_pos)
                    max_displacement = 20.0
                    if abs(displacement) > max_displacement:
                        # Clamp to max displacement
                        if displacement > 0:
                            new_pos = (true_pos + max_displacement) % 360
                        else:
                            new_pos = (true_pos - max_displacement) % 360

                    max_movement = max(max_movement, abs(force))
                    display_positions[planet] = new_pos

            # Check for convergence
            if max_movement < convergence_threshold:
                break

        # Build result dictionary
        adjusted_positions = {}
        for planet in planets:
            original_long = planet.longitude
            adjusted_long = display_positions[planet]

            # Check if position was actually changed (more than 0.5° difference)
            angle_diff = abs(
                self._signed_circular_distance(original_long, adjusted_long)
            )
            is_adjusted = angle_diff > 0.5

            adjusted_positions[planet] = {
                "longitude": adjusted_long,
                "adjusted": is_adjusted,
            }

        return adjusted_positions

    def _circular_distance(self, pos1: float, pos2: float) -> float:
        """
        Calculate the shortest angular distance between two positions on a circle.

        Always returns a positive value representing the absolute distance.

        Args:
            pos1: First position in degrees (0-360)
            pos2: Second position in degrees (0-360)

        Returns:
            Shortest angular distance in degrees (0-180)
        """
        diff = abs(pos2 - pos1)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _signed_circular_distance(self, from_pos: float, to_pos: float) -> float:
        """
        Calculate the signed angular distance from one position to another.

        Positive = clockwise (increasing degrees), Negative = counter-clockwise.

        Args:
            from_pos: Starting position in degrees (0-360)
            to_pos: Target position in degrees (0-360)

        Returns:
            Signed angular distance in degrees (-180 to +180)
        """
        diff = to_pos - from_pos
        # Normalize to -180 to +180
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        return diff


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
        outer_start_x, outer_start_y = renderer.polar_to_cartesian(
            start_lon, outer_radius
        )
        outer_end_x, outer_end_y = renderer.polar_to_cartesian(end_lon, outer_radius)
        inner_start_x, inner_start_y = renderer.polar_to_cartesian(
            start_lon, inner_radius
        )
        inner_end_x, inner_end_y = renderer.polar_to_cartesian(end_lon, inner_radius)

        # Create the arc path
        path_data = self._create_arc_path(
            outer_start_x,
            outer_start_y,
            outer_end_x,
            outer_end_y,
            inner_start_x,
            inner_start_y,
            inner_end_x,
            inner_end_y,
            inner_radius,
            outer_radius,
            moon_range.arc_size,
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
        outer_start_x: float,
        outer_start_y: float,
        outer_end_x: float,
        outer_end_y: float,
        inner_start_x: float,
        inner_start_y: float,
        inner_end_x: float,
        inner_end_y: float,
        inner_r: float,
        outer_r: float,
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
