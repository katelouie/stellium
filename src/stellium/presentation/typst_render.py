"""Themed PDF rendering via the bundled Typst design system.

This module serialises a report (chart + section data) to the JSON contract that
``typst_theme/`` consumes, then compiles the bundled Typst template to PDF. A
*theme* is chosen by name and passed through ``sys.inputs`` — layout, glyphs and
components are shared; the theme is pure data (see ``typst_theme/palettes.typ``).

The old string-building renderer emitted Typst markup inline; this one keeps all
visual concerns inside the ``.typ`` design system and hands it structured data.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from typing import Any

try:  # typst-py is an optional/heavy dependency
    import typst as _typst
except ImportError:  # pragma: no cover - exercised only when typst missing
    _typst = None

THEMES = ("house", "sepia", "celestial", "blues", "greyscale")
THEME_LABELS = {
    "house": "House Style",
    "sepia": "Sepia",
    "celestial": "Celestial",
    "blues": "Blues",
    "greyscale": "Greyscale",
}
_TEMPLATE_FILES = (
    "palettes.typ",
    "glyphs.typ",
    "components.typ",
    "engine.typ",
    "report.typ",
)


def _theme_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "typst_theme")


# ---------------------------------------------------------------------------
# meta (title page) derivation
# ---------------------------------------------------------------------------
def _overview_pairs(section_data: list[tuple[str, dict[str, Any]]]) -> dict[str, str]:
    """Pull the Chart Overview key/value dict, if the report includes one."""
    for name, d in section_data:
        if d.get("type") == "key_value" and name.lower().startswith("chart overview"):
            return {str(k): str(v) for k, v in d.get("data", {}).items()}
    return {}


def _card(
    chart: Any, obj_name: str, label: str, *, rising: bool = False
) -> dict | None:
    """Build a Sun/Moon/Ascendant title-page card from the chart."""
    try:
        if rising:
            pos = next(
                (a for a in chart.get_angles() if a.name in ("ASC", "Ascendant")),
                None,
            )
        else:
            pos = chart.get_object(obj_name)
        if pos is None:
            return None
        deg = int(pos.sign_degree)
        minute = int((pos.sign_degree % 1) * 60)
        value = f"{deg}°{minute:02d}'"
        if rising:
            sub = f"{pos.sign} · Rising"
        else:
            house = None
            try:
                placements = chart.house_placements[chart.default_house_system]
                house = placements.get(pos.name)
            except (KeyError, AttributeError):
                pass
            sub = f"{pos.sign}" + (f" · {_ordinal(house)} house" if house else "")
        return {"label": label, "value": value, "sub": sub}
    except Exception:  # pragma: no cover - defensive; never break the PDF
        return None


def _ordinal(n: Any) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _metadata_line(chart: Any, overview: dict[str, str]) -> list[str]:
    """The gold tracked-caps chips under the title (ruler / sect / phase / …)."""
    items: list[str] = []
    ruler = overview.get("Chart Ruler", "")
    if ruler:
        items.append(f"{ruler.split(' (')[0]}-ruled")
    sect = overview.get("Chart Sect", "")
    if sect:
        items.append(sect)
    try:
        moon = chart.get_object("Moon")
        img = getattr(moon, "image_data", None)
        if img is not None:
            frac = getattr(img, "illuminated_fraction", None)
            phase = getattr(img, "phase_name", None)
            if phase and frac is not None:
                items.append(f"{phase} {frac * 100:.0f}%")
    except Exception:
        pass
    hs = overview.get("House System", "")
    if hs:
        items.append(hs.split(",")[0].strip())
    zod = overview.get("Zodiac", "")
    if zod:
        items.append(zod)
    return items


def _build_meta(
    chart: Any,
    section_data: list[tuple[str, dict[str, Any]]],
    title: str | None,
    theme: str,
) -> dict[str, Any]:
    overview = _overview_pairs(section_data)
    name = (
        overview.get("Name")
        or (chart.metadata.get("name") if chart else None)
        or (title or "Natal Chart")
    )
    # subtitle: Location · Date · Time · Timezone
    bits = [
        overview.get("Location"),
        overview.get("Date"),
        overview.get("Time"),
        overview.get("Timezone"),
    ]
    subtitle = " · ".join(b for b in bits if b)
    cards = [
        _card(chart, "Sun", "Sun"),
        _card(chart, "Moon", "Moon"),
        _card(chart, None, "Ascendant", rising=True),
    ]
    return {
        "running_left": title or "Natal Chart",
        "running_right": name,
        "footer": THEME_LABELS.get(theme, theme.title()),
        "kicker": title or "Natal Chart",
        "name": name,
        "subtitle": subtitle,
        "cards": [c for c in cards if c],
        "metadata": _metadata_line(chart, overview),
    }


# ---------------------------------------------------------------------------
# snapshot (distribution & balance) derivation
# ---------------------------------------------------------------------------
def _snapshot_section(chart: Any) -> dict | None:
    try:
        from stellium.analysis.frames import _count_elements, _count_modalities
    except Exception:  # pragma: no cover
        return None
    try:
        el = _count_elements(chart)
        mo = _count_modalities(chart)
    except Exception:
        return None
    if sum(el.values()) == 0:
        return None

    el_order = [
        ("Fire", "fire"),
        ("Earth", "earth"),
        ("Air", "air"),
        ("Water", "water"),
    ]
    mo_order = [("Cardinal", "cardinal"), ("Fixed", "fixed"), ("Mutable", "mutable")]
    total = sum(el.values())
    dom_el = max(el_order, key=lambda p: el[p[1]])
    dom_mo = max(mo_order, key=lambda p: mo[p[1]])
    yang = el["fire"] + el["air"]
    yin = el["earth"] + el["water"]
    polarity = "Balanced" if yang == yin else ("Yang" if yang > yin else "Yin")

    return {
        "kind": "snapshot",
        "title": "Snapshot",
        "descriptor": "distribution & balance",
        "cards": [
            {
                "label": "Dominant Element",
                "value": dom_el[0],
                "sub": f"{el[dom_el[1]]} of {total}",
            },
            {
                "label": "Dominant Modality",
                "value": dom_mo[0],
                "sub": f"{mo[dom_mo[1]]} of {total}",
            },
            {"label": "Polarity", "value": polarity, "sub": f"Yang {yang} · Yin {yin}"},
        ],
        "elements": [{"label": lbl, "count": el[key]} for lbl, key in el_order],
        "modalities": [{"label": lbl, "count": mo[key]} for lbl, key in mo_order],
        "polarity": {"yang": yang, "yin": yin},
    }


# ---------------------------------------------------------------------------
# hero + generic section mapping
# ---------------------------------------------------------------------------
def _planet_positions(name: str, d: dict[str, Any]) -> dict | None:
    """Read the section's structured planet payload (single source of truth).

    Returns None if the section didn't emit structure (e.g. comparison /
    multichart variants), so the caller falls back to a themed generic table.
    """
    planets = d.get("planets")
    if not planets:
        return None
    return {
        "kind": "planet_positions",
        "title": name,
        "house_headers": [str(h) for h in d.get("house_headers", [])],
        "show_speed": bool(d.get("show_speed", True)),
        "planets": planets,
    }


def _moon_phase(name: str, d: dict[str, Any]) -> dict | None:
    """Build the rich moon-phase block from the section's key/value data."""
    data = d.get("data", {})
    if not data:
        return None

    def get(*keys):
        for k in keys:
            if k in data:
                return str(data[k])
        return None

    phase = (get("Phase Name", "Phase") or "Moon").split(" (")[0]
    fields: list[list] = []
    illum = get("Illumination")
    direction = get("Direction")
    if illum:
        fields.append(["Illumination", illum, True])
    if direction:
        fields.append(["Direction", direction, True])
    for label, keys in (
        ("Phase Angle", ("Phase Angle",)),
        ("Sun–Moon Sep.", ("Sun-Moon Separation", "Sun–Moon Separation")),
        ("App. Magnitude", ("Apparent Magnitude",)),
        ("App. Diameter", ("Apparent Diameter",)),
        ("Geocentric Parallax", ("Geocentric Parallax",)),
    ):
        val = get(*keys)
        if val:
            fields.append([label, val])
    if not fields:
        return None
    return {"kind": "moon_phase", "title": name, "phase": phase, "fields": fields}


def _generic(name: str, d: dict[str, Any]) -> dict | None:
    """Map a generic section dict to a themed engine section."""
    typ = d.get("type")
    if typ == "table":
        return {
            "kind": "table",
            "title": name,
            "headers": [str(h) for h in d.get("headers", [])],
            "rows": [[str(c) for c in r] for r in d.get("rows", [])],
        }
    if typ == "key_value":
        return {
            "kind": "key_value",
            "title": name,
            "pairs": [[str(k), str(v)] for k, v in d.get("data", {}).items()],
        }
    if typ == "text":
        return {
            "kind": "text",
            "title": name,
            "text": str(d.get("text", d.get("content", ""))),
        }
    if typ == "side_by_side_tables":
        return {
            "kind": "side_by_side",
            "title": name,
            "tables": [
                {
                    "title": str(t.get("title", "")),
                    "headers": [str(h) for h in t.get("headers", [])],
                    "rows": [[str(c) for c in r] for r in t.get("rows", [])],
                }
                for t in d.get("tables", [])
            ],
        }
    if typ == "compound":
        subs = []
        for sub_name, sub_d in d.get("sections", []):
            mapped = _generic(sub_name, sub_d)
            if mapped:
                subs.append(mapped)
        return {"kind": "compound", "title": name, "sections": subs}
    # svg / unknown: skip (inline SVG sections not embedded in this pass)
    return None


def _map_section(name: str, d: dict[str, Any], chart: Any) -> dict | None:
    lname = name.lower()
    if lname.startswith("chart overview") and d.get("type") == "key_value":
        return {
            "kind": "chart_overview",
            "title": name,
            "pairs": [[str(k), str(v)] for k, v in d.get("data", {}).items()],
        }
    if d.get("planets") is not None:
        rich = _planet_positions(name, d)
        if rich:
            return rich
    if lname.startswith("moon phase"):
        rich = _moon_phase(name, d)
        if rich:
            return rich
    return _generic(name, d)


def build_report_data(
    chart: Any,
    section_data: list[tuple[str, dict[str, Any]]],
    title: str | None,
    theme: str,
) -> dict[str, Any]:
    """Serialise a report to the typst_theme JSON contract."""
    meta = _build_meta(chart, section_data, title, theme)
    sections: list[dict] = []
    snap = _snapshot_section(chart)
    if snap:
        sections.append(snap)
    for name, d in section_data:
        mapped = _map_section(name, d, chart)
        if mapped:
            sections.append(mapped)
    return {"meta": meta, "sections": sections}


# ---------------------------------------------------------------------------
# compile driver
# ---------------------------------------------------------------------------
def render_pdf(
    chart: Any,
    section_data: list[tuple[str, dict[str, Any]]],
    chart_svg_path: str | None = None,
    title: str | None = None,
    theme: str = "house",
) -> bytes:
    """Render a report to PDF bytes using the bundled Typst design system."""
    if _typst is None:
        raise RuntimeError(
            "Typst library not available. Install with: pip install typst"
        )
    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}. Choose from: {', '.join(THEMES)}")

    data = build_report_data(chart, section_data, title, theme)

    with tempfile.TemporaryDirectory(prefix="stellium_pdf_") as tmp:
        for fn in _TEMPLATE_FILES:
            shutil.copy2(os.path.join(_theme_dir(), fn), os.path.join(tmp, fn))
        if chart_svg_path and os.path.exists(chart_svg_path):
            shutil.copy2(chart_svg_path, os.path.join(tmp, "chart.svg"))
            data["meta"]["chart_svg"] = "chart.svg"
        with open(os.path.join(tmp, "data.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        pdf_bytes = _typst.compile(
            os.path.join(tmp, "report.typ"),
            root=tmp,
            sys_inputs={"theme": theme, "data": "data.json"},
        )
    return pdf_bytes
