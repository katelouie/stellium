"""
File I/O utilities for importing and exporting astrological data.

This module provides parsers for common astrology software file formats,
allowing users to import their existing chart collections into Stellium.

Supported formats:
- AAF (Astrodienst Astrological Format): Export format from astro.com

Example:
    >>> from stellium.io import parse_aaf
    >>> natives = parse_aaf("my_charts.aaf")
    >>> for native in natives:
    ...     chart = ChartBuilder.from_native(native).calculate()
"""

from stellium.io.aaf import parse_aaf

__all__ = [
    "parse_aaf",
]
