"""
Dignity-related report sections.

Includes:

- DignitySection: Essential dignities table
- DispositorSection: Dispositor chains and final dispositors
"""

from typing import TYPE_CHECKING, Any

from stellium.core.comparison import Comparison
from stellium.core.models import CalculatedChart, ObjectType
from stellium.core.multichart import MultiChart
from stellium.i18n import get_default_locale, msg, render, term

if TYPE_CHECKING:
    from stellium.engines.dispositors import DispositorResult


from ._utils import get_object_display, get_object_sort_key, glyph_label


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
                "text": (
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
                "text": "No dignity data available.",
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

            row: list[Any] = []

            # Planet name with glyph (a catalog term)
            _, glyph = get_object_display(pos.name)
            row.append(glyph_label(glyph, f"body.{pos.name}"))

            dignity_info = planet_dignities[pos.name]

            # Traditional column
            if self.essential in ("traditional", "both"):
                if "traditional" in dignity_info:
                    trad = dignity_info["traditional"]
                    if self.show_details:
                        # Dignity names are catalog terms. The engine emits them
                        # lowercased ("exaltation"); the catalog and the astrology
                        # convention are capitalized, so title-case for the key — this
                        # also capitalizes the English display, which is correct.
                        dignity_names = trad.get("dignities", [])
                        if dignity_names:
                            row.append(
                                [term(f"dignity.{d.title()}") for d in dignity_names]
                            )
                        else:
                            row.append(
                                term("dignity.Peregrine")
                                if trad.get("is_peregrine")
                                else "—"
                            )
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
                        # Catalog terms, title-cased (see the traditional column).
                        dignity_names = mod.get("dignities", [])
                        if dignity_names:
                            row.append(
                                [term(f"dignity.{d.title()}") for d in dignity_names]
                            )
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
        planetary = None
        if self.mode in ("planetary", "both"):
            planetary = engine.planetary()
            sections.append(self._format_result(planetary, "Planetary"))

        # House dispositors
        house = None
        if self.mode in ("house", "both"):
            house = engine.house_based()
            sections.append(self._format_result(house, "House-Based"))

        # Try to generate SVG graph (for HTML/PDF rendering)
        svg_section = self._render_graph_svg(planetary, house)
        if svg_section:
            sections.insert(0, svg_section)

        # If only one mode and no SVG, return text directly
        if len(sections) == 1:
            title, data = sections[0]
            return {
                "type": "text",
                "text": data.get("text", ""),
            }

        # Otherwise return compound section (list of tuples)
        return {
            "type": "compound",
            "sections": sections,
        }

    def _render_graph_svg(
        self,
        planetary: "DispositorResult | None",
        house: "DispositorResult | None",
    ) -> tuple[str, dict[str, Any]] | None:
        """Build the dispositor graph section.

        Emits a structured, laid-out ``graph`` payload (nodes + edges + ranks)
        that the Typst PDF draws natively, plus an svgwrite-rendered SVG (same
        layout) for the other renderers (HTML embeds it). No graphviz dependency.
        """
        from stellium.engines.dispositors import (
            dispositor_graph_data,
            render_dispositor_svg,
        )

        # The graph is a baked diagram — its title is drawn into the SVG and read by the
        # native PDF renderer, so localize it in the ambient locale before it is drawn.
        # (The in-diagram node labels remain English pending a graph-engine i18n pass.)
        loc = get_default_locale()

        graphs = []
        if planetary:
            graphs.append(
                {
                    "title": render(msg("Planetary Dispositors"), loc),
                    **dispositor_graph_data(planetary),
                }
            )
        if house:
            graphs.append(
                {
                    "title": render(msg("House Dispositors"), loc),
                    **dispositor_graph_data(house),
                }
            )
        if not graphs:
            return None

        sub: dict[str, Any] = {"type": "svg", "graph": {"graphs": graphs}}
        try:
            sub["content"] = render_dispositor_svg(graphs)
        except Exception:
            pass

        return (msg("Dispositor Graph"), sub)

    def _format_result(self, result, title: str) -> dict[str, Any]:
        """Format a DispositorResult for display.

        This section emits a ``text`` block, which the resolve pass leaves alone (free-form
        prose localizes as a whole, not term-by-term). So it bakes its own localized text in
        the report's ambient locale — the sanctioned path for generate-time sections — via
        ``render(msg/term)``, which also brackets under the pseudolocale so the completeness
        oracle still sees it.
        """
        from stellium.core.registry import CELESTIAL_REGISTRY

        loc = get_default_locale()

        def L(token: Any) -> str:
            return render(token, loc)

        def planet(name: str) -> str:
            label = L(term(f"body.{name}"))
            if name in CELESTIAL_REGISTRY:
                return f"{CELESTIAL_REGISTRY[name].glyph} {label}"
            return label

        def house(num: Any) -> str:
            return L(msg("House {n}", n=num))

        lines = []

        # Final dispositor
        if result.final_dispositor:
            if isinstance(result.final_dispositor, tuple):
                if result.mode == "planetary":
                    fd_str = " ↔ ".join(planet(p) for p in result.final_dispositor)
                else:
                    fd_str = " ↔ ".join(house(h) for h in result.final_dispositor)
                lines.append(
                    L(msg("Final Dispositor: {fd} (mutual reception)", fd=fd_str))
                )
            else:
                if result.mode == "planetary":
                    fd_str = planet(result.final_dispositor)
                else:
                    fd_str = house(result.final_dispositor)
                lines.append(L(msg("Final Dispositor: {fd}", fd=fd_str)))
        else:
            lines.append(L(msg("Final Dispositor: None (complex loop structure)")))

        # Mutual receptions
        if result.mutual_receptions:
            lines.append("")
            lines.append(L(msg("Mutual Receptions:")))
            for mr in result.mutual_receptions:
                if result.mode == "planetary":
                    lines.append(f"  {planet(mr.node1)} ↔ {planet(mr.node2)}")
                else:
                    lines.append(
                        f"  {house(mr.node1)} ({planet(mr.planet1)}) ↔ "
                        f"{house(mr.node2)} ({planet(mr.planet2)})"
                    )

        # Chains (optional)
        if self.show_chains and result.chains:
            lines.append("")
            lines.append(L(msg("Disposition Chains:")))
            for _start, chain in sorted(result.chains.items()):
                if result.mode == "planetary":
                    # Glyphs only — language-neutral.
                    chain_str = " → ".join(
                        CELESTIAL_REGISTRY[node].glyph
                        if node in CELESTIAL_REGISTRY
                        else node
                        for node in chain
                    )
                else:
                    chain_str = " → ".join(str(node) for node in chain)
                lines.append(f"  {chain_str}")

        # Return as tuple of (title, data) for compound rendering. The title is a message
        # the resolve pass localizes; the text block is baked above.
        return (
            msg(f"{title} Dispositors"),
            {
                "type": "text",
                "text": "\n".join(lines),
            },
        )
