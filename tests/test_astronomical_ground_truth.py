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


# ===========================================================================
# 5. TRADITIONAL DOCTRINE — the tables must match the sources they claim
# ===========================================================================
#
# These are not opinions. Essential dignity is a documented scheme, and if our table
# disagrees with Dorotheus then our table is wrong. Verified against
# https://en.wikipedia.org/wiki/Triplicity and standard dignity tables.
#
# This layer already earned its keep: the Water triplicity had its day and night
# rulers SWAPPED (Mars by day, Venus by night). Fire, Earth and Air all matched
# Dorotheus exactly, so the table was plainly meant to be Dorothean and Water alone
# was reversed — which mis-assigned triplicity dignity for every water-sign planet
# in a day chart, and fed that error into almuten, sect analysis and length-of-life.


def test_domicile_rulers_match_the_traditional_scheme():
    """The seven classical planets rule twelve signs — the luminaries one each."""
    from stellium.engines.dignities import DIGNITIES

    expected = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter",
    }
    for sign, ruler in expected.items():
        assert DIGNITIES[sign]["traditional"]["ruler"] == ruler, sign


def test_a_sign_and_its_opposite_have_opposite_dignities():
    """A planet in domicile is in detriment in the opposite sign. Always."""
    from stellium.engines.dignities import DIGNITIES

    opposites = {
        "Aries": "Libra",
        "Taurus": "Scorpio",
        "Gemini": "Sagittarius",
        "Cancer": "Capricorn",
        "Leo": "Aquarius",
        "Virgo": "Pisces",
    }
    for sign, across in {**opposites, **{v: k for k, v in opposites.items()}}.items():
        ruler = DIGNITIES[sign]["traditional"]["ruler"]
        assert DIGNITIES[across]["traditional"]["detriment"] == ruler, (
            f"{ruler} rules {sign}, so it must be in detriment in {across}"
        )


def test_exaltations_and_falls_are_opposite():
    """A planet exalted in one sign is in fall in the sign across from it."""
    from stellium.engines.dignities import DIGNITIES

    expected_exaltations = {
        "Aries": ("Sun", 19),
        "Taurus": ("Moon", 3),
        "Cancer": ("Jupiter", 15),
        "Virgo": ("Mercury", 15),
        "Libra": ("Saturn", 21),
        "Capricorn": ("Mars", 28),
        "Pisces": ("Venus", 27),
    }
    opposite = {
        "Aries": "Libra",
        "Taurus": "Scorpio",
        "Cancer": "Capricorn",
        "Virgo": "Pisces",
        "Libra": "Aries",
        "Capricorn": "Cancer",
        "Pisces": "Virgo",
    }

    for sign, (planet, degree) in expected_exaltations.items():
        assert DIGNITIES[sign]["traditional"]["exaltation"] == planet, sign
        assert DIGNITIES[sign]["exaltation_degree"] == degree, sign
        assert DIGNITIES[opposite[sign]]["traditional"]["fall"] == planet, (
            f"{planet} is exalted in {sign}, so it falls in {opposite[sign]}"
        )


def test_triplicity_rulers_match_dorotheus():
    """The bug this layer was written to catch.

    Dorothean triplicity (Wikipedia, and every standard table):

        Fire   day Sun      night Jupiter  participating Saturn
        Earth  day Venus    night Moon     participating Mars
        Air    day Saturn   night Mercury  participating Jupiter
        Water  day Venus    night Mars     participating Moon

    Ours had Water reversed — Mars by day, Venus by night.
    """
    from stellium.engines.dignities import DIGNITIES

    expected = {
        "Fire": {"day": "Sun", "night": "Jupiter", "coop": "Saturn"},
        "Earth": {"day": "Venus", "night": "Moon", "coop": "Mars"},
        "Air": {"day": "Saturn", "night": "Mercury", "coop": "Jupiter"},
        "Water": {"day": "Venus", "night": "Mars", "coop": "Moon"},
    }
    for sign, data in DIGNITIES.items():
        assert data["triplicity"] == expected[data["element"]], sign


def test_every_sign_has_a_complete_set_of_egyptian_bounds():
    """Five bounds per sign, covering 0-30° with no gaps, and no luminaries."""
    from stellium.engines.dignities import DIGNITIES

    for sign, data in DIGNITIES.items():
        bounds = data["bound_egypt"]
        assert len(bounds) == 5, sign
        assert min(bounds) == 0, sign
        assert max(bounds) < 30, sign
        # The Sun and Moon never rule bounds — only the five non-luminaries do.
        assert set(bounds.values()) <= {
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
        }, sign
        assert len(set(bounds.values())) == 5, f"{sign} repeats a bound lord"


def test_dignity_scores_agree_with_the_tables():
    """A planet in its own sign must outscore the same planet in its detriment."""
    from stellium.core.models import CelestialPosition, ObjectType
    from stellium.engines.dignities import DIGNITIES, TraditionalDignityCalculator

    calculator = TraditionalDignityCalculator()

    def score(planet: str, longitude: float) -> int:
        position = CelestialPosition(
            name=planet,
            object_type=ObjectType.PLANET,
            longitude=longitude,
            latitude=0.0,
            distance=1.0,
        )
        return calculator.calculate_dignities(position, sect="day")["score"]

    signs = list(DIGNITIES)
    for sign_index, sign in enumerate(signs):
        traditional = DIGNITIES[sign]["traditional"]
        middle = sign_index * 30 + 15

        ruler = traditional["ruler"]
        if ruler in {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}:
            assert score(ruler, middle) > 0, f"{ruler} in its own {sign} scores <= 0"

        detriment = traditional["detriment"]
        if detriment in {
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
        }:
            assert score(detriment, middle) < 0, (
                f"{detriment} in detriment in {sign} scores >= 0"
            )


# ===========================================================================
# 6. CYCLES — the returns and the timelords keep known schedules
# ===========================================================================


def test_the_saturn_return_arrives_at_about_twenty_nine_and_a_half():
    """Saturn's orbit is 29.46 years, which is why the return lands around 29-30."""
    from stellium.returns import ReturnBuilder

    natal = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()
    saturn = natal.get_object("Saturn")

    # NOTE a trap: `occurrence=1` is not the Saturn return. Saturn can retrograde
    # back over its own natal degree within a year or two of birth, and that counts
    # as a crossing. The return proper — Saturn having gone all the way round — is a
    # later occurrence. So find the first crossing that is actually ~29 years out.
    ages = {}
    for occurrence in (1, 2, 3):
        chart = ReturnBuilder.planetary(
            natal, "Saturn", occurrence=occurrence
        ).calculate()
        ages[occurrence] = (
            chart.datetime.utc_datetime - natal.datetime.utc_datetime
        ).days / 365.25

    matured = [age for age in ages.values() if age > 20]
    assert matured, f"no Saturn crossing beyond age 20: {ages}"
    age = min(matured)
    assert 28.0 < age < 31.0, f"Saturn return at age {age:.1f} (all: {ages})"

    occurrence = next(k for k, v in ages.items() if v == age)
    first = ReturnBuilder.planetary(natal, "Saturn", occurrence=occurrence).calculate()
    returned = first.get_object("Saturn")
    gap = abs((returned.longitude - saturn.longitude + 180) % 360 - 180)
    assert gap < 0.1, f"Saturn is {gap:.2f}° from its natal place"


def test_the_jupiter_return_arrives_at_about_twelve():
    """Jupiter's orbit is 11.86 years."""
    from stellium.returns import ReturnBuilder

    natal = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()
    jupiter = natal.get_object("Jupiter")

    # Same trap as Saturn: an early occurrence can be a retrograde re-crossing.
    ages = {}
    for occurrence in (1, 2, 3):
        chart = ReturnBuilder.planetary(
            natal, "Jupiter", occurrence=occurrence
        ).calculate()
        ages[occurrence] = (
            chart.datetime.utc_datetime - natal.datetime.utc_datetime
        ).days / 365.25

    matured = [age for age in ages.values() if age > 8]
    assert matured, f"no Jupiter crossing beyond age 8: {ages}"
    age = min(matured)
    assert 11.0 < age < 13.0, f"Jupiter return at age {age:.1f} (all: {ages})"

    occurrence = next(k for k, v in ages.items() if v == age)
    first = ReturnBuilder.planetary(natal, "Jupiter", occurrence=occurrence).calculate()
    returned = first.get_object("Jupiter")
    gap = abs((returned.longitude - jupiter.longitude + 180) % 360 - 180)
    assert gap < 0.1


def test_the_solar_return_lands_on_the_birthday():
    """By definition: the Sun is back at its natal degree."""
    from stellium.returns import ReturnBuilder

    natal = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()
    sun = natal.get_object("Sun")

    solar = ReturnBuilder.solar(natal, year=2026).calculate()
    assert solar.datetime.utc_datetime.month == 5
    assert 14 <= solar.datetime.utc_datetime.day <= 16

    gap = abs((solar.get_object("Sun").longitude - sun.longitude + 180) % 360 - 180)
    assert gap < 0.01


def test_profections_cycle_every_twelve_years():
    """One sign per year of life, twelve signs — so age 0, 12, 24, 36 all profect
    to the 1st house, and the Lord of the Year repeats with them."""
    natal = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()

    for age in (0, 12, 24, 36, 48):
        result = natal.profection(age=age, include_monthly=False)
        assert result.profected_house == 1, f"age {age}"

    # Every age advances exactly one house.
    for age in range(0, 25):
        result = natal.profection(age=age, include_monthly=False)
        assert result.profected_house == (age % 12) + 1, f"age {age}"

    # And the same point in the cycle gives the same lord.
    assert (
        natal.profection(age=5, include_monthly=False).ruler
        == natal.profection(age=17, include_monthly=False).ruler
        == natal.profection(age=29, include_monthly=False).ruler
    )


# ===========================================================================
# 7. VOID-OF-COURSE — the definition, checked against the sky
# ===========================================================================


def test_void_of_course_means_no_more_aspects_before_the_moon_leaves_its_sign():
    """The definition, not the implementation.

    The Moon is void from its last Ptolemaic aspect to a visible planet until it
    changes sign. So during a VOC period the Moon must make NO further exact aspect
    to Sun-Saturn — and it must still be in the sign it started in.

    Note the sign is sampled strictly INSIDE the window. A void window is a closed
    interval whose endpoints are ingress instants, where the Moon sits exactly on a
    30° boundary and the sign index is a coin-flip on the last floating-point bit.
    """
    from stellium.electional.intervals import voc_windows
    from stellium.engines.search import _julian_day_to_datetime

    windows = voc_windows(datetime(2026, 1, 1), datetime(2026, 2, 1))
    assert windows, "January must contain void-of-course periods"

    visible = ("Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
    moon_id = SWISS_EPHEMERIS_IDS["Moon"]
    inside = 0.002  # ~3 minutes; the Moon moves ~0.03° — well clear of a boundary

    for window in windows[:6]:
        start_jd, end_jd = window.start_jd, window.end_jd

        # The Moon does not change sign mid-void: the ingress is what ENDS it.
        just_after_start = int(
            _get_position_and_speed(moon_id, start_jd + inside)[0] % 360 // 30
        )
        just_before_end = int(
            _get_position_and_speed(moon_id, end_jd - inside)[0] % 360 // 30
        )
        assert just_after_start == just_before_end, (
            f"the Moon changed sign during a void period starting "
            f"{_julian_day_to_datetime(start_jd):%Y-%m-%d %H:%M}"
        )

        # And it perfects no aspect while void.
        for planet in visible:
            for angle in (0.0, 60.0, 90.0, 120.0, 180.0):
                hits = find_all_aspect_exacts(
                    "Moon",
                    planet,
                    angle,
                    _julian_day_to_datetime(start_jd + 0.002),
                    _julian_day_to_datetime(end_jd - 0.002),
                )
                assert not hits, (
                    f"the Moon perfected {angle}° to {planet} at "
                    f"{hits[0].datetime_utc:%Y-%m-%d %H:%M}, during a period the "
                    f"engine calls void-of-course"
                )


def test_the_moon_enters_leo_on_2026_01_04_at_13_43_ut():
    """An almanac fact, to anchor the whole-sign void below.

    Cafe Astrology publishes this ingress at 8:43 AM ET — 13:43 UT.
    """
    from stellium.engines.search import find_all_sign_changes

    changes = find_all_sign_changes("Moon", datetime(2026, 1, 4), datetime(2026, 1, 5))
    leo = [c for c in changes if c.datetime_utc.day == 4]
    assert leo, "the Moon must enter a new sign on 2026-01-04"

    ingress = leo[0].datetime_utc
    assert ingress.hour == 13 and abs(ingress.minute - 43) <= 1, (
        f"published ingress is 13:43 UT; we say {ingress:%H:%M}"
    )


def test_a_whole_sign_void_is_possible_and_traditional_rules_produce_one():
    """The Moon's entire Leo passage of Jan 2026 is void under traditional rules.

    Not a bug — a consequence of the definition. Aspect targets from a single planet
    sit at 0/±60/±90/±120/180, a lattice with 60° holes in it. In January 2026 five of
    the six traditional planets are clustered in Capricorn, so their holes coincide,
    and the gap lands squarely on Leo: the Moon's last aspect (trine Saturn, 116.4°)
    perfects in Cancer, and the next (trine Mercury, 154.2°) waits until Virgo.

    The outer planets fill that hole, which is why the modern mode sees an ordinary
    few-hour void over the same passage — and why published tables (which use the
    outers) show a short one. Both are right; they are different definitions.

    This test exists so nobody "fixes" the long window away.
    """
    from stellium.electional.intervals import voc_windows

    leo_passage = (datetime(2026, 1, 4, 14, 0), datetime(2026, 1, 6, 16, 0))

    traditional = voc_windows(*leo_passage, mode="traditional")
    assert len(traditional) == 1, "the Leo passage is one unbroken traditional void"
    trad_hours = (traditional[0].end_jd - traditional[0].start_jd) * 24
    assert trad_hours > 24, (
        f"traditional rules must find a whole-sign void here, got {trad_hours:.1f}h"
    )

    modern = voc_windows(*leo_passage, mode="modern")
    modern_hours = sum((w.end_jd - w.start_jd) * 24 for w in modern)
    assert modern_hours < 12, (
        f"the outers fill the 60° gap, so the modern void is short; "
        f"got {modern_hours:.1f}h"
    )
    assert modern_hours < trad_hours, (
        "a modern void is a subset of the traditional one — more planets to aspect "
        "means the Moon's last aspect can only come later"
    )


# ===========================================================================
# 8. ASTEROID IDENTITY — are we even asking for the right rock?
# ===========================================================================
#
# Swiss Ephemeris addresses a numbered asteroid as MPC number + AST_OFFSET (10000),
# and it does not validate: ask for the wrong id and you get a different asteroid,
# computed perfectly, with no complaint. The registry once stored raw MPC numbers in
# a field named `swiss_ephemeris_id`, so requesting Eris's position asked swisseph
# for id 136199 -- which resolves to the file `s126199s.se1`, an entirely different
# body.
#
# There are also TWO conventions, and both are correct:
#   - Ceres, Pallas, Juno, Vesta, Chiron, Pholus use swisseph's BUILT-IN ids
#     (17, 18, 19, 20, 15, 16). NOT MPC + offset.
#   - Everything else is MPC + AST_OFFSET.
# Get that wrong for Hygiea (MPC 10) and id `10` is not an asteroid at all -- it is
# the Mean Node.
#
# The reference longitudes below are from NASA JPL Horizons (ObsEcLon: ecliptic-of-
# date longitude of the apparent position, with light-time, deflection and stellar
# aberration -- exactly what Swiss Ephemeris computes), for 2000-01-01 12:00 UT.
# Horizons shares no code with Swiss Ephemeris, so agreement means we are asking for
# the right body. Verified live at the time of writing; worst disagreement 2".

JPL_HORIZONS_2000_01_01 = {
    # name:        (swiss id, JPL ObsEcLon, what JPL says the body IS)
    "Ceres": (17, 184.4531, "1 Ceres"),
    "Pallas": (18, 134.0433, "2 Pallas"),
    "Juno": (19, 277.9961, "3 Juno"),
    "Vesta": (20, 245.9720, "4 Vesta"),
    "Chiron": (15, 251.6176, "2060 Chiron"),
    "Pholus": (16, 215.4913, "5145 Pholus"),
    "Hygiea": (10010, 227.8826, "10 Hygiea"),
    "Nessus": (17066, 272.9138, "7066 Nessus"),
    "Chariklo": (20199, 151.2472, "10199 Chariklo"),
    "Gonggong": (235088, 327.3093, "225088 Gonggong"),
    "Eris": (146199, 18.5913, "136199 Eris"),
    "Sedna": (100377, 45.3567, "90377 Sedna"),
    "Quaoar": (60000, 247.8631, "50000 Quaoar"),
    "Orcus": (100482, 141.5759, "90482 Orcus"),
    "Makemake": (146472, 166.3840, "136472 Makemake"),
    "Haumea": (146108, 187.5650, "136108 Haumea"),
    # The named asteroids — relationship and vocation work.
    "Psyche": (10016, 330.3347, "16 Psyche"),
    "Sappho": (10080, 247.9877, "80 Sappho"),
    "Pandora": (10055, 283.0135, "55 Pandora"),
    "Amor": (11221, 347.5330, "1221 Amor"),
    "Astraea": (10005, 218.6520, "5 Astraea"),
    "Hebe": (10006, 71.5224, "6 Hebe"),
    "Iris": (10007, 139.8471, "7 Iris"),
    "Flora": (10008, 259.2723, "8 Flora"),
    "Metis": (10009, 268.0995, "9 Metis"),
    "Fortuna": (10019, 226.2070, "19 Fortuna"),
    "Diana": (10078, 267.3357, "78 Diana"),
    "Hidalgo": (10944, 267.1750, "944 Hidalgo"),
    "Icarus": (11566, 283.0601, "1566 Icarus"),
    "Toro": (11685, 334.2433, "1685 Toro"),
    "Bacchus": (12063, 275.7490, "2063 Bacchus"),
}


@pytest.mark.parametrize(
    "body,swiss_id,jpl_longitude,jpl_identity",
    [(n, *v) for n, v in JPL_HORIZONS_2000_01_01.items()],
)
def test_the_registry_asks_swiss_ephemeris_for_the_right_asteroid(
    body, swiss_id, jpl_longitude, jpl_identity
):
    """The id in the registry must address the body the name claims.

    A wrong id does not raise -- it returns a different asteroid's position, and the
    only way to notice is to ask something outside Swiss Ephemeris entirely.
    """
    import swisseph as swe

    from stellium.core.registry import CELESTIAL_REGISTRY
    from stellium.data.paths import initialize_ephemeris

    assert CELESTIAL_REGISTRY[body].swiss_ephemeris_id == swiss_id, (
        f"{body}'s registry id changed; if that was deliberate, re-verify it against "
        f"JPL Horizons — it is supposed to be {jpl_identity}"
    )

    initialize_ephemeris()
    try:
        position, _ = swe.calc_ut(2451545.0, swiss_id, swe.FLG_SWIEPH)
    except Exception as exc:  # the .se1 file is a separate download
        pytest.skip(f"{body}: ephemeris file not installed ({exc})")

    error = abs((position[0] - jpl_longitude + 180) % 360 - 180)
    assert error < 0.01, (
        f"{body} (swiss id {swiss_id}) is at {position[0]:.4f}°, but JPL Horizons puts "
        f'{jpl_identity} at {jpl_longitude:.4f}° — a {error * 3600:.0f}" disagreement. '
        f"We are almost certainly computing a different asteroid."
    )
