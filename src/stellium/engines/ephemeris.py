"""Ephemeris calculation engines."""

import swisseph as swe

from stellium.core.ayanamsa import ZodiacType, get_ayanamsa
from stellium.core.config import CalculationConfig
from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    ObjectType,
    PhaseData,
)
from stellium.core.registry import get_object_info
from stellium.data.paths import initialize_ephemeris
from stellium.utils.cache import cached


def _set_ephemeris_path() -> None:
    """
    Set the path to Swiss Ephemeris data files.

    This function initializes the ephemeris system by:
    1. Ensuring the user ephe directory exists (~/.stellium/ephe/)
    2. Copying bundled ephemeris files from the package if needed
    3. Setting the Swiss Ephemeris path

    The ephemeris files are stored in the user's home directory so that:
    - Users can add their own asteroid ephemeris files
    - The package size stays small (only essential files bundled)
    - Updates don't overwrite user-downloaded files
    """
    initialize_ephemeris()


# Swiss Ephemeris object IDs
# Source: swe.h (Swiss Ephemeris C library constants)
SWISS_EPHEMERIS_IDS = {
    # --- Main Planets & Luminaries ---
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    # --- Earth ---
    # Note: Earth is rarely used, as charts are geocentric
    "Earth": 14,
    # --- Lunar Nodes & Apsides ---
    "Mean Node": 10,
    "True Node": 11,
    "Mean Apogee": 12,  # Mean Lilith (Black Moon)
    "True Apogee": 13,  # True/Osculating Lilith
    # --- Major Asteroids & Centaurs ---
    "Chiron": 15,
    "Pholus": 16,
    "Ceres": 17,
    "Pallas": 18,
    "Juno": 19,
    "Vesta": 20,
    # --- Fictitious / Uranian / Hamburg School ---
    "Cupido": 40,
    "Hades": 41,
    "Zeus": 42,
    "Kronos": 43,
    "Apollon": 44,
    "Admetos": 45,
    "Vulkanus": 46,
    "Poseidon": 47,
    # --- Other "Planets" ---
    "Isis": 48,
    "Nibiru": 49,
    "Harrington": 50,
    "Leverrier": 51,
    "Adams": 52,
    "Lowell": 53,
    "Pickering": 54,
    # --- Special Points (Calculated by swe.houses) ---
    # These are NOT calculated with swe.calc_ut
    # They are returned by the swe.houses() function.
    # The IDs are listed here for completeness.
    "Ascendant": -2,  # SE_ASC constant
    "Midheaven": -3,  # SE_MC constant
    "Vertex": -5,  # SE_VERTEX constant
    # --- Trans-Neptunian Objects (TNOs) ---
    #
    # For asteroids/TNOs with MPC numbers, you must add swe.AST_OFFSET (10000)
    # to the MPC number. Swiss Ephemeris uses this to identify external asteroids.
    #
    # E.g., Eris (MPC 136199) is passed as 136199 + 10000 = 146199
    # The ephemeris file is still named by MPC number: s136199s.se1
    #
    # Common TNOs (MPC number + 10000):
    "Eris": 136199 + 10000,  # MPC 136199
    "Sedna": 90377 + 10000,  # MPC 90377
    "Quaoar": 50000 + 10000,  # MPC 50000
    "Makemake": 136472 + 10000,  # MPC 136472
    "Haumea": 136108 + 10000,  # MPC 136108
    "Orcus": 90482 + 10000,  # MPC 90482
}


class SwissEphemerisEngine:
    """
    Swiss Ephemeris calculation engine.

    This is our default, high-precision ephemeris calculator. Uses the pyswisseph
    library for accurate planetary positions.
    """

    # Class-level set to track which missing ephemeris warnings have been shown
    # This prevents repeated warnings for the same object across multiple calculations
    _warned_missing_ephemeris: set[str] = set()

    def __init__(self):
        """Initialize Swiss Ephemeris."""
        _set_ephemeris_path()
        self._object_ids = SWISS_EPHEMERIS_IDS.copy()

    def _get_object_type(self, name: str) -> ObjectType:
        """Determine the ObjectType for a celestial object by name using the registry."""
        # Try to get from registry first
        obj_info = get_object_info(name)
        if obj_info:
            return obj_info.object_type

        # Fallback for objects not in registry (shouldn't happen, but defensive)
        # Nodes
        if "Node" in name:
            return ObjectType.NODE
        # Points (Lilith/Apogees)
        if "Apogee" in name or "Lilith" in name:
            return ObjectType.POINT
        # Asteroids
        if name in ("Ceres", "Pallas", "Juno", "Vesta"):
            return ObjectType.ASTEROID
        # Everything else is a planet
        return ObjectType.PLANET

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
        config: CalculationConfig | None = None,
    ) -> list[CelestialPosition]:
        """
        Calculate positions using Swiss Ephemeris.

        Args:
            datetime: When to calculate
            location: Where to calculate from
            objects: Which objects to calculate (None = all standard)
            config: Calculation configuration (for zodiac type)

        Returns:
            List of CelestialPosition objects
        """
        # Default to all major objects
        if objects is None:
            objects = [
                "Sun",
                "Moon",
                "Mercury",
                "Venus",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
                "Pluto",
                "True Node",
                "Chiron",
                "Mean Apogee",  # Black Moon Lilith
            ]

        # Use default config if not provided
        if config is None:
            config = CalculationConfig()

        # Set up sidereal mode if needed
        self._setup_sidereal_mode(config)

        positions = []

        for obj_name in objects:
            if obj_name not in self._object_ids:
                continue

            obj_id = self._object_ids[obj_name]
            position = self._calculate_single_position(
                datetime.julian_day, obj_id, obj_name, config
            )
            # Skip objects that couldn't be calculated (missing ephemeris files)
            if position is not None:
                positions.append(position)

        # Add South Node (opposite of True Node)
        if "True Node" in objects:
            north_node = next(p for p in positions if p.name == "True Node")
            south_node = CelestialPosition(
                name="South Node",
                object_type=ObjectType.NODE,
                longitude=(north_node.longitude + 180) % 360,
                latitude=-north_node.latitude,
                speed_longitude=-north_node.speed_longitude,
                speed_latitude=-north_node.speed_latitude,
            )
            positions.append(south_node)

        # Add Aries Point (fixed at 0° longitude - fundamental reference in Uranian astrology)
        if "Aries Point" in objects:
            aries_point = CelestialPosition(
                name="Aries Point",
                object_type=ObjectType.POINT,
                longitude=0.0,
                latitude=0.0,
                speed_longitude=0.0,
                speed_latitude=0.0,
            )
            positions.append(aries_point)

        return positions

    def _setup_sidereal_mode(self, config: CalculationConfig) -> None:
        """Set up sidereal mode if needed.

        Args:
            config: Calculation configuration
        """
        if config.zodiac_type == ZodiacType.SIDEREAL:
            if config.ayanamsa is None:
                raise ValueError("Ayanamsa must be specified for sidereal calculations")
            ayanamsa_info = get_ayanamsa(config.ayanamsa)
            swe.set_sid_mode(ayanamsa_info.swe_constant)

    def _get_calculation_flags(self, config: CalculationConfig) -> int:
        """Get Swiss Ephemeris flags based on configuration.

        Args:
            config: Calculation configuration

        Returns:
            Flags for swe.calc_ut()
        """
        # Base flags: use Swiss Ephemeris data and calculate speeds
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # Add sidereal flag if using sidereal zodiac
        if config.zodiac_type == ZodiacType.SIDEREAL:
            flags |= swe.FLG_SIDEREAL

        # Add heliocentric flag if using Sun-centered coordinates
        if config.heliocentric:
            flags |= swe.FLG_HELCTR

        return flags

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_single_position(
        self,
        julian_day: float,
        object_id: int,
        object_name: str,
        config: CalculationConfig,
    ) -> CelestialPosition | None:
        """
        Calculate position for a single object (cached).

        Args:
            julian_day: Julian day number
            object_id: Swiss Ephemeris object ID
            object_name: Name of the object
            config: Calculation configuration (for zodiac type)

        Returns:
            CelestialPosition with ecliptic AND equatorial coordinates,
            or None if the ephemeris file is missing (with warning printed)
        """
        try:
            # Get appropriate flags for zodiac type
            flags = self._get_calculation_flags(config)

            # Calculate ecliptic coordinates (for zodiac position)
            result = swe.calc_ut(julian_day, object_id, flags)

            # Calculate equatorial coordinates (for declination)
            equ_flags = flags | swe.FLG_EQUATORIAL
            equ_result = swe.calc_ut(julian_day, object_id, equ_flags)

            # Calculate phase data if available (pass longitude for Moon waxing fix)
            phase_data = self._calculate_phase(
                julian_day, object_id, object_name, object_longitude=result[0][0]
            )

            return CelestialPosition(
                name=object_name,
                object_type=self._get_object_type(object_name),
                # Ecliptic coordinates
                longitude=result[0][0],
                latitude=result[0][1],
                distance=result[0][2],
                speed_longitude=result[0][3],
                speed_latitude=result[0][4],
                speed_distance=result[0][5],
                # Equatorial coordinates
                right_ascension=equ_result[0][0],
                declination=equ_result[0][1],
                # Phase data
                phase=phase_data,
            )
        except swe.Error as e:
            error_msg = str(e)
            # Check if this is a missing ephemeris file error
            if "not found" in error_msg.lower() and ".se1" in error_msg.lower():
                self._warn_missing_ephemeris(object_name, object_id, error_msg)
                return None
            # Re-raise other errors
            raise RuntimeError(f"Failed to calculate {object_name}: {e}") from swe.Error

    def _warn_missing_ephemeris(
        self, object_name: str, object_id: int, error_msg: str
    ) -> None:
        """
        Print a helpful warning when an ephemeris file is missing.

        Only warns once per object per session to avoid spam.

        Args:
            object_name: Name of the object
            object_id: Swiss Ephemeris ID (includes AST_OFFSET for asteroids)
            error_msg: Original error message
        """
        # Only warn once per object
        if object_name in SwissEphemerisEngine._warned_missing_ephemeris:
            return
        SwissEphemerisEngine._warned_missing_ephemeris.add(object_name)

        import sys

        # For asteroids, the object_id includes AST_OFFSET (10000)
        # We need to show the MPC number (without offset) in the message
        mpc_number = object_id
        if object_id >= swe.AST_OFFSET:
            mpc_number = object_id - swe.AST_OFFSET

        # Determine the asteroid folder (ast0, ast1, etc.)
        # Files are grouped: ast0 has 0-999, ast1 has 1000-1999, etc.
        folder_num = mpc_number // 1000

        print(
            f"\n⚠️  Missing ephemeris file for {object_name} (skipping)",
            file=sys.stderr,
        )
        print(
            f"   To download, run: stellium ephemeris download-asteroid {mpc_number}",
            file=sys.stderr,
        )
        print(
            f"   Or manually download from: ast{folder_num}/ folder",
            file=sys.stderr,
        )

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_phase(
        self,
        julian_day: float,
        object_id: int,
        object_name: str,
        object_longitude: float | None = None,
    ) -> PhaseData | None:
        """
        Calculate phase data for an object.

        Uses swe.pheno_ut() which works for:
        - Moon (most useful)
        - Sun (phase angle = 0, always fully lit from Earth's perspective)
        - All planets
        - Some asteroids

        Args:
            julian_day: Julian day number
            object_id: Swiss Ephemeris object ID
            object_name: Name of object (for logging)
            object_longitude: Longitude of the object (for Moon waxing calculation)

        Returns:
            PhaseData if calculation succeeds, None otherwise

        Why try/except instead of object type check?
        - Swiss Ephemeris supports phase for many object types
        - The list of supported objects may change
        - Better to attempt and gracefully fail than maintain a whitelist
        - Performance impact is negligible (only runs once per object per chart)
        """
        try:
            # Calculate phase using Swiss Ephemeris
            pheno_result = swe.pheno_ut(julian_day, object_id)

            # pheno_result is a tuple:
            # [0] phase_angle (0-180° - can't distinguish waxing/waning!)
            # [1] illuminated_fraction (0.0-1.0)
            # [2] elongation (same as [0])
            # [3] apparent_diameter (arc seconds)
            # [4] apparent_magnitude (visual)
            # [5] geocentric_parallax (primarily for Moon)

            # For Moon: calculate Sun longitude for accurate waxing determination
            # (phase_angle from pheno_ut is 0-180°, can't tell waxing vs waning)
            sun_longitude = None
            moon_longitude = None
            if object_name == "Moon" and object_longitude is not None:
                # Use default flags (tropical, geocentric) for Sun calc
                flags = swe.FLG_SWIEPH | swe.FLG_SPEED
                sun_result = swe.calc_ut(julian_day, swe.SUN, flags)
                sun_longitude = sun_result[0][0]
                moon_longitude = object_longitude

            return PhaseData(
                phase_angle=pheno_result[0],
                illuminated_fraction=pheno_result[1],
                elongation=pheno_result[2],
                apparent_diameter=pheno_result[3],
                apparent_magnitude=pheno_result[4],
                geocentric_parallax=pheno_result[5],
                sun_longitude=sun_longitude,
                moon_longitude=moon_longitude,
            )

        except (swe.Error, IndexError, TypeError) as _e:
            # Phase calculation not supported for this object
            # This is normal for:
            # - Angles (ASC, MC, etc.)
            # - Nodes
            # - Some hypothetical objects
            # - Fixed stars
            # Silently return None - this is not an error condition
            return None


class MockEphemerisEngine:
    """
    Mock ephemeris engine for testing.

    Returns fixed positions instead of calculating them.

    Useful for:
    - Unit tests
    - Development
    - Benchmarking other components
    """

    def __init__(self, mock_data: dict[str, float] | None = None) -> None:
        """
        Initialize mock engine.

        Args:
            mock_data: Optional dict of {object_name: longitude}
        """
        self._mock_data = mock_data or {
            "Sun": 0.0,  # 0° Aries
            "Moon": 90.0,  # 0° Cancer
            "Mercury": 30.0,  # 0° Taurus
            "Venus": 60.0,  # 0° Gemini
            "Mars": 120.0,  # 0° Leo
        }

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
        config: CalculationConfig | None = None,
    ) -> list[CelestialPosition]:
        """Return mock positions.

        Args:
            datetime: When to calculate positions (ignored in mock)
            location: Where to calculate from (ignored in mock)
            objects: Which objects to calculate (None = all mock objects)
            config: Calculation config (ignored in mock)

        Returns:
            List of mock CelestialPosition objects
        """
        if objects is None:
            objects = list(self._mock_data.keys())

        positions = []
        for obj_name in objects:
            if obj_name in self._mock_data:
                positions.append(
                    CelestialPosition(
                        name=obj_name,
                        object_type=ObjectType.PLANET,
                        longitude=self._mock_data[obj_name],
                        speed_longitude=1.0,  # Direct motion
                    )
                )

        return positions
