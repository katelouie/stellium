"""
Extended canvas layers for position tables and aspectarian grids.

These layers render tabular data outside the main chart wheel,
requiring an extended canvas with additional space.
"""

from typing import Any

import svgwrite

from stellium.core.chart_utils import is_comparison, is_multichart
from stellium.core.models import Aspect, CalculatedChart, ObjectType
from stellium.core.registry import CELESTIAL_REGISTRY, get_aspect_info

from .core import ChartRenderer, get_glyph

# Legacy aliases for backward compatibility within this module
# These are used by layers.py which imports them from here
_is_comparison = is_comparison
_is_multichart = is_multichart


def _filter_objects_for_tables(positions, object_types=None):
    """
    Filter positions to include in position tables and aspectarian.

    Default includes:
    - All PLANET objects (except Earth)
    - All ASTEROID objects
    - All POINT objects
    - North Node only (exclude South Node)
    - ASC/AC and MC only (exclude DSC/DC and IC)

    Default excludes:
    - MIDPOINT, ARABIC_PART, FIXED_STAR

    Args:
        positions: List of CelestialPosition objects
        object_types: Optional list of ObjectType enum values or strings to include.
                     If None, uses default filter (planet, asteroid, point, node, angle).
                     Examples: ["planet", "asteroid", "midpoint"]
                              [ObjectType.PLANET, ObjectType.ASTEROID]

    Returns:
        Filtered list of CelestialPosition objects
    """
    # Convert object_types to a set of ObjectType enums for fast lookup
    if object_types is None:
        # Default: include planet, asteroid, point, node, angle
        included_types = {
            ObjectType.PLANET,
            ObjectType.ASTEROID,
            ObjectType.POINT,
            ObjectType.NODE,
            ObjectType.ANGLE,
        }
    else:
        # Convert strings to ObjectType enums
        included_types = set()
        for obj_type in object_types:
            if isinstance(obj_type, str):
                # Convert string to ObjectType enum
                try:
                    included_types.add(ObjectType(obj_type.lower()))
                except ValueError:
                    # Skip invalid type names
                    pass
            elif isinstance(obj_type, ObjectType):
                included_types.add(obj_type)

    filtered = []
    for p in positions:
        # Skip Earth
        if p.name == "Earth":
            continue

        # Check if object type is in included types
        if p.object_type not in included_types:
            continue

        # For planets: include all except Earth (already checked)
        if p.object_type == ObjectType.PLANET:
            filtered.append(p)
            continue

        # For asteroids: include all
        if p.object_type == ObjectType.ASTEROID:
            filtered.append(p)
            continue

        # For nodes: include North Node only (exclude South Node)
        if p.object_type == ObjectType.NODE:
            if p.name in ("North Node", "True Node", "Mean Node"):
                filtered.append(p)
            continue

        # For points: include all
        if p.object_type == ObjectType.POINT:
            filtered.append(p)
            continue

        # For angles: include only ASC/AC and MC (exclude DSC/DC and IC)
        if p.object_type == ObjectType.ANGLE:
            if p.name in ("ASC", "AC", "Ascendant", "MC", "Midheaven"):
                filtered.append(p)
            continue

        # For midpoints and arabic parts: include all if type is in included_types
        if p.object_type in (
            ObjectType.MIDPOINT,
            ObjectType.ARABIC_PART,
            ObjectType.FIXED_STAR,
        ):
            filtered.append(p)
            continue

    return filtered


class PositionTableLayer:
    """
    Renders a table of planetary positions.

    Shows planet name, sign, degree, house, and speed in a tabular format.
    Respects chart theme colors.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "text_size": "10px",
        "header_size": "11px",
        "line_height": 16,
        "col_spacing": 55,  # Pixels between columns (reduced from 70 for tighter spacing)
        "font_weight": "normal",
        "header_weight": "bold",
        "show_speed": True,
        "show_house": True,
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
        object_types: list[str | ObjectType] | None = None,
        config: Any | None = None,
    ) -> None:
        """
        Initialize position table layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
            object_types: Optional list of object types to include.
                         If None, uses default (planet, asteroid, point, node, angle).
                         Examples: ["planet", "asteroid", "midpoint"]
            config: Optional ChartVisualizationConfig for column widths, padding, etc.
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.object_types = object_types
        self.config = config

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render position table.

        Handles CalculatedChart, Comparison, and MultiChart objects.
        For Comparison/MultiChart, displays two separate side-by-side tables.
        """
        # Check if this is a Comparison or MultiChart object
        if _is_comparison(chart):
            # Render two separate tables side by side
            self._render_comparison_tables(renderer, dwg, chart)
        elif _is_multichart(chart):
            # MultiChart uses same rendering as comparison (side-by-side)
            self._render_multichart_tables(renderer, dwg, chart)
        else:
            # Render standard single table
            self._render_single_table(renderer, dwg, chart)

    def _get_house_systems_to_display(self, chart) -> list[str]:
        """Determine which house systems to display in the table.

        Returns list of house system names based on config settings.
        """
        if not chart.house_systems:
            return []

        # Check config for house_systems setting
        if self.config and hasattr(self.config, "wheel"):
            config_systems = self.config.wheel.house_systems
            if config_systems == "all":
                # Show all available house systems
                return list(chart.house_systems.keys())
            elif isinstance(config_systems, list):
                # Show specific systems (filter to only those available)
                return [s for s in config_systems if s in chart.house_systems]

        # Default: just show the default house system
        if chart.default_house_system:
            return [chart.default_house_system]
        return list(chart.house_systems.keys())[:1]  # First available

    def _render_single_table(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render a single position table for a standard chart."""
        # Standard CalculatedChart - use filter function to include angles
        chart_positions = _filter_objects_for_tables(chart.positions, self.object_types)

        # Get defined names from registry
        name_priority = {name: i for i, name in enumerate(CELESTIAL_REGISTRY.keys())}
        # Sort by object type priority, then registry order
        type_priority = {
            ObjectType.PLANET: 0,
            ObjectType.ASTEROID: 1,
            ObjectType.NODE: 2,
            ObjectType.POINT: 3,
            ObjectType.ANGLE: 4,
            ObjectType.MIDPOINT: 5,
            ObjectType.ARABIC_PART: 6,
            ObjectType.FIXED_STAR: 7,
        }
        chart_positions.sort(
            key=lambda p: (
                type_priority.get(p.object_type, 99),
                name_priority.get(p.name, 999),
            )
        )

        # Build table
        x_start = self.x_offset
        y_start = self.y_offset

        # Get column widths from config if available, otherwise use hardcoded style
        if self.config and hasattr(self.config.tables, "position_col_widths"):
            col_widths = self.config.tables.position_col_widths
            padding = self.config.tables.padding
            gap = self.config.tables.gap_between_columns
        else:
            # Fallback to evenly-spaced columns
            col_widths = {
                "planet": 100,
                "sign": 50,
                "degree": 60,
                "house": 25,
                "speed": 25,
            }
            padding = 10
            gap = 5

        # Determine which house systems to show
        house_systems = (
            self._get_house_systems_to_display(chart)
            if self.style["show_house"]
            else []
        )

        # Header row with column mapping
        col_names = ["planet", "sign", "degree"]
        headers = ["Planet", "Sign", "Degree"]

        # Add house column(s) - one per system
        for system_name in house_systems:
            col_names.append("house")
            # Use abbreviated name for header if multiple systems
            if len(house_systems) > 1:
                # Abbreviate system names for header
                abbrev = self._abbreviate_house_system(system_name)
                headers.append(abbrev)
            else:
                headers.append("House")

        if self.style["show_speed"]:
            col_names.append("speed")
            headers.append("Speed")

        # Calculate column x positions (cumulative widths)
        col_x_positions = [x_start + padding]
        for i in range(1, len(col_names)):
            prev_col_name = col_names[i - 1]
            prev_x = col_x_positions[i - 1]
            prev_width = col_widths.get(prev_col_name, 50)
            col_x_positions.append(prev_x + prev_width + gap)

        # Get theme-aware colors (fallback to hardcoded if not in renderer)
        text_color = renderer.style.get("text_color", self.style["text_color"])
        header_color = renderer.style.get("text_color", self.style["header_color"])

        # Render headers
        for i, header in enumerate(headers):
            x = col_x_positions[i]
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start + padding),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=header_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows
        for row_idx, pos in enumerate(chart_positions):
            y = y_start + padding + ((row_idx + 1) * self.style["line_height"])

            # Column 0: Planet name + glyph
            glyph_info = get_glyph(pos.name)
            # Get display name from registry
            obj_info = CELESTIAL_REGISTRY.get(pos.name)
            display_name = obj_info.display_name if obj_info else pos.name

            if glyph_info["type"] == "unicode":
                planet_text = f"{glyph_info['value']} {display_name}"
            else:
                planet_text = display_name

            # Add retrograde symbol if applicable
            if pos.is_retrograde:
                planet_text += " ℞"

            dwg.add(
                dwg.text(
                    planet_text,
                    insert=(col_x_positions[0], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 1: Sign
            dwg.add(
                dwg.text(
                    pos.sign,
                    insert=(col_x_positions[1], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 2: Degree
            degrees = int(pos.sign_degree)
            minutes = int((pos.sign_degree % 1) * 60)
            degree_text = f"{degrees}°{minutes:02d}'"
            dwg.add(
                dwg.text(
                    degree_text,
                    insert=(col_x_positions[2], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # House columns (one per system)
            col_idx = 3
            for system_name in house_systems:
                house = self._get_house_placement_for_system(chart, pos, system_name)
                dwg.add(
                    dwg.text(
                        str(house) if house else "-",
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )
                col_idx += 1

            # Speed column (if enabled)
            if self.style["show_speed"]:
                speed_text = f"{pos.speed_longitude:.2f}"
                dwg.add(
                    dwg.text(
                        speed_text,
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )

    def _abbreviate_house_system(self, name: str) -> str:
        """Get abbreviated name for house system header."""
        abbreviations = {
            "Placidus": "Plac",
            "Whole Sign": "WS",
            "Koch": "Koch",
            "Equal": "Equ",
            "Regiomontanus": "Regio",
            "Campanus": "Camp",
            "Porphyry": "Porph",
            "Morinus": "Mor",
            "Alcabitius": "Alca",
            "Topocentric": "Topo",
        }
        return abbreviations.get(name, name[:4])

    def _get_house_placement_for_system(
        self, chart, position, system_name: str
    ) -> int | None:
        """Get house placement for a position in a specific house system."""
        if not chart.house_placements:
            return None
        placements = chart.house_placements.get(system_name, {})
        return placements.get(position.name)

    def _render_comparison_tables(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, comparison
    ) -> None:
        """Render two separate side-by-side tables for comparison charts."""
        # Get positions from both charts
        chart1_positions = _filter_objects_for_tables(
            comparison.chart1.positions, self.object_types
        )
        chart2_positions = _filter_objects_for_tables(
            comparison.chart2.positions, self.object_types
        )

        # Get defined names from registry
        name_priority = {name: i for i, name in enumerate(CELESTIAL_REGISTRY.keys())}

        # Sort both lists
        type_priority = {
            ObjectType.PLANET: 0,
            ObjectType.ASTEROID: 1,
            ObjectType.NODE: 2,
            ObjectType.POINT: 3,
            ObjectType.ANGLE: 4,
            ObjectType.MIDPOINT: 5,
            ObjectType.ARABIC_PART: 6,
            ObjectType.FIXED_STAR: 7,
        }
        chart1_positions.sort(
            key=lambda p: (
                type_priority.get(p.object_type, 99),
                name_priority.get(p.name, 999),
            )
        )
        chart2_positions.sort(
            key=lambda p: (
                type_priority.get(p.object_type, 99),
                name_priority.get(p.name, 999),
            )
        )

        # Get column widths from config if available
        if self.config and hasattr(self.config.tables, "position_col_widths"):
            col_widths = self.config.tables.position_col_widths
            padding = self.config.tables.padding
            gap = self.config.tables.gap_between_columns
            gap_between_tables = self.config.tables.gap_between_tables
        else:
            # Fallback
            col_widths = {
                "planet": 100,
                "sign": 50,
                "degree": 60,
                "house": 25,
                "speed": 25,
            }
            padding = 10
            gap = 5
            gap_between_tables = 20

        # Calculate single table width from column widths
        col_names = ["planet", "sign", "degree"]
        if self.style["show_house"]:
            col_names.append("house")
        if self.style["show_speed"]:
            col_names.append("speed")

        single_table_width = 2 * padding  # left and right padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:
                single_table_width += gap

        # Render Chart 1 table (left)
        x_chart1 = self.x_offset
        y_start = self.y_offset

        # Chart 1 title
        title_text = f"{comparison.chart1_label or 'Chart 1'} (Inner Wheel)"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart1, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=self.style["header_color"],
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 1 table (offset by title height)
        self._render_table_for_chart(
            renderer, dwg, comparison.chart1, chart1_positions, x_chart1, y_start + 20
        )

        # Render Chart 2 table (right, with spacing)
        x_chart2 = x_chart1 + single_table_width + gap_between_tables

        # Chart 2 title
        title_text = f"{comparison.chart2_label or 'Chart 2'} (Outer Wheel)"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart2, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=self.style["header_color"],
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 2 table (offset by title height)
        self._render_table_for_chart(
            renderer, dwg, comparison.chart2, chart2_positions, x_chart2, y_start + 20
        )

    def _render_multichart_tables(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, multichart
    ) -> None:
        """Render side-by-side tables for MultiChart (2+ charts)."""
        # Get positions from first two charts (for biwheel display)
        chart1_positions = _filter_objects_for_tables(
            multichart.charts[0].positions, self.object_types
        )
        chart2_positions = _filter_objects_for_tables(
            multichart.charts[1].positions, self.object_types
        )

        # Get defined names from registry
        name_priority = {name: i for i, name in enumerate(CELESTIAL_REGISTRY.keys())}

        # Sort both lists
        type_priority = {
            ObjectType.PLANET: 0,
            ObjectType.ASTEROID: 1,
            ObjectType.NODE: 2,
            ObjectType.POINT: 3,
            ObjectType.ANGLE: 4,
            ObjectType.MIDPOINT: 5,
            ObjectType.ARABIC_PART: 6,
            ObjectType.FIXED_STAR: 7,
        }
        chart1_positions.sort(
            key=lambda p: (
                type_priority.get(p.object_type, 99),
                name_priority.get(p.name, 999),
            )
        )
        chart2_positions.sort(
            key=lambda p: (
                type_priority.get(p.object_type, 99),
                name_priority.get(p.name, 999),
            )
        )

        # Get column widths from config if available
        if self.config and hasattr(self.config.tables, "position_col_widths"):
            col_widths = self.config.tables.position_col_widths
            padding = self.config.tables.padding
            gap = self.config.tables.gap_between_columns
            gap_between_tables = self.config.tables.gap_between_tables
        else:
            # Fallback
            col_widths = {
                "planet": 100,
                "sign": 50,
                "degree": 60,
                "house": 25,
                "speed": 25,
            }
            padding = 10
            gap = 5
            gap_between_tables = 20

        # Calculate single table width from column widths
        col_names = ["planet", "sign", "degree"]
        if self.style["show_house"]:
            col_names.append("house")
        if self.style["show_speed"]:
            col_names.append("speed")

        single_table_width = 2 * padding  # left and right padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:
                single_table_width += gap

        # Get labels from multichart
        label1 = multichart.labels[0] if multichart.labels else "Chart 1"
        label2 = multichart.labels[1] if len(multichart.labels) > 1 else "Chart 2"

        # Render Chart 1 table (left)
        x_chart1 = self.x_offset
        y_start = self.y_offset

        # Chart 1 title
        title_text = f"{label1} (Inner Wheel)"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart1, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=self.style["header_color"],
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 1 table (offset by title height)
        self._render_table_for_chart(
            renderer,
            dwg,
            multichart.charts[0],
            chart1_positions,
            x_chart1,
            y_start + 20,
        )

        # Render Chart 2 table (right, with spacing)
        x_chart2 = x_chart1 + single_table_width + gap_between_tables

        # Chart 2 title
        title_text = f"{label2} (Outer Wheel)"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart2, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=self.style["header_color"],
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 2 table (offset by title height)
        self._render_table_for_chart(
            renderer,
            dwg,
            multichart.charts[1],
            chart2_positions,
            x_chart2,
            y_start + 20,
        )

    def _render_table_for_chart(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart,
        positions,
        x_offset,
        y_offset,
    ) -> None:
        """Render a table for a specific chart."""
        x_start = x_offset
        y_start = y_offset

        # Get column widths from config if available, otherwise use hardcoded style
        if self.config and hasattr(self.config.tables, "position_col_widths"):
            col_widths = self.config.tables.position_col_widths
            padding = self.config.tables.padding
            gap = self.config.tables.gap_between_columns
        else:
            # Fallback to evenly-spaced columns
            col_widths = {
                "planet": 100,
                "sign": 50,
                "degree": 60,
                "house": 25,
                "speed": 25,
            }
            padding = 10
            gap = 5

        # Header row with column mapping
        col_names = ["planet", "sign", "degree"]
        headers = ["Planet", "Sign", "Degree"]
        if self.style["show_house"]:
            col_names.append("house")
            headers.append("House")
        if self.style["show_speed"]:
            col_names.append("speed")
            headers.append("Speed")

        # Calculate column x positions (cumulative widths)
        col_x_positions = [x_start + padding]
        for i in range(1, len(col_names)):
            prev_col_name = col_names[i - 1]
            prev_x = col_x_positions[i - 1]
            prev_width = col_widths.get(prev_col_name, 50)
            col_x_positions.append(prev_x + prev_width + gap)

        # Get theme-aware colors (fallback to hardcoded if not in renderer)
        text_color = renderer.style.get("text_color", self.style["text_color"])
        header_color = renderer.style.get("text_color", self.style["header_color"])

        # Render headers
        for i, header in enumerate(headers):
            x = col_x_positions[i]
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start + padding),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=header_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows
        for row_idx, pos in enumerate(positions):
            y = y_start + padding + ((row_idx + 1) * self.style["line_height"])

            # Column 0: Planet name + glyph
            glyph_info = get_glyph(pos.name)
            # Get display name from registry
            obj_info = CELESTIAL_REGISTRY.get(pos.name)
            display_name = obj_info.display_name if obj_info else pos.name

            if glyph_info["type"] == "unicode":
                planet_text = f"{glyph_info['value']} {display_name}"
            else:
                planet_text = display_name

            # Add retrograde symbol if applicable
            if pos.is_retrograde:
                planet_text += " ℞"

            dwg.add(
                dwg.text(
                    planet_text,
                    insert=(col_x_positions[0], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 1: Sign
            dwg.add(
                dwg.text(
                    pos.sign,
                    insert=(col_x_positions[1], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 2: Degree
            degrees = int(pos.sign_degree)
            minutes = int((pos.sign_degree % 1) * 60)
            degree_text = f"{degrees}°{minutes:02d}'"
            dwg.add(
                dwg.text(
                    degree_text,
                    insert=(col_x_positions[2], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 3: House (if enabled)
            col_idx = 3
            if self.style["show_house"]:
                house = self._get_house_placement(chart, pos)
                dwg.add(
                    dwg.text(
                        str(house) if house else "-",
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )
                col_idx += 1

            # Column 4: Speed (if enabled)
            if self.style["show_speed"]:
                speed_text = f"{pos.speed_longitude:.2f}"
                dwg.add(
                    dwg.text(
                        speed_text,
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )

    def _get_house_placement(self, chart: CalculatedChart, position) -> int | None:
        """Get house placement for a position."""
        if not chart.default_house_system or not chart.house_placements:
            return None

        placements = chart.house_placements.get(chart.default_house_system, {})
        return placements.get(position.name)


class HouseCuspTableLayer:
    """
    Renders a table of house cusps with sign placements.

    Shows house number, cusp longitude, sign, and degree in sign.
    Respects chart theme colors.
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "text_size": "10px",
        "header_size": "11px",
        "line_height": 16,
        "col_spacing": 55,  # Pixels between columns (reduced from 70 for tighter spacing)
        "font_weight": "normal",
        "header_weight": "bold",
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
        config: Any | None = None,
    ) -> None:
        """
        Initialize house cusp table layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
            config: Optional ChartVisualizationConfig for column widths, padding, etc.
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.config = config

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render house cusp table.

        Handles CalculatedChart, Comparison, and MultiChart objects.
        For Comparison/MultiChart, displays two separate side-by-side tables.
        """
        # Check if this is a Comparison or MultiChart object
        is_comparison = _is_comparison(chart)
        is_multichart = _is_multichart(chart)

        if is_comparison:
            # Render two separate house cusp tables side by side
            self._render_comparison_house_tables(renderer, dwg, chart)
        elif is_multichart:
            # MultiChart uses similar rendering to comparison
            self._render_multichart_house_tables(renderer, dwg, chart)
        else:
            # Render standard single table
            self._render_single_house_table(renderer, dwg, chart)

    def _get_house_systems_to_display(self, chart) -> list[str]:
        """Determine which house systems to display in the table."""
        if not chart.house_systems:
            return []

        # Check config for house_systems setting
        if self.config and hasattr(self.config, "wheel"):
            config_systems = self.config.wheel.house_systems
            if config_systems == "all":
                return list(chart.house_systems.keys())
            elif isinstance(config_systems, list):
                return [s for s in config_systems if s in chart.house_systems]

        # Default: just show the default house system
        if chart.default_house_system:
            return [chart.default_house_system]
        return list(chart.house_systems.keys())[:1]

    def _abbreviate_house_system(self, name: str) -> str:
        """Get abbreviated name for house system header."""
        abbreviations = {
            "Placidus": "Plac",
            "Whole Sign": "WS",
            "Koch": "Koch",
            "Equal": "Equ",
            "Regiomontanus": "Regio",
            "Campanus": "Camp",
            "Porphyry": "Porph",
            "Morinus": "Mor",
            "Alcabitius": "Alca",
            "Topocentric": "Topo",
        }
        return abbreviations.get(name, name[:4])

    def _render_single_house_table(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart
    ) -> None:
        """Render a single house cusp table for a standard chart.

        Supports multiple house systems as additional columns.
        """
        # Get house systems to display
        house_systems = self._get_house_systems_to_display(chart)
        if not house_systems:
            return

        # Build table
        x_start = self.x_offset
        y_start = self.y_offset

        # Get column widths from config if available
        if self.config and hasattr(self.config.tables, "house_col_widths"):
            col_widths = self.config.tables.house_col_widths
            padding = self.config.tables.padding
            gap = self.config.tables.gap_between_columns
        else:
            # Fallback
            col_widths = {"house": 30, "sign": 50, "degree": 60}
            padding = 10
            gap = 5

        # Build column names and headers: House + (Sign, Degree) per system
        col_names = ["house"]
        headers = ["House"]

        for system_name in house_systems:
            col_names.extend(["sign", "degree"])
            if len(house_systems) > 1:
                # Use abbreviated system name as header prefix
                abbrev = self._abbreviate_house_system(system_name)
                headers.extend([f"{abbrev}", "Deg"])
            else:
                headers.extend(["Sign", "Degree"])

        # Calculate column x positions (cumulative widths)
        col_x_positions = [x_start + padding]
        for i in range(1, len(col_names)):
            prev_col_name = col_names[i - 1]
            prev_x = col_x_positions[i - 1]
            prev_width = col_widths.get(prev_col_name, 50)
            col_x_positions.append(prev_x + prev_width + gap)

        # Get theme-aware colors
        text_color = renderer.style.get("text_color", self.style["text_color"])
        header_color = renderer.style.get("text_color", self.style["header_color"])

        # Sign names for conversion
        sign_names = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]

        # Render headers
        for i, header in enumerate(headers):
            x = col_x_positions[i]
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start + padding),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=header_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows for all 12 houses
        for house_num in range(1, 13):
            y = y_start + padding + (house_num * self.style["line_height"])

            # Column 0: House number
            dwg.add(
                dwg.text(
                    str(house_num),
                    insert=(col_x_positions[0], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Render sign and degree for each house system
            col_idx = 1
            for system_name in house_systems:
                houses = chart.get_houses(system_name)
                if not houses:
                    col_idx += 2
                    continue

                cusp_longitude = houses.cusps[house_num - 1]
                sign_index = int(cusp_longitude / 30)
                sign_name = sign_names[sign_index % 12]
                degree_in_sign = cusp_longitude % 30

                # Sign column
                dwg.add(
                    dwg.text(
                        sign_name,
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )
                col_idx += 1

                # Degree column
                degrees = int(degree_in_sign)
                minutes = int((degree_in_sign % 1) * 60)
                degree_text = f"{degrees}°{minutes:02d}'"
                dwg.add(
                    dwg.text(
                        degree_text,
                        insert=(col_x_positions[col_idx], y),
                        text_anchor="start",
                        dominant_baseline="hanging",
                        font_size=self.style["text_size"],
                        fill=text_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight=self.style["font_weight"],
                    )
                )
                col_idx += 1

    def _render_comparison_house_tables(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, comparison
    ) -> None:
        """Render two separate side-by-side house cusp tables for comparison charts."""
        # Get house cusps from both charts
        if not comparison.chart1.default_house_system:
            return
        if not comparison.chart2.default_house_system:
            return

        houses1 = comparison.chart1.get_houses(comparison.chart1.default_house_system)
        houses2 = comparison.chart2.get_houses(comparison.chart2.default_house_system)

        if not houses1 or not houses2:
            return

        # Get config values
        if self.config and hasattr(self.config.tables, "house_col_widths"):
            col_widths = self.config.tables.house_col_widths
            padding = self.config.tables.padding
            gap_between_cols = self.config.tables.gap_between_columns
            gap_between_tables = self.config.tables.gap_between_tables
        else:
            # Fallback
            col_widths = {"house": 30, "sign": 50, "degree": 60}
            padding = 10
            gap_between_cols = 5
            gap_between_tables = 20

        # Calculate single table width: padding + columns + gaps + padding
        col_names = ["house", "sign", "degree"]
        single_table_width = 2 * padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:
                single_table_width += gap_between_cols

        # Render Chart 1 house table (left)
        x_chart1 = self.x_offset
        y_start = self.y_offset

        # Get theme-aware colors
        text_color = renderer.style.get("text_color", self.style["text_color"])
        header_color = renderer.style.get("text_color", self.style["header_color"])

        # Chart 1 title
        title_text = f"{comparison.chart1_label or 'Chart 1'} Houses"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart1, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=header_color,
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 1 house table (offset by title height)
        self._render_house_table_for_chart(
            renderer,
            dwg,
            houses1,
            x_chart1,
            y_start + 20,
            col_widths,
            padding,
            gap_between_cols,
            text_color,
            header_color,
        )

        # Render Chart 2 house table (right, with spacing)
        x_chart2 = x_chart1 + single_table_width + gap_between_tables

        # Chart 2 title
        title_text = f"{comparison.chart2_label or 'Chart 2'} Houses"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart2, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=header_color,
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 2 house table (offset by title height)
        self._render_house_table_for_chart(
            renderer,
            dwg,
            houses2,
            x_chart2,
            y_start + 20,
            col_widths,
            padding,
            gap_between_cols,
            text_color,
            header_color,
        )

    def _render_multichart_house_tables(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, multichart
    ) -> None:
        """Render two separate side-by-side house cusp tables for MultiChart."""
        chart1 = multichart.charts[0]
        chart2 = multichart.charts[1]

        # Get house cusps from both charts
        if not chart1.default_house_system:
            return
        if not chart2.default_house_system:
            return

        houses1 = chart1.get_houses(chart1.default_house_system)
        houses2 = chart2.get_houses(chart2.default_house_system)

        if not houses1 or not houses2:
            return

        # Get config values
        if self.config and hasattr(self.config.tables, "house_col_widths"):
            col_widths = self.config.tables.house_col_widths
            padding = self.config.tables.padding
            gap_between_cols = self.config.tables.gap_between_columns
            gap_between_tables = self.config.tables.gap_between_tables
        else:
            # Fallback
            col_widths = {"house": 30, "sign": 50, "degree": 60}
            padding = 10
            gap_between_cols = 5
            gap_between_tables = 20

        # Calculate single table width: padding + columns + gaps + padding
        col_names = ["house", "sign", "degree"]
        single_table_width = 2 * padding
        for i, col_name in enumerate(col_names):
            single_table_width += col_widths.get(col_name, 50)
            if i < len(col_names) - 1:
                single_table_width += gap_between_cols

        # Get labels from multichart
        label1 = multichart.labels[0] if multichart.labels else "Chart 1"
        label2 = multichart.labels[1] if len(multichart.labels) > 1 else "Chart 2"

        # Render Chart 1 house table (left)
        x_chart1 = self.x_offset
        y_start = self.y_offset

        # Get theme-aware colors
        text_color = renderer.style.get("text_color", self.style["text_color"])
        header_color = renderer.style.get("text_color", self.style["header_color"])

        # Chart 1 title
        title_text = f"{label1} Houses"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart1, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=header_color,
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 1 house table (offset by title height)
        self._render_house_table_for_chart(
            renderer,
            dwg,
            houses1,
            x_chart1,
            y_start + 20,
            col_widths,
            padding,
            gap_between_cols,
            text_color,
            header_color,
        )

        # Render Chart 2 house table (right, with spacing)
        x_chart2 = x_chart1 + single_table_width + gap_between_tables

        # Chart 2 title
        title_text = f"{label2} Houses"
        dwg.add(
            dwg.text(
                title_text,
                insert=(x_chart2, y_start),
                text_anchor="start",
                dominant_baseline="hanging",
                font_size="12px",
                fill=header_color,
                font_family=renderer.style["font_family_text"],
                font_weight="bold",
            )
        )

        # Render chart 2 house table (offset by title height)
        self._render_house_table_for_chart(
            renderer,
            dwg,
            houses2,
            x_chart2,
            y_start + 20,
            col_widths,
            padding,
            gap_between_cols,
            text_color,
            header_color,
        )

    def _render_house_table_for_chart(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        houses,
        x_offset,
        y_offset,
        col_widths,
        padding,
        gap,
        text_color,
        header_color,
    ) -> None:
        """Render a house cusp table for a specific chart."""
        x_start = x_offset
        y_start = y_offset

        # Header row with column mapping
        col_names = ["house", "sign", "degree"]
        headers = ["House", "Sign", "Degree"]

        # Calculate column x positions (cumulative widths)
        col_x_positions = [x_start + padding]
        for i in range(1, len(col_names)):
            prev_col_name = col_names[i - 1]
            prev_x = col_x_positions[i - 1]
            prev_width = col_widths.get(prev_col_name, 50)
            col_x_positions.append(prev_x + prev_width + gap)

        # Render headers
        for i, header in enumerate(headers):
            x = col_x_positions[i]
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_start + padding),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["header_size"],
                    fill=header_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["header_weight"],
                )
            )

        # Render data rows for all 12 houses
        for house_num in range(1, 13):
            y = y_start + padding + (house_num * self.style["line_height"])

            # Get cusp longitude
            cusp_longitude = houses.cusps[house_num - 1]

            # Calculate sign and degree
            sign_index = int(cusp_longitude / 30)
            sign_names = [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces",
            ]
            sign_name = sign_names[sign_index % 12]
            degree_in_sign = cusp_longitude % 30

            # Column 0: House number
            house_text = f"{house_num}"
            dwg.add(
                dwg.text(
                    house_text,
                    insert=(col_x_positions[0], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 1: Sign
            dwg.add(
                dwg.text(
                    sign_name,
                    insert=(col_x_positions[1], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Column 2: Degree
            degrees = int(degree_in_sign)
            minutes = int((degree_in_sign % 1) * 60)
            degree_text = f"{degrees}°{minutes:02d}'"
            dwg.add(
                dwg.text(
                    degree_text,
                    insert=(col_x_positions[2], y),
                    text_anchor="start",
                    dominant_baseline="hanging",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight=self.style["font_weight"],
                )
            )


class AspectarianLayer:
    """
    Renders an aspectarian grid (triangle aspect table).

    Shows aspects between all planets in a classic triangle grid format.
    Respects chart theme colors.

    Supports two modes:
    - Simple (default): Large aspect glyphs only
    - Detailed: Smaller glyphs with orb value and A/S (applying/separating) indicator
    """

    DEFAULT_STYLE = {
        "text_color": "#333333",
        "header_color": "#222222",
        "grid_color": "#CCCCCC",
        "text_size": "14px",  # Larger glyph for simple mode
        "text_size_detailed": "11px",  # Smaller glyph for detailed mode
        "orb_size": "6px",  # Small font for orb text
        "header_size": "10px",
        "cell_size": 24,  # Size of each grid cell
        "font_weight": "normal",
        "header_weight": "bold",
        "show_grid": True,
    }

    def __init__(
        self,
        x_offset: float = 0,
        y_offset: float = 0,
        style_override: dict[str, Any] | None = None,
        object_types: list[str | ObjectType] | None = None,
        config: Any | None = None,
        detailed: bool = False,
    ) -> None:
        """
        Initialize aspectarian layer.

        Args:
            x_offset: X position offset from canvas origin
            y_offset: Y position offset from canvas origin
            style_override: Optional style overrides
            object_types: Optional list of object types to include.
                         If None, uses default (planet, asteroid, point, node, angle).
                         Examples: ["planet", "asteroid", "midpoint"]
            config: Optional ChartVisualizationConfig for cell sizing, padding, etc.
            detailed: If True, show orb and applying/separating indicator in cells.
                     If False (default), show larger glyphs only.
        """
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}
        self.object_types = object_types
        self.config = config
        self.detailed = detailed

    def render(self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart) -> None:
        """Render aspectarian grid.

        Handles CalculatedChart, Comparison, and MultiChart objects.
        For Comparison/MultiChart, displays cross-chart aspects including Asc and MC from both charts.
        """
        # Check if this is a Comparison or MultiChart object
        is_comparison = _is_comparison(chart)
        is_multichart = _is_multichart(chart)
        cell_size = self.style["cell_size"]
        padding = self.style.get("label_padding", 4)

        if is_comparison or is_multichart:
            # Get chart1 and chart2 positions (different access for Comparison vs MultiChart)
            if is_multichart:
                chart1_positions = chart.charts[0].positions
                chart2_positions = chart.charts[1].positions
                cross_aspects = chart.get_all_cross_aspects()
            else:
                chart1_positions = chart.chart1.positions
                chart2_positions = chart.chart2.positions
                cross_aspects = chart.cross_aspects

            # For comparisons: get all celestial objects using filter function
            # Chart1 objects (rows - inner wheel)
            chart1_objects = _filter_objects_for_tables(
                chart1_positions, self.object_types
            )

            # Chart2 objects (columns - outer wheel)
            chart2_objects = _filter_objects_for_tables(
                chart2_positions, self.object_types
            )

            # Sort by traditional order (planets first, nodes, points, then angles)
            object_order = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
                "North Node",
                "True Node",
                "Mean Node",
                "ASC",
                "AC",
                "Ascendant",
                "MC",
                "Midheaven",
            ]

            chart1_objects.sort(
                key=lambda p: object_order.index(p.name)
                if p.name in object_order
                else 99
            )
            chart2_objects.sort(
                key=lambda p: object_order.index(p.name)
                if p.name in object_order
                else 99
            )

            # Build aspect lookup from cross_aspects
            aspect_lookup = {}
            for aspect in cross_aspects:
                # Key format: (chart1_obj_name, chart2_obj_name)
                key = (aspect.object1.name, aspect.object2.name)
                aspect_lookup[key] = aspect

            # Use chart1_objects for rows, chart2_objects for columns
            row_objects = chart1_objects
            col_objects = chart2_objects

        else:
            # Standard CalculatedChart - use filter function to include angles and nodes
            planets = _filter_objects_for_tables(chart.positions, self.object_types)

            # Sort by traditional order (planets, nodes, points, angles)
            planet_order = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
                "North Node",
                "True Node",
                "Mean Node",
                "ASC",
                "AC",
                "Ascendant",
                "MC",
                "Midheaven",
            ]
            planets.sort(
                key=lambda p: planet_order.index(p.name)
                if p.name in planet_order
                else 99
            )

            # Build aspect lookup
            aspect_lookup = {}
            for aspect in chart.aspects:
                key1 = (aspect.object1.name, aspect.object2.name)
                key2 = (aspect.object2.name, aspect.object1.name)
                aspect_lookup[key1] = aspect
                aspect_lookup[key2] = aspect

            # Use planets for both rows and columns (traditional triangle grid)
            row_objects = planets
            col_objects = planets

        # Render grid
        cell_size = self.style["cell_size"]
        x_start = self.x_offset
        y_start = self.y_offset

        if is_comparison:
            # For comparisons: full rectangular grid (chart1 rows × chart2 columns)
            # Column headers (chart2 objects - outer wheel) - aligned at left edge of column
            for col_idx, obj in enumerate(col_objects):
                glyph_info = get_glyph(obj.name)
                glyph = (
                    glyph_info["value"]
                    if glyph_info["type"] == "unicode"
                    else obj.name[:2]
                )

                # Add 2 indicator for chart2
                glyph = f"{glyph}₂"

                # Center of the column (offset by cell_size for row header column)
                x = x_start + cell_size + (col_idx * cell_size) + (cell_size / 2)

                # Bottom of the text sits just above the first row (y_start + cell_size)
                # We subtract the padding from the top of the grid
                y = y_start + cell_size - padding

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y),
                        text_anchor="middle",  # Center aligned
                        # dominant_baseline="hanging",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

            # Row headers (chart1 objects - inner wheel) and grid cells
            for row_idx, obj_row in enumerate(row_objects):
                glyph_info = get_glyph(obj_row.name)
                glyph = (
                    glyph_info["value"]
                    if glyph_info["type"] == "unicode"
                    else obj_row.name[:2]
                )

                # Add 1 indicator for chart1
                glyph = f"{glyph}₁"

                # Center of the row vertically
                y_row_center = y_start + ((row_idx + 1) * cell_size) + (cell_size / 2)

                # Right-align text against the grid edge (x_start + cell_size)
                x_text = x_start + cell_size - padding

                # Row header
                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x_text, y_row_center),
                        text_anchor="end",  # Right aligned (tight to grid)
                        dominant_baseline="middle",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

                # Grid cells (all columns for rectangular grid)
                for col_idx, obj_col in enumerate(col_objects):
                    cell_x_left = x_start + cell_size + (col_idx * cell_size)
                    cell_x_center = cell_x_left + (cell_size / 2)

                    # Draw grid lines if enabled
                    if self.style["show_grid"]:
                        cell_y = y_start + ((row_idx + 1) * cell_size)

                        dwg.add(
                            dwg.rect(
                                insert=(cell_x_left, cell_y),
                                size=(cell_size, cell_size),
                                fill="none",
                                stroke=self.style["grid_color"],
                                stroke_width=0.5,
                            )
                        )

                    # Aspects
                    aspect_key = (obj_row.name, obj_col.name)
                    if aspect_key in aspect_lookup:
                        self._render_aspect_glyph(
                            dwg,
                            renderer,
                            aspect_lookup[aspect_key],
                            cell_x_center,
                            y_row_center,
                        )

        else:
            # === SINGLE CHART: TRIANGLE GRID ===

            # Column headers (Top - Stair Step)
            # Only go up to len - 1 because the last planet never heads a column in a triangle
            for col_idx in range(len(row_objects) - 1):
                obj = row_objects[col_idx]
                glyph_info = get_glyph(obj.name)
                glyph = (
                    glyph_info["value"]
                    if glyph_info["type"] == "unicode"
                    else obj.name[:2]
                )

                # Center of the column
                x = x_start + ((col_idx + 1) * cell_size) + (cell_size / 2)
                # STAIR STEP CALCULATION:
                # The column for planet index `i` starts at row index `i + 1`.
                # We want the label to sit on top of that first box.
                # Top of first box = y_start + ((col_idx + 1) * cell_size)
                y = y_start + ((col_idx + 1) * cell_size) - padding

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y),
                        text_anchor="middle",  # Center aligned
                        # dominant_baseline="hanging",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

            # Row headers (left) and grid cells (lower triangle only)
            for row_idx in range(1, len(row_objects)):
                obj_row = row_objects[row_idx]
                glyph_info = get_glyph(obj_row.name)
                glyph = (
                    glyph_info["value"]
                    if glyph_info["type"] == "unicode"
                    else obj_row.name[:2]
                )

                y_row_center = y_start + (row_idx * cell_size) + (cell_size / 2)

                # Right-align text against the grid edge
                x_text = x_start + cell_size - padding

                # Row header
                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x_text, y_row_center),
                        text_anchor="end",  # Right aligned
                        dominant_baseline="middle",
                        font_size=self.style["header_size"],
                        fill=self.style["header_color"],
                        font_family=renderer.style["font_family_glyphs"],
                        font_weight=self.style["header_weight"],
                    )
                )

                # Grid cells (only lower triangle)
                for col_idx in range(row_idx):
                    obj_col = row_objects[col_idx]
                    cell_x_left = x_start + cell_size + (col_idx * cell_size)
                    cell_x_center = cell_x_left + (cell_size / 2)

                    # Draw grid lines if enabled
                    if self.style["show_grid"]:
                        # Cell border
                        cell_y = y_start + (row_idx * cell_size)

                        dwg.add(
                            dwg.rect(
                                insert=(cell_x_left, cell_y),
                                size=(cell_size, cell_size),
                                fill="none",
                                stroke=self.style["grid_color"],
                                stroke_width=0.5,
                            )
                        )

                    # Check for aspect
                    aspect_key = (obj_row.name, obj_col.name)
                    if aspect_key in aspect_lookup:
                        self._render_aspect_glyph(
                            dwg,
                            renderer,
                            aspect_lookup[aspect_key],
                            cell_x_center,
                            y_row_center,
                        )

    def _render_aspect_glyph(
        self,
        dwg: svgwrite.Drawing,
        renderer: ChartRenderer,
        aspect: Aspect,
        x: float,
        y: float,
    ):
        """Helper to render the aspect glyph in a cell.

        In simple mode (default): renders a larger glyph centered in the cell.
        In detailed mode: renders a smaller glyph with orb and A/S indicator below.
        """
        aspect_info = get_aspect_info(aspect.aspect_name)

        if aspect_info and aspect_info.glyph:
            aspect_glyph = aspect_info.glyph
        else:
            aspect_glyph = aspect.aspect_name[:1]

        # Get color from aspect palette (renderer.style["aspects"])
        aspect_style_dict = renderer.style.get("aspects", {})
        aspect_style = aspect_style_dict.get(
            aspect.aspect_name, aspect_style_dict.get("default", {})
        )
        if isinstance(aspect_style, dict):
            text_color = aspect_style.get("color", self.style["text_color"])
        else:
            text_color = self.style["text_color"]

        if self.detailed:
            # Detailed mode: smaller glyph at top, orb + A/S at bottom
            glyph_y = y - 4  # Shift glyph up slightly

            # Render smaller aspect glyph
            dwg.add(
                dwg.text(
                    aspect_glyph,
                    insert=(x, glyph_y),
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_size=self.style["text_size_detailed"],
                    fill=text_color,
                    font_family=renderer.style["font_family_glyphs"],
                    font_weight=self.style["font_weight"],
                )
            )

            # Build orb + A/S text
            orb_text = f"{aspect.orb:.0f}°"
            if aspect.is_applying is not None:
                orb_text += "A" if aspect.is_applying else "S"

            # Render orb text below glyph
            orb_y = y + 5  # Below the glyph
            # Get theme-aware color for orb text (use info_color like other info text)
            orb_color = renderer.style.get("planets", {}).get(
                "info_color", self.style["text_color"]
            )

            dwg.add(
                dwg.text(
                    orb_text,
                    insert=(x, orb_y),
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_size=self.style["orb_size"],
                    fill=orb_color,
                    font_family=renderer.style["font_family_text"],
                    font_weight="normal",
                )
            )
        else:
            # Simple mode: larger glyph centered in cell
            dwg.add(
                dwg.text(
                    aspect_glyph,
                    insert=(x, y),
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_size=self.style["text_size"],
                    fill=text_color,
                    font_family=renderer.style["font_family_glyphs"],
                    font_weight=self.style["font_weight"],
                )
            )


# =============================================================================
# Standalone Aspectarian Generator
# =============================================================================


def generate_aspectarian_svg(
    chart,
    output_path: str | None = None,
    cell_size: int | None = None,
    detailed: bool = False,
    theme: str | None = None,
    aspect_palette: str | None = None,
    padding: int | None = None,
) -> str:
    """
    Generate a standalone aspectarian SVG (triangle for single charts, square for comparisons).

    Args:
        chart: CalculatedChart or Comparison object
        output_path: Optional path to save SVG file. If None, returns SVG string.
        cell_size: Size of each grid cell in pixels (default: from config, typically 24)
        detailed: If True, show orb and applying/separating indicator (default: False)
        theme: Optional theme name (e.g., "dark", "midnight")
        aspect_palette: Optional aspect color palette
        padding: Padding around the grid in pixels (default: from config, typically 10)

    Returns:
        SVG string if output_path is None, otherwise the output_path

    Example:
        # Generate and save triangle aspectarian
        chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
        generate_aspectarian_svg(chart, "einstein_aspects.svg")

        # Generate square aspectarian for synastry
        comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()
        svg_string = generate_aspectarian_svg(comparison)

        # With styling
        generate_aspectarian_svg(
            chart,
            "aspects.svg",
            cell_size=28,
            detailed=True,
            theme="midnight",
        )
    """
    from stellium.visualization.config import (
        ChartVisualizationConfig,
        ChartWheelConfig,
        InfoCornerConfig,
        TableConfig,
    )
    from stellium.visualization.layout.measurer import ContentMeasurer

    # Create config with overrides
    table_config_kwargs = {"aspectarian_detailed": detailed}
    if cell_size is not None:
        table_config_kwargs["aspectarian_cell_size"] = cell_size
    if padding is not None:
        table_config_kwargs["padding"] = padding

    table_config = TableConfig(**table_config_kwargs)
    is_comparison = _is_comparison(chart)
    config = ChartVisualizationConfig(
        wheel=ChartWheelConfig(chart_type="biwheel" if is_comparison else "single"),
        corners=InfoCornerConfig(),
        tables=table_config,
    )

    # Use measurer for dimensions
    measurer = ContentMeasurer()
    dims = measurer.measure_aspectarian(chart, config)

    # Add padding
    actual_padding = padding if padding is not None else config.tables.padding
    width = dims.width + (2 * actual_padding)
    height = dims.height + (2 * actual_padding)

    # Create renderer (for style/font info)
    renderer = ChartRenderer(
        size=max(width, height),
        theme=theme,
        aspect_palette=aspect_palette,
    )

    # Create SVG drawing
    dwg = svgwrite.Drawing(
        filename=output_path or "aspectarian.svg",
        size=(f"{width}px", f"{height}px"),
        profile="full",
    )

    # Add background
    bg_color = renderer.style.get("background_color", "#FFFFFF")
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=bg_color))

    # Create and render aspectarian layer
    actual_cell_size = (
        cell_size if cell_size is not None else config.tables.aspectarian_cell_size
    )
    layer = AspectarianLayer(
        x_offset=actual_padding,
        y_offset=actual_padding,
        style_override={"cell_size": actual_cell_size},
        detailed=detailed,
    )
    layer.render(renderer, dwg, chart)

    # Save or return
    if output_path:
        dwg.saveas(output_path)
        return output_path
    else:
        return dwg.tostring()


def get_aspectarian_dimensions(
    chart,
    cell_size: int | None = None,
    padding: int | None = None,
) -> tuple[int, int]:
    """
    Calculate the dimensions of an aspectarian SVG without rendering.

    Uses the ContentMeasurer for consistency with the rest of the visualization system.

    Args:
        chart: CalculatedChart or Comparison object
        cell_size: Size of each grid cell in pixels (default: from config, typically 24)
        padding: Padding around the grid in pixels (default: from config, typically 10)

    Returns:
        Tuple of (width, height) in pixels
    """
    from stellium.visualization.config import (
        ChartVisualizationConfig,
        ChartWheelConfig,
        InfoCornerConfig,
        TableConfig,
    )
    from stellium.visualization.layout.measurer import ContentMeasurer

    # Create config with overrides
    table_config_kwargs = {}
    if cell_size is not None:
        table_config_kwargs["aspectarian_cell_size"] = cell_size
    if padding is not None:
        table_config_kwargs["padding"] = padding

    table_config = TableConfig(**table_config_kwargs)
    is_comparison = _is_comparison(chart)
    config = ChartVisualizationConfig(
        wheel=ChartWheelConfig(chart_type="biwheel" if is_comparison else "single"),
        corners=InfoCornerConfig(),
        tables=table_config,
    )

    # Use measurer
    measurer = ContentMeasurer()
    dims = measurer.measure_aspectarian(chart, config)

    # Add padding
    actual_padding = padding if padding is not None else config.tables.padding
    width = dims.width + (2 * actual_padding)
    height = dims.height + (2 * actual_padding)

    return (width, height)
