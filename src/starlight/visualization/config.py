from dataclasses import dataclass, field
from typing import Literal

from starlight.visualization.themes import ChartTheme


@dataclass(frozen=True)
class ChartWheelConfig:
    """Configuration for the main chart wheel."""

    chart_type: Literal["single", "biwheel"]

    # Radii adjustments
    # For single charts only inner radii are used
    # For biwhell charts we use both inner and outer
    radii_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            # Single chart radii
            "zodiac_outer": 0.50,
            "zodiac_inner": 0.40,
            "planets": 0.35,
            "houses_numbers": 0.22,
            "aspects_inner": 0.20,
            # Biwheel additional radii
            "biwheel_inner_planets": 0.25,  # Shrink inner wheel
            "biwheel_outer_planets": 0.50,  # Expand for outer wheel
            "biwheel_outer_houses": 0.52,  # House lines outside zodiac
        }
    )

    # Visual theme
    theme: ChartTheme | None = None
    zodiac_palette: str | None = None
    aspect_palette: str | None = "classic"
    planet_glyph_palette: str | None = "default"
    color_sign_info: bool = False


@dataclass(frozen=True)
class InfoCornerConfig:
    """Configuration for the 4 info corners."""

    chart_info: bool = True
    chart_info_position: Literal[
        "top-left", "top-right", "bottom-left", "bottom-right"
    ] = "top-left"

    aspect_counts: bool = False
    aspect_counts_position: str = "top-right"

    element_modality: bool = False
    element_modality_position: str = "bottom-left"

    chart_shape: bool = False
    chart_shape_position: str = "bottom-right"

    moon_phase: bool = True
    moon_phase_position: str | None = "bottom-right"  # None = auto-position


@dataclass(frozen=True)
class TableConfig:
    """Configuration for extended tables."""

    enabled: bool = False
    placement: Literal["right", "left", "below"] = "right"

    # Individual table toggles
    show_positions: bool = True
    show_houses: bool = True
    show_aspectarian: bool = True

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
    auto_grow_wheel: bool = True  # Grow wheel if canvas gets big
    min_margin: int = 10  # Minimum space between components


@dataclass(frozen=True)
class Dimensions:
    """Represents width and height."""

    width: float
    height: float
