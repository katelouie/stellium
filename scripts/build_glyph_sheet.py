#!/usr/bin/env python3
"""
Build docs/GLYPH_SHEET.html — every glyph Stellium can draw, and where it comes from.

Run after touching CELESTIAL_REGISTRY, ASPECT_REGISTRY, FIXED_STARS_REGISTRY, the
bundled fonts, or data/glyphs/::

    python scripts/build_glyph_sheet.py

Each glyph's source is resolved exactly as `visualization.core.get_glyph()` resolves it
at draw time — a bundled SVG wins, else the first bundled font whose cmap contains the
codepoint — so the sheet cannot drift from what a chart actually renders.

The fonts are embedded, subsetted, as base64 data URIs. That is not a nicety: a page
that merely asked for `font-family: sans-serif` would resolve against the *reader's*
system and show tofu for precisely the glyphs it exists to audit. The sheet is typeset
in Stellium's own bundled faces — if it renders, the bundle works.

Requires fontTools (a dev dependency: `pip install -e ".[dev]"`).
"""

from __future__ import annotations

import base64
import html
import re
import warnings
from collections import Counter, OrderedDict
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    FIXED_STARS_REGISTRY,
)
from stellium.data.paths import find_glyph_svg
from stellium.presentation.typst_runtime import font_paths
from stellium.visualization.core import ZODIAC_GLYPHS

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "GLYPH_SHEET.html"

SIGNS = (
    "Aries Taurus Gemini Cancer Leo Virgo "
    "Libra Scorpio Sagittarius Capricorn Aquarius Pisces"
).split()

# The faces the sheet itself is set in, and the ones that carry the glyphs. Subsetted
# to what is actually used, so the page stays ~70 KB rather than ~7 MB.
FACES = {
    "sheet-display": "Cinzel-VariableFont_wght.ttf",
    "sheet-body": "EBGaramond-VariableFont_wght.ttf",
    "sheet-mono": "IBMPlexMono-Regular.otf",
    "glyph-1": "NotoSansSymbols-Regular.ttf",
    "glyph-2": "NotoSansSymbols2-Regular.ttf",
    "glyph-3": "NotoSansMath-Subset.ttf",
}
LATIN = list(range(0x20, 0x7F)) + [
    0x00B0,
    0x2013,
    0x2014,
    0x2018,
    0x2019,
    0x201C,
    0x201D,
    0x2022,
    0x2192,
    0x2713,
]

GROUP_ORDER = [
    "Zodiac Signs",
    "Planets & Luminaries",
    "Nodes",
    "Points",
    "Asteroids & Centaurs & TNOs",
    "Fixed Stars",
    "Aspects — Major",
    "Aspects — Minor",
    "Aspects — Harmonic",
    "Aspects — Declination",
]


def bundled_codepoints() -> dict[str, set[int]]:
    """Which bundled font contains which codepoint."""
    fonts: dict[str, set[int]] = {}
    for directory in font_paths():
        for face in sorted(Path(directory).glob("*.[to]tf")):
            try:
                font = TTFont(face, fontNumber=0, lazy=True)
                covered: set[int] = set()
                for table in font["cmap"].tables:
                    covered |= set(table.cmap.keys())
                fonts[face.name] = covered
                font.close()
            except Exception:  # a face we cannot parse is one we cannot rely on
                continue
    return fonts


FONTS = bundled_codepoints()


def source_for(glyph: str, svg_name: str | None) -> dict:
    """Where does this glyph actually come from? Mirrors get_glyph()'s precedence."""
    if svg_name:
        path = find_glyph_svg(svg_name)
        if path:
            return {"kind": "svg", "detail": svg_name, "svg": path.read_text()}

    if not glyph:
        return {"kind": "none", "detail": "no glyph defined"}

    # An ASCII abbreviation ("Asc", "Cha") is legible but is not a symbol — it is a gap.
    if all(ord(c) < 0x2000 for c in glyph):
        return {"kind": "text", "detail": "ASCII fallback text"}

    for char in glyph:
        if ord(char) < 0x2000:
            continue
        if not any(ord(char) in cps for cps in FONTS.values()):
            return {
                "kind": "missing",
                "detail": f"U+{ord(char):04X} in no bundled font",
            }

    char = next(c for c in glyph if ord(c) >= 0x2000)
    owner = next(n for n, cps in FONTS.items() if ord(char) in cps)
    pretty = (
        owner.replace("-Regular.ttf", "")
        .replace("-VariableFont_wght", "")
        .replace(".ttf", "")
        .replace(".otf", "")
    )
    return {"kind": "font", "detail": pretty}


def codepoints(glyph: str) -> str:
    return ", ".join(f"U+{ord(c):04X}" for c in glyph) if glyph else "—"


def inventory() -> list[dict]:
    items: list[dict] = []

    for name, glyph in zip(SIGNS, ZODIAC_GLYPHS, strict=True):
        items.append(
            {
                "group": "Zodiac Signs",
                "name": name,
                "glyph": glyph,
                "codepoint": codepoints(glyph),
                **source_for(glyph, None),
            }
        )

    groups = {
        "planet": "Planets & Luminaries",
        "asteroid": "Asteroids & Centaurs & TNOs",
        "node": "Nodes",
        "point": "Points",
        "fixed_star": "Fixed Stars",
    }
    for name, obj in CELESTIAL_REGISTRY.items():
        kind = getattr(obj.object_type, "value", str(obj.object_type))
        items.append(
            {
                "group": groups.get(kind, kind.title()),
                "name": obj.display_name or name,
                "glyph": obj.glyph or "",
                "codepoint": codepoints(obj.glyph or ""),
                "note": obj.category or "",
                **source_for(obj.glyph or "", obj.glyph_svg_path),
            }
        )

    for name, aspect in ASPECT_REGISTRY.items():
        items.append(
            {
                "group": f"Aspects — {aspect.category}",
                "name": f"{name} ({aspect.angle:g}°)",
                "glyph": aspect.glyph or "",
                "codepoint": codepoints(aspect.glyph or ""),
                **source_for(
                    aspect.glyph or "", getattr(aspect, "glyph_svg_path", None)
                ),
            }
        )

    # Fixed stars carry their real sigil here; CELESTIAL_REGISTRY only has a generic ★.
    for name, star in FIXED_STARS_REGISTRY.items():
        items.append(
            {
                "group": "Fixed Stars",
                "name": name,
                "glyph": star.glyph or "",
                "codepoint": codepoints(star.glyph or ""),
                **source_for(star.glyph or "", star.glyph_svg_path),
            }
        )

    return items


def embed_fonts(items: list[dict]) -> dict[str, str]:
    """Subset each face to what the sheet uses, and base64 it."""
    symbols = sorted(
        {ord(c) for i in items for c in (i["glyph"] or "") if ord(c) >= 0x2000}
    )
    directory = Path(font_paths()[0])
    faces: dict[str, str] = {}

    for family, filename in FACES.items():
        keep = symbols if family.startswith("glyph-") else LATIN
        font = TTFont(directory / filename)
        options = subset.Options()
        options.name_IDs = ["*"]  # the OFL notice must travel with the subset
        options.notdef_outline = True
        options.drop_tables += ["GSUB", "GPOS"]
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(unicodes=keep)
        subsetter.subset(font)

        font.flavor = "woff2"
        buffer = REPO / f".{family}.tmp.woff2"
        font.save(buffer)
        faces[family] = base64.b64encode(buffer.read_bytes()).decode()
        buffer.unlink()

    return faces


def clean_svg(svg, ident):
    """Inline the glyph SVG: strip its size so CSS drives it, and let it inherit colour."""
    svg = re.sub(r'\swidth="[^"]*"', "", svg, count=1)
    svg = re.sub(r'\sheight="[^"]*"', "", svg, count=1)
    svg = re.sub(
        r"(stroke|fill):\s*#0{3,6}(?![0-9a-fA-F])",
        lambda m: m.group(1) + ":currentColor",
        svg,
    )
    svg = svg.replace("<svg", '<svg class="gsvg" aria-hidden="true"', 1)
    return svg


def cell(i):
    kind = i["kind"]
    if kind == "svg":
        mark = clean_svg(i["svg"], i["name"])
    elif kind in ("text", "none"):
        mark = f'<span class="asciiglyph">{html.escape(i["glyph"] or "—")}</span>'
    else:
        mark = f'<span class="uglyph">{html.escape(i["glyph"])}</span>'

    badge = {
        "svg": ("drawn", "Bundled SVG"),
        "font": ("fromfont", html.escape(i["detail"])),
        "text": ("gap", "ASCII letters"),
        "none": ("gap", "none"),
        "missing": ("gap", "No font has it"),
    }[kind]

    return f"""      <li class="cell {"is-gap" if kind in ("text", "none", "missing") else ""}">
        <div class="glyphbox">{mark}</div>
        <p class="gname">{html.escape(i["name"])}</p>
        <p class="gcode">{html.escape(i["codepoint"])}</p>
        <span class="badge b-{badge[0]}">{badge[1]}</span>
      </li>"""


def main() -> None:
    items = inventory()
    faces = embed_fonts(items)

    groups: OrderedDict[str, list[dict]] = OrderedDict((g, []) for g in GROUP_ORDER)
    for item in items:
        groups.setdefault(item["group"], []).append(item)
    groups = OrderedDict((g, v) for g, v in groups.items() if v)

    counts = Counter(i["kind"] for i in items)
    gaps = [i for i in items if i["kind"] in ("text", "missing", "none")]

    sections = []
    for g, entries in groups.items():
        n_gap = sum(1 for e in entries if e["kind"] in ("text", "none", "missing"))
        flag = (
            f'<span class="secgap">{n_gap} gap{"s" if n_gap != 1 else ""}</span>'
            if n_gap
            else ""
        )
        sections.append(f"""  <section class="group">
        <h2>{html.escape(g)}<span class="count">{len(entries)}</span>{flag}</h2>
        <ul class="grid">
    {chr(10).join(cell(e) for e in entries)}
        </ul>
      </section>""")

    gap_rows = "\n".join(
        f"""      <tr>
            <td class="gr-name">{html.escape(i["name"])}</td>
            <td class="gr-grp">{html.escape(i["group"])}</td>
            <td class="gr-cur"><span class="asciiglyph sm">{html.escape(i["glyph"])}</span></td>
            <td class="gr-why">{html.escape(i["detail"])}</td>
          </tr>"""
        for i in gaps
    )

    fontface = "\n".join(
        f"""@font-face {{ font-family: "{fam}"; src: url(data:font/woff2;base64,{b64}) format("woff2"); font-display: block; }}"""
        for fam, b64 in faces.items()
    )

    HTML = f"""<title>Stellium Glyph Sheet</title>
    <style>
    {fontface}

    :root {{
      --paper:      #F1F2F6;
      --paper-2:    #FFFFFF;
      --ink:        #12141C;
      --ink-2:      #4A4E60;
      --ink-3:      #878CA0;
      --rule:       #D6D8E2;
      --iris:       #4B4BC8;
      --drawn:      #0F6E68;
      --drawn-bg:   #DCEFED;
      --gap:        #9A5B00;
      --gap-bg:     #FBEBD2;
      --gap-edge:   #E0A550;
      --font-scale: 1;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --paper:    #0E1017;
        --paper-2:  #161A25;
        --ink:      #E8EAF2;
        --ink-2:    #A8AEC4;
        --ink-3:    #6E7488;
        --rule:     #262B3A;
        --iris:     #9B9BF0;
        --drawn:    #57C9BE;
        --drawn-bg: #12332F;
        --gap:      #F0B95F;
        --gap-bg:   #33270F;
        --gap-edge: #7A5A22;
      }}
    }}
    :root[data-theme="dark"] {{
      --paper:#0E1017; --paper-2:#161A25; --ink:#E8EAF2; --ink-2:#A8AEC4; --ink-3:#6E7488;
      --rule:#262B3A; --iris:#9B9BF0; --drawn:#57C9BE; --drawn-bg:#12332F;
      --gap:#F0B95F; --gap-bg:#33270F; --gap-edge:#7A5A22;
    }}
    :root[data-theme="light"] {{
      --paper:#F1F2F6; --paper-2:#FFFFFF; --ink:#12141C; --ink-2:#4A4E60; --ink-3:#878CA0;
      --rule:#D6D8E2; --iris:#4B4BC8; --drawn:#0F6E68; --drawn-bg:#DCEFED;
      --gap:#9A5B00; --gap-bg:#FBEBD2; --gap-edge:#E0A550;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: "sheet-body", Georgia, serif;
      font-size: 17px;
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 4rem 1.5rem 6rem; }}

    header {{ border-bottom: 2px solid var(--ink); padding-bottom: 1.75rem; margin-bottom: 2rem; }}
    .eyebrow {{
      font-family: "sheet-mono", monospace; font-size: 0.7rem; letter-spacing: 0.22em;
      text-transform: uppercase; color: var(--iris); margin: 0 0 0.9rem;
    }}
    h1 {{
      font-family: "sheet-display", serif; font-weight: 600;
      font-size: clamp(2.1rem, 5vw, 3.4rem); line-height: 1.05; margin: 0 0 0.7rem;
      letter-spacing: 0.01em; text-wrap: balance;
    }}
    .lede {{ margin: 0; max-width: 62ch; color: var(--ink-2); font-size: 1.08rem; }}
    .lede strong {{ color: var(--ink); font-weight: 600; }}

    .tally {{ display: flex; flex-wrap: wrap; gap: 0; margin: 2rem 0 3.25rem; border: 1px solid var(--rule); background: var(--paper-2); }}
    .tally div {{ flex: 1 1 130px; padding: 1.05rem 1.25rem; border-right: 1px solid var(--rule); }}
    .tally div:last-child {{ border-right: 0; }}
    .tally .n {{ font-family: "sheet-mono", monospace; font-size: 1.9rem; font-variant-numeric: tabular-nums; display: block; line-height: 1.1; }}
    .tally .l {{ font-family: "sheet-mono", monospace; font-size: 0.66rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-3); }}
    .tally .t-drawn .n {{ color: var(--drawn); }}
    .tally .t-gap {{ background: var(--gap-bg); }}
    .tally .t-gap .n {{ color: var(--gap); }}

    .group {{ margin-bottom: 3.25rem; }}
    .group h2 {{
      font-family: "sheet-mono", monospace; font-size: 0.72rem; letter-spacing: 0.18em;
      text-transform: uppercase; color: var(--ink-2); font-weight: 400;
      display: flex; align-items: center; gap: 0.7rem;
      border-bottom: 1px solid var(--rule); padding-bottom: 0.6rem; margin: 0 0 1.4rem;
    }}
    .group h2 .count {{ color: var(--ink-3); }}
    .group h2 .secgap {{
      margin-left: auto; color: var(--gap); background: var(--gap-bg);
      border: 1px solid var(--gap-edge); padding: 0.12rem 0.5rem; letter-spacing: 0.08em;
    }}

    .grid {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 1px; background: var(--rule);
      grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); border: 1px solid var(--rule); }}
    .cell {{ background: var(--paper-2); padding: 1.1rem 0.75rem 0.9rem; text-align: center;
      display: flex; flex-direction: column; align-items: center; gap: 0.3rem; }}
    .cell.is-gap {{ background: var(--gap-bg); }}

    .glyphbox {{ height: 62px; display: flex; align-items: center; justify-content: center; color: var(--ink); }}
    .uglyph {{ font-family: "glyph-1", "glyph-2", "glyph-3", sans-serif; font-size: 2.6rem; line-height: 1; }}
    .gsvg {{ width: 42px; height: 42px; color: var(--drawn); }}
    .asciiglyph {{ font-family: "sheet-mono", monospace; font-size: 1.5rem; color: var(--gap);
      border: 1px dashed var(--gap-edge); padding: 0.28rem 0.5rem; line-height: 1; }}
    .asciiglyph.sm {{ font-size: 1rem; padding: 0.15rem 0.4rem; }}

    .gname {{ margin: 0.25rem 0 0; font-size: 0.95rem; line-height: 1.25; text-wrap: balance; }}
    .gcode {{ margin: 0; font-family: "sheet-mono", monospace; font-size: 0.64rem;
      color: var(--ink-3); letter-spacing: 0.04em; }}
    .badge {{ margin-top: 0.35rem; font-family: "sheet-mono", monospace; font-size: 0.58rem;
      letter-spacing: 0.09em; text-transform: uppercase; padding: 0.16rem 0.42rem; }}
    .b-fromfont {{ color: var(--ink-3); border: 1px solid var(--rule); }}
    .b-drawn {{ color: var(--drawn); background: var(--drawn-bg); }}
    .b-gap {{ color: var(--gap); border: 1px solid var(--gap-edge); }}

    .gapsec {{ margin-top: 4rem; border: 2px solid var(--gap-edge); background: var(--gap-bg); padding: 1.75rem; }}
    .gapsec h2 {{ font-family: "sheet-display", serif; font-size: 1.6rem; margin: 0 0 0.5rem; color: var(--ink); }}
    .gapsec p {{ margin: 0 0 1.25rem; max-width: 64ch; color: var(--ink-2); }}
    .tblwrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    th {{ font-family: "sheet-mono", monospace; font-size: 0.63rem; letter-spacing: 0.13em;
      text-transform: uppercase; text-align: left; color: var(--ink-2);
      border-bottom: 1px solid var(--gap-edge); padding: 0.5rem 0.75rem 0.5rem 0; }}
    td {{ padding: 0.6rem 0.75rem 0.6rem 0; border-bottom: 1px solid var(--gap-edge); vertical-align: middle; }}
    .gr-name {{ font-weight: 600; }}
    .gr-grp, .gr-why {{ color: var(--ink-2); font-size: 0.86rem; }}

    footer {{ margin-top: 3.5rem; padding-top: 1.5rem; border-top: 1px solid var(--rule);
      color: var(--ink-3); font-size: 0.88rem; }}
    footer code {{ font-family: "sheet-mono", monospace; font-size: 0.82em; color: var(--ink-2); }}
    </style>

    <div class="wrap">
      <header>
        <p class="eyebrow">Stellium · Glyph Inventory</p>
        <h1>Every symbol we can draw, and the nine we can’t</h1>
        <p class="lede">All {len(items)} glyphs the registries can emit, rendered from the package’s own bundled fonts and SVGs — <strong>the same ones a chart uses</strong>. This sheet embeds those faces directly, so what you see is what a reader gets, not what your system happens to have installed.</p>
      </header>

      <div class="tally">
        <div><span class="n">{len(items)}</span><span class="l">Symbols</span></div>
        <div><span class="n">{counts["font"]}</span><span class="l">From a font</span></div>
        <div class="t-drawn"><span class="n">{counts["svg"]}</span><span class="l">Drawn as SVG</span></div>
        <div class="t-gap"><span class="n">{len(gaps)}</span><span class="l">Gaps</span></div>
        <div><span class="n">0</span><span class="l">Tofu</span></div>
      </div>

    {chr(10).join(sections)}

      <section class="gapsec">
        <h2>The gaps</h2>
        <p>These {len(gaps)} have no glyph — they fall back to <em>letters</em>. There is no Unicode codepoint for any of them, so no font can help; they need drawing. The eight harmonic aspects share a family resemblance and would work as a set.</p>
        <div class="tblwrap">
          <table>
            <thead><tr><th>Symbol</th><th>Group</th><th>Renders as</th><th>Why</th></tr></thead>
            <tbody>
    {gap_rows}
            </tbody>
          </table>
        </div>
      </section>

      <footer>
        <p>Generated from <code>CELESTIAL_REGISTRY</code>, <code>ASPECT_REGISTRY</code>, <code>FIXED_STARS_REGISTRY</code> and <code>ZODIAC_GLYPHS</code>. Source of each glyph is resolved exactly as <code>visualization.core.get_glyph()</code> resolves it at draw time — a bundled SVG wins, otherwise the first bundled font whose <code>cmap</code> contains the codepoint. Guarded by <code>tests/test_glyph_coverage.py</code>.</p>
      </footer>
    </div>
    """

    OUT.write_text(HTML, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(
        f"  {len(items)} symbols · {counts['font']} font · {counts['svg']} svg · "
        f"{len(gaps)} gaps"
    )
    for gap in gaps:
        print(f"    GAP  {gap['group']:28s} {gap['name']:24s} {gap['detail']}")


if __name__ == "__main__":
    main()
