"""Bazi (Four Pillars / 八字) astrology system.

Bazi, also known as Four Pillars of Destiny, is a Chinese astrological system
that uses the year, month, day, and hour of birth to create a chart of eight
characters (four pairs of Heavenly Stem + Earthly Branch).

Example:
    >>> from stellium.chinese.bazi import BaZiEngine
    >>> from datetime import datetime
    >>>
    >>> engine = BaZiEngine(timezone_offset_hours=-8)  # PST
    >>> chart = engine.calculate(datetime(1994, 1, 6, 11, 47))
    >>>
    >>> print(chart.hanzi)  # The eight characters
    >>> print(chart.day_master)  # The Day Master (self)
    >>> print(chart.display())  # Formatted table
    >>> print(chart.display_detailed())  # With hidden stems and Ten Gods
"""

from stellium.chinese.bazi.analysis import (
    TenGod,
    TenGodRelation,
    analyze_ten_gods,
    calculate_ten_god,
    count_ten_god_categories,
    count_ten_gods,
)
from stellium.chinese.bazi.engine import BaZiCalculator, BaZiEngine
from stellium.chinese.bazi.models import BaZiChart, Pillar
from stellium.chinese.bazi.renderers import (
    BaziProseRenderer,
    BaziRichRenderer,
    BaziSVGRenderer,
)

__all__ = [
    # Engine
    "BaZiEngine",
    "BaZiCalculator",  # Backwards compatibility alias
    # Models
    "BaZiChart",
    "Pillar",
    # Analysis
    "TenGod",
    "TenGodRelation",
    "analyze_ten_gods",
    "calculate_ten_god",
    "count_ten_gods",
    "count_ten_god_categories",
    # Renderers
    "BaziRichRenderer",
    "BaziProseRenderer",
    "BaziSVGRenderer",
]
