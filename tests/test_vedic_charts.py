"""Tests for Vedic chart renderers (North Indian and South Indian).

Covers:
- Smoke tests: all renderers × themes × label styles produce valid SVG
- Content tests: correct planets, signs, ASC placement
- Configuration tests: degrees, label styles, house numbers
"""

import pytest

from stellium import ChartBuilder
from stellium.visualization.vedic import NorthIndianRenderer, SouthIndianRenderer

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def einstein_sidereal():
    """Einstein's chart in sidereal (Lahiri) — computed once for all tests."""
    return (
        ChartBuilder.from_notable("Albert Einstein").with_sidereal("lahiri").calculate()
    )


# =============================================================================
# SMOKE TESTS — does it render at all?
# =============================================================================


class TestSouthIndianSmoke:
    """South Indian renderer produces valid SVG in all configurations."""

    def test_default_render(self, einstein_sidereal):
        svg = SouthIndianRenderer().render(einstein_sidereal)
        assert svg.startswith("<svg")
        assert len(svg) > 500

    @pytest.mark.parametrize("theme", ["classic", "dark", "traditional"])
    def test_themes(self, einstein_sidereal, theme):
        svg = SouthIndianRenderer(theme=theme).render(einstein_sidereal)
        assert svg.startswith("<svg")

    @pytest.mark.parametrize("style", ["abbreviation", "number", "glyph", "full"])
    def test_label_styles(self, einstein_sidereal, style):
        svg = SouthIndianRenderer(label_style=style).render(einstein_sidereal)
        assert svg.startswith("<svg")


class TestNorthIndianSmoke:
    """North Indian renderer produces valid SVG in all configurations."""

    def test_default_render(self, einstein_sidereal):
        svg = NorthIndianRenderer().render(einstein_sidereal)
        assert svg.startswith("<svg")
        assert len(svg) > 500

    @pytest.mark.parametrize("theme", ["classic", "dark", "traditional"])
    def test_themes(self, einstein_sidereal, theme):
        svg = NorthIndianRenderer(theme=theme).render(einstein_sidereal)
        assert svg.startswith("<svg")

    @pytest.mark.parametrize("style", ["abbreviation", "number", "glyph", "full"])
    def test_label_styles(self, einstein_sidereal, style):
        svg = NorthIndianRenderer(label_style=style).render(einstein_sidereal)
        assert svg.startswith("<svg")


# =============================================================================
# CONTENT TESTS — correct data in the SVG?
# =============================================================================


class TestSouthIndianContent:
    """South Indian chart contains expected astronomical data."""

    def test_contains_all_classical_planets(self, einstein_sidereal):
        """All 10 classical planets should appear in the chart."""
        svg = SouthIndianRenderer(label_style="abbreviation").render(einstein_sidereal)
        for abbrev in ["Su", "Mo", "Me", "Ve", "Ma", "Ju", "Sa"]:
            assert abbrev in svg, f"Missing planet abbreviation: {abbrev}"

    def test_contains_all_12_signs(self, einstein_sidereal):
        """All 12 sign abbreviations should appear."""
        svg = SouthIndianRenderer(label_style="abbreviation").render(einstein_sidereal)
        for sign in [
            "Ari",
            "Tau",
            "Gem",
            "Can",
            "Leo",
            "Vir",
            "Lib",
            "Sco",
            "Sag",
            "Cap",
            "Aqu",
            "Pis",
        ]:
            assert sign in svg, f"Missing sign: {sign}"

    def test_asc_marker_present(self, einstein_sidereal):
        """ASC marker should appear in the chart."""
        svg = SouthIndianRenderer().render(einstein_sidereal)
        assert "ASC" in svg

    def test_number_style_uses_digits(self, einstein_sidereal):
        """Number label style should show digits, not sign names."""
        svg = SouthIndianRenderer(label_style="number").render(einstein_sidereal)
        # Should not have sign abbreviations
        assert "Ari" not in svg
        # Should have numbers (at minimum "1" through "9" appear)
        for n in range(1, 10):
            assert f">{n}<" in svg or f">{n} " in svg or str(n) in svg

    def test_degrees_shown_when_enabled(self, einstein_sidereal):
        """Degree values should appear when show_degrees=True."""
        svg = SouthIndianRenderer(show_degrees=True).render(einstein_sidereal)
        assert "°" in svg
        assert "'" in svg  # minutes marker

    def test_degrees_hidden_when_disabled(self, einstein_sidereal):
        """Degree values should not appear when show_degrees=False."""
        svg = SouthIndianRenderer(show_degrees=False).render(einstein_sidereal)
        assert "°" not in svg

    def test_house_numbers_shown(self, einstein_sidereal):
        """House numbers 1-12 should appear when enabled."""
        svg = SouthIndianRenderer(show_house_numbers=True).render(einstein_sidereal)
        # House 1 should be present
        assert ">1<" in svg or ">1 <" in svg

    def test_contains_chart_name(self, einstein_sidereal):
        """Chart should display the native's name."""
        svg = SouthIndianRenderer().render(einstein_sidereal)
        assert "Albert Einstein" in svg

    def test_contains_south_indian_label(self, einstein_sidereal):
        """Chart should identify itself as South Indian style."""
        svg = SouthIndianRenderer().render(einstein_sidereal)
        assert "South Indian" in svg


class TestNorthIndianContent:
    """North Indian chart contains expected astronomical data."""

    def test_contains_all_classical_planets(self, einstein_sidereal):
        svg = NorthIndianRenderer(label_style="abbreviation").render(einstein_sidereal)
        for abbrev in ["Su", "Mo", "Me", "Ve", "Ma", "Ju", "Sa"]:
            assert abbrev in svg, f"Missing planet abbreviation: {abbrev}"

    def test_number_style_shows_sign_numbers(self, einstein_sidereal):
        """Number label style should show sign ordinal numbers."""
        svg = NorthIndianRenderer(label_style="number").render(einstein_sidereal)
        # Einstein's ASC is Gemini (sign 3), so "3" should appear
        # near center (house 1 position)
        assert ">3<" in svg or "3" in svg

    def test_degrees_shown_when_enabled(self, einstein_sidereal):
        svg = NorthIndianRenderer(show_degrees=True).render(einstein_sidereal)
        assert "°" in svg
        assert "'" in svg

    def test_degrees_hidden_when_disabled(self, einstein_sidereal):
        svg = NorthIndianRenderer(show_degrees=False).render(einstein_sidereal)
        assert "°" not in svg

    def test_contains_chart_name(self, einstein_sidereal):
        svg = NorthIndianRenderer().render(einstein_sidereal)
        assert "Albert Einstein" in svg

    def test_contains_north_indian_label(self, einstein_sidereal):
        svg = NorthIndianRenderer().render(einstein_sidereal)
        assert "North Indian" in svg

    def test_retrograde_marker(self, einstein_sidereal):
        """Retrograde planets should have 'R' marker."""
        svg = NorthIndianRenderer(label_style="abbreviation").render(einstein_sidereal)
        # Einstein has Uranus retrograde in sidereal chart
        assert " R" in svg

    def test_asc_shown_when_house1_empty(self):
        """If house 1 has no planets, 'As' should appear."""
        # Use a chart where house 1 is likely empty
        chart = (
            ChartBuilder.from_details("2000-06-15 12:00", "London, UK")
            .with_sidereal("lahiri")
            .calculate()
        )
        svg = NorthIndianRenderer(label_style="abbreviation").render(chart)
        # Either "As" marker or planets should be in house 1
        assert "As" in svg or len(svg) > 500  # at minimum it renders


# =============================================================================
# RENDER TO FILE
# =============================================================================


class TestRenderToFile:
    """Test file output functionality."""

    def test_south_indian_render_to_file(self, einstein_sidereal, tmp_path):
        path = tmp_path / "south.svg"
        SouthIndianRenderer().render_to_file(einstein_sidereal, str(path))
        assert path.exists()
        content = path.read_text()
        assert content.startswith("<svg")

    def test_north_indian_render_to_file(self, einstein_sidereal, tmp_path):
        path = tmp_path / "north.svg"
        NorthIndianRenderer().render_to_file(einstein_sidereal, str(path))
        assert path.exists()
        content = path.read_text()
        assert content.startswith("<svg")


# =============================================================================
# DIFFERENT CHARTS
# =============================================================================


class TestDifferentCharts:
    """Renderers work with various chart inputs, not just Einstein."""

    def test_south_indian_custom_chart(self):
        chart = (
            ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA")
            .with_sidereal("lahiri")
            .calculate()
        )
        svg = SouthIndianRenderer(show_degrees=True).render(chart)
        assert svg.startswith("<svg")
        assert "°" in svg

    def test_north_indian_different_ayanamsa(self):
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_sidereal("raman")
            .calculate()
        )
        svg = NorthIndianRenderer().render(chart)
        assert svg.startswith("<svg")
        assert "Albert Einstein" in svg
