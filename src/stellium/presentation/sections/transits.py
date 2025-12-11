"""
Transit calendar report sections.

These sections show sky events (not natal chart analysis):
- StationSection: Planetary stations (retrograde/direct)
- IngressSection: Sign ingresses (future)
- EclipseSection: Solar and lunar eclipses (future)

Unlike other sections, these are date-range based rather than
chart-analysis based. The chart is passed for protocol compliance
but the sections use their own start/end dates.
"""

import datetime as dt
from typing import Any

from stellium.core.models import CalculatedChart
from stellium.engines.search import Station, find_all_stations

from ._utils import get_sign_glyph

# Default planets to check for stations (ones that go retrograde)
DEFAULT_STATION_PLANETS = [
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]


class StationSection:
    """
    Planetary stations report section.

    Shows when planets station retrograde or direct within a date range.
    Useful for retrograde calendars and transit planning.

    Note: This section uses explicit start/end dates rather than
    analyzing the natal chart. The chart parameter in generate_data()
    is accepted for protocol compliance but not used internally.
    """

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        planets: list[str] | None = None,
        include_minor: bool = False,
    ) -> None:
        """
        Initialize station section.

        Args:
            start: Start date for station search
            end: End date for station search
            planets: Which planets to include (default: Mercury through Pluto)
            include_minor: Include Chiron and other minor bodies (default: False)
        """
        self.start = start
        self.end = end
        self.planets = planets or DEFAULT_STATION_PLANETS.copy()

        if include_minor:
            self.planets.append("Chiron")

    @property
    def section_name(self) -> str:
        return "Planetary Stations"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate station data for the date range.

        Args:
            chart: CalculatedChart (accepted for protocol, not used internally)

        Returns:
            Dictionary with station data for rendering
        """
        # Collect all stations across all planets
        all_stations: list[Station] = []

        for planet in self.planets:
            try:
                stations = find_all_stations(planet, self.start, self.end)
                all_stations.extend(stations)
            except ValueError:
                # Skip planets that can't station (Sun, Moon)
                continue

        # Sort by date
        all_stations.sort(key=lambda s: s.julian_day)

        # Format for display
        rows = []
        for station in all_stations:
            degree = int(station.degree_in_sign)
            minute = int((station.degree_in_sign - degree) * 60)
            sign_glyph = get_sign_glyph(station.sign)

            rows.append(
                {
                    "date": station.datetime_utc.strftime("%Y-%m-%d"),
                    "time": station.datetime_utc.strftime("%H:%M"),
                    "planet": station.object_name,
                    "station_type": station.station_type.capitalize(),
                    "position": f"{degree}°{minute:02d}'",
                    "sign": station.sign,
                    "sign_glyph": sign_glyph,
                    # For sorting/filtering
                    "is_retrograde": station.is_turning_retrograde,
                    "datetime": station.datetime_utc,
                }
            )

        return {
            "type": "table",
            "title": self.section_name,
            "subtitle": f"{self.start.strftime('%Y-%m-%d')} to {self.end.strftime('%Y-%m-%d')}",
            "date_range": {
                "start": self.start.strftime("%Y-%m-%d"),
                "end": self.end.strftime("%Y-%m-%d"),
            },
            "planets_included": self.planets,
            "total_stations": len(all_stations),
            "headers": ["Date", "Time", "Planet", "Station", "Position", "Sign"],
            "rows": [
                [
                    row["date"],
                    row["time"],
                    row["planet"],
                    row["station_type"],
                    f"{row['position']} {row['sign_glyph']}",
                    row["sign"],
                ]
                for row in rows
            ],
        }
