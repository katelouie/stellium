"""Primary-direction activation for the time-posterior (Phase A2).

The sharp technique. For a chart cast at candidate time `t`, direct each of the
seven planets to the four angles (solar-arc-style, via stellium's
`DirectionsEngine`). A directed hit lands at a specific **age**, and that age
depends on the angle positions — which move ~360°/day — so sweeping `t` moves
every hit. Signal: at the true time, hits whose **promissor signifies an event**
fall **near that event's age**; at wrong times they scatter.

Per candidate we score, de-confounded against a per-person type-shuffle null,
Σ_events (significance × best nearby significator-matching directed hit). Memoised
so the null is cheap. Unlike profection this depends on the *whole* chart (angles),
so it is recomputed per candidate — no rising-sign caching.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from datetime import date

from models import CorpusPerson
from significators import PLANET_SIGNIFICATORS, planet_significance

from stellium.engines.directions import DirectionsEngine

PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
ALL_TYPES = tuple(PLANET_SIGNIFICATORS)  # the full event taxonomy
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}
ORB_YEARS = 1.5  # a directed hit "activates" an event within ±this many years
N_PERMUTATIONS = 150
SEED = 11


def _directed_hits(chart) -> list[tuple[float, str]]:
    """(age, promissor-planet) for in-lifespan directed hits of planets to angles."""
    eng = DirectionsEngine(chart, method="zodiacal", time_key="naibod")
    out: list[tuple[float, str]] = []
    for planet in PLANETS:
        try:
            to_angles = eng.direct_to_angles(planet)
        except Exception:
            continue
        for res in to_angles.values():
            if res.age is not None and 0.0 <= res.age <= 95.0:
                out.append((res.age, planet))
    return out


def _events(person: CorpusPerson) -> list[tuple[str, str, float]]:
    """(type, significance, fractional-age-at-event) for post-birth events."""
    by, bm, bd = (int(x) for x in person.birth_data.date.split("-"))
    birth = date(by, bm, bd)
    out = []
    for e in person.events:
        age = (e.representative_date - birth).days / 365.25
        if age >= 0:
            out.append((e.type, e.significance, age))
    return out


def make_directions_scorer(
    person: CorpusPerson,
) -> Callable[[CorpusPerson, object], float]:
    items = _events(person)
    types = [t for t, _, _ in items]
    sig_w = [SIGNIFICANCE_WEIGHT.get(sg, 0.5) for _, sg, _ in items]
    ages = [a for _, _, a in items]

    def score(_p: CorpusPerson, chart: object) -> float:
        hits = _directed_hits(chart)

        def best_fit(event_type: str, age: float) -> float:
            best = 0.0
            for hit_age, promissor in hits:
                d = abs(hit_age - age)
                if d < ORB_YEARS:
                    v = planet_significance(event_type, promissor) * (1 - d / ORB_YEARS)
                    if v > best:
                        best = v
            return best

        # memoise best_fit(type, age_i) over the whole taxonomy, once per candidate
        fmaps = [{tp: best_fit(tp, age) for tp in ALL_TYPES} for age in ages]

        def total(assigned: list[str]) -> float:
            return sum(sig_w[i] * fmaps[i][assigned[i]] for i in range(len(items)))

        raw = total(types)
        rng = random.Random(SEED)
        perm = list(types)
        null = 0.0
        for _ in range(N_PERMUTATIONS):
            rng.shuffle(perm)
            null += total(perm)
        return raw - null / N_PERMUTATIONS

    return score
