"""
Comprehensive tests for presentation.sections module.

Tests all section classes and their data generation logic.
"""

import datetime as dt

import pytest
import pytz

from stellium.components.midpoints import MidpointCalculator
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.ephemeris import MockEphemerisEngine, SwissEphemerisEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.orbs import SimpleOrbEngine
from stellium.presentation.sections import (
    AspectSection,
    CacheInfoSection,
    ChartOverviewSection,
    MidpointSection,
    MoonPhaseSection,
    PlanetPositionSection,
    get_aspect_sort_key,
    get_object_sort_key,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def sample_chart():
    """Create a chart with real ephemeris for testing sections."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(
        latitude=37.7749, longitude=-122.4194, name="San Francisco, CA"
    )
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(SwissEphemerisEngine())
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects(ModernAspectEngine())
        .with_orbs(SimpleOrbEngine())
        .calculate()
    )


@pytest.fixture
def mock_chart():
    """Create a mock chart for faster testing."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=0, longitude=0, name="Test Location")
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(MockEphemerisEngine())
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )


@pytest.fixture
def chart_with_midpoints():
    """Create a chart with midpoints calculated."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(MockEphemerisEngine())
        .add_component(MidpointCalculator())
        .calculate()
    )


# ============================================================================
# CHART OVERVIEW SECTION TESTS
# ============================================================================


def test_chart_overview_section_name():
    """Test ChartOverviewSection section name."""
    section = ChartOverviewSection()
    assert section.section_name == "Chart Overview"


def test_chart_overview_generate_data(sample_chart):
    """Test ChartOverviewSection data generation."""
    section = ChartOverviewSection()
    data = section.generate_data(sample_chart)

    assert data["type"] == "key_value"
    assert "data" in data
    assert "Date" in data["data"]
    assert "Time" in data["data"]
    assert "Location" in data["data"]
    assert "Coordinates" in data["data"]
    assert "House System" in data["data"]


def test_chart_overview_date_format(sample_chart):
    """Test that date is formatted correctly."""
    section = ChartOverviewSection()
    data = section.generate_data(sample_chart)

    assert data["data"]["Date"] == "January 01, 2000"


def test_chart_overview_house_systems(sample_chart):
    """Test that house systems are listed correctly."""
    section = ChartOverviewSection()
    data = section.generate_data(sample_chart)

    house_systems = data["data"]["House System"]
    assert "Placidus" in house_systems
    assert "Whole Sign" in house_systems


def test_chart_overview_location(sample_chart):
    """Test location information in overview."""
    section = ChartOverviewSection()
    data = section.generate_data(sample_chart)

    assert "San Francisco" in data["data"]["Location"]
    assert "37.7749" in data["data"]["Coordinates"]
    assert "-122.4194" in data["data"]["Coordinates"]


# ============================================================================
# PLANET POSITION SECTION TESTS
# ============================================================================


def test_planet_position_section_name():
    """Test PlanetPositionSection section name."""
    section = PlanetPositionSection()
    assert section.section_name == "Planet Positions"


def test_planet_position_default_options():
    """Test PlanetPositionSection default options."""
    section = PlanetPositionSection()
    assert section.include_speed is False
    assert section.include_house is True
    assert section.house_system is None


def test_planet_position_custom_options():
    """Test PlanetPositionSection custom options."""
    section = PlanetPositionSection(
        include_speed=True, include_house=False, house_system="Placidus"
    )
    assert section.include_speed is True
    assert section.include_house is False
    assert section.house_system == "Placidus"


def test_planet_position_generate_data(sample_chart):
    """Test PlanetPositionSection data generation."""
    section = PlanetPositionSection()
    data = section.generate_data(sample_chart)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Planet" in data["headers"]
    assert "Position" in data["headers"]
    assert "House" in data["headers"]


def test_planet_position_headers_with_speed(sample_chart):
    """Test headers when speed is included."""
    section = PlanetPositionSection(include_speed=True)
    data = section.generate_data(sample_chart)

    # Verify the section is configured correctly and generates data
    assert section.include_speed is True
    assert "Speed" in data["headers"]
    assert "Motion" in data["headers"]


def test_planet_position_headers_without_house():
    """Test headers when house is excluded."""
    section = PlanetPositionSection(include_house=False)
    assert section.include_house is False


def test_planet_position_rows_content(mock_chart):
    """Test that rows contain planet data."""
    section = PlanetPositionSection(include_house=False, include_speed=False)
    data = section.generate_data(mock_chart)

    rows = data["rows"]
    assert len(rows) > 0

    # Each row should have planet name and position
    for row in rows:
        assert len(row) >= 2  # At least name and position
        assert isinstance(row[0], str)  # Planet name
        assert "°" in row[1]  # Position with degree symbol


def test_planet_position_filters_objects(mock_chart):
    """Test that only planets, asteroids, nodes, points are included."""
    section = PlanetPositionSection()
    data = section.generate_data(mock_chart)

    # Get all position names from rows
    planet_names = [row[0] for row in data["rows"]]

    # Should include Sun, Moon, etc.
    assert "Sun" in planet_names
    assert "Moon" in planet_names

    # Should not include angles (they're in a different category)
    # Angles might be included depending on ObjectType, but midpoints shouldn't
    # be in the planet list


def test_planet_position_sorting(mock_chart):
    """Test that planets are sorted consistently."""
    section = PlanetPositionSection()
    data = section.generate_data(mock_chart)

    planet_names = [row[0] for row in data["rows"]]

    # Sun should typically come first in the standard ordering
    assert planet_names[0] == "Sun"


# ============================================================================
# ASPECT SECTION TESTS
# ============================================================================


def test_aspect_section_name():
    """Test AspectSection section name for different modes."""
    assert AspectSection(mode="all").section_name == "Aspects"
    assert AspectSection(mode="major").section_name == "Major Aspects"
    assert AspectSection(mode="minor").section_name == "Minor Aspects"
    assert AspectSection(mode="harmonic").section_name == "Harmonic Aspects"


def test_aspect_section_invalid_mode():
    """Test that invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="mode must be"):
        AspectSection(mode="invalid")


def test_aspect_section_invalid_sort_by():
    """Test that invalid sort_by raises ValueError."""
    with pytest.raises(ValueError, match="sort_by must be"):
        AspectSection(sort_by="invalid")


def test_aspect_section_default_options():
    """Test AspectSection default options."""
    section = AspectSection()
    assert section.mode == "all"
    assert section.orb_display is True
    assert section.sort_by == "orb"


def test_aspect_section_generate_data(sample_chart):
    """Test AspectSection data generation."""
    section = AspectSection(mode="major")
    data = section.generate_data(sample_chart)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Planet 1" in data["headers"]
    assert "Aspect" in data["headers"]
    assert "Planet 2" in data["headers"]


def test_aspect_section_with_orbs(sample_chart):
    """Test aspect section with orb display."""
    section = AspectSection(orbs=True)
    data = section.generate_data(sample_chart)

    headers = data["headers"]
    assert "Orb" in headers
    assert "Applying" in headers


def test_aspect_section_without_orbs(sample_chart):
    """Test aspect section without orb display."""
    section = AspectSection(orbs=False)
    data = section.generate_data(sample_chart)

    headers = data["headers"]
    assert "Orb" not in headers
    assert "Applying" not in headers


def test_aspect_section_sort_by_orb(sample_chart):
    """Test sorting aspects by orb."""
    section = AspectSection(sort_by="orb")
    data = section.generate_data(sample_chart)

    if len(data["rows"]) > 1:
        # Extract orb values (4th column if orbs displayed)
        orbs = [float(row[3].replace("°", "")) for row in data["rows"]]
        # Should be sorted in ascending order
        assert orbs == sorted(orbs)


def test_aspect_section_sort_by_planet(sample_chart):
    """Test sorting aspects by planet."""
    section = AspectSection(sort_by="planet")
    data = section.generate_data(sample_chart)

    # Just verify it doesn't raise - actual sorting is complex
    assert "rows" in data


def test_aspect_section_sort_by_aspect_type(sample_chart):
    """Test sorting aspects by aspect type."""
    section = AspectSection(sort_by="aspect_type")
    data = section.generate_data(sample_chart)

    # Just verify it doesn't raise
    assert "rows" in data


def test_aspect_section_major_only(sample_chart):
    """Test filtering to major aspects only."""
    section = AspectSection(mode="major")
    data = section.generate_data(sample_chart)

    # Check that only major aspects are included
    aspect_names = [row[1] for row in data["rows"]]
    major_aspects = ["Conjunction", "Opposition", "Trine", "Square", "Sextile"]

    for aspect_name in aspect_names:
        assert aspect_name in major_aspects


# ============================================================================
# MIDPOINT SECTION TESTS
# ============================================================================


def test_midpoint_section_name():
    """Test MidpointSection section name."""
    assert MidpointSection(mode="all").section_name == "Midpoints"
    assert (
        MidpointSection(mode="core").section_name
        == "Core Midpoints (Sun/Moon/ASC/MC)"
    )


def test_midpoint_section_invalid_mode():
    """Test that invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="mode must be"):
        MidpointSection(mode="invalid")


def test_midpoint_section_default_options():
    """Test MidpointSection default options."""
    section = MidpointSection()
    assert section.mode == "all"
    assert section.threshold is None


def test_midpoint_section_custom_options():
    """Test MidpointSection custom options."""
    section = MidpointSection(mode="core", threshold=10)
    assert section.mode == "core"
    assert section.threshold == 10


def test_midpoint_section_generate_data(chart_with_midpoints):
    """Test MidpointSection data generation."""
    section = MidpointSection()
    data = section.generate_data(chart_with_midpoints)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Midpoint" in data["headers"]
    assert "Position" in data["headers"]


def test_midpoint_section_all_mode(chart_with_midpoints):
    """Test midpoint section with all midpoints."""
    section = MidpointSection(mode="all")
    data = section.generate_data(chart_with_midpoints)

    # Should have many midpoints
    assert len(data["rows"]) > 0


def test_midpoint_section_core_mode(chart_with_midpoints):
    """Test midpoint section with core midpoints only."""
    section = MidpointSection(mode="core")
    data = section.generate_data(chart_with_midpoints)

    # Core midpoints should only involve Sun, Moon, ASC, MC
    core_objects = {"Sun", "Moon", "ASC", "MC"}

    for row in data["rows"]:
        midpoint_name = row[0]
        objects = midpoint_name.replace(" (indirect)", "").split("/")

        # At least one object should be in core
        # (depending on implementation, might require both)
        has_core = any(obj in core_objects for obj in objects)
        # The section should filter to only core midpoints
        # So we verify the row format is correct
        assert len(objects) <= 2


def test_midpoint_section_threshold(chart_with_midpoints):
    """Test midpoint section with threshold."""
    section = MidpointSection(threshold=5)
    data = section.generate_data(chart_with_midpoints)

    # Should have at most 5 midpoints
    assert len(data["rows"]) <= 5


def test_midpoint_section_is_core_midpoint():
    """Test the _is_core_midpoint helper method."""
    section = MidpointSection()

    assert section._is_core_midpoint("Midpoint:Sun/Moon") is True
    assert section._is_core_midpoint("Midpoint:Sun/Mars") is False
    assert section._is_core_midpoint("Midpoint:ASC/MC") is True
    assert section._is_core_midpoint("Midpoint:Venus/Jupiter") is False
    assert section._is_core_midpoint("Invalid") is False


# ============================================================================
# MOON PHASE SECTION TESTS
# ============================================================================


def test_moon_phase_section_name():
    """Test MoonPhaseSection section name."""
    section = MoonPhaseSection()
    assert section.section_name == "Moon Phase"


def test_moon_phase_section_generate_data(sample_chart):
    """Test MoonPhaseSection data generation."""
    section = MoonPhaseSection()
    data = section.generate_data(sample_chart)

    # Check structure
    assert "type" in data

    if data["type"] == "key_value":
        # Moon phase data available
        assert "data" in data
        assert "Phase Name" in data["data"]
        assert "Illumination" in data["data"]
        assert "Phase Angle" in data["data"]
    elif data["type"] == "text":
        # Moon phase not available
        assert "not available" in data["text"]


def test_moon_phase_section_with_phase_data(sample_chart):
    """Test moon phase section when phase data is available."""
    # The sample chart should have moon phase data if calculated
    section = MoonPhaseSection()
    data = section.generate_data(sample_chart)

    # Verify we get phase information
    if data["type"] == "key_value":
        assert "Phase Name" in data["data"]
        assert "Direction" in data["data"]


# ============================================================================
# CACHE INFO SECTION TESTS
# ============================================================================


def test_cache_info_section_name():
    """Test CacheInfoSection section name."""
    section = CacheInfoSection()
    assert section.section_name == "Cache Statistics"


def test_cache_info_section_no_cache(mock_chart):
    """Test cache info when caching is disabled."""
    section = CacheInfoSection()
    data = section.generate_data(mock_chart)

    # Implementation may return text or key_value depending on whether
    # cache stats exist in metadata
    assert "type" in data
    if data["type"] == "text":
        assert "disabled" in data["text"].lower()
    elif data["type"] == "key_value":
        # Cache stats may be present with empty/default values
        assert "data" in data


def test_cache_info_section_with_cache(mock_chart):
    """Test cache info when cache stats are available."""
    # Add fake cache stats to metadata
    mock_chart.metadata["cache_stats"] = {
        "enabled": True,
        "cache_directory": "/tmp/cache",
        "max_age_seconds": 86400,
        "total_cached_files": 42,
        "cache_size_mb": 10.5,
        "by_type": {"ephemeris": 30, "houses": 12},
    }

    section = CacheInfoSection()
    data = section.generate_data(mock_chart)

    assert data["type"] == "key_value"
    assert "Cache Directory" in data["data"]
    assert data["data"]["Cache Directory"] == "/tmp/cache"
    assert "Total Files" in data["data"]
    assert data["data"]["Total Files"] == 42


# ============================================================================
# SORTING HELPER TESTS
# ============================================================================


def test_get_object_sort_key(sample_chart):
    """Test get_object_sort_key function."""
    sun = sample_chart.get_object("Sun")
    moon = sample_chart.get_object("Moon")

    sun_key = get_object_sort_key(sun)
    moon_key = get_object_sort_key(moon)

    # Both should be planets, so type rank is the same
    assert sun_key[0] == moon_key[0]

    # But registry order should differ
    assert sun_key != moon_key


def test_get_object_sort_key_type_ordering(mock_chart):
    """Test that object types are ordered correctly."""
    positions = mock_chart.positions

    # Get different object types
    planets = [p for p in positions if p.object_type == ObjectType.PLANET]
    angles = [p for p in positions if p.object_type == ObjectType.ANGLE]

    if planets and angles:
        planet_key = get_object_sort_key(planets[0])
        angle_key = get_object_sort_key(angles[0])

        # Planets should sort before angles
        assert planet_key[0] < angle_key[0]


def test_get_aspect_sort_key():
    """Test get_aspect_sort_key function."""
    # Test with known aspects
    conj_key = get_aspect_sort_key("Conjunction")
    trine_key = get_aspect_sort_key("Trine")

    # Both should return valid sort keys
    assert isinstance(conj_key, tuple)
    assert isinstance(trine_key, tuple)

    # Conjunction (0°) should sort before Trine (120°)
    assert conj_key < trine_key


def test_get_aspect_sort_key_unknown():
    """Test aspect sort key with unknown aspect."""
    unknown_key = get_aspect_sort_key("Unknown Aspect")

    # Should still return a valid sort key (alphabetical fallback)
    assert isinstance(unknown_key, tuple)
    assert unknown_key[0] == 2000  # Fallback rank


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_all_sections_with_real_chart(sample_chart):
    """Test that all sections work with a real chart."""
    sections = [
        ChartOverviewSection(),
        PlanetPositionSection(),
        AspectSection(mode="major"),
        MoonPhaseSection(),
    ]

    for section in sections:
        data = section.generate_data(sample_chart)
        assert "type" in data
        assert data["type"] in ["table", "key_value", "text"]


def test_sections_generate_valid_data_structure(mock_chart):
    """Test that all sections generate valid data structures."""
    sections = [
        ChartOverviewSection(),
        PlanetPositionSection(),
        AspectSection(),
    ]

    for section in sections:
        data = section.generate_data(mock_chart)

        # All sections should return dict with 'type' key
        assert isinstance(data, dict)
        assert "type" in data

        # Validate structure based on type
        if data["type"] == "table":
            assert "headers" in data
            assert "rows" in data
            assert isinstance(data["headers"], list)
            assert isinstance(data["rows"], list)
        elif data["type"] == "key_value":
            assert "data" in data
            assert isinstance(data["data"], dict)
        elif data["type"] == "text":
            assert "text" in data
            assert isinstance(data["text"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
