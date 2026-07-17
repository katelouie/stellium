"""
Core report sections for basic chart information.

Includes:

- ChartOverviewSection: Basic chart metadata (date, time, location)
- PlanetPositionSection: Positions of celestial objects
- HouseCuspsSection: House cusp positions for multiple systems
"""

import datetime as dt
from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, ObjectType
from stellium.core.multichart import MultiChart
from stellium.i18n import msg, term
from stellium.utils.chart_ruler import get_chart_ruler_from_chart

from ._utils import (
    get_object_display,
    get_object_sort_key,
    get_sign_glyph,
)


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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate chart overview data.

        For Comparison/MultiChart objects, shows all charts' information.

        Why key-value format?

        - Simple label: value pairs
        - Easy to render as a list or small table
        - Human-readable structure
        """
        # Handle MultiChart objects
        if isinstance(chart, MultiChart):
            return self._generate_multichart_data(chart)

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

        # Date and time. The raw date/time objects are handed over; the renderer lays
        # them out per the active locale (a date is a reorder, not a word — the whole
        # reason post-hoc translation could not do this). See i18n.render / format_date.
        birth: dt.datetime = chart.datetime.local_datetime
        date_label = f"{label} Date" if label else "Date"
        time_label = f"{label} Time" if label else "Time"
        data[date_label] = birth.date()
        data[time_label] = birth.time()

        if not label:  # Only show timezone for single charts
            data["Timezone"] = str(chart.location.timezone)

        # Location — a geocoded place name, do-not-translate.
        loc = chart.location
        loc_label = f"{label} Location" if label else "Location"
        data[loc_label] = f"{loc.name}" if loc.name else "Unknown"

        if not label:  # Only show detailed info for single charts
            data["Coordinates"] = f"{loc.latitude:.4f}°, {loc.longitude:.4f}°"

            # House systems: a comma-list of catalog terms (render joins them).
            data["House System"] = [
                term(f"house_system.{name}") for name in chart.house_systems
            ]

            # Zodiac system
            if chart.zodiac_type:
                zodiac_word = chart.zodiac_type.value.title()  # Tropical / Sidereal
                if chart.zodiac_type.value == "sidereal" and chart.ayanamsa:
                    ayanamsa_display = chart.ayanamsa.replace("_", " ").title()
                    data["Zodiac"] = msg(
                        "{zodiac} ({ayanamsa})",
                        zodiac=msg(zodiac_word),
                        ayanamsa=ayanamsa_display,
                    )
                else:
                    data["Zodiac"] = msg(zodiac_word)

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
                data["Chart Sect"] = msg(
                    "{sect} Chart", sect=term(f"sect.{sect.title()}")
                )

            # Chart Ruler
            try:
                ruler, asc_sign = get_chart_ruler_from_chart(chart)
                data["Chart Ruler"] = msg(
                    "{ruler} ({sign} Rising)",
                    ruler=term(f"body.{ruler}"),
                    sign=term(f"sign.{asc_sign}"),
                )
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

    def _generate_multichart_data(self, multichart: MultiChart) -> dict[str, Any]:
        """Generate overview data for a MultiChart object."""
        data = {}

        # Chart count and type
        chart_count = multichart.chart_count
        chart_types = {2: "Biwheel", 3: "Triwheel", 4: "Quadwheel"}
        data["Chart Type"] = chart_types.get(chart_count, f"{chart_count}-Wheel")

        # Relationship types (if any)
        if multichart.relationships:
            rel_types = {r.value.title() for r in multichart.relationships.values()}
            data["Relationship"] = ", ".join(rel_types)

        # Info for each chart
        for i, chart in enumerate(multichart.charts):
            label = (
                multichart.labels[i] if i < len(multichart.labels) else f"Chart {i + 1}"
            )

            if "name" in chart.metadata:
                data[label] = chart.metadata["name"]
            else:
                data[label] = "(unnamed)"

            birth: dt.datetime = chart.datetime.local_datetime
            data[f"{label} Date"] = birth.strftime("%B %d, %Y")
            data[f"{label} Time"] = birth.strftime("%I:%M %p")
            data[f"{label} Location"] = (
                chart.location.name if chart.location.name else "Unknown"
            )

        # Cross-chart aspect count
        total_aspects = sum(
            len(aspects) for aspects in multichart.cross_aspects.values()
        )
        if total_aspects > 0:
            data["Cross-Chart Aspects"] = total_aspects

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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate planet positions table.

        For Comparison/MultiChart objects, generates side-by-side tables for each chart.
        """
        # Handle MultiChart objects with side-by-side tables
        if isinstance(chart, MultiChart):
            return self._generate_multichart_data(chart)

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

        # Build headers based on options. The "House (Pl)" header is *composed* — the one
        # thing the old substring translator could never localize (it matched whole cells,
        # not fragments), so it becomes a message with the system as a short-form term.
        headers: list[Any] = ["Planet", "Position"]
        # The structured (PDF) planet table shows a narrow per-system column; its header is
        # the short-form house term, which localizes (Placidus -> "Pl" / "普") instead of
        # the raw English abbreviation the Typst renderer used to print verbatim.
        house_headers: list[Any] = []

        if self.include_house and systems_to_show:
            for system_name in systems_to_show:
                short_term = term(f"house_system.{system_name}", short=True)
                headers.append(msg("House ({system})", system=short_term))
                house_headers.append(short_term)

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

        # Build the planet payload ONCE — the single source of truth. Canonical identity
        # fields (name, sign, the glyph chars) stay raw for the structured renderer's
        # colour/glyph lookups; display fields are i18n tokens the resolve pass localizes.
        # The flat ``rows`` are then DERIVED from it, reusing the same tokens, so no data
        # is composed twice. See the Unified Renderer Contract spec §4.3.
        planets: list[dict[str, Any]] = []
        for pos in positions:
            _display_name, glyph = get_object_display(pos.name)
            degree = int(pos.sign_degree)
            minute = int((pos.sign_degree % 1) * 60)
            deg_str = f"{degree}°{minute:02d}'"
            sign_glyph = get_sign_glyph(pos.sign)

            houses: list[str] = []
            if self.include_house and systems_to_show:
                for system_name in systems_to_show:
                    try:
                        house_placements = chart.house_placements[system_name]
                        house = house_placements.get(pos.name, "—")
                        houses.append(str(house) if house else "—")
                    except KeyError:
                        houses.append("—")

            motion = "Retrograde" if pos.is_retrograde else "Direct"
            planets.append(
                {
                    "name": pos.name,  # canonical — colour/glyph/matching
                    "label": term(
                        f"body.{pos.name}"
                    ),  # display (localized by the pass)
                    "glyph": glyph or "",  # language-neutral
                    "sign": pos.sign,  # canonical — disc tint, glyph fallback
                    "sign_label": term(f"sign.{pos.sign}"),  # display
                    "sign_glyph": sign_glyph or "",  # language-neutral
                    "degree": deg_str,
                    "houses": houses,
                    "speed": f"{pos.speed_longitude:.3f}°",  # structured-view speed
                    "speed_value": pos.speed_longitude,  # raw, for the text view
                    "retro": bool(pos.is_retrograde),
                    "motion": term(f"motion.{motion}", short=True),  # display (abbrev)
                }
            )

        # Derive the flat rows from the payload — reuse the same tokens, compose last.
        rows = []
        for p in planets:
            name_cell: Any = (
                msg("{glyph} {name}", glyph=p["glyph"], name=p["label"])
                if p["glyph"]
                else p["label"]
            )
            position_cell: Any = (
                msg(
                    "{glyph} {sign} {deg}",
                    glyph=p["sign_glyph"],
                    sign=p["sign_label"],
                    deg=p["degree"],
                )
                if p["sign_glyph"]
                else msg("{sign} {deg}", sign=p["sign_label"], deg=p["degree"])
            )
            row: list[Any] = [name_cell, position_cell, *p["houses"]]
            if self.include_speed:
                # "°/day" is a unit; a message so a locale can render "day" (天).
                row.append(msg("{v}°/day", v=f"{p['speed_value']:.4f}"))
                # Text view uses the full motion word, not the column abbreviation.
                row.append(term(f"motion.{'Retrograde' if p['retro'] else 'Direct'}"))
            rows.append(row)

        result = {
            "type": "table",
            "headers": headers,
            "rows": rows,
            # Structured payload for structure-aware renderers:
            "planets": planets,
            "house_headers": house_headers,
            "show_speed": self.include_speed,
            # Chrome for the structured (Typst) planet table: the template reads these
            # localized labels instead of hardcoding English column headers.
            "labels": {
                "planet": msg("Planet"),
                "position": msg("Position"),
                "speed": msg("Speed"),
                "motion": msg("Motion"),
            },
        }
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

    def _generate_multichart_data(self, multichart: MultiChart) -> dict[str, Any]:
        """Generate side-by-side position tables for a MultiChart."""
        from stellium.core.chart_utils import get_chart_labels

        labels = get_chart_labels(multichart)
        tables = []

        for i, (chart, label) in enumerate(
            zip(multichart.charts, labels, strict=False)
        ):
            chart_data = self._generate_single_chart_data(chart, title=label)
            tables.append(
                {
                    "title": chart_data.get("title", f"Chart {i + 1}"),
                    "headers": chart_data["headers"],
                    "rows": chart_data["rows"],
                }
            )

        return {
            "type": "side_by_side_tables",
            "tables": tables,
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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate house cusps table.

        For Comparison/MultiChart objects, generates side-by-side tables for each chart.
        """
        # Handle MultiChart objects with side-by-side tables
        if isinstance(chart, MultiChart):
            return self._generate_multichart_data(chart)

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

        # Build headers. "Cusp (Pl)" is composed, like the planet-table house header —
        # a message with the system as a short-form term.
        headers: list[Any] = ["House"]
        for system_name in systems_to_show:
            headers.append(
                msg(
                    "Cusp ({system})",
                    system=term(f"house_system.{system_name}", short=True),
                )
            )

        # Build rows (houses 1-12)
        rows = []
        for house_num in range(1, 13):
            row: list[Any] = [str(house_num)]

            for system_name in systems_to_show:
                house_cusps = chart.house_systems[system_name]
                cusp_longitude = house_cusps.cusps[house_num - 1]

                # Convert to sign and degree
                sign, sign_degree = longitude_to_sign_and_degree(cusp_longitude)
                degree = int(sign_degree)
                minute = int((sign_degree % 1) * 60)

                # Glyph form is language-neutral (number + glyph). The name fallback is a
                # term, so a sign with no glyph still localizes rather than leaking.
                sign_glyph = get_sign_glyph(sign)
                if sign_glyph:
                    row.append(f"{degree}° {sign_glyph} {minute:02d}'")
                else:
                    row.append(
                        msg(
                            "{deg}° {sign} {min}'",
                            deg=degree,
                            sign=term(f"sign.{sign}"),
                            min=f"{minute:02d}",
                        )
                    )

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

    def _generate_multichart_data(self, multichart: MultiChart) -> dict[str, Any]:
        """Generate side-by-side house cusps tables for a MultiChart."""
        from stellium.core.chart_utils import get_chart_labels

        labels = get_chart_labels(multichart)
        tables = []

        for i, (chart, label) in enumerate(
            zip(multichart.charts, labels, strict=False)
        ):
            chart_data = self._generate_single_chart_data(chart, title=label)
            tables.append(
                {
                    "title": chart_data.get("title", f"Chart {i + 1}"),
                    "headers": chart_data["headers"],
                    "rows": chart_data["rows"],
                }
            )

        return {
            "type": "side_by_side_tables",
            "tables": tables,
        }
