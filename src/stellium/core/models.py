"""
Immutable data models for astrological calculations.

These are pure data containers - no business logic, no calculations.

They represent the OUTPUT of calculations, not the process.
"""

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


def longitude_to_sign_and_degree(longitude: float) -> tuple[str, float]:
    """Convert position longitude to a sign and sign degree.

    Args:
        longitude: Position longitude (0-360)

    Returns:
        tuple of (sign_name, sign_degree)
    """
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    sign_name = signs[int(longitude // 30)]
    sign_degree = longitude % 30

    return sign_name, sign_degree


class ObjectType(Enum):
    """Type of astrological object."""

    PLANET = "planet"
    ANGLE = "angle"
    ASTEROID = "asteroid"
    POINT = "point"
    NODE = "node"
    ARABIC_PART = "arabic_part"
    MIDPOINT = "midpoint"
    FIXED_STAR = "fixed_star"


class ComparisonType(Enum):
    """Type of chart comparison."""

    SYNASTRY = "synastry"
    TRANSIT = "transit"
    PROGRESSION = "progression"


@dataclass(frozen=True)
class ChartLocation:
    """Immutable location data for chart calculation."""

    latitude: float
    longitude: float
    name: str = ""
    timezone: str = ""

    def __post_init__(self) -> None:
        """Validate coordinates"""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalud latitude: {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}")


@dataclass(frozen=True)
class ChartDateTime:
    """Immutable datetime data for chart calculation."""

    utc_datetime: dt.datetime
    julian_day: float
    local_datetime: dt.datetime | None = None

    def __post_init__(self) -> None:
        """Ensure datetime is timezone-aware."""
        if self.utc_datetime.tzinfo is None:
            raise ValueError("DateTime must be timezone-aware")


@dataclass(frozen=True)
class CelestialPosition:
    """Immutable representation of a celestial object's position.

    This is the OUTPUT of ephemeris calculations.
    """

    # Identity
    name: str
    object_type: ObjectType

    # Ecliptic coordinates (standard zodiac system)
    longitude: float  # 0-360 degrees
    latitude: float = 0.0  # Ecliptic latitude (distance from ecliptic plane)
    distance: float = 0.0

    # Velocity data
    speed_longitude: float = 0.0
    speed_latitude: float = 0.0
    speed_distance: float = 0.0

    # Equatorial coordinates (for declination aspects)
    declination: float | None = None  # Distance from celestial equator (-90 to +90)
    right_ascension: float | None = None  # Like longitude but measured from vernal equinox

    # Derived data (calculated from longitude)
    sign: str = field(init=False)
    sign_degree: float = field(init=False)

    # Optional metadata
    is_retrograde: bool = field(init=False)

    # Phase data
    phase: "PhaseData | None" = None

    def __post_init__(self) -> None:
        """Calculate derived fields."""
        # Use object.__setattr__ because the dataclass is frozen!
        sign, sign_degree = longitude_to_sign_and_degree(self.longitude)
        object.__setattr__(self, "sign", sign)
        object.__setattr__(self, "sign_degree", sign_degree)
        object.__setattr__(self, "is_retrograde", self.speed_longitude < 0)

    @property
    def sign_position(self) -> str:
        """Human-readable sign position (e.g. 15°23' Aries)"""
        degrees = int(self.sign_degree)
        minutes = int((self.sign_degree % 1) * 60)
        return f"{degrees}°{minutes:02d}' {self.sign}"

    @property
    def is_out_of_bounds(self) -> bool:
        """Planet is beyond the Sun's maximum declination (~23°27').

        Out-of-bounds planets are considered to have extra intensity,
        unpredictability, or unconventional expression in their significations.

        The Sun's declination varies between approximately +23.4367° and -23.4367°
        (the Tropic of Cancer and Tropic of Capricorn). When a planet exceeds
        these bounds, it's "out of bounds."

        Moon, Mercury, Mars, and Venus can go out of bounds.
        Jupiter, Saturn, and outer planets rarely or never do.
        """
        if self.declination is None:
            return False
        # Maximum solar declination (obliquity of ecliptic)
        return abs(self.declination) > 23.4367

    @property
    def declination_direction(self) -> str:
        """Direction of declination: 'north', 'south', or 'none'."""
        if self.declination is None:
            return "none"
        return "north" if self.declination >= 0 else "south"

    def __str__(self) -> str:
        retro = " ℞" if self.is_retrograde else ""
        return f"{self.name}: {self.sign_position} ({self.longitude:.2f}°){retro}"


@dataclass(frozen=True)
class MidpointPosition(CelestialPosition):
    """
    Specialized position type for midpoints between two celestial objects.

    A midpoint represents the halfway point between two celestial objects,
    either along the shorter arc (direct) or the longer arc (indirect).

    Attributes:
        object1: First component object
        object2: Second component object
        is_indirect: True if this is the indirect (opposite) midpoint

    Example:
        # Sun at 10° Aries, Moon at 20° Aries
        # Direct midpoint: 15° Aries
        # Indirect midpoint: 15° Libra (opposite)

        midpoint = MidpointPosition(
            name="Midpoint:Sun/Moon",
            object_type=ObjectType.MIDPOINT,
            longitude=15.0,  # 15° Aries
            object1=sun_position,
            object2=moon_position,
            is_indirect=False,
        )
    """

    # Use field with default_factory=None pattern to handle required fields after optional ones
    object1: CelestialPosition = field(default=None)  # type: ignore
    object2: CelestialPosition = field(default=None)  # type: ignore
    is_indirect: bool = False

    def __post_init__(self) -> None:
        """Validate that object1 and object2 are provided."""
        # Call parent __post_init__ first
        super().__post_init__()

        # Validate required fields
        if self.object1 is None:
            raise ValueError("object1 is required for MidpointPosition")
        if self.object2 is None:
            raise ValueError("object2 is required for MidpointPosition")


@dataclass(frozen=True)
class FixedStarPosition(CelestialPosition):
    """
    Position of a fixed star at a specific time.

    Extends CelestialPosition with fixed star-specific metadata from the registry,
    including traditional astrological properties like planetary nature and keywords.

    Fixed stars move very slowly due to precession (~1° per 72 years), so their
    positions change slightly between charts. Swiss Ephemeris handles precession
    automatically based on the Julian Day.

    Attributes:
        swe_name: Swiss Ephemeris lookup name
        constellation: Traditional constellation (e.g., "Leo")
        bayer: Bayer designation (e.g., "Alpha Leonis")
        tier: Star tier (1=Royal, 2=Major, 3=Extended)
        is_royal: Whether this is one of the four Royal Stars of Persia
        magnitude: Apparent visual magnitude (lower = brighter)
        nature: Traditional planetary nature (e.g., "Mars/Jupiter")
        keywords: Interpretive keywords for the star

    Example:
        regulus = FixedStarPosition(
            name="Regulus",
            object_type=ObjectType.FIXED_STAR,
            longitude=150.12,  # ~0° Virgo (moves slowly through precession)
            swe_name="Regulus",
            constellation="Leo",
            tier=1,
            is_royal=True,
            magnitude=1.35,
            nature="Mars/Jupiter",
            keywords=("royalty", "success", "fame"),
        )
    """

    # Fixed star-specific fields (with defaults to satisfy dataclass inheritance)
    swe_name: str = ""
    constellation: str = ""
    bayer: str = ""
    tier: int = 2  # 1=Royal, 2=Major, 3=Extended
    is_royal: bool = False
    magnitude: float = 0.0
    nature: str = ""
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        tier_label = {1: "Royal", 2: "Major", 3: "Extended"}.get(self.tier, "")
        return f"★ {self.name}: {self.sign_position} ({tier_label}, mag {self.magnitude:.1f})"


@dataclass(frozen=True)
class HouseCusps:
    """Immutable house cusp data."""

    system: str
    cusps: tuple[float, ...]  # 12 cusps, 0-360 degrees

    def __post_init__(self) -> None:
        """Validate cusp count."""
        if len(self.cusps) != 12:
            raise ValueError(f"Expected 12 cusps, got {len(self.cusps)}")

        signs = []
        sign_degrees = []
        houses = []

        for i, cusp in enumerate(self.cusps):
            sign, sign_degree = longitude_to_sign_and_degree(cusp)
            houses.append(i + 1)
            signs.append(sign)
            sign_degrees.append(sign_degree)

        # Frozen
        object.__setattr__(self, "houses", houses)
        object.__setattr__(self, "signs", signs)
        object.__setattr__(self, "sign_degrees", sign_degrees)

    def _sign_position(self, sign, sign_degree) -> str:
        """Human-readable sign position (e.g. 15°23' Aries)"""
        degrees = int(sign_degree)
        minutes = int((sign_degree % 1) * 60)
        return f"{degrees}°{minutes:02d}' {sign}"

    def get_cusp(self, house_number: int) -> float:
        """Get cusp for a specific house (1-12)"""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        return self.cusps[house_number - 1]

    def get_sign(self, house_number: int) -> str:
        """Get sign name for a specific house (1-12)"""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        return self.signs[house_number - 1]

    def get_sign_degree(self, house_number: int) -> str:
        """Get sign name for a specific house (1-12)"""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        return self.sign_degrees[house_number - 1]

    def get_description(self, house_number: int) -> str:
        """Get human-readable cusp description for a specific house."""
        if not 1 <= house_number <= 12:
            raise ValueError(f"House number must be 1-12, got {house_number}")
        sign_position = self._sign_position(
            self.signs[house_number - 1], self.sign_degrees[house_number - 1]
        )
        house_string = f"House {house_number}: {sign_position} ({self.cusps[house_number - 1]:.2f}°)"
        return house_string

    def __str__(self) -> str:
        strings = []
        for i in range(len(self.cusps)):
            strings.append(self.get_description(i + 1))
        return "\n".join(strings)


@dataclass(frozen=True)
class Aspect:
    """Immutable aspect between two objects."""

    object1: CelestialPosition
    object2: CelestialPosition
    aspect_name: str
    aspect_degree: int  # 0, 60, 90, 120, 180, etc.
    orb: float  # Actual orb in degrees
    is_applying: bool | None = None

    @property
    def description(self) -> str:
        """Human-readable aspect description."""
        if self.is_applying is None:
            applying = ""
        elif self.is_applying:
            applying = " (applying)"
        else:  # is separating
            applying = " (separating)"

        return f"{self.object1.name} {self.aspect_name} {self.object2.name} (orb: {self.orb:.2f}°){applying}"

    def __str__(self) -> str:
        return self.description


@dataclass(frozen=True)
class AspectPattern:
    """
    Represents a detected aspect pattern in a chart.
    (e.g., Grand Trine, T-Square, Yod, etc.)
    """

    name: str
    planets: list[CelestialPosition]
    aspects: list[Aspect]
    element: str | None = None  # eg Fire
    quality: str | None = None  # eg Cardinal

    def __str__(self) -> str:
        planet_names = ", ".join([p.name for p in self.planets])
        return f"{self.name} ({planet_names})"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage/JSON."""
        return {
            "name": self.name,
            "planets": [p.name for p in self.planets],
            "aspects": [a.description for a in self.aspects],
            "element": self.element,
            "quality": self.quality,
            "focal_planet": self.focal_planet,
        }

    @property
    def focal_planet(self) -> CelestialPosition | None:
        """Get the focal/apex planet for patterns that have one."""
        if self.name in ("T-Square", "Yod"):
            return self.planets[2]  # Last planet is apex
        return None


@dataclass(frozen=True)
class CalculatedChart:
    """
    Complete calculated chart - the final output.

    This is what a ChartBuilder returns. It's immutable and contains everything
    you need to analyze or visualize the chart.
    """

    # Input parameters
    datetime: ChartDateTime
    location: ChartLocation

    # Calculated data
    positions: tuple[CelestialPosition, ...]
    house_systems: dict[str, HouseCusps] = field(default_factory=dict)
    # chart.placements["Placidus"]["Sun"] -> 10
    house_placements: dict[str, dict[str, int]] = field(default_factory=dict)
    aspects: tuple[Aspect, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # Zodiac system metadata
    zodiac_type: Any = None  # ZodiacType | None (avoiding circular import)
    ayanamsa: str | None = None  # Only set if zodiac_type is SIDEREAL
    ayanamsa_value: float | None = None  # Actual ayanamsa offset in degrees at chart time

    # Metadata
    calculation_timestamp: dt.datetime = field(
        default_factory=lambda: dt.datetime.now(dt.UTC)
    )

    def _get_default_house_system(self) -> str:
        """
        Get the default house system to use.

        Returns the first (and typically only) house system in the chart.
        Raises ValueError if no house systems are available.
        """
        if not self.house_systems:
            raise ValueError(
                "No house systems calculated. Add a house system engine when building the chart."
            )

        # Get the first system (dict maintains insertion order in Python 3.7+)
        return next(iter(self.house_systems.keys()))

    @property
    def default_house_system(self) -> str:
        return self._get_default_house_system()

    def get_house(self, object_name: str, system_name: str | None = None) -> int | None:
        """
        Helper method to get the house number for a specific object in a specific system.
        """
        if system_name is None:
            system_name = self.default_house_system
        return self.house_placements.get(system_name, {}).get(object_name)

    def get_houses(self, system_name: str | None = None) -> HouseCusps:
        """Get all cusps for a specific system (or default system)."""
        if system_name is None:
            system_name = self.default_house_system

        return self.house_systems[system_name]

    def get_object(self, name: str) -> CelestialPosition | None:
        """Get a celestial object by name."""
        for obj in self.positions:
            if obj.name == name:
                return obj

        return None

    def get_planets(self) -> list[CelestialPosition]:
        """Get all planetary objects."""
        return [p for p in self.positions if p.object_type == ObjectType.PLANET]

    def get_angles(self) -> list[CelestialPosition]:
        """Get all chart angles."""
        return [p for p in self.positions if p.object_type == ObjectType.ANGLE]

    def get_points(self) -> list[CelestialPosition]:
        """Get all calculated points (Vertex, Lilith, etc.)."""
        return [p for p in self.positions if p.object_type == ObjectType.POINT]

    def get_nodes(self) -> list[CelestialPosition]:
        """Get all nodes (True Node, South Node, etc.)."""
        return [p for p in self.positions if p.object_type == ObjectType.NODE]

    def get_dignities(self, system: str = "traditional") -> dict[str, Any]:
        """
        Get essential dignity calculations.

        Args:
            system: "traditional" or "modern"

        Returns:
            Dictionary of planet dignities, or empty dict if not calculated
        """
        dignity_data = self.metadata.get("dignities", {})
        planet_dignities = dignity_data.get("planet_dignities", {})

        result = {}
        for planet_name, data in planet_dignities.items():
            if system in data:
                result[planet_name] = data[system]

        return result

    def get_planet_dignity(
        self, planet_name: str, system: str = "traditional"
    ) -> dict[str, Any] | None:
        """
        Get dignity calculation for a specific planet.

        Args:
            planet_name: Name of the planet (e.g., "Sun", "Moon")
            system: "traditional" or "modern"

        Returns:
            Dignity data for the planet, or None if not found
        """
        dignities = self.get_dignities(system)
        return dignities.get(planet_name)

    def get_mutual_receptions(
        self, system: str = "traditional"
    ) -> list[dict[str, Any]]:
        """
        Get all mutual receptions in the chart.

        Args:
            system: "traditional" or "modern"

        Returns:
            List of mutual reception dictionaries
        """
        dignity_data = self.metadata.get("dignities", {})
        receptions = dignity_data.get("mutual_receptions", {})
        return receptions.get(system, [])

    def get_all_accidental_dignities(self) -> dict[str, Any]:
        """Get all accidental dignities (entire object)."""
        return self.metadata.get("accidental_dignities", {})

    def get_accidental_dignities(self, system: str | None = None) -> dict[str, Any]:
        """
        Get accidental dignity calculations.

        Args:
            system: Specific house system ("Placidus"). If None returns all systems.

        Returns:
            Dictionary of planetary accidental dignities
        """
        all_accidentals = self.metadata.get("accidental_dignities", {})

        if system is None:
            # Use the first house system in the chart
            system = self.default_house_system

        # Return for specific system
        result = {}
        for planet_name, data in all_accidentals.items():
            by_system = data.get("by_system", {})
            universal = data.get("universal", {})

            if system in by_system:
                # Combine system-specific and universal
                system_data = by_system[system].copy()

                # Add universal conditions to this system's conditions
                combined_conditions = system_data.get("conditions", []).copy()
                combined_conditions.extend(universal.get("conditions", []))

                result[planet_name] = {
                    "planet": planet_name,
                    "score": system_data.get("score", 0) + universal.get("score", 0),
                    "house": system_data.get("house"),
                    "conditions": combined_conditions,
                    "system": system,
                }

        return result

    def get_planet_accidental(
        self, planet_name: str, system: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get accidental dignity for a specific planet.

        Args:
            planet_name: Name of the planet
            system: House system (defaults to default house system if None)

        Returns:
            Accidental dignity data, or None if not found
        """
        accidentals = self.get_accidental_dignities(system)
        return accidentals.get(planet_name)

    def get_strongest_planet(
        self, system: str = "traditional"
    ) -> tuple[str, int] | None:
        """
        Find the planet with the highest dignity score (Almuten).

        Args:
            system: "traditional" or "modern"

        Returns:
            Tuple of (planet_name, score) or None if no dignities calculated
        """
        dignities = self.get_dignities(system)

        if not dignities:
            return None

        strongest = max(dignities.items(), key=lambda x: x[1].get("score", 0))

        return strongest[0], strongest[1].get("score", 0)

    def get_planet_total_score(
        self,
        planet_name: str,
        essential_system: str = "traditional",
        accidental_system: str | None = None,
    ) -> dict[str, Any]:
        """
        Get combined essential + accidental dignity score.

        Args:
            planet_name: Name of the planet
            essential_system: "traditional" or "modern"
            accidental_system: House system name (defaults to default system)

        Returns:
            Dict with essential, accidental, and total scores
        """
        essential = self.get_planet_dignity(planet_name, essential_system)
        accidental = self.get_planet_accidental(planet_name, accidental_system)

        essential_score = essential.get("score", 0) if essential else 0
        accidental_score = accidental.get("score", 0) if accidental else 0

        return {
            "planet": planet_name,
            "essential_score": essential_score,
            "essential_system": essential_system,
            "accidental_score": accidental_score,
            "accidental_system": accidental_system or self.default_house_system,
            "total_score": essential_score + accidental_score,
            "interpretation": self._interpret_total_score(
                essential_score + accidental_score
            ),
        }

    def _interpret_total_score(self, total_score: int) -> str:
        """Interpret combined dignity score."""
        if total_score >= 15:
            return "Exceptionally strong - excellent condition"
        elif total_score >= 10:
            return "Very strong - favorable condition"
        elif total_score >= 5:
            return "Strong - good condition"
        elif total_score >= 0:
            return "Moderate - neutral to favorable"
        elif total_score >= -5:
            return "Challenged - some difficulties"
        elif total_score >= -10:
            return "Significantly challenged - considerable difficulties"
        else:
            return "Severely challenged - very difficult condition"

    def sect(self) -> bool | None:
        """
        Check which sect this chart is (day or night) (Sun above the horizon).

        Returns:
            "day" or "night"
        """
        dignity_data = self.metadata.get("dignities", {})
        return dignity_data.get("sect")

    def draw(self, filename: str = "chart.svg") -> "ChartDrawBuilder":
        """
        Start building a chart visualization with fluent API.

        This is a convenience method that creates a ChartDrawBuilder for
        easy, discoverable chart visualization. It provides presets and
        a fluent interface for customization.

        Args:
            filename: Output filename for the SVG

        Returns:
            ChartDrawBuilder instance for chaining

        Example:
            # Simple preset
            chart.draw("my_chart.svg").preset_standard().save()

            # Custom configuration
            chart.draw("custom.svg") \\
                .with_theme("dark") \\
                .with_moon_phase(position="top-left", show_label=True) \\
                .with_chart_info(position="top-right") \\
                .save()
        """
        from stellium.visualization.builder import ChartDrawBuilder

        return ChartDrawBuilder(self).with_filename(filename)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize to dictionary for JSON export.

        This enables web API integration, storage, etc.
        """
        base_dict = {
            "datetime": {
                "utc": self.datetime.utc_datetime.isoformat(),
                "julian_date": self.datetime.julian_day,
            },
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "name": self.location.name,
            },
            "house_systems": {
                system_name: {
                    "cusps": list(house_cusps.cusps),
                    "signs": house_cusps.signs,
                    "sign_degrees": house_cusps.sign_degrees,
                }
                for system_name, house_cusps in self.house_systems.items()
            },
            "default_house_system": self.default_house_system,
            "house_placements": self.house_placements,
            "positions": [
                {
                    "name": p.name,
                    "type": p.object_type.value,
                    "longitude": p.longitude,
                    "latitude": p.latitude,
                    "sign": p.sign,
                    "sign_degree": p.sign_degree,
                    "is_retrograde": p.is_retrograde,
                }
                for p in self.positions
            ],
            "aspects": [
                {
                    "object1": a.object1.name,
                    "object2": a.object2.name,
                    "aspect": a.aspect_name,
                    "orb": a.orb,
                }
                for a in self.aspects
            ],
        }

        # add metadata
        if self.metadata:
            base_dict["metadata"] = {}
            for key, value in self.metadata.items():
                if key == "aspect_patterns":
                    serialized = [ap.to_dict() for ap in value]
                    base_dict["metadata"][key] = serialized
                else:
                    # Dignities or otherwise
                    base_dict["metadata"][key] = value

        return base_dict


@dataclass(frozen=True)
class PhaseData:
    """
    Planetary phase information.

    Contains data about a celestial object's appearance and illumination
    as seen from Earth. Available for Moon, planets, and some asteroids.

    Attributes:
        phase_angle: Angular separation from Sun (0-360°)
            - 0° = conjunction (new moon)
            - 90° = quadrature (quarter moon)
            - 180° = opposition (full moon)
        illuminated_fraction: Fraction of disk that is illuminated (0.0-1.0)
            - 0.0 = completely dark (new)
            - 0.5 = half illuminated (quarter)
            - 1.0 = fully illuminated (full)
        elongation: Elongation of the planet
        apparent_diameter: Angular diameter as seen from Earth (arc seconds)
        apparent_magnitude: Visual brightness magnitude (lower = brighter)
        geocentric_parallax: Parallax angle (radians) - primarily for Moon
    """

    phase_angle: float  # 0-360 degrees
    illuminated_fraction: float  # 0.0 to 1.0
    elongation: float
    apparent_diameter: float  # arc seconds
    apparent_magnitude: float  # visual magnitude
    geocentric_parallax: float = 0.0  # radians (mainly for Moon)

    @property
    def is_waxing(self) -> bool:
        """
        Whether object is waxing (growing in illumination).

        For the Moon: 0-180° = waxing, 180-360° = waning
        """
        return self.phase_angle <= 180.0

    @property
    def phase_name(self) -> str:
        """
        Human-readable phase name (primarily for Moon).

        Returns:
            Phase name like "New", "Waxing Crescent", etc.
        """
        frac = self.illuminated_fraction
        waxing = self.is_waxing

        # Special cases
        if frac < 0.03:
            return "New"
        elif frac > 0.97:
            return "Full"
        elif 0.48 <= frac <= 0.52:
            return "First Quarter" if waxing else "Last Quarter"

        # Crescents and gibbous
        if frac < 0.48:
            return "Waxing Crescent" if waxing else "Waning Crescent"
        else:
            return "Waxing Gibbous" if waxing else "Waning Gibbous"

    def __repr__(self) -> str:
        return (
            f"PhaseData(angle={self.phase_angle:.1f}°, "
            f"illuminated={self.illuminated_fraction:.1%}, "
            f"magnitude={self.apparent_magnitude:.2f})"
        )

    def __str__(self) -> str:
        return f"Phase: {self.phase_name} ({self.illuminated_fraction:.1%} illuminated)"


@dataclass(frozen=True)
class ComparisonAspect(Aspect):
    """Aspect between objects from two different charts.

    This extends the base Aspect model with comparison-specific metadata.
    """

    # Core aspect data
    object1: CelestialPosition  # From chart1 (native/inner)
    object2: CelestialPosition  # From chart2 (partner/transit/outer)
    aspect_name: str
    aspect_degree: int
    orb: float

    # Comparison-specific metadata
    is_applying: bool | None = None
    chart1_to_chart2: bool = True

    # Synastry-specific: which chart's house the aspect "lands in"
    in_chart1_house: int | None = None
    in_chart2_house: int | None = None

    @property
    def description(self) -> str:
        direction = "A→B" if self.chart1_to_chart2 else "A←B"
        applying = (
            " (applying)"
            if self.is_applying
            else " (separating)"
            if self.is_applying is not None
            else ""
        )
        return f"{self.object1.name} {direction} {self.aspect_name} {direction} {self.object2.name} (orb: {self.orb:.2f}°){applying}"


@dataclass(frozen=True)
class HouseOverlay:
    """
    Represents one chart's planets falling in another chart's houses.
    """

    planet_name: str
    planet_owner: Literal["chart1", "chart2"]
    falls_in_house: int  # 1-12
    house_owner: Literal["chart1", "chart2"]
    planet_position: CelestialPosition

    @property
    def description(self) -> str:
        owner_name = "Person A" if self.planet_owner == "chart1" else "Person B"
        house_owner_name = (
            "Person A's" if self.house_owner == "chart1" else "Person B's"
        )
        return f"{owner_name}'s {self.planet_name} in {house_owner_name} house {self.falls_in_house}"


# =============================================================================
# Unknown Birth Time Charts
# =============================================================================


@dataclass(frozen=True)
class MoonRange:
    """
    Moon position range for unknown birth time charts.

    When birth time is unknown, the Moon's position could be anywhere within
    a ~12-14° range (Moon moves about 12-14° per day). This dataclass captures
    the full range to display on the chart.

    Attributes:
        start_longitude: Moon position at 00:00:00 local time
        end_longitude: Moon position at 23:59:59 local time
        noon_longitude: Moon position at 12:00:00 (displayed position)
        start_sign: Zodiac sign at start of day
        end_sign: Zodiac sign at end of day
        crosses_sign_boundary: True if Moon changes sign during the day
    """

    start_longitude: float  # Position at 00:00:00
    end_longitude: float  # Position at 23:59:59
    noon_longitude: float  # Position at 12:00:00 (displayed position)
    start_sign: str
    end_sign: str
    crosses_sign_boundary: bool

    @property
    def arc_size(self) -> float:
        """
        Size of the Moon's arc in degrees.

        Handles wrap-around at 0°/360° Aries point.
        """
        if self.end_longitude < self.start_longitude:
            # Wraps around 0° Aries
            return (360 - self.start_longitude) + self.end_longitude
        return self.end_longitude - self.start_longitude

    @property
    def sign_display(self) -> str:
        """Human-readable sign display for the Moon range."""
        if self.crosses_sign_boundary:
            return f"{self.start_sign} - {self.end_sign}"
        return self.start_sign

    def __str__(self) -> str:
        if self.crosses_sign_boundary:
            return (
                f"Moon: {self.start_sign} {self.start_longitude % 30:.0f}° - "
                f"{self.end_sign} {self.end_longitude % 30:.0f}° "
                f"(arc: {self.arc_size:.1f}°)"
            )
        start_deg = self.start_longitude % 30
        end_deg = self.end_longitude % 30
        return f"Moon: {self.start_sign} {start_deg:.0f}° - {end_deg:.0f}° (arc: {self.arc_size:.1f}°)"


@dataclass(frozen=True)
class UnknownTimeChart(CalculatedChart):
    """
    A natal chart calculated without known birth time.

    Inherits from CalculatedChart for compatibility with all existing code,
    but has some key differences:
    - Houses are empty (no house cusps without birth time)
    - Angles are not calculated (no Asc/MC/Dsc/IC)
    - Moon is shown as a range rather than single position
    - Planetary positions are calculated for noon

    The chart can still be:
    - Visualized (without houses, with moon arc)
    - Exported to JSON
    - Used for aspect calculations (using noon Moon)
    - Used for dignity calculations (planets only)

    Attributes:
        moon_range: MoonRange showing the Moon's possible positions throughout the day
    """

    moon_range: MoonRange = field(default=None)  # type: ignore

    def __post_init__(self) -> None:
        """Validate that moon_range is provided."""
        if self.moon_range is None:
            raise ValueError("moon_range is required for UnknownTimeChart")

    @property
    def is_time_unknown(self) -> bool:
        """Always True for this chart type."""
        return True

    def get_house(self, object_name: str, system_name: str | None = None) -> None:
        """Houses are not available for unknown time charts."""
        return None

    def get_houses(self, system_name: str | None = None) -> None:
        """Houses are not available for unknown time charts."""
        return None

    def get_angles(self) -> list[CelestialPosition]:
        """Angles are not available for unknown time charts."""
        return []

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary, including moon_range."""
        base_dict = super().to_dict()

        # Add moon range info
        base_dict["time_unknown"] = True
        base_dict["moon_range"] = {
            "start_longitude": self.moon_range.start_longitude,
            "end_longitude": self.moon_range.end_longitude,
            "noon_longitude": self.moon_range.noon_longitude,
            "start_sign": self.moon_range.start_sign,
            "end_sign": self.moon_range.end_sign,
            "crosses_sign_boundary": self.moon_range.crosses_sign_boundary,
            "arc_size": self.moon_range.arc_size,
        }

        return base_dict
