#!/usr/bin/env python3
"""
MultiChart Cookbook - Comprehensive Examples

This cookbook demonstrates the unified MultiChart architecture, which replaces
both Comparison and MultiWheel with a single, flexible API for 2-4 chart
comparisons and visualizations.

Contents:
    1. Basic Synastry (2 charts)
    2. Basic Transit Comparison
    3. Secondary Progressions
    4. Arc Directions
    5. Triwheel: Natal + Progressed + Transit
    6. Quadwheel: Four Charts
    7. Cross-Aspect Configuration
    8. House Overlay Analysis
    9. Compatibility Scoring
    10. Accessing Charts (Dual Access Pattern)
    11. Relationship Types Per-Pair
    12. Visualization: Drawing MultiCharts
    13. Visualization: Themes and Customization
    14. Reports: Chart Overview
    15. Reports: Cross-Chart Aspects
    16. Reports: Full Synastry Report
    17. Serialization: Export to JSON
    18. Migration from Comparison/MultiWheel

Run with:
    source ~/.zshrc && pyenv activate starlight && python examples/multichart_cookbook.py
"""

from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder


def example_01_basic_synastry():
    """
    Example 1: Basic Synastry (Two-Chart Comparison)

    The simplest use case - compare two natal charts for relationship analysis.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Synastry")
    print("=" * 60)

    # Create two natal charts
    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),  # Palo Alto, CA
        name="Person A",
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30",
        (47.6062, -122.3321),  # Seattle, WA
        name="Person B",
    ).calculate()

    # Create synastry MultiChart
    mc = MultiChartBuilder.synastry(
        chart1, chart2, label1="Person A", label2="Person B"
    ).calculate()

    print(f"Chart count: {mc.chart_count}")
    print(f"Labels: {mc.labels}")
    print(f"Relationship: {mc.get_relationship(0, 1)}")
    print(f"Cross-aspects: {len(mc.get_cross_aspects())} aspects found")


def example_02_basic_transit():
    """
    Example 2: Basic Transit Comparison

    Compare a natal chart to the sky at a specific time.
    """
    print("\n" + "=" * 60)
    print("Example 2: Transit Comparison")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Native",
    ).calculate()

    # Transit using tuple (datetime, location)
    # Location can be None to use natal location
    mc = MultiChartBuilder.transit(
        natal,
        ("2025-06-15 12:00", None),  # Uses natal location
        natal_label="Natal",
        transit_label="Transit",
    ).calculate()

    print(f"Relationship: {mc.get_relationship(0, 1)}")
    print(f"Natal Sun: {mc.chart1.get_object('Sun').sign_position}")
    print(f"Transit Sun: {mc.chart2.get_object('Sun').sign_position}")


def example_03_progressions():
    """
    Example 3: Secondary Progressions

    Auto-calculate progressed chart by age or target date.
    """
    print("\n" + "=" * 60)
    print("Example 3: Secondary Progressions")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Native",
    ).calculate()

    # Progression by age
    mc_age = MultiChartBuilder.progression(
        natal,
        age=30,
        angle_method="quotidian",  # Options: quotidian, solar_arc, naibod
    ).calculate()

    print("Progressed by age 30:")
    print(f"  Natal Sun: {mc_age.natal.get_object('Sun').sign_position}")
    print(f"  Prog Sun: {mc_age.chart2.get_object('Sun').sign_position}")

    # Progression by target date
    mc_date = MultiChartBuilder.progression(
        natal,
        target_date="2024-06-15",
        angle_method="solar_arc",
    ).calculate()

    print("\nProgressed to 2024-06-15 (solar arc angles):")
    print(f"  Prog Sun: {mc_date.chart2.get_object('Sun').sign_position}")


def example_04_arc_directions():
    """
    Example 4: Arc Directions

    All points move by the same arc (solar, naibod, lunar, etc.)
    """
    print("\n" + "=" * 60)
    print("Example 4: Arc Directions")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Native",
    ).calculate()

    # Solar arc directions
    mc = MultiChartBuilder.arc_direction(
        natal,
        age=30,
        arc_type="solar_arc",  # Options: solar_arc, naibod, lunar, chart_ruler, sect
    ).calculate()

    print("Solar arc at age 30:")
    print(f"  Arc: {mc.chart2.metadata.get('arc_degrees', 0):.2f}°")
    print(f"  Natal MC: {mc.natal.get_object('MC').sign_position}")
    print(f"  Directed MC: {mc.chart2.get_object('MC').sign_position}")


def example_05_triwheel():
    """
    Example 5: Triwheel - Natal + Progressed + Transit

    Build a 3-chart configuration step by step.
    """
    print("\n" + "=" * 60)
    print("Example 5: Triwheel")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Native",
    ).calculate()

    # Build triwheel step by step
    mc = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15 12:00", label="Transit")
        .calculate()
    )

    print(f"Chart count: {mc.chart_count}")
    print(f"Labels: {mc.labels}")
    print(f"Chart 1 (Natal): {mc.chart1.metadata.get('name')}")
    print(f"Chart 2 (Progressed): {mc.chart2.metadata.get('name')}")
    print(f"Chart 3 (Transit): {mc.chart3.metadata.get('name')}")

    # Check relationships
    print("\nRelationships:")
    print(f"  0↔1: {mc.get_relationship(0, 1)}")  # Natal to Progressed
    print(f"  0↔2: {mc.get_relationship(0, 2)}")  # Natal to Transit


def example_06_quadwheel():
    """
    Example 6: Quadwheel - Four Charts

    Maximum supported is 4 charts.
    """
    print("\n" + "=" * 60)
    print("Example 6: Quadwheel")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),
        name="Native",
    ).calculate()

    # Build quadwheel
    mc = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_arc_direction(age=30, arc_type="solar_arc", label="Directed")
        .add_transit("2025-06-15 12:00", label="Transit")
        .calculate()
    )

    print(f"Chart count: {mc.chart_count}")
    print(f"Labels: {mc.labels}")
    print(f"Chart 4: {mc.chart4 is not None}")


def example_07_cross_aspect_config():
    """
    Example 7: Cross-Aspect Configuration

    Control which chart pairs have aspects calculated.
    """
    print("\n" + "=" * 60)
    print("Example 7: Cross-Aspect Configuration")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Native"
    ).calculate()

    # Default: "to_primary" - only aspects to chart 0
    mc_primary = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15", label="Transit")
        .with_cross_aspects("to_primary")  # Default
        .calculate()
    )

    print("to_primary mode:")
    print(f"  (0,1) aspects: {len(mc_primary.get_cross_aspects(0, 1))}")
    print(f"  (0,2) aspects: {len(mc_primary.get_cross_aspects(0, 2))}")
    print(f"  (1,2) aspects: {len(mc_primary.get_cross_aspects(1, 2))}")  # Empty

    # "all" - all pairs
    mc_all = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15", label="Transit")
        .with_cross_aspects("all")
        .calculate()
    )

    print("\nall mode:")
    print(f"  (0,1) aspects: {len(mc_all.get_cross_aspects(0, 1))}")
    print(f"  (0,2) aspects: {len(mc_all.get_cross_aspects(0, 2))}")
    print(f"  (1,2) aspects: {len(mc_all.get_cross_aspects(1, 2))}")  # Now has aspects

    # Explicit pairs
    mc_explicit = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15", label="Transit")
        .with_cross_aspects([(0, 2)])  # Only natal to transit
        .calculate()
    )

    print("\nexplicit [(0,2)] mode:")
    print(f"  (0,1) aspects: {len(mc_explicit.get_cross_aspects(0, 1))}")  # Empty
    print(f"  (0,2) aspects: {len(mc_explicit.get_cross_aspects(0, 2))}")


def example_08_house_overlays():
    """
    Example 8: House Overlay Analysis

    See where one person's planets fall in another's houses.
    """
    print("\n" + "=" * 60)
    print("Example 8: House Overlays")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    # Get house overlays
    # (planet_chart, house_chart) - whose planets in whose houses
    overlays_1_in_2 = mc.get_house_overlays(
        0, 1
    )  # Person A's planets in Person B's houses
    overlays_2_in_1 = mc.get_house_overlays(
        1, 0
    )  # Person B's planets in Person A's houses

    print(f"Person A's planets in Person B's houses: {len(overlays_1_in_2)}")
    for overlay in overlays_1_in_2[:3]:
        print(f"  {overlay.planet_name} in House {overlay.falls_in_house}")

    print(f"\nPerson B's planets in Person A's houses: {len(overlays_2_in_1)}")
    for overlay in overlays_2_in_1[:3]:
        print(f"  {overlay.planet_name} in House {overlay.falls_in_house}")

    # Disable house overlays for performance
    mc_no_overlays = (
        MultiChartBuilder.synastry(chart1, chart2).without_house_overlays().calculate()
    )
    print(
        f"\nWithout overlays: {len(mc_no_overlays.get_all_house_overlays())} overlays"
    )


def example_09_compatibility_scoring():
    """
    Example 9: Compatibility Scoring

    Calculate a simple compatibility score for synastry.
    """
    print("\n" + "=" * 60)
    print("Example 9: Compatibility Scoring")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    # Default scoring
    score = mc.calculate_compatibility_score()
    print(f"Default compatibility score: {score:.1f}/100")

    # Custom weights
    custom_weights = {
        "Conjunction": 1.0,
        "Trine": 1.5,
        "Sextile": 1.0,
        "Square": -0.8,
        "Opposition": -0.5,
    }
    custom_score = mc.calculate_compatibility_score(weights=custom_weights)
    print(f"Custom weights score: {custom_score:.1f}/100")


def example_10_dual_access_pattern():
    """
    Example 10: Accessing Charts (Dual Access Pattern)

    MultiChart supports both indexed and named access.
    """
    print("\n" + "=" * 60)
    print("Example 10: Dual Access Pattern")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Native"
    ).calculate()

    mc = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_transit("2025-06-15", label="Transit")
        .calculate()
    )

    # Indexed access
    print("Indexed access:")
    print(f"  mc[0] Sun: {mc[0].get_object('Sun').sign_position}")
    print(f"  mc[1] Sun: {mc[1].get_object('Sun').sign_position}")

    # Named properties
    print("\nNamed properties:")
    print(f"  mc.chart1 Sun: {mc.chart1.get_object('Sun').sign_position}")
    print(f"  mc.chart2 Sun: {mc.chart2.get_object('Sun').sign_position}")

    # Semantic aliases
    print("\nSemantic aliases:")
    print(f"  mc.inner Sun: {mc.inner.get_object('Sun').sign_position}")
    print(f"  mc.outer Sun: {mc.outer.get_object('Sun').sign_position}")
    print(f"  mc.natal Sun: {mc.natal.get_object('Sun').sign_position}")

    # Query methods
    print("\nQuery methods:")
    print(
        f"  mc.get_object('Sun', chart=0): {mc.get_object('Sun', chart=0).sign_position}"
    )
    print(f"  mc.get_planets(chart=1): {len(mc.get_planets(chart=1))} planets")


def example_11_relationship_types():
    """
    Example 11: Relationship Types Per-Pair

    Each chart pair can have its own relationship type.
    """
    print("\n" + "=" * 60)
    print("Example 11: Relationship Types Per-Pair")
    print("=" * 60)

    natal = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Native"
    ).calculate()

    mc = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15", label="Transit")
        .calculate()
    )

    # Each pair has its own relationship
    print("Relationships:")
    print(f"  Natal↔Progressed (0,1): {mc.get_relationship(0, 1)}")
    print(f"  Natal↔Transit (0,2): {mc.get_relationship(0, 2)}")
    print(f"  Progressed↔Transit (1,2): {mc.get_relationship(1, 2)}")  # None


def example_12_visualization_basic():
    """
    Example 12: Basic Visualization

    Draw MultiCharts as SVG files.
    """
    print("\n" + "=" * 60)
    print("Example 12: Basic Visualization")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(
        chart1, chart2, label1="Person A", label2="Person B"
    ).calculate()

    # Draw and save
    mc.draw("examples/chart_examples/multichart_synastry.svg").save()
    print("Saved: examples/chart_examples/multichart_synastry.svg")

    # Triwheel
    natal = chart1
    mc_tri = (
        MultiChartBuilder.from_chart(natal, "Natal")
        .add_progression(age=30, label="Progressed")
        .add_transit("2025-06-15", label="Transit")
        .calculate()
    )

    mc_tri.draw("examples/chart_examples/multichart_triwheel.svg").save()
    print("Saved: examples/chart_examples/multichart_triwheel.svg")


def example_13_visualization_themes():
    """
    Example 13: Visualization Themes and Customization

    Apply themes and customize the chart appearance.
    """
    print("\n" + "=" * 60)
    print("Example 13: Visualization Themes")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    # With theme
    mc.draw("examples/chart_examples/multichart_midnight.svg").with_theme(
        "midnight"
    ).save()
    print("Saved: examples/chart_examples/multichart_midnight.svg")

    # With size
    mc.draw("examples/chart_examples/multichart_large.svg").with_size(1000).save()
    print("Saved: examples/chart_examples/multichart_large.svg")

    # Without header
    mc.draw("examples/chart_examples/multichart_no_header.svg").without_header().save()
    print("Saved: examples/chart_examples/multichart_no_header.svg")


def example_14_reports_overview():
    """
    Example 14: Reports - Chart Overview

    Generate a chart overview section for MultiChart.
    """
    print("\n" + "=" * 60)
    print("Example 14: Reports - Chart Overview")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(
        chart1, chart2, label1="Person A", label2="Person B"
    ).calculate()

    (ReportBuilder().from_chart(mc).with_chart_overview().render(format="rich_table"))


def example_15_reports_cross_aspects():
    """
    Example 15: Reports - Cross-Chart Aspects

    Display cross-chart aspects in a report.
    """
    print("\n" + "=" * 60)
    print("Example 15: Reports - Cross-Chart Aspects")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    (
        ReportBuilder()
        .from_chart(mc)
        .with_cross_aspects(mode="major", sort_by="orb")
        .render(format="rich_table")
    )


def example_16_reports_full_synastry():
    """
    Example 16: Full Synastry Report

    Generate a complete synastry report.
    """
    print("\n" + "=" * 60)
    print("Example 16: Full Synastry Report")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(
        chart1, chart2, label1="Person A", label2="Person B"
    ).calculate()

    (
        ReportBuilder()
        .from_chart(mc)
        .with_chart_overview()
        .with_planet_positions()
        .with_cross_aspects(mode="all")
        .render(format="rich_table")
    )


def example_17_serialization():
    """
    Example 17: Serialization - Export to JSON

    Export MultiChart data for external use.
    """
    print("\n" + "=" * 60)
    print("Example 17: Serialization")
    print("=" * 60)

    chart1 = ChartBuilder.from_details(
        "1994-01-06 11:47", (37.4419, -122.1430), name="Person A"
    ).calculate()

    chart2 = ChartBuilder.from_details(
        "2000-05-15 14:30", (47.6062, -122.3321), name="Person B"
    ).calculate()

    mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    # Export to dict
    data = mc.to_dict()

    print(f"Exported keys: {list(data.keys())}")
    print(f"Chart count: {data['chart_count']}")
    print(f"Labels: {data['labels']}")
    print(f"Cross-aspect pairs: {list(data['cross_aspects'].keys())}")

    # Can be JSON-serialized
    import json

    json_str = json.dumps(data, indent=2, default=str)
    print(f"\nJSON length: {len(json_str)} chars")


def example_18_migration():
    """
    Example 18: Migration from Comparison/MultiWheel

    How to migrate existing code to MultiChart.
    """
    print("\n" + "=" * 60)
    print("Example 18: Migration Guide")
    print("=" * 60)

    print("""
Migration from Comparison/ComparisonBuilder:
--------------------------------------------
# OLD (deprecated, emits warning):
from stellium import ComparisonBuilder
comp = ComparisonBuilder.synastry(chart1, chart2).calculate()
aspects = comp.cross_aspects  # tuple

# NEW:
from stellium import MultiChartBuilder
mc = MultiChartBuilder.synastry(chart1, chart2).calculate()
aspects = mc.get_cross_aspects()  # tuple (same data)

# API equivalents:
comp.chart1          -> mc.chart1 or mc[0] or mc.natal
comp.chart2          -> mc.chart2 or mc[1] or mc.outer
comp.cross_aspects   -> mc.get_cross_aspects() or mc.cross_aspects[(0,1)]
comp.house_overlays  -> mc.get_all_house_overlays()


Migration from MultiWheel/MultiWheelBuilder:
--------------------------------------------
# OLD (deprecated, emits warning):
from stellium import MultiWheelBuilder
mw = MultiWheelBuilder.from_charts([c1, c2, c3]).calculate()

# NEW:
from stellium import MultiChartBuilder
mc = MultiChartBuilder.from_charts([c1, c2, c3]).calculate()

# API equivalents:
mw.charts           -> mc.charts
mw.labels           -> mc.labels
mw.chart_count      -> mc.chart_count
mw.cross_aspects    -> mc.cross_aspects (same dict format!)
mw.draw()           -> mc.draw()


Key Differences:
----------------
1. MultiChart ALWAYS uses dict for cross_aspects: {(0,1): aspects, ...}
   (Comparison used tuple, MultiWheel used dict)

2. MultiChart has per-pair relationships:
   mc.get_relationship(0, 1)  # Returns ComparisonType

3. MultiChart has richer query methods:
   mc.get_cross_aspects(0, 1)  # Specific pair
   mc.get_all_cross_aspects()  # All flattened
   mc.get_house_overlays(planet_chart, house_chart)

4. Builder has more configuration:
   .with_cross_aspects("to_primary" | "all" | "adjacent" | [(i,j), ...])
   .with_house_overlays() / .without_house_overlays()
""")


def main():
    """Run all examples."""
    example_01_basic_synastry()
    example_02_basic_transit()
    example_03_progressions()
    example_04_arc_directions()
    example_05_triwheel()
    example_06_quadwheel()
    example_07_cross_aspect_config()
    example_08_house_overlays()
    example_09_compatibility_scoring()
    example_10_dual_access_pattern()
    example_11_relationship_types()
    example_12_visualization_basic()
    example_13_visualization_themes()
    example_14_reports_overview()
    example_15_reports_cross_aspects()
    example_16_reports_full_synastry()
    example_17_serialization()
    example_18_migration()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
