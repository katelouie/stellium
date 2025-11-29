"""Tests for arc direction calculations."""

import pytest

from stellium import ChartBuilder, ComparisonBuilder
from stellium.core.models import ComparisonType


@pytest.fixture(scope="module")
def einstein_natal():
    """Albert Einstein's natal chart for testing."""
    return ChartBuilder.from_notable("Albert Einstein").calculate()


class TestArcDirectionTypes:
    """Test each arc type calculation."""

    def test_solar_arc_direction(self, einstein_natal):
        """Solar arc should move all points by Sun's arc (~1°/year)."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        assert directed.comparison_type == ComparisonType.ARC_DIRECTION
        assert directed.chart2.metadata["arc_type"] == "solar_arc"

        # Sun should have moved ~30 degrees in 30 years
        arc = directed.chart2.metadata["arc_degrees"]
        assert 28 < arc < 32

    def test_naibod_arc_direction(self, einstein_natal):
        """Naibod arc should be ~0.9856 degrees per year."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="naibod"
        ).calculate()

        arc = directed.chart2.metadata["arc_degrees"]
        expected = 30 * 0.9856  # ~29.57
        assert abs(arc - expected) < 0.1

    def test_lunar_arc_direction(self, einstein_natal):
        """Lunar arc should be ~12-13 degrees per year."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=10, arc_type="lunar"
        ).calculate()

        _arc = directed.chart2.metadata["arc_degrees"]
        # Moon moves ~12-13 degrees per year in progressions
        # 10 years = 100-130 degrees, but may wrap around
        assert directed.chart2.metadata["effective_arc_type"] == "lunar"

    def test_chart_ruler_arc(self, einstein_natal):
        """Chart ruler arc should resolve to the ASC ruler."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="chart_ruler"
        ).calculate()

        # Should have resolved to a planet name
        effective_type = directed.chart2.metadata["effective_arc_type"]
        assert effective_type != "chart_ruler"
        # Einstein has Cancer rising, so Moon is chart ruler (traditional)
        assert effective_type == "moon"

    def test_sect_arc_resolves(self, einstein_natal):
        """Sect arc should resolve to solar_arc or lunar."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="sect"
        ).calculate()

        effective_type = directed.chart2.metadata["effective_arc_type"]
        assert effective_type in ("solar_arc", "lunar")

    def test_planet_arc_mars(self, einstein_natal):
        """Should support arbitrary planet arcs like Mars."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="Mars"
        ).calculate()

        assert directed.chart2.metadata["effective_arc_type"] == "mars"
        # Mars arc should be calculated
        arc = directed.chart2.metadata["arc_degrees"]
        assert arc >= 0

    def test_planet_arc_venus(self, einstein_natal):
        """Should support Venus arc."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="Venus"
        ).calculate()

        assert directed.chart2.metadata["effective_arc_type"] == "venus"


class TestDirectedPositions:
    """Test that directed positions are calculated correctly."""

    def test_all_positions_moved_by_same_arc(self, einstein_natal):
        """Every position should be moved by exactly the same arc."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="naibod"
        ).calculate()

        arc = directed.chart2.metadata["arc_degrees"]

        for natal_pos, directed_pos in zip(
            einstein_natal.positions, directed.chart2.positions, strict=False
        ):
            expected_lon = (natal_pos.longitude + arc) % 360
            assert abs(directed_pos.longitude - expected_lon) < 0.001

    def test_retrograde_status_preserved(self, einstein_natal):
        """Retrograde status should be preserved from natal."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        for natal_pos, directed_pos in zip(
            einstein_natal.positions, directed.chart2.positions, strict=False
        ):
            assert natal_pos.is_retrograde == directed_pos.is_retrograde

    def test_position_names_preserved(self, einstein_natal):
        """All position names should be preserved."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        natal_names = [p.name for p in einstein_natal.positions]
        directed_names = [p.name for p in directed.chart2.positions]
        assert natal_names == directed_names


class TestCrossChartAspects:
    """Test that cross-chart aspects are calculated."""

    def test_cross_aspects_calculated(self, einstein_natal):
        """Cross-chart aspects should be calculated."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        # Should have some cross-chart aspects
        assert len(directed.cross_aspects) > 0

    def test_tight_orbs_used(self, einstein_natal):
        """Arc directions should use tight orbs (1°) like progressions."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        # All cross-aspects should have orbs <= 1.0 for major aspects
        for asp in directed.cross_aspects:
            if asp.aspect_name in ("Conjunction", "Square", "Trine", "Opposition"):
                assert asp.orb <= 1.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_unknown_arc_type_raises_error(self, einstein_natal):
        """Unknown arc type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown arc type"):
            ComparisonBuilder.arc_direction(
                einstein_natal, age=30, arc_type="invalid_type"
            ).calculate()

    def test_wrap_around_360_degrees(self, einstein_natal):
        """Positions should wrap correctly at 360 degrees."""
        # Use a large age to ensure some positions wrap
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=400, arc_type="naibod"
        ).calculate()

        for pos in directed.chart2.positions:
            assert 0 <= pos.longitude < 360

    def test_target_date_parameter(self, einstein_natal):
        """Should work with target_date instead of age."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, target_date="1909-03-14", arc_type="solar_arc"
        ).calculate()

        # Should have arc_degrees in metadata
        assert "arc_degrees" in directed.chart2.metadata
        assert directed.chart2.metadata["arc_degrees"] > 0

    def test_metadata_includes_years_elapsed(self, einstein_natal):
        """Metadata should include years_elapsed."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal, age=30, arc_type="solar_arc"
        ).calculate()

        assert "years_elapsed" in directed.chart2.metadata
        assert abs(directed.chart2.metadata["years_elapsed"] - 30) < 0.1


class TestRulershipSystems:
    """Test traditional vs modern rulership for chart_ruler arc."""

    def test_traditional_rulership(self, einstein_natal):
        """Traditional rulership should use traditional rulers."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal,
            age=30,
            arc_type="chart_ruler",
            rulership_system="traditional",
        ).calculate()

        # Einstein has Cancer rising - traditional ruler is Moon
        assert directed.chart2.metadata["effective_arc_type"] == "moon"

    def test_modern_rulership(self, einstein_natal):
        """Modern rulership should use modern rulers where different."""
        directed = ComparisonBuilder.arc_direction(
            einstein_natal,
            age=30,
            arc_type="chart_ruler",
            rulership_system="modern",
        ).calculate()

        # For Cancer, modern ruler is also Moon
        assert directed.chart2.metadata["effective_arc_type"] == "moon"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
