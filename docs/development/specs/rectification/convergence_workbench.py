#!/usr/bin/env python3
"""Fork (2), deepened: the two-lens Tebbs convergence workbench.

Puts *all the timing info* in front of a human-in-the-loop practitioner, through
TWO complementary lenses over one shared candidate-time sweep — never collapsing to
a verdict (our study proved blind combination *cancels* signal; only human
selection lifts it, so we display and let the eye decide):

  LENS A — the STRUCTURAL band. Columns are the genuinely distinct charts across the
     24h (each sect region × Ascendant sign). Rows are the methods (sect structure +
     solar-arc, transits, profection, firdaria, progressed Moon). "Which chart is it,
     and how well does each one fit the known life?"

  LENS B — the EVENT HOOKS. The events themselves nominate times: a histogram across
     the 24h of how many distinct events get an apt directed/transiting hit at each
     candidate time. "Which times do the events collectively point at?"

  SYNTHESIS — do the two lenses (and the validated sect anchor) agree?

Every timing score here is *whisper-level* (single techniques placed the truth at
only the ~55–59th percentile; see RECTIFICATION_REPORT.md). The workbench shows them
raw and never sums them into a master score. Convergence is COUNTED, not summed.

    python convergence_workbench.py "Frida Kahlo"
"""

from __future__ import annotations

import argparse
import statistics
import sys

import directions as dr
import harness
import transits as tr
import workbench as wb
from models import CorpusPerson, load_corpus
from profection import DOMICILE_RULER, make_profection_scorer
from progressed_moon import progressed_moon_signal
from sect import classify_sect

SWEEP_STEP = 15  # minutes — the fine grid feeding both lenses

OUT_OF_SECT_MALEFIC = {"day": "Mars", "night": "Saturn"}
SECT_LIGHT = {"day": "Sun", "night": "Moon"}


def _hhmm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def _sweep(person: CorpusPerson) -> list[dict]:
    """Fine grid: per candidate time, structure + each method's fit + event hooks."""
    bd = person.birth_data
    dir_score = dr.make_directions_scorer(person)
    prof_score = make_profection_scorer(person)
    trans_score = tr.make_transits_scorer(person)
    tpos = tr.transiter_positions(person)  # cached for hooks

    grid: list[dict] = []
    for minute in range(0, 24 * 60, SWEEP_STEP):
        chart = harness.build_chart(bd, divmod(minute, 60))
        grid.append(
            {
                "minute": minute,
                "chart": chart,
                "sect": chart.sect,
                "asc": chart.get_object("ASC").sign,
                "dir": dir_score(person, chart),
                "prof": prof_score(person, chart),
                "trans": trans_score(person, chart),
                "dir_hooks": set(dr.event_hooks(person, chart)),
                "trans_hooks": set(tr.event_hooks(person, chart, tpos)),
            }
        )
    return grid


# ── LENS A: the structural band ───────────────────────────────────────────────


def _columns(grid: list[dict]) -> list[dict]:
    """Collapse the fine grid into distinct (sect, Asc-sign) charts."""
    cols: list[dict] = []
    for cell in grid:
        key = (cell["sect"], cell["asc"])
        if not cols or cols[-1]["key"] != key:
            cols.append({"key": key, "members": [cell]})
        else:
            cols[-1]["members"].append(cell)
    # merge a wrapped-midnight column that shares the first column's key
    if len(cols) > 1 and cols[0]["key"] == cols[-1]["key"]:
        cols[0]["members"] = cols[-1]["members"] + cols[0]["members"]
        cols.pop()
    for c in cols:
        members = c["members"]
        rep = members[len(members) // 2]  # representative chart (middle of the span)
        c["sect"], c["asc"] = c["key"]
        c["rep"] = rep
        c["start"] = members[0]["minute"]
        for m in ("dir", "prof", "trans"):
            c[m] = statistics.mean(x[m] for x in members)
    cols.sort(
        key=lambda c: c["start"]
    )  # chronological (wrapped-midnight col sorts last)
    return cols


def _lens_a(person: CorpusPerson, cols: list[dict], pmoon: float, fird) -> list[str]:
    W = 8  # per-column cell width
    heads = [c["sect"][:1].upper() + _hhmm(c["start"]) for c in cols]

    def line(label: str, cells: list[str]) -> str:
        return f"  {label:26}" + "".join(f"{c:>{W}}" for c in cells)

    L = ["", "═" * (28 + W * len(cols))]
    L.append("  LENS A — STRUCTURAL BAND  (each column = a genuinely distinct chart)")
    L.append("═" * (28 + W * len(cols)))
    L.append(line("time / sect", heads))
    L.append(line("Ascendant", [c["asc"][:3] for c in cols]))
    L.append(
        line(
            "  Asc-ruler",
            [DOMICILE_RULER[c["asc"]][:3] for c in cols],
        )
    )
    L.append(line("sect light", [SECT_LIGHT[c["sect"]][:3] for c in cols]))
    L.append(
        line("out-of-sect malefic", [OUT_OF_SECT_MALEFIC[c["sect"]][:3] for c in cols])
    )
    L.append("  " + "─" * (26 + W * len(cols)))
    L.append("  timing fit vs known events  (whisper-level — raw, never summed)")

    # per-column time-discriminating methods; mark each method's argmax column
    def fit_row(label: str, key: str) -> str:
        vals = [c[key] for c in cols]
        best = max(range(len(cols)), key=lambda i: vals[i])
        cells = [
            (f"*{v:+.2f}" if i == best else f"{v:+.2f}") for i, v in enumerate(vals)
        ]
        return line(label, cells)

    L.append(fit_row("  solar-arc → angles", "dir"))
    L.append(fit_row("  transits → angles", "trans"))
    L.append(fit_row("  profection (annual)", "prof"))
    L.append("  " + "─" * (26 + W * len(cols)))
    L.append("  reference (near time-independent)")
    L.append(
        line(
            "  firdaria (by sect)",
            [
                f"{(fird.signal_day if c['sect'] == 'day' else fird.signal_night):+.2f}"
                for c in cols
            ],
        )
    )
    L.append(line("  progressed Moon", [f"{pmoon:+.2f}" for _ in cols]))
    L.append("  " + "─" * (26 + W * len(cols)))

    # convergence: how many of the 3 discriminating methods peak in each column
    peaks = {"dir": None, "trans": None, "prof": None}
    for key in peaks:
        vals = [c[key] for c in cols]
        peaks[key] = max(range(len(cols)), key=lambda i: vals[i])
    counts = [sum(1 for k in peaks if peaks[k] == i) for i in range(len(cols))]
    L.append(line("CONVERGENCE (methods peak)", [("●" * n or "·") for n in counts]))
    L.append(
        "  * = that method's best column.  ● = a method peaks here (counted, not summed)."
    )
    return L


# ── LENS B: event hooks ───────────────────────────────────────────────────────


def _lens_b(person: CorpusPerson, grid: list[dict]) -> list[str]:
    for cell in grid:
        cell["hooked"] = cell["dir_hooks"] | cell["trans_hooks"]
    maxh = max((len(c["hooked"]) for c in grid), default=0)

    L = ["", "═" * 78]
    L.append("  LENS B — EVENT HOOKS  (which times do the events themselves nominate?)")
    L.append("═" * 78)
    if maxh == 0:
        L.append(
            "  No directed/transiting hooks landed within orb — the events do "
            "not nominate\n  any particular time (fully consistent with the "
            "ill-posed-time finding)."
        )
        return L
    L.append("  distinct events with an apt directed/transiting hit, across the 24h:")
    L.append("")
    # compact histogram, one row per grid step bucketed to the hour for width
    by_hour: dict[int, int] = {}
    for c in grid:
        h = c["minute"] // 60
        by_hour[h] = max(by_hour.get(h, 0), len(c["hooked"]))
    for h in range(24):
        n = by_hour.get(h, 0)
        bar = "█" * n
        L.append(f"    {h:02d}:00  {bar}{'' if n else '·'}  {n or ''}")
    # honest read of the histogram's shape
    hours_hit = [by_hour.get(h, 0) for h in range(24)]
    spread = sum(1 for v in hours_hit if v >= 0.6 * maxh)
    if spread >= 8:
        L.append("")
        L.append(
            "  ⚠ the hooks are spread across most of the day — the events do NOT "
            "localise time\n    well (the expected ill-posed-time signature). Read "
            "the peaks as weak nominations."
        )

    # top peak times and what hooks them
    peaks = sorted(grid, key=lambda c: -len(c["hooked"]))[:3]
    L.append("")
    L.append("  top event-nominated times:")
    for c in peaks:
        if not c["hooked"]:
            continue
        who = []
        for i in sorted(c["hooked"]):
            e = person.events[i]
            tech = []
            if i in c["dir_hooks"]:
                tech.append("dir")
            if i in c["trans_hooks"]:
                tech.append("tr")
            who.append(f"{e.date_str}·{e.type}[{'+'.join(tech)}]")
        L.append(
            f"    {_hhmm(c['minute'])} ({c['sect']}, Asc {c['asc'][:3]}): "
            f"{len(c['hooked'])} events — " + ", ".join(who[:6])
        )
    return L


# ── synthesis ─────────────────────────────────────────────────────────────────


def _synthesis(cols: list[dict], grid: list[dict], p_day: float) -> list[str]:
    # Lens-A convergence winner (most methods peaking)
    def peak_col(key: str) -> int:
        vals = [c[key] for c in cols]
        return max(range(len(cols)), key=lambda i: vals[i])

    peaks = [peak_col(k) for k in ("dir", "trans", "prof")]
    best_count = max(peaks.count(i) for i in set(peaks))
    a_winner = max(set(peaks), key=peaks.count)
    a_col = cols[a_winner]
    a_convergent = best_count >= 2  # do ≥2 methods actually agree on a column?

    # Lens-B winner (most events hooked)
    b = max(grid, key=lambda c: len(c["dir_hooks"] | c["trans_hooks"]))
    b_hooked = len(b["dir_hooks"] | b["trans_hooks"])

    anchor = "DAY" if p_day >= 0.5 else "NIGHT"
    L = ["", "═" * 78, "  SYNTHESIS — do the lenses agree?", "═" * 78]
    L.append(
        f"    validated sect anchor : {anchor}  (P(day)={p_day:.2f})   "
        "← the ONLY cross-validated signal (~70%)"
    )
    if a_convergent:
        L.append(
            f"    Lens A (structure)    : {a_col['sect']}, Asc {a_col['asc']} "
            f"@ ~{_hhmm(a_col['start'])}  ({best_count}/3 timing methods peak together)"
        )
    else:
        L.append(
            "    Lens A (structure)    : no structural convergence — the 3 timing "
            "methods peak in\n                            different columns "
            f"({', '.join(cols[i]['asc'][:3] for i in peaks)}). Whisper-level."
        )
    if b_hooked:
        L.append(
            f"    Lens B (event hooks)  : {b['sect']}, Asc {b['asc']} "
            f"@ {_hhmm(b['minute'])}  ({b_hooked} events nominate it — weakly)"
        )
    else:
        L.append("    Lens B (event hooks)  : no time nominated (events silent)")

    L.append("")
    # The hierarchy our study earned: anchor decides SECT; lenses only explore TIME.
    L.append("  HOW TO READ THIS (the hierarchy the validation earned):")
    L.append(
        "    • SECT — trust the anchor. The timing lenses are whisper-level "
        "(~55–59th pct) and\n      routinely point the wrong way; when they "
        "disagree with the anchor on sect, the\n      anchor wins. It is the only "
        "signal that survived cross-validation."
    )
    L.append(
        "    • TIME-WITHIN-SECT — this is what the lenses are FOR. Inside the "
        f"anchored sect ({anchor}),\n      read where Lens A structure and Lens B "
        "hooks reinforce each other, then decide\n      with first-hand knowledge. "
        "The tool never collapses this step for you — by design."
    )

    a_sect_agrees = (not a_convergent) or a_col["sect"] == anchor.lower()
    if a_convergent and b_hooked and a_col["sect"] == b["sect"] == anchor.lower():
        L.append(
            "  → all three agree on sect: the strongest honest picture. Still "
            "corroboration, not proof."
        )
    elif not a_sect_agrees or (b_hooked and b["sect"] != anchor.lower()):
        L.append(
            "  → the timing lenses fight the anchor on sect. Per the rule above, "
            "hold the anchor's\n    sect and treat the lenses as contested — this "
            "is precisely where the eye earns its keep."
        )
    L.append(
        "  [future rows: primary directions proper, tertiary progressions, "
        "solar-return angles]"
    )
    return L


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Two-lens Tebbs convergence workbench.")
    ap.add_argument("name", nargs="?", default="Frida Kahlo")
    ap.add_argument(
        "--no-sect-block",
        action="store_true",
        help="skip the sect-anchor block (show only the two lenses)",
    )
    args = ap.parse_args(argv)

    corpus = load_corpus()
    person = next((p for p in corpus if p.name.lower() == args.name.lower()), None)
    if person is None:
        print(f"'{args.name}' not in corpus.", file=sys.stderr)
        return 1

    print(
        "fitting validated classifier + sweeping candidate times…",
        file=sys.stderr,
        flush=True,
    )
    model = wb._fit_corpus_model(corpus)

    if not args.no_sect_block:
        print(wb.build_report(person, model))

    p_day = model.p_day(wb.sc.features(person))
    fird = classify_sect(person)
    pmoon = progressed_moon_signal(person)
    grid = _sweep(person)
    cols = _columns(grid)

    print("\n".join(_lens_a(person, cols, pmoon, fird)))
    print("\n".join(_lens_b(person, grid)))
    print("\n".join(_synthesis(cols, grid, p_day)))

    truth = harness.true_sect(person)
    print(f"\n  (corpus ground truth: {truth.upper()} — hidden in real use)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
