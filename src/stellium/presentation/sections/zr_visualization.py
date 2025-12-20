"""
Zodiacal Releasing visualization section.

Generates SVG timeline visualizations similar to Honeycomb Collective style:
- Page 1: Overview (natal angles chart + period length reference table)
- Page 2: Stacked L1/L2/L3 timelines with peak shapes
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import svgwrite

from stellium.core.models import CalculatedChart, ZRPeriod, ZRTimeline
from stellium.core.registry import CELESTIAL_REGISTRY
from stellium.engines.releasing import PLANET_PERIODS

from ._utils import get_sign_glyph

if TYPE_CHECKING:
    from datetime import date


# =============================================================================
# Constants & Styling
# =============================================================================

# Honeycomb-inspired color palette
COLORS = {
    "background": "#ffffff",
    "current_period": "#f5e6c8",  # Warm cream/yellow highlight
    "default_period": "#f0e8d8",  # Default period fill
    "post_loosing": "#e8e0d0",  # Lighter shade for post-LB
    "loosing_bond_stroke": "#333333",  # Dark outline for LB
    "peak_stroke": "#4a3353",  # Purple stroke for peaks
    "text_dark": "#2d2330",
    "text_muted": "#6b4d6e",
    "grid_line": "#d0c8c0",
    "label_badge": "#4a3353",
    "label_badge_text": "#ffffff",
}

# Dimensions
SVG_WIDTH = 800
OVERVIEW_HEIGHT = 600
TIMELINE_HEIGHT = 500

# Timeline level heights and spacing
LEVEL_HEIGHT = 120  # Height allocated per timeline level
LEVEL_SPACING = 30  # Vertical spacing between levels
TIMELINE_MARGIN_TOP = 80
TIMELINE_MARGIN_BOTTOM = 40
TIMELINE_MARGIN_X = 60

# Peak heights based on angularity
MAJOR_PEAK_HEIGHT = 50  # 10th from Lot
MODERATE_PEAK_HEIGHT = 35  # 4th/7th from Lot
MINOR_PEAK_HEIGHT = 20  # 1st from Lot
BASELINE_HEIGHT = 5  # Non-angular

# Sign order (zodiacal)
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

# Planet period order (for table)
PERIOD_RULERS = ["Venus", "Jupiter", "Mars", "Sun", "Mercury", "Moon", "Saturn"]


@dataclass
class ZRVizConfig:
    """Configuration for ZR visualization."""

    # Date range
    year: int | None = None
    start_date: date | None = None
    end_date: date | None = None

    # Display options
    levels: tuple[int, ...] = (1, 2, 3)
    highlight_date: dt.datetime | None = None
    show_loosing_bond: bool = True
    show_overview: bool = True
    show_timeline: bool = True

    # Styling
    width: int = SVG_WIDTH
    colors: dict = field(default_factory=lambda: COLORS.copy())


class ZRVisualizationSection:
    """
    Zodiacal Releasing visualization section.

    Generates SVG timeline visualizations in Honeycomb Collective style:
    - Overview page: natal angles chart + period length reference
    - Timeline page: stacked L1/L2/L3 timelines with peak shapes

    Returns SVG content that can be embedded in PDF planners or reports.

    Example:
        section = ZRVisualizationSection(
            lot="Part of Fortune",
            year=2025,
            output="timeline"  # or "overview" or "both"
        )
        data = section.generate_data(chart)
        # data["content"] contains SVG string
    """

    def __init__(
        self,
        lot: str = "Part of Fortune",
        year: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        levels: tuple[int, ...] = (1, 2, 3),
        highlight_date: dt.datetime | None = None,
        output: str = "both",  # "overview", "timeline", or "both"
    ) -> None:
        """
        Initialize ZR visualization section.

        Args:
            lot: Which lot to visualize (e.g., "Part of Fortune")
            year: Year to visualize (sets Jan 1 - Dec 31 range)
            start_date: Custom start date (alternative to year)
            end_date: Custom end date (alternative to year)
            levels: Which levels to show in timeline (default: 1, 2, 3)
            highlight_date: Date to highlight as "current" (default: now)
            output: What to generate - "overview", "timeline", or "both"
        """
        self.lot = lot
        self.year = year
        self.start_date = start_date
        self.end_date = end_date
        self.levels = levels
        self.highlight_date = highlight_date or dt.datetime.now(dt.UTC)
        self.output = output

    @property
    def section_name(self) -> str:
        return f"Zodiacal Releasing Visualization ({self.lot})"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate ZR visualization data.

        Returns:
            Dict with type="svg" or type="compound" containing SVG content(s)
        """
        # Check if ZR data exists
        if "zodiacal_releasing" not in chart.metadata:
            return {
                "type": "text",
                "content": (
                    "Zodiacal Releasing not calculated. Add ZodiacalReleasingAnalyzer:\n\n"
                    "  from stellium.engines.releasing import ZodiacalReleasingAnalyzer\n\n"
                    "  chart = (\n"
                    "      ChartBuilder.from_native(native)\n"
                    "      .add_analyzer(ZodiacalReleasingAnalyzer(['Part of Fortune']))\n"
                    "      .calculate()\n"
                    "  )"
                ),
            }

        zr_data = chart.metadata["zodiacal_releasing"]

        if self.lot not in zr_data:
            available = ", ".join(zr_data.keys())
            return {
                "type": "text",
                "content": f"Lot '{self.lot}' not found. Available: {available}",
            }

        timeline: ZRTimeline = zr_data[self.lot]

        # Determine date range
        if self.year:
            start = dt.date(self.year, 1, 1)
            end = dt.date(self.year, 12, 31)
        elif self.start_date and self.end_date:
            start = self.start_date
            end = self.end_date
        else:
            # Default to current year
            now = dt.datetime.now()
            start = dt.date(now.year, 1, 1)
            end = dt.date(now.year, 12, 31)

        # Build config
        config = ZRVizConfig(
            year=self.year,
            start_date=start,
            end_date=end,
            levels=self.levels,
            highlight_date=self.highlight_date,
            show_overview=self.output in ("overview", "both"),
            show_timeline=self.output in ("timeline", "both"),
        )

        # Generate SVG(s)
        results = []

        if config.show_overview:
            overview_svg = self._render_overview(timeline, chart, config)
            results.append(
                (
                    "Zodiacal Releasing Overview",
                    {
                        "type": "svg",
                        "content": overview_svg,
                        "width": SVG_WIDTH,
                        "height": OVERVIEW_HEIGHT,
                    },
                )
            )

        if config.show_timeline:
            timeline_svg = self._render_timeline(timeline, chart, config)
            results.append(
                (
                    f"Zodiacal Releasing from {self.lot}",
                    {
                        "type": "svg",
                        "content": timeline_svg,
                        "width": SVG_WIDTH,
                        "height": TIMELINE_HEIGHT,
                    },
                )
            )

        if len(results) == 1:
            # Single output - return directly
            return results[0][1]
        else:
            # Multiple outputs - return as compound
            return {
                "type": "compound",
                "sections": results,
            }

    # =========================================================================
    # Overview Page Rendering
    # =========================================================================

    def _render_overview(
        self, timeline: ZRTimeline, chart: CalculatedChart, config: ZRVizConfig
    ) -> str:
        """Render the overview page with natal angles and period length table."""
        dwg = svgwrite.Drawing(size=(config.width, OVERVIEW_HEIGHT))

        # Add background
        dwg.add(
            dwg.rect(
                (0, 0),
                (config.width, OVERVIEW_HEIGHT),
                fill=config.colors["background"],
            )
        )

        y_offset = 30

        # Title
        dwg.add(
            dwg.text(
                "ZODIACAL RELEASING OVERVIEW",
                insert=(config.width / 2, y_offset),
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size="18px",
                font_weight="bold",
                fill=config.colors["text_dark"],
            )
        )

        y_offset += 40

        # Section 1: Natal Fortune Angles
        y_offset = self._render_natal_angles_section(
            dwg, timeline, chart, config, y_offset
        )

        y_offset += 30

        # Section 2: Period Length Reference
        self._render_period_length_table(dwg, config, y_offset)

        return dwg.tostring()

    def _render_natal_angles_section(
        self,
        dwg: svgwrite.Drawing,
        timeline: ZRTimeline,
        chart: CalculatedChart,
        config: ZRVizConfig,
        y_start: float,
    ) -> float:
        """Render the natal angles chart showing peak periods by sign."""
        # Section header
        self._add_section_header(dwg, "NATAL FORTUNE ANGLES", 40, y_start, config)
        y_offset = y_start + 30

        # Description text
        dwg.add(
            dwg.text(
                "Peak periods based on angular relationship to the Lot.",
                insert=(40, y_offset),
                font_family="Arial, sans-serif",
                font_size="10px",
                fill=config.colors["text_muted"],
            )
        )
        y_offset += 25

        # Calculate angular signs from lot
        lot_sign_idx = SIGNS.index(timeline.lot_sign)
        angular_positions = {
            lot_sign_idx: 1,  # 1st from Lot
            (lot_sign_idx + 3) % 12: 4,  # 4th from Lot
            (lot_sign_idx + 6) % 12: 7,  # 7th from Lot
            (lot_sign_idx + 9) % 12: 10,  # 10th from Lot (peak!)
        }

        # Get natal planets by sign
        planets_by_sign: dict[str, list[str]] = {}
        for pos in chart.positions:
            if pos.sign not in planets_by_sign:
                planets_by_sign[pos.sign] = []
            glyph = CELESTIAL_REGISTRY.get(pos.name, None)
            planets_by_sign[pos.sign].append(glyph.glyph if glyph else pos.name[:2])

        # Draw the angular chart
        chart_width = config.width - 80
        cell_width = chart_width / 12
        chart_x = 40

        # Draw peak indicators (triangular shapes above)
        for i in range(12):
            sign_idx = (lot_sign_idx + i) % 12
            x = chart_x + i * cell_width
            angle = angular_positions.get(sign_idx)

            if angle == 10:  # Major peak
                self._draw_peak_indicator(
                    dwg, x + cell_width / 2, y_offset, 25, config.colors["peak_stroke"]
                )
            elif angle in (4, 7):  # Moderate peak
                self._draw_peak_indicator(
                    dwg, x + cell_width / 2, y_offset, 15, config.colors["peak_stroke"]
                )
            elif angle == 1:  # Minor peak
                self._draw_peak_indicator(
                    dwg, x + cell_width / 2, y_offset, 8, config.colors["peak_stroke"]
                )

        y_offset += 35

        # Sign row with house numbers
        for i in range(12):
            sign_idx = (lot_sign_idx + i) % 12
            sign = SIGNS[sign_idx]
            x = chart_x + i * cell_width

            # Sign glyph
            glyph = get_sign_glyph(sign)
            dwg.add(
                dwg.text(
                    glyph,
                    insert=(x + cell_width / 2, y_offset),
                    text_anchor="middle",
                    font_family="Noto Sans Symbols 2, Arial",
                    font_size="16px",
                    fill=config.colors["text_dark"],
                )
            )

            # House number below
            dwg.add(
                dwg.text(
                    str(i + 1),
                    insert=(x + cell_width / 2, y_offset + 18),
                    text_anchor="middle",
                    font_family="Arial, sans-serif",
                    font_size="10px",
                    fill=config.colors["text_muted"],
                )
            )

        y_offset += 35

        # Planets row
        for i in range(12):
            sign_idx = (lot_sign_idx + i) % 12
            sign = SIGNS[sign_idx]
            x = chart_x + i * cell_width

            if sign in planets_by_sign:
                planet_glyphs = planets_by_sign[sign]
                for j, glyph in enumerate(planet_glyphs[:4]):  # Max 4 per cell
                    dwg.add(
                        dwg.text(
                            glyph,
                            insert=(x + cell_width / 2, y_offset + j * 14),
                            text_anchor="middle",
                            font_family="Noto Sans Symbols 2, Arial",
                            font_size="12px",
                            fill=config.colors["text_dark"],
                        )
                    )

        return y_offset + 60

    def _draw_peak_indicator(
        self, dwg: svgwrite.Drawing, x: float, y: float, height: float, color: str
    ) -> None:
        """Draw a triangular peak indicator."""
        points = [
            (x - height / 2, y),
            (x, y - height),
            (x + height / 2, y),
        ]
        dwg.add(dwg.polygon(points, fill=color, opacity=0.3))

    def _render_period_length_table(
        self, dwg: svgwrite.Drawing, config: ZRVizConfig, y_start: float
    ) -> None:
        """Render the period length reference table."""
        self._add_section_header(dwg, "LENGTH OF GENERAL PERIODS", 40, y_start, config)
        y_offset = y_start + 30

        # Description
        dwg.add(
            dwg.text(
                "Period length by planetary ruler. Level durations scale proportionally.",
                insert=(40, y_offset),
                font_family="Arial, sans-serif",
                font_size="10px",
                fill=config.colors["text_muted"],
            )
        )
        y_offset += 25

        # Table headers
        headers = [
            "Ruler",
            "Signs",
            "L1 (Years)",
            "L2 (Months)",
            "L3 (Days)",
            "L4 (Hours)",
        ]
        col_widths = [80, 140, 80, 80, 80, 80]
        x_start = 60

        # Header row
        x = x_start
        for i, header in enumerate(headers):
            dwg.add(
                dwg.text(
                    header,
                    insert=(x, y_offset),
                    font_family="Arial, sans-serif",
                    font_size="10px",
                    font_weight="bold",
                    fill=config.colors["text_dark"],
                )
            )
            x += col_widths[i]

        y_offset += 18

        # Draw header line
        dwg.add(
            dwg.line(
                (x_start, y_offset - 5),
                (x_start + sum(col_widths), y_offset - 5),
                stroke=config.colors["grid_line"],
                stroke_width=1,
            )
        )

        # Data rows
        ruler_signs = {
            "Venus": ["Taurus", "Libra"],
            "Jupiter": ["Sagittarius", "Pisces"],
            "Mars": ["Aries", "Scorpio"],
            "Sun": ["Leo"],
            "Mercury": ["Gemini", "Virgo"],
            "Moon": ["Cancer"],
            "Saturn": ["Capricorn", "Aquarius"],
        }

        for ruler in PERIOD_RULERS:
            years = PLANET_PERIODS[ruler]
            signs = ruler_signs[ruler]

            # Get ruler glyph
            ruler_info = CELESTIAL_REGISTRY.get(ruler)
            ruler_display = f"{ruler_info.glyph} {ruler}" if ruler_info else ruler

            # Format signs with glyphs
            sign_display = " ".join(get_sign_glyph(s) for s in signs)

            # Calculate level durations
            months = years  # L2 months = L1 years
            days = years * 30.437 / 12  # Approximate
            hours = days * 24 / 30  # Approximate

            row_data = [
                ruler_display,
                sign_display,
                f"{years}",
                f"{months}",
                f"{days:.1f}",
                f"{hours:.0f}",
            ]

            x = x_start
            for i, cell in enumerate(row_data):
                dwg.add(
                    dwg.text(
                        cell,
                        insert=(x, y_offset),
                        font_family="Noto Sans Symbols 2, Arial, sans-serif",
                        font_size="11px",
                        fill=config.colors["text_dark"],
                    )
                )
                x += col_widths[i]

            y_offset += 20

    def _add_section_header(
        self,
        dwg: svgwrite.Drawing,
        text: str,
        x: float,
        y: float,
        config: ZRVizConfig,
    ) -> None:
        """Add a styled section header badge."""
        # Background badge
        text_width = len(text) * 7 + 20
        dwg.add(
            dwg.rect(
                (x, y - 14),
                (text_width, 20),
                rx=3,
                ry=3,
                fill=config.colors["label_badge"],
            )
        )

        # Text
        dwg.add(
            dwg.text(
                text,
                insert=(x + 10, y),
                font_family="Arial, sans-serif",
                font_size="11px",
                font_weight="bold",
                fill=config.colors["label_badge_text"],
            )
        )

    # =========================================================================
    # Timeline Page Rendering
    # =========================================================================

    def _render_timeline(
        self, timeline: ZRTimeline, chart: CalculatedChart, config: ZRVizConfig
    ) -> str:
        """Render the timeline page with stacked L1/L2/L3 views."""
        # Calculate height based on number of levels
        num_levels = len(config.levels)
        total_height = (
            TIMELINE_MARGIN_TOP
            + num_levels * LEVEL_HEIGHT
            + (num_levels - 1) * LEVEL_SPACING
            + TIMELINE_MARGIN_BOTTOM
        )

        dwg = svgwrite.Drawing(size=(config.width, total_height))

        # Add background
        dwg.add(
            dwg.rect(
                (0, 0), (config.width, total_height), fill=config.colors["background"]
            )
        )

        # Title
        lot_short = self.lot.replace("Part of ", "")
        dwg.add(
            dwg.text(
                f"ZODIACAL RELEASING FROM {lot_short.upper()}",
                insert=(config.width / 2, 30),
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size="18px",
                font_weight="bold",
                fill=config.colors["text_dark"],
            )
        )

        # Legend
        self._render_legend(dwg, config.width - 180, 20, config)

        # Render each level
        y_offset = TIMELINE_MARGIN_TOP

        for level in config.levels:
            self._render_level(dwg, timeline, chart, config, level, y_offset)
            y_offset += LEVEL_HEIGHT + LEVEL_SPACING

        return dwg.tostring()

    def _render_legend(
        self, dwg: svgwrite.Drawing, x: float, y: float, config: ZRVizConfig
    ) -> None:
        """Render the legend showing what colors/patterns mean."""
        items = [
            (config.colors["current_period"], "Current period"),
            (config.colors["loosing_bond_stroke"], "Loosing of the bond"),
            (config.colors["post_loosing"], "Post-loosing period"),
        ]

        for i, (color, label) in enumerate(items):
            iy = y + i * 16

            # Color swatch
            if "stroke" in color or color == config.colors["loosing_bond_stroke"]:
                # Draw outlined box
                dwg.add(
                    dwg.rect(
                        (x, iy), (12, 12), fill="none", stroke=color, stroke_width=2
                    )
                )
            else:
                dwg.add(dwg.rect((x, iy), (12, 12), fill=color))

            # Label
            dwg.add(
                dwg.text(
                    label,
                    insert=(x + 18, iy + 10),
                    font_family="Arial, sans-serif",
                    font_size="9px",
                    fill=config.colors["text_muted"],
                )
            )

    def _render_level(
        self,
        dwg: svgwrite.Drawing,
        timeline: ZRTimeline,
        chart: CalculatedChart,
        config: ZRVizConfig,
        level: int,
        y_offset: float,
    ) -> None:
        """Render a single timeline level."""
        # Level label
        level_names = {1: "LIFETIME VIEW", 2: "DECADE VIEW", 3: "YEAR VIEW"}
        level_name = level_names.get(level, f"LEVEL {level}")

        # Level badge
        self._add_section_header(
            dwg, f"LEVEL {level}", TIMELINE_MARGIN_X, y_offset, config
        )

        dwg.add(
            dwg.text(
                level_name,
                insert=(TIMELINE_MARGIN_X + 70, y_offset),
                font_family="Arial, sans-serif",
                font_size="10px",
                fill=config.colors["text_muted"],
            )
        )

        y_offset += 20

        # Get periods for this level
        periods = timeline.periods.get(level, [])
        if not periods:
            return

        # Determine visible date range based on level
        if level == 1:
            # Lifetime view: show all L1 periods
            visible_start = timeline.birth_date
            visible_end = timeline.birth_date + dt.timedelta(days=120 * 365.25)
        elif level == 2:
            # Decade view: ~10 years centered on highlight date
            center = config.highlight_date
            visible_start = center - dt.timedelta(days=5 * 365.25)
            visible_end = center + dt.timedelta(days=5 * 365.25)
        else:
            # Year view: use configured date range
            visible_start = dt.datetime.combine(config.start_date, dt.time.min)
            visible_end = dt.datetime.combine(config.end_date, dt.time.max)

        # Make datetime-aware if needed
        if visible_start.tzinfo is None:
            visible_start = visible_start.replace(tzinfo=dt.UTC)
        if visible_end.tzinfo is None:
            visible_end = visible_end.replace(tzinfo=dt.UTC)

        # Filter to visible periods
        visible_periods = [
            p for p in periods if p.end > visible_start and p.start < visible_end
        ]

        if not visible_periods:
            return

        # Calculate x-axis scale
        timeline_width = config.width - 2 * TIMELINE_MARGIN_X
        total_span = (visible_end - visible_start).total_seconds()

        def date_to_x(d: dt.datetime) -> float:
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.UTC)
            elapsed = (d - visible_start).total_seconds()
            return TIMELINE_MARGIN_X + (elapsed / total_span) * timeline_width

        # Baseline y position
        baseline_y = y_offset + LEVEL_HEIGHT - 30

        # Draw each period
        for period in visible_periods:
            x1 = max(date_to_x(period.start), TIMELINE_MARGIN_X)
            x2 = min(date_to_x(period.end), config.width - TIMELINE_MARGIN_X)

            if x2 <= x1:
                continue

            self._draw_period_shape(
                dwg,
                period,
                x1,
                x2,
                baseline_y,
                config,
                is_current=self._is_current_period(period, config),
            )

        # Draw date labels along bottom
        self._render_date_labels(
            dwg, visible_periods, date_to_x, baseline_y + 15, config
        )

    def _draw_period_shape(
        self,
        dwg: svgwrite.Drawing,
        period: ZRPeriod,
        x1: float,
        x2: float,
        baseline_y: float,
        config: ZRVizConfig,
        is_current: bool = False,
    ) -> None:
        """
        Draw the characteristic ZR period shape:

             ___________
            /           \\
           /   PLATEAU   \\
          /               \\
        START            END
        """
        # Calculate peak height based on angularity
        if period.is_peak:  # 10th from Lot
            peak_height = MAJOR_PEAK_HEIGHT
        elif period.angle_from_lot in (4, 7):
            peak_height = MODERATE_PEAK_HEIGHT
        elif period.angle_from_lot == 1:
            peak_height = MINOR_PEAK_HEIGHT
        else:
            peak_height = BASELINE_HEIGHT

        # Calculate shape points
        width = x2 - x1
        prep_width = width * 0.15  # Preparatory phase
        follow_width = width * 0.15  # Follow-through phase

        points = [
            (x1, baseline_y),  # Start bottom
            (x1 + prep_width, baseline_y - peak_height),  # Top of prep slope
            (x2 - follow_width, baseline_y - peak_height),  # End of plateau
            (x2, baseline_y),  # End bottom
        ]

        # Determine fill color
        if is_current:
            fill = config.colors["current_period"]
        elif period.is_loosing_bond:
            fill = config.colors["post_loosing"]
        else:
            fill = config.colors["default_period"]

        # Draw shape
        stroke = (
            config.colors["peak_stroke"]
            if period.is_peak
            else config.colors["grid_line"]
        )
        stroke_width = 1.5 if period.is_peak else 0.5

        dwg.add(
            dwg.polygon(
                points,
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width,
            )
        )

        # Add loosing of bond indicator (thick outline)
        if period.is_loosing_bond:
            dwg.add(
                dwg.polygon(
                    points,
                    fill="none",
                    stroke=config.colors["loosing_bond_stroke"],
                    stroke_width=2,
                )
            )

        # Add sign glyph at top center of plateau
        if width > 30:  # Only if there's room
            glyph = get_sign_glyph(period.sign)
            center_x = (x1 + prep_width + x2 - follow_width) / 2
            dwg.add(
                dwg.text(
                    glyph,
                    insert=(center_x, baseline_y - peak_height - 5),
                    text_anchor="middle",
                    font_family="Noto Sans Symbols 2, Arial",
                    font_size="14px",
                    fill=config.colors["text_dark"],
                )
            )

    def _render_date_labels(
        self,
        dwg: svgwrite.Drawing,
        periods: list[ZRPeriod],
        date_to_x: callable,
        y: float,
        config: ZRVizConfig,
    ) -> None:
        """Render date labels at period boundaries."""
        labeled_positions: set[int] = set()

        for period in periods:
            x = date_to_x(period.start)
            x_rounded = int(x / 50) * 50  # Avoid overlapping labels

            if x_rounded not in labeled_positions:
                labeled_positions.add(x_rounded)

                # Format date based on period length
                if period.length_days > 365:
                    date_str = period.start.strftime("%b %Y")
                elif period.length_days > 30:
                    date_str = period.start.strftime("%b %Y")
                else:
                    date_str = period.start.strftime("%d %b")

                dwg.add(
                    dwg.text(
                        date_str,
                        insert=(x, y),
                        text_anchor="start",
                        font_family="Arial, sans-serif",
                        font_size="8px",
                        fill=config.colors["text_muted"],
                        transform=f"rotate(-45, {x}, {y})",
                    )
                )

    def _is_current_period(self, period: ZRPeriod, config: ZRVizConfig) -> bool:
        """Check if a period contains the highlight date."""
        highlight = config.highlight_date
        if highlight.tzinfo is None:
            highlight = highlight.replace(tzinfo=dt.UTC)

        start = period.start
        end = period.end
        if start.tzinfo is None:
            start = start.replace(tzinfo=dt.UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=dt.UTC)

        return start <= highlight < end
