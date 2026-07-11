"""Benchmark harness — builds charts from the corpus via stellium's public API.

Full recompute per chart (spec §4.1): no hand-rolled re-cast, so the Moon and
per-candidate sect are always exactly right. The v0 sect classifier is
essentially grid-free — it compares the day-order vs night-order firdaria, each
near time-independent — so it needs only ~3 chart builds per person (true +
a day-representative + a night-representative), not a 360-candidate sweep.

This is the ONE layer that imports stellium (as a public-API consumer).
"""

from __future__ import annotations

from models import BirthData, CorpusPerson

from stellium import ChartBuilder, Native


def build_chart(bd: BirthData, hhmm: tuple[int, int] | None = None):
    """Full `.calculate()` for this birth data, optionally overriding the time.

    Coordinates + explicit timezone → no geocoding, no network.
    """
    time = bd.time if hhmm is None else f"{hhmm[0]:02d}:{hhmm[1]:02d}"
    native = Native(
        f"{bd.date} {time}:00",
        {"latitude": bd.latitude, "longitude": bd.longitude, "timezone": bd.timezone},
    )
    return ChartBuilder.from_native(native).calculate()


def true_chart(person: CorpusPerson):
    """Chart at the person's real (verified) birth time."""
    return build_chart(person.birth_data)


def true_sect(person: CorpusPerson) -> str:
    """Ground-truth sect ("day"/"night") from the real birth time."""
    return true_chart(person).sect


def firdaria_day_night(person: CorpusPerson):
    """Return (day_order_timeline, night_order_timeline).

    Extracted from a noon chart (day sect) and a midnight chart (night sect).
    The ~12 h birth-time offset between the two shifts period boundaries by far
    less than any event's date precision, so it is immaterial for matching.
    """
    day_chart = build_chart(person.birth_data, (12, 0))
    night_chart = build_chart(person.birth_data, (0, 0))
    # Temperate corpus: noon is day, midnight is night. Guard the assumption.
    if day_chart.sect != "day" or night_chart.sect != "night":
        raise ValueError(
            f"{person.name}: noon/midnight did not yield day/night "
            f"(noon={day_chart.sect}, midnight={night_chart.sect}) — polar birth?"
        )
    return day_chart.firdaria(), night_chart.firdaria()


def candidate_sects(
    person: CorpusPerson, step_minutes: int = 10
) -> list[tuple[int, str]]:
    """Full-recompute sweep of sect across the local day (spec §4.1 baseline).

    Returns (minutes-since-local-midnight, sect) per candidate. Not used by the
    v0 classifier — it exercises the full-recompute path and reveals the
    three-region sect structure empirically. Profile lever lives here.
    """
    out: list[tuple[int, str]] = []
    for minute_of_day in range(0, 24 * 60, step_minutes):
        chart = build_chart(person.birth_data, divmod(minute_of_day, 60))
        out.append((minute_of_day, chart.sect))
    return out
