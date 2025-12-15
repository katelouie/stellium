"""
Dignity-related report sections.

Includes:
- DignitySection: Essential dignities table
- DispositorSection: Dispositor chains and final dispositors
"""

from typing import Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, ObjectType
from stellium.core.multichart import MultiChart

from ._utils import get_object_display, get_object_sort_key


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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate dignity table.

        For MultiChart/Comparison, shows dignities for each chart grouped by label.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's dignities
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            sections = []

            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                sections.append((f"{label} Dignities", single_data))

            return {"type": "compound", "sections": sections}

        # Single chart: standard processing
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate dignity table for a single chart."""
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

    def generate_data(
        self, chart: CalculatedChart | Comparison | MultiChart
    ) -> dict[str, Any]:
        """
        Generate dispositor analysis.

        For MultiChart/Comparison, shows dispositors for each chart grouped by label.
        Returns a compound section with subsections for planetary and/or house
        dispositors, each showing final dispositor and mutual receptions.
        """
        from stellium.core.chart_utils import get_all_charts, get_chart_labels

        # Handle MultiChart/Comparison - show each chart's dispositors
        charts = get_all_charts(chart)
        if len(charts) > 1:
            labels = get_chart_labels(chart)
            all_sections = []

            for c, label in zip(charts, labels, strict=False):
                single_data = self._generate_single_chart_data(c)
                # Unwrap compound sections and prefix with chart label
                if single_data.get("type") == "compound":
                    for title, data in single_data["sections"]:
                        all_sections.append((f"{label} - {title}", data))
                else:
                    all_sections.append((f"{label} Dispositors", single_data))

            return {"type": "compound", "sections": all_sections}

        # Single chart: standard processing
        return self._generate_single_chart_data(chart)

    def _generate_single_chart_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate dispositor analysis for a single chart."""
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
