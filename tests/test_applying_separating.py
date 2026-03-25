"""Comprehensive tests for applying/separating aspect determination.

Tests the _is_applying function in aspects.py, covering:
- Basic applying/separating detection
- Stationary body handling (speed near zero)
- Speed-unknown handling (speed == 0.0 default)
- 0°/360° zodiac seam edge cases
- Retrograde motion
- Various aspect types (conjunction, opposition, trine, square)
- Edge cases near exact aspects

Regression tests for GitHub issue #24 (TheDaniel166):
- Stationary body misclassification
- Zodiac seam failure in applying/separating
"""

from stellium.core.models import CelestialPosition, ObjectType
from stellium.engines.aspects import (
    _STATIONARY_THRESHOLD,
    _angular_distance,
    _is_applying,
)


def _make_pos(name: str, longitude: float, speed: float = 1.0) -> CelestialPosition:
    """Helper to create a CelestialPosition with minimal fields."""
    return CelestialPosition(
        name=name,
        object_type=ObjectType.PLANET,
        longitude=longitude,
        speed_longitude=speed,
    )


# =============================================================================
# BASIC APPLYING / SEPARATING
# =============================================================================


class TestBasicApplyingSeparating:
    """Test straightforward applying/separating detection."""

    def test_applying_conjunction_faster_planet_behind(self):
        """Faster planet catching up to slower → applying conjunction."""
        obj1 = _make_pos("Mars", 100.0, speed=0.8)
        obj2 = _make_pos("Saturn", 105.0, speed=0.2)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is True

    def test_separating_conjunction_slower_planet_behind(self):
        """Slower planet falling behind faster → separating conjunction."""
        obj1 = _make_pos("Saturn", 100.0, speed=0.2)
        obj2 = _make_pos("Mars", 105.0, speed=0.8)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is False

    def test_applying_opposition(self):
        """Saturn barely past opposition, Sun catching up → applying."""
        obj1 = _make_pos("Sun", 10.0, speed=1.0)
        obj2 = _make_pos("Saturn", 192.0, speed=0.05)
        distance = _angular_distance(10.0, 192.0)
        # Distance is 182°, Sun closing toward 180° exact
        result = _is_applying(obj1, obj2, 180.0, distance)
        assert result is True

    def test_separating_opposition(self):
        """Sun already past exact opposition, moving away → separating."""
        obj1 = _make_pos("Sun", 10.0, speed=1.0)
        obj2 = _make_pos("Saturn", 185.0, speed=0.05)
        distance = _angular_distance(10.0, 185.0)
        # Distance is 175°, Sun moving further from 180° exact
        result = _is_applying(obj1, obj2, 180.0, distance)
        assert result is False

    def test_applying_trine(self):
        """Slower planet leading, gap widening toward 120° exact → applying."""
        obj1 = _make_pos("Jupiter", 0.0, speed=0.08)
        obj2 = _make_pos("Sun", 119.0, speed=1.0)
        distance = _angular_distance(0.0, 119.0)
        # Sun pulling away from Jupiter, gap 119° growing toward 120° → applying
        result = _is_applying(obj1, obj2, 120.0, distance)
        assert result is True

    def test_separating_trine(self):
        """Slow planet leading, fast planet already well past trine → separating."""
        # Jupiter at 120°, Sun already at 5° and racing ahead
        # Gap is 115° and SHRINKING (toward conjunction, not trine)
        # For separating trine: need the gap to be growing AWAY from 120°
        obj1 = _make_pos("Jupiter", 100.0, speed=0.08)
        obj2 = _make_pos("Mars", 220.5, speed=0.5)
        distance = _angular_distance(100.0, 220.5)
        # Distance is 120.5°, Mars moving away → orb growing
        result = _is_applying(obj1, obj2, 120.0, distance)
        assert result is False

    def test_applying_square(self):
        """Planet approaching exact square → applying."""
        obj1 = _make_pos("Moon", 85.0, speed=13.0)
        obj2 = _make_pos("Saturn", 178.0, speed=0.1)
        distance = _angular_distance(85.0, 178.0)
        # Distance is ~93°, approaching 90° as Moon catches up
        result = _is_applying(obj1, obj2, 90.0, distance)
        assert result is True


# =============================================================================
# STATIONARY BODY DETECTION (GitHub issue #24, bug 1)
# =============================================================================


class TestStationaryBody:
    """Test that stationary bodies (speed near zero) return None, not False."""

    def test_stationary_obj1_returns_none(self):
        """First body at station → applying/separating is undefined."""
        obj1 = _make_pos("Saturn", 100.0, speed=0.001)  # nearly stationary
        obj2 = _make_pos("Sun", 105.0, speed=1.0)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is None

    def test_stationary_obj2_returns_none(self):
        """Second body at station → applying/separating is undefined."""
        obj1 = _make_pos("Sun", 100.0, speed=1.0)
        obj2 = _make_pos("Saturn", 105.0, speed=0.002)  # nearly stationary
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is None

    def test_both_stationary_returns_none(self):
        """Both bodies stationary → undefined."""
        obj1 = _make_pos("Saturn", 100.0, speed=0.001)
        obj2 = _make_pos("Jupiter", 105.0, speed=-0.002)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is None

    def test_speed_exactly_zero_returns_none(self):
        """Speed == 0.0 (the default) should be treated as stationary/unknown."""
        obj1 = _make_pos("Mars", 100.0, speed=0.0)
        obj2 = _make_pos("Sun", 105.0, speed=1.0)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is None

    def test_speed_just_above_threshold_is_not_stationary(self):
        """Speed just above threshold should NOT be treated as stationary."""
        obj1 = _make_pos("Mars", 100.0, speed=_STATIONARY_THRESHOLD + 0.001)
        obj2 = _make_pos("Saturn", 105.0, speed=0.1)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is not None  # should return True or False, not None

    def test_negative_speed_stationary(self):
        """Negative speed near zero (retrograde station) → stationary."""
        obj1 = _make_pos("Mercury", 100.0, speed=-0.003)
        obj2 = _make_pos("Sun", 105.0, speed=1.0)
        distance = _angular_distance(100.0, 105.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is None


# =============================================================================
# ZODIAC SEAM (0°/360°) EDGE CASES (GitHub issue #24, bug 2)
# =============================================================================


class TestZodiacSeam:
    """Test that applying/separating works correctly near 0° Aries."""

    def test_conjunction_straddling_aries_point_applying(self):
        """One body at 359°, other at 1° — should detect applying if closing."""
        obj1 = _make_pos("Mars", 359.0, speed=0.7)
        obj2 = _make_pos("Jupiter", 1.0, speed=0.1)
        distance = _angular_distance(359.0, 1.0)  # = 2°
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is True  # Mars closing the 2° gap

    def test_conjunction_straddling_aries_point_separating(self):
        """Bodies moving apart across 0° → separating."""
        obj1 = _make_pos("Mars", 1.0, speed=0.7)
        obj2 = _make_pos("Jupiter", 359.0, speed=-0.1)
        distance = _angular_distance(1.0, 359.0)  # = 2°
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is False  # Moving apart

    def test_opposition_near_seam(self):
        """Opposition with one body near 0° and other near 180°."""
        obj1 = _make_pos("Sun", 358.0, speed=1.0)
        obj2 = _make_pos("Saturn", 181.0, speed=0.05)
        distance = _angular_distance(358.0, 181.0)  # = 177°
        result = _is_applying(obj1, obj2, 180.0, distance)
        # Distance is 177°, Sun crossing 0° toward exact 180° opposition
        assert result is True

    def test_trine_near_seam(self):
        """Trine with one body near 0°: 355° and 115° are ~120° apart."""
        obj1 = _make_pos("Venus", 355.0, speed=1.2)
        obj2 = _make_pos("Jupiter", 116.0, speed=0.08)
        distance = _angular_distance(355.0, 116.0)  # = 121°
        result = _is_applying(obj1, obj2, 120.0, distance)
        assert result is True  # Venus approaching exact trine


# =============================================================================
# RETROGRADE MOTION
# =============================================================================


class TestRetrograde:
    """Test applying/separating with retrograde (negative speed) planets."""

    def test_retrograde_planet_applying_conjunction(self):
        """Retrograde planet backing into a conjunction → applying."""
        obj1 = _make_pos("Mercury", 105.0, speed=-1.5)  # retrograde
        obj2 = _make_pos("Sun", 100.0, speed=1.0)
        distance = _angular_distance(105.0, 100.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is True

    def test_retrograde_planet_separating(self):
        """Retrograde planet moving away → separating."""
        obj1 = _make_pos(
            "Mercury", 95.0, speed=-1.5
        )  # retrograde, moving away from Sun
        obj2 = _make_pos("Sun", 100.0, speed=1.0)
        distance = _angular_distance(95.0, 100.0)
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is False

    def test_both_retrograde(self):
        """Both planets retrograde — faster retrograde closes gap."""
        obj1 = _make_pos("Mercury", 105.0, speed=-1.5)
        obj2 = _make_pos("Mars", 100.0, speed=-0.3)
        distance = _angular_distance(105.0, 100.0)
        # Mercury at -1.5 is moving backward faster than Mars at -0.3
        # Mercury approaches Mars from behind
        result = _is_applying(obj1, obj2, 0.0, distance)
        assert result is True


# =============================================================================
# ANGULAR DISTANCE HELPER
# =============================================================================


class TestAngularDistance:
    """Test the _angular_distance helper function."""

    def test_same_position(self):
        assert _angular_distance(100.0, 100.0) == 0.0

    def test_simple_distance(self):
        assert _angular_distance(10.0, 50.0) == 40.0

    def test_opposite(self):
        assert _angular_distance(0.0, 180.0) == 180.0

    def test_wrap_around(self):
        """359° to 1° should be 2°, not 358°."""
        assert _angular_distance(359.0, 1.0) == 2.0

    def test_symmetric(self):
        """Distance should be the same regardless of order."""
        assert _angular_distance(30.0, 150.0) == _angular_distance(150.0, 30.0)

    def test_large_values(self):
        """Values near 360° should work correctly."""
        assert _angular_distance(350.0, 10.0) == 20.0
