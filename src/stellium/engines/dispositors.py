"""
Dispositor graph calculation engine.

Dispositors trace the "chain of command" in a chart - each planet is disposed
by the ruler of the sign it occupies. Following these chains reveals:

1. **Planetary Dispositors**: Which planets "dispose" (rule over) which others.
   The final dispositor is the planet that rules its own sign (e.g., Mars in Aries).

2. **House Dispositors** (Kate's innovation): Which life areas flow into which others.
   "What planet rules this house's cusp, and what house is THAT planet in?"
   The final dispositor house is the life area that supports/feeds the others.

Example:
    >>> from stellium import ChartBuilder
    >>> from stellium.engines.dispositors import DispositorEngine
    >>>
    >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
    >>> engine = DispositorEngine(chart)
    >>>
    >>> # Planetary dispositors
    >>> planetary = engine.planetary()
    >>> print(f"Final dispositor: {planetary.final_dispositor}")
    >>> print(f"Mutual receptions: {planetary.mutual_receptions}")
    >>>
    >>> # House dispositors (Kate's innovation)
    >>> houses = engine.house_based()
    >>> print(f"Final dispositor house: {houses.final_dispositor}")
"""

from dataclasses import dataclass
from typing import Literal

import graphviz

from stellium.core.models import CalculatedChart
from stellium.engines.dignities import DIGNITIES

# Traditional planets only (no outer planets - they can't rule signs traditionally)
TRADITIONAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Sign order for reference
SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def get_sign_ruler(
    sign: str, system: Literal["traditional", "modern"] = "traditional"
) -> str:
    """
    Get the planetary ruler of a zodiac sign.

    Args:
        sign: The zodiac sign name (e.g., "Aries", "Leo")
        system: "traditional" (classical rulerships) or "modern" (includes outer planets)

    Returns:
        The name of the ruling planet
    """
    if sign not in DIGNITIES:
        raise ValueError(f"Unknown sign: {sign}")
    return DIGNITIES[sign][system]["ruler"]


# =============================================================================
# Data Models
# =============================================================================


@dataclass(frozen=True)
class DispositorEdge:
    """
    A single edge in the dispositor graph.

    For planetary: "Sun in Leo is disposed by Sun" (self-disposing)
    For house: "House 10 (Capricorn) flows to House 11 (where Saturn is)"
    """

    source: str  # Planet name or house number as string
    target: str  # Planet name or house number as string
    source_sign: str  # The sign of the source
    ruler: str  # The ruling planet

    def __str__(self) -> str:
        return f"{self.source} → {self.target}"


@dataclass(frozen=True)
class MutualReception:
    """
    Two nodes that dispose each other.

    Planetary: Mars in Capricorn ↔ Saturn in Aries (each rules the other's sign)
    House: House 9 ↔ House 11 (their rulers are in each other's houses)
    """

    node1: str
    node2: str
    planet1: str | None = None  # For house-based: the ruling planet of node1
    planet2: str | None = None  # For house-based: the ruling planet of node2

    def __str__(self) -> str:
        return f"{self.node1} ↔ {self.node2}"


@dataclass(frozen=True)
class DispositorResult:
    """
    Complete dispositor analysis result.

    Contains the full graph structure, final dispositor(s), mutual receptions,
    and chains for analysis.

    Attributes:
        mode: "planetary" or "house"
        edges: All edges in the dispositor graph
        final_dispositor: The node(s) where all chains terminate (or None if loops)
        mutual_receptions: List of mutual reception pairs
        chains: Dict mapping each starting node to its full chain
        rulership_system: "traditional" or "modern"
    """

    mode: Literal["planetary", "house"]
    edges: tuple[DispositorEdge, ...]
    final_dispositor: str | tuple[str, ...] | None
    mutual_receptions: tuple[MutualReception, ...]
    chains: dict[str, list[str]]
    rulership_system: str

    def __str__(self) -> str:
        if self.final_dispositor:
            if isinstance(self.final_dispositor, tuple):
                fd = " & ".join(self.final_dispositor)
            else:
                fd = self.final_dispositor
            return f"Final dispositor: {fd}"
        elif self.mutual_receptions:
            mrs = ", ".join(str(mr) for mr in self.mutual_receptions)
            return f"Mutual receptions: {mrs} (no single final dispositor)"
        else:
            return "Complex loop structure (no final dispositor)"

    def get_chain(self, start: str) -> list[str]:
        """Get the full dispositor chain starting from a node."""
        return self.chains.get(start, [])

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON export."""
        return {
            "mode": self.mode,
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "sign": e.source_sign,
                    "ruler": e.ruler,
                }
                for e in self.edges
            ],
            "final_dispositor": self.final_dispositor,
            "mutual_receptions": [
                {"node1": mr.node1, "node2": mr.node2} for mr in self.mutual_receptions
            ],
            "chains": self.chains,
            "rulership_system": self.rulership_system,
        }


# =============================================================================
# Engine
# =============================================================================


class DispositorEngine:
    """
    Calculate dispositor graphs for a chart.

    Supports two modes:
    - Planetary: Traditional planet-rules-planet dispositors
    - House: Kate's innovation - life-area-flows-to-life-area dispositors

    Example:
        >>> chart = ChartBuilder.from_notable("Albert Einstein").calculate()
        >>> engine = DispositorEngine(chart)
        >>>
        >>> # Planetary dispositors
        >>> p = engine.planetary()
        >>> print(p.final_dispositor)
        >>>
        >>> # House dispositors
        >>> h = engine.house_based()
        >>> print(h.final_dispositor)
    """

    def __init__(
        self,
        chart: CalculatedChart,
        rulership_system: Literal["traditional", "modern"] = "traditional",
        house_system: str | None = None,
    ):
        """
        Initialize the dispositor engine.

        Args:
            chart: The calculated chart to analyze
            rulership_system: "traditional" or "modern" rulerships
            house_system: House system to use (defaults to chart's default)
        """
        self.chart = chart
        self.rulership_system = rulership_system
        self.house_system = house_system or chart.default_house_system

    def planetary(self) -> DispositorResult:
        """
        Calculate planetary dispositor graph.

        Each planet is disposed by the ruler of the sign it occupies.
        A planet in its own sign (e.g., Mars in Aries) is self-disposing.

        Returns:
            DispositorResult with planetary dispositor analysis
        """
        edges = []
        graph = {}  # planet -> disposes_to_planet

        # Get traditional planets from the chart
        for planet_name in TRADITIONAL_PLANETS:
            planet = self.chart.get_object(planet_name)
            if planet is None:
                continue

            sign = planet.sign
            ruler = get_sign_ruler(sign, self.rulership_system)

            # Create edge
            edges.append(
                DispositorEdge(
                    source=planet_name,
                    target=ruler,
                    source_sign=sign,
                    ruler=ruler,
                )
            )
            graph[planet_name] = ruler

        # Find mutual receptions
        mutual_receptions = self._find_mutual_receptions(graph)

        # Build chains and find final dispositor
        chains = self._build_chains(graph)
        final_dispositor = self._find_final_dispositor(graph, chains)

        return DispositorResult(
            mode="planetary",
            edges=tuple(edges),
            final_dispositor=final_dispositor,
            mutual_receptions=tuple(mutual_receptions),
            chains=chains,
            rulership_system=self.rulership_system,
        )

    def house_based(self) -> DispositorResult:
        """
        Calculate house-based dispositor graph (Kate's innovation).

        For each house: find the ruler of the sign on its cusp,
        then find what house that ruling planet is in.

        This shows how life areas flow into and support each other.

        Returns:
            DispositorResult with house-based dispositor analysis
        """
        edges = []
        graph = {}  # house_num_str -> target_house_num_str
        house_rulers = {}  # house_num_str -> ruling planet name

        houses = self.chart.get_houses(self.house_system)

        for house_num in range(1, 13):
            house_str = str(house_num)
            sign = houses.get_sign(house_num)
            ruler = get_sign_ruler(sign, self.rulership_system)
            house_rulers[house_str] = ruler

            # Find what house the ruler is in
            ruler_house = self.chart.get_house(ruler, self.house_system)
            if ruler_house is None:
                # Ruler not in chart (outer planet in traditional mode?)
                # Fall back to finding the planet position
                ruler_pos = self.chart.get_object(ruler)
                if ruler_pos:
                    # Calculate house manually from longitude
                    ruler_house = self._longitude_to_house(ruler_pos.longitude, houses)

            if ruler_house is not None:
                target_str = str(ruler_house)
                edges.append(
                    DispositorEdge(
                        source=house_str,
                        target=target_str,
                        source_sign=sign,
                        ruler=ruler,
                    )
                )
                graph[house_str] = target_str

        # Find mutual receptions (with ruler info for house-based)
        mutual_receptions = self._find_house_mutual_receptions(graph, house_rulers)

        # Build chains and find final dispositor
        chains = self._build_chains(graph)
        final_dispositor = self._find_final_dispositor(graph, chains)

        return DispositorResult(
            mode="house",
            edges=tuple(edges),
            final_dispositor=final_dispositor,
            mutual_receptions=tuple(mutual_receptions),
            chains=chains,
            rulership_system=self.rulership_system,
        )

    def _longitude_to_house(self, longitude: float, houses) -> int:
        """
        Determine which house a longitude falls in.

        Args:
            longitude: The ecliptic longitude (0-360)
            houses: HouseCusps object

        Returns:
            House number (1-12)
        """
        cusps = houses.cusps  # List of 12 cusp longitudes

        for i in range(12):
            cusp_start = cusps[i]
            cusp_end = cusps[(i + 1) % 12]

            # Handle wrap-around at 360/0 degrees
            if cusp_start > cusp_end:
                # Cusp crosses 0 degrees
                if longitude >= cusp_start or longitude < cusp_end:
                    return i + 1
            else:
                if cusp_start <= longitude < cusp_end:
                    return i + 1

        return 1  # Fallback (shouldn't happen)

    def _find_mutual_receptions(self, graph: dict[str, str]) -> list[MutualReception]:
        """Find mutual receptions in a planetary graph."""
        mutual = []
        seen = set()

        for node1, target1 in graph.items():
            if target1 in graph:
                target2 = graph[target1]
                if target2 == node1 and node1 != target1:
                    # Mutual reception!
                    pair = tuple(sorted([node1, target1]))
                    if pair not in seen:
                        seen.add(pair)
                        mutual.append(MutualReception(node1=node1, node2=target1))

        return mutual

    def _find_house_mutual_receptions(
        self,
        graph: dict[str, str],
        house_rulers: dict[str, str],
    ) -> list[MutualReception]:
        """Find mutual receptions in a house graph, including ruler info."""
        mutual = []
        seen = set()

        for node1, target1 in graph.items():
            if target1 in graph:
                target2 = graph[target1]
                if target2 == node1 and node1 != target1:
                    # Mutual reception!
                    pair = tuple(sorted([node1, target1]))
                    if pair not in seen:
                        seen.add(pair)
                        mutual.append(
                            MutualReception(
                                node1=node1,
                                node2=target1,
                                planet1=house_rulers.get(node1),
                                planet2=house_rulers.get(target1),
                            )
                        )

        return mutual

    def _build_chains(self, graph: dict[str, str]) -> dict[str, list[str]]:
        """
        Build the full dispositor chain for each starting node.

        Follows edges until reaching a self-loop or a cycle.
        """
        chains = {}

        for start in graph:
            chain = [start]
            current = start
            visited = {start}

            while current in graph:
                next_node = graph[current]
                chain.append(next_node)

                if next_node == current:
                    # Self-disposing (final dispositor)
                    break
                if next_node in visited:
                    # Cycle detected (mutual reception or longer loop)
                    break

                visited.add(next_node)
                current = next_node

            chains[start] = chain

        return chains

    def _find_final_dispositor(
        self,
        graph: dict[str, str],
        chains: dict[str, list[str]],
    ) -> str | tuple[str, ...] | None:
        """
        Find the final dispositor - the node where all chains terminate.

        A final dispositor is a node that disposes itself (planet in own sign,
        or house whose ruler is in that same house).

        If there are mutual receptions acting as the sink, returns both nodes
        in the mutual reception pair.

        Returns:
            - Single string if one self-disposing final dispositor
            - Tuple of strings if mutual reception acts as sink, or multiple self-disposing
            - None if no clear final dispositor (complex loops)
        """
        # Find self-disposing nodes (TRUE final dispositors)
        self_disposing = []
        for node, target in graph.items():
            if target == node:
                self_disposing.append(node)

        if len(self_disposing) == 1:
            return self_disposing[0]
        elif len(self_disposing) > 1:
            return tuple(sorted(self_disposing))

        # No self-disposing node - find mutual reception(s) acting as sink
        # A mutual reception is a sink if chains from other nodes flow into it
        mutual_pairs = []
        for node1, target1 in graph.items():
            if target1 in graph and graph[target1] == node1 and node1 != target1:
                pair = tuple(sorted([node1, target1]))
                if pair not in mutual_pairs:
                    mutual_pairs.append(pair)

        if len(mutual_pairs) == 1:
            # Single mutual reception acts as sink
            return mutual_pairs[0]
        elif len(mutual_pairs) > 1:
            # Multiple mutual receptions - find which one is the main sink
            # by counting how many chains terminate at each pair
            pair_counts = dict.fromkeys(mutual_pairs, 0)
            for chain in chains.values():
                if len(chain) >= 2:
                    terminal = chain[-1]
                    for pair in mutual_pairs:
                        if terminal in pair:
                            pair_counts[pair] += 1
                            break

            max_count = max(pair_counts.values())
            top_pairs = [p for p, c in pair_counts.items() if c == max_count]
            if len(top_pairs) == 1:
                return top_pairs[0]
            # Multiple equal - return all as flat tuple
            all_nodes = set()
            for pair in top_pairs:
                all_nodes.update(pair)
            return tuple(sorted(all_nodes))

        return None


# =============================================================================
# Graphviz Rendering
# =============================================================================


def render_dispositor_graph(
    result: DispositorResult,
    *,
    use_glyphs: bool = True,
    title: str | None = None,
) -> "graphviz.Digraph":
    """
    Render a single dispositor result as a graphviz Digraph.

    Args:
        result: DispositorResult from DispositorEngine
        use_glyphs: Use planet glyphs (☉♀♂) instead of names
        title: Optional title for the graph

    Returns:
        graphviz.Digraph object (call .render() to save)

    Raises:
        ImportError: If graphviz is not installed
    """
    from stellium.core.registry import CELESTIAL_REGISTRY

    # Create digraph with Stellium styling
    dot = graphviz.Digraph(comment=title or f"{result.mode.title()} Dispositors")

    # Stellium palette (matching PDF/chart styling)
    dot.attr(bgcolor="#F5F0E6")  # Cream background
    dot.attr(
        "node",
        shape="circle",
        style="filled",
        fillcolor="#E8E0D4",  # Warm beige nodes
        color="#8B7355",  # Warm brown border
        fontname="Crimson Pro",
        fontsize="14",
        penwidth="1.5",
    )
    dot.attr(
        "edge",
        color="#9B8AA6",  # Purple-ish edges
        penwidth="1.5",
    )

    # Set title
    if title:
        dot.attr(label=title, fontsize="16", fontname="Crimson Pro", labelloc="t")

    # Helper to get node label
    def get_label(node: str) -> str:
        if result.mode == "planetary" and use_glyphs:
            if node in CELESTIAL_REGISTRY:
                return CELESTIAL_REGISTRY[node].glyph
        elif result.mode == "house":
            # For houses, just use the number
            return node
        return node

    # Collect all nodes
    nodes = set()
    for edge in result.edges:
        nodes.add(edge.source)
        nodes.add(edge.target)

    # Find final dispositor(s) for special styling
    final_set = set()
    if result.final_dispositor:
        if isinstance(result.final_dispositor, tuple):
            final_set = set(result.final_dispositor)
        else:
            final_set = {result.final_dispositor}

    # Find mutual reception nodes
    mr_nodes = set()
    for mr in result.mutual_receptions:
        mr_nodes.add(mr.node1)
        mr_nodes.add(mr.node2)

    # Add nodes with special styling for final dispositor
    for node in nodes:
        label = get_label(node)
        if node in final_set:
            # Final dispositor gets gold fill and thicker border
            dot.node(
                node,
                label,
                fillcolor="#D4AF37",  # Gold
                color="#8B6914",  # Darker gold border
                penwidth="2.5",
            )
        elif node in mr_nodes:
            # Mutual reception nodes get a subtle purple tint
            dot.node(
                node,
                label,
                fillcolor="#D8D0E0",  # Light purple
            )
        else:
            dot.node(node, label)

    # Add edges
    seen_edges = set()
    for edge in result.edges:
        _edge_key = (edge.source, edge.target)

        # Check if this is part of a mutual reception
        is_mutual = False
        for mr in result.mutual_receptions:
            if (edge.source == mr.node1 and edge.target == mr.node2) or (
                edge.source == mr.node2 and edge.target == mr.node1
            ):
                is_mutual = True
                break

        if is_mutual:
            # Render mutual receptions with bidirectional arrow (only once)
            pair = tuple(sorted([edge.source, edge.target]))
            if pair not in seen_edges:
                seen_edges.add(pair)
                dot.edge(
                    edge.source,
                    edge.target,
                    dir="both",
                    color="#7B6B8A",  # Darker purple for emphasis
                    penwidth="2.0",
                )
        else:
            # Self-loop (final dispositor)
            if edge.source == edge.target:
                dot.edge(
                    edge.source,
                    edge.target,
                    color="#8B6914",  # Gold edge for self-loop
                    penwidth="2.0",
                )
            else:
                dot.edge(edge.source, edge.target)

    return dot


def render_both_dispositors(
    planetary: DispositorResult,
    house: DispositorResult,
    *,
    use_glyphs: bool = True,
) -> "graphviz.Digraph":
    """
    Render both planetary and house dispositors as subgraphs in a single SVG.

    Args:
        planetary: Planetary DispositorResult
        house: House-based DispositorResult
        use_glyphs: Use planet glyphs for planetary graph

    Returns:
        graphviz.Digraph with both graphs as labeled clusters

    Example:
        >>> engine = DispositorEngine(chart)
        >>> planetary = engine.planetary()
        >>> house = engine.house_based()
        >>> graph = render_both_dispositors(planetary, house)
        >>> graph.render("dispositors", format="svg")
    """
    from stellium.core.registry import CELESTIAL_REGISTRY

    # Create parent digraph
    dot = graphviz.Digraph(comment="Dispositor Graphs")
    dot.attr(bgcolor="#F5F0E6", rankdir="TB")
    dot.attr(
        "node",
        shape="circle",
        style="filled",
        fillcolor="#E8E0D4",
        color="#8B7355",
        fontname="Crimson Pro",
        fontsize="14",
        penwidth="1.5",
    )
    dot.attr(
        "edge",
        color="#9B8AA6",
        penwidth="1.5",
    )

    def get_label(node: str, mode: str) -> str:
        if mode == "planetary" and use_glyphs:
            if node in CELESTIAL_REGISTRY:
                return CELESTIAL_REGISTRY[node].glyph
        return node

    def add_subgraph(result: DispositorResult, cluster_id: str, label: str):
        """Add a dispositor result as a subgraph cluster."""
        with dot.subgraph(name=f"cluster_{cluster_id}") as c:
            c.attr(label=label, fontsize="14", fontname="Crimson Pro")
            c.attr(style="rounded", color="#8B7355", bgcolor="#FAF7F2")

            # Find special nodes
            final_set = set()
            if result.final_dispositor:
                if isinstance(result.final_dispositor, tuple):
                    final_set = set(result.final_dispositor)
                else:
                    final_set = {result.final_dispositor}

            mr_nodes = set()
            for mr in result.mutual_receptions:
                mr_nodes.add(mr.node1)
                mr_nodes.add(mr.node2)

            # Collect nodes
            nodes = set()
            for edge in result.edges:
                nodes.add(edge.source)
                nodes.add(edge.target)

            # Prefix node names to avoid conflicts between subgraphs
            prefix = f"{cluster_id}_"

            # Add nodes
            for node in nodes:
                node_id = prefix + node
                label_text = get_label(node, result.mode)

                if node in final_set:
                    c.node(
                        node_id,
                        label_text,
                        fillcolor="#D4AF37",
                        color="#8B6914",
                        penwidth="2.5",
                    )
                elif node in mr_nodes:
                    c.node(
                        node_id,
                        label_text,
                        fillcolor="#D8D0E0",
                    )
                else:
                    c.node(node_id, label_text)

            # Add edges
            seen_edges = set()
            for edge in result.edges:
                src_id = prefix + edge.source
                tgt_id = prefix + edge.target

                is_mutual = False
                for mr in result.mutual_receptions:
                    if (edge.source == mr.node1 and edge.target == mr.node2) or (
                        edge.source == mr.node2 and edge.target == mr.node1
                    ):
                        is_mutual = True
                        break

                if is_mutual:
                    pair = tuple(sorted([edge.source, edge.target]))
                    if pair not in seen_edges:
                        seen_edges.add(pair)
                        c.edge(
                            src_id,
                            tgt_id,
                            dir="both",
                            color="#7B6B8A",
                            penwidth="2.0",
                        )
                elif edge.source == edge.target:
                    c.edge(
                        src_id,
                        tgt_id,
                        color="#8B6914",
                        penwidth="2.0",
                    )
                else:
                    c.edge(src_id, tgt_id)

    # Add both subgraphs
    add_subgraph(planetary, "planetary", "Planetary Dispositors")
    add_subgraph(house, "house", "House Dispositors")

    return dot
