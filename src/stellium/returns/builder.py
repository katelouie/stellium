"""ReturnBuilder: Fluent builder for planetary return charts.

A "return" is a chart cast for the moment when a transiting planet
returns to its exact natal position. Common returns include:
- Solar Return: Sun returns to natal Sun position (~birthday)
- Lunar Return: Moon returns to natal Moon position (~monthly)
- Saturn Return: Saturn returns to natal Saturn (~age 29, 58)

ReturnBuilder wraps ChartBuilder using composition, delegating
all chainable configuration methods while handling the return-specific
calculations internally.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import CalculatedChart, ChartLocation
from stellium.core.protocols import (
    AspectEngine,
    ChartAnalyzer,
    ChartComponent,
    EphemerisEngine,
    HouseSystemEngine,
    OrbEngine,
)
from stellium.utils.planetary_crossing import (
    find_nth_return,
    find_return_near_date,
)
from stellium.utils.time import datetime_to_julian_day, julian_day_to_datetime

if TYPE_CHECKING:
    from stellium.core.config import CalculationConfig


@dataclass
class ReturnInfo:
    """Internal data about a calculated return moment."""

    return_jd: float
    return_datetime: dt.datetime
    natal_longitude: float
    return_number: int | None  # None for "near_date" returns
    location: ChartLocation


class ReturnBuilder:
    """
    Fluent builder for planetary return charts.

    Uses composition: wraps ChartBuilder rather than inheriting from it.
    This allows us to:
    - Lazily calculate the return moment before building the inner chart
    - Inject return-specific metadata into the final chart
    - Delegate all chainable methods without tight coupling

    Usage:
        >>> # Solar Return for 2025
        >>> sr = ReturnBuilder.solar(natal_chart, 2025).calculate()
        >>>
        >>> # Lunar Return near a date
        >>> lr = ReturnBuilder.lunar(natal_chart, near_date="2025-03-15").calculate()
        >>>
        >>> # First Saturn Return
        >>> saturn = ReturnBuilder.planetary(natal_chart, "Saturn", occurrence=1).calculate()
        >>>
        >>> # Relocated Solar Return
        >>> sr_relocated = (
        ...     ReturnBuilder.solar(natal_chart, 2025, location="Tokyo, Japan")
        ...     .calculate()
        ... )
    """

    def __init__(
        self,
        natal: CalculatedChart,
        planet: str,
        *,
        year: int | None = None,
        near_date: str | dt.datetime | None = None,
        occurrence: int | None = None,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> None:
        """
        Initialize ReturnBuilder (use factory methods instead).

        Args:
            natal: The natal chart to find returns for
            planet: Planet name (e.g., "Sun", "Moon", "Saturn")
            year: For annual returns (Solar), the year to calculate
            near_date: Find return nearest to this date
            occurrence: Find the Nth return (1 = first, 2 = second)
            location: Override location (for relocated returns)
        """
        self._natal = natal
        self._planet = planet
        self._year = year
        self._near_date = near_date
        self._occurrence = occurrence
        self._location_override = location

        # Inner builder (lazily created)
        self._inner_builder: ChartBuilder | None = None

        # Deferred configuration (applied when inner builder is created)
        self._deferred_ephemeris: EphemerisEngine | None = None
        self._deferred_house_systems: list[HouseSystemEngine] | None = None
        self._deferred_aspect_engine: AspectEngine | None = None
        self._deferred_orb_engine: OrbEngine | None = None
        self._deferred_components: list[ChartComponent] = []
        self._deferred_analyzers: list[ChartAnalyzer] = []
        self._deferred_config: CalculationConfig | None = None

    # ---- Factory Methods ----

    @classmethod
    def solar(
        cls,
        natal: CalculatedChart,
        year: int,
        *,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> ReturnBuilder:
        """
        Create a Solar Return builder.

        A Solar Return is the chart cast for when the Sun returns to its
        exact natal position. This happens approximately on your birthday
        each year (but the exact time varies).

        Args:
            natal: The natal chart
            year: Year to calculate the return for
            location: Override location (for relocated Solar Return)

        Returns:
            ReturnBuilder configured for Solar Return

        Example:
            >>> sr_2025 = ReturnBuilder.solar(natal, 2025).calculate()
        """
        return cls(natal, "Sun", year=year, location=location)

    @classmethod
    def lunar(
        cls,
        natal: CalculatedChart,
        *,
        near_date: str | dt.datetime | None = None,
        occurrence: int | None = None,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> ReturnBuilder:
        """
        Create a Lunar Return builder.

        A Lunar Return is the chart cast for when the Moon returns to its
        exact natal position. This happens approximately every 27.3 days.

        Args:
            natal: The natal chart
            near_date: Find the return nearest to this date (default: now)
            occurrence: Find the Nth return after birth (1 = first)
            location: Override location

        Returns:
            ReturnBuilder configured for Lunar Return

        Example:
            >>> # Lunar Return nearest to March 15, 2025
            >>> lr = ReturnBuilder.lunar(natal, near_date="2025-03-15").calculate()
            >>>
            >>> # The 100th Lunar Return
            >>> lr_100 = ReturnBuilder.lunar(natal, occurrence=100).calculate()
        """
        # Default to current time if neither specified
        if near_date is None and occurrence is None:
            near_date = dt.datetime.now(dt.UTC)

        return cls(
            natal, "Moon", near_date=near_date, occurrence=occurrence, location=location
        )

    @classmethod
    def planetary(
        cls,
        natal: CalculatedChart,
        planet: str,
        *,
        near_date: str | dt.datetime | None = None,
        occurrence: int | None = None,
        location: str | tuple[float, float] | ChartLocation | None = None,
    ) -> ReturnBuilder:
        """
        Create a planetary return builder for any planet.

        Args:
            natal: The natal chart
            planet: Planet name ("Saturn", "Jupiter", "Mars", etc.)
            near_date: Find the return nearest to this date
            occurrence: Find the Nth return (1 = first)
            location: Override location

        Returns:
            ReturnBuilder configured for the specified planetary return

        Example:
            >>> # First Saturn Return (~age 29)
            >>> sr1 = ReturnBuilder.planetary(natal, "Saturn", occurrence=1).calculate()
            >>>
            >>> # Jupiter Return nearest to 2025
            >>> jr = ReturnBuilder.planetary(
            ...     natal, "Jupiter", near_date="2025-06-01"
            ... ).calculate()
        """
        if near_date is None and occurrence is None:
            raise ValueError(
                "Must specify either near_date or occurrence for planetary returns"
            )

        return cls(
            natal, planet, near_date=near_date, occurrence=occurrence, location=location
        )

    # ---- Delegated Configuration Methods ----
    # These mirror ChartBuilder's fluent API but store config for later

    def with_ephemeris(self, engine: EphemerisEngine) -> ReturnBuilder:
        """Set the ephemeris engine."""
        self._deferred_ephemeris = engine
        return self

    def with_house_systems(self, engines: list[HouseSystemEngine]) -> ReturnBuilder:
        """Set the house system engines."""
        self._deferred_house_systems = engines
        return self

    def add_house_system(self, engine: HouseSystemEngine) -> ReturnBuilder:
        """Add an additional house system."""
        if self._deferred_house_systems is None:
            self._deferred_house_systems = []
        self._deferred_house_systems.append(engine)
        return self

    def with_aspects(self, engine: AspectEngine | None = None) -> ReturnBuilder:
        """Set the aspect engine."""
        self._deferred_aspect_engine = engine
        return self

    def with_orbs(self, engine: OrbEngine | None = None) -> ReturnBuilder:
        """Set the orb engine."""
        self._deferred_orb_engine = engine
        return self

    def add_component(self, component: ChartComponent) -> ReturnBuilder:
        """Add a calculation component."""
        self._deferred_components.append(component)
        return self

    def add_analyzer(self, analyzer: ChartAnalyzer) -> ReturnBuilder:
        """Add a chart analyzer."""
        self._deferred_analyzers.append(analyzer)
        return self

    def with_config(self, config: CalculationConfig) -> ReturnBuilder:
        """Set the calculation configuration."""
        self._deferred_config = config
        return self

    # ---- Main Calculation ----

    def calculate(self) -> CalculatedChart:
        """
        Calculate the return chart.

        This:
        1. Finds the exact moment of the planetary return
        2. Creates a ChartBuilder for that moment
        3. Applies any deferred configuration
        4. Injects return metadata
        5. Returns the calculated chart

        Returns:
            CalculatedChart with return metadata in chart.metadata
        """
        self._ensure_builder()
        assert self._inner_builder is not None
        return self._inner_builder.calculate()

    # ---- Internal Methods ----

    def _ensure_builder(self) -> None:
        """Lazily create the inner ChartBuilder with return datetime."""
        if self._inner_builder is not None:
            return

        # Calculate the return moment
        return_info = self._calculate_return_info()

        # Resolve location
        location = self._resolve_location(return_info)

        # Create chart name
        natal_name = self._natal.metadata.get("name", "Chart")
        chart_name = f"{natal_name} - {self._planet} Return"
        if self._year:
            chart_name = f"{natal_name} - {self._year} {self._planet} Return"

        # Create inner builder
        self._inner_builder = ChartBuilder.from_details(
            return_info.return_datetime,
            location,
            name=chart_name,
        )

        # Apply deferred configuration
        self._apply_deferred_config()

        # Inject return metadata via the hook we added
        self._inner_builder._extra_metadata = {  # type: ignore[attr-defined]
            "chart_type": "return",
            "return_planet": self._planet,
            "natal_planet_longitude": return_info.natal_longitude,
            "return_julian_day": return_info.return_jd,
        }
        if return_info.return_number is not None:
            self._inner_builder._extra_metadata["return_number"] = (
                return_info.return_number
            )  # type: ignore[attr-defined]

    def _calculate_return_info(self) -> ReturnInfo:
        """Calculate the return moment based on configuration."""
        # Get natal planet position
        natal_planet = self._natal.get_object(self._planet)
        if natal_planet is None:
            raise ValueError(f"Planet '{self._planet}' not found in natal chart")

        natal_longitude = natal_planet.longitude
        birth_jd = self._natal.datetime.julian_day

        return_jd: float
        return_number: int | None = None

        if self._year is not None:
            # Solar return: find return in specified year
            # Start searching from Jan 1 of that year
            search_start = datetime_to_julian_day(
                dt.datetime(self._year, 1, 1, tzinfo=pytz.UTC)
            )
            return_jd = find_return_near_date(
                self._planet, natal_longitude, search_start
            )

        elif self._occurrence is not None:
            # Nth return after birth
            return_jd = find_nth_return(
                self._planet, natal_longitude, birth_jd, self._occurrence
            )
            return_number = self._occurrence

        elif self._near_date is not None:
            # Return nearest to specified date
            if isinstance(self._near_date, str):
                # Parse string date
                from dateutil.parser import parse

                target_dt = parse(self._near_date)
                if target_dt.tzinfo is None:
                    target_dt = pytz.UTC.localize(target_dt)
            else:
                target_dt = self._near_date
                if target_dt.tzinfo is None:
                    target_dt = pytz.UTC.localize(target_dt)

            target_jd = datetime_to_julian_day(target_dt)
            return_jd = find_return_near_date(self._planet, natal_longitude, target_jd)

        else:
            raise ValueError("Must specify year, occurrence, or near_date")

        # Convert JD back to datetime
        return_datetime = julian_day_to_datetime(return_jd)

        return ReturnInfo(
            return_jd=return_jd,
            return_datetime=return_datetime,
            natal_longitude=natal_longitude,
            return_number=return_number,
            location=self._natal.location,  # Default to natal location
        )

    def _resolve_location(self, return_info: ReturnInfo) -> str | tuple[float, float]:
        """Resolve the location for the return chart."""
        if self._location_override is None:
            # Use natal location
            loc = self._natal.location
            return (loc.latitude, loc.longitude)

        if isinstance(self._location_override, ChartLocation):
            return (self._location_override.latitude, self._location_override.longitude)

        # String or tuple - pass through to ChartBuilder.from_details
        return self._location_override

    def _apply_deferred_config(self) -> None:
        """Apply any deferred configuration to the inner builder."""
        assert self._inner_builder is not None

        if self._deferred_ephemeris is not None:
            self._inner_builder.with_ephemeris(self._deferred_ephemeris)

        if self._deferred_house_systems is not None:
            self._inner_builder.with_house_systems(self._deferred_house_systems)

        if self._deferred_aspect_engine is not None:
            self._inner_builder.with_aspects(self._deferred_aspect_engine)
        else:
            # Default: enable aspects
            self._inner_builder.with_aspects()

        if self._deferred_orb_engine is not None:
            self._inner_builder.with_orbs(self._deferred_orb_engine)

        for component in self._deferred_components:
            self._inner_builder.add_component(component)

        for analyzer in self._deferred_analyzers:
            self._inner_builder.add_analyzer(analyzer)

        if self._deferred_config is not None:
            self._inner_builder.with_config(self._deferred_config)
