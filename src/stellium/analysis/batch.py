"""
Batch chart calculation for large-scale analysis.

BatchCalculator provides efficient calculation of many charts at once,
with support for progress tracking, filtering, and generator-based processing.
"""

from collections.abc import Callable, Generator, Iterable
from typing import Any

from stellium.core.builder import ChartBuilder
from stellium.core.models import CalculatedChart
from stellium.core.native import Native
from stellium.core.protocols import (
    AspectEngine,
    ChartAnalyzer,
    HouseSystemEngine,
    OrbEngine,
)
from stellium.data import get_notable_registry
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.houses import PlacidusHouses
from stellium.engines.orbs import SimpleOrbEngine


class BatchCalculator:
    """
    Efficient batch calculation of multiple charts.

    Supports calculation from:
    - NotableRegistry (with optional filters)
    - List of Native objects
    - Any iterable of chart data

    Example::

        # From NotableRegistry
        charts = (BatchCalculator
            .from_registry(category="scientist", verified=True)
            .with_aspects()
            .calculate_all())

        # From list of Natives
        charts = BatchCalculator.from_natives(natives).calculate_all()

        # Generator for memory efficiency
        for chart in BatchCalculator.from_registry().calculate():
            process(chart)
    """

    def __init__(self, sources: Iterable[Native]) -> None:
        """
        Initialize with an iterable of Native objects.

        Use factory methods like `from_registry()` or `from_natives()` instead.
        """
        self._sources = sources

        # Default engines (same as ChartBuilder)
        self._house_engines: list[HouseSystemEngine] = [PlacidusHouses()]
        self._aspect_engine: AspectEngine | None = None
        self._orb_engine: OrbEngine = SimpleOrbEngine()
        self._analyzers: list[ChartAnalyzer] = []

        # Progress callback
        self._progress_callback: Callable[[int, int, str], None] | None = None

        # Count for progress (if known)
        self._total_count: int | None = None

    # ---- Factory Methods ----

    @classmethod
    def from_registry(
        cls,
        *,
        category: str | None = None,
        event_type: str | None = None,
        verified: bool | None = None,
        data_quality: str | None = None,
        **filters: Any,
    ) -> "BatchCalculator":
        """
        Create BatchCalculator from NotableRegistry with optional filters.

        Args:
            category: Filter by category (e.g., "scientist", "artist")
            event_type: Filter by event type ("birth" or "event")
            verified: Filter by verified status
            data_quality: Filter by data quality ("AA", "A", "B", "C")
            **filters: Additional filters passed to registry.search()

        Returns:
            BatchCalculator ready to configure and run

        Example::

            # All verified scientists
            batch = BatchCalculator.from_registry(
                category="scientist",
                verified=True
            )

            # High-quality birth data only
            batch = BatchCalculator.from_registry(
                event_type="birth",
                data_quality="AA"
            )
        """
        registry = get_notable_registry()

        # Build filter dict
        filter_dict: dict[str, Any] = {}
        if category is not None:
            filter_dict["category"] = category
        if event_type is not None:
            filter_dict["event_type"] = event_type
        if verified is not None:
            filter_dict["verified"] = verified
        if data_quality is not None:
            filter_dict["data_quality"] = data_quality
        filter_dict.update(filters)

        # Get filtered notables
        if filter_dict:
            notables = registry.search(**filter_dict)
        else:
            notables = registry.get_all()

        batch = cls(notables)
        batch._total_count = len(notables)
        return batch

    @classmethod
    def from_natives(cls, natives: list[Native]) -> "BatchCalculator":
        """
        Create BatchCalculator from a list of Native objects.

        Args:
            natives: List of Native objects to calculate charts for

        Returns:
            BatchCalculator ready to configure and run

        Example::

            natives = [
                Native("2000-01-01 12:00", "New York, NY", name="Person 1"),
                Native("1990-06-15 08:30", "Los Angeles, CA", name="Person 2"),
            ]
            batch = BatchCalculator.from_natives(natives)
        """
        batch = cls(natives)
        batch._total_count = len(natives)
        return batch

    @classmethod
    def from_iterable(cls, sources: Iterable[Native]) -> "BatchCalculator":
        """
        Create BatchCalculator from any iterable of Native objects.

        Use this for streaming data or custom data sources.

        Args:
            sources: Iterable yielding Native objects

        Returns:
            BatchCalculator ready to configure and run
        """
        return cls(sources)

    # ---- Configuration Methods (Fluent API) ----

    def with_house_systems(self, engines: list[HouseSystemEngine]) -> "BatchCalculator":
        """Set the house systems to calculate."""
        if not engines:
            raise ValueError("House engine list cannot be empty")
        self._house_engines = engines
        return self

    def with_aspects(self, engine: AspectEngine | None = None) -> "BatchCalculator":
        """Enable aspect calculation with optional custom engine."""
        self._aspect_engine = engine or ModernAspectEngine()
        return self

    def with_orbs(self, engine: OrbEngine | None = None) -> "BatchCalculator":
        """Set the orb calculation engine."""
        self._orb_engine = engine or SimpleOrbEngine()
        return self

    def add_analyzer(self, analyzer: ChartAnalyzer) -> "BatchCalculator":
        """Add a chart analyzer (e.g., PatternAnalysisEngine)."""
        self._analyzers.append(analyzer)
        return self

    def with_progress(
        self, callback: Callable[[int, int, str], None]
    ) -> "BatchCalculator":
        """
        Set progress callback for tracking calculation progress.

        The callback receives:
        - current: Current chart number (1-based)
        - total: Total number of charts (or -1 if unknown)
        - name: Name of current chart being calculated

        Args:
            callback: Function to call with progress updates

        Example::

            def show_progress(current, total, name):
                if total > 0:
                    print(f"Calculating {current}/{total}: {name}")
                else:
                    print(f"Calculating {current}: {name}")

            batch = BatchCalculator.from_registry().with_progress(show_progress)
        """
        self._progress_callback = callback
        return self

    # ---- Calculation Methods ----

    def calculate(self) -> Generator[CalculatedChart, None, None]:
        """
        Calculate charts as a generator (memory efficient).

        Yields charts one at a time, suitable for processing large datasets
        without loading all charts into memory.

        Yields:
            CalculatedChart for each source

        Example::

            for chart in BatchCalculator.from_registry().calculate():
                # Process one chart at a time
                print(chart.get_object("Sun").sign)
        """
        total = self._total_count or -1
        current = 0

        for source in self._sources:
            current += 1
            name = getattr(source, "name", None) or f"Chart {current}"

            # Report progress
            if self._progress_callback:
                self._progress_callback(current, total, name)

            # Build and calculate chart
            chart = self._build_chart(source)
            yield chart

    def calculate_all(self) -> list[CalculatedChart]:
        """
        Calculate all charts and return as a list.

        Loads all charts into memory. Use `calculate()` generator for
        large datasets that don't fit in memory.

        Returns:
            List of all calculated charts

        Example::

            charts = BatchCalculator.from_registry(category="artist").calculate_all()
            print(f"Calculated {len(charts)} artist charts")
        """
        return list(self.calculate())

    def _build_chart(self, source: Native) -> CalculatedChart:
        """Build a single chart from a Native source."""
        builder = ChartBuilder.from_native(source)

        # Configure house systems
        builder.with_house_systems(self._house_engines)

        # Configure aspects (if enabled)
        if self._aspect_engine:
            builder.with_aspects(self._aspect_engine)
            builder.with_orbs(self._orb_engine)

        # Add analyzers
        for analyzer in self._analyzers:
            builder.add_analyzer(analyzer)

        return builder.calculate()

    def count(self) -> int:
        """
        Get the count of sources (if known).

        Returns:
            Number of sources, or -1 if unknown (for streaming iterables)
        """
        if self._total_count is not None:
            return self._total_count
        return -1

    def __len__(self) -> int:
        """
        Get the count of sources.

        Raises:
            TypeError: If count is unknown (streaming iterable)
        """
        if self._total_count is not None:
            return self._total_count
        raise TypeError("Cannot get length of streaming BatchCalculator")

    def __repr__(self) -> str:
        count = self._total_count
        if count is not None:
            return f"<BatchCalculator: {count} sources>"
        return "<BatchCalculator: streaming>"
