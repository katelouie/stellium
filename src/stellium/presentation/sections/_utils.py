"""
Utility functions for report sections.

These helper functions are shared across multiple section implementations
for consistent formatting and display.
"""

from stellium.core.models import ObjectType
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    get_aspect_by_alias,
    get_aspect_info,
)
from stellium.engines.dignities import DIGNITIES


def get_object_display(name: str) -> tuple[str, str]:
    """
    Get display name and glyph for a celestial object.

    Args:
        name: Internal object name (e.g., "Sun", "True Node")

    Returns:
        Tuple of (display_name, glyph)
    """
    if name in CELESTIAL_REGISTRY:
        info = CELESTIAL_REGISTRY[name]
        return info.display_name, info.glyph
    return name, ""


def get_sign_glyph(sign_name: str) -> str:
    """Get the zodiac glyph for a sign name."""
    if sign_name in DIGNITIES:
        return DIGNITIES[sign_name]["symbol"]
    return ""


def get_aspect_display(aspect_name: str) -> tuple[str, str]:
    """
    Get display name and glyph for an aspect.

    Args:
        aspect_name: Aspect name (e.g., "Conjunction", "Trine")

    Returns:
        Tuple of (name, glyph)
    """
    if aspect_name in ASPECT_REGISTRY:
        info = ASPECT_REGISTRY[aspect_name]
        return info.name, info.glyph
    return aspect_name, ""


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


def abbreviate_house_system(system_name: str) -> str:
    """
    Generate 2-4 character abbreviation for house system names.

    Args:
        system_name: Full house system name (e.g., "Placidus", "Whole Sign")

    Returns:
        Short abbreviation (e.g., "Pl", "WS")

    Example:
        >>> abbreviate_house_system("Placidus")
        'Pl'
        >>> abbreviate_house_system("Whole Sign")
        'WS'
    """
    abbreviations = {
        "Placidus": "Pl",
        "Whole Sign": "WS",
        "Koch": "Ko",
        "Equal": "Eq",
        "Porphyry": "Po",
        "Regiomontanus": "Re",
        "Campanus": "Ca",
        "Morinus": "Mo",
        "Meridian": "Me",
        "Alcabitius": "Al",
    }
    return abbreviations.get(system_name, system_name[:4])
