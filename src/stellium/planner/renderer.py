"""
PlannerRenderer - Generate beautiful PDF planners using Typst.

This module handles:
- Generating front matter (charts, ZR timeline, graphic ephemeris)
- Rendering daily pages with events
- Typst compilation to PDF
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stellium.planner.builder import PlannerConfig

# Check if typst is available
try:
    import typst as typst_lib

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


@dataclass
class ChartPaths:
    """Paths to generated chart SVG files."""

    natal: str | None = None
    progressed: str | None = None
    solar_return: str | None = None
    graphic_ephemeris: str | None = None


class PlannerRenderer:
    """
    Renders PDF planners using Typst typesetting.

    Generates:
    - Title page with planner info
    - Front matter section with charts
    - Month overview pages
    - Daily pages with transit events
    """

    def __init__(self, config: PlannerConfig) -> None:
        """
        Initialize renderer with configuration.

        Args:
            config: PlannerConfig from PlannerBuilder
        """
        if not TYPST_AVAILABLE:
            raise ImportError(
                "Typst library not available. Install with: pip install typst"
            )

        self.config = config
        self._temp_dir: str | None = None
        self._chart_paths = ChartPaths()

    def render(self) -> bytes:
        """
        Render the complete planner to PDF.

        Returns:
            PDF as bytes
        """

        # Create temp directory for chart files
        self._temp_dir = tempfile.mkdtemp(prefix="stellium_planner_")

        try:
            # Generate charts
            self._generate_charts()

            # Collect events
            events_by_date = self._collect_events()

            # Generate Typst document
            typst_content = self._generate_typst_document(events_by_date)

            # Write to temp file and compile
            typst_path = os.path.join(self._temp_dir, "planner.typ")
            with open(typst_path, "w", encoding="utf-8") as f:
                f.write(typst_content)

            # Get font directories
            font_dirs = self._get_font_dirs()

            # Compile to PDF
            pdf_bytes = typst_lib.compile(
                typst_path,
                root="/",
                font_paths=font_dirs,
            )

            return pdf_bytes

        finally:
            # Clean up temp files
            self._cleanup_temp_files()

    def _get_font_dirs(self) -> list[str]:
        """Get font directories for Typst compilation."""
        base_font_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "assets",
            "fonts",
        )
        return [
            base_font_dir,
            os.path.join(base_font_dir, "Cinzel_Decorative"),
            os.path.join(base_font_dir, "Crimson_Pro"),
            os.path.join(base_font_dir, "Crimson_Pro", "static"),
        ]

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        import shutil

        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)

    def _generate_charts(self) -> None:
        """Generate chart SVG files for front matter."""
        from stellium.core.builder import ChartBuilder

        # Generate natal chart
        natal_chart = ChartBuilder.from_native(self.config.native).calculate()

        if self.config.include_natal_chart:
            natal_path = os.path.join(self._temp_dir, "natal.svg")
            natal_chart.draw(natal_path).with_zodiac_palette("rainbow").save()
            self._chart_paths.natal = natal_path

        # Generate progressed chart
        if self.config.include_progressed_chart:
            from stellium.core.multichart import MultiChartBuilder

            # Calculate age at start of planner
            birth_date = self.config.native.datetime.local_datetime.date()
            planner_start = self.config.start_date
            age = planner_start.year - birth_date.year
            if (planner_start.month, planner_start.day) < (
                birth_date.month,
                birth_date.day,
            ):
                age -= 1

            try:
                mc = MultiChartBuilder.progression(natal_chart, age=age).calculate()
                progressed_path = os.path.join(self._temp_dir, "progressed.svg")
                mc.draw(progressed_path).with_zodiac_palette("rainbow").save()
                self._chart_paths.progressed = progressed_path
            except Exception:
                pass  # Skip if progression fails

        # Generate solar return
        if self.config.include_solar_return:
            from stellium.returns import ReturnBuilder

            try:
                sr_year = self.config.year or self.config.start_date.year
                sr_chart = ReturnBuilder.solar(natal_chart, sr_year).calculate()
                sr_path = os.path.join(self._temp_dir, "solar_return.svg")
                sr_chart.draw(sr_path).with_zodiac_palette("rainbow").save()
                self._chart_paths.solar_return = sr_path
            except Exception:
                pass

        # Generate graphic ephemeris with natal chart overlay
        if self.config.include_graphic_ephemeris:
            from stellium.visualization import GraphicEphemeris

            try:
                start_str = self.config.start_date.isoformat()
                end_str = self.config.end_date.isoformat()
                eph = GraphicEphemeris(
                    start_date=start_str,
                    end_date=end_str,
                    harmonic=self.config.graphic_ephemeris_harmonic,
                    natal_chart=natal_chart,  # Include natal positions for transit aspects
                )
                eph_path = os.path.join(self._temp_dir, "ephemeris.svg")
                eph.draw(eph_path)
                self._chart_paths.graphic_ephemeris = eph_path
            except Exception:
                pass

    def _collect_events(self) -> dict[date, list]:
        """Collect all events for the planner period."""
        from stellium.core.builder import ChartBuilder
        from stellium.planner.events import DailyEventCollector

        natal_chart = ChartBuilder.from_native(self.config.native).calculate()

        collector = DailyEventCollector(
            natal_chart=natal_chart,
            start=self.config.start_date,
            end=self.config.end_date,
            timezone=self.config.timezone,
        )

        collector.collect_all(
            natal_transits=self.config.natal_transit_planets is not None
            or self.config.include_mundane_transits,
            transit_planets=self.config.natal_transit_planets,
            ingresses=self.config.ingress_planets is not None,
            ingress_planets=self.config.ingress_planets,
            stations=self.config.station_planets is not None,
            station_planets=self.config.station_planets,
            moon_phases=self.config.include_moon_phases,
            voc=self.config.include_voc,
            voc_mode=self.config.voc_mode,
            eclipses=True,
        )

        return collector._events_by_date

    def _generate_typst_document(self, events_by_date: dict[date, list]) -> str:
        """Generate complete Typst document."""
        parts = []

        # Document preamble
        parts.append(self._get_preamble())

        # Title page
        parts.append(self._render_title_page())

        # Front matter
        parts.append(self._render_front_matter())

        # Monthly pages
        parts.append(self._render_monthly_pages(events_by_date))

        return "\n".join(parts)

    def _get_preamble(self) -> str:
        """Get Typst document preamble with styling."""
        page_size = {
            "a4": '"a4"',
            "letter": '"us-letter"',
            "half-letter": "(width: 5.5in, height: 8.5in)",
        }.get(self.config.page_size, '"a4"')

        binding = self.config.binding_margin

        return f"""// Stellium Astrological Planner
// Generated with Typst

// ============================================================================
// COLOR PALETTE - Warm mystical purple theme
// ============================================================================
#let primary = rgb("#4a3353")
#let secondary = rgb("#6b4d6e")
#let accent = rgb("#8e6b8a")
#let gold = rgb("#b8953d")
#let cream = rgb("#faf8f5")
#let text-dark = rgb("#2d2330")

// ============================================================================
// PAGE SETUP
// ============================================================================
#set page(
  paper: {page_size},
  margin: (top: 0.6in, bottom: 0.6in, left: {0.7 + binding}in, right: 0.7in),
  fill: cream,
  header: context {{
    if counter(page).get().first() > 2 [
      #set text(font: "Cinzel Decorative", size: 7pt, fill: accent, tracking: 0.5pt)
      #h(1fr)
      Astrological Planner
      #h(1fr)
    ]
  }},
  footer: context {{
    set text(size: 7pt, fill: accent)
    h(1fr)
    counter(page).display("1")
    h(1fr)
  }},
)

// ============================================================================
// TYPOGRAPHY
// ============================================================================
#set text(
  font: ("Crimson Pro", "Noto Sans Symbols 2", "Noto Sans Symbols", "Georgia", "serif"),
  size: 9pt,
  fill: text-dark,
)

#set par(justify: true, leading: 0.7em)

// Heading styles
#show heading.where(level: 1): it => {{
  set text(font: "Cinzel Decorative", size: 22pt, weight: "regular", fill: primary, tracking: 1.5pt)
  set par(justify: false)
  align(center)[#it.body]
  v(0.4em)
}}

#show heading.where(level: 2): it => {{
  v(0.8em)
  block(
    width: 100%,
    fill: primary,
    inset: (x: 10pt, y: 6pt),
    radius: 2pt,
  )[
    #set text(font: "Cinzel Decorative", size: 9pt, weight: "regular", fill: white, tracking: 0.5pt)
    #sym.star.stroked #it.body
  ]
  v(0.4em)
}}

#show heading.where(level: 3): it => {{
  set text(font: "Cinzel Decorative", size: 9pt, weight: "regular", fill: secondary)
  v(0.3em)
  it.body
  v(0.2em)
}}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================
#let star-divider = {{
  set align(center)
  v(0.1in)
  box(width: 60%)[
    #grid(
      columns: (1fr, auto, 1fr),
      align: (right, center, left),
      column-gutter: 8pt,
      line(length: 100%, stroke: 0.6pt + gold),
      text(fill: gold, size: 8pt)[#sym.star.stroked],
      line(length: 100%, stroke: 0.6pt + gold),
    )
  ]
  v(0.1in)
}}

#let day-header(day-name, date-str, moon-info) = {{
  block(
    width: 100%,
    fill: primary,
    inset: (x: 8pt, y: 5pt),
    radius: 2pt,
  )[
    #set text(fill: white, size: 8pt)
    #text(font: "Cinzel Decorative", weight: "regular")[#day-name, #date-str]
    #h(1fr)
    #text(fill: cream.lighten(20%), size: 7pt)[#moon-info]
  ]
}}

#let event-row(time-str, event-text) = {{
  grid(
    columns: (50pt, 1fr),
    gutter: 6pt,
    text(fill: secondary, size: 8pt)[#time-str],
    text(size: 8pt)[#event-text],
  )
}}
"""

    def _render_title_page(self) -> str:
        """Render the title page."""
        native = self.config.native
        name = getattr(native, "name", "Personal") or "Personal"

        year_str = ""
        if self.config.year:
            year_str = str(self.config.year)
        else:
            year_str = f"{self.config.start_date} - {self.config.end_date}"

        return f"""
// ============================================================================
// TITLE PAGE
// ============================================================================
#v(1.5in)
#star-divider

= Astrological Planner

#star-divider
#v(0.3in)

#align(center)[
  #text(font: "Cinzel Decorative", size: 14pt, fill: secondary)[
    {self._escape(name)}
  ]
  #v(0.2in)
  #text(size: 11pt, fill: accent)[
    {year_str}
  ]
]

#v(1fr)

#align(center)[
  #text(font: "Cinzel Decorative", size: 8pt, fill: accent, style: "italic")[
    Generated with Stellium
  ]
]

#pagebreak()
"""

    def _render_front_matter(self) -> str:
        """Render front matter pages with charts."""
        parts = []

        parts.append("""
// ============================================================================
// FRONT MATTER
// ============================================================================
""")

        # Natal chart
        if self._chart_paths.natal:
            parts.append(f"""
== Natal Chart

#align(center)[
  #box(
    stroke: 1pt + gold,
    radius: 4pt,
    clip: true,
    inset: 8pt,
    fill: white,
    image("{self._chart_paths.natal}", width: 85%)
  )
]

#pagebreak()
""")

        # Progressed chart
        if self._chart_paths.progressed:
            parts.append(f"""
== Progressed Chart

#align(center)[
  #box(
    stroke: 1pt + gold,
    radius: 4pt,
    clip: true,
    inset: 8pt,
    fill: white,
    image("{self._chart_paths.progressed}", width: 85%)
  )
]

#pagebreak()
""")

        # Solar Return
        if self._chart_paths.solar_return:
            year = self.config.year or self.config.start_date.year
            parts.append(f"""
== Solar Return {year}

#align(center)[
  #box(
    stroke: 1pt + gold,
    radius: 4pt,
    clip: true,
    inset: 8pt,
    fill: white,
    image("{self._chart_paths.solar_return}", width: 85%)
  )
]

#pagebreak()
""")

        # Profections
        if self.config.include_profections:
            parts.append(self._render_profections())

        # Graphic Ephemeris
        if self._chart_paths.graphic_ephemeris:
            parts.append(f"""
== Graphic Ephemeris

#align(center)[
  #box(
    stroke: 1pt + gold,
    radius: 4pt,
    clip: true,
    inset: 8pt,
    fill: white,
    image("{self._chart_paths.graphic_ephemeris}", width: 95%)
  )
]

#pagebreak()
""")

        return "\n".join(parts)

    def _render_profections(self) -> str:
        """Render profection information."""
        from stellium.core.builder import ChartBuilder
        from stellium.engines.profections import ProfectionEngine

        natal_chart = ChartBuilder.from_native(self.config.native).calculate()
        engine = ProfectionEngine(natal_chart)

        # Calculate age at planner start
        birth_date = self.config.native.datetime.local_datetime.date()
        planner_start = self.config.start_date
        age = planner_start.year - birth_date.year
        if (planner_start.month, planner_start.day) < (
            birth_date.month,
            birth_date.day,
        ):
            age -= 1

        try:
            result = engine.annual(age)
            profected_sign = result.profected_sign
            lord = result.ruler
        except Exception:
            profected_sign = "Unknown"
            lord = "Unknown"

        return f"""
== Annual Profection

#block(
  fill: rgb("#f9f6f7"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  #grid(
    columns: (120pt, 1fr),
    gutter: 8pt,
    row-gutter: 10pt,
    [#text(fill: secondary, weight: "semibold")[Age:]], [{age}],
    [#text(fill: secondary, weight: "semibold")[Profected Sign:]], [{profected_sign}],
    [#text(fill: secondary, weight: "semibold")[Lord of the Year:]], [{lord}],
  )
]

#v(0.5em)
#text(size: 8pt, fill: accent)[
  The Lord of the Year indicates themes and areas of focus for this annual period.
  Transits to and from {lord} may be especially significant.
]

#pagebreak()
"""

    def _render_monthly_pages(self, events_by_date: dict[date, list]) -> str:
        """Render month calendar grids and weekly detail pages."""
        parts = []

        parts.append("""
// ============================================================================
// CALENDAR PAGES
// ============================================================================
""")

        # Process each month in the range
        current_month_start = self.config.start_date.replace(day=1)

        while current_month_start <= self.config.end_date:
            # Month calendar grid
            parts.append(
                self._render_month_calendar(current_month_start, events_by_date)
            )

            # Weekly detail pages for this month
            parts.append(self._render_month_weeks(current_month_start, events_by_date))

            # Move to next month
            if current_month_start.month == 12:
                current_month_start = current_month_start.replace(
                    year=current_month_start.year + 1, month=1
                )
            else:
                current_month_start = current_month_start.replace(
                    month=current_month_start.month + 1
                )

        return "\n".join(parts)

    def _get_week_start_day(self) -> int:
        """Get Python calendar firstweekday from config."""
        # Python calendar: 0=Monday, 6=Sunday
        return 6 if self.config.week_starts_on == "sunday" else 0

    def _get_day_headers(self) -> list[str]:
        """Get day header names based on week start."""
        if self.config.week_starts_on == "sunday":
            return ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        else:
            return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def _render_month_calendar(
        self, month_start: date, events_by_date: dict[date, list]
    ) -> str:
        """Render a full-page month calendar grid with all events."""
        import calendar

        month_name = month_start.strftime("%B %Y")
        cal = calendar.Calendar(firstweekday=self._get_week_start_day())

        # Get all days in month (including padding from prev/next months)
        month_days = list(cal.itermonthdates(month_start.year, month_start.month))

        # Build week rows
        weeks = []
        for i in range(0, len(month_days), 7):
            week = month_days[i : i + 7]
            weeks.append(week)

        num_weeks = len(weeks)
        day_headers = self._get_day_headers()

        # Build day cells with full event listings
        day_cells = []
        for week in weeks:
            for day in week:
                is_current_month = day.month == month_start.month
                events = events_by_date.get(day, []) if is_current_month else []

                # Build cell content with ALL events (single column, may clip)
                if is_current_month:
                    # Format each event line
                    event_lines = []
                    for evt in events:
                        time_str = evt.time.strftime("%I:%M").lstrip("0")
                        am_pm = evt.time.strftime("%p").lower()[0]  # 'a' or 'p'
                        event_lines.append(
                            f"#text(size: 5.5pt, fill: secondary)[{time_str}{am_pm}] "
                            f"#text(size: 5.5pt)[{self._escape(evt.symbol)}]"
                        )

                    # Single column for month grid (space is limited)
                    events_display = (
                        " #linebreak() ".join(event_lines) if event_lines else ""
                    )

                    # Day number prominent at top, events below
                    cell = f"""table.cell(
      fill: cream,
      inset: 4pt,
    )[
      #align(left)[
        #text(size: 11pt, weight: "bold", fill: primary)[{day.day}]
      ]
      #v(2pt)
      {events_display}
    ]"""
                else:
                    # Gray out days from other months
                    cell = f"""table.cell(
      fill: rgb("#f5f3f0"),
      inset: 4pt,
    )[
      #align(left)[
        #text(size: 11pt, fill: accent)[{day.day}]
      ]
    ]"""

                day_cells.append(cell)

        rows_str = ",\n  ".join(day_cells)

        # Build header row with correct day order
        header_cells = ",\n  ".join(
            f'table.cell(fill: primary, inset: 6pt)[#align(center)[#text(fill: white, size: 8pt, weight: "bold")[{d}]]]'
            for d in day_headers
        )

        return f"""
#pagebreak()

// Month: {month_name}
#block(height: 100%)[
  #align(center)[
    #text(font: "Cinzel Decorative", size: 18pt, fill: primary, tracking: 1pt)[{month_name}]
  ]
  #v(0.12in)

  // Full-page calendar grid
  #block(
    width: 100%,
    height: 1fr,
    radius: 6pt,
    clip: true,
    stroke: 1pt + primary,
  )[
    #table(
      columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      rows: (auto, 1fr, 1fr, 1fr, 1fr, 1fr, {"1fr, " if num_weeks > 5 else ""}),
      stroke: 0.5pt + accent,
      align: left + top,

      // Header row
      {header_cells},

      // Day cells
      {rows_str}
    )
  ]
]
"""

    def _render_month_weeks(
        self, month_start: date, events_by_date: dict[date, list]
    ) -> str:
        """Render weekly detail pages for a month."""
        import calendar

        parts = []
        cal = calendar.Calendar(firstweekday=self._get_week_start_day())

        # Get weeks that contain days from this month
        month_days = list(cal.itermonthdates(month_start.year, month_start.month))

        for i in range(0, len(month_days), 7):
            week = month_days[i : i + 7]

            # Only render week if it contains days from this month
            if any(d.month == month_start.month for d in week):
                parts.append(self._render_week_page(week, month_start, events_by_date))

        return "\n".join(parts)

    def _render_week_page(
        self, week: list[date], month_start: date, events_by_date: dict[date, list]
    ) -> str:
        """Render a single week as a full page with 7 day boxes."""
        # Week date range for header
        week_start = week[0]
        week_end = week[-1]
        week_header = (
            f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        )

        # Build day boxes
        day_boxes = []
        for day in week:
            is_current_month = day.month == month_start.month
            events = events_by_date.get(day, [])

            # Day header
            day_name = day.strftime("%A")
            day_num = day.day

            # Format events - single column, tight spacing
            event_lines = []
            for event in events:
                time_str = event.time.strftime("%I:%M%p").lower().lstrip("0")
                event_lines.append(
                    f"#text(fill: secondary, size: 6pt)[{time_str}] #text(size: 6pt)[{self._escape(event.description)}]"
                )

            if event_lines:
                # Use tight line breaks with no extra spacing
                events_str = " #linebreak() ".join(event_lines)
            else:
                events_str = (
                    '#text(fill: accent, size: 6pt, style: "italic")[No events]'
                )

            if is_current_month:
                fill_color = "cream"
                text_color = "text-dark"
            else:
                fill_color = 'rgb("#f0ede8")'
                text_color = "accent"

            day_boxes.append(f"""  box(
    width: 100%,
    height: 100%,
    stroke: 0.5pt + accent,
    radius: 2pt,
    fill: {fill_color},
    inset: 5pt,
    clip: true,
  )[
    #grid(
      columns: (1fr, auto),
      [#text(font: "Cinzel Decorative", size: 8pt, fill: {text_color})[{day_name}]],
      [#text(size: 12pt, weight: "bold", fill: {text_color})[{day_num}]],
    )
    #line(length: 100%, stroke: 0.3pt + accent)
    #v(2pt)
    {events_str}
  ],""")

        days_content = "\n".join(day_boxes)

        return f"""
#pagebreak()

// Week: {week_header}
#align(center)[
  #text(font: "Cinzel Decorative", size: 11pt, fill: secondary)[{week_header}]
]
#v(0.05in)

#block(height: 1fr)[
#grid(
  columns: (1fr,),
  rows: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  row-gutter: 3pt,
{days_content}
)
]
"""

    def _render_day(self, day: date, events: list) -> str:
        """Render a single day entry (legacy - kept for reference)."""
        day_name = day.strftime("%A")
        date_str = day.strftime("%B %d")

        # Get moon info (simplified for now)
        moon_info = ""  # TODO: Add moon sign/phase

        # Format events
        event_rows = []
        for event in events:
            time_str = event.time.strftime("%I:%M %p").lstrip("0")
            event_rows.append(
                f'  #event-row("{time_str}", "{self._escape(event.description)}")'
            )

        events_content = (
            "\n".join(event_rows)
            if event_rows
            else "  #text(fill: accent, size: 7pt)[No major transits]"
        )

        return f"""
#day-header("{day_name}", "{date_str}", "{moon_info}")
#v(3pt)
{events_content}
#v(6pt)
"""

    def _escape(self, text: str) -> str:
        """Escape text for Typst."""
        if not text:
            return ""
        # Escape special Typst characters
        text = text.replace("\\", "\\\\")
        text = text.replace("#", "\\#")
        text = text.replace("$", "\\$")
        text = text.replace("@", "\\@")
        text = text.replace("<", "\\<")
        text = text.replace(">", "\\>")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace("{", "\\{")
        text = text.replace("}", "\\}")
        text = text.replace("_", "\\_")
        text = text.replace("*", "\\*")
        text = text.replace('"', '\\"')
        return text
