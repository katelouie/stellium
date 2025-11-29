"""Chart ruler calculation utilities.

The chart ruler is the planet that rules the Ascendant sign.
"""

from typing import Literal

from stellium.engines.dignities import DIGNITIES


def get_sign_ruler(
    sign: str,
    system: Literal["traditional", "modern"] = "traditional",
) -> str:
    """
    Get the planetary ruler of a zodiac sign.

    Args:
        sign: The zodiac sign name (e.g., "Aries", "Leo")
        system: "traditional" (classical rulerships) or "modern" (includes outer planets)

    Returns:
        The name of the ruling planet

    Example:
        >>> get_sign_ruler("Aries")
        'Mars'
        >>> get_sign_ruler("Scorpio", system="modern")
        'Pluto'
        >>> get_sign_ruler("Scorpio", system="traditional")
        'Mars'
    """
    if sign not in DIGNITIES:
        raise ValueError(f"Unknown sign: {sign}")

    return DIGNITIES[sign][system]["ruler"]


def get_chart_ruler(
    ascendant_sign: str,
    system: Literal["traditional", "modern"] = "traditional",
) -> str:
    """
    Get the chart ruler based on the Ascendant sign.

    The chart ruler is the planet that rules the rising sign.
    It is considered one of the most important planets in the natal chart.

    Args:
        ascendant_sign: The zodiac sign on the Ascendant (e.g., "Leo", "Scorpio")
        system: "traditional" (classical rulerships) or "modern" (includes outer planets)

    Returns:
        The name of the chart ruler planet

    Example:
        >>> get_chart_ruler("Leo")
        'Sun'
        >>> get_chart_ruler("Aquarius", system="modern")
        'Uranus'
        >>> get_chart_ruler("Aquarius", system="traditional")
        'Saturn'
    """
    return get_sign_ruler(ascendant_sign, system)


def get_chart_ruler_from_chart(
    chart,  # CalculatedChart - avoiding import for type hint to prevent circular imports
    system: Literal["traditional", "modern"] = "traditional",
) -> tuple[str, str]:
    """
    Get the chart ruler from a CalculatedChart object.

    Args:
        chart: A CalculatedChart instance
        system: "traditional" or "modern" rulership system

    Returns:
        A tuple of (ruler_planet_name, ascendant_sign)

    Example:
        >>> chart = ChartBuilder.from_notable("Kate Louie").calculate()
        >>> ruler, sign = get_chart_ruler_from_chart(chart)
        >>> print(f"Chart ruler: {ruler} (ruling {sign} rising)")
        Chart ruler: Sun (ruling Leo rising)
    """
    # Get the Ascendant from the chart
    asc = chart.get_object("ASC")
    if asc is None:
        raise ValueError("Chart does not contain an Ascendant")

    ascendant_sign = asc.sign
    ruler = get_chart_ruler(ascendant_sign, system)

    return (ruler, ascendant_sign)
