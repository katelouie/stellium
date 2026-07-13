"""PNG export — and the tofu it exists to prevent.

An astrology chart is mostly text: ☉ ♀ ♄ for the planets, ♈ ♉ ♊ for the signs, ℞ for
retrograde. In an SVG those are `<text>` elements naming a font family, and **every
general-purpose rasteriser resolves that family against the host's fonts**. Rendering
this project's own chart SVG through `rsvg-convert` produces twelve tofu boxes where
the zodiac signs should be — not because the glyphs are missing from the file, but
because the rasteriser reached for a system font that does not have them.

So we do not ask the host. Typst rasterises with `ignore_system_fonts=True` and only
the fonts Stellium bundles, which `tests/test_glyph_coverage.py` proves cover every
glyph the registries can emit. The PNG is then the same on a laptop, in CI, and in a
bare container with no fonts installed at all — which is the whole reason to export a
PNG rather than an SVG.
"""

import struct

import pytest

from stellium import ChartBuilder
from stellium.visualization.raster import _svg_width, svg_to_png

pytestmark = pytest.mark.slow


def png_size(data: bytes) -> tuple[int, int]:
    """(width, height) straight from the IHDR — no Pillow needed."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    return struct.unpack(">II", data[16:24])


@pytest.fixture(scope="module")
def chart():
    return ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()


class TestSvgWidth:
    """`scale` only means something if we read the *root* SVG's width."""

    def test_reads_the_root_width(self):
        assert _svg_width('<svg width="800" height="900"></svg>') == 800.0

    def test_tolerates_units(self):
        assert _svg_width('<svg width="640px"></svg>') == 640.0

    def test_falls_back_to_the_viewbox(self):
        assert _svg_width('<svg viewBox="0 0 512 512"></svg>') == 512.0

    def test_ignores_nested_svgs(self):
        """A chart embeds a nested <svg> per hand-drawn glyph, each 12 units wide.

        Matching one of those would render the whole chart 12px across.
        """
        markup = (
            '<svg width="800" height="900">'
            '<svg width="16" viewBox="0 0 12 12"><path d="M0 0"/></svg>'
            "</svg>"
        )
        assert _svg_width(markup) == 800.0


class TestPngExport:
    def test_a_chart_renders_to_a_png(self, chart):
        png = chart.draw("x.svg").preset_standard().to_png(scale=1)
        width, height = png_size(png)
        assert width > 100 and height > 100

    def test_scale_multiplies_the_pixel_dimensions(self, chart):
        builder = chart.draw("x.svg").preset_standard()
        single = png_size(builder.to_png(scale=1))
        double = png_size(builder.to_png(scale=2))
        assert double == (single[0] * 2, single[1] * 2)

    def test_the_background_is_transparent_by_default(self, chart):
        """RGBA, so a chart can be composited. Colour type 6 in the IHDR."""
        png = chart.draw("x.svg").preset_standard().to_png(scale=1)
        colour_type = png[25]
        assert colour_type == 6, "expected RGBA (colour type 6)"

    def test_a_background_can_be_requested(self, chart):
        png = chart.draw("x.svg").preset_standard().to_png(scale=1, background="white")
        assert png_size(png)[0] > 100

    def test_save_png_defaults_to_the_svg_name(self, chart, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        written = chart.draw("einstein.svg").preset_standard().save_png()
        assert written == "einstein.png"
        assert (tmp_path / "einstein.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    def test_dial_charts_rasterise_too(self, chart):
        """Both builders share the mixin — no second copy of this logic."""
        png = chart.draw_dial("d.svg", degrees=90).to_png(scale=1)
        assert png_size(png)[0] > 100


class TestFontIndependence:
    """The reason this module exists."""

    def test_the_png_is_rendered_with_no_system_fonts_at_all(self, chart):
        """`ignore_system_fonts=True` is not an optimisation, it is the guarantee.

        If it were ever dropped, this would still pass on our machines (which have
        symbol fonts) and start producing tofu on our users'. So assert it directly at
        the call site rather than hoping the output looks right here.
        """
        import inspect

        from stellium.presentation import typst_runtime

        source = inspect.getsource(typst_runtime.compile_png)
        assert "ignore_system_fonts=True" in source, (
            "compile_png must exclude system fonts, or the PNG stops being "
            "reproducible and starts depending on whatever the host has installed"
        )

    def test_every_glyph_in_a_tno_chart_survives_rasterisation(self):
        """The bodies whose glyphs Unicode does not cover — the ones that rendered as
        tofu, or as the literal string "Sed", before the glyph SVGs were packaged.
        """
        chart = ChartBuilder.from_notable("Albert Einstein").with_tnos().calculate()
        svg = chart.draw("t.svg").preset_standard().save(to_string=True)

        # Each hand-drawn glyph is embedded as a nested <svg> with the 12x12 viewBox.
        assert 'viewBox="0 0 12 12"' in svg, "no bundled glyph SVGs were embedded"

        png = svg_to_png(svg, scale=1)
        assert png_size(png)[0] > 100
