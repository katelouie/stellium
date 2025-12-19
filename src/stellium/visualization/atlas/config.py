"""
Configuration dataclasses for atlas generation.
"""

from dataclasses import dataclass, field
from typing import Any

from stellium.core.native import Native


@dataclass
class AtlasEntry:
    """
    Single entry in the atlas.

    Each entry represents one chart page in the PDF.

    Attributes:
        native: The Native (birth data) for this chart
        chart_type: Type of chart to render ("wheel" or "dial")
        chart_options: Additional options for the chart type
            - For "dial": {"degrees": 90} (90, 45, or 360)
    """

    native: Native
    chart_type: str = "wheel"
    chart_options: dict[str, Any] = field(default_factory=dict)


@dataclass
class AtlasConfig:
    """
    Configuration for atlas PDF generation.

    Attributes:
        entries: List of AtlasEntry objects (charts to include)
        page_size: Paper size ("letter", "a4", "half-letter")
        theme: Visual theme for charts (e.g., "classic", "midnight")
        zodiac_palette: Zodiac ring color palette (default: "rainbow")
        show_header: Whether to show native info header on each chart
        show_aspects: Whether to show aspect lines on charts
        show_extended_tables: Whether to show extended tables (enables landscape)
        show_aspect_counts: Whether to show aspect counts corner
        show_element_modality: Whether to show element/modality table corner
        title: Optional title for title page (None = no title page)
        filename: Output PDF filename
    """

    entries: list[AtlasEntry] = field(default_factory=list)
    page_size: str = "letter"
    theme: str = "classic"
    zodiac_palette: str = "rainbow"
    show_header: bool = True
    show_aspects: bool = True
    show_extended_tables: bool = False
    show_aspect_counts: bool = True
    show_element_modality: bool = True
    title: str | None = None
    filename: str = "atlas.pdf"
