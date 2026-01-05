"""Protocols (interfaces) for Chinese astrology systems.

These define the common operations that all Chinese chart types should support,
enabling polymorphic handling while allowing each system its unique structure.
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from stellium.chinese.core import Element


@runtime_checkable
class ChineseChart(Protocol):
    """Protocol for all Chinese astrology chart types.

    This defines the minimum interface that Bazi, Zi Wei, Qi Men, etc.
    should all implement, enabling shared visualization and export logic.
    """

    @property
    def system_name(self) -> str:
        """The name of the system (e.g., 'Bazi', 'Zi Wei Dou Shu')."""
        ...

    @property
    def birth_datetime(self) -> datetime:
        """The birth/event datetime used to calculate this chart."""
        ...

    def element_counts(self) -> dict[Element, int]:
        """Count of each element in the chart."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Export chart data as a dictionary (for JSON serialization)."""
        ...

    def display(self) -> str:
        """Human-readable text representation of the chart."""
        ...


@runtime_checkable
class ChineseChartEngine(Protocol):
    """Protocol for Chinese chart calculation engines.

    Mirrors the pattern from Western astrology engines.
    """

    @property
    def system_name(self) -> str:
        """The name of the system this engine calculates."""
        ...

    def calculate(self, birth_datetime: datetime) -> ChineseChart:
        """Calculate a chart for the given datetime."""
        ...


@runtime_checkable
class ChineseChartRenderer(Protocol):
    """Protocol for rendering Chinese charts to visual formats.

    Each system (Bazi, Zi Wei, etc.) will have its own renderer
    due to their vastly different visual structures.
    """

    def render_svg(self, chart: ChineseChart, **options: Any) -> str:
        """Render the chart as an SVG string."""
        ...

    def render_text(self, chart: ChineseChart, **options: Any) -> str:
        """Render the chart as formatted text."""
        ...
