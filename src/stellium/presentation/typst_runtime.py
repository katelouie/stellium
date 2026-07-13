"""The Typst runtime: where the design system lives, where the fonts live, and how a
document gets compiled.

Three subsystems render PDFs through Typst — the report, the planner and the atlas —
and each had grown its own copy of "find the fonts". All three disagreed, and two
were wrong:

    typst_render._font_paths()   -> stellium/data/fonts        ✅ packaged
    planner._get_font_dirs()     -> <repo>/assets/fonts        ❌ not in the wheel
    atlas._get_font_dirs()       -> <repo>/src/assets/fonts    ❌ never existed at all

The atlas copy was one `dirname()` short, because it lives a directory deeper than the
planner it was copied from — so its fonts had *never* worked, in any environment, and
nobody noticed because Typst silently substitutes. That is the whole argument for this
module: a path that is duplicated is a path that drifts, and Typst does not complain
when it drifts.

Everything a Typst consumer needs is here and is **public**. The report and the
planner previously reached across a package boundary for `typst_render._font_paths`
and `_theme_dir` — importing each other's underscore-prefixed privates, which is the
code *saying* "shared infrastructure" while *spelling* it "private".
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections.abc import Iterator, Sequence
from typing import Any

try:  # typst is an optional dependency
    import typst as _typst
except ImportError:  # pragma: no cover
    _typst = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# themes
# ---------------------------------------------------------------------------

THEMES = ("house", "sepia", "celestial", "blues", "greyscale")

THEME_LABELS = {
    "house": "House Style",
    "sepia": "Sepia",
    "celestial": "Celestial",
    "blues": "Blues",
    "greyscale": "Greyscale",
}

# The design-system modules every document imports. A document's own entry file
# (report.typ, planner.typ) is copied alongside them.
DESIGN_SYSTEM = (
    "palettes.typ",
    "glyphs.typ",
    "components.typ",
    "engine.typ",
)

# Per-theme wheel styling: (visualization theme, zodiac palette, aspect palette).
# Keeps an embedded chart wheel coherent with the PDF theme AND matching the PDF's
# own aspect colours (see theme-aspect-colors in palettes.typ). Greyscale is fully
# desaturated: grey wheel + greyscale aspects.
THEME_WHEEL = {
    "house": ("classic", "rainbow", "classic"),
    "sepia": ("classic", "rainbow_sepia", "sepia"),
    "celestial": ("celestial", "rainbow_celestial", "celestial"),
    "blues": ("midnight", "rainbow_midnight", "midnight"),
    "greyscale": ("classic", "grey", "greyscale"),
}


def validate_theme(theme: str) -> str:
    """Reject an unknown theme by name rather than rendering something surprising."""
    if theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}. Choose from: {', '.join(THEMES)}")
    return theme


# ---------------------------------------------------------------------------
# where things are
# ---------------------------------------------------------------------------


def theme_dir() -> str:
    """The bundled Typst design system (``presentation/typst_theme/``).

    Package-relative, so it resolves in a source checkout and an installed wheel
    alike — provided the ``.typ`` files actually *ship*, which they did not until
    issue #60. `tests/test_packaging.py` now guards that.
    """
    return os.path.join(os.path.dirname(__file__), "typst_theme")


def font_paths() -> list[str]:
    """The bundled font directory (``stellium/data/fonts``).

    Every display/body/mono face the themes use, plus the Noto symbol fonts, so a PDF
    renders identically on any machine with no dependency on host fonts. System fonts
    are still searched as well (``ignore_system_fonts`` stays False), but the bundle
    is self-sufficient.

    **This is the only correct answer, and it is the reason this module exists** — see
    the module docstring for the two wrong ones it replaces.
    """
    fonts = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # -> stellium/
        "data",
        "fonts",
    )
    return [fonts] if os.path.isdir(fonts) else []


# ---------------------------------------------------------------------------
# compiling
# ---------------------------------------------------------------------------


def typst_available() -> bool:
    """Whether the optional ``typst`` dependency is importable."""
    return _typst is not None


def require_typst() -> Any:
    """The typst module, or a clear error. Call this *before* doing expensive work —
    a planner spends seconds building charts, and discovering at the compile step
    that Typst was never installed is a poor way to spend them.
    """
    if _typst is None:
        raise RuntimeError(
            "Typst library not available. Install with: pip install typst"
        )
    return _typst


def compile_pdf(
    entry: str,
    *,
    root: str,
    sys_inputs: dict[str, str] | None = None,
) -> bytes:
    """Compile a ``.typ`` entry file to PDF bytes, with the bundled fonts available.

    ``root`` is the Typst project root. Callers pass their temp directory rather than
    ``/``: every file the document references is generated in there, and a POSIX root
    breaks on Windows when the temp dir lives on another drive.
    """
    return require_typst().compile(
        entry,
        root=root,
        font_paths=font_paths(),
        sys_inputs=sys_inputs or {},
    )


def materialize_svgs(
    sections: list[dict], root: str, seq: list[int] | None = None
) -> None:
    """Write any inline ``svg_content`` out to a file Typst can ``image()``.

    Recurses into compound subsections. Mutates in place: ``svg_content`` is replaced
    by ``svg_file`` (a name relative to the project root), because the SVG is often
    large and there is no reason to also ship it inside data.json.
    """
    if seq is None:
        seq = [0]

    for section in sections:
        if section.get("kind") == "svg" and section.get("svg_content"):
            seq[0] += 1
            name = f"embed_{seq[0]}.svg"
            with open(os.path.join(root, name), "w", encoding="utf-8") as fh:
                fh.write(section["svg_content"])
            section["svg_file"] = name
            del section["svg_content"]

        subsections = section.get("sections")
        if subsections:
            materialize_svgs(subsections, root, seq)


class TypstDocument:
    """A temporary Typst project with the design system copied into it.

    The report and the planner do the identical dance — temp dir, copy the design
    system, materialise SVGs, write data.json, compile with
    ``sys_inputs={theme, data}`` — so they do it here, once::

        with TypstDocument("report.typ", theme="sepia") as doc:
            doc.add_file("chart.svg", src=svg_path)
            pdf = doc.render(data, svg_sections=data["sections"])
    """

    def __init__(
        self,
        entry: str,
        theme: str,
        *,
        extra_templates: Sequence[str] = (),
        prefix: str = "stellium_typst_",
    ):
        self.entry = entry
        self.theme = validate_theme(theme)
        # Documents that add their own components (the planner does) name them here;
        # everything imports the shared DESIGN_SYSTEM.
        self.templates = (*DESIGN_SYSTEM, *extra_templates, entry)
        self._prefix = prefix
        self._tmp: tempfile.TemporaryDirectory | None = None

    def __enter__(self) -> TypstDocument:
        require_typst()
        self._tmp = tempfile.TemporaryDirectory(prefix=self._prefix)
        for filename in self.templates:
            shutil.copy2(
                os.path.join(theme_dir(), filename),
                os.path.join(self.root, filename),
            )
        return self

    def __exit__(self, *exc: object) -> None:
        if self._tmp is not None:
            self._tmp.cleanup()
            self._tmp = None

    @property
    def root(self) -> str:
        if self._tmp is None:
            raise RuntimeError("TypstDocument must be used as a context manager")
        return self._tmp.name

    def add_file(
        self, name: str, *, content: str | None = None, src: str | None = None
    ) -> str:
        """Put a file in the project root. Returns the name, for the data contract."""
        target = os.path.join(self.root, name)
        if src is not None:
            shutil.copy2(src, target)
        else:
            with open(target, "w", encoding="utf-8") as fh:
                fh.write(content or "")
        return name

    def render(self, data: dict, *, svg_sections: list[dict] | None = None) -> bytes:
        """Materialise SVGs, write the data contract, compile."""
        if svg_sections is not None:
            materialize_svgs(svg_sections, self.root)

        with open(os.path.join(self.root, "data.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)

        return compile_pdf(
            os.path.join(self.root, self.entry),
            root=self.root,
            sys_inputs={"theme": self.theme, "data": "data.json"},
        )


def iter_themes() -> Iterator[tuple[str, str]]:
    """(name, label) for every theme — for CLIs and galleries."""
    yield from ((name, THEME_LABELS[name]) for name in THEMES)
