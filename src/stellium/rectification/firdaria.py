"""Firdaria event-timing convergence — a de-confounded day-vs-night signal.

For each dated event, find the active firdaria time-lord under the **day** and
**night** orderings and score how aptly that lord signifies the event. Because the
night ordering front-loads the generically-significant planets in the event-dense
early decades, raw sums are confounded; we subtract a per-person permutation null
(shuffle the event types onto the same lord sequence) so only a genuine
type↔lord alignment survives. The excess of day-fit over its null vs night-fit over
its null is the signal. On its own this was ~null in the study — it rides here as a
*corroborating* row, not a decider.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from stellium.core.models import CalculatedChart
from stellium.rectification._data import (
    SIGNIFICANCE_WEIGHT,
    planet_significance,
)
from stellium.rectification._recast import recast

_SUB_LORD_WEIGHT = 0.5
_N_PERMUTATIONS = 300
_SEED = 12345


@dataclass(frozen=True)
class FirdariaConvergence:
    """Per-event day/night firdaria fits, de-confounded."""

    signal_day: float
    signal_night: float
    day_hits: int
    night_hits: int
    ties: int

    @property
    def favors(self) -> str:
        if self.signal_day > self.signal_night:
            return "day"
        if self.signal_night > self.signal_day:
            return "night"
        return "tie"


def _fit(event_type: str, significance: str, lord: str, sub: str | None) -> float:
    weight = SIGNIFICANCE_WEIGHT.get(significance, 0.5)
    score = planet_significance(event_type, lord)
    if sub:
        score += _SUB_LORD_WEIGHT * planet_significance(event_type, sub)
    return weight * score


def firdaria_convergence(
    chart: CalculatedChart, events: Iterable
) -> FirdariaConvergence:
    """Compare the day- and night-order firdaria against the known events."""
    events = list(events)
    day_tl = recast(chart, 12, 0).firdaria()
    night_tl = recast(chart, 0, 0).firdaria()

    type_sig: list[tuple[str, str]] = []
    day_lords: list[tuple[str, str | None]] = []
    night_lords: list[tuple[str, str | None]] = []
    day_hits = night_hits = ties = 0
    for e in events:
        d = e.representative_date
        when = datetime(d.year, d.month, d.day)
        pd, pn = day_tl.at(when), night_tl.at(when)
        dl = (pd.ruler, pd.sub_ruler) if pd else ("—", None)
        nl = (pn.ruler, pn.sub_ruler) if pn else ("—", None)
        type_sig.append((e.type, e.significance))
        day_lords.append(dl)
        night_lords.append(nl)
        fd = _fit(e.type, e.significance, *dl)
        fn = _fit(e.type, e.significance, *nl)
        if fd > fn:
            day_hits += 1
        elif fn > fd:
            night_hits += 1
        else:
            ties += 1

    def total(lords: list[tuple[str, str | None]], ts: list[tuple[str, str]]) -> float:
        return sum(
            _fit(t, s, lo, su) for (t, s), (lo, su) in zip(ts, lords, strict=True)
        )

    score_day = total(day_lords, type_sig)
    score_night = total(night_lords, type_sig)

    rng = random.Random(_SEED)
    perm = list(type_sig)
    null_day = null_night = 0.0
    for _ in range(_N_PERMUTATIONS):
        rng.shuffle(perm)
        null_day += total(day_lords, perm)
        null_night += total(night_lords, perm)
    null_day /= _N_PERMUTATIONS
    null_night /= _N_PERMUTATIONS

    return FirdariaConvergence(
        signal_day=score_day - null_day,
        signal_night=score_night - null_night,
        day_hits=day_hits,
        night_hits=night_hits,
        ties=ties,
    )
