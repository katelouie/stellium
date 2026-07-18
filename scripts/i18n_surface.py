"""Enumerate the user-visible string surface, so Phase 2 of the i18n spec can be scoped.

Grepping for capitalised literals gives an upper bound full of dict keys, enum names and
internal identifiers. This instead renders the real thing and captures what actually
reaches the output:

- **Reports** — every registered section is run against a fully-populated chart and its
  section data is walked. Strings are tagged by the role they appear in (section name,
  table header, key-value key, cell, table title), because the role decides what a
  string *becomes* under the format-last design: a header is usually a message template,
  a cell is usually a catalog term.
- **Charts** — an SVG is rendered and its ``<text>`` nodes are read. Most are glyphs;
  the point is to find the few that are words.

Each captured string is then classified. ``composed`` is the interesting bucket: those
are the ones a substring translator can never fix, and the ones that must become
messages with named slots.

Writes ``i18n_surface.json``. Run it from anywhere:

    python scripts/i18n_surface.py [-o path/to/i18n_surface.json]

See docs/development/specs/I18N.md, Phase 0.
"""

from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from stellium import ChartBuilder
from stellium.presentation import sections as sections_pkg

# A string with no letter in it is a glyph, a number, or punctuation — never translatable.
_HAS_LETTER = re.compile(r"[^\W\d_]", re.UNICODE)
# Latin letters specifically: what an English UI string is made of.
_HAS_LATIN = re.compile(r"[A-Za-z]")
# A slot that a format-last message would need: anything that is not a plain word.
_LOOKS_COMPOSED = re.compile(r"[\d(){}\[\]:/,]|°|'|\"")


def _is_glyph_only(s: str) -> bool:
    """True if the string carries no letters — an astrological glyph, a number, a rule."""
    return not _HAS_LETTER.search(s)


def _classify(s: str) -> str:
    """Bucket a captured string by what the format-last design would have to do with it.

    The buckets are ordered by how much work they imply, cheapest first.
    """
    stripped = s.strip()
    if not stripped:
        return "empty"
    if _is_glyph_only(stripped):
        return "glyph_or_number"
    if not _HAS_LATIN.search(stripped):
        # Letters, but none of them Latin: already translated (or a non-Latin proper noun).
        return "already_localized"
    if _LOOKS_COMPOSED.search(stripped):
        # Digits, brackets, degrees, colons: built by an f-string from parts.
        return "composed"
    return "word"


def _walk(data: Any, role: str, out: list[dict[str, str]]) -> None:
    """Collect every string in a section-data structure, tagged with the role it plays."""
    if isinstance(data, str):
        out.append({"text": data, "role": role})
        return
    if isinstance(data, dict):
        dtype = data.get("type")
        if dtype == "table":
            for h in data.get("headers", []):
                _walk(h, "header", out)
            for row in data.get("rows", []):
                for cell in row:
                    _walk(cell, "cell", out)
        elif dtype == "key_value":
            for k, v in data.get("data", {}).items():
                _walk(k, "kv_key", out)
                _walk(v, "cell", out)
        elif dtype == "text":
            _walk(data.get("text", ""), "prose", out)
        elif dtype in ("compound",):
            for name, sub in data.get("sections", []):
                _walk(name, "section_name", out)
                _walk(sub, role, out)
        elif dtype in ("side_by_side_tables", "grouped_tables"):
            for tbl in data.get("tables", []):
                _walk(tbl.get("title", ""), "table_title", out)
                for h in tbl.get("headers", []):
                    _walk(h, "header", out)
                for row in tbl.get("rows", []):
                    for cell in row:
                        _walk(cell, "cell", out)
        # svg / unknown: no translatable text
        return
    if isinstance(data, (list, tuple)):
        for item in data:
            _walk(item, role, out)


def _sample_chart():
    """A chart with every optional component on, so no section has to bail out."""
    from stellium.components import (
        ArabicPartsCalculator,
        DignityComponent,
        FixedStarsComponent,
        MidpointCalculator,
    )
    from stellium.engines import PlacidusHouses, WholeSignHouses

    return (
        ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .add_component(ArabicPartsCalculator())
        .add_component(MidpointCalculator())
        .add_component(DignityComponent())
        .add_component(FixedStarsComponent())
        .calculate()
    )


def survey_reports(chart) -> tuple[list[dict[str, str]], list[str]]:
    """Run every section that will instantiate with defaults; capture what it emits."""
    found: list[dict[str, str]] = []
    skipped: list[str] = []

    names = [n for n in dir(sections_pkg) if n.endswith("Section")]
    for name in sorted(names):
        cls = getattr(sections_pkg, name)
        if not inspect.isclass(cls):
            continue
        try:
            section = cls()
        except Exception as e:  # needs constructor args this survey can't guess
            skipped.append(f"{name}: cannot construct with defaults ({e})")
            continue
        try:
            data = section.generate_data(chart)
        except Exception as e:  # a section may need data this chart lacks
            skipped.append(f"{name}: {type(e).__name__}: {e}")
            continue

        found.append({"text": section.section_name, "role": "section_name"})
        entries: list[dict[str, str]] = []
        _walk(data, "cell", entries)
        for e in entries:
            e["section"] = name
        found.extend(entries)

    return found, skipped


def survey_chart_svg(chart) -> list[dict[str, str]]:
    """Read the <text> nodes out of a rendered wheel."""
    import tempfile
    import xml.etree.ElementTree as ET

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "chart.svg"
        chart.draw(str(path)).save()
        tree = ET.parse(path)

    out: list[dict[str, str]] = []
    for node in tree.iter():
        if not node.tag.endswith("}text") and node.tag != "text":
            continue
        text = "".join(node.itertext()).strip()
        if text:
            out.append({"text": text, "role": "svg_text", "section": "chart_svg"})
    return out


def _describe(s: str) -> str:
    """Name the scripts present, so a non-Latin string is self-explaining in the report."""
    scripts = {
        unicodedata.name(ch, "?").split()[0] for ch in s if _HAS_LETTER.match(ch)
    }
    return "+".join(sorted(scripts)) or "-"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "i18n_surface.json",
    )
    args = parser.parse_args()

    chart = _sample_chart()
    report_strings, skipped = survey_reports(chart)
    svg_strings = survey_chart_svg(chart)
    every = report_strings + svg_strings

    for entry in every:
        entry["kind"] = _classify(entry["text"])

    # Distinct (text, role) pairs: the same word as a header and as a cell are two
    # different jobs under format-last.
    distinct: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in every:
        key = (entry["text"], entry["role"])
        if key not in distinct:
            distinct[key] = {**entry, "count": 0, "scripts": _describe(entry["text"])}
        distinct[key]["count"] += 1

    by_kind = Counter(e["kind"] for e in distinct.values())
    by_role = Counter(e["role"] for e in distinct.values())

    # The number the spec actually needs: distinct strings that need a human decision.
    needs_work = sorted(
        (e for e in distinct.values() if e["kind"] in ("word", "composed")),
        key=lambda e: (e["kind"], e["role"], e["text"]),
    )

    payload = {
        "totals": {
            "captured": len(every),
            "distinct": len(distinct),
            "translatable": len(needs_work),
        },
        "by_kind": dict(by_kind.most_common()),
        "by_role": dict(by_role.most_common()),
        "skipped_sections": skipped,
        "strings": needs_work,
        "all": sorted(distinct.values(), key=lambda e: (e["role"], e["text"])),
    }
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"captured {len(every)} strings, {len(distinct)} distinct\n")
    print("by kind:")
    for kind, n in by_kind.most_common():
        print(f"  {kind:20} {n:5}")
    print("\nby role:")
    for role, n in by_role.most_common():
        print(f"  {role:20} {n:5}")
    composed = [e for e in needs_work if e["kind"] == "composed"]
    print(f"\n>>> {len(needs_work)} distinct strings need translating")
    print(f">>> of which {len(composed)} are COMPOSED (unfixable by a substring swap)")
    if skipped:
        print(f"\n{len(skipped)} sections skipped:")
        for s in skipped:
            print(f"  - {s}")
    print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
