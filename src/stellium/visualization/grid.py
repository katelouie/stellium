"""
SVG Grid Layout (stellium.visualization.grid)

Creates subplot-like grid arrangements of multiple charts in a single SVG file.
Similar to matplotlib's subplot functionality but for astrology charts.
"""

from typing import Any

import svgwrite

from stellium.core.models import CalculatedChart, ObjectType

from .core import ChartRenderer
from .layers import AngleLayer, AspectLayer, HouseCuspLayer, PlanetLayer, ZodiacLayer
from .moon_phase import MoonPhaseLayer
from .palettes import ZodiacPalette
from .themes import ChartTheme, get_theme_default_palette


def draw_chart_grid(
    charts: list[CalculatedChart],
    filename: str = "chart_grid.svg",
    labels: list[str] | None = None,
    rows: int | None = None,
    cols: int | None = None,
    chart_size: int = 400,
    padding: int = 30,
    themes: list[ChartTheme | str] | None = None,
    zodiac_palettes: list[ZodiacPalette | str] | None = None,
    aspect_palettes: list[str] | None = None,
    planet_glyph_palettes: list[str] | None = None,
    color_sign_info: bool = False,
    color_zodiac_glyphs: bool = False,
    moon_phase: bool = True,
    background_color: str = "#FAFAFA",
) -> str:
    """
    Draw multiple charts in a grid layout in a single SVG file.

    This function creates a subplot-like arrangement of multiple charts,
    perfect for comparing different chart styles, themes, or palettes.

    Args:
        charts: List of CalculatedChart objects to render
        filename: Output SVG filename
        labels: Optional labels for each chart (displayed at bottom)
        rows: Number of rows (auto-calculated if None)
        cols: Number of columns (auto-calculated if None)
        chart_size: Size of each individual chart in pixels
        padding: Padding between charts in pixels
        themes: Optional list of themes (one per chart, or None for default)
        zodiac_palettes: Optional list of zodiac palettes (one per chart)
        aspect_palettes: Optional list of aspect palettes (one per chart)
        planet_glyph_palettes: Optional list of planet glyph palettes (one per chart)
        color_sign_info: Apply adaptive sign info coloring to all charts
        color_zodiac_glyphs: Apply adaptive zodiac glyph coloring to all charts
        moon_phase: Show moon phase in all charts
        background_color: Background color for the entire grid

    Returns:
        The filename of the saved chart grid

    Example:
        >>> from stellium import ChartBuilder
        >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
        >>> # Create grid showing same chart with different themes
        >>> draw_chart_grid(
        ...     charts=[chart] * 4,
        ...     labels=["Classic", "Dark", "Midnight", "Neon"],
        ...     themes=["classic", "dark", "midnight", "neon"],
        ...     rows=2,
        ...     cols=2,
        ... )
    """
    num_charts = len(charts)
    if num_charts == 0:
        raise ValueError("At least one chart must be provided")

    # Auto-calculate grid dimensions if not provided
    if rows is None and cols is None:
        # Default: try to make a square-ish grid
        cols = int(num_charts**0.5) + (1 if num_charts**0.5 % 1 > 0 else 0)
        rows = (num_charts + cols - 1) // cols
    elif rows is None:
        rows = (num_charts + cols - 1) // cols
    elif cols is None:
        cols = (num_charts + rows - 1) // rows

    # Ensure we have enough grid cells
    if rows * cols < num_charts:
        raise ValueError(
            f"Grid size {rows}x{cols} is too small for {num_charts} charts"
        )

    # Set up per-chart configurations (cycle if lists are too short)
    def get_item(lst: list | None, index: int, default: Any = None) -> Any:
        if lst is None:
            return default
        if len(lst) == 0:
            return default
        return lst[index % len(lst)]

    # Calculate total SVG size
    label_height = 40 if labels else 0
    total_width = cols * chart_size + (cols + 1) * padding
    total_height = rows * (chart_size + label_height) + (rows + 1) * padding

    # Create main SVG
    dwg = svgwrite.Drawing(
        filename=filename,
        size=(f"{total_width}px", f"{total_height}px"),
        viewBox=f"0 0 {total_width} {total_height}",
        profile="full",
    )

    # Add background
    dwg.add(
        dwg.rect(
            insert=(0, 0),
            size=(f"{total_width}px", f"{total_height}px"),
            fill=background_color,
        )
    )

    # Render each chart in the grid
    for i, chart in enumerate(charts):
        if i >= rows * cols:
            break  # Don't overflow the grid

        row = i // cols
        col = i % cols

        # Calculate position
        x = padding + col * (chart_size + padding)
        y = padding + row * (chart_size + label_height + padding)

        # Get configuration for this chart
        theme = get_item(themes, i)
        zodiac_palette = get_item(zodiac_palettes, i)
        aspect_palette = get_item(aspect_palettes, i)
        planet_glyph_palette = get_item(planet_glyph_palettes, i)
        label = get_item(labels, i)

        # Determine theme and palette
        if theme:
            theme_enum = ChartTheme(theme) if isinstance(theme, str) else theme
            if zodiac_palette is None:
                zodiac_palette = get_theme_default_palette(theme_enum)
        else:
            if zodiac_palette is None:
                zodiac_palette = ZodiacPalette.GREY

        # Convert zodiac_palette to string
        if hasattr(zodiac_palette, "value"):
            zodiac_palette_str = zodiac_palette.value
        else:
            zodiac_palette_str = zodiac_palette

        # Get rotation angle
        asc_object = chart.get_object("ASC")
        rotation_angle = asc_object.longitude if asc_object else 0.0

        # Create renderer for this chart
        renderer = ChartRenderer(
            size=chart_size,
            rotation=rotation_angle,
            theme=theme,
            zodiac_palette=zodiac_palette_str,
            aspect_palette=aspect_palette,
            planet_glyph_palette=planet_glyph_palette,
            color_sign_info=color_sign_info,
            color_zodiac_glyphs=color_zodiac_glyphs,
        )

        # Create a group for this chart
        chart_group = dwg.g(transform=f"translate({x},{y})")

        # Create chart elements (we'll render them into a temporary drawing
        # then copy the elements into our group)
        # This is a bit of a workaround since we can't directly share drawings

        # Create a mini-SVG for this chart
        mini_dwg = svgwrite.Drawing(size=(chart_size, chart_size))

        # Add background and borders
        mini_dwg.add(
            mini_dwg.rect(
                insert=(0, 0),
                size=(chart_size, chart_size),
                fill=renderer.style["background_color"],
            )
        )
        mini_dwg.add(
            mini_dwg.circle(
                center=(renderer.center, renderer.center),
                r=renderer.radii["outer_border"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )
        mini_dwg.add(
            mini_dwg.circle(
                center=(renderer.center, renderer.center),
                r=renderer.radii["aspect_ring_inner"],
                fill="none",
                stroke=renderer.style["border_color"],
                stroke_width=renderer.style["border_width"],
            )
        )

        # Get planets to draw
        planets_to_draw = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]

        # Assemble layers
        layers = [
            ZodiacLayer(palette=zodiac_palette),
            HouseCuspLayer(house_system_name=chart.default_house_system),
            AspectLayer(),
            PlanetLayer(planet_set=planets_to_draw, radius_key="planet_ring"),
            AngleLayer(),
        ]

        if moon_phase:
            layers.insert(3, MoonPhaseLayer())

        # Render layers
        for layer in layers:
            layer.render(renderer, mini_dwg, chart)

        # Copy all elements from mini_dwg to chart_group
        for element in mini_dwg.elements:
            chart_group.add(element)

        # Add chart group to main drawing
        dwg.add(chart_group)

        # Add label if provided
        if label:
            label_y = y + chart_size + 25
            label_x = x + chart_size // 2

            dwg.add(
                dwg.text(
                    label,
                    insert=(label_x, label_y),
                    text_anchor="middle",
                    font_family="Arial, Helvetica, sans-serif",
                    font_size="14px",
                    font_weight="bold",
                    fill="#333333",
                )
            )

    # Save the grid
    dwg.save()
    return filename


def draw_theme_comparison(
    chart: CalculatedChart,
    filename: str = "theme_comparison.svg",
    themes: list[ChartTheme | str] | None = None,
    chart_size: int = 300,
) -> str:
    """
    Create a grid comparing the same chart rendered in different themes.

    Args:
        chart: The chart to render in different themes
        filename: Output SVG filename
        themes: List of themes to compare (defaults to all built-in themes)
        chart_size: Size of each chart in pixels

    Returns:
        The filename of the saved comparison grid

    Example:
        >>> from stellium import ChartBuilder
        >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
        >>> draw_theme_comparison(chart, "einstein_themes.svg")
    """
    if themes is None:
        # Use all built-in themes
        themes = [
            ChartTheme.CLASSIC,
            ChartTheme.DARK,
            ChartTheme.MIDNIGHT,
            ChartTheme.NEON,
            ChartTheme.SEPIA,
            ChartTheme.PASTEL,
            ChartTheme.CELESTIAL,
            ChartTheme.VIRIDIS,
            ChartTheme.PLASMA,
            ChartTheme.INFERNO,
            ChartTheme.MAGMA,
            ChartTheme.CIVIDIS,
        ]

    # Create labels from theme names
    labels = [
        t.value.title() if hasattr(t, "value") else str(t).title() for t in themes
    ]

    # Create grid with one chart per theme
    return draw_chart_grid(
        charts=[chart] * len(themes),
        filename=filename,
        labels=labels,
        themes=themes,
        chart_size=chart_size,
        cols=4,  # 4 columns for nice layout
    )


def draw_palette_comparison(
    chart: CalculatedChart,
    filename: str = "palette_comparison.svg",
    palettes: list[ZodiacPalette | str] | None = None,
    theme: ChartTheme | str = ChartTheme.DARK,
    chart_size: int = 300,
    color_zodiac_glyphs: bool = True,
) -> str:
    """
    Create a grid comparing the same chart with different zodiac palettes.

    Args:
        chart: The chart to render with different palettes
        filename: Output SVG filename
        palettes: List of zodiac palettes to compare (defaults to popular ones)
        theme: Base theme to use (default: dark, works well with colorful palettes)
        chart_size: Size of each chart in pixels
        color_zodiac_glyphs: Enable adaptive zodiac glyph coloring

    Returns:
        The filename of the saved comparison grid

    Example:
        >>> from stellium import ChartBuilder
        >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
        >>> draw_palette_comparison(chart, "einstein_palettes.svg")
    """
    if palettes is None:
        # Use interesting palettes
        palettes = [
            ZodiacPalette.GREY,
            ZodiacPalette.RAINBOW,
            ZodiacPalette.ELEMENTAL,
            ZodiacPalette.VIRIDIS,
            ZodiacPalette.PLASMA,
            ZodiacPalette.INFERNO,
            ZodiacPalette.MAGMA,
            ZodiacPalette.TURBO,
        ]

    # Create labels from palette names
    labels = [
        p.value.title() if hasattr(p, "value") else str(p).title() for p in palettes
    ]

    # Create grid with same theme but different palettes
    return draw_chart_grid(
        charts=[chart] * len(palettes),
        filename=filename,
        labels=labels,
        themes=[theme] * len(palettes),
        zodiac_palettes=palettes,
        chart_size=chart_size,
        color_zodiac_glyphs=color_zodiac_glyphs,
        cols=4,
    )
