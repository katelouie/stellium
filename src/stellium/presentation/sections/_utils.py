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


def get_orb_sort_key(aspect) -> tuple:
    """Sort key for ordering aspects by orb — a *total* order, and a stable one.

    `sorted(aspects, key=lambda a: a.orb)` is not stable across machines, because
    two aspects that are *mathematically* the same angle can hold different floats:

        Neptune Square True Node    5.1401672080752405
        Neptune Square South Node   5.140167208075212

    The nodes are exactly 180° apart, so those orbs are the same number — they differ
    only in the last bits, and which one sorts first depends on the platform's libm.
    That is how the aspect table came out with two rows swapped on Linux versus macOS,
    and it is not a rounding difference anyone can see: both print as 5.14°.

    So the key quantizes before comparing, then breaks any resulting tie by name.
    Quantizing alone is not enough (a true value can straddle the boundary and round
    two ways); the names make the order total.

    **This changes no value anywhere.** `aspect.orb` keeps every digit it had, in the
    chart, in `to_dict()`, and on the page. The rounding exists only inside this
    comparison and is thrown away with it.

    1e-9° is ~3.6 microarcseconds. Swiss Ephemeris resolves about 0.001″, so the bits
    being discarded here are roughly a million times finer than the ephemeris can see.
    They are noise, not data.
    """
    return (
        round(aspect.orb, 9),
        aspect.object1.name,
        aspect.aspect_name,
        aspect.object2.name,
    )


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


# Short forms for a narrow table column, per locale.
#
# English falls back to the first four characters when a system is not listed, which
# collided: "Equal (MC)" and "Equal (Vertex)" both became "Equa". All 17 shipped
# systems are now listed explicitly.
#
# Chinese gets one character per system, which is what a Han character is for — and it
# resolves the collision English could not: 等中 / 等宿.
HOUSE_ABBREVIATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Placidus": "Pl",
        "Whole Sign": "WS",
        "Koch": "Ko",
        "Equal": "Eq",
        "Equal (MC)": "EqMC",
        "Equal (Vertex)": "EqVx",
        "Porphyry": "Po",
        "Regiomontanus": "Re",
        "Campanus": "Ca",
        "Morinus": "Mo",
        "Meridian": "Me",
        "Alcabitius": "Al",
        "Horizontal": "Hz",
        "Axial Rotation": "Ax",
        "Topocentric": "Tp",
        "Krusinski": "Kr",
        "Vehlow Equal": "Ve",
        "APC": "APC",
    },
    "zh_CN": {
        "Placidus": "普",
        "Whole Sign": "整",
        "Koch": "科",
        "Equal": "等",
        "Equal (MC)": "等中",
        "Equal (Vertex)": "等宿",
        "Porphyry": "波",
        "Regiomontanus": "雷",
        "Campanus": "坎",
        "Morinus": "莫",
        "Meridian": "子",
        "Alcabitius": "阿",
        "Horizontal": "地平",
        "Axial Rotation": "轴",
        "Topocentric": "站",
        "Krusinski": "克",
        "Vehlow Equal": "韦",
        "APC": "APC",
    },
}


def abbreviate_house_system(system_name: str, locale: str | None = None) -> str:
    """
    Short form of a house system name, for a table column header.

    Args:
        system_name: Full house system name (e.g., "Placidus", "Whole Sign")
        locale: Locale to abbreviate for. Defaults to the active locale.

    Returns:
        A short abbreviation (e.g., "Pl", "WS", or 普 / 整 in Chinese)

    Example:
        >>> abbreviate_house_system("Placidus")
        'Pl'
        >>> abbreviate_house_system("Equal (Vertex)")
        'EqVx'
        >>> abbreviate_house_system("Placidus", locale="zh_CN")
        '普'
    """
    from stellium.i18n.loader import get_default_locale

    lang = locale or get_default_locale() or "en"
    table = HOUSE_ABBREVIATIONS.get(lang) or HOUSE_ABBREVIATIONS["en"]
    fallback = HOUSE_ABBREVIATIONS["en"]
    return table.get(system_name) or fallback.get(system_name) or system_name[:4]
