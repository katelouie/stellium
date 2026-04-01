"""Tests for CalculatedChart.get_component_result() and available_components()."""

import pytest

from stellium import ChartBuilder
from stellium.components import (
    AntisciaCalculator,
    ArabicPartsCalculator,
    FixedStarsComponent,
    MidpointCalculator,
)
from stellium.components.dignity import AccidentalDignityComponent, DignityComponent
from stellium.core.models import CalculatedChart, CelestialPosition, ObjectType
from stellium.engines import ZodiacalReleasingAnalyzer
from stellium.engines.patterns import AspectPatternAnalyzer

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def full_chart() -> CalculatedChart:
    """Chart with all component types for comprehensive testing."""
    return (
        ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
        .add_component(ArabicPartsCalculator())
        .add_component(MidpointCalculator())
        .add_component(FixedStarsComponent())
        .add_component(DignityComponent())
        .add_component(AccidentalDignityComponent())
        .add_component(AntisciaCalculator())
        .add_analyzer(AspectPatternAnalyzer())
        .with_aspects()
        .calculate()
    )


@pytest.fixture(scope="module")
def zr_chart() -> CalculatedChart:
    """Chart with ZodiacalReleasingAnalyzer (requires Arabic Parts)."""
    return (
        ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
        .add_component(ArabicPartsCalculator())
        .add_analyzer(ZodiacalReleasingAnalyzer(lots=["Part of Fortune"]))
        .with_aspects()
        .calculate()
    )


@pytest.fixture(scope="module")
def bare_chart() -> CalculatedChart:
    """Chart with no components or analyzers."""
    return ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA").calculate()


# ─── Position-based components ───────────────────────────────────────────


class TestPositionBased:
    def test_arabic_parts(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Arabic Parts")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(p, CelestialPosition) for p in result)
        assert all(p.object_type == ObjectType.ARABIC_PART for p in result)

    def test_midpoints(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Midpoints")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(p, CelestialPosition) for p in result)
        assert all(p.object_type == ObjectType.MIDPOINT for p in result)

    def test_fixed_stars(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Fixed Stars")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(p, CelestialPosition) for p in result)
        assert all(p.object_type == ObjectType.FIXED_STAR for p in result)


# ─── Metadata-based components ───────────────────────────────────────────


class TestMetadataBased:
    def test_dignity_component(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Essential Dignities")
        assert isinstance(result, dict)
        assert "planet_dignities" in result

    def test_accidental_dignity_component(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Accidental Dignities")
        assert isinstance(result, dict)


# ─── Dual-storage components ─────────────────────────────────────────────


class TestDualStorage:
    def test_antiscia(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Antiscia")
        assert isinstance(result, dict)
        assert "positions" in result
        assert "metadata" in result
        assert isinstance(result["positions"], list)
        assert all(isinstance(p, CelestialPosition) for p in result["positions"])
        assert all(
            p.object_type in (ObjectType.ANTISCION, ObjectType.CONTRA_ANTISCION)
            for p in result["positions"]
        )


# ─── Analyzers ───────────────────────────────────────────────────────────


class TestAnalyzers:
    def test_aspect_pattern_analyzer(self, full_chart: CalculatedChart):
        result = full_chart.get_component_result("Aspect Patterns")
        assert isinstance(result, list)

    def test_zodiacal_releasing_analyzer(self, zr_chart: CalculatedChart):
        result = zr_chart.get_component_result("ZodiacalReleasing")
        assert isinstance(result, dict)


# ─── Alias lookup ────────────────────────────────────────────────────────


class TestAliasLookup:
    def test_metadata_key_alias(self, full_chart: CalculatedChart):
        """Lookup by metadata key ('dignities') works same as component name."""
        by_name = full_chart.get_component_result("Essential Dignities")
        by_alias = full_chart.get_component_result("dignities")
        assert by_name is by_alias

    def test_accidental_alias(self, full_chart: CalculatedChart):
        by_name = full_chart.get_component_result("Accidental Dignities")
        by_alias = full_chart.get_component_result("accidental_dignities")
        assert by_name is by_alias

    def test_antiscia_alias(self, full_chart: CalculatedChart):
        by_name = full_chart.get_component_result("Antiscia")
        by_alias = full_chart.get_component_result("antiscia")
        # Dual-storage returns a new dict each time, so check content equality
        assert by_name["metadata"] is by_alias["metadata"]


# ─── Discovery ───────────────────────────────────────────────────────────


class TestDiscovery:
    def test_available_components(self, full_chart: CalculatedChart):
        available = full_chart.available_components()
        assert isinstance(available, list)
        assert available == sorted(available), "Should be sorted"
        assert "Arabic Parts" in available
        assert "Midpoints" in available
        assert "Fixed Stars" in available
        assert "Essential Dignities" in available
        assert "Accidental Dignities" in available
        assert "Antiscia" in available
        assert "Aspect Patterns" in available

    def test_available_components_includes_zr(self, zr_chart: CalculatedChart):
        available = zr_chart.available_components()
        assert "ZodiacalReleasing" in available
        assert "Arabic Parts" in available

    def test_available_components_empty(self, bare_chart: CalculatedChart):
        assert bare_chart.available_components() == []


# ─── Error handling ──────────────────────────────────────────────────────


class TestErrorHandling:
    def test_unknown_name_raises_key_error(self, full_chart: CalculatedChart):
        with pytest.raises(KeyError, match="No component or analyzer named"):
            full_chart.get_component_result("Nonexistent")

    def test_error_lists_available_names(self, full_chart: CalculatedChart):
        with pytest.raises(KeyError, match="Arabic Parts"):
            full_chart.get_component_result("Nonexistent")

    def test_bare_chart_raises_clear_error(self, bare_chart: CalculatedChart):
        with pytest.raises(KeyError, match="Available: none"):
            bare_chart.get_component_result("Arabic Parts")

    def test_bare_chart_error_suggests_api(self, bare_chart: CalculatedChart):
        with pytest.raises(KeyError, match="add_component"):
            bare_chart.get_component_result("Arabic Parts")


# ─── User-reported scenario ──────────────────────────────────────────────


class TestUserScenario:
    def test_github_issue_scenario(self):
        """Exact code from the GitHub issue should work without error."""
        chart = (
            ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
            .add_component(ArabicPartsCalculator())
            .add_component(MidpointCalculator())
            .calculate()
        )
        arabic_parts = chart.get_component_result("Arabic Parts")
        assert len(arabic_parts) > 0
        midpoints = chart.get_component_result("Midpoints")
        assert len(midpoints) > 0
        assert chart.available_components() == ["Arabic Parts", "Midpoints"]


# ─── Inheritance ─────────────────────────────────────────────────────────


class TestInheritance:
    def test_synthesis_chart_has_method(self):
        """SynthesisChart inherits get_component_result via CalculatedChart."""
        from stellium.core.synthesis import SynthesisChart

        assert hasattr(SynthesisChart, "get_component_result")
        assert hasattr(SynthesisChart, "available_components")
