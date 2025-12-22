"""
Profection wheel visualization section.

Generates SVG wheel visualizations for annual profections:
- Circular wheel with ages 0-95 spiraling through 12 houses
- House labels with zodiac signs around perimeter
- Natal planet positions marked on the wheel
- Current age highlighting
- Summary table with profection details
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import svgwrite

from stellium.core.models import CalculatedChart
from stellium.core.registry import CELESTIAL_REGISTRY

from ._utils import get_sign_glyph
from .zr_visualization import _add_font_defs

if TYPE_CHECKING:
    pass

# =============================================================================
# Constants & Styling
# =============================================================================

# Color palette (matching ZR visualization style)
COLORS = {
    "background": "#ffffff",
    "current_period": "#f5e6c8",  # Warm cream highlight for current age
    "wheel_background": "#faf8f5",  # Light cream for wheel background
    "zodiac_ring": "#e8e4df",  # Shaded ring for zodiac signs
    "natal_ring": "#e8dff0",  # Light purple ring for natal placements
    "house_line": "#d0c8c0",  # Subtle house division lines
    "text_dark": "#2d2330",
    "text_muted": "#6b4d6e",
    "age_text": "#4a4a4a",
    "house_label": "#2d2330",
    "legend_box": "#f5e6c8",
    "legend_border": "#d0c8c0",
    "table_header": "#4a3353",
    "table_border": "#d0c8c0",
}

# Wheel dimensions
SVG_WIDTH = 600
SVG_HEIGHT = 800  # Includes table below
WHEEL_SIZE = 520
WHEEL_CENTER = WHEEL_SIZE / 2
WHEEL_MARGIN = 40

# Ring structure:
# - Innermost: house labels (1st, 2nd, etc.)
# - Middle 8 rings: ages 0-95
# - Zodiac ring: shaded ring with zodiac signs and rulers
# - Outermost: natal placements ring (light purple)
NUM_AGE_RINGS = 8
HOUSE_LABEL_RADIUS = 45  # Inner ring for house labels
AGE_INNER_RADIUS = 70  # Where age rings start
AGE_OUTER_RADIUS = 200  # Where age rings end
ZODIAC_RING_INNER = 205  # Shaded zodiac ring
ZODIAC_RING_OUTER = 235
NATAL_RING_INNER = 238  # Light purple natal placements ring
NATAL_RING_OUTER = 260
AGE_RING_WIDTH = (AGE_OUTER_RADIUS - AGE_INNER_RADIUS) / NUM_AGE_RINGS

# Legacy names for compatibility
OUTER_RADIUS = AGE_OUTER_RADIUS
INNER_RADIUS = AGE_INNER_RADIUS
NUM_RINGS = NUM_AGE_RINGS
RING_WIDTH = AGE_RING_WIDTH

# Sign order
SIGNS = [
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


@dataclass
class ProfectionVizConfig:
    """Configuration for profection wheel visualization."""

    # Display options
    current_age: int | None = None
    show_wheel: bool = True
    show_table: bool = True
    compare_ages: list[int] | None = None  # For side-by-side comparison in table

    # Styling
    width: int = SVG_WIDTH
    colors: dict = field(default_factory=lambda: COLORS.copy())


class ProfectionVisualizationSection:
    """
    Profection wheel visualization section.

    Generates an SVG visualization showing:
    - Circular wheel with ages spiraling through 12 houses
    - Zodiac signs and house labels around the perimeter
    - Natal planet positions
    - Current age highlighted
    - Summary table with profection details

    Example:
        section = ProfectionVisualizationSection(
            age=30,
            show_table=True
        )
        data = section.generate_data(chart)
        # data["content"] contains SVG string
    """

    def __init__(
        self,
        age: int | None = None,
        date: dt.datetime | str | None = None,
        compare_ages: list[int] | None = None,
        show_wheel: bool = True,
        show_table: bool = True,
        house_system: str | None = None,
        rulership: str = "traditional",
    ) -> None:
        """
        Initialize profection visualization section.

        Args:
            age: Current age to highlight (if None, calculated from date)
            date: Target date for profection (alternative to age)
            compare_ages: List of ages to compare in table (default: current and next)
            show_wheel: Whether to show the wheel visualization
            show_table: Whether to show the summary table
            house_system: House system to use (default: Whole Sign)
            rulership: Rulership system ("traditional" or "modern")
        """
        self.age = age
        self.date = date
        self.compare_ages = compare_ages
        self.show_wheel = show_wheel
        self.show_table = show_table
        self.house_system = house_system
        self.rulership = rulership

    @property
    def section_name(self) -> str:
        if self.age is not None:
            return f"Annual Profections (Age {self.age})"
        return "Annual Profections"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate profection visualization data."""
        from stellium.engines.profections import ProfectionEngine

        # Create engine
        try:
            engine = ProfectionEngine(chart, self.house_system, self.rulership)
        except ValueError as e:
            return {
                "type": "text",
                "content": f"Could not calculate profections: {e}",
            }

        # Determine current age
        if self.date is not None:
            if isinstance(self.date, str):
                target_date = dt.datetime.fromisoformat(self.date)
            else:
                target_date = self.date
            current_age = engine._calculate_age_at_date(target_date)
        elif self.age is not None:
            current_age = self.age
        else:
            # Default to current date
            current_age = engine._calculate_age_at_date(dt.datetime.now())

        # Build config
        config = ProfectionVizConfig(
            current_age=current_age,
            show_wheel=self.show_wheel,
            show_table=self.show_table,
            compare_ages=self.compare_ages or [current_age, current_age + 1],
        )

        # Generate SVG
        results = []

        if config.show_wheel:
            wheel_svg = self._render_wheel(chart, engine, config)
            results.append(
                (
                    "Annual Profections Wheel",
                    {
                        "type": "svg",
                        "content": wheel_svg,
                        "width": WHEEL_SIZE + WHEEL_MARGIN * 2,
                        "height": WHEEL_SIZE + WHEEL_MARGIN * 2,
                    },
                )
            )

        if config.show_table:
            table_svg = self._render_table(chart, engine, config)
            results.append(
                (
                    "Profection Details",
                    {
                        "type": "svg",
                        "content": table_svg,
                        "width": SVG_WIDTH,
                        "height": 200,
                    },
                )
            )

        if len(results) == 1:
            return results[0][1]
        elif len(results) > 1:
            return {
                "type": "compound",
                "sections": results,
            }
        else:
            return {
                "type": "text",
                "content": "No visualization requested.",
            }

    # =========================================================================
    # Wheel Rendering
    # =========================================================================

    def _render_wheel(
        self,
        chart: CalculatedChart,
        engine,
        config: ProfectionVizConfig,
    ) -> str:
        """Render the profection wheel visualization."""
        size = WHEEL_SIZE + WHEEL_MARGIN * 2
        dwg = svgwrite.Drawing(size=(size, size))

        # Embed font for symbol rendering
        _add_font_defs(dwg)

        # Add background
        dwg.add(
            dwg.rect(
                (0, 0),
                (size, size),
                fill=config.colors["background"],
            )
        )

        center_x = size / 2
        center_y = size / 2

        # Get the sign on the 1st house cusp (natal ASC sign)
        houses = chart.get_houses(engine.house_system)
        asc_sign = houses.get_sign(1)
        asc_sign_idx = SIGNS.index(asc_sign)

        # Draw wheel background
        dwg.add(
            dwg.circle(
                center=(center_x, center_y),
                r=OUTER_RADIUS + 30,
                fill=config.colors["wheel_background"],
                stroke="none",
            )
        )

        # Draw house sectors and age numbers
        self._draw_house_sectors(dwg, center_x, center_y, asc_sign_idx, config)

        # Draw age spiral
        self._draw_age_spiral(dwg, center_x, center_y, config.current_age, config)

        # Draw house labels and zodiac signs
        self._draw_house_labels(dwg, center_x, center_y, houses, config)

        # Draw natal planet positions
        self._draw_natal_planets(dwg, center_x, center_y, chart, houses, config)

        # Title
        dwg.add(
            dwg.text(
                "ANNUAL PROFECTIONS",
                insert=(center_x, 25),
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size="16px",
                font_weight="bold",
                fill=config.colors["text_dark"],
            )
        )

        # Legend
        self._draw_legend(dwg, size - 120, 20, config)

        return dwg.tostring()

    def _draw_house_sectors(
        self,
        dwg: svgwrite.Drawing,
        cx: float,
        cy: float,
        asc_sign_idx: int,
        config: ProfectionVizConfig,
    ) -> None:
        """Draw the 12 house sector divisions, inner labels, and outer rings."""
        # Draw natal placements ring (outermost, light purple)
        dwg.add(
            dwg.circle(
                center=(cx, cy),
                r=NATAL_RING_OUTER,
                fill=config.colors["natal_ring"],
                stroke=config.colors["house_line"],
                stroke_width=1,
            )
        )
        dwg.add(
            dwg.circle(
                center=(cx, cy),
                r=NATAL_RING_INNER,
                fill=config.colors["zodiac_ring"],
                stroke=config.colors["house_line"],
                stroke_width=1,
            )
        )

        # Draw shaded zodiac ring
        dwg.add(
            dwg.circle(
                center=(cx, cy),
                r=ZODIAC_RING_OUTER,
                fill=config.colors["zodiac_ring"],
                stroke=config.colors["house_line"],
                stroke_width=1,
            )
        )
        dwg.add(
            dwg.circle(
                center=(cx, cy),
                r=ZODIAC_RING_INNER,
                fill=config.colors["wheel_background"],
                stroke=config.colors["house_line"],
                stroke_width=1,
            )
        )

        # Draw radial lines for house divisions
        # House 1 starts at 9 o'clock (180°), progressing counter-clockwise
        center_radius = 25  # Where radial lines start
        for house in range(12):
            # 180° is 9 o'clock, subtract to go counter-clockwise
            angle = math.radians(180 - house * 30)
            # Lines go from center circle to outer natal ring
            x1 = cx + center_radius * math.cos(angle)
            y1 = cy + center_radius * math.sin(angle)
            x2 = cx + NATAL_RING_OUTER * math.cos(angle)
            y2 = cy + NATAL_RING_OUTER * math.sin(angle)

            dwg.add(
                dwg.line(
                    (x1, y1),
                    (x2, y2),
                    stroke=config.colors["house_line"],
                    stroke_width=1,
                )
            )

        # Draw center circle to cap off radial lines
        dwg.add(
            dwg.circle(
                center=(cx, cy),
                r=center_radius,
                fill=config.colors["wheel_background"],
                stroke=config.colors["house_line"],
                stroke_width=1,
            )
        )

        # Draw concentric ring outlines for age rings
        for ring in range(NUM_AGE_RINGS + 1):
            radius = AGE_INNER_RADIUS + ring * AGE_RING_WIDTH
            dwg.add(
                dwg.circle(
                    center=(cx, cy),
                    r=radius,
                    fill="none",
                    stroke=config.colors["house_line"],
                    stroke_width=0.5,
                )
            )

        # Draw house labels (1st, 2nd, etc.) in the innermost area
        for house_num in range(1, 13):
            house_sector = house_num - 1
            # Center of each sector
            angle_deg = 180 - (house_sector * 30 + 15)
            angle = math.radians(angle_deg)

            x = cx + HOUSE_LABEL_RADIUS * math.cos(angle)
            y = cy + HOUSE_LABEL_RADIUS * math.sin(angle)

            ordinal = self._get_ordinal(house_num)
            dwg.add(
                dwg.text(
                    ordinal,
                    insert=(x, y + 4),
                    text_anchor="middle",
                    font_family="Arial, sans-serif",
                    font_size="9px",
                    font_weight="bold",
                    fill=config.colors["text_muted"],
                )
            )

    def _draw_age_spiral(
        self,
        dwg: svgwrite.Drawing,
        cx: float,
        cy: float,
        current_age: int | None,
        config: ProfectionVizConfig,
    ) -> None:
        """Draw age numbers in spiral pattern through houses."""
        for age in range(96):  # Ages 0-95
            # Determine which ring (cycle) this age is in
            ring = age // 12  # 0, 1, 2, 3, 4, 5, 6, 7
            if ring >= NUM_RINGS:
                break

            # Determine which house/sector (0-11)
            house_sector = age % 12

            # Calculate position
            # House 1 starts at 9 o'clock (180°), progressing counter-clockwise
            # Offset by 15 degrees to center in sector
            angle_deg = 180 - (house_sector * 30 + 15)
            angle = math.radians(angle_deg)

            # Radius: inner rings are closer to center
            radius = INNER_RADIUS + (ring + 0.5) * RING_WIDTH

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            # Highlight current age
            is_current = current_age is not None and age == current_age
            if is_current:
                # Draw highlight circle behind the number
                dwg.add(
                    dwg.circle(
                        center=(x, y),
                        r=12,
                        fill=config.colors["current_period"],
                        stroke=config.colors["text_dark"],
                        stroke_width=1,
                    )
                )

            # Draw age number
            font_size = "9px" if ring < 4 else "8px"
            font_weight = "bold" if is_current else "normal"
            dwg.add(
                dwg.text(
                    str(age),
                    insert=(x, y + 3),
                    text_anchor="middle",
                    font_family="Arial, sans-serif",
                    font_size=font_size,
                    font_weight=font_weight,
                    fill=config.colors["text_dark"]
                    if is_current
                    else config.colors["age_text"],
                )
            )

    def _draw_house_labels(
        self,
        dwg: svgwrite.Drawing,
        cx: float,
        cy: float,
        houses,
        config: ProfectionVizConfig,
    ) -> None:
        """Draw zodiac signs and their ruling planets in the shaded ring."""
        from stellium.engines.dignities import DIGNITIES

        # Zodiac glyphs go in the center of the shaded outer ring
        zodiac_radius = (ZODIAC_RING_INNER + ZODIAC_RING_OUTER) / 2

        for house_num in range(1, 13):
            # Calculate angle for this house (centered in sector)
            # House 1 starts at 9 o'clock (180°), progressing counter-clockwise
            house_sector = house_num - 1
            angle_deg = 180 - (house_sector * 30 + 15)
            angle = math.radians(angle_deg)

            x = cx + zodiac_radius * math.cos(angle)
            y = cy + zodiac_radius * math.sin(angle)

            # Get zodiac sign for this house
            sign = houses.get_sign(house_num)
            sign_glyph = get_sign_glyph(sign)

            # Get traditional ruler for this sign
            ruler = DIGNITIES[sign]["traditional"]["ruler"]
            ruler_glyph = ""
            if ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[ruler].glyph

            # Draw sign glyph (slightly above center)
            dwg.add(
                dwg.text(
                    sign_glyph,
                    insert=(x, y - 1),
                    text_anchor="middle",
                    font_family="Noto Sans Symbols2, Arial",
                    font_size="14px",
                    fill=config.colors["text_dark"],
                )
            )

            # Draw ruler glyph (below sign glyph)
            dwg.add(
                dwg.text(
                    ruler_glyph,
                    insert=(x, y + 12),
                    text_anchor="middle",
                    font_family="Noto Sans Symbols2, Arial",
                    font_size="10px",
                    fill=config.colors["text_muted"],
                )
            )

    def _draw_natal_planets(
        self,
        dwg: svgwrite.Drawing,
        cx: float,
        cy: float,
        chart: CalculatedChart,
        houses,
        config: ProfectionVizConfig,
    ) -> None:
        """Draw natal planet glyphs in their sign positions in the natal ring."""
        # Planets go in the center of the natal ring
        planet_radius = (NATAL_RING_INNER + NATAL_RING_OUTER) / 2

        # Group planets by sign to handle conjunctions
        planets_by_sign: dict[str, list[str]] = {}
        for pos in chart.get_planets():
            sign = pos.sign
            if sign not in planets_by_sign:
                planets_by_sign[sign] = []
            planets_by_sign[sign].append(pos.name)

        # Also add ASC, MC if available
        for point_name in ["ASC", "MC"]:
            point = chart.get_object(point_name)
            if point:
                sign = point.sign
                if sign not in planets_by_sign:
                    planets_by_sign[sign] = []
                planets_by_sign[sign].append(point_name)

        # Draw each planet
        for sign, planet_names in planets_by_sign.items():
            # Find which house this sign is on
            house_num = None
            for h in range(1, 13):
                if houses.get_sign(h) == sign:
                    house_num = h
                    break

            if house_num is None:
                continue

            # Calculate base angle for this house
            # House 1 at 9 o'clock (180°), counter-clockwise, centered in sector
            house_sector = house_num - 1
            base_angle_deg = 180 - (house_sector * 30 + 15)

            # Spread multiple planets within the sector
            num_planets = len(planet_names)
            for i, planet_name in enumerate(planet_names):
                # Offset within sector
                if num_planets == 1:
                    offset = 0
                else:
                    offset = (i - (num_planets - 1) / 2) * 8

                angle = math.radians(base_angle_deg + offset)
                x = cx + planet_radius * math.cos(angle)
                y = cy + planet_radius * math.sin(angle)

                # Get planet glyph
                if planet_name in CELESTIAL_REGISTRY:
                    glyph = CELESTIAL_REGISTRY[planet_name].glyph
                else:
                    glyph = planet_name[:2]

                dwg.add(
                    dwg.text(
                        glyph,
                        insert=(x, y + 4),
                        text_anchor="middle",
                        font_family="Noto Sans Symbols2, Arial",
                        font_size="12px",
                        fill=config.colors["text_dark"],
                    )
                )

    def _draw_legend(
        self,
        dwg: svgwrite.Drawing,
        x: float,
        y: float,
        config: ProfectionVizConfig,
    ) -> None:
        """Draw the legend showing current period and natal placements indicators."""
        # Legend box (taller to fit both entries)
        dwg.add(
            dwg.rect(
                (x, y),
                (115, 45),
                fill="white",
                stroke=config.colors["legend_border"],
                stroke_width=1,
                rx=3,
                ry=3,
            )
        )

        # Current period indicator
        dwg.add(
            dwg.rect(
                (x + 8, y + 7),
                (12, 12),
                fill=config.colors["current_period"],
                stroke=config.colors["text_dark"],
                stroke_width=1,
            )
        )

        dwg.add(
            dwg.text(
                "Current period",
                insert=(x + 26, y + 16),
                font_family="Arial, sans-serif",
                font_size="9px",
                fill=config.colors["text_dark"],
            )
        )

        # Natal placements indicator
        dwg.add(
            dwg.rect(
                (x + 8, y + 26),
                (12, 12),
                fill=config.colors["natal_ring"],
                stroke=config.colors["text_dark"],
                stroke_width=1,
            )
        )

        dwg.add(
            dwg.text(
                "Natal placements",
                insert=(x + 26, y + 35),
                font_family="Arial, sans-serif",
                font_size="9px",
                fill=config.colors["text_dark"],
            )
        )

    def _get_ordinal(self, n: int) -> str:
        """Get ordinal string for a number (1st, 2nd, 3rd, etc.)."""
        if 11 <= n <= 13:
            return f"{n}th"
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    # =========================================================================
    # Table Rendering
    # =========================================================================

    def _render_table(
        self,
        chart: CalculatedChart,
        engine,
        config: ProfectionVizConfig,
    ) -> str:
        """Render the profection details table."""
        width = SVG_WIDTH
        height = 200
        dwg = svgwrite.Drawing(size=(width, height))

        # Embed font
        _add_font_defs(dwg)

        # Add background
        dwg.add(
            dwg.rect(
                (0, 0),
                (width, height),
                fill=config.colors["background"],
            )
        )

        # Get ages to compare
        ages = config.compare_ages or [config.current_age, config.current_age + 1]

        # Table layout
        row_labels = [
            "SOLAR RETURN\n(NATAL LOCATION)",
            "PROFECTED HOUSE",
            "ANNUAL TIMELORD",
            "NATAL PLACEMENTS IN\nPROFECTED HOUSE",
            "TIMELORD'S NATAL POSITION",
            "TIMELORD ALSO RULES",
        ]

        label_width = 180
        col_width = (width - label_width) / len(ages)
        row_height = 25
        start_x = 10
        start_y = 10

        # Draw header row (ages)
        for i, age in enumerate(ages):
            x = start_x + label_width + i * col_width
            dwg.add(
                dwg.rect(
                    (x, start_y),
                    (col_width - 2, row_height),
                    fill=config.colors["table_header"],
                    rx=2,
                    ry=2,
                )
            )
            dwg.add(
                dwg.text(
                    f"AGE {age}",
                    insert=(x + col_width / 2, start_y + 17),
                    text_anchor="middle",
                    font_family="Arial, sans-serif",
                    font_size="11px",
                    font_weight="bold",
                    fill="white",
                )
            )

        start_y += row_height + 5

        # Draw data rows
        for row_idx, label in enumerate(row_labels):
            y = start_y + row_idx * row_height

            # Draw row label
            # Handle multi-line labels
            label_lines = label.split("\n")
            for line_idx, line in enumerate(label_lines):
                line_y = y + 15 + (line_idx - len(label_lines) / 2 + 0.5) * 10
                dwg.add(
                    dwg.text(
                        line,
                        insert=(start_x, line_y),
                        font_family="Arial, sans-serif",
                        font_size="8px",
                        fill=config.colors["text_muted"],
                    )
                )

            # Draw data cells for each age
            for i, age in enumerate(ages):
                x = start_x + label_width + i * col_width

                # Get profection data for this age
                profection = engine.annual(age)
                cell_value = self._get_table_cell_value(
                    row_idx, age, profection, chart, engine
                )

                # Use Arial for text-heavy rows (solar return), symbol font for others
                if row_idx == 0:  # Solar return - text only
                    font_family = "Arial, sans-serif"
                    font_size = "9px"
                else:
                    font_family = "Noto Sans Symbols2, Arial"
                    font_size = "11px"

                dwg.add(
                    dwg.text(
                        cell_value,
                        insert=(x + col_width / 2, y + 16),
                        text_anchor="middle",
                        font_family=font_family,
                        font_size=font_size,
                        fill=config.colors["text_dark"],
                    )
                )

            # Draw row separator
            if row_idx < len(row_labels) - 1:
                dwg.add(
                    dwg.line(
                        (start_x, y + row_height),
                        (width - 10, y + row_height),
                        stroke=config.colors["table_border"],
                        stroke_width=0.5,
                    )
                )

        return dwg.tostring()

    def _get_table_cell_value(
        self,
        row_idx: int,
        age: int,
        profection,
        chart: CalculatedChart,
        engine,
    ) -> str:
        """Get the value for a specific table cell."""
        if row_idx == 0:
            # Solar return date
            # Calculate solar return for this age
            try:
                sr_date = self._calculate_solar_return_date(chart, age)
                return sr_date.strftime("%d %b %Y, %I:%M%p")
            except Exception:
                return "—"

        elif row_idx == 1:
            # Profected house
            sign_glyph = get_sign_glyph(profection.profected_sign)
            return f"{sign_glyph} {profection.profected_house}"

        elif row_idx == 2:
            # Annual timelord
            ruler_glyph = ""
            if profection.ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[profection.ruler].glyph
            return ruler_glyph

        elif row_idx == 3:
            # Natal placements in profected house
            if profection.planets_in_house:
                glyphs = []
                for planet in profection.planets_in_house:
                    if planet.name in CELESTIAL_REGISTRY:
                        glyphs.append(CELESTIAL_REGISTRY[planet.name].glyph)
                return " ".join(glyphs) if glyphs else "—"
            return "—"

        elif row_idx == 4:
            # Timelord's natal position
            if profection.ruler_position:
                sign_glyph = get_sign_glyph(profection.ruler_position.sign)
                house = profection.ruler_house or "?"
                return f"{sign_glyph} {house}"
            return "—"

        elif row_idx == 5:
            # Timelord also rules (other signs ruled by this planet)
            other_signs = self._get_other_ruled_signs(
                profection.ruler, profection.profected_sign
            )
            if other_signs:
                glyphs_houses = []
                houses = chart.get_houses(engine.house_system)
                for sign in other_signs:
                    sign_glyph = get_sign_glyph(sign)
                    # Find which house this sign is on
                    for h in range(1, 13):
                        if houses.get_sign(h) == sign:
                            glyphs_houses.append(f"{sign_glyph} {h}")
                            break
                return " ".join(glyphs_houses) if glyphs_houses else "—"
            return "—"

        return "—"

    def _calculate_solar_return_date(
        self, chart: CalculatedChart, age: int
    ) -> dt.datetime:
        """Calculate the solar return date for a given age."""
        from stellium.utils.planetary_crossing import find_nth_return

        natal_sun = chart.get_object("Sun")
        if natal_sun is None:
            raise ValueError("No Sun in chart")

        birth_jd = chart.datetime.julian_day

        if age == 0:
            # Return birth date for age 0
            return chart.datetime.utc_datetime

        # Find the nth solar return
        sr_jd = find_nth_return("Sun", natal_sun.longitude, birth_jd, n=age)

        # Convert JD to datetime
        from stellium.utils.time import julian_day_to_datetime

        return julian_day_to_datetime(sr_jd)

    def _get_other_ruled_signs(self, ruler: str, current_sign: str) -> list[str]:
        """Get other signs ruled by the same planet."""
        from stellium.engines.dignities import DIGNITIES

        other_signs = []
        for sign, dignity in DIGNITIES.items():
            if sign != current_sign:
                if dignity["traditional"]["ruler"] == ruler:
                    other_signs.append(sign)
        return other_signs
