"""
HTML Reference Sheet Generator (stellium.visualization.reference_sheet)

Generates comprehensive HTML reference sheets showing all available
themes, palettes, and their colors for easy reference.
"""

from .palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    get_aspect_palette_colors,
    get_aspect_palette_description,
    get_palette_colors,
    get_palette_description,
    get_planet_glyph_color,
    get_planet_glyph_palette_description,
)
from .themes import ChartTheme, get_theme_description, get_theme_style


def generate_html_reference(
    filename: str = "stellium_color_reference.html",
    include_zodiac: bool = True,
    include_aspects: bool = True,
    include_planet_glyphs: bool = True,
    include_themes: bool = True,
) -> str:
    """
    Generate a comprehensive HTML reference sheet for all Stellium colors and palettes.

    Args:
        filename: Output HTML filename
        include_zodiac: Include zodiac palettes section
        include_aspects: Include aspect palettes section
        include_planet_glyphs: Include planet glyph palettes section
        include_themes: Include themes section

    Returns:
        The filename of the generated HTML file

    Example:
        >>> from stellium.visualization import generate_html_reference
        >>> generate_html_reference("colors.html")
    """
    html_parts = []

    # HTML header and CSS
    html_parts.append(
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stellium Color & Theme Reference</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            border-bottom: 2px solid #ddd;
            padding-bottom: 8px;
            margin-top: 40px;
        }
        .palette-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .palette-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 15px;
        }
        .palette-name {
            font-weight: bold;
            font-size: 1.1em;
            color: #333;
            margin-bottom: 5px;
        }
        .palette-description {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .color-swatches {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 4px;
            border: 1px solid #ccc;
            position: relative;
            cursor: pointer;
        }
        .color-swatch:hover::after {
            content: attr(data-color);
            position: absolute;
            bottom: -25px;
            left: 0;
            background: #333;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.75em;
            white-space: nowrap;
            z-index: 10;
        }
        .color-label {
            font-size: 0.75em;
            color: #666;
            margin-top: 4px;
            text-align: center;
        }
        .aspect-colors {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
        }
        .aspect-item {
            text-align: center;
        }
        .planet-colors {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 10px;
        }
        .planet-item {
            text-align: center;
        }
        .theme-preview {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 15px;
            align-items: start;
        }
        .theme-info {
            display: grid;
            gap: 8px;
        }
        .theme-color-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .theme-color-label {
            font-size: 0.85em;
            color: #666;
            min-width: 150px;
        }
        .theme-color-swatch {
            width: 40px;
            height: 30px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        .theme-color-value {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #888;
        }
        code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>🌟 Stellium Color & Theme Reference</h1>
    <p>
        This reference sheet shows all available color palettes and themes in the Stellium visualization system.
        Hover over color swatches to see hex values.
    </p>
"""
    )

    # Zodiac Palettes Section
    if include_zodiac:
        html_parts.append("<h2>🌈 Zodiac Wheel Palettes</h2>")
        html_parts.append(
            "<p>Color palettes for the 12 zodiac signs on the outer wheel.</p>"
        )
        html_parts.append('<div class="palette-grid">')

        for palette in ZodiacPalette:
            colors = get_palette_colors(palette)
            description = get_palette_description(palette)

            html_parts.append('<div class="palette-card">')
            html_parts.append(
                f'<div class="palette-name">{palette.value.title()}</div>'
            )
            html_parts.append(f'<div class="palette-description">{description}</div>')
            html_parts.append('<div class="color-swatches">')

            sign_names = [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces",
            ]

            for i, color in enumerate(colors):
                html_parts.append(
                    f'<div><div class="color-swatch" style="background-color: {color};" '
                    f'data-color="{color}"></div>'
                    f'<div class="color-label">{sign_names[i][:3]}</div></div>'
                )

            html_parts.append("</div></div>")

        html_parts.append("</div>")

    # Aspect Palettes Section
    if include_aspects:
        html_parts.append("<h2>🔷 Aspect Line Palettes</h2>")
        html_parts.append("<p>Color palettes for aspect lines in the chart center.</p>")
        html_parts.append('<div class="palette-grid">')

        for palette in AspectPalette:
            colors = get_aspect_palette_colors(palette)
            description = get_aspect_palette_description(palette)

            html_parts.append('<div class="palette-card">')
            html_parts.append(
                f'<div class="palette-name">{palette.value.title()}</div>'
            )
            html_parts.append(f'<div class="palette-description">{description}</div>')
            html_parts.append('<div class="aspect-colors">')

            for aspect_name, color in colors.items():
                html_parts.append(
                    f'<div class="aspect-item">'
                    f'<div class="color-swatch" style="background-color: {color};" '
                    f'data-color="{color}"></div>'
                    f'<div class="color-label">{aspect_name}</div>'
                    f"</div>"
                )

            html_parts.append("</div></div>")

        html_parts.append("</div>")

    # Planet Glyph Palettes Section
    if include_planet_glyphs:
        html_parts.append("<h2>🪐 Planet Glyph Palettes</h2>")
        html_parts.append("<p>Color palettes for planet glyphs.</p>")
        html_parts.append('<div class="palette-grid">')

        planet_names = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]

        for palette in PlanetGlyphPalette:
            description = get_planet_glyph_palette_description(palette)

            html_parts.append('<div class="palette-card">')
            html_parts.append(
                f'<div class="palette-name">{palette.value.title()}</div>'
            )
            html_parts.append(f'<div class="palette-description">{description}</div>')
            html_parts.append('<div class="planet-colors">')

            for planet_name in planet_names:
                color = get_planet_glyph_color(planet_name, palette, "#222222")
                html_parts.append(
                    f'<div class="planet-item">'
                    f'<div class="color-swatch" style="background-color: {color};" '
                    f'data-color="{color}"></div>'
                    f'<div class="color-label">{planet_name}</div>'
                    f"</div>"
                )

            html_parts.append("</div></div>")

        html_parts.append("</div>")

    # Themes Section
    if include_themes:
        html_parts.append("<h2>🎨 Chart Themes</h2>")
        html_parts.append(
            "<p>Complete visual themes with coordinated colors across all elements.</p>"
        )
        html_parts.append('<div class="palette-grid">')

        for theme in ChartTheme:
            style = get_theme_style(theme)
            description = get_theme_description(theme)

            html_parts.append('<div class="palette-card">')
            html_parts.append(f'<div class="palette-name">{theme.value.title()}</div>')
            html_parts.append(f'<div class="palette-description">{description}</div>')
            html_parts.append('<div class="theme-preview">')

            # Theme color details
            html_parts.append('<div class="theme-info">')

            theme_colors = [
                ("Background", style["background_color"]),
                ("Border", style["border_color"]),
                ("Zodiac Ring", style["zodiac"]["ring_color"]),
                ("Zodiac Line", style["zodiac"]["line_color"]),
                ("Zodiac Glyph", style["zodiac"]["glyph_color"]),
                ("Planet Glyph", style["planets"]["glyph_color"]),
                ("Planet Info", style["planets"]["info_color"]),
                ("House Line", style["houses"]["line_color"]),
                ("Angle Line", style["angles"]["line_color"]),
            ]

            for label, color in theme_colors:
                html_parts.append(
                    f'<div class="theme-color-row">'
                    f'<span class="theme-color-label">{label}:</span>'
                    f'<div class="theme-color-swatch" style="background-color: {color};"></div>'
                    f'<span class="theme-color-value">{color}</span>'
                    f"</div>"
                )

            html_parts.append("</div></div></div>")

        html_parts.append("</div>")

    # HTML footer
    html_parts.append(
        """
    <hr style="margin: 40px 0; border: none; border-top: 2px solid #ddd;">
    <p style="text-align: center; color: #888; font-size: 0.9em;">
        Generated by <strong>Stellium</strong> - Computational Astrology Library<br>
        For more information, visit the <a href="https://github.com/katelouie/stellium">GitHub repository</a>
    </p>
</body>
</html>
"""
    )

    # Write to file
    html_content = "\n".join(html_parts)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filename


def generate_zodiac_palette_reference(filename: str = "zodiac_palettes.html") -> str:
    """Generate a reference sheet showing only zodiac palettes."""
    return generate_html_reference(
        filename=filename,
        include_zodiac=True,
        include_aspects=False,
        include_planet_glyphs=False,
        include_themes=False,
    )


def generate_aspect_palette_reference(filename: str = "aspect_palettes.html") -> str:
    """Generate a reference sheet showing only aspect palettes."""
    return generate_html_reference(
        filename=filename,
        include_zodiac=False,
        include_aspects=True,
        include_planet_glyphs=False,
        include_themes=False,
    )


def generate_theme_reference(filename: str = "themes.html") -> str:
    """Generate a reference sheet showing only themes."""
    return generate_html_reference(
        filename=filename,
        include_zodiac=False,
        include_aspects=False,
        include_planet_glyphs=False,
        include_themes=True,
    )
