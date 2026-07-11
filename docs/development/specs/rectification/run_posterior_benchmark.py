#!/usr/bin/env python3
"""Phase-A1 benchmark: profection time-posterior → sect marginal + rising-sign recovery.

python run_posterior_benchmark.py
python run_posterior_benchmark.py --detail
"""

from __future__ import annotations

import argparse
import statistics
import time

import harness
from models import load_corpus
from posterior import build_posterior
from profection import SIGN_ORDER, make_profection_scorer
from run_benchmark import wilson_ci


def sign_distance(a: str, b: str) -> int:
    """Circular distance in signs (0..6)."""
    d = abs(SIGN_ORDER.index(a) - SIGN_ORDER.index(b)) % 12
    return min(d, 12 - d)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Profection posterior benchmark.")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--step", type=int, default=20, help="grid step (minutes)")
    ap.add_argument("--temperature", type=float, default=1.0)
    args = ap.parse_args(argv)

    corpus = load_corpus()
    t0 = time.perf_counter()

    rows = []  # (name, truth_sect, pred_sect, p_day, true_rising, map_rising)
    for p in corpus:
        true_chart = harness.true_chart(p)
        truth = true_chart.sect
        true_rising = true_chart.get_object("ASC").sign
        post = build_posterior(
            p,
            make_profection_scorer(p),
            step_minutes=args.step,
            temperature=args.temperature,
        )
        pred = "day" if post.p_day > 0.5 else "night"
        rows.append(
            (p.name, truth, pred, post.p_day, true_rising, post.map_rising_sign)
        )
    elapsed = time.perf_counter() - t0

    n = len(rows)
    # sect
    correct = sum(t == pr for _, t, pr, _, _, _ in rows)
    acc = correct / n
    lo, hi = wilson_ci(correct, n)
    n_day = sum(t == "day" for _, t, _, _, _, _ in rows)
    majority = max(n_day, n - n_day) / n
    gaps = [(pd, 1 if t == "day" else 0) for _, t, _, pd, _, _ in rows]
    xs = [g for g, _ in gaps]
    ys = [y for _, y in gaps]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in gaps) / n
    r = cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)

    # rising sign recovery
    exact = sum(tr == mr for _, _, _, _, tr, mr in rows)
    within1 = sum(sign_distance(tr, mr) <= 1 for _, _, _, _, tr, mr in rows)
    mean_dist = statistics.mean(sign_distance(tr, mr) for _, _, _, _, tr, mr in rows)

    print("=" * 66)
    print("PHASE A1 — profection time-posterior (sect marginal)")
    print("=" * 66)
    print(f"n = {n}   grid step = {args.step} min   T = {args.temperature}")
    print()
    print("SECT MARGINAL:")
    print(f"  accuracy = {acc:.1%}   CI = [{lo:.1%}, {hi:.1%}]")
    print(f"  corr(p_day, day) = {r:+.3f}")
    print(f"  baselines: chance 50%, majority {majority:.1%}, malefic prior 65.1%")
    print()
    print("RISING-SIGN RECOVERY (posterior mode vs true ascendant):")
    print(f"  exact  = {exact}/{n} = {exact / n:.1%}   (chance 8.3%)")
    print(f"  within ±1 sign = {within1}/{n} = {within1 / n:.1%}   (chance ~25%)")
    print(f"  mean sign distance = {mean_dist:.2f}   (chance 3.0)")
    print()
    print(f"profile: {elapsed:.1f}s  ({elapsed / n * 1000:.0f} ms/person)")

    if args.detail:
        print("\nper person (sorted by p_day):")
        for name, t, pr, pd, tr, mr in sorted(rows, key=lambda x: x[3]):
            mark = "✓" if t == pr else "✗"
            print(f"  {mark} {name:28} truth={t:5} P(day)={pd:.2f}  rising {tr}→{mr}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
