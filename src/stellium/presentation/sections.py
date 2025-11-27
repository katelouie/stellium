"""
Report section implementations.

Each section extracts specific data from a CalculatedChart and formats it
into a standardized structure that renderers can consume.
"""

import datetime as dt
from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, MidpointPosition, ObjectType
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    FIXED_STARS_REGISTRY,
    get_aspects_by_category,
)
from stellium.engines.dignities import DIGNITIES


def get_object_display(name: str) -> tuple[str, str]:
    """
    Get display name and glyph for a celestial object.

    Args:
        name: Internal object name (e.g., "Sun", "True Node")

    Returns:
        Tuple of (display_name, glyph)
    """
    if name in CELESTIAL_REGISTRY:
        info = CELESTIAL_REGISTRY[name]
        return info.display_name, info.glyph
    return name, ""


def get_sign_glyph(sign_name: str) -> str:
    """Get the zodiac glyph for a sign name."""
    if sign_name in DIGNITIES:
        return DIGNITIES[sign_name]["symbol"]
    return ""


def get_aspect_display(aspect_name: str) -> tuple[str, str]:
    """
    Get display name and glyph for an aspect.

    Args:
        aspect_name: Aspect name (e.g., "Conjunction", "Trine")

    Returns:
        Tuple of (name, glyph)
    """
    if aspect_name in ASPECT_REGISTRY:
        info = ASPECT_REGISTRY[aspect_name]
        return info.name, info.glyph
    return aspect_name, ""


def get_object_sort_key(position):
    """
    Generate sort key for consistent object ordering in reports.

    Sorting hierarchy:
    1. Object type (Planet < Node < Point < Asteroid < Angle < Midpoint)
    2. Registry insertion order (for registered objects)
    3. Swiss Ephemeris ID (for unregistered known objects)
    4. Alphabetical name (for custom objects)

    Args:
        position: A celestial object position from CalculatedChart

    Returns:
        Tuple sort key for use with sorted()

    Example:
        positions = sorted(chart.positions, key=get_object_sort_key)
    """
    # Define type ordering
    type_order = {
        ObjectType.PLANET: 0,
        ObjectType.NODE: 1,
        ObjectType.POINT: 2,
        ObjectType.ASTEROID: 3,
        ObjectType.ANGLE: 4,
        ObjectType.MIDPOINT: 5,
    }

    type_rank = type_order.get(position.object_type, 999)

    # Try registry order (using insertion order of dict keys)
    registry_keys = list(CELESTIAL_REGISTRY.keys())
    if position.name in registry_keys:
        registry_index = registry_keys.index(position.name)
        return (type_rank, registry_index)

    # Fallback to Swiss Ephemeris ID
    if (
        hasattr(position, "swiss_ephemeris_id")
        and position.swiss_ephemeris_id is not None
    ):
        return (type_rank, 10000 + position.swiss_ephemeris_id)

    # Final fallback: alphabetical by name
    return (type_rank, 20000, position.name)


def get_aspect_sort_key(aspect_name: str) -> tuple:
    """
    Generate sort key for consistent aspect ordering in reports.

    Sorting hierarchy:
    1. Registry insertion order (aspects ordered by angle: 0°, 60°, 90°, etc.)
    2. Angle value (for aspects not in registry)
    3. Alphabetical name (final fallback)

    Args:
        aspect_name: Name of the aspect (e.g., "Conjunction", "Trine")

    Returns:
        Tuple sort key for use with sorted()

    Example:
        aspects = sorted(aspects, key=lambda a: get_aspect_sort_key(a.aspect_name))
    """
    from stellium.core.registry import (
        ASPECT_REGISTRY,
        get_aspect_by_alias,
        get_aspect_info,
    )

    # Try registry order (insertion order = angle order)
    registry_keys = list(ASPECT_REGISTRY.keys())
    if aspect_name in registry_keys:
        registry_index = registry_keys.index(aspect_name)
        return (registry_index,)

    # Try to find by alias
    aspect_info = get_aspect_by_alias(aspect_name)
    if aspect_info and aspect_info.name in registry_keys:
        registry_index = registry_keys.index(aspect_info.name)
        return (registry_index,)

    # Fallback: try to get angle from registry
    aspect_info = get_aspect_info(aspect_name)
    if aspect_info:
        return (1000 + aspect_info.angle,)

    # Final fallback: alphabetical
    return (2000, aspect_name)


def abbreviate_house_system(system_name: str) -> str:
    """
    Generate 2-4 character abbreviation for house system names.

    Args:
        system_name: Full house system name (e.g., "Placidus", "Whole Sign")

    Returns:
        Short abbreviation (e.g., "Pl", "WS")

    Example:
        >>> abbreviate_house_system("Placidus")
        'Pl'
        >>> abbreviate_house_system("Whole Sign")
        'WS'
    """
    abbreviations = {
        "Placidus": "Pl",
        "Whole Sign": "WS",
        "Koch": "Ko",
        "Equal": "Eq",
        "Porphyry": "Po",
        "Regiomontanus": "Re",
        "Campanus": "Ca",
        "Morinus": "Mo",
        "Meridian": "Me",
        "Alcabitius": "Al",
    }
    return abbreviations.get(system_name, system_name[:4])


class ChartOverviewSection:
    """
    Overview section with basic chart information.

    Shows:
    - Native name (if available)
    - Birth date/time
    - Location
    - Chart type (day/night)
    - House system

    For Comparison objects, shows info for both charts.
    """

    @property
    def section_name(self) -> str:
        return "Chart Overview"

    def generate_data(self, chart: CalculatedChart | Comparison) -> dict[str, Any]:
        """
        Generate chart overview data.

        For Comparison objects, shows both charts' information.

        Why key-value format?
        - Simple label: value pairs
        - Easy to render as a list or small table
        - Human-readable structure
        """
        # Handle Comparison objects
        if isinstance(chart, Comparison):
            return self._generate_comparison_data(chart)

        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(
        self, chart: CalculatedChart, label: str | None = None
    ) -> dict[str, Any]:
        """Generate overview data for a single chart."""
        data = {}

        # Name (if available in metadata)
        if "name" in chart.metadata:
            name = chart.metadata["name"]
            if label:
                data[f"{label}"] = name
            else:
                data["Name"] = name

        # Date and time
        birth: dt.datetime = chart.datetime.local_datetime
        date_label = f"{label} Date" if label else "Date"
        time_label = f"{label} Time" if label else "Time"
        data[date_label] = birth.strftime("%B %d, %Y")
        data[time_label] = birth.strftime("%I:%M %p")

        if not label:  # Only show timezone for single charts
            data["Timezone"] = str(chart.location.timezone)

        # Location
        loc = chart.location
        loc_label = f"{label} Location" if label else "Location"
        data[loc_label] = f"{loc.name}" if loc.name else "Unknown"

        if not label:  # Only show detailed info for single charts
            data["Coordinates"] = f"{loc.latitude:.4f}°, {loc.longitude:.4f}°"

            # Chart metadata
            house_systems = ", ".join(chart.house_systems.keys())
            data["House System"] = house_systems

            # Zodiac system
            if chart.zodiac_type:
                zodiac_display = chart.zodiac_type.value.title()
                if chart.zodiac_type.value == "sidereal" and chart.ayanamsa:
                    ayanamsa_display = chart.ayanamsa.replace("_", " ").title()
                    zodiac_display = f"{zodiac_display} ({ayanamsa_display})"
                data["Zodiac"] = zodiac_display

                if (
                    chart.zodiac_type.value == "sidereal"
                    and chart.ayanamsa_value is not None
                ):
                    degrees = int(chart.ayanamsa_value)
                    minutes = int((chart.ayanamsa_value % 1) * 60)
                    seconds = int(((chart.ayanamsa_value % 1) * 60 % 1) * 60)
                    data["Ayanamsa"] = f"{degrees}°{minutes:02d}'{seconds:02d}\""

            # Sect (if available in metadata)
            if "dignities" in chart.metadata:
                sect = chart.metadata["dignities"].get("sect", "unknown")
                data["Chart Sect"] = f"{sect.title()} Chart"

        return {
            "type": "key_value",
            "data": data,
        }

    def _generate_comparison_data(self, comparison: Comparison) -> dict[str, Any]:
        """Generate overview data for a Comparison object."""
        data = {}

        # Comparison type
        comp_type = comparison.comparison_type.value.title()
        data["Comparison Type"] = comp_type

        # Chart 1 info
        chart1 = comparison.chart1
        label1 = comparison.chart1_label or "Chart 1"
        if "name" in chart1.metadata:
            data[label1] = chart1.metadata["name"]
        else:
            data[label1] = "(unnamed)"

        birth1: dt.datetime = chart1.datetime.local_datetime
        data[f"{label1} Date"] = birth1.strftime("%B %d, %Y")
        data[f"{label1} Time"] = birth1.strftime("%I:%M %p")
        data[f"{label1} Location"] = (
            chart1.location.name if chart1.location.name else "Unknown"
        )

        # Chart 2 info
        chart2 = comparison.chart2
        label2 = comparison.chart2_label or "Chart 2"
        if "name" in chart2.metadata:
            data[label2] = chart2.metadata["name"]
        else:
            data[label2] = "(unnamed)"

        birth2: dt.datetime = chart2.datetime.local_datetime
        data[f"{label2} Date"] = birth2.strftime("%B %d, %Y")
        data[f"{label2} Time"] = birth2.strftime("%I:%M %p")
        data[f"{label2} Location"] = (
            chart2.location.name if chart2.location.name else "Unknown"
        )

        # Cross-chart aspect count
        data["Cross-Chart Aspects"] = len(comparison.cross_aspects)

        return {
            "type": "key_value",
            "data": data,
        }


class PlanetPositionSection:
    """Table of planet positions.

    Shows:
    - Planet name
    - Sign + degree
    - House (optional)
    - Speed (optional, shows retrograde status)
    """

    def __init__(
        self,
        include_speed: bool = False,
        include_house: bool = True,
        house_systems: str | list[str] = "all",
    ) -> None:
        """
        Initialize section with display options.

        Args:
            include_speed: Show speed column (for retrograde detection)
            include_house: Show house placement column
            house_systems: Which systems to display:
                - "all": Show all calculated house systems (DEFAULT)
                - list[str]: Show specific systems (e.g., ["Placidus", "Whole Sign"])
                - None: Show default system only
        """
        self.include_speed = include_speed
        self.include_house = include_house

        # Normalize to internal representation
        if house_systems == "all":
            self._house_systems_mode = "all"
            self._house_systems = None
        elif isinstance(house_systems, list):
            self._house_systems_mode = "specific"
            self._house_systems = house_systems
        elif house_systems is None:
            self._house_systems_mode = "default"
            self._house_systems = None
        else:
            # Single system name as string
            self._house_systems_mode = "specific"
            self._house_systems = [house_systems]

    @property
    def section_name(self) -> str:
        return "Planet Positions"

    def generate_data(self, chart: CalculatedChart | Comparison) -> dict[str, Any]:
        """
        Generate planet positions table.

        For Comparison objects, generates side-by-side tables for each chart.
        """
        # Handle Comparison objects with side-by-side tables
        if isinstance(chart, Comparison):
            return self._generate_comparison_data(chart)

        # Single chart: standard table
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(
        self, chart: CalculatedChart, title: str | None = None
    ) -> dict[str, Any]:
        """Generate position table data for a single chart."""
        # Determine which house systems to show
        if self._house_systems_mode == "all":
            systems_to_show = list(chart.house_systems.keys())
        elif self._house_systems_mode == "specific":
            systems_to_show = [
                s for s in self._house_systems if s in chart.house_systems
            ]
        else:  # "default"
            systems_to_show = [chart.default_house_system]

        # Build headers based on options
        headers = ["Planet", "Position"]

        if self.include_house and systems_to_show:
            for system_name in systems_to_show:
                abbrev = abbreviate_house_system(system_name)
                headers.append(f"House ({abbrev})")

        if self.include_speed:
            headers.append("Speed")
            headers.append("Motion")

        # Filter to planets, asteroids, nodes and points
        positions = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
                ObjectType.NODE,
                ObjectType.POINT,
            )
        ]

        # Sort positions consistently
        positions = sorted(positions, key=get_object_sort_key)

        # Build rows
        rows = []
        for pos in positions:
            row = []
            # Planet name with glyph
            display_name, glyph = get_object_display(pos.name)
            if glyph:
                row.append(f"{glyph} {display_name}")
            else:
                row.append(display_name)

            # Position with sign glyph
            degree = int(pos.sign_degree)
            minute = int((pos.sign_degree % 1) * 60)
            sign_glyph = get_sign_glyph(pos.sign)
            if sign_glyph:
                row.append(f"{sign_glyph} {pos.sign} {degree}°{minute:02d}'")
            else:
                row.append(f"{pos.sign} {degree}°{minute:02d}'")

            # House columns (one per system)
            if self.include_house and systems_to_show:
                for system_name in systems_to_show:
                    try:
                        house_placements = chart.house_placements[system_name]
                        house = house_placements.get(pos.name, "—")
                        row.append(str(house) if house else "—")
                    except KeyError:
                        row.append("—")

            # Speed and motion (if requested)
            if self.include_speed:
                row.append(f"{pos.speed_longitude:.4f}°/day")
                row.append("Retrograde" if pos.is_retrograde else "Direct")

            rows.append(row)

        result = {"type": "table", "headers": headers, "rows": rows}
        if title:
            result["title"] = title
        return result

    def _generate_comparison_data(self, comparison: Comparison) -> dict[str, Any]:
        """Generate side-by-side position tables for a Comparison."""
        # Generate table data for each chart
        chart1_data = self._generate_single_chart_data(
            comparison.chart1, title=comparison.chart1_label
        )
        chart2_data = self._generate_single_chart_data(
            comparison.chart2, title=comparison.chart2_label
        )

        return {
            "type": "side_by_side_tables",
            "tables": [
                {
                    "title": chart1_data.get("title", "Chart 1"),
                    "headers": chart1_data["headers"],
                    "rows": chart1_data["rows"],
                },
                {
                    "title": chart2_data.get("title", "Chart 2"),
                    "headers": chart2_data["headers"],
                    "rows": chart2_data["rows"],
                },
            ],
        }


class HouseCuspsSection:
    """
    Table of house cusp positions for multiple house systems.

    Shows:
    - House number (1-12)
    - Cusp position for each calculated house system
    """

    def __init__(self, systems: str | list[str] = "all") -> None:
        """
        Initialize section with system selection.

        Args:
            systems: Which systems to display:
                - "all": Show all calculated house systems (DEFAULT)
                - list[str]: Show specific systems (e.g., ["Placidus", "Whole Sign"])
        """
        # Normalize to internal representation
        if systems == "all":
            self._systems_mode = "all"
            self._systems = None
        elif isinstance(systems, list):
            self._systems_mode = "specific"
            self._systems = systems
        else:
            # Single system name as string
            self._systems_mode = "specific"
            self._systems = [systems]

    @property
    def section_name(self) -> str:
        return "House Cusps"

    def generate_data(self, chart: CalculatedChart | Comparison) -> dict[str, Any]:
        """
        Generate house cusps table.

        For Comparison objects, generates side-by-side tables for each chart.
        """
        # Handle Comparison objects with side-by-side tables
        if isinstance(chart, Comparison):
            return self._generate_comparison_data(chart)

        # Single chart: standard table
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(
        self, chart: CalculatedChart, title: str | None = None
    ) -> dict[str, Any]:
        """Generate house cusps table data for a single chart."""
        from stellium.core.models import longitude_to_sign_and_degree

        # Determine which house systems to show
        if self._systems_mode == "all":
            systems_to_show = list(chart.house_systems.keys())
        else:  # "specific"
            systems_to_show = [s for s in self._systems if s in chart.house_systems]

        # Build headers
        headers = ["House"]
        for system_name in systems_to_show:
            abbrev = abbreviate_house_system(system_name)
            headers.append(f"Cusp ({abbrev})")

        # Build rows (houses 1-12)
        rows = []
        for house_num in range(1, 13):
            row = [str(house_num)]

            for system_name in systems_to_show:
                house_cusps = chart.house_systems[system_name]
                cusp_longitude = house_cusps.cusps[house_num - 1]

                # Convert to sign and degree
                sign, sign_degree = longitude_to_sign_and_degree(cusp_longitude)
                degree = int(sign_degree)
                minute = int((sign_degree % 1) * 60)

                # Format with sign glyph
                sign_glyph = get_sign_glyph(sign)
                if sign_glyph:
                    row.append(f"{degree}° {sign_glyph} {minute:02d}'")
                else:
                    row.append(f"{degree}° {sign} {minute:02d}'")

            rows.append(row)

        result = {"type": "table", "headers": headers, "rows": rows}
        if title:
            result["title"] = title
        return result

    def _generate_comparison_data(self, comparison: Comparison) -> dict[str, Any]:
        """Generate side-by-side house cusps tables for a Comparison."""
        chart1_data = self._generate_single_chart_data(
            comparison.chart1, title=comparison.chart1_label
        )
        chart2_data = self._generate_single_chart_data(
            comparison.chart2, title=comparison.chart2_label
        )

        return {
            "type": "side_by_side_tables",
            "tables": [
                {
                    "title": chart1_data.get("title", "Chart 1"),
                    "headers": chart1_data["headers"],
                    "rows": chart1_data["rows"],
                },
                {
                    "title": chart2_data.get("title", "Chart 2"),
                    "headers": chart2_data["headers"],
                    "rows": chart2_data["rows"],
                },
            ],
        }


class DignitySection:
    """
    Table of essential dignities for planets.

    Shows dignity scores and details for traditional and/or modern systems.
    Gracefully handles missing dignity data with helpful message.
    """

    def __init__(
        self,
        essential: str = "both",
        show_details: bool = False,
    ) -> None:
        """
        Initialize dignity section.

        Args:
            essential: Which essential dignity system(s) to show:
                - "traditional": Traditional dignities only
                - "modern": Modern dignities only
                - "both": Both systems (DEFAULT)
                - "none": Skip essential dignities
            show_details: Show dignity names instead of just scores
        """
        if essential not in ("traditional", "modern", "both", "none"):
            raise ValueError(
                f"essential must be 'traditional', 'modern', 'both', or 'none': got {essential}"
            )
        self.essential = essential
        self.show_details = show_details

    @property
    def section_name(self) -> str:
        return "Essential Dignities"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate dignity table.
        """
        # Check if dignity data exists
        if "dignities" not in chart.metadata:
            # Graceful handling: return helpful message
            return {
                "type": "text",
                "content": (
                    "Add DignityComponent() to chart builder to enable dignity calculations.\n\n"
                    "Example:\n"
                    "  chart = ChartBuilder.from_native(native).add_component(DignityComponent()).calculate()"
                ),
            }

        dignity_data = chart.metadata["dignities"]
        planet_dignities = dignity_data.get("planet_dignities", {})

        if not planet_dignities:
            return {
                "type": "text",
                "content": "No dignity data available.",
            }

        # Build headers
        headers = ["Planet"]

        if self.essential in ("traditional", "both"):
            if self.show_details:
                headers.append("Traditional Dignities")
            else:
                headers.append("Trad Score")

        if self.essential in ("modern", "both"):
            if self.show_details:
                headers.append("Modern Dignities")
            else:
                headers.append("Mod Score")

        # Filter to planets only
        positions = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.ASTEROID,
            )
        ]

        # Sort positions consistently
        positions = sorted(positions, key=get_object_sort_key)

        # Build rows
        rows = []
        for pos in positions:
            if pos.name not in planet_dignities:
                continue

            row = []

            # Planet name with glyph
            display_name, glyph = get_object_display(pos.name)
            if glyph:
                row.append(f"{glyph} {display_name}")
            else:
                row.append(display_name)

            dignity_info = planet_dignities[pos.name]

            # Traditional column
            if self.essential in ("traditional", "both"):
                if "traditional" in dignity_info:
                    trad = dignity_info["traditional"]
                    if self.show_details:
                        # Show dignity names
                        dignity_names = trad.get("dignities", [])
                        if dignity_names:
                            row.append(", ".join(dignity_names))
                        else:
                            row.append("Peregrine" if trad.get("is_peregrine") else "—")
                    else:
                        # Show score
                        score = trad.get("score", 0)
                        row.append(f"{score:+d}" if score != 0 else "0")
                else:
                    row.append("—")

            # Modern column
            if self.essential in ("modern", "both"):
                if "modern" in dignity_info:
                    mod = dignity_info["modern"]
                    if self.show_details:
                        # Show dignity names
                        dignity_names = mod.get("dignities", [])
                        if dignity_names:
                            row.append(", ".join(dignity_names))
                        else:
                            row.append("—")
                    else:
                        # Show score
                        score = mod.get("score", 0)
                        row.append(f"{score:+d}" if score != 0 else "0")
                else:
                    row.append("—")

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class AspectPatternSection:
    """
    Table of detected aspect patterns.

    Shows Grand Trines, T-Squares, Yods, etc.
    Gracefully handles missing pattern data with helpful message.
    """

    def __init__(
        self,
        pattern_types: str | list[str] = "all",
        sort_by: str = "type",
    ) -> None:
        """
        Initialize aspect pattern section.

        Args:
            pattern_types: Which pattern types to show:
                - "all": Show all detected patterns (DEFAULT)
                - list[str]: Show specific pattern types (e.g., ["Grand Trine", "T-Square"])
            sort_by: How to sort patterns:
                - "type": Group by pattern type
                - "element": Group by element (Fire, Earth, Air, Water)
                - "count": Sort by number of planets involved
        """
        self.pattern_types = pattern_types
        self.sort_by = sort_by

    @property
    def section_name(self) -> str:
        return "Aspect Patterns"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate aspect pattern table.
        """
        # Check if aspect pattern data exists
        if "aspect_patterns" not in chart.metadata:
            # Graceful handling: return helpful message
            return {
                "type": "text",
                "content": (
                    "Add AspectPatternAnalyzer() to chart builder to enable pattern detection.\n\n"
                    "Example:\n"
                    "  from stellium.engines.patterns import AspectPatternAnalyzer\n"
                    "  chart = ChartBuilder.from_native(native).add_analyzer(AspectPatternAnalyzer()).calculate()"
                ),
            }

        patterns = chart.metadata["aspect_patterns"]

        if not patterns:
            return {
                "type": "text",
                "content": "No aspect patterns detected in this chart.",
            }

        # Filter patterns if specific types requested
        if self.pattern_types != "all":
            if isinstance(self.pattern_types, list):
                patterns = [p for p in patterns if p.name in self.pattern_types]
            else:
                patterns = [p for p in patterns if p.name == self.pattern_types]

        if not patterns:
            return {
                "type": "text",
                "content": f"No patterns of type {self.pattern_types} found.",
            }

        # Sort patterns
        if self.sort_by == "element":
            patterns = sorted(
                patterns,
                key=lambda p: (p.element or "zzz", p.name),  # Put None at end
            )
        elif self.sort_by == "count":
            patterns = sorted(
                patterns,
                key=lambda p: (-len(p.planets), p.name),  # Descending by count
            )
        else:  # "type"
            patterns = sorted(patterns, key=lambda p: p.name)

        # Build headers
        headers = ["Pattern", "Planets", "Element/Quality", "Details"]

        # Build rows
        rows = []
        for pattern in patterns:
            row = []

            # Pattern name
            row.append(pattern.name)

            # Planets involved (with glyphs)
            planet_names = []
            for planet in pattern.planets:
                display_name, glyph = get_object_display(planet.name)
                if glyph:
                    planet_names.append(f"{glyph} {display_name}")
                else:
                    planet_names.append(display_name)
            row.append(", ".join(planet_names))

            # Element/Quality
            elem_qual = []
            if pattern.element:
                elem_qual.append(pattern.element)
            if pattern.quality:
                elem_qual.append(pattern.quality)
            row.append(" / ".join(elem_qual) if elem_qual else "—")

            # Details (count + focal planet if applicable)
            details = []
            details.append(f"{len(pattern.planets)} planets")

            # Check for focal/apex planet
            focal = pattern.focal_planet
            if focal:
                focal_display, focal_glyph = get_object_display(focal.name)
                if focal_glyph:
                    details.append(f"Apex: {focal_glyph} {focal_display}")
                else:
                    details.append(f"Apex: {focal_display}")

            row.append(", ".join(details))

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class AspectSection:
    """
    Table of aspects between planets.

    Shows:
    - Planet 1
    - Aspect type
    - Planet 2
    - Orb (optional)
    - Applying/Separating (optional)
    """

    def __init__(
        self, mode: str = "all", orbs: bool = True, sort_by: str = "orb"
    ) -> None:
        """
        Initialize aspect section.

        Args:
            mode: "all", "major", "minor", or "harmonic"
        """
        if mode not in ("all", "major", "minor", "harmonic"):
            raise ValueError(
                f"mode must be 'all', 'major', 'minor', or 'harmonic', got {mode}"
            )
        if sort_by not in ("orb", "planet", "aspect_type"):
            raise ValueError(
                f"sort_by must be 'orb', 'planet', or 'aspect_type', got {sort_by}"
            )

        self.mode = mode
        self.orb_display = orbs
        self.sort_by = sort_by

    @property
    def section_name(self) -> str:
        if self.mode == "major":
            return "Major Aspects"
        elif self.mode == "minor":
            return "Minor Aspects"
        elif self.mode == "harmonic":
            return "Harmonic Aspects"
        return "Aspects"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate aspects table."""
        # Filer aspects based on mode
        aspects = chart.aspects
        aspect_category = self.mode.title()
        allowed_aspects = [a.name for a in get_aspects_by_category(aspect_category)]
        aspects = [a for a in aspects if a.aspect_name in allowed_aspects]

        # Sort aspects
        if self.sort_by == "orb":
            aspects = sorted(aspects, key=lambda a: a.orb)
        elif self.sort_by == "aspect_type":
            # Sort by aspect using registry order (angle order)
            aspects = sorted(aspects, key=lambda a: get_aspect_sort_key(a.aspect_name))
        elif self.sort_by == "planet":
            # Sort by first object, then second object
            aspects = sorted(
                aspects,
                key=lambda a: (
                    get_object_sort_key(a.object1),
                    get_object_sort_key(a.object2),
                ),
            )

        # Build headers
        headers = ["Planet 1", "Aspect", "Planet 2"]
        if self.orb_display:
            headers.append("Orb")
            headers.append("Applying")

        # Build rows
        rows = []
        for aspect in aspects:
            # Planet 1 with glyph
            name1, glyph1 = get_object_display(aspect.object1.name)
            planet1 = f"{glyph1} {name1}" if glyph1 else name1

            # Aspect with glyph
            aspect_name, aspect_glyph = get_aspect_display(aspect.aspect_name)
            aspect_display = (
                f"{aspect_glyph} {aspect_name}" if aspect_glyph else aspect_name
            )

            # Planet 2 with glyph
            name2, glyph2 = get_object_display(aspect.object2.name)
            planet2 = f"{glyph2} {name2}" if glyph2 else name2

            row = [planet1, aspect_display, planet2]

            if self.orb_display:
                row.append(f"{aspect.orb:.2f}°")

                # Applying/separating
                if aspect.is_applying is None:
                    row.append("—")
                elif aspect.is_applying:
                    row.append("A→")  # Applying
                else:
                    row.append("←S")  # Separating

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class CrossChartAspectSection:
    """
    Table of cross-chart aspects for Comparison charts.

    Shows aspects between chart1 planets and chart2 planets:
    - Chart 1 Planet (with label)
    - Aspect type
    - Chart 2 Planet (with label)
    - Orb (optional)
    - Applying/Separating (optional)
    """

    def __init__(
        self, mode: str = "all", orbs: bool = True, sort_by: str = "orb"
    ) -> None:
        """
        Initialize cross-chart aspect section.

        Args:
            mode: "all", "major", "minor", or "harmonic"
            orbs: Show orb column
            sort_by: How to sort aspects ("orb", "planet", "aspect_type")
        """
        if mode not in ("all", "major", "minor", "harmonic"):
            raise ValueError(
                f"mode must be 'all', 'major', 'minor', or 'harmonic', got {mode}"
            )
        if sort_by not in ("orb", "planet", "aspect_type"):
            raise ValueError(
                f"sort_by must be 'orb', 'planet', or 'aspect_type', got {sort_by}"
            )

        self.mode = mode
        self.orb_display = orbs
        self.sort_by = sort_by

    @property
    def section_name(self) -> str:
        if self.mode == "major":
            return "Cross-Chart Aspects (Major)"
        elif self.mode == "minor":
            return "Cross-Chart Aspects (Minor)"
        elif self.mode == "harmonic":
            return "Cross-Chart Aspects (Harmonic)"
        return "Cross-Chart Aspects"

    def generate_data(self, chart: CalculatedChart | Comparison) -> dict[str, Any]:
        """Generate cross-chart aspects table."""
        # This section only works with Comparison objects
        if not isinstance(chart, Comparison):
            return {
                "type": "text",
                "content": (
                    "Cross-chart aspects require a Comparison object.\n\n"
                    "Example:\n"
                    "  comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()\n"
                    "  report = ReportBuilder().from_chart(comparison).with_cross_aspects().render()"
                ),
            }

        # Get cross-chart aspects
        aspects = list(chart.cross_aspects)

        # Filter aspects based on mode
        if self.mode != "all":
            aspect_category = self.mode.title()
            allowed_aspects = [a.name for a in get_aspects_by_category(aspect_category)]
            aspects = [a for a in aspects if a.aspect_name in allowed_aspects]

        if not aspects:
            return {
                "type": "text",
                "content": "No cross-chart aspects found.",
            }

        # Sort aspects
        if self.sort_by == "orb":
            aspects = sorted(aspects, key=lambda a: a.orb)
        elif self.sort_by == "aspect_type":
            aspects = sorted(aspects, key=lambda a: get_aspect_sort_key(a.aspect_name))
        elif self.sort_by == "planet":
            aspects = sorted(
                aspects,
                key=lambda a: (
                    get_object_sort_key(a.object1),
                    get_object_sort_key(a.object2),
                ),
            )

        # Build headers with chart labels
        chart1_label = chart.chart1_label or "Chart 1"
        chart2_label = chart.chart2_label or "Chart 2"

        headers = [f"{chart1_label}", "Aspect", f"{chart2_label}"]
        if self.orb_display:
            headers.append("Orb")
            headers.append("Applying")

        # Build rows
        rows = []
        for aspect in aspects:
            # Planet 1 with glyph (from chart1)
            name1, glyph1 = get_object_display(aspect.object1.name)
            planet1 = f"{glyph1} {name1}" if glyph1 else name1

            # Aspect with glyph
            aspect_name, aspect_glyph = get_aspect_display(aspect.aspect_name)
            aspect_display = (
                f"{aspect_glyph} {aspect_name}" if aspect_glyph else aspect_name
            )

            # Planet 2 with glyph (from chart2)
            name2, glyph2 = get_object_display(aspect.object2.name)
            planet2 = f"{glyph2} {name2}" if glyph2 else name2

            row = [planet1, aspect_display, planet2]

            if self.orb_display:
                row.append(f"{aspect.orb:.2f}°")

                # Applying/separating
                if aspect.is_applying is None:
                    row.append("—")
                elif aspect.is_applying:
                    row.append("A→")  # Applying
                else:
                    row.append("←S")  # Separating

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class MidpointSection:
    """
    Table of midpoints.

    Shows:
    - Midpoint pair (e.g., "Sun/Moon")
    - Degree position
    - Sign
    """

    CORE_OBJECTS = {"Sun", "Moon", "ASC", "MC"}

    def __init__(self, mode: str = "all", threshold: int | None = None) -> None:
        """
        Initialize midpoint section.

        Args:
            mode: "all" or "core" (only Sun/Moon/ASC/MC midpoints)
            threshold: Only show top N midpoints
        """
        if mode not in ("all", "core"):
            raise ValueError(f"mode must be 'all' or 'core', got {mode}")

        self.mode = mode
        self.threshold = threshold

    @property
    def section_name(self) -> str:
        if self.mode == "core":
            return "Core Midpoints (Sun/Moon/ASC/MC)"
        return "Midpoints"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoints table."""
        # Get midpoints
        midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]
        # Filter to core midpoints if requested
        if self.mode == "core":
            midpoints = [mp for mp in midpoints if self._is_core_midpoint(mp.name)]

        # Sort midpoints by component objects using object1/object2
        def get_midpoint_sort_key(mp):
            # Use isinstance to check if it's a MidpointPosition
            if isinstance(mp, MidpointPosition):
                # Direct access to component objects - use registry order!
                return (
                    get_object_sort_key(mp.object1),
                    get_object_sort_key(mp.object2),
                )
            else:
                # Fallback for legacy CelestialPosition midpoints (backward compatibility)
                # Parse names like "Midpoint:Sun/Moon"
                if ":" in mp.name:
                    pair_part = mp.name.split(":")[1]
                else:
                    pair_part = mp.name

                # Remove "(indirect)" if present
                pair_part = pair_part.replace(" (indirect)", "")

                # Split into component names
                objects = pair_part.split("/")
                if len(objects) == 2:
                    return (objects[0], objects[1])

                # Final fallback: use full name
                return (mp.name,)

        midpoints = sorted(midpoints, key=get_midpoint_sort_key)

        # Apply threshold AFTER sorting (limit to top N)
        if self.threshold:
            midpoints = midpoints[: self.threshold]
        # Build table
        headers = ["Midpoint", "Position"]
        rows = []

        for mp in midpoints:
            # Parse midpoint name (e.g., "Midpoint:Sun/Moon")
            name_parts = mp.name.split(":")
            if len(name_parts) > 1:
                pair_name = name_parts[1]
            else:
                pair_name = mp.name

            # Position
            degree = int(mp.sign_degree)
            minute = int((mp.sign_degree % 1) * 60)
            position = f"{degree}° {mp.sign} {minute:02d}'"

            rows.append([pair_name, position])

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _is_core_midpoint(self, midpoint_name: str) -> bool:
        """Check if midpoint involves core objects."""
        # Midpoint name format: "Midpoint:Sun/Moon" or "Midpoint:Sun/Moon (indirect)"
        if ":" not in midpoint_name:
            return False

        pair_part = midpoint_name.split(":")[1]
        # Remove "(indirect)" if present
        pair_part = pair_part.replace(" (indirect)", "")

        # Split pair
        objects = pair_part.split("/")
        if len(objects) != 2:
            return False

        # Check if both are core objects
        return all(obj in self.CORE_OBJECTS for obj in objects)


class CacheInfoSection:
    """Display cache statistics in reports."""

    @property
    def section_name(self) -> str:
        return "Cache Statistics"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate cache info from chart metadata."""
        cache_stats = chart.metadata.get("cache_stats", {})

        if not cache_stats.get("enabled", False):
            return {"type": "text", "text": "Caching is disabled for this chart."}

        data = {
            "Cache Directory": cache_stats.get("cache_directory", "N/A"),
            "Max Age": f"{cache_stats.get('max_age_seconds', 0) / 3600:.1f} hours",
            "Total Files": cache_stats.get("total_cached_files", 0),
            "Total Size": f"{cache_stats.get('cache_size_mb', 0)} MB",
        }

        # Add breakdown by type
        by_type = cache_stats.get("by_type", {})
        for cache_type, count in by_type.items():
            data[f"{cache_type.title()} Files"] = count

        return {
            "type": "key_value",
            "data": data,
        }


class MoonPhaseSection:
    """Display Moon phase information."""

    @property
    def section_name(self) -> str:
        return "Moon Phase"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate moon phase data."""
        moon = chart.get_object("Moon")

        if not moon or not moon.phase:
            return {"type": "text", "text": "Moon phase data not available."}

        phase = moon.phase

        data = {
            "Phase Name": phase.phase_name,
            "Illumination": f"{phase.illuminated_fraction:.1%}",
            "Phase Angle": f"{phase.phase_angle:.1f}°",
            "Direction": "Waxing" if phase.is_waxing else "Waning",
            "Apparent Magnitude": f"{phase.apparent_magnitude:.2f}",
            "Apparent Diameter": f"{phase.apparent_diameter:.1f}″",
            "Geocentric Parallax": f"{phase.geocentric_parallax:.4f} rad",
        }

        return {
            "type": "key_value",
            "data": data,
        }


class DeclinationSection:
    """Table of planetary declinations.

    Shows:
    - Planet name with glyph
    - Declination value (degrees north/south of celestial equator)
    - Direction (North/South)
    - Out-of-bounds status
    """

    @property
    def section_name(self) -> str:
        return "Declinations"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate declination table data.

        Shows declination values for all planets with equatorial coordinates.
        Highlights out-of-bounds planets (beyond Sun's max declination).
        """
        headers = ["Planet", "Declination", "Direction", "Status"]
        rows = []

        # Get all planets and major points
        all_objects = list(chart.positions)

        for obj in all_objects:
            # Skip if no declination data
            if obj.declination is None:
                continue

            # Skip asteroids and minor points for cleaner display
            if obj.object_type in (ObjectType.ASTEROID, ObjectType.POINT):
                continue

            display_name, glyph = get_object_display(obj.name)
            planet_label = f"{glyph} {display_name}"

            # Format declination as degrees°minutes'
            dec_abs = abs(obj.declination)
            degrees = int(dec_abs)
            minutes = int((dec_abs % 1) * 60)
            dec_str = f"{degrees}°{minutes:02d}'"

            # Direction
            direction = obj.declination_direction.title()

            # Status - mark out-of-bounds planets
            status = "OOB ⚠" if obj.is_out_of_bounds else ""

            rows.append([planet_label, dec_str, direction, status])

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }


class FixedStarsSection:
    """Table of fixed star positions.

    Shows:
    - Star name with glyph
    - Zodiac position (sign + degree)
    - Constellation
    - Magnitude (brightness)
    - Traditional planetary nature
    - Keywords
    """

    def __init__(
        self,
        tier: int | None = None,
        include_keywords: bool = True,
        sort_by: str = "longitude",
    ) -> None:
        """
        Initialize fixed stars section.

        Args:
            tier: Filter to specific tier (1=Royal, 2=Major, 3=Extended).
                  None shows all tiers.
            include_keywords: Include interpretive keywords column
            sort_by: Sort order - "longitude" (zodiacal order),
                    "magnitude" (brightest first), or "tier" (royal first)
        """
        self.tier = tier
        self.include_keywords = include_keywords
        self.sort_by = sort_by

        if sort_by not in ("longitude", "magnitude", "tier"):
            raise ValueError("sort_by must be 'longitude', 'magnitude', or 'tier'")

    @property
    def section_name(self) -> str:
        if self.tier == 1:
            return "Royal Stars"
        elif self.tier == 2:
            return "Major Fixed Stars"
        elif self.tier == 3:
            return "Extended Fixed Stars"
        return "Fixed Stars"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate fixed stars table data."""
        # Get fixed stars from chart positions
        fixed_stars = [
            p for p in chart.positions
            if p.object_type == ObjectType.FIXED_STAR
        ]

        if not fixed_stars:
            return {
                "type": "text",
                "text": (
                    "No fixed stars calculated. Add FixedStarsComponent() to include them:\n\n"
                    "    from stellium.components import FixedStarsComponent\n\n"
                    "    chart = (\n"
                    "        ChartBuilder.from_native(native)\n"
                    "        .add_component(FixedStarsComponent())\n"
                    "        .calculate()\n"
                    "    )"
                ),
            }

        # Filter by tier if specified
        if self.tier is not None:
            fixed_stars = [
                s for s in fixed_stars if hasattr(s, "tier") and s.tier == self.tier
            ]

        # Sort stars
        if self.sort_by == "magnitude":
            fixed_stars = sorted(
                fixed_stars, key=lambda s: getattr(s, "magnitude", 99)
            )
        elif self.sort_by == "tier":
            fixed_stars = sorted(
                fixed_stars, key=lambda s: (getattr(s, "tier", 9), s.longitude)
            )
        else:  # longitude (default)
            fixed_stars = sorted(fixed_stars, key=lambda s: s.longitude)

        # Build headers
        headers = ["Star", "Position", "Constellation", "Mag", "Nature"]
        if self.include_keywords:
            headers.append("Keywords")

        # Build rows
        rows = []
        for star in fixed_stars:
            # Star name with glyph
            tier_marker = ""
            if hasattr(star, "is_royal") and star.is_royal:
                tier_marker = " ♔"  # Crown for royal stars

            star_label = f"★ {star.name}{tier_marker}"

            # Position with sign glyph
            degree = int(star.sign_degree)
            minute = int((star.sign_degree % 1) * 60)
            sign_glyph = get_sign_glyph(star.sign)
            if sign_glyph:
                position = f"{sign_glyph} {star.sign} {degree}°{minute:02d}'"
            else:
                position = f"{star.sign} {degree}°{minute:02d}'"

            # Constellation
            constellation = getattr(star, "constellation", "")

            # Magnitude (lower = brighter)
            magnitude = getattr(star, "magnitude", None)
            mag_str = f"{magnitude:.2f}" if magnitude is not None else "—"

            # Nature
            nature = getattr(star, "nature", "")

            row = [star_label, position, constellation, mag_str, nature]

            # Keywords
            if self.include_keywords:
                keywords = getattr(star, "keywords", ())
                row.append(", ".join(keywords[:3]) if keywords else "")

            rows.append(row)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }
