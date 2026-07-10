"""Tests for the Firdaria time-lord engine.

Chart-calculating, so marked slow. Verifies sect-based ordering, the node-
placement presets, seven equal Chaldean sub-periods, the repeat behavior, and
the unknown-time guard. See docs/development/specs/HELLENISTIC_PERIODS_SPEC.md.
"""

import datetime as dt

import pytest

from stellium import ChartBuilder
from stellium.core.models import FirdariaTimeline

pytestmark = pytest.mark.slow

_NODES = ("North Node", "South Node")


@pytest.fixture(scope="module")
def day_chart():
    # Noon in New York -> Sun above the horizon -> day chart.
    return ChartBuilder.from_details(
        "1990-06-15 12:00", (40.7128, -74.0060), name="Day"
    ).calculate()


@pytest.fixture(scope="module")
def night_chart():
    # After midnight -> Sun below the horizon -> night chart.
    return ChartBuilder.from_details(
        "1990-06-15 00:30", (40.7128, -74.0060), name="Night"
    ).calculate()


def _first_pass(timeline):
    """Major rulers up to the first repeat (before age 75/70)."""
    horizon = 75
    return [m.ruler for m in timeline.majors() if m.start_age < horizon]


# === Sect ordering ==========================================================


def test_day_chart_starts_with_sun(day_chart):
    tl = day_chart.firdaria()
    assert isinstance(tl, FirdariaTimeline)
    assert tl.sect == "day"
    assert tl.majors()[0].ruler == "Sun"


def test_night_chart_starts_with_moon(night_chart):
    tl = night_chart.firdaria()
    assert tl.sect == "night"
    assert tl.majors()[0].ruler == "Moon"


def test_default_first_pass_order_day(day_chart):
    assert _first_pass(day_chart.firdaria()) == [
        "Sun",
        "Venus",
        "Mercury",
        "Moon",
        "Saturn",
        "Jupiter",
        "Mars",
        "North Node",
        "South Node",
    ]


def test_default_nodes_at_end_night(night_chart):
    # abu_mashar default: nodes at the end even for a night chart.
    assert _first_pass(night_chart.firdaria())[-2:] == ["North Node", "South Node"]


# === Node-placement presets =================================================


def test_bonatti_nocturnal_nodes_after_mars(night_chart):
    order = _first_pass(night_chart.firdaria(preset="bonatti"))
    assert order == [
        "Moon",
        "Saturn",
        "Jupiter",
        "Mars",
        "North Node",
        "South Node",
        "Sun",
        "Venus",
        "Mercury",
    ]


def test_bonatti_day_chart_nodes_still_at_end(day_chart):
    # For day charts, "after Mars" == at end (Mars is last of the seven).
    assert _first_pass(day_chart.firdaria(preset="bonatti"))[-2:] == list(_NODES)


def test_al_biruni_is_alias_of_default(day_chart):
    assert _first_pass(day_chart.firdaria(preset="al_biruni")) == _first_pass(
        day_chart.firdaria(preset="abu_mashar")
    )


def test_no_nodes_preset_has_no_node_majors(day_chart):
    tl = day_chart.firdaria(preset="no_nodes")
    assert all(m.ruler not in _NODES for m in tl.majors())
    # Seven-planet first pass sums to 70 years.
    first_seven = tl.majors()[:7]
    assert first_seven[0].start_age == 0
    assert first_seven[-1].end_age == 70


def test_unknown_preset_raises(day_chart):
    with pytest.raises(ValueError, match="preset"):
        day_chart.firdaria(preset="nonsense")


# === Major periods & totals =================================================


def test_first_pass_total_is_75_years(day_chart):
    majors = day_chart.firdaria().majors()
    # The ninth major (South Node) ends the first cycle at age 75.
    assert majors[8].end_age == pytest.approx(75.0)
    assert majors[0].start_age == 0.0


def test_major_lengths_match_firdaria_years(day_chart):
    from stellium.core.planetary_years import FIRDARIA_YEARS

    for m in day_chart.firdaria().majors():
        assert m.length_years == pytest.approx(FIRDARIA_YEARS[m.ruler])


# === Sub-periods ============================================================


def test_seven_equal_subperiods_chaldean_from_ruler(day_chart):
    tl = day_chart.firdaria()
    sun_major = tl.majors()[0]  # Sun, 10 years
    sun_subs = [
        s
        for s in tl.subperiods()
        if s.ruler == "Sun" and s.start_age < sun_major.end_age
    ][:7]
    assert [s.sub_ruler for s in sun_subs] == [
        "Sun",
        "Venus",
        "Mercury",
        "Moon",
        "Saturn",
        "Jupiter",
        "Mars",
    ]
    # Each is one-seventh of the 10-year major.
    for s in sun_subs:
        assert s.length_years == pytest.approx(10 / 7)


def test_node_majors_have_no_subperiods(day_chart):
    tl = day_chart.firdaria()
    assert not any(s.ruler in _NODES for s in tl.subperiods())


def test_at_returns_active_major_and_sub(day_chart):
    tl = day_chart.firdaria()
    birth = day_chart.datetime.utc_datetime
    # Age ~5: still in the Sun major (0-10); Sun subs are ~1.43 yr each, so
    # age 5 falls in the 4th sub -> Moon.
    p = tl.at(birth + dt.timedelta(days=5 * 365.2425))
    assert p is not None
    assert p.level == 2
    assert p.ruler == "Sun"
    assert p.sub_ruler == "Moon"


def test_at_outside_span_returns_none(day_chart):
    tl = day_chart.firdaria(max_age=20)
    birth = day_chart.datetime.utc_datetime
    assert tl.at(birth + dt.timedelta(days=50 * 365.2425)) is None


# === Repeat & horizon =======================================================


def test_repeat_false_stops_after_one_pass(day_chart):
    tl = day_chart.firdaria(repeat=False)
    assert len(tl.majors()) == 9  # seven planets + two nodes, once
    assert tl.majors()[-1].end_age == pytest.approx(75.0)


def test_repeat_true_extends_past_75(day_chart):
    tl = day_chart.firdaria(max_age=96)
    assert tl.majors()[-1].end_age > 75
    # After the first cycle it returns to the Sun.
    assert tl.majors()[9].ruler == "Sun"


# === Unknown time ===========================================================


def test_unknown_time_chart_raises():
    chart = ChartBuilder.from_details(
        "1990-06-15", (40.7128, -74.0060), time_unknown=True
    ).calculate()
    with pytest.raises(ValueError, match="known birth time"):
        chart.firdaria()
