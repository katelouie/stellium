"""Tests for the notable biographical datasets (life events + temperament)."""

import warnings
from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest

from stellium import (
    LifeEvent,
    Native,
    Temperament,
    get_notable_life_events,
    get_notable_registry,
    get_notable_temperament,
)
from stellium.exceptions import DataQualityWarning


def test_life_events_load_for_a_known_notable():
    events = get_notable_life_events("Frida Kahlo")
    assert len(events) >= 6
    assert all(isinstance(e, LifeEvent) for e in events)
    assert all(e.precision in {"day", "month", "year"} for e in events)


def test_accepts_a_native_not_just_a_name():
    native = Native(
        datetime(1940, 10, 21, 3, 0),
        {"latitude": -21.7149, "longitude": -45.2533, "timezone": "America/Sao_Paulo"},
        name="Pelé",
    )
    assert len(get_notable_life_events(native)) >= 6


def test_unknown_native_returns_empty():
    assert get_notable_life_events("Nobody McNobody") == ()
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # no warning for an empty temperament miss
        assert get_notable_temperament("Nobody McNobody") == ()


def test_representative_date_fills_toward_mid_span():
    e = LifeEvent("1905", "year", "recognition", "x")
    assert e.representative_date == date(1905, 7, 15)
    assert LifeEvent("1969-07-20", "day", "career", "x").representative_date == date(
        1969, 7, 20
    )


def test_temperament_warns_and_is_soft():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        traits = get_notable_temperament("Frida Kahlo")
    assert len(traits) >= 4
    assert all(isinstance(t, Temperament) for t in traits)
    assert any(
        issubclass(x.category, DataQualityWarning) and "SOFT" in str(x.message)
        for x in w
    )


def test_models_are_frozen():
    e = get_notable_life_events("Frida Kahlo")[0]
    with pytest.raises(FrozenInstanceError):
        e.date = "nope"  # type: ignore[misc]


def test_registry_ignores_the_biography_subdirs():
    # Loading the registry must not choke on life_events/ or temperament/.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        reg = get_notable_registry()
    assert len(reg.get_births()) > 60


def test_case_and_accent_insensitive_lookup():
    assert get_notable_life_events("frida kahlo") == get_notable_life_events(
        "Frida Kahlo"
    )
    assert len(get_notable_life_events("Pelé")) >= 6
