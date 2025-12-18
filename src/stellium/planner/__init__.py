"""
Stellium Planner - Generate beautiful astrological planners as PDFs.

This module creates personalized 12-month planners with:
- Front matter: natal chart, progressed chart, solar return, profections, ZR timeline, graphic ephemeris
- Daily pages: transit listings with times, Moon phases, VOC periods, ingresses

Example:
    >>> from stellium import Native
    >>> from stellium.planner import PlannerBuilder
    >>>
    >>> native = Native("1990-05-15 14:30", "San Francisco, CA")
    >>> planner = (PlannerBuilder.for_native(native)
    ...     .year(2025)
    ...     .timezone("America/Los_Angeles")
    ...     .with_natal_chart()
    ...     .with_progressed_chart()
    ...     .with_solar_return()
    ...     .with_profections()
    ...     .with_zr_timeline()
    ...     .with_graphic_ephemeris()
    ...     .include_natal_transits()
    ...     .include_mundane_transits()
    ...     .include_moon_phases()
    ...     .include_voc()
    ...     .generate("my_planner_2025.pdf"))
"""

from stellium.planner.builder import PlannerBuilder

__all__ = [
    "PlannerBuilder",
]
