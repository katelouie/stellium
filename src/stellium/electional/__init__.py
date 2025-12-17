"""
Electional Astrology Search Engine.

Find auspicious times by searching for moments that match astrological conditions.
Uses hierarchical filtering for performance and integrates with existing Stellium
infrastructure (VOC, dignities, aspects, phases, house placements).

Core Concepts:
    - **Condition**: A callable that takes a CalculatedChart and returns bool
    - **Composition**: `all_of()`, `any_of()`, `not_()` combine conditions
    - **Search**: ElectionalSearch finds times matching conditions

Example with lambdas (no imports needed):

    >>> from stellium.electional import ElectionalSearch
    >>> search = ElectionalSearch("2025-01-01", "2025-06-30", "San Francisco, CA")
    >>> results = (search
    ...     .where(lambda c: c.get_object("Moon").phase.is_waxing)
    ...     .where(lambda c: not c.voc_moon().is_void)
    ...     .find_windows())

Example with helper predicates:

    >>> from stellium.electional import ElectionalSearch, is_waxing, not_voc, on_angle
    >>> results = (ElectionalSearch("2025-01-01", "2025-12-31", "New York, NY")
    ...     .where(is_waxing())
    ...     .where(not_voc())
    ...     .where(on_angle("Jupiter"))
    ...     .find_moments(max_results=50))
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from stellium.core.builder import ChartBuilder
from stellium.core.models import CalculatedChart, ChartLocation

# Import interval types for optimization
from stellium.electional.intervals import TimeWindow, intersect_windows

# Import planetary hours for re-export
from stellium.electional.planetary_hours import (
    CHALDEAN_ORDER,
    DAY_RULERS,
    PlanetaryHour,
    get_day_ruler,
    get_planetary_hour,
    get_planetary_hours_for_day,
    get_sunrise_sunset,
)

# Import predicates for re-export (allows: from stellium.electional import is_waxing)
from stellium.electional.predicates import (
    SPEED_DAY,
    SPEED_DAY_SIGN,
    SPEED_HOUR,
    SPEED_MINUTE,
    angle_at_degree,
    aspect_applying,
    aspect_exact_within,
    aspect_separating,
    cadent,
    get_speed_hint,
    get_window_generator,
    has_aspect,
    in_house,
    in_planetary_hour,
    is_combust,
    is_debilitated,
    is_dignified,
    is_out_of_bounds,
    is_retrograde,
    is_voc,
    is_waning,
    is_waxing,
    moon_phase,
    no_aspect,
    no_hard_aspect,
    no_malefic_aspect,
    not_combust,
    not_debilitated,
    not_in_house,
    not_out_of_bounds,
    not_retrograde,
    not_voc,
    on_angle,
    sign_in,
    sign_not_in,
    star_on_angle,
    succedent,
)

if TYPE_CHECKING:
    pass

# =============================================================================
# Core Types
# =============================================================================

# The only abstraction needed - same type ChartQuery uses
Condition = Callable[[CalculatedChart], bool]


@dataclass(frozen=True)
class ElectionWindow:
    """A time window where all conditions are met.

    ElectionWindow stores times as naive datetimes representing local time
    for the search location. This is the user-facing result type.

    Note:
        Times are in the local timezone of the search location (as specified
        when creating ElectionalSearch). They are naive datetimes without
        tzinfo attached.

    See Also:
        TimeWindow: Internal type that stores UTC/JD for interval math.

    Attributes:
        start: Start of the window (local time, naive datetime)
        end: End of the window (local time, naive datetime)
        chart: Chart calculated at the start of the window
    """

    start: dt.datetime
    end: dt.datetime
    chart: CalculatedChart

    @property
    def duration(self) -> dt.timedelta:
        """Duration of this window."""
        return self.end - self.start

    @property
    def midpoint(self) -> dt.datetime:
        """Midpoint of this window."""
        return self.start + (self.end - self.start) / 2

    def __str__(self) -> str:
        duration = self.duration
        # Format duration nicely
        if duration.days > 0:
            duration_str = f"{duration.days}d {duration.seconds // 3600}h"
        elif duration.seconds >= 3600:
            duration_str = (
                f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
            )
        else:
            duration_str = f"{duration.seconds // 60}m"

        # Show full end date if different day
        if self.start.date() == self.end.date():
            end_str = self.end.strftime("%H:%M")
        else:
            end_str = self.end.strftime("%Y-%m-%d %H:%M")

        return f"{self.start.strftime('%Y-%m-%d %H:%M')} - {end_str} ({duration_str})"


@dataclass(frozen=True)
class ElectionMoment:
    """A specific moment matching all conditions.

    Attributes:
        datetime: The exact datetime
        chart: The calculated chart at this moment
    """

    datetime: dt.datetime
    chart: CalculatedChart

    def __str__(self) -> str:
        return self.datetime.strftime("%Y-%m-%d %H:%M")


# =============================================================================
# Composition Functions
# =============================================================================


def all_of(*conditions: Condition) -> Condition:
    """All conditions must be true (AND).

    Example:
        >>> combined = all_of(is_waxing(), not_voc(), not_retrograde("Mercury"))
        >>> results = search.where(combined).find_moments()
    """

    def check(chart: CalculatedChart) -> bool:
        return all(cond(chart) for cond in conditions)

    return check


def any_of(*conditions: Condition) -> Condition:
    """At least one condition must be true (OR).

    Example:
        >>> angular = any_of(in_house("Moon", [1]), in_house("Moon", [10]))
        >>> # Equivalent to: Moon in 1st OR Moon in 10th
    """

    def check(chart: CalculatedChart) -> bool:
        return any(cond(chart) for cond in conditions)

    return check


def not_(condition: Condition) -> Condition:
    """Negate a condition (NOT).

    Example:
        >>> not_scorpio = not_(sign_in("Moon", ["Scorpio"]))
        >>> not_voc = not_(is_voc())  # Equivalent to not_voc() helper
    """

    def check(chart: CalculatedChart) -> bool:
        return not condition(chart)

    return check


# =============================================================================
# Time step utilities
# =============================================================================

_STEP_MINUTES = {
    "minute": 1,
    "5min": 5,
    "15min": 15,
    "30min": 30,
    "hour": 60,
    "2hour": 120,
    "4hour": 240,
    "day": 1440,
}


def _parse_datetime(dt_input: dt.datetime | str) -> dt.datetime:
    """Parse datetime from string or pass through datetime."""
    if isinstance(dt_input, dt.datetime):
        return dt_input
    # Try common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return dt.datetime.strptime(dt_input, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse datetime: {dt_input}")


def _time_steps(
    start: dt.datetime,
    end: dt.datetime,
    step: str,
) -> Generator[dt.datetime, None, None]:
    """Generate time steps between start and end."""
    step_minutes = _STEP_MINUTES.get(step, 60)
    delta = dt.timedelta(minutes=step_minutes)
    current = start
    while current <= end:
        yield current
        current += delta


# =============================================================================
# Main Search Class
# =============================================================================


class ElectionalSearch:
    """Find auspicious times matching astrological conditions.

    The search engine accepts conditions (callable filters) and finds times
    within a date range where all conditions are met.

    Conditions can be:
    - Lambda functions: `lambda c: c.get_object("Moon").phase.is_waxing`
    - Helper predicates: `is_waxing()`, `not_voc()`, `on_angle("Jupiter")`
    - Composed conditions: `all_of(cond1, cond2)`, `any_of(cond1, cond2)`, `not_(cond)`

    Example:
        >>> search = ElectionalSearch("2025-01-01", "2025-06-30", "San Francisco, CA")
        >>> results = (search
        ...     .where(lambda c: c.get_object("Moon").phase.is_waxing)
        ...     .where(lambda c: c.get_object("Moon").sign not in ["Scorpio", "Capricorn"])
        ...     .find_windows())

    Attributes:
        start: Search range start
        end: Search range end
        location: Location for chart calculations
    """

    def __init__(
        self,
        start: dt.datetime | str,
        end: dt.datetime | str,
        location: str | ChartLocation,
    ):
        """Initialize search with date range and location.

        Args:
            start: Start of search range (datetime or string like "2025-01-01")
            end: End of search range
            location: Location string (geocoded) or ChartLocation object
        """
        self.start = _parse_datetime(start)
        self.end = _parse_datetime(end)
        self.location = location
        self._conditions: list[Condition] = []
        self._progress_callback: Callable[[int, int], None] | None = None
        # Cache resolved location with timezone for interval optimization
        self._resolved_location: ChartLocation | None = None
        self._timezone_str: str | None = None

    def _get_timezone(self) -> str:
        """Get timezone string for the location, resolving if needed.

        Returns:
            Timezone string like "America/Los_Angeles"
        """
        if self._timezone_str is not None:
            return self._timezone_str

        # Resolve location to get timezone
        if isinstance(self.location, ChartLocation):
            self._timezone_str = self.location.timezone
        else:
            # Use Native class to resolve location string
            from stellium.core.native import Native

            # Create a dummy Native just to resolve location
            native = Native(self.start, self.location)
            self._resolved_location = native.location
            self._timezone_str = native.location.timezone

        return self._timezone_str

    def _local_datetime_to_jd(self, local_dt: dt.datetime) -> float:
        """Convert a naive local datetime to Julian Day.

        This properly handles timezone conversion, treating the naive datetime
        as local time for the search location, then converting to UTC for JD.

        Args:
            local_dt: Naive datetime interpreted as local time

        Returns:
            Julian Day number (UTC-based)
        """
        import pytz

        from stellium.engines.search import _datetime_to_julian_day

        tz_str = self._get_timezone()
        tz = pytz.timezone(tz_str)

        # Localize the naive datetime to the location's timezone
        local_aware = tz.localize(local_dt)

        # Convert to UTC
        utc_dt = local_aware.astimezone(pytz.UTC)

        # Convert UTC datetime to Julian Day
        # _datetime_to_julian_day expects a naive datetime treated as UTC
        return _datetime_to_julian_day(utc_dt.replace(tzinfo=None))

    def where(self, condition: Condition) -> ElectionalSearch:
        """Add a condition that must be met.

        Conditions are combined with AND logic. All conditions must be true
        for a time to be considered valid.

        Args:
            condition: A callable taking CalculatedChart, returning bool

        Returns:
            Self for method chaining
        """
        self._conditions.append(condition)
        return self

    def with_progress(self, callback: Callable[[int, int], None]) -> ElectionalSearch:
        """Set a progress callback for long searches.

        Args:
            callback: Function called with (current_step, total_steps)

        Returns:
            Self for method chaining
        """
        self._progress_callback = callback
        return self

    def _calculate_chart(self, when: dt.datetime) -> CalculatedChart:
        """Calculate a chart at the given datetime."""
        # Use ChartBuilder.from_details for flexible input handling
        return (
            ChartBuilder.from_details(when, self.location)
            .with_aspects()  # Need aspects for aspect conditions
            .calculate()
        )

    def _check_conditions(self, chart: CalculatedChart) -> bool:
        """Check if all conditions pass for this chart."""
        return all(cond(chart) for cond in self._conditions)

    def _categorize_conditions(
        self,
    ) -> tuple[list[Condition], list[Condition], list[Condition]]:
        """Categorize conditions by speed for hierarchical filtering.

        Returns:
            Tuple of (day_conditions, day_sign_conditions, other_conditions)
            - day_conditions: Check at noon, skip day if fails (phase, retrograde)
            - day_sign_conditions: Check at start+end, skip if BOTH fail (sign-based)
            - other_conditions: Check at every step (hour/minute level)
        """
        day_conditions: list[Condition] = []
        day_sign_conditions: list[Condition] = []
        other_conditions: list[Condition] = []

        for cond in self._conditions:
            speed = get_speed_hint(cond)
            if speed == SPEED_DAY:
                day_conditions.append(cond)
            elif speed == SPEED_DAY_SIGN:
                day_sign_conditions.append(cond)
            else:
                other_conditions.append(cond)

        return day_conditions, day_sign_conditions, other_conditions

    def _get_valid_windows(
        self,
    ) -> tuple[list[TimeWindow] | None, list[Condition]]:
        """Compute valid windows by intersecting interval-based conditions.

        For conditions that have window generators, pre-compute windows where
        they are true and intersect them. This is much faster than point-checking.

        Returns:
            Tuple of (valid_windows, remaining_conditions):
            - valid_windows: List of TimeWindow objects, or None if no interval optimization
            - remaining_conditions: Conditions without window generators that must still be checked
        """
        # Separate conditions with and without window generators
        window_generators = []
        remaining_conditions = []

        for cond in self._conditions:
            gen = get_window_generator(cond)
            if gen is not None:
                window_generators.append(gen)
            else:
                remaining_conditions.append(cond)

        # If no conditions have window generators, can't optimize
        if not window_generators:
            return None, self._conditions

        # Convert local datetimes to JD once, properly handling timezone
        start_jd = self._local_datetime_to_jd(self.start)
        end_jd = self._local_datetime_to_jd(self.end)

        # Start with first generator's windows (pass JD floats)
        result = window_generators[0](start_jd, end_jd)

        # Intersect with each subsequent generator's windows
        for gen in window_generators[1:]:
            windows = gen(start_jd, end_jd)
            result = intersect_windows(result, windows)

            # If intersection is empty, we're done
            if not result:
                return [], remaining_conditions

        return result, remaining_conditions

    def _is_in_valid_windows(
        self, when: dt.datetime, windows: list[TimeWindow]
    ) -> bool:
        """Check if a datetime falls within any of the valid windows.

        Uses binary search for efficiency.
        """
        jd = self._local_datetime_to_jd(when)

        # Binary search for the window that could contain this time
        # We want the first window where end_jd >= jd (could contain jd)
        lo, hi = 0, len(windows)
        while lo < hi:
            mid = (lo + hi) // 2
            # Use < instead of <= to handle endpoint inclusion correctly
            if windows[mid].end_jd < jd:
                lo = mid + 1
            else:
                hi = mid

        # Check if we're in the window at position lo
        # Use <= for end to include the endpoint (consistent with _time_steps)
        if lo < len(windows) and windows[lo].start_jd <= jd <= windows[lo].end_jd:
            return True

        return False

    def _get_passing_days(
        self,
        day_conditions: list[Condition],
        day_sign_conditions: list[Condition],
    ) -> set[dt.date]:
        """Pre-filter days using day-level conditions.

        For SPEED_DAY conditions: Check at start, noon, AND end of day.
            Only skip if ALL THREE fail (handles mid-day retrograde stations).
        For SPEED_DAY_SIGN conditions: Check start+end of day, skip if BOTH fail.

        Returns:
            Set of dates that pass day-level filtering
        """
        passing_days: set[dt.date] = set()

        # Generate all days in range
        current_date = self.start.date()
        end_date = self.end.date()

        while current_date <= end_date:
            day_passes = True

            # Check SPEED_DAY conditions at start, noon, AND end of day
            # Only skip if ALL THREE fail (handles mid-day phase/retrograde changes)
            if day_conditions:
                start_of_day = dt.datetime.combine(current_date, dt.time(0, 0))
                noon = dt.datetime.combine(current_date, dt.time(12, 0))
                end_of_day = dt.datetime.combine(current_date, dt.time(23, 59))

                day_passes_start = False
                day_passes_noon = False
                day_passes_end = False

                try:
                    start_chart = self._calculate_chart(start_of_day)
                    day_passes_start = all(cond(start_chart) for cond in day_conditions)
                except Exception:
                    pass

                try:
                    noon_chart = self._calculate_chart(noon)
                    day_passes_noon = all(cond(noon_chart) for cond in day_conditions)
                except Exception:
                    pass

                try:
                    end_chart = self._calculate_chart(end_of_day)
                    day_passes_end = all(cond(end_chart) for cond in day_conditions)
                except Exception:
                    pass

                # Only skip if ALL THREE fail
                if not day_passes_start and not day_passes_noon and not day_passes_end:
                    day_passes = False

            # Check SPEED_DAY_SIGN conditions at start AND end of day
            # Only skip if BOTH fail (conservative - might have valid hours)
            if day_passes and day_sign_conditions:
                start_of_day = dt.datetime.combine(current_date, dt.time(0, 0))
                end_of_day = dt.datetime.combine(current_date, dt.time(23, 59))

                try:
                    start_chart = self._calculate_chart(start_of_day)
                    start_passes = all(
                        cond(start_chart) for cond in day_sign_conditions
                    )
                except Exception:
                    start_passes = False

                try:
                    end_chart = self._calculate_chart(end_of_day)
                    end_passes = all(cond(end_chart) for cond in day_sign_conditions)
                except Exception:
                    end_passes = False

                # Only skip if BOTH fail
                if not start_passes and not end_passes:
                    day_passes = False

            if day_passes:
                passing_days.add(current_date)

            current_date += dt.timedelta(days=1)

        return passing_days

    def find_moments(
        self,
        max_results: int = 100,
        step: Literal[
            "minute", "5min", "15min", "30min", "hour", "2hour", "4hour", "day"
        ] = "hour",
        optimize: bool = True,
    ) -> list[ElectionMoment]:
        """Find specific moments meeting all conditions.

        Uses hierarchical filtering for performance: day-level conditions are
        checked first to skip entire days that can't have valid moments.

        Args:
            max_results: Maximum number of results to return
            step: Time step granularity (default: "hour")
                - "minute": Every minute (slow, use for short ranges)
                - "5min", "15min", "30min": 5/15/30 minute steps
                - "hour": Every hour (good default)
                - "2hour", "4hour": Coarser steps for long ranges
                - "day": Daily (for very long ranges, may miss windows)
            optimize: If True, use hierarchical day-level filtering (default True)

        Returns:
            List of ElectionMoment objects, sorted by datetime
        """
        results: list[ElectionMoment] = []

        # Categorize conditions by speed
        day_conds, day_sign_conds, other_conds = self._categorize_conditions()

        # Pre-filter days if we have day-level conditions and optimization is enabled
        passing_days: set[dt.date] | None = None
        if optimize and (day_conds or day_sign_conds):
            passing_days = self._get_passing_days(day_conds, day_sign_conds)

        # Count total steps for progress (approximate - actual may be less if days skipped)
        step_minutes = _STEP_MINUTES.get(step, 60)
        total_minutes = int((self.end - self.start).total_seconds() / 60)
        total_steps = total_minutes // step_minutes

        step_count = 0
        for when in _time_steps(self.start, self.end, step):
            step_count += 1

            # Progress callback
            if self._progress_callback and step_count % 100 == 0:
                self._progress_callback(step_count, total_steps)

            # Skip if day didn't pass pre-filter
            if passing_days is not None and when.date() not in passing_days:
                continue

            try:
                chart = self._calculate_chart(when)
                if self._check_conditions(chart):
                    results.append(ElectionMoment(datetime=when, chart=chart))
                    if len(results) >= max_results:
                        break
            except Exception:
                # Skip times that fail to calculate (edge cases)
                continue

        return results

    def find_first(
        self,
        step: Literal[
            "minute", "5min", "15min", "30min", "hour", "2hour", "4hour", "day"
        ] = "hour",
    ) -> ElectionMoment | None:
        """Find the first moment meeting all conditions.

        Args:
            step: Time step granularity (see find_moments)

        Returns:
            First matching ElectionMoment, or None if no matches
        """
        results = self.find_moments(max_results=1, step=step)
        return results[0] if results else None

    def find_windows(
        self,
        step: Literal[
            "minute", "5min", "15min", "30min", "hour", "2hour", "4hour", "day"
        ] = "hour",
        min_duration_minutes: int = 0,
        optimize: bool = True,
    ) -> list[ElectionWindow]:
        """Find time windows where all conditions are met.

        Adjacent passing moments are coalesced into windows. This is useful
        for seeing "good periods" rather than individual moments.

        Uses hierarchical filtering for performance: day-level conditions are
        checked first to skip entire days that can't have valid moments.

        Args:
            step: Time step granularity (see find_moments)
            min_duration_minutes: Minimum window duration to include (default 0)
            optimize: If True, use hierarchical day-level filtering (default True)

        Returns:
            List of ElectionWindow objects, sorted by start time
        """
        windows: list[ElectionWindow] = []
        step_delta = dt.timedelta(minutes=_STEP_MINUTES.get(step, 60))

        window_start: dt.datetime | None = None
        window_chart: CalculatedChart | None = None
        last_passing_time: dt.datetime | None = None

        # Categorize conditions by speed
        day_conds, day_sign_conds, _ = self._categorize_conditions()

        # Pre-filter days if we have day-level conditions and optimization is enabled
        passing_days: set[dt.date] | None = None
        if optimize and (day_conds or day_sign_conds):
            passing_days = self._get_passing_days(day_conds, day_sign_conds)

        # Count total steps for progress
        step_minutes = _STEP_MINUTES.get(step, 60)
        total_minutes = int((self.end - self.start).total_seconds() / 60)
        total_steps = total_minutes // step_minutes

        step_count = 0
        for when in _time_steps(self.start, self.end, step):
            step_count += 1

            # Progress callback
            if self._progress_callback and step_count % 100 == 0:
                self._progress_callback(step_count, total_steps)

            # Skip if day didn't pass pre-filter (treat as failing)
            if passing_days is not None and when.date() not in passing_days:
                # Close any open window before skipping
                if window_start is not None and last_passing_time is not None:
                    window_end = last_passing_time + step_delta
                    window = ElectionWindow(
                        start=window_start,
                        end=window_end,
                        chart=window_chart,  # type: ignore
                    )
                    if window.duration.total_seconds() / 60 >= min_duration_minutes:
                        windows.append(window)
                    window_start = None
                    window_chart = None
                    last_passing_time = None
                continue

            try:
                chart = self._calculate_chart(when)
                passes = self._check_conditions(chart)
            except Exception:
                passes = False
                chart = None

            if passes and chart is not None:
                if window_start is None:
                    # Start new window
                    window_start = when
                    window_chart = chart
                last_passing_time = when
            else:
                if window_start is not None and last_passing_time is not None:
                    # Close current window
                    window_end = last_passing_time + step_delta
                    window = ElectionWindow(
                        start=window_start,
                        end=window_end,
                        chart=window_chart,  # type: ignore
                    )
                    if window.duration.total_seconds() / 60 >= min_duration_minutes:
                        windows.append(window)
                    window_start = None
                    window_chart = None
                    last_passing_time = None

        # Handle final window if search ends while passing
        if window_start is not None and last_passing_time is not None:
            window_end = last_passing_time + step_delta
            window = ElectionWindow(
                start=window_start,
                end=window_end,
                chart=window_chart,  # type: ignore
            )
            if window.duration.total_seconds() / 60 >= min_duration_minutes:
                windows.append(window)

        return windows

    def iter_moments(
        self,
        step: Literal[
            "minute", "5min", "15min", "30min", "hour", "2hour", "4hour", "day"
        ] = "hour",
        optimize: bool = True,
    ) -> Generator[ElectionMoment, None, None]:
        """Iterate over moments meeting conditions (memory efficient).

        Unlike find_moments(), this yields results one at a time without
        storing them all in memory. Useful for very long searches.

        Uses interval algebra for performance when optimize=True and predicates
        have window generators attached. Falls back to day-level filtering for
        predicates without window generators.

        Args:
            step: Time step granularity
            optimize: If True, use interval-based optimization (default True)

        Yields:
            ElectionMoment objects as they are found
        """
        # Try interval-based optimization first (fastest)
        valid_windows: list[TimeWindow] | None = None
        remaining_conditions: list[Condition] = self._conditions
        if optimize:
            valid_windows, remaining_conditions = self._get_valid_windows()

        # Fast path: if ALL conditions have window generators and we have valid windows,
        # we can directly iterate windows without calculating charts for checking
        all_conditions_have_windows = len(remaining_conditions) == 0

        # Fall back to day-level pre-filter if interval optimization not available
        passing_days: set[dt.date] | None = None
        if valid_windows is None and optimize:
            day_conds, day_sign_conds, _ = self._categorize_conditions()
            if day_conds or day_sign_conds:
                passing_days = self._get_passing_days(day_conds, day_sign_conds)

        for when in _time_steps(self.start, self.end, step):
            # Skip if outside valid windows (interval optimization)
            if valid_windows is not None:
                if not self._is_in_valid_windows(when, valid_windows):
                    continue

            # Skip if day didn't pass pre-filter (day-level optimization)
            if passing_days is not None and when.date() not in passing_days:
                continue

            try:
                chart = self._calculate_chart(when)
                # If all conditions have windows, we know they're satisfied (we're in the window)
                # Just need to check any remaining conditions without window generators
                if all_conditions_have_windows or all(
                    cond(chart) for cond in remaining_conditions
                ):
                    yield ElectionMoment(datetime=when, chart=chart)
            except Exception:
                continue

    def _count_steps_in_windows(self, windows: list[TimeWindow], step: str) -> int:
        """Fast count of time steps that fall within valid windows.

        This is the O(1) optimization - no chart calculations needed!
        """
        step_minutes = _STEP_MINUTES.get(step, 60)
        step_jd = step_minutes / (24 * 60)  # Convert minutes to JD

        total = 0
        start_jd = self._local_datetime_to_jd(self.start)
        end_jd = self._local_datetime_to_jd(self.end)

        for window in windows:
            # Clip window to search range
            win_start = max(window.start_jd, start_jd)
            win_end = min(window.end_jd, end_jd)

            if win_start >= win_end:
                continue

            # Find first step >= win_start
            # Steps are at: start_jd, start_jd + step_jd, start_jd + 2*step_jd, ...
            # First step >= win_start is at index: ceil((win_start - start_jd) / step_jd)
            steps_to_start = (win_start - start_jd) / step_jd
            first_step_index = int(steps_to_start)
            if first_step_index < steps_to_start:
                first_step_index += 1

            first_step_jd = start_jd + first_step_index * step_jd

            # Count steps from first_step_jd up to and including win_end
            if first_step_jd > win_end:
                continue

            # Last valid step is the largest index such that start_jd + index * step_jd <= win_end
            last_step_index = int((win_end - start_jd) / step_jd)
            last_step_jd = start_jd + last_step_index * step_jd

            # Adjust if last step exceeds win_end (shouldn't happen with int(), but be safe)
            while last_step_jd > win_end and last_step_index >= first_step_index:
                last_step_index -= 1
                last_step_jd = start_jd + last_step_index * step_jd

            if last_step_index >= first_step_index:
                total += last_step_index - first_step_index + 1

        return total

    def count(
        self,
        step: Literal[
            "minute", "5min", "15min", "30min", "hour", "2hour", "4hour", "day"
        ] = "hour",
        optimize: bool = True,
    ) -> int:
        """Count how many moments match conditions (without storing them).

        Uses interval algebra for O(windows) performance when optimize=True and
        all conditions have window generators. Falls back to iteration otherwise.

        Args:
            step: Time step granularity
            optimize: If True, use interval-based optimization (default True)

        Returns:
            Number of matching moments
        """
        if optimize:
            valid_windows, remaining_conditions = self._get_valid_windows()

            # FAST PATH: If all conditions have window generators, just count steps in windows
            if valid_windows is not None and len(remaining_conditions) == 0:
                return self._count_steps_in_windows(valid_windows, step)

        # Slow path: iterate and count
        count = 0
        for _ in self.iter_moments(step=step, optimize=optimize):
            count += 1
        return count

    def __repr__(self) -> str:
        return (
            f"<ElectionalSearch {self.start.date()} to {self.end.date()}, "
            f"{len(self._conditions)} conditions>"
        )


__all__ = [
    # Core types
    "Condition",
    "ElectionWindow",
    "ElectionMoment",
    # Composition
    "all_of",
    "any_of",
    "not_",
    # Main search class
    "ElectionalSearch",
    # Predicates - Moon phase
    "is_waxing",
    "is_waning",
    "moon_phase",
    # Predicates - VOC
    "is_voc",
    "not_voc",
    # Predicates - Sign
    "sign_in",
    "sign_not_in",
    # Predicates - House
    "in_house",
    "not_in_house",
    "on_angle",
    "succedent",
    "cadent",
    # Predicates - Retrograde
    "is_retrograde",
    "not_retrograde",
    # Predicates - Dignity
    "is_dignified",
    "is_debilitated",
    "not_debilitated",
    # Predicates - Aspects
    "aspect_applying",
    "aspect_separating",
    "has_aspect",
    "no_aspect",
    "no_hard_aspect",
    "no_malefic_aspect",
    # Predicates - Aspect exactitude
    "aspect_exact_within",
    # Predicates - Combust
    "is_combust",
    "not_combust",
    # Predicates - Out of bounds
    "is_out_of_bounds",
    "not_out_of_bounds",
    # Predicates - Angles and fixed stars
    "angle_at_degree",
    "star_on_angle",
    # Predicates - Planetary hours
    "in_planetary_hour",
    # Planetary hours utilities
    "PlanetaryHour",
    "CHALDEAN_ORDER",
    "DAY_RULERS",
    "get_planetary_hour",
    "get_planetary_hours_for_day",
    "get_day_ruler",
    "get_sunrise_sunset",
]
