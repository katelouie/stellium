"""
Fixed Stars component for chart calculations.

This component calculates fixed star positions and integrates them into the chart.
Stars are calculated for the chart's Julian Day, with Swiss Ephemeris handling
precession automatically.

Usage:
    >>> from stellium import ChartBuilder
    >>> from stellium.components import FixedStarsComponent
    >>>
    >>> # All stars
    >>> chart = (ChartBuilder.from_native(native)
    ...     .add_component(FixedStarsComponent())
    ...     .calculate())
    >>>
    >>> # Royal stars only
    >>> chart = (ChartBuilder.from_native(native)
    ...     .add_component(FixedStarsComponent(tier=1))
    ...     .calculate())
    >>>
    >>> # Specific stars
    >>> chart = (ChartBuilder.from_native(native)
    ...     .add_component(FixedStarsComponent(stars=["Regulus", "Algol"]))
    ...     .calculate())
"""

from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    FixedStarPosition,
    HouseCusps,
)
from stellium.engines.fixed_stars import SwissEphemerisFixedStarsEngine


class FixedStarsComponent:
    """
    Component that calculates fixed star positions for a chart.

    This component uses SwissEphemerisFixedStarsEngine to calculate precise
    positions for fixed stars and returns them as FixedStarPosition objects.

    Stars can be filtered by:
    - Specific star names
    - Tier (1=Royal, 2=Major, 3=Extended)
    - Royal stars only

    The calculated positions include all metadata from FIXED_STARS_REGISTRY,
    including traditional planetary nature, keywords, and constellation.

    Attributes:
        stars: List of specific star names to calculate (None = use tier/royal filters)
        tier: Tier level to calculate (None = all tiers)
        royal_only: If True, calculate only the four Royal Stars

    Example:
        >>> # Add all stars in registry
        >>> comp = FixedStarsComponent()
        >>>
        >>> # Add only Royal stars (Aldebaran, Regulus, Antares, Fomalhaut)
        >>> comp = FixedStarsComponent(royal_only=True)
        >>>
        >>> # Add only tier 1 and 2 stars
        >>> comp = FixedStarsComponent(tier=2, include_higher_tiers=True)
        >>>
        >>> # Add specific stars
        >>> comp = FixedStarsComponent(stars=["Sirius", "Algol", "Spica"])
    """

    def __init__(
        self,
        stars: list[str] | None = None,
        tier: int | None = None,
        royal_only: bool = False,
        include_higher_tiers: bool = False,
    ):
        """
        Initialize the fixed stars component.

        Args:
            stars: Specific star names to calculate. If provided, overrides
                   tier and royal_only settings.
            tier: Tier level to calculate (1=Royal, 2=Major, 3=Extended).
                  If include_higher_tiers=False, only this tier is calculated.
                  If include_higher_tiers=True, this tier and all higher (lower number)
                  tiers are calculated.
            royal_only: If True, calculate only the four Royal Stars (tier 1).
                        Equivalent to tier=1.
            include_higher_tiers: If True and tier is set, include all stars
                                  with tier <= the specified tier.
        """
        self.stars = stars
        self.tier = tier
        self.royal_only = royal_only
        self.include_higher_tiers = include_higher_tiers
        self._engine = SwissEphemerisFixedStarsEngine()

    @property
    def component_name(self) -> str:
        """Name of this component."""
        return "Fixed Stars"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate fixed star positions for the chart.

        Args:
            datetime: Chart datetime (used to get Julian Day)
            location: Chart location (unused for fixed stars, required by protocol)
            positions: Already-calculated positions (unused, required by protocol)
            house_systems_map: House systems map (unused, required by protocol)
            house_placements_map: House placements (unused, required by protocol)

        Returns:
            List of FixedStarPosition objects for the requested stars
        """
        julian_day = datetime.julian_day

        # Determine which stars to calculate
        if self.stars is not None:
            # Explicit list overrides everything
            return self._engine.calculate_stars(julian_day, stars=self.stars)

        if self.royal_only:
            # Royal stars only
            return self._engine.calculate_royal_stars(julian_day)

        if self.tier is not None:
            if self.include_higher_tiers:
                # Include this tier and all higher priority tiers (lower numbers)
                results: list[FixedStarPosition] = []
                for t in range(1, self.tier + 1):
                    results.extend(self._engine.calculate_stars_by_tier(julian_day, t))
                return results
            else:
                # Just this tier
                return self._engine.calculate_stars_by_tier(julian_day, self.tier)

        # Default: all stars
        return self._engine.calculate_stars(julian_day)
