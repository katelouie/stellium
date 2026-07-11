"""Phase 1 — the sect classifier (the proving experiment).

For each dated event, find the active firdaria time-lord under the **day** and
**night** orderings, and score how well that lord naturally signifies the event
(theory §6 planetary significators, weighted by event significance).

Naively comparing the two raw sums is **confounded**: the night ordering
front-loads Saturn/Jupiter/Mars in the event-dense early decades, and those are
the generically-significant planets (Saturn alone signifies 8/15 event types), so
night scores higher for *anyone*. We remove that with a **per-person permutation
null**: each ordering is scored as its *excess over* what it would score if the
event-types were shuffled onto the same lord sequence. The true sect's ordering
should align types with apt lords better than chance; the wrong one shouldn't.

Still just firdaria × significators — no grid, no calibration.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime

import harness
from models import CorpusPerson, LifeEvent
from significators import planet_significance

# Permutation-null settings (seeded → deterministic).
N_PERMUTATIONS = 300
SEED = 12345

# How much an event counts, by significance.
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}
# Sub-period lord counts less than the major-period lord.
SUB_LORD_WEIGHT = 0.5
# Softmax temperature — affects the *reported probability* only, not the argmax.
DEFAULT_TEMPERATURE = 0.4


@dataclass(frozen=True)
class EventFit:
    event: LifeEvent
    day_lord: str
    day_sub: str | None
    night_lord: str
    night_sub: str | None
    day_score: float
    night_score: float

    @property
    def favors(self) -> str:
        if self.day_score > self.night_score:
            return "day"
        if self.night_score > self.day_score:
            return "night"
        return "tie"


@dataclass(frozen=True)
class SectVerdict:
    person: str
    predicted: str  # "day" | "night"
    p_day: float
    p_night: float
    signal_day: float  # excess of day-fit over its permutation null
    signal_night: float
    score_day: float  # raw sums (for the report / diagnostics)
    score_night: float
    fits: tuple[EventFit, ...]


def _fit(event_type: str, significance: str, lord: str, sub_lord: str | None) -> float:
    """Significance-weighted fit of a period's lords to an event type."""
    weight = SIGNIFICANCE_WEIGHT.get(significance, 0.5)
    score = planet_significance(event_type, lord)
    if sub_lord:
        score += SUB_LORD_WEIGHT * planet_significance(event_type, sub_lord)
    return weight * score


def classify_sect(
    person: CorpusPerson,
    *,
    temperature: float = DEFAULT_TEMPERATURE,
    n_perm: int = N_PERMUTATIONS,
) -> SectVerdict:
    """Predict day vs night from the events alone (permutation-null de-confounded)."""
    day_tl, night_tl = harness.firdaria_day_night(person)

    # Per event: (type, significance) and the lords each ordering assigns.
    type_sig: list[tuple[str, str]] = []
    day_lords: list[tuple[str, str | None]] = []
    night_lords: list[tuple[str, str | None]] = []
    fits: list[EventFit] = []
    for e in person.events:
        d = e.representative_date
        when = datetime(d.year, d.month, d.day)
        pday, pnight = day_tl.at(when), night_tl.at(when)
        dl = (pday.ruler, pday.sub_ruler) if pday else ("—", None)
        nl = (pnight.ruler, pnight.sub_ruler) if pnight else ("—", None)
        type_sig.append((e.type, e.significance))
        day_lords.append(dl)
        night_lords.append(nl)
        fd = _fit(e.type, e.significance, *dl)
        fn = _fit(e.type, e.significance, *nl)
        fits.append(EventFit(e, dl[0], dl[1], nl[0], nl[1], fd, fn))

    def total(lords: list[tuple[str, str | None]], ts: list[tuple[str, str]]) -> float:
        return sum(
            _fit(t, s, lo, su) for (t, s), (lo, su) in zip(ts, lords, strict=True)
        )

    score_day = total(day_lords, type_sig)
    score_night = total(night_lords, type_sig)

    # Permutation null: shuffle the (type, significance) labels onto the same
    # lord sequence; the excess of actual over null is the de-confounded signal.
    rng = random.Random(SEED)
    perm = list(type_sig)
    null_day = null_night = 0.0
    for _ in range(n_perm):
        rng.shuffle(perm)
        null_day += total(day_lords, perm)
        null_night += total(night_lords, perm)
    null_day /= n_perm
    null_night /= n_perm

    signal_day = score_day - null_day
    signal_night = score_night - null_night

    a, b = signal_day / temperature, signal_night / temperature
    m = max(a, b)
    ed, en = math.exp(a - m), math.exp(b - m)
    p_day = ed / (ed + en)
    predicted = "night" if signal_night > signal_day else "day"

    return SectVerdict(
        person=person.name,
        predicted=predicted,
        p_day=p_day,
        p_night=1.0 - p_day,
        signal_day=signal_day,
        signal_night=signal_night,
        score_day=score_day,
        score_night=score_night,
        fits=tuple(fits),
    )


def contrastive_report(person: CorpusPerson) -> str:
    """Human-readable 'walk both paths': per event, which sect's lord fit better."""
    v = classify_sect(person)
    lines = [
        f"{person.name} — predicted {v.predicted.upper()} "
        f"(P(day)={v.p_day:.2f}; signal day={v.signal_day:+.2f} vs "
        f"night={v.signal_night:+.2f}; raw {v.score_day:.1f}/{v.score_night:.1f})",
        f"{'event':<34}{'type':<18}{'day-lord':<16}{'night-lord':<16}favors",
        "-" * 100,
    ]
    for f in v.fits:
        e = f.event
        desc = (e.description[:30] + "…") if len(e.description) > 31 else e.description
        day_l = f.day_lord + (f"/{f.day_sub}" if f.day_sub else "")
        night_l = f.night_lord + (f"/{f.night_sub}" if f.night_sub else "")
        star = {"day": "← day", "night": "night →", "tie": "·"}[f.favors]
        lines.append(
            f"{e.date_str + ' ' + desc:<34}{e.type:<18}{day_l:<16}{night_l:<16}{star}"
        )
    return "\n".join(lines)
