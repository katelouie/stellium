"""
ChartBuilder: The main API for creating charts.

This is the fluent interface that users interact with. It orchestrates all the engines
and components to build a complete chart.
"""

import datetime as dt

import swisseph as swe

from stellium.core.ayanamsa import ZodiacType
from stellium.core.config import CalculationConfig
from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    MoonRange,
    UnknownTimeChart,
    longitude_to_sign_and_degree,
)
from stellium.core.native import Native
from stellium.core.protocols import (
    AspectEngine,
    ChartAnalyzer,
    ChartComponent,
    EphemerisEngine,
    HouseSystemEngine,
    OrbEngine,
)
from stellium.data import get_notable_registry
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.ephemeris import SwissEphemerisEngine
from stellium.engines.houses import PlacidusHouses
from stellium.engines.orbs import SimpleOrbEngine
from stellium.utils.cache import Cache, get_default_cache


class ChartBuilder:
    """
    Fluent builder for creating astrological charts.

    Example::

        chart = (
            ChartBuilder.from_native(native)
            .with_ephemeris(SwissEphemeris())
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .with_aspects(ModernAspectEngine())
            .with_orbs(SimpleOrbEngine())
            .calculate()
        )
    """

    def __init__(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        native: Native | None = None,
    ) -> None:
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

        # Declination aspect engine (optional)
        self._declination_aspect_engine = None

        # Unknown time flag
        self._time_unknown: bool = False

    @classmethod
    def from_native(cls, native: Native) -> "ChartBuilder":
        """Create a new ChartBuilder from a Native object.

        This is the primary factory method.
        """
        # The Native object has already done all the processing.
        # We just pass its clean attributes to our "pro chef" __init__.
        builder = cls(native.datetime, native.location, native=native)
        # If the Native has a name, use it
        if native.name:
            builder._name = native.name
        # If the Native has time_unknown flag, propagate it
        if native.time_unknown:
            builder._time_unknown = True
        return builder

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
    def from_details(
        cls,
        datetime_input: str | dt.datetime | dict,
        location_input: str | tuple[float, float] | dict,
        *,
        name: str | None = None,
        time_unknown: bool = False,
    ) -> "ChartBuilder":
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
            name: Optional name of the person or event (for display purposes)
            time_unknown: If True, creates an UnknownTimeChart (no houses/angles,
                Moon shown as range, time normalized to noon)

        Returns:
            ChartBuilder instance ready to configure

        Examples:
            >>> # Simple string inputs
            >>> chart = ChartBuilder.from_details(
            ...     "1994-01-06 11:47",
            ...     "Palo Alto, CA"
            ... ).calculate()
            >>>
            >>> # With a name
            >>> chart = ChartBuilder.from_details(
            ...     "1994-01-06 11:47",
            ...     "Palo Alto, CA",
            ...     name="Kate Louie"
            ... ).calculate()
            >>>
            >>> # Unknown birth time
            >>> chart = ChartBuilder.from_details(
            ...     "1994-01-06",
            ...     "Palo Alto, CA",
            ...     name="Someone",
            ...     time_unknown=True
            ... ).calculate()
        """
        # Create Native internally (it handles all the parsing)
        native = Native(
            datetime_input, location_input, name=name, time_unknown=time_unknown
        )
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

    def with_tnos(self) -> "ChartBuilder":
        """
        Include Trans-Neptunian Objects in the calculation.

        Adds the major TNOs:
        - Eris (dwarf planet, discord)
        - Sedna (isolation, deep healing)
        - Makemake (resourcefulness, manifestation)
        - Haumea (rebirth, fertility)
        - Orcus (oaths, consequences)
        - Quaoar (creation, harmony)

        Note: TNOs require additional Swiss Ephemeris asteroid files (se1 files)
        to be present in your ephemeris data directory. Download them from:
        https://www.astro.com/ftp/swisseph/ephe/

        Example::

            chart = ChartBuilder.from_native(native).with_tnos().calculate()
        """
        tno_names = ["Eris", "Sedna", "Makemake", "Haumea", "Orcus", "Quaoar"]
        for name in tno_names:
            if name not in self._config.include_asteroids:
                self._config.include_asteroids.append(name)
        return self

    def with_uranian(self) -> "ChartBuilder":
        """
        Include Hamburg/Uranian hypothetical planets and points in the calculation.

        Adds the 8 transneptunian points (TNPs) used in Uranian astrology:
        - Cupido (family, groups, art, community)
        - Hades (decay, the past, what's hidden)
        - Zeus (leadership, fire, directed energy)
        - Kronos (authority, expertise, high position)
        - Apollon (expansion, science, commerce, success)
        - Admetos (depth, stagnation, raw materials)
        - Vulkanus (immense power, force, intensity)
        - Poseidon (spirituality, enlightenment, clarity)

        Also adds the Aries Point (0° Aries), a fundamental reference point
        in Uranian astrology representing worldly manifestation and the
        intersection of personal and collective.

        These are hypothetical planets developed by Alfred Witte and the
        Hamburg School of Astrology.

        Example::

            # Just Uranian planets
            chart = ChartBuilder.from_native(native).with_uranian().calculate()

            # Full Uranian setup (TNOs + TNPs)
            chart = ChartBuilder.from_native(native).with_tnos().with_uranian().calculate()
        """
        uranian_names = [
            "Cupido",
            "Hades",
            "Zeus",
            "Kronos",
            "Apollon",
            "Admetos",
            "Vulkanus",
            "Poseidon",
            "Aries Point",
        ]
        for name in uranian_names:
            if name not in self._config.include_asteroids:
                self._config.include_asteroids.append(name)
        return self

    def with_sidereal(self, ayanamsa: str = "lahiri") -> "ChartBuilder":
        """
        Use sidereal zodiac for calculations.

        The sidereal zodiac is based on fixed star positions, unlike the tropical
        zodiac which is based on the seasons. Different ayanamsa systems represent
        different methods of calculating the offset between tropical and sidereal.

        Args:
            ayanamsa: The ayanamsa system to use. Common options:
                - "lahiri" (default) - Indian government standard, most common for Vedic
                - "fagan_bradley" - Primary Western sidereal
                - "raman" - B.V. Raman's system, popular in South India
                - "krishnamurti" - Used in KP system
                - "yukteshwar" - Sri Yukteshwar's system
                See stellium.core.ayanamsa.list_ayanamsas() for all options

        Returns:
            Self for method chaining

        Example:
            >>> # Vedic-style chart with Lahiri ayanamsa
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_sidereal("lahiri")
            ...     .calculate())
            >>>
            >>> # Western sidereal with Fagan-Bradley
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_sidereal("fagan_bradley")
            ...     .calculate())
        """
        self._config.zodiac_type = ZodiacType.SIDEREAL
        self._config.ayanamsa = ayanamsa
        return self

    def with_tropical(self) -> "ChartBuilder":
        """
        Use tropical zodiac for calculations (default).

        The tropical zodiac is based on the seasons, with 0° Aries aligned
        to the March equinox. This is the standard system used in Western
        astrology.

        This method is included for explicitness - tropical is already the
        default, so you only need to call this if you want to override a
        previous .with_sidereal() call.

        Returns:
            Self for method chaining

        Example:
            >>> # Explicit tropical (same as default)
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_tropical()
            ...     .calculate())
            >>>
            >>> # Override previous sidereal setting
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_sidereal("lahiri")
            ...     .with_tropical()  # Back to tropical
            ...     .calculate())
        """
        self._config.zodiac_type = ZodiacType.TROPICAL
        self._config.ayanamsa = None
        return self

    def with_heliocentric(self) -> "ChartBuilder":
        """
        Use heliocentric (Sun-centered) coordinates.

        In a heliocentric chart, positions are calculated as seen from the Sun
        rather than Earth. This changes the chart significantly:

        - **Earth** appears as a planet (replacing the Sun)
        - **Sun** is removed (it's the center point)
        - **Lunar nodes and apogees** are removed (Earth-relative concepts)
        - **Moon** is kept (still orbits Earth, has heliocentric position)
        - **Houses and angles** are not calculated (Earth-horizon concepts)

        Heliocentric charts are used in:
        - Financial astrology (market timing)
        - Some modern experimental techniques
        - Scientific/astronomical contexts

        Returns:
            Self for method chaining

        Example:
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_heliocentric()
            ...     .calculate())
            >>> earth = chart.get_object("Earth")
            >>> print(earth.sign_position)  # Where Earth is from the Sun's view
        """
        self._config.heliocentric = True
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

    def with_declination_aspects(
        self,
        orb: float = 1.0,
        include_types: set | None = None,
    ) -> "ChartBuilder":
        """
        Enable declination aspect calculation (Parallel/Contraparallel).

        Declination aspects are based on equatorial coordinates rather than
        ecliptic longitude. They use a tighter orb (default 1.0°) than
        longitude-based aspects.

        - Parallel: Two bodies at the same declination (same hemisphere).
          Interpreted like a conjunction.
        - Contraparallel: Two bodies at equal declination but opposite
          hemispheres. Interpreted like an opposition.

        Args:
            orb: Maximum orb in degrees (default 1.0°, range 1.0-1.5° typical)
            include_types: Which ObjectTypes to include. Default: PLANET, NODE.
                          Can also include ANGLE, ASTEROID, POINT.

        Returns:
            Self for chaining

        Example:
            >>> chart = (ChartBuilder.from_native(native)
            ...     .with_aspects()
            ...     .with_declination_aspects(orb=1.0)
            ...     .calculate())
            >>> for asp in chart.declination_aspects:
            ...     print(asp.description)
            >>> parallels = chart.get_parallels()
            >>> contraparallels = chart.get_contraparallels()
        """
        from stellium.engines.aspects import DeclinationAspectEngine

        self._declination_aspect_engine = DeclinationAspectEngine(
            orb=orb, include_types=include_types
        )
        return self

    def with_unknown_time(self) -> "ChartBuilder":
        """
        Mark this chart as having unknown birth time.

        When birth time is unknown:
        - Time is normalized to noon for planet calculations
        - Houses and angles will NOT be calculated
        - Moon will include a range showing possible positions throughout the day
        - The resulting chart is an UnknownTimeChart (subclass of CalculatedChart)

        Returns:
            Self for method chaining

        Example:
            >>> chart = (ChartBuilder
            ...     .from_details("1994-01-06", "Palo Alto, CA")
            ...     .with_unknown_time()
            ...     .calculate())
            >>> isinstance(chart, UnknownTimeChart)
            True
            >>> chart.moon_range.arc_size
            13.5  # Moon travels ~13.5° that day
        """
        self._time_unknown = True
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

        # Handle heliocentric mode: add Earth, remove Sun and Earth-relative points
        if self._config.heliocentric:
            # Remove Sun (it's the center in heliocentric)
            objects = [o for o in objects if o != "Sun"]
            # Remove lunar nodes (Earth-relative concepts)
            objects = [o for o in objects if o not in ("True Node", "Mean Node")]
            # Remove lunar apogees (Earth-relative concepts)
            objects = [o for o in objects if "Apogee" not in o]
            # Add Earth (it's now a planet in the chart)
            objects.append("Earth")

        # Ensure all names are unique
        return list(set(objects))

    def calculate(self) -> CalculatedChart | UnknownTimeChart:
        """
        Execute all calculations and return the final chart.

        Returns:
            CalculatedChart with all calculated data, or
            UnknownTimeChart if time_unknown flag is set
        """
        # Dispatch to unknown time calculation if needed
        if self._time_unknown:
            return self._calculate_unknown_time_chart()

        # Step 1: Calculate planetary positions
        objects_to_calculate = self._get_objects_list()
        positions = self._ephemeris.calculate_positions(
            self._datetime, self._location, objects_to_calculate, self._config
        )

        # Step 2: Calculate all house systems AND angles
        # (Skip for heliocentric charts - houses are Earth-horizon concepts)
        house_systems_map: dict[str, HouseCusps] = {}
        calculated_angles: list[CelestialPosition] = []
        house_placements_map: dict[str, dict[str, int]] = {}

        if not self._config.heliocentric:
            for engine in self._house_engines:
                system_name = engine.system_name
                if system_name in house_systems_map:
                    continue  # Avoid duplicate calculations

                # Call the efficient protocol method
                cusps, angles = engine.calculate_house_data(
                    self._datetime, self._location, self._config
                )

                house_systems_map[system_name] = cusps

                # Angles are universal, only save them once
                if not calculated_angles:
                    calculated_angles = angles

            # Step 3: Add angles to the main position list
            positions.extend(calculated_angles)

            # Step 4: Assign house placements for all systems
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

        # Step 6b: Calculate declination aspects (if engine provided)
        declination_aspects = []
        if self._declination_aspect_engine:
            declination_aspects = self._declination_aspect_engine.calculate_aspects(
                positions
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
            declination_aspects=tuple(declination_aspects),
            metadata=component_metadata,  # Start with component metadata
        )

        final_metadata = component_metadata.copy()
        # Allow external metadata injection (used by ReturnBuilder, etc.)
        if hasattr(self, "_extra_metadata"):
            final_metadata.update(self._extra_metadata)
        for analyzer in self._analyzers:
            final_metadata[analyzer.metadata_name] = analyzer.analyze(provisional_chart)

        # Note: Cache stats removed from metadata for performance.
        # get_stats() was scanning 100k+ files on every calculate() call.
        # Use stellium.utils.cache.get_cache_stats() directly if needed.

        # Add chart name to metadata if set
        if self._name is not None:
            final_metadata["name"] = self._name

        # Calculate ayanamsa value if sidereal
        ayanamsa_value = None
        if self._config.zodiac_type == ZodiacType.SIDEREAL:
            from stellium.core.ayanamsa import get_ayanamsa_value

            ayanamsa_value = get_ayanamsa_value(
                self._datetime.julian_day,
                self._config.ayanamsa,  # type: ignore  # Already validated in config.__post_init__
            )

        # Build chart tags based on configuration
        chart_tags: tuple[str, ...] = ()
        if self._config.heliocentric:
            chart_tags = ("heliocentric",)

        # Step 7: Build final chart
        return CalculatedChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            house_systems=house_systems_map,
            house_placements=house_placements_map,
            aspects=tuple(aspects),
            declination_aspects=tuple(declination_aspects),
            metadata=final_metadata,
            zodiac_type=self._config.zodiac_type,
            ayanamsa=self._config.ayanamsa,
            ayanamsa_value=ayanamsa_value,
            chart_tags=chart_tags,
        )

    def _calculate_unknown_time_chart(self) -> UnknownTimeChart:
        """
        Calculate a chart for unknown birth time.

        This is a specialized calculation that:
        - Calculates planetary positions for noon
        - Skips house and angle calculations entirely
        - Calculates Moon range (positions at 00:00, 12:00, 23:59)
        - Still calculates aspects (using noon Moon)

        Returns:
            UnknownTimeChart with moon_range and no houses/angles
        """
        # Step 1: Calculate planetary positions (at noon, already normalized)
        objects_to_calculate = self._get_objects_list()
        positions = self._ephemeris.calculate_positions(
            self._datetime, self._location, objects_to_calculate
        )

        # Step 2: Calculate Moon range (need positions at start and end of day)
        moon_range = self._calculate_moon_range()

        # Step 3: Calculate aspects (if engine provided)
        # Uses noon Moon position for aspect calculations
        aspects = []
        if self._aspect_engine:
            aspects = self._aspect_engine.calculate_aspects(
                positions,
                self._orb_engine,
            )

        # Build metadata
        final_metadata: dict = {}

        # Note: Cache stats removed from metadata for performance.
        # get_stats() was scanning 100k+ files on every calculate() call.

        # Add chart name to metadata if set
        if self._name is not None:
            final_metadata["name"] = self._name

        # Mark as time unknown
        final_metadata["time_unknown"] = True

        # Step 4: Build UnknownTimeChart (no houses, no angles)
        return UnknownTimeChart(
            datetime=self._datetime,
            location=self._location,
            positions=tuple(positions),
            house_systems={},  # No houses for unknown time
            house_placements={},  # No house placements
            aspects=tuple(aspects),
            metadata=final_metadata,
            moon_range=moon_range,
        )

    def _calculate_moon_range(self) -> MoonRange:
        """
        Calculate the Moon's position range for the day.

        Calculates Moon position at:
        - 00:00:00 (start of day)
        - 12:00:00 (noon - displayed position)
        - 23:59:59 (end of day)

        Returns:
            MoonRange with start, noon, and end positions
        """
        # Get the date from current datetime (already at noon)
        utc_dt = self._datetime.utc_datetime

        # Calculate Julian Day for start of day (00:00:00 UTC)
        start_of_day = utc_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        jd_start = swe.julday(
            start_of_day.year,
            start_of_day.month,
            start_of_day.day,
            0.0,  # 00:00:00
        )

        # Calculate Julian Day for end of day (23:59:59 UTC)
        end_of_day = utc_dt.replace(hour=23, minute=59, second=59, microsecond=0)
        jd_end = swe.julday(
            end_of_day.year,
            end_of_day.month,
            end_of_day.day,
            23.0 + 59.0 / 60.0 + 59.0 / 3600.0,  # 23:59:59
        )

        # Get Moon position at start of day
        moon_start = swe.calc_ut(jd_start, swe.MOON)[0]
        start_longitude = moon_start[0]

        # Get Moon position at end of day
        moon_end = swe.calc_ut(jd_end, swe.MOON)[0]
        end_longitude = moon_end[0]

        # Get Moon position at noon (current calculation time)
        moon_noon = swe.calc_ut(self._datetime.julian_day, swe.MOON)[0]
        noon_longitude = moon_noon[0]

        # Determine signs
        start_sign, _ = longitude_to_sign_and_degree(start_longitude)
        end_sign, _ = longitude_to_sign_and_degree(end_longitude)

        # Check if Moon crosses sign boundary
        crosses_boundary = start_sign != end_sign

        return MoonRange(
            start_longitude=start_longitude,
            end_longitude=end_longitude,
            noon_longitude=noon_longitude,
            start_sign=start_sign,
            end_sign=end_sign,
            crosses_sign_boundary=crosses_boundary,
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
