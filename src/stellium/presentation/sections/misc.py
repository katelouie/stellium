"""
Miscellaneous report sections.

Includes:
- CacheInfoSection: Cache statistics
- MoonPhaseSection: Moon phase information
- DeclinationSection: Planetary declinations
- DeclinationAspectSection: Parallel and contraparallel aspects
- FixedStarsSection: Fixed star positions
- ArabicPartsSection: Arabic Parts (Lots)
"""

from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, ObjectType
from stellium.core.multichart import MultiChart

from ._utils import (
    get_aspect_display,
    get_object_display,
    get_object_sort_key,
    get_sign_glyph,
)


def _wrap_for_multichart(generate_single_func, section_label: str):
    """Helper to wrap single-chart generator for multi-chart support."""

    def wrapper(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []
            for c, label in zip(charts, labels, strict=False):
                single_data = generate_single_func(self, c)
                sections.append((f"{label} {section_label}", single_data))
            return {"type": "compound", "sections": sections}
        return generate_single_func(self, chart)

    return wrapper


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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate declination table data.

        For MultiChart/Comparison, shows declinations for each chart grouped by label.
        Shows declination values for all planets with equatorial coordinates.
        Highlights out-of-bounds planets (beyond Sun's max declination).
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []
            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                sections.append((f"{label} Declinations", single_data))
            return {"type": "compound", "sections": sections}

        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate declination table for a single chart."""
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
        # Import here to avoid circular imports
        from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG

        if part_name not in ARABIC_PARTS_CATALOG:
            return "—"

        config = ARABIC_PARTS_CATALOG[part_name]
        points = config["points"]
        sect_flip = config["sect_flip"]

        # Format: ASC + Point2 - Point3 (or note if flips)
        formula = f"{points[0]} + {points[1]} - {points[2]}"
        if sect_flip:
            formula += " *"  # Asterisk indicates sect-aware

        return formula

    def _get_description(self, part_name: str) -> str:
        """Get the description for a part."""
        # Import here to avoid circular imports
        from stellium.components.arabic_parts import ARABIC_PARTS_CATALOG

        if part_name not in ARABIC_PARTS_CATALOG:
            return "—"

        config = ARABIC_PARTS_CATALOG[part_name]
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


class AntisciaSection:
    """
    Table of Antiscia and Contra-Antiscia conjunctions.

    Antiscia are "hidden conjunctions" - when one planet's reflection point
    (across the solstice axis) is conjunct another planet. Contra-antiscia
    are reflections across the equinox axis.

    Shows:
    - The two planets involved
    - Whether it's antiscia or contra-antiscia
    - The orb of the conjunction
    - Whether the aspect is applying or separating
    """

    def __init__(
        self,
        include_contra: bool = True,
        show_points: bool = False,
    ) -> None:
        """
        Initialize Antiscia section.

        Args:
            include_contra: Include contra-antiscia conjunctions (default True)
            show_points: Also show the antiscia point positions (default False)
        """
        self.include_contra = include_contra
        self.show_points = show_points

    @property
    def section_name(self) -> str:
        if self.include_contra:
            return "Antiscia & Contra-Antiscia"
        return "Antiscia"

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """Generate antiscia table."""
        from stellium.core.chart_utils import get_all_charts

        # For multi-charts, only use the first chart
        charts = get_all_charts(chart)
        target_chart = charts[0]

        # Get antiscia data from metadata
        antiscia_data = target_chart.metadata.get("antiscia", {})

        if not antiscia_data:
            return {
                "type": "text",
                "text": (
                    "No antiscia calculated. Add AntisciaCalculator to include them:\n\n"
                    "    from stellium.components import AntisciaCalculator\n\n"
                    "    chart = (\n"
                    "        ChartBuilder.from_native(native)\n"
                    "        .add_component(AntisciaCalculator())\n"
                    "        .calculate()\n"
                    "    )"
                ),
            }

        conjunctions = antiscia_data.get("conjunctions", [])
        contra_conjunctions = antiscia_data.get("contra_conjunctions", [])
        orb = antiscia_data.get("orb", 1.5)

        # Combine or separate based on settings
        all_conjs = []
        for conj in conjunctions:
            all_conjs.append(("Antiscia", conj))
        if self.include_contra:
            for conj in contra_conjunctions:
                all_conjs.append(("Contra-Antiscia", conj))

        if not all_conjs:
            return {
                "type": "text",
                "text": f"No antiscia conjunctions found within {orb}° orb.",
            }

        # Build table
        headers = ["Planet 1", "Planet 2", "Type", "Orb", "State"]
        rows = []

        for conj_type, conj in all_conjs:
            # Get planet display (returns tuple of name, glyph)
            name1, glyph1 = get_object_display(conj.planet1)
            name2, glyph2 = get_object_display(conj.planet2)
            planet1 = f"{glyph1} {name1}" if glyph1 else name1
            planet2 = f"{glyph2} {name2}" if glyph2 else name2

            # Orb formatting
            orb_str = f"{conj.orb:.1f}°"

            # Applying/separating
            state = "Applying" if conj.is_applying else "Separating"

            rows.append([planet1, planet2, conj_type, orb_str, state])

        result: dict[str, Any] = {
            "type": "table",
            "headers": headers,
            "rows": rows,
        }

        # Optionally add antiscia point positions
        if self.show_points:
            antiscia_pts = [
                p
                for p in target_chart.positions
                if p.object_type == ObjectType.ANTISCION
            ]
            contra_pts = [
                p
                for p in target_chart.positions
                if p.object_type == ObjectType.CONTRA_ANTISCION
            ]

            point_rows = []
            for pt in antiscia_pts:
                degree = int(pt.sign_degree)
                minute = int((pt.sign_degree % 1) * 60)
                sign_glyph = get_sign_glyph(pt.sign)
                position = f"{degree}°{sign_glyph}{pt.sign} {minute:02d}'"
                point_rows.append([pt.name, position, "Antiscion"])

            if self.include_contra:
                for pt in contra_pts:
                    degree = int(pt.sign_degree)
                    minute = int((pt.sign_degree % 1) * 60)
                    sign_glyph = get_sign_glyph(pt.sign)
                    position = f"{degree}°{sign_glyph}{pt.sign} {minute:02d}'"
                    point_rows.append([pt.name, position, "Contra-Antiscion"])

            if point_rows:
                result = {
                    "type": "compound",
                    "sections": [
                        ("Antiscia Conjunctions", result),
                        (
                            "Antiscia Points",
                            {
                                "type": "table",
                                "headers": ["Point", "Position", "Type"],
                                "rows": point_rows,
                            },
                        ),
                    ],
                }

        return result
