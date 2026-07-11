"""Tests for the sect rectification subsystem + report sections."""

from dataclasses import FrozenInstanceError

import pytest

from stellium import (
    ChartBuilder,
    Native,
    ReportBuilder,
    SectAnalysis,
    analyze_sect,
    convergence_matrix,
)
from stellium.data import LifeEvent
from stellium.rectification import calibrated_p_day

pytestmark = pytest.mark.slow  # builds charts + re-casts


@pytest.fixture(scope="module")
def frida():
    return ChartBuilder.from_notable("Frida Kahlo").calculate()


# ── core analysis ─────────────────────────────────────────────────────────────


def test_analyze_sect_notable_autolookup(frida):
    a = analyze_sect(frida)
    assert isinstance(a, SectAnalysis)
    assert a.name == "Frida Kahlo"
    assert a.has_events  # events auto-looked-up from the biography catalog
    assert 0.0 <= a.p_day <= 1.0
    assert a.leans in ("day", "night")
    # Frida is a day chart; the validated anchor should recover it.
    assert a.leans == "day"


def test_hypotheses_are_sect_correct(frida):
    a = analyze_sect(frida)
    assert a.day.sect_light.planet == "Sun"
    assert a.day.out_of_sect_malefic.planet == "Mars"
    assert a.day.in_sect_benefic.planet == "Jupiter"
    assert a.night.sect_light.planet == "Moon"
    assert a.night.out_of_sect_malefic.planet == "Saturn"
    assert a.night.in_sect_benefic.planet == "Venus"


def test_frozen(frida):
    a = analyze_sect(frida)
    with pytest.raises(FrozenInstanceError):
        a.p_day = 0.5  # type: ignore[misc]


def test_geometry_only_for_non_notable():
    native = Native("1990-03-15 09:00:00", "Chicago, IL")
    chart = ChartBuilder.from_native(native).calculate()
    a = analyze_sect(chart, events=())  # force geometry-only
    assert not a.has_events
    assert a.hardship is None
    assert 0.0 <= a.p_day <= 1.0  # daylight-prior-only estimate still available


def test_explicit_events_override(frida):
    ev = [
        LifeEvent(
            date="1925",
            precision="year",
            type="accident",
            description="near-fatal bus crash, iron rail",
            significance="major",
        ),
    ]
    a = analyze_sect(frida, events=ev)
    assert a.has_events
    # A single Mars-flavoured accident should tilt hardship toward day.
    assert a.hardship == (1.0, 0.0)


def test_baked_model_reproduces_workbench(frida):
    # Frida with her real events reproduces the documented workbench value ~0.80.
    a = analyze_sect(frida)
    assert a.p_day == pytest.approx(0.80, abs=0.03)
    # Geometry-only (no events): malefic is centred at the corpus mean, so "no
    # evidence" reads mildly day — a weaker lean than the event-informed 0.80.
    assert calibrated_p_day(frida, []) == pytest.approx(0.64, abs=0.05)


# ── report sections ───────────────────────────────────────────────────────────


@pytest.mark.parametrize("fmt", ["markdown", "plain_table", "prose", "html"])
def test_rectification_section_renders(frida, fmt):
    s = ReportBuilder().from_chart(frida).with_sect_rectification().to_string(fmt)
    assert "Unknown type" not in s
    assert "P(day)" in s
    assert "Sect light" in s  # a comparison-table row, present in every format


def test_convergence_matrix_data(frida):
    m = convergence_matrix(frida)
    assert m.columns  # non-empty structural band
    assert len(m.hooks_by_hour) == 24
    assert m.anchor_sect in ("day", "night")


@pytest.mark.parametrize("fmt", ["markdown", "plain_table"])
def test_convergence_matrix_section_renders(frida, fmt):
    s = ReportBuilder().from_chart(frida).with_sect_convergence_matrix().to_string(fmt)
    assert "Unknown type" not in s
    assert "Lens A" in s and "Lens B" in s


def test_matrix_empty_without_events():
    native = Native("1990-03-15 09:00:00", "Chicago, IL")
    chart = ChartBuilder.from_native(native).calculate()
    m = convergence_matrix(chart, events=())
    assert m.columns == ()
