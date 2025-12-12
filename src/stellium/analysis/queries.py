"""
Research query interface for filtering chart collections.

ChartQuery provides a fluent API for filtering charts by astrological criteria
like sun sign, moon phase, aspects, patterns, and more.
"""

from collections.abc import Callable, Sequence
from typing import Any

from stellium.analysis.frames import (
    _count_elements,
    _count_modalities,
    _has_pattern,
    _require_pandas,
    charts_to_dataframe,
)
from stellium.core.models import CalculatedChart


class ChartQuery:
    """
    Fluent query interface for filtering chart collections.

    Supports chained method calls to build complex filters. Filters are
    lazily evaluated when results() or count() is called.

    Example::

        from stellium.analysis import ChartQuery

        # Find charts with Sun in Aries and Moon in Cancer
        matches = (ChartQuery(charts)
            .where_sun(sign="Aries")
            .where_moon(sign=["Cancer", "Scorpio"])
            .where_planet("Mars", house=10)
            .results())

        # Get as DataFrame
        df = ChartQuery(charts).where_sun(sign="Aries").to_dataframe()

        # Count results
        count = ChartQuery(charts).where_moon(sign="Leo").count()
    """

    def __init__(self, charts: Sequence[CalculatedChart]) -> None:
        """
        Initialize query with a collection of charts.

        Args:
            charts: Sequence of CalculatedChart objects to query
        """
        self._charts = list(charts)
        self._filters: list[Callable[[CalculatedChart], bool]] = []

    def _add_filter(self, predicate: Callable[[CalculatedChart], bool]) -> "ChartQuery":
        """Add a filter predicate and return self for chaining."""
        self._filters.append(predicate)
        return self

    # ---- Position Filters ----

    def where_sun(
        self,
        sign: str | Sequence[str] | None = None,
        house: int | Sequence[int] | None = None,
        degree_min: float | None = None,
        degree_max: float | None = None,
    ) -> "ChartQuery":
        """
        Filter charts by Sun position.

        Args:
            sign: Zodiac sign(s) (e.g., "Aries" or ["Aries", "Leo"])
            house: House number(s) (e.g., 10 or [1, 10])
            degree_min: Minimum sign degree (0-30)
            degree_max: Maximum sign degree (0-30)

        Example::

            query.where_sun(sign="Aries")
            query.where_sun(sign=["Aries", "Leo", "Sagittarius"])  # Fire signs
            query.where_sun(house=10)
            query.where_sun(degree_min=0, degree_max=5)  # Early degrees
        """
        return self._where_object("Sun", sign, house, degree_min, degree_max)

    def where_moon(
        self,
        sign: str | Sequence[str] | None = None,
        house: int | Sequence[int] | None = None,
        degree_min: float | None = None,
        degree_max: float | None = None,
        phase: str | Sequence[str] | None = None,
    ) -> "ChartQuery":
        """
        Filter charts by Moon position or phase.

        Args:
            sign: Zodiac sign(s)
            house: House number(s)
            degree_min: Minimum sign degree
            degree_max: Maximum sign degree
            phase: Moon phase(s) (e.g., "New Moon", "Full Moon")

        Example::

            query.where_moon(sign="Cancer")
            query.where_moon(phase="Full Moon")
            query.where_moon(phase=["New Moon", "Full Moon"])
        """
        # First apply standard position filter
        query = self._where_object("Moon", sign, house, degree_min, degree_max)

        # Then apply phase filter if specified
        if phase is not None:
            phases = [phase] if isinstance(phase, str) else list(phase)
            phases_lower = [p.lower() for p in phases]

            def phase_filter(chart: CalculatedChart) -> bool:
                moon = chart.get_object("Moon")
                if moon is None or moon.phase is None:
                    return False
                return moon.phase.phase_name.lower() in phases_lower

            query._add_filter(phase_filter)

        return query

    def where_planet(
        self,
        name: str,
        sign: str | Sequence[str] | None = None,
        house: int | Sequence[int] | None = None,
        degree_min: float | None = None,
        degree_max: float | None = None,
        retrograde: bool | None = None,
        out_of_bounds: bool | None = None,
    ) -> "ChartQuery":
        """
        Filter charts by any planet's position.

        Args:
            name: Planet name (e.g., "Mars", "Venus")
            sign: Zodiac sign(s)
            house: House number(s)
            degree_min: Minimum sign degree
            degree_max: Maximum sign degree
            retrograde: Filter by retrograde status
            out_of_bounds: Filter by out-of-bounds status

        Example::

            query.where_planet("Mars", sign="Aries", retrograde=True)
            query.where_planet("Venus", house=[5, 7])
            query.where_planet("Mercury", out_of_bounds=True)
        """
        query = self._where_object(name, sign, house, degree_min, degree_max)

        # Retrograde filter
        if retrograde is not None:

            def retro_filter(chart: CalculatedChart) -> bool:
                obj = chart.get_object(name)
                if obj is None:
                    return False
                return obj.is_retrograde == retrograde

            query._add_filter(retro_filter)

        # Out of bounds filter
        if out_of_bounds is not None:

            def oob_filter(chart: CalculatedChart) -> bool:
                obj = chart.get_object(name)
                if obj is None:
                    return False
                return obj.is_out_of_bounds == out_of_bounds

            query._add_filter(oob_filter)

        return query

    def where_angle(
        self,
        name: str,
        sign: str | Sequence[str] | None = None,
        degree_min: float | None = None,
        degree_max: float | None = None,
    ) -> "ChartQuery":
        """
        Filter charts by angle position (ASC, MC, DSC, IC).

        Args:
            name: Angle name ("ASC", "MC", "DSC", "IC")
            sign: Zodiac sign(s)
            degree_min: Minimum sign degree
            degree_max: Maximum sign degree

        Example::

            query.where_angle("ASC", sign="Leo")
            query.where_angle("MC", sign=["Aries", "Capricorn"])
        """
        return self._where_object(name, sign, None, degree_min, degree_max)

    def _where_object(
        self,
        name: str,
        sign: str | Sequence[str] | None,
        house: int | Sequence[int] | None,
        degree_min: float | None,
        degree_max: float | None,
    ) -> "ChartQuery":
        """Internal helper for position filters."""
        # Sign filter
        if sign is not None:
            signs = [sign] if isinstance(sign, str) else list(sign)

            def sign_filter(chart: CalculatedChart) -> bool:
                obj = chart.get_object(name)
                if obj is None:
                    return False
                return obj.sign in signs

            self._add_filter(sign_filter)

        # House filter
        if house is not None:
            houses = [house] if isinstance(house, int) else list(house)

            def house_filter(chart: CalculatedChart) -> bool:
                obj_house = chart.get_house(name)
                if obj_house is None:
                    return False
                return obj_house in houses

            self._add_filter(house_filter)

        # Degree range filter
        if degree_min is not None or degree_max is not None:
            min_deg = degree_min if degree_min is not None else 0.0
            max_deg = degree_max if degree_max is not None else 30.0

            def degree_filter(chart: CalculatedChart) -> bool:
                obj = chart.get_object(name)
                if obj is None:
                    return False
                return min_deg <= obj.sign_degree <= max_deg

            self._add_filter(degree_filter)

        return self

    # ---- Aspect Filters ----

    def where_aspect(
        self,
        object1: str,
        object2: str,
        aspect: str | Sequence[str] | None = None,
        orb_max: float | None = None,
        applying: bool | None = None,
    ) -> "ChartQuery":
        """
        Filter charts by presence of specific aspects.

        Args:
            object1: First object name
            object2: Second object name
            aspect: Aspect type(s) (e.g., "Conjunction", ["Square", "Opposition"])
            orb_max: Maximum orb in degrees
            applying: Filter to applying (True) or separating (False) aspects

        Example::

            query.where_aspect("Sun", "Moon", aspect="conjunction")
            query.where_aspect("Venus", "Mars", orb_max=3.0)
            query.where_aspect("Saturn", "Sun", applying=True)
        """
        aspects_list = None
        if aspect is not None:
            aspects_list = (
                [aspect.lower()]
                if isinstance(aspect, str)
                else [a.lower() for a in aspect]
            )

        def aspect_filter(chart: CalculatedChart) -> bool:
            for asp in chart.aspects:
                # Check if objects match (in either order)
                names = {asp.object1.name, asp.object2.name}
                if object1 not in names or object2 not in names:
                    continue

                # Check aspect type
                if aspects_list is not None:
                    if asp.aspect_name.lower() not in aspects_list:
                        continue

                # Check orb
                if orb_max is not None:
                    if asp.orb > orb_max:
                        continue

                # Check applying
                if applying is not None:
                    if asp.is_applying != applying:
                        continue

                return True
            return False

        return self._add_filter(aspect_filter)

    # ---- Pattern Filters ----

    def where_pattern(self, pattern_name: str) -> "ChartQuery":
        """
        Filter charts by presence of aspect patterns.

        Args:
            pattern_name: Pattern name (e.g., "Grand Trine", "T-Square", "Yod")

        Example::

            query.where_pattern("Grand Trine")
            query.where_pattern("T-Square")
        """

        def pattern_filter(chart: CalculatedChart) -> bool:
            return _has_pattern(chart, pattern_name)

        return self._add_filter(pattern_filter)

    # ---- Element/Modality Filters ----

    def where_element_dominant(
        self,
        element: str,
        min_count: int = 4,
    ) -> "ChartQuery":
        """
        Filter charts where an element is dominant.

        Args:
            element: Element name ("fire", "earth", "air", "water")
            min_count: Minimum planet count to consider dominant (default 4)

        Example::

            query.where_element_dominant("fire")
            query.where_element_dominant("water", min_count=5)
        """
        element_lower = element.lower()

        def element_filter(chart: CalculatedChart) -> bool:
            counts = _count_elements(chart)
            return counts.get(element_lower, 0) >= min_count

        return self._add_filter(element_filter)

    def where_modality_dominant(
        self,
        modality: str,
        min_count: int = 4,
    ) -> "ChartQuery":
        """
        Filter charts where a modality is dominant.

        Args:
            modality: Modality name ("cardinal", "fixed", "mutable")
            min_count: Minimum planet count to consider dominant (default 4)

        Example::

            query.where_modality_dominant("cardinal")
            query.where_modality_dominant("fixed", min_count=5)
        """
        modality_lower = modality.lower()

        def modality_filter(chart: CalculatedChart) -> bool:
            counts = _count_modalities(chart)
            return counts.get(modality_lower, 0) >= min_count

        return self._add_filter(modality_filter)

    # ---- Sect Filter ----

    def where_sect(self, sect: str) -> "ChartQuery":
        """
        Filter charts by sect (day or night).

        Args:
            sect: "day" or "night"

        Example::

            query.where_sect("day")  # Day charts only
        """
        sect_lower = sect.lower()

        def sect_filter(chart: CalculatedChart) -> bool:
            chart_sect = chart.sect()
            return chart_sect is not None and chart_sect.lower() == sect_lower

        return self._add_filter(sect_filter)

    # ---- Custom Filter ----

    def where_custom(
        self, predicate: Callable[[CalculatedChart], bool]
    ) -> "ChartQuery":
        """
        Filter charts with a custom predicate function.

        Args:
            predicate: Function that takes a CalculatedChart and returns bool

        Example::

            # Charts with more than 3 retrograde planets
            query.where_custom(
                lambda chart: sum(1 for p in chart.get_planets() if p.is_retrograde) > 3
            )
        """
        return self._add_filter(predicate)

    # ---- Result Methods ----

    def results(self) -> list[CalculatedChart]:
        """
        Execute the query and return matching charts.

        Returns:
            List of CalculatedChart objects matching all filters
        """
        result = self._charts
        for filter_fn in self._filters:
            result = [chart for chart in result if filter_fn(chart)]
        return result

    def count(self) -> int:
        """
        Execute the query and return count of matching charts.

        Returns:
            Number of charts matching all filters
        """
        return len(self.results())

    def first(self) -> CalculatedChart | None:
        """
        Return the first matching chart, or None if no matches.

        Returns:
            First CalculatedChart matching all filters, or None
        """
        results = self.results()
        return results[0] if results else None

    def to_dataframe(self, include_patterns: bool = True) -> Any:
        """
        Execute the query and return results as a DataFrame.

        Requires pandas: pip install stellium[analysis]

        Args:
            include_patterns: Include pattern detection columns

        Returns:
            pandas DataFrame of matching charts
        """
        _require_pandas()
        return charts_to_dataframe(self.results(), include_patterns=include_patterns)

    def __len__(self) -> int:
        """Return count of matching charts."""
        return self.count()

    def __iter__(self):
        """Iterate over matching charts."""
        return iter(self.results())

    def __repr__(self) -> str:
        return f"<ChartQuery: {len(self._charts)} charts, {len(self._filters)} filters>"
