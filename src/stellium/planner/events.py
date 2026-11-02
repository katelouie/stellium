"""
DailyEventCollector - Gather astrological events for planner pages.

This module collects and organizes transits, ingresses, stations,
Moon phases, and VOC periods for each day of the planner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Literal

import pytz

from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    ECLIPTIC_ASPECT_REGISTRY,
)
from stellium.engines.dignities import DIGNITIES
from stellium.planner.almanac import (
    TransitHit,
    find_natal_transits,
    search_failed,
    utc_window,
)

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart


# Glyphs are *derived* from the registries rather than hand-maintained here. This
# module used to carry its own three hardcoded copies — which is how the planner's
# legend and the report could drift apart, and how any body outside the hardcoded
# dozen (an asteroid, a lot) silently rendered as a bare letter.
PLANET_GLYPHS: dict[str, str] = {
    name: info.glyph for name, info in CELESTIAL_REGISTRY.items() if info.glyph
}
# The angles have no registry glyph; astrologers write them as letters anyway.
PLANET_GLYPHS.setdefault("ASC", "AC")
PLANET_GLYPHS.setdefault("MC", "MC")

# Moon phases, from the bundled fonts. NOT the emoji moons (🌑🌓🌗): Typst renders
# with system fonts switched off, and only 🌕 exists in any font we ship, so a New
# Moon printed as an empty box. Lit is white, dark is black, as on a calendar.
MOON_PHASE_GLYPHS: dict[str, str] = {
    "new": "●",  # ●
    "first_quarter": "◐",  # ◐ — right half lit (northern hemisphere)
    "full": "○",  # ○
    "last_quarter": "◑",  # ◑ — left half lit
}

MOON_PHASE_NAMES: dict[str, str] = {
    "new": "New Moon",
    "first_quarter": "First Quarter Moon",
    "full": "Full Moon",
    "last_quarter": "Last Quarter Moon",
}

# The registry's sign symbols carry a U+FE0E text-presentation selector. That is
# right for a standalone glyph, but these get concatenated into dense one-line
# calendar entries, so strip it and keep the bare codepoint.
SIGN_GLYPHS: dict[str, str] = {
    sign: data["symbol"].replace("︎", "")
    for sign, data in DIGNITIES.items()
    if data.get("symbol")
}

# Keyed by name — the unambiguous key. Anything reading an aspect semantically
# (the legend, the almanac) should use this.
ASPECT_GLYPHS_BY_NAME: dict[str, str] = {
    info.name: info.glyph for info in ASPECT_REGISTRY.values() if info.glyph
}

# Keyed by exact angle, because that is the unit the longitude-crossing search
# works in. Built over the *ecliptic* view: angle is only a unique key there, since
# declination aspects are recorded at 0°/180° by analogy with Conjunction and
# Opposition and would otherwise overwrite them.
ASPECT_GLYPHS: dict[int, str] = {
    int(info.angle): info.glyph
    for info in ECLIPTIC_ASPECT_REGISTRY.values()
    if info.glyph
}

# Default planets for natal transits (all 10 planets + Node + Chiron)
DEFAULT_TRANSIT_PLANETS = [
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
    "True Node",
    "Chiron",
]

# Bodies paired up for mundane (planet-to-planet) transits.
DEFAULT_MUNDANE_PLANETS = [
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

# angle -> name, for describing a mundane aspect in words.
ASPECT_GLYPHS_BY_NAME_INV: dict[int, str] = {
    int(info.angle): info.name
    for info in ECLIPTIC_ASPECT_REGISTRY.values()
    if info.glyph
}

# Default planets for stations
DEFAULT_STATION_PLANETS = [
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "Chiron",
]

# Reader-facing names for natal points whose chart names are terse.
_POINT_LABELS: dict[str, str] = {
    "ASC": "Ascendant",
    "MC": "Midheaven",
    "True Node": "North Node",
}


def _point_label(name: str) -> str:
    return _POINT_LABELS.get(name, name)


@dataclass(frozen=True)
class DailyEvent:
    """
    A single astrological event for display in the planner.

    Attributes:
        time: Event time in the user's timezone
        event_type: Category of event
        description: Human-readable description
        symbol: Glyph representation for compact display
        priority: Sorting priority (1=highest, 5=lowest)
        event_class: How the reader should *weight* this event (see below)
    """

    time: datetime
    event_type: Literal[
        "transit_natal",  # Transit to natal planet
        "transit_mundane",  # Planet-to-planet in sky
        "ingress",  # Planet enters sign
        "station",  # Retrograde or direct station
        "moon_phase",  # New, full, quarter moons
        "voc_start",  # VOC begins
        "voc_end",  # VOC ends (Moon ingress)
        "eclipse",  # Solar or lunar eclipse
    ]
    description: str
    symbol: str
    priority: int = 3

    # A packed day is unreadable when every line is the same ink. `event_type`
    # says *what happened*; `event_class` says *how much it is about you*, which
    # is what the eye needs to triage a cell at a glance:
    #
    #   natal    — touches your natal chart. The reason you own this planner.
    #   notable  — a landmark in the sky itself (eclipse, station, lunation).
    #   lunar    — the Moon's own housekeeping (ingresses, void-of-course).
    #              Frequent and low-stakes, so it should recede.
    #   mundane  — everything else happening in the sky.
    #
    # Renderers key a colour off this. Set at collection time, because the
    # collector is the only place that knows without guessing.
    event_class: Literal["natal", "notable", "lunar", "mundane"] = "mundane"

    def __lt__(self, other: DailyEvent) -> bool:
        """Sort by time, then priority."""
        if self.time != other.time:
            return self.time < other.time
        return self.priority < other.priority


@dataclass
class DailyEventCollector:
    """
    Collects all astrological events for a date range.

    This class gathers events from various sources (transits, ingresses,
    stations, Moon phases, VOC periods) and organizes them by date.

    Example:
        >>> collector = DailyEventCollector(
        ...     natal_chart=chart,
        ...     start=date(2025, 1, 1),
        ...     end=date(2025, 12, 31),
        ...     timezone="America/Los_Angeles"
        ... )
        >>> collector.collect_all()
        >>> events = collector.get_events_for_day(date(2025, 1, 15))
    """

    natal_chart: CalculatedChart
    start: date
    end: date
    timezone: str

    # Internal storage
    _events: list[DailyEvent] = field(default_factory=list, init=False)
    _events_by_date: dict[date, list[DailyEvent]] = field(
        default_factory=dict, init=False
    )
    _tz: pytz.BaseTzInfo = field(init=False)

    def __post_init__(self) -> None:
        """Initialize timezone."""
        self._tz = pytz.timezone(self.timezone)

    def _utc_to_local(self, utc_dt: datetime) -> datetime:
        """Convert UTC datetime to local timezone."""
        if utc_dt.tzinfo is None:
            utc_dt = pytz.UTC.localize(utc_dt)
        return utc_dt.astimezone(self._tz)

    def _jd_to_local(self, jd: float) -> datetime:
        """Convert Julian Day to local datetime."""
        from stellium.engines.search import _julian_day_to_datetime

        utc_dt = _julian_day_to_datetime(jd)
        return self._utc_to_local(utc_dt)

    def _add_event(self, event: DailyEvent) -> None:
        """Add an event to the collection."""
        self._events.append(event)

    def _window(self) -> tuple[datetime, datetime]:
        """The planner's local days as the UTC window the searches take."""
        return utc_window(self.start, self.end, self._tz)

    def collect_natal_transits(
        self,
        transit_planets: list[str] | None = None,
        aspects: list[int] | None = None,
        moon_aspects: list[int] | None = None,
        include_points: bool = True,
        known_hits: list[TransitHit] | None = None,
    ) -> None:
        """
        Collect transits from the moving planets to the natal chart.

        Uses longitude crossing search to find when transit planets
        reach aspect positions to fixed natal longitudes.

        Args:
            transit_planets: Which transiting planets (default:
                DEFAULT_TRANSIT_PLANETS — all ten planets, the Node and Chiron)
            aspects: Which aspects to include (default: major Ptolemaic)
            moon_aspects: Aspects to collect for the *transiting Moon* specifically
                (default: conjunctions only). The Moon aspects every natal planet
                every month, so at the full major set it produces ~68% of all natal
                transit lines and drowns the slower, more meaningful hits. Pass
                ``aspects`` here to opt back into the whole set.
            include_points: Also collect transits to the natal angles and Node
            known_hits: Hits already found by ``find_natal_transits`` for this
                range (the renderer runs that search for the year's summary).
                Their transiting planets are not searched again.
        """
        if transit_planets is None:
            transit_planets = DEFAULT_TRANSIT_PLANETS

        if aspects is None:
            aspects = [0, 60, 90, 120, 180]

        if moon_aspects is None:
            moon_aspects = [0]

        hits: list[TransitHit] = []
        reused: set[str] = set()
        if known_hits:
            reused = {h.transit_planet for h in known_hits} & set(transit_planets)
            reused.discard("Moon")  # the Moon gets its own aspect set
            hits.extend(
                h
                for h in known_hits
                if h.transit_planet in reused and h.aspect_angle in aspects
            )

        def search(planets: list[str], angles: list[int]) -> None:
            if planets and angles:
                hits.extend(
                    find_natal_transits(
                        self.natal_chart,
                        self.start,
                        self.end,
                        self.timezone,
                        transit_planets=planets,
                        aspects=angles,
                        include_points=include_points,
                    )
                )

        search([p for p in transit_planets if p != "Moon" and p not in reused], aspects)
        if "Moon" in transit_planets:
            search(["Moon"], moon_aspects)

        for hit in hits:
            aspect_glyph = ASPECT_GLYPHS.get(hit.aspect_angle, "?")
            transit_glyph = PLANET_GLYPHS.get(
                hit.transit_planet, hit.transit_planet[:2]
            )
            natal_glyph = PLANET_GLYPHS.get(hit.natal_planet, hit.natal_planet[:2])
            natal_label = _point_label(hit.natal_planet)

            self._add_event(
                DailyEvent(
                    time=hit.exact.astimezone(self._tz),
                    event_type="transit_natal",
                    event_class="natal",
                    description=(
                        f"{hit.transit_planet} {hit.aspect_name.lower()} "
                        f"natal {natal_label}"
                    ),
                    symbol=f"{transit_glyph}{aspect_glyph}{natal_glyph}(n)",
                    priority=2 if hit.aspect_angle in (0, 90, 180) else 3,
                )
            )

    def collect_mundane_transits(
        self,
        planets: list[str] | None = None,
        aspects: list[int] | None = None,
        moon_aspects: list[int] | None = None,
    ) -> None:
        """Collect exact aspects between transiting planets — the sky's own weather.

        Distinct from natal transits: nobody's chart is involved, this is just what
        the planets are doing to each other. A good almanac shows both, and prints
        them differently, so the reader can tell "this is about me" from "this is
        the background sky".

        Args:
            planets: Bodies to pair up (default: the traditional seven + the outers)
            aspects: Aspects between them (default: major Ptolemaic)
            moon_aspects: Aspects for pairs *involving the Moon* (default:
                conjunctions only). The Moon aspects every other planet several
                times a month — measured over January it was 74 of 108 mundane hits,
                69% of them — and at the full set it would double the calendar and
                bury everything else. Pass ``aspects`` to opt back in.
        """
        from itertools import combinations

        from stellium.engines.search import find_all_aspect_exacts

        if planets is None:
            planets = list(DEFAULT_MUNDANE_PLANETS)
        if aspects is None:
            aspects = [0, 60, 90, 120, 180]
        if moon_aspects is None:
            moon_aspects = [0]

        start_dt, end_dt = self._window()

        for first, second in combinations(planets, 2):
            involves_moon = "Moon" in (first, second)
            pair_aspects = moon_aspects if involves_moon else aspects

            for angle in pair_aspects:
                try:
                    exacts = find_all_aspect_exacts(
                        first, second, float(angle), start_dt, end_dt
                    )
                except Exception as exc:
                    search_failed(f"{first}–{second} aspects", exc)
                    continue

                glyph1 = PLANET_GLYPHS.get(first, first[:2])
                glyph2 = PLANET_GLYPHS.get(second, second[:2])
                aspect_glyph = ASPECT_GLYPHS.get(angle, "")
                aspect_name = ASPECT_GLYPHS_BY_NAME_INV.get(angle, str(angle))

                for exact in exacts:
                    self._add_event(
                        DailyEvent(
                            time=self._jd_to_local(exact.julian_day),
                            event_type="transit_mundane",
                            # The Moon's chatter is the background of the background.
                            event_class="lunar" if involves_moon else "mundane",
                            description=f"{first} {aspect_name.lower()} {second}",
                            symbol=f"{glyph1}{aspect_glyph}{glyph2}",
                            priority=4 if involves_moon else 3,
                        )
                    )

    def collect_ingresses(self, planets: list[str] | None = None) -> None:
        """
        Collect planet sign ingresses.

        Args:
            planets: Which planets to track (default: the transiting bodies).
                NOT every body Stellium knows a glyph for — PLANET_GLYPHS is now
                derived from the registry and covers ~50 objects including fixed
                stars, which have no ingresses worth reporting.
        """
        from stellium.engines.search import find_all_sign_changes

        if planets is None:
            planets = list(DEFAULT_TRANSIT_PLANETS)

        start_dt, end_dt = self._window()

        for planet in planets:
            try:
                ingresses = find_all_sign_changes(planet, start_dt, end_dt)
            except Exception as exc:
                search_failed(f"{planet} ingresses", exc)
                continue
            else:
                for ingress in ingresses:
                    local_time = self._jd_to_local(ingress.julian_day)
                    planet_glyph = PLANET_GLYPHS.get(planet, planet[0])
                    sign_glyph = SIGN_GLYPHS.get(ingress.sign, ingress.sign[:3])

                    # The Moon changes sign every ~2.5 days; that is housekeeping,
                    # not news, so it recedes into the lunar class.
                    is_moon = planet == "Moon"

                    self._add_event(
                        DailyEvent(
                            time=local_time,
                            event_type="ingress",
                            event_class="lunar" if is_moon else "mundane",
                            description=f"{planet} enters {ingress.sign}",
                            symbol=f"{planet_glyph}\u2192{sign_glyph}",  # → arrow
                            priority=4 if is_moon else 2,
                        )
                    )

    def collect_stations(self, planets: list[str] | None = None) -> None:
        """
        Collect retrograde and direct stations.

        Args:
            planets: Which planets to track (default: Mercury-Pluto)
        """
        from stellium.engines.search import find_all_stations

        if planets is None:
            planets = DEFAULT_STATION_PLANETS

        start_dt, end_dt = self._window()

        for planet in planets:
            try:
                stations = find_all_stations(planet, start_dt, end_dt)
            except Exception as exc:
                search_failed(f"{planet} stations", exc)
                continue
            else:
                for station in stations:
                    local_time = self._jd_to_local(station.julian_day)
                    planet_glyph = PLANET_GLYPHS.get(planet, planet[0])

                    if station.station_type == "retrograde":
                        symbol = f"{planet_glyph}\u211e"  # Rx symbol
                        desc = f"{planet} stations retrograde"
                    else:
                        symbol = f"{planet_glyph}D"
                        desc = f"{planet} stations direct"

                    self._add_event(
                        DailyEvent(
                            time=local_time,
                            event_type="station",
                            event_class="notable",
                            description=desc,
                            symbol=symbol,
                            priority=1,  # Stations are important
                        )
                    )

    def collect_moon_phases(self, quarters: bool = True) -> None:
        """Collect New and Full Moons, and (by default) the two quarter Moons.

        Args:
            quarters: Also collect First and Last Quarter Moons. They are the
                Sun–Moon squares, so they are found as exact aspects and told
                apart by elongation (Moon 90° ahead of the Sun is the first).
        """
        from stellium.electional.intervals import _find_all_lunations
        from stellium.engines.search import _datetime_to_julian_day

        start_dt, end_dt = self._window()
        start_jd = _datetime_to_julian_day(start_dt)
        end_jd = _datetime_to_julian_day(end_dt)

        moments: list[tuple[str, float]] = []
        for phase in ("new", "full"):
            try:
                moments += [
                    (phase, jd) for jd in _find_all_lunations(start_jd, end_jd, phase)
                ]
            except Exception as exc:
                search_failed(MOON_PHASE_NAMES[phase] + "s", exc)

        if quarters:
            moments += self._quarter_moons(start_dt, end_dt)

        for phase, jd in moments:
            self._add_event(
                DailyEvent(
                    time=self._jd_to_local(jd),
                    event_type="moon_phase",
                    description=MOON_PHASE_NAMES[phase],
                    symbol=MOON_PHASE_GLYPHS[phase],
                    # Quarters are the turn of the lunar week, not a culmination.
                    priority=1 if phase in ("new", "full") else 2,
                    event_class="notable" if phase in ("new", "full") else "lunar",
                )
            )

    def _quarter_moons(
        self, start_dt: datetime, end_dt: datetime
    ) -> list[tuple[str, float]]:
        """First and last quarters: the Sun–Moon squares, sorted by elongation."""
        from stellium.engines.search import (
            SWISS_EPHEMERIS_IDS,
            _get_position_and_speed,
            find_all_aspect_exacts,
        )

        try:
            squares = find_all_aspect_exacts("Sun", "Moon", 90.0, start_dt, end_dt)
        except Exception as exc:
            search_failed("quarter Moons", exc)
            return []

        found = []
        for exact in squares:
            sun, _ = _get_position_and_speed(
                SWISS_EPHEMERIS_IDS["Sun"], exact.julian_day
            )
            moon, _ = _get_position_and_speed(
                SWISS_EPHEMERIS_IDS["Moon"], exact.julian_day
            )
            elongation = (moon - sun) % 360
            phase = "first_quarter" if elongation < 180 else "last_quarter"
            found.append((phase, exact.julian_day))
        return found

    def collect_voc_periods(
        self, mode: Literal["traditional", "modern"] = "traditional"
    ) -> None:
        """
        Collect Void of Course Moon periods.

        Adds both start and end times for each VOC period.

        Args:
            mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)
        """
        from datetime import timedelta

        from stellium.electional.intervals import voc_windows

        # Padded by a few days: voc_windows clips a period at the edge of the
        # search, which printed a fake "VOC ends" at midnight on the day after the
        # range (and could fake a "VOC begins" at its first midnight). A void Moon
        # lasts at most ~2.5 days, so the pad lets every edge period resolve to its
        # real start and end; _in_range then drops whatever falls outside.
        pad = timedelta(days=3)
        start_dt, end_dt = utc_window(self.start - pad, self.end + pad, self._tz)

        # Get VOC windows (these are when Moon IS void)
        try:
            voc_wins = voc_windows(start_dt, end_dt, mode=mode)
        except Exception as exc:
            search_failed("void-of-course Moon periods", exc)
            return

        for win in voc_wins:
            # VOC start
            start_local = self._jd_to_local(win.start_jd)
            self._add_event(
                DailyEvent(
                    time=start_local,
                    event_type="voc_start",
                    event_class="lunar",
                    description="VOC begins",
                    symbol="\u263d\u2205",  # ☽∅ (Moon + empty set)
                    priority=4,
                )
            )

            # VOC end
            end_local = self._jd_to_local(win.end_jd)
            self._add_event(
                DailyEvent(
                    time=end_local,
                    event_type="voc_end",
                    event_class="lunar",
                    description="VOC ends",
                    symbol="\u263d\u2713",  # ☽✓ (Moon + check)
                    priority=4,
                )
            )

    def collect_eclipses(self) -> None:
        """Collect solar and lunar eclipses."""
        from stellium.engines.search import find_all_eclipses

        try:
            eclipses = find_all_eclipses(*self._window())
        except Exception as exc:
            search_failed("eclipses", exc)
            return

        for eclipse in eclipses:
            kind = "Solar" if eclipse.eclipse_type.startswith("solar") else "Lunar"
            # "Total Solar Eclipse", not "Solar Eclipse (solar)": eclipse_type is
            # only ever "solar"/"lunar" — the useful word is the classification.
            detail = (getattr(eclipse, "classification", "") or "").title()
            if kind == "Solar":
                symbol = MOON_PHASE_GLYPHS["new"] + "☉"  # ●☉
            else:
                symbol = MOON_PHASE_GLYPHS["full"] + "☽"  # ○☽

            self._add_event(
                DailyEvent(
                    time=self._jd_to_local(eclipse.julian_day),
                    event_type="eclipse",
                    event_class="notable",
                    description=f"{detail} {kind} Eclipse".strip(),
                    symbol=symbol,
                    priority=1,  # Eclipses are very important
                )
            )

    def _merge_eclipse_lunations(self) -> None:
        """An eclipse *is* its New or Full Moon — print it once, as the eclipse.

        Both collectors find the same moment, so an eclipse day carried "New Moon"
        and "Solar Eclipse" as two lines. Drop the lunation when an eclipse of the
        matching kind sits within a day of it.
        """
        eclipses = [e for e in self._events if e.event_type == "eclipse"]
        if not eclipses:
            return

        def eclipsed(event: DailyEvent) -> bool:
            if event.event_type != "moon_phase":
                return False
            kind = {"New Moon": "Solar", "Full Moon": "Lunar"}.get(event.description)
            return kind is not None and any(
                kind in e.description
                and abs((e.time - event.time).total_seconds()) < 86400
                for e in eclipses
            )

        self._events = [e for e in self._events if not eclipsed(e)]

    def collect_all(
        self,
        natal_transits: bool = True,
        transit_planets: list[str] | None = None,
        moon_natal_aspects: list[int] | None = None,
        natal_points: bool = True,
        known_hits: list[TransitHit] | None = None,
        mundane_transits: bool = False,
        mundane_planets: list[str] | None = None,
        ingresses: bool = True,
        ingress_planets: list[str] | None = None,
        stations: bool = True,
        station_planets: list[str] | None = None,
        moon_phases: bool = True,
        quarter_moons: bool = True,
        voc: bool = True,
        voc_mode: Literal["traditional", "modern"] = "traditional",
        eclipses: bool = True,
    ) -> None:
        """
        Collect all configured event types.

        Args:
            natal_transits: Include transits to natal planets
            transit_planets: Which transiting planets
            moon_natal_aspects: Aspects to collect for the transiting Moon
                (default: conjunctions only — see collect_natal_transits)
            natal_points: Include transits to the natal angles and Node
            known_hits: Pre-computed natal transit hits to reuse
                (see collect_natal_transits)
            mundane_transits: Include planet-to-planet aspects in the sky
            mundane_planets: Which bodies to pair up for those
            ingresses: Include sign ingresses
            ingress_planets: Which planets for ingresses
            stations: Include retrograde/direct stations
            station_planets: Which planets for stations
            moon_phases: Include Moon phases
            quarter_moons: Include the First and Last Quarter Moons too
            voc: Include VOC periods
            voc_mode: VOC calculation mode
            eclipses: Include eclipses
        """
        if natal_transits:
            self.collect_natal_transits(
                transit_planets,
                moon_aspects=moon_natal_aspects,
                include_points=natal_points,
                known_hits=known_hits,
            )

        if mundane_transits:
            self.collect_mundane_transits(planets=mundane_planets)

        if ingresses:
            self.collect_ingresses(ingress_planets)

        if stations:
            self.collect_stations(station_planets)

        if moon_phases:
            self.collect_moon_phases(quarters=quarter_moons)

        if voc:
            self.collect_voc_periods(voc_mode)

        if eclipses:
            self.collect_eclipses()
            self._merge_eclipse_lunations()

        # Only the planner's own local days. Searches that need context past the
        # edges (VOC) run padded, and the rest end exactly at local midnight; this
        # is the one place that enforces the range for all of them.
        self._events = [e for e in self._events if self._in_range(e)]

        # Build the date index
        self._build_date_index()

    def _in_range(self, event: DailyEvent) -> bool:
        return self.start <= event.time.date() <= self.end

    def _build_date_index(self) -> None:
        """Build index of events by date for fast lookup."""
        self._events_by_date.clear()

        for event in sorted(self._events):
            event_date = event.time.date()
            if event_date not in self._events_by_date:
                self._events_by_date[event_date] = []
            self._events_by_date[event_date].append(event)

    def get_events_for_day(self, day: date) -> list[DailyEvent]:
        """
        Get all events for a specific day, sorted by time.

        Args:
            day: The date to get events for

        Returns:
            List of DailyEvent objects, sorted by time then priority
        """
        return self._events_by_date.get(day, [])

    def get_all_events(self) -> list[DailyEvent]:
        """Get all collected events, sorted."""
        return sorted(self._events)
