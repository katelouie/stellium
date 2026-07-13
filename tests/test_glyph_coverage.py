"""Can every glyph we emit actually be *drawn*?

A glyph has exactly two honest ways to reach a page:

1. a **bundled SVG** — a hand-drawn path, no font needed; or
2. a **Unicode codepoint that a bundled font actually contains**.

Anything else renders as a tofu box (□) or, worse, silently as something else. And
nothing complains: fonts substitute quietly, SVG readers substitute quietly, Typst
substitutes quietly. A missing glyph is not an error anywhere in the stack — it is
just a chart that looks wrong to the person holding it.

So it has to be a test, because no human will notice it in review, and we will not
notice it locally: our own machines have Apple Symbols and a repo-root `assets/`
directory, and our users have neither.

Two real bugs sit behind this file:

- The glyph SVGs lived in a repo-root `assets/glyphs/`, referenced by the *relative*
  path `"assets/glyphs/pholus.svg"`. Not in the wheel — so for every pip user, 25
  bodies fell through to a Unicode fallback. Pholus's is U+2B30, which exists in **no
  font on any platform**, and Sedna's was the literal string `"Sed"`.
- Three glyphs (Semisquare ∠, Contraparallel ⋕, Pholus ⬰) are in none of the fonts we
  bundle, so even with the SVGs shipping they had nowhere to come from.
"""

from pathlib import Path

import pytest

pytest.importorskip("fontTools", reason="fontTools is needed to read font cmaps")

from fontTools.ttLib import TTFont  # noqa: E402

from stellium.core.registry import (  # noqa: E402
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
)
from stellium.data.paths import find_glyph_svg, glyph_svg_dir  # noqa: E402
from stellium.presentation.typst_runtime import font_paths  # noqa: E402

# Below this, a "glyph" is ASCII (an abbreviation like "Asc" or "MC"), which any font
# renders. Only the symbol range needs a font that actually covers it.
SYMBOL_FLOOR = 0x2000


def _bundled_codepoints() -> set[int]:
    """Every codepoint present in any font we ship."""
    covered: set[int] = set()
    for directory in font_paths():
        for face in sorted(Path(directory).glob("*.[to]tf")):
            try:
                font = TTFont(face, fontNumber=0, lazy=True)
                for table in font["cmap"].tables:
                    covered |= set(table.cmap.keys())
                font.close()
            except Exception:  # a face we cannot parse is a face we cannot rely on
                continue
    return covered


def _glyph_entries():
    """(source, name, glyph, svg_filename) for everything that has a glyph.

    Includes the **legacy dicts** in `visualization/core.py`, not just the registries.
    They are not vestigial: `get_glyph()` falls back to them, so `Part of Fortune` —
    which lives only there — was rendering as ⊗ (U+2297), a codepoint in none of our
    bundled fonts. It was tofu in every chart with Arabic Parts, and this test walked
    straight past it because it only looked at the registries.
    """
    from stellium.core.registry import FIXED_STARS_REGISTRY, QUALITY_REGISTRY
    from stellium.visualization.core import (
        ANGLE_GLYPHS,
        PLANET_GLYPHS,
        ZODIAC_GLYPHS,
    )

    for registry_name, registry in (
        ("CELESTIAL", CELESTIAL_REGISTRY),
        ("ASPECT", ASPECT_REGISTRY),
        ("FIXED_STARS", FIXED_STARS_REGISTRY),
        ("QUALITY", QUALITY_REGISTRY),
    ):
        for name, info in registry.items():
            glyph = getattr(info, "glyph", None)
            if not glyph:
                continue
            yield registry_name, name, glyph, getattr(info, "glyph_svg_path", None)

    for name, glyph in PLANET_GLYPHS.items():
        yield "PLANET_GLYPHS", name, glyph, None
    for name, glyph in ANGLE_GLYPHS.items():
        yield "ANGLE_GLYPHS", name, glyph, None
    for index, glyph in enumerate(ZODIAC_GLYPHS):
        yield "ZODIAC_GLYPHS", f"sign {index + 1}", glyph, None


def test_the_bundled_glyph_directory_ships_and_is_not_empty():
    directory = glyph_svg_dir()
    assert directory.is_dir(), f"the packaged glyph directory is missing: {directory}"
    assert list(directory.glob("*.svg")), "no glyph SVGs in the package"


def test_every_registry_svg_reference_resolves():
    """A registry entry pointing at a glyph file that isn't there is the bug that
    made 25 bodies render as tofu for every pip user."""
    missing = [
        f"{name} -> {svg}"
        for _reg, name, _glyph, svg in _glyph_entries()
        if svg and find_glyph_svg(svg) is None
    ]
    assert not missing, "registry glyph SVGs that do not resolve:\n  " + "\n  ".join(
        missing
    )


def test_glyph_svg_paths_are_bare_filenames_not_paths():
    """They used to be `assets/glyphs/x.svg`, resolved against the repo root — which
    is meaningless once installed, and against the *cwd* if you weren't careful."""
    offenders = [
        f"{name} -> {svg}"
        for _reg, name, _glyph, svg in _glyph_entries()
        if svg and ("/" in svg or "\\" in svg)
    ]
    assert not offenders, (
        "glyph_svg_path must be a bare filename resolved against the packaged glyph "
        "directory, not a path:\n  " + "\n  ".join(offenders)
    )


def test_every_glyph_can_actually_be_drawn():
    """THE test. Either a bundled SVG, or a codepoint a bundled font contains.

    Nothing in the rendering stack will tell you when this is false — fonts, SVG
    readers and Typst all substitute silently.
    """
    covered = _bundled_codepoints()
    assert covered, "no bundled fonts found — cannot verify glyph coverage"

    unrenderable = []
    for registry, name, glyph, svg in _glyph_entries():
        if svg and find_glyph_svg(svg) is not None:
            continue  # drawn as a path; needs no font at all
        for char in glyph:
            if ord(char) < SYMBOL_FLOOR:
                continue  # plain ASCII; every font has it
            if ord(char) not in covered:
                unrenderable.append(
                    f"{registry} {name}: {char!r} (U+{ord(char):04X}) is in no "
                    f"bundled font and has no SVG"
                )

    assert not unrenderable, (
        "these glyphs cannot be drawn — they will render as tofu boxes:\n  "
        + "\n  ".join(unrenderable)
        + "\n\nFix by adding an SVG to stellium/data/glyphs/ and pointing the "
        "registry entry at it, or by bundling a font that covers the codepoint."
    )


# ---------------------------------------------------------------------------
# fixed stars — three separate bugs, all of which rendered silently
# ---------------------------------------------------------------------------


def test_fixed_stars_resolve_to_their_drawn_glyph_not_a_generic_star():
    """A fixed star lives in BOTH registries.

    CELESTIAL_REGISTRY carries a generic ★; FIXED_STARS_REGISTRY carries the real
    hand-drawn sigil. `get_glyph()` used to consult only the former, so eight drawn
    star glyphs were unreachable and every star rendered as the same anonymous ★.
    Algol passed by pure accident — its celestial entry happened to name the same file.
    """
    from stellium.core.registry import FIXED_STARS_REGISTRY
    from stellium.visualization.core import get_glyph

    drawn = [n for n, s in FIXED_STARS_REGISTRY.items() if s.glyph_svg_path]
    assert drawn, "expected some fixed stars to have hand-drawn glyphs"

    generic = [n for n in drawn if get_glyph(n)["type"] != "svg"]
    assert not generic, (
        f"these stars have a drawn glyph that get_glyph() cannot reach, so they "
        f"render as a generic ★: {generic}"
    )


# ---------------------------------------------------------------------------
# THE GLYPH CONTRACT
# ---------------------------------------------------------------------------
#
# `embed_svg_glyph()` does not parse SVG — it lifts out the path data and the paint and
# re-emits them. So the glyphs have to conform to it, rather than it growing a parser
# for every dialect a drawing program can produce. These SVGs are our own data; the
# sane move is to fix the data.
#
# Run `python scripts/normalize_glyphs.py` and these all pass by construction.


def _glyph_files():
    from stellium.data.paths import glyph_svg_dir

    return sorted(glyph_svg_dir().glob("*.svg"))


def test_glyph_svgs_are_square_so_they_are_not_shrunk_and_clipped():
    """`embed_svg_glyph` nests the SVG in a SQUARE box using the file's own viewBox.

    The star glyphs shipped with a 2:1 landscape viewBox (52.9 x 26.5), so
    preserveAspectRatio fitted the *width* and they rendered at ~57% scale with their
    tops and bottoms clipped off.
    """
    import re

    skewed = []
    for svg in _glyph_files():
        box = re.search(r'viewBox="([^"]+)"', svg.read_text())
        assert box, f"{svg.name} has no viewBox"
        _, _, w, h = (float(v) for v in box.group(1).split())
        if abs(w - h) > 0.01 * max(w, h):
            skewed.append(f"{svg.name} ({w:g} x {h:g})")

    assert not skewed, (
        "glyph SVGs must have a square viewBox or they are scaled down and clipped "
        "when embedded:\n  " + "\n  ".join(skewed)
    )


def test_every_glyph_is_either_stroked_or_filled_and_says_so_plainly():
    """Two paint modes, and no third option:

        stroked   fill:none         + stroke:currentColor    (the bodies)
        filled    fill:currentColor + stroke:none            (the star sigils)

    Both are needed — a body glyph is a line drawing, a star sigil is a solid shape.
    What is *not* allowed is a transparent fill sitting next to a stroke
    (`fill:#000;fill-opacity:0`, which a drawing program emits happily). A browser
    renders that as an outline, but "has a fill" then stops meaning "is filled", and
    the renderer — which only looks at `fill:` — draws a solid blob instead. Exactly
    one glyph shipped like that, and it would have rendered as an ink splat.
    """
    import re

    offenders = []
    for svg in _glyph_files():
        text = svg.read_text()
        for element in re.findall(r"<path[^>]*/?>", text, re.S):
            style = (re.search(r'style="([^"]*)"', element) or [None, ""])[1]

            fill = re.search(r"(?:^|;)\s*fill\s*:\s*([^;]+)", style)
            stroke = re.search(r"(?:^|;)\s*stroke\s*:\s*([^;]+)", style)
            fill = fill.group(1).strip() if fill else None
            stroke = stroke.group(1).strip() if stroke else None

            stroked = fill == "none" and stroke == "currentColor"
            filled = fill == "currentColor" and stroke == "none"

            if not (stroked or filled):
                offenders.append(
                    f"{svg.name}: fill={fill!r} stroke={stroke!r} — must be either "
                    f"(none, currentColor) or (currentColor, none)"
                )
            if "opacity" in style:
                offenders.append(
                    f"{svg.name}: carries an opacity. A transparent fill beside a "
                    f"stroke is an outline that the renderer reads as a solid shape."
                )

    assert not offenders, (
        "glyph SVGs violate the contract — run `python scripts/normalize_glyphs.py`:"
        "\n  " + "\n  ".join(offenders)
    )


def test_glyph_svgs_theme_themselves():
    """`currentColor`, never a literal.

    A hardcoded #000 is invisible on a dark background — which is precisely what the
    star glyphs were, on every dark theme, for their whole existence.
    """
    import re

    literals = [
        svg.name
        for svg in _glyph_files()
        if re.search(r"(?:fill|stroke)\s*:\s*#[0-9a-fA-F]{3,8}", svg.read_text())
    ]
    assert not literals, (
        "these glyphs hardcode a colour instead of inheriting it, so they cannot be "
        f"themed: {literals}"
    )


def test_glyph_svgs_carry_no_editor_cruft():
    """No sodipodi/inkscape namespaces, no metadata, no CSS classes.

    The renderer pulls paths out with a regex. Anything else in the file is at best
    dead weight in the wheel and at worst something it will misread.
    """
    offenders = []
    for svg in _glyph_files():
        text = svg.read_text()
        for junk in ("sodipodi", "inkscape", "<metadata", "<style", "class="):
            if junk in text:
                offenders.append(f"{svg.name}: contains {junk!r}")

    assert not offenders, "run `python scripts/normalize_glyphs.py`:\n  " + "\n  ".join(
        offenders
    )


def test_filled_glyphs_are_recoloured_by_the_theme_not_left_black():
    """Two drawing conventions live in the bundle, and both must theme.

        bodies (Pholus, Eris)  fill:none  + stroke:<colour>   -> an outline
        stars  (Sirius, Algol) fill:<colour> + stroke:none     -> a solid shape

    `embed_svg_glyph` used to theme the stroke and copy the *file's* fill through
    verbatim, so the filled star glyphs stayed #000000 whatever the theme — black on
    black on every dark theme, and nothing anywhere said so.
    """
    import svgwrite

    from stellium.visualization.core import embed_svg_glyph, get_glyph

    themed = "#F0B95F"
    for name in ("Sirius", "Aldebaran"):  # filled
        dwg = svgwrite.Drawing(size=(100, 100))
        embed_svg_glyph(dwg, get_glyph(name)["value"], 50, 50, 40, fill_color=themed)
        markup = dwg.tostring()
        assert f'fill="{themed}"' in markup, f"{name}'s fill was not themed"
        assert "#000" not in markup, f"{name} still carries a hardcoded black"

    for name in ("Pholus", "Eris"):  # stroked
        dwg = svgwrite.Drawing(size=(100, 100))
        embed_svg_glyph(dwg, get_glyph(name)["value"], 50, 50, 40, fill_color=themed)
        assert f'stroke="{themed}"' in dwg.tostring(), f"{name}'s stroke was not themed"


# ---------------------------------------------------------------------------
# The harmonic aspects: is the drawn glyph geometrically *true*?
# ---------------------------------------------------------------------------


def test_harmonic_aspect_glyphs_subtend_their_own_angle():
    """Each harmonic glyph must be the star polygon whose edge *is* the aspect.

    This is the rule the classical glyphs already follow — △ is the trine because a
    triangle's edge subtends 120°, □ is the square because a square's subtends 90° —
    and the 5th/7th/9th harmonics were simply never given the same treatment. So the
    glyph is not decorative and "it looks like a star" is not the standard: the angle
    between two vertices joined by the path must equal the aspect's angle, or the
    glyph is quietly claiming to be a different aspect.

    A drawing can be checked against a number, so it should be.
    """
    import math
    import re

    from stellium.core.registry import get_aspects_by_category

    harmonics = [a for a in get_aspects_by_category("Harmonic") if a.glyph_svg_path]
    assert len(harmonics) == 8, (
        "expected 8 drawn harmonic aspects, found "
        f"{[a.name for a in harmonics]} — did a glyph_svg_path go missing?"
    )

    for aspect in harmonics:
        svg_file = find_glyph_svg(aspect.glyph_svg_path)
        assert svg_file is not None, f"{aspect.name}: {aspect.glyph_svg_path} missing"

        d = re.search(r'\sd="([^"]+)"', svg_file.read_text()).group(1)
        points = [
            (float(x), float(y))
            for x, y in re.findall(r"[ML]\s*(-?[\d.]+)\s+(-?[\d.]+)", d)
        ]
        assert len(points) >= 5, f"{aspect.name}: only {len(points)} vertices"

        # The centre of a regular polygon is the mean of its vertices.
        cx = sum(x for x, _ in points) / len(points)
        cy = sum(y for _, y in points) / len(points)

        bearings = [math.degrees(math.atan2(y - cy, x - cx)) for x, y in points]
        for i in range(len(bearings)):
            step = abs(bearings[(i + 1) % len(bearings)] - bearings[i]) % 360
            subtended = min(step, 360 - step)  # unsigned, and every harmonic is < 180°
            assert abs(subtended - aspect.angle) < 0.05, (
                f"{aspect.name} is drawn subtending {subtended:.2f}° but the aspect "
                f"is {aspect.angle:.2f}° — the glyph depicts the wrong aspect"
            )


def test_no_harmonic_glyph_is_a_degenerate_star():
    """{9/3} is three triangles, not a nine-fold star — and it is *also* the trine.

    A star polygon {n/k} is a single closed figure only when gcd(n, k) == 1. Where it
    isn't, the edge subtends a *lower* harmonic's angle (3·360/9 = 120° — the trine),
    which is exactly why ASPECT_REGISTRY has never carried a "trinovile". If one ever
    appears, it is a duplicate of an aspect we already have under another name, and
    its glyph would be a lie about which aspect it is.
    """
    from math import gcd

    from stellium.core.registry import get_aspects_by_category

    for aspect in get_aspects_by_category("Harmonic"):
        if not aspect.family:
            continue
        n = {"Quintile Series": 5, "Septile Series": 7, "Novile Series": 9}[
            aspect.family
        ]
        k = round(aspect.angle * n / 360)
        assert gcd(n, k) == 1, (
            f"{aspect.name} is {{{n}/{k}}}, which degenerates into {gcd(n, k)} "
            f"figures — it is not a {n}-fold aspect but a {360 * gcd(n, k) / n:g}° one"
        )
        assert abs(k * 360 / n - aspect.angle) < 0.01, (
            f"{aspect.name}'s angle {aspect.angle}° is not a {n}th harmonic"
        )
