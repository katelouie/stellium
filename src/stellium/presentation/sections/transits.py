"""
Transit calendar report sections.

These sections show sky events (not natal chart analysis):
- StationSection: Planetary stations (retrograde/direct)
- IngressSection: Sign ingresses
- EclipseSection: Solar and lunar eclipses

Unlike other sections, these are date-range based rather than
chart-analysis based. The chart is passed for protocol compliance
but the sections use their own start/end dates.
"""

import datetime as dt
from typing import Any

from stellium.core.models import CalculatedChart
from stellium.engines.search import (
    Eclipse,
    SignIngress,
    Station,
    find_all_eclipses,
    find_all_sign_changes,
    find_all_stations,
)

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

# Default planets to check for ingresses
DEFAULT_INGRESS_PLANETS = [
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


class IngressSection:
    """
    Sign ingress report section.

    Shows when planets enter new zodiac signs within a date range.
    Useful for tracking sign changes and transit planning.

    Note: This section uses explicit start/end dates rather than
    analyzing the natal chart. The chart parameter in generate_data()
    is accepted for protocol compliance but not used internally.
    """

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        planets: list[str] | None = None,
        include_moon: bool = False,
        include_minor: bool = False,
    ) -> None:
        """
        Initialize ingress section.

        Args:
            start: Start date for ingress search
            end: End date for ingress search
            planets: Which planets to include (default: Sun through Pluto)
            include_moon: Include Moon ingresses (default: False, very frequent)
            include_minor: Include Chiron and other minor bodies (default: False)
        """
        self.start = start
        self.end = end
        self.planets = planets or DEFAULT_INGRESS_PLANETS.copy()

        if include_moon:
            # Insert Moon after Sun for logical ordering
            if "Moon" not in self.planets:
                sun_idx = self.planets.index("Sun") if "Sun" in self.planets else 0
                self.planets.insert(sun_idx + 1, "Moon")

        if include_minor:
            if "Chiron" not in self.planets:
                self.planets.append("Chiron")

    @property
    def section_name(self) -> str:
        return "Sign Ingresses"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate ingress data for the date range.

        Args:
            chart: CalculatedChart (accepted for protocol, not used internally)

        Returns:
            Dictionary with ingress data for rendering
        """
        # Collect all ingresses across all planets
        all_ingresses: list[SignIngress] = []

        for planet in self.planets:
            try:
                ingresses = find_all_sign_changes(planet, self.start, self.end)
                all_ingresses.extend(ingresses)
            except ValueError:
                # Skip unknown objects
                continue

        # Sort by date
        all_ingresses.sort(key=lambda i: i.julian_day)

        # Format for display
        rows = []
        for ingress in all_ingresses:
            sign_glyph = get_sign_glyph(ingress.sign)
            from_sign_glyph = get_sign_glyph(ingress.from_sign)

            # Show retrograde indicator if applicable
            direction = "Rx " if ingress.is_retrograde else ""

            rows.append(
                {
                    "date": ingress.datetime_utc.strftime("%Y-%m-%d"),
                    "time": ingress.datetime_utc.strftime("%H:%M"),
                    "planet": ingress.object_name,
                    "direction": direction,
                    "from_sign": ingress.from_sign,
                    "from_sign_glyph": from_sign_glyph,
                    "to_sign": ingress.sign,
                    "to_sign_glyph": sign_glyph,
                    # For sorting/filtering
                    "is_retrograde": ingress.is_retrograde,
                    "datetime": ingress.datetime_utc,
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
            "total_ingresses": len(all_ingresses),
            "headers": ["Date", "Time", "Planet", "From", "To"],
            "rows": [
                [
                    row["date"],
                    row["time"],
                    f"{row['direction']}{row['planet']}",
                    f"{row['from_sign_glyph']} {row['from_sign']}",
                    f"{row['to_sign_glyph']} {row['to_sign']}",
                ]
                for row in rows
            ],
        }


class EclipseSection:
    """
    Eclipse report section.

    Shows solar and lunar eclipses within a date range.
    Useful for eclipse calendars and transit planning.

    Note: This section uses explicit start/end dates rather than
    analyzing the natal chart. The chart parameter in generate_data()
    is accepted for protocol compliance but not used internally.
    """

    def __init__(
        self,
        start: dt.datetime,
        end: dt.datetime,
        eclipse_types: str = "both",
    ) -> None:
        """
        Initialize eclipse section.

        Args:
            start: Start date for eclipse search
            end: End date for eclipse search
            eclipse_types: Which types to include ("both", "solar", "lunar")
        """
        self.start = start
        self.end = end
        self.eclipse_types = eclipse_types

    @property
    def section_name(self) -> str:
        if self.eclipse_types == "solar":
            return "Solar Eclipses"
        elif self.eclipse_types == "lunar":
            return "Lunar Eclipses"
        return "Eclipses"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate eclipse data for the date range.

        Args:
            chart: CalculatedChart (accepted for protocol, not used internally)

        Returns:
            Dictionary with eclipse data for rendering
        """
        # Find all eclipses in range
        all_eclipses: list[Eclipse] = find_all_eclipses(
            self.start, self.end, eclipse_types=self.eclipse_types
        )

        # Format for display
        rows = []
        for eclipse in all_eclipses:
            degree = int(eclipse.degree_in_sign)
            minute = int((eclipse.degree_in_sign - degree) * 60)
            sign_glyph = get_sign_glyph(eclipse.sign)

            # Format type nicely
            eclipse_label = (
                f"{eclipse.classification.capitalize()} {eclipse.eclipse_type}"
            )
            node_label = (
                "North Node" if eclipse.nearest_node == "north" else "South Node"
            )

            rows.append(
                {
                    "date": eclipse.datetime_utc.strftime("%Y-%m-%d"),
                    "time": eclipse.datetime_utc.strftime("%H:%M"),
                    "type": eclipse_label,
                    "position": f"{degree}°{minute:02d}'",
                    "sign": eclipse.sign,
                    "sign_glyph": sign_glyph,
                    "node": node_label,
                    "orb": f"{eclipse.orb_to_node:.1f}°",
                    # For sorting/filtering
                    "is_solar": eclipse.is_solar,
                    "is_lunar": eclipse.is_lunar,
                    "classification": eclipse.classification,
                    "datetime": eclipse.datetime_utc,
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
            "eclipse_types": self.eclipse_types,
            "total_eclipses": len(all_eclipses),
            "headers": ["Date", "Time", "Type", "Position", "Sign", "Node"],
            "rows": [
                [
                    row["date"],
                    row["time"],
                    row["type"],
                    f"{row['position']} {row['sign_glyph']}",
                    row["sign"],
                    row["node"],
                ]
                for row in rows
            ],
        }
