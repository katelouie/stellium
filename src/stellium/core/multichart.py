"""
Unified MultiChart implementation for 2-4 chart comparisons.

This module provides a single interface for all multi-chart scenarios:
- Synastry (two natal charts)
- Transits (natal + current sky)
- Progressions (natal + progressed)
- Arc Directions (natal + directed)
- Triwheels (3 charts)
- Quadwheels (4 charts)

The MultiChart class combines the features of the former Comparison and MultiWheel
classes into a unified architecture.

Ring order (center -> out):
- Tiny aspect center
- Chart 1 ring (innermost) - primary/natal chart
- Chart 2 ring
- Chart 3 ring (if present)
- Chart 4 ring (if present)
- Zodiac ring (outermost)
"""

import datetime as dt
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

from stellium.core.builder import ChartBuilder
from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ComparisonType,
    HouseOverlay,
    ObjectType,
)
from stellium.core.native import Native
from stellium.core.protocols import OrbEngine

if TYPE_CHECKING:
    from stellium.visualization.builder import ChartDrawBuilder


@dataclass(frozen=True)
class MultiChart:
    """
    Unified multi-chart container supporting 2-4 charts with analysis and visualization.

    Supports all chart relationship types:
    - Synastry (two natal charts)
    - Transits (natal + transit sky)
    - Progressions (natal + progressed)
    - Arc Directions (natal + directed)
    - Triwheels/Quadwheels (3-4 charts)

    Access charts via:
    - Indexed: mc[0], mc[1], mc.charts[2]
    - Named: mc.chart1, mc.chart2, mc.chart3, mc.chart4
    - Semantic: mc.inner, mc.outer, mc.natal

    Attributes:
        charts: Tuple of 2-4 CalculatedChart objects
        labels: Display labels for each chart
        relationships: Per-pair relationship types {(0,1): ComparisonType.SYNASTRY}
        cross_aspects: Cross-chart aspects indexed by pair {(0,1): (aspects...)}
        house_overlays: House overlays indexed by (planet_chart, house_chart)
        calculation_timestamp: When this MultiChart was created
        metadata: Additional metadata
    """

    # Core data
    charts: tuple[CalculatedChart, ...]
    labels: tuple[str, ...] = ()

    # Per-pair relationship types
    relationships: dict[tuple[int, int], ComparisonType] = field(default_factory=dict)

    # Calculated analysis data
    cross_aspects: dict[tuple[int, int], tuple[Aspect, ...]] = field(
        default_factory=dict
    )
    house_overlays: dict[tuple[int, int], tuple[HouseOverlay, ...]] = field(
        default_factory=dict
    )

    # Metadata
    calculation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(dt.UTC)
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate chart count and auto-generate labels if needed."""
        if len(self.charts) < 2:
            raise ValueError("MultiChart requires at least 2 charts")
        if len(self.charts) > 4:
            raise ValueError("MultiChart supports at most 4 charts")

        # Auto-generate labels if not provided
        if not self.labels:
            default_labels = ("Chart 1", "Chart 2", "Chart 3", "Chart 4")
            object.__setattr__(self, "labels", default_labels[: len(self.charts)])

    # ===== Indexed Access =====

    def __getitem__(self, index: int) -> CalculatedChart:
        """Allow mc[0], mc[1], etc."""
        return self.charts[index]

    def __len__(self) -> int:
        """Number of charts."""
        return len(self.charts)

    # ===== Named Properties =====

    @property
    def chart_count(self) -> int:
        """Number of charts in this MultiChart."""
        return len(self.charts)

    @property
    def chart1(self) -> CalculatedChart:
        """Primary chart (innermost ring)."""
        return self.charts[0]

    @property
    def chart2(self) -> CalculatedChart:
        """Second chart."""
        return self.charts[1]

    @property
    def chart3(self) -> CalculatedChart | None:
        """Third chart (if present)."""
        return self.charts[2] if len(self.charts) > 2 else None

    @property
    def chart4(self) -> CalculatedChart | None:
        """Fourth chart (if present)."""
        return self.charts[3] if len(self.charts) > 3 else None

    # ===== Semantic Aliases =====

    @property
    def inner(self) -> CalculatedChart:
        """Semantic alias for innermost chart (chart1)."""
        return self.charts[0]

    @property
    def outer(self) -> CalculatedChart:
        """Semantic alias for outermost chart."""
        return self.charts[-1]

    @property
    def natal(self) -> CalculatedChart:
        """Semantic alias for the natal/base chart (chart1)."""
        return self.charts[0]

    # ===== Delegate Properties (for visualization compatibility) =====

    @property
    def location(self):
        """Delegate to chart1's location for visualization compatibility."""
        return self.charts[0].location

    @property
    def datetime(self):
        """Delegate to chart1's datetime for visualization compatibility."""
        return self.charts[0].datetime

    # ===== Query Methods =====

    def get_object(self, name: str, chart: int = 0) -> CelestialPosition | None:
        """
        Get a celestial object by name from a specific chart.

        Args:
            name: Object name (e.g., "Sun", "Moon")
            chart: Chart index (0-based) or 1-based if > 0

        Returns:
            CelestialPosition or None
        """
        return self.charts[chart].get_object(name)

    def get_planets(self, chart: int = 0) -> list[CelestialPosition]:
        """Get all planetary objects from specified chart."""
        return self.charts[chart].get_planets()

    def get_angles(self, chart: int = 0) -> list[CelestialPosition]:
        """Get all chart angles from specified chart."""
        return self.charts[chart].get_angles()

    def get_relationship(self, idx1: int, idx2: int) -> ComparisonType | None:
        """
        Get the relationship type between two charts.

        Args:
            idx1: First chart index
            idx2: Second chart index

        Returns:
            ComparisonType or None if not defined
        """
        # Normalize key order (smaller first)
        key = (min(idx1, idx2), max(idx1, idx2))
        return self.relationships.get(key)

    def get_cross_aspects(
        self, chart1_idx: int = 0, chart2_idx: int = 1
    ) -> tuple[Aspect, ...]:
        """
        Get cross-chart aspects between two specific charts.

        Args:
            chart1_idx: First chart index (default: 0)
            chart2_idx: Second chart index (default: 1)

        Returns:
            Tuple of Aspect objects
        """
        # Normalize key order (smaller first)
        key = (min(chart1_idx, chart2_idx), max(chart1_idx, chart2_idx))
        return self.cross_aspects.get(key, ())

    def get_all_cross_aspects(self) -> list[Aspect]:
        """
        Get all cross-chart aspects flattened into a single list.

        Returns:
            List of all Aspect objects from all chart pairs
        """
        all_aspects = []
        for aspects in self.cross_aspects.values():
            all_aspects.extend(aspects)
        return all_aspects

    def get_object_aspects(self, object_name: str, chart: int = 0) -> list[Aspect]:
        """
        Get all cross-chart aspects involving a specific object from a specific chart.

        Args:
            object_name: Name of the celestial object (e.g., "Venus", "Moon")
            chart: Chart index (0 = inner/natal, 1 = outer/transit, etc.)

        Returns:
            List of Aspect objects involving the specified object

        Example:
            >>> venus_aspects = multichart.get_object_aspects("Venus", chart=0)
            >>> for asp in venus_aspects:
            ...     print(f"Venus {asp.aspect_name} {asp.object2.name}")
        """
        all_aspects = self.get_all_cross_aspects()
        result = []
        for asp in all_aspects:
            # Check if object1 matches (from specified chart)
            if asp.object1.name == object_name:
                result.append(asp)
            # Check if object2 matches (swap perspective)
            elif asp.object2.name == object_name:
                result.append(asp)
        return result

    def get_house_overlays(
        self, planet_chart: int, house_chart: int
    ) -> tuple[HouseOverlay, ...]:
        """
        Get house overlays for a specific chart pair.

        Args:
            planet_chart: Index of chart whose planets to check
            house_chart: Index of chart whose houses to use

        Returns:
            Tuple of HouseOverlay objects
        """
        return self.house_overlays.get((planet_chart, house_chart), ())

    def get_all_house_overlays(self) -> list[HouseOverlay]:
        """
        Get all house overlays flattened into a single list.

        Returns:
            List of all HouseOverlay objects
        """
        all_overlays = []
        for overlays in self.house_overlays.values():
            all_overlays.extend(overlays)
        return all_overlays

    # ===== Compatibility Scoring (for synastry) =====

    def calculate_compatibility_score(
        self,
        pair: tuple[int, int] = (0, 1),
        weights: dict[str, float] | None = None,
    ) -> float:
        """
        Calculate a simple compatibility score based on aspects.

        This is a basic implementation - users can implement their own
        weighting schemes.

        Args:
            pair: Which chart pair to score (default: (0, 1))
            weights: Optional custom weights for aspect types

        Returns:
            Compatibility score (0-100)
        """
        if weights is None:
            weights = {
                "Conjunction": 0.5,
                "Sextile": 1.0,
                "Square": -0.5,
                "Trine": 1.0,
                "Opposition": -0.3,
            }

        aspects = self.get_cross_aspects(pair[0], pair[1])

        if not aspects:
            return 50.0

        total_score = 0.0
        for aspect in aspects:
            weight = weights.get(aspect.aspect_name, 0.0)
            orb_strength = 1.0 - (aspect.orb / 10.0)
            orb_strength = max(0.0, min(1.0, orb_strength))
            total_score += weight * orb_strength

        normalized = ((total_score / len(aspects)) + 0.5) / 1.5 * 100
        return max(0.0, min(100.0, normalized))

    # ===== Visualization =====

    def draw(self, filename: str = "multichart.svg") -> "ChartDrawBuilder":
        """
        Start building a multi-chart visualization.

        Args:
            filename: Output filename for the SVG

        Returns:
            ChartDrawBuilder configured for this MultiChart
        """
        from stellium.visualization.builder import ChartDrawBuilder

        return ChartDrawBuilder(self).with_filename(filename)

    # ===== Serialization =====

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        Returns:
            Dictionary with full MultiChart data
        """
        # Serialize relationships
        relationships_dict = {
            f"{k[0]},{k[1]}": v.value for k, v in self.relationships.items()
        }

        # Serialize cross-aspects
        cross_aspects_dict = {}
        for (i, j), aspects in self.cross_aspects.items():
            key = f"{i},{j}"
            cross_aspects_dict[key] = [
                {
                    "object1": asp.object1.name,
                    "object1_chart": i,
                    "object2": asp.object2.name,
                    "object2_chart": j,
                    "aspect": asp.aspect_name,
                    "orb": asp.orb,
                    "is_applying": asp.is_applying,
                }
                for asp in aspects
            ]

        # Serialize house overlays
        house_overlays_dict = {}
        for (planet_chart, house_chart), overlays in self.house_overlays.items():
            key = f"{planet_chart},{house_chart}"
            house_overlays_dict[key] = [
                {
                    "planet": overlay.planet_name,
                    "planet_chart": planet_chart,
                    "house": overlay.falls_in_house,
                    "house_chart": house_chart,
                }
                for overlay in overlays
            ]

        return {
            "chart_count": self.chart_count,
            "labels": list(self.labels),
            "charts": [chart.to_dict() for chart in self.charts],
            "relationships": relationships_dict,
            "cross_aspects": cross_aspects_dict,
            "house_overlays": house_overlays_dict,
            "metadata": self.metadata,
        }


# =============================================================================
# MultiChartBuilder
# =============================================================================


class MultiChartBuilder:
    """
    Fluent builder for creating MultiChart objects.

    Supports all multi-chart scenarios:

    For synastry:
        mc = MultiChartBuilder.synastry(chart1, chart2).calculate()

    For transits:
        mc = MultiChartBuilder.transit(natal, "2025-06-15").calculate()

    For progressions:
        mc = MultiChartBuilder.progression(natal, age=30).calculate()

    For 3-4 chart configurations:
        mc = (MultiChartBuilder.from_chart(natal, "Natal")
            .add_progression(age=30, label="Progressed")
            .add_transit("2025-06-15", label="Transit")
            .calculate())
    """

    def __init__(self, charts: list[CalculatedChart] | None = None) -> None:
        """
        Initialize builder.

        Args:
            charts: Optional initial list of charts
        """
        self._charts: list[CalculatedChart] = charts or []
        self._labels: list[str] = []
        self._relationships: dict[tuple[int, int], ComparisonType] = {}

        # Aspect configuration
        self._cross_aspect_pairs: (
            list[tuple[int, int]] | Literal["all", "to_primary", "adjacent"]
        ) = "to_primary"
        self._aspect_engine = None
        self._orb_engine: OrbEngine | None = None
        self._internal_aspect_engine = None
        self._internal_orb_engine: OrbEngine | None = None

        # House overlay configuration
        self._calculate_house_overlays: bool = True

        # Metadata
        self._metadata: dict[str, Any] = {}

    # ===== Generic Constructors =====

    @classmethod
    def from_charts(
        cls,
        charts: list[CalculatedChart],
        labels: list[str] | None = None,
    ) -> "MultiChartBuilder":
        """
        Create a MultiChartBuilder from a list of calculated charts.

        Args:
            charts: List of 2-4 CalculatedChart objects
            labels: Optional labels for each chart

        Returns:
            MultiChartBuilder ready for configuration
        """
        if len(charts) < 2:
            raise ValueError("MultiChart requires at least 2 charts")
        if len(charts) > 4:
            raise ValueError("MultiChart supports at most 4 charts")

        builder = cls(charts)
        if labels:
            builder._labels = labels
        return builder

    @classmethod
    def from_chart(
        cls, chart: CalculatedChart, label: str = "Chart 1"
    ) -> "MultiChartBuilder":
        """
        Start building from a single chart.

        Use .add_chart(), .add_transit(), etc. to add more charts.

        Args:
            chart: Initial chart
            label: Label for this chart

        Returns:
            MultiChartBuilder ready for adding more charts
        """
        builder = cls([chart])
        builder._labels = [label]
        return builder

    # ===== Convenience Constructors (2-chart) =====

    @classmethod
    def synastry(
        cls,
        data1: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        data2: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        label1: str = "Person 1",
        label2: str = "Person 2",
    ) -> "MultiChartBuilder":
        """
        Create a synastry comparison between two natal charts.

        Args:
            data1: First person's chart data
            data2: Second person's chart data
            label1: Label for first person
            label2: Label for second person

        Returns:
            MultiChartBuilder configured for synastry
        """
        chart1 = cls._to_chart(data1)
        chart2 = cls._to_chart(data2, location_fallback=chart1.location)

        builder = cls([chart1, chart2])
        builder._labels = [label1, label2]
        builder._relationships[(0, 1)] = ComparisonType.SYNASTRY
        return builder

    @classmethod
    def transit(
        cls,
        natal_data: CalculatedChart
        | Native
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict],
        transit_data: CalculatedChart
        | Native
        | dt.datetime
        | str
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict | None],
        natal_label: str = "Natal",
        transit_label: str = "Transit",
    ) -> "MultiChartBuilder":
        """
        Create a transit comparison (natal chart vs current sky).

        Args:
            natal_data: Natal chart data (CalculatedChart, Native, or tuple)
            transit_data: Transit time - can be:
                - CalculatedChart: use as-is
                - Native: build chart from Native
                - datetime or str: use natal chart's location
                - tuple[datetime, location]: build chart from tuple
            natal_label: Label for natal chart
            transit_label: Label for transit chart

        Returns:
            MultiChartBuilder configured for transits

        Example:
            # Using a raw datetime (uses natal location)
            mc = MultiChartBuilder.transit(natal, datetime(2025, 1, 1, 12, 0))

            # Using a tuple with explicit location
            mc = MultiChartBuilder.transit(natal, (datetime(2025, 1, 1), "New York"))
        """
        natal_chart = cls._to_chart(natal_data)
        transit_chart = cls._to_chart(
            transit_data, location_fallback=natal_chart.location
        )

        builder = cls([natal_chart, transit_chart])
        builder._labels = [natal_label, transit_label]
        builder._relationships[(0, 1)] = ComparisonType.TRANSIT
        return builder

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
    ) -> "MultiChartBuilder":
        """
        Create a progression comparison with auto-calculation support.

        Secondary progressions use the symbolic equation "one day = one year."

        Args:
            natal_data: Natal chart data
            progressed_data: Optional pre-calculated progressed chart
            target_date: Target date for progression
            age: Age in years for progression
            angle_method: How to progress angles
            natal_label: Label for natal chart
            progressed_label: Label for progressed chart

        Returns:
            MultiChartBuilder configured for progressions
        """
        from stellium.utils.progressions import (
            calculate_naibod_arc,
            calculate_progressed_datetime,
            calculate_solar_arc,
            calculate_years_elapsed,
        )

        natal_chart = cls._to_chart(natal_data)

        if progressed_data is not None:
            progressed_chart = cls._to_chart(
                progressed_data, location_fallback=natal_chart.location
            )
        else:
            natal_datetime = natal_chart.datetime.local_datetime

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

            progressed_dt = calculate_progressed_datetime(natal_datetime, target)

            name = natal_chart.metadata.get("name", "Chart")
            progressed_chart = ChartBuilder.from_details(
                progressed_dt,
                natal_chart.location,
                name=f"{name} - Progressed",
            ).calculate()

            if angle_method != "quotidian":
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
                        arc = 0.0

                    adjusted_positions = []
                    for pos in progressed_chart.positions:
                        if pos.object_type == ObjectType.ANGLE:
                            natal_angle = natal_chart.get_object(pos.name)
                            if natal_angle:
                                new_lon = (natal_angle.longitude + arc) % 360
                                adjusted_positions.append(
                                    replace(pos, longitude=new_lon)
                                )
                            else:
                                adjusted_positions.append(pos)
                        else:
                            adjusted_positions.append(pos)

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

        builder = cls([natal_chart, progressed_chart])
        builder._labels = [natal_label, progressed_label]
        builder._relationships[(0, 1)] = ComparisonType.PROGRESSION
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
    ) -> "MultiChartBuilder":
        """
        Create an arc direction comparison (natal vs directed chart).

        Arc directions move ALL points by the same angular distance.

        Args:
            natal_data: Natal chart data
            target_date: Target date for directions
            age: Age in years
            arc_type: Type of arc to use
            rulership_system: "traditional" or "modern"
            natal_label: Label for natal chart
            directed_label: Label for directed chart

        Returns:
            MultiChartBuilder configured for arc directions
        """
        from stellium.utils.progressions import (
            calculate_lunar_arc,
            calculate_naibod_arc,
            calculate_planetary_arc,
            calculate_progressed_datetime,
            calculate_solar_arc,
            calculate_years_elapsed,
        )

        natal_chart = cls._to_chart(natal_data)
        natal_datetime = natal_chart.datetime.local_datetime

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

        progressed_dt = calculate_progressed_datetime(natal_datetime, target)
        progressed_chart = ChartBuilder.from_details(
            progressed_dt, natal_chart.location
        ).calculate()

        natal_positions = {pos.name: pos.longitude for pos in natal_chart.positions}
        progressed_positions = {
            pos.name: pos.longitude for pos in progressed_chart.positions
        }

        effective_arc_type = arc_type.lower()
        original_arc_type = arc_type

        if effective_arc_type == "chart_ruler":
            from stellium.utils.chart_ruler import get_chart_ruler

            asc = natal_chart.get_object("ASC")
            if asc:
                ruler_name = get_chart_ruler(asc.sign, rulership_system)
                effective_arc_type = ruler_name.lower()
            else:
                effective_arc_type = "solar_arc"

        elif effective_arc_type == "sect":
            sun = natal_chart.get_object("Sun")
            asc = natal_chart.get_object("ASC")
            if sun and asc:
                asc_lon = asc.longitude
                dsc_lon = (asc_lon + 180) % 360
                sun_lon = sun.longitude

                if asc_lon < dsc_lon:
                    is_day = asc_lon <= sun_lon < dsc_lon
                else:
                    is_day = sun_lon >= asc_lon or sun_lon < dsc_lon

                effective_arc_type = "solar_arc" if is_day else "lunar"
            else:
                effective_arc_type = "solar_arc"

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
            planet = effective_arc_type.title()
            if planet not in natal_positions:
                raise ValueError(
                    f"Unknown arc type or planet not found: '{arc_type}'. "
                    f"Available: solar_arc, naibod, lunar, chart_ruler, sect, "
                    f"or a planet name."
                )
            arc = calculate_planetary_arc(
                natal_positions[planet], progressed_positions[planet]
            )

        directed_positions = []
        for pos in natal_chart.positions:
            new_longitude = (pos.longitude + arc) % 360
            directed_positions.append(replace(pos, longitude=new_longitude))

        name = natal_chart.metadata.get("name", "Chart")
        directed_chart = CalculatedChart(
            datetime=natal_chart.datetime,
            location=natal_chart.location,
            positions=tuple(directed_positions),
            house_systems=natal_chart.house_systems,
            house_placements=natal_chart.house_placements,
            aspects=(),
            metadata={
                "arc_type": original_arc_type,
                "effective_arc_type": effective_arc_type,
                "arc_degrees": arc,
                "years_elapsed": years_elapsed,
                "target_date": target.isoformat() if target else None,
                "name": f"{name} - Directed",
            },
        )

        builder = cls([natal_chart, directed_chart])
        builder._labels = [natal_label, directed_label]
        builder._relationships[(0, 1)] = ComparisonType.ARC_DIRECTION
        return builder

    # ===== Adding Charts (for 3-4 chart configs) =====

    def add_chart(
        self,
        chart: CalculatedChart,
        label: str,
        relationship_to: int = 0,
        relationship_type: ComparisonType | None = None,
    ) -> "MultiChartBuilder":
        """
        Add a chart to the builder.

        Args:
            chart: Chart to add
            label: Label for this chart
            relationship_to: Which existing chart this relates to (default: 0)
            relationship_type: Type of relationship (optional)

        Returns:
            Self for chaining
        """
        if len(self._charts) >= 4:
            raise ValueError("MultiChart supports at most 4 charts")

        new_idx = len(self._charts)
        self._charts.append(chart)
        self._labels.append(label)

        if relationship_type is not None:
            key = (min(relationship_to, new_idx), max(relationship_to, new_idx))
            self._relationships[key] = relationship_type

        return self

    def add_transit(
        self,
        transit_data: str | datetime | CalculatedChart,
        location: Any = None,
        label: str = "Transit",
    ) -> "MultiChartBuilder":
        """
        Add a transit chart.

        Args:
            transit_data: Transit datetime or chart
            location: Location (uses chart[0] location if None)
            label: Label for transit chart

        Returns:
            Self for chaining
        """
        if not self._charts:
            raise ValueError("Must have at least one chart before adding transit")

        if isinstance(transit_data, CalculatedChart):
            transit_chart = transit_data
        else:
            loc = location or self._charts[0].location
            transit_chart = self._to_chart((transit_data, loc))

        return self.add_chart(
            transit_chart,
            label,
            relationship_to=0,
            relationship_type=ComparisonType.TRANSIT,
        )

    def add_progression(
        self,
        *,
        target_date: str | datetime | None = None,
        age: float | None = None,
        angle_method: Literal["quotidian", "solar_arc", "naibod"] = "quotidian",
        label: str = "Progressed",
    ) -> "MultiChartBuilder":
        """
        Add a progressed chart.

        Args:
            target_date: Target date for progression
            age: Age in years
            angle_method: How to progress angles
            label: Label for progressed chart

        Returns:
            Self for chaining
        """
        if not self._charts:
            raise ValueError("Must have at least one chart before adding progression")

        # Build temporary progression to get the chart
        temp_builder = MultiChartBuilder.progression(
            self._charts[0],
            target_date=target_date,
            age=age,
            angle_method=angle_method,
        )
        progressed_chart = temp_builder._charts[1]

        return self.add_chart(
            progressed_chart,
            label,
            relationship_to=0,
            relationship_type=ComparisonType.PROGRESSION,
        )

    def add_arc_direction(
        self,
        *,
        target_date: str | datetime | None = None,
        age: float | None = None,
        arc_type: str = "solar_arc",
        rulership_system: Literal["traditional", "modern"] = "traditional",
        label: str = "Directed",
    ) -> "MultiChartBuilder":
        """
        Add a directed chart.

        Args:
            target_date: Target date for directions
            age: Age in years
            arc_type: Type of arc to use
            rulership_system: Rulership system
            label: Label for directed chart

        Returns:
            Self for chaining
        """
        if not self._charts:
            raise ValueError("Must have at least one chart before adding direction")

        temp_builder = MultiChartBuilder.arc_direction(
            self._charts[0],
            target_date=target_date,
            age=age,
            arc_type=arc_type,
            rulership_system=rulership_system,
        )
        directed_chart = temp_builder._charts[1]

        return self.add_chart(
            directed_chart,
            label,
            relationship_to=0,
            relationship_type=ComparisonType.ARC_DIRECTION,
        )

    # ===== Configuration Methods =====

    def with_labels(self, labels: list[str]) -> "MultiChartBuilder":
        """
        Set labels for each chart.

        Args:
            labels: List of labels

        Returns:
            Self for chaining
        """
        self._labels = labels
        return self

    def with_cross_aspects(
        self,
        pairs: list[tuple[int, int]]
        | Literal["all", "to_primary", "adjacent"] = "to_primary",
    ) -> "MultiChartBuilder":
        """
        Configure which chart pairs to calculate cross-aspects for.

        Args:
            pairs: Either:
                - "to_primary": Only aspects to chart[0] (default)
                - "adjacent": Adjacent pairs (0-1, 1-2, 2-3)
                - "all": All possible pairs
                - List of (i, j) tuples for explicit pairs

        Returns:
            Self for chaining
        """
        self._cross_aspect_pairs = pairs
        return self

    def without_cross_aspects(self) -> "MultiChartBuilder":
        """
        Disable cross-aspect calculation.

        Returns:
            Self for chaining
        """
        self._cross_aspect_pairs = []
        return self

    def with_house_overlays(self, enabled: bool = True) -> "MultiChartBuilder":
        """
        Enable or disable house overlay calculation.

        Args:
            enabled: Whether to calculate house overlays

        Returns:
            Self for chaining
        """
        self._calculate_house_overlays = enabled
        return self

    def without_house_overlays(self) -> "MultiChartBuilder":
        """
        Disable house overlay calculation.

        Returns:
            Self for chaining
        """
        self._calculate_house_overlays = False
        return self

    def with_aspect_engine(self, engine) -> "MultiChartBuilder":
        """
        Set the aspect engine for cross-chart aspects.

        Args:
            engine: AspectEngine instance

        Returns:
            Self for chaining
        """
        self._aspect_engine = engine
        return self

    def with_orb_engine(self, engine: OrbEngine) -> "MultiChartBuilder":
        """
        Set the orb engine for cross-chart aspects.

        Args:
            engine: OrbEngine instance

        Returns:
            Self for chaining
        """
        self._orb_engine = engine
        return self

    def with_internal_aspect_engine(self, engine) -> "MultiChartBuilder":
        """
        Set aspect engine for calculating internal (natal) aspects.

        Args:
            engine: AspectEngine instance

        Returns:
            Self for chaining
        """
        self._internal_aspect_engine = engine
        return self

    def with_internal_orb_engine(self, engine: OrbEngine) -> "MultiChartBuilder":
        """
        Set orb engine for calculating internal (natal) aspects.

        Args:
            engine: OrbEngine instance

        Returns:
            Self for chaining
        """
        self._internal_orb_engine = engine
        return self

    # ===== Build =====

    def calculate(self) -> MultiChart:
        """
        Execute all calculations and return the MultiChart.

        Returns:
            MultiChart object with all calculated data
        """
        if len(self._charts) < 2:
            raise ValueError("Must have at least 2 charts to create MultiChart")

        # Ensure all charts have internal aspects
        charts_with_aspects = []
        for chart in self._charts:
            if not chart.aspects:
                chart = self._ensure_internal_aspects(chart)
            charts_with_aspects.append(chart)

        # Determine which pairs to calculate aspects for
        pairs = self._resolve_aspect_pairs()

        # Calculate cross-aspects
        cross_aspects: dict[tuple[int, int], tuple[Aspect, ...]] = {}
        if pairs:
            for i, j in pairs:
                aspects = self._calculate_cross_aspects(
                    charts_with_aspects[i], charts_with_aspects[j], i, j
                )
                if aspects:
                    cross_aspects[(i, j)] = tuple(aspects)

        # Calculate house overlays
        house_overlays: dict[tuple[int, int], tuple[HouseOverlay, ...]] = {}
        if self._calculate_house_overlays:
            # Calculate overlays to primary only (same default as aspects)
            for i in range(1, len(charts_with_aspects)):
                # Chart[i] planets in chart[0] houses
                overlays_i_in_0 = self._calculate_house_overlays_for_pair(
                    charts_with_aspects[i], charts_with_aspects[0], i, 0
                )
                if overlays_i_in_0:
                    house_overlays[(i, 0)] = tuple(overlays_i_in_0)

                # Chart[0] planets in chart[i] houses
                overlays_0_in_i = self._calculate_house_overlays_for_pair(
                    charts_with_aspects[0], charts_with_aspects[i], 0, i
                )
                if overlays_0_in_i:
                    house_overlays[(0, i)] = tuple(overlays_0_in_i)

        return MultiChart(
            charts=tuple(charts_with_aspects),
            labels=tuple(self._labels) if self._labels else (),
            relationships=self._relationships,
            cross_aspects=cross_aspects,
            house_overlays=house_overlays,
            metadata=self._metadata,
        )

    # ===== Private Helper Methods =====

    @staticmethod
    def _to_chart(
        data: CalculatedChart
        | Native
        | dt.datetime
        | str
        | tuple[str | dt.datetime | dict, str | tuple[float, float] | dict | None],
        location_fallback: Any = None,
    ) -> CalculatedChart:
        """Convert various input types to CalculatedChart.

        Args:
            data: Input data - can be:
                - CalculatedChart: returned as-is
                - Native: builds chart from Native
                - datetime or str: builds chart using location_fallback
                - tuple[datetime, location]: builds chart from tuple
            location_fallback: Location to use when only datetime is provided

        Returns:
            CalculatedChart instance
        """
        if isinstance(data, CalculatedChart):
            return data
        elif isinstance(data, Native):
            return ChartBuilder.from_native(data).calculate()
        elif isinstance(data, dt.datetime | str) and not isinstance(data, tuple):
            # Handle raw datetime or date string - use location fallback
            if location_fallback is None:
                raise ValueError(
                    "Location fallback required when passing datetime without location. "
                    "Either pass a tuple (datetime, location) or ensure a fallback is available."
                )
            native = Native(data, location_fallback)
            return ChartBuilder.from_native(native).calculate()
        elif isinstance(data, tuple) and len(data) == 2:
            datetime_input, location_input = data
            if location_input is None:
                if location_fallback is None:
                    raise ValueError("Location cannot be None without fallback")
                location_input = location_fallback
            native = Native(datetime_input, location_input)
            return ChartBuilder.from_native(native).calculate()
        else:
            raise TypeError(f"Invalid data type: {type(data)}")

    def _resolve_aspect_pairs(self) -> list[tuple[int, int]]:
        """Resolve which chart pairs to calculate aspects for."""
        n = len(self._charts)

        if isinstance(self._cross_aspect_pairs, list):
            return self._cross_aspect_pairs
        elif self._cross_aspect_pairs == "to_primary":
            return [(0, i) for i in range(1, n)]
        elif self._cross_aspect_pairs == "adjacent":
            return [(i, i + 1) for i in range(n - 1)]
        elif self._cross_aspect_pairs == "all":
            pairs = []
            for i in range(n):
                for j in range(i + 1, n):
                    pairs.append((i, j))
            return pairs
        else:
            return []

    def _get_orb_engine_for_pair(self, i: int, j: int) -> OrbEngine:
        """Get orb engine for a specific chart pair."""
        from stellium.engines.orbs import SimpleOrbEngine

        if self._orb_engine:
            return self._orb_engine

        # Determine default orbs based on relationship type
        key = (min(i, j), max(i, j))
        relationship = self._relationships.get(key)

        if relationship == ComparisonType.SYNASTRY:
            orb_map = {
                "Conjunction": 6.0,
                "Sextile": 4.0,
                "Square": 6.0,
                "Trine": 6.0,
                "Opposition": 6.0,
            }
        elif relationship == ComparisonType.TRANSIT:
            orb_map = {
                "Conjunction": 3.0,
                "Sextile": 2.0,
                "Square": 3.0,
                "Trine": 3.0,
                "Opposition": 3.0,
            }
        elif relationship in (ComparisonType.PROGRESSION, ComparisonType.ARC_DIRECTION):
            orb_map = {
                "Conjunction": 1.0,
                "Sextile": 1.0,
                "Square": 1.0,
                "Trine": 1.0,
                "Opposition": 1.0,
            }
        else:
            orb_map = {
                "Conjunction": 6.0,
                "Sextile": 4.0,
                "Square": 6.0,
                "Trine": 6.0,
                "Opposition": 6.0,
            }

        return SimpleOrbEngine(orb_map=orb_map)

    def _ensure_internal_aspects(self, chart: CalculatedChart) -> CalculatedChart:
        """Ensure a chart has internal aspects calculated."""
        from stellium.engines.aspects import ModernAspectEngine
        from stellium.engines.orbs import SimpleOrbEngine

        aspect_engine = self._internal_aspect_engine or ModernAspectEngine()
        orb_engine = self._internal_orb_engine or SimpleOrbEngine()

        internal_aspects = aspect_engine.calculate_aspects(
            list(chart.positions), orb_engine
        )

        return CalculatedChart(
            datetime=chart.datetime,
            location=chart.location,
            positions=chart.positions,
            house_systems=chart.house_systems,
            house_placements=chart.house_placements,
            aspects=tuple(internal_aspects),
            metadata=chart.metadata,
        )

    def _calculate_cross_aspects(
        self,
        chart1: CalculatedChart,
        chart2: CalculatedChart,
        idx1: int,
        idx2: int,
    ) -> list[Aspect]:
        """Calculate cross-chart aspects between two charts."""
        from stellium.engines.aspects import CrossChartAspectEngine

        engine = self._aspect_engine or CrossChartAspectEngine()
        orb_engine = self._get_orb_engine_for_pair(idx1, idx2)

        return engine.calculate_cross_aspects(
            list(chart1.positions),
            list(chart2.positions),
            orb_engine,
        )

    def _calculate_house_overlays_for_pair(
        self,
        planet_chart: CalculatedChart,
        house_chart: CalculatedChart,
        planet_idx: int,
        house_idx: int,
    ) -> list[HouseOverlay]:
        """Calculate house overlays for one chart's planets in another's houses."""
        from stellium.utils.houses import find_house_for_longitude

        overlays = []

        try:
            house_cusps = house_chart.get_houses().cusps
        except (ValueError, KeyError):
            return overlays

        for pos in planet_chart.positions:
            house_num = find_house_for_longitude(pos.longitude, house_cusps)
            overlay = HouseOverlay(
                planet_name=pos.name,
                planet_owner=f"chart{planet_idx + 1}",
                falls_in_house=house_num,
                house_owner=f"chart{house_idx + 1}",
                planet_position=pos,
            )
            overlays.append(overlay)

        return overlays
