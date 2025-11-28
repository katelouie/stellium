"""
Stellium Web - Timing Page

Chart types for forecasting: Transits, Progressions, and Returns.
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
    RETURN_PLANETS,
    TABLE_POSITIONS,
    TIMING_CHART_TYPES,
    ZODIAC_PALETTES,
)
from nicegui import ui
from state import ChartState, PDFReportState, TimingState

# Stellium imports
from stellium import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
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
from stellium.presentation import ReportBuilder
from stellium.returns import ReturnBuilder
from stellium.utils.progressions import calculate_progressed_datetime

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


def create_natal_input_form(state: ChartState, on_change=None):
    """Create birth data input form for the natal chart."""
    from components.birth_input_unified import create_unified_birth_input

    create_unified_birth_input(
        state=state,
        on_change=on_change,
        label="BIRTH DATA",
        show_notable_toggle=True,
    )


def create_timing_options(state: TimingState, on_change=None):
    """Create timing-specific options based on chart type."""
    from components.location_input import create_location_input

    def update_field(field: str, value):
        setattr(state, field, value)
        if on_change:
            on_change()

    def on_relocation_change(value: str):
        """Update relocation location in state."""
        update_field("relocation_location", value)

    with ui.element("div").classes("w-full"):
        # Timing date/year input (context-sensitive label)
        def get_timing_label():
            if state.chart_type == "transits":
                return "Transit Date:"
            elif state.chart_type == "progressions":
                return "Progress To:"
            elif state.chart_type == "solar_return":
                return "Return Year:"
            elif state.chart_type == "lunar_return":
                return "Near Date:"
            elif state.chart_type == "planetary_return":
                return "Near Date:"
            return "Date:"

        def get_timing_placeholder():
            if state.chart_type == "solar_return":
                return "YYYY"
            return "YYYY-MM-DD"

        with ui.row().classes("items-center gap-3 w-full mb-4"):
            ui.label(get_timing_label()).classes("w-28 flex-shrink-0 text-sm").style(
                f"color: {COLORS['text']}"
            )
            ui.input(
                value=state.timing_date,
                placeholder=get_timing_placeholder(),
                on_change=lambda e: update_field("timing_date", e.value),
            ).classes("minimal-input flex-grow").props("borderless dense")

        # Planetary return: planet selector
        if state.chart_type == "planetary_return":
            with ui.column().classes("gap-3 mb-4"):
                ui.label("Return Planet:").classes("text-sm").style(
                    f"color: {COLORS['text_muted']}"
                )
                ui.select(
                    dict(RETURN_PLANETS),
                    value=state.return_planet,
                    on_change=lambda e: update_field("return_planet", e.value),
                ).classes("w-full")

        # Relocation option (for returns)
        if state.chart_type in ("solar_return", "lunar_return", "planetary_return"):
            ui.checkbox(
                "Relocate return chart",
                value=state.relocate,
                on_change=lambda e: update_field("relocate", e.value),
            ).props("dense").classes("mb-2")

            with ui.element("div").bind_visibility_from(
                state, "relocate", backward=lambda x: x
            ):
                with ui.row().classes("items-center gap-3 w-full"):
                    ui.label("Location:").classes("w-20 flex-shrink-0 text-sm").style(
                        f"color: {COLORS['text']}"
                    )
                    with ui.element("div").classes("flex-grow"):
                        create_location_input(
                            value=state.relocation_location,
                            placeholder="City, Country",
                            on_change=on_relocation_change,
                        )


def create_timing_chart_options(state: TimingState, on_change=None):
    """Create chart options for timing charts."""

    def update_field(field: str, value):
        setattr(state, field, value)
        if on_change:
            on_change()

    with ui.element("div").classes("w-full"):
        # ===== HOUSE SYSTEM =====
        with (
            ui.expansion("House System", icon="home")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
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


def create_timing_page():
    """Create the timing/forecasts page."""

    # Page state
    state = TimingState()
    report_state = PDFReportState()
    chart_svg: dict[str, str | None] = {"content": None}
    calculated_chart: dict[str, object | None] = {"ref": None}
    chart_container: dict[str, ui.element | None] = {"ref": None}
    actions_container: dict[str, ui.element | None] = {"ref": None}
    timing_options_container: dict[str, ui.element | None] = {"ref": None}

    def refresh_timing_options():
        """Refresh timing-specific options when chart type changes."""
        if timing_options_container["ref"]:
            timing_options_container["ref"].clear()
            with timing_options_container["ref"]:
                create_timing_options(state, on_change=None)

    def build_chart():
        """Build chart from current state."""
        natal = state.natal
        if not natal.is_valid():
            ui.notify("Please fill in natal birth details", type="warning")
            return

        if not state.timing_date and state.chart_type not in ("lunar_return", "planetary_return"):
            ui.notify("Please enter a date or year", type="warning")
            return

        try:
            # Build natal chart first
            natal_dt = natal.date if natal.time_unknown else f"{natal.date} {natal.time}"
            natal_builder = ChartBuilder.from_details(natal_dt, natal.location, name=natal.name)

            if natal.time_unknown:
                natal_builder = natal_builder.with_unknown_time()

            # Add house system
            if state.house_system in HOUSE_SYSTEM_MAP:
                natal_builder = natal_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

            if state.include_aspects:
                natal_builder = natal_builder.with_aspects()

            natal_chart = natal_builder.calculate()

            # Now build based on chart type
            if state.chart_type == "transits":
                # Build transit chart for the specified date
                transit_builder = ChartBuilder.from_details(
                    state.timing_date,
                    natal.location,  # Use natal location for transits
                    name=f"Transits - {state.timing_date}"
                )

                if state.house_system in HOUSE_SYSTEM_MAP:
                    transit_builder = transit_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

                if state.include_aspects:
                    transit_builder = transit_builder.with_aspects()

                transit_chart = transit_builder.calculate()

                # Create bi-wheel comparison
                comparison = ComparisonBuilder.synastry(
                    natal_chart,
                    transit_chart,
                    chart1_label=natal.name or "Natal",
                    chart2_label="Transits",
                ).calculate()

                calculated_chart["ref"] = comparison
                drawer = comparison.draw()

            elif state.chart_type == "progressions":
                # Calculate progressed datetime
                from dateutil.parser import parse
                natal_datetime = parse(natal_dt)
                target_date = parse(state.timing_date)

                progressed_datetime = calculate_progressed_datetime(natal_datetime, target_date)

                # Build progressed chart
                progressed_builder = ChartBuilder.from_details(
                    progressed_datetime,
                    natal.location,
                    name=f"{natal.name or 'Chart'} - Progressed to {state.timing_date}"
                )

                if state.house_system in HOUSE_SYSTEM_MAP:
                    progressed_builder = progressed_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

                if state.include_aspects:
                    progressed_builder = progressed_builder.with_aspects()

                progressed_chart = progressed_builder.calculate()

                # Show as bi-wheel with natal
                comparison = ComparisonBuilder.synastry(
                    natal_chart,
                    progressed_chart,
                    chart1_label=natal.name or "Natal",
                    chart2_label="Progressed",
                ).calculate()

                calculated_chart["ref"] = comparison
                drawer = comparison.draw()

            elif state.chart_type == "solar_return":
                # Solar Return for specified year
                year = int(state.timing_date)

                return_builder = ReturnBuilder.solar(
                    natal_chart,
                    year,
                    location=state.relocation_location if state.relocate else None,
                )

                if state.house_system in HOUSE_SYSTEM_MAP:
                    return_builder = return_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

                if state.include_aspects:
                    return_builder = return_builder.with_aspects()

                return_chart = return_builder.calculate()
                calculated_chart["ref"] = return_chart
                drawer = return_chart.draw()

            elif state.chart_type == "lunar_return":
                # Lunar Return near specified date (or now if not specified)
                near_date = state.timing_date if state.timing_date else None

                return_builder = ReturnBuilder.lunar(
                    natal_chart,
                    near_date=near_date,
                    location=state.relocation_location if state.relocate else None,
                )

                if state.house_system in HOUSE_SYSTEM_MAP:
                    return_builder = return_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

                if state.include_aspects:
                    return_builder = return_builder.with_aspects()

                return_chart = return_builder.calculate()
                calculated_chart["ref"] = return_chart
                drawer = return_chart.draw()

            elif state.chart_type == "planetary_return":
                # Planetary Return
                near_date = state.timing_date if state.timing_date else None

                return_builder = ReturnBuilder.planetary(
                    natal_chart,
                    state.return_planet,
                    near_date=near_date,
                    location=state.relocation_location if state.relocate else None,
                )

                if state.house_system in HOUSE_SYSTEM_MAP:
                    return_builder = return_builder.with_house_systems([HOUSE_SYSTEM_MAP[state.house_system]()])

                if state.include_aspects:
                    return_builder = return_builder.with_aspects()

                return_chart = return_builder.calculate()
                calculated_chart["ref"] = return_chart
                drawer = return_chart.draw()

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

            type_names = {
                "transits": "Transit",
                "progressions": "Progressed",
                "solar_return": "Solar Return",
                "lunar_return": "Lunar Return",
                "planetary_return": f"{state.return_planet} Return"
            }
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
            name_part = state.natal.name.replace(" ", "_").lower() if state.natal.name else "chart"
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
            name_part = state.natal.name.replace(" ", "_").lower() if state.natal.name else "chart"
            filename = f"{name_part}_{state.chart_type}_report.pdf"

            import os
            import tempfile

            chart_svg_path = None
            if rs.include_chart_image and chart_svg["content"]:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
                    f.write(chart_svg["content"])
                    chart_svg_path = f.name

            try:
                with tempfile.NamedTemporaryFile(mode="wb", suffix=".pdf", delete=False) as pdf_file:
                    pdf_path = pdf_file.name

                type_names = {
                    "transits": "Transits",
                    "progressions": "Secondary Progressions",
                    "solar_return": "Solar Return",
                    "lunar_return": "Lunar Return",
                    "planetary_return": f"{state.return_planet} Return"
                }
                title = f"{state.natal.name or 'Chart'} - {type_names[state.chart_type]}"

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
        refresh_timing_options()

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
                ui.label("Timing & Forecasts").classes(
                    "font-display text-3xl md:text-4xl tracking-wide"
                ).style(f"color: {COLORS['text']}")
                ui.label("Transits, Progressions & Returns").classes("text-base mt-2").style(
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
                            {code: name for code, name, desc in TIMING_CHART_TYPES},
                            value=state.chart_type,
                            on_change=lambda e: update_chart_type(e.value),
                        ).props("dense")

                        # Description for selected type
                        with ui.element("div").classes("mt-2 ml-6"):
                            desc_map = {code: desc for code, name, desc in TIMING_CHART_TYPES}
                            ui.label(desc_map.get(state.chart_type, "")).classes("text-xs").style(
                                f"color: {COLORS['text_muted']}"
                            )

                    # Natal birth data input
                    with (
                        ui.element("div")
                        .classes("w-full p-5 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        create_natal_input_form(state.natal)

                    # Timing-specific options (changes based on chart type)
                    with (
                        ui.element("div")
                        .classes("w-full p-5 rounded-lg")
                        .style(f"background-color: {COLORS['cream_dark']};")
                    ):
                        ui.label("☆  TIMING OPTIONS").classes(
                            "font-display text-xs tracking-[0.2em] mb-4"
                        ).style(f"color: {COLORS['primary']}")

                        timing_options_container["ref"] = ui.element("div").classes("w-full")
                        with timing_options_container["ref"]:
                            create_timing_options(state, on_change=None)

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

                        create_timing_chart_options(state, on_change=None)

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
