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

PAGE_SIZES = ("a4", "a5", "letter", "half-letter")
WEEKDAYS = ("sunday", "monday")
TIME_FORMATS = ("12h", "24h")
VOC_MODES = ("traditional", "modern")
EPHEMERIS_HARMONICS = (360, 90, 45)


def _check_choice(what: str, value: object, choices: tuple) -> None:
    """Reject a bad option at the call that set it, not deep inside generate().

    Several of these used to be accepted silently — an unknown harmonic quietly
    became 90 — or only failed after every chart and search had already run.
    """
    if value not in choices:
        options = ", ".join(repr(c) for c in choices)
        raise ValueError(f"Unknown {what} {value!r}. Choose from: {options}")


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

    # Where the planner is used: casts the solar return there and labels the
    # times. The *times themselves* follow `timezone`, never this.
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
    include_natal_transits: bool = True
    # None = DEFAULT_TRANSIT_PLANETS: all ten planets, the True Node and Chiron
    natal_transit_planets: list[str] | None = None
    natal_transit_points: bool = True  # also transits to the ASC, MC and Node
    include_mundane_transits: bool = True
    mundane_planets: list[str] | None = None  # None = the ten planets
    include_moon_phases: bool = True
    include_quarter_moons: bool = True
    include_eclipses: bool = True
    include_voc: bool = True
    voc_mode: Literal["traditional", "modern"] = "traditional"
    include_ingresses: bool = True
    ingress_planets: list[str] | None = None  # None = DEFAULT_TRANSIT_PLANETS
    include_stations: bool = True
    station_planets: list[str] | None = None  # None = Mercury–Pluto and Chiron

    # Page layout
    page_size: Literal["a4", "a5", "letter", "half-letter"] = "a4"
    binding_margin: float = 0.0  # Extra margin for binding (inches)

    # The month grid and the weekly pages are different reading surfaces, so they
    # get independent first days: a US reader often wants a Sunday-led month grid
    # but a Monday-led working week. `weekly_starts_on=None` follows the monthly.
    week_starts_on: Literal["sunday", "monday"] = "sunday"
    weekly_starts_on: Literal["sunday", "monday"] | None = None

    # 24h suits most of the world; the calendar cells are tight either way.
    time_format: Literal["12h", "24h"] = "12h"

    # Design system theme (see stellium.presentation.typst_render.THEMES).
    # "greyscale" is laser-printer safe, which matters more for a planner than a
    # report — people print these at home.
    theme: str = "house"


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
        self._natal_transits = True
        self._natal_transit_planets: list[str] | None = None
        self._natal_transit_points = True
        self._mundane_transits = True
        self._mundane_planets: list[str] | None = None
        self._moon_phases = True
        self._quarter_moons = True
        self._eclipses = True
        self._voc = True
        self._voc_mode: Literal["traditional", "modern"] = "traditional"
        self._ingresses = True
        self._ingress_planets: list[str] | None = None
        self._stations = True
        self._station_planets: list[str] | None = None

        # Page layout
        self._page_size: Literal["a4", "a5", "letter", "half-letter"] = "a4"
        self._binding_margin = 0.0
        self._week_starts_on: Literal["sunday", "monday"] = "sunday"
        self._weekly_starts_on: Literal["sunday", "monday"] | None = None
        self._time_format: Literal["12h", "24h"] = "12h"

        # Design system theme
        self._theme = "house"

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
        Set the timezone the planner is written in.

        This is required. Every event time is shown in this timezone, and each
        page's day runs from local midnight to midnight here. It changes only how
        times are *displayed* and which day an event lands on — the astronomy is
        computed in UTC either way.

        Args:
            tz: IANA timezone (e.g., "America/New_York", "Europe/London")

        Returns:
            Self for chaining
        """
        import pytz

        try:
            pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            raise ValueError(
                f"Unknown timezone {tz!r}. Use an IANA name such as "
                "'America/New_York' or 'Europe/London'."
            ) from None
        self._timezone = tz
        return self

    def location(self, location: str | tuple[float, float]) -> PlannerBuilder:
        """
        Set where the planner will be used.

        The solar return is cast for this place (a relocated return), and the
        title page says the times are local to it. It does not change the times
        themselves — those follow ``.timezone()``. Without it, the solar return is
        cast for the birth place and the title page names the timezone.

        Args:
            location: City name or (latitude, longitude) tuple

        Returns:
            Self for chaining
        """
        self._location = location
        return self

    # ===== Theme =====

    def theme(self, name: str) -> PlannerBuilder:
        """Choose the design-system theme.

        One of ``house`` (default), ``sepia``, ``celestial``, ``blues``, or
        ``greyscale``. Prefer ``greyscale`` if the planner is destined for a home
        laser printer — it swaps ink fills for outlines.

        Example:
            >>> PlannerBuilder.for_native(native).year(2026).theme("greyscale")
        """
        from stellium.presentation.typst_runtime import THEMES

        _check_choice("theme", name, THEMES)
        self._theme = name
        return self

    def time_format(self, fmt: Literal["12h", "24h"]) -> PlannerBuilder:
        """Render event times as 12-hour (``2:49p``) or 24-hour (``14:49``).

        Example:
            >>> PlannerBuilder.for_native(native).year(2026).time_format("24h")
        """
        _check_choice("time format", fmt, TIME_FORMATS)
        self._time_format = fmt
        return self

    def weekly_starts_on(self, day: Literal["sunday", "monday"]) -> PlannerBuilder:
        """First day of the *weekly* pages, independent of the month grid.

        The month grid and the weekly pages are different reading surfaces — a US
        reader often wants a Sunday-led month but a Monday-led working week. If
        this is never called, the weekly pages follow ``week_starts_on``.
        """
        _check_choice("weekday", day, WEEKDAYS)
        self._weekly_starts_on = day
        return self

    # ===== Front Matter Configuration =====
    #
    # The front matter is curated by default — a planner should be useful out of
    # the box — so these are opt-*outs*. Use ``.without_*()`` to drop a page.

    def without_natal_chart(self) -> PlannerBuilder:
        """Drop the natal reference page."""
        return self.with_natal_chart(False)

    def without_progressed_chart(self) -> PlannerBuilder:
        """Drop the progressed-Moon page."""
        return self.with_progressed_chart(False)

    def without_solar_return(self) -> PlannerBuilder:
        """Drop the solar return chart."""
        return self.with_solar_return(False)

    def without_profections(self) -> PlannerBuilder:
        """Drop the profections wheel."""
        return self.with_profections(False)

    def without_zr_timeline(self) -> PlannerBuilder:
        """Drop the zodiacal-releasing page."""
        return self.with_zr_timeline(enabled=False)

    def without_graphic_ephemeris(self) -> PlannerBuilder:
        """Drop the year's transit map."""
        return self.with_graphic_ephemeris(enabled=False)

    def with_natal_chart(self, enabled: bool = True) -> PlannerBuilder:
        """Include natal chart wheel in front matter."""
        self._natal_chart = enabled
        return self

    def with_progressed_chart(self, enabled: bool = True) -> PlannerBuilder:
        """Include the progressed-Moon page in the front matter."""
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
        _check_choice("graphic ephemeris harmonic", harmonic, EPHEMERIS_HARMONICS)
        self._graphic_ephemeris = enabled
        self._graphic_ephemeris_harmonic = harmonic
        return self

    # ===== Daily Content Configuration =====

    def include_natal_transits(
        self,
        planets: list[str] | None = None,
        *,
        to_angles: bool = True,
        enabled: bool = True,
    ) -> PlannerBuilder:
        """
        Include transits to the natal chart on the daily pages.

        Args:
            planets: Which transiting planets to include. Default (None) uses all
                ten planets plus the True Node and Chiron. (The transiting Moon
                contributes conjunctions only — it would otherwise be two-thirds of
                every page.) The year's "Transits That Shape the Year" page always
                lists only the slow planets, Jupiter through Pluto, narrowed to
                this choice.
            to_angles: Also find transits to the natal Ascendant, Midheaven and
                North Node, not just the planets (default True)
            enabled: False drops natal transits from the daily pages

        Returns:
            Self for chaining
        """
        self._natal_transits = enabled
        self._natal_transit_planets = planets
        self._natal_transit_points = to_angles
        return self

    def exclude_natal_transits(self) -> PlannerBuilder:
        """Leave natal transits off the daily pages."""
        self._natal_transits = False
        return self

    def include_mundane_transits(
        self, enabled: bool = True, planets: list[str] | None = None
    ) -> PlannerBuilder:
        """Include mundane transits (planet-to-planet in sky).

        Args:
            enabled: Whether to include them
            planets: Which bodies to pair up (default: the ten planets)
        """
        self._mundane_transits = enabled
        self._mundane_planets = planets
        return self

    def exclude_mundane_transits(self) -> PlannerBuilder:
        """Leave planet-to-planet aspects off the daily pages."""
        self._mundane_transits = False
        return self

    def include_moon_phases(
        self, enabled: bool = True, quarters: bool = True
    ) -> PlannerBuilder:
        """Include Moon phases.

        Args:
            enabled: Whether to include New and Full Moons
            quarters: Also include the First and Last Quarter Moons
        """
        self._moon_phases = enabled
        self._quarter_moons = quarters
        return self

    def include_eclipses(self, enabled: bool = True) -> PlannerBuilder:
        """Include solar and lunar eclipses on the daily pages (default on)."""
        self._eclipses = enabled
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
        _check_choice("VOC mode", mode, VOC_MODES)
        self._voc = True
        self._voc_mode = mode
        return self

    def exclude_voc(self) -> PlannerBuilder:
        """Exclude Void of Course Moon periods."""
        self._voc = False
        return self

    def include_ingresses(
        self, planets: list[str] | None = None, enabled: bool = True
    ) -> PlannerBuilder:
        """
        Include planet sign ingresses on the daily pages.

        Args:
            planets: Which planets to track. Default (None): all ten planets, the
                True Node and Chiron.
            enabled: False drops ingresses from the daily pages

        Returns:
            Self for chaining
        """
        self._ingresses = enabled
        self._ingress_planets = planets
        return self

    def exclude_ingresses(self) -> PlannerBuilder:
        """Leave sign ingresses off the daily pages."""
        self._ingresses = False
        return self

    def include_stations(
        self, planets: list[str] | None = None, enabled: bool = True
    ) -> PlannerBuilder:
        """
        Include retrograde/direct stations on the daily pages.

        Args:
            planets: Which planets to track. Default (None): Mercury through
                Pluto, plus Chiron.
            enabled: False drops stations from the daily pages

        Returns:
            Self for chaining
        """
        self._stations = enabled
        self._station_planets = planets
        return self

    def exclude_stations(self) -> PlannerBuilder:
        """Leave stations off the daily pages."""
        self._stations = False
        return self

    # ===== Page Layout Configuration =====

    def page_size(
        self, size: Literal["a4", "a5", "letter", "half-letter"]
    ) -> PlannerBuilder:
        """
        Set page size.

        Args:
            size: "a4" (default), "a5", "letter", or "half-letter" (US Statement,
                5.5 × 8.5 in — close to A5 but not the same paper)

        Returns:
            Self for chaining
        """
        _check_choice("page size", size, PAGE_SIZES)
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
        if inches < 0:
            raise ValueError("Binding margin cannot be negative")
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
        _check_choice("weekday", day, WEEKDAYS)
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
            include_natal_transits=self._natal_transits,
            natal_transit_planets=self._natal_transit_planets,
            natal_transit_points=self._natal_transit_points,
            include_mundane_transits=self._mundane_transits,
            mundane_planets=self._mundane_planets,
            include_moon_phases=self._moon_phases,
            include_quarter_moons=self._quarter_moons,
            include_eclipses=self._eclipses,
            include_voc=self._voc,
            voc_mode=self._voc_mode,
            include_ingresses=self._ingresses,
            ingress_planets=self._ingress_planets,
            include_stations=self._stations,
            station_planets=self._station_planets,
            page_size=self._page_size,
            binding_margin=self._binding_margin,
            week_starts_on=self._week_starts_on,
            weekly_starts_on=self._weekly_starts_on,
            time_format=self._time_format,
            theme=self._theme,
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
