"""Ayanamsa (sidereal offset) definitions and registry for Stellium.

This module provides the ZodiacType enum and a registry of ayanamsa systems
used in sidereal astrology. Each ayanamsa represents a different calculation
method for determining the offset between the tropical and sidereal zodiacs.
"""

from dataclasses import dataclass
from enum import Enum

import swisseph as swe


class ZodiacType(Enum):
    """Type of zodiac system used for calculations.

    TROPICAL: Based on the seasons (0° Aries = March equinox)
    SIDEREAL: Based on fixed star positions (varies by ayanamsa)
    """

    TROPICAL = "tropical"
    SIDEREAL = "sidereal"


@dataclass(frozen=True)
class AyanamsaInfo:
    """Information about a specific ayanamsa system.

    Attributes:
        name: Human-readable name of the ayanamsa
        swe_constant: Swiss Ephemeris constant for this ayanamsa
        description: Brief description of the system
        tradition: Tradition this ayanamsa belongs to (vedic, western_sidereal, etc.)
    """

    name: str
    swe_constant: int
    description: str
    tradition: str


# Registry of supported ayanamsa systems
# Key is lowercase name with underscores (for lookup)
AYANAMSA_REGISTRY: dict[str, AyanamsaInfo] = {
    "lahiri": AyanamsaInfo(
        name="Lahiri",
        swe_constant=swe.SIDM_LAHIRI,
        description="Indian government standard, Chitrapaksha ayanamsa",
        tradition="vedic",
    ),
    "fagan_bradley": AyanamsaInfo(
        name="Fagan-Bradley",
        swe_constant=swe.SIDM_FAGAN_BRADLEY,
        description="Primary Western sidereal ayanamsa",
        tradition="western_sidereal",
    ),
    "raman": AyanamsaInfo(
        name="Raman",
        swe_constant=swe.SIDM_RAMAN,
        description="B.V. Raman's ayanamsa, popular in South India",
        tradition="vedic",
    ),
    "krishnamurti": AyanamsaInfo(
        name="Krishnamurti",
        swe_constant=swe.SIDM_KRISHNAMURTI,
        description="Used in KP (Krishnamurti Paddhati) system",
        tradition="vedic",
    ),
    "yukteshwar": AyanamsaInfo(
        name="Yukteshwar",
        swe_constant=swe.SIDM_YUKTESHWAR,
        description="Sri Yukteshwar's ayanamsa from The Holy Science",
        tradition="vedic",
    ),
    "jn_bhasin": AyanamsaInfo(
        name="J.N. Bhasin",
        swe_constant=swe.SIDM_JN_BHASIN,
        description="J.N. Bhasin's ayanamsa, North Indian variant",
        tradition="vedic",
    ),
    "true_citra": AyanamsaInfo(
        name="True Chitrapaksha",
        swe_constant=swe.SIDM_TRUE_CITRA,
        description="Spica (Chitra) at exactly 0° Libra",
        tradition="vedic",
    ),
    "true_revati": AyanamsaInfo(
        name="True Revati",
        swe_constant=swe.SIDM_TRUE_REVATI,
        description="Revati at exactly 0° Aries",
        tradition="vedic",
    ),
    "deluce": AyanamsaInfo(
        name="De Luce",
        swe_constant=swe.SIDM_DELUCE,
        description="De Luce's Western sidereal ayanamsa",
        tradition="western_sidereal",
    ),
}


def get_ayanamsa(name: str) -> AyanamsaInfo:
    """Get ayanamsa information by name.

    Args:
        name: Name of the ayanamsa (case-insensitive, accepts spaces/hyphens)

    Returns:
        AyanamsaInfo for the requested ayanamsa

    Raises:
        ValueError: If ayanamsa name is not recognized

    Examples:
        >>> info = get_ayanamsa("lahiri")
        >>> info.name
        'Lahiri'
        >>> info = get_ayanamsa("Fagan-Bradley")  # Case insensitive, hyphen ok
        >>> info.tradition
        'western_sidereal'
    """
    # Normalize name to lowercase with underscores
    key = name.lower().replace("-", "_").replace(" ", "_")

    if key not in AYANAMSA_REGISTRY:
        available = ", ".join(sorted(AYANAMSA_REGISTRY.keys()))
        raise ValueError(f"Unknown ayanamsa '{name}'. Available options: {available}")

    return AYANAMSA_REGISTRY[key]


def get_ayanamsa_value(julian_day: float, ayanamsa: str) -> float:
    """Calculate the ayanamsa offset value for a specific date.

    The ayanamsa value represents the difference in degrees between the
    tropical and sidereal zodiacs at a given point in time.

    Args:
        julian_day: Julian day number for the calculation
        ayanamsa: Name of the ayanamsa system to use

    Returns:
        Ayanamsa offset in degrees

    Example:
        >>> from stellium.utils.time import datetime_to_julian_day
        >>> from datetime import datetime
        >>> jd = datetime_to_julian_day(datetime(2000, 1, 1, 12, 0))
        >>> offset = get_ayanamsa_value(jd, "lahiri")
        >>> print(f"Lahiri ayanamsa in 2000: {offset:.2f}°")
        Lahiri ayanamsa in 2000: 23.85°
    """
    ayanamsa_info = get_ayanamsa(ayanamsa)
    swe.set_sid_mode(ayanamsa_info.swe_constant)
    return swe.get_ayanamsa_ut(julian_day)


def list_ayanamsas() -> list[str]:
    """Get a list of all available ayanamsa names.

    Returns:
        Sorted list of ayanamsa names (registry keys)

    Example:
        >>> available = list_ayanamsas()
        >>> "lahiri" in available
        True
        >>> "fagan_bradley" in available
        True
    """
    return sorted(AYANAMSA_REGISTRY.keys())
