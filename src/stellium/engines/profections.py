"""
Profection calculation engine.

Profections are a Hellenistic timing technique where the Ascendant (and other
points) move forward one sign per year of life. The planet ruling the profected
sign becomes the "Lord of the Year" - a key focus for that year's themes.

Example:
    >>> from stellium import ChartBuilder
    >>> from stellium.engines.profections import ProfectionEngine
    >>>
    >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    >>> engine = ProfectionEngine(chart)
    >>>
    >>> # Annual profection for age 30
    >>> result = engine.annual(30)
    >>> print(f"Age 30: {result.profected_sign} year, Lord = {result.ruler}")
    >>>
    >>> # Multi-point profections
    >>> results = engine.multi(30, points=["ASC", "Sun", "Moon", "MC"])
    >>> print(f"Lords: {results.lords}")
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from stellium.core.models import CalculatedChart, CelestialPosition
from stellium.engines.dignities import DIGNITIES

# Zodiac signs in order (0-indexed: Aries=0, Taurus=1, ...)
SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def sign_to_index(sign: str) -> int:
    """Convert sign name to index (0-11)."""
    return SIGNS.index(sign)


def index_to_sign(index: int) -> str:
    """Convert index to sign name, wrapping around."""
    return SIGNS[index % 12]


def get_sign_ruler(
    sign: str, system: Literal["traditional", "modern"] = "traditional"
) -> str:
    """
    Get the planetary ruler of a zodiac sign.

    Args:
        sign: The zodiac sign name (e.g., "Aries", "Leo")
        system: "traditional" (classical rulerships) or "modern" (includes outer planets)

    Returns:
        The name of the ruling planet
    """
    if sign not in DIGNITIES:
        raise ValueError(f"Unknown sign: {sign}")

    return DIGNITIES[sign][system]["ruler"]


# =============================================================================
# Data Models
# =============================================================================


@dataclass(frozen=True)
class ProfectionResult:
    """
    Result of profecting a single point.

    Contains everything you'd want to know about a profection:
    what was profected, where it landed, who rules it, and what's there.

    Attributes:
        source_point: Name of the profected point ("ASC", "Sun", etc.)
        source_sign: The sign the point is in natally
        source_house: The house the point is in natally (1-12)
        units: How many signs forward the point moved
        unit_type: Type of profection ("year", "month", "day")
        profected_house: The house that is activated (1-12)
        profected_sign: The sign on that house cusp
        ruler: Traditional ruler of the profected sign (Lord of Year/Month)
        ruler_position: Natal position of the ruling planet
        ruler_house: Which house the ruler is in natally
        ruler_modern: Modern ruler if different from traditional
        planets_in_house: List of natal planets in the profected house
    """

    # What was profected
    source_point: str
    source_sign: str
    source_house: int

    # Profection parameters
    units: int
    unit_type: str

    # The result
    profected_house: int
    profected_sign: str

    # The rulers
    ruler: str
    ruler_position: CelestialPosition | None
    ruler_house: int | None
    ruler_modern: str | None

    # Activated planets
    planets_in_house: tuple[CelestialPosition, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return (
            f"Profection: {self.source_point} → House {self.profected_house} "
            f"({self.profected_sign}), Lord = {self.ruler}"
        )


@dataclass(frozen=True)
class MultiProfectionResult:
    """
    Profections from multiple points for the same time period.

    Useful for seeing all the lords at once - e.g., who rules the
    profected ASC, Sun, Moon, MC, and Fortune for age 30.

    Attributes:
        age: The age for these profections
        date: Optional specific date (for monthly profections)
        results: Dictionary of ProfectionResult keyed by point name
    """

    age: int
    date: datetime | None
    results: dict[str, ProfectionResult]

    @property
    def lords(self) -> dict[str, str]:
        """Get all lords by point name."""
        return {point: r.ruler for point, r in self.results.items()}

    @property
    def activated_houses(self) -> dict[str, int]:
        """Get all activated houses by point name."""
        return {point: r.profected_house for point, r in self.results.items()}

    def __str__(self) -> str:
        lords_str = ", ".join(f"{k}→{v}" for k, v in self.lords.items())
        return f"Profections (age {self.age}): {lords_str}"


@dataclass(frozen=True)
class ProfectionTimeline:
    """
    A range of profections over time.

    Useful for seeing the sequence of lords through a span of life,
    or for displaying in a timeline visualization.

    Attributes:
        point: The point being profected (e.g., "ASC")
        start_age: First age in the timeline
        end_age: Last age in the timeline
        entries: List of ProfectionResult for each age
    """

    point: str
    start_age: int
    end_age: int
    entries: tuple[ProfectionResult, ...]

    def lords_sequence(self) -> list[str]:
        """Get the sequence of lords."""
        return [e.ruler for e in self.entries]

    def find_by_lord(self, lord: str) -> list[ProfectionResult]:
        """Find all years ruled by a specific planet."""
        return [e for e in self.entries if e.ruler == lord]

    def __str__(self) -> str:
        lords = self.lords_sequence()
        return f"Timeline {self.point} ages {self.start_age}-{self.end_age}: {' → '.join(lords)}"


# =============================================================================
# Profection Engine
# =============================================================================


class ProfectionEngine:
    """
    General-purpose profection calculator.

    Profections move a point forward one sign per unit of time (year, month, day).
    This engine handles all the complexity of looking up houses, rulers, and
    finding what planets are activated.

    Args:
        chart: The natal chart to profect from
        house_system: House system to use (default "Whole Sign" - traditional)
        rulership: Rulership system ("traditional" or "modern")

    Example:
        >>> engine = ProfectionEngine(chart)
        >>> result = engine.annual(30)  # Age 30 profection
        >>> print(result.ruler)  # Lord of the Year
    """

    # Default points for multi-point profections
    DEFAULT_POINTS = ["ASC", "Sun", "Moon", "MC"]

    def __init__(
        self,
        chart: CalculatedChart,
        house_system: str | None = None,
        rulership: Literal["traditional", "modern"] = "traditional",
    ):
        self.chart = chart
        self.rulership = rulership

        # Determine which house system to use
        # Priority: explicit parameter > Whole Sign if available > chart default
        if house_system is None:
            # Prefer Whole Sign (traditional for profections) if available
            available = list(chart.house_systems.keys())
            whole_sign_variants = [h for h in available if "whole" in h.lower()]
            if whole_sign_variants:
                house_system = whole_sign_variants[0]
            else:
                # Fall back to chart's default house system
                house_system = chart.default_house_system

        self.house_system = house_system

        # Get house cusps for this system
        # Try the exact name first, then try common variations
        try:
            self._houses = chart.get_houses(house_system)
        except KeyError as err:
            # Try to find a matching house system
            available = list(chart.house_systems.keys())
            matching = [h for h in available if house_system.lower() in h.lower()]
            if matching:
                self._houses = chart.get_houses(matching[0])
                self.house_system = matching[0]
            else:
                raise ValueError(
                    f"House system '{house_system}' not found. Available: {available}"
                ) from err

    # =========================================================================
    # Layer 0-1: Core Profection
    # =========================================================================

    def profect(
        self,
        point: str,
        units: int,
        unit_type: str = "year",
    ) -> ProfectionResult:
        """
        Core profection operation.

        Profects any point forward by N signs and returns everything
        you'd want to know about the result.

        Args:
            point: Point to profect ("ASC", "Sun", "Moon", "MC", etc.)
            units: Number of signs to move forward (typically age for years)
            unit_type: Type of profection ("year", "month", "day")

        Returns:
            ProfectionResult with full details

        Example:
            >>> result = engine.profect("ASC", units=30, unit_type="year")
            >>> print(f"House {result.profected_house}: {result.profected_sign}")
        """
        # Get source info based on point type
        if point == "ASC":
            source_house = 1
            source_sign = self._houses.get_sign(1)
        elif point in ["MC", "DSC", "IC"]:
            # Angles
            pos = self.chart.get_object(point)
            if pos is None:
                raise ValueError(f"Angle '{point}' not found in chart")
            source_sign = pos.sign
            source_house = self.chart.get_house(point, self.house_system) or 1
        else:
            # Planets, lots, etc.
            pos = self.chart.get_object(point)
            if pos is None:
                raise ValueError(f"Point '{point}' not found in chart")
            source_sign = pos.sign
            source_house = self.chart.get_house(point, self.house_system) or 1

        # Calculate profected house (1-indexed)
        # Age 0 = house 1 (1st house), Age 1 = house 2, etc.
        # Formula: ((source_house - 1) + units) % 12 + 1
        profected_house = ((source_house - 1 + units) % 12) + 1

        # Get the sign on that house cusp
        profected_sign = self._houses.get_sign(profected_house)

        # Get rulers
        ruler = get_sign_ruler(profected_sign, self.rulership)
        ruler_modern = get_sign_ruler(profected_sign, "modern")
        if ruler == ruler_modern:
            ruler_modern = None  # Don't repeat if same

        # Get ruler's natal position and house
        ruler_position = self.chart.get_object(ruler)
        ruler_house = self.chart.get_house(ruler, self.house_system)

        # Find planets in the profected house
        planets_in_house = tuple(
            p
            for p in self.chart.get_planets()
            if self.chart.get_house(p.name, self.house_system) == profected_house
        )

        return ProfectionResult(
            source_point=point,
            source_sign=source_sign,
            source_house=source_house,
            units=units,
            unit_type=unit_type,
            profected_house=profected_house,
            profected_sign=profected_sign,
            ruler=ruler,
            ruler_position=ruler_position,
            ruler_house=ruler_house,
            ruler_modern=ruler_modern,
            planets_in_house=planets_in_house,
        )

    # =========================================================================
    # Layer 2: Convenience Methods
    # =========================================================================

    def annual(self, age: int, point: str = "ASC") -> ProfectionResult:
        """
        Annual profection for a given age.

        This is the most common use case: what house and lord are
        activated for a specific year of life?

        Args:
            age: Age in completed years (0 = first year of life)
            point: Point to profect (default "ASC")

        Returns:
            ProfectionResult for that age

        Example:
            >>> result = engine.annual(30)
            >>> print(f"At age 30: {result.profected_sign} year")
            >>> print(f"Lord of the Year: {result.ruler}")
        """
        if age < 0:
            raise ValueError("Age cannot be negative")
        return self.profect(point=point, units=age, unit_type="year")

    def lord_of_year(self, age: int, point: str = "ASC") -> str:
        """
        Convenience: just get the Lord of the Year.

        Args:
            age: Age in completed years
            point: Point to profect (default "ASC")

        Returns:
            Name of the ruling planet

        Example:
            >>> print(engine.lord_of_year(30))  # "Saturn"
        """
        return self.annual(age, point).ruler

    def monthly(
        self,
        age: int,
        month: int,
        point: str = "ASC",
    ) -> ProfectionResult:
        """
        Monthly profection within a given year.

        Profects forward by (age + month) signs total.

        Args:
            age: Age in completed years
            month: Month within the profection year (0-11)
            point: Point to profect (default "ASC")

        Returns:
            ProfectionResult for that month

        Example:
            >>> # 4th month of age 30 year
            >>> result = engine.monthly(age=30, month=4)
            >>> print(f"Month 4: {result.profected_sign}")
        """
        if age < 0:
            raise ValueError("Age cannot be negative")
        if not 0 <= month <= 11:
            raise ValueError("Month must be 0-11")

        total_signs = age + month
        return self.profect(point=point, units=total_signs, unit_type="month")

    def lord_of_month(self, age: int, month: int, point: str = "ASC") -> str:
        """
        Convenience: just get the Lord of the Month.

        Args:
            age: Age in completed years
            month: Month within profection year (0-11)
            point: Point to profect (default "ASC")

        Returns:
            Name of the ruling planet
        """
        return self.monthly(age, month, point).ruler

    # =========================================================================
    # Layer 3: Date-Aware Methods (Solar Ingress)
    # =========================================================================

    def for_date(
        self,
        date: datetime | str,
        point: str = "ASC",
        include_monthly: bool = True,
    ) -> ProfectionResult | tuple[ProfectionResult, ProfectionResult]:
        """
        Calculate profections for a specific date.

        If include_monthly is True, returns both annual and monthly profection.

        Args:
            date: Target date (datetime or ISO string)
            point: Point to profect (default "ASC")
            include_monthly: Whether to calculate monthly profection too

        Returns:
            ProfectionResult, or tuple of (annual, monthly) if include_monthly

        Example:
            >>> annual, monthly = engine.for_date("2025-06-15")
            >>> print(f"Year: {annual.ruler}, Month: {monthly.ruler}")
        """
        if isinstance(date, str):
            date = datetime.fromisoformat(date)

        age = self._calculate_age_at_date(date)
        annual = self.annual(age, point)

        if not include_monthly:
            return annual

        month = self._calculate_month_in_year(date, age)
        monthly = self.monthly(age, month, point)

        return annual, monthly

    def _calculate_age_at_date(self, date: datetime) -> int:
        """Calculate completed years since birth."""
        birth = self.chart.datetime.local_datetime
        if birth is None:
            birth = self.chart.datetime.utc_datetime

        age = date.year - birth.year
        if (date.month, date.day) < (birth.month, birth.day):
            age -= 1
        return max(0, age)

    def _calculate_month_in_year(self, date: datetime, age: int) -> int:
        """
        Calculate which month (0-11) within the profection year.

        Uses the solar ingress method: each month starts when the
        transiting Sun enters a new sign.

        Args:
            date: Target date
            age: Age at target date

        Returns:
            Month number 0-11 within the profection year
        """
        from stellium.utils.planetary_crossing import find_planetary_crossing
        from stellium.utils.time import datetime_to_julian_day

        # Get the birth date and Sun position
        natal_sun = self.chart.get_object("Sun")
        if natal_sun is None:
            raise ValueError("Cannot calculate monthly profection: no Sun in chart")

        natal_sun_long = natal_sun.longitude
        birth_jd = self.chart.datetime.julian_day

        # Find this year's solar return (start of profection year)
        from stellium.utils.planetary_crossing import find_nth_return

        if age == 0:
            year_start_jd = birth_jd
        else:
            year_start_jd = find_nth_return("Sun", natal_sun_long, birth_jd, n=age)

        # Current date as JD
        current_jd = datetime_to_julian_day(date)

        # Find each solar ingress after the solar return
        # Month 0 = from solar return until Sun enters next sign
        # Month 1 = from first ingress to second ingress, etc.

        # Starting sign (at solar return)
        start_sign_index = int(natal_sun_long // 30)

        month = 0
        search_jd = year_start_jd

        for m in range(12):
            # Find when Sun enters the next sign
            next_sign_index = (start_sign_index + 1 + m) % 12
            next_sign_degree = next_sign_index * 30

            try:
                ingress_jd = find_planetary_crossing(
                    "Sun", next_sign_degree, search_jd, direction=1
                )

                if ingress_jd > current_jd:
                    # Current date is before this ingress, so we're in month m
                    break

                month = m + 1
                search_jd = ingress_jd + 0.1  # Move past ingress

            except ValueError:
                # Shouldn't happen within a year, but be safe
                break

        return min(month, 11)

    # =========================================================================
    # Layer 4: Multi-Point Methods
    # =========================================================================

    def multi(
        self,
        age: int,
        points: list[str] | None = None,
    ) -> MultiProfectionResult:
        """
        Profect multiple points at once.

        Useful for seeing all the lords for a given age -
        who rules the profected ASC, Sun, Moon, MC?

        Args:
            age: Age in completed years
            points: Points to profect (default: ASC, Sun, Moon, MC)

        Returns:
            MultiProfectionResult with all profections

        Example:
            >>> results = engine.multi(30)
            >>> print(results.lords)  # {"ASC": "Saturn", "Sun": "Mars", ...}
        """
        if points is None:
            points = self.DEFAULT_POINTS

        results = {point: self.annual(age, point) for point in points}

        return MultiProfectionResult(age=age, date=None, results=results)

    def multi_for_date(
        self,
        date: datetime | str,
        points: list[str] | None = None,
    ) -> MultiProfectionResult:
        """
        Profect multiple points for a specific date.

        Args:
            date: Target date
            points: Points to profect (default: ASC, Sun, Moon, MC)

        Returns:
            MultiProfectionResult with date attached
        """
        if isinstance(date, str):
            date = datetime.fromisoformat(date)

        age = self._calculate_age_at_date(date)
        result = self.multi(age, points)

        # Return with date attached
        return MultiProfectionResult(age=age, date=date, results=result.results)

    # =========================================================================
    # Layer 5: Timeline
    # =========================================================================

    def timeline(
        self,
        start_age: int,
        end_age: int,
        point: str = "ASC",
    ) -> ProfectionTimeline:
        """
        Generate profections for a range of ages.

        Useful for seeing the sequence of lords through life,
        or for timeline visualizations.

        Args:
            start_age: First age (inclusive)
            end_age: Last age (inclusive)
            point: Point to profect (default "ASC")

        Returns:
            ProfectionTimeline with all entries

        Example:
            >>> timeline = engine.timeline(25, 35)
            >>> for entry in timeline.entries:
            ...     print(f"Age {entry.units}: {entry.ruler}")
        """
        if start_age < 0:
            raise ValueError("start_age cannot be negative")
        if end_age < start_age:
            raise ValueError("end_age must be >= start_age")

        entries = tuple(
            self.annual(age, point) for age in range(start_age, end_age + 1)
        )

        return ProfectionTimeline(
            point=point,
            start_age=start_age,
            end_age=end_age,
            entries=entries,
        )
