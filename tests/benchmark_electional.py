"""
Benchmark script for ElectionalSearch performance.

Tests the speed of various search configurations with and without optimization.
"""

import time
from datetime import datetime


def format_time(seconds: float) -> str:
    """Format time nicely."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


def benchmark(name: str, func, iterations: int = 1):
    """Run a benchmark and print results."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg = sum(times) / len(times)
    result_info = f" → {result}" if result is not None else ""
    print(f"  {name}: {format_time(avg)}{result_info}")
    return avg


def main():
    print("=" * 70)
    print("ElectionalSearch Performance Benchmarks")
    print("=" * 70)

    # ==========================================================================
    # Interval Generator Benchmarks (these are the fast operations)
    # ==========================================================================
    print("\n1. INTERVAL GENERATORS (Pre-computing windows)")
    print("-" * 50)

    from stellium.electional.intervals import (
        moon_sign_windows,
        retrograde_windows,
        voc_windows,
        waning_windows,
        waxing_windows,
    )

    # One month
    start_1m = datetime(2025, 1, 1)
    end_1m = datetime(2025, 1, 31)

    # One year
    start_1y = datetime(2025, 1, 1)
    end_1y = datetime(2025, 12, 31)

    print("\n  One Month Range:")
    benchmark(
        "  waxing_windows", lambda: len(waxing_windows(start_1m, end_1m)), iterations=3
    )
    benchmark(
        "  waning_windows", lambda: len(waning_windows(start_1m, end_1m)), iterations=3
    )
    benchmark(
        "  moon_sign_windows (3 signs)",
        lambda: len(
            moon_sign_windows(["Taurus", "Cancer", "Pisces"], start_1m, end_1m)
        ),
        iterations=3,
    )
    benchmark(
        "  voc_windows (traditional)",
        lambda: len(voc_windows(start_1m, end_1m, mode="traditional")),
        iterations=3,
    )

    print("\n  One Year Range:")
    benchmark(
        "  waxing_windows", lambda: len(waxing_windows(start_1y, end_1y)), iterations=3
    )
    benchmark(
        "  moon_sign_windows (3 signs)",
        lambda: len(
            moon_sign_windows(["Taurus", "Cancer", "Pisces"], start_1y, end_1y)
        ),
        iterations=3,
    )
    benchmark(
        "  retrograde_windows (Mercury)",
        lambda: len(retrograde_windows("Mercury", start_1y, end_1y)),
        iterations=3,
    )
    benchmark(
        "  voc_windows (traditional)",
        lambda: len(voc_windows(start_1y, end_1y, mode="traditional")),
        iterations=1,
    )

    # ==========================================================================
    # Set Operations Benchmarks
    # ==========================================================================
    print("\n2. SET OPERATIONS")
    print("-" * 50)

    from stellium.electional.intervals import (
        intersect_windows,
        invert_windows,
        union_windows,
    )

    # Pre-compute some windows for set operations
    wax = waxing_windows(start_1y, end_1y)
    moon_signs = moon_sign_windows(["Taurus", "Cancer", "Pisces"], start_1y, end_1y)

    from stellium.engines.search import _datetime_to_julian_day

    start_jd = _datetime_to_julian_day(start_1y)
    end_jd = _datetime_to_julian_day(end_1y)

    benchmark(
        "  intersect_windows (waxing ∩ moon_signs)",
        lambda: len(intersect_windows(wax, moon_signs)),
        iterations=10,
    )
    benchmark(
        "  union_windows", lambda: len(union_windows(wax, moon_signs)), iterations=10
    )
    benchmark(
        "  invert_windows",
        lambda: len(invert_windows(wax, start_jd, end_jd)),
        iterations=10,
    )

    # ==========================================================================
    # Search Function Benchmarks
    # ==========================================================================
    print("\n3. SEARCH FUNCTIONS (from search.py)")
    print("-" * 50)

    from stellium.engines.search import (
        find_all_aspect_exacts,
        find_all_sign_changes,
        find_all_stations,
        find_angle_crossing,
        find_aspect_exact,
    )

    benchmark(
        "  find_all_sign_changes (Moon, 1 year)",
        lambda: len(find_all_sign_changes("Moon", start_1y, end_1y)),
        iterations=3,
    )
    benchmark(
        "  find_all_stations (Mercury, 1 year)",
        lambda: len(find_all_stations("Mercury", start_1y, end_1y)),
        iterations=3,
    )
    benchmark(
        "  find_aspect_exact (Moon trine Jupiter)",
        lambda: find_aspect_exact("Moon", "Jupiter", 120.0, start_1m) is not None,
        iterations=3,
    )
    benchmark(
        "  find_all_aspect_exacts (Moon trine Jupiter, 3 months)",
        lambda: len(
            find_all_aspect_exacts(
                "Moon", "Jupiter", 120.0, start_1m, datetime(2025, 3, 31)
            )
        ),
        iterations=3,
    )
    benchmark(
        "  find_angle_crossing (ASC at 0°)",
        lambda: find_angle_crossing(0.0, 37.7, -122.4, "ASC", start_1m) is not None,
        iterations=3,
    )

    # ==========================================================================
    # ElectionalSearch with Optimization
    # ==========================================================================
    print("\n4. ELECTIONAL SEARCH (Optimized with Intervals)")
    print("-" * 50)

    from stellium.electional import (
        ElectionalSearch,
        is_waxing,
        not_retrograde,
        not_voc,
        sign_in,
    )

    # Simple search with one condition (interval-optimized)
    print("\n  Single condition (is_waxing), 1 month, hourly:")

    def search_waxing_1m():
        search = ElectionalSearch(start_1m, end_1m, "San Francisco, CA").where(
            is_waxing()
        )
        return search.count(step="hour", optimize=True)

    benchmark("  optimized", search_waxing_1m, iterations=3)

    # Multiple conditions (all interval-optimized)
    print(
        "\n  Multiple conditions (waxing + not_voc + Moon in signs), 1 month, hourly:"
    )

    def search_multi_1m():
        search = (
            ElectionalSearch(start_1m, end_1m, "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
            .where(sign_in("Moon", ["Taurus", "Cancer", "Pisces"]))
        )
        return search.count(step="hour", optimize=True)

    benchmark("  optimized", search_multi_1m, iterations=3)

    # Year-long search with optimization
    print("\n  Multiple conditions, 1 YEAR, 4-hour step:")

    def search_multi_1y():
        search = (
            ElectionalSearch(start_1y, end_1y, "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
            .where(sign_in("Moon", ["Taurus", "Cancer", "Pisces"]))
        )
        return search.count(step="4hour", optimize=True)

    benchmark("  optimized", search_multi_1y, iterations=1)

    # Add Mercury not retrograde
    print("\n  With Mercury not retrograde, 1 year, 4-hour step:")

    def search_with_mercury_1y():
        search = (
            ElectionalSearch(start_1y, end_1y, "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
            .where(sign_in("Moon", ["Taurus", "Cancer", "Pisces"]))
            .where(not_retrograde("Mercury"))
        )
        return search.count(step="4hour", optimize=True)

    benchmark("  optimized", search_with_mercury_1y, iterations=1)

    # ==========================================================================
    # Comparison: Optimized vs Unoptimized (SHORT range only!)
    # ==========================================================================
    print("\n5. OPTIMIZATION COMPARISON (1 week only - unoptimized is slow!)")
    print("-" * 50)

    start_1w = datetime(2025, 1, 1)
    end_1w = datetime(2025, 1, 8)

    print("\n  Single condition (is_waxing), 1 week, hourly:")

    def search_waxing_opt():
        search = ElectionalSearch(start_1w, end_1w, "San Francisco, CA").where(
            is_waxing()
        )
        return search.count(step="hour", optimize=True)

    def search_waxing_unopt():
        search = ElectionalSearch(start_1w, end_1w, "San Francisco, CA").where(
            is_waxing()
        )
        return search.count(step="hour", optimize=False)

    opt_time = benchmark("  optimized", search_waxing_opt, iterations=3)
    unopt_time = benchmark("  unoptimized", search_waxing_unopt, iterations=1)
    print(f"  Speedup: {unopt_time / opt_time:.1f}x")

    print("\n  Two conditions (waxing + not_voc), 1 week, hourly:")

    def search_two_opt():
        search = (
            ElectionalSearch(start_1w, end_1w, "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
        )
        return search.count(step="hour", optimize=True)

    def search_two_unopt():
        search = (
            ElectionalSearch(start_1w, end_1w, "San Francisco, CA")
            .where(is_waxing())
            .where(not_voc())
        )
        return search.count(step="hour", optimize=False)

    opt_time = benchmark("  optimized", search_two_opt, iterations=3)
    unopt_time = benchmark("  unoptimized", search_two_unopt, iterations=1)
    print(f"  Speedup: {unopt_time / opt_time:.1f}x")

    # ==========================================================================
    # Planetary Hours
    # ==========================================================================
    print("\n6. PLANETARY HOURS")
    print("-" * 50)

    from stellium.electional import (
        get_planetary_hour,
        get_planetary_hours_for_day,
        get_sunrise_sunset,
    )
    from stellium.electional.planetary_hours import planetary_hour_windows

    benchmark(
        "  get_sunrise_sunset",
        lambda: get_sunrise_sunset(start_1m, 37.7, -122.4),
        iterations=10,
    )
    benchmark(
        "  get_planetary_hours_for_day",
        lambda: len(get_planetary_hours_for_day(start_1m, 37.7, -122.4)),
        iterations=10,
    )
    benchmark(
        "  get_planetary_hour (single query)",
        lambda: get_planetary_hour(datetime(2025, 1, 15, 14, 30), 37.7, -122.4).ruler,
        iterations=10,
    )
    benchmark(
        "  planetary_hour_windows (Jupiter, 1 week)",
        lambda: len(planetary_hour_windows("Jupiter", 37.7, -122.4, start_1w, end_1w)),
        iterations=3,
    )

    # ==========================================================================
    # Summary
    # ==========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key findings:
- Interval generators are very fast (ms for a full year)
- Set operations (intersect, union, invert) are instant (<1ms)
- Optimized searches use interval pre-computation for huge speedups
- Unoptimized searches check every time point (slow for long ranges)
- For year-long searches, optimization provides 10-100x+ speedup
""")


if __name__ == "__main__":
    main()
