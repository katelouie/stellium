"""
Output renderers for reports.

Renderers take structured data from sections and format it for different
output mediums (terminal with Rich, plain text, PDF, HTML, etc.).
"""

from typing import Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichTableRenderer:
    """
    Renderer using the Rich library for beautiful terminal output.

    Requires: pip install rich

    Features:
    - Colored tables with borders
    - Automatic column width adjustment
    - Unicode box characters
    """

    def __init__(self) -> None:
        """Initialize Rich renderer."""
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library not available. Install with: pip install rich"
            )

        # Use record=True to properly capture styled output
        self.console = Console(record=True)

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section with Rich."""
        data_type = section_data.get("type")

        if data_type == "table":
            return self._render_table(section_name, section_data)
        elif data_type == "key_value":
            return self._render_key_value(section_name, section_data)
        elif data_type == "text":
            return self._render_text(section_name, section_data)
        elif data_type == "side_by_side_tables":
            return self._render_side_by_side_tables(section_name, section_data)
        else:
            return f"Unknown section type: {data_type}"

    def print_report(self, sections: list[tuple[str, dict[str, Any]]]) -> None:
        """
        Print report directly to terminal with Rich formatting.

        This method prints the report with full ANSI colors and styling,
        intended for immediate terminal display.
        """
        # Create a fresh console for direct printing (no recording)
        console = Console()

        for section_name, section_data in sections:
            # Print section header
            console.print(f"\n{section_name}", style="bold cyan")
            console.print("─" * len(section_name), style="cyan")

            # Print section content based on type
            data_type = section_data.get("type")

            if data_type == "table":
                self._print_table(console, section_data)
            elif data_type == "key_value":
                self._print_key_value(console, section_data)
            elif data_type == "text":
                console.print(section_data.get("text", ""))
            elif data_type == "side_by_side_tables":
                self._print_side_by_side_tables(console, section_data)
            else:
                console.print(f"Unknown section type: {data_type}")

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """
        Render complete report to plaintext string (ANSI codes stripped).

        Used for file output and testing.
        Returns clean text without ANSI escape codes.
        """
        output_parts = []

        for section_name, section_data in sections:
            # Render section header
            header = Text(f"\n{section_name}", style="bold cyan")
            output_parts.append(header)
            output_parts.append(Text("─" * len(section_name), style="cyan"))

            # Render section content
            content = self.render_section(section_name, section_data)
            output_parts.append(content)

        # Render all parts
        for part in output_parts:
            if isinstance(part, str):
                self.console.print(part)
            else:
                self.console.print(part)

        # Export as plain text (strips ANSI codes for file output)
        return self.console.export_text()

    def _render_table(self, section_name: str, data: dict[str, Any]) -> str:
        """Render table data with Rich."""
        table = Table(title=None, show_header=True, header_style="bold magenta")

        # Add columns
        for header in data["headers"]:
            table.add_column(header)

        # Add rows
        for row in data["rows"]:
            # Convert all values to strings
            str_row = [str(cell) for cell in row]
            table.add_row(*str_row)

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _render_key_value(self, section_name: str, data: dict[str, Any]) -> str:
        """Render key-value data."""
        output = []

        for key, value in data["data"].items():
            # Format: "Key: Value" with key in bold
            line = Text()
            line.append(f"{key}: ", style="bold")
            line.append(str(value))
            output.append(line)

        with self.console.capture() as capture:
            for line in output:
                self.console.print(line)

        return capture.get()

    def _render_text(self, section_name: str, data: dict[str, Any]) -> str:
        """Render plain text block."""
        return data.get("text", "")

    def _print_table(self, console: Console, data: dict[str, Any]) -> None:
        """Print table directly to console with Rich formatting."""
        table = Table(title=None, show_header=True, header_style="bold magenta")

        # Add columns
        for header in data["headers"]:
            table.add_column(header)

        # Add rows
        for row in data["rows"]:
            # Convert all values to strings
            str_row = [str(cell) for cell in row]
            table.add_row(*str_row)

        console.print(table)

    def _print_key_value(self, console: Console, data: dict[str, Any]) -> None:
        """Print key-value pairs directly to console with Rich formatting."""
        for key, value in data["data"].items():
            # Format: "Key: Value" with key in bold
            line = Text()
            line.append(f"{key}: ", style="bold")
            line.append(str(value))
            console.print(line)

    def _render_side_by_side_tables(
        self, section_name: str, data: dict[str, Any]
    ) -> str:
        """Render two tables side by side with Rich."""
        from rich.columns import Columns

        tables_data = data.get("tables", [])
        if not tables_data:
            return ""

        # Create Rich tables for each
        rich_tables = []
        for table_data in tables_data:
            table = Table(
                title=table_data.get("title"),
                show_header=True,
                header_style="bold magenta",
            )

            for header in table_data["headers"]:
                table.add_column(header)

            for row in table_data["rows"]:
                str_row = [str(cell) for cell in row]
                table.add_row(*str_row)

            rich_tables.append(table)

        # Use Columns to display side by side
        with self.console.capture() as capture:
            self.console.print(Columns(rich_tables, equal=True, expand=True))

        return capture.get()

    def _print_side_by_side_tables(
        self, console: Console, data: dict[str, Any]
    ) -> None:
        """Print two tables side by side directly to console."""
        from rich.columns import Columns

        tables_data = data.get("tables", [])
        if not tables_data:
            return

        # Create Rich tables for each
        rich_tables = []
        for table_data in tables_data:
            table = Table(
                title=table_data.get("title"),
                show_header=True,
                header_style="bold magenta",
            )

            for header in table_data["headers"]:
                table.add_column(header)

            for row in table_data["rows"]:
                str_row = [str(cell) for cell in row]
                table.add_row(*str_row)

            rich_tables.append(table)

        # Use Columns to display side by side
        console.print(Columns(rich_tables, equal=True, expand=True))


class PlainTextRenderer:
    """
    Plain text renderer with no dependencies.

    Creates simple ASCII tables and formatted text suitable for:
    - Log files
    - Email
    - Systems without Rich library
    - Piping to other tools
    """

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section as plain text."""
        data_type = section_data.get("type")

        if data_type == "table":
            return self._render_table(section_name, section_data)
        elif data_type == "key_value":
            return self._render_key_value(section_name, section_data)
        elif data_type == "text":
            return section_data.get("text", "")
        elif data_type == "side_by_side_tables":
            return self._render_side_by_side_tables(section_name, section_data)
        else:
            return f"Unknown section type: {data_type}"

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """Render complete report as plain text."""
        parts = []

        for section_name, section_data in sections:
            # Section header
            parts.append(f"\n{section_name}")
            parts.append("=" * len(section_name))

            # Section content
            content = self.render_section(section_name, section_data)
            parts.append(content)
            parts.append("")  # Blank line between sections

        return "\n".join(parts)

    def _render_table(self, section_name: str, data: dict[str, Any]) -> str:
        """
        Render ASCII table.

        Algorithm:
        1. Calculate column widths based on content
        2. Create header row with separators
        3. Create data rows
        4. Use | and - for borders
        """
        headers = data["headers"]
        rows = data["rows"]

        # Convert all cells to strings
        str_rows = [[str(cell) for cell in row] for row in rows]

        # Calculate column widths
        col_widths = []
        for i, header in enumerate(headers):
            # Start with header width
            width = len(header)

            # Check all row values
            for row in str_rows:
                if i < len(row):
                    width = max(width, len(row[i]))

            col_widths.append(width)

        # Build table
        lines = []

        # Header row
        header_cells = [h.ljust(w) for h, w in zip(headers, col_widths)]
        lines.append("| " + " | ".join(header_cells) + " |")

        # Separator
        separator_cells = ["-" * w for w in col_widths]
        lines.append("|-" + "-|-".join(separator_cells) + "-|")

        # Data rows
        for row in str_rows:
            # Pad row if needed
            padded_row = row + [""] * (len(headers) - len(row))

            row_cells = [cell.ljust(w) for cell, w in zip(padded_row, col_widths)]
            lines.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(lines)

    def _render_key_value(self, section_name: str, data: dict[str, Any]) -> str:
        """Render key-value pairs."""
        lines = []

        # Find longest key for alignment
        max_key_len = max(len(k) for k in data["data"].keys())

        for key, value in data["data"].items():
            # Right-align keys for neat columns
            lines.append(f"{key.rjust(max_key_len)}: {value}")

        return "\n".join(lines)

    def _render_side_by_side_tables(
        self, section_name: str, data: dict[str, Any]
    ) -> str:
        """
        Render two tables side by side in plain text.

        For plain text, we render tables vertically (one after the other)
        with clear titles, since true side-by-side is complex in ASCII.
        """
        tables_data = data.get("tables", [])
        if not tables_data:
            return ""

        output_parts = []
        for table_data in tables_data:
            # Add title if present
            title = table_data.get("title", "")
            if title:
                output_parts.append(f"\n{title}")
                output_parts.append("-" * len(title))

            # Render the table using existing method
            table_output = self._render_table(
                section_name,
                {"headers": table_data["headers"], "rows": table_data["rows"]},
            )
            output_parts.append(table_output)

        return "\n".join(output_parts)


class HTMLRenderer:
    """
    Renderer that converts report sections to HTML.

    Can be used directly for HTML output or as input to PDFRenderer.
    Generates clean, semantic HTML with embedded CSS styling.
    """

    def __init__(self, css_style: str | None = None) -> None:
        """
        Initialize HTML renderer.

        Args:
            css_style: Optional custom CSS. If None, uses default styling.
        """
        self.css_style = css_style or self._get_default_css()

    def _get_default_css(self) -> str:
        """Get default CSS styling for reports.

        Embeds Astronomicon font for proper astrological symbol rendering in PDFs.
        Falls back to system symbol fonts for browsers.
        """
        # Get path to Noto Sans Symbols font (has proper Unicode zodiac/planet glyphs)
        import os

        font_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "assets",
            "fonts",
        )
        noto_symbols_path = os.path.join(font_dir, "NotoSansSymbols-Regular.ttf")

        return f"""
        <style>
            /* Embed Noto Sans Symbols for proper Unicode astrological glyphs */
            @font-face {{
                font-family: 'Noto Sans Symbols';
                src: url('file://{noto_symbols_path}') format('truetype');
                font-weight: normal;
                font-style: normal;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                color: #333;
            }}

            /* Font stack for tables - Noto Sans Symbols for zodiac/planet glyphs */
            table, td, th {{
                font-family: 'Noto Sans Symbols', 'Apple Symbols', 'Segoe UI Symbol',
                             'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            h2 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 14px;
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 10px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 8px 10px;
                border-bottom: 1px solid #ddd;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            dl {{
                margin: 15px 0;
            }}
            dt {{
                font-weight: 600;
                color: #2c3e50;
                margin-top: 10px;
            }}
            dd {{
                margin-left: 20px;
                color: #555;
            }}
            .chart-svg {{
                margin: 20px auto;
                text-align: center;
            }}
            .chart-svg svg {{
                max-width: 100%;
                height: auto;
            }}
            .chart-svg svg text {{
                font-family: 'Astronomicon', 'Apple Symbols', sans-serif;
            }}
        </style>
        """

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section to HTML."""
        data_type = section_data.get("type")

        html = f"<h2>{section_name}</h2>\n"

        if data_type == "table":
            html += self._render_table(section_data)
        elif data_type == "key_value":
            html += self._render_key_value(section_data)
        elif data_type == "text":
            html += self._render_text(section_data)
        else:
            html += f"<p>Unknown section type: {data_type}</p>"

        return html

    def _render_table(self, data: dict[str, Any]) -> str:
        """Convert table data to HTML table."""
        html = ["<table>"]

        # Headers
        if "headers" in data and data["headers"]:
            html.append("  <thead><tr>")
            for header in data["headers"]:
                html.append(f"    <th>{header}</th>")
            html.append("  </tr></thead>")

        # Rows
        if "rows" in data and data["rows"]:
            html.append("  <tbody>")
            for row in data["rows"]:
                html.append("  <tr>")
                for cell in row:
                    # Escape HTML and preserve unicode glyphs
                    cell_str = str(cell).replace("<", "&lt;").replace(">", "&gt;")
                    html.append(f"    <td>{cell_str}</td>")
                html.append("  </tr>")
            html.append("  </tbody>")

        html.append("</table>")
        return "\n".join(html)

    def _render_key_value(self, data: dict[str, Any]) -> str:
        """Convert key-value data to HTML definition list."""
        html = ["<dl>"]
        for key, value in data.get("data", {}).items():
            html.append(f"  <dt>{key}</dt>")
            html.append(f"  <dd>{value}</dd>")
        html.append("</dl>")
        return "\n".join(html)

    def _render_text(self, data: dict[str, Any]) -> str:
        """Convert text data to HTML paragraph."""
        text = data.get("text", "")
        # Convert newlines to <br> tags
        text = text.replace("\n", "<br>\n")
        return f"<p>{text}</p>"

    def render_report(
        self,
        sections: list[tuple[str, dict[str, Any]]],
        chart_svg_content: str | None = None,
    ) -> str:
        """
        Render complete report to HTML string.

        Args:
            sections: List of (section_name, section_data) tuples
            chart_svg_content: Optional SVG content to embed

        Returns:
            Complete HTML document as string
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "  <meta charset='UTF-8'>",
            "  <title>Astrological Report</title>",
            self.css_style,
            "</head>",
            "<body>",
        ]

        # Add chart SVG if provided
        if chart_svg_content:
            html_parts.append("<div class='chart-svg'>")
            html_parts.append(chart_svg_content)
            html_parts.append("</div>")

        # Add sections
        for section_name, section_data in sections:
            html_parts.append(self.render_section(section_name, section_data))

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)


# Check for typst availability
try:
    import typst as typst_lib

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


class TypstRenderer:
    """
    Renderer that creates beautiful PDFs using Typst typesetting.

    Typst is a modern typesetting system with LaTeX-quality output
    but much simpler syntax and faster compilation.

    Requires: pip install typst

    Features:
    - Professional typography (kerning, ligatures, hyphenation)
    - Clean table styling with alternating row colors
    - Proper font handling for astrological symbols
    - Embedded SVG chart support
    - Page headers/footers with page numbers
    """

    def __init__(self) -> None:
        """Initialize Typst renderer."""
        if not TYPST_AVAILABLE:
            raise ImportError(
                "Typst library not available. Install with: pip install typst"
            )

    def render_report(
        self,
        sections: list[tuple[str, dict[str, Any]]],
        output_file: str | None = None,
        chart_svg_path: str | None = None,
        title: str = "Astrological Report",
    ) -> bytes:
        """
        Render complete report to PDF using Typst.

        Args:
            sections: List of (section_name, section_data) tuples
            output_file: Optional file path to save PDF
            chart_svg_path: Optional path to chart SVG file to embed
            title: Report title

        Returns:
            PDF as bytes
        """
        import os
        import tempfile

        # Generate Typst content
        typst_content = self._generate_typst_document(sections, chart_svg_path, title)

        # Write to temp file (typst-py requires file path)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".typ", delete=False, encoding="utf-8"
        ) as f:
            f.write(typst_content)
            temp_path = f.name

        try:
            # Get font directories for custom fonts
            base_font_dir = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                ),
                "assets",
                "fonts",
            )
            # Include subdirectories for Cinzel Decorative and Crimson Pro
            font_dirs = [
                base_font_dir,
                os.path.join(base_font_dir, "Cinzel_Decorative"),
                os.path.join(base_font_dir, "Crimson_Pro"),
                os.path.join(base_font_dir, "Crimson_Pro", "static"),  # Static weights
            ]

            # Compile to PDF
            # Use root="/" to allow absolute paths in the document
            # Add font_paths for all our custom fonts
            pdf_bytes = typst_lib.compile(
                temp_path,
                root="/",
                font_paths=font_dirs,
            )

            # Save to output file if requested
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)

            return pdf_bytes
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    def _generate_typst_document(
        self,
        sections: list[tuple[str, dict[str, Any]]],
        chart_svg_path: str | None,
        title: str,
    ) -> str:
        """Generate complete Typst document markup."""
        parts = []

        # Document setup
        parts.append(self._get_document_preamble(title))

        # Title page with chart
        parts.append(self._render_title_page(title, chart_svg_path))

        # Page break after title
        parts.append("\n#pagebreak()\n")

        # Sections
        for section_name, section_data in sections:
            parts.append(self._render_section(section_name, section_data))

        # Footer with generation info
        parts.append("""
#v(1fr)
#generated-footer
""")

        return "\n".join(parts)

    def _render_title_page(self, title: str, chart_svg_path: str | None = None) -> str:
        """Generate Typst markup for title page."""
        parts = []

        # Add breathing room at top
        parts.append("#v(0.3in)")

        # Star divider (now using the function from preamble)
        parts.append("#star-divider")
        parts.append("")

        # Main title
        parts.append(f"= {self._escape(title)}")
        parts.append("")

        # Star divider again
        parts.append("#star-divider")
        parts.append("#v(0.2in)")

        # Chart wheel if provided
        if chart_svg_path:
            import os

            abs_path = os.path.abspath(chart_svg_path)
            parts.append(f'''
    #align(center)[
    #box(
        stroke: 1.5pt + gold,
        radius: 6pt,
        clip: true,
        inset: 10pt,
        fill: white,
        image("{abs_path}", width: 80%)
    )
    ]
    ''')

        # Push remaining space to bottom
        parts.append("#v(1fr)")

        return "\n".join(parts)

    def _get_document_preamble(
        self, title: str, include_title_page: bool = True
    ) -> str:
        """Get Typst document preamble with styling."""
        # Note: Using regular string (not f-string) because Typst uses { } syntax
        return """// Stellium Astrology Report
// Generated with Typst for beautiful typography

// ============================================================================
// COLOR PALETTE - Warm mystical purple theme (matches cream undertones)
// ============================================================================
#let primary = rgb("#4a3353")       // Warm deep purple (more burgundy undertone)
#let secondary = rgb("#6b4d6e")     // Warm medium purple
#let accent = rgb("#8e6b8a")        // Warm light purple/mauve
#let gold = rgb("#b8953d")          // Warm antique gold
#let cream = rgb("#faf8f5")         // Warm cream background
#let text-dark = rgb("#2d2330")     // Warm near-black

// ============================================================================
// PAGE SETUP with subtle cream background
// ============================================================================
#set page(
  paper: "us-letter",
  margin: (top: 0.75in, bottom: 0.75in, left: 0.85in, right: 0.85in),
  fill: cream,
  header: context {
    if counter(page).get().first() > 1 [
      #set text(font: "Cinzel Decorative", size: 8pt, fill: accent, tracking: 0.5pt)
      #h(1fr)
      Astrological Report
      #h(1fr)
    ]
  },
  footer: context {
    set text(size: 8pt, fill: accent)
    h(1fr)
    counter(page).display("1 of 1", both: true)
    h(1fr)
  },
)

// ============================================================================
// TYPOGRAPHY - Crimson Pro body, Cinzel Decorative headings
// ============================================================================
#set text(
  font: ("Crimson Pro", "Crimson Text", "Georgia", "New Computer Modern", "Noto Sans Symbols"),
  size: 10.5pt,
  fill: text-dark,
  hyphenate: true,
)

#set par(
  justify: true,
  leading: 0.85em,
  first-line-indent: 0em,
)

// ============================================================================
// HEADING STYLES - Using Cinzel Decorative for that esoteric feel
// ============================================================================

// Main title (used on title page)
#show heading.where(level: 1): it => {
  set text(font: "Cinzel Decorative", size: 26pt, weight: "regular", fill: primary, tracking: 2pt)
  set par(justify: false)
  align(center)[#it.body]
  v(0.5em)
}

// Section headings with colored band and star symbol
#show heading.where(level: 2): it => {
  v(1em)
  block(
    width: 100%,
    fill: primary,
    inset: (x: 12pt, y: 8pt),
    radius: 2pt,
  )[
    #set text(font: "Cinzel Decorative", size: 10pt, weight: "regular", fill: white, tracking: 0.5pt)
    #sym.star.stroked #it.body
  ]
  v(0.6em)
}

// Subsection headings
#show heading.where(level: 3): it => {
  set text(font: "Cinzel Decorative", size: 10pt, weight: "regular", fill: secondary)
  v(0.5em)
  it.body
  v(0.3em)
  line(length: 40%, stroke: 0.5pt + accent)
  v(0.3em)
}

// === DESIGN FLOURISHES ===
#let star-divider = {
  set align(center)
  v(0.15in)
  box(width: 65%)[
    #grid(
      columns: (1fr, auto, 1fr),
      align: (right, center, left),
      column-gutter: 10pt,
      line(length: 100%, stroke: 0.75pt + gold),
      text(fill: gold, size: 9pt, baseline: -1pt)[★ #h(4pt) #text(fill: primary)[☆] #h(4pt) ★],
      line(length: 100%, stroke: 0.75pt + gold),
    )
  ]
  v(0.15in)
}

#let generated-footer = {
  v(1fr)  // pushes to bottom of available space
  align(center)[
    #line(length: 15%, stroke: 0.5pt + accent)
    #v(6pt)
    #text(font: "Cinzel Decorative", size: 7.5pt, fill: accent, tracking: 0.5pt, style: "italic")[
      Generated with Stellium
    ]
    #v(3pt)
    #text(fill: gold, size: 6pt)[#emoji.moon.crescent]
  ]
}
"""

    def _render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """Render a single section to Typst markup."""
        data_type = section_data.get("type")

        parts = [f"\n== {self._escape(section_name)}\n"]

        if data_type == "table":
            parts.append(self._render_table(section_data))
        elif data_type == "key_value":
            parts.append(self._render_key_value(section_data))
        elif data_type == "text":
            parts.append(self._render_text(section_data))
        elif data_type == "side_by_side_tables":
            parts.append(self._render_side_by_side_tables(section_data))
        else:
            parts.append(f"Unknown section type: {data_type}")

        return "\n".join(parts)

    def _render_table(self, data: dict[str, Any]) -> str:
        """Convert table data to Typst table markup."""
        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not headers:
            return ""

        num_cols = len(headers)
        num_rows = len(rows)

        # Wrap table in a block with rounded corners and clip
        # Use a box to contain the table with rounded corners
        lines = [
            "#align(center)[",
            "#block(",
            "  clip: true,",
            "  radius: 6pt,",
            ")[",
            "#table(",
            f"  columns: {num_cols},",
            "  stroke: none,",  # Remove internal strokes, we have the outer border
            "  inset: (x: 14pt, y: 10pt),",
            "  align: (col, row) => if col == 0 { left } else { center },",
            f"  fill: (col, row) => {{",
            f'    if row == 0 {{ rgb("#4a3353") }}',  # warm primary purple for header
            f'    else if calc.odd(row) {{ rgb("#f9f6f7") }}',  # subtle warm purple tint
            f'    else {{ rgb("#faf8f5") }}',  # cream
            "  },",
        ]

        # Header row with white text
        header_cells = ", ".join(
            f'[#text(fill: white, weight: "semibold")[{self._escape(h)}]]'
            for h in headers
        )
        lines.append(f"  {header_cells},")

        # Data rows
        for row in rows:
            # Ensure row has right number of cells
            padded_row = list(row) + [""] * (num_cols - len(row))
            row_cells = ", ".join(
                f"[{self._escape(str(cell))}]" for cell in padded_row[:num_cols]
            )
            lines.append(f"  {row_cells},")

        lines.append(")")  # close table
        lines.append("]")  # close block
        lines.append("]")  # close align(center)

        return "\n".join(lines)

    def _render_key_value(self, data: dict[str, Any]) -> str:
        """Convert key-value data to Typst grid markup."""
        kv_data = data.get("data", {})

        if not kv_data:
            return ""

        # Elegant key-value display with warm purple styling
        lines = [
            "#block(",
            '  fill: rgb("#f9f6f7"),',  # warm purple tint
            "  inset: 12pt,",
            "  radius: 4pt,",
            "  width: 100%,",
            ")[",
            "#grid(",
            "  columns: (110pt, 1fr),",
            "  gutter: 6pt,",
            "  row-gutter: 8pt,",
        ]

        for key, value in kv_data.items():
            lines.append(
                f'  [#text(fill: rgb("#6b4d6e"), weight: "semibold")[{self._escape(key)}:]], [{self._escape(str(value))}],'
            )

        lines.append(")")
        lines.append("]")

        return "\n".join(lines)

    def _render_text(self, data: dict[str, Any]) -> str:
        """Convert text data to Typst paragraph."""
        text = data.get("text", "")
        return self._escape(text)

    def _render_side_by_side_tables(self, data: dict[str, Any]) -> str:
        """
        Render two tables side by side in Typst.

        Uses Typst's grid layout to place tables next to each other.
        """
        tables_data = data.get("tables", [])
        if not tables_data:
            return ""

        # For two tables, use a grid with two columns
        # For more tables, adjust proportionally
        num_tables = len(tables_data)
        col_spec = ", ".join(["1fr"] * num_tables)

        lines = [
            "#grid(",
            f"  columns: ({col_spec}),",
            "  column-gutter: 16pt,",
        ]

        for i, table_data in enumerate(tables_data):
            title = table_data.get("title", f"Table {i + 1}")
            headers = table_data.get("headers", [])
            rows = table_data.get("rows", [])

            if not headers:
                lines.append("  [],")  # Empty cell
                continue

            num_cols = len(headers)

            # Build table for this chart
            table_lines = [
                "  [",
                f'    #text(font: "Cinzel Decorative", size: 9pt, fill: rgb("#6b4d6e"), tracking: 0.5pt)[{self._escape(title)}]',
                "    #v(6pt)",
                "    #block(",
                "      clip: true,",
                "      radius: 4pt,",
                "      width: 100%,",
                "    )[",
                "    #table(",
                f"      columns: {num_cols},",
                "      stroke: none,",
                "      inset: (x: 8pt, y: 6pt),",
                "      align: (col, row) => if col == 0 { left } else { center },",
                "      fill: (col, row) => {",
                '        if row == 0 { rgb("#4a3353") }',
                '        else if calc.odd(row) { rgb("#f9f6f7") }',
                '        else { rgb("#faf8f5") }',
                "      },",
            ]

            # Header row
            header_cells = ", ".join(
                f'[#text(fill: white, weight: "semibold", size: 8pt)[{self._escape(h)}]]'
                for h in headers
            )
            table_lines.append(f"      {header_cells},")

            # Data rows
            for row in rows:
                padded_row = list(row) + [""] * (num_cols - len(row))
                row_cells = ", ".join(
                    f"[#text(size: 8pt)[{self._escape(str(cell))}]]"
                    for cell in padded_row[:num_cols]
                )
                table_lines.append(f"      {row_cells},")

            table_lines.append("    )")  # close table
            table_lines.append("    ]")  # close block
            table_lines.append("  ],")  # close grid cell

            lines.extend(table_lines)

        lines.append(")")  # close grid

        return "\n".join(lines)

    def _render_chart_svg(self, svg_path: str) -> str:
        """Generate Typst markup to embed chart SVG."""
        import os

        # Make path absolute for Typst to find it
        abs_path = os.path.abspath(svg_path)
        return f'''
#align(center)[
  #box(
    stroke: 1pt + rgb("#e2e8f0"),
    radius: 4pt,
    clip: true,
    inset: 8pt,
    image("{abs_path}", width: 90%)
  )
]
#v(0.5em)
'''

    def _escape(self, text: str) -> str:
        """Escape special Typst characters in text."""
        # Characters that need escaping in Typst
        # Note: # starts commands, * is bold, _ is italic, etc.
        text = str(text)
        # Escape backslashes first
        text = text.replace("\\", "\\\\")
        # Escape other special chars
        for char in ["#", "*", "_", "@", "$", "`"]:
            text = text.replace(char, "\\" + char)
        return text
