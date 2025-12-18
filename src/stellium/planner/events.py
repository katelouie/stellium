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

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart


# Planet glyphs for display
PLANET_GLYPHS = {
    "Sun": "\u2609",  # ☉
    "Moon": "\u263d",  # ☽
    "Mercury": "\u263f",  # ☿
    "Venus": "\u2640",  # ♀
    "Mars": "\u2642",  # ♂
    "Jupiter": "\u2643",  # ♃
    "Saturn": "\u2644",  # ♄
    "Uranus": "\u2645",  # ♅
    "Neptune": "\u2646",  # ♆
    "Pluto": "\u2647",  # ♇
    "True Node": "\u260a",  # ☊
    "Chiron": "\u26b7",  # ⚷
}

# Aspect glyphs
ASPECT_GLYPHS = {
    0: "\u260c",  # ☌ conjunction
    60: "\u26b9",  # ⚹ sextile
    90: "\u25a1",  # □ square
    120: "\u25b3",  # △ trine
    180: "\u260d",  # ☍ opposition
}

# Sign glyphs
SIGN_GLYPHS = {
    "Aries": "\u2648",
    "Taurus": "\u2649",
    "Gemini": "\u264a",
    "Cancer": "\u264b",
    "Leo": "\u264c",
    "Virgo": "\u264d",
    "Libra": "\u264e",
    "Scorpio": "\u264f",
    "Sagittarius": "\u2650",
    "Capricorn": "\u2651",
    "Aquarius": "\u2652",
    "Pisces": "\u2653",
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

    def collect_natal_transits(
        self,
        transit_planets: list[str] | None = None,
        aspects: list[int] | None = None,
    ) -> None:
        """
        Collect transits from outer planets to natal planets.

        Uses longitude crossing search to find when transit planets
        reach aspect positions to fixed natal planet longitudes.

        Args:
            transit_planets: Which transiting planets (default: Jupiter-Pluto)
            aspects: Which aspects to include (default: major Ptolemaic)
        """
        from stellium.engines.search import find_all_longitude_crossings

        if transit_planets is None:
            transit_planets = DEFAULT_TRANSIT_PLANETS

        if aspects is None:
            aspects = [0, 60, 90, 120, 180]

        # Get start/end as datetime for search functions
        start_dt = datetime.combine(self.start, datetime.min.time())
        end_dt = datetime.combine(self.end, datetime.max.time())

        # Get natal planet positions
        natal_planets = self.natal_chart.get_planets()

        for transit_planet in transit_planets:
            for natal_obj in natal_planets:
                natal_name = natal_obj.name
                natal_lon = natal_obj.longitude

                for aspect_angle in aspects:
                    # Calculate target longitude(s) for this aspect
                    # For most aspects, there's one target
                    # For non-conjunction/opposition, the aspect can form from either side
                    if aspect_angle == 0:
                        # Conjunction: transit crosses natal longitude
                        target_lons = [natal_lon]
                    elif aspect_angle == 180:
                        # Opposition: transit crosses opposite point
                        target_lons = [(natal_lon + 180) % 360]
                    else:
                        # Other aspects: can form from either direction
                        target_lons = [
                            (natal_lon + aspect_angle) % 360,
                            (natal_lon - aspect_angle) % 360,
                        ]

                    for target_lon in target_lons:
                        try:
                            crossings = find_all_longitude_crossings(
                                transit_planet,
                                target_lon,
                                start_dt,
                                end_dt,
                            )

                            for crossing in crossings:
                                local_time = self._utc_to_local(crossing.datetime_utc)
                                aspect_glyph = ASPECT_GLYPHS.get(aspect_angle, "?")
                                transit_glyph = PLANET_GLYPHS.get(
                                    transit_planet, transit_planet[0]
                                )
                                natal_glyph = PLANET_GLYPHS.get(
                                    natal_name, natal_name[0]
                                )

                                # Priority based on aspect type
                                priority = 2 if aspect_angle in [0, 90, 180] else 3

                                self._add_event(
                                    DailyEvent(
                                        time=local_time,
                                        event_type="transit_natal",
                                        description=f"{transit_planet} {aspect_glyph} natal {natal_name}",
                                        symbol=f"{transit_glyph}{aspect_glyph}{natal_glyph}(n)",
                                        priority=priority,
                                    )
                                )
                        except Exception:
                            # Skip if search fails (e.g., missing ephemeris)
                            pass

    def collect_ingresses(self, planets: list[str] | None = None) -> None:
        """
        Collect planet sign ingresses.

        Args:
            planets: Which planets to track (default: all)
        """
        from stellium.engines.search import find_all_sign_changes

        if planets is None:
            planets = list(PLANET_GLYPHS.keys())

        start_dt = datetime.combine(self.start, datetime.min.time())
        end_dt = datetime.combine(self.end, datetime.max.time())

        for planet in planets:
            try:
                ingresses = find_all_sign_changes(planet, start_dt, end_dt)

                for ingress in ingresses:
                    local_time = self._jd_to_local(ingress.julian_day)
                    planet_glyph = PLANET_GLYPHS.get(planet, planet[0])
                    sign_glyph = SIGN_GLYPHS.get(ingress.sign, ingress.sign[:3])

                    # Moon ingresses are lower priority
                    priority = 4 if planet == "Moon" else 2

                    self._add_event(
                        DailyEvent(
                            time=local_time,
                            event_type="ingress",
                            description=f"{planet} enters {ingress.sign}",
                            symbol=f"{planet_glyph}\u2192{sign_glyph}",  # → arrow
                            priority=priority,
                        )
                    )
            except Exception:
                pass

    def collect_stations(self, planets: list[str] | None = None) -> None:
        """
        Collect retrograde and direct stations.

        Args:
            planets: Which planets to track (default: Mercury-Pluto)
        """
        from stellium.engines.search import find_all_stations

        if planets is None:
            planets = DEFAULT_STATION_PLANETS

        start_dt = datetime.combine(self.start, datetime.min.time())
        end_dt = datetime.combine(self.end, datetime.max.time())

        for planet in planets:
            try:
                stations = find_all_stations(planet, start_dt, end_dt)

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
                            description=desc,
                            symbol=symbol,
                            priority=1,  # Stations are important
                        )
                    )
            except Exception:
                pass

    def collect_moon_phases(self) -> None:
        """Collect New Moon, Full Moon, and quarter phases."""
        from stellium.electional.intervals import _find_all_lunations
        from stellium.engines.search import _datetime_to_julian_day

        start_jd = _datetime_to_julian_day(
            datetime.combine(self.start, datetime.min.time())
        )
        end_jd = _datetime_to_julian_day(
            datetime.combine(self.end, datetime.max.time())
        )

        # New Moons
        new_moons = _find_all_lunations(start_jd, end_jd, "new")
        for jd in new_moons:
            local_time = self._jd_to_local(jd)
            self._add_event(
                DailyEvent(
                    time=local_time,
                    event_type="moon_phase",
                    description="New Moon",
                    symbol="\U0001f311",  # 🌑
                    priority=1,
                )
            )

        # Full Moons
        full_moons = _find_all_lunations(start_jd, end_jd, "full")
        for jd in full_moons:
            local_time = self._jd_to_local(jd)
            self._add_event(
                DailyEvent(
                    time=local_time,
                    event_type="moon_phase",
                    description="Full Moon",
                    symbol="\U0001f315",  # 🌕
                    priority=1,
                )
            )

        # TODO: Add quarter phases if desired

    def collect_voc_periods(
        self, mode: Literal["traditional", "modern"] = "traditional"
    ) -> None:
        """
        Collect Void of Course Moon periods.

        Adds both start and end times for each VOC period.

        Args:
            mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)
        """
        from stellium.electional.intervals import voc_windows

        start_dt = datetime.combine(self.start, datetime.min.time())
        end_dt = datetime.combine(self.end, datetime.max.time())

        # Get VOC windows (these are when Moon IS void)
        voc_wins = voc_windows(start_dt, end_dt, mode=mode)

        for win in voc_wins:
            # VOC start
            start_local = self._jd_to_local(win.start_jd)
            self._add_event(
                DailyEvent(
                    time=start_local,
                    event_type="voc_start",
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
                    description="VOC ends",
                    symbol="\u263d\u2713",  # ☽✓ (Moon + check)
                    priority=4,
                )
            )

    def collect_eclipses(self) -> None:
        """Collect solar and lunar eclipses."""
        from stellium.engines.search import find_all_eclipses

        start_dt = datetime.combine(self.start, datetime.min.time())
        end_dt = datetime.combine(self.end, datetime.max.time())

        try:
            eclipses = find_all_eclipses(start_dt, end_dt)

            for eclipse in eclipses:
                local_time = self._jd_to_local(eclipse.julian_day)

                if eclipse.eclipse_type.startswith("solar"):
                    symbol = "\U0001f311\u2609"  # 🌑☉
                    desc = f"Solar Eclipse ({eclipse.eclipse_type})"
                else:
                    symbol = "\U0001f315\u263d"  # 🌕☽
                    desc = f"Lunar Eclipse ({eclipse.eclipse_type})"

                self._add_event(
                    DailyEvent(
                        time=local_time,
                        event_type="eclipse",
                        description=desc,
                        symbol=symbol,
                        priority=1,  # Eclipses are very important
                    )
                )
        except Exception:
            pass

    def collect_all(
        self,
        natal_transits: bool = True,
        transit_planets: list[str] | None = None,
        ingresses: bool = True,
        ingress_planets: list[str] | None = None,
        stations: bool = True,
        station_planets: list[str] | None = None,
        moon_phases: bool = True,
        voc: bool = True,
        voc_mode: Literal["traditional", "modern"] = "traditional",
        eclipses: bool = True,
    ) -> None:
        """
        Collect all configured event types.

        Args:
            natal_transits: Include transits to natal planets
            transit_planets: Which transiting planets
            ingresses: Include sign ingresses
            ingress_planets: Which planets for ingresses
            stations: Include retrograde/direct stations
            station_planets: Which planets for stations
            moon_phases: Include Moon phases
            voc: Include VOC periods
            voc_mode: VOC calculation mode
            eclipses: Include eclipses
        """
        if natal_transits:
            self.collect_natal_transits(transit_planets)

        if ingresses:
            self.collect_ingresses(ingress_planets)

        if stations:
            self.collect_stations(station_planets)

        if moon_phases:
            self.collect_moon_phases()

        if voc:
            self.collect_voc_periods(voc_mode)

        if eclipses:
            self.collect_eclipses()

        # Build the date index
        self._build_date_index()

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
