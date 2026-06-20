"""
Locale file loader and translation function.

Loads JSON locale files from the locales/ directory, caches them,
and provides the t() translation function.
"""

import json
import threading
from pathlib import Path

# Directory containing locale subdirectories (e.g., locales/zh_CN/strings.json)
_LOCALES_DIR = Path(__file__).parent / "locales"

# Module-level state
_default_locale: str = "en"
_locale_lock = threading.Lock()

# Cache: locale_name -> flat dict of {english_key: translated_string}
_cache: dict[str, dict[str, str]] = {}


def _load_locale(locale: str) -> dict[str, str]:
    """Load and flatten a locale's strings from its JSON file.

    Args:
        locale: Locale identifier (e.g., "zh_CN")

    Returns:
        Flat dict mapping English keys to translated strings.
        Empty dict if the locale directory or file doesn't exist.
    """
    locale_dir = _LOCALES_DIR / locale
    strings_file = locale_dir / "strings.json"

    if not strings_file.exists():
        return {}

    try:
        data = json.loads(strings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    # The "strings" key contains the flat key-value mapping.
    # If the file is just a flat dict (no "strings" wrapper), use it directly.
    if "strings" in data and isinstance(data["strings"], dict):
        return data["strings"]

    # Fallback: try to flatten all non-metadata dict values
    flat: dict[str, str] = {}
    for key, value in data.items():
        if key == "metadata":
            continue
        if isinstance(value, dict):
            flat.update(value)
        elif isinstance(value, str):
            flat[key] = value
    return flat


def _get_locale_strings(locale: str) -> dict[str, str]:
    """Get cached locale strings, loading if needed."""
    if locale not in _cache:
        with _locale_lock:
            # Double-check after acquiring lock
            if locale not in _cache:
                _cache[locale] = _load_locale(locale)
    return _cache[locale]


def t(key: str, locale: str | None = None) -> str:
    """Translate a string to the active or specified locale.

    English is the identity locale: the key IS the English string,
    so no English locale file is needed. For non-English locales,
    the key is looked up in the locale's strings.json. If not found,
    the key itself is returned (graceful degradation).

    Args:
        key: The English string to translate (e.g., "Chart Overview")
        locale: Override locale. If None, uses the default locale.

    Returns:
        Translated string, or the key itself if no translation exists.
    """
    loc = locale or _default_locale

    # English is the identity function
    if loc == "en":
        return key

    strings = _get_locale_strings(loc)
    return strings.get(key, key)


def set_default_locale(locale: str) -> None:
    """Set the default locale for all subsequent t() calls.

    Args:
        locale: Locale identifier (e.g., "zh_CN", "en").
            Use "en" to reset to English (the default).
    """
    global _default_locale
    _default_locale = locale


def get_default_locale() -> str:
    """Get the current default locale.

    Returns:
        Current default locale identifier (e.g., "en", "zh_CN").
    """
    return _default_locale


def get_available_locales() -> list[str]:
    """List all available locales (those with a strings.json file).

    Always includes "en" (the identity locale, no file needed).

    Returns:
        Sorted list of locale identifiers.
    """
    locales = {"en"}

    if _LOCALES_DIR.exists():
        for locale_dir in _LOCALES_DIR.iterdir():
            if locale_dir.is_dir() and (locale_dir / "strings.json").exists():
                locales.add(locale_dir.name)

    return sorted(locales)


def reload_locale(locale: str) -> None:
    """Force reload a locale from disk (useful after editing locale files).

    Args:
        locale: Locale identifier to reload.
    """
    with _locale_lock:
        _cache.pop(locale, None)
