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
        """Get default CSS styling for reports."""
        return """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                color: #333;
            }
            h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
                margin-top: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 14px;
            }
            th {
                background-color: #3498db;
                color: white;
                padding: 10px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 8px 10px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            dl {
                margin: 15px 0;
            }
            dt {
                font-weight: 600;
                color: #2c3e50;
                margin-top: 10px;
            }
            dd {
                margin-left: 20px;
                color: #555;
            }
            .chart-svg {
                margin: 20px auto;
                text-align: center;
            }
            .chart-svg svg {
                max-width: 100%;
                height: auto;
                font-variant-emoji: text;  /* Prefer text glyphs over emoji */
            }
            .chart-svg svg text {
                font-variant-emoji: text;  /* Also apply to text elements */
            }
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

    def render_report(self, sections: list[tuple[str, dict[str, Any]]],
                     chart_svg_content: str | None = None) -> str:
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


class PDFRenderer:
    """
    Renderer that converts report sections to PDF using WeasyPrint.

    Requires: pip install weasyprint
    """

    def __init__(self) -> None:
        """Initialize PDF renderer."""
        try:
            import weasyprint
            self.weasyprint = weasyprint
        except ImportError:
            raise ImportError(
                "WeasyPrint not available. Install with: pip install weasyprint"
            )

        self.html_renderer = HTMLRenderer()

    def render_report(self, sections: list[tuple[str, dict[str, Any]]],
                     output_file: str | None = None,
                     chart_svg_path: str | None = None) -> bytes:
        """
        Render complete report to PDF.

        Args:
            sections: List of (section_name, section_data) tuples
            output_file: Optional file path to save PDF
            chart_svg_path: Optional path to chart SVG file to embed

        Returns:
            PDF as bytes
        """
        # Load SVG content if path provided
        svg_content = None
        if chart_svg_path:
            try:
                with open(chart_svg_path, "r") as f:
                    svg_content = f.read()
            except Exception as e:
                print(f"Warning: Could not load SVG from {chart_svg_path}: {e}")

        # Generate HTML
        html_content = self.html_renderer.render_report(sections, svg_content)

        # Convert HTML to PDF
        html_doc = self.weasyprint.HTML(string=html_content)
        pdf_bytes = html_doc.write_pdf()

        # Save to file if requested
        if output_file:
            with open(output_file, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes
