"""
Stellium Web - Code Preview Component

Shows the equivalent Python code for the current chart and report configuration.
"""

from config import COLORS
from nicegui import ui
from state import ChartState, PDFReportState


def generate_python_code(state: ChartState, report_state: PDFReportState) -> str:
    """Generate Python code that reproduces the current chart and report configuration."""

    lines = [
        "from stellium import ChartBuilder",
    ]

    # Imports based on options
    imports = []
    if len(state.house_systems) > 0:
        # Note: Import from stellium.engines.houses for all house systems
        house_imports = [
            f"{hs.replace(' ', '').replace('(', '').replace(')', '')}Houses"
            for hs in state.house_systems
        ]
        imports.append(f"from stellium.engines.houses import {', '.join(house_imports)}")

    components = []
    if state.include_dignities:
        components.append("DignityComponent")
    if state.include_midpoints:
        components.append("MidpointCalculator")
    if state.include_arabic_parts:
        components.append("ArabicPartsCalculator")
    if state.include_fixed_stars:
        components.append("FixedStarsComponent")
    if components:
        imports.append(f"from stellium.components import {', '.join(components)}")

    if state.include_patterns:
        imports.append("from stellium.engines.patterns import AspectPatternAnalyzer")

    # Add report import
    imports.append("from stellium.presentation import ReportBuilder")

    lines.extend(imports)
    lines.append("")

    # Build the chart
    datetime_str = f"{state.date} {state.time}" if state.time else state.date
    name_part = f', name="{state.name}"' if state.name else ""
    lines.append(
        f'chart = (ChartBuilder.from_details("{datetime_str}", "{state.location}"{name_part})'
    )

    # House systems
    if state.house_systems:
        hs_list = [
            f"{hs.replace(' ', '').replace('(', '').replace(')', '')}Houses()"
            for hs in state.house_systems
        ]
        lines.append(f"    .with_house_systems([{', '.join(hs_list)}])")

    # Sidereal
    if state.zodiac_type == "sidereal":
        lines.append(f'    .with_sidereal("{state.ayanamsa}")')

    # Time unknown
    if state.time_unknown:
        lines.append("    .with_unknown_time()")

    # Aspects
    if state.include_aspects:
        lines.append("    .with_aspects()")

    # Components
    if state.include_dignities:
        lines.append("    .add_component(DignityComponent())")
    if state.include_midpoints:
        lines.append("    .add_component(MidpointCalculator())")
    if state.include_arabic_parts:
        lines.append("    .add_component(ArabicPartsCalculator())")
    if state.include_fixed_stars:
        if state.fixed_stars_mode == "royal":
            lines.append("    .add_component(FixedStarsComponent(royal_only=True))")
        elif state.fixed_stars_mode == "major":
            lines.append(
                "    .add_component(FixedStarsComponent(tier=2, include_higher_tiers=True))"
            )
        else:
            lines.append("    .add_component(FixedStarsComponent())")
    if state.include_patterns:
        lines.append("    .add_analyzer(AspectPatternAnalyzer())")

    lines.append("    .calculate())")
    lines.append("")

    # Visualization
    lines.append("# Generate chart visualization")
    lines.append('(chart.draw("my_chart.svg")')
    lines.append(f'    .with_theme("{state.theme}")')
    lines.append(f'    .with_zodiac_palette("{state.zodiac_palette}")')
    lines.append(f'    .with_aspect_palette("{state.aspect_palette}")')
    lines.append(f'    .with_planet_glyph_palette("{state.planet_glyph_palette}")')
    if state.color_sign_info:
        lines.append("    .with_adaptive_colors(sign_info=True)")

    # Show multiple house systems on chart wheel
    if len(state.house_systems) > 1:
        lines.append(f"    .with_house_systems({state.house_systems})")
    elif state.house_systems:
        lines.append(f'    .with_house_systems("{state.house_systems[0]}")')

    if state.show_header:
        lines.append("    .with_header()")
    else:
        lines.append("    .without_header()")

    if state.show_moon_phase:
        lines.append(
            f'    .with_moon_phase(position="{state.moon_phase_position}", '
            f"show_label={state.moon_phase_show_label})"
        )

    if state.show_chart_info:
        lines.append('    .with_chart_info(position="top-left")')
    if state.show_aspect_counts:
        lines.append('    .with_aspect_counts(position="top-right")')
    if state.show_element_modality:
        lines.append('    .with_element_modality_table(position="bottom-left")')

    if state.show_tables:
        lines.append(
            f'    .with_tables(position="{state.table_position}", '
            f"show_position_table={state.table_show_positions}, "
            f"show_house_cusps={state.table_show_houses}, "
            f"show_aspectarian={state.table_show_aspectarian})"
        )

    lines.append("    .save())")
    lines.append("")

    # Generate report code
    lines.append("# Generate PDF report")
    lines.append("report = ReportBuilder().from_chart(chart)")

    rs = report_state
    if rs.include_chart_overview:
        lines.append("report = report.with_chart_overview()")

    if rs.include_moon_phase:
        lines.append("report = report.with_moon_phase()")

    if rs.include_planet_positions:
        lines.append(
            f"report = report.with_planet_positions("
            f"include_speed={rs.positions_include_speed}, "
            f"include_house={rs.positions_include_house})"
        )

    if rs.include_declinations:
        lines.append("report = report.with_declinations()")

    if rs.include_house_cusps:
        lines.append("report = report.with_house_cusps()")

    if rs.include_aspects:
        lines.append(
            f'report = report.with_aspects(mode="{rs.aspects_mode}", '
            f"orbs={rs.aspects_show_orbs}, "
            f'sort_by="{rs.aspects_sort_by}")'
        )

    if rs.include_aspect_patterns:
        lines.append("report = report.with_aspect_patterns()")

    if rs.include_dignities:
        lines.append(
            f'report = report.with_dignities(essential="{rs.dignities_system}", '
            f"show_details={rs.dignities_show_details})"
        )

    if rs.include_midpoints:
        lines.append(f'report = report.with_midpoints(mode="{rs.midpoints_mode}")')

    if rs.include_midpoint_aspects:
        lines.append(
            f'report = report.with_midpoint_aspects(mode="{rs.midpoint_aspects_mode}", '
            f"orb={rs.midpoint_aspects_orb}, "
            f'midpoint_filter="{rs.midpoint_aspects_filter}")'
        )

    if rs.include_fixed_stars:
        tier_map = {"royal": "1", "major": "2", "all": "None"}
        tier_str = tier_map.get(rs.fixed_stars_tier, "None")
        lines.append(
            f"report = report.with_fixed_stars(tier={tier_str}, "
            f"include_keywords={rs.fixed_stars_include_keywords})"
        )

    lines.append("")
    lines.append("# Render to PDF")
    if rs.include_chart_image:
        lines.append(
            'report.render(format="pdf", file="report.pdf", chart_svg_path="my_chart.svg")'
        )
    else:
        lines.append('report.render(format="pdf", file="report.pdf")')

    return "\n".join(lines)


def create_code_preview_dialog(state: ChartState, report_state: PDFReportState):
    """Create a dialog showing the Python code."""

    code = generate_python_code(state, report_state)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl max-h-[90vh]"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("☆  PYTHON CODE").classes(
                "font-display text-sm tracking-[0.2em]"
            ).style(f"color: {COLORS['primary']}")
            ui.button(icon="close", on_click=dialog.close).props("flat dense")

        ui.label(
            "Copy this code to reproduce your chart and report with Stellium:"
        ).classes("text-sm mb-4").style(f"color: {COLORS['text_muted']}")

        # Scrollable code block
        with ui.scroll_area().classes("w-full").style("max-height: 60vh;"):
            ui.code(code, language="python").classes("w-full")

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button(
                "Copy to Clipboard",
                icon="content_copy",
                on_click=lambda: ui.notify(
                    "Copied!", type="positive"
                ),  # TODO: actual clipboard
            ).style(
                f"background-color: {COLORS['primary']} !important; color: white !important;"
            )

            ui.button("Close", on_click=dialog.close).props("outline").style(
                f"color: {COLORS['text_muted']} !important; border-color: {COLORS['border']} !important;"
            )

    return dialog
