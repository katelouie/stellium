"""Transiting chronocrators (Saturn, Jupiter) to the natal angles — a
time-sensitive timing method for the convergence workbench.

Traditional practice reads transits of the *greater* chronocrators (Saturn, then
Jupiter) across the angles as markers of major turning points. The natal **angles**
move ~360°/day, so *which candidate birth time* places an angle under a transiting
Saturn/Jupiter at a known event's date is genuinely discriminating — unlike the
planets, whose transiting positions at the event date don't move with birth time.

We restrict to Saturn + Jupiter deliberately: they are slow enough that a
year-precision event still pins the transit to a few degrees, and they are the only
outer transiters with entries in our (traditional) significator table. Scored and
de-confounded against a per-person event-type shuffle, exactly like ``directions``.
"""

from __future__ import annotations

import random
from collections.abc import Callable

from models import CorpusPerson
from significators import PLANET_SIGNIFICATORS, planet_significance

from stellium import ChartBuilder, Native

TRANSITERS = ("Saturn", "Jupiter")
ASPECTS = (0.0, 90.0, 180.0)  # conjunction, square, opposition (the hard hits)
ORB = 3.0
ALL_TYPES = tuple(PLANET_SIGNIFICATORS)
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}
N_PERMUTATIONS = 150
SEED = 13


def _sep(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _aspect_closeness(transit_lon: float, angle_lon: float) -> float:
    """Closeness in (0, 1] to the nearest hard aspect within orb, else 0."""
    best = 0.0
    sep = _sep(transit_lon, angle_lon)
    for asp in ASPECTS:
        d = abs(sep - asp)
        if d < ORB:
            best = max(best, 1.0 - d / ORB)
    return best


def transiter_positions(person: CorpusPerson) -> dict[int, dict[str, float]]:
    """{event_index: {planet: transiting longitude}} at each event's date (noon)."""
    bd = person.birth_data
    out: dict[int, dict[str, float]] = {}
    for i, e in enumerate(person.events):
        d = e.representative_date
        nat = Native(
            f"{d.year:04d}-{d.month:02d}-{d.day:02d} 12:00:00",
            {
                "latitude": bd.latitude,
                "longitude": bd.longitude,
                "timezone": bd.timezone,
            },
        )
        tc = ChartBuilder.from_native(nat).calculate()
        out[i] = {p: tc.get_object(p).longitude for p in TRANSITERS}
    return out


def make_transits_scorer(
    person: CorpusPerson,
) -> Callable[[CorpusPerson, object], float]:
    events = list(person.events)
    types = [e.type for e in events]
    sig_w = [SIGNIFICANCE_WEIGHT.get(e.significance, 0.5) for e in events]
    tpos = transiter_positions(person)  # fixed — independent of birth time

    def score(_p: CorpusPerson, chart: object) -> float:
        asc = chart.get_object("ASC").longitude
        mc = chart.get_object("MC").longitude

        def fit_for(i: int, event_type: str) -> float:
            best = 0.0
            for pl, lon in tpos[i].items():
                sigv = planet_significance(event_type, pl)
                if sigv <= 0:
                    continue
                close = max(_aspect_closeness(lon, asc), _aspect_closeness(lon, mc))
                best = max(best, sigv * close)
            return best

        fmaps = [{tp: fit_for(i, tp) for tp in ALL_TYPES} for i in range(len(events))]

        def total(assigned: list[str]) -> float:
            return sum(sig_w[i] * fmaps[i][assigned[i]] for i in range(len(events)))

        raw = total(types)
        rng = random.Random(SEED)
        perm = list(types)
        null = 0.0
        for _ in range(N_PERMUTATIONS):
            rng.shuffle(perm)
            null += total(perm)
        return raw - null / N_PERMUTATIONS

    return score


def event_hooks(
    person: CorpusPerson, chart: object, tpos: dict[int, dict[str, float]] | None = None
) -> list[int]:
    """Indices of events with an apt Saturn/Jupiter-to-angle transit at this chart.

    Pass a precomputed ``tpos`` (from :func:`transiter_positions`) to avoid
    rebuilding the event charts on every candidate in a sweep.
    """
    asc = chart.get_object("ASC").longitude
    mc = chart.get_object("MC").longitude
    if tpos is None:
        tpos = transiter_positions(person)
    hooked: list[int] = []
    for i, e in enumerate(person.events):
        for pl, lon in tpos[i].items():
            if planet_significance(e.type, pl) <= 0:
                continue
            if max(_aspect_closeness(lon, asc), _aspect_closeness(lon, mc)) > 0:
                hooked.append(i)
                break
    return hooked
