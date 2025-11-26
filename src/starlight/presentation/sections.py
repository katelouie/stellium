"""
Report section implementations.

Each section extracts specific data from a CalculatedChart and formats it
into a standardized structure that renderers can consume.
"""

import datetime as dt
from typing import Any

from starlight.core.models import CalculatedChart, MidpointPosition, ObjectType
from starlight.core.registry import CELESTIAL_REGISTRY, get_aspects_by_category


def get_object_sort_key(position):
    """
    Generate sort key for consistent object ordering in reports.

    Sorting hierarchy:
    1. Object type (Planet < Node < Point < Asteroid < Angle < Midpoint)
    2. Registry insertion order (for registered objects)
    3. Swiss Ephemeris ID (for unregistered known objects)
    4. Alphabetical name (for custom objects)

    Args:
        position: A celestial object position from CalculatedChart

    Returns:
        Tuple sort key for use with sorted()

    Example:
        positions = sorted(chart.positions, key=get_object_sort_key)
    """
    # Define type ordering
    type_order = {
        ObjectType.PLANET: 0,
        ObjectType.NODE: 1,
        ObjectType.POINT: 2,
        ObjectType.ASTEROID: 3,
        ObjectType.ANGLE: 4,
        ObjectType.MIDPOINT: 5,
    }

    type_rank = type_order.get(position.object_type, 999)

    # Try registry order (using insertion order of dict keys)
    registry_keys = list(CELESTIAL_REGISTRY.keys())
    if position.name in registry_keys:
        registry_index = registry_keys.index(position.name)
        return (type_rank, registry_index)

    # Fallback to Swiss Ephemeris ID
    if (
        hasattr(position, "swiss_ephemeris_id")
        and position.swiss_ephemeris_id is not None
    ):
        return (type_rank, 10000 + position.swiss_ephemeris_id)

    # Final fallback: alphabetical by name
    return (type_rank, 20000, position.name)


def get_aspect_sort_key(aspect_name: str) -> tuple:
    """
    Generate sort key for consistent aspect ordering in reports.

    Sorting hierarchy:
    1. Registry insertion order (aspects ordered by angle: 0°, 60°, 90°, etc.)
    2. Angle value (for aspects not in registry)
    3. Alphabetical name (final fallback)

    Args:
        aspect_name: Name of the aspect (e.g., "Conjunction", "Trine")

    Returns:
        Tuple sort key for use with sorted()

    Example:
        aspects = sorted(aspects, key=lambda a: get_aspect_sort_key(a.aspect_name))
    """
    from starlight.core.registry import (
        ASPECT_REGISTRY,
        get_aspect_by_alias,
        get_aspect_info,
    )

    # Try registry order (insertion order = angle order)
    registry_keys = list(ASPECT_REGISTRY.keys())
    if aspect_name in registry_keys:
        registry_index = registry_keys.index(aspect_name)
        return (registry_index,)

    # Try to find by alias
    aspect_info = get_aspect_by_alias(aspect_name)
    if aspect_info and aspect_info.name in registry_keys:
        registry_index = registry_keys.index(aspect_info.name)
        return (registry_index,)

    # Fallback: try to get angle from registry
    aspect_info = get_aspect_info(aspect_name)
    if aspect_info:
        return (1000 + aspect_info.angle,)

    # Final fallback: alphabetical
    return (2000, aspect_name)


class ChartOverviewSection:
    """
    Overview section with basic chart information.

    Shows:
    - Native name (if available)
    - Birth date/time
    - Location
    - Chart type (day/night)
    - House system
    """

    @property
    def section_name(self) -> str:
        return "Chart Overview"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate chart overview data.

        Why key-value format?
        - Simple label: value pairs
        - Easy to render as a list or small table
        - Human-readable structure
        """
        data = {}

        # Name (if available in metadata)
        if "name" in chart.metadata:
            data["Name"] = chart.metadata["name"]

        # Date and time
        birth: dt.datetime = chart.datetime.local_datetime
        data["Date"] = birth.strftime("%B %d, %Y")
        data["Time"] = birth.strftime("%I:%M %p")
        data["Timezone"] = str(chart.location.timezone)

        # Location
        loc = chart.location
        data["Location"] = f"{loc.name}" if loc.name else "Unknown"
        data["Coordinates"] = f"{loc.latitude:.4f}°, {loc.longitude:.4f}°"

        # Chart metadata
        house_systems = ", ".join(chart.house_systems.keys())
        data["House System"] = house_systems

        # Sect (if available in metadata)
        if "dignities" in chart.metadata:
            sect = chart.metadata["dignities"].get("sect", "unknown")
            data["Chart Sect"] = f"{sect.title()} Chart"

        return {
            "type": "key_value",
            "data": data,
        }


class PlanetPositionSection:
    """Table of planet positions.

    Shows:
    - Planet name
    - Sign + degree
    - House (optional)
    - Speed (optional, shows retrograde status)
    """

    def __init__(
        self,
        include_speed: bool = False,
        include_house: bool = True,
        house_system: str | None = None,
    ) -> None:
        """
        Initialize section with display options.

        Args:
            include_speed: Show speed column (for retrograde detection)
            include_house: Show house placement column
            house_system: Which system to use for houses (None = chart default)
        """
        self.include_speed = include_speed
        self.include_house = include_house
        self.house_system = house_system

    @property
    def section_name(self) -> str:
        return "Planet Positions"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate planet positions table.
        """
        # Build headers based on options
        headers = ["Planet", "Position"]

        if self.include_house:
            headers.append("House")

        if self.include_speed:
            headers.append("Speed")
            headers.append("Motion")

        # Filter to planets, asteroids, nodes and points
        positions = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]

        # Sort positions consistently
        positions = sorted(positions, key=get_object_sort_key)

        # Build rows
        rows = []
        for pos in positions:
            row = []
            # Planet name
            row.append(pos.name)

            # Position (e.g., "15° ♌ 32'")
            degree = int(pos.sign_degree)
            minute = int((pos.sign_degree % 1) * 60)
            row.append(f"{degree}° {pos.sign} {minute:02d}'")

            # House (if requested)
            if self.include_house:
                system = self.house_system or chart.default_house_system
                try:
                    house_placements = chart.house_placements[system]
                    house = house_placements.get(pos.name, "—")
                    row.append(str(house) if house else "—")
                except KeyError:
                    row.append("—")

            # Speed and motion (if requested)
            if self.include_speed:
                row.append(f"{pos.speed_longitude:.4f}°/day")
                row.append("Retrograde" if pos.is_retrograde else "Direct")

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class AspectSection:
    """
    Table of aspects between planets.

    Shows:
    - Planet 1
    - Aspect type
    - Planet 2
    - Orb (optional)
    - Applying/Separating (optional)
    """

    def __init__(
        self, mode: str = "all", orbs: bool = True, sort_by: str = "orb"
    ) -> None:
        """
        Initialize aspect section.

        Args:
            mode: "all", "major", "minor", or "harmonic"
        """
        if mode not in ("all", "major", "minor", "harmonic"):
            raise ValueError(
                f"mode must be 'all', 'major', 'minor', or 'harmonic', got {mode}"
            )
        if sort_by not in ("orb", "planet", "aspect_type"):
            raise ValueError(
                f"sort_by must be 'orb', 'planet', or 'aspect_type', got {sort_by}"
            )

        self.mode = mode
        self.orb_display = orbs
        self.sort_by = sort_by

    @property
    def section_name(self) -> str:
        if self.mode == "major":
            return "Major Aspects"
        elif self.mode == "minor":
            return "Minor Aspects"
        elif self.mode == "harmonic":
            return "Harmonic Aspects"
        return "Aspects"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate aspects table."""
        # Filer aspects based on mode
        aspects = chart.aspects
        aspect_category = self.mode.title()
        allowed_aspects = [a.name for a in get_aspects_by_category(aspect_category)]
        aspects = [a for a in aspects if a.aspect_name in allowed_aspects]

        # Sort aspects
        if self.sort_by == "orb":
            aspects = sorted(aspects, key=lambda a: a.orb)
        elif self.sort_by == "aspect_type":
            # Sort by aspect using registry order (angle order)
            aspects = sorted(aspects, key=lambda a: get_aspect_sort_key(a.aspect_name))
        elif self.sort_by == "planet":
            # Sort by first object, then second object
            aspects = sorted(
                aspects,
                key=lambda a: (
                    get_object_sort_key(a.object1),
                    get_object_sort_key(a.object2),
                ),
            )

        # Build headers
        headers = ["Planet 1", "Aspect", "Planet 2"]
        if self.orb_display:
            headers.append("Orb")
            headers.append("Applying")

        # Build rows
        rows = []
        for aspect in aspects:
            row = [aspect.object1.name, aspect.aspect_name, aspect.object2.name]

            if self.orb_display:
                row.append(f"{aspect.orb:.2f}°")

                # Applying/separating
                if aspect.is_applying is None:
                    row.append("—")
                elif aspect.is_applying:
                    row.append("A→")  # Applying
                else:
                    row.append("←S")  # Separating

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


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

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoints table."""
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


class CacheInfoSection:
    """Display cache statistics in reports."""

    @property
    def section_name(self) -> str:
        return "Cache Statistics"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate cache info from chart metadata."""
        cache_stats = chart.metadata.get("cache_stats", {})

        if not cache_stats.get("enabled", False):
            return {"type": "text", "text": "Caching is disabled for this chart."}

        data = {
            "Cache Directory": cache_stats.get("cache_directory", "N/A"),
            "Max Age": f"{cache_stats.get('max_age_seconds', 0) / 3600:.1f} hours",
            "Total Files": cache_stats.get("total_cached_files", 0),
            "Total Size": f"{cache_stats.get('cache_size_mb', 0)} MB",
        }

        # Add breakdown by type
        by_type = cache_stats.get("by_type", {})
        for cache_type, count in by_type.items():
            data[f"{cache_type.title()} Files"] = count

        return {
            "type": "key_value",
            "data": data,
        }


class MoonPhaseSection:
    """Display Moon phase information."""

    @property
    def section_name(self) -> str:
        return "Moon Phase"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate moon phase data."""
        moon = chart.get_object("Moon")

        if not moon or not moon.phase:
            return {"type": "text", "text": "Moon phase data not available."}

        phase = moon.phase

        data = {
            "Phase Name": phase.phase_name,
            "Illumination": f"{phase.illuminated_fraction:.1%}",
            "Phase Angle": f"{phase.phase_angle:.1f}°",
            "Direction": "Waxing" if phase.is_waxing else "Waning",
            "Apparent Magnitude": f"{phase.apparent_magnitude:.2f}",
            "Apparent Diameter": f"{phase.apparent_diameter:.1f}″",
            "Geocentric Parallax": f"{phase.geocentric_parallax:.4f} rad",
        }

        return {
            "type": "key_value",
            "data": data,
        }
