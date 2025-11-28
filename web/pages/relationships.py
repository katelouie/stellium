"""
Stellium Web - Relationships Page

Chart types for comparing two people: Synastry, Composite, Davison.
"""

from components.chart_display import create_chart_actions, create_chart_display
from components.header import create_header, create_nav
from components.report_options import create_report_options
from config import (
    ASPECT_MODES,
    ASPECT_PALETTES,
    CHART_THEMES,
    COLORS,
    HOUSE_SYSTEMS,
    MOON_PHASE_POSITIONS,
    PLANET_GLYPH_PALETTES,
    TABLE_POSITIONS,
    ZODIAC_PALETTES,
)
from nicegui import ui
from state import ChartState, PDFReportState, RelationshipsState

# Stellium imports
from stellium import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.synthesis import SynthesisBuilder
from stellium.presentation import ReportBuilder
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


def create_person_input_form(state: ChartState, label: str, on_change=None):
    """Create a compact birth data input form for one person."""
    from components.birth_input_unified import create_unified_birth_input

    create_unified_birth_input(
        state=state,
        on_change=on_change,
        label=label.upper(),
        show_notable_toggle=True,
    )


def create_relationships_chart_options(state: RelationshipsState, on_change=None):
    """Create chart options specific to relationship charts."""

    def update_field(field: str, value):
        setattr(state, field, value)
        if on_change:
            on_change()

    with ui.element("div").classes("w-full"):
        # ===== HOUSE SYSTEM (for Composite/Davison) =====
        with (
            ui.expansion("House System", icon="home")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.label("For Composite & Davison charts:").classes("text-xs").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.select(
                    [name for name, _ in HOUSE_SYSTEMS],  # All house systems
                    value=state.house_system,
                    on_change=lambda e: update_field("house_system", e.value),
                ).classes("w-full")

        # ===== ASPECTS =====
        with (
            ui.expansion("Aspects", icon="hub")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-3 p-4"):
                ui.checkbox(
                    "Show Aspects",
                    value=state.include_aspects,
                    on_change=lambda e: update_field("include_aspects", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    state, "include_aspects", backward=lambda x: x
                ):
                    ui.label("Aspect Set:").classes("text-sm mt-2").style(
                        f"color: {COLORS['text_muted']}"
                    )
                    ui.select(
                        {code: name for name, code in ASPECT_MODES},
                        value=state.aspect_mode,
                        on_change=lambda e: update_field("aspect_mode", e.value),
                    ).classes("w-full")

        # ===== THEME & PALETTES =====
        with (
            ui.expansion("Theme & Palettes", icon="palette")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-3 p-4"):
                ui.label("Chart Theme").classes("text-sm").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.select(
                    CHART_THEMES,
                    value=state.theme,
                    on_change=lambda e: update_field("theme", e.value),
                ).classes("w-full")

                ui.label("Color Palettes").classes("text-sm mt-3").style(
                    f"color: {COLORS['text_muted']}"
                )
                with ui.element("div").classes("grid grid-cols-2 gap-x-4 gap-y-2"):
                    with ui.column().classes("gap-1"):
                        ui.label("Zodiac Ring").classes("text-xs").style(
                            f"color: {COLORS['accent']}"
                        )
                        ui.select(
                            ZODIAC_PALETTES,
                            value=state.zodiac_palette,
                            on_change=lambda e: update_field("zodiac_palette", e.value),
                        ).classes("w-full")

                    with ui.column().classes("gap-1"):
                        ui.label("Aspect Lines").classes("text-xs").style(
                            f"color: {COLORS['accent']}"
                        )
                        ui.select(
                            ASPECT_PALETTES,
                            value=state.aspect_palette,
                            on_change=lambda e: update_field("aspect_palette", e.value),
                        ).classes("w-full")

                    with ui.column().classes("gap-1"):
                        ui.label("Planet Glyphs").classes("text-xs").style(
                            f"color: {COLORS['accent']}"
                        )
                        ui.select(
                            {code: name for name, code in PLANET_GLYPH_PALETTES},
                            value=state.planet_glyph_palette,
                            on_change=lambda e: update_field(
                                "planet_glyph_palette", e.value
                            ),
                        ).classes("w-full")

                    with ui.column().classes("gap-1"):
                        ui.label("Sign Colors").classes("text-xs").style(
                            f"color: {COLORS['accent']}"
                        )
                        ui.checkbox(
                            "Color sign glyphs",
                            value=state.color_sign_info,
                            on_change=lambda e: update_field("color_sign_info", e.value),
                        ).props("dense")

        # ===== DISPLAY OPTIONS =====
        with (
            ui.expansion("Display Options", icon="visibility")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-3 p-4"):
                ui.checkbox(
                    "Show Header Band",
                    value=state.show_header,
                    on_change=lambda e: update_field("show_header", e.value),
                ).props("dense")

                # Moon Phase (more relevant for composite/davison)
                ui.checkbox(
                    "Show Moon Phase",
                    value=state.show_moon_phase,
                    on_change=lambda e: update_field("show_moon_phase", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    state, "show_moon_phase", backward=lambda x: x
                ):
                    with ui.row().classes("ml-6 gap-4 items-center"):
                        ui.select(
                            {code: name for name, code in MOON_PHASE_POSITIONS},
                            value=state.moon_phase_position,
                            on_change=lambda e: update_field(
                                "moon_phase_position", e.value
                            ),
                        ).classes("w-32")
                        ui.checkbox(
                            "Label",
                            value=state.moon_phase_show_label,
                            on_change=lambda e: update_field(
                                "moon_phase_show_label", e.value
                            ),
                        ).props("dense")

                # Info Corners
                ui.label("Info Corners").classes("text-sm mt-3").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.checkbox(
                    "Chart Info",
                    value=state.show_chart_info,
                    on_change=lambda e: update_field("show_chart_info", e.value),
                ).props("dense")
                ui.checkbox(
                    "Aspect Counts",
                    value=state.show_aspect_counts,
                    on_change=lambda e: update_field("show_aspect_counts", e.value),
                ).props("dense")

        # ===== TABLES =====
        with (
            ui.expansion("Tables (Extended View)", icon="table_chart")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-3 p-4"):
                ui.checkbox(
                    "Show Extended Tables",
                    value=state.show_tables,
                    on_change=lambda e: update_field("show_tables", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    state, "show_tables", backward=lambda x: x
                ):
                    ui.label("Table Position:").classes("text-sm mt-2").style(
                        f"color: {COLORS['text_muted']}"
                    )
                    ui.select(
                        {code: name for name, code in TABLE_POSITIONS},
                        value=state.table_position,
                        on_change=lambda e: update_field("table_position", e.value),
                    ).classes("w-full")


def create_relationships_page():
    """Create the relationships chart page."""

    # Page state
    state = RelationshipsState()
    report_state = PDFReportState()
    chart_svg: dict[str, str | None] = {"content": None}
    calculated_chart: dict[str, object | None] = {"ref": None}
    chart_container: dict[str, ui.element | None] = {"ref": None}
    actions_container: dict[str, ui.element | None] = {"ref": None}

    def build_chart():
        """Build chart from current state."""
        if not state.is_valid():
            ui.notify("Please fill in birth details for both people", type="warning")
            return

        try:
            p1 = state.person1
            p2 = state.person2

            dt1 = p1.date if p1.time_unknown else f"{p1.date} {p1.time}"
            dt2 = p2.date if p2.time_unknown else f"{p2.date} {p2.time}"

            # Build individual charts
            builder1 = ChartBuilder.from_details(dt1, p1.location, name=p1.name)
            if p1.time_unknown:
                builder1 = builder1.with_unknown_time()
            if state.include_aspects:
                builder1 = builder1.with_aspects()
            chart1 = builder1.calculate()

            builder2 = ChartBuilder.from_details(dt2, p2.location, name=p2.name)
            if p2.time_unknown:
                builder2 = builder2.with_unknown_time()
            if state.include_aspects:
                builder2 = builder2.with_aspects()
            chart2 = builder2.calculate()

            # Build comparison/synthesis based on chart type
            if state.chart_type == "synastry":
                comparison = ComparisonBuilder.synastry(
                    chart1,
                    chart2,
                    chart1_label=p1.name or "Person 1",
                    chart2_label=p2.name or "Person 2",
                ).calculate()
                calculated_chart["ref"] = comparison
                drawer = comparison.draw()

            elif state.chart_type == "composite":
                synthesis = SynthesisBuilder.composite(chart1, chart2).calculate()
                calculated_chart["ref"] = synthesis
                drawer = synthesis.draw()

            elif state.chart_type == "davison":
                synthesis = SynthesisBuilder.davison(chart1, chart2).calculate()
                calculated_chart["ref"] = synthesis
                drawer = synthesis.draw()

            else:
                ui.notify(f"Unknown chart type: {state.chart_type}", type="negative")
                return

            # Apply visualization options
            drawer = drawer.with_theme(state.theme)
            drawer = drawer.with_zodiac_palette(state.zodiac_palette)
            drawer = drawer.with_aspect_palette(state.aspect_palette)
            drawer = drawer.with_planet_glyph_palette(state.planet_glyph_palette)

            if state.color_sign_info:
                drawer = drawer.with_adaptive_colors(sign_info=True)

            if state.show_header:
                drawer = drawer.with_header()
            else:
                drawer = drawer.without_header()

            if state.show_moon_phase:
                drawer = drawer.with_moon_phase(
                    position=state.moon_phase_position,
                    show_label=state.moon_phase_show_label,
                )

            if state.show_chart_info:
                drawer = drawer.with_chart_info(position="top-left")
            if state.show_aspect_counts:
                drawer = drawer.with_aspect_counts(position="top-right")

            if state.show_tables:
                drawer = drawer.with_tables(position=state.table_position)

            chart_svg["content"] = drawer.save(to_string=True)
            refresh_chart_display()

            type_names = {"synastry": "Synastry", "composite": "Composite", "davison": "Davison"}
            ui.notify(f"{type_names[state.chart_type]} chart generated!", type="positive")

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

        if actions_container["ref"]:
            actions_container["ref"].clear()
            with actions_container["ref"]:
                create_chart_actions(
                    on_download_svg=download_svg,
                    on_download_pdf=download_pdf,
                    on_view_code=lambda: ui.notify("Code preview coming soon!"),
                    enabled=chart_svg["content"] is not None,
                )

    def download_svg():
        """Download the chart as an SVG file."""
        if chart_svg["content"]:
            p1_name = state.person1.name or "person1"
            p2_name = state.person2.name or "person2"
            name_part = f"{p1_name}_{p2_name}".replace(" ", "_").lower()
            filename = f"{name_part}_{state.chart_type}_chart.svg"
            ui.download(chart_svg["content"].encode("utf-8"), filename, "image/svg+xml")

    def download_pdf():
        """Generate and download the PDF report."""
        if not calculated_chart["ref"]:
            ui.notify("Please generate a chart first", type="warning")
            return

        try:
            chart = calculated_chart["ref"]
            rs = report_state

            # Build report
            builder = ReportBuilder().from_chart(chart)

            if rs.include_chart_overview:
                builder = builder.with_chart_overview()
            if rs.include_planet_positions:
                builder = builder.with_planet_positions()
            if rs.include_house_cusps:
                builder = builder.with_house_cusps()
            if rs.include_aspects:
                builder = builder.with_aspects(mode=rs.aspects_mode)

            # Generate filename
            p1_name = state.person1.name or "person1"
            p2_name = state.person2.name or "person2"
            name_part = f"{p1_name}_{p2_name}".replace(" ", "_").lower()
            filename = f"{name_part}_{state.chart_type}_report.pdf"

            import tempfile
            import os

            chart_svg_path = None
            if rs.include_chart_image and chart_svg["content"]:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
                    f.write(chart_svg["content"])
                    chart_svg_path = f.name

            try:
                with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as pdf_file:
                    pdf_path = pdf_file.name

                type_names = {"synastry": "Synastry", "composite": "Composite", "davison": "Davison"}
                title = f"{state.person1.name or 'Person 1'} & {state.person2.name or 'Person 2'} — {type_names[state.chart_type]}"

                builder.render(
                    format="pdf",
                    file=pdf_path,
                    show=False,
                    chart_svg_path=chart_svg_path,
                    title=title,
                )

                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                ui.download(pdf_bytes, filename, "application/pdf")
                ui.notify("PDF generated!", type="positive")
                os.unlink(pdf_path)

            finally:
                if chart_svg_path and os.path.exists(chart_svg_path):
                    os.unlink(chart_svg_path)

        except Exception as e:
            ui.notify(f"Error generating PDF: {str(e)}", type="negative")
            import traceback
            traceback.print_exc()

    def update_chart_type(value):
        state.chart_type = value

    # ===== PAGE LAYOUT =====

    create_header()
    create_nav()

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
                ui.label("Relationship Charts").classes(
                    "font-display text-3xl md:text-4xl tracking-wide"
                ).style(f"color: {COLORS['text']}")
                ui.label("Synastry, Composite & Davison").classes("text-base mt-2").style(
                    f"color: {COLORS['text_muted']}"
                )

            # Two column layout
            with ui.row().classes("w-full gap-8 flex-wrap lg:flex-nowrap"):
                # LEFT COLUMN: Forms and options
                with ui.column().classes("w-full lg:w-[420px] lg:flex-shrink-0 gap-6"):
                    # Chart type selector
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  CHART TYPE").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        ui.radio(
                            {
                                "synastry": "Synastry (Bi-wheel overlay)",
                                "composite": "Composite (Midpoint chart)",
                                "davison": "Davison (Time-space midpoint)",
                            },
                            value=state.chart_type,
                            on_change=lambda e: update_chart_type(e.value),
                        ).props("dense")

                    # Person 1 input
                    with (
                        ui.element("div")
                        .classes("w-full p-5 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        create_person_input_form(state.person1, "Person 1")

                    # Person 2 input
                    with (
                        ui.element("div")
                        .classes("w-full p-5 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        create_person_input_form(state.person2, "Person 2")

                    # Create chart button
                    ui.button("CREATE CHART", on_click=build_chart).classes(
                        "w-full py-4 text-sm tracking-[0.15em] rounded"
                    ).style(
                        f"background-color: {COLORS['primary']} !important; color: white !important;"
                    )

                    # Chart Options
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  CHART OPTIONS").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        create_relationships_chart_options(state, on_change=None)

                    # Report Options
                    with (
                        ui.element("div")
                        .classes("w-full p-4 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  REPORT OPTIONS").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        create_report_options(report_state, on_change=None)

                # RIGHT COLUMN: Chart display
                with ui.column().classes("w-full lg:flex-1 min-w-0"):
                    chart_container["ref"] = ui.element("div").classes("w-full")
                    with chart_container["ref"]:
                        create_chart_display(None)

                    actions_container["ref"] = ui.element("div").classes("w-full")
                    with actions_container["ref"]:
                        create_chart_actions(
                            on_download_svg=download_svg,
                            on_download_pdf=download_pdf,
                            on_view_code=lambda: ui.notify("Code preview coming soon!"),
                            enabled=False,
                        )
