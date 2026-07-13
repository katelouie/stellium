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
    """(registry, name, glyph, svg_filename) for everything that has a glyph."""
    for registry_name, registry in (
        ("CELESTIAL", CELESTIAL_REGISTRY),
        ("ASPECT", ASPECT_REGISTRY),
    ):
        for name, info in registry.items():
            glyph = getattr(info, "glyph", None)
            if not glyph:
                continue
            yield registry_name, name, glyph, getattr(info, "glyph_svg_path", None)


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
