"""
Planner Cookbook - Recipes for creating personalized astrological planners.

The PlannerBuilder generates beautiful PDF planners with:
- Front matter: natal chart, progressed chart, solar return, profections, graphic ephemeris
- Monthly calendar grids with all events
- Weekly detail pages with daily transit listings

All charts use the rainbow zodiac palette by default.
"""

from pathlib import Path

from stellium import Native, PlannerBuilder

# Output directory for all generated planners
OUTPUT_DIR = Path(__file__).parent / "planners"


def get_output_path(filename: str) -> str:
    """Get the full path for a planner file, creating the directory if needed."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return str(OUTPUT_DIR / filename)


# =============================================================================
# BASIC PLANNER
# =============================================================================


def basic_planner():
    """
    Create a simple planner with default settings.

    Includes natal chart and basic transit info.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        .generate(get_output_path("basic_planner.pdf"))
    )

    print(f"Basic planner: {len(planner):,} bytes")


# =============================================================================
# FULL-FEATURED PLANNER
# =============================================================================


def full_planner():
    """
    Create a comprehensive planner with all features enabled.

    Includes:
    - All front matter (natal, progressed, solar return, profections, ephemeris)
    - All 10 planets + Node + Chiron for transits
    - Moon phases, VOC periods, ingresses, stations
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        # Front matter
        .with_natal_chart()
        .with_progressed_chart()
        .with_solar_return()
        .with_profections()
        .with_graphic_ephemeris(harmonic=90)  # 90° shows hard aspects as conjunctions
        # Daily content - all planets
        .include_natal_transits()  # Default: all planets + Node + Chiron
        .include_moon_phases()
        .include_voc(mode="traditional")
        .include_ingresses(["Sun", "Moon", "Mercury", "Venus", "Mars"])
        .include_stations()  # All planets that station
        # Output
        .generate(get_output_path("full_planner.pdf"))
    )

    print(f"Full planner: {len(planner):,} bytes")


# =============================================================================
# OUTER PLANETS ONLY
# =============================================================================


def outer_planets_planner():
    """
    Create a planner focused on slow-moving outer planet transits.

    Good for seeing major life themes without the noise of fast-moving planets.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        .with_natal_chart()
        .with_graphic_ephemeris(harmonic=360)  # Full zodiac view
        # Only outer planets for transits
        .include_natal_transits(["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])
        .include_moon_phases()
        .include_stations(["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"])
        .generate(get_output_path("outer_planets_planner.pdf"))
    )

    print(f"Outer planets planner: {len(planner):,} bytes")


# =============================================================================
# WEEK STARTS MONDAY
# =============================================================================


def monday_start_planner():
    """
    Create a planner where weeks start on Monday (European style).

    By default, weeks start on Sunday (US style).
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="London, UK",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("Europe/London")
        .week_starts_on("monday")  # Monday-Sunday weeks
        .with_natal_chart()
        .include_natal_transits()
        .include_moon_phases()
        .include_voc(mode="traditional")
        .generate(get_output_path("monday_start_planner.pdf"))
    )

    print(f"Monday-start planner: {len(planner):,} bytes")


# =============================================================================
# CUSTOM DATE RANGE
# =============================================================================


def custom_range_planner():
    """
    Create a planner for a specific date range instead of a full year.

    Useful for project planning, event timing, or partial-year planners.
    """
    from datetime import date

    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .date_range(date(2025, 6, 1), date(2025, 8, 31))  # Summer 2025
        .timezone("America/Los_Angeles")
        .with_natal_chart()
        .include_natal_transits()
        .include_moon_phases()
        .include_voc(mode="traditional")
        .generate(get_output_path("summer_2025_planner.pdf"))
    )

    print(f"Summer planner: {len(planner):,} bytes")


# =============================================================================
# LETTER SIZE WITH BINDING MARGIN
# =============================================================================


def printable_planner():
    """
    Create a planner optimized for printing and binding.

    Uses US Letter size with extra margin for hole punching or binding.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="New York, NY",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/New_York")
        .page_size("letter")  # US Letter (8.5" x 11")
        .binding_margin(0.25)  # Extra 0.25" on inner edge
        .with_natal_chart()
        .with_solar_return()
        .include_natal_transits()
        .include_moon_phases()
        .generate(get_output_path("printable_planner.pdf"))
    )

    print(f"Printable planner: {len(planner):,} bytes")


# =============================================================================
# MINIMAL PLANNER
# =============================================================================


def minimal_planner():
    """
    Create a minimal planner with just Moon phases and VOC.

    Good for quick reference or people new to astrology.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    # Disable front matter by not calling with_* methods
    # The builder defaults have these enabled, so we need to explicitly disable
    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        # Just Moon info - no front matter charts requested
        .include_moon_phases()
        .include_voc(mode="traditional")
        .include_ingresses(["Moon"])  # Only Moon sign changes
        .generate(get_output_path("minimal_planner.pdf"))
    )

    print(f"Minimal planner: {len(planner):,} bytes")


# =============================================================================
# MODERN VOC
# =============================================================================


def modern_voc_planner():
    """
    Create a planner using modern VOC calculation (includes outer planets).

    Traditional VOC only considers aspects to Sun through Saturn.
    Modern VOC includes Uranus, Neptune, and Pluto, resulting in shorter VOC periods.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        .with_natal_chart()
        .include_natal_transits()
        .include_moon_phases()
        .include_voc(mode="modern")  # Include outer planets in VOC calculation
        .generate(get_output_path("modern_voc_planner.pdf"))
    )

    print(f"Modern VOC planner: {len(planner):,} bytes")


# =============================================================================
# USING A NOTABLE
# =============================================================================


def notable_planner():
    """
    Create a planner for a notable person from the database.
    """
    # Create a native from Einstein's data
    native = Native(
        datetime_input="1879-03-14 11:30",
        location_input="Ulm, Germany",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("Europe/Berlin")
        .with_natal_chart()
        .with_graphic_ephemeris(harmonic=90)
        .include_natal_transits()
        .include_moon_phases()
        .generate(get_output_path("einstein_2025_planner.pdf"))
    )

    print(f"Einstein planner: {len(planner):,} bytes")


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PLANNER COOKBOOK EXAMPLES")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Uncomment the examples you want to run:

    # basic_planner()
    full_planner()
    # outer_planets_planner()
    # monday_start_planner()
    # custom_range_planner()
    # printable_planner()
    # minimal_planner()
    # modern_voc_planner()
    # notable_planner()

    print()
    print(f"Done! Check the generated PDF files in {OUTPUT_DIR}")
