"""
PlannerBuilder - Fluent API for creating personalized astrological planners.

This module provides a builder pattern for configuring and generating
PDF planners with charts, transits, and daily astrological events.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from stellium.core.native import Native


@dataclass
class PlannerConfig:
    """Configuration for planner generation."""

    # Required
    native: Native
    timezone: str

    # Date range
    start_date: date | None = None
    end_date: date | None = None
    year: int | None = None

    # Location for angles/planetary hours (defaults to birth location)
    location: str | tuple[float, float] | None = None

    # Front matter options
    include_natal_chart: bool = True
    include_progressed_chart: bool = True
    include_solar_return: bool = True
    include_profections: bool = True
    include_zr_timeline: bool = True
    zr_lot: str = "Part of Fortune"
    include_graphic_ephemeris: bool = True
    graphic_ephemeris_harmonic: int = 360

    # Daily content options
    natal_transit_planets: list[str] | None = None  # None = all outer planets
    include_mundane_transits: bool = True
    include_moon_phases: bool = True
    include_voc: bool = True
    voc_mode: Literal["traditional", "modern"] = "traditional"
    ingress_planets: list[str] | None = None  # None = all planets
    station_planets: list[str] | None = None  # None = outer planets

    # Page layout
    page_size: Literal["a4", "letter", "half-letter"] = "a4"
    binding_margin: float = 0.0  # Extra margin for binding (inches)
    week_starts_on: Literal["sunday", "monday"] = "sunday"


class PlannerBuilder:
    """
    Fluent builder for creating personalized astrological planners.

    Example:
        >>> from stellium import Native
        >>> from stellium.planner import PlannerBuilder
        >>>
        >>> native = Native("1990-05-15 14:30", "San Francisco, CA")
        >>> planner = (PlannerBuilder.for_native(native)
        ...     .year(2025)
        ...     .timezone("America/Los_Angeles")
        ...     .with_natal_chart()
        ...     .with_solar_return()
        ...     .include_natal_transits()
        ...     .generate("my_planner.pdf"))
    """

    def __init__(self, native: Native) -> None:
        """Initialize builder with a native."""
        self._native = native
        self._timezone: str | None = None
        self._year: int | None = None
        self._start_date: date | None = None
        self._end_date: date | None = None
        self._location: str | tuple[float, float] | None = None

        # Front matter flags
        self._natal_chart = True
        self._progressed_chart = True
        self._solar_return = True
        self._profections = True
        self._zr_timeline = True
        self._zr_lot = "Part of Fortune"
        self._graphic_ephemeris = True
        self._graphic_ephemeris_harmonic = 360

        # Daily content flags
        self._natal_transit_planets: list[str] | None = None
        self._mundane_transits = True
        self._moon_phases = True
        self._voc = True
        self._voc_mode: Literal["traditional", "modern"] = "traditional"
        self._ingress_planets: list[str] | None = None
        self._station_planets: list[str] | None = None

        # Page layout
        self._page_size: Literal["a4", "letter", "half-letter"] = "a4"
        self._binding_margin = 0.0
        self._week_starts_on: Literal["sunday", "monday"] = "sunday"

    # ===== Constructors =====

    @classmethod
    def for_native(cls, native: Native) -> PlannerBuilder:
        """
        Start building a planner for a native.

        Args:
            native: The Native whose planner to create

        Returns:
            PlannerBuilder instance for chaining
        """
        return cls(native)

    # ===== Date Range Configuration =====

    def year(self, year: int) -> PlannerBuilder:
        """
        Set the calendar year for the planner.

        Args:
            year: Calendar year (e.g., 2025)

        Returns:
            Self for chaining
        """
        self._year = year
        self._start_date = date(year, 1, 1)
        self._end_date = date(year, 12, 31)
        return self

    def date_range(self, start: date, end: date) -> PlannerBuilder:
        """
        Set a custom date range for the planner.

        Args:
            start: Start date
            end: End date

        Returns:
            Self for chaining
        """
        if end <= start:
            raise ValueError("End date must be after start date")
        self._start_date = start
        self._end_date = end
        self._year = None  # Clear year if custom range
        return self

    def timezone(self, tz: str) -> PlannerBuilder:
        """
        Set the timezone for transit times.

        This is required - transit times will be displayed in this timezone.

        Args:
            tz: Timezone string (e.g., "America/Los_Angeles", "Europe/London")

        Returns:
            Self for chaining
        """
        self._timezone = tz
        return self

    def location(self, location: str | tuple[float, float]) -> PlannerBuilder:
        """
        Set location for angle calculations and planetary hours.

        Defaults to the native's birth location if not specified.

        Args:
            location: City name or (latitude, longitude) tuple

        Returns:
            Self for chaining
        """
        self._location = location
        return self

    # ===== Front Matter Configuration =====

    def with_natal_chart(self, enabled: bool = True) -> PlannerBuilder:
        """Include natal chart wheel in front matter."""
        self._natal_chart = enabled
        return self

    def with_progressed_chart(self, enabled: bool = True) -> PlannerBuilder:
        """Include secondary progressed chart in front matter."""
        self._progressed_chart = enabled
        return self

    def with_solar_return(self, enabled: bool = True) -> PlannerBuilder:
        """Include solar return chart for the planner year."""
        self._solar_return = enabled
        return self

    def with_profections(self, enabled: bool = True) -> PlannerBuilder:
        """Include annual profection info (Lord of the Year)."""
        self._profections = enabled
        return self

    def with_zr_timeline(
        self, lot: str = "Part of Fortune", enabled: bool = True
    ) -> PlannerBuilder:
        """
        Include Zodiacal Releasing timeline visualization.

        Args:
            lot: Which lot to release from (default: "Part of Fortune")
            enabled: Whether to include ZR timeline

        Returns:
            Self for chaining
        """
        self._zr_timeline = enabled
        self._zr_lot = lot
        return self

    def with_graphic_ephemeris(
        self, harmonic: int = 360, enabled: bool = True
    ) -> PlannerBuilder:
        """
        Include graphic ephemeris for the planner period.

        Args:
            harmonic: Harmonic compression (360=full zodiac, 90=cardinal, 45=semi-square)
            enabled: Whether to include graphic ephemeris

        Returns:
            Self for chaining
        """
        self._graphic_ephemeris = enabled
        self._graphic_ephemeris_harmonic = harmonic
        return self

    # ===== Daily Content Configuration =====

    def include_natal_transits(
        self, planets: list[str] | None = None
    ) -> PlannerBuilder:
        """
        Include transits to natal planets.

        Args:
            planets: Which transiting planets to include. Default (None) uses
                     outer planets: Jupiter, Saturn, Uranus, Neptune, Pluto

        Returns:
            Self for chaining
        """
        self._natal_transit_planets = planets
        return self

    def include_mundane_transits(self, enabled: bool = True) -> PlannerBuilder:
        """Include mundane transits (planet-to-planet in sky)."""
        self._mundane_transits = enabled
        return self

    def include_moon_phases(self, enabled: bool = True) -> PlannerBuilder:
        """Include Moon phases (new, full, quarters)."""
        self._moon_phases = enabled
        return self

    def include_voc(
        self, mode: Literal["traditional", "modern"] = "traditional"
    ) -> PlannerBuilder:
        """
        Include Void of Course Moon periods.

        Args:
            mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)

        Returns:
            Self for chaining
        """
        self._voc = True
        self._voc_mode = mode
        return self

    def exclude_voc(self) -> PlannerBuilder:
        """Exclude Void of Course Moon periods."""
        self._voc = False
        return self

    def include_ingresses(self, planets: list[str] | None = None) -> PlannerBuilder:
        """
        Include planet sign ingresses.

        Args:
            planets: Which planets to track. Default (None) includes all.

        Returns:
            Self for chaining
        """
        self._ingress_planets = planets
        return self

    def include_stations(self, planets: list[str] | None = None) -> PlannerBuilder:
        """
        Include retrograde/direct stations.

        Args:
            planets: Which planets to track. Default (None) uses Mercury-Pluto.

        Returns:
            Self for chaining
        """
        self._station_planets = planets
        return self

    # ===== Page Layout Configuration =====

    def page_size(self, size: Literal["a4", "letter", "half-letter"]) -> PlannerBuilder:
        """
        Set page size.

        Args:
            size: "a4" (default), "letter", or "half-letter"

        Returns:
            Self for chaining
        """
        self._page_size = size
        return self

    def binding_margin(self, inches: float) -> PlannerBuilder:
        """
        Add extra margin for binding.

        Args:
            inches: Extra margin in inches (added to inner edge)

        Returns:
            Self for chaining
        """
        self._binding_margin = inches
        return self

    def week_starts_on(self, day: Literal["sunday", "monday"]) -> PlannerBuilder:
        """
        Set the first day of the week for calendar grids.

        Args:
            day: "sunday" (default) or "monday"

        Returns:
            Self for chaining
        """
        self._week_starts_on = day
        return self

    # ===== Build / Generate =====

    def _validate(self) -> None:
        """Validate configuration before generation."""
        if self._timezone is None:
            raise ValueError(
                "Timezone is required. Call .timezone('America/Los_Angeles') or similar."
            )

        if self._start_date is None or self._end_date is None:
            raise ValueError(
                "Date range is required. Call .year(2025) or .date_range(start, end)."
            )

    def _build_config(self) -> PlannerConfig:
        """Build the configuration object."""
        self._validate()

        return PlannerConfig(
            native=self._native,
            timezone=self._timezone,  # type: ignore (validated above)
            start_date=self._start_date,
            end_date=self._end_date,
            year=self._year,
            location=self._location,
            include_natal_chart=self._natal_chart,
            include_progressed_chart=self._progressed_chart,
            include_solar_return=self._solar_return,
            include_profections=self._profections,
            include_zr_timeline=self._zr_timeline,
            zr_lot=self._zr_lot,
            include_graphic_ephemeris=self._graphic_ephemeris,
            graphic_ephemeris_harmonic=self._graphic_ephemeris_harmonic,
            natal_transit_planets=self._natal_transit_planets,
            include_mundane_transits=self._mundane_transits,
            include_moon_phases=self._moon_phases,
            include_voc=self._voc,
            voc_mode=self._voc_mode,
            ingress_planets=self._ingress_planets,
            station_planets=self._station_planets,
            page_size=self._page_size,
            binding_margin=self._binding_margin,
            week_starts_on=self._week_starts_on,
        )

    def generate(self, output_path: str | None = None) -> bytes:
        """
        Generate the PDF planner.

        Args:
            output_path: Optional file path to save the PDF.
                        If None, only returns bytes.

        Returns:
            PDF as bytes
        """
        from stellium.planner.renderer import PlannerRenderer

        config = self._build_config()
        renderer = PlannerRenderer(config)
        pdf_bytes = renderer.render()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes
