#!/usr/bin/env python3
"""
BaZi (Four Pillars / 八字) Cookbook — Comprehensive Examples

This cookbook demonstrates Stellium's Chinese astrology BaZi system,
from basic chart calculation to advanced Day Master strength analysis.

Contents:
    Part 1: Basic Chart Calculation
        1. Simple chart from datetime
        2. Chart with timezone
        3. Accessing chart data
        4. Eight Characters (八字)

    Part 2: Pillars Deep Dive
        5. Year Pillar and Li Chun boundary
        6. Month Pillar and Solar Terms
        7. Day Pillar (the 60-day cycle)
        8. Hour Pillar (the twelve double-hours)
        9. Hidden Stems (藏干)

    Part 3: Five Elements (Wu Xing / 五行)
        10. Element cycles (generative and controlling)
        11. Element counting in a chart
        12. Polarity (Yin/Yang) balance

    Part 4: Ten Gods Analysis (十神)
        13. Basic Ten Gods
        14. Ten Gods by category
        15. Ten Gods for specific pillars

    Part 5: Day Master Strength (日主强弱)
        16. Basic strength analysis
        17. Seasonal strength
        18. Comparing charts — strong vs weak Day Masters
        19. Favorable and unfavorable elements

    Part 6: Rendering and Export
        20. Rich terminal output
        21. Prose output
        22. JSON export

    Part 7: Advanced
        23. Direct engine usage (BaZiEngine with manual timezone)

Run with:
    source ~/.zshrc && pyenv activate starlight && python examples/bazi_cookbook.py
"""

from datetime import datetime

from stellium import ChartBuilder
from stellium.chinese import BaZiEngine
from stellium.chinese.bazi import (
    BaziProseRenderer,
    BaziRichRenderer,
    analyze_ten_gods,
    count_ten_god_categories,
)
from stellium.chinese.core import Element


def section_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# =============================================================================
# PART 1: BASIC CHART CALCULATION
# =============================================================================


def example_01_simple_chart():
    """
    Example 1: Simple Chart via ChartBuilder

    The easiest way to get a BaZi chart — use ChartBuilder.from_details()
    with .bazi(). Location is geocoded and timezone handled automatically,
    just like Western chart calculation.
    """
    section_header("Example 1: Simple Chart via ChartBuilder")

    from stellium import ChartBuilder

    bazi = ChartBuilder.from_details("2000-06-15 12:00", "Beijing, China").bazi()

    print(f"Eight Characters: {bazi.hanzi}")
    print(f"Day Master: {bazi.day_master.hanzi} ({bazi.day_master.element.english})")
    print(f"Birth: {bazi.birth_datetime}")


def example_02_from_western_chart():
    """
    Example 2: BaZi from an Existing Western Chart

    If you already have a calculated Western chart, call .bazi()
    on it to get the Four Pillars. The timezone and location are
    reused automatically.
    """
    section_header("Example 2: BaZi from Western Chart")

    from stellium import ChartBuilder

    # Calculate Western chart first
    chart = (
        ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
        .with_aspects()
        .calculate()
    )

    # Get BaZi from the same birth data — no re-specifying timezone!
    bazi = chart.bazi()

    print(f"Western Sun: {chart.get_object('Sun').sign}")
    print(f"BaZi Eight Characters: {bazi.hanzi}")
    print(
        f"BaZi Day Master: {bazi.day_master.hanzi} ({bazi.day_master_element.english})"
    )
    print("\nBoth from the same birth data, zero duplication.")


def example_03_accessing_chart_data():
    """
    Example 3: Accessing Chart Data

    Each pillar has a stem and branch with rich metadata.
    """
    section_header("Example 3: Accessing Chart Data")

    chart = ChartBuilder.from_details("1990-10-15 08:30", "Beijing, China").bazi()

    for name, pillar in [
        ("Year", chart.year),
        ("Month", chart.month),
        ("Day", chart.day),
        ("Hour", chart.hour),
    ]:
        print(f"{name} Pillar: {pillar.hanzi} ({pillar.pinyin})")
        print(
            f"  Stem: {pillar.stem.hanzi} ({pillar.stem.element.english} "
            f"{pillar.stem.polarity.value})"
        )
        print(
            f"  Branch: {pillar.branch.hanzi} ({pillar.branch.animal}, "
            f"{pillar.branch.element.english})"
        )
        print()


def example_04_eight_characters():
    """
    Example 4: The Eight Characters (八字)

    "BaZi" literally means "eight characters" — four stem-branch pairs.
    Each pair contributes two Chinese characters.
    """
    section_header("Example 4: Eight Characters")

    # Famous charts — ChartBuilder handles timezone from location
    famous = [
        ("Albert Einstein", "1879-03-14 11:30", "Ulm, Germany"),
        ("Bruce Lee", "1940-11-27 08:00", "San Francisco, CA"),
    ]

    for name, birth, location in famous:
        chart = ChartBuilder.from_details(birth, location).bazi()
        print(f"{name}: {chart.hanzi}")
        print(
            f"  Year: {chart.year.hanzi}  Month: {chart.month.hanzi}  "
            f"Day: {chart.day.hanzi}  Hour: {chart.hour.hanzi}"
        )
        print(
            f"  Day Master: {chart.day_master.hanzi} "
            f"({chart.day_master_element.english})"
        )
        print()


# =============================================================================
# PART 2: PILLARS DEEP DIVE
# =============================================================================


def example_05_year_pillar_li_chun():
    """
    Example 5: Year Pillar and Li Chun

    The Chinese year starts at Li Chun (Start of Spring, ~Feb 4),
    not January 1. A January birth belongs to the PREVIOUS year's pillar.
    """
    section_header("Example 5: Year Pillar and Li Chun")

    # Use Beijing coordinates for timezone accuracy
    # 2024 is a Dragon year (Jia Chen / 甲辰)
    # But a Jan 15 2024 birth is still in the 2023 Chinese year
    before = ChartBuilder.from_details("2024-01-15 12:00", (39.9, 116.4)).bazi()
    after = ChartBuilder.from_details("2024-03-01 12:00", (39.9, 116.4)).bazi()

    print(f"Jan 15, 2024: {before.year.hanzi} ({before.year.branch.animal})")
    print("  → Still in 2023 Chinese year (before Li Chun)")
    print(f"Mar 1, 2024:  {after.year.hanzi} ({after.year.branch.animal})")
    print("  → Now in 2024 Chinese year (after Li Chun)")


def example_06_month_pillar_solar_terms():
    """
    Example 6: Month Pillar and Solar Terms

    Month branches follow the solar terms (Jie Qi), not calendar months.
    The first BaZi month starts at Li Chun with the Tiger branch (寅).
    """
    section_header("Example 6: Month Pillar and Solar Terms")

    print("Month progression through 2024:")
    dates = [
        ("2024-02-10 12:00", "Feb 10"),
        ("2024-03-10 12:00", "Mar 10"),
        ("2024-04-10 12:00", "Apr 10"),
        ("2024-05-10 12:00", "May 10"),
        ("2024-06-10 12:00", "Jun 10"),
        ("2024-07-10 12:00", "Jul 10"),
    ]

    for birth, label in dates:
        chart = ChartBuilder.from_details(birth, (39.9, 116.4)).bazi()
        print(
            f"  {label}: {chart.month.hanzi} ({chart.month.branch.animal} month, "
            f"{chart.month.stem_element.english})"
        )


def example_07_day_pillar():
    """
    Example 7: Day Pillar (the 60-day cycle)

    The day pillar cycles through all 60 stem-branch combinations
    continuously. It's the most personal pillar — the Day Master
    (day stem) represents YOU.
    """
    section_header("Example 7: Day Pillar")

    print("Three consecutive days:")
    for day in range(15, 18):
        chart = ChartBuilder.from_details(
            f"2024-06-{day:02d} 12:00", "London, UK"
        ).bazi()
        print(
            f"  June {day}: {chart.day.hanzi} ({chart.day.pinyin}) "
            f"— Day Master: {chart.day_master.hanzi} "
            f"({chart.day_master_element.english})"
        )


def example_08_hour_pillar():
    """
    Example 8: Hour Pillar (the twelve double-hours)

    Each day is divided into 12 two-hour periods, each ruled by
    an Earthly Branch. The Chinese day starts at 23:00 (Zi hour).
    """
    section_header("Example 8: Hour Pillar")

    hours = [
        ("23:30", "Late night (Zi hour)"),
        ("01:00", "After midnight (Chou hour)"),
        ("07:00", "Morning (Chen hour)"),
        ("12:00", "Noon (Wu hour)"),
        ("17:00", "Afternoon (You hour)"),
        ("21:00", "Evening (Hai hour)"),
    ]

    print("Hour pillar changes through the day (June 15, 2024):")
    for time_str, label in hours:
        chart = ChartBuilder.from_details(
            f"2024-06-15 {time_str}", "Beijing, China"
        ).bazi()
        print(
            f"  {time_str} {label:30s} {chart.hour.hanzi} ({chart.hour.branch.animal})"
        )


def example_09_hidden_stems():
    """
    Example 9: Hidden Stems (藏干)

    Each Earthly Branch contains 1-3 "hidden" Heavenly Stems.
    These represent the internal energies of each branch:
    - Main qi (本气): the primary hidden stem
    - Middle qi (中气): secondary (if present)
    - Residual qi (余气): tertiary (if present)
    """
    section_header("Example 9: Hidden Stems")

    chart = ChartBuilder.from_details("1990-10-15 08:30", "Beijing, China").bazi()

    for name, pillar in [
        ("Year", chart.year),
        ("Month", chart.month),
        ("Day", chart.day),
        ("Hour", chart.hour),
    ]:
        hidden = pillar.branch.get_hidden_stem_objects()
        hidden_str = ", ".join(f"{h.hanzi}({h.element.hanzi})" for h in hidden)
        print(f"{name} {pillar.branch.hanzi} ({pillar.branch.animal}): {hidden_str}")


# =============================================================================
# PART 3: FIVE ELEMENTS
# =============================================================================


def example_10_element_cycles():
    """
    Example 10: Element Cycles (Generative and Controlling)

    The Five Elements interact in two cycles:
    - Generative (生): Wood → Fire → Earth → Metal → Water → Wood
    - Controlling (克): Wood → Earth → Water → Fire → Metal → Wood
    """
    section_header("Example 10: Element Cycles")

    print("Generative cycle (生):")
    for elem in Element:
        print(
            f"  {elem.hanzi} {elem.english} → produces → "
            f"{elem.produces.hanzi} {elem.produces.english}"
        )

    print("\nControlling cycle (克):")
    for elem in Element:
        print(
            f"  {elem.hanzi} {elem.english} → controls → "
            f"{elem.controls.hanzi} {elem.controls.english}"
        )

    print("\nReverse lookups:")
    for elem in Element:
        print(
            f"  {elem.hanzi} {elem.english}: produced by {elem.produced_by.english}, "
            f"controlled by {elem.controlled_by.english}"
        )


def example_11_element_counting():
    """
    Example 11: Element Counting in a Chart

    Count how many of each element appear in the chart.
    Can include or exclude hidden stems.
    """
    section_header("Example 11: Element Counting")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    print(f"Chart: {chart.hanzi}")
    print(f"Day Master: {chart.day_master.hanzi} ({chart.day_master_element.english})")

    print("\nElement count (stems only):")
    for elem, count in chart.element_counts(include_hidden=False).items():
        bar = "█" * count
        print(f"  {elem.hanzi} {elem.english:6s}: {count} {bar}")

    print("\nElement count (with hidden stems):")
    for elem, count in chart.element_counts(include_hidden=True).items():
        bar = "█" * count
        print(f"  {elem.hanzi} {elem.english:6s}: {count} {bar}")


def example_12_polarity_balance():
    """
    Example 12: Polarity (Yin/Yang) Balance

    Check the distribution of Yin and Yang in the chart.
    """
    section_header("Example 12: Polarity Balance")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    counts = chart.polarity_counts()
    total = sum(counts.values())

    print(f"Chart: {chart.hanzi}")
    for polarity, count in counts.items():
        pct = count / total * 100 if total > 0 else 0
        print(f"  {polarity.hanzi} {polarity.value:4s}: {count} ({pct:.0f}%)")


# =============================================================================
# PART 4: TEN GODS ANALYSIS
# =============================================================================


def example_13_basic_ten_gods():
    """
    Example 13: Basic Ten Gods (十神)

    The Ten Gods describe the relationship between the Day Master
    and every other stem in the chart. They reveal the chart's
    dynamics — what supports you, what drains you, what challenges you.
    """
    section_header("Example 13: Basic Ten Gods")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    print(f"Day Master: {chart.day_master.hanzi} ({chart.day_master_element.english})")
    print()

    relations = analyze_ten_gods(chart, include_hidden=False)
    for rel in relations:
        print(
            f"  {rel.stem.hanzi} ({rel.pillar_name:6s}): "
            f"{rel.ten_god.hanzi} {rel.ten_god.english}"
        )


def example_14_ten_gods_by_category():
    """
    Example 14: Ten Gods by Category

    The Ten Gods group into five categories:
    - Self/Companion (比劫): same element — peers, siblings, competitors
    - Output (食伤): element you produce — creativity, expression
    - Wealth (财星): element you control — money, resources, father
    - Power (官杀): element that controls you — authority, pressure, career
    - Resource (印星): element that produces you — support, knowledge, mother
    """
    section_header("Example 14: Ten Gods by Category")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    relations = analyze_ten_gods(chart, include_hidden=True)
    categories = count_ten_god_categories(relations)

    print(f"Day Master: {chart.day_master.hanzi} ({chart.day_master_element.english})")
    print("\nCategory distribution (including hidden stems):")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {cat:12s}: {count:2d} {bar}")


def example_15_ten_gods_per_pillar():
    """
    Example 15: Ten Gods for Specific Pillars

    Examine which Ten Gods appear in each pillar position.
    The pillar location gives context — Year = society/ancestors,
    Month = career/parents, Day = self/spouse, Hour = children/legacy.
    """
    section_header("Example 15: Ten Gods Per Pillar")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    relations = analyze_ten_gods(chart, include_hidden=True)

    for pillar_name in ["year", "month", "day", "hour"]:
        pillar_gods = [r for r in relations if r.pillar_name.startswith(pillar_name)]
        gods_str = ", ".join(f"{r.ten_god.hanzi}" for r in pillar_gods)
        print(f"  {pillar_name.capitalize():6s}: {gods_str}")


# =============================================================================
# PART 5: DAY MASTER STRENGTH
# =============================================================================


def example_16_basic_strength():
    """
    Example 16: Basic Strength Analysis

    The Day Master strength determines whether you need more support
    or more challenge in your chart. This is fundamental to BaZi
    interpretation — it determines which elements are favorable.

    Use .strength() directly on the BaZi chart — no separate import needed.
    """
    section_header("Example 16: Basic Strength Analysis")

    from stellium import ChartBuilder

    bazi = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    # .strength() is a method on the chart itself
    result = bazi.strength()
    print(result.display())


def example_17_seasonal_strength():
    """
    Example 17: Seasonal Strength

    The same Day Master element has different strength depending
    on the birth month. Wood is strongest in spring, weakest in autumn.
    """
    section_header("Example 17: Seasonal Strength")

    print("Same person, different birth months:")
    print(
        f"  {'Month':<10} {'Season':<12} {'DM Element':<12} {'Seasonal':>8} {'Strength'}"
    )
    print(f"  {'-' * 60}")

    # Sample different months to show seasonal variation
    for month, season in [
        (2, "Spring"),
        (5, "Summer"),
        (8, "Autumn"),
        (11, "Winter"),
    ]:
        bazi = ChartBuilder.from_details(
            f"1990-{month:02d}-15 12:00", (39.9, 116.4)
        ).bazi()
        result = bazi.strength()
        print(
            f"  {month:02d}/15      {season:<12} {result.day_master_element.english:<12} "
            f"{result.seasonal_score:>+8d} {result.strength.english}"
        )


def example_18_strong_vs_weak():
    """
    Example 18: Comparing Charts — Strong vs Weak Day Masters

    A Water Day Master born in winter (Water season) vs summer
    (Fire season) will have very different strength profiles.
    """
    section_header("Example 18: Strong vs Weak Day Masters")

    # Winter birth (Water season — Water DM will be strong)
    winter = ChartBuilder.from_details("2000-12-21 00:00", (39.9, 116.4)).bazi()
    winter_result = winter.strength()

    # Summer birth (Fire season — different dynamics)
    summer = ChartBuilder.from_details("2000-07-15 12:00", (39.9, 116.4)).bazi()
    summer_result = summer.strength()

    for label, chart, result in [
        ("Winter birth", winter, winter_result),
        ("Summer birth", summer, summer_result),
    ]:
        print(f"{label}: {chart.hanzi}")
        print(
            f"  Day Master: {result.day_master.hanzi} ({result.day_master_element.english})"
        )
        print(
            f"  Strength: {result.strength.hanzi} ({result.strength.english}) "
            f"[score: {result.score:.1f}]"
        )
        print(
            f"  Seasonal: {result.seasonal_score:+d}, "
            f"Roots: {result.root_count}, "
            f"Support: {result.support_count}, "
            f"Drain: {result.drain_count}"
        )
        print()


def example_19_favorable_elements():
    """
    Example 19: Favorable and Unfavorable Elements

    Based on whether the Day Master is strong or weak, different
    elements become favorable (用神) or unfavorable (忌神).

    Strong DM → needs draining (Output, Wealth, Power are good)
    Weak DM → needs support (Companion, Resource are good)
    """
    section_header("Example 19: Favorable & Unfavorable Elements")

    from stellium import ChartBuilder

    bazi = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()
    result = bazi.strength()

    print(
        f"Day Master: {result.day_master.hanzi} ({result.day_master_element.english})"
    )
    print(f"Strength: {result.strength.hanzi} ({result.strength.english})")
    print()
    print("Favorable elements (用神):")
    for elem in result.favorable_elements:
        print(f"  {elem.hanzi} {elem.english}")
    print("\nUnfavorable elements (忌神):")
    for elem in result.unfavorable_elements:
        print(f"  {elem.hanzi} {elem.english}")


# =============================================================================
# PART 6: RENDERING AND EXPORT
# =============================================================================


def example_20_rich_terminal():
    """
    Example 20: Rich Terminal Output

    Beautiful formatted table with colors, Ten Gods, and hidden stems.
    """
    section_header("Example 20: Rich Terminal Output")

    chart = ChartBuilder.from_details("1879-03-14 11:30", "Ulm, Germany").bazi()

    renderer = BaziRichRenderer()
    output = renderer.render_chart(chart)
    print(output)


def example_21_prose_output():
    """
    Example 21: Prose Output

    Natural language description of the chart, suitable for
    conversation or LLM prompts.
    """
    section_header("Example 21: Prose Output")

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    renderer = BaziProseRenderer()
    print(renderer.render(chart))


def example_22_json_export():
    """
    Example 22: JSON Export

    Export the chart to a JSON-serializable dictionary.
    """
    section_header("Example 22: JSON Export")

    import json

    chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()

    data = chart.to_dict()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:500] + "\n  ...")

    # Strength analysis also exports
    result = chart.strength()
    strength_data = result.to_dict()
    print("\nStrength export:")
    print(json.dumps(strength_data, indent=2, ensure_ascii=False))


# =============================================================================
# PART 7: ADVANCED — DIRECT ENGINE USAGE
# =============================================================================


def example_23_direct_engine():
    """
    Example 23: Advanced — Direct Engine Usage

    For most cases, ChartBuilder.from_details().bazi() is the best path —
    it handles geocoding and timezone automatically.

    But if you need fine control over the timezone offset (e.g., you already
    know the exact UTC offset and don't want geocoding overhead), you can
    use BaZiEngine directly with a manual timezone_offset_hours.

    This is also useful for:
    - Batch processing with a known fixed offset
    - Historical dates where timezone databases may be unreliable
    - Testing and benchmarking without network calls
    """
    section_header("Example 23: Advanced — Direct Engine Usage")

    # Direct engine: you supply the UTC offset yourself
    engine = BaZiEngine(timezone_offset_hours=-8)
    chart = engine.calculate(datetime(1994, 1, 6, 11, 47))

    print(f"Direct engine result: {chart.hanzi}")
    print(f"Day Master: {chart.day_master.hanzi} ({chart.day_master_element.english})")
    print()

    # Compare: same birth via ChartBuilder (handles timezone automatically)
    builder_chart = ChartBuilder.from_details(
        "1994-01-06 11:47", "Palo Alto, CA"
    ).bazi()

    print(f"ChartBuilder result: {builder_chart.hanzi}")
    print(
        f"Day Master: {builder_chart.day_master.hanzi} "
        f"({builder_chart.day_master_element.english})"
    )
    print()
    print("Both produce the same chart. Use ChartBuilder for convenience,")
    print("or BaZiEngine directly when you need explicit timezone control.")


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("\n" + "=" * 60)
    print("  八字 BAZI (FOUR PILLARS) COOKBOOK")
    print("  Stellium - Chinese Astrology Module")
    print("=" * 60)

    # Part 1: Basic Chart Calculation
    example_01_simple_chart()
    example_02_from_western_chart()
    example_03_accessing_chart_data()
    example_04_eight_characters()

    # Part 2: Pillars Deep Dive
    example_05_year_pillar_li_chun()
    example_06_month_pillar_solar_terms()
    example_07_day_pillar()
    example_08_hour_pillar()
    example_09_hidden_stems()

    # Part 3: Five Elements
    example_10_element_cycles()
    example_11_element_counting()
    example_12_polarity_balance()

    # Part 4: Ten Gods
    example_13_basic_ten_gods()
    example_14_ten_gods_by_category()
    example_15_ten_gods_per_pillar()

    # Part 5: Day Master Strength
    example_16_basic_strength()
    example_17_seasonal_strength()
    example_18_strong_vs_weak()
    example_19_favorable_elements()

    # Part 6: Rendering and Export
    example_20_rich_terminal()
    example_21_prose_output()
    example_22_json_export()

    # Part 7: Advanced
    example_23_direct_engine()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
