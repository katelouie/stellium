"""Event-type -> significators, from RECTIFICATION_THEORY.md §6.

Two layers:

* ``PLANET_SIGNIFICATORS`` — the **natural planetary** significators, weighted.
  These are what the v0 sect classifier uses: firdaria time-lords are the seven
  traditional planets, and their appropriateness for an event is *independent of
  birth time*, so they isolate the sect signal (which flips the firdaria order).

* ``HOUSE_LOT_SIGNIFICATORS`` — the house / lot significators (also from §6),
  recorded for the later time-sensitive phases. **Not used by v0** (they need the
  chart, hence the time, which is exactly what we're inferring).

The weights are an expert-prior starting point (theory §7: "fixed table, then
calibrate"); they are meant to be tuned, not treated as ground truth.
"""

from __future__ import annotations

# The seven traditional planets — the only bodies that can be a firdaria lord.
TRADITIONAL_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")

# event-taxonomy key -> {planet: weight in (0, 1]}
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
    "other": {},  # deliberately no planetary signal
}

# Reference only (later phases). house numbers + lots + "ruler_of_N".
HOUSE_LOT_SIGNIFICATORS: dict[str, dict[str, list]] = {
    "relationship": {"houses": [7], "lots": ["Marriage"], "rulers": [7]},
    "career": {"houses": [10], "lots": ["Spirit"], "rulers": [10], "points": ["MC"]},
    "recognition": {
        "houses": [10],
        "lots": ["Spirit"],
        "rulers": [10],
        "points": ["MC"],
    },
    "relocation": {"houses": [4, 9], "rulers": [4]},
    "bereavement_parent": {"houses": [4, 10, 8], "rulers": [4, 10]},
    "bereavement_other": {"houses": [8], "rulers": [8]},
    "childbirth": {"houses": [5], "lots": ["Children"], "rulers": [5]},
    "health_crisis": {"houses": [1, 6, 8], "lots": ["Fortune"], "rulers": [6]},
    "accident": {"houses": [1, 6, 8], "lots": ["Fortune"], "rulers": [8]},
    "windfall": {"houses": [2, 8], "lots": ["Fortune"], "rulers": [2]},
    "financial_loss": {"houses": [2, 8], "lots": ["Fortune"], "rulers": [2]},
    "legal": {"houses": [12, 7], "rulers": [12]},
    "education": {"houses": [3, 9], "rulers": [9]},
    "spiritual": {"houses": [9, 12], "rulers": [9]},
    "other": {},
}


def planet_significance(event_type: str, planet: str) -> float:
    """How strongly ``planet`` naturally signifies ``event_type`` (0 if not)."""
    return PLANET_SIGNIFICATORS.get(event_type, {}).get(planet, 0.0)
