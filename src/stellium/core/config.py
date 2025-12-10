"""Configuration models for chart calculation."""

from dataclasses import dataclass, field

from stellium.core.ayanamsa import ZodiacType


@dataclass
class AspectConfig:
    """Configuration for aspect calculations.

    Will be passed directly into the AspectEngine.
    """

    # Which aspects to calculate (by name - angles are looked up from registry)
    aspects: list[str] = field(
        default_factory=lambda: [
            "Conjunction",
            "Sextile",
            "Square",
            "Trine",
            "Opposition",
        ]
    )

    # Which object types to include in aspect calculations
    # (The AspectEngine will use this to filter pairs)
    include_angles: bool = True
    include_nodes: bool = True
    include_asteroids: bool = True


@dataclass
class CalculationConfig:
    """Overall configuration for chart calculations.

    Passed to the ChartBuilder.
    """

    # Which objects to calculate
    include_planets: list[str] = field(
        default_factory=lambda: [
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
        ]
    )
    include_nodes: bool = True
    include_chiron: bool = True
    include_points: list[str] = field(
        default_factory=lambda: ["Mean Apogee"]  # Black Moon Lilith by default
    )
    include_asteroids: list[str] = field(default_factory=list)  # Default empty

    # Zodiac system configuration
    zodiac_type: ZodiacType = ZodiacType.TROPICAL
    ayanamsa: str | None = None  # Only used if zodiac_type is SIDEREAL

    # Coordinate system
    heliocentric: bool = False  # Sun-centered instead of Earth-centered

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Set default ayanamsa if sidereal but none specified
        if self.zodiac_type == ZodiacType.SIDEREAL and self.ayanamsa is None:
            object.__setattr__(self, "ayanamsa", "lahiri")  # Default to Lahiri

    @classmethod
    def minimal(cls) -> "CalculationConfig":
        """Minimal calculation - planets only."""
        return cls(
            include_nodes=False,
            include_chiron=False,
            include_points=[],
            include_asteroids=[],
        )

    @classmethod
    def comprehensive(cls) -> "CalculationConfig":
        """Comprehensive calculation -- a well-rounded set."""
        return cls(
            include_nodes=True,
            include_chiron=True,
            include_points=["Mean Apogee", "True Apogee"],  # Both Liliths
            include_asteroids=["Chiron", "Pholus", "Ceres", "Pallas", "Juno", "Vesta"],
        )
