"""Report sections for sect rectification (the compare-hypothesis workbench)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from stellium.core.models import CalculatedChart
from stellium.rectification.analysis import SectAnalysis, analyze_sect
from stellium.rectification.matrix import ConvergenceMatrix, convergence_matrix

_SECT_LIGHT_ABBR = {"day": "Sun", "night": "Moon"}
_MALEFIC_ABBR = {"day": "Mars", "night": "Saturn"}

_MALEFIC_FLAVOR = {
    "day": "hot, sharp, sudden — accidents, violence, fever, conflict",
    "night": "cold, slow, chronic — illness, poverty, confinement, decline",
}
_BENEFIC_FLAVOR = {
    "day": "Jupiter-toned — honour, wealth, law, faith, expansion",
    "night": "Venus-toned — love, art, beauty, pleasure, music",
}


def _cond(pc) -> str:
    return f"{pc.planet} in {pc.sign} ({pc.dignity})"


def _hypothesis_table(a: SectAnalysis) -> dict[str, Any]:
    """A single side-by-side comparison table (renders in every format)."""
    d, n = a.day, a.night
    return {
        "type": "table",
        "headers": ["", "IF DAY (above horizon)", "IF NIGHT (below horizon)"],
        "rows": [
            ["Sect light", _cond(d.sect_light), _cond(n.sect_light)],
            [
                "Out-of-sect malefic",
                _cond(d.out_of_sect_malefic),
                _cond(n.out_of_sect_malefic),
            ],
            ["  → hardship reads", _MALEFIC_FLAVOR["day"], _MALEFIC_FLAVOR["night"]],
            ["In-sect benefic", _cond(d.in_sect_benefic), _cond(n.in_sect_benefic)],
            ["  → fortune reads", _BENEFIC_FLAVOR["day"], _BENEFIC_FLAVOR["night"]],
        ],
    }


def _lean_word(day_v: float, night_v: float) -> str:
    if abs(day_v - night_v) < 1e-9:
        return "even"
    return "DAY" if day_v > night_v else "NIGHT"


class SectRectificationSection:
    """Compare-hypothesis sect analysis — day vs night, anchored by the validated
    daylight × malefic classifier (~70% LOO). An *indicator, not an oracle*.

    Events/temperament are auto-looked-up for notables (by chart name); pass them
    explicitly for anyone else, or pass ``events=()`` for a geometry-only analysis.
    """

    def __init__(
        self,
        *,
        events: Iterable | None = None,
        temperament: Iterable | None = None,
    ) -> None:
        self._events = events
        self._temperament = temperament

    @property
    def section_name(self) -> str:
        return "Sect Rectification"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        a = analyze_sect(chart, events=self._events, temperament=self._temperament)

        anchor = {
            "Chart sect (as given)": (a.chart_sect or "undetermined").capitalize(),
            "Daylight prior P(day)": f"{a.daylight_fraction:.2f}  (geometry, the base rate)",
            "Calibrated P(day)": (
                f"{a.p_day:.2f}  → leans {a.leans.upper()} ({a.confidence:.0%} conf)"
                + ("" if a.has_events else "  [geometry only — no events]")
            ),
            "Reading": "indicator, not oracle — adjudicate with real knowledge",
        }
        if a.moon_band:
            anchor["⚠ Moon band"] = a.moon_band

        sections: list[tuple[str, dict[str, Any]]] = [
            ("Anchor", {"type": "key_value", "data": anchor}),
            ("Day vs Night hypotheses", _hypothesis_table(a)),
        ]

        if a.has_events or a.has_temperament:
            sections.append(
                (
                    "Evidence & convergence",
                    {"type": "text", "text": self._evidence_text(a)},
                )
            )

        return {"type": "compound", "sections": sections}

    def _evidence_text(self, a: SectAnalysis) -> str:
        lines: list[str] = []
        if a.has_events:
            lines.append("Evidence alignment — does the life match each hypothesis?")
            if a.hardship:
                lines.append(
                    f"  hardship flavour (malefic-of-sect, VALIDATED +0.35): "
                    f"leans {_lean_word(*a.hardship)}  "
                    f"({a.hardship[0]:.1f} day / {a.hardship[1]:.1f} night)"
                )
            if a.fortune:
                lines.append(
                    f"  fortune flavour  (benefic-of-sect): "
                    f"leans {_lean_word(*a.fortune)}  "
                    f"({a.fortune[0]:.1f} day / {a.fortune[1]:.1f} night)"
                )
            if a.firdaria:
                lines.append(
                    f"  firdaria time-lord fit: day-hits {a.firdaria.day_hits} / "
                    f"night-hits {a.firdaria.night_hits} → favours {a.firdaria.favors}"
                )
        if a.has_temperament:
            lines.append("")
            lines.append(
                "Soft signals (⚠ ~null on strangers — high value only with "
                "real first-hand knowledge):"
            )
            mt = a.malefic_temper or 0.0
            st = a.sect_light_temper or 0.0
            lines.append(
                f"  malefic-of-temperament (Mars-hot − Saturn-cold) = {mt:+.0f} → "
                f"{'DAY' if mt > 0 else 'NIGHT' if mt < 0 else '—'}"
            )
            lines.append(
                f"  sect-light temperament (Solar − Lunar)        = {st:+.0f} → "
                f"{'DAY' if st > 0 else 'NIGHT' if st < 0 else '—'}"
            )
        votes = a.technique_votes()
        dv = sum(1 for _, v in votes if v == "day")
        nv = len(votes) - dv
        lines.append("")
        lines.append(
            f"Convergence (counted, never summed): DAY {dv} · NIGHT {nv} "
            f"(of {len(votes)} techniques)"
        )
        lines.append(
            "→ SECT: trust this anchor — it is the only cross-validated signal (~70%). "
            "The soft/timing rows routinely point the wrong way; when they fight the "
            "anchor on sect, the anchor wins. TIME-within-sect is where your own "
            "knowledge decides."
        )
        return "\n".join(lines)


def _hhmm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


class SectConvergenceMatrixSection:
    """Two-lens Tebbs convergence matrix (exploratory, ~10s per render).

    Lens A lays out the distinct charts across the 24h scored by solar-arc /
    transits / profection; Lens B histograms which times the events themselves
    nominate. The timing signals are whisper-level (never summed) — the matrix is a
    *display* for a human, and defers to the validated sect anchor on sect.
    """

    def __init__(self, *, events: Iterable | None = None) -> None:
        self._events = events

    @property
    def section_name(self) -> str:
        return "Sect Convergence Matrix"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        m = convergence_matrix(chart, events=self._events)
        if not m.columns:
            return {
                "type": "text",
                "text": (
                    "No life events available for a convergence matrix. Supply "
                    "events=[...] or use a notable with a biographical timeline."
                ),
            }
        return {
            "type": "compound",
            "sections": [
                ("Lens A — structural band", self._lens_a_table(m)),
                (
                    "Lens B — event hooks",
                    {"type": "text", "text": self._lens_b_text(m)},
                ),
                ("Synthesis", {"type": "text", "text": self._synthesis_text(m)}),
            ],
        }

    def _lens_a_table(self, m: ConvergenceMatrix) -> dict[str, Any]:
        cols = m.columns
        heads = [""] + [f"{c.sect[0].upper()}{_hhmm(c.start_minute)}" for c in cols]

        def fit_cells(key: str) -> list[str]:
            peak = m.method_peak_index.get(key)
            return [
                (f"*{getattr(c, key):+.2f}" if i == peak else f"{getattr(c, key):+.2f}")
                for i, c in enumerate(cols)
            ]

        rows = [
            ["Ascendant", *[c.asc_sign[:3] for c in cols]],
            ["Asc-ruler", *[c.asc_ruler[:3] for c in cols]],
            ["sect light", *[_SECT_LIGHT_ABBR[c.sect][:3] for c in cols]],
            ["out-of-sect malefic", *[_MALEFIC_ABBR[c.sect][:3] for c in cols]],
            ["solar-arc → angles", *fit_cells("dir")],
            ["transits → angles", *fit_cells("trans")],
            ["profection", *fit_cells("prof")],
            [
                "firdaria (by sect)",
                *[
                    f"{(m.firdaria_day if c.sect == 'day' else m.firdaria_night):+.2f}"
                    for c in cols
                ],
            ],
            ["progressed Moon", *[f"{m.progressed_moon:+.2f}" for _ in cols]],
            ["convergence", *[("●" * n or "·") for n in m.convergence_counts]],
        ]
        return {"type": "table", "headers": heads, "rows": rows}

    def _lens_b_text(self, m: ConvergenceMatrix) -> str:
        lines = [
            "distinct events with an apt directed/transiting hit, across the 24h:",
            "",
        ]
        for h in range(24):
            n = m.hooks_by_hour[h]
            lines.append(f"  {h:02d}:00  {'█' * n}{'' if n else '·'}  {n or ''}")
        if m.hooks_spread:
            lines.append("")
            lines.append(
                "⚠ hooks spread across most of the day — the events do NOT localise "
                "time well (the expected ill-posed-time signature). Read peaks as weak."
            )
        if m.hook_peaks:
            lines.append("")
            lines.append("top event-nominated times:")
            for p in m.hook_peaks:
                lines.append(
                    f"  {_hhmm(p.minute)} ({p.sect}, Asc {p.asc_sign[:3]}): "
                    f"{p.count} events — " + ", ".join(p.detail)
                )
        return "\n".join(lines)

    def _synthesis_text(self, m: ConvergenceMatrix) -> str:
        anchor = m.anchor_sect.upper()
        lines = [
            f"validated sect anchor : {anchor}  (P(day)={m.p_day:.2f})  "
            "← the only cross-validated signal (~70%)"
        ]
        if m.a_convergent and m.a_winner_index is not None:
            w = m.columns[m.a_winner_index]
            lines.append(
                f"Lens A (structure)    : {w.sect}, Asc {w.asc_sign} @ "
                f"~{_hhmm(w.start_minute)}  ({max(m.convergence_counts)}/3 methods peak)"
            )
        else:
            lines.append(
                "Lens A (structure)    : no structural convergence — the "
                "timing methods peak in different columns (whisper-level)."
            )
        if m.hook_peaks:
            b = m.hook_peaks[0]
            lines.append(
                f"Lens B (event hooks)  : {b.sect}, Asc {b.asc_sign} @ {_hhmm(b.minute)} "
                f"({b.count} events nominate it — weakly)"
            )
        lines.append("")
        lines.append(
            "HOW TO READ: for SECT, trust the anchor — the timing lenses are "
            "whisper-level and routinely point the wrong way; when they fight the "
            "anchor on sect, the anchor wins. The lenses are for exploring "
            f"TIME-WITHIN-SECT ({anchor}), then deciding with first-hand knowledge. "
            "The matrix never collapses that step — by design."
        )
        return "\n".join(lines)
