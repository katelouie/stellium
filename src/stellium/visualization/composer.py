import svgwrite

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.core.multiwheel import MultiWheel
from stellium.visualization.config import ChartVisualizationConfig
from stellium.visualization.core import ChartRenderer
from stellium.visualization.extended_canvas import (
    AspectarianLayer,
    HouseCuspTableLayer,
    PositionTableLayer,
)
from stellium.visualization.layer_factory import LayerFactory
from stellium.visualization.layout.engine import LayoutEngine, LayoutResult
from stellium.visualization.themes import get_theme_style


class ChartComposer:
    """
    Main orchestrator for chart visualization.

    This is the new public API that replaces draw_chart() and draw_comparison_chart().
    """

    def __init__(self, config: ChartVisualizationConfig):
        self.config = config
        self.layout_engine = LayoutEngine(config)
        self.layer_factory = LayerFactory(config)

    def compose(
        self,
        chart: CalculatedChart | Comparison | MultiWheel | MultiChart,
        to_string: bool = False,
    ) -> str:
        """
        Compose and render a complete chart visualization.

        This is a pure, testable pipeline:
        1. Calculate layout
        2. Create SVG canvas
        3. Create layers
        4. Render layers
        5. Save
        """
        # Step 1: Calculate complete layout
        layout = self.layout_engine.calculate_layout(chart)

        # Step 2: Create canvas with correct dimensions
        canvas = self._create_canvas(layout)

        # Step 3: Create renderer with calculated radii
        renderer = self._create_renderer(layout, chart)

        # Step 4: Create configured layers
        layers = self.layer_factory.create_layers(chart, layout)

        # Step 5: Render all layers
        for layer in layers:
            layer.render(renderer, canvas, chart)

        # Step 6: Render tables (separate from layers)
        if self.config.tables.enabled:
            self._render_tables(canvas, renderer, chart, layout)

        if to_string:
            return canvas.tostring()
        else:
            # Step 7: Save
            canvas.save()

            return self.config.filename

    def _create_canvas(self, layout: LayoutResult) -> svgwrite.Drawing:
        """Create SVG canvas with correct dimensions (only once)."""
        dims = layout.canvas_dimensions

        dwg = svgwrite.Drawing(
            filename=self.config.filename,
            size=(f"{dims.width}px", f"{dims.height}px"),
            viewBox=f"0 0 {dims.width} {dims.height}",
            profile="full",
        )

        # Background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(f"{dims.width}px", f"{dims.height}px"),
                fill=self._get_background_color(),
            )
        )

        return dwg

    def _create_renderer(
        self,
        layout: LayoutResult,
        chart: CalculatedChart | Comparison | MultiWheel | MultiChart,
    ) -> ChartRenderer:
        """Create renderer with pre-calculated radii."""
        renderer = ChartRenderer(
            size=layout.wheel_size,
            rotation=self._get_rotation_angle(chart),
            theme=self.config.wheel.theme,
            zodiac_palette=self.config.wheel.zodiac_palette,
            aspect_palette=self.config.wheel.aspect_palette,
            planet_glyph_palette=self.config.wheel.planet_glyph_palette,
            color_sign_info=self.config.wheel.color_sign_info,
        )
        # Set the pre-calculated radii
        renderer.radii = layout.wheel_radii

        # Set position offsets
        renderer.x_offset = int(layout.wheel_position.x)
        renderer.y_offset = int(layout.wheel_position.y)

        # Set header height for layers that need to account for it
        renderer.header_height = layout.header_height

        return renderer

    def _get_background_color(self) -> str:
        """Get background color from theme or default."""
        if self.config.wheel.theme:
            style = get_theme_style(self.config.wheel.theme)
            return style.get("background_color", "#FFFFFF")
        return "#FFFFFF"

    def _get_rotation_angle(
        self, chart: CalculatedChart | Comparison | MultiWheel | MultiChart
    ) -> float:
        """
        Calculate chart rotation based on ASC.

        For single charts, rotates to put ASC on the left.
        For comparisons, uses chart1's ASC.
        For multiwheels/multicharts, uses the innermost chart's (chart[0]) ASC.
        """
        if isinstance(chart, MultiChart):
            chart = chart.charts[0]  # Use innermost chart
        elif isinstance(chart, MultiWheel):
            chart = chart.charts[0]  # Use innermost chart
        elif isinstance(chart, Comparison):
            chart = chart.chart1

        # Get the ASC angle
        angles = chart.get_angles()
        asc = next((a for a in angles if a.name == "ASC"), None)
        return asc.longitude if asc else 0.0

    def _render_tables(
        self,
        canvas: svgwrite.Drawing,
        renderer: ChartRenderer,
        chart: CalculatedChart | Comparison,
        layout: LayoutResult,
    ) -> None:
        """
        Render table layers using calculated layout positions.

        This delegates to the adapted table layers from extended_canvas.
        """
        is_comparison = isinstance(chart, Comparison)

        # Build style override from theme colors
        extended_style = {
            "text_color": renderer.style.get("planets", {}).get(
                "info_color", "#333333"
            ),
            "header_color": renderer.style.get("planets", {}).get(
                "glyph_color", "#222222"
            ),
            "grid_color": renderer.style.get("zodiac", {}).get("line_color", "#CCCCCC"),
        }

        # Render positions table if enabled
        if self.config.tables.show_positions and "positions" in layout.tables:
            table_bbox = layout.tables["positions"]

            # Create position table layer with layout-calculated position
            position_layer = PositionTableLayer(
                x_offset=int(table_bbox.position.x),
                y_offset=int(table_bbox.position.y),
                object_types=self.config.tables.object_types,
                config=self.config,
                style_override=extended_style,
            )
            position_layer.render(renderer, canvas, chart)

        # Render houses table if enabled
        if self.config.tables.show_houses and "houses" in layout.tables:
            table_bbox = layout.tables["houses"]

            # Create house cusp table layer
            house_layer = HouseCuspTableLayer(
                x_offset=int(table_bbox.position.x),
                y_offset=int(table_bbox.position.y),
                config=self.config,
                style_override=extended_style,
            )
            house_layer.render(renderer, canvas, chart)

        # Render aspectarian if enabled
        if self.config.tables.show_aspectarian and "aspectarian" in layout.tables:
            table_bbox = layout.tables["aspectarian"]

            # Determine aspectarian mode
            if is_comparison:
                # For comparison charts, default to cross-chart aspects
                _mode = "cross-chart"  # Can make configurable later
            else:
                _mode = "internal"

            # Create aspectarian layer
            aspectarian_layer = AspectarianLayer(
                x_offset=int(table_bbox.position.x),
                y_offset=int(table_bbox.position.y),
                object_types=self.config.tables.object_types,
                config=self.config,
                style_override=extended_style,
                detailed=self.config.tables.aspectarian_detailed,
            )
            aspectarian_layer.render(renderer, canvas, chart)
