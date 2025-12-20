"""
Stellium Web - Reactive State Management

Manages the application state for chart building.
"""

from dataclasses import dataclass, field


@dataclass
class ChartState:
    """Reactive state for chart configuration."""

    # Birth data
    name: str = ""
    date: str = ""
    time: str = ""
    time_unknown: bool = False
    location: str = ""

    # Zodiac
    zodiac_type: str = "tropical"  # or "sidereal"
    ayanamsa: str = "lahiri"

    # House systems (multiple allowed)
    house_systems: list[str] = field(default_factory=lambda: ["Placidus"])

    # Aspect configuration
    include_aspects: bool = True
    aspect_mode: str = "major"  # major, all, minor, harmonic

    # Components / Calculations
    include_dignities: bool = False
    include_midpoints: bool = False
    include_arabic_parts: bool = False
    include_fixed_stars: bool = False
    fixed_stars_mode: str = "royal"  # royal, major, all
    include_patterns: bool = False
    include_declinations: bool = False

    # Visualization - Theme & Palettes
    theme: str = "classic"
    zodiac_palette: str = "rainbow"
    aspect_palette: str = "classic"
    planet_glyph_palette: str = "default"
    color_sign_info: bool = False  # Color sign glyphs in planet info stacks

    # Visualization - Header
    show_header: bool = True

    # Visualization - Moon Phase
    show_moon_phase: bool = True
    moon_phase_position: str = "bottom-right"
    moon_phase_show_label: bool = True

    # Visualization - Tables
    show_tables: bool = False
    table_position: str = "right"
    table_show_positions: bool = True
    table_show_houses: bool = True
    table_show_aspectarian: bool = True

    # Visualization - Info Corners
    show_chart_info: bool = True
    show_aspect_counts: bool = False
    show_element_modality: bool = False

    def is_valid(self) -> bool:
        """Check if we have enough data to generate a chart."""
        has_date = bool(self.date)
        has_time = bool(self.time) or self.time_unknown
        has_location = bool(self.location)
        return has_date and has_time and has_location


@dataclass
class RelationshipsState:
    """State for relationships charts (synastry, composite, davison)."""

    # Birth data for both people
    person1: ChartState = field(default_factory=ChartState)
    person2: ChartState = field(default_factory=ChartState)

    # Chart type
    chart_type: str = "synastry"  # synastry, composite, davison

    # House system (for composite/davison - synastry uses individual charts' houses)
    house_system: str = "Placidus"

    # Aspect configuration
    include_aspects: bool = True
    aspect_mode: str = "major"  # major, all, minor, harmonic

    # Visualization - Theme & Palettes
    theme: str = "classic"
    zodiac_palette: str = "rainbow"
    aspect_palette: str = "classic"
    planet_glyph_palette: str = "default"
    color_sign_info: bool = False

    # Visualization - Header
    show_header: bool = True

    # Visualization - Moon Phase (for composite/davison)
    show_moon_phase: bool = False
    moon_phase_position: str = "bottom-right"
    moon_phase_show_label: bool = True

    # Visualization - Tables
    show_tables: bool = False
    table_position: str = "right"

    # Visualization - Info Corners
    show_chart_info: bool = True
    show_aspect_counts: bool = False

    def is_valid(self) -> bool:
        """Check if we have enough data to generate a chart."""
        return self.person1.is_valid() and self.person2.is_valid()


@dataclass
class PDFReportState:
    """State for PDF report generation options."""

    # Sections to include
    include_chart_overview: bool = True
    include_moon_phase: bool = True
    include_planet_positions: bool = True
    include_declinations: bool = False
    include_house_cusps: bool = True
    include_aspects: bool = True
    include_aspect_patterns: bool = False
    include_dignities: bool = False
    include_midpoints: bool = False
    include_midpoint_aspects: bool = False
    include_fixed_stars: bool = False

    # Planet positions options
    positions_include_speed: bool = False
    positions_include_house: bool = True

    # Aspects options
    aspects_mode: str = "major"  # major, all, minor, harmonic
    aspects_show_orbs: bool = True
    aspects_sort_by: str = "orb"  # orb, planet, aspect_type

    # Midpoints options
    midpoints_mode: str = "all"  # all, core

    # Midpoint aspects options
    midpoint_aspects_mode: str = "conjunction"  # conjunction, hard, all
    midpoint_aspects_orb: float = 1.5
    midpoint_aspects_filter: str = "all"  # all, core

    # Fixed stars options
    fixed_stars_tier: str = "all"  # royal, major, all
    fixed_stars_include_keywords: bool = True

    # Dignities options
    dignities_system: str = "both"  # traditional, modern, both
    dignities_show_details: bool = False

    # Output options
    include_chart_image: bool = True


def create_report_state_from_chart_state(chart_state: ChartState) -> PDFReportState:
    """Create a PDFReportState pre-filled from ChartState settings."""
    return PDFReportState(
        # Pre-fill based on chart state choices
        include_aspects=chart_state.include_aspects,
        include_aspect_patterns=chart_state.include_patterns,
        include_dignities=chart_state.include_dignities,
        include_midpoints=chart_state.include_midpoints,
        include_midpoint_aspects=chart_state.include_midpoints,  # If midpoints enabled, show aspects too
        include_fixed_stars=chart_state.include_fixed_stars,
        include_declinations=chart_state.include_declinations,
        # Match aspect mode
        aspects_mode=chart_state.aspect_mode,
        # Match fixed stars mode
        fixed_stars_tier=chart_state.fixed_stars_mode,
    )


@dataclass
class TimingState:
    """State for timing charts (transits, progressions, returns)."""

    # Natal chart data (the base chart)
    natal: ChartState = field(default_factory=ChartState)

    # Chart type
    chart_type: str = "transits"  # transits, progressions, solar_return, lunar_return, planetary_return

    # Timing date (when to cast the transit/progressed chart)
    timing_date: str = (
        ""  # For transits: the transit date; for returns: the year/date to find
    )

    # For returns: optional relocation
    relocate: bool = False
    relocation_location: str = ""

    # For planetary returns (other than Solar/Lunar)
    return_planet: str = "Saturn"  # Jupiter, Saturn, Mars, etc.

    # For returns: occurrence number (1 = first, 2 = second) vs near_date
    return_mode: str = (
        "year"  # year (solar), near_date (lunar/planetary), occurrence (planetary)
    )
    return_occurrence: int = 1  # For occurrence mode

    # House system
    house_system: str = "Placidus"

    # Aspect configuration
    include_aspects: bool = True
    aspect_mode: str = "major"  # major, all, minor, harmonic

    # Visualization - Theme & Palettes
    theme: str = "classic"
    zodiac_palette: str = "rainbow"
    aspect_palette: str = "classic"
    planet_glyph_palette: str = "default"
    color_sign_info: bool = False

    # Visualization - Header
    show_header: bool = True

    # Visualization - Moon Phase
    show_moon_phase: bool = True
    moon_phase_position: str = "bottom-right"
    moon_phase_show_label: bool = True

    # Visualization - Tables
    show_tables: bool = False
    table_position: str = "right"

    # Visualization - Info Corners
    show_chart_info: bool = True
    show_aspect_counts: bool = False

    def is_valid(self) -> bool:
        """Check if we have enough data to generate a chart."""
        if not self.natal.is_valid():
            return False

        if self.chart_type in ("transits", "progressions"):
            return bool(self.timing_date)
        elif self.chart_type == "solar_return":
            # Need a year
            return bool(self.timing_date)
        elif self.chart_type in ("lunar_return", "planetary_return"):
            # Need either a near_date or occurrence
            return bool(self.timing_date) or self.return_occurrence >= 1
        return False


@dataclass
class PlannerState:
    """State for astrological planner generation."""

    # Birth data (whose planner to create)
    native: ChartState = field(default_factory=ChartState)

    # Date range
    year: int = 2025
    use_custom_range: bool = False
    start_date: str = ""  # YYYY-MM-DD
    end_date: str = ""  # YYYY-MM-DD

    # Timezone (required)
    timezone: str = "America/Los_Angeles"

    # Location for angles/planetary hours (defaults to birth location)
    use_custom_location: bool = False
    custom_location: str = ""

    # Front matter options
    include_natal_chart: bool = True
    include_progressed_chart: bool = True
    include_solar_return: bool = True
    include_profections: bool = True
    include_zr_timeline: bool = True
    zr_lot: str = "Part of Fortune"  # or "Part of Spirit"
    include_graphic_ephemeris: bool = True
    graphic_ephemeris_harmonic: int = 360  # 360, 90, 45

    # Daily content options
    include_natal_transits: bool = True
    natal_transit_planets: str = "outer"  # outer, all, custom
    include_mundane_transits: bool = True
    include_moon_phases: bool = True
    include_voc: bool = True
    voc_mode: str = "traditional"  # traditional, modern
    include_ingresses: bool = True
    include_stations: bool = True

    # Page layout
    page_size: str = "a4"  # a4, letter, half-letter
    binding_margin: float = 0.0
    week_starts_on: str = "sunday"  # sunday, monday

    def is_valid(self) -> bool:
        """Check if we have enough data to generate a planner."""
        if not self.native.is_valid():
            return False
        if not self.timezone:
            return False
        if self.use_custom_range:
            return bool(self.start_date and self.end_date)
        return bool(self.year)


# Global state instances
chart_state = ChartState()
relationships_state = RelationshipsState()
timing_state = TimingState()
planner_state = PlannerState()
