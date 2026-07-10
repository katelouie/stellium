"""Firdaria time-lord engine (Persian planetary periods).

Firdaria assigns fixed-length chunks of life to the planets (and lunar nodes) in
a sect-determined order, each major period subdividing into seven sub-periods.
Period values and orders come from ``stellium.core.planetary_years``; the design
and source attribution are in
``docs/development/specs/HELLENISTIC_PERIODS_SPEC.md``.

The one genuine scholarly fork — where the nodes fall in *nocturnal* charts — is
exposed as a preset: ``abu_mashar`` (default; nodes at the end in both sects) vs.
``bonatti`` (nocturnal nodes after Mars).
"""

from __future__ import annotations

import datetime as dt

from stellium.core.models import (
    CalculatedChart,
    FirdariaPeriod,
    FirdariaTimeline,
)
from stellium.core.planetary_years import (
    FIRDARIA_YEARS,
    firdaria_order,
    subperiod_order,
)

_NODES = ("North Node", "South Node")

# preset -> (include nodes?, nocturnal node placement)
_PRESETS: dict[str, dict[str, object]] = {
    "abu_mashar": {"nodes": True, "nocturnal_nodes": "end"},
    "al_biruni": {"nodes": True, "nocturnal_nodes": "end"},  # alias of default
    "bonatti": {"nodes": True, "nocturnal_nodes": "after_mars"},
    "no_nodes": {"nodes": False, "nocturnal_nodes": "end"},
}


class FirdariaEngine:
    """Calculate a Firdaria timeline for a chart.

    The defaults are the **Abu Ma'shar / Persian** configuration — the fullest,
    earliest primary source and the dominant modern-scholarly reading: nodes at
    the end in both sects, seven equal sub-periods in Chaldean order from the
    major ruler, node majors not subdivided, the sequence repeating past 75
    years, and a real (365.2425-day) solar year.
    """

    def __init__(
        self,
        chart: CalculatedChart,
        *,
        preset: str = "abu_mashar",
        year_length: float = 365.2425,
        repeat: bool = True,
        max_age: float = 96.0,
    ) -> None:
        if preset not in _PRESETS:
            raise ValueError(
                f"Unknown Firdaria preset {preset!r}; choose from {sorted(_PRESETS)}."
            )
        self.chart = chart
        self.preset = preset
        self._cfg = _PRESETS[preset]
        self.year_length = year_length
        self.repeat = repeat
        self.max_age = max_age

    def _sect(self) -> str:
        # A noon-normalized unknown-time chart would report a bogus "day" sect,
        # so refuse explicitly rather than trusting the derived value.
        if self.chart.is_time_unknown:
            raise ValueError(
                "Firdaria requires a known birth time; this chart's time is "
                "unknown (sect cannot be determined, and it is decisive here)."
            )
        sect = self.chart.sect
        if sect not in ("day", "night"):
            raise ValueError(
                "Firdaria requires a known birth time: the chart's sect "
                "(day/night) could not be determined."
            )
        return sect

    def _major_order(self, sect: str) -> list[str]:
        """The full major-period order for a sect, nodes placed per preset."""
        order = firdaria_order(sect)  # the seven planets
        if not self._cfg["nodes"]:
            return order
        if sect == "night" and self._cfg["nocturnal_nodes"] == "after_mars":
            idx = order.index("Mars")
            return order[: idx + 1] + list(_NODES) + order[idx + 1 :]
        # Default: nodes at the end (both sects; day charts are always end).
        return order + list(_NODES)

    def calculate(self) -> FirdariaTimeline:
        """Build the full timeline out to ``max_age``."""
        sect = self._sect()
        order = self._major_order(sect)
        birth = self.chart.datetime.utc_datetime

        majors: list[FirdariaPeriod] = []
        subs: list[FirdariaPeriod] = []

        age = 0.0
        count = 0
        n = len(order)
        while age < self.max_age:
            if not self.repeat and count >= n:
                break
            ruler = order[count % n]
            count += 1

            years = FIRDARIA_YEARS[ruler]
            start_age, end_age = age, age + years
            majors.append(
                FirdariaPeriod(
                    ruler=ruler,
                    sub_ruler=None,
                    level=1,
                    start=self._at_age(birth, start_age),
                    end=self._at_age(birth, end_age),
                    start_age=start_age,
                    end_age=end_age,
                )
            )

            # Node majors do not subdivide; planets get seven equal sub-periods.
            if ruler not in _NODES:
                sub_len = years / 7
                for j, sub_ruler in enumerate(subperiod_order(ruler)):
                    s_start_age = start_age + j * sub_len
                    s_end_age = start_age + (j + 1) * sub_len
                    subs.append(
                        FirdariaPeriod(
                            ruler=ruler,
                            sub_ruler=sub_ruler,
                            level=2,
                            start=self._at_age(birth, s_start_age),
                            end=self._at_age(birth, s_end_age),
                            start_age=s_start_age,
                            end_age=s_end_age,
                        )
                    )

            age = end_age

        return FirdariaTimeline(
            sect=sect,
            birth=birth,
            periods=tuple(majors + subs),
            preset=self.preset,
        )

    def _at_age(self, birth: dt.datetime, age: float) -> dt.datetime:
        return birth + dt.timedelta(days=age * self.year_length)
