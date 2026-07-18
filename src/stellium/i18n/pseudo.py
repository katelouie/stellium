"""The pseudolocale: a synthetic language that makes untranslated text *visible*.

"Has every section stopped stringifying?" cannot be answered by reading the code — a
leftover ``f"{sign} {deg}"`` in one branch of one section looks exactly like correct code,
and no linter will find it.

So ask the question mechanically instead. In the pseudolocale, every string that goes
through the i18n layer comes back **bracketed**::

    body.Sun          →  ⟦Ṡüṅ···⟧
    House ({system})  →  ⟦Ħöüṡé ({system})···⟧
    format.date       →  ⟦{day}/{month_num}/{year}⟧      (reordered on purpose)

Therefore any **unbracketed Latin text** in the output is, by construction, a string that
some section composed behind the contract's back. The i18n leak test and the
structure-first completeness test are the same test.

Two more properties fall out of the same artifact:

- **Expansion.** The padding simulates the ~35% growth of German and Russian, so a label
  that will clip its SVG box clips *here*, before a translator ever sees it.
- **Order.** The date pattern is deliberately reordered, proving nothing downstream
  assumes English word order.

It is *synthesised*, never loaded from disk, so it cannot drift as the catalog grows.

See docs/development/specs/STRUCTURE_FIRST_SECTIONS.md §9.
"""

from __future__ import annotations

import re

OPEN = "⟦"
CLOSE = "⟧"
PAD = "·"

# Enough to look foreign and to survive a round-trip through the renderers, while staying
# recognisably the same word to a human reading a diff.
_ACCENTS = str.maketrans(
    "aeiouyAEIOUYcdnsztgrlbmpfhwkvjxCDNSZTGRLBMPFHWKVJX",
    "áéíóúýÁÉÍÓÚÝçđñšžŧǥŕłƀɱƥƒħŵķvǰxÇĐÑŠŽŦǤŔŁƁṀƤƑĦŴĶVǰX",
)

# {slot} and {slot:spec} must survive verbatim — they are the contract with the caller.
_SLOT = re.compile(r"\{[^{}]*\}")

# Formats are patterns, not words. Reordering them is the point, so they are given
# explicit pseudo values rather than being transliterated.
_PSEUDO_FORMATS: dict[str, str] = {
    "format.date": f"{OPEN}{{day}}/{{month_num}}/{{year}}{CLOSE}",
    "format.time": f"{OPEN}{{minute}}h{{hour24}}{CLOSE}",
    "format.datetime": f"{OPEN}{{time}} {{date}}{CLOSE}",
    "format.degrees": f"{OPEN}{{min:02d}}'{{deg}}°{CLOSE}",
    "format.decimal_sep": ",",
    "format.latitude": f"{OPEN}{{hemisphere}}{{value}}°{CLOSE}",
    "format.longitude": f"{OPEN}{{hemisphere}}{{value}}°{CLOSE}",
}

# ~35% expansion, the documented worst case for English → German/Russian.
_EXPANSION = 0.35


def _accent(text: str) -> str:
    """Transliterate the words, leaving {slots} and punctuation alone."""
    parts = []
    last = 0
    for match in _SLOT.finditer(text):
        parts.append(text[last : match.start()].translate(_ACCENTS))
        parts.append(match.group(0))
        last = match.end()
    parts.append(text[last:].translate(_ACCENTS))
    return "".join(parts)


def _bracket(source: str) -> str:
    body = _accent(source)
    visible = len(_SLOT.sub("", body))
    padding = PAD * max(1, round(visible * _EXPANSION))
    return f"{OPEN}{body}{padding}{CLOSE}"


def pseudo_message(template: str) -> str:
    """Pseudo-ise a message template, preserving its slots."""
    return _bracket(template)


def pseudo_translate(key: str) -> str | None:
    """The pseudolocale's value for a **known** key, or None if the key is not one.

    Partial on purpose. A *total* pseudolocale would return a bracketed value for any
    string handed to it — and the legacy translator hands it arbitrary cell content, so
    ``Albert Einstein`` and ``March 14, 1879`` would come back bracketed too. Everything
    would look translated, and an oracle that brackets everything proves nothing.

    Bracketing must mean exactly one thing: *this went through the catalog*. So an
    unknown key passes through untouched, and shows up in the output as the English it
    always was.
    """
    if key in _PSEUDO_FORMATS:
        return _PSEUDO_FORMATS[key]

    from stellium.i18n.catalog import english

    if english(key) is None:
        return None

    # A catalog key's *last segment* is the word — "body.Sun" should read as ⟦Ṡüṅ⟧, not
    # as ⟦ḃöḋẏ.Ṡüṅ⟧.
    source = key.rsplit(".", 1)[-1]
    if source == "short":  # "house_system.Placidus.short"
        source = key.rsplit(".", 2)[-2]
    return _bracket(source)


def find_leaks(text: str) -> list[str]:
    """Latin word-runs in pseudolocale output that never went through the i18n layer.

    Strips everything inside ⟦…⟧ — that part is accounted for — and reports what English
    is left. Callers allow-list the do-not-translate values (a person's name, a geocoded
    place, an IANA timezone), which are slot *values* and correctly never translated.
    """
    outside = re.sub(f"{OPEN}[^{CLOSE}]*{CLOSE}", " ", text)
    return re.findall(r"[A-Za-z][A-Za-z'’./-]{2,}", outside)
