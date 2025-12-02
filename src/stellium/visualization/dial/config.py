"""
Configuration dataclasses for dial visualization.

Colors and styling are derived from themes (same as main chart) to ensure
visual consistency. The DialConfig only stores structural settings;
actual colors come from the theme at render time.
"""

from dataclasses import dataclass, field
from typing import Any

from stellium.visualization.themes import ChartTheme, get_theme_style


@dataclass
class DialRadii:
    """
    Radii configuration for dial chart rings.

    All values are multipliers of the base size (0.0 to 0.5).
    Rings are listed from outermost to innermost.
    """

    # Outer rings for additional data (transits, directions, midpoints)
    outer_ring_3: float = 0.48
    outer_ring_2: float = 0.44
    outer_ring_1: float = 0.40

    # Graduation ring (tick marks)
    graduation_outer: float = 0.36
    graduation_inner: float = 0.32

    # Planet ring (natal planets)
    planet_ring: float = 0.26

    # Inner modality wheel
    modality_outer: float = 0.20
    modality_inner: float = 0.08  # Small center hole

    def to_absolute(self, size: int) -> dict[str, float]:
        """Convert relative radii to absolute pixel values."""
        return {
            "outer_ring_3": size * self.outer_ring_3,
            "outer_ring_2": size * self.outer_ring_2,
            "outer_ring_1": size * self.outer_ring_1,
            "graduation_outer": size * self.graduation_outer,
            "graduation_inner": size * self.graduation_inner,
            "planet_ring": size * self.planet_ring,
            "modality_outer": size * self.modality_outer,
            "modality_inner": size * self.modality_inner,
        }


@dataclass
class DialGraduationConfig:
    """Configuration for graduation tick marks (structural settings only)."""

    # Tick lengths (as fraction of graduation ring width)
    tick_1_degree: float = 0.3  # Every 1°
    tick_5_degree: float = 0.5  # Every 5°
    tick_10_degree: float = 0.7  # Every 10° (if labels not shown)

    # Labels
    show_labels: bool = True
    label_interval: int = 5  # Label every N degrees
    label_font_size: str = "8px"

    # Line widths (colors come from theme)
    tick_width: float = 0.5


@dataclass
class DialCardinalConfig:
    """Configuration for cardinal point markers (structural settings only)."""

    # Which cardinal points to mark (for 90° dial: 0, 22.5, 45, 67.5)
    show_arrows: bool = True
    arrow_width: float = 2.0

    # Black accent marks on outer ring
    show_accents: bool = True
    accent_width: float = 4.0


@dataclass
class DialModalityConfig:
    """Configuration for inner modality wheel (structural settings only)."""

    # Sector styling (colors come from theme's houses.fill_color_1/2)
    sector_line_width: float = 1.0

    # Zodiac glyphs
    glyph_font_size: str = "14px"


@dataclass
class DialPlanetConfig:
    """Configuration for planet display (structural settings only)."""

    # Glyph styling
    glyph_font_size: str = "18px"

    # Tick marks at true position
    show_ticks: bool = True
    tick_width: float = 1.0
    tick_length: float = 8.0

    # Connector lines (when glyph is displaced)
    connector_dash: str = "2,2"
    connector_width: float = 0.5

    # Collision detection
    min_glyph_spacing: float = 15.0  # Minimum degrees between glyph centers


@dataclass
class DialPointerConfig:
    """Configuration for 360° dial pointer (structural settings only)."""

    width: float = 2.0
    arrow_size: float = 10.0
    show_center_circle: bool = True
    center_circle_radius: float = 5.0


@dataclass
class DialConfig:
    """
    Complete configuration for dial visualization.

    This is the main config class that contains all dial settings.
    Colors are derived from the theme at render time for consistency
    with the main chart visualization system.
    """

    # Core settings
    dial_degrees: int = 90  # 90, 45, or 360
    size: int = 600
    rotation: float = 0.0  # What degree points "up" (12 o'clock)

    # Theme (uses same themes as main chart)
    theme: ChartTheme | str | None = None

    # Output
    filename: str = "dial.svg"

    # Sub-configs (structural only - colors from theme)
    radii: DialRadii = field(default_factory=DialRadii)
    graduation: DialGraduationConfig = field(default_factory=DialGraduationConfig)
    cardinal: DialCardinalConfig = field(default_factory=DialCardinalConfig)
    modality: DialModalityConfig = field(default_factory=DialModalityConfig)
    planet: DialPlanetConfig = field(default_factory=DialPlanetConfig)
    pointer: DialPointerConfig = field(default_factory=DialPointerConfig)

    # Layer toggles
    show_graduation: bool = True
    show_cardinal_points: bool = True
    show_modality_wheel: bool = True
    show_planets: bool = True
    show_midpoints: bool = True
    show_pointer: bool = False  # Only for 360° dial

    # Midpoint settings
    midpoint_ring: str = "outer_ring_1"
    midpoint_notation: str = "full"  # "full", "abbreviated", "tick"

    # Pointer settings (360° dial)
    pointer_target: float | str = 0.0  # Degree or planet name

    def __post_init__(self):
        """Validate configuration and normalize theme."""
        if self.dial_degrees not in (90, 45, 360):
            raise ValueError(
                f"dial_degrees must be 90, 45, or 360, got {self.dial_degrees}"
            )

        # Normalize theme to ChartTheme enum
        if isinstance(self.theme, str):
            self.theme = ChartTheme(self.theme)

        # Auto-enable pointer for 360° dial if target is specified
        if self.dial_degrees == 360 and self.pointer_target != 0.0:
            self.show_pointer = True

    def get_style(self) -> dict[str, Any]:
        """
        Get the complete style dictionary from the theme.

        Returns theme-derived colors for all dial elements.
        Falls back to classic theme if no theme specified.
        """
        theme = self.theme or ChartTheme.CLASSIC
        return get_theme_style(theme)

    def get_dial_style(self) -> "DialStyle":
        """
        Get dial-specific style settings derived from the theme.

        Maps theme colors to dial elements for easy access by layers.
        """
        style = self.get_style()
        return DialStyle.from_theme_style(style)


@dataclass
class DialStyle:
    """
    Dial-specific style settings derived from a theme.

    This maps the main chart theme colors to dial-specific elements,
    providing a convenient interface for layers to access colors.
    """

    # Background
    background_color: str = "#FFFFFF"

    # Graduation ring
    graduation_ring_color: str = "#EEEEEE"
    graduation_tick_color: str = "#333333"
    graduation_label_color: str = "#444444"

    # Cardinal points
    cardinal_arrow_color: str = "#000000"
    cardinal_accent_color: str = "#000000"

    # Modality wheel
    modality_sector_color_1: str = "#F5F5F5"
    modality_sector_color_2: str = "#FFFFFF"
    modality_line_color: str = "#CCCCCC"
    modality_glyph_color: str = "#555555"

    # Planets
    planet_glyph_color: str = "#222222"
    planet_tick_color: str = "#666666"
    planet_connector_color: str = "#999999"

    # Pointer (360° dial)
    pointer_color: str = "#000000"

    # Fonts
    font_family_glyphs: str = '"Symbola", "Noto Sans Symbols", serif'
    font_family_text: str = '"Arial", "Helvetica", sans-serif'

    @classmethod
    def from_theme_style(cls, style: dict[str, Any]) -> "DialStyle":
        """
        Create DialStyle from a theme style dictionary.

        Maps theme colors to dial elements:
        - Graduation uses zodiac ring colors
        - Cardinal points use angle colors
        - Modality uses house fill colors
        - Planets use planet colors
        """
        zodiac = style.get("zodiac", {})
        houses = style.get("houses", {})
        angles = style.get("angles", {})
        planets = style.get("planets", {})

        return cls(
            # Background
            background_color=style.get("background_color", "#FFFFFF"),
            # Graduation - use zodiac styling
            graduation_ring_color=zodiac.get("ring_color", "#EEEEEE"),
            graduation_tick_color=zodiac.get("line_color", "#BBBBBB"),
            graduation_label_color=zodiac.get("glyph_color", "#555555"),
            # Cardinal points - use angle styling (prominent)
            cardinal_arrow_color=angles.get("line_color", "#555555"),
            cardinal_accent_color=angles.get("line_color", "#555555"),
            # Modality wheel - use house styling
            modality_sector_color_1=houses.get("fill_color_1", "#F5F5F5"),
            modality_sector_color_2=houses.get("fill_color_2", "#FFFFFF"),
            modality_line_color=houses.get("line_color", "#CCCCCC"),
            modality_glyph_color=zodiac.get("glyph_color", "#555555"),
            # Planets - use planet styling
            planet_glyph_color=planets.get("glyph_color", "#222222"),
            planet_tick_color=planets.get("info_color", "#444444"),
            planet_connector_color=houses.get("line_color", "#CCCCCC"),
            # Pointer - use angle line color
            pointer_color=angles.get("line_color", "#555555"),
            # Fonts
            font_family_glyphs=style.get(
                "font_family_glyphs",
                '"Symbola", "Noto Sans Symbols", serif',
            ),
            font_family_text=style.get(
                "font_family_text",
                '"Arial", "Helvetica", sans-serif',
            ),
        )
