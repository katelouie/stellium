"""
Graphic Ephemeris Visualization (stellium.visualization.ephemeris)

Renders a graphic ephemeris showing planetary positions over time.
The X-axis represents time, the Y-axis represents zodiacal position
(optionally compressed to 90° or 45° harmonic).

Example:
    >>> from stellium.visualization import GraphicEphemeris
    >>> eph = GraphicEphemeris(
    ...     start_date="2025-01-01",
    ...     end_date="2025-12-31",
    ...     harmonic=90,
    ... )
    >>> eph.draw("ephemeris_2025.svg")
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Literal

import svgwrite

if TYPE_CHECKING:
    from stellium.core.models import CalculatedChart

from stellium.visualization.palettes import PlanetGlyphPalette, get_planet_glyph_color

# Default planets to show (outer planets + luminaries for typical use)
DEFAULT_PLANETS = [
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
]

# Extended set including Chiron and North Node
EXTENDED_PLANETS = DEFAULT_PLANETS + ["Chiron", "True Node"]

# Mapping planet names to Swiss Ephemeris IDs
PLANET_IDS = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
    "Uranus": 7,
    "Neptune": 8,
    "Pluto": 9,
    "True Node": 11,
    "Chiron": 15,
}

# Zodiac sign glyphs (proper astrological symbols, not emojis)
SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def _longitude_to_sign_degree(longitude: float) -> tuple[str, int]:
    """Convert longitude to sign glyph and degree."""
    sign_index = int(longitude // 30) % 12
    degree = int(longitude % 30)
    return SIGN_GLYPHS[sign_index], degree


@dataclass
class EphemerisDataPoint:
    """A single data point for one planet at one time."""

    date: date
    julian_day: float
    longitude: float  # 0-360° ecliptic longitude
    speed: float  # degrees per day (negative = retrograde)
    harmonic_position: float  # Position after harmonic compression


@dataclass
class StationPoint:
    """A retrograde or direct station point."""

    date: date
    julian_day: float
    longitude: float
    harmonic_position: float
    station_type: Literal["retrograde", "direct"]


@dataclass
class AspectCrossing:
    """A point where two planet lines cross (aspect in harmonic view)."""

    date: date
    harmonic_position: float
    planet1: str
    planet2: str
    aspect_type: str  # "conjunction", "square", "opposition"
    longitude1: float  # Actual longitude of planet 1
    longitude2: float  # Actual longitude of planet 2
    is_transit_to_natal: bool = False  # True if this is a transit-to-natal aspect


@dataclass
class NatalPosition:
    """A natal planet position for overlay on the ephemeris."""

    planet: str
    longitude: float
    harmonic_position: float


@dataclass
class GraphicEphemerisConfig:
    """Configuration for graphic ephemeris rendering."""

    start_date: date
    end_date: date
    harmonic: Literal[360, 90, 45] = 90
    planets: list[str] = field(default_factory=lambda: DEFAULT_PLANETS.copy())

    # Dimensions
    width: int = 1400
    height: int = 900

    # Margins (pixels)
    margin_left: int = 90  # Space for Y-axis labels + left glyphs
    margin_right: int = 80  # Space for right glyphs + degree info
    margin_top: int = 60  # Space for title
    margin_bottom: int = 80  # Space for X-axis labels + legend

    # Styling
    background_color: str = "#FFFFFF"
    grid_color: str = "#E8E8E8"
    grid_color_major: str = "#D0D0D0"
    axis_color: str = "#666666"
    text_color: str = "#333333"
    line_width: float = 2.5  # Thicker lines

    # Features
    show_stations: bool = True
    show_grid: bool = True
    show_title: bool = True
    show_legend: bool = True
    show_aspects: bool = True  # Show aspect markers at line crossings
    title: str | None = None  # Auto-generated if None

    # Data resolution
    days_per_point: int = 1  # Calculate position every N days


class GraphicEphemeris:
    """
    Graphic Ephemeris visualization.

    Renders planetary positions over time as a graph, with optional
    harmonic compression (90° or 45°) to show hard aspects as conjunctions.

    Example:
        >>> eph = GraphicEphemeris(
        ...     start_date="2025-01-01",
        ...     end_date="2025-12-31",
        ...     harmonic=90,
        ... )
        >>> eph.draw("ephemeris_2025.svg")

        # Include Chiron and North Node
        >>> eph = GraphicEphemeris(
        ...     start_date="2025-01-01",
        ...     end_date="2025-12-31",
        ...     planets=EXTENDED_PLANETS,
        ... )

        # With natal chart overlay (shows transit-to-natal aspects)
        >>> from stellium import ChartBuilder
        >>> natal = ChartBuilder.from_native(my_native).calculate()
        >>> eph = GraphicEphemeris(
        ...     start_date="2025-01-01",
        ...     end_date="2025-12-31",
        ...     natal_chart=natal,
        ... )
        >>> eph.draw("transits_2025.svg")
    """

    def __init__(
        self,
        start_date: str | date,
        end_date: str | date,
        harmonic: Literal[360, 90, 45] = 90,
        planets: list[str] | None = None,
        natal_chart: "CalculatedChart | None" = None,
        natal_planets: list[str] | None = None,
        width: int = 1400,
        height: int = 900,
        show_stations: bool = True,
        show_grid: bool = True,
        show_legend: bool = True,
        show_aspects: bool = True,
        title: str | None = None,
    ):
        """
        Initialize a graphic ephemeris.

        Args:
            start_date: Start date (YYYY-MM-DD string or date object)
            end_date: End date (YYYY-MM-DD string or date object)
            harmonic: Harmonic compression (360=full, 90=quarter, 45=eighth)
            planets: List of planet names to include (default: Sun through Pluto)
                     Use EXTENDED_PLANETS to include Chiron and North Node
            natal_chart: Optional CalculatedChart to overlay natal positions
            natal_planets: Which natal planets to show (default: same as planets)
            width: SVG width in pixels
            height: SVG height in pixels
            show_stations: Show retrograde/direct station markers
            show_grid: Show background grid lines
            show_legend: Show legend explaining station symbols
            show_aspects: Show aspect type labels at line crossings (90°/45° only)
                         If natal_chart is provided, shows transit-to-natal aspects instead
            title: Custom title (auto-generated if None)
        """
        # Parse dates if strings
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        self.config = GraphicEphemerisConfig(
            start_date=start_date,
            end_date=end_date,
            harmonic=harmonic,
            planets=planets if planets is not None else DEFAULT_PLANETS.copy(),
            width=width,
            height=height,
            show_stations=show_stations,
            show_grid=show_grid,
            show_legend=show_legend,
            show_aspects=show_aspects,
            title=title,
        )

        # Natal chart overlay
        self._natal_chart = natal_chart
        self._natal_planets = natal_planets
        self._natal_positions: list[NatalPosition] | None = None

        # Data storage (lazy-loaded)
        self._data: dict[str, list[EphemerisDataPoint]] | None = None
        self._stations: dict[str, list[StationPoint]] | None = None
        self._aspects: list[AspectCrossing] | None = None

    @property
    def plot_width(self) -> int:
        """Width of the plot area (excluding margins)."""
        return self.config.width - self.config.margin_left - self.config.margin_right

    @property
    def plot_height(self) -> int:
        """Height of the plot area (excluding margins)."""
        return self.config.height - self.config.margin_top - self.config.margin_bottom

    def _date_to_julian_day(self, d: date) -> float:
        """Convert a date to Julian Day number."""
        import swisseph as swe

        return swe.julday(d.year, d.month, d.day, 12.0)  # Noon UTC

    def _generate_data(self) -> dict[str, list[EphemerisDataPoint]]:
        """
        Calculate planetary positions for all dates in the range.

        Returns:
            Dictionary mapping planet names to lists of data points.
        """
        import swisseph as swe

        from stellium.engines.ephemeris import _set_ephemeris_path

        _set_ephemeris_path()

        data: dict[str, list[EphemerisDataPoint]] = {
            planet: [] for planet in self.config.planets
        }

        # Iterate through date range
        current_date = self.config.start_date
        while current_date <= self.config.end_date:
            jd = self._date_to_julian_day(current_date)

            for planet in self.config.planets:
                if planet not in PLANET_IDS:
                    continue

                planet_id = PLANET_IDS[planet]

                try:
                    # Calculate position with speed
                    result = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
                    longitude = result[0][0]
                    speed = result[0][3]  # degrees per day

                    # Apply harmonic compression
                    harmonic_pos = longitude % self.config.harmonic

                    data[planet].append(
                        EphemerisDataPoint(
                            date=current_date,
                            julian_day=jd,
                            longitude=longitude,
                            speed=speed,
                            harmonic_position=harmonic_pos,
                        )
                    )
                except Exception:
                    # Skip points that fail to calculate
                    pass

            current_date += timedelta(days=self.config.days_per_point)

        return data

    def _detect_stations(
        self, data: dict[str, list[EphemerisDataPoint]]
    ) -> dict[str, list[StationPoint]]:
        """
        Detect retrograde and direct station points.

        A station occurs when the planet's speed changes sign
        (positive to negative = retrograde station, negative to positive = direct).

        Args:
            data: Ephemeris data from _generate_data()

        Returns:
            Dictionary mapping planet names to lists of station points.
        """
        stations: dict[str, list[StationPoint]] = {
            planet: [] for planet in self.config.planets
        }

        for planet, points in data.items():
            # Sun and Moon don't go retrograde
            if planet in ("Sun", "Moon"):
                continue

            for i in range(1, len(points)):
                prev_point = points[i - 1]
                curr_point = points[i]

                # Check for sign change in speed
                if prev_point.speed > 0 and curr_point.speed < 0:
                    # Retrograde station
                    stations[planet].append(
                        StationPoint(
                            date=curr_point.date,
                            julian_day=curr_point.julian_day,
                            longitude=curr_point.longitude,
                            harmonic_position=curr_point.harmonic_position,
                            station_type="retrograde",
                        )
                    )
                elif prev_point.speed < 0 and curr_point.speed > 0:
                    # Direct station
                    stations[planet].append(
                        StationPoint(
                            date=curr_point.date,
                            julian_day=curr_point.julian_day,
                            longitude=curr_point.longitude,
                            harmonic_position=curr_point.harmonic_position,
                            station_type="direct",
                        )
                    )

        return stations

    def _detect_aspect_crossings(
        self, data: dict[str, list[EphemerisDataPoint]]
    ) -> list[AspectCrossing]:
        """
        Detect where planet lines cross (aspects in harmonic view).

        In a 90° harmonic:
        - Lines crossing = hard aspect (conjunction, square, or opposition)
        - Determine which by checking actual longitude difference

        Args:
            data: Ephemeris data from _generate_data()

        Returns:
            List of aspect crossings.
        """
        if self.config.harmonic == 360:
            # Full zodiac - crossings are just conjunctions
            return []

        aspects: list[AspectCrossing] = []
        planets = list(data.keys())

        # Check all planet pairs
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i + 1 :]:
                points1 = data[planet1]
                points2 = data[planet2]

                if not points1 or not points2:
                    continue

                # Find crossings by checking when the difference changes sign
                for j in range(1, min(len(points1), len(points2))):
                    prev_diff = (
                        points1[j - 1].harmonic_position
                        - points2[j - 1].harmonic_position
                    )
                    curr_diff = (
                        points1[j].harmonic_position - points2[j].harmonic_position
                    )

                    # Handle wrap-around
                    if abs(prev_diff) > self.config.harmonic / 2:
                        continue
                    if abs(curr_diff) > self.config.harmonic / 2:
                        continue

                    # Sign change indicates crossing
                    if prev_diff * curr_diff < 0 and abs(curr_diff) < 10:
                        # Crossing detected - determine aspect type
                        lon1 = points1[j].longitude
                        lon2 = points2[j].longitude
                        diff = abs(lon1 - lon2)
                        if diff > 180:
                            diff = 360 - diff

                        # Classify aspect
                        if diff < 15 or diff > 345:
                            aspect_type = "☌"  # Conjunction
                        elif 75 < diff < 105:
                            aspect_type = "□"  # Square
                        elif 165 < diff < 195:
                            aspect_type = "☍"  # Opposition
                        else:
                            continue  # Not a clean hard aspect

                        aspects.append(
                            AspectCrossing(
                                date=points1[j].date,
                                harmonic_position=points1[j].harmonic_position,
                                planet1=planet1,
                                planet2=planet2,
                                aspect_type=aspect_type,
                                longitude1=lon1,
                                longitude2=lon2,
                            )
                        )

        return aspects

    def _extract_natal_positions(self) -> list[NatalPosition]:
        """
        Extract natal planet positions from the natal chart.

        Returns:
            List of NatalPosition objects.
        """
        if self._natal_chart is None:
            return []

        positions = []
        # Determine which planets to show from natal chart
        natal_planets = self._natal_planets or self.config.planets

        for pos in self._natal_chart.positions:
            if pos.name in natal_planets:
                harmonic_pos = pos.longitude % self.config.harmonic
                positions.append(
                    NatalPosition(
                        planet=pos.name,
                        longitude=pos.longitude,
                        harmonic_position=harmonic_pos,
                    )
                )

        return positions

    def _detect_transit_to_natal_aspects(
        self,
        data: dict[str, list[EphemerisDataPoint]],
        natal_positions: list[NatalPosition],
    ) -> list[AspectCrossing]:
        """
        Detect when transiting planets cross natal planet positions.

        In a 90° harmonic, a transit line crossing a natal horizontal line
        indicates a hard aspect (conjunction, square, or opposition).

        Args:
            data: Transit ephemeris data
            natal_positions: Natal planet positions

        Returns:
            List of transit-to-natal aspect crossings.
        """
        if self.config.harmonic == 360:
            return []

        aspects: list[AspectCrossing] = []

        for natal in natal_positions:
            natal_y = natal.harmonic_position

            for transit_planet, points in data.items():
                if not points:
                    continue

                # Find when transit line crosses the natal position
                for j in range(1, len(points)):
                    prev_pos = points[j - 1].harmonic_position
                    curr_pos = points[j].harmonic_position

                    # Skip wrap-around points
                    if abs(curr_pos - prev_pos) > self.config.harmonic / 2:
                        continue

                    # Check if the transit crossed the natal line
                    prev_diff = prev_pos - natal_y
                    curr_diff = curr_pos - natal_y

                    # Handle wrap-around for natal position
                    if abs(prev_diff) > self.config.harmonic / 2:
                        if prev_diff > 0:
                            prev_diff -= self.config.harmonic
                        else:
                            prev_diff += self.config.harmonic
                    if abs(curr_diff) > self.config.harmonic / 2:
                        if curr_diff > 0:
                            curr_diff -= self.config.harmonic
                        else:
                            curr_diff += self.config.harmonic

                    # Sign change indicates crossing
                    if prev_diff * curr_diff < 0 and abs(curr_diff) < 10:
                        # Crossing detected - determine aspect type
                        transit_lon = points[j].longitude
                        natal_lon = natal.longitude
                        diff = abs(transit_lon - natal_lon)
                        if diff > 180:
                            diff = 360 - diff

                        # Classify aspect
                        if diff < 15 or diff > 345:
                            aspect_type = "☌"  # Conjunction
                        elif 75 < diff < 105:
                            aspect_type = "□"  # Square
                        elif 165 < diff < 195:
                            aspect_type = "☍"  # Opposition
                        else:
                            continue  # Not a clean hard aspect

                        aspects.append(
                            AspectCrossing(
                                date=points[j].date,
                                harmonic_position=natal_y,  # Use natal position for Y
                                planet1=transit_planet,
                                planet2=natal.planet,
                                aspect_type=aspect_type,
                                longitude1=transit_lon,
                                longitude2=natal_lon,
                                is_transit_to_natal=True,
                            )
                        )

        return aspects

    def _date_to_x(self, d: date) -> float:
        """Convert a date to X coordinate in the plot area."""
        total_days = (self.config.end_date - self.config.start_date).days
        if total_days == 0:
            return self.config.margin_left

        day_offset = (d - self.config.start_date).days
        x_ratio = day_offset / total_days
        return self.config.margin_left + (x_ratio * self.plot_width)

    def _position_to_y(self, harmonic_position: float) -> float:
        """
        Convert a harmonic position to Y coordinate.

        Y increases downward in SVG, but we want 0° at bottom.
        """
        y_ratio = harmonic_position / self.config.harmonic
        # Invert: 0° at bottom, harmonic° at top
        return self.config.margin_top + ((1 - y_ratio) * self.plot_height)

    def _get_planet_color(self, planet: str) -> str:
        """Get the color for a planet line."""
        return get_planet_glyph_color(
            planet,
            PlanetGlyphPalette.SIGN_RULER,
            theme_default_color="#666666",
        )

    def _draw_grid(self, dwg: svgwrite.Drawing) -> None:
        """Draw the background grid."""
        cfg = self.config

        # Horizontal grid lines (position)
        # For 90° harmonic: lines at 0, 10, 20, 30, ... 90
        # Major lines at 0, 30, 60, 90 (sign boundaries)
        step = 5 if cfg.harmonic == 90 else (15 if cfg.harmonic == 45 else 30)
        major_step = 30 if cfg.harmonic >= 90 else 15

        for pos in range(0, cfg.harmonic + 1, step):
            y = self._position_to_y(pos)
            is_major = pos % major_step == 0

            dwg.add(
                dwg.line(
                    start=(cfg.margin_left, y),
                    end=(cfg.width - cfg.margin_right, y),
                    stroke=cfg.grid_color_major if is_major else cfg.grid_color,
                    stroke_width=1.0 if is_major else 0.5,
                )
            )

        # Vertical grid lines (time) - monthly
        current = date(cfg.start_date.year, cfg.start_date.month, 1)
        while current <= cfg.end_date:
            x = self._date_to_x(current)

            # Major line at January (year boundary)
            is_major = current.month == 1

            if x >= cfg.margin_left and x <= cfg.width - cfg.margin_right:
                dwg.add(
                    dwg.line(
                        start=(x, cfg.margin_top),
                        end=(x, cfg.height - cfg.margin_bottom),
                        stroke=cfg.grid_color_major if is_major else cfg.grid_color,
                        stroke_width=1.0 if is_major else 0.5,
                    )
                )

            # Next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

    def _draw_natal_lines(
        self,
        dwg: svgwrite.Drawing,
        natal_positions: list[NatalPosition],
    ) -> None:
        """Draw horizontal lines for natal planet positions (labels drawn separately)."""
        cfg = self.config

        for natal in natal_positions:
            y = self._position_to_y(natal.harmonic_position)
            color = self._get_planet_color(natal.planet)

            # Draw horizontal dashed line across the plot
            dwg.add(
                dwg.line(
                    start=(cfg.margin_left, y),
                    end=(cfg.width - cfg.margin_right, y),
                    stroke=color,
                    stroke_width=1.5,
                    stroke_dasharray="6,4",  # Dashed line
                    opacity=0.7,
                )
            )

    def _draw_axes(self, dwg: svgwrite.Drawing) -> None:
        """Draw the axes and labels."""
        cfg = self.config

        # Y-axis labels (position)
        if cfg.harmonic == 90:
            # Labels every 5° with modality names at major points
            labels = []
            for deg in range(0, 91, 5):
                if deg == 0 or deg == 90:
                    labels.append((deg, "0° Cardinal"))
                elif deg == 30:
                    labels.append((deg, "0° Fixed"))
                elif deg == 60:
                    labels.append((deg, "0° Mutable"))
                else:
                    labels.append((deg, f"{deg % 30}°"))
        elif cfg.harmonic == 45:
            # Labels every 5° for 45° harmonic
            labels = []
            for deg in range(0, 46, 5):
                if deg == 0 or deg == 45:
                    labels.append((deg, "0°"))
                else:
                    labels.append((deg, f"{deg}°"))
        else:  # 360
            labels = [
                (0, "0° ♈"),
                (30, "0° ♉"),
                (60, "0° ♊"),
                (90, "0° ♋"),
                (120, "0° ♌"),
                (150, "0° ♍"),
                (180, "0° ♎"),
                (210, "0° ♏"),
                (240, "0° ♐"),
                (270, "0° ♑"),
                (300, "0° ♒"),
                (330, "0° ♓"),
                (360, "0° ♈"),
            ]

        for pos, label in labels:
            y = self._position_to_y(pos)
            # Use smaller font for intermediate labels
            is_major = (
                (cfg.harmonic == 90 and pos % 30 == 0)
                or (cfg.harmonic == 45 and pos % 15 == 0)
                or cfg.harmonic == 360
            )
            dwg.add(
                dwg.text(
                    label,
                    insert=(cfg.margin_left - 15, y + 4),
                    text_anchor="end",
                    font_size="11px" if is_major else "9px",
                    font_family='"Arial", "Helvetica", sans-serif',
                    fill=cfg.text_color if is_major else "#888888",
                )
            )

        # X-axis labels (time) - months
        current = date(cfg.start_date.year, cfg.start_date.month, 1)
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        while current <= cfg.end_date:
            x = self._date_to_x(current)

            if x >= cfg.margin_left and x <= cfg.width - cfg.margin_right:
                # Month label
                dwg.add(
                    dwg.text(
                        month_names[current.month - 1],
                        insert=(x, cfg.height - cfg.margin_bottom + 20),
                        text_anchor="middle",
                        font_size="10px",
                        font_family="Arial, sans-serif",
                        fill=cfg.text_color,
                    )
                )

                # Year label (only at January or start)
                if current.month == 1 or current == date(
                    cfg.start_date.year, cfg.start_date.month, 1
                ):
                    dwg.add(
                        dwg.text(
                            str(current.year),
                            insert=(x, cfg.height - cfg.margin_bottom + 35),
                            text_anchor="middle",
                            font_size="12px",
                            font_weight="bold",
                            font_family="Arial, sans-serif",
                            fill=cfg.text_color,
                        )
                    )

            # Next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)

    def _draw_planet_line(
        self,
        dwg: svgwrite.Drawing,
        planet: str,
        points: list[EphemerisDataPoint],
    ) -> None:
        """
        Draw the line for a single planet.

        Handles wrap-around at harmonic boundaries by breaking the line.
        """
        if not points:
            return

        color = self._get_planet_color(planet)
        cfg = self.config

        # Build path segments (break at wrap-around points)
        segments: list[list[tuple[float, float]]] = []
        current_segment: list[tuple[float, float]] = []

        prev_pos = None
        for point in points:
            x = self._date_to_x(point.date)
            y = self._position_to_y(point.harmonic_position)

            # Detect wrap-around (position jumps by more than half the harmonic)
            if prev_pos is not None:
                delta = abs(point.harmonic_position - prev_pos)
                if delta > cfg.harmonic / 2:
                    # Wrap-around detected - start new segment
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = []

            current_segment.append((x, y))
            prev_pos = point.harmonic_position

        if current_segment:
            segments.append(current_segment)

        # Draw each segment as a path
        for segment in segments:
            if len(segment) < 2:
                continue

            # Build SVG path
            path_data = f"M {segment[0][0]:.1f} {segment[0][1]:.1f}"
            for x, y in segment[1:]:
                path_data += f" L {x:.1f} {y:.1f}"

            dwg.add(
                dwg.path(
                    d=path_data,
                    stroke=color,
                    stroke_width=cfg.line_width,
                    fill="none",
                    stroke_linecap="round",
                    stroke_linejoin="round",
                )
            )

    def _draw_stations(
        self,
        dwg: svgwrite.Drawing,
        planet: str,
        stations: list[StationPoint],
    ) -> None:
        """Draw station markers for a planet."""
        if not stations:
            return

        color = self._get_planet_color(planet)

        for station in stations:
            x = self._date_to_x(station.date)
            y = self._position_to_y(station.harmonic_position)

            # Draw smaller circle marker (radius 3 instead of 5)
            # Filled for retrograde, hollow for direct
            dwg.add(
                dwg.circle(
                    center=(x, y),
                    r=3,
                    stroke=color,
                    stroke_width=1.5,
                    fill=color if station.station_type == "retrograde" else "none",
                )
            )

    def _draw_aspects(
        self,
        dwg: svgwrite.Drawing,
        aspects: list[AspectCrossing],
    ) -> None:
        """Draw aspect markers at line crossings."""
        for aspect in aspects:
            x = self._date_to_x(aspect.date)
            y = self._position_to_y(aspect.harmonic_position)

            # Draw larger, bolder aspect glyph directly at crossing
            dwg.add(
                dwg.text(
                    aspect.aspect_type,
                    insert=(x, y + 5),  # Centered on the crossing
                    text_anchor="middle",
                    font_size="14px",
                    font_weight="bold",
                    font_family='"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
                    fill="#555555",
                )
            )

    def _draw_planet_glyphs(
        self,
        dwg: svgwrite.Drawing,
        data: dict[str, list[EphemerisDataPoint]],
    ) -> None:
        """
        Draw planet glyphs with degree info.

        If natal chart is provided: transits on left, natal on right.
        Otherwise: transits on both left and right.
        """
        from stellium.visualization.core import PLANET_GLYPHS

        cfg = self.config
        has_natal = self._natal_positions is not None and len(self._natal_positions) > 0

        # Collect transit positions for left side (start of year)
        left_positions: list[
            tuple[float, str, str, float]
        ] = []  # (y, planet, glyph, longitude)

        for planet, points in data.items():
            if not points:
                continue

            glyph = PLANET_GLYPHS.get(planet, planet[:2])
            first_point = points[0]
            y_left = self._position_to_y(first_point.harmonic_position)
            left_positions.append((y_left, planet, glyph, first_point.longitude))

        # Collect right side positions
        if has_natal:
            # Right side shows natal positions
            right_positions: list[
                tuple[float, str, str, float, bool]
            ] = []  # (y, planet, glyph, longitude, is_natal)
            for natal in self._natal_positions:
                glyph = PLANET_GLYPHS.get(natal.planet, natal.planet[:2])
                y = self._position_to_y(natal.harmonic_position)
                right_positions.append((y, natal.planet, glyph, natal.longitude, True))
        else:
            # Right side shows transit end positions
            right_positions = []
            for planet, points in data.items():
                if not points:
                    continue
                glyph = PLANET_GLYPHS.get(planet, planet[:2])
                last_point = points[-1]
                y_right = self._position_to_y(last_point.harmonic_position)
                right_positions.append(
                    (y_right, planet, glyph, last_point.longitude, False)
                )

        # Sort by Y position and offset overlapping glyphs
        min_spacing = 14  # Minimum vertical spacing between glyphs

        def offset_overlapping_4(
            positions: list[tuple[float, str, str, float]],
        ) -> list[tuple[float, str, str, float]]:
            """Offset overlapping glyphs vertically (4-tuple version)."""
            if not positions:
                return positions
            sorted_pos = sorted(positions, key=lambda p: p[0])
            result = [sorted_pos[0]]
            for i in range(1, len(sorted_pos)):
                y, planet, glyph, lon = sorted_pos[i]
                prev_y = result[-1][0]
                if y - prev_y < min_spacing:
                    y = prev_y + min_spacing
                result.append((y, planet, glyph, lon))
            return result

        def offset_overlapping_5(
            positions: list[tuple[float, str, str, float, bool]],
        ) -> list[tuple[float, str, str, float, bool]]:
            """Offset overlapping glyphs vertically (5-tuple version)."""
            if not positions:
                return positions
            sorted_pos = sorted(positions, key=lambda p: p[0])
            result = [sorted_pos[0]]
            for i in range(1, len(sorted_pos)):
                y, planet, glyph, lon, is_natal = sorted_pos[i]
                prev_y = result[-1][0]
                if y - prev_y < min_spacing:
                    y = prev_y + min_spacing
                result.append((y, planet, glyph, lon, is_natal))
            return result

        left_positions = offset_overlapping_4(left_positions)
        right_positions = offset_overlapping_5(right_positions)

        # Draw left side glyphs (transits at start)
        for y, planet, glyph, longitude in left_positions:
            color = self._get_planet_color(planet)
            sign_glyph, degree = _longitude_to_sign_degree(longitude)

            # Degree + sign info (to the left)
            dwg.add(
                dwg.text(
                    f"{degree}°{sign_glyph}",
                    insert=(cfg.margin_left - 45, y + 4),
                    text_anchor="end",
                    font_size="10px",
                    font_family='"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", "Arial", sans-serif',
                    fill=cfg.text_color,
                )
            )
            # Glyph (closer to graph)
            dwg.add(
                dwg.text(
                    glyph,
                    insert=(cfg.margin_left - 8, y + 5),
                    text_anchor="end",
                    font_size="14px",
                    font_family='"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
                    fill=color,
                )
            )

        # Draw right side glyphs
        for y, planet, glyph, longitude, is_natal in right_positions:
            color = self._get_planet_color(planet)
            sign_glyph, degree = _longitude_to_sign_degree(longitude)

            # Glyph (closer to graph) - prefix with 'n' if natal
            glyph_text = f"n{glyph}" if is_natal else glyph
            dwg.add(
                dwg.text(
                    glyph_text,
                    insert=(cfg.width - cfg.margin_right + 8, y + 5),
                    text_anchor="start",
                    font_size="14px" if not is_natal else "12px",
                    font_family='"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", serif',
                    fill=color,
                )
            )
            # Degree + sign info (to the right)
            x_offset = 28 if not is_natal else 35  # More offset for natal "n☉" prefix
            dwg.add(
                dwg.text(
                    f"{degree}°{sign_glyph}",
                    insert=(cfg.width - cfg.margin_right + x_offset, y + 4),
                    text_anchor="start",
                    font_size="10px",
                    font_family='"Symbola", "Noto Sans Symbols", "Apple Symbols", "Segoe UI Symbol", "Arial", sans-serif',
                    fill=cfg.text_color,
                )
            )

    def _draw_legend(self, dwg: svgwrite.Drawing) -> None:
        """Draw legend explaining station symbols."""
        cfg = self.config

        # Position legend at bottom right
        legend_x = cfg.width - cfg.margin_right - 120
        legend_y = cfg.height - 25

        # Retrograde station
        dwg.add(
            dwg.circle(
                center=(legend_x, legend_y),
                r=3,
                stroke="#666666",
                stroke_width=1.5,
                fill="#666666",
            )
        )
        dwg.add(
            dwg.text(
                "Rx Station",
                insert=(legend_x + 10, legend_y + 4),
                font_size="10px",
                font_family="Arial, sans-serif",
                fill=cfg.text_color,
            )
        )

        # Direct station
        dwg.add(
            dwg.circle(
                center=(legend_x + 80, legend_y),
                r=3,
                stroke="#666666",
                stroke_width=1.5,
                fill="none",
            )
        )
        dwg.add(
            dwg.text(
                "Direct Station",
                insert=(legend_x + 90, legend_y + 4),
                font_size="10px",
                font_family="Arial, sans-serif",
                fill=cfg.text_color,
            )
        )

    def _draw_title(self, dwg: svgwrite.Drawing) -> None:
        """Draw the chart title and natal chart info if present."""
        cfg = self.config

        if cfg.title:
            title = cfg.title
        else:
            # Auto-generate title
            year_start = cfg.start_date.year
            year_end = cfg.end_date.year
            if year_start == year_end:
                year_str = str(year_start)
            else:
                year_str = f"{year_start}-{year_end}"

            if self._natal_chart is not None:
                title = f"Transits {year_str} ({cfg.harmonic}° Harmonic)"
            else:
                title = f"Graphic Ephemeris {year_str} ({cfg.harmonic}° Harmonic)"

        # Main title (left-aligned if natal, centered otherwise)
        if self._natal_chart is not None:
            title_x = cfg.margin_left
            title_anchor = "start"
        else:
            title_x = cfg.width / 2
            title_anchor = "middle"

        dwg.add(
            dwg.text(
                title,
                insert=(title_x, 30),
                text_anchor=title_anchor,
                font_size="18px",
                font_weight="bold",
                font_family="Arial, sans-serif",
                fill=cfg.text_color,
            )
        )

        # If natal chart provided, show chart info on right side
        if self._natal_chart is not None:
            info_x = cfg.width - cfg.margin_right

            # Get natal chart info
            name = self._natal_chart.metadata.get("name", "")
            if name:
                dwg.add(
                    dwg.text(
                        f"Natal: {name}",
                        insert=(info_x, 18),
                        text_anchor="end",
                        font_size="12px",
                        font_weight="bold",
                        font_family="Arial, sans-serif",
                        fill=cfg.text_color,
                    )
                )

            # Format datetime
            local_dt = self._natal_chart.datetime.local_datetime
            date_str = local_dt.strftime("%b %d, %Y %H:%M")

            # Get location
            location = self._natal_chart.location
            location_str = (
                location.name
                if location.name
                else f"{location.latitude:.2f}, {location.longitude:.2f}"
            )

            # Draw datetime and location
            dwg.add(
                dwg.text(
                    f"{date_str} · {location_str}",
                    insert=(info_x, 32),
                    text_anchor="end",
                    font_size="10px",
                    font_family="Arial, sans-serif",
                    fill="#666666",
                )
            )

    def draw(self, filename: str = "ephemeris.svg") -> svgwrite.Drawing:
        """
        Render the graphic ephemeris to SVG.

        Args:
            filename: Output filename for the SVG

        Returns:
            The svgwrite.Drawing object (already saved to disk)
        """
        cfg = self.config

        # Generate data if needed
        if self._data is None:
            self._data = self._generate_data()

        if self._stations is None and cfg.show_stations:
            self._stations = self._detect_stations(self._data)

        # Extract natal positions if natal chart provided
        if self._natal_positions is None and self._natal_chart is not None:
            self._natal_positions = self._extract_natal_positions()

        # Detect aspects - either transit-to-transit or transit-to-natal
        if self._aspects is None and cfg.show_aspects and cfg.harmonic in (90, 45):
            if self._natal_positions:
                # Transit-to-natal aspects
                self._aspects = self._detect_transit_to_natal_aspects(
                    self._data, self._natal_positions
                )
            else:
                # Transit-to-transit aspects
                self._aspects = self._detect_aspect_crossings(self._data)

        # Create SVG drawing
        dwg = svgwrite.Drawing(
            filename=filename,
            size=(f"{cfg.width}px", f"{cfg.height}px"),
            viewBox=f"0 0 {cfg.width} {cfg.height}",
        )

        # Background
        dwg.add(
            dwg.rect(
                insert=(0, 0),
                size=(cfg.width, cfg.height),
                fill=cfg.background_color,
            )
        )

        # Draw layers
        if cfg.show_grid:
            self._draw_grid(dwg)

        # Draw natal lines (before transit lines so they appear behind)
        if self._natal_positions:
            self._draw_natal_lines(dwg, self._natal_positions)

        self._draw_axes(dwg)

        # Draw planet lines
        for planet in cfg.planets:
            if planet in self._data:
                self._draw_planet_line(dwg, planet, self._data[planet])

        # Draw stations
        if cfg.show_stations and self._stations:
            for planet in cfg.planets:
                if planet in self._stations:
                    self._draw_stations(dwg, planet, self._stations[planet])

        # Draw aspect markers
        if cfg.show_aspects and self._aspects:
            self._draw_aspects(dwg, self._aspects)

        # Draw glyphs on both sides (only for transits, not natal)
        self._draw_planet_glyphs(dwg, self._data)

        # Legend
        if cfg.show_legend and cfg.show_stations:
            self._draw_legend(dwg)

        # Title
        if cfg.show_title:
            self._draw_title(dwg)

        # Save
        dwg.save()

        return dwg
