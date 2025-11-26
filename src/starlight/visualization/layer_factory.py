"""
Layer factory for creating visualization layers based on configuration.

This factory encapsulates the logic for creating the right layers
in the right order based on the user's configuration.
"""

from typing import Protocol

from starlight.core.comparison import Comparison
from starlight.core.models import CalculatedChart, UnknownTimeChart
from starlight.visualization.config import ChartVisualizationConfig
from starlight.visualization.layers import (
    AngleLayer,
    AspectCountsLayer,
    AspectLayer,
    ChartInfoLayer,
    ChartShapeLayer,
    ElementModalityTableLayer,
    HeaderLayer,
    HouseCuspLayer,
    MoonRangeLayer,
    OuterAngleLayer,
    OuterBorderLayer,
    OuterHouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)
from starlight.visualization.moon_phase import MoonPhaseLayer
from starlight.visualization.layout.engine import LayoutResult


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
        self, chart: CalculatedChart | Comparison, layout: LayoutResult
    ) -> list[IRenderLayer]:
        """
        Create all configured layers for this chart.

        Layers are returned in render order (bottom to top).

        Args:
            chart: The chart to visualize
            layout: The calculated layout (for positioning info)

        Returns:
            List of layers ready to render
        """
        is_comparison = isinstance(chart, Comparison)
        is_unknown_time = isinstance(chart, UnknownTimeChart)
        header_enabled = self.config.header.enabled

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
                # Single chart: just one set of houses
                layers.append(
                    HouseCuspLayer(
                        house_system_name=chart.default_house_system,
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
                )
            )
        else:
            # Single chart: one planet ring
            planets = [p for p in chart.positions if self._is_planetary_object(p)]
            layers.append(
                PlanetLayer(
                    planet_set=planets,
                    radius_key="planet_ring",
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
            layers.append(
                ChartInfoLayer(
                    position=self.config.corners.chart_info_position,
                    header_enabled=header_enabled,
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
        from starlight.core.models import ObjectType

        return position.object_type in (
            ObjectType.PLANET,
            ObjectType.ASTEROID,
            ObjectType.POINT,
            ObjectType.NODE,
        )
