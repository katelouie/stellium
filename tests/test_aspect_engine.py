"""Test aspect engines."""

import pytest

from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.aspects import HarmonicAspectEngine, ModernAspectEngine
from stellium.engines.orbs import SimpleOrbEngine


def test_conjunction_detection():
    """Test conjunction aspect detection."""
    engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()

    # Two planets in conjunction (within 8 degrees)
    sun = CelestialPosition(
        name="Sun", object_type=ObjectType.PLANET, longitude=30.0, speed_longitude=1.0
    )
    mercury = CelestialPosition(
        name="Mercury",
        object_type=ObjectType.PLANET,
        longitude=35.0,
        speed_longitude=1.2,
    )

    aspects = engine.calculate_aspects([sun, mercury], orb_engine)

    assert len(aspects) == 1
    assert aspects[0].aspect_name == "Conjunction"
    assert aspects[0].orb == 5.0


def test_trine_detection():
    """Test trine aspect detection."""
    engine = ModernAspectEngine()
    orb_engine = SimpleOrbEngine()

    sun = CelestialPosition(
        name="Sun", object_type=ObjectType.PLANET, longitude=0.0, speed_longitude=1.0
    )
    moon = CelestialPosition(
        name="Moon",
        object_type=ObjectType.PLANET,
        longitude=122.0,
        speed_longitude=13.0,
    )

    aspects = engine.calculate_aspects([sun, moon], orb_engine)

    assert len(aspects) == 1
    assert aspects[0].aspect_name == "Trine"
    assert aspects[0].orb == 2.0


def test_harmonic_aspects():
    """Test harmonic aspect engine."""
    engine = HarmonicAspectEngine(harmonic=7)
    orb_engine = SimpleOrbEngine(fallback_orb=1)

    # Septile = 360/7 = 51.43 degrees
    obj1 = CelestialPosition(name="Sun", object_type=ObjectType.PLANET, longitude=0.0)
    obj2 = CelestialPosition(name="Moon", object_type=ObjectType.PLANET, longitude=51.0)

    aspects = engine.calculate_aspects([obj1, obj2], orb_engine)

    assert len(aspects) > 0
    assert aspects[0].aspect_name == "H7"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
