"""
Comprehensive tests for visualization modules.

This test suite covers:
- ChartRenderer: Core rendering engine with coordinate transformations
- Visualization Layers: ZodiacLayer, HouseCuspLayer, PlanetLayer, AspectLayer, etc.
- draw_chart(): High-level chart drawing function
- SVG generation and output
- Theme and palette system
- Edge cases and error handling
"""

import datetime as dt
import math
import os
import tempfile
from unittest.mock import Mock

import pytest
import svgwrite

from stellium.core.builder import ChartBuilder
from stellium.core.models import (
    CalculatedChart,
    ChartLocation,
    ObjectType,
)
from stellium.core.native import Native
from stellium.engines.houses import PlacidusHouses, WholeSignHouses
from stellium.visualization.core import ChartRenderer, get_display_name, get_glyph
from stellium.visualization.layers import (
    AngleLayer,
    AspectCountsLayer,
    AspectLayer,
    ChartInfoLayer,
    ChartShapeLayer,
    ElementModalityTableLayer,
    HouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from stellium.visualization.palettes import ZodiacPalette

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def test_chart() -> CalculatedChart:
    """Create a test chart with real data."""
    native = Native(
        dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=37.7749,
            longitude=-122.4194,
            name="San Francisco, CA",
            timezone="America/Los_Angeles",
        ),
    )
    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )
    return chart


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for SVG output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def renderer() -> ChartRenderer:
    """Create a standard ChartRenderer for testing."""
    return ChartRenderer(size=600, rotation=0)


@pytest.fixture
def mock_dwg():
    """Create a mock SVG drawing object."""
    dwg = Mock(spec=svgwrite.Drawing)
    dwg.add = Mock()
    # Add SVG element creation methods
    dwg.path = Mock(return_value=Mock())
    dwg.line = Mock(return_value=Mock())
    dwg.circle = Mock(return_value=Mock())
    dwg.text = Mock(return_value=Mock())
    dwg.rect = Mock(return_value=Mock())
    dwg.image = Mock(return_value=Mock())
    return dwg


# ============================================================================
# CHARTRENDERER TESTS
# ============================================================================


class TestChartRenderer:
    """Tests for the core ChartRenderer class."""

    def test_initialization_default(self):
        """Test ChartRenderer initialization with defaults."""
        renderer = ChartRenderer()
        assert renderer.size == 600
        assert renderer.rotation == 0
        assert renderer.center == 300

    def test_initialization_custom_size(self):
        """Test ChartRenderer initialization with custom size."""
        renderer = ChartRenderer(size=800)
        assert renderer.size == 800
        assert renderer.center == 400

    def test_initialization_custom_rotation(self):
        """Test ChartRenderer initialization with custom rotation."""
        renderer = ChartRenderer(rotation=90)
        assert renderer.rotation == 90

    def test_radii_calculation(self, renderer):
        """Test that radii are properly calculated."""
        assert "outer_border" in renderer.radii
        assert "zodiac_ring_outer" in renderer.radii
        assert "zodiac_ring_inner" in renderer.radii
        assert "house_number_ring" in renderer.radii
        assert "planet_ring" in renderer.radii

        # Check that radii are in descending order
        assert renderer.radii["outer_border"] > renderer.radii["zodiac_ring_outer"]
        assert renderer.radii["zodiac_ring_outer"] > renderer.radii["zodiac_ring_inner"]
        assert renderer.radii["zodiac_ring_inner"] > renderer.radii["house_number_ring"]

    def test_polar_to_cartesian_basic(self, renderer):
        """Test polar to Cartesian coordinate conversion."""
        # 0° Aries is at 9 o'clock position (180° SVG) with no rotation
        x, y = renderer.polar_to_cartesian(0, 100)
        assert abs(x - (renderer.center - 100)) < 0.1  # center - 100 (left)
        assert abs(y - renderer.center) < 0.1  # center

    def test_polar_to_cartesian_90_degrees(self, renderer):
        """Test polar conversion at 90 degrees."""
        # 90° astrological (Cancer) is at 6 o'clock position with no rotation
        x, y = renderer.polar_to_cartesian(90, 100)
        assert isinstance(x, float)
        assert isinstance(y, float)

    def test_polar_to_cartesian_180_degrees(self, renderer):
        """Test polar conversion at 180 degrees."""
        # 180° astrological (Libra) is at 3 o'clock position with no rotation
        x, y = renderer.polar_to_cartesian(180, 100)
        assert abs(x - (renderer.center + 100)) < 0.1  # center + 100 (right)
        assert abs(y - renderer.center) < 0.1  # center

    def test_polar_to_cartesian_270_degrees(self, renderer):
        """Test polar conversion at 270 degrees."""
        # 270° astrological (Capricorn) is at 12 o'clock position with no rotation
        x, y = renderer.polar_to_cartesian(270, 100)
        assert isinstance(x, float)
        assert isinstance(y, float)

    def test_polar_to_cartesian_with_rotation(self):
        """Test polar conversion with chart rotation."""
        renderer = ChartRenderer(rotation=90)
        # Rotation shifts the entire zodiac wheel
        x, y = renderer.polar_to_cartesian(0, 100)
        assert isinstance(x, float)
        assert isinstance(y, float)

    def test_astrological_to_svg_angle(self, renderer):
        """Test astrological to SVG angle conversion."""
        # 0° Aries should map to 180° SVG (9 o'clock)
        svg_angle = renderer.astrological_to_svg_angle(0)
        assert abs(svg_angle - 180) < 0.1

    def test_astrological_to_svg_angle_with_rotation(self):
        """Test angle conversion with rotation."""
        renderer = ChartRenderer(rotation=90)
        svg_angle = renderer.astrological_to_svg_angle(90)
        # With 90° rotation, 90° astrological should map to 180° SVG
        assert isinstance(svg_angle, int | float)


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Tests for helper functions in visualization.core."""

    def test_get_glyph_planet(self):
        """Test getting glyph for a planet."""
        result = get_glyph("Sun")
        assert "type" in result
        assert "value" in result
        assert result["type"] == "unicode"
        assert result["value"] == "☉"

    def test_get_glyph_moon(self):
        """Test getting glyph for Moon."""
        result = get_glyph("Moon")
        assert result["type"] == "unicode"
        assert result["value"] == "☽"

    def test_get_glyph_unknown(self):
        """Test getting glyph for unknown object falls back gracefully."""
        result = get_glyph("UnknownPlanet")
        assert "type" in result
        assert "value" in result
        assert result["type"] == "unicode"
        # Should return first 3 characters as fallback
        assert result["value"] == "Unk"

    def test_get_display_name(self):
        """Test getting display name for celestial objects."""
        # get_display_name returns the display name from registry, not the glyph
        assert get_display_name("Sun") == "Sun"
        assert get_display_name("Moon") == "Moon"
        assert get_display_name("ASC") == "ASC"  # No registry entry, returns original


# ============================================================================
# ZODIAC LAYER TESTS
# ============================================================================


class TestZodiacLayer:
    """Tests for ZodiacLayer."""

    def test_initialization_default(self):
        """Test ZodiacLayer initialization with defaults."""
        layer = ZodiacLayer()
        assert layer.palette == ZodiacPalette.GREY

    def test_initialization_custom_palette(self):
        """Test ZodiacLayer with custom palette."""
        layer = ZodiacLayer(palette=ZodiacPalette.ELEMENTAL)
        assert layer.palette == ZodiacPalette.ELEMENTAL

    def test_initialization_palette_from_string(self):
        """Test ZodiacLayer with palette as string."""
        layer = ZodiacLayer(palette="elemental")
        assert layer.palette == ZodiacPalette.ELEMENTAL

    def test_render(self, renderer, mock_dwg, test_chart):
        """Test ZodiacLayer rendering."""
        layer = ZodiacLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added elements to the drawing
        assert mock_dwg.add.called

    def test_render_with_style_override(self, renderer, mock_dwg, test_chart):
        """Test ZodiacLayer with style overrides."""
        layer = ZodiacLayer(style_override={"stroke": "blue"})
        layer.render(renderer, mock_dwg, test_chart)

        assert mock_dwg.add.called


# ============================================================================
# HOUSE CUSP LAYER TESTS
# ============================================================================


class TestHouseCuspLayer:
    """Tests for HouseCuspLayer."""

    def test_initialization(self):
        """Test HouseCuspLayer initialization."""
        layer = HouseCuspLayer(house_system_name="Placidus")
        assert layer is not None
        assert layer.system_name == "Placidus"

    def test_render_with_houses(self, renderer, mock_dwg, test_chart):
        """Test HouseCuspLayer rendering when houses exist."""
        layer = HouseCuspLayer(house_system_name="Placidus")
        layer.render(renderer, mock_dwg, test_chart)

        # Should have rendered house cusps
        assert mock_dwg.add.called

    def test_render_without_houses(self, renderer, mock_dwg):
        """Test HouseCuspLayer when no houses are calculated."""
        # Create a minimal chart without houses
        native = Native(
            dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
            ChartLocation(0, 0, "Test", "UTC"),
        )
        chart = ChartBuilder.from_native(native).calculate()

        layer = HouseCuspLayer(house_system_name="Placidus")
        # Should not crash when no houses are present (will print warning)
        layer.render(renderer, mock_dwg, chart)


# ============================================================================
# PLANET LAYER TESTS
# ============================================================================


class TestPlanetLayer:
    """Tests for PlanetLayer."""

    def test_initialization(self, test_chart):
        """Test PlanetLayer initialization."""
        planets = [
            p
            for p in test_chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]
        layer = PlanetLayer(planet_set=planets)
        assert layer is not None
        assert layer.planets == planets

    def test_render_with_planets(self, renderer, mock_dwg, test_chart):
        """Test PlanetLayer rendering."""
        planets = [
            p
            for p in test_chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]
        layer = PlanetLayer(planet_set=planets)
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added planet glyphs
        assert mock_dwg.add.called

    def test_render_filters_planets_only(self, renderer, mock_dwg, test_chart):
        """Test that PlanetLayer only renders planets (not angles)."""
        # Filter to planets only
        planets = [
            p for p in test_chart.positions if p.object_type == ObjectType.PLANET
        ]
        layer = PlanetLayer(planet_set=planets)
        layer.render(renderer, mock_dwg, test_chart)

        # Verify it filtered correctly (by checking it ran without error)
        assert mock_dwg.add.called


# ============================================================================
# ANGLE LAYER TESTS
# ============================================================================


class TestAngleLayer:
    """Tests for AngleLayer."""

    def test_initialization(self):
        """Test AngleLayer initialization."""
        layer = AngleLayer()
        assert layer is not None

    def test_render_with_angles(self, renderer, mock_dwg, test_chart):
        """Test AngleLayer rendering."""
        layer = AngleLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added angle markers
        assert mock_dwg.add.called


# ============================================================================
# ASPECT LAYER TESTS
# ============================================================================


class TestAspectLayer:
    """Tests for AspectLayer."""

    def test_initialization(self):
        """Test AspectLayer initialization."""
        layer = AspectLayer()
        assert layer is not None

    def test_render_with_aspects(self, renderer, mock_dwg, test_chart):
        """Test AspectLayer rendering when aspects exist."""
        layer = AspectLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have drawn aspect lines
        if test_chart.aspects:
            assert mock_dwg.add.called

    def test_render_without_aspects(self, renderer, mock_dwg):
        """Test AspectLayer when no aspects are calculated."""
        # Create a minimal chart without aspects
        native = Native(
            dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
            ChartLocation(0, 0, "Test", "UTC"),
        )
        chart = ChartBuilder.from_native(native).calculate()

        layer = AspectLayer()
        # Should not crash when no aspects are present
        layer.render(renderer, mock_dwg, chart)


# ============================================================================
# CHART INFO LAYER TESTS
# ============================================================================


class TestChartInfoLayer:
    """Tests for ChartInfoLayer."""

    def test_initialization_default(self):
        """Test ChartInfoLayer initialization with defaults."""
        layer = ChartInfoLayer()
        assert layer.position == "top-left"
        # Default fields include name, location, datetime, etc.
        assert layer.fields is not None
        assert "name" in layer.fields

    def test_initialization_custom_position(self):
        """Test ChartInfoLayer with custom position."""
        layer = ChartInfoLayer(position="bottom-right")
        assert layer.position == "bottom-right"

    def test_initialization_custom_fields(self):
        """Test ChartInfoLayer with custom fields."""
        fields = ["name", "location"]
        layer = ChartInfoLayer(fields=fields)
        assert layer.fields == fields

    def test_render(self, renderer, mock_dwg, test_chart):
        """Test ChartInfoLayer rendering."""
        layer = ChartInfoLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added text elements
        assert mock_dwg.add.called


# ============================================================================
# ASPECT COUNTS LAYER TESTS
# ============================================================================


class TestAspectCountsLayer:
    """Tests for AspectCountsLayer."""

    def test_initialization(self):
        """Test AspectCountsLayer initialization."""
        layer = AspectCountsLayer()
        assert layer.position == "top-right"

    def test_render(self, renderer, mock_dwg, test_chart):
        """Test AspectCountsLayer rendering."""
        layer = AspectCountsLayer()
        layer.render(renderer, mock_dwg, test_chart)

        if test_chart.aspects:
            assert mock_dwg.add.called


# ============================================================================
# ELEMENT MODALITY TABLE LAYER TESTS
# ============================================================================


class TestElementModalityTableLayer:
    """Tests for ElementModalityTableLayer."""

    def test_initialization(self):
        """Test ElementModalityTableLayer initialization."""
        layer = ElementModalityTableLayer()
        assert layer.position == "bottom-left"

    def test_render(self, renderer, mock_dwg, test_chart):
        """Test ElementModalityTableLayer rendering."""
        layer = ElementModalityTableLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added table elements
        assert mock_dwg.add.called


# ============================================================================
# CHART SHAPE LAYER TESTS
# ============================================================================


class TestChartShapeLayer:
    """Tests for ChartShapeLayer."""

    def test_initialization(self):
        """Test ChartShapeLayer initialization."""
        layer = ChartShapeLayer()
        assert layer.position == "bottom-right"

    def test_render(self, renderer, mock_dwg, test_chart):
        """Test ChartShapeLayer rendering."""
        layer = ChartShapeLayer()
        layer.render(renderer, mock_dwg, test_chart)

        # Should have added shape info
        assert mock_dwg.add.called


# ============================================================================
# INTEGRATION TESTS - draw_chart()
# ============================================================================


class TestDrawChart:
    """Tests for the high-level draw_chart() function."""

    def test_draw_chart_basic(self, test_chart, temp_output_dir):
        """Test basic chart drawing."""
        filepath = os.path.join(temp_output_dir, "test_chart.svg")
        result = test_chart.draw(filepath).with_size(600).save()

        assert result == filepath
        assert os.path.exists(filepath)

        # Check file has content
        with open(filepath) as f:
            content = f.read()
            assert len(content) > 0
            assert "<svg" in content

    def test_draw_chart_custom_size(self, test_chart, temp_output_dir):
        """Test chart drawing with custom size."""
        filepath = os.path.join(temp_output_dir, "test_800.svg")
        test_chart.draw(filepath).with_size(800).save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_moon_phase(self, test_chart, temp_output_dir):
        """Test chart drawing with moon phase."""
        filepath = os.path.join(temp_output_dir, "test_moon.svg")
        test_chart.draw(filepath).with_moon_phase().save()

        assert os.path.exists(filepath)

    def test_draw_chart_without_moon_phase(self, test_chart, temp_output_dir):
        """Test chart drawing without moon phase."""
        filepath = os.path.join(temp_output_dir, "test_no_moon.svg")
        test_chart.draw(filepath).without_moon_phase().save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_info(self, test_chart, temp_output_dir):
        """Test chart drawing with chart info."""
        filepath = os.path.join(temp_output_dir, "test_info.svg")
        test_chart.draw(filepath).with_chart_info().save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_aspect_counts(self, test_chart, temp_output_dir):
        """Test chart drawing with aspect counts."""
        filepath = os.path.join(temp_output_dir, "test_aspects.svg")
        test_chart.draw(filepath).with_aspect_counts().save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_element_table(self, test_chart, temp_output_dir):
        """Test chart drawing with element/modality table."""
        filepath = os.path.join(temp_output_dir, "test_elements.svg")
        test_chart.draw(filepath).with_element_modality_table().save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_chart_shape(self, test_chart, temp_output_dir):
        """Test chart drawing with chart shape."""
        filepath = os.path.join(temp_output_dir, "test_shape.svg")
        test_chart.draw(filepath).with_chart_shape().save()

        assert os.path.exists(filepath)

    def test_draw_chart_all_features(self, test_chart, temp_output_dir):
        """Test chart drawing with all features enabled."""
        filepath = os.path.join(temp_output_dir, "test_full.svg")
        (
            test_chart.draw(filepath)
            .with_moon_phase()
            .with_chart_info()
            .with_aspect_counts()
            .with_element_modality_table()
            .with_chart_shape()
            .save()
        )

        assert os.path.exists(filepath)

        # Verify substantial content
        with open(filepath) as f:
            content = f.read()
            assert len(content) > 1000  # Should be substantial

    def test_draw_chart_with_theme(self, test_chart, temp_output_dir):
        """Test chart drawing with theme."""
        filepath = os.path.join(temp_output_dir, "test_theme.svg")
        test_chart.draw(filepath).with_theme("dark").save()

        assert os.path.exists(filepath)

    def test_draw_chart_with_zodiac_palette(self, test_chart, temp_output_dir):
        """Test chart drawing with zodiac palette."""
        filepath = os.path.join(temp_output_dir, "test_palette.svg")
        test_chart.draw(filepath).with_zodiac_palette("elemental").save()

        assert os.path.exists(filepath)

    def test_draw_chart_multiple_house_systems(self, test_chart, temp_output_dir):
        """Test chart drawing with multiple house systems."""
        # Create chart with multiple house systems
        native = Native(
            dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
            ChartLocation(37.7749, -122.4194, "SF", "America/Los_Angeles"),
        )
        multi_house_chart = (
            ChartBuilder.from_native(native)
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .calculate()
        )

        filepath = os.path.join(temp_output_dir, "test_multi_houses.svg")
        multi_house_chart.draw(filepath).save()

        assert os.path.exists(filepath)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestVisualizationEdgeCases:
    """Tests for edge cases in visualization."""

    def test_chart_with_no_aspects(self, temp_output_dir):
        """Test rendering a chart with no aspects."""
        native = Native(
            dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
            ChartLocation(0, 0, "Test", "UTC"),
        )
        chart = ChartBuilder.from_native(native).calculate()

        filepath = os.path.join(temp_output_dir, "no_aspects.svg")
        chart.draw(filepath).save()

        assert os.path.exists(filepath)

    def test_chart_with_minimal_data(self, temp_output_dir):
        """Test rendering a chart with minimal data."""
        native = Native(
            dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
            ChartLocation(0, 0, "Test", "UTC"),
        )
        chart = ChartBuilder.from_native(native).calculate()

        filepath = os.path.join(temp_output_dir, "minimal.svg")
        chart.draw(filepath).without_moon_phase().save()

        assert os.path.exists(filepath)

    def test_renderer_at_boundary_angles(self):
        """Test renderer coordinate conversion at boundary angles."""
        renderer = ChartRenderer()

        # Test 0, 90, 180, 270, 360 degrees
        for angle in [0, 90, 180, 270, 360]:
            x, y = renderer.polar_to_cartesian(angle, 100)
            assert isinstance(x, float)
            assert isinstance(y, float)
            assert not math.isnan(x)
            assert not math.isnan(y)

    def test_renderer_with_negative_angles(self):
        """Test renderer with negative angles."""
        renderer = ChartRenderer()

        x1, y1 = renderer.polar_to_cartesian(-90, 100)
        x2, y2 = renderer.polar_to_cartesian(270, 100)

        # -90 and 270 should be equivalent
        assert abs(x1 - x2) < 0.1
        assert abs(y1 - y2) < 0.1

    def test_renderer_with_large_angles(self):
        """Test renderer with angles > 360."""
        renderer = ChartRenderer()

        x1, y1 = renderer.polar_to_cartesian(0, 100)
        x2, y2 = renderer.polar_to_cartesian(360, 100)
        x3, y3 = renderer.polar_to_cartesian(720, 100)

        # All should be equivalent
        assert abs(x1 - x2) < 0.1
        assert abs(x1 - x3) < 0.1


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestVisualizationPerformance:
    """Performance tests for visualization."""

    def test_draw_chart_performance(self, test_chart, temp_output_dir):
        """Test that chart drawing completes in reasonable time."""
        import time

        filepath = os.path.join(temp_output_dir, "perf_test.svg")

        start = time.time()
        test_chart.draw(filepath).save()
        elapsed = time.time() - start

        # Should complete in under 5 seconds
        assert elapsed < 5.0
        assert os.path.exists(filepath)

    def test_multiple_charts_creation(self, test_chart, temp_output_dir):
        """Test creating multiple charts in sequence."""
        for i in range(5):
            filepath = os.path.join(temp_output_dir, f"chart_{i}.svg")
            test_chart.draw(filepath).save()
            assert os.path.exists(filepath)


# ============================================================================
# REGRESSION TESTS
# ============================================================================


def test_chart_file_not_empty(test_chart, temp_output_dir):
    """Regression test: Ensure generated SVG files are not empty."""
    filepath = os.path.join(temp_output_dir, "not_empty.svg")
    test_chart.draw(filepath).save()

    file_size = os.path.getsize(filepath)
    assert file_size > 100  # Should be at least 100 bytes


def test_svg_well_formed(test_chart, temp_output_dir):
    """Regression test: Ensure SVG is well-formed XML."""
    filepath = os.path.join(temp_output_dir, "well_formed.svg")
    test_chart.draw(filepath).save()

    with open(filepath) as f:
        content = f.read()
        assert content.startswith("<?xml") or content.startswith("<svg")
        assert "</svg>" in content


def test_coordinate_system_consistency():
    """Regression test: Ensure coordinate system is consistent."""
    renderer = ChartRenderer()

    # Convert to cartesian and verify consistency
    test_angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    for angle in test_angles:
        x, y = renderer.polar_to_cartesian(angle, 100)

        # Distance from center should always be 100
        dx = x - renderer.center
        dy = y - renderer.center
        distance = (dx**2 + dy**2) ** 0.5

        assert abs(distance - 100) < 0.1
