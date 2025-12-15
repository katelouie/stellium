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
        elif data_type == "compound":
            return self._render_compound(section_name, section_data)
        elif data_type == "svg":
            return self._render_svg(section_name, section_data)
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
            elif data_type == "compound":
                self._print_compound(console, section_data)
            elif data_type == "svg":
                self._print_svg(console, section_data)
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

    def _render_compound(self, section_name: str, data: dict[str, Any]) -> str:
        """Render compound section with multiple sub-sections (supports nesting)."""
        parts = []
        for sub_name, sub_data in data.get("sections", []):
            sub_type = sub_data.get("type")
            if sub_type == "table":
                parts.append(self._render_table(sub_name, sub_data))
            elif sub_type == "key_value":
                parts.append(self._render_key_value(sub_name, sub_data))
            elif sub_type == "text":
                parts.append(
                    f"\n{sub_name}:\n{sub_data.get('content', sub_data.get('text', ''))}"
                )
            elif sub_type == "compound":
                # Recursive: render nested compound section
                parts.append(f"\n{sub_name}:")
                parts.append(self._render_compound(sub_name, sub_data))
            elif sub_type == "svg":
                # SVG in compound - show placeholder in terminal
                parts.append(self._render_svg(sub_name, sub_data))
            else:
                parts.append(f"\n{sub_name}: (unknown type {sub_type})")
        return "\n".join(parts)

    def _render_svg(self, section_name: str, data: dict[str, Any]) -> str:
        """Render SVG placeholder for terminal output."""
        # Terminal can't display SVGs - show info message
        svg_content = data.get("content", "")
        # Extract dimensions if possible
        import re

        width_match = re.search(r'width="(\d+)(?:px)?"', svg_content)
        height_match = re.search(r'height="(\d+)(?:px)?"', svg_content)
        width = width_match.group(1) if width_match else "?"
        height = height_match.group(1) if height_match else "?"
        return f"[SVG: {width}x{height}px - use HTML/PDF output to view]"

    def _print_svg(self, console: Console, data: dict[str, Any]) -> None:
        """Print SVG placeholder for terminal output."""
        svg_content = data.get("content", "")
        # Extract dimensions if possible
        import re

        width_match = re.search(r'width="(\d+)(?:px)?"', svg_content)
        height_match = re.search(r'height="(\d+)(?:px)?"', svg_content)
        width = width_match.group(1) if width_match else "?"
        height = height_match.group(1) if height_match else "?"
        console.print(
            f"[SVG: {width}x{height}px - use HTML/PDF output to view]", style="dim"
        )

    def _print_compound(
        self, console: Console, data: dict[str, Any], indent: int = 0
    ) -> None:
        """Print compound section with multiple sub-sections (supports nesting)."""
        prefix = "  " * indent
        for sub_name, sub_data in data.get("sections", []):
            # Print sub-section header
            console.print(f"\n{prefix}  {sub_name}", style="bold yellow")

            sub_type = sub_data.get("type")
            if sub_type == "table":
                self._print_table(console, sub_data)
            elif sub_type == "key_value":
                self._print_key_value(console, sub_data)
            elif sub_type == "text":
                console.print(
                    f"{prefix}  {sub_data.get('content', sub_data.get('text', ''))}"
                )
            elif sub_type == "compound":
                # Recursive: print nested compound section
                self._print_compound(console, sub_data, indent + 1)
            elif sub_type == "svg":
                # SVG in compound - show placeholder
                self._print_svg(console, sub_data)
            else:
                console.print(f"{prefix}  (unknown type {sub_type})")

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
        elif data_type == "compound":
            return self._render_compound(section_name, section_data)
        else:
            return f"Unknown section type: {data_type}"

    def _render_compound(self, section_name: str, data: dict[str, Any]) -> str:
        """Render compound section with multiple sub-sections."""
        parts = []
        for sub_name, sub_data in data.get("sections", []):
            # Sub-section header
            parts.append(f"\n  {sub_name}")
            parts.append("  " + "-" * len(sub_name))

            sub_type = sub_data.get("type")
            if sub_type == "table":
                parts.append(self._render_table(sub_name, sub_data))
            elif sub_type == "key_value":
                parts.append(self._render_key_value(sub_name, sub_data))
            elif sub_type == "text":
                parts.append(f"  {sub_data.get('content', sub_data.get('text', ''))}")
            else:
                parts.append(f"  (unknown type {sub_type})")
        return "\n".join(parts)

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
        header_cells = [h.ljust(w) for h, w in zip(headers, col_widths, strict=False)]
        lines.append("| " + " | ".join(header_cells) + " |")

        # Separator
        separator_cells = ["-" * w for w in col_widths]
        lines.append("|-" + "-|-".join(separator_cells) + "-|")

        # Data rows
        for row in str_rows:
            # Pad row if needed
            padded_row = row + [""] * (len(headers) - len(row))

            row_cells = [
                cell.ljust(w) for cell, w in zip(padded_row, col_widths, strict=False)
            ]
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
            parts.append(f"""
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
    """)

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
        elif data_type == "compound":
            parts.append(self._render_compound(section_data))
        elif data_type == "svg":
            # SVG sections need special handling
            parts.append(self._render_svg_section(section_data))
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
        _num_rows = len(rows)

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
            "  fill: (col, row) => {",
            '    if row == 0 { rgb("#6b4d6e") }',  # secondary purple for table header (lighter than section headers)
            '    else if calc.odd(row) { rgb("#f9f6f7") }',  # subtle warm purple tint
            '    else { rgb("#faf8f5") }',  # cream
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
        return f"""
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
"""

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

    def _render_compound(self, data: dict[str, Any]) -> str:
        """Render compound section with multiple sub-sections."""
        parts = []
        for sub_name, sub_data in data.get("sections", []):
            sub_type = sub_data.get("type")

            # Add subsection heading
            parts.append(f"\n=== {self._escape(sub_name)}\n")

            if sub_type == "table":
                parts.append(self._render_table(sub_data))
            elif sub_type == "key_value":
                parts.append(self._render_key_value(sub_data))
            elif sub_type == "text":
                parts.append(self._render_text(sub_data))
            elif sub_type == "side_by_side_tables":
                parts.append(self._render_side_by_side_tables(sub_data))
            elif sub_type == "svg":
                parts.append(self._render_svg_section(sub_data))
            elif sub_type == "compound":
                # Recursive: nested compound section
                parts.append(self._render_compound(sub_data))
            else:
                parts.append(f"(unknown sub-section type: {sub_type})")

        return "\n".join(parts)

    def _render_svg_section(self, data: dict[str, Any]) -> str:
        """Render an inline SVG section.

        For Typst, we need to save the SVG to a temp file and reference it,
        or note that SVG embedding requires special handling.
        """
        import os
        import tempfile

        svg_content = data.get("content", "")
        if not svg_content:
            return "_No SVG content available_"

        # Write SVG to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".svg", delete=False, encoding="utf-8"
        ) as f:
            f.write(svg_content)
            svg_path = f.name

        abs_path = os.path.abspath(svg_path)

        return f"""
#align(center)[
  #box(
    stroke: 1pt + gold,
    radius: 4pt,
    clip: true,
    inset: 8pt,
    fill: white,
    image("{abs_path}", width: 90%)
  )
]
#v(0.5em)
"""


class ProseRenderer:
    """
    Renderer that converts structured section data to natural language prose.

    Designed for pasting chart info into conversations with AI friends or
    anywhere you want clean, readable text without tables or formatting codes.

    Output format:
    - Chart overview as flowing sentences
    - Lists of positions/aspects as bullet points
    - No tables, no headers, no special formatting

    Example output:
        Kate Louie was born on January 6, 1994 at 11:47 AM in Mountain View, CA.
        This is a day chart with Aries rising. The chart ruler is Mars.

        Planet Positions:
        • The Sun is at 15°52' Capricorn in the 9th house
        • The Moon is at 22°14' Scorpio in the 6th house
        ...
    """

    def __init__(self, bullet: str = "•") -> None:
        """
        Initialize prose renderer.

        Args:
            bullet: Character to use for list items (default: •)
        """
        self.bullet = bullet

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """
        Render complete report as natural language prose.

        Args:
            sections: List of (section_name, section_data) tuples

        Returns:
            Prose text suitable for pasting into conversations
        """
        paragraphs = []

        for section_name, section_data in sections:
            prose = self._render_section(section_name, section_data)
            if prose:
                paragraphs.append(prose)

        return "\n\n".join(paragraphs)

    def _render_section(self, section_name: str, data: dict[str, Any]) -> str:
        """
        Render a single section to prose.

        Dispatches to section-specific formatters based on section_name,
        with fallback to generic formatting.
        """
        # Map section names to specialized prose formatters
        formatters: dict[str, Any] = {
            "Chart Overview": self._prose_chart_overview,
            "Planet Positions": self._prose_planet_positions,
            "House Cusps": self._prose_house_cusps,
            "Aspects": self._prose_aspects,
            "Major Aspects": self._prose_aspects,
            "Minor Aspects": self._prose_aspects,
            "Harmonic Aspects": self._prose_aspects,
            "Aspect Patterns": self._prose_aspect_patterns,
            "Moon Phase": self._prose_moon_phase,
            "Essential Dignities": self._prose_dignities,
            "Arabic Parts": self._prose_arabic_parts,
            "Midpoints": self._prose_midpoints,
            "Planetary Stations": self._prose_stations,
            "Stations": self._prose_stations,
            "Sign Ingresses": self._prose_ingresses,
            "Ingresses": self._prose_ingresses,
            "Eclipses": self._prose_eclipses,
        }

        formatter = formatters.get(section_name)
        if formatter:
            return formatter(section_name, data)
        else:
            # Fallback: generic prose conversion
            return self._prose_generic(section_name, data)

    # =========================================================================
    # CORE SECTION FORMATTERS
    # =========================================================================

    def _prose_chart_overview(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert chart overview key-value data to flowing prose."""
        if data.get("type") != "key_value":
            return self._prose_generic(section_name, data)

        kv = data.get("data", {})
        parts = []

        # Build opening sentence with name, date, time, location
        name = kv.get("Name", "")
        date = kv.get("Date", "")
        time = kv.get("Time", "")
        location = kv.get("Location", "")

        if name and date and time and location:
            parts.append(f"{name} was born on {date} at {time} in {location}.")
        elif date and time and location:
            parts.append(f"Chart for {date} at {time} in {location}.")
        elif date and time:
            parts.append(f"Chart for {date} at {time}.")

        # Add chart sect and ruler
        sect = kv.get("Chart Sect", "")
        ruler = kv.get("Chart Ruler", "")
        if sect and ruler:
            # Extract rising sign from ruler string like "Mars (Aries Rising)"
            if "(" in ruler and "Rising" in ruler:
                rising = ruler.split("(")[1].replace(" Rising)", "").strip()
                chart_ruler = ruler.split()[0]
                parts.append(
                    f"This is a {sect.lower()} with {rising} rising. The chart ruler is {chart_ruler}."
                )
            else:
                parts.append(f"This is a {sect.lower()}. The chart ruler is {ruler}.")
        elif sect:
            parts.append(f"This is a {sect.lower()}.")
        elif ruler:
            parts.append(f"The chart ruler is {ruler}.")

        # Add house system and zodiac
        house_system = kv.get("House System", "")
        zodiac = kv.get("Zodiac", "")
        if house_system and zodiac:
            parts.append(f"Using {house_system} houses with {zodiac} zodiac.")
        elif house_system:
            parts.append(f"Using {house_system} houses.")

        return " ".join(parts)

    def _prose_planet_positions(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert planet positions table to bulleted list."""
        if data.get("type") == "side_by_side_tables":
            # Comparison chart - handle both charts
            return self._prose_side_by_side_positions(section_name, data)

        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not rows:
            return ""

        lines = ["Planet Positions:"]

        # Figure out column indices
        pos_idx = headers.index("Position") if "Position" in headers else 1

        # Find house column (might be "House (P)" or "House (WS)" etc.)
        house_idx = None
        for i, h in enumerate(headers):
            if h.startswith("House"):
                house_idx = i
                break

        # Check for speed/motion columns
        motion_idx = headers.index("Motion") if "Motion" in headers else None

        for row in rows:
            planet = row[0]  # Already has glyph
            position = row[pos_idx] if pos_idx < len(row) else ""

            # Build the sentence
            sentence = f"{self.bullet} {planet} is at {position}"

            # Add house if available
            if house_idx is not None and house_idx < len(row):
                house = row[house_idx]
                if house and house != "—":
                    try:
                        sentence += f" in the {self._ordinal(int(house))} house"
                    except ValueError:
                        sentence += f" in house {house}"

            # Add retrograde status if available
            if motion_idx is not None and motion_idx < len(row):
                motion = row[motion_idx]
                if motion == "Retrograde":
                    sentence += ", retrograde"

            lines.append(sentence)

        return "\n".join(lines)

    def _prose_side_by_side_positions(
        self, section_name: str, data: dict[str, Any]
    ) -> str:
        """Handle side-by-side planet positions for comparisons."""
        tables = data.get("tables", [])
        if not tables:
            return ""

        all_lines = []
        for table in tables:
            title = table.get("title", "Chart")
            headers = table.get("headers", [])
            rows = table.get("rows", [])

            lines = [f"{title} - Planet Positions:"]

            pos_idx = headers.index("Position") if "Position" in headers else 1
            house_idx = None
            for i, h in enumerate(headers):
                if h.startswith("House"):
                    house_idx = i
                    break

            for row in rows:
                planet = row[0]
                position = row[pos_idx] if pos_idx < len(row) else ""
                sentence = f"{self.bullet} {planet} is at {position}"

                if house_idx is not None and house_idx < len(row):
                    house = row[house_idx]
                    if house and house != "—":
                        try:
                            sentence += f" in the {self._ordinal(int(house))} house"
                        except ValueError:
                            sentence += f" in house {house}"

                lines.append(sentence)

            all_lines.append("\n".join(lines))

        return "\n\n".join(all_lines)

    def _prose_house_cusps(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert house cusps table to bulleted list."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not rows:
            return ""

        # Get the first cusp column (skip "House" column)
        cusp_col = 1 if len(headers) > 1 else 0

        lines = ["House Cusps:"]
        for row in rows:
            house_num = row[0]
            cusp_pos = row[cusp_col] if cusp_col < len(row) else ""
            lines.append(f"{self.bullet} House {house_num} cusp at {cusp_pos}")

        return "\n".join(lines)

    def _prose_aspects(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert aspects table to bulleted list."""
        # Handle compound sections (with aspectarian SVG)
        if data.get("type") == "compound":
            # Find the table sub-section
            for _sub_name, sub_data in data.get("sections", []):
                if sub_data.get("type") == "table":
                    data = sub_data
                    break
            else:
                return self._prose_generic(section_name, data)

        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])

        if not rows:
            return f"No {section_name.lower()} found."

        lines = [f"{section_name}:"]

        # Get column indices
        orb_idx = headers.index("Orb") if "Orb" in headers else None
        applying_idx = headers.index("Applying") if "Applying" in headers else None

        for row in rows:
            planet1 = row[0]
            aspect = row[1]
            planet2 = row[2]

            sentence = f"{self.bullet} {planet1} {aspect} {planet2}"

            # Add orb
            if orb_idx is not None and orb_idx < len(row):
                orb = row[orb_idx]
                sentence += f" (orb {orb}"

                # Add applying/separating
                if applying_idx is not None and applying_idx < len(row):
                    app = row[applying_idx]
                    if app == "A→":
                        sentence += ", applying"
                    elif app == "←S":
                        sentence += ", separating"

                sentence += ")"

            lines.append(sentence)

        return "\n".join(lines)

    def _prose_aspect_patterns(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert aspect patterns to prose."""
        if data.get("type") == "text":
            return data.get("content", "")

        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        rows = data.get("rows", [])
        if not rows:
            return "No aspect patterns detected."

        lines = ["Aspect Patterns:"]
        for row in rows:
            pattern_name = row[0]
            planets = row[1]
            element = row[2] if len(row) > 2 else ""

            sentence = f"{self.bullet} {pattern_name} involving {planets}"
            if element and element != "—":
                sentence += f" ({element})"

            lines.append(sentence)

        return "\n".join(lines)

    def _prose_moon_phase(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert moon phase to prose."""
        if data.get("type") == "key_value":
            kv = data.get("data", {})
            # Handle both "Phase" and "Phase Name" keys
            phase = kv.get("Phase Name", kv.get("Phase", ""))
            illumination = kv.get("Illumination", "")
            direction = kv.get("Direction", "")

            parts = []
            if phase:
                parts.append(f"Moon Phase: The Moon is in its {phase} phase")
            if illumination:
                parts.append(f" ({illumination} illuminated)")
            if direction:
                parts.append(f", {direction.lower()}")

            if parts:
                return "".join(parts) + "."

            return ""

        return self._prose_generic(section_name, data)

    def _prose_dignities(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert dignities table to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        rows = data.get("rows", [])
        if not rows:
            return ""

        lines = ["Essential Dignities:"]
        for row in rows:
            planet = row[0]
            dignity = row[1] if len(row) > 1 else ""

            if dignity and dignity != "—" and dignity != "Peregrine":
                lines.append(f"{self.bullet} {planet}: {dignity}")
            elif dignity == "Peregrine":
                lines.append(
                    f"{self.bullet} {planet}: Peregrine (no essential dignity)"
                )

        return "\n".join(lines) if len(lines) > 1 else ""

    def _prose_arabic_parts(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert Arabic parts to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        rows = data.get("rows", [])
        if not rows:
            return ""

        lines = ["Arabic Parts (Lots):"]
        for row in rows:
            part_name = row[0]
            position = row[1] if len(row) > 1 else ""
            house = row[2] if len(row) > 2 else ""

            sentence = f"{self.bullet} {part_name} at {position}"
            if house and house != "—":
                try:
                    sentence += f" in the {self._ordinal(int(house))} house"
                except ValueError:
                    sentence += f" in house {house}"
            lines.append(sentence)

        return "\n".join(lines)

    def _prose_midpoints(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert midpoints to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        rows = data.get("rows", [])
        if not rows:
            return ""

        lines = ["Midpoints:"]
        for row in rows:
            midpoint = row[0]
            position = row[1] if len(row) > 1 else ""
            lines.append(f"{self.bullet} {midpoint} at {position}")

        return "\n".join(lines)

    # =========================================================================
    # TRANSIT CALENDAR FORMATTERS
    # =========================================================================

    def _prose_stations(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert stations table to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])
        if not rows:
            return "No planetary stations in this period."

        # Get column indices - format is: Date, Time, Planet, Station, Position, Sign
        date_idx = 0
        time_idx = headers.index("Time") if "Time" in headers else 1
        planet_idx = headers.index("Planet") if "Planet" in headers else 2
        station_idx = headers.index("Station") if "Station" in headers else 3
        pos_idx = headers.index("Position") if "Position" in headers else 4
        sign_idx = headers.index("Sign") if "Sign" in headers else 5

        lines = ["Planetary Stations:"]
        for row in rows:
            date = row[date_idx] if date_idx < len(row) else ""
            time = row[time_idx] if time_idx < len(row) else ""
            planet = row[planet_idx] if planet_idx < len(row) else ""
            station = row[station_idx] if station_idx < len(row) else ""
            position = row[pos_idx] if pos_idx < len(row) else ""
            sign = row[sign_idx] if sign_idx < len(row) else ""

            sentence = f"{self.bullet} {date} at {time}: {planet} stations {station} at {position} {sign}"
            lines.append(sentence)

        return "\n".join(lines)

    def _prose_ingresses(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert ingresses table to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])
        if not rows:
            return "No sign ingresses in this period."

        # Get column indices - format is: Date, Time, Planet, From, To
        date_idx = 0
        time_idx = headers.index("Time") if "Time" in headers else 1
        planet_idx = headers.index("Planet") if "Planet" in headers else 2
        to_idx = headers.index("To") if "To" in headers else 4

        lines = ["Sign Ingresses:"]
        for row in rows:
            date = row[date_idx] if date_idx < len(row) else ""
            time = row[time_idx] if time_idx < len(row) else ""
            planet = row[planet_idx] if planet_idx < len(row) else ""
            to_sign = row[to_idx] if to_idx < len(row) else ""

            lines.append(f"{self.bullet} {date} at {time}: {planet} enters {to_sign}")

        return "\n".join(lines)

    def _prose_eclipses(self, section_name: str, data: dict[str, Any]) -> str:
        """Convert eclipses table to prose."""
        if data.get("type") != "table":
            return self._prose_generic(section_name, data)

        headers = data.get("headers", [])
        rows = data.get("rows", [])
        if not rows:
            return "No eclipses in this period."

        # Get column indices - format is: Date, Time, Type, Position, Sign, Node
        date_idx = 0
        time_idx = headers.index("Time") if "Time" in headers else 1
        type_idx = headers.index("Type") if "Type" in headers else 2
        pos_idx = headers.index("Position") if "Position" in headers else 3
        sign_idx = headers.index("Sign") if "Sign" in headers else 4
        node_idx = headers.index("Node") if "Node" in headers else 5

        lines = ["Eclipses:"]
        for row in rows:
            date = row[date_idx] if date_idx < len(row) else ""
            time = row[time_idx] if time_idx < len(row) else ""
            eclipse_type = row[type_idx] if type_idx < len(row) else ""
            position = row[pos_idx] if pos_idx < len(row) else ""
            sign = row[sign_idx] if sign_idx < len(row) else ""
            node = row[node_idx] if node_idx < len(row) else ""

            sentence = f"{self.bullet} {date} at {time}: {eclipse_type} eclipse at {position} {sign}"
            if node:
                sentence += f" (near {node})"
            lines.append(sentence)

        return "\n".join(lines)

    # =========================================================================
    # GENERIC FALLBACK
    # =========================================================================

    def _prose_generic(self, section_name: str, data: dict[str, Any]) -> str:
        """
        Generic fallback for sections without specific formatters.

        Converts tables to bulleted lists and key-value to sentences.
        """
        data_type = data.get("type")

        if data_type == "text":
            return f"{section_name}:\n{data.get('text', data.get('content', ''))}"

        if data_type == "key_value":
            kv = data.get("data", {})
            lines = [f"{section_name}:"]
            for key, value in kv.items():
                lines.append(f"{self.bullet} {key}: {value}")
            return "\n".join(lines)

        if data_type == "table":
            _headers = data.get("headers", [])
            rows = data.get("rows", [])

            if not rows:
                return ""

            lines = [f"{section_name}:"]
            for row in rows:
                # Join row values intelligently
                parts = [str(cell) for cell in row if cell and cell != "—"]
                lines.append(f"{self.bullet} {' | '.join(parts)}")

            return "\n".join(lines)

        if data_type == "compound":
            parts = [f"{section_name}:"]
            for sub_name, sub_data in data.get("sections", []):
                if sub_data.get("type") == "svg":
                    continue  # Skip SVG in prose output
                sub_prose = self._render_section(sub_name, sub_data)
                if sub_prose:
                    parts.append(sub_prose)
            return "\n\n".join(parts)

        if data_type == "side_by_side_tables":
            tables = data.get("tables", [])
            parts = []
            for table in tables:
                title = table.get("title", "")
                rows = table.get("rows", [])
                lines = [f"{title}:" if title else f"{section_name}:"]
                for row in rows:
                    cell_parts = [str(c) for c in row if c and c != "—"]
                    lines.append(f"{self.bullet} {' | '.join(cell_parts)}")
                parts.append("\n".join(lines))
            return "\n\n".join(parts)

        return f"{section_name}: (unsupported format)"

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal string (1st, 2nd, 3rd, etc.)."""
        if 11 <= (n % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"
