"""
Aspect calculation engines.

These engines are responsible for finding angular relationships (aspects)
between celestial objects. They follow the `AspectEngine` protocol.
"""

from itertools import combinations

from stellium.core.config import AspectConfig
from stellium.core.models import Aspect, CelestialPosition, ObjectType
from stellium.core.protocols import OrbEngine
from stellium.core.registry import get_aspect_by_alias, get_aspect_info

# --- Helper Functions (Shared Logic) ---


def _are_axis_pair(obj1: CelestialPosition, obj2: CelestialPosition) -> bool:
    """
    Check if two objects are an axis pair that shouldn't aspect each other.

    Axis pairs:
    - ASC/DSC (Ascendant-Descendant axis)
    - MC/IC (Midheaven-Imum Coeli axis)
    - True Node/South Node (Nodal axis)

    These pairs are always in exact opposition by definition, so calculating
    aspects between them is redundant and clutters the aspect list.

    Returns:
        True if the pair is an axis pair that should be excluded
    """
    # Define axis pairs (order doesn't matter)
    axis_pairs = {
        frozenset(["ASC", "DSC"]),
        frozenset(["MC", "IC"]),
        frozenset(["True Node", "South Node"]),
    }

    # Check if this pair is an axis pair
    pair = frozenset([obj1.name, obj2.name])
    return pair in axis_pairs


def _angular_distance(long1: float, long2: float) -> float:
    """Calculate shortest angular distance between two longitudes."""
    diff = abs(long1 - long2)
    if diff > 180:
        diff = 360 - diff
    return diff


def _is_applying(
    obj1: CelestialPosition,
    obj2: CelestialPosition,
    aspect_angle: float,
    current_distance: float,
) -> bool | None:
    """
    Determine if aspect is applying or separating.
    An aspect is "applying" if the planets are moving *toward*
    the exact aspect angle.

    Returns:
        True if applying, False if separating, None if speed is unknown.
    """
    # Need speed data for both objects
    if obj1.speed_longitude == 0 or obj2.speed_longitude == 0:
        return None

    # Use a 1-minute interval.
    # This is (1 day / 24 hours / 60 minutes)
    interval_fraction = 1.0 / (24.0 * 60.0)

    # Calculate where they'll be in one minute
    future_long1 = (obj1.longitude + (obj1.speed_longitude * interval_fraction)) % 360
    future_long2 = (obj2.longitude + (obj2.speed_longitude * interval_fraction)) % 360
    future_distance = _angular_distance(future_long1, future_long2)

    # Calculate the orb (distance from exactness) now and in one minute
    current_orb = abs(current_distance - aspect_angle)
    future_orb = abs(future_distance - aspect_angle)

    # Applying = the future orb is smaller than the current orb
    # This check is now safe from the "crossover" bug because
    # the interval is too small to cross and return an equal
    # absolute value.
    return future_orb < current_orb


class ModernAspectEngine:
    """
    Calculates standard aspects (conjunction, square, trine, etc.)
    based on a provided AspectConfig.
    """

    def __init__(self, config: AspectConfig | None = None):
        """
        Initialize the engine.

        Args:
            config: An AspectConfig object defining which aspect angles
                    and object types to use. If None, a default
                    AspectConfig is created.
        """
        self._config = config or AspectConfig()

    def calculate_aspects(
        self, positions: list[CelestialPosition], orb_engine: OrbEngine
    ) -> list[Aspect]:
        """
        Calculate aspects based on the engine's config and the provided orb engine.

        Args:
            positions: The list of CelestialPosition objects to check.
            orb_engine: The OrbEngine that will provide the orb allowance
                        for each potential aspect.

        Returns:
            A list of found Aspect objects.
        """
        aspects = []

        # 1. Filter the list of positions based on our config
        valid_types = {ObjectType.PLANET, ObjectType.NODE, ObjectType.POINT}
        if self._config.include_angles:
            valid_types.add(ObjectType.ANGLE)
        if self._config.include_asteroids:
            valid_types.add(ObjectType.ASTEROID)

        valid_objects = [p for p in positions if p.object_type in valid_types]

        # 2. Iterate over every unique pair of objects
        for obj1, obj2 in combinations(valid_objects, 2):
            # Skip axis pairs (ASC/DSC, MC/IC, True Node/South Node)
            if _are_axis_pair(obj1, obj2):
                continue

            # Skip aspects TO Dsc/IC (but allow aspects TO Asc/MC)
            if obj2.name in ["DSC", "IC"] or obj1.name in ["DSC", "IC"]:
                continue

            # Skip Asc-MC aspect (angle to angle)
            if {obj1.name, obj2.name} == {"ASC", "MC"}:
                continue

            distance = _angular_distance(obj1.longitude, obj2.longitude)

            # 3. Check against each aspect in our config
            for aspect_name in self._config.aspects:
                # Look up the aspect angle from the registry
                aspect_info = get_aspect_info(aspect_name)
                if not aspect_info:
                    # Try as alias
                    aspect_info = get_aspect_by_alias(aspect_name)

                if not aspect_info:
                    # Skip unknown aspects
                    continue

                aspect_angle = aspect_info.angle
                actual_orb = abs(distance - aspect_angle)

                # 4. Ask the OrbEngine for the allowance
                orb_allowance = orb_engine.get_orb_allowance(obj1, obj2, aspect_name)

                # 5. If it's a match, create the Aspect object
                if actual_orb <= orb_allowance:
                    is_applying = _is_applying(obj1, obj2, aspect_angle, distance)

                    aspect = Aspect(
                        object1=obj1,
                        object2=obj2,
                        aspect_name=aspect_name,
                        aspect_degree=aspect_angle,
                        orb=actual_orb,
                        is_applying=is_applying,
                    )
                    aspects.append(aspect)

                    # Only one aspect per pair
                    break

        return aspects


class HarmonicAspectEngine:
    """
    Calculates harmonic aspects (eg H5, H7, H9).
    This engine does *not* use AspectConfig, as it defines its own angles.
    It *does* use the OrbEngine, which can be configured to give different orbs
    for different harmonics.
    """

    def __init__(self, harmonic: int) -> None:
        """
        Initialize the harmonic engine.

        Args:
            harmonic: The harmonic number (eg. 7 for septiles)
        """
        if harmonic <= 1:
            raise ValueError("Harmonic must be greater than 1.")

        self.harmonic = harmonic
        self.aspect_name = f"H{harmonic}"

        # Generate the aspect angles for this harmonic
        # e.g., H7 = [51.42, 102.85, 154.28]
        # We skip the 0/360 conjunction
        base_angle = 360.0 / harmonic
        self.aspect_angles = [(i * base_angle) for i in range(1, harmonic // 2 + 1)]

    def calculate_aspects(
        self, positions: list[CelestialPosition], orb_engine: OrbEngine
    ) -> list[Aspect]:
        """
        Calculate harmonic aspects for the configured harmonic number.

        Currently only calculates between ObjectType=Planet objects.

        Args:
            positions: The list of CelestialPositions objects to check.
            orb_engine: The OrbEngine that will provide the orb allowance.

        Returns:
            A list of found Aspect objects.
        """
        aspects = []

        # Harmonics are typically only calculated between planets
        valid_objects = [p for p in positions if p.object_type == ObjectType.PLANET]

        for obj1, obj2 in combinations(valid_objects, 2):
            distance = _angular_distance(obj1.longitude, obj2.longitude)

            # Check against each harmonic angle (e.g., 51.4, 102.8 for H7)
            for aspect_angle in self.aspect_angles:
                actual_orb = abs(distance - aspect_angle)

                # Ask the OrbEngine for allowance for "H7", etc.
                orb_allowance = orb_engine.get_orb_allowance(
                    obj1, obj2, self.aspect_name
                )

                if actual_orb <= orb_allowance:
                    is_applying = _is_applying(obj1, obj2, aspect_angle, distance)

                    aspect = Aspect(
                        object1=obj1,
                        object2=obj2,
                        aspect_name=self.aspect_name,
                        aspect_degree=round(aspect_angle),
                        orb=actual_orb,
                        is_applying=is_applying,
                    )
                    aspects.append(aspect)

                    # Only use one harmonic aspect per pair
                    break

        return aspects


class CrossChartAspectEngine:
    """
    Calculate aspects between two separate charts.

    Unlike ModernAspectEngine which finds all aspects within a single chart
    (using combinations of all positions), this engine specifically handles
    cross-chart scenarios where we want aspects BETWEEN chart1 objects and
    chart2 objects (but not within each chart).

    Use cases:
    - Synastry: Person A's planets aspecting Person B's planets
    - Transits: Current sky aspecting natal chart
    - Progressions: Progressed chart aspecting natal chart

    The key difference: controlled iteration. We only check pairs where
    one object is from chart1 and the other is from chart2. This prevents:
    - Object identity collision (same planet in both charts)
    - Redundant calculation (internal aspects already calculated separately)
    - Incorrect filtering (can't distinguish sources after merging lists)
    """

    def __init__(self, config: AspectConfig | None = None):
        """
        Initialize the cross-chart aspect engine.

        Args:
            config: An AspectConfig object defining which aspect angles
                    and object types to use. If None, a default
                    AspectConfig is created.
        """
        self._config = config or AspectConfig()

    def calculate_cross_aspects(
        self,
        chart1_positions: list[CelestialPosition],
        chart2_positions: list[CelestialPosition],
        orb_engine: OrbEngine,
    ) -> list[Aspect]:
        """
        Calculate aspects between two sets of positions.

        This only calculates aspects WHERE one object is from chart1
        and the other is from chart2. Internal aspects within each
        chart are NOT calculated by this method.

        Args:
            chart1_positions: Positions from first chart (e.g., natal/inner)
            chart2_positions: Positions from second chart (e.g., transit/outer)
            orb_engine: The OrbEngine that will provide orb allowances

        Returns:
            List of Aspect objects representing cross-chart aspects

        Example:
            >>> engine = CrossChartAspectEngine()
            >>> orb_engine = SimpleOrbEngine()
            >>> aspects = engine.calculate_cross_aspects(
            ...     natal_chart.positions,
            ...     transit_chart.positions,
            ...     orb_engine
            ... )
            >>> # Gets natal Sun trine transit Jupiter, etc.
            >>> # Does NOT get natal Sun trine natal Moon (internal)
        """
        aspects = []

        # 1. Filter positions based on config
        valid_types = {ObjectType.PLANET, ObjectType.NODE, ObjectType.POINT}
        if self._config.include_angles:
            valid_types.add(ObjectType.ANGLE)
        if self._config.include_asteroids:
            valid_types.add(ObjectType.ASTEROID)

        chart1_objects = [p for p in chart1_positions if p.object_type in valid_types]
        chart2_objects = [p for p in chart2_positions if p.object_type in valid_types]

        # 2. Controlled iteration: chart1 × chart2 only
        for obj1 in chart1_objects:
            for obj2 in chart2_objects:
                distance = _angular_distance(obj1.longitude, obj2.longitude)

                # 3. Check each aspect from config
                for aspect_name in self._config.aspects:
                    # Look up aspect angle from registry
                    aspect_info = get_aspect_info(aspect_name)
                    if not aspect_info:
                        # Try as alias
                        aspect_info = get_aspect_by_alias(aspect_name)

                    if not aspect_info:
                        # Skip unknown aspects
                        continue

                    aspect_angle = aspect_info.angle
                    actual_orb = abs(distance - aspect_angle)

                    # 4. Ask OrbEngine for allowance
                    orb_allowance = orb_engine.get_orb_allowance(
                        obj1, obj2, aspect_name
                    )

                    # 5. If close enough, create the aspect
                    if actual_orb <= orb_allowance:
                        is_applying = _is_applying(obj1, obj2, aspect_angle, distance)

                        aspect = Aspect(
                            object1=obj1,
                            object2=obj2,
                            aspect_name=aspect_name,
                            aspect_degree=aspect_angle,
                            orb=actual_orb,
                            is_applying=is_applying,
                        )
                        aspects.append(aspect)

                        # Only one aspect per pair
                        break

        return aspects


class DeclinationAspectEngine:
    """
    Calculates declination aspects (Parallel and Contraparallel).

    Declination aspects are based on celestial equatorial coordinates:
    - Parallel: Two bodies at the SAME declination (both north or both south).
      Interpreted similarly to a conjunction - blending of energies.
    - Contraparallel: Two bodies at the SAME declination magnitude but
      OPPOSITE hemispheres. Interpreted similarly to an opposition - polarity.

    Unlike longitude-based aspects which use variable orbs by planet,
    declination aspects traditionally use a fixed tight orb (1.0-1.5 degrees).

    Example:
        >>> engine = DeclinationAspectEngine(orb=1.0)
        >>> aspects = engine.calculate_aspects(chart.positions)
        >>> for asp in aspects:
        ...     print(asp)
        Sun Parallel Moon (orb: 0.45°)
        Mars Contraparallel Saturn (orb: 0.78°)
    """

    def __init__(
        self,
        orb: float = 1.0,
        include_types: set[ObjectType] | None = None,
    ) -> None:
        """
        Initialize the declination aspect engine.

        Args:
            orb: Maximum orb allowance in degrees (default 1.0°).
                 Traditional range is 1.0-1.5°. Declination aspects
                 use tighter orbs than longitude aspects.
            include_types: Which ObjectTypes to calculate aspects for.
                          Default: PLANET, NODE. Can also include ANGLE,
                          ASTEROID, POINT.
        """
        self.orb = orb
        self.include_types = include_types or {ObjectType.PLANET, ObjectType.NODE}

    def calculate_aspects(
        self,
        positions: list[CelestialPosition],
        orb_engine: OrbEngine
        | None = None,  # Ignored but included for protocol compatibility
    ) -> list[Aspect]:
        """
        Calculate parallel and contraparallel aspects.

        Args:
            positions: List of CelestialPosition objects to check.
                      Only positions with non-None declination are used.
            orb_engine: Ignored. Declination aspects use fixed orb.
                       Included for compatibility with AspectEngine protocol.

        Returns:
            List of Aspect objects for detected declination aspects.
        """
        aspects = []

        # Filter to valid objects with declination data
        valid_objects = [
            p
            for p in positions
            if p.object_type in self.include_types and p.declination is not None
        ]

        for obj1, obj2 in combinations(valid_objects, 2):
            # Skip axis pairs
            if _are_axis_pair(obj1, obj2):
                continue

            dec1, dec2 = obj1.declination, obj2.declination

            # Determine if same hemisphere (both north or both south)
            same_hemisphere = (dec1 >= 0) == (dec2 >= 0)

            # Calculate orb as difference in declination magnitude
            orb = abs(abs(dec1) - abs(dec2))

            if orb > self.orb:
                continue

            # Parallel = same hemisphere, same declination magnitude
            # Contraparallel = opposite hemispheres, same declination magnitude
            aspect_name = "Parallel" if same_hemisphere else "Contraparallel"
            aspect_degree = 0 if same_hemisphere else 180

            aspects.append(
                Aspect(
                    object1=obj1,
                    object2=obj2,
                    aspect_name=aspect_name,
                    aspect_degree=aspect_degree,
                    orb=orb,
                    is_applying=None,  # Would need declination velocity to determine
                )
            )

        return aspects
