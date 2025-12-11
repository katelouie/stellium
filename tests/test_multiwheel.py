"""Tests for stellium.core.multiwheel - MultiWheel chart comparisons.

Tests cover:
- MultiWheel dataclass validation and properties
- MultiWheelBuilder fluent API
- Cross-chart aspect calculation
- Biwheel, triwheel, and quadwheel configurations
"""

import datetime as dt

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.multiwheel import MultiWheel, MultiWheelBuilder

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def natal_chart():
    """A natal chart for testing."""
    return ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Natal",
    ).calculate()


@pytest.fixture(scope="module")
def transit_chart():
    """A transit chart for testing."""
    return ChartBuilder.from_details(
        "2024-06-15 12:00",
        "Palo Alto, CA",
        name="Transit",
    ).calculate()


@pytest.fixture(scope="module")
def progressed_chart():
    """A progressed-style chart for testing (different date)."""
    return ChartBuilder.from_details(
        "2024-01-06 11:47",
        "Palo Alto, CA",
        name="Progressed",
    ).calculate()


@pytest.fixture(scope="module")
def fourth_chart():
    """A fourth chart for quadwheel testing."""
    return ChartBuilder.from_details(
        "2000-01-01 12:00",
        "Palo Alto, CA",
        name="Fourth",
    ).calculate()


# =============================================================================
# MultiWheel Dataclass Tests
# =============================================================================


class TestMultiWheelDataclass:
    """Tests for the MultiWheel frozen dataclass."""

    def test_create_biwheel(self, natal_chart, transit_chart):
        """Create a basic biwheel (2 charts)."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        assert multiwheel.chart_count == 2
        assert multiwheel.chart1 is natal_chart
        assert multiwheel.chart2 is transit_chart
        assert multiwheel.chart3 is None
        assert multiwheel.chart4 is None

    def test_create_triwheel(self, natal_chart, transit_chart, progressed_chart):
        """Create a triwheel (3 charts)."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart, progressed_chart))

        assert multiwheel.chart_count == 3
        assert multiwheel.chart1 is natal_chart
        assert multiwheel.chart2 is transit_chart
        assert multiwheel.chart3 is progressed_chart
        assert multiwheel.chart4 is None

    def test_create_quadwheel(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Create a quadwheel (4 charts)."""
        multiwheel = MultiWheel(
            charts=(natal_chart, transit_chart, progressed_chart, fourth_chart)
        )

        assert multiwheel.chart_count == 4
        assert multiwheel.chart1 is natal_chart
        assert multiwheel.chart2 is transit_chart
        assert multiwheel.chart3 is progressed_chart
        assert multiwheel.chart4 is fourth_chart

    def test_too_few_charts_raises(self, natal_chart):
        """Creating MultiWheel with <2 charts raises ValueError."""
        with pytest.raises(ValueError, match="at least 2 charts"):
            MultiWheel(charts=(natal_chart,))

    def test_too_many_charts_raises(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Creating MultiWheel with >4 charts raises ValueError."""
        # Create a 5th chart inline
        fifth_chart = ChartBuilder.from_details(
            "1990-01-01 12:00", (37.0, -122.0)
        ).calculate()

        with pytest.raises(ValueError, match="at most 4 charts"):
            MultiWheel(
                charts=(
                    natal_chart,
                    transit_chart,
                    progressed_chart,
                    fourth_chart,
                    fifth_chart,
                )
            )

    def test_auto_generated_labels(self, natal_chart, transit_chart):
        """Labels are auto-generated if not provided."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        assert multiwheel.labels == ("Chart 1", "Chart 2")

    def test_auto_generated_labels_triwheel(
        self, natal_chart, transit_chart, progressed_chart
    ):
        """Labels are auto-generated for triwheel."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart, progressed_chart))

        assert multiwheel.labels == ("Chart 1", "Chart 2", "Chart 3")

    def test_auto_generated_labels_quadwheel(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Labels are auto-generated for quadwheel."""
        multiwheel = MultiWheel(
            charts=(natal_chart, transit_chart, progressed_chart, fourth_chart)
        )

        assert multiwheel.labels == ("Chart 1", "Chart 2", "Chart 3", "Chart 4")

    def test_custom_labels(self, natal_chart, transit_chart):
        """Custom labels are preserved."""
        multiwheel = MultiWheel(
            charts=(natal_chart, transit_chart),
            labels=("Natal", "Transits"),
        )

        assert multiwheel.labels == ("Natal", "Transits")

    def test_frozen_dataclass(self, natal_chart, transit_chart):
        """MultiWheel is immutable (frozen)."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        with pytest.raises(AttributeError):
            multiwheel.charts = (transit_chart, natal_chart)

    def test_calculation_timestamp(self, natal_chart, transit_chart):
        """MultiWheel has a calculation timestamp."""
        before = dt.datetime.now(dt.UTC)
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))
        after = dt.datetime.now(dt.UTC)

        assert before <= multiwheel.calculation_timestamp <= after

    def test_empty_cross_aspects_by_default(self, natal_chart, transit_chart):
        """Cross aspects dict is empty by default."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        assert multiwheel.cross_aspects == {}

    def test_cross_aspects_stored(self, natal_chart, transit_chart):
        """Cross aspects can be provided at construction."""

        # Create a mock aspect (we don't need real data for this test)
        mock_aspects = ()  # Empty tuple is fine for testing storage

        multiwheel = MultiWheel(
            charts=(natal_chart, transit_chart),
            cross_aspects={(0, 1): mock_aspects},
        )

        assert (0, 1) in multiwheel.cross_aspects


# =============================================================================
# MultiWheelBuilder Tests
# =============================================================================


class TestMultiWheelBuilder:
    """Tests for the MultiWheelBuilder fluent API."""

    def test_from_charts_biwheel(self, natal_chart, transit_chart):
        """Build a biwheel using from_charts."""
        multiwheel = MultiWheelBuilder.from_charts(
            [natal_chart, transit_chart]
        ).calculate()

        assert multiwheel.chart_count == 2
        assert multiwheel.chart1 is natal_chart
        assert multiwheel.chart2 is transit_chart

    def test_from_charts_triwheel(self, natal_chart, transit_chart, progressed_chart):
        """Build a triwheel using from_charts."""
        multiwheel = MultiWheelBuilder.from_charts(
            [natal_chart, transit_chart, progressed_chart]
        ).calculate()

        assert multiwheel.chart_count == 3

    def test_from_charts_quadwheel(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Build a quadwheel using from_charts."""
        multiwheel = MultiWheelBuilder.from_charts(
            [natal_chart, transit_chart, progressed_chart, fourth_chart]
        ).calculate()

        assert multiwheel.chart_count == 4

    def test_too_few_charts_raises(self, natal_chart):
        """Builder rejects <2 charts."""
        with pytest.raises(ValueError, match="at least 2 charts"):
            MultiWheelBuilder.from_charts([natal_chart])

    def test_too_many_charts_raises(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Builder rejects >4 charts."""
        fifth_chart = ChartBuilder.from_details(
            "1990-01-01 12:00", (37.0, -122.0)
        ).calculate()

        with pytest.raises(ValueError, match="at most 4 charts"):
            MultiWheelBuilder.from_charts(
                [
                    natal_chart,
                    transit_chart,
                    progressed_chart,
                    fourth_chart,
                    fifth_chart,
                ]
            )

    def test_with_labels(self, natal_chart, transit_chart):
        """with_labels sets custom labels."""
        multiwheel = (
            MultiWheelBuilder.from_charts([natal_chart, transit_chart])
            .with_labels(["Natal", "Transit 2024"])
            .calculate()
        )

        assert multiwheel.labels == ("Natal", "Transit 2024")

    def test_with_labels_chaining(self, natal_chart, transit_chart):
        """with_labels returns self for chaining."""
        builder = MultiWheelBuilder.from_charts([natal_chart, transit_chart])
        result = builder.with_labels(["A", "B"])

        assert result is builder

    def test_with_cross_aspects(self, natal_chart, transit_chart):
        """with_cross_aspects enables aspect calculation."""
        multiwheel = (
            MultiWheelBuilder.from_charts([natal_chart, transit_chart])
            .with_cross_aspects()
            .calculate()
        )

        # Should have calculated aspects between charts 0 and 1
        assert (0, 1) in multiwheel.cross_aspects
        # The aspects should be a tuple
        assert isinstance(multiwheel.cross_aspects[(0, 1)], tuple)

    def test_with_cross_aspects_chaining(self, natal_chart, transit_chart):
        """with_cross_aspects returns self for chaining."""
        builder = MultiWheelBuilder.from_charts([natal_chart, transit_chart])
        result = builder.with_cross_aspects()

        assert result is builder

    def test_cross_aspects_triwheel(self, natal_chart, transit_chart, progressed_chart):
        """Cross aspects calculated for all pairs in triwheel."""
        multiwheel = (
            MultiWheelBuilder.from_charts(
                [natal_chart, transit_chart, progressed_chart]
            )
            .with_cross_aspects()
            .calculate()
        )

        # Should have aspects between all pairs: (0,1), (0,2), (1,2)
        assert (0, 1) in multiwheel.cross_aspects
        assert (0, 2) in multiwheel.cross_aspects
        assert (1, 2) in multiwheel.cross_aspects

    def test_cross_aspects_quadwheel(
        self, natal_chart, transit_chart, progressed_chart, fourth_chart
    ):
        """Cross aspects calculated for all pairs in quadwheel."""
        multiwheel = (
            MultiWheelBuilder.from_charts(
                [natal_chart, transit_chart, progressed_chart, fourth_chart]
            )
            .with_cross_aspects()
            .calculate()
        )

        # Should have aspects between all pairs: 6 pairs total
        # (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
        assert (0, 1) in multiwheel.cross_aspects
        assert (0, 2) in multiwheel.cross_aspects
        assert (0, 3) in multiwheel.cross_aspects
        assert (1, 2) in multiwheel.cross_aspects
        assert (1, 3) in multiwheel.cross_aspects
        assert (2, 3) in multiwheel.cross_aspects

    def test_fluent_chain_all_options(
        self, natal_chart, transit_chart, progressed_chart
    ):
        """Test full fluent chain with all options."""
        multiwheel = (
            MultiWheelBuilder.from_charts(
                [natal_chart, transit_chart, progressed_chart]
            )
            .with_labels(["Natal", "Transit", "Progressed"])
            .with_cross_aspects()
            .calculate()
        )

        assert multiwheel.chart_count == 3
        assert multiwheel.labels == ("Natal", "Transit", "Progressed")
        assert len(multiwheel.cross_aspects) == 3  # 3 pairs


# =============================================================================
# Cross-Aspect Tests
# =============================================================================


class TestCrossAspects:
    """Tests for cross-chart aspect calculation."""

    def test_cross_aspects_contain_aspects(self, natal_chart, transit_chart):
        """Cross aspects should contain actual aspect objects."""
        multiwheel = (
            MultiWheelBuilder.from_charts([natal_chart, transit_chart])
            .with_cross_aspects()
            .calculate()
        )

        aspects = multiwheel.cross_aspects[(0, 1)]

        # Should have found some aspects between the charts
        # (two real charts will have aspects)
        assert len(aspects) > 0

    def test_cross_aspects_are_aspect_objects(self, natal_chart, transit_chart):
        """Cross aspects should be Aspect objects."""
        from stellium.core.models import Aspect

        multiwheel = (
            MultiWheelBuilder.from_charts([natal_chart, transit_chart])
            .with_cross_aspects()
            .calculate()
        )

        aspects = multiwheel.cross_aspects[(0, 1)]

        for aspect in aspects:
            assert isinstance(aspect, Aspect)

    def test_no_cross_aspects_by_default(self, natal_chart, transit_chart):
        """Without with_cross_aspects(), no aspects calculated."""
        multiwheel = MultiWheelBuilder.from_charts(
            [natal_chart, transit_chart]
        ).calculate()

        assert multiwheel.cross_aspects == {}


# =============================================================================
# Draw Method Tests
# =============================================================================


class TestMultiWheelDraw:
    """Tests for the draw() method."""

    def test_draw_returns_builder(self, natal_chart, transit_chart):
        """draw() returns a ChartDrawBuilder."""
        from stellium.visualization.builder import ChartDrawBuilder

        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))
        builder = multiwheel.draw("test.svg")

        assert isinstance(builder, ChartDrawBuilder)

    def test_draw_with_custom_filename(self, natal_chart, transit_chart):
        """draw() accepts custom filename."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        # Just verify it doesn't raise - actual file writing is visualization's job
        builder = multiwheel.draw("my_biwheel.svg")
        assert builder is not None

    def test_draw_default_filename(self, natal_chart, transit_chart):
        """draw() has default filename."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        # Default is "multiwheel.svg"
        builder = multiwheel.draw()
        assert builder is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestMultiWheelIntegration:
    """Integration tests for MultiWheel with real charts."""

    def test_synastry_biwheel(self, natal_chart, transit_chart):
        """Create a synastry-style biwheel."""
        multiwheel = (
            MultiWheelBuilder.from_charts([natal_chart, transit_chart])
            .with_labels(["Person A", "Person B"])
            .with_cross_aspects()
            .calculate()
        )

        assert multiwheel.chart_count == 2
        assert "Person A" in multiwheel.labels
        assert "Person B" in multiwheel.labels

        # Should have inter-chart aspects
        aspects = multiwheel.cross_aspects[(0, 1)]
        assert len(aspects) > 0

    def test_natal_progressed_transit_triwheel(
        self, natal_chart, progressed_chart, transit_chart
    ):
        """Create a natal + progressed + transit triwheel."""
        multiwheel = (
            MultiWheelBuilder.from_charts(
                [natal_chart, progressed_chart, transit_chart]
            )
            .with_labels(["Natal", "Progressed", "Transit"])
            .with_cross_aspects()
            .calculate()
        )

        assert multiwheel.chart_count == 3

        # Access each chart
        assert multiwheel.chart1 is natal_chart
        assert multiwheel.chart2 is progressed_chart
        assert multiwheel.chart3 is transit_chart

        # Should have aspects between all pairs
        assert len(multiwheel.cross_aspects) == 3

    def test_charts_preserve_positions(self, natal_chart, transit_chart):
        """Charts in MultiWheel preserve their position data."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        # Positions should be accessible
        natal_sun = multiwheel.chart1.get_object("Sun")
        transit_sun = multiwheel.chart2.get_object("Sun")

        assert natal_sun is not None
        assert transit_sun is not None

        # They should have different positions (different dates)
        assert natal_sun.longitude != transit_sun.longitude

    def test_charts_preserve_houses(self, natal_chart, transit_chart):
        """Charts in MultiWheel preserve their house data."""
        multiwheel = MultiWheel(charts=(natal_chart, transit_chart))

        # Houses should be accessible
        natal_houses = multiwheel.chart1.get_houses()
        transit_houses = multiwheel.chart2.get_houses()

        assert natal_houses is not None
        assert transit_houses is not None
