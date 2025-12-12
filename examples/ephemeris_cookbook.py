"""
Graphic Ephemeris Cookbook
==========================

This cookbook demonstrates the GraphicEphemeris visualization, which plots
planetary positions over time. The X-axis shows time, the Y-axis shows
zodiacal position (optionally compressed to 90° or 45° harmonic).

Key features:
- Three harmonic modes: 360° (full zodiac), 90° (hard aspects), 45° (8th harmonic)
- Station markers for retrograde/direct points
- Aspect markers at line crossings
- Optional natal chart overlay with transit-to-natal aspects
- Customizable planet selection (including Chiron and North Node)
"""

from pathlib import Path

from stellium import ChartBuilder
from stellium.visualization import EXTENDED_PLANETS, GraphicEphemeris

# Output directory for all examples
OUTPUT_DIR = Path(__file__).parent / "ephemeris"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# Basic Usage
# =============================================================================


def example_basic_90_harmonic():
    """
    Basic 90° harmonic ephemeris for one year.

    The 90° harmonic compresses the zodiac into 90° segments, so:
    - 0° = Cardinal signs (Aries, Cancer, Libra, Capricorn)
    - 30° = Fixed signs (Taurus, Leo, Scorpio, Aquarius)
    - 60° = Mutable signs (Gemini, Virgo, Sagittarius, Pisces)

    When planet lines cross in this view, they form hard aspects
    (conjunction, square, or opposition).
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
    )
    eph.draw(OUTPUT_DIR / "basic_90_harmonic.svg")
    print(f"Created: {OUTPUT_DIR / 'basic_90_harmonic.svg'}")


def example_basic_45_harmonic():
    """
    45° harmonic ephemeris.

    The 45° harmonic shows semi-squares and sesquiquadrates as conjunctions.
    Useful for tracking stress aspects.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=45,
    )
    eph.draw(OUTPUT_DIR / "basic_45_harmonic.svg")
    print(f"Created: {OUTPUT_DIR / 'basic_45_harmonic.svg'}")


def example_basic_360_full_zodiac():
    """
    Full 360° zodiac ephemeris.

    Shows actual zodiacal positions without harmonic compression.
    Y-axis labels show sign ingresses.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=360,
    )
    eph.draw(OUTPUT_DIR / "basic_360_full_zodiac.svg")
    print(f"Created: {OUTPUT_DIR / 'basic_360_full_zodiac.svg'}")


# =============================================================================
# Multi-Year Views
# =============================================================================


def example_multi_year():
    """
    Multi-year ephemeris for seeing longer cycles.

    Great for tracking outer planet aspects like Jupiter-Saturn,
    Saturn-Uranus, etc.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2027-12-31",
        harmonic=90,
        width=1800,  # Wider to accommodate more time
        height=1000,
    )
    eph.draw(OUTPUT_DIR / "multi_year_2025_2027.svg")
    print(f"Created: {OUTPUT_DIR / 'multi_year_2025_2027.svg'}")


# =============================================================================
# Planet Selection
# =============================================================================


def example_outer_planets_only():
    """
    Show only outer planets for cleaner long-term views.

    Inner planets move too fast for multi-year views,
    so focusing on Jupiter through Pluto shows clearer patterns.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2030-12-31",
        harmonic=90,
        planets=["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
        width=2000,
        height=900,
    )
    eph.draw(OUTPUT_DIR / "outer_planets_2025_2030.svg")
    print(f"Created: {OUTPUT_DIR / 'outer_planets_2025_2030.svg'}")


def example_with_chiron_and_node():
    """
    Include Chiron and North Node using EXTENDED_PLANETS.

    EXTENDED_PLANETS = Sun through Pluto + Chiron + True Node
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        planets=EXTENDED_PLANETS,
        width=1600,
        height=1000,
    )
    eph.draw(OUTPUT_DIR / "extended_planets_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'extended_planets_2025.svg'}")


def example_custom_planet_selection():
    """
    Custom planet selection for specific research.

    Example: Just the social planets and outer planets.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        planets=["Mars", "Jupiter", "Saturn", "Chiron", "Uranus", "Neptune", "Pluto"],
    )
    eph.draw(OUTPUT_DIR / "custom_planets_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'custom_planets_2025.svg'}")


# =============================================================================
# Natal Chart Overlay (Transits)
# =============================================================================


def example_transits_to_natal():
    """
    Transit ephemeris with natal chart overlay.

    When a natal chart is provided:
    - Horizontal dashed lines show natal planet positions
    - Left side shows transit positions at start of period
    - Right side shows natal planet positions
    - Aspect markers show where transits cross natal positions
    - Header shows natal chart info (name, date, location)
    """
    # Create natal chart
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()

    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        natal_chart=natal,
    )
    eph.draw(OUTPUT_DIR / "transits_einstein_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'transits_einstein_2025.svg'}")


def example_transits_custom_natal_planets():
    """
    Transit ephemeris showing only specific natal planets.

    Use natal_planets to filter which natal positions are shown.
    Useful for focusing on personal planets or specific points.
    """
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()

    # Only show transits to natal Sun, Moon, Mercury, Venus, Mars
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        natal_chart=natal,
        natal_planets=["Sun", "Moon", "Mercury", "Venus", "Mars"],
    )
    eph.draw(OUTPUT_DIR / "transits_inner_planets_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'transits_inner_planets_2025.svg'}")


def example_transits_outer_to_natal():
    """
    Show only outer planet transits to natal chart.

    Filters both transit planets AND natal planets for a cleaner view
    of major life transits.
    """
    natal = ChartBuilder.from_notable("Albert Einstein").calculate()

    outer = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2027-12-31",
        harmonic=90,
        planets=outer,  # Transit planets
        natal_chart=natal,
        natal_planets=["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"],
        width=1800,
    )
    eph.draw(OUTPUT_DIR / "outer_transits_einstein_2025_2027.svg")
    print(f"Created: {OUTPUT_DIR / 'outer_transits_einstein_2025_2027.svg'}")


# =============================================================================
# Display Options
# =============================================================================


def example_minimal_display():
    """
    Minimal display with no stations, aspects, or legend.

    Just the planet lines and grid for a cleaner look.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        show_stations=False,
        show_aspects=False,
        show_legend=False,
    )
    eph.draw(OUTPUT_DIR / "minimal_display_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'minimal_display_2025.svg'}")


def example_custom_title():
    """
    Custom title instead of auto-generated.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        title="Planetary Movements - 2025",
    )
    eph.draw(OUTPUT_DIR / "custom_title_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'custom_title_2025.svg'}")


def example_large_format():
    """
    Large format for printing or detailed analysis.
    """
    eph = GraphicEphemeris(
        start_date="2025-01-01",
        end_date="2025-12-31",
        harmonic=90,
        width=2400,
        height=1600,
    )
    eph.draw(OUTPUT_DIR / "large_format_2025.svg")
    print(f"Created: {OUTPUT_DIR / 'large_format_2025.svg'}")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("Graphic Ephemeris Cookbook")
    print("=" * 50)
    print()

    print("Basic Usage:")
    example_basic_90_harmonic()
    example_basic_45_harmonic()
    example_basic_360_full_zodiac()
    print()

    print("Multi-Year Views:")
    example_multi_year()
    print()

    print("Planet Selection:")
    example_outer_planets_only()
    example_with_chiron_and_node()
    example_custom_planet_selection()
    print()

    print("Natal Chart Overlay:")
    example_transits_to_natal()
    example_transits_custom_natal_planets()
    example_transits_outer_to_natal()
    print()

    print("Display Options:")
    example_minimal_display()
    example_custom_title()
    example_large_format()
    print()

    print("=" * 50)
    print(f"All examples saved to: {OUTPUT_DIR}")
