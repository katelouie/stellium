"""Bazi (Four Pillars) calculation engine.

This module implements the traditional calculation methods:
- Year Pillar: Based on the Chinese year (starting at Li Chun)
- Month Pillar: Based on solar terms, using the "Five Tigers" (五虎遁) formula
- Day Pillar: Based on the day count from a reference date
- Hour Pillar: Based on the two-hour periods, using "Five Rats" (五鼠遁) formula

Reference date for day pillar: Feb 12, 1900 = Jia Zi day (甲子日)

Implements the ChineseChartEngine protocol.
"""

import datetime as dt

import swisseph as swe

from stellium.chinese.bazi.models import BaZiChart, Pillar
from stellium.chinese.calendar import SolarTermEngine
from stellium.chinese.core import EarthlyBranch, HeavenlyStem
from stellium.utils.time import datetime_to_julian_day

# Reference point: Feb 20, 1900 is a Jia Zi (甲子) day
# Julian Day for Feb 20, 1900 00:00 UT
REFERENCE_JD = 2415070.5  # Feb 20, 1900
REFERENCE_STEM_INDEX = 0  # Jia (甲)
REFERENCE_BRANCH_INDEX = 0  # Zi (子)


# Five Tigers Formula (五虎遁)
# Given the year stem, find the month stem for the first month (Tiger month)
# Then count forward for subsequent months
FIVE_TIGERS = {
    HeavenlyStem.JIA: HeavenlyStem.BING,  # 甲/己年 -> 丙寅月
    HeavenlyStem.JI: HeavenlyStem.BING,
    HeavenlyStem.YI: HeavenlyStem.WU,  # 乙/庚年 -> 戊寅月
    HeavenlyStem.GENG: HeavenlyStem.WU,
    HeavenlyStem.BING: HeavenlyStem.GENG,  # 丙/辛年 -> 庚寅月
    HeavenlyStem.XIN: HeavenlyStem.GENG,
    HeavenlyStem.DING: HeavenlyStem.REN,  # 丁/壬年 -> 壬寅月
    HeavenlyStem.REN: HeavenlyStem.REN,
    HeavenlyStem.WU: HeavenlyStem.JIA,  # 戊/癸年 -> 甲寅月
    HeavenlyStem.GUI: HeavenlyStem.JIA,
}


# Five Rats Formula (五鼠遁)
# Given the day stem, find the hour stem for the first hour (Zi hour, 23:00-01:00)
# Then count forward for subsequent hours
FIVE_RATS = {
    HeavenlyStem.JIA: HeavenlyStem.JIA,  # 甲/己日 -> 甲子时
    HeavenlyStem.JI: HeavenlyStem.JIA,
    HeavenlyStem.YI: HeavenlyStem.BING,  # 乙/庚日 -> 丙子时
    HeavenlyStem.GENG: HeavenlyStem.BING,
    HeavenlyStem.BING: HeavenlyStem.WU,  # 丙/辛日 -> 戊子时
    HeavenlyStem.XIN: HeavenlyStem.WU,
    HeavenlyStem.DING: HeavenlyStem.GENG,  # 丁/壬日 -> 庚子时
    HeavenlyStem.REN: HeavenlyStem.GENG,
    HeavenlyStem.WU: HeavenlyStem.REN,  # 戊/癸日 -> 壬子时
    HeavenlyStem.GUI: HeavenlyStem.REN,
}


def hour_to_branch_index(hour: int, minute: int = 0) -> int:
    """Convert clock hour to Earthly Branch index.

    The Chinese day starts at 23:00 (Zi hour).
    Each branch covers 2 hours:
    - Zi (子): 23:00-00:59
    - Chou (丑): 01:00-02:59
    - Yin (寅): 03:00-04:59
    - etc.

    Args:
        hour: Hour in 24-hour format (0-23)
        minute: Minutes (0-59)

    Returns:
        Branch index 0-11
    """
    # Convert to minutes since midnight
    total_minutes = hour * 60 + minute

    # Zi hour starts at 23:00 (1380 minutes)
    # Adjust so Zi hour = 0
    adjusted = (total_minutes + 60) % 1440  # +60 to shift 23:00 to 0

    # Each branch is 120 minutes (2 hours)
    branch_index = adjusted // 120

    return branch_index


class BaZiEngine:
    """Calculate Bazi (Four Pillars) charts.

    Implements the ChineseChartEngine protocol.

    Example:
        >>> from datetime import datetime
        >>> engine = BaZiEngine(timezone_offset_hours=-8)  # PST
        >>> chart = engine.calculate(datetime(1994, 1, 6, 11, 47))
        >>> print(chart.display())
    """

    def __init__(self, timezone_offset_hours: float = 0.0):
        """Initialize engine.

        Args:
            timezone_offset_hours: Offset from UTC for the birth location.
                                   E.g., +8 for Beijing, -8 for PST.
        """
        self.timezone_offset = timezone_offset_hours

    @property
    def system_name(self) -> str:
        """The name of the system this engine calculates."""
        return "Bazi"

    def calculate(self, birth_datetime: dt.datetime) -> BaZiChart:
        """Calculate the Four Pillars chart for a birth datetime.

        Args:
            birth_datetime: The birth date and time. Should be in local time
                           if timezone_offset was provided, otherwise UTC.

        Returns:
            Complete BaZiChart with all four pillars.
        """
        # Convert to UTC if needed
        if self.timezone_offset != 0:
            utc_dt = birth_datetime - dt.timedelta(hours=self.timezone_offset)
        else:
            utc_dt = birth_datetime

        jd = datetime_to_julian_day(utc_dt)

        # Calculate each pillar
        year_pillar = self._calculate_year_pillar(jd)
        month_pillar = self._calculate_month_pillar(jd, year_pillar.stem)
        day_pillar = self._calculate_day_pillar(jd)
        hour_pillar = self._calculate_hour_pillar(
            birth_datetime.hour,
            birth_datetime.minute,
            day_pillar.stem,
        )

        return BaZiChart(
            year=year_pillar,
            month=month_pillar,
            day=day_pillar,
            hour=hour_pillar,
            birth_datetime=birth_datetime,
        )

    def _calculate_year_pillar(self, jd: float) -> Pillar:
        """Calculate the Year Pillar.

        The Chinese year starts at Li Chun (Start of Spring), not Jan 1.
        The sexagenary cycle starts from 甲子 (Jia Zi) and repeats every 60 years.

        Reference: 1984 was a Jia Zi (甲子) year.
        """
        # Get solar longitude to check if we're before or after Li Chun
        sun_long = SolarTermEngine.get_solar_longitude(jd)

        # Convert JD to Gregorian year
        year, month, day = swe.revjul(jd)[:3]

        # If sun hasn't reached Li Chun (315°) yet in this calendar year,
        # we're still in the previous Chinese year
        if sun_long < 315 and month < 3:  # Before ~Feb 4
            year -= 1

        # 1984 = Jia Zi year (index 0 in the 60-year cycle)
        cycle_position = (year - 1984) % 60

        stem_index = cycle_position % 10
        branch_index = cycle_position % 12

        return Pillar(
            stem=HeavenlyStem.from_index(stem_index),
            branch=EarthlyBranch.from_index(branch_index),
        )

    def _calculate_month_pillar(self, jd: float, year_stem: HeavenlyStem) -> Pillar:
        """Calculate the Month Pillar using the Five Tigers formula.

        Month branches are fixed:
        - Month 1 (Tiger/寅): after Li Chun (~Feb 4)
        - Month 2 (Rabbit/卯): after Jing Zhe (~Mar 6)
        - etc.

        Month stems are determined by the Five Tigers (五虎遁) formula
        based on the year stem.
        """
        # Get the Bazi month index (0 = Tiger, 1 = Rabbit, etc.)
        month_index = SolarTermEngine.get_bazi_month_index(jd)

        # Branch: Tiger (index 2) + month_index
        # Tiger is branch index 2 (YIN)
        branch_index = (2 + month_index) % 12
        branch = EarthlyBranch.from_index(branch_index)

        # Stem: Use Five Tigers formula
        tiger_month_stem = FIVE_TIGERS[year_stem]
        stem_index = (tiger_month_stem.index + month_index) % 10
        stem = HeavenlyStem.from_index(stem_index)

        return Pillar(stem=stem, branch=branch)

    def _calculate_day_pillar(self, jd: float) -> Pillar:
        """Calculate the Day Pillar.

        The day pillar cycles through the 60 Jia Zi combinations continuously.
        Reference: Feb 12, 1900 = Jia Zi day.
        """
        # Days since reference date
        days_diff = int(jd - REFERENCE_JD)

        # Calculate position in the 60-day cycle
        stem_index = (REFERENCE_STEM_INDEX + days_diff) % 10
        branch_index = (REFERENCE_BRANCH_INDEX + days_diff) % 12

        return Pillar(
            stem=HeavenlyStem.from_index(stem_index),
            branch=EarthlyBranch.from_index(branch_index),
        )

    def _calculate_hour_pillar(
        self,
        hour: int,
        minute: int,
        day_stem: HeavenlyStem,
    ) -> Pillar:
        """Calculate the Hour Pillar using the Five Rats formula.

        Hour branches are fixed based on the 2-hour periods.
        Hour stems are determined by the Five Rats (五鼠遁) formula
        based on the day stem.
        """
        # Get branch index from clock time
        branch_index = hour_to_branch_index(hour, minute)
        branch = EarthlyBranch.from_index(branch_index)

        # Stem: Use Five Rats formula
        zi_hour_stem = FIVE_RATS[day_stem]
        stem_index = (zi_hour_stem.index + branch_index) % 10
        stem = HeavenlyStem.from_index(stem_index)

        return Pillar(stem=stem, branch=branch)


# Backwards compatibility alias
BaZiCalculator = BaZiEngine
