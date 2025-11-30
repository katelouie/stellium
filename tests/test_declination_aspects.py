"""Tests for declination aspects (Parallel and Contraparallel)."""

import pytest

from stellium import ChartBuilder
from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.aspects import DeclinationAspectEngine

# =============================================================================
# Unit Tests for DeclinationAspectEngine
# =============================================================================


class TestDeclinationAspectEngine:
    """Unit tests for the DeclinationAspectEngine."""

    def test_parallel_detection_same_hemisphere_north(self):
        """Test parallel aspect detection: both planets north, within orb."""
        engine = DeclinationAspectEngine(orb=1.0)

        # Both north, similar declination (0.3° difference)
        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.5,  # 15.5° North
        )
        moon = CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,  # Different longitude
            declination=15.8,  # 15.8° North (0.3° orb)
        )

        aspects = engine.calculate_aspects([sun, moon])

        assert len(aspects) == 1
        assert aspects[0].aspect_name == "Parallel"
        assert abs(aspects[0].orb - 0.3) < 0.01

    def test_parallel_detection_same_hemisphere_south(self):
        """Test parallel aspect detection: both planets south, within orb."""
        engine = DeclinationAspectEngine(orb=1.0)

        # Both south, similar declination
        venus = CelestialPosition(
            name="Venus",
            object_type=ObjectType.PLANET,
            longitude=60.0,
            declination=-18.5,  # 18.5° South
        )
        mars = CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=200.0,
            declination=-18.2,  # 18.2° South (0.3° orb)
        )

        aspects = engine.calculate_aspects([venus, mars])

        assert len(aspects) == 1
        assert aspects[0].aspect_name == "Parallel"
        assert abs(aspects[0].orb - 0.3) < 0.01

    def test_contraparallel_detection(self):
        """Test contraparallel detection: opposite hemispheres, same magnitude."""
        engine = DeclinationAspectEngine(orb=1.0)

        # Sun north, Saturn south, similar magnitude
        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=20.0,  # 20° North
        )
        saturn = CelestialPosition(
            name="Saturn",
            object_type=ObjectType.PLANET,
            longitude=210.0,
            declination=-20.5,  # 20.5° South (0.5° orb)
        )

        aspects = engine.calculate_aspects([sun, saturn])

        assert len(aspects) == 1
        assert aspects[0].aspect_name == "Contraparallel"
        assert abs(aspects[0].orb - 0.5) < 0.01

    def test_no_aspect_outside_orb(self):
        """Test that aspects outside orb are not detected."""
        engine = DeclinationAspectEngine(orb=1.0)

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,
        )
        moon = CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            declination=17.5,  # 2.5° difference > 1.0° orb
        )

        aspects = engine.calculate_aspects([sun, moon])
        assert len(aspects) == 0

    def test_skips_objects_without_declination(self):
        """Test that objects without declination data are skipped."""
        engine = DeclinationAspectEngine()

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,
        )
        vertex = CelestialPosition(
            name="Vertex",
            object_type=ObjectType.POINT,
            longitude=120.0,
            declination=None,  # No declination
        )

        aspects = engine.calculate_aspects([sun, vertex])
        assert len(aspects) == 0

    def test_out_of_bounds_declinations(self):
        """Test parallel/contraparallel with out-of-bounds declinations."""
        engine = DeclinationAspectEngine(orb=1.5)

        # Moon at extreme northern declination (OOB)
        moon = CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=25.5,  # Out of bounds (> 23.4367°)
        )
        mars = CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            declination=26.0,  # Also OOB, within orb
        )

        aspects = engine.calculate_aspects([moon, mars])

        assert len(aspects) == 1
        assert aspects[0].aspect_name == "Parallel"
        # Both participants are out-of-bounds
        assert moon.is_out_of_bounds
        assert mars.is_out_of_bounds

    def test_custom_object_types(self):
        """Test filtering by ObjectType."""
        engine = DeclinationAspectEngine(
            orb=1.0,
            include_types={ObjectType.PLANET},  # Exclude nodes
        )

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,
        )
        node = CelestialPosition(
            name="True Node",
            object_type=ObjectType.NODE,
            longitude=120.0,
            declination=15.2,  # Within orb but NODE type
        )

        aspects = engine.calculate_aspects([sun, node])
        assert len(aspects) == 0  # Node excluded

    def test_default_object_types_include_nodes(self):
        """Test that default ObjectTypes include nodes."""
        engine = DeclinationAspectEngine(orb=1.0)  # Default includes PLANET, NODE

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,
        )
        node = CelestialPosition(
            name="True Node",
            object_type=ObjectType.NODE,
            longitude=120.0,
            declination=15.2,  # Within orb
        )

        aspects = engine.calculate_aspects([sun, node])
        assert len(aspects) == 1  # Node included by default

    def test_configurable_orb(self):
        """Test that orb is configurable."""
        # Tight orb - should NOT find aspect
        tight_engine = DeclinationAspectEngine(orb=0.5)

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,
        )
        moon = CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=120.0,
            declination=15.8,  # 0.8° difference
        )

        aspects_tight = tight_engine.calculate_aspects([sun, moon])
        assert len(aspects_tight) == 0

        # Wider orb - should find aspect
        wide_engine = DeclinationAspectEngine(orb=1.0)
        aspects_wide = wide_engine.calculate_aspects([sun, moon])
        assert len(aspects_wide) == 1

    def test_axis_pairs_excluded(self):
        """Test that axis pairs (ASC/DSC, MC/IC, True Node/South Node) are excluded."""
        engine = DeclinationAspectEngine(orb=1.0, include_types={ObjectType.NODE})

        true_node = CelestialPosition(
            name="True Node",
            object_type=ObjectType.NODE,
            longitude=30.0,
            declination=10.0,
        )
        south_node = CelestialPosition(
            name="South Node",
            object_type=ObjectType.NODE,
            longitude=210.0,
            declination=-10.0,  # Would be contraparallel
        )

        aspects = engine.calculate_aspects([true_node, south_node])
        assert len(aspects) == 0  # Axis pair excluded

    def test_zero_declination_objects(self):
        """Test objects at exactly 0° declination (on the equator)."""
        engine = DeclinationAspectEngine(orb=1.0)

        # Both at 0° declination (equator) - should be parallel
        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=0.0,  # 0° Aries (equinox)
            declination=0.0,
        )
        mercury = CelestialPosition(
            name="Mercury",
            object_type=ObjectType.PLANET,
            longitude=5.0,
            declination=0.3,  # Close to equator
        )

        aspects = engine.calculate_aspects([sun, mercury])
        assert len(aspects) == 1
        assert aspects[0].aspect_name == "Parallel"

    def test_multiple_aspects(self):
        """Test finding multiple declination aspects."""
        engine = DeclinationAspectEngine(orb=1.0)

        sun = CelestialPosition(
            name="Sun",
            object_type=ObjectType.PLANET,
            longitude=30.0,
            declination=15.0,  # North
        )
        moon = CelestialPosition(
            name="Moon",
            object_type=ObjectType.PLANET,
            longitude=60.0,
            declination=15.3,  # Parallel with Sun
        )
        mars = CelestialPosition(
            name="Mars",
            object_type=ObjectType.PLANET,
            longitude=200.0,
            declination=-15.2,  # Contraparallel with both Sun and Moon
        )

        aspects = engine.calculate_aspects([sun, moon, mars])

        # Sun-Moon: Parallel
        # Sun-Mars: Contraparallel
        # Moon-Mars: Contraparallel
        assert len(aspects) == 3

        parallels = [a for a in aspects if a.aspect_name == "Parallel"]
        contraparallels = [a for a in aspects if a.aspect_name == "Contraparallel"]

        assert len(parallels) == 1
        assert len(contraparallels) == 2


# =============================================================================
# Integration Tests with ChartBuilder
# =============================================================================


class TestDeclinationAspectsIntegration:
    """Integration tests for declination aspects with ChartBuilder."""

    def test_chart_builder_with_declination_aspects(self):
        """Test ChartBuilder.with_declination_aspects() method."""
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects()
            .with_declination_aspects(orb=1.0)
            .calculate()
        )

        # Should have declination aspects
        assert hasattr(chart, "declination_aspects")
        assert isinstance(chart.declination_aspects, tuple)

        # Einstein's chart should have some declination aspects
        assert len(chart.declination_aspects) > 0

    def test_chart_declination_aspect_accessors(self):
        """Test chart.get_parallels() and chart.get_contraparallels() methods."""
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects()
            .with_declination_aspects(orb=1.0)
            .calculate()
        )

        all_dec_aspects = chart.get_declination_aspects()
        parallels = chart.get_parallels()
        contraparallels = chart.get_contraparallels()

        # Combined should equal total
        assert len(parallels) + len(contraparallels) == len(all_dec_aspects)

        # All parallels should be named "Parallel"
        for asp in parallels:
            assert asp.aspect_name == "Parallel"

        # All contraparallels should be named "Contraparallel"
        for asp in contraparallels:
            assert asp.aspect_name == "Contraparallel"

    def test_chart_to_dict_includes_declination_aspects(self):
        """Test that to_dict() serializes declination aspects."""
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects()
            .with_declination_aspects()
            .calculate()
        )

        data = chart.to_dict()

        assert "declination_aspects" in data
        assert isinstance(data["declination_aspects"], list)

        if data["declination_aspects"]:
            first = data["declination_aspects"][0]
            assert "object1" in first
            assert "object2" in first
            assert "aspect" in first
            assert "orb" in first

    def test_chart_without_declination_aspects(self):
        """Test that charts without with_declination_aspects() have empty tuple."""
        chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

        assert hasattr(chart, "declination_aspects")
        assert chart.declination_aspects == ()
        assert chart.get_parallels() == []
        assert chart.get_contraparallels() == []

    def test_custom_orb_via_builder(self):
        """Test custom orb configuration via builder."""
        # Tight orb
        chart_tight = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects()
            .with_declination_aspects(orb=0.5)
            .calculate()
        )

        # Wider orb
        chart_wide = (
            ChartBuilder.from_notable("Albert Einstein")
            .with_aspects()
            .with_declination_aspects(orb=1.5)
            .calculate()
        )

        # Wider orb should find more or equal aspects
        assert len(chart_wide.declination_aspects) >= len(
            chart_tight.declination_aspects
        )


# =============================================================================
# Registry Tests
# =============================================================================


class TestDeclinationAspectRegistry:
    """Test that Parallel and Contraparallel are in the aspect registry."""

    def test_parallel_in_registry(self):
        """Test that Parallel aspect is in the registry."""
        from stellium.core.registry import get_aspect_info

        info = get_aspect_info("Parallel")

        assert info is not None
        assert info.name == "Parallel"
        assert info.angle == 0.0
        assert info.category == "Declination"
        assert info.family == "Declination"
        assert info.glyph == "∥"
        assert info.default_orb == 1.0

    def test_contraparallel_in_registry(self):
        """Test that Contraparallel aspect is in the registry."""
        from stellium.core.registry import get_aspect_info

        info = get_aspect_info("Contraparallel")

        assert info is not None
        assert info.name == "Contraparallel"
        assert info.angle == 180.0
        assert info.category == "Declination"
        assert info.family == "Declination"
        assert info.glyph == "⋕"
        assert info.default_orb == 1.0
        assert "Contra-parallel" in info.aliases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
