"""
Concrete Render Layers (stellium.visualization.layers)

These are the concrete implementations of the IRenderLayer protocol.
Each class knows how to draw one specific part of a chart,
reading its data from the CalculatedChart object.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    HouseCusps,
    UnknownTimeChart,
)

from .core import (
    ANGLE_GLYPHS,
    ZODIAC_GLYPHS,
    ChartRenderer,
    embed_svg_glyph,
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


class HeaderLayer:
    """
    Renders the chart header band at the top of the canvas.

    Displays native information prominently:
    - Single chart: Name, location, datetime, timezone, coordinates
    - Biwheel: Two-column layout with chart1 info left-aligned, chart2 right-aligned
    - Synthesis: "Composite: Name1 & Name2" or "Davison: Name1 & Name2" with midpoint info

    The header uses Baskerville italic-semibold for names (elegant, classical feel)
    and the normal text font for details.
    """

    def __init__(
        self,
        height: int = 70,
        name_font_size: str = "18px",
        name_font_family: str = "Baskerville, 'Libre Baskerville', Georgia, serif",
        name_font_weight: str = "600",  # Semibold (falls back to bold if unavailable)
        name_font_style: str = "italic",
        details_font_size: str = "12px",
        line_height: int = 16,
        coord_precision: int = 4,
    ) -> None:
        """
        Initialize header layer.

        Args:
            height: Header height in pixels
            name_font_size: Font size for name(s)
            name_font_family: Font family for name(s)
            name_font_weight: Font weight for name(s) - "600" for semibold, "bold" for bold
            name_font_style: Font style for name(s) - "italic" or "normal"
            details_font_size: Font size for details
            line_height: Line height for detail rows
            coord_precision: Decimal places for coordinates
        """
        self.height = height
        self.name_font_size = name_font_size
        self.name_font_family = name_font_family
        self.name_font_weight = name_font_weight
        self.name_font_style = name_font_style
        self.details_font_size = details_font_size
        self.line_height = line_height
        self.coord_precision = coord_precision

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        """Render the header band."""
        from stellium.core.comparison import Comparison
        from stellium.core.multichart import MultiChart
        from stellium.core.multiwheel import MultiWheel
        from stellium.core.synthesis import SynthesisChart

        # Get theme colors
        style = renderer.style
        planet_style = style.get("planets", {})
        name_color = planet_style.get("glyph_color", "#222222")
        info_color = planet_style.get("info_color", "#333333")

        # Header renders at the TOP of the canvas, not relative to wheel position
        # Use a fixed margin for the header area
        margin = renderer.size * 0.03

        # Header spans the full wheel width, positioned at top of canvas
        # Note: x_offset accounts for extended canvas, but header should align with wheel
        x_offset = getattr(renderer, "x_offset", 0)

        header_left = x_offset + margin
        header_right = x_offset + renderer.size - margin
        header_top = margin  # Start at top of canvas, not offset by wheel position!
        header_width = header_right - header_left

        # Dispatch to appropriate renderer based on chart type
        if isinstance(chart, SynthesisChart):
            self._render_synthesis_header(
                dwg,
                chart,
                header_left,
                header_right,
                header_top,
                header_width,
                name_color,
                info_color,
                renderer,
            )
        elif isinstance(chart, MultiChart):
            # MultiChart uses the same header rendering as MultiWheel
            self._render_multiwheel_header(
                dwg,
                chart,
                header_left,
                header_right,
                header_top,
                header_width,
                name_color,
                info_color,
                renderer,
            )
        elif isinstance(chart, MultiWheel):
            # For multiwheel, render using innermost chart's info
            self._render_multiwheel_header(
                dwg,
                chart,
                header_left,
                header_right,
                header_top,
                header_width,
                name_color,
                info_color,
                renderer,
            )
        elif isinstance(chart, Comparison):
            self._render_comparison_header(
                dwg,
                chart,
                header_left,
                header_right,
                header_top,
                header_width,
                name_color,
                info_color,
                renderer,
            )
        else:
            self._render_single_header(
                dwg,
                chart,
                header_left,
                header_right,
                header_top,
                header_width,
                name_color,
                info_color,
                renderer,
            )

    def _parse_location_name(self, location_name: str) -> tuple[str, str | None]:
        """
        Parse a geopy location string into a short name and country.

        Args:
            location_name: Full location string like "Palo Alto, Santa Clara County, California, United States of America"

        Returns:
            Tuple of (short_name, country) where short_name is "City, State/Region"
            and country is the last part (or None if it looks like USA)
        """
        if not location_name:
            return ("", None)

        parts = [p.strip() for p in location_name.split(",")]

        if len(parts) <= 2:
            # Already short enough
            return (location_name, None)

        # First part is usually city
        city = parts[0]

        # Last part is usually country
        country = parts[-1]

        # Try to find state/region (usually second-to-last or third-to-last)
        # Skip things like "County" parts
        region = None
        for part in reversed(parts[1:-1]):
            if "county" not in part.lower():
                region = part
                break

        # Build short name
        if region:
            short_name = f"{city}, {region}"
        else:
            short_name = city

        # Skip country for common cases
        skip_countries = ["United States of America", "United States", "USA", "US"]
        if country in skip_countries:
            country = None

        return (short_name, country)

    def _render_single_header(
        self,
        dwg,
        chart,
        left: float,
        right: float,
        top: float,
        width: float,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render header for a single natal chart."""
        # Get native info
        name = chart.metadata.get("name") if hasattr(chart, "metadata") else None

        current_y = top

        # Name (big, italic-semibold, Baskerville)
        if name:
            dwg.add(
                dwg.text(
                    name,
                    insert=(left, current_y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.name_font_size,
                    fill=name_color,
                    font_family=self.name_font_family,
                    font_weight=self.name_font_weight,
                    font_style=self.name_font_style,
                )
            )
            current_y += int(float(self.name_font_size[:-2]) * 1.3)

        # Line 2: Location (short) + coordinates
        if chart.location:
            location_name = getattr(chart.location, "name", None)
            short_name, country = self._parse_location_name(location_name)

            # Build location line with coordinates
            lat = chart.location.latitude
            lon = chart.location.longitude
            lat_dir = "N" if lat >= 0 else "S"
            lon_dir = "E" if lon >= 0 else "W"
            coord_str = f"({abs(lat):.{self.coord_precision}f}°{lat_dir}, {abs(lon):.{self.coord_precision}f}°{lon_dir})"

            if short_name:
                location_line = f"{short_name} · {coord_str}"
            else:
                location_line = coord_str

            dwg.add(
                dwg.text(
                    location_line,
                    insert=(left, current_y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.details_font_size,
                    fill=info_color,
                    font_family=renderer.style["font_family_text"],
                )
            )
            current_y += self.line_height

        # Line 3: Datetime + timezone
        datetime_parts = []

        if chart.datetime:
            is_unknown_time = isinstance(chart, UnknownTimeChart)

            if is_unknown_time:
                if chart.datetime.local_datetime:
                    dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y")
                else:
                    dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y")
                dt_str += " (Time Unknown)"
            elif chart.datetime.local_datetime:
                dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y %I:%M %p")
            else:
                dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y %H:%M UTC")

            datetime_parts.append(dt_str)

        # Add timezone + UTC offset
        if chart.location:
            timezone = getattr(chart.location, "timezone", None)
            if timezone:
                tz_str = timezone
                if chart.datetime and chart.datetime.local_datetime:
                    try:
                        utc_offset = chart.datetime.local_datetime.strftime("%z")
                        if utc_offset:
                            sign = utc_offset[0]
                            hours = int(utc_offset[1:3])
                            minutes = int(utc_offset[3:5])
                            if minutes:
                                offset_str = f"UTC{sign}{hours}:{minutes:02d}"
                            else:
                                offset_str = f"UTC{sign}{hours}"
                            tz_str = f"{timezone} ({offset_str})"
                    except Exception:
                        pass
                datetime_parts.append(tz_str)

        if datetime_parts:
            datetime_line = " · ".join(datetime_parts)
            dwg.add(
                dwg.text(
                    datetime_line,
                    insert=(left, current_y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.details_font_size,
                    fill=info_color,
                    font_family=renderer.style["font_family_text"],
                )
            )

    def _render_comparison_header(
        self,
        dwg,
        chart,
        left: float,
        right: float,
        top: float,
        width: float,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render two-column header for comparison/biwheel chart."""
        # Calculate column boundaries with padding in the middle
        # Each column gets ~45% of width, with 10% gap in the middle
        col_width = width * 0.45
        left_col_right = left + col_width
        right_col_left = right - col_width

        # Left column: chart1 (inner wheel) - left aligned
        self._render_chart_column(
            dwg,
            chart.chart1,
            left,
            left_col_right,
            top,
            "start",
            name_color,
            info_color,
            renderer,
        )

        # Right column: chart2 (outer wheel) - right aligned
        self._render_chart_column(
            dwg,
            chart.chart2,
            right_col_left,
            right,
            top,
            "end",
            name_color,
            info_color,
            renderer,
        )

    def _render_chart_column(
        self,
        dwg,
        chart,
        col_left: float,
        col_right: float,
        top: float,
        anchor: str,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render a single column of chart info (used for biwheel headers)."""
        current_y = top

        # Determine x position based on anchor
        x = col_left if anchor == "start" else col_right

        # Name
        name = chart.metadata.get("name") if hasattr(chart, "metadata") else None
        if name:
            dwg.add(
                dwg.text(
                    name,
                    insert=(x, current_y),
                    text_anchor=anchor,
                    dominant_baseline="hanging",
                    font_size=self.name_font_size,
                    fill=name_color,
                    font_family=self.name_font_family,
                    font_weight=self.name_font_weight,
                    font_style=self.name_font_style,
                )
            )
            current_y += int(float(self.name_font_size[:-2]) * 1.3)

        # Location (short name only)
        if chart.location:
            location_name = getattr(chart.location, "name", None)
            short_name, _ = self._parse_location_name(location_name)
            if short_name:
                dwg.add(
                    dwg.text(
                        short_name,
                        insert=(x, current_y),
                        text_anchor=anchor,
                        dominant_baseline="hanging",
                        font_size=self.details_font_size,
                        fill=info_color,
                        font_family=renderer.style["font_family_text"],
                    )
                )
                current_y += self.line_height

        # Date/time
        if chart.datetime:
            is_unknown_time = isinstance(chart, UnknownTimeChart)

            if is_unknown_time:
                if chart.datetime.local_datetime:
                    dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y")
                else:
                    dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y")
                dt_str += " (Time Unknown)"
            elif chart.datetime.local_datetime:
                dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y %I:%M %p")
            else:
                dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y %H:%M UTC")

            dwg.add(
                dwg.text(
                    dt_str,
                    insert=(x, current_y),
                    text_anchor=anchor,
                    dominant_baseline="hanging",
                    font_size=self.details_font_size,
                    fill=info_color,
                    font_family=renderer.style["font_family_text"],
                )
            )

    def _render_multiwheel_header(
        self,
        dwg,
        chart,  # MultiWheel
        left: float,
        right: float,
        top: float,
        width: float,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render header for multiwheel chart.

        For 2 charts: Side-by-side layout like comparison charts
        For 3-4 charts: Horizontal compact layout with all chart info
        """
        chart_count = chart.chart_count

        if chart_count == 2:
            # Use side-by-side layout like comparison charts
            col_width = width / 2
            right_col_left = left + col_width

            # Left column: chart1 (inner wheel)
            self._render_chart_column(
                dwg,
                chart.charts[0],
                left,
                left + col_width - 10,
                top,
                "start",
                name_color,
                info_color,
                renderer,
            )

            # Right column: chart2 (outer wheel) - right aligned
            self._render_chart_column(
                dwg,
                chart.charts[1],
                right_col_left,
                right,
                top,
                "end",
                name_color,
                info_color,
                renderer,
            )
        else:
            # For 3-4 charts: compact horizontal layout
            self._render_multiwheel_compact_header(
                dwg,
                chart,
                left,
                right,
                top,
                width,
                name_color,
                info_color,
                renderer,
            )

    def _render_multiwheel_compact_header(
        self,
        dwg,
        chart,  # MultiWheel
        left: float,
        right: float,
        top: float,
        width: float,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render compact header for 3-4 chart multiwheels.

        Shows each chart's label and date in a horizontal row.
        """
        current_y = top
        chart_count = chart.chart_count

        # Calculate column width for each chart
        col_width = width / chart_count
        small_font_size = "11px"

        for i, inner_chart in enumerate(chart.charts):
            col_left = left + (i * col_width)
            col_center = col_left + (col_width / 2)

            # Get label (from multiwheel labels or chart metadata)
            if chart.labels and i < len(chart.labels):
                label = chart.labels[i]
            else:
                name = (
                    inner_chart.metadata.get("name")
                    if hasattr(inner_chart, "metadata")
                    else None
                )
                label = name or f"Chart {i + 1}"

            # Chart label (bold, centered in column)
            dwg.add(
                dwg.text(
                    label,
                    insert=(col_center, current_y),
                    text_anchor="middle",
                    dominant_baseline="hanging",
                    font_size="14px",
                    fill=name_color,
                    font_family=self.name_font_family,
                    font_weight="600",
                    font_style=self.name_font_style,
                )
            )

        # Second row: locations
        current_y += 18
        for i, inner_chart in enumerate(chart.charts):
            col_left = left + (i * col_width)
            col_center = col_left + (col_width / 2)

            if inner_chart.location:
                short_name, _ = self._parse_location_name(inner_chart.location.name)
                if short_name:
                    dwg.add(
                        dwg.text(
                            short_name,
                            insert=(col_center, current_y),
                            text_anchor="middle",
                            dominant_baseline="hanging",
                            font_size=small_font_size,
                            fill=info_color,
                            font_family=renderer.style["font_family_text"],
                        )
                    )

        # Third row: dates with times
        current_y += 14
        for i, inner_chart in enumerate(chart.charts):
            col_left = left + (i * col_width)
            col_center = col_left + (col_width / 2)

            if inner_chart.datetime:
                is_unknown_time = isinstance(inner_chart, UnknownTimeChart)
                if is_unknown_time:
                    if inner_chart.datetime.local_datetime:
                        dt_str = inner_chart.datetime.local_datetime.strftime(
                            "%b %d, %Y"
                        )
                    else:
                        dt_str = inner_chart.datetime.utc_datetime.strftime("%b %d, %Y")
                    dt_str += " (Unknown)"
                elif inner_chart.datetime.local_datetime:
                    dt_str = inner_chart.datetime.local_datetime.strftime(
                        "%b %d, %Y %I:%M %p"
                    )
                else:
                    dt_str = inner_chart.datetime.utc_datetime.strftime(
                        "%b %d, %Y %H:%M UTC"
                    )

                dwg.add(
                    dwg.text(
                        dt_str,
                        insert=(col_center, current_y),
                        text_anchor="middle",
                        dominant_baseline="hanging",
                        font_size=small_font_size,
                        fill=info_color,
                        font_family=renderer.style["font_family_text"],
                    )
                )

    def _render_synthesis_header(
        self,
        dwg,
        chart,
        left: float,
        right: float,
        top: float,
        width: float,
        name_color: str,
        info_color: str,
        renderer,
    ) -> None:
        """Render header for synthesis (composite/davison) chart."""
        current_y = top

        # Get synthesis type and labels
        synthesis_method = getattr(chart, "synthesis_method", "Composite")
        label1 = getattr(chart, "chart1_label", None)
        label2 = getattr(chart, "chart2_label", None)

        # Capitalize synthesis method for display
        method_display = synthesis_method.title() if synthesis_method else "Synthesis"

        # Title: "Composite: Alice & Bob" or "Davison: Alice & Bob"
        # Skip default labels like "Chart 1" and "Chart 2"
        if label1 and label2 and label1 != "Chart 1" and label2 != "Chart 2":
            title = f"{method_display}: {label1} & {label2}"
        else:
            title = f"{method_display} Chart"

        dwg.add(
            dwg.text(
                title,
                insert=(left, current_y),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size=self.name_font_size,
                fill=name_color,
                font_family=self.name_font_family,
                font_weight=self.name_font_weight,
                font_style=self.name_font_style,
            )
        )
        current_y += int(float(self.name_font_size[:-2]) * 1.3)

        # Midpoint location line
        if chart.location:
            lat = chart.location.latitude
            lon = chart.location.longitude
            lat_dir = "N" if lat >= 0 else "S"
            lon_dir = "E" if lon >= 0 else "W"
            coord_str = f"{abs(lat):.{self.coord_precision}f}°{lat_dir}, {abs(lon):.{self.coord_precision}f}°{lon_dir}"

            # For midpoint charts, just show coordinates (the "name" is usually just raw coords anyway)
            location_line = f"Midpoint: {coord_str}"

            dwg.add(
                dwg.text(
                    location_line,
                    insert=(left, current_y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.details_font_size,
                    fill=info_color,
                    font_family=renderer.style["font_family_text"],
                )
            )
            current_y += self.line_height

        # Datetime line (for Davison charts especially)
        if chart.datetime and chart.datetime.local_datetime:
            dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y %I:%M %p")
            dwg.add(
                dwg.text(
                    dt_str,
                    insert=(left, current_y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.details_font_size,
                    fill=info_color,
                    font_family=renderer.style["font_family_text"],
                )
            )


class ZodiacLayer:
    """Renders the outer Zodiac ring, including glyphs and tick marks."""

    def __init__(
        self,
        palette: ZodiacPalette | str = ZodiacPalette.GREY,
        style_override: dict[str, Any] | None = None,
        show_degree_ticks: bool = False,
    ) -> None:
        """
        Initialize the zodiac layer.

        Args:
            palette: The color palette to use (ZodiacPalette enum, palette name, or "single_color:#RRGGBB")
            style_override: Optional style overrides
            show_degree_ticks: If True, show 1° tick marks between the 5° marks
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
        self.show_degree_ticks = show_degree_ticks

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

        # Draw degree tick marks
        # Use angles line color for all tick marks
        tick_color = renderer.style["angles"]["line_color"]
        for sign_index in range(12):
            sign_start = sign_index * 30.0

            # Determine which degrees to draw ticks for
            # Always draw at 5°, 10°, 15°, 20°, 25° (0° is handled by sign boundary lines)
            # Optionally draw 1° ticks for all other degrees
            if self.show_degree_ticks:
                degrees_to_draw = list(range(1, 30))  # 1-29 (skip 0)
            else:
                degrees_to_draw = [5, 10, 15, 20, 25]

            for degree_in_sign in degrees_to_draw:
                absolute_degree = sign_start + degree_in_sign

                # Tick sizing hierarchy: 10°/20° > 5°/15°/25° > 1° ticks
                if degree_in_sign in [10, 20]:
                    tick_length = 10
                    tick_width = 0.8
                elif degree_in_sign in [5, 15, 25]:
                    tick_length = 7
                    tick_width = 0.5
                else:  # 1° ticks (smallest)
                    tick_length = 4
                    tick_width = 0.3

                # Draw tick from zodiac_ring_inner outward
                x_inner, y_inner = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_inner"]
                )
                x_outer, y_outer = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_inner"] + tick_length
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


class RingBoundaryLayer:
    """
    Renders circular boundary lines between chart rings in a multiwheel chart.

    Draws circles at the boundaries between:
    - Each chart ring (chart1_ring_outer, chart2_ring_outer, etc.)
    - The outermost chart and the zodiac ring (zodiac_ring_inner)

    Uses the theme's ring_border styling for color and width.
    """

    def __init__(
        self,
        chart_count: int = 2,
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            chart_count: Number of charts in the multiwheel (2, 3, or 4)
            style_override: Optional style overrides for border color/width
        """
        self.chart_count = chart_count
        self.style = style_override or {}

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render ring boundary circles."""
        # Get ring border styling from theme (with fallbacks)
        style = renderer.style.get("ring_border", {})
        style = {**style, **self.style}  # Apply overrides

        # Use houses line color as default (matches house cusp lines)
        default_color = renderer.style.get("houses", {}).get(
            "line_color", renderer.style.get("border_color", "#CCCCCC")
        )
        border_color = style.get("color", default_color)
        border_width = style.get("width", 1.0)

        # Collect the radii where we need to draw boundaries (using set to avoid duplicates)
        boundary_radii = set()

        # Add boundary at each chart ring's outer edge
        for chart_num in range(1, self.chart_count + 1):
            ring_outer_key = f"chart{chart_num}_ring_outer"
            if ring_outer_key in renderer.radii:
                boundary_radii.add(renderer.radii[ring_outer_key])

        # Add boundary at zodiac ring inner edge (between outermost chart and zodiac)
        if "zodiac_ring_inner" in renderer.radii:
            boundary_radii.add(renderer.radii["zodiac_ring_inner"])

        # Draw circular boundaries
        # Center coordinates account for any canvas offsets
        cx = renderer.x_offset + renderer.center
        cy = renderer.y_offset + renderer.center
        for radius in boundary_radii:
            dwg.add(
                dwg.circle(
                    center=(cx, cy),
                    r=radius,
                    fill="none",
                    stroke=border_color,
                    stroke_width=border_width,
                )
            )


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


class ChartInfoLayer:
    """
    Renders chart metadata information in a corner of the chart.

    When header is disabled: displays all native info (name, location, datetime, etc.)
    When header is enabled: displays only calculation settings (house system, ephemeris)
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "text_size": "11px",
        "line_height": 14,  # Pixels between lines
        "font_weight": "normal",
        "name_size": "16px",  # Larger font for name
        "name_weight": "bold",  # Bold weight for name
    }

    # Fields that should only appear if header is disabled
    NATIVE_INFO_FIELDS = {"name", "location", "datetime", "timezone", "coordinates"}

    # Fields that always appear (calculation settings)
    CALCULATION_FIELDS = {"house_system", "ephemeris"}

    def __init__(
        self,
        position: str = "top-left",
        fields: list[str] | None = None,
        style_override: dict[str, Any] | None = None,
        house_systems: list[str] | None = None,
        header_enabled: bool = False,
    ) -> None:
        """
        Initialize chart info layer.

        Args:
            position: Where to place the info block.
                Options: "top-left", "top-right", "bottom-left", "bottom-right"
            fields: List of fields to display. Options:
                "name", "location", "datetime", "timezone", "coordinates",
                "house_system", "ephemeris"
                If None, displays all relevant fields based on header_enabled.
            style_override: Optional style overrides
            house_systems: List of house system names being rendered on the chart.
                If provided, will display all systems instead of just the default.
            header_enabled: If True, only show calculation settings (house system, ephemeris).
                Native info (name, location, datetime) is in the header instead.
        """
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right"]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position: {position}. Must be one of {valid_positions}"
            )

        self.position = position
        self.header_enabled = header_enabled

        if fields is not None:
            # User specified fields explicitly
            self.fields = fields
        elif header_enabled:
            # Header is on - only show calculation settings
            self.fields = ["house_system", "ephemeris"]
        else:
            # Header is off - show everything
            self.fields = [
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
        # Only show name if header is disabled and "name" is in fields
        if self.header_enabled:
            name = None  # Name is in header, not here
        else:
            name = chart.metadata.get("name") if hasattr(chart, "metadata") else None
            # Only show name if it's in the fields list
            if "name" not in self.fields:
                name = None

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

        # Get theme-aware text color from planets info_color
        theme_text_color = renderer.style.get("planets", {}).get(
            "info_color", self.style["text_color"]
        )
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            theme_text_color, background_color, min_contrast=4.5
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

        The y_offset already accounts for header positioning (it's the wheel's
        top-left corner), so we just add margin for the corner positions.

        Args:
            renderer: ChartRenderer instance
            num_lines: Number of text lines to display

        Returns:
            Tuple of (x, y) coordinates
        """
        # Base margin - match the chart's own padding
        # zodiac_ring_outer is at radius 0.47 * size from center
        # center is at size/2, so padding = size/2 - 0.47 * size = 0.03 * size
        base_margin = renderer.size * 0.03
        total_height = num_lines * self.style["line_height"]

        # Get offsets for extended canvas positioning
        # Note: y_offset already includes header height (it's the wheel's top-left position)
        x_offset = getattr(renderer, "x_offset", 0)
        y_offset = getattr(renderer, "y_offset", 0)

        # Manual adjustments for specific corners to move them away from wheel
        if self.position == "top-left":
            return (x_offset + base_margin, y_offset + base_margin)
        elif self.position == "top-right":
            # Aspect counter: reduce margin to push further away
            margin = base_margin * 0.3  # Reduced from base to push outward
            return (x_offset + renderer.size - margin, y_offset + margin)
        elif self.position == "bottom-left":
            # Element modality: reduce margin to push further away
            margin = base_margin * 0.3  # Reduced from base to push outward
            return (x_offset + margin, y_offset + renderer.size - margin - total_height)
        elif self.position == "bottom-right":
            return (
                x_offset + renderer.size - base_margin,
                y_offset + renderer.size - base_margin - total_height,
            )
        else:
            # Fallback to top-left
            return (x_offset + base_margin, y_offset + base_margin)


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
        from stellium.core.registry import get_aspect_info

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
                glyph = None  # No glyph, just use text

            # Get the color for this aspect (for legend)
            aspect_style = aspect_style_dict.get(
                aspect_name, aspect_style_dict.get("default", {})
            )
            if isinstance(aspect_style, dict):
                aspect_color = aspect_style.get("color", "#888888")
            else:
                aspect_color = "#888888"

            # Store glyph separately for proper font rendering
            lines.append((glyph, f"{aspect_name}: {count}", aspect_color))

        # Calculate position
        x, y = self._get_position_coordinates(renderer, len(lines))

        # Determine text anchor based on position
        if "right" in self.position:
            text_anchor = "end"
        else:
            text_anchor = "start"

        # Get theme-aware text color for header from planets info_color
        theme_text_color = renderer.style.get("planets", {}).get(
            "info_color", self.style["text_color"]
        )
        background_color = renderer.style.get("background_color", "#FFFFFF")
        header_color = adjust_color_for_contrast(
            theme_text_color, background_color, min_contrast=4.5
        )

        # Render each line
        glyph_width = 14  # Approximate width for a glyph
        glyph_y_offset = -2  # Nudge glyphs up to align with text baseline

        for i, line_data in enumerate(lines):
            line_y = y + (i * self.style["line_height"])
            font_weight = (
                self.style["title_weight"] if i == 0 else self.style["font_weight"]
            )

            # Header line: (text, None) format
            if i == 0:
                line_text, _ = line_data
                dwg.add(
                    dwg.text(
                        line_text,
                        insert=(x, line_y),
                        text_anchor=text_anchor,
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=header_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=font_weight,
                    )
                )
            else:
                # Aspect lines: (glyph, text, color) format
                glyph, line_text, line_color = line_data
                fill_color = line_color if line_color else header_color

                # Calculate x positions based on text anchor
                if text_anchor == "end":
                    # Right-aligned: text first (rightmost), then glyph to its left
                    text_x = x
                    glyph_x = (
                        x - len(line_text) * 5.5
                    )  # Estimate text width, minimal gap
                else:
                    # Left-aligned: glyph first, then text
                    glyph_x = x
                    text_x = x + glyph_width if glyph else x

                # Render glyph with symbol font (if present)
                if glyph:
                    dwg.add(
                        dwg.text(
                            glyph,
                            insert=(glyph_x, line_y + glyph_y_offset),
                            text_anchor=text_anchor
                            if text_anchor == "end"
                            else "start",
                            dominant_baseline="hanging",
                            font_size=self.style["text_size"],
                            fill=fill_color,
                            font_family=renderer.style["font_family_glyphs"],
                            font_weight=font_weight,
                        )
                    )

                # Render text with text font
                dwg.add(
                    dwg.text(
                        line_text,
                        insert=(text_x, line_y),
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
        """Calculate position coordinates for AspectCountsLayer."""
        # Match the chart's own padding
        base_margin = renderer.size * 0.03
        total_height = num_lines * self.style["line_height"]

        # Get offsets for extended canvas positioning
        x_offset = getattr(renderer, "x_offset", 0)
        y_offset = getattr(renderer, "y_offset", 0)

        if self.position == "top-left":
            return (x_offset + base_margin, y_offset + base_margin)
        elif self.position == "top-right":
            # Aspect counter: reduce margin to push further right and up
            margin = base_margin * 0.3
            return (x_offset + renderer.size - margin, y_offset + margin)
        elif self.position == "bottom-left":
            margin = base_margin * 0.3
            return (x_offset + margin, y_offset + renderer.size - margin - total_height)
        elif self.position == "bottom-right":
            return (
                x_offset + renderer.size - base_margin,
                y_offset + renderer.size - base_margin - total_height,
            )
        else:
            return (x_offset + base_margin, y_offset + base_margin)


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
        from stellium.core.models import ObjectType

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

        # Get theme-aware text color from planets info_color
        theme_text_color = renderer.style.get("planets", {}).get(
            "info_color", self.style["text_color"]
        )
        background_color = renderer.style.get("background_color", "#FFFFFF")
        text_color = adjust_color_for_contrast(
            theme_text_color, background_color, min_contrast=4.5
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
        glyph_width = 12  # Approximate width for element symbol
        glyph_y_offset = -2  # Nudge glyphs up to align with text baseline

        for i, element in enumerate(elements):
            row_y = header_y + ((i + 1) * line_height)

            # Element symbol + name (row header) - render separately for proper fonts
            symbol = self.ELEMENT_SYMBOLS.get(element, element[0])
            element_abbrev = element[:2]

            if "right" in self.position:
                # Right-aligned: text first (rightmost), then symbol to its left
                text_x = row_header_x
                symbol_x = row_header_x - len(element_abbrev) * 6 - 4
                symbol_anchor = "end"
            else:
                # Left-aligned: symbol first, then text
                symbol_x = row_header_x
                text_x = row_header_x + glyph_width
                symbol_anchor = "start"

            # Render symbol with glyph font
            dwg.add(
                dwg.text(
                    symbol,
                    insert=(symbol_x, row_y + glyph_y_offset),
                    text_anchor=symbol_anchor,
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_glyphs"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Render text with text font
            dwg.add(
                dwg.text(
                    element_abbrev,
                    insert=(text_x, row_y),
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
        """Calculate position coordinates for ElementModalityTableLayer."""
        # Match the chart's own padding
        base_margin = renderer.size * 0.03
        total_height = num_lines * self.style["line_height"]

        # Get offsets for extended canvas positioning
        x_offset = getattr(renderer, "x_offset", 0)
        y_offset = getattr(renderer, "y_offset", 0)

        if self.position == "top-left":
            return (x_offset + base_margin, y_offset + base_margin)
        elif self.position == "top-right":
            margin = base_margin * 0.3
            return (x_offset + renderer.size - margin, y_offset + margin)
        elif self.position == "bottom-left":
            # Element modality: reduce margin to push further left and down
            margin = base_margin * 0.3
            return (x_offset + margin, y_offset + renderer.size - margin - total_height)
        elif self.position == "bottom-right":
            return (
                x_offset + renderer.size - base_margin,
                y_offset + renderer.size - base_margin - total_height,
            )
        else:
            return (x_offset + base_margin, y_offset + base_margin)


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
                    renderer.center + renderer.y_offset,
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
