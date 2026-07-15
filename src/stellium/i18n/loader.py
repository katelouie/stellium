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


# The pseudolocale is synthesised, never loaded from disk — so it cannot go stale as the
# catalog grows. See pseudo.py.
PSEUDO_LOCALE = "qps"

# metadata blocks, cached alongside the strings
_metadata_cache: dict[str, dict] = {}


def _locale_metadata(locale: str) -> dict:
    """The locale file's ``metadata`` block ({} if there is no such locale)."""
    if locale not in _metadata_cache:
        strings_file = _LOCALES_DIR / locale / "strings.json"
        meta: dict = {}
        if strings_file.exists():
            try:
                data = json.loads(strings_file.read_text(encoding="utf-8"))
                if isinstance(data.get("metadata"), dict):
                    meta = data["metadata"]
            except (json.JSONDecodeError, OSError):
                meta = {}
        with _locale_lock:
            _metadata_cache[locale] = meta
    return _metadata_cache[locale]


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


def locale_chain(locale: str) -> list[str]:
    """The lookup order for a locale, most specific first, always ending at English.

    ``"zh_Hant_TW"`` → ``["zh_Hant_TW", "zh_Hant", "zh", "en"]``, so a regional locale
    inherits from its parent and overrides only what differs. A locale may also name an
    explicit parent via ``metadata.fallback``, which is inserted before English.
    """
    if locale == "en":
        return ["en"]

    chain: list[str] = []
    parts = locale.split("_")
    for i in range(len(parts), 0, -1):
        chain.append("_".join(parts[:i]))

    declared = _locale_metadata(locale).get("fallback")
    if isinstance(declared, str) and declared not in chain:
        chain.append(declared)

    chain.append("en")
    return chain


def t(key: str, locale: str | None = None) -> str:
    """Translate a string, walking the locale's fallback chain.

    English is the identity locale: the key IS the English string, so no English locale
    file is needed. If nothing in the chain defines the key, the key itself is returned —
    which for a *message* is already correct English, and is why a half-finished locale
    degrades to mixed-but-readable rather than to raw identifiers.

    Catalog keys (``body.Sun``) are the exception: the key is not English, so callers
    should go through :func:`stellium.i18n.render`, which falls back to the catalog's
    English value instead.

    Args:
        key: The English string, or a namespaced catalog key.
        locale: Override locale. If None, uses the default locale.

    Returns:
        Translated string, or the key itself if no translation exists.
    """
    loc = locale or _default_locale

    if loc == "en":
        return key

    if loc == PSEUDO_LOCALE:
        from stellium.i18n.pseudo import pseudo_translate

        pseudo = pseudo_translate(key)
        return pseudo if pseudo is not None else key

    for step in locale_chain(loc):
        if step == "en":
            break
        found = _get_locale_strings(step).get(key)
        if found is not None:
            return found
    return key


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
