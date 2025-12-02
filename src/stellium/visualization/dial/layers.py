"""
Dial Chart Layers (stellium.visualization.dial.layers)

Concrete layer implementations for dial chart visualization.
Each layer draws one specific part of the dial chart.
"""

import math
from typing import Protocol

import svgwrite

from stellium.core.models import CalculatedChart, CelestialPosition
from stellium.visualization.core import embed_svg_glyph, get_glyph
from stellium.visualization.dial.config import DialStyle
from stellium.visualization.dial.renderer import DialRenderer


class IDialLayer(Protocol):
    """Protocol for dial chart layers."""

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Render this layer onto the dial chart."""
        ...


# =============================================================================
# Modality Signs Mapping
# =============================================================================

# Signs grouped by modality (for the inner wheel)
CARDINAL_SIGNS = ["Aries", "Cancer", "Libra", "Capricorn"]
FIXED_SIGNS = ["Taurus", "Leo", "Scorpio", "Aquarius"]
MUTABLE_SIGNS = ["Gemini", "Virgo", "Sagittarius", "Pisces"]

# Sign index to glyph mapping
SIGN_GLYPHS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

# Trans-Neptunian Objects (TNOs) to include by default in dial charts
# These are important for Uranian astrology
TNO_NAMES = {"Eris", "Sedna", "Makemake", "Haumea", "Orcus", "Quaoar"}

# Hamburg/Uranian School hypothetical planets and reference points
# These 8 theoretical planets + Aries Point are fundamental to Uranian astrology
HAMBURG_NAMES = {
    "Cupido",
    "Hades",
    "Zeus",
    "Kronos",
    "Apollon",
    "Admetos",
    "Vulkanus",
    "Poseidon",
    "Aries Point",
}


# =============================================================================
# Background Layer
# =============================================================================


class DialBackgroundLayer:
    """
    Renders the dial background and outer border.
    """

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw the dial background."""
        style = renderer.style
        radii = renderer.radii

        # Outer border circle
        dwg.add(
            renderer.draw_circle(
                dwg,
                radii["graduation_outer"],
                fill="none",
                stroke=style.graduation_tick_color,
                stroke_width=1,
            )
        )


# =============================================================================
# Graduation Layer
# =============================================================================


class DialGraduationLayer:
    """
    Renders the graduated tick marks and degree labels on the outer ring.

    Draws:
    - Small tick marks every 1°
    - Medium tick marks every 5°
    - Labels at configured intervals (default every 5°)
    """

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw graduation tick marks and labels."""
        config = renderer.config
        style = renderer.style
        radii = renderer.radii
        grad_config = config.graduation

        outer_r = radii["graduation_outer"]
        inner_r = radii["graduation_inner"]
        ring_width = outer_r - inner_r

        # Draw tick marks for each degree
        for deg in range(config.dial_degrees):
            # Determine tick length based on degree
            if deg % 10 == 0:
                tick_frac = grad_config.tick_10_degree
            elif deg % 5 == 0:
                tick_frac = grad_config.tick_5_degree
            else:
                tick_frac = grad_config.tick_1_degree

            tick_length = ring_width * tick_frac
            tick_outer = outer_r
            tick_inner = outer_r - tick_length

            # Draw tick
            line = renderer.draw_line_radial(
                dwg,
                deg,
                tick_inner,
                tick_outer,
                stroke=style.graduation_tick_color,
                stroke_width=grad_config.tick_width,
            )
            dwg.add(line)

        # Draw labels
        if grad_config.show_labels:
            label_radius = inner_r - 8  # Position labels inside the graduation ring

            # Adjust label interval based on dial size
            # 90° dial: every 5°, 45° dial: every 5°, 360° dial: every 10°
            if config.dial_degrees == 360:
                label_interval = 10
            else:
                label_interval = grad_config.label_interval

            for deg in range(0, config.dial_degrees, label_interval):
                x, y = renderer.polar_to_cartesian(deg, label_radius)

                dwg.add(
                    dwg.text(
                        str(deg),
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_size=grad_config.label_font_size,
                        font_family=style.font_family_text,
                        fill=style.graduation_label_color,
                    )
                )


# =============================================================================
# Cardinal Points Layer
# =============================================================================


class DialCardinalLayer:
    """
    Renders the cardinal point markers (arrows and accent marks).

    For 90° dial: marks at 0°, 22.5°, 45°, 67.5°
    These represent the cardinal cross of the zodiac.
    """

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw cardinal point markers."""
        config = renderer.config
        style = renderer.style
        radii = renderer.radii
        cardinal_config = config.cardinal

        cardinal_points = renderer.get_cardinal_points()

        for deg in cardinal_points:
            # Draw arrow markers
            if cardinal_config.show_arrows:
                self._draw_arrow(renderer, dwg, deg, style, radii, cardinal_config)

            # Draw accent marks on outer ring
            if cardinal_config.show_accents:
                self._draw_accent(renderer, dwg, deg, style, radii, cardinal_config)

    def _draw_arrow(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        deg: float,
        style: DialStyle,
        radii: dict,
        config,
    ) -> None:
        """Draw an arrow marker pointing inward at the given degree."""
        outer_r = radii["graduation_outer"]
        inner_r = radii["graduation_inner"]

        # Arrow extends from outside the graduation ring to inside
        arrow_outer = outer_r + 15
        arrow_inner = inner_r - 5

        # Main arrow line
        line = renderer.draw_line_radial(
            dwg,
            deg,
            arrow_inner,
            arrow_outer,
            stroke=style.cardinal_arrow_color,
            stroke_width=config.arrow_width,
        )
        dwg.add(line)

        # Arrow head (pointing inward)
        tip_x, tip_y = renderer.polar_to_cartesian(deg, arrow_inner)
        head_size = 8

        # Get the angle for arrow head wings
        svg_angle = renderer.dial_to_svg_angle(deg)
        angle_rad = math.radians(svg_angle)

        # Wing points (30° spread)
        wing_angle = math.radians(25)
        wing_length = head_size

        # Calculate wing endpoints
        # Wings point back toward the outer edge
        wing1_x = tip_x + wing_length * math.cos(angle_rad + wing_angle)
        wing1_y = tip_y + wing_length * math.sin(angle_rad + wing_angle)
        wing2_x = tip_x + wing_length * math.cos(angle_rad - wing_angle)
        wing2_y = tip_y + wing_length * math.sin(angle_rad - wing_angle)

        # Draw arrow head as filled triangle
        arrow_head = dwg.polygon(
            points=[(tip_x, tip_y), (wing1_x, wing1_y), (wing2_x, wing2_y)],
            fill=style.cardinal_arrow_color,
        )
        dwg.add(arrow_head)

    def _draw_accent(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        deg: float,
        style: DialStyle,
        radii: dict,
        config,
    ) -> None:
        """Draw a thick accent mark at the cardinal point."""
        outer_r = radii["graduation_outer"]

        # Draw a thick arc segment at this position
        arc_span = 2  # degrees
        start = deg - arc_span / 2
        end = deg + arc_span / 2

        # We'll use a thick stroke on a circle segment
        x1, y1 = renderer.polar_to_cartesian(start, outer_r)
        x2, y2 = renderer.polar_to_cartesian(end, outer_r)

        # Just draw a thick line for the accent
        line = renderer.draw_line_radial(
            dwg,
            deg,
            outer_r - 3,
            outer_r + 3,
            stroke=style.cardinal_accent_color,
            stroke_width=config.accent_width,
        )
        dwg.add(line)


# =============================================================================
# Modality Wheel Layer
# =============================================================================


class DialModalityLayer:
    """
    Renders the inner modality wheel with zodiac glyphs.

    The wheel is divided into 3 sectors (Cardinal, Fixed, Mutable),
    each containing the 4 zodiac signs of that modality.
    """

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw the modality wheel."""
        config = renderer.config
        style = renderer.style
        radii = renderer.radii
        mod_config = config.modality

        outer_r = radii["modality_outer"]
        inner_r = radii["modality_inner"]

        sectors = renderer.get_modality_sectors()

        # Draw sector backgrounds
        for i, (start_deg, end_deg, _modality) in enumerate(sectors):
            fill_color = (
                style.modality_sector_color_1
                if i % 2 == 0
                else style.modality_sector_color_2
            )

            # Draw sector as a path (pie slice)
            self._draw_sector(
                renderer, dwg, start_deg, end_deg, inner_r, outer_r, fill_color, style
            )

        # Draw sector dividing lines
        for start_deg, _end_deg, _ in sectors:
            line = renderer.draw_line_radial(
                dwg,
                start_deg,
                inner_r,
                outer_r,
                stroke=style.modality_line_color,
                stroke_width=mod_config.sector_line_width,
            )
            dwg.add(line)

        # Draw zodiac glyphs in each sector
        self._draw_modality_glyphs(renderer, dwg, style, mod_config, outer_r, inner_r)

    def _draw_sector(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        start_deg: float,
        end_deg: float,
        inner_r: float,
        outer_r: float,
        fill_color: str,
        style: DialStyle,
    ) -> None:
        """Draw a pie sector."""
        # Get corner points
        outer_start = renderer.polar_to_cartesian(start_deg, outer_r)
        outer_end = renderer.polar_to_cartesian(end_deg, outer_r)
        inner_start = renderer.polar_to_cartesian(start_deg, inner_r)
        inner_end = renderer.polar_to_cartesian(end_deg, inner_r)

        # Calculate arc span for large-arc flag
        arc_span = (end_deg - start_deg) % renderer.dial_degrees
        svg_span = arc_span * (360 / renderer.dial_degrees)
        large_arc = 1 if svg_span > 180 else 0

        # Build path: outer arc, line to inner, inner arc (reverse), line back
        d = (
            f"M {outer_start[0]} {outer_start[1]} "
            f"A {outer_r} {outer_r} 0 {large_arc} 1 {outer_end[0]} {outer_end[1]} "
            f"L {inner_end[0]} {inner_end[1]} "
            f"A {inner_r} {inner_r} 0 {large_arc} 0 {inner_start[0]} {inner_start[1]} "
            f"Z"
        )

        path = dwg.path(d=d, fill=fill_color, stroke="none")
        dwg.add(path)

    def _draw_modality_glyphs(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        style: DialStyle,
        mod_config,
        outer_r: float,
        inner_r: float,
    ) -> None:
        """Draw zodiac glyphs arranged in the modality sectors."""
        modality_signs = [
            (CARDINAL_SIGNS, 0),
            (FIXED_SIGNS, 1),
            (MUTABLE_SIGNS, 2),
        ]

        sector_size = renderer.dial_degrees / 3
        glyph_radius = (outer_r + inner_r) / 2  # Center of the ring

        for signs, sector_index in modality_signs:
            # Center of this sector
            sector_center = sector_size * sector_index + sector_size / 2

            # Arrange 4 glyphs in a vertical stack within the sector
            # We'll position them at different radii instead of different angles
            # to avoid overcrowding
            for i, sign in enumerate(signs):
                glyph = SIGN_GLYPHS[sign]

                # Stack glyphs vertically (different radii)
                # Alternate between slightly left and right of center
                angle_offset = (i % 2 - 0.5) * 8  # -4 or +4 degrees
                radius_offset = (i // 2 - 0.5) * 12  # -6 or +6 pixels

                x, y = renderer.polar_to_cartesian(
                    sector_center + angle_offset,
                    glyph_radius + radius_offset,
                )

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_size=mod_config.glyph_font_size,
                        font_family=style.font_family_glyphs,
                        fill=style.modality_glyph_color,
                    )
                )


# =============================================================================
# Collision Detection Utilities
# =============================================================================


def resolve_dial_collisions(
    positions: list[dict],
    dial_degrees: int,
    min_spacing_360: float = 8.0,
) -> list[dict]:
    """
    Resolve collisions between glyphs on a dial chart.

    Uses a spreading algorithm that scales appropriately for the dial size.
    The min_spacing is specified for a 360° chart and automatically scaled.

    Args:
        positions: List of dicts with "true_deg" and "display_deg" keys
        dial_degrees: Size of the dial (90, 45, or 360)
        min_spacing_360: Minimum spacing in degrees for a 360° chart (default: 8°)

    Returns:
        Updated positions list with adjusted display_deg values
    """
    if not positions or len(positions) < 2:
        return positions

    # Scale min_spacing for the dial size
    # On a 90° dial, 8° on a 360° chart becomes 2° (8 * 90/360)
    min_spacing = min_spacing_360 * dial_degrees / 360

    # Sort by true position
    positions = sorted(positions, key=lambda p: p["true_deg"])

    # Multiple passes to spread out collisions
    for _ in range(20):  # Max iterations
        moved = False

        for i in range(len(positions)):
            curr = positions[i]
            prev_idx = (i - 1) % len(positions)
            next_idx = (i + 1) % len(positions)

            prev_pos = positions[prev_idx]
            next_pos = positions[next_idx]

            # Calculate distances (handling wrap-around)
            display_deg = curr["display_deg"]

            dist_to_prev = _angular_distance(
                display_deg, prev_pos["display_deg"], dial_degrees
            )
            dist_to_next = _angular_distance(
                next_pos["display_deg"], display_deg, dial_degrees
            )

            # Check if too close to neighbors
            if dist_to_prev < min_spacing or dist_to_next < min_spacing:
                # Calculate push amount (smaller for smaller dials)
                push = 0.5 * dial_degrees / 360  # 0.5° for 360°, 0.125° for 90°
                push = max(push, 0.2)  # Minimum push of 0.2°

                # Push away from closer neighbor
                if dist_to_prev < dist_to_next:
                    # Move away from prev (forward)
                    curr["display_deg"] = (display_deg + push) % dial_degrees
                else:
                    # Move away from next (backward)
                    curr["display_deg"] = (
                        display_deg - push + dial_degrees
                    ) % dial_degrees

                moved = True

        if not moved:
            break

    return positions


def _angular_distance(deg1: float, deg2: float, dial_size: float) -> float:
    """Calculate angular distance on a circular dial."""
    diff = abs(deg1 - deg2)
    return min(diff, dial_size - diff)


# =============================================================================
# Planet Layer
# =============================================================================


class DialPlanetLayer:
    """
    Renders planet glyphs on the dial with collision detection.

    By default, includes:
    - All 10 planets (Sun through Pluto)
    - Trans-Neptunian Objects (Eris, Sedna, Makemake, Haumea, Orcus, Quaoar)
    - Hamburg/Uranian hypothetical planets (Cupido, Hades, Zeus, Kronos,
      Apollon, Admetos, Vulkanus, Poseidon)

    Draws:
    - Tick marks at true (compressed) positions
    - Planet glyphs with collision avoidance
    - Dashed connector lines when glyphs are displaced
    """

    def __init__(
        self,
        ring: str = "planet_ring",
        include_tnos: bool = True,
        include_uranian: bool = True,
    ):
        """
        Initialize planet layer.

        Args:
            ring: Which radius to draw planets on (default: "planet_ring")
            include_tnos: Whether to include Trans-Neptunian Objects (default: True)
            include_uranian: Whether to include Hamburg/Uranian hypothetical
                planets (default: True)
        """
        self.ring = ring
        self.include_tnos = include_tnos
        self.include_uranian = include_uranian

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw planet glyphs with collision detection."""
        config = renderer.config
        style = renderer.style
        radii = renderer.radii
        planet_config = config.planet
        dial_degrees = renderer.dial_degrees

        planet_radius = radii[self.ring]
        tick_outer = radii["graduation_inner"]
        tick_inner = tick_outer - planet_config.tick_length

        # Get planet positions
        planets = list(chart.get_planets())

        # Add TNOs if requested and present in the chart
        if self.include_tnos:
            for pos in chart.positions:
                if pos.name in TNO_NAMES:
                    planets.append(pos)

        # Add Hamburg/Uranian planets if requested and present in the chart
        if self.include_uranian:
            for pos in chart.positions:
                if pos.name in HAMBURG_NAMES:
                    planets.append(pos)

        # Convert to dial positions
        dial_positions = []
        for planet in planets:
            dial_deg = renderer.compress_longitude(planet.longitude)
            dial_positions.append(
                {
                    "planet": planet,
                    "true_deg": dial_deg,
                    "display_deg": dial_deg,  # Will be adjusted for collisions
                }
            )

        # Apply collision detection (scaled for dial size)
        dial_positions = resolve_dial_collisions(
            dial_positions,
            dial_degrees,
            min_spacing_360=planet_config.min_glyph_spacing,
        )

        # Draw tick marks and glyphs
        for pos_data in dial_positions:
            planet = pos_data["planet"]
            true_deg = pos_data["true_deg"]
            display_deg = pos_data["display_deg"]

            # Draw tick mark at true position
            if planet_config.show_ticks:
                tick = renderer.draw_line_radial(
                    dwg,
                    true_deg,
                    tick_inner,
                    tick_outer,
                    stroke=style.planet_tick_color,
                    stroke_width=planet_config.tick_width,
                )
                dwg.add(tick)

            # Draw connector if displaced (threshold scales with dial size)
            displacement = _angular_distance(display_deg, true_deg, dial_degrees)
            if (
                displacement > 0.3 * dial_degrees / 360
            ):  # ~0.3° for 360°, ~0.075° for 90°
                tick_x, tick_y = renderer.polar_to_cartesian(true_deg, tick_inner)
                glyph_x, glyph_y = renderer.polar_to_cartesian(
                    display_deg, planet_radius
                )

                connector = dwg.line(
                    start=(tick_x, tick_y),
                    end=(glyph_x, glyph_y),
                    stroke=style.planet_connector_color,
                    stroke_width=planet_config.connector_width,
                    stroke_dasharray=planet_config.connector_dash,
                )
                dwg.add(connector)

            # Draw planet glyph
            glyph_info = get_glyph(planet.name)
            x, y = renderer.polar_to_cartesian(display_deg, planet_radius)

            if glyph_info["type"] == "svg":
                # Render inline SVG glyph
                glyph_size = float(planet_config.glyph_font_size.replace("px", ""))
                embed_svg_glyph(
                    dwg,
                    glyph_info["value"],
                    x,
                    y,
                    glyph_size,
                    fill_color=style.planet_glyph_color,
                )
            else:
                # Render Unicode text glyph
                dwg.add(
                    dwg.text(
                        glyph_info["value"],
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_size=planet_config.glyph_font_size,
                        font_family=style.font_family_glyphs,
                        fill=style.planet_glyph_color,
                    )
                )


# =============================================================================
# Midpoint Layer
# =============================================================================


class DialMidpointLayer:
    """
    Renders midpoints on an outer ring of the dial.

    Midpoints are the halfway points between two planets.
    Each midpoint has:
    - A tick mark at its true position
    - A label/glyph with collision avoidance
    - A dashed connector line if displaced
    """

    def __init__(self, ring: str = "outer_ring_1", notation: str = "full"):
        """
        Initialize midpoint layer.

        Args:
            ring: Which outer ring to draw on
            notation: "full" (☉/☽), "abbreviated", or "tick"
        """
        self.ring = ring
        self.notation = notation

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw midpoints on the outer ring with collision detection."""
        _config = renderer.config
        style = renderer.style
        radii = renderer.radii
        dial_degrees = renderer.dial_degrees

        midpoint_radius = radii[self.ring]
        # Tick marks go on the inner edge of the outer ring
        tick_inner = radii["graduation_outer"] + 2
        tick_outer = tick_inner + 6

        planets = chart.get_planets()

        # Calculate all midpoints
        midpoints = []
        for i, p1 in enumerate(planets):
            for p2 in planets[i + 1 :]:
                mp_longitude = self._calculate_midpoint(p1.longitude, p2.longitude)
                mp_dial = renderer.compress_longitude(mp_longitude)
                midpoints.append(
                    {
                        "planet1": p1,
                        "planet2": p2,
                        "true_deg": mp_dial,
                        "display_deg": mp_dial,  # Will be adjusted for collisions
                    }
                )

        # Apply collision detection (use smaller spacing for midpoints)
        midpoints = resolve_dial_collisions(
            midpoints,
            dial_degrees,
            min_spacing_360=6.0,  # Smaller spacing for midpoints (they're smaller)
        )

        # Draw midpoints
        for mp in midpoints:
            true_deg = mp["true_deg"]
            display_deg = mp["display_deg"]

            # Always draw tick mark at true position
            tick = renderer.draw_line_radial(
                dwg,
                true_deg,
                tick_inner,
                tick_outer,
                stroke=style.planet_tick_color,
                stroke_width=0.5,
            )
            dwg.add(tick)

            if self.notation == "tick":
                # Just tick marks, no labels
                continue

            # Draw connector if displaced
            displacement = _angular_distance(display_deg, true_deg, dial_degrees)
            if displacement > 0.3 * dial_degrees / 360:
                tick_x, tick_y = renderer.polar_to_cartesian(true_deg, tick_outer)
                label_x, label_y = renderer.polar_to_cartesian(
                    display_deg, midpoint_radius
                )

                connector = dwg.line(
                    start=(tick_x, tick_y),
                    end=(label_x, label_y),
                    stroke=style.planet_connector_color,
                    stroke_width=0.4,
                    stroke_dasharray="2,2",
                )
                dwg.add(connector)

            # Draw notation (e.g., "☉/☽")
            g1_info = get_glyph(mp["planet1"].name)
            g2_info = get_glyph(mp["planet2"].name)

            # For SVG glyphs, use first letter of planet name as fallback
            if g1_info["type"] == "svg":
                g1 = mp["planet1"].name[0]
            else:
                g1 = g1_info["value"]

            if g2_info["type"] == "svg":
                g2 = mp["planet2"].name[0]
            else:
                g2 = g2_info["value"]

            if self.notation == "full":
                label = f"{g1}/{g2}"
            else:  # abbreviated
                label = f"{g1[:1]}/{g2[:1]}"

            x, y = renderer.polar_to_cartesian(display_deg, midpoint_radius)

            dwg.add(
                dwg.text(
                    label,
                    insert=(x, y),
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_size="8px",
                    font_family=style.font_family_glyphs,
                    fill=style.planet_tick_color,
                )
            )

    def _calculate_midpoint(self, long1: float, long2: float) -> float:
        """Calculate the midpoint between two longitudes."""
        # Handle the shorter arc
        diff = abs(long2 - long1)
        if diff > 180:
            # Use the shorter arc
            mp = (long1 + long2) / 2 + 180
        else:
            mp = (long1 + long2) / 2

        return mp % 360


# =============================================================================
# Outer Ring Layer (for transits, directions, etc.)
# =============================================================================


class DialOuterRingLayer:
    """
    Generic outer ring layer for additional chart data.

    Can display transit planets, solar arc directions, progressions, etc.
    Each outer ring has:
    - Border circles defining the ring area
    - Tick marks at true positions
    - Glyphs with collision detection
    - Dashed connector lines when displaced
    """

    def __init__(
        self,
        positions: list[CelestialPosition],
        ring: str = "outer_ring_2",
        label: str = "",
        glyph_color: str | None = None,
    ):
        """
        Initialize outer ring layer.

        Args:
            positions: Celestial positions to display
            ring: Which outer ring to use
            label: Optional label for this ring
            glyph_color: Optional color override for glyphs
        """
        self.positions = positions
        self.ring = ring
        self.label = label
        self.glyph_color = glyph_color

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw positions on the outer ring with border, ticks, and collision detection."""
        style = renderer.style
        radii = renderer.radii
        dial_degrees = renderer.dial_degrees

        # Determine ring boundaries based on which ring we're using
        glyph_radius = radii[self.ring]

        # Calculate inner and outer borders for this ring
        # Each outer ring gets its own bordered area
        ring_width = 20  # Width of the ring area
        outer_border = glyph_radius + ring_width / 2
        inner_border = glyph_radius - ring_width / 2

        # Tick marks sit at the inner border
        tick_inner = inner_border - 2
        tick_outer = inner_border + 4

        glyph_color = self.glyph_color or style.planet_tick_color
        border_color = style.graduation_tick_color

        # Draw border circles for this ring
        dwg.add(
            renderer.draw_circle(
                dwg,
                outer_border,
                fill="none",
                stroke=border_color,
                stroke_width=0.5,
            )
        )
        dwg.add(
            renderer.draw_circle(
                dwg,
                inner_border,
                fill="none",
                stroke=border_color,
                stroke_width=0.5,
            )
        )

        # Convert positions to dial coordinates
        dial_positions = []
        for pos in self.positions:
            dial_deg = renderer.compress_longitude(pos.longitude)
            dial_positions.append(
                {
                    "position": pos,
                    "true_deg": dial_deg,
                    "display_deg": dial_deg,
                }
            )

        # Apply collision detection
        dial_positions = resolve_dial_collisions(
            dial_positions,
            dial_degrees,
            min_spacing_360=12.0,  # Slightly larger spacing for outer rings
        )

        # Draw tick marks, connectors, and glyphs
        for pos_data in dial_positions:
            pos = pos_data["position"]
            true_deg = pos_data["true_deg"]
            display_deg = pos_data["display_deg"]

            # Draw tick mark at true position
            tick = renderer.draw_line_radial(
                dwg,
                true_deg,
                tick_inner,
                tick_outer,
                stroke=glyph_color,
                stroke_width=0.8,
            )
            dwg.add(tick)

            # Draw connector if displaced
            displacement = _angular_distance(display_deg, true_deg, dial_degrees)
            if displacement > 0.3 * dial_degrees / 360:
                tick_x, tick_y = renderer.polar_to_cartesian(true_deg, tick_outer)
                glyph_x, glyph_y = renderer.polar_to_cartesian(
                    display_deg, glyph_radius
                )

                connector = dwg.line(
                    start=(tick_x, tick_y),
                    end=(glyph_x, glyph_y),
                    stroke=style.planet_connector_color,
                    stroke_width=0.5,
                    stroke_dasharray="2,2",
                )
                dwg.add(connector)

            # Draw glyph
            glyph_info = get_glyph(pos.name)
            x, y = renderer.polar_to_cartesian(display_deg, glyph_radius)

            if glyph_info["type"] == "svg":
                # Render inline SVG glyph
                glyph_size = 12.0  # Match font-size
                embed_svg_glyph(
                    dwg,
                    glyph_info["value"],
                    x,
                    y,
                    glyph_size,
                    fill_color=glyph_color,
                )
            else:
                # Render Unicode text glyph
                dwg.add(
                    dwg.text(
                        glyph_info["value"],
                        insert=(x, y),
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_size="12px",
                        font_family=style.font_family_glyphs,
                        fill=glyph_color,
                    )
                )


# =============================================================================
# Pointer Layer (for 360° dial)
# =============================================================================


class DialPointerLayer:
    """
    Renders the rotatable pointer for 360° dials.

    The pointer is a double-ended arrow that can point to any degree.
    """

    def __init__(self, pointing_to: float = 0.0):
        """
        Initialize pointer layer.

        Args:
            pointing_to: Dial degree to point to (0-360 for 360° dial)
        """
        self.pointing_to = pointing_to

    def render(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """Draw the pointer arrow."""
        config = renderer.config
        style = renderer.style
        radii = renderer.radii
        pointer_config = config.pointer

        # Pointer extends from center to near the graduation ring
        outer_r = radii["graduation_inner"] - 10

        # Draw main line through center
        x1, y1 = renderer.polar_to_cartesian(self.pointing_to, outer_r)
        x2, y2 = renderer.polar_to_cartesian(self.pointing_to + 180, outer_r)

        line = dwg.line(
            start=(x1, y1),
            end=(x2, y2),
            stroke=style.pointer_color,
            stroke_width=pointer_config.width,
        )
        dwg.add(line)

        # Draw arrow heads at both ends
        self._draw_arrow_head(
            renderer, dwg, self.pointing_to, outer_r, style, pointer_config
        )
        self._draw_arrow_head(
            renderer, dwg, self.pointing_to + 180, outer_r, style, pointer_config
        )

        # Draw center circle
        if pointer_config.show_center_circle:
            dwg.add(
                dwg.circle(
                    center=(renderer.center, renderer.center),
                    r=pointer_config.center_circle_radius,
                    fill="none",
                    stroke=style.pointer_color,
                    stroke_width=pointer_config.width,
                )
            )

    def _draw_arrow_head(
        self,
        renderer: DialRenderer,
        dwg: svgwrite.Drawing,
        deg: float,
        radius: float,
        style: DialStyle,
        config,
    ) -> None:
        """Draw an arrow head at the given position."""
        tip_x, tip_y = renderer.polar_to_cartesian(deg, radius)

        # Get SVG angle for arrow direction
        svg_angle = renderer.dial_to_svg_angle(deg)
        angle_rad = math.radians(svg_angle)

        # Arrow head wings
        wing_angle = math.radians(25)
        wing_length = config.arrow_size

        # Wings point back toward center
        wing1_x = tip_x - wing_length * math.cos(angle_rad + wing_angle)
        wing1_y = tip_y - wing_length * math.sin(angle_rad + wing_angle)
        wing2_x = tip_x - wing_length * math.cos(angle_rad - wing_angle)
        wing2_y = tip_y - wing_length * math.sin(angle_rad - wing_angle)

        arrow_head = dwg.polygon(
            points=[(tip_x, tip_y), (wing1_x, wing1_y), (wing2_x, wing2_y)],
            fill=style.pointer_color,
        )
        dwg.add(arrow_head)
