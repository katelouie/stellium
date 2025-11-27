#!/usr/bin/env python3
"""
Report Cookbook - Comprehensive Examples for Stellium Report Generation

This cookbook demonstrates all the ways to generate reports with Stellium,
from simple terminal output to beautiful PDF documents.

Run this script to generate example reports in examples/reports/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/report_cookbook.py

For full documentation, see docs/REPORTS.md
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder
from stellium.components import DignityComponent, MidpointCalculator
from stellium.engines import PlacidusHouses, WholeSignHouses

# Output directory for generated reports
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC REPORTS
# =============================================================================


def example_1_minimal_terminal():
    """
    Example 1: Minimal Terminal Report

    The simplest possible report - just overview and positions,
    displayed directly in your terminal with Rich formatting.
    """
    section_header("Example 1: Minimal Terminal Report")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print("Generating minimal report...\n")
    ReportBuilder().from_chart(chart).preset_minimal().render()


def example_2_standard_terminal():
    """
    Example 2: Standard Terminal Report

    A balanced report with positions, aspects, and houses.
    Great for everyday use.
    """
    section_header("Example 2: Standard Terminal Report")

    chart = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

    print("Generating standard report...\n")
    ReportBuilder().from_chart(chart).preset_standard().render()


def example_3_detailed_terminal():
    """
    Example 3: Detailed Terminal Report

    Comprehensive report with moon phase, declinations, and dignities.
    """
    section_header("Example 3: Detailed Terminal Report")

    chart = (
        ChartBuilder.from_notable("Nikola Tesla")
        .with_aspects()
        .add_component(DignityComponent())
        .calculate()
    )

    print("Generating detailed report...\n")
    ReportBuilder().from_chart(chart).preset_detailed().render()


# =============================================================================
# PART 2: PDF REPORTS WITH TYPST
# =============================================================================


def example_4_basic_pdf():
    """
    Example 4: Basic PDF Report

    Generate a simple but beautiful PDF using Typst.
    Features Cinzel Decorative headings and Crimson Pro body text.
    """
    section_header("Example 4: Basic PDF Report")

    chart = ChartBuilder.from_notable("Frida Kahlo").with_aspects().calculate()

    output_file = OUTPUT_DIR / "basic_report.pdf"

    print(f"Generating PDF report to {output_file}...")

    ReportBuilder().from_chart(chart).preset_standard().render(
        format="pdf",
        file=str(output_file),
        show=False,
    )

    print(f"Done! Open {output_file} to see the result.")


def example_5_pdf_with_chart():
    """
    Example 5: PDF Report with Embedded Chart Wheel

    Generate a PDF with the natal chart wheel displayed on the title page.
    This is the most visually impressive output!
    """
    section_header("Example 5: PDF Report with Chart Wheel")

    chart = (
        ChartBuilder.from_notable("Carl Jung")
        .with_aspects()
        .add_component(DignityComponent())
        .calculate()
    )

    # First, generate the chart wheel SVG
    svg_path = OUTPUT_DIR / "jung_chart.svg"
    print(f"Generating chart wheel to {svg_path}...")

    chart.draw(str(svg_path)).with_theme("celestial").with_zodiac_palette(
        "rainbow_celestial"
    ).with_moon_phase(position="bottom-left").save()

    # Then generate the PDF report with the chart embedded
    pdf_path = OUTPUT_DIR / "jung_full_report.pdf"
    print(f"Generating PDF report to {pdf_path}...")

    ReportBuilder().from_chart(chart).preset_detailed().render(
        format="pdf",
        file=str(pdf_path),
        chart_svg_path=str(svg_path),
        title="Carl Jung - Natal Chart Analysis",
        show=False,
    )

    print(f"Done! Open {pdf_path} to see the result.")


def example_6_full_pdf():
    """
    Example 6: Complete PDF Report with All Sections

    Generate a comprehensive PDF with every available section.
    Requires DignityComponent and MidpointCalculator.
    """
    section_header("Example 6: Complete PDF Report")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .add_component(DignityComponent())
        .add_component(MidpointCalculator())
        .calculate()
    )

    # Generate chart wheel
    svg_path = OUTPUT_DIR / "einstein_chart.svg"
    print(f"Generating chart wheel to {svg_path}...")

    chart.draw(str(svg_path)).with_theme("midnight").with_zodiac_palette(
        "rainbow_midnight"
    ).with_moon_phase(position="bottom-left").with_chart_info(
        position="top-left"
    ).save()

    # Generate full PDF
    pdf_path = OUTPUT_DIR / "einstein_complete_report.pdf"
    print(f"Generating complete PDF report to {pdf_path}...")

    ReportBuilder().from_chart(chart).preset_full().render(
        format="pdf",
        file=str(pdf_path),
        chart_svg_path=str(svg_path),
        title="Albert Einstein - Complete Natal Analysis",
        show=False,
    )

    print(f"Done! Open {pdf_path} to see the result.")


# =============================================================================
# PART 3: CUSTOM REPORTS
# =============================================================================


def example_7_custom_sections():
    """
    Example 7: Custom Report with Selected Sections

    Build a report with exactly the sections you want.
    """
    section_header("Example 7: Custom Report")

    chart = (
        ChartBuilder.from_notable("Leonardo da Vinci")
        .with_aspects()
        .add_component(MidpointCalculator())
        .calculate()
    )

    print("Generating custom report (positions + major aspects + midpoints)...\n")

    (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_planet_positions(include_speed=True, include_house=True)
        .with_aspects(mode="major", sort_by="planet")
        .with_midpoints(mode="core", threshold=10)
        .render()
    )


def example_8_aspect_focused():
    """
    Example 8: Aspect-Focused Report

    A report that emphasizes planetary relationships.
    """
    section_header("Example 8: Aspect-Focused Report")

    chart = ChartBuilder.from_notable("Wolfgang Mozart").with_aspects().calculate()

    output_file = OUTPUT_DIR / "mozart_aspects.pdf"
    svg_path = OUTPUT_DIR / "mozart_chart.svg"

    # Generate minimal chart (aspects visible)
    chart.draw(str(svg_path)).preset_minimal().save()

    print(f"Generating aspect-focused PDF to {output_file}...")

    (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_aspects(mode="all", orbs=True, sort_by="orb")
        .render(
            format="pdf",
            file=str(output_file),
            chart_svg_path=str(svg_path),
            title="Wolfgang Mozart - Aspects Analysis",
            show=False,
        )
    )

    print(f"Done! Open {output_file} to see the result.")


def example_9_positions_only():
    """
    Example 9: Positions-Only Report

    Focus on placements without aspects - useful for quick reference.
    """
    section_header("Example 9: Positions-Only Report")

    chart = (
        ChartBuilder.from_notable("Queen Elizabeth II")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate()
    )

    print("Generating positions-only report...\n")

    (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_planet_positions(
            include_speed=True, include_house=True, house_systems="all"
        )
        .with_declinations()
        .with_house_cusps(systems="all")
        .render()
    )


# =============================================================================
# PART 4: COMPARISON REPORTS (SYNASTRY & TRANSITS)
# =============================================================================


def example_10_synastry_report():
    """
    Example 10: Synastry Report

    Generate a relationship comparison report with side-by-side tables.
    """
    section_header("Example 10: Synastry Report")

    # Calculate individual charts
    person1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
    person2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

    # Create synastry comparison
    synastry = (
        ComparisonBuilder.from_native(person1, native_label="John Lennon")
        .with_partner(person2, partner_label="Yoko Ono")
        .calculate()
    )

    # Generate biwheel chart
    svg_path = OUTPUT_DIR / "lennon_ono_biwheel.svg"
    print(f"Generating biwheel chart to {svg_path}...")

    synastry.draw(str(svg_path)).with_theme("celestial").save()

    # Generate synastry PDF
    pdf_path = OUTPUT_DIR / "lennon_ono_synastry.pdf"
    print(f"Generating synastry PDF to {pdf_path}...")

    ReportBuilder().from_chart(synastry).preset_synastry().render(
        format="pdf",
        file=str(pdf_path),
        chart_svg_path=str(svg_path),
        title="John Lennon & Yoko Ono - Synastry",
        show=False,
    )

    print(f"Done! Open {pdf_path} to see the result.")


def example_11_transit_report():
    """
    Example 11: Transit Report

    Show current planetary transits to a natal chart.
    """
    section_header("Example 11: Transit Report")

    from datetime import datetime

    # Natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    # Transit time (use a specific date for reproducibility)
    transit_time = datetime(2025, 1, 1, 12, 0)

    # Create transit chart at natal location
    transit_chart = (
        ChartBuilder.from_details(
            transit_time,
            natal.location.latitude,
            natal.location.longitude,
            natal.location.name,
        )
        .with_aspects()
        .calculate()
    )

    # Create comparison
    transits = (
        ComparisonBuilder.from_native(natal, native_label="Natal")
        .with_partner(transit_chart, partner_label="Transits 2025-01-01")
        .calculate()
    )

    # Generate transit PDF
    pdf_path = OUTPUT_DIR / "einstein_transits.pdf"
    print(f"Generating transit PDF to {pdf_path}...")

    ReportBuilder().from_chart(transits).preset_transit().render(
        format="pdf",
        file=str(pdf_path),
        title="Albert Einstein - Transits for Jan 1, 2025",
        show=False,
    )

    print(f"Done! Open {pdf_path} to see the result.")


def example_12_custom_synastry():
    """
    Example 12: Custom Synastry Report

    Build a detailed synastry report with specific sections.
    """
    section_header("Example 12: Custom Synastry Report")

    person1 = (
        ChartBuilder.from_notable("Prince William")
        .with_aspects()
        .add_component(DignityComponent())
        .calculate()
    )
    person2 = (
        ChartBuilder.from_notable("Kate Middleton")
        .with_aspects()
        .add_component(DignityComponent())
        .calculate()
    )

    synastry = (
        ComparisonBuilder.from_native(person1, native_label="Prince William")
        .with_partner(person2, partner_label="Kate Middleton")
        .calculate()
    )

    # Generate biwheel
    svg_path = OUTPUT_DIR / "royal_biwheel.svg"
    print(f"Generating biwheel to {svg_path}...")

    synastry.draw(str(svg_path)).with_theme("midnight").with_tables().save()

    # Custom detailed synastry report
    pdf_path = OUTPUT_DIR / "royal_synastry_detailed.pdf"
    print(f"Generating detailed synastry PDF to {pdf_path}...")

    (
        ReportBuilder()
        .from_chart(synastry)
        .with_chart_overview()
        .with_planet_positions(include_house=True, include_speed=True)
        .with_cross_aspects(mode="all", sort_by="orb")
        .with_house_cusps()
        .render(
            format="pdf",
            file=str(pdf_path),
            chart_svg_path=str(svg_path),
            title="Prince William & Kate Middleton - Detailed Synastry",
            show=False,
        )
    )

    print(f"Done! Open {pdf_path} to see the result.")


# =============================================================================
# PART 5: OUTPUT FORMATS
# =============================================================================


def example_13_plain_text():
    """
    Example 13: Plain Text Output

    Generate reports as plain ASCII text - great for logs or email.
    """
    section_header("Example 13: Plain Text Output")

    chart = ChartBuilder.from_notable("Isaac Newton").with_aspects().calculate()

    output_file = OUTPUT_DIR / "newton_report.txt"
    print(f"Generating plain text report to {output_file}...")

    ReportBuilder().from_chart(chart).preset_standard().render(
        format="plain_table",
        file=str(output_file),
        show=False,
    )

    print(f"Done! Contents:\n")

    # Show first 40 lines
    with open(output_file) as f:
        lines = f.readlines()[:40]
        print("".join(lines))
        if len(lines) == 40:
            print("... (truncated)")


def example_14_save_and_display():
    """
    Example 14: Save to File AND Display in Terminal

    You can do both at once!
    """
    section_header("Example 14: Save and Display")

    chart = ChartBuilder.from_notable("Galileo Galilei").with_aspects().calculate()

    output_file = OUTPUT_DIR / "galileo_report.txt"

    print(f"Generating report (saving to {output_file} AND displaying)...\n")

    ReportBuilder().from_chart(chart).preset_minimal().render(
        format="rich_table",
        file=str(output_file),
        show=True,  # Display in terminal
    )

    print(f"\nAlso saved to {output_file}")


# =============================================================================
# PART 6: BATCH PROCESSING
# =============================================================================


def example_15_batch_reports():
    """
    Example 15: Batch Report Generation

    Generate reports for multiple people at once.
    """
    section_header("Example 15: Batch Report Generation")

    scientists = [
        "Albert Einstein",
        "Marie Curie",
        "Nikola Tesla",
        "Isaac Newton",
        "Galileo Galilei",
    ]

    print(f"Generating reports for {len(scientists)} scientists...\n")

    for name in scientists:
        # Calculate chart
        chart = ChartBuilder.from_notable(name).with_aspects().calculate()

        # Safe filename
        filename = name.lower().replace(" ", "_")

        # Generate chart SVG
        svg_path = OUTPUT_DIR / f"{filename}_chart.svg"
        chart.draw(str(svg_path)).with_theme("celestial").with_moon_phase().save()

        # Generate PDF
        pdf_path = OUTPUT_DIR / f"{filename}_report.pdf"
        ReportBuilder().from_chart(chart).preset_standard().render(
            format="pdf",
            file=str(pdf_path),
            chart_svg_path=str(svg_path),
            title=f"{name} - Natal Chart",
            show=False,
        )

        print(f"  Created {pdf_path}")

    print(f"\nDone! Generated {len(scientists)} reports in {OUTPUT_DIR}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run selected examples."""
    print("\n" + "=" * 60)
    print("  STELLIUM REPORT COOKBOOK")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}\n")

    # Uncomment the examples you want to run:

    # --- Part 1: Basic Reports (Terminal) ---
    example_1_minimal_terminal()
    example_2_standard_terminal()
    # example_3_detailed_terminal()

    # --- Part 2: PDF Reports ---
    example_4_basic_pdf()
    example_5_pdf_with_chart()
    example_6_full_pdf()

    # --- Part 3: Custom Reports ---
    # example_7_custom_sections()
    # example_8_aspect_focused()
    # example_9_positions_only()

    # --- Part 4: Comparison Reports ---
    example_10_synastry_report()
    # example_11_transit_report()
    # example_12_custom_synastry()

    # --- Part 5: Output Formats ---
    # example_13_plain_text()
    # example_14_save_and_display()

    # --- Part 6: Batch Processing ---
    # example_15_batch_reports()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files are in: {OUTPUT_DIR}")
    print("See docs/REPORTS.md for full documentation.\n")


if __name__ == "__main__":
    main()
