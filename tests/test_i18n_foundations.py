"""Phase 1 acceptance criteria for the format-last i18n architecture.

These are the criteria from docs/development/specs/STRUCTURE_FIRST_SECTIONS.md §12, not a
guard per function. The load-bearing one is `test_english_and_zh_output_unchanged`: Phase
1 adds machinery but must not move any rendered output — if it does, it is a bug.
"""

from __future__ import annotations

import datetime as dt
import hashlib

import pytest

from stellium import ChartBuilder, ReportBuilder
from stellium.i18n import (
    PSEUDO_LOCALE,
    build_catalog,
    format_date,
    locale_chain,
    msg,
    render,
    term,
)
from stellium.i18n.pseudo import find_leaks


def test_catalog_derives_from_registries():
    """Adding a body to the registry must add a catalog key with no edit to catalog.py."""
    from stellium.core.registry import CELESTIAL_REGISTRY

    catalog = build_catalog()
    for name in CELESTIAL_REGISTRY:
        assert f"body.{name}" in catalog


def test_fallback_chain_is_most_specific_first_ending_english():
    assert locale_chain("zh_Hant_TW") == ["zh_Hant_TW", "zh_Hant", "zh", "en"]
    assert locale_chain("zh_CN") == ["zh_CN", "zh", "en"]
    assert locale_chain("en") == ["en"]


def test_message_composes_and_reorders():
    m = msg("House ({system})", system=term("house_system.Placidus", short=True))
    assert render(m, "en") == "House (Pl)"
    assert render(m, "zh_CN") == "宫位（普）"


def test_english_message_needs_no_locale_file():
    """The identity locale must work with nothing on disk — the key IS the English."""
    m = msg(
        "{ruler} (ruler of {sign})", ruler=term("body.Mars"), sign=term("sign.Aries")
    )
    assert render(m, "en") == "Mars (ruler of Aries)"


def test_date_is_reordered_not_word_swapped():
    """The case post-hoc translation cannot do: March 14, 1879 -> 1879年3月14日."""
    d = dt.datetime(1879, 3, 14)
    assert format_date(d, "en") == "March 14, 1879"
    assert format_date(d, "zh_CN") == "1879年3月14日"


def test_namespacing_separates_a_real_collision():
    """`Earth` is both a planet and an element; zh_CN translates them differently.

    Before namespacing, the flat translator mapped `Earth` -> 土象 (the element) for both,
    so a heliocentric chart rendered the *planet* Earth as the element.
    """
    assert render(term("body.Earth"), "zh_CN") == "地球"
    assert render(term("element.Earth"), "zh_CN") == "土象"


def test_term_falls_back_to_english_never_the_raw_key():
    """An untranslated catalog key must degrade to English, not leak `body.Sedna`."""
    got = render(term("body.Sedna"), "zh_CN")
    assert got == "Sedna"
    assert "." not in got


def test_untranslated_template_still_localizes_its_slots():
    """An untranslated template falls back to the English frame but keeps translated
    slots — partial translation degrades per-slot, it does not crash or go all-English."""
    m = msg("in {sign}", sign=term("sign.Aries"))
    assert render(m, "en") == "in Aries"
    assert render(m, "zh_CN") == "in 白羊座"  # frame English, slot translated


def test_bad_translation_that_invents_a_slot_degrades_to_english(monkeypatch):
    """If a locale's translation references a slot the English template lacks, render
    falls back to the English template rather than KeyError-ing mid-chart."""
    import stellium.i18n.message as message_mod

    real_t = message_mod.t

    def fake_t(key, locale=None):
        # Only corrupt the one template; let term lookups resolve normally.
        if key == "{ruler} rules":
            return "{ruler} rules {typo}"  # invents a slot the English lacks
        return real_t(key, locale=locale)

    monkeypatch.setattr(message_mod, "t", fake_t)
    m = msg("{ruler} rules", ruler=term("body.Mars"))
    # The guard reverts the *frame* to English; the slot still localizes (Mars -> 火星).
    # The point is only that it does not raise KeyError on {typo}.
    assert render(m, "zh_CN") == "火星 rules"


def test_locale_flatten_and_nest_are_mutual_inverses():
    """The grouped file and the dotted keys it loads to must round-trip losslessly.

    flatten(nested) is what the loader returns; nest(flat) is what tooling uses to
    regenerate the file. They are inverses, so a translator can edit either form. The
    one thing flatten discards is the message/legacy split (both flatten to bare keys),
    so nest takes the legacy key set to recover it.
    """
    import json
    from pathlib import Path

    from stellium.i18n.loader import _flatten_locale, _nest_locale

    path = Path("src/stellium/i18n/locales/zh_CN/strings.json")
    doc = json.loads(path.read_text(encoding="utf-8"))
    flat = _flatten_locale(doc)
    legacy = frozenset(doc.get("legacy", {}))

    # The direction tooling depends on: edit the dotted keys, regroup, no loss.
    assert _flatten_locale(_nest_locale(flat, doc["metadata"], legacy)) == flat

    # Full structural round-trip: the regrouped document equals the file on disk.
    rebuilt = _nest_locale(flat, doc["metadata"], legacy)
    assert rebuilt == doc

    # A namespaced key must not collide a bare English one: body.Earth and element.Earth
    # survive the round-trip as distinct keys with distinct values.
    assert flat["body.Earth"] != flat["element.Earth"]


def _report(chart, locale):
    return (
        ReportBuilder()
        .from_chart(chart)
        .with_locale(locale)
        .with_chart_overview()
        .with_planet_positions()
        .with_aspects(mode="major")
        .with_dignities()
        .with_moon_phase()
        .to_string(format="markdown")
    )


@pytest.mark.slow
def test_english_report_byte_identical():
    """The refactor invariant, across every phase: English output does not move.

    Hash captured against commit 3399e86 (before any i18n code). Each phase migrates
    sections to the format-last contract; if any of that changes the *English* report,
    it is a bug. (The zh_CN report is *meant* to change as leaks are fixed — that is
    asserted separately, by rendered content rather than a hash that would churn.)
    """
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    got = hashlib.sha1(_report(chart, "en").encode()).hexdigest()
    assert got == "d7349ef80c503871fc3b49bb1358020db06a981a", (
        f"English report changed (now {got}) — the migration must not touch English"
    )


@pytest.mark.slow
def test_chart_overview_localizes_fully_in_zh():
    """ChartOverview is migrated: its zh_CN output has no English but proper nouns.

    The four original leaks lived here — the date (a reorder), the time, "Rising", and
    "Day Chart" (composed). A person's name, a geocoded place and an IANA timezone are
    data, not translatable, so they stay; nothing else may.
    """
    import re

    dnt = {"Albert", "Einstein", "Ulm", "Germany", "Europe", "Berlin"}
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    out = (
        ReportBuilder()
        .from_chart(chart)
        .with_locale("zh_CN")
        .with_chart_overview()
        .to_string(format="markdown")
    )
    leaks = [w for w in re.findall(r"[A-Za-z][A-Za-z'’.]+", out) if w not in dnt]
    assert leaks == [], f"zh_CN ChartOverview still leaks English: {leaks}"


def test_pseudolocale_is_a_partial_oracle():
    """Bracketing must mean 'went through the catalog' — and nothing else.

    A catalog term IS bracketed; an arbitrary string handed to the layer is NOT. If the
    pseudolocale were total (bracketing everything), a proper noun would look translated
    and the oracle — 'unbracketed Latin text is a leak' — would be worthless.
    """
    # Routed through the catalog: bracketed, so find_leaks sees nothing to report.
    routed = render(term("body.Sun"), PSEUDO_LOCALE)
    assert routed.startswith("⟦") and routed.endswith("⟧")
    assert find_leaks(routed) == []

    # A composed English string that never went through the layer: NOT bracketed, so it
    # is reported as a leak. This is the whole mechanism.
    assert find_leaks("Chart Overview") == ["Chart", "Overview"]


@pytest.mark.slow
def test_migrated_sections_have_no_pseudolocale_leaks():
    """The completeness oracle: a fully-migrated section, rendered in the pseudolocale,
    has NO unbracketed text outside the do-not-translate set.

    Every string ChartOverview and PlanetPositions emit — values, headers, key labels,
    the section name — now goes through the catalog, so it is bracketed. The only Latin
    left is proper nouns (a person's name, a place, a timezone), which are data. If a
    future edit stringifies a cell behind the contract's back, this fails.
    """
    dnt = {"Albert", "Einstein", "Ulm", "Germany", "Europe", "Berlin", "Europe/Berlin"}
    chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    out = (
        ReportBuilder()
        .from_chart(chart)
        .with_locale(PSEUDO_LOCALE)
        .with_chart_overview()
        .with_planet_positions()
        .to_string(format="markdown")
    )
    leaks = [w for w in find_leaks(out) if w not in dnt]
    assert leaks == [], (
        f"a migrated section is stringifying behind the contract: {leaks}"
    )
