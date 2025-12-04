from dataclasses import dataclass, field
from typing import Literal

from stellium.visualization.themes import ChartTheme


@dataclass(frozen=True)
class ChartWheelConfig:
    """Configuration for the main chart wheel."""

    chart_type: Literal["single", "biwheel", "multiwheel"]

    # House systems (None = use chart's default, "all" = all available, or list of names)
    house_systems: list[str] | str | None = None

    # Radii for single chart (keys match renderer.radii keys directly)
    single_radii: dict[str, float] = field(
        default_factory=lambda: {
            "zodiac_ring_outer": 0.50,
            "zodiac_ring_inner": 0.40,
            "planet_ring": 0.35,
            "house_number_ring": 0.22,
            "aspect_ring_inner": 0.20,
        }
    )

    # Radii for biwheel/comparison chart (keys match renderer.radii keys directly)
    # NOTE: Legacy biwheel renders outer chart OUTSIDE zodiac - deprecated by multiwheel_2
    biwheel_radii: dict[str, float] = field(
        default_factory=lambda: {
            "zodiac_ring_outer": 0.38,
            "zodiac_ring_inner": 0.30,
            "planet_ring_inner": 0.27,  # Inner wheel planets
            "planet_ring_outer": 0.41,  # Outer wheel planets
            "house_number_ring": 0.16,
            "aspect_ring_inner": 0.15,
            # Outer wheel house cusps
            "outer_cusp_start": 0.38,  # Start of outer house cusp line
            "outer_cusp_end": 0.48,  # End of outer house cusp line
            "outer_house_number": 0.39,  # Position of outer house numbers
            # Outer containment borders (auto-selected based on info stack visibility)
            "outer_containment_border_compact": 0.46,  # When info stacks hidden
            "outer_containment_border_full": 0.51,  # When info stacks visible
        }
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # MULTIWHEEL RADII - All charts rendered INSIDE the zodiac ring
    # Ring order: Center → Chart1 → Chart2 → ... → ChartN → Zodiac (outermost)
    # ═══════════════════════════════════════════════════════════════════════════

    # Radii for 2-chart multiwheel (replaces biwheel for inside-zodiac rendering)
    multiwheel_2_radii: dict[str, float] = field(
        default_factory=lambda: {
            # Zodiac ring (outermost, same as single)
            "zodiac_ring_outer": 0.50,
            "zodiac_ring_inner": 0.42,
            # Chart 2 ring (outer chart, just inside zodiac)
            "chart2_ring_outer": 0.42,
            "chart2_ring_inner": 0.28,
            "chart2_planet_ring": 0.38,
            "chart2_house_number": 0.29,
            # Chart 1 ring (inner chart, closest to center)
            "chart1_ring_outer": 0.28,
            "chart1_ring_inner": 0.14,
            "chart1_planet_ring": 0.24,
            "chart1_house_number": 0.15,
            # Aspect center (minimal - no lines drawn, but defines center space)
            "aspect_ring_inner": 0.14,
        }
    )

    # Radii for 3-chart multiwheel (triwheel)
    multiwheel_3_radii: dict[str, float] = field(
        default_factory=lambda: {
            # Zodiac ring (outermost)
            "zodiac_ring_outer": 0.50,
            "zodiac_ring_inner": 0.44,
            # Chart 3 ring (outermost chart)
            "chart3_ring_outer": 0.44,
            "chart3_ring_inner": 0.34,
            "chart3_planet_ring": 0.41,
            "chart3_house_number": 0.35,
            # Chart 2 ring (middle chart)
            "chart2_ring_outer": 0.34,
            "chart2_ring_inner": 0.23,
            "chart2_planet_ring": 0.30,
            "chart2_house_number": 0.24,
            # Chart 1 ring (innermost chart)
            "chart1_ring_outer": 0.23,
            "chart1_ring_inner": 0.08,
            "chart1_planet_ring": 0.19,
            "chart1_house_number": 0.11,
            # Aspect center (minimal)
            "aspect_ring_inner": 0.08,
        }
    )

    # Radii for 4-chart multiwheel (quadwheel)
    # Equal bands for charts 2/3/4 (0.09 each), slightly larger for chart1 (0.11)
    multiwheel_4_radii: dict[str, float] = field(
        default_factory=lambda: {
            # Zodiac ring (outermost)
            "zodiac_ring_outer": 0.50,
            "zodiac_ring_inner": 0.45,
            # Chart 4 ring (outermost chart) - width 0.09
            "chart4_ring_outer": 0.45,
            "chart4_ring_inner": 0.36,
            "chart4_planet_ring": 0.43,
            "chart4_house_number": 0.37,
            # Chart 3 ring - width 0.09
            "chart3_ring_outer": 0.36,
            "chart3_ring_inner": 0.27,
            "chart3_planet_ring": 0.34,
            "chart3_house_number": 0.28,
            # Chart 2 ring - width 0.09
            "chart2_ring_outer": 0.27,
            "chart2_ring_inner": 0.18,
            "chart2_planet_ring": 0.25,
            "chart2_house_number": 0.19,
            # Chart 1 ring (innermost chart) - width 0.11 (slightly larger)
            "chart1_ring_outer": 0.18,
            "chart1_ring_inner": 0.07,
            "chart1_planet_ring": 0.16,
            "chart1_house_number": 0.09,
            # Aspect center (minimal)
            "aspect_ring_inner": 0.07,
        }
    )

    # Visual theme
    theme: ChartTheme | None = None
    zodiac_palette: str | None = None
    aspect_palette: str | None = None  # None = use theme default
    planet_glyph_palette: str | None = None  # None = use theme default
    color_sign_info: bool = False

    # Tick marks
    show_degree_ticks: bool = False  # Show 1° tick marks on zodiac ring
    show_planet_ticks: bool = True  # Show colored planet position ticks

    # ═══════════════════════════════════════════════════════════════════════════
    # MULTIWHEEL GLYPH SIZING
    # Glyph sizes and info stack distances for multiwheel charts.
    # Keys are chart count (2, 3, 4). Values: glyph size string or None for default.
    # ═══════════════════════════════════════════════════════════════════════════

    # Glyph sizes per wheel count (e.g., "24px" or None for theme default 32px)
    multiwheel_glyph_sizes: dict[int, str | None] = field(
        default_factory=lambda: {
            2: None,  # Biwheel: use default 32px
            3: "22px",  # Triwheel: 75%
            4: "20px",  # Quadwheel: ~62%
        }
    )

    # Info stack distance multiplier per wheel count (smaller = closer to glyph)
    multiwheel_info_distances: dict[int, float] = field(
        default_factory=lambda: {
            2: 0.8,  # Biwheel: normal
            3: 0.8,  # Triwheel: tighter
            4: 0.8,  # Quadwheel: even tighter
        }
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # MULTIWHEEL CANVAS SCALING
    # Scale factors for base canvas size. More charts = larger canvas for clarity.
    # ═══════════════════════════════════════════════════════════════════════════

    # Canvas scale factor per wheel count (multiplied against base_size)
    multiwheel_canvas_scales: dict[int, float] = field(
        default_factory=lambda: {
            2: 1.0,  # Biwheel: same size as single chart
            3: 1.15,  # Triwheel: 15% larger
            4: 1.3,  # Quadwheel: 30% larger
        }
    )

    def get_multiwheel_canvas_scale(self, chart_count: int) -> float:
        """Get the canvas scale factor for a multiwheel with N charts.

        Args:
            chart_count: Number of charts (2, 3, or 4)

        Returns:
            Scale factor to multiply against base_size
        """
        return self.multiwheel_canvas_scales.get(chart_count, 1.0)

    def get_multiwheel_radii(self, chart_count: int) -> dict[str, float]:
        """Get the appropriate radii config for a multiwheel with N charts.

        Args:
            chart_count: Number of charts (2, 3, or 4)

        Returns:
            Radii dictionary for the specified chart count

        Raises:
            ValueError: If chart_count is not 2, 3, or 4
        """
        radii_map = {
            2: self.multiwheel_2_radii,
            3: self.multiwheel_3_radii,
            4: self.multiwheel_4_radii,
        }
        if chart_count not in radii_map:
            raise ValueError(f"MultiWheel supports 2-4 charts, got {chart_count}")
        return radii_map[chart_count]


@dataclass(frozen=True)
class HeaderConfig:
    """Configuration for the chart header band."""

    # Header toggle
    enabled: bool = True

    # Header height (pixels added to canvas)
    height: int = 70

    # Styling
    name_font_size: str = "18px"
    name_font_family: str = "Cinzel, serif"  # Elegant display font
    details_font_size: str = "12px"
    line_height: int = 16

    # Coordinate precision (decimal places)
    coord_precision: int = 4


@dataclass(frozen=True)
class InfoCornerConfig:
    """Configuration for the 4 info corners (now simplified when header is enabled)."""

    # Chart info (simplified to just house system + ephemeris when header is enabled)
    chart_info: bool = True
    chart_info_position: Literal[
        "top-left", "top-right", "bottom-left", "bottom-right"
    ] = "top-left"
    chart_info_fields: list[str] | None = None  # None = use defaults

    # Aspect counts
    aspect_counts: bool = False
    aspect_counts_position: str = "top-right"

    # Element/modality
    element_modality: bool = False
    element_modality_position: str = "bottom-left"

    # Chart shape
    chart_shape: bool = False
    chart_shape_position: str = "bottom-right"

    # Moon phase
    moon_phase: bool = True
    moon_phase_position: str | None = "bottom-right"  # None = auto-position
    moon_phase_show_label: bool = True
    moon_phase_size: int | None = None  # None = auto-size based on position
    moon_phase_label_size: str | None = None  # None = auto-size based on position


@dataclass(frozen=True)
class TableConfig:
    """Configuration for extended tables."""

    enabled: bool = False
    placement: Literal["right", "left", "below"] = "right"

    # Individual table toggles
    show_positions: bool = True
    show_houses: bool = True
    show_aspectarian: bool = True

    # Aspectarian mode (for comparison charts)
    aspectarian_mode: str = "cross_chart"  # "cross_chart", "all", "chart1", "chart2"

    # Aspectarian detailed mode - show orb and applying/separating in cells
    aspectarian_detailed: bool = False

    # Table spacing controls (tweakable)
    padding: int = 10
    gap_between_tables: int = 20
    gap_between_columns: int = 5

    # Column widths for position table (tweakable)
    position_col_widths: dict[str, int] = field(
        default_factory=lambda: {
            "planet": 80,  # Planet name + glyph
            "sign": 50,  # Sign name
            "degree": 45,  # Degree/minutes
            "house": 35,  # House number (per system)
            "speed": 25,  # Speed value
        }
    )

    # Column widths for house table
    house_col_widths: dict[str, int] = field(
        default_factory=lambda: {
            "house": 35,
            "sign": 50,
            "degree": 60,
        }
    )

    # Aspectarian settings
    aspectarian_cell_size: int = 24

    # Object filtering
    object_types: list[str] | None = None


@dataclass(frozen=True)
class ChartVisualizationConfig:
    """Complete configuration for chart visualization."""

    # Component configs
    wheel: ChartWheelConfig
    corners: InfoCornerConfig
    tables: TableConfig
    header: HeaderConfig = None  # None triggers default creation

    # Core settings
    base_size: int = 600
    filename: str = "chart.svg"

    # Auto-layout settings
    auto_center: bool = True
    auto_grow_wheel: bool = False  # Grow wheel if canvas gets big
    min_margin: int = 10  # Minimum space between components

    def __post_init__(self):
        """Create default HeaderConfig if None provided."""
        if self.header is None:
            # Use object.__setattr__ because frozen dataclass
            object.__setattr__(self, "header", HeaderConfig())


@dataclass(frozen=True)
class Dimensions:
    """Represents width and height."""

    width: float
    height: float
