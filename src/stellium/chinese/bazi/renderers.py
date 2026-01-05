"""Renderers for Bazi (Four Pillars) charts.

This module provides different output formats for Bazi charts:
- BaziRichRenderer: Beautiful terminal output using Rich library
- BaziSVGRenderer: Visual SVG chart rendering
- BaziProseRenderer: Natural language prose output
"""

from typing import TYPE_CHECKING, Any

from stellium.chinese.core import Element

if TYPE_CHECKING:
    from stellium.chinese.bazi.models import BaZiChart

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Element colors for Rich output
ELEMENT_COLORS = {
    Element.WOOD: "green",
    Element.FIRE: "red",
    Element.EARTH: "yellow",
    Element.METAL: "white",
    Element.WATER: "blue",
}


class BaziRichRenderer:
    """Render Bazi charts using Rich library for beautiful terminal output.

    Requires: pip install rich

    Example:
        >>> from stellium.chinese.bazi import BaZiEngine
        >>> from stellium.chinese.bazi.renderers import BaziRichRenderer
        >>> from datetime import datetime
        >>>
        >>> engine = BaZiEngine(timezone_offset_hours=-8)
        >>> chart = engine.calculate(datetime(1994, 1, 6, 11, 47))
        >>>
        >>> renderer = BaziRichRenderer()
        >>> renderer.print_chart(chart)  # Prints to terminal
    """

    def __init__(self) -> None:
        """Initialize Rich renderer."""
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library not available. Install with: pip install rich"
            )
        self.console = Console(record=True)

    def print_chart(
        self,
        chart: "BaZiChart",
        show_hidden_stems: bool = True,
        show_ten_gods: bool = True,
        show_summary: bool = True,
    ) -> None:
        """Print Bazi chart to terminal with Rich formatting.

        Args:
            chart: The BaZiChart to render
            show_hidden_stems: Whether to show hidden stems in branches
            show_ten_gods: Whether to show Ten Gods relationships
            show_summary: Whether to show element/polarity summary
        """
        console = Console()

        # Title
        console.print()
        console.print(
            Panel(
                f"[bold]八字 Bazi Chart[/bold]\n{chart.birth_datetime.strftime('%Y-%m-%d %H:%M')}",
                style="cyan",
                expand=False,
            )
        )

        # Main pillars table
        table = self._create_pillars_table(chart, show_hidden_stems, show_ten_gods)
        console.print(table)

        # Summary panel
        if show_summary:
            self._print_summary(console, chart)

    def render_chart(
        self,
        chart: "BaZiChart",
        show_hidden_stems: bool = True,
        show_ten_gods: bool = True,
        show_summary: bool = True,
    ) -> str:
        """Render Bazi chart to string (for file output).

        Returns plain text with ANSI codes stripped.
        """
        # Create fresh console for recording
        console = Console(record=True)

        # Title
        console.print()
        console.print("八字 Bazi Chart")
        console.print(f"{chart.birth_datetime.strftime('%Y-%m-%d %H:%M')}")
        console.print()

        # Main pillars table
        table = self._create_pillars_table(chart, show_hidden_stems, show_ten_gods)
        console.print(table)

        # Summary
        if show_summary:
            self._print_summary(console, chart)

        return console.export_text()

    def _create_pillars_table(
        self,
        chart: "BaZiChart",
        show_hidden_stems: bool,
        show_ten_gods: bool,
    ) -> Table:
        """Create the main pillars table."""
        from stellium.chinese.bazi.analysis import calculate_ten_god

        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            title="Four Pillars (四柱)",
            title_style="bold cyan",
        )

        # Pillar labels for columns
        pillar_names = ["Year", "Month", "Day", "Hour"]
        pillar_hanzi = ["年", "月", "日", "时"]

        # Add columns dynamically
        table.add_column("", style="dim")  # Row labels
        for eng, chn in zip(pillar_names, pillar_hanzi, strict=True):
            # Day pillar gets bold style since it contains the Day Master
            style = "bold" if eng == "Day" else None
            table.add_column(f"{eng} ({chn})", justify="center", style=style)

        # Ten Gods row
        if show_ten_gods:
            gods_row = ["十神"]
            for pillar in chart.pillars:
                god = calculate_ten_god(chart.day_master, pillar.stem)
                gods_row.append(f"{god.hanzi}")
            table.add_row(*gods_row, style="cyan")

        # Stems row
        stems_row = ["天干"]
        for pillar in chart.pillars:
            stem = pillar.stem
            color = ELEMENT_COLORS.get(stem.element, "white")
            stems_row.append(f"[{color}]{stem.hanzi}[/{color}] {stem.element.hanzi}")
        table.add_row(*stems_row)

        # Branches row
        branches_row = ["地支"]
        for pillar in chart.pillars:
            branch = pillar.branch
            color = ELEMENT_COLORS.get(branch.element, "white")
            branches_row.append(f"[{color}]{branch.hanzi}[/{color}] {branch.animal}")
        table.add_row(*branches_row)

        # Hidden stems rows
        if show_hidden_stems:
            max_hidden = max(len(p.hidden_stems) for p in chart.pillars)
            hidden_labels = ["藏干(本)", "藏干(中)", "藏干(余)"]

            for i in range(max_hidden):
                row_label = (
                    hidden_labels[i] if i < len(hidden_labels) else f"藏干({i+1})"
                )
                hidden_row = [row_label]

                for pillar in chart.pillars:
                    if i < len(pillar.hidden_stems):
                        hs = pillar.hidden_stems[i]
                        god = calculate_ten_god(chart.day_master, hs)
                        color = ELEMENT_COLORS.get(hs.element, "white")
                        hidden_row.append(
                            f"[{color}]{hs.hanzi}[/{color}]{god.hanzi[:1]}"
                        )
                    else:
                        hidden_row.append("")

                table.add_row(*hidden_row, style="dim")

        return table

    def _print_summary(self, console: Console, chart: "BaZiChart") -> None:
        """Print summary information below the chart."""
        from stellium.chinese.bazi.analysis import (
            analyze_ten_gods,
            count_ten_god_categories,
        )

        console.print()

        # Day Master info
        dm = chart.day_master
        dm_color = ELEMENT_COLORS.get(dm.element, "white")
        console.print(
            f"Day Master (日主): [{dm_color}]{dm.hanzi}[/{dm_color}] "
            f"({dm.element.english} {dm.polarity.value})"
        )
        console.print(f"Eight Characters: {chart.hanzi}")

        # Element counts
        console.print()
        console.print("[bold]Element Balance (including hidden stems):[/bold]")
        element_counts = chart.element_counts(include_hidden=True)
        elements_text = []
        for elem in Element:
            count = element_counts.get(elem, 0)
            color = ELEMENT_COLORS.get(elem, "white")
            elements_text.append(f"[{color}]{elem.hanzi}[/{color}]: {count}")
        console.print("  " + "  ".join(elements_text))

        # Ten Gods category counts
        relations = analyze_ten_gods(chart, include_hidden=True)
        categories = count_ten_god_categories(relations)
        console.print()
        console.print("[bold]Ten Gods Categories:[/bold]")
        cat_text = []
        for cat in ["Self", "Companion", "Output", "Wealth", "Power", "Resource"]:
            count = categories.get(cat, 0)
            cat_text.append(f"{cat}: {count}")
        console.print("  " + "  ".join(cat_text))


class BaziProseRenderer:
    """Render Bazi charts as natural language prose.

    Designed for pasting into conversations or documents.

    Example:
        >>> renderer = BaziProseRenderer()
        >>> prose = renderer.render(chart)
        >>> print(prose)
    """

    def __init__(self, bullet: str = "•") -> None:
        """Initialize prose renderer.

        Args:
            bullet: Character to use for list items
        """
        self.bullet = bullet

    def render(
        self,
        chart: "BaZiChart",
        include_hidden_stems: bool = True,
        include_ten_gods: bool = True,
    ) -> str:
        """Render chart as prose text.

        Args:
            chart: The BaZiChart to render
            include_hidden_stems: Include hidden stem analysis
            include_ten_gods: Include Ten Gods relationships

        Returns:
            Natural language description of the chart
        """
        from stellium.chinese.bazi.analysis import (
            analyze_ten_gods,
            count_ten_god_categories,
        )

        paragraphs = []

        # Opening with datetime and Day Master
        dm = chart.day_master
        opening = (
            f"Bazi chart for {chart.birth_datetime.strftime('%B %d, %Y at %I:%M %p')}. "
            f"The Day Master is {dm.hanzi} ({dm.pinyin}), "
            f"a {dm.polarity.value} {dm.element.english} person."
        )
        paragraphs.append(opening)

        # Eight Characters
        paragraphs.append(f"Eight Characters (八字): {chart.hanzi}")

        # Four Pillars breakdown
        pillar_names = ["Year", "Month", "Day", "Hour"]
        pillar_lines = ["The Four Pillars:"]
        for name, pillar in zip(pillar_names, chart.pillars, strict=False):
            pillar_lines.append(
                f"{self.bullet} {name}: {pillar.hanzi} "
                f"({pillar.stem.element.english} {pillar.branch.animal})"
            )
        paragraphs.append("\n".join(pillar_lines))

        # Ten Gods analysis
        if include_ten_gods:
            relations = analyze_ten_gods(chart, include_hidden=include_hidden_stems)
            main_relations = [r for r in relations if not r.is_hidden]

            gods_lines = ["Ten Gods (十神) in main stems:"]
            for r in main_relations:
                if r.pillar_name == "day":
                    gods_lines.append(
                        f"{self.bullet} {r.pillar_name.capitalize()}: {r.stem.hanzi} - Self (日主)"
                    )
                else:
                    gods_lines.append(
                        f"{self.bullet} {r.pillar_name.capitalize()}: {r.stem.hanzi} - "
                        f"{r.ten_god.english} ({r.ten_god.chinese})"
                    )
            paragraphs.append("\n".join(gods_lines))

            # Category summary
            categories = count_ten_god_categories(relations)
            cat_parts = [f"{cat}: {count}" for cat, count in sorted(categories.items())]
            paragraphs.append("Ten Gods category distribution: " + ", ".join(cat_parts))

        # Element balance
        element_counts = chart.element_counts(include_hidden=include_hidden_stems)
        elem_parts = [
            f"{elem.english}: {count}" for elem, count in element_counts.items()
        ]
        paragraphs.append("Element balance: " + ", ".join(elem_parts))

        return "\n\n".join(paragraphs)


class BaziSVGRenderer:
    """Render Bazi charts as SVG images.

    Creates a visual representation of the Four Pillars with:
    - Color-coded elements
    - Hidden stems shown below main characters
    - Ten Gods labels
    - Element balance visualization

    Example:
        >>> renderer = BaziSVGRenderer()
        >>> svg_content = renderer.render(chart)
        >>> with open("chart.svg", "w") as f:
        ...     f.write(svg_content)
    """

    # Colors matching Chinese element associations
    ELEMENT_COLORS = {
        Element.WOOD: "#4caf50",  # Green
        Element.FIRE: "#f44336",  # Red
        Element.EARTH: "#795548",  # Brown
        Element.METAL: "#9e9e9e",  # Gray/Silver
        Element.WATER: "#2196f3",  # Blue
    }

    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        font_family: str = "Noto Sans SC, SimSun, Microsoft YaHei, sans-serif",
    ) -> None:
        """Initialize SVG renderer.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
            font_family: CSS font-family for Chinese characters
        """
        self.width = width
        self.height = height
        self.font_family = font_family

    def render(
        self,
        chart: "BaZiChart",
        show_hidden_stems: bool = True,
        show_ten_gods: bool = True,
        title: str | None = None,
    ) -> str:
        """Render chart as SVG string.

        Args:
            chart: The BaZiChart to render
            show_hidden_stems: Show hidden stems row
            show_ten_gods: Show Ten Gods labels
            title: Optional title (defaults to birth datetime)

        Returns:
            SVG content as string
        """
        from stellium.chinese.bazi.analysis import calculate_ten_god

        # Layout constants
        col_width = self.width / 4
        header_height = 50
        row_height = 45
        padding = 20

        # Calculate total height needed
        num_rows = 2  # stems + branches
        if show_ten_gods:
            num_rows += 1
        if show_hidden_stems:
            max_hidden = max(len(p.hidden_stems) for p in chart.pillars)
            num_rows += max_hidden

        total_height = (
            header_height + (num_rows * row_height) + padding * 2 + 60
        )  # extra for title

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{total_height}" '
            f'viewBox="0 0 {self.width} {total_height}">',
            "<style>",
            f"  .title {{ font-family: {self.font_family}; font-size: 18px; font-weight: bold; }}",
            f"  .header {{ font-family: {self.font_family}; font-size: 14px; fill: #666; }}",
            f"  .hanzi {{ font-family: {self.font_family}; font-size: 24px; font-weight: bold; }}",
            f"  .label {{ font-family: {self.font_family}; font-size: 12px; fill: #888; }}",
            f"  .god {{ font-family: {self.font_family}; font-size: 14px; fill: #666; }}",
            f"  .hidden {{ font-family: {self.font_family}; font-size: 16px; }}",
            "</style>",
            '<rect width="100%" height="100%" fill="#fafafa"/>',
        ]

        # Title
        title_text = (
            title or f"Bazi Chart - {chart.birth_datetime.strftime('%Y-%m-%d %H:%M')}"
        )
        svg_parts.append(
            f'<text x="{self.width/2}" y="30" text-anchor="middle" class="title">{title_text}</text>'
        )

        # Column headers
        pillar_labels = [
            ("Year", "年柱"),
            ("Month", "月柱"),
            ("Day", "日柱"),
            ("Hour", "时柱"),
        ]
        y_start = 60

        for i, (eng, chn) in enumerate(pillar_labels):
            x = col_width * i + col_width / 2
            svg_parts.append(
                f'<text x="{x}" y="{y_start}" text-anchor="middle" class="header">{eng}</text>'
            )
            svg_parts.append(
                f'<text x="{x}" y="{y_start + 16}" text-anchor="middle" class="header">{chn}</text>'
            )

        current_y = y_start + header_height - 20

        # Ten Gods row
        if show_ten_gods:
            for i, pillar in enumerate(chart.pillars):
                god = calculate_ten_god(chart.day_master, pillar.stem)
                x = col_width * i + col_width / 2
                svg_parts.append(
                    f'<text x="{x}" y="{current_y}" text-anchor="middle" class="god">{god.hanzi}</text>'
                )
            current_y += row_height

        # Stems row
        for i, pillar in enumerate(chart.pillars):
            x = col_width * i + col_width / 2
            color = self.ELEMENT_COLORS.get(pillar.stem.element, "#333")
            svg_parts.append(
                f'<text x="{x}" y="{current_y}" text-anchor="middle" class="hanzi" fill="{color}">'
                f"{pillar.stem.hanzi}</text>"
            )
            # Element label
            svg_parts.append(
                f'<text x="{x + 20}" y="{current_y}" text-anchor="start" class="label">'
                f"{pillar.stem.element.hanzi}</text>"
            )
        current_y += row_height

        # Branches row
        for i, pillar in enumerate(chart.pillars):
            x = col_width * i + col_width / 2
            color = self.ELEMENT_COLORS.get(pillar.branch.element, "#333")
            svg_parts.append(
                f'<text x="{x}" y="{current_y}" text-anchor="middle" class="hanzi" fill="{color}">'
                f"{pillar.branch.hanzi}</text>"
            )
            # Animal label
            svg_parts.append(
                f'<text x="{x + 20}" y="{current_y}" text-anchor="start" class="label">'
                f"{pillar.branch.animal}</text>"
            )
        current_y += row_height

        # Hidden stems rows
        if show_hidden_stems:
            max_hidden = max(len(p.hidden_stems) for p in chart.pillars)
            for row_idx in range(max_hidden):
                for i, pillar in enumerate(chart.pillars):
                    if row_idx < len(pillar.hidden_stems):
                        hs = pillar.hidden_stems[row_idx]
                        x = col_width * i + col_width / 2
                        color = self.ELEMENT_COLORS.get(hs.element, "#333")
                        god = calculate_ten_god(chart.day_master, hs)
                        svg_parts.append(
                            f'<text x="{x}" y="{current_y}" text-anchor="middle" class="hidden" fill="{color}">'
                            f"{hs.hanzi}{god.hanzi[:1]}</text>"
                        )
                current_y += row_height - 10

        # Day Master summary at bottom
        dm = chart.day_master
        dm_color = self.ELEMENT_COLORS.get(dm.element, "#333")
        summary_y = current_y + 20
        svg_parts.append(
            f'<text x="{self.width/2}" y="{summary_y}" text-anchor="middle" class="label">'
            f'Day Master: <tspan fill="{dm_color}" font-weight="bold">{dm.hanzi}</tspan> '
            f"({dm.element.english} {dm.polarity.value}) | "
            f"八字: {chart.hanzi}</text>"
        )

        svg_parts.append("</svg>")

        return "\n".join(svg_parts)

    def render_to_file(
        self,
        chart: "BaZiChart",
        filepath: str,
        **kwargs: Any,
    ) -> None:
        """Render chart and save to file.

        Args:
            chart: The BaZiChart to render
            filepath: Output file path (should end in .svg)
            **kwargs: Additional arguments passed to render()
        """
        svg_content = self.render(chart, **kwargs)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
