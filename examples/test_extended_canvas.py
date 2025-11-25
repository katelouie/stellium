#!/usr/bin/env python3
"""
Test script for extended canvas features.

Tests:
1. Position table on right
2. Aspectarian on right
3. Both tables on right
4. Tables below chart
5. Tables on left
6. Extended canvas with different themes
"""

from starlight import ChartBuilder


def test_extended_right():
    """Test extended canvas to the right."""
    print("Testing extended canvas (right)...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    (
        chart.draw("examples/chart_examples/extended_right.svg")
        .without_moon_phase()
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_right.svg")


def test_extended_left():
    """Test extended canvas to the left."""
    print("\nTesting extended canvas (left)...")

    chart = ChartBuilder.from_notable("Marie Curie").calculate()

    (
        chart.draw("examples/chart_examples/extended_left.svg")
        .without_moon_phase()
        .with_tables(position="left", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_left.svg")


def test_extended_below():
    """Test extended canvas below."""
    print("\nTesting extended canvas (below)...")

    chart = ChartBuilder.from_notable("Frida Kahlo").calculate()

    (
        chart.draw("examples/chart_examples/extended_below.svg")
        .without_moon_phase()
        .with_tables(position="below", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_below.svg")


def test_extended_with_themes():
    """Test extended canvas with different themes."""
    print("\nTesting extended canvas with themes...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Dark theme
    (
        chart.draw("examples/chart_examples/extended_dark.svg")
        .with_theme("dark")
        .without_moon_phase()
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_dark.svg (dark theme)")

    # Midnight theme
    (
        chart.draw("examples/chart_examples/extended_midnight.svg")
        .with_theme("midnight")
        .without_moon_phase()
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_midnight.svg (midnight theme)")


def test_extended_with_corners():
    """Test extended canvas combined with corner info."""
    print("\nTesting extended canvas with corner info...")

    chart = ChartBuilder.from_notable("Marie Curie").calculate()

    (
        chart.draw("examples/chart_examples/extended_full_featured.svg")
        .with_moon_phase()
        .with_chart_info()
        .with_aspect_counts()
        .with_element_modality_table()
        .with_chart_shape()
        .with_tables(position="right", show_position_table=True, show_aspectarian=True)
        .save()
    )
    print("✓ Generated: extended_full_featured.svg (all features)")


if __name__ == "__main__":
    print("=" * 70)
    print("Extended Canvas Test Suite")
    print("=" * 70)

    test_extended_right()
    test_extended_left()
    test_extended_below()
    test_extended_with_themes()
    test_extended_with_corners()

    print("\n" + "=" * 70)
    print("All tests completed! Check examples/chart_examples/ for results.")
    print("=" * 70)
