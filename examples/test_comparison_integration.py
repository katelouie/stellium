#!/usr/bin/env python3
"""
Test script for bi-wheel comparison chart integration with ChartDrawBuilder.

Tests the integration of:
- Comparison.draw() method
- ChartDrawBuilder.with_tables() method
- ChartDrawBuilder.preset_synastry() auto-configuration for Comparison objects
"""

from datetime import datetime
import datetime as dt

from stellium import ChartBuilder, ComparisonBuilder
from stellium.core.models import ChartLocation


def test_comparison_draw_method():
    """Test Comparison.draw() method with fluent builder API."""
    print("Testing Comparison.draw() method...")

    # Create synastry
    chart_a = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart_b = ChartBuilder.from_notable("Marie Curie").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Einstein")
        .with_partner(chart_b, "Curie")
        .calculate()
    )

    # Use .draw() method directly on Comparison object
    synastry.draw("examples/chart_examples/synastry_draw_method.svg") \
        .with_theme("midnight") \
        .with_tables(position="right") \
        .save()

    print("✓ Generated: synastry_draw_method.svg")


def test_preset_synastry_auto_config():
    """Test preset_synastry() auto-configuration for Comparison objects."""
    print("\nTesting preset_synastry() auto-configuration...")

    chart_a = ChartBuilder.from_notable("Frida Kahlo").calculate()
    chart_b = ChartBuilder.from_notable("Marie Curie").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Frida")
        .with_partner(chart_b, "Marie")
        .calculate()
    )

    # preset_synastry() should automatically configure bi-wheel layout
    synastry.draw("examples/chart_examples/synastry_preset_auto.svg") \
        .preset_synastry() \
        .save()

    print("✓ Generated: synastry_preset_auto.svg (auto bi-wheel)")


def test_with_tables_variations():
    """Test various with_tables() configurations."""
    print("\nTesting with_tables() variations...")

    chart_a = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart_b = ChartBuilder.from_notable("Frida Kahlo").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Einstein")
        .with_partner(chart_b, "Frida")
        .calculate()
    )

    # Position table only
    synastry.draw("examples/chart_examples/synastry_position_table_only.svg") \
        .with_theme("classic") \
        .with_tables(position="right", show_aspectarian=False) \
        .save()
    print("✓ Generated: synastry_position_table_only.svg (position table only)")

    # Aspectarian only
    synastry.draw("examples/chart_examples/synastry_aspectarian_only.svg") \
        .with_theme("dark") \
        .with_tables(position="right", show_position_table=False) \
        .save()
    print("✓ Generated: synastry_aspectarian_only.svg (aspectarian only)")

    # Tables on left
    synastry.draw("examples/chart_examples/synastry_tables_left.svg") \
        .with_theme("celestial") \
        .with_tables(position="left") \
        .save()
    print("✓ Generated: synastry_tables_left.svg (tables on left)")

    # Tables below
    synastry.draw("examples/chart_examples/synastry_tables_below.svg") \
        .with_theme("pastel") \
        .with_tables(position="below") \
        .save()
    print("✓ Generated: synastry_tables_below.svg (tables below)")


def test_custom_configuration():
    """Test custom builder configuration for comparison charts."""
    print("\nTesting custom configuration...")

    chart_a = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart_b = ChartBuilder.from_notable("Marie Curie").calculate()

    synastry = (
        ComparisonBuilder.from_native(chart_a, "Einstein")
        .with_partner(chart_b, "Curie")
        .calculate()
    )

    # Fully custom configuration
    synastry.draw("examples/chart_examples/synastry_custom.svg") \
        .with_size(800) \
        .with_theme("neon") \
        .with_tables(position="right", aspectarian_mode="cross_chart") \
        .with_chart_info(position="top-left") \
        .with_aspect_counts(position="top-right") \
        .without_moon_phase() \
        .save()
    print("✓ Generated: synastry_custom.svg (custom configuration)")


def test_natal_chart_unchanged():
    """Verify natal charts still work with with_tables()."""
    print("\nTesting natal chart compatibility...")

    chart = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Natal chart with tables should still work
    chart.draw("examples/chart_examples/natal_with_tables.svg") \
        .with_theme("classic") \
        .with_tables(position="right") \
        .save()
    print("✓ Generated: natal_with_tables.svg (natal chart with tables)")


if __name__ == "__main__":
    print("=" * 70)
    print("Comparison Chart Integration Test Suite")
    print("=" * 70)

    test_comparison_draw_method()
    test_preset_synastry_auto_config()
    test_with_tables_variations()
    test_custom_configuration()
    test_natal_chart_unchanged()

    print("\n" + "=" * 70)
    print("All integration tests completed!")
    print("=" * 70)
    print("\nKey features demonstrated:")
    print("  ✓ Comparison.draw() method")
    print("  ✓ ChartDrawBuilder.with_tables()")
    print("  ✓ preset_synastry() auto bi-wheel configuration")
    print("  ✓ Customizable table layouts and options")
    print("  ✓ Backward compatibility with natal charts")
    print("=" * 70)
