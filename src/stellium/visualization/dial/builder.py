"""
Dial Chart Builder (stellium.visualization.dial.builder)

Fluent API for creating dial chart visualizations.
"""

from typing import TYPE_CHECKING

from stellium.core.models import CalculatedChart, CelestialPosition
from stellium.visualization.dial.config import DialConfig
from stellium.visualization.dial.layers import (
    DialBackgroundLayer,
    DialCardinalLayer,
    DialGraduationLayer,
    DialMidpointLayer,
    DialModalityLayer,
    DialOuterRingLayer,
    DialPlanetLayer,
    DialPointerLayer,
)
from stellium.visualization.dial.renderer import DialRenderer
from stellium.visualization.themes import ChartTheme

if TYPE_CHECKING:
    pass


class DialDrawBuilder:
    """
    Fluent builder for dial chart visualization.

    Provides a convenient API for creating Uranian/Hamburg school dial charts
    with support for 90°, 45°, and 360° dials.

    Example::

        # Basic 90° dial
        chart.draw_dial("dial.svg").save()

        # With theme
        chart.draw_dial("dial.svg").with_theme("midnight").save()

        # With transits on outer ring
        chart.draw_dial("dial.svg", degrees=90)
            .with_outer_ring(transit_chart.get_planets(), label="Transits")
            .save()

        # 360° dial with pointer
        chart.draw_dial("dial.svg", degrees=360)
            .with_pointer(pointing_to="Sun")
            .save()

        # Minimal dial without midpoints
        chart.draw_dial("dial.svg")
            .without_midpoints()
            .save()
    """

    def __init__(
        self,
        chart: CalculatedChart,
        filename: str = "dial.svg",
        dial_degrees: int = 90,
    ):
        """
        Initialize the dial builder.

        Args:
            chart: The chart to visualize
            filename: Output SVG filename
            dial_degrees: Dial size (90, 45, or 360)
        """
        self._chart = chart
        self._filename = filename
        self._dial_degrees = dial_degrees

        # Configuration
        self._size: int = 600
        self._theme: ChartTheme | str | None = None
        self._rotation: float = 0.0

        # Layer toggles
        self._show_graduation: bool = True
        self._show_cardinal_points: bool = True
        self._show_modality_wheel: bool = True
        self._show_planets: bool = True
        self._show_midpoints: bool = True
        self._show_pointer: bool = False

        # TNO and Uranian settings (important for Uranian astrology)
        self._include_tnos: bool = True
        self._include_uranian: bool = True

        # Midpoint settings
        self._midpoint_ring: str = "outer_ring_1"
        self._midpoint_notation: str = "full"

        # Outer rings (for transits, directions, etc.)
        self._outer_rings: list[
            tuple[list[CelestialPosition], str, str, str | None]
        ] = []

        # Pointer settings (360° dial)
        self._pointer_target: float | str = 0.0

    # =========================================================================
    # Configuration Methods
    # =========================================================================

    def with_filename(self, filename: str) -> "DialDrawBuilder":
        """Set the output filename."""
        self._filename = filename
        return self

    def with_size(self, size: int) -> "DialDrawBuilder":
        """
        Set the dial size in pixels.

        Args:
            size: Dial diameter in pixels (default: 600)
        """
        self._size = size
        return self

    def with_theme(self, theme: str | ChartTheme) -> "DialDrawBuilder":
        """
        Set the visual theme.

        Uses the same themes as the main chart visualization:
        - "classic" (default), "dark", "midnight", "neon", "sepia", "pastel", "celestial"
        - Data science themes: "viridis", "plasma", "inferno", "magma", "cividis", "turbo"

        Args:
            theme: Theme name or ChartTheme enum
        """
        self._theme = theme
        return self

    def with_rotation(self, rotation: float) -> "DialDrawBuilder":
        """
        Set the dial rotation.

        By default, 0° is at the top (12 o'clock). This shifts which degree
        appears at the top.

        Args:
            rotation: Degrees to rotate (positive = clockwise)
        """
        self._rotation = rotation
        return self

    # =========================================================================
    # Layer Toggle Methods
    # =========================================================================

    def without_graduation(self) -> "DialDrawBuilder":
        """Hide the graduation tick marks and labels."""
        self._show_graduation = False
        return self

    def without_cardinal_points(self) -> "DialDrawBuilder":
        """Hide the cardinal point markers."""
        self._show_cardinal_points = False
        return self

    def without_modality_wheel(self) -> "DialDrawBuilder":
        """Hide the inner modality wheel."""
        self._show_modality_wheel = False
        return self

    def without_planets(self) -> "DialDrawBuilder":
        """Hide the planet glyphs."""
        self._show_planets = False
        return self

    def without_tnos(self) -> "DialDrawBuilder":
        """
        Exclude Trans-Neptunian Objects from the dial.

        By default, TNOs (Eris, Sedna, Makemake, Haumea, Orcus, Quaoar) are
        included because they are important in Uranian astrology. Use this
        to show only traditional planets.
        """
        self._include_tnos = False
        return self

    def with_tnos(self) -> "DialDrawBuilder":
        """
        Include Trans-Neptunian Objects on the dial.

        TNOs are included by default. This method is provided for clarity
        when you want to explicitly enable them after disabling.
        """
        self._include_tnos = True
        return self

    def without_uranian(self) -> "DialDrawBuilder":
        """
        Exclude Hamburg/Uranian hypothetical planets from the dial.

        By default, the 8 Uranian planets (Cupido, Hades, Zeus, Kronos,
        Apollon, Admetos, Vulkanus, Poseidon) are included because they
        are fundamental to Uranian astrology. Use this to exclude them.
        """
        self._include_uranian = False
        return self

    def with_uranian(self) -> "DialDrawBuilder":
        """
        Include Hamburg/Uranian hypothetical planets on the dial.

        Uranian planets are included by default. This method is provided
        for clarity when you want to explicitly enable them after disabling.
        """
        self._include_uranian = True
        return self

    def with_midpoints(
        self,
        ring: str = "outer_ring_1",
        notation: str = "full",
    ) -> "DialDrawBuilder":
        """
        Show midpoints on an outer ring.

        Midpoints are enabled by default. Use this to customize.

        Args:
            ring: Which ring to display on ("outer_ring_1", "outer_ring_2", "outer_ring_3")
            notation: "full" (☉/☽), "abbreviated", or "tick"
        """
        self._show_midpoints = True
        self._midpoint_ring = ring
        self._midpoint_notation = notation
        return self

    def without_midpoints(self) -> "DialDrawBuilder":
        """Hide midpoints."""
        self._show_midpoints = False
        return self

    # =========================================================================
    # Outer Ring Methods
    # =========================================================================

    def with_outer_ring(
        self,
        positions: list[CelestialPosition],
        ring: str = "outer_ring_2",
        label: str = "",
        color: str | None = None,
    ) -> "DialDrawBuilder":
        """
        Add positions to an outer ring.

        Use this to display transit planets, solar arc directions,
        progressed positions, etc.

        Args:
            positions: List of CelestialPosition objects to display
            ring: Which ring to use ("outer_ring_1", "outer_ring_2", "outer_ring_3")
            label: Optional label for this ring
            color: Optional color override for glyphs

        Example::

            # Add transit planets
            chart.draw_dial("dial.svg")
                .with_outer_ring(transit_chart.get_planets(), label="Transits")
                .save()
        """
        self._outer_rings.append((positions, ring, label, color))
        return self

    # =========================================================================
    # Pointer Methods (360° dial)
    # =========================================================================

    def with_pointer(self, pointing_to: float | str = 0.0) -> "DialDrawBuilder":
        """
        Add a rotatable pointer (primarily for 360° dials).

        Args:
            pointing_to: Where the pointer should point. Can be:
                - A degree value (0-360 for 360° dial, 0-90 for 90° dial)
                - A planet name (e.g., "Sun", "Moon") - will point to that planet's position

        Example::

            # Point to 45°
            chart.draw_dial("dial.svg", degrees=360).with_pointer(45).save()

            # Point to natal Sun
            chart.draw_dial("dial.svg", degrees=360).with_pointer("Sun").save()
        """
        self._show_pointer = True
        self._pointer_target = pointing_to
        return self

    def without_pointer(self) -> "DialDrawBuilder":
        """Hide the pointer."""
        self._show_pointer = False
        return self

    # =========================================================================
    # Build and Save
    # =========================================================================

    def save(self, to_string: bool = False) -> str:
        """
        Build and save the dial chart.

        Args:
            to_string: If True, return SVG as string instead of saving to file

        Returns:
            Filename of saved SVG, or SVG string if to_string=True
        """
        # Build config
        config = DialConfig(
            dial_degrees=self._dial_degrees,
            size=self._size,
            rotation=self._rotation,
            theme=self._theme,
            filename=self._filename,
            show_graduation=self._show_graduation,
            show_cardinal_points=self._show_cardinal_points,
            show_modality_wheel=self._show_modality_wheel,
            show_planets=self._show_planets,
            show_midpoints=self._show_midpoints,
            show_pointer=self._show_pointer,
            midpoint_ring=self._midpoint_ring,
            midpoint_notation=self._midpoint_notation,
            pointer_target=self._pointer_target,
        )

        # Create renderer
        renderer = DialRenderer(config)

        # Create drawing
        dwg = renderer.create_drawing()

        # Build and render layers
        layers = self._create_layers(config, renderer)
        for layer in layers:
            layer.render(renderer, dwg, self._chart)

        # Save or return string
        if to_string:
            return dwg.tostring()
        else:
            dwg.save()
            return self._filename

    def _create_layers(self, config: DialConfig, renderer: DialRenderer) -> list:
        """Create the layer stack based on configuration."""
        layers = []

        # Background (always first)
        layers.append(DialBackgroundLayer())

        # Modality wheel (drawn under other elements)
        if config.show_modality_wheel:
            layers.append(DialModalityLayer())

        # Graduation ring
        if config.show_graduation:
            layers.append(DialGraduationLayer())

        # Cardinal points
        if config.show_cardinal_points:
            layers.append(DialCardinalLayer())

        # Planets (includes TNOs and Uranian planets by default for Uranian astrology)
        if config.show_planets:
            layers.append(
                DialPlanetLayer(
                    include_tnos=self._include_tnos,
                    include_uranian=self._include_uranian,
                )
            )

        # Midpoints
        if config.show_midpoints:
            layers.append(
                DialMidpointLayer(
                    ring=config.midpoint_ring,
                    notation=config.midpoint_notation,
                )
            )

        # Outer rings (transits, directions, etc.)
        for positions, ring, label, color in self._outer_rings:
            layers.append(
                DialOuterRingLayer(
                    positions=positions,
                    ring=ring,
                    label=label,
                    glyph_color=color,
                )
            )

        # Pointer (on top)
        if config.show_pointer:
            pointer_deg = self._resolve_pointer_target(config.pointer_target)
            layers.append(DialPointerLayer(pointing_to=pointer_deg))

        return layers

    def _resolve_pointer_target(self, target: float | str) -> float:
        """
        Resolve pointer target to a dial degree.

        If target is a planet name, find that planet's position.
        """
        if isinstance(target, str):
            # Look up planet position
            planet = self._chart.get_object(target)
            if planet:
                # Compress to dial degrees
                return planet.longitude % self._dial_degrees
            else:
                # Default to 0 if planet not found
                return 0.0
        else:
            return float(target)
