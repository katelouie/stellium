#!/usr/bin/env python3
"""Probe: do natal planetary dignities add sect signal (new channel), and does
dignity-weighting sharpen the malefic signal that already works?

Two tests, both nearly time-independent (planet signs are ~fixed across a day):

1. **Dignity sect-balance** — sect-rejoicing intuition: are the DIURNAL planets
   (Sun/Jupiter/Saturn) better-dignified than the NOCTURNAL ones
   (Moon/Venus/Mars)? balance>0 -> day. (Theoretically weak: sect is a horizon
   fact, ~orthogonal to sign placements — but cheap and untested.)
2. **Dignity-weighted malefic** — weight the malefic-of-sect event signal by the
   natal condition of Mars vs Saturn (does a debilitated/strong contrary-sect
   malefic matter?). Enriches the signal that works rather than a new channel.

Decisive test: partial corr | daylight, malefic, and 3-feature LOO vs 2-feature.
"""

from __future__ import annotations

import statistics

import harness
import sect_classifier as sc
import sect_signals as sig
from models import load_corpus
from profection import DOMICILE_RULER, SIGN_ORDER
from run_benchmark import wilson_ci

EXALT_SIGN = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mercury": "Virgo",
    "Venus": "Pisces",
    "Mars": "Capricorn",
    "Jupiter": "Cancer",
    "Saturn": "Libra",
}
DIURNAL = ("Sun", "Jupiter", "Saturn")
NOCTURNAL = ("Moon", "Venus", "Mars")


def _opposite(sign: str) -> str:
    return SIGN_ORDER[(SIGN_ORDER.index(sign) + 6) % 12]


def essential_dignity(planet: str, sign: str) -> int:
    """Coarse Ptolemaic essential dignity by sign (domicile/exalt/detriment/fall)."""
    if DOMICILE_RULER[sign] == planet:
        return 5
    if EXALT_SIGN.get(planet) == sign:
        return 4
    if DOMICILE_RULER[_opposite(sign)] == planet:  # detriment
        return -5
    if EXALT_SIGN.get(planet) == _opposite(sign):  # fall
        return -4
    return 0


def _planet_signs(person) -> dict[str, str]:
    chart = harness.build_chart(person.birth_data, (12, 0))  # noon; signs ~time-indep
    return {p: chart.get_object(p).sign for p in DIURNAL + NOCTURNAL}


def dignity_balance(person) -> float:
    signs = _planet_signs(person)
    diurnal = sum(essential_dignity(p, signs[p]) for p in DIURNAL)
    nocturnal = sum(essential_dignity(p, signs[p]) for p in NOCTURNAL)
    return float(diurnal - nocturnal)


def malefic_dignity_weighted(person) -> float:
    """Malefic-of-sect signal, each side scaled by that malefic's natal condition.

    A *debilitated* malefic is the more destructive, so scale Mars-hardship by
    (1 - mars_dignity/5) and Saturn-hardship likewise — down-weighting hardship
    when the malefic is dignified.
    """
    signs = _planet_signs(person)
    mars_w = 1.0 - essential_dignity("Mars", signs["Mars"]) / 10.0
    sat_w = 1.0 - essential_dignity("Saturn", signs["Saturn"]) / 10.0
    mars, saturn = sig.malefic_tally(person)
    return mars_w * mars - sat_w * saturn


def corr(xs, ys):
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / n
    return cov / (statistics.pstdev(xs) * statistics.pstdev(ys) + 1e-12)


def _resid(target, controls):
    import numpy as np

    x = np.array([[1.0, *c] for c in zip(*controls, strict=True)])
    y = np.array(target)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return (y - x @ beta).tolist()


def loo(features, y):
    n = len(features)
    c = 0
    for i in range(n):
        tr = [features[j] for j in range(n) if j != i]
        ty = [y[j] for j in range(n) if j != i]
        m = sc.fit(tr, ty)
        c += (m.p_day(features[i]) > 0.5) == (y[i] == 1)
    return c, n


def main() -> int:
    corpus = load_corpus()
    daylight = [sc.features(p)[0] for p in corpus]
    malefic = [sig.sect_score(p, use_benefic=False) for p in corpus]
    dignity = [dignity_balance(p) for p in corpus]
    mal_dw = [malefic_dignity_weighted(p) for p in corpus]
    y = [1 if harness.true_sect(p) == "day" else 0 for p in corpus]
    yf = [float(v) for v in y]

    print("correlations with sect:")
    print(f"  daylight            {corr(daylight, y):+.3f}")
    print(f"  malefic (plain)     {corr(malefic, y):+.3f}")
    print(f"  dignity-balance     {corr(dignity, y):+.3f}")
    print(f"  malefic dignity-wtd {corr(mal_dw, y):+.3f}")

    pd = corr(_resid(dignity, [daylight, malefic]), _resid(yf, [daylight, malefic]))
    print(f"\npartial corr(dignity-balance, sect | daylight, malefic) = {pd:+.3f}")

    c2, n = loo(list(zip(daylight, malefic, strict=True)), y)
    c3, _ = loo(list(zip(daylight, malefic, dignity, strict=True)), y)
    # dignity-weighted malefic *replacing* plain malefic
    cdw, _ = loo(list(zip(daylight, mal_dw, strict=True)), y)
    lo2, _ = wilson_ci(c2, n)
    print("\nLOO-CV accuracy:")
    print(f"  daylight + malefic                 = {c2 / n:.1%}  ({c2}/{n})")
    print(f"  daylight + malefic + dignity       = {c3 / n:.1%}  ({c3}/{n})")
    print(f"  daylight + malefic(dignity-weighted)= {cdw / n:.1%}  ({cdw}/{n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
