"""End-to-end tests for the planner: builder → events → contract → PDF.

``test_planner_almanac.py`` covers the year-level data layer. Nothing covered the
rest of the pipeline, which is how every bug below shipped:

- the date range was searched as UTC days, not the reader's local days;
- the progressed Moon was progressed from the *local* birth time read as UTC;
- weeks straddling two months were printed twice;
- ``.without_progressed_chart()`` did nothing;
- the solar return printed in UTC, and for the wrong year on a Sep→Aug planner;
- a custom transit list flooded "Transits That Shape the Year";
- the void-of-course search invented a "VOC ends" at the range's last midnight;
- the New Moon glyph (🌑) is in no bundled font, so it printed as a box.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime

import pytest
import pytz

from stellium import ChartBuilder, Native
from stellium.planner import PlannerBuilder
from stellium.planner.almanac import (
    _natal_utc,
    find_progressed_moon,
    solar_return_year,
    utc_window,
)
from stellium.planner.contract import (
    _fmt_datetime,
    _month_weeks_detail,
    _period_label,
    _week_owner,
)
from stellium.planner.events import (
    MOON_PHASE_GLYPHS,
    DailyEventCollector,
)
from stellium.planner.renderer import PlannerRenderer, _timezone_label

EASTERN = "America/New_York"


@pytest.fixture(scope="module")
def native():
    return Native("1990-05-15 14:30", "San Francisco, CA", name="Test Native")


@pytest.fixture(scope="module")
def natal_chart(native):
    return ChartBuilder.from_native(native).calculate()


# ---------------------------------------------------------------------------
# pure logic (no ephemeris)
# ---------------------------------------------------------------------------


def test_utc_window_spans_local_midnight_to_midnight():
    # Tokyo is UTC+9: March 1st begins at 15:00 UTC on Feb 28th.
    start, end = utc_window(date(2026, 3, 1), date(2026, 3, 31), "Asia/Tokyo")
    assert start == datetime(2026, 2, 28, 15, 0)
    assert end.replace(microsecond=0) == datetime(2026, 3, 31, 14, 59, 59)
    assert start.tzinfo is None and end.tzinfo is None  # the engine wants naive UTC


def test_utc_window_follows_daylight_saving():
    # Eastern is UTC-5 in January and UTC-4 in July.
    jan, _ = utc_window(date(2026, 1, 1), date(2026, 1, 2), EASTERN)
    jul, _ = utc_window(date(2026, 7, 1), date(2026, 7, 2), EASTERN)
    assert jan == datetime(2026, 1, 1, 5, 0)
    assert jul == datetime(2026, 7, 1, 4, 0)


def test_week_owner_takes_the_month_with_most_in_range_days():
    cal = calendar.Calendar(firstweekday=6)
    # Sun Mar 29 – Sat Apr 4, 2026: three March days, four April days.
    week = next(w for w in cal.monthdatescalendar(2026, 3) if w[0] == date(2026, 3, 29))
    assert _week_owner(week, date(2026, 1, 1), date(2026, 12, 31)) == (2026, 4)
    # Clipped to a March-only planner, the week's in-range days are all March's.
    assert _week_owner(week, date(2026, 3, 1), date(2026, 3, 31)) == (2026, 3)
    # Wholly outside the range.
    assert _week_owner(week, date(2026, 6, 1), date(2026, 6, 30)) is None


@pytest.mark.parametrize("first_weekday", [6, 0])
def test_every_week_gets_exactly_one_weekly_page(first_weekday):
    start, end = date(2026, 1, 1), date(2026, 12, 31)
    labels = []
    for month in range(1, 13):
        labels += [
            page["label"]
            for page in _month_weeks_detail(2026, month, {}, first_weekday, start, end)
        ]
    assert len(labels) == len(set(labels)), "a straddling week was printed twice"
    # And none were lost: 2026's 365 days touch 53 calendar weeks either way.
    assert len(labels) == 53


def test_period_label_only_says_the_year_for_the_whole_year():
    assert _period_label(date(2026, 1, 1), date(2026, 12, 31)) == "2026"
    assert _period_label(date(2026, 1, 15), date(2026, 12, 10)) == "Jan–Dec 2026"
    assert _period_label(date(2026, 3, 1), date(2026, 3, 31)) == "March 2026"


def test_fmt_datetime_names_the_timezone():
    dt = pytz.timezone(EASTERN).localize(datetime(2026, 5, 15, 10, 33))
    assert _fmt_datetime(dt) == "May 15, 2026 at 10:33 AM EDT"
    assert _fmt_datetime(dt, "24h") == "May 15, 2026 at 10:33 EDT"


def test_timezone_label():
    assert _timezone_label(EASTERN) == "US Eastern"
    assert _timezone_label("Europe/London") == "Europe/London"
    assert _timezone_label("America/Argentina/Buenos_Aires") == (
        "America/Argentina/Buenos Aires"
    )


@pytest.mark.parametrize(
    "configure",
    [
        lambda b: b.theme("purple"),
        lambda b: b.timezone("Mars/Olympus"),
        lambda b: b.with_graphic_ephemeris(harmonic=7),
        lambda b: b.page_size("legal"),
        lambda b: b.week_starts_on("friday"),
        lambda b: b.weekly_starts_on("friday"),
        lambda b: b.time_format("military"),
        lambda b: b.include_voc("sidereal"),
        lambda b: b.binding_margin(-0.25),
    ],
)
def test_builder_rejects_bad_options_immediately(native, configure):
    with pytest.raises(ValueError):
        configure(PlannerBuilder.for_native(native))


def test_year_summary_stays_slow_even_with_a_custom_planet_list(native):
    builder = (
        PlannerBuilder.for_native(native)
        .year(2026)
        .timezone(EASTERN)
        .include_natal_transits(["Moon", "Mars", "Saturn"])
    )
    renderer = PlannerRenderer(builder._build_config())
    assert renderer._year_transit_planets() == ["Saturn"]


def test_builder_toggles_reach_the_config(native):
    config = (
        PlannerBuilder.for_native(native)
        .year(2026)
        .timezone(EASTERN)
        .exclude_natal_transits()
        .exclude_ingresses()
        .exclude_stations()
        .exclude_mundane_transits()
        .include_moon_phases(quarters=False)
        .include_eclipses(False)
        ._build_config()
    )
    assert not config.include_natal_transits
    assert not config.include_ingresses
    assert not config.include_stations
    assert not config.include_mundane_transits
    assert config.include_moon_phases and not config.include_quarter_moons
    assert not config.include_eclipses


def test_planner_glyphs_are_in_a_bundled_font():
    """Typst renders with system fonts off, so every symbol a daily cell can carry
    must exist in a font we ship — the old New Moon emoji did not."""
    pytest.importorskip("fontTools", reason="fontTools is needed to read font cmaps")
    from fontTools.ttLib import TTFont

    from stellium.planner.events import PLANET_GLYPHS, SIGN_GLYPHS
    from stellium.presentation.typst_runtime import font_paths

    covered: set[int] = set()
    for folder in font_paths():
        for path in __import__("pathlib").Path(folder).glob("*.[ot]tf"):
            covered |= set(TTFont(path, lazy=True).getBestCmap())

    symbols = list(MOON_PHASE_GLYPHS.values()) + ["☉", "☽", "∅"]
    symbols += [PLANET_GLYPHS[p] for p in ("Sun", "Moon", "Mercury", "Saturn")]
    symbols += list(SIGN_GLYPHS.values())
    missing = [s for s in symbols for ch in s if ord(ch) not in covered]
    assert not missing, f"no bundled font draws: {missing}"


# ---------------------------------------------------------------------------
# with the ephemeris
# ---------------------------------------------------------------------------


@pytest.mark.slow
@pytest.mark.parametrize("timezone", ["Asia/Tokyo", EASTERN, "America/Los_Angeles"])
def test_daily_events_stay_on_the_planners_local_days(natal_chart, timezone):
    collector = DailyEventCollector(
        natal_chart, date(2026, 3, 1), date(2026, 3, 31), timezone
    )
    collector.collect_all()
    events = collector.get_all_events()

    assert events
    assert all(date(2026, 3, 1) <= e.time.date() <= date(2026, 3, 31) for e in events)
    # The old VOC search clipped at the range edge and invented an event there.
    assert not [
        e
        for e in events
        if e.event_type.startswith("voc")
        and (e.time.hour, e.time.minute, e.time.second) == (0, 0, 0)
    ]


@pytest.mark.slow
def test_progressed_moon_is_progressed_from_utc_birth_time(natal_chart):
    """Day-for-a-year from the UTC birth moment, checked against Swiss Ephemeris."""
    import swisseph as swe

    from stellium.engines.search import _datetime_to_julian_day

    on = date(2026, 1, 1)
    birth_utc = _natal_utc(natal_chart)
    age_years = (datetime(2026, 1, 1, 12) - birth_utc).total_seconds() / (
        365.25 * 86400
    )
    jd = _datetime_to_julian_day(birth_utc) + age_years
    expected = swe.calc_ut(jd, swe.MOON)[0][0] % 360

    pm = find_progressed_moon(natal_chart, on, date(2026, 1, 2))
    sign_start = int(expected // 30) * 30
    got = sign_start + pm.start_degree
    # A 7-hour error (the old bug, for a California birth) is ~3.5°.
    assert got == pytest.approx(expected, abs=0.25)


@pytest.mark.slow
def test_solar_return_is_the_one_inside_the_range(natal_chart):
    # Born May 15. A Sep 2026 → Aug 2027 planner holds the May 2027 return.
    assert solar_return_year(natal_chart, date(2026, 9, 1), date(2027, 8, 31)) == 2027
    assert solar_return_year(natal_chart, date(2026, 1, 1), date(2026, 12, 31)) == 2026
    # No birthday inside a short range: the return already in force.
    assert solar_return_year(natal_chart, date(2026, 9, 1), date(2026, 10, 31)) == 2026
    assert solar_return_year(natal_chart, date(2026, 2, 1), date(2026, 3, 31)) == 2025


@pytest.mark.slow
def test_eclipses_replace_their_lunation_and_quarters_appear(natal_chart):
    collector = DailyEventCollector(
        natal_chart, date(2026, 8, 1), date(2026, 8, 31), EASTERN
    )
    collector.collect_all()
    days = {}
    for e in collector.get_all_events():
        days.setdefault(e.time.date(), []).append(e.description)

    eclipse_days = {d: ds for d, ds in days.items() if any("Eclipse" in x for x in ds)}
    assert eclipse_days, "August 2026 has two eclipses"
    for descriptions in eclipse_days.values():
        assert "New Moon" not in descriptions and "Full Moon" not in descriptions
        assert not any("(solar)" in x or "(lunar)" in x for x in descriptions)

    every = [x for ds in days.values() for x in ds]
    assert "First Quarter Moon" in every and "Last Quarter Moon" in every


@pytest.mark.slow
def test_transits_reach_the_natal_angles(natal_chart):
    collector = DailyEventCollector(
        natal_chart, date(2026, 1, 1), date(2026, 3, 31), EASTERN
    )
    collector.collect_natal_transits()
    descriptions = [e.description for e in collector._events]
    assert any("natal Ascendant" in d or "natal Midheaven" in d for d in descriptions)

    without = DailyEventCollector(
        natal_chart, date(2026, 1, 1), date(2026, 3, 31), EASTERN
    )
    without.collect_natal_transits(include_points=False)
    assert not any("Ascendant" in e.description for e in without._events)


@pytest.mark.slow
def test_full_planner_contract(native):
    """One contract build, many assertions — the expensive part runs once."""
    from stellium.planner.almanac import build_year_almanac, find_natal_transits
    from stellium.planner.contract import build_planner_data

    def build(**options):
        builder = PlannerBuilder.for_native(native).year(2026).timezone(EASTERN)
        if options.get("drop_progressed"):
            builder = builder.without_progressed_chart()
        config = builder._build_config()
        renderer = PlannerRenderer(config)
        start, end = renderer._date_range()
        chart = renderer._build_natal_chart()
        hits = find_natal_transits(
            chart, start, end, EASTERN, transit_planets=renderer._year_transit_planets()
        )
        almanac = build_year_almanac(
            chart,
            start,
            end,
            EASTERN,
            transits=hits,
            include_progressed=config.include_progressed_chart,
        )
        events = renderer._collect_events(chart, start, end, hits)
        data = build_planner_data(
            chart,
            almanac,
            events,
            name="Test",
            theme="house",
            include_progressed=config.include_progressed_chart,
            location_label=renderer._location_label(chart),
            timezone_label=_timezone_label(EASTERN),
        )
        return almanac, data

    almanac, data = build()
    titles = [f.get("title") for f in data["front"]]
    assert "The Progressed Moon" in titles

    # The solar return is shown in the planner's timezone, not UTC.
    assert almanac.solar_return.tzinfo is not None
    assert almanac.solar_return.utcoffset().total_seconds() == -4 * 3600  # EDT

    # Born May 15: the profected year turns over inside a calendar-year planner.
    assert almanac.profection_change is not None
    assert almanac.profection_change.date == date(2026, 5, 15)
    dashboard = data["front"][0]["sections"][0]["pairs"]
    assert any(label.startswith("From May 15") for label, _ in dashboard)

    # Times are labelled with the planner's timezone, not the birth place.
    assert "All times US Eastern" in data["meta"]["metadata"]

    # The year's summary is slow planets only.
    assert {t.transit_planet for t in almanac.transits} <= {
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    }

    # One weekly page per week.
    labels = [w["label"] for m in data["months"] for w in m["weeks_detail"]]
    assert len(labels) == len(set(labels))

    _, dropped = build(drop_progressed=True)
    assert "The Progressed Moon" not in [f.get("title") for f in dropped["front"]]


@pytest.mark.slow
def test_generate_renders_a_pdf(native):
    pytest.importorskip("typst")
    pdf = (
        PlannerBuilder.for_native(native)
        .date_range(date(2026, 9, 1), date(2026, 9, 30))
        .timezone(EASTERN)
        .page_size("letter")
        .generate()
    )
    assert pdf[:4] == b"%PDF"
