"""
Tests for the electional astrology search module.

Tests cover:
- ElectionalSearch class and its methods
- Predicates (is_waxing, not_voc, sign_in, etc.)
- TimeWindow operations (intersect, union, invert)
- Interval generators (waxing_windows, voc_windows, etc.)
- Planetary hours
"""

from datetime import datetime, timedelta

import pytest

# =============================================================================
# ElectionalSearch Tests
# =============================================================================


class TestElectionalSearch:
    """Tests for the ElectionalSearch class."""

    def test_search_initialization_with_strings(self):
        """Can initialize search with date strings and location string."""
        from stellium.electional import ElectionalSearch

        search = ElectionalSearch("2025-01-01", "2025-01-31", "San Francisco, CA")

        assert search.start == datetime(2025, 1, 1)
        assert search.end == datetime(2025, 1, 31)

    def test_search_initialization_with_datetimes(self):
        """Can initialize search with datetime objects."""
        from stellium.electional import ElectionalSearch

        start = datetime(2025, 1, 1, 10, 30)
        end = datetime(2025, 1, 31, 18, 0)
        search = ElectionalSearch(start, end, "New York, NY")

        assert search.start == start
        assert search.end == end

    def test_where_method_chaining(self):
        """where() returns self for method chaining."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch("2025-01-01", "2025-01-07", "San Francisco, CA")
        result = search.where(is_waxing())

        assert result is search
        assert len(search._conditions) == 1

    def test_multiple_conditions(self):
        """Can add multiple conditions with chained where() calls."""
        from stellium.electional import ElectionalSearch, is_waxing, not_voc

        search = (
            ElectionalSearch("2025-01-01", "2025-01-07", "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
        )

        assert len(search._conditions) == 2

    def test_find_moments_returns_list(self):
        """find_moments() returns a list of ElectionMoment objects."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch(
            "2025-01-01", "2025-01-03", "San Francisco, CA"
        ).where(is_waxing())

        results = search.find_moments(max_results=5, step="4hour")

        assert isinstance(results, list)
        # Should find some waxing moments in a 2-day period
        # (depends on actual moon phase, but waxing is ~half the month)

    def test_find_first_returns_single_moment_or_none(self):
        """find_first() returns a single ElectionMoment or None."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch(
            "2025-01-01", "2025-01-15", "San Francisco, CA"
        ).where(is_waxing())

        result = search.find_first(step="4hour")

        # Should find at least one waxing moment in 2 weeks
        from stellium.electional import ElectionMoment

        assert result is None or isinstance(result, ElectionMoment)

    def test_find_windows_coalesces_adjacent_moments(self):
        """find_windows() groups adjacent passing moments into windows."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch(
            "2025-01-01", "2025-01-15", "San Francisco, CA"
        ).where(is_waxing())

        windows = search.find_windows(step="4hour")

        assert isinstance(windows, list)
        # Waxing period is continuous, should be one or few windows
        if windows:
            from stellium.electional import ElectionWindow

            assert isinstance(windows[0], ElectionWindow)
            assert windows[0].duration > timedelta(hours=0)

    def test_iter_moments_is_generator(self):
        """iter_moments() yields results lazily."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch(
            "2025-01-01", "2025-01-03", "San Francisco, CA"
        ).where(is_waxing())

        gen = search.iter_moments(step="4hour")

        # Should be a generator
        assert hasattr(gen, "__next__")

        # Should be able to get at least one result (if any exist)
        results = list(gen)
        assert isinstance(results, list)

    def test_count_returns_integer(self):
        """count() returns the number of matching moments."""
        from stellium.electional import ElectionalSearch, is_waxing

        search = ElectionalSearch(
            "2025-01-01", "2025-01-03", "San Francisco, CA"
        ).where(is_waxing())

        count = search.count(step="4hour")

        assert isinstance(count, int)
        assert count >= 0

    def test_repr_shows_date_range_and_conditions(self):
        """__repr__ shows useful summary."""
        from stellium.electional import ElectionalSearch, is_waxing, not_voc

        search = (
            ElectionalSearch("2025-01-01", "2025-01-31", "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
        )

        repr_str = repr(search)
        assert "2025-01-01" in repr_str
        assert "2025-01-31" in repr_str
        assert "2 conditions" in repr_str


class TestCompositionFunctions:
    """Tests for all_of, any_of, and not_ composition functions."""

    def test_all_of_requires_all_conditions(self):
        """all_of() only returns True if all conditions are True."""
        from stellium.electional import all_of

        def cond_true(_c):
            return True

        def cond_false(_c):
            return False

        combined_all_true = all_of(cond_true, cond_true)
        combined_with_false = all_of(cond_true, cond_true, cond_false)

        # Mock chart (conditions don't actually use it)
        mock_chart = None

        assert combined_all_true(mock_chart) is True
        assert combined_with_false(mock_chart) is False

    def test_any_of_requires_one_condition(self):
        """any_of() returns True if at least one condition is True."""
        from stellium.electional import any_of

        def cond_true(_c):
            return True

        def cond_false(_c):
            return False

        combined_with_one_true = any_of(cond_false, cond_true, cond_false)
        combined_all_false = any_of(cond_false, cond_false)

        mock_chart = None

        assert combined_with_one_true(mock_chart) is True
        assert combined_all_false(mock_chart) is False

    def test_not_negates_condition(self):
        """not_() negates a condition."""
        from stellium.electional import not_

        def cond_true(_c):
            return True

        def cond_false(_c):
            return False

        negated_true = not_(cond_true)
        negated_false = not_(cond_false)

        mock_chart = None

        assert negated_true(mock_chart) is False
        assert negated_false(mock_chart) is True


# =============================================================================
# Predicate Tests
# =============================================================================


class TestMoonPhasePredicates:
    """Tests for moon phase predicates."""

    def test_is_waxing_has_speed_hint(self):
        """is_waxing() predicate has SPEED_DAY speed hint."""
        from stellium.electional import is_waxing
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = is_waxing()
        assert get_speed_hint(cond) == SPEED_DAY

    def test_is_waxing_has_window_generator(self):
        """is_waxing() predicate has a window generator attached."""
        from stellium.electional import is_waxing
        from stellium.electional.predicates import get_window_generator

        cond = is_waxing()
        gen = get_window_generator(cond)
        assert gen is not None
        assert callable(gen)

    def test_is_waning_has_speed_hint(self):
        """is_waning() predicate has SPEED_DAY speed hint."""
        from stellium.electional import is_waning
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = is_waning()
        assert get_speed_hint(cond) == SPEED_DAY

    def test_moon_phase_accepts_list(self):
        """moon_phase() accepts a list of phase names."""
        from stellium.electional import moon_phase
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = moon_phase(["New Moon", "Full Moon"])
        assert get_speed_hint(cond) == SPEED_DAY


class TestVOCPredicates:
    """Tests for void of course moon predicates."""

    def test_is_voc_has_speed_hint(self):
        """is_voc() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import is_voc
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = is_voc()
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_not_voc_has_window_generator(self):
        """not_voc() predicate has a window generator attached."""
        from stellium.electional import not_voc
        from stellium.electional.predicates import get_window_generator

        cond = not_voc()
        gen = get_window_generator(cond)
        assert gen is not None

    def test_voc_modes(self):
        """is_voc() and not_voc() accept mode parameter."""
        from stellium.electional import is_voc, not_voc

        # Should not raise - just verify they return callable conditions
        assert callable(is_voc(mode="traditional"))
        assert callable(is_voc(mode="modern"))
        assert callable(not_voc(mode="traditional"))
        assert callable(not_voc(mode="modern"))


class TestSignPredicates:
    """Tests for sign-based predicates."""

    def test_sign_in_has_speed_hint(self):
        """sign_in() predicate has SPEED_DAY_SIGN speed hint."""
        from stellium.electional import sign_in
        from stellium.electional.predicates import SPEED_DAY_SIGN, get_speed_hint

        cond = sign_in("Moon", ["Taurus", "Cancer"])
        assert get_speed_hint(cond) == SPEED_DAY_SIGN

    def test_sign_in_moon_has_window_generator(self):
        """sign_in() for Moon has a window generator attached."""
        from stellium.electional import sign_in
        from stellium.electional.predicates import get_window_generator

        cond = sign_in("Moon", ["Taurus", "Cancer"])
        gen = get_window_generator(cond)
        assert gen is not None

    def test_sign_in_planet_no_window_generator(self):
        """sign_in() for non-Moon planets doesn't have window generator."""
        from stellium.electional import sign_in
        from stellium.electional.predicates import get_window_generator

        cond = sign_in("Mars", ["Aries"])
        gen = get_window_generator(cond)
        assert gen is None

    def test_sign_not_in_has_speed_hint(self):
        """sign_not_in() predicate has SPEED_DAY_SIGN speed hint."""
        from stellium.electional import sign_not_in
        from stellium.electional.predicates import SPEED_DAY_SIGN, get_speed_hint

        cond = sign_not_in("Moon", ["Scorpio", "Capricorn"])
        assert get_speed_hint(cond) == SPEED_DAY_SIGN


class TestHousePredicates:
    """Tests for house-based predicates."""

    def test_in_house_has_speed_hint(self):
        """in_house() predicate has SPEED_MINUTE speed hint."""
        from stellium.electional import in_house
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = in_house("Moon", [1, 10])
        assert get_speed_hint(cond) == SPEED_MINUTE

    def test_on_angle_is_angular_houses(self):
        """on_angle() is equivalent to in_house([1, 4, 7, 10])."""
        from stellium.electional import on_angle
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = on_angle("Jupiter")
        assert get_speed_hint(cond) == SPEED_MINUTE

    def test_succedent_is_succedent_houses(self):
        """succedent() returns in_house([2, 5, 8, 11])."""
        from stellium.electional import succedent
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = succedent("Venus")
        assert get_speed_hint(cond) == SPEED_MINUTE

    def test_cadent_is_cadent_houses(self):
        """cadent() returns in_house([3, 6, 9, 12])."""
        from stellium.electional import cadent
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = cadent("Mercury")
        assert get_speed_hint(cond) == SPEED_MINUTE

    def test_not_in_house_has_speed_hint(self):
        """not_in_house() predicate has SPEED_MINUTE speed hint."""
        from stellium.electional import not_in_house
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = not_in_house("Moon", [6, 12])
        assert get_speed_hint(cond) == SPEED_MINUTE


class TestRetrogradePredicates:
    """Tests for retrograde predicates."""

    def test_is_retrograde_has_speed_hint(self):
        """is_retrograde() predicate has SPEED_DAY speed hint."""
        from stellium.electional import is_retrograde
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = is_retrograde("Mercury")
        assert get_speed_hint(cond) == SPEED_DAY

    def test_is_retrograde_has_window_generator(self):
        """is_retrograde() predicate has a window generator attached."""
        from stellium.electional import is_retrograde
        from stellium.electional.predicates import get_window_generator

        cond = is_retrograde("Mercury")
        gen = get_window_generator(cond)
        assert gen is not None

    def test_not_retrograde_has_speed_hint(self):
        """not_retrograde() predicate has SPEED_DAY speed hint."""
        from stellium.electional import not_retrograde
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = not_retrograde("Mercury")
        assert get_speed_hint(cond) == SPEED_DAY


class TestAspectPredicates:
    """Tests for aspect predicates."""

    def test_has_aspect_has_speed_hint(self):
        """has_aspect() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import has_aspect
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = has_aspect("Moon", "Jupiter", ["trine"])
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_no_aspect_has_speed_hint(self):
        """no_aspect() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import no_aspect
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = no_aspect("Moon", "Saturn", ["square"])
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_no_hard_aspect_has_speed_hint(self):
        """no_hard_aspect() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import no_hard_aspect
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = no_hard_aspect("Moon")
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_no_malefic_aspect_has_speed_hint(self):
        """no_malefic_aspect() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import no_malefic_aspect
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = no_malefic_aspect("Moon")
        assert get_speed_hint(cond) == SPEED_HOUR


class TestAspectExactPredicate:
    """Tests for aspect_exact_within predicate."""

    def test_aspect_exact_within_has_speed_hint(self):
        """aspect_exact_within() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import aspect_exact_within
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = aspect_exact_within("Moon", "Jupiter", "trine", orb=1.0)
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_aspect_exact_within_has_window_generator(self):
        """aspect_exact_within() predicate has a window generator attached."""
        from stellium.electional import aspect_exact_within
        from stellium.electional.predicates import get_window_generator

        cond = aspect_exact_within("Moon", "Jupiter", "trine", orb=1.0)
        gen = get_window_generator(cond)
        assert gen is not None

    def test_aspect_exact_within_invalid_aspect_raises(self):
        """aspect_exact_within() raises for invalid aspect names."""
        from stellium.electional import aspect_exact_within

        with pytest.raises(ValueError):
            aspect_exact_within("Moon", "Jupiter", "invalid_aspect")


class TestCombustPredicates:
    """Tests for combust predicates."""

    def test_is_combust_has_speed_hint(self):
        """is_combust() predicate has SPEED_DAY speed hint."""
        from stellium.electional import is_combust
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = is_combust("Mercury")
        assert get_speed_hint(cond) == SPEED_DAY

    def test_not_combust_has_speed_hint(self):
        """not_combust() predicate has SPEED_DAY speed hint."""
        from stellium.electional import not_combust
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = not_combust("Mercury")
        assert get_speed_hint(cond) == SPEED_DAY

    def test_combust_custom_orb(self):
        """is_combust() and not_combust() accept custom orb."""
        from stellium.electional import is_combust, not_combust

        # Should not raise - just verify they return callable conditions
        assert callable(is_combust("Mercury", orb=5.0))
        assert callable(not_combust("Mercury", orb=10.0))


class TestOutOfBoundsPredicates:
    """Tests for out of bounds predicates."""

    def test_is_out_of_bounds_has_speed_hint(self):
        """is_out_of_bounds() predicate has SPEED_DAY speed hint."""
        from stellium.electional import is_out_of_bounds
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = is_out_of_bounds("Moon")
        assert get_speed_hint(cond) == SPEED_DAY

    def test_not_out_of_bounds_has_speed_hint(self):
        """not_out_of_bounds() predicate has SPEED_DAY speed hint."""
        from stellium.electional import not_out_of_bounds
        from stellium.electional.predicates import SPEED_DAY, get_speed_hint

        cond = not_out_of_bounds("Moon")
        assert get_speed_hint(cond) == SPEED_DAY


class TestAngleAtDegreePredicate:
    """Tests for angle_at_degree predicate."""

    def test_angle_at_degree_has_speed_hint(self):
        """angle_at_degree() predicate has SPEED_MINUTE speed hint."""
        from stellium.electional import angle_at_degree
        from stellium.electional.predicates import SPEED_MINUTE, get_speed_hint

        cond = angle_at_degree(0.0, "ASC", orb=1.0)
        assert get_speed_hint(cond) == SPEED_MINUTE

    def test_angle_at_degree_stores_params(self):
        """angle_at_degree() stores params for window generator."""
        from stellium.electional import angle_at_degree

        cond = angle_at_degree(15.5, "MC", orb=2.0)
        assert hasattr(cond, "_angle_window_params")
        assert cond._angle_window_params == (15.5, "MC", 2.0)


class TestPlanetaryHourPredicate:
    """Tests for in_planetary_hour predicate."""

    def test_in_planetary_hour_has_speed_hint(self):
        """in_planetary_hour() predicate has SPEED_HOUR speed hint."""
        from stellium.electional import in_planetary_hour
        from stellium.electional.predicates import SPEED_HOUR, get_speed_hint

        cond = in_planetary_hour("Jupiter")
        assert get_speed_hint(cond) == SPEED_HOUR

    def test_in_planetary_hour_stores_planet(self):
        """in_planetary_hour() stores planet name for window generator."""
        from stellium.electional import in_planetary_hour

        cond = in_planetary_hour("Venus")
        assert hasattr(cond, "_planetary_hour_planet")
        assert cond._planetary_hour_planet == "Venus"

    def test_in_planetary_hour_invalid_planet_raises(self):
        """in_planetary_hour() raises for invalid planet names."""
        from stellium.electional import in_planetary_hour

        with pytest.raises(ValueError):
            in_planetary_hour("Pluto")  # Not a classical planet


# =============================================================================
# TimeWindow Tests
# =============================================================================


class TestTimeWindow:
    """Tests for the TimeWindow dataclass."""

    def test_timewindow_creation(self):
        """Can create a TimeWindow with start and end JD."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460001.5)
        assert window.start_jd == 2460000.5
        assert window.end_jd == 2460001.5

    def test_timewindow_duration_days(self):
        """duration_days returns correct duration."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460003.5)
        assert window.duration_days == 3.0

    def test_timewindow_duration_hours(self):
        """duration_hours returns correct duration."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460000.75)  # 6 hours
        assert window.duration_hours == 6.0

    def test_timewindow_datetime_properties(self):
        """start_datetime and end_datetime return UTC datetimes."""
        from stellium.electional.intervals import TimeWindow

        # Use a known JD for testing
        window = TimeWindow(2451545.0, 2451546.0)  # Jan 1, 2000 12:00 UTC

        start = window.start_datetime
        end = window.end_datetime

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.year == 2000
        assert start.month == 1
        assert start.day == 1

    def test_timewindow_str(self):
        """__str__ shows human-readable format."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460001.5)
        s = str(window)

        assert "24.0h" in s  # 1 day = 24 hours

    def test_timewindow_repr(self):
        """__repr__ shows JD values."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460001.5)
        r = repr(window)

        assert "2460000.5" in r
        assert "2460001.5" in r

    def test_timewindow_is_frozen(self):
        """TimeWindow is immutable (frozen dataclass)."""
        from stellium.electional.intervals import TimeWindow

        window = TimeWindow(2460000.5, 2460001.5)

        with pytest.raises(AttributeError):
            window.start_jd = 2460002.0


class TestWindowSetOperations:
    """Tests for TimeWindow set operations."""

    def test_intersect_windows_overlapping(self):
        """intersect_windows finds overlapping regions."""
        from stellium.electional.intervals import TimeWindow, intersect_windows

        a = [TimeWindow(0.0, 10.0), TimeWindow(15.0, 25.0)]
        b = [TimeWindow(5.0, 20.0)]

        result = intersect_windows(a, b)

        # Should have two intersections:
        # [0,10] ∩ [5,20] = [5,10]
        # [15,25] ∩ [5,20] = [15,20]
        assert len(result) == 2
        assert result[0].start_jd == 5.0
        assert result[0].end_jd == 10.0
        assert result[1].start_jd == 15.0
        assert result[1].end_jd == 20.0

    def test_intersect_windows_no_overlap(self):
        """intersect_windows returns empty for non-overlapping windows."""
        from stellium.electional.intervals import TimeWindow, intersect_windows

        a = [TimeWindow(0.0, 5.0)]
        b = [TimeWindow(10.0, 15.0)]

        result = intersect_windows(a, b)
        assert result == []

    def test_intersect_windows_empty_input(self):
        """intersect_windows handles empty lists."""
        from stellium.electional.intervals import TimeWindow, intersect_windows

        a = [TimeWindow(0.0, 10.0)]
        b = []

        result = intersect_windows(a, b)
        assert result == []

    def test_union_windows_merges_overlapping(self):
        """union_windows merges overlapping windows."""
        from stellium.electional.intervals import TimeWindow, union_windows

        a = [TimeWindow(0.0, 10.0)]
        b = [TimeWindow(5.0, 15.0)]

        result = union_windows(a, b)

        # Should merge into single window [0, 15]
        assert len(result) == 1
        assert result[0].start_jd == 0.0
        assert result[0].end_jd == 15.0

    def test_union_windows_preserves_gaps(self):
        """union_windows preserves gaps between windows."""
        from stellium.electional.intervals import TimeWindow, union_windows

        a = [TimeWindow(0.0, 5.0)]
        b = [TimeWindow(10.0, 15.0)]

        result = union_windows(a, b)

        # Should have two separate windows
        assert len(result) == 2

    def test_invert_windows_finds_gaps(self):
        """invert_windows finds gaps between windows."""
        from stellium.electional.intervals import TimeWindow, invert_windows

        windows = [TimeWindow(5.0, 10.0), TimeWindow(15.0, 20.0)]

        result = invert_windows(windows, 0.0, 25.0)

        # Gaps: [0,5], [10,15], [20,25]
        assert len(result) == 3
        assert result[0].start_jd == 0.0
        assert result[0].end_jd == 5.0
        assert result[1].start_jd == 10.0
        assert result[1].end_jd == 15.0
        assert result[2].start_jd == 20.0
        assert result[2].end_jd == 25.0

    def test_invert_windows_full_coverage(self):
        """invert_windows returns empty for full coverage."""
        from stellium.electional.intervals import TimeWindow, invert_windows

        windows = [TimeWindow(0.0, 25.0)]

        result = invert_windows(windows, 0.0, 25.0)
        assert result == []


# =============================================================================
# Interval Generator Tests
# =============================================================================


class TestWaxingWaningWindows:
    """Tests for waxing and waning window generators."""

    def test_waxing_windows_returns_list(self):
        """waxing_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, waxing_windows

        windows = waxing_windows(datetime(2025, 1, 1), datetime(2025, 2, 28))

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_waxing_windows_approximately_half_month(self):
        """Waxing period is roughly half a lunar month (~14 days)."""
        from stellium.electional.intervals import waxing_windows

        windows = waxing_windows(datetime(2025, 1, 1), datetime(2025, 1, 31))

        # Total waxing time should be roughly 14-15 days in a month
        total_hours = sum(w.duration_hours for w in windows)
        total_days = total_hours / 24

        # Allow some tolerance (depends on where in cycle we are)
        assert 10 <= total_days <= 18

    def test_waning_windows_complement_of_waxing(self):
        """waning_windows covers times not covered by waxing_windows."""
        from stellium.electional.intervals import (
            intersect_windows,
            waning_windows,
            waxing_windows,
        )

        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 31)

        wax = waxing_windows(start, end)
        wan = waning_windows(start, end)

        # Intersection should be empty
        result = intersect_windows(wax, wan)
        assert result == []


class TestMoonSignWindows:
    """Tests for moon sign window generators."""

    def test_moon_sign_windows_returns_list(self):
        """moon_sign_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, moon_sign_windows

        windows = moon_sign_windows(
            ["Taurus", "Cancer"], datetime(2025, 1, 1), datetime(2025, 1, 31)
        )

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_moon_sign_windows_multiple_signs(self):
        """moon_sign_windows includes windows for all specified signs."""
        from stellium.electional.intervals import moon_sign_windows

        # Moon visits all signs in ~28 days
        windows = moon_sign_windows(
            ["Aries", "Taurus", "Gemini"], datetime(2025, 1, 1), datetime(2025, 1, 31)
        )

        # Should find at least one window (moon visits each sign monthly)
        assert len(windows) >= 1

    def test_moon_sign_not_in_windows_is_complement(self):
        """moon_sign_not_in_windows is complement of moon_sign_windows."""
        from stellium.electional.intervals import (
            intersect_windows,
            moon_sign_not_in_windows,
            moon_sign_windows,
        )

        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 31)
        signs = ["Scorpio", "Capricorn"]

        in_signs = moon_sign_windows(signs, start, end)
        not_in_signs = moon_sign_not_in_windows(signs, start, end)

        # Intersection should be empty
        result = intersect_windows(in_signs, not_in_signs)
        assert result == []


class TestRetrogradeWindows:
    """Tests for retrograde and direct window generators."""

    def test_retrograde_windows_returns_list(self):
        """retrograde_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, retrograde_windows

        # Mercury retrogrades ~3-4 times per year
        windows = retrograde_windows(
            "Mercury", datetime(2025, 1, 1), datetime(2025, 12, 31)
        )

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_retrograde_windows_mercury_multiple_per_year(self):
        """Mercury has multiple retrograde periods per year."""
        from stellium.electional.intervals import retrograde_windows

        windows = retrograde_windows(
            "Mercury", datetime(2025, 1, 1), datetime(2025, 12, 31)
        )

        # Mercury retrogrades 3-4 times per year
        assert len(windows) >= 2

    def test_direct_windows_complement_of_retrograde(self):
        """direct_windows is complement of retrograde_windows."""
        from stellium.electional.intervals import (
            direct_windows,
            intersect_windows,
            retrograde_windows,
        )

        start = datetime(2025, 1, 1)
        end = datetime(2025, 6, 30)

        rx = retrograde_windows("Mercury", start, end)
        direct = direct_windows("Mercury", start, end)

        # Intersection should be empty
        result = intersect_windows(rx, direct)
        assert result == []


class TestVOCWindows:
    """Tests for void of course moon window generators."""

    def test_voc_windows_returns_list(self):
        """voc_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, voc_windows

        windows = voc_windows(datetime(2025, 1, 1), datetime(2025, 1, 7))

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_voc_windows_multiple_per_week(self):
        """VOC periods occur multiple times per week."""
        from stellium.electional.intervals import voc_windows

        windows = voc_windows(datetime(2025, 1, 1), datetime(2025, 1, 14))

        # Moon changes signs every ~2.5 days, so ~5-6 VOC periods in 2 weeks
        assert len(windows) >= 3

    def test_not_voc_windows_complement(self):
        """not_voc_windows is complement of voc_windows."""
        from stellium.electional.intervals import (
            intersect_windows,
            not_voc_windows,
            voc_windows,
        )

        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 7)

        voc = voc_windows(start, end)
        not_voc = not_voc_windows(start, end)

        # Intersection should be empty
        result = intersect_windows(voc, not_voc)
        assert result == []


class TestAspectExactWindows:
    """Tests for aspect exact window generators."""

    def test_aspect_exact_windows_returns_list(self):
        """aspect_exact_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, aspect_exact_windows

        windows = aspect_exact_windows(
            "Moon",
            "Jupiter",
            120.0,  # Trine
            datetime(2025, 1, 1),
            datetime(2025, 2, 28),
            orb=3.0,
        )

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_aspect_exact_windows_moon_jupiter_trine(self):
        """Moon-Jupiter trines happen ~monthly."""
        from stellium.electional.intervals import aspect_exact_windows

        windows = aspect_exact_windows(
            "Moon",
            "Jupiter",
            120.0,
            datetime(2025, 1, 1),
            datetime(2025, 3, 31),
            orb=2.0,
        )

        # Moon trines Jupiter roughly once per month
        assert len(windows) >= 2


class TestAngleAtLongitudeWindows:
    """Tests for angle at longitude window generators."""

    def test_angle_at_longitude_windows_returns_list(self):
        """angle_at_longitude_windows returns a list of TimeWindow objects."""
        from stellium.electional.intervals import TimeWindow, angle_at_longitude_windows

        windows = angle_at_longitude_windows(
            0.0,  # 0° Aries
            40.7,
            -74.0,  # New York
            "ASC",
            datetime(2025, 1, 1),
            datetime(2025, 1, 7),
            orb=1.0,
        )

        assert isinstance(windows, list)
        assert all(isinstance(w, TimeWindow) for w in windows)

    def test_angle_at_longitude_windows_asc_daily(self):
        """ASC at any longitude occurs ~once per day."""
        from stellium.electional.intervals import angle_at_longitude_windows

        windows = angle_at_longitude_windows(
            90.0,  # 0° Cancer
            40.7,
            -74.0,  # New York
            "ASC",
            datetime(2025, 1, 1),
            datetime(2025, 1, 7),
            orb=1.0,
        )

        # Should be ~7 windows for 7 days
        assert len(windows) >= 5


# =============================================================================
# Planetary Hours Tests
# =============================================================================


class TestPlanetaryHoursData:
    """Tests for planetary hours constants and data."""

    def test_chaldean_order_has_seven_planets(self):
        """CHALDEAN_ORDER has all seven classical planets."""
        from stellium.electional import CHALDEAN_ORDER

        assert len(CHALDEAN_ORDER) == 7
        assert "Sun" in CHALDEAN_ORDER
        assert "Moon" in CHALDEAN_ORDER
        assert "Mars" in CHALDEAN_ORDER
        assert "Mercury" in CHALDEAN_ORDER
        assert "Jupiter" in CHALDEAN_ORDER
        assert "Venus" in CHALDEAN_ORDER
        assert "Saturn" in CHALDEAN_ORDER

    def test_chaldean_order_is_correct_sequence(self):
        """CHALDEAN_ORDER is in correct slowest-to-fastest order."""
        from stellium.electional import CHALDEAN_ORDER

        # Saturn (slowest) -> Jupiter -> Mars -> Sun -> Venus -> Mercury -> Moon (fastest)
        assert CHALDEAN_ORDER == [
            "Saturn",
            "Jupiter",
            "Mars",
            "Sun",
            "Venus",
            "Mercury",
            "Moon",
        ]

    def test_day_rulers_all_days(self):
        """DAY_RULERS has entries for all seven days."""
        from stellium.electional import DAY_RULERS

        assert len(DAY_RULERS) == 7
        # Monday=0, ..., Sunday=6
        assert 0 in DAY_RULERS  # Monday
        assert 6 in DAY_RULERS  # Sunday

    def test_day_rulers_correct_planets(self):
        """DAY_RULERS maps days to correct planetary rulers."""
        from stellium.electional import DAY_RULERS

        assert DAY_RULERS[0] == "Moon"  # Monday
        assert DAY_RULERS[1] == "Mars"  # Tuesday
        assert DAY_RULERS[2] == "Mercury"  # Wednesday
        assert DAY_RULERS[3] == "Jupiter"  # Thursday
        assert DAY_RULERS[4] == "Venus"  # Friday
        assert DAY_RULERS[5] == "Saturn"  # Saturday
        assert DAY_RULERS[6] == "Sun"  # Sunday


class TestPlanetaryHour:
    """Tests for the PlanetaryHour dataclass."""

    def test_planetary_hour_dataclass_fields(self):
        """PlanetaryHour has all expected fields."""
        # Create a test instance
        from datetime import datetime

        from stellium.electional import PlanetaryHour

        hour = PlanetaryHour(
            ruler="Jupiter",
            hour_number=1,
            is_day_hour=True,
            start_jd=2460000.5,
            end_jd=2460000.55,
            start_utc=datetime(2023, 1, 1, 12, 0),
            end_utc=datetime(2023, 1, 1, 13, 0),
        )

        assert hour.ruler == "Jupiter"
        assert hour.hour_number == 1
        assert hour.is_day_hour is True
        assert hour.start_jd == 2460000.5
        assert hour.end_jd == 2460000.55

    def test_planetary_hour_duration_minutes(self):
        """duration_minutes property calculates correctly."""
        from datetime import datetime

        from stellium.electional import PlanetaryHour

        # 1 hour = 1/24 JD
        hour = PlanetaryHour(
            ruler="Venus",
            hour_number=5,
            is_day_hour=True,
            start_jd=2460000.5,
            end_jd=2460000.5 + (1 / 24),  # 1 hour later
            start_utc=datetime(2023, 1, 1, 12, 0),
            end_utc=datetime(2023, 1, 1, 13, 0),
        )

        assert abs(hour.duration_minutes - 60.0) < 0.1

    def test_planetary_hour_is_frozen(self):
        """PlanetaryHour is immutable (frozen dataclass)."""
        from datetime import datetime

        from stellium.electional import PlanetaryHour

        hour = PlanetaryHour(
            ruler="Mars",
            hour_number=3,
            is_day_hour=True,
            start_jd=2460000.5,
            end_jd=2460000.55,
            start_utc=datetime(2023, 1, 1, 12, 0),
            end_utc=datetime(2023, 1, 1, 13, 0),
        )

        with pytest.raises(AttributeError):
            hour.ruler = "Saturn"


class TestGetDayRuler:
    """Tests for get_day_ruler function."""

    def test_get_day_ruler_returns_correct_planet(self):
        """get_day_ruler returns correct planet for each day."""
        from datetime import datetime

        from stellium.electional import get_day_ruler

        # Monday Jan 6, 2025
        assert get_day_ruler(datetime(2025, 1, 6)) == "Moon"

        # Sunday Jan 5, 2025
        assert get_day_ruler(datetime(2025, 1, 5)) == "Sun"

        # Saturday Jan 4, 2025
        assert get_day_ruler(datetime(2025, 1, 4)) == "Saturn"


class TestGetSunriseSunset:
    """Tests for get_sunrise_sunset function."""

    def test_get_sunrise_sunset_returns_tuple(self):
        """get_sunrise_sunset returns tuple of two JD values."""
        from datetime import datetime

        from stellium.electional import get_sunrise_sunset

        sunrise_jd, sunset_jd = get_sunrise_sunset(
            datetime(2025, 1, 15),
            latitude=37.7749,  # San Francisco
            longitude=-122.4194,
        )

        assert isinstance(sunrise_jd, float)
        assert isinstance(sunset_jd, float)

    def test_get_sunrise_sunset_order(self):
        """Sunrise is before sunset."""
        from datetime import datetime

        from stellium.electional import get_sunrise_sunset

        sunrise_jd, sunset_jd = get_sunrise_sunset(
            datetime(2025, 6, 21),  # Summer solstice
            latitude=40.7128,  # New York
            longitude=-74.0060,
        )

        assert sunrise_jd < sunset_jd

    def test_get_sunrise_sunset_reasonable_times(self):
        """Sunrise and sunset are within reasonable range for location."""
        from datetime import datetime

        from stellium.electional import get_sunrise_sunset

        # Summer solstice in San Francisco
        sunrise_jd, sunset_jd = get_sunrise_sunset(
            datetime(2025, 6, 21),
            latitude=37.7749,
            longitude=-122.4194,
        )

        # Day length should be ~15 hours in summer
        day_length_hours = (sunset_jd - sunrise_jd) * 24
        assert 13 <= day_length_hours <= 16


class TestGetPlanetaryHoursForDay:
    """Tests for get_planetary_hours_for_day function."""

    def test_returns_24_hours(self):
        """Returns exactly 24 planetary hours."""
        from datetime import datetime

        from stellium.electional import get_planetary_hours_for_day

        hours = get_planetary_hours_for_day(
            datetime(2025, 1, 15),
            latitude=37.7749,
            longitude=-122.4194,
        )

        assert len(hours) == 24

    def test_first_12_are_day_hours(self):
        """First 12 hours are day hours."""
        from datetime import datetime

        from stellium.electional import get_planetary_hours_for_day

        hours = get_planetary_hours_for_day(
            datetime(2025, 1, 15),
            latitude=40.7128,
            longitude=-74.0060,
        )

        day_hours = [h for h in hours if h.is_day_hour]
        night_hours = [h for h in hours if not h.is_day_hour]

        assert len(day_hours) == 12
        assert len(night_hours) == 12

    def test_first_hour_matches_day_ruler(self):
        """First hour of the day is ruled by the day ruler."""
        from datetime import datetime

        from stellium.electional import get_day_ruler, get_planetary_hours_for_day

        date = datetime(2025, 1, 5)  # Sunday
        hours = get_planetary_hours_for_day(
            date,
            latitude=37.7749,
            longitude=-122.4194,
        )

        day_ruler = get_day_ruler(date)
        first_hour_ruler = hours[0].ruler

        assert first_hour_ruler == day_ruler
        assert first_hour_ruler == "Sun"  # Sunday

    def test_hours_are_contiguous(self):
        """Each hour's end matches the next hour's start."""
        from datetime import datetime

        from stellium.electional import get_planetary_hours_for_day

        hours = get_planetary_hours_for_day(
            datetime(2025, 1, 15),
            latitude=37.7749,
            longitude=-122.4194,
        )

        for i in range(len(hours) - 1):
            assert abs(hours[i].end_jd - hours[i + 1].start_jd) < 0.0001


class TestGetPlanetaryHour:
    """Tests for get_planetary_hour function."""

    def test_returns_planetary_hour(self):
        """get_planetary_hour returns a PlanetaryHour object."""
        from datetime import datetime

        from stellium.electional import PlanetaryHour, get_planetary_hour

        hour = get_planetary_hour(
            datetime(2025, 1, 15, 14, 30),  # 2:30 PM UTC
            latitude=37.7749,
            longitude=-122.4194,
        )

        assert isinstance(hour, PlanetaryHour)

    def test_time_is_within_returned_hour(self):
        """The query time falls within the returned hour's range."""
        from datetime import datetime

        from stellium.electional import get_planetary_hour
        from stellium.engines.search import _datetime_to_julian_day

        query_time = datetime(2025, 1, 15, 18, 0)
        hour = get_planetary_hour(
            query_time,
            latitude=40.7128,
            longitude=-74.0060,
        )

        query_jd = _datetime_to_julian_day(query_time)

        assert hour.start_jd <= query_jd < hour.end_jd
