"""
Transit Timeline Cookbook
=========================

This cookbook demonstrates Stellium's transit period analysis and
Gantt timeline visualization. Transits show when planets in the sky
form aspects to positions in your natal chart.

Key features:
- Transit-to-natal aspect detection with orb windows
- Multi-pass retrograde transit detection (e.g., Jupiter stations
  and crosses your natal Sun three times)
- Plain-text list output for detailed analysis
- SVG Gantt chart for visual timeline overview
- Customizable planet selection, aspects, and orbs

Run this script to generate example transit outputs:

    source ~/.zshrc && pyenv activate starlight
    python examples/transit_cookbook.py
"""

import datetime as dt
from pathlib import Path

from stellium import ChartBuilder, ReportBuilder
from stellium.presentation.sections.transit_periods import (
    TransitGanttSection,
    TransitListSection,
    calculate_transit_periods,
)

# Output directory
OUTPUT_DIR = Path(__file__).parent / "transits"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# Example 1: Basic Transit List
# =============================================================================


def example_1_basic_transit_list():
    """
    Basic transit list for 6 months.

    Shows all outer planet transits to natal positions in a readable
    text format. Fast planets (Sun, Moon, Mercury, Venus, Mars) are
    included but produce many short entries.
    """
    print("\n=== Example 1: Basic Transit List ===\n")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()

    start = dt.datetime(2026, 1, 1)
    end = dt.datetime(2026, 7, 1)

    # Build a report with the transit list section
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_section(TransitListSection(start=start, end=end))
    )
    report.render(format="rich_table")


# =============================================================================
# Example 2: Gantt Timeline (Outer Planets Only)
# =============================================================================


def example_2_gantt_outer_planets():
    """
    SVG Gantt timeline showing outer planet transits.

    By default, TransitGanttSection excludes fast planets (Sun through Mars)
    since their many short transits make the chart unreadable. This gives
    a clean view of the major transits: Jupiter, Saturn, Uranus, Neptune,
    Pluto, True Node, and Chiron.

    The Gantt chart shows:
    - Colored bars = orb window (when the transit is "active")
    - White tick marks = exact dates
    - Multiple ticks on one bar = retrograde multi-pass transit
    - Rows grouped by transiting planet
    """
    print("\n=== Example 2: Gantt Timeline (Outer Planets) ===\n")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()

    start = dt.datetime(2025, 6, 1)
    end = dt.datetime(2026, 6, 1)

    # Dark theme (default)
    section_dark = TransitGanttSection(start=start, end=end, theme="dark")
    report = ReportBuilder().from_chart(chart).with_section(section_dark)
    report.render(format="rich_table")

    output_path = OUTPUT_DIR / "transit_gantt_outer_dark.svg"
    data = section_dark.generate_data(chart)
    Path(output_path).write_text(data["content"])
    print(f"\nSaved: {output_path}")

    # Light theme
    section_light = TransitGanttSection(start=start, end=end, theme="light")
    data = section_light.generate_data(chart)
    output_path = OUTPUT_DIR / "transit_gantt_outer_light.svg"
    Path(output_path).write_text(data["content"])
    print(f"Saved: {output_path}")


# =============================================================================
# Example 3: Gantt with All Planets
# =============================================================================


def example_3_gantt_all_planets():
    """
    Gantt timeline including fast planets.

    Set exclude_fast_planets=False to see ALL transits. This produces
    a much denser chart but shows the full picture including Mercury
    retrogrades and Mars transits.
    """
    print("\n=== Example 3: Gantt with All Planets ===\n")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()

    start = dt.datetime(2026, 1, 1)
    end = dt.datetime(2026, 4, 1)

    # Shorter window + all planets = manageable density
    section = TransitGanttSection(
        start=start,
        end=end,
        exclude_fast_planets=False,
    )

    report = ReportBuilder().from_chart(chart).with_section(section)
    report.render(format="rich_table")

    output_path = OUTPUT_DIR / "transit_gantt_all.svg"
    data = section.generate_data(chart)
    Path(output_path).write_text(data["content"])
    print(f"\nSaved: {output_path}")


# =============================================================================
# Example 4: Custom Aspects and Orbs
# =============================================================================


def example_4_custom_aspects():
    """
    Customize which aspects to track and their orb sizes.

    Useful for traditional astrology (major aspects only with tight orbs)
    or modern astrology (wider aspect set with generous orbs).
    """
    print("\n=== Example 4: Custom Aspects and Orbs ===\n")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()

    start = dt.datetime(2026, 1, 1)
    end = dt.datetime(2026, 12, 31)

    # Traditional: only hard aspects, tight orbs
    traditional_aspects = {
        "Conjunction": 1.5,
        "Square": 1.5,
        "Opposition": 1.5,
    }

    section = TransitGanttSection(
        start=start,
        end=end,
        aspects=traditional_aspects,
    )

    report = ReportBuilder().from_chart(chart).with_section(section)
    report.render(format="rich_table")

    output_path = OUTPUT_DIR / "transit_gantt_traditional.svg"
    data = section.generate_data(chart)
    Path(output_path).write_text(data["content"])
    print(f"\nSaved: {output_path}")


# =============================================================================
# Example 5: Programmatic Access to Transit Data
# =============================================================================


def example_5_programmatic_access():
    """
    Access transit period data directly for custom analysis.

    calculate_transit_periods() returns TransitPeriod objects you can
    filter, sort, and process however you need.
    """
    print("\n=== Example 5: Programmatic Transit Data ===\n")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()

    start = dt.datetime(2026, 1, 1)
    end = dt.datetime(2026, 12, 31)

    periods = calculate_transit_periods(chart, start, end)

    # Filter: only multi-pass (retrograde) transits
    retro_transits = [p for p in periods if p.is_multi_pass]
    print(f"Total transits: {len(periods)}")
    print(f"Multi-pass (retrograde) transits: {len(retro_transits)}")

    for p in retro_transits[:5]:
        dates = ", ".join(d.strftime("%b %d") for d in p.exact_dates)
        print(f"  {p.transit_planet} {p.aspect_name} natal {p.natal_planet}")
        print(f"    Exact dates: {dates}")
        if p.duration_days:
            print(f"    Duration: {p.duration_days:.0f} days")
        print()

    # Filter: only Pluto transits (major life themes)
    pluto_transits = [p for p in periods if p.transit_planet == "Pluto"]
    print(f"Pluto transits in 2026: {len(pluto_transits)}")
    for p in pluto_transits:
        print(f"  Pluto {p.aspect_name} natal {p.natal_planet}")


# =============================================================================
# Example 6: Generate README Image
# =============================================================================


def generate_readme_image():
    """
    Generate the transit Gantt chart used in the README.

    Uses a notable birth chart for a clean, reproducible example.
    """
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    start = dt.datetime(2025, 6, 1)
    end = dt.datetime(2026, 6, 1)

    section = TransitGanttSection(start=start, end=end)
    data = section.generate_data(chart)

    output_path = Path(__file__).parent.parent / "images" / "transit_gantt_example.svg"
    output_path.write_text(data["content"])
    print(f"README image saved: {output_path}")


# =============================================================================
# Run all examples
# =============================================================================

if __name__ == "__main__":
    example_1_basic_transit_list()
    example_2_gantt_outer_planets()
    example_3_gantt_all_planets()
    example_4_custom_aspects()
    example_5_programmatic_access()
    generate_readme_image()
    print("\n✅ All transit examples complete!")
