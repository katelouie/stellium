#!/usr/bin/env python3
"""
Test script for new chart info and moon phase positioning features.

Tests:
1. Moon phase in different positions
2. Moon phase with label
3. Chart info in different corners
4. Combined moon phase and chart info
"""

from datetime import datetime
from stellium import ChartBuilder


def test_moon_positions():
    """Test moon phase in different positions."""
    print("Testing moon phase positions...")

    # Use a notable chart to avoid geocoding issues
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 1: Moon in center (default)
    chart.draw("examples/chart_examples/moon_center.svg").with_moon_phase().save()
    print("✓ Generated: moon_center.svg")

    # Test 2: Moon in top-right with label
    chart.draw("examples/chart_examples/moon_top_right_labeled.svg").with_moon_phase().save()
    print("✓ Generated: moon_top_right_labeled.svg")

    # Test 3: Moon in bottom-left with label
    chart.draw("examples/chart_examples/moon_bottom_left_labeled.svg").with_moon_phase().save()
    print("✓ Generated: moon_bottom_left_labeled.svg")


def test_chart_info():
    """Test chart info display."""
    print("\nTesting chart info display...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 4: Chart info in top-left
    (
        chart.draw("examples/chart_examples/chart_info_top_left.svg")
        .without_moon_phase()
        .with_chart_info()
        .save()
    )
    print("✓ Generated: chart_info_top_left.svg")

    # Test 5: Chart info in top-right
    (
        chart.draw("examples/chart_examples/chart_info_top_right.svg")
        .without_moon_phase()
        .with_chart_info()
        .save()
    )
    print("✓ Generated: chart_info_top_right.svg")


def test_combined():
    """Test combined moon phase and chart info."""
    print("\nTesting combined features...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 6: Moon in bottom-right, chart info in top-left
    (
        chart.draw("examples/chart_examples/combined_moon_and_info.svg")
        .with_moon_phase()
        .with_chart_info()
        .save()
    )
    print("✓ Generated: combined_moon_and_info.svg")

    # Test 7: Moon in top-right, chart info in top-left (showing full aspect lines)
    (
        chart.draw("examples/chart_examples/moon_corner_full_aspects.svg")
        .with_theme("dark")
        .with_moon_phase()
        .with_chart_info()
        .save()
    )
    print("✓ Generated: moon_corner_full_aspects.svg (with dark theme)")


def test_notable():
    """Test with a notable chart."""
    print("\nTesting with notable (Albert Einstein)...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Test 8: Full-featured chart with notable
    (
        chart.draw("examples/chart_examples/einstein_full_featured.svg")
        .with_theme("midnight")
        .with_moon_phase()
        .with_chart_info()
        .save()
    )
    print("✓ Generated: einstein_full_featured.svg")


if __name__ == "__main__":
    print("=" * 60)
    print("Chart Info & Moon Phase Positioning Test Suite")
    print("=" * 60)

    test_moon_positions()
    test_chart_info()
    test_combined()
    test_notable()

    print("\n" + "=" * 60)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 60)
