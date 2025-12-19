"""
Dial Chart Renderer (stellium.visualization.dial.renderer)

Core coordinate system and rendering context for dial charts.
Similar to ChartRenderer but with longitude compression for 90°/45°/360° dials.
"""

import math
from typing import Any

import svgwrite

from stellium.visualization.dial.config import DialConfig


class DialRenderer:
    """
    Core renderer for dial chart visualization.

    Provides coordinate transformation for compressed dial charts
    (90°, 45°, or 360°). The dial compresses the zodiac so that
    hard aspects appear as conjunctions.

    For a 90° dial:
    - 0° Aries, Cancer, Libra, Capricorn all map to 0° on the dial
    - 0° Taurus, Leo, Scorpio, Aquarius all map to 30° on the dial
    - 0° Gemini, Virgo, Sagittarius, Pisces all map to 60° on the dial

    The coordinate system places 0° at the top (12 o'clock) and
    progresses clockwise.
    """

    def __init__(self, config: DialConfig):
        """
        Initialize the dial renderer.

        Args:
            config: DialConfig with all dial settings and theme
        """
        self.config = config
        self.dial_degrees = config.dial_degrees
        self.size = config.size
        self.rotation = config.rotation

        # Header support: when header is enabled, canvas is taller
        # and dial center is offset down
        self.header_height = config.header.height if config.show_header else 0
        self.canvas_height = config.size + self.header_height

        # Center is in the middle of the dial area (below header)
        self.center = config.size // 2
        self.center_y = self.header_height + self.center

        # Get radii in absolute pixels
        self.radii = config.radii.to_absolute(config.size)

        # Get theme-derived style
        self.style = config.get_dial_style()

    def compress_longitude(self, longitude: float) -> float:
        """
        Compress 360° zodiac longitude to dial degrees.

        Args:
            longitude: Zodiac longitude (0-360°)

        Returns:
            Compressed dial position (0 to dial_degrees)

        Examples:
            For 90° dial:
            - 0° (Aries) → 0°
            - 90° (Cancer) → 0°
            - 180° (Libra) → 0°
            - 270° (Capricorn) → 0°
            - 45° (mid-Taurus) → 45°
            - 135° (mid-Leo) → 45°
        """
        return longitude % self.dial_degrees

    def dial_to_svg_angle(self, dial_deg: float) -> float:
        """
        Convert dial degrees to SVG angle.

        SVG coordinate system:
        - 0° = 3 o'clock (right)
        - 90° = 6 o'clock (bottom)
        - Angles increase clockwise

        Dial coordinate system:
        - 0° = 12 o'clock (top)
        - Angles increase clockwise
        - Rotation shifts where 0° appears

        Args:
            dial_deg: Position on the dial (0 to dial_degrees)

        Returns:
            SVG angle in degrees (0-360)
        """
        # Apply rotation
        rotated = (dial_deg - self.rotation) % self.dial_degrees

        # Scale to 360° for SVG (e.g., 90° dial → multiply by 4)
        scale_factor = 360 / self.dial_degrees
        scaled = rotated * scale_factor

        # Convert from dial coordinates (0° at top) to SVG (0° at right)
        # Dial 0° (top) = SVG 270°
        # Dial 90° (right on 360° dial) = SVG 0°
        svg_angle = (scaled + 270) % 360

        return svg_angle

    def polar_to_cartesian(self, dial_deg: float, radius: float) -> tuple[float, float]:
        """
        Convert dial degree and radius to (x, y) cartesian coordinates.

        Args:
            dial_deg: Position on the dial (0 to dial_degrees, or any value
                     which will be taken modulo dial_degrees)
            radius: Distance from center in pixels

        Returns:
            Tuple of (x, y) coordinates
        """
        svg_angle = self.dial_to_svg_angle(dial_deg)
        svg_angle_rad = math.radians(svg_angle)

        # SVG y-axis is inverted (positive = down)
        # Use center for x, center_y for y (accounts for header offset)
        x = self.center + radius * math.cos(svg_angle_rad)
        y = self.center_y + radius * math.sin(svg_angle_rad)

        return x, y

    def longitude_to_cartesian(
        self, longitude: float, radius: float
    ) -> tuple[float, float]:
        """
        Convert zodiac longitude directly to cartesian coordinates.

        Convenience method that compresses longitude and converts to cartesian
        in one step.

        Args:
            longitude: Zodiac longitude (0-360°)
            radius: Distance from center in pixels

        Returns:
            Tuple of (x, y) coordinates
        """
        dial_deg = self.compress_longitude(longitude)
        return self.polar_to_cartesian(dial_deg, radius)

    def create_drawing(self) -> svgwrite.Drawing:
        """
        Create the SVG drawing with background.

        Returns:
            svgwrite.Drawing ready for layers to render into
        """
        dwg = svgwrite.Drawing(
            filename=self.config.filename,
            size=(f"{self.size}px", f"{self.canvas_height}px"),
            viewBox=f"0 0 {self.size} {self.canvas_height}",
            profile="full",
        )

        # Add background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(f"{self.size}px", f"{self.canvas_height}px"),
                fill=self.style.background_color,
            )
        )

        return dwg

    def draw_arc(
        self,
        dwg: svgwrite.Drawing,
        start_deg: float,
        end_deg: float,
        radius: float,
        **kwargs: Any,
    ) -> svgwrite.path.Path:
        """
        Draw an arc on the dial.

        Args:
            dwg: SVG drawing
            start_deg: Start position in dial degrees
            end_deg: End position in dial degrees
            radius: Radius of the arc
            **kwargs: Additional SVG path attributes (stroke, fill, etc.)

        Returns:
            SVG path element
        """
        x1, y1 = self.polar_to_cartesian(start_deg, radius)
        x2, y2 = self.polar_to_cartesian(end_deg, radius)

        # Determine if this is a large arc (> 180° in SVG terms)
        arc_span = (end_deg - start_deg) % self.dial_degrees
        svg_span = arc_span * (360 / self.dial_degrees)
        large_arc = 1 if svg_span > 180 else 0

        # SVG arc: A rx ry x-axis-rotation large-arc-flag sweep-flag x y
        # sweep-flag=1 for clockwise
        d = f"M {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2}"

        path = dwg.path(d=d, **kwargs)
        return path

    def draw_line_radial(
        self,
        dwg: svgwrite.Drawing,
        dial_deg: float,
        inner_radius: float,
        outer_radius: float,
        **kwargs: Any,
    ) -> svgwrite.shapes.Line:
        """
        Draw a radial line from inner to outer radius at a given dial degree.

        Args:
            dwg: SVG drawing
            dial_deg: Position in dial degrees
            inner_radius: Inner radius in pixels
            outer_radius: Outer radius in pixels
            **kwargs: Additional SVG line attributes

        Returns:
            SVG line element
        """
        x1, y1 = self.polar_to_cartesian(dial_deg, inner_radius)
        x2, y2 = self.polar_to_cartesian(dial_deg, outer_radius)

        line = dwg.line(start=(x1, y1), end=(x2, y2), **kwargs)
        return line

    def draw_circle(
        self,
        dwg: svgwrite.Drawing,
        radius: float,
        **kwargs: Any,
    ) -> svgwrite.shapes.Circle:
        """
        Draw a circle centered on the dial.

        Args:
            dwg: SVG drawing
            radius: Circle radius in pixels
            **kwargs: Additional SVG circle attributes

        Returns:
            SVG circle element
        """
        circle = dwg.circle(center=(self.center, self.center_y), r=radius, **kwargs)
        return circle

    def get_cardinal_points(self) -> list[float]:
        """
        Get the cardinal point positions for this dial size.

        For 90° dial: 0°, 22.5°, 45°, 67.5°
        For 45° dial: 0°, 11.25°, 22.5°, 33.75°
        For 360° dial: 0°, 90°, 180°, 270°

        Returns:
            List of dial degrees for cardinal points
        """
        # Cardinal points divide the dial into 4 equal parts
        quarter = self.dial_degrees / 4
        return [0, quarter, quarter * 2, quarter * 3]

    def get_modality_sectors(self) -> list[tuple[float, float, str]]:
        """
        Get the modality sector definitions for this dial.

        For 90° dial, each 30° sector represents one modality:
        - 0°-30°: Cardinal (Aries, Cancer, Libra, Capricorn)
        - 30°-60°: Fixed (Taurus, Leo, Scorpio, Aquarius)
        - 60°-90°: Mutable (Gemini, Virgo, Sagittarius, Pisces)

        Returns:
            List of (start_deg, end_deg, modality_name) tuples
        """
        sector_size = self.dial_degrees / 3
        return [
            (0, sector_size, "Cardinal"),
            (sector_size, sector_size * 2, "Fixed"),
            (sector_size * 2, self.dial_degrees, "Mutable"),
        ]
