"""
Layer factory for creating visualization layers based on configuration.

This factory encapsulates the logic for creating the right layers
in the right order based on the user's configuration.
"""

from typing import Protocol

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, UnknownTimeChart
from stellium.core.multichart import MultiChart
from stellium.core.multiwheel import MultiWheel
from stellium.visualization.config import ChartVisualizationConfig
from stellium.visualization.layers import (
    AngleLayer,
    AspectCountsLayer,
    AspectLayer,
    ChartInfoLayer,
    ChartShapeLayer,
    ElementModalityTableLayer,
    HeaderLayer,
    HouseCuspLayer,
    MoonRangeLayer,
    MultiWheelAspectLayer,
    OuterAngleLayer,
    OuterBorderLayer,
    OuterHouseCuspLayer,
    PlanetLayer,
    RingBoundaryLayer,
    ZodiacLayer,
)
from stellium.visualization.layout.engine import LayoutResult
from stellium.visualization.moon_phase import MoonPhaseLayer
from stellium.visualization.themes import get_theme_style


class IRenderLayer(Protocol):
    """Protocol for render layers."""

    def render(self, renderer, dwg, chart) -> None:
        """Render this layer to the SVG drawing."""
        ...


class LayerFactory:
    """
    Creates visualization layers based on configuration.

    This encapsulates all the logic for determining which layers to create,
    in what order, with what settings - based on the ChartVisualizationConfig.
    """

    def __init__(self, config: ChartVisualizationConfig):
        self.config = config

    def create_layers(
        self,
        chart: CalculatedChart | Comparison | MultiWheel | MultiChart,
        layout: LayoutResult,
    ) -> list[IRenderLayer]:
        """
        Create all configured layers for this chart.

        Layers are returned in render order (bottom to top).

        Args:
            chart: The chart to visualize (single, comparison, multiwheel, or multichart)
            layout: The calculated layout (for positioning info)

        Returns:
            List of layers ready to render
        """
        is_multichart = isinstance(chart, MultiChart)
        is_multiwheel = isinstance(chart, MultiWheel)
        is_comparison = isinstance(chart, Comparison)
        is_unknown_time = isinstance(chart, UnknownTimeChart)
        header_enabled = self.config.header.enabled

        # Dispatch to specialized method for multichart and multiwheel
        if is_multichart:
            return self._create_multichart_layers(chart, layout)
        if is_multiwheel:
            return self._create_multiwheel_layers(chart, layout)

        layers = []

        # Layer 0: Header (if enabled) - rendered first, in the header area
        if header_enabled:
            layers.append(
                HeaderLayer(
                    height=self.config.header.height,
                    name_font_size=self.config.header.name_font_size,
                    name_font_family=self.config.header.name_font_family,
                    details_font_size=self.config.header.details_font_size,
                    line_height=self.config.header.line_height,
                    coord_precision=self.config.header.coord_precision,
                )
            )

        # Layer 1: Zodiac ring (always present)
        layers.append(
            ZodiacLayer(
                palette=self.config.wheel.zodiac_palette or "grey",
                show_degree_ticks=self.config.wheel.show_degree_ticks,
            )
        )

        # Layer 2: House cusps (skip for unknown time charts - no houses without time!)
        if not is_unknown_time:
            if is_comparison:
                # Biwheel: inner chart houses inside, outer chart houses outside
                layers.append(
                    HouseCuspLayer(
                        house_system_name=chart.chart1.default_house_system,
                    )
                )
                layers.append(
                    OuterHouseCuspLayer(
                        house_system_name=chart.chart2.default_house_system,
                    )
                )
            else:
                # Single chart: determine which house systems to show
                house_systems_to_render = self._get_house_systems_to_render(chart)

                # Always render the primary system
                primary_system = house_systems_to_render[0]
                layers.append(
                    HouseCuspLayer(
                        house_system_name=primary_system,
                    )
                )

                # Render additional house systems as overlays with distinct styling
                for i, system_name in enumerate(house_systems_to_render[1:], start=1):
                    # Use different colors/styles for secondary systems
                    overlay_style = self._get_overlay_style(i)
                    layers.append(
                        HouseCuspLayer(
                            house_system_name=system_name,
                            style_override=overlay_style,
                        )
                    )

        # Layer 3: Angles (ASC, MC, DSC, IC) - skip for unknown time charts
        if not is_unknown_time:
            # Always show angles for inner wheel (chart1 for comparisons)
            layers.append(AngleLayer())

            # Layer 3b: Outer wheel angles (for comparisons only)
            if is_comparison:
                layers.append(OuterAngleLayer())

        # Layer 4: Aspects
        if is_comparison:
            # For comparisons, show cross-chart aspects
            # TODO: May need separate aspect layer for cross-chart vs internal
            layers.append(AspectLayer())
        else:
            # Single chart aspects
            layers.append(AspectLayer())

        # Layer 5: Planets
        if is_comparison:
            # Biwheel: inner and outer planet rings
            inner_planets = [
                p for p in chart.chart1.positions if self._is_planetary_object(p)
            ]
            outer_planets = [
                p for p in chart.chart2.positions if self._is_planetary_object(p)
            ]

            # Inner wheel: info stack extends inward (default)
            layers.append(
                PlanetLayer(
                    planet_set=inner_planets,
                    radius_key="planet_ring_inner",
                    show_position_ticks=self.config.wheel.show_planet_ticks,
                )
            )

            # Outer wheel: info stack extends outward
            # Hide info stack if position table is enabled (redundant info)
            show_outer_info = not (
                self.config.tables.enabled and self.config.tables.show_positions
            )

            layers.append(
                PlanetLayer(
                    planet_set=outer_planets,
                    radius_key="planet_ring_outer",
                    use_outer_wheel_color=True,
                    info_stack_direction="outward",  # Flip stack direction
                    show_info_stack=show_outer_info,  # Hide if position table enabled
                    show_position_ticks=self.config.wheel.show_planet_ticks,
                )
            )
        else:
            # Single chart: one planet ring
            planets = [p for p in chart.positions if self._is_planetary_object(p)]
            layers.append(
                PlanetLayer(
                    planet_set=planets,
                    radius_key="planet_ring",
                    show_position_ticks=self.config.wheel.show_planet_ticks,
                )
            )

        # Layer 5b: Moon range arc (for unknown time charts only)
        if is_unknown_time:
            layers.append(MoonRangeLayer())

        # Layer 5c: Moon phase (if enabled, and not a comparison chart)
        if self.config.corners.moon_phase and not is_comparison:
            # Build style override from config if size/label_size specified
            moon_style = {}
            if self.config.corners.moon_phase_size is not None:
                moon_style["size"] = self.config.corners.moon_phase_size
            if self.config.corners.moon_phase_label_size is not None:
                moon_style["label_size"] = self.config.corners.moon_phase_label_size

            layers.append(
                MoonPhaseLayer(
                    position=self.config.corners.moon_phase_position,
                    show_label=self.config.corners.moon_phase_show_label,
                    style_override=moon_style if moon_style else None,
                )
            )

        # Layer 6: Info corners (if enabled)
        if self.config.corners.chart_info:
            # Pass house systems list if multiple are being rendered
            house_systems_for_info = None
            if not is_comparison and not is_unknown_time:
                house_systems_to_render = self._get_house_systems_to_render(chart)
                if len(house_systems_to_render) > 0:
                    house_systems_for_info = house_systems_to_render

            layers.append(
                ChartInfoLayer(
                    position=self.config.corners.chart_info_position,
                    header_enabled=header_enabled,
                    house_systems=house_systems_for_info,
                )
            )

        if self.config.corners.aspect_counts:
            layers.append(
                AspectCountsLayer(
                    position=self.config.corners.aspect_counts_position,
                )
            )

        if self.config.corners.element_modality:
            layers.append(
                ElementModalityTableLayer(
                    position=self.config.corners.element_modality_position,
                )
            )

        if self.config.corners.chart_shape:
            layers.append(
                ChartShapeLayer(
                    position=self.config.corners.chart_shape_position,
                )
            )

        # Layer N: Outer border (for comparison charts only, drawn last so it's on top)
        if is_comparison:
            layers.append(OuterBorderLayer())

        return layers

    def _is_planetary_object(self, position) -> bool:
        """
        Check if a CelestialPosition should be rendered as a planet.

        Includes planets, asteroids, points, nodes - excludes angles.
        """
        from stellium.core.models import ObjectType

        return position.object_type in (
            ObjectType.PLANET,
            ObjectType.ASTEROID,
            ObjectType.POINT,
            ObjectType.NODE,
        )

    def _get_house_systems_to_render(self, chart: CalculatedChart) -> list[str]:
        """
        Determine which house systems to render based on config and chart data.

        Args:
            chart: The chart being rendered

        Returns:
            List of house system names to render, with the primary system first
        """
        config_systems = self.config.wheel.house_systems

        if config_systems is None:
            # Use chart's default only
            return [chart.default_house_system]

        if config_systems == "all":
            # Use all house systems available in the chart
            available_systems = list(chart.house_systems.keys())
            # Make sure the default system is first
            if chart.default_house_system in available_systems:
                available_systems.remove(chart.default_house_system)
                available_systems.insert(0, chart.default_house_system)
            return available_systems

        if isinstance(config_systems, str):
            # Single system specified
            return [config_systems]

        # List of systems specified
        return list(config_systems)

    def _get_overlay_style(self, index: int) -> dict:
        """
        Get distinct styling for overlay house systems.

        Uses the theme's secondary_color for the first overlay, with fallback
        colors for additional overlays.

        Args:
            index: 1-based index of the overlay (1 = first overlay, 2 = second, etc.)

        Returns:
            Style dictionary for HouseCuspLayer
        """
        # Get the secondary color from the theme
        secondary_color = "#3498DB"  # Default fallback (blue)

        if self.config.wheel.theme:
            style = get_theme_style(self.config.wheel.theme)
            houses_style = style.get("houses", {})
            secondary_color = houses_style.get("secondary_color", secondary_color)

        # Fallback colors for additional overlays (beyond the first)
        fallback_colors = [
            secondary_color,  # First overlay uses theme color
            "#E74C3C",  # Red
            "#2ECC71",  # Green
            "#9B59B6",  # Purple
            "#F39C12",  # Orange
        ]

        color = fallback_colors[(index - 1) % len(fallback_colors)]

        return {
            "line_color": color,
            "number_color": color,
            "line_width": 0.6,  # Thinner than primary
            "line_dash": "3,2",  # Dashed to distinguish from primary
            "fill_alternate": False,  # No fills for overlay systems (only primary gets fills)
        }

    def _create_multiwheel_layers(
        self, chart: MultiWheel, layout: LayoutResult
    ) -> list[IRenderLayer]:
        """
        Create layers for a multiwheel chart (2-4 charts rendered concentrically).

        Layer order (bottom to top):
        1. Header (if enabled)
        2. Zodiac ring (outermost visual element)
        3. Chart rings from outer to inner (each has houses, angles, planets)
        4. Info corners

        No aspect lines are drawn in multiwheel (too cluttered).

        Args:
            chart: The MultiWheel containing 2-4 charts
            layout: The calculated layout

        Returns:
            List of layers ready to render
        """
        header_enabled = self.config.header.enabled
        layers = []

        # Layer 0: Header (if enabled)
        if header_enabled:
            layers.append(
                HeaderLayer(
                    height=self.config.header.height,
                    name_font_size=self.config.header.name_font_size,
                    name_font_family=self.config.header.name_font_family,
                    details_font_size=self.config.header.details_font_size,
                    line_height=self.config.header.line_height,
                    coord_precision=self.config.header.coord_precision,
                )
            )

        # Layer 1: Zodiac ring (always present, outermost)
        layers.append(
            ZodiacLayer(
                palette=self.config.wheel.zodiac_palette or "grey",
                show_degree_ticks=self.config.wheel.show_degree_ticks,
            )
        )

        chart_count = chart.chart_count

        # Get glyph size and info stack distance from config
        glyph_size_override = self.config.wheel.multiwheel_glyph_sizes.get(chart_count)
        info_stack_dist = self.config.wheel.multiwheel_info_distances.get(
            chart_count, 0.8
        )

        # Layers 2-N: House cusps for all chart rings (OUTER to INNER)
        # These render first so fills don't cover other elements
        for wheel_idx in range(chart_count - 1, -1, -1):  # Reverse: outer to inner
            current_chart = chart.charts[wheel_idx]
            layers.append(
                HouseCuspLayer(
                    house_system_name=current_chart.default_house_system,
                    wheel_index=wheel_idx,
                    chart=current_chart,
                )
            )

        # Ring boundary lines (between chart rings and zodiac)
        # Drawn AFTER house cusps so boundaries appear on top of fills
        layers.append(RingBoundaryLayer(chart_count=chart_count))

        # Angles and planets for each chart ring
        for wheel_idx in range(chart_count - 1, -1, -1):  # Reverse: outer to inner
            current_chart = chart.charts[wheel_idx]

            # Draw angles for all charts in multiwheel
            # Each chart shows its own ASC/MC/DSC/IC in its ring
            layers.append(
                AngleLayer(
                    wheel_index=wheel_idx,
                    chart=current_chart,
                )
            )

            # Planets for this ring
            planets = [
                p for p in current_chart.positions if self._is_planetary_object(p)
            ]

            # Use no_sign info mode for all multiwheel charts
            # Sign is already visible from zodiac position, so glyph is redundant
            # This gives us degree + minutes in a tighter 2-row stack
            info_mode = "no_sign"

            layers.append(
                PlanetLayer(
                    planet_set=planets,
                    wheel_index=wheel_idx,
                    info_mode=info_mode,
                    show_position_ticks=self.config.wheel.show_planet_ticks,
                    glyph_size_override=glyph_size_override,
                    info_stack_distance=info_stack_dist,
                )
            )

        # Cross-chart aspects for 2-chart multiwheels only
        # For 3-4 charts, it's too cluttered - use aspectarian table instead
        if chart_count == 2 and chart.cross_aspects:
            layers.append(MultiWheelAspectLayer())

        # Layer N: Info corners (using innermost chart for data)
        if self.config.corners.chart_info:
            layers.append(
                ChartInfoLayer(
                    position=self.config.corners.chart_info_position,
                    header_enabled=header_enabled,
                )
            )

        # Moon phase for innermost chart (if enabled)
        if self.config.corners.moon_phase:
            moon_style = {}
            if self.config.corners.moon_phase_size is not None:
                moon_style["size"] = self.config.corners.moon_phase_size
            if self.config.corners.moon_phase_label_size is not None:
                moon_style["label_size"] = self.config.corners.moon_phase_label_size

            layers.append(
                MoonPhaseLayer(
                    position=self.config.corners.moon_phase_position,
                    show_label=self.config.corners.moon_phase_show_label,
                    style_override=moon_style if moon_style else None,
                )
            )

        return layers

    def _create_multichart_layers(
        self, chart: MultiChart, layout: LayoutResult
    ) -> list[IRenderLayer]:
        """
        Create layers for a MultiChart (2-4 charts rendered concentrically).

        This is similar to _create_multiwheel_layers but uses the MultiChart API.
        MultiChart is the unified replacement for Comparison and MultiWheel.

        Args:
            chart: The MultiChart containing 2-4 charts
            layout: The calculated layout

        Returns:
            List of layers ready to render
        """
        header_enabled = self.config.header.enabled
        layers = []

        # Layer 0: Header (if enabled)
        if header_enabled:
            layers.append(
                HeaderLayer(
                    height=self.config.header.height,
                    name_font_size=self.config.header.name_font_size,
                    name_font_family=self.config.header.name_font_family,
                    details_font_size=self.config.header.details_font_size,
                    line_height=self.config.header.line_height,
                    coord_precision=self.config.header.coord_precision,
                )
            )

        # Layer 1: Zodiac ring (always present, outermost)
        layers.append(
            ZodiacLayer(
                palette=self.config.wheel.zodiac_palette or "grey",
                show_degree_ticks=self.config.wheel.show_degree_ticks,
            )
        )

        chart_count = chart.chart_count

        # Get glyph size and info stack distance from config
        glyph_size_override = self.config.wheel.multiwheel_glyph_sizes.get(chart_count)
        info_stack_dist = self.config.wheel.multiwheel_info_distances.get(
            chart_count, 0.8
        )

        # Layers 2-N: House cusps for all chart rings (OUTER to INNER)
        for wheel_idx in range(chart_count - 1, -1, -1):
            current_chart = chart.charts[wheel_idx]
            layers.append(
                HouseCuspLayer(
                    house_system_name=current_chart.default_house_system,
                    wheel_index=wheel_idx,
                    chart=current_chart,
                )
            )

        # Ring boundary lines
        layers.append(RingBoundaryLayer(chart_count=chart_count))

        # Angles and planets for each chart ring
        for wheel_idx in range(chart_count - 1, -1, -1):
            current_chart = chart.charts[wheel_idx]

            layers.append(
                AngleLayer(
                    wheel_index=wheel_idx,
                    chart=current_chart,
                )
            )

            planets = [
                p for p in current_chart.positions if self._is_planetary_object(p)
            ]

            info_mode = "no_sign"

            layers.append(
                PlanetLayer(
                    planet_set=planets,
                    wheel_index=wheel_idx,
                    info_mode=info_mode,
                    show_position_ticks=self.config.wheel.show_planet_ticks,
                    glyph_size_override=glyph_size_override,
                    info_stack_distance=info_stack_dist,
                )
            )

        # Cross-chart aspects for 2-chart multicharts only
        if chart_count == 2 and chart.cross_aspects:
            layers.append(MultiWheelAspectLayer())

        # Info corners
        if self.config.corners.chart_info:
            layers.append(
                ChartInfoLayer(
                    position=self.config.corners.chart_info_position,
                    header_enabled=header_enabled,
                )
            )

        # Moon phase
        if self.config.corners.moon_phase:
            moon_style = {}
            if self.config.corners.moon_phase_size is not None:
                moon_style["size"] = self.config.corners.moon_phase_size
            if self.config.corners.moon_phase_label_size is not None:
                moon_style["label_size"] = self.config.corners.moon_phase_label_size

            layers.append(
                MoonPhaseLayer(
                    position=self.config.corners.moon_phase_position,
                    show_label=self.config.corners.moon_phase_show_label,
                    style_override=moon_style if moon_style else None,
                )
            )

        return layers
