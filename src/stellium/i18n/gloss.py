"""Gloss: a concept resolved for a locale, carrying both its identity and its mask.

The i18n bugs all shared one root cause: the resolve pass flattened a ``Term`` into its
localized display string *too early*, so downstream machinery — the Typst mappers, section
dispatch, glyph lookup — had no identity left to match on. A ``Gloss`` keeps both
dimensions coupled so nothing has to choose between them:

- ``.en``  — the **identity**. The internal language everything matches on; machinery reads
  it (a dict key, an ``==``, a glyph lookup).
- ``.loc`` — the **presentation**. The mask a renderer flips on at the very last step.

It is deliberately **not** a ``str`` subclass. ``==`` and ``hash`` delegate to ``.en`` so a
``Gloss`` still works as a dict key and compares equal to its English string — but a string
*operation* (``.upper()``, slicing, ``+``) fails loudly rather than silently returning
English and dropping the mask. And ``__str__`` returns ``.en``, so a renderer that forgets
``.loc`` leaks **visible English**, which the pseudolocale completeness oracle catches
mechanically. Silent-wrong output is impossible by construction.

See docs/development/specs/UNIFIED_RENDERER_CONTRACT.md §4.
"""

from __future__ import annotations

from typing import Any

from stellium.i18n.message import Term, render


class Gloss:
    """A concept resolved for one locale: identity (``en``) + display mask (``loc``)."""

    __slots__ = ("en", "loc", "key")

    def __init__(self, en: str, loc: str | None = None, key: str | None = None) -> None:
        self.en = en
        self.loc = en if loc is None else loc
        self.key = key

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Gloss):
            return self.en == other.en
        return self.en == other

    def __hash__(self) -> int:
        return hash(self.en)

    def __str__(self) -> str:
        # The identity, never the mask — a forgotten .loc leaks visible English, not a
        # silent lookup failure. The oracle catches English; it cannot catch silence.
        return self.en

    def __repr__(self) -> str:
        return f"Gloss({self.en!r}→{self.loc!r})"


def gloss(value: Any, locale: str) -> Gloss:
    """Resolve a Term / Message / date / string into a ``Gloss``.

    Both dimensions go through the same :func:`~stellium.i18n.message.render`, so a
    Message's slots and a list join localize consistently in each. A plain string with no
    translation glosses to itself (``en == loc``); a catalog ``Term`` carries its ``key``
    for the finest identity (glyph/colour lookup).
    """
    key = value.key if isinstance(value, Term) else None
    return Gloss(en=render(value, "en"), loc=render(value, locale), key=key)


def display(value: Any) -> Any:
    """The presentation of a value: a ``Gloss``'s ``.loc`` mask, else the value unchanged.

    What a renderer calls at its display edge — the one place the mask is flipped *on* for
    the user. (The identity underneath is ``.en``; this returns what is shown, not that.)
    """
    return value.loc if isinstance(value, Gloss) else value


def display_all(value: Any) -> Any:
    """Deep-flatten a structure to its presentation: every ``Gloss`` → its ``.loc`` mask.

    A text renderer applies this once at its boundary, *after* any machinery has read the
    ``.en`` identities, so its internals can stay plain-string. Dict keys flip too, so a
    key_value's localized labels appear.
    """
    if isinstance(value, Gloss):
        return value.loc
    if isinstance(value, dict):
        return {display_all(k): display_all(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(display_all(v) for v in value)
    return value
