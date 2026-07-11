#!/usr/bin/env python3
"""Phase-A2 benchmark: primary-directions posterior → sect marginal + TIME recovery.

python run_directions_benchmark.py
"""

from __future__ import annotations

import argparse
import statistics
import time

import harness
from directions import make_directions_scorer
from models import load_corpus
from posterior import build_posterior
from run_benchmark import wilson_ci


def circ(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, 1440 - d)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=20)
    ap.add_argument("--temperature", type=float, default=0.5)
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args(argv)

    corpus = load_corpus()
    t0 = time.perf_counter()
    rows = []  # (name, truth_sect, p_day, true_min, map_min, mass90, mass180)
    for p in corpus:
        bd = p.birth_data
        true_min = int(bd.time[:2]) * 60 + int(bd.time[3:])
        truth = harness.true_sect(p)
        post = build_posterior(
            p,
            make_directions_scorer(p),
            step_minutes=args.step,
            temperature=args.temperature,
        )
        mass90 = sum(
            c.prob for c in post.candidates if circ(c.minute_of_day, true_min) <= 90
        )
        mass180 = sum(
            c.prob for c in post.candidates if circ(c.minute_of_day, true_min) <= 180
        )
        rows.append(
            (p.name, truth, post.p_day, true_min, post.map_minute, mass90, mass180)
        )
    elapsed = time.perf_counter() - t0

    n = len(rows)
    # sect marginal
    correct = sum((pd > 0.5) == (t == "day") for _, t, pd, _, _, _, _ in rows)
    lo, hi = wilson_ci(correct, n)
    n_day = sum(t == "day" for _, t, _, _, _, _, _ in rows)
    majority = max(n_day, n - n_day) / n
    # time recovery
    errs = [circ(mm, tm) for _, _, _, tm, mm, _, _ in rows]
    med_err = statistics.median(errs)
    mean_mass90 = statistics.mean(m for *_, m, _ in rows)
    mean_mass180 = statistics.mean(m for *_, m in rows)

    print("=" * 64)
    print("PHASE A2 — primary-directions posterior")
    print("=" * 64)
    print(f"n = {n}   step = {args.step} min   T = {args.temperature}")
    print("\nSECT MARGINAL:")
    print(f"  accuracy = {correct / n:.1%}   CI = [{lo:.1%}, {hi:.1%}]")
    print(f"  baselines: majority {majority:.1%}, daylight+malefic 69.8%")
    print("\nTIME RECOVERY (posterior mode vs true time):")
    print(f"  median |Δ| = {med_err} min   (chance ≈ 360 min)")
    print(
        f"  mean posterior mass within ±90 min of truth  = {mean_mass90:.3f}  (chance 0.125)"
    )
    print(
        f"  mean posterior mass within ±180 min of truth = {mean_mass180:.3f}  (chance 0.25)"
    )
    print(f"\nprofile: {elapsed:.1f}s  ({elapsed / n * 1000:.0f} ms/person)")

    if args.detail:
        for name, _t, _pd, tm, mm, m90, _ in sorted(
            rows, key=lambda r: circ(r[4], r[3])
        ):
            print(
                f"  {name:26} true={tm // 60:02d}:{tm % 60:02d} MAP={mm // 60:02d}:{mm % 60:02d} "
                f"|Δ|={circ(mm, tm):4d}m mass±90={m90:.2f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
