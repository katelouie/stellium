"""Tests for primary directions calculations.

This module tests the directions engine including:
- Spherical math functions (ascensional difference, semi-arcs, oblique ascension)
- Time keys (Ptolemy, Naibod)
- Direction methods (Zodiacal, Mundane)
- DirectionsEngine API
- DistributionsCalculator

References for validation:
- https://morinus-astrology.com/placidus-direction/ (Churchill example)
- https://sevenstarsastrology.com/astrological-predictive-techniques-primary-directions-2-software-calculation/
- http://flatangle.com/blog/2014/primary-directions-simple/
"""

import datetime as dt

import pytest

from stellium import ChartBuilder
from stellium.engines.directions import (
    DirectionArc,
    DirectionResult,
    DirectionsEngine,
    DistributionsCalculator,
    EquatorialPoint,
    MundaneDirections,
    MundanePosition,
    NaibodKey,
    PtolemyKey,
    TimeLordPeriod,
    ZodiacalDirections,
    ascensional_difference,
    ecliptic_to_equatorial,
    get_obliquity,
    meridian_distance,
    oblique_ascension,
    semi_arcs,
)

# =============================================================================
# SECTION 1: SPHERICAL MATH FUNCTION TESTS
# =============================================================================


class TestAscensionalDifference:
    """Test ascensional difference calculations.

    Formula: sin(AD) = tan(dec) * tan(pole)
    """

    def test_zero_declination_gives_zero_ad(self):
        """A point on the equator (dec=0) has no ascensional difference."""
        ad = ascensional_difference(declination=0.0, pole=45.0)
        assert ad == pytest.approx(0.0, abs=0.001)

    def test_zero_latitude_gives_zero_ad(self):
        """At the equator (pole=0), there's no tilt effect."""
        ad = ascensional_difference(declination=23.44, pole=0.0)
        assert ad == pytest.approx(0.0, abs=0.001)

    def test_positive_declination_positive_latitude(self):
        """Northern declination at northern latitude increases day arc."""
        # At 51° latitude, Sun at summer solstice (dec ~23.44°)
        ad = ascensional_difference(declination=23.44, pole=51.0)
        # AD should be positive and significant
        assert ad > 25.0  # Roughly ~31° for London at solstice
        assert ad < 40.0

    def test_negative_declination_positive_latitude(self):
        """Southern declination at northern latitude decreases day arc."""
        # At 51° latitude, Sun at winter solstice (dec ~-23.44°)
        ad = ascensional_difference(declination=-23.44, pole=51.0)
        # AD should be negative
        assert ad < -25.0
        assert ad > -40.0

    def test_symmetric_with_sign_change(self):
        """AD is antisymmetric: changing sign of dec or pole negates result."""
        ad_pos = ascensional_difference(declination=20.0, pole=45.0)
        ad_neg_dec = ascensional_difference(declination=-20.0, pole=45.0)
        ad_neg_pole = ascensional_difference(declination=20.0, pole=-45.0)

        assert ad_neg_dec == pytest.approx(-ad_pos, abs=0.001)
        assert ad_neg_pole == pytest.approx(-ad_pos, abs=0.001)

    def test_clamping_extreme_values(self):
        """Extreme values should be clamped to prevent math errors."""
        # This would cause tan overflow without clamping
        ad = ascensional_difference(declination=80.0, pole=80.0)
        # Should return a valid number, not crash
        assert -90 <= ad <= 90


class TestSemiArcs:
    """Test diurnal and nocturnal semi-arc calculations."""

    def test_equator_gives_equal_arcs(self):
        """At equator with 0 dec, both semi-arcs are 90°."""
        dsa, nsa = semi_arcs(declination=0.0, latitude=0.0)
        assert dsa == pytest.approx(90.0, abs=0.01)
        assert nsa == pytest.approx(90.0, abs=0.01)

    def test_arcs_sum_to_180(self):
        """Diurnal + nocturnal semi-arc always equals 180°."""
        test_cases = [
            (0.0, 45.0),
            (23.44, 51.0),
            (-23.44, 51.0),
            (15.0, 30.0),
            (-10.0, 60.0),
        ]
        for dec, lat in test_cases:
            dsa, nsa = semi_arcs(dec, lat)
            assert dsa + nsa == pytest.approx(180.0, abs=0.01)

    def test_northern_summer_longer_days(self):
        """Positive declination at positive latitude = longer day arc."""
        dsa, nsa = semi_arcs(declination=23.44, latitude=51.0)
        assert dsa > 90.0  # Day arc longer than 6 hours
        assert nsa < 90.0  # Night arc shorter

    def test_northern_winter_shorter_days(self):
        """Negative declination at positive latitude = shorter day arc."""
        dsa, nsa = semi_arcs(declination=-23.44, latitude=51.0)
        assert dsa < 90.0  # Day arc shorter than 6 hours
        assert nsa > 90.0  # Night arc longer


class TestMeridianDistance:
    """Test meridian distance calculations."""

    def test_same_ra_gives_zero_md(self):
        """When RA equals RAMC, meridian distance is 0."""
        md = meridian_distance(right_ascension=120.0, ramc=120.0)
        assert md == pytest.approx(0.0, abs=0.001)

    def test_ra_east_of_mc_positive(self):
        """RA greater than RAMC (east) gives positive MD."""
        md = meridian_distance(right_ascension=150.0, ramc=120.0)
        assert md == pytest.approx(30.0, abs=0.001)

    def test_ra_west_of_mc_negative(self):
        """RA less than RAMC (west) gives negative MD."""
        md = meridian_distance(right_ascension=90.0, ramc=120.0)
        assert md == pytest.approx(-30.0, abs=0.001)

    def test_wraparound_east(self):
        """Handle wraparound when RA is near 360 and RAMC near 0."""
        md = meridian_distance(right_ascension=350.0, ramc=10.0)
        assert md == pytest.approx(-20.0, abs=0.001)

    def test_wraparound_west(self):
        """Handle wraparound when RA is near 0 and RAMC near 360."""
        md = meridian_distance(right_ascension=10.0, ramc=350.0)
        assert md == pytest.approx(20.0, abs=0.001)

    def test_normalize_to_180_range(self):
        """Result is always in -180 to +180 range."""
        # Even with large differences
        md = meridian_distance(right_ascension=0.0, ramc=200.0)
        assert -180 <= md <= 180


class TestObliqueAscension:
    """Test oblique ascension calculations."""

    def test_zero_pole_equals_ra(self):
        """At equator (pole=0), OA equals RA."""
        oa = oblique_ascension(right_ascension=120.0, declination=15.0, pole=0.0)
        assert oa == pytest.approx(120.0, abs=0.01)

    def test_zero_declination_equals_ra(self):
        """For equatorial points (dec=0), OA equals RA."""
        oa = oblique_ascension(right_ascension=120.0, declination=0.0, pole=51.0)
        assert oa == pytest.approx(120.0, abs=0.01)

    def test_oa_normalized_to_360(self):
        """Result is always in 0-360 range."""
        oa = oblique_ascension(right_ascension=10.0, declination=20.0, pole=60.0)
        assert 0 <= oa < 360


class TestEclipticToEquatorial:
    """Tests for ecliptic to equatorial coordinate conversion."""

    def test_vernal_equinox(self):
        """0° Aries should have RA=0, Dec=0."""
        ra, dec = ecliptic_to_equatorial(0.0, 0.0, 23.44)
        assert ra == pytest.approx(0.0, abs=0.01)
        assert dec == pytest.approx(0.0, abs=0.01)

    def test_summer_solstice(self):
        """0° Cancer should have RA=90, Dec=+obliquity."""
        obliquity = 23.44
        ra, dec = ecliptic_to_equatorial(90.0, 0.0, obliquity)
        assert ra == pytest.approx(90.0, abs=0.01)
        assert dec == pytest.approx(obliquity, abs=0.01)

    def test_autumnal_equinox(self):
        """0° Libra should have RA=180, dec=0."""
        ra, dec = ecliptic_to_equatorial(180.0, 0.0, 23.44)
        assert ra == pytest.approx(180.0, abs=0.01)
        assert dec == pytest.approx(0.0, abs=0.01)

    def test_winter_solstice(self):
        """0° Capricorn should have RA=270, Dec=-obliquity."""
        obliquity = 23.44
        ra, dec = ecliptic_to_equatorial(270.0, 0.0, obliquity)
        assert ra == pytest.approx(270.0, abs=0.01)
        assert dec == pytest.approx(-obliquity, abs=0.01)


# =============================================================================
# SECTION 2: TIME KEY TESTS
# =============================================================================


class TestPtolemyKey:
    """Test Ptolemy's time key: 1° = 1 year."""

    def test_arc_to_years_direct(self):
        """1 degree = 1 year exactly."""
        key = PtolemyKey()
        assert key.arc_to_years(1.0) == pytest.approx(1.0, abs=0.001)
        assert key.arc_to_years(30.0) == pytest.approx(30.0, abs=0.001)
        assert key.arc_to_years(45.5) == pytest.approx(45.5, abs=0.001)

    def test_arc_to_date(self):
        """Arc of 30° from birth = birth + 30 years."""
        key = PtolemyKey()
        birth = dt.datetime(2000, 1, 1, 12, 0)
        result = key.arc_to_date(30.0, birth)

        # Should be approximately 30 years later
        diff_years = (result - birth).days / 365.25
        assert diff_years == pytest.approx(30.0, abs=0.01)

    def test_key_name(self):
        """Key name property."""
        key = PtolemyKey()
        assert key.key_name == "Ptolemy"


class TestNaibodKey:
    """Test Naibod's time key: ~1.0146° per year."""

    def test_arc_to_years_conversion(self):
        """Naibod: 1° ≈ 1.0146 years."""
        key = NaibodKey()
        years = key.arc_to_years(1.0)
        # Naibod factor is approximately 1.0146
        assert years == pytest.approx(1.0146, abs=0.01)

    def test_arc_to_date_churchill_example(self):
        """Validate against Churchill's known direction.

        From https://morinus-astrology.com/placidus-direction/:
        Arc of 24°25' = 24.78 years using Naibod key.
        """
        key = NaibodKey()
        arc_degrees = 24.0 + 25.0 / 60.0  # 24°25'

        years = key.arc_to_years(arc_degrees)
        # Should be approximately 24.78 years
        assert years == pytest.approx(24.78, abs=0.5)

    def test_naibod_slower_than_ptolemy(self):
        """Same arc gives more years with Naibod than Ptolemy."""
        ptolemy = PtolemyKey()
        naibod = NaibodKey()

        arc = 30.0
        assert naibod.arc_to_years(arc) > ptolemy.arc_to_years(arc)

    def test_key_name(self):
        """Key name property."""
        key = NaibodKey()
        assert key.key_name == "Naibod"


# =============================================================================
# SECTION 3: DATA MODEL TESTS
# =============================================================================


class TestEquatorialPoint:
    """Test EquatorialPoint dataclass."""

    def test_creation(self):
        """Basic creation and attribute access."""
        point = EquatorialPoint("Sun", right_ascension=120.5, declination=-15.3)
        assert point.name == "Sun"
        assert point.right_ascension == 120.5
        assert point.declination == -15.3

    def test_frozen(self):
        """Dataclass is immutable."""
        point = EquatorialPoint("Sun", 120.5, -15.3)
        with pytest.raises(Exception) as _e:  # FrozenInstanceError
            point.name = "Moon"


class TestMundanePosition:
    """Test MundanePosition dataclass."""

    def test_current_semi_arc_above_horizon(self):
        """Above horizon uses diurnal semi-arc."""
        pos = MundanePosition(
            point=EquatorialPoint("Sun", 120.0, 15.0),
            meridian_distance=30.0,
            semi_arc_diurnal=100.0,
            semi_arc_nocturnal=80.0,
            is_above_horizon=True,
            is_eastern=True,
        )
        assert pos.current_semi_arc == 100.0

    def test_current_semi_arc_below_horizon(self):
        """Below horizon uses nocturnal semi-arc."""
        pos = MundanePosition(
            point=EquatorialPoint("Sun", 120.0, 15.0),
            meridian_distance=100.0,
            semi_arc_diurnal=100.0,
            semi_arc_nocturnal=80.0,
            is_above_horizon=False,
            is_eastern=True,
        )
        assert pos.current_semi_arc == 80.0

    def test_mundane_ratio_at_meridian(self):
        """At meridian (MD=0), ratio is 0."""
        pos = MundanePosition(
            point=EquatorialPoint("Test", 0, 0),
            meridian_distance=0.0,
            semi_arc_diurnal=90.0,
            semi_arc_nocturnal=90.0,
            is_above_horizon=True,
            is_eastern=True,
        )
        assert pos.mundane_ratio == pytest.approx(0.0, abs=0.001)

    def test_mundane_ratio_at_horizon(self):
        """At horizon (MD=SA), ratio is 1."""
        pos = MundanePosition(
            point=EquatorialPoint("Test", 0, 0),
            meridian_distance=90.0,
            semi_arc_diurnal=90.0,
            semi_arc_nocturnal=90.0,
            is_above_horizon=True,
            is_eastern=True,
        )
        assert pos.mundane_ratio == pytest.approx(1.0, abs=0.001)


class TestDirectionResult:
    """Test DirectionResult dataclass."""

    def test_creation_with_all_fields(self):
        """Create with arc, date, and age."""
        arc = DirectionArc("Sun", "ASC", 30.5, "zodiacal", "direct")
        result = DirectionResult(
            arc=arc,
            date=dt.datetime(2030, 6, 15),
            age=30.5,
        )
        assert result.arc.promissor == "Sun"
        assert result.arc.significator == "ASC"
        assert result.age == 30.5

    def test_optional_fields(self):
        """Date and age can be None."""
        arc = DirectionArc("Sun", "ASC", 30.5, "zodiacal")
        result = DirectionResult(arc=arc)
        assert result.date is None
        assert result.age is None


# =============================================================================
# SECTION 4: DIRECTION METHOD TESTS
# =============================================================================


class TestZodiacalDirections:
    """Test zodiacal (2D) direction method."""

    def test_method_name(self):
        """Method name property."""
        method = ZodiacalDirections()
        assert method.method_name == "zodiacal"

    def test_same_point_zero_arc(self):
        """Directing a point to itself gives 0 arc."""
        method = ZodiacalDirections()
        point = EquatorialPoint("Test", 120.0, 15.0)

        arc = method.calculate_arc(
            promissor=point,
            significator=point,
            latitude=51.0,
            ramc=100.0,
        )
        assert arc == pytest.approx(0.0, abs=0.01)

    def test_arc_calculation(self):
        """Basic arc calculation produces reasonable result."""
        method = ZodiacalDirections()

        promissor = EquatorialPoint("Sun", 230.0, -18.0)
        significator = EquatorialPoint("ASC", 128.0, 15.0)

        arc = method.calculate_arc(
            promissor=promissor,
            significator=significator,
            latitude=51.5,
            ramc=12.0,
        )

        # Arc should be positive and within valid range
        assert 0 <= arc < 360


class TestMundaneDirections:
    """Test mundane (3D/Placidus) direction method."""

    def test_method_name(self):
        """Method name property."""
        method = MundaneDirections()
        assert method.method_name == "mundane"

    def test_to_mundane_conversion(self):
        """Test internal conversion to MundanePosition."""
        method = MundaneDirections()
        point = EquatorialPoint("Sun", 120.0, 15.0)

        pos = method._to_mundane(point, latitude=51.0, ramc=100.0)

        assert pos.point == point
        assert pos.semi_arc_diurnal + pos.semi_arc_nocturnal == pytest.approx(
            180.0, abs=0.01
        )


# =============================================================================
# SECTION 5: DIRECTIONS ENGINE TESTS
# =============================================================================


class TestDirectionsEngine:
    """Test the main DirectionsEngine API."""

    @pytest.fixture
    def prince_charles_chart(self):
        """Prince Charles chart for testing."""
        birth = dt.datetime(1948, 11, 14, 21, 14)
        return ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

    def test_engine_creation_default(self, prince_charles_chart):
        """Create engine with default settings."""
        engine = DirectionsEngine(prince_charles_chart)
        assert engine._method.method_name == "zodiacal"
        assert engine._time_key.key_name == "Naibod"

    def test_engine_creation_mundane(self, prince_charles_chart):
        """Create engine with mundane method."""
        engine = DirectionsEngine(prince_charles_chart, method="mundane")
        assert engine._method.method_name == "mundane"

    def test_engine_creation_ptolemy(self, prince_charles_chart):
        """Create engine with Ptolemy key."""
        engine = DirectionsEngine(prince_charles_chart, time_key="ptolemy")
        assert engine._time_key.key_name == "Ptolemy"

    def test_direct_returns_result(self, prince_charles_chart):
        """direct() returns a DirectionResult."""
        engine = DirectionsEngine(prince_charles_chart)
        result = engine.direct("Sun", "ASC")

        assert isinstance(result, DirectionResult)
        assert result.arc.promissor == "Sun"
        assert result.arc.significator == "ASC"
        assert result.age is not None
        assert result.date is not None

    def test_direct_invalid_promissor(self, prince_charles_chart):
        """Raises error for unknown promissor."""
        engine = DirectionsEngine(prince_charles_chart)
        with pytest.raises(ValueError, match="not found"):
            engine.direct("NotAPlanet", "ASC")

    def test_direct_invalid_significator(self, prince_charles_chart):
        """Raises error for unknown significator."""
        engine = DirectionsEngine(prince_charles_chart)
        with pytest.raises(ValueError, match="not found"):
            engine.direct("Sun", "NotAnAngle")

    def test_direct_to_angles(self, prince_charles_chart):
        """direct_to_angles returns dict with all 4 angles."""
        engine = DirectionsEngine(prince_charles_chart)
        results = engine.direct_to_angles("Sun")

        assert isinstance(results, dict)
        assert "ASC" in results
        assert "MC" in results
        assert "DSC" in results
        assert "IC" in results
        assert all(isinstance(r, DirectionResult) for r in results.values())

    def test_direct_all_to(self, prince_charles_chart):
        """direct_all_to returns sorted list of results."""
        engine = DirectionsEngine(prince_charles_chart)
        results = engine.direct_all_to("ASC")

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, DirectionResult) for r in results)

        # Should be sorted by age
        ages = [r.age for r in results if r.age is not None]
        assert ages == sorted(ages)

    def test_compare_methods_different_results(self, prince_charles_chart):
        """Zodiacal and mundane methods can give different arcs."""
        z_engine = DirectionsEngine(prince_charles_chart, method="zodiacal")
        m_engine = DirectionsEngine(prince_charles_chart, method="mundane")

        z_result = z_engine.direct("Sun", "ASC")
        m_result = m_engine.direct("Sun", "ASC")

        # Both should produce valid results
        assert z_result.arc.arc_degrees > 0
        assert m_result.arc.arc_degrees > 0

        # Method names should differ
        assert z_result.arc.method == "zodiacal"
        assert m_result.arc.method == "mundane"

    def test_compare_time_keys_different_ages(self, prince_charles_chart):
        """Ptolemy and Naibod keys give different ages for same arc."""
        p_engine = DirectionsEngine(prince_charles_chart, time_key="ptolemy")
        n_engine = DirectionsEngine(prince_charles_chart, time_key="naibod")

        p_result = p_engine.direct("Mars", "ASC")
        n_result = n_engine.direct("Mars", "ASC")

        # Same arc
        assert p_result.arc.arc_degrees == pytest.approx(
            n_result.arc.arc_degrees, abs=0.01
        )

        # Different ages (Naibod slower, so more years)
        assert n_result.age > p_result.age


# =============================================================================
# SECTION 6: DISTRIBUTIONS CALCULATOR TESTS
# =============================================================================


class TestDistributionsCalculator:
    """Test term/bound distributions calculations."""

    @pytest.fixture
    def prince_charles_chart(self):
        """Prince Charles chart for testing."""
        birth = dt.datetime(1948, 11, 14, 21, 14)
        return ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

    def test_calculator_creation(self, prince_charles_chart):
        """Create calculator successfully."""
        calc = DistributionsCalculator(prince_charles_chart)
        assert calc._time_key.key_name == "Naibod"
        assert calc._bound_system == "egypt"

    def test_calculate_returns_periods(self, prince_charles_chart):
        """calculate() returns list of TimeLordPeriod."""
        calc = DistributionsCalculator(prince_charles_chart)
        periods = calc.calculate(years=50)

        assert isinstance(periods, list)
        assert len(periods) > 0
        assert all(isinstance(p, TimeLordPeriod) for p in periods)

    def test_first_period_is_birth(self, prince_charles_chart):
        """First period starts at birth (age 0)."""
        calc = DistributionsCalculator(prince_charles_chart)
        periods = calc.calculate(years=50)

        assert periods[0].start_age == 0.0

    def test_periods_sorted_by_age(self, prince_charles_chart):
        """Periods are in chronological order."""
        calc = DistributionsCalculator(prince_charles_chart)
        periods = calc.calculate(years=80)

        ages = [p.start_age for p in periods]
        assert ages == sorted(ages)

    def test_periods_have_valid_rulers(self, prince_charles_chart):
        """All periods have valid planetary rulers."""
        valid_rulers = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
        calc = DistributionsCalculator(prince_charles_chart)
        periods = calc.calculate(years=50)

        for period in periods:
            assert period.ruler in valid_rulers

    def test_periods_have_signs(self, prince_charles_chart):
        """Periods include sign information."""
        calc = DistributionsCalculator(prince_charles_chart)
        periods = calc.calculate(years=50)

        # At least some periods should have sign info
        signs_present = any(p.sign for p in periods)
        assert signs_present

    def test_years_limit_respected(self, prince_charles_chart):
        """No period starts after the year limit."""
        calc = DistributionsCalculator(prince_charles_chart)
        years_limit = 30
        periods = calc.calculate(years=years_limit)

        for period in periods:
            assert period.start_age <= years_limit

    def test_ptolemy_key_option(self, prince_charles_chart):
        """Can use Ptolemy time key for distributions."""
        calc = DistributionsCalculator(prince_charles_chart, time_key="ptolemy")
        periods = calc.calculate(years=50)

        assert len(periods) > 0


# =============================================================================
# SECTION 7: INTEGRATION TESTS
# =============================================================================


class TestDirectionsIntegration:
    """Integration tests using real chart data."""

    def test_full_workflow_prince_charles(self):
        """Complete workflow with Prince Charles chart."""
        # Create chart
        birth = dt.datetime(1948, 11, 14, 21, 14)
        chart = ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

        # Create engine
        engine = DirectionsEngine(chart)

        # Calculate some directions
        sun_asc = engine.direct("Sun", "ASC")
        moon_mc = engine.direct("Moon", "MC")

        # All should produce valid results
        assert sun_asc.age > 0
        assert moon_mc.age > 0
        assert sun_asc.date > birth
        assert moon_mc.date > birth

    def test_full_workflow_distributions(self):
        """Complete distributions workflow."""
        birth = dt.datetime(1948, 11, 14, 21, 14)
        chart = ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

        calc = DistributionsCalculator(chart)
        periods = calc.calculate(years=80)

        # Should have multiple periods
        assert len(periods) >= 5

        # Periods should span a reasonable range
        ages = [p.start_age for p in periods]
        assert max(ages) > 50  # Should have periods into later life

    def test_einstein_notable(self):
        """Test with a notable chart (Einstein)."""
        chart = ChartBuilder.from_notable("Albert Einstein").calculate()

        engine = DirectionsEngine(chart)
        result = engine.direct("Sun", "ASC")

        assert result.age is not None
        assert result.arc.method == "zodiacal"

    def test_obliquity_varies_by_date(self):
        """Obliquity should vary slightly between different dates."""
        # Two charts 100 years apart
        chart1 = ChartBuilder.from_details(
            dt.datetime(1900, 1, 1, 12, 0), (0.0, 51.5)
        ).calculate()
        chart2 = ChartBuilder.from_details(
            dt.datetime(2000, 1, 1, 12, 0), (0.0, 51.5)
        ).calculate()

        obl1 = get_obliquity(chart1.datetime.julian_day)
        obl2 = get_obliquity(chart2.datetime.julian_day)

        # Should be close but not identical
        assert obl1 != obl2
        assert abs(obl1 - obl2) < 0.5  # Within 0.5 degrees


# =============================================================================
# SECTION 8: EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_high_latitude_chart(self):
        """Charts at extreme latitudes should still work."""
        # Reykjavik, Iceland (64°N)
        birth = dt.datetime(2000, 6, 21, 12, 0)
        chart = ChartBuilder.from_details(birth, (-21.9, 64.1)).calculate()

        engine = DirectionsEngine(chart)
        result = engine.direct("Sun", "ASC")

        # Should produce valid result even at high latitude
        assert result.age is not None

    def test_southern_hemisphere(self):
        """Southern hemisphere charts should work correctly."""
        # Sydney, Australia (lon, lat)
        birth = dt.datetime(2000, 1, 1, 12, 0)
        chart = ChartBuilder.from_details(birth, (-33.9, 151.2)).calculate()

        engine = DirectionsEngine(chart)
        result = engine.direct("Sun", "ASC")

        assert result.age is not None
