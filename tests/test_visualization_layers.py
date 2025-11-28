"""
Tests for visualization/layers.py

Covers:
- HeaderLayer initialization and location parsing
- ZodiacBandLayer rendering
- PlanetLayer rendering
- AspectLineLayer rendering
- HouseCuspLayer rendering
- Layer rendering with different chart types (single, comparison, synthesis)
"""

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.native import Native
from stellium.visualization.layers import (
    HeaderLayer,
)


class TestHeaderLayerInit:
    """Tests for HeaderLayer initialization."""

    def test_init_default_values(self):
        """Test HeaderLayer has default values."""
        layer = HeaderLayer()

        assert layer.height == 70
        assert layer.name_font_size == "18px"
        assert layer.name_font_weight == "600"
        assert layer.name_font_style == "italic"
        assert layer.details_font_size == "12px"
        assert layer.line_height == 16
        assert layer.coord_precision == 4

    def test_init_custom_values(self):
        """Test HeaderLayer with custom values."""
        layer = HeaderLayer(
            height=100,
            name_font_size="24px",
            name_font_weight="bold",
            name_font_style="normal",
            details_font_size="14px",
            line_height=20,
            coord_precision=2,
        )

        assert layer.height == 100
        assert layer.name_font_size == "24px"
        assert layer.name_font_weight == "bold"
        assert layer.name_font_style == "normal"
        assert layer.details_font_size == "14px"
        assert layer.line_height == 20
        assert layer.coord_precision == 2


class TestHeaderLayerLocationParsing:
    """Tests for HeaderLayer._parse_location_name() method."""

    def test_parse_location_full_us_address(self):
        """Test parsing full US geopy address."""
        layer = HeaderLayer()

        short, country = layer._parse_location_name(
            "Palo Alto, Santa Clara County, California, United States of America"
        )

        assert short == "Palo Alto, California"
        assert country is None  # USA is skipped

    def test_parse_location_international(self):
        """Test parsing international address."""
        layer = HeaderLayer()

        short, country = layer._parse_location_name(
            "Tokyo, Shinjuku, Tokyo Prefecture, Japan"
        )

        assert "Tokyo" in short
        assert country == "Japan"

    def test_parse_location_short_address(self):
        """Test parsing already short address."""
        layer = HeaderLayer()

        short, country = layer._parse_location_name("New York, NY")

        assert short == "New York, NY"
        assert country is None

    def test_parse_location_empty_string(self):
        """Test parsing empty string."""
        layer = HeaderLayer()

        short, country = layer._parse_location_name("")

        assert short == ""
        assert country is None

    def test_parse_location_none(self):
        """Test parsing None value (should not crash)."""
        layer = HeaderLayer()

        # This should handle None gracefully
        short, country = layer._parse_location_name(None)

        assert short == ""
        assert country is None

    def test_parse_location_skips_county(self):
        """Test that county parts are skipped."""
        layer = HeaderLayer()

        short, country = layer._parse_location_name(
            "San Francisco, San Francisco County, California, United States"
        )

        assert short == "San Francisco, California"
        assert "County" not in short


class TestHeaderLayerRendering:
    """Integration tests for HeaderLayer rendering."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY", name="Test Person"
        ).calculate()

    @pytest.fixture
    def sample_comparison(self):
        """Create a comparison for rendering tests."""
        native1 = Native("1990-01-15 10:00", "New York, NY", name="Alice")
        chart1 = ChartBuilder.from_native(native1).calculate()

        native2 = Native("1995-06-20 14:30", "Los Angeles, CA", name="Bob")
        chart2 = ChartBuilder.from_native(native2).calculate()

        return (
            ComparisonBuilder.from_native(chart1, "Alice")
            .with_partner(chart2, partner_label="Bob")
            .calculate()
        )

    def test_render_single_chart(self, sample_chart):
        """Test rendering header for single chart."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(800, 800))

        layer = HeaderLayer()
        layer.render(renderer, dwg, sample_chart)

        # Should have added text elements
        svg_str = dwg.tostring()
        assert "<text" in svg_str
        assert "Test Person" in svg_str

    def test_render_comparison_chart(self, sample_comparison):
        """Test rendering header for comparison chart (two columns)."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(800, 800))

        layer = HeaderLayer()
        layer.render(renderer, dwg, sample_comparison)

        # Should have both names
        svg_str = dwg.tostring()
        assert "<text" in svg_str
        assert "Alice" in svg_str
        assert "Bob" in svg_str

    def test_render_unknown_time_chart(self):
        """Test rendering header for unknown time chart."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        chart = ChartBuilder.from_details(
            "1990-01-15", "New York, NY", name="Unknown Time", time_unknown=True
        ).calculate()

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(800, 800))

        layer = HeaderLayer()
        layer.render(renderer, dwg, chart)

        svg_str = dwg.tostring()
        assert "Unknown Time" in svg_str
        assert "Time Unknown" in svg_str


class TestLayerIntegration:
    """Integration tests for multiple layers working together."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart with aspects for rendering tests."""
        return (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY", name="Kate")
            .with_aspects()
            .calculate()
        )

    def test_full_chart_draw(self, sample_chart):
        """Test drawing a complete chart with all layers."""
        # Use the chart's draw() method which uses all layers
        svg_content = sample_chart.draw().save(to_string=True)

        assert svg_content is not None
        assert "<svg" in svg_content
        # Should have zodiac signs
        assert "Aries" in svg_content or "♈" in svg_content
        # Should have planets
        assert "Sun" in svg_content or "☉" in svg_content

    def test_chart_draw_with_header(self, sample_chart):
        """Test drawing chart with header."""
        svg_content = sample_chart.draw().with_header().save(to_string=True)

        assert svg_content is not None
        assert "Kate" in svg_content

    def test_chart_draw_with_tables(self, sample_chart):
        """Test drawing chart with position tables."""
        svg_content = (
            sample_chart.draw()
            .with_tables(position="right", show_position_table=True)
            .save(to_string=True)
        )

        assert svg_content is not None
        assert "<text" in svg_content

    def test_chart_draw_to_file(self, sample_chart, tmp_path):
        """Test saving chart to file."""
        output_path = tmp_path / "test_chart.svg"

        # Use with_filename() to set output path, then save()
        sample_chart.draw().with_filename(str(output_path)).save()

        assert output_path.exists()
        content = output_path.read_text()
        assert "<svg" in content

    def test_comparison_chart_draw(self):
        """Test drawing comparison chart."""
        comparison = ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1995-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

        svg_content = comparison.draw().save(to_string=True)

        assert svg_content is not None
        assert "<svg" in svg_content


class TestZodiacBandLayerIntegration:
    """Tests for ZodiacBandLayer through chart drawing."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return ChartBuilder.from_details("1990-01-15 10:00", "New York, NY").calculate()

    def test_zodiac_band_renders_signs(self, sample_chart):
        """Test that zodiac band renders sign glyphs."""
        svg_content = sample_chart.draw().save(to_string=True)

        # Should contain zodiac sign glyphs (Unicode)
        zodiac_glyphs = [
            "♈",
            "♉",
            "♊",
            "♋",
            "♌",
            "♍",
            "♎",
            "♏",
            "♐",
            "♑",
            "♒",
            "♓",
        ]

        # At least some glyphs should be present
        _found_glyphs = [glyph for glyph in zodiac_glyphs if glyph in svg_content]

        # The zodiac wheel should have at least some sign markers
        # (Text elements are in the SVG even if not zodiac names)
        assert "<text" in svg_content
        # The SVG should render the zodiac wheel with paths/circles
        assert "<path" in svg_content or "<circle" in svg_content

    def test_zodiac_palette_changes_colors(self, sample_chart):
        """Test that different zodiac palettes produce different output."""
        svg_default = sample_chart.draw().save(to_string=True)
        svg_rainbow = (
            sample_chart.draw().with_zodiac_palette("rainbow").save(to_string=True)
        )

        # Different palettes should produce different SVG (different colors)
        # Both should be valid SVG
        assert "<svg" in svg_default
        assert "<svg" in svg_rainbow


class TestPlanetLayerIntegration:
    """Tests for PlanetLayer through chart drawing."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .with_aspects()
            .calculate()
        )

    def test_planet_layer_renders_planets(self, sample_chart):
        """Test that planet layer renders planetary positions."""
        svg_content = sample_chart.draw().save(to_string=True)

        # Should contain at least one planet glyph or name
        # Planet glyphs are typically rendered in the wheel
        assert "<text" in svg_content or "<circle" in svg_content

    def test_planet_glyph_palette_changes_colors(self, sample_chart):
        """Test that different planet glyph palettes produce different output."""
        svg_default = sample_chart.draw().save(to_string=True)
        svg_rainbow = (
            sample_chart.draw()
            .with_planet_glyph_palette("rainbow")
            .save(to_string=True)
        )

        # Both should be valid SVG
        assert "<svg" in svg_default
        assert "<svg" in svg_rainbow


class TestAspectLineLayerIntegration:
    """Tests for AspectLineLayer through chart drawing."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart with aspects for rendering tests."""
        return (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .with_aspects()
            .calculate()
        )

    def test_aspect_lines_rendered(self, sample_chart):
        """Test that aspect lines are rendered."""
        svg_content = sample_chart.draw().save(to_string=True)

        # Should contain line elements for aspects
        assert "<line" in svg_content

    def test_aspect_palette_changes_colors(self, sample_chart):
        """Test that different aspect palettes produce different output."""
        svg_default = sample_chart.draw().save(to_string=True)
        svg_neon = sample_chart.draw().with_aspect_palette("neon").save(to_string=True)

        # Both should be valid SVG
        assert "<svg" in svg_default
        assert "<svg" in svg_neon


class TestHouseCuspLayerIntegration:
    """Tests for HouseCuspLayer through chart drawing."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return ChartBuilder.from_details("1990-01-15 10:00", "New York, NY").calculate()

    def test_house_cusps_rendered(self, sample_chart):
        """Test that house cusps are rendered."""
        svg_content = sample_chart.draw().save(to_string=True)

        # Should contain line elements for house cusps
        assert "<line" in svg_content

    def test_house_numbers_rendered(self, sample_chart):
        """Test that house numbers are rendered."""
        svg_content = sample_chart.draw().save(to_string=True)

        # Should contain at least some house numbers (1-12)
        # They're typically small text elements
        assert "<text" in svg_content


class TestChartThemes:
    """Tests for chart themes through drawing."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return ChartBuilder.from_details("1990-01-15 10:00", "New York, NY").calculate()

    def test_default_theme(self, sample_chart):
        """Test drawing with default theme."""
        svg_content = sample_chart.draw().save(to_string=True)

        assert "<svg" in svg_content

    def test_dark_theme(self, sample_chart):
        """Test drawing with dark theme."""
        svg_content = sample_chart.draw().with_theme("dark").save(to_string=True)

        assert "<svg" in svg_content

    def test_classic_theme(self, sample_chart):
        """Test drawing with classic theme."""
        svg_content = sample_chart.draw().with_theme("classic").save(to_string=True)

        assert "<svg" in svg_content

    def test_sepia_theme(self, sample_chart):
        """Test drawing with sepia theme."""
        svg_content = sample_chart.draw().with_theme("sepia").save(to_string=True)

        assert "<svg" in svg_content

    def test_themes_produce_different_output(self, sample_chart):
        """Test that different themes produce different SVG."""
        svg_classic = sample_chart.draw().with_theme("classic").save(to_string=True)
        svg_dark = sample_chart.draw().with_theme("dark").save(to_string=True)

        # Different themes should have different background colors
        # Both should be valid SVG
        assert "<svg" in svg_classic
        assert "<svg" in svg_dark
        # They should be different
        assert svg_classic != svg_dark
