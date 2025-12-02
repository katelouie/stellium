"""
Stellium Web - Code Preview Component

Shows the equivalent Python code for the current chart and report configuration.
Supports Natal, Relationships (synastry/composite/davison), and Timing charts.
"""

from config import COLORS
from nicegui import ui
from state import ChartState, PDFReportState, RelationshipsState, TimingState


def generate_natal_code(state: ChartState, report_state: PDFReportState) -> str:
    """Generate Python code for a natal chart and report."""

    lines = [
        "from stellium import ChartBuilder, ReportBuilder",
    ]

    # Imports based on options
    imports = []
    if len(state.house_systems) > 0:
        house_imports = [
            f"{hs.replace(' ', '').replace('(', '').replace(')', '')}Houses"
            for hs in state.house_systems
        ]
        imports.append(
            f"from stellium.engines.houses import {', '.join(house_imports)}"
        )

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
    lines.append("(ReportBuilder().from_chart(chart)")

    rs = report_state
    if rs.include_chart_overview:
        lines.append("    .with_chart_overview()")

    if rs.include_moon_phase:
        lines.append("    .with_moon_phase()")

    if rs.include_planet_positions:
        lines.append(
            f"    .with_planet_positions("
            f"include_speed={rs.positions_include_speed}, "
            f"include_house={rs.positions_include_house})"
        )

    if rs.include_declinations:
        lines.append("    .with_declinations()")

    if rs.include_house_cusps:
        lines.append("    .with_house_cusps()")

    if rs.include_aspects:
        lines.append(
            f'    .with_aspects(mode="{rs.aspects_mode}", '
            f"orbs={rs.aspects_show_orbs}, "
            f'sort_by="{rs.aspects_sort_by}")'
        )

    if rs.include_aspect_patterns:
        lines.append("    .with_aspect_patterns()")

    if rs.include_dignities:
        lines.append(
            f'    .with_dignities(essential="{rs.dignities_system}", '
            f"show_details={rs.dignities_show_details})"
        )

    if rs.include_midpoints:
        lines.append(f'    .with_midpoints(mode="{rs.midpoints_mode}")')

    if rs.include_midpoint_aspects:
        lines.append(
            f'    .with_midpoint_aspects(mode="{rs.midpoint_aspects_mode}", '
            f"orb={rs.midpoint_aspects_orb}, "
            f'midpoint_filter="{rs.midpoint_aspects_filter}")'
        )

    if rs.include_fixed_stars:
        tier_map = {"royal": "1", "major": "2", "all": "None"}
        tier_str = tier_map.get(rs.fixed_stars_tier, "None")
        lines.append(
            f"    .with_fixed_stars(tier={tier_str}, "
            f"include_keywords={rs.fixed_stars_include_keywords})"
        )

    # Use new API
    if rs.include_chart_image:
        lines.append('    .with_chart_image("my_chart.svg")')

    title = f"{state.name} - Natal Chart" if state.name else "Natal Chart Report"
    lines.append(f'    .with_title("{title}")')
    lines.append('    .render(format="pdf", file="report.pdf"))')

    return "\n".join(lines)


def generate_relationships_code(
    state: RelationshipsState, report_state: PDFReportState
) -> str:
    """Generate Python code for relationship charts (synastry, composite, davison)."""

    lines = ["from stellium import ChartBuilder, ReportBuilder"]

    # Add appropriate imports based on chart type
    if state.chart_type == "synastry":
        lines.append("from stellium.core.comparison import ComparisonBuilder")
    else:
        lines.append("from stellium.core.synthesis import SynthesisBuilder")

    if state.house_system != "Placidus":
        hs_class = state.house_system.replace(" ", "").replace("(", "").replace(")", "")
        lines.append(f"from stellium.engines.houses import {hs_class}Houses")

    lines.append("")

    p1 = state.person1
    p2 = state.person2

    # Build person 1 chart
    dt1 = p1.date if p1.time_unknown else f"{p1.date} {p1.time}"
    name1 = p1.name or "Person 1"
    lines.append(f"# Build chart for {name1}")
    lines.append(
        f'chart1 = (ChartBuilder.from_details("{dt1}", "{p1.location}", name="{name1}")'
    )
    if p1.time_unknown:
        lines.append("    .with_unknown_time()")
    if state.include_aspects:
        lines.append("    .with_aspects()")
    lines.append("    .calculate())")
    lines.append("")

    # Build person 2 chart
    dt2 = p2.date if p2.time_unknown else f"{p2.date} {p2.time}"
    name2 = p2.name or "Person 2"
    lines.append(f"# Build chart for {name2}")
    lines.append(
        f'chart2 = (ChartBuilder.from_details("{dt2}", "{p2.location}", name="{name2}")'
    )
    if p2.time_unknown:
        lines.append("    .with_unknown_time()")
    if state.include_aspects:
        lines.append("    .with_aspects()")
    lines.append("    .calculate())")
    lines.append("")

    # Build relationship chart based on type
    if state.chart_type == "synastry":
        lines.append("# Create synastry comparison (bi-wheel)")
        lines.append("comparison = (ComparisonBuilder.synastry(chart1, chart2,")
        lines.append(f'    chart1_label="{name1}",')
        lines.append(f'    chart2_label="{name2}")')
        lines.append("    .calculate())")
        lines.append("")
        lines.append("# Generate bi-wheel chart")
        lines.append('comparison.draw("synastry_chart.svg")')
    elif state.chart_type == "composite":
        lines.append("# Create composite chart (midpoint method)")
        lines.append(
            "composite = SynthesisBuilder.composite(chart1, chart2).calculate()"
        )
        lines.append("")
        lines.append("# Generate composite chart")
        lines.append('composite.draw("composite_chart.svg")')
    else:  # davison
        lines.append("# Create Davison chart (time-space midpoint)")
        lines.append("davison = SynthesisBuilder.davison(chart1, chart2).calculate()")
        lines.append("")
        lines.append("# Generate Davison chart")
        lines.append('davison.draw("davison_chart.svg")')

    # Visualization options
    lines.append(f'    .with_theme("{state.theme}")')
    lines.append(f'    .with_zodiac_palette("{state.zodiac_palette}")')
    lines.append(f'    .with_aspect_palette("{state.aspect_palette}")')

    if state.show_header:
        lines.append("    .with_header()")
    else:
        lines.append("    .without_header()")

    if state.show_moon_phase:
        lines.append(f'    .with_moon_phase(position="{state.moon_phase_position}")')

    lines.append("    .save()")
    lines.append("")

    # Generate report
    chart_var = {
        "synastry": "comparison",
        "composite": "composite",
        "davison": "davison",
    }[state.chart_type]

    chart_file = {
        "synastry": "synastry_chart.svg",
        "composite": "composite_chart.svg",
        "davison": "davison_chart.svg",
    }[state.chart_type]

    type_names = {
        "synastry": "Synastry",
        "composite": "Composite",
        "davison": "Davison",
    }

    lines.append("# Generate PDF report")
    lines.append(f"(ReportBuilder().from_chart({chart_var})")

    rs = report_state
    if rs.include_chart_overview:
        lines.append("    .with_chart_overview()")
    if rs.include_planet_positions:
        lines.append("    .with_planet_positions()")
    if rs.include_house_cusps:
        lines.append("    .with_house_cusps()")
    if rs.include_aspects:
        lines.append(f'    .with_aspects(mode="{rs.aspects_mode}")')

    if rs.include_chart_image:
        lines.append(f'    .with_chart_image("{chart_file}")')

    title = f"{name1} & {name2} - {type_names[state.chart_type]}"
    lines.append(f'    .with_title("{title}")')
    lines.append('    .render(format="pdf", file="relationship_report.pdf"))')

    return "\n".join(lines)


def generate_timing_code(state: TimingState, report_state: PDFReportState) -> str:
    """Generate Python code for timing charts (transits, progressions, returns)."""

    lines = ["from stellium import ChartBuilder, ReportBuilder"]

    # Add imports based on chart type
    if state.chart_type in ("transits", "progressions"):
        lines.append("from stellium.core.comparison import ComparisonBuilder")
    if state.chart_type == "progressions":
        lines.append(
            "from stellium.utils.progressions import calculate_progressed_datetime"
        )
    if state.chart_type in ("solar_return", "lunar_return", "planetary_return"):
        lines.append("from stellium.returns import ReturnBuilder")

    if state.house_system != "Placidus":
        hs_class = state.house_system.replace(" ", "").replace("(", "").replace(")", "")
        lines.append(f"from stellium.engines.houses import {hs_class}Houses")

    lines.append("")

    natal = state.natal
    natal_dt = natal.date if natal.time_unknown else f"{natal.date} {natal.time}"
    natal_name = natal.name or "Chart"

    # Build natal chart
    lines.append("# Build natal chart")
    lines.append(
        f'natal = (ChartBuilder.from_details("{natal_dt}", "{natal.location}", name="{natal_name}")'
    )
    if natal.time_unknown:
        lines.append("    .with_unknown_time()")
    if state.include_aspects:
        lines.append("    .with_aspects()")
    if state.house_system != "Placidus":
        hs_class = state.house_system.replace(" ", "").replace("(", "").replace(")", "")
        lines.append(f"    .with_house_systems([{hs_class}Houses()])")
    lines.append("    .calculate())")
    lines.append("")

    # Build timing chart based on type
    if state.chart_type == "transits":
        lines.append(f"# Build transit chart for {state.timing_date}")
        lines.append(
            f'transits = (ChartBuilder.from_details("{state.timing_date}", "{natal.location}")'
        )
        if state.include_aspects:
            lines.append("    .with_aspects()")
        lines.append("    .calculate())")
        lines.append("")
        lines.append("# Create bi-wheel with natal inside, transits outside")
        lines.append("comparison = (ComparisonBuilder.synastry(natal, transits,")
        lines.append(f'    chart1_label="{natal_name}",')
        lines.append('    chart2_label="Transits")')
        lines.append("    .calculate())")
        chart_var = "comparison"

    elif state.chart_type == "progressions":
        lines.append(f"# Calculate progressed positions for {state.timing_date}")
        lines.append("from dateutil.parser import parse")
        lines.append(f'natal_datetime = parse("{natal_dt}")')
        lines.append(f'target_date = parse("{state.timing_date}")')
        lines.append(
            "progressed_datetime = calculate_progressed_datetime(natal_datetime, target_date)"
        )
        lines.append("")
        lines.append("# Build progressed chart")
        lines.append(
            f'progressed = (ChartBuilder.from_details(progressed_datetime, "{natal.location}")'
        )
        if state.include_aspects:
            lines.append("    .with_aspects()")
        lines.append("    .calculate())")
        lines.append("")
        lines.append("# Create bi-wheel with natal inside, progressed outside")
        lines.append("comparison = (ComparisonBuilder.synastry(natal, progressed,")
        lines.append(f'    chart1_label="{natal_name}",')
        lines.append('    chart2_label="Progressed")')
        lines.append("    .calculate())")
        chart_var = "comparison"

    elif state.chart_type == "solar_return":
        lines.append(f"# Calculate Solar Return for {state.timing_date}")
        location_arg = (
            f', location="{state.relocation_location}"' if state.relocate else ""
        )
        lines.append(
            f"solar_return = (ReturnBuilder.solar(natal, {state.timing_date}{location_arg})"
        )
        if state.include_aspects:
            lines.append("    .with_aspects()")
        lines.append("    .calculate())")
        chart_var = "solar_return"

    elif state.chart_type == "lunar_return":
        lines.append("# Calculate Lunar Return")
        near_date_arg = f'near_date="{state.timing_date}"' if state.timing_date else ""
        location_arg = (
            f', location="{state.relocation_location}"' if state.relocate else ""
        )
        args = ", ".join(filter(None, [near_date_arg, location_arg.lstrip(", ")]))
        lines.append(f"lunar_return = (ReturnBuilder.lunar(natal, {args})")
        if state.include_aspects:
            lines.append("    .with_aspects()")
        lines.append("    .calculate())")
        chart_var = "lunar_return"

    elif state.chart_type == "planetary_return":
        lines.append(f"# Calculate {state.return_planet} Return")
        near_date_arg = f'near_date="{state.timing_date}"' if state.timing_date else ""
        location_arg = (
            f', location="{state.relocation_location}"' if state.relocate else ""
        )
        args = ", ".join(filter(None, [near_date_arg, location_arg.lstrip(", ")]))
        lines.append(
            f'planetary_return = (ReturnBuilder.planetary(natal, "{state.return_planet}", {args})'
        )
        if state.include_aspects:
            lines.append("    .with_aspects()")
        lines.append("    .calculate())")
        chart_var = "planetary_return"
    else:
        chart_var = "natal"

    lines.append("")

    # Visualization
    chart_file = f"{state.chart_type}_chart.svg"
    lines.append("# Generate chart visualization")
    lines.append(f'{chart_var}.draw("{chart_file}")')
    lines.append(f'    .with_theme("{state.theme}")')
    lines.append(f'    .with_zodiac_palette("{state.zodiac_palette}")')
    if state.show_header:
        lines.append("    .with_header()")
    else:
        lines.append("    .without_header()")
    lines.append("    .save()")
    lines.append("")

    # Generate report
    type_names = {
        "transits": "Transits",
        "progressions": "Secondary Progressions",
        "solar_return": "Solar Return",
        "lunar_return": "Lunar Return",
        "planetary_return": f"{state.return_planet} Return",
    }

    lines.append("# Generate PDF report")
    lines.append(f"(ReportBuilder().from_chart({chart_var})")

    rs = report_state
    if rs.include_chart_overview:
        lines.append("    .with_chart_overview()")
    if rs.include_planet_positions:
        lines.append("    .with_planet_positions()")
    if rs.include_house_cusps:
        lines.append("    .with_house_cusps()")
    if rs.include_aspects:
        lines.append(f'    .with_aspects(mode="{rs.aspects_mode}")')

    if rs.include_chart_image:
        lines.append(f'    .with_chart_image("{chart_file}")')

    title = f"{natal_name} - {type_names[state.chart_type]}"
    lines.append(f'    .with_title("{title}")')
    lines.append('    .render(format="pdf", file="timing_report.pdf"))')

    return "\n".join(lines)


def create_code_preview_dialog(
    code: str,
    title: str = "Python Code",
):
    """Create a dialog showing the Python code."""

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl max-h-[90vh]"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label(f"☆  {title.upper()}").classes(
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
                on_click=lambda: (
                    ui.run_javascript(f"navigator.clipboard.writeText({repr(code)})"),
                    ui.notify("Copied to clipboard!", type="positive"),
                ),
            ).style(
                f"background-color: {COLORS['primary']} !important; color: white !important;"
            )

            ui.button("Close", on_click=dialog.close).props("outline").style(
                f"color: {COLORS['text_muted']} !important; border-color: {COLORS['border']} !important;"
            )

    return dialog


# Convenience functions for each page type
def create_natal_code_preview_dialog(state: ChartState, report_state: PDFReportState):
    """Create a code preview dialog for natal charts."""
    code = generate_natal_code(state, report_state)
    return create_code_preview_dialog(code, "Natal Chart Code")


def create_relationships_code_preview_dialog(
    state: RelationshipsState, report_state: PDFReportState
):
    """Create a code preview dialog for relationship charts."""
    code = generate_relationships_code(state, report_state)
    type_names = {
        "synastry": "Synastry",
        "composite": "Composite",
        "davison": "Davison",
    }
    return create_code_preview_dialog(code, f"{type_names[state.chart_type]} Code")


def create_timing_code_preview_dialog(state: TimingState, report_state: PDFReportState):
    """Create a code preview dialog for timing charts."""
    code = generate_timing_code(state, report_state)
    type_names = {
        "transits": "Transits",
        "progressions": "Progressions",
        "solar_return": "Solar Return",
        "lunar_return": "Lunar Return",
        "planetary_return": f"{state.return_planet} Return",
    }
    return create_code_preview_dialog(code, f"{type_names[state.chart_type]} Code")
