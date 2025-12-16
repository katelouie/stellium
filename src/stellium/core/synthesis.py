"""
Synthesis charts: Composite and Davison chart calculations.

These create a single "synthesized" chart from two source charts,
representing a relationship or combined energy.

Composite: Midpoint of each planet/point between charts
Davison: Midpoint in time and space, then regular chart calculation
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from math import atan2, cos, degrees, floor, radians, sin, sqrt
from typing import TYPE_CHECKING, Any

import pytz
import swisseph as swe

from stellium.core.models import (
    CalculatedChart,
    ChartDateTime,
    ChartLocation,
)

if TYPE_CHECKING:
    from stellium.core.native import Native


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_midpoint_longitude(
    lon1: float, lon2: float, method: str = "short_arc"
) -> float:
    """
    Calculate midpoint between two zodiac longitudes.

    Args:
        lon1: First longitude (0-360)
        lon2: Second longitude (0-360)
        method: "short_arc" (default) or "long_arc"

    Returns:
        Midpoint longitude (0-360)

    Examples:
        >>> calculate_midpoint_longitude(10, 20)  # Both in Aries
        15.0

        >>> calculate_midpoint_longitude(10, 190)  # Aries and Libra
        100.0  # Cancer (short arc)

        >>> calculate_midpoint_longitude(10, 190, "long_arc")
        280.0  # Capricorn (long arc)
    """
    if method == "short_arc":
        # Find shorter path around circle
        diff = (lon2 - lon1 + 360) % 360
        if diff > 180:
            diff = diff - 360
        return (lon1 + diff / 2) % 360

    elif method == "long_arc":
        # Find longer path around circle
        diff = (lon2 - lon1 + 360) % 360
        if diff <= 180:
            diff = diff - 360
        return (lon1 + diff / 2) % 360

    else:
        raise ValueError(f"Unknown midpoint method: {method}")


def julian_day_to_datetime(jd: float, timezone: str = "UTC") -> dt.datetime:
    """
    Convert Julian day to Python datetime.

    Args:
        jd: Julian day number
        timezone: Timezone string (default UTC)

    Returns:
        Timezone-aware datetime object
    """
    # swe.revjul returns (year, month, day, hour_as_float)
    year, month, day, h_float = swe.revjul(jd)

    # Extract hours, minutes, seconds from the float hour
    hour = floor(h_float)
    h_float = (h_float - hour) * 60
    minute = floor(h_float)
    h_float = (h_float - minute) * 60
    second = int(round(h_float))

    # Handle edge cases where rounding pushes values over
    if second == 60:
        minute += 1
        second = 0
    if minute == 60:
        hour += 1
        minute = 0
    if hour == 24:
        # Need to advance the day - let datetime handle it
        base_dt = dt.datetime(year, month, day, 0, 0, 0)
        base_dt = base_dt + dt.timedelta(days=1)
        year, month, day = base_dt.year, base_dt.month, base_dt.day
        hour = 0

    # Create datetime and localize to UTC (Julian days are in UT)
    utc_dt = dt.datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)

    return utc_dt


def calculate_datetime_midpoint(
    dt1: ChartDateTime, dt2: ChartDateTime
) -> tuple[dt.datetime, float]:
    """
    Calculate midpoint between two datetimes using Julian day.

    Args:
        dt1: First chart datetime
        dt2: Second chart datetime

    Returns:
        Tuple of (midpoint_datetime, midpoint_julian_day)
    """
    # Average the Julian days - this handles all calendar complexity!
    jd_mid = (dt1.julian_day + dt2.julian_day) / 2

    # Convert back to datetime
    mid_datetime = julian_day_to_datetime(jd_mid)

    return mid_datetime, jd_mid


def calculate_location_midpoint(
    loc1: ChartLocation, loc2: ChartLocation, method: str = "great_circle"
) -> ChartLocation:
    """
    Calculate geographic midpoint between two locations.

    Args:
        loc1: First location
        loc2: Second location
        method: "great_circle" (default, geodesic) or "simple" (arithmetic mean)

    Returns:
        Midpoint location

    Note:
        Great circle (geodesic) midpoint follows the Earth's curvature and is
        more accurate for locations far apart. Simple arithmetic mean can give
        incorrect results, especially across the date line or for distant points.
    """
    if method == "simple":
        # Simple arithmetic mean - fast but inaccurate for distant points
        mid_lat = (loc1.latitude + loc2.latitude) / 2
        mid_lon = (loc1.longitude + loc2.longitude) / 2

    elif method == "great_circle":
        # Great circle midpoint using spherical geometry
        # Formula from: https://www.movable-type.co.uk/scripts/latlong.html

        # Convert to radians
        lat1 = radians(loc1.latitude)
        lat2 = radians(loc2.latitude)
        lon1 = radians(loc1.longitude)
        lon2 = radians(loc2.longitude)

        # Difference in longitude
        d_lon = lon2 - lon1

        # Calculate midpoint using vector math on unit sphere
        # Convert both points to Cartesian, average, convert back
        bx = cos(lat2) * cos(d_lon)
        by = cos(lat2) * sin(d_lon)

        mid_lat = atan2(sin(lat1) + sin(lat2), sqrt((cos(lat1) + bx) ** 2 + by**2))
        mid_lon = lon1 + atan2(by, cos(lat1) + bx)

        # Convert back to degrees
        mid_lat = degrees(mid_lat)
        mid_lon = degrees(mid_lon)

        # Normalize longitude to -180 to 180
        mid_lon = ((mid_lon + 180) % 360) - 180

    else:
        raise ValueError(f"Unknown location midpoint method: {method}")

    # Create location name from both sources
    name1 = loc1.name or "Location 1"
    name2 = loc2.name or "Location 2"
    mid_name = f"Midpoint: {name1} / {name2}"

    # For timezone, we'll leave it empty - the Native class will handle it
    # based on the coordinates when we create the chart
    return ChartLocation(
        latitude=mid_lat,
        longitude=mid_lon,
        name=mid_name,
        timezone="",
    )


# =============================================================================
# SynthesisChart Data Model
# =============================================================================


@dataclass(frozen=True)
class SynthesisChart(CalculatedChart):
    """
    A chart synthesized from two source charts (composite or davison).

    Inherits all fields from CalculatedChart:
    - positions: tuple[CelestialPosition, ...]
    - aspects: tuple[Aspect, ...]
    - house_systems: dict[str, HouseCusps]
    - house_placements: dict[str, dict]
    - datetime: ChartDateTime
    - location: ChartLocation
    - metadata: dict

    And adds synthesis-specific fields.
    """

    # === Core Synthesis Metadata ===

    synthesis_method: str = ""
    """The synthesis method used: "composite" or "davison" """

    source_chart1: CalculatedChart | None = None
    """The first source chart (full chart object for reference)"""

    source_chart2: CalculatedChart | None = None
    """The second source chart (full chart object for reference)"""

    chart1_label: str = "Chart 1"
    """Descriptive label for first chart (e.g., "Alice", "Natal")"""

    chart2_label: str = "Chart 2"
    """Descriptive label for second chart (e.g., "Bob", "Transit")"""

    # === Method-Specific Configuration ===

    midpoint_method: str | None = None
    """Composite only: "short_arc" or "long_arc" """

    houses_config: bool | str | None = None
    """Composite only: True (derived), False (none), or "place" """

    location_method: str | None = None
    """Davison only: "simple" or "great_circle" """

    def to_dict(self) -> dict[str, Any]:
        """Extend parent's to_dict with synthesis-specific fields."""
        base_dict = super().to_dict()

        # Add synthesis metadata
        base_dict["synthesis"] = {
            "method": self.synthesis_method,
            "chart1_label": self.chart1_label,
            "chart2_label": self.chart2_label,
        }

        # Add method-specific config
        if self.synthesis_method == "composite":
            base_dict["synthesis"]["midpoint_method"] = self.midpoint_method
            base_dict["synthesis"]["houses"] = self.houses_config
        elif self.synthesis_method == "davison":
            base_dict["synthesis"]["location_method"] = self.location_method

        return base_dict


# =============================================================================
# SynthesisBuilder
# =============================================================================


class SynthesisBuilder:
    """
    Builder for synthesizing two charts into one (composite or davison).

    Example::

        # Simple davison
        davison = SynthesisBuilder.davison(chart1, chart2).calculate()

        # Configured composite
        composite = (SynthesisBuilder.composite(chart1, chart2)
            .with_midpoint_method("short_arc")
            .with_labels("Alice", "Bob")
            .calculate())
    """

    def __init__(
        self,
        chart1: CalculatedChart | Native,
        chart2: CalculatedChart | Native,
        method: str,
    ):
        """Internal constructor. Use .composite() or .davison() instead."""
        self._chart1 = chart1
        self._chart2 = chart2
        self._method = method

        # Configuration (with defaults)
        self._midpoint_method = "short_arc"  # Composite: "short_arc" or "long_arc"
        self._houses: bool | str = (
            True  # Composite: True (derived), False (none), "place"
        )
        self._location_method = "great_circle"  # Davison: "great_circle" or "simple"
        self._chart1_label = "Chart 1"
        self._chart2_label = "Chart 2"

    # --- Constructors ---

    @classmethod
    def composite(
        cls, chart1: CalculatedChart | Native, chart2: CalculatedChart | Native
    ) -> SynthesisBuilder:
        """
        Create composite chart (midpoint of all positions).

        Args:
            chart1: First chart (CalculatedChart or Native)
            chart2: Second chart (CalculatedChart or Native)

        Returns:
            SynthesisBuilder configured for composite calculation
        """
        return cls(chart1, chart2, method="composite")

    @classmethod
    def davison(
        cls, chart1: CalculatedChart | Native, chart2: CalculatedChart | Native
    ) -> SynthesisBuilder:
        """
        Create davison chart (midpoint in time and space).

        Args:
            chart1: First chart (CalculatedChart or Native)
            chart2: Second chart (CalculatedChart or Native)

        Returns:
            SynthesisBuilder configured for davison calculation
        """
        return cls(chart1, chart2, method="davison")

    # --- Configuration Methods ---

    def with_midpoint_method(self, method: str) -> SynthesisBuilder:
        """
        Set midpoint calculation method for composite charts.

        Args:
            method: "short_arc" (default) or "long_arc"
                   - short_arc: Always takes shorter path around zodiac
                   - long_arc: Always takes longer path

        Returns:
            Self for chaining
        """
        self._midpoint_method = method
        return self

    def with_houses(self, houses: bool | str) -> SynthesisBuilder:
        """
        Set house calculation method for composite charts.

        Args:
            houses: True (default) - Derived ASC method (midpoint Ascendants, derive cusps)
                    False - No houses (positions only)
                    "place" - Reference place method (geographic midpoint + derived time)

        Returns:
            Self for chaining

        Example:
            # No houses
            composite = SynthesisBuilder.composite(c1, c2).with_houses(False).calculate()

            # Reference place method
            composite = SynthesisBuilder.composite(c1, c2).with_houses("place").calculate()
        """
        self._houses = houses
        return self

    def with_location_method(self, method: str) -> SynthesisBuilder:
        """
        Set location midpoint method for davison charts.

        Args:
            method: "great_circle" (default) - Geodesic midpoint following Earth's curvature
                    "simple" - Arithmetic mean of lat/lon (faster but less accurate)

        Returns:
            Self for chaining
        """
        self._location_method = method
        return self

    def with_labels(self, label1: str, label2: str) -> SynthesisBuilder:
        """
        Set descriptive labels for source charts.

        Args:
            label1: Label for first chart (e.g., "Alice", "Natal")
            label2: Label for second chart (e.g., "Bob", "Transit")

        Returns:
            Self for chaining
        """
        self._chart1_label = label1
        self._chart2_label = label2
        return self

    # --- Calculation ---

    def calculate(self) -> SynthesisChart:
        """
        Calculate the synthesis chart.

        Returns:
            SynthesisChart (subclass of CalculatedChart)
        """
        # Ensure we have CalculatedChart objects
        chart1 = self._ensure_calculated(self._chart1)
        chart2 = self._ensure_calculated(self._chart2)

        if self._method == "composite":
            return self._calculate_composite(chart1, chart2)
        elif self._method == "davison":
            return self._calculate_davison(chart1, chart2)
        else:
            raise ValueError(f"Unknown synthesis method: {self._method}")

    # --- Internal Helpers ---

    def _ensure_calculated(
        self, chart_or_native: CalculatedChart | Native
    ) -> CalculatedChart:
        """Convert Native to CalculatedChart if needed."""
        from stellium.core.builder import ChartBuilder
        from stellium.core.native import Native

        if isinstance(chart_or_native, Native):
            return ChartBuilder.from_native(chart_or_native).calculate()
        return chart_or_native

    def _calculate_davison(
        self, chart1: CalculatedChart, chart2: CalculatedChart
    ) -> SynthesisChart:
        """
        Calculate davison chart using time/space midpoint.

        Algorithm:
        1. Calculate midpoint datetime (average Julian day)
        2. Calculate midpoint location (simple or great_circle)
        3. Create Native with midpoint datetime/location
        4. Use ChartBuilder to calculate chart normally
        5. Wrap result in SynthesisChart with source chart references
        """
        from stellium.core.builder import ChartBuilder
        from stellium.core.native import Native

        # 1. Calculate datetime midpoint
        mid_datetime, mid_jd = calculate_datetime_midpoint(
            chart1.datetime, chart2.datetime
        )

        # 2. Calculate location midpoint
        mid_location = calculate_location_midpoint(
            chart1.location, chart2.location, method=self._location_method
        )

        # 3. Create Native with midpoint coordinates
        # Native will handle timezone lookup from coordinates
        native = Native(
            datetime_input=mid_datetime,
            location_input=(mid_location.latitude, mid_location.longitude),
        )

        # 4. Calculate chart normally using ChartBuilder
        # Include aspects so they appear in the davison chart visualization
        base_chart = ChartBuilder.from_native(native).with_aspects().calculate()

        # 5. Wrap in SynthesisChart with full metadata
        return SynthesisChart(
            # From base chart calculation
            datetime=base_chart.datetime,
            location=base_chart.location,
            positions=base_chart.positions,
            house_systems=base_chart.house_systems,
            house_placements=base_chart.house_placements,
            aspects=base_chart.aspects,
            metadata=base_chart.metadata,
            calculation_timestamp=base_chart.calculation_timestamp,
            # Synthesis-specific
            synthesis_method="davison",
            source_chart1=chart1,
            source_chart2=chart2,
            chart1_label=self._chart1_label,
            chart2_label=self._chart2_label,
            location_method=self._location_method,
        )

    def _calculate_composite(
        self, chart1: CalculatedChart, chart2: CalculatedChart
    ) -> SynthesisChart:
        """
        Calculate composite chart using midpoint method.

        Algorithm:
        1. For each planet in chart1, find corresponding planet in chart2
        2. Calculate midpoint longitude (respecting midpoint_method)
        3. Create new CelestialPosition with midpoint coordinates
        4. Calculate houses based on _houses setting:
           - True: Derived ASC method (midpoint Ascendants)
           - False: No houses
           - "place": Reference place method (geographic midpoint)
        5. Calculate aspects between composite positions
        6. Return SynthesisChart with all data
        """
        from stellium.core.builder import ChartBuilder
        from stellium.core.models import CelestialPosition
        from stellium.core.native import Native
        from stellium.engines.aspects import ModernAspectEngine

        # 1. Calculate composite positions (midpoint of each planet/point)
        composite_positions: list[CelestialPosition] = []

        for pos1 in chart1.positions:
            # Find matching position in chart2
            pos2 = chart2.get_object(pos1.name)
            if pos2 is None:
                continue  # Skip if not found in both charts

            # Calculate midpoint longitude
            mid_lon = calculate_midpoint_longitude(
                pos1.longitude, pos2.longitude, method=self._midpoint_method
            )

            # For latitude, use simple average (latitude midpoints don't wrap)
            mid_lat = (pos1.latitude + pos2.latitude) / 2

            # For distance, use average
            mid_dist = (pos1.distance + pos2.distance) / 2

            # For speed, use average (affects retrograde detection)
            mid_speed_lon = (pos1.speed_longitude + pos2.speed_longitude) / 2
            mid_speed_lat = (pos1.speed_latitude + pos2.speed_latitude) / 2
            mid_speed_dist = (pos1.speed_distance + pos2.speed_distance) / 2

            # Create composite position
            composite_pos = CelestialPosition(
                name=pos1.name,
                object_type=pos1.object_type,
                longitude=mid_lon,
                latitude=mid_lat,
                distance=mid_dist,
                speed_longitude=mid_speed_lon,
                speed_latitude=mid_speed_lat,
                speed_distance=mid_speed_dist,
                phase=None,  # Composite charts don't have meaningful phase data
            )
            composite_positions.append(composite_pos)

        # 2. Calculate houses based on configuration
        house_systems: dict = {}
        house_placements: dict = {}
        composite_datetime = None
        composite_location = None

        if self._houses is False:
            # No houses - just use placeholder datetime/location from chart1
            composite_datetime = chart1.datetime
            composite_location = chart1.location

        elif self._houses is True:
            # Derived ASC method
            # Use midpoint datetime and midpoint location to calculate houses
            # The ASC will naturally be the midpoint of the two ASCs
            mid_datetime, _ = calculate_datetime_midpoint(
                chart1.datetime, chart2.datetime
            )
            mid_location = calculate_location_midpoint(
                chart1.location, chart2.location, method="great_circle"
            )

            # Create native and calculate just for houses
            native = Native(
                datetime_input=mid_datetime,
                location_input=(mid_location.latitude, mid_location.longitude),
            )
            temp_chart = ChartBuilder.from_native(native).calculate()

            house_systems = temp_chart.house_systems
            house_placements = self._calculate_house_placements(
                composite_positions, house_systems
            )
            composite_datetime = temp_chart.datetime
            composite_location = temp_chart.location

        elif self._houses == "place":
            # Reference place method
            # Use geographic midpoint with a derived time
            mid_location = calculate_location_midpoint(
                chart1.location, chart2.location, method="great_circle"
            )
            mid_datetime, _ = calculate_datetime_midpoint(
                chart1.datetime, chart2.datetime
            )

            native = Native(
                datetime_input=mid_datetime,
                location_input=(mid_location.latitude, mid_location.longitude),
            )
            temp_chart = ChartBuilder.from_native(native).calculate()

            house_systems = temp_chart.house_systems
            house_placements = self._calculate_house_placements(
                composite_positions, house_systems
            )
            composite_datetime = temp_chart.datetime
            composite_location = temp_chart.location

        # 3. Calculate aspects between composite positions
        from stellium.engines.orbs import SimpleOrbEngine

        aspect_engine = ModernAspectEngine()
        orb_engine = SimpleOrbEngine()
        aspects = aspect_engine.calculate_aspects(composite_positions, orb_engine)

        # 4. Create and return SynthesisChart
        return SynthesisChart(
            datetime=composite_datetime,
            location=composite_location,
            positions=tuple(composite_positions),
            house_systems=house_systems,
            house_placements=house_placements,
            aspects=tuple(aspects),
            metadata={},
            # Synthesis-specific
            synthesis_method="composite",
            source_chart1=chart1,
            source_chart2=chart2,
            chart1_label=self._chart1_label,
            chart2_label=self._chart2_label,
            midpoint_method=self._midpoint_method,
            houses_config=self._houses,
        )

    def _calculate_house_placements(
        self,
        positions: list,
        house_systems: dict,
    ) -> dict:
        """Calculate which house each position falls in for each house system."""
        from stellium.utils.houses import find_house_for_longitude

        placements: dict = {}
        for system_name, house_cusps in house_systems.items():
            placements[system_name] = {}
            for pos in positions:
                house = find_house_for_longitude(pos.longitude, house_cusps.cusps)
                placements[system_name][pos.name] = house
        return placements
