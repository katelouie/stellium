"""
Protocol definitions for Stellium components.

Protocols define INTERFACES - what methods a component must implement.
They don't provide implementation - that's in the engine classes.

Think of these as contracts: "If you want to be an EphemerisEngine,
you must implement these methods with these signatures."
"""

from typing import TYPE_CHECKING, Any, Protocol

from stellium.core.models import (
    Aspect,
    CalculatedChart,
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
)

if TYPE_CHECKING:
    from stellium.core.config import CalculationConfig
    from stellium.visualization.builder import ChartDrawBuilder


# Type alias for any chart-like object
ChartType = "CalculatedChart | Comparison | MultiChart"


class EphemerisEngine(Protocol):
    """
    Protocol for planetary position calculation engines.

    Different implementations might use:
    - Swiss Ephemeris
    - JPL Ephemeris
    - Custom calculation algorithms
    - Mock data for testing
    """

    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
        config: "CalculationConfig | None" = None,
    ) -> list[CelestialPosition]:
        """
        Calculate positions for celestial objects.

        Args:
            datetime: When to calculate positions
            location: Where to calculate from (for topocentric)
            objects: Which objects to calculate (None = all standard objects)
            config: Optional calculation configuration (zodiac type, etc.)

        Returns:
            List of CelestialPosition objects
        """
        ...


class HouseSystemEngine(Protocol):
    """
    Protocol for house system calculation engines.

    Different implementations for different house systems:
    - Whole Sign
    - Placidus
    - Koch
    - Equal House
    - etc
    """

    @property
    def system_name(self) -> str:
        """Name of this house system (e.g. Placidus)"""
        ...

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> tuple[HouseCusps, list[CelestialPosition]]:
        """
        Calculate house cusps for this system.

        Args:
            datetime: Chart datetime
            location: Chart location

        Returns:
            Tuple containing:
            1. HouseCusps object with 12 cusp positions (For this specific system)
            2. A List of CelestialPosition objects for the primary angles
               (ASC, MC, DSC, IC, Vertex)
        """
        ...

    def assign_houses(
        self, positions: list[CelestialPosition], cusps: HouseCusps
    ) -> dict[str, int]:
        """
        Assign house numbers to celestial positions.

        Args:
            positions: Celestial objects to assign houses
            cusps: House cusps to use for assignment

        Returns:
            A dictionary of {object_name: house_number}
        """
        ...


class OrbEngine(Protocol):
    """
    Protocol for orb calculation.

    Encapsulates logic for determining orb allowance, which can be simple (by aspect)
    or complex (by planet, by planet pair, by day/night, etc.).
    """

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """
        Get the allowed orb for a specific aspect between two objects.

        Args:
            obj1: The first celestial object
            obj2: The second celestial object
            aspect_name: The name of the aspect (e.g. Square)

        Returns:
            The maximum allowed orb in degrees
        """
        ...


class CrossChartAspectEngine(Protocol):
    """
    Protocol for calculating aspects between two charts.

    This is separate from AspectEngine to allow different
    orb configurations and aspect sets for cross-chart work.
    """


class AspectEngine(Protocol):
    """
    Protocol for aspect calculation engines.

    Different implementations might use:
    - Traditional aspects (Ptolemaic)
    - Modern aspects (including minor aspects)
    - Harmonic aspects
    - Vedic aspects (completely different system)
    """

    def calculate_aspects(
        self,
        positions: list[CelestialPosition],
        orb_engine: OrbEngine,
    ) -> list[Aspect]:
        """
        Calculate aspects between celestial objects.

        Args:
            positions: Objects to find aspects between
            orb_engine: Optional custom orb settings

        Returns:
            List of Aspect objects
        """
        ...


class DignityCalculator(Protocol):
    """
    Protocol for dignity/debility calculation.

    Different implementations:
    - Traditional essential dignities
    - Modern rulerships
    - Vedic dignity system
    """

    def calculate_dignities(self, position: CelestialPosition) -> dict[str, Any]:
        """
        Calculate dignities for a celestial position.

        Args:
            position: Position to calculate dignities for

        Returns:
            Dictionary with dignity information
        """
        ...


class ChartComponent(Protocol):
    """
    Base protocol for chart calculation components.

    Components can be:
    - Arabic part calculators
    - Midpoint finders
    - Pattern detectors (grand trine, T-square, etc.)
    - Fixed star calculators
    - Harmonic charts
    """

    metadata_name = ""

    @property
    def component_name(self) -> str:
        """Name of this component."""
        ...

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate additional chart objects.

        Args:
            datetime: Chart datetime
            location: Chart location
            positions: Already calculated positions
            house_systems_map: House cusps by system
            house_placements_map: House placements by system then planet

        Returns:
            List of additional CelestialPosition objects
        """
        ...


class ChartLike(Protocol):
    """
    Protocol for chart-like objects (single or multi-chart).

    This protocol defines the common interface that all chart types should support,
    enabling code to work with CalculatedChart, MultiChart, or Comparison objects
    interchangeably where appropriate.

    Note: The `chart` parameter in methods like `get_object()` defaults to 0,
    which works for single charts (ignored) and multi-charts (returns from first chart).
    """

    @property
    def datetime(self) -> ChartDateTime:
        """The primary datetime of the chart (or first chart for multi-charts)."""
        ...

    @property
    def location(self) -> ChartLocation:
        """The primary location of the chart (or first chart for multi-charts)."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Chart metadata dictionary."""
        ...

    def get_object(self, name: str, chart: int = 0) -> CelestialPosition | None:
        """
        Get a celestial object by name.

        Args:
            name: Name of the object (e.g., "Sun", "Moon")
            chart: For multi-charts, which chart to query (0-indexed). Ignored for single charts.

        Returns:
            The CelestialPosition if found, None otherwise
        """
        ...

    def get_planets(self, chart: int = 0) -> list[CelestialPosition]:
        """
        Get all planetary positions.

        Args:
            chart: For multi-charts, which chart to query (0-indexed). Ignored for single charts.

        Returns:
            List of planet CelestialPosition objects
        """
        ...

    def draw(self, filename: str = "chart.svg") -> "ChartDrawBuilder":
        """
        Create a visualization builder for this chart.

        Args:
            filename: Default filename for saving

        Returns:
            ChartDrawBuilder configured for this chart
        """
        ...


class ReportSection(Protocol):
    """
    Protocol for report sections.

    Each section knows how to extract data from a chart (single or multi-chart)
    and format it into a standardized structure that renderers can consume.

    **Multi-Chart Support:**
    Sections may receive any of:
    - CalculatedChart: Single natal/event chart
    - Comparison: Two-chart comparison (deprecated, use MultiChart)
    - MultiChart: 2-4 charts for synastry, transits, progressions, etc.

    Implementations should use `stellium.core.chart_utils` helpers to handle
    different chart types consistently:
    - `get_all_charts(chart)` - Get list of all charts
    - `get_chart_labels(chart)` - Get labels for each chart
    - `chart_count(chart)` - Get number of charts

    Why a protocol?
    - Extensibility: Users can create custom sections
    - Type safety: MyPy/Pyright can verify implementations
    - No inheritance required: Keep components lightweight
    """

    @property
    def section_name(self) -> str:
        """
        Human-readable name for this section.

        Used as a header in rendered output.
        """
        ...

    def generate_data(self, chart: ChartType) -> dict[str, Any]:
        """
        Extract and structure data from the chart.

        Returns a standardized dictionary format that renderers understand::

            {
                "type": "table" | "text" | "key_value" | "side_by_side_tables" | "grouped_tables",
                "headers": [...],      # For tables
                "rows": [...],         # For tables
                "text": "...",         # For text blocks
                "data": {...},         # For key-value pairs
                "tables": [...],       # For side_by_side_tables or grouped_tables
            }

        Args:
            chart: The chart to extract data from (may be single or multi-chart)

        Returns:
            Structured data dictionary
        """
        ...


class ReportRenderer(Protocol):
    """
    Protocol for output renderers.

    Renderers take structured section data and format it for a specific
    output medium (terminal, plain text, HTML, etc.).

    Why separate renderers?
    - Same data, multiple output formats
    - Easy to add new formats without touching section code
    - Testable in isolation
    """

    def render_section(self, section_name: str, section_data: dict[str, Any]) -> str:
        """
        Render a single section.

        Args:
            section_name: Header for the section
            section_data: Structured data from section.generate_data()

        Returns:
            Formatted string for this section
        """
        ...

    def render_report(self, sections: list[tuple[str, dict[str, Any]]]) -> str:
        """
        Render a complete report with multiple sections.

        Args:
            sections: List of (section_name, section_data) tuples

        Returns:
            Complete formatted report
        """
        ...


class ChartAnalyzer(Protocol):
    """
    Protocol for chart analysis components.

    Analyzers examine a calculated chart and return findings.
    """

    @property
    def analyzer_name(self) -> str:
        """Name of this analyzer."""
        ...

    @property
    def metadata_name(self) -> str:
        """Name that the metadata should be store under"""
        ...

    def analyze(self, chart: CalculatedChart) -> list | dict:
        """
        Analyze the chart.

        Args:
            chart: Chart to analyze

        Returns:
            Dict of findings (type depends on analyzer)
        """
        ...
