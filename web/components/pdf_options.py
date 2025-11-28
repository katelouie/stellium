"""
Stellium Web - PDF Report Options Dialog

Dialog for configuring PDF report generation with section selection
and detailed options for each section.
"""

from config import ASPECT_MODES, COLORS
from nicegui import ui
from state import PDFReportState


def create_pdf_options_dialog(
    report_state: PDFReportState,
    on_generate: callable,
):
    """
    Create a dialog for PDF report options.

    Args:
        report_state: PDFReportState instance to bind to
        on_generate: Callback when user clicks Generate PDF
    """

    def update_field(field: str, value):
        setattr(report_state, field, value)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl max-h-[90vh]"):
        # Header
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("☆  PDF REPORT OPTIONS").classes(
                "font-display text-sm tracking-[0.2em]"
            ).style(f"color: {COLORS['primary']}")
            ui.button(icon="close", on_click=dialog.close).props("flat dense")

        ui.label(
            "Select which sections to include in your PDF report. "
            "Options are pre-filled based on your chart settings."
        ).classes("text-sm mb-4").style(f"color: {COLORS['text_muted']}")

        # Scrollable content area
        with ui.scroll_area().classes("w-full").style("max-height: 60vh;"):
            with ui.element("div").classes("w-full pr-4"):
                # ===== CORE SECTIONS =====
                with (
                    ui.expansion("Core Sections", icon="article", value=True)
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Chart Overview",
                            value=report_state.include_chart_overview,
                            on_change=lambda e: update_field(
                                "include_chart_overview", e.value
                            ),
                        ).props("dense")
                        ui.label("Name, birth data, location, coordinates").classes(
                            "text-xs ml-6 -mt-1"
                        ).style(f"color: {COLORS['accent']}")

                        ui.checkbox(
                            "Moon Phase",
                            value=report_state.include_moon_phase,
                            on_change=lambda e: update_field(
                                "include_moon_phase", e.value
                            ),
                        ).props("dense")

                        ui.checkbox(
                            "Include Chart Image",
                            value=report_state.include_chart_image,
                            on_change=lambda e: update_field(
                                "include_chart_image", e.value
                            ),
                        ).props("dense")
                        ui.label("Embed the SVG chart in the PDF").classes(
                            "text-xs ml-6 -mt-1"
                        ).style(f"color: {COLORS['accent']}")

                # ===== POSITIONS SECTION =====
                with (
                    ui.expansion("Planet Positions", icon="public", value=True)
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Include Planet Positions Table",
                            value=report_state.include_planet_positions,
                            on_change=lambda e: update_field(
                                "include_planet_positions", e.value
                            ),
                        ).props("dense")

                        with ui.element("div").bind_visibility_from(
                            report_state,
                            "include_planet_positions",
                            backward=lambda x: x,
                        ):
                            with ui.row().classes("ml-6 gap-4"):
                                ui.checkbox(
                                    "Show Speed (℞)",
                                    value=report_state.positions_include_speed,
                                    on_change=lambda e: update_field(
                                        "positions_include_speed", e.value
                                    ),
                                ).props("dense")
                                ui.checkbox(
                                    "Show House",
                                    value=report_state.positions_include_house,
                                    on_change=lambda e: update_field(
                                        "positions_include_house", e.value
                                    ),
                                ).props("dense")

                        ui.checkbox(
                            "Include House Cusps Table",
                            value=report_state.include_house_cusps,
                            on_change=lambda e: update_field(
                                "include_house_cusps", e.value
                            ),
                        ).props("dense")

                        ui.checkbox(
                            "Include Declinations",
                            value=report_state.include_declinations,
                            on_change=lambda e: update_field(
                                "include_declinations", e.value
                            ),
                        ).props("dense")
                        ui.label("Equatorial coordinates, out-of-bounds detection").classes(
                            "text-xs ml-6 -mt-1"
                        ).style(f"color: {COLORS['accent']}")

                # ===== ASPECTS SECTION =====
                with (
                    ui.expansion("Aspects", icon="hub")
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Include Aspects Table",
                            value=report_state.include_aspects,
                            on_change=lambda e: update_field("include_aspects", e.value),
                        ).props("dense")

                        with ui.element("div").bind_visibility_from(
                            report_state, "include_aspects", backward=lambda x: x
                        ):
                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Mode:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {code: name for name, code in ASPECT_MODES},
                                    value=report_state.aspects_mode,
                                    on_change=lambda e: update_field(
                                        "aspects_mode", e.value
                                    ),
                                ).classes("w-40")

                            with ui.row().classes("ml-6 gap-4"):
                                ui.checkbox(
                                    "Show Orbs",
                                    value=report_state.aspects_show_orbs,
                                    on_change=lambda e: update_field(
                                        "aspects_show_orbs", e.value
                                    ),
                                ).props("dense")

                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Sort by:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {
                                        "orb": "Tightest First",
                                        "planet": "By Planet",
                                        "aspect_type": "By Aspect Type",
                                    },
                                    value=report_state.aspects_sort_by,
                                    on_change=lambda e: update_field(
                                        "aspects_sort_by", e.value
                                    ),
                                ).classes("w-40")

                        ui.checkbox(
                            "Include Aspect Patterns",
                            value=report_state.include_aspect_patterns,
                            on_change=lambda e: update_field(
                                "include_aspect_patterns", e.value
                            ),
                        ).props("dense")
                        ui.label("Grand Trines, T-Squares, Yods, Stelliums").classes(
                            "text-xs ml-6 -mt-1"
                        ).style(f"color: {COLORS['accent']}")

                # ===== DIGNITIES SECTION =====
                with (
                    ui.expansion("Essential Dignities", icon="star")
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Include Dignities Table",
                            value=report_state.include_dignities,
                            on_change=lambda e: update_field(
                                "include_dignities", e.value
                            ),
                        ).props("dense")

                        with ui.element("div").bind_visibility_from(
                            report_state, "include_dignities", backward=lambda x: x
                        ):
                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("System:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {
                                        "both": "Traditional & Modern",
                                        "traditional": "Traditional Only",
                                        "modern": "Modern Only",
                                    },
                                    value=report_state.dignities_system,
                                    on_change=lambda e: update_field(
                                        "dignities_system", e.value
                                    ),
                                ).classes("w-48")

                            ui.checkbox(
                                "Show Details (dignity names)",
                                value=report_state.dignities_show_details,
                                on_change=lambda e: update_field(
                                    "dignities_show_details", e.value
                                ),
                            ).props("dense").classes("ml-6")

                # ===== MIDPOINTS SECTION =====
                with (
                    ui.expansion("Midpoints", icon="commit")
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Include Midpoints Table",
                            value=report_state.include_midpoints,
                            on_change=lambda e: update_field(
                                "include_midpoints", e.value
                            ),
                        ).props("dense")

                        with ui.element("div").bind_visibility_from(
                            report_state, "include_midpoints", backward=lambda x: x
                        ):
                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Mode:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {
                                        "all": "All Midpoints",
                                        "core": "Core Only (Sun/Moon/ASC/MC)",
                                    },
                                    value=report_state.midpoints_mode,
                                    on_change=lambda e: update_field(
                                        "midpoints_mode", e.value
                                    ),
                                ).classes("w-56")

                        ui.checkbox(
                            "Include Midpoint Aspects",
                            value=report_state.include_midpoint_aspects,
                            on_change=lambda e: update_field(
                                "include_midpoint_aspects", e.value
                            ),
                        ).props("dense")
                        ui.label("Planets activating midpoints (conjunctions)").classes(
                            "text-xs ml-6 -mt-1"
                        ).style(f"color: {COLORS['accent']}")

                        with ui.element("div").bind_visibility_from(
                            report_state,
                            "include_midpoint_aspects",
                            backward=lambda x: x,
                        ):
                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Aspect type:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {
                                        "conjunction": "Conjunctions Only",
                                        "hard": "Hard Aspects",
                                        "all": "All Major Aspects",
                                    },
                                    value=report_state.midpoint_aspects_mode,
                                    on_change=lambda e: update_field(
                                        "midpoint_aspects_mode", e.value
                                    ),
                                ).classes("w-44")

                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Max orb:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.number(
                                    value=report_state.midpoint_aspects_orb,
                                    min=0.5,
                                    max=5.0,
                                    step=0.5,
                                    format="%.1f°",
                                    on_change=lambda e: update_field(
                                        "midpoint_aspects_orb", e.value
                                    ),
                                ).classes("w-24")

                # ===== FIXED STARS SECTION =====
                with (
                    ui.expansion("Fixed Stars", icon="auto_awesome")
                    .classes("w-full")
                    .props('header-class="text-sm font-medium"')
                ):
                    with ui.column().classes("gap-2 p-4"):
                        ui.checkbox(
                            "Include Fixed Stars Table",
                            value=report_state.include_fixed_stars,
                            on_change=lambda e: update_field(
                                "include_fixed_stars", e.value
                            ),
                        ).props("dense")

                        with ui.element("div").bind_visibility_from(
                            report_state, "include_fixed_stars", backward=lambda x: x
                        ):
                            with ui.row().classes("ml-6 gap-4 items-center"):
                                ui.label("Stars to include:").classes("text-sm").style(
                                    f"color: {COLORS['text_muted']}"
                                )
                                ui.select(
                                    {
                                        "royal": "Royal Stars (4)",
                                        "major": "Major Stars (15)",
                                        "all": "All Stars (26)",
                                    },
                                    value=report_state.fixed_stars_tier,
                                    on_change=lambda e: update_field(
                                        "fixed_stars_tier", e.value
                                    ),
                                ).classes("w-40")

                            ui.checkbox(
                                "Include Keywords",
                                value=report_state.fixed_stars_include_keywords,
                                on_change=lambda e: update_field(
                                    "fixed_stars_include_keywords", e.value
                                ),
                            ).props("dense").classes("ml-6")

        # Footer with action buttons
        with ui.row().classes("w-full justify-end gap-2 mt-4 pt-4").style(
            f"border-top: 1px solid {COLORS['border']}"
        ):
            ui.button("Cancel", on_click=dialog.close).props("outline").style(
                f"color: {COLORS['text_muted']} !important; border-color: {COLORS['border']} !important;"
            )

            ui.button(
                "Generate PDF",
                icon="picture_as_pdf",
                on_click=lambda: (on_generate(), dialog.close()),
            ).style(
                f"background-color: {COLORS['primary']} !important; color: white !important;"
            )

    return dialog
