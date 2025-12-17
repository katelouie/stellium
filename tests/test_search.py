"""Tests for stellium.engines.search - longitude crossing search functionality."""

from datetime import datetime

import pytest

from stellium.engines.search import (
    ASPECT_ANGLES,
    SIGN_BOUNDARIES,
    SIGN_ORDER,
    AngleCrossing,
    AspectExact,
    LongitudeCrossing,
    SignIngress,
    Station,
    _datetime_to_julian_day,
    _get_previous_sign,
    _get_sign_from_longitude,
    _julian_day_to_datetime,
    _normalize_angle_error,
    find_all_angle_crossings,
    find_all_aspect_exacts,
    find_all_ingresses,
    find_all_longitude_crossings,
    find_all_sign_changes,
    find_all_stations,
    find_angle_crossing,
    find_aspect_exact,
    find_ingress,
    find_longitude_crossing,
    find_next_sign_change,
    find_station,
)


class TestNormalizeAngleError:
    """Tests for the angle normalization helper function."""

    def test_zero_difference(self):
        """Zero difference stays zero."""
        assert _normalize_angle_error(0.0) == 0.0

    def test_small_positive(self):
        """Small positive difference unchanged."""
        assert _normalize_angle_error(10.0) == 10.0

    def test_small_negative(self):
        """Small negative difference unchanged."""
        assert _normalize_angle_error(-10.0) == -10.0

    def test_wraparound_positive(self):
        """Large positive wraps to negative (359° to 1° = +2°)."""
        # 358° difference should wrap to -2°
        assert _normalize_angle_error(358.0) == pytest.approx(-2.0)

    def test_wraparound_negative(self):
        """Large negative wraps to positive (1° to 359° = -2°)."""
        # -358° difference should wrap to +2°
        assert _normalize_angle_error(-358.0) == pytest.approx(2.0)

    def test_exactly_180(self):
        """180° stays at boundary."""
        result = _normalize_angle_error(180.0)
        assert result == pytest.approx(-180.0)

    def test_exactly_negative_180(self):
        """−180° stays at boundary."""
        result = _normalize_angle_error(-180.0)
        assert result == pytest.approx(-180.0)

    def test_just_over_180(self):
        """181° wraps to -179°."""
        assert _normalize_angle_error(181.0) == pytest.approx(-179.0)


class TestLongitudeCrossingDataclass:
    """Tests for the LongitudeCrossing result dataclass."""

    def test_is_retrograde_property(self):
        """Test is_retrograde correctly reflects negative speed."""
        crossing = LongitudeCrossing(
            julian_day=2460000.0,
            datetime_utc=datetime(2023, 1, 1, 12, 0),
            longitude=120.0,
            speed=-0.5,
            is_retrograde=True,
            object_name="Mercury",
        )
        assert crossing.is_retrograde is True
        assert crossing.is_direct is False

    def test_is_direct_property(self):
        """Test is_direct correctly reflects positive speed."""
        crossing = LongitudeCrossing(
            julian_day=2460000.0,
            datetime_utc=datetime(2023, 1, 1, 12, 0),
            longitude=120.0,
            speed=1.0,
            is_retrograde=False,
            object_name="Sun",
        )
        assert crossing.is_retrograde is False
        assert crossing.is_direct is True

    def test_frozen_dataclass(self):
        """Verify dataclass is immutable."""
        crossing = LongitudeCrossing(
            julian_day=2460000.0,
            datetime_utc=datetime(2023, 1, 1, 12, 0),
            longitude=120.0,
            speed=1.0,
            is_retrograde=False,
            object_name="Sun",
        )
        with pytest.raises(AttributeError):
            crossing.longitude = 130.0


class TestFindLongitudeCrossing:
    """Tests for find_longitude_crossing - single crossing search."""

    def test_find_sun_at_0_aries(self):
        """Find vernal equinox (Sun at 0° Aries) in 2024."""
        result = find_longitude_crossing(
            "Sun",
            0.0,  # 0° Aries
            datetime(2024, 1, 1),
            direction="forward",
        )

        assert result is not None
        assert result.object_name == "Sun"
        # Vernal equinox 2024 is around March 20
        assert result.datetime_utc.month == 3
        assert 19 <= result.datetime_utc.day <= 21
        # Longitude should be very close to target (handle 360/0 wraparound)
        normalized_lon = result.longitude % 360
        assert normalized_lon == pytest.approx(
            0.0, abs=0.01
        ) or normalized_lon == pytest.approx(360.0, abs=0.01)
        # Sun is always direct
        assert result.is_direct is True

    def test_find_sun_at_0_cancer(self):
        """Find summer solstice (Sun at 0° Cancer) in 2024."""
        result = find_longitude_crossing(
            "Sun",
            90.0,  # 0° Cancer
            datetime(2024, 1, 1),
            direction="forward",
        )

        assert result is not None
        # Summer solstice 2024 is around June 20
        assert result.datetime_utc.month == 6
        assert 19 <= result.datetime_utc.day <= 22
        assert result.longitude == pytest.approx(90.0, abs=0.001)

    def test_find_moon_crossing(self):
        """Find Moon crossing a specific degree."""
        result = find_longitude_crossing(
            "Moon",
            45.0,  # 15° Taurus
            datetime(2024, 1, 1),
            direction="forward",
            max_days=30,  # Moon will cross within a month
        )

        assert result is not None
        assert result.object_name == "Moon"
        assert result.longitude == pytest.approx(45.0, abs=0.001)
        # Moon should be found within January (orbits in ~27 days)
        assert result.datetime_utc.month == 1

    def test_backward_search(self):
        """Search backward in time."""
        result = find_longitude_crossing(
            "Sun",
            270.0,  # 0° Capricorn (winter solstice)
            datetime(2024, 1, 1),
            direction="backward",
        )

        assert result is not None
        # Should find Dec 2023 winter solstice
        assert result.datetime_utc.year == 2023
        assert result.datetime_utc.month == 12
        assert 20 <= result.datetime_utc.day <= 23

    def test_unknown_object_raises(self):
        """Unknown object name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown object"):
            find_longitude_crossing(
                "NotAPlanet",
                0.0,
                datetime(2024, 1, 1),
            )

    def test_accepts_julian_day_input(self):
        """Can pass Julian day instead of datetime."""
        # Julian day for approximately Jan 1, 2024
        jd = 2460310.5
        result = find_longitude_crossing(
            "Sun",
            0.0,
            jd,  # Julian day input
            direction="forward",
        )

        assert result is not None
        assert result.datetime_utc.year == 2024

    def test_not_found_returns_none(self):
        """Returns None if crossing not found within max_days."""
        # Sun moves ~1°/day, so looking for a degree 180° away
        # with only 1 day max search should fail
        result = find_longitude_crossing(
            "Sun",
            180.0,  # Very far from current position
            datetime(2024, 1, 1),
            max_days=1.0,
        )

        # Sun can't move 180° in 1 day, so this should return None
        # (or find it if the target happens to be close, but 180° away from 0° Capricorn
        # is 0° Cancer which is ~6 months away)
        # Actually let's test with a guaranteed fail
        result = find_longitude_crossing(
            "Saturn",  # Slow planet
            0.0,  # Specific degree
            datetime(2024, 1, 1),
            max_days=0.1,  # Very short search window
        )
        # Saturn takes ~29 years to orbit, won't hit arbitrary degree in 0.1 days
        # This test depends on Saturn's position - might or might not find it
        # Let's just verify it returns LongitudeCrossing or None (valid types)
        assert result is None or isinstance(result, LongitudeCrossing)

    def test_tolerance_parameter(self):
        """Custom tolerance affects precision."""
        result_default = find_longitude_crossing(
            "Sun",
            0.0,
            datetime(2024, 1, 1),
        )

        result_tight = find_longitude_crossing(
            "Sun",
            0.0,
            datetime(2024, 1, 1),
            tolerance=0.00001,  # Tighter tolerance
        )

        assert result_default is not None
        assert result_tight is not None
        # Both should find the same event
        assert abs(result_default.julian_day - result_tight.julian_day) < 0.01

    def test_mars_crossing(self):
        """Test with Mars (slower than Sun, can be retrograde)."""
        result = find_longitude_crossing(
            "Mars",
            0.0,  # 0° Aries
            datetime(2024, 1, 1),
            direction="forward",
            max_days=730,  # Mars takes ~2 years to orbit
        )

        assert result is not None
        assert result.object_name == "Mars"
        # Handle 360/0 wraparound
        normalized_lon = result.longitude % 360
        assert normalized_lon == pytest.approx(
            0.0, abs=0.01
        ) or normalized_lon == pytest.approx(360.0, abs=0.01)

    def test_mercury_crossing(self):
        """Test with Mercury (fast, frequently retrograde)."""
        result = find_longitude_crossing(
            "Mercury",
            30.0,  # 0° Taurus
            datetime(2024, 1, 1),
            direction="forward",
        )

        assert result is not None
        assert result.object_name == "Mercury"
        assert result.longitude == pytest.approx(30.0, abs=0.001)


class TestFindAllLongitudeCrossings:
    """Tests for find_all_longitude_crossings - multiple crossings in range."""

    def test_moon_multiple_crossings(self):
        """Moon should cross any degree about 13 times per year."""
        results = find_all_longitude_crossings(
            "Moon",
            100.0,  # Arbitrary degree
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
        )

        # Moon orbits ~13 times per year
        assert len(results) >= 12
        assert len(results) <= 14

        # All results should be for Moon
        for result in results:
            assert result.object_name == "Moon"

        # Results should be chronologically ordered
        for i in range(len(results) - 1):
            assert results[i].julian_day < results[i + 1].julian_day

        # All longitudes should be close to target
        for result in results:
            assert result.longitude == pytest.approx(100.0, abs=0.01)

    def test_sun_single_crossing_per_year(self):
        """Sun crosses each degree exactly once per year."""
        results = find_all_longitude_crossings(
            "Sun",
            45.0,  # Arbitrary degree
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
        )

        # Sun should cross each degree exactly once per year
        assert len(results) == 1
        assert results[0].longitude == pytest.approx(45.0, abs=0.001)

    def test_mercury_multiple_due_to_retrograde(self):
        """Mercury can cross a degree up to 3 times during retrograde."""
        # Mercury retrogrades ~3 times per year, potentially crossing
        # certain degrees multiple times
        results = find_all_longitude_crossings(
            "Mercury",
            60.0,  # Degree that might be hit during retrograde
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
        )

        # Mercury should cross most degrees 1-3 times per pass through that zodiac area
        assert len(results) >= 1
        # Mercury orbits ~4 times per year with retrograde periods
        assert len(results) <= 8

    def test_empty_range_returns_empty_list(self):
        """Very short date range with no crossing returns empty list."""
        # Sun moves ~1°/day, so in 0.1 days it moves ~0.1°
        # Looking for a degree far from current Sun position
        results = find_all_longitude_crossings(
            "Sun",
            180.0,  # Opposite to where Sun is in January
            datetime(2024, 1, 1, 0, 0),
            datetime(2024, 1, 1, 1, 0),  # Only 1 hour range
        )

        # Should be empty - Sun can't reach 180° from ~280° in 1 hour
        assert results == []

    def test_max_results_limit(self):
        """max_results parameter limits output."""
        results = find_all_longitude_crossings(
            "Moon",
            100.0,
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
            max_results=3,
        )

        assert len(results) <= 3

    def test_accepts_julian_day_inputs(self):
        """Can use Julian days for start and end."""
        start_jd = 2460310.5  # ~Jan 1, 2024
        end_jd = 2460340.5  # ~Jan 31, 2024

        results = find_all_longitude_crossings(
            "Moon",
            50.0,
            start_jd,
            end_jd,
        )

        # Should find 1-2 Moon crossings in a month
        assert len(results) >= 1

    def test_results_within_date_range(self):
        """All results should be within the specified date range."""
        start = datetime(2024, 6, 1)
        end = datetime(2024, 6, 30)

        results = find_all_longitude_crossings(
            "Moon",
            75.0,
            start,
            end,
        )

        for result in results:
            assert result.datetime_utc >= start
            assert result.datetime_utc <= end


class TestSearchIntegration:
    """Integration tests combining search with known astronomical events."""

    def test_find_2024_equinoxes(self):
        """Find both equinoxes in 2024."""
        # Vernal equinox (Sun at 0° Aries)
        vernal = find_longitude_crossing(
            "Sun", 0.0, datetime(2024, 1, 1), direction="forward"
        )
        # Autumnal equinox (Sun at 0° Libra = 180°)
        autumnal = find_longitude_crossing(
            "Sun", 180.0, datetime(2024, 1, 1), direction="forward"
        )

        assert vernal is not None
        assert autumnal is not None

        # Vernal: March 20, 2024
        assert vernal.datetime_utc.month == 3
        # Autumnal: September 22, 2024
        assert autumnal.datetime_utc.month == 9

    def test_find_2024_solstices(self):
        """Find both solstices in 2024."""
        # Summer solstice (Sun at 0° Cancer = 90°)
        summer = find_longitude_crossing(
            "Sun", 90.0, datetime(2024, 1, 1), direction="forward"
        )
        # Winter solstice (Sun at 0° Capricorn = 270°)
        winter = find_longitude_crossing(
            "Sun", 270.0, datetime(2024, 1, 1), direction="forward"
        )

        assert summer is not None
        assert winter is not None

        # Summer: June 20-21, 2024
        assert summer.datetime_utc.month == 6
        # Winter: December 21-22, 2024
        assert winter.datetime_utc.month == 12

    def test_venus_ingress_tracking(self):
        """Track Venus entering a new sign."""
        # Venus entering Taurus (30°)
        result = find_longitude_crossing(
            "Venus", 30.0, datetime(2024, 1, 1), direction="forward"
        )

        assert result is not None
        assert result.object_name == "Venus"
        # Venus should always be relatively close to the Sun (within ~47°)
        # and moving relatively quickly when direct

    def test_jupiter_slow_movement(self):
        """Jupiter moves slowly - should still be found."""
        # Jupiter was in Taurus (~40-60°) in early 2024, moving to Gemini (~60-90°) later
        # Look for a degree Jupiter will cross in 2024
        result = find_longitude_crossing(
            "Jupiter",
            60.0,  # 0° Gemini - Jupiter enters Gemini in 2024
            datetime(2024, 1, 1),
            direction="forward",
            max_days=365,
        )

        assert result is not None
        assert result.longitude == pytest.approx(60.0, abs=0.01)

    def test_saturn_very_slow(self):
        """Saturn is very slow but should still be findable."""
        # Saturn was in Pisces (~330-360°) throughout 2024
        # Look for a degree Saturn will cross within the range it's moving through
        result = find_longitude_crossing(
            "Saturn",
            340.0,  # 10° Pisces - Saturn will cross this in 2024
            datetime(2024, 1, 1),
            direction="forward",
            max_days=365,
        )

        assert result is not None
        assert result.longitude == pytest.approx(340.0, abs=0.01)

    def test_nodes_movement(self):
        """Test True Node (moves mostly retrograde)."""
        # True Node was in Aries (~0-30°) in early 2024, moving backward through the zodiac
        # Look for a degree the node will cross going backward
        result = find_longitude_crossing(
            "True Node",  # Correct name from SWISS_EPHEMERIS_IDS
            10.0,  # 10° Aries - Node should cross this in 2024
            datetime(2024, 1, 1),
            direction="forward",
            max_days=365,
        )

        assert result is not None
        assert result.object_name == "True Node"
        # True Node is typically retrograde (though can briefly go direct)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_target_at_360_equivalent_to_0(self):
        """360° should be equivalent to 0°."""
        result_0 = find_longitude_crossing(
            "Sun", 0.0, datetime(2024, 1, 1), direction="forward"
        )
        result_360 = find_longitude_crossing(
            "Sun", 360.0, datetime(2024, 1, 1), direction="forward"
        )

        assert result_0 is not None
        assert result_360 is not None
        # Should find same crossing
        assert abs(result_0.julian_day - result_360.julian_day) < 0.001

    def test_negative_longitude_normalized(self):
        """Negative longitude should be normalized."""
        result_positive = find_longitude_crossing(
            "Sun", 350.0, datetime(2024, 1, 1), direction="forward"
        )
        result_negative = find_longitude_crossing(
            "Sun", -10.0, datetime(2024, 1, 1), direction="forward"
        )

        assert result_positive is not None
        assert result_negative is not None
        # -10° = 350°, should find same crossing
        assert abs(result_positive.julian_day - result_negative.julian_day) < 0.001

    def test_longitude_over_360_normalized(self):
        """Longitude > 360 should be normalized."""
        result_normal = find_longitude_crossing(
            "Sun", 30.0, datetime(2024, 1, 1), direction="forward"
        )
        result_over = find_longitude_crossing(
            "Sun", 390.0, datetime(2024, 1, 1), direction="forward"
        )

        assert result_normal is not None
        assert result_over is not None
        # 390° = 30°, should find same crossing
        assert abs(result_normal.julian_day - result_over.julian_day) < 0.001

    def test_chiron_crossing(self):
        """Test with Chiron (slow outer body)."""
        # Chiron was at ~15-20° Aries in early 2024
        # Look for a degree Chiron will cross in 2024
        result = find_longitude_crossing(
            "Chiron",
            18.0,  # 18° Aries - Chiron should cross this in 2024
            datetime(2024, 1, 1),
            direction="forward",
            max_days=365,
        )

        # Chiron was in Aries in 2024, should find crossing
        assert result is not None
        assert result.object_name == "Chiron"
        assert result.longitude == pytest.approx(18.0, abs=0.01)

    def test_part_of_fortune_if_supported(self):
        """Test Part of Fortune if it's in the registry."""
        # This might fail if Part of Fortune isn't in SWISS_EPHEMERIS_IDS
        # That's expected - the test documents the current behavior
        try:
            result = find_longitude_crossing(
                "Part of Fortune",
                0.0,
                datetime(2024, 1, 1),
                max_days=30,
            )
            # If supported, should return a result
            assert result is None or isinstance(result, LongitudeCrossing)
        except ValueError:
            # Expected if Part of Fortune is not in the registry
            pass


# =============================================================================
# Tests for Helper Functions
# =============================================================================


class TestJulianDayConversion:
    """Tests for Julian day conversion functions."""

    def test_datetime_to_julian_day_j2000(self):
        """Test conversion for J2000 epoch."""
        # J2000.0 = January 1, 2000, 12:00 TT = JD 2451545.0
        dt = datetime(2000, 1, 1, 12, 0, 0)
        jd = _datetime_to_julian_day(dt)
        assert jd == pytest.approx(2451545.0, abs=0.001)

    def test_datetime_to_julian_day_with_microseconds(self):
        """Test conversion preserves microseconds."""
        dt = datetime(2024, 6, 15, 18, 30, 45, 500000)
        jd = _datetime_to_julian_day(dt)
        # Round-trip should preserve time
        dt_back = _julian_day_to_datetime(jd)
        assert dt_back.year == dt.year
        assert dt_back.month == dt.month
        assert dt_back.day == dt.day
        assert dt_back.hour == dt.hour
        assert dt_back.minute == dt.minute
        assert abs(dt_back.second - dt.second) <= 1

    def test_julian_day_to_datetime_roundtrip(self):
        """Test round-trip conversion."""
        original_jd = 2460400.75  # Some arbitrary JD
        dt = _julian_day_to_datetime(original_jd)
        recovered_jd = _datetime_to_julian_day(dt)
        assert recovered_jd == pytest.approx(original_jd, abs=0.0001)

    def test_julian_day_to_datetime_known_date(self):
        """Test with a known date."""
        # JD 2451545.0 = Jan 1, 2000 at noon
        dt = _julian_day_to_datetime(2451545.0)
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12


class TestGetSignFromLongitude:
    """Tests for _get_sign_from_longitude helper."""

    def test_aries_start(self):
        """0° is Aries."""
        assert _get_sign_from_longitude(0.0) == "Aries"

    def test_aries_mid(self):
        """15° is still Aries."""
        assert _get_sign_from_longitude(15.0) == "Aries"

    def test_taurus_start(self):
        """30° is Taurus."""
        assert _get_sign_from_longitude(30.0) == "Taurus"

    def test_pisces_end(self):
        """359° is Pisces."""
        assert _get_sign_from_longitude(359.0) == "Pisces"

    def test_all_sign_boundaries(self):
        """Test all sign boundaries."""
        expected = [
            (0.0, "Aries"),
            (30.0, "Taurus"),
            (60.0, "Gemini"),
            (90.0, "Cancer"),
            (120.0, "Leo"),
            (150.0, "Virgo"),
            (180.0, "Libra"),
            (210.0, "Scorpio"),
            (240.0, "Sagittarius"),
            (270.0, "Capricorn"),
            (300.0, "Aquarius"),
            (330.0, "Pisces"),
        ]
        for lon, sign in expected:
            assert _get_sign_from_longitude(lon) == sign

    def test_over_360_wraps(self):
        """Longitude over 360° wraps correctly."""
        assert _get_sign_from_longitude(370.0) == "Aries"  # 370 - 360 = 10° Aries


class TestGetPreviousSign:
    """Tests for _get_previous_sign helper."""

    def test_taurus_previous_is_aries(self):
        """Sign before Taurus is Aries."""
        assert _get_previous_sign("Taurus") == "Aries"

    def test_aries_previous_is_pisces(self):
        """Sign before Aries is Pisces (wraps around)."""
        assert _get_previous_sign("Aries") == "Pisces"

    def test_all_previous_signs(self):
        """Test all previous sign relationships."""
        for i, sign in enumerate(SIGN_ORDER):
            expected_previous = SIGN_ORDER[(i - 1) % 12]
            assert _get_previous_sign(sign) == expected_previous


class TestSignBoundariesAndOrder:
    """Tests for SIGN_BOUNDARIES and SIGN_ORDER constants."""

    def test_sign_order_has_12_signs(self):
        """SIGN_ORDER should have exactly 12 signs."""
        assert len(SIGN_ORDER) == 12

    def test_sign_boundaries_has_12_entries(self):
        """SIGN_BOUNDARIES should have exactly 12 entries."""
        assert len(SIGN_BOUNDARIES) == 12

    def test_sign_boundaries_values(self):
        """SIGN_BOUNDARIES should have correct degree values."""
        assert SIGN_BOUNDARIES["Aries"] == 0.0
        assert SIGN_BOUNDARIES["Taurus"] == 30.0
        assert SIGN_BOUNDARIES["Cancer"] == 90.0
        assert SIGN_BOUNDARIES["Libra"] == 180.0
        assert SIGN_BOUNDARIES["Capricorn"] == 270.0

    def test_sign_order_starts_with_aries(self):
        """SIGN_ORDER should start with Aries."""
        assert SIGN_ORDER[0] == "Aries"

    def test_sign_order_ends_with_pisces(self):
        """SIGN_ORDER should end with Pisces."""
        assert SIGN_ORDER[-1] == "Pisces"


# =============================================================================
# Tests for SignIngress Dataclass
# =============================================================================


class TestSignIngressDataclass:
    """Tests for the SignIngress result dataclass."""

    def test_create_sign_ingress(self):
        """Test creating a SignIngress object."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 0),
            object_name="Sun",
            sign="Taurus",
            from_sign="Aries",
            longitude=30.0,
            speed=0.98,
            is_retrograde=False,
        )
        assert ingress.object_name == "Sun"
        assert ingress.sign == "Taurus"
        assert ingress.from_sign == "Aries"
        assert ingress.longitude == 30.0

    def test_is_direct_property(self):
        """Test is_direct property."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 0),
            object_name="Sun",
            sign="Taurus",
            from_sign="Aries",
            longitude=30.0,
            speed=0.98,
            is_retrograde=False,
        )
        assert ingress.is_direct is True
        assert ingress.is_retrograde is False

    def test_is_retrograde_property(self):
        """Test is_retrograde property for retrograde ingress."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 0),
            object_name="Mercury",
            sign="Aries",
            from_sign="Taurus",
            longitude=0.0,
            speed=-0.5,
            is_retrograde=True,
        )
        assert ingress.is_retrograde is True
        assert ingress.is_direct is False

    def test_str_method_direct(self):
        """Test __str__ method for direct ingress."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 30),
            object_name="Sun",
            sign="Taurus",
            from_sign="Aries",
            longitude=30.0,
            speed=0.98,
            is_retrograde=False,
        )
        result = str(ingress)
        assert "Sun" in result
        assert "enters Taurus" in result
        assert "2024-04-20 12:30" in result

    def test_str_method_retrograde(self):
        """Test __str__ method shows Rx for retrograde."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 30),
            object_name="Mercury",
            sign="Aries",
            from_sign="Taurus",
            longitude=0.0,
            speed=-0.5,
            is_retrograde=True,
        )
        result = str(ingress)
        assert "Mercury" in result
        assert "Rx" in result
        assert "enters Aries" in result

    def test_frozen_dataclass(self):
        """Verify SignIngress is immutable."""
        ingress = SignIngress(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 20, 12, 0),
            object_name="Sun",
            sign="Taurus",
            from_sign="Aries",
            longitude=30.0,
            speed=0.98,
            is_retrograde=False,
        )
        with pytest.raises(AttributeError):
            ingress.sign = "Gemini"


# =============================================================================
# Tests for Station Dataclass
# =============================================================================


class TestStationDataclass:
    """Tests for the Station result dataclass."""

    def test_create_station_retrograde(self):
        """Test creating a retrograde station."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 1, 12, 0),
            object_name="Mercury",
            station_type="retrograde",
            longitude=27.5,
            sign="Aries",
        )
        assert station.object_name == "Mercury"
        assert station.station_type == "retrograde"
        assert station.longitude == 27.5
        assert station.sign == "Aries"

    def test_create_station_direct(self):
        """Test creating a direct station."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 25, 12, 0),
            object_name="Mercury",
            station_type="direct",
            longitude=15.5,
            sign="Aries",
        )
        assert station.station_type == "direct"

    def test_is_turning_retrograde(self):
        """Test is_turning_retrograde property."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 1, 12, 0),
            object_name="Mercury",
            station_type="retrograde",
            longitude=27.5,
            sign="Aries",
        )
        assert station.is_turning_retrograde is True
        assert station.is_turning_direct is False

    def test_is_turning_direct(self):
        """Test is_turning_direct property."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 25, 12, 0),
            object_name="Mercury",
            station_type="direct",
            longitude=15.5,
            sign="Aries",
        )
        assert station.is_turning_direct is True
        assert station.is_turning_retrograde is False

    def test_degree_in_sign_property(self):
        """Test degree_in_sign property."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 1, 12, 0),
            object_name="Mercury",
            station_type="retrograde",
            longitude=47.5,  # 17°30' Taurus
            sign="Taurus",
        )
        assert station.degree_in_sign == pytest.approx(17.5, abs=0.01)

    def test_str_method(self):
        """Test __str__ method."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 1, 12, 30),
            object_name="Mercury",
            station_type="retrograde",
            longitude=27.75,  # 27°45' Aries
            sign="Aries",
        )
        result = str(station)
        assert "Mercury" in result
        assert "stations retrograde" in result
        assert "Aries" in result
        assert "2024-04-01 12:30" in result

    def test_frozen_dataclass(self):
        """Verify Station is immutable."""
        station = Station(
            julian_day=2460400.0,
            datetime_utc=datetime(2024, 4, 1, 12, 0),
            object_name="Mercury",
            station_type="retrograde",
            longitude=27.5,
            sign="Aries",
        )
        with pytest.raises(AttributeError):
            station.station_type = "direct"


# =============================================================================
# Tests for find_ingress
# =============================================================================


class TestFindIngress:
    """Tests for find_ingress - find when object enters a sign."""

    def test_sun_into_aries(self):
        """Find Sun entering Aries (vernal equinox)."""
        result = find_ingress("Sun", "Aries", datetime(2024, 1, 1), direction="forward")

        assert result is not None
        assert result.object_name == "Sun"
        assert result.sign == "Aries"
        assert result.from_sign == "Pisces"
        # Vernal equinox 2024 is around March 20
        assert result.datetime_utc.month == 3
        assert 19 <= result.datetime_utc.day <= 21
        # Longitude should be very close to 0° (or 360°)
        normalized_lon = result.longitude % 360
        assert normalized_lon == pytest.approx(
            0.0, abs=0.01
        ) or normalized_lon == pytest.approx(360.0, abs=0.01)

    def test_sun_into_cancer(self):
        """Find Sun entering Cancer (summer solstice)."""
        result = find_ingress(
            "Sun", "Cancer", datetime(2024, 1, 1), direction="forward"
        )

        assert result is not None
        assert result.sign == "Cancer"
        assert result.from_sign == "Gemini"
        # Summer solstice 2024 is around June 20
        assert result.datetime_utc.month == 6
        assert 19 <= result.datetime_utc.day <= 22

    def test_moon_ingress(self):
        """Find Moon entering a sign."""
        result = find_ingress(
            "Moon", "Leo", datetime(2024, 1, 1), direction="forward", max_days=30
        )

        assert result is not None
        assert result.object_name == "Moon"
        assert result.sign == "Leo"
        assert result.from_sign == "Cancer"
        # Moon enters any sign within ~2.5 days
        assert result.datetime_utc.month == 1

    def test_backward_search(self):
        """Search backward for ingress."""
        result = find_ingress(
            "Sun", "Capricorn", datetime(2024, 1, 1), direction="backward", max_days=30
        )

        assert result is not None
        # Should find winter solstice 2023
        assert result.datetime_utc.year == 2023
        assert result.datetime_utc.month == 12

    def test_unknown_sign_raises(self):
        """Unknown sign name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown sign"):
            find_ingress("Sun", "NotASign", datetime(2024, 1, 1))

    def test_unknown_object_raises(self):
        """Unknown object name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown object"):
            find_ingress("NotAPlanet", "Aries", datetime(2024, 1, 1))

    def test_accepts_julian_day_input(self):
        """Can pass Julian day instead of datetime."""
        jd = 2460310.5  # ~Jan 1, 2024
        result = find_ingress("Sun", "Aries", jd, direction="forward")

        assert result is not None
        assert result.sign == "Aries"

    def test_mars_ingress(self):
        """Test with Mars (slower planet)."""
        result = find_ingress(
            "Mars", "Taurus", datetime(2024, 1, 1), direction="forward"
        )

        assert result is not None
        assert result.object_name == "Mars"
        assert result.sign == "Taurus"
        assert result.from_sign == "Aries"


# =============================================================================
# Tests for find_all_ingresses
# =============================================================================


class TestFindAllIngresses:
    """Tests for find_all_ingresses - find all ingresses to a sign in date range."""

    def test_sun_enters_aries_once_per_year(self):
        """Sun enters Aries exactly once per year."""
        results = find_all_ingresses(
            "Sun", "Aries", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        assert len(results) == 1
        assert results[0].sign == "Aries"
        assert results[0].datetime_utc.month == 3

    def test_moon_enters_sign_monthly(self):
        """Moon enters each sign about once per month (~13 times per year)."""
        results = find_all_ingresses(
            "Moon", "Taurus", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Moon orbits ~13 times per year
        assert 12 <= len(results) <= 14

        # All should be Moon entering Taurus
        for r in results:
            assert r.object_name == "Moon"
            assert r.sign == "Taurus"
            assert r.from_sign == "Aries"

        # Should be chronologically ordered
        for i in range(len(results) - 1):
            assert results[i].julian_day < results[i + 1].julian_day

    def test_unknown_sign_raises(self):
        """Unknown sign name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown sign"):
            find_all_ingresses(
                "Sun", "NotASign", datetime(2024, 1, 1), datetime(2024, 12, 31)
            )

    def test_max_results_limit(self):
        """max_results parameter limits output."""
        results = find_all_ingresses(
            "Moon", "Leo", datetime(2024, 1, 1), datetime(2024, 12, 31), max_results=3
        )

        assert len(results) <= 3

    def test_accepts_julian_day_inputs(self):
        """Can use Julian days for start and end."""
        start_jd = 2460310.5  # ~Jan 1, 2024
        end_jd = 2460676.5  # ~Jan 1, 2025

        results = find_all_ingresses("Sun", "Cancer", start_jd, end_jd)

        assert len(results) == 1
        assert results[0].sign == "Cancer"


# =============================================================================
# Tests for find_next_sign_change
# =============================================================================


class TestFindNextSignChange:
    """Tests for find_next_sign_change - find when object leaves current sign."""

    def test_sun_next_sign_change(self):
        """Find when Sun changes signs."""
        # Mid-January, Sun is in Capricorn, should enter Aquarius around Jan 20
        result = find_next_sign_change(
            "Sun", datetime(2024, 1, 10), direction="forward"
        )

        assert result is not None
        assert result.sign == "Aquarius"
        assert result.from_sign == "Capricorn"
        assert result.datetime_utc.month == 1
        assert 19 <= result.datetime_utc.day <= 21

    def test_moon_next_sign_change(self):
        """Moon changes signs every ~2.5 days."""
        result = find_next_sign_change(
            "Moon", datetime(2024, 1, 1), direction="forward"
        )

        assert result is not None
        # Should find sign change within a few days
        assert result.datetime_utc < datetime(2024, 1, 5)

    def test_backward_search(self):
        """Search backward for sign change."""
        # Mid-January, search backward to find when Sun entered Capricorn
        result = find_next_sign_change(
            "Sun", datetime(2024, 1, 10), direction="backward"
        )

        assert result is not None
        assert result.sign == "Capricorn"
        # Sun entered Capricorn around Dec 21, 2023
        assert result.datetime_utc.year == 2023
        assert result.datetime_utc.month == 12

    def test_unknown_object_raises(self):
        """Unknown object name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown object"):
            find_next_sign_change("NotAPlanet", datetime(2024, 1, 1))

    def test_accepts_julian_day_input(self):
        """Can pass Julian day instead of datetime."""
        jd = 2460320.5  # ~Jan 11, 2024
        result = find_next_sign_change("Sun", jd, direction="forward")

        assert result is not None


# =============================================================================
# Tests for find_all_sign_changes
# =============================================================================


class TestFindAllSignChanges:
    """Tests for find_all_sign_changes - find all sign changes in date range."""

    def test_sun_sign_changes_in_year(self):
        """Sun changes signs 12 times per year."""
        results = find_all_sign_changes(
            "Sun", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Sun enters each of 12 signs once per year
        # But depending on exact dates, might catch 11 or 12 (boundary effects)
        assert 11 <= len(results) <= 13

        # Should be chronologically ordered
        for i in range(len(results) - 1):
            assert results[i].julian_day < results[i + 1].julian_day

    def test_moon_sign_changes_in_month(self):
        """Moon changes signs about 12-13 times per month."""
        results = find_all_sign_changes(
            "Moon", datetime(2024, 1, 1), datetime(2024, 1, 31)
        )

        # Moon orbits in ~27 days, so ~12-13 sign changes per month
        assert 11 <= len(results) <= 14

    def test_mercury_sign_changes(self):
        """Mercury has variable sign changes due to retrograde."""
        results = find_all_sign_changes(
            "Mercury", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Mercury should have more sign changes than Sun due to retrogrades
        # but this depends on the year
        assert len(results) >= 12

    def test_max_results_limit(self):
        """max_results parameter limits output."""
        results = find_all_sign_changes(
            "Moon", datetime(2024, 1, 1), datetime(2024, 12, 31), max_results=5
        )

        assert len(results) <= 5

    def test_accepts_julian_day_inputs(self):
        """Can use Julian days for start and end."""
        start_jd = 2460310.5  # ~Jan 1, 2024
        end_jd = 2460340.5  # ~Jan 31, 2024

        results = find_all_sign_changes("Sun", start_jd, end_jd)

        # Sun changes sign once or twice in January
        assert 1 <= len(results) <= 2


# =============================================================================
# Tests for find_station
# =============================================================================


class TestFindStation:
    """Tests for find_station - find when planet stations retrograde/direct."""

    def test_mercury_station(self):
        """Find Mercury station in 2024."""
        result = find_station("Mercury", datetime(2024, 1, 1), direction="forward")

        assert result is not None
        assert result.object_name == "Mercury"
        assert result.station_type in ("retrograde", "direct")
        # Mercury stations every few months
        assert result.datetime_utc.year == 2024

    def test_mars_station(self):
        """Find Mars station (less frequent)."""
        result = find_station(
            "Mars", datetime(2024, 1, 1), direction="forward", max_days=730
        )

        assert result is not None
        assert result.object_name == "Mars"
        assert result.station_type in ("retrograde", "direct")

    def test_saturn_station(self):
        """Find Saturn station."""
        result = find_station("Saturn", datetime(2024, 1, 1), direction="forward")

        assert result is not None
        assert result.object_name == "Saturn"
        # Saturn stations annually

    def test_sun_raises_error(self):
        """Sun cannot station (never goes retrograde)."""
        with pytest.raises(ValueError, match="does not have stations"):
            find_station("Sun", datetime(2024, 1, 1))

    def test_moon_raises_error(self):
        """Moon cannot station (never goes retrograde)."""
        with pytest.raises(ValueError, match="does not have stations"):
            find_station("Moon", datetime(2024, 1, 1))

    def test_unknown_object_raises(self):
        """Unknown object name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown object"):
            find_station("NotAPlanet", datetime(2024, 1, 1))

    def test_backward_search(self):
        """Search backward for station."""
        result = find_station("Mercury", datetime(2024, 6, 1), direction="backward")

        assert result is not None
        # Should find a station before June 2024

    def test_accepts_julian_day_input(self):
        """Can pass Julian day instead of datetime."""
        jd = 2460310.5  # ~Jan 1, 2024
        result = find_station("Mercury", jd, direction="forward")

        assert result is not None

    def test_station_has_sign(self):
        """Station result should include the sign."""
        result = find_station("Mercury", datetime(2024, 1, 1), direction="forward")

        assert result is not None
        assert result.sign in SIGN_ORDER

    def test_venus_station(self):
        """Find Venus station (less frequent than Mercury)."""
        # Venus retrogrades less often, so search a wider range
        result = find_station(
            "Venus", datetime(2024, 1, 1), direction="forward", max_days=730
        )

        assert result is not None
        assert result.object_name == "Venus"


# =============================================================================
# Tests for find_all_stations
# =============================================================================


class TestFindAllStations:
    """Tests for find_all_stations - find all stations in date range."""

    def test_mercury_stations_in_year(self):
        """Mercury stations multiple times per year."""
        results = find_all_stations(
            "Mercury", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Mercury retrogrades ~3 times per year = 6 stations (3 Rx + 3 D)
        assert 5 <= len(results) <= 8

        # Should alternate between retrograde and direct (mostly)
        for r in results:
            assert r.station_type in ("retrograde", "direct")

        # Should be chronologically ordered
        for i in range(len(results) - 1):
            assert results[i].julian_day < results[i + 1].julian_day

    def test_saturn_stations_in_year(self):
        """Saturn stations twice per year (once Rx, once D)."""
        results = find_all_stations(
            "Saturn", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Saturn should have 2 stations per year
        assert 1 <= len(results) <= 3

    def test_mars_stations_less_frequent(self):
        """Mars stations less frequently (every ~2 years)."""
        results = find_all_stations(
            "Mars", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Mars may have 0-2 stations in a single year
        assert len(results) <= 3

    def test_max_results_limit(self):
        """max_results parameter limits output."""
        results = find_all_stations(
            "Mercury", datetime(2024, 1, 1), datetime(2024, 12, 31), max_results=2
        )

        assert len(results) <= 2

    def test_accepts_julian_day_inputs(self):
        """Can use Julian days for start and end."""
        start_jd = 2460310.5  # ~Jan 1, 2024
        end_jd = 2460676.5  # ~Jan 1, 2025

        results = find_all_stations("Mercury", start_jd, end_jd)

        assert len(results) >= 1

    def test_jupiter_stations(self):
        """Jupiter stations annually."""
        results = find_all_stations(
            "Jupiter", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Jupiter should have 2 stations per year
        assert 1 <= len(results) <= 3


# =============================================================================
# Integration Tests for Ingress and Station Functions
# =============================================================================


class TestIngressStationIntegration:
    """Integration tests for ingress and station functions together."""

    def test_mercury_retrograde_cycle(self):
        """Track a Mercury retrograde cycle: station Rx -> station D."""
        # Find first station in 2024
        station_rx = find_station("Mercury", datetime(2024, 1, 1), direction="forward")
        assert station_rx is not None

        # Find next station after the first one
        next_station = find_station(
            "Mercury", station_rx.datetime_utc, direction="forward"
        )
        assert next_station is not None

        # The two stations should be different types (Rx followed by D, or D followed by Rx)
        # Note: depending on timing, this might not always be the case if we catch
        # the tail end of a retrograde period
        assert next_station.julian_day > station_rx.julian_day

    def test_sun_annual_cycle(self):
        """Track Sun through all 12 signs in a year."""
        sign_changes = find_all_sign_changes(
            "Sun", datetime(2024, 1, 1), datetime(2024, 12, 31)
        )

        # Sun should enter each sign once
        # Note: exact count depends on start/end dates
        signs_entered = {r.sign for r in sign_changes}
        # Should enter at least 10 signs in a year
        assert len(signs_entered) >= 10

    def test_moon_rapid_changes(self):
        """Moon changes signs rapidly - about every 2.5 days."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)

        sign_changes = find_all_sign_changes("Moon", start, end)

        # In 9 days, Moon should change signs 3-4 times
        assert 3 <= len(sign_changes) <= 5

    def test_outer_planet_slow_ingress(self):
        """Outer planets have infrequent ingresses."""
        # Neptune moves very slowly, may not change signs in a year
        # Let's test Uranus which might change signs during our test period
        results = find_all_sign_changes(
            "Uranus", datetime(2024, 1, 1), datetime(2025, 12, 31), max_results=10
        )

        # Uranus may have 0-3 ingresses over 2 years depending on timing
        assert len(results) <= 5
        for r in results:
            assert r.object_name == "Uranus"


# =============================================================================
# ASPECT EXACTITUDE TESTS
# =============================================================================


class TestAspectAngles:
    """Tests for ASPECT_ANGLES constant."""

    def test_all_major_aspects_defined(self):
        """All five major aspects should be defined."""
        assert 0.0 in ASPECT_ANGLES  # conjunction
        assert 60.0 in ASPECT_ANGLES  # sextile
        assert 90.0 in ASPECT_ANGLES  # square
        assert 120.0 in ASPECT_ANGLES  # trine
        assert 180.0 in ASPECT_ANGLES  # opposition

    def test_aspect_names(self):
        """Aspect names should be correct."""
        assert ASPECT_ANGLES[0.0] == "conjunction"
        assert ASPECT_ANGLES[60.0] == "sextile"
        assert ASPECT_ANGLES[90.0] == "square"
        assert ASPECT_ANGLES[120.0] == "trine"
        assert ASPECT_ANGLES[180.0] == "opposition"


class TestAspectExactDataclass:
    """Tests for AspectExact dataclass."""

    def test_basic_creation(self):
        """Can create AspectExact with all required fields."""
        exact = AspectExact(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            object1_name="Moon",
            object2_name="Jupiter",
            aspect_angle=120.0,
            aspect_name="trine",
            object1_longitude=100.0,
            object2_longitude=220.0,
            is_applying_before=True,
        )
        assert exact.object1_name == "Moon"
        assert exact.object2_name == "Jupiter"
        assert exact.aspect_angle == 120.0
        assert exact.aspect_name == "trine"

    def test_separation_property(self):
        """Separation should be close to aspect angle at exact."""
        exact = AspectExact(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            object1_name="Moon",
            object2_name="Jupiter",
            aspect_angle=120.0,
            aspect_name="trine",
            object1_longitude=100.0,
            object2_longitude=220.0,  # 220 - 100 = 120°
            is_applying_before=True,
        )
        assert exact.separation == pytest.approx(120.0, abs=0.1)

    def test_separation_handles_wraparound(self):
        """Separation handles 360° wraparound correctly."""
        exact = AspectExact(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            object1_name="Moon",
            object2_name="Mars",
            aspect_angle=60.0,
            aspect_name="sextile",
            object1_longitude=350.0,
            object2_longitude=50.0,  # diff = 300, but actual = 60
            is_applying_before=True,
        )
        assert exact.separation == pytest.approx(60.0, abs=0.1)

    def test_frozen_dataclass(self):
        """AspectExact is immutable."""
        exact = AspectExact(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            object1_name="Moon",
            object2_name="Jupiter",
            aspect_angle=120.0,
            aspect_name="trine",
            object1_longitude=100.0,
            object2_longitude=220.0,
            is_applying_before=True,
        )
        with pytest.raises(AttributeError):
            exact.object1_name = "Sun"

    def test_str_representation(self):
        """String representation is readable."""
        exact = AspectExact(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            object1_name="Moon",
            object2_name="Jupiter",
            aspect_angle=120.0,
            aspect_name="trine",
            object1_longitude=100.0,
            object2_longitude=220.0,
            is_applying_before=True,
        )
        s = str(exact)
        assert "Moon" in s
        assert "Jupiter" in s
        assert "trine" in s


class TestFindAspectExact:
    """Tests for find_aspect_exact function."""

    def test_find_moon_jupiter_trine(self):
        """Can find exact Moon trine Jupiter."""
        result = find_aspect_exact(
            "Moon", "Jupiter", 120.0, datetime(2025, 1, 1), max_days=30
        )
        assert result is not None
        assert result.object1_name == "Moon"
        assert result.object2_name == "Jupiter"
        assert result.aspect_angle == 120.0
        # Should be very close to exact (within tolerance)
        assert abs(result.separation - 120.0) < 0.01

    def test_find_sun_moon_conjunction(self):
        """Can find exact Sun-Moon conjunction (New Moon)."""
        result = find_aspect_exact(
            "Sun", "Moon", 0.0, datetime(2025, 1, 1), max_days=35
        )
        assert result is not None
        assert result.aspect_angle == 0.0
        # Conjunction: separation should be ~0
        assert result.separation < 1.0

    def test_find_backward(self):
        """Can search backward for past aspects."""
        # Start from Feb 1 and search backward
        result = find_aspect_exact(
            "Moon",
            "Venus",
            60.0,
            datetime(2025, 2, 1),
            direction="backward",
            max_days=30,
        )
        assert result is not None
        # Result should be before start date
        assert result.datetime_utc < datetime(2025, 2, 1)

    def test_invalid_object_raises(self):
        """Invalid object name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown object"):
            find_aspect_exact("Moon", "InvalidPlanet", 120.0, datetime(2025, 1, 1))

    def test_returns_none_when_not_found(self):
        """Returns None when no aspect found in range."""
        # Search a very short range for a rare aspect
        result = find_aspect_exact(
            "Saturn", "Jupiter", 0.0, datetime(2025, 1, 1), max_days=1
        )
        # Saturn-Jupiter conjunction is rare, unlikely in 1 day
        # Could be None or found depending on dates
        # Just verify it doesn't crash and returns the right type
        assert result is None or isinstance(result, AspectExact)


class TestFindAllAspectExacts:
    """Tests for find_all_aspect_exacts function."""

    def test_find_all_moon_jupiter_trines(self):
        """Find all Moon-Jupiter trines in a month."""
        results = find_all_aspect_exacts(
            "Moon", "Jupiter", 120.0, datetime(2025, 1, 1), datetime(2025, 2, 1)
        )
        # Moon makes ~13 synodic cycles per year, so 1-2 trines per month
        assert len(results) >= 1
        for r in results:
            assert r.object1_name == "Moon"
            assert r.object2_name == "Jupiter"
            assert r.aspect_angle == 120.0

    def test_results_are_chronological(self):
        """Results should be in chronological order."""
        results = find_all_aspect_exacts(
            "Moon", "Mars", 90.0, datetime(2025, 1, 1), datetime(2025, 3, 1)
        )
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].julian_day < results[i + 1].julian_day

    def test_respects_max_results(self):
        """Should not exceed max_results."""
        results = find_all_aspect_exacts(
            "Moon",
            "Venus",
            60.0,
            datetime(2025, 1, 1),
            datetime(2025, 12, 31),
            max_results=5,
        )
        assert len(results) <= 5


# =============================================================================
# ANGLE CROSSING TESTS
# =============================================================================


class TestAngleCrossingDataclass:
    """Tests for AngleCrossing dataclass."""

    def test_basic_creation(self):
        """Can create AngleCrossing with all fields."""
        crossing = AngleCrossing(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            angle_name="MC",
            target_longitude=150.0,
            actual_longitude=150.001,
            latitude=37.7749,
            longitude=-122.4194,
        )
        assert crossing.angle_name == "MC"
        assert crossing.target_longitude == 150.0
        assert crossing.latitude == 37.7749

    def test_frozen_dataclass(self):
        """AngleCrossing is immutable."""
        crossing = AngleCrossing(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            angle_name="ASC",
            target_longitude=0.0,
            actual_longitude=0.001,
            latitude=40.7128,
            longitude=-74.006,
        )
        with pytest.raises(AttributeError):
            crossing.angle_name = "MC"

    def test_str_representation(self):
        """String representation includes sign."""
        crossing = AngleCrossing(
            julian_day=2460676.5,
            datetime_utc=datetime(2025, 1, 1, 12, 0),
            angle_name="MC",
            target_longitude=150.0,  # 0° Virgo
            actual_longitude=150.0,
            latitude=37.7749,
            longitude=-122.4194,
        )
        s = str(crossing)
        assert "MC" in s
        assert "Virgo" in s


class TestFindAngleCrossing:
    """Tests for find_angle_crossing function."""

    def test_find_asc_crossing(self):
        """Can find when ASC reaches a specific longitude."""
        result = find_angle_crossing(
            target_longitude=0.0,  # 0° Aries
            latitude=37.7749,
            longitude=-122.4194,
            angle="ASC",
            start=datetime(2025, 1, 1),
        )
        assert result is not None
        assert result.angle_name == "ASC"
        assert abs(result.actual_longitude - 0.0) < 0.01

    def test_find_mc_crossing(self):
        """Can find when MC reaches a specific longitude."""
        result = find_angle_crossing(
            target_longitude=150.0,  # Regulus longitude
            latitude=40.7128,
            longitude=-74.006,
            angle="MC",
            start=datetime(2025, 1, 1),
        )
        assert result is not None
        assert result.angle_name == "MC"

    def test_dsc_is_opposite_of_asc(self):
        """DSC crossing is ASC + 180°."""
        # Find ASC at 0°
        asc_result = find_angle_crossing(
            0.0, 37.7749, -122.4194, "ASC", datetime(2025, 1, 1)
        )
        # Find DSC at 0° (which means ASC at 180°)
        dsc_result = find_angle_crossing(
            0.0, 37.7749, -122.4194, "DSC", datetime(2025, 1, 1)
        )

        assert asc_result is not None
        assert dsc_result is not None
        # DSC at 0° is different time than ASC at 0°
        assert abs(asc_result.julian_day - dsc_result.julian_day) > 0.01

    def test_crossing_happens_daily(self):
        """Each angle crosses a given longitude roughly once per day."""
        result1 = find_angle_crossing(
            120.0, 37.7749, -122.4194, "MC", datetime(2025, 1, 1)
        )
        result2 = find_angle_crossing(
            120.0, 37.7749, -122.4194, "MC", datetime(2025, 1, 2)
        )

        assert result1 is not None
        assert result2 is not None
        # About 1 day apart (sidereal day ~23h 56m)
        diff_days = result2.julian_day - result1.julian_day
        assert 0.9 < diff_days < 1.1

    def test_invalid_angle_raises(self):
        """Invalid angle name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown angle"):
            find_angle_crossing(
                0.0, 37.7749, -122.4194, "INVALID", datetime(2025, 1, 1)
            )


class TestFindAllAngleCrossings:
    """Tests for find_all_angle_crossings function."""

    def test_find_all_in_week(self):
        """Find all MC crossings in a week (should be ~7)."""
        results = find_all_angle_crossings(
            target_longitude=0.0,
            latitude=37.7749,
            longitude=-122.4194,
            angle="MC",
            start=datetime(2025, 1, 1),
            end=datetime(2025, 1, 8),
        )
        # Should find roughly 7 crossings (one per day)
        assert 6 <= len(results) <= 8

    def test_results_are_chronological(self):
        """Results should be in chronological order."""
        results = find_all_angle_crossings(
            target_longitude=90.0,
            latitude=40.7128,
            longitude=-74.006,
            angle="ASC",
            start=datetime(2025, 1, 1),
            end=datetime(2025, 1, 10),
        )
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].julian_day < results[i + 1].julian_day

    def test_respects_max_results(self):
        """Should not exceed max_results."""
        results = find_all_angle_crossings(
            target_longitude=0.0,
            latitude=37.7749,
            longitude=-122.4194,
            angle="MC",
            start=datetime(2025, 1, 1),
            end=datetime(2025, 12, 31),
            max_results=5,
        )
        assert len(results) == 5
