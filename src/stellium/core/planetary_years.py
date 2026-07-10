"""Canonical planetary-period ("planetary years") tables.

The Hellenistic/Perso-Arabic "planetary years" are a shared primitive consumed
by several time-lord and length-of-life techniques, each in a different
*family*:

- **Least (minor) years** — Zodiacal Releasing sign-periods; Decennials.
- **Greater years** — length-of-life (alcocoden, angular); origin of the
  Capricorn/Aquarius ZR values.
- **Mean years** — length-of-life (alcocoden, succedent).
- **Greatest years** — mundane/dynastic spans; *genuinely contested* between
  authors (see ``GREATEST_YEARS_VARIANTS``).

Plus the **Firdaria** periods, which are a *separate* set — NOT the least years.

This module is pure data (zero stellium imports) so it is safe to import from
``core``, ``engines``, and ``components`` without cycles. Values and source
attribution are documented in
``docs/development/specs/HELLENISTIC_PERIODS_SPEC.md`` and the two verification
reports it cites.

Reliability tiers:

- Least / greater / mean: canonical, near-universal across the tradition.
- Greatest: contested — presented as attributed variants, with *no* default.
"""

from __future__ import annotations

# =============================================================================
# LEAST / MINOR years — canonical (Valens Anthology III/IV; Firmicus II.29).
# Sum = 129 (the basis of Decennials). Consumed by Zodiacal Releasing.
# =============================================================================

LEAST_YEARS: dict[str, int] = {
    "Sun": 19,
    "Moon": 25,
    "Mercury": 20,
    "Venus": 8,
    "Mars": 15,
    "Jupiter": 12,
    "Saturn": 30,
}

# =============================================================================
# GREATER years — canonical. The five non-luminary values are the sum of each
# planet's Egyptian terms/bounds across the zodiac (Ptolemy Tetrabiblos I.20);
# they total 360 and are cross-checked against DIGNITIES[...]["bound_egypt"] in
# the test-suite. Luminaries rule no terms: Sun 120 (greatest solar semi-arc),
# Moon 108 (= 120 - ~12deg lunar visibility).
# =============================================================================

GREATER_YEARS: dict[str, int] = {
    "Sun": 120,
    "Moon": 108,
    "Saturn": 57,
    "Jupiter": 79,
    "Mars": 66,
    "Venus": 82,
    "Mercury": 76,
}

# =============================================================================
# MEAN / MIDDLE years — DERIVED, never hand-typed: (least + greater) / 2.
# Half-integer luminaries (Sun 69.5, Moon 66.5) per the alcocoden "Table of
# Years"; some popular tables round these, we keep the precise values.
# =============================================================================

MEAN_YEARS: dict[str, float] = {
    planet: (LEAST_YEARS[planet] + GREATER_YEARS[planet]) / 2 for planet in LEAST_YEARS
}

# =============================================================================
# GREATEST / MAXIMUM years — the least stable family; authors genuinely
# disagree. Presented as attributed variants with NO default. Chiefly used for
# mundane/dynastic timespans, not natal work.
# =============================================================================

GREATEST_YEARS_VARIANTS: dict[str, dict[str, int]] = {
    # De Vore, Encyclopedia of Astrology (widely reproduced table).
    "de_vore": {
        "Saturn": 465,
        "Jupiter": 428,
        "Mars": 264,
        "Sun": 1460,
        "Venus": 151,
        "Mercury": 450,
        "Moon": 320,
    },
    # Astronomical reconstruction (Neugebauer; Houlding/Skyscript): sidereal
    # period x "period number".
    "astronomical": {
        "Saturn": 265,
        "Jupiter": 427,
        "Mars": 284,
        "Sun": 1461,
        "Venus": 1151,
        "Mercury": 461,
        "Moon": 520,
    },
}

# The Moon's greatest year is the single most-contested figure in the tradition.
MOON_GREATEST_VARIANTS: dict[str, int] = {
    "antiochus_rhetorius": 25,  # clashes with the least-year 25
    "lilly": 320,
    "bonatti": 420,  # likely a transmission error
    "later_arabic": 520,  # Al-Qabisi / Al-Biruni / Ibn Ezra / astronomical
}

# =============================================================================
# FIRDARIA periods (years).  ***NOT the least years.***  Abu Ma'shar via Dykes,
# *Persian Nativities*. Seven planets = 70 yr; with the nodes = 75 yr, then the
# sequence returns to the sect light. Ordering is Chaldean-descending from the
# sect light, with the lunar nodes appended (their nocturnal placement is a
# documented fork — see FirdariaEngine).
# =============================================================================

FIRDARIA_YEARS: dict[str, int] = {
    "Sun": 10,
    "Venus": 8,
    "Mercury": 13,
    "Moon": 9,
    "Saturn": 11,
    "Jupiter": 12,
    "Mars": 7,
    "North Node": 3,
    "South Node": 2,
}

# Sect-dependent major-period order (seven planets; nodes appended by the engine
# per the chosen node placement). Undisputed across sources.
FIRDARIA_ORDER_DAY: list[str] = [
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars",
]
FIRDARIA_ORDER_NIGHT: list[str] = [
    "Moon",
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
]

# Descending Chaldean order (slowest to fastest), used to generate the 7 equal
# sub-periods starting from a major-period ruler.
CHALDEAN_ORDER: list[str] = [
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
]


# =============================================================================
# Accessors
# =============================================================================


def least_years(planet: str) -> int:
    """Least/minor years for a planet (ZR, Decennials)."""
    return LEAST_YEARS[planet]


def greater_years(planet: str) -> int:
    """Greater years for a planet (length-of-life, angular alcocoden)."""
    return GREATER_YEARS[planet]


def mean_years(planet: str) -> float:
    """Mean years for a planet — ``(least + greater) / 2`` (succedent alcocoden)."""
    return MEAN_YEARS[planet]


def firdaria_years(planet: str) -> int:
    """Firdaria period length in years (NOT the least years)."""
    return FIRDARIA_YEARS[planet]


def firdaria_order(sect: str) -> list[str]:
    """The seven-planet firdaria major-period order for a sect.

    Args:
        sect: ``"day"`` or ``"night"``.

    Returns:
        The planetary order (nodes are appended by the engine, per its node
        placement setting).
    """
    if sect == "day":
        return list(FIRDARIA_ORDER_DAY)
    if sect == "night":
        return list(FIRDARIA_ORDER_NIGHT)
    raise ValueError(f"sect must be 'day' or 'night', got {sect!r}")


def subperiod_order(major_ruler: str) -> list[str]:
    """The 7 sub-period rulers for a planetary major period.

    Descending Chaldean order starting from (and including) the major ruler,
    wrapping around — e.g. Sun -> Sun, Venus, Mercury, Moon, Saturn, Jupiter,
    Mars.

    Args:
        major_ruler: One of the seven planets (not a node — node majors do not
            subdivide in the classical scheme).

    Returns:
        Seven planet names.
    """
    start = CHALDEAN_ORDER.index(major_ruler)
    return [CHALDEAN_ORDER[(start + i) % 7] for i in range(7)]
