"""Tests for MoietyOrbEngine — traditional moiety-based orb calculation."""

import pytest

from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.orbs import (
    LILLY_FULL_ORBS,
    PTOLEMY_FULL_ORBS,
    MoietyOrbEngine,
)


def _make_pos(name: str) -> CelestialPosition:
    """Create a minimal CelestialPosition for testing."""
    return CelestialPosition(
        name=name,
        object_type=ObjectType.PLANET,
        longitude=0.0,
        latitude=0.0,
        distance=1.0,
        speed_longitude=0.0,
        speed_latitude=0.0,
        speed_distance=0.0,
    )


# Fixtures
SUN = _make_pos("Sun")
MOON = _make_pos("Moon")
MARS = _make_pos("Mars")
SATURN = _make_pos("Saturn")
JUPITER = _make_pos("Jupiter")
VENUS = _make_pos("Venus")
MERCURY = _make_pos("Mercury")
PLUTO = _make_pos("Pluto")
CHIRON = _make_pos("Chiron")


class TestMoietyFormula:
    """Core moiety calculation: effective_orb = (full_A + full_B) / 2."""

    def test_sun_moon(self):
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        assert orb == (15.0 + 12.0) / 2  # 13.5

    def test_sun_saturn(self):
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(SUN, SATURN, "Square")
        assert orb == (15.0 + 9.0) / 2  # 12.0

    def test_mars_venus(self):
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(MARS, VENUS, "Trine")
        assert orb == (8.0 + 7.0) / 2  # 7.5

    def test_mercury_mercury(self):
        """Same planet (e.g., progressed Mercury to natal Mercury)."""
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(MERCURY, MERCURY, "Conjunction")
        assert orb == 7.0  # (7 + 7) / 2

    def test_symmetric(self):
        """Order of planets shouldn't matter."""
        engine = MoietyOrbEngine()
        assert engine.get_orb_allowance(
            SUN, MARS, "Opposition"
        ) == engine.get_orb_allowance(MARS, SUN, "Opposition")

    def test_aspect_type_ignored_by_default(self):
        """Without minor_aspect_multiplier, aspect type doesn't affect orb."""
        engine = MoietyOrbEngine()
        conj = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        semi = engine.get_orb_allowance(SUN, MOON, "Semisextile")
        assert conj == semi


class TestSystems:
    """Named moiety system presets."""

    def test_default_is_lilly(self):
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        assert orb == (LILLY_FULL_ORBS["Sun"] + LILLY_FULL_ORBS["Moon"]) / 2

    def test_ptolemy_system(self):
        engine = MoietyOrbEngine(system="ptolemy")
        orb = engine.get_orb_allowance(SUN, JUPITER, "Trine")
        assert orb == (PTOLEMY_FULL_ORBS["Sun"] + PTOLEMY_FULL_ORBS["Jupiter"]) / 2
        # Ptolemy: (17 + 12) / 2 = 14.5 vs Lilly: (15 + 9) / 2 = 12.0
        assert orb == 14.5

    def test_lilly_explicit(self):
        engine = MoietyOrbEngine(system="lilly")
        orb = engine.get_orb_allowance(SUN, JUPITER, "Trine")
        assert orb == 12.0

    def test_ptolemy_vs_lilly_jupiter(self):
        """Ptolemy gives Jupiter a much larger orb (12° vs 9°)."""
        lilly = MoietyOrbEngine(system="lilly")
        ptolemy = MoietyOrbEngine(system="ptolemy")
        lilly_orb = lilly.get_orb_allowance(JUPITER, SATURN, "Conjunction")
        ptolemy_orb = ptolemy.get_orb_allowance(JUPITER, SATURN, "Conjunction")
        assert ptolemy_orb > lilly_orb


class TestCustomOrbs:
    """Custom orb_map overrides and merging."""

    def test_custom_orb_map(self):
        engine = MoietyOrbEngine(orb_map={"Sun": 20.0, "Moon": 15.0})
        orb = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        assert orb == (20.0 + 15.0) / 2

    def test_custom_overrides_system(self):
        """Custom values override system defaults for specific planets."""
        engine = MoietyOrbEngine(system="lilly", orb_map={"Sun": 20.0})
        orb = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        # Sun overridden to 20, Moon stays at Lilly default 12
        assert orb == (20.0 + 12.0) / 2

    def test_fallback_orb(self):
        """Unknown planets use fallback_orb."""
        engine = MoietyOrbEngine(fallback_orb=2.0)
        unknown = _make_pos("Hypothetical Planet X")
        orb = engine.get_orb_allowance(SUN, unknown, "Conjunction")
        assert orb == (15.0 + 2.0) / 2  # 8.5

    def test_default_fallback(self):
        """Default fallback is 3.0."""
        engine = MoietyOrbEngine()
        unknown = _make_pos("Hypothetical Planet X")
        orb = engine.get_orb_allowance(unknown, unknown, "Conjunction")
        assert orb == 3.0


class TestMinorAspectMultiplier:
    """Optional tighter orbs for non-major aspects."""

    def test_major_aspect_unaffected(self):
        engine = MoietyOrbEngine(minor_aspect_multiplier=0.4)
        orb = engine.get_orb_allowance(SUN, MOON, "Conjunction")
        assert orb == (15.0 + 12.0) / 2  # Major → no multiplier

    def test_minor_aspect_reduced(self):
        engine = MoietyOrbEngine(minor_aspect_multiplier=0.4)
        base_orb = (15.0 + 12.0) / 2  # 13.5
        orb = engine.get_orb_allowance(SUN, MOON, "Semisextile")
        assert orb == pytest.approx(base_orb * 0.4)

    def test_harmonic_aspect_reduced(self):
        engine = MoietyOrbEngine(minor_aspect_multiplier=0.3)
        base_orb = (15.0 + 12.0) / 2
        orb = engine.get_orb_allowance(SUN, MOON, "Quintile")
        assert orb == pytest.approx(base_orb * 0.3)

    def test_no_multiplier_all_equal(self):
        """Without multiplier, major and minor get same orb."""
        engine = MoietyOrbEngine()
        major = engine.get_orb_allowance(SUN, SATURN, "Square")
        minor = engine.get_orb_allowance(SUN, SATURN, "Semisextile")
        assert major == minor


class TestOuterPlanets:
    """Outer planets have conservative defaults."""

    def test_pluto_has_smaller_orb(self):
        engine = MoietyOrbEngine()
        sun_pluto = engine.get_orb_allowance(SUN, PLUTO, "Conjunction")
        sun_mars = engine.get_orb_allowance(SUN, MARS, "Conjunction")
        assert sun_pluto < sun_mars  # Pluto (5°) < Mars (8°)

    def test_chiron_has_small_orb(self):
        engine = MoietyOrbEngine()
        orb = engine.get_orb_allowance(SUN, CHIRON, "Conjunction")
        assert orb == (15.0 + 3.0) / 2  # 9.0


class TestIntegration:
    """Integration with ChartBuilder."""

    @pytest.mark.slow
    def test_chart_with_moiety_engine(self):
        from stellium import ChartBuilder

        chart = (
            ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
            .with_aspects()
            .with_orbs(MoietyOrbEngine())
            .calculate()
        )
        assert len(chart.aspects) > 0

    @pytest.mark.slow
    def test_chart_with_ptolemy_moieties(self):
        from stellium import ChartBuilder

        chart = (
            ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
            .with_aspects()
            .with_orbs(MoietyOrbEngine(system="ptolemy"))
            .calculate()
        )
        assert len(chart.aspects) > 0

    @pytest.mark.slow
    def test_moiety_finds_more_aspects_than_simple(self):
        """Moiety orbs are generally wider, so should find >= as many aspects."""
        from stellium import ChartBuilder
        from stellium.engines.orbs import SimpleOrbEngine

        builder = ChartBuilder.from_details(
            "2000-01-06 12:00", "Seattle, WA"
        ).with_aspects()
        simple_chart = builder.with_orbs(SimpleOrbEngine()).calculate()
        moiety_chart = builder.with_orbs(MoietyOrbEngine()).calculate()
        # Moiety orbs tend to be wider for luminary aspects
        assert len(moiety_chart.aspects) >= len(simple_chart.aspects) * 0.8
