"""
Stellium Web - Report Options Component

Expandable panels for PDF report section selection and configuration.
Designed to sit below the chart options in the left column.
"""

from config import ASPECT_MODES, COLORS
from i18n import wt
from nicegui import ui
from state import PDFReportState


def create_report_options(report_state: PDFReportState, on_change=None):
    """
    Create the report configuration options panels.

    Args:
        report_state: PDFReportState instance to bind to
        on_change: Optional callback when any option changes
    """
    _ = wt()

    def update_field(field: str, value):
        setattr(report_state, field, value)
        if on_change:
            on_change()

    with ui.element("div").classes("w-full"):
        # ===== CORE SECTIONS =====
        with (
            ui.expansion(_("Report Sections"), icon="article", value=True)
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.checkbox(
                    _("Chart Overview"),
                    value=report_state.include_chart_overview,
                    on_change=lambda e: update_field("include_chart_overview", e.value),
                ).props("dense")

                ui.checkbox(
                    _("Moon Phase"),
                    value=report_state.include_moon_phase,
                    on_change=lambda e: update_field("include_moon_phase", e.value),
                ).props("dense")

                ui.checkbox(
                    _("Planet Positions"),
                    value=report_state.include_planet_positions,
                    on_change=lambda e: update_field(
                        "include_planet_positions", e.value
                    ),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_planet_positions", backward=lambda x: x
                ):
                    with ui.row().classes("ml-6 gap-4"):
                        ui.checkbox(
                            _("Speed (℞)"),
                            value=report_state.positions_include_speed,
                            on_change=lambda e: update_field(
                                "positions_include_speed", e.value
                            ),
                        ).props("dense")
                        ui.checkbox(
                            _("Houses"),
                            value=report_state.positions_include_house,
                            on_change=lambda e: update_field(
                                "positions_include_house", e.value
                            ),
                        ).props("dense")

                ui.checkbox(
                    _("House Cusps"),
                    value=report_state.include_house_cusps,
                    on_change=lambda e: update_field("include_house_cusps", e.value),
                ).props("dense")

                ui.checkbox(
                    _("Declinations"),
                    value=report_state.include_declinations,
                    on_change=lambda e: update_field("include_declinations", e.value),
                ).props("dense")

                ui.checkbox(
                    _("Include Chart Image"),
                    value=report_state.include_chart_image,
                    on_change=lambda e: update_field("include_chart_image", e.value),
                ).props("dense")

        # ===== ASPECTS SECTION =====
        with (
            ui.expansion(_("Aspects in Report"), icon="hub")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.checkbox(
                    _("Aspects Table"),
                    value=report_state.include_aspects,
                    on_change=lambda e: update_field("include_aspects", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_aspects", backward=lambda x: x
                ):
                    with ui.row().classes("ml-6 gap-2 items-center"):
                        ui.select(
                            {code: name for name, code in ASPECT_MODES},
                            value=report_state.aspects_mode,
                            on_change=lambda e: update_field("aspects_mode", e.value),
                        ).classes("w-36")
                        ui.checkbox(
                            _("Orbs"),
                            value=report_state.aspects_show_orbs,
                            on_change=lambda e: update_field(
                                "aspects_show_orbs", e.value
                            ),
                        ).props("dense")

                    ui.label(_("Sort by:")).classes("text-xs ml-6 mt-1").style(
                        f"color: {COLORS['text_muted']}"
                    )
                    ui.select(
                        {
                            "orb": _("Tightest First"),
                            "planet": _("By Planet"),
                            "aspect_type": _("By Aspect Type"),
                        },
                        value=report_state.aspects_sort_by,
                        on_change=lambda e: update_field("aspects_sort_by", e.value),
                    ).classes("w-36 ml-6")

                ui.checkbox(
                    _("Aspect Patterns"),
                    value=report_state.include_aspect_patterns,
                    on_change=lambda e: update_field(
                        "include_aspect_patterns", e.value
                    ),
                ).props("dense")
                ui.label(_("Grand Trines, T-Squares, Yods, etc.")).classes(
                    "text-xs ml-6 -mt-1"
                ).style(f"color: {COLORS['accent']}")

        # ===== DIGNITIES SECTION =====
        with (
            ui.expansion(_("Dignities in Report"), icon="star")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.checkbox(
                    _("Essential Dignities"),
                    value=report_state.include_dignities,
                    on_change=lambda e: update_field("include_dignities", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_dignities", backward=lambda x: x
                ):
                    ui.select(
                        {
                            "both": _("Traditional & Modern"),
                            "traditional": _("Traditional Only"),
                            "modern": _("Modern Only"),
                        },
                        value=report_state.dignities_system,
                        on_change=lambda e: update_field("dignities_system", e.value),
                    ).classes("w-44 ml-6")

                    ui.checkbox(
                        _("Show Details"),
                        value=report_state.dignities_show_details,
                        on_change=lambda e: update_field(
                            "dignities_show_details", e.value
                        ),
                    ).props("dense").classes("ml-6")

        # ===== MIDPOINTS SECTION =====
        with (
            ui.expansion(_("Midpoints in Report"), icon="commit")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.checkbox(
                    _("Midpoints Table"),
                    value=report_state.include_midpoints,
                    on_change=lambda e: update_field("include_midpoints", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_midpoints", backward=lambda x: x
                ):
                    ui.select(
                        {
                            "all": _("All Midpoints"),
                            "core": _("Core (Sun/Moon/ASC/MC)"),
                        },
                        value=report_state.midpoints_mode,
                        on_change=lambda e: update_field("midpoints_mode", e.value),
                    ).classes("w-44 ml-6")

                ui.checkbox(
                    _("Midpoint Aspects"),
                    value=report_state.include_midpoint_aspects,
                    on_change=lambda e: update_field(
                        "include_midpoint_aspects", e.value
                    ),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_midpoint_aspects", backward=lambda x: x
                ):
                    with ui.row().classes("ml-6 gap-2 items-center"):
                        ui.select(
                            {
                                "conjunction": _("Conjunctions"),
                                "hard": _("Hard Aspects"),
                                "all": _("All Aspects"),
                            },
                            value=report_state.midpoint_aspects_mode,
                            on_change=lambda e: update_field(
                                "midpoint_aspects_mode", e.value
                            ),
                        ).classes("w-32")
                        ui.number(
                            value=report_state.midpoint_aspects_orb,
                            min=0.5,
                            max=5.0,
                            step=0.5,
                            format="%.1f°",
                            on_change=lambda e: update_field(
                                "midpoint_aspects_orb", e.value
                            ),
                        ).classes("w-20")

        # ===== FIXED STARS SECTION =====
        with (
            ui.expansion(_("Fixed Stars in Report"), icon="auto_awesome")
            .classes("w-full")
            .props('header-class="text-sm font-medium"')
        ):
            with ui.column().classes("gap-2 p-4"):
                ui.checkbox(
                    _("Fixed Stars Table"),
                    value=report_state.include_fixed_stars,
                    on_change=lambda e: update_field("include_fixed_stars", e.value),
                ).props("dense")

                with ui.element("div").bind_visibility_from(
                    report_state, "include_fixed_stars", backward=lambda x: x
                ):
                    ui.select(
                        {
                            "royal": _("Royal Stars (4)"),
                            "major": _("Major Stars (15)"),
                            "all": _("All Stars (26)"),
                        },
                        value=report_state.fixed_stars_tier,
                        on_change=lambda e: update_field("fixed_stars_tier", e.value),
                    ).classes("w-36 ml-6")

                    ui.checkbox(
                        _("Include Keywords"),
                        value=report_state.fixed_stars_include_keywords,
                        on_change=lambda e: update_field(
                            "fixed_stars_include_keywords", e.value
                        ),
                    ).props("dense").classes("ml-6")
