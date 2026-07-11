#!/usr/bin/env python3
"""Combined sect-classifier benchmark (daylight prior + malefic), LOO cross-validated.

python run_sect_benchmark.py
python run_sect_benchmark.py --detail
"""

from __future__ import annotations

import argparse

import harness
import sect_classifier as sc
from models import load_corpus
from run_benchmark import wilson_ci


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Combined sect classifier (LOO-CV).")
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args(argv)

    corpus = load_corpus()
    feats = [sc.features(p) for p in corpus]
    y = [1 if harness.true_sect(p) == "day" else 0 for p in corpus]
    n = len(corpus)

    # In-sample (fit on all) — for the deployable model + coefficients.
    model = sc.fit(feats, y)
    ins = sum(
        (model.p_day(f) > 0.5) == (yy == 1) for f, yy in zip(feats, y, strict=True)
    )

    # Leave-one-out CV — the honest generalisation estimate.
    loo_rows = []
    for i in range(n):
        tr_x = [feats[j] for j in range(n) if j != i]
        tr_y = [y[j] for j in range(n) if j != i]
        m = sc.fit(tr_x, tr_y)
        p = m.p_day(feats[i])
        loo_rows.append((corpus[i].name, y[i], p))
    loo = sum((p > 0.5) == (yy == 1) for _, yy, p in loo_rows)

    lo, hi = wilson_ci(loo, n)
    n_day = sum(y)
    majority = max(n_day, n - n_day) / n

    print("=" * 60)
    print("SECT CLASSIFIER — daylight prior × malefic-of-sect (LOO-CV)")
    print("=" * 60)
    print(f"n = {n}   day = {n_day}   night = {n - n_day}")
    print(f"in-sample accuracy = {ins / n:.1%}")
    print(f"LOO-CV accuracy    = {loo}/{n} = {loo / n:.1%}   CI = [{lo:.1%}, {hi:.1%}]")
    print()
    print(
        f"baselines: chance 50%, majority {majority:.1%}, "
        f"daylight-alone 68.3%, malefic-alone 65.1%"
    )
    print(
        f"fitted std coefs: daylight={model.weights[0]:+.2f}, "
        f"malefic={model.weights[1]:+.2f}"
    )
    gate = "GO" if (loo / n >= 0.65 and lo > majority) else "NO-GO"
    print(f"\npre-registered gate (LOO acc ≥ 65% AND CI-low > majority) -> {gate}")

    if args.detail:
        print("\nLOO per person (sorted by P(day)):")
        for name, yy, p in sorted(loo_rows, key=lambda r: r[2]):
            truth = "day" if yy == 1 else "night"
            pred = "day" if p > 0.5 else "night"
            mark = "✓" if truth == pred else "✗"
            print(f"  {mark} {name:28} truth={truth:5} P(day)={p:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
