"""
Aspect-related report sections.

Includes:
- AspectSection: Table of aspects between planets
- AspectPatternSection: Detected aspect patterns (Grand Trines, T-Squares, etc.)
- CrossChartAspectSection: Cross-chart aspects for synastry/comparison
"""

from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart
from stellium.core.multichart import MultiChart
from stellium.core.registry import get_aspects_by_category

from ._utils import (
    get_aspect_display,
    get_aspect_sort_key,
    get_object_display,
    get_object_sort_key,
)


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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate aspect pattern table.

        For MultiChart/Comparison, shows patterns for each chart grouped by label.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's patterns
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []

            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                sections.append((f"{label} Patterns", single_data))

            return {"type": "compound", "sections": sections}

        # Single chart: standard processing
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate aspect pattern table for a single chart."""
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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """Generate aspects table with optional aspectarian SVG.

        For MultiChart/Comparison, shows each chart's internal aspects
        grouped by chart label.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's aspects
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []

            for c, label in zip(charts, labels, strict=False):
                # Generate single chart data for each
                single_data = self._generate_single_chart_data(c)

                # Add the aspectarian with chart label
                if self.include_aspectarian:
                    from stellium.visualization.extended_canvas import (
                        generate_aspectarian_svg,
                    )

                    svg_string = generate_aspectarian_svg(
                        c,
                        output_path=None,
                        cell_size=self.aspectarian_cell_size,
                        detailed=self.aspectarian_detailed,
                        theme=self.aspectarian_theme,
                    )
                    sections.append(
                        (f"{label} Aspectarian", {"type": "svg", "content": svg_string})
                    )

                sections.append((f"{label} Aspects", single_data))

            return {"type": "compound", "sections": sections}

        # Single chart: standard processing with optional aspectarian
        return self._generate_single_chart_with_aspectarian(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate aspects table for a single chart."""
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

        return {"type": "table", "headers": headers, "rows": rows}

    def _generate_single_chart_with_aspectarian(
        self, chart: CalculatedChart
    ) -> dict[str, Any]:
        """Generate aspects table with aspectarian for a single chart.

        This is used when processing a single CalculatedChart directly.
        For multi-charts, the aspectarian is handled at the generate_data level.
        """
        table_data = self._generate_single_chart_data(chart)

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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """Generate cross-chart aspects table."""
        # This section works with Comparison or MultiChart objects
        if isinstance(chart, MultiChart):
            return self._generate_multichart_data(chart)
        elif isinstance(chart, Comparison):
            return self._generate_comparison_data(chart)
        else:
            return {
                "type": "text",
                "content": (
                    "Cross-chart aspects require a Comparison or MultiChart object.\n\n"
                    "Example:\n"
                    "  mc = MultiChartBuilder.synastry(chart1, chart2).calculate()\n"
                    "  report = ReportBuilder().from_chart(mc).with_cross_aspects().render()"
                ),
            }

    def _generate_comparison_data(self, chart: Comparison) -> dict[str, Any]:
        """Generate cross-chart aspects for Comparison."""
        # Get cross-chart aspects (tuple format)
        aspects = list(chart.cross_aspects)
        return self._build_aspect_table(
            aspects,
            chart1_label=chart.chart1_label or "Chart 1",
            chart2_label=chart.chart2_label or "Chart 2",
        )

    def _generate_multichart_data(self, chart: MultiChart) -> dict[str, Any]:
        """Generate cross-chart aspects for MultiChart.

        MultiChart stores aspects in a dict: {(0,1): aspects, (0,2): aspects, ...}
        By default, shows aspects to primary (chart 0).
        """
        # Collect all aspects to primary (chart 0)
        all_aspects = []
        for (i, j), aspects in chart.cross_aspects.items():
            # Only include aspects involving chart 0 (to_primary default)
            if i == 0 or j == 0:
                all_aspects.extend(aspects)

        if not all_aspects:
            # Fall back to showing all aspects if none to primary
            all_aspects = chart.get_all_cross_aspects()

        # Use labels from MultiChart
        chart1_label = chart.labels[0] if chart.labels else "Chart 1"
        chart2_label = (
            "Other Charts"
            if chart.chart_count > 2
            else (chart.labels[1] if len(chart.labels) > 1 else "Chart 2")
        )

        return self._build_aspect_table(
            all_aspects,
            chart1_label=chart1_label,
            chart2_label=chart2_label,
        )

    def _build_aspect_table(
        self,
        aspects: list,
        chart1_label: str,
        chart2_label: str,
    ) -> dict[str, Any]:
        """Build the aspect table from a list of aspects."""
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
