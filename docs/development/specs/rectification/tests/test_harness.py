"""Harness tests — real chart builds via stellium's public API.

Slow-ish (builds charts); kept to a handful of subjects.
"""

from __future__ import annotations

import harness
from models import load_corpus

CORPUS = load_corpus()
BY_NAME = {p.name: p for p in CORPUS}


def test_true_sect_is_valid_for_everyone():
    for p in CORPUS:
        assert harness.true_sect(p) in ("day", "night"), p.name


def test_known_sects():
    assert harness.true_sect(BY_NAME["Pelé"]) == "night"  # 03:00, pre-dawn
    assert harness.true_sect(BY_NAME["Marilyn Monroe"]) == "day"  # 09:30, morning


def test_firdaria_orderings_start_with_sun_and_moon():
    day_tl, night_tl = harness.firdaria_day_night(BY_NAME["Pelé"])
    assert day_tl.periods[0].ruler == "Sun"
    assert night_tl.periods[0].ruler == "Moon"
    # the two orderings are genuinely different sequences
    assert [x.ruler for x in day_tl.majors()] != [x.ruler for x in night_tl.majors()]


def test_candidate_sweep_shows_three_regions():
    sweep = harness.candidate_sects(BY_NAME["Pelé"], step_minutes=30)
    sects = {s for _, s in sweep}
    assert sects == {"day", "night"}  # both present (temperate)
    at_hour = {m // 60: s for m, s in sweep}
    assert at_hour[0] == "night"  # midnight
    assert at_hour[12] == "day"  # midday
    assert at_hour[23] == "night"  # late evening
