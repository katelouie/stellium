"""Tests for AtlasBuilder chart atlas generation."""

import datetime as dt
import os
import tempfile

import pytest

from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.visualization.atlas import AtlasBuilder, AtlasConfig, AtlasEntry

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_native():
    """Create a sample native for testing."""
    return Native(
        datetime_input=dt.datetime(1994, 1, 6, 11, 47),
        location_input=ChartLocation(
            latitude=37.4419,
            longitude=-122.143,
            name="Palo Alto, CA",
            timezone="America/Los_Angeles",
        ),
        name="Test Person",
    )


@pytest.fixture
def sample_natives():
    """Create multiple sample natives for testing."""
    locations = [
        ("New York, NY", 40.7128, -74.0060, "America/New_York"),
        ("London, UK", 51.5074, -0.1278, "Europe/London"),
        ("Tokyo, Japan", 35.6762, 139.6503, "Asia/Tokyo"),
    ]

    natives = []
    for i, (name, lat, lon, tz) in enumerate(locations):
        native = Native(
            datetime_input=dt.datetime(1990 + i, 6, 15, 12, 0),
            location_input=ChartLocation(
                latitude=lat,
                longitude=lon,
                name=name,
                timezone=tz,
            ),
            name=f"Person {i + 1}",
        )
        natives.append(native)

    return natives


# =============================================================================
# Builder Tests
# =============================================================================


def test_builder_initialization():
    """Test AtlasBuilder initializes with correct defaults."""
    builder = AtlasBuilder()

    # Check internal state
    assert builder._entries == []
    assert builder._default_chart_type == "wheel"
    assert builder._theme == "atlas"
    assert builder._show_header is True
    assert builder._page_size == "letter"
    assert builder._title is None


def test_add_native(sample_native):
    """Test adding a single native."""
    builder = AtlasBuilder().add_native(sample_native)

    assert len(builder._entries) == 1
    assert builder._entries[0].native == sample_native
    assert builder._entries[0].chart_type == "wheel"


def test_add_natives(sample_natives):
    """Test adding multiple natives."""
    builder = AtlasBuilder().add_natives(sample_natives)

    assert len(builder._entries) == 3


def test_add_entry_with_custom_type(sample_native):
    """Test adding entry with custom chart type."""
    builder = AtlasBuilder().add_entry(sample_native, chart_type="dial", degrees=90)

    assert len(builder._entries) == 1
    assert builder._entries[0].chart_type == "dial"
    assert builder._entries[0].chart_options.get("degrees") == 90


def test_with_chart_type():
    """Test setting default chart type."""
    builder = AtlasBuilder().with_chart_type("dial", degrees=45)

    assert builder._default_chart_type == "dial"
    assert builder._default_chart_options.get("degrees") == 45


def test_with_invalid_chart_type():
    """Test that invalid chart type raises error."""
    with pytest.raises(ValueError, match="Invalid chart_type"):
        AtlasBuilder().with_chart_type("invalid")


def test_with_theme():
    """Test setting theme."""
    builder = AtlasBuilder().with_theme("midnight")

    assert builder._theme == "midnight"


def test_with_header():
    """Test header configuration."""
    builder = AtlasBuilder().with_header(True)
    assert builder._show_header is True

    builder = AtlasBuilder().with_header(False)
    assert builder._show_header is False

    builder = AtlasBuilder().without_header()
    assert builder._show_header is False


def test_with_page_size():
    """Test page size configuration."""
    builder = AtlasBuilder().with_page_size("a4")
    assert builder._page_size == "a4"

    builder = AtlasBuilder().with_page_size("half-letter")
    assert builder._page_size == "half-letter"


def test_with_invalid_page_size():
    """Test that invalid page size raises error."""
    with pytest.raises(ValueError, match="Invalid page_size"):
        AtlasBuilder().with_page_size("invalid")


def test_with_title_page():
    """Test title page configuration."""
    builder = AtlasBuilder().with_title_page("My Chart Atlas")

    assert builder._title == "My Chart Atlas"


def test_fluent_chaining(sample_natives):
    """Test fluent method chaining."""
    builder = (
        AtlasBuilder()
        .add_natives(sample_natives)
        .with_chart_type("dial", degrees=90)
        .with_theme("midnight")
        .with_header()
        .with_page_size("a4")
        .with_title_page("Test Atlas")
    )

    assert len(builder._entries) == 3
    assert builder._default_chart_type == "dial"
    assert builder._theme == "midnight"
    assert builder._show_header is True
    assert builder._page_size == "a4"
    assert builder._title == "Test Atlas"


def test_save_without_entries():
    """Test that save raises error without entries."""
    with pytest.raises(ValueError, match="No entries added"):
        AtlasBuilder().save("test.pdf")


def test_render_without_entries():
    """Test that render raises error without entries."""
    with pytest.raises(ValueError, match="No entries added"):
        AtlasBuilder().render()


# =============================================================================
# Config Tests
# =============================================================================


def test_atlas_entry_defaults(sample_native):
    """Test AtlasEntry default values."""
    entry = AtlasEntry(native=sample_native)

    assert entry.native == sample_native
    assert entry.chart_type == "wheel"
    assert entry.chart_options == {}


def test_atlas_config_defaults():
    """Test AtlasConfig default values."""
    config = AtlasConfig()

    assert config.entries == []
    assert config.page_size == "letter"
    assert config.theme == "classic"
    assert config.show_header is True
    assert config.title is None
    assert config.filename == "atlas.pdf"


# =============================================================================
# Integration Tests (require typst)
# =============================================================================


def test_atlas_generation_wheel(sample_natives):
    """Test generating atlas with wheel charts."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name

    try:
        result = (
            AtlasBuilder()
            .add_natives(sample_natives)
            .with_theme("classic")
            .save(output_path)
        )

        assert result == output_path
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

        # Check it's a valid PDF (starts with %PDF-)
        with open(output_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_atlas_generation_dial(sample_natives):
    """Test generating atlas with dial charts."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name

    try:
        result = (
            AtlasBuilder()
            .add_natives(sample_natives)
            .with_chart_type("dial", degrees=90)
            .with_theme("midnight")
            .save(output_path)
        )

        assert result == output_path
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_atlas_with_title_page(sample_natives):
    """Test generating atlas with title page."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name

    try:
        result = (
            AtlasBuilder()
            .add_natives(sample_natives)
            .with_title_page("Famous Scientists")
            .save(output_path)
        )

        assert result == output_path
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_atlas_render_bytes(sample_native):
    """Test rendering atlas to bytes."""
    pdf_bytes = AtlasBuilder().add_native(sample_native).render()

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:5] == b"%PDF-"


def test_atlas_with_notable():
    """Test adding notable by name."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name

    try:
        result = AtlasBuilder().add_notable("Albert Einstein").save(output_path)

        assert result == output_path
        assert os.path.exists(output_path)

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_add_notable_not_found():
    """Test that adding unknown notable raises error."""
    with pytest.raises(ValueError, match="Notable not found"):
        AtlasBuilder().add_notable("Unknown Person 12345")


# =============================================================================
# Factory Method Tests
# =============================================================================


def test_from_all_notables():
    """Test creating atlas from all notables."""
    builder = AtlasBuilder.from_all_notables()

    # Should have multiple entries
    assert len(builder._entries) > 0

    # Check they're sorted alphabetically by default
    names = [e.native.name for e in builder._entries]
    assert names == sorted(names)


def test_from_all_notables_with_category():
    """Test filtering notables by category."""
    builder = AtlasBuilder.from_all_notables(category="scientist")

    # Should have entries (assuming scientists exist in registry)
    assert len(builder._entries) > 0

    # All should be scientists
    for entry in builder._entries:
        assert entry.native.category == "scientist"


def test_from_all_notables_sorted_by_date():
    """Test sorting notables by date."""
    builder = AtlasBuilder.from_all_notables(sort_by="date")

    # Should have entries
    assert len(builder._entries) > 0

    # Check dates are in order (chronological)
    dates = [e.native.datetime.utc_datetime for e in builder._entries]
    assert dates == sorted(dates)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
