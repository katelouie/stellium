"""Chinese astrology systems for Stellium.

This module provides implementations of various Chinese astrology systems:
- Bazi (Four Pillars / 八字) - implemented
- Zi Wei Dou Shu (Purple Star / 紫微斗數) - planned

Core primitives (stems, branches, elements) are shared across all systems.
All chart types implement the ChineseChart protocol for interoperability.

Example:
    >>> from stellium.chinese import BaZiEngine
    >>> from datetime import datetime
    >>>
    >>> engine = BaZiEngine(timezone_offset_hours=8)  # Beijing time
    >>> chart = engine.calculate(datetime(1990, 5, 15, 10, 30))
    >>> print(chart.display())
"""

# Core primitives (shared across all Chinese astrology systems)
# Bazi (Four Pillars)
from stellium.chinese.bazi import (
    BaZiCalculator,  # Backwards compatibility
    BaZiChart,
    BaZiEngine,
    Pillar,
    # Analysis
    TenGod,
    TenGodRelation,
    analyze_ten_gods,
    calculate_ten_god,
)

# Calendar utilities
from stellium.chinese.calendar import (
    SolarTerm,
    SolarTermEngine,
    SolarTermEvent,
)
from stellium.chinese.core import (
    EarthlyBranch,
    Element,
    HeavenlyStem,
    Polarity,
)

# Protocols (interfaces)
from stellium.chinese.protocols import (
    ChineseChart,
    ChineseChartEngine,
    ChineseChartRenderer,
)

__all__ = [
    # Core
    "Element",
    "Polarity",
    "HeavenlyStem",
    "EarthlyBranch",
    # Protocols
    "ChineseChart",
    "ChineseChartEngine",
    "ChineseChartRenderer",
    # Calendar
    "SolarTerm",
    "SolarTermEngine",
    "SolarTermEvent",
    # Bazi
    "BaZiEngine",
    "BaZiCalculator",
    "BaZiChart",
    "Pillar",
    # Bazi Analysis
    "TenGod",
    "TenGodRelation",
    "analyze_ten_gods",
    "calculate_ten_god",
]
