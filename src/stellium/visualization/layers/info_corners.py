"""
Info corner layers - chart info, aspect counts, element/modality tables.
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
from stellium.visualization.palettes import (
    adjust_color_for_contrast,
)

__all__ = ["ChartInfoLayer", "AspectCountsLayer", "ElementModalityTableLayer"]


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
