"""Re-cast a chart at a different local time — the day/night hypotheses.

Sect analysis on an *unknown-time* chart works by casting BOTH a day-sect (noon)
and a night-sect (midnight) hypothesis from the same birth date + place, never from
the (unknown) real time. This helper rebuilds a chart at an arbitrary local time via
the public :class:`~stellium.core.builder.ChartBuilder`, so the Moon and every
angle are always exactly right (full recompute, no hand-rolled re-cast).
"""

from __future__ import annotations

import math
from datetime import date
from zoneinfo import ZoneInfo

from stellium.core.models import CalculatedChart, CelestialPosition


def require_obj(chart: CalculatedChart, name: str) -> CelestialPosition:
    """Get a chart object that is expected to exist (angles, luminaries, planets)."""
    obj = chart.get_object(name)
    if obj is None:
        raise ValueError(f"chart is missing required object {name!r}")
    return obj


def local_birth_date(chart: CalculatedChart) -> date:
    """The chart's *local* calendar date (what a re-cast keeps fixed)."""
    dt_info = chart.datetime
    if dt_info.local_datetime is not None:
        return dt_info.local_datetime.date()
    tz = chart.location.timezone or "UTC"
    return dt_info.utc_datetime.astimezone(ZoneInfo(tz)).date()


def recast(chart: CalculatedChart, hour: int, minute: int) -> CalculatedChart:
    """A full re-cast of this birth date + place at the given local ``hour:minute``."""
    # Lazy import to avoid any package-init import cycle.
    from stellium.core.builder import ChartBuilder
    from stellium.core.native import Native

    d = local_birth_date(chart)
    loc = chart.location
    native = Native(
        f"{d.isoformat()} {hour:02d}:{minute:02d}:00",
        {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "timezone": loc.timezone,
        },
    )
    return ChartBuilder.from_native(native).calculate()


def daylight_fraction(chart: CalculatedChart) -> float:
    """P(day | date, latitude) under a uniform birth time — the geometric prior.

    The fraction of the 24h that the Sun is above the horizon, from the standard
    sunrise hour-angle ``cos H = -tan φ · tan δ`` (φ = latitude, δ = Sun's
    declination). Polar day/night clamp to 1/0. This is the strongest single sect
    signal — longer day ⇒ more likely born by day — and it needs no re-cast.
    """
    sun = chart.get_object("Sun")
    decl = getattr(sun, "declination", 0.0) if sun is not None else 0.0
    lat = chart.location.latitude
    x = -math.tan(math.radians(lat)) * math.tan(math.radians(decl))
    if x <= -1.0:
        return 1.0  # polar day — sun never sets
    if x >= 1.0:
        return 0.0  # polar night — sun never rises
    hour_angle = math.degrees(math.acos(x))  # 0..180
    return hour_angle / 180.0
