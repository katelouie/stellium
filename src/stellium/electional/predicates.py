"""
Helper predicates for electional astrology conditions.

These factory functions return Condition callables that can be used with
ElectionalSearch. They provide readable, reusable building blocks for
common astrological filters.

All predicates return `Callable[[CalculatedChart], bool]` (the Condition type).

Each predicate is tagged with a "speed hint" indicating how quickly the condition
changes, enabling hierarchical filtering for performance:
- SPEED_DAY: Stable conditions (phase, retrograde) - checked once at noon
- SPEED_DAY_SIGN: Sign-based conditions - checked at start+end of day
- SPEED_HOUR: Hour-level conditions (VOC, aspects)
- SPEED_MINUTE: House/angular positions (change with Earth's rotation)

Example:
    >>> from stellium.electional import ElectionalSearch, is_waxing, not_voc, on_angle
    >>> results = (ElectionalSearch("2025-01-01", "2025-12-31", "New York, NY")
    ...     .where(is_waxing())
    ...     .where(not_voc())
    ...     .where(on_angle("Jupiter"))
    ...     .find_moments())
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart

# Type alias for conditions
Condition = Callable[["CalculatedChart"], bool]

# =============================================================================
# Speed Hint Constants
# =============================================================================
# These indicate how quickly a condition changes, enabling hierarchical filtering.

SPEED_DAY = 1  # Stable: phase, retrograde - check noon, skip day if fails
SPEED_DAY_SIGN = 2  # Sign-based: check start+end of day, skip only if BOTH fail
SPEED_HOUR = 3  # VOC, aspects - check hourly
SPEED_MINUTE = 4  # House placement - check at user's step (default for lambdas)


def _tag(condition: Condition, speed: int) -> Condition:
    """Tag a condition with its speed hint for hierarchical filtering."""
    condition._speed_hint = speed  # type: ignore[attr-defined]
    return condition


def _tag_windows(
    condition: Condition, window_generator: Callable[..., Any]
) -> Condition:
    """Tag a condition with its window generator for interval optimization.

    The window_generator should be a callable that takes (start, end) and returns
    a list of TimeWindow objects.
    """
    condition._get_windows = window_generator  # type: ignore[attr-defined]
    return condition


def get_speed_hint(condition: Any) -> int:
    """Get the speed hint for a condition, defaulting to SPEED_MINUTE."""
    return getattr(condition, "_speed_hint", SPEED_MINUTE)


def get_window_generator(condition: Any) -> Callable[..., Any] | None:
    """Get the window generator for a condition, if available."""
    return getattr(condition, "_get_windows", None)


# =============================================================================
# Moon Phase Predicates
# =============================================================================


def is_waxing() -> Condition:
    """Moon is waxing (between New and Full Moon).

    Returns:
        Condition that checks if Moon phase is waxing

    Example:
        >>> search.where(is_waxing())
    """
    from stellium.electional.intervals import waxing_windows

    def check(chart: CalculatedChart) -> bool:
        moon = chart.get_object("Moon")
        if moon is None or moon.phase is None:
            return False
        return moon.phase.is_waxing

    condition = _tag(check, SPEED_DAY)
    return _tag_windows(condition, waxing_windows)


def is_waning() -> Condition:
    """Moon is waning (between Full and New Moon).

    Returns:
        Condition that checks if Moon phase is waning
    """
    from stellium.electional.intervals import waning_windows

    def check(chart: CalculatedChart) -> bool:
        moon = chart.get_object("Moon")
        if moon is None or moon.phase is None:
            return False
        return not moon.phase.is_waxing

    condition = _tag(check, SPEED_DAY)
    return _tag_windows(condition, waning_windows)


def moon_phase(phases: list[str]) -> Condition:
    """Moon is in one of the specified phases.

    Args:
        phases: List of phase names, e.g., ["New Moon", "Full Moon"]
            Valid phases: "New Moon", "Waxing Crescent", "First Quarter",
            "Waxing Gibbous", "Full Moon", "Waning Gibbous",
            "Last Quarter", "Waning Crescent"

    Returns:
        Condition that checks if Moon phase matches any in the list
    """
    phases_lower = [p.lower() for p in phases]

    def check(chart: CalculatedChart) -> bool:
        moon = chart.get_object("Moon")
        if moon is None or moon.phase is None:
            return False
        return moon.phase.phase_name.lower() in phases_lower

    return _tag(check, SPEED_DAY)


# =============================================================================
# Void of Course Moon
# =============================================================================


def is_voc(mode: str = "traditional") -> Condition:
    """Moon is void of course.

    A void of course Moon has no major aspects before leaving its current sign.

    Args:
        mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)

    Returns:
        Condition that checks if Moon is void of course
    """
    from functools import partial

    from stellium.electional.intervals import voc_windows

    def check(chart: CalculatedChart) -> bool:
        voc_result = chart.voc_moon(aspects=mode)
        return voc_result.is_void

    condition = _tag(check, SPEED_HOUR)
    return _tag_windows(condition, partial(voc_windows, mode=mode))


def not_voc(mode: str = "traditional") -> Condition:
    """Moon is NOT void of course.

    Args:
        mode: "traditional" (Sun-Saturn) or "modern" (includes outer planets)

    Returns:
        Condition that checks Moon is NOT void of course
    """
    from functools import partial

    from stellium.electional.intervals import not_voc_windows

    def check(chart: CalculatedChart) -> bool:
        voc_result = chart.voc_moon(aspects=mode)
        return not voc_result.is_void

    condition = _tag(check, SPEED_HOUR)
    return _tag_windows(condition, partial(not_voc_windows, mode=mode))


# =============================================================================
# Sign Predicates
# =============================================================================


def sign_in(name: str, signs: list[str]) -> Condition:
    """Object is in one of the specified signs.

    Args:
        name: Object name (e.g., "Moon", "Sun", "Mars")
        signs: List of sign names (e.g., ["Aries", "Leo", "Sagittarius"])

    Returns:
        Condition that checks if object is in any of the signs
    """
    from functools import partial

    from stellium.electional.intervals import moon_sign_windows

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return False
        return obj.sign in signs

    condition = _tag(check, SPEED_DAY_SIGN)

    # Only attach window generator for Moon (fast-moving)
    if name.lower() == "moon":
        condition = _tag_windows(condition, partial(moon_sign_windows, signs))

    return condition


def sign_not_in(name: str, signs: list[str]) -> Condition:
    """Object is NOT in any of the specified signs.

    Args:
        name: Object name (e.g., "Moon", "Sun", "Mars")
        signs: List of sign names to exclude

    Returns:
        Condition that checks if object is NOT in any of the signs
    """
    from functools import partial

    from stellium.electional.intervals import moon_sign_not_in_windows

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return False
        return obj.sign not in signs

    condition = _tag(check, SPEED_DAY_SIGN)

    # Only attach window generator for Moon (fast-moving)
    if name.lower() == "moon":
        condition = _tag_windows(condition, partial(moon_sign_not_in_windows, signs))

    return condition


# =============================================================================
# House Predicates
# =============================================================================


def in_house(name: str, houses: list[int]) -> Condition:
    """Object is in one of the specified houses.

    Args:
        name: Object name (e.g., "Moon", "Jupiter")
        houses: List of house numbers (1-12)

    Returns:
        Condition that checks if object is in any of the houses
    """

    def check(chart: CalculatedChart) -> bool:
        house = chart.get_house(name)
        if house is None:
            return False
        return house in houses

    return _tag(check, SPEED_MINUTE)


def on_angle(name: str) -> Condition:
    """Object is angular (in houses 1, 4, 7, or 10).

    Angular houses are the most powerful positions in electional astrology.

    Args:
        name: Object name (e.g., "Jupiter", "Venus", "Moon")

    Returns:
        Condition that checks if object is in an angular house
    """
    return in_house(name, [1, 4, 7, 10])


def succedent(name: str) -> Condition:
    """Object is in a succedent house (2, 5, 8, 11).

    Args:
        name: Object name

    Returns:
        Condition that checks if object is in a succedent house
    """
    return in_house(name, [2, 5, 8, 11])


def cadent(name: str) -> Condition:
    """Object is in a cadent house (3, 6, 9, 12).

    Args:
        name: Object name

    Returns:
        Condition that checks if object is in a cadent house
    """
    return in_house(name, [3, 6, 9, 12])


def not_in_house(name: str, houses: list[int]) -> Condition:
    """Object is NOT in any of the specified houses.

    Args:
        name: Object name
        houses: List of house numbers to avoid

    Returns:
        Condition that checks if object is NOT in any of the houses
    """

    def check(chart: CalculatedChart) -> bool:
        house = chart.get_house(name)
        if house is None:
            return True  # If no house data, consider it "not in" the bad houses
        return house not in houses

    return _tag(check, SPEED_MINUTE)


# =============================================================================
# Retrograde Predicates
# =============================================================================


def is_retrograde(name: str) -> Condition:
    """Planet is retrograde.

    Args:
        name: Planet name (e.g., "Mercury", "Venus", "Mars")

    Returns:
        Condition that checks if planet is retrograde
    """
    from functools import partial

    from stellium.electional.intervals import retrograde_windows

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return False
        return obj.is_retrograde

    condition = _tag(check, SPEED_DAY)
    return _tag_windows(condition, partial(retrograde_windows, name))


def not_retrograde(name: str) -> Condition:
    """Planet is NOT retrograde (direct motion).

    Args:
        name: Planet name (e.g., "Mercury", "Venus", "Mars")

    Returns:
        Condition that checks if planet is NOT retrograde
    """
    from functools import partial

    from stellium.electional.intervals import direct_windows

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return True  # If object doesn't exist, not retrograde
        return not obj.is_retrograde

    condition = _tag(check, SPEED_DAY)
    return _tag_windows(condition, partial(direct_windows, name))


# =============================================================================
# Dignity Predicates
# =============================================================================


def is_dignified(
    name: str,
    dignities: list[str] | None = None,
    system: str = "traditional",
) -> Condition:
    """Planet has essential dignity.

    Essential dignity means the planet is strengthened by its sign position:
    - ruler: Planet rules the sign (e.g., Mars in Aries)
    - exaltation: Planet is exalted (e.g., Sun in Aries)
    - triplicity: Planet rules the element (depends on sect)
    - bound/term: Planet rules the degree range
    - decan/face: Planet rules the 10° section

    Args:
        name: Planet name
        dignities: List of dignity types to check. If None, checks for
            major dignities (ruler or exaltation)
        system: "traditional" or "modern" dignity system

    Returns:
        Condition that checks if planet has specified dignities
    """

    def check(chart: CalculatedChart) -> bool:
        try:
            dig_data = chart.get_planet_dignity(name, system=system)
        except Exception:
            return False

        if dig_data is None:
            return False

        if dignities is None:
            # Check for any major dignity
            return dig_data.get("ruler", False) or dig_data.get("exaltation", False)

        return any(dig_data.get(d, False) for d in dignities)

    return _tag(check, SPEED_DAY_SIGN)


def is_debilitated(
    name: str,
    debilities: list[str] | None = None,
    system: str = "traditional",
) -> Condition:
    """Planet is debilitated (in detriment or fall).

    Args:
        name: Planet name
        debilities: List of debility types to check ["detriment", "fall"].
            If None, checks for either.
        system: "traditional" or "modern" dignity system

    Returns:
        Condition that checks if planet is debilitated
    """

    def check(chart: CalculatedChart) -> bool:
        try:
            dig_data = chart.get_planet_dignity(name, system=system)
        except Exception:
            return False

        if dig_data is None:
            return False

        if debilities is None:
            return dig_data.get("detriment", False) or dig_data.get("fall", False)

        return any(dig_data.get(d, False) for d in debilities)

    return _tag(check, SPEED_DAY_SIGN)


def not_debilitated(name: str, system: str = "traditional") -> Condition:
    """Planet is NOT in detriment or fall.

    Args:
        name: Planet name
        system: "traditional" or "modern" dignity system

    Returns:
        Condition that checks planet is NOT debilitated
    """

    def check(chart: CalculatedChart) -> bool:
        try:
            dig_data = chart.get_planet_dignity(name, system=system)
        except Exception:
            return True  # If no data, assume not debilitated

        if dig_data is None:
            return True

        return not (dig_data.get("detriment", False) or dig_data.get("fall", False))

    return _tag(check, SPEED_DAY_SIGN)


# =============================================================================
# Aspect Predicates
# =============================================================================


def aspect_applying(
    obj1: str,
    obj2: str,
    aspects: list[str] | None = None,
    orb_max: float | None = None,
) -> Condition:
    """Applying aspect between two objects.

    An applying aspect is getting tighter (objects moving toward exact aspect).

    Args:
        obj1: First object name
        obj2: Second object name
        aspects: List of aspect types (e.g., ["conjunction", "trine", "sextile"]).
            If None, matches any aspect type.
        orb_max: Maximum orb in degrees. If None, uses default orbs.

    Returns:
        Condition that checks for applying aspect between the objects
    """
    aspects_lower = [a.lower() for a in aspects] if aspects else None

    def check(chart: CalculatedChart) -> bool:
        for asp in chart.aspects:
            names = {asp.object1.name, asp.object2.name}
            if obj1 not in names or obj2 not in names:
                continue

            # Check aspect type
            if aspects_lower and asp.aspect_name.lower() not in aspects_lower:
                continue

            # Check orb
            if orb_max is not None and asp.orb > orb_max:
                continue

            # Check if applying
            if asp.is_applying:
                return True

        return False

    return _tag(check, SPEED_HOUR)


def aspect_separating(
    obj1: str,
    obj2: str,
    aspects: list[str] | None = None,
    orb_max: float | None = None,
) -> Condition:
    """Separating aspect between two objects.

    A separating aspect is getting looser (objects moving away from exact aspect).

    Args:
        obj1: First object name
        obj2: Second object name
        aspects: List of aspect types. If None, matches any type.
        orb_max: Maximum orb in degrees.

    Returns:
        Condition that checks for separating aspect between the objects
    """
    aspects_lower = [a.lower() for a in aspects] if aspects else None

    def check(chart: CalculatedChart) -> bool:
        for asp in chart.aspects:
            names = {asp.object1.name, asp.object2.name}
            if obj1 not in names or obj2 not in names:
                continue

            if aspects_lower and asp.aspect_name.lower() not in aspects_lower:
                continue

            if orb_max is not None and asp.orb > orb_max:
                continue

            # Check if separating (not applying)
            if asp.is_applying is False:
                return True

        return False

    return _tag(check, SPEED_HOUR)


def has_aspect(
    obj1: str,
    obj2: str,
    aspects: list[str] | None = None,
    orb_max: float | None = None,
) -> Condition:
    """Objects are in aspect (regardless of applying/separating).

    Args:
        obj1: First object name
        obj2: Second object name
        aspects: List of aspect types. If None, matches any type.
        orb_max: Maximum orb in degrees.

    Returns:
        Condition that checks if objects are in aspect
    """
    aspects_lower = [a.lower() for a in aspects] if aspects else None

    def check(chart: CalculatedChart) -> bool:
        for asp in chart.aspects:
            names = {asp.object1.name, asp.object2.name}
            if obj1 not in names or obj2 not in names:
                continue

            if aspects_lower and asp.aspect_name.lower() not in aspects_lower:
                continue

            if orb_max is not None and asp.orb > orb_max:
                continue

            return True

        return False

    return _tag(check, SPEED_HOUR)


def no_aspect(
    obj1: str,
    obj2: str,
    aspects: list[str] | None = None,
    orb_max: float | None = None,
) -> Condition:
    """Objects are NOT in aspect.

    Args:
        obj1: First object name
        obj2: Second object name
        aspects: List of aspect types. If None, means no aspect at all.
        orb_max: Maximum orb to consider.

    Returns:
        Condition that checks if objects are NOT in aspect
    """
    has_the_aspect = has_aspect(obj1, obj2, aspects, orb_max)

    def check(chart: CalculatedChart) -> bool:
        return not has_the_aspect(chart)

    # Inherit speed from has_aspect (SPEED_HOUR)
    return _tag(check, SPEED_HOUR)


def no_hard_aspect(
    name: str,
    exclude_objects: list[str] | None = None,
    applying_only: bool = True,
) -> Condition:
    """Object has no hard aspects (square, opposition) from any planet.

    Hard aspects from malefics (Mars, Saturn) are particularly problematic
    in electional astrology.

    Args:
        name: Object name to check
        exclude_objects: Objects to ignore (e.g., ["Mars"] if Mars is dignified)
        applying_only: If True, only count applying aspects (default True)

    Returns:
        Condition that checks object has no hard aspects
    """
    exclude = exclude_objects or []
    hard_aspects = ["square", "opposition"]

    def check(chart: CalculatedChart) -> bool:
        for asp in chart.aspects:
            # Check if this aspect involves our object
            names = {asp.object1.name, asp.object2.name}
            if name not in names:
                continue

            # Get the other object
            other = (names - {name}).pop()
            if other in exclude:
                continue

            # Check if it's a hard aspect
            if asp.aspect_name.lower() not in hard_aspects:
                continue

            # Check if applying (if required)
            if applying_only and not asp.is_applying:
                continue

            # Found a hard aspect
            return False

        return True

    return _tag(check, SPEED_HOUR)


def no_malefic_aspect(name: str, applying_only: bool = True) -> Condition:
    """Object has no hard aspects from Mars or Saturn.

    Args:
        name: Object name to check
        applying_only: If True, only count applying aspects

    Returns:
        Condition that checks object has no Mars/Saturn hard aspects
    """
    hard_aspects = ["conjunction", "square", "opposition"]
    malefics = ["Mars", "Saturn"]

    def check(chart: CalculatedChart) -> bool:
        for asp in chart.aspects:
            names = {asp.object1.name, asp.object2.name}
            if name not in names:
                continue

            other = (names - {name}).pop()
            if other not in malefics:
                continue

            if asp.aspect_name.lower() not in hard_aspects:
                continue

            if applying_only and not asp.is_applying:
                continue

            return False

        return True

    return _tag(check, SPEED_HOUR)


# =============================================================================
# Combust Predicate
# =============================================================================


def is_combust(name: str, orb: float = 8.5) -> Condition:
    """Planet is combust (too close to the Sun).

    A combust planet is weakened by proximity to the Sun.

    Args:
        name: Planet name
        orb: Maximum degrees from Sun to consider combust (default 8.5)

    Returns:
        Condition that checks if planet is combust
    """

    def check(chart: CalculatedChart) -> bool:
        planet = chart.get_object(name)
        sun = chart.get_object("Sun")

        if planet is None or sun is None:
            return False

        # Calculate angular distance
        diff = abs(planet.longitude - sun.longitude)
        if diff > 180:
            diff = 360 - diff

        return diff <= orb

    return _tag(check, SPEED_DAY)


def not_combust(name: str, orb: float = 8.5) -> Condition:
    """Planet is NOT combust.

    Args:
        name: Planet name
        orb: Minimum degrees from Sun to NOT be combust

    Returns:
        Condition that checks if planet is NOT combust
    """

    def check(chart: CalculatedChart) -> bool:
        planet = chart.get_object(name)
        sun = chart.get_object("Sun")

        if planet is None or sun is None:
            return True

        diff = abs(planet.longitude - sun.longitude)
        if diff > 180:
            diff = 360 - diff

        return diff > orb

    return _tag(check, SPEED_DAY)


# =============================================================================
# Out of Bounds
# =============================================================================


def is_out_of_bounds(name: str) -> Condition:
    """Object is out of bounds (declination beyond ~23.4°).

    Out of bounds planets are considered to operate outside normal rules.

    Args:
        name: Object name

    Returns:
        Condition that checks if object is out of bounds
    """

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return False
        return obj.is_out_of_bounds

    return _tag(check, SPEED_DAY)


def not_out_of_bounds(name: str) -> Condition:
    """Object is NOT out of bounds.

    Args:
        name: Object name

    Returns:
        Condition that checks if object is NOT out of bounds
    """

    def check(chart: CalculatedChart) -> bool:
        obj = chart.get_object(name)
        if obj is None:
            return True
        return not obj.is_out_of_bounds

    return _tag(check, SPEED_DAY)


# =============================================================================
# Aspect Exactitude Predicates
# =============================================================================

# Aspect name to angle mapping
_ASPECT_ANGLES = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}


def aspect_exact_within(
    obj1: str,
    obj2: str,
    aspect: str,
    orb: float = 1.0,
) -> Condition:
    """Aspect between objects is within orb of exact.

    This predicate checks if two objects are within a tight orb of an exact
    aspect. Useful for finding moments near perfection of an aspect.

    Args:
        obj1: First object name (e.g., "Moon")
        obj2: Second object name (e.g., "Jupiter")
        aspect: Aspect name ("conjunction", "sextile", "square", "trine", "opposition")
        orb: Maximum orb from exact in degrees (default 1°)

    Returns:
        Condition that checks if aspect is within orb of exact

    Example:
        >>> # Find moments when Moon is within 0.5° of exact trine to Jupiter
        >>> search.where(aspect_exact_within("Moon", "Jupiter", "trine", orb=0.5))
    """
    from functools import partial

    from stellium.electional.intervals import aspect_exact_windows

    if aspect.lower() not in _ASPECT_ANGLES:
        raise ValueError(
            f"Unknown aspect: {aspect}. Must be one of {list(_ASPECT_ANGLES.keys())}"
        )

    aspect_angle = _ASPECT_ANGLES[aspect.lower()]

    def check(chart: CalculatedChart) -> bool:
        p1 = chart.get_object(obj1)
        p2 = chart.get_object(obj2)

        if p1 is None or p2 is None:
            return False

        # Calculate actual separation
        diff = abs(p2.longitude - p1.longitude)
        if diff > 180:
            diff = 360 - diff

        # Check if within orb of the aspect angle
        error = abs(diff - aspect_angle)
        return error <= orb

    condition = _tag(check, SPEED_HOUR)
    return _tag_windows(
        condition, partial(aspect_exact_windows, obj1, obj2, aspect_angle, orb=orb)
    )


# =============================================================================
# Angle at Longitude Predicates
# =============================================================================


def angle_at_degree(
    target_longitude: float,
    angle: str = "ASC",
    orb: float = 1.0,
) -> Condition:
    """Chart angle is within orb of a specific zodiac degree.

    This predicate checks if a chart angle (ASC, MC, DSC, IC) is within
    the specified orb of a target longitude. Useful for finding moments
    when specific degrees rise or culminate.

    Args:
        target_longitude: Target longitude in degrees (0-360)
        angle: Which angle ("ASC", "MC", "DSC", "IC")
        orb: Maximum orb in degrees (default 1°)

    Returns:
        Condition that checks if angle is within orb of target

    Example:
        >>> # Find moments when 0° Aries is rising
        >>> search.where(angle_at_degree(0.0, "ASC", orb=1.0))

        >>> # Find moments when 15° Leo is culminating
        >>> search.where(angle_at_degree(135.0, "MC", orb=0.5))
    """
    from functools import partial

    from stellium.electional.intervals import angle_at_longitude_windows

    target = target_longitude % 360

    def check(chart: CalculatedChart) -> bool:
        houses = chart.get_houses()
        if houses is None:
            return False

        # Get angle longitude from house cusps
        # ASC = House 1, MC = House 10, DSC = House 7, IC = House 4
        angle_upper = angle.upper()
        if angle_upper in ("ASC", "ASCENDANT"):
            angle_lon = houses.get_cusp(1)
        elif angle_upper in ("MC", "MIDHEAVEN"):
            angle_lon = houses.get_cusp(10)
        elif angle_upper in ("DSC", "DESCENDANT"):
            angle_lon = houses.get_cusp(7)
        elif angle_upper in ("IC", "IMUM COELI"):
            angle_lon = houses.get_cusp(4)
        else:
            return False

        # Calculate difference handling wraparound
        diff = abs(angle_lon - target)
        if diff > 180:
            diff = 360 - diff

        return diff <= orb

    # Create window generator with location from search context
    def make_window_gen(latitude: float, longitude: float):
        return partial(
            angle_at_longitude_windows, target, latitude, longitude, angle, orb=orb
        )

    # Tag with location-aware window generator
    condition = _tag(check, SPEED_MINUTE)
    condition._angle_window_params = (target, angle, orb)  # Store for later
    return condition


def star_on_angle(
    star_name: str,
    angle: str = "ASC",
    orb: float = 1.0,
) -> Condition:
    """Fixed star is conjunct a chart angle.

    This is a convenience wrapper around angle_at_degree() that looks up
    the star's current longitude and checks if the specified angle is
    within orb of it.

    Note: Fixed stars move very slowly (~50 arcseconds/year due to precession),
    so for practical purposes within a year search, the star's longitude
    is effectively constant.

    Args:
        star_name: Name of the fixed star (e.g., "Regulus", "Spica", "Algol")
        angle: Which angle ("ASC", "MC", "DSC", "IC")
        orb: Maximum orb in degrees (default 1°)

    Returns:
        Condition that checks if star is conjunct angle

    Example:
        >>> # Find moments when Regulus is rising
        >>> search.where(star_on_angle("Regulus", "ASC", orb=1.0))

        >>> # Find moments when Spica is culminating
        >>> search.where(star_on_angle("Spica", "MC", orb=0.5))
    """
    from stellium.core.registry import FIXED_STARS_REGISTRY
    from stellium.engines.fixed_stars import SwissEphemerisFixedStarsEngine

    if star_name not in FIXED_STARS_REGISTRY:
        available = list(FIXED_STARS_REGISTRY.keys())
        raise ValueError(
            f"Unknown star: {star_name}. Available stars: {available[:10]}..."
        )

    def check(chart: CalculatedChart) -> bool:
        # Get star position at chart time
        engine = SwissEphemerisFixedStarsEngine()
        stars = engine.calculate_stars(chart.datetime.julian_day, stars=[star_name])

        if not stars:
            return False

        star = stars[0]
        star_lon = star.longitude

        # Get angle longitude
        houses = chart.get_houses()
        if houses is None:
            return False

        angle_upper = angle.upper()
        if angle_upper in ("ASC", "ASCENDANT"):
            angle_lon = houses.get_cusp(1)
        elif angle_upper in ("MC", "MIDHEAVEN"):
            angle_lon = houses.get_cusp(10)
        elif angle_upper in ("DSC", "DESCENDANT"):
            angle_lon = houses.get_cusp(7)
        elif angle_upper in ("IC", "IMUM COELI"):
            angle_lon = houses.get_cusp(4)
        else:
            return False

        # Calculate difference handling wraparound
        diff = abs(angle_lon - star_lon)
        if diff > 180:
            diff = 360 - diff

        return diff <= orb

    condition = _tag(check, SPEED_MINUTE)
    condition._star_angle_params = (star_name, angle, orb)  # Store for later
    return condition


# =============================================================================
# Planetary Hour Predicates
# =============================================================================


def in_planetary_hour(planet: str) -> Condition:
    """Check if the current time is in a planetary hour ruled by the specified planet.

    Planetary hours are a traditional timing system where each hour of the day
    is ruled by one of the seven classical planets in Chaldean order.

    Args:
        planet: Planet name ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

    Returns:
        Condition that checks if current time is in that planet's hour

    Example:
        >>> # Find Jupiter hours (good for expansion, luck, legal matters)
        >>> search.where(in_planetary_hour("Jupiter"))

        >>> # Find Venus hours on Friday for love matters
        >>> search.where(in_planetary_hour("Venus"))
    """
    from stellium.electional.planetary_hours import (
        CHALDEAN_ORDER,
        get_planetary_hour_at_jd,
    )

    if planet not in CHALDEAN_ORDER:
        raise ValueError(f"Unknown planet: {planet}. Must be one of {CHALDEAN_ORDER}")

    def check(chart: CalculatedChart) -> bool:
        try:
            hour = get_planetary_hour_at_jd(
                chart.datetime.julian_day,
                chart.location.latitude,
                chart.location.longitude,
            )
            return hour.ruler == planet
        except ValueError:
            # Circumpolar sun or other issue
            return False

    # Planetary hours change roughly every hour (varies by season)
    condition = _tag(check, SPEED_HOUR)
    condition._planetary_hour_planet = planet  # Store for window generator
    return condition


__all__ = [
    # Speed hint constants and utilities
    "SPEED_DAY",
    "SPEED_DAY_SIGN",
    "SPEED_HOUR",
    "SPEED_MINUTE",
    "get_speed_hint",
    "get_window_generator",
    # Moon phase
    "is_waxing",
    "is_waning",
    "moon_phase",
    # VOC
    "is_voc",
    "not_voc",
    # Sign
    "sign_in",
    "sign_not_in",
    # House
    "in_house",
    "on_angle",
    "succedent",
    "cadent",
    "not_in_house",
    # Retrograde
    "is_retrograde",
    "not_retrograde",
    # Dignity
    "is_dignified",
    "is_debilitated",
    "not_debilitated",
    # Aspects
    "aspect_applying",
    "aspect_separating",
    "has_aspect",
    "no_aspect",
    "no_hard_aspect",
    "no_malefic_aspect",
    # Combust
    "is_combust",
    "not_combust",
    # Out of bounds
    "is_out_of_bounds",
    "not_out_of_bounds",
    # Aspect exactitude
    "aspect_exact_within",
    # Angle at longitude
    "angle_at_degree",
    "star_on_angle",
    # Planetary hours
    "in_planetary_hour",
]
