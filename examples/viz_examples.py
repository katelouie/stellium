"""
Example Usage for the Starlight Visualization System.

This file demonstrates how to use the high-level drawing functions
and how to manually assemble layers for custom charts.
"""

import datetime as dt
import os
from pathlib import Path

import pytz

from starlight.core.builder import ChartBuilder
from starlight.core.models import CalculatedChart, ObjectType

# --- Core Starlight Imports ---
from starlight.core.native import Native
from starlight.engines.aspects import ModernAspectEngine
from starlight.engines.houses import PlacidusHouses, WholeSignHouses
from starlight.engines.orbs import LuminariesOrbEngine

# --- Advanced Imports (for Custom Charts) ---
from starlight.visualization.core import ChartRenderer, IRenderLayer
from starlight.visualization.layers import (
    AngleLayer,
    AspectLayer,
    HouseCuspLayer,
    PlanetLayer,
    ZodiacLayer,
)

# --- Output Directory ---
# Get the directory *this* script is in
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "chart_examples"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_sample_chart(multi_house: bool = False) -> CalculatedChart:
    """Helper to create a standard chart for our examples."""

    # 1. Create the Native object
    native = Native(
        datetime_input=dt.datetime(
            1994, 1, 6, 11, 47, tzinfo=pytz.timezone("America/Los_Angeles")
        ),
        location_input="San Francisco, CA",
    )

    # 2. Build the chart
    builder = (
        ChartBuilder.from_native(native)
        .with_aspects(ModernAspectEngine())
        .with_orbs(LuminariesOrbEngine())
    )  # Use a slightly different orb engine

    if multi_house:
        builder.with_house_systems([PlacidusHouses(), WholeSignHouses()])
    else:
        builder.with_house_systems([PlacidusHouses()])

    return builder.calculate()


def example_1_standard_natal_chart():
    """
    Draws a standard natal chart using the simplest high-level function.
    """
    print("Running Example 1: Standard Natal Chart...")
    chart = create_sample_chart(multi_house=False)

    output_path = os.path.join(OUTPUT_DIR, "example_1_natal_chart.svg")

    chart.draw(output_path).with_size(800).save()

    print(f"✅ Success! Chart saved to {output_path}\n")


def example_2_multi_house_chart():
    """
    Draws a chart showing two house systems overlaid, using the
    fluent builder API.
    """
    print("Running Example 2: Multi-House Chart...")
    chart = create_sample_chart(multi_house=True)

    output_path = os.path.join(OUTPUT_DIR, "example_2_multi_house.svg")

    chart.draw(output_path).with_size(800).with_house_systems("all").save()

    print(f"✅ Success! Chart saved to {output_path}\n")


def example_3_advanced_synastry_chart():
    """
    Demonstrates the power of the layer system by manually
    assembling a synastry (bi-wheel) chart.

    This shows the "extensibility" you were aiming for.
    """
    print("Running Example 3: Advanced Synastry Chart...")

    # 1. Create two natives and two charts
    native1 = Native(
        dt.datetime(1990, 5, 20, 14, 30, tzinfo=pytz.timezone("Europe/London")),
        "London, UK",
    )
    chart1 = (
        ChartBuilder.from_native(native1)
        .with_aspects(ModernAspectEngine())
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )

    native2 = Native(
        dt.datetime(1992, 11, 10, 6, 15, tzinfo=pytz.timezone("America/New_York")),
        "New York, NY",
    )
    chart2 = (
        ChartBuilder.from_native(native2).with_aspects(ModernAspectEngine()).calculate()
    )  # No houses needed for inner wheel

    # 2. Create the renderer and SVG object
    output_path = os.path.join(OUTPUT_DIR, "example_3_synastry_chart.svg")

    rotation = chart1.get_object("ASC").longitude or 0.0
    renderer = ChartRenderer(size=800, rotation=rotation)
    dwg = renderer.create_svg_drawing(output_path)

    # 3. Get planet sets (includes nodes and points)
    planets1 = [
        p
        for p in chart1.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]
    planets2 = [
        p
        for p in chart2.positions
        if p.object_type
        in (ObjectType.PLANET, ObjectType.ASTEROID, ObjectType.NODE, ObjectType.POINT)
    ]

    # 4. Manually assemble the layers
    # We use chart1 for the "frame" (houses, zodiac, angles)
    layers: list[IRenderLayer] = [
        # Outer frame
        ZodiacLayer(),
        HouseCuspLayer(house_system_name=chart1.default_house_system),
        AngleLayer(),
        # Aspects between the two charts (synastry aspects)
        # Note: We'd need a synastry calculator for this.
        # For now, we'll just draw aspects from chart 1.
        AspectLayer(),
        # --- The Synastry "Bi-Wheel" ---
        # Draw Chart 1's planets on the main (outer) ring
        PlanetLayer(planet_set=planets1, radius_key="synastry_planet_ring_outer"),
        # Draw Chart 2's planets on the inner synastry ring
        PlanetLayer(
            planet_set=planets2,
            radius_key="synastry_planet_ring_inner",
            style_override={
                "glyph_color": "#0066CC",  # Make inner planets blue
                "glyph_size": "20px",
                "info_color": "#0066CC",
                "info_size": "9px",
            },
        ),
    ]

    # 5. Render all layers
    for layer in layers:
        layer.render(renderer, dwg, chart1)  # Use chart1 as the base

    # 6. Save the final image
    dwg.save()
    print(f"✅ Success! Synastry chart saved to {output_path}\n")


if __name__ == "__main__":
    example_1_standard_natal_chart()
    example_2_multi_house_chart()
    example_3_advanced_synastry_chart()
