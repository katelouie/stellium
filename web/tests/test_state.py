"""Tier 2 — pure validation logic on the state dataclasses."""

from state import ChartState, PlannerState, RelationshipsState, TimingState


def test_chartstate_invalid_when_empty() -> None:
    assert not ChartState().is_valid()


def test_chartstate_valid_with_date_time_location() -> None:
    assert ChartState(
        date="2000-01-06", time="12:00", location="Seattle, WA"
    ).is_valid()


def test_chartstate_valid_with_coords_and_unknown_time() -> None:
    # Coordinates substitute for a place name; unknown time substitutes for a time.
    assert ChartState(
        date="2000-01-06", time_unknown=True, latitude=47.6, longitude=-122.3
    ).is_valid()


def test_chartstate_requires_location() -> None:
    assert not ChartState(date="2000-01-06", time="12:00").is_valid()


def test_timingstate_transits_require_a_date() -> None:
    natal = ChartState(date="2000-01-06", time="12:00", location="X")
    t = TimingState(natal=natal, chart_type="transits", timing_date="")
    assert not t.is_valid()
    t.timing_date = "2025-01-01"
    assert t.is_valid()


def test_relationships_require_both_people() -> None:
    r = RelationshipsState()
    r.person1 = ChartState(date="2000-01-06", time="12:00", location="X")
    assert not r.is_valid()
    r.person2 = ChartState(date="1990-01-01", time="10:00", location="Y")
    assert r.is_valid()


def test_planner_requires_year_or_custom_range() -> None:
    native = ChartState(date="2000-01-06", time="12:00", location="X")
    p = PlannerState(native=native, year=2025)
    assert p.is_valid()

    p.use_custom_range = True
    p.start_date = p.end_date = ""
    assert not p.is_valid()
    p.start_date, p.end_date = "2025-01-01", "2025-12-31"
    assert p.is_valid()
