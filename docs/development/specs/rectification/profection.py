"""Annual-profection activation for the time-posterior (Phase A1).

Whole-sign annual profection: at age N the profected sign is N signs from the
natal Ascendant, and the **year-lord** is that sign's traditional ruler. So the
year-lord sequence depends on the **rising sign** — sweeping the birth time moves
the Ascendant and re-shuffles the lords, and the events can discriminate the time
(unlike firdaria, which was ~time-independent).

Per candidate we score, de-confounded against a per-person permutation null (the
firdaria lesson), how well the profected year-lords match the events' natural
significators. Scores are cached per rising sign (only 12 distinct values).
"""

from __future__ import annotations

import random
from collections.abc import Callable

from models import CorpusPerson
from significators import planet_significance

SIGN_ORDER = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)
DOMICILE_RULER = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}
N_PERMUTATIONS = 200
SEED = 7


def year_lord(rising_sign: str, age: int) -> str:
    """Whole-sign profected year-lord: ruler of the sign `age` places from ASC."""
    idx = (SIGN_ORDER.index(rising_sign) + age) % 12
    return DOMICILE_RULER[SIGN_ORDER[idx]]


def _events_ages(person: CorpusPerson) -> list[tuple[str, str, int]]:
    """(type, significance, completed-age-at-event) for post-birth events."""
    by, bm, bd = (int(x) for x in person.birth_data.date.split("-"))
    out = []
    for e in person.events:
        ed = e.representative_date
        age = ed.year - by - (1 if (ed.month, ed.day) < (bm, bd) else 0)
        if age >= 0:
            out.append((e.type, e.significance, age))
    return out


def make_profection_scorer(
    person: CorpusPerson,
) -> Callable[[CorpusPerson, object], float]:
    """A score_fn(person, chart) -> de-confounded profection log-likelihood.

    Caches by rising sign (the only thing that varies across candidates)."""
    items = _events_ages(person)
    type_sig = [(t, sg) for t, sg, _ in items]
    ages = [a for _, _, a in items]
    cache: dict[str, float] = {}

    def score(_p: CorpusPerson, chart: object) -> float:
        rising = chart.get_object("ASC").sign
        if rising not in cache:
            lords = [year_lord(rising, a) for a in ages]

            def total(seq: list[tuple[str, str]]) -> float:
                return sum(
                    SIGNIFICANCE_WEIGHT.get(sg, 0.5) * planet_significance(t, lo)
                    for (t, sg), lo in zip(seq, lords, strict=True)
                )

            raw = total(type_sig)
            rng = random.Random(SEED)
            perm = list(type_sig)
            null = 0.0
            for _ in range(N_PERMUTATIONS):
                rng.shuffle(perm)
                null += total(perm)
            cache[rising] = raw - null / N_PERMUTATIONS
        return cache[rising]

    return score
