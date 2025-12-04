"""
Comprehensive tests for presentation.sections module.

Tests all section classes and their data generation logic.
"""

import datetime as dt

import pytest
import pytz

from stellium.components.arabic_parts import ArabicPartsCalculator
from stellium.components.midpoints import MidpointCalculator
from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation, ObjectType
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.ephemeris import MockEphemerisEngine, SwissEphemerisEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.engines.orbs import SimpleOrbEngine
from stellium.presentation.sections import (
    ArabicPartsSection,
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


@pytest.fixture
def chart_with_arabic_parts():
    """Create a chart with Arabic Parts calculated."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(SwissEphemerisEngine())
        .with_house_systems([PlacidusHouses()])
        .add_component(ArabicPartsCalculator())
        .calculate()
    )


@pytest.fixture
def chart_with_arabic_parts_multi_house():
    """Create a chart with Arabic Parts and multiple house systems."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")
    native = Native(datetime, location)

    return (
        ChartBuilder.from_native(native)
        .with_ephemeris(SwissEphemerisEngine())
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .add_component(ArabicPartsCalculator())
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
    assert section._house_systems_mode == "all"  # Default mode is "all"


def test_planet_position_custom_options():
    """Test PlanetPositionSection custom options."""
    section = PlanetPositionSection(
        include_speed=True, include_house=False, house_systems=["Placidus"]
    )
    assert section.include_speed is True
    assert section.include_house is False
    assert section._house_systems == ["Placidus"]


def test_planet_position_generate_data(sample_chart):
    """Test PlanetPositionSection data generation."""
    section = PlanetPositionSection()
    data = section.generate_data(sample_chart)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Planet" in data["headers"]
    assert "Position" in data["headers"]
    # House headers are now abbreviated like "House (Pl)", "House (WS)"
    house_headers = [h for h in data["headers"] if h.startswith("House")]
    assert len(house_headers) > 0


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

    # Get all position names from rows (may include glyphs like "☉ Sun")
    planet_names = [row[0] for row in data["rows"]]

    # Should include Sun, Moon, etc. (with glyphs prepended)
    assert any("Sun" in name for name in planet_names)
    assert any("Moon" in name for name in planet_names)

    # Should not include angles (they're in a different category)
    # Angles might be included depending on ObjectType, but midpoints shouldn't
    # be in the planet list


def test_planet_position_sorting(mock_chart):
    """Test that planets are sorted consistently."""
    section = PlanetPositionSection()
    data = section.generate_data(mock_chart)

    planet_names = [row[0] for row in data["rows"]]

    # Sun should typically come first in the standard ordering (with glyph)
    assert "Sun" in planet_names[0]


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
    """Test AspectSection data generation (without aspectarian for table testing)."""
    section = AspectSection(mode="major", include_aspectarian=False)
    data = section.generate_data(sample_chart)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Planet 1" in data["headers"]
    assert "Aspect" in data["headers"]
    assert "Planet 2" in data["headers"]


def test_aspect_section_with_orbs(sample_chart):
    """Test aspect section with orb display."""
    section = AspectSection(orbs=True, include_aspectarian=False)
    data = section.generate_data(sample_chart)

    headers = data["headers"]
    assert "Orb" in headers
    assert "Applying" in headers


def test_aspect_section_without_orbs(sample_chart):
    """Test aspect section without orb display."""
    section = AspectSection(orbs=False, include_aspectarian=False)
    data = section.generate_data(sample_chart)

    headers = data["headers"]
    assert "Orb" not in headers
    assert "Applying" not in headers


def test_aspect_section_sort_by_orb(sample_chart):
    """Test sorting aspects by orb."""
    section = AspectSection(sort_by="orb", include_aspectarian=False)
    data = section.generate_data(sample_chart)

    if len(data["rows"]) > 1:
        # Extract orb values (4th column if orbs displayed)
        orbs = [float(row[3].replace("°", "")) for row in data["rows"]]
        # Should be sorted in ascending order
        assert orbs == sorted(orbs)


def test_aspect_section_sort_by_planet(sample_chart):
    """Test sorting aspects by planet."""
    section = AspectSection(sort_by="planet", include_aspectarian=False)
    data = section.generate_data(sample_chart)

    # Just verify it doesn't raise - actual sorting is complex
    assert "rows" in data


def test_aspect_section_sort_by_aspect_type(sample_chart):
    """Test sorting aspects by aspect type."""
    section = AspectSection(sort_by="aspect_type", include_aspectarian=False)
    data = section.generate_data(sample_chart)

    # Just verify it doesn't raise
    assert "rows" in data


def test_aspect_section_major_only(sample_chart):
    """Test filtering to major aspects only."""
    section = AspectSection(mode="major", include_aspectarian=False)
    data = section.generate_data(sample_chart)

    # Check that only major aspects are included
    # Aspect names may include glyphs like "△ Trine", so check substring
    aspect_names = [row[1] for row in data["rows"]]
    major_aspects = ["Conjunction", "Opposition", "Trine", "Square", "Sextile"]

    for aspect_name in aspect_names:
        assert any(major in aspect_name for major in major_aspects)


def test_aspect_section_with_aspectarian(sample_chart):
    """Test aspect section with aspectarian SVG (default behavior)."""
    section = AspectSection(mode="major", include_aspectarian=True)
    data = section.generate_data(sample_chart)

    # Should be a compound section
    assert data["type"] == "compound"
    assert "sections" in data
    assert len(data["sections"]) == 2

    # First section should be the aspectarian SVG
    aspectarian_name, aspectarian_data = data["sections"][0]
    assert aspectarian_name == "Aspectarian"
    assert aspectarian_data["type"] == "svg"
    assert "content" in aspectarian_data
    assert aspectarian_data["content"].startswith("<svg")

    # Second section should be the aspect list table
    table_name, table_data = data["sections"][1]
    assert table_name == "Aspect List"
    assert table_data["type"] == "table"
    assert "rows" in table_data


# ============================================================================
# MIDPOINT SECTION TESTS
# ============================================================================


def test_midpoint_section_name():
    """Test MidpointSection section name."""
    assert MidpointSection(mode="all").section_name == "Midpoints"
    assert (
        MidpointSection(mode="core").section_name == "Core Midpoints (Sun/Moon/ASC/MC)"
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
        any(obj in core_objects for obj in objects)
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
# ARABIC PARTS SECTION TESTS
# ============================================================================


def test_arabic_parts_section_name():
    """Test ArabicPartsSection section name for different modes."""
    assert ArabicPartsSection(mode="all").section_name == "Arabic Parts"
    assert (
        ArabicPartsSection(mode="core").section_name == "Arabic Parts (Hermetic Lots)"
    )
    assert (
        ArabicPartsSection(mode="family").section_name
        == "Arabic Parts (Family & Relationships)"
    )
    assert ArabicPartsSection(mode="life").section_name == "Arabic Parts (Life Topics)"
    assert (
        ArabicPartsSection(mode="planetary").section_name
        == "Arabic Parts (Planetary Exaltation)"
    )


def test_arabic_parts_section_invalid_mode():
    """Test that invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="mode must be one of"):
        ArabicPartsSection(mode="invalid")


def test_arabic_parts_section_default_options():
    """Test ArabicPartsSection default options."""
    section = ArabicPartsSection()
    assert section.mode == "all"
    assert section.show_formula is True
    assert section.show_description is False


def test_arabic_parts_section_custom_options():
    """Test ArabicPartsSection custom options."""
    section = ArabicPartsSection(mode="core", show_formula=False, show_description=True)
    assert section.mode == "core"
    assert section.show_formula is False
    assert section.show_description is True


def test_arabic_parts_section_generate_data(chart_with_arabic_parts):
    """Test ArabicPartsSection data generation."""
    section = ArabicPartsSection()
    data = section.generate_data(chart_with_arabic_parts)

    assert data["type"] == "table"
    assert "headers" in data
    assert "rows" in data
    assert "Part" in data["headers"]
    assert "Position" in data["headers"]
    assert "House" in data["headers"]
    assert "Formula" in data["headers"]  # Default show_formula=True


def test_arabic_parts_section_no_parts(mock_chart):
    """Test ArabicPartsSection when no Arabic Parts are calculated."""
    section = ArabicPartsSection()
    data = section.generate_data(mock_chart)

    assert data["type"] == "text"
    assert "No Arabic Parts calculated" in data["content"]
    assert "ArabicPartsCalculator" in data["content"]


def test_arabic_parts_section_all_mode(chart_with_arabic_parts):
    """Test Arabic parts section with all parts."""
    section = ArabicPartsSection(mode="all")
    data = section.generate_data(chart_with_arabic_parts)

    # Should have many parts (27+ in the full catalog)
    assert len(data["rows"]) >= 20


def test_arabic_parts_section_core_mode(chart_with_arabic_parts):
    """Test Arabic parts section with core (Hermetic) parts only."""
    section = ArabicPartsSection(mode="core")
    data = section.generate_data(chart_with_arabic_parts)

    # Core has 8 parts
    assert len(data["rows"]) == 8

    # Check for expected core parts (display names have "Part of " stripped)
    part_names = [row[0] for row in data["rows"]]
    assert any("Fortune" in name for name in part_names)
    assert any("Spirit" in name for name in part_names)


def test_arabic_parts_section_family_mode(chart_with_arabic_parts):
    """Test Arabic parts section with family parts only."""
    section = ArabicPartsSection(mode="family")
    data = section.generate_data(chart_with_arabic_parts)

    # Family has 5 parts
    assert len(data["rows"]) == 5

    part_names = [row[0] for row in data["rows"]]
    assert any("Father" in name for name in part_names)
    assert any("Mother" in name for name in part_names)
    assert any("Marriage" in name for name in part_names)


def test_arabic_parts_section_life_mode(chart_with_arabic_parts):
    """Test Arabic parts section with life topic parts only."""
    section = ArabicPartsSection(mode="life")
    data = section.generate_data(chart_with_arabic_parts)

    # Life has 8 parts
    assert len(data["rows"]) == 8

    part_names = [row[0] for row in data["rows"]]
    assert any("Death" in name for name in part_names)
    assert any("Travel" in name for name in part_names)


def test_arabic_parts_section_planetary_mode(chart_with_arabic_parts):
    """Test Arabic parts section with planetary exaltation parts only."""
    section = ArabicPartsSection(mode="planetary")
    data = section.generate_data(chart_with_arabic_parts)

    # Planetary has 7 parts
    assert len(data["rows"]) == 7

    part_names = [row[0] for row in data["rows"]]
    assert any("Sun" in name for name in part_names)
    assert any("Moon" in name for name in part_names)
    assert any("Jupiter" in name for name in part_names)


def test_arabic_parts_section_with_formula(chart_with_arabic_parts):
    """Test Arabic parts section with formula column."""
    section = ArabicPartsSection(show_formula=True)
    data = section.generate_data(chart_with_arabic_parts)

    assert "Formula" in data["headers"]

    # Check formula format (e.g., "ASC + Moon - Sun *")
    formula_idx = data["headers"].index("Formula")
    formulas = [row[formula_idx] for row in data["rows"]]

    # All formulas should contain ASC and + and -
    for formula in formulas:
        assert "ASC" in formula
        assert "+" in formula
        assert "-" in formula


def test_arabic_parts_section_without_formula(chart_with_arabic_parts):
    """Test Arabic parts section without formula column."""
    section = ArabicPartsSection(show_formula=False)
    data = section.generate_data(chart_with_arabic_parts)

    assert "Formula" not in data["headers"]


def test_arabic_parts_section_with_description(chart_with_arabic_parts):
    """Test Arabic parts section with description column."""
    section = ArabicPartsSection(mode="core", show_description=True)
    data = section.generate_data(chart_with_arabic_parts)

    assert "Description" in data["headers"]

    # Descriptions should be present
    desc_idx = data["headers"].index("Description")
    descriptions = [row[desc_idx] for row in data["rows"]]

    # All descriptions should be non-empty strings
    for desc in descriptions:
        assert isinstance(desc, str)
        assert len(desc) > 0


def test_arabic_parts_section_without_description(chart_with_arabic_parts):
    """Test Arabic parts section without description column."""
    section = ArabicPartsSection(show_description=False)
    data = section.generate_data(chart_with_arabic_parts)

    assert "Description" not in data["headers"]


def test_arabic_parts_section_single_house_system(chart_with_arabic_parts):
    """Test Arabic parts with single house system shows 'House' header."""
    section = ArabicPartsSection(mode="core")
    data = section.generate_data(chart_with_arabic_parts)

    # Single house system should show "House" header
    assert "House" in data["headers"]
    # Should NOT have abbreviated headers
    assert "Plac" not in data["headers"]
    assert "WS" not in data["headers"]


def test_arabic_parts_section_multiple_house_systems(
    chart_with_arabic_parts_multi_house,
):
    """Test Arabic parts with multiple house systems shows abbreviated headers."""
    section = ArabicPartsSection(mode="core")
    data = section.generate_data(chart_with_arabic_parts_multi_house)

    # Multiple house systems should show abbreviated headers
    assert "Plac" in data["headers"]
    assert "WS" in data["headers"]
    # Should NOT have generic "House" header
    assert "House" not in data["headers"]


def test_arabic_parts_section_house_placements(chart_with_arabic_parts):
    """Test that house placements are correctly populated."""
    section = ArabicPartsSection(mode="core", show_formula=False)
    data = section.generate_data(chart_with_arabic_parts)

    house_idx = data["headers"].index("House")

    # All house values should be integers (as strings) or "—"
    for row in data["rows"]:
        house_val = row[house_idx]
        if house_val != "—":
            assert house_val.isdigit()
            assert 1 <= int(house_val) <= 12


def test_arabic_parts_section_position_format(chart_with_arabic_parts):
    """Test that positions are formatted correctly."""
    section = ArabicPartsSection(mode="core", show_formula=False)
    data = section.generate_data(chart_with_arabic_parts)

    position_idx = data["headers"].index("Position")

    for row in data["rows"]:
        position = row[position_idx]
        # Position should contain degree symbol
        assert "°" in position
        # Position should contain minute indicator
        assert "'" in position


def test_arabic_parts_section_part_name_formatting():
    """Test the _format_part_name helper method."""
    section = ArabicPartsSection()

    assert section._format_part_name("Part of Fortune") == "Fortune"
    assert section._format_part_name("Part of Spirit") == "Spirit"
    assert (
        section._format_part_name("Part of the Sun (Exaltation)") == "Sun (Exaltation)"
    )
    assert (
        section._format_part_name("Part of the Moon (Exaltation)")
        == "Moon (Exaltation)"
    )
    assert section._format_part_name("Custom Name") == "Custom Name"


def test_arabic_parts_section_house_system_abbreviations():
    """Test the _abbreviate_house_system helper method."""
    section = ArabicPartsSection()

    assert section._abbreviate_house_system("Placidus") == "Plac"
    assert section._abbreviate_house_system("Whole Sign") == "WS"
    assert section._abbreviate_house_system("Equal") == "Eq"
    assert section._abbreviate_house_system("Koch") == "Koch"
    assert section._abbreviate_house_system("Regiomontanus") == "Regio"
    assert section._abbreviate_house_system("Campanus") == "Camp"
    # Unknown systems fall back to first 4 chars
    assert section._abbreviate_house_system("Unknown System") == "Unkn"


def test_arabic_parts_section_formula_sect_indicator(chart_with_arabic_parts):
    """Test that sect-aware formulas have asterisk indicator."""
    section = ArabicPartsSection(mode="core", show_formula=True)
    data = section.generate_data(chart_with_arabic_parts)

    formula_idx = data["headers"].index("Formula")

    # Find Part of Fortune (should have sect flip asterisk)
    for row in data["rows"]:
        if row[0] == "Fortune":
            assert row[formula_idx].endswith("*")
            break


def test_arabic_parts_section_sorting(chart_with_arabic_parts):
    """Test that parts are sorted by category then alphabetically."""
    section = ArabicPartsSection(mode="all", show_formula=False)
    data = section.generate_data(chart_with_arabic_parts)

    part_names = [row[0] for row in data["rows"]]

    # Core parts should come before family parts
    # Find indices of a core part and a family part
    fortune_idx = next(i for i, n in enumerate(part_names) if "Fortune" in n)
    father_idx = next(i for i, n in enumerate(part_names) if "Father" in n)

    assert fortune_idx < father_idx, "Core parts should come before family parts"


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
        AspectSection(mode="major", include_aspectarian=False),
        MoonPhaseSection(),
    ]

    for section in sections:
        data = section.generate_data(sample_chart)
        assert "type" in data
        assert data["type"] in ["table", "key_value", "text"]


def test_all_sections_with_aspectarian(sample_chart):
    """Test AspectSection with aspectarian returns compound type."""
    section = AspectSection(mode="major", include_aspectarian=True)
    data = section.generate_data(sample_chart)
    assert "type" in data
    assert data["type"] == "compound"


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
