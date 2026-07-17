"""
Timing technique report sections.

Includes:

- ProfectionSection: Annual and monthly profections
- ZodiacalReleasingSection: Zodiacal releasing periods and timeline
"""

import datetime as dt
from typing import Any

from stellium.core.models import CalculatedChart, ZRPeriod, ZRSnapshot, ZRTimeline
from stellium.core.registry import CELESTIAL_REGISTRY
from stellium.i18n import format_date, get_default_locale, msg, render, term

from ._utils import get_sign_glyph, glyph_label


class ProfectionSection:
    """
    Profection timing analysis section.

    Shows annual profections with Lord of the Year, activated house,
    and optionally monthly profections and multi-point analysis.
    """

    def __init__(
        self,
        age: int | None = None,
        date: dt.datetime | str | None = None,
        include_monthly: bool = True,
        include_multi_point: bool = True,
        include_timeline: bool = False,
        timeline_range: tuple[int, int] | None = None,
        points: list[str] | None = None,
        house_system: str | None = None,
        rulership: str = "traditional",
    ) -> None:
        """
        Initialize profection section.

        Args:
            age: Age for profection (either age OR date required)
            date: Target date for profection (datetime or ISO string)
            include_monthly: Show monthly profection (when date provided)
            include_multi_point: Show profections for ASC, Sun, Moon, MC
            include_timeline: Show timeline of Lords
            timeline_range: Range for timeline, e.g., (25, 40). If None, uses age±5
            points: Custom points for multi-point (default: ASC, Sun, Moon, MC)
            house_system: House system to use (default: prefers Whole Sign)
            rulership: "traditional" or "modern"
        """
        if age is None and date is None:
            raise ValueError("Either age or date must be provided for profections")

        self.age = age
        self.date = date
        self.include_monthly = include_monthly
        self.include_multi_point = include_multi_point
        self.include_timeline = include_timeline
        self.timeline_range = timeline_range
        self.points = points
        self.house_system = house_system
        self.rulership = rulership

    @property
    def section_name(self) -> str:
        if self.age is not None:
            return f"Profections (Age {self.age})"
        elif self.date:
            date_str = (
                self.date
                if isinstance(self.date, str)
                else self.date.strftime("%Y-%m-%d")
            )
            return f"Profections ({date_str})"
        return "Profections"

    def generate_data(self, chart: CalculatedChart) -> dict:
        """
        Generate profection analysis data.
        """
        from stellium.engines.profections import ProfectionEngine

        # Create engine
        try:
            engine = ProfectionEngine(chart, self.house_system, self.rulership)
        except ValueError as e:
            return {
                "type": "text",
                "text": f"Could not calculate profections: {e}",
            }

        # Calculate the age
        if self.date is not None:
            if isinstance(self.date, str):
                target_date = dt.datetime.fromisoformat(self.date)
            else:
                target_date = self.date
            age = engine._calculate_age_at_date(target_date)
        else:
            age = self.age
            target_date = None

        # Build result sections
        sections = []

        # Section 1: Annual Profection Summary
        annual = engine.annual(age)
        summary_data = self._build_annual_summary(annual, engine.house_system)
        sections.append(("Annual Profection", summary_data))

        # Section 2: Monthly Profection (if date provided)
        if self.include_monthly and target_date is not None:
            annual_result, monthly_result = engine.for_date(target_date)
            monthly_data = self._build_monthly_summary(monthly_result, age)
            sections.append(("Monthly Profection", monthly_data))

        # Section 3: Multi-Point Lords
        if self.include_multi_point:
            multi = engine.multi(age, self.points)
            multi_data = self._build_multi_point_table(multi)
            sections.append(("All Lords", multi_data))

        # Section 4: Planets in Profected House
        if annual.planets_in_house:
            planets_data = self._build_planets_in_house(annual)
            sections.append(("Natal Planets in Activated House", planets_data))

        # Section 5: Lord's Natal Condition
        lord_data = self._build_lord_condition(annual)
        sections.append(("Lord of Year - Natal Condition", lord_data))

        # Section 6: Timeline (if enabled)
        if self.include_timeline:
            if self.timeline_range:
                start, end = self.timeline_range
            else:
                # Default: age ± 5
                start = max(0, age - 5)
                end = age + 5

            timeline = engine.timeline(start, end)
            timeline_data = self._build_timeline_table(timeline, age)
            sections.append((f"Timeline (Ages {start}-{end})", timeline_data))

        # Build compound result
        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_annual_summary(self, result, house_system: str) -> dict:
        """Build the annual profection summary."""
        # Get ruler glyph
        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        # Get sign glyph
        sign_glyph = get_sign_glyph(result.profected_sign)

        data: dict[str, Any] = {
            "Age": str(result.units),
            "Activated House": msg("House {number}", number=result.profected_house),
            "Activated Sign": msg(
                "{glyph} {sign}",
                glyph=sign_glyph,
                sign=term(f"sign.{result.profected_sign}"),
            ),
            "Lord of the Year": glyph_label(ruler_glyph, f"body.{result.ruler}"),
            "House System": house_system,
        }

        if result.ruler_modern:
            modern_glyph = ""
            if result.ruler_modern in CELESTIAL_REGISTRY:
                modern_glyph = CELESTIAL_REGISTRY[result.ruler_modern].glyph
            data["Modern Ruler"] = glyph_label(
                modern_glyph, f"body.{result.ruler_modern}"
            )

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_monthly_summary(self, result, age: int) -> dict:
        """Build monthly profection summary."""
        month = result.units - age

        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        sign_glyph = get_sign_glyph(result.profected_sign)

        data: dict[str, Any] = {
            "Month in Year": str(month),
            "Activated House": msg("House {number}", number=result.profected_house),
            "Activated Sign": msg(
                "{glyph} {sign}",
                glyph=sign_glyph,
                sign=term(f"sign.{result.profected_sign}"),
            ),
            "Lord of the Month": glyph_label(ruler_glyph, f"body.{result.ruler}"),
        }

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_multi_point_table(self, multi) -> dict:
        """Build multi-point lords table."""
        headers = ["Point", "Activated House", "Sign", "Lord"]
        rows = []

        for point, result in multi.results.items():
            point_glyph = ""
            if point in CELESTIAL_REGISTRY:
                point_glyph = CELESTIAL_REGISTRY[point].glyph

            sign_glyph = get_sign_glyph(result.profected_sign)

            ruler_glyph = ""
            if result.ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

            rows.append(
                [
                    glyph_label(point_glyph, f"body.{point}"),
                    msg("House {number}", number=result.profected_house),
                    msg(
                        "{glyph} {sign}",
                        glyph=sign_glyph,
                        sign=term(f"sign.{result.profected_sign}"),
                    ),
                    glyph_label(ruler_glyph, f"body.{result.ruler}"),
                ]
            )

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _build_planets_in_house(self, result) -> dict:
        """Build list of natal planets in the activated house."""
        planet_names = []
        for planet in result.planets_in_house:
            glyph = ""
            if planet.name in CELESTIAL_REGISTRY:
                glyph = CELESTIAL_REGISTRY[planet.name].glyph
            planet_names.append(f"{glyph} {planet.name}" if glyph else planet.name)

        return {
            "type": "text",
            "text": f"House {result.profected_house} contains: {', '.join(planet_names)}",
        }

    def _build_lord_condition(self, result) -> dict:
        """Build Lord of Year natal condition details."""
        if result.ruler_position is None:
            return {
                "type": "text",
                "text": f"{result.ruler} position not found in chart.",
            }

        pos = result.ruler_position
        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        sign_glyph = get_sign_glyph(pos.sign)

        # Format degree/minute
        degree = int(pos.sign_degree)
        minute = int((pos.sign_degree % 1) * 60)

        data: dict[str, Any] = {
            "Planet": glyph_label(ruler_glyph, f"body.{result.ruler}"),
            "Natal Sign": msg(
                "{glyph} {sign}", glyph=sign_glyph, sign=term(f"sign.{pos.sign}")
            ),
            "Natal Degree": f"{degree}°{minute:02d}'",
            "Natal House": msg("House {number}", number=result.ruler_house)
            if result.ruler_house
            else "—",
            "Retrograde": "Yes ℞" if pos.is_retrograde else "No",
        }

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_timeline_table(self, timeline, current_age: int) -> dict:
        """Build timeline table with Lords sequence."""
        headers = ["Age", "House", "Sign", "Lord"]
        rows = []

        for entry in timeline.entries:
            sign_glyph = get_sign_glyph(entry.profected_sign)
            ruler_glyph = ""
            if entry.ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[entry.ruler].glyph

            # Mark current age
            age_str = str(entry.units)
            if entry.units == current_age:
                age_str = f"→ {entry.units} ←"

            rows.append(
                [
                    age_str,
                    msg("House {number}", number=entry.profected_house),
                    msg(
                        "{glyph} {sign}",
                        glyph=sign_glyph,
                        sign=term(f"sign.{entry.profected_sign}"),
                    ),
                    glyph_label(ruler_glyph, f"body.{entry.ruler}"),
                ]
            )

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }


class ZodiacalReleasingSection:
    """
    Zodiacal Releasing timing analysis section.

    Shows ZR periods from one or more Lots (Fortune, Spirit, etc.),
    with options to display current snapshot and/or L1 timeline.

    Snapshot mode shows:

    - Current L1/L2 periods (always shown)
    - L3/L4 context (current ± 2 periods) for finer timing

    Timeline mode shows:

    - All L1 periods with ages and status indicators
    - Peak (★), Angular (◆), and Current (⚡) markers
    """

    def __init__(
        self,
        lots: str | list[str] | None = None,
        mode: str = "both",
        query_date: dt.datetime | str | None = None,
        query_age: float | None = None,
        context_periods: int = 2,
    ) -> None:
        """
        Initialize Zodiacal Releasing section.

        Args:
            lots: Which lot(s) to display:

                - str: Single lot name (e.g., "Part of Fortune")
                - list[str]: Multiple lots (e.g., ["Part of Fortune", "Part of Spirit"])
                - None or "all": All lots calculated in the chart
            mode: Display mode:

                - "snapshot": Current periods only
                - "timeline": L1 timeline only
                - "both": Both snapshot and timeline (DEFAULT)
            query_date: Date for snapshot (defaults to now)

                - datetime: Use this date
                - str: Parse as ISO format
                - None: Use current date/time
            query_age: Age for snapshot (alternative to query_date)

                - float: Use this age
                - None: Calculate from query_date
            context_periods: Number of periods before/after current to show
                for L3/L4 context (default: 2)
        """
        # Normalize lots parameter
        if lots is None or lots == "all":
            self._lots_mode = "all"
            self._lots = None
        elif isinstance(lots, str):
            self._lots_mode = "specific"
            self._lots = [lots]
        else:
            self._lots_mode = "specific"
            self._lots = list(lots)

        if mode not in ("snapshot", "timeline", "both"):
            raise ValueError(
                f"mode must be 'snapshot', 'timeline', or 'both', got {mode}"
            )

        self.mode = mode
        self.context_periods = context_periods

        # Handle query date/age
        if query_date is not None:
            if isinstance(query_date, str):
                self._query_date = dt.datetime.fromisoformat(query_date)
            else:
                self._query_date = query_date
            self._query_age = None
        elif query_age is not None:
            self._query_date = None
            self._query_age = query_age
        else:
            # Default to now
            self._query_date = dt.datetime.now(dt.UTC)
            self._query_age = None

    @property
    def section_name(self) -> str:
        return "Zodiacal Releasing"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate Zodiacal Releasing data."""
        # Check if ZR data exists
        if "zodiacal_releasing" not in chart.metadata:
            return {
                "type": "text",
                "text": (
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

        # Determine which lots to show
        if self._lots_mode == "all":
            lots_to_show = list(zr_data.keys())
        else:
            lots_to_show = [lot for lot in self._lots if lot in zr_data]

        if not lots_to_show:
            return {
                "type": "text",
                "text": "No Zodiacal Releasing data found for the specified lot(s).",
            }

        # Build sections for each lot
        sections = []

        for lot_name in lots_to_show:
            timeline: ZRTimeline = zr_data[lot_name]

            # Get snapshot for query date/age
            try:
                if self._query_age is not None:
                    snapshot = timeline.at_age(self._query_age)
                else:
                    snapshot = timeline.at_date(self._query_date)
            except ValueError:
                # Date outside timeline range - use age 0 as fallback
                snapshot = timeline.at_age(0)

            # Build lot header — the lot name and its sign are both terms.
            lot_token = msg(lot_name)
            lot_title = msg(
                "{lot} ({sign})",
                lot=lot_token,
                sign=term(f"sign.{timeline.lot_sign}"),
            )

            if self.mode in ("snapshot", "both"):
                # Add snapshot section
                snapshot_data = self._build_snapshot(timeline, snapshot, chart)
                sections.append((lot_title, snapshot_data))

            if self.mode in ("timeline", "both"):
                # Add timeline section
                timeline_data = self._build_timeline(timeline, snapshot)
                timeline_title = (
                    msg("{lot} — L1 Timeline", lot=lot_token)
                    if self.mode == "both"
                    else lot_title
                )
                sections.append((timeline_title, timeline_data))

        # Return as compound section
        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_snapshot(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot, chart: CalculatedChart
    ) -> dict[str, Any]:
        """Build snapshot display showing current periods at all levels."""
        sections = []

        # Header info. The date is laid out per locale; the age string and status labels
        # are messages. Values in a key_value localize through the resolve pass.
        # key_value keys stay plain strings — the resolve pass wraps them as messages
        # (a token is unhashable and can't be a dict key). Values may be tokens.
        loc = get_default_locale()
        header_data: dict[str, Any] = {
            "Current Age": msg(
                "{age} years ({date})",
                age=f"{snapshot.age:.1f}",
                date=format_date(snapshot.date, loc),
            ),
            "Active Rulers": self._format_rulers(snapshot.rulers),
        }

        # Add status indicators (joined with " | ", so composed as one message to keep
        # that separator rather than the comma a list would join with).
        status_parts = []
        if snapshot.is_peak:
            status_parts.append(msg("★ Peak Period"))
        if snapshot.is_lb:
            status_parts.append(msg("⚡ Loosing of Bond"))
        if len(status_parts) == 2:
            header_data["Status"] = msg(
                "{a} | {b}", a=status_parts[0], b=status_parts[1]
            )
        elif status_parts:
            header_data["Status"] = status_parts[0]

        sections.append(
            (msg("Current State"), {"type": "key_value", "data": header_data})
        )

        # L1/L2 table (always show)
        l1_l2_table = self._build_l1_l2_table(snapshot, chart)
        sections.append((msg("Major Periods"), l1_l2_table))

        # L3 context (if available)
        if snapshot.l3 is not None:
            l3_context = self._build_level_context(timeline, snapshot, level=3)
            sections.append((msg("L3 Context"), l3_context))

        # L4 context (if available)
        if snapshot.l4 is not None:
            l4_context = self._build_level_context(timeline, snapshot, level=4)
            sections.append((msg("L4 Context"), l4_context))

        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_l1_l2_table(
        self, snapshot: ZRSnapshot, chart: CalculatedChart
    ) -> dict[str, Any]:
        """Build table for L1 and L2 periods."""
        headers = [
            msg("Level"),
            msg("Sign"),
            msg("Ruler"),
            msg("Period"),
            msg("Quality"),
            msg("Status"),
        ]
        rows = []

        # L1 row
        l1 = snapshot.l1
        l1_age_start = (l1.start - chart.datetime.utc_datetime).days / 365.25
        l1_age_end = (l1.end - chart.datetime.utc_datetime).days / 365.25
        l1_period = msg(
            "Ages {start} - {end}",
            start=f"{l1_age_start:.0f}",
            end=f"{l1_age_end:.0f}",
        )

        rows.append(
            [
                msg("L1 (Major)"),
                self._sign_cell(l1.sign),
                self._format_ruler(l1.ruler),
                l1_period,
                self._format_quality(l1),
                self._format_period_status(l1),
            ]
        )

        # L2 row
        l2 = snapshot.l2
        l2_period = msg(
            "{start} - {end}",
            start=self._month_year(l2.start),
            end=self._month_year(l2.end),
        )

        rows.append(
            [
                msg("L2 (Sub)"),
                self._sign_cell(l2.sign),
                self._format_ruler(l2.ruler),
                l2_period,
                self._format_quality(l2),
                self._format_period_status(l2),
            ]
        )

        return {"type": "table", "headers": headers, "rows": rows}

    def _build_level_context(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot, level: int
    ) -> dict[str, Any]:
        """Build context table for L3 or L4 showing periods around current."""
        loc = get_default_locale()
        periods = timeline.periods.get(level, [])
        if not periods:
            return {
                "type": "text",
                "text": render(msg("No L{n} data available.", n=level), loc),
            }

        # Find current period index
        current_period = snapshot.l3 if level == 3 else snapshot.l4
        if current_period is None:
            return {
                "type": "text",
                "text": render(msg("No L{n} data available.", n=level), loc),
            }

        # Find index of current period
        current_idx = None
        for i, p in enumerate(periods):
            if p.start == current_period.start:
                current_idx = i
                break

        if current_idx is None:
            return {
                "type": "text",
                "text": render(
                    msg("Could not locate current L{n} period.", n=level), loc
                ),
            }

        # Get context window
        start_idx = max(0, current_idx - self.context_periods)
        end_idx = min(len(periods), current_idx + self.context_periods + 1)
        context_periods = periods[start_idx:end_idx]

        # Build table
        headers = [msg("Sign"), msg("Ruler"), msg("Period"), msg("Status")]
        rows = []

        for period in context_periods:
            is_current = period.start == current_period.start
            period_str = msg(
                "{start} - {end}",
                start=self._month_day(period.start),
                end=self._month_day(period.end),
            )
            rows.append(
                [
                    self._sign_cell(period.sign, current=is_current),
                    self._format_ruler(period.ruler),
                    period_str,
                    self._format_period_status(period),
                ]
            )

        return {"type": "table", "headers": headers, "rows": rows}

    def _build_timeline(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot
    ) -> dict[str, Any]:
        """Build L1 timeline table."""
        loc = get_default_locale()
        l1_periods = timeline.l1_periods()

        if not l1_periods:
            return {
                "type": "text",
                "text": render(msg("No L1 timeline data available."), loc),
            }

        headers = [
            msg("Sign"),
            msg("Ruler"),
            msg("Ages"),
            msg("Quality"),
            msg("Status"),
        ]
        rows = []

        for period in l1_periods:
            is_current = period.start == snapshot.l1.start

            # Calculate ages
            age_start = (period.start - timeline.birth_date).days / 365.25
            age_end = (period.end - timeline.birth_date).days / 365.25
            ages_str = f"{age_start:3.0f} - {age_end:3.0f}"

            rows.append(
                [
                    self._sign_cell(period.sign, current=is_current),
                    self._format_ruler(period.ruler),
                    ages_str,
                    self._format_quality(period),
                    self._format_period_status(period),
                ]
            )

        # Legend (baked; footer is free-form text). The glyph keys are neutral, the words
        # localize.
        legend = render(
            msg(
                "★ = {peak}  ◆ = {angular}  ⚡ = {current}  LB = {lb}  +/- = {score}",
                peak=msg("Peak (10th)"),
                angular=msg("Angular"),
                current=msg("Current"),
                lb=msg("Loosing of Bond"),
                score=msg("Quality Score"),
            ),
            loc,
        )

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "footer": legend,
        }

    def _format_period_status(self, period: ZRPeriod) -> Any:
        """Format status indicators for a period as a token (or empty string)."""
        parts = []
        if period.is_peak:
            parts.append(msg("★ Peak (10th)"))
        elif period.is_angular:
            parts.append(msg("◆ Angular ({angle})", angle=period.angle_from_lot))
        if period.is_loosing_bond:
            parts.append(msg("LB"))
        if not parts:
            return ""
        if len(parts) == 2:
            return msg("{a} | {b}", a=parts[0], b=parts[1])
        return parts[0]

    # The scoring engine's internal role names → the abbreviations the report prints.
    _ROLE_ABBR = {
        "sect_benefic": "S.Ben",
        "contrary_benefic": "C.Ben",
        "sect_malefic": "S.Mal",
        "contrary_malefic": "C.Mal",
        "sect_light": "S.Lgt",
        "contrary_light": "C.Lgt",
    }

    def _format_quality(self, period: ZRPeriod) -> Any:
        """Format quality/scoring for a period. Score and sentiment icon are neutral; the
        ruler-role abbreviation is a message so a locale can render it."""
        if period.sentiment == "positive":
            sentiment_icon = "✓"
        elif period.sentiment == "challenging":
            sentiment_icon = "✗"
        else:
            sentiment_icon = "—"
        base = f"{period.score:+d} {sentiment_icon}"

        if period.ruler_role:
            abbr = self._ROLE_ABBR.get(period.ruler_role, period.ruler_role)
            return msg("{base} ({role})", base=base, role=msg(abbr))
        return base

    def _format_ruler(self, ruler: str) -> Any:
        """Format ruler as a glyph + catalog-term token (localizes in the resolve pass)."""
        glyph = CELESTIAL_REGISTRY[ruler].glyph if ruler in CELESTIAL_REGISTRY else ""
        return glyph_label(glyph, f"body.{ruler}")

    def _format_rulers(self, rulers: list[str]) -> list[Any]:
        """Format multiple rulers as tokens (a list renders comma-joined)."""
        return [self._format_ruler(r) for r in rulers]

    def _sign_cell(self, sign: str, *, current: bool = False) -> Any:
        """A sign cell: glyph + sign term, optionally flagged as the current period."""
        template = "⚡ {glyph} {sign}" if current else "{glyph} {sign}"
        return msg(template, glyph=get_sign_glyph(sign), sign=term(f"sign.{sign}"))

    def _month_year(self, d: dt.datetime) -> Any:
        """A month+year token (locales reorder via the '{month} {year}' template)."""
        return msg(
            "{month} {year}", month=term(f"month.{d.strftime('%B')}"), year=d.year
        )

    def _month_day(self, d: dt.datetime) -> Any:
        """A month+day token (locales reorder via the '{month} {day}' template)."""
        return msg("{month} {day}", month=term(f"month.{d.strftime('%B')}"), day=d.day)
