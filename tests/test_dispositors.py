"""Tests for dispositor graph calculations."""

import pytest

from stellium import ChartBuilder
from stellium.engines.dispositors import (
    DispositorEngine,
    DispositorResult,
    render_both_dispositors,
    render_dispositor_graph,
)


@pytest.fixture(scope="module")
def einstein_chart():
    """Albert Einstein's natal chart for testing."""
    return ChartBuilder.from_notable("Albert Einstein").calculate()


@pytest.fixture(scope="module")
def second_chart():
    """A second notable chart for additional testing."""
    return ChartBuilder.from_notable("Nikola Tesla").calculate()


# =============================================================================
# Planetary Dispositor Tests
# =============================================================================


class TestPlanetaryDispositors:
    """Test planetary dispositor calculations."""

    def test_planetary_result_type(self, einstein_chart):
        """Planetary dispositors should return DispositorResult."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        assert isinstance(result, DispositorResult)
        assert result.mode == "planetary"

    def test_all_traditional_planets_included(self, einstein_chart):
        """All 7 traditional planets should have edges."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        sources = {e.source for e in result.edges}
        expected = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}

        assert sources == expected

    def test_edges_have_correct_structure(self, einstein_chart):
        """Each edge should have source, target, sign, and ruler."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        for edge in result.edges:
            assert edge.source is not None
            assert edge.target is not None
            assert edge.source_sign is not None
            assert edge.ruler is not None
            # Target should equal ruler for planetary mode
            assert edge.target == edge.ruler

    def test_chains_exist_for_all_planets(self, einstein_chart):
        """Every planet should have a chain."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        expected_planets = {
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
        }
        assert set(result.chains.keys()) == expected_planets

    def test_chains_terminate_at_loop_or_self(self, einstein_chart):
        """Chains should end at self-loop or cycle."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        for _start, chain in result.chains.items():
            assert len(chain) >= 1
            # Last two elements should be same (self-loop) or
            # last element should appear earlier (cycle)
            if len(chain) >= 2:
                if chain[-1] == chain[-2]:
                    pass  # Self-loop
                else:
                    # Should be a cycle
                    assert chain[-1] in chain[:-1]

    def test_mutual_reception_detection(self, einstein_chart):
        """Should detect Mars-Saturn mutual reception in Einstein's chart."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        # Einstein has Mars-Saturn mutual reception
        assert len(result.mutual_receptions) >= 1

        mr_pairs = [(mr.node1, mr.node2) for mr in result.mutual_receptions]
        # Mars and Saturn should be in mutual reception
        assert ("Mars", "Saturn") in mr_pairs or ("Saturn", "Mars") in mr_pairs

    def test_final_dispositor_with_mutual_reception(self, einstein_chart):
        """Final dispositor should be mutual reception pair when no self-disposing planet."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        # Einstein's chart has Mars-Saturn mutual reception as the sink
        assert result.final_dispositor is not None
        if isinstance(result.final_dispositor, tuple):
            assert "Mars" in result.final_dispositor
            assert "Saturn" in result.final_dispositor


class TestPlanetaryRulershipSystems:
    """Test traditional vs modern rulership."""

    def test_traditional_rulership(self, einstein_chart):
        """Traditional rulership should use classical rulers."""
        engine = DispositorEngine(einstein_chart, rulership_system="traditional")
        result = engine.planetary()

        assert result.rulership_system == "traditional"

    def test_modern_rulership(self, einstein_chart):
        """Modern rulership should be selectable."""
        engine = DispositorEngine(einstein_chart, rulership_system="modern")
        result = engine.planetary()

        assert result.rulership_system == "modern"


# =============================================================================
# House-Based Dispositor Tests
# =============================================================================


class TestHouseBasedDispositors:
    """Test house-based dispositor calculations (Kate's innovation)."""

    def test_house_result_type(self, einstein_chart):
        """House dispositors should return DispositorResult."""
        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        assert isinstance(result, DispositorResult)
        assert result.mode == "house"

    def test_all_houses_included(self, einstein_chart):
        """All 12 houses should have edges."""
        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        sources = {e.source for e in result.edges}
        expected = {str(i) for i in range(1, 13)}

        assert sources == expected

    def test_house_edges_have_rulers(self, einstein_chart):
        """Each house edge should include the ruling planet."""
        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        for edge in result.edges:
            assert edge.ruler is not None
            # Target should be a house number (string)
            assert edge.target in {str(i) for i in range(1, 13)}

    def test_house_chains_exist(self, einstein_chart):
        """Every house should have a chain."""
        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        expected_houses = {str(i) for i in range(1, 13)}
        assert set(result.chains.keys()) == expected_houses

    def test_house_mutual_reception_includes_rulers(self, einstein_chart):
        """House mutual receptions should include planet info."""
        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        for mr in result.mutual_receptions:
            assert mr.planet1 is not None
            assert mr.planet2 is not None


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_different_house_systems(self):
        """Should work with different house systems."""
        from stellium.engines.houses import PlacidusHouses, WholeSignHouses

        # Create chart with multiple house systems
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .calculate()
        )

        engine_placidus = DispositorEngine(chart, house_system="Placidus")
        engine_whole = DispositorEngine(chart, house_system="Whole Sign")

        result_p = engine_placidus.house_based()
        result_w = engine_whole.house_based()

        # Both should have valid results
        assert len(result_p.edges) == 12
        assert len(result_w.edges) == 12

    def test_serialization_to_dict(self, einstein_chart):
        """Results should be serializable to dict."""
        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        data = result.to_dict()

        assert "mode" in data
        assert "edges" in data
        assert "final_dispositor" in data
        assert "mutual_receptions" in data
        assert "chains" in data


# =============================================================================
# Graphviz Rendering Tests
# =============================================================================


class TestGraphvizRendering:
    """Test graphviz rendering functions."""

    def test_render_planetary_graph(self, einstein_chart):
        """Should render planetary dispositor graph."""
        pytest.importorskip("graphviz")

        engine = DispositorEngine(einstein_chart)
        result = engine.planetary()

        graph = render_dispositor_graph(result, use_glyphs=True)

        # Should have a graphviz.Digraph
        assert graph is not None
        assert hasattr(graph, "render")

    def test_render_house_graph(self, einstein_chart):
        """Should render house dispositor graph."""
        pytest.importorskip("graphviz")

        engine = DispositorEngine(einstein_chart)
        result = engine.house_based()

        graph = render_dispositor_graph(result, use_glyphs=False)

        assert graph is not None

    def test_render_both_dispositors(self, einstein_chart):
        """Should render both graphs as subgraphs."""
        pytest.importorskip("graphviz")

        engine = DispositorEngine(einstein_chart)
        planetary = engine.planetary()
        house = engine.house_based()

        graph = render_both_dispositors(planetary, house)

        assert graph is not None
        # Should contain subgraph clusters
        source = graph.source
        assert "cluster_planetary" in source
        assert "cluster_house" in source

    def test_graphviz_import_error(self, einstein_chart):
        """Should raise ImportError with helpful message if graphviz not installed."""
        # This test would require mocking the import, skip for now
        pass


# =============================================================================
# Report Integration Tests
# =============================================================================


class TestReportIntegration:
    """Test integration with ReportBuilder."""

    def test_report_with_dispositors(self, einstein_chart):
        """Should integrate with ReportBuilder."""
        from stellium import ReportBuilder

        report = (
            ReportBuilder().from_chart(einstein_chart).with_dispositors(mode="both")
        )

        # Generate section data
        section_data = [
            (s.section_name, s.generate_data(einstein_chart)) for s in report._sections
        ]

        assert len(section_data) == 1
        name, data = section_data[0]
        assert name == "Dispositors"
        assert data["type"] == "compound"

    def test_report_planetary_only(self, einstein_chart):
        """Should work with planetary mode only."""
        from stellium.presentation.sections import DispositorSection

        section = DispositorSection(mode="planetary")
        data = section.generate_data(einstein_chart)

        # Single mode returns text type
        assert data["type"] == "text"

    def test_report_house_only(self, einstein_chart):
        """Should work with house mode only."""
        from stellium.presentation.sections import DispositorSection

        section = DispositorSection(mode="house")
        data = section.generate_data(einstein_chart)

        assert data["type"] == "text"

    def test_report_with_different_rulership(self, einstein_chart):
        """Should accept rulership parameter."""
        from stellium.presentation.sections import DispositorSection

        section = DispositorSection(mode="planetary", rulership="modern")
        data = section.generate_data(einstein_chart)

        assert data["type"] == "text"


# =============================================================================
# Specific Chart Tests
# =============================================================================


class TestSpecificCharts:
    """Test with specific notable charts."""

    def test_second_chart_dispositors(self, second_chart):
        """Test a second chart has valid dispositor structure."""
        engine = DispositorEngine(second_chart)

        planetary = engine.planetary()
        house = engine.house_based()

        # Both should have valid structure
        assert len(planetary.edges) == 7
        assert len(house.edges) == 12

    def test_final_dispositor_or_mutual_reception(self, second_chart):
        """Every chart should have either final dispositor or mutual receptions."""
        engine = DispositorEngine(second_chart)
        result = engine.planetary()

        # Should have either a final dispositor or mutual receptions
        has_final = result.final_dispositor is not None
        has_mutual = len(result.mutual_receptions) > 0

        # At least one should be true
        assert has_final or has_mutual


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
