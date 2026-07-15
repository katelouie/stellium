"""Themed PDF rendering for **reports**, via the bundled Typst design system.

This module's job is the *report-specific* half: turning a chart plus its section
data into the JSON contract that ``typst_theme/report.typ`` consumes. The generic
half — where the design system lives, where the fonts live, how a document is
compiled — is in :mod:`stellium.presentation.typst_runtime`, which the planner and
the atlas share.

A *theme* is chosen by name and passed through ``sys.inputs``: layout, glyphs and
components are shared, and the theme is pure data (see ``typst_theme/palettes.typ``).
"""

from __future__ import annotations

import os
from typing import Any

from stellium.i18n import format_date, format_time, msg, render, term
from stellium.presentation.typst_runtime import (
    THEME_LABELS,
    THEME_WHEEL,
    THEMES,
    TypstDocument,
    validate_theme,
)
from stellium.utils.chart_ruler import get_chart_ruler_from_chart

__all__ = [
    "MOON_STYLES",
    "THEMES",
    "THEME_LABELS",
    "THEME_WHEEL",
    "build_report_data",
    "render_pdf",
]

# Per-theme moon-phase illustration colours (lit = illuminated limb, shadow =
# dark limb). Light themes: light lit on a dark shadow; dark themes: light lit on
# a near-black shadow, with a theme accent border.
MOON_STYLES = {
    "house": {
        "lit_color": "#F2ECE0",
        "shadow_color": "#3A2233",
        "border_color": "#A08A72",
    },
    "sepia": {
        "lit_color": "#F6EEDD",
        "shadow_color": "#3A2A1A",
        "border_color": "#9A7A52",
    },
    "celestial": {
        "lit_color": "#E9DEFA",
        "shadow_color": "#100B1A",
        "border_color": "#E8B44A",
    },
    "blues": {
        "lit_color": "#DCEFFF",
        "shadow_color": "#06182A",
        "border_color": "#7FB2D8",
    },
    "greyscale": {
        "lit_color": "#FFFFFF",
        "shadow_color": "#1B1B1B",
        "border_color": "#1B1B1B",
    },
}


# ---------------------------------------------------------------------------
# meta (title page) derivation
# ---------------------------------------------------------------------------
def _card(
    chart: Any, obj_name: str, label: str, locale: str, *, rising: bool = False
) -> dict | None:
    """Build a Sun/Moon/Ascendant title-page card from the chart, in ``locale``."""
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
        sign = render(term(f"sign.{pos.sign}"), locale)
        if rising:
            sub = f"{sign} · {render(msg('Rising'), locale)}"
        else:
            house = None
            try:
                placements = chart.house_placements[chart.default_house_system]
                house = placements.get(pos.name)
            except (KeyError, AttributeError):
                pass
            if house:
                # Supply both an English ordinal and the raw number, so a locale can pick
                # ({ordinal} → "5th house"; a locale may use {n} → "第5宮").
                house_str = render(
                    msg("{ordinal} house", ordinal=_ordinal(house), n=house), locale
                )
                sub = f"{sign} · {house_str}"
            else:
                sub = sign
        return {
            "label": render(term(f"body.{label}"), locale),
            "value": value,
            "sub": sub,
        }
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


def _metadata_line(chart: Any, locale: str) -> list[str]:
    """The gold tracked-caps chips under the title (ruler / sect / phase / …).

    Derived from the chart and localized, not scraped from the rendered overview — the
    overview's keys are themselves localized, so an English-keyed lookup finds nothing.
    """
    items: list[str] = []

    # Chart ruler → "{ruler}-ruled".
    try:
        ruler, _asc = get_chart_ruler_from_chart(chart)
    except Exception:
        ruler = None
    if ruler:
        items.append(render(msg("{ruler}-ruled", ruler=term(f"body.{ruler}")), locale))

    # Sect → "Day Chart" / "Night Chart".
    dignities = chart.metadata.get("dignities") if hasattr(chart, "metadata") else None
    sect = dignities.get("sect") if isinstance(dignities, dict) else None
    if sect and sect != "unknown":
        items.append(
            render(msg("{sect} Chart", sect=term(f"sect.{sect.title()}")), locale)
        )

    # Moon phase → "Waning Gibbous 74%".
    try:
        moon = chart.get_object("Moon")
        ph = getattr(moon, "phase", None)
        if ph is not None:
            frac = getattr(ph, "illuminated_fraction", None)
            phase = getattr(ph, "phase_name", None)
            if phase and frac is not None:
                items.append(
                    f"{render(term(f'phase.{phase}'), locale)} {frac * 100:.0f}%"
                )
    except Exception:
        pass

    # House system (the first) and zodiac.
    systems = getattr(chart, "house_systems", None)
    if systems:
        first = next(iter(systems))
        items.append(render(term(f"house_system.{first}"), locale))
    zodiac_type = getattr(chart, "zodiac_type", None)
    if zodiac_type:
        items.append(render(msg(zodiac_type.value.title()), locale))

    return items


def _build_meta(
    chart: Any,
    title: str | None,
    theme: str,
    locale: str,
) -> dict[str, Any]:
    default_title = title or render(msg("Natal Chart"), locale)
    name = (
        (chart.metadata.get("name") if chart and hasattr(chart, "metadata") else None)
        or title
        or default_title
    )

    # subtitle: Location · Date · Time · Timezone. The place and IANA zone are data; the
    # date and time are laid out per the locale (a reorder, not a word swap).
    bits: list[str] = []
    location = getattr(chart, "location", None)
    if location is not None and getattr(location, "name", None):
        bits.append(location.name)
    try:
        local_dt = chart.datetime.local_datetime
        bits.append(format_date(local_dt.date(), locale))
        bits.append(format_time(local_dt.time(), locale))
    except Exception:  # pragma: no cover - defensive; unknown-time charts etc.
        pass
    if location is not None and getattr(location, "timezone", None):
        bits.append(str(location.timezone))
    subtitle = " · ".join(b for b in bits if b)

    cards = [
        _card(chart, "Sun", "Sun", locale),
        _card(chart, "Moon", "Moon", locale),
        _card(chart, None, "Ascendant", locale, rising=True),
    ]
    return {
        "running_left": default_title,
        "running_right": name,
        "footer": THEME_LABELS.get(theme, theme.title()),
        "kicker": default_title,
        "name": name,
        "subtitle": subtitle,
        "cards": [c for c in cards if c],
        "metadata": _metadata_line(chart, locale),
    }


# ---------------------------------------------------------------------------
# snapshot (distribution & balance) derivation
# ---------------------------------------------------------------------------
def _snapshot_section(chart: Any, locale: str) -> dict | None:
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

    def count_of(n: int) -> str:
        return render(msg("{count} of {total}", count=n, total=total), locale)

    yang_word = render(term("polarity.Yang"), locale)
    yin_word = render(term("polarity.Yin"), locale)

    return {
        "kind": "snapshot",
        "title": render(msg("Snapshot"), locale),
        "descriptor": render(msg("distribution & balance"), locale),
        "cards": [
            {
                "label": render(msg("Dominant Element"), locale),
                "value": render(term(f"element.{dom_el[0]}"), locale),
                "sub": count_of(el[dom_el[1]]),
            },
            {
                "label": render(msg("Dominant Modality"), locale),
                "value": render(term(f"modality.{dom_mo[0]}"), locale),
                "sub": count_of(mo[dom_mo[1]]),
            },
            {
                "label": render(msg("Polarity"), locale),
                "value": render(term(f"polarity.{polarity}"), locale),
                "sub": f"{yang_word} {yang} · {yin_word} {yin}",
            },
        ],
        "elements": [
            {"label": render(term(f"element.{lbl}"), locale), "count": el[key]}
            for lbl, key in el_order
        ],
        "modalities": [
            {"label": render(term(f"modality.{lbl}"), locale), "count": mo[key]}
            for lbl, key in mo_order
        ],
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
    # Structured dispositor graph (drawn natively; SVG kept for other renderers).
    dg = d.get("graph")
    if dg and dg.get("graphs"):
        return {"kind": "dispositor_graph", "title": name, "graphs": dg["graphs"]}
    # Structured aspectarian (carried on the "svg" aspectarian subsection).
    ac = d.get("aspectarian")
    if ac and ac.get("bodies"):
        return {
            "kind": "aspectarian",
            "title": name,
            "bodies": ac["bodies"],
            "cells": ac.get("cells", []),
        }
    # Structured aspect list (the "Aspect List" subsection carries aspect_pairs).
    if d.get("aspect_pairs") is not None:
        return {"kind": "aspect_list", "title": name, "aspects": d["aspect_pairs"]}
    typ = d.get("type")
    if typ == "table":
        headers = [str(h) for h in d.get("headers", [])]
        rows = [[str(c) for c in r] for r in d.get("rows", [])]
        # Narrow + long tables (e.g. house cusps) waste the page's width run as a
        # single column. Split them into two halves side by side so they fill it.
        if len(headers) <= 3 and len(rows) >= 12:
            mid = (len(rows) + 1) // 2
            return {
                "kind": "side_by_side",
                "title": name,
                "tables": [
                    {"title": "", "headers": headers, "rows": rows[:mid]},
                    {"title": "", "headers": headers, "rows": rows[mid:]},
                ],
            }
        return {"kind": "table", "title": name, "headers": headers, "rows": rows}
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
    if typ == "svg":
        content = d.get("content", "")
        if content:
            # svg_content is materialised to a file in render_pdf (Typst embeds
            # an image path, not an inline SVG string).
            return {"kind": "svg", "title": name, "svg_content": content}
        return None
    # unknown: skip
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
    if lname.startswith("dispositor") and d.get("type") == "compound":
        return _dispositor_section(name, d)
    return _generic(name, d)


def _dispositor_section(name: str, d: dict[str, Any]) -> dict:
    """Graph on top, then the planetary + house text blocks side by side."""
    out_subs: list[dict] = []
    text_cols: list[dict] = []
    for sub_name, sub_d in d.get("sections", []):
        if sub_d.get("graph"):
            mapped = _generic(sub_name, sub_d)
            if mapped:
                out_subs.append(mapped)
        elif sub_d.get("type") == "text":
            text_cols.append({"title": sub_name, "text": str(sub_d.get("text", ""))})
        else:
            mapped = _generic(sub_name, sub_d)
            if mapped:
                out_subs.append(mapped)
    if text_cols:
        out_subs.append({"kind": "text_columns", "columns": text_cols})
    return {"kind": "compound", "title": name, "sections": out_subs}


def build_report_data(
    chart: Any,
    section_data: list[tuple[str, dict[str, Any]]],
    title: str | None,
    theme: str,
    locale: str = "en",
) -> dict[str, Any]:
    """Serialise a report to the typst_theme JSON contract."""
    meta = _build_meta(chart, title, theme, locale)
    sections: list[dict] = []
    snap = _snapshot_section(chart, locale)
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
    locale: str = "en",
) -> bytes:
    """Render a report to PDF bytes using the bundled Typst design system.

    The temp-dir/copy-templates/materialise-SVGs/compile dance lives in
    :class:`~stellium.presentation.typst_runtime.TypstDocument`, which the planner
    shares. What is left here is the part that is genuinely about *reports*.
    """
    validate_theme(theme)
    data = build_report_data(chart, section_data, title, theme, locale)

    with TypstDocument("report.typ", theme, prefix="stellium_pdf_") as doc:
        if chart_svg_path and os.path.exists(chart_svg_path):
            data["meta"]["chart_svg"] = doc.add_file("chart.svg", src=chart_svg_path)

        _draw_moon_phase(doc, chart, data, theme)

        return doc.render(data, svg_sections=data.get("sections", []))


def _draw_moon_phase(doc: TypstDocument, chart: Any, data: dict, theme: str) -> None:
    """Draw the standalone moon-phase illustration, if the report has such a section."""
    section = next(
        (s for s in data.get("sections", []) if s.get("kind") == "moon_phase"), None
    )
    if section is None:
        return

    try:
        from stellium.visualization import moon_phase_svg

        moon_phase_svg(
            chart,
            os.path.join(doc.root, "moon.svg"),
            size=200,
            style=MOON_STYLES.get(theme),
        )
        section["moon_svg"] = "moon.svg"
    except Exception:  # never let a drawing failure break the PDF
        pass
