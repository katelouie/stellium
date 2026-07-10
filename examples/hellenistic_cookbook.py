#!/usr/bin/env python3
"""
Hellenistic Cookbook - Planetary Years, Almuten, Hyleg, Length of Life, Firdaria

A tour of the traditional (Hellenistic / Perso-Arabic) apparatus in Stellium:
the shared planetary-year tables and the techniques built on them — the almuten
of a degree, the hyleg, the length-of-life years table, and the Firdaria
time-lords.

Note: length of life is a *computed traditional indicator*, not a prediction of
actual lifespan.

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/hellenistic_cookbook.py

For full documentation, see docs/development/specs/HELLENISTIC_PERIODS_SPEC.md
and docs/development/specs/LENGTH_OF_LIFE_SPEC.md.
"""

from datetime import datetime

from stellium import ChartBuilder
from stellium.core import planetary_years as py
from stellium.engines import almuten_of_degree
from stellium.engines.dignities import DIGNITIES

_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


# =============================================================================
# PART 1: PLANETARY YEARS (the shared foundation)
# =============================================================================


def example_1_least_years():
    """
    Example 1: The Least (Minor) Years

    The canonical planetary periods that Zodiacal Releasing and Decennials use.
    They sum to 129 (the Decennials total).
    """
    section_header("Example 1: Least (Minor) Years")

    for planet in _PLANETS:
        print(f"  {planet:8} {py.least_years(planet):>3}")
    print(f"  {'-' * 13}")
    print(f"  {'Sum':8} {sum(py.LEAST_YEARS.values()):>3}  (the Decennials total)")


def example_2_all_four_families():
    """
    Example 2: Least, Mean, and Greater Years Side by Side

    Different techniques draw on different families. Mean is derived as
    (least + greater) / 2 — note the half-integer luminaries.
    """
    section_header("Example 2: Least / Mean / Greater Years")

    print(f"  {'Planet':8} {'least':>6} {'mean':>6} {'greater':>8}")
    print(f"  {'-' * 30}")
    for planet in _PLANETS:
        print(
            f"  {planet:8} {py.least_years(planet):>6} "
            f"{py.mean_years(planet):>6} {py.greater_years(planet):>8}"
        )
    print("\n  Length of life uses greater/mean/least by the alcocoden's angularity.")


def example_3_greatest_years_are_contested():
    """
    Example 3: The Greatest Years Genuinely Disagree

    Unlike the other families, the greatest years vary between authorities —
    Stellium stores attributed variants rather than a single "right" number.
    """
    section_header("Example 3: Greatest Years (contested)")

    de_vore = py.GREATEST_YEARS_VARIANTS["de_vore"]
    astro = py.GREATEST_YEARS_VARIANTS["astronomical"]
    print(f"  {'Planet':8} {'De Vore':>8} {'Astronomical':>13}")
    print(f"  {'-' * 30}")
    for planet in _PLANETS:
        print(f"  {planet:8} {de_vore[planet]:>8} {astro[planet]:>13}")

    print("\n  The Moon is the flashpoint — four attested values:")
    for source, value in py.MOON_GREATEST_VARIANTS.items():
        print(f"    {source:22} {value}")


def example_4_firdaria_periods_are_not_least_years():
    """
    Example 4: Firdaria Periods Are a SEPARATE Set

    A classic conflation: the Firdaria periods are NOT the least years.
    """
    section_header("Example 4: Firdaria Periods (not the least years)")

    print(f"  {'Planet':12} {'firdaria':>9} {'least':>6}")
    print(f"  {'-' * 29}")
    for planet in _PLANETS:
        print(
            f"  {planet:12} {py.firdaria_years(planet):>9} {py.least_years(planet):>6}"
        )
    for node in ("North Node", "South Node"):
        print(f"  {node:12} {py.firdaria_years(node):>9} {'-':>6}")
    print(f"\n  Firdaria total (with nodes): {sum(py.FIRDARIA_YEARS.values())} years")


def example_5_greater_years_come_from_the_terms():
    """
    Example 5: Greater Years = Sum of a Planet's Egyptian Terms

    The five non-luminary greater years are the total degrees each planet rules
    by bound/term across the zodiac (they sum to 360). Stellium verifies this
    against its dignity tables.
    """
    section_header("Example 5: Greater Years from the Terms")

    totals = dict.fromkeys(_PLANETS, 0)
    for sign_data in DIGNITIES.values():
        bounds = sign_data["bound_egypt"]
        starts = sorted(bounds)
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else 30
            totals[bounds[start]] += end - start

    print(f"  {'Planet':8} {'term sum':>9} {'greater':>8}")
    print(f"  {'-' * 27}")
    for planet in ["Saturn", "Jupiter", "Mars", "Venus", "Mercury"]:
        print(f"  {planet:8} {totals[planet]:>9} {py.greater_years(planet):>8}")
    non_lum = ["Saturn", "Jupiter", "Mars", "Venus", "Mercury"]
    print(f"  {'-' * 27}")
    print(f"  {'Total':8} {sum(totals[p] for p in non_lum):>9}  (= 360)")


# =============================================================================
# PART 2: ALMUTEN OF A DEGREE
# =============================================================================


def example_6_almuten_of_a_degree():
    """
    Example 6: The Almuten (Essential-Dignity Victor) of a Degree

    Scores each planet's essential dignity at a longitude (domicile 5,
    exaltation 4, triplicity 3, term 2, face 1) and returns the winner.
    """
    section_header("Example 6: Almuten of a Degree")

    result = almuten_of_degree(15.0, "day")  # 15 deg Aries, day chart
    print("  Almuten of 15 deg Aries (day):", result.winner)
    print("\n  Per-planet scores:")
    for planet in _PLANETS:
        if result.scores[planet]:
            held = ", ".join(result.dignities[planet])
            print(f"    {planet:8} {result.scores[planet]:>2}  ({held})")


def example_7_almuten_is_sect_sensitive():
    """
    Example 7: Triplicity Makes the Almuten Sect-Sensitive

    The same degree can have a different victor by day and by night, because
    the triplicity ruler changes with sect.
    """
    section_header("Example 7: Almuten Sect Sensitivity")

    for sect in ("day", "night"):
        r = almuten_of_degree(15.0, sect)
        tie = f"  (tie: {', '.join(r.tie)})" if r.tie else ""
        print(f"  15 deg Aries, {sect:5}: {r.winner}{tie}")


# =============================================================================
# PART 3: HYLEG (the giver of life)
# =============================================================================


def example_8_find_the_hyleg():
    """
    Example 8: Finding the Hyleg

    The prorogator is the first sect-ordered candidate found in a hylegiacal
    place (houses 1, 7, 9, 10, 11). The result carries a candidacy trace.
    """
    section_header("Example 8: Finding the Hyleg")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    hyleg = chart.hyleg()
    print(f"  Hyleg: {hyleg.point} at {hyleg.longitude:.2f} deg (house {hyleg.place})")
    print("\n  Candidacy trace (candidate -> in a hylegiacal place?):")
    for candidate, qualified in hyleg.candidates_tried:
        mark = "yes" if qualified else "no"
        print(f"    {candidate:10} {mark}")


def example_9_hyleg_is_sect_ordered():
    """
    Example 9: Hyleg Candidate Order Follows Sect

    By day the Sun is examined first; by night the Moon.
    """
    section_header("Example 9: Hyleg Sect Ordering")

    day = ChartBuilder.from_details("1990-06-15 12:00", (40.7128, -74.0060)).calculate()
    night = ChartBuilder.from_details(
        "1990-06-15 00:30", (40.7128, -74.0060)
    ).calculate()
    for label, chart in (("Day", day), ("Night", night)):
        h = chart.hyleg()
        first = h.candidates_tried[0][0]
        print(
            f"  {label:5} chart ({chart.sect}): first candidate {first}, hyleg {h.point}"
        )


# =============================================================================
# PART 4: LENGTH OF LIFE (hyleg -> alcocoden -> years)
# =============================================================================


def example_10_length_of_life():
    """
    Example 10: The Length-of-Life Years Table (Lilly)

    A transparent, itemized indicator: hyleg -> alcocoden -> base years by
    angularity -> modifiers. NOT a prediction of actual lifespan.
    """
    section_header("Example 10: Length of Life")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    r = chart.length_of_life()
    print(f"  Hyleg:      {r.hyleg.point}")
    print(f"  Alcocoden:  {r.alcocoden} ({r.alcocoden_angularity})")
    print(f"  Base years: {r.base_years} ({r.base_family})")
    if r.modifiers:
        print("  Modifiers:")
        for m in r.modifiers:
            print(f"    {m.delta:+g}  {m.source}: {m.reason}")
    print(f"  TOTAL:      {r.total:g} {r.unit}")
    print("\n  (A computed traditional indicator — read as significator, not fact.)")


def example_11_the_result_is_fully_itemized():
    """
    Example 11: The Result Explains Itself

    base_years + every modifier delta always sums to total, so the reasoning
    can be audited.
    """
    section_header("Example 11: Auditing the Result")

    r = ChartBuilder.from_notable("Steve Jobs").calculate().length_of_life()
    itemized = r.base_years + sum(m.delta for m in r.modifiers)
    print(
        f"  base_years ({r.base_years:g}) + modifiers "
        f"({sum(m.delta for m in r.modifiers):+g}) = {itemized:g}"
    )
    print(f"  total = {r.total:g} {r.unit}")
    print(f"  invariant holds: {abs(itemized - r.total) < 1e-9}")


def example_12_combust_alcocoden_gives_months():
    """
    Example 12: A Combust Alcocoden Counts in Months

    When the alcocoden is combust (within ~8.5 deg of the Sun), the tradition
    reads the count as months, not years — a short-life signification.
    """
    section_header("Example 12: Combust Alcocoden")

    r = ChartBuilder.from_notable("Marilyn Monroe").calculate().length_of_life()
    print(f"  Alcocoden: {r.alcocoden} ({r.alcocoden_angularity})")
    print(f"  Total: {r.total:g} {r.unit}")
    for note in r.notes:
        print(f"  Note: {note}")


# =============================================================================
# PART 5: FIRDARIA (Persian time-lords)
# =============================================================================


def example_13_firdaria_basics():
    """
    Example 13: The Firdaria Sequence

    Sect-ordered major periods (day: Sun-first, night: Moon-first). The default
    is the Abu Ma'shar preset (nodes at the end in both sects).
    """
    section_header("Example 13: Firdaria Basics")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    timeline = chart.firdaria()
    print(f"  Sect: {timeline.sect}  |  Preset: {timeline.preset}")
    print("\n  First cycle of major periods (lord -> ages):")
    for major in timeline.majors():
        if major.start_age >= 75:
            break
        print(f"    {major.ruler:12} {major.start_age:>5.1f} - {major.end_age:<5.1f}")


def example_14_firdaria_subperiods():
    """
    Example 14: Sub-Periods ("second firdaria")

    Each planetary major divides into seven equal sub-periods in Chaldean order
    from the major ruler. Node majors do not subdivide.
    """
    section_header("Example 14: Firdaria Sub-Periods")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    timeline = chart.firdaria()
    first = timeline.majors()[0]
    print(f"  Sub-periods of the opening {first.ruler} major:")
    for sub in timeline.subperiods():
        if sub.ruler != first.ruler or sub.start_age >= first.end_age:
            continue
        print(
            f"    {first.ruler} / {sub.sub_ruler:8} "
            f"{sub.start_age:>5.2f} - {sub.end_age:<5.2f}"
        )


def example_15_firdaria_at_a_date():
    """
    Example 15: Who Rules a Given Moment

    at() returns the major-and-sub period in effect at a datetime.
    """
    section_header("Example 15: Firdaria at a Date")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    timeline = chart.firdaria()
    when = datetime(1920, 1, 1)
    period = timeline.at(when)
    if period:
        print(
            f"  On {when:%B %d, %Y}: lord {period.ruler}, "
            f"partner {period.sub_ruler} (ages "
            f"{period.start_age:.1f}-{period.end_age:.1f})"
        )


def example_16_firdaria_node_presets():
    """
    Example 16: The Nocturnal-Node Fork (Presets)

    The one real scholarly disagreement: where the nodes fall in a night chart.
    Abu Ma'shar puts them at the end; Bonatti puts them after Mars.
    """
    section_header("Example 16: Firdaria Node Presets (night chart)")

    night = ChartBuilder.from_details(
        "1990-06-15 00:30", (40.7128, -74.0060)
    ).calculate()
    for preset in ("abu_mashar", "bonatti"):
        order = [
            m.ruler for m in night.firdaria(preset=preset).majors() if m.start_age < 75
        ]
        print(f"  {preset:12}: {' -> '.join(order)}")


def main():
    """Run all Hellenistic examples."""
    print("\n" + "=" * 70)
    print("  STELLIUM HELLENISTIC COOKBOOK")
    print("  Planetary Years, Almuten, Hyleg, Length of Life, Firdaria")
    print("=" * 70)

    # Part 1: Planetary Years (the foundation)
    example_1_least_years()
    example_2_all_four_families()
    example_3_greatest_years_are_contested()
    example_4_firdaria_periods_are_not_least_years()
    example_5_greater_years_come_from_the_terms()

    # Part 2: Almuten of a Degree
    example_6_almuten_of_a_degree()
    example_7_almuten_is_sect_sensitive()

    # Part 3: Hyleg
    example_8_find_the_hyleg()
    example_9_hyleg_is_sect_ordered()

    # Part 4: Length of Life
    example_10_length_of_life()
    example_11_the_result_is_fully_itemized()
    example_12_combust_alcocoden_gives_months()

    # Part 5: Firdaria
    example_13_firdaria_basics()
    example_14_firdaria_subperiods()
    example_15_firdaria_at_a_date()
    example_16_firdaria_node_presets()

    print("\n" + "=" * 70)
    print("  COOKBOOK COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
