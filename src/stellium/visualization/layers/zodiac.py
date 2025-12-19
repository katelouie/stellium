"""
Zodiac ring layer - renders the zodiac wheel with signs and degrees.
"""

from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
)
from stellium.visualization.core import (
    ZODIAC_GLYPHS,
    ChartRenderer,
)
from stellium.visualization.palettes import (
    ZodiacPalette,
    adjust_color_for_contrast,
    get_palette_colors,
)

__all__ = ["ZodiacLayer"]


class ZodiacLayer:
    """Renders the outer Zodiac ring, including glyphs and tick marks."""

    def __init__(
        self,
        palette: ZodiacPalette | str = ZodiacPalette.GREY,
        style_override: dict[str, Any] | None = None,
        show_degree_ticks: bool = False,
    ) -> None:
        """
        Initialize the zodiac layer.

        Args:
            palette: The color palette to use (ZodiacPalette enum, palette name, or "single_color:#RRGGBB")
            style_override: Optional style overrides
            show_degree_ticks: If True, show 1° tick marks between the 5° marks
        """
        # Try to convert string to enum, but allow pass-through for special formats
        if isinstance(palette, str):
            try:
                self.palette = ZodiacPalette(palette)
            except ValueError:
                # Not a valid enum value, pass through as-is (e.g., "single_color:#RRGGBB")
                self.palette = palette
        else:
            self.palette = palette
        self.style = style_override or {}
        self.show_degree_ticks = show_degree_ticks

    def render(
        self, renderer: ChartRenderer, dwg: svgwrite.Drawing, chart: CalculatedChart
    ) -> None:
        style = renderer.style["zodiac"]
        style.update(self.style)

        # Use renderer's zodiac palette if layer palette not explicitly set
        active_palette = self.palette
        if active_palette == ZodiacPalette.GREY and renderer.zodiac_palette:
            # If layer is using default and renderer has a palette, use renderer's
            active_palette = renderer.zodiac_palette

        # Get colors for the palette
        if active_palette == "monochrome":
            # Monochrome: use theme's ring_color for all 12 signs
            ring_color = style.get("ring_color", "#EEEEEE")
            sign_colors = [ring_color] * 12
        else:
            # Convert to enum if string
            if isinstance(active_palette, str):
                active_palette = ZodiacPalette(active_palette)
            sign_colors = get_palette_colors(active_palette)

        # Draw 12 zodiac sign wedges (30° each)
        for sign_index in range(12):
            sign_start = sign_index * 30.0
            sign_end = sign_start + 30.0
            fill_color = sign_colors[sign_index]

            # Create wedge path for this sign
            # We need to draw an arc segment (annulus wedge) from sign_start to sign_end
            x_outer_start, y_outer_start = renderer.polar_to_cartesian(
                sign_start, renderer.radii["zodiac_ring_outer"]
            )
            x_outer_end, y_outer_end = renderer.polar_to_cartesian(
                sign_end, renderer.radii["zodiac_ring_outer"]
            )
            x_inner_start, y_inner_start = renderer.polar_to_cartesian(
                sign_start, renderer.radii["zodiac_ring_inner"]
            )
            x_inner_end, y_inner_end = renderer.polar_to_cartesian(
                sign_end, renderer.radii["zodiac_ring_inner"]
            )

            # Create path: outer arc + line + inner arc (reverse) + line back
            # All signs are 30° so never need large arc flag
            path_data = f"M {x_outer_start},{y_outer_start} "
            path_data += f"A {renderer.radii['zodiac_ring_outer']},{renderer.radii['zodiac_ring_outer']} 0 0,0 {x_outer_end},{y_outer_end} "
            path_data += f"L {x_inner_end},{y_inner_end} "
            path_data += f"A {renderer.radii['zodiac_ring_inner']},{renderer.radii['zodiac_ring_inner']} 0 0,1 {x_inner_start},{y_inner_start} "
            path_data += "Z"

            dwg.add(
                dwg.path(
                    d=path_data,
                    fill=fill_color,
                    stroke="none",
                )
            )

        # Draw degree tick marks
        # Use angles line color for all tick marks
        tick_color = renderer.style["angles"]["line_color"]
        for sign_index in range(12):
            sign_start = sign_index * 30.0

            # Determine which degrees to draw ticks for
            # Always draw at 5°, 10°, 15°, 20°, 25° (0° is handled by sign boundary lines)
            # Optionally draw 1° ticks for all other degrees
            if self.show_degree_ticks:
                degrees_to_draw = list(range(1, 30))  # 1-29 (skip 0)
            else:
                degrees_to_draw = [5, 10, 15, 20, 25]

            for degree_in_sign in degrees_to_draw:
                absolute_degree = sign_start + degree_in_sign

                # Tick sizing hierarchy: 10°/20° > 5°/15°/25° > 1° ticks
                if degree_in_sign in [10, 20]:
                    tick_length = 10
                    tick_width = 0.8
                elif degree_in_sign in [5, 15, 25]:
                    tick_length = 7
                    tick_width = 0.5
                else:  # 1° ticks (smallest)
                    tick_length = 4
                    tick_width = 0.3

                # Draw tick from zodiac_ring_inner outward
                x_inner, y_inner = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_inner"]
                )
                x_outer, y_outer = renderer.polar_to_cartesian(
                    absolute_degree, renderer.radii["zodiac_ring_inner"] + tick_length
                )

                dwg.add(
                    dwg.line(
                        start=(x_outer, y_outer),
                        end=(x_inner, y_inner),
                        stroke=tick_color,
                        stroke_width=tick_width,
                    )
                )

        # Draw 12 sign boundaries and glyphs
        # Use angles line color for sign boundaries (major divisions)
        boundary_color = renderer.style["angles"]["line_color"]

        for i in range(12):
            deg = i * 30.0

            # Line
            x1, y1 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_outer"]
            )
            x2, y2 = renderer.polar_to_cartesian(
                deg, renderer.radii["zodiac_ring_inner"]
            )
            dwg.add(
                dwg.line(
                    start=(x1, y1),
                    end=(x2, y2),
                    stroke=boundary_color,
                    stroke_width=0.5,
                )
            )

            # Glyph with automatic adaptive coloring for accessibility
            glyph_deg = (i * 30.0) + 15.0
            x_glyph, y_glyph = renderer.polar_to_cartesian(
                glyph_deg, renderer.radii["zodiac_glyph"]
            )

            # Always adapt glyph color for contrast against wedge background
            # This ensures glyphs are readable on all palette backgrounds
            sign_bg_color = sign_colors[i]
            glyph_color = adjust_color_for_contrast(
                style["glyph_color"],
                sign_bg_color,
                min_contrast=4.5,
            )

            dwg.add(
                dwg.text(
                    ZODIAC_GLYPHS[i],
                    insert=(x_glyph, y_glyph),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=style["glyph_size"],
                    fill=glyph_color,
                    font_family=renderer.style["font_family_glyphs"],
                )
            )
