"""
Comparison chart implementation for synastry, transits, and progressions.

This module provides a unified interface for comparing two charts:
- Synastry: Two natal charts (relationship analysis)
- Transits: Natal chart + current sky positions (timing analysis)
- Progressions: Progressed chart + natal chart (symbolic timing)

The Comparison class mimics CalculatedChart's interface while providing
cross-chart analysis capabilities.

Configuration:
--------------
Uses AspectEngine + OrbEngine for aspect calculations:

**AspectEngine:**
- Determines which aspects to calculate (via AspectConfig)
- CrossChartAspectEngine for cross-chart aspects (chart1 × chart2)
- ModernAspectEngine for internal aspects (if charts lack them)

**OrbEngine:**
- Determines orb allowances for each aspect
- Defaults are comparison-type specific:
  - Synastry: 6°/4° (moderate - connections matter)
  - Transits: 3°/2° (tight - timing precision)
  - Progressions: 1° (very tight - symbolic timing)

Builder Methods:
----------------
**Cross-chart aspects:**
- .with_aspect_engine(engine) - Custom CrossChartAspectEngine
- .with_orb_engine(engine) - Custom orb allowances

**Internal (natal) aspects:**
- .with_internal_aspect_engine(engine) - Engine for chart1/chart2 internal aspects
- .with_internal_orb_engine(engine) - Orbs for internal aspects

**House overlays:**
- .without_house_overlays() - Disable house overlay calculation
"""

import datetime as dt
import warnings
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

from stellium.core.builder import ChartBuilder
from stellium.core.config import AspectConfig
from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    ComparisonAspect,
    ComparisonType,
    HouseCusps,
    HouseOverlay,
    ObjectType,
)
from stellium.core.native import Native
from stellium.core.protocols import OrbEngine

if TYPE_CHECKING:
    from stellium.visualization import ChartDrawBuilder


@dataclass(frozen=True)
class Comparison:
    """
    Comparison between two charts (synastry or transits).

    This class mimics CalculatedChart's interface while providing
    cross-chart analysis. It holds two complete charts and calculates
    their interactions.
    """

    # Chart identification
    comparison_type: ComparisonType

    # The two charts being compared
    chart1: CalculatedChart  # Native/Person A/Inner circle
    chart2: CalculatedChart  # Transit/Person B/Outer circle

    # Calculated comparison data
    cross_aspects: tuple[ComparisonAspect, ...] = ()
    house_overlays: tuple[HouseOverlay, ...] = ()

    # Optional labels for reports
    chart1_label: str = "Native"
    chart2_label: str = "Other"

    # Metadata
    calculation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(dt.UTC)
    )

    def __post_init__(self) -> None:
        """Issue deprecation warning."""
        warnings.warn(
            "Comparison is deprecated, use MultiChart instead. "
            "See stellium.core.multichart.MultiChart for the unified API.",
            DeprecationWarning,
            stacklevel=2,
        )

    # ===== Chart1 (Native/Inner) Convenience Properties =====
    @property
    def datetime(self) -> ChartDateTime:
        """Primary chart datetime (chart1/native)."""
        return self.chart1.datetime

    @property
    def location(self) -> ChartLocation:
        """Primary chart location (chart1/native)."""
        return self.chart1.location

    @property
    def positions(self) -> tuple[CelestialPosition, ...]:
        """Primary chart positions (chart1/native)."""
        return self.chart1.positions

    @property
    def houses(self) -> HouseCusps:
        """Primary chart houses (chart1/native)."""
        return self.chart1.house_systems[self.chart1.default_house_system]

    @property
    def aspects(self) -> tuple[Aspect, ...]:
        """Primary chart's natal aspects (chart1 internal)."""
        return self.chart1.aspects

    # ===== Chart2 (Partner/Transit/Outer) Properties =====

    @property
    def chart2_datetime(self) -> ChartDateTime:
        """Secondary chart datetime."""
        return self.chart2.datetime

    @property
    def chart2_location(self) -> ChartLocation:
        """Secondary chart location."""
        return self.chart2.location

    @property
    def chart2_positions(self) -> tuple[CelestialPosition, ...]:
        """Secondary chart positions."""
        return self.chart2.positions

    @property
    def chart2_houses(self) -> HouseCusps:
        """Secondary chart houses."""
        return self.chart2.house_systems[self.chart2.default_house_system]

    @property
    def chart2_aspects(self) -> tuple[Aspect, ...]:
        """Secondary chart's internal aspects."""
        return self.chart2.aspects

    # ===== Query Methods (mimic CalculatedChart interface) =====

    def get_object(
        self, name: str, chart: Literal[1, 2] = 1
    ) -> CelestialPosition | None:
        """
        Get a celestial object by name from either chart.

        Args:
            name: Object name (e.g., "Sun", "Moon")
            from_chart: Which chart to get from

        Returns:
            CelestialPosition or None
        """
        retrieved_chart = self.chart1 if chart == 1 else self.chart2
        return retrieved_chart.get_object(name)

    def get_planets(self, chart: Literal[1, 2] = 1) -> list[CelestialPosition]:
        """Get all planetary objects from specified chart."""
        retrieved_chart = self.chart1 if chart == 1 else self.chart2
        return retrieved_chart.get_planets()

    def get_angles(self, chart: Literal[1, 2] = 1) -> list[CelestialPosition]:
        """Get all chart angles from specified chart."""
        retrieved_chart = self.chart1 if chart == 1 else self.chart2
        return retrieved_chart.get_angles()

    # ===== Comparison-Specific Query Methods =====

    def get_object_aspects(
        self, object_name: str, chart: Literal[1, 2] = 1
    ) -> list[ComparisonAspect]:
        """
        Get all cross-chart aspects involving a specific object.

        Args:
            object_name: Name of the object
            chart: Which chart the object belongs to

        Returns:
            List of ComparisonAspect objects
        """
        return [
            asp
            for asp in self.cross_aspects
            if (chart == "chart1" and asp.object1.name == object_name)
            or (chart == "chart2" and asp.object2.name == object_name)
        ]

    def get_object_houses(
        self, object_name: str, chart: Literal[1, 2] = 1
    ) -> list[HouseOverlay]:
        """
        Get house overlays for a specific planet.

        Args:
            planet_name: Planet name
            planet_owner: Which chart owns the planet

        Returns:
            List of HouseOverlay objects
        """
        return [
            overlay
            for overlay in self.house_overlays
            if overlay.planet_name == object_name
            and overlay.planet_owner == f"chart{chart}"
        ]

    def get_objects_in_house(
        self,
        house_number: int,
        house_owner: Literal[1, 2],
        planet_owner: Literal[1, 2, "both"] = "both",
    ) -> list[HouseOverlay]:
        """
        Get all planets falling in a specific house.

        Args:
            house_number: House number (1-12)
            house_owner: Whose house system to use
            planet_owner: Whose planets to check (or "both")

        Returns:
            List of HouseOverlay objects
        """
        overlays = [
            overlay
            for overlay in self.house_overlays
            if overlay.falls_in_house == house_number
            and overlay.house_owner == f"chart{house_owner}"
        ]

        if planet_owner != "both":
            overlays = [o for o in overlays if o.planet_owner == f"chart{house_owner}"]

        return overlays

    # ===== Compatibility Scoring (for synastry) =====
    def calculate_compatibility_score(
        self, weights: dict[str, float] | None = None
    ) -> float:
        """
        Calculate a simple compatibility score based on aspects.

        This is a basic implementation - users can implement their own
        weighting schemes.

        Args:
            weights: Optional custom weights for aspect types

        Returns:
            Compatibility score (0-100)
        """
        if weights is None:
            # Default weights: harmonious positive, challenging neutral/negative
            weights = {
                "Conjunction": 0.5,  # Neutral (depends on planets)
                "Sextile": 1.0,  # Harmonious
                "Square": -0.5,  # Challenging
                "Trine": 1.0,  # Harmonious
                "Opposition": -0.3,  # Challenging but connecting
            }

        total_score = 0.0
        max_possible = len(self.cross_aspects)  # Each aspect could be +1

        if max_possible == 0:
            return 50.0  # Neutral if no aspects

        for aspect in self.cross_aspects:
            weight = weights.get(aspect.aspect_name, 0.0)

            # Tighter orbs are stronger
            orb_strength = 1.0 - (aspect.orb / 10.0)  # Assume max 10° orb
            orb_strength = max(0.0, min(1.0, orb_strength))

            total_score += weight * orb_strength

        # Normalize to 0-100 scale
        # Assuming average score per aspect ranges from -0.5 to 1.0
        normalized = ((total_score / max_possible) + 0.5) / 1.5 * 100
        return max(0.0, min(100.0, normalized))

    def draw(self, filename: str = "synastry.svg") -> "ChartDrawBuilder":
        """
        Start building a comparison chart visualization with fluent API.

        This is a convenience method that creates a ChartDrawBuilder for
        easy, discoverable comparison chart visualization. It provides
        synastry-specific presets and a fluent interface for customization.

        Args:
            filename: Output filename for the SVG

        Returns:
            ChartDrawBuilder instance for chaining

        Example::

            # Simple synastry preset
            comparison.draw("synastry.svg").preset_synastry().save()

            # Custom configuration
            comparison.draw("custom.svg").with_theme("celestial").with_moon_phase(
                position="top-left"
            ).with_chart_info(position="top-right").save()
        """
        from stellium.visualization.builder import ChartDrawBuilder

        return ChartDrawBuilder(self).with_filename(filename)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        Returns:
            Dictionary with full comparison data
        """
        return {
            "comparison_type": self.comparison_type.value,
            "chart1_label": self.chart1_label,
            "chart2_label": self.chart2_label,
            "chart1": self.chart1.to_dict(),
            "chart2": self.chart2.to_dict(),
            "cross_aspects": [
                {
                    "object1": asp.object1.name,
                    "object1_chart": "chart1",
                    "object2": asp.object2.name,
                    "object2_chart": "chart2",
                    "aspect": asp.aspect_name,
                    "orb": asp.orb,
                    "is_applying": asp.is_applying,
                    "in_chart1_house": asp.in_chart1_house,
                    "in_chart2_house": asp.in_chart2_house,
                }
                for asp in self.cross_aspects
            ],
            "house_overlays": [
                {
                    "planet": overlay.planet_name,
                    "planet_owner": overlay.planet_owner,
                    "house": overlay.falls_in_house,
                    "house_owner": overlay.house_owner,
                }
                for overlay in self.house_overlays
            ],
        }


# ===== Builder Class with Fluent Interface =====
class ComparisonBuilder:
    """
    Fluent builder for creating Comparison objects.

    Provides convenient construction methods for both synastry and transits:

    For synastry:
        comp = ComparisonBuilder.from_native(chart1) \\
            .with_partner(chart2) \\
            .calculate()

    For transits:
        comp = ComparisonBuilder.from_native(natal_chart) \\
            .with_transit(transit_datetime, transit_location) \\
            .calculate()
    """

    def __init__(
        self,
        chart1: CalculatedChart,
        comparison_type: ComparisonType,
        chart1_label: str = "Native",
    ):
        """
        Initialize builder with the primary chart.

        Args:
            chart1: The native/primary chart (inner circle)
            comparison_type: Type of comparison
            chart1_label: Label for chart1 in reports
        """
        warnings.warn(
            "ComparisonBuilder is deprecated, use MultiChartBuilder instead. "
            "See stellium.core.multichart.MultiChartBuilder for the unified API.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._chart1 = chart1
        self._comparison_type = comparison_type
        self._chart1_label = chart1_label

        self._chart2: CalculatedChart | None = None
        self._chart2_label: str = "Other"

        # Cross-chart aspect configuration
        self._aspect_engine = None  # CrossChartAspectEngine or custom
        self._orb_engine: OrbEngine = self._get_default_comparison_orbs()

        # Internal (natal) aspect configuration for chart1/chart2
        # Used if charts don't already have aspects calculated
        self._internal_aspect_engine = None  # Default: ModernAspectEngine
        self._internal_orb_engine: OrbEngine | None = None  # Default: registry orbs

        # Other options
        self._make_house_overlays: bool = True

    # ===== Convenience Constructors =====
    @classmethod
    def from_native(
        cls, native_chart: CalculatedChart, native_label: str = "Native"
    ) -> "ComparisonBuilder":
        """
        Start building a comparison from a native chart.

        Use this when you have a CalculatedChart already.
        Chain with .with_partner() or .with_transit()

        Args:
            native_chart: The native/primary chart
            native_label: Label for the native chart

        Returns:
            ComparisonBuilder instance
        """
        # We don't know the type yet - will be set by with_partner/with_transit
        return cls(
            native_chart,
            ComparisonType.SYNASTRY,  # Default, will be overridden
            native_label,
        )

    @classmethod
    def compare(
        cls,
        data1: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        data2: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        comparison_type: str,
        chart1_label: str = "Chart 1",
        chart2_label: str = "Chart 2",
    ) -> "ComparisonBuilder":
        """
        General method for creating any type of comparison.

        This is the flexible method that accepts any combination of inputs and any
        comparison type. Convenience methods (.synastry(), .transit(), .progression())
        are thin wrappers that call this method with appropriate defaults.

        Args:
            data1: First chart data (CalculatedChart, Native, or (datetime, location) tuple)
            data2: Second chart data (CalculatedChart, Native, or (datetime, location) tuple)
            comparison_type: Type of comparison ("synastry", "transit", "progression")
            chart1_label: Label for first chart (default: "Chart 1")
            chart2_label: Label for second chart (default: "Chart 2")

        Returns:
            ComparisonBuilder instance ready to configure and calculate

        Examples:
            >>> # With Native objects
            >>> native1 = Native("1994-01-06 11:47", "Palo Alto, CA")
            >>> native2 = Native("2000-01-01 17:00", "Seattle, WA")
            >>> comparison = ComparisonBuilder.compare(native1, native2, "synastry").calculate()
            >>>
            >>> # With (datetime, location) tuples
            >>> comparison = ComparisonBuilder.compare(
            ...     ("1994-01-06 11:47", "Palo Alto, CA"),
            ...     ("2000-01-01 17:00", "Seattle, WA"),
            ...     "synastry"
            ... ).calculate()
            >>>
            >>> # Mixed inputs
            >>> comparison = ComparisonBuilder.compare(
            ...     native1,
            ...     ("2024-11-24 14:30", None),  # Uses chart1's location for transits
            ...     "transit"
            ... ).calculate()
        """
        # Convert comparison_type string to ComparisonType enum
        type_map = {
            "synastry": ComparisonType.SYNASTRY,
            "transit": ComparisonType.TRANSIT,
            "progression": ComparisonType.PROGRESSION,
        }
        comp_type = type_map.get(comparison_type.lower())
        if comp_type is None:
            raise ValueError(
                f"Invalid comparison type: '{comparison_type}'. "
                f"Must be one of: {', '.join(type_map.keys())}"
            )

        # Helper to convert data input to CalculatedChart
        def to_chart(data, location_fallback=None) -> CalculatedChart:
            if isinstance(data, CalculatedChart):
                return data
            elif isinstance(data, Native):
                return ChartBuilder.from_native(data).calculate()
            elif isinstance(data, tuple) and len(data) == 2:
                datetime_input, location_input = data
                # Handle None location (use fallback for transits)
                if location_input is None:
                    if location_fallback is None:
                        raise ValueError(
                            "Location cannot be None unless comparing to an existing chart "
                            "(e.g., for transits)"
                        )
                    location_input = location_fallback
                # Create Native internally (handles all parsing)
                native = Native(datetime_input, location_input)
                return ChartBuilder.from_native(native).calculate()
            else:
                raise TypeError(
                    f"Invalid data type: {type(data)}. "
                    f"Expected CalculatedChart, Native, or (datetime, location) tuple"
                )

        # Convert data1 first
        chart1 = to_chart(data1)

        # Convert data2 (with chart1's location as fallback for transits)
        chart2 = to_chart(data2, location_fallback=chart1.location)

        # Create builder with both charts configured
        builder = cls(chart1, comp_type, chart1_label)
        builder._chart2 = chart2
        builder._chart2_label = chart2_label

        return builder

    @classmethod
    def synastry(
        cls,
        data1: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        data2: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        chart1_label: str = "Person 1",
        chart2_label: str = "Person 2",
    ) -> "ComparisonBuilder":
        """
        Create a synastry comparison between two natal charts.

        Synastry analyzes the relationship between two people by comparing their
        birth charts. This is a convenience method that calls .compare() with
        comparison_type="synastry".

        Args:
            data1: First person's chart data (Native, CalculatedChart, or (datetime, location) tuple)
            data2: Second person's chart data (Native, CalculatedChart, or (datetime, location) tuple)
            chart1_label: Label for first person (default: "Person 1")
            chart2_label: Label for second person (default: "Person 2")

        Returns:
            ComparisonBuilder instance ready to configure and calculate

        Examples:
            >>> # Simple string inputs
            >>> comparison = ComparisonBuilder.synastry(
            ...     ("1994-01-06 11:47", "Palo Alto, CA"),
            ...     ("2000-01-01 17:00", "Seattle, WA")
            ... ).calculate()
            >>>
            >>> # With Native objects
            >>> native1 = Native("1994-01-06 11:47", "Palo Alto, CA")
            >>> native2 = Native("2000-01-01 17:00", "Seattle, WA")
            >>> comparison = ComparisonBuilder.synastry(native1, native2).calculate()
            >>>
            >>> # With custom labels
            >>> comparison = ComparisonBuilder.synastry(
            ...     ("1994-01-06 11:47", "Palo Alto, CA"),
            ...     ("2000-01-01 17:00", "Seattle, WA"),
            ...     chart1_label="Kate",
            ...     chart2_label="Partner"
            ... ).calculate()
        """
        return cls.compare(data1, data2, "synastry", chart1_label, chart2_label)

    @classmethod
    def transit(
        cls,
        natal_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        transit_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict | None],
        natal_label: str = "Natal",
        transit_label: str = "Transit",
    ) -> "ComparisonBuilder":
        """
        Create a transit comparison (natal chart vs current sky positions).

        Transits analyze how current planetary positions interact with a natal chart
        for timing and prediction. This is a convenience method that calls .compare()
        with comparison_type="transit".

        Args:
            natal_data: Natal chart data (Native, CalculatedChart, or (datetime, location) tuple)
            transit_data: Transit time data. Can be:
                - (datetime, location) tuple
                - (datetime, None) to use natal location
                - Native or CalculatedChart
            natal_label: Label for natal chart (default: "Natal")
            transit_label: Label for transit chart (default: "Transit")

        Returns:
            ComparisonBuilder instance ready to configure and calculate

        Examples:
            >>> # Transit using natal location
            >>> comparison = ComparisonBuilder.transit(
            ...     ("1994-01-06 11:47", "Palo Alto, CA"),
            ...     ("2024-11-24 14:30", None)  # Uses Palo Alto
            ... ).calculate()
            >>>
            >>> # Transit with different location
            >>> comparison = ComparisonBuilder.transit(
            ...     ("1994-01-06 11:47", "Palo Alto, CA"),
            ...     ("2024-11-24 14:30", "New York, NY")
            ... ).calculate()
            >>>
            >>> # With Native object
            >>> natal = Native("1994-01-06 11:47", "Palo Alto, CA")
            >>> comparison = ComparisonBuilder.transit(
            ...     natal,
            ...     ("2024-11-24 14:30", None)
            ... ).calculate()
        """
        return cls.compare(
            natal_data, transit_data, "transit", natal_label, transit_label
        )

    @classmethod
    def progression(
        cls,
        natal_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        progressed_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict]
        | None = None,
        *,
        target_date: str | datetime | None = None,
        age: float | None = None,
        angle_method: Literal["quotidian", "solar_arc", "naibod"] = "quotidian",
        natal_label: str = "Natal",
        progressed_label: str = "Progressed",
    ) -> "ComparisonBuilder":
        """
        Create a progression comparison with auto-calculation support.

        Secondary progressions use the symbolic equation "one day = one year."
        To find progressed positions at age 30, look at where planets were
        30 days after birth.

        Can be called three ways:
        1. Auto-calculate by target date: progression(natal, target_date="2025-06-15")
        2. Auto-calculate by age: progression(natal, age=30)
        3. Manual (legacy): progression(natal, progressed_chart)

        Args:
            natal_data: Natal chart data (Native, CalculatedChart, or (datetime, location) tuple)
            progressed_data: Optional pre-calculated progressed chart (for backwards compatibility)
            target_date: Target date for progression (triggers auto-calculation)
            age: Age in years for progression (alternative to target_date)
            angle_method: How to progress angles:
                - "quotidian" (default): Actual daily motion from Swiss Ephemeris
                - "solar_arc": Angles progress at rate of progressed Sun
                - "naibod": Angles progress at mean Sun rate (59'08"/year)
            natal_label: Label for natal chart (default: "Natal")
            progressed_label: Label for progressed chart (default: "Progressed")

        Returns:
            ComparisonBuilder instance ready to configure and calculate

        Examples:
            >>> # Auto-calculate by age (most convenient)
            >>> prog = ComparisonBuilder.progression(natal, age=30).calculate()
            >>>
            >>> # Auto-calculate by target date
            >>> prog = ComparisonBuilder.progression(
            ...     natal, target_date="2025-06-15"
            ... ).calculate()
            >>>
            >>> # With solar arc angles
            >>> prog = ComparisonBuilder.progression(
            ...     natal, age=30, angle_method="solar_arc"
            ... ).calculate()
            >>>
            >>> # Legacy: explicit progressed chart (backwards compatible)
            >>> progressed_chart = ChartBuilder.from_details(
            ...     "1994-02-05 11:47", "Palo Alto, CA"
            ... ).calculate()
            >>> prog = ComparisonBuilder.progression(natal, progressed_chart).calculate()
        """
        from stellium.utils.progressions import (
            calculate_naibod_arc,
            calculate_progressed_datetime,
            calculate_solar_arc,
            calculate_years_elapsed,
        )

        # Helper to convert input to CalculatedChart
        def to_chart(data, location_fallback=None) -> CalculatedChart:
            if isinstance(data, CalculatedChart):
                return data
            elif isinstance(data, Native):
                return ChartBuilder.from_native(data).calculate()
            elif isinstance(data, tuple) and len(data) == 2:
                datetime_input, location_input = data
                if location_input is None:
                    if location_fallback is None:
                        raise ValueError(
                            "Location cannot be None unless comparing to an existing chart"
                        )
                    location_input = location_fallback
                native = Native(datetime_input, location_input)
                return ChartBuilder.from_native(native).calculate()
            else:
                raise TypeError(
                    f"Invalid data type: {type(data)}. "
                    f"Expected CalculatedChart, Native, or (datetime, location) tuple"
                )

        # Convert natal data to chart
        natal_chart = to_chart(natal_data)

        # Determine progressed chart
        if progressed_data is not None:
            # Legacy path: use provided chart directly
            progressed_chart = to_chart(
                progressed_data, location_fallback=natal_chart.location
            )
        else:
            # Auto-calculate path
            natal_datetime = natal_chart.datetime.local_datetime

            # Determine target date
            if age is not None:
                # Calculate target date from age
                target = natal_datetime + timedelta(days=age * 365.25)
            elif target_date is not None:
                # Parse target date string if needed
                if isinstance(target_date, str):
                    # Use Native's parsing (handles ISO format, etc.)
                    temp_native = Native(target_date, natal_chart.location)
                    # Native.datetime is ChartDateTime, we need the local datetime
                    target = temp_native.datetime.local_datetime
                else:
                    target = target_date
            else:
                # Default to now (naive datetime to match natal)
                target = datetime.now()

            # Calculate progressed datetime using 1 day = 1 year rule
            progressed_dt = calculate_progressed_datetime(natal_datetime, target)

            # Create progressed chart at natal location
            name = natal_chart.metadata.get("name", "Chart")
            progressed_chart = ChartBuilder.from_details(
                progressed_dt,
                natal_chart.location,
                name=f"{name} - Progressed",
            ).calculate()

            # Apply angle adjustment if not quotidian
            # For solar arc and naibod, angles are natal angles + arc
            # (NOT quotidian progressed angles + arc)
            if angle_method != "quotidian":
                # Get natal and progressed Sun positions
                natal_sun = natal_chart.get_object("Sun")
                progressed_sun = progressed_chart.get_object("Sun")

                if natal_sun and progressed_sun:
                    if angle_method == "solar_arc":
                        arc = calculate_solar_arc(
                            natal_sun.longitude, progressed_sun.longitude
                        )
                    elif angle_method == "naibod":
                        years = calculate_years_elapsed(natal_datetime, target)
                        arc = calculate_naibod_arc(years)
                    else:
                        arc = 0.0  # Shouldn't happen with type hints

                    # For solar arc/naibod, we need to replace the quotidian
                    # progressed angles with natal angles + arc
                    # Build a new positions tuple with adjusted angles
                    adjusted_positions = []
                    for pos in progressed_chart.positions:
                        if pos.object_type == ObjectType.ANGLE:
                            # Find the natal angle position
                            natal_angle = natal_chart.get_object(pos.name)
                            if natal_angle:
                                # Natal angle + arc = progressed angle
                                new_lon = (natal_angle.longitude + arc) % 360
                                adjusted_positions.append(
                                    replace(pos, longitude=new_lon)
                                )
                            else:
                                adjusted_positions.append(pos)
                        else:
                            adjusted_positions.append(pos)

                    # Create new chart with adjusted positions
                    progressed_chart = CalculatedChart(
                        datetime=progressed_chart.datetime,
                        location=progressed_chart.location,
                        positions=tuple(adjusted_positions),
                        house_systems=progressed_chart.house_systems,
                        house_placements=progressed_chart.house_placements,
                        aspects=progressed_chart.aspects,
                        metadata={
                            **progressed_chart.metadata,
                            "angle_method": angle_method,
                            "angle_arc": arc,
                        },
                    )

        # Create builder with both charts configured
        builder = cls(natal_chart, ComparisonType.PROGRESSION, natal_label)
        builder._chart2 = progressed_chart
        builder._chart2_label = progressed_label

        return builder

    @classmethod
    def arc_direction(
        cls,
        natal_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        *,
        target_date: str | datetime | None = None,
        age: float | None = None,
        arc_type: str = "solar_arc",
        rulership_system: Literal["traditional", "modern"] = "traditional",
        natal_label: str = "Natal",
        directed_label: str = "Directed",
    ) -> "ComparisonBuilder":
        """
        Create an arc direction comparison (natal vs directed chart).

        Arc directions move ALL points by the same angular distance, preserving
        natal relationships. This differs from progressions where each planet
        moves at its own rate.

        Arc types supported:
            - "solar_arc": Arc = progressed Sun - natal Sun (~1°/year actual)
            - "naibod": Arc = 0.9856° × years (mean solar motion)
            - "lunar": Arc = progressed Moon - natal Moon (~12-13°/year)
            - "chart_ruler": Arc based on planet ruling the Ascendant sign
            - "sect": Day charts use solar arc, night charts use lunar arc
            - Any planet name (e.g., "Mars", "Venus"): Uses that planet's arc

        Args:
            natal_data: Natal chart data (Native, CalculatedChart, or tuple)
            target_date: Target date for directions (either this or age required)
            age: Age in years (alternative to target_date)
            arc_type: Type of arc to use (see above)
            rulership_system: "traditional" or "modern" (for chart_ruler arc)
            natal_label: Label for natal chart (default: "Natal")
            directed_label: Label for directed chart (default: "Directed")

        Returns:
            ComparisonBuilder instance ready to configure and calculate

        Examples:
            >>> # Solar arc directions at age 30
            >>> directed = ComparisonBuilder.arc_direction(
            ...     natal_chart, age=30, arc_type="solar_arc"
            ... ).calculate()

            >>> # Naibod arc directions to a specific date
            >>> directed = ComparisonBuilder.arc_direction(
            ...     natal_chart, target_date="2025-06-15", arc_type="naibod"
            ... ).calculate()

            >>> # Chart ruler arc (uses planet ruling ASC sign)
            >>> directed = ComparisonBuilder.arc_direction(
            ...     natal_chart, age=30, arc_type="chart_ruler"
            ... ).calculate()

            >>> # Sect-based arc (solar for day charts, lunar for night)
            >>> directed = ComparisonBuilder.arc_direction(
            ...     natal_chart, age=30, arc_type="sect"
            ... ).calculate()

            >>> # Mars arc directions
            >>> directed = ComparisonBuilder.arc_direction(
            ...     natal_chart, age=30, arc_type="Mars"
            ... ).calculate()
        """
        from stellium.utils.progressions import (
            calculate_lunar_arc,
            calculate_naibod_arc,
            calculate_planetary_arc,
            calculate_progressed_datetime,
            calculate_solar_arc,
            calculate_years_elapsed,
        )

        # Helper to convert input to CalculatedChart
        def to_chart(data, location_fallback=None) -> CalculatedChart:
            if isinstance(data, CalculatedChart):
                return data
            elif isinstance(data, Native):
                return ChartBuilder.from_native(data).calculate()
            elif isinstance(data, tuple) and len(data) == 2:
                datetime_input, location_input = data
                if location_input is None:
                    if location_fallback is None:
                        raise ValueError("Location cannot be None")
                    location_input = location_fallback
                native = Native(datetime_input, location_input)
                return ChartBuilder.from_native(native).calculate()
            else:
                raise TypeError(f"Invalid data type: {type(data)}")

        # Convert natal data to chart
        natal_chart = to_chart(natal_data)
        natal_datetime = natal_chart.datetime.local_datetime

        # Determine target date
        if age is not None:
            target = natal_datetime + timedelta(days=age * 365.25)
        elif target_date is not None:
            if isinstance(target_date, str):
                temp_native = Native(target_date, natal_chart.location)
                target = temp_native.datetime.local_datetime
            else:
                target = target_date
        else:
            target = datetime.now()

        years_elapsed = calculate_years_elapsed(natal_datetime, target)

        # Calculate progressed chart for position-based arcs
        progressed_dt = calculate_progressed_datetime(natal_datetime, target)
        progressed_chart = ChartBuilder.from_details(
            progressed_dt, natal_chart.location
        ).calculate()

        # Build position dictionaries for arc calculation
        natal_positions = {pos.name: pos.longitude for pos in natal_chart.positions}
        progressed_positions = {
            pos.name: pos.longitude for pos in progressed_chart.positions
        }

        # Resolve special arc types
        effective_arc_type = arc_type.lower()
        original_arc_type = arc_type

        if effective_arc_type == "chart_ruler":
            # Get the planet ruling the Ascendant sign
            from stellium.utils.chart_ruler import get_chart_ruler

            asc = natal_chart.get_object("ASC")
            if asc:
                ruler_name = get_chart_ruler(asc.sign, rulership_system)
                effective_arc_type = ruler_name.lower()
            else:
                effective_arc_type = "solar_arc"  # Fallback

        elif effective_arc_type == "sect":
            # Determine if day or night chart
            sun = natal_chart.get_object("Sun")
            asc = natal_chart.get_object("ASC")
            if sun and asc:
                # Simple sect check: Sun above horizon = day chart
                # Sun is above horizon if its longitude is between ASC and DSC
                # going through MC (upper hemisphere)
                asc_lon = asc.longitude
                dsc_lon = (asc_lon + 180) % 360
                sun_lon = sun.longitude

                # Check if Sun is in upper hemisphere
                if asc_lon < dsc_lon:
                    is_day = asc_lon <= sun_lon < dsc_lon
                else:
                    is_day = sun_lon >= asc_lon or sun_lon < dsc_lon

                effective_arc_type = "solar_arc" if is_day else "lunar"
            else:
                effective_arc_type = "solar_arc"  # Fallback

        # Calculate the arc
        if effective_arc_type == "naibod":
            arc = calculate_naibod_arc(years_elapsed)
        elif effective_arc_type == "solar_arc":
            arc = calculate_solar_arc(
                natal_positions["Sun"], progressed_positions["Sun"]
            )
        elif effective_arc_type == "lunar":
            arc = calculate_lunar_arc(
                natal_positions["Moon"], progressed_positions["Moon"]
            )
        else:
            # Assume it's a planet name (Mars, Venus, Jupiter, Saturn, Mercury)
            planet = effective_arc_type.title()
            if planet not in natal_positions:
                raise ValueError(
                    f"Unknown arc type or planet not found: '{arc_type}'. "
                    f"Available: solar_arc, naibod, lunar, chart_ruler, sect, "
                    f"or a planet name like 'Mars', 'Venus', etc."
                )
            arc = calculate_planetary_arc(
                natal_positions[planet], progressed_positions[planet]
            )

        # Create directed chart by applying arc to ALL natal positions
        directed_positions = []
        for pos in natal_chart.positions:
            new_longitude = (pos.longitude + arc) % 360
            directed_positions.append(replace(pos, longitude=new_longitude))

        # Create a new CalculatedChart with the directed positions
        name = natal_chart.metadata.get("name", "Chart")
        directed_chart = CalculatedChart(
            datetime=natal_chart.datetime,  # Keep natal datetime for reference
            location=natal_chart.location,
            positions=tuple(directed_positions),
            house_systems=natal_chart.house_systems,
            house_placements=natal_chart.house_placements,
            aspects=(),  # Cross-chart aspects will be calculated
            metadata={
                "arc_type": original_arc_type,
                "effective_arc_type": effective_arc_type,
                "arc_degrees": arc,
                "years_elapsed": years_elapsed,
                "target_date": target.isoformat() if target else None,
                "name": f"{name} - Directed",
            },
        )

        # Create builder
        builder = cls(natal_chart, ComparisonType.ARC_DIRECTION, natal_label)
        builder._chart2 = directed_chart
        builder._chart2_label = directed_label

        return builder

    # ===== Configuration Methods =====
    def with_partner(
        self,
        partner_chart_or_datetime_or_native: CalculatedChart | datetime | Native,
        location: ChartLocation | None = None,
        partner_label: str = "Partner",
    ) -> "ComparisonBuilder":
        """
        Add partner chart for synastry comparison.

        Args:
            partner_chart_or_datetime: Either a CalculatedChart or datetime
            location: Required if providing datetime
            partner_label: Label for the partner chart

        Returns:
            Self for chaining
        """
        self._comparison_type = ComparisonType.SYNASTRY
        self._chart2_label = partner_label

        if isinstance(partner_chart_or_datetime_or_native, CalculatedChart):
            self._chart2 = partner_chart_or_datetime_or_native
        elif isinstance(partner_chart_or_datetime_or_native, Native):
            self._chart2 = ChartBuilder.from_native(
                partner_chart_or_datetime_or_native
            ).calculate()
        else:
            if location is None:
                raise ValueError(
                    "Location required when providing datetime for partner"
                )

            native2 = Native(partner_chart_or_datetime_or_native, location)
            self._chart2 = ChartBuilder.from_native(native2).calculate()

        return self

    def with_other(
        self,
        other_input: CalculatedChart | datetime | Native,
        location: ChartLocation | str | None = None,
        other_label: str = "Other",
        comparison_type: ComparisonType | None = None,
    ) -> "ComparisonBuilder":
        """
        Generic method to add second chart.

        This is a flexible alternative to with_partner() and with_transit().

        Args:
            other_input: Either a CalculatedChart, Native or datetime
            location: Required if providing datetime. ChartLocation or str place name
            other_label: Label for the other chart
            comparison_type: Optional comparison type (default: SYNASTRY)

        Returns:
            Self for chaining
        """
        if comparison_type is not None:
            self._comparison_type = comparison_type

        self._chart2_label = other_label

        if isinstance(other_input, CalculatedChart):
            self._chart2 = other_input
        elif isinstance(other_input, Native):
            self._chart2 = ChartBuilder.from_native(other_input).calculate()
        else:
            if location is None:
                # For transits, use native's location
                location = self._chart1.location

            native2 = Native(other_input, location)
            self._chart2 = ChartBuilder.from_native(native2).calculate()

        return self

    def with_transit(
        self, transit_datetime: datetime, location: ChartLocation | None = None
    ) -> "ComparisonBuilder":
        """
        Add transit chart for transit comparison.

        Convenience method that calls with_other() with appropriate settings.

        Args:
            transit_datetime: Transit datetime
            location: Optional location (defaults to native's location)

        Returns:
            Self for chaining
        """
        return self.with_other(
            transit_datetime,
            location or self._chart1.location,
            other_label="Transit",
            comparison_type=ComparisonType.TRANSIT,
        )

    def with_aspect_engine(self, engine) -> "ComparisonBuilder":
        """
        Set the aspect engine for cross-chart aspects.

        Args:
            engine: AspectEngine instance

        Returns:
            Self for chaining
        """
        self._aspect_engine = engine
        return self

    def with_orb_engine(self, engine) -> "ComparisonBuilder":
        """
        Set the orb calculation engine for dynamic orb calculation.

        OrbEngine will be used to calculate orbs for each planet pair
        dynamically (e.g., wider orbs for Sun/Moon, tighter for fast planets).

        If provided, OrbEngine takes precedence over AspectConfig.orbs.

        Examples:
            from stellium.engines.orbs import SimpleOrbEngine, LuminariesOrbEngine

            # Simple engine with fixed orbs per aspect
            simple = SimpleOrbEngine({'Conjunction': 8.0, 'Trine': 8.0})
            builder.with_orb_engine(simple)

            # Luminaries engine (wider orbs for Sun/Moon)
            lum = LuminariesOrbEngine()
            builder.with_orb_engine(lum)

        Args:
            engine: OrbEngine instance implementing get_orb_allowance()

        Returns:
            Self for chaining
        """
        self._orb_engine = engine
        return self

    def with_aspect_config(self, aspect_config: AspectConfig) -> "ComparisonBuilder":
        """
        Set aspect configuration (orbs, which aspects, etc.).

        Args:
            aspect_config: AspectConfig instance

        Returns:
            Self for chaining
        """
        self._aspect_config = aspect_config
        return self

    def without_house_overlays(self) -> "ComparisonBuilder":
        """
        Disable house overlay calculation.

        Returns:
            Self for chaining
        """
        self._make_house_overlays = False
        return self

    def with_internal_aspect_engine(self, engine) -> "ComparisonBuilder":
        """
        Set aspect engine for calculating internal (natal) aspects.

        This engine will be used to calculate aspects within chart1 and chart2
        if they don't already have aspects calculated. If not set, defaults
        to ModernAspectEngine().

        Args:
            engine: AspectEngine instance for internal aspects

        Returns:
            Self for chaining
        """
        self._internal_aspect_engine = engine
        return self

    def with_internal_orb_engine(self, engine: OrbEngine) -> "ComparisonBuilder":
        """
        Set orb engine for calculating internal (natal) aspects.

        This engine will be used for orb allowances when calculating
        internal aspects in chart1/chart2. If not set, defaults to
        SimpleOrbEngine with registry defaults.

        Args:
            engine: OrbEngine instance for internal aspect orbs

        Returns:
            Self for chaining
        """
        self._internal_orb_engine = engine
        return self

    def calculate(self) -> "Comparison":
        """
        Execute all calculations and return the final Comparison.

        This method ensures that both charts have their internal aspects
        calculated before computing cross-chart aspects. If a chart doesn't
        already have aspects, they will be calculated using the internal
        aspect engine configuration.

        Returns:
            Comparison object with all calculated data
        """
        if self._chart2 is None:
            raise ValueError(
                "Must set chart2 via with_partner(), with_transit(), or with_other()"
            )

        # Ensure chart1 has internal aspects calculated
        if not self._chart1.aspects:
            self._chart1 = self._ensure_internal_aspects(self._chart1)

        # Ensure chart2 has internal aspects calculated
        if not self._chart2.aspects:
            self._chart2 = self._ensure_internal_aspects(self._chart2)

        # Calculate cross-chart aspects
        cross_aspects = self._calculate_cross_aspects()

        # Calculate house overlays (if enabled)
        house_overlays = ()
        if self._make_house_overlays:
            house_overlays = self._calculate_house_overlays()

        return Comparison(
            comparison_type=self._comparison_type,
            chart1=self._chart1,
            chart2=self._chart2,
            cross_aspects=tuple(cross_aspects),
            house_overlays=house_overlays,
            chart1_label=self._chart1_label,
            chart2_label=self._chart2_label,
        )

    # ===== Private Calculation Methods =====

    def _get_default_comparison_orbs(self) -> OrbEngine:
        """
        Get default orb engine for cross-chart aspects.

        Comparison charts typically use different orb allowances than natal charts,
        depending on the type of comparison:

        - **Synastry (6°/4°):** Moderate orbs for finding strong connections
          between two people. We care about meaningful aspects, not just exact ones.

        - **Transits (3°/2°):** Tight orbs for precise timing. When does the
          transit actually perfect? Timing precision matters for prediction.

        - **Progressions (1°):** Very tight orbs for symbolic timing. In
          progressions, 1° of motion = 1 year of life, so precision is crucial.

        Returns:
            OrbEngine configured with appropriate defaults for this comparison type

        Note:
            These are defaults. Users can override with .with_orb_engine()
            for custom orb allowances.
        """
        from stellium.engines.orbs import SimpleOrbEngine

        if self._comparison_type == ComparisonType.SYNASTRY:
            # Synastry: Moderate orbs (connections matter, not super tight)
            orb_map = {
                "Conjunction": 6.0,
                "Sextile": 4.0,
                "Square": 6.0,
                "Trine": 6.0,
                "Opposition": 6.0,
                # Minor aspects
                "Semisextile": 2.0,
                "Semisquare": 2.0,
                "Sesquisquare": 2.0,
                "Quincunx": 3.0,
            }
        elif self._comparison_type == ComparisonType.TRANSIT:
            # Transits: Tight orbs (timing precision matters)
            orb_map = {
                "Conjunction": 3.0,
                "Sextile": 2.0,
                "Square": 3.0,
                "Trine": 3.0,
                "Opposition": 3.0,
                # Minor aspects (rarely used for transits, very tight)
                "Semisextile": 1.0,
                "Semisquare": 1.0,
                "Sesquisquare": 1.0,
                "Quincunx": 1.5,
            }
        elif self._comparison_type == ComparisonType.PROGRESSION:
            # Progressions: Very tight orbs (symbolic timing, 1° = 1 year)
            orb_map = {
                "Conjunction": 1.0,
                "Sextile": 1.0,
                "Square": 1.0,
                "Trine": 1.0,
                "Opposition": 1.0,
                # Minor aspects (rarely used in progressions)
                "Semisextile": 0.5,
                "Semisquare": 0.5,
                "Sesquisquare": 0.5,
                "Quincunx": 0.5,
            }
        elif self._comparison_type == ComparisonType.ARC_DIRECTION:
            # Arc Directions: Same as progressions (symbolic timing, 1° = 1 year)
            orb_map = {
                "Conjunction": 1.0,
                "Sextile": 1.0,
                "Square": 1.0,
                "Trine": 1.0,
                "Opposition": 1.0,
                # Minor aspects
                "Semisextile": 0.5,
                "Semisquare": 0.5,
                "Sesquisquare": 0.5,
                "Quincunx": 0.5,
            }
        else:
            # Fallback: moderate orbs
            orb_map = {
                "Conjunction": 6.0,
                "Sextile": 4.0,
                "Square": 6.0,
                "Trine": 6.0,
                "Opposition": 6.0,
            }

        return SimpleOrbEngine(orb_map=orb_map)

    def _get_orb_for_pair(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str,
    ) -> float:
        """
        Get orb allowance for a specific planet pair and aspect.

        The orb engine is always present (initialized with comparison-type
        specific defaults), so we simply delegate to it.

        Args:
            obj1: First celestial position (from chart1)
            obj2: Second celestial position (from chart2)
            aspect_name: Name of aspect (e.g., "Trine", "Square")

        Returns:
            Orb allowance in degrees
        """
        # OrbEngine is always present (see __init__)
        return self._orb_engine.get_orb_allowance(obj1, obj2, aspect_name)

    def _ensure_internal_aspects(self, chart: CalculatedChart) -> CalculatedChart:
        """
        Ensure a chart has internal aspects calculated.

        If the chart doesn't have aspects, calculates them using the
        internal aspect engine and orb engine configuration.

        Args:
            chart: Chart to ensure has aspects

        Returns:
            Chart with aspects calculated (new instance if aspects were added)
        """
        from stellium.engines.aspects import ModernAspectEngine
        from stellium.engines.orbs import SimpleOrbEngine

        # Determine which engine to use
        aspect_engine = self._internal_aspect_engine or ModernAspectEngine()
        orb_engine = self._internal_orb_engine or SimpleOrbEngine()

        # Calculate aspects
        internal_aspects = aspect_engine.calculate_aspects(
            list(chart.positions), orb_engine
        )

        # Create new chart with aspects
        return CalculatedChart(
            datetime=chart.datetime,
            location=chart.location,
            positions=chart.positions,
            house_systems=chart.house_systems,
            house_placements=chart.house_placements,
            aspects=tuple(internal_aspects),
            metadata=chart.metadata,
        )

    def _calculate_cross_aspects(self) -> list[ComparisonAspect]:
        """
        Calculate aspects between chart1 and chart2.

        Uses CrossChartAspectEngine to find aspects where one object
        is from chart1 and the other is from chart2. Then enhances
        each aspect with house placement information.

        Returns:
            List of ComparisonAspect objects
        """
        from stellium.engines.aspects import CrossChartAspectEngine

        # Use configured engine or create default
        if self._aspect_engine:
            engine = self._aspect_engine
        else:
            # Default cross-chart engine
            engine = CrossChartAspectEngine()

        # Calculate cross-chart aspects
        cross_aspects = engine.calculate_cross_aspects(
            list(self._chart1.positions),
            list(self._chart2.positions),
            self._orb_engine,
        )

        # Enhance Aspect → ComparisonAspect with house metadata
        comparison_aspects = []
        for asp in cross_aspects:
            # Find which house each object falls into
            obj1_house = self._chart1.get_house(asp.object1.name)
            obj2_house = self._chart2.get_house(asp.object2.name)

            comp_asp = ComparisonAspect(
                object1=asp.object1,
                object2=asp.object2,
                aspect_name=asp.aspect_name,
                aspect_degree=asp.aspect_degree,
                orb=asp.orb,
                is_applying=asp.is_applying,
                chart1_to_chart2=True,  # Always chart1→chart2 in our iteration
                in_chart1_house=obj1_house,
                in_chart2_house=obj2_house,
            )
            comparison_aspects.append(comp_asp)

        return comparison_aspects

    def _calculate_house_overlays(self) -> tuple[HouseOverlay, ...]:
        """
        Calculate which houses each chart's planets fall into.

        This calculates house overlays in both directions:
        - Chart1 planets in Chart2 houses
        - Chart2 planets in Chart1 houses

        Returns:
            Tuple of HouseOverlay objects
        """
        from stellium.utils.houses import find_house_for_longitude

        overlays = []

        # Chart1 planets in Chart2 houses
        chart2_cusps = self._chart2.get_houses().cusps
        for pos in self._chart1.positions:
            house_num = find_house_for_longitude(pos.longitude, chart2_cusps)
            overlay = HouseOverlay(
                planet_name=pos.name,
                planet_owner="chart1",
                falls_in_house=house_num,
                house_owner="chart2",
                planet_position=pos,
            )
            overlays.append(overlay)

        # Chart2 planets in Chart1 houses
        chart1_cusps = self._chart1.get_houses().cusps
        for pos in self._chart2.positions:
            house_num = find_house_for_longitude(pos.longitude, chart1_cusps)
            overlay = HouseOverlay(
                planet_name=pos.name,
                planet_owner="chart2",
                falls_in_house=house_num,
                house_owner="chart1",
                planet_position=pos,
            )
            overlays.append(overlay)

        return tuple(overlays)
