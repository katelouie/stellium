"""
Zodiacal Releasing visualization section.

Generates SVG timeline visualizations similar to Honeycomb Collective style:
- Page 1: Overview (natal angles chart + period length reference table)
- Page 2: Stacked L1/L2/L3 timelines with peak shapes
"""

from __future__ import annotations

import base64
import datetime as dt
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import svgwrite

from stellium.core.models import CalculatedChart, ZRPeriod, ZRTimeline
from stellium.core.registry import CELESTIAL_REGISTRY
from stellium.engines.releasing import PLANET_PERIODS

from ._utils import get_sign_glyph

# =============================================================================
# Font Embedding Utilities
# =============================================================================


@lru_cache(maxsize=1)
def _get_embedded_font_style() -> str:
    """
    Get CSS style with embedded Noto Sans Symbols 2 font (base64 encoded).

    This ensures zodiac and planet glyphs render correctly in PDFs
    without requiring the font to be installed on the viewing system.

    Returns:
        CSS style string with @font-face declaration
    """
    # Find the font file
    font_dir = os.path.join(
        os.path.dirname(__file__),  # sections/
        "..",  # presentation/
        "..",  # stellium/
        "..",  # src/
        "..",  # project root
        "assets",
        "fonts",
    )
    font_path = os.path.join(font_dir, "NotoSansSymbols2-Regular.ttf")

    # Also check NotoSansSymbols-Regular as fallback
    if not os.path.exists(font_path):
        font_path = os.path.join(font_dir, "NotoSansSymbols-Regular.ttf")

    if not os.path.exists(font_path):
        # Can't embed font, return empty style
        return ""

    # Read and encode font
    with open(font_path, "rb") as f:
        font_data = f.read()
    font_base64 = base64.b64encode(font_data).decode("ascii")

    return f"""
        @font-face {{
            font-family: 'Noto Sans Symbols2';
            src: url('data:font/truetype;base64,{font_base64}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
    """


def _add_font_defs(dwg: svgwrite.Drawing) -> None:
    """
    Add embedded font definitions to an SVG drawing.

    Args:
        dwg: The svgwrite Drawing to add font defs to
    """
    font_style = _get_embedded_font_style()
    if font_style:
        # Add style element to defs
        style = dwg.style(font_style)
        dwg.defs.add(style)


if TYPE_CHECKING:
    from datetime import date


# =============================================================================
# Constants & Styling
# =============================================================================

# Honeycomb-inspired color palette
COLORS = {
    "background": "#ffffff",
    "current_period": "#d8c8e8",  # Light purple highlight for current period
    "default_period": "#f0e8d8",  # Default period fill (cream)
    "post_loosing": "#e8e0d0",  # Lighter shade for post-LB
    "loosing_bond_stroke": "#2d2330",  # Dark outline for LB (thick)
    "peak_stroke": "#4a3353",  # Purple stroke for angular peaks
    "text_dark": "#2d2330",
    "text_muted": "#6b4d6e",
    "grid_line": "#d0c8c0",
    "label_badge": "#4a3353",
    "label_badge_text": "#ffffff",
}

# Dimensions
SVG_WIDTH = 800
OVERVIEW_HEIGHT = 520  # Bar graph + period table (explanation moved to Typst)
TIMELINE_HEIGHT = 500

# Timeline level heights and spacing
LEVEL_HEIGHT = 140  # Height allocated per timeline level (increased for taller bars)
LEVEL_SPACING = 30  # Vertical spacing between levels
TIMELINE_MARGIN_TOP = 80
TIMELINE_MARGIN_BOTTOM = 40
TIMELINE_MARGIN_X = 60

# Bar heights based on position from lot (matching overview bar graph pattern)
# Heights are proportional - angular signs are tallest, adjacent signs step down
BAR_HEIGHTS = {
    1: 70,  # 1st from lot (primary angular)
    2: 52,  # Adjacent to 1
    3: 38,  # Adjacent to 4
    4: 50,  # 4th from lot (secondary angular)
    5: 38,  # Adjacent to 4
    6: 38,  # Adjacent to 7
    7: 50,  # 7th from lot (secondary angular)
    8: 38,  # Adjacent to 7
    9: 52,  # Adjacent to 10
    10: 70,  # 10th from lot (PEAK - primary angular)
    11: 52,  # Adjacent to 10
    12: 52,  # Adjacent to 1
}

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

        # Generate SVG(s) and text sections
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
            # Add explanation text (rendered by Typst for nice typography)
            results.append(
                (
                    "Understanding Zodiacal Releasing",
                    {
                        "type": "text",
                        "text": self._get_explanation_text(self.lot),
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

        # Embed font for symbol rendering
        _add_font_defs(dwg)

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
        """Render the natal angles as a bar graph showing angular prominence."""
        # Section header
        self._add_section_header(dwg, "NATAL FORTUNE ANGLES", 40, y_start, config)
        y_offset = y_start + 30

        # Description text
        dwg.add(
            dwg.text(
                "Bar height shows angular strength. Brighter bars = peak periods.",
                insert=(40, y_offset),
                font_family="Arial, sans-serif",
                font_size="10px",
                fill=config.colors["text_muted"],
            )
        )
        y_offset += 20

        # Bar graph dimensions
        chart_width = config.width - 80
        bar_width = (chart_width / 12) * 0.7  # 70% of cell width for bar
        cell_width = chart_width / 12
        chart_x = 40
        max_bar_height = 100
        baseline_y = y_offset + max_bar_height + 10

        # Get natal planets by sign
        planets_by_sign: dict[str, list[str]] = {}
        for pos in chart.positions:
            if pos.sign not in planets_by_sign:
                planets_by_sign[pos.sign] = []
            glyph = CELESTIAL_REGISTRY.get(pos.name, None)
            planets_by_sign[pos.sign].append(glyph.glyph if glyph else pos.name[:2])

        lot_sign_idx = SIGNS.index(timeline.lot_sign)

        # Define bar heights and colors for each position from lot (1-12)
        # Position 1 = 1st from lot, Position 10 = 10th from lot (peak), etc.
        # Heights: 1,10 = highest; 4,7 = medium; adjacent signs step down
        bar_config = {
            1: {"height": 1.0, "bright": True},  # 1st from lot (angular)
            2: {"height": 0.75, "bright": False},  # Adjacent to 1
            3: {"height": 0.50, "bright": False},  # Adjacent to 4
            4: {"height": 0.65, "bright": True},  # 4th from lot (angular)
            5: {"height": 0.50, "bright": False},  # Adjacent to 4
            6: {"height": 0.50, "bright": False},  # Adjacent to 7
            7: {"height": 0.65, "bright": True},  # 7th from lot (angular)
            8: {"height": 0.50, "bright": False},  # Adjacent to 7
            9: {"height": 0.75, "bright": False},  # Adjacent to 10
            10: {"height": 1.0, "bright": True},  # 10th from lot (PEAK!)
            11: {"height": 0.75, "bright": False},  # Adjacent to 10
            12: {"height": 0.75, "bright": False},  # Adjacent to 1
        }

        # Colors for bars
        bright_color = config.colors["peak_stroke"]  # Purple for angular
        muted_color = config.colors["default_period"]  # Cream for non-angular

        # Draw bars
        for i in range(12):
            position = i + 1  # 1-indexed position from lot
            sign_idx = (lot_sign_idx + i) % 12
            sign = SIGNS[sign_idx]

            x = chart_x + i * cell_width + (cell_width - bar_width) / 2
            cfg = bar_config[position]
            bar_height = max_bar_height * cfg["height"]
            bar_y = baseline_y - bar_height

            # Bar fill color
            fill_color = bright_color if cfg["bright"] else muted_color
            stroke_color = (
                config.colors["text_dark"]
                if cfg["bright"]
                else config.colors["grid_line"]
            )

            # Draw bar
            dwg.add(
                dwg.rect(
                    (x, bar_y),
                    (bar_width, bar_height),
                    fill=fill_color,
                    stroke=stroke_color,
                    stroke_width=1,
                    rx=3,
                    ry=3,
                )
            )

            # Add sign glyph inside bar (near top)
            # Use white text on dark angular bars, dark text on light non-angular bars
            glyph = get_sign_glyph(sign)
            glyph_y = bar_y + 18 if bar_height > 30 else bar_y + bar_height / 2 + 5
            text_color = "#ffffff" if cfg["bright"] else config.colors["text_muted"]
            dwg.add(
                dwg.text(
                    glyph,
                    insert=(x + bar_width / 2, glyph_y),
                    text_anchor="middle",
                    font_family="Noto Sans Symbols2, Arial",
                    font_size="14px",
                    fill=text_color,
                )
            )

            # Add planets inside bar if present
            if sign in planets_by_sign:
                planet_glyphs = planets_by_sign[sign]
                planet_start_y = glyph_y + 16
                for j, planet_glyph in enumerate(planet_glyphs[:3]):  # Max 3
                    if planet_start_y + j * 14 < baseline_y - 5:
                        dwg.add(
                            dwg.text(
                                planet_glyph,
                                insert=(x + bar_width / 2, planet_start_y + j * 14),
                                text_anchor="middle",
                                font_family="Noto Sans Symbols2, Arial",
                                font_size="11px",
                                fill=text_color,
                            )
                        )

        # Draw baseline
        dwg.add(
            dwg.line(
                (chart_x, baseline_y),
                (chart_x + chart_width, baseline_y),
                stroke=config.colors["grid_line"],
                stroke_width=1,
            )
        )

        # Add position numbers below baseline
        for i in range(12):
            x = chart_x + i * cell_width + cell_width / 2
            dwg.add(
                dwg.text(
                    str(i + 1),
                    insert=(x, baseline_y + 15),
                    text_anchor="middle",
                    font_family="Arial, sans-serif",
                    font_size="10px",
                    fill=config.colors["text_muted"],
                )
            )

        # Add axis label
        lot_short = timeline.lot.replace("Part of ", "")
        dwg.add(
            dwg.text(
                f"Houses from {lot_short}",
                insert=(chart_x + chart_width / 2, baseline_y + 30),
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size="11px",
                font_style="italic",
                fill=config.colors["text_muted"],
            )
        )

        return baseline_y + 45

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
    ) -> float:
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

        # Draw header line (below headers, above data)
        dwg.add(
            dwg.line(
                (x_start, y_offset + 5),
                (x_start + sum(col_widths), y_offset + 5),
                stroke=config.colors["grid_line"],
                stroke_width=1,
            )
        )

        y_offset += 18

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
                        font_family="Noto Sans Symbols2, Arial, sans-serif",
                        font_size="11px",
                        fill=config.colors["text_dark"],
                    )
                )
                x += col_widths[i]

            y_offset += 20

        return y_offset

    def _get_explanation_text(self, lot_name: str) -> str:
        """Get explanatory text about Zodiacal Releasing for Typst rendering."""
        # Lot-specific descriptions for ZR context
        lot_descriptions = {
            "Part of Fortune": (
                "You are releasing from the Part of Fortune, the primary lot of embodiment "
                "and material experience. Fortune reveals the timing of your physical vitality, "
                "health fluctuations, material circumstances, and how life 'happens to you.' "
                "Peak periods often bring increased visibility, opportunities, or significant "
                "life events related to your body, resources, and worldly circumstances. This "
                "is the most commonly used lot for general life timing."
            ),
            "Part of Spirit": (
                "You are releasing from the Part of Spirit, the lot of will, intellect, and "
                "purposeful action. Spirit reveals the timing of your vocational calling, "
                "career developments, and how you consciously shape your life. Peak periods "
                "often bring breakthroughs in work, recognition for your efforts, or pivotal "
                "decisions about your life direction. Spirit shows what you do, while Fortune "
                "shows what happens to you."
            ),
            "Part of Eros (Love)": (
                "You are releasing from the Part of Eros, the lot of love, desire, and "
                "romantic connection. Eros reveals the timing of relationships, attractions, "
                "and matters of the heart. Peak periods often coincide with significant "
                "romantic encounters, deepening of bonds, or important relationship transitions."
            ),
            "Part of Necessity (Ananke)": (
                "You are releasing from the Part of Necessity, the lot of constraints, fate, "
                "and unavoidable circumstances. Necessity reveals timing around struggles, "
                "enemies, and the things we must endure. Peak periods may bring challenges "
                "that ultimately strengthen character, or confrontations with limitations "
                "that reshape your path."
            ),
            "Part of Courage (Tolma)": (
                "You are releasing from the Part of Courage, the lot of boldness, action, "
                "and assertive energy. Courage reveals timing for taking risks, confronting "
                "fears, and decisive action. Peak periods often demand bravery and can bring "
                "both triumphs and conflicts depending on how that martial energy is channeled."
            ),
            "Part of Victory (Nike)": (
                "You are releasing from the Part of Victory, the lot of success, faith, and "
                "honors. Victory reveals timing for achievements, recognition, and fortunate "
                "alliances. Peak periods often bring rewards, public acknowledgment, or "
                "beneficial connections that elevate your standing."
            ),
            "Part of Nemesis": (
                "You are releasing from the Part of Nemesis, the lot of hidden matters, karma, "
                "and that which comes due. Nemesis reveals timing around debts (literal or "
                "metaphorical), endings, and subconscious patterns surfacing. Peak periods "
                "may bring closure, reckoning, or the resolution of long-standing issues."
            ),
        }

        # Get lot-specific description or fall back to catalog
        if lot_name in lot_descriptions:
            lot_paragraph = lot_descriptions[lot_name]
        else:
            # Try to get from ARABIC_PARTS_CATALOG
            from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG

            if lot_name in ARABIC_PARTS_CATALOG:
                catalog_desc = ARABIC_PARTS_CATALOG[lot_name].get("description", "")
                lot_paragraph = (
                    f"You are releasing from the {lot_name}. {catalog_desc} "
                    "Peak periods in angular signs will intensify these themes, bringing "
                    "increased activity and visibility in this life area."
                )
            else:
                lot_paragraph = (
                    f"You are releasing from the {lot_name}. Peak periods in angular signs "
                    "will bring increased activity and visibility in the life areas "
                    "associated with this lot."
                )

        return f"""{lot_paragraph}

Zodiacal Releasing is a Hellenistic timing technique that divides life into major periods ruled by zodiac signs. Each sign's ruling planet colors the themes of that time. This technique was preserved by Vettius Valens in the 2nd century CE and has been revived by modern traditional astrologers.

The bar graph above shows which signs are angular (most active) from your Lot. The tallest bars at positions 1 and 10 represent peak periods of heightened visibility and activity. Positions 4 and 7 are also angular but less intense. When your current period falls in one of these signs, expect increased momentum in that lot's life area.

The table shows how long each planetary ruler's periods last. Saturn rules the longest periods (30 years at L1), while the Moon rules the shortest (25 years). Each level subdivides proportionally: L1 measures in years, L2 in months, L3 in days, and L4 in hours. This creates a fractal structure where the same planetary themes echo across different time scales.

The timeline on the following page shows your actual periods with start and end dates. Trapezoidal shapes rise higher for angular signs. The current period is highlighted in warm cream. "Loosing of the Bond" periods (marked with darker outlines) indicate pivotal transitions when focus shifts. Use this to understand where you are in your life's unfolding story."""

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

        # Embed font for symbol rendering
        _add_font_defs(dwg)

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
            ("current", config.colors["current_period"], "Current period"),
            ("loosing", config.colors["loosing_bond_stroke"], "Loosing of the bond"),
            ("post_loosing", config.colors["post_loosing"], "Post-loosing phase"),
            ("default", config.colors["default_period"], "Regular period"),
        ]

        for i, (item_type, color, label) in enumerate(items):
            iy = y + i * 16

            # Color swatch
            if item_type == "loosing":
                # Draw box with thick dark outline (like loosing of bond bars)
                dwg.add(
                    dwg.rect(
                        (x, iy),
                        (12, 12),
                        fill=config.colors["default_period"],
                        stroke=color,
                        stroke_width=2.5,
                        rx=2,
                        ry=2,
                    )
                )
            else:
                # Regular filled box (current, post_loosing, default)
                dwg.add(
                    dwg.rect(
                        (x, iy),
                        (12, 12),
                        fill=color,
                        stroke=config.colors["grid_line"],
                        stroke_width=0.5,
                        rx=2,
                        ry=2,
                    )
                )

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

        # Baseline y positions
        # Label baseline stays fixed, bar baseline is shifted up 5px
        label_baseline_y = y_offset + LEVEL_HEIGHT - 30
        baseline_y = label_baseline_y - 5  # Bars drawn 5px higher

        # For Level 3, track post-loosing state within each L2 period
        post_loosing_state = False
        current_l2_start = None

        if level == 3:
            # Get L2 periods to track boundaries
            l2_periods = timeline.periods.get(2, [])

        # Draw each period
        for period in visible_periods:
            x1 = max(date_to_x(period.start), TIMELINE_MARGIN_X)
            x2 = min(date_to_x(period.end), config.width - TIMELINE_MARGIN_X)

            if x2 <= x1:
                continue

            # For Level 3, check if we're in post-loosing phase
            is_post_loosing = False
            if level == 3:
                # Find which L2 period contains this L3 period
                period_start = period.start
                if period_start.tzinfo is None:
                    period_start = period_start.replace(tzinfo=dt.UTC)

                for l2_p in l2_periods:
                    l2_start = l2_p.start
                    l2_end = l2_p.end
                    if l2_start.tzinfo is None:
                        l2_start = l2_start.replace(tzinfo=dt.UTC)
                    if l2_end.tzinfo is None:
                        l2_end = l2_end.replace(tzinfo=dt.UTC)

                    if l2_start <= period_start < l2_end:
                        # Reset post-loosing state when entering new L2 period
                        if current_l2_start != l2_start:
                            current_l2_start = l2_start
                            post_loosing_state = False
                        break

                # If this period is loosing of bond, mark subsequent as post-loosing
                if period.is_loosing_bond:
                    post_loosing_state = True
                elif post_loosing_state:
                    is_post_loosing = True

            self._draw_period_shape(
                dwg,
                period,
                x1,
                x2,
                baseline_y,
                config,
                is_current=self._is_current_period(period, config),
                lot_sign=timeline.lot_sign,
                is_post_loosing=is_post_loosing,
            )

        # For Level 3, draw vertical lines where Level 2 periods begin
        if level == 3:
            l2_periods = timeline.periods.get(2, [])
            for l2_period in l2_periods:
                # Check if L2 period start falls within visible range
                l2_start = l2_period.start
                if l2_start.tzinfo is None:
                    l2_start = l2_start.replace(tzinfo=dt.UTC)

                if visible_start < l2_start < visible_end:
                    x = date_to_x(l2_start)
                    # Draw vertical line from top of chart area to baseline
                    dwg.add(
                        dwg.line(
                            (x, y_offset - 15),
                            (x, baseline_y),
                            stroke=config.colors["peak_stroke"],
                            stroke_width=1.5,
                            stroke_dasharray="4,2",
                        )
                    )
                    # Add L2 sign label at top
                    l2_glyph = get_sign_glyph(l2_period.sign)
                    dwg.add(
                        dwg.text(
                            f"L2: {l2_glyph}",
                            insert=(x + 3, y_offset - 5),
                            font_family="Noto Sans Symbols2, Arial",
                            font_size="8px",
                            fill=config.colors["peak_stroke"],
                        )
                    )

        # Draw date labels along bottom (using label baseline, not bar baseline)
        self._render_date_labels(
            dwg, visible_periods, date_to_x, label_baseline_y + 20, config
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
        lot_sign: str = "Aries",
        is_post_loosing: bool = False,
    ) -> None:
        """
        Draw period as a bar graph rectangle.

        Bar height based on position from lot:
        - 1st & 10th: tallest (primary angular)
        - 4th & 7th: medium-tall (secondary angular)
        - Adjacent to angular: slightly shorter than their neighbor
        """
        # Calculate position from lot (1-12) based on sign
        lot_sign_idx = SIGNS.index(lot_sign) if lot_sign in SIGNS else 0
        period_sign_idx = SIGNS.index(period.sign) if period.sign in SIGNS else 0
        position = ((period_sign_idx - lot_sign_idx) % 12) + 1  # 1-indexed

        bar_height = BAR_HEIGHTS.get(position, 38)  # Default to medium if unknown

        width = x2 - x1
        bar_y = baseline_y - bar_height

        # Determine fill color
        if is_current:
            fill = config.colors["current_period"]  # Light purple
        elif period.is_loosing_bond or is_post_loosing:
            fill = config.colors["post_loosing"]  # Lighter shade for LB and post-LB
        else:
            fill = config.colors["default_period"]

        # Draw bar with rounded corners
        stroke = config.colors["grid_line"]
        stroke_width = 0.5

        dwg.add(
            dwg.rect(
                (x1, bar_y),
                (width, bar_height),
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width,
                rx=2,
                ry=2,
            )
        )

        # Add loosing of bond indicator (thick dark border)
        if period.is_loosing_bond:
            dwg.add(
                dwg.rect(
                    (x1, bar_y),
                    (width, bar_height),
                    fill="none",
                    stroke=config.colors["loosing_bond_stroke"],
                    stroke_width=2.5,
                    rx=2,
                    ry=2,
                )
            )

        # Add sign glyph inside bar (centered, scaled to fit)
        glyph = get_sign_glyph(period.sign)
        center_x = (x1 + x2) / 2

        # Scale font size based on bar width
        if width >= 30:
            font_size = "12px"
        elif width >= 18:
            font_size = "10px"
        elif width >= 10:
            font_size = "8px"
        else:
            font_size = "6px"

        # Position glyph in upper portion of bar
        glyph_y = bar_y + min(18, bar_height * 0.5)
        dwg.add(
            dwg.text(
                glyph,
                insert=(center_x, glyph_y),
                text_anchor="middle",
                font_family="Noto Sans Symbols2, Arial",
                font_size=font_size,
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

        # Add extra spacing below bars for labels
        label_y = y + 8

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
                        insert=(x, label_y),
                        text_anchor="start",
                        font_family="Arial, sans-serif",
                        font_size="8px",
                        fill=config.colors["text_muted"],
                        transform=f"rotate(-90, {x}, {label_y})",
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
