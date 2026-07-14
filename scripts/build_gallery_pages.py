#!/usr/bin/env python3
"""Render the theme and palette galleries from the registries, at build time.

    python scripts/build_gallery_pages.py

The galleries used to be 1,373 lines of hand-written Markdown listing every theme and
every palette, with image paths typed in by hand. A gallery of a registry is not a
document — it is a *view* of the registry, and maintaining it by hand means it is
wrong from the first commit that adds a theme. It was: the page opened with "each of
Stellium's 13 themes" while `ChartTheme` had 14 members.

So nothing here is authored. `ChartTheme`, `ZodiacPalette`, `AspectPalette` and
`PlanetGlyphPalette` are enumerated, one chart is drawn per member, and the pages are
written around the results. Add a theme to the enum and it appears in the gallery with
no page to update — which is the only arrangement in which the gallery cannot lie.

The model is seaborn's: the thumbnail you click *is the output of the code shown on
the page it takes you to*. Same native throughout (Einstein), so the only thing that
changes between two images is the styling being demonstrated.

Generated, gitignored, rebuilt every build — like the cookbooks. There is no copy to
drift.
"""

from __future__ import annotations

import os
from pathlib import Path

from stellium import ChartBuilder
from stellium.visualization.palettes import (
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    get_aspect_palette_description,
    get_palette_description,
    get_planet_glyph_palette_description,
)
from stellium.visualization.themes import (
    ChartTheme,
    get_theme_default_aspect_palette,
    get_theme_default_palette,
    get_theme_default_planet_palette,
    get_theme_description,
)

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
OUT = DOCS / "gallery"
IMAGES = OUT / "images"

# One chart, every time. If two images differ, the styling is the only reason.
NATIVE = "Albert Einstein"

FAST = os.environ.get("STELLIUM_DOCS_FAST") == "1"


def strip_prefix(text: str, name: str) -> str:
    """ "Midnight - Elegant night sky…" -> "Elegant night sky…" — the name is the heading."""
    for sep in (" - ", " — ", ": "):
        head, _, tail = text.partition(sep)
        if tail and head.strip().lower() == name.lower():
            return tail.strip()
    return text.strip()


def draw(chart, path: Path, **style) -> None:
    d = chart.draw(str(path))
    for method, value in style.items():
        d = getattr(d, method)(value)
    d.preset_standard().save()


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    chart = ChartBuilder.from_notable(NATIVE).with_aspects().calculate()

    themes = list(ChartTheme)
    zodiacs = list(ZodiacPalette)
    aspects = list(AspectPalette)
    glyphs = list(PlanetGlyphPalette)

    if FAST:
        themes, zodiacs, aspects, glyphs = (
            themes[:3],
            zodiacs[:3],
            aspects[:3],
            glyphs[:3],
        )

    # ---- one detail page per theme -------------------------------------------------
    for theme in themes:
        name = theme.value
        zod = get_theme_default_palette(theme).value
        asp = get_theme_default_aspect_palette(theme).value
        gly = get_theme_default_planet_palette(theme).value
        blurb = strip_prefix(get_theme_description(theme), name)

        draw(chart, IMAGES / f"theme_{name}.svg", with_theme=name)

        (OUT / f"{name}.md").write_text(
            f"""# {name.title()}

{blurb}

```{{code-block}} python
:caption: {name}.py

from stellium import ChartBuilder

chart = ChartBuilder.from_notable("{NATIVE}").with_aspects().calculate()
chart.draw("{name}.svg").with_theme("{name}").preset_standard().save()
```

```{{figure}} images/theme_{name}.svg
:alt: {name} theme
```

## Its default palettes

A theme picks a palette for each of the three layers. Naming one explicitly overrides
just that layer — the rest of the theme stays put.

| Layer | Default | Override with |
|---|---|---|
| Zodiac ring | `{zod}` | `.with_zodiac_palette("...")` |
| Aspect lines | `{asp}` | `.with_aspect_palette("...")` |
| Planet glyphs | `{gly}` | `.with_planet_glyph_palette("...")` |

See the [Palette Gallery](../PALETTE_GALLERY.md) for every option, or the
[Theme Gallery](../THEME_GALLERY.md) for the other {len(list(ChartTheme)) - 1} themes.
""",
            encoding="utf-8",
        )

    # ---- the theme index: a grid you click into ------------------------------------
    cards = []
    for theme in themes:
        name = theme.value
        blurb = strip_prefix(get_theme_description(theme), name)
        cards += [
            ":::{container} st-shot",
            f"[![{name}](gallery/images/theme_{name}.svg)](gallery/{name}.md)",
            f"[{name}]{{.st-shot-label}}",
            f"[{blurb}]{{.st-shot-note}}",
            ":::",
            "",
        ]

    (DOCS / "THEME_GALLERY.md").write_text(
        f"""# Theme Gallery

A **theme** sets the whole look at once — background, zodiac ring, aspect lines and
glyphs. Pass its name to `.with_theme()`.

```python
chart.draw("out.svg").with_theme("midnight")
```

Every image below is the same chart ({NATIVE}), so the styling is the only thing that
differs. Click one for the code that made it.

::::{{container}} st-strip

{chr(10).join(cards)}
::::

Palettes are the finer controls layered on top — see the
[Palette Gallery](PALETTE_GALLERY.md).

```{{toctree}}
:hidden:
:maxdepth: 1

{chr(10).join(f"gallery/{t.value}" for t in themes)}
```
""",
        encoding="utf-8",
    )

    # ---- the palette families ------------------------------------------------------
    families = [
        (
            "Zodiac ring",
            "with_zodiac_palette",
            zodiacs,
            get_palette_description,
            "zodiac",
            "Colours the twelve sign segments of the ring.",
        ),
        (
            "Aspect lines",
            "with_aspect_palette",
            aspects,
            get_aspect_palette_description,
            "aspect",
            "Colours the lines drawn between planets in aspect.",
        ),
        (
            "Planet glyphs",
            "with_planet_glyph_palette",
            glyphs,
            get_planet_glyph_palette_description,
            "glyph",
            "Colours the planet symbols themselves.",
        ),
    ]

    sections = []
    for title, method, members, describe, slug, intro in families:
        sections += [f"## {title}", "", intro, "", "::::{container} st-strip", ""]
        for member in members:
            value = member.value
            img = IMAGES / f"{slug}_{value}.svg"
            draw(chart, img, **{method: value})
            note = strip_prefix(describe(member), value)
            sections += [
                ":::{container} st-shot",
                f"![{value}](gallery/images/{slug}_{value}.svg)",
                f"[{value}]{{.st-shot-label}}",
                f"[{note}]{{.st-shot-note}}",
                ":::",
                "",
            ]
        sections += ["::::", ""]

    (DOCS / "PALETTE_GALLERY.md").write_text(
        f"""# Palette Gallery

A **palette** controls one layer of the chart. A [theme](THEME_GALLERY.md) picks a
palette for each layer; naming one explicitly overrides just that layer.

```python
chart.draw("out.svg").with_theme("classic").with_zodiac_palette("elemental")
```

Same chart ({NATIVE}) throughout, on the `classic` theme, so only the named layer
changes.

{chr(10).join(sections)}""",
        encoding="utf-8",
    )

    print(
        f"  {len(themes)} themes, {len(zodiacs)} zodiac, {len(aspects)} aspect, "
        f"{len(glyphs)} glyph palettes"
        f"\n  -> docs/THEME_GALLERY.md, docs/PALETTE_GALLERY.md, docs/gallery/"
    )


if __name__ == "__main__":
    main()
