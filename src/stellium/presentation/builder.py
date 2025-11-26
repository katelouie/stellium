"""
Report builder for creating chart reports.

The builder pattern allows users to progressively construct reports
by adding sections one at a time, then rendering in their chosen format.
"""

from typing import Any

from stellium.core.models import CalculatedChart
from stellium.core.protocols import ReportRenderer, ReportSection

from .renderers import PlainTextRenderer, RichTableRenderer
from .sections import (
    AspectPatternSection,
    AspectSection,
    ChartOverviewSection,
    DignitySection,
    HouseCuspsSection,
    MidpointSection,
    MoonPhaseSection,
    PlanetPositionSection,
)


class ReportBuilder:
    """
    Builder for chart reports.

    Usage:
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
        self._chart: CalculatedChart | None = None
        self._sections: list[ReportSection] = []

    def from_chart(self, chart: CalculatedChart) -> "ReportBuilder":
        """
        Set the chart to generate reports from.

        Args:
            chart: A CalculatedChart from ChartBuilder

        Returns:
            Self for chaining
        """
        self._chart = chart
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
    ) -> "ReportBuilder":
        """
        Add aspects table.

        Args:
            mode: "all", "major", "minor", or "harmonic"
            orb_display: Show orb column
            sort_by: How to sort aspects

        Returns:
            Self for chaining
        """
        self._sections.append(
            AspectSection(
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

    def with_section(self, section: ReportSection) -> "ReportBuilder":
        """
        Add a custom section.

        This allows users to extend the report system with their own sections.

        Args:
            section: Any object implementing the ReportSection protocol

        Returns:
            Self for chaining

        Example:
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

    # -------------------------------------------------------------------------
    # Rendering Methods
    # -------------------------------------------------------------------------
    def render(
        self,
        format: str = "rich_table",
        file: str | None = None,
        show: bool = True,
        chart_svg_path: str | None = None,
        title: str | None = None,
    ) -> str | None:
        """
        Render the report with flexible output options.

        Args:
            format: Output format ("rich_table", "plain_table", "text", "pdf", "html", "typst")
            file: Optional filename to save to
            show: Whether to display in terminal (default True, ignored for pdf/html/typst)
            chart_svg_path: Optional path to chart SVG file (for pdf/html/typst formats)
            title: Optional report title (for typst format)

        Returns:
            Filename if saved to file, None otherwise

        Raises:
            ValueError: If no chart has been set
            ValueError: If unknown format specified

        Examples:
            # Show in terminal with Rich formatting
            report.render(format="rich_table")

            # Save to file (with terminal preview)
            report.render(format="plain_table", file="chart.txt")

            # Save quietly (no terminal output)
            report.render(format="plain_table", file="chart.txt", show=False)

            # Generate PDF with embedded chart (WeasyPrint)
            report.render(format="pdf", file="report.pdf", chart_svg_path="chart.svg")

            # Generate beautiful PDF with Typst (recommended!)
            report.render(format="typst", file="report.pdf", chart_svg_path="chart.svg")

            # Generate HTML
            report.render(format="html", file="report.html", chart_svg_path="chart.svg")
        """
        if not self._chart:
            raise ValueError("No chart set. Call .from_chart(chart) before rendering.")

        # Generate section data once
        section_data = [
            (section.section_name, section.generate_data(self._chart))
            for section in self._sections
        ]

        # Terminal-friendly formats
        terminal_formats = {"rich_table", "plain_table", "text"}

        # Show in terminal if requested and format supports it
        if show and format in terminal_formats:
            self._print_to_console(section_data, format)

        # Save to file if requested
        if file:
            # Handle PDF formats (binary output)
            if format == "pdf":
                content = self._to_pdf(section_data, chart_svg_path)
                with open(file, "wb") as f:
                    f.write(content)
            elif format == "typst":
                content = self._to_typst_pdf(section_data, chart_svg_path, title)
                with open(file, "wb") as f:
                    f.write(content)
            else:
                content = self._to_string(section_data, format, chart_svg_path)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
            return file

        return None

    def _to_string(
        self, section_data: list[tuple[str, dict[str, Any]]], format: str,
        chart_svg_path: str | None = None
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
        elif format == "html":
            # HTML renderer
            from stellium.presentation.renderers import HTMLRenderer
            renderer = HTMLRenderer()

            # Load SVG if path provided
            svg_content = None
            if chart_svg_path:
                try:
                    with open(chart_svg_path, "r") as f:
                        svg_content = f.read()
                except Exception:
                    pass  # Silently skip if can't load

            return renderer.render_report(section_data, svg_content)
        else:
            available = "rich_table, plain_table, text, pdf, html, typst"
            raise ValueError(f"Unknown format '{format}'. Available: {available}")

    def _to_pdf(
        self, section_data: list[tuple[str, dict[str, Any]]],
        chart_svg_path: str | None = None
    ) -> bytes:
        """
        Convert report to PDF bytes using WeasyPrint (internal helper).

        Args:
            section_data: List of (section_name, section_dict) tuples
            chart_svg_path: Optional path to chart SVG to embed

        Returns:
            PDF as bytes
        """
        from stellium.presentation.renderers import PDFRenderer
        renderer = PDFRenderer()
        return renderer.render_report(section_data, chart_svg_path=chart_svg_path)

    def _to_typst_pdf(
        self, section_data: list[tuple[str, dict[str, Any]]],
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
        else:
            raise ValueError(
                f"Format '{format}' is not terminal-friendly. "
                f"Use 'rich_table', 'plain_table', or 'text'."
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
