"""
Transit period sections for natal chart transit analysis.

Computes when transiting planets form aspects to natal positions,
with orb entry/exit windows and multi-pass handling for retrograde transits.

Two output modes:
- TransitListSection: plain-text rows, e.g.:
    Dec 2 - Mar 2 '26 — Jupiter △ natal Chiron
    Dec 4 — Mercury □ natal Jupiter
    Jan 8 - Feb 6 '26 — Uranus △ natal Neptune (3x: Jan 15, Jan 30, Feb 12)

- TransitGanttSection: SVG horizontal bar chart grouped by transiting planet.
  Rows are aspect events; bars show orb window; tick marks show exact dates.

Both sections take an explicit start/end date range and accept a natal
CalculatedChart via generate_data() following the ReportSection protocol.
"""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

# Default transiting planets for natal transit analysis
DEFAULT_TRANSIT_PLANETS = [
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
    "True Node",
    "Chiron",
]

# Default aspects with transit orbs (tighter than natal chart orbs)
DEFAULT_TRANSIT_ASPECTS: dict[str, float] = {
    "Conjunction": 2.0,
    "Sextile": 1.5,
    "Square": 2.0,
    "Trine": 2.0,
    "Opposition": 2.0,
}

# Planet colors for Gantt chart
_PLANET_COLORS: dict[str, str] = {
    "Sun": "#F4C542",
    "Moon": "#A8C8E8",
    "Mercury": "#B5D5A0",
    "Venus": "#E8A0C0",
    "Mars": "#E07060",
    "Jupiter": "#C0A060",
    "Saturn": "#8090A0",
    "Uranus": "#70B8C0",
    "Neptune": "#7090D0",
    "Pluto": "#906880",
    "True Node": "#C8A060",
    "Chiron": "#90A870",
}

# Aspect colors for Gantt chart bars
_ASPECT_COLORS: dict[str, str] = {
    "Conjunction": "#E07060",
    "Sextile": "#70B870",
    "Square": "#F4A030",
    "Trine": "#60A0D0",
    "Opposition": "#C060B0",
}

# Fast planets excluded from Gantt by default (too many short transits)
_FAST_PLANETS = {"Sun", "Moon", "Mercury", "Venus", "Mars"}

# Maximum days between crossings to be considered the same retrograde transit
_MAX_WINDOW_DAYS = 200

# Minimum days between exact crossings — deduplicate near-station oscillations
# (slow planets near a station can trigger many crossings within a few days)
_MIN_CROSSING_SEPARATION_DAYS = 3


# ---------------------------------------------------------------------------
# TransitPeriod dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransitPeriod:
    """
    A single transit event: one transiting planet forming one aspect to one natal point.

    Includes the orb entry/exit window and all exact dates within the window.
    Multi-pass transits (retrograde causing 2–3 exact crossings) are represented
    as a single TransitPeriod with multiple exact_dates entries.

    Attributes:
        transit_planet: Name of the transiting planet (e.g. "Jupiter")
        natal_planet:   Name of the natal point being aspected (e.g. "Sun")
        aspect_name:    Name of the aspect (e.g. "Trine")
        aspect_angle:   Aspect angle in degrees (e.g. 120.0)
        orb:            Orb used for this calculation in degrees
        exact_dates:    One or more exact-aspect datetimes (UTC); 2–3 = retrograde passes
        start:          When transit entered orb, or None if before the search window
        end:            When transit exits orb, or None if extends beyond search window
    """

    transit_planet: str
    natal_planet: str
    aspect_name: str
    aspect_angle: float
    orb: float
    exact_dates: tuple[dt.datetime, ...]
    start: dt.datetime | None
    end: dt.datetime | None

    @property
    def is_multi_pass(self) -> bool:
        """True if the transit crosses the exact point more than once (retrograde)."""
        return len(self.exact_dates) > 1

    @property
    def peak_date(self) -> dt.datetime:
        """The middle exact date — most representative for sorting."""
        return self.exact_dates[len(self.exact_dates) // 2]

    @property
    def duration_days(self) -> float | None:
        """Duration in days, or None if window extends outside the search range."""
        if self.start and self.end:
            return (self.end - self.start).total_seconds() / 86400
        return None


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------


def calculate_transit_periods(
    natal_chart: CalculatedChart,
    start: dt.datetime,
    end: dt.datetime,
    transit_planets: list[str] | None = None,
    aspects: dict[str, float] | None = None,
    include_natal_points: list[str] | None = None,
) -> list[TransitPeriod]:
    """
    Calculate transit-to-natal aspect periods for a date range.

    For each (transiting planet × natal point × aspect) combination, returns
    TransitPeriod objects with orb entry/exit dates and all exact dates within
    the window, including multiple passes from retrograde motion.

    Reuses stellium.engines.search functions for all ephemeris lookups — no
    raw Swiss Ephemeris calls here.

    Args:
        natal_chart:          The natal CalculatedChart to transit to.
        start:                Start of date range (UTC).
        end:                  End of date range (UTC).
        transit_planets:      Planets to use as transits (default: all 12).
        aspects:              Dict of {aspect_name: orb_degrees} (default: 5 major).
        include_natal_points: Limit natal points checked (default: all planets).

    Returns:
        List of TransitPeriod objects sorted by start date (or first exact date
        if start is outside the search window).
    """
    from stellium.core.registry import ASPECT_REGISTRY
    from stellium.engines.search import (
        find_all_longitude_crossings,
        find_longitude_crossing,
    )

    if transit_planets is None:
        transit_planets = DEFAULT_TRANSIT_PLANETS
    if aspects is None:
        aspects = DEFAULT_TRANSIT_ASPECTS

    # Resolve aspect angles from the registry
    aspect_configs: list[tuple[str, float, float]] = []  # (name, angle, orb)
    for aspect_name, orb in aspects.items():
        if aspect_name in ASPECT_REGISTRY:
            angle = ASPECT_REGISTRY[aspect_name].angle
            aspect_configs.append((aspect_name, angle, orb))

    # Get natal positions
    natal_positions = natal_chart.get_planets()
    if include_natal_points:
        natal_positions = [p for p in natal_positions if p.name in include_natal_points]

    periods: list[TransitPeriod] = []

    for transit_planet in transit_planets:
        for natal_obj in natal_positions:
            natal_lon = natal_obj.longitude

            for aspect_name, aspect_angle, orb in aspect_configs:
                # Compute target longitude(s).
                # - Conjunction: one target at natal longitude
                # - Opposition: one target at natal + 180°
                # - All others: two targets (aspect forms from either side of the natal point)
                if aspect_angle == 0.0:
                    target_lons = [natal_lon]
                elif aspect_angle == 180.0:
                    target_lons = [(natal_lon + 180.0) % 360.0]
                else:
                    target_lons = [
                        (natal_lon + aspect_angle) % 360.0,
                        (natal_lon - aspect_angle) % 360.0,
                    ]

                for target_lon in target_lons:
                    try:
                        exact_crossings = find_all_longitude_crossings(
                            transit_planet, target_lon, start, end
                        )
                    except Exception:
                        continue

                    if not exact_crossings:
                        continue

                    # Deduplicate near-station oscillations: slow planets near a
                    # station can trigger many crossings within a few days of each
                    # other. Keep only one crossing per _MIN_CROSSING_SEPARATION_DAYS.
                    deduped = [exact_crossings[0]]
                    for crossing in exact_crossings[1:]:
                        if (
                            crossing.julian_day - deduped[-1].julian_day
                            >= _MIN_CROSSING_SEPARATION_DAYS
                        ):
                            deduped.append(crossing)
                    exact_crossings = deduped

                    # Group crossings that belong to the same retrograde event.
                    # Any two crossings within _MAX_WINDOW_DAYS are part of
                    # the same direct→retrograde→direct transit arc.
                    groups: list[list] = []
                    for crossing in exact_crossings:
                        if (
                            groups
                            and (crossing.julian_day - groups[-1][-1].julian_day)
                            < _MAX_WINDOW_DAYS
                        ):
                            groups[-1].append(crossing)
                        else:
                            groups.append([crossing])

                    for group in groups:
                        first = group[0]
                        last = group[-1]
                        exact_dates = tuple(c.datetime_utc for c in group)

                        # Find orb entry: search backward from the first exact crossing.
                        # Try both (target - orb) and (target + orb) and take the
                        # LATER result — that's the actual entry into the orb window.
                        t_minus = (target_lon - orb) % 360.0
                        t_plus = (target_lon + orb) % 360.0

                        c1 = find_longitude_crossing(
                            transit_planet,
                            t_minus,
                            first.julian_day,
                            direction="backward",
                            max_days=90,
                        )
                        c2 = find_longitude_crossing(
                            transit_planet,
                            t_plus,
                            first.julian_day,
                            direction="backward",
                            max_days=90,
                        )
                        entry_candidates = [c for c in (c1, c2) if c is not None]
                        orb_start = (
                            max(
                                entry_candidates, key=lambda c: c.julian_day
                            ).datetime_utc
                            if entry_candidates
                            else None
                        )

                        # Find orb exit: search forward from the last exact crossing.
                        # Take the EARLIER result — that's the actual exit from the orb window.
                        c3 = find_longitude_crossing(
                            transit_planet,
                            t_minus,
                            last.julian_day,
                            direction="forward",
                            max_days=90,
                        )
                        c4 = find_longitude_crossing(
                            transit_planet,
                            t_plus,
                            last.julian_day,
                            direction="forward",
                            max_days=90,
                        )
                        exit_candidates = [c for c in (c3, c4) if c is not None]
                        orb_end = (
                            min(
                                exit_candidates, key=lambda c: c.julian_day
                            ).datetime_utc
                            if exit_candidates
                            else None
                        )

                        periods.append(
                            TransitPeriod(
                                transit_planet=transit_planet,
                                natal_planet=natal_obj.name,
                                aspect_name=aspect_name,
                                aspect_angle=aspect_angle,
                                orb=orb,
                                exact_dates=exact_dates,
                                start=orb_start,
                                end=orb_end,
                            )
                        )

    # Sort by orb start date, falling back to first exact date
    periods.sort(key=lambda p: p.start or p.exact_dates[0])
    return periods


# ---------------------------------------------------------------------------
# Date formatting helpers
# ---------------------------------------------------------------------------


def _fmt_date(d: dt.datetime, ref_year: int | None = None) -> str:
    """Format a date concisely, omitting the year if it matches ref_year."""
    if ref_year is not None and d.year == ref_year:
        return d.strftime("%-d %b")
    short_year = str(d.year)[2:]
    return f"{d.strftime('%-d %b')} '{short_year}"


def _fmt_period(p: TransitPeriod, ref_year: int | None = None) -> str:
    """
    Format a TransitPeriod as a human-readable string.

    Examples:
        Dec 2 - Mar 2 '26 — Jupiter △ natal Chiron
        Dec 4 — Mercury □ natal Jupiter
        Dec 2 - Mar 2 '26 — Jupiter △ natal Chiron (3x: Dec 15, Jan 8, Feb 12)
    """
    from stellium.core.registry import ASPECT_REGISTRY

    glyph = (
        ASPECT_REGISTRY[p.aspect_name].glyph
        if p.aspect_name in ASPECT_REGISTRY
        else p.aspect_name
    )
    label = f"{p.transit_planet} {glyph} natal {p.natal_planet}"

    if p.start and p.end:
        date_str = f"{_fmt_date(p.start, ref_year)} – {_fmt_date(p.end, ref_year)}"
    elif p.exact_dates:
        date_str = _fmt_date(p.exact_dates[0], ref_year)
    else:
        date_str = "?"

    result = f"{date_str} — {label}"

    if p.is_multi_pass:
        pass_strs = ", ".join(_fmt_date(d, ref_year) for d in p.exact_dates)
        result += f" ({len(p.exact_dates)}x: {pass_strs})"

    return result


# ---------------------------------------------------------------------------
# TransitListSection
# ---------------------------------------------------------------------------


class TransitListSection:
    """
    Natal transit aspect periods as a plain-text list.

    Shows when transiting planets form aspects to natal positions,
    with orb entry/exit dates, e.g.::

        Dec 2 - Mar 2 '26 — Jupiter △ natal Chiron
        Dec 4 — Mercury □ natal Jupiter
        Jan 8 - Feb 6 '26 — Uranus △ natal Neptune (3x: Jan 15, Jan 30, Feb 12)

    Usage::

        section = TransitListSection(
            start=datetime(2025, 12, 1),
            end=datetime(2026, 6, 1),
        )
        report = ReportBuilder().from_chart(natal_chart).add_section(section)
        report.render()

    Note: The chart parameter in generate_data() is the natal chart.
    """

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        transit_planets: list[str] | None = None,
        aspects: dict[str, float] | None = None,
        include_natal_points: list[str] | None = None,
        exclude_fast_planets: bool = False,
    ) -> None:
        """
        Initialize transit list section.

        Args:
            start:                Start of transit window (UTC).
            end:                  End of transit window (UTC).
            transit_planets:      Planets to use as transits (default: all 12).
            aspects:              Dict of {aspect_name: orb_degrees} (default: 5 major).
            include_natal_points: Limit natal points checked (default: all planets).
            exclude_fast_planets: If True, exclude Sun, Moon, Mercury, Venus, Mars.
        """
        self.start = start
        self.end = end
        self.aspects = aspects or DEFAULT_TRANSIT_ASPECTS
        planets = list(transit_planets or DEFAULT_TRANSIT_PLANETS)
        if exclude_fast_planets:
            planets = [p for p in planets if p not in _FAST_PLANETS]
        self.transit_planets = planets
        self.include_natal_points = include_natal_points

    @property
    def section_name(self) -> str:
        return "Natal Transits"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Calculate and return transit periods as text rows.

        Args:
            chart: The natal CalculatedChart to transit to.

        Returns:
            Dict with type="text" and structured period data.
        """
        periods = calculate_transit_periods(
            natal_chart=chart,
            start=self.start,
            end=self.end,
            transit_planets=self.transit_planets,
            aspects=self.aspects,
            include_natal_points=self.include_natal_points,
        )

        ref_year = self.start.year
        lines = [_fmt_period(p, ref_year) for p in periods]

        return {
            "type": "text",
            "title": self.section_name,
            "subtitle": (
                f"{self.start.strftime('%Y-%m-%d')} to "
                f"{self.end.strftime('%Y-%m-%d')}"
            ),
            "date_range": {
                "start": self.start.strftime("%Y-%m-%d"),
                "end": self.end.strftime("%Y-%m-%d"),
            },
            "total_transits": len(periods),
            "text": "\n".join(lines),
            # Structured data for custom renderers
            "periods": [
                {
                    "transit_planet": p.transit_planet,
                    "natal_planet": p.natal_planet,
                    "aspect_name": p.aspect_name,
                    "aspect_angle": p.aspect_angle,
                    "orb": p.orb,
                    "start": p.start.isoformat() if p.start else None,
                    "end": p.end.isoformat() if p.end else None,
                    "exact_dates": [d.isoformat() for d in p.exact_dates],
                    "is_multi_pass": p.is_multi_pass,
                    "duration_days": p.duration_days,
                    "label": _fmt_period(p, ref_year),
                }
                for p in periods
            ],
        }


# ---------------------------------------------------------------------------
# TransitGanttSection
# ---------------------------------------------------------------------------

# SVG layout constants
_LABEL_WIDTH = 200
_RIGHT_PAD = 20
_HEADER_HEIGHT = 30
_ROW_HEIGHT = 14
_ROW_PAD = 2
_BG_COLOR = "#1a1a2e"
_GRID_COLOR = "#333355"
_TEXT_COLOR = "#cccccc"
_MONTH_COLOR = "#8888aa"


class TransitGanttSection:
    """
    Natal transit periods as an SVG Gantt timeline chart.

    Each row is a transit event; bars span the orb window; tick marks
    indicate exact dates. Rows are grouped by transiting planet.

    Defaults to excluding fast planets (Sun, Moon, Mercury, Venus, Mars)
    since their many short transits make the chart unreadable. Use
    TransitListSection for comprehensive fast-planet output.

    Usage::

        section = TransitGanttSection(
            start=datetime(2025, 12, 1),
            end=datetime(2026, 6, 1),
        )
        report = ReportBuilder().from_chart(natal_chart).add_section(section)
        report.render(format="pdf")
    """

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        transit_planets: list[str] | None = None,
        aspects: dict[str, float] | None = None,
        include_natal_points: list[str] | None = None,
        width: int = 900,
        row_height: int = _ROW_HEIGHT,
        exclude_fast_planets: bool = True,
    ) -> None:
        """
        Initialize transit Gantt section.

        Args:
            start:                Start of transit window (UTC).
            end:                  End of transit window (UTC).
            transit_planets:      Planets to use as transits (default: all 12).
            aspects:              Dict of {aspect_name: orb_degrees} (default: 5 major).
            include_natal_points: Limit natal points checked (default: all planets).
            width:                Total SVG width in pixels (default: 900).
            row_height:           Height of each row in pixels (default: 14).
            exclude_fast_planets: If True, exclude Sun, Moon, Mercury, Venus, Mars
                                  (default: True — they overwhelm the chart).
        """
        self.start = start
        self.end = end
        self.aspects = aspects or DEFAULT_TRANSIT_ASPECTS
        planets = list(transit_planets or DEFAULT_TRANSIT_PLANETS)
        if exclude_fast_planets:
            planets = [p for p in planets if p not in _FAST_PLANETS]
        self.transit_planets = planets
        self.include_natal_points = include_natal_points
        self.width = width
        self.row_height = row_height

    @property
    def section_name(self) -> str:
        return "Transit Timeline"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Calculate and return transit periods as an SVG Gantt chart.

        Args:
            chart: The natal CalculatedChart to transit to.

        Returns:
            Dict with type="svg" and SVG content string.
        """
        periods = calculate_transit_periods(
            natal_chart=chart,
            start=self.start,
            end=self.end,
            transit_planets=self.transit_planets,
            aspects=self.aspects,
            include_natal_points=self.include_natal_points,
        )

        svg_content = self._render_gantt(periods)
        height = self._calc_height(periods)

        return {
            "type": "svg",
            "title": self.section_name,
            "subtitle": (
                f"{self.start.strftime('%Y-%m-%d')} to "
                f"{self.end.strftime('%Y-%m-%d')}"
            ),
            "content": svg_content,
            "width": self.width,
            "height": height,
            "total_transits": len(periods),
        }

    def _calc_height(self, periods: list[TransitPeriod]) -> int:
        """Calculate total SVG height based on number of rows."""
        by_planet: dict[str, list] = defaultdict(list)
        for p in periods:
            by_planet[p.transit_planet].append(p)

        # Count: one header row per planet + one data row per period
        n_rows = sum(1 + len(ps) for ps in by_planet.values())
        return _HEADER_HEIGHT + n_rows * (self.row_height + _ROW_PAD) + 20

    def _render_gantt(self, periods: list[TransitPeriod]) -> str:
        """Render periods as an SVG Gantt chart string."""
        import svgwrite

        from stellium.core.registry import ASPECT_REGISTRY

        if not periods:
            dwg = svgwrite.Drawing(size=(400, 40))
            dwg.add(
                dwg.text(
                    "No transits found in this period.",
                    insert=(10, 25),
                    font_family="sans-serif",
                    font_size=12,
                    fill="#666666",
                )
            )
            return dwg.tostring()

        chart_width = self.width - _LABEL_WIDTH - _RIGHT_PAD
        total_days = max((self.end - self.start).total_seconds() / 86400, 1)

        def date_to_x(d: dt.datetime) -> float:
            days = (d - self.start).total_seconds() / 86400
            return _LABEL_WIDTH + (days / total_days) * chart_width

        # Group periods by transiting planet, preserving transit_planets order
        by_planet: dict[str, list[TransitPeriod]] = defaultdict(list)
        for p in periods:
            by_planet[p.transit_planet].append(p)

        # Build ordered row list: (planet_name, period_or_None_for_header)
        rows: list[tuple[str, TransitPeriod | None]] = []
        for planet in self.transit_planets:
            if planet not in by_planet:
                continue
            rows.append((planet, None))  # planet group header
            for p in by_planet[planet]:
                rows.append((planet, p))

        height = self._calc_height(periods)
        dwg = svgwrite.Drawing(size=(self.width, height))

        # Background
        dwg.add(dwg.rect(insert=(0, 0), size=(self.width, height), fill=_BG_COLOR))

        # Month grid lines and labels
        current = self.start.replace(day=1)
        while current <= self.end:
            x = date_to_x(current)
            if x >= _LABEL_WIDTH:
                dwg.add(
                    dwg.line(
                        start=(x, _HEADER_HEIGHT - 8),
                        end=(x, height - 10),
                        stroke=_GRID_COLOR,
                        stroke_width=0.5,
                    )
                )
                month_label = (
                    current.strftime("%b %Y")
                    if current.month == 1
                    else current.strftime("%b")
                )
                dwg.add(
                    dwg.text(
                        month_label,
                        insert=(x + 3, _HEADER_HEIGHT - 10),
                        font_family="sans-serif",
                        font_size=9,
                        fill=_MONTH_COLOR,
                    )
                )
            # Advance to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Today marker (dashed white line)
        # Use timezone-aware UTC if start/end are aware; naive UTC otherwise
        if self.start.tzinfo is not None:
            today = dt.datetime.now(dt.UTC)
        else:
            today = dt.datetime.now(dt.UTC).replace(tzinfo=None)
        if self.start <= today <= self.end:
            tx = date_to_x(today)
            dwg.add(
                dwg.line(
                    start=(tx, _HEADER_HEIGHT - 8),
                    end=(tx, height - 10),
                    stroke="#ffffff",
                    stroke_width=0.8,
                    stroke_dasharray="3,3",
                    opacity=0.4,
                )
            )

        # Rows
        rh = self.row_height
        rpad = _ROW_PAD
        for row_idx, (planet, period) in enumerate(rows):
            y_top = _HEADER_HEIGHT + row_idx * (rh + rpad)
            y_mid = y_top + rh / 2
            planet_color = _PLANET_COLORS.get(planet, "#aaaaaa")

            if period is None:
                # Planet group header row
                dwg.add(
                    dwg.text(
                        planet,
                        insert=(_LABEL_WIDTH - 5, y_mid + 4),
                        font_family="sans-serif",
                        font_size=9,
                        fill=planet_color,
                        font_weight="bold",
                        text_anchor="end",
                    )
                )
                dwg.add(
                    dwg.line(
                        start=(_LABEL_WIDTH, y_top),
                        end=(self.width - _RIGHT_PAD, y_top),
                        stroke=_GRID_COLOR,
                        stroke_width=0.3,
                    )
                )
            else:
                aspect_glyph = (
                    ASPECT_REGISTRY[period.aspect_name].glyph
                    if period.aspect_name in ASPECT_REGISTRY
                    else ""
                )
                bar_color = _ASPECT_COLORS.get(period.aspect_name, planet_color)

                # Row label: "△ Sun" etc.
                dwg.add(
                    dwg.text(
                        f"{aspect_glyph} {period.natal_planet}",
                        insert=(_LABEL_WIDTH - 5, y_mid + 3),
                        font_family="sans-serif",
                        font_size=8,
                        fill=_TEXT_COLOR,
                        text_anchor="end",
                    )
                )

                # Orb window bar
                bar_x = date_to_x(period.start) if period.start else _LABEL_WIDTH
                bar_end = (
                    date_to_x(period.end) if period.end else _LABEL_WIDTH + chart_width
                )
                bar_w = max(2.0, bar_end - bar_x)
                dwg.add(
                    dwg.rect(
                        insert=(bar_x, y_top + 1),
                        size=(bar_w, rh - 2),
                        fill=bar_color,
                        opacity=0.6,
                        rx=2,
                        ry=2,
                    )
                )

                # Exact date tick marks (white vertical lines on bar)
                for exact_dt in period.exact_dates:
                    ex = date_to_x(exact_dt)
                    if _LABEL_WIDTH <= ex <= (_LABEL_WIDTH + chart_width):
                        dwg.add(
                            dwg.line(
                                start=(ex, y_top + 1),
                                end=(ex, y_top + rh - 1),
                                stroke="#ffffff",
                                stroke_width=1.0,
                                opacity=0.85,
                            )
                        )

        return dwg.tostring()
