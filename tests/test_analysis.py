"""
Tests for the stellium.analysis module.

Tests batch calculation, DataFrame conversion, queries, and statistics.
"""

import tempfile
from pathlib import Path

import pytest

from stellium.analysis import (
    BatchCalculator,
    ChartQuery,
    ChartStats,
    aspects_to_dataframe,
    charts_to_dataframe,
    export_csv,
    export_json,
    positions_to_dataframe,
)
from stellium.core.builder import ChartBuilder
from stellium.core.models import ObjectType
from stellium.core.native import Native

# Skip all tests if pandas is not available
pytest.importorskip("pandas")
import pandas as pd  # noqa

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_natives():
    """Create a small list of sample Native objects for testing."""
    return [
        Native("2000-01-01 12:00", "New York, NY", name="Person 1"),
        Native("1990-06-15 08:30", "Los Angeles, CA", name="Person 2"),
        Native("1985-03-21 14:00", "Chicago, IL", name="Person 3"),
    ]


@pytest.fixture
def sample_charts(sample_natives):
    """Calculate charts from sample natives."""
    return [
        ChartBuilder.from_native(native).with_aspects().calculate()
        for native in sample_natives
    ]


# ============================================================================
# BatchCalculator Tests
# ============================================================================


class TestBatchCalculator:
    """Tests for BatchCalculator."""

    def test_from_natives(self, sample_natives):
        """Test creating BatchCalculator from list of Natives."""
        batch = BatchCalculator.from_natives(sample_natives)
        assert batch.count() == 3

    def test_calculate_all(self, sample_natives):
        """Test calculating all charts at once."""
        charts = BatchCalculator.from_natives(sample_natives).calculate_all()
        assert len(charts) == 3
        assert all(chart.get_object("Sun") is not None for chart in charts)

    def test_calculate_generator(self, sample_natives):
        """Test calculating charts as generator."""
        batch = BatchCalculator.from_natives(sample_natives)
        count = 0
        for chart in batch.calculate():
            count += 1
            assert chart.get_object("Sun") is not None
        assert count == 3

    def test_with_aspects(self, sample_natives):
        """Test batch calculation with aspect engine."""
        charts = (
            BatchCalculator.from_natives(sample_natives).with_aspects().calculate_all()
        )
        # Should have aspects calculated
        assert all(len(chart.aspects) > 0 for chart in charts)

    def test_progress_callback(self, sample_natives):
        """Test progress callback is called correctly."""
        progress_calls = []

        def track_progress(current, total, name):
            progress_calls.append((current, total, name))

        BatchCalculator.from_natives(sample_natives).with_progress(
            track_progress
        ).calculate_all()

        assert len(progress_calls) == 3
        assert progress_calls[0][0] == 1  # First chart
        assert progress_calls[0][1] == 3  # Total count
        assert progress_calls[-1][0] == 3  # Last chart

    def test_len_and_repr(self, sample_natives):
        """Test __len__ and __repr__."""
        batch = BatchCalculator.from_natives(sample_natives)
        assert len(batch) == 3
        assert "3 sources" in repr(batch)


# ============================================================================
# DataFrame Conversion Tests
# ============================================================================


class TestDataFrameConversion:
    """Tests for DataFrame conversion functions."""

    def test_charts_to_dataframe(self, sample_charts):
        """Test converting charts to chart-level DataFrame."""
        df = charts_to_dataframe(sample_charts)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "chart_id" in df.columns
        assert "sun_sign" in df.columns
        assert "moon_sign" in df.columns
        assert "fire_count" in df.columns

    def test_charts_to_dataframe_columns(self, sample_charts):
        """Test that all expected columns are present."""
        df = charts_to_dataframe(sample_charts)

        expected_columns = [
            "chart_id",
            "name",
            "datetime_utc",
            "julian_day",
            "latitude",
            "longitude",
            "location_name",
            "sun_longitude",
            "sun_sign",
            "moon_longitude",
            "moon_sign",
            "fire_count",
            "earth_count",
            "air_count",
            "water_count",
            "cardinal_count",
            "fixed_count",
            "mutable_count",
            "retrograde_count",
        ]

        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_positions_to_dataframe(self, sample_charts):
        """Test converting charts to position-level DataFrame."""
        df = positions_to_dataframe(sample_charts)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > len(sample_charts)  # Multiple positions per chart
        assert "chart_id" in df.columns
        assert "object_name" in df.columns
        assert "longitude" in df.columns
        assert "sign" in df.columns
        assert "is_retrograde" in df.columns

    def test_positions_to_dataframe_filter(self, sample_charts):
        """Test filtering positions by object type."""
        df = positions_to_dataframe(sample_charts, object_types=[ObjectType.PLANET])

        # Should only have planets
        assert all(df["object_type"] == "planet")

    def test_aspects_to_dataframe(self, sample_charts):
        """Test converting charts to aspect-level DataFrame."""
        df = aspects_to_dataframe(sample_charts)

        assert isinstance(df, pd.DataFrame)
        assert "chart_id" in df.columns
        assert "object1" in df.columns
        assert "object2" in df.columns
        assert "aspect_name" in df.columns
        assert "orb" in df.columns


# ============================================================================
# ChartQuery Tests
# ============================================================================


class TestChartQuery:
    """Tests for ChartQuery."""

    def test_where_sun_sign(self, sample_charts):
        """Test filtering by sun sign."""
        # Get all sun signs first
        all_signs = [c.get_object("Sun").sign for c in sample_charts]

        # Query for one of them
        if all_signs:
            target_sign = all_signs[0]
            results = ChartQuery(sample_charts).where_sun(sign=target_sign).results()
            assert len(results) >= 1
            for chart in results:
                assert chart.get_object("Sun").sign == target_sign

    def test_where_sun_multiple_signs(self, sample_charts):
        """Test filtering by multiple sun signs."""
        fire_signs = ["Aries", "Leo", "Sagittarius"]
        results = ChartQuery(sample_charts).where_sun(sign=fire_signs).results()

        for chart in results:
            assert chart.get_object("Sun").sign in fire_signs

    def test_where_planet(self, sample_charts):
        """Test filtering by planet position."""
        # Just make sure it doesn't error
        results = ChartQuery(sample_charts).where_planet("Mars", sign="Aries").results()
        assert isinstance(results, list)

    def test_where_aspect(self, sample_charts):
        """Test filtering by aspect."""
        results = (
            ChartQuery(sample_charts)
            .where_aspect("Sun", "Moon", aspect="conjunction")
            .results()
        )
        assert isinstance(results, list)

    def test_where_element_dominant(self, sample_charts):
        """Test filtering by dominant element."""
        results = (
            ChartQuery(sample_charts)
            .where_element_dominant("fire", min_count=3)
            .results()
        )
        assert isinstance(results, list)

    def test_chained_filters(self, sample_charts):
        """Test chaining multiple filters."""
        results = (
            ChartQuery(sample_charts)
            .where_sun(sign=["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo"])
            .where_sect("day")
            .results()
        )
        assert isinstance(results, list)

    def test_count(self, sample_charts):
        """Test count method."""
        count = ChartQuery(sample_charts).count()
        assert count == len(sample_charts)

    def test_first(self, sample_charts):
        """Test first method."""
        first = ChartQuery(sample_charts).first()
        assert first is not None
        assert first == sample_charts[0] or first in sample_charts

    def test_to_dataframe(self, sample_charts):
        """Test to_dataframe method."""
        df = ChartQuery(sample_charts).to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_charts)

    def test_where_custom(self, sample_charts):
        """Test custom filter predicate."""
        # Filter for charts with more than 5 aspects
        results = (
            ChartQuery(sample_charts)
            .where_custom(lambda c: len(c.aspects) > 5)
            .results()
        )
        for chart in results:
            assert len(chart.aspects) > 5


# ============================================================================
# ChartStats Tests
# ============================================================================


class TestChartStats:
    """Tests for ChartStats."""

    def test_chart_count(self, sample_charts):
        """Test chart count property."""
        stats = ChartStats(sample_charts)
        assert stats.chart_count == 3

    def test_element_distribution(self, sample_charts):
        """Test element distribution calculation."""
        stats = ChartStats(sample_charts)
        dist = stats.element_distribution()

        assert "fire" in dist
        assert "earth" in dist
        assert "air" in dist
        assert "water" in dist

        # Normalized should sum to ~1
        assert abs(sum(dist.values()) - 1.0) < 0.01

    def test_element_distribution_raw(self, sample_charts):
        """Test raw element counts."""
        stats = ChartStats(sample_charts)
        dist = stats.element_distribution(normalize=False)

        # Should be counts, not proportions
        assert all(isinstance(v, float) for v in dist.values())
        assert sum(dist.values()) > 0

    def test_modality_distribution(self, sample_charts):
        """Test modality distribution calculation."""
        stats = ChartStats(sample_charts)
        dist = stats.modality_distribution()

        assert "cardinal" in dist
        assert "fixed" in dist
        assert "mutable" in dist

    def test_sign_distribution(self, sample_charts):
        """Test sign distribution for an object."""
        stats = ChartStats(sample_charts)
        dist = stats.sign_distribution("Sun")

        # Should have all 12 signs
        assert len(dist) == 12
        assert "Aries" in dist
        assert "Pisces" in dist

        # Total should equal chart count
        assert sum(dist.values()) == 3

    def test_aspect_frequency(self, sample_charts):
        """Test aspect frequency calculation."""
        stats = ChartStats(sample_charts)
        freq = stats.aspect_frequency()

        assert isinstance(freq, dict)

    def test_sect_distribution(self, sample_charts):
        """Test sect distribution."""
        stats = ChartStats(sample_charts)
        dist = stats.sect_distribution()

        # Should have day and/or night
        assert "day" in dist or "night" in dist

    def test_retrograde_frequency(self, sample_charts):
        """Test retrograde frequency calculation."""
        stats = ChartStats(sample_charts)
        freq = stats.retrograde_frequency()

        assert isinstance(freq, dict)

    def test_summary(self, sample_charts):
        """Test summary method."""
        stats = ChartStats(sample_charts)
        summary = stats.summary()

        assert "chart_count" in summary
        assert "element_distribution" in summary
        assert "sun_sign_distribution" in summary


# ============================================================================
# Export Tests
# ============================================================================


class TestExport:
    """Tests for export functions."""

    def test_export_csv(self, sample_charts):
        """Test CSV export."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = Path(f.name)

        try:
            export_csv(sample_charts, path)
            assert path.exists()

            # Read back and verify
            df = pd.read_csv(path)
            assert len(df) == 3
        finally:
            path.unlink(missing_ok=True)

    def test_export_csv_positions(self, sample_charts):
        """Test CSV export with positions schema."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = Path(f.name)

        try:
            export_csv(sample_charts, path, schema="positions")
            assert path.exists()

            df = pd.read_csv(path)
            assert len(df) > 3  # More rows than charts
            assert "object_name" in df.columns
        finally:
            path.unlink(missing_ok=True)

    def test_export_json(self, sample_charts):
        """Test JSON export."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            export_json(sample_charts, path)
            assert path.exists()

            import json

            with open(path) as f:
                data = json.load(f)
            assert len(data) == 3
        finally:
            path.unlink(missing_ok=True)

    def test_export_json_lines(self, sample_charts):
        """Test JSON Lines export."""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            path = Path(f.name)

        try:
            export_json(sample_charts, path, lines=True)
            assert path.exists()

            import json

            with open(path) as f:
                lines = f.readlines()
            assert len(lines) == 3

            # Each line should be valid JSON
            for line in lines:
                json.loads(line)
        finally:
            path.unlink(missing_ok=True)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow(self, sample_natives):
        """Test complete analysis workflow."""
        # 1. Batch calculate
        charts = (
            BatchCalculator.from_natives(sample_natives).with_aspects().calculate_all()
        )

        # 2. Query for specific criteria
        fire_suns = (
            ChartQuery(charts).where_element_dominant("fire", min_count=2).results()
        )

        # 3. Get statistics
        stats = ChartStats(charts)
        element_dist = stats.element_distribution()

        # 4. Convert to DataFrame
        df = charts_to_dataframe(charts)

        # Verify everything worked
        assert len(charts) == 3
        assert isinstance(fire_suns, list)
        assert sum(element_dist.values()) > 0
        assert len(df) == 3

    def test_dataframe_filtering(self, sample_charts):
        """Test using pandas filtering on exported DataFrame."""
        df = charts_to_dataframe(sample_charts)

        # Filter using pandas
        capricorn_suns = df[df["sun_sign"] == "Capricorn"]
        fire_heavy = df[df["fire_count"] >= 3]

        assert isinstance(capricorn_suns, pd.DataFrame)
        assert isinstance(fire_heavy, pd.DataFrame)
