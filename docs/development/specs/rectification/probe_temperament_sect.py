#!/usr/bin/env python3
"""Probe: does a sect-light temperament signal ADD to the daylight+malefic classifier?

Sect-light doctrine: the luminary of the sect leads the character — day charts are
Sun-led (willful, proud, authoritative, visible), night charts Moon-led (receptive,
private, adaptive, emotional). Signal: Solar-flavoured temperament -> day,
Lunar-flavoured -> night. Keywords a priori from Sun/Moon significations.

The decisive question is not corr(temperament, sect) but whether temperament adds
independent value after controlling for daylight + malefic (partial corr; 3-feature
LOO vs 2-feature LOO).
"""

from __future__ import annotations

import statistics

import harness
import sect_classifier as sc
import sect_signals as sig
from models import load_corpus
from run_benchmark import wilson_ci

SOLAR_WORDS = (
    "proud",
    "pride",
    "ambitious",
    "ambition",
    "authoritative",
    "authority",
    "dominant",
    "domineering",
    "commanding",
    "willful",
    "strong-willed",
    "confident",
    "self-assured",
    "leader",
    "leadership",
    "ego",
    "bold",
    "assertive",
    "magnanimous",
    "charismatic",
    "driven",
    "forceful",
    "imperious",
    "grandiose",
    "vain",
    "flamboyant",
    "regal",
    "self-confident",
)
LUNAR_WORDS = (
    "private",
    "reserved",
    "receptive",
    "nurturing",
    "caring",
    "moody",
    "moody",
    "sensitive",
    "emotional",
    "adaptable",
    "adaptive",
    "retiring",
    "shy",
    "introverted",
    "gentle",
    "empathetic",
    "empathic",
    "changeable",
    "insecure",
    "withdrawn",
    "melancholic",
    "melancholy",
    "quiet",
    "tender",
    "domestic",
    "vulnerable",
    "fluid",
    "self-effacing",
    "humble",
)


def temperament_signal(person) -> float:
    """Solar − Lunar over the person's temperament (day-positive)."""
    solar = lunar = 0.0
    for tr in person.temperament:
        text = (tr.trait + " " + " ".join(tr.tags)).lower()
        solar += sum(w in text for w in SOLAR_WORDS)
        lunar += sum(w in text for w in LUNAR_WORDS)
    return solar - lunar


def corr(xs, ys):
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / n
    return cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)


def _resid(target, controls):
    """Residual of target after OLS on controls (+intercept), pure python (normal eqs)."""
    import numpy as np

    x = np.array([[1.0, *c] for c in zip(*controls, strict=True)])
    y = np.array(target)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return (y - x @ beta).tolist()


def main() -> int:
    corpus = load_corpus()
    daylight = [sc.features(p)[0] for p in corpus]
    malefic = [sig.sect_score(p, use_benefic=False) for p in corpus]
    temper = [temperament_signal(p) for p in corpus]
    y = [1 if harness.true_sect(p) == "day" else 0 for p in corpus]

    print("correlations with sect:")
    print(f"  daylight    {corr(daylight, y):+.3f}")
    print(f"  malefic     {corr(malefic, y):+.3f}")
    print(f"  temperament {corr(temper, y):+.3f}")
    print(f"\nredundancy — corr(temperament, malefic) = {corr(temper, malefic):+.3f}")

    # partial corr(temperament, sect | daylight, malefic)
    rt = _resid(temper, [daylight, malefic])
    ry = _resid([float(v) for v in y], [daylight, malefic])
    print(f"partial corr(temperament, sect | daylight, malefic) = {corr(rt, ry):+.3f}")
    print("  ^ the decisive number: does temperament add independent signal?")

    # 2-feature vs 3-feature LOO
    def loo(features):
        n = len(features)
        c = 0
        for i in range(n):
            tr = [features[j] for j in range(n) if j != i]
            ty = [y[j] for j in range(n) if j != i]
            m = sc.fit(tr, ty)
            c += (m.p_day(features[i]) > 0.5) == (y[i] == 1)
        return c, n

    f2 = list(zip(daylight, malefic, strict=True))
    f3 = list(zip(daylight, malefic, temper, strict=True))
    c2, n = loo(f2)
    c3, _ = loo(f3)
    lo2, hi2 = wilson_ci(c2, n)
    lo3, hi3 = wilson_ci(c3, n)
    print("\nLOO-CV accuracy:")
    print(
        f"  daylight+malefic            = {c2}/{n} = {c2 / n:.1%}  CI=[{lo2:.1%},{hi2:.1%}]"
    )
    print(
        f"  daylight+malefic+temperament = {c3}/{n} = {c3 / n:.1%}  CI=[{lo3:.1%},{hi3:.1%}]"
    )
    print("\n-> add temperament?" + (" YES" if c3 > c2 else " no (no LOO gain)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
