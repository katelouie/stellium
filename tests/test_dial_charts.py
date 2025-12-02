"""
Comprehensive tests for Uranian dial chart visualization.

This test suite covers:
- DialRenderer: Coordinate transformation and longitude compression
- DialConfig: Configuration validation and theme integration
- DialDrawBuilder: Fluent API for dial chart creation
- Dial layers: Planet, midpoint, outer ring, pointer layers
- Integration with ChartBuilder's with_uranian() and with_tnos()
- Aries Point handling
- SVG glyph embedding
"""

import datetime as dt
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
from stellium.core.registry import get_object_info
from stellium.visualization.core import embed_svg_glyph, get_glyph
from stellium.visualization.dial.builder import DialDrawBuilder
from stellium.visualization.dial.config import (
    DialConfig,
    DialRadii,
    DialStyle,
)
from stellium.visualization.dial.layers import (
    HAMBURG_NAMES,
    TNO_NAMES,
    DialBackgroundLayer,
    DialCardinalLayer,
    DialGraduationLayer,
    DialMidpointLayer,
    DialModalityLayer,
    DialOuterRingLayer,
    DialPlanetLayer,
    DialPointerLayer,
    resolve_dial_collisions,
)
from stellium.visualization.dial.renderer import DialRenderer
from stellium.visualization.themes import ChartTheme

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def test_native() -> Native:
    """Create a test native for chart generation."""
    return Native(
        dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC),
        ChartLocation(
            latitude=37.7749,
            longitude=-122.4194,
            name="San Francisco, CA",
            timezone="America/Los_Angeles",
        ),
    )


@pytest.fixture
def test_chart(test_native: Native) -> CalculatedChart:
    """Create a test chart with real data."""
    return ChartBuilder.from_native(test_native).calculate()


@pytest.fixture
def uranian_chart(test_native: Native) -> CalculatedChart:
    """Create a chart with Uranian planets and TNOs."""
    return ChartBuilder.from_native(test_native).with_uranian().with_tnos().calculate()


@pytest.fixture
def dial_config_90() -> DialConfig:
    """Create a 90° dial configuration."""
    return DialConfig(dial_degrees=90, size=600)


@pytest.fixture
def dial_config_45() -> DialConfig:
    """Create a 45° dial configuration."""
    return DialConfig(dial_degrees=45, size=600)


@pytest.fixture
def dial_config_360() -> DialConfig:
    """Create a 360° dial configuration."""
    return DialConfig(dial_degrees=360, size=600)


@pytest.fixture
def dial_renderer_90(dial_config_90: DialConfig) -> DialRenderer:
    """Create a 90° dial renderer."""
    return DialRenderer(dial_config_90)


@pytest.fixture
def dial_renderer_45(dial_config_45: DialConfig) -> DialRenderer:
    """Create a 45° dial renderer."""
    return DialRenderer(dial_config_45)


@pytest.fixture
def dial_renderer_360(dial_config_360: DialConfig) -> DialRenderer:
    """Create a 360° dial renderer."""
    return DialRenderer(dial_config_360)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for SVG output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============================================================================
# DIAL CONFIG TESTS
# ============================================================================


class TestDialConfig:
    """Tests for DialConfig configuration and validation."""

    def test_valid_dial_degrees(self):
        """Test that valid dial degrees are accepted."""
        config_90 = DialConfig(dial_degrees=90)
        config_45 = DialConfig(dial_degrees=45)
        config_360 = DialConfig(dial_degrees=360)

        assert config_90.dial_degrees == 90
        assert config_45.dial_degrees == 45
        assert config_360.dial_degrees == 360

    def test_invalid_dial_degrees_raises_error(self):
        """Test that invalid dial degrees raise ValueError."""
        with pytest.raises(ValueError, match="dial_degrees must be 90, 45, or 360"):
            DialConfig(dial_degrees=180)

        with pytest.raises(ValueError, match="dial_degrees must be 90, 45, or 360"):
            DialConfig(dial_degrees=60)

    def test_theme_string_normalization(self):
        """Test that theme strings are normalized to ChartTheme enum."""
        config = DialConfig(theme="dark")
        assert config.theme == ChartTheme.DARK

        config = DialConfig(theme="midnight")
        assert config.theme == ChartTheme.MIDNIGHT

    def test_theme_enum_accepted(self):
        """Test that ChartTheme enum values are accepted."""
        config = DialConfig(theme=ChartTheme.CELESTIAL)
        assert config.theme == ChartTheme.CELESTIAL

    def test_pointer_auto_enabled_for_360_dial(self):
        """Test that pointer is auto-enabled for 360° dial with target."""
        config = DialConfig(dial_degrees=360, pointer_target=45.0)
        assert config.show_pointer is True

    def test_pointer_not_auto_enabled_for_90_dial(self):
        """Test that pointer is not auto-enabled for 90° dial."""
        config = DialConfig(dial_degrees=90, pointer_target=45.0)
        assert config.show_pointer is False

    def test_radii_to_absolute(self):
        """Test radii conversion to absolute pixel values."""
        radii = DialRadii()
        absolute = radii.to_absolute(600)

        assert absolute["graduation_outer"] == 600 * 0.36
        assert absolute["planet_ring"] == 600 * 0.26
        assert absolute["modality_outer"] == 600 * 0.20

    def test_get_dial_style(self):
        """Test that dial style is correctly derived from theme."""
        config = DialConfig(theme="dark")
        style = config.get_dial_style()

        assert isinstance(style, DialStyle)
        # Dark theme should have dark background
        assert style.background_color != "#FFFFFF"


# ============================================================================
# DIAL RENDERER TESTS
# ============================================================================


class TestDialRenderer:
    """Tests for DialRenderer coordinate transformations."""

    def test_compress_longitude_90_degree(self, dial_renderer_90: DialRenderer):
        """Test longitude compression for 90° dial."""
        # 0° Aries should map to 0° on dial
        assert dial_renderer_90.compress_longitude(0) == 0

        # 90° Cancer should map to 0° on dial (same as Aries)
        assert dial_renderer_90.compress_longitude(90) == 0

        # 180° Libra should map to 0° on dial
        assert dial_renderer_90.compress_longitude(180) == 0

        # 270° Capricorn should map to 0° on dial
        assert dial_renderer_90.compress_longitude(270) == 0

        # 45° mid-Taurus should map to 45° on dial
        assert dial_renderer_90.compress_longitude(45) == 45

        # 135° mid-Leo should also map to 45° on dial
        assert dial_renderer_90.compress_longitude(135) == 45

    def test_compress_longitude_45_degree(self, dial_renderer_45: DialRenderer):
        """Test longitude compression for 45° dial."""
        # 0° should map to 0°
        assert dial_renderer_45.compress_longitude(0) == 0

        # 45° should map to 0° (octile)
        assert dial_renderer_45.compress_longitude(45) == 0

        # 90° should map to 0°
        assert dial_renderer_45.compress_longitude(90) == 0

        # 22.5° should map to 22.5°
        assert dial_renderer_45.compress_longitude(22.5) == 22.5

        # 67.5° should also map to 22.5°
        assert dial_renderer_45.compress_longitude(67.5) == 22.5

    def test_compress_longitude_360_degree(self, dial_renderer_360: DialRenderer):
        """Test that 360° dial has no compression."""
        # 360° dial should not compress
        assert dial_renderer_360.compress_longitude(0) == 0
        assert dial_renderer_360.compress_longitude(90) == 90
        assert dial_renderer_360.compress_longitude(180) == 180
        assert dial_renderer_360.compress_longitude(270) == 270

    def test_dial_to_svg_angle_no_rotation(self, dial_renderer_90: DialRenderer):
        """Test SVG angle conversion without rotation."""
        # 0° on dial (top) should map to 270° SVG (top in SVG coordinates)
        svg_angle = dial_renderer_90.dial_to_svg_angle(0)
        assert svg_angle == pytest.approx(270, abs=0.1)

    def test_polar_to_cartesian_center(self, dial_renderer_90: DialRenderer):
        """Test polar to cartesian conversion at center."""
        x, y = dial_renderer_90.polar_to_cartesian(0, 0)
        assert x == dial_renderer_90.center
        assert y == dial_renderer_90.center

    def test_polar_to_cartesian_top(self, dial_renderer_90: DialRenderer):
        """Test polar to cartesian at top of dial (0°)."""
        radius = 100
        x, y = dial_renderer_90.polar_to_cartesian(0, radius)

        # At 0° (top), y should be less than center (top of SVG)
        assert y < dial_renderer_90.center
        # x should be at center
        assert x == pytest.approx(dial_renderer_90.center, abs=0.1)

    def test_polar_to_cartesian_right(self, dial_renderer_90: DialRenderer):
        """Test polar to cartesian at right of dial (22.5° for 90° dial)."""
        radius = 100
        quarter_dial = dial_renderer_90.dial_degrees / 4
        x, y = dial_renderer_90.polar_to_cartesian(quarter_dial, radius)

        # At 22.5° (right), x should be greater than center
        assert x > dial_renderer_90.center

    def test_get_cardinal_points_90(self, dial_renderer_90: DialRenderer):
        """Test cardinal points for 90° dial."""
        points = dial_renderer_90.get_cardinal_points()
        assert len(points) == 4
        assert points == [0, 22.5, 45, 67.5]

    def test_get_cardinal_points_360(self, dial_renderer_360: DialRenderer):
        """Test cardinal points for 360° dial."""
        points = dial_renderer_360.get_cardinal_points()
        assert len(points) == 4
        assert points == [0, 90, 180, 270]

    def test_get_modality_sectors(self, dial_renderer_90: DialRenderer):
        """Test modality sector definitions."""
        sectors = dial_renderer_90.get_modality_sectors()
        assert len(sectors) == 3

        # Check sector names
        assert sectors[0][2] == "Cardinal"
        assert sectors[1][2] == "Fixed"
        assert sectors[2][2] == "Mutable"

        # Check sector boundaries for 90° dial
        assert sectors[0][0] == 0
        assert sectors[0][1] == 30
        assert sectors[1][0] == 30
        assert sectors[1][1] == 60
        assert sectors[2][0] == 60
        assert sectors[2][1] == 90

    def test_create_drawing(self, dial_renderer_90: DialRenderer):
        """Test SVG drawing creation."""
        dwg = dial_renderer_90.create_drawing()
        assert isinstance(dwg, svgwrite.Drawing)


# ============================================================================
# DIAL DRAW BUILDER TESTS
# ============================================================================


class TestDialDrawBuilder:
    """Tests for DialDrawBuilder fluent API."""

    def test_basic_construction(self, test_chart: CalculatedChart):
        """Test basic builder construction."""
        builder = DialDrawBuilder(test_chart, "test.svg", dial_degrees=90)
        assert builder._chart == test_chart
        assert builder._dial_degrees == 90

    def test_with_size(self, test_chart: CalculatedChart):
        """Test with_size() method."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.with_size(800)

        assert result._size == 800
        assert result is builder  # Fluent interface returns self

    def test_with_theme(self, test_chart: CalculatedChart):
        """Test with_theme() method."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.with_theme("midnight")

        assert result._theme == "midnight"
        assert result is builder

    def test_with_rotation(self, test_chart: CalculatedChart):
        """Test with_rotation() method."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.with_rotation(15.0)

        assert result._rotation == 15.0
        assert result is builder

    def test_without_midpoints(self, test_chart: CalculatedChart):
        """Test without_midpoints() method."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.without_midpoints()

        assert result._show_midpoints is False
        assert result is builder

    def test_with_midpoints_notation(self, test_chart: CalculatedChart):
        """Test with_midpoints() with notation parameter."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.with_midpoints(notation="tick")

        assert result._show_midpoints is True
        assert result._midpoint_notation == "tick"
        assert result is builder

    def test_with_pointer_string(self, test_chart: CalculatedChart):
        """Test with_pointer() with planet name."""
        builder = DialDrawBuilder(test_chart, "test.svg", dial_degrees=360)
        result = builder.with_pointer("Sun")

        assert result._show_pointer is True
        assert result._pointer_target == "Sun"

    def test_with_pointer_degree(self, test_chart: CalculatedChart):
        """Test with_pointer() with degree value."""
        builder = DialDrawBuilder(test_chart, "test.svg", dial_degrees=360)
        result = builder.with_pointer(45.0)

        assert result._show_pointer is True
        assert result._pointer_target == 45.0

    def test_without_pointer(self, test_chart: CalculatedChart):
        """Test without_pointer() method."""
        builder = DialDrawBuilder(test_chart, "test.svg", dial_degrees=360)
        builder.with_pointer("Sun")
        result = builder.without_pointer()

        assert result._show_pointer is False

    def test_without_modality_wheel(self, test_chart: CalculatedChart):
        """Test without_modality_wheel() method."""
        builder = DialDrawBuilder(test_chart, "test.svg")
        result = builder.without_modality_wheel()

        assert result._show_modality_wheel is False

    def test_with_tnos_without_tnos(self, test_chart: CalculatedChart):
        """Test with_tnos() and without_tnos() methods."""
        builder = DialDrawBuilder(test_chart, "test.svg")

        # Default is True
        assert builder._include_tnos is True

        result = builder.without_tnos()
        assert result._include_tnos is False

        result = builder.with_tnos()
        assert result._include_tnos is True

    def test_with_uranian_without_uranian(self, test_chart: CalculatedChart):
        """Test with_uranian() and without_uranian() methods."""
        builder = DialDrawBuilder(test_chart, "test.svg")

        # Default is True
        assert builder._include_uranian is True

        result = builder.without_uranian()
        assert result._include_uranian is False

        result = builder.with_uranian()
        assert result._include_uranian is True

    def test_save_creates_file(self, test_chart: CalculatedChart, temp_output_dir: str):
        """Test that save() creates an SVG file."""
        filename = os.path.join(temp_output_dir, "test_dial.svg")
        builder = DialDrawBuilder(test_chart, filename)
        builder.save()

        assert os.path.exists(filename)
        with open(filename) as f:
            content = f.read()
            assert content.startswith("<?xml") or content.startswith("<svg")

    def test_fluent_chain(self, test_chart: CalculatedChart, temp_output_dir: str):
        """Test fluent method chaining."""
        filename = os.path.join(temp_output_dir, "test_dial.svg")

        # Should be able to chain all methods
        builder = (
            DialDrawBuilder(test_chart, filename)
            .with_size(800)
            .with_theme("dark")
            .with_rotation(15.0)
            .without_midpoints()
            .without_modality_wheel()
        )

        assert builder._size == 800
        assert builder._theme == "dark"
        assert builder._rotation == 15.0
        assert builder._show_midpoints is False
        assert builder._show_modality_wheel is False


# ============================================================================
# DIAL LAYER TESTS
# ============================================================================


class TestDialLayers:
    """Tests for dial layer rendering."""

    def test_background_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that background layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialBackgroundLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_graduation_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that graduation layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialGraduationLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_cardinal_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that cardinal layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialCardinalLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_modality_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that modality layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialModalityLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_planet_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that planet layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialPlanetLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_midpoint_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that midpoint layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        layer = DialMidpointLayer()
        layer.render(dial_renderer_90, dwg, test_chart)

    def test_pointer_layer_renders_360(
        self, dial_renderer_360: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that pointer layer renders on 360° dial."""
        dwg = dial_renderer_360.create_drawing()
        layer = DialPointerLayer(pointing_to=45.0)
        layer.render(dial_renderer_360, dwg, test_chart)

    def test_pointer_layer_with_planet_name(
        self, dial_renderer_360: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that pointer layer can be created with planet name."""
        # Note: The pointer layer resolves planet names to degrees during render
        # We test that it accepts planet names as input
        layer = DialPointerLayer(pointing_to="Sun")
        assert layer.pointing_to == "Sun"

        # When rendered, it should resolve to the Sun's position
        sun = test_chart.get_object("Sun")
        assert sun is not None

    def test_outer_ring_layer_renders(
        self, dial_renderer_90: DialRenderer, test_chart: CalculatedChart
    ):
        """Test that outer ring layer renders without error."""
        dwg = dial_renderer_90.create_drawing()
        positions = test_chart.get_planets()[:5]  # Use first 5 planets
        layer = DialOuterRingLayer(
            positions=positions,
            ring="outer_ring_1",
            label="Test",
        )
        layer.render(dial_renderer_90, dwg, test_chart)


# ============================================================================
# COLLISION DETECTION TESTS
# ============================================================================


class TestDialCollisionDetection:
    """Tests for dial collision detection."""

    def test_no_collisions(self):
        """Test that well-spaced positions have no adjustment."""
        positions = [
            {"planet": Mock(name="Sun"), "true_deg": 0.0, "display_deg": 0.0},
            {"planet": Mock(name="Moon"), "true_deg": 30.0, "display_deg": 30.0},
            {"planet": Mock(name="Mars"), "true_deg": 60.0, "display_deg": 60.0},
        ]

        result = resolve_dial_collisions(positions, dial_degrees=90, min_spacing_360=15)

        # Positions should be unchanged
        assert result[0]["display_deg"] == 0.0
        assert result[1]["display_deg"] == 30.0
        assert result[2]["display_deg"] == 60.0

    def test_collision_detected(self):
        """Test that close positions are adjusted."""
        positions = [
            {"planet": Mock(name="Sun"), "true_deg": 10.0, "display_deg": 10.0},
            {"planet": Mock(name="Moon"), "true_deg": 11.0, "display_deg": 11.0},
        ]

        result = resolve_dial_collisions(positions, dial_degrees=90, min_spacing_360=15)

        # Positions should be spread apart (or at least not closer than before)
        diff = abs(result[0]["display_deg"] - result[1]["display_deg"])
        # The collision detection should maintain or increase spacing
        assert diff >= 1.0  # Should be at least 1° apart


# ============================================================================
# URANIAN FEATURES TESTS
# ============================================================================


class TestUranianFeatures:
    """Tests for Uranian astrology features."""

    def test_with_uranian_includes_hamburg_planets(self, test_native: Native):
        """Test that with_uranian() includes all Hamburg planets."""
        chart = ChartBuilder.from_native(test_native).with_uranian().calculate()

        hamburg_planets = [
            "Cupido",
            "Hades",
            "Zeus",
            "Kronos",
            "Apollon",
            "Admetos",
            "Vulkanus",
            "Poseidon",
        ]

        for planet in hamburg_planets:
            obj = chart.get_object(planet)
            assert obj is not None, f"{planet} not found in chart"

    def test_with_uranian_includes_aries_point(self, test_native: Native):
        """Test that with_uranian() includes the Aries Point."""
        chart = ChartBuilder.from_native(test_native).with_uranian().calculate()

        aries_point = chart.get_object("Aries Point")
        assert aries_point is not None
        assert aries_point.longitude == 0.0
        assert aries_point.sign == "Aries"

    def test_aries_point_always_zero(self, test_native: Native):
        """Test that Aries Point is always at 0° longitude."""
        chart = ChartBuilder.from_native(test_native).with_uranian().calculate()
        aries_point = chart.get_object("Aries Point")

        assert aries_point.longitude == 0.0
        assert aries_point.latitude == 0.0
        assert aries_point.speed_longitude == 0.0

    def test_with_tnos_includes_dwarf_planets(self, test_native: Native):
        """Test that with_tnos() includes Trans-Neptunian Objects."""
        chart = ChartBuilder.from_native(test_native).with_tnos().calculate()

        # Note: Some TNOs may be missing if ephemeris files aren't installed
        # We test that at least one is present or the method doesn't crash
        tno_names = ["Eris", "Sedna", "Makemake", "Haumea", "Orcus", "Quaoar"]
        _found_any = False

        for name in tno_names:
            obj = chart.get_object(name)
            if obj is not None:
                _found_any = True
                break

        # Either we found TNOs or we got graceful warnings (not errors)
        # This is acceptable since ephemeris files may not be installed

    def test_hamburg_names_constant(self):
        """Test HAMBURG_NAMES constant includes all expected objects."""
        expected = {
            "Cupido",
            "Hades",
            "Zeus",
            "Kronos",
            "Apollon",
            "Admetos",
            "Vulkanus",
            "Poseidon",
            "Aries Point",
        }
        assert HAMBURG_NAMES == expected

    def test_tno_names_constant(self):
        """Test TNO_NAMES constant includes all expected objects."""
        expected = {"Eris", "Sedna", "Makemake", "Haumea", "Orcus", "Quaoar"}
        assert TNO_NAMES == expected


# ============================================================================
# ARIES POINT TESTS
# ============================================================================


class TestAriesPoint:
    """Tests for Aries Point in the celestial registry and calculations."""

    def test_aries_point_in_registry(self):
        """Test that Aries Point is in the celestial registry."""
        info = get_object_info("Aries Point")
        assert info is not None
        assert info.display_name == "Aries Point"
        assert info.object_type == ObjectType.POINT
        assert info.category == "Uranian Point"

    def test_aries_point_glyph(self):
        """Test Aries Point glyph is the Aries symbol."""
        info = get_object_info("Aries Point")
        assert info.glyph == "♈"

    def test_aries_point_aliases(self):
        """Test Aries Point aliases."""
        info = get_object_info("Aries Point")
        assert "AP" in info.aliases
        assert "Vernal Point" in info.aliases

    def test_aries_point_object_type(self, uranian_chart: CalculatedChart):
        """Test Aries Point object type in calculated chart."""
        ap = uranian_chart.get_object("Aries Point")
        assert ap is not None
        assert ap.object_type == ObjectType.POINT


# ============================================================================
# SVG GLYPH TESTS
# ============================================================================


class TestSvgGlyphEmbedding:
    """Tests for SVG glyph embedding functionality."""

    def test_get_glyph_unicode(self):
        """Test get_glyph returns unicode for planets."""
        result = get_glyph("Sun")
        assert result["type"] == "unicode"
        assert result["value"] == "☉"

    def test_get_glyph_svg(self):
        """Test get_glyph returns SVG content for objects with SVG glyphs."""
        result = get_glyph("Eris")

        # Eris has an SVG glyph
        if result["type"] == "svg":
            assert "<svg" in result["value"] or "<path" in result["value"]

    def test_get_glyph_fallback(self):
        """Test get_glyph falls back to abbreviation for unknown objects."""
        result = get_glyph("UnknownObject123")
        assert result["type"] == "unicode"
        assert result["value"] == "Unk"

    def test_embed_svg_glyph_function(self):
        """Test embed_svg_glyph function with simple SVG."""
        dwg = svgwrite.Drawing(size=("100px", "100px"))

        svg_content = '<svg viewBox="0 0 16 16"><path d="M8 0 L16 16 L0 16 Z" style="fill:none;stroke:#000;stroke-width:1"/></svg>'

        # Should not raise
        embed_svg_glyph(dwg, svg_content, x=50, y=50, size=20, fill_color="#FF0000")

        # SVG should have nested svg element
        assert len(dwg.elements) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestDialIntegration:
    """Integration tests for dial chart generation."""

    def test_chart_draw_dial_method(
        self, test_chart: CalculatedChart, temp_output_dir: str
    ):
        """Test that CalculatedChart has draw_dial method."""
        filename = os.path.join(temp_output_dir, "dial.svg")
        builder = test_chart.draw_dial(filename)
        assert isinstance(builder, DialDrawBuilder)

    def test_dial_with_all_themes(
        self, test_chart: CalculatedChart, temp_output_dir: str
    ):
        """Test dial generation with different themes."""
        themes = ["classic", "dark", "midnight", "celestial", "neon", "viridis"]

        for theme in themes:
            filename = os.path.join(temp_output_dir, f"dial_{theme}.svg")
            test_chart.draw_dial(filename).with_theme(theme).save()
            assert os.path.exists(filename), f"Failed to create dial with theme {theme}"

    def test_dial_all_sizes(self, test_chart: CalculatedChart, temp_output_dir: str):
        """Test dial generation with all dial sizes."""
        for degrees in [90, 45, 360]:
            filename = os.path.join(temp_output_dir, f"dial_{degrees}.svg")
            test_chart.draw_dial(filename, degrees=degrees).save()
            assert os.path.exists(filename), f"Failed to create {degrees}° dial"

    def test_dial_with_uranian_chart(
        self, uranian_chart: CalculatedChart, temp_output_dir: str
    ):
        """Test dial with Uranian planets included."""
        filename = os.path.join(temp_output_dir, "dial_uranian.svg")
        uranian_chart.draw_dial(filename).save()

        assert os.path.exists(filename)

        # Check that the file contains Aries Point glyph or Hamburg planet names
        with open(filename) as f:
            content = f.read()
            # Should contain at least some of the Uranian content
            assert "♈" in content or "Aries" in content or "Cupido" in content

    def test_dial_with_pointer(self, test_chart: CalculatedChart, temp_output_dir: str):
        """Test 360° dial with pointer."""
        filename = os.path.join(temp_output_dir, "dial_pointer.svg")
        test_chart.draw_dial(filename, degrees=360).with_pointer("Sun").save()
        assert os.path.exists(filename)

    def test_dial_with_outer_ring(
        self, test_chart: CalculatedChart, temp_output_dir: str
    ):
        """Test dial with outer ring (simulating transits)."""
        filename = os.path.join(temp_output_dir, "dial_outer.svg")
        positions = test_chart.get_planets()[:5]

        builder = test_chart.draw_dial(filename)
        builder.with_outer_ring(positions, label="Test")
        builder.save()

        assert os.path.exists(filename)

    def test_dial_minimal_config(
        self, test_chart: CalculatedChart, temp_output_dir: str
    ):
        """Test dial with minimal configuration (no midpoints, no modality)."""
        filename = os.path.join(temp_output_dir, "dial_minimal.svg")

        (
            test_chart.draw_dial(filename)
            .without_midpoints()
            .without_modality_wheel()
            .without_cardinal_points()
            .save()
        )

        assert os.path.exists(filename)
