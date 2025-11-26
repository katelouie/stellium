"""Performance benchmarks."""

import datetime as dt
import time

import pytz

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine


def benchmark_chart_calculation():
    """Benchmark basic chart calculation."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(birthday, location)

    iterations = 100
    start = time.time()

    for _ in range(iterations):
        _chart = (
            ChartBuilder.from_native(native)
            .with_aspects(ModernAspectEngine())
            .calculate()
        )

    elapsed = time.time() - start
    per_chart = elapsed / iterations

    print("Performance Benchmark")
    print(f"{'=' * 50}")
    print(f"Charts calculated: {iterations}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Per chart: {per_chart * 1000:.2f}ms")
    print(f"Charts/second: {iterations / elapsed:.1f}")
    print(f"{'=' * 50}")

    assert per_chart < 0.5, "Chart calculation should be under 500ms"


if __name__ == "__main__":
    benchmark_chart_calculation()
