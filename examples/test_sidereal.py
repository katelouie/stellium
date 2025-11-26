"""Test sidereal zodiac calculations.

This example demonstrates the new sidereal zodiac support in Stellium,
showing how planetary positions shift between tropical and sidereal systems.
"""

from stellium import ChartBuilder, ReportBuilder
from stellium.core.native import Native
from stellium.engines.houses import WholeSignHouses

# Test with a known date
native = Native("1994-01-06 11:47", "Palo Alto, CA", name="Kate")

print("=" * 80)
print("TROPICAL vs SIDEREAL COMPARISON")
print("=" * 80)
print()

# Calculate tropical chart (default)
print("Calculating TROPICAL chart...")
tropical_chart = (
    ChartBuilder.from_native(native)
    .with_tropical()  # Explicit (but this is the default)
    .with_house_systems([WholeSignHouses()])
    .calculate()
)

# Calculate sidereal chart with Lahiri ayanamsa
print("Calculating SIDEREAL chart (Lahiri)...")
sidereal_chart = (
    ChartBuilder.from_native(native)
    .with_sidereal("lahiri")
    .with_house_systems([WholeSignHouses()])
    .calculate()
)

print()
print("=" * 80)
print("TROPICAL CHART")
print("=" * 80)
print()

# Show tropical report
tropical_report = (
    ReportBuilder()
    .from_chart(tropical_chart)
    .with_chart_overview()
    .with_planet_positions(house_systems="all")
)
tropical_report.render(format="rich_table")

print()
print("=" * 80)
print("SIDEREAL CHART (Lahiri Ayanamsa)")
print("=" * 80)
print()

# Show sidereal report
sidereal_report = (
    ReportBuilder()
    .from_chart(sidereal_chart)
    .with_chart_overview()
    .with_planet_positions(house_systems="all")
)
sidereal_report.render(format="rich_table")

print()
print("=" * 80)
print("POSITION COMPARISON")
print("=" * 80)
print()

# Compare specific positions
sun_tropical = tropical_chart.get_object("Sun")
sun_sidereal = sidereal_chart.get_object("Sun")

moon_tropical = tropical_chart.get_object("Moon")
moon_sidereal = sidereal_chart.get_object("Moon")

# Calculate degrees in sign (longitude % 30)
sun_trop_deg = sun_tropical.longitude % 30
sun_sid_deg = sun_sidereal.longitude % 30
moon_trop_deg = moon_tropical.longitude % 30
moon_sid_deg = moon_sidereal.longitude % 30

print(f"Sun:")
print(f"  Tropical:  {sun_tropical.sign} {sun_trop_deg:.2f}°")
print(f"  Sidereal:  {sun_sidereal.sign} {sun_sid_deg:.2f}°")
print(f"  Difference: {abs(sun_tropical.longitude - sun_sidereal.longitude):.2f}°")
print()

print(f"Moon:")
print(f"  Tropical:  {moon_tropical.sign} {moon_trop_deg:.2f}°")
print(f"  Sidereal:  {moon_sidereal.sign} {moon_sid_deg:.2f}°")
print(f"  Difference: {abs(moon_tropical.longitude - moon_sidereal.longitude):.2f}°")
print()

print(f"Ayanamsa offset: {sidereal_chart.ayanamsa_value:.4f}°")
print()

# Test with different ayanamsa
print("=" * 80)
print("TESTING DIFFERENT AYANAMSA (Fagan-Bradley)")
print("=" * 80)
print()

fagan_bradley_chart = (
    ChartBuilder.from_native(native)
    .with_sidereal("fagan_bradley")
    .with_house_systems([WholeSignHouses()])
    .calculate()
)

sun_fb = fagan_bradley_chart.get_object("Sun")
sun_fb_deg = sun_fb.longitude % 30
print(f"Sun (Fagan-Bradley): {sun_fb.sign} {sun_fb_deg:.2f}°")
print(f"Sun (Lahiri):        {sun_sidereal.sign} {sun_sid_deg:.2f}°")
print(f"Difference between ayanamsas: {abs(sun_fb.longitude - sun_sidereal.longitude):.2f}°")
print()

print("✓ Sidereal calculations working!")
print()
