#!/usr/bin/env python3
"""
Aspects & Orbs Cookbook — Comprehensive Examples

This cookbook demonstrates Stellium's full aspect and orb calculation system,
from simple defaults to advanced traditional techniques.

Contents:
    Part 1: Aspect Engines
        1. Default aspects (major Ptolemaic)
        2. Custom aspect selection via AspectConfig
        3. Harmonic aspects (quintiles, septiles, noviles)
        4. Declination aspects (parallels and contraparallels)
        5. Combining aspect types

    Part 2: Orb Engines
        6. SimpleOrbEngine (aspect-based orbs)
        7. LuminariesOrbEngine (wider orbs for Sun/Moon)
        8. ComplexOrbEngine (cascading priority matrix)
        9. MoietyOrbEngine (traditional moiety system)
        10. Comparing orb engines side by side

    Part 3: Traditional Moiety Deep Dive
        11. Lilly vs Ptolemy moiety systems
        12. Custom moiety values
        13. Minor aspect multiplier
        14. Moiety calculation examples

Run with:
    source ~/.zshrc && pyenv activate starlight && python examples/aspects_and_orbs_cookbook.py
"""

import os
from pathlib import Path

from stellium import ChartBuilder
from stellium.core.config import AspectConfig
from stellium.engines.aspects import (
    HarmonicAspectEngine,
    ModernAspectEngine,
)
from stellium.engines.orbs import (
    LILLY_FULL_ORBS,
    PTOLEMY_FULL_ORBS,
    ComplexOrbEngine,
    LuminariesOrbEngine,
    MoietyOrbEngine,
    SimpleOrbEngine,
)

SCRIPT_DIR = Path(__file__).parent
# Where the cookbook writes. Overridable so that running it — from the test
# suite, or the docs build — does not rewrite the artifacts committed in
# examples/, which are regenerated deliberately and not as a side effect.
OUTPUT_ROOT = Path(os.environ.get("STELLIUM_EXAMPLE_OUTPUT", SCRIPT_DIR))
OUTPUT_DIR = OUTPUT_ROOT / "aspects_and_orbs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_aspects(chart, max_show: int = 10) -> None:
    """Print aspects in a readable format."""
    for asp in chart.aspects[:max_show]:
        applying = "Applying" if asp.is_applying else "Separating"
        print(
            f"  {asp.object1.name:<10} {asp.aspect_name:<14} {asp.object2.name:<10} "
            f"(orb: {asp.orb:.2f}°, {applying})"
        )
    if len(chart.aspects) > max_show:
        print(f"  ... and {len(chart.aspects) - max_show} more")


# =============================================================================
# PART 1: ASPECT ENGINES
# =============================================================================


def example_01_default_aspects():
    """
    Example 1: Default Aspects (Major Ptolemaic)

    The simplest configuration — just call .with_aspects() with no arguments.
    Uses ModernAspectEngine with the 5 major Ptolemaic aspects:
    Conjunction (0°), Sextile (60°), Square (90°), Trine (120°), Opposition (180°).
    """
    section_header("Example 1: Default Aspects")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    print(f"Total aspects found: {len(chart.aspects)}")
    print_aspects(chart)


def example_02_custom_aspect_selection():
    """
    Example 2: Custom Aspect Selection via AspectConfig

    Choose exactly which aspects to look for using AspectConfig.
    Also configure which objects participate in aspects.
    """
    section_header("Example 2: Custom Aspect Selection")

    # Major + minor aspects
    config = AspectConfig(
        aspects=[
            "Conjunction",
            "Sextile",
            "Square",
            "Trine",
            "Opposition",
            "Semisextile",
            "Quincunx",
        ],
    )
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine(config))
        .calculate()
    )
    print(f"Major + Minor aspects: {len(chart.aspects)}")
    print_aspects(chart, max_show=5)

    # Only hard aspects (conjunction, square, opposition)
    hard_config = AspectConfig(aspects=["Conjunction", "Square", "Opposition"])
    hard_chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine(hard_config))
        .calculate()
    )
    print(f"\nHard aspects only: {len(hard_chart.aspects)}")
    print_aspects(hard_chart, max_show=5)

    # Exclude angles and nodes from aspect calculations
    no_angles = AspectConfig(include_angles=False, include_nodes=False)
    planets_only = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine(no_angles))
        .calculate()
    )
    print(f"\nPlanets only (no angles/nodes): {len(planets_only.aspects)}")


def example_03_harmonic_aspects():
    """
    Example 3: Harmonic Aspects

    HarmonicAspectEngine calculates aspects based on harmonic divisions
    of the circle. Each harmonic divides 360° by N.

    Harmonic 5 = Quintile (72°), Biquintile (144°)
    Harmonic 7 = Septile (51.43°), Biseptile (102.86°), Triseptile (154.29°)
    Harmonic 9 = Novile (40°), Binovile (80°), Quadranovile (160°)
    """
    section_header("Example 3: Harmonic Aspects")

    for harmonic in [5, 7, 9]:
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects(HarmonicAspectEngine(harmonic=harmonic))
            .calculate()
        )
        aspect_names = sorted({a.aspect_name for a in chart.aspects})
        print(f"Harmonic {harmonic}: {len(chart.aspects)} aspects found")
        print(f"  Types: {', '.join(aspect_names)}")


def example_04_declination_aspects():
    """
    Example 4: Declination Aspects (Parallels and Contraparallels)

    Declination aspects compare planets' declination (angular distance
    north or south of the celestial equator) rather than ecliptic longitude.

    - Parallel: same declination (both N or S) — like a conjunction
    - Contraparallel: opposite declination — like an opposition
    """
    section_header("Example 4: Declination Aspects")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_declination_aspects(orb=1.0)
        .calculate()
    )

    print(f"Ecliptic aspects: {len(chart.aspects)}")
    print(f"Declination aspects: {len(chart.declination_aspects)}")
    for asp in chart.declination_aspects[:5]:
        print(
            f"  {asp.object1.name:<10} {asp.aspect_name:<16} {asp.object2.name:<10} "
            f"(orb: {asp.orb:.2f}°)"
        )

    # Tighter orb for more precise parallels
    tight_chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_declination_aspects(orb=0.5)
        .calculate()
    )
    print(
        f"\nTighter orb (0.5°): {len(tight_chart.declination_aspects)} declination aspects"
    )


def example_05_combining_aspects():
    """
    Example 5: Combining Aspect Types

    Use ecliptic aspects, harmonic aspects, and declination aspects together
    for a comprehensive picture.
    """
    section_header("Example 5: Combining Aspect Types")

    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_declination_aspects(orb=1.0)
        .calculate()
    )

    print(f"Ecliptic aspects: {len(chart.aspects)}")
    print(f"Declination aspects: {len(chart.declination_aspects)}")
    print(f"Total: {len(chart.aspects) + len(chart.declination_aspects)}")


# =============================================================================
# PART 2: ORB ENGINES
# =============================================================================


def example_06_simple_orb_engine():
    """
    Example 6: SimpleOrbEngine (Default)

    The simplest orb system — one orb value per aspect type,
    regardless of which planets are involved.
    """
    section_header("Example 6: SimpleOrbEngine")

    # Default orbs from the aspect registry
    engine = SimpleOrbEngine()
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_orbs(engine)
        .calculate()
    )
    print(f"Default SimpleOrbEngine: {len(chart.aspects)} aspects")
    print_aspects(chart, max_show=5)

    # Custom orb values
    tight = SimpleOrbEngine(
        orb_map={
            "Conjunction": 6.0,
            "Sextile": 4.0,
            "Square": 6.0,
            "Trine": 6.0,
            "Opposition": 6.0,
        }
    )
    tight_chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_orbs(tight)
        .calculate()
    )
    print(f"\nTight orbs: {len(tight_chart.aspects)} aspects")


def example_07_luminaries_orb_engine():
    """
    Example 7: LuminariesOrbEngine

    Gives wider orbs to aspects involving the Sun or Moon,
    which is a very common modern practice.
    """
    section_header("Example 7: LuminariesOrbEngine")

    engine = LuminariesOrbEngine()
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_orbs(engine)
        .calculate()
    )

    # Show the difference for luminary vs non-luminary aspects
    luminary_aspects = [
        a
        for a in chart.aspects
        if a.object1.name in ("Sun", "Moon") or a.object2.name in ("Sun", "Moon")
    ]
    other_aspects = [
        a
        for a in chart.aspects
        if a.object1.name not in ("Sun", "Moon")
        and a.object2.name not in ("Sun", "Moon")
    ]

    print(f"Luminary aspects: {len(luminary_aspects)} (wider orbs)")
    print(f"Other aspects: {len(other_aspects)} (standard orbs)")
    print(f"Total: {len(chart.aspects)}")


def example_08_complex_orb_engine():
    """
    Example 8: ComplexOrbEngine

    The most configurable orb engine — set orbs by specific planet pair,
    by individual planet, by aspect type, with cascading priority.
    """
    section_header("Example 8: ComplexOrbEngine")

    config = {
        "by_pair": {
            "Sun-Moon": {"Conjunction": 12.0, "Opposition": 12.0, "default": 10.0},
            "Mars-Saturn": {"Square": 5.0, "default": 4.0},
        },
        "by_planet": {
            "Sun": {"default": 8.0},
            "Moon": {"default": 8.0},
            "Saturn": {"default": 5.0},
        },
        "by_aspect": {
            "Conjunction": 8.0,
            "Square": 7.0,
            "Trine": 7.0,
            "Opposition": 8.0,
            "Sextile": 5.0,
        },
        "default": 3.0,
    }

    engine = ComplexOrbEngine(config)
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_orbs(engine)
        .calculate()
    )
    print(f"ComplexOrbEngine: {len(chart.aspects)} aspects")
    print_aspects(chart, max_show=5)


def example_09_moiety_orb_engine():
    """
    Example 9: MoietyOrbEngine (Traditional)

    The traditional moiety system where each planet has its own orb value.
    Effective orb = average of both planets' full orbs.

    This is the system used by Lilly, Bonatti, Al-Biruni, and the
    entire medieval astrological tradition.
    """
    section_header("Example 9: MoietyOrbEngine (Traditional)")

    # Default: Lilly / medieval consensus
    engine = MoietyOrbEngine()
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects()
        .with_orbs(engine)
        .calculate()
    )
    print(f"Lilly moieties: {len(chart.aspects)} aspects")
    print_aspects(chart, max_show=5)

    # Show some moiety calculations
    print("\nMoiety calculations (Lilly):")
    pairs = [
        ("Sun", "Moon"),
        ("Sun", "Saturn"),
        ("Mars", "Venus"),
        ("Mercury", "Jupiter"),
    ]
    for a, b in pairs:
        orb_a = LILLY_FULL_ORBS[a]
        orb_b = LILLY_FULL_ORBS[b]
        effective = (orb_a + orb_b) / 2
        print(f"  {a} ({orb_a}°) + {b} ({orb_b}°) → effective orb: {effective}°")


def example_10_comparing_orb_engines():
    """
    Example 10: Comparing Orb Engines Side by Side

    Same chart, different orb engines — see how the choice
    of orb system affects which aspects are found.
    """
    section_header("Example 10: Comparing Orb Engines")

    builder = ChartBuilder.from_notable("Albert Einstein").with_aspects()

    engines = {
        "Simple (default)": SimpleOrbEngine(),
        "Luminaries": LuminariesOrbEngine(),
        "Moiety (Lilly)": MoietyOrbEngine(),
        "Moiety (Ptolemy)": MoietyOrbEngine(system="ptolemy"),
    }

    for name, engine in engines.items():
        chart = builder.with_orbs(engine).calculate()
        print(f"  {name:<22} → {len(chart.aspects)} aspects")


# =============================================================================
# PART 3: TRADITIONAL MOIETY DEEP DIVE
# =============================================================================


def example_11_lilly_vs_ptolemy():
    """
    Example 11: Lilly vs Ptolemy Moiety Systems

    The medieval consensus (Lilly et al.) and Ptolemy differ significantly
    on several planets — especially Jupiter (9° vs 12°) and the Sun (15° vs 17°).
    """
    section_header("Example 11: Lilly vs Ptolemy Systems")

    print("Full orb comparison:")
    print(f"  {'Planet':<10} {'Lilly':>8} {'Ptolemy':>8} {'Diff':>8}")
    print(f"  {'-' * 36}")
    for planet in ["Sun", "Moon", "Saturn", "Jupiter", "Mars", "Venus", "Mercury"]:
        lilly = LILLY_FULL_ORBS[planet]
        ptolemy = PTOLEMY_FULL_ORBS[planet]
        diff = ptolemy - lilly
        marker = " ←" if abs(diff) > 1 else ""
        print(f"  {planet:<10} {lilly:>7.1f}° {ptolemy:>7.1f}° {diff:>+7.1f}°{marker}")

    # Show practical difference
    builder = ChartBuilder.from_notable("Albert Einstein").with_aspects()
    lilly_chart = builder.with_orbs(MoietyOrbEngine(system="lilly")).calculate()
    ptolemy_chart = builder.with_orbs(MoietyOrbEngine(system="ptolemy")).calculate()

    print("\nEinstein's chart:")
    print(f"  Lilly moieties:  {len(lilly_chart.aspects)} aspects")
    print(f"  Ptolemy moieties: {len(ptolemy_chart.aspects)} aspects")


def example_12_custom_moieties():
    """
    Example 12: Custom Moiety Values

    Override specific planet orbs while keeping system defaults for the rest.
    Useful for experimenting or following a specific author's values.
    """
    section_header("Example 12: Custom Moiety Values")

    # Start with Lilly but give outer planets wider orbs
    wide_outers = MoietyOrbEngine(
        orb_map={
            "Uranus": 9.0,  # Treat like Saturn
            "Neptune": 9.0,  # Treat like Jupiter
            "Pluto": 8.0,  # Treat like Mars
        }
    )

    builder = ChartBuilder.from_notable("Albert Einstein").with_aspects()
    default_chart = builder.with_orbs(MoietyOrbEngine()).calculate()
    wide_chart = builder.with_orbs(wide_outers).calculate()

    print(f"Default outer planet orbs: {len(default_chart.aspects)} aspects")
    print(f"Wider outer planet orbs:   {len(wide_chart.aspects)} aspects")


def example_13_minor_aspect_multiplier():
    """
    Example 13: Minor Aspect Multiplier

    Traditional moieties applied to all aspects equally. But modern practice
    often tightens orbs for minor aspects. The multiplier parameter scales
    down the moiety-calculated orb for Minor and Harmonic aspects.
    """
    section_header("Example 13: Minor Aspect Multiplier")

    # Full moiety orbs for all aspects
    config = AspectConfig(
        aspects=[
            "Conjunction",
            "Sextile",
            "Square",
            "Trine",
            "Opposition",
            "Semisextile",
            "Quincunx",
        ],
    )

    full_moiety = MoietyOrbEngine()
    reduced_minor = MoietyOrbEngine(minor_aspect_multiplier=0.4)

    builder = ChartBuilder.from_notable("Albert Einstein").with_aspects(
        ModernAspectEngine(config)
    )

    full_chart = builder.with_orbs(full_moiety).calculate()
    reduced_chart = builder.with_orbs(reduced_minor).calculate()

    print(f"Full moiety for all aspects:    {len(full_chart.aspects)} aspects")
    print(f"40% moiety for minor aspects:   {len(reduced_chart.aspects)} aspects")

    # Show the difference
    print(f"\nSun-Moon moiety: {(15 + 12) / 2:.1f}°")
    print(f"  Major aspect orb: {(15 + 12) / 2:.1f}°")
    print(f"  Minor aspect orb (×0.4): {(15 + 12) / 2 * 0.4:.1f}°")


def example_14_moiety_calculation_table():
    """
    Example 14: Complete Moiety Calculation Table

    Show the effective orb for every planet pair under the Lilly system.
    """
    section_header("Example 14: Moiety Calculation Table")

    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    # Header
    print(f"  {'':>8}", end="")
    for p in planets:
        print(f" {p[:3]:>5}", end="")
    print()
    print(f"  {'':>8} {'─' * 35}")

    # Rows
    for p1 in planets:
        print(f"  {p1:>8}", end="")
        for p2 in planets:
            effective = (LILLY_FULL_ORBS[p1] + LILLY_FULL_ORBS[p2]) / 2
            print(f" {effective:>5.1f}", end="")
        print()


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("\n" + "=" * 60)
    print("  STELLIUM ASPECTS & ORBS COOKBOOK")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}\n")

    # Part 1: Aspect Engines
    example_01_default_aspects()
    example_02_custom_aspect_selection()
    example_03_harmonic_aspects()
    example_04_declination_aspects()
    example_05_combining_aspects()

    # Part 2: Orb Engines
    example_06_simple_orb_engine()
    example_07_luminaries_orb_engine()
    example_08_complex_orb_engine()
    example_09_moiety_orb_engine()
    example_10_comparing_orb_engines()

    # Part 3: Traditional Moiety Deep Dive
    example_11_lilly_vs_ptolemy()
    example_12_custom_moieties()
    example_13_minor_aspect_multiplier()
    example_14_moiety_calculation_table()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
