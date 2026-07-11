"""Integrity tests for the event -> significator table."""

from __future__ import annotations

from models import PRECISIONS  # noqa: F401  (ensure package import path works)
from significators import (
    PLANET_SIGNIFICATORS,
    TRADITIONAL_PLANETS,
    planet_significance,
)

# The full event taxonomy the corpus + prompt use.
TAXONOMY = {
    "relationship",
    "career",
    "recognition",
    "relocation",
    "bereavement_parent",
    "bereavement_other",
    "childbirth",
    "health_crisis",
    "accident",
    "windfall",
    "financial_loss",
    "legal",
    "education",
    "spiritual",
    "other",
}


def test_table_covers_the_whole_taxonomy():
    assert set(PLANET_SIGNIFICATORS) == TAXONOMY


def test_weights_are_in_range_and_planets_are_traditional():
    for etype, sigs in PLANET_SIGNIFICATORS.items():
        for planet, weight in sigs.items():
            assert planet in TRADITIONAL_PLANETS, f"{etype}: {planet} not traditional"
            assert 0.0 < weight <= 1.0, (
                f"{etype}: {planet} weight {weight} out of range"
            )


def test_every_type_except_other_has_a_signal():
    for etype, sigs in PLANET_SIGNIFICATORS.items():
        if etype == "other":
            assert sigs == {}
        else:
            assert sigs, f"{etype} has no significators"


def test_lookup_helper():
    assert planet_significance("relationship", "Venus") == 1.0
    assert planet_significance("accident", "Mars") == 1.0
    assert planet_significance("relationship", "Saturn") == 0.0  # not a significator
    assert planet_significance("nonsense", "Venus") == 0.0  # unknown type
