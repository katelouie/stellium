"""Tier 2 — web i18n translator, list lookup, and report-locale mapping.

These read the user's locale via ``i18n.get_user_locale()``; we monkeypatch
that rather than standing up a NiceGUI session, so they stay pure-logic tests.
"""

import i18n
import pytest


@pytest.fixture
def english(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n, "get_user_locale", lambda: "en")


@pytest.fixture
def chinese(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n, "get_user_locale", lambda: "zh_CN")
    i18n._cache.clear()
    i18n._raw_cache.clear()


def test_wt_passes_english_through(english: None) -> None:
    _ = i18n.wt()
    assert _("CREATE CHART") == "CREATE CHART"


def test_wt_translates_and_falls_back(chinese: None) -> None:
    _ = i18n.wt()
    assert _("CREATE CHART") == "生成星盘"  # present in zh_CN.json
    assert _("a string with no translation") == "a string with no translation"


def test_report_locale_identity_for_english(english: None) -> None:
    assert i18n.report_locale() == "en"


def test_report_locale_passes_through_known_library_locale(chinese: None) -> None:
    # zh_CN has a stellium.i18n locale file, so it maps through unchanged.
    assert i18n.report_locale() == "zh_CN"


def test_report_locale_falls_back_for_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n, "get_user_locale", lambda: "fr_FR")
    assert i18n.report_locale() == "en"


def test_wt_list_returns_fallback_for_english(english: None) -> None:
    fallback = [["★", "Feature", "Description"]]
    assert i18n.wt_list("features", fallback) is fallback


def test_wt_list_returns_translated_for_chinese(chinese: None) -> None:
    # zh_CN.json ships 12 translated feature triples.
    fallback = [["★", f"title {i}", f"desc {i}"] for i in range(12)]
    out = i18n.wt_list("features", fallback)
    assert len(out) == 12
    assert out != fallback


def test_wt_list_falls_back_on_length_mismatch(chinese: None) -> None:
    fallback = [["★", "only one", "entry"]]  # wrong length -> fallback
    assert i18n.wt_list("features", fallback) is fallback
