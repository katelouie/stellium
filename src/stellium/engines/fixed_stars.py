"""
Fixed Stars calculation engine using Swiss Ephemeris.

This module provides the engine for calculating fixed star positions at any given time.
Swiss Ephemeris handles precession automatically - just pass the Julian Day and it returns
the correct ecliptic longitude for that epoch.

Usage:
    >>> from stellium.engines.fixed_stars import SwissEphemerisFixedStarsEngine
    >>> engine = SwissEphemerisFixedStarsEngine()
    >>> stars = engine.calculate_stars(julian_day=2451545.0)  # All registered stars
    >>> royal_stars = engine.calculate_stars(julian_day, stars=["Regulus", "Aldebaran"])
"""

from typing import Protocol

import swisseph as swe

from stellium.core.models import FixedStarPosition, ObjectType
from stellium.core.registry import FIXED_STARS_REGISTRY, FixedStarInfo
from stellium.data.paths import initialize_ephemeris


def _set_ephemeris_path() -> None:
    """Set the path to Swiss Ephemeris data files (including sefstars.txt)."""
    initialize_ephemeris()


class FixedStarsEngine(Protocol):
    """
    Protocol for fixed star calculation engines.

    Implementations must provide a method to calculate positions for
    fixed stars at a given Julian Day.
    """

    def calculate_stars(
        self,
        julian_day: float,
        stars: list[str] | None = None,
    ) -> list[FixedStarPosition]:
        """
        Calculate positions for specified fixed stars.

        Args:
            julian_day: The Julian Day for calculation
            stars: List of star names to calculate. If None, calculates all
                   stars in FIXED_STARS_REGISTRY.

        Returns:
            List of FixedStarPosition objects with calculated positions
        """
        ...


class SwissEphemerisFixedStarsEngine:
    """
    Swiss Ephemeris implementation of fixed star calculations.

    Uses swe.fixstar_ut() to calculate precise ecliptic positions for fixed stars,
    with automatic precession handling.

    The engine pulls metadata from FIXED_STARS_REGISTRY to enrich the position
    objects with traditional astrological meanings.

    Attributes:
        registry: The fixed star registry to use (defaults to FIXED_STARS_REGISTRY)

    Example:
        >>> engine = SwissEphemerisFixedStarsEngine()
        >>> # Calculate all stars
        >>> all_stars = engine.calculate_stars(julian_day=2451545.0)
        >>> # Calculate specific stars
        >>> royal = engine.calculate_stars(2451545.0, stars=["Regulus", "Aldebaran"])
        >>> print(f"{royal[0].name}: {royal[0].sign_position}")
        Regulus: 29°50' Leo
    """

    def __init__(self, registry: dict[str, FixedStarInfo] | None = None):
        """
        Initialize the fixed stars engine.

        Args:
            registry: Optional custom registry. Defaults to FIXED_STARS_REGISTRY.
        """
        # Ensure ephemeris path is set for sefstars.txt
        _set_ephemeris_path()
        self.registry = registry if registry is not None else FIXED_STARS_REGISTRY

    def calculate_stars(
        self,
        julian_day: float,
        stars: list[str] | None = None,
    ) -> list[FixedStarPosition]:
        """
        Calculate positions for specified fixed stars.

        Args:
            julian_day: The Julian Day for calculation. Swiss Ephemeris handles
                       precession automatically based on this value.
            stars: List of star names to calculate. If None, calculates all stars
                   in the registry.

        Returns:
            List of FixedStarPosition objects with calculated ecliptic positions
            and registry metadata.

        Raises:
            ValueError: If a requested star is not in the registry
        """
        if stars is None:
            stars = list(self.registry.keys())

        results: list[FixedStarPosition] = []

        for star_name in stars:
            star_info = self.registry.get(star_name)
            if star_info is None:
                raise ValueError(
                    f"Star '{star_name}' not found in registry. "
                    f"Available stars: {list(self.registry.keys())}"
                )

            position = self._calculate_single_star(julian_day, star_info)
            if position is not None:
                results.append(position)

        return results

    def calculate_royal_stars(
        self,
        julian_day: float,
    ) -> list[FixedStarPosition]:
        """
        Calculate positions for the four Royal Stars of Persia.

        A convenience method for getting just the most important stars:
        Aldebaran, Regulus, Antares, and Fomalhaut.

        Args:
            julian_day: The Julian Day for calculation

        Returns:
            List of FixedStarPosition objects for the four royal stars
        """
        royal_names = [name for name, info in self.registry.items() if info.is_royal]
        return self.calculate_stars(julian_day, stars=royal_names)

    def calculate_stars_by_tier(
        self,
        julian_day: float,
        tier: int,
    ) -> list[FixedStarPosition]:
        """
        Calculate positions for all stars of a specific tier.

        Args:
            julian_day: The Julian Day for calculation
            tier: The tier level (1=Royal, 2=Major, 3=Extended)

        Returns:
            List of FixedStarPosition objects for stars of the specified tier
        """
        tier_names = [name for name, info in self.registry.items() if info.tier == tier]
        return self.calculate_stars(julian_day, stars=tier_names)

    def _calculate_single_star(
        self,
        julian_day: float,
        star_info: FixedStarInfo,
    ) -> FixedStarPosition | None:
        """
        Calculate position for a single fixed star.

        Args:
            julian_day: The Julian Day for calculation
            star_info: The star's registry metadata

        Returns:
            FixedStarPosition with calculated coordinates, or None if calculation fails
        """
        try:
            # swe.fixstar_ut returns:
            # ((lon, lat, dist, speed_lon, speed_lat, speed_dist), star_name, retflag)
            result = swe.fixstar_ut(star_info.swe_name, julian_day)

            # Unpack the position tuple
            position_data = result[0]
            longitude = position_data[0]
            latitude = position_data[1]
            distance = position_data[2]
            speed_lon = position_data[3]
            speed_lat = position_data[4]
            speed_dist = position_data[5]

            return FixedStarPosition(
                # CelestialPosition fields
                name=star_info.name,
                object_type=ObjectType.FIXED_STAR,
                longitude=longitude,
                latitude=latitude,
                distance=distance,
                speed_longitude=speed_lon,
                speed_latitude=speed_lat,
                speed_distance=speed_dist,
                # FixedStarPosition-specific fields
                swe_name=star_info.swe_name,
                constellation=star_info.constellation,
                bayer=star_info.bayer,
                tier=star_info.tier,
                is_royal=star_info.is_royal,
                magnitude=star_info.magnitude,
                nature=star_info.nature,
                keywords=star_info.keywords,
            )

        except Exception as e:
            # Swiss Ephemeris raises various exceptions for unknown stars
            # Log and return None rather than crashing
            import warnings

            warnings.warn(
                f"Failed to calculate position for star '{star_info.name}': {e}",
                stacklevel=2,
            )
            return None

    def get_magnitude(self, star_name: str) -> float | None:
        """
        Get the apparent magnitude of a star.

        This uses the registry value rather than calling swe.fixstar_mag()
        since we've already populated magnitude in FixedStarInfo.

        Args:
            star_name: Name of the star

        Returns:
            Apparent magnitude (lower = brighter), or None if not found
        """
        star_info = self.registry.get(star_name)
        if star_info is None:
            return None
        return star_info.magnitude
