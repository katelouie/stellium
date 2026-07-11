"""Data models + corpus loader for the rectification proving harness.

Frozen dataclasses mirroring the parent spec's ``LifeEvent`` / ``Evidence`` so
promotion into ``stellium/rectification/`` is a move, not a rewrite. ``load_corpus``
maps ``rectification-corpus-events.yaml`` straight onto them.

Stdlib + PyYAML only (no stellium import at this layer).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

# The assembled corpus lives one level up (docs/development/specs/).
DEFAULT_CORPUS = (
    Path(__file__).resolve().parent.parent / "rectification-corpus-events.yaml"
)

PRECISIONS = frozenset({"day", "month", "year"})
SIGNIFICANCES = frozenset({"major", "moderate", "minor"})


@dataclass(frozen=True)
class LifeEvent:
    """A single dated life event (hard data)."""

    date_str: str  # as recorded: "YYYY", "YYYY-MM", or "YYYY-MM-DD"
    precision: str  # day | month | year
    type: str  # event-taxonomy key (relationship, career, ...)
    description: str
    significance: str = "major"  # major | moderate | minor
    age_at_event: int | None = None
    source: str = ""

    @property
    def representative_date(self) -> date:
        """A single date to key timing techniques on.

        Missing month/day are filled toward the *middle* of the unknown span
        (year -> mid-year, month -> mid-month) to minimise the average error —
        immaterial for year-scale techniques like firdaria, honest for the rest.
        """
        parts = [int(p) for p in str(self.date_str).split("-")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 7
        day = parts[2] if len(parts) > 2 else 15
        return date(year, month, day)


@dataclass(frozen=True)
class Trait:
    """A temperament descriptor (soft data)."""

    trait: str
    tags: tuple[str, ...] = ()
    evidence: str = ""
    source: str = ""


@dataclass(frozen=True)
class BirthData:
    """Verified birth data — the ground truth we blank and try to recover."""

    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM", 24-hour, local
    timezone: str  # IANA name
    place: str
    latitude: float
    longitude: float
    rodden_rating: str

    def datetime(self) -> datetime:
        """Timezone-aware local birth datetime."""
        year, month, day = (int(x) for x in self.date.split("-"))
        hour, minute = (int(x) for x in self.time.split(":"))
        tz = ZoneInfo(self.timezone) if self.timezone else None
        return datetime(year, month, day, hour, minute, tzinfo=tz)


@dataclass(frozen=True)
class CorpusPerson:
    """One benchmark subject: verified birth truth + gathered evidence."""

    name: str
    birth_data: BirthData
    events: tuple[LifeEvent, ...]
    temperament: tuple[Trait, ...]
    notes: str = ""


def load_corpus(path: str | Path = DEFAULT_CORPUS) -> list[CorpusPerson]:
    """Load the assembled corpus YAML into ``CorpusPerson`` records."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    people: list[CorpusPerson] = []
    for p in raw:
        bd = p["birth_data"]
        birth = BirthData(
            date=str(bd["date"]),
            time=str(bd["time"]),
            timezone=str(bd.get("timezone", "")),
            place=str(bd.get("place", "")),
            latitude=bd.get("latitude"),
            longitude=bd.get("longitude"),
            rodden_rating=str(bd.get("rodden_rating", "")),
        )
        events = tuple(
            LifeEvent(
                date_str=str(e["date"]),
                precision=str(e.get("precision", "day")),
                type=str(e.get("type", "other")),
                description=str(e.get("description", "")),
                significance=str(e.get("significance", "major")),
                age_at_event=e.get("age_at_event"),
                source=str(e.get("source", "")),
            )
            for e in (p.get("events") or [])
        )
        traits = tuple(
            Trait(
                trait=str(t.get("trait", "")),
                tags=tuple(str(x) for x in (t.get("tags") or [])),
                evidence=str(t.get("evidence", "")),
                source=str(t.get("source", "")),
            )
            for t in (p.get("temperament") or [])
        )
        people.append(
            CorpusPerson(
                name=str(p["name"]),
                birth_data=birth,
                events=events,
                temperament=traits,
                notes=str(p.get("notes", "")),
            )
        )
    return people
