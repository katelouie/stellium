#!/usr/bin/env python3
"""
MultiWheel Chart Examples

Demonstrates 2-4 chart multiwheel visualizations with all charts
rendered concentrically inside the zodiac ring.

Usage:
    python examples/multiwheel/multiwheel_examples.py
"""

from pathlib import Path

from stellium import ChartBuilder, MultiWheelBuilder

# Output directory
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(exist_ok=True)


def example_01_biwheel_basic():
    """Basic 2-chart multiwheel: Natal + Transit."""
    print("Example 01: Basic biwheel (natal + transit)")

    # Create charts
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()
    transit = ChartBuilder.from_notable("Nikola Tesla").calculate()

    # Build multiwheel
    mw = (
        MultiWheelBuilder.from_charts([natal, transit])
        .with_labels(["Einstein (Natal)", "Tesla (Transit)"])
        .calculate()
    )

    # Draw and save
    output = mw.draw(str(OUTPUT_DIR / "01_biwheel_basic.svg")).save()
    print(f"  Saved: {output}")
    return output


def example_02_biwheel_themed():
    """Biwheel with midnight theme."""
    print("Example 02: Biwheel with midnight theme")

    natal = ChartBuilder.from_notable("Marie Curie").calculate()
    transit = ChartBuilder.from_notable("Ada Lovelace").calculate()

    mw = (
        MultiWheelBuilder.from_charts([natal, transit])
        .with_labels(["Curie", "Lovelace"])
        .calculate()
    )

    output = (
        mw.draw(str(OUTPUT_DIR / "02_biwheel_midnight.svg"))
        .with_theme("midnight")
        .save()
    )
    print(f"  Saved: {output}")
    return output


def example_03_triwheel():
    """3-chart multiwheel: Natal + Progressed + Transit."""
    print("Example 03: Triwheel (3 charts)")

    # Use three different notables as stand-ins for natal/progressed/transit
    chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart2 = ChartBuilder.from_notable("Marie Curie").calculate()
    chart3 = ChartBuilder.from_notable("Nikola Tesla").calculate()

    mw = (
        MultiWheelBuilder.from_charts([chart1, chart2, chart3])
        .with_labels(["Natal", "Progressed", "Transit"])
        .calculate()
    )

    output = mw.draw(str(OUTPUT_DIR / "03_triwheel.svg")).save()
    print(f"  Saved: {output}")
    return output


def example_04_quadwheel():
    """4-chart multiwheel: Maximum supported."""
    print("Example 04: Quadwheel (4 charts)")

    chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
    chart2 = ChartBuilder.from_notable("Marie Curie").calculate()
    chart3 = ChartBuilder.from_notable("Nikola Tesla").calculate()
    chart4 = ChartBuilder.from_notable("Ada Lovelace").calculate()

    mw = (
        MultiWheelBuilder.from_charts([chart1, chart2, chart3, chart4])
        .with_labels(["Einstein", "Curie", "Tesla", "Lovelace"])
        .calculate()
    )

    output = mw.draw(str(OUTPUT_DIR / "04_quadwheel.svg")).save()
    print(f"  Saved: {output}")
    return output


def example_05_triwheel_dark():
    """Triwheel with dark theme."""
    print("Example 05: Triwheel with dark theme")

    chart1 = ChartBuilder.from_notable("Wolfgang Mozart").calculate()
    chart2 = ChartBuilder.from_notable("Vincent van Gogh").calculate()
    chart3 = ChartBuilder.from_notable("Frida Kahlo").calculate()

    mw = (
        MultiWheelBuilder.from_charts([chart1, chart2, chart3])
        .with_labels(["Mozart", "Van Gogh", "Kahlo"])
        .calculate()
    )

    output = mw.draw(str(OUTPUT_DIR / "05_triwheel_dark.svg")).with_theme("dark").save()
    print(f"  Saved: {output}")
    return output


def example_06_biwheel_celestial():
    """Biwheel with celestial theme."""
    print("Example 06: Biwheel with celestial theme")

    chart1 = ChartBuilder.from_notable("Vincent van Gogh").calculate()
    chart2 = ChartBuilder.from_notable("Pablo Picasso").calculate()

    mw = (
        MultiWheelBuilder.from_charts([chart1, chart2])
        .with_labels(["Van Gogh", "Picasso"])
        .calculate()
    )

    output = (
        mw.draw(str(OUTPUT_DIR / "06_biwheel_celestial.svg"))
        .with_theme("celestial")
        .save()
    )
    print(f"  Saved: {output}")
    return output


def main():
    """Run all examples."""
    print("=" * 60)
    print("MultiWheel Chart Examples")
    print("=" * 60)
    print()

    examples = [
        example_01_biwheel_basic,
        example_02_biwheel_themed,
        example_03_triwheel,
        example_04_quadwheel,
        example_05_triwheel_dark,
        example_06_biwheel_celestial,
    ]

    outputs = []
    for example in examples:
        try:
            output = example()
            outputs.append(output)
        except Exception as e:
            print(f"  ERROR: {e}")
        print()

    print("=" * 60)
    print(f"Generated {len(outputs)} examples in {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
