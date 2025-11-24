"""
ChartBuilder: The main API for creating charts.

This is the fluent interface that users interact with. It orchestrates all the engines
and components to build a complete chart.
"""

import datetime as dt

import pytz
import swisseph as swe

from starlight.core.config import CalculationConfig
from starlight.core.models import (
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
)
from starlight.core.native import Native
from starlight.core.protocols import (
    AspectEngine,
    ChartAnalyzer,
    ChartComponent,
    EphemerisEngine,
    HouseSystemEngine,
    OrbEngine,
)
from starlight.data import get_notable_registry
from starlight.engines.aspects import ModernAspectEngine
from starlight.engines.ephemeris import SwissEphemerisEngine
from starlight.engines.houses import PlacidusHouses
from starlight.engines.orbs import SimpleOrbEngine
from starlight.utils.cache import Cache, cached, get_default_cache


class ChartBuilder:
    """
    Fluent builder for creating astrological charts.

    Usage:
        chart = (
            ChartBuilder.from_native(native)
            .with_ephemeris(SwissEphemeris())
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .with_aspects(ModernAspectEngine())
            .with_orbs(SimpleOrbEngine())
            .calculate()
        )
    """

    def __init__(self, datetime: ChartDateTime, location: ChartLocation, native: Native | None = None) -> None:
        """
        Initialize builder with required data.

        Args:
            datetime: Chart datetime
            location: Chart location
            native: Optional Native object (for convenience methods)
        """
        self._datetime = datetime
        self._location = location
        self.native = native  # Store Native for reference

        # Default engines (can be overridden)
        self._ephemeris: EphemerisEngine = SwissEphemerisEngine()
        self._house_engines: list[HouseSystemEngine] = [PlacidusHouses()]
        self._aspect_engine: AspectEngine | None = None  # optional
        self._orb_engine: OrbEngine = SimpleOrbEngine()

        # Configuration
        self._config = CalculationConfig()

        # Additional components
        self._components: list[ChartComponent] = []

        # Analyzers
        self._analyzers: list[ChartAnalyzer] = []

        # Cache management
        self._cache: Cache | None = None

        # Optional chart name (for display purposes)
        self._name: str | None = None

    @classmethod
    def from_native(cls, native: Native) -> "ChartBuilder":
        """Create a new ChartBuilder from a Native object.

        This is the primary factory method.
        """
        # The Native object has already done all the processing.
        # We just pass its clean attributes to our "pro chef" __init__.
        return cls(native.datetime, native.location, native=native)

    @classmethod
    def from_notable(cls, name: str) -> "ChartBuilder":
        """
        Create a ChartBuilder from the notable registry by name.

        This is a convenience method that looks up a famous birth or event
        from the curated registry and creates a chart for it.

        The notable's name is automatically set on the chart for display purposes.

        Args:
            name: Name of person or event (case-insensitive)

        Returns:
            ChartBuilder instance ready to build, with name pre-set

        Raises:
            ValueError: If name not found in registry

        Example:
            >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
            >>> chart = ChartBuilder.from_notable("marie curie").calculate()
        """
        registry = get_notable_registry()
        notable = registry.get_by_name(name)
        if notable is None:
            available = len(registry)
            raise ValueError(
                f"No notable found: '{name}'. "
                f"Registry contains {available} entries. "
                f"Use get_notable_registry().get_all() to see available notables."
            )
        # Notable IS-A Native, so we can use from_native!
        builder = cls.from_native(notable)
        # Automatically set the notable's name on the chart
        builder._name = notable.name
        return builder

    @classmethod
    def from_details(cls, datetime_input: str | dt.datetime | dict, location_input: str | tuple[float, float] | dict) -> "ChartBuilder":
        """
        Create a ChartBuilder from datetime and location (convenience method).

        This method accepts flexible datetime and location inputs, creates a Native
        object internally, and returns a ready-to-configure ChartBuilder.

        Args:
            datetime_input: Datetime as string, datetime object, or dict
                - String: "2024-11-24 14:30", "11/24/2024 2:30 PM", etc.
                - datetime: Any datetime object (naive will be localized to location)
                - dict: {"year": 2024, "month": 11, "day": 24, "hour": 14, "minute": 30}
            location_input: Location as string, (lat, lon) tuple, or dict
                - String: "Palo Alto, CA" (will be geocoded)
                - Tuple: (37.4419, -122.1430)
                - dict: {"latitude": 37.4419, "longitude": -122.1430, "name": "Palo Alto"}

        Returns:
            ChartBuilder instance ready to configure

        Examples:
            >>> # Simple string inputs
            >>> chart = ChartBuilder.from_details(
            ...     "1994-01-06 11:47",
            ...     "Palo Alto, CA"
            ... ).calculate()
            >>>
            >>> # US date format
            >>> chart = ChartBuilder.from_details(
            ...     "01/06/1994 11:47 AM",
            ...     "Seattle, WA"
            ... ).calculate()
            >>>
            >>> # With coordinates
            >>> chart = ChartBuilder.from_details(
            ...     "2024-11-24 14:30",
            ...     (37.4419, -122.1430)
            ... ).calculate()
        """
        # Create Native internally (it handles all the parsing)
        native = Native(datetime_input, location_input)
        # Use from_native which stores the native reference
        return cls.from_native(native)

    # ---- Fluent configuration methods ---
    def with_ephemeris(self, engine: EphemerisEngine) -> "ChartBuilder":
        """Set the ephemeris engine."""
        self._ephemeris = engine
        return self

    def with_house_systems(self, engines: list[HouseSystemEngine]) -> "ChartBuilder":
        """
        Replaces the entire list of house engines (eg - to calculate *only* Whole Sign)
        """
        if not engines:
            raise ValueError("House engine list cannot be empty")
        self._house_engines = engines
        return self

    def add_house_system(self, engine: HouseSystemEngine) -> "ChartBuilder":
        """
        Adds an additional house engine to the calculation list.
        (e.g., to calculate Placidus *and* Whole Sign)
        """
        self._house_engines.append(engine)
        return self

    def with_aspects(self, engine: AspectEngine | None = None) -> "ChartBuilder":
        """Set the aspect calculation engine."""
        self._aspect_engine = engine or ModernAspectEngine()
        return self

    def with_orbs(self, engine: OrbEngine | None = None) -> "ChartBuilder":
        """Set the orb calculation engine."""
        self._orb_engine = engine or SimpleOrbEngine()
        return self

    def with_name(self, name: str) -> "ChartBuilder":
        """
        Set the chart name (for display purposes).

        Args:
            name: Name to display on the chart (e.g., person's name, event name)

        Returns:
            Self for method chaining

        Example:
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_name("John Doe")
            ...     .calculate())
        """
        self._name = name
        return self

    def with_config(self, config: CalculationConfig) -> "ChartBuilder":
        """Set the calculation configuration (which objects to find)."""
        self._config = config
        return self

    def add_component(self, component: ChartComponent) -> "ChartBuilder":
        """Add an additional calculation component (e.g. ArabicParts)."""
        self._components.append(component)
        return self

    def add_analyzer(self, analyzer: ChartAnalyzer) -> "ChartBuilder":
        """
        Adds a data analyzer to the calculation pipeline.
        (e.g., PatternDetector)
        """
        self._analyzers.append(analyzer)
        return self

    # --- Calculation ---

    def _get_objects_list(self) -> list[str]:
        """Get list of objects to calculate based on config."""
        objects = self._config.include_planets.copy()

        if self._config.include_nodes:
            objects.append("True Node")

        if self._config.include_chiron:
            objects.append("Chiron")

        objects.extend(self._config.include_points)
        objects.extend(self._config.include_asteroids)

        # Ensure all names are unique
        return list(set(objects))

    def calculate(self) -> CalculatedChart:
        """
        Execute all calculations and return the final chart.

        Returns:
            CalculatedChart with all calculated data
        """
        # Step 1: Calculate planetary positions
        objects_to_calculate = self._get_objects_list()
        positions = self._ephemeris.calculate_positions(
            self._datetime, self._location, objects_to_calculate
        )

        # Step 2: Calculate all house systems AND angles
        house_systems_map: dict[str, HouseCusps] = {}
        calculated_angles: list[CelestialPosition] = []

        for engine in self._house_engines:
            system_name = engine.system_name
            if system_name in house_systems_map:
                continue  # Avoid duplicate calculations

            # Call the efficient protocol method
            cusps, angles = engine.calculate_house_data(self._datetime, self._location)

            house_systems_map[system_name] = cusps

            # Angles are universal, only save them once
            if not calculated_angles:
                calculated_angles = angles

        # Step 3: Add angles to the main position list
        positions.extend(calculated_angles)

        # Step 4: Assign house placements for all systems
        house_placements_map: dict[str, dict[str, int]] = {}
        for engine in self._house_engines:
            system_name = engine.system_name
            cusps = house_systems_map[system_name]

            # Get the {object_name: house_num} dict
            placements = engine.assign_houses(positions, cusps)
            house_placements_map[system_name] = placements

        # Step 5: Run additional components (Arabic parts, etc)
        # (Components can now see angles in the position list)
        component_metadata = {}

        for component in self._components:
            additional = component.calculate(
                self._datetime,
                self._location,
                positions,
                house_systems_map,  # Pass the full map of cusps
                house_placements_map,
            )
            positions.extend(additional)

            # If component returned new CelestialPositions
            # add their house placements to the placement map for all systems
            if additional:
                for engine in self._house_engines:
                    system_name = engine.system_name
                    cusps = house_systems_map[system_name]
                    placements = engine.assign_houses(additional, cusps)
                    house_placements_map[system_name].update(placements)

            # Add the metadata to the chart object if component has any
            if hasattr(component, "get_metadata"):
                metadata_key = component.metadata_name
                component_metadata[metadata_key] = component.get_metadata()

        # Step 6: Calculate aspects (if engine provided)
        aspects = []
        if self._aspect_engine:
            aspects = self._aspect_engine.calculate_aspects(
                positions,
                self._orb_engine,  # Pass the configured orb engine
            )

        # Run analyzers
        # --- Create a "provisional" chart object ---
        # Analyzers need the *full chart* to work on.
        provisional_chart = CalculatedChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            house_systems=house_systems_map,
            house_placements=house_placements_map,
            aspects=tuple(aspects),
            metadata=component_metadata,  # Start with component metadata
        )

        final_metadata = component_metadata.copy()
        for analyzer in self._analyzers:
            final_metadata[analyzer.metadata_name] = analyzer.analyze(provisional_chart)

        # Add cache statistics to the metadata
        cache_stats = self._get_cache().get_stats()
        final_metadata["cache_stats"] = cache_stats

        # Add chart name to metadata if set
        if self._name is not None:
            final_metadata["name"] = self._name

        # Step 7: Build final chart
        return CalculatedChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            house_systems=house_systems_map,
            house_placements=house_placements_map,
            aspects=tuple(aspects),
            metadata=final_metadata,
        )

    def with_cache(
        self,
        cache: Cache | None = None,
        enabled: bool = True,
        cache_dir: str = ".cache",
        max_age_seconds: int = 86400,
    ) -> "ChartBuilder":
        """
        Configure caching for this chart calculation.

        Args:
            cache: Custom cache instance (creates new one if None)
            enabled: Whether to enable caching
            cache_dir: Cache directory
            max_age_seconds: Maximum cache age

        Returns:
            Self for chaining

        Examples:
            # Disable caching for this chart
            chart = ChartBuilder.from_native(native).with_cache(enabled=False).calculate()

            # Use custom cache directory
            chart = ChartBuilder.from_native(native).with_cache(cache_dir="/tmp/my_cache").calculate()

            # Use shared cache instance
            my_cache = Cache(cache_dir="/shared/cache")
            chart1 = ChartBuilder.from_native(n1).with_cache(cache=my_cache).calculate()
            chart2 = ChartBuilder.from_native(n2).with_cache(cache=my_cache).calculate()
        """
        if cache is not None:
            self._cache = cache
        else:
            self._cache = Cache(
                cache_dir=cache_dir,
                max_age_seconds=max_age_seconds,
                enabled=enabled,
            )

        return self

    def _get_cache(self) -> Cache:
        """Get the cache instance for this builder."""
        if self._cache is None:
            return get_default_cache()
        return self._cache
