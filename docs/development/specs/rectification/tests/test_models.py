"""Tests for the corpus loader + data models."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from models import BirthData, CorpusPerson, LifeEvent, load_corpus

CORPUS = load_corpus()
BY_NAME = {p.name: p for p in CORPUS}


# --- loading ---------------------------------------------------------------


def test_corpus_has_63_people():
    assert len(CORPUS) == 63


def test_every_person_well_formed():
    for p in CORPUS:
        assert isinstance(p, CorpusPerson)
        assert p.name
        assert isinstance(p.birth_data, BirthData)
        assert len(p.events) >= 6, f"{p.name} has {len(p.events)} events"
        assert len(p.temperament) >= 4, f"{p.name} has {len(p.temperament)} traits"


def test_events_and_traits_are_typed():
    p = CORPUS[0]
    assert all(isinstance(e, LifeEvent) for e in p.events)
    assert all(e.precision in {"day", "month", "year"} for e in p.events)
    assert all(e.significance in {"major", "moderate", "minor"} for e in p.events)


# --- a known person, exact values ------------------------------------------


def test_pele_birth_data_is_verified_truth():
    pele = BY_NAME["Pelé"]
    bd = pele.birth_data
    assert bd.date == "1940-10-21"
    assert bd.time == "03:00"
    assert bd.timezone == "America/Sao_Paulo"
    assert bd.rodden_rating == "AA"
    dt = bd.datetime()
    assert (dt.year, dt.month, dt.day, dt.hour, dt.minute) == (1940, 10, 21, 3, 0)
    assert dt.tzinfo is not None  # timezone-aware


# --- representative_date across precisions ---------------------------------


def test_representative_date_day_precision_is_exact():
    e = LifeEvent("1969-03-20", "day", "relationship", "x")
    assert e.representative_date == date(1969, 3, 20)


def test_representative_date_fills_toward_the_middle():
    assert LifeEvent("1905", "year", "recognition", "x").representative_date == date(
        1905, 7, 15
    )
    assert LifeEvent("1901-11", "month", "career", "x").representative_date == date(
        1901, 11, 15
    )


def test_all_corpus_event_dates_parse():
    for p in CORPUS:
        for e in p.events:
            d = e.representative_date  # must not raise
            assert 1400 <= d.year <= 2026


# --- immutability ----------------------------------------------------------


def test_models_are_frozen():
    with pytest.raises(FrozenInstanceError):
        CORPUS[0].name = "nope"  # type: ignore[misc]
