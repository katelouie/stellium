"""
AtlasRenderer - Generate atlas PDFs using Typst typesetting.

Renders chart SVGs and compiles them into a multi-page PDF.
"""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stellium.visualization.atlas.config import AtlasConfig, AtlasEntry

# Check if typst is available
try:
    import typst as typst_lib

    TYPST_AVAILABLE = True
except ImportError:
    TYPST_AVAILABLE = False


class AtlasRenderer:
    """
    Renders atlas PDF using Typst typesetting.

    Generates chart SVGs for each entry, embeds them in a Typst document,
    and compiles to PDF.
    """

    def __init__(self, config: AtlasConfig) -> None:
        """
        Initialize renderer with configuration.

        Args:
            config: AtlasConfig from AtlasBuilder
        """
        if not TYPST_AVAILABLE:
            raise ImportError(
                "Typst library not available. Install with: pip install typst"
            )

        self.config = config
        self._temp_dir: str | None = None
        self._svg_paths: list[str] = []

    def render(self) -> bytes:
        """
        Render the complete atlas to PDF.

        Returns:
            PDF as bytes
        """
        # Create temp directory for chart files
        self._temp_dir = tempfile.mkdtemp(prefix="stellium_atlas_")

        try:
            # Generate chart SVGs
            self._generate_charts()

            # Generate Typst document
            typst_content = self._generate_typst_document()

            # Write to temp file and compile
            typst_path = os.path.join(self._temp_dir, "atlas.typ")
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
            os.path.join(base_font_dir, "Noto_Sans_Symbols"),
            os.path.join(base_font_dir, "Noto_Sans_Symbols_2"),
            os.path.join(base_font_dir, "Symbola"),
        ]

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        import shutil

        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)

    def _generate_charts(self) -> None:
        """Generate chart files for all entries."""
        for i, entry in enumerate(self.config.entries):
            svg_path = self._generate_chart_svg(entry, i)
            self._svg_paths.append(svg_path)

    def _generate_chart_svg(self, entry: AtlasEntry, index: int) -> str:
        """
        Generate SVG file for one entry.

        Args:
            entry: AtlasEntry with native and chart config
            index: Entry index for filename

        Returns:
            Path to generated SVG file
        """
        from stellium.core.builder import ChartBuilder
        from stellium.engines import ModernAspectEngine

        # Calculate chart with aspects
        chart = (
            ChartBuilder.from_native(entry.native)
            .with_aspects(ModernAspectEngine())
            .calculate()
        )

        # Generate SVG based on chart_type
        svg_path = os.path.join(self._temp_dir, f"chart_{index}.svg")

        if entry.chart_type == "wheel":
            builder = chart.draw(svg_path)

            # Apply configuration
            if self.config.show_header:
                builder.with_header()
            builder.with_theme(self.config.theme)
            builder.with_zodiac_palette(self.config.zodiac_palette)

            # Info corners
            if self.config.show_aspect_counts:
                builder.with_aspect_counts()
            if self.config.show_element_modality:
                builder.with_element_modality_table()

            # Extended tables
            if self.config.show_extended_tables:
                builder.with_tables(position="right")

            builder.save()

        elif entry.chart_type == "dial":
            degrees = entry.chart_options.get("degrees", 90)
            builder = chart.draw_dial(svg_path, degrees=degrees)

            # Apply configuration
            if self.config.show_header:
                builder.with_header()
            builder.with_theme(self.config.theme)

            builder.save()

        else:
            raise ValueError(f"Unknown chart_type: {entry.chart_type}")

        return svg_path

    def _generate_typst_document(self) -> str:
        """Generate complete Typst document."""
        parts = []

        # Document preamble
        parts.append(self._get_preamble())

        # Optional title page
        if self.config.title:
            parts.append(self._render_title_page())

        # Group entries by event type for section dividers
        births = []
        events = []
        other = []

        for i, entry in enumerate(self.config.entries):
            # Check if entry has event_type (Notable has it, Native doesn't)
            event_type = getattr(entry.native, "event_type", None)
            if event_type == "birth":
                births.append((i, self._svg_paths[i], entry))
            elif event_type == "event":
                events.append((i, self._svg_paths[i], entry))
            else:
                other.append((i, self._svg_paths[i], entry))

        # Render sections with dividers if we have both types
        has_sections = len(births) > 0 and (len(events) > 0 or len(other) > 0)

        # Births section
        if births:
            if has_sections:
                parts.append(self._render_section_divider("Births", len(births)))
            for i, svg_path, _entry in births:
                parts.append(self._render_chart_page(svg_path, i))

        # Events section
        if events:
            if has_sections:
                parts.append(
                    self._render_section_divider("Historical Events", len(events))
                )
            for i, svg_path, _entry in events:
                parts.append(self._render_chart_page(svg_path, i))

        # Other (entries without event_type, e.g., plain Native objects)
        if other:
            if has_sections and (births or events):
                parts.append(self._render_section_divider("Charts", len(other)))
            for i, svg_path, _entry in other:
                parts.append(self._render_chart_page(svg_path, i))

        return "\n".join(parts)

    def _get_preamble(self) -> str:
        """Get Typst document preamble with styling."""
        # Handle landscape for extended tables
        if self.config.show_extended_tables:
            # Landscape - use flipped parameter
            page_size = {
                "a4": '"a4"',
                "letter": '"us-letter"',
                "half-letter": '"us-letter"',  # Fall back to letter for half
            }.get(self.config.page_size, '"us-letter"')
            page_flipped = "true"
        else:
            # Portrait dimensions
            page_size = {
                "a4": '"a4"',
                "letter": '"us-letter"',
                "half-letter": '"us-letter"',
            }.get(self.config.page_size, '"us-letter"')
            page_flipped = "false"

        return f"""// Stellium Chart Atlas
// Generated with Typst

// ============================================================================
// COLOR PALETTE
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
  flipped: {page_flipped},
  margin: 0.4in,
  fill: cream,
)

// ============================================================================
// TYPOGRAPHY
// ============================================================================
#set text(
  font: ("Crimson Pro", "Noto Sans Symbols 2", "Noto Sans Symbols", "Symbola", "Georgia", "serif"),
  size: 11pt,
  fill: text-dark,
)
"""

    def _render_section_divider(self, section_name: str, count: int) -> str:
        """Render a section divider page."""
        return f"""
// ============================================================================
// SECTION: {section_name}
// ============================================================================
#pagebreak()
#align(center + horizon)[
  #box(width: 70%)[
    #line(length: 100%, stroke: 0.75pt + gold)
    #v(0.3in)
    #text(font: "Cinzel Decorative", size: 32pt, fill: primary, tracking: 1.5pt)[
      {self._escape(section_name)}
    ]
    #v(0.15in)
    #text(size: 14pt, fill: secondary)[
      {count} {"chart" if count == 1 else "charts"}
    ]
    #v(0.3in)
    #line(length: 100%, stroke: 0.75pt + gold)
  ]
]
#pagebreak()
"""

    def _render_title_page(self) -> str:
        """Render the title page."""
        title = self._escape(self.config.title or "Chart Atlas")

        return f"""
// ============================================================================
// TITLE PAGE
// ============================================================================
#align(center + horizon)[
  #box(width: 70%)[
    #line(length: 100%, stroke: 0.75pt + gold)
    #v(0.2in)
    #text(font: "Cinzel Decorative", size: 28pt, fill: primary, tracking: 1.5pt)[
      {title}
    ]
    #v(0.2in)
    #line(length: 100%, stroke: 0.75pt + gold)
  ]
]

#v(1fr)

#align(center)[
  #text(font: "Cinzel Decorative", size: 9pt, fill: accent, style: "italic")[
    Generated with Stellium
  ]
]

#pagebreak()
"""

    def _render_chart_page(self, svg_path: str, index: int) -> str:
        """
        Render a single chart page.

        Args:
            svg_path: Path to chart SVG file
            index: Chart index

        Returns:
            Typst markup for the chart page
        """
        abs_path = os.path.abspath(svg_path)

        # Use align center+horizon to center the chart on the page
        # width: 100% and height: 100% with fit: contain ensures it fills
        # the page while maintaining aspect ratio
        return f"""
// Chart {index + 1}
#align(center + horizon)[
  #image("{abs_path}", width: 100%, height: 100%, fit: "contain")
]
#pagebreak()
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
