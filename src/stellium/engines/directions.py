"""Primary directions calculation engine.

This module provides primary directions calculations for Stellium, supporting
both zodiacal (2D/Regiomontanus-style) and mundane (3D/Placidus) methods.

Primary directions track when a "promissor" (moving point) reaches a
"significator" (target point) via the Earth's daily rotation. The resulting
arc is converted to years using a time key.

Example:
    >>> from stellium.engines.directions import DirectionsEngine
    >>> engine = DirectionsEngine(chart)
    >>> result = engine.direct("Sun", "ASC")
    >>> print(f"Sun to ASC: age {result.age:.1f}")
"""

from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

import swisseph as swe

from stellium.engines.dignities import DIGNITIES

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart, CelestialPosition


# =============================================================================
# SECTION 1: DATA MODELS (frozen dataclasses)
# =============================================================================


@dataclass(frozen=True)
class EquatorialPoint:
    """A point in equatorial coordinates (RA/Dec).

    This is the universal coordinate system for primary directions.
    All chart positions are converted to this format before calculation.

    Attributes:
        name: Name of the point (e.g., "Sun", "ASC")
        right_ascension: Right ascension in degrees (0-360)
        declination: Declination in degrees (-90 to +90)
    """

    name: str
    right_ascension: float
    declination: float


@dataclass(frozen=True)
class MundanePosition:
    """A point with full mundane (house-space) context.

    Knows its position relative to the local horizon/meridian system.
    Used by the MundaneDirections method for Placidus-style calculations.

    Attributes:
        point: The underlying equatorial point
        meridian_distance: Degrees from MC (-180 to +180, positive = east)
        semi_arc_diurnal: Degrees of the day arc radius
        semi_arc_nocturnal: Degrees of the night arc radius
        is_above_horizon: True if point is above the horizon
        is_eastern: True if point is on the rising (eastern) side
    """

    point: EquatorialPoint
    meridian_distance: float
    semi_arc_diurnal: float
    semi_arc_nocturnal: float
    is_above_horizon: bool
    is_eastern: bool

    @property
    def current_semi_arc(self) -> float:
        """Which semi-arc is currently applicable."""
        return (
            self.semi_arc_diurnal if self.is_above_horizon else self.semi_arc_nocturnal
        )

    @property
    def mundane_ratio(self) -> float:
        """Position as fraction of semi-arc (0=meridian, 1=horizon)."""
        if self.current_semi_arc == 0:
            return 0.0
        return abs(self.meridian_distance) / self.current_semi_arc


@dataclass(frozen=True)
class DirectionArc:
    """The result of a primary direction calculation.

    Attributes:
        promissor: Name of the moving point
        significator: Name of the target point
        arc_degrees: The calculated arc in degrees
        method: Direction method used ("zodiacal" or "mundane")
        direction: "direct" or "converse"
    """

    promissor: str
    significator: str
    arc_degrees: float
    method: str
    direction: str = "direct"


@dataclass(frozen=True)
class DirectionResult:
    """Complete result of directing one point to another.

    Attributes:
        arc: The direction arc details
        date: Calendar date when the direction perfects (if calculable)
        age: Age in years when the direction perfects (if calculable)
    """

    arc: DirectionArc
    date: dt.datetime | None = None
    age: float | None = None


@dataclass(frozen=True)
class TimeLordPeriod:
    """A period ruled by a term/bound lord.

    Used in distributions to track which planetary term the directed
    Ascendant occupies at different ages.

    Attributes:
        ruler: Name of the ruling planet
        start_date: Date this period begins
        start_age: Age when this period begins
        sign: Zodiac sign containing this term
        end_date: Date this period ends (optional)
        end_age: Age when this period ends (optional)
    """

    ruler: str
    start_date: dt.datetime
    start_age: float
    sign: str = ""
    end_date: dt.datetime | None = None
    end_age: float | None = None


@dataclass(frozen=True)
class TermBoundary:
    """Represents the starting boundary of a term.

    Attributes:
        absolute_degree: Position in the zodiac (0-360)
        ruler: Planet ruling this term
        sign: Zodiac sign name
    """

    absolute_degree: float
    ruler: str
    sign: str


# =============================================================================
# SECTION 2: PROTOCOLS
# =============================================================================


class DirectionMethod(Protocol):
    """Protocol for direction calculation methods.

    Different implementations provide different mathematical approaches:
    - ZodiacalDirections: Projects onto ecliptic plane (2D)
    - MundaneDirections: Uses house-space proportions (3D/Placidus)
    """

    @property
    def method_name(self) -> str:
        """Name of this direction method."""
        ...

    def calculate_arc(
        self,
        promissor: EquatorialPoint,
        significator: EquatorialPoint,
        latitude: float,
        ramc: float,
    ) -> float:
        """Calculate the arc between promissor and significator.

        Args:
            promissor: The moving point
            significator: The target point
            latitude: Geographic latitude of the observer
            ramc: Right Ascension of the Medium Coeli (MC)

        Returns:
            Arc in degrees
        """
        ...


class TimeKey(Protocol):
    """Protocol for converting arcs to time.

    Different keys represent different symbolic rates of motion:
    - Ptolemy: 1 degree = 1 year
    - Naibod: Based on mean solar motion (~1.0146 years/degree)
    """

    @property
    def key_name(self) -> str:
        """Name of this time key."""
        ...

    def arc_to_years(self, arc: float) -> float:
        """Convert arc to years."""
        ...

    def arc_to_date(self, arc: float, birth_date: dt.datetime) -> dt.datetime:
        """Convert arc to calendar date from birth."""
        ...


# =============================================================================
# SECTION 3: SPHERICAL MATH (pure functions)
# =============================================================================


def ascensional_difference(declination: float, pole: float) -> float:
    """Calculate ascensional difference (the 'wobble' from pole tilt).

    The ascensional difference is how much a point's rising/setting time
    deviates from 6 hours due to both its own declination and the observer's
    latitude (pole).

    Formula: sin(AD) = tan(dec) * tan(pole)

    Args:
        declination: Declination of the point in degrees
        pole: Geographic latitude (or pole of a house) in degrees

    Returns:
        Ascensional difference in degrees
    """
    try:
        rad_dec = math.radians(declination)
        rad_pole = math.radians(pole)

        wobble_factor = math.tan(rad_dec) * math.tan(rad_pole)
        # Clamp to valid range for arcsin
        wobble_factor = max(-1.0, min(1.0, wobble_factor))

        return math.degrees(math.asin(wobble_factor))

    except ValueError:
        # Circumpolar point (never rises/sets)
        return 0.0


def semi_arcs(declination: float, latitude: float) -> tuple[float, float]:
    """Calculate diurnal and nocturnal semi-arcs.

    A semi-arc is half the arc a point travels above (diurnal) or below
    (nocturnal) the horizon. At the equator with 0 declination, both are 90.

    Args:
        declination: Declination of the point in degrees
        latitude: Geographic latitude in degrees

    Returns:
        Tuple of (diurnal_semi_arc, nocturnal_semi_arc) in degrees
    """
    ad = ascensional_difference(declination, latitude)
    dsa = 90.0 + ad  # Day arc
    nsa = 90.0 - ad  # Night arc (they sum to 180)
    return dsa, nsa


def meridian_distance(right_ascension: float, ramc: float) -> float:
    """Calculate distance from the upper meridian (MC).

    Positive values indicate the point is east (rising toward MC).
    Negative values indicate the point is west (setting from MC).

    Args:
        right_ascension: RA of the point in degrees
        ramc: Right Ascension of MC in degrees

    Returns:
        Meridian distance in degrees (-180 to +180)
    """
    dist = right_ascension - ramc

    # Normalize to -180 to +180
    while dist > 180:
        dist -= 360
    while dist < -180:
        dist += 360

    return dist


def oblique_ascension(right_ascension: float, declination: float, pole: float) -> float:
    """Calculate oblique ascension.

    Oblique ascension is the RA adjusted for the pole (geographic latitude
    or house pole). It's used in zodiacal directions.

    Formula: OA = RA - AD

    Args:
        right_ascension: RA in degrees
        declination: Declination in degrees
        pole: Pole (latitude) in degrees

    Returns:
        Oblique ascension in degrees (0-360)
    """
    ad = ascensional_difference(declination, pole)
    return (right_ascension - ad) % 360.0


def get_obliquity(julian_day: float) -> float:
    """Get the true obliquity of the ecliptic for a given time.

    Args:
        julian_day: Julian day number

    Returns:
        True obliquity in degrees
    """
    result = swe.calc_ut(julian_day, swe.ECL_NUT)
    return result[0][0]


def ecliptic_to_equatorial(
    longitude: float, latitude: float, obliquity: float
) -> tuple[float, float]:
    """Convert ecliptic coordinates to equatorial.

    Args:
        longitude: Ecliptic longitude in degrees
        latitude: Ecliptic latitude in degrees (usually 0 for zodiacal points)
        obliquity: Obliquity of the ecliptic in degrees

    Returns:
        Tuple of (right_ascension, declination) in degrees
    """
    ra, dec, _ = swe.cotrans((longitude, latitude, 1.0), -obliquity)
    return ra, dec


# =============================================================================
# SECTION 4: TIME KEYS
# =============================================================================


class PtolemyKey:
    """The Classic Key: 1 degree = 1 year.

    The simplest and oldest time key, attributed to Ptolemy.
    """

    @property
    def key_name(self) -> str:
        return "Ptolemy"

    def arc_to_years(self, arc: float) -> float:
        """1 degree = 1 year."""
        return arc

    def arc_to_date(self, arc: float, birth_date: dt.datetime) -> dt.datetime:
        """Convert arc to date using 1 deg = 1 year."""
        days_to_add = arc * 365.25
        return birth_date + dt.timedelta(days=days_to_add)


class NaibodKey:
    """The Precision Key: Based on mean solar motion.

    Uses the Sun's mean daily motion of 59'08" (0.9856 deg per day).
    This makes 1 deg approx 1.0146 years.
    """

    # Solar year in days / degrees in a circle
    DAYS_PER_DEGREE = 365.25 / 360.0 * 365.25  # ~370.56

    @property
    def key_name(self) -> str:
        return "Naibod"

    def arc_to_years(self, arc: float) -> float:
        """Convert arc to years using Naibod rate."""
        return arc * (self.DAYS_PER_DEGREE / 365.25)

    def arc_to_date(self, arc: float, birth_date: dt.datetime) -> dt.datetime:
        """Convert arc to date using Naibod rate."""
        days_to_add = arc * self.DAYS_PER_DEGREE
        return birth_date + dt.timedelta(days=days_to_add)


# =============================================================================
# SECTION 5: DIRECTION METHOD IMPLEMENTATIONS
# =============================================================================


class ZodiacalDirections:
    """Zodiacal (Regiomontanus-style) primary directions.

    Projects points onto the ecliptic plane. The significator's pole
    determines the projection plane. This is the "2D" method.

    In zodiacal directions, we compare oblique ascensions calculated
    using the same pole (typically the geographic latitude for ASC).
    """

    @property
    def method_name(self) -> str:
        return "zodiacal"

    def calculate_arc(
        self,
        promissor: EquatorialPoint,
        significator: EquatorialPoint,
        latitude: float,
        ramc: float,  # noqa: ARG002 - required by protocol, used by MundaneDirections
    ) -> float:
        """Calculate zodiacal arc via oblique ascension difference.

        The arc is the difference in oblique ascension between the
        promissor and significator, using the same pole for both.
        """
        _ = ramc  # Unused in zodiacal method, but required by protocol
        # Use geographic latitude as the pole (for directions to ASC)
        pole = latitude

        oa_prom = oblique_ascension(
            promissor.right_ascension,
            promissor.declination,
            pole,
        )
        oa_sig = oblique_ascension(
            significator.right_ascension,
            significator.declination,
            pole,
        )

        arc = (oa_prom - oa_sig) % 360.0

        return arc


class MundaneDirections:
    """Mundane (Placidus) primary directions.

    Uses house-space proportions. The promissor must travel to reach
    the same "mundane ratio" as the significator. This is the "3D" method.

    The mundane ratio is how far through its current semi-arc a point has
    traveled (0 = at meridian, 1 = at horizon).
    """

    @property
    def method_name(self) -> str:
        return "mundane"

    def _to_mundane(
        self,
        point: EquatorialPoint,
        latitude: float,
        ramc: float,
    ) -> MundanePosition:
        """Convert equatorial point to mundane position."""
        dsa, nsa = semi_arcs(point.declination, latitude)
        md = meridian_distance(point.right_ascension, ramc)

        return MundanePosition(
            point=point,
            meridian_distance=md,
            semi_arc_diurnal=dsa,
            semi_arc_nocturnal=nsa,
            is_above_horizon=abs(md) <= dsa,
            is_eastern=md >= 0,
        )

    def calculate_arc(
        self,
        promissor: EquatorialPoint,
        significator: EquatorialPoint,
        latitude: float,
        ramc: float,
    ) -> float:
        """Calculate mundane arc using Placidus proportions.

        The promissor must travel until it reaches the same proportional
        position within its semi-arc as the significator.
        """
        prom_m = self._to_mundane(promissor, latitude, ramc)
        sig_m = self._to_mundane(significator, latitude, ramc)

        # Handle special cases for angles
        # ASC: ratio = 1.0 (at eastern horizon)
        # MC: ratio = 0.0 (at upper meridian)
        if sig_m.is_eastern and sig_m.mundane_ratio >= 0.99:
            return self._arc_to_eastern_horizon(prom_m)

        if sig_m.is_above_horizon and sig_m.mundane_ratio <= 0.01:
            return self._arc_to_upper_meridian(prom_m)

        # General case: proportional calculation
        target_ratio = sig_m.mundane_ratio
        target_md = target_ratio * prom_m.current_semi_arc

        return abs(prom_m.meridian_distance) - target_md

    def _arc_to_upper_meridian(self, p: MundanePosition) -> float:
        """Calculate arc to reach the MC."""
        if p.is_eastern:
            return abs(p.meridian_distance)
        return 0.0  # Already past MC

    def _arc_to_eastern_horizon(self, p: MundanePosition) -> float:
        """Calculate arc to reach the Ascendant (eastern horizon)."""
        # Lower East (Q4): Climbing to horizon
        if p.is_eastern and not p.is_above_horizon:
            return p.semi_arc_nocturnal - abs(p.meridian_distance)

        # Lower West (Q3): Must go to IC, then climb
        if not p.is_eastern and not p.is_above_horizon:
            dist_to_ic = 180.0 - abs(p.meridian_distance)
            dist_up_east = p.semi_arc_nocturnal
            return dist_to_ic + dist_up_east

        # Upper West (Q2): Must set, go under, then rise
        if not p.is_eastern and p.is_above_horizon:
            dist_to_set = p.semi_arc_diurnal - abs(p.meridian_distance)
            full_night = p.semi_arc_nocturnal * 2.0
            return dist_to_set + full_night

        # Upper East (Q1): Already past ASC
        return 0.0


# =============================================================================
# SECTION 6: DIRECTIONS ENGINE (main API)
# =============================================================================


class DirectionsEngine:
    """Primary directions calculation engine.

    Calculates primary directions between chart points using either
    zodiacal (2D) or mundane (3D/Placidus) methods.

    Args:
        chart: The natal chart to calculate directions for
        method: Direction method - "zodiacal" (default) or "mundane"
        time_key: Time key - "naibod" (default) or "ptolemy"

    Example:
        >>> engine = DirectionsEngine(chart)
        >>> result = engine.direct("Sun", "ASC")
        >>> print(f"Sun to ASC: age {result.age:.1f}")

        >>> # Compare methods
        >>> z = DirectionsEngine(chart, method="zodiacal").direct("Sun", "ASC")
        >>> m = DirectionsEngine(chart, method="mundane").direct("Sun", "ASC")
    """

    METHODS: dict[str, type[DirectionMethod]] = {
        "zodiacal": ZodiacalDirections,
        "mundane": MundaneDirections,
    }

    TIME_KEYS: dict[str, type[TimeKey]] = {
        "ptolemy": PtolemyKey,
        "naibod": NaibodKey,
    }

    def __init__(
        self,
        chart: CalculatedChart,
        method: str = "zodiacal",
        time_key: str = "naibod",
    ):
        """Initialize the directions engine.

        Args:
            chart: The natal chart
            method: "zodiacal" or "mundane"
            time_key: "ptolemy" or "naibod"
        """
        self.chart = chart
        self._method = self.METHODS[method]()
        self._time_key = self.TIME_KEYS[time_key]()

        # Extract chart context
        self._latitude = chart.location.latitude
        ramc_obj = chart.get_object("RAMC")
        if ramc_obj is None:
            raise ValueError("Chart must have RAMC calculated")
        self._ramc = ramc_obj.longitude
        self._obliquity = get_obliquity(chart.datetime.julian_day)
        self._birth_date = chart.datetime.local_datetime or chart.datetime.utc_datetime

    def _to_equatorial(self, obj: CelestialPosition) -> EquatorialPoint:
        """Convert chart position to equatorial coordinates.

        Handles both planets (which have RA/Dec from ephemeris) and
        angles (which only have ecliptic longitude).
        """
        # For angles, convert from ecliptic
        ra, dec = ecliptic_to_equatorial(obj.longitude, 0.0, self._obliquity)
        return EquatorialPoint(obj.name, ra, dec)

    def direct(
        self,
        promissor: str | CelestialPosition,
        significator: str | CelestialPosition,
        direction: str = "direct",
    ) -> DirectionResult:
        """Calculate a primary direction.

        Args:
            promissor: Name or position of moving point (e.g., "Sun")
            significator: Name or position of target (e.g., "ASC")
            direction: "direct" or "converse"

        Returns:
            DirectionResult with arc, date, and age
        """
        # Resolve names to positions
        prom_pos = (
            self.chart.get_object(promissor)
            if isinstance(promissor, str)
            else promissor
        )
        sig_pos = (
            self.chart.get_object(significator)
            if isinstance(significator, str)
            else significator
        )

        if prom_pos is None:
            raise ValueError(f"Promissor '{promissor}' not found in chart")
        if sig_pos is None:
            raise ValueError(f"Significator '{significator}' not found in chart")

        # Convert and calculate
        prom_eq = self._to_equatorial(prom_pos)
        sig_eq = self._to_equatorial(sig_pos)

        arc = self._method.calculate_arc(prom_eq, sig_eq, self._latitude, self._ramc)

        arc_result = DirectionArc(
            promissor=prom_eq.name,
            significator=sig_eq.name,
            arc_degrees=arc,
            method=self._method.method_name,
            direction=direction,
        )

        return DirectionResult(
            arc=arc_result,
            date=self._time_key.arc_to_date(arc, self._birth_date),
            age=self._time_key.arc_to_years(arc),
        )

    def direct_to_angles(
        self, promissor: str | CelestialPosition
    ) -> dict[str, DirectionResult]:
        """Direct a planet to all four angles.

        Args:
            promissor: Name or position of the planet

        Returns:
            Dictionary mapping angle names to DirectionResults
        """
        angles = ["ASC", "MC", "DSC", "IC"]
        return {angle: self.direct(promissor, angle) for angle in angles}

    def direct_all_to(
        self,
        significator: str | CelestialPosition,
        planets: list[str] | None = None,
    ) -> list[DirectionResult]:
        """Direct multiple planets to a single significator.

        Args:
            significator: The target point
            planets: List of planet names (defaults to traditional planets)

        Returns:
            List of DirectionResults sorted by age
        """
        if planets is None:
            planets = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
            ]

        results = []
        for planet in planets:
            try:
                result = self.direct(planet, significator)
                if result.age is not None and result.age > 0:
                    results.append(result)
            except ValueError:
                continue

        return sorted(results, key=lambda r: r.age or 0)


# =============================================================================
# SECTION 7: DISTRIBUTIONS CALCULATOR (separate class)
# =============================================================================


class DistributionsCalculator:
    """Calculate term/bound distributions.

    Distributions track which planetary term (bound) the directed Ascendant
    occupies at different ages. This creates a timeline of "life chapters"
    ruled by different planets.

    Args:
        chart: The natal chart
        time_key: Time key - "naibod" (default) or "ptolemy"
        bound_system: Which bound system to use (default: "egypt")

    Example:
        >>> calc = DistributionsCalculator(chart)
        >>> periods = calc.calculate(years=80)
        >>> for p in periods:
        ...     print(f"Age {p.start_age:.1f}: {p.ruler} ({p.sign})")
    """

    TIME_KEYS: dict[str, type[TimeKey]] = {
        "ptolemy": PtolemyKey,
        "naibod": NaibodKey,
    }

    def __init__(
        self,
        chart: CalculatedChart,
        time_key: str = "naibod",
        bound_system: str = "egypt",
    ):
        """Initialize the distributions calculator.

        Args:
            chart: The natal chart
            time_key: "ptolemy" or "naibod"
            bound_system: Bound system to use ("egypt")
        """
        self.chart = chart
        self._time_key = self.TIME_KEYS[time_key]()
        self._bound_system = bound_system

        # Extract chart context
        self._latitude = chart.location.latitude
        ramc_obj = chart.get_object("RAMC")
        asc_obj = chart.get_object("ASC")
        if ramc_obj is None:
            raise ValueError("Chart must have RAMC calculated")
        if asc_obj is None:
            raise ValueError("Chart must have ASC calculated")
        self._ramc = ramc_obj.longitude
        self._obliquity = get_obliquity(chart.datetime.julian_day)
        self._birth_date = chart.datetime.local_datetime or chart.datetime.utc_datetime
        self._asc_degree = asc_obj.longitude

        # Load term boundaries
        self._boundaries = self._load_terms()

    def _load_terms(self) -> list[TermBoundary]:
        """Load term boundaries from the dignities data."""
        boundaries = []
        bound_key = f"bound_{self._bound_system}"

        for i, sign_name in enumerate(DIGNITIES.keys()):
            sign_offset = i * 30.0
            sign_data = DIGNITIES.get(sign_name, {})
            bounds = sign_data.get(bound_key, {})

            for local_deg, planet in bounds.items():
                abs_deg = sign_offset + local_deg
                boundaries.append(
                    TermBoundary(
                        absolute_degree=abs_deg,
                        ruler=planet,
                        sign=sign_name,
                    )
                )

        boundaries.sort(key=lambda x: x.absolute_degree)
        return boundaries

    def _create_boundary_point(self, degree: float) -> EquatorialPoint:
        """Create an equatorial point for a zodiacal degree."""
        ra, dec = ecliptic_to_equatorial(degree, 0.0, self._obliquity)
        return EquatorialPoint(f"Term_{degree:.0f}", ra, dec)

    def _calculate_arc_to_degree(self, target_degree: float) -> float:
        """Calculate the arc from ASC to a target zodiacal degree."""
        asc_point = self._create_boundary_point(self._asc_degree)
        target_point = self._create_boundary_point(target_degree)

        # Use zodiacal method for distributions
        method = ZodiacalDirections()
        return method.calculate_arc(target_point, asc_point, self._latitude, self._ramc)

    def calculate(self, years: int = 100) -> list[TimeLordPeriod]:
        """Calculate term distributions for a lifetime.

        Args:
            years: Maximum years to calculate

        Returns:
            List of TimeLordPeriod objects sorted by age
        """
        # Find current term ruler (term containing the ASC)
        start_index = 0
        current_ruler = "Unknown"
        current_sign = ""

        for i, b in enumerate(self._boundaries):
            if b.absolute_degree > self._asc_degree:
                start_index = i
                prev = self._boundaries[i - 1] if i > 0 else self._boundaries[-1]
                current_ruler = prev.ruler
                current_sign = prev.sign
                break

        periods = [
            TimeLordPeriod(
                ruler=current_ruler,
                start_date=self._birth_date,
                start_age=0.0,
                sign=current_sign,
            )
        ]

        # Iterate through boundaries
        current_idx = start_index
        total_boundaries = len(self._boundaries)

        while True:
            target = self._boundaries[current_idx]
            arc = self._calculate_arc_to_degree(target.absolute_degree)

            date = self._time_key.arc_to_date(arc, self._birth_date)
            age = self._time_key.arc_to_years(arc)

            if age > years:
                break

            periods.append(
                TimeLordPeriod(
                    ruler=target.ruler,
                    start_date=date,
                    start_age=age,
                    sign=target.sign,
                )
            )

            current_idx = (current_idx + 1) % total_boundaries

            # Safety break
            if len(periods) > 50:
                break

        return periods
