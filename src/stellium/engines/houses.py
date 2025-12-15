"""House system calculation engines."""

import swisseph as swe

from stellium.core.ayanamsa import ZodiacType, get_ayanamsa
from stellium.core.config import CalculationConfig
from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    ObjectType,
)
from stellium.utils.cache import cached

# Swiss Ephemeris house system codes
HOUSE_SYSTEM_CODES = {
    "Alcabitius": b"B",
    "APC": b"Y",
    "Axial Rotation": b"X",
    "Campanus": b"C",
    "Equal": b"A",
    "Equal (MC)": b"D",
    "Equal (Vertex)": b"E",
    "Gauquelin": b"G",
    "Horizontal": b"H",
    "Koch": b"K",
    "Krusinski": b"U",
    "Morinus": b"M",
    "Placidus": b"P",
    "Porphyry": b"O",
    "Regiomontanus": b"R",
    "Topocentric": b"T",
    "Vehlow Equal": b"V",
    "Whole Sign": b"W",
}


class SwissHouseSystemBase:
    """
    Provides a default implementation for calling swisseph and assigning houses.

    This is NOT a protocol, just a helper class for code reuse.
    """

    @property
    def system_name(self) -> str:
        return "BaseClass"

    def _setup_sidereal_mode(self, config: CalculationConfig | None) -> None:
        """Set up sidereal mode if needed.

        Args:
            config: Calculation configuration (None = use tropical)
        """
        if config and config.zodiac_type == ZodiacType.SIDEREAL:
            if config.ayanamsa is None:
                raise ValueError("Ayanamsa must be specified for sidereal calculations")
            ayanamsa_info = get_ayanamsa(config.ayanamsa)
            swe.set_sid_mode(ayanamsa_info.swe_constant)

    def _get_calculation_flags(self, config: CalculationConfig | None) -> int:
        """Get Swiss Ephemeris flags based on configuration.

        Args:
            config: Calculation configuration (None = use tropical)

        Returns:
            Flags for swe.houses_ex()
        """
        flags = 0  # Default for tropical

        if config and config.zodiac_type == ZodiacType.SIDEREAL:
            flags = swe.FLG_SIDEREAL

        return flags

    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def _calculate_swiss_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        system_code: bytes,
        config: CalculationConfig | None = None,
    ) -> tuple:
        """Cached Swiss Ephemeris house calculation.

        Args:
            julian_day: Julian day number
            latitude: Geographic latitude
            longitude: Geographic longitude
            system_code: House system code (e.g., b"P" for Placidus)
            config: Calculation configuration (for zodiac type)

        Returns:
            Tuple of (cusps, angles) from Swiss Ephemeris
        """
        # Set up sidereal mode if needed
        self._setup_sidereal_mode(config)

        # Get appropriate flags
        flags = self._get_calculation_flags(config)

        # Use houses_ex for sidereal support
        return swe.houses_ex(
            julian_day, latitude, longitude, hsys=system_code, flags=flags
        )

    def assign_houses(
        self, positions: list[CelestialPosition], cusps: HouseCusps
    ) -> dict[str, int]:
        """Assign house numbers to positions. Returns a simple name: house dict."""
        placements = {}
        for pos in positions:
            house_num = self._find_house(pos.longitude, cusps.cusps)
            placements[pos.name] = house_num
        return placements

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Find which house a longitude falls into."""
        cusp_list = list(cusps)

        for i in range(12):
            cusp1 = cusp_list[i]
            cusp2 = cusp_list[(i + 1) % 12]

            # Handles wrapping about 360 degrees
            if cusp2 < cusp1:
                cusp2 += 360
                test_long = longitude if longitude >= cusp1 else longitude + 360
            else:
                test_long = longitude

            if cusp1 <= test_long < cusp2:
                return i + 1

        return 1  # fallback

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        config: CalculationConfig | None = None,
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """Calculate house system's house cusps and chart angles.

        Args:
            datetime: Chart datetime
            location: Chart location
            config: Calculation configuration (for zodiac type)

        Returns:
            Tuple of (house cusps, angle positions)
        """
        # Cusps
        cusps_list, angles_list = self._calculate_swiss_houses(
            datetime.julian_day,
            location.latitude,
            location.longitude,
            HOUSE_SYSTEM_CODES[self.system_name],
            config,
        )
        cusps = HouseCusps(system=self.system_name, cusps=tuple(cusps_list))

        # Chart angles
        asc = angles_list[0]
        mc = angles_list[1]
        ramc = angles_list[2]
        vertex = angles_list[3]

        angles = [
            CelestialPosition(name="ASC", object_type=ObjectType.ANGLE, longitude=asc),
            CelestialPosition(name="MC", object_type=ObjectType.ANGLE, longitude=mc),
            # Derive Dsc and IC
            CelestialPosition(
                name="DSC", object_type=ObjectType.ANGLE, longitude=(asc + 180) % 360
            ),
            CelestialPosition(
                name="IC", object_type=ObjectType.ANGLE, longitude=(mc + 180) % 360
            ),
            # Include Vertex
            CelestialPosition(
                name="Vertex", object_type=ObjectType.POINT, longitude=vertex
            ),
            CelestialPosition(
                name="RAMC", object_type=ObjectType.TECHNICAL, longitude=ramc
            ),
        ]

        return cusps, angles


class PlacidusHouses(SwissHouseSystemBase):
    """Placidus house system engine."""

    @property
    def system_name(self) -> str:
        return "Placidus"


class WholeSignHouses(SwissHouseSystemBase):
    """Whole sign house system engine."""

    @property
    def system_name(self) -> str:
        return "Whole Sign"


class KochHouses(SwissHouseSystemBase):
    """Koch house system engine."""

    @property
    def system_name(self) -> str:
        return "Koch"


class EqualHouses(SwissHouseSystemBase):
    """Equal house system engine."""

    @property
    def system_name(self) -> str:
        return "Equal"


class PorphyryHouses(SwissHouseSystemBase):
    """Porphyry house system engine."""

    @property
    def system_name(self) -> str:
        return "Porphyry"


class RegiomontanusHouses(SwissHouseSystemBase):
    """Regiomontanus house system engine."""

    @property
    def system_name(self) -> str:
        return "Regiomontanus"


class CampanusHouses(SwissHouseSystemBase):
    """Campanus house system engine."""

    @property
    def system_name(self) -> str:
        return "Campanus"


class EqualMCHouses(SwissHouseSystemBase):
    """Equal (MC) house system engine."""

    @property
    def system_name(self) -> str:
        return "Equal (MC)"


class VehlowEqualHouses(SwissHouseSystemBase):
    """Vehlow Equal house system engine."""

    @property
    def system_name(self) -> str:
        return "Vehlow Equal"


class AlcabitiusHouses(SwissHouseSystemBase):
    """Alcabitius house system engine."""

    @property
    def system_name(self) -> str:
        return "Alcabitius"


class TopocentricHouses(SwissHouseSystemBase):
    """Topocentric house system engine."""

    @property
    def system_name(self) -> str:
        return "Topocentric"


class MorinusHouses(SwissHouseSystemBase):
    """Morinus house system engine."""

    @property
    def system_name(self) -> str:
        return "Morinus"


class EqualVertexHouses(SwissHouseSystemBase):
    """Equal (Vertex) house system engine."""

    @property
    def system_name(self) -> str:
        return "Equal (Vertex)"


class GauquelinHouses(SwissHouseSystemBase):
    """Gauquelin house system engine."""

    @property
    def system_name(self) -> str:
        return "Gauquelin"


class HorizontalHouses(SwissHouseSystemBase):
    """Horizontal house system engine."""

    @property
    def system_name(self) -> str:
        return "Horizontal"


class KrusinskiHouses(SwissHouseSystemBase):
    """Krusinski house system engine."""

    @property
    def system_name(self) -> str:
        return "Krusinski"


class AxialRotationHouses(SwissHouseSystemBase):
    """Axial Rotation house system engine."""

    @property
    def system_name(self) -> str:
        return "Axial Rotation"


class APCHouses(SwissHouseSystemBase):
    """APC house system engine."""

    @property
    def system_name(self) -> str:
        return "APC"
