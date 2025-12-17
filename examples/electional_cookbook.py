#!/usr/bin/env python3
"""
Electional Astrology Cookbook
=============================

This cookbook demonstrates Stellium's electional search engine for finding
auspicious times that match specific astrological criteria.

Electional astrology is the art of choosing optimal times for important
undertakings - starting a business, getting married, launching a project,
or creating talismans. The goal is to find moments when planetary positions
support the intended activity.

**Output directory:** `examples/elections/`

Run this cookbook:
    source ~/.zshrc && pyenv activate starlight
    python examples/electional_cookbook.py

Contents:
---------
Part 1: Basic Searches
    1. Simplest search (lambda conditions)
    2. Using helper predicates
    3. Finding time windows vs moments
    4. Search with progress callback

Part 2: Moon Conditions
    5. Moon phase requirements
    6. Void of course Moon
    7. Moon sign restrictions
    8. Moon aspects (applying/separating)

Part 3: Planetary Conditions
    9. Retrograde avoidance
    10. Dignity requirements
    11. Combust planets
    12. Out of bounds planets

Part 4: Aspect Conditions
    13. Requiring specific aspects
    14. Avoiding hard aspects
    15. Malefic avoidance (Mars/Saturn)
    16. Complex aspect combinations

Part 5: House & Angle Conditions
    17. Angular planets
    18. Avoiding difficult houses
    19. Benefics in good houses

Part 6: Composition & Complex Queries
    20. AND logic (all_of)
    21. OR logic (any_of)
    22. NOT logic (not_)
    23. Nested boolean expressions
    24. The Reddit "Regulus Talisman" query

Part 7: Practical Elections
    25. General good times
    26. Business launch election
    27. Relationship/marriage election
    28. Mercury matters (contracts, communication)
    29. Mars matters (competition, surgery)
    30. Jupiter matters (expansion, luck)

Part 8: Aspect Exactitude
    31. Finding moments near exact aspects
    32. Tight orb elections

Part 9: Fixed Stars & Angles
    33. Fixed star on angle (Regulus rising)
    34. Specific degrees on angles
    35. The complete Regulus talisman query

Part 10: Planetary Hours
    36. Finding planetary hours
    37. Jupiter hour elections
    38. Combining planetary hours with other conditions

Part 11: Advanced Usage
    39. Generator-based iteration (memory efficient)
    40. Counting matches without storing
    41. Custom lambda conditions
    42. Integration with ChartQuery
    43. Exporting results
"""

from pathlib import Path

# Stellium imports
from stellium.core.models import ChartLocation
from stellium.electional import (
    CHALDEAN_ORDER,
    DAY_RULERS,
    # Main search class
    ElectionalSearch,
    all_of,
    # Angles and fixed stars
    angle_at_degree,
    any_of,
    # Aspect predicates
    aspect_applying,
    # Aspect exactitude
    aspect_exact_within,
    get_planetary_hour,
    get_planetary_hours_for_day,
    has_aspect,
    # House predicates
    in_house,
    # Planetary hours
    in_planetary_hour,
    # Dignity predicates
    is_dignified,
    # Out of bounds predicates
    is_out_of_bounds,
    is_waning,
    # Moon phase predicates
    is_waxing,
    moon_phase,
    no_aspect,
    no_hard_aspect,
    no_malefic_aspect,
    not_,
    # Combust predicates
    not_combust,
    not_debilitated,
    not_in_house,
    not_out_of_bounds,
    # Retrograde predicates
    not_retrograde,
    # VOC predicates
    not_voc,
    on_angle,
    # Sign predicates
    sign_in,
    sign_not_in,
    star_on_angle,
)

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "elections"
OUTPUT_DIR.mkdir(exist_ok=True)

# Default location for examples (San Francisco)
DEFAULT_LOCATION = ChartLocation(
    latitude=37.7749,
    longitude=-122.4194,
    timezone="America/Los_Angeles",
)

# Shorter date range for faster examples
SHORT_RANGE = ("2025-01-01", "2025-01-15")
MONTH_RANGE = ("2025-01-01", "2025-01-31")
QUARTER_RANGE = ("2025-01-01", "2025-03-31")


def print_header(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def print_results(results, max_show: int = 5, detailed: bool = True) -> None:
    """Print search results nicely."""
    print(f"Found {len(results)} results")
    if not results:
        print("  (No matches found)")
        return

    for i, moment in enumerate(results[:max_show], 1):
        chart = moment.chart
        moon = chart.get_object("Moon")

        print(f"\n{i}. {moment.datetime.strftime('%a %b %d, %Y at %I:%M %p')}")

        if detailed and moon:
            phase_info = f"{moon.phase.phase_name}" if moon.phase else "unknown"
            print(f"   Moon: {moon.sign} ({phase_info})")

            # Show Moon's applying aspects
            applying = []
            for asp in chart.aspects:
                if asp.object1.name == "Moon" or asp.object2.name == "Moon":
                    other = (
                        asp.object2.name
                        if asp.object1.name == "Moon"
                        else asp.object1.name
                    )
                    if asp.is_applying:
                        applying.append(f"{asp.aspect_name} {other}")
            if applying:
                print(f"   Applying: {', '.join(applying[:3])}")

    if len(results) > max_show:
        print(f"\n   ... and {len(results) - max_show} more")


def print_windows(windows, max_show: int = 5) -> None:
    """Print window results nicely."""
    print(f"Found {len(windows)} windows")
    if not windows:
        print("  (No windows found)")
        return

    for i, window in enumerate(windows[:max_show], 1):
        print(f"\n{i}. {window}")
        moon = window.chart.get_object("Moon")
        if moon:
            print(f"   Moon at start: {moon.sign}")

    if len(windows) > max_show:
        print(f"\n   ... and {len(windows) - max_show} more")


# =============================================================================
# PART 1: BASIC SEARCHES
# =============================================================================


def example_1_simplest_search():
    """
    Example 1: Simplest Search with Lambda Conditions
    -------------------------------------------------
    The most basic way to use ElectionalSearch is with lambda functions.
    Each lambda takes a CalculatedChart and returns True/False.

    This approach requires no additional imports beyond ElectionalSearch
    and gives you full access to the chart object.
    """
    print_header("Example 1: Simplest Search (Lambda Conditions)")

    print("Query: Find times when Moon is waxing")
    print("Method: Using a lambda function")
    print()

    search = ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)

    # Lambda directly accesses chart attributes
    results = search.where(lambda c: c.get_object("Moon").phase.is_waxing).find_moments(
        max_results=5, step="day"
    )

    print_results(results)


def example_2_helper_predicates():
    """
    Example 2: Using Helper Predicates
    ----------------------------------
    Helper predicates are factory functions that return conditions.
    They're more readable than lambdas and handle edge cases properly.

    Compare:
        lambda c: c.get_object("Moon").phase.is_waxing
    vs:
        is_waxing()

    Both do the same thing, but the predicate is cleaner.
    """
    print_header("Example 2: Using Helper Predicates")

    print("Query: Moon waxing AND not void of course")
    print("Method: Using is_waxing() and not_voc() predicates")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=5, step="day")
    )

    print_results(results)


def example_3_time_windows():
    """
    Example 3: Finding Time Windows vs Moments
    ------------------------------------------
    find_moments() returns individual time points.
    find_windows() coalesces adjacent passing moments into windows.

    Windows are useful for seeing "good periods" - e.g., "Tuesday 2pm-6pm"
    rather than "Tuesday 2pm, 3pm, 4pm, 5pm, 6pm".
    """
    print_header("Example 3: Time Windows vs Moments")

    search = ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION).where(is_waxing())

    print("MOMENTS (individual time points):")
    moments = search.find_moments(max_results=3, step="4hour")
    for m in moments:
        print(f"  {m.datetime.strftime('%a %b %d at %I:%M %p')}")

    print("\nWINDOWS (coalesced periods):")
    windows = search.find_windows(step="4hour")
    print_windows(windows, max_show=3)


def example_4_progress_callback():
    """
    Example 4: Search with Progress Callback
    ----------------------------------------
    Long searches can take a while. Use with_progress() to track progress.
    The callback receives (current_step, total_steps).
    """
    print_header("Example 4: Progress Callback")

    print("Searching with progress reporting...")
    print()

    steps_shown = [0]

    def show_progress(current: int, total: int) -> None:
        pct = (current / total) * 100 if total > 0 else 0
        if pct >= steps_shown[0] + 25:  # Show every 25%
            print(f"  Progress: {pct:.0f}%")
            steps_shown[0] = pct

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .with_progress(show_progress)
        .find_moments(max_results=3, step="hour")
    )

    print()
    print_results(results, detailed=False)


# =============================================================================
# PART 2: MOON CONDITIONS
# =============================================================================


def example_5_moon_phase():
    """
    Example 5: Moon Phase Requirements
    ----------------------------------
    The Moon's phase is crucial in electional astrology:
    - Waxing (New to Full): Good for beginnings, growth, increase
    - Waning (Full to New): Good for endings, decrease, banishing
    - Specific phases: New Moon, Full Moon, quarters, etc.
    """
    print_header("Example 5: Moon Phase Requirements")

    print("A) Finding waxing Moon times:")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .find_moments(max_results=3, step="day")
    )
    print_results(results, max_show=3)

    print("\n" + "-" * 50)
    print("\nB) Finding waning Moon times:")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waning())
        .find_moments(max_results=3, step="day")
    )
    print_results(results, max_show=3)

    print("\n" + "-" * 50)
    print("\nC) Finding specific phases (First Quarter or Full Moon):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(moon_phase(["First Quarter", "Full Moon"]))
        .find_moments(max_results=3, step="4hour")
    )
    print_results(results, max_show=3)


def example_6_void_of_course():
    """
    Example 6: Void of Course Moon
    ------------------------------
    A void-of-course Moon has made its last major aspect before
    changing signs. Traditional electional astrology avoids VOC periods
    for important undertakings - things "come to nothing."

    not_voc() is one of the most important electional filters.
    """
    print_header("Example 6: Void of Course Moon")

    print("Query: Find times when Moon is NOT void of course")
    print()

    # Not VOC with traditional aspects (Sun through Saturn)
    print("A) Using traditional aspects (Sun-Saturn):")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_voc(mode="traditional"))
        .find_moments(max_results=3, step="4hour")
    )
    print_results(results, max_show=3)

    print("\n" + "-" * 50)

    # Not VOC with modern aspects (includes Uranus, Neptune, Pluto)
    print("\nB) Using modern aspects (includes outers):")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_voc(mode="modern"))
        .find_moments(max_results=3, step="4hour")
    )
    print_results(results, max_show=3)


def example_7_moon_sign():
    """
    Example 7: Moon Sign Restrictions
    ---------------------------------
    Some Moon signs are better for certain activities:
    - Moon in Scorpio: "Fall" - Moon is weakened
    - Moon in Capricorn: "Detriment" - Moon is uncomfortable
    - Moon in Taurus: "Exaltation" - Moon is strengthened
    - Moon in Cancer: "Domicile" - Moon rules this sign

    For general elections, avoid Scorpio and Capricorn.
    """
    print_header("Example 7: Moon Sign Restrictions")

    print("A) Avoid Moon in debility (Scorpio or Capricorn):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Require Moon in dignity (Cancer or Taurus):")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(sign_in("Moon", ["Cancer", "Taurus"]))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


def example_8_moon_aspects():
    """
    Example 8: Moon Aspects (Applying/Separating)
    ---------------------------------------------
    The Moon's applying aspects show what's "coming" - very important
    in electional work. Separating aspects show what's "past."

    - Applying trine/sextile to Jupiter or Venus: Excellent
    - Applying square/opposition to Mars or Saturn: Avoid
    """
    print_header("Example 8: Moon Aspects")

    print("A) Moon applying trine or sextile to Jupiter:")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(aspect_applying("Moon", "Jupiter", ["trine", "sextile"]))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Moon applying to Venus (any harmonious aspect):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(aspect_applying("Moon", "Venus", ["conjunction", "trine", "sextile"]))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


# =============================================================================
# PART 3: PLANETARY CONDITIONS
# =============================================================================


def example_9_retrograde():
    """
    Example 9: Retrograde Avoidance
    -------------------------------
    Retrograde planets appear to move backward. Traditional electional
    avoids starting things when key planets are retrograde:
    - Mercury Rx: Communication, contracts, travel issues
    - Venus Rx: Relationship, beauty, value issues
    - Mars Rx: Action, competition, energy issues
    """
    print_header("Example 9: Retrograde Avoidance")

    print("Query: Mercury NOT retrograde")
    print("(Important for contracts, communication, travel)")
    print()

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(not_retrograde("Mercury"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nQuery: Both Mercury AND Venus NOT retrograde")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(not_retrograde("Mercury"))
        .where(not_retrograde("Venus"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


def example_10_dignity():
    """
    Example 10: Dignity Requirements
    --------------------------------
    Planets in dignity are strengthened:
    - Domicile/Ruler: Planet in the sign it rules
    - Exaltation: Planet in sign where it's exalted

    For elections involving a planet, having it dignified helps.
    """
    print_header("Example 10: Dignity Requirements")

    print("A) Venus dignified (in Taurus, Libra, or Pisces):")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(is_dignified("Venus", ["ruler", "exaltation"]))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Mars NOT debilitated (not in Cancer or Libra):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(not_debilitated("Mars"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


def example_11_combust():
    """
    Example 11: Combust Planets
    ---------------------------
    A planet within ~8.5° of the Sun is "combust" - hidden by the Sun's
    light and weakened. Avoid elections where key planets are combust.

    Exception: Cazimi (within 17') is extremely powerful, not weak.
    """
    print_header("Example 11: Combust Planets")

    print("Query: Moon NOT combust (more than 8.5° from Sun)")
    print("(Combust Moon = hidden, weakened lunar energy)")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_combust("Moon"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    # Show Sun-Moon distance
    if results:
        print("\nSun-Moon distances:")
        for m in results[:3]:
            moon = m.chart.get_object("Moon")
            sun = m.chart.get_object("Sun")
            diff = abs(moon.longitude - sun.longitude)
            if diff > 180:
                diff = 360 - diff
            print(f"  {m.datetime.strftime('%b %d')}: {diff:.1f}°")


def example_12_out_of_bounds():
    """
    Example 12: Out of Bounds Planets
    ---------------------------------
    Planets beyond the Sun's maximum declination (~23.4°) are "out of bounds."
    OOB planets operate outside normal rules - can be genius or erratic.

    Some electional traditions avoid OOB Moon; others seek it for
    unconventional undertakings.
    """
    print_header("Example 12: Out of Bounds Planets")

    print("A) Moon NOT out of bounds (conventional energy):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(not_out_of_bounds("Moon"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Finding OUT OF BOUNDS Moon (unconventional energy):")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(is_out_of_bounds("Moon"))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


# =============================================================================
# PART 4: ASPECT CONDITIONS
# =============================================================================


def example_13_requiring_aspects():
    """
    Example 13: Requiring Specific Aspects
    --------------------------------------
    You can require that two planets be in a specific aspect.
    Applying aspects are usually more important than separating.
    """
    print_header("Example 13: Requiring Specific Aspects")

    print("A) Sun trine Jupiter (applying) - excellent for expansion:")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(aspect_applying("Sun", "Jupiter", ["trine"]))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Venus conjunct or sextile Mars - passion/attraction:")
    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(has_aspect("Venus", "Mars", ["conjunction", "sextile"]))
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


def example_14_avoiding_hard_aspects():
    """
    Example 14: Avoiding Hard Aspects
    ---------------------------------
    Hard aspects (squares and oppositions) bring tension and obstacles.
    no_hard_aspect() checks that a planet has no applying hard aspects.
    """
    print_header("Example 14: Avoiding Hard Aspects")

    print("Query: Moon has NO applying squares or oppositions")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(no_hard_aspect("Moon"))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


def example_15_malefic_avoidance():
    """
    Example 15: Malefic Avoidance (Mars/Saturn)
    -------------------------------------------
    Mars and Saturn are traditional "malefics" - they can bring
    difficulties, delays, and conflict. no_malefic_aspect() specifically
    checks for hard aspects from Mars or Saturn.
    """
    print_header("Example 15: Malefic Avoidance")

    print("Query: Moon has no hard aspects from Mars or Saturn")
    print("(Avoids applying conjunction, square, opposition to malefics)")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(no_malefic_aspect("Moon"))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


def example_16_complex_aspect_combinations():
    """
    Example 16: Complex Aspect Combinations
    ---------------------------------------
    Combine aspect requirements with boolean logic for sophisticated
    electional criteria.
    """
    print_header("Example 16: Complex Aspect Combinations")

    print("Query: Moon applying to Jupiter OR Venus (harmonious)")
    print("       AND Moon has no hard aspects from Mars or Saturn")
    print()

    benefic_contact = any_of(
        aspect_applying("Moon", "Jupiter", ["conjunction", "trine", "sextile"]),
        aspect_applying("Moon", "Venus", ["conjunction", "trine", "sextile"]),
    )

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(benefic_contact)
        .where(no_malefic_aspect("Moon"))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


# =============================================================================
# PART 5: HOUSE & ANGLE CONDITIONS
# =============================================================================


def example_17_angular_planets():
    """
    Example 17: Angular Planets
    ---------------------------
    Angular houses (1, 4, 7, 10) are the most powerful positions.
    Planets there have maximum influence. on_angle() checks for this.
    """
    print_header("Example 17: Angular Planets")

    print("A) Jupiter angular (in houses 1, 4, 7, or 10):")
    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(on_angle("Jupiter"))
        .find_moments(max_results=5, step="hour")
    )
    print_results(results, max_show=5)

    print("\n" + "-" * 50)

    print("\nB) Moon angular:")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(on_angle("Moon"))
        .find_moments(max_results=5, step="hour")
    )
    print_results(results, max_show=5)


def example_18_avoiding_difficult_houses():
    """
    Example 18: Avoiding Difficult Houses
    -------------------------------------
    Houses 6, 8, and 12 are traditionally "difficult" houses associated
    with illness, death, and hidden enemies. Avoid key planets there.
    """
    print_header("Example 18: Avoiding Difficult Houses")

    print("Query: Moon NOT in houses 6, 8, or 12")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_in_house("Moon", [6, 8, 12]))
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


def example_19_benefics_in_good_houses():
    """
    Example 19: Benefics in Good Houses
    -----------------------------------
    Jupiter and Venus are "benefics" - they bring good fortune.
    Having them in prominent houses (1, 4, 7, 10, 11) strengthens
    an election.
    """
    print_header("Example 19: Benefics in Good Houses")

    print("Query: Jupiter in houses 1, 4, 7, 10, or 11")
    print("       OR Venus in houses 1, 4, 7, 10, or 11")
    print()

    good_houses = [1, 4, 7, 10, 11]

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(
            any_of(
                in_house("Jupiter", good_houses),
                in_house("Venus", good_houses),
            )
        )
        .find_moments(max_results=5, step="hour")
    )
    print_results(results, max_show=5)


# =============================================================================
# PART 6: COMPOSITION & COMPLEX QUERIES
# =============================================================================


def example_20_and_logic():
    """
    Example 20: AND Logic (all_of)
    ------------------------------
    all_of() requires ALL conditions to be true.
    This is equivalent to chaining .where() calls.
    """
    print_header("Example 20: AND Logic (all_of)")

    print("These two searches are equivalent:")
    print()
    print("A) Using chained .where() calls:")

    results1 = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(not_retrograde("Mercury"))
        .find_moments(max_results=3, step="day")
    )
    print(f"   Found: {len(results1)} results")

    print("\nB) Using all_of():")
    combined = all_of(is_waxing(), not_voc(), not_retrograde("Mercury"))

    results2 = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(combined)
        .find_moments(max_results=3, step="day")
    )
    print(f"   Found: {len(results2)} results")


def example_21_or_logic():
    """
    Example 21: OR Logic (any_of)
    -----------------------------
    any_of() requires AT LEAST ONE condition to be true.
    """
    print_header("Example 21: OR Logic (any_of)")

    print("Query: Moon in Cancer OR Moon in Taurus (dignity)")
    print()

    dignified_moon = any_of(
        sign_in("Moon", ["Cancer"]),  # Domicile
        sign_in("Moon", ["Taurus"]),  # Exaltation
    )

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(dignified_moon)
        .find_moments(max_results=5, step="day")
    )
    print_results(results, max_show=5)


def example_22_not_logic():
    """
    Example 22: NOT Logic (not_)
    ----------------------------
    not_() negates a condition. You can negate any predicate or
    composed condition.
    """
    print_header("Example 22: NOT Logic (not_)")

    print("A) NOT waning = waxing:")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_(is_waning()))
        .find_moments(max_results=3, step="day")
    )
    print(f"   Found: {len(results)} results")

    print("\nB) NOT (Moon in fire signs):")
    fire_signs = sign_in("Moon", ["Aries", "Leo", "Sagittarius"])

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(not_(fire_signs))
        .find_moments(max_results=3, step="day")
    )
    print_results(results, max_show=3)


def example_23_nested_boolean():
    """
    Example 23: Nested Boolean Expressions
    --------------------------------------
    Compose arbitrarily complex conditions by nesting all_of, any_of, not_.
    """
    print_header("Example 23: Nested Boolean Expressions")

    print("Query: (Moon trine Jupiter OR Moon sextile Venus)")
    print("       AND NOT (Moon in Scorpio OR Moon in Capricorn)")
    print("       AND Moon is waxing")
    print()

    # Build each piece
    good_aspect = any_of(
        aspect_applying("Moon", "Jupiter", ["trine"]),
        aspect_applying("Moon", "Venus", ["sextile"]),
    )

    bad_sign = any_of(
        sign_in("Moon", ["Scorpio"]),
        sign_in("Moon", ["Capricorn"]),
    )

    # Combine
    complex_condition = all_of(good_aspect, not_(bad_sign), is_waxing())

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(complex_condition)
        .find_moments(max_results=5, step="4hour")
    )
    print_results(results, max_show=5)


def example_24_regulus_talisman():
    """
    Example 24: The Reddit "Regulus Talisman" Query
    -----------------------------------------------
    This is inspired by the Reddit post that sparked this feature.
    A Regulus talisman election requires many strict conditions:

    1. Regulus applying conjunction to Ascendant OR Midheaven
    2. Regulus NOT in applying square/opposition to any planet
    3. Moon applying conjunction/trine/sextile to Regulus
    4. Moon waxing
    5. Moon NOT combust
    6. Moon NOT in applying square/opposition to any planet
    7. Moon NOT in detriment (Capricorn) or fall (Scorpio)
    8. Moon NOT void of course

    Note: Some conditions (like Regulus on exact Ascendant) require
    Phase 2 optimization to search efficiently. This example shows
    the Moon-focused conditions.
    """
    print_header("Example 24: Reddit 'Regulus Talisman' Query (Moon Conditions)")

    print("Strict traditional election criteria:")
    print("  - Moon waxing")
    print("  - Moon NOT void of course")
    print("  - Moon NOT combust")
    print("  - Moon NOT in Scorpio or Capricorn")
    print("  - Moon has NO applying hard aspects")
    print("  - Moon has NO hard aspects from Mars or Saturn")
    print()
    print("Searching 3 months...")
    print()

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(not_combust("Moon"))
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .where(no_hard_aspect("Moon"))
        .where(no_malefic_aspect("Moon"))
        .find_moments(max_results=10, step="4hour")
    )

    print_results(results, max_show=10)


# =============================================================================
# PART 7: PRACTICAL ELECTIONS
# =============================================================================


def example_25_general_good_times():
    """
    Example 25: General Good Times
    ------------------------------
    A simple "generally good" election for any important undertaking.
    """
    print_header("Example 25: General Good Times")

    print("Criteria for generally auspicious times:")
    print("  - Moon waxing")
    print("  - Moon NOT void of course")
    print("  - Moon NOT in difficult signs (Scorpio, Capricorn)")
    print("  - Mercury NOT retrograde")
    print()

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .where(not_retrograde("Mercury"))
        .find_moments(max_results=10, step="4hour")
    )

    print_results(results, max_show=10)


def example_26_business_launch():
    """
    Example 26: Business Launch Election
    ------------------------------------
    For starting a business, emphasize:
    - Strong Moon (waxing, not VOC, good sign)
    - Mercury direct (communication, contracts)
    - Jupiter well-placed (expansion, success)
    - No major malefic afflictions
    """
    print_header("Example 26: Business Launch Election")

    print("Criteria for launching a business:")
    print("  - Moon waxing (growth)")
    print("  - Moon NOT void of course")
    print("  - Mercury NOT retrograde (contracts)")
    print("  - Moon NOT square/opposite Saturn (delays)")
    print("  - Jupiter in good house (1, 4, 7, 10, 11)")
    print()

    good_jupiter = in_house("Jupiter", [1, 4, 7, 10, 11])
    no_saturn_trouble = no_aspect("Moon", "Saturn", ["square", "opposition"])

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(not_retrograde("Mercury"))
        .where(no_saturn_trouble)
        .where(good_jupiter)
        .find_moments(max_results=10, step="hour")
    )

    print_results(results, max_show=10)


def example_27_relationship_election():
    """
    Example 27: Relationship/Marriage Election
    ------------------------------------------
    For relationships and marriage, emphasize:
    - Venus strong and well-aspected
    - Moon in good aspect to Venus
    - 7th house (partnerships) well-supported
    - Avoid Venus retrograde
    """
    print_header("Example 27: Relationship/Marriage Election")

    print("Criteria for relationship matters:")
    print("  - Moon waxing")
    print("  - Venus NOT retrograde")
    print("  - Moon applying trine or sextile to Venus")
    print("  - Moon NOT in difficult signs")
    print()

    moon_venus_harmony = aspect_applying(
        "Moon", "Venus", ["conjunction", "trine", "sextile"]
    )

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(not_retrograde("Venus"))
        .where(moon_venus_harmony)
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .find_moments(max_results=10, step="4hour")
    )

    print_results(results, max_show=10)


def example_28_mercury_matters():
    """
    Example 28: Mercury Matters (Contracts, Communication, Travel)
    --------------------------------------------------------------
    For Mercury-ruled activities (writing, contracts, communication,
    short trips, learning), emphasize:
    - Mercury direct
    - Mercury well-aspected
    - Moon applying to Mercury
    """
    print_header("Example 28: Mercury Matters")

    print("Criteria for contracts, communication, travel:")
    print("  - Mercury NOT retrograde")
    print("  - Moon applying to Mercury (any aspect)")
    print("  - Moon waxing and not VOC")
    print()

    moon_mercury_contact = aspect_applying(
        "Moon", "Mercury", ["conjunction", "sextile", "trine"]
    )

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(not_retrograde("Mercury"))
        .where(moon_mercury_contact)
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=10, step="4hour")
    )

    print_results(results, max_show=10)


def example_29_mars_matters():
    """
    Example 29: Mars Matters (Competition, Surgery, Physical Action)
    ----------------------------------------------------------------
    For Mars-ruled activities (competition, surgery, physical feats,
    confrontation), emphasize:
    - Mars well-placed and direct
    - Mars not afflicted
    - Moon supporting Mars (if desired) or avoiding (if unwanted)
    """
    print_header("Example 29: Mars Matters")

    print("Criteria for competition, physical action:")
    print("  - Mars NOT retrograde")
    print("  - Mars NOT in detriment (Cancer, Libra)")
    print("  - Moon NOT square or opposite Mars")
    print("  - Moon waxing")
    print()

    no_moon_mars_tension = no_aspect("Moon", "Mars", ["square", "opposition"])

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(not_retrograde("Mars"))
        .where(not_debilitated("Mars"))
        .where(no_moon_mars_tension)
        .where(is_waxing())
        .find_moments(max_results=10, step="day")
    )

    print_results(results, max_show=10)


def example_30_jupiter_matters():
    """
    Example 30: Jupiter Matters (Expansion, Luck, Legal, Education)
    ---------------------------------------------------------------
    For Jupiter-ruled activities (legal matters, education, publishing,
    long journeys, expansion), emphasize:
    - Jupiter direct and well-placed
    - Moon in good aspect to Jupiter
    """
    print_header("Example 30: Jupiter Matters")

    print("Criteria for expansion, legal, education:")
    print("  - Jupiter NOT retrograde")
    print("  - Moon applying trine or sextile to Jupiter")
    print("  - Moon waxing and not VOC")
    print()

    moon_jupiter_harmony = aspect_applying("Moon", "Jupiter", ["trine", "sextile"])

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(not_retrograde("Jupiter"))
        .where(moon_jupiter_harmony)
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=10, step="4hour")
    )

    print_results(results, max_show=10)


# =============================================================================
# PART 8: ASPECT EXACTITUDE
# =============================================================================


def example_31_aspect_exactitude():
    """
    Example 31: Finding Moments Near Exact Aspects
    ----------------------------------------------
    aspect_exact_within() finds moments when two planets are within a tight
    orb of an exact aspect. This is useful for talismanic elections where
    you want aspects to be perfecting or just perfected.
    """
    print_header("Example 31: Aspect Exactitude")

    print("Query: Moon within 1° of exact trine to Jupiter")
    print("(For Jupiter talismans, prosperity elections)")
    print()

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(aspect_exact_within("Moon", "Jupiter", "trine", orb=1.0))
        .where(is_waxing())
        .find_moments(max_results=5, step="30min")
    )

    print_results(results, max_show=5)

    # Show the actual Moon-Jupiter separation
    if results:
        print("\nMoon-Jupiter separations:")
        for m in results[:3]:
            moon = m.chart.get_object("Moon")
            jupiter = m.chart.get_object("Jupiter")
            diff = abs(jupiter.longitude - moon.longitude)
            if diff > 180:
                diff = 360 - diff
            error = abs(diff - 120)  # 120° = trine
            print(
                f"  {m.datetime.strftime('%b %d %H:%M')}: {diff:.2f}° ({error:.2f}° from exact)"
            )


def example_32_tight_orb_elections():
    """
    Example 32: Tight Orb Elections
    -------------------------------
    For talismanic work, tighter orbs are often preferred.
    Combine aspect_exact_within with other conditions.
    """
    print_header("Example 32: Tight Orb Elections")

    print("Query: Venus within 0.5° of exact sextile to Jupiter")
    print("       + Moon waxing + not VOC")
    print("(Excellent for love/prosperity talismans)")
    print()

    results = (
        ElectionalSearch(*QUARTER_RANGE, DEFAULT_LOCATION)
        .where(aspect_exact_within("Venus", "Jupiter", "sextile", orb=0.5))
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=5, step="hour")
    )

    print_results(results, max_show=5)


# =============================================================================
# PART 9: FIXED STARS & ANGLES
# =============================================================================


def example_33_fixed_star_on_angle():
    """
    Example 33: Fixed Star on Angle (Regulus Rising)
    ------------------------------------------------
    star_on_angle() finds moments when a fixed star is conjunct an angle.
    This is essential for stellar magic and talismanic elections.

    Fixed stars rotate with the celestial sphere, crossing each angle
    roughly once per day (like the Sun's diurnal motion).
    """
    print_header("Example 33: Fixed Star on Angle")

    print("Query: Regulus (Heart of the Lion) on MC")
    print("Regulus: Success, fame, leadership, military honors")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(star_on_angle("Regulus", "MC", orb=1.0))
        .find_moments(max_results=5, step="minute")
    )

    print(f"Found {len(results)} moments with Regulus on MC")
    if results:
        for m in results[:3]:
            houses = m.chart.get_houses()
            mc = houses.get_cusp(10)
            print(
                f"  {m.datetime.strftime('%b %d %H:%M')} - MC at {mc:.1f}° (Regulus ~150°)"
            )

    print("\n" + "-" * 50)
    print("\nOther notable fixed stars for elections:")
    print("  Spica (224°):  Brilliance, talent, gifts")
    print("  Sirius (104°): Fame, ambition, devotion")
    print("  Algol (56°):   Transformation, intensity")
    print("  Fomalhaut (334°): Magic, idealism, charisma")


def example_34_specific_degrees():
    """
    Example 34: Specific Degrees on Angles
    --------------------------------------
    angle_at_degree() is more general - find when any degree rises or
    culminates. Useful for:
    - Critical degrees (0°, 15°, 29° of signs)
    - Natal chart activations
    - Specific zodiacal points
    """
    print_header("Example 34: Specific Degrees on Angles")

    print("A) 0° Aries rising (Vernal Point = new beginnings):")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(angle_at_degree(0.0, "ASC", orb=1.0))
        .find_moments(max_results=3, step="minute")
    )
    print(f"   Found {len(results)} moments")
    for m in results[:2]:
        houses = m.chart.get_houses()
        asc = houses.get_cusp(1)
        print(f"   {m.datetime.strftime('%b %d %H:%M')} - ASC at {asc:.1f}°")

    print("\n" + "-" * 50)
    print("\nB) 15° Leo on MC (Royal degree of Leo):")
    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(angle_at_degree(135.0, "MC", orb=1.0))  # 15° Leo = 120° + 15° = 135°
        .find_moments(max_results=3, step="minute")
    )
    print(f"   Found {len(results)} moments")
    for m in results[:2]:
        houses = m.chart.get_houses()
        mc = houses.get_cusp(10)
        print(f"   {m.datetime.strftime('%b %d %H:%M')} - MC at {mc:.1f}°")


def example_35_complete_regulus_talisman():
    """
    Example 35: The Complete Regulus Talisman Election
    --------------------------------------------------
    This combines fixed star placement with traditional election criteria.
    A proper Regulus talisman election requires:

    1. Regulus conjunct MC or ASC (within 1°)
    2. Moon waxing
    3. Moon not void of course
    4. Moon not combust
    5. Moon not in detriment/fall (Scorpio, Capricorn)
    6. Moon no hard aspects from malefics
    """
    print_header("Example 35: Complete Regulus Talisman Election")

    print("Full traditional criteria:")
    print("  - Regulus on MC (within 1°)")
    print("  - Moon waxing")
    print("  - Moon not void of course")
    print("  - Moon not combust")
    print("  - Moon not in Scorpio or Capricorn")
    print("  - Moon no hard aspects from Mars/Saturn")
    print()
    print("Searching first 2 weeks of January...")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(star_on_angle("Regulus", "MC", orb=1.0))
        .where(is_waxing())
        .where(not_voc())
        .where(not_combust("Moon"))
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .where(no_malefic_aspect("Moon"))
        .find_moments(max_results=10, step="minute")
    )

    print(f"Found {len(results)} moments matching ALL criteria")
    print()

    if results:
        for i, m in enumerate(results[:5], 1):
            moon = m.chart.get_object("Moon")
            houses = m.chart.get_houses()
            mc = houses.get_cusp(10)
            print(f"{i}. {m.datetime.strftime('%a %b %d at %I:%M %p')}")
            print(f"   MC: {mc:.1f}° | Moon: {moon.sign} ({moon.phase.phase_name})")
    else:
        print("No perfect elections found in this range.")
        print("Try extending the search range or relaxing criteria.")


# =============================================================================
# PART 10: PLANETARY HOURS
# =============================================================================


def example_36_planetary_hours():
    """
    Example 36: Finding Planetary Hours
    -----------------------------------
    Planetary hours are a traditional timing system where each hour of the
    day is ruled by one of the seven classical planets in Chaldean order.

    The day starts at sunrise (not midnight), and hours are of unequal
    length - day hours = (sunset - sunrise) / 12, night hours = (sunrise - sunset) / 12.
    """
    print_header("Example 36: Planetary Hours")

    from datetime import datetime

    print("Planetary hours for San Francisco on Wednesday January 1, 2025:")
    print()

    hours = get_planetary_hours_for_day(
        datetime(2025, 1, 1),
        DEFAULT_LOCATION.latitude,
        DEFAULT_LOCATION.longitude,
    )

    print("Day hours (sunrise to sunset):")
    for h in hours[:12]:
        start_local = h.start_utc.hour - 8  # PST
        if start_local < 0:
            start_local += 24
        print(
            f"  Hour {h.hour_number:2d}: {h.ruler:8s} (~{start_local:02d}:{h.start_utc.minute:02d} local, {h.duration_minutes:.0f} min)"
        )

    print()
    print("Chaldean order:", " → ".join(CHALDEAN_ORDER))
    print()
    print("Day rulers:")
    for day_num, ruler in DAY_RULERS.items():
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        print(f"  {days[day_num]}: {ruler}")


def example_37_jupiter_hour_elections():
    """
    Example 37: Jupiter Hour Elections
    ----------------------------------
    Jupiter hours are traditionally favorable for:
    - Legal matters, lawsuits
    - Education, publishing
    - Long journeys, foreign affairs
    - Expansion, growth, prosperity
    - Religious/spiritual matters

    in_planetary_hour() finds times during a specific planet's hour.
    """
    print_header("Example 37: Jupiter Hour Elections")

    print("Query: Jupiter hours + Moon waxing + not VOC")
    print("(Excellent for expansion, luck, legal matters)")
    print()

    results = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(in_planetary_hour("Jupiter"))
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=10, step="hour")
    )

    print(f"Found {len(results)} Jupiter hour moments")
    print()

    if results:
        for m in results[:5]:
            moon = m.chart.get_object("Moon")
            hour = get_planetary_hour(
                m.datetime,
                DEFAULT_LOCATION.latitude,
                DEFAULT_LOCATION.longitude,
            )
            period = "day" if hour.is_day_hour else "night"
            print(
                f"  {m.datetime.strftime('%b %d %H:%M')} - {hour.ruler} hour ({period}) - Moon in {moon.sign}"
            )


def example_38_planetary_hours_combined():
    """
    Example 38: Combining Planetary Hours with Other Conditions
    -----------------------------------------------------------
    The most powerful elections combine planetary hours with other
    traditional criteria.

    Examples:
    - Venus hour on Friday for love (Venus rules Friday)
    - Mars hour on Tuesday for competition (Mars rules Tuesday)
    - Mercury hour when Mercury is not retrograde for contracts
    """
    print_header("Example 38: Planetary Hours Combined")

    print("A) Venus hour + Venus not retrograde + Moon waxing")
    print("   (For relationship matters, art, beauty)")
    print()

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(in_planetary_hour("Venus"))
        .where(not_retrograde("Venus"))
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=5, step="hour")
    )

    print(f"Found {len(results)} Venus hour moments")
    for m in results[:3]:
        print(f"  {m.datetime.strftime('%a %b %d %H:%M')}")

    print("\n" + "-" * 50)
    print("\nB) Sun hour + Sun angular + Moon waxing")
    print("   (For fame, recognition, authority matters)")
    print()

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(in_planetary_hour("Sun"))
        .where(on_angle("Sun"))
        .where(is_waxing())
        .find_moments(max_results=5, step="hour")
    )

    print(f"Found {len(results)} Sun hour + Sun angular moments")
    for m in results[:3]:
        house = m.chart.get_house("Sun")
        print(f"  {m.datetime.strftime('%a %b %d %H:%M')} - Sun in house {house}")


# =============================================================================
# PART 11: ADVANCED USAGE
# =============================================================================


def example_39_generator_iteration():
    """
    Example 39: Generator-Based Iteration (Memory Efficient)
    --------------------------------------------------------
    iter_moments() yields results one at a time without storing them all.
    Useful for very long searches or when you want to process as you go.
    """
    print_header("Example 39: Generator-Based Iteration")

    print("Processing results one at a time (first 5):")
    print()

    search = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
    )

    count = 0
    for moment in search.iter_moments(step="day"):
        count += 1
        moon = moment.chart.get_object("Moon")
        print(f"  {count}. {moment.datetime.strftime('%b %d')} - Moon in {moon.sign}")
        if count >= 5:
            break

    print("\n  (Stopped after 5 - generator continues to yield if needed)")


def example_40_counting():
    """
    Example 40: Counting Matches Without Storing
    --------------------------------------------
    count() tells you how many matches exist without storing them.
    Memory efficient for "how many?" questions.
    """
    print_header("Example 40: Counting Matches")

    print("How many 'waxing + not VOC' hours in January?")
    print()

    search = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
    )

    total = search.count(step="hour")
    print(f"  Total: {total} hours match the criteria")
    print(f"  That's about {total / 24:.1f} days worth of good times")


def example_41_custom_lambdas():
    """
    Example 41: Custom Lambda Conditions
    ------------------------------------
    For conditions not covered by predicates, write custom lambdas.
    You have full access to the CalculatedChart object.
    """
    print_header("Example 41: Custom Lambda Conditions")

    print("Custom condition: Moon faster than 13°/day")
    print("(Fast Moon = quicker manifestation)")
    print()

    def fast_moon(c):
        return c.get_object("Moon").speed_longitude > 13.0

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(fast_moon)
        .find_moments(max_results=5, step="day")
    )

    print_results(results, max_show=5, detailed=False)

    # Show Moon speeds
    if results:
        print("\nMoon speeds:")
        for m in results[:3]:
            moon = m.chart.get_object("Moon")
            print(f"  {m.datetime.strftime('%b %d')}: {moon.speed_longitude:.2f}°/day")


def example_42_integration_with_chartquery():
    """
    Example 42: Integration with ChartQuery
    ---------------------------------------
    ElectionalSearch finds times; ChartQuery filters existing charts.
    You can combine them: search for times, then filter further.
    """
    print_header("Example 42: Integration with ChartQuery")

    print("Step 1: Find election times")
    moments = (
        ElectionalSearch(*SHORT_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .find_moments(max_results=20, step="4hour")
    )
    print(f"  Found {len(moments)} moments")

    print("\nStep 2: Extract charts and filter with ChartQuery")
    from stellium.analysis import ChartQuery

    charts = [m.chart for m in moments]

    # Further filter: Sun in Capricorn
    filtered = ChartQuery(charts).where_sun(sign="Capricorn").results()

    print(f"  After ChartQuery filter: {len(filtered)} charts")
    print("  (Only those with Sun in Capricorn)")


def example_43_exporting_results():
    """
    Example 43: Exporting Results
    -----------------------------
    Save election results to a file for later reference.
    """
    print_header("Example 43: Exporting Results")

    print("Finding good times and exporting to file...")
    print()

    results = (
        ElectionalSearch(*MONTH_RANGE, DEFAULT_LOCATION)
        .where(is_waxing())
        .where(not_voc())
        .where(sign_not_in("Moon", ["Scorpio", "Capricorn"]))
        .where(not_retrograde("Mercury"))
        .find_moments(max_results=20, step="4hour")
    )

    # Export to text file
    output_file = OUTPUT_DIR / "january_2025_elections.txt"
    with open(output_file, "w") as f:
        f.write("Good Election Times - January 2025\n")
        f.write("=" * 50 + "\n\n")
        f.write("Criteria:\n")
        f.write("  - Moon waxing\n")
        f.write("  - Moon not void of course\n")
        f.write("  - Moon not in Scorpio or Capricorn\n")
        f.write("  - Mercury not retrograde\n\n")
        f.write(f"Found {len(results)} good times:\n\n")

        for i, m in enumerate(results, 1):
            moon = m.chart.get_object("Moon")
            f.write(f"{i}. {m.datetime.strftime('%a %b %d, %Y at %I:%M %p')}\n")
            if moon:
                f.write(f"   Moon: {moon.sign} ({moon.phase.phase_name})\n")
            f.write("\n")

    print(f"Exported {len(results)} results to:")
    print(f"  {output_file}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all examples."""
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           STELLIUM ELECTIONAL ASTROLOGY COOKBOOK                 ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  Find auspicious times matching astrological conditions          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # Uncomment the examples you want to run

    # --- Part 1: Basic Searches ---
    example_1_simplest_search()
    example_2_helper_predicates()
    example_3_time_windows()
    example_4_progress_callback()

    # --- Part 2: Moon Conditions ---
    example_5_moon_phase()
    example_6_void_of_course()
    example_7_moon_sign()
    example_8_moon_aspects()

    # --- Part 3: Planetary Conditions ---
    example_9_retrograde()
    example_10_dignity()
    example_11_combust()
    example_12_out_of_bounds()

    # --- Part 4: Aspect Conditions ---
    example_13_requiring_aspects()
    example_14_avoiding_hard_aspects()
    example_15_malefic_avoidance()
    example_16_complex_aspect_combinations()

    # --- Part 5: House & Angle Conditions ---
    example_17_angular_planets()
    example_18_avoiding_difficult_houses()
    example_19_benefics_in_good_houses()

    # --- Part 6: Composition & Complex Queries ---
    example_20_and_logic()
    example_21_or_logic()
    example_22_not_logic()
    example_23_nested_boolean()
    example_24_regulus_talisman()

    # --- Part 7: Practical Elections ---
    example_25_general_good_times()
    example_26_business_launch()
    example_27_relationship_election()
    example_28_mercury_matters()
    example_29_mars_matters()
    example_30_jupiter_matters()

    # --- Part 8: Aspect Exactitude ---
    example_31_aspect_exactitude()
    example_32_tight_orb_elections()

    # --- Part 9: Fixed Stars & Angles ---
    example_33_fixed_star_on_angle()
    example_34_specific_degrees()
    example_35_complete_regulus_talisman()

    # --- Part 10: Planetary Hours ---
    example_36_planetary_hours()
    example_37_jupiter_hour_elections()
    example_38_planetary_hours_combined()

    # --- Part 11: Advanced Usage ---
    example_39_generator_iteration()
    example_40_counting()
    example_41_custom_lambdas()
    example_42_integration_with_chartquery()
    example_43_exporting_results()

    print()
    print("=" * 70)
    print("COOKBOOK COMPLETE")
    print("=" * 70)
    print()
    print(f"Output files saved to: {OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
