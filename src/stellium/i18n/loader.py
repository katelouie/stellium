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


# Groups whose keys are already the full lookup string (an English message, or a bare
# catalog term the legacy translator still looks up), so they flatten *without* a prefix.
# Every other group is a namespace and prefixes its keys with the group name — that
# prefix is exactly what keeps ``body.Earth`` and ``element.Earth`` from colliding, the
# collision the old no-prefix flatten produced.
_PASSTHROUGH_GROUPS = frozenset({"message", "legacy"})


def _flatten_locale(data: dict) -> dict[str, str]:
    """Flatten a nested locale document to dotted keys, preserving the namespace prefix.

    ``{"body": {"Sun": "太阳"}}`` → ``{"body.Sun": "太阳"}``. Keys inside a passthrough
    group are used verbatim. A key that already contains a dot (``"Placidus.short"``
    under ``house_system``) simply extends the path: ``house_system.Placidus.short``.

    The inverse is :func:`_nest_locale`; the two are mutual inverses on a well-formed
    document (see ``test_i18n_locale_roundtrip``).
    """
    flat: dict[str, str] = {}
    for group, entries in data.items():
        if group == "metadata" or not isinstance(entries, dict):
            continue
        prefix = "" if group in _PASSTHROUGH_GROUPS else f"{group}."
        for key, value in entries.items():
            if isinstance(value, str):
                flat[f"{prefix}{key}"] = value
    return flat


def _key_group(dotted_key: str, namespaces: frozenset[str]) -> tuple[str, str]:
    """Which group a flat key belongs to, and its key within that group.

    The inverse of the prefix rule in :func:`_flatten_locale`. A key is namespaced only
    if its first dot-segment is a *known* namespace — so ``body.Sun`` splits to
    ``("body", "Sun")`` but ``"No eclipses in this period."`` (a full English sentence
    that merely contains a dot) does not, and stays whole in a passthrough group.
    """
    head = dotted_key.split(".", 1)[0]
    if "." in dotted_key and head in namespaces:
        return head, dotted_key.split(".", 1)[1]
    return "", dotted_key  # passthrough: the key is already the full lookup string


def _nest_locale(
    flat: dict[str, str],
    metadata: dict | None = None,
    legacy_keys: frozenset[str] = frozenset(),
) -> dict:
    """Rebuild the grouped document from a flat dotted mapping — the inverse of flatten.

    Namespaced keys nest under their namespace. Everything else is a passthrough key
    (an English message string), which goes to the ``legacy`` group if it is named in
    ``legacy_keys`` — the bare catalog duplicates the pre-format-last renderer looks up
    — and to ``message`` otherwise. ``legacy_keys`` is the one thing flatten discards
    (both passthrough groups flatten to bare keys), so pass it to recover the split;
    omit it and every passthrough key lands in ``message``, which is still lossless as a
    key/value mapping.
    """
    from stellium.i18n.catalog import namespaces as catalog_namespaces

    known = frozenset(catalog_namespaces()) | {"format"}
    groups: dict[str, dict[str, str]] = {}
    for key, value in flat.items():
        group, subkey = _key_group(key, known)
        if not group:
            group = "legacy" if key in legacy_keys else "message"
        groups.setdefault(group, {})[subkey] = value

    doc: dict = {"metadata": metadata or {}}
    catalog_ns = sorted(k for k in groups if k not in {"format", "message", "legacy"})
    for name in catalog_ns:
        doc[name] = dict(sorted(groups[name].items()))
    for tail in ("format", "message", "legacy"):
        if groups.get(tail):
            doc[tail] = dict(sorted(groups[tail].items()))
    return doc


def _load_locale(locale: str) -> dict[str, str]:
    """Load and flatten a locale's strings from its JSON file.

    The file is grouped by namespace (``body``, ``sign``, ``house_system``, ``format``,
    ``message``, ``legacy``); this returns the flat dotted-key mapping the rest of the
    system looks up. See :func:`_flatten_locale`.

    Args:
        locale: Locale identifier (e.g., "zh_CN")

    Returns:
        Flat dict mapping dotted keys to translated strings. Empty if the locale file
        does not exist.
    """
    strings_file = _LOCALES_DIR / locale / "strings.json"

    if not strings_file.exists():
        return {}

    try:
        data = json.loads(strings_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    # A legacy flat file kept its strings under a "strings" wrapper; the grouped format
    # puts namespaces at the top level. Support both so an old file still loads.
    if "strings" in data and isinstance(data["strings"], dict):
        return data["strings"]

    return _flatten_locale(data)


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


def resolved_coverage(locale: str) -> tuple[int, int]:
    """``(translated, total)`` catalog terms this locale resolves through its chain.

    Counts each catalog key that resolves to a non-English value *somewhere* in the
    fallback chain (excluding English) — so a base-plus-override locale like
    ``zh_Hant_TW`` reports its true coverage (base + overrides), not just the handful of
    keys in its own file.
    """
    from stellium.i18n.catalog import build_catalog

    catalog = build_catalog()
    steps = [s for s in locale_chain(locale) if s != "en"]
    translated = sum(
        any(_get_locale_strings(step).get(key) is not None for step in steps)
        for key in catalog
    )
    return translated, len(catalog)


def available_locales_info() -> list[dict]:
    """Every available locale with its language, status, coverage and fallback chain.

    The at-a-glance companion to :func:`get_available_locales` (which returns bare codes)
    and ``stellium i18n coverage <locale>`` (which details one). English is the identity
    locale — fully covered by definition, no file.
    """
    from stellium.i18n.catalog import build_catalog

    total = len(build_catalog())
    info = []
    for code in get_available_locales():
        if code == "en":
            info.append(
                {
                    "code": "en",
                    "language": "English",
                    "status": "identity",
                    "coverage": (total, total),
                    "chain": ["en"],
                }
            )
            continue
        meta = _locale_metadata(code)
        info.append(
            {
                "code": code,
                "language": meta.get("language", code),
                "status": meta.get("status", "unknown"),
                "coverage": resolved_coverage(code),
                "chain": locale_chain(code),
            }
        )
    return info


def reload_locale(locale: str) -> None:
    """Force reload a locale from disk (useful after editing locale files).

    Args:
        locale: Locale identifier to reload.
    """
    with _locale_lock:
        _cache.pop(locale, None)
