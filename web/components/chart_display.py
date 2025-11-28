"""
Stellium Web - Chart Display Component

Displays the generated SVG chart and provides download options.
"""

import re

from config import COLORS
from nicegui import ui


def make_svg_responsive(svg_content: str) -> tuple[str, float]:
    """
    Make SVG responsive by removing fixed dimensions and extracting aspect ratio.

    Returns:
        Tuple of (modified SVG string, aspect ratio as height/width)
    """
    # Extract dimensions from viewBox (more reliable than width/height attributes)
    viewbox_match = re.search(r'viewBox=["\'](\d+)\s+(\d+)\s+(\d+)\s+(\d+)["\']', svg_content)

    if viewbox_match:
        # viewBox format: "minX minY width height"
        vb_width = int(viewbox_match.group(3))
        vb_height = int(viewbox_match.group(4))
        aspect_ratio = vb_height / vb_width
    else:
        # Fallback: try to get from width/height attributes
        width_match = re.search(r'width=["\'](\d+)', svg_content)
        height_match = re.search(r'height=["\'](\d+)', svg_content)

        if width_match and height_match:
            width = int(width_match.group(1))
            height = int(height_match.group(1))
            aspect_ratio = height / width
        else:
            aspect_ratio = 1.0  # Default to square

    # Remove fixed width and height, replace with 100%
    # This allows the SVG to scale responsively while viewBox maintains aspect ratio
    modified_svg = re.sub(r'width=["\']\d+px?["\']', 'width="100%"', svg_content)
    modified_svg = re.sub(r'height=["\']\d+px?["\']', 'height="100%"', modified_svg)

    return modified_svg, aspect_ratio


def create_chart_display(svg_content: str | None = None, is_loading: bool = False):
    """
    Create the chart display area.

    Args:
        svg_content: The SVG string to display, or None for placeholder
        is_loading: Whether a chart is currently being generated
    """

    if is_loading:
        # Loading state - square placeholder with spinner
        with (
            ui.element("div")
            .classes(
                "w-full aspect-square max-w-2xl mx-auto flex items-center justify-center rounded-lg"
            )
            .style(
                f"background-color: {COLORS['cream_dark']}; border: 1px solid {COLORS['border']};"
            )
        ):
            ui.spinner("dots", size="xl").style(f"color: {COLORS['primary']}")

    elif svg_content:
        # Chart generated - make SVG responsive
        responsive_svg, aspect_ratio = make_svg_responsive(svg_content)
        padding_percent = aspect_ratio * 100

        with (
            ui.element("div")
            .classes("w-full mx-auto rounded-lg overflow-hidden")
            .style(
                f"background-color: {COLORS['cream_dark']}; border: 1px solid {COLORS['border']};"
            )
        ):
            # Responsive container that maintains aspect ratio using padding trick
            with (
                ui.element("div")
                .classes("relative w-full")
                .style(f"padding-bottom: {padding_percent}%;")
            ):
                # SVG fills the container absolutely positioned
                ui.html(responsive_svg, sanitize=False).classes(
                    "absolute inset-0 w-full h-full"
                ).style("display: block;")

    else:
        # Placeholder - square with hint text
        with (
            ui.element("div")
            .classes(
                "w-full aspect-square max-w-2xl mx-auto flex items-center justify-center rounded-lg"
            )
            .style(
                f"background-color: {COLORS['cream_dark']}; border: 1px solid {COLORS['border']};"
            )
        ):
            with ui.column().classes("items-center gap-4"):
                ui.label("★").classes("text-6xl").style(
                    f"color: {COLORS['gold']}; opacity: 0.3;"
                )
                ui.label("Your chart will appear here").classes("text-lg").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.label("Fill in your birth details and click Create Chart").classes(
                    "text-sm"
                ).style(f"color: {COLORS['accent']}")


def create_chart_actions(
    on_download_svg=None, on_download_pdf=None, on_view_code=None, enabled: bool = False
):
    """
    Create action buttons for the chart.

    Args:
        on_download_svg: Callback for SVG download
        on_download_pdf: Callback for PDF download
        on_view_code: Callback for viewing Python code
        enabled: Whether buttons should be enabled
    """

    with ui.row().classes("gap-4 justify-center mt-6"):
        ui.button("Download SVG", icon="download", on_click=on_download_svg).props(
            "outline"
        ).classes("text-sm").style(
            f"color: {COLORS['primary']} !important; border-color: {COLORS['primary']} !important;"
        ).set_enabled(enabled)

        ui.button(
            "Download PDF", icon="picture_as_pdf", on_click=on_download_pdf
        ).props("outline").classes("text-sm").style(
            f"color: {COLORS['primary']} !important; border-color: {COLORS['primary']} !important;"
        ).set_enabled(enabled)

        ui.button("View as Python", icon="code", on_click=on_view_code).props(
            "outline"
        ).classes("text-sm").style(
            f"color: {COLORS['gold']} !important; border-color: {COLORS['gold']} !important;"
        ).set_enabled(enabled)
