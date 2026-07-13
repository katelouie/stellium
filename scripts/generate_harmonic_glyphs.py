#!/usr/bin/env python3
"""
Generate the eight harmonic aspect glyphs as regular star polygons.

    python scripts/generate_harmonic_glyphs.py

WHY THESE SHAPES

The classical aspect glyphs are not mnemonics. They are the figures themselves:

    Trine    (3rd harmonic, 120°)  △   the triangle
    Square   (4th harmonic,  90°)  □   the square
    Sextile  (6th harmonic,  60°)  ⚹   the six-fold star

Each glyph *is* the regular polygon whose edge subtends the aspect's angle. The
5th, 7th and 9th harmonics were simply never given the same treatment — they
inherited ASCII initials instead (Q, bQ, S, bS, tS, N, bN, qN), which is the
convention in Solar Fire and on astro.com, and which is typography rather than
iconography.

So there is nothing to invent here, only a pattern to finish. Every harmonic
aspect is the star polygon {n/k}: place `n` points on a circle and join every
`k`-th one. Its edge subtends exactly `k · 360/n` degrees — which is the aspect.

    Quintile     72°     {5/1}   pentagon
    Biquintile  144°     {5/2}   pentagram          <- the five-pointed star
    Septile      51.43°  {7/1}   heptagon
    Biseptile   102.86°  {7/2}   heptagram, open
    Triseptile  154.29°  {7/3}   heptagram, sharp
    Novile       40°     {9/1}   nonagon
    Binovile     80°     {9/2}   nonagram, open
    Quadnovile  160°     {9/4}   nonagram, sharp

The family reads off the silhouette (count the points) and the multiple reads off
the density (open vs. sharp), which is as much as any glyph can carry at 12px.

THE CONFIRMATION

`{9/3}` is absent, and it should be: gcd(9, 3) = 3, so the figure degenerates into
three separate triangles rather than a nine-fold star — and 3 · 360/9 = 120°, which
is the trine. A "trinovile" is not a distinct aspect, and ASPECT_REGISTRY has never
listed one. The geometry predicted the registry's contents, which is the sign the
system is being *recovered* rather than imposed.

The generated paths satisfy the glyph contract by construction (see
scripts/normalize_glyphs.py); run that afterwards to snap the viewBox, or just run
this, which calls it for you.
"""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GLYPHS = REPO / "src" / "stellium" / "data" / "glyphs"

RADIUS = 5.0
CENTRE = 6.0  # a 12-unit box, matching the hand-drawn bodies

# (filename, aspect name, n, k) — k is the step, so the edge subtends k·360/n.
HARMONICS: list[tuple[str, str, int, int]] = [
    ("quintile.svg", "Quintile", 5, 1),
    ("biquintile.svg", "Biquintile", 5, 2),
    ("septile.svg", "Septile", 7, 1),
    ("biseptile.svg", "Biseptile", 7, 2),
    ("triseptile.svg", "Triseptile", 7, 3),
    ("novile.svg", "Novile", 9, 1),
    ("binovile.svg", "Binovile", 9, 2),
    ("quadnovile.svg", "Quadnovile", 9, 4),
]


def star_polygon(n: int, k: int) -> str:
    """The path data for {n/k}: n points on a circle, joined every k-th.

    A single closed path exists only when gcd(n, k) == 1 — otherwise the figure
    falls apart into gcd(n, k) disjoint pieces and is not an n-fold star at all.
    """
    if math.gcd(n, k) != 1:
        raise ValueError(
            f"{{{n}/{k}}} is degenerate: gcd({n}, {k}) = {math.gcd(n, k)}, so it is "
            f"{math.gcd(n, k)} separate figures, not one star. Its edge subtends "
            f"{k * 360 / n:g}°, which is a lower harmonic's aspect."
        )

    points = []
    for step in range(n):
        # Start at the top (-90°) so every glyph shares an upright axis.
        theta = math.radians(-90 + (step * k) * 360 / n)
        points.append(
            (CENTRE + RADIUS * math.cos(theta), CENTRE + RADIUS * math.sin(theta))
        )

    head = f"M {points[0][0]:.4f} {points[0][1]:.4f}"
    tail = " ".join(f"L {x:.4f} {y:.4f}" for x, y in points[1:])
    return f"{head} {tail} Z"


def main() -> None:
    if not GLYPHS.is_dir():
        sys.exit(f"no glyph directory at {GLYPHS}")

    style = (
        "fill:none;stroke:currentColor;stroke-width:0.6;"
        "stroke-linecap:round;stroke-linejoin:round"
    )

    for filename, aspect, n, k in HARMONICS:
        d = star_polygon(n, k)
        (GLYPHS / filename).write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
            f'viewBox="0 0 12 12"><path style="{style}" d="{d}"/></svg>\n'
        )
        print(f"  {aspect:12s} {{{n}/{k}}}  {k * 360 / n:7.2f}°  -> {filename}")

    print("\nnormalising …")
    subprocess.run(  # noqa: S603
        [sys.executable, str(REPO / "scripts" / "normalize_glyphs.py")],
        check=True,
        capture_output=True,
    )
    print(f"{len(HARMONICS)} harmonic glyphs written to {GLYPHS.relative_to(REPO)}")


if __name__ == "__main__":
    main()
