"""
Stellium Web - Natal Chart Page

The main chart building experience.
"""

from components.birth_input import create_birth_input_form
from components.chart_display import create_chart_actions, create_chart_display
from components.chart_options import create_chart_options
from components.code_preview import create_natal_code_preview_dialog
from components.header import create_header, create_nav
from components.report_options import create_report_options
from config import COLORS
from nicegui import ui
from state import ChartState, PDFReportState

# Stellium imports
from stellium import ChartBuilder
from stellium.components import (
    ArabicPartsCalculator,
    DignityComponent,
    FixedStarsComponent,
    MidpointCalculator,
)
from stellium.engines.houses import (
    AlcabitiusHouses,
    APCHouses,
    AxialRotationHouses,
    CampanusHouses,
    EqualHouses,
    EqualMCHouses,
    EqualVertexHouses,
    GauquelinHouses,
    HorizontalHouses,
    KochHouses,
    KrusinskiHouses,
    MorinusHouses,
    PlacidusHouses,
    PorphyryHouses,
    RegiomontanusHouses,
    TopocentricHouses,
    VehlowEqualHouses,
    WholeSignHouses,
)
from stellium.engines.patterns import AspectPatternAnalyzer
from stellium.presentation import ReportBuilder

# House system mapping (all 18 systems)
HOUSE_SYSTEM_MAP = {
    # Popular
    "Placidus": PlacidusHouses,
    "Whole Sign": WholeSignHouses,
    "Koch": KochHouses,
    "Equal": EqualHouses,
    # Traditional
    "Porphyry": PorphyryHouses,
    "Regiomontanus": RegiomontanusHouses,
    "Campanus": CampanusHouses,
    "Alcabitius": AlcabitiusHouses,
    # Modern
    "Topocentric": TopocentricHouses,
    "Morinus": MorinusHouses,
    "Krusinski": KrusinskiHouses,
    # Equal variants
    "Equal (MC)": EqualMCHouses,
    "Vehlow Equal": VehlowEqualHouses,
    "Equal (Vertex)": EqualVertexHouses,
    # Specialized
    "Gauquelin": GauquelinHouses,
    "Horizontal": HorizontalHouses,
    "Axial Rotation": AxialRotationHouses,
    "APC": APCHouses,
}


def create_natal_page():
    """Create the natal chart page."""

    # Page state
    state = ChartState()
    report_state = PDFReportState()  # Report options - always available
    chart_svg: dict[str, str | None] = {"content": None}
    calculated_chart: dict[str, object | None] = {
        "ref": None
    }  # Store the CalculatedChart
    chart_container: dict[str, ui.element | None] = {"ref": None}
    actions_container: dict[str, ui.element | None] = {"ref": None}

    def build_chart():
        """Build chart from current state."""
        if not state.is_valid():
            ui.notify("Please fill in all required fields", type="warning")
            return

        try:
            # Build datetime string
            if state.time_unknown:
                datetime_str = state.date
            else:
                datetime_str = f"{state.date} {state.time}"

            # Start building
            builder = ChartBuilder.from_details(
                datetime_str, state.location, name=state.name
            )

            # House systems
            if state.house_systems:
                houses = [
                    HOUSE_SYSTEM_MAP[hs]()
                    for hs in state.house_systems
                    if hs in HOUSE_SYSTEM_MAP
                ]
                if houses:
                    builder = builder.with_house_systems(houses)

            # Zodiac
            if state.zodiac_type == "sidereal":
                builder = builder.with_sidereal(state.ayanamsa)

            # Time unknown
            if state.time_unknown:
                builder = builder.with_unknown_time()

            # Aspects
            if state.include_aspects:
                builder = builder.with_aspects()

            # Components
            if state.include_dignities:
                builder = builder.add_component(DignityComponent())
            if state.include_midpoints:
                builder = builder.add_component(MidpointCalculator())
            if state.include_arabic_parts:
                builder = builder.add_component(ArabicPartsCalculator())
            if state.include_fixed_stars:
                # Configure fixed stars based on mode
                if state.fixed_stars_mode == "royal":
                    builder = builder.add_component(
                        FixedStarsComponent(royal_only=True)
                    )
                elif state.fixed_stars_mode == "major":
                    builder = builder.add_component(
                        FixedStarsComponent(tier=2, include_higher_tiers=True)
                    )
                else:  # all
                    builder = builder.add_component(FixedStarsComponent())
            if state.include_patterns:
                builder = builder.add_analyzer(AspectPatternAnalyzer())

            # Calculate
            chart = builder.calculate()

            # Store for PDF generation
            calculated_chart["ref"] = chart

            # Build visualization
            drawer = chart.draw()
            drawer = drawer.with_theme(state.theme)
            drawer = drawer.with_zodiac_palette(state.zodiac_palette)
            drawer = drawer.with_aspect_palette(state.aspect_palette)
            drawer = drawer.with_planet_glyph_palette(state.planet_glyph_palette)
            if state.color_sign_info:
                drawer = drawer.with_adaptive_colors(sign_info=True)

            # Show all selected house systems on the chart wheel
            if len(state.house_systems) > 1:
                drawer = drawer.with_house_systems(state.house_systems)
            elif state.house_systems:
                drawer = drawer.with_house_systems(state.house_systems[0])

            # Header
            if state.show_header:
                drawer = drawer.with_header()
            else:
                drawer = drawer.without_header()

            # Moon phase
            if state.show_moon_phase:
                drawer = drawer.with_moon_phase(
                    position=state.moon_phase_position,
                    show_label=state.moon_phase_show_label,
                )

            # Info corners
            if state.show_chart_info:
                drawer = drawer.with_chart_info(position="top-left")
            if state.show_aspect_counts:
                drawer = drawer.with_aspect_counts(position="top-right")
            if state.show_element_modality:
                drawer = drawer.with_element_modality_table(position="bottom-left")

            # Tables
            if state.show_tables:
                drawer = drawer.with_tables(
                    position=state.table_position,
                    show_position_table=state.table_show_positions,
                    show_house_cusps=state.table_show_houses,
                    show_aspectarian=state.table_show_aspectarian,
                )

            # Get SVG string
            chart_svg["content"] = drawer.save(to_string=True)

            # Update display
            refresh_chart_display()

            ui.notify("Chart generated!", type="positive")

        except Exception as e:
            ui.notify(f"Error: {str(e)}", type="negative")
            import traceback

            traceback.print_exc()

    def refresh_chart_display():
        """Refresh the chart display area and action buttons."""
        if chart_container["ref"]:
            chart_container["ref"].clear()
            with chart_container["ref"]:
                create_chart_display(chart_svg["content"])

        # Also refresh action buttons to enable them
        if actions_container["ref"]:
            actions_container["ref"].clear()
            with actions_container["ref"]:
                create_chart_actions(
                    on_download_svg=download_svg,
                    on_download_pdf=download_pdf,
                    on_view_code=show_code,
                    enabled=chart_svg["content"] is not None,
                )

    def download_svg():
        """Download the chart as an SVG file."""
        if chart_svg["content"]:
            # Generate filename from name or default
            name_part = state.name.replace(" ", "_").lower() if state.name else "chart"
            filename = f"{name_part}_natal_chart.svg"

            # Trigger download
            ui.download(chart_svg["content"].encode("utf-8"), filename, "image/svg+xml")

    def show_code():
        """Show the Python code dialog."""
        dialog = create_natal_code_preview_dialog(state, report_state)
        dialog.open()

    def sync_report_state_from_chart():
        """Sync report state options based on chart state settings."""
        # Update report state to match chart calculations
        report_state.include_aspects = state.include_aspects
        report_state.include_aspect_patterns = state.include_patterns
        report_state.include_dignities = state.include_dignities
        report_state.include_midpoints = state.include_midpoints
        report_state.include_midpoint_aspects = state.include_midpoints
        report_state.include_fixed_stars = state.include_fixed_stars
        report_state.include_declinations = state.include_declinations
        report_state.aspects_mode = state.aspect_mode
        report_state.fixed_stars_tier = state.fixed_stars_mode

    def download_pdf():
        """Generate and download the PDF report."""
        if not calculated_chart["ref"]:
            ui.notify("Please generate a chart first", type="warning")
            return

        try:
            chart = calculated_chart["ref"]
            rs = report_state

            # Build the report
            builder = ReportBuilder().from_chart(chart)

            # Add sections based on report state
            if rs.include_chart_overview:
                builder = builder.with_chart_overview()

            if rs.include_moon_phase:
                builder = builder.with_moon_phase()

            if rs.include_planet_positions:
                builder = builder.with_planet_positions(
                    include_speed=rs.positions_include_speed,
                    include_house=rs.positions_include_house,
                )

            if rs.include_declinations:
                builder = builder.with_declinations()

            if rs.include_house_cusps:
                builder = builder.with_house_cusps()

            if rs.include_aspects:
                builder = builder.with_aspects(
                    mode=rs.aspects_mode,
                    orbs=rs.aspects_show_orbs,
                    sort_by=rs.aspects_sort_by,
                )

            if rs.include_aspect_patterns:
                builder = builder.with_aspect_patterns()

            if rs.include_dignities:
                builder = builder.with_dignities(
                    essential=rs.dignities_system,
                    show_details=rs.dignities_show_details,
                )

            if rs.include_midpoints:
                builder = builder.with_midpoints(mode=rs.midpoints_mode)

            if rs.include_midpoint_aspects:
                builder = builder.with_midpoint_aspects(
                    mode=rs.midpoint_aspects_mode,
                    orb=rs.midpoint_aspects_orb,
                    midpoint_filter=rs.midpoint_aspects_filter,
                )

            if rs.include_fixed_stars:
                # Convert tier string to int or None
                tier_map = {"royal": 1, "major": 2, "all": None}
                tier = tier_map.get(rs.fixed_stars_tier)
                builder = builder.with_fixed_stars(
                    tier=tier,
                    include_keywords=rs.fixed_stars_include_keywords,
                )

            # Generate filename
            name_part = state.name.replace(" ", "_").lower() if state.name else "chart"
            filename = f"{name_part}_natal_report.pdf"

            # For PDF with chart image, we need to save SVG to temp file
            import os
            import tempfile

            chart_svg_path = None
            if rs.include_chart_image and chart_svg["content"]:
                # Create temp SVG file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".svg", delete=False
                ) as f:
                    f.write(chart_svg["content"])
                    chart_svg_path = f.name

            try:
                # Configure builder with chart image and title
                title = (
                    f"{state.name} — Natal Chart"
                    if state.name
                    else "Natal Chart Report"
                )
                if chart_svg_path:
                    builder = builder.with_chart_image(chart_svg_path)
                builder = builder.with_title(title)

                # Generate PDF to temp file
                with tempfile.NamedTemporaryFile(
                    mode="wb", suffix=".pdf", delete=False
                ) as pdf_file:
                    pdf_path = pdf_file.name

                builder.render(
                    format="pdf",
                    file=pdf_path,
                    show=False,
                )

                # Read PDF bytes and trigger download
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                ui.download(pdf_bytes, filename, "application/pdf")
                ui.notify("PDF generated!", type="positive")

                # Clean up temp PDF
                os.unlink(pdf_path)

            finally:
                # Clean up temp SVG
                if chart_svg_path and os.path.exists(chart_svg_path):
                    os.unlink(chart_svg_path)

        except Exception as e:
            ui.notify(f"Error generating PDF: {str(e)}", type="negative")
            import traceback

            traceback.print_exc()

    # ===== PAGE LAYOUT =====

    create_header()
    create_nav()

    # Main content
    with (
        ui.element("main")
        .classes("w-full min-h-screen py-8 px-6")
        .style(f"background-color: {COLORS['cream']}")
    ):
        with ui.element("div").classes("w-full max-w-7xl mx-auto"):
            # Page title
            with ui.element("div").classes("w-full text-center mb-8"):
                ui.label("★  ☆  ★").classes("text-lg mb-4").style(
                    f"color: {COLORS['gold']}"
                )
                ui.label("Create Your Birth Chart").classes(
                    "font-display text-3xl md:text-4xl tracking-wide"
                ).style(f"color: {COLORS['text']}")
                ui.label("Natal Chart & Report").classes("text-base mt-2").style(
                    f"color: {COLORS['text_muted']}"
                )

            # Two column layout using flexbox
            with ui.row().classes("w-full gap-8 flex-wrap lg:flex-nowrap"):
                # LEFT COLUMN: Form and options (narrower)
                with ui.column().classes("w-full lg:w-[420px] lg:flex-shrink-0 gap-6"):
                    # Birth data card
                    with (
                        ui.element("div")
                        .classes("w-full p-6 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        create_birth_input_form(state, on_change=None)

                        # Create chart button
                        ui.button("CREATE CHART", on_click=build_chart).classes(
                            "w-full mt-6 py-4 text-sm tracking-[0.15em] rounded"
                        ).style(
                            f"background-color: {COLORS['primary']} !important; color: white !important;"
                        )

                    # Chart Options accordion
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  CHART OPTIONS").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        create_chart_options(
                            state, on_change=sync_report_state_from_chart
                        )

                    # Report Options accordion
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  REPORT OPTIONS").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        create_report_options(report_state, on_change=None)

                # RIGHT COLUMN: Chart display (grows to fill space)
                with ui.column().classes("w-full lg:flex-1 min-w-0"):
                    chart_container["ref"] = ui.element("div").classes("w-full")
                    with chart_container["ref"]:
                        create_chart_display(None)

                    actions_container["ref"] = ui.element("div").classes("w-full")
                    with actions_container["ref"]:
                        create_chart_actions(
                            on_download_svg=download_svg,
                            on_download_pdf=download_pdf,
                            on_view_code=show_code,
                            enabled=False,  # Enable when chart is generated
                        )
