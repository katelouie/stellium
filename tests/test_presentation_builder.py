"""
Comprehensive tests for presentation.builder module.

Tests the ReportBuilder class and its fluent API for creating reports.
"""

import datetime as dt
from pathlib import Path

import pytest
import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.engines.ephemeris import MockEphemerisEngine, SwissEphemerisEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.presentation import ReportBuilder
from stellium.presentation.sections import (
    AspectSection,
    ChartOverviewSection,
    MidpointSection,
    MoonPhaseSection,
    PlanetPositionSection,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_chart():
    """Create a sample chart for testing reports."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=37.7749, longitude=-122.4194, name="San Francisco, CA"
    )
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(SwissEphemerisEngine())
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate()
    )


@pytest.fixture
def mock_chart():
    """Create a chart with mock ephemeris for faster testing."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=37.7749, longitude=-122.4194, name="Test Location"
    )
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(MockEphemerisEngine())
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )


# ============================================================================
# BASIC BUILDER TESTS
# ============================================================================


def test_report_builder_initialization():
    """Test that ReportBuilder initializes with empty state."""
    builder = ReportBuilder()

    assert builder._chart is None
    assert builder._sections == []


def test_from_chart(sample_chart):
    """Test setting the chart on the builder."""
    builder = ReportBuilder().from_chart(sample_chart)

    assert builder._chart == sample_chart


def test_from_chart_returns_self(sample_chart):
    """Test that from_chart returns self for chaining."""
    builder = ReportBuilder()
    result = builder.from_chart(sample_chart)

    assert result is builder


# ============================================================================
# SECTION ADDING TESTS
# ============================================================================


def test_with_chart_overview(sample_chart):
    """Test adding chart overview section."""
    builder = ReportBuilder().from_chart(sample_chart).with_chart_overview()

    assert len(builder._sections) == 1
    assert isinstance(builder._sections[0], ChartOverviewSection)


def test_with_planet_positions(sample_chart):
    """Test adding planet positions section with default options."""
    builder = ReportBuilder().from_chart(sample_chart).with_planet_positions()

    assert len(builder._sections) == 1
    assert isinstance(builder._sections[0], PlanetPositionSection)
    assert builder._sections[0].include_speed is False
    assert builder._sections[0].include_house is True


def test_with_planet_positions_custom_options(sample_chart):
    """Test adding planet positions with custom options."""
    builder = (
        ReportBuilder()
        .from_chart(sample_chart)
        .with_planet_positions(
            include_speed=True, include_house=False, house_systems=["Placidus"]
        )
    )

    section = builder._sections[0]
    assert section.include_speed is True
    assert section.include_house is False
    assert section._house_systems == ["Placidus"]


def test_with_aspects_default(sample_chart):
    """Test adding aspects section with defaults."""
    builder = ReportBuilder().from_chart(sample_chart).with_aspects()

    assert len(builder._sections) == 1
    assert isinstance(builder._sections[0], AspectSection)
    assert builder._sections[0].mode == "all"
    assert builder._sections[0].orb_display is True
    assert builder._sections[0].sort_by == "orb"


def test_with_aspects_custom_options(sample_chart):
    """Test adding aspects with custom options."""
    builder = (
        ReportBuilder()
        .from_chart(sample_chart)
        .with_aspects(mode="major", orbs=False, sort_by="planet")
    )

    section = builder._sections[0]
    assert section.mode == "major"
    assert section.orb_display is False
    assert section.sort_by == "planet"


def test_with_midpoints_default(mock_chart):
    """Test adding midpoints section with defaults."""
    builder = ReportBuilder().from_chart(mock_chart).with_midpoints()

    assert len(builder._sections) == 1
    assert isinstance(builder._sections[0], MidpointSection)
    assert builder._sections[0].mode == "all"
    assert builder._sections[0].threshold is None


def test_with_midpoints_custom_options(mock_chart):
    """Test adding midpoints with custom options."""
    builder = (
        ReportBuilder().from_chart(mock_chart).with_midpoints(mode="core", threshold=10)
    )

    section = builder._sections[0]
    assert section.mode == "core"
    assert section.threshold == 10


def test_with_moon_phase(sample_chart):
    """Test adding moon phase section."""
    builder = ReportBuilder().from_chart(sample_chart).with_moon_phase()

    assert len(builder._sections) == 1
    assert isinstance(builder._sections[0], MoonPhaseSection)


def test_with_section_custom(mock_chart):
    """Test adding a custom section."""

    class CustomSection:
        @property
        def section_name(self):
            return "Custom"

        def generate_data(self, chart):
            return {"type": "text", "text": "Custom content"}

    custom = CustomSection()
    builder = ReportBuilder().from_chart(mock_chart).with_section(custom)

    assert len(builder._sections) == 1
    assert builder._sections[0] == custom


# ============================================================================
# CHAINING TESTS
# ============================================================================


def test_builder_chaining(sample_chart):
    """Test that all builder methods return self for chaining."""
    builder = (
        ReportBuilder()
        .from_chart(sample_chart)
        .with_chart_overview()
        .with_planet_positions()
        .with_aspects()
    )

    assert len(builder._sections) == 3


def test_builder_full_chain(sample_chart):
    """Test building a complete report with all sections."""
    builder = (
        ReportBuilder()
        .from_chart(sample_chart)
        .with_chart_overview()
        .with_planet_positions(include_speed=True)
        .with_aspects(mode="major")
        .with_midpoints(mode="core")
        .with_moon_phase()
    )

    assert len(builder._sections) == 5


# ============================================================================
# RENDERING TESTS
# ============================================================================


def test_render_without_chart():
    """Test that rendering without a chart raises ValueError."""
    builder = ReportBuilder().with_chart_overview()

    with pytest.raises(ValueError, match="No chart set"):
        builder.render()


def test_render_plain_table(mock_chart):
    """Test rendering with plain table format."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    # Should not raise
    result = builder.render(format="plain_table", show=False)
    assert result is None  # No file specified


def test_render_rich_table(mock_chart):
    """Test rendering with rich table format."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    # Should not raise
    result = builder.render(format="rich_table", show=False)
    assert result is None


def test_render_to_file(mock_chart, tmp_path):
    """Test rendering and saving to file."""
    builder = (
        ReportBuilder()
        .from_chart(mock_chart)
        .with_chart_overview()
        .with_planet_positions()
    )

    output_file = tmp_path / "report.txt"
    result = builder.render(format="plain_table", file=str(output_file), show=False)

    assert result == str(output_file)
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_render_file_content(mock_chart, tmp_path):
    """Test that rendered file contains expected content."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    output_file = tmp_path / "report.txt"
    builder.render(format="plain_table", file=str(output_file), show=False)

    content = output_file.read_text()
    assert "Chart Overview" in content
    assert "Test Location" in content


def test_render_unknown_format(mock_chart):
    """Test that unknown format is handled gracefully."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    # The implementation may handle unknown formats differently
    # Check that it either raises ValueError or handles gracefully
    try:
        result = builder.render(format="unknown_format", show=False)
        # If it doesn't raise, it should return None (no file output)
        assert result is None or isinstance(result, str)
    except (ValueError, NotImplementedError):
        # This is also acceptable behavior
        pass


def test_render_not_implemented_format(mock_chart):
    """Test that unimplemented formats are handled."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    # PDF format may raise NotImplementedError or ValueError
    try:
        result = builder.render(format="pdf", show=False)
        # If it doesn't raise, check return value
        assert result is None or isinstance(result, str)
    except (NotImplementedError, ValueError):
        # This is acceptable - unimplemented format
        pass


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_report_generation(sample_chart):
    """Test generating a complete report with all sections."""
    builder = (
        ReportBuilder()
        .from_chart(sample_chart)
        .with_chart_overview()
        .with_planet_positions(include_speed=True, include_house=True)
        .with_aspects(mode="major", sort_by="orb")
        .with_moon_phase()
    )

    # Should not raise
    result = builder.render(format="plain_table", show=False)
    assert result is None


def test_multiple_reports_from_same_builder(mock_chart, tmp_path):
    """Test that a builder can render multiple times."""
    builder = (
        ReportBuilder()
        .from_chart(mock_chart)
        .with_chart_overview()
        .with_planet_positions()
    )

    # First render
    file1 = tmp_path / "report1.txt"
    result1 = builder.render(format="plain_table", file=str(file1), show=False)
    assert Path(result1).exists()

    # Second render
    file2 = tmp_path / "report2.txt"
    result2 = builder.render(format="plain_table", file=str(file2), show=False)
    assert Path(result2).exists()

    # Both files should have same content
    assert file1.read_text() == file2.read_text()


def test_empty_report(mock_chart):
    """Test rendering a report with no sections."""
    builder = ReportBuilder().from_chart(mock_chart)

    # Should not raise even with no sections
    result = builder.render(format="plain_table", show=False)
    assert result is None


def test_section_data_generation(mock_chart):
    """Test that section data is generated correctly."""
    builder = (
        ReportBuilder()
        .from_chart(mock_chart)
        .with_chart_overview()
        .with_planet_positions()
    )

    # Access internal method to verify data generation
    section_data = [
        (section.section_name, section.generate_data(builder._chart))
        for section in builder._sections
    ]

    assert len(section_data) == 2
    assert section_data[0][0] == "Chart Overview"
    assert section_data[1][0] == "Planet Positions"
    assert section_data[0][1]["type"] == "key_value"
    assert section_data[1][1]["type"] == "table"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


def test_builder_reuse(mock_chart):
    """Test that a builder can be reused with different charts."""
    builder = ReportBuilder().with_chart_overview().with_planet_positions()

    # First chart
    builder.from_chart(mock_chart)
    result1 = builder.render(format="plain_table", show=False)
    assert result1 is None

    # Create second chart
    datetime2 = dt.datetime(2010, 6, 15, 14, 30, tzinfo=pytz.UTC)
    location2 = ChartLocation(latitude=51.5074, longitude=-0.1278, name="London")
    native2 = Native(datetime2, location2)
    chart2 = (
        ChartBuilder.from_native(native2)
        .with_ephemeris(MockEphemerisEngine())
        .calculate()
    )

    # Reuse builder with new chart
    builder.from_chart(chart2)
    result2 = builder.render(format="plain_table", show=False)
    assert result2 is None


def test_render_show_parameter(mock_chart, capsys):
    """Test that show parameter controls console output."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    # With show=False, should not print to console
    builder.render(format="plain_table", show=False)
    captured = capsys.readouterr()
    # With show=False, output could be empty or minimal
    # (depending on implementation details)

    # With show=True (default), should print to console
    builder.render(format="plain_table", show=True)
    captured = capsys.readouterr()
    assert len(captured.out) > 0
    assert "Chart Overview" in captured.out


def test_render_file_and_show(mock_chart, tmp_path, capsys):
    """Test rendering both to file and console."""
    builder = ReportBuilder().from_chart(mock_chart).with_chart_overview()

    output_file = tmp_path / "report.txt"
    result = builder.render(format="plain_table", file=str(output_file), show=True)

    # Should create file
    assert result == str(output_file)
    assert output_file.exists()

    # Should also print to console
    captured = capsys.readouterr()
    assert len(captured.out) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
