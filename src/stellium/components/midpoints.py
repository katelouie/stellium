"""
Midpoint calculator component.

Midpoints are the halfway point between two celestial objects.
They represent the synthesis or blend of two planetary energies.

In midpoint astrology:
- Direct midpoint: Shortest arc between two points
- Indirect midpoint: Opposite point (180° from direct)

Both are significant, but direct midpoint is more commonly used.
"""

from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    MidpointPosition,
    ObjectType,
)


class MidpointCalculator:
    """
    Calculate midpoints between celestial objects.

    Midpoints reveal how two planetary energies blend or interact.
    They're used extensively in Uranian astrology and some modern approaches.
    """

    # Common midpoint pairs used in traditional interpretation
    DEFAULT_PAIRS = [
        # === Core Identity Axes ===
        # These are the "big four" of the chart and their combinations.
        ("Sun", "Moon"),
        ("Sun", "ASC"),
        ("Sun", "MC"),
        ("Moon", "ASC"),
        ("Moon", "MC"),
        ("ASC", "MC"),
        # === Personality Expression ===
        # How the core identity (Sun/Moon) blends with
        # thought (Mercury), love/values (Venus), and drive (Mars).
        ("Sun", "Mercury"),
        ("Sun", "Venus"),
        ("Sun", "Mars"),
        ("Moon", "Mercury"),
        ("Moon", "Venus"),
        ("Moon", "Mars"),
        # === Inner Planet Dynamics ===
        # The key blends for love, communication, and action.
        ("Mercury", "Venus"),
        ("Mercury", "Mars"),
        ("Venus", "Mars"),
        # === Key Social & Structural Points ===
        # How the personal planets interact with opportunity (Jupiter)
        # and structure/limitation (Saturn).
        ("Sun", "Jupiter"),
        ("Sun", "Saturn"),
        ("Moon", "Jupiter"),
        ("Moon", "Saturn"),
        # These two are classic "action" and "structure" midpoints.
        ("Mars", "Jupiter"),
        ("Mars", "Saturn"),
        # The "great benefics" and "social cycle" midpoints.
        ("Venus", "Jupiter"),
        ("Jupiter", "Saturn"),
    ]

    def __init__(
        self,
        pairs: list[tuple[str, str]] | None = None,
        calculate_all: bool = False,
        indirect: bool = False,
    ) -> None:
        """
        Initialize midpoint calculator.

        Args:
            pairs: Specific pairs to calculate (None=use defaults)
            calculate_all: Calculate all planet pairs (overrides `pairs`)
            indirect: Also calculate indirect midpoints (180 degrees opposite)
        """
        self._pairs = pairs or self.DEFAULT_PAIRS
        self._calculate_all = calculate_all
        self._include_indirect = indirect

    @property
    def component_name(self) -> str:
        return "Midpoints"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate midpoints.

        Args:
            datetime: Chart datetime (unused)
            location: Chart location (unused)
            positions: Already calculated positions
            house_systems_map: House cusps for house assignment (unused)
            house_placements_map: (unused)

        Returns:
            List of CelestialPosition objects for midpoints
        """
        # Build position lookup
        pos_dict = {p.name: p for p in positions}

        # Determine which pairs to calculate
        if self._calculate_all:
            # All planet-to-planet and planet-to-node pairs
            valid_objects = [
                p
                for p in positions
                if p.object_type in (ObjectType.PLANET, ObjectType.NODE)
            ]
            pairs = [
                (p1.name, p2.name)
                for i, p1 in enumerate(valid_objects)
                for p2 in valid_objects[i + 1 :]
            ]
        else:
            pairs = self._pairs

        midpoints = []

        for obj1_name, obj2_name in pairs:
            if obj1_name not in pos_dict or obj2_name not in pos_dict:
                continue

            obj1 = pos_dict[obj1_name]
            obj2 = pos_dict[obj2_name]

            # Calculate direct midpoint
            direct_mid = self._calculate_direct_midpoint(obj1, obj2)
            midpoints.append(direct_mid)

            # Calculate indirect midpoint too if requested
            if self._include_indirect:
                indirect_mid = self._calculate_indirect_midpoint(obj1, obj2)
                midpoints.append(indirect_mid)

        return midpoints

    def _calculate_direct_midpoint(
        self, obj1: CelestialPosition, obj2: CelestialPosition
    ) -> MidpointPosition:
        """
        Calculate direct midpoint (shortest arc).

        Args:
            obj1: First object
            obj2: Second object

        Returns:
            MidpointPosition for the midpoint
        """
        # Calculate shortest arc midpoint
        long1, long2 = obj1.longitude, obj2.longitude

        # Calculate angular distance
        diff = abs(long2 - long1)

        if diff <= 180:
            # Direct arc
            midpoint_long = (long1 + long2) / 2
        else:
            # Shorter arc goes the other way
            midpoint_long = ((long1 + long2) / 2 + 180) % 360

        # Create midpoint position
        return MidpointPosition(
            name=f"Midpoint:{obj1.name}/{obj2.name}",
            object_type=ObjectType.MIDPOINT,
            longitude=midpoint_long,
            object1=obj1,
            object2=obj2,
            is_indirect=False,
        )

    def _calculate_indirect_midpoint(
        self, obj1: CelestialPosition, obj2: CelestialPosition
    ) -> MidpointPosition:
        """
        Calculate indirect midpoint (opposite of direct).

        Args:
            obj1: First object
            obj2: Second object

        Returns:
            MidpointPosition for the indirect midpoint
        """
        # Get direct midpoint
        direct = self._calculate_direct_midpoint(obj1, obj2)

        # Indirect is 180° opposite
        indirect_long = (direct.longitude + 180) % 360

        return MidpointPosition(
            name=f"Midpoint:{obj1.name}/{obj2.name} (indirect)",
            object_type=ObjectType.MIDPOINT,
            longitude=indirect_long,
            object1=obj1,
            object2=obj2,
            is_indirect=True,
        )
