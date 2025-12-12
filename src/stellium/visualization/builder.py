"""
Fluent builder API for chart visualization.

Provides a convenient, discoverable API for creating chart visualizations
with presets and easy customization.
"""

from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.core.multiwheel import MultiWheel
from stellium.visualization.composer import ChartComposer
from stellium.visualization.config import (
    ChartVisualizationConfig,
    ChartWheelConfig,
    HeaderConfig,
    InfoCornerConfig,
    TableConfig,
)
from stellium.visualization.themes import ChartTheme

# Sentinel value to indicate "use theme's default colorful palette"
_USE_THEME_DEFAULT_PALETTE = object()


class ChartDrawBuilder:
    """
    Fluent builder for chart visualization with preset support.

    This builder provides a high-level, user-friendly API for creating
    chart visualizations. It wraps the lower-level draw_chart() function
    with a fluent interface and convenient presets.

    Example::

        # Simple preset
        chart.draw("chart.svg").preset_standard().save()

        # Custom configuration
        chart.draw("custom.svg").with_size(800).with_theme("midnight").with_moon_phase(
            position="top-left", show_label=True
        ).save()

        # Comparison charts
        comparison.draw("synastry.svg").preset_synastry().save()
    """

    def __init__(self, chart: CalculatedChart | Comparison | MultiWheel | MultiChart):
        """
        Initialize the builder.

        Builder starts with NO defaults - all values are None until user sets them.
        This ensures that config classes are the single source of truth for defaults.

        Args:
            chart: The chart, comparison, multiwheel, or multichart to visualize
        """
        self._chart = chart
        self._is_comparison = isinstance(chart, Comparison)
        self._is_multiwheel = isinstance(chart, MultiWheel)
        self._is_multichart = isinstance(chart, MultiChart)

        # Core settings - None = use config defaults
        self._filename: str | None = None
        self._size: int | None = None
        self._margin: int | None = None

        # Theme and palettes - None = use config defaults
        self._theme: str | None = None
        self._zodiac_palette: str | None = None
        self._aspect_palette: str | None = None
        self._planet_glyph_palette: str | None = None
        self._color_sign_info: bool | None = None

        # Tick marks - None = use config defaults
        self._show_degree_ticks: bool | None = None
        self._show_planet_ticks: bool | None = None

        # Moon phase - None = use config defaults
        self._moon_phase: bool | None = None
        self._moon_phase_position: str | None = None
        self._moon_phase_show_label: bool | None = None
        self._moon_phase_size: int | None = None
        self._moon_phase_label_size: str | None = None

        # Chart info - None = use config defaults
        self._chart_info: bool | None = None
        self._chart_info_position: str | None = None
        self._chart_info_fields: list[str] | None = None

        # Aspect counts - None = use config defaults
        self._aspect_counts: bool | None = None
        self._aspect_counts_position: str | None = None

        # Element/modality table - None = use config defaults
        self._element_modality_table: bool | None = None
        self._element_modality_table_position: str | None = None

        # Chart shape - None = use config defaults
        self._chart_shape: bool | None = None
        self._chart_shape_position: str | None = None

        # Extended canvas and tables - None = use config defaults
        self._extended_canvas: str | None = None
        self._show_position_table: bool | None = None
        self._show_aspectarian: bool | None = None
        self._show_house_cusps: bool | None = None
        self._aspectarian_mode: str | None = None
        self._aspectarian_detailed: bool | None = None
        self._table_object_types: list[str] | None = None

        # House systems - None = use config defaults
        self._house_systems: list[str] | str | None = None

        # Header - None = use config defaults (header is ON by default)
        self._header: bool | None = None
        self._header_height: int | None = None

    def with_filename(self, filename: str) -> "ChartDrawBuilder":
        """
        Set the output filename.

        Args:
            filename: Path to save the SVG file

        Returns:
            Self for chaining
        """
        self._filename = filename
        return self

    def with_size(self, size: int) -> "ChartDrawBuilder":
        """
        Set the chart size in pixels.

        Args:
            size: Chart size (width and height)

        Returns:
            Self for chaining
        """
        self._size = size
        return self

    def with_theme(self, theme: str) -> "ChartDrawBuilder":
        """
        Set the chart theme.

        Args:
            theme: Theme name (e.g., "classic", "dark", "midnight", "neon", "celestial")

        Returns:
            Self for chaining
        """
        self._theme = theme
        return self

    def with_zodiac_palette(self, palette: str | bool) -> "ChartDrawBuilder":
        """
        Set the zodiac ring color palette.

        Args:
            palette: Can be:
                - True: Use theme's default colorful palette
                - str: Specific palette name (e.g., "grey", "rainbow", "viridis", "elemental")

        Returns:
            Self for chaining

        Usage:
            # Default (no call): Monochrome using theme's zodiac ring_color

            .with_zodiac_palette(True)       # Use theme's colorful default palette
            .with_zodiac_palette("rainbow")  # Use specific rainbow palette
            .with_zodiac_palette("grey")     # Monochrome grey palette
        """
        if palette is True:
            # True: signal to use theme's default colorful palette
            self._zodiac_palette = _USE_THEME_DEFAULT_PALETTE
        else:
            # Specific palette name provided
            self._zodiac_palette = palette
        return self

    def with_aspect_palette(self, palette: str) -> "ChartDrawBuilder":
        """
        Set the aspect line color palette.

        Args:
            palette: Palette name (e.g., "classic", "dark", "blues", "plasma")

        Returns:
            Self for chaining
        """
        self._aspect_palette = palette
        return self

    def with_planet_glyph_palette(self, palette: str) -> "ChartDrawBuilder":
        """
        Set the planet glyph color palette.

        Args:
            palette: Palette name (e.g., "default", "element", "chakra", "rainbow")

        Returns:
            Self for chaining
        """
        self._planet_glyph_palette = palette
        return self

    def with_adaptive_colors(self, sign_info: bool = True) -> "ChartDrawBuilder":
        """
        Enable adaptive coloring for sign glyphs in planet info stack.

        Args:
            sign_info: Color sign glyphs in planet info based on zodiac palette

        Returns:
            Self for chaining

        Note:
            Zodiac wheel glyphs are always adaptively colored for accessibility.
            This setting only controls the tiny sign glyphs in planet info stacks.
        """
        self._color_sign_info = sign_info
        return self

    def with_degree_ticks(self, enabled: bool = True) -> "ChartDrawBuilder":
        """
        Enable or disable 1-degree tick marks on the zodiac ring.

        When enabled, adds small tick marks at every degree (1°-29° within each sign),
        in addition to the standard 5° and 10° tick marks.

        Args:
            enabled: True to show 1° ticks, False to hide them (default: True)

        Returns:
            Self for chaining

        Example:
            chart.draw().with_degree_ticks().save()  # Enable detailed ticks
            chart.draw().with_degree_ticks(False).save()  # Explicitly disable
        """
        self._show_degree_ticks = enabled
        return self

    def with_planet_ticks(self, enabled: bool = True) -> "ChartDrawBuilder":
        """
        Enable or disable colored planet position tick marks.

        When enabled (default), draws small colored tick marks on the inner edge
        of the zodiac ring at each planet's true position. The ticks use the
        planet's glyph color. When planets are spread out due to collision
        detection, the dashed connector line goes from the glyph to the tick.

        Args:
            enabled: True to show planet ticks, False to hide them (default: True)

        Returns:
            Self for chaining

        Example:
            chart.draw().with_planet_ticks(False).save()  # Disable planet ticks
        """
        self._show_planet_ticks = enabled
        return self

    def with_house_systems(self, systems: str | list[str]) -> "ChartDrawBuilder":
        """
        Configure multiple house systems to overlay on the chart.

        Args:
            systems: House system(s) to display. Can be:
                - Single system name (e.g., "Placidus")
                - List of system names (e.g., ["Placidus", "Whole Sign"])
                - "all" to display all available house systems from the chart

        Returns:
            Self for chaining

        Example:
            # Single additional system
            builder.with_house_systems("Whole Sign")

            # Multiple systems
            builder.with_house_systems(["Placidus", "Koch", "Whole Sign"])

            # All available systems
            builder.with_house_systems("all")
        """
        self._house_systems = systems
        return self

    def with_header(self, height: int | None = None) -> "ChartDrawBuilder":
        """
        Enable the chart header band.

        The header displays native information prominently at the top of the chart:
        - Single chart: Name, location (with coordinates), datetime, timezone
        - Biwheel: Two-column layout with chart1 left-aligned, chart2 right-aligned
        - Synthesis: "Composite: Name1 & Name2" with midpoint info

        When header is enabled, the chart canvas becomes taller (a rectangle instead
        of a square), and the simplified info corner shows only calculation settings
        (house system, ephemeris).

        Args:
            height: Optional custom height in pixels (default: 70)

        Returns:
            Self for chaining

        Example:
            # Default header
            chart.draw("chart.svg").with_header().save()

            # Custom header height
            chart.draw("chart.svg").with_header(height=90).save()
        """
        self._header = True
        if height is not None:
            self._header_height = height
        return self

    def without_header(self) -> "ChartDrawBuilder":
        """
        Disable the chart header band.

        When header is disabled, all native info (name, location, datetime, etc.)
        is displayed in the chart info corner instead.

        Returns:
            Self for chaining
        """
        self._header = False
        return self

    def with_moon_phase(
        self,
        position: str = "center",
        show_label: bool = True,
        size: int | None = None,
        label_size: str | None = None,
    ) -> "ChartDrawBuilder":
        """
        Configure moon phase display.

        Args:
            position: Where to place moon ("center", "top-left", "top-right", "bottom-left", "bottom-right")
            show_label: Whether to show the phase name
            size: Moon radius in pixels (defaults: 60 for center, 30-35 for corners)
            label_size: Label font size (defaults: "14px" for center, "11px" for corners)

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = position
        self._moon_phase_show_label = show_label

        # Auto-size based on position if not specified
        if size is not None:
            self._moon_phase_size = size
        elif position == "center":
            self._moon_phase_size = 60
        else:
            self._moon_phase_size = 32

        # Auto-size label based on position if not specified
        if label_size is not None:
            self._moon_phase_label_size = label_size
        elif position == "center":
            self._moon_phase_label_size = "14px"
        else:
            self._moon_phase_label_size = "11px"

        return self

    def without_moon_phase(self) -> "ChartDrawBuilder":
        """
        Disable moon phase display.

        Returns:
            Self for chaining
        """
        self._moon_phase = False
        return self

    def with_chart_info(
        self,
        position: str = "top-left",
        fields: list[str] | None = None,
    ) -> "ChartDrawBuilder":
        """
        Add chart information box.

        Args:
            position: Corner position ("top-left", "top-right", "bottom-left", "bottom-right")
            fields: Fields to display (options: "name", "location", "datetime", "timezone", "coordinates", "house_system")

        Returns:
            Self for chaining
        """
        self._chart_info = True
        self._chart_info_position = position
        self._chart_info_fields = fields
        return self

    def with_aspect_counts(self, position: str = "top-right") -> "ChartDrawBuilder":
        """
        Add aspect counts summary.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._aspect_counts = True
        self._aspect_counts_position = position
        return self

    def with_element_modality_table(
        self, position: str = "bottom-left"
    ) -> "ChartDrawBuilder":
        """
        Add element × modality cross-table.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._element_modality_table = True
        self._element_modality_table_position = position
        return self

    def with_chart_shape(self, position: str = "bottom-right") -> "ChartDrawBuilder":
        """
        Add chart shape detection display.

        Args:
            position: Corner position

        Returns:
            Self for chaining
        """
        self._chart_shape = True
        self._chart_shape_position = position
        return self

    def with_tables(
        self,
        position: str = "right",
        show_position_table: bool = True,
        show_aspectarian: bool = True,
        show_house_cusps: bool = True,
        aspectarian_mode: str = "cross_chart",
        aspectarian_detailed: bool = False,
        show_object_types: list[str] | None = None,
    ) -> "ChartDrawBuilder":
        """
        Add extended canvas with position table and/or aspectarian grid.

        This enables an extended canvas area (right, left, or below the chart)
        that can display tabular data like planetary positions and aspect grids.

        Args:
            position: Where to place the extended canvas ("right", "left", or "below")
            show_position_table: Show planetary position table
            show_aspectarian: Show aspectarian grid
            show_house_cusps: Show house cusp table (natal charts only)
            aspectarian_mode: For comparison charts, which aspects to show:
                - "cross_chart": Only cross-chart aspects (default)
                - "all": All three grids (chart1 internal, chart2 internal, cross-chart)
                - "chart1": Only chart1 internal aspects
                - "chart2": Only chart2 internal aspects
            aspectarian_detailed: If True, show orb and A/S (applying/separating)
                indicator in each cell. If False (default), show larger glyphs only.
            show_object_types: List of object types to include in tables.
                If None, uses default (planet, asteroid, point, node, angle).
                Example values: ``["planet", "asteroid", "midpoint"]`` or
                ``["planet", "asteroid", "point", "node", "angle", "arabic_part"]``

        Returns:
            Self for chaining

        Example::

            # Standard extended canvas
            builder.with_tables(position="right")

            # Position table only
            builder.with_tables(position="right", show_aspectarian=False)

            # With house cusps table (natal charts)
            builder.with_tables(position="right", show_house_cusps=True)

            # Custom aspectarian mode for synastry
            builder.with_tables(position="right", aspectarian_mode="all")

            # Detailed aspectarian with orb and applying/separating
            builder.with_tables(position="right", aspectarian_detailed=True)

            # Include midpoints and Arabic parts in tables
            builder.with_tables(
                position="right",
                show_object_types=["planet", "asteroid", "midpoint", "arabic_part"]
            )
        """
        self._extended_canvas = position
        self._show_position_table = show_position_table
        self._show_aspectarian = show_aspectarian
        self._show_house_cusps = show_house_cusps
        self._aspectarian_mode = aspectarian_mode
        self._aspectarian_detailed = aspectarian_detailed
        self._table_object_types = show_object_types
        return self

    def without_tables(self) -> "ChartDrawBuilder":
        """
        Disable extended canvas tables.

        Returns:
            Self for chaining
        """
        self._extended_canvas = None
        self._show_position_table = False
        self._show_aspectarian = False
        self._show_house_cusps = False
        self._table_object_types = None
        return self

    def with_margin(self, margin: int) -> "ChartDrawBuilder":
        """
        Set the margin around the chart.

        Args:
            margin: Margin in pixels (default: 10)

        Returns:
            Self for chaining
        """
        self._margin = margin
        return self

    # === Preset Methods ===

    def preset_minimal(self) -> "ChartDrawBuilder":
        """
        Minimal preset: Just the core chart with no decorations.

        Returns:
            Self for chaining
        """
        self._moon_phase = False
        self._chart_info = False
        self._aspect_counts = False
        self._element_modality_table = False
        self._chart_shape = False
        return self

    def preset_standard(self) -> "ChartDrawBuilder":
        """
        Standard preset: Core chart with moon phase in center.

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = None  # Auto-detect based on aspects
        self._moon_phase_show_label = True
        self._chart_info = True
        self._aspect_counts = False
        self._element_modality_table = False
        self._chart_shape = False
        return self

    def preset_detailed(self) -> "ChartDrawBuilder":
        """
        Detailed preset: Chart with info boxes and moon phase.

        Includes chart info (top-left), aspect counts (top-right),
        element/modality table (bottom-left), chart shape (bottom-right),
        and auto-positioned moon phase (center when no aspects, bottom-right
        when aspects present).

        Note: Chart shape is automatically hidden at render time when moon
        phase is positioned in bottom-right to avoid collision.

        Returns:
            Self for chaining
        """
        self._moon_phase = True
        self._moon_phase_position = None  # Auto-detect based on aspects
        self._moon_phase_show_label = True

        self._chart_info = True
        self._chart_info_position = "top-left"

        self._aspect_counts = True
        self._aspect_counts_position = "top-right"

        self._element_modality_table = True
        self._element_modality_table_position = "bottom-left"

        # Chart shape enabled - will be auto-hidden if moon phase is in bottom-right
        self._chart_shape = True
        self._chart_shape_position = "bottom-right"

        return self

    def preset_synastry(self) -> "ChartDrawBuilder":
        """
        Synastry preset: Optimized for relationship comparison charts.

        For Comparison objects, automatically enables bi-wheel layout with:
        - Inner wheel: chart1 (native/person1) planets
        - Outer wheel: chart2 (partner/transit) planets
        - Extended canvas with position table and aspectarian
        - Chart info for both people

        Returns:
            Self for chaining
        """
        if self._is_comparison:
            # Bi-wheel comparison chart
            # Moon in corner (show chart1's moon by default)
            self._moon_phase = True
            self._moon_phase_position = "bottom-right"
            self._moon_phase_show_label = True

            # Chart info for comparison metadata
            self._chart_info = True
            self._chart_info_position = "top-left"

            # Extended canvas with tables
            self._extended_canvas = "right"
            self._show_position_table = True
            self._show_aspectarian = True
            self._aspectarian_mode = (
                "cross_chart"  # Cross-chart aspects only by default
            )

            # Aspect counts for cross-chart aspects
            self._aspect_counts = True
            self._aspect_counts_position = "top-right"

        else:
            # Standard natal chart synastry preset
            # Moon in corner to make room for annotations
            self._chart_info = True
            self._chart_info_position = "top-left"
            self._moon_phase = True
            self._moon_phase_position = "bottom-right"
            self._moon_phase_show_label = True

            self._chart_info = True
            self._chart_info_position = "top-right"

            self._aspect_counts = True
            self._aspect_counts_position = "bottom-right"

        return self

    # === Execute ===

    def save(self, to_string: bool = False) -> str:
        """
        Build and save the chart visualization using the composer.

        Only user-specified values are passed to config classes.
        All other values use the config defaults (single source of truth).

        Returns:
            The filename of the saved SVG file

        Raises:
            ValueError: If required configuration is missing
        """
        # Determine chart type
        if self._is_multichart:
            chart_type = "multiwheel"  # MultiChart uses multiwheel rendering
        elif self._is_multiwheel:
            chart_type = "multiwheel"
        elif self._is_comparison:
            chart_type = "biwheel"
        else:
            chart_type = "single"

        # Build wheel config kwargs (only user-specified values)
        wheel_kwargs = {"chart_type": chart_type}
        if self._house_systems is not None:
            wheel_kwargs["house_systems"] = self._house_systems
        if self._theme is not None:
            wheel_kwargs["theme"] = ChartTheme(self._theme)
        # Handle zodiac palette
        if self._zodiac_palette is _USE_THEME_DEFAULT_PALETTE:
            # User called .with_zodiac_palette(True) → use theme's colorful default
            wheel_kwargs["zodiac_palette"] = (
                None  # Signals renderer to use theme default
            )
        elif self._zodiac_palette is not None:
            # User specified a palette name
            wheel_kwargs["zodiac_palette"] = self._zodiac_palette
        else:
            # User didn't call .with_zodiac_palette() → use monochrome
            wheel_kwargs["zodiac_palette"] = "monochrome"
        if self._aspect_palette is not None:
            wheel_kwargs["aspect_palette"] = self._aspect_palette
        if self._planet_glyph_palette is not None:
            wheel_kwargs["planet_glyph_palette"] = self._planet_glyph_palette
        if self._color_sign_info is not None:
            wheel_kwargs["color_sign_info"] = self._color_sign_info
        if self._show_degree_ticks is not None:
            wheel_kwargs["show_degree_ticks"] = self._show_degree_ticks
        if self._show_planet_ticks is not None:
            wheel_kwargs["show_planet_ticks"] = self._show_planet_ticks

        # Auto-hide chart shape if moon phase is in bottom-right (they would overlap)
        moon_in_bottom_right = (
            self._moon_phase is True and self._moon_phase_position == "bottom-right"
        )
        if moon_in_bottom_right and self._chart_shape is True:
            # Disable chart shape to avoid collision with moon phase
            self._chart_shape = False

        # Build corners config kwargs (only user-specified values)
        corners_kwargs = {}
        if self._chart_info is not None:
            corners_kwargs["chart_info"] = self._chart_info
        if self._chart_info_position is not None:
            corners_kwargs["chart_info_position"] = self._chart_info_position
        if self._chart_info_fields is not None:
            corners_kwargs["chart_info_fields"] = self._chart_info_fields
        if self._aspect_counts is not None:
            corners_kwargs["aspect_counts"] = self._aspect_counts
        if self._aspect_counts_position is not None:
            corners_kwargs["aspect_counts_position"] = self._aspect_counts_position
        if self._element_modality_table is not None:
            corners_kwargs["element_modality"] = self._element_modality_table
        if self._element_modality_table_position is not None:
            corners_kwargs["element_modality_position"] = (
                self._element_modality_table_position
            )
        if self._chart_shape is not None:
            corners_kwargs["chart_shape"] = self._chart_shape
        if self._chart_shape_position is not None:
            corners_kwargs["chart_shape_position"] = self._chart_shape_position
        if self._moon_phase is not None:
            corners_kwargs["moon_phase"] = self._moon_phase
        if self._moon_phase_position is not None:
            corners_kwargs["moon_phase_position"] = self._moon_phase_position
        if self._moon_phase_show_label is not None:
            corners_kwargs["moon_phase_show_label"] = self._moon_phase_show_label
        if self._moon_phase_size is not None:
            corners_kwargs["moon_phase_size"] = self._moon_phase_size
        if self._moon_phase_label_size is not None:
            corners_kwargs["moon_phase_label_size"] = self._moon_phase_label_size

        # Build tables config kwargs (only user-specified values)
        tables_kwargs = {}
        if self._extended_canvas is not None:
            tables_kwargs["enabled"] = True
            tables_kwargs["placement"] = self._extended_canvas
        if self._show_position_table is not None:
            tables_kwargs["show_positions"] = self._show_position_table
        if self._show_house_cusps is not None:
            tables_kwargs["show_houses"] = self._show_house_cusps
        if self._show_aspectarian is not None:
            tables_kwargs["show_aspectarian"] = self._show_aspectarian
        if self._aspectarian_mode is not None:
            tables_kwargs["aspectarian_mode"] = self._aspectarian_mode
        if self._aspectarian_detailed is not None:
            tables_kwargs["aspectarian_detailed"] = self._aspectarian_detailed
        if self._table_object_types is not None:
            tables_kwargs["object_types"] = self._table_object_types

        # Build header config kwargs (only user-specified values)
        header_kwargs = {}
        if self._header is not None:
            header_kwargs["enabled"] = self._header
        if self._header_height is not None:
            header_kwargs["height"] = self._header_height

        # Build main config kwargs (only user-specified values)
        config_kwargs: dict[str, Any] = {
            "wheel": ChartWheelConfig(**wheel_kwargs),
            "corners": InfoCornerConfig(**corners_kwargs),
            "tables": TableConfig(**tables_kwargs),
            "header": HeaderConfig(**header_kwargs)
            if header_kwargs
            else HeaderConfig(),
        }
        if self._filename is not None:
            config_kwargs["filename"] = self._filename
        if self._size is not None:
            config_kwargs["base_size"] = self._size
        if self._margin is not None:
            config_kwargs["min_margin"] = self._margin

        # Create config with only user-specified values
        config = ChartVisualizationConfig(**config_kwargs)

        # Create composer and render
        composer = ChartComposer(config)
        return composer.compose(self._chart, to_string=to_string)
