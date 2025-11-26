#!/usr/bin/env python3
"""
Test script for bi-wheel comparison chart drawing.

Tests the new draw_comparison_chart function with a synastry example.
"""

from datetime import datetime
import datetime as dt

from stellium import ChartBuilder, ComparisonBuilder
from stellium.core.models import ChartLocation


def test_basic_synastry():
    """Test basic synastry bi-wheel chart."""
    print("Testing basic synastry bi-wheel chart...")

    # Create location
    new_york = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York, NY")

    # Person A's birth data
    person_a_native = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Person B's birth data
    person_b = ChartBuilder.from_notable("Marie Curie").calculate()

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(person_a_native, native_label="Albert Einstein")
        .with_partner(person_b, partner_label="Marie Curie")
        .calculate()
    )

    # Draw bi-wheel chart
    (
        synastry.draw("examples/chart_examples/biwheel_synastry_basic.svg")
        .with_theme("classic")
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save()
    )

    print("✓ Generated: biwheel_synastry_basic.svg")


def test_synastry_themes():
    """Test synastry with different themes."""
    print("\nTesting synastry with different themes...")

    # Get two charts
    chart_a = ChartBuilder.from_notable("Frida Kahlo").calculate()
    chart_b = ChartBuilder.from_notable("Marie Curie").calculate()

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(chart_a, "Frida")
        .with_partner(chart_b, partner_label="Marie")
        .calculate()
    )

    # Dark theme
    (
        synastry.draw("examples/chart_examples/biwheel_synastry_dark.svg")
        .with_theme("dark")
        .with_tables(position="right")
        .save()
    )
    print("✓ Generated: biwheel_synastry_dark.svg (dark theme)")

    # Midnight theme
    (
        synastry.draw("examples/chart_examples/biwheel_synastry_midnight.svg")
        .with_theme("midnight")
        .with_tables(position="right")
        .save()
    )
    print("✓ Generated: biwheel_synastry_midnight.svg (midnight theme)")


def test_extended_canvas_positions():
    """Test different extended canvas positions."""
    print("\nTesting different extended canvas positions...")

    chart_a = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart_b = ChartBuilder.from_notable("Frida Kahlo").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Einstein")
        .with_partner(chart_b, partner_label="Frida")
        .calculate()
    )

    # Extended canvas on left
    (
        synastry.draw("examples/chart_examples/biwheel_extended_left.svg")
        .with_tables(position="left")
        .with_theme("classic")
        .save()
    )
    print("✓ Generated: biwheel_extended_left.svg")

    # Extended canvas below
    (
        synastry.draw("examples/chart_examples/biwheel_extended_below.svg")
        .with_tables(position="below")
        .with_theme("classic")
        .save()
    )
    print("✓ Generated: biwheel_extended_below.svg")


if __name__ == "__main__":
    print("=" * 70)
    print("Bi-Wheel Comparison Chart Test Suite")
    print("=" * 70)

    test_basic_synastry()
    test_synastry_themes()
    test_extended_canvas_positions()

    print("\n" + "=" * 70)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 70)
