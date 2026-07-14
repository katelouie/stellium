#!/usr/bin/env python3
"""
Dignities & Dispositors Cookbook — Comprehensive Examples

This cookbook demonstrates Stellium's full essential dignity, accidental dignity,
mutual reception, and dispositor graph systems.

Contents:
    Part 1: Essential Dignities
        1. Traditional essential dignities (scoring breakdown)
        2. Modern essential dignities (outer planet rulerships)
        3. Comparing traditional vs modern for a full chart
        4. Peregrine planets (no essential dignity)

    Part 2: Accidental Dignities
        5. House-based accidental dignities (angular/succedent/cadent)
        6. Universal conditions (retrograde, cazimi, combust, speed)
        7. Combined essential + accidental scoring

    Part 3: Mutual Reception
        8. Mutual reception by domicile
        9. Mutual reception by exaltation and mixed
        10. Programmatic mutual reception analysis

    Part 4: Dispositor Graphs
        11. Planetary dispositors and final dispositor
        12. House-based dispositors (life area flow)
        13. Dispositor graph visualization (Graphviz SVG)

    Part 5: Reports
        14. Full dignity report via ReportBuilder

Run with:
    source ~/.zshrc && pyenv activate starlight && python examples/dignities_cookbook.py
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ReportBuilder
from stellium.components.dignity import (
    AccidentalDignityComponent,
    DignityComponent,
)
from stellium.engines.dignities import (
    ModernDignityCalculator,
    MutualReceptionAnalyzer,
    TraditionalDignityCalculator,
)
from stellium.engines.dispositors import (
    DispositorEngine,
    dispositor_graph_data,
    render_dispositor_svg,
)

SCRIPT_DIR = Path(__file__).parent
# Where the cookbook writes. Overridable so that running it — from the test
# suite, or the docs build — does not rewrite the artifacts committed in
# examples/, which are regenerated deliberately and not as a side effect.
OUTPUT_ROOT = Path(os.environ.get("STELLIUM_EXAMPLE_OUTPUT", SCRIPT_DIR))
OUTPUT_DIR = OUTPUT_ROOT / "dignities"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_header(title: str) -> None:
    print(f"\n--- {title} ---\n")


# =============================================================================
#  Part 1: Essential Dignities
# =============================================================================


def example_01_traditional_dignities():
    """
    Example 1: Traditional Essential Dignities (Scoring Breakdown)

    The traditional system uses seven planets (Sun through Saturn) and
    evaluates each planet's strength based on its sign placement:

        +5  Domicile (rulership) — planet in its own sign
        +4  Exaltation — planet in its sign of exaltation
        +3  Triplicity ruler — planet rules the element of its sign (by sect)
        +2  Term/Bound — planet rules the Egyptian bound at that degree
        +1  Face/Decan — planet rules the decan at that degree
        -5  Detriment — planet in the sign opposite its domicile
        -4  Fall — planet in the sign opposite its exaltation
         0  Peregrine — no essential dignity at all
    """
    section_header("Part 1: Essential Dignities")
    print_header("Example 1: Traditional Essential Dignities")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    calc = TraditionalDignityCalculator(decans="chaldean")

    # Determine sect (day or night chart) for triplicity rulers
    sun = chart.get_object("Sun")
    asc = chart.get_object("ASC")
    if sun and asc:
        dsc_long = (asc.longitude + 180) % 360
        if asc.longitude < dsc_long:
            sect = "night" if asc.longitude <= sun.longitude < dsc_long else "day"
        else:
            sect = (
                "night"
                if sun.longitude >= asc.longitude or sun.longitude < dsc_long
                else "day"
            )
    else:
        sect = "day"

    print(f"Chart: Albert Einstein ({sect} chart)\n")
    print(f"{'Planet':<10} {'Sign':<14} {'Score':>5}  {'Dignities'}")
    print("-" * 60)

    traditional_planets = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
    ]
    for name in traditional_planets:
        pos = chart.get_object(name)
        if pos is None:
            continue
        result = calc.calculate_dignities(pos, sect)
        score = result.get("score", 0)
        dignity_list = result.get("dignities", [])
        # Filter out 'peregrine' for display — we'll show it separately
        display_dignities = [d for d in dignity_list if d != "peregrine"]
        dignity_str = ", ".join(display_dignities) if display_dignities else "Peregrine"
        print(f"{name:<10} {pos.sign:<14} {score:>+5}  {dignity_str}")

    print(f"\nInterpretation: {result.get('interpretation', '')}")


def example_02_modern_dignities():
    """
    Example 2: Modern Essential Dignities

    The modern system adds outer planet rulerships:
        Uranus  -> Aquarius (traditional: Saturn)
        Neptune -> Pisces   (traditional: Jupiter)
        Pluto   -> Scorpio  (traditional: Mars)
    """
    print_header("Example 2: Modern Essential Dignities")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    calc = ModernDignityCalculator(decans="chaldean")

    # Check outer planets — these only have dignities in the modern system
    outer_planets = ["Uranus", "Neptune", "Pluto"]

    print("Outer planet dignities (modern system only):\n")
    for name in outer_planets:
        pos = chart.get_object(name)
        if pos is None:
            continue
        result = calc.calculate_dignities(pos)
        score = result.get("score", 0)
        dignity_list = result.get("dignities", [])
        display = [d for d in dignity_list if d != "peregrine"]
        dignity_str = ", ".join(display) if display else "Peregrine"
        print(f"  {name:<10} in {pos.sign:<14} score: {score:>+3}  ({dignity_str})")


def example_03_traditional_vs_modern():
    """
    Example 3: Comparing Traditional vs Modern for a Full Chart

    Some planets score differently between systems. The most notable
    differences are for planets in Aquarius, Pisces, and Scorpio where
    rulership assignments change.
    """
    print_header("Example 3: Traditional vs Modern Comparison")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    trad_calc = TraditionalDignityCalculator()
    modern_calc = ModernDignityCalculator()

    print(f"{'Planet':<10} {'Sign':<14} {'Trad':>5} {'Modern':>7}  {'Difference'}")
    print("-" * 55)

    all_planets = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]
    for name in all_planets:
        pos = chart.get_object(name)
        if pos is None:
            continue
        trad = trad_calc.calculate_dignities(pos)
        mod = modern_calc.calculate_dignities(pos)
        trad_score = trad.get("score", 0)
        mod_score = mod.get("score", 0)
        diff = mod_score - trad_score
        diff_str = f"{diff:>+3}" if diff != 0 else "  ="
        print(f"{name:<10} {pos.sign:<14} {trad_score:>+5} {mod_score:>+7}  {diff_str}")


def example_04_peregrine():
    """
    Example 4: Peregrine Planets

    A peregrine planet has NO essential dignity — it's a stranger in
    the sign it occupies. Peregrine planets are considered weakened
    in traditional astrology; they lack the support structure that
    dignity provides. Think of them as guests in someone else's house
    with no connections to the host.
    """
    print_header("Example 4: Peregrine Planets")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    calc = TraditionalDignityCalculator()

    peregrines = []
    traditional_planets = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
    ]
    for name in traditional_planets:
        pos = chart.get_object(name)
        if pos is None:
            continue
        result = calc.calculate_dignities(pos)
        if result.get("is_peregrine"):
            peregrines.append((name, pos.sign, pos.sign_degree))

    if peregrines:
        print("Peregrine planets (no essential dignity):\n")
        for name, sign, degree in peregrines:
            print(f"  {name} at {degree:.1f} {sign}")
        print(
            f"\n{len(peregrines)} of 7 traditional planets are peregrine — "
            "they lack essential dignity support."
        )
    else:
        print("No peregrine planets — every traditional planet has some dignity!")


# =============================================================================
#  Part 2: Accidental Dignities
# =============================================================================


def example_05_house_accidental():
    """
    Example 5: House-Based Accidental Dignities

    Accidental dignity comes from a planet's circumstances rather than
    its sign placement. House position is the primary accidental factor:

        Angular houses  (1, 4, 7, 10): +5 — strongest placement
        Succedent houses (2, 5, 8, 11): +3 — moderate strength
        Cadent houses   (3, 6, 9, 12): +1 — weakest placement

    Planetary joy (planet in its preferred house) adds +5:
        Mercury=1st, Moon=3rd, Venus=5th, Mars=6th,
        Sun=9th, Jupiter=11th, Saturn=12th
    """
    section_header("Part 2: Accidental Dignities")
    print_header("Example 5: House-Based Accidental Dignities")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(AccidentalDignityComponent())
        .calculate()
    )

    acc_data = chart.metadata.get("accidental_dignities", {})
    default_system = chart.default_house_system

    print(f"House system: {default_system}\n")
    print(f"{'Planet':<10} {'House':>5}  {'Score':>5}  {'Conditions'}")
    print("-" * 60)

    for planet_name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        planet_data = acc_data.get(planet_name, {})
        by_system = planet_data.get("by_system", {})
        system_data = by_system.get(default_system, {})
        house = system_data.get("house", "?")
        house_score = system_data.get("score", 0)
        conditions = [c["type"] for c in system_data.get("conditions", [])]
        print(
            f"{planet_name:<10} {house:>5}  {house_score:>+5}  {', '.join(conditions)}"
        )


def example_06_universal_conditions():
    """
    Example 6: Universal Accidental Conditions

    These conditions apply regardless of house system:

        Direct motion:      +4
        Retrograde:         -5
        Swift in motion:    +2 (>120% of average daily speed)
        Slow in motion:     -2 (<30% of average daily speed)
        Cazimi:             +5 (within 17' of Sun — "in the heart")
        Combust:            -4 (within 8 degrees of Sun)
        Under the beams:    -5 (within 15 degrees of Sun)
    """
    print_header("Example 6: Universal Accidental Conditions")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(AccidentalDignityComponent())
        .calculate()
    )

    acc_data = chart.metadata.get("accidental_dignities", {})

    print(f"{'Planet':<10} {'Score':>5}  {'Conditions'}")
    print("-" * 60)

    for planet_name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        planet_data = acc_data.get(planet_name, {})
        universal = planet_data.get("universal", {})
        score = universal.get("score", 0)
        conditions = universal.get("conditions", [])
        cond_strs = [c["type"] for c in conditions]
        print(f"{planet_name:<10} {score:>+5}  {', '.join(cond_strs)}")


def example_07_combined_scoring():
    """
    Example 7: Combined Essential + Accidental Scoring

    A planet's total strength is the sum of its essential dignity score
    (sign placement) and accidental dignity score (house placement and
    circumstances). This gives a complete picture of planetary condition.
    """
    print_header("Example 7: Combined Essential + Accidental Scoring")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(DignityComponent())
        .add_component(AccidentalDignityComponent())
        .calculate()
    )

    ess_data = chart.metadata.get("dignities", {})
    acc_data = chart.metadata.get("accidental_dignities", {})
    planet_dignities = ess_data.get("planet_dignities", {})
    default_system = chart.default_house_system

    print(
        f"{'Planet':<10} {'Essential':>9} {'Accidental':>10} {'Total':>6}  {'Assessment'}"
    )
    print("-" * 65)

    for planet_name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        # Essential score
        pd = planet_dignities.get(planet_name, {})
        trad = pd.get("traditional", {})
        ess_score = trad.get("score", 0)

        # Accidental score (house + universal)
        ad = acc_data.get(planet_name, {})
        house_score = ad.get("by_system", {}).get(default_system, {}).get("score", 0)
        univ_score = ad.get("universal", {}).get("score", 0)
        acc_score = house_score + univ_score

        total = ess_score + acc_score

        if total >= 8:
            assessment = "Very strong"
        elif total >= 4:
            assessment = "Strong"
        elif total >= 0:
            assessment = "Moderate"
        elif total >= -4:
            assessment = "Challenged"
        else:
            assessment = "Very challenged"

        print(
            f"{planet_name:<10} {ess_score:>+9} {acc_score:>+10} {total:>+6}  {assessment}"
        )


# =============================================================================
#  Part 3: Mutual Reception
# =============================================================================


def example_08_reception_domicile():
    """
    Example 8: Mutual Reception by Domicile

    Mutual reception occurs when two planets are each in the sign
    ruled by the other. For example, Mars in Capricorn and Saturn
    in Aries — Mars rules Aries (where Saturn is) and Saturn rules
    Capricorn (where Mars is). This creates a powerful bond: each
    planet can "act as if" it were in its own sign through the
    other's support.

    This is the strongest form of mutual reception.
    """
    section_header("Part 3: Mutual Reception")
    print_header("Example 8: Mutual Reception by Domicile")

    # Use a chart likely to have mutual receptions
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    analyzer = MutualReceptionAnalyzer(system="traditional")

    receptions = analyzer.find_mutual_receptions(chart.positions)

    domicile_receptions = [
        r for r in receptions if r["type"] == "mutual_reception_domicile"
    ]

    if domicile_receptions:
        print("Mutual receptions by domicile (strongest form):\n")
        for r in domicile_receptions:
            print(f"  {r['planet1']} in {r['planet1_sign']}")
            print(f"  {r['planet2']} in {r['planet2_sign']}")
            print(f"  Strength: {r['strength']}")
            print(f"  {r['description']}")
            print()
    else:
        print("No mutual receptions by domicile in this chart.")
        print("(This is common — not every chart has them.)\n")

    # Show what the analyzer checks
    print("The analyzer checks all planet pairs for reciprocal rulership.")
    print(f"Total positions checked: {len(chart.positions)}")


def example_09_reception_exaltation():
    """
    Example 9: Mutual Reception by Exaltation and Mixed

    Beyond domicile, mutual reception can also occur by exaltation
    (both planets in each other's exaltation sign) or mixed (one in
    the other's domicile, the other in the first's exaltation).

    These are considered moderate-strength receptions.
    """
    print_header("Example 9: Exaltation and Mixed Reception")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    analyzer = MutualReceptionAnalyzer(system="traditional")
    receptions = analyzer.find_mutual_receptions(chart.positions)

    exalt = [r for r in receptions if r["type"] == "mutual_reception_exaltation"]
    mixed = [r for r in receptions if r["type"] == "mutual_reception_mixed"]

    print(f"Receptions by exaltation: {len(exalt)}")
    for r in exalt:
        print(f"  {r['description']}")

    print(f"\nMixed receptions (domicile/exaltation): {len(mixed)}")
    for r in mixed:
        print(f"  {r['description']}")

    if not exalt and not mixed:
        print("\nNo exaltation or mixed receptions in this chart.")

    # Also check modern system
    modern_analyzer = MutualReceptionAnalyzer(system="modern")
    modern_receptions = modern_analyzer.find_mutual_receptions(chart.positions)

    print(f"\nModern system finds {len(modern_receptions)} total reception(s)")
    print(f"Traditional system finds {len(receptions)} total reception(s)")


def example_10_reception_via_component():
    """
    Example 10: Mutual Reception via DignityComponent

    When using the ChartBuilder integration path, mutual receptions
    are automatically calculated as part of the DignityComponent
    and stored in the chart metadata alongside the dignity scores.
    """
    print_header("Example 10: Mutual Reception via DignityComponent")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(DignityComponent())
        .calculate()
    )

    dignity_data = chart.metadata.get("dignities", {})
    receptions = dignity_data.get("mutual_receptions", {})

    for system_name, system_receptions in receptions.items():
        print(f"{system_name.title()} system receptions: {len(system_receptions)}")
        for r in system_receptions:
            print(f"  Type: {r['type']}")
            print(
                f"  {r['planet1']} in {r['planet1_sign']} <-> {r['planet2']} in {r['planet2_sign']}"
            )
            print(f"  Strength: {r['strength']}")
            print()

    if not any(receptions.values()):
        print("No mutual receptions found in either system.")
        print("\n(Tip: try other charts — mutual receptions are fairly uncommon.)")


# =============================================================================
#  Part 4: Dispositor Graphs
# =============================================================================


def example_11_planetary_dispositors():
    """
    Example 11: Planetary Dispositors and Final Dispositor

    Dispositors trace the "chain of command" in a chart. Each planet
    is disposed by the ruler of the sign it occupies. Following these
    chains reveals the final dispositor — the planet where all chains
    terminate (a planet in its own sign, like Mars in Aries).

    If no planet is self-disposing, the chains may terminate in a
    mutual reception pair instead.
    """
    section_header("Part 4: Dispositor Graphs")
    print_header("Example 11: Planetary Dispositors")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DispositorEngine(chart)
    result = engine.planetary()

    print(f"Rulership system: {result.rulership_system}")
    print(f"Final dispositor: {result.final_dispositor}\n")

    # Show edges (who disposes whom)
    print("Dispositor edges:")
    for edge in result.edges:
        marker = " (self-disposing)" if edge.source == edge.target else ""
        print(
            f"  {edge.source} in {edge.source_sign} -> disposed by {edge.ruler}{marker}"
        )

    # Show mutual receptions
    if result.mutual_receptions:
        print(f"\nMutual receptions: {len(result.mutual_receptions)}")
        for mr in result.mutual_receptions:
            print(f"  {mr.node1} <-> {mr.node2}")

    # Show a full chain
    print("\nDispositor chains:")
    for _planet, chain in result.chains.items():
        print(f"  {' -> '.join(chain)}")


def example_12_house_dispositors():
    """
    Example 12: House-Based Dispositors

    House dispositors show how life areas flow into and support each
    other. For each house: find the ruler of the cusp sign, then find
    what house that ruler is in. The final dispositor house is the
    life area that supports all others.

    Example: If the 7th house cusp is Libra (ruled by Venus), and
    Venus is in the 10th house, then house 7 flows to house 10 —
    relationships feed into career.
    """
    print_header("Example 12: House-Based Dispositors")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DispositorEngine(chart)
    result = engine.house_based()

    print(f"Final dispositor house: {result.final_dispositor}\n")

    # Show the house flow
    print("House flow (life area connections):")
    for edge in result.edges:
        marker = " (self-disposing)" if edge.source == edge.target else ""
        print(
            f"  House {edge.source} ({edge.source_sign}, ruled by {edge.ruler}) "
            f"-> House {edge.target}{marker}"
        )

    if result.mutual_receptions:
        print("\nHouse mutual receptions:")
        for mr in result.mutual_receptions:
            planet_info = ""
            if mr.planet1 and mr.planet2:
                planet_info = f" (via {mr.planet1} and {mr.planet2})"
            print(f"  House {mr.node1} <-> House {mr.node2}{planet_info}")


def example_13_dispositor_graph():
    """
    Example 13: Dispositor Graph Visualization (SVG)

    Render the planetary + house dispositor graphs to a single SVG with the
    built-in svgwrite renderer (no graphviz dependency). The layered layout
    puts the "leaf" bodies at the top flowing down to the final dispositor,
    using Stellium's visual palette:
        - Gold nodes for final dispositors
        - Bidirectional arrows for mutual-reception edges
    """
    print_header("Example 13: Dispositor Graph Visualization")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    engine = DispositorEngine(chart)

    planetary = engine.planetary()
    house = engine.house_based()

    graphs = [
        {
            "title": "Einstein — Planetary Dispositors",
            **dispositor_graph_data(planetary),
        },
        {"title": "Einstein — House Dispositors", **dispositor_graph_data(house)},
    ]
    output_path = OUTPUT_DIR / "einstein_dispositors.svg"
    render_dispositor_svg(graphs, str(output_path))
    print(f"Saved: {output_path}")

    print(f"\nPlanetary final dispositor: {planetary.final_dispositor}")
    print(f"House final dispositor: {house.final_dispositor}")


# =============================================================================
#  Part 5: Reports
# =============================================================================


def example_14_dignity_report():
    """
    Example 14: Full Dignity Report via ReportBuilder

    The ReportBuilder integrates dignity data into formatted reports.
    Use .with_dignities() to add the essential dignities table.
    The chart must have DignityComponent added during construction.
    """
    section_header("Part 5: Reports")
    print_header("Example 14: Dignity Report via ReportBuilder")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .add_component(DignityComponent())
        .add_component(AccidentalDignityComponent())
        .calculate()
    )

    # Scores only
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_dignities(essential="both", show_details=False)
    )
    report.render(format="rich_table")

    print("\n--- With dignity names shown ---\n")

    # With dignity names
    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_dignities(essential="traditional", show_details=True)
    )
    report.render(format="rich_table")


# =============================================================================
#  Main
# =============================================================================


if __name__ == "__main__":
    print("Dignities & Dispositors Cookbook")
    print("=" * 60)

    # Part 1: Essential Dignities
    example_01_traditional_dignities()
    example_02_modern_dignities()
    example_03_traditional_vs_modern()
    example_04_peregrine()

    # Part 2: Accidental Dignities
    example_05_house_accidental()
    example_06_universal_conditions()
    example_07_combined_scoring()

    # Part 3: Mutual Reception
    example_08_reception_domicile()
    example_09_reception_exaltation()
    example_10_reception_via_component()

    # Part 4: Dispositor Graphs
    example_11_planetary_dispositors()
    example_12_house_dispositors()
    example_13_dispositor_graph()

    # Part 5: Reports
    example_14_dignity_report()

    print("\n" + "=" * 60)
    print("  Cookbook complete!")
    print("=" * 60)
