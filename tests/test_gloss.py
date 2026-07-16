"""Gloss — the concept-with-two-masks that keeps identity and presentation coupled.

The property that matters: a Gloss is its English *identity* to every machine operation
(dict key, ==, dispatch) and its localized *mask* only when a renderer asks for `.loc`. So
a lookup keyed on English works in any locale — the root cause of the whole class of
"lookup breaks under localization" bugs. See UNIFIED_RENDERER_CONTRACT.md §4.
"""

from __future__ import annotations

import json

from stellium.i18n import Gloss, display, gloss, msg, term
from stellium.i18n.pseudo import find_leaks


def test_gloss_is_its_identity_to_machinery():
    """== and hash go by .en, so a Gloss is a drop-in for its English string as a key."""
    g = Gloss(en="Illumination", loc="照明度")
    assert g == "Illumination"
    assert g == Gloss(en="Illumination", loc="anything else")  # identity, not mask
    assert hash(g) == hash("Illumination")
    d = {g: "57.9%"}
    assert d["Illumination"] == "57.9%"  # dict lookup by the English string finds it


def test_gloss_is_not_a_str():
    """Deliberately not a str subclass: a string op fails loudly instead of dropping
    the mask silently. str(g) is the identity, so a forgotten .loc leaks visible English."""
    g = Gloss(en="Retrograde", loc="逆行")
    assert not isinstance(g, str)
    assert (
        str(g) == "Retrograde"
    )  # identity — oracle-catchable if it ever reaches output
    assert display(g) == "逆行"  # the mask, flipped on at the display edge
    assert display("plain") == "plain"  # a non-Gloss passes through


def test_gloss_of_a_term_carries_both_dimensions_and_the_key():
    g = gloss(term("body.Sun"), "zh_CN")
    assert g.en == "Sun"  # identity
    assert g.loc == "太阳"  # mask
    assert g.key == "body.Sun"  # finest identity, for glyph/colour lookup


def test_english_gloss_is_byte_identical():
    """In English the mask *is* the identity — nothing moves versus the old flat render."""
    g = gloss(term("sign.Aries"), "en")
    assert g.en == g.loc == "Aries"
    m = gloss(
        msg("House ({system})", system=term("house_system.Placidus", short=True)), "en"
    )
    assert m.en == m.loc == "House (Pl)"


def test_message_gloss_composes_both_dimensions():
    """A Message's .en fills the English template with English slots; .loc fills the
    localized template with localized slots — one render() call each, so it just works."""
    g = gloss(
        msg(
            "{ruler} (ruler of {sign})",
            ruler=term("body.Mars"),
            sign=term("sign.Aries"),
        ),
        "zh_CN",
    )
    assert g.en == "Mars (ruler of Aries)"
    assert "火星" in g.loc and "白羊座" in g.loc


def test_untranslated_gloss_falls_back_to_english_in_loc():
    """A term with no translation masks to English — visible, not a raw key, not a crash."""
    g = gloss(
        term("body.Amor"), "zh_CN"
    )  # deliberately untranslated in the zh_CN audit
    assert g.en == "Amor"
    assert g.loc == "Amor"


def test_json_encoder_emits_both_dimensions():
    """The Typst boundary: a Gloss serializes to {en, loc} so the template prints .loc and
    looks up glyphs by .en."""

    class Enc(json.JSONEncoder):
        def default(self, o):
            return (
                {"en": o.en, "loc": o.loc}
                if isinstance(o, Gloss)
                else super().default(o)
            )

    payload = {"label": gloss(term("body.Sun"), "zh_CN")}
    out = json.loads(json.dumps(payload, cls=Enc))
    assert out["label"] == {"en": "Sun", "loc": "太阳"}


def test_pseudolocale_masks_bracket_and_identity_stays_english():
    """The oracle checks .loc (the mask) — bracketed, no leak. .en is identity, never shown."""
    g = gloss(term("phase.Waning Gibbous"), "qps")
    assert g.en == "Waning Gibbous"  # plain identity
    assert g.loc.startswith("⟦") and g.loc.endswith("⟧")  # bracketed mask
    assert find_leaks(g.loc) == []  # a masked string is not a leak
    assert find_leaks(g.en) == ["Waning", "Gibbous"]  # identity IS English, by design
