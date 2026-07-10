"""Almuten of a degree — the essential-dignity victor over a longitude.

Given a zodiacal longitude, the almuten is the planet holding the most essential
dignity *there*, scored by the classical weights (Ibn Ezra / Lilly): domicile 5,
exaltation 4, triplicity 3, term 2, face 1. This is the foundation of the hyleg
and alcocoden (length of life) and is generally reusable.

Distinct from ``CalculatedChart.get_strongest_planet()``, which finds the almuten
*among the placed planets*; this is the almuten *of a point*.
"""

from __future__ import annotations

from dataclasses import dataclass

from stellium.core.models import longitude_to_sign_and_degree
from stellium.engines.dignities import DIGNITIES

# Classical essential-dignity weights.
DIGNITY_WEIGHTS: dict[str, int] = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity": 3,
    "term": 2,
    "face": 1,
}

_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")


@dataclass(frozen=True)
class AlmutenResult:
    """The almuten of a degree, with its supporting scores.

    Attributes:
        winner: The planet with the most essential dignity (``""`` if none —
            i.e. the degree is peregrine for all seven, which cannot happen for
            term/face but is guarded anyway).
        scores: Per-planet total essential-dignity score at the degree.
        dignities: Which dignities (``"domicile"``, ``"term"``, …) each planet
            holds at the degree.
        tie: The planets sharing the top score when there is a tie (empty
            otherwise). Callers with chart context break ties by accidental
            strength (e.g. angularity).
    """

    winner: str
    scores: dict[str, int]
    dignities: dict[str, list[str]]
    tie: tuple[str, ...]


def _term_ruler(sign_data: dict, degree: float) -> str:
    """The Egyptian-term ruler at ``degree`` within a sign."""
    bounds = sign_data["bound_egypt"]
    ruler = ""
    for start in sorted(bounds):
        if degree >= start:
            ruler = bounds[start]
    return ruler


def _face_ruler(sign_data: dict, degree: float) -> str:
    """The Chaldean face (decan) ruler at ``degree`` within a sign."""
    return sign_data["decan_chaldean"][min(int(degree // 10), 2)]


def almuten_of_degree(
    longitude: float,
    sect: str = "day",
    *,
    system: str = "traditional",
) -> AlmutenResult:
    """Compute the almuten (essential-dignity victor) of a longitude.

    Args:
        longitude: Zodiacal longitude (0-360).
        sect: ``"day"`` or ``"night"`` — selects the triplicity ruler.
        system: ``"traditional"`` or ``"modern"`` rulerships (for domicile /
            exaltation; terms and faces are traditional either way).

    Returns:
        An :class:`AlmutenResult`.
    """
    sign, degree = longitude_to_sign_and_degree(longitude)
    data = DIGNITIES[sign]

    scores: dict[str, int] = dict.fromkeys(_PLANETS, 0)
    dignities: dict[str, list[str]] = {p: [] for p in _PLANETS}

    def award(planet: str | None, kind: str) -> None:
        # Guard: exaltation/domicile can name a node in some schemes.
        if planet in scores:
            scores[planet] += DIGNITY_WEIGHTS[kind]
            dignities[planet].append(kind)

    award(data[system]["ruler"], "domicile")
    award(data[system].get("exaltation"), "exaltation")
    trip = data["triplicity"].get(sect, data["triplicity"]["day"])
    award(trip, "triplicity")
    award(_term_ruler(data, degree), "term")
    award(_face_ruler(data, degree), "face")

    top = max(scores.values())
    winners = tuple(p for p in _PLANETS if scores[p] == top and top > 0)
    return AlmutenResult(
        winner=winners[0] if winners else "",
        scores=scores,
        dignities=dignities,
        tie=winners if len(winners) > 1 else (),
    )
