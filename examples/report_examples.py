"""Examples of using the presentation layer."""

import datetime as dt

from stellium.components.midpoints import MidpointCalculator
from stellium.core.builder import ChartBuilder
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.orbs import SimpleOrbEngine
from stellium.presentation import ReportBuilder

# Create a chart
native = Native(dt.datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

chart = (
    ChartBuilder.from_native(native)
    .with_aspects(ModernAspectEngine())
    .with_orbs(SimpleOrbEngine())
    .add_component(MidpointCalculator())
    .calculate()
)

# Example 1: Simple report
simple_report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .render(format="rich_table")
)
print(simple_report)

# Example 2: Comprehensive report
full_report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions(include_speed=True)
    .with_aspects(mode="major", orbs=True)
    .with_midpoints(mode="core")
    .render(format="rich_table")
)
print(full_report)

# Example 3: Save to file
(
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .with_aspects(mode="major")
    .render(file="chart_report.txt", format="plain_table")
)
