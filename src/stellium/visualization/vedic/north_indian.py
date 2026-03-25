"""North Indian style Vedic chart renderer.

The North Indian chart is a square with an inner diamond (X through it),
creating 12 triangular houses. House positions are FIXED:

    House 1  = top diamond (ASC — always here)
    House 4  = left diamond
    House 7  = bottom diamond
    House 10 = right diamond
    Houses 2,3 / 5,6 / 8,9 / 11,12 = side triangles in each quadrant

Signs ROTATE based on the ascendant. The traditional way to indicate
which sign is in each house is to write the sign's ordinal number
(1=Aries, 2=Taurus, etc.) at the inner corners of the chart.
"""

from __future__ import annotations

import svgwrite

from stellium.core.models import CalculatedChart
from stellium.visualization.core import ZODIAC_GLYPHS, get_glyph
from stellium.visualization.vedic.south_indian import (
    _GLYPH_FONT,
    _PLANET_ABBREV,
    _SIGN_ABBREV,
    _SIGN_NAMES,
    _THEMES,
    VedicPlanetInfo,
)


class NorthIndianRenderer:
    """Render a North Indian style Vedic chart as SVG.

    Usage::

        renderer = NorthIndianRenderer(size=500, theme="classic")
        svg_string = renderer.render(chart)
        renderer.render_to_file(chart, "vedic_north.svg")
    """

    def __init__(
        self,
        size: int = 500,
        theme: str = "classic",
        show_degrees: bool = False,
        label_style: str = "abbreviation",
    ) -> None:
        """
        Args:
            size: SVG width/height in pixels.
            theme: Color theme — "classic", "dark", or "traditional".
            show_degrees: Show degree + minutes for each planet.
            label_style: "abbreviation" (Ari, Tau), "glyph" (unicode symbols),
                "full" (Aries, Taurus), or "number" (1, 2 — traditional North Indian).
        """
        self.size = size
        self.theme = _THEMES.get(theme, _THEMES["classic"])
        self.show_degrees = show_degrees
        self.label_style = label_style

    def _sign_label(self, sign_idx: int) -> str:
        if self.label_style == "number":
            return str(sign_idx + 1)
        elif self.label_style == "glyph":
            return ZODIAC_GLYPHS[sign_idx]
        elif self.label_style == "full":
            return _SIGN_NAMES[sign_idx]
        return _SIGN_ABBREV[sign_idx]

    def _planet_label(self, planet: VedicPlanetInfo) -> str:
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

    def _font_family(self) -> str:
        return _GLYPH_FONT if self.label_style == "glyph" else "sans-serif"

    def _get_planets_by_sign(
        self, chart: CalculatedChart
    ) -> dict[int, list[VedicPlanetInfo]]:
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
        houses = chart.get_houses()
        if houses and houses.cusps:
            return int(houses.cusps[0] // 30)
        return 0

    def render(self, chart: CalculatedChart) -> str:
        th = self.theme
        s = self.size
        c = s / 2
        title_h = 48  # space for name + date + location
        total_h = s + title_h
        yo = title_h  # y-offset for chart area
        pad = s * 0.05

        dwg = svgwrite.Drawing(size=(s, total_h))
        dwg.add(dwg.rect(insert=(0, 0), size=(s, total_h), fill=th["bg"]))

        # ── Outer square ──
        dwg.add(
            dwg.rect(
                insert=(pad, yo + pad),
                size=(s - 2 * pad, s - 2 * pad),
                fill="none",
                stroke=th["line"],
                stroke_width=2,
            )
        )

        # Key points (in chart-area coordinates, offset by yo when drawing)
        tl = (pad, pad)
        tr = (s - pad, pad)
        bl = (pad, s - pad)
        br = (s - pad, s - pad)
        mt = (c, pad)  # mid-top
        ml = (pad, c)  # mid-left
        mb = (c, s - pad)  # mid-bottom
        mr = (s - pad, c)  # mid-right

        def draw_line(p1, p2, width=1):
            dwg.add(
                dwg.line(
                    start=(p1[0], yo + p1[1]),
                    end=(p2[0], yo + p2[1]),
                    stroke=th["line"],
                    stroke_width=width,
                )
            )

        # ── Inner diamond (connect midpoints of sides) ──
        dwg.add(
            dwg.polygon(
                points=[
                    (mt[0], yo + mt[1]),
                    (mr[0], yo + mr[1]),
                    (mb[0], yo + mb[1]),
                    (ml[0], yo + ml[1]),
                ],
                fill="none",
                stroke=th["line"],
                stroke_width=1.5,
            )
        )

        # ── X diagonals (corner to corner) ──
        draw_line(tl, br)
        draw_line(tr, bl)

        # ── ASC highlight (house 1 = top triangle) ──
        dwg.add(
            dwg.polygon(
                points=[(tl[0], yo + tl[1]), (mt[0], yo + mt[1]), (tr[0], yo + tr[1])],
                fill=th["asc_bg"],
                stroke="none",
                opacity=0.4,
            )
        )

        # ── Chart data ──
        asc_sign = self._get_asc_sign_index(chart)
        planets_by_sign = self._get_planets_by_sign(chart)

        # house_num → sign_index
        house_to_sign = {h + 1: (asc_sign + h) % 12 for h in range(12)}

        font = self._font_family()
        n = 10  # nudge for sign labels

        # ── Sign labels ──
        # Cardinal houses: just offset from center X crossing
        cardinal_sign_pos = {
            1: (c, c - n),  # above center
            4: (c - n, c),  # left of center
            7: (c, c + n),  # below center
            10: (c + n, c),  # right of center
        }

        # Side triangle pairs: positioned where the X diagonals cross
        # the inner diamond edges.
        #
        # The inner diamond edge from mid-top to mid-left is crossed by
        # the X diagonal from top-left to bottom-right. That crossing
        # point is at (midpoint of mt and ml) = ((c+pad)/2, (pad+c)/2)
        # which simplifies to the quarter-point of the square.

        q = (s - 2 * pad) / 4  # quarter of the inner square

        # X crosses upper-left diamond edge: houses 2,3
        ul_x, ul_y = pad + q, pad + q
        # X crosses lower-left diamond edge: houses 5,6
        ll_x, ll_y = pad + q, s - pad - q
        # X crosses lower-right diamond edge: houses 8,9
        lr_x, lr_y = s - pad - q, s - pad - q
        # X crosses upper-right diamond edge: houses 11,12
        ur_x, ur_y = s - pad - q, pad + q

        # Both labels sit OUTSIDE the diamond, on either side of the X line.
        # The X goes from top-left to bottom-right through the upper-left
        # crossing point. "Outside the diamond" means toward the corner of
        # the square (away from center). Straddling the X means one label
        # is shifted perpendicular to the X line on each side.

        # Perpendicular nudge to straddle the X line
        pn = n * 0.9

        # Outward nudge: push the whole pair away from center (toward their corner)
        on = n * 0.8  # outward nudge

        side_sign_pos = {
            # Upper-left pair: nudged northwest (toward top-left corner)
            2: (ul_x - on - pn, ul_y - on + pn),
            3: (ul_x - on + pn, ul_y - on - pn),
            # Lower-left pair: nudged southwest (toward bottom-left corner)
            5: (ll_x - on + pn, ll_y + on + pn),
            6: (ll_x - on - pn, ll_y + on - pn),
            # Lower-right pair: nudged southeast (toward bottom-right corner)
            8: (lr_x + on + pn, lr_y + on - pn),
            9: (lr_x + on - pn, lr_y + on + pn),
            # Upper-right pair: nudged northeast (toward top-right corner)
            11: (ur_x + on - pn, ur_y - on - pn),
            12: (ur_x + on + pn, ur_y - on + pn),
        }

        all_sign_pos = {**cardinal_sign_pos, **side_sign_pos}

        for house_num, (sx, sy) in all_sign_pos.items():
            sign_idx = house_to_sign[house_num]
            label = self._sign_label(sign_idx)
            dwg.add(
                dwg.text(
                    label,
                    insert=(sx, yo + sy),
                    font_family=font,
                    font_size=10,
                    fill=th["sign_text"],
                    text_anchor="middle",
                    dominant_baseline="central",
                )
            )

        # ── Planet text ──
        # Planet centers use fractional positions within the square.
        # Inner square runs from pad to s-pad on both axes.
        iw = s - 2 * pad  # inner width/height

        def sq(fx: float, fy: float) -> tuple[float, float]:
            """Convert fractional (0-1) position within the square to coords."""
            return (pad + iw * fx, pad + iw * fy)

        planet_centers = {
            1: sq(1 / 2, 1 / 4),  # top diamond: centered, 1/4 down
            2: sq(1 / 4, 1 / 8),  # upper-left triangle (wide)
            3: sq(1 / 8, 1 / 4),  # upper-left triangle (tall)
            4: sq(1 / 4, 1 / 2),  # left diamond: 1/4 across, centered
            5: sq(1 / 8, 3 / 4),  # lower-left triangle (tall)
            6: sq(1 / 4, 7 / 8),  # lower-left triangle (wide)
            7: sq(1 / 2, 3 / 4),  # bottom diamond: centered, 3/4 down
            8: sq(3 / 4, 7 / 8),  # lower-right triangle (wide)
            9: sq(7 / 8, 3 / 4),  # lower-right triangle (tall)
            10: sq(3 / 4, 1 / 2),  # right diamond: 3/4 across, centered
            11: sq(7 / 8, 1 / 4),  # upper-right triangle (tall)
            12: sq(3 / 4, 1 / 8),  # upper-right triangle (wide)
        }

        for house_num in range(1, 13):
            sign_idx = house_to_sign[house_num]
            cx, cy = planet_centers[house_num]
            planets = planets_by_sign.get(sign_idx, [])

            if not planets and house_num == 1:
                # Show "As" in empty house 1
                dwg.add(
                    dwg.text(
                        "As",
                        insert=(cx, yo + cy),
                        font_family="sans-serif",
                        font_size=11,
                        fill=th["house_marker"],
                        text_anchor="middle",
                        font_weight="bold",
                    )
                )
                continue

            # Center the planet stack vertically
            start_y = cy - (len(planets) * 14) / 2 + 7
            for planet in planets:
                label = self._planet_label(planet)
                dwg.add(
                    dwg.text(
                        label,
                        insert=(cx, yo + start_y),
                        font_family=font,
                        font_size=11,
                        fill=th["planet_text"],
                        text_anchor="middle",
                    )
                )
                start_y += 14

        # ── Title area above chart: name, datetime, location ──
        info_y = 14

        name = chart.metadata.get("name") if hasattr(chart, "metadata") else None
        if name:
            dwg.add(
                dwg.text(
                    name,
                    insert=(c, info_y),
                    font_family="sans-serif",
                    font_size=13,
                    fill=th["planet_text"],
                    text_anchor="middle",
                    font_weight="bold",
                )
            )
            info_y += 15

        if hasattr(chart, "datetime") and chart.datetime:
            if chart.datetime.local_datetime:
                dt_str = chart.datetime.local_datetime.strftime("%b %d, %Y  %I:%M %p")
            else:
                dt_str = chart.datetime.utc_datetime.strftime("%b %d, %Y  %H:%M UTC")
            dwg.add(
                dwg.text(
                    dt_str,
                    insert=(c, info_y),
                    font_family="sans-serif",
                    font_size=10,
                    fill=th["sign_text"],
                    text_anchor="middle",
                )
            )
            info_y += 13

        if hasattr(chart, "location") and chart.location:
            loc_name = getattr(chart.location, "name", None)
            if loc_name:
                dwg.add(
                    dwg.text(
                        loc_name,
                        insert=(c, info_y),
                        font_family="sans-serif",
                        font_size=10,
                        fill=th["sign_text"],
                        text_anchor="middle",
                    )
                )
                info_y += 13

        dwg.add(
            dwg.text(
                "North Indian",
                insert=(c, info_y),
                font_family="sans-serif",
                font_size=9,
                fill=th["sign_text"],
                text_anchor="middle",
                font_style="italic",
            )
        )

        return dwg.tostring()

    def render_to_file(self, chart: CalculatedChart, path: str) -> None:
        from pathlib import Path as _Path

        _Path(path).write_text(self.render(chart))
