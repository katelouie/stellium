"""
Midpoint-related report sections.

Includes:
- MidpointSection: Table of calculated midpoints
- MidpointAspectsSection: Planets aspecting midpoints
"""

from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, MidpointPosition, ObjectType
from stellium.core.multichart import MultiChart

from ._utils import get_aspect_display, get_object_display, get_object_sort_key


class MidpointSection:
    """
    Table of midpoints.

    Shows:
    - Midpoint pair (e.g., "Sun/Moon")
    - Degree position
    - Sign
    """

    CORE_OBJECTS = {"Sun", "Moon", "ASC", "MC"}

    def __init__(self, mode: str = "all", threshold: int | None = None) -> None:
        """
        Initialize midpoint section.

        Args:
            mode: "all" or "core" (only Sun/Moon/ASC/MC midpoints)
            threshold: Only show top N midpoints
        """
        if mode not in ("all", "core"):
            raise ValueError(f"mode must be 'all' or 'core', got {mode}")

        self.mode = mode
        self.threshold = threshold

    @property
    def section_name(self) -> str:
        if self.mode == "core":
            return "Core Midpoints (Sun/Moon/ASC/MC)"
        return "Midpoints"

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """Generate midpoints table.

        For MultiChart/Comparison, shows midpoints for each chart grouped by label.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's midpoints
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []

            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                sections.append((f"{label} Midpoints", single_data))

            return {"type": "compound", "sections": sections}

        # Single chart: standard processing
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoints table for a single chart."""
        # Get midpoints
        midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]
        # Filter to core midpoints if requested
        if self.mode == "core":
            midpoints = [mp for mp in midpoints if self._is_core_midpoint(mp.name)]

        # Sort midpoints by component objects using object1/object2
        def get_midpoint_sort_key(mp):
            # Use isinstance to check if it's a MidpointPosition
            if isinstance(mp, MidpointPosition):
                # Direct access to component objects - use registry order!
                return (
                    get_object_sort_key(mp.object1),
                    get_object_sort_key(mp.object2),
                )
            else:
                # Fallback for legacy CelestialPosition midpoints (backward compatibility)
                # Parse names like "Midpoint:Sun/Moon"
                if ":" in mp.name:
                    pair_part = mp.name.split(":")[1]
                else:
                    pair_part = mp.name

                # Remove "(indirect)" if present
                pair_part = pair_part.replace(" (indirect)", "")

                # Split into component names
                objects = pair_part.split("/")
                if len(objects) == 2:
                    return (objects[0], objects[1])

                # Final fallback: use full name
                return (mp.name,)

        midpoints = sorted(midpoints, key=get_midpoint_sort_key)

        # Apply threshold AFTER sorting (limit to top N)
        if self.threshold:
            midpoints = midpoints[: self.threshold]
        # Build table
        headers = ["Midpoint", "Position"]
        rows = []

        for mp in midpoints:
            # Parse midpoint name (e.g., "Midpoint:Sun/Moon")
            name_parts = mp.name.split(":")
            if len(name_parts) > 1:
                pair_name = name_parts[1]
            else:
                pair_name = mp.name

            # Position
            degree = int(mp.sign_degree)
            minute = int((mp.sign_degree % 1) * 60)
            position = f"{degree}° {mp.sign} {minute:02d}'"

            rows.append([pair_name, position])

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _is_core_midpoint(self, midpoint_name: str) -> bool:
        """Check if midpoint involves core objects."""
        # Midpoint name format: "Midpoint:Sun/Moon" or "Midpoint:Sun/Moon (indirect)"
        if ":" not in midpoint_name:
            return False

        pair_part = midpoint_name.split(":")[1]
        # Remove "(indirect)" if present
        pair_part = pair_part.replace(" (indirect)", "")

        # Split pair
        objects = pair_part.split("/")
        if len(objects) != 2:
            return False

        # Check if both are core objects
        return all(obj in self.CORE_OBJECTS for obj in objects)


class MidpointAspectsSection:
    """
    Table of planets aspecting midpoints.

    This is what most people care about with midpoints: which planets
    activate which midpoints? Typically conjunctions are most important
    (1-2° orb), but hard aspects (square, opposition) can also be shown.

    Shows:
    - Planet that aspects the midpoint
    - Aspect type (conjunction, square, etc.)
    - Midpoint being aspected (e.g., "Sun/Moon")
    - Orb in degrees
    """

    CORE_OBJECTS = {"Sun", "Moon", "ASC", "MC"}

    # Default aspect angles to check (degrees)
    ASPECT_ANGLES = {
        "Conjunction": 0,
        "Opposition": 180,
        "Square": 90,
        "Trine": 120,
        "Sextile": 60,
    }

    def __init__(
        self,
        mode: str = "conjunction",
        orb: float = 1.5,
        midpoint_filter: str = "all",
        sort_by: str = "orb",
    ) -> None:
        """
        Initialize midpoint aspects section.

        Args:
            mode: Which aspects to show
                - "conjunction": Only conjunctions (most common, recommended)
                - "hard": Conjunction, square, opposition
                - "all": All major aspects
            orb: Maximum orb in degrees (default 1.5°, typical for midpoints)
            midpoint_filter: Which midpoints to check
                - "all": All midpoints
                - "core": Only Sun/Moon/ASC/MC midpoints
            sort_by: Sort order
                - "orb": Tightest aspects first (default)
                - "planet": Group by aspecting planet
                - "midpoint": Group by midpoint
        """
        valid_modes = ("conjunction", "hard", "all")
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}, got {mode}")

        valid_sorts = ("orb", "planet", "midpoint")
        if sort_by not in valid_sorts:
            raise ValueError(f"sort_by must be one of {valid_sorts}, got {sort_by}")

        self.mode = mode
        self.orb = orb
        self.midpoint_filter = midpoint_filter
        self.sort_by = sort_by

        # Set which aspects to check based on mode
        if mode == "conjunction":
            self._aspects = {"Conjunction": 0}
        elif mode == "hard":
            self._aspects = {
                "Conjunction": 0,
                "Square": 90,
                "Opposition": 180,
            }
        else:  # all
            self._aspects = self.ASPECT_ANGLES.copy()

    @property
    def section_name(self) -> str:
        if self.mode == "conjunction":
            return "Planets Conjunct Midpoints"
        elif self.mode == "hard":
            return "Hard Aspects to Midpoints"
        return "Aspects to Midpoints"

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """Generate midpoint aspects table.

        For MultiChart/Comparison, shows midpoint aspects for each chart grouped by label.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's midpoint aspects
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []

            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                sections.append((f"{label} Midpoint Aspects", single_data))

            return {"type": "compound", "sections": sections}

        # Single chart: standard processing
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoint aspects table for a single chart."""
        # Get midpoints
        midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

        if not midpoints:
            return {
                "type": "text",
                "text": (
                    "No midpoints calculated. Add MidpointCalculator() to include them:\n\n"
                    "    from stellium.components import MidpointCalculator\n\n"
                    "    chart = (\n"
                    "        ChartBuilder.from_native(native)\n"
                    "        .add_component(MidpointCalculator())\n"
                    "        .calculate()\n"
                    "    )"
                ),
            }

        # Filter to core midpoints if requested
        if self.midpoint_filter == "core":
            midpoints = [mp for mp in midpoints if self._is_core_midpoint(mp.name)]

        # Get planets/points to check (exclude midpoints and fixed stars)
        planets = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.NODE,
                ObjectType.POINT,
                ObjectType.ANGLE,
            )
        ]

        # Find aspects between planets and midpoints
        found_aspects = []

        for planet in planets:
            for midpoint in midpoints:
                # Skip if planet is one of the midpoint's components
                if isinstance(midpoint, MidpointPosition):
                    if planet.name in (midpoint.object1.name, midpoint.object2.name):
                        continue

                # Check each aspect type
                for aspect_name, aspect_angle in self._aspects.items():
                    orb = self._calculate_orb(
                        planet.longitude, midpoint.longitude, aspect_angle
                    )

                    if orb <= self.orb:
                        # Parse midpoint display name
                        mp_display = self._get_midpoint_display(midpoint)

                        found_aspects.append(
                            {
                                "planet": planet,
                                "aspect": aspect_name,
                                "midpoint": midpoint,
                                "midpoint_display": mp_display,
                                "orb": orb,
                            }
                        )

        if not found_aspects:
            return {
                "type": "text",
                "text": f"No planets found within {self.orb}° of midpoints.",
            }

        # Sort results
        if self.sort_by == "orb":
            found_aspects.sort(key=lambda x: x["orb"])
        elif self.sort_by == "planet":
            found_aspects.sort(
                key=lambda x: (
                    get_object_sort_key(x["planet"]),
                    x["orb"],
                )
            )
        else:  # midpoint
            found_aspects.sort(
                key=lambda x: (
                    x["midpoint_display"],
                    x["orb"],
                )
            )

        # Build table
        headers = ["Planet", "Aspect", "Midpoint", "Orb"]
        rows = []

        for asp in found_aspects:
            planet = asp["planet"]
            display_name, glyph = get_object_display(planet.name)
            planet_label = f"{glyph} {display_name}" if glyph else display_name

            aspect_name, aspect_glyph = get_aspect_display(asp["aspect"])
            aspect_label = (
                f"{aspect_glyph} {aspect_name}" if aspect_glyph else aspect_name
            )

            orb_str = f"{asp['orb']:.2f}°"

            rows.append([planet_label, aspect_label, asp["midpoint_display"], orb_str])

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _calculate_orb(self, lon1: float, lon2: float, aspect_angle: float) -> float:
        """Calculate orb between two longitudes for a given aspect."""
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff

        return abs(diff - aspect_angle)

    def _is_core_midpoint(self, midpoint_name: str) -> bool:
        """Check if midpoint involves core objects."""
        if ":" not in midpoint_name:
            return False

        pair_part = midpoint_name.split(":")[1]
        pair_part = pair_part.replace(" (indirect)", "")

        objects = pair_part.split("/")
        if len(objects) != 2:
            return False

        return all(obj in self.CORE_OBJECTS for obj in objects)

    def _get_midpoint_display(self, midpoint) -> str:
        """Get display name for a midpoint."""
        if ":" in midpoint.name:
            pair_part = midpoint.name.split(":")[1]
        else:
            pair_part = midpoint.name

        # Remove "(indirect)" but add marker
        if "(indirect)" in pair_part:
            pair_part = pair_part.replace(" (indirect)", "") + "*"

        return pair_part
