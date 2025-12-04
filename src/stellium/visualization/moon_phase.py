"""
Moon phase visualization layer.

Renders accurate moon phase symbols showing the illuminated portion
with curved terminator lines.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    ObjectType,
    PhaseData,
)

from .core import ChartRenderer


class MoonPhaseLayer:
    """
    Renders the moon phase on the chart.

    This layer draws an accurate representation of the moon's current phase
    using curved terminator lines to show the illuminated portion.

    The moon can be positioned in the center or in any corner, and can
    optionally display the phase name as a text label.
    """

    DEFAULT_STYLE = {
        "size": 40,  # Radius in pixels (auto-sized: 60 for center, 28 for corners)
        "border_color": "#2C3E50",
        "border_width": 2,
        "lit_color": "#F8F9FA",
        "shadow_color": "#2C3E50",
        "opacity": 0.95,
        "label_color": "#2C3E50",
        "label_size": "11px",  # Auto-sized: 14px for center, 11px for corners to match corner text
        "label_offset": 10,  # Pixels from moon symbol (above for upper corners, below for others)
    }

    def __init__(
        self,
        position: str | None = None,  # None = auto-detect based on chart content
        show_label: bool = True,
        style_override: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize moon phase layer.

        Args:
            position: Where to place the moon phase symbol.
                Options: "center", "top-left", "top-right", "bottom-left", "bottom-right", None
                If None (default), automatically chooses:
                - "bottom-right" if chart has aspects (keeps center clear)
                - "center" if chart has no aspects (makes use of empty space)
            show_label: Whether to display the phase name below the moon
            style_override: Optional style overrides
        """
        valid_positions = [
            "center",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            None,
        ]
        if position not in valid_positions:
            raise ValueError(
                f"Invalid position: {position}. Must be one of {valid_positions}"
            )

        self.position = position  # None means auto-detect later in render()
        self.show_label = show_label
        self.style = {**self.DEFAULT_STYLE, **(style_override or {})}

        # Auto-size moon and label based on position if not explicitly overridden
        if style_override is None or "size" not in style_override:
            if position == "center":
                self.style["size"] = 60  # Larger for center
            else:
                self.style["size"] = 28  # Smaller for corners

        if style_override is None or "label_size" not in style_override:
            if position == "center":
                self.style["label_size"] = "14px"
            else:
                self.style["label_size"] = "11px"  # Match corner text size

    def render(
        self,
        renderer: ChartRenderer,
        dwg: svgwrite.Drawing,
        chart: CalculatedChart,
    ) -> None:
        """
        Render the moon phase.

        Args:
            renderer: ChartRenderer instance
            dwg: SVG drawing object
            chart: Calculated chart (or MultiWheel - uses innermost chart)
        """
        from stellium.core.multiwheel import MultiWheel

        # Handle MultiWheel: use innermost chart
        actual_chart = chart.charts[0] if isinstance(chart, MultiWheel) else chart

        # Find the Moon
        moon = actual_chart.get_object("Moon")
        if not moon or not moon.phase:
            return

        # Auto-detect position if not explicitly set
        if self.position is None:
            # Smart default: bottom-right if aspects present, center if not
            if actual_chart.aspects and len(actual_chart.aspects) > 0:
                actual_position = "bottom-right"
            else:
                actual_position = "center"
        else:
            actual_position = self.position

        # Auto-size based on detected position
        if actual_position == "center":
            self.style["size"] = self.style.get("size", 60)
            self.style["label_size"] = self.style.get("label_size", "14px")
        else:
            self.style["size"] = self.style.get("size", 28)
            self.style["label_size"] = self.style.get("label_size", "11px")

        # Temporarily set position for coordinate calculation
        original_position = self.position
        self.position = actual_position

        # Access the phase data cleanly
        phase_data = moon.phase

        # Create moon phase symbol
        moon_group = self._create_moon_phase_symbol(
            dwg,
            phase_data.phase_angle,
            phase_data.illuminated_fraction,
            self.style["size"],
            self.style["border_color"],
            self.style["border_width"],
            self.style["lit_color"],
            self.style["shadow_color"],
            self.style["opacity"],
        )

        if moon_group:
            # Calculate position based on position setting
            x, y = self._get_position_coordinates(renderer)

            # Position the moon
            positioned_group = dwg.g(transform=f"translate({x}, {y})")
            for element in moon_group.elements:
                positioned_group.add(element)
            dwg.add(positioned_group)

            # Add label if requested
            if self.show_label:
                # Place label above moon for upper corners, below for others
                # Ensure label has enough padding from edge (minimum margin)
                min_margin = renderer.size * 0.03  # Match chart padding

                # Get y_offset to account for header
                y_offset = getattr(renderer, "y_offset", 0)

                if self.position in ["top-left", "top-right"]:
                    # Above the moon - ensure we don't hit top edge
                    label_y = max(
                        y - self.style["size"] - self.style["label_offset"],
                        y_offset + min_margin + 12,  # 12px for text height
                    )
                    dominant_baseline = "auto"  # Bottom of text aligns with y
                else:
                    # Below the moon - ensure we don't hit bottom edge
                    # y_offset + renderer.size is the bottom of the wheel area
                    label_y = min(
                        y + self.style["size"] + self.style["label_offset"],
                        y_offset + renderer.size - min_margin - 4,  # 4px buffer
                    )
                    dominant_baseline = "hanging"  # Top of text aligns with y

                # Get theme-aware label color from planets info_color (match corner text)
                from .palettes import adjust_color_for_contrast

                theme_text_color = renderer.style.get("planets", {}).get(
                    "info_color", self.style["label_color"]
                )
                background_color = renderer.style.get("background_color", "#FFFFFF")
                label_color = adjust_color_for_contrast(
                    theme_text_color, background_color, min_contrast=4.5
                )

                dwg.add(
                    dwg.text(
                        phase_data.phase_name,
                        insert=(x, label_y),
                        text_anchor="middle",
                        dominant_baseline=dominant_baseline,
                        font_size=self.style["label_size"],
                        fill=label_color,
                        font_family=renderer.style["font_family_text"],
                        font_weight="normal",  # Match corner text (not bold)
                    )
                )

        # Restore original position
        self.position = original_position

    def _get_position_coordinates(self, renderer: ChartRenderer) -> tuple[float, float]:
        """
        Calculate the (x, y) coordinates for moon placement based on position setting.

        Args:
            renderer: ChartRenderer instance

        Returns:
            Tuple of (x, y) coordinates
        """
        # Match chart padding for corner placement
        margin = renderer.size * 0.01

        # Get offsets for extended canvas positioning
        x_offset = getattr(renderer, "x_offset", 0)
        y_offset = getattr(renderer, "y_offset", 0)

        # For corner placement, add moon size + padding for proper inset
        if self.position != "center":
            # Use configured size from style
            moon_radius = self.style["size"]
            corner_inset = margin + moon_radius

            # For bottom corners with labels, add extra vertical space
            # to prevent label collision with bottom edge
            if self.show_label and self.position in ["bottom-left", "bottom-right"]:
                # Extract font size (e.g., "11px" -> 11)
                label_height = int(float(self.style["label_size"][:-2]))
                # Add label height + offset + small buffer to move moon up
                extra_spacing = label_height + self.style["label_offset"]
                bottom_inset = corner_inset + extra_spacing
            else:
                bottom_inset = corner_inset

            if self.position == "top-left":
                return (x_offset + corner_inset, y_offset + corner_inset)
            elif self.position == "top-right":
                return (
                    x_offset + renderer.size - corner_inset,
                    y_offset + corner_inset,
                )
            elif self.position == "bottom-left":
                return (
                    x_offset + corner_inset + 15,
                    y_offset + renderer.size - bottom_inset,
                )
            elif self.position == "bottom-right":
                return (
                    x_offset + renderer.size - corner_inset - 15,
                    y_offset + renderer.size - bottom_inset,
                )

        # Center position
        return (x_offset + renderer.center, y_offset + renderer.center)

    def _create_moon_phase_symbol(
        self,
        dwg: svgwrite.Drawing,
        phase_angle: float,
        illuminated_fraction: float,
        radius: float,
        border_color: str,
        border_width: float,
        lit_color: str,
        shadow_color: str,
        opacity: float,
    ) -> svgwrite.container.Group:
        """
        Create an SVG group containing accurate moon phase visualization.

        Args:
            dwg: SVG drawing object
            moon: Moon position with phase data
            radius: Moon radius
            border_color: Border color
            border_width: Border width
            lit_color: Color for illuminated portion
            shadow_color: Color for shadowed portion
            opacity: Overall opacity

        Returns:
            SVG group containing moon phase
        """
        # Determine if waxing or waning
        waxing = self._is_moon_waxing(phase_angle)

        # Create group
        group = dwg.g()

        # Handle special cases
        if illuminated_fraction <= 0.01:
            # New moon - completely dark
            group.add(
                dwg.circle(
                    center=(0, 0),
                    r=radius,
                    fill=shadow_color,
                    stroke=border_color,
                    stroke_width=border_width,
                    opacity=opacity,
                )
            )
            return group
        elif illuminated_fraction >= 0.99:
            # Full moon - completely lit
            group.add(
                dwg.circle(
                    center=(0, 0),
                    r=radius,
                    fill=lit_color,
                    stroke=border_color,
                    stroke_width=border_width,
                    opacity=opacity,
                )
            )
            return group

        # Start with base circle (shadow)
        group.add(
            dwg.circle(
                center=(0, 0),
                r=radius,
                fill=shadow_color,
                stroke="none",
                opacity=opacity,
            )
        )

        # Calculate and draw the terminator
        if abs(illuminated_fraction - 0.5) < 0.001:
            # Quarter moon - exactly half lit
            if waxing:
                # First quarter - right half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 1 0 {radius} Z"
            else:
                # Last quarter - left half lit
                path_d = f"M 0 {-radius} A {radius} {radius} 0 0 0 0 {radius} Z"

            group.add(
                dwg.path(d=path_d, fill=lit_color, stroke="none", opacity=opacity)
            )
        else:
            # Crescent or gibbous - curved terminator
            terminator_width = abs(2 * (illuminated_fraction - 0.5)) * radius

            if illuminated_fraction < 0.5:
                # Crescent phase
                if waxing:
                    path_d = self._create_crescent_path(radius, terminator_width, True)
                else:
                    path_d = self._create_crescent_path(radius, terminator_width, False)

                group.add(
                    dwg.path(d=path_d, fill=lit_color, stroke="none", opacity=opacity)
                )
            else:
                # Gibbous phase - fill with lit, add shadow crescent
                group.add(
                    dwg.circle(
                        center=(0, 0),
                        r=radius,
                        fill=lit_color,
                        stroke="none",
                        opacity=opacity,
                    )
                )

                if waxing:
                    path_d = self._create_crescent_path(radius, terminator_width, False)
                else:
                    path_d = self._create_crescent_path(radius, terminator_width, True)

                group.add(
                    dwg.path(
                        d=path_d, fill=shadow_color, stroke="none", opacity=opacity
                    )
                )

        # Add border
        group.add(
            dwg.circle(
                center=(0, 0),
                r=radius,
                fill="none",
                stroke=border_color,
                stroke_width=border_width,
                opacity=opacity,
            )
        )

        return group

    def _is_moon_waxing(self, phase_angle: float) -> bool:
        """
        Determine if moon is waxing based on phase angle.

        Args:
            phase_angle: Phase angle in degrees

        Returns:
            True if waxing, False if waning
        """
        normalized_angle = phase_angle % 360
        return normalized_angle <= 180

    def _create_crescent_path(
        self, radius: float, terminator_width: float, on_right: bool
    ) -> str:
        """
        Create SVG path for crescent shape with elliptical terminator.

        Args:
            radius: Moon radius
            terminator_width: Width of terminator ellipse
            on_right: True if crescent on right, False if on left

        Returns:
            SVG path string
        """
        if on_right:
            # Crescent on right side
            path = f"M 0 {-radius} "
            path += f"A {radius} {radius} 0 0 1 0 {radius} "
            path += f"A {terminator_width} {radius} 0 0 0 0 {-radius} "
            path += "Z"
        else:
            # Crescent on left side
            path = f"M 0 {-radius} "
            path += f"A {radius} {radius} 0 0 0 0 {radius} "
            path += f"A {terminator_width} {radius} 0 0 1 0 {-radius} "
            path += "Z"

        return path


def draw_moon_phase_standalone(
    phase_frac: float,
    phase_angle: float,
    filename: str = "moon_phase.svg",
    size: int = 200,
    style: dict[str, Any] | None = None,
) -> str:
    """
    Draw a standalone moon phase SVG.

    Useful for testing or standalone moon phase displays.

    Args:
        phase_frac: Illuminated fraction (0-1)
        phase_angle: Phase angle in degrees (0-360)
        filename: Output filename
        size: SVG size in pixels
        style: Style overrides

    Returns:
        Filename of saved SVG

    Example:
        # Draw a waxing crescent
        draw_moon_phase_standalone(0.25, 90, "waxing_crescent.svg")

        # Draw a full moon
        draw_moon_phase_standalone(1.0, 180, "full_moon.svg")
    """
    moon = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=0.0,
    )
    moon_phase_data = PhaseData(
        phase_angle=phase_angle,
        illuminated_fraction=phase_frac,
        elongation=0.0,
        apparent_diameter=0.0,
        apparent_magnitude=0.0,
    )
    object.__setattr__(moon, "phase", moon_phase_data)

    # Create SVG
    dwg = svgwrite.Drawing(
        filename=filename,
        size=(f"{size}px", f"{size}px"),
        viewBox=f"0 0 {size} {size}",
    )

    # Add background
    dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill="#1a1a1a"))

    # Create moon phase layer
    layer = MoonPhaseLayer(style_override=style)

    # Render (need a mock renderer/chart for the interface)
    from unittest.mock import Mock

    mock_renderer = Mock()
    mock_renderer.center = size // 2
    mock_chart = Mock()
    mock_chart.get_object = lambda name: moon if name == "Moon" else None

    layer.render(mock_renderer, dwg, mock_chart)

    dwg.save()
    return filename
