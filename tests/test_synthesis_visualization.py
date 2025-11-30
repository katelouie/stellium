"""
Test that SynthesisChart can be visualized using the inherited draw() method.

This tests that the inheritance from CalculatedChart works properly.
"""

import os
import tempfile

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.synthesis import SynthesisBuilder


class TestSynthesisVisualization:
    """Tests for SynthesisChart visualization via inheritance."""

    @pytest.fixture
    def davison_chart(self):
        """Create a davison chart for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47",
            (37.4419, -122.1430),  # Palo Alto
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00",
            (47.6062, -122.3321),  # Seattle
        ).calculate()

        return (
            SynthesisBuilder.davison(chart1, chart2)
            .with_labels("Person A", "Person B")
            .calculate()
        )

    def test_draw_method_exists(self, davison_chart):
        """Test that SynthesisChart has inherited draw() method."""
        assert hasattr(davison_chart, "draw")
        assert callable(davison_chart.draw)

    def test_draw_returns_builder(self, davison_chart):
        """Test that draw() returns a ChartDrawBuilder."""
        from stellium.visualization.builder import ChartDrawBuilder

        builder = davison_chart.draw("test.svg")
        assert isinstance(builder, ChartDrawBuilder)

    def test_draw_and_save_creates_file(self, davison_chart):
        """Test that we can actually save a chart SVG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "davison_test.svg")

            # This should work via inheritance!
            davison_chart.draw(filepath).preset_standard().save()

            # Verify file was created
            assert os.path.exists(filepath)

            # Verify it's a valid SVG (starts with XML/SVG)
            with open(filepath) as f:
                content = f.read()
                assert "<?xml" in content or "<svg" in content

    def test_draw_with_theme(self, davison_chart):
        """Test that theme customization works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "davison_dark.svg")

            davison_chart.draw(filepath).with_theme("dark").save()

            assert os.path.exists(filepath)

    def test_draw_with_moon_phase(self, davison_chart):
        """Test that moon phase works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "davison_moon.svg")

            davison_chart.draw(filepath).with_moon_phase().save()

            assert os.path.exists(filepath)

    def test_draw_full_customization(self, davison_chart):
        """Test full customization chain works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "davison_custom.svg")

            (
                davison_chart.draw(filepath)
                .with_theme("celestial")
                .with_size(800)
                .with_moon_phase(position="top-left")
                .with_chart_info(position="top-right")
                .save()
            )

            assert os.path.exists(filepath)

            # Verify reasonable file size (not empty, not corrupted)
            size = os.path.getsize(filepath)
            assert size > 1000  # At least 1KB


class TestSynthesisChartContent:
    """Tests for the content of generated SVG files."""

    @pytest.fixture
    def davison_chart(self):
        """Create a davison chart for testing."""
        chart1 = ChartBuilder.from_details(
            "1994-01-06 11:47", (37.4419, -122.1430)
        ).calculate()

        chart2 = ChartBuilder.from_details(
            "2000-06-15 17:00", (47.6062, -122.3321)
        ).calculate()

        return SynthesisBuilder.davison(chart1, chart2).calculate()

    def test_svg_contains_zodiac_signs(self, davison_chart):
        """Test that SVG contains zodiac sign elements."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.svg")
            davison_chart.draw(filepath).preset_standard().save()

            with open(filepath) as f:
                content = f.read()

            # SVG should contain circle elements (for zodiac wheel)
            assert "<circle" in content

    def test_svg_has_reasonable_size(self, davison_chart):
        """Test that generated SVG has reasonable dimensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.svg")
            davison_chart.draw(filepath).with_size(600).save()

            with open(filepath) as f:
                content = f.read()

            # Should contain viewBox with 600 dimensions
            assert "600" in content
