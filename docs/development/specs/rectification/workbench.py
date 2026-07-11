#!/usr/bin/env python3
"""Fork (2): the compare-hypothesis sect workbench.

Mechanises what a practitioner does by hand to settle sect on an unknown-time
chart: construct BOTH the day and the night hypothesis, derive the sect-dependent
structures each one implies, lay them side by side, anchor the whole thing with the
one quantitative signal that survived validation (daylight prior × malefic-of-sect,
~70% LOO), tally convergence across techniques Tebbs-style — and then STOP, handing
the adjudication to the human, who has the high-resolution truth (knowing the
person) that no model does.

This is deliberately **not** an inference engine. Our ML rematch proved a model
cannot exceed thin biographical truth (~70%); the value here is the *display*, not
a verdict. The calibrated P(day) is shown as an indicator, never an oracle.

Works on any ``CorpusPerson`` — including one whose birth *time* is unknown, since
the two hypotheses are built from a noon (day-sect) and midnight (night-sect) cast,
never from the real time.

    python workbench.py "Frida Kahlo"
    python workbench.py "Marilyn Monroe"
"""

from __future__ import annotations

import argparse
import sys

import harness
import sect_classifier as sc
import sect_signals as sig
from models import CorpusPerson, load_corpus
from probe_compare_hypothesis import malefic_temperament_signal
from probe_dignity_sect import essential_dignity
from probe_temperament_sect import temperament_signal
from sect import classify_sect

# The out-of-sect malefic (the sharper destroyer) and in-sect benefic per sect.
OUT_OF_SECT_MALEFIC = {"day": "Mars", "night": "Saturn"}
IN_SECT_BENEFIC = {"day": "Jupiter", "night": "Venus"}
SECT_LIGHT = {"day": "Sun", "night": "Moon"}

MALEFIC_FLAVOR = {
    "day": "hot, sharp, sudden — accidents, violence, fever, conflict, burns",
    "night": "cold, slow, chronic — illness, poverty, confinement, decline, loss",
}
BENEFIC_FLAVOR = {
    "day": "Jupiter-toned fortune — honour, wealth, law, faith, expansion, travel",
    "night": "Venus-toned fortune — love, art, beauty, pleasure, music, women",
}


def _dignity_label(planet: str, sign: str) -> str:
    return {
        5: "domicile",
        4: "exalted",
        0: "peregrine",
        -4: "in fall",
        -5: "in detriment",
    }[essential_dignity(planet, sign)]


def _condition(chart, planet: str) -> str:
    obj = chart.get_object(planet)
    if obj is None:
        return "—"
    retro = getattr(obj, "retrograde", None)
    rx = " ℞" if retro else ""
    return f"{obj.sign} ({_dignity_label(planet, obj.sign)}){rx}"


def _moon_band_note(day_chart, night_chart) -> str:
    """Flag the practitioner's key worry: does the Moon cross a sign in the 24h?"""
    noon = day_chart.get_object("Moon").sign
    midnight = night_chart.get_object("Moon").sign
    if noon == midnight:
        return f"Moon stays in {noon} across the day — sign-level reading is safe."
    return (
        f"⚠ Moon crosses {midnight} → {noon} within the 24h — its sign, and any "
        f"threshold it rules, is a BAND, not a point. Weigh accordingly."
    )


def _col(text: str, width: int = 46) -> str:
    return text[: width - 1] + "…" if len(text) > width else text.ljust(width)


def build_report(person: CorpusPerson, model: sc.SectModel) -> str:
    day_chart = harness.build_chart(person.birth_data, (12, 0))
    night_chart = harness.build_chart(person.birth_data, (0, 0))

    # ---- quantitative anchor (the one validated signal) ----
    feats = sc.features(person)
    p_day = model.p_day(feats)
    daylight = sc.daylight_fraction(person)
    mars_h, saturn_h = sig.malefic_tally(person)
    jup_f, ven_f = sig.benefic_tally(person)

    lean = "DAY" if p_day >= 0.5 else "NIGHT"
    conf = max(p_day, 1 - p_day)

    L: list[str] = []
    L.append("=" * 96)
    L.append(f"  COMPARE-HYPOTHESIS SECT WORKBENCH — {person.name}")
    L.append(
        f"  {person.birth_data.place}  ·  {person.birth_data.date}  "
        f"(Rodden {person.birth_data.rodden_rating})"
    )
    L.append("=" * 96)
    L.append("")
    L.append("  QUANTITATIVE ANCHOR  (validated daylight × malefic-of-sect, ~70% LOO)")
    L.append(
        f"    daylight prior P(day | date, latitude) = {daylight:.2f}   "
        f"(geometry alone, the base rate)"
    )
    L.append(
        f"    hardship flavour   Mars {mars_h:.1f}  vs  Saturn {saturn_h:.1f}   "
        f"→ leans {'DAY' if mars_h > saturn_h else 'NIGHT' if saturn_h > mars_h else '—'}"
    )
    L.append(
        f"    calibrated  P(day) = {p_day:.2f}   →   leans {lean} "
        f"({conf:.0%} confidence)"
    )
    L.append(
        "    ↑ indicator, NOT an oracle. Adjudicate below with what you actually "
        "know of the person."
    )
    L.append("")
    L.append(f"  {_moon_band_note(day_chart, night_chart)}")
    L.append("")

    # ---- side-by-side hypotheses ----
    L.append("-" * 96)
    L.append(
        f"  {'│ IF DAY (born above the horizon)':<47}"
        f"│ IF NIGHT (born below the horizon)"
    )
    L.append("-" * 96)

    def row(label: str, day_val: str, night_val: str) -> None:
        L.append(f"  {label}")
        L.append(f"    {_col('│ ' + day_val)}│ {night_val}")

    row(
        "Sect light (the leading luminary):",
        f"Sun in {_condition(day_chart, 'Sun')}",
        f"Moon in {_condition(night_chart, 'Moon')}",
    )
    row(
        "Out-of-sect malefic (the sharper destroyer):",
        f"Mars — {_condition(day_chart, 'Mars')}",
        f"Saturn — {_condition(night_chart, 'Saturn')}",
    )
    row("  …so hardship should read:", MALEFIC_FLAVOR["day"], MALEFIC_FLAVOR["night"])
    row(
        "In-sect benefic (the stronger helper):",
        f"Jupiter — {_condition(day_chart, 'Jupiter')}",
        f"Venus — {_condition(night_chart, 'Venus')}",
    )
    row("  …so fortune should read:", BENEFIC_FLAVOR["day"], BENEFIC_FLAVOR["night"])
    L.append("")

    # ---- evidence alignment: the falsification test ----
    L.append("-" * 96)
    L.append("  EVIDENCE ALIGNMENT — does the life match the hypothesis's prediction?")
    L.append("-" * 96)
    hv = classify_sect(person)
    day_hits = sum(1 for f in hv.fits if f.favors == "day")
    night_hits = sum(1 for f in hv.fits if f.favors == "night")
    ties = sum(1 for f in hv.fits if f.favors == "tie")

    def verdict(day_score: float, night_score: float, name: str) -> str:
        if abs(day_score - night_score) < 1e-9:
            return f"    {name}: even"
        w = "DAY" if day_score > night_score else "NIGHT"
        return f"    {name}: leans {w}  ({day_score:.1f} day / {night_score:.1f} night)"

    L.append(
        verdict(
            mars_h,
            saturn_h,
            "hardship-flavour (malefic-of-sect · events, VALIDATED +0.35)",
        )
    )
    L.append(verdict(jup_f, ven_f, "fortune-flavour  (benefic-of-sect · events)"))
    L.append(
        f"    firdaria time-lord fit (per-event): "
        f"day-hits {day_hits} / night-hits {night_hits}"
        + (f" / ties {ties}" if ties else "")
    )
    L.append("")

    # ---- soft signals: shown, but flagged as low-resolution ----
    mt = malefic_temperament_signal(person)
    st = temperament_signal(person)
    L.append(
        "  SOFT SIGNALS  (⚠ null on the corpus — HIGH value only with real "
        "first-hand knowledge)"
    )
    L.append(
        f"    malefic-of-temperament  Mars-hot − Saturn-cold = {mt:+.0f}   "
        f"→ {'DAY' if mt > 0 else 'NIGHT' if mt < 0 else '—'}   "
        "(the mom tie-breaker — trust YOUR read, not the keyword tally)"
    )
    L.append(
        f"    sect-light temperament  Solar − Lunar        = {st:+.0f}   "
        f"→ {'DAY' if st > 0 else 'NIGHT' if st < 0 else '—'}"
    )
    L.append("")

    # ---- Tebbs-style convergence tally ----
    L.append("-" * 96)
    L.append("  CONVERGENCE TALLY (Tebbs) — count each independent technique's vote")
    L.append("-" * 96)
    votes: list[tuple[str, str]] = []
    votes.append(("daylight prior", "day" if daylight > 0.5 else "night"))
    if mars_h != saturn_h:
        votes.append(("hardship flavour", "day" if mars_h > saturn_h else "night"))
    if jup_f != ven_f:
        votes.append(("fortune flavour", "day" if jup_f > ven_f else "night"))
    if hv.signal_day != hv.signal_night:
        votes.append(
            ("firdaria fit", "day" if hv.signal_day > hv.signal_night else "night")
        )
    dv = sum(1 for _, v in votes if v == "day")
    nv = len(votes) - dv
    for name, v in votes:
        L.append(f"    {name:24} → {v.upper()}")
    L.append("    ───────────────────────────────")
    L.append(
        f"    CONVERGENCE:  DAY {dv}  ·  NIGHT {nv}   (of {len(votes)} techniques)"
    )
    if dv and nv:
        L.append(
            "    ↑ techniques DISAGREE — this is exactly where the trained eye "
            "and real truth decide."
        )
    else:
        L.append(
            "    ↑ techniques CONVERGE — but convergence is corroboration, not "
            "proof (thin-truth ceiling ~70%)."
        )
    L.append(
        "    [hooks for future robustness: solar-arc-to-angles, progressed Moon, "
        "outer-planet transits]"
    )
    L.append("=" * 96)
    return "\n".join(L)


def _fit_corpus_model(corpus: list[CorpusPerson]) -> sc.SectModel:
    """Fit the validated 2-feature classifier on the whole corpus (the ~70% model)."""
    rows = [sc.features(p) for p in corpus]
    y = [1 if harness.true_sect(p) == "day" else 0 for p in corpus]
    return sc.fit(rows, y)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compare-hypothesis sect workbench.")
    ap.add_argument(
        "name",
        nargs="?",
        default="Frida Kahlo",
        help="corpus person to adjudicate (default: Frida Kahlo)",
    )
    args = ap.parse_args(argv)

    corpus = load_corpus()
    person = next((p for p in corpus if p.name.lower() == args.name.lower()), None)
    if person is None:
        print(f"'{args.name}' not in corpus. Available:", file=sys.stderr)
        for p in corpus:
            print(f"  {p.name}", file=sys.stderr)
        return 1

    print(
        "fitting the validated classifier on the corpus…", file=sys.stderr, flush=True
    )
    model = _fit_corpus_model(corpus)
    print(build_report(person, model))
    # honesty footer: how did the anchor do vs the (normally-hidden) truth?
    truth = harness.true_sect(person)
    print(
        f"\n  (ground truth for this corpus example: {truth.upper()} — "
        "hidden in real unknown-time use)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
