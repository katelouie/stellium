"""Top-level sect analysis — the compare-hypothesis workbench, as data.

``analyze_sect(chart)`` constructs BOTH the day and night hypotheses from a chart's
birth date + place, derives the sect-dependent structures each implies, anchors them
with the validated daylight × malefic classifier, and returns a renderer-neutral
:class:`SectAnalysis`. It is an *indicator, not an oracle*: sect is only ~70%
recoverable from biography-thin data (the ceiling is truth resolution, not method),
so the result is built to be adjudicated by a human with real knowledge, not trusted
blindly. See ``docs/development/specs/RECTIFICATION_REPORT.md``.

Events/temperament are looked up automatically for notables (by ``chart.metadata``
name) and can be supplied explicitly for anyone.
"""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from stellium.core.models import CalculatedChart
from stellium.rectification._data import dignity_label
from stellium.rectification._recast import daylight_fraction, recast, require_obj
from stellium.rectification.evidence import (
    benefic_tally,
    malefic_tally,
    malefic_temperament_score,
    sect_light_temperament_score,
)
from stellium.rectification.firdaria import FirdariaConvergence, firdaria_convergence
from stellium.rectification.model import calibrated_p_day

SECT_LIGHT = {"day": "Sun", "night": "Moon"}
OUT_OF_SECT_MALEFIC = {"day": "Mars", "night": "Saturn"}
IN_SECT_BENEFIC = {"day": "Jupiter", "night": "Venus"}


@dataclass(frozen=True)
class PlanetCondition:
    """A planet's sign + coarse essential dignity under a given hypothesis."""

    planet: str
    sign: str
    dignity: str  # domicile | exalted | peregrine | fall | detriment


@dataclass(frozen=True)
class Hypothesis:
    """The sect-dependent structures implied by one sect assumption."""

    sect: str  # "day" | "night"
    sect_light: PlanetCondition
    out_of_sect_malefic: PlanetCondition
    in_sect_benefic: PlanetCondition


@dataclass(frozen=True)
class SectAnalysis:
    """The full compare-hypothesis sect picture — renderer-neutral."""

    name: str
    chart_sect: str | None  # sect of the *given* chart (None if undetermined)
    daylight_fraction: float
    p_day: float
    has_events: bool
    has_temperament: bool
    day: Hypothesis
    night: Hypothesis
    moon_band: str | None
    hardship: tuple[float, float] | None  # (mars, saturn) weight
    fortune: tuple[float, float] | None  # (jupiter, venus) weight
    firdaria: FirdariaConvergence | None
    malefic_temper: float | None  # Mars-hot − Saturn-cold (soft)
    sect_light_temper: float | None  # Solar − Lunar (soft)

    @property
    def leans(self) -> str:
        return "day" if self.p_day >= 0.5 else "night"

    @property
    def confidence(self) -> float:
        return max(self.p_day, 1 - self.p_day)

    def technique_votes(self) -> list[tuple[str, str]]:
        """(technique, 'day'|'night') for each technique with a definite lean."""
        votes: list[tuple[str, str]] = []
        votes.append(
            ("daylight prior", "day" if self.daylight_fraction > 0.5 else "night")
        )
        if self.hardship and self.hardship[0] != self.hardship[1]:
            votes.append(
                (
                    "hardship flavour",
                    "day" if self.hardship[0] > self.hardship[1] else "night",
                )
            )
        if self.fortune and self.fortune[0] != self.fortune[1]:
            votes.append(
                (
                    "fortune flavour",
                    "day" if self.fortune[0] > self.fortune[1] else "night",
                )
            )
        if self.firdaria and self.firdaria.favors != "tie":
            votes.append(("firdaria fit", self.firdaria.favors))
        return votes


def _condition(chart: CalculatedChart, planet: str) -> PlanetCondition:
    obj = chart.get_object(planet)
    sign = obj.sign if obj is not None else "?"
    return PlanetCondition(planet, sign, dignity_label(planet, sign) if obj else "?")


def _hypothesis(chart: CalculatedChart, sect: str) -> Hypothesis:
    return Hypothesis(
        sect=sect,
        sect_light=_condition(chart, SECT_LIGHT[sect]),
        out_of_sect_malefic=_condition(chart, OUT_OF_SECT_MALEFIC[sect]),
        in_sect_benefic=_condition(chart, IN_SECT_BENEFIC[sect]),
    )


def _moon_band(day_chart: CalculatedChart, night_chart: CalculatedChart) -> str | None:
    noon = require_obj(day_chart, "Moon").sign
    midnight = require_obj(night_chart, "Moon").sign
    if noon == midnight:
        return None
    return (
        f"Moon crosses {midnight} → {noon} within the 24h — its sign (and anything it "
        "rules) is a band, not a point."
    )


def _auto_events(chart: CalculatedChart) -> tuple:
    name = chart.metadata.get("name")
    if not name:
        return ()
    try:
        from stellium.data import get_notable_life_events

        return get_notable_life_events(name)
    except Exception:
        return ()


def _auto_temperament(chart: CalculatedChart) -> tuple:
    name = chart.metadata.get("name")
    if not name:
        return ()
    try:
        from stellium.data import get_notable_temperament

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # the getter's soft-data warning
            return get_notable_temperament(name)
    except Exception:
        return ()


def analyze_sect(
    chart: CalculatedChart,
    *,
    events: Iterable | None = None,
    temperament: Iterable | None = None,
) -> SectAnalysis:
    """Build the compare-hypothesis sect analysis for ``chart``.

    Args:
        chart: the natal chart (any assumed time; both hypotheses are re-cast from
            its birth date + place).
        events: life events to weigh; if ``None``, auto-looked-up for notables.
            Pass ``()`` to force the geometry-only analysis.
        temperament: soft character traits; if ``None``, auto-looked-up for notables.

    Returns:
        A :class:`SectAnalysis` (indicator, not oracle).
    """
    ev: Sequence = list(events) if events is not None else list(_auto_events(chart))
    tp: Sequence = (
        list(temperament) if temperament is not None else list(_auto_temperament(chart))
    )

    day_chart = recast(chart, 12, 0)
    night_chart = recast(chart, 0, 0)

    p_day = calibrated_p_day(chart, ev)
    name = chart.metadata.get("name") or "this chart"

    hardship = malefic_tally(ev) if ev else None
    fortune = benefic_tally(ev) if ev else None
    fird = firdaria_convergence(chart, ev) if ev else None
    mal_temper = malefic_temperament_score(tp) if tp else None
    light_temper = sect_light_temperament_score(tp) if tp else None

    return SectAnalysis(
        name=name,
        chart_sect=chart.sect,
        daylight_fraction=daylight_fraction(chart),
        p_day=p_day,
        has_events=bool(ev),
        has_temperament=bool(tp),
        day=_hypothesis(day_chart, "day"),
        night=_hypothesis(night_chart, "night"),
        moon_band=_moon_band(day_chart, night_chart),
        hardship=hardship,
        fortune=fortune,
        firdaria=fird,
        malefic_temper=mal_temper,
        sect_light_temper=light_temper,
    )
