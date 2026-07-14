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
            house_system: House system to use for house_based() (defaults to the
                chart's default). Resolved lazily -- see the house_system
                property -- so the engine can be constructed (and planetary()
                run) on a chart that has no house systems.
        """
        self.chart = chart
        self.rulership_system = rulership_system
        # Store the raw argument and resolve lazily. planetary() uses only sign
        # rulerships (no houses), so requiring a house system here would wrongly
        # couple it to houses -- and break the engine entirely for a house-less
        # chart such as an unknown-time chart.
        self._house_system = house_system

    @property
    def house_system(self) -> str:
        """House system used by house_based() dispositors, resolved lazily.

        Falls back to the chart's default system. Only house_based() reads this,
        so planetary() works even when the chart has no house systems. Accessing
        it on a house-less chart raises ValueError (via default_house_system).
        """
        return self._house_system or self.chart.default_house_system

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

        Raises:
            ValueError: If the chart has no house systems (e.g. an unknown-time
                chart). Use planetary() for that case.
        """
        if not self.chart.house_systems:
            raise ValueError(
                "House-based dispositors require a chart with house systems, but "
                "this chart has none (e.g. an unknown-time chart). Use "
                "planetary() for sign-rulership dispositors instead."
            )

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


def dispositor_graph_data(result: "DispositorResult") -> dict:
    """Structured, laid-out dispositor graph for native (non-graphviz) drawing.

    The graph is a functional DAG (each node points to its single ruler, chains
    converging on the final dispositor / mutual-reception cycle), so a clean
    layered layout is just a BFS: rank = number of steps from the sink. Returns
    nodes (with display name, glyph, rank, column) + edges + max_rank, ready for
    a renderer to place circles by (col, rank) and draw arrows between them.

    Portable and themeable: no graphviz, no fonts baked into an SVG.
    """
    from collections import deque

    from stellium.core.registry import CELESTIAL_REGISTRY

    node_ids: list[str] = []
    fwd: dict[str, str] = {}
    rev: dict[str, list[str]] = {}
    for e in result.edges:
        for n in (e.source, e.target):
            if n not in node_ids:
                node_ids.append(n)
        fwd[e.source] = e.target
        rev.setdefault(e.target, []).append(e.source)
    if not node_ids:
        return {"nodes": [], "edges": [], "max_rank": 0}

    # Sink = final dispositor / mutual-reception nodes (everything flows here).
    sink: set[str] = set()
    fd = result.final_dispositor
    if fd:
        sink.update(fd if isinstance(fd, tuple) else (fd,))
    for mr in result.mutual_receptions:
        sink.add(mr.node1)
        sink.add(mr.node2)
    sink &= set(node_ids)
    if not sink:
        sink = {n for n in node_ids if fwd.get(n) in (None, n)} or {node_ids[0]}

    # rank = distance from the sink, following dependents (reverse edges) outward.
    rank: dict[str, int] = dict.fromkeys(sink, 0)
    q = deque(sink)
    while q:
        n = q.popleft()
        for dep in rev.get(n, []):
            if dep not in rank:
                rank[dep] = rank[n] + 1
                q.append(dep)
    # Disconnected nodes: follow their forward chain to something ranked.
    for n in node_ids:
        if n not in rank:
            chain: list[str] = []
            cur: str | None = n
            guard = 0
            while (
                cur is not None and cur not in rank and cur not in chain and guard < 100
            ):
                chain.append(cur)
                cur = fwd.get(cur)
                guard += 1
            base = rank.get(cur, 0)
            for i, m in enumerate(reversed(chain)):
                rank[m] = base + i + 1

    max_rank = max(rank.values())
    by_rank: dict[int, list[str]] = {}
    for n in node_ids:
        by_rank.setdefault(rank[n], []).append(n)

    mutual_nodes: set[str] = set()
    for mr in result.mutual_receptions:
        mutual_nodes.add(mr.node1)
        mutual_nodes.add(mr.node2)

    is_house = result.mode == "house"
    nodes = []
    for n in node_ids:
        r = rank[n]
        row = by_rank[r]
        if is_house or n not in CELESTIAL_REGISTRY:
            label, glyph = str(n), ""
        else:
            reg = CELESTIAL_REGISTRY[n]
            label, glyph = reg.display_name, (reg.glyph or "")
        nodes.append(
            {
                "id": n,
                "label": label,
                "glyph": glyph,
                "rank": r,
                "col": row.index(n),
                "ncols": len(row),
                "final": n in sink,
                "mutual": n in mutual_nodes,
            }
        )

    mr_pairs = {tuple(sorted((m.node1, m.node2))) for m in result.mutual_receptions}
    seen_mr: set = set()
    edges = []
    for e in result.edges:
        key = tuple(sorted((e.source, e.target)))
        mutual = key in mr_pairs
        if mutual:
            if key in seen_mr:
                continue
            seen_mr.add(key)
        edges.append({"from": e.source, "to": e.target, "mutual": mutual})

    return {"nodes": nodes, "edges": edges, "max_rank": max_rank}


def render_dispositor_svg(
    graphs: list[dict],
    filename: str | None = None,
) -> str:
    """Render one or more laid-out dispositor graphs to an SVG string (svgwrite).

    Replaces the old graphviz renderer: uses the same layered layout as the
    native PDF graph (dispositor_graph_data), so there is no graphviz dependency.

    Args:
        graphs: list of dicts, each ``{"title", "nodes", "edges", "max_rank"}``
            (dispositor_graph_data output plus a title). Rendered side by side,
            each in its own rounded panel.
        filename: optional path to also save the SVG.

    Returns:
        The SVG document as a string.
    """
    import math

    import svgwrite

    R = 20
    gap = 66
    colw = 74
    pad = 22
    title_h = 34
    c_panel, c_border = "#FAF6EE", "#D8CBB6"
    c_node, c_node_edge = "#EFE9DC", "#8B7355"
    c_final, c_final_edge = "#D4AF37", "#8B6914"
    c_glyph, c_title = "#3A2233", "#8B7355"
    c_edge, c_edge_mr = "#9B8AA6", "#8B6914"

    layouts = []
    for g in graphs:
        maxr = g["max_rank"]
        max_ncols = max((n["ncols"] for n in g["nodes"]), default=1)
        gw = max(max_ncols * colw, colw)
        gh = title_h + pad + maxr * gap + 2 * R + pad
        layouts.append((g, gw, gh, maxr))
    total_w = sum(gw for _, gw, _, _ in layouts) + pad * (len(layouts) + 1)
    total_h = max((gh for _, _, gh, _ in layouts), default=120) + pad

    dwg = svgwrite.Drawing(
        filename=filename or "dispositor.svg",
        size=(f"{total_w}px", f"{total_h}px"),
        viewBox=f"0 0 {total_w} {total_h}",
        debug=False,
    )
    # forward arrowhead (line end) + reversed one (line start, for mutual pairs).
    m_end = dwg.marker(insert=(7, 3), size=(8, 6), orient="auto", id="disp-arrow")
    m_end.viewbox(0, 0, 8, 6)
    m_end.add(dwg.path(d="M0,0 L8,3 L0,6 Z", fill=c_edge_mr))
    dwg.defs.add(m_end)
    m_start = dwg.marker(insert=(1, 3), size=(8, 6), orient="auto", id="disp-arrow-rev")
    m_start.viewbox(0, 0, 8, 6)
    m_start.add(dwg.path(d="M8,0 L0,3 L8,6 Z", fill=c_edge_mr))
    dwg.defs.add(m_start)

    x_off = pad
    for g, gw, gh, maxr in layouts:
        dwg.add(
            dwg.rect(
                insert=(x_off, pad / 2),
                size=(gw, gh - pad / 2),
                rx=10,
                fill=c_panel,
                stroke=c_border,
                stroke_width=1,
            )
        )
        dwg.add(
            dwg.text(
                g["title"].upper(),
                insert=(x_off + gw / 2, title_h - 6),
                text_anchor="middle",
                font_size="11px",
                font_family="Georgia, serif",
                fill=c_title,
                letter_spacing="1.5",
            )
        )
        nmap = {n["id"]: n for n in g["nodes"]}

        def _pos(n, _x_off=x_off, _gw=gw, _maxr=maxr):
            x = _x_off + _gw * (n["col"] + 0.5) / max(n["ncols"], 1)
            y = title_h + pad + R + (_maxr - n["rank"]) * gap
            return x, y

        for e in g["edges"]:
            a, b = nmap[e["from"]], nmap[e["to"]]
            ax, ay = _pos(a)
            bx, by = _pos(b)
            dx, dy = bx - ax, by - ay
            length = max(math.hypot(dx, dy), 0.001)
            ux, uy = dx / length, dy / length
            sx, sy = ax + ux * R, ay + uy * R
            ex, ey = bx - ux * (R + 2), by - uy * (R + 2)
            col = c_edge_mr if e["mutual"] else c_edge
            line = dwg.line(start=(sx, sy), end=(ex, ey), stroke=col, stroke_width=1.5)
            line["marker-end"] = "url(#disp-arrow)"
            if e["mutual"]:
                line["marker-start"] = "url(#disp-arrow-rev)"
            dwg.add(line)

        for n in g["nodes"]:
            x, y = _pos(n)
            dwg.add(
                dwg.circle(
                    center=(x, y),
                    r=R,
                    fill=(c_final if n["final"] else c_node),
                    stroke=(c_final_edge if n["final"] else c_node_edge),
                    stroke_width=1.4,
                )
            )
            label = n["glyph"] if n["glyph"] else n["label"]
            dwg.add(
                dwg.text(
                    label,
                    insert=(x, y),
                    text_anchor="middle",
                    dominant_baseline="central",
                    font_size=("17px" if n["glyph"] else "13px"),
                    font_family="'Noto Sans Symbols', 'Noto Sans Symbols2', sans-serif",
                    fill=c_glyph,
                )
            )
        x_off += gw + pad

    if filename:
        dwg.save()
    return dwg.tostring()
