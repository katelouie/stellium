#!/usr/bin/env python3
"""
Generate a beautiful PDF report using Typst renderer.

This script creates a natal chart and renders it as a professional-quality
PDF report with Cinzel Decorative headers and Crimson Pro body text.

Usage:
    python examples/generate_beautiful_report.py
"""

import sys

sys.path.insert(0, "/Users/katelouie/code/stellium/src")

from stellium import ChartBuilder, ReportBuilder
from stellium.engines import PlacidusHouses, WholeSignHouses

# ============================================================================
# CHART CONFIGURATION
# ============================================================================
NAME = "Kate Louie"
DATETIME = "1994-01-06 11:47"
LOCATION = "Palo Alto, CA"

# Output paths
SVG_PATH = "/Users/katelouie/code/stellium/examples/chart_examples/beautiful_chart.svg"
PDF_PATH = (
    "/Users/katelouie/code/stellium/examples/chart_examples/beautiful_report.pdf"
)

# ============================================================================
# GENERATE CHART
# ============================================================================
print("Creating chart...")
chart = (
    ChartBuilder.from_details(DATETIME, LOCATION, name=NAME)
    .with_aspects()
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .calculate()
)
print(f"✓ Chart created for {NAME} in {LOCATION}")

# ============================================================================
# SAVE SVG (with rainbow zodiac palette)
# ============================================================================
print("\nGenerating chart wheel SVG...")
# Name is taken from the chart metadata (set via from_details(..., name=NAME))
chart.draw(SVG_PATH).preset_minimal().with_zodiac_palette(
    "rainbow"
).with_moon_phase().save()
print(f"✓ Chart SVG saved to {SVG_PATH}")

# ============================================================================
# GENERATE PDF REPORT
# ============================================================================
print("\nGenerating PDF report with Typst...")
report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .with_aspects(mode="major")
)

# Title will be auto-generated from the chart's name!
report.render(format="typst", file=PDF_PATH, chart_svg_path=SVG_PATH, show=False)
print(f"✓ PDF saved to {PDF_PATH}")

print("\n" + "=" * 50)
print("🌟 Done! Open the PDF to see your beautiful report!")
print("=" * 50)
