#!/usr/bin/env python3
"""
Zodiacal Releasing Cookbook - Examples for Stellium ZR Analysis

Zodiacal Releasing is a Hellenistic predictive technique that divides life into
major periods (L1) and sub-periods (L2, L3, L4), each ruled by a zodiac sign.
It's particularly useful for understanding the timing of life themes.

This cookbook demonstrates:
- Setting up ZR with ChartBuilder
- Querying timelines by date or age
- Understanding peak periods and Loosing of the Bond
- Generating ZR reports

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/zodiacal_releasing_cookbook.py

Key Concepts:
- **Lot of Fortune**: Body, health, circumstances, material life
- **Lot of Spirit**: Mind, career, actions, vocation
- **L1 (Major)**: Life chapters lasting years to decades
- **L2 (Sub)**: Sub-periods within L1, lasting months to years
- **L3/L4**: Finer timing divisions (weeks/days)
- **Peak (10th from Lot)**: Heightened activity and visibility
- **Angular (1st, 4th, 7th, 10th)**: Significant, impactful periods
- **Loosing of the Bond**: When L2+ enters an angular sign, shifts focus
"""

from datetime import UTC, datetime

from stellium import ChartBuilder
from stellium.engines.releasing import (
    ZodiacalReleasingAnalyzer,
    ZodiacalReleasingEngine,
)
from stellium.presentation import ReportBuilder


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


# =============================================================================
# PART 1: BASIC SETUP
# =============================================================================


def example_1_basic_setup():
    """
    Example 1: Basic ZR Setup with ChartBuilder

    Add ZodiacalReleasingAnalyzer to calculate ZR timelines.
    """
    section_header("Example 1: Basic ZR Setup")

    # Calculate chart with ZR for Part of Fortune
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    # Access the ZR timeline
    timeline = chart.zodiacal_releasing("Part of Fortune")

    print(f"Lot Sign: {timeline.lot_sign}")
    print(f"Birth Date: {timeline.birth_date.strftime('%B %d, %Y')}")
    print(f"Max Level Calculated: {timeline.max_level}")


def example_2_multiple_lots():
    """
    Example 2: Calculate Multiple Lots

    Fortune for body/circumstances, Spirit for mind/career.
    """
    section_header("Example 2: Multiple Lots")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )

    fortune = chart.zodiacal_releasing("Part of Fortune")
    spirit = chart.zodiacal_releasing("Part of Spirit")

    print(f"Fortune Lot Sign: {fortune.lot_sign}")
    print(f"Spirit Lot Sign: {spirit.lot_sign}")
    print()
    print("These different starting points give different life chapter timings!")


# =============================================================================
# PART 2: QUERYING TIMELINES
# =============================================================================


def example_3_snapshot_by_age():
    """
    Example 3: Get ZR Snapshot at a Specific Age

    See what periods are active at any point in life.
    """
    section_header("Example 3: Snapshot by Age")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    # Einstein's "miracle year" was 1905 when he was ~26
    snapshot = chart.zr_at_age(26)

    print("At age 26 (Einstein's Miracle Year, 1905):")
    print(f"  L1: {snapshot.l1.sign} ({snapshot.l1.ruler})")
    print(f"  L2: {snapshot.l2.sign} ({snapshot.l2.ruler})")
    print(f"  Active Rulers: {', '.join(snapshot.rulers)}")
    print(f"  Is Peak: {snapshot.is_peak}")
    print(f"  Is Loosing of Bond: {snapshot.is_lb}")


def example_4_snapshot_by_date():
    """
    Example 4: Get ZR Snapshot at a Specific Date

    Query by actual date rather than age.
    """
    section_header("Example 4: Snapshot by Date")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    # Query a specific date
    query_date = datetime(2025, 1, 1, tzinfo=UTC)
    snapshot = chart.zr_at_date(query_date)

    print("On January 1, 2025:")
    print(f"  Age: {snapshot.age:.1f} years")
    print(f"  L1: {snapshot.l1.sign} ({snapshot.l1.ruler})")
    print(f"  L2: {snapshot.l2.sign} ({snapshot.l2.ruler})")
    if snapshot.l3:
        print(f"  L3: {snapshot.l3.sign} ({snapshot.l3.ruler})")
    if snapshot.l4:
        print(f"  L4: {snapshot.l4.sign} ({snapshot.l4.ruler})")


def example_5_l1_timeline():
    """
    Example 5: View L1 Timeline (Major Life Chapters)

    See all major periods and when they occur.
    """
    section_header("Example 5: L1 Timeline")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    timeline = chart.zodiacal_releasing("Part of Fortune")
    l1_periods = timeline.l1_periods()

    print(f"L1 Timeline from {timeline.lot_sign}:\n")
    print(f"{'Sign':<12} {'Ruler':<10} {'Ages':<12} {'Status':<20}")
    print("-" * 54)

    for period in l1_periods:
        age_start = (period.start - timeline.birth_date).days / 365.25
        age_end = (period.end - timeline.birth_date).days / 365.25

        status = ""
        if period.is_peak:
            status = "Peak (10th)"
        elif period.is_angular:
            status = f"Angular ({period.angle_from_lot})"

        print(f"{period.sign:<12} {period.ruler:<10} {age_start:3.0f} - {age_end:3.0f}    {status}")


# =============================================================================
# PART 3: FINDING SIGNIFICANT PERIODS
# =============================================================================


def example_6_find_peaks():
    """
    Example 6: Find Peak Periods

    Peaks (10th from Lot) are times of heightened visibility and activity.
    """
    section_header("Example 6: Find Peak Periods")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"], lifespan=100))
        .calculate()
    )

    timeline = chart.zodiacal_releasing("Part of Fortune")

    # Find L2 peaks (more common, happen within each L1)
    l2_peaks = timeline.find_peaks(level=2)

    print("L2 Peak Periods (10th from Lot):")
    print(f"Found {len(l2_peaks)} peak periods\n")

    # Show first 5
    for period in l2_peaks[:5]:
        start_str = period.start.strftime("%b %Y")
        end_str = period.end.strftime("%b %Y")
        print(f"  {period.sign} ({period.ruler}): {start_str} - {end_str}")


def example_7_find_loosing_bonds():
    """
    Example 7: Find Loosing of the Bond Periods

    Loosing of the Bond occurs when L2+ enters an angular sign,
    indicating a shift in focus or new chapter beginning.
    """
    section_header("Example 7: Find Loosing of the Bond")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    timeline = chart.zodiacal_releasing("Part of Fortune")
    lb_periods = timeline.find_loosing_bonds(level=2)

    print("L2 Loosing of the Bond Periods:")
    print(f"Found {len(lb_periods)} LB periods\n")

    # Show first 5
    for period in lb_periods[:5]:
        start_str = period.start.strftime("%b %Y")
        end_str = period.end.strftime("%b %Y")
        angle = f"({period.angle_from_lot} from Lot)"
        print(f"  {period.sign} ({period.ruler}): {start_str} - {end_str} {angle}")


# =============================================================================
# PART 4: REPORTS
# =============================================================================


def example_8_basic_report():
    """
    Example 8: Basic ZR Report

    Use ReportBuilder to generate formatted ZR output.
    """
    section_header("Example 8: Basic ZR Report")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )

    # Generate report at age 30
    (
        ReportBuilder()
        .from_chart(chart)
        .with_zodiacal_releasing(lots="Part of Fortune", query_age=30)
        .render()
    )


def example_9_snapshot_only_report():
    """
    Example 9: Snapshot-Only Report

    Show just the current state without the timeline.
    """
    section_header("Example 9: Snapshot-Only Report")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )

    # Snapshot only, for current time
    (
        ReportBuilder()
        .from_chart(chart)
        .with_zodiacal_releasing(mode="snapshot")
        .render()
    )


def example_10_timeline_only_report():
    """
    Example 10: Timeline-Only Report

    Show just the L1 timeline for life overview.
    """
    section_header("Example 10: Timeline-Only Report")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )

    # Timeline only
    (
        ReportBuilder()
        .from_chart(chart)
        .with_zodiacal_releasing(mode="timeline")
        .render()
    )


def example_11_full_report():
    """
    Example 11: Full Report with ZR

    ZR is included in preset_full() for comprehensive analysis.
    """
    section_header("Example 11: Full Report (excerpt)")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .with_aspects()
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )

    # Just show ZR portion for this example
    (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_zodiacal_releasing()
        .render()
    )


# =============================================================================
# PART 5: ADVANCED USAGE
# =============================================================================


def example_12_direct_engine_usage():
    """
    Example 12: Direct Engine Usage

    Use ZodiacalReleasingEngine directly for more control.
    """
    section_header("Example 12: Direct Engine Usage")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Create engine directly
    engine = ZodiacalReleasingEngine(
        chart,
        lot="Part of Fortune",
        max_level=4,  # Calculate all 4 levels
        lifespan=100,  # Calculate to age 100
    )

    print(f"Lot Position: {engine.lot_position:.2f}° {engine.lot_sign}")
    print(f"Angular Signs from Lot: {list(engine.angular_signs.keys())}")
    print()

    # Get all periods
    periods = engine.calculate_all_periods()

    print(f"Total L1 periods: {len(periods[1])}")
    print(f"Total L2 periods: {len(periods[2])}")
    print(f"Total L3 periods: {len(periods[3])}")
    print(f"Total L4 periods: {len(periods[4])}")


def example_13_custom_lifespan():
    """
    Example 13: Custom Lifespan

    Calculate ZR for different lifespans.
    """
    section_header("Example 13: Custom Lifespan")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_analyzer(
            ZodiacalReleasingAnalyzer(
                ["Part of Fortune"],
                max_level=2,  # Only L1 and L2 for faster calculation
                lifespan=120,  # Extended lifespan
            )
        )
        .calculate()
    )

    timeline = chart.zodiacal_releasing("Part of Fortune")
    l1_periods = timeline.l1_periods()

    print(f"With 120-year lifespan, {len(l1_periods)} L1 periods calculated:")
    for period in l1_periods:
        age_start = (period.start - timeline.birth_date).days / 365.25
        age_end = (period.end - timeline.birth_date).days / 365.25
        print(f"  {period.sign}: ages {age_start:.0f} - {age_end:.0f}")


def example_14_comparing_fortune_spirit():
    """
    Example 14: Comparing Fortune vs Spirit

    Fortune and Spirit often have different timings and themes.
    """
    section_header("Example 14: Fortune vs Spirit Comparison")

    chart = (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )

    fortune = chart.zodiacal_releasing("Part of Fortune")
    spirit = chart.zodiacal_releasing("Part of Spirit")

    # Compare at age 30
    fortune_snap = fortune.at_age(30)
    spirit_snap = spirit.at_age(30)

    print("At age 30:")
    print()
    print("Part of Fortune (body, circumstances, material):")
    print(f"  L1: {fortune_snap.l1.sign} ({fortune_snap.l1.ruler})")
    print(f"  L2: {fortune_snap.l2.sign} ({fortune_snap.l2.ruler})")
    print(f"  Peak: {fortune_snap.is_peak}, LB: {fortune_snap.is_lb}")
    print()
    print("Part of Spirit (mind, career, vocation):")
    print(f"  L1: {spirit_snap.l1.sign} ({spirit_snap.l1.ruler})")
    print(f"  L2: {spirit_snap.l2.sign} ({spirit_snap.l2.ruler})")
    print(f"  Peak: {spirit_snap.is_peak}, LB: {spirit_snap.is_lb}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  ZODIACAL RELEASING COOKBOOK")
    print("  Hellenistic Predictive Timing Technique")
    print("=" * 70)

    # Part 1: Basic Setup
    example_1_basic_setup()
    example_2_multiple_lots()

    # Part 2: Querying Timelines
    example_3_snapshot_by_age()
    example_4_snapshot_by_date()
    example_5_l1_timeline()

    # Part 3: Finding Significant Periods
    example_6_find_peaks()
    example_7_find_loosing_bonds()

    # Part 4: Reports
    example_8_basic_report()
    example_9_snapshot_only_report()
    example_10_timeline_only_report()
    example_11_full_report()

    # Part 5: Advanced Usage
    example_12_direct_engine_usage()
    example_13_custom_lifespan()
    example_14_comparing_fortune_spirit()

    print("\n" + "=" * 70)
    print("  COOKBOOK COMPLETE!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
