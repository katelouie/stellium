"""Tests for hyleg and length of life (years-table, Lilly).

Chart-calculating, so marked slow. Length of life is a computed traditional
*indicator*; tests assert structural correctness (candidacy, angularity ->
years family, itemized modifiers summing to total, non-negativity, the combust
unit switch), not real lifespans.
"""

import pytest

from stellium import ChartBuilder
from stellium.core.models import HylegResult, LengthOfLifeResult
from stellium.engines.length_of_life import _orb_aspect, find_hyleg

pytestmark = pytest.mark.slow

_ANGULAR = {1, 4, 7, 10}
_SUCCEDENT = {2, 5, 8, 11}


@pytest.fixture(scope="module")
def einstein():
    return ChartBuilder.from_notable("Albert Einstein").calculate()


@pytest.fixture(scope="module")
def day_chart():
    return ChartBuilder.from_details(
        "1990-06-15 12:00", (40.7128, -74.0060), name="Day"
    ).calculate()


# === Hyleg ==================================================================


def test_hyleg_is_traced_and_sect_ordered(day_chart):
    h = day_chart.hyleg()
    assert isinstance(h, HylegResult)
    # Day chart: Sun is the first candidate tried.
    assert h.candidates_tried[0][0] == "Sun"
    # Whatever wins sits in a hylegiacal place.
    assert h.place in {1, 7, 9, 10, 11}
    # The winning point is the last (True) entry in the trace.
    assert h.candidates_tried[-1] == (h.point, True)


def test_hyleg_ascendant_is_the_backstop(day_chart):
    # The Ascendant is always in house 1 (hylegiacal), so a hyleg always exists.
    h = day_chart.hyleg()
    assert h.point in {"Sun", "Moon", "Fortune", "Syzygy", "Ascendant"}


def test_hyleg_unknown_method_raises(day_chart):
    with pytest.raises(ValueError, match="lilly"):
        find_hyleg(day_chart, method="dorotheus")


def test_hyleg_unknown_time_raises():
    chart = ChartBuilder.from_details(
        "1990-06-15", (40.7128, -74.0060), time_unknown=True
    ).calculate()
    with pytest.raises(ValueError, match="known birth time"):
        chart.hyleg()


# === Length of life =========================================================


def test_result_shape_and_invariant(einstein):
    r = einstein.length_of_life()
    assert isinstance(r, LengthOfLifeResult)
    # base_years + all modifier deltas == total (modifiers are exhaustive).
    assert r.base_years + sum(m.delta for m in r.modifiers) == pytest.approx(r.total)
    assert r.total >= 0
    assert r.unit in {"years", "months", "days"}


def test_angularity_matches_family(einstein):
    r = einstein.length_of_life()
    # base_family is set from the alcocoden's angularity.
    if r.alcocoden_angularity == "angular":
        assert r.base_family == "greater"
    elif r.alcocoden_angularity == "succedent":
        assert r.base_family == "mean"
    else:
        assert r.base_family == "least"


def test_alcocoden_beholds_the_hyleg(einstein):
    r = einstein.length_of_life()
    alco_lon = einstein.get_object(r.alcocoden).longitude
    # Whole-sign beholding: sign distance in {0,2,3,4,6}.
    d = abs(int(alco_lon // 30) - int(r.hyleg.longitude // 30)) % 12
    assert min(d, 12 - d) in {0, 2, 3, 4, 6} or r.notes  # or a documented fallback


def test_einstein_known_selection(einstein):
    # Deterministic given the ephemeris + notable data (see spec smoke).
    r = einstein.length_of_life()
    assert r.hyleg.point == "Sun"
    assert r.alcocoden == "Mars"
    assert r.base_family == "mean"


def test_combust_alcocoden_switches_unit_to_months():
    # Marilyn Monroe's alcocoden (Mercury) is combust in this method.
    r = ChartBuilder.from_notable("Marilyn Monroe").calculate().length_of_life()
    if r.alcocoden != "Sun" and any("combust" in n for n in r.notes):
        assert r.unit == "months"


def test_ptolemy_method_not_implemented(einstein):
    with pytest.raises(NotImplementedError, match="directional"):
        einstein.length_of_life(method="ptolemy")


def test_unknown_time_raises():
    chart = ChartBuilder.from_details(
        "1990-06-15", (40.7128, -74.0060), time_unknown=True
    ).calculate()
    with pytest.raises(ValueError, match="known birth time"):
        chart.length_of_life()


# === Orb-aspect helper ======================================================


def test_orb_aspect_respects_moiety_orb():
    # Sun (moiety 15) + Saturn (9): orb = 12. A 100 deg separation is a square
    # (90) within 12 deg.
    assert _orb_aspect(0.0, 100.0, "Sun", "Saturn") == "square"
    # 0 vs 130: nearest aspect is trine(120), off by 10 <= 12 -> trine.
    assert _orb_aspect(0.0, 130.0, "Sun", "Saturn") == "trine"
    # Two Mercuries (orb 7): 0 vs 100 -> square off by 10 > 7 -> no aspect.
    assert _orb_aspect(0.0, 100.0, "Mercury", "Mercury") is None
