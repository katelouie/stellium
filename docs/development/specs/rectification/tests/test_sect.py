"""Sect-classifier tests — determinism + invariants (not accuracy; that's the
benchmark's job)."""

from __future__ import annotations

import sect
from models import load_corpus

BY = {p.name: p for p in load_corpus()}
PELE = BY["Pelé"]


def test_deterministic():
    a = sect.classify_sect(PELE)
    b = sect.classify_sect(PELE)
    assert a.predicted == b.predicted
    assert a.score_day == b.score_day
    assert a.score_night == b.score_night


def test_probabilities_sum_to_one():
    v = sect.classify_sect(PELE)
    assert abs(v.p_day + v.p_night - 1.0) < 1e-9


def test_predicted_matches_score_argmax():
    v = sect.classify_sect(PELE)
    expected = "night" if v.score_night > v.score_day else "day"
    assert v.predicted == expected
    # probability agrees with the winner
    assert (v.p_day > 0.5) == (v.predicted == "day")


def test_fits_cover_every_event():
    v = sect.classify_sect(PELE)
    assert len(v.fits) == len(PELE.events)


def test_sanity_pele_favors_night():
    # A clear known-night case (03:00 birth); its events lean night.
    assert sect.classify_sect(PELE).predicted == "night"


def test_contrastive_report_renders():
    r = sect.contrastive_report(PELE)
    assert "Pelé" in r and "favors" in r
    assert len(r.splitlines()) >= len(PELE.events)
