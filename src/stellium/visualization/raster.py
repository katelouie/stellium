"""Rasterise chart SVGs to PNG, without tofu.

An astrology chart is mostly *text*: ☉ ♀ ♄ for the planets, ♈ ♉ ♊ for the signs, ℞ for
retrograde, plus names, degrees and house numbers. In an SVG those are ``<text>``
elements naming a font family — and **every general-purpose rasteriser resolves that
family against the host's installed fonts.** rsvg, cairosvg, Inkscape, browsers: all
of them. On a machine without a symbol font, the chart comes out full of tofu boxes.
That is not a bug in those tools; it is what they are for.

We solve it by not asking the host anything. Stellium already **bundles** every font
its charts need (see ``data/fonts/`` and ``tests/test_glyph_coverage.py``, which
asserts that every glyph the registries emit is in one of them), and it already
depends on Typst, which can rasterise with ``ignore_system_fonts=True``.

So the PNG is rendered by Typst using *only* the bundled fonts. The output is
byte-identical on a developer's laptop, in CI, and in a bare container with no fonts
installed — which is the entire point of exporting a PNG in the first place.

    chart.draw("chart.svg").preset_standard().save_png("chart.png", scale=2)
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from stellium.presentation.typst_runtime import compile_png

# SVG's own default when a root <svg> gives no width/height.
_FALLBACK_WIDTH = 800.0

_LENGTH = re.compile(r"^\s*([0-9.]+)\s*(px|pt)?\s*$", re.IGNORECASE)

_HEX = re.compile(r"^#(?:[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", re.IGNORECASE)

# Typst's built-in colour identifiers. `rgb()` takes hex only, so a named colour has
# to be passed as a bare token — `rgb("white")` is an error, not a colour.
_NAMED = {
    "black",
    "gray",
    "silver",
    "white",
    "navy",
    "blue",
    "aqua",
    "teal",
    "eastern",
    "purple",
    "fuchsia",
    "maroon",
    "red",
    "orange",
    "yellow",
    "olive",
    "green",
    "lime",
}


def _fill(background: str | None) -> str:
    """A Typst colour expression for the page fill."""
    if background is None:
        return "none"

    value = background.strip()
    if _HEX.match(value):
        return f'rgb("{value}")'

    name = "gray" if value.lower() == "grey" else value.lower()
    if name in _NAMED:
        return name

    raise ValueError(
        f"background must be a hex colour ('#faf8f5') or one of {sorted(_NAMED)}; "
        f"got {background!r}"
    )


def _svg_width(svg: str) -> float:
    """The SVG's intrinsic width in user units, so `scale` means what it says.

    Prefers the root ``width``; falls back to the viewBox, then to a default. The
    *root* attribute matters — a chart embeds nested ``<svg>`` elements for the
    hand-drawn glyphs, and matching one of those would scale the output to 12px.
    """
    root = re.search(r"<svg\b[^>]*>", svg)
    if root:
        attrs = root.group(0)
        width = re.search(r'\bwidth="([^"]+)"', attrs)
        if width:
            match = _LENGTH.match(width.group(1))
            if match:
                return float(match.group(1))

        viewbox = re.search(r'\bviewBox="([^"]+)"', attrs)
        if viewbox:
            parts = viewbox.group(1).replace(",", " ").split()
            if len(parts) == 4:
                try:
                    return float(parts[2])
                except ValueError:
                    pass

    return _FALLBACK_WIDTH


def svg_to_png(
    svg: str | Path,
    *,
    scale: float = 2.0,
    background: str | None = None,
    extra_fonts: list[str] | None = None,
) -> bytes:
    """Rasterise SVG markup (or a path to an ``.svg``) to PNG bytes.

    Args:
        svg: SVG markup, or a path to a file containing it.
        scale: Pixels per SVG user unit. ``scale=2`` renders an 800-unit-wide chart at
            1600px — the usual choice for a retina display or a print-quality asset.
        background: A CSS colour for the page (``"white"``, ``"#faf8f5"``). Default is
            **transparent**, which is what you want for compositing; pass ``"white"``
            if the target cannot handle an alpha channel.

    Returns:
        PNG bytes.

    Raises:
        RuntimeError: If the optional ``typst`` dependency is not installed.
    """
    markup = _read(svg)
    width = _svg_width(markup)

    fill = _fill(background)

    with tempfile.TemporaryDirectory(prefix="stellium_png_") as root:
        (Path(root) / "chart.svg").write_text(markup, encoding="utf-8")

        # width: auto + an explicit image width means the page is exactly the image,
        # with no margin. ppi then converts user units to pixels: at 72 ppi one unit is
        # one pixel, so `scale` is simply a multiplier on that.
        (Path(root) / "raster.typ").write_text(
            f"#set page(width: auto, height: auto, margin: 0pt, fill: {fill})\n"
            f'#image("chart.svg", width: {width}pt)\n',
            encoding="utf-8",
        )

        return compile_png(
            os.path.join(root, "raster.typ"),
            root=root,
            ppi=72.0 * scale,
            extra_fonts=extra_fonts,
        )


def _read(svg: str | Path) -> str:
    """Accept markup or a path, and tell them apart without guessing."""
    if isinstance(svg, Path):
        return svg.read_text(encoding="utf-8")
    if "<svg" in svg:
        return svg
    return Path(svg).read_text(encoding="utf-8")


class RasterMixin:
    """``.to_png()`` / ``.save_png()`` for any builder that can ``save(to_string=True)``.

    A mixin rather than a copy in each builder — three subsystems each growing their
    own font-path helper is what produced today's other bugs, and this is the same
    shape of temptation.
    """

    def to_png(self, *, scale: float = 2.0, background: str | None = None) -> bytes:
        """Render to PNG bytes.

        Rasterised by Typst using **only Stellium's bundled fonts**, so the glyphs come
        out identical on every machine. A general-purpose SVG rasteriser resolves fonts
        against the *host*, and will cheerfully render every zodiac sign as a tofu box
        on a system with no symbol font installed.

        Args:
            scale: Pixels per SVG unit. ``2.0`` gives a retina-density image.
            background: Page colour. Default transparent; pass ``"white"`` for viewers
                that cannot cope with an alpha channel.
        """
        return svg_to_png(
            self.save(to_string=True),  # type: ignore[attr-defined]
            scale=scale,
            background=background,
            extra_fonts=self._extra_font_dirs(),
        )

    def _extra_font_dirs(self) -> list[str]:
        """Directories for an explicit ``with_font`` path (Typst searches directories).

        The bundled fonts and downloaded packs are already on the path; this adds only a
        font the caller pointed at directly. A file contributes its parent directory.
        """
        font = getattr(self, "_font", None)
        if not font:
            return []
        p = Path(font)
        return [str(p if p.is_dir() else p.parent)]

    def save_png(
        self,
        filename: str | None = None,
        *,
        scale: float = 2.0,
        background: str | None = None,
    ) -> str:
        """Render to a PNG file. Returns the filename written.

        Defaults to the SVG's own filename with a ``.png`` suffix, so
        ``chart.draw("einstein.svg").save_png()`` writes ``einstein.png``.
        """
        if filename is None:
            base = getattr(self, "_filename", None) or "chart.svg"
            filename = str(Path(base).with_suffix(".png"))

        Path(filename).write_bytes(self.to_png(scale=scale, background=background))
        return filename
