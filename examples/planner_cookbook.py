"""
Planner Cookbook - Recipes for creating personalized astrological planners.

A planner is an instrument you consult, not a report you read once. So its front
matter is a *reference section* — the things the daily pages send you to look up:

- The Year at a Glance: Lord of the Year, eclipses placed in YOUR houses,
  retrograde windows, and the slow transits that shape the year
- A year overview: twelve mini-months with eclipse and station days marked
- Your natal chart as a lookup table (plus the wheel)
- The year's transit map, solar return, and profections
- The progressed Moon's dated aspects to your natal planets
- Zodiacal releasing, scoped to this year
- A glyph legend for reading the daily pages

Then: monthly calendar grids, and weekly pages with room to write.

The front matter is curated by default, so a bare planner is already useful.
Drop any page with the matching `.without_*()` call.

Planners are rendered by the bundled Typst design system, so they take a theme:
"house" (default), "sepia", "celestial", "blues", or "greyscale". Reach for
"greyscale" if you're printing at home — it swaps ink fills for outlines.
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
        .year(2026)
        .timezone("America/Los_Angeles")
        .page_size("letter")
        .theme("house")  # the default; try "celestial" or "greyscale"
        # Front matter (all on by default — listed here to show what you get)
        .with_natal_chart()
        .with_progressed_chart()
        .with_solar_return()
        .with_profections()
        .with_graphic_ephemeris(harmonic=90)  # 90° shows hard aspects as conjunctions
        .with_zr_timeline()
        # Daily content - all planets
        .include_natal_transits()  # Default: outer planets (Jupiter, Saturn, Uranus, Neptune, Pluto)
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
# ONE MONTH, FULL FRONT MATTER, AND A SECOND LOCATION
# =============================================================================


def one_month_relocated_planner():
    """
    A single month, with the whole reference section, for someone living abroad.

    Two things worth knowing here.

    **The range is free.** `.year(2026)` is only shorthand for
    `.date_range(date(2026, 1, 1), date(2026, 12, 31))`. Any span works, and the
    front matter adapts: the pages are titled from the actual range, so this one
    says "March 2026 at a Glance" rather than pretending to be a year. A month
    takes about 6 seconds and comes out ~20 pages — a good way to preview a theme
    or a config without waiting on a full year.

    **Birth place and current place are different things.** The native was born in
    Boston; she lives in Lisbon now. So:

    - `.timezone()` sets the clock every event is printed in. This is the one that
      matters most day to day — it is what makes "Moon enters Leo, 1:43 PM" true
      where you are standing.
    - `.location()` sets where charts are *cast*, which is what makes the solar
      return a relocated one. Recast for Lisbon, this native's solar return
      Ascendant moves by nearly 60°, taking every house cusp with it.

    Most of a planner is location-independent and that is not a limitation: the
    transits, ingresses, stations, lunations and void-of-course periods are all
    geocentric ecliptic longitudes. The sky does the same thing whichever city you
    watch it from — only the *clock* and the *houses* are local.
    """
    from datetime import date

    native = Native(
        datetime_input="1990-07-15 14:30",
        location_input="Boston, MA",  # where she was born
    )

    planner = (
        PlannerBuilder.for_native(native)
        .date_range(date(2026, 3, 1), date(2026, 3, 31))
        .timezone("Europe/Lisbon")  # the clock she actually lives on
        .location("Lisbon, Portugal")  # where her charts get cast
        .theme("sepia")
        .generate(get_output_path("one_month_relocated_planner.pdf"))
    )

    print(f"One-month relocated planner: {len(planner):,} bytes")


# =============================================================================
# LETTER SIZE WITH BINDING MARGIN
# =============================================================================


def printable_planner():
    """
    Create a planner optimized for printing and binding.

    Uses US Letter size with extra margin for hole punching or binding, and the
    greyscale theme so a home laser printer doesn't drink a cartridge of ink —
    discs and badges become outlines, and the chart wheel goes grey.
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
        .binding_margin(0.25)  # Extra 0.25" on the inner (bound) edge
        .theme("greyscale")  # laser-printer safe
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

    The front matter is curated ON by default — a planner should be useful out of
    the box — so a minimal one is built by opting *out* with `.without_*()`.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    planner = (
        PlannerBuilder.for_native(native)
        .year(2025)
        .timezone("America/Los_Angeles")
        # Strip the reference pages back to nothing
        .without_natal_chart()
        .without_progressed_chart()
        .without_solar_return()
        .without_profections()
        .without_zr_timeline()
        .without_graphic_ephemeris()
        # Just Moon info on the daily pages
        .include_moon_phases()
        .include_voc(mode="traditional")
        .include_ingresses(["Moon"])  # Only Moon sign changes
        .generate(get_output_path("minimal_planner.pdf"))
    )

    print(f"Minimal planner: {len(planner):,} bytes")


# =============================================================================
# THEMES
# =============================================================================


def themed_planners():
    """
    Render the same planner in each of the five design-system themes.

    A theme is pure data — colour tokens, a font trio, a sign palette — so the
    chart wheels, aspect colours and table shading all stay coordinated with the
    page. "greyscale" is laser-printer safe: outlines instead of ink fills.
    """
    native = Native(
        datetime_input="1990-05-15 14:30",
        location_input="San Francisco, CA",
    )

    for theme in ("house", "sepia", "celestial", "blues", "greyscale"):
        planner = (
            PlannerBuilder.for_native(native)
            .year(2026)
            .timezone("America/Los_Angeles")
            .page_size("letter")
            .theme(theme)
            .generate(get_output_path(f"themed_{theme}_planner.pdf"))
        )
        print(f"  {theme:10} {len(planner):,} bytes")


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

    # Uncomment the examples you want to run. Only full_planner() runs by
    # default — each planner takes ~20s, and this cookbook is a CI smoke test.

    # basic_planner()
    full_planner()
    # outer_planets_planner()
    # monday_start_planner()
    # custom_range_planner()
    # one_month_relocated_planner()  # ~6s — the quickest way to preview a config
    # printable_planner()
    # minimal_planner()
    # modern_voc_planner()
    # notable_planner()
    # themed_planners()  # all five themes, ~2 minutes

    print()
    print(f"Done! Check the generated PDF files in {OUTPUT_DIR}")
