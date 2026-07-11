"""Biographical datasets for notable natives — life events and temperament.

These are catalog **lookups keyed by name**, deliberately kept separate from birth
data because their provenance is different:

* **Life events** (`get_notable_life_events`) — dated biographical events, gathered
  from biographies + AstroDataBank via research: sourced, but **not** individually
  certificate-verified. Treat as Rodden ~B (secondary) grade, and honour each
  event's ``precision`` (day/month/year).
* **Temperament** (`get_notable_temperament`) — **soft, interpretive** character
  descriptors distilled from biographies, *not* measurements. The getter emits a
  :class:`~stellium.exceptions.DataQualityWarning` on access to keep that honest.

Both getters accept a name string or anything carrying a ``.name`` (a ``Native`` or
``Notable``), so ``get_notable_life_events(native)`` works.
"""

from __future__ import annotations

import importlib.resources
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from stellium.exceptions import DataQualityWarning


@dataclass(frozen=True)
class LifeEvent:
    """A dated biographical event for a notable native (~B provenance)."""

    date: str  # as recorded: "YYYY", "YYYY-MM", or "YYYY-MM-DD"
    precision: str  # "day" | "month" | "year"
    type: str  # event-taxonomy key (relationship, career, bereavement_*, ...)
    description: str
    significance: str = "major"  # major | moderate | minor
    age_at_event: int | None = None
    source: str = ""

    @property
    def representative_date(self) -> date:
        """A single date for timing work; missing month/day fill toward mid-span."""
        parts = [int(p) for p in str(self.date).split("-")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 7
        day = parts[2] if len(parts) > 2 else 15
        return date(year, month, day)


@dataclass(frozen=True)
class Temperament:
    """A soft, interpretive character descriptor for a notable native."""

    trait: str
    tags: tuple[str, ...] = ()
    evidence: str = ""
    source: str = ""


# --- loading (lazy, cached) --------------------------------------------------

_life_events: dict[str, tuple[LifeEvent, ...]] | None = None
_temperament: dict[str, tuple[Temperament, ...]] | None = None


def _key(name_or_native: object) -> str:
    """Normalise a name (or a Native/Notable's .name) for case/accent-stable lookup."""
    name = getattr(name_or_native, "name", name_or_native)
    return unicodedata.normalize("NFC", str(name)).strip().casefold()


def _subdir(name: str) -> Path | None:
    """Resolve notables/<name>/ across editable and installed layouts."""
    try:
        files = importlib.resources.files("stellium.data")
        target = files / "notables" / name
        if hasattr(target, "_path"):
            p = Path(target._path)
            if p.exists():
                return p
        with importlib.resources.as_file(target) as p:
            return p if p.exists() else None
    except (TypeError, FileNotFoundError, AttributeError):
        return None


def _load_life_events() -> dict[str, tuple[LifeEvent, ...]]:
    global _life_events
    if _life_events is not None:
        return _life_events
    out: dict[str, tuple[LifeEvent, ...]] = {}
    d = _subdir("life_events")
    if d is not None:
        for f in sorted(d.glob("*.yaml")):
            for person in yaml.safe_load(f.read_text(encoding="utf-8")) or []:
                events = tuple(
                    LifeEvent(
                        date=str(e["date"]),
                        precision=str(e.get("precision", "day")),
                        type=str(e.get("type", "other")),
                        description=str(e.get("description", "")),
                        significance=str(e.get("significance", "major")),
                        age_at_event=e.get("age_at_event"),
                        source=str(e.get("source", "")),
                    )
                    for e in (person.get("events") or [])
                )
                out[_key(person["name"])] = events
    _life_events = out
    return out


def _load_temperament() -> dict[str, tuple[Temperament, ...]]:
    global _temperament
    if _temperament is not None:
        return _temperament
    out: dict[str, tuple[Temperament, ...]] = {}
    d = _subdir("temperament")
    if d is not None:
        for f in sorted(d.glob("*.yaml")):
            for person in yaml.safe_load(f.read_text(encoding="utf-8")) or []:
                traits = tuple(
                    Temperament(
                        trait=str(t.get("trait", "")),
                        tags=tuple(str(x) for x in (t.get("tags") or [])),
                        evidence=str(t.get("evidence", "")),
                        source=str(t.get("source", "")),
                    )
                    for t in (person.get("temperament") or [])
                )
                out[_key(person["name"])] = traits
    _temperament = out
    return out


# --- public API --------------------------------------------------------------


def get_notable_life_events(name_or_native: object) -> tuple[LifeEvent, ...]:
    """Dated biographical life events for a notable native.

    Args:
        name_or_native: a name string, or a ``Native``/``Notable`` (its ``.name``
            is used).

    Returns:
        A tuple of :class:`LifeEvent` (empty if the native isn't catalogued).

    Note:
        These events are ~B (secondary-source) provenance — sourced but not
        certificate-verified. Honour each event's ``precision``.
    """
    return _load_life_events().get(_key(name_or_native), ())


def get_notable_temperament(name_or_native: object) -> tuple[Temperament, ...]:
    """Soft, interpretive temperament descriptors for a notable native.

    Args:
        name_or_native: a name string, or a ``Native``/``Notable``.

    Returns:
        A tuple of :class:`Temperament` (empty if the native isn't catalogued).

    Warns:
        :class:`~stellium.exceptions.DataQualityWarning` on access — this data is
        subjective and distilled from biographies, not measured. Use accordingly.
    """
    data = _load_temperament().get(_key(name_or_native), ())
    if data:
        warnings.warn(
            "Notable temperament data is SOFT/interpretive (subjective descriptors "
            "distilled from biographies, not measurements) — treat as low-confidence.",
            DataQualityWarning,
            stacklevel=2,
        )
    return data
