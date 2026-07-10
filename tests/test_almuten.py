"""Tests for the almuten-of-a-degree primitive.

Pure-data (no chart calculation). Hand-checkable essential-dignity scoring:
domicile 5, exaltation 4, triplicity 3, term 2, face 1.
"""

from stellium.engines.almuten import DIGNITY_WEIGHTS, almuten_of_degree


def _lon(sign_index: int, degree: float) -> float:
    """Longitude for a 0-based sign index (Aries=0) and degree-in-sign."""
    return sign_index * 30 + degree


# === Core scoring ===========================================================


def test_15_aries_day_sun_wins():
    # Mars domicile(5); Sun exaltation(4)+triplicity-day(3)+face(1)=8; Mercury term(2).
    r = almuten_of_degree(_lon(0, 15), "day")
    assert r.scores["Sun"] == 8
    assert r.scores["Mars"] == 5
    assert r.scores["Mercury"] == 2
    assert r.winner == "Sun"
    assert r.tie == ()


def test_15_aries_night_ties_sun_and_mars():
    # Night triplicity -> Jupiter, so Sun drops to exaltation(4)+face(1)=5,
    # equal to Mars's domicile(5).
    r = almuten_of_degree(_lon(0, 15), "night")
    assert r.scores["Sun"] == 5
    assert r.scores["Mars"] == 5
    assert set(r.tie) == {"Sun", "Mars"}
    assert r.winner in {"Sun", "Mars"}


def test_dignities_are_recorded():
    r = almuten_of_degree(_lon(0, 15), "day")
    assert r.dignities["Sun"] == ["exaltation", "triplicity", "face"]
    assert r.dignities["Mars"] == ["domicile"]
    assert r.dignities["Mercury"] == ["term"]


# === Term & face rulers =====================================================


def test_term_ruler_reflects_corrected_sagittarius():
    # 22 deg Sagittarius: after the term fix, Saturn rules 21-26 (was Mars).
    r = almuten_of_degree(_lon(8, 22), "day")
    assert "term" in r.dignities["Saturn"]
    assert "term" not in r.dignities["Mars"]


def test_face_ruler_chaldean():
    # 15 deg Aries -> 2nd face -> Sun (Aries chaldean faces: Mars, Sun, Venus).
    r = almuten_of_degree(_lon(0, 15), "day")
    assert "face" in r.dignities["Sun"]
    # 5 deg Aries -> 1st face -> Mars.
    r0 = almuten_of_degree(_lon(0, 5), "day")
    assert "face" in r0.dignities["Mars"]


# === Sect sensitivity =======================================================


def test_triplicity_is_sect_dependent():
    day = almuten_of_degree(_lon(0, 15), "day")
    night = almuten_of_degree(_lon(0, 15), "night")
    # Aries triplicity: day Sun, night Jupiter.
    assert "triplicity" in day.dignities["Sun"]
    assert "triplicity" in night.dignities["Jupiter"]


# === Robustness =============================================================


def test_node_exaltation_is_not_awarded():
    # Some modern schemes put a node as a sign's exaltation ruler; the almuten
    # only scores the seven planets, so a node must never receive points.
    for sign_index in range(12):
        for deg in (1, 14, 27):
            r = almuten_of_degree(_lon(sign_index, deg), "day", system="modern")
            assert "North Node" not in r.scores
            assert "South Node" not in r.scores


def test_term_and_face_guarantee_a_winner():
    # Every degree has a term ruler and a face ruler, so there is always a
    # positively-scored planet.
    for sign_index in range(12):
        r = almuten_of_degree(_lon(sign_index, 17), "day")
        assert r.winner != ""
        assert max(r.scores.values()) > 0


def test_weights_are_the_classical_set():
    assert DIGNITY_WEIGHTS == {
        "domicile": 5,
        "exaltation": 4,
        "triplicity": 3,
        "term": 2,
        "face": 1,
    }
