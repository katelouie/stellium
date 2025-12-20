"""
Stellium Web - Planner Page

Generate personalized astrological planners with transits, moon phases, and more.
"""

from datetime import date, datetime

from components.birth_input_unified import create_unified_birth_input
from components.header import create_header, create_nav
from config import COLORS
from nicegui import ui
from state import PlannerState

# Common timezones for dropdown
COMMON_TIMEZONES = [
    ("America/Los_Angeles", "US Pacific (Los Angeles)"),
    ("America/Denver", "US Mountain (Denver)"),
    ("America/Chicago", "US Central (Chicago)"),
    ("America/New_York", "US Eastern (New York)"),
    ("Europe/London", "UK (London)"),
    ("Europe/Paris", "Central Europe (Paris)"),
    ("Europe/Berlin", "Central Europe (Berlin)"),
    ("Asia/Tokyo", "Japan (Tokyo)"),
    ("Asia/Shanghai", "China (Shanghai)"),
    ("Australia/Sydney", "Australia (Sydney)"),
]


def create_planner_page():
    """Create the planner generation page."""

    # Page state
    state = PlannerState()
    # Set default year to current year
    state.year = datetime.now().year

    def update_field(field: str, value):
        """Update a field on the state."""
        setattr(state, field, value)

    # Reference to loading dialog
    loading_dialog_ref: dict[str, ui.dialog | None] = {"dialog": None}

    async def generate_planner():
        """Generate the planner PDF."""
        if not state.is_valid():
            ui.notify("Please fill in all required fields", type="warning")
            return

        # Show loading dialog with spinner
        with ui.dialog() as loading_dialog, ui.card().classes("items-center p-8"):
            ui.spinner("dots", size="xl", color="primary")
            ui.label("Generating your planner...").classes("text-lg mt-4").style(
                f"color: {COLORS['text']}"
            )
            ui.label("This may take a minute or two.").classes("text-sm").style(
                f"color: {COLORS['text_muted']}"
            )

        loading_dialog_ref["dialog"] = loading_dialog
        loading_dialog.open()

        # Run the heavy computation in a background thread
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def build_planner():
            """Build the planner in a background thread."""
            from stellium import Native
            from stellium.planner import PlannerBuilder

            # Build the native from state
            if state.native.time_unknown:
                datetime_str = state.native.date
            else:
                datetime_str = f"{state.native.date} {state.native.time}"

            native = Native(datetime_str, state.native.location, name=state.native.name)

            # Start building planner
            builder = PlannerBuilder.for_native(native)

            # Date range
            if state.use_custom_range:
                start = date.fromisoformat(state.start_date)
                end = date.fromisoformat(state.end_date)
                builder = builder.date_range(start, end)
            else:
                builder = builder.year(state.year)

            # Timezone
            builder = builder.timezone(state.timezone)

            # Location (optional override)
            if state.use_custom_location and state.custom_location:
                builder = builder.location(state.custom_location)

            # Front matter
            builder = builder.with_natal_chart(state.include_natal_chart)
            builder = builder.with_progressed_chart(state.include_progressed_chart)
            builder = builder.with_solar_return(state.include_solar_return)
            builder = builder.with_profections(state.include_profections)
            builder = builder.with_zr_timeline(state.zr_lot, state.include_zr_timeline)
            builder = builder.with_graphic_ephemeris(
                state.graphic_ephemeris_harmonic, state.include_graphic_ephemeris
            )

            # Daily content
            if state.include_natal_transits:
                if state.natal_transit_planets == "outer":
                    builder = builder.include_natal_transits()  # Default outer planets
                elif state.natal_transit_planets == "all":
                    builder = builder.include_natal_transits(
                        [
                            "Sun",
                            "Moon",
                            "Mercury",
                            "Venus",
                            "Mars",
                            "Jupiter",
                            "Saturn",
                            "Uranus",
                            "Neptune",
                            "Pluto",
                        ]
                    )

            builder = builder.include_mundane_transits(state.include_mundane_transits)
            builder = builder.include_moon_phases(state.include_moon_phases)

            if state.include_voc:
                builder = builder.include_voc(state.voc_mode)
            else:
                builder = builder.exclude_voc()

            if state.include_ingresses:
                builder = builder.include_ingresses()
            if state.include_stations:
                builder = builder.include_stations()

            # Page layout
            builder = builder.page_size(state.page_size)
            builder = builder.binding_margin(state.binding_margin)
            builder = builder.week_starts_on(state.week_starts_on)

            # Generate PDF
            return builder.generate()

        try:
            # Run in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                pdf_bytes = await loop.run_in_executor(executor, build_planner)

            # Close loading dialog
            if loading_dialog_ref["dialog"]:
                loading_dialog_ref["dialog"].close()

            # Create filename
            name_part = (
                state.native.name.replace(" ", "_").lower()
                if state.native.name
                else "planner"
            )
            year_part = state.year if not state.use_custom_range else "custom"
            filename = f"{name_part}_{year_part}_planner.pdf"

            # Trigger download
            ui.download(pdf_bytes, filename, "application/pdf")
            ui.notify("Planner generated!", type="positive")

        except Exception as e:
            # Close loading dialog on error too
            if loading_dialog_ref["dialog"]:
                loading_dialog_ref["dialog"].close()

            ui.notify(f"Error: {str(e)}", type="negative")
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
        with ui.element("div").classes("w-full max-w-4xl mx-auto"):
            # Page title
            with ui.element("div").classes("w-full text-center mb-8"):
                ui.label("★  ☆  ★").classes("text-lg mb-4").style(
                    f"color: {COLORS['gold']}"
                )
                ui.label("Astrological Planner").classes(
                    "font-display text-3xl md:text-4xl tracking-wide"
                ).style(f"color: {COLORS['text']}")
                ui.label("Generate a personalized PDF planner").classes(
                    "text-base mt-2"
                ).style(f"color: {COLORS['text_muted']}")

            # Form sections
            with ui.column().classes("w-full gap-6"):
                # ===== BIRTH DATA SECTION =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    create_unified_birth_input(
                        state.native,
                        on_change=None,
                        label="BIRTH DETAILS",
                        show_notable_toggle=True,
                    )

                # ===== DATE RANGE SECTION =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    ui.label("☆  DATE RANGE").classes(
                        "font-display text-xs tracking-[0.2em] mb-4"
                    ).style(f"color: {COLORS['primary']}")

                    with ui.column().classes("gap-4 w-full"):
                        # Year vs custom range toggle
                        with ui.row().classes("items-center gap-4"):
                            ui.radio(
                                ["Full Year", "Custom Range"],
                                value="Full Year",
                                on_change=lambda e: update_field(
                                    "use_custom_range", e.value == "Custom Range"
                                ),
                            ).props("inline")

                        # Year selector (shown when not custom)
                        with ui.row().classes("items-center gap-4"):
                            ui.label("Year:").classes("w-24").style(
                                f"color: {COLORS['text']}"
                            )
                            ui.number(
                                value=state.year,
                                min=1900,
                                max=2100,
                                step=1,
                                on_change=lambda e: update_field("year", int(e.value)),
                            ).classes("w-32").props("dense")

                        # Custom date range (always visible but grayed when not used)
                        with ui.row().classes("items-center gap-4"):
                            ui.label("Start:").classes("w-24").style(
                                f"color: {COLORS['text_muted']}"
                            )
                            ui.input(
                                value=state.start_date,
                                placeholder="YYYY-MM-DD",
                                on_change=lambda e: update_field("start_date", e.value),
                            ).classes("w-40").props("dense")

                            ui.label("End:").classes("w-16 ml-4").style(
                                f"color: {COLORS['text_muted']}"
                            )
                            ui.input(
                                value=state.end_date,
                                placeholder="YYYY-MM-DD",
                                on_change=lambda e: update_field("end_date", e.value),
                            ).classes("w-40").props("dense")

                # ===== TIMEZONE SECTION =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    ui.label("☆  TIMEZONE").classes(
                        "font-display text-xs tracking-[0.2em] mb-4"
                    ).style(f"color: {COLORS['primary']}")

                    with ui.row().classes("items-center gap-4"):
                        ui.label("Timezone:").classes("w-24").style(
                            f"color: {COLORS['text']}"
                        )
                        ui.select(
                            options=dict(COMMON_TIMEZONES),
                            value=state.timezone,
                            on_change=lambda e: update_field("timezone", e.value),
                        ).classes("w-64")

                    ui.label(
                        "All transit times will be displayed in this timezone."
                    ).classes("text-sm mt-2").style(f"color: {COLORS['text_muted']}")

                # ===== FRONT MATTER OPTIONS =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    ui.label("☆  FRONT MATTER").classes(
                        "font-display text-xs tracking-[0.2em] mb-4"
                    ).style(f"color: {COLORS['primary']}")

                    ui.label(
                        "Charts and reference pages at the start of your planner."
                    ).classes("text-sm mb-4").style(f"color: {COLORS['text_muted']}")

                    with ui.column().classes("gap-2"):
                        ui.checkbox(
                            "Natal Chart",
                            value=state.include_natal_chart,
                            on_change=lambda e: update_field(
                                "include_natal_chart", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        ui.checkbox(
                            "Secondary Progressed Chart",
                            value=state.include_progressed_chart,
                            on_change=lambda e: update_field(
                                "include_progressed_chart", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        ui.checkbox(
                            "Solar Return Chart",
                            value=state.include_solar_return,
                            on_change=lambda e: update_field(
                                "include_solar_return", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        ui.checkbox(
                            "Profections (Lord of the Year)",
                            value=state.include_profections,
                            on_change=lambda e: update_field(
                                "include_profections", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        with ui.row().classes("items-center gap-2"):
                            ui.checkbox(
                                "Zodiacal Releasing Timeline",
                                value=state.include_zr_timeline,
                                on_change=lambda e: update_field(
                                    "include_zr_timeline", e.value
                                ),
                            ).style(f"color: {COLORS['text']}")
                            ui.select(
                                options=["Part of Fortune", "Part of Spirit"],
                                value=state.zr_lot,
                                on_change=lambda e: update_field("zr_lot", e.value),
                            ).classes("w-40").props("dense")

                        with ui.row().classes("items-center gap-2"):
                            ui.checkbox(
                                "Graphic Ephemeris",
                                value=state.include_graphic_ephemeris,
                                on_change=lambda e: update_field(
                                    "include_graphic_ephemeris", e.value
                                ),
                            ).style(f"color: {COLORS['text']}")
                            ui.select(
                                options={
                                    360: "Full Zodiac (360°)",
                                    90: "90° Dial",
                                    45: "45° Dial",
                                },
                                value=state.graphic_ephemeris_harmonic,
                                on_change=lambda e: update_field(
                                    "graphic_ephemeris_harmonic", e.value
                                ),
                            ).classes("w-40").props("dense")

                # ===== DAILY CONTENT OPTIONS =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    ui.label("☆  DAILY CONTENT").classes(
                        "font-display text-xs tracking-[0.2em] mb-4"
                    ).style(f"color: {COLORS['primary']}")

                    ui.label("What to include in your daily/weekly pages.").classes(
                        "text-sm mb-4"
                    ).style(f"color: {COLORS['text_muted']}")

                    with ui.column().classes("gap-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.checkbox(
                                "Transits to Natal Planets",
                                value=state.include_natal_transits,
                                on_change=lambda e: update_field(
                                    "include_natal_transits", e.value
                                ),
                            ).style(f"color: {COLORS['text']}")
                            ui.select(
                                options={
                                    "outer": "Outer planets only",
                                    "all": "All planets",
                                },
                                value=state.natal_transit_planets,
                                on_change=lambda e: update_field(
                                    "natal_transit_planets", e.value
                                ),
                            ).classes("w-44").props("dense")

                        ui.checkbox(
                            "Mundane Transits (planet-to-planet in sky)",
                            value=state.include_mundane_transits,
                            on_change=lambda e: update_field(
                                "include_mundane_transits", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        ui.checkbox(
                            "Moon Phases (new, full, quarters)",
                            value=state.include_moon_phases,
                            on_change=lambda e: update_field(
                                "include_moon_phases", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        with ui.row().classes("items-center gap-2"):
                            ui.checkbox(
                                "Void of Course Moon",
                                value=state.include_voc,
                                on_change=lambda e: update_field(
                                    "include_voc", e.value
                                ),
                            ).style(f"color: {COLORS['text']}")
                            ui.select(
                                options={
                                    "traditional": "Traditional (Sun-Saturn)",
                                    "modern": "Modern (includes outers)",
                                },
                                value=state.voc_mode,
                                on_change=lambda e: update_field("voc_mode", e.value),
                            ).classes("w-52").props("dense")

                        ui.checkbox(
                            "Sign Ingresses",
                            value=state.include_ingresses,
                            on_change=lambda e: update_field(
                                "include_ingresses", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                        ui.checkbox(
                            "Retrograde/Direct Stations",
                            value=state.include_stations,
                            on_change=lambda e: update_field(
                                "include_stations", e.value
                            ),
                        ).style(f"color: {COLORS['text']}")

                # ===== PAGE LAYOUT OPTIONS =====
                with (
                    ui.element("div")
                    .classes("w-full p-6 rounded-lg")
                    .style(f"background-color: {COLORS['cream_dark']};")
                ):
                    ui.label("☆  PAGE LAYOUT").classes(
                        "font-display text-xs tracking-[0.2em] mb-4"
                    ).style(f"color: {COLORS['primary']}")

                    with ui.column().classes("gap-4"):
                        with ui.row().classes("items-center gap-4"):
                            ui.label("Page Size:").classes("w-32").style(
                                f"color: {COLORS['text']}"
                            )
                            ui.select(
                                options={
                                    "a4": "A4",
                                    "a5": "A5 (Half A4)",
                                    "letter": "US Letter",
                                },
                                value=state.page_size,
                                on_change=lambda e: update_field("page_size", e.value),
                            ).classes("w-40")

                        with ui.row().classes("items-center gap-4"):
                            ui.label("Week Starts On:").classes("w-32").style(
                                f"color: {COLORS['text']}"
                            )
                            ui.select(
                                options={"sunday": "Sunday", "monday": "Monday"},
                                value=state.week_starts_on,
                                on_change=lambda e: update_field(
                                    "week_starts_on", e.value
                                ),
                            ).classes("w-40")

                        with ui.row().classes("items-center gap-4"):
                            ui.label("Binding Margin:").classes("w-32").style(
                                f"color: {COLORS['text']}"
                            )
                            ui.number(
                                value=state.binding_margin,
                                min=0,
                                max=1,
                                step=0.125,
                                suffix=" inches",
                                on_change=lambda e: update_field(
                                    "binding_margin", e.value
                                ),
                            ).classes("w-40").props("dense")

                # ===== GENERATE BUTTON =====
                ui.button(
                    "GENERATE PLANNER",
                    on_click=generate_planner,
                ).classes("w-full py-4 text-sm tracking-[0.15em] rounded").style(
                    f"background-color: {COLORS['primary']} !important; color: white !important;"
                )

    # Footer
    with (
        ui.element("footer")
        .classes("w-full py-6 px-6 border-t")
        .style(
            f"border-color: {COLORS['border']}; background-color: {COLORS['cream']};"
        )
    ):
        with ui.element("div").classes("w-full max-w-5xl mx-auto text-center"):
            ui.label("★  Generated with Stellium  ★").classes("text-sm").style(
                f"color: {COLORS['text_muted']}"
            )
