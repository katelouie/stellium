"""Void of Course Moon calculation engine.

The Moon is void of course (VOC) when it will not complete any major
(Ptolemaic) aspects before leaving its current sign. This is traditionally
considered an inauspicious time for beginning new ventures.

Traditional VOC uses only the seven visible planets (Sun through Saturn).
Modern VOC includes the outer planets (Uranus, Neptune, Pluto).

Example:
    >>> result = chart.voc_moon()
    >>> if result.is_void:
    ...     print(f"Moon is VOC until {result.void_until}")
    ... else:
    ...     print(f"Moon will {result.next_aspect} before leaving {result.moon_sign}")
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from stellium.engines.search import find_longitude_crossing

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart


# Ptolemaic aspect angles
PTOLEMAIC_ASPECTS = {
    0: "conjunction",
    60: "sextile",
    90: "square",
    120: "trine",
    180: "opposition",
}

# Planet sets for different modes
TRADITIONAL_PLANETS = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
MODERN_PLANETS = TRADITIONAL_PLANETS + ["Uranus", "Neptune", "Pluto"]

# Sign boundaries in longitude
SIGN_NAMES = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


@dataclass(frozen=True)
class VOCMoonResult:
    """Result of a void-of-course Moon calculation.

    Attributes:
        is_void: True if the Moon is currently void of course
        moon_longitude: Current Moon longitude in degrees
        moon_sign: Current zodiac sign of the Moon
        void_until: Datetime when the void period ends
        ends_by: How the void ends - "aspect" or "ingress"
        next_aspect: Description of next aspect (e.g., "trine Jupiter") or None
        next_aspect_degree: The aspect angle (0, 60, 90, 120, 180) or None
        next_planet: Name of planet Moon will next aspect, or None
        next_sign: The sign Moon will enter next
        ingress_time: Datetime when Moon enters the next sign
        aspect_mode: Which planet set was used ("traditional" or "modern")
    """

    is_void: bool
    moon_longitude: float
    moon_sign: str
    void_until: dt.datetime
    ends_by: Literal["aspect", "ingress"]
    next_aspect: str | None
    next_aspect_degree: int | None
    next_planet: str | None
    next_sign: str
    ingress_time: dt.datetime
    aspect_mode: str

    def __str__(self) -> str:
        if self.is_void:
            return (
                f"Moon is void of course in {self.moon_sign} "
                f"until {self.void_until.strftime('%Y-%m-%d %H:%M')} "
                f"(ingress to {self.next_sign})"
            )
        return (
            f"Moon in {self.moon_sign} will {self.next_aspect} "
            f"at {self.void_until.strftime('%Y-%m-%d %H:%M')}"
        )


def _get_next_sign_boundary(moon_longitude: float) -> tuple[float, str]:
    """Get the longitude of the next sign boundary and the sign name.

    Args:
        moon_longitude: Current Moon longitude (0-360)

    Returns:
        Tuple of (boundary_longitude, next_sign_name)
    """
    current_sign_index = int(moon_longitude // 30)
    next_sign_index = (current_sign_index + 1) % 12
    boundary = (current_sign_index + 1) * 30.0 % 360.0
    return boundary, SIGN_NAMES[next_sign_index]


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 range."""
    return longitude % 360.0


def calculate_voc_moon(
    chart: CalculatedChart,
    aspects: Literal["traditional", "modern"] = "traditional",
) -> VOCMoonResult:
    """Calculate void-of-course Moon status for a chart.

    The Moon is void of course when it will not perfect any major
    Ptolemaic aspect (conjunction, sextile, square, trine, opposition)
    to any planet before leaving its current sign.

    Args:
        chart: The calculated chart to analyze
        aspects: "traditional" (Sun-Saturn) or "modern" (includes outers)

    Returns:
        VOCMoonResult with void status and timing details

    Raises:
        ValueError: If Moon is not found in chart
    """
    # Get Moon position
    moon = chart.get_object("Moon")
    if moon is None:
        raise ValueError("Chart must contain Moon position")

    moon_longitude = moon.longitude
    moon_sign = moon.sign
    _chart_time = chart.datetime.utc_datetime
    julian_day = chart.datetime.julian_day

    # Determine which planets to check
    planets = TRADITIONAL_PLANETS if aspects == "traditional" else MODERN_PLANETS

    # Find when Moon enters next sign
    next_boundary, next_sign = _get_next_sign_boundary(moon_longitude)
    ingress_result = find_longitude_crossing(
        "Moon",
        next_boundary,
        julian_day,
        direction="forward",
        max_days=30.0,  # Moon takes ~2.5 days per sign max
    )

    if ingress_result is None:
        raise ValueError("Could not calculate Moon ingress time")

    ingress_time = ingress_result.datetime_utc

    # Check each planet for applying aspects
    earliest_aspect_time: dt.datetime | None = None
    earliest_aspect_name: str | None = None
    earliest_aspect_degree: int | None = None
    earliest_planet: str | None = None

    for planet_name in planets:
        planet = chart.get_object(planet_name)
        if planet is None:
            continue

        planet_longitude = planet.longitude

        # Check each Ptolemaic aspect
        for aspect_angle, aspect_name in PTOLEMAIC_ASPECTS.items():
            # Calculate target longitudes where this aspect would perfect
            # (planet_longitude + aspect_angle) and (planet_longitude - aspect_angle)
            targets = [
                _normalize_longitude(planet_longitude + aspect_angle),
                _normalize_longitude(planet_longitude - aspect_angle),
            ]

            # For conjunction (0°) and opposition (180°), only one target
            if aspect_angle == 0 or aspect_angle == 180:
                targets = [targets[0]]

            for target in targets:
                # Skip if target is behind the Moon (would require retrograde)
                # We need to check if Moon will reach this target going forward
                # before the ingress

                # Find when Moon reaches this target
                crossing = find_longitude_crossing(
                    "Moon",
                    target,
                    julian_day,
                    direction="forward",
                    max_days=30.0,
                )

                if crossing is None:
                    continue

                aspect_time = crossing.datetime_utc

                # Check if this aspect perfects before the ingress
                if aspect_time < ingress_time:
                    # This is a valid applying aspect
                    if (
                        earliest_aspect_time is None
                        or aspect_time < earliest_aspect_time
                    ):
                        earliest_aspect_time = aspect_time
                        earliest_aspect_name = f"{aspect_name} {planet_name}"
                        earliest_aspect_degree = aspect_angle
                        earliest_planet = planet_name

    # Determine VOC status
    if earliest_aspect_time is not None:
        # Moon will make an aspect before leaving the sign - NOT void
        return VOCMoonResult(
            is_void=False,
            moon_longitude=moon_longitude,
            moon_sign=moon_sign,
            void_until=earliest_aspect_time,
            ends_by="aspect",
            next_aspect=earliest_aspect_name,
            next_aspect_degree=earliest_aspect_degree,
            next_planet=earliest_planet,
            next_sign=next_sign,
            ingress_time=ingress_time,
            aspect_mode=aspects,
        )
    else:
        # No aspects before ingress - Moon IS void
        return VOCMoonResult(
            is_void=True,
            moon_longitude=moon_longitude,
            moon_sign=moon_sign,
            void_until=ingress_time,
            ends_by="ingress",
            next_aspect=None,
            next_aspect_degree=None,
            next_planet=None,
            next_sign=next_sign,
            ingress_time=ingress_time,
            aspect_mode=aspects,
        )
