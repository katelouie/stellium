"""Planetary returns module for Stellium.

This module provides tools for calculating planetary return charts:
- Solar Returns (birthday charts)
- Lunar Returns (~monthly)
- Saturn Returns, Jupiter Returns, etc.

Example:
    >>> from stellium import ChartBuilder
    >>> from stellium.returns import ReturnBuilder
    >>>
    >>> # Create a natal chart
    >>> natal = ChartBuilder.from_notable("Kate Louie").calculate()
    >>>
    >>> # Calculate 2025 Solar Return
    >>> sr_2025 = ReturnBuilder.solar(natal, 2025).calculate()
    >>>
    >>> # Calculate Lunar Return near a specific date
    >>> lr = ReturnBuilder.lunar(natal, near_date="2025-03-15").calculate()
    >>>
    >>> # Calculate first Saturn Return
    >>> saturn_return = ReturnBuilder.planetary(natal, "Saturn", occurrence=1).calculate()
"""

from stellium.returns.builder import ReturnBuilder

__all__ = ["ReturnBuilder"]
