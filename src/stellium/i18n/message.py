"""Terms and messages: the two things a section can emit instead of a display string.

The old translation layer ran *after* formatting, so it could only find-and-replace on
finished strings — which cannot reorder, and therefore cannot produce ``1879年3月14日``
from ``March 14, 1879``. These two types let a section hand the renderer *structure*, so
the string is composed last, in a locale:

    >>> render(msg("House ({system})",
    ...            system=term("house_system.Placidus", short=True)), "en")
    'House (Pl)'

The message key **is** the English template, so an untranslated locale still renders
correct English, and a translator opening the locale file can see the slots they must
preserve. A translated template may reorder those slots freely — that is the whole point.

See docs/development/specs/STRUCTURE_FIRST_SECTIONS.md §4.3.
"""

from __future__ import annotations

import string
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from stellium.i18n.catalog import english
from stellium.i18n.loader import PSEUDO_LOCALE, t


@dataclass(frozen=True)
class Term:
    """A reference to the closed vocabulary — a body, sign, aspect, house system…

    ``key`` is namespaced (``body.Sun``), which is what lets a translator tell
    ``modality.Fixed`` from ``star.Fixed``.
    """

    key: str
    short: bool = False


@dataclass(frozen=True)
class Message:
    """An English template plus named slots. Slot values are themselves renderable."""

    template: str
    slots: Mapping[str, Any]


def term(key: str, *, short: bool = False) -> Term:
    """Reference a catalog term. ``short=True`` asks for the abbreviated form."""
    return Term(key=key, short=short)


def msg(template: str, **slots: Any) -> Message:
    """An English template with named slots: ``msg("House ({system})", system=...)``."""
    return Message(template=template, slots=slots)


def _slot_names(template: str) -> set[str]:
    return {
        name for _, name, _, _ in string.Formatter().parse(template) if name is not None
    }


def _render_term(value: Term, locale: str) -> str:
    """Resolve a term, falling back to *English* — never to the raw key.

    ``t()`` returns the key when a translation is missing, which is right for a message
    (the key is already English) and wrong for a term (``body.Sun`` is not a word). So a
    term that misses resolves through the catalog instead.
    """
    lookup = f"{value.key}.short" if value.short else value.key

    translated = t(lookup, locale=locale)
    if translated != lookup:
        return translated

    # No translation for the short form? Try the long one before giving up on the locale.
    if value.short:
        long_translated = t(value.key, locale=locale)
        if long_translated != value.key:
            return long_translated

    return english(lookup) or english(value.key) or value.key


def render(value: Any, locale: str | None = None) -> str:
    """Render a Term, a Message, or anything else, into a string in ``locale``.

    A plain ``str`` passes through untouched. That is deliberate: it is the bridge that
    lets sections and renderers migrate to structure one file at a time without breaking
    the ones that haven't (spec §7.1).
    """
    if isinstance(value, str):
        return value

    if isinstance(value, Term):
        return _render_term(value, locale or "en")

    if isinstance(value, Message):
        if locale == PSEUDO_LOCALE:
            # Message keys are written at call sites and cannot be enumerated up front,
            # so the pseudolocale brackets the template here, where we hold it.
            from stellium.i18n.pseudo import pseudo_message

            template = pseudo_message(value.template)
        else:
            template = t(value.template, locale=locale)
        rendered = {k: render(v, locale) for k, v in value.slots.items()}

        # A translation that invents a slot would raise KeyError mid-chart. A bad
        # translation should degrade, not crash: fall back to the English template.
        # `stellium i18n coverage` reports these so they can actually be fixed.
        if not _slot_names(template) <= set(rendered):
            template = value.template

        return template.format(**rendered)

    return str(value)
