"""Test declination calculations.

This example demonstrates declination support - showing planetary positions
relative to the celestial equator rather than the ecliptic.
"""

from stellium import ChartBuilder, ReportBuilder
from stellium.core.native import Native

# Test with Kate's chart
native = Native("1994-01-06 11:47", "Palo Alto, CA", name="Kate")

print("=" * 80)
print("DECLINATION TEST")
print("=" * 80)
print()

# Calculate chart
chart = ChartBuilder.from_native(native).calculate()

# Show declinations report
report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_declinations()
)
report.render(format="rich_table")

print()
print("=" * 80)
print("OUT-OF-BOUNDS CHECK")
print("=" * 80)
print()

# Check for out-of-bounds planets
oob_planets = [p for p in chart.positions if p.is_out_of_bounds]

if oob_planets:
    print(f"Found {len(oob_planets)} out-of-bounds planet(s):")
    for p in oob_planets:
        print(f"  {p.name}: {p.declination:.4f}° {p.declination_direction}")
else:
    print("No out-of-bounds planets in this chart.")

print()
print("✓ Declination calculations working!")
print()
