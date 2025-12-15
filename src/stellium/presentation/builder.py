"""
Report builder for creating chart reports.

The builder pattern allows users to progressively construct reports
by adding sections one at a time, then rendering in their chosen format.
"""

import datetime as dt
from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.core.protocols import ReportRenderer, ReportSection

from .renderers import PlainTextRenderer, RichTableRenderer
from .sections import (
    ArabicPartsSection,
    AspectPatternSection,
    AspectSection,
    ChartOverviewSection,
    CrossChartAspectSection,
    DeclinationAspectSection,
    DeclinationSection,
    DignitySection,
    DispositorSection,
    EclipseSection,
    FixedStarsSection,
    HouseCuspsSection,
    IngressSection,
    MidpointAspectsSection,
    MidpointSection,
    MoonPhaseSection,
    PlanetPositionSection,
    ProfectionSection,
    StationSection,
    ZodiacalReleasingSection,
)


class ReportBuilder:
    """
    Builder for chart reports.

    Example::

        report = (
            ReportBuilder()
            .from_chart(chart)
            .with_chart_overview()
            .with_planet_positions()
            .render(format="rich_table")
        )
    """

    def __init__(self) -> None:
        """Initialize an empty report builder."""
        self._chart: CalculatedChart | Comparison | MultiChart | None = None
        self._sections: list[ReportSection] = []
        self._chart_image_path: str | None = None
        self._auto_generate_chart_image: bool = False
        self._title: str | None = None

    def from_chart(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> "ReportBuilder":
        """
        Set the chart to generate reports from.

        Args:
            chart: A CalculatedChart, Comparison, or MultiChart

        Returns:
            Self for chaining
        """
        self._chart = chart
        return self

    def _is_comparison(self) -> bool:
        """Check if the current chart is a Comparison object."""
        return isinstance(self._chart, Comparison)

    def _is_multichart(self) -> bool:
        """Check if the current chart is a MultiChart object."""
        return isinstance(self._chart, MultiChart)

    def with_chart_image(self, path: str | None = None) -> "ReportBuilder":
        """
        Include a chart wheel image in the report.

        When called without arguments, automatically generates a chart SVG
        using the chart's default draw settings.

        Args:
            path: Optional path to an existing SVG file. If not provided,
                  a chart image will be auto-generated when rendering.

        Returns:
            Self for chaining

        Examples:
            # Auto-generate chart image
            report.with_chart_image()

            # Use existing SVG file
            report.with_chart_image("my_chart.svg")
        """
        if path:
            self._chart_image_path = path
            self._auto_generate_chart_image = False
        else:
            self._auto_generate_chart_image = True
        return self

    def with_title(self, title: str) -> "ReportBuilder":
        """
        Set a custom title for the report.

        The title appears on the cover page of PDF reports.
        If not set, a default title is generated from the chart's name.

        Args:
            title: Custom title string

        Returns:
            Self for chaining

        Examples:
            report.with_title("Birth Chart Analysis")
            report.with_title("Albert Einstein - Complete Natal Analysis")
        """
        self._title = title
        return self

    # -------------------------------------------------------------------------
    # Section Adding Methods
    # -------------------------------------------------------------------------
    # Each .with_*() method adds a section to the report.
    # Sections are not evaluated until render() is called.
    def with_chart_overview(self) -> "ReportBuilder":
        """
        Add chart overview section (birth data, chart type, etc.).

        Returns:
            Self for chaining
        """
        self._sections.append(ChartOverviewSection())
        return self

    def with_planet_positions(
        self,
        include_speed: bool = False,
        include_house: bool = True,
        house_systems: str | list[str] = "all",
    ) -> "ReportBuilder":
        """
        Add planet positions table.

        Args:
            include_speed: Show speed in longitude (for retrogrades)
            include_house: Show house placement
            house_systems: Which house systems to display (DEFAULT: "all")
                - "all": Show all calculated systems
                - list[str]: Show specific systems
                - None: Show default system only

        Returns:
            Self for chaining
        """
        self._sections.append(
            PlanetPositionSection(
                include_speed=include_speed,
                include_house=include_house,
                house_systems=house_systems,
            )
        )
        return self

    def with_aspects(
        self,
        mode: str = "all",
        orbs: bool = True,
        sort_by: str = "orb",  # or "planet" or "aspect_type"
        include_aspectarian: bool = True,
        aspectarian_detailed: bool = False,
        aspectarian_cell_size: int | None = None,
        aspectarian_theme: str | None = None,
    ) -> "ReportBuilder":
        """
        Add aspects table with optional aspectarian grid.

        Args:
            mode: "all", "major", "minor", or "harmonic"
            orbs: Show orb column
            sort_by: How to sort aspects ("orb", "planet", or "aspect_type")
            include_aspectarian: Include aspectarian grid SVG (default: True)
            aspectarian_detailed: Show orb and A/S in aspectarian cells (default: False)
            aspectarian_cell_size: Override cell size for aspectarian (default: config default)
            aspectarian_theme: Theme for aspectarian rendering (default: None)

        Returns:
            Self for chaining

        Note:
            The aspectarian SVG is displayed in HTML/PDF output. Terminal output
            shows a placeholder with dimensions.
        """
        self._sections.append(
            AspectSection(
                mode=mode,
                orbs=orbs,
                sort_by=sort_by,
                include_aspectarian=include_aspectarian,
                aspectarian_detailed=aspectarian_detailed,
                aspectarian_cell_size=aspectarian_cell_size,
                aspectarian_theme=aspectarian_theme,
            )
        )
        return self

    def with_cross_aspects(
        self,
        mode: str = "all",
        orbs: bool = True,
        sort_by: str = "orb",
    ) -> "ReportBuilder":
        """
        Add cross-chart aspects table (for Comparison charts).

        Shows aspects between chart1 planets and chart2 planets with
        appropriate labels for each chart.

        Args:
            mode: "all", "major", "minor", or "harmonic"
            orbs: Show orb column
            sort_by: How to sort aspects ("orb", "planet", "aspect_type")

        Returns:
            Self for chaining

        Note:
            This section requires a Comparison object (from ComparisonBuilder).
            If used with a single CalculatedChart, displays a helpful message.

        Example:
            >>> comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()
            >>> report = (ReportBuilder()
            ...     .from_chart(comparison)
            ...     .with_cross_aspects(mode="major")
            ...     .render())
        """
        self._sections.append(
            CrossChartAspectSection(
                mode=mode,
                orbs=orbs,
                sort_by=sort_by,
            )
        )
        return self

    def with_midpoints(
        self,
        mode: str = "all",
        threshold: int | None = None,
    ) -> "ReportBuilder":
        """
        Add midpoints table.

        Args:
            mode: "all" or "core" (Sun/Moon/ASC/MC midpoints)
            threshold: Only show top N midpoints by importance

        Returns:
            Self for chaining
        """
        self._sections.append(
            MidpointSection(
                mode=mode,
                threshold=threshold,
            )
        )
        return self

    def with_midpoint_aspects(
        self,
        mode: str = "conjunction",
        orb: float = 1.5,
        midpoint_filter: str = "all",
        sort_by: str = "orb",
    ) -> "ReportBuilder":
        """
        Add planets aspecting midpoints table.

        This shows which planets activate which midpoints - the most useful
        way to interpret midpoints. Typically only conjunctions matter (1-2° orb).

        Args:
            mode: Which aspects to check (DEFAULT: "conjunction")
                - "conjunction": Only conjunctions (most common, recommended)
                - "hard": Conjunction, square, opposition
                - "all": All major aspects
            orb: Maximum orb in degrees (DEFAULT: 1.5°)
                Midpoints use tighter orbs than regular aspects.
            midpoint_filter: Which midpoints to check (DEFAULT: "all")
                - "all": All calculated midpoints
                - "core": Only Sun/Moon/ASC/MC midpoints
            sort_by: Sort order (DEFAULT: "orb")
                - "orb": Tightest aspects first
                - "planet": Group by aspecting planet
                - "midpoint": Group by midpoint

        Returns:
            Self for chaining

        Example:
            >>> # Show planets conjunct any midpoint within 1.5°
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_midpoint_aspects()
            ...     .render())
            >>>
            >>> # Show hard aspects to core midpoints only
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_midpoint_aspects(
            ...         mode="hard",
            ...         midpoint_filter="core",
            ...         orb=2.0
            ...     )
            ...     .render())

        Note:
            Requires MidpointCalculator to be added to chart builder:
                chart = (ChartBuilder.from_native(native)
                    .add_component(MidpointCalculator())
                    .calculate())
        """
        self._sections.append(
            MidpointAspectsSection(
                mode=mode,
                orb=orb,
                midpoint_filter=midpoint_filter,
                sort_by=sort_by,
            )
        )
        return self

    def with_arabic_parts(
        self,
        mode: str = "all",
        show_formula: bool = True,
        show_description: bool = False,
    ) -> "ReportBuilder":
        """
        Add Arabic Parts (Lots) table.

        Args:
            mode: Which parts to display (DEFAULT: "all")
                - "all": All calculated parts
                - "core": 7 Hermetic Lots (Fortune, Spirit, Eros, etc.)
                - "family": Family & Relationship Lots
                - "life": Life Topic Lots
                - "planetary": Planetary Exaltation Lots
            show_formula: Include the formula column (DEFAULT: True)
                Formula shows as "ASC + Point2 - Point3" with * for sect-aware parts
            show_description: Include part descriptions (DEFAULT: False)

        Returns:
            Self for chaining

        Example:
            >>> # Show all Arabic Parts with formulas
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_arabic_parts()
            ...     .render())
            >>>
            >>> # Show only core Hermetic Lots with descriptions
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_arabic_parts(
            ...         mode="core",
            ...         show_description=True
            ...     )
            ...     .render())

        Note:
            Requires ArabicPartsCalculator to be added to chart builder:
                from stellium.components.arabic_parts import ArabicPartsCalculator

                chart = (ChartBuilder.from_native(native)
                    .add_component(ArabicPartsCalculator())
                    .calculate())
        """
        self._sections.append(
            ArabicPartsSection(
                mode=mode,
                show_formula=show_formula,
                show_description=show_description,
            )
        )
        return self

    def with_house_cusps(self, systems: str | list[str] = "all") -> "ReportBuilder":
        """
        Add house cusps table.

        Args:
            systems: Which house systems to display (DEFAULT: "all")
                - "all": Show all calculated systems
                - list[str]: Show specific systems

        Returns:
            Self for chaining
        """
        self._sections.append(HouseCuspsSection(systems=systems))
        return self

    def with_dignities(
        self,
        essential: str = "both",
        show_details: bool = False,
    ) -> "ReportBuilder":
        """
        Add essential dignities table.

        Args:
            essential: Which essential dignity system(s) to show (DEFAULT: "both")
                - "traditional": Traditional dignities only
                - "modern": Modern dignities only
                - "both": Both systems
                - "none": Skip essential dignities
            show_details: Show dignity names instead of just scores

        Returns:
            Self for chaining

        Note:
            Requires DignityComponent to be added to chart builder.
            If missing, displays helpful message instead of erroring.
        """
        self._sections.append(
            DignitySection(
                essential=essential,
                show_details=show_details,
            )
        )
        return self

    def with_aspect_patterns(
        self,
        pattern_types: str | list[str] = "all",
        sort_by: str = "type",
    ) -> "ReportBuilder":
        """
        Add aspect patterns table (Grand Trines, T-Squares, Yods, etc.).

        Args:
            pattern_types: Which pattern types to show (DEFAULT: "all")
                - "all": Show all detected patterns
                - list[str]: Show specific pattern types
            sort_by: How to sort patterns (DEFAULT: "type")
                - "type": Group by pattern type
                - "element": Group by element
                - "count": Sort by number of planets

        Returns:
            Self for chaining

        Note:
            Requires AspectPatternAnalyzer to be added to chart builder.
            If missing, displays helpful message instead of erroring.
        """
        self._sections.append(
            AspectPatternSection(
                pattern_types=pattern_types,
                sort_by=sort_by,
            )
        )
        return self

    def with_profections(
        self,
        age: int | None = None,
        date: str | None = None,
        include_monthly: bool = True,
        include_multi_point: bool = True,
        include_timeline: bool = False,
        timeline_range: tuple[int, int] | None = None,
        points: list[str] | None = None,
        house_system: str | None = None,
        rulership: str = "traditional",
    ) -> "ReportBuilder":
        """
        Add profection timing analysis section.

        Profections are a Hellenistic technique where the ASC advances
        one sign per year. The planet ruling that sign becomes the
        "Lord of the Year."

        Args:
            age: Age for profection (either age OR date required)
            date: Target date as ISO string (e.g., "2025-06-15")
            include_monthly: Show monthly profection when date is provided
            include_multi_point: Show lords for ASC, Sun, Moon, MC
            include_timeline: Show timeline table of Lords
            timeline_range: Custom range for timeline (e.g., (25, 40))
            points: Custom points for multi-point analysis
            house_system: House system to use (default: prefers Whole Sign)
            rulership: "traditional" or "modern"

        Returns:
            Self for chaining

        Example::

            # By age
            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_profections(age=30)
                .render()
            )

            # By date with timeline
            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_profections(date="2025-06-15", include_timeline=True)
                .render()
            )
        """
        self._sections.append(
            ProfectionSection(
                age=age,
                date=date,
                include_monthly=include_monthly,
                include_multi_point=include_multi_point,
                include_timeline=include_timeline,
                timeline_range=timeline_range,
                points=points,
                house_system=house_system,
                rulership=rulership,
            )
        )
        return self

    def with_zodiacal_releasing(
        self,
        lots: str | list[str] | None = None,
        mode: str = "both",
        query_date: str | None = None,
        query_age: float | None = None,
        context_periods: int = 2,
    ) -> "ReportBuilder":
        """
        Add Zodiacal Releasing timing analysis section.

        Zodiacal Releasing is a Hellenistic predictive technique that divides
        life into major periods ruled by signs, showing when different life
        themes are activated.

        Args:
            lots: Which lot(s) to display:
                - str: Single lot name (e.g., "Part of Fortune")
                - list[str]: Multiple lots (e.g., ["Part of Fortune", "Part of Spirit"])
                - None: All lots calculated in the chart (DEFAULT)
            mode: Display mode:
                - "snapshot": Current periods only
                - "timeline": L1 timeline only
                - "both": Both snapshot and timeline (DEFAULT)
            query_date: Date for snapshot as ISO string (defaults to now)
            query_age: Age for snapshot (alternative to query_date)
            context_periods: Number of L3/L4 periods to show before/after current (default: 2)

        Returns:
            Self for chaining

        Note:
            Requires ZodiacalReleasingAnalyzer to be added during chart calculation:

                from stellium.engines.releasing import ZodiacalReleasingAnalyzer

                chart = (
                    ChartBuilder.from_native(native)
                    .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
                    .calculate()
                )

        Example::

            # Show current ZR state for all calculated lots
            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_zodiacal_releasing()
                .render()
            )

            # Show ZR for specific lot at specific age
            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_zodiacal_releasing(
                    lots="Part of Fortune",
                    mode="snapshot",
                    query_age=30
                )
                .render()
            )

            # Show only L1 timeline for Fortune and Spirit
            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_zodiacal_releasing(
                    lots=["Part of Fortune", "Part of Spirit"],
                    mode="timeline"
                )
                .render()
            )
        """
        self._sections.append(
            ZodiacalReleasingSection(
                lots=lots,
                mode=mode,
                query_date=query_date,
                query_age=query_age,
                context_periods=context_periods,
            )
        )
        return self

    def with_section(self, section: ReportSection) -> "ReportBuilder":
        """
        Add a custom section.

        This allows users to extend the report system with their own sections.

        Args:
            section: Any object implementing the ReportSection protocol

        Returns:
            Self for chaining

        Example::

            class MyCustomSection:
                @property
                def section_name(self) -> str:
                    return "My Analysis"

                def generate_data(self, chart: CalculatedChart) -> dict:
                    return {"type": "text", "text": "Custom analysis..."}

            report = (
                ReportBuilder()
                .from_chart(chart)
                .with_section(MyCustomSection())
                .render()
            )
        """
        self._sections.append(section)
        return self

    def with_moon_phase(self) -> "ReportBuilder":
        """Add moon phase section."""
        self._sections.append(MoonPhaseSection())
        return self

    def with_declinations(self) -> "ReportBuilder":
        """
        Add declinations table.

        Shows planetary declinations (distance from celestial equator),
        direction (north/south), and out-of-bounds status.

        Out-of-bounds planets have declination beyond the Sun's maximum
        (~23°27') and are considered to have extra intensity or unconventional
        expression.

        Returns:
            Self for chaining

        Example:
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_chart_overview()
            ...     .with_declinations()
            ...     .render())
        """
        self._sections.append(DeclinationSection())
        return self

    def with_declination_aspects(
        self,
        mode: str = "all",
        show_orbs: bool = True,
        show_oob_status: bool = True,
        sort_by: str = "orb",
    ) -> "ReportBuilder":
        """
        Add declination aspects table (Parallel and Contraparallel).

        Declination aspects are based on equatorial coordinates rather than
        ecliptic longitude. They represent a different type of planetary
        relationship.

        - Parallel: Two planets at the same declination (same hemisphere).
          Interpreted like a conjunction.
        - Contraparallel: Two planets at equal declination but opposite
          hemispheres. Interpreted like an opposition.

        Args:
            mode: Which aspects to show (DEFAULT: "all")
                - "all": Both parallel and contraparallel
                - "parallel": Only parallel aspects
                - "contraparallel": Only contraparallel aspects
            show_orbs: Show orb column (DEFAULT: True)
            show_oob_status: Show out-of-bounds status (DEFAULT: True)
            sort_by: How to sort aspects (DEFAULT: "orb")
                - "orb": Tightest aspects first
                - "planet": Group by planet
                - "aspect_type": Group by Parallel/Contraparallel

        Returns:
            Self for chaining

        Note:
            Requires .with_declination_aspects() on ChartBuilder:
                chart = (ChartBuilder.from_native(native)
                    .with_aspects()
                    .with_declination_aspects(orb=1.0)
                    .calculate())

        Example:
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_chart_overview()
            ...     .with_declination_aspects(mode="all")
            ...     .render())
        """
        self._sections.append(
            DeclinationAspectSection(
                mode=mode,
                show_orbs=show_orbs,
                show_oob_status=show_oob_status,
                sort_by=sort_by,
            )
        )
        return self

    def with_dispositors(
        self,
        mode: str = "both",
        rulership: str = "traditional",
        house_system: str | None = None,
        show_chains: bool = True,
    ) -> "ReportBuilder":
        """
        Add dispositor analysis section.

        Shows planetary and/or house-based dispositor chains, final dispositor(s),
        and mutual receptions.

        Args:
            mode: Which dispositor analysis to show (DEFAULT: "both")
                - "planetary": Traditional planet-disposes-planet
                - "house": Kate's house-based innovation (life area flow)
                - "both": Show both analyses
            rulership: "traditional" or "modern" rulership system (DEFAULT: "traditional")
            house_system: House system for house-based mode (defaults to chart's default)
            show_chains: Whether to show full disposition chain details (DEFAULT: True)

        Returns:
            Self for chaining

        Example:
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_chart_overview()
            ...     .with_dispositors(mode="both")
            ...     .render())

        Note:
            For graphical output (SVG), use the DispositorEngine directly:
                from stellium.engines.dispositors import DispositorEngine, render_both_dispositors
                engine = DispositorEngine(chart)
                graph = render_both_dispositors(engine.planetary(), engine.house_based())
                graph.render("dispositors", format="svg")
        """
        self._sections.append(
            DispositorSection(
                mode=mode,
                rulership=rulership,
                house_system=house_system,
                show_chains=show_chains,
            )
        )
        return self

    def with_fixed_stars(
        self,
        tier: int | None = None,
        include_keywords: bool = True,
        sort_by: str = "longitude",
    ) -> "ReportBuilder":
        """
        Add fixed stars table.

        Shows positions and metadata for fixed stars in the chart.
        Requires FixedStarsComponent to be added to chart builder.

        Args:
            tier: Filter to specific tier (DEFAULT: None = all tiers)
                - 1: Royal Stars only (Aldebaran, Regulus, Antares, Fomalhaut)
                - 2: Major Stars only
                - 3: Extended Stars only
                - None: All tiers
            include_keywords: Include interpretive keywords column (DEFAULT: True)
            sort_by: Sort order (DEFAULT: "longitude")
                - "longitude": Zodiacal order
                - "magnitude": Brightest first
                - "tier": Royal first, then Major, then Extended

        Returns:
            Self for chaining

        Example:
            >>> # Royal stars only
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_fixed_stars(tier=1)
            ...     .render())
            >>>
            >>> # All stars sorted by brightness
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_fixed_stars(sort_by="magnitude")
            ...     .render())

        Note:
            Requires FixedStarsComponent to be added to chart builder:
                chart = (ChartBuilder.from_native(native)
                    .add_component(FixedStarsComponent())
                    .calculate())
        """
        self._sections.append(
            FixedStarsSection(
                tier=tier,
                include_keywords=include_keywords,
                sort_by=sort_by,
            )
        )
        return self

    def with_stations(
        self,
        end: dt.datetime,
        start: dt.datetime | None = None,
        planets: list[str] | None = None,
        include_minor: bool = False,
    ) -> "ReportBuilder":
        """
        Add planetary stations (retrograde/direct) table.

        Shows when planets station retrograde or direct within a date range.
        Useful for retrograde calendars and transit planning.

        Args:
            end: End date for station search (required)
            start: Start date for station search (optional, defaults to chart date)
            planets: Which planets to include (default: Mercury through Pluto)
            include_minor: Include Chiron (default: False)

        Returns:
            Self for chaining

        Example:
            >>> # Stations for the next year from chart date
            >>> from datetime import datetime, timedelta
            >>> chart_date = chart.datetime.utc_datetime
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_stations(end=chart_date + timedelta(days=365))
            ...     .render())
            >>>
            >>> # Specific date range
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_stations(
            ...         start=datetime(2025, 1, 1),
            ...         end=datetime(2025, 12, 31)
            ...     )
            ...     .render())
        """
        # Use chart date as start if not provided
        if start is None:
            if self._chart is None:
                raise ValueError(
                    "Must call from_chart() before with_stations() when start is not provided"
                )
            if isinstance(self._chart, Comparison):
                start = self._chart.chart1.datetime.utc_datetime
            else:
                start = self._chart.datetime.utc_datetime

        self._sections.append(
            StationSection(
                start=start,
                end=end,
                planets=planets,
                include_minor=include_minor,
            )
        )
        return self

    def with_ingresses(
        self,
        end: dt.datetime,
        start: dt.datetime | None = None,
        planets: list[str] | None = None,
        include_moon: bool = False,
        include_minor: bool = False,
    ) -> "ReportBuilder":
        """
        Add sign ingresses table.

        Shows when planets enter new zodiac signs within a date range.
        Useful for tracking sign changes and transit planning.

        Args:
            end: End date for ingress search (required)
            start: Start date for ingress search (optional, defaults to chart date)
            planets: Which planets to include (default: Sun through Pluto)
            include_moon: Include Moon ingresses (default: False, very frequent)
            include_minor: Include Chiron (default: False)

        Returns:
            Self for chaining

        Example:
            >>> # Ingresses for the next year from chart date
            >>> from datetime import datetime, timedelta
            >>> chart_date = chart.datetime.utc_datetime
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_ingresses(end=chart_date + timedelta(days=365))
            ...     .render())
            >>>
            >>> # Specific date range with Moon included
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_ingresses(
            ...         start=datetime(2025, 1, 1),
            ...         end=datetime(2025, 12, 31),
            ...         include_moon=True
            ...     )
            ...     .render())
        """
        # Use chart date as start if not provided
        if start is None:
            if self._chart is None:
                raise ValueError(
                    "Must call from_chart() before with_ingresses() when start is not provided"
                )
            if isinstance(self._chart, Comparison):
                start = self._chart.chart1.datetime.utc_datetime
            else:
                start = self._chart.datetime.utc_datetime

        self._sections.append(
            IngressSection(
                start=start,
                end=end,
                planets=planets,
                include_moon=include_moon,
                include_minor=include_minor,
            )
        )
        return self

    def with_eclipses(
        self,
        end: dt.datetime,
        start: dt.datetime | None = None,
        eclipse_types: str = "both",
    ) -> "ReportBuilder":
        """
        Add eclipses table.

        Shows solar and lunar eclipses within a date range.
        Useful for eclipse calendars and transit planning.

        Args:
            end: End date for eclipse search (required)
            start: Start date for eclipse search (optional, defaults to chart date)
            eclipse_types: Which types to include ("both", "solar", "lunar")

        Returns:
            Self for chaining

        Example:
            >>> # Eclipses for the next 2 years from chart date
            >>> from datetime import datetime, timedelta
            >>> chart_date = chart.datetime.utc_datetime
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_eclipses(end=chart_date + timedelta(days=730))
            ...     .render())
            >>>
            >>> # Only solar eclipses in a specific range
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .with_eclipses(
            ...         start=datetime(2025, 1, 1),
            ...         end=datetime(2025, 12, 31),
            ...         eclipse_types="solar"
            ...     )
            ...     .render())
        """
        # Use chart date as start if not provided
        if start is None:
            if self._chart is None:
                raise ValueError(
                    "Must call from_chart() before with_eclipses() when start is not provided"
                )
            if isinstance(self._chart, Comparison):
                start = self._chart.chart1.datetime.utc_datetime
            else:
                start = self._chart.datetime.utc_datetime

        self._sections.append(
            EclipseSection(
                start=start,
                end=end,
                eclipse_types=eclipse_types,
            )
        )
        return self

    # -------------------------------------------------------------------------
    # Preset Methods
    # -------------------------------------------------------------------------
    # Convenience methods that bundle multiple sections into common configurations.

    def preset_minimal(self) -> "ReportBuilder":
        """
        Minimal preset: Just the basics.

        Includes:
        - Chart overview (name, date, location)
        - Planet positions

        Returns:
            Self for chaining

        Example:
            >>> report = ReportBuilder().from_chart(chart).preset_minimal().render()
        """
        return self.with_chart_overview().with_planet_positions()

    def preset_standard(self) -> "ReportBuilder":
        """
        Standard preset: Common report sections for everyday use.

        Includes:
        - Chart overview
        - Planet positions (with house placements)
        - Major aspects (sorted by orb)
        - House cusps

        Returns:
            Self for chaining

        Example:
            >>> report = ReportBuilder().from_chart(chart).preset_standard().render()
        """
        return (
            self.with_chart_overview()
            .with_planet_positions(include_house=True)
            .with_aspects(mode="major")
            .with_house_cusps()
        )

    def preset_detailed(self) -> "ReportBuilder":
        """
        Detailed preset: Comprehensive report with all major sections.

        Includes:
        - Chart overview
        - Moon phase
        - Planet positions (with speed and all house systems)
        - Declinations
        - All aspects (sorted by orb)
        - House cusps
        - Essential dignities

        Returns:
            Self for chaining

        Example:
            >>> report = ReportBuilder().from_chart(chart).preset_detailed().render()
        """
        return (
            self.with_chart_overview()
            .with_moon_phase()
            .with_planet_positions(include_speed=True, include_house=True)
            .with_declinations()
            .with_aspects(mode="all")
            .with_house_cusps()
            .with_dignities()
        )

    def preset_full(self) -> "ReportBuilder":
        """
        Full preset: Everything available.

        Includes all sections for maximum detail:
        - Chart overview
        - Moon phase
        - Planet positions (with speed and all house systems)
        - Declinations
        - All aspects
        - Aspect patterns (Grand Trines, T-Squares, etc.)
        - House cusps
        - Essential dignities
        - Midpoints and midpoint aspects
        - Fixed stars
        - Zodiacal Releasing (Part of Fortune and Part of Spirit)

        Note: Some sections require specific components to be added during
        chart calculation (e.g., DignityComponent, AspectPatternAnalyzer,
        MidpointCalculator, FixedStarsComponent, ZodiacalReleasingAnalyzer).
        Missing components show helpful messages rather than errors.

        Returns:
            Self for chaining

        Example:
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_aspects()
            ...     .add_component(DignityComponent())
            ...     .add_component(AspectPatternAnalyzer())
            ...     .add_component(MidpointCalculator())
            ...     .add_component(FixedStarsComponent())
            ...     .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
            ...     .calculate())
            >>> report = ReportBuilder().from_chart(chart).preset_full().render()
        """
        return (
            self.with_chart_overview()
            .with_moon_phase()
            .with_planet_positions(include_speed=True, include_house=True)
            .with_house_cusps()
            .with_aspects(mode="all")
            .with_aspect_patterns()
            .with_dignities(show_details=True)
            .with_dispositors()
            .with_declinations()
            .with_declination_aspects()
            .with_midpoints()
            .with_midpoint_aspects()
            .with_fixed_stars()
            .with_zodiacal_releasing(
                lots=["Part of Fortune", "Part of Spirit"],
                mode="both",
            )
        )

    def preset_positions_only(self) -> "ReportBuilder":
        """
        Positions-only preset: Focus on planetary placements.

        Includes:
        - Chart overview
        - Planet positions (with speed and house placements)
        - Declinations
        - House cusps

        No aspects or interpretive sections.

        Returns:
            Self for chaining

        Example:
            >>> report = ReportBuilder().from_chart(chart).preset_positions_only().render()
        """
        return (
            self.with_chart_overview()
            .with_planet_positions(include_speed=True, include_house=True)
            .with_declinations()
            .with_house_cusps()
        )

    def preset_aspects_only(self) -> "ReportBuilder":
        """
        Aspects-only preset: Focus on planetary relationships.

        Includes:
        - Chart overview
        - All aspects (with orbs)
        - Aspect patterns (Grand Trines, T-Squares, etc.)

        Returns:
            Self for chaining

        Note: Aspect patterns require AspectPatternAnalyzer component.

        Example:
            >>> report = ReportBuilder().from_chart(chart).preset_aspects_only().render()
        """
        return (
            self.with_chart_overview()
            .with_aspects(mode="all", orbs=True)
            .with_aspect_patterns()
        )

    def preset_synastry(self) -> "ReportBuilder":
        """
        Synastry preset: Optimized for relationship comparison charts.

        Designed for Comparison objects, this preset shows:
        - Chart overview (displays both charts' info)
        - Planet positions (side-by-side tables for each chart)
        - Cross-chart aspects (with chart labels)
        - House cusps (side-by-side tables for each chart)

        Returns:
            Self for chaining

        Example:
            >>> comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()
            >>> report = ReportBuilder().from_chart(comparison).preset_synastry().render()
        """
        return (
            self.with_chart_overview()
            .with_planet_positions(include_house=True)
            .with_cross_aspects(mode="major")
            .with_house_cusps()
        )

    def preset_transit(self) -> "ReportBuilder":
        """
        Transit preset: Optimized for transit comparison charts.

        Shows natal chart positions alongside transit positions,
        with cross-chart aspects showing transiting planets'
        aspects to natal positions.

        Includes:
        - Chart overview
        - Planet positions (side-by-side: natal vs transit)
        - Cross-chart aspects (all aspects, tight orbs)
        - House cusps (side-by-side)

        Returns:
            Self for chaining

        Example:
            >>> transit = ComparisonBuilder.transit(natal, transit_time).calculate()
            >>> report = ReportBuilder().from_chart(transit).preset_transit().render()
        """
        return (
            self.with_chart_overview()
            .with_planet_positions(include_house=True)
            .with_cross_aspects(mode="all")
            .with_house_cusps()
        )

    def preset_transit_calendar(
        self,
        end: dt.datetime,
        start: dt.datetime | None = None,
        include_minor_planets: bool = False,
    ) -> "ReportBuilder":
        """
        Transit calendar preset: Sky events over a date range.

        Bundles all three transit calendar sections showing what's
        happening in the sky between two dates. Useful for planning
        around retrogrades, sign changes, and eclipses.

        Includes:
        - Planetary stations (retrograde/direct)
        - Sign ingresses (planets changing signs)
        - Eclipses (solar and lunar)

        Args:
            end: End date for the calendar (required)
            start: Start date (optional, defaults to chart date)
            include_minor_planets: Include Chiron in stations/ingresses (default: False)

        Returns:
            Self for chaining

        Example:
            >>> # Transit calendar for the next year from chart date
            >>> from datetime import timedelta
            >>> chart_date = chart.datetime.utc_datetime
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .preset_transit_calendar(end=chart_date + timedelta(days=365))
            ...     .render())
            >>>
            >>> # Specific date range
            >>> from datetime import datetime
            >>> report = (ReportBuilder()
            ...     .from_chart(chart)
            ...     .preset_transit_calendar(
            ...         start=datetime(2025, 1, 1),
            ...         end=datetime(2025, 12, 31)
            ...     )
            ...     .render())

        Note:
            This preset does NOT include natal chart information - it's purely
            about sky events. For transits TO your natal chart, use
            ComparisonBuilder.transit() with preset_transit() instead.
        """
        return (
            self.with_stations(
                end=end, start=start, include_minor=include_minor_planets
            )
            .with_ingresses(end=end, start=start, include_minor=include_minor_planets)
            .with_eclipses(end=end, start=start)
        )

    # -------------------------------------------------------------------------
    # Rendering Methods
    # -------------------------------------------------------------------------
    def render(
        self,
        format: str = "rich_table",
        file: str | None = None,
        show: bool | None = None,
    ) -> str | None:
        """
        Render the report with flexible output options.

        Args:
            format: Output format ("rich_table", "plain_table", "text", "prose", "pdf", "html")
            file: Optional filename to save to
            show: Whether to display in terminal. Defaults to True for terminal
                  formats (rich_table, plain_table, text, prose) and False for file
                  formats (pdf, html).

        Returns:
            Filename if saved to file, None otherwise

        Raises:
            ValueError: If no chart has been set
            ValueError: If unknown format specified

        Examples:
            # Show in terminal with Rich formatting
            report.render()

            # Save to file (with terminal preview)
            report.render(format="plain_table", file="chart.txt")

            # Save quietly (no terminal output)
            report.render(format="plain_table", file="chart.txt", show=False)

            # Generate PDF with chart image and title (configured via builder)
            report.with_chart_image().with_title("My Report").render(
                format="pdf", file="report.pdf"
            )
        """
        if not self._chart:
            raise ValueError("No chart set. Call .from_chart(chart) before rendering.")

        # Terminal-friendly formats
        terminal_formats = {"rich_table", "plain_table", "text", "prose"}

        # Default show behavior: True for terminal formats, False for file formats
        if show is None:
            show = format in terminal_formats

        # Resolve chart image path (auto-generate if requested)
        chart_svg_path = self._resolve_chart_image_path(file)

        # Resolve title (use instance var or generate default)
        title = self._title

        # Generate section data once
        section_data = [
            (section.section_name, section.generate_data(self._chart))
            for section in self._sections
        ]

        # Show in terminal if requested and format supports it
        if show and format in terminal_formats:
            self._print_to_console(section_data, format)

        # Save to file if requested
        if file:
            # Handle PDF format (binary output via Typst)
            if format == "pdf":
                content = self._to_typst_pdf(section_data, chart_svg_path, title)
                with open(file, "wb") as f:
                    f.write(content)
            else:
                content = self._to_string(section_data, format, chart_svg_path)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
            return file

        return None

    def _resolve_chart_image_path(self, output_file: str | None) -> str | None:
        """
        Resolve the chart image path for rendering.

        If a path was explicitly set via with_chart_image(path), use that.
        If auto-generate was requested via with_chart_image(), generate a temp SVG.
        Otherwise return None.

        Args:
            output_file: The output file path (used to determine temp file location)

        Returns:
            Path to chart SVG file, or None
        """
        import os
        import tempfile

        # Explicit path provided
        if self._chart_image_path:
            return self._chart_image_path

        # Auto-generate requested
        if self._auto_generate_chart_image and self._chart:
            # Generate temp file path based on output file or use system temp
            if output_file:
                base_dir = os.path.dirname(os.path.abspath(output_file))
                base_name = os.path.splitext(os.path.basename(output_file))[0]
                svg_path = os.path.join(base_dir, f"{base_name}_chart.svg")
            else:
                # Use temp directory
                fd, svg_path = tempfile.mkstemp(suffix=".svg", prefix="stellium_chart_")
                os.close(fd)

            # Generate the chart
            self._chart.draw(svg_path).preset_standard().save()
            return svg_path

        return None

    def _to_string(
        self,
        section_data: list[tuple[str, dict[str, Any]]],
        format: str,
        chart_svg_path: str | None = None,
    ) -> str:
        """
        Convert report to plaintext string (internal helper).

        Used for file saving and testing. Always returns text without ANSI codes.

        Args:
            section_data: List of (section_name, section_dict) tuples
            format: Output format
            chart_svg_path: Optional path to chart SVG (for HTML format)

        Returns:
            Plaintext string representation
        """
        # Map format names to renderer methods
        if format in ("rich_table", "plain_table", "text"):
            # For terminal formats, use PlainTextRenderer for file output
            # (or use RichTableRenderer.render_report which strips ANSI)
            if format == "rich_table":
                # Use Rich renderer's string method (strips ANSI)
                renderer = RichTableRenderer()
                return renderer.render_report(section_data)
            else:
                # Use plain text renderer
                renderer = PlainTextRenderer()
                return renderer.render_report(section_data)
        elif format == "prose":
            # Natural language prose (for pasting into conversations)
            from stellium.presentation.renderers import ProseRenderer

            renderer = ProseRenderer()
            return renderer.render_report(section_data)
        elif format == "html":
            # HTML renderer
            from stellium.presentation.renderers import HTMLRenderer

            renderer = HTMLRenderer()

            # Load SVG if path provided
            svg_content = None
            if chart_svg_path:
                try:
                    with open(chart_svg_path) as f:
                        svg_content = f.read()
                except Exception:
                    pass  # Silently skip if can't load

            return renderer.render_report(section_data, svg_content)
        else:
            available = "rich_table, plain_table, text, prose, pdf, html, typst"
            raise ValueError(f"Unknown format '{format}'. Available: {available}")

    def _to_typst_pdf(
        self,
        section_data: list[tuple[str, dict[str, Any]]],
        chart_svg_path: str | None = None,
        title: str | None = None,
    ) -> bytes:
        """
        Convert report to PDF bytes using Typst (internal helper).

        Typst produces beautiful, professional-quality PDFs with proper
        typography, kerning, and hyphenation.

        Args:
            section_data: List of (section_name, section_dict) tuples
            chart_svg_path: Optional path to chart SVG to embed
            title: Optional report title (uses chart's name if not provided)

        Returns:
            PDF as bytes
        """
        from stellium.presentation.renderers import TypstRenderer

        # Build title from chart name if not provided
        if title is None and self._chart:
            chart_name = self._chart.metadata.get("name")
            if chart_name:
                title = f"{chart_name} — Natal Chart"  # em dash
            else:
                title = "Natal Chart Report"

        renderer = TypstRenderer()
        return renderer.render_report(
            section_data,
            chart_svg_path=chart_svg_path,
            title=title or "Astrological Report",
        )

    def _print_to_console(
        self, section_data: list[tuple[str, dict[str, Any]]], format: str
    ) -> None:
        """
        Print report directly to console (internal helper).

        Args:
            section_data: List of (section_name, section_dict) tuples
            format: Output format (must be terminal-friendly)
        """
        if format == "rich_table":
            # Use Rich renderer's print method (preserves ANSI formatting)
            renderer = RichTableRenderer()
            renderer.print_report(section_data)
        elif format in ("plain_table", "text"):
            # Use plain text renderer and print the result
            renderer = PlainTextRenderer()
            output = renderer.render_report(section_data)
            print(output)
        elif format == "prose":
            # Natural language prose output
            from stellium.presentation.renderers import ProseRenderer

            renderer = ProseRenderer()
            output = renderer.render_report(section_data)
            print(output)
        else:
            raise ValueError(
                f"Format '{format}' is not terminal-friendly. "
                f"Use 'rich_table', 'plain_table', 'text', or 'prose'."
            )

    def _get_renderer(self, format: str) -> ReportRenderer:
        """
        Get the appropriate renderer for the format.

        Why a factory method?
        - Centralizes renderer selection logic
        - Easy to add new renderers
        - Can implement caching if needed

        Args:
            format: Renderer name

        Returns:
            Renderer instance

        Raises:
            ValueError: If format is unknown
        """
        renderers = {
            "rich_table": RichTableRenderer(),
            "plaintext": PlainTextRenderer(),
            # Future: "html": HTMLRenderer(),
            # Future: "markdown": MarkdownRenderer(),
        }

        if format not in renderers:
            available = ", ".join(renderers.keys())
            raise ValueError(f"Unknown format '{format}'. Available: {available}")

        return renderers[format]
