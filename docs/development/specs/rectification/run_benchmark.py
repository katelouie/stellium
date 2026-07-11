#!/usr/bin/env python3
"""Sect-classifier benchmark over the 63-person corpus — the go/no-go number.

Blanks each person's time, classifies day/night from events alone, and scores
against the verified truth. Reports accuracy with a binomial 95% CI, a confusion
matrix, the baselines to beat, and a wall-clock profile.

    python run_benchmark.py            # full report
    python run_benchmark.py --misses   # also list the ones it got wrong
"""

from __future__ import annotations

import argparse
import math
import time

import harness
import sect
from models import load_corpus


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95% score interval for a binomial proportion (good for small n)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sect-classifier benchmark.")
    ap.add_argument("--misses", action="store_true", help="list misclassified people")
    args = ap.parse_args(argv)

    corpus = load_corpus()
    t0 = time.perf_counter()

    rows = []  # (name, truth, predicted, p_day)
    for p in corpus:
        truth = harness.true_sect(p)
        v = sect.classify_sect(p)
        rows.append((p.name, truth, v.predicted, v.p_day))

    elapsed = time.perf_counter() - t0

    n = len(rows)
    correct = sum(t == pr for _, t, pr, _ in rows)
    acc = correct / n
    lo, hi = wilson_ci(correct, n)

    # baselines
    n_day = sum(t == "day" for _, t, _, _ in rows)
    n_night = n - n_day
    majority = max(n_day, n_night) / n

    # confusion (truth × predicted)
    conf = {
        ("day", "day"): 0,
        ("day", "night"): 0,
        ("night", "day"): 0,
        ("night", "night"): 0,
    }
    for _, t, pr, _ in rows:
        conf[(t, pr)] += 1

    print("=" * 60)
    print("SECT CLASSIFIER — BENCHMARK (v0: firdaria × significators)")
    print("=" * 60)
    print(f"n = {n}   correct = {correct}   accuracy = {acc:.1%}")
    print(f"95% CI (Wilson) = [{lo:.1%}, {hi:.1%}]")
    print()
    print(f"corpus sect balance: day={n_day}  night={n_night}")
    print(f"baseline — majority class: {majority:.1%}")
    print("baseline — chance:         50.0%")
    print()
    print("confusion (rows=truth, cols=predicted):")
    print("            pred day   pred night")
    print(f"  true day    {conf[('day', 'day')]:>5}       {conf[('day', 'night')]:>5}")
    print(
        f"  true night  {conf[('night', 'day')]:>5}       {conf[('night', 'night')]:>5}"
    )
    print()

    # pre-registered go/no-go (spec §6): acc >= 65% AND CI lower bound > majority.
    verdict = "GO" if (acc >= 0.65 and lo > majority) else "NO-GO"
    print(f"pre-registered gate: acc ≥ 65% AND CI-low > majority ({majority:.1%})")
    print(f"  -> {verdict}")
    print()
    print(
        f"profile: {elapsed:.1f}s for {n} people "
        f"({elapsed / n * 1000:.0f} ms/person, ~3 chart builds each)"
    )

    if args.misses:
        print("\nmisclassified:")
        for name, t, pr, p_day in rows:
            if t != pr:
                print(f"  {name:28} truth={t:5} pred={pr:5} P(day)={p_day:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
