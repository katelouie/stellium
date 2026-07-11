#!/usr/bin/env python3
"""Compare sect signals: malefic-only, benefic-only, combined.

python probe_sect_combined.py
python probe_sect_combined.py --detail
"""

from __future__ import annotations

import argparse
import statistics

import harness
import sect_signals as sig
from models import load_corpus
from run_benchmark import wilson_ci


def evaluate(corpus, truth, use_malefic, use_benefic):
    rows = []  # (name, truth, pred, score)
    undecided = 0
    for p in corpus:
        s = sig.sect_score(p, use_malefic=use_malefic, use_benefic=use_benefic)
        if s > 0:
            pred = "day"
        elif s < 0:
            pred = "night"
        else:
            pred = "day"  # tie -> majority
            undecided += 1
        rows.append((p.name, truth[p.name], pred, s))
    n = len(rows)
    correct = sum(t == pr for _, t, pr, _ in rows)
    acc = correct / n
    lo, hi = wilson_ci(correct, n)
    gaps = [(s, 1 if t == "day" else 0) for _, t, _, s in rows]
    xs = [g for g, _ in gaps]
    ys = [y for _, y in gaps]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in gaps) / n
    r = cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)
    conf = dict.fromkeys(
        [("day", "day"), ("day", "night"), ("night", "day"), ("night", "night")], 0
    )
    for _, t, pr, _ in rows:
        conf[(t, pr)] += 1
    return {
        "rows": rows,
        "acc": acc,
        "ci": (lo, hi),
        "corr": r,
        "undecided": undecided,
        "conf": conf,
        "correct": correct,
        "n": n,
    }


def line(label, res, majority):
    lo, hi = res["ci"]
    gate = "GO" if (res["acc"] >= 0.65 and lo > majority) else "no-go"
    print(
        f"{label:16} acc={res['acc']:.1%}  CI=[{lo:.1%},{hi:.1%}]  "
        f"corr={res['corr']:+.3f}  undecided={res['undecided']:>2}  -> {gate}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compare sect signals.")
    ap.add_argument("--detail", action="store_true")
    args = ap.parse_args(argv)

    corpus = load_corpus()
    truth = {p.name: harness.true_sect(p) for p in corpus}
    n_day = sum(v == "day" for v in truth.values())
    majority = max(n_day, len(truth) - n_day) / len(truth)

    malefic = evaluate(corpus, truth, True, False)
    benefic = evaluate(corpus, truth, False, True)
    combined = evaluate(corpus, truth, True, True)

    print("=" * 72)
    print("SECT SIGNALS — malefic vs benefic vs combined (positive = day)")
    print("=" * 72)
    print(f"n={len(corpus)}  majority baseline={majority:.1%}  (day={n_day})\n")
    line("malefic-only", malefic, majority)
    line("benefic-only", benefic, majority)
    line("COMBINED", combined, majority)
    c = combined["conf"]
    print("\ncombined confusion (rows=truth, cols=pred):")
    print("            pred day   pred night")
    print(f"  true day    {c[('day', 'day')]:>5}       {c[('day', 'night')]:>5}")
    print(f"  true night  {c[('night', 'day')]:>5}       {c[('night', 'night')]:>5}")

    if args.detail:
        print("\ncombined per-person (sorted by score):")
        for name, t, pr, s in sorted(combined["rows"], key=lambda x: x[3]):
            mark = "✓" if t == pr else "✗"
            print(f"  {mark} {name:30} truth={t:5} pred={pr:5} score={s:+.1f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
