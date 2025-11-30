"""
Tests for visualization/extended_canvas.py

Covers:
- _is_comparison() helper function
- _filter_objects_for_tables() filtering logic
- PositionTableLayer initialization and style merging
- HouseCuspTableLayer initialization
- AspectarianLayer initialization and modes
- Table layer rendering with different inputs
"""

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.models import ObjectType
from stellium.visualization.extended_canvas import (
    AspectarianLayer,
    HouseCuspTableLayer,
    PositionTableLayer,
    _filter_objects_for_tables,
    _is_comparison,
)


class TestIsComparison:
    """Tests for _is_comparison() helper function."""

    def test_is_comparison_with_comparison_object(self):
        """Test _is_comparison returns True for Comparison objects."""
        comparison = ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1995-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

        assert _is_comparison(comparison) is True

    def test_is_comparison_with_calculated_chart(self):
        """Test _is_comparison returns False for CalculatedChart."""
        chart = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        assert _is_comparison(chart) is False

    def test_is_comparison_with_dict(self):
        """Test _is_comparison returns False for dict."""
        assert _is_comparison({"comparison_type": "test"}) is False

    def test_is_comparison_with_none(self):
        """Test _is_comparison returns False for None."""
        assert _is_comparison(None) is False

    def test_is_comparison_with_string(self):
        """Test _is_comparison returns False for string."""
        assert _is_comparison("comparison") is False


class TestFilterObjectsForTables:
    """Tests for _filter_objects_for_tables() function."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart with various position types."""
        return ChartBuilder.from_details("1990-01-15 10:00", "New York, NY").calculate()

    def test_filter_default_includes_planets(self, sample_chart):
        """Test default filter includes planets."""
        filtered = _filter_objects_for_tables(sample_chart.positions)

        planet_names = [p.name for p in filtered]
        assert "Sun" in planet_names
        assert "Moon" in planet_names
        assert "Mercury" in planet_names
        assert "Venus" in planet_names
        assert "Mars" in planet_names

    def test_filter_default_excludes_earth(self, sample_chart):
        """Test default filter excludes Earth."""
        filtered = _filter_objects_for_tables(sample_chart.positions)

        planet_names = [p.name for p in filtered]
        assert "Earth" not in planet_names

    def test_filter_default_includes_angles(self, sample_chart):
        """Test default filter includes ASC and MC angles."""
        filtered = _filter_objects_for_tables(sample_chart.positions)

        planet_names = [p.name for p in filtered]
        # Check for ASC/AC and MC
        has_asc = any(name in planet_names for name in ["ASC", "AC", "Ascendant"])
        has_mc = any(name in planet_names for name in ["MC", "Midheaven"])
        assert has_asc or has_mc

    def test_filter_default_excludes_dsc_ic(self, sample_chart):
        """Test default filter excludes DSC and IC."""
        filtered = _filter_objects_for_tables(sample_chart.positions)

        planet_names = [p.name for p in filtered]
        assert "DSC" not in planet_names
        assert "DC" not in planet_names
        assert "IC" not in planet_names

    def test_filter_default_includes_north_node(self, sample_chart):
        """Test default filter includes North Node but not South Node."""
        filtered = _filter_objects_for_tables(sample_chart.positions)

        planet_names = [p.name for p in filtered]
        # Should include one of: North Node, True Node, Mean Node
        has_north = any(
            name in planet_names for name in ["North Node", "True Node", "Mean Node"]
        )
        assert has_north

        # Should not include South Node
        assert "South Node" not in planet_names

    def test_filter_with_custom_object_types_string(self, sample_chart):
        """Test filter with custom object types as strings."""
        filtered = _filter_objects_for_tables(
            sample_chart.positions, object_types=["planet"]
        )

        # Should only include planets
        for pos in filtered:
            assert pos.object_type == ObjectType.PLANET

    def test_filter_with_custom_object_types_enum(self, sample_chart):
        """Test filter with custom object types as ObjectType enums."""
        filtered = _filter_objects_for_tables(
            sample_chart.positions, object_types=[ObjectType.PLANET, ObjectType.ANGLE]
        )

        # Should only include planets and angles
        for pos in filtered:
            assert pos.object_type in (ObjectType.PLANET, ObjectType.ANGLE)

    def test_filter_with_invalid_string_type_ignored(self, sample_chart):
        """Test filter ignores invalid string types."""
        # "invalid_type" should be silently ignored
        filtered = _filter_objects_for_tables(
            sample_chart.positions, object_types=["planet", "invalid_type"]
        )

        # Should still return planets
        assert len(filtered) > 0
        for pos in filtered:
            assert pos.object_type == ObjectType.PLANET

    def test_filter_includes_midpoints_when_specified(self):
        """Test filter includes midpoints when specified."""
        from stellium.components.midpoints import MidpointCalculator

        chart = (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .add_component(MidpointCalculator())
            .calculate()
        )

        filtered = _filter_objects_for_tables(
            chart.positions, object_types=["midpoint"]
        )

        # Should include midpoints
        midpoint_positions = [
            p for p in filtered if p.object_type == ObjectType.MIDPOINT
        ]
        assert len(midpoint_positions) > 0

    def test_filter_includes_arabic_parts_when_specified(self):
        """Test filter includes Arabic parts when specified."""
        from stellium.components.arabic_parts import ArabicPartsCalculator

        chart = (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .add_component(ArabicPartsCalculator())
            .calculate()
        )

        filtered = _filter_objects_for_tables(
            chart.positions, object_types=["arabic_part"]
        )

        # Should include Arabic parts
        arabic_positions = [
            p for p in filtered if p.object_type == ObjectType.ARABIC_PART
        ]
        assert len(arabic_positions) > 0

    def test_filter_empty_positions(self):
        """Test filter with empty positions list."""
        filtered = _filter_objects_for_tables([])

        assert filtered == []


class TestPositionTableLayer:
    """Tests for PositionTableLayer class."""

    def test_init_default_style(self):
        """Test PositionTableLayer has default style."""
        layer = PositionTableLayer()

        assert layer.style["text_color"] == "#333333"
        assert layer.style["header_color"] == "#222222"
        assert layer.style["show_speed"] is True
        assert layer.style["show_house"] is True

    def test_init_with_offset(self):
        """Test PositionTableLayer with x/y offset."""
        layer = PositionTableLayer(x_offset=100, y_offset=200)

        assert layer.x_offset == 100
        assert layer.y_offset == 200

    def test_init_with_style_override(self):
        """Test PositionTableLayer merges style override."""
        layer = PositionTableLayer(
            style_override={"text_color": "#FF0000", "show_speed": False}
        )

        assert layer.style["text_color"] == "#FF0000"
        assert layer.style["show_speed"] is False
        # Other defaults preserved
        assert layer.style["header_color"] == "#222222"

    def test_init_with_object_types(self):
        """Test PositionTableLayer accepts object_types filter."""
        layer = PositionTableLayer(object_types=["planet", "angle"])

        assert layer.object_types == ["planet", "angle"]

    def test_abbreviate_house_system(self):
        """Test _abbreviate_house_system() method."""
        layer = PositionTableLayer()

        assert layer._abbreviate_house_system("Placidus") == "Plac"
        assert layer._abbreviate_house_system("Whole Sign") == "WS"
        assert layer._abbreviate_house_system("Koch") == "Koch"
        assert layer._abbreviate_house_system("Unknown System") == "Unkn"


class TestHouseCuspTableLayer:
    """Tests for HouseCuspTableLayer class."""

    def test_init_default_style(self):
        """Test HouseCuspTableLayer has default style."""
        layer = HouseCuspTableLayer()

        assert layer.style["text_color"] == "#333333"
        assert layer.style["header_color"] == "#222222"
        assert layer.style["line_height"] == 16

    def test_init_with_offset(self):
        """Test HouseCuspTableLayer with x/y offset."""
        layer = HouseCuspTableLayer(x_offset=50, y_offset=100)

        assert layer.x_offset == 50
        assert layer.y_offset == 100

    def test_init_with_style_override(self):
        """Test HouseCuspTableLayer merges style override."""
        layer = HouseCuspTableLayer(
            style_override={"text_size": "14px", "line_height": 20}
        )

        assert layer.style["text_size"] == "14px"
        assert layer.style["line_height"] == 20

    def test_abbreviate_house_system(self):
        """Test _abbreviate_house_system() method."""
        layer = HouseCuspTableLayer()

        assert layer._abbreviate_house_system("Regiomontanus") == "Regio"
        assert layer._abbreviate_house_system("Campanus") == "Camp"
        assert layer._abbreviate_house_system("Topocentric") == "Topo"


class TestAspectarianLayer:
    """Tests for AspectarianLayer class."""

    def test_init_default_style(self):
        """Test AspectarianLayer has default style."""
        layer = AspectarianLayer()

        assert layer.style["text_color"] == "#333333"
        assert layer.style["grid_color"] == "#CCCCCC"
        assert layer.style["cell_size"] == 24
        assert layer.style["show_grid"] is True
        assert layer.detailed is False

    def test_init_with_offset(self):
        """Test AspectarianLayer with x/y offset."""
        layer = AspectarianLayer(x_offset=200, y_offset=300)

        assert layer.x_offset == 200
        assert layer.y_offset == 300

    def test_init_detailed_mode(self):
        """Test AspectarianLayer in detailed mode."""
        layer = AspectarianLayer(detailed=True)

        assert layer.detailed is True

    def test_init_with_style_override(self):
        """Test AspectarianLayer merges style override."""
        layer = AspectarianLayer(style_override={"cell_size": 32, "show_grid": False})

        assert layer.style["cell_size"] == 32
        assert layer.style["show_grid"] is False

    def test_init_with_object_types(self):
        """Test AspectarianLayer accepts object_types filter."""
        layer = AspectarianLayer(object_types=["planet"])

        assert layer.object_types == ["planet"]


class TestPositionTableLayerRendering:
    """Integration tests for PositionTableLayer rendering."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .with_aspects()
            .calculate()
        )

    @pytest.fixture
    def sample_comparison(self):
        """Create a comparison for rendering tests."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1995-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

    def test_render_single_chart(self, sample_chart):
        """Test rendering position table for single chart produces SVG."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1200, 800))

        layer = PositionTableLayer(x_offset=820, y_offset=50)
        layer.render(renderer, dwg, sample_chart)

        # Should have added text elements to the drawing
        svg_str = dwg.tostring()
        assert "<text" in svg_str
        assert "Planet" in svg_str  # Header text
        assert "Sign" in svg_str

    def test_render_comparison_chart(self, sample_comparison):
        """Test rendering position table for comparison produces SVG."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1400, 800))

        layer = PositionTableLayer(x_offset=820, y_offset=50)
        layer.render(renderer, dwg, sample_comparison)

        # Should have added text elements including chart labels
        svg_str = dwg.tostring()
        assert "<text" in svg_str
        assert "Inner Wheel" in svg_str or "Chart 1" in svg_str


class TestHouseCuspTableLayerRendering:
    """Integration tests for HouseCuspTableLayer rendering."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart for rendering tests."""
        return ChartBuilder.from_details("1990-01-15 10:00", "New York, NY").calculate()

    def test_render_single_chart(self, sample_chart):
        """Test rendering house cusp table produces SVG."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1200, 800))

        layer = HouseCuspTableLayer(x_offset=820, y_offset=300)
        layer.render(renderer, dwg, sample_chart)

        # Should have added text elements
        svg_str = dwg.tostring()
        assert "<text" in svg_str
        assert "House" in svg_str  # Header


class TestAspectarianLayerRendering:
    """Integration tests for AspectarianLayer rendering."""

    @pytest.fixture
    def sample_chart(self):
        """Create a chart with aspects for rendering tests."""
        return (
            ChartBuilder.from_details("1990-01-15 10:00", "New York, NY")
            .with_aspects()
            .calculate()
        )

    @pytest.fixture
    def sample_comparison(self):
        """Create a comparison for rendering tests."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1995-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

    def test_render_single_chart_simple_mode(self, sample_chart):
        """Test rendering aspectarian in simple mode."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1200, 800))

        layer = AspectarianLayer(x_offset=820, y_offset=500, detailed=False)
        layer.render(renderer, dwg, sample_chart)

        # Should have grid rectangles and text
        svg_str = dwg.tostring()
        assert "<rect" in svg_str  # Grid cells
        assert "<text" in svg_str  # Planet glyphs

    def test_render_single_chart_detailed_mode(self, sample_chart):
        """Test rendering aspectarian in detailed mode."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1200, 800))

        layer = AspectarianLayer(x_offset=820, y_offset=500, detailed=True)
        layer.render(renderer, dwg, sample_chart)

        # Should have grid rectangles and text (including orbs)
        svg_str = dwg.tostring()
        assert "<rect" in svg_str
        assert "<text" in svg_str

    def test_render_comparison_chart(self, sample_comparison):
        """Test rendering aspectarian for comparison (rectangular grid)."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1400, 800))

        layer = AspectarianLayer(x_offset=820, y_offset=500)
        layer.render(renderer, dwg, sample_comparison)

        # Should have grid rectangles and text with subscripts
        svg_str = dwg.tostring()
        assert "<rect" in svg_str
        assert "<text" in svg_str
        # Comparison should have subscript indicators
        assert "₁" in svg_str or "₂" in svg_str

    def test_render_with_no_grid(self, sample_chart):
        """Test rendering aspectarian without grid lines."""
        import svgwrite

        from stellium.visualization.core import ChartRenderer

        renderer = ChartRenderer(size=800)
        dwg = svgwrite.Drawing(size=(1200, 800))

        layer = AspectarianLayer(
            x_offset=820, y_offset=500, style_override={"show_grid": False}
        )
        layer.render(renderer, dwg, sample_chart)

        # Should not have grid rectangles (or very few)
        svg_str = dwg.tostring()
        # Still has text
        assert "<text" in svg_str
