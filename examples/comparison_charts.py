"""
Comparison Charts Examples - Synastry, Transits, and Progressions

This example demonstrates how to use Stellium's comparison chart features
to analyze relationships (synastry), timing (transits), and symbolic development
(progressions).

Comparison charts calculate aspects BETWEEN two charts, as well as house overlays
(where one chart's planets fall in another chart's houses).
"""

import datetime as dt
from datetime import datetime

from stellium.core.builder import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.engines.aspects import CrossChartAspectEngine, ModernAspectEngine
from stellium.engines.orbs import SimpleOrbEngine


# ===== Example 1: Basic Synastry =====
def example_basic_synastry():
    """
    Calculate synastry between two people.

    Synastry shows how two people's charts interact - which planets
    aspect each other, and where each person's planets fall in the
    other's houses.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Synastry")
    print("=" * 60)

    # Create location
    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    # Person A's birth data
    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    # Person B's birth data
    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    # Calculate synastry using default settings
    synastry = (
        ComparisonBuilder.from_native(chart_a, native_label="Person A")
        .with_partner(chart_b, partner_label="Person B")
        .calculate()
    )

    # Display results
    print(f"\nSynastry between {synastry.chart1_label} and {synastry.chart2_label}")
    print(f"Comparison type: {synastry.comparison_type.value}")
    print(f"\nCross-chart aspects found: {len(synastry.cross_aspects)}")

    # Show first 5 aspects
    print("\nFirst 5 aspects:")
    for i, asp in enumerate(synastry.cross_aspects[:5], 1):
        print(
            f"  {i}. {asp.object1.name} ({synastry.chart1_label}) "
            f"{asp.aspect_name} "
            f"{asp.object2.name} ({synastry.chart2_label}) "
            f"(orb: {asp.orb:.2f}°)"
        )

    # Show house overlays
    print(f"\nHouse overlays calculated: {len(synastry.house_overlays)}")

    # Example: Person A's Sun in Person B's houses
    a_sun_overlay = [
        o
        for o in synastry.house_overlays
        if o.planet_name == "Sun" and o.planet_owner == "chart1"
    ]
    if a_sun_overlay:
        overlay = a_sun_overlay[0]
        print(
            f"\n{synastry.chart1_label}'s Sun falls in "
            f"{synastry.chart2_label}'s house {overlay.falls_in_house}"
        )


# ===== Example 2: Transits =====
def example_transits():
    """
    Calculate current transits to a natal chart.

    Transits show how current planetary positions aspect your
    natal chart. Useful for timing and prediction.
    """
    print("\n" + "=" * 60)
    print("Example 2: Transits")
    print("=" * 60)

    # Natal chart
    los_angeles = ChartLocation(
        latitude=34.0522, longitude=-118.2437, name="Los Angeles, CA"
    )
    native = Native(datetime(1988, 11, 22, 8, 45, tzinfo=dt.UTC), los_angeles)
    natal = ChartBuilder.from_native(native).calculate()

    # Current time (transits)
    transit_time = datetime(2025, 11, 16, 20, 0, tzinfo=dt.UTC)

    # Calculate transits
    # Note: Transits use natal's location by default
    transits = (
        ComparisonBuilder.from_native(natal, native_label="Natal")
        .with_transit(transit_time)
        .calculate()
    )

    print(f"\nTransits for {transits.chart1_label}")
    print(f"Natal: {natal.datetime.local_datetime}")
    print(f"Transit: {transits.chart2_datetime.local_datetime}")
    print(f"\nTransit aspects found: {len(transits.cross_aspects)}")

    # Transits use tighter orbs by default (3°/2° instead of 6°/4°)
    print("\nNote: Transits use tight orbs (3°/2°) for timing precision")

    # Show transits by natal planet
    print("\nTransits to natal Sun:")
    sun_transits = [
        asp
        for asp in transits.cross_aspects
        if asp.object1.name == "Sun"  # Natal Sun is from chart1
    ]

    for asp in sun_transits[:3]:  # First 3
        applying = "applying" if asp.is_applying else "separating"
        print(
            f"  Transit {asp.object2.name} {asp.aspect_name} "
            f"natal Sun (orb: {asp.orb:.2f}°, {applying})"
        )


# ===== Example 3: Custom Orbs =====
def example_custom_orbs():
    """
    Use custom orb allowances for synastry.

    Sometimes you want tighter or wider orbs than the defaults.
    """
    print("\n" + "=" * 60)
    print("Example 3: Custom Orbs")
    print("=" * 60)

    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    # Use very tight orbs (like transit orbs)
    tight_orbs = SimpleOrbEngine(
        orb_map={
            "Conjunction": 3.0,
            "Sextile": 2.0,
            "Square": 3.0,
            "Trine": 3.0,
            "Opposition": 3.0,
        }
    )

    synastry_tight = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .with_orb_engine(tight_orbs)
        .calculate()
    )

    print(
        f"Synastry with tight orbs (3°/2°): {len(synastry_tight.cross_aspects)} aspects"
    )

    # Compare with default synastry orbs (6°/4°)
    synastry_normal = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .calculate()
    )

    print(
        f"Synastry with normal orbs (6°/4°): {len(synastry_normal.cross_aspects)} aspects"
    )
    print(
        f"\nDifference: {len(synastry_normal.cross_aspects) - len(synastry_tight.cross_aspects)} "
        "more aspects with wider orbs"
    )


# ===== Example 4: Without House Overlays =====
def example_without_house_overlays():
    """
    Calculate synastry without house overlays.

    If you only care about aspects and not house placements,
    you can disable house overlay calculation for faster results.
    """
    print("\n" + "=" * 60)
    print("Example 4: Synastry Without House Overlays")
    print("=" * 60)

    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    # Disable house overlays
    synastry = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .without_house_overlays()
        .calculate()
    )

    print(f"Cross-aspects calculated: {len(synastry.cross_aspects)}")
    print(f"House overlays calculated: {len(synastry.house_overlays)}")
    print("\nHouse overlays disabled - only aspects calculated")


# ===== Example 5: Query Methods =====
def example_query_methods():
    """
    Use Comparison query methods to find specific information.

    The Comparison object provides helper methods to query aspects
    and house overlays for specific planets.
    """
    print("\n" + "=" * 60)
    print("Example 5: Query Methods")
    print("=" * 60)

    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .calculate()
    )

    # Get aspects involving a specific planet
    print("\nAspects involving Person A's Venus:")
    venus_aspects = synastry.get_object_aspects("Venus", chart=1)
    for asp in venus_aspects[:3]:  # First 3
        print(f"  {asp.object1.name} {asp.aspect_name} {asp.object2.name}")

    # Get house overlays for a specific planet
    print("\nWhere does Person A's Mars fall in Person B's chart?")
    mars_overlays = synastry.get_object_houses("Mars", chart=1)
    for overlay in mars_overlays:
        if overlay.house_owner == "chart2":
            print(f"  Person A's Mars in Person B's house {overlay.falls_in_house}")

    # Get all planets in a specific house
    print("\nWhat falls in Person B's 7th house (relationships)?")
    seventh_house = synastry.get_objects_in_house(
        house_number=7, house_owner=2, planet_owner="both"
    )
    for overlay in seventh_house:
        owner = "Person A" if overlay.planet_owner == "chart1" else "Person B"
        print(f"  {owner}'s {overlay.planet_name}")


# ===== Example 6: Compatibility Scoring =====
def example_compatibility_scoring():
    """
    Use the built-in compatibility scoring.

    The Comparison class includes a simple compatibility score
    based on aspect harmony. You can customize the weights.
    """
    print("\n" + "=" * 60)
    print("Example 6: Compatibility Scoring")
    print("=" * 60)

    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .calculate()
    )

    # Default weights (harmonious positive, challenging negative/neutral)
    score = synastry.calculate_compatibility_score()
    print(f"\nCompatibility score (default weights): {score:.1f}/100")

    # Custom weights (maybe you care more about trines)
    custom_weights = {
        "Conjunction": 0.3,  # Somewhat positive
        "Sextile": 0.8,  # Harmonious
        "Square": -0.8,  # More challenging
        "Trine": 1.5,  # VERY harmonious (weighted higher)
        "Opposition": 0.0,  # Neutral (polarizing but connecting)
    }

    custom_score = synastry.calculate_compatibility_score(weights=custom_weights)
    print(f"Compatibility score (custom weights): {custom_score:.1f}/100")

    print(
        "\nNote: Compatibility is complex! This is just a simple numerical indicator."
    )


# ===== Example 7: Advanced - Custom Aspect Engine =====
def example_custom_aspect_engine():
    """
    Use a custom aspect engine configuration.

    You can control which aspects are calculated by providing
    a custom CrossChartAspectEngine with an AspectConfig.
    """
    print("\n" + "=" * 60)
    print("Example 7: Custom Aspect Engine")
    print("=" * 60)

    from stellium.core.config import AspectConfig

    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    person_a = Native(datetime(1990, 3, 15, 14, 30, tzinfo=dt.UTC), new_york)
    chart_a = ChartBuilder.from_native(person_a).calculate()

    person_b = Native(datetime(1992, 7, 8, 9, 15, tzinfo=dt.UTC), new_york)
    chart_b = ChartBuilder.from_native(person_b).calculate()

    # Only calculate hard aspects (conjunction, square, opposition)
    hard_aspects_config = AspectConfig(
        aspects=["Conjunction", "Square", "Opposition"],
        include_angles=True,
        include_asteroids=False,  # Skip asteroids for speed
    )

    hard_aspects_engine = CrossChartAspectEngine(config=hard_aspects_config)

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .with_aspect_engine(hard_aspects_engine)
        .calculate()
    )

    print(f"\nHard aspects only: {len(synastry.cross_aspects)} aspects")

    # Show breakdown by aspect type
    aspect_counts = {}
    for asp in synastry.cross_aspects:
        aspect_counts[asp.aspect_name] = aspect_counts.get(asp.aspect_name, 0) + 1

    print("\nBreakdown:")
    for aspect_name, count in sorted(aspect_counts.items()):
        print(f"  {aspect_name}: {count}")


# ===== Run All Examples =====
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("STARLIGHT COMPARISON CHARTS EXAMPLES")
    print("=" * 60)
    print("\nDemonstrating synastry, transits, and progressions")
    print("with various configuration options.\n")

    example_basic_synastry()
    example_transits()
    example_custom_orbs()
    example_without_house_overlays()
    example_query_methods()
    example_compatibility_scoring()
    example_custom_aspect_engine()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
    print(
        "\nFor more information, see the comparison.py module docstring"
        "\nand the ComparisonBuilder API documentation."
    )
