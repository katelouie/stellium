"""Tests for the canonical planetary-years primitive.

Pure-data tests (no ephemeris / chart calculation). The headline test is the
term-sum cross-check (``test_greater_years_match_egyptian_term_sums``): it
derives the non-luminary greater years from the dignity term data and asserts
they match, guarding transcription drift in *both* tables. See
``docs/development/specs/HELLENISTIC_PERIODS_SPEC.md``.
"""

from collections import defaultdict

import pytest

from stellium.core.planetary_years import (
    CHALDEAN_ORDER,
    FIRDARIA_ORDER_DAY,
    FIRDARIA_ORDER_NIGHT,
    FIRDARIA_YEARS,
    GREATER_YEARS,
    GREATEST_YEARS_VARIANTS,
    LEAST_YEARS,
    MEAN_YEARS,
    MOON_GREATEST_VARIANTS,
    firdaria_order,
    greater_years,
    least_years,
    mean_years,
    subperiod_order,
)

_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
_NON_LUMINARIES = ["Saturn", "Jupiter", "Mars", "Venus", "Mercury"]


# === Least years ============================================================


def test_least_years_canonical_values():
    assert LEAST_YEARS == {
        "Sun": 19,
        "Moon": 25,
        "Mercury": 20,
        "Venus": 8,
        "Mars": 15,
        "Jupiter": 12,
        "Saturn": 30,
    }


def test_least_years_sum_is_129():
    """The Decennials total."""
    assert sum(LEAST_YEARS.values()) == 129


# === Greater years ==========================================================


def test_greater_years_canonical_values():
    assert GREATER_YEARS == {
        "Sun": 120,
        "Moon": 108,
        "Saturn": 57,
        "Jupiter": 79,
        "Mars": 66,
        "Venus": 82,
        "Mercury": 76,
    }


def test_greater_years_non_luminaries_sum_to_360():
    assert sum(GREATER_YEARS[p] for p in _NON_LUMINARIES) == 360


def test_greater_years_match_egyptian_term_sums():
    """Non-luminary greater years == sum of each planet's Egyptian terms.

    Ptolemy Tetrabiblos I.20: the greater years are the total degrees each
    planet rules by bound/term across the twelve signs. This ties the years
    table to DIGNITIES[...]["bound_egypt"] and permanently guards a
    transcription error in either — it is the test that caught the transposed
    Sagittarius terms.
    """
    from stellium.engines.dignities import DIGNITIES

    totals: dict[str, int] = defaultdict(int)
    for sign_data in DIGNITIES.values():
        bounds = sign_data["bound_egypt"]
        starts = sorted(bounds)
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else 30
            totals[bounds[start]] += end - start

    for planet in _NON_LUMINARIES:
        assert totals[planet] == GREATER_YEARS[planet], (
            f"{planet}: term-sum {totals[planet]} != greater years "
            f"{GREATER_YEARS[planet]} — a bound_egypt or GREATER_YEARS entry drifted"
        )
    # Luminaries rule no terms in this scheme.
    assert totals["Sun"] == 0
    assert totals["Moon"] == 0


# === Mean years =============================================================


def test_mean_years_are_derived_averages():
    for planet in _PLANETS:
        assert MEAN_YEARS[planet] == (LEAST_YEARS[planet] + GREATER_YEARS[planet]) / 2


def test_mean_years_half_integer_luminaries():
    assert MEAN_YEARS["Sun"] == 69.5
    assert MEAN_YEARS["Moon"] == 66.5


# === Greatest years (contested — variants, no default) ======================


def test_greatest_years_variants_present_and_distinct():
    de_vore = GREATEST_YEARS_VARIANTS["de_vore"]
    astro = GREATEST_YEARS_VARIANTS["astronomical"]
    assert set(de_vore) == set(_PLANETS)
    assert set(astro) == set(_PLANETS)
    # The two traditions genuinely disagree (e.g. Venus 151 vs 1151).
    assert de_vore != astro
    assert de_vore["Venus"] != astro["Venus"]


def test_moon_greatest_is_the_contested_figure():
    # Four distinct attested values, including the least-year clash at 25.
    assert MOON_GREATEST_VARIANTS["antiochus_rhetorius"] == 25
    assert set(MOON_GREATEST_VARIANTS.values()) == {25, 320, 420, 520}


# === Firdaria periods (a SEPARATE set) ======================================


def test_firdaria_years_values_and_sum():
    assert FIRDARIA_YEARS == {
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
    assert sum(FIRDARIA_YEARS.values()) == 75  # with nodes
    seven = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    assert sum(FIRDARIA_YEARS[p] for p in seven) == 70  # without nodes


def test_firdaria_periods_are_not_the_least_years():
    """A regression guard against the classic conflation."""
    assert FIRDARIA_YEARS["Sun"] != LEAST_YEARS["Sun"]  # 10 vs 19
    assert FIRDARIA_YEARS["Moon"] != LEAST_YEARS["Moon"]  # 9 vs 25
    assert FIRDARIA_YEARS["Saturn"] != LEAST_YEARS["Saturn"]  # 11 vs 30


def test_firdaria_order_by_sect():
    assert firdaria_order("day") == FIRDARIA_ORDER_DAY
    assert firdaria_order("night") == FIRDARIA_ORDER_NIGHT
    assert FIRDARIA_ORDER_DAY[0] == "Sun"
    assert FIRDARIA_ORDER_NIGHT[0] == "Moon"
    # Both are the same seven planets in Chaldean rotation.
    assert set(FIRDARIA_ORDER_DAY) == set(FIRDARIA_ORDER_NIGHT)


def test_firdaria_order_rejects_bad_sect():
    with pytest.raises(ValueError, match="day.*night"):
        firdaria_order("twilight")


# === Sub-period order =======================================================


def test_subperiod_order_starts_from_ruler_chaldean():
    assert subperiod_order("Sun") == [
        "Sun",
        "Venus",
        "Mercury",
        "Moon",
        "Saturn",
        "Jupiter",
        "Mars",
    ]


def test_subperiod_order_is_seven_unique_from_each_planet():
    for planet in CHALDEAN_ORDER:
        order = subperiod_order(planet)
        assert len(order) == 7
        assert set(order) == set(CHALDEAN_ORDER)
        assert order[0] == planet


# === Accessors ==============================================================


def test_accessors():
    assert least_years("Saturn") == 30
    assert greater_years("Saturn") == 57
    assert mean_years("Saturn") == 43.5
