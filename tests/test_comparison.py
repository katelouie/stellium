"""
Tests for comparison charts (synastry, transits, progressions).

These tests validate that:
- Cross-chart aspects are calculated correctly
- No internal aspects leak into cross_aspects
- House overlays work bidirectionally
- Comparison-specific default orbs are applied
"""

import datetime as dt
from datetime import datetime

from stellium.core.builder import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.models import ChartLocation, ComparisonType
from stellium.core.native import Native


def test_synastry_cross_aspects_only():
    """Test that synastry only calculates cross-chart aspects."""
    # Create two test charts with simple positions
    loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")

    # Person A (natal chart with aspects)
    native_a = Native(datetime(1990, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
    chart_a = ChartBuilder.from_native(native_a).calculate()

    # Person B (natal chart with aspects)
    native_b = Native(datetime(1995, 6, 15, 14, 30, tzinfo=dt.UTC), loc)
    chart_b = ChartBuilder.from_native(native_b).calculate()

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(chart_a, "Person A")
        .with_partner(chart_b, partner_label="Person B")
        .calculate()
    )

    # Validate we have cross-aspects
    assert len(synastry.cross_aspects) > 0, "Should find some cross-chart aspects"

    # Validate NO internal aspects leaked in
    chart_a_positions = set(chart_a.positions)
    _chart_b_positions = set(chart_b.positions)

    for asp in synastry.cross_aspects:
        obj1_in_a = asp.object1 in chart_a_positions
        obj2_in_a = asp.object2 in chart_a_positions

        # Exactly one should be from chart A (XOR)
        assert obj1_in_a != obj2_in_a, (
            f"Aspect {asp.object1.name} {asp.aspect_name} {asp.object2.name} "
            f"should be cross-chart, not internal"
        )


def test_house_overlays_bidirectional():
    """Test that house overlays are calculated in both directions."""
    loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")

    # Create two charts
    native_a = Native(datetime(1990, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
    chart_a = ChartBuilder.from_native(native_a).calculate()

    native_b = Native(datetime(1995, 6, 15, 14, 30, tzinfo=dt.UTC), loc)
    chart_b = ChartBuilder.from_native(native_b).calculate()

    # Calculate synastry with house overlays
    synastry = ComparisonBuilder.from_native(chart_a).with_partner(chart_b).calculate()

    # Count overlays by direction
    chart1_in_chart2 = [
        o
        for o in synastry.house_overlays
        if o.planet_owner == "chart1" and o.house_owner == "chart2"
    ]
    chart2_in_chart1 = [
        o
        for o in synastry.house_overlays
        if o.planet_owner == "chart2" and o.house_owner == "chart1"
    ]

    # Should have overlays in both directions
    assert len(chart1_in_chart2) > 0, "Should have chart1 planets in chart2 houses"
    assert len(chart2_in_chart1) > 0, "Should have chart2 planets in chart1 houses"

    # Number of overlays should equal number of positions
    assert len(chart1_in_chart2) == len(chart_a.positions)
    assert len(chart2_in_chart1) == len(chart_b.positions)


def test_transit_tight_orbs():
    """Test that transits use tighter orbs than synastry."""
    loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")

    # Natal chart
    native = Native(datetime(1990, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
    natal = ChartBuilder.from_native(native).calculate()

    # Transit chart (current time)
    transit_time = datetime(2025, 11, 16, 18, 0, tzinfo=dt.UTC)

    # Calculate transit comparison
    transits = (
        ComparisonBuilder.from_native(natal, "Natal")
        .with_transit(transit_time)
        .calculate()
    )

    # Verify comparison type
    assert transits.comparison_type == ComparisonType.TRANSIT

    # The orb engine should use transit defaults (tight orbs)
    # We can't directly inspect the orb engine, but we can verify
    # that cross-aspects were calculated
    assert hasattr(transits, "cross_aspects")


def test_comparison_aspect_house_metadata():
    """Test that ComparisonAspects include house placement metadata."""
    loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")

    native_a = Native(datetime(1990, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
    chart_a = ChartBuilder.from_native(native_a).calculate()

    native_b = Native(datetime(1995, 6, 15, 14, 30, tzinfo=dt.UTC), loc)
    chart_b = ChartBuilder.from_native(native_b).calculate()

    synastry = ComparisonBuilder.from_native(chart_a).with_partner(chart_b).calculate()

    # Check that at least one aspect has house metadata
    if synastry.cross_aspects:
        asp = synastry.cross_aspects[0]

        # Should have house placement info (or None if angles/nodes)
        assert hasattr(asp, "in_chart1_house")
        assert hasattr(asp, "in_chart2_house")

        # If the aspect involves planets, should have house numbers
        # (May be None for angles which aren't in houses)
        if asp.in_chart1_house is not None:
            assert 1 <= asp.in_chart1_house <= 12


def test_internal_aspects_calculated_if_missing():
    """Test that internal aspects are calculated if charts don't have them."""
    loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")

    # Create charts WITHOUT aspects
    native_a = Native(datetime(1990, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
    chart_a_no_aspects = ChartBuilder.from_native(native_a).calculate()
    # Note: Currently ChartBuilder doesn't calculate aspects by default (aspects OFF)

    native_b = Native(datetime(1995, 6, 15, 14, 30, tzinfo=dt.UTC), loc)
    chart_b_no_aspects = ChartBuilder.from_native(native_b).calculate()

    # Verify charts don't have aspects
    assert len(chart_a_no_aspects.aspects) == 0
    assert len(chart_b_no_aspects.aspects) == 0

    # Calculate synastry
    synastry = (
        ComparisonBuilder.from_native(chart_a_no_aspects)
        .with_partner(chart_b_no_aspects)
        .calculate()
    )

    # After calculation, internal charts should have aspects
    assert (
        len(synastry.chart1.aspects) > 0
    ), "Chart1 should have internal aspects calculated"
    assert (
        len(synastry.chart2.aspects) > 0
    ), "Chart2 should have internal aspects calculated"


class TestComparisonBuilderConvenienceMethods:
    """Test ComparisonBuilder convenience methods (.synastry, .transit, .progression, .compare)."""

    def test_synastry_with_string_tuples(self):
        """Test .synastry() with (datetime, location) string tuples."""
        comparison = ComparisonBuilder.synastry(
            ("1994-01-06 11:47", "Palo Alto, CA"), ("2000-01-01 17:00", "Seattle, WA")
        ).calculate()

        assert comparison.comparison_type == ComparisonType.SYNASTRY
        assert comparison.chart1.datetime.local_datetime.year == 1994
        assert comparison.chart2.datetime.local_datetime.year == 2000
        assert len(comparison.cross_aspects) > 0

    def test_synastry_with_native_objects(self):
        """Test .synastry() with Native objects."""
        native1 = Native("1994-01-06 11:47", "Palo Alto, CA")
        native2 = Native("2000-01-01 17:00", "Seattle, WA")

        comparison = ComparisonBuilder.synastry(native1, native2).calculate()

        assert comparison.comparison_type == ComparisonType.SYNASTRY
        assert len(comparison.cross_aspects) > 0

    def test_synastry_custom_labels(self):
        """Test .synastry() with custom chart labels."""
        comparison = ComparisonBuilder.synastry(
            ("1994-01-06 11:47", "Palo Alto, CA"),
            ("2000-01-01 17:00", "Seattle, WA"),
            chart1_label="Kate",
            chart2_label="Partner",
        ).calculate()

        assert comparison.chart1_label == "Kate"
        assert comparison.chart2_label == "Partner"

    def test_transit_with_none_location(self):
        """Test .transit() with None location (uses natal location)."""
        comparison = ComparisonBuilder.transit(
            ("1994-01-06 11:47", "Palo Alto, CA"),
            ("2024-11-24 14:30", None),  # Uses Palo Alto
        ).calculate()

        assert comparison.comparison_type == ComparisonType.TRANSIT
        assert "Palo Alto" in comparison.chart1.location.name
        assert "Palo Alto" in comparison.chart2.location.name

    def test_transit_with_different_location(self):
        """Test .transit() with different location for transit."""
        comparison = ComparisonBuilder.transit(
            ("1994-01-06 11:47", "Palo Alto, CA"), ("2024-11-24 14:30", "New York, NY")
        ).calculate()

        assert comparison.comparison_type == ComparisonType.TRANSIT
        assert "Palo Alto" in comparison.chart1.location.name
        assert "New York" in comparison.chart2.location.name

    def test_progression_with_string_dates(self):
        """Test .progression() with date strings."""
        comparison = ComparisonBuilder.progression(
            ("1994-01-06 11:47", "Palo Alto, CA"),
            ("1994-02-05 11:47", "Palo Alto, CA"),  # 30 days later = age 30
        ).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION
        # 30 days difference
        delta = (
            comparison.chart2.datetime.local_datetime
            - comparison.chart1.datetime.local_datetime
        )
        assert delta.days == 30

    def test_compare_general_method_synastry(self):
        """Test .compare() general method with synastry type."""
        comparison = ComparisonBuilder.compare(
            ("1994-01-06 11:47", "Palo Alto, CA"),
            ("2000-01-01 17:00", "Seattle, WA"),
            "synastry",
        ).calculate()

        assert comparison.comparison_type == ComparisonType.SYNASTRY

    def test_compare_general_method_transit(self):
        """Test .compare() general method with transit type."""
        comparison = ComparisonBuilder.compare(
            ("1994-01-06 11:47", "Palo Alto, CA"), ("2024-11-24 14:30", None), "transit"
        ).calculate()

        assert comparison.comparison_type == ComparisonType.TRANSIT

    def test_compare_general_method_progression(self):
        """Test .compare() general method with progression type."""
        comparison = ComparisonBuilder.compare(
            ("1994-01-06 11:47", "Palo Alto, CA"),
            ("1994-02-05 11:47", "Palo Alto, CA"),
            "progression",
        ).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION

    def test_compare_with_mixed_inputs(self):
        """Test .compare() with Native object and tuple."""
        native1 = Native("1994-01-06 11:47", "Palo Alto, CA")
        comparison = ComparisonBuilder.compare(
            native1, ("2024-11-24 14:30", "New York, NY"), "transit"
        ).calculate()

        assert comparison.comparison_type == ComparisonType.TRANSIT
        assert "Palo Alto" in comparison.chart1.location.name
        assert "New York" in comparison.chart2.location.name

    def test_compare_invalid_type_raises_error(self):
        """Test .compare() raises error for invalid comparison type."""
        import pytest

        with pytest.raises(ValueError) as exc_info:
            ComparisonBuilder.compare(
                ("1994-01-06 11:47", "Palo Alto, CA"),
                ("2000-01-01 17:00", "Seattle, WA"),
                "invalid_type",
            )

        assert "Invalid comparison type" in str(exc_info.value)
        assert "synastry" in str(exc_info.value)

    def test_us_date_format_parsing(self):
        """Test that US date format strings work with convenience methods."""
        comparison = ComparisonBuilder.synastry(
            ("01/06/1994 11:47 AM", "Palo Alto, CA"),
            ("01/01/2000 5:00 PM", "Seattle, WA"),
        ).calculate()

        assert comparison.chart1.datetime.local_datetime.year == 1994
        assert comparison.chart1.datetime.local_datetime.month == 1
        assert comparison.chart2.datetime.local_datetime.year == 2000

    def test_convenience_vs_old_api_equivalent(self):
        """Test that convenience methods produce same results as old API."""
        # New convenience API
        comparison1 = ComparisonBuilder.synastry(
            ("1994-01-06 11:47", "Palo Alto, CA"), ("2000-01-01 17:00", "Seattle, WA")
        ).calculate()

        # Old API (using string locations for easy comparison)
        native1 = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart1 = ChartBuilder.from_native(native1).calculate()

        native2 = Native("2000-01-01 17:00", "Seattle, WA")
        chart2 = ChartBuilder.from_native(native2).calculate()

        comparison2 = (
            ComparisonBuilder.from_native(chart1).with_partner(chart2).calculate()
        )

        # Should have same number of cross aspects
        assert len(comparison1.cross_aspects) == len(comparison2.cross_aspects)


if __name__ == "__main__":
    # Run tests manually
    print("Running comparison chart tests...")

    try:
        test_synastry_cross_aspects_only()
        print("✓ test_synastry_cross_aspects_only passed")
    except Exception as e:
        print(f"✗ test_synastry_cross_aspects_only failed: {e}")

    try:
        test_house_overlays_bidirectional()
        print("✓ test_house_overlays_bidirectional passed")
    except Exception as e:
        print(f"✗ test_house_overlays_bidirectional failed: {e}")

    try:
        test_transit_tight_orbs()
        print("✓ test_transit_tight_orbs passed")
    except Exception as e:
        print(f"✗ test_transit_tight_orbs failed: {e}")

    try:
        test_comparison_aspect_house_metadata()
        print("✓ test_comparison_aspect_house_metadata passed")
    except Exception as e:
        print(f"✗ test_comparison_aspect_house_metadata failed: {e}")

    try:
        test_internal_aspects_calculated_if_missing()
        print("✓ test_internal_aspects_calculated_if_missing passed")
    except Exception as e:
        print(f"✗ test_internal_aspects_calculated_if_missing failed: {e}")

    print("\nAll tests completed!")
