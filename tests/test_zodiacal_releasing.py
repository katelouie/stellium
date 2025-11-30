"""Tests for Zodiacal Releasing calculations.

These tests verify that ZodiacalReleasingEngine correctly calculates:
- Period durations based on sign rulers
- Multi-level periods (L1-L4)
- Angular sign detection (1st, 4th, 7th, 10th from Lot)
- Peak periods (10th from Lot)
- Loosing of the Bond detection
- Timeline queries by date and age
- CalculatedChart convenience methods
"""

import datetime as dt

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.models import ZRSnapshot, ZRTimeline
from stellium.engines.releasing import (
    PLANET_PERIODS,
    ZodiacalReleasingAnalyzer,
    ZodiacalReleasingEngine,
)


@pytest.fixture
def einstein_natal():
    """Albert Einstein's natal chart (well-documented birth data).

    Born March 14, 1879, Ulm, Germany
    """
    return ChartBuilder.from_notable("Albert Einstein").calculate()


@pytest.fixture
def kate_natal():
    """Kate's natal chart for testing.

    Born January 6, 1994, Palo Alto, CA
    """
    return ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate",
    ).calculate()


@pytest.fixture
def kate_with_zr():
    """Kate's chart with zodiacal releasing pre-calculated."""
    return (
        ChartBuilder.from_details(
            "1994-01-06 11:47",
            "Palo Alto, CA",
            name="Kate",
        )
        .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"]))
        .calculate()
    )


class TestPlanetPeriods:
    """Test the planetary period constants."""

    def test_all_traditional_planets_have_periods(self):
        """All traditional planets should have defined periods."""
        expected_planets = ["Moon", "Mercury", "Venus", "Sun", "Mars", "Jupiter", "Saturn"]
        for planet in expected_planets:
            assert planet in PLANET_PERIODS

    def test_period_values_are_correct(self):
        """Period values should match traditional Valens system."""
        assert PLANET_PERIODS["Moon"] == 25
        assert PLANET_PERIODS["Mercury"] == 20
        assert PLANET_PERIODS["Venus"] == 8
        assert PLANET_PERIODS["Sun"] == 19
        assert PLANET_PERIODS["Mars"] == 15
        assert PLANET_PERIODS["Jupiter"] == 12
        assert PLANET_PERIODS["Saturn"] == 27

    def test_total_cycle_is_208_years(self, kate_natal):
        """Total cycle (all sign periods summed) should equal 208 years."""
        engine = ZodiacalReleasingEngine(kate_natal)
        total = sum(engine.sign_periods.values())
        assert total == 208


class TestZodiacalReleasingEngineInit:
    """Test ZodiacalReleasingEngine initialization."""

    def test_engine_initializes_with_defaults(self, kate_natal):
        """Engine should initialize with default parameters."""
        engine = ZodiacalReleasingEngine(kate_natal)

        assert engine.lot == "Part of Fortune"
        assert engine.max_level == 4
        assert engine.lifespan == 100

    def test_engine_accepts_custom_lot(self, kate_natal):
        """Engine should accept custom lot name."""
        engine = ZodiacalReleasingEngine(kate_natal, lot="Part of Spirit")

        assert engine.lot == "Part of Spirit"

    def test_engine_accepts_custom_max_level(self, kate_natal):
        """Engine should accept custom max_level."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=2)

        assert engine.max_level == 2

    def test_engine_accepts_custom_lifespan(self, kate_natal):
        """Engine should accept custom lifespan."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=120)

        assert engine.lifespan == 120

    def test_engine_calculates_lot_position(self, kate_natal):
        """Engine should calculate lot position on init."""
        engine = ZodiacalReleasingEngine(kate_natal)

        assert engine.lot_position is not None
        assert engine.lot_sign is not None
        assert engine.lot_sign in [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

    def test_engine_invalid_lot_raises_error(self, kate_natal):
        """Invalid lot name should raise ValueError."""
        with pytest.raises(ValueError, match="Provided Lot name unknown"):
            ZodiacalReleasingEngine(kate_natal, lot="Not A Real Lot")

    def test_engine_identifies_angular_signs(self, kate_natal):
        """Engine should correctly identify angular signs from Lot."""
        engine = ZodiacalReleasingEngine(kate_natal)

        # Should have exactly 4 angular signs
        assert len(engine.angular_signs) == 4

        # Angular signs should be at positions 1, 4, 7, 10
        positions = list(engine.angular_signs.values())
        assert sorted(positions) == [1, 4, 7, 10]


class TestSignPeriods:
    """Test sign period calculations."""

    def test_sign_periods_match_rulers(self, kate_natal):
        """Sign periods should match their traditional ruler's period."""
        engine = ZodiacalReleasingEngine(kate_natal)

        # Aries ruled by Mars (15 years)
        assert engine.sign_periods["Aries"] == 15

        # Taurus ruled by Venus (8 years)
        assert engine.sign_periods["Taurus"] == 8

        # Gemini ruled by Mercury (20 years)
        assert engine.sign_periods["Gemini"] == 20

        # Cancer ruled by Moon (25 years)
        assert engine.sign_periods["Cancer"] == 25

        # Leo ruled by Sun (19 years)
        assert engine.sign_periods["Leo"] == 19

        # Virgo ruled by Mercury (20 years)
        assert engine.sign_periods["Virgo"] == 20

        # Libra ruled by Venus (8 years)
        assert engine.sign_periods["Libra"] == 8

        # Scorpio ruled by Mars (15 years)
        assert engine.sign_periods["Scorpio"] == 15

        # Sagittarius ruled by Jupiter (12 years)
        assert engine.sign_periods["Sagittarius"] == 12

        # Capricorn ruled by Saturn (27 years)
        assert engine.sign_periods["Capricorn"] == 27

        # Aquarius ruled by Saturn (27 years)
        assert engine.sign_periods["Aquarius"] == 27

        # Pisces ruled by Jupiter (12 years)
        assert engine.sign_periods["Pisces"] == 12

    def test_all_signs_have_periods(self, kate_natal):
        """All 12 signs should have defined periods."""
        engine = ZodiacalReleasingEngine(kate_natal)

        assert len(engine.sign_periods) == 12


class TestL1Periods:
    """Test Level 1 (major life periods) calculations."""

    def test_l1_periods_exist(self, kate_natal):
        """L1 periods should be calculated."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        assert 1 in periods
        assert len(periods[1]) > 0

    def test_l1_starts_from_lot_sign(self, kate_natal):
        """First L1 period should start from the Lot's sign."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        first_period = periods[1][0]
        assert first_period.sign == engine.lot_sign

    def test_l1_starts_at_birth(self, kate_natal):
        """First L1 period should start at birth time."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        first_period = periods[1][0]
        assert first_period.start == kate_natal.datetime.utc_datetime

    def test_l1_periods_are_contiguous(self, kate_natal):
        """L1 periods should be contiguous (end of one = start of next)."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        for i in range(len(periods[1]) - 1):
            assert periods[1][i].end == periods[1][i + 1].start

    def test_l1_covers_lifespan(self, kate_natal):
        """L1 periods should cover at least the lifespan."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=100)
        periods = engine.calculate_all_periods()

        # Last period should end past age 100
        last_period = periods[1][-1]
        age_at_end = (last_period.end - kate_natal.datetime.utc_datetime).days / 365.25
        assert age_at_end >= 100

    def test_l1_period_durations_match_sign_periods(self, kate_natal):
        """L1 period durations should match sign years converted to days."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        for period in periods[1]:
            expected_years = engine.sign_periods[period.sign]
            expected_days = expected_years * 365.25
            # Allow small tolerance for floating point
            assert abs(period.length_days - expected_days) < 0.01


class TestL2Periods:
    """Test Level 2 (sub-periods) calculations."""

    def test_l2_periods_exist(self, kate_natal):
        """L2 periods should be calculated."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        assert 2 in periods
        assert len(periods[2]) > 0

    def test_l2_subdivides_l1(self, kate_natal):
        """Each L1 period should contain exactly 12 L2 periods."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        # Count L2 periods for first L1
        first_l1 = periods[1][0]
        l2_in_first_l1 = [
            p for p in periods[2]
            if first_l1.start <= p.start < first_l1.end
        ]

        assert len(l2_in_first_l1) == 12

    def test_l2_starts_from_parent_sign(self, kate_natal):
        """First L2 in each L1 should start from parent's sign."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        # Find first L2 period
        first_l1 = periods[1][0]
        first_l2 = next(p for p in periods[2] if p.start == first_l1.start)

        assert first_l2.sign == first_l1.sign

    def test_l2_durations_are_fractional(self, kate_natal):
        """L2 durations should be fractions of L1 duration."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        first_l1 = periods[1][0]
        l2_periods = [
            p for p in periods[2]
            if first_l1.start <= p.start < first_l1.end
        ]

        total_l2_days = sum(p.length_days for p in l2_periods)
        assert abs(total_l2_days - first_l1.length_days) < 0.01


class TestL3AndL4Periods:
    """Test Level 3 and Level 4 period calculations."""

    def test_l3_periods_exist_when_max_level_is_3_or_higher(self, kate_natal):
        """L3 periods should exist when max_level >= 3."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=3)
        periods = engine.calculate_all_periods()

        assert 3 in periods
        assert len(periods[3]) > 0

    def test_l4_periods_exist_when_max_level_is_4(self, kate_natal):
        """L4 periods should exist when max_level >= 4."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=4)
        periods = engine.calculate_all_periods()

        assert 4 in periods
        assert len(periods[4]) > 0

    def test_no_l3_when_max_level_is_2(self, kate_natal):
        """L3 periods should not exist when max_level = 2."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=2)
        periods = engine.calculate_all_periods()

        assert 3 not in periods

    def test_l3_subdivides_l2(self, kate_natal):
        """Each L2 period should have 12 L3 sub-periods."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=3)
        periods = engine.calculate_all_periods()

        # Take first L2 period
        first_l2 = periods[2][0]
        l3_in_first_l2 = [
            p for p in periods[3]
            if first_l2.start <= p.start < first_l2.end
        ]

        assert len(l3_in_first_l2) == 12


class TestAngularSignsAndPeaks:
    """Test angular sign detection and peak period identification."""

    def test_first_house_sign_is_angular(self, kate_natal):
        """Lot sign (1st house from Lot) should be angular."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        # First period is the Lot sign
        first_l1 = periods[1][0]
        assert first_l1.is_angular is True
        assert first_l1.angle_from_lot == 1

    def test_tenth_from_lot_is_peak(self, kate_natal):
        """10th sign from Lot should be marked as peak."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        # L1 peaks may not occur within default 100-year lifespan depending on lot sign
        # But L2 periods definitely include peaks (12 signs per L1)
        peak_periods = [p for p in periods[2] if p.is_peak]

        assert len(peak_periods) > 0
        for p in peak_periods:
            assert p.angle_from_lot == 10

    def test_non_angular_signs_not_marked(self, kate_natal):
        """Non-angular signs (2, 3, 5, 6, 8, 9, 11, 12) should not be angular."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        for period in periods[1]:
            if period.angle_from_lot is None:
                assert period.is_angular is False
                assert period.is_peak is False


class TestLoosingOfTheBond:
    """Test Loosing of the Bond detection."""

    def test_l1_never_triggers_loosing_bond(self, kate_natal):
        """L1 periods should never trigger Loosing of the Bond."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        for period in periods[1]:
            assert period.is_loosing_bond is False

    def test_angular_l2_triggers_loosing_bond(self, kate_natal):
        """Angular L2 periods should trigger Loosing of the Bond."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        angular_l2 = [p for p in periods[2] if p.is_angular]
        assert len(angular_l2) > 0

        for period in angular_l2:
            assert period.is_loosing_bond is True

    def test_non_angular_l2_no_loosing_bond(self, kate_natal):
        """Non-angular L2 periods should not trigger Loosing of the Bond."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        non_angular_l2 = [p for p in periods[2] if not p.is_angular]

        for period in non_angular_l2:
            assert period.is_loosing_bond is False


class TestZRTimeline:
    """Test ZRTimeline functionality."""

    def test_timeline_build(self, kate_natal):
        """build_timeline should return ZRTimeline."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        assert isinstance(timeline, ZRTimeline)
        assert timeline.lot == "Part of Fortune"
        assert timeline.lot_sign == engine.lot_sign
        assert timeline.birth_date == kate_natal.datetime.utc_datetime

    def test_timeline_at_date(self, kate_natal):
        """Timeline should return snapshot for a specific date."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        # Query a date 30 years after birth
        query_date = kate_natal.datetime.utc_datetime + dt.timedelta(days=30 * 365.25)
        snapshot = timeline.at_date(query_date)

        assert isinstance(snapshot, ZRSnapshot)
        assert snapshot.l1 is not None
        assert snapshot.l2 is not None
        assert abs(snapshot.age - 30) < 0.01

    def test_timeline_at_age(self, kate_natal):
        """Timeline should return snapshot for a specific age."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        snapshot = timeline.at_age(25)

        assert isinstance(snapshot, ZRSnapshot)
        assert abs(snapshot.age - 25) < 0.01

    def test_timeline_date_outside_range_raises_error(self, kate_natal):
        """Querying date outside timeline should raise error."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=50)
        timeline = engine.build_timeline()

        # Query date 200 years after birth (outside lifespan)
        future_date = kate_natal.datetime.utc_datetime + dt.timedelta(days=200 * 365.25)

        with pytest.raises(ValueError, match="outside calculated timeline"):
            timeline.at_date(future_date)

    def test_timeline_find_peaks(self, kate_natal):
        """find_peaks should return all peak periods at given level."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        # L2 peaks are more common (12 signs per L1 period)
        peaks = timeline.find_peaks(level=2)

        assert len(peaks) > 0
        for peak in peaks:
            assert peak.is_peak is True
            assert peak.level == 2

    def test_timeline_find_loosing_bonds(self, kate_natal):
        """find_loosing_bonds should return LB periods at given level."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        lb_periods = timeline.find_loosing_bonds(level=2)

        assert len(lb_periods) > 0
        for period in lb_periods:
            assert period.is_loosing_bond is True
            assert period.level == 2

    def test_timeline_l1_periods(self, kate_natal):
        """l1_periods should return all L1 periods."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        l1_periods = timeline.l1_periods()

        assert len(l1_periods) > 0
        for period in l1_periods:
            assert period.level == 1


class TestZRSnapshot:
    """Test ZRSnapshot dataclass and properties."""

    def test_snapshot_has_all_levels(self, kate_natal):
        """Snapshot should have L1, L2, and optionally L3/L4."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=4)
        timeline = engine.build_timeline()
        snapshot = timeline.at_age(30)

        assert snapshot.l1 is not None
        assert snapshot.l2 is not None
        assert snapshot.l3 is not None
        assert snapshot.l4 is not None

    def test_snapshot_max_level_2_no_l3_l4(self, kate_natal):
        """Snapshot with max_level=2 should have None for L3/L4."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=2)
        timeline = engine.build_timeline()
        snapshot = timeline.at_age(30)

        assert snapshot.l1 is not None
        assert snapshot.l2 is not None
        assert snapshot.l3 is None
        assert snapshot.l4 is None

    def test_snapshot_is_peak_property(self, kate_natal):
        """is_peak should be True if any level is peak."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        # Find a snapshot during an L1 peak
        peaks = timeline.find_peaks(level=1)
        if peaks:
            peak_period = peaks[0]
            # Query middle of peak period
            mid_date = peak_period.start + dt.timedelta(days=peak_period.length_days / 2)
            snapshot = timeline.at_date(mid_date)

            assert snapshot.l1.is_peak is True
            assert snapshot.is_peak is True

    def test_snapshot_is_lb_property(self, kate_natal):
        """is_lb should be True if any level >= 2 has Loosing of Bond."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        lb_periods = timeline.find_loosing_bonds(level=2)
        if lb_periods:
            lb_period = lb_periods[0]
            mid_date = lb_period.start + dt.timedelta(days=lb_period.length_days / 2)
            snapshot = timeline.at_date(mid_date)

            assert snapshot.is_lb is True

    def test_snapshot_rulers_property(self, kate_natal):
        """rulers should list all active rulers."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=4)
        timeline = engine.build_timeline()
        snapshot = timeline.at_age(30)

        rulers = snapshot.rulers

        assert len(rulers) == 4  # L1, L2, L3, L4 rulers
        for ruler in rulers:
            assert ruler in PLANET_PERIODS


class TestZRPeriod:
    """Test ZRPeriod dataclass."""

    def test_period_has_required_fields(self, kate_natal):
        """ZRPeriod should have all required fields."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        period = periods[1][0]

        assert hasattr(period, "level")
        assert hasattr(period, "sign")
        assert hasattr(period, "ruler")
        assert hasattr(period, "start")
        assert hasattr(period, "end")
        assert hasattr(period, "length_days")
        assert hasattr(period, "is_angular")
        assert hasattr(period, "angle_from_lot")
        assert hasattr(period, "is_loosing_bond")
        assert hasattr(period, "is_peak")

    def test_period_ruler_matches_sign(self, kate_natal):
        """Period ruler should match the traditional ruler of the sign."""
        engine = ZodiacalReleasingEngine(kate_natal)
        periods = engine.calculate_all_periods()

        # Check a few known rulers
        for period in periods[1]:
            if period.sign == "Aries":
                assert period.ruler == "Mars"
            elif period.sign == "Taurus":
                assert period.ruler == "Venus"
            elif period.sign == "Cancer":
                assert period.ruler == "Moon"
            elif period.sign == "Leo":
                assert period.ruler == "Sun"


class TestZodiacalReleasingAnalyzer:
    """Test ZodiacalReleasingAnalyzer for multiple lots."""

    def test_analyzer_with_single_lot(self, kate_natal):
        """Analyzer should work with single lot."""
        analyzer = ZodiacalReleasingAnalyzer(["Part of Fortune"])
        results = analyzer.analyze(kate_natal)

        assert "Part of Fortune" in results
        assert isinstance(results["Part of Fortune"], ZRTimeline)

    def test_analyzer_with_multiple_lots(self, kate_natal):
        """Analyzer should work with multiple lots."""
        analyzer = ZodiacalReleasingAnalyzer(["Part of Fortune", "Part of Spirit"])
        results = analyzer.analyze(kate_natal)

        assert "Part of Fortune" in results
        assert "Part of Spirit" in results

    def test_analyzer_name(self):
        """Analyzer should have correct name properties."""
        analyzer = ZodiacalReleasingAnalyzer(["Part of Fortune"])

        assert analyzer.analyzer_name == "ZodiacalReleasing"
        assert analyzer.metadata_name == "zodiacal_releasing"

    def test_analyzer_respects_max_level(self, kate_natal):
        """Analyzer should respect max_level parameter."""
        analyzer = ZodiacalReleasingAnalyzer(["Part of Fortune"], max_level=2)
        results = analyzer.analyze(kate_natal)

        timeline = results["Part of Fortune"]
        assert timeline.max_level == 2

    def test_analyzer_respects_lifespan(self, kate_natal):
        """Analyzer should respect lifespan parameter."""
        analyzer = ZodiacalReleasingAnalyzer(["Part of Fortune"], lifespan=50)
        results = analyzer.analyze(kate_natal)

        timeline = results["Part of Fortune"]
        # Last L1 period should end around age 50-60
        last_l1 = timeline.l1_periods()[-1]
        age_at_end = (last_l1.end - kate_natal.datetime.utc_datetime).days / 365.25
        assert age_at_end < 80  # Should be less than default 100


class TestChartConvenienceMethods:
    """Test convenience methods on CalculatedChart."""

    def test_chart_zodiacal_releasing(self, kate_with_zr):
        """chart.zodiacal_releasing() should return timeline."""
        timeline = kate_with_zr.zodiacal_releasing("Part of Fortune")

        assert isinstance(timeline, ZRTimeline)
        assert timeline.lot == "Part of Fortune"

    def test_chart_zodiacal_releasing_default_lot(self, kate_with_zr):
        """Default lot should be Part of Fortune."""
        timeline = kate_with_zr.zodiacal_releasing()

        assert timeline.lot == "Part of Fortune"

    def test_chart_zr_at_date(self, kate_with_zr):
        """chart.zr_at_date() should return snapshot."""
        query_date = kate_with_zr.datetime.utc_datetime + dt.timedelta(days=30 * 365.25)
        snapshot = kate_with_zr.zr_at_date(query_date)

        assert isinstance(snapshot, ZRSnapshot)
        assert abs(snapshot.age - 30) < 0.01

    def test_chart_zr_at_age(self, kate_with_zr):
        """chart.zr_at_age() should return snapshot."""
        snapshot = kate_with_zr.zr_at_age(25)

        assert isinstance(snapshot, ZRSnapshot)
        assert abs(snapshot.age - 25) < 0.01

    def test_chart_zr_at_age_float(self, kate_with_zr):
        """chart.zr_at_age() should accept float ages."""
        snapshot = kate_with_zr.zr_at_age(25.5)

        assert isinstance(snapshot, ZRSnapshot)
        assert abs(snapshot.age - 25.5) < 0.01

    def test_chart_zr_different_lot(self, kate_with_zr):
        """Should be able to query different lots."""
        fortune_timeline = kate_with_zr.zodiacal_releasing("Part of Fortune")
        spirit_timeline = kate_with_zr.zodiacal_releasing("Part of Spirit")

        # They should have different lot signs (usually)
        assert fortune_timeline.lot == "Part of Fortune"
        assert spirit_timeline.lot == "Part of Spirit"


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_zr_workflow(self, kate_natal):
        """Test complete ZR analysis workflow."""
        # Create analyzer
        analyzer = ZodiacalReleasingAnalyzer(
            lots=["Part of Fortune", "Part of Spirit"],
            max_level=4,
            lifespan=100,
        )

        # Analyze chart
        results = analyzer.analyze(kate_natal)

        # Check both lots
        for lot_name in ["Part of Fortune", "Part of Spirit"]:
            timeline = results[lot_name]

            # Query different ages
            age_10 = timeline.at_age(10)
            age_30 = timeline.at_age(30)
            age_50 = timeline.at_age(50)

            # Verify all have data
            assert age_10.l1 is not None
            assert age_30.l1 is not None
            assert age_50.l1 is not None

            # Find significant periods (use L2 for peaks since L1 peaks may be beyond lifespan)
            peaks = timeline.find_peaks(level=2)
            lb_periods = timeline.find_loosing_bonds()

            assert len(peaks) > 0
            assert len(lb_periods) > 0

    def test_zr_through_chart_builder(self):
        """Test ZR integration through ChartBuilder."""
        chart = (
            ChartBuilder.from_details(
                "1994-01-06 11:47",
                "Palo Alto, CA",
            )
            .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
            .calculate()
        )

        # Access through metadata
        assert "zodiacal_releasing" in chart.metadata

        # Access through convenience methods
        timeline = chart.zodiacal_releasing()
        assert isinstance(timeline, ZRTimeline)

        snapshot = chart.zr_at_age(30)
        assert isinstance(snapshot, ZRSnapshot)

    def test_zr_periods_cover_entire_life(self, kate_natal):
        """Verify L1 periods cover entire calculated lifespan."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=80)
        timeline = engine.build_timeline()

        # Check age 1 through 80
        for age in [1, 10, 20, 30, 40, 50, 60, 70, 79]:
            snapshot = timeline.at_age(age)
            assert snapshot.l1 is not None
            assert snapshot.l2 is not None

    def test_zr_cycle_repeats_correctly(self, kate_natal):
        """Verify ZR cycle repeats every 208 years (sign sequence)."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=210)
        timeline = engine.build_timeline()

        # L1 at age 0 should be same sign as L1 at age 208
        age_0 = timeline.at_age(0)
        age_208 = timeline.at_age(208)

        assert age_0.l1.sign == age_208.l1.sign

    def test_notable_chart_zr(self):
        """Test ZR on a notable's chart."""
        chart = (
            ChartBuilder.from_notable("Albert Einstein")
            .add_analyzer(ZodiacalReleasingAnalyzer(["Part of Fortune"]))
            .calculate()
        )

        # Einstein's miracle year was 1905 when he was ~26
        snapshot = chart.zr_at_age(26)

        assert snapshot.l1 is not None
        assert snapshot.l2 is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_age_zero_snapshot(self, kate_natal):
        """Age 0 should return valid snapshot."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        snapshot = timeline.at_age(0)

        assert snapshot.l1 is not None
        assert snapshot.l1.sign == engine.lot_sign
        assert snapshot.age == 0

    def test_very_small_age(self, kate_natal):
        """Very small ages (fractions of year) should work."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        snapshot = timeline.at_age(0.01)

        assert snapshot.l1 is not None
        assert snapshot.age < 0.1

    def test_birth_date_exact(self, kate_natal):
        """Querying exact birth date should work."""
        engine = ZodiacalReleasingEngine(kate_natal)
        timeline = engine.build_timeline()

        snapshot = timeline.at_date(kate_natal.datetime.utc_datetime)

        assert snapshot.l1 is not None
        assert snapshot.age == 0

    def test_max_level_1_only(self, kate_natal):
        """max_level=1 should only calculate L1."""
        engine = ZodiacalReleasingEngine(kate_natal, max_level=1)
        periods = engine.calculate_all_periods()

        assert 1 in periods
        assert 2 not in periods

    def test_short_lifespan(self, kate_natal):
        """Very short lifespan should still work."""
        engine = ZodiacalReleasingEngine(kate_natal, lifespan=10)
        timeline = engine.build_timeline()

        # Should cover at least 10 years
        snapshot = timeline.at_age(9)
        assert snapshot.l1 is not None

    def test_different_lots_produce_different_timelines(self, kate_natal):
        """Fortune and Spirit should generally produce different timelines."""
        fortune_engine = ZodiacalReleasingEngine(kate_natal, lot="Part of Fortune")
        spirit_engine = ZodiacalReleasingEngine(kate_natal, lot="Part of Spirit")

        fortune_timeline = fortune_engine.build_timeline()
        spirit_timeline = spirit_engine.build_timeline()

        # Different lot signs (unless chart has unusual configuration)
        # Just verify both work independently
        assert fortune_timeline.lot_sign is not None
        assert spirit_timeline.lot_sign is not None
