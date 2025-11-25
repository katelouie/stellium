from dataclasses import dataclass, field
from typing import Literal

from starlight.visualization.themes import ChartTheme


@dataclass(frozen=True)
class ChartWheelConfig:
    """Configuration for the main chart wheel."""

    chart_type: Literal["single", "biwheel"]

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

    # Visual theme
    theme: ChartTheme | None = None
    zodiac_palette: str | None = None
    aspect_palette: str | None = None  # None = use theme default
    planet_glyph_palette: str | None = None  # None = use theme default
    color_sign_info: bool = False


@dataclass(frozen=True)
class InfoCornerConfig:
    """Configuration for the 4 info corners."""

    # Chart info
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

    # Core settings
    base_size: int = 600
    filename: str = "chart.svg"

    # Auto-layout settings
    auto_center: bool = True
    auto_grow_wheel: bool = False  # Grow wheel if canvas gets big
    min_margin: int = 10  # Minimum space between components


@dataclass(frozen=True)
class Dimensions:
    """Represents width and height."""

    width: float
    height: float
