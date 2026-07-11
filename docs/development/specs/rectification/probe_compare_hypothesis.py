#!/usr/bin/env python3
"""Probe (1): the compare-hypothesis ML test.

Encodes the FULL contrastive (day-fit − night-fit) feature set a practitioner
actually uses when adjudicating sect by hand — construct both hypotheses, read
what falls out of each, see which nets more aligning signal — and asks whether a
model that *combines* them beats the validated two-feature daylight+malefic
classifier (~70% LOO). Two model families, testing two different hypotheses:

  * regularised **logistic** — "is there a *linear combination* we missed?"
  * a shallow **decision tree** — "is there an *interaction / veto* we missed?"
    (a tree can encode the "one HUGE indicator overrides everything" rule as a
    top split — literally the practitioner's override move.)

Features (all day-positive; >0 leans day, <0 leans night):
  1. daylight        logit P(day | date, lat)        geometric prior (validated)
  2. malefic_event   Mars−Saturn hardship flavour    validated +0.35
  3. malefic_temper  Mars-hot − Saturn-cold character NEW — the mom tie-breaker,
                        never before encoded (we only tested malefic on *events*)
  4. sectlight       Solar − Lunar character          tested null (solo)
  5. benefic_event   Jupiter − Venus fortune flavour  tested null (solo)
  6. firdaria        day-fit − night-fit event timing tested null (solo)

Prediction: ~70% — malefic dominates, thin biographical truth caps it. The value
is in MEASURING whether the fuller compare-hypothesis exceeds the single feature,
whether the NEW malefic-temperament feature adds independent signal, and which
features a free model actually leans on.

    source ~/.zshrc && pyenv activate starlight && \
        python docs/development/specs/rectification/probe_compare_hypothesis.py
"""

from __future__ import annotations

import math
import statistics

import harness
import sect_classifier as sc
import sect_signals as sig
from models import load_corpus
from probe_temperament_sect import temperament_signal
from run_benchmark import wilson_ci
from sect import classify_sect

# Daylight-fraction sweep resolution — matches the validated classifier (10 min).
DAYLIGHT_STEP = 10

# ── NEW feature: malefic-of-sect on TEMPERAMENT ───────────────────────────────
# Doctrine, same as the event version but read off *character* instead of events:
# the out-of-sect malefic colours the temperament. Day → Mars is out of sect →
# a hot, sharp, combative character. Night → Saturn out of sect → a cold, heavy,
# restrained one. So Mars-hot character → day, Saturn-cold → night. Keywords are
# a priori Mars/Saturn significations for *disposition*, disjoint in intent from
# the Solar/Lunar sect-light words (proud/authoritative vs receptive/private).
MARS_TEMPER_WORDS = (
    "aggressive",
    "angry",
    "anger",
    "hot-tempered",
    "hot temper",
    "quick-tempered",
    "temper",
    "irritable",
    "combative",
    "confrontational",
    "belligerent",
    "violent",
    "violence",
    "impulsive",
    "reckless",
    "rash",
    "brash",
    "daring",
    "fearless",
    "competitive",
    "aggression",
    "forceful",
    "fierce",
    "fiery",
    "restless",
    "energetic",
    "volatile",
    "explosive",
    "abrasive",
    "ruthless",
    "domineering",
    "pugnacious",
    "hostile",
    "sharp-tongued",
    "brave",
    "courageous",
    "audacious",
)
SATURN_TEMPER_WORDS = (
    "cold",
    "aloof",
    "detached",
    "disciplined",
    "restrained",
    "reserved",
    "serious",
    "austere",
    "stern",
    "grave",
    "dour",
    "rigid",
    "controlled",
    "cautious",
    "guarded",
    "methodical",
    "patient",
    "frugal",
    "miserly",
    "melancholic",
    "melancholy",
    "pessimistic",
    "fearful",
    "anxious",
    "inhibited",
    "withdrawn",
    "solitary",
    "stoic",
    "calculating",
    "hard-working",
    "industrious",
    "persevering",
    "duty",
    "dutiful",
    "responsible",
    "rigorous",
    "unyielding",
    "brooding",
)


def malefic_temperament_signal(person) -> float:
    """Mars-hot − Saturn-cold over the person's temperament (day-positive)."""
    mars = saturn = 0.0
    for tr in person.temperament:
        text = (tr.trait + " " + " ".join(tr.tags) + " " + tr.evidence).lower()
        mars += sum(w in text for w in MARS_TEMPER_WORDS)
        saturn += sum(w in text for w in SATURN_TEMPER_WORDS)
    return mars - saturn


# ── feature matrix (unsupervised — no label ever touched) ─────────────────────

FEATURE_NAMES = (
    "daylight",
    "malefic_event",
    "malefic_temper",
    "sectlight",
    "benefic_event",
    "firdaria",
)


def build_features(corpus) -> tuple[list[tuple[float, ...]], list[int]]:
    """Return (feature rows, truth labels[1=day])."""
    rows: list[tuple[float, ...]] = []
    y: list[int] = []
    for i, p in enumerate(corpus):
        dl = min(max(sc.daylight_fraction(p, DAYLIGHT_STEP), 1e-3), 1 - 1e-3)
        daylight = math.log(dl / (1 - dl))
        malefic_event = sig.sect_score(p, use_benefic=False)
        malefic_temper = malefic_temperament_signal(p)
        sectlight = temperament_signal(p)
        jup, ven = sig.benefic_tally(p)
        benefic_event = jup - ven
        v = classify_sect(p)
        firdaria = v.signal_day - v.signal_night
        rows.append(
            (
                daylight,
                malefic_event,
                malefic_temper,
                sectlight,
                benefic_event,
                firdaria,
            )
        )
        y.append(1 if harness.true_sect(p) == "day" else 0)
        print(f"  [{i + 1:>2}/{len(corpus)}] {p.name}", flush=True)
    return rows, y


# ── correlation helpers (pure python) ─────────────────────────────────────────


def corr(xs, ys) -> float:
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / n
    return cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)


def resid(target, controls) -> list[float]:
    """Residual of target after OLS on controls (+intercept)."""
    import numpy as np

    x = np.array([[1.0, *c] for c in zip(*controls, strict=True)])
    y = np.array(target)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return (y - x @ beta).tolist()


# ── shallow decision tree (hand-rolled CART; encodes the veto/interaction) ─────


class _Node:
    __slots__ = ("feat", "thr", "left", "right", "pred")

    def __init__(self) -> None:
        self.feat: int | None = None
        self.thr: float = 0.0
        self.left: _Node | None = None
        self.right: _Node | None = None
        self.pred: float = 0.5


def _gini(y: list[int]) -> float:
    n = len(y)
    if n == 0:
        return 0.0
    p = sum(y) / n
    return 1.0 - p * p - (1 - p) * (1 - p)


def build_tree(
    x: list[tuple[float, ...]], y: list[int], depth: int, max_depth: int, min_leaf: int
) -> _Node:
    node = _Node()
    node.pred = sum(y) / len(y)
    if depth >= max_depth or len(y) < 2 * min_leaf or node.pred in (0.0, 1.0):
        return node
    parent = _gini(y)
    best = None  # (gain, feat, thr, left_idx, right_idx)
    for f in range(len(x[0])):
        vals = sorted({row[f] for row in x})
        for a, b in zip(vals, vals[1:], strict=False):
            thr = (a + b) / 2
            left = [i for i in range(len(x)) if x[i][f] <= thr]
            right = [i for i in range(len(x)) if x[i][f] > thr]
            if len(left) < min_leaf or len(right) < min_leaf:
                continue
            yl = [y[i] for i in left]
            yr = [y[i] for i in right]
            gain = parent - (len(yl) * _gini(yl) + len(yr) * _gini(yr)) / len(y)
            if best is None or gain > best[0]:
                best = (gain, f, thr, left, right)
    if best is None or best[0] <= 1e-9:
        return node
    _, f, thr, left, right = best
    node.feat, node.thr = f, thr
    node.left = build_tree(
        [x[i] for i in left], [y[i] for i in left], depth + 1, max_depth, min_leaf
    )
    node.right = build_tree(
        [x[i] for i in right], [y[i] for i in right], depth + 1, max_depth, min_leaf
    )
    return node


def tree_predict(node: _Node, xi: tuple[float, ...]) -> float:
    while node.feat is not None:
        node = node.left if xi[node.feat] <= node.thr else node.right  # type: ignore[assignment]
    return node.pred


# ── LOO evaluators ────────────────────────────────────────────────────────────


def loo_logistic(rows, y, cols) -> tuple[int, int]:
    """Leave-one-out accuracy of the k-feature logistic on the given columns."""
    feats = [tuple(r[c] for c in cols) for r in rows]
    n = len(feats)
    correct = 0
    for i in range(n):
        tr = [feats[j] for j in range(n) if j != i]
        ty = [y[j] for j in range(n) if j != i]
        m = sc.fit(tr, ty)
        correct += (m.p_day(feats[i]) > 0.5) == (y[i] == 1)
    return correct, n


def loo_tree(rows, y, cols, max_depth=3, min_leaf=5) -> tuple[int, int, list[int]]:
    """LOO accuracy of the shallow tree; also returns the root-split feature per fold."""
    feats = [tuple(r[c] for c in cols) for r in rows]
    n = len(feats)
    correct = 0
    roots: list[int] = []
    for i in range(n):
        tr = [feats[j] for j in range(n) if j != i]
        ty = [y[j] for j in range(n) if j != i]
        root = build_tree(tr, ty, 0, max_depth, min_leaf)
        roots.append(cols[root.feat] if root.feat is not None else -1)
        correct += (tree_predict(root, feats[i]) > 0.5) == (y[i] == 1)
    return correct, n, roots


def try_sklearn_loo(rows, y, cols):
    """LOO for GBM + RF if sklearn is installed, else None."""
    try:
        from sklearn.ensemble import (
            GradientBoostingClassifier,
            RandomForestClassifier,
        )
    except ImportError:
        return None
    import numpy as np

    x = np.array([[r[c] for c in cols] for r in rows])
    yy = np.array(y)
    n = len(y)
    out = {}
    for name, mk in [
        ("gbm", lambda: GradientBoostingClassifier(max_depth=2, n_estimators=60)),
        ("rf", lambda: RandomForestClassifier(max_depth=3, n_estimators=200)),
    ]:
        c = 0
        for i in range(n):
            mask = np.arange(n) != i
            clf = mk().fit(x[mask], yy[mask])
            c += int(clf.predict(x[i : i + 1])[0] == yy[i])
        out[name] = (c, n)
    return out


def _line(label: str, c: int, n: int, majority: float) -> str:
    lo, hi = wilson_ci(c, n)
    gate = "GO " if (c / n >= 0.65 and lo > majority) else "   "
    return f"  {gate}{label:32} {c}/{n} = {c / n:5.1%}   CI=[{lo:.0%},{hi:.0%}]"


def main() -> int:
    corpus = load_corpus()
    print(f"building features for {len(corpus)} people (full recompute)…", flush=True)
    rows, y = build_features(corpus)
    n = len(y)
    n_day = sum(y)
    majority = max(n_day, n - n_day) / n

    # ---- feature diagnostics -------------------------------------------------
    print("\n" + "=" * 68)
    print("FEATURE CORRELATIONS WITH SECT (day=1)")
    print("=" * 68)
    for f, name in enumerate(FEATURE_NAMES):
        xs = [r[f] for r in rows]
        print(f"  {name:16} corr = {corr(xs, [float(v) for v in y]):+.3f}")

    # the decisive number for the NEW feature: does malefic-of-temperament add
    # signal beyond the two validated features (daylight + malefic-event)?
    ctrl = [[r[0] for r in rows], [r[1] for r in rows]]
    rt = resid([r[2] for r in rows], ctrl)
    ry = resid([float(v) for v in y], ctrl)
    print(
        f"\n  partial corr(malefic_temper, sect | daylight, malefic_event) = "
        f"{corr(rt, ry):+.3f}"
    )
    print("    ^ NEW feature's independent contribution (the mom tie-breaker)")

    # ---- LOO model comparison ------------------------------------------------
    print("\n" + "=" * 68)
    print(f"LEAVE-ONE-OUT ACCURACY   (n={n}, day={n_day}, majority={majority:.1%})")
    print("=" * 68)

    baselines = [
        ("majority class", int(round(majority * n)), n),
    ]
    for label, c, nn in baselines:
        print(_line(label, c, nn, majority))

    # single & pair logistic baselines
    c, _ = loo_logistic(rows, y, [0])
    print(_line("logistic: daylight only", c, n, majority))
    c, _ = loo_logistic(rows, y, [0, 1])
    print(_line("logistic: daylight+malefic  [validated]", c, n, majority))

    # the NEW feature stacked on the validated pair
    c, _ = loo_logistic(rows, y, [0, 1, 2])
    print(_line("logistic: +malefic_temper (NEW)", c, n, majority))

    # full compare-hypothesis feature set
    all_cols = list(range(len(FEATURE_NAMES)))
    c, _ = loo_logistic(rows, y, all_cols)
    print(_line("logistic: ALL 6 features", c, n, majority))

    c, _, roots = loo_tree(rows, y, all_cols)
    print(_line("tree(d3): ALL 6 features", c, n, majority))
    root_counts = {
        FEATURE_NAMES[r] if r >= 0 else "(stump)": roots.count(r) for r in set(roots)
    }
    top = sorted(root_counts.items(), key=lambda kv: -kv[1])
    print(
        "      tree root-split across folds: " + ", ".join(f"{k}×{v}" for k, v in top)
    )

    sk = try_sklearn_loo(rows, y, all_cols)
    if sk:
        for name, (c, nn) in sk.items():
            print(_line(f"sklearn {name}: ALL 6 features", c, nn, majority))
    else:
        print("  (sklearn not installed — skipped GBM/RF; tree+logistic answer it)")

    print(
        "\nread: does any combination clear the validated daylight+malefic bar,\n"
        "and does the NEW malefic-temperament feature earn its place?"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
