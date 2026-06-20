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
    """Get cached locale strings."""
    if locale not in _cache:
        _cache[locale] = _load_locale(locale)
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


def get_available_locales() -> dict[str, str]:
    """Get available locales as {code: display_name} dict."""
    locales = {"en": "English"}

    for f in _LOCALES_DIR.glob("*.json"):
        code = f.stem
        # Try to read the language name from metadata
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            lang = data.get("metadata", {}).get("language", code)
            # Map known codes to display names
            display_names = {
                "zh-CN": "简体中文",
                "zh_CN": "简体中文",
                "ja": "日本語",
                "ko": "한국어",
            }
            locales[code] = display_names.get(lang, display_names.get(code, code))
        except Exception:
            locales[code] = code

    return locales
