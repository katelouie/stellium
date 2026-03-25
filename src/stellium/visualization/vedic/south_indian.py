"""South Indian style Vedic chart renderer.

The South Indian chart is a 4×4 grid where the 4 center cells are
merged, creating 12 outer cells. Each cell represents a fixed zodiac
sign (Aries is always in the same position). Planets are placed in
the cell corresponding to their sign.

Grid layout (sign indices 0-11, where 0=Aries):
    ┌──────┬──────┬──────┬──────┐
    │  11  │   0  │   1  │   2  │
    │ Pisc │ Arie │ Taur │ Gemi │
    ├──────┼──────┴──────┼──────┤
    │  10  │             │   3  │
    │ Aqua │   (center)  │ Canc │
    ├──────┤             ├──────┤
    │   9  │             │   4  │
    │ Capr │             │  Leo │
    ├──────┼──────┬──────┼──────┤
    │   8  │   7  │   6  │   5  │
    │ Sagi │ Scor │ Libr │ Virg │
    └──────┴──────┴──────┴──────┘
"""

from __future__ import annotations

from dataclasses import dataclass

import svgwrite

from stellium.core.models import CalculatedChart
from stellium.visualization.core import ZODIAC_GLYPHS, get_glyph

# ── Sign names and glyphs ──────────────────────────────────────────

_SIGN_NAMES = [
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

_SIGN_ABBREV = [
    "Ari",
    "Tau",
    "Gem",
    "Can",
    "Leo",
    "Vir",
    "Lib",
    "Sco",
    "Sag",
    "Cap",
    "Aqu",
    "Pis",
]

_PLANET_ABBREV: dict[str, str] = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mercury": "Me",
    "Venus": "Ve",
    "Mars": "Ma",
    "Jupiter": "Ju",
    "Saturn": "Sa",
    "Uranus": "Ur",
    "Neptune": "Ne",
    "Pluto": "Pl",
    "True Node": "Ra",
    "South Node": "Ke",
    "Chiron": "Ch",
    "Black Moon Lilith": "Li",
    "Part of Fortune": "PoF",
    "Ceres": "Ce",
    "Pallas": "Pa",
    "Juno": "Jn",
    "Vesta": "Ve",
}

# Font stack for unicode zodiac/planet glyphs (same as Western chart system)
_GLYPH_FONT = (
    '"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif'
)

# Cell positions: sign_index → (row, col) in the 4×4 grid
# Arranged counterclockwise from Pisces (top-left)
_SIGN_CELLS: dict[int, tuple[int, int]] = {
    0: (0, 1),  # Aries — top row, 2nd col
    1: (0, 2),  # Taurus
    2: (0, 3),  # Gemini
    3: (1, 3),  # Cancer
    4: (2, 3),  # Leo
    5: (3, 3),  # Virgo
    6: (3, 2),  # Libra
    7: (3, 1),  # Scorpio
    8: (3, 0),  # Sagittarius
    9: (2, 0),  # Capricorn
    10: (1, 0),  # Aquarius
    11: (0, 0),  # Pisces
}

# ── Themes ─────────────────────────────────────────────────────────

_THEMES: dict[str, dict[str, str]] = {
    "classic": {
        "bg": "#ffffff",
        "line": "#333333",
        "sign_text": "#666666",
        "planet_text": "#222222",
        "house_marker": "#cc4444",
        "center_bg": "#fafaf5",
        "asc_bg": "#fff3e0",
    },
    "dark": {
        "bg": "#1a1a2e",
        "line": "#555577",
        "sign_text": "#8888aa",
        "planet_text": "#cccccc",
        "house_marker": "#ff8866",
        "center_bg": "#22223a",
        "asc_bg": "#2a2a40",
    },
    "traditional": {
        "bg": "#fdf6e3",
        "line": "#8b4513",
        "sign_text": "#8b6914",
        "planet_text": "#333333",
        "house_marker": "#cc3300",
        "center_bg": "#faf0d7",
        "asc_bg": "#fff0cc",
    },
}


@dataclass(frozen=True)
class VedicPlanetInfo:
    """Planet data for placement in a Vedic chart cell."""

    name: str
    glyph: str
    sign_index: int
    degree: float
    is_retrograde: bool


class SouthIndianRenderer:
    """Render a South Indian style Vedic chart as SVG.

    Usage::

        renderer = SouthIndianRenderer(size=500, theme="classic")
        svg_string = renderer.render(chart)

        # Or save directly:
        renderer.render_to_file(chart, "vedic_south.svg")
    """

    def __init__(
        self,
        size: int = 500,
        theme: str = "classic",
        show_degrees: bool = False,
        show_house_numbers: bool = True,
        label_style: str = "abbreviation",
    ) -> None:
        """
        Args:
            size: SVG width/height in pixels.
            theme: Color theme — "classic", "dark", or "traditional".
            show_degrees: Show degree + minutes for each planet.
            show_house_numbers: Show house numbers in each cell.
            label_style: How to render signs/planets —
                "abbreviation" (Su, Mo, Ari, Tau — traditional Vedic style),
                "glyph" (☉, ☽, ♈, ♉ — Unicode symbols),
                or "full" (Sun, Moon, Aries, Taurus — full names).
        """
        self.size = size
        self.cell_size = size / 4
        self.theme = _THEMES.get(theme, _THEMES["classic"])
        self.show_degrees = show_degrees
        self.show_house_numbers = show_house_numbers
        self.label_style = label_style

    def _sign_label(self, sign_idx: int) -> str:
        """Get the sign label in the current label style."""
        if self.label_style == "number":
            return str(sign_idx + 1)
        elif self.label_style == "glyph":
            return ZODIAC_GLYPHS[sign_idx]
        elif self.label_style == "full":
            return _SIGN_NAMES[sign_idx]
        return _SIGN_ABBREV[sign_idx]

    def _planet_label(self, planet: VedicPlanetInfo) -> str:
        """Get the planet label in the current label style with optional degree."""
        if self.label_style == "glyph":
            name_part = planet.glyph
        elif self.label_style == "full":
            name_part = planet.name
        else:
            name_part = _PLANET_ABBREV.get(planet.name, planet.name[:2])

        if planet.is_retrograde:
            name_part += " R"

        if self.show_degrees:
            deg = int(planet.degree)
            mins = int((planet.degree - deg) * 60)
            name_part += f" {deg}°{mins:02d}'"

        return name_part

    def _sign_font_family(self) -> str:
        """Font family depending on label style."""
        if self.label_style == "glyph":
            return _GLYPH_FONT
        return "sans-serif"

    def _get_chart_info(
        self, chart: CalculatedChart
    ) -> list[tuple[str, int, str, str]]:
        """Extract chart info lines: (text, font_size, font_weight, color)."""
        th = self.theme
        lines = []

        # Name
        name = chart.metadata.get("name") if hasattr(chart, "metadata") else None
        if name:
            lines.append((name, 13, "bold", th["planet_text"]))

        # Datetime
        if hasattr(chart, "datetime") and chart.datetime:
            if chart.datetime.local_datetime:
                dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y  %I:%M %p")
            else:
                dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y  %H:%M UTC")
            lines.append((dt_str, 10, "normal", th["sign_text"]))

        # Location
        if hasattr(chart, "location") and chart.location:
            loc_name = getattr(chart.location, "name", None)
            if loc_name:
                lines.append((loc_name, 10, "normal", th["sign_text"]))

        return lines

    def _get_planets_by_sign(
        self, chart: CalculatedChart
    ) -> dict[int, list[VedicPlanetInfo]]:
        """Group planets by their zodiac sign index (0=Aries)."""
        by_sign: dict[int, list[VedicPlanetInfo]] = {i: [] for i in range(12)}

        for pos in chart.get_planets():
            sign_idx = int(pos.longitude // 30)
            degree = pos.longitude % 30
            glyph_info = get_glyph(pos.name)
            is_retro = pos.speed_longitude < 0 if pos.speed_longitude else False

            by_sign[sign_idx].append(
                VedicPlanetInfo(
                    name=pos.name,
                    glyph=glyph_info["value"],
                    sign_index=sign_idx,
                    degree=degree,
                    is_retrograde=is_retro,
                )
            )

        return by_sign

    def _get_asc_sign_index(self, chart: CalculatedChart) -> int:
        """Get the sign index where the ASC falls."""
        houses = chart.get_houses()
        if houses and houses.cusps:
            asc_long = houses.cusps[0]  # first cusp = ASC
            return int(asc_long // 30)
        return 0

    def _cell_rect(self, row: int, col: int) -> tuple[float, float, float, float]:
        """Get (x, y, width, height) for a grid cell."""
        cs = self.cell_size
        return (col * cs, row * cs, cs, cs)

    def render(self, chart: CalculatedChart) -> str:
        """Render the chart as an SVG string."""
        th = self.theme
        cs = self.cell_size
        size = self.size

        dwg = svgwrite.Drawing(size=(size, size))

        # Background
        dwg.add(dwg.rect(insert=(0, 0), size=(size, size), fill=th["bg"]))

        # Center area background
        dwg.add(
            dwg.rect(
                insert=(cs, cs),
                size=(cs * 2, cs * 2),
                fill=th["center_bg"],
            )
        )

        planets_by_sign = self._get_planets_by_sign(chart)
        asc_sign = self._get_asc_sign_index(chart)

        # Compute house numbers: house 1 = ASC sign, house 2 = next sign, etc.
        house_for_sign: dict[int, int] = {}
        for h in range(12):
            sign_idx = (asc_sign + h) % 12
            house_for_sign[sign_idx] = h + 1

        # Draw cells
        for sign_idx, (row, col) in _SIGN_CELLS.items():
            x, y, w, h = self._cell_rect(row, col)
            is_asc = sign_idx == asc_sign

            # ASC cell highlight
            if is_asc:
                dwg.add(dwg.rect(insert=(x, y), size=(w, h), fill=th["asc_bg"]))

            # Cell border
            dwg.add(
                dwg.rect(
                    insert=(x, y),
                    size=(w, h),
                    fill="none",
                    stroke=th["line"],
                    stroke_width=1.5,
                )
            )

            # Sign label (top-left corner)
            dwg.add(
                dwg.text(
                    self._sign_label(sign_idx),
                    insert=(x + 4, y + 14),
                    font_family=self._sign_font_family(),
                    font_size=11,
                    fill=th["sign_text"],
                )
            )

            # House number (top-right corner)
            if self.show_house_numbers:
                house_num = house_for_sign.get(sign_idx, 0)
                dwg.add(
                    dwg.text(
                        str(house_num),
                        insert=(x + w - 6, y + 14),
                        font_family="sans-serif",
                        font_size=9,
                        fill=th["house_marker"],
                        text_anchor="end",
                    )
                )

            # ASC marker
            if is_asc:
                dwg.add(
                    dwg.text(
                        "ASC",
                        insert=(x + w - 6, y + h - 4),
                        font_family="sans-serif",
                        font_size=8,
                        fill=th["house_marker"],
                        text_anchor="end",
                        font_weight="bold",
                    )
                )

            # Planets in this sign
            planets = planets_by_sign.get(sign_idx, [])
            planet_y = y + 30  # start below the sign label
            for _pi, planet in enumerate(planets):
                label = self._planet_label(planet)
                dwg.add(
                    dwg.text(
                        label,
                        insert=(x + w / 2, planet_y),
                        font_family=self._sign_font_family(),
                        font_size=12,
                        fill=th["planet_text"],
                        text_anchor="middle",
                    )
                )
                planet_y += 16

        # Center text: chart info (name, datetime, location)
        cx = size / 2
        cy = size / 2

        info_lines = self._get_chart_info(chart)
        # Stack lines centered in the middle area
        total_lines = len(info_lines) + 1  # +1 for "South Indian" label
        line_h = 16
        start_y = cy - (total_lines * line_h) / 2 + line_h / 2

        for i, (text, font_size, weight, color) in enumerate(info_lines):
            dwg.add(
                dwg.text(
                    text,
                    insert=(cx, start_y + i * line_h),
                    font_family="sans-serif",
                    font_size=font_size,
                    fill=color,
                    text_anchor="middle",
                    font_weight=weight,
                )
            )

        # "South Indian" label at bottom of center block
        dwg.add(
            dwg.text(
                "South Indian",
                insert=(cx, start_y + len(info_lines) * line_h),
                font_family="sans-serif",
                font_size=9,
                fill=th["sign_text"],
                text_anchor="middle",
                font_style="italic",
            )
        )

        return dwg.tostring()

    def render_to_file(self, chart: CalculatedChart, path: str) -> None:
        """Render and save to an SVG file."""
        from pathlib import Path as _Path

        _Path(path).write_text(self.render(chart))
