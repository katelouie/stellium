"""
Stellium internationalization (i18n) system.

Provides locale-aware string translation for report output, chart labels,
and astrology terminology.

Usage:
    from stellium.i18n import t, set_default_locale, get_available_locales

    # Translate a string (defaults to English passthrough)
    label = t("Chart Overview")  # "Chart Overview"

    # Set a different default locale
    set_default_locale("zh_CN")
    label = t("Chart Overview")  # "星盘概览"

    # Override locale per-call
    label = t("Chart Overview", locale="zh_CN")  # "星盘概览"

    # List available locales
    print(get_available_locales())  # ["en", "zh_CN"]

Design notes:
    - English is the identity locale: keys ARE the English strings, so no
      English locale file is needed.
    - Unknown keys return the key itself (graceful degradation).
    - Locale files are loaded lazily and cached.
    - Thread-safe: the default locale is a module-level string, but the
      translation lookup is pure (no mutation during read).
"""

from stellium.i18n.loader import (
    get_available_locales,
    get_default_locale,
    set_default_locale,
    t,
)

__all__ = [
    "t",
    "set_default_locale",
    "get_default_locale",
    "get_available_locales",
]
