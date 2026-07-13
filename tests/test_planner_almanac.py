"""Tests for the planner's year-level almanac.

The planner had no unit tests before the design-system revamp; these cover the
data layer the new front matter is built on.
"""

from datetime import date

import pytest

from stellium import ChartBuilder, Native
from stellium.engines.releasing import ZodiacalReleasingAnalyzer
from stellium.planner.almanac import (
    _signed_aspect_error,
    _wrap180,
    build_year_almanac,
    find_progressed_moon,
    find_retrogrades,
    find_zr_year,
    house_for_longitude,
)

YEAR_START = date(2026, 1, 1)
YEAR_END = date(2026, 12, 31)
TZ = "America/Los_Angeles"


@pytest.fixture(scope="module")
def natal_chart():
    """A natal chart with the ZR analyzer, as the planner builds it."""
    native = Native("1990-05-15 14:30", "San Francisco, CA")
    return (
        ChartBuilder.from_native(native)
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
        .calculate()
    )


@pytest.fixture(scope="module")
def almanac(natal_chart):
    return build_year_almanac(natal_chart, YEAR_START, YEAR_END, TZ)


# ---------------------------------------------------------------------------
# pure logic (no ephemeris)
# ---------------------------------------------------------------------------


def test_wrap180_folds_into_signed_half_circle():
    assert _wrap180(0) == 0
    assert _wrap180(190) == -170
    assert _wrap180(-190) == 170
    assert _wrap180(360) == 0


def test_signed_aspect_error_is_zero_at_exact_aspect():
    # A body at 100° is exactly square a natal point at 10°.
    assert _signed_aspect_error(100.0, 10.0, 90) == pytest.approx(0.0, abs=1e-9)
    # And exactly conjunct a natal point at 100°.
    assert _signed_aspect_error(100.0, 100.0, 0) == pytest.approx(0.0, abs=1e-9)


def test_signed_aspect_error_changes_sign_across_exactness():
    """The sign flip is what makes crossings detectable between samples."""
    before = _signed_aspect_error(99.5, 10.0, 90)
    after = _signed_aspect_error(100.5, 10.0, 90)
    assert before < 0 < after


def test_signed_aspect_error_handles_zodiac_wraparound():
    # 5° Aries is exactly trine 245° — the aspect wraps past 0°.
    assert _signed_aspect_error(5.0, 245.0, 120) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# ephemeris-backed
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_house_for_longitude_covers_the_whole_circle(natal_chart):
    """Every degree of the zodiac lands in exactly one house."""
    for longitude in range(0, 360, 7):
        house = house_for_longitude(natal_chart, float(longitude))
        assert house is not None
        assert 1 <= house <= 12


@pytest.mark.slow
def test_house_for_longitude_matches_a_known_planet(natal_chart):
    """Placing the Sun's own longitude must reproduce the Sun's house."""
    sun = natal_chart.get_object("Sun")
    assert house_for_longitude(natal_chart, sun.longitude) == natal_chart.get_house(
        "Sun"
    )


@pytest.mark.slow
def test_lord_of_the_year_from_profection(almanac):
    """Age 35 profects to the 12th house; in this chart that is Leo, ruled by the Sun."""
    assert almanac.age == 35
    assert almanac.profected_house == 12
    assert almanac.profected_sign == "Leo"
    assert almanac.lord_of_year == "Sun"


@pytest.mark.slow
def test_progressed_moon_changes_sign_at_most_once_per_year(almanac):
    """The core astronomical invariant.

    Secondary progression is one day per year of life and the Moon moves ~13°/day,
    so the progressed Moon covers only ~13° in a year — it cannot cross more than
    one sign boundary. A regression here means the progression time-map is wrong.
    """
    pm = almanac.progressed_moon
    assert pm is not None

    travelled = (
        pm.end_degree + 30 if pm.end_sign != pm.start_sign else pm.end_degree
    ) - pm.start_degree
    assert 8.0 < travelled < 20.0, f"progressed Moon moved {travelled:.1f}° in a year"

    # At most one ingress, and if there is one it must fall inside the year.
    if pm.ingress_date is not None:
        assert YEAR_START <= pm.ingress_date <= YEAR_END
        assert pm.ingress_sign is not None


@pytest.mark.slow
def test_progressed_moon_aspects_fall_inside_the_year(almanac):
    pm = almanac.progressed_moon
    assert pm.aspects, "expected the progressed Moon to aspect natal planets"
    for aspect in pm.aspects:
        assert YEAR_START <= aspect.date <= YEAR_END


@pytest.mark.slow
def test_eclipses_are_placed_in_natal_houses(almanac):
    assert almanac.eclipses, "2026 has eclipses"
    for eclipse in almanac.eclipses:
        assert eclipse.eclipse_type in {"solar", "lunar"}
        assert YEAR_START <= eclipse.date <= YEAR_END
        assert eclipse.natal_house is not None
        assert 1 <= eclipse.natal_house <= 12
        assert 0.0 <= eclipse.degree < 30.0


@pytest.mark.slow
def test_finds_the_2026_february_solar_eclipse(almanac):
    """A real-world anchor: there is a solar eclipse in mid-February 2026."""
    february = [
        e
        for e in almanac.eclipses
        if e.eclipse_type == "solar" and e.date.month == 2 and e.date.year == 2026
    ]
    assert len(february) == 1


@pytest.mark.slow
def test_retrograde_windows_are_ordered_and_overlap_the_year():
    periods = find_retrogrades(YEAR_START, YEAR_END, TZ)
    assert periods

    for period in periods:
        # Every reported window must actually intersect the year.
        if period.station_retrograde and period.station_direct:
            assert period.station_retrograde < period.station_direct
            assert not (
                period.station_direct < YEAR_START
                or period.station_retrograde > YEAR_END
            )


@pytest.mark.slow
def test_retrogrades_include_the_three_mercury_windows():
    """Mercury retrogrades three times in 2026 — a planner must show all three."""
    periods = find_retrogrades(YEAR_START, YEAR_END, TZ, planets=["Mercury"])
    assert len(periods) == 3


@pytest.mark.slow
def test_retrograde_straddling_the_year_boundary_is_flagged_not_dropped():
    """A retrograde that began in the previous year is still the reader's business."""
    periods = find_retrogrades(YEAR_START, YEAR_END, TZ)
    straddlers = [p for p in periods if p.starts_before_year or p.ends_after_year]
    assert straddlers, "expected at least one window crossing a year boundary"


@pytest.mark.slow
def test_zr_periods_require_the_analyzer_and_are_year_scoped(natal_chart, almanac):
    """ZR is read from analyzer metadata; a plain chart yields nothing, not a crash."""
    plain = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()
    assert find_zr_year(plain, YEAR_START, YEAR_END) == []

    # With the analyzer, the native is always inside some L1 period.
    assert almanac.zr_periods
    levels = {p.level for p in almanac.zr_periods}
    assert 1 in levels
    for period in almanac.zr_periods:
        assert period.start <= YEAR_END and period.end >= YEAR_START


@pytest.mark.slow
def test_transits_are_sorted_and_year_defining(almanac):
    assert almanac.transits
    times = [t.exact for t in almanac.transits]
    assert times == sorted(times)

    # Only the slow movers belong in a year summary.
    for transit in almanac.transits:
        assert transit.transit_planet in {
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        }


@pytest.mark.slow
def test_progressed_moon_handles_a_chart_with_no_ingress():
    """Most years the progressed Moon never leaves its sign; that is not a failure."""
    native = Native("1990-05-15 14:30", "San Francisco, CA")
    chart = ChartBuilder.from_native(native).calculate()

    # Some year is guaranteed to have no ingress, since a sign takes ~2.3 years.
    no_ingress = [
        find_progressed_moon(chart, date(y, 1, 1), date(y, 12, 31))
        for y in (2026, 2027, 2028)
    ]
    assert any(pm is not None and pm.ingress_date is None for pm in no_ingress)


@pytest.mark.slow
def test_solar_return_lands_near_the_birthday(almanac):
    assert almanac.solar_return is not None
    assert almanac.solar_return.month == 5
    assert 13 <= almanac.solar_return.day <= 17


@pytest.mark.slow
def test_almanac_datetime_access_does_not_assume_a_native_attribute():
    """Regression: CalculatedChart has no `.native` — birth data lives on .datetime."""
    chart = ChartBuilder.from_native(
        Native("1990-05-15 14:30", "San Francisco, CA")
    ).calculate()
    assert not hasattr(chart, "native")
    # Must still build without touching a `.native` attribute.
    almanac = build_year_almanac(chart, YEAR_START, YEAR_END, TZ)
    assert almanac.age == 35


# ---------------------------------------------------------------------------
# glyphs (derived from the registries, not hand-maintained)
# ---------------------------------------------------------------------------


def test_aspect_glyphs_by_angle_exclude_declination_aspects():
    """Regression: Parallel sits at 0° and Contraparallel at 180°.

    Both live in ASPECT_REGISTRY alongside Conjunction (0°) and Opposition (180°),
    so an angle-keyed map built over the *whole* registry silently replaces ☌ with
    ∥ and ☍ with ⋕ (last one wins). This map is built over ECLIPTIC_ASPECT_REGISTRY,
    where angle is a unique key — see TestAspectRegistryViews.
    """
    from stellium.planner.events import ASPECT_GLYPHS

    assert ASPECT_GLYPHS[0] == "☌"
    assert ASPECT_GLYPHS[180] == "☍"
    assert ASPECT_GLYPHS[90] == "□"
    assert ASPECT_GLYPHS[120] == "△"
    assert ASPECT_GLYPHS[60] == "⚹"


def test_sign_glyphs_have_no_variation_selector():
    """The registry's symbols carry U+FE0E; the calendar concatenates them inline."""
    from stellium.planner.events import SIGN_GLYPHS

    assert SIGN_GLYPHS["Aries"] == "♈"
    for glyph in SIGN_GLYPHS.values():
        assert "︎" not in glyph


def test_glyphs_are_derived_from_the_registry_not_a_hardcoded_dozen():
    """They used to be three hardcoded dicts, so an asteroid rendered as a letter."""
    from stellium.planner.events import ASPECT_GLYPHS_BY_NAME, PLANET_GLYPHS

    # The classic bodies still resolve...
    assert PLANET_GLYPHS["Sun"] == "☉"
    assert PLANET_GLYPHS["Pluto"] == "♇"
    # ...and so do bodies the old hardcoded dict never covered.
    assert PLANET_GLYPHS.get("Ceres")
    assert len(PLANET_GLYPHS) > 12

    assert ASPECT_GLYPHS_BY_NAME["Conjunction"] == "☌"
    assert ASPECT_GLYPHS_BY_NAME["Opposition"] == "☍"


# ---------------------------------------------------------------------------
# planner options (Honeycomb parity)
# ---------------------------------------------------------------------------


def test_period_label_does_not_call_a_september_range_a_year():
    """A planner need not be a calendar year — Honeycomb's run Sep→Aug."""
    from stellium.planner.contract import _period_label

    assert _period_label(date(2026, 1, 1), date(2026, 12, 31)) == "2026"
    assert _period_label(date(2026, 9, 1), date(2027, 8, 31)) == "Sep 2026 – Aug 2027"
    assert _period_label(date(2026, 6, 1), date(2026, 8, 31)) == "Jun–Aug 2026"
    assert _period_label(date(2026, 3, 1), date(2026, 3, 31)) == "March 2026"


def test_the_dashboard_is_not_called_a_year_when_it_is_a_month():
    """The dashboard hardcoded "The Year at a Glance" and a "%B %Y – %B %Y"
    descriptor, so a one-month planner announced "March 2026 – March 2026"."""
    from stellium.planner.contract import _span_descriptor

    assert _span_descriptor(date(2026, 3, 1), date(2026, 3, 31)) == "1 – 31 March 2026"
    assert (
        _span_descriptor(date(2026, 6, 1), date(2026, 8, 31))
        == "1 June – 31 August 2026"
    )
    assert (
        _span_descriptor(date(2026, 9, 1), date(2027, 8, 31))
        == "1 September 2026 – 31 August 2027"
    )


def test_no_front_matter_page_calls_a_one_month_planner_a_year(natal_chart):
    """The front matter used to be year-shaped in its wording: a March planner was
    headed "The Year at a Glance" and titled its panels "The Year", "The Year's
    Transits", "The Year's Charts". A planner's span is whatever you asked for.
    """
    from stellium.planner.almanac import build_year_almanac
    from stellium.planner.contract import build_planner_data

    start, end = date(2026, 3, 1), date(2026, 3, 31)
    almanac = build_year_almanac(natal_chart, start, end, TZ)

    data = build_planner_data(
        natal_chart,
        almanac,
        {},
        name="Test",
        theme="house",
    )

    assert data["meta"]["period"] == "March 2026"

    titles = [str(section.get("title", "")) for section in data["front"]]
    titles += [
        str(sub.get("title", ""))
        for section in data["front"]
        for sub in section.get("sections", [])
    ]

    offenders = [t for t in titles if "year" in t.lower()]
    assert not offenders, f"a one-month planner is calling itself a year: {offenders}"


def test_time_format_switches_between_12h_and_24h():
    from datetime import datetime

    from stellium.planner.contract import _fmt_time

    stamp = datetime(2026, 1, 1, 15, 16)
    assert _fmt_time(stamp, "12h") == "3:16p"
    assert _fmt_time(stamp, "24h") == "15:16"


def test_week_start_rotates_every_calendar_surface():
    """Both the month grid and the year-overview mini-months honour the week start.

    They reach `first_weekday` down separate paths, so a fix to one can silently
    leave the other Sunday-led — and a planner with a Monday month grid above
    Sunday-led mini-months just looks broken.
    """
    from stellium.planner.contract import (
        _weekday_initials,
        _weekday_names,
        _year_overview,
    )

    SUNDAY, MONDAY = 6, 0

    assert _weekday_names(SUNDAY)[0] == "Sun"
    assert _weekday_names(MONDAY)[0] == "Mon"
    assert _weekday_initials(SUNDAY) == ["S", "M", "T", "W", "T", "F", "S"]
    assert _weekday_initials(MONDAY) == ["M", "T", "W", "T", "F", "S", "S"]

    for first_weekday, expected in ((SUNDAY, "S"), (MONDAY, "M")):
        overview = _year_overview(
            date(2026, 3, 1), date(2026, 3, 31), {}, first_weekday
        )
        mini = overview["months"][0]
        assert mini["weekday_initials"][0] == expected


@pytest.mark.slow
def test_weekly_pages_can_start_on_a_different_day_than_the_month_grid(natal_chart):
    """A US reader often wants a Sunday-led month but a Monday-led working week."""
    from stellium.planner.contract import build_planner_data
    from stellium.planner.events import DailyEventCollector

    collector = DailyEventCollector(
        natal_chart=natal_chart, start=YEAR_START, end=YEAR_END, timezone=TZ
    )
    collector.collect_all()
    events: dict = {}
    for event in collector.get_all_events():
        events.setdefault(event.time.date(), []).append(event)

    almanac = build_year_almanac(natal_chart, YEAR_START, YEAR_END, TZ)
    data = build_planner_data(
        natal_chart,
        almanac,
        events,
        name="Test",
        theme="house",
        week_starts_on="sunday",
        weekly_starts_on="monday",
    )

    month = data["months"][0]
    assert month["weekdays"][0] == "Sun"
    assert month["weeks_detail"][0]["days"][0]["weekday"] == "Monday"


# ---------------------------------------------------------------------------
# the sky, annotated with what it touches in you
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_retrograde_shadow_brackets_the_retrograde(natal_chart):
    """The shadow is defined by the OTHER station's degree, not the station's own.

    Enters shadow: first passing the degree it will later station direct at.
    Leaves shadow: climbing back to the degree it stationed retrograde at.
    Using a station's own degree trivially returns the station's own date — which
    is exactly the bug this pins.
    """
    from stellium.planner.almanac import find_stations

    stations = find_stations(natal_chart, YEAR_START, YEAR_END, TZ, planets=["Mercury"])
    retrogrades = [s for s in stations if s.direction == "retrograde"]
    directs = [s for s in stations if s.direction == "direct"]
    assert retrogrades and directs

    for station in retrogrades:
        assert station.shadow_enter is not None
        assert station.shadow_enter < station.date, "shadow must precede the station"

    for station in directs:
        assert station.shadow_exit is not None
        assert station.shadow_exit > station.date, "shadow must outlast the station"


@pytest.mark.slow
def test_lunations_are_placed_in_houses_and_tag_eclipses(natal_chart):
    from stellium.planner.almanac import find_lunations

    lunations = find_lunations(natal_chart, YEAR_START, YEAR_END, TZ)
    # Roughly two per synodic month.
    assert 20 <= len(lunations) <= 30

    for lunation in lunations:
        assert lunation.phase in {"new", "full"}
        assert 1 <= (lunation.natal_house or 0) <= 12
        assert 0.0 <= lunation.degree < 30.0

    # 2026's eclipses must surface as tagged lunations, not as separate events.
    eclipses = [x for x in lunations if x.eclipse]
    assert len(eclipses) == 4


@pytest.mark.slow
def test_natal_contacts_respect_the_orb(natal_chart):
    from stellium.planner.almanac import CONTACT_ORB, find_lunations

    lunations = find_lunations(natal_chart, YEAR_START, YEAR_END, TZ)
    contacts = [c for lunation in lunations for c in lunation.natal_contacts]
    assert contacts
    for contact in contacts:
        assert contact.orb <= CONTACT_ORB


def test_contact_glyphs_lead_with_the_bodies_the_event_is_about():
    """Sorted by orb alone, slow outer planets crowd out the event's own bodies."""
    from stellium.planner.almanac import NatalContact
    from stellium.planner.contract import _contacts_glyphs

    contacts = [
        NatalContact("Saturn", "Moon", 60, "Sextile", 0.1),
        NatalContact("Mercury", "Sun", 60, "Sextile", 2.9),
    ]
    # By orb, Saturn's tighter aspect wins the single slot...
    assert _contacts_glyphs(contacts, limit=1).startswith("♄⚹☽")
    # ...but for a Mercury station, Mercury's own contact is what you came for.
    assert _contacts_glyphs(contacts, limit=1, focus=("Mercury",)).startswith("☿⚹☉")

    # Anything trimmed is counted, never silently dropped.
    assert _contacts_glyphs(contacts, limit=1).endswith("+1")


# ---------------------------------------------------------------------------
# traditional condition
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_chart_condition_reads_the_traditional_lords(natal_chart):
    from stellium.planner.almanac import find_chart_condition

    condition = find_chart_condition(natal_chart)

    # Sun above the horizon in the 9th → a day chart, with the day sect assignments.
    assert condition.sect.sect == "day"
    assert condition.sect.sect_light == "Sun"
    assert condition.sect.benefic_of_sect == "Jupiter"
    assert condition.sect.malefic_of_sect == "Saturn"

    by_name = {p.planet: p for p in condition.planets}

    # Saturn in its own Capricorn rules the ground it stands on.
    saturn = by_name["Saturn"]
    assert saturn.sign == "Capricorn"
    assert saturn.domicile_lord == "Saturn"
    assert saturn.score > 0

    # Jupiter is exalted in Cancer.
    assert by_name["Jupiter"].sign == "Cancer"
    assert "exaltation" in by_name["Jupiter"].dignities

    # Every planet gets bound, decan and triplicity lords.
    for planet in condition.planets:
        assert planet.bound_lord
        assert planet.decan_lord
        assert planet.triplicity_lords


@pytest.mark.slow
def test_absent_exaltation_lord_is_none_not_the_string_none(natal_chart):
    """Regression: DIGNITIES records "no exaltation" as the literal string "None".

    Aquarius, Leo, Gemini, Scorpio and Sagittarius have no traditional exaltation
    lord, but the table stores `"None"` — so a bare truthiness check prints "None"
    as though it were a planet.
    """
    from stellium.planner.almanac import find_chart_condition

    condition = find_chart_condition(natal_chart)
    moon = next(p for p in condition.planets if p.planet == "Moon")

    assert moon.sign == "Aquarius"
    assert moon.exaltation_lord is None  # not the string "None"

    for planet in condition.planets:
        assert planet.exaltation_lord != "None"
        assert planet.domicile_lord != "None"


def test_no_glibc_only_strftime_directives_anywhere_in_the_planner():
    """`%-d` and `%-I` are a **glibc extension**, not standard C.

    Windows rejects them outright — `ValueError: Invalid format string` — so a planner
    built there crashed while every test on Linux and macOS passed. Caught only by the
    CI matrix. There is no portable directive (Windows spells it `%#d`), so the fix is
    to format the parts by hand; this test makes sure nobody reintroduces one.
    """
    import inspect

    from stellium.planner import contract, events, renderer

    for module in (contract, events, renderer):
        source = inspect.getsource(module)
        for directive in ("%-d", "%-I", "%-m", "%-H", "%-j", "%-y"):
            # The module may *mention* one in a comment explaining why not to use it.
            offenders = [
                line
                for line in source.splitlines()
                if directive in line and not line.lstrip().startswith("#")
            ]
            assert not offenders, (
                f"{module.__name__} uses {directive!r}, which raises ValueError on "
                f"Windows:\n  " + "\n  ".join(offenders)
            )


def test_times_and_dates_format_without_leading_zeros():
    """The behaviour the glibc directives were there for, now done portably."""
    from datetime import datetime

    from stellium.planner.contract import _fmt_date, _fmt_datetime, _fmt_time

    assert _fmt_date(date(2026, 3, 3)) == "Mar 3"  # not "Mar 03"
    assert _fmt_time(datetime(2026, 1, 1, 14, 49)) == "2:49p"
    assert _fmt_time(datetime(2026, 1, 1, 9, 5)) == "9:05a"
    assert _fmt_time(datetime(2026, 1, 1, 14, 49), "24h") == "14:49"

    # Midnight is 12am and noon is 12pm — the classic 12-hour-clock off-by-twelve.
    assert _fmt_time(datetime(2026, 1, 1, 0, 30)) == "12:30a"
    assert _fmt_time(datetime(2026, 1, 1, 12, 30)) == "12:30p"

    assert _fmt_datetime(datetime(2026, 7, 15, 11, 19)) == "July 15, 2026 at 11:19 AM"
