"""Example usage of the refactored primary directions engine."""

import datetime as dt

from stellium import ChartBuilder
from stellium.engines.directions import (
    DirectionsEngine,
    DistributionsCalculator,
)


def run_test():
    print("--- PRIMARY DIRECTIONS ENGINE ---")
    print("Loading Chart: Prince Charles...")
    birth = dt.datetime(1948, 11, 14, 21, 14)
    chart = ChartBuilder.from_details(birth, (51.50735, -0.12776)).calculate()

    # 1. BASIC DIRECTION
    print("\n--- ZODIACAL DIRECTIONS (default) ---")
    engine = DirectionsEngine(chart)
    result = engine.direct("Sun", "ASC")
    print(f"Sun to ASC: {result.arc.arc_degrees:.2f} deg = age {result.age:.1f}")
    print(f"  Date: {result.date.strftime('%Y-%m-%d') if result.date else 'N/A'}")

    # 2. COMPARE METHODS
    print("\n--- COMPARING METHODS ---")
    z_engine = DirectionsEngine(chart, method="zodiacal")
    m_engine = DirectionsEngine(chart, method="mundane")

    z_result = z_engine.direct("Sun", "ASC")
    m_result = m_engine.direct("Sun", "ASC")

    print(f"Zodiacal: {z_result.arc.arc_degrees:.2f} deg = age {z_result.age:.1f}")
    print(f"Mundane:  {m_result.arc.arc_degrees:.2f} deg = age {m_result.age:.1f}")

    # 3. DIRECT TO ALL ANGLES
    print("\n--- SUN TO ALL ANGLES (zodiacal) ---")
    angles = engine.direct_to_angles("Sun")
    for angle, res in angles.items():
        if res.age and 0 < res.age < 100:
            print(f"  Sun to {angle}: age {res.age:.1f}")

    # 4. ALL PLANETS TO ASC
    print("\n--- ALL PLANETS TO ASC ---")
    results = engine.direct_all_to("ASC")
    for res in results[:5]:  # Top 5 earliest
        print(f"  {res.arc.promissor} to ASC: age {res.age:.1f}")

    # 5. DISTRIBUTIONS (separate calculator)
    print("\n--- LIFE CHAPTERS (Term Distributions) ---")
    calc = DistributionsCalculator(chart)
    periods = calc.calculate(years=80)

    for p in periods:
        print(
            f"  Age {p.start_age:5.1f} | {p.start_date.strftime('%Y-%m-%d')} | "
            f"{p.sign}: {p.ruler}"
        )

    # 6. COMPARE TIME KEYS
    print("\n--- COMPARE TIME KEYS ---")
    ptolemy = DirectionsEngine(chart, time_key="ptolemy")
    naibod = DirectionsEngine(chart, time_key="naibod")

    p_result = ptolemy.direct("Mars", "ASC")
    n_result = naibod.direct("Mars", "ASC")

    print(f"Mars to ASC (Ptolemy): age {p_result.age:.1f}")
    print(f"Mars to ASC (Naibod):  age {n_result.age:.1f}")


if __name__ == "__main__":
    run_test()
