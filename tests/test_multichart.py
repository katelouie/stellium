"""
Tests for MultiChart and MultiChartBuilder.

Tests the unified multi-chart architecture that combines features from
Comparison and MultiWheel into a single class.
"""

import pytest

from stellium import ChartBuilder
from stellium.core.models import (
    Aspect,
    ComparisonType,
)
from stellium.core.multichart import MultiChart, MultiChartBuilder

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def natal_chart():
    """A natal chart for testing.
    Uses tuple coordinates to avoid geocoding in CI/CD.
    """
    return ChartBuilder.from_details(
        "1994-01-06 11:47",
        (37.4419, -122.1430),  # Palo Alto, CA
        name="Test Native",
    ).calculate()


@pytest.fixture(scope="module")
def partner_chart():
    """A partner chart for synastry testing.
    Uses tuple coordinates to avoid geocoding in CI/CD.
    """
    return ChartBuilder.from_details(
        "2000-01-01 17:00",
        (47.6062, -122.3321),  # Seattle, WA
        name="Test Partner",
    ).calculate()


@pytest.fixture(scope="module")
def transit_chart():
    """A transit chart for testing.
    Uses tuple coordinates to avoid geocoding in CI/CD.
    """
    return ChartBuilder.from_details(
        "2025-06-15 12:00",
        (37.4419, -122.1430),  # Palo Alto, CA
        name="Transit",
    ).calculate()


@pytest.fixture(scope="module")
def third_chart():
    """A third chart for triwheel testing.
    Uses tuple coordinates to avoid geocoding in CI/CD.
    """
    return ChartBuilder.from_details(
        "2020-03-20 12:00",
        (37.4419, -122.1430),  # Palo Alto, CA
        name="Third Chart",
    ).calculate()


@pytest.fixture(scope="module")
def fourth_chart():
    """A fourth chart for quadwheel testing.
    Uses tuple coordinates to avoid geocoding in CI/CD.
    """
    return ChartBuilder.from_details(
        "2010-06-21 12:00",
        (37.4419, -122.1430),  # Palo Alto, CA
        name="Fourth Chart",
    ).calculate()


# =============================================================================
# MultiChart Dataclass Tests
# =============================================================================


class TestMultiChartDataclass:
    """Tests for the MultiChart dataclass."""

    def test_basic_creation(self, natal_chart, partner_chart):
        """Test basic MultiChart creation with two charts."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        assert mc.chart_count == 2
        assert mc.chart1 is natal_chart
        assert mc.chart2 is partner_chart
        assert mc.chart3 is None
        assert mc.chart4 is None

    def test_auto_generated_labels(self, natal_chart, partner_chart):
        """Test that labels are auto-generated if not provided."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        assert mc.labels == ("Chart 1", "Chart 2")

    def test_custom_labels(self, natal_chart, partner_chart):
        """Test custom labels."""
        mc = MultiChart(
            charts=(natal_chart, partner_chart),
            labels=("Kate", "Partner"),
        )

        assert mc.labels == ("Kate", "Partner")

    def test_too_few_charts_raises(self, natal_chart):
        """Test that fewer than 2 charts raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 charts"):
            MultiChart(charts=(natal_chart,))

    def test_too_many_charts_raises(
        self, natal_chart, partner_chart, transit_chart, third_chart, fourth_chart
    ):
        """Test that more than 4 charts raises ValueError."""
        with pytest.raises(ValueError, match="at most 4 charts"):
            MultiChart(
                charts=(
                    natal_chart,
                    partner_chart,
                    transit_chart,
                    third_chart,
                    fourth_chart,
                )
            )

    def test_triwheel_creation(self, natal_chart, partner_chart, transit_chart):
        """Test triwheel (3 chart) creation."""
        mc = MultiChart(charts=(natal_chart, partner_chart, transit_chart))

        assert mc.chart_count == 3
        assert mc.chart1 is natal_chart
        assert mc.chart2 is partner_chart
        assert mc.chart3 is transit_chart
        assert mc.chart4 is None

    def test_quadwheel_creation(
        self, natal_chart, partner_chart, transit_chart, third_chart
    ):
        """Test quadwheel (4 chart) creation."""
        mc = MultiChart(charts=(natal_chart, partner_chart, transit_chart, third_chart))

        assert mc.chart_count == 4
        assert mc.chart1 is natal_chart
        assert mc.chart2 is partner_chart
        assert mc.chart3 is transit_chart
        assert mc.chart4 is third_chart

    def test_frozen_dataclass(self, natal_chart, partner_chart):
        """Test that MultiChart is immutable."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        with pytest.raises(AttributeError):
            mc.charts = (partner_chart, natal_chart)


class TestMultiChartIndexedAccess:
    """Tests for indexed access to charts."""

    def test_getitem(self, natal_chart, partner_chart, transit_chart):
        """Test __getitem__ access."""
        mc = MultiChart(charts=(natal_chart, partner_chart, transit_chart))

        assert mc[0] is natal_chart
        assert mc[1] is partner_chart
        assert mc[2] is transit_chart

    def test_len(self, natal_chart, partner_chart, transit_chart):
        """Test __len__ returns chart count."""
        mc = MultiChart(charts=(natal_chart, partner_chart, transit_chart))

        assert len(mc) == 3


class TestMultiChartSemanticAliases:
    """Tests for semantic property aliases."""

    def test_inner_outer(self, natal_chart, partner_chart, transit_chart):
        """Test .inner and .outer aliases."""
        mc = MultiChart(charts=(natal_chart, partner_chart, transit_chart))

        assert mc.inner is natal_chart  # Always first
        assert mc.outer is transit_chart  # Always last

    def test_natal_alias(self, natal_chart, partner_chart):
        """Test .natal alias."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        assert mc.natal is natal_chart


class TestMultiChartQueryMethods:
    """Tests for query methods."""

    def test_get_object(self, natal_chart, partner_chart):
        """Test getting an object from a specific chart."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        sun_chart1 = mc.get_object("Sun", chart=0)
        sun_chart2 = mc.get_object("Sun", chart=1)

        assert sun_chart1 is not None
        assert sun_chart2 is not None
        assert sun_chart1.name == "Sun"
        assert sun_chart2.name == "Sun"
        # Different charts, potentially different positions
        assert sun_chart1 is natal_chart.get_object("Sun")
        assert sun_chart2 is partner_chart.get_object("Sun")

    def test_get_planets(self, natal_chart, partner_chart):
        """Test getting planets from a specific chart."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        planets = mc.get_planets(chart=0)

        assert len(planets) == 10  # Standard planets
        assert all(
            p.name
            in [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
            ]
            for p in planets
        )

    def test_get_angles(self, natal_chart, partner_chart):
        """Test getting angles from a specific chart."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        angles = mc.get_angles(chart=0)

        assert len(angles) >= 2  # At least ASC and MC


class TestMultiChartCrossAspects:
    """Tests for cross-aspect functionality."""

    def test_get_cross_aspects_default(self, natal_chart, partner_chart):
        """Test getting cross-aspects for default pair (0, 1)."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart])
            .with_cross_aspects("all")
            .calculate()
        )

        aspects = mc.get_cross_aspects()

        assert isinstance(aspects, tuple)
        assert len(aspects) > 0
        assert all(isinstance(a, Aspect) for a in aspects)

    def test_get_cross_aspects_specific_pair(
        self, natal_chart, partner_chart, transit_chart
    ):
        """Test getting cross-aspects for a specific pair."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart, transit_chart])
            .with_cross_aspects("all")
            .calculate()
        )

        aspects_0_1 = mc.get_cross_aspects(0, 1)
        aspects_0_2 = mc.get_cross_aspects(0, 2)

        assert isinstance(aspects_0_1, tuple)
        assert isinstance(aspects_0_2, tuple)

    def test_get_all_cross_aspects(self, natal_chart, partner_chart, transit_chart):
        """Test getting all cross-aspects flattened."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart, transit_chart])
            .with_cross_aspects("all")
            .calculate()
        )

        all_aspects = mc.get_all_cross_aspects()

        assert isinstance(all_aspects, list)


class TestMultiChartRelationships:
    """Tests for relationship type functionality."""

    def test_get_relationship(self, natal_chart, partner_chart):
        """Test getting relationship type for a pair."""
        mc = MultiChart(
            charts=(natal_chart, partner_chart),
            relationships={(0, 1): ComparisonType.SYNASTRY},
        )

        assert mc.get_relationship(0, 1) == ComparisonType.SYNASTRY
        assert mc.get_relationship(1, 0) == ComparisonType.SYNASTRY  # Order normalized

    def test_get_relationship_undefined(self, natal_chart, partner_chart):
        """Test getting undefined relationship returns None."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        assert mc.get_relationship(0, 1) is None


class TestMultiChartCompatibilityScore:
    """Tests for compatibility scoring."""

    def test_calculate_compatibility_score(self, natal_chart, partner_chart):
        """Test basic compatibility score calculation."""
        mc = MultiChartBuilder.synastry(natal_chart, partner_chart).calculate()

        score = mc.calculate_compatibility_score()

        assert 0.0 <= score <= 100.0

    def test_compatibility_score_with_custom_weights(self, natal_chart, partner_chart):
        """Test compatibility score with custom weights."""
        mc = MultiChartBuilder.synastry(natal_chart, partner_chart).calculate()

        custom_weights = {
            "Conjunction": 1.0,
            "Trine": 1.5,
            "Sextile": 1.0,
            "Square": -1.0,
            "Opposition": -0.5,
        }

        score = mc.calculate_compatibility_score(weights=custom_weights)

        assert 0.0 <= score <= 100.0


class TestMultiChartSerialization:
    """Tests for serialization."""

    def test_to_dict(self, natal_chart, partner_chart):
        """Test to_dict serialization."""
        mc = MultiChartBuilder.synastry(
            natal_chart, partner_chart, label1="Kate", label2="Partner"
        ).calculate()

        data = mc.to_dict()

        assert data["chart_count"] == 2
        assert data["labels"] == ["Kate", "Partner"]
        assert "charts" in data
        assert len(data["charts"]) == 2
        assert "relationships" in data
        assert "cross_aspects" in data


class TestMultiChartVisualization:
    """Tests for visualization integration."""

    def test_draw_returns_builder(self, natal_chart, partner_chart):
        """Test that .draw() returns a ChartDrawBuilder."""
        mc = MultiChart(charts=(natal_chart, partner_chart))

        builder = mc.draw("test.svg")

        assert builder is not None
        # ChartDrawBuilder should have common methods
        assert hasattr(builder, "with_filename")


# =============================================================================
# MultiChartBuilder Tests
# =============================================================================


class TestMultiChartBuilderFromCharts:
    """Tests for from_charts constructor."""

    def test_from_charts_biwheel(self, natal_chart, partner_chart):
        """Test creating biwheel from charts."""
        mc = MultiChartBuilder.from_charts([natal_chart, partner_chart]).calculate()

        assert mc.chart_count == 2
        # Charts may be recreated if aspects need calculation, so compare data not identity
        assert mc.chart1.datetime == natal_chart.datetime
        assert mc.chart2.datetime == partner_chart.datetime

    def test_from_charts_with_labels(self, natal_chart, partner_chart):
        """Test from_charts with custom labels."""
        mc = MultiChartBuilder.from_charts(
            [natal_chart, partner_chart], labels=["Kate", "Partner"]
        ).calculate()

        assert mc.labels == ("Kate", "Partner")

    def test_from_charts_too_few_raises(self, natal_chart):
        """Test that fewer than 2 charts raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 charts"):
            MultiChartBuilder.from_charts([natal_chart])

    def test_from_charts_too_many_raises(
        self, natal_chart, partner_chart, transit_chart, third_chart, fourth_chart
    ):
        """Test that more than 4 charts raises ValueError."""
        with pytest.raises(ValueError, match="at most 4 charts"):
            MultiChartBuilder.from_charts(
                [natal_chart, partner_chart, transit_chart, third_chart, fourth_chart]
            )


class TestMultiChartBuilderFromChart:
    """Tests for from_chart constructor."""

    def test_from_chart_and_add_chart(self, natal_chart, partner_chart):
        """Test building from a single chart then adding another."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_chart(partner_chart, "Partner")
            .calculate()
        )

        assert mc.chart_count == 2
        assert mc.labels == ("Natal", "Partner")


class TestMultiChartBuilderSynastry:
    """Tests for synastry constructor."""

    def test_synastry_with_charts(self, natal_chart, partner_chart):
        """Test synastry with CalculatedChart objects."""
        mc = MultiChartBuilder.synastry(
            natal_chart, partner_chart, label1="Kate", label2="Partner"
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.SYNASTRY
        assert mc.labels == ("Kate", "Partner")

    def test_synastry_with_tuples(self):
        """Test synastry with (datetime, location) tuples."""
        mc = MultiChartBuilder.synastry(
            ("1994-01-06 11:47", (37.4419, -122.1430)),
            ("2000-01-01 17:00", (47.6062, -122.3321)),
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.SYNASTRY


class TestMultiChartBuilderTransit:
    """Tests for transit constructor."""

    def test_transit_with_charts(self, natal_chart, transit_chart):
        """Test transit with CalculatedChart objects."""
        mc = MultiChartBuilder.transit(natal_chart, transit_chart).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.TRANSIT

    def test_transit_with_datetime_tuple(self, natal_chart):
        """Test transit with datetime tuple (uses natal location)."""
        mc = MultiChartBuilder.transit(
            natal_chart,
            ("2025-06-15 12:00", None),  # None = use natal location
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.TRANSIT


class TestMultiChartBuilderProgression:
    """Tests for progression constructor."""

    def test_progression_by_age(self, natal_chart):
        """Test progression calculation by age."""
        mc = MultiChartBuilder.progression(natal_chart, age=30).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.PROGRESSION

    def test_progression_by_target_date(self, natal_chart):
        """Test progression calculation by target date."""
        mc = MultiChartBuilder.progression(
            natal_chart, target_date="2024-06-15"
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.PROGRESSION


class TestMultiChartBuilderArcDirection:
    """Tests for arc direction constructor."""

    def test_arc_direction_solar_arc(self, natal_chart):
        """Test solar arc direction."""
        mc = MultiChartBuilder.arc_direction(
            natal_chart, age=30, arc_type="solar_arc"
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.ARC_DIRECTION

    def test_arc_direction_naibod(self, natal_chart):
        """Test naibod arc direction."""
        mc = MultiChartBuilder.arc_direction(
            natal_chart, age=30, arc_type="naibod"
        ).calculate()

        assert mc.chart_count == 2
        assert mc.get_relationship(0, 1) == ComparisonType.ARC_DIRECTION


class TestMultiChartBuilderAddMethods:
    """Tests for add_* methods."""

    def test_add_transit(self, natal_chart):
        """Test add_transit method."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_transit("2025-06-15 12:00", label="Transit")
            .calculate()
        )

        assert mc.chart_count == 2
        assert mc.labels == ("Natal", "Transit")
        assert mc.get_relationship(0, 1) == ComparisonType.TRANSIT

    def test_add_progression(self, natal_chart):
        """Test add_progression method."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_progression(age=30, label="Progressed")
            .calculate()
        )

        assert mc.chart_count == 2
        assert mc.labels == ("Natal", "Progressed")
        assert mc.get_relationship(0, 1) == ComparisonType.PROGRESSION

    def test_add_arc_direction(self, natal_chart):
        """Test add_arc_direction method."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_arc_direction(age=30, label="Directed")
            .calculate()
        )

        assert mc.chart_count == 2
        assert mc.labels == ("Natal", "Directed")
        assert mc.get_relationship(0, 1) == ComparisonType.ARC_DIRECTION

    def test_build_triwheel(self, natal_chart):
        """Test building a triwheel with add methods."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_progression(age=30, label="Progressed")
            .add_transit("2025-06-15 12:00", label="Transit")
            .calculate()
        )

        assert mc.chart_count == 3
        assert mc.labels == ("Natal", "Progressed", "Transit")


class TestMultiChartBuilderCrossAspects:
    """Tests for cross-aspect configuration."""

    def test_with_cross_aspects_to_primary(
        self, natal_chart, partner_chart, transit_chart
    ):
        """Test 'to_primary' cross-aspect calculation."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart, transit_chart])
            .with_cross_aspects("to_primary")
            .calculate()
        )

        # Should have aspects for (0,1) and (0,2), but not (1,2)
        assert (0, 1) in mc.cross_aspects
        assert (0, 2) in mc.cross_aspects
        assert (1, 2) not in mc.cross_aspects

    def test_with_cross_aspects_all(self, natal_chart, partner_chart, transit_chart):
        """Test 'all' cross-aspect calculation."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart, transit_chart])
            .with_cross_aspects("all")
            .calculate()
        )

        # Should have aspects for all pairs
        assert (0, 1) in mc.cross_aspects
        assert (0, 2) in mc.cross_aspects
        assert (1, 2) in mc.cross_aspects

    def test_with_cross_aspects_explicit_pairs(
        self, natal_chart, partner_chart, transit_chart
    ):
        """Test explicit pairs cross-aspect calculation."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart, transit_chart])
            .with_cross_aspects([(0, 1)])
            .calculate()
        )

        # Should only have aspects for (0,1)
        assert (0, 1) in mc.cross_aspects
        assert (0, 2) not in mc.cross_aspects
        assert (1, 2) not in mc.cross_aspects

    def test_without_cross_aspects(self, natal_chart, partner_chart):
        """Test disabling cross-aspect calculation."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart])
            .without_cross_aspects()
            .calculate()
        )

        assert len(mc.cross_aspects) == 0


class TestMultiChartBuilderHouseOverlays:
    """Tests for house overlay configuration."""

    def test_house_overlays_calculated_by_default(self, natal_chart, partner_chart):
        """Test that house overlays are calculated by default."""
        mc = MultiChartBuilder.synastry(natal_chart, partner_chart).calculate()

        all_overlays = mc.get_all_house_overlays()
        assert len(all_overlays) > 0

    def test_without_house_overlays(self, natal_chart, partner_chart):
        """Test disabling house overlay calculation."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart])
            .without_house_overlays()
            .calculate()
        )

        assert len(mc.house_overlays) == 0


class TestMultiChartBuilderLabels:
    """Tests for label configuration."""

    def test_with_labels(self, natal_chart, partner_chart):
        """Test with_labels method."""
        mc = (
            MultiChartBuilder.from_charts([natal_chart, partner_chart])
            .with_labels(["Person A", "Person B"])
            .calculate()
        )

        assert mc.labels == ("Person A", "Person B")


# =============================================================================
# Integration Tests
# =============================================================================


class TestMultiChartIntegration:
    """Integration tests for complete workflows."""

    def test_synastry_workflow(self, natal_chart, partner_chart):
        """Test complete synastry workflow."""
        mc = MultiChartBuilder.synastry(
            natal_chart, partner_chart, label1="Kate", label2="Partner"
        ).calculate()

        # Check structure
        assert mc.chart_count == 2
        assert mc.labels == ("Kate", "Partner")
        assert mc.get_relationship(0, 1) == ComparisonType.SYNASTRY

        # Check cross-aspects
        aspects = mc.get_cross_aspects()
        assert len(aspects) > 0

        # Check house overlays
        overlays = mc.get_all_house_overlays()
        assert len(overlays) > 0

        # Check compatibility score
        score = mc.calculate_compatibility_score()
        assert 0.0 <= score <= 100.0

        # Check serialization
        data = mc.to_dict()
        assert data["chart_count"] == 2

    def test_triwheel_natal_progressed_transit(self, natal_chart):
        """Test triwheel: natal + progressed + transit."""
        mc = (
            MultiChartBuilder.from_chart(natal_chart, "Natal")
            .add_progression(age=30, label="Progressed")
            .add_transit("2025-06-15 12:00", label="Transit")
            .with_cross_aspects("to_primary")
            .calculate()
        )

        assert mc.chart_count == 3
        assert mc.labels == ("Natal", "Progressed", "Transit")

        # Should have aspects to primary (natal) only
        assert (0, 1) in mc.cross_aspects
        assert (0, 2) in mc.cross_aspects
        assert (1, 2) not in mc.cross_aspects

    def test_data_preservation(self, natal_chart, partner_chart):
        """Test that chart data is preserved through MultiChart.

        Note: Using MultiChart directly (not builder) preserves identity.
        Builder may recreate charts when calculating aspects.
        """
        mc = MultiChart(charts=(natal_chart, partner_chart))

        # Positions should be preserved (identity when using MultiChart directly)
        natal_sun = natal_chart.get_object("Sun")
        mc_sun = mc.get_object("Sun", chart=0)

        assert natal_sun is mc_sun
        assert natal_sun.longitude == mc_sun.longitude

        # Houses should be preserved
        natal_houses = natal_chart.get_houses()
        mc_natal = mc.chart1
        assert mc_natal.get_houses() is natal_houses
