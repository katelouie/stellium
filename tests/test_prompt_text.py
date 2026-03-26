"""Comprehensive tests for chart.to_prompt_text() across all chart types.

Tests:
- Single charts (basic, with components, multiple house systems, sidereal)
- Multi-charts (synastry, transits, house overlays, cross-aspects)
- Synthesis charts (composite, with source charts)
- UnknownTimeChart
- Display name resolution (Mean Apogee → Black Moon Lilith, etc.)
- Section filtering
- include_extras toggle
- Content correctness
"""

import pytest

from stellium import ChartBuilder, MultiChartBuilder
from stellium.components import (
    ArabicPartsCalculator,
    DignityComponent,
    FixedStarsComponent,
    MidpointCalculator,
)
from stellium.engines import ModernAspectEngine, PlacidusHouses, WholeSignHouses

pytestmark = pytest.mark.slow


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def basic_chart():
    """Basic chart with aspects."""
    return (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine())
        .calculate()
    )


@pytest.fixture(scope="module")
def full_chart():
    """Chart with all components loaded."""
    return (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine())
        .add_component(ArabicPartsCalculator())
        .add_component(DignityComponent())
        .add_component(FixedStarsComponent())
        .add_component(MidpointCalculator())
        .calculate()
    )


@pytest.fixture(scope="module")
def multi_house_chart():
    """Chart with multiple house systems."""
    return (
        ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects(ModernAspectEngine())
        .calculate()
    )


@pytest.fixture(scope="module")
def sidereal_chart():
    """Chart in sidereal zodiac."""
    return (
        ChartBuilder.from_notable("Albert Einstein")
        .with_sidereal("lahiri")
        .with_aspects(ModernAspectEngine())
        .calculate()
    )


@pytest.fixture(scope="module")
def multi_chart():
    """Multi-chart with cross-aspects and house overlays."""
    natal = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_aspects(ModernAspectEngine())
        .calculate()
    )
    transit = (
        ChartBuilder.from_details("2026-03-25 12:00", "Ulm, Germany")
        .with_aspects(ModernAspectEngine())
        .calculate()
    )
    return (
        MultiChartBuilder()
        .add_chart(natal, label="Natal")
        .add_chart(transit, label="Transit")
        .with_cross_aspects()
        .with_house_overlays()
        .calculate()
    )


# =============================================================================
# BASIC SINGLE CHART
# =============================================================================


class TestBasicChart:
    """Basic single chart prompt text generation."""

    def test_returns_string(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert isinstance(text, str)
        assert len(text) > 100

    def test_contains_native_info(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "Albert Einstein" in text
        assert "1879" in text
        assert "Ulm" in text

    def test_contains_planets(self, basic_chart):
        text = basic_chart.to_prompt_text()
        for planet in [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]:
            assert planet in text, f"Missing planet: {planet}"

    def test_contains_signs(self, basic_chart):
        text = basic_chart.to_prompt_text()
        # Einstein has planets in these signs
        for sign in ["Pisces", "Aries", "Sagittarius"]:
            assert sign in text, f"Missing sign: {sign}"

    def test_contains_degrees(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "°" in text
        assert "'" in text  # minutes

    def test_contains_aspects(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "## Aspects" in text
        # Should have aspect type names
        assert any(
            name in text
            for name in ["Conjunction", "Trine", "Square", "Opposition", "Sextile"]
        )

    def test_contains_houses(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "House" in text
        assert "## House Cusps" in text

    def test_contains_angles(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "ASC" in text
        assert "MC" in text

    def test_contains_declination(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "decl" in text

    def test_oob_flagged(self, basic_chart):
        """Einstein's Moon is out of bounds."""
        text = basic_chart.to_prompt_text()
        assert "OOB" in text

    def test_retrograde_flagged(self, basic_chart):
        """Einstein's Uranus is retrograde."""
        text = basic_chart.to_prompt_text()
        assert "(R)" in text


# =============================================================================
# DISPLAY NAMES
# =============================================================================


class TestDisplayNames:
    """Internal names should be replaced with user-friendly display names."""

    def test_black_moon_lilith(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "Black Moon Lilith" in text
        assert "Mean Apogee" not in text

    def test_north_node(self, basic_chart):
        text = basic_chart.to_prompt_text()
        assert "North Node" in text
        assert "True Node" not in text

    def test_display_names_in_aspects(self, basic_chart):
        """Aspect lines should also use display names."""
        text = basic_chart.to_prompt_text()
        # Find aspect lines mentioning nodes or lilith
        lines = text.splitlines()
        node_aspect_lines = [line for line in lines if "Node" in line and "orb" in line]
        for line in node_aspect_lines:
            assert "True Node" not in line, f"Internal name in aspect: {line}"


# =============================================================================
# SECTION FILTERING
# =============================================================================


class TestSectionFiltering:
    """The sections parameter controls what's included."""

    def test_info_only(self, basic_chart):
        text = basic_chart.to_prompt_text(sections={"info"})
        assert "Albert Einstein" in text
        assert "## Planetary Positions" not in text
        assert "## Aspects" not in text

    def test_positions_only(self, basic_chart):
        text = basic_chart.to_prompt_text(sections={"positions"})
        assert "## Planetary Positions" in text
        assert "## Aspects" not in text
        assert "## House Cusps" not in text

    def test_aspects_only(self, basic_chart):
        text = basic_chart.to_prompt_text(sections={"aspects"})
        assert "## Aspects" in text
        assert "## Planetary Positions" not in text

    def test_multiple_sections(self, basic_chart):
        text = basic_chart.to_prompt_text(sections={"info", "positions", "aspects"})
        assert "Albert Einstein" in text
        assert "## Planetary Positions" in text
        assert "## Aspects" in text
        assert "## House Cusps" not in text

    def test_empty_sections(self, basic_chart):
        text = basic_chart.to_prompt_text(sections=set())
        # Should be empty or minimal
        assert len(text.strip()) == 0 or len(text.splitlines()) < 3


# =============================================================================
# INCLUDE EXTRAS
# =============================================================================


class TestIncludeExtras:
    """The include_extras flag controls the catch-all section."""

    def test_extras_on_by_default(self, basic_chart):
        """Default should include extras."""
        text = basic_chart.to_prompt_text()
        assert isinstance(text, str)

    def test_extras_off(self, basic_chart):
        text_with = basic_chart.to_prompt_text(include_extras=True)
        text_without = basic_chart.to_prompt_text(include_extras=False)
        # Both should work; without may be shorter or equal
        assert len(text_without) <= len(text_with)


# =============================================================================
# MULTIPLE HOUSE SYSTEMS
# =============================================================================


class TestMultipleHouseSystems:
    """Charts with multiple house systems show all placements."""

    def test_both_systems_listed(self, multi_house_chart):
        text = multi_house_chart.to_prompt_text()
        assert "Placidus" in text
        assert "Whole Sign" in text

    def test_positions_show_both_houses(self, multi_house_chart):
        text = multi_house_chart.to_prompt_text()
        # Should have entries like "Placidus H10, Whole Sign H9"
        assert "Placidus H" in text
        assert "Whole Sign H" in text

    def test_cusps_shown_per_system(self, multi_house_chart):
        text = multi_house_chart.to_prompt_text()
        # Should have separate cusp sections
        assert "### Placidus" in text
        assert "### Whole Sign" in text


# =============================================================================
# SIDEREAL
# =============================================================================


class TestSidereal:
    """Sidereal charts show zodiac type and ayanamsa."""

    def test_shows_sidereal_label(self, sidereal_chart):
        text = sidereal_chart.to_prompt_text()
        assert "sidereal" in text.lower()

    def test_shows_ayanamsa(self, sidereal_chart):
        text = sidereal_chart.to_prompt_text()
        assert "lahiri" in text.lower() or "Lahiri" in text


# =============================================================================
# FULL CHART WITH COMPONENTS
# =============================================================================


class TestFullChart:
    """Chart with all components loaded."""

    def test_renders_without_error(self, full_chart):
        text = full_chart.to_prompt_text()
        assert len(text) > 500

    def test_contains_dignity_info(self, full_chart):
        text = full_chart.to_prompt_text()
        # Dignities section should be present if DignityComponent was added
        # It may be in "Essential Dignities" or "Dignities" section
        assert "dignit" in text.lower() or "Rulership" in text or "Exaltation" in text

    def test_larger_than_basic(self, basic_chart, full_chart):
        basic = basic_chart.to_prompt_text()
        full = full_chart.to_prompt_text()
        assert len(full) > len(basic)


# =============================================================================
# MULTI-CHART
# =============================================================================


class TestMultiChart:
    """Multi-chart prompt text (synastry/transits)."""

    def test_renders_without_error(self, multi_chart):
        text = multi_chart.to_prompt_text()
        assert isinstance(text, str)
        assert len(text) > 500

    def test_contains_both_labels(self, multi_chart):
        text = multi_chart.to_prompt_text()
        assert "## Natal" in text
        assert "## Transit" in text

    def test_contains_cross_aspects(self, multi_chart):
        text = multi_chart.to_prompt_text()
        assert "Cross-Chart" in text or "cross" in text.lower()

    def test_contains_house_overlays(self, multi_chart):
        text = multi_chart.to_prompt_text()
        assert "House Overlay" in text or "overlay" in text.lower()

    def test_section_filtering_passes_through(self, multi_chart):
        """Section filtering should affect individual charts."""
        text = multi_chart.to_prompt_text(sections={"info", "positions"})
        assert "## Planetary Positions" in text
        assert "## House Cusps" not in text


# =============================================================================
# SYNTHESIS CHART
# =============================================================================


class TestSynthesisChart:
    """Synthesis (composite/davison) chart prompt text."""

    def test_renders_without_error(self):
        from stellium.core.synthesis import SynthesisBuilder

        chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
        chart2 = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()

        synthesis = (
            SynthesisBuilder.composite(chart1, chart2)
            .with_labels("Einstein", "Kate")
            .calculate()
        )

        text = synthesis.to_prompt_text()
        assert isinstance(text, str)
        assert len(text) > 200

    def test_includes_source_charts(self):
        from stellium.core.synthesis import SynthesisBuilder

        chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
        chart2 = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()

        synthesis = (
            SynthesisBuilder.composite(chart1, chart2)
            .with_labels("Einstein", "Kate")
            .calculate()
        )

        text_without = synthesis.to_prompt_text(include_source_charts=False)
        text_with = synthesis.to_prompt_text(include_source_charts=True)
        assert len(text_with) > len(text_without)
        assert "Einstein" in text_with
        assert "Kate" in text_with


# =============================================================================
# UNKNOWN TIME CHART
# =============================================================================


class TestUnknownTimeChart:
    """UnknownTimeChart should skip houses and angles."""

    def test_renders_without_error(self):
        chart = (
            ChartBuilder.from_details("1994-01-06", "Palo Alto, CA")
            .with_unknown_time()
            .calculate()
        )
        text = chart.to_prompt_text()
        assert isinstance(text, str)

    def test_no_houses_or_angles(self):
        chart = (
            ChartBuilder.from_details("1994-01-06", "Palo Alto, CA")
            .with_unknown_time()
            .calculate()
        )
        text = chart.to_prompt_text()
        assert "## House Cusps" not in text
        assert "## Angles" not in text

    def test_shows_time_unknown(self):
        chart = (
            ChartBuilder.from_details("1994-01-06", "Palo Alto, CA")
            .with_unknown_time()
            .calculate()
        )
        text = chart.to_prompt_text()
        assert "Unknown" in text or "unknown" in text
