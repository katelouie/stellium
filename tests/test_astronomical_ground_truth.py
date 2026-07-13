"""Ground-truth tests: does the engine agree with the actual sky?

Most of our tests check that the code does what the code says. These check that it
says something *true*. The distinction is not academic — `find_aspect_exact` folded
its angle with `% 180`, so every opposition search silently became a conjunction
search, and it survived seven months because the tests covered 0°, 60° and 120° and
never 180°. It found *an* aspect and returned it under the requested name, so from
the inside it looked like it worked.

Nothing here trusts our own implementation. Each test appeals to something that is
true about the solar system whether or not Stellium exists:

1. IMPOSSIBILITIES  — geometry forbids it, so we must never report it
2. PERIODICITIES    — the sky repeats on known schedules, so counts are predictable
3. ALMANAC FACTS    — dated events anyone can look up
4. CROSS-ENGINE     — two independent code paths must agree with each other

The fourth is the most valuable and the cheapest to extend: when a bug hides in one
path, the other path is the oracle.
"""

from datetime import date, datetime

import pytest

from stellium import ChartBuilder, Native
from stellium.engines.search import (
    SWISS_EPHEMERIS_IDS,
    _get_position_and_speed,
    find_all_aspect_exacts,
    find_all_eclipses,
    find_all_sign_changes,
    find_all_stations,
)

pytestmark = pytest.mark.slow

YEAR_START = datetime(2026, 1, 1)
YEAR_END = datetime(2026, 12, 31)


def separation(name1: str, name2: str, julian_day: float) -> float:
    """True angular separation, straight from the ephemeris. Our oracle."""
    a, _ = _get_position_and_speed(SWISS_EPHEMERIS_IDS[name1], julian_day)
    b, _ = _get_position_and_speed(SWISS_EPHEMERIS_IDS[name2], julian_day)
    return abs((a - b + 180) % 360 - 180)


# ===========================================================================
# 1. IMPOSSIBILITIES — geometry forbids these, so we must never report them
# ===========================================================================
#
# The inner planets orbit *inside* Earth's orbit, so from here they can never get
# far from the Sun. Mercury reaches ~28° elongation, Venus ~47°. Every aspect wider
# than that is physically impossible, and an engine that reports one is inventing.


@pytest.mark.parametrize(
    "planet,max_elongation",
    [("Mercury", 28.0), ("Venus", 47.0)],
)
@pytest.mark.parametrize("angle", [60.0, 90.0, 120.0, 180.0])
def test_inner_planets_cannot_make_wide_aspects_to_the_sun(
    planet, max_elongation, angle
):
    if angle <= max_elongation:
        pytest.skip("within reach")

    hits = find_all_aspect_exacts("Sun", planet, angle, YEAR_START, YEAR_END)
    assert hits == [], (
        f"reported {len(hits)} Sun-{planet} aspects at {angle}°, but {planet} never "
        f"strays more than ~{max_elongation}° from the Sun"
    )


def test_the_sun_and_moon_never_retrograde():
    """Neither ever appears to move backwards from Earth.

    The engine refuses the question outright rather than quietly returning nothing,
    which is the better contract: asking for the Sun's stations is a mistake, not an
    empty result.
    """
    for body in ("Sun", "Moon"):
        with pytest.raises(ValueError, match="does not have stations"):
            find_all_stations(body, YEAR_START, YEAR_END)

    # And the ephemeris agrees: their speed is never negative.
    from stellium.engines.search import _datetime_to_julian_day

    start = _datetime_to_julian_day(YEAR_START)
    for body in ("Sun", "Moon"):
        object_id = SWISS_EPHEMERIS_IDS[body]
        for day in range(0, 365, 5):
            _, speed = _get_position_and_speed(object_id, start + day)
            assert speed > 0, f"{body} appears retrograde"


def test_inner_planet_elongation_never_exceeds_its_limit():
    """Sample the year and check the geometry directly."""
    from stellium.engines.search import _datetime_to_julian_day

    start = _datetime_to_julian_day(YEAR_START)
    for planet, limit in (("Mercury", 29.0), ("Venus", 48.0)):
        worst = max(separation("Sun", planet, start + day) for day in range(0, 365, 3))
        assert worst < limit, f"{planet} reached {worst:.1f}° elongation"


# ===========================================================================
# 2. PERIODICITIES — the sky repeats on schedules we know independently
# ===========================================================================


def test_a_year_holds_twelve_or_thirteen_lunations():
    """The synodic month is 29.53 days: 365.25 / 29.53 = 12.4."""
    new = find_all_aspect_exacts("Sun", "Moon", 0.0, YEAR_START, YEAR_END)
    full = find_all_aspect_exacts("Sun", "Moon", 180.0, YEAR_START, YEAR_END)
    assert 12 <= len(new) <= 13
    assert 12 <= len(full) <= 13


def test_each_outer_planet_opposes_the_sun_exactly_once_a_year():
    """Earth laps them, so opposition recurs a little over once per year."""
    for planet in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
        hits = find_all_aspect_exacts("Sun", planet, 180.0, YEAR_START, YEAR_END)
        assert len(hits) == 1, f"{planet}: {len(hits)} solar oppositions"
        assert abs(separation("Sun", planet, hits[0].julian_day) - 180.0) < 0.01


def test_mercury_retrogrades_three_or_four_times_a_year():
    """A well-known fact, and a good canary for the station search."""
    stations = find_all_stations("Mercury", YEAR_START, YEAR_END)
    retrogrades = [s for s in stations if s.station_type == "retrograde"]
    assert 3 <= len(retrogrades) <= 4


def test_the_sun_enters_all_twelve_signs_once_a_year():
    """And spends about a month in each."""
    ingresses = find_all_sign_changes("Sun", YEAR_START, YEAR_END)
    assert len(ingresses) == 12
    assert len({i.sign for i in ingresses}) == 12

    days = sorted(i.julian_day for i in ingresses)
    for earlier, later in zip(days, days[1:], strict=False):
        assert 28 <= (later - earlier) <= 32


def test_a_year_holds_between_four_and_seven_eclipses():
    """Two eclipse seasons a year, each with at least one solar and one lunar."""
    eclipses = find_all_eclipses(YEAR_START, YEAR_END)
    assert 4 <= len(eclipses) <= 7
    assert any(e.eclipse_type == "solar" for e in eclipses)
    assert any(e.eclipse_type == "lunar" for e in eclipses)


def test_the_moon_changes_sign_every_two_and_a_half_days():
    """It circles the zodiac in 27.3 days, so ~13 ingresses a month."""
    ingresses = find_all_sign_changes(
        "Moon", datetime(2026, 1, 1), datetime(2026, 2, 1)
    )
    assert 11 <= len(ingresses) <= 14


# ===========================================================================
# 3. ALMANAC FACTS — dated events anyone can look up
# ===========================================================================


def test_the_great_conjunction_of_2020():
    """Jupiter conjunct Saturn on 21 December 2020 — the closest since 1623."""
    hits = find_all_aspect_exacts(
        "Jupiter", "Saturn", 0.0, datetime(2020, 12, 1), datetime(2021, 1, 15)
    )
    assert len(hits) == 1
    assert hits[0].datetime_utc.date() == date(2020, 12, 21)


def test_the_great_american_eclipses():
    """21 Aug 2017 and 8 Apr 2024 — both total, both crossed the United States."""
    for when in (date(2017, 8, 21), date(2024, 4, 8)):
        found = find_all_eclipses(
            datetime(when.year, when.month, 1),
            datetime(when.year, when.month, 28),
        )
        solar = [e for e in found if e.eclipse_type == "solar"]
        assert any(e.datetime_utc.date() == when for e in solar), when


def test_the_august_2026_total_solar_eclipse():
    """12 August 2026 — totality over Iceland and Spain."""
    eclipses = find_all_eclipses(datetime(2026, 8, 1), datetime(2026, 8, 31))
    solar = [e for e in eclipses if e.eclipse_type == "solar"]
    assert len(solar) == 1
    assert solar[0].datetime_utc.date() == date(2026, 8, 12)


# ===========================================================================
# 4. CROSS-ENGINE AGREEMENT — two independent paths must tell the same story
# ===========================================================================
#
# The most valuable layer. Each of these computes the same fact two different ways;
# when a bug hides in one path, the other is the oracle.


def test_new_moons_agree_with_the_lunation_finder():
    """`Sun conjunct Moon` and the electional lunation search are the same event."""
    from stellium.electional.intervals import _find_all_lunations
    from stellium.engines.search import _datetime_to_julian_day

    by_aspect = {
        h.datetime_utc.date()
        for h in find_all_aspect_exacts("Sun", "Moon", 0.0, YEAR_START, YEAR_END)
    }
    by_lunation = {
        _julian_to_date(jd)
        for jd in _find_all_lunations(
            _datetime_to_julian_day(YEAR_START),
            _datetime_to_julian_day(YEAR_END),
            "new",
        )
    }
    assert by_aspect == by_lunation


def test_full_moons_agree_with_the_lunation_finder():
    """This one could not have passed before the opposition bug was fixed."""
    from stellium.electional.intervals import _find_all_lunations
    from stellium.engines.search import _datetime_to_julian_day

    by_aspect = {
        h.datetime_utc.date()
        for h in find_all_aspect_exacts("Sun", "Moon", 180.0, YEAR_START, YEAR_END)
    }
    by_lunation = {
        _julian_to_date(jd)
        for jd in _find_all_lunations(
            _datetime_to_julian_day(YEAR_START),
            _datetime_to_julian_day(YEAR_END),
            "full",
        )
    }
    assert by_aspect == by_lunation


def _julian_to_date(julian_day: float) -> date:
    from stellium.engines.search import _julian_day_to_datetime

    return _julian_day_to_datetime(julian_day).date()


def test_every_eclipse_falls_on_a_lunation():
    """A solar eclipse IS a new Moon; a lunar eclipse IS a full Moon. Always."""
    eclipses = find_all_eclipses(YEAR_START, YEAR_END)
    new = {
        h.datetime_utc.date()
        for h in find_all_aspect_exacts("Sun", "Moon", 0.0, YEAR_START, YEAR_END)
    }
    full = {
        h.datetime_utc.date()
        for h in find_all_aspect_exacts("Sun", "Moon", 180.0, YEAR_START, YEAR_END)
    }

    for eclipse in eclipses:
        when = eclipse.datetime_utc.date()
        expected = new if eclipse.eclipse_type == "solar" else full
        # Allow a day either side: the eclipse and the syzygy can straddle midnight.
        assert any(abs((when - d).days) <= 1 for d in expected), (
            f"{eclipse.eclipse_type} eclipse on {when} is not at a syzygy"
        )


def test_stations_agree_with_the_ephemeris_changing_direction():
    """A station is where speed crosses zero. Check the ephemeris directly."""
    for planet in ("Mercury", "Mars", "Saturn"):
        object_id = SWISS_EPHEMERIS_IDS[planet]
        for station in find_all_stations(planet, YEAR_START, YEAR_END):
            _, before = _get_position_and_speed(object_id, station.julian_day - 1.0)
            _, after = _get_position_and_speed(object_id, station.julian_day + 1.0)
            assert before * after < 0, (
                f"{planet} '{station.station_type}' station on "
                f"{station.datetime_utc:%Y-%m-%d} has speed {before:+.4f} before and "
                f"{after:+.4f} after — that is not a change of direction"
            )
            if station.station_type == "retrograde":
                assert before > 0 > after
            else:
                assert before < 0 < after


def test_ingresses_agree_with_the_ephemeris_crossing_a_sign_boundary():
    """A sign ingress is a longitude crossing a multiple of 30°."""
    for planet in ("Sun", "Mars", "Jupiter"):
        object_id = SWISS_EPHEMERIS_IDS[planet]
        for ingress in find_all_sign_changes(planet, YEAR_START, YEAR_END):
            longitude, _ = _get_position_and_speed(object_id, ingress.julian_day)
            degrees_into_sign = longitude % 30
            assert min(degrees_into_sign, 30 - degrees_into_sign) < 0.05, (
                f"{planet} 'entered {ingress.sign}' at {longitude % 30:.3f}° into a "
                f"sign — not a boundary"
            )


def test_every_exact_aspect_is_actually_exact():
    """The invariant the % 180 bug violated. Never report an aspect that isn't."""
    cases = [
        ("Sun", "Mars", 90.0),
        ("Sun", "Jupiter", 180.0),
        ("Venus", "Mars", 0.0),
        ("Jupiter", "Saturn", 120.0),
        ("Moon", "Saturn", 60.0),
        ("Mars", "Pluto", 90.0),
    ]
    for name1, name2, angle in cases:
        for hit in find_all_aspect_exacts(name1, name2, angle, YEAR_START, YEAR_END):
            actual = separation(name1, name2, hit.julian_day)
            assert abs(actual - angle) < 0.01, (
                f"{name1} {angle}° {name2} on {hit.datetime_utc:%Y-%m-%d}: the true "
                f"separation is {actual:.3f}°"
            )


def test_chart_aspects_agree_with_raw_longitudes():
    """Whatever the aspect engine reports must be visible in the longitudes."""
    chart = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()

    for aspect in chart.aspects:
        gap = abs(
            (aspect.object1.longitude - aspect.object2.longitude + 180) % 360 - 180
        )
        expected = aspect.aspect_degree
        assert abs(gap - expected) == pytest.approx(aspect.orb, abs=0.02), (
            f"{aspect.object1.name} {aspect.aspect_name} {aspect.object2.name}: "
            f"claimed orb {aspect.orb:.2f}° but the longitudes are {gap:.2f}° apart"
        )


def test_retrograde_flags_agree_with_speed():
    """`is_retrograde` must mean the body is actually moving backwards."""
    chart = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()

    for position in chart.get_planets():
        if position.speed_longitude is None:
            continue
        assert position.is_retrograde == (position.speed_longitude < 0), position.name


def test_a_planets_sign_agrees_with_its_longitude():
    """The most basic invariant in the library."""
    from stellium.core.registry import CELESTIAL_REGISTRY  # noqa: F401

    signs = [
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
    chart = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()

    for position in chart.positions:
        expected = signs[int(position.longitude % 360 // 30)]
        assert position.sign == expected, (
            f"{position.name} at {position.longitude:.2f}° is in {expected}, "
            f"not {position.sign}"
        )
