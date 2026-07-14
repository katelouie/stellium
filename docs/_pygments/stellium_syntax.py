"""The syntax palette from the design, as a real Pygments style.

The docs shipped Pygments' stock **monokai** — magenta keywords, amber strings — while
the design (and every mockup) specifies five colours:

    keyword   #c4b5fd     string    #a3d0a8
    call      #e8c07d     comment   #6b6d82
    class     #7fd0a8

`StelliumStyle` is that palette. It sets no background: the theme paints the block
from `--code-bg`, which differs between light and dark, so a style-level background
would only fight it.

`StelliumPythonLexer` is the part that is not just a colour table. Pygments' Python
lexer tags a name as `Name.Function` **only where it is defined** — `def calculate():`
— so in a call it is a plain `Name`, indistinguishable from a variable. For a library
whose entire public API is a method chain, that is precisely the wrong thing to leave
uncoloured:

    chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate())

`CallFilter` re-tags any name immediately followed by `(` — as a call, which is what it
is. A capitalised one becomes `Name.Class`, which is the convention the code already
follows and the distinction the mockups draw (`PlacidusHouses` green, `.calculate`
gold).
"""

from __future__ import annotations

from pygments.filter import Filter
from pygments.lexers.python import PythonLexer
from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

KEYWORD = "#c4b5fd"  # from, import, class, def, for, in, as, True
CALL = "#e8c07d"  # .from_notable, .calculate, .draw, print
STRING = "#a3d0a8"  # "Albert Einstein"
CLASS = "#7fd0a8"  # PlacidusHouses, ModernAspectEngine, list, float
COMMENT = "#6b6d82"  # # lazy — nothing runs until here

# Identifiers, operators and punctuation are *not* coloured here. They must inherit
# `--code-fg`, which is #dee0ec in light and #dbdce9 in dark — and a Pygments style can
# only name one colour. Emitting nothing lets `.highlight pre { color: var(--code-fg) }`
# do it, so the one token that legitimately differs between themes keeps differing.
INHERIT = ""


class StelliumStyle(Style):
    """The five design colours, mapped onto Pygments' token tree."""

    # The theme paints the block from --code-bg; a background here would only fight it.
    background_color = "transparent"
    line_number_color = COMMENT

    styles = {
        Text: INHERIT,
        Whitespace: INHERIT,
        Name: INHERIT,
        Operator: INHERIT,
        Punctuation: INHERIT,
        Error: "#e06c75",
        Comment: f"italic {COMMENT}",
        Comment.Preproc: COMMENT,
        Keyword: KEYWORD,
        Keyword.Constant: KEYWORD,  # True / False / None
        Keyword.Namespace: KEYWORD,  # import / from
        Operator.Word: KEYWORD,  # and / or / not / in
        Name.Function: CALL,
        Name.Function.Magic: CALL,
        Name.Class: CLASS,
        Name.Exception: CLASS,
        Name.Decorator: CLASS,
        # `list`, `float`, `dict` — used as types, they read as types. Used as calls,
        # CallFilter promotes them to Name.Function first, so `print(...)` comes out
        # gold and the annotation `-> list[str]` comes out green. Same token, and the
        # difference between them is exactly whether it is being *called*.
        Name.Builtin: CLASS,
        Name.Builtin.Pseudo: KEYWORD,  # self, cls
        String: STRING,
        String.Doc: f"italic {COMMENT}",
        String.Escape: CALL,
        String.Interpol: INHERIT,
        Number: CALL,
        Generic.Output: INHERIT,
        Generic.Prompt: COMMENT,
        Generic.Emph: "italic",
        Generic.Strong: "bold",
    }


class CallFilter(Filter):
    """Re-tag `foo(` as a call, and `Foo(` as a class.

    Pygments only marks a name as a function where it is *defined*, so every method in
    a fluent chain arrives as a bare `Name`. This looks one token ahead — skipping the
    whitespace a call may legally contain — and promotes the name if what follows is an
    opening parenthesis.
    """

    def filter(self, lexer, stream):  # noqa: A003 - Pygments' interface
        pending: tuple | None = None
        held: list[tuple] = []

        for ttype, value in stream:
            if pending is not None:
                # Whitespace between the name and its `(` is legal: hold and keep looking.
                if ttype in Text and not value.strip():
                    held.append((ttype, value))
                    continue

                is_call = ttype in Punctuation and value == "("
                if is_call:
                    name = pending[1]
                    promoted = Name.Class if name[:1].isupper() else Name.Function
                    yield promoted, name
                else:
                    yield pending

                yield from held
                pending, held = None, []

            if ttype in Name and (ttype in Name.Builtin or ttype is Name):
                pending = (ttype, value)
                continue

            yield ttype, value

        if pending is not None:
            yield pending
            yield from held


class StelliumPythonLexer(PythonLexer):
    """PythonLexer that knows a call when it sees one."""

    name = "StelliumPython"
    aliases = ["python", "py"]

    def __init__(self, **options):
        super().__init__(**options)
        self.add_filter(CallFilter())
