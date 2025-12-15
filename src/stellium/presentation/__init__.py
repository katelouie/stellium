"""
Presentation layer for Stellium.

Provides report building and rendering capabilities.

Usage:
    from stellium.presentation import ReportBuilder

    report = (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_overview()
        .with_planet_positions()
        .with_aspects(mode="major")
        .render(format="rich_table")
    )

    print(report)
"""

from stellium.core.protocols import ReportRenderer, ReportSection

from .builder import ReportBuilder
from .renderers import HTMLRenderer, PlainTextRenderer, ProseRenderer, RichTableRenderer

# Import from the new sections package
from .sections import (
    AspectSection,
    ChartOverviewSection,
    MidpointSection,
    PlanetPositionSection,
)

__all__ = [
    # Main API
    "ReportBuilder",
    # Protocols (for custom extensions)
    "ReportSection",
    "ReportRenderer",
    # Built-in sections
    "ChartOverviewSection",
    "PlanetPositionSection",
    "AspectSection",
    "MidpointSection",
    # Renderers
    "RichTableRenderer",
    "PlainTextRenderer",
    "HTMLRenderer",
    "ProseRenderer",
]
