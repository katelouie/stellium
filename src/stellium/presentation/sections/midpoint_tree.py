"""
Midpoint Tree visualization section.

Generates tree diagrams showing which midpoints aspect focal points (planets/angles).
This is a standard Uranian/Hamburg astrology technique for interpreting planetary pictures.

Example tree output:
    ☉ Sun (15°23' ♑)
    ├── ☽/♂ ☌ 0.3°   Moon/Mars conjunction
    ├── ♀/♄ □ 1.1°   Venus/Saturn square
    └── ☿/♃ ⊼ 0.8°   Mercury/Jupiter semi-square
"""

from dataclasses import dataclass
from typing import Any

import svgwrite

from stellium.core.models import (
    CalculatedChart,
    CelestialPosition,
    MidpointPosition,
    ObjectType,
)

from ._utils import get_aspect_display, get_object_display, get_sign_glyph


@dataclass
class MidpointBranch:
    """A single branch in a midpoint tree (one midpoint aspecting the focal point)."""

    midpoint: MidpointPosition | CelestialPosition
    midpoint_display: str  # e.g., "☽/♂" or "Moon/Mars"
    aspect_name: str  # e.g., "Conjunction"
    aspect_glyph: str  # e.g., "☌"
    orb: float
    midpoint_position: str  # e.g., "15°05' ♑"


@dataclass
class MidpointTree:
    """A complete midpoint tree for one focal point."""

    focal_point: CelestialPosition
    focal_display: str  # e.g., "☉ Sun"
    focal_position: str  # e.g., "15°23' ♑"
    branches: list[MidpointBranch]


class MidpointTreeSection:
    """
    Midpoint Tree visualization section.

    Generates tree diagrams showing which midpoints aspect focal points.
    Standard technique in Uranian/Hamburg astrology for interpreting
    planetary pictures.

    For each focal point (default: Sun, Moon, MC, ASC), shows all midpoints
    that aspect it within the configured orb.

    Example::

        section = MidpointTreeSection(
            tree_bases=["Sun", "Moon", "MC", "ASC"],
            orb=1.5,
            aspect_mode="hard",  # conjunction + 45° series
            output="both"
        )
    """

    # Default focal points (tree bases)
    DEFAULT_TREE_BASES = ["Sun", "Moon", "MC", "ASC"]

    # Default objects to include in midpoint calculations
    DEFAULT_BRANCH_OBJECTS = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "ASC",
        "MC",
        "True Node",
    ]

    # Hard aspects for Uranian work (the 22.5° series, but we use 45° increments)
    HARD_ASPECTS = {
        "Conjunction": 0,
        "Semisquare": 45,
        "Square": 90,
        "Sesquisquare": 135,
        "Opposition": 180,
    }

    ALL_ASPECTS = {
        "Conjunction": 0,
        "Sextile": 60,
        "Square": 90,
        "Trine": 120,
        "Opposition": 180,
    }

    def __init__(
        self,
        tree_bases: list[str] | None = None,
        branch_objects: list[str] | None = None,
        orb: float = 1.5,
        aspect_mode: str = "conjunction",
        output: str = "both",
    ) -> None:
        """
        Initialize midpoint tree section.

        Args:
            tree_bases: Focal points to build trees for.
                Default: ["Sun", "Moon", "MC", "ASC"]
            branch_objects: Objects to include in midpoint pairs.
                Default: 10 planets + ASC + MC + True Node
            orb: Maximum orb in degrees (default 1.5°)
            aspect_mode: Which aspects to check:
                - "conjunction": Only conjunctions (0°)
                - "hard": Conjunction + 45° series (0°, 45°, 90°, 135°, 180°)
                - "all": All major aspects
            output: What to generate:
                - "svg": Just SVG visualization
                - "text": Just text output
                - "both": Both SVG and text (default)
        """
        self.tree_bases = tree_bases or self.DEFAULT_TREE_BASES
        self.branch_objects = branch_objects or self.DEFAULT_BRANCH_OBJECTS
        self.orb = orb
        self.aspect_mode = aspect_mode
        self.output = output

        # Set which aspects to check based on mode
        if aspect_mode == "conjunction":
            self._aspects = {"Conjunction": 0}
        elif aspect_mode == "hard":
            self._aspects = self.HARD_ASPECTS.copy()
        else:  # all
            self._aspects = self.ALL_ASPECTS.copy()

    @property
    def section_name(self) -> str:
        if self.aspect_mode == "hard":
            return "Midpoint Trees (Hard Aspects)"
        elif self.aspect_mode == "conjunction":
            return "Midpoint Trees (Conjunctions)"
        return "Midpoint Trees"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate midpoint tree visualization data."""
        # Get midpoints from chart
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

        # Filter midpoints to only those made from branch_objects
        filtered_midpoints = self._filter_midpoints(midpoints)

        if not filtered_midpoints:
            return {
                "type": "text",
                "text": "No midpoints found matching the configured branch objects.",
            }

        # Build trees for each focal point
        trees = []
        for base_name in self.tree_bases:
            focal = self._get_position(chart, base_name)
            if focal is None:
                continue

            tree = self._build_tree(focal, filtered_midpoints)
            if tree.branches:  # Only include trees that have branches
                trees.append(tree)

        if not trees:
            return {
                "type": "text",
                "text": f"No midpoints found within {self.orb}° of focal points.",
            }

        # Generate output based on mode
        results = []

        if self.output in ("text", "both"):
            text_output = self._render_text_trees(trees)
            results.append(
                (
                    "Midpoint Trees",
                    {
                        "type": "text",
                        "text": text_output,
                    },
                )
            )

        if self.output in ("svg", "both"):
            svg_output = self._render_svg_trees(trees)
            # Calculate height based on content
            height = self._calculate_svg_height(trees)
            results.append(
                (
                    "Midpoint Tree Visualization",
                    {
                        "type": "svg",
                        "content": svg_output,
                        "width": 780,
                        "height": height,
                    },
                )
            )

        if len(results) == 1:
            return results[0][1]
        else:
            return {
                "type": "compound",
                "sections": results,
            }

    def _filter_midpoints(
        self, midpoints: list[CelestialPosition]
    ) -> list[CelestialPosition]:
        """Filter midpoints to only those made from branch_objects."""
        filtered = []
        branch_set = set(self.branch_objects)

        for mp in midpoints:
            if isinstance(mp, MidpointPosition):
                # Direct access to component objects
                if mp.object1.name in branch_set and mp.object2.name in branch_set:
                    filtered.append(mp)
            else:
                # Parse name for legacy midpoints
                obj1, obj2 = self._parse_midpoint_name(mp.name)
                if obj1 in branch_set and obj2 in branch_set:
                    filtered.append(mp)

        return filtered

    def _get_position(
        self, chart: CalculatedChart, name: str
    ) -> CelestialPosition | None:
        """Get a position from the chart by name."""
        for pos in chart.positions:
            if pos.name == name:
                return pos
        return None

    def _build_tree(
        self, focal: CelestialPosition, midpoints: list[CelestialPosition]
    ) -> MidpointTree:
        """Build a midpoint tree for a focal point."""
        branches = []

        for mp in midpoints:
            # Skip if focal point is part of this midpoint
            if isinstance(mp, MidpointPosition):
                if focal.name in (mp.object1.name, mp.object2.name):
                    continue
            else:
                obj1, obj2 = self._parse_midpoint_name(mp.name)
                if focal.name in (obj1, obj2):
                    continue

            # Check each aspect type
            for aspect_name, aspect_angle in self._aspects.items():
                orb = self._calculate_orb(focal.longitude, mp.longitude, aspect_angle)

                if orb <= self.orb:
                    # Get display info
                    mp_display = self._get_midpoint_glyph_display(mp)
                    aspect_display_name, aspect_glyph = get_aspect_display(aspect_name)

                    # Format midpoint position
                    mp_pos = self._format_position(mp)

                    branches.append(
                        MidpointBranch(
                            midpoint=mp,
                            midpoint_display=mp_display,
                            aspect_name=aspect_display_name,
                            aspect_glyph=aspect_glyph,
                            orb=orb,
                            midpoint_position=mp_pos,
                        )
                    )

        # Sort branches by orb (tightest first)
        branches.sort(key=lambda b: b.orb)

        # Get focal point display info
        focal_display_name, focal_glyph = get_object_display(focal.name)
        focal_display = (
            f"{focal_glyph} {focal_display_name}" if focal_glyph else focal_display_name
        )
        focal_pos = self._format_position(focal)

        return MidpointTree(
            focal_point=focal,
            focal_display=focal_display,
            focal_position=focal_pos,
            branches=branches,
        )

    def _calculate_orb(self, lon1: float, lon2: float, aspect_angle: float) -> float:
        """Calculate orb between two longitudes for a given aspect."""
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff
        return abs(diff - aspect_angle)

    def _parse_midpoint_name(self, name: str) -> tuple[str, str]:
        """Parse midpoint name like 'Midpoint:Sun/Moon' into components."""
        if ":" in name:
            pair_part = name.split(":")[1]
        else:
            pair_part = name

        pair_part = pair_part.replace(" (indirect)", "")
        parts = pair_part.split("/")

        if len(parts) == 2:
            return parts[0], parts[1]
        return "", ""

    def _get_midpoint_glyph_display(self, mp: CelestialPosition) -> str:
        """Get glyph-based display for a midpoint (e.g., '☽/♂')."""
        if isinstance(mp, MidpointPosition):
            name1, glyph1 = get_object_display(mp.object1.name)
            name2, glyph2 = get_object_display(mp.object2.name)
        else:
            obj1, obj2 = self._parse_midpoint_name(mp.name)
            name1, glyph1 = get_object_display(obj1)
            name2, glyph2 = get_object_display(obj2)

        # Use glyph if available, otherwise fall back to short name for each component
        display1 = glyph1 if glyph1 else name1[:2]
        display2 = glyph2 if glyph2 else name2[:2]
        return f"{display1}/{display2}"

    def _get_midpoint_name_display(self, mp: CelestialPosition) -> str:
        """Get name-based display for a midpoint (e.g., 'Moon/Mars')."""
        if isinstance(mp, MidpointPosition):
            return f"{mp.object1.name}/{mp.object2.name}"
        else:
            obj1, obj2 = self._parse_midpoint_name(mp.name)
            return f"{obj1}/{obj2}"

    def _format_position(self, pos: CelestialPosition) -> str:
        """Format a position as '15°23' ♑'."""
        degree = int(pos.sign_degree)
        minute = int((pos.sign_degree % 1) * 60)
        sign_glyph = get_sign_glyph(pos.sign)
        return f"{degree}°{minute:02d}' {sign_glyph}"

    # =========================================================================
    # Text Rendering
    # =========================================================================

    def _render_text_trees(self, trees: list[MidpointTree]) -> str:
        """Render trees as text/ASCII art."""
        lines = []

        for i, tree in enumerate(trees):
            if i > 0:
                lines.append("")  # Blank line between trees

            # Tree header
            lines.append(f"{tree.focal_display} ({tree.focal_position})")

            # Branches
            for j, branch in enumerate(tree.branches):
                is_last = j == len(tree.branches) - 1
                prefix = "└──" if is_last else "├──"

                # Format: ├── ☽/♂ ☌ 0.3°  Moon/Mars
                name_display = self._get_midpoint_name_display(branch.midpoint)
                line = f"    {prefix} {branch.midpoint_display} {branch.aspect_glyph} {branch.orb:.1f}°  {name_display}"
                lines.append(line)

        return "\n".join(lines)

    # =========================================================================
    # SVG Rendering
    # =========================================================================

    def _calculate_tree_height(self, tree: MidpointTree) -> int:
        """Calculate height needed for a single tree."""
        # Tree header (40) + branches (25 each) + spacing (20)
        return 40 + len(tree.branches) * 25 + 20

    def _calculate_svg_height(self, trees: list[MidpointTree], columns: int = 3) -> int:
        """Calculate required SVG height based on content with multi-column layout."""
        if not trees:
            return 200

        # Distribute trees into columns
        num_cols = min(columns, len(trees))
        col_trees: list[list[MidpointTree]] = [[] for _ in range(num_cols)]

        for i, tree in enumerate(trees):
            col_trees[i % num_cols].append(tree)

        # Calculate height of each column
        col_heights = []
        for col in col_trees:
            height = sum(self._calculate_tree_height(t) for t in col)
            col_heights.append(height)

        # Total height = header + tallest column
        return 60 + max(col_heights) if col_heights else 200

    def _render_svg_trees(self, trees: list[MidpointTree]) -> str:
        """Render trees as SVG with multi-column layout."""
        columns = 3
        width = 780  # Slightly wider for 3 columns
        col_width = (width - 40) // columns  # 40px total margin

        height = self._calculate_svg_height(trees, columns)

        dwg = svgwrite.Drawing(size=(width, height))

        # Background
        dwg.add(dwg.rect((0, 0), (width, height), fill="#ffffff"))

        # Title
        dwg.add(
            dwg.text(
                "MIDPOINT TREES",
                insert=(width / 2, 30),
                text_anchor="middle",
                font_family="Arial, sans-serif",
                font_size="16px",
                font_weight="bold",
                fill="#2d2330",
            )
        )

        # Distribute trees into columns (round-robin for balance)
        num_cols = min(columns, len(trees))
        col_trees: list[list[MidpointTree]] = [[] for _ in range(num_cols)]

        for i, tree in enumerate(trees):
            col_trees[i % num_cols].append(tree)

        # Render each column
        for col_idx, col in enumerate(col_trees):
            x_offset = 20 + col_idx * col_width
            y_offset = 60

            for tree in col:
                y_offset = self._render_svg_tree(
                    dwg, tree, y_offset, x_offset, col_width - 20
                )
                y_offset += 20  # Spacing between trees

        return dwg.tostring()

    def _render_svg_tree(
        self,
        dwg: svgwrite.Drawing,
        tree: MidpointTree,
        y_start: float,
        x_offset: float = 40,
        max_width: float = 200,
    ) -> float:
        """Render a single tree in SVG, return new y position."""
        x_base = x_offset
        y = y_start

        # Tree header (focal point)
        dwg.add(
            dwg.text(
                f"{tree.focal_display}",
                insert=(x_base, y),
                font_family="Noto Sans Symbols2, Arial, sans-serif",
                font_size="14px",
                font_weight="bold",
                fill="#4a3353",
            )
        )

        # Position after the name
        dwg.add(
            dwg.text(
                f"({tree.focal_position})",
                insert=(x_base + 100, y),
                font_family="Noto Sans Symbols2, Arial, sans-serif",
                font_size="12px",
                fill="#6b4d6e",
            )
        )

        y += 25

        # Draw branches
        for i, branch in enumerate(tree.branches):
            is_last = i == len(tree.branches) - 1

            # Tree line
            line_x = x_base + 10

            # Vertical line - always draw from above down to horizontal junction
            # For non-last branches, extend below for the next branch
            vertical_end = y - 5 if is_last else y + 10
            dwg.add(
                dwg.line(
                    (line_x, y - 15),
                    (line_x, vertical_end),
                    stroke="#d0c8c0",
                    stroke_width=1,
                )
            )

            # Horizontal branch
            dwg.add(
                dwg.line(
                    (line_x, y - 5),
                    (line_x + 15, y - 5),
                    stroke="#d0c8c0",
                    stroke_width=1,
                )
            )

            # Branch content
            text_x = x_base + 30

            # Midpoint glyphs
            dwg.add(
                dwg.text(
                    branch.midpoint_display,
                    insert=(text_x, y),
                    font_family="Noto Sans Symbols2, Arial, sans-serif",
                    font_size="12px",
                    fill="#2d2330",
                )
            )

            # Aspect glyph
            dwg.add(
                dwg.text(
                    branch.aspect_glyph,
                    insert=(text_x + 45, y),
                    font_family="Noto Sans Symbols2, Arial, sans-serif",
                    font_size="12px",
                    fill="#4a3353",
                )
            )

            # Orb
            dwg.add(
                dwg.text(
                    f"{branch.orb:.1f}°",
                    insert=(text_x + 65, y),
                    font_family="Arial, sans-serif",
                    font_size="11px",
                    fill="#6b4d6e",
                )
            )

            # Full name
            name_display = self._get_midpoint_name_display(branch.midpoint)
            dwg.add(
                dwg.text(
                    name_display,
                    insert=(text_x + 110, y),
                    font_family="Arial, sans-serif",
                    font_size="11px",
                    fill="#8b7b8e",
                )
            )

            y += 25

        return y
