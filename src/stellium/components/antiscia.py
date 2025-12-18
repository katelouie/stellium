"""
Antiscia and Contra-Antiscia calculator component.

Antiscia are reflection points across the solstice axis (0° Cancer / 0° Capricorn).
Two planets are "in antiscia" when one planet's antiscion point is conjunct
another planet - this is considered a "hidden conjunction."

Contra-antiscia are reflections across the equinox axis (0° Aries / 0° Libra).

Traditional astrologers use antiscia to find hidden connections between planets
that don't make conventional aspects.

Formulas:
- Antiscion = (360° - longitude + 180°) % 360° = (180° - longitude) % 360°
  Equivalently: reflect across Cancer-Capricorn axis
- Contra-antiscion = (360° - longitude) % 360°
  Equivalently: reflect across Aries-Libra axis
"""

from dataclasses import dataclass
from typing import Any

from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    ObjectType,
)


@dataclass(frozen=True)
class AntisciaConjunction:
    """
    Represents a conjunction between a planet and another planet's antiscion.

    When planet1's antiscion point is conjunct planet2, we say
    "planet1 and planet2 are in antiscia."
    """

    planet1: str  # The planet whose antiscion is involved
    planet2: str  # The planet that is conjunct the antiscion
    orb: float  # The orb of the conjunction in degrees
    is_applying: bool  # Whether the aspect is applying (getting closer)
    antiscion_longitude: float  # The antiscion point's longitude
    planet2_longitude: float  # Planet2's longitude

    @property
    def description(self) -> str:
        """Human-readable description of this antiscia relationship."""
        direction = "applying" if self.is_applying else "separating"
        return f"{self.planet1} in antiscia with {self.planet2} ({direction}, orb {self.orb:.1f}°)"


# Default planets to calculate antiscia for (traditional 7 + modern outers)
DEFAULT_ANTISCIA_PLANETS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    # Modern additions (optional but included by default)
    "Uranus",
    "Neptune",
    "Pluto",
    # Nodes
    "True Node",
]


class AntisciaCalculator:
    """
    Calculate antiscia and contra-antiscia points and find conjunctions.

    Antiscia are reflection points that reveal "hidden" connections between
    planets. When planet A's antiscion is conjunct planet B, they are said
    to be "in antiscia" - a connection as powerful as a conjunction but
    operating on a hidden or fated level.

    Usage:
        chart = (ChartBuilder.from_native(native)
            .add_component(AntisciaCalculator())
            .calculate())

        # Access antiscia points (added to chart.positions)
        antiscia_points = [p for p in chart.positions
                          if p.object_type == ObjectType.ANTISCION]

        # Access conjunction data (in metadata)
        antiscia_data = chart.metadata.get("antiscia", {})
        conjunctions = antiscia_data.get("conjunctions", [])
    """

    metadata_name = "antiscia"

    def __init__(
        self,
        planets: list[str] | None = None,
        orb: float = 1.5,
        include_contra: bool = True,
    ):
        """
        Initialize the antiscia calculator.

        Args:
            planets: List of planet names to calculate antiscia for.
                    Defaults to traditional 7 + Uranus, Neptune, Pluto, True Node.
            orb: Maximum orb for antiscia conjunctions (default 1.5°).
                 Traditional practice uses tight orbs of 1-2°.
            include_contra: Whether to also calculate contra-antiscia (default True).
        """
        self.planets = planets or DEFAULT_ANTISCIA_PLANETS
        self.orb = orb
        self.include_contra = include_contra

        # Store calculated data for get_metadata()
        self._conjunctions: list[AntisciaConjunction] = []
        self._contra_conjunctions: list[AntisciaConjunction] = []

    @property
    def component_name(self) -> str:
        return "Antiscia"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate antiscia and contra-antiscia points.

        Returns the antiscia points as CelestialPosition objects.
        Also populates internal conjunction data accessible via get_metadata().
        """
        # Reset conjunction lists
        self._conjunctions = []
        self._contra_conjunctions = []

        # Build lookup of positions by name
        position_map = {p.name: p for p in positions}

        # Calculate antiscia points
        antiscia_points: list[CelestialPosition] = []

        for planet_name in self.planets:
            if planet_name not in position_map:
                continue

            planet = position_map[planet_name]

            # Calculate antiscion point (reflection across Cancer-Capricorn axis)
            # Formula: antiscion = (180 - longitude) % 360
            # This reflects: 0° Aries -> 0° Virgo, 15° Taurus -> 15° Leo, etc.
            antiscion_long = (180.0 - planet.longitude) % 360.0

            antiscia_points.append(
                CelestialPosition(
                    name=f"{planet_name} Antiscion",
                    object_type=ObjectType.ANTISCION,
                    longitude=antiscion_long,
                    latitude=0.0,  # Antiscia are on the ecliptic
                    distance=0.0,
                )
            )

            # Calculate contra-antiscion if enabled
            if self.include_contra:
                # Contra-antiscion reflects across Aries-Libra axis
                # Formula: contra = (360 - longitude) % 360 = -longitude % 360
                contra_long = (360.0 - planet.longitude) % 360.0

                antiscia_points.append(
                    CelestialPosition(
                        name=f"{planet_name} Contra-Antiscion",
                        object_type=ObjectType.CONTRA_ANTISCION,
                        longitude=contra_long,
                        latitude=0.0,
                        distance=0.0,
                    )
                )

        # Find conjunctions between antiscia points and planets
        self._find_conjunctions(positions, position_map)

        return antiscia_points

    def _find_conjunctions(
        self,
        positions: list[CelestialPosition],
        position_map: dict[str, CelestialPosition],
    ) -> None:
        """
        Find conjunctions between antiscia/contra-antiscia points and planets.

        A conjunction occurs when an antiscion point is within orb of a planet.
        """
        # Get all planets we're checking against
        check_against = [
            p
            for p in positions
            if p.object_type
            in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE)
            and p.name in self.planets
        ]

        for planet1_name in self.planets:
            if planet1_name not in position_map:
                continue

            planet1 = position_map[planet1_name]

            # Calculate antiscion longitude
            antiscion_long = (180.0 - planet1.longitude) % 360.0

            # Check for conjunctions with other planets
            for planet2 in check_against:
                # Don't check a planet against its own antiscion
                if planet2.name == planet1_name:
                    continue

                orb = self._calculate_orb(antiscion_long, planet2.longitude)
                if orb <= self.orb:
                    # Determine if applying based on speeds
                    # (simplified - assumes planet2 is moving toward/away from antiscion)
                    is_applying = self._is_applying(
                        antiscion_long, planet2.longitude, planet2.speed_longitude
                    )

                    self._conjunctions.append(
                        AntisciaConjunction(
                            planet1=planet1_name,
                            planet2=planet2.name,
                            orb=orb,
                            is_applying=is_applying,
                            antiscion_longitude=antiscion_long,
                            planet2_longitude=planet2.longitude,
                        )
                    )

            # Check contra-antiscia conjunctions if enabled
            if self.include_contra:
                contra_long = (360.0 - planet1.longitude) % 360.0

                for planet2 in check_against:
                    if planet2.name == planet1_name:
                        continue

                    orb = self._calculate_orb(contra_long, planet2.longitude)
                    if orb <= self.orb:
                        is_applying = self._is_applying(
                            contra_long, planet2.longitude, planet2.speed_longitude
                        )

                        self._contra_conjunctions.append(
                            AntisciaConjunction(
                                planet1=planet1_name,
                                planet2=planet2.name,
                                orb=orb,
                                is_applying=is_applying,
                                antiscion_longitude=contra_long,
                                planet2_longitude=planet2.longitude,
                            )
                        )

    def _calculate_orb(self, long1: float, long2: float) -> float:
        """Calculate the shortest angular distance between two longitudes."""
        diff = abs(long2 - long1)
        if diff > 180:
            diff = 360 - diff
        return diff

    def _is_applying(
        self, target_long: float, planet_long: float, planet_speed: float
    ) -> bool:
        """
        Determine if a planet is applying to (moving toward) a target point.

        Args:
            target_long: The longitude of the target (antiscion point)
            planet_long: The planet's current longitude
            planet_speed: The planet's daily motion in degrees

        Returns:
            True if the planet is moving toward the target
        """
        if planet_speed == 0:
            return False

        # Calculate signed distance to target
        diff = target_long - planet_long
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        # Planet is applying if it's moving in the direction of the target
        # (positive speed = moving forward in zodiac)
        if planet_speed > 0:
            # Moving forward - applying if target is ahead (positive diff up to 180)
            return 0 < diff <= 180
        else:
            # Retrograde - applying if target is behind (negative diff)
            return -180 <= diff < 0

    def get_metadata(self) -> dict[str, Any]:
        """
        Get the calculated antiscia conjunction data.

        Returns:
            Dictionary containing:
            - conjunctions: List of AntisciaConjunction objects
            - contra_conjunctions: List of contra-antiscia conjunctions
            - orb: The orb used for calculations
        """
        return {
            "conjunctions": self._conjunctions,
            "contra_conjunctions": self._contra_conjunctions,
            "orb": self.orb,
        }
