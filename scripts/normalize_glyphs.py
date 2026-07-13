#!/usr/bin/env python3
"""
Normalise data/glyphs/*.svg to the one shape the renderer is allowed to expect.

Run after adding or re-exporting a glyph:

    python scripts/normalize_glyphs.py

These SVGs are *our* data, so the sane move is to fix the data rather than teach the
renderer to cope with every dialect a drawing program can emit. `embed_svg_glyph()`
does not parse SVG; it pulls out the path data and the paint, and re-emits it. Ask it
to understand `fill:#000;fill-opacity:0` (an outline that *looks* filled), or grouped
transforms, or CSS classes, and you are reimplementing an SVG renderer badly — and the
next export from a different editor finds a corner you missed.

So: one contract, enforced by tests/test_glyph_coverage.py.

THE CONTRACT
------------
- A **square** viewBox, tight around the drawing. A 2:1 viewBox gets fitted by width
  when nested in a square box, so the glyph renders small and clipped — which is what
  the fixed stars did for their whole existence.
- Exactly one of two paint modes, and no third option:

      stroked   fill:none            + stroke:currentColor   (the bodies)
      filled    fill:currentColor    + stroke:none           (the star sigils)

  Both are needed: a body glyph is a line drawing, a star sigil is a solid shape. What
  is *not* allowed is a transparent fill sitting alongside a stroke, because "has a
  fill" then stops meaning "is filled" and every reader has to guess.
- `currentColor`, never a literal, so any consumer — chart, PDF, web page — themes it
  by setting `color`. A hardcoded #000 is invisible on a dark background, which is
  exactly what the star glyphs were.
- No editor cruft: no sodipodi/inkscape namespaces, no metadata, no CSS classes.

Requires svgelements (dev-only) for a true bezier bounding box.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from svgelements import Path as SvgPath

REPO = Path(__file__).resolve().parent.parent
GLYPHS = REPO / "src" / "stellium" / "data" / "glyphs"

# Optical breathing room around the drawing, matching the hand-drawn bodies (whose
# strokes slightly overflow a 12-unit box).
PADDING = 1.06

STROKE_WIDTH = 0.6  # in viewBox units, at the canonical 12-unit scale


def paint(prop: str, style: str, element: str) -> str | None:
    """The effective value of a paint property: `style` wins, then the attribute."""
    in_style = re.search(rf"(?:^|;)\s*{prop}\s*:\s*([^;]+)", style)
    if in_style:
        return in_style.group(1).strip()
    as_attribute = re.search(rf'\s{prop}="([^"]*)"', element)
    return as_attribute.group(1).strip() if as_attribute else None


def is_visible(prop: str, style: str, element: str) -> bool:
    """Does this paint actually draw anything?

    "Has a fill" is not "is filled": an editor may leave a fill colour in place and
    make it transparent (`fill:#000;fill-opacity:0`), which a browser draws as an
    outline. Deciding this *here*, once, is the whole point of normalising.
    """
    value = paint(prop, style, element)
    if value in (None, "", "none", "transparent"):
        return False

    opacity = paint(f"{prop}-opacity", style, element)
    if opacity is not None:
        try:
            return float(opacity) > 0
        except ValueError:
            pass
    return True


def normalise(path: Path) -> tuple[str, str]:
    """Rewrite one glyph. Returns (mode, note)."""
    source = path.read_text()

    paths = re.findall(r"<path[^>]*/?>", source, re.S)
    if not paths:
        return "skipped", "no <path> element"

    drawings: list[str] = []
    filled_votes = 0
    for element in paths:
        d = re.search(r'\sd="([^"]+)"', element, re.S)
        if not d:
            continue
        drawings.append(d.group(1))

        style = (re.search(r'style="([^"]*)"', element) or [None, ""])[1]
        has_fill = is_visible("fill", style, element)
        has_stroke = is_visible("stroke", style, element)
        if has_fill and not has_stroke:
            filled_votes += 1

    if not drawings:
        return "skipped", "no path data"

    mode = "filled" if filled_votes == len(drawings) else "stroked"

    # A square viewBox, tight around the true bezier bounds of every subpath.
    boxes = [SvgPath(d).bbox() for d in drawings]
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)

    side = max(x1 - x0, y1 - y0) * PADDING
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vx, vy = cx - side / 2, cy - side / 2

    if mode == "filled":
        style = "fill:currentColor;stroke:none;fill-rule:evenodd"
    else:
        # Keep the stroke visually constant regardless of how big the drawing's own
        # coordinate space happens to be.
        width = STROKE_WIDTH * side / 12.0
        style = (
            f"fill:none;stroke:currentColor;stroke-width:{width:.4g};"
            "stroke-linecap:round;stroke-linejoin:round"
        )

    body = "".join(f'<path style="{style}" d="{d}"/>' for d in drawings)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        f'viewBox="{vx:.4g} {vy:.4g} {side:.4g} {side:.4g}">{body}</svg>\n'
    )
    return mode, f"{len(drawings)} path{'s' if len(drawings) > 1 else ''}"


def main() -> None:
    files = sorted(GLYPHS.glob("*.svg"))
    if not files:
        sys.exit(f"no glyphs found in {GLYPHS}")

    counts: dict[str, int] = {}
    for path in files:
        mode, note = normalise(path)
        counts[mode] = counts.get(mode, 0) + 1
        print(f"  {path.stem:12s} {mode:8s} {note}")

    print()
    print(f"{len(files)} glyphs: " + ", ".join(f"{n} {m}" for m, n in counts.items()))


if __name__ == "__main__":
    main()
