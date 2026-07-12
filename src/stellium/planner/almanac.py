"""Year-level astrological aggregation — the planner's almanac.

``events.py`` answers *what happens today*: one dated line per event, feeding the
monthly and weekly pages. This module answers the questions those lines provoke.

When a daily page says ``Moon □ natal Mercury``, the reader needs somewhere to
look up *where natal Mercury is*. When it marks an eclipse, they want to know
*which of my houses it fell in*. A planner is an instrument you consult, so the
front matter is a reference section, and these are its contents: who rules the
year, when the retrogrades actually run, where the eclipses land, where the
progressed Moon is walking.

Those are year-scoped facts rather than daily events, so they are aggregated
here. Everything is computed from the engines directly (stations, eclipses,
longitude crossings, profections, releasing) rather than by re-parsing the
human-readable strings in ``DailyEvent`` — the almanac is structured data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import pytz

from stellium.core.models import CalculatedChart

# Aspects the almanac reports, by exact angle.
ASPECT_NAMES: dict[int, str] = {
    0: "Conjunction",
    60: "Sextile",
    90: "Square",
    120: "Trine",
    180: "Opposition",
}

# The slow movers whose transits define a year's shape. Faster bodies produce
# too many hits to be a useful year-level summary (they belong on the daily pages).
YEAR_DEFINING_PLANETS: list[str] = [
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]

RETROGRADE_PLANETS: list[str] = [
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]

# A retrograde can straddle the year boundary, so stations are searched over a
# padded window and the resulting periods are clipped back to the year.
_STATION_PAD_DAYS = 220


@dataclass(frozen=True)
class TransitHit:
    """One exact transit aspect from a moving body to a fixed natal point.

    This is the structured primitive behind both the daily transit lines and the
    year's transit summary, so the underlying search runs once.

    Attributes:
        exact: Local datetime the aspect is exact
        transit_planet: The moving body
        natal_planet: The natal point being aspected
        aspect_angle: Exact angle of the aspect (0, 60, 90, 120, 180)
        aspect_name: Human-readable aspect name
    """

    exact: datetime
    transit_planet: str
    natal_planet: str
    aspect_angle: int
    aspect_name: str


@dataclass(frozen=True)
class EclipseEntry:
    """An eclipse, placed in the native's own houses.

    The house is what makes an eclipse legible to the person holding the planner —
    "a solar eclipse in your 7th" means something a bare date does not.
    """

    date: date
    eclipse_type: str  # "solar" | "lunar"
    detail: str  # e.g. "total", "partial", "annular"
    sign: str
    degree: float
    natal_house: int | None


@dataclass(frozen=True)
class RetrogradePeriod:
    """A retrograde window, clipped to the planner's year.

    ``station_retrograde`` / ``station_direct`` are None when the corresponding
    station falls outside the searched window (i.e. the period runs past the edge
    of the year).
    """

    planet: str
    station_retrograde: date | None
    station_direct: date | None
    starts_before_year: bool
    ends_after_year: bool


@dataclass(frozen=True)
class ProgressedMoonAspect:
    """An exact aspect from the progressed Moon to a natal planet."""

    date: date
    natal_planet: str
    aspect_angle: int
    aspect_name: str


@dataclass(frozen=True)
class ProgressedMoon:
    """The progressed Moon's walk through the planner's year.

    Secondary progression advances one day per year of life, so the progressed
    Moon covers only ~13° in a year — roughly half a sign. It changes sign at most
    once per year, and often not at all. Its dated aspects to natal planets are
    therefore the payload: a handful of real, placeable events.
    """

    start_sign: str
    start_degree: float
    end_sign: str
    end_degree: float
    natal_house: int | None
    ingress_date: date | None
    ingress_sign: str | None
    aspects: tuple[ProgressedMoonAspect, ...]


@dataclass(frozen=True)
class ZRYearPeriod:
    """A zodiacal-releasing period overlapping the planner's year."""

    level: int
    sign: str
    ruler: str
    start: date
    end: date
    is_peak: bool
    is_loosing_bond: bool


@dataclass(frozen=True)
class YearAlmanac:
    """Everything the planner's reference pages need about a single year."""

    start: date
    end: date

    # Who rules the year
    age: int
    profected_house: int
    profected_sign: str
    lord_of_year: str
    lord_natal_sign: str | None
    lord_natal_house: int | None

    solar_return: datetime | None

    eclipses: tuple[EclipseEntry, ...]
    retrogrades: tuple[RetrogradePeriod, ...]
    progressed_moon: ProgressedMoon | None
    transits: tuple[TransitHit, ...]
    zr_periods: tuple[ZRYearPeriod, ...]

    # The sky, annotated with what it touches in the native's chart.
    ingresses: tuple[IngressEntry, ...] = ()
    stations: tuple[StationEntry, ...] = ()
    lunations: tuple[LunationEntry, ...] = ()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def house_for_longitude(chart: CalculatedChart, longitude: float) -> int | None:
    """Which of the chart's houses a given ecliptic longitude falls in.

    ``CalculatedChart.get_house()`` resolves houses for *named* objects only; the
    almanac needs to place arbitrary points (eclipse degrees, the progressed Moon).

    Args:
        chart: The natal chart supplying the house cusps
        longitude: Ecliptic longitude in degrees

    Returns:
        House number 1-12, or None if the chart has no houses
    """
    try:
        houses = chart.get_houses()
    except Exception:
        return None
    if houses is None:
        return None

    lon = longitude % 360
    for house in range(1, 13):
        start = houses.get_cusp(house) % 360
        end = houses.get_cusp(1 if house == 12 else house + 1) % 360
        # A house spans start -> end going forward through the zodiac, and may
        # wrap past 0° Aries.
        span = (end - start) % 360
        offset = (lon - start) % 360
        if span == 0:
            continue
        if offset < span:
            return house
    return None


def _natal_datetime(chart: CalculatedChart) -> datetime:
    """The chart's birth datetime, preferring local time over UTC."""
    return chart.datetime.local_datetime or chart.datetime.utc_datetime


def _sign_of(longitude: float) -> str:
    from stellium.engines.search import _get_sign_from_longitude

    return _get_sign_from_longitude(longitude % 360)


def _degree_in_sign(longitude: float) -> float:
    return (longitude % 360) % 30


def _to_local_date(dt: datetime, tz: pytz.BaseTzInfo) -> date:
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(tz).date()


# ---------------------------------------------------------------------------
# the shared transit primitive
# ---------------------------------------------------------------------------


def find_natal_transits(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    timezone: str,
    transit_planets: list[str] | None = None,
    aspects: list[int] | None = None,
) -> list[TransitHit]:
    """Find every exact transit aspect to natal planets in a date range.

    This is the single search behind both the daily transit lines and the year's
    transit summary — callers should run it once and share the result.

    Args:
        natal_chart: The natal chart whose planets are being transited
        start: First date of the range
        end: Last date of the range
        timezone: IANA timezone for the returned exact times
        transit_planets: Moving bodies to search (default: the year-defining planets)
        aspects: Aspect angles to search (default: the major Ptolemaic set)

    Returns:
        Exact transit hits, sorted by time
    """
    from stellium.engines.search import find_all_longitude_crossings

    if transit_planets is None:
        transit_planets = list(YEAR_DEFINING_PLANETS)
    if aspects is None:
        aspects = [0, 60, 90, 120, 180]

    tz = pytz.timezone(timezone)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    hits: list[TransitHit] = []
    for transit_planet in transit_planets:
        for natal_obj in natal_chart.get_planets():
            natal_lon = natal_obj.longitude

            for angle in aspects:
                if angle == 0:
                    targets = [natal_lon]
                elif angle == 180:
                    targets = [(natal_lon + 180) % 360]
                else:
                    targets = [
                        (natal_lon + angle) % 360,
                        (natal_lon - angle) % 360,
                    ]

                for target in targets:
                    try:
                        crossings = find_all_longitude_crossings(
                            transit_planet, target, start_dt, end_dt
                        )
                    except Exception:
                        continue

                    for crossing in crossings:
                        exact_utc = _jd_to_utc(crossing.julian_day)
                        hits.append(
                            TransitHit(
                                exact=exact_utc.astimezone(tz),
                                transit_planet=transit_planet,
                                natal_planet=natal_obj.name,
                                aspect_angle=angle,
                                aspect_name=ASPECT_NAMES.get(angle, f"{angle}°"),
                            )
                        )

    hits.sort(key=lambda h: h.exact)
    return hits


def _jd_to_utc(julian_day: float) -> datetime:
    from stellium.engines.search import _julian_day_to_datetime

    dt = _julian_day_to_datetime(julian_day)
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt


# ---------------------------------------------------------------------------
# the pieces
# ---------------------------------------------------------------------------


def find_eclipses(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    timezone: str,
) -> list[EclipseEntry]:
    """The year's eclipses, each placed in the native's houses."""
    from stellium.engines.search import find_all_eclipses

    tz = pytz.timezone(timezone)
    entries: list[EclipseEntry] = []

    try:
        eclipses = find_all_eclipses(
            datetime.combine(start, datetime.min.time()),
            datetime.combine(end, datetime.max.time()),
        )
    except Exception:
        return entries

    for eclipse in eclipses:
        # A solar eclipse happens at the Sun/Moon conjunction; a lunar one is read
        # at the Moon's own degree.
        kind = "solar" if eclipse.eclipse_type.startswith("solar") else "lunar"
        longitude = eclipse.sun_longitude if kind == "solar" else eclipse.moon_longitude

        entries.append(
            EclipseEntry(
                date=_to_local_date(eclipse.datetime_utc, tz),
                eclipse_type=kind,
                detail=getattr(eclipse, "classification", ""),
                sign=eclipse.sign,
                degree=_degree_in_sign(longitude),
                natal_house=house_for_longitude(natal_chart, longitude),
            )
        )

    entries.sort(key=lambda e: e.date)
    return entries


def find_retrogrades(
    start: date,
    end: date,
    timezone: str,
    planets: list[str] | None = None,
) -> list[RetrogradePeriod]:
    """The retrograde windows overlapping the year.

    Stations are searched over a padded window so that a retrograde straddling
    January 1st or December 31st is still reported, flagged as running past the
    edge of the year rather than silently truncated.
    """
    from stellium.engines.search import find_all_stations

    if planets is None:
        planets = list(RETROGRADE_PLANETS)

    tz = pytz.timezone(timezone)
    search_start = datetime.combine(
        start - timedelta(days=_STATION_PAD_DAYS), datetime.min.time()
    )
    search_end = datetime.combine(
        end + timedelta(days=_STATION_PAD_DAYS), datetime.max.time()
    )

    periods: list[RetrogradePeriod] = []

    for planet in planets:
        try:
            stations = sorted(
                find_all_stations(planet, search_start, search_end),
                key=lambda s: s.julian_day,
            )
        except Exception:
            continue

        # Pair each retrograde station with the next direct station.
        pending_rx: date | None = None
        for station in stations:
            when = _to_local_date(_jd_to_utc(station.julian_day), tz)

            if station.station_type == "retrograde":
                pending_rx = when
                continue

            # A direct station closes an open retrograde. If we never saw its
            # retrograde station, the period began before the searched window.
            rx_date = pending_rx
            pending_rx = None
            if _overlaps(rx_date, when, start, end):
                periods.append(
                    RetrogradePeriod(
                        planet=planet,
                        station_retrograde=rx_date,
                        station_direct=when,
                        starts_before_year=rx_date is not None and rx_date < start,
                        ends_after_year=when > end,
                    )
                )

        # A retrograde still open at the end of the search window.
        if pending_rx is not None and _overlaps(pending_rx, None, start, end):
            periods.append(
                RetrogradePeriod(
                    planet=planet,
                    station_retrograde=pending_rx,
                    station_direct=None,
                    starts_before_year=pending_rx < start,
                    ends_after_year=True,
                )
            )

    periods.sort(key=lambda p: (p.station_retrograde or start, p.planet))
    return periods


def _overlaps(
    period_start: date | None,
    period_end: date | None,
    start: date,
    end: date,
) -> bool:
    """Whether a (possibly open-ended) period intersects the year."""
    if period_start is not None and period_start > end:
        return False
    if period_end is not None and period_end < start:
        return False
    return True


def find_progressed_moon(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
) -> ProgressedMoon | None:
    """The progressed Moon's path through the year, with its natal aspects.

    Secondary progression maps one day of life to one year, so the progressed Moon
    advances only ~13° across a whole year and is always direct (the Moon never
    retrogrades). That monotonic motion means sign ingresses and exact aspects can
    be found by sampling and interpolating, without a bracketing search.
    """
    from stellium.engines.search import (
        SWISS_EPHEMERIS_IDS,
        _datetime_to_julian_day,
        _get_position_and_speed,
    )
    from stellium.utils.progressions import calculate_progressed_datetime

    natal_dt = _natal_datetime(natal_chart)
    moon_id = SWISS_EPHEMERIS_IDS["Moon"]

    def progressed_longitude(on: date) -> float | None:
        try:
            prog_dt = calculate_progressed_datetime(
                natal_dt, datetime.combine(on, datetime.min.time()), "secondary"
            )
            jd = _datetime_to_julian_day(prog_dt)
            longitude, _speed = _get_position_and_speed(moon_id, jd)
            return longitude % 360
        except Exception:
            return None

    # Daily samples: the progressed Moon moves ~0.036°/day, so a day's resolution
    # is far finer than the ~1° precision a planner date needs.
    samples: list[tuple[date, float]] = []
    cursor = start
    while cursor <= end:
        longitude = progressed_longitude(cursor)
        if longitude is not None:
            samples.append((cursor, longitude))
        cursor += timedelta(days=1)

    if len(samples) < 2:
        return None

    first_date, first_lon = samples[0]
    last_date, last_lon = samples[-1]

    # Sign ingress: the progressed Moon covers ~13°/year, so it crosses at most one
    # sign boundary — but check every step rather than assuming.
    ingress_date: date | None = None
    ingress_sign: str | None = None
    for (_prev_date, prev_lon), (this_date, this_lon) in zip(
        samples, samples[1:], strict=False
    ):
        if _sign_of(prev_lon) != _sign_of(this_lon):
            ingress_date = this_date
            ingress_sign = _sign_of(this_lon)
            break

    # Exact aspects to natal planets, found by watching the aspect's angular
    # separation cross zero between consecutive samples.
    aspects: list[ProgressedMoonAspect] = []
    for natal_obj in natal_chart.get_planets():
        for angle, name in ASPECT_NAMES.items():
            for (_prev_date, prev_lon), (this_date, this_lon) in zip(
                samples, samples[1:], strict=False
            ):
                prev_sep = _signed_aspect_error(prev_lon, natal_obj.longitude, angle)
                this_sep = _signed_aspect_error(this_lon, natal_obj.longitude, angle)
                # A sign change across a small step means the aspect went exact.
                if prev_sep == 0 or (
                    prev_sep < 0 < this_sep or this_sep < 0 < prev_sep
                ):
                    if abs(prev_sep) > 1 or abs(this_sep) > 1:
                        continue  # a wraparound, not a crossing
                    aspects.append(
                        ProgressedMoonAspect(
                            date=this_date,
                            natal_planet=natal_obj.name,
                            aspect_angle=angle,
                            aspect_name=name,
                        )
                    )

    aspects.sort(key=lambda a: a.date)

    return ProgressedMoon(
        start_sign=_sign_of(first_lon),
        start_degree=_degree_in_sign(first_lon),
        end_sign=_sign_of(last_lon),
        end_degree=_degree_in_sign(last_lon),
        natal_house=house_for_longitude(natal_chart, last_lon),
        ingress_date=ingress_date,
        ingress_sign=ingress_sign,
        aspects=tuple(aspects),
    )


def _signed_aspect_error(moving: float, fixed: float, angle: int) -> float:
    """How far a moving body is from exact aspect, signed, in degrees (-180, 180].

    Zero means the aspect is exact. The sign flips as the body passes exactness,
    which is what makes crossings detectable between samples.
    """
    separation = (moving - fixed) % 360
    # An aspect can form on either side of the natal point; take the nearer.
    candidates = [(separation - angle), (separation - (360 - angle))]
    best = min(candidates, key=lambda d: abs(_wrap180(d)))
    return _wrap180(best)


def _wrap180(degrees: float) -> float:
    wrapped = (degrees + 180) % 360 - 180
    return wrapped


def find_zr_year(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    lot: str = "Part of Fortune",
) -> list[ZRYearPeriod]:
    """Zodiacal-releasing periods (L1 and L2) overlapping the planner's year.

    A planner covers one year, so the lifetime view is the wrong scope — what
    matters is which period the native is *in*, and whether a peak or a loosing of
    the bond lands inside these twelve months.

    Requires a chart built with ``ZodiacalReleasingAnalyzer`` for this lot (the
    timeline lives in chart metadata). Returns an empty list if it is absent —
    that is a legitimate "not requested", not an error to swallow.
    """
    timelines = natal_chart.metadata.get("zodiacal_releasing")
    if not timelines or lot not in timelines:
        return []
    timeline = timelines[lot]

    found: list[ZRYearPeriod] = []
    for level in (1, 2):
        for period in timeline.periods.get(level, []):
            p_start = (
                period.start.date()
                if isinstance(period.start, datetime)
                else period.start
            )
            p_end = (
                period.end.date() if isinstance(period.end, datetime) else period.end
            )
            if p_end < start or p_start > end:
                continue
            found.append(
                ZRYearPeriod(
                    level=level,
                    sign=period.sign,
                    ruler=period.ruler,
                    start=p_start,
                    end=p_end,
                    is_peak=bool(period.is_peak),
                    is_loosing_bond=bool(period.is_loosing_bond),
                )
            )

    found.sort(key=lambda p: (p.level, p.start))
    return found


# ---------------------------------------------------------------------------
# the aggregate
# ---------------------------------------------------------------------------


def build_year_almanac(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    timezone: str,
    lot: str = "Part of Fortune",
    transits: list[TransitHit] | None = None,
) -> YearAlmanac:
    """Aggregate a year into the planner's reference structures.

    Args:
        natal_chart: The native's natal chart
        start: First day of the planner's range
        end: Last day of the planner's range
        timezone: IANA timezone the planner is written in
        lot: Lot to release from for the ZR section
        transits: Pre-computed transit hits. The daily event collector runs the
            same search, so pass its result here rather than searching twice.

    Returns:
        The year's almanac
    """
    if transits is None:
        transits = find_natal_transits(natal_chart, start, end, timezone)

    # Who rules the year. Profections advance one sign per year of life, so the
    # profection is taken at the start of the planner's range.
    age = _age_on(natal_chart, start)
    profection = natal_chart.profection(age=age, include_monthly=False)

    lord = profection.ruler
    lord_obj = natal_chart.get_object(lord)

    solar_return = _solar_return_datetime(natal_chart, start, timezone)

    return YearAlmanac(
        start=start,
        end=end,
        age=age,
        profected_house=profection.profected_house,
        profected_sign=profection.profected_sign,
        lord_of_year=lord,
        lord_natal_sign=lord_obj.sign if lord_obj else None,
        lord_natal_house=natal_chart.get_house(lord) if lord_obj else None,
        solar_return=solar_return,
        eclipses=tuple(find_eclipses(natal_chart, start, end, timezone)),
        retrogrades=tuple(find_retrogrades(start, end, timezone)),
        progressed_moon=find_progressed_moon(natal_chart, start, end),
        transits=tuple(transits),
        zr_periods=tuple(find_zr_year(natal_chart, start, end, lot=lot)),
        ingresses=tuple(find_ingresses(start, end, timezone)),
        stations=tuple(find_stations(natal_chart, start, end, timezone)),
        lunations=tuple(find_lunations(natal_chart, start, end, timezone)),
    )


def _age_on(natal_chart: CalculatedChart, on: date) -> int:
    """The native's age (completed years) on a given date."""
    birth = _natal_datetime(natal_chart).date()
    age = on.year - birth.year
    if (on.month, on.day) < (birth.month, birth.day):
        age -= 1
    return max(age, 0)


def _solar_return_datetime(
    natal_chart: CalculatedChart,
    start: date,
    timezone: str,
) -> datetime | None:
    """The solar return falling in the planner's year, if it can be computed."""
    from stellium.returns import ReturnBuilder

    try:
        chart = ReturnBuilder.solar(natal_chart, year=start.year).calculate()
    except Exception:
        return None

    try:
        return _natal_datetime(chart)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# the sky, annotated with what it touches in you
# ---------------------------------------------------------------------------
#
# The organizing idea behind a good almanac: a mundane event is only half the
# story. "New Moon, 21°58' Virgo" is a fact about the sky; "...and it squares your
# natal Saturn" is the reason you are holding the book. So every sky event below
# carries its contacts to the native's chart.

# Contacts are reported tightly — a station or lunation is a moment, not a season,
# so a wide orb would list half the chart.
CONTACT_ORB = 3.0

# Only the inner planets have a retrograde "shadow" worth printing: the outer ones
# spend so long retrograde that the shadow is most of the year.
SHADOW_PLANETS: list[str] = ["Mercury", "Venus", "Mars"]


@dataclass(frozen=True)
class NatalContact:
    """An aspect from a body in the sky to a natal planet, at a given moment."""

    transit_planet: str
    natal_planet: str
    aspect_angle: int
    aspect_name: str
    orb: float


@dataclass(frozen=True)
class IngressEntry:
    """A planet changing sign."""

    date: date
    planet: str
    sign: str
    retrograde: bool


@dataclass(frozen=True)
class StationEntry:
    """A planet turning retrograde or direct, and what it touches in the chart.

    ``shadow_enter`` / ``shadow_exit`` bracket the retrograde: the planet first
    crosses the degree it will later station at, and finally clears the degree it
    stationed direct at. Reported only for the inner planets (see SHADOW_PLANETS).
    """

    date: date
    planet: str
    direction: str  # "retrograde" | "direct"
    degree: float
    sign: str
    natal_contacts: tuple[NatalContact, ...]
    shadow_enter: date | None = None
    shadow_exit: date | None = None


@dataclass(frozen=True)
class LunationEntry:
    """A new or full Moon — placed in the native's houses, with its natal contacts."""

    date: date
    phase: str  # "new" | "full"
    degree: float
    sign: str
    natal_house: int | None
    eclipse: str | None  # e.g. "total solar", None if not an eclipse
    natal_contacts: tuple[NatalContact, ...]


def natal_contacts_at(
    natal_chart: CalculatedChart,
    julian_day: float,
    orb: float = CONTACT_ORB,
    planets: list[str] | None = None,
) -> list[NatalContact]:
    """What the sky is aspecting in the natal chart at a given instant.

    Reads transiting longitudes straight from the ephemeris rather than building a
    whole chart — this is called once per station and lunation, and a chart build
    per event would dominate the planner's runtime.
    """
    from stellium.engines.search import SWISS_EPHEMERIS_IDS, _get_position_and_speed

    if planets is None:
        planets = [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]

    contacts: list[NatalContact] = []
    for transit_planet in planets:
        object_id = SWISS_EPHEMERIS_IDS.get(transit_planet)
        if object_id is None:
            continue
        try:
            longitude, _speed = _get_position_and_speed(object_id, julian_day)
        except Exception:
            continue

        for natal_obj in natal_chart.get_planets():
            for angle, name in ASPECT_NAMES.items():
                error = abs(_signed_aspect_error(longitude, natal_obj.longitude, angle))
                if error <= orb:
                    contacts.append(
                        NatalContact(
                            transit_planet=transit_planet,
                            natal_planet=natal_obj.name,
                            aspect_angle=angle,
                            aspect_name=name,
                            orb=error,
                        )
                    )

    contacts.sort(key=lambda c: c.orb)
    return contacts


def find_ingresses(
    start: date,
    end: date,
    timezone: str,
    planets: list[str] | None = None,
) -> list[IngressEntry]:
    """Every sign change in the range, for the reference page."""
    from stellium.engines.search import find_all_sign_changes

    if planets is None:
        planets = [
            "Sun",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]

    tz = pytz.timezone(timezone)
    entries: list[IngressEntry] = []

    for planet in planets:
        try:
            changes = find_all_sign_changes(
                planet,
                datetime.combine(start, datetime.min.time()),
                datetime.combine(end, datetime.max.time()),
            )
        except Exception:
            continue

        for change in changes:
            entries.append(
                IngressEntry(
                    date=_to_local_date(_jd_to_utc(change.julian_day), tz),
                    planet=planet,
                    sign=change.sign,
                    retrograde=bool(getattr(change, "retrograde", False)),
                )
            )

    entries.sort(key=lambda e: e.date)
    return entries


def find_stations(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    timezone: str,
    planets: list[str] | None = None,
) -> list[StationEntry]:
    """Stations in the range, each with its natal contacts and retrograde shadow.

    Stations are *paired* (retrograde → direct) because the shadow is defined by
    the other end of the retrograde, not by the station itself:

      enters shadow — when the planet first passes the degree it will later
                      station DIRECT at
      leaves shadow — when, after turning direct, it climbs back to the degree it
                      stationed RETROGRADE at

    Using a station's own degree would trivially return the station's own date.
    """
    from stellium.engines.search import find_all_stations

    if planets is None:
        planets = list(RETROGRADE_PLANETS)

    tz = pytz.timezone(timezone)
    entries: list[StationEntry] = []

    # Padded, so a station inside the range can still find its partner outside it.
    search_start = datetime.combine(
        start - timedelta(days=_STATION_PAD_DAYS), datetime.min.time()
    )
    search_end = datetime.combine(
        end + timedelta(days=_STATION_PAD_DAYS), datetime.max.time()
    )

    for planet in planets:
        try:
            stations = sorted(
                find_all_stations(planet, search_start, search_end),
                key=lambda st: st.julian_day,
            )
        except Exception:
            continue

        wants_shadow = planet in SHADOW_PLANETS

        for index, station in enumerate(stations):
            longitude = getattr(station, "longitude", None)
            if longitude is None:
                continue

            when = _to_local_date(_jd_to_utc(station.julian_day), tz)
            if not (start <= when <= end):
                continue  # only report stations inside the planner's range

            shadow_enter: date | None = None
            shadow_exit: date | None = None

            if wants_shadow:
                if station.station_type == "retrograde":
                    partner = _next_station(stations, index, "direct")
                    if partner is not None:
                        shadow_enter = _crossing_near(
                            planet,
                            getattr(partner, "longitude", None),
                            station.julian_day,
                            tz,
                            back=True,
                        )
                else:
                    partner = _previous_station(stations, index, "retrograde")
                    if partner is not None:
                        shadow_exit = _crossing_near(
                            planet,
                            getattr(partner, "longitude", None),
                            station.julian_day,
                            tz,
                            back=False,
                        )

            entries.append(
                StationEntry(
                    date=when,
                    planet=planet,
                    direction=station.station_type,
                    degree=_degree_in_sign(longitude),
                    sign=_sign_of(longitude),
                    natal_contacts=tuple(
                        natal_contacts_at(natal_chart, station.julian_day)
                    ),
                    shadow_enter=shadow_enter,
                    shadow_exit=shadow_exit,
                )
            )

    entries.sort(key=lambda e: e.date)
    return entries


def _next_station(stations: list, index: int, kind: str):
    for station in stations[index + 1 :]:
        if station.station_type == kind:
            return station
    return None


def _previous_station(stations: list, index: int, kind: str):
    for station in reversed(stations[:index]):
        if station.station_type == kind:
            return station
    return None


def _crossing_near(
    planet: str,
    degree: float | None,
    station_jd: float,
    tz: pytz.BaseTzInfo,
    back: bool,
) -> date | None:
    """When the planet last/next passed a given degree, either side of a station."""
    from stellium.engines.search import find_all_longitude_crossings

    if degree is None:
        return None

    station_dt = _jd_to_utc(station_jd).replace(tzinfo=None)
    # An inner-planet retrograde plus its shadow fits comfortably inside ~4 months.
    window = timedelta(days=120)
    lo = station_dt - window if back else station_dt
    hi = station_dt if back else station_dt + window

    try:
        crossings = find_all_longitude_crossings(planet, degree % 360, lo, hi)
    except Exception:
        return None
    if not crossings:
        return None

    # Going back we want the *earliest* pass of that degree; going forward, the last.
    chosen = crossings[0] if back else crossings[-1]
    return _to_local_date(_jd_to_utc(chosen.julian_day), tz)


def find_lunations(
    natal_chart: CalculatedChart,
    start: date,
    end: date,
    timezone: str,
) -> list[LunationEntry]:
    """Every new and full Moon, placed in the native's houses, with natal contacts."""
    from stellium.electional.intervals import _find_all_lunations
    from stellium.engines.search import (
        SWISS_EPHEMERIS_IDS,
        _datetime_to_julian_day,
        _get_position_and_speed,
    )

    tz = pytz.timezone(timezone)
    start_jd = _datetime_to_julian_day(datetime.combine(start, datetime.min.time()))
    end_jd = _datetime_to_julian_day(datetime.combine(end, datetime.max.time()))

    # Eclipses are lunations too; tag them rather than listing them twice.
    eclipses = {e.date: e for e in find_eclipses(natal_chart, start, end, timezone)}

    moon_id = SWISS_EPHEMERIS_IDS["Moon"]
    entries: list[LunationEntry] = []

    for phase in ("new", "full"):
        try:
            moments = _find_all_lunations(start_jd, end_jd, phase)
        except Exception:
            continue

        for jd in moments:
            try:
                longitude, _speed = _get_position_and_speed(moon_id, jd)
            except Exception:
                continue

            when = _to_local_date(_jd_to_utc(jd), tz)
            eclipse = eclipses.get(when)

            entries.append(
                LunationEntry(
                    date=when,
                    phase=phase,
                    degree=_degree_in_sign(longitude),
                    sign=_sign_of(longitude),
                    natal_house=house_for_longitude(natal_chart, longitude),
                    eclipse=(
                        f"{eclipse.detail} {eclipse.eclipse_type}".strip()
                        if eclipse
                        else None
                    ),
                    natal_contacts=tuple(natal_contacts_at(natal_chart, jd)),
                )
            )

    entries.sort(key=lambda e: e.date)
    return entries


# ---------------------------------------------------------------------------
# traditional condition — the chart analysis page
# ---------------------------------------------------------------------------

TRADITIONAL_PLANETS: list[str] = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
]


@dataclass(frozen=True)
class PlanetCondition:
    """A traditional planet, and the rulers of the place it occupies.

    Honeycomb's "chart analysis" is the *inverse* of a dignity score: rather than
    asking what dignities a planet holds, it asks who governs the ground it stands
    on — its domicile, exaltation, bound, triplicity and decan lords. That is the
    raw material for judging condition, and it is what the daily pages' timelord
    notation refers back to.
    """

    planet: str
    sign: str
    degree: float
    house: int | None
    element: str
    modality: str

    domicile_lord: str | None
    exaltation_lord: str | None
    bound_lord: str | None
    triplicity_lords: tuple[str, ...]
    decan_lord: str | None

    dignities: tuple[str, ...]  # dignities this planet itself holds
    score: int
    is_peregrine: bool


@dataclass(frozen=True)
class SectCondition:
    """Who is on side, and who is not.

    Sect is the single most consequential judgement in traditional practice: it
    decides which benefic helps most and which malefic hurts most.
    """

    sect: str  # "day" | "night"
    sect_light: str  # Sun by day, Moon by night
    benefic_of_sect: str
    benefic_contrary: str
    malefic_of_sect: str
    malefic_contrary: str


@dataclass(frozen=True)
class ChartCondition:
    """The traditional condition of a chart."""

    sect: SectCondition
    planets: tuple[PlanetCondition, ...]


def _lord(value: Any) -> str | None:
    """Normalise a ruler name out of the dignity tables.

    `DIGNITIES` records the absence of an exaltation lord as the literal *string*
    ``"None"`` (Aquarius, Leo, Gemini, Scorpio, Sagittarius), so a bare truthiness
    check happily prints "None" as if it were a planet.
    """
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    return text


def _bound_lord(sign: str, degree_in_sign: float) -> str | None:
    """The Egyptian bound lord for a degree of a sign."""
    from stellium.engines.dignities import DIGNITIES

    bounds = DIGNITIES.get(sign, {}).get("bound_egypt") or {}
    lord = None
    for start in sorted(bounds):
        if degree_in_sign >= start:
            lord = bounds[start]
    return lord


def _decan_lord(
    sign: str, degree_in_sign: float, system: str = "chaldean"
) -> str | None:
    """The decan (face) lord — Chaldean order by default, as Honeycomb uses."""
    from stellium.engines.dignities import DIGNITIES

    key = "decan_chaldean" if system == "chaldean" else "decan_trip"
    decans = DIGNITIES.get(sign, {}).get(key) or []
    index = min(int(degree_in_sign // 10), 2)
    return decans[index] if len(decans) > index else None


def find_chart_condition(natal_chart: CalculatedChart) -> ChartCondition:
    """The traditional condition of the natal chart.

    Uses only what Stellium already models — sect, the essential-dignity tables,
    Egyptian bounds and Chaldean decans. It deliberately does NOT attempt
    bonification and maltreatment: those are a further layer of Hellenistic
    doctrine that this library does not model, and inventing them here would be
    dressing a guess up as a judgement.
    """
    from stellium.engines.dignities import DIGNITIES, TraditionalDignityCalculator

    sect = getattr(natal_chart, "sect", None) or "day"
    is_day = sect == "day"

    sect_condition = SectCondition(
        sect=sect,
        sect_light="Sun" if is_day else "Moon",
        benefic_of_sect="Jupiter" if is_day else "Venus",
        benefic_contrary="Venus" if is_day else "Jupiter",
        malefic_of_sect="Saturn" if is_day else "Mars",
        malefic_contrary="Mars" if is_day else "Saturn",
    )

    calculator = TraditionalDignityCalculator()
    conditions: list[PlanetCondition] = []

    for name in TRADITIONAL_PLANETS:
        position = natal_chart.get_object(name)
        if position is None:
            continue

        sign = position.sign
        data = DIGNITIES.get(sign, {})
        traditional = data.get("traditional", {})
        triplicity = data.get("triplicity", {})
        degree_in_sign = _degree_in_sign(position.longitude)

        try:
            dignity = calculator.calculate_dignities(position, sect=sect)
        except Exception:
            dignity = {}

        # Day/night ordering matters: the sect ruler leads, then the other, then
        # the cooperating (participating) ruler.
        if is_day:
            lords = (triplicity.get("day"), triplicity.get("night"))
        else:
            lords = (triplicity.get("night"), triplicity.get("day"))
        triplicity_lords = tuple(
            lord
            for lord in (
                _lord(lords[0]),
                _lord(lords[1]),
                _lord(triplicity.get("coop")),
            )
            if lord
        )

        conditions.append(
            PlanetCondition(
                planet=name,
                sign=sign,
                degree=degree_in_sign,
                house=natal_chart.get_house(name),
                element=data.get("element", ""),
                modality=data.get("modality", ""),
                domicile_lord=_lord(traditional.get("ruler")),
                exaltation_lord=_lord(traditional.get("exaltation")),
                bound_lord=_bound_lord(sign, degree_in_sign),
                triplicity_lords=triplicity_lords,
                decan_lord=_decan_lord(sign, degree_in_sign),
                dignities=tuple(dignity.get("dignities", ())),
                score=int(dignity.get("score", 0) or 0),
                is_peregrine=bool(dignity.get("is_peregrine", False)),
            )
        )

    return ChartCondition(sect=sect_condition, planets=tuple(conditions))
