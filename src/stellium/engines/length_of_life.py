"""Length of life — hyleg, alcocoden, and the Perso-Arabic years-table (Lilly).

A **computed traditional indicator, not a prediction of actual lifespan.** The
result is deliberately transparent (which hyleg and why, which alcocoden, the
base years, and every modifier itemized) so the reasoning can be inspected.

Design and source attribution: ``docs/development/specs/LENGTH_OF_LIFE_SPEC.md``.
Ptolemy's rival *directional* method (prorogating the hyleg to the anareta) is
not implemented here; requesting ``method="ptolemy"`` raises.
"""

from __future__ import annotations

from stellium.core.models import (
    CalculatedChart,
    HylegResult,
    LengthOfLifeResult,
    YearModifier,
    longitude_to_sign_and_degree,
)
from stellium.core.planetary_years import greater_years, least_years, mean_years
from stellium.engines.almuten import almuten_of_degree
from stellium.engines.dignities import DIGNITIES
from stellium.utils.houses import find_house_for_longitude

_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
_BENEFIC = {"Jupiter", "Venus"}
_MALEFIC = {"Saturn", "Mars"}
_LIGHTS = {"Sun", "Moon"}

# Ptolemy's aphetic ("hylegiacal") houses — where a prorogator can give life.
_HYLEGIACAL = {1, 7, 9, 10, 11}
_ANGULAR = {1, 4, 7, 10}
_SUCCEDENT = {2, 5, 8, 11}

# Whole-sign ("beholding") aspects by sign distance; 1 & 5 signs = aversion.
# Used for the alcocoden's *beholding* of the hyleg (a sign relationship).
_ASPECTS = {0: "conjunction", 2: "sextile", 3: "square", 4: "trine", 6: "opposition"}
_HARD = {"conjunction", "square", "opposition"}
_SOFT = {"sextile", "trine"}

# Degree-based aspects with traditional moiety orbs — used for the year
# *modifiers* (a planet must actually be in orb to assist/afflict, otherwise
# every planet in an aspecting sign would over-count).
_ASPECT_ANGLES = {
    0: "conjunction",
    60: "sextile",
    90: "square",
    120: "trine",
    180: "opposition",
}
_MOIETY = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mercury": 7.0,
    "Venus": 7.0,
    "Mars": 8.0,
    "Jupiter": 9.0,
    "Saturn": 9.0,
}

_COMBUSTION_ORB = 8.5


def _require_timed_sect(chart: CalculatedChart) -> str:
    if chart.is_time_unknown:
        raise ValueError(
            "Length of life requires a known birth time (it needs houses, "
            "angles, and sect)."
        )
    sect = chart.sect
    if sect not in ("day", "night"):
        raise ValueError("Could not determine chart sect (day/night).")
    return sect


def _whole_sign_aspect(lon_a: float, lon_b: float) -> str | None:
    """The whole-sign aspect between two longitudes, or None (aversion)."""
    d = abs(int(lon_a // 30) - int(lon_b // 30)) % 12
    return _ASPECTS.get(min(d, 12 - d))


def _orb_aspect(lon_a: float, lon_b: float, planet_a: str, planet_b: str) -> str | None:
    """The degree-based aspect between two planets within their moiety orb.

    Orb = half the sum of the two bodies' traditional moieties (Lilly).
    """
    sep = abs((lon_a - lon_b + 180) % 360 - 180)  # 0..180
    orb = (_MOIETY[planet_a] + _MOIETY[planet_b]) / 2
    for angle, name in _ASPECT_ANGLES.items():
        if abs(sep - angle) <= orb:
            return name
    return None


def _prenatal_syzygy_longitude(chart: CalculatedChart) -> float:
    """Longitude of the New/Full Moon immediately before birth.

    Uses the more recent of the preceding new and full moons. Simplification:
    the Full-Moon "luminary above the horizon" refinement is not applied — the
    Moon's degree at the syzygy is used for both.
    """
    from stellium.engines.search import _find_lunation

    jd = chart.datetime.julian_day
    prior = [
        r
        for r in (
            _find_lunation(jd, "new", direction="backward"),
            _find_lunation(jd, "full", direction="backward"),
        )
        if r is not None
    ]
    if not prior:
        return chart.get_object("Moon").longitude  # pragma: no cover
    _jd, _sun_lon, moon_lon = max(prior, key=lambda r: r[0])
    return moon_lon


def find_hyleg(chart: CalculatedChart, method: str = "lilly") -> HylegResult:
    """Find the hyleg (prorogator / giver of life).

    Candidates are tested in a sect-ordered priority list; the first sitting in
    a hylegiacal (aphetic) place wins. The Ascendant is a guaranteed backstop
    (it always occupies house 1). Whole-house place membership is used (the
    degree-based Ptolemaic boundaries are a documented future refinement).

    Args:
        chart: A timed chart.
        method: Authority method (``"lilly"`` only for now).

    Returns:
        A :class:`HylegResult` with a full candidacy trace.
    """
    if method != "lilly":
        raise ValueError(f"Unknown hyleg method {method!r}; only 'lilly' is supported.")

    sect = _require_timed_sect(chart)
    cusps = chart.get_houses().cusps
    asc = next(a.longitude for a in chart.get_angles() if a.name == "ASC")
    sun = chart.get_object("Sun").longitude
    moon = chart.get_object("Moon").longitude
    fortune = (asc + moon - sun) % 360 if sect == "day" else (asc + sun - moon) % 360
    syzygy = _prenatal_syzygy_longitude(chart)

    lights = [("Sun", sun), ("Moon", moon)]
    if sect == "night":
        lights.reverse()
    candidates = [
        *lights,
        ("Fortune", fortune),
        ("Syzygy", syzygy),
        ("Ascendant", asc),  # backstop — always in house 1
    ]

    trace: list[tuple[str, bool]] = []
    for name, lon in candidates:
        place = find_house_for_longitude(lon, cusps)
        qualified = place in _HYLEGIACAL
        trace.append((name, qualified))
        if qualified:
            return HylegResult(
                point=name,
                longitude=lon,
                place=place,
                method=method,
                candidates_tried=tuple(trace),
            )
    # Unreachable: the Ascendant always qualifies.
    raise RuntimeError("No hylegiacal candidate found (unexpected).")


def length_of_life(chart: CalculatedChart, method: str = "lilly") -> LengthOfLifeResult:
    """Estimate the length of life via the Perso-Arabic years table (Lilly).

    A computed traditional indicator, **not** a prediction of actual lifespan.

    Args:
        chart: A timed chart.
        method: ``"lilly"`` (default). ``"ptolemy"`` (directional) is reserved
            but not implemented.

    Returns:
        A :class:`LengthOfLifeResult` whose ``modifiers`` deltas sum, with
        ``base_years``, into ``total``.
    """
    if method == "ptolemy":
        raise NotImplementedError(
            "Ptolemy's directional length-of-life method is not implemented; "
            "see docs/development/specs/LENGTH_OF_LIFE_SPEC.md."
        )
    if method != "lilly":
        raise ValueError(f"Unknown method {method!r}; only 'lilly' is supported.")

    sect = _require_timed_sect(chart)
    cusps = chart.get_houses().cusps
    hyleg = find_hyleg(chart, method)
    notes: list[str] = []

    # Alcocoden = almuten of the hyleg's degree that also beholds the hyleg.
    almuten = almuten_of_degree(hyleg.longitude, sect)
    alcocoden = ""
    for planet, score in sorted(almuten.scores.items(), key=lambda kv: -kv[1]):
        if score <= 0:
            break
        plon = chart.get_object(planet).longitude
        if _whole_sign_aspect(plon, hyleg.longitude) is not None:
            alcocoden = planet
            break
    if not alcocoden:
        alcocoden = almuten.winner
        notes.append(
            f"No dignity ruler of the hyleg beholds it; using the almuten "
            f"{alcocoden} regardless."
        )

    # Base years by the alcocoden's angularity.
    alco_lon = chart.get_object(alcocoden).longitude
    alco_house = find_house_for_longitude(alco_lon, cusps)
    if alco_house in _ANGULAR:
        angularity, family, base = "angular", "greater", float(greater_years(alcocoden))
    elif alco_house in _SUCCEDENT:
        angularity, family, base = "succedent", "mean", float(mean_years(alcocoden))
    else:
        angularity, family, base = "cadent", "least", float(least_years(alcocoden))

    # Combustion is computed up front so the Sun's aspect isn't also charged as
    # a subtraction (combustion is the effect; it converts the unit).
    sun_lon = chart.get_object("Sun").longitude
    combust = (
        alcocoden != "Sun"
        and abs((alco_lon - sun_lon + 180) % 360 - 180) < _COMBUSTION_ORB
    )

    # Aspect modifiers (Lilly), each within traditional moiety orb: benefics
    # add, malefics (hard) subtract, the lights add by soft / subtract by hard,
    # Mercury adds by soft.
    modifiers: list[YearModifier] = []
    for p in _PLANETS:
        if p == alcocoden:
            continue
        if p == "Sun" and combust:
            continue  # handled as combustion (unit change), not a subtraction
        asp = _orb_aspect(chart.get_object(p).longitude, alco_lon, p, alcocoden)
        if asp is None:
            continue
        ly = float(least_years(p))
        if p in _BENEFIC:
            modifiers.append(YearModifier(p, f"benefic {asp} to alcocoden", ly))
        elif p in _MALEFIC and asp in _HARD:
            modifiers.append(YearModifier(p, f"malefic {asp} to alcocoden", -ly))
        elif p in _LIGHTS and asp in _SOFT:
            modifiers.append(YearModifier(p, f"{p} {asp} to alcocoden", ly))
        elif p in _LIGHTS and asp in _HARD:
            modifiers.append(YearModifier(p, f"{p} {asp} to alcocoden", -ly))
        elif p == "Mercury" and asp in _SOFT:
            modifiers.append(YearModifier(p, f"Mercury {asp} to alcocoden", ly))

    running = base + sum(m.delta for m in modifiers)

    # Alcocoden in fall or retrograde halves the years.
    sign, _deg = longitude_to_sign_and_degree(alco_lon)
    in_fall = DIGNITIES[sign]["traditional"].get("fall") == alcocoden
    retrograde = bool(getattr(chart.get_object(alcocoden), "is_retrograde", False))
    if in_fall or retrograde:
        why = "in fall" if in_fall else "retrograde"
        halved = -running / 2
        modifiers.append(
            YearModifier(alcocoden, f"alcocoden {why} (years halved)", halved)
        )
        running += halved

    # Heavy affliction can drive the arithmetic below zero; the indicated years
    # are then "exhausted" — floor at 0 (as an itemized adjustment so
    # base + modifiers still sums to total) rather than report a negative.
    if running < 0:
        modifiers.append(
            YearModifier(
                alcocoden,
                "indicated years floored at 0 (heavy affliction)",
                -running,
            )
        )
        notes.append(
            "Modifiers reduced the indicated years below zero — a heavily "
            "afflicted alcocoden signifies a very short indicated life; floored at 0."
        )
        running = 0.0

    # Combust alcocoden -> the count is in months, not years.
    unit = "months" if combust else "years"
    if combust:
        notes.append(
            f"Alcocoden {alcocoden} is combust (within {_COMBUSTION_ORB}° of the "
            "Sun): the count is in months, not years."
        )

    return LengthOfLifeResult(
        hyleg=hyleg,
        alcocoden=alcocoden,
        alcocoden_angularity=angularity,
        base_years=base,
        base_family=family,
        modifiers=tuple(modifiers),
        total=running,
        unit=unit,
        method=method,
        notes=tuple(notes),
    )
