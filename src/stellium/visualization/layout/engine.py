from dataclasses import dataclass
from typing import Protocol

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.core.multiwheel import MultiWheel
from stellium.visualization.config import ChartVisualizationConfig, Dimensions
from stellium.visualization.layout.measurer import ContentMeasurer


@dataclass(frozen=True)
class Position:
    """Represents x, y coordinates."""

    x: float
    y: float


@dataclass(frozen=True)
class BoundingBox:
    """Represents a positioned element with dimensions."""

    position: Position
    dimensions: Dimensions

    @property
    def right(self) -> float:
        return self.position.x + self.dimensions.width

    @property
    def bottom(self) -> float:
        return self.position.y + self.dimensions.height


class ChartElement(Protocol):
    """Protocol for measurable chart elements."""

    def measure(self) -> Dimensions:
        """Calculate dimensions without rendering."""
        ...


@dataclass(frozen=True)
class LayoutResult:
    """Complete layout specification - everything positioned!"""

    # Canvas
    canvas_dimensions: Dimensions

    # Chart wheel
    wheel_position: Position
    wheel_size: int
    wheel_radii: dict[str, float]

    # Info corners (only for enabled corners)
    corners: dict[str, BoundingBox]  # e.g., {"top-left": BoundingBox(...)}

    # Tables (only for enabled tables)
    tables: dict[str, BoundingBox]  # e.g., {"positions": BoundingBox(...)}

    # Useful metadata
    wheel_grew: bool  # Did we grow the wheel due to large canvas?
    actual_margins: dict[str, float]  # Actual margins used

    # Header (optional, with defaults)
    header_enabled: bool = False
    header_height: int = 0


@dataclass(frozen=True)
class TableLayoutSpec:
    """
    Specification for table layout (before final positioning).

    This represents the relative layout of tables to each other,
    which will be finalized once we know the wheel position. It's the blueprint
    for the tables.
    """

    # Dimensions:
    total_width: float
    total_height: float

    # Relative positions of each table (before wheel positioning)
    table_positions: dict[str, Position]  # e.g., {"positions": Position(0, 0)}
    table_dimensions: dict[str, Dimensions]  # e.g., {"positions": Dimensions(200, 300)}

    @staticmethod
    def empty() -> "TableLayoutSpec":
        """Create an empty layout spec when tables are disabled."""
        return TableLayoutSpec(
            total_width=0,
            total_height=0,
            table_positions={},
            table_dimensions={},
        )


class LayoutEngine:
    """
    The heart of the system - calculates all positions before rendering.

    This is a pure calculation engine - no rendering, no side effects.
    """

    def __init__(self, config: ChartVisualizationConfig):
        self.config = config
        self.measurer = ContentMeasurer()

    def calculate_layout(
        self, chart: CalculatedChart | Comparison | MultiWheel | MultiChart
    ) -> LayoutResult:
        """
        Calculate complete layout for the chart.

        Steps:
        1. Measure all enabled elements
        2. Calculate table positions and sizes
        3. Calculate required canvas size (scaled for multiwheel)
        4. Calculate wheel size (possibly grown)
        5. Center everything
        6. Position info corners (with collision detection)
        7. Return complete layout specification
        """
        # Step 0: Determine effective base size (scale up for multiwheels)
        effective_base_size = self._get_effective_base_size(chart)

        # Step 1: Measure everything
        measurements = self._measure_all_elements(chart)

        # Step 2: Calculate table layout
        table_layout = self._calculate_table_layout(measurements)

        # Step 3: Calculate canvas size (using scaled base for multiwheel)
        canvas_dims = self._calculate_canvas_size(
            base_wheel_size=effective_base_size,
            table_layout=table_layout,
            measurements=measurements,
        )

        # Step 4: Calculate wheel size (auto-grow if enabled)
        wheel_size = self._calculate_wheel_size(canvas_dims, effective_base_size)

        # Step 5: Position the wheel
        wheel_pos = self._position_wheel(canvas_dims, wheel_size, table_layout)

        # Step 6: Calculate wheel radii
        wheel_radii = self._calculate_wheel_radii(wheel_size, chart)

        # Step 7: Position info corners
        corners = self._position_info_corners(wheel_pos, wheel_size, measurements)

        # Step 8: Finalize table positions (relative to wheel)
        final_tables = self._finalize_table_positions(
            table_layout, wheel_pos, wheel_size
        )

        return LayoutResult(
            canvas_dimensions=canvas_dims,
            header_enabled=self.config.header.enabled,
            header_height=self.config.header.height
            if self.config.header.enabled
            else 0,
            wheel_position=wheel_pos,
            wheel_size=wheel_size,
            wheel_radii=wheel_radii,
            corners=corners,
            tables=final_tables,
            wheel_grew=(wheel_size > effective_base_size),
            actual_margins=self._calculate_margins(
                canvas_dims, wheel_pos, wheel_size, final_tables
            ),
        )

    def _measure_all_elements(
        self, chart: CalculatedChart | Comparison | MultiWheel | MultiChart
    ) -> dict[str, Dimensions]:
        """Measure all enabled elements."""
        measurements = {}

        # Measure tables if enabled
        if self.config.tables.enabled:
            if self.config.tables.show_positions:
                measurements["position_table"] = self.measurer.measure_position_table(
                    chart, self.config
                )
            if self.config.tables.show_houses:
                measurements["house_table"] = self.measurer.measure_house_table(
                    chart, self.config
                )
            if self.config.tables.show_aspectarian:
                measurements["aspectarian"] = self.measurer.measure_aspectarian(
                    chart, self.config
                )

        # Measure corner elements
        # (Roughly fixed size anyway)
        for corner_name in [
            "chart_info",
            "aspect_counts",
            "element_modality",
            "chart_shape",
        ]:
            if getattr(self.config.corners, corner_name, False):
                measurements[corner_name] = self.measurer.measure_corner_element(
                    corner_name, chart, self.config
                )

        return measurements

    def _calculate_table_layout(
        self, measurements: dict[str, Dimensions]
    ) -> TableLayoutSpec:
        """
        Calculate where tables should go relative to each other.

        Returns a specification that can be finalized once we know wheel position.
        """
        if not self.config.tables.enabled:
            return TableLayoutSpec.empty()

        placement = self.config.tables.placement
        padding = self.config.tables.padding
        gap = self.config.tables.gap_between_tables

        # Get enabled tables
        enabled_tables = []
        if self.config.tables.show_positions:
            enabled_tables.append(("positions", measurements.get("position_table")))
        if self.config.tables.show_houses:
            enabled_tables.append(("houses", measurements.get("house_table")))
        if self.config.tables.show_aspectarian:
            enabled_tables.append(("aspectarian", measurements.get("aspectarian")))

        # Calculate relative positions based on placement
        if placement == "right" or placement == "left":
            return self._layout_tables_vertically(enabled_tables, padding, gap)
        else:  # placement = "below"
            return self._layout_tables_horizontally(enabled_tables, padding, gap)

    def _layout_tables_vertically(
        self, tables: list[tuple[str, Dimensions]], padding: int, gap: int
    ) -> TableLayoutSpec:
        """
        Layout tables for vertical (right/left) placement.

        For single-wheel charts:
        - Position and House tables side-by-side in top row
        - Aspectarian below them (centered or full width)

        For comparison charts:
        - All tables stack vertically (old behavior)
        """
        if not tables:
            return TableLayoutSpec.empty()

        table_positions = {}
        table_dimensions = {}

        # Check if we have the typical single-wheel set (positions, houses, aspectarian)
        table_names = [name for name, _ in tables]
        has_positions = "positions" in table_names
        has_houses = "houses" in table_names
        has_aspectarian = "aspectarian" in table_names

        # Single-wheel custom layout: positions + houses side-by-side, aspectarian below
        if has_positions and has_houses and len(tables) <= 3:
            positions_dims = next(dims for name, dims in tables if name == "positions")
            houses_dims = next(dims for name, dims in tables if name == "houses")

            # Top row: positions and houses side by side
            # Note: dimensions already include internal padding, so y=0 is correct
            table_positions["positions"] = Position(x=0, y=0)
            table_dimensions["positions"] = positions_dims

            table_positions["houses"] = Position(x=positions_dims.width + gap, y=0)
            table_dimensions["houses"] = houses_dims

            top_row_width = positions_dims.width + gap + houses_dims.width
            top_row_height = max(positions_dims.height, houses_dims.height)

            # Aspectarian below (if present)
            if has_aspectarian:
                aspectarian_dims = next(
                    dims for name, dims in tables if name == "aspectarian"
                )
                table_positions["aspectarian"] = Position(x=0, y=top_row_height + gap)
                table_dimensions["aspectarian"] = aspectarian_dims

                total_width = max(top_row_width, aspectarian_dims.width)
                total_height = top_row_height + gap + aspectarian_dims.height
            else:
                total_width = top_row_width
                total_height = top_row_height

            return TableLayoutSpec(
                total_width=total_width,
                total_height=total_height,
                table_positions=table_positions,
                table_dimensions=table_dimensions,
            )

        # Default: stack vertically (old behavior for comparison charts)
        current_y = padding
        max_width = 0
        for table_name, dims in tables:
            # Position this table
            table_positions[table_name] = Position(x=0, y=current_y)
            table_dimensions[table_name] = dims

            # Track max width
            max_width = max(max_width, dims.width)

            # Move down for next table
            current_y += dims.height + gap

        # Calculate total dimensions (remove last gap)
        total_width = max_width + (padding * 2)  # padding on left and right
        total_height = current_y - gap + padding

        return TableLayoutSpec(
            total_width=total_width,
            total_height=total_height,
            table_positions=table_positions,
            table_dimensions=table_dimensions,
        )

    def _layout_tables_horizontally(
        self, tables: list[tuple[str, Dimensions]], padding: int, gap: int
    ) -> TableLayoutSpec:
        """
        Stack tables horizontally with proper spacing.

        For below placement, tables go left to right.
        """
        if not tables:
            return TableLayoutSpec.empty()

        table_positions = {}
        table_dimensions = {}

        # Start from the left
        current_x = padding
        max_height = 0

        for table_name, dims in tables:
            # Position this table
            table_positions[table_name] = Position(x=current_x, y=0)
            table_dimensions[table_name] = dims

            # Track maximum height
            max_height = max(max_height, dims.height)

            # Move right for the next table
            current_x += dims.width + gap

        # Calculate total dimensions (remove last gap)
        total_width = current_x - gap + padding
        total_height = max_height + (padding * 2)

        return TableLayoutSpec(
            total_width=total_width,
            total_height=total_height,
            table_positions=table_positions,
            table_dimensions=table_dimensions,
        )

    def _get_effective_base_size(
        self, chart: CalculatedChart | Comparison | MultiWheel | MultiChart
    ) -> int:
        """
        Get the effective base size, scaled for multiwheel charts.

        MultiWheel charts with more rings get larger canvases by default
        to keep the information readable.
        """
        if isinstance(chart, MultiChart):
            scale = self.config.wheel.get_multiwheel_canvas_scale(chart.chart_count)
            return int(self.config.base_size * scale)
        elif isinstance(chart, MultiWheel):
            scale = self.config.wheel.get_multiwheel_canvas_scale(chart.chart_count)
            return int(self.config.base_size * scale)
        return self.config.base_size

    def _calculate_wheel_size(
        self, canvas_dims: Dimensions, effective_base_size: int
    ) -> int:
        """
        Calculate wheel size, potentially growing it if canvas is large.

        Args:
            canvas_dims: The calculated canvas dimensions
            effective_base_size: The base size (possibly scaled for multiwheel)
        """
        if not self.config.auto_grow_wheel:
            return effective_base_size

        # If canvas is significantly larger than base size, grow the wheel
        # This keeps the chart from looking tiny in a huge canvas
        max_dim = max(canvas_dims.width, canvas_dims.height)

        if max_dim > effective_base_size * 2:
            # Grow wheel by up to 30%
            growth_factor = min(1.3, max_dim / (effective_base_size * 2))
            return int(effective_base_size * growth_factor)

        return effective_base_size

    def _calculate_wheel_radii(
        self,
        wheel_size: int,
        chart: CalculatedChart | Comparison | MultiWheel | MultiChart,
    ) -> dict[str, float]:
        """
        Calculate all wheel radii based on wheel size and chart type.

        Config keys now match renderer keys directly - no mapping needed!

        For MultiWheel, uses the multiwheel_N_radii config based on chart count.
        """
        # Determine which radii config to use
        is_multichart = isinstance(chart, MultiChart)
        is_multiwheel = isinstance(chart, MultiWheel)
        is_biwheel = (
            isinstance(chart, Comparison) or self.config.wheel.chart_type == "biwheel"
        )

        if is_multichart:
            # Use multiwheel-specific radii based on chart count
            multipliers = self.config.wheel.get_multiwheel_radii(chart.chart_count)
        elif is_multiwheel:
            # Use multiwheel-specific radii based on chart count
            multipliers = self.config.wheel.get_multiwheel_radii(chart.chart_count)
        elif is_biwheel:
            multipliers = self.config.wheel.biwheel_radii
        else:
            multipliers = self.config.wheel.single_radii

        # Direct multiplication - config keys = renderer keys!
        radii = {key: wheel_size * mult for key, mult in multipliers.items()}

        # Calculate derived radius (zodiac glyph is positioned between rings)
        radii["zodiac_glyph"] = wheel_size * (
            (multipliers["zodiac_ring_outer"] + multipliers["zodiac_ring_inner"]) / 2
        )

        # Auto-select outer containment border based on table configuration
        # (Will be overridden in layer_factory based on actual show_info_stack value)
        if is_biwheel and not is_multiwheel:
            # Default to compact if tables with positions enabled (info stacks hidden)
            # Will be refined in layer_factory which has access to show_info_stack
            if self.config.tables.enabled and self.config.tables.show_positions:
                radii["outer_containment_border"] = radii.get(
                    "outer_containment_border_compact",
                    radii.get("outer_containment_border_full", 0),
                )
            else:
                radii["outer_containment_border"] = radii.get(
                    "outer_containment_border_full",
                    radii.get("outer_containment_border_compact", 0),
                )

        return radii

    def _position_info_corners(
        self, wheel_pos: Position, wheel_size: int, measurements: dict[str, Dimensions]
    ) -> dict[str, BoundingBox]:
        """
        Position info corner elements outside the wheel's bounding box.

        Corners are positioned relative to the wheel's edges, but pushed outward
        to avoid overlapping the wheel itself.
        """
        corners = {}
        # Gap between wheel edge and info corners
        corner_gap = 5

        # Position each enabled corner
        corner_configs = [
            (
                "chart_info",
                self.config.corners.chart_info,
                self.config.corners.chart_info_position,
            ),
            (
                "aspect_counts",
                self.config.corners.aspect_counts,
                self.config.corners.aspect_counts_position,
            ),
            (
                "element_modality",
                self.config.corners.element_modality,
                self.config.corners.element_modality_position,
            ),
            (
                "chart_shape",
                self.config.corners.chart_shape,
                self.config.corners.chart_shape_position,
            ),
        ]

        for name, enabled, position in corner_configs:
            if not enabled:
                continue

            dims = measurements.get(name, Dimensions(100, 80))  # Fallback dims

            # Calculate position based on corner - OUTSIDE wheel bounding box
            # TESTING with large values to verify positioning is working
            if position == "top-left":
                # Position above and to the left of wheel
                pos = Position(
                    wheel_pos.x - dims.width - corner_gap,
                    wheel_pos.y - dims.height - corner_gap,
                )
            elif position == "top-right":
                # Aspect counter: TEST with 50px offset
                pos = Position(
                    wheel_pos.x + wheel_size + corner_gap + 50,
                    wheel_pos.y - dims.height - corner_gap - 50,
                )
            elif position == "bottom-left":
                # Element modality table: TEST with 50px offset
                pos = Position(
                    wheel_pos.x - dims.width - corner_gap - 50,
                    wheel_pos.y + wheel_size + corner_gap + 50,
                )
            else:  # "bottom-right"
                # Position below and to the right of wheel
                pos = Position(
                    wheel_pos.x + wheel_size + corner_gap,
                    wheel_pos.y + wheel_size + corner_gap,
                )

            corners[name] = BoundingBox(position=pos, dimensions=dims)

        # TODO: Add collision detection and auto-adjustment
        # if collisions are detected

        return corners

    def _calculate_canvas_size(
        self,
        base_wheel_size: int,
        table_layout: TableLayoutSpec,
        measurements: dict[str, Dimensions],
    ) -> Dimensions:
        """
        Calculate required canvas size based on wheel + tables + corners + header.

        Logic:
        1. Start with base wheel size
        2. Add header height if enabled
        3. Add table dimensions based on placement
        4. Add padding for margins
        5. Ensure minimum space for corner elements
        """
        padding = self.config.min_margin * 2

        # Start with wheel size + padding
        width = base_wheel_size + padding
        height = base_wheel_size + padding

        # Add header height if enabled
        if self.config.header.enabled:
            height += self.config.header.height

        # Add table dimensions based on placement

        if self.config.tables.enabled and table_layout:
            if self.config.tables.placement == "right":
                # Tables extend the width
                width += table_layout.total_width + self.config.tables.padding
                # Make sure height accommodates tallest element (wheel or tables)
                height = max(height, table_layout.total_height + padding)
            elif self.config.tables.placement == "left":
                # Tables extend the width
                width += table_layout.total_width + self.config.tables.padding
                # Make sure height accommodates tallest element (wheel or tables)
                height = max(height, table_layout.total_height + padding)
            elif self.config.tables.placement == "below":
                # Tables extend the height
                height += table_layout.total_height + self.config.tables.padding
                # Make sure width accommodates widest element (wheel or tables)
                width = max(width, table_layout.total_width + padding)

        # Ensure minimum space for corner elements
        # (They're positioned inside the wheel area, so no additional space needed)

        return Dimensions(width, height)

    def _position_wheel(
        self, canvas_dims: Dimensions, wheel_size: int, table_layout: TableLayoutSpec
    ) -> Position:
        """
        Calculate wheel position within canvas.

        Centers the wheel, accounting for table placement and header.
        """
        # Calculate header offset
        header_offset = self.config.header.height if self.config.header.enabled else 0

        if not self.config.auto_center:
            # Simple top-left positioning with margin, accounting for header
            return Position(
                self.config.min_margin, self.config.min_margin + header_offset
            )

        if not self.config.tables.enabled:
            # Simple centering when no tables
            x = (canvas_dims.width - wheel_size) / 2
            # Center wheel in the space BELOW the header
            available_height = canvas_dims.height - header_offset
            y = header_offset + (available_height - wheel_size) / 2
            return Position(x, y)

        # Adjust for table placement
        placement = self.config.tables.placement

        if placement == "right":
            # Wheel goes on the left, centered in available space
            available_width = (
                canvas_dims.width
                - table_layout.total_width
                - self.config.tables.padding
            )
            x = (available_width - wheel_size) / 2
            # Center wheel in the space BELOW the header
            available_height = canvas_dims.height - header_offset
            y = header_offset + (available_height - wheel_size) / 2

        elif placement == "left":
            # Wheel goes on the right, shifted by table width
            table_space = table_layout.total_width + self.config.tables.padding
            available_width = canvas_dims.width - table_space
            x = table_space + ((available_width - wheel_size) / 2)
            # Center wheel in the space BELOW the header
            available_height = canvas_dims.height - header_offset
            y = header_offset + (available_height - wheel_size) / 2

        elif placement == "below":
            # Wheel goes on top (but below header), centered horizontally
            x = (canvas_dims.width - wheel_size) / 2
            available_height = (
                canvas_dims.height
                - header_offset
                - table_layout.total_height
                - self.config.tables.padding
            )
            y = header_offset + (available_height - wheel_size) / 2

        else:
            # Fallback to simple centering
            x = (canvas_dims.width - wheel_size) / 2
            available_height = canvas_dims.height - header_offset
            y = header_offset + (available_height - wheel_size) / 2

        return Position(x, y)

    def _finalize_table_positions(
        self, table_layout: TableLayoutSpec, wheel_pos: Position, wheel_size: int
    ) -> dict[str, BoundingBox]:
        """
        Convert relative table positions to absolute canvas positions.

        Args:
            table_layout: The relative layout specification
            wheel_pos: Position of the wheel on canvas
            wheel_size: Size of the wheel

        Returns:
            Dictionary mapping table names to their final bounding boxes
        """
        if not self.config.tables.enabled or not table_layout.table_positions:
            return {}

        final_tables = {}
        placement = self.config.tables.placement

        for table_name, relative_pos in table_layout.table_positions.items():
            dims = table_layout.table_dimensions[table_name]

            # Calculate absolute position based on placement
            if placement == "right":
                # Tables start after the wheel + padding
                absolute_x = (
                    wheel_pos.x
                    + wheel_size
                    + self.config.tables.padding
                    + relative_pos.x
                )
                absolute_y = relative_pos.y

            elif placement == "left":
                # Tables are positioned at their relative position (already includes padding)
                absolute_x = relative_pos.x
                absolute_y = relative_pos.y

            elif placement == "below":
                # Tables start below the wheel + padding
                absolute_x = wheel_pos.x + relative_pos.x
                absolute_y = (
                    wheel_pos.y
                    + wheel_size
                    + self.config.tables.padding
                    + relative_pos.y
                )

            else:
                # Fallback
                absolute_x = relative_pos.x
                absolute_y = relative_pos.y

            final_tables[table_name] = BoundingBox(
                position=Position(absolute_x, absolute_y),
                dimensions=dims,
            )

        return final_tables

    def _calculate_margins(
        self,
        canvas_dims: Dimensions,
        wheel_pos: Position,
        wheel_size: int,
        tables: dict[str, BoundingBox],
    ) -> dict[str, float]:
        """
        Calculate actual margins between elements.

        Useful for debugging and validation.
        """
        margins = {
            "wheel_left": wheel_pos.x,
            "wheel_top": wheel_pos.y,
            "wheel_right": canvas_dims.width - (wheel_pos.x + wheel_size),
            "wheel_bottom": canvas_dims.height - (wheel_pos.y + wheel_size),
        }
        # Calculate margins to tables if present
        if tables:
            if self.config.tables.placement == "right":
                first_table = next(iter(tables.values()))
                margins["table_gap"] = first_table.position.x - (
                    wheel_pos.x + wheel_size
                )
            elif self.config.tables.placement == "left":
                first_table = next(iter(tables.values()))
                margins["table_gap"] = wheel_pos.x - (
                    first_table.position.x + first_table.dimensions.width
                )
            elif self.config.tables.placement == "below":
                first_table = next(iter(tables.values()))
                margins["table_gap"] = first_table.position.y - (
                    wheel_pos.y + wheel_size
                )

        return margins
