"""Tests for tertiary and minor progression types."""

from datetime import datetime, timedelta

import pytest

from stellium.utils.progressions import (
    LUNAR_MONTH_DAYS,
    calculate_progressed_datetime,
)

pytestmark = pytest.mark.slow


# ─── Utility function tests (fast, no ephemeris) ────────────────────────


class TestProgressedDatetimeCalculation:
    """Test the core time-key conversion for all progression types."""

    natal = datetime(1994, 1, 6, 11, 47)
    target_30 = datetime(2024, 1, 6, 11, 47)  # 30 years later

    def test_secondary_day_for_year(self):
        """Secondary: 30 years → ~30 progressed days."""
        result = calculate_progressed_datetime(self.natal, self.target_30, "secondary")
        delta = (result - self.natal).total_seconds() / 86400
        assert 29.9 < delta < 30.1  # ~30 days

    def test_tertiary_day_for_lunar_month(self):
        """Tertiary: 30 years → ~401 progressed days."""
        result = calculate_progressed_datetime(self.natal, self.target_30, "tertiary")
        delta = (result - self.natal).total_seconds() / 86400
        # 30 years × 365.25 days/year ÷ 27.32 days/lunar_month ≈ 401 days
        expected = (30 * 365.25) / LUNAR_MONTH_DAYS
        assert abs(delta - expected) < 1.0

    def test_minor_lunar_month_for_year(self):
        """Minor: 30 years → ~820 progressed days."""
        result = calculate_progressed_datetime(self.natal, self.target_30, "minor")
        delta = (result - self.natal).total_seconds() / 86400
        # 30 years × 27.32 days/lunar_month ≈ 820 days
        expected = 30 * LUNAR_MONTH_DAYS
        assert abs(delta - expected) < 1.0

    def test_tertiary_faster_than_secondary(self):
        """Tertiary should produce more progressed days than secondary."""
        sec = calculate_progressed_datetime(self.natal, self.target_30, "secondary")
        ter = calculate_progressed_datetime(self.natal, self.target_30, "tertiary")
        assert ter > sec

    def test_minor_faster_than_secondary(self):
        """Minor should produce more progressed days than secondary."""
        sec = calculate_progressed_datetime(self.natal, self.target_30, "secondary")
        minor = calculate_progressed_datetime(self.natal, self.target_30, "minor")
        assert minor > sec

    def test_minor_faster_than_tertiary(self):
        """Minor should produce more progressed days than tertiary."""
        ter = calculate_progressed_datetime(self.natal, self.target_30, "tertiary")
        minor = calculate_progressed_datetime(self.natal, self.target_30, "minor")
        assert minor > ter

    def test_secondary_is_default(self):
        """No progression_type arg should give secondary behavior."""
        default = calculate_progressed_datetime(self.natal, self.target_30)
        explicit = calculate_progressed_datetime(
            self.natal, self.target_30, "secondary"
        )
        assert default == explicit

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Unknown progression_type"):
            calculate_progressed_datetime(self.natal, self.target_30, "converse")

    def test_short_period_tertiary(self):
        """Tertiary over 3 months should produce ~3 progressed days."""
        target_3mo = self.natal + timedelta(days=90)
        result = calculate_progressed_datetime(self.natal, target_3mo, "tertiary")
        delta = (result - self.natal).total_seconds() / 86400
        # 90 days ÷ 27.32 ≈ 3.3 days
        assert 3.0 < delta < 3.6


# ─── Integration tests with chart calculation ────────────────────────────


class TestProgressionTypeIntegration:
    """Test progression types through MultiChartBuilder."""

    @pytest.fixture(scope="class")
    def natal(self):
        from stellium import ChartBuilder

        return ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    def test_tertiary_via_builder(self, natal):
        from stellium import MultiChartBuilder

        prog = MultiChartBuilder.progression(
            natal, age=30, progression_type="tertiary"
        ).calculate()
        assert prog.chart2 is not None
        assert prog.chart2.metadata.get("name") == "Albert Einstein - Tertiary"

    def test_minor_via_builder(self, natal):
        from stellium import MultiChartBuilder

        prog = MultiChartBuilder.progression(
            natal, age=30, progression_type="minor"
        ).calculate()
        assert prog.chart2 is not None
        assert prog.chart2.metadata.get("name") == "Albert Einstein - Minor"

    def test_secondary_default_unchanged(self, natal):
        """Existing behavior unchanged — no progression_type = secondary."""
        from stellium import MultiChartBuilder

        prog = MultiChartBuilder.progression(natal, age=30).calculate()
        assert prog.chart2.metadata.get("name") == "Albert Einstein - Progressed"

    def test_all_types_produce_different_charts(self, natal):
        """Each type should give a different progressed Sun position."""
        from stellium import MultiChartBuilder

        types = ["secondary", "tertiary", "minor"]
        sun_lons = []
        for ptype in types:
            prog = MultiChartBuilder.progression(
                natal, age=30, progression_type=ptype
            ).calculate()
            sun_lons.append(prog.chart2.get_object("Sun").longitude)

        # All three should be different
        assert len({round(lon, 2) for lon in sun_lons}) == 3

    def test_tertiary_with_angle_method(self, natal):
        """Tertiary should work with solar_arc angle method."""
        from stellium import MultiChartBuilder

        prog = MultiChartBuilder.progression(
            natal,
            age=30,
            progression_type="tertiary",
            angle_method="solar_arc",
        ).calculate()
        assert prog.chart2.metadata.get("angle_method") == "solar_arc"
        assert prog.chart2.metadata.get("progression_type") == "tertiary"

    def test_add_progression_with_type(self, natal):
        """add_progression() should pass through progression_type."""
        from stellium import MultiChartBuilder

        mc = (
            MultiChartBuilder.from_chart(natal, "Natal")
            .add_progression(age=30, progression_type="tertiary", label="Tertiary")
            .calculate()
        )
        assert mc.chart2.metadata.get("name") == "Albert Einstein - Tertiary"
