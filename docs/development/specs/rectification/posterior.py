"""Technique-agnostic time-posterior pipeline (Phase A).

Sweep candidate birth times across the day; for each, cast the chart (full
recompute) and ask a technique's ``score_fn`` how well that candidate's timing
lights the person's events; normalise to a posterior over `t`; read **sect as the
marginal** (P(day) = Σ posterior over day-cells, sect computed per candidate).

The technique (profection, directions, …) owns its own scoring + de-confounding
and hands back one de-confounded log-likelihood per candidate. This module only
does the grid, the normalisation, and the marginal.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import harness
from models import CorpusPerson


@dataclass(frozen=True)
class Candidate:
    minute_of_day: int
    sect: str  # "day" | "night" (computed per candidate)
    rising_sign: str
    log_like: float  # de-confounded technique score
    prob: float  # normalised posterior mass


@dataclass(frozen=True)
class TimePosterior:
    person: str
    candidates: tuple[Candidate, ...]
    p_day: float
    p_night: float
    map_minute: int  # posterior-mode minute-of-day
    map_rising_sign: str


# score_fn(person, chart) -> de-confounded log-likelihood for this candidate.
ScoreFn = Callable[[CorpusPerson, object], float]


def build_posterior(
    person: CorpusPerson,
    score_fn: ScoreFn,
    *,
    step_minutes: int = 20,
    temperature: float = 1.0,
) -> TimePosterior:
    raw: list[tuple[int, str, str, float]] = []
    for minute in range(0, 24 * 60, step_minutes):
        chart = harness.build_chart(person.birth_data, divmod(minute, 60))
        asc = chart.get_object("ASC")
        raw.append((minute, chart.sect, asc.sign, score_fn(person, chart)))

    lls = [ll for *_, ll in raw]
    m = max(lls)
    weights = [math.exp((ll - m) / temperature) for ll in lls]
    z = sum(weights) or 1.0

    cands = tuple(
        Candidate(minute, sect, sign, ll, w / z)
        for (minute, sect, sign, ll), w in zip(raw, weights, strict=True)
    )
    p_day = sum(c.prob for c in cands if c.sect == "day")
    mode = max(cands, key=lambda c: c.prob)
    return TimePosterior(
        person=person.name,
        candidates=cands,
        p_day=p_day,
        p_night=1.0 - p_day,
        map_minute=mode.minute_of_day,
        map_rising_sign=mode.rising_sign,
    )
