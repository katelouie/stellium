#!/usr/bin/env python3
"""Probe: does the malefic-contrary-to-sect doctrine recover sect from events?

Traditional doctrine: the malefic *out of sect* is the sharper destroyer.
  * DAY charts  -> Mars is out of sect  -> expect Mars-flavored hardship
  * NIGHT charts -> Saturn is out of sect -> expect Saturn-flavored hardship

So: Mars-heavy hardship -> predict DAY; Saturn-heavy -> predict NIGHT. This is
(almost) chart-free — it reads the *character* of a life's misfortunes — and it
tests a different mechanism than the firdaria time-lord sequence that failed.

Keyword lists are set from Mars/Saturn significations a priori (not tuned).

    python probe_malefic_sect.py            # accuracy + CI + confusion + corr
    python probe_malefic_sect.py --detail   # per-person Mars/Saturn tallies
"""

from __future__ import annotations

import argparse
import statistics

import harness
from models import load_corpus
from run_benchmark import wilson_ci

# Only misfortune events inform the malefic-of-sect.
HARDSHIP_TYPES = {
    "health_crisis",
    "accident",
    "financial_loss",
    "bereavement_parent",
    "bereavement_other",
    "legal",
}

# Mars: hot, sharp, sudden, iron, blood, fire, violence.
MARS_WORDS = (
    "accident",
    "crash",
    "collision",
    "shot",
    "gunshot",
    "gun ",
    "stabbed",
    "knife",
    "killed",
    "murder",
    "assassin",
    "war",
    "battle",
    "combat",
    "fight",
    "assault",
    "violence",
    "violent",
    "wound",
    "injury",
    "injured",
    "surgery",
    "operation",
    "amputat",
    "fire",
    "burned",
    "burns",
    "explosion",
    "blood",
    "acute",
    "overdose",
    "beaten",
    "shooting",
    "duel",
)
# Saturn: cold, slow, chronic, restriction, decay, poverty, confinement, age.
SATURN_WORDS = (
    "illness",
    "disease",
    "cancer",
    "tuberculosis",
    "chronic",
    "ill health",
    "prison",
    "jail",
    "imprison",
    "incarcerat",
    "bankruptcy",
    "bankrupt",
    "ruin",
    "poverty",
    "debt",
    "exile",
    "banish",
    "decline",
    "paralysis",
    "stroke",
    "depression",
    "melancholy",
    "old age",
    "natural causes",
    "starv",
    "foreclosure",
    "lingering",
    "confined",
    "arthritis",
    "polio",
    "dementia",
    "alzheimer",
)
# Per-type fallback lean when no keyword matches.
TYPE_LEAN = {
    "accident": "mars",
    "financial_loss": "saturn",
    "bereavement_parent": "saturn",
    "bereavement_other": "saturn",
    "legal": "saturn",  # confinement/restriction default
    "health_crisis": None,  # too ambiguous without a keyword
}

SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}


def _flavor(description: str, etype: str) -> str | None:
    text = description.lower()
    mars = any(w in text for w in MARS_WORDS)
    sat = any(w in text for w in SATURN_WORDS)
    if mars and not sat:
        return "mars"
    if sat and not mars:
        return "saturn"
    if mars and sat:
        return None  # mixed — abstain
    return TYPE_LEAN.get(etype)  # no keyword -> type default


def tally(person) -> tuple[float, float]:
    """(mars_score, saturn_score) over the person's hardship events."""
    mars = saturn = 0.0
    for e in person.events:
        if e.type not in HARDSHIP_TYPES:
            continue
        flav = _flavor(e.description, e.type)
        w = SIGNIFICANCE_WEIGHT.get(e.significance, 0.5)
        if flav == "mars":
            mars += w
        elif flav == "saturn":
            saturn += w
    return mars, saturn


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Malefic-contrary-to-sect probe.")
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args(argv)

    corpus = load_corpus()
    rows = []  # (name, truth, predicted, mars, saturn)
    undecided = 0
    for p in corpus:
        truth = harness.true_sect(p)
        mars, saturn = tally(p)
        if mars > saturn:
            pred = "day"
        elif saturn > mars:
            pred = "night"
        else:
            pred = "day"  # tie -> majority class
            undecided += 1
        rows.append((p.name, truth, pred, mars, saturn))

    n = len(rows)
    correct = sum(t == pr for _, t, pr, _, _ in rows)
    acc = correct / n
    lo, hi = wilson_ci(correct, n)
    n_day = sum(t == "day" for _, t, _, _, _ in rows)
    majority = max(n_day, n - n_day) / n

    conf = dict.fromkeys(
        [("day", "day"), ("day", "night"), ("night", "day"), ("night", "night")], 0
    )
    for _, t, pr, _, _ in rows:
        conf[(t, pr)] += 1

    # correlation of (mars - saturn) with day
    gaps = [(m - s, 1 if t == "day" else 0) for _, t, _, m, s in rows]
    xs = [g for g, _ in gaps]
    ys = [y for _, y in gaps]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in gaps) / n
    r = cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)

    print("=" * 60)
    print("MALEFIC-CONTRARY-TO-SECT PROBE (Mars→day, Saturn→night)")
    print("=" * 60)
    print(f"n = {n}   correct = {correct}   accuracy = {acc:.1%}")
    print(f"95% CI (Wilson) = [{lo:.1%}, {hi:.1%}]   majority = {majority:.1%}")
    print(f"corr(mars−saturn, day) = {r:+.3f}   (ties/undecided: {undecided})")
    print()
    print("confusion (rows=truth, cols=predicted):")
    print("            pred day   pred night")
    print(f"  true day    {conf[('day', 'day')]:>5}       {conf[('day', 'night')]:>5}")
    print(
        f"  true night  {conf[('night', 'day')]:>5}       {conf[('night', 'night')]:>5}"
    )
    verdict = "GO" if (acc >= 0.65 and lo > majority) else "NO-GO"
    print(f"\npre-registered gate -> {verdict}")

    if args.detail:
        print("\nper-person (mars vs saturn hardship):")
        for name, t, pr, m, s in sorted(rows, key=lambda x: x[3] - x[4]):
            mark = "✓" if t == pr else "✗"
            print(
                f"  {mark} {name:30} truth={t:5} pred={pr:5} mars={m:.1f} saturn={s:.1f}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
