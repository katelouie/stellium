"""
Chart frame layers - header, borders, and ring boundaries.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    UnknownTimeChart,
)
from stellium.visualization.core import (
    ChartRenderer,
)

__all__ = ["HeaderLayer", "RingBoundaryLayer", "OuterBorderLayer"]


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
