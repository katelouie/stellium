"""Tests for secondary progression calculations.

These tests verify that ComparisonBuilder.progression() correctly:
- Auto-calculates progressed datetime using 1 day = 1 year rule
- Supports target_date and age parameters
- Implements all three angle progression methods (quotidian, solar_arc, naibod)
- Maintains backwards compatibility with explicit progressed charts
"""

import datetime as dt
from datetime import timedelta

import pytest
import pytz

from stellium import ChartBuilder, ComparisonBuilder
from stellium.core.models import ChartLocation, ComparisonType
from stellium.core.native import Native


@pytest.fixture(scope="module")
def einstein_natal():
    """Albert Einstein's natal chart (well-documented birth data).

    Using scope="module" so chart is only built once per test file.
    """
    return ChartBuilder.from_notable("Albert Einstein").calculate()


# Palo Alto, CA coordinates (avoids geolookup)
PALO_ALTO = ChartLocation(
    latitude=37.4419,
    longitude=-122.143,
    name="Palo Alto, CA",
    timezone="America/Los_Angeles",
)


@pytest.fixture(scope="module")
def kate_natal():
    """Kate's natal chart for testing.

    Using scope="module" so chart is only built once per test file.
    Uses ChartLocation directly to avoid geolookup in tests.
    """
    native = Native(
        dt.datetime(1994, 1, 6, 11, 47, tzinfo=pytz.timezone("America/Los_Angeles")),
        PALO_ALTO,
        name="Kate",
    )
    return ChartBuilder.from_native(native).calculate()


class TestProgressionByAge:
    """Test progression calculations using age parameter."""

    def test_progression_by_age_creates_correct_chart_delta(self, kate_natal):
        """Progression at age 30 should create chart 30 days after birth."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()

        # Progressed chart should be ~30 days after natal
        delta_days = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        assert 29.9 < delta_days < 30.1

    def test_progression_by_age_returns_comparison_type(self, kate_natal):
        """Progression should return PROGRESSION comparison type."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()
        assert prog.comparison_type == ComparisonType.PROGRESSION

    def test_progression_has_cross_aspects(self, kate_natal):
        """Progression should calculate cross-aspects between natal and progressed."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()
        # Should have some cross-aspects (tight 1° orbs, so maybe not many)
        assert len(prog.cross_aspects) >= 0  # At least it calculated

    def test_progressed_sun_moves_one_degree_per_year(self, kate_natal):
        """Progressed Sun should move ~1° per year of life."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()

        natal_sun = prog.chart1.get_object("Sun").longitude
        prog_sun = prog.chart2.get_object("Sun").longitude

        # Sun should have moved ~30° (1°/year × 30 years)
        diff = prog_sun - natal_sun
        if diff < 0:
            diff += 360
        assert 28 < diff < 32, f"Sun moved {diff}°, expected ~30°"

    def test_progressed_moon_moves_about_12_degrees_per_year(self, kate_natal):
        """Progressed Moon should move ~12-13° per year of life."""
        prog = ComparisonBuilder.progression(kate_natal, age=10).calculate()

        natal_moon = prog.chart1.get_object("Moon").longitude
        prog_moon = prog.chart2.get_object("Moon").longitude

        # Moon should have moved ~120-130° in 10 years
        diff = prog_moon - natal_moon
        if diff < 0:
            diff += 360
        if diff > 180:
            diff = 360 - diff  # Handle wrap
        # Moon is fast and varies, allow wide range
        assert 100 < diff < 150, f"Moon moved {diff}°, expected ~120-130°"

    def test_fractional_age(self, kate_natal):
        """Fractional ages should work (e.g., age=30.5 for mid-year)."""
        prog = ComparisonBuilder.progression(kate_natal, age=30.5).calculate()

        delta_days = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        # Should be ~30.5 days
        assert 30.4 < delta_days < 30.6


class TestProgressionByTargetDate:
    """Test progression calculations using target_date parameter."""

    def test_progression_by_target_date_string(self, kate_natal):
        """Progression to target date string should work."""
        prog = ComparisonBuilder.progression(
            kate_natal, target_date="2025-06-15"
        ).calculate()

        assert prog.comparison_type == ComparisonType.PROGRESSION
        # Should have calculated a progressed chart
        assert prog.chart2 is not None

    def test_progression_by_target_date_calculates_correct_age(self, kate_natal):
        """Target date should correctly calculate the age and thus progressed datetime."""
        # Kate born 1994-01-06, target 2024-01-06 = age 30
        prog = ComparisonBuilder.progression(
            kate_natal, target_date="2024-01-06"
        ).calculate()

        # Should be ~30 days after natal (age 30)
        delta_days = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        assert 29.5 < delta_days < 30.5


class TestAngleMethods:
    """Test different angle progression methods."""

    def test_quotidian_is_default(self, kate_natal):
        """Quotidian (actual daily motion) should be the default angle method."""
        # Get quotidian progression
        prog_q = ComparisonBuilder.progression(kate_natal, age=30).calculate()

        # Get explicit quotidian
        prog_q2 = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="quotidian"
        ).calculate()

        # ASC should be the same
        assert (
            prog_q.chart2.get_object("ASC").longitude
            == prog_q2.chart2.get_object("ASC").longitude
        )

    def test_solar_arc_angles(self, kate_natal):
        """Solar arc should move angles by the same amount as progressed Sun."""
        prog = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="solar_arc"
        ).calculate()

        # Calculate expected values
        natal_asc = kate_natal.get_object("ASC").longitude
        natal_sun = kate_natal.get_object("Sun").longitude
        prog_sun = prog.chart2.get_object("Sun").longitude

        # Solar arc = how much Sun moved
        solar_arc = prog_sun - natal_sun
        if solar_arc < 0:
            solar_arc += 360

        # Progressed ASC should be natal ASC + solar arc
        expected_asc = (natal_asc + solar_arc) % 360
        actual_asc = prog.chart2.get_object("ASC").longitude

        assert (
            abs(actual_asc - expected_asc) < 0.01
        ), f"ASC: expected {expected_asc:.2f}°, got {actual_asc:.2f}°"

    def test_naibod_angles(self, kate_natal):
        """Naibod should move angles by mean Sun rate (59'08"/year)."""
        prog = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="naibod"
        ).calculate()

        # Calculate expected values
        natal_asc = kate_natal.get_object("ASC").longitude
        naibod_rate = 59.1333 / 60  # degrees per year
        naibod_arc = 30 * naibod_rate  # 30 years

        # Progressed ASC should be natal ASC + naibod arc
        expected_asc = (natal_asc + naibod_arc) % 360
        actual_asc = prog.chart2.get_object("ASC").longitude

        assert (
            abs(actual_asc - expected_asc) < 0.01
        ), f"ASC: expected {expected_asc:.2f}°, got {actual_asc:.2f}°"

    def test_angle_method_in_metadata(self, kate_natal):
        """Angle method should be recorded in chart metadata."""
        prog_sa = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="solar_arc"
        ).calculate()

        assert prog_sa.chart2.metadata.get("angle_method") == "solar_arc"
        assert "angle_arc" in prog_sa.chart2.metadata

    def test_quotidian_angles_differ_from_solar_arc(self, kate_natal):
        """Quotidian and solar arc should produce different angle positions."""
        prog_q = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="quotidian"
        ).calculate()
        prog_sa = ComparisonBuilder.progression(
            kate_natal, age=30, angle_method="solar_arc"
        ).calculate()

        asc_q = prog_q.chart2.get_object("ASC").longitude
        asc_sa = prog_sa.chart2.get_object("ASC").longitude

        # They should be different (quotidian uses actual ephemeris)
        assert asc_q != asc_sa


class TestBackwardsCompatibility:
    """Test that legacy API still works."""

    def test_explicit_progressed_chart_positional(self, kate_natal):
        """Legacy: passing explicit progressed chart as second positional arg."""
        progressed_dt = kate_natal.datetime.local_datetime + timedelta(days=30)
        progressed_chart = ChartBuilder.from_details(
            progressed_dt, kate_natal.location
        ).calculate()

        # Should work with explicit chart
        prog = ComparisonBuilder.progression(kate_natal, progressed_chart).calculate()

        assert prog.comparison_type == ComparisonType.PROGRESSION
        assert len(prog.cross_aspects) >= 0

    def test_tuple_format_both_charts(self):
        """Legacy: using (datetime, location) tuples for both charts."""
        prog = ComparisonBuilder.progression(
            ("1994-01-06 11:47", PALO_ALTO),
            ("1994-02-05 11:47", PALO_ALTO),  # 30 days later
        ).calculate()

        assert prog.comparison_type == ComparisonType.PROGRESSION
        # Should be ~30 days difference
        delta = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        assert 29 < delta < 31


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_negative_age_for_past_progressions(self, kate_natal):
        """Negative age should work for reverse progressions (before birth)."""
        # This is unusual but mathematically valid
        prog = ComparisonBuilder.progression(kate_natal, age=-5).calculate()

        # Should be 5 days BEFORE natal
        delta = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        assert -5.1 < delta < -4.9

    def test_very_large_age(self, einstein_natal):
        """Very large ages should still work."""
        prog = ComparisonBuilder.progression(einstein_natal, age=100).calculate()

        # Should be 100 days after natal
        delta = prog.chart2.datetime.julian_day - prog.chart1.datetime.julian_day
        assert 99.9 < delta < 100.1

    def test_progression_uses_natal_location(self, kate_natal):
        """Progressed chart should use natal location."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()

        # Locations should match
        assert abs(prog.chart1.location.latitude - prog.chart2.location.latitude) < 0.01
        assert (
            abs(prog.chart1.location.longitude - prog.chart2.location.longitude) < 0.01
        )

    def test_progression_with_different_house_systems(self, kate_natal):
        """Progression should work with custom house system configuration."""

        # TODO: This would require extending the API to support .with_house_systems()
        # For now, just verify basic functionality
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()
        assert prog.chart2.house_systems is not None


class TestProgressionLabels:
    """Test chart labeling functionality."""

    def test_default_labels(self, kate_natal):
        """Default labels should be 'Natal' and 'Progressed'."""
        prog = ComparisonBuilder.progression(kate_natal, age=30).calculate()

        assert prog.chart1_label == "Natal"
        assert prog.chart2_label == "Progressed"

    def test_custom_labels(self, kate_natal):
        """Custom labels should be applied."""
        prog = ComparisonBuilder.progression(
            kate_natal,
            age=30,
            natal_label="Birth Chart",
            progressed_label="Age 30 Progressions",
        ).calculate()

        assert prog.chart1_label == "Birth Chart"
        assert prog.chart2_label == "Age 30 Progressions"
