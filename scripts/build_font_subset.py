#!/usr/bin/env python3
"""
Rebuild data/fonts/NotoSansMath-Subset.ttf.

Noto Sans Math is the last resort in the symbol-font fallback chain: it carries the
handful of codepoints Noto Sans Symbols 1 and 2 do not, and without it those glyphs are
tofu boxes in both the SVG and the PDF. At the time of writing that means Semisquare
(U+2220), Contraparallel (U+22D5), Pholus (U+2B30) and Part of Fortune (U+2297).

The full face is 967 KB for a handful of glyphs, so we ship a **subset** — currently
8 KB. The OFL permits this: Noto Sans Math declares no Reserved Font Name, and the
subsetter is told to keep the name table so the copyright and licence notices travel
with the file. See data/fonts/LICENSE-FONTS.txt.

The codepoints are derived from every glyph source Stellium actually draws from — the
registries *and* the legacy dicts in visualization/core.py, which are not vestigial
(`get_glyph()` falls back to them, and `Part of Fortune` lives only there). Run this
after adding a glyph that needs a codepoint the other faces lack; `pytest
tests/test_glyph_coverage.py` will tell you when that is.

    python scripts/build_font_subset.py

Requires fontTools and network access (it fetches the upstream face).
"""

from __future__ import annotations

import urllib.request
import warnings
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parent.parent
FONT_DIR = REPO / "src" / "stellium" / "data" / "fonts"
OUT = FONT_DIR / "NotoSansMath-Subset.ttf"

UPSTREAM = (
    "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/"
    "fonts/NotoSansMath/hinted/ttf/NotoSansMath-Regular.ttf"
)

SYMBOL_FLOOR = 0x2000  # below this a "glyph" is an ASCII abbreviation, not a symbol


def wanted_codepoints() -> set[int]:
    """Every symbol codepoint Stellium can emit, from every source get_glyph() reads."""
    from stellium.core.registry import (
        ASPECT_REGISTRY,
        CELESTIAL_REGISTRY,
        FIXED_STARS_REGISTRY,
    )
    from stellium.visualization.core import (
        ANGLE_GLYPHS,
        PLANET_GLYPHS,
        ZODIAC_GLYPHS,
    )

    glyphs: list[str] = []
    for registry in (CELESTIAL_REGISTRY, ASPECT_REGISTRY, FIXED_STARS_REGISTRY):
        glyphs += [getattr(o, "glyph", "") or "" for o in registry.values()]
    glyphs += list(PLANET_GLYPHS.values())
    glyphs += list(ANGLE_GLYPHS.values())
    glyphs += list(ZODIAC_GLYPHS)

    return {ord(c) for g in glyphs for c in g if ord(c) >= SYMBOL_FLOOR}


def main() -> None:
    wanted = wanted_codepoints()

    source = REPO / ".NotoSansMath-Regular.tmp.ttf"
    print(f"fetching {UPSTREAM.rsplit('/', 1)[-1]} …")
    urllib.request.urlretrieve(UPSTREAM, source)  # noqa: S310 - pinned upstream

    font = TTFont(source)
    available: set[int] = set()
    for table in font["cmap"].tables:
        available |= set(table.cmap.keys())

    keep = sorted(wanted & available)
    print(f"Noto Sans Math covers {len(keep)} of the {len(wanted)} symbols we emit")

    options = subset.Options()
    options.name_IDs = ["*"]  # the OFL notice must survive into the subset
    options.name_legacy = True
    options.notdef_outline = True
    options.recalc_bounds = True

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=keep)
    subsetter.subset(font)
    font.save(OUT)
    source.unlink()

    print(f"wrote {OUT.relative_to(REPO)} — {OUT.stat().st_size / 1024:.1f} KB")
    print("  " + " ".join(f"U+{c:04X}" for c in keep))


if __name__ == "__main__":
    main()
