"""Tier 2 — the "View as Python" generators.

The generators are pure functions returning a code string, so we can assert
the output is valid, runnable Python (``ast.parse``) and that the localized
report chain is reflected. ``report_locale`` is imported into the module, so
we patch it there.
"""

import ast

import components.code_preview as cp
import pytest
from state import ChartState, PDFReportState, RelationshipsState, TimingState


@pytest.fixture
def report_state() -> PDFReportState:
    return PDFReportState()


def _natal_state() -> ChartState:
    return ChartState(
        name="Test", date="2000-01-06", time="12:00", location="Seattle, WA"
    )


def test_natal_code_is_valid_python_without_locale(
    report_state: PDFReportState, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cp, "report_locale", lambda: "en")
    code = cp.generate_natal_code(_natal_state(), report_state)
    ast.parse(code)  # must be runnable
    assert ".with_locale(" not in code  # English is a no-op, omitted


def test_natal_code_includes_locale_when_selected(
    report_state: PDFReportState, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cp, "report_locale", lambda: "zh_CN")
    code = cp.generate_natal_code(_natal_state(), report_state)
    ast.parse(code)
    assert '.with_locale("zh_CN")' in code


@pytest.mark.parametrize("chart_type", ["synastry", "composite", "davison"])
def test_relationships_code_is_valid_python(
    chart_type: str, report_state: PDFReportState, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cp, "report_locale", lambda: "zh_CN")
    state = RelationshipsState()
    state.chart_type = chart_type
    for person in (state.person1, state.person2):
        person.date, person.time, person.location = "1990-01-01", "10:00", "NYC"
    code = cp.generate_relationships_code(state, report_state)
    ast.parse(code)
    assert '.with_locale("zh_CN")' in code


@pytest.mark.parametrize(
    "chart_type",
    ["transits", "progressions", "solar_return", "lunar_return", "planetary_return"],
)
def test_timing_code_is_valid_python(
    chart_type: str, report_state: PDFReportState, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(cp, "report_locale", lambda: "en")
    state = TimingState()
    state.chart_type = chart_type
    state.natal = ChartState(date="1985-03-03", time="08:00", location="Chicago")
    # Solar return expects a year (UI placeholder "YYYY"); others take a date.
    state.timing_date = "2025" if chart_type == "solar_return" else "2025-01-01"
    code = cp.generate_timing_code(state, report_state)
    ast.parse(code)
