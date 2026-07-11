"""Time-discriminating timing techniques for the convergence matrix (exploratory).

These are the whisper-level methods from the study — solar-arc/primary directions,
transiting chronocrators to the angles, annual profection, and the secondary
progressed Moon. Each scores how well a candidate chart's *time-dependent* structure
fits the known events, de-confounded against a per-person event-type shuffle. On
their own they are near-null (truth at only the ~55–59th percentile) and blind
combination *cancels* them; they are here to be **displayed**, never summed.

All operate on a package ``CalculatedChart`` + a sequence of
:class:`~stellium.data.LifeEvent`.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from datetime import date, datetime

from stellium.core.models import CalculatedChart
from stellium.rectification._data import (
    ALL_EVENT_TYPES,
    DOMICILE_RULER,
    SIGN_ORDER,
    SIGNIFICANCE_WEIGHT,
    planet_significance,
)
from stellium.rectification._recast import local_birth_date, require_obj

_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")


def _ages(events: Sequence, birth: date) -> list[float]:
    return [(e.representative_date - birth).days / 365.25 for e in events]


def _deconfound(
    raw_total: Callable[[list[str]], float],
    types: list[str],
    seed: int,
    n_perm: int = 150,
) -> float:
    """raw − mean(shuffled) using the given total(assigned) closure."""
    rng = random.Random(seed)
    perm = list(types)
    null = 0.0
    for _ in range(n_perm):
        rng.shuffle(perm)
        null += raw_total(perm)
    return raw_total(types) - null / n_perm


# ── solar-arc / primary directions to the angles ──────────────────────────────

_DIR_ORB_YEARS = 1.5


def _directed_hits(chart: CalculatedChart) -> list[tuple[float, str]]:
    from stellium.engines.directions import DirectionsEngine

    eng = DirectionsEngine(chart, method="zodiacal", time_key="naibod")
    out: list[tuple[float, str]] = []
    for planet in _PLANETS:
        try:
            to_angles = eng.direct_to_angles(planet)
        except Exception:
            continue
        for res in to_angles.values():
            if res.age is not None and 0.0 <= res.age <= 95.0:
                out.append((res.age, planet))
    return out


def make_directions_scorer(
    events: Sequence, birth: date
) -> Callable[[CalculatedChart], float]:
    ages = _ages(events, birth)
    idx = [i for i, a in enumerate(ages) if a >= 0]
    types = [events[i].type for i in idx]
    sig_w = [SIGNIFICANCE_WEIGHT.get(events[i].significance, 0.5) for i in idx]
    evt_ages = [ages[i] for i in idx]

    def score(chart: CalculatedChart) -> float:
        hits = _directed_hits(chart)

        def best_fit(etype: str, age: float) -> float:
            best = 0.0
            for hit_age, promissor in hits:
                d = abs(hit_age - age)
                if d < _DIR_ORB_YEARS:
                    v = planet_significance(etype, promissor) * (1 - d / _DIR_ORB_YEARS)
                    best = max(best, v)
            return best

        fmaps = [{tp: best_fit(tp, a) for tp in ALL_EVENT_TYPES} for a in evt_ages]

        def total(assigned: list[str]) -> float:
            return sum(sig_w[i] * fmaps[i][assigned[i]] for i in range(len(idx)))

        return _deconfound(total, types, seed=11)

    return score


def directions_hooks(chart: CalculatedChart, events: Sequence, birth: date) -> set[int]:
    hits = _directed_hits(chart)
    hooked: set[int] = set()
    for i, e in enumerate(events):
        age = (e.representative_date - birth).days / 365.25
        if age < 0:
            continue
        for hit_age, promissor in hits:
            if (
                abs(hit_age - age) < _DIR_ORB_YEARS
                and planet_significance(e.type, promissor) > 0
            ):
                hooked.add(i)
                break
    return hooked


# ── transiting chronocrators (Saturn, Jupiter) to the natal angles ────────────

_TRANSITERS = ("Saturn", "Jupiter")
_TR_ASPECTS = (0.0, 90.0, 180.0)
_TR_ORB = 3.0


def _sep(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _aspect_closeness(t: float, angle: float) -> float:
    best = 0.0
    sep = _sep(t, angle)
    for asp in _TR_ASPECTS:
        d = abs(sep - asp)
        if d < _TR_ORB:
            best = max(best, 1.0 - d / _TR_ORB)
    return best


def transiter_positions(
    events: Sequence, chart: CalculatedChart
) -> dict[int, dict[str, float]]:
    from stellium.core.builder import ChartBuilder
    from stellium.core.native import Native

    loc = chart.location
    out: dict[int, dict[str, float]] = {}
    for i, e in enumerate(events):
        d = e.representative_date
        nat = Native(
            f"{d.year:04d}-{d.month:02d}-{d.day:02d} 12:00:00",
            {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "timezone": loc.timezone,
            },
        )
        tc = ChartBuilder.from_native(nat).calculate()
        out[i] = {p: require_obj(tc, p).longitude for p in _TRANSITERS}
    return out


def make_transits_scorer(
    events: Sequence, tpos: dict[int, dict[str, float]]
) -> Callable[[CalculatedChart], float]:
    types = [e.type for e in events]
    sig_w = [SIGNIFICANCE_WEIGHT.get(e.significance, 0.5) for e in events]

    def score(chart: CalculatedChart) -> float:
        asc = require_obj(chart, "ASC").longitude
        mc = require_obj(chart, "MC").longitude

        def fit_for(i: int, etype: str) -> float:
            best = 0.0
            for pl, lon in tpos[i].items():
                sigv = planet_significance(etype, pl)
                if sigv <= 0:
                    continue
                close = max(_aspect_closeness(lon, asc), _aspect_closeness(lon, mc))
                best = max(best, sigv * close)
            return best

        fmaps = [
            {tp: fit_for(i, tp) for tp in ALL_EVENT_TYPES} for i in range(len(events))
        ]

        def total(assigned: list[str]) -> float:
            return sum(sig_w[i] * fmaps[i][assigned[i]] for i in range(len(events)))

        return _deconfound(total, types, seed=13)

    return score


def transits_hooks(
    chart: CalculatedChart, events: Sequence, tpos: dict[int, dict[str, float]]
) -> set[int]:
    asc = require_obj(chart, "ASC").longitude
    mc = require_obj(chart, "MC").longitude
    hooked: set[int] = set()
    for i, e in enumerate(events):
        for pl, lon in tpos[i].items():
            if planet_significance(e.type, pl) <= 0:
                continue
            if max(_aspect_closeness(lon, asc), _aspect_closeness(lon, mc)) > 0:
                hooked.add(i)
                break
    return hooked


# ── annual profection (Ascendant-driven, time-discriminating) ─────────────────


def year_lord(rising_sign: str, age: int) -> str:
    idx = (SIGN_ORDER.index(rising_sign) + age) % 12
    return DOMICILE_RULER[SIGN_ORDER[idx]]


def make_profection_scorer(
    events: Sequence, birth: date
) -> Callable[[CalculatedChart], float]:
    ages = _ages(events, birth)
    idx = [i for i, a in enumerate(ages) if a >= 0]
    types = [events[i].type for i in idx]
    sig_w = [SIGNIFICANCE_WEIGHT.get(events[i].significance, 0.5) for i in idx]
    int_ages = [int(ages[i]) for i in idx]
    cache: dict[str, float] = {}

    def score(chart: CalculatedChart) -> float:
        rising = require_obj(chart, "ASC").sign
        if rising in cache:
            return cache[rising]
        lords = [year_lord(rising, a) for a in int_ages]

        def total(assigned: list[str]) -> float:
            return sum(
                sig_w[i] * planet_significance(assigned[i], lords[i])
                for i in range(len(idx))
            )

        cache[rising] = _deconfound(total, types, seed=7)
        return cache[rising]

    return score


# ── secondary progressed Moon (near time-independent reference) ───────────────

_PM_ASPECTS = (0.0, 60.0, 90.0, 120.0, 180.0)
_PM_ORB = 1.5


def _pm_close(a: float, b: float) -> float:
    best = 0.0
    sep = _sep(a, b)
    for asp in _PM_ASPECTS:
        d = abs(sep - asp)
        if d < _PM_ORB:
            best = max(best, 1.0 - d / _PM_ORB)
    return best


def progressed_moon_signal(chart: CalculatedChart, events: Sequence) -> float:
    from stellium.core.builder import ChartBuilder
    from stellium.core.native import Native
    from stellium.rectification._recast import recast
    from stellium.utils.progressions import calculate_progressed_datetime

    birth = local_birth_date(chart)
    natal_dt = datetime(birth.year, birth.month, birth.day, 12, 0)
    natal = recast(chart, 12, 0)
    natal_lon = {p: require_obj(natal, p).longitude for p in _PLANETS}
    loc = chart.location

    prog_moon: list[float] = []
    for e in events:
        d = e.representative_date
        pdt = calculate_progressed_datetime(
            natal_dt, datetime(d.year, d.month, d.day, 12, 0), "secondary"
        )
        nat = Native(
            pdt.strftime("%Y-%m-%d %H:%M:%S"),
            {
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "timezone": loc.timezone,
            },
        )
        pchart = ChartBuilder.from_native(nat).calculate()
        prog_moon.append(require_obj(pchart, "Moon").longitude)

    types = [e.type for e in events]
    sig_w = [SIGNIFICANCE_WEIGHT.get(e.significance, 0.5) for e in events]

    def fit_for(i: int, etype: str) -> float:
        best = 0.0
        for pl in _PLANETS:
            sigv = planet_significance(etype, pl)
            if sigv <= 0:
                continue
            best = max(best, sigv * _pm_close(prog_moon[i], natal_lon[pl]))
        return best

    fmaps = [{tp: fit_for(i, tp) for tp in ALL_EVENT_TYPES} for i in range(len(events))]

    def total(assigned: list[str]) -> float:
        return sum(sig_w[i] * fmaps[i][assigned[i]] for i in range(len(events)))

    return _deconfound(total, types, seed=17)
