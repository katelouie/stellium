"""
Web app i18n loader.

Loads JSON locale files from web/i18n/ and provides a translation function
scoped to the current user's session via app.storage.user.

Usage in pages:
    from i18n import wt, language_selector

    @ui.page('/')
    def index():
        _ = wt()  # Get translator for current user's locale
        ui.label(_("BIRTH CHART"))
        language_selector()  # Adds the language dropdown
"""

import json
from collections.abc import Callable
from pathlib import Path

from nicegui import app

_LOCALES_DIR = Path(__file__).parent
_cache: dict[str, dict[str, str]] = {}
_raw_cache: dict[str, dict] = {}

# The locales offered in the header dropdown, code -> display name. Curated (not just a
# glob of *.json) so a *base* file like ``zh_Hant`` powers the fallback chain without
# appearing as its own selectable language — users pick a region (TW/HK), not the base.
_DISPLAY_NAMES = {
    "en": "English",
    "zh_CN": "简体中文",
    "zh_Hant_TW": "繁體中文（台灣）",
    "zh_Hant_HK": "繁體中文（香港）",
}


def _locale_chain(locale: str) -> list[str]:
    """Fallback chain, most-specific first: ``zh_Hant_TW`` -> ``zh_Hant`` -> ``zh``.

    Mirrors the library's ``stellium.i18n`` resolution: a regional file overrides only
    the terms that genuinely differ, everything else resolves from the base, and any key
    missing from the whole chain falls back to the English source string (the key itself).
    """
    parts = locale.split("_")
    return ["_".join(parts[:i]) for i in range(len(parts), 0, -1)]


def _load_raw(locale: str) -> dict:
    """Load the raw (unflattened) locale JSON, preserving nested lists/dicts."""
    if locale in _raw_cache:
        return _raw_cache[locale]
    locale_file = _LOCALES_DIR / f"{locale}.json"
    data: dict = {}
    if locale_file.exists():
        try:
            data = json.loads(locale_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    _raw_cache[locale] = data
    return data


def _find_list(data: dict, key: str) -> list | None:
    """Recursively find the first list stored under ``key`` in nested dicts."""
    for k, v in data.items():
        if k == key and isinstance(v, list):
            return v
        if isinstance(v, dict):
            found = _find_list(v, key)
            if found is not None:
                return found
    return None


def _load_locale(locale: str) -> dict[str, str]:
    """Load and flatten a web locale file."""
    locale_file = _LOCALES_DIR / f"{locale}.json"
    if not locale_file.exists():
        return {}

    try:
        data = json.loads(locale_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    # Flatten all nested dicts into a single key-value mapping
    flat: dict[str, str] = {}
    for key, value in data.items():
        if key == "metadata" or key == "excluded_categories":
            continue
        if isinstance(value, dict):
            _flatten_dict(value, flat)
        elif isinstance(value, str):
            flat[key] = value
    return flat


def _flatten_dict(d: dict, flat: dict[str, str], prefix: str = "") -> None:
    """Recursively flatten nested dicts into a flat key-value mapping."""
    for key, value in d.items():
        if isinstance(value, str):
            flat[key] = value
        elif isinstance(value, dict):
            _flatten_dict(value, flat)
        # Skip lists and other types (like feature arrays)


def _get_strings(locale: str) -> dict[str, str]:
    """Cached strings for a locale, merged across its fallback chain (most-specific wins)."""
    if locale not in _cache:
        merged: dict[str, str] = {}
        for step in reversed(_locale_chain(locale)):  # least specific first
            merged.update(_load_locale(step))
        _cache[locale] = merged
    return _cache[locale]


def get_user_locale() -> str:
    """Get the current user's locale from session storage."""
    try:
        return app.storage.user.get("language", "en")
    except Exception:
        return "en"


def set_user_locale(locale: str) -> None:
    """Set the current user's locale in session storage."""
    app.storage.user["language"] = locale


def wt() -> Callable[[str], str]:
    """Get the translation function for the current user's locale.

    Returns a callable that translates strings. English keys pass through
    unchanged. Unknown keys return the key itself.

    Usage:
        _ = wt()
        ui.label(_("BIRTH CHART"))  # -> "本命盘" if locale is zh_CN
    """
    locale = get_user_locale()

    if locale == "en":
        return lambda key: key

    strings = _get_strings(locale)
    return lambda key: strings.get(key, key)


def wt_list(key: str, fallback: list) -> list:
    """Return a translated nested list (e.g. the home ``features`` array).

    Looks up ``key`` in the current user's raw locale data and returns the
    nested list found there. Falls back to ``fallback`` (the English list)
    when the locale is English, the key is missing, or the shape differs.

    Usage:
        features = wt_list("features", ENGLISH_FEATURES)
    """
    locale = get_user_locale()
    if locale == "en":
        return fallback

    # Walk the fallback chain: use the most-specific file that carries the list.
    for step in _locale_chain(locale):
        translated = _find_list(_load_raw(step), key)
        if translated is not None and len(translated) == len(fallback):
            return translated
    return fallback


def report_locale() -> str:
    """Map the current user's web locale to a library (``stellium.i18n``) locale.

    The web UI and the library use the same locale codes (e.g. ``"zh_CN"``),
    but the two translation systems are independent. This returns the code to
    pass to ``ReportBuilder.with_locale()`` so generated reports follow the
    user's selected language -- or ``"en"`` if the library has no matching
    locale file, so report rendering degrades gracefully to English.
    """
    locale = get_user_locale()
    if locale == "en":
        return "en"
    try:
        from stellium.i18n import get_available_locales as _lib_locales

        if locale in _lib_locales():
            return locale
    except Exception:
        pass
    return "en"


def get_available_locales() -> dict[str, str]:
    """Selectable locales for the header dropdown, ``{code: display_name}``.

    Curated via ``_DISPLAY_NAMES`` rather than a raw ``*.json`` glob, so a base file
    (``zh_Hant``) that only exists to feed the fallback chain is not itself offered as a
    language. English is always available (the identity locale, no file needed).
    """
    locales = {"en": "English"}
    for f in _LOCALES_DIR.glob("*.json"):
        code = f.stem
        if code in _DISPLAY_NAMES:
            locales[code] = _DISPLAY_NAMES[code]
    return locales
