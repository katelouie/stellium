"""
Report section implementations.

Each section extracts specific data from a CalculatedChart and formats it
into a standardized structure that renderers can consume.
"""

import datetime as dt
from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import (
    CalculatedChart,
    MidpointPosition,
    ObjectType,
    ZRPeriod,
    ZRSnapshot,
    ZRTimeline,
)
from stellium.core.registry import (
    ASPECT_REGISTRY,
    CELESTIAL_REGISTRY,
    get_aspects_by_category,
)
from stellium.engines.dignities import DIGNITIES
from stellium.utils.chart_ruler import get_chart_ruler_from_chart


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

            # Chart Ruler
            try:
                ruler, asc_sign = get_chart_ruler_from_chart(chart)
                data["Chart Ruler"] = f"{ruler} ({asc_sign} Rising)"
            except (ValueError, KeyError):
                pass  # Skip if ASC not found

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

    Optionally includes an aspectarian grid SVG (triangle for single charts).
    """

    def __init__(
        self,
        mode: str = "all",
        orbs: bool = True,
        sort_by: str = "orb",
        include_aspectarian: bool = True,
        aspectarian_detailed: bool = False,
        aspectarian_cell_size: int | None = None,
        aspectarian_theme: str | None = None,
    ) -> None:
        """
        Initialize aspect section.

        Args:
            mode: "all", "major", "minor", or "harmonic"
            orbs: Show orb column in table
            sort_by: "orb", "planet", or "aspect_type"
            include_aspectarian: Include aspectarian grid SVG (default: True)
            aspectarian_detailed: Show orb and A/S in aspectarian cells (default: False)
            aspectarian_cell_size: Override cell size for aspectarian (default: config default)
            aspectarian_theme: Theme for aspectarian rendering (default: None)
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
        self.include_aspectarian = include_aspectarian
        self.aspectarian_detailed = aspectarian_detailed
        self.aspectarian_cell_size = aspectarian_cell_size
        self.aspectarian_theme = aspectarian_theme

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
        """Generate aspects table with optional aspectarian SVG."""
        # Filter aspects based on mode
        aspects = chart.aspects

        # Only filter if not "all" mode
        if self.mode != "all":
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

        table_data = {"type": "table", "headers": headers, "rows": rows}

        # Include aspectarian SVG if requested
        if self.include_aspectarian:
            from stellium.visualization.extended_canvas import generate_aspectarian_svg

            svg_string = generate_aspectarian_svg(
                chart,
                output_path=None,  # Return string
                cell_size=self.aspectarian_cell_size,
                detailed=self.aspectarian_detailed,
                theme=self.aspectarian_theme,
            )

            # Return compound section with SVG first, then table
            return {
                "type": "compound",
                "sections": [
                    ("Aspectarian", {"type": "svg", "content": svg_string}),
                    ("Aspect List", table_data),
                ],
            }

        return table_data


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


class MidpointAspectsSection:
    """
    Table of planets aspecting midpoints.

    This is what most people care about with midpoints: which planets
    activate which midpoints? Typically conjunctions are most important
    (1-2° orb), but hard aspects (square, opposition) can also be shown.

    Shows:
    - Planet that aspects the midpoint
    - Aspect type (conjunction, square, etc.)
    - Midpoint being aspected (e.g., "Sun/Moon")
    - Orb in degrees
    """

    CORE_OBJECTS = {"Sun", "Moon", "ASC", "MC"}

    # Default aspect angles to check (degrees)
    ASPECT_ANGLES = {
        "Conjunction": 0,
        "Opposition": 180,
        "Square": 90,
        "Trine": 120,
        "Sextile": 60,
    }

    def __init__(
        self,
        mode: str = "conjunction",
        orb: float = 1.5,
        midpoint_filter: str = "all",
        sort_by: str = "orb",
    ) -> None:
        """
        Initialize midpoint aspects section.

        Args:
            mode: Which aspects to show
                - "conjunction": Only conjunctions (most common, recommended)
                - "hard": Conjunction, square, opposition
                - "all": All major aspects
            orb: Maximum orb in degrees (default 1.5°, typical for midpoints)
            midpoint_filter: Which midpoints to check
                - "all": All midpoints
                - "core": Only Sun/Moon/ASC/MC midpoints
            sort_by: Sort order
                - "orb": Tightest aspects first (default)
                - "planet": Group by aspecting planet
                - "midpoint": Group by midpoint
        """
        valid_modes = ("conjunction", "hard", "all")
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}, got {mode}")

        valid_sorts = ("orb", "planet", "midpoint")
        if sort_by not in valid_sorts:
            raise ValueError(f"sort_by must be one of {valid_sorts}, got {sort_by}")

        self.mode = mode
        self.orb = orb
        self.midpoint_filter = midpoint_filter
        self.sort_by = sort_by

        # Set which aspects to check based on mode
        if mode == "conjunction":
            self._aspects = {"Conjunction": 0}
        elif mode == "hard":
            self._aspects = {
                "Conjunction": 0,
                "Square": 90,
                "Opposition": 180,
            }
        else:  # all
            self._aspects = self.ASPECT_ANGLES.copy()

    @property
    def section_name(self) -> str:
        if self.mode == "conjunction":
            return "Planets Conjunct Midpoints"
        elif self.mode == "hard":
            return "Hard Aspects to Midpoints"
        return "Aspects to Midpoints"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoint aspects table."""
        # Get midpoints
        midpoints = [p for p in chart.positions if p.object_type == ObjectType.MIDPOINT]

        if not midpoints:
            return {
                "type": "text",
                "text": (
                    "No midpoints calculated. Add MidpointCalculator() to include them:\n\n"
                    "    from stellium.components import MidpointCalculator\n\n"
                    "    chart = (\n"
                    "        ChartBuilder.from_native(native)\n"
                    "        .add_component(MidpointCalculator())\n"
                    "        .calculate()\n"
                    "    )"
                ),
            }

        # Filter to core midpoints if requested
        if self.midpoint_filter == "core":
            midpoints = [mp for mp in midpoints if self._is_core_midpoint(mp.name)]

        # Get planets/points to check (exclude midpoints and fixed stars)
        planets = [
            p
            for p in chart.positions
            if p.object_type
            in (
                ObjectType.PLANET,
                ObjectType.NODE,
                ObjectType.POINT,
                ObjectType.ANGLE,
            )
        ]

        # Find aspects between planets and midpoints
        found_aspects = []

        for planet in planets:
            for midpoint in midpoints:
                # Skip if planet is one of the midpoint's components
                if isinstance(midpoint, MidpointPosition):
                    if planet.name in (midpoint.object1.name, midpoint.object2.name):
                        continue

                # Check each aspect type
                for aspect_name, aspect_angle in self._aspects.items():
                    orb = self._calculate_orb(
                        planet.longitude, midpoint.longitude, aspect_angle
                    )

                    if orb <= self.orb:
                        # Parse midpoint display name
                        mp_display = self._get_midpoint_display(midpoint)

                        found_aspects.append(
                            {
                                "planet": planet,
                                "aspect": aspect_name,
                                "midpoint": midpoint,
                                "midpoint_display": mp_display,
                                "orb": orb,
                            }
                        )

        if not found_aspects:
            return {
                "type": "text",
                "text": f"No planets found within {self.orb}° of midpoints.",
            }

        # Sort results
        if self.sort_by == "orb":
            found_aspects.sort(key=lambda x: x["orb"])
        elif self.sort_by == "planet":
            found_aspects.sort(
                key=lambda x: (
                    get_object_sort_key(x["planet"]),
                    x["orb"],
                )
            )
        else:  # midpoint
            found_aspects.sort(
                key=lambda x: (
                    x["midpoint_display"],
                    x["orb"],
                )
            )

        # Build table
        headers = ["Planet", "Aspect", "Midpoint", "Orb"]
        rows = []

        for asp in found_aspects:
            planet = asp["planet"]
            display_name, glyph = get_object_display(planet.name)
            planet_label = f"{glyph} {display_name}" if glyph else display_name

            aspect_name, aspect_glyph = get_aspect_display(asp["aspect"])
            aspect_label = (
                f"{aspect_glyph} {aspect_name}" if aspect_glyph else aspect_name
            )

            orb_str = f"{asp['orb']:.2f}°"

            rows.append([planet_label, aspect_label, asp["midpoint_display"], orb_str])

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _calculate_orb(self, lon1: float, lon2: float, aspect_angle: float) -> float:
        """Calculate orb between two longitudes for a given aspect."""
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff

        return abs(diff - aspect_angle)

    def _is_core_midpoint(self, midpoint_name: str) -> bool:
        """Check if midpoint involves core objects."""
        if ":" not in midpoint_name:
            return False

        pair_part = midpoint_name.split(":")[1]
        pair_part = pair_part.replace(" (indirect)", "")

        objects = pair_part.split("/")
        if len(objects) != 2:
            return False

        return all(obj in self.CORE_OBJECTS for obj in objects)

    def _get_midpoint_display(self, midpoint) -> str:
        """Get display name for a midpoint."""
        if ":" in midpoint.name:
            pair_part = midpoint.name.split(":")[1]
        else:
            pair_part = midpoint.name

        # Remove "(indirect)" but add marker
        if "(indirect)" in pair_part:
            pair_part = pair_part.replace(" (indirect)", "") + "*"

        return pair_part


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
            p for p in chart.positions if p.object_type == ObjectType.FIXED_STAR
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
            fixed_stars = sorted(fixed_stars, key=lambda s: getattr(s, "magnitude", 99))
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


class ProfectionSection:
    """
    Profection timing analysis section.

    Shows annual profections with Lord of the Year, activated house,
    and optionally monthly profections and multi-point analysis.
    """

    def __init__(
        self,
        age: int | None = None,
        date: dt.datetime | str | None = None,
        include_monthly: bool = True,
        include_multi_point: bool = True,
        include_timeline: bool = False,
        timeline_range: tuple[int, int] | None = None,
        points: list[str] | None = None,
        house_system: str | None = None,
        rulership: str = "traditional",
    ) -> None:
        """
        Initialize profection section.

        Args:
            age: Age for profection (either age OR date required)
            date: Target date for profection (datetime or ISO string)
            include_monthly: Show monthly profection (when date provided)
            include_multi_point: Show profections for ASC, Sun, Moon, MC
            include_timeline: Show timeline of Lords
            timeline_range: Range for timeline, e.g., (25, 40). If None, uses age±5
            points: Custom points for multi-point (default: ASC, Sun, Moon, MC)
            house_system: House system to use (default: prefers Whole Sign)
            rulership: "traditional" or "modern"
        """
        if age is None and date is None:
            raise ValueError("Either age or date must be provided for profections")

        self.age = age
        self.date = date
        self.include_monthly = include_monthly
        self.include_multi_point = include_multi_point
        self.include_timeline = include_timeline
        self.timeline_range = timeline_range
        self.points = points
        self.house_system = house_system
        self.rulership = rulership

    @property
    def section_name(self) -> str:
        if self.age is not None:
            return f"Profections (Age {self.age})"
        elif self.date:
            date_str = (
                self.date
                if isinstance(self.date, str)
                else self.date.strftime("%Y-%m-%d")
            )
            return f"Profections ({date_str})"
        return "Profections"

    def generate_data(self, chart: CalculatedChart) -> dict:
        """
        Generate profection analysis data.
        """
        from stellium.engines.profections import ProfectionEngine

        # Create engine
        try:
            engine = ProfectionEngine(chart, self.house_system, self.rulership)
        except ValueError as e:
            return {
                "type": "text",
                "content": f"Could not calculate profections: {e}",
            }

        # Calculate the age
        if self.date is not None:
            if isinstance(self.date, str):
                target_date = dt.datetime.fromisoformat(self.date)
            else:
                target_date = self.date
            age = engine._calculate_age_at_date(target_date)
        else:
            age = self.age
            target_date = None

        # Build result sections
        sections = []

        # Section 1: Annual Profection Summary
        annual = engine.annual(age)
        summary_data = self._build_annual_summary(annual, engine.house_system)
        sections.append(("Annual Profection", summary_data))

        # Section 2: Monthly Profection (if date provided)
        if self.include_monthly and target_date is not None:
            annual_result, monthly_result = engine.for_date(target_date)
            monthly_data = self._build_monthly_summary(monthly_result, age)
            sections.append(("Monthly Profection", monthly_data))

        # Section 3: Multi-Point Lords
        if self.include_multi_point:
            multi = engine.multi(age, self.points)
            multi_data = self._build_multi_point_table(multi)
            sections.append(("All Lords", multi_data))

        # Section 4: Planets in Profected House
        if annual.planets_in_house:
            planets_data = self._build_planets_in_house(annual)
            sections.append(("Natal Planets in Activated House", planets_data))

        # Section 5: Lord's Natal Condition
        lord_data = self._build_lord_condition(annual)
        sections.append(("Lord of Year - Natal Condition", lord_data))

        # Section 6: Timeline (if enabled)
        if self.include_timeline:
            if self.timeline_range:
                start, end = self.timeline_range
            else:
                # Default: age ± 5
                start = max(0, age - 5)
                end = age + 5

            timeline = engine.timeline(start, end)
            timeline_data = self._build_timeline_table(timeline, age)
            sections.append((f"Timeline (Ages {start}-{end})", timeline_data))

        # Build compound result
        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_annual_summary(self, result, house_system: str) -> dict:
        """Build the annual profection summary."""
        # Get ruler glyph
        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        # Get sign glyph
        sign_glyph = get_sign_glyph(result.profected_sign)

        data = {
            "Age": str(result.units),
            "Activated House": f"House {result.profected_house}",
            "Activated Sign": f"{sign_glyph} {result.profected_sign}",
            "Lord of the Year": f"{ruler_glyph} {result.ruler}",
            "House System": house_system,
        }

        if result.ruler_modern:
            modern_glyph = ""
            if result.ruler_modern in CELESTIAL_REGISTRY:
                modern_glyph = CELESTIAL_REGISTRY[result.ruler_modern].glyph
            data["Modern Ruler"] = f"{modern_glyph} {result.ruler_modern}"

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_monthly_summary(self, result, age: int) -> dict:
        """Build monthly profection summary."""
        month = result.units - age

        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        sign_glyph = get_sign_glyph(result.profected_sign)

        data = {
            "Month in Year": str(month),
            "Activated House": f"House {result.profected_house}",
            "Activated Sign": f"{sign_glyph} {result.profected_sign}",
            "Lord of the Month": f"{ruler_glyph} {result.ruler}",
        }

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_multi_point_table(self, multi) -> dict:
        """Build multi-point lords table."""
        headers = ["Point", "Activated House", "Sign", "Lord"]
        rows = []

        for point, result in multi.results.items():
            point_glyph = ""
            if point in CELESTIAL_REGISTRY:
                point_glyph = CELESTIAL_REGISTRY[point].glyph

            sign_glyph = get_sign_glyph(result.profected_sign)

            ruler_glyph = ""
            if result.ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

            rows.append(
                [
                    f"{point_glyph} {point}" if point_glyph else point,
                    f"House {result.profected_house}",
                    f"{sign_glyph} {result.profected_sign}",
                    f"{ruler_glyph} {result.ruler}",
                ]
            )

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _build_planets_in_house(self, result) -> dict:
        """Build list of natal planets in the activated house."""
        planet_names = []
        for planet in result.planets_in_house:
            glyph = ""
            if planet.name in CELESTIAL_REGISTRY:
                glyph = CELESTIAL_REGISTRY[planet.name].glyph
            planet_names.append(f"{glyph} {planet.name}" if glyph else planet.name)

        return {
            "type": "text",
            "content": f"House {result.profected_house} contains: {', '.join(planet_names)}",
        }

    def _build_lord_condition(self, result) -> dict:
        """Build Lord of Year natal condition details."""
        if result.ruler_position is None:
            return {
                "type": "text",
                "content": f"{result.ruler} position not found in chart.",
            }

        pos = result.ruler_position
        ruler_glyph = ""
        if result.ruler in CELESTIAL_REGISTRY:
            ruler_glyph = CELESTIAL_REGISTRY[result.ruler].glyph

        sign_glyph = get_sign_glyph(pos.sign)

        # Format degree/minute
        degree = int(pos.sign_degree)
        minute = int((pos.sign_degree % 1) * 60)

        data = {
            "Planet": f"{ruler_glyph} {result.ruler}",
            "Natal Sign": f"{sign_glyph} {pos.sign}",
            "Natal Degree": f"{degree}°{minute:02d}'",
            "Natal House": f"House {result.ruler_house}" if result.ruler_house else "—",
            "Retrograde": "Yes ℞" if pos.is_retrograde else "No",
        }

        return {
            "type": "key_value",
            "data": data,
        }

    def _build_timeline_table(self, timeline, current_age: int) -> dict:
        """Build timeline table with Lords sequence."""
        headers = ["Age", "House", "Sign", "Lord"]
        rows = []

        for entry in timeline.entries:
            sign_glyph = get_sign_glyph(entry.profected_sign)
            ruler_glyph = ""
            if entry.ruler in CELESTIAL_REGISTRY:
                ruler_glyph = CELESTIAL_REGISTRY[entry.ruler].glyph

            # Mark current age
            age_str = str(entry.units)
            if entry.units == current_age:
                age_str = f"→ {entry.units} ←"

            rows.append(
                [
                    age_str,
                    f"House {entry.profected_house}",
                    f"{sign_glyph} {entry.profected_sign}",
                    f"{ruler_glyph} {entry.ruler}",
                ]
            )

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }


class DeclinationAspectSection:
    """
    Table of declination aspects (Parallel and Contraparallel).

    Shows:
    - Planet 1 (with glyph)
    - Aspect type (Parallel ∥ or Contraparallel ⋕)
    - Planet 2 (with glyph)
    - Orb (optional)
    - Out-of-bounds status (if either planet is OOB)
    """

    def __init__(
        self,
        mode: str = "all",
        show_orbs: bool = True,
        show_oob_status: bool = True,
        sort_by: str = "orb",
    ) -> None:
        """
        Initialize declination aspect section.

        Args:
            mode: "all", "parallel", or "contraparallel"
            show_orbs: Whether to show the orb column
            show_oob_status: Whether to show out-of-bounds status
            sort_by: How to sort aspects ("orb", "planet", "aspect_type")
        """
        if mode not in ("all", "parallel", "contraparallel"):
            raise ValueError(
                f"mode must be 'all', 'parallel', or 'contraparallel', got {mode}"
            )
        if sort_by not in ("orb", "planet", "aspect_type"):
            raise ValueError(
                f"sort_by must be 'orb', 'planet', or 'aspect_type', got {sort_by}"
            )

        self.mode = mode
        self.show_orbs = show_orbs
        self.show_oob_status = show_oob_status
        self.sort_by = sort_by

    @property
    def section_name(self) -> str:
        if self.mode == "parallel":
            return "Parallel Aspects"
        elif self.mode == "contraparallel":
            return "Contraparallel Aspects"
        return "Declination Aspects"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate declination aspects table."""
        # Get declination aspects
        aspects = list(chart.declination_aspects)

        if not aspects:
            return {
                "type": "text",
                "content": (
                    "No declination aspects calculated. Enable with:\n\n"
                    "  chart = (ChartBuilder.from_native(native)\n"
                    "      .with_aspects()\n"
                    "      .with_declination_aspects(orb=1.0)\n"
                    "      .calculate())"
                ),
            }

        # Filter by mode
        if self.mode == "parallel":
            aspects = [a for a in aspects if a.aspect_name == "Parallel"]
        elif self.mode == "contraparallel":
            aspects = [a for a in aspects if a.aspect_name == "Contraparallel"]

        if not aspects:
            return {
                "type": "text",
                "content": f"No {self.mode} aspects found.",
            }

        # Sort
        if self.sort_by == "orb":
            aspects = sorted(aspects, key=lambda a: a.orb)
        elif self.sort_by == "aspect_type":
            aspects = sorted(aspects, key=lambda a: a.aspect_name)
        elif self.sort_by == "planet":
            aspects = sorted(
                aspects,
                key=lambda a: (
                    get_object_sort_key(a.object1),
                    get_object_sort_key(a.object2),
                ),
            )

        # Build headers
        headers = ["Planet 1", "Aspect", "Planet 2"]
        if self.show_orbs:
            headers.append("Orb")
        if self.show_oob_status:
            headers.append("OOB")

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

            if self.show_orbs:
                row.append(f"{aspect.orb:.2f}°")

            if self.show_oob_status:
                oob_markers = []
                if aspect.object1.is_out_of_bounds:
                    oob_markers.append(aspect.object1.name[:2])
                if aspect.object2.is_out_of_bounds:
                    oob_markers.append(aspect.object2.name[:2])
                row.append(", ".join(oob_markers) if oob_markers else "")

            rows.append(row)

        return {"type": "table", "headers": headers, "rows": rows}


class DispositorSection:
    """
    Dispositor analysis section.

    Shows planetary and/or house-based dispositor chains, final dispositor(s),
    and mutual receptions. Text summary only - graphviz rendering is separate.

    Example:
        >>> section = DispositorSection(mode="both")
        >>> data = section.generate_data(chart)
    """

    def __init__(
        self,
        mode: str = "both",
        rulership: str = "traditional",
        house_system: str | None = None,
        show_chains: bool = True,
    ) -> None:
        """
        Initialize dispositor section.

        Args:
            mode: Which dispositor analysis to show:
                - "planetary": Traditional planet-disposes-planet
                - "house": Kate's house-based innovation
                - "both": Show both (DEFAULT)
            rulership: "traditional" or "modern" rulership system
            house_system: House system for house-based mode (defaults to chart's default)
            show_chains: Whether to show full chain details
        """
        self.mode = mode
        self.rulership = rulership
        self.house_system = house_system
        self.show_chains = show_chains

    @property
    def section_name(self) -> str:
        if self.mode == "planetary":
            return "Planetary Dispositors"
        elif self.mode == "house":
            return "House Dispositors"
        return "Dispositors"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """
        Generate dispositor analysis.

        Returns a compound section with subsections for planetary and/or house
        dispositors, each showing final dispositor and mutual receptions.
        """
        from stellium.engines.dispositors import DispositorEngine

        engine = DispositorEngine(
            chart,
            rulership_system=self.rulership,
            house_system=self.house_system,
        )

        sections = []

        # Planetary dispositors
        if self.mode in ("planetary", "both"):
            planetary = engine.planetary()
            sections.append(self._format_result(planetary, "Planetary"))

        # House dispositors
        if self.mode in ("house", "both"):
            house = engine.house_based()
            sections.append(self._format_result(house, "House-Based"))

        # If only one mode, return that directly (as text with section content)
        if len(sections) == 1:
            title, data = sections[0]
            return {
                "type": "text",
                "text": data.get("content", ""),
            }

        # Otherwise return compound section (list of tuples)
        return {
            "type": "compound",
            "sections": sections,
        }

    def _format_result(self, result, title: str) -> dict[str, Any]:
        """Format a DispositorResult for display."""
        from stellium.core.registry import CELESTIAL_REGISTRY

        lines = []

        # Final dispositor
        if result.final_dispositor:
            if isinstance(result.final_dispositor, tuple):
                if result.mode == "planetary":
                    # Format with glyphs
                    fd_parts = []
                    for planet in result.final_dispositor:
                        if planet in CELESTIAL_REGISTRY:
                            glyph = CELESTIAL_REGISTRY[planet].glyph
                            fd_parts.append(f"{glyph} {planet}")
                        else:
                            fd_parts.append(planet)
                    fd_str = " ↔ ".join(fd_parts)
                    lines.append(f"Final Dispositor: {fd_str} (mutual reception)")
                else:
                    fd_str = " ↔ ".join([f"House {h}" for h in result.final_dispositor])
                    lines.append(f"Final Dispositor: {fd_str} (mutual reception)")
            else:
                if result.mode == "planetary":
                    if result.final_dispositor in CELESTIAL_REGISTRY:
                        glyph = CELESTIAL_REGISTRY[result.final_dispositor].glyph
                        lines.append(
                            f"Final Dispositor: {glyph} {result.final_dispositor}"
                        )
                    else:
                        lines.append(f"Final Dispositor: {result.final_dispositor}")
                else:
                    lines.append(f"Final Dispositor: House {result.final_dispositor}")
        else:
            lines.append("Final Dispositor: None (complex loop structure)")

        # Mutual receptions
        if result.mutual_receptions:
            lines.append("")
            lines.append("Mutual Receptions:")
            for mr in result.mutual_receptions:
                if result.mode == "planetary":
                    glyph1 = CELESTIAL_REGISTRY.get(mr.node1, {})
                    glyph2 = CELESTIAL_REGISTRY.get(mr.node2, {})
                    g1 = glyph1.glyph if hasattr(glyph1, "glyph") else ""
                    g2 = glyph2.glyph if hasattr(glyph2, "glyph") else ""
                    lines.append(f"  {g1} {mr.node1} ↔ {g2} {mr.node2}")
                else:
                    # House mode - include ruling planets
                    lines.append(
                        f"  House {mr.node1} ({mr.planet1}) ↔ "
                        f"House {mr.node2} ({mr.planet2})"
                    )

        # Chains (optional)
        if self.show_chains and result.chains:
            lines.append("")
            lines.append("Disposition Chains:")
            for _start, chain in sorted(result.chains.items()):
                if result.mode == "planetary":
                    # Format with glyphs
                    chain_parts = []
                    for node in chain:
                        if node in CELESTIAL_REGISTRY:
                            chain_parts.append(CELESTIAL_REGISTRY[node].glyph)
                        else:
                            chain_parts.append(node)
                    chain_str = " → ".join(chain_parts)
                else:
                    chain_str = " → ".join(chain)
                lines.append(f"  {chain_str}")

        # Return as tuple of (title, data) for compound rendering
        return (
            f"{title} Dispositors",
            {
                "type": "text",
                "content": "\n".join(lines),
            },
        )


class ZodiacalReleasingSection:
    """
    Zodiacal Releasing timing analysis section.

    Shows ZR periods from one or more Lots (Fortune, Spirit, etc.),
    with options to display current snapshot and/or L1 timeline.

    Snapshot mode shows:
    - Current L1/L2 periods (always shown)
    - L3/L4 context (current ± 2 periods) for finer timing

    Timeline mode shows:
    - All L1 periods with ages and status indicators
    - Peak (★), Angular (◆), and Current (⚡) markers
    """

    def __init__(
        self,
        lots: str | list[str] | None = None,
        mode: str = "both",
        query_date: dt.datetime | str | None = None,
        query_age: float | None = None,
        context_periods: int = 2,
    ) -> None:
        """
        Initialize Zodiacal Releasing section.

        Args:
            lots: Which lot(s) to display:
                - str: Single lot name (e.g., "Part of Fortune")
                - list[str]: Multiple lots (e.g., ["Part of Fortune", "Part of Spirit"])
                - None or "all": All lots calculated in the chart
            mode: Display mode:
                - "snapshot": Current periods only
                - "timeline": L1 timeline only
                - "both": Both snapshot and timeline (DEFAULT)
            query_date: Date for snapshot (defaults to now)
                - datetime: Use this date
                - str: Parse as ISO format
                - None: Use current date/time
            query_age: Age for snapshot (alternative to query_date)
                - float: Use this age
                - None: Calculate from query_date
            context_periods: Number of periods before/after current to show
                for L3/L4 context (default: 2)
        """
        # Normalize lots parameter
        if lots is None or lots == "all":
            self._lots_mode = "all"
            self._lots = None
        elif isinstance(lots, str):
            self._lots_mode = "specific"
            self._lots = [lots]
        else:
            self._lots_mode = "specific"
            self._lots = list(lots)

        if mode not in ("snapshot", "timeline", "both"):
            raise ValueError(
                f"mode must be 'snapshot', 'timeline', or 'both', got {mode}"
            )

        self.mode = mode
        self.context_periods = context_periods

        # Handle query date/age
        if query_date is not None:
            if isinstance(query_date, str):
                self._query_date = dt.datetime.fromisoformat(query_date)
            else:
                self._query_date = query_date
            self._query_age = None
        elif query_age is not None:
            self._query_date = None
            self._query_age = query_age
        else:
            # Default to now
            self._query_date = dt.datetime.now(dt.UTC)
            self._query_age = None

    @property
    def section_name(self) -> str:
        return "Zodiacal Releasing"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate Zodiacal Releasing data."""
        # Check if ZR data exists
        if "zodiacal_releasing" not in chart.metadata:
            return {
                "type": "text",
                "content": (
                    "Zodiacal Releasing not calculated. Add ZodiacalReleasingAnalyzer:\n\n"
                    "  from stellium.engines.releasing import ZodiacalReleasingAnalyzer\n\n"
                    "  chart = (\n"
                    "      ChartBuilder.from_native(native)\n"
                    "      .add_analyzer(ZodiacalReleasingAnalyzer(['Part of Fortune']))\n"
                    "      .calculate()\n"
                    "  )"
                ),
            }

        zr_data = chart.metadata["zodiacal_releasing"]

        # Determine which lots to show
        if self._lots_mode == "all":
            lots_to_show = list(zr_data.keys())
        else:
            lots_to_show = [lot for lot in self._lots if lot in zr_data]

        if not lots_to_show:
            return {
                "type": "text",
                "content": "No Zodiacal Releasing data found for the specified lot(s).",
            }

        # Build sections for each lot
        sections = []

        for lot_name in lots_to_show:
            timeline: ZRTimeline = zr_data[lot_name]

            # Get snapshot for query date/age
            try:
                if self._query_age is not None:
                    snapshot = timeline.at_age(self._query_age)
                else:
                    snapshot = timeline.at_date(self._query_date)
            except ValueError:
                # Date outside timeline range - use age 0 as fallback
                snapshot = timeline.at_age(0)

            # Build lot header
            lot_title = f"{lot_name} ({timeline.lot_sign})"

            if self.mode in ("snapshot", "both"):
                # Add snapshot section
                snapshot_data = self._build_snapshot(timeline, snapshot, chart)
                sections.append((lot_title, snapshot_data))

            if self.mode in ("timeline", "both"):
                # Add timeline section
                timeline_data = self._build_timeline(timeline, snapshot)
                timeline_title = (
                    f"{lot_name} — L1 Timeline" if self.mode == "both" else lot_title
                )
                sections.append((timeline_title, timeline_data))

        # Return as compound section
        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_snapshot(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot, chart: CalculatedChart
    ) -> dict[str, Any]:
        """Build snapshot display showing current periods at all levels."""
        sections = []

        # Header info
        query_date_str = snapshot.date.strftime("%B %d, %Y")
        header_data = {
            "Current Age": f"{snapshot.age:.1f} years ({query_date_str})",
            "Active Rulers": ", ".join(self._format_rulers(snapshot.rulers)),
        }

        # Add status indicators
        status_parts = []
        if snapshot.is_peak:
            status_parts.append("★ Peak Period")
        if snapshot.is_lb:
            status_parts.append("⚡ Loosing of Bond")
        if status_parts:
            header_data["Status"] = " | ".join(status_parts)

        sections.append(("Current State", {"type": "key_value", "data": header_data}))

        # L1/L2 table (always show)
        l1_l2_table = self._build_l1_l2_table(snapshot, chart)
        sections.append(("Major Periods", l1_l2_table))

        # L3 context (if available)
        if snapshot.l3 is not None:
            l3_context = self._build_level_context(timeline, snapshot, level=3)
            sections.append(("L3 Context", l3_context))

        # L4 context (if available)
        if snapshot.l4 is not None:
            l4_context = self._build_level_context(timeline, snapshot, level=4)
            sections.append(("L4 Context", l4_context))

        return {
            "type": "compound",
            "sections": sections,
        }

    def _build_l1_l2_table(
        self, snapshot: ZRSnapshot, chart: CalculatedChart
    ) -> dict[str, Any]:
        """Build table for L1 and L2 periods."""
        headers = ["Level", "Sign", "Ruler", "Period", "Quality", "Status"]
        rows = []

        # L1 row
        l1 = snapshot.l1
        l1_age_start = (l1.start - chart.datetime.utc_datetime).days / 365.25
        l1_age_end = (l1.end - chart.datetime.utc_datetime).days / 365.25
        l1_period = f"Ages {l1_age_start:.0f} - {l1_age_end:.0f}"
        l1_status = self._format_period_status(l1)
        l1_quality = self._format_quality(l1)

        rows.append(
            [
                "L1 (Major)",
                f"{get_sign_glyph(l1.sign)} {l1.sign}",
                self._format_ruler(l1.ruler),
                l1_period,
                l1_quality,
                l1_status,
            ]
        )

        # L2 row
        l2 = snapshot.l2
        l2_start = l2.start.strftime("%b %Y")
        l2_end = l2.end.strftime("%b %Y")
        l2_period = f"{l2_start} - {l2_end}"
        l2_status = self._format_period_status(l2)
        l2_quality = self._format_quality(l2)

        rows.append(
            [
                "L2 (Sub)",
                f"{get_sign_glyph(l2.sign)} {l2.sign}",
                self._format_ruler(l2.ruler),
                l2_period,
                l2_quality,
                l2_status,
            ]
        )

        return {"type": "table", "headers": headers, "rows": rows}

    def _build_level_context(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot, level: int
    ) -> dict[str, Any]:
        """Build context table for L3 or L4 showing periods around current."""
        periods = timeline.periods.get(level, [])
        if not periods:
            return {"type": "text", "content": f"No L{level} data available."}

        # Find current period index
        current_period = snapshot.l3 if level == 3 else snapshot.l4
        if current_period is None:
            return {"type": "text", "content": f"No L{level} data available."}

        # Find index of current period
        current_idx = None
        for i, p in enumerate(periods):
            if p.start == current_period.start:
                current_idx = i
                break

        if current_idx is None:
            return {
                "type": "text",
                "content": f"Could not locate current L{level} period.",
            }

        # Get context window
        start_idx = max(0, current_idx - self.context_periods)
        end_idx = min(len(periods), current_idx + self.context_periods + 1)
        context_periods = periods[start_idx:end_idx]

        # Build table
        headers = ["Sign", "Ruler", "Period", "Status"]
        rows = []

        for period in context_periods:
            is_current = period.start == current_period.start

            # Format sign with current marker
            sign_str = f"{get_sign_glyph(period.sign)} {period.sign}"
            if is_current:
                sign_str = f"⚡ {sign_str}"

            # Format dates
            start_str = period.start.strftime("%b %d")
            end_str = period.end.strftime("%b %d")
            period_str = f"{start_str} - {end_str}"

            # Status
            status = self._format_period_status(period)

            rows.append(
                [sign_str, self._format_ruler(period.ruler), period_str, status]
            )

        return {"type": "table", "headers": headers, "rows": rows}

    def _build_timeline(
        self, timeline: ZRTimeline, snapshot: ZRSnapshot
    ) -> dict[str, Any]:
        """Build L1 timeline table."""
        l1_periods = timeline.l1_periods()

        if not l1_periods:
            return {"type": "text", "content": "No L1 timeline data available."}

        headers = ["Sign", "Ruler", "Ages", "Quality", "Status"]
        rows = []

        for period in l1_periods:
            is_current = (
                period.start <= snapshot.date < period.end
                if snapshot.l1.start == period.start
                else False
            )
            # Actually check if this is the current L1
            is_current = period.start == snapshot.l1.start

            # Calculate ages
            age_start = (period.start - timeline.birth_date).days / 365.25
            age_end = (period.end - timeline.birth_date).days / 365.25

            # Format sign with current marker
            sign_str = f"{get_sign_glyph(period.sign)} {period.sign}"
            if is_current:
                sign_str = f"⚡ {sign_str}"

            # Format ages
            ages_str = f"{age_start:3.0f} - {age_end:3.0f}"

            # Quality
            quality = self._format_quality(period)

            # Status
            status = self._format_period_status(period)

            rows.append(
                [sign_str, self._format_ruler(period.ruler), ages_str, quality, status]
            )

        # Add legend
        legend = "★ = Peak (10th)  ◆ = Angular  ⚡ = Current  LB = Loosing of Bond  +/- = Quality Score"

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
            "footer": legend,
        }

    def _format_period_status(self, period: ZRPeriod) -> str:
        """Format status indicators for a period."""
        parts = []
        if period.is_peak:
            parts.append("★ Peak (10th)")
        elif period.is_angular:
            parts.append(f"◆ Angular ({period.angle_from_lot})")
        if period.is_loosing_bond:
            parts.append("LB")
        return " | ".join(parts) if parts else ""

    def _format_quality(self, period: ZRPeriod) -> str:
        """Format quality/scoring information for a period."""
        # Build quality string with score and sentiment
        score_str = f"{period.score:+d}"

        # Add sentiment icon
        if period.sentiment == "positive":
            sentiment_icon = "✓"
        elif period.sentiment == "challenging":
            sentiment_icon = "✗"
        else:
            sentiment_icon = "—"

        quality = f"{score_str} {sentiment_icon}"

        # Optionally add role info (if present and not too long)
        roles = []
        if period.ruler_role:
            # Shorten role names for display
            role_map = {
                "sect_benefic": "S.Ben",
                "contrary_benefic": "C.Ben",
                "sect_malefic": "S.Mal",
                "contrary_malefic": "C.Mal",
                "sect_light": "S.Lgt",
                "contrary_light": "C.Lgt",
            }
            roles.append(role_map.get(period.ruler_role, period.ruler_role))

        if roles:
            quality += f" ({', '.join(roles)})"

        return quality

    def _format_ruler(self, ruler: str) -> str:
        """Format ruler with glyph."""
        if ruler in CELESTIAL_REGISTRY:
            glyph = CELESTIAL_REGISTRY[ruler].glyph
            return f"{glyph} {ruler}"
        return ruler

    def _format_rulers(self, rulers: list[str]) -> list[str]:
        """Format multiple rulers with glyphs."""
        return [self._format_ruler(r) for r in rulers]


class ArabicPartsSection:
    """
    Table of Arabic Parts (Lots).

    Shows calculated Arabic Parts with their positions, house placements,
    and optionally their formulas and descriptions.

    Modes:
    - "all": All calculated parts
    - "core": 7 Hermetic Lots (Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis)
    - "family": Family & Relationship Lots (Father, Mother, Marriage, Children, Siblings)
    - "life": Life Topic Lots (Action, Profession, Passion, Illness, Death, etc.)
    - "planetary": Planetary Exaltation Lots (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn)
    """

    # Category definitions for filtering
    CORE_PARTS = {
        "Part of Fortune",
        "Part of Spirit",
        "Part of Eros (Love)",
        "Part of Eros (Planetary)",
        "Part of Necessity (Ananke)",
        "Part of Courage (Tolma)",
        "Part of Victory (Nike)",
        "Part of Nemesis",
    }

    FAMILY_PARTS = {
        "Part of Father",
        "Part of Mother",
        "Part of Marriage",
        "Part of Children",
        "Part of Siblings",
    }

    LIFE_PARTS = {
        "Part of Action (Praxis)",
        "Part of Profession (User)",
        "Part of Passion / Lust",
        "Part of Illness / Disease",
        "Part of Death",
        "Part of Debt / Bondage",
        "Part of Travel",
        "Part of Friends / Associates",
    }

    PLANETARY_PARTS = {
        "Part of the Sun (Exaltation)",
        "Part of the Moon (Exaltation)",
        "Part of Mercury (Exaltation)",
        "Part of Venus (Exaltation)",
        "Part of Mars (Exaltation)",
        "Part of Jupiter (Exaltation)",
        "Part of Saturn (Exaltation)",
    }

    # Import the catalog for formula lookups
    from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG

    def __init__(
        self,
        mode: str = "all",
        show_formula: bool = True,
        show_description: bool = False,
    ) -> None:
        """
        Initialize Arabic Parts section.

        Args:
            mode: Which parts to display:
                - "all": All calculated parts (default)
                - "core": 7 Hermetic Lots
                - "family": Family & Relationship Lots
                - "life": Life Topic Lots
                - "planetary": Planetary Exaltation Lots
            show_formula: Include the formula column (default True)
            show_description: Include part descriptions (default False)
        """
        valid_modes = ("all", "core", "family", "life", "planetary")
        if mode not in valid_modes:
            raise ValueError(f"mode must be one of {valid_modes}, got {mode}")

        self.mode = mode
        self.show_formula = show_formula
        self.show_description = show_description

    @property
    def section_name(self) -> str:
        mode_names = {
            "all": "Arabic Parts",
            "core": "Arabic Parts (Hermetic Lots)",
            "family": "Arabic Parts (Family & Relationships)",
            "life": "Arabic Parts (Life Topics)",
            "planetary": "Arabic Parts (Planetary Exaltation)",
        }
        return mode_names.get(self.mode, "Arabic Parts")

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate Arabic Parts table."""
        # Get all Arabic Parts from the chart
        parts = [p for p in chart.positions if p.object_type == ObjectType.ARABIC_PART]

        if not parts:
            return {
                "type": "text",
                "content": (
                    "No Arabic Parts calculated. Add ArabicPartsCalculator:\n\n"
                    "  from stellium.components.arabic_parts import ArabicPartsCalculator\n\n"
                    "  chart = (\n"
                    "      ChartBuilder.from_native(native)\n"
                    "      .add_component(ArabicPartsCalculator())\n"
                    "      .calculate()\n"
                    "  )"
                ),
            }

        # Filter by mode
        parts = self._filter_by_mode(parts)

        if not parts:
            return {
                "type": "text",
                "content": f"No {self.mode} Arabic Parts found in this chart.",
            }

        # Sort parts by category order, then alphabetically within category
        parts = self._sort_parts(parts)

        # Get house systems and their placements
        house_systems = list(chart.house_systems.keys()) if chart.house_systems else []

        # Build table headers
        headers = ["Part", "Position"]

        # Add house columns - one per system with abbreviated labels
        if len(house_systems) == 1:
            # Single system: just "House"
            headers.append("House")
        elif len(house_systems) > 1:
            # Multiple systems: abbreviated labels
            for system in house_systems:
                abbrev = self._abbreviate_house_system(system)
                headers.append(abbrev)
        else:
            # No house systems
            headers.append("House")

        if self.show_formula:
            headers.append("Formula")
        if self.show_description:
            headers.append("Description")

        rows = []
        for part in parts:
            # Part name (clean up for display)
            display_name = self._format_part_name(part.name)

            # Position (degree° Sign minute')
            degree = int(part.sign_degree)
            minute = int((part.sign_degree % 1) * 60)
            sign_glyph = get_sign_glyph(part.sign)
            position = f"{degree}°{sign_glyph}{part.sign} {minute:02d}'"

            row = [display_name, position]

            # House placements - one column per system
            if len(house_systems) == 0:
                row.append("—")
            else:
                for system in house_systems:
                    placements = chart.house_placements.get(system, {})
                    house = placements.get(part.name, "—")
                    house_str = str(house) if house != "—" else "—"
                    row.append(house_str)

            # Formula (optional)
            if self.show_formula:
                formula = self._get_formula(part.name)
                row.append(formula)

            # Description (optional)
            if self.show_description:
                description = self._get_description(part.name)
                row.append(description)

            rows.append(row)

        return {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

    def _filter_by_mode(self, parts: list) -> list:
        """Filter parts based on selected mode."""
        if self.mode == "all":
            return parts

        mode_sets = {
            "core": self.CORE_PARTS,
            "family": self.FAMILY_PARTS,
            "life": self.LIFE_PARTS,
            "planetary": self.PLANETARY_PARTS,
        }

        filter_set = mode_sets.get(self.mode, set())
        return [p for p in parts if p.name in filter_set]

    def _sort_parts(self, parts: list) -> list:
        """Sort parts by category, then alphabetically."""
        # Define category order
        category_order = {
            "core": 0,
            "family": 1,
            "life": 2,
            "planetary": 3,
            "other": 4,
        }

        def get_category(part_name: str) -> str:
            if part_name in self.CORE_PARTS:
                return "core"
            elif part_name in self.FAMILY_PARTS:
                return "family"
            elif part_name in self.LIFE_PARTS:
                return "life"
            elif part_name in self.PLANETARY_PARTS:
                return "planetary"
            return "other"

        def sort_key(part):
            category = get_category(part.name)
            return (category_order[category], part.name)

        return sorted(parts, key=sort_key)

    def _format_part_name(self, name: str) -> str:
        """Format part name for display (shorter version)."""
        # Remove "Part of the " prefix first (longer, more specific)
        if name.startswith("Part of the "):
            return name[12:]  # Remove "Part of the "
        # Then check for "Part of " prefix
        if name.startswith("Part of "):
            return name[8:]  # Remove "Part of "
        return name

    def _get_formula(self, part_name: str) -> str:
        """Get the formula string for a part."""
        if part_name not in self.ARABIC_PARTS_CATALOG:
            return "—"

        config = self.ARABIC_PARTS_CATALOG[part_name]
        points = config["points"]
        sect_flip = config["sect_flip"]

        # Format: ASC + Point2 - Point3 (or note if flips)
        formula = f"{points[0]} + {points[1]} - {points[2]}"
        if sect_flip:
            formula += " *"  # Asterisk indicates sect-aware

        return formula

    def _get_description(self, part_name: str) -> str:
        """Get the description for a part."""
        if part_name not in self.ARABIC_PARTS_CATALOG:
            return "—"

        config = self.ARABIC_PARTS_CATALOG[part_name]
        description = config.get("description", "—")

        # Truncate long descriptions
        if len(description) > 80:
            description = description[:77] + "..."

        return description

    def _abbreviate_house_system(self, system_name: str) -> str:
        """Get abbreviated label for a house system."""
        abbreviations = {
            "Placidus": "Plac",
            "Whole Sign": "WS",
            "Equal": "Eq",
            "Koch": "Koch",
            "Regiomontanus": "Regio",
            "Campanus": "Camp",
            "Porphyry": "Porph",
            "Morinus": "Morin",
            "Alcabitius": "Alcab",
            "Topocentric": "Topo",
        }
        return abbreviations.get(system_name, system_name[:4])
