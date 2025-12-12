"""
DataFrame conversion utilities for chart analysis.

Provides functions to convert CalculatedChart objects to pandas DataFrames
in various schemas optimized for different analysis use cases.

Requires pandas: pip install stellium[analysis]
"""

import hashlib
from collections.abc import Sequence
from typing import Any

from stellium.core.models import CalculatedChart, ObjectType

# Optional pandas import
try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None  # type: ignore


def _require_pandas() -> None:
    """Raise ImportError if pandas is not available."""
    if not PANDAS_AVAILABLE:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install with: pip install stellium[analysis]"
        )


def _generate_chart_id(chart: CalculatedChart) -> str:
    """Generate a unique ID for a chart based on datetime and location."""
    key = f"{chart.datetime.julian_day}:{chart.location.latitude}:{chart.location.longitude}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def _get_chart_name(chart: CalculatedChart) -> str:
    """Get the name from chart metadata."""
    return chart.metadata.get("name", "")


# Element and Modality mappings
SIGN_ELEMENTS = {
    "Aries": "fire",
    "Taurus": "earth",
    "Gemini": "air",
    "Cancer": "water",
    "Leo": "fire",
    "Virgo": "earth",
    "Libra": "air",
    "Scorpio": "water",
    "Sagittarius": "fire",
    "Capricorn": "earth",
    "Aquarius": "air",
    "Pisces": "water",
}

SIGN_MODALITIES = {
    "Aries": "cardinal",
    "Taurus": "fixed",
    "Gemini": "mutable",
    "Cancer": "cardinal",
    "Leo": "fixed",
    "Virgo": "mutable",
    "Libra": "cardinal",
    "Scorpio": "fixed",
    "Sagittarius": "mutable",
    "Capricorn": "cardinal",
    "Aquarius": "fixed",
    "Pisces": "mutable",
}


def _count_elements(chart: CalculatedChart) -> dict[str, int]:
    """Count planets in each element."""
    counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    planets = chart.get_planets()

    for planet in planets:
        element = SIGN_ELEMENTS.get(planet.sign)
        if element:
            counts[element] += 1

    return counts


def _count_modalities(chart: CalculatedChart) -> dict[str, int]:
    """Count planets in each modality."""
    counts = {"cardinal": 0, "fixed": 0, "mutable": 0}
    planets = chart.get_planets()

    for planet in planets:
        modality = SIGN_MODALITIES.get(planet.sign)
        if modality:
            counts[modality] += 1

    return counts


def _count_retrogrades(chart: CalculatedChart) -> int:
    """Count retrograde planets."""
    return sum(1 for p in chart.get_planets() if p.is_retrograde)


def _has_pattern(chart: CalculatedChart, pattern_name: str) -> bool:
    """Check if chart has a specific aspect pattern."""
    patterns = chart.metadata.get("aspect_patterns", [])
    for pattern in patterns:
        if isinstance(pattern, dict):
            if pattern.get("name", "").lower() == pattern_name.lower():
                return True
        elif hasattr(pattern, "name"):
            if pattern.name.lower() == pattern_name.lower():
                return True
    return False


def charts_to_dataframe(
    charts: Sequence[CalculatedChart],
    include_patterns: bool = True,
) -> "pd.DataFrame":
    """
    Convert charts to a DataFrame with one row per chart.

    This schema is best for:
    - Comparing charts across a dataset
    - Element/modality distribution analysis
    - Chart-wide pattern matching

    Args:
        charts: Sequence of CalculatedChart objects
        include_patterns: Include pattern detection columns (requires patterns in metadata)

    Returns:
        DataFrame with columns:
        - chart_id: Unique identifier
        - name: Chart name (from metadata)
        - datetime_utc: UTC datetime
        - julian_day: Julian day number
        - latitude, longitude: Location coordinates
        - location_name: Location name
        - sun_longitude, sun_sign, moon_longitude, moon_sign, moon_phase
        - asc_longitude, asc_sign, mc_longitude, mc_sign
        - fire_count, earth_count, air_count, water_count
        - cardinal_count, fixed_count, mutable_count
        - sect: "day" or "night"
        - retrograde_count: Number of retrograde planets
        - has_grand_trine, has_t_square, has_grand_cross (if include_patterns)

    Example::

        from stellium.analysis import BatchCalculator, charts_to_dataframe

        charts = BatchCalculator.from_registry(category="artist").calculate_all()
        df = charts_to_dataframe(charts)

        # Filter by sun sign
        aries_suns = df[df['sun_sign'] == 'Aries']
    """
    _require_pandas()

    records = []
    for chart in charts:
        record = _chart_to_record(chart, include_patterns)
        records.append(record)

    return pd.DataFrame(records)


def _chart_to_record(chart: CalculatedChart, include_patterns: bool) -> dict[str, Any]:
    """Convert a single chart to a flat record dict."""
    record: dict[str, Any] = {}

    # Chart identification
    record["chart_id"] = _generate_chart_id(chart)
    record["name"] = _get_chart_name(chart)

    # DateTime
    record["datetime_utc"] = chart.datetime.utc_datetime
    record["julian_day"] = chart.datetime.julian_day

    # Location
    record["latitude"] = chart.location.latitude
    record["longitude"] = chart.location.longitude
    record["location_name"] = chart.location.name or ""

    # Sun position
    sun = chart.get_object("Sun")
    if sun:
        record["sun_longitude"] = sun.longitude
        record["sun_sign"] = sun.sign
        record["sun_sign_degree"] = sun.sign_degree
    else:
        record["sun_longitude"] = None
        record["sun_sign"] = None
        record["sun_sign_degree"] = None

    # Moon position
    moon = chart.get_object("Moon")
    if moon:
        record["moon_longitude"] = moon.longitude
        record["moon_sign"] = moon.sign
        record["moon_sign_degree"] = moon.sign_degree
        # Moon phase (if available)
        if moon.phase:
            record["moon_phase"] = moon.phase.phase_name
            record["moon_illumination"] = moon.phase.illuminated_fraction
        else:
            record["moon_phase"] = None
            record["moon_illumination"] = None
    else:
        record["moon_longitude"] = None
        record["moon_sign"] = None
        record["moon_sign_degree"] = None
        record["moon_phase"] = None
        record["moon_illumination"] = None

    # Ascendant
    asc = chart.get_object("ASC")
    if asc:
        record["asc_longitude"] = asc.longitude
        record["asc_sign"] = asc.sign
    else:
        record["asc_longitude"] = None
        record["asc_sign"] = None

    # Midheaven
    mc = chart.get_object("MC")
    if mc:
        record["mc_longitude"] = mc.longitude
        record["mc_sign"] = mc.sign
    else:
        record["mc_longitude"] = None
        record["mc_sign"] = None

    # Element counts
    elements = _count_elements(chart)
    record["fire_count"] = elements["fire"]
    record["earth_count"] = elements["earth"]
    record["air_count"] = elements["air"]
    record["water_count"] = elements["water"]

    # Modality counts
    modalities = _count_modalities(chart)
    record["cardinal_count"] = modalities["cardinal"]
    record["fixed_count"] = modalities["fixed"]
    record["mutable_count"] = modalities["mutable"]

    # Sect
    record["sect"] = chart.sect()

    # Retrograde count
    record["retrograde_count"] = _count_retrogrades(chart)

    # Pattern detection (if requested)
    if include_patterns:
        record["has_grand_trine"] = _has_pattern(chart, "grand trine")
        record["has_t_square"] = _has_pattern(chart, "t-square")
        record["has_grand_cross"] = _has_pattern(chart, "grand cross")
        record["has_yod"] = _has_pattern(chart, "yod")
        record["has_stellium"] = _has_pattern(chart, "stellium")

    return record


def positions_to_dataframe(
    charts: Sequence[CalculatedChart],
    object_types: Sequence[ObjectType] | None = None,
) -> "pd.DataFrame":
    """
    Convert charts to a DataFrame with one row per celestial position.

    This schema is best for:
    - Position distributions across many charts
    - Sign/house analysis
    - Speed and retrograde analysis

    Args:
        charts: Sequence of CalculatedChart objects
        object_types: Filter to specific ObjectTypes (default: all)

    Returns:
        DataFrame with columns:
        - chart_id: Links to chart-level data
        - chart_name: Chart name
        - object_name: "Sun", "Moon", etc.
        - object_type: "planet", "angle", etc.
        - longitude: Ecliptic longitude (0-360)
        - latitude: Ecliptic latitude
        - sign: Zodiac sign
        - sign_degree: Degree within sign (0-30)
        - house: House placement (1-12, if available)
        - speed: Longitude speed (deg/day)
        - is_retrograde: Retrograde flag
        - declination: Declination (nullable)
        - is_out_of_bounds: OOB flag

    Example::

        from stellium.analysis import BatchCalculator, positions_to_dataframe

        charts = BatchCalculator.from_registry().calculate_all()
        df = positions_to_dataframe(charts)

        # Sun sign distribution
        sun_df = df[df['object_name'] == 'Sun']
        sun_df['sign'].value_counts()
    """
    _require_pandas()

    records = []
    for chart in charts:
        chart_id = _generate_chart_id(chart)
        chart_name = _get_chart_name(chart)

        # Get default house system for placements
        try:
            default_system = chart.default_house_system
            house_placements = chart.house_placements.get(default_system, {})
        except ValueError:
            house_placements = {}

        for pos in chart.positions:
            # Filter by object type if specified
            if object_types is not None and pos.object_type not in object_types:
                continue

            record: dict[str, Any] = {
                "chart_id": chart_id,
                "chart_name": chart_name,
                "object_name": pos.name,
                "object_type": pos.object_type.value,
                "longitude": pos.longitude,
                "latitude": pos.latitude,
                "sign": pos.sign,
                "sign_degree": pos.sign_degree,
                "house": house_placements.get(pos.name),
                "speed": pos.speed_longitude,
                "is_retrograde": pos.is_retrograde,
                "declination": pos.declination,
                "is_out_of_bounds": pos.is_out_of_bounds,
            }
            records.append(record)

    return pd.DataFrame(records)


def aspects_to_dataframe(
    charts: Sequence[CalculatedChart],
    include_declination: bool = False,
) -> "pd.DataFrame":
    """
    Convert charts to a DataFrame with one row per aspect.

    This schema is best for:
    - Aspect frequency analysis
    - Aspect pattern research
    - Orb distribution analysis

    Args:
        charts: Sequence of CalculatedChart objects
        include_declination: Include declination aspects (parallel/contraparallel)

    Returns:
        DataFrame with columns:
        - chart_id: Links to chart-level data
        - chart_name: Chart name
        - object1: First object name
        - object2: Second object name
        - aspect_name: "Conjunction", "Square", etc.
        - aspect_degree: 0, 60, 90, 120, 180, etc.
        - orb: Actual orb in degrees
        - is_applying: Applying vs separating
        - aspect_type: "longitude" or "declination"

    Example::

        from stellium.analysis import BatchCalculator, aspects_to_dataframe

        charts = BatchCalculator.from_registry().with_aspects().calculate_all()
        df = aspects_to_dataframe(charts)

        # Most common aspects
        df['aspect_name'].value_counts()

        # Sun-Moon aspects
        sun_moon = df[(df['object1'] == 'Sun') & (df['object2'] == 'Moon')]
    """
    _require_pandas()

    records = []
    for chart in charts:
        chart_id = _generate_chart_id(chart)
        chart_name = _get_chart_name(chart)

        # Regular (longitude) aspects
        for aspect in chart.aspects:
            record: dict[str, Any] = {
                "chart_id": chart_id,
                "chart_name": chart_name,
                "object1": aspect.object1.name,
                "object2": aspect.object2.name,
                "aspect_name": aspect.aspect_name,
                "aspect_degree": aspect.aspect_degree,
                "orb": aspect.orb,
                "is_applying": aspect.is_applying,
                "aspect_type": "longitude",
            }
            records.append(record)

        # Declination aspects (if requested)
        if include_declination:
            for aspect in chart.declination_aspects:
                record = {
                    "chart_id": chart_id,
                    "chart_name": chart_name,
                    "object1": aspect.object1.name,
                    "object2": aspect.object2.name,
                    "aspect_name": aspect.aspect_name,
                    "aspect_degree": aspect.aspect_degree,
                    "orb": aspect.orb,
                    "is_applying": aspect.is_applying,
                    "aspect_type": "declination",
                }
                records.append(record)

    return pd.DataFrame(records)


# Convenience aliases
to_chart_dataframe = charts_to_dataframe
to_positions_dataframe = positions_to_dataframe
to_aspects_dataframe = aspects_to_dataframe
