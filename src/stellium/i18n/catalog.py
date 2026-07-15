"""The closed vocabulary: every astrological term that can be translated.

Built **from the registries**, so a body added to ``CELESTIAL_REGISTRY`` gains a catalog
key with no edit here. That is the point — the previous translation layer kept a
hand-written list of ~90 terms which had already drifted from both the registries and the
locale data.

Keys are **namespaced**, and the namespace is what carries context::

    body.Sun    sign.Cancer    aspect.Square    modality.Fixed    star.Fixed

A flat English word list cannot express that ``Fixed`` is a modality in one column and a
star classification in another, so a translator has to guess — and guesses wrong silently.
Namespacing is the fix, and it is also what lets a locale file be reviewed by someone who
has never seen the code.

Vocabularies that already have a canonical home are derived from it. Signs, moon phases,
motion states and dignities do not have one (the twelve signs are spelled out in 19
separate modules), so this module declares them and should become that home.

See docs/development/specs/STRUCTURE_FIRST_SECTIONS.md §4.2.
"""

from __future__ import annotations

from functools import lru_cache

from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    ELEMENTS,
    FIXED_STARS_REGISTRY,
    MODALITIES,
)
from stellium.engines.houses import HOUSE_SYSTEM_CODES

# --- vocabularies with no canonical home elsewhere -------------------------------------

SIGNS: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

# The names `PhaseData.phase_name` actually returns — "New", not "New Moon". The report
# sections say "New Moon"; that difference belongs in a *message*, not in the catalog.
PHASES: tuple[str, ...] = (
    "New",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full",
    "Waning Gibbous",
    "Last Quarter",
    "Waning Crescent",
)

MOTIONS: tuple[str, ...] = ("Direct", "Retrograde", "Stationary")

DIGNITIES: tuple[str, ...] = (
    "Domicile",
    "Exaltation",
    "Detriment",
    "Fall",
    "Triplicity",
    "Term",
    "Face",
    "Peregrine",
)

SECTS: tuple[str, ...] = ("Day", "Night")

ASPECT_MOTIONS: tuple[str, ...] = ("Applying", "Separating")

# The cardinal coordinate directions. Their English *is* the single letter a chart prints
# after a latitude/longitude ("47.60°N"); a locale translates the letter and reorders it
# via the format.latitude / format.longitude pattern (Chinese writes "北47.60°").
DIRECTIONS: tuple[str, ...] = ("N", "S", "E", "W")

# Elemental polarity, as the report's snapshot names it. "Yang"/"Yin" are the attested
# terms even in English astrology; a Chinese chart renders them with the native 陽/陰.
POLARITIES: tuple[str, ...] = ("Yang", "Yin", "Balanced")


def _house_short_forms() -> dict[str, str]:
    """The English short forms, from the one implementation that has all 17 systems."""
    from stellium.presentation.sections._utils import HOUSE_ABBREVIATIONS

    return HOUSE_ABBREVIATIONS["en"]


@lru_cache(maxsize=1)
def build_catalog() -> dict[str, str]:
    """Every catalog key mapped to its English display string.

    The English value — never the key — is what a term falls back to when a locale has no
    translation for it. Returning ``"body.Sun"`` to a reader would be worse than not
    translating at all.
    """
    catalog: dict[str, str] = {}

    for name, info in CELESTIAL_REGISTRY.items():
        catalog[f"body.{name}"] = info.display_name or name

    for name in ASPECT_REGISTRY:
        catalog[f"aspect.{name}"] = name

    shorts = _house_short_forms()
    for name in HOUSE_SYSTEM_CODES:
        catalog[f"house_system.{name}"] = name
        if name in shorts:
            catalog[f"house_system.{name}.short"] = shorts[name]

    for name in FIXED_STARS_REGISTRY:
        catalog[f"star.{name}"] = name

    for namespace, names in (
        ("sign", SIGNS),
        ("element", ELEMENTS),
        ("modality", MODALITIES),
        ("phase", PHASES),
        ("motion", MOTIONS),
        ("dignity", DIGNITIES),
        ("sect", SECTS),
        ("aspect_motion", ASPECT_MOTIONS),
        ("direction", DIRECTIONS),
        ("polarity", POLARITIES),
    ):
        for name in names:
            catalog[f"{namespace}.{name}"] = name

    # A short form for the one place a narrow column abbreviates it (the PDF motion
    # column prints "Retro"). Everything else falls back to the full term.
    catalog["motion.Retrograde.short"] = "Retro"

    return catalog


def english(key: str) -> str | None:
    """The English display string for a catalog key, or None if it isn't one."""
    catalog = build_catalog()
    if key in catalog:
        return catalog[key]
    # A `.short` with no short form defined falls back to the full term.
    if key.endswith(".short"):
        return catalog.get(key[: -len(".short")])
    return None


def namespaces() -> dict[str, list[str]]:
    """Catalog keys grouped by namespace — the shape a translator's worklist wants."""
    grouped: dict[str, list[str]] = {}
    for key in build_catalog():
        grouped.setdefault(key.split(".", 1)[0], []).append(key)
    return {ns: sorted(keys) for ns, keys in sorted(grouped.items())}
