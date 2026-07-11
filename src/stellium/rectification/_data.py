"""Internal reference tables for sect analysis — significators + coarse dignity.

Kept private to the subsystem: these are the expert-prior tables the empirical
rectification study used (see ``docs/development/specs/RECTIFICATION_REPORT.md``),
not general-purpose package data. The seven traditional planets only.
"""

from __future__ import annotations

SIGN_ORDER = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

DOMICILE_RULER = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

EXALT_SIGN = {
    "Sun": "Aries",
    "Moon": "Taurus",
    "Mercury": "Virgo",
    "Venus": "Pisces",
    "Mars": "Capricorn",
    "Jupiter": "Cancer",
    "Saturn": "Libra",
}

# event-taxonomy key -> {planet: natural-significator weight in (0, 1]}
PLANET_SIGNIFICATORS: dict[str, dict[str, float]] = {
    "relationship": {"Venus": 1.0, "Moon": 0.4, "Jupiter": 0.3},
    "career": {"Sun": 0.7, "Saturn": 0.7, "Mercury": 0.4, "Jupiter": 0.4, "Mars": 0.3},
    "recognition": {"Sun": 1.0, "Jupiter": 0.6, "Mars": 0.3},
    "relocation": {"Moon": 0.9, "Mercury": 0.5, "Saturn": 0.3},
    "bereavement_parent": {"Saturn": 0.9, "Sun": 0.4, "Moon": 0.4},
    "bereavement_other": {"Saturn": 0.8, "Mars": 0.4},
    "childbirth": {"Jupiter": 1.0, "Moon": 0.6, "Venus": 0.5},
    "health_crisis": {"Mars": 0.8, "Saturn": 0.8},
    "accident": {"Mars": 1.0, "Saturn": 0.5},
    "windfall": {"Jupiter": 1.0, "Venus": 0.5, "Sun": 0.3},
    "financial_loss": {"Saturn": 0.9, "Mars": 0.4},
    "legal": {"Saturn": 0.8, "Mercury": 0.5, "Mars": 0.5},
    "education": {"Mercury": 1.0, "Jupiter": 0.6},
    "spiritual": {"Jupiter": 0.8, "Saturn": 0.5},
    "other": {},
}
ALL_EVENT_TYPES = tuple(PLANET_SIGNIFICATORS)
SIGNIFICANCE_WEIGHT = {"major": 1.0, "moderate": 0.6, "minor": 0.3}


def planet_significance(event_type: str, planet: str) -> float:
    """How strongly ``planet`` naturally signifies ``event_type`` (0 if not)."""
    return PLANET_SIGNIFICATORS.get(event_type, {}).get(planet, 0.0)


def _opposite(sign: str) -> str:
    return SIGN_ORDER[(SIGN_ORDER.index(sign) + 6) % 12]


def essential_dignity(planet: str, sign: str) -> int:
    """Coarse Ptolemaic essential dignity by sign (domicile/exalt/detriment/fall)."""
    if DOMICILE_RULER[sign] == planet:
        return 5
    if EXALT_SIGN.get(planet) == sign:
        return 4
    if DOMICILE_RULER[_opposite(sign)] == planet:  # detriment
        return -5
    if EXALT_SIGN.get(planet) == _opposite(sign):  # fall
        return -4
    return 0


DIGNITY_LABEL = {
    5: "domicile",
    4: "exalted",
    0: "peregrine",
    -4: "fall",
    -5: "detriment",
}


def dignity_label(planet: str, sign: str) -> str:
    return DIGNITY_LABEL[essential_dignity(planet, sign)]
