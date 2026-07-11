"""Tests for the time-posterior pipeline + combined sect classifier."""

from __future__ import annotations

import sect_classifier as sc
from models import load_corpus
from posterior import build_posterior
from profection import make_profection_scorer, year_lord

CORPUS = load_corpus()
BY = {p.name: p for p in CORPUS}
PELE = BY["Pelé"]


def test_year_lord_whole_sign():
    # Leo rising, age 0 -> Leo -> Sun; age 1 -> Virgo -> Mercury.
    assert year_lord("Leo", 0) == "Sun"
    assert year_lord("Leo", 1) == "Mercury"
    assert year_lord("Aries", 0) == "Mars"


def test_posterior_normalised_and_marginal():
    post = build_posterior(PELE, make_profection_scorer(PELE), step_minutes=30)
    total = sum(c.prob for c in post.candidates)
    assert abs(total - 1.0) < 1e-9
    assert abs(post.p_day + post.p_night - 1.0) < 1e-9
    day_mass = sum(c.prob for c in post.candidates if c.sect == "day")
    assert abs(post.p_day - day_mass) < 1e-9


def test_posterior_deterministic():
    a = build_posterior(PELE, make_profection_scorer(PELE), step_minutes=30)
    b = build_posterior(PELE, make_profection_scorer(PELE), step_minutes=30)
    assert a.p_day == b.p_day and a.map_minute == b.map_minute


def test_daylight_fraction_is_a_probability():
    dl = sc.daylight_fraction(PELE)
    assert 0.0 < dl < 1.0


def test_classifier_fit_and_predict():
    feats = [sc.features(p) for p in CORPUS[:20]]
    y = [1, 0] * 10
    model = sc.fit(feats, y, epochs=200)
    p = model.p_day(feats[0])
    assert 0.0 <= p <= 1.0
    # deterministic
    assert sc.fit(feats, y, epochs=200).weights == model.weights
