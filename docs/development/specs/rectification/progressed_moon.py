"""Secondary-progressed Moon to natal significators — a chapter-timing method.

The progressed Moon (~1°/month, one cycle in ~27 years) is the classic marker of
life "chapters": when it aspects a natal planet that signifies an event, near that
event's date, the timing corroborates. It is nearly **birth-time-independent** — it
rides the natal Moon, which moves only ~6° across a whole day — so we compute it
once per person and, in the workbench, show it as a near-constant reference row. Its
*flatness* across candidate times is itself the honest readout: this technique
barely discriminates birth time, it only corroborates the life's chapter structure.

Scored and de-confounded against a per-person event-type shuffle, like the others.
"""

from __future__ import annotations

import random
from datetime import datetime

import harness
from models import CorpusPerson
from significators import PLANET_SIGNIFICATORS, planet_significance

from stellium import ChartBuilder, Native
from stellium.utils.progressions import calculate_progressed_datetime

NATAL_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
ASPECTS = (0.0, 60.0, 90.0, 120.0, 180.0)  # Ptolemaic set
ORB = 1.5
ALL_TYPES = tuple(PLANET_SIGNIFICATORS)
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}
N_PERMUTATIONS = 150
SEED = 17


def _sep(a: float, b: float) -> float:
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _aspect_closeness(a: float, b: float) -> float:
    best = 0.0
    sep = _sep(a, b)
    for asp in ASPECTS:
        d = abs(sep - asp)
        if d < ORB:
            best = max(best, 1.0 - d / ORB)
    return best


def progressed_moon_signal(person: CorpusPerson) -> float:
    """De-confounded fit of the progressed Moon's aspects to apt natal planets."""
    bd = person.birth_data
    by, bm, bday = (int(x) for x in bd.date.split("-"))
    natal_dt = datetime(by, bm, bday, 12, 0)
    natal = harness.build_chart(bd, (12, 0))  # noon; ~time-independent for this method
    natal_lon = {p: natal.get_object(p).longitude for p in NATAL_PLANETS}

    events = list(person.events)
    types = [e.type for e in events]
    sig_w = [SIGNIFICANCE_WEIGHT.get(e.significance, 0.5) for e in events]

    # progressed-Moon longitude per event (computed once)
    prog_moon: list[float] = []
    for e in events:
        d = e.representative_date
        pdt = calculate_progressed_datetime(
            natal_dt, datetime(d.year, d.month, d.day, 12, 0), "secondary"
        )
        # build a chart at the progressed datetime and read its Moon
        nat = Native(
            pdt.strftime("%Y-%m-%d %H:%M:%S"),
            {
                "latitude": bd.latitude,
                "longitude": bd.longitude,
                "timezone": bd.timezone,
            },
        )
        pchart = ChartBuilder.from_native(nat).calculate()
        prog_moon.append(pchart.get_object("Moon").longitude)

    def fit_for(i: int, event_type: str) -> float:
        best = 0.0
        for pl in NATAL_PLANETS:
            sigv = planet_significance(event_type, pl)
            if sigv <= 0:
                continue
            close = _aspect_closeness(prog_moon[i], natal_lon[pl])
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
