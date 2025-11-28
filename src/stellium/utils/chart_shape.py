"""
Chart shape detection utilities.

Identifies the overall pattern/distribution of planets in a chart.
Classic chart shapes include: Bundle, Bowl, Bucket, Locomotive, Seesaw, Splay, and Splash.
"""

from typing import Literal

from stellium.core.models import CalculatedChart, CelestialPosition, ObjectType

ChartShape = Literal[
    "Bundle",
    "Bowl",
    "Bucket",
    "Locomotive",
    "Seesaw",
    "Splay",
    "Splash",
]


def detect_chart_shape(chart: CalculatedChart) -> tuple[ChartShape, dict]:
    """
    Detect the overall shape/pattern of planets in a chart.

    Args:
        chart: Calculated chart

    Returns:
        Tuple of (shape_name, metadata_dict) where metadata contains
        additional info like span, leading planet, handle planet, etc.
    """
    # Get only planets for shape detection (not angles, asteroids, or points)
    planets = [
        p
        for p in chart.positions
        if p.object_type == ObjectType.PLANET and p.name != "Earth"
    ]

    if len(planets) < 3:
        return "Splash", {}  # Not enough planets to determine shape

    # Sort planets by longitude
    sorted_planets = sorted(planets, key=lambda p: p.longitude)

    # Calculate gaps between consecutive planets
    gaps = []
    for i in range(len(sorted_planets)):
        current = sorted_planets[i]
        next_planet = sorted_planets[(i + 1) % len(sorted_planets)]

        # Calculate gap (handling 360° wrap)
        gap = (next_planet.longitude - current.longitude) % 360
        gaps.append(
            {
                "from": current,
                "to": next_planet,
                "degrees": gap,
            }
        )

    # Calculate total span (from first to last planet in sorted order)
    span = _calculate_span(sorted_planets)
    largest_gap = max(gaps, key=lambda g: g["degrees"])

    # Detection logic (order matters!)

    # 1. Bundle: All planets within 120°
    if span <= 120:
        return "Bundle", {
            "span": span,
            "leading_planet": sorted_planets[0].name,
        }

    # 2. Bowl: All planets within 180° (half the chart)
    if span <= 180:
        return "Bowl", {
            "span": span,
            "leading_planet": sorted_planets[0].name,
            "rim_start": sorted_planets[0].name,
            "rim_end": sorted_planets[-1].name,
        }

    # 3. Bucket: Bowl + one isolated planet as "handle"
    # Check if largest gap is > 180° and there's one planet isolated
    if largest_gap["degrees"] > 180:
        # Check if the remaining planets form a bowl
        remaining_planets = [p for p in sorted_planets if p != largest_gap["from"]]
        if len(remaining_planets) >= 2:
            remaining_span = _calculate_span(remaining_planets)
            if remaining_span <= 180:
                return "Bucket", {
                    "span": remaining_span,
                    "handle": largest_gap["from"].name,
                    "rim_start": remaining_planets[0].name,
                    "rim_end": remaining_planets[-1].name,
                }

    # 4. Locomotive: Planets in 240° with 120° gap
    if 210 <= span <= 270 and largest_gap["degrees"] >= 100:
        return "Locomotive", {
            "span": span,
            "gap": largest_gap["degrees"],
            "leading_planet": sorted_planets[0].name,
        }

    # 5. Seesaw: Two opposing groups with large gap between them
    # Look for two significant gaps (> 60°)
    significant_gaps = [g for g in gaps if g["degrees"] > 60]
    if len(significant_gaps) >= 2:
        # Check if gaps are roughly opposite each other
        gap1, gap2 = significant_gaps[0], significant_gaps[1]
        gap_separation = abs(gap1["degrees"] - gap2["degrees"])

        if gap_separation < 60:  # Gaps are similar size
            return "Seesaw", {
                "gap1": gap1["degrees"],
                "gap2": gap2["degrees"],
                "group1_start": gap1["to"].name,
                "group2_start": gap2["to"].name,
            }

    # 6. Splay: Irregular distribution with multiple gaps
    # At least 3 gaps of 60°+
    large_gaps = [g for g in gaps if g["degrees"] >= 60]
    if len(large_gaps) >= 3:
        return "Splay", {
            "num_gaps": len(large_gaps),
            "irregular": True,
        }

    # 7. Splash: Default - planets evenly distributed
    # No clear pattern detected
    return "Splash", {
        "span": span,
        "largest_gap": largest_gap["degrees"],
        "distribution": "even",
    }


def _calculate_span(planets: list[CelestialPosition]) -> float:
    """
    Calculate the total span of planets in degrees.

    Args:
        planets: List of planets (should be sorted by longitude)

    Returns:
        Span in degrees (0-360)
    """
    if len(planets) < 2:
        return 0.0

    # Already sorted, so first and last define the span
    first = planets[0].longitude
    last = planets[-1].longitude

    # Calculate span (handling 360° wrap)
    span = (last - first) % 360

    return span


def get_chart_shape_description(shape: ChartShape, metadata: dict) -> str:
    """
    Get a human-readable description of a chart shape.

    Args:
        shape: Chart shape name
        metadata: Metadata dict from detect_chart_shape()

    Returns:
        Description string
    """
    descriptions = {
        "Bundle": "Focused energy, concentrated in one area",
        "Bowl": "Self-contained, purposeful direction",
        "Bucket": "Bowl with singular focus point",
        "Locomotive": "Dynamic, driven, constant motion",
        "Seesaw": "Balanced opposites, see-saw energy",
        "Splay": "Individualistic, strong-willed",
        "Splash": "Well-rounded, versatile",
    }

    base_desc = descriptions.get(shape, "")

    # Add metadata details
    if shape == "Bundle" and "span" in metadata:
        return f"{base_desc} ({metadata['span']:.0f}° span)"
    elif shape == "Bucket" and "handle" in metadata:
        return f"{base_desc} (handle: {metadata['handle']})"
    elif shape == "Locomotive" and "gap" in metadata:
        return f"{base_desc} ({metadata['gap']:.0f}° gap)"

    return base_desc
