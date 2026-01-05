"""Chinese calendar calculations: solar terms, lunar calendar conversions.

This module handles the astronomical calculations needed for Chinese astrology:
- Solar terms (Jie Qi / 节气) for Bazi month determination
- Lunar calendar conversions (future)

Solar terms are based on the Sun's ecliptic longitude:
- Li Chun (立春, Start of Spring) = 315°
- Each of the 24 terms is 15° apart
- The 12 "major" terms (Zhong Qi) mark Bazi month boundaries
"""

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Literal

import swisseph as swe

from stellium.engines.search import find_longitude_crossing
from stellium.utils.time import julian_day_to_datetime


class SolarTerm(Enum):
    """The 24 Solar Terms (Jie Qi / 节气).

    Values are (index, solar_longitude, chinese_name, english_name).
    Index 0 = Li Chun (Start of Spring) at 315°.
    """

    LI_CHUN = (0, 315, "立春", "Start of Spring")
    YU_SHUI = (1, 330, "雨水", "Rain Water")
    JING_ZHE = (2, 345, "惊蛰", "Awakening of Insects")
    CHUN_FEN = (3, 0, "春分", "Spring Equinox")
    QING_MING = (4, 15, "清明", "Clear and Bright")
    GU_YU = (5, 30, "谷雨", "Grain Rain")
    LI_XIA = (6, 45, "立夏", "Start of Summer")
    XIAO_MAN = (7, 60, "小满", "Grain Buds")
    MANG_ZHONG = (8, 75, "芒种", "Grain in Ear")
    XIA_ZHI = (9, 90, "夏至", "Summer Solstice")
    XIAO_SHU = (10, 105, "小暑", "Minor Heat")
    DA_SHU = (11, 120, "大暑", "Major Heat")
    LI_QIU = (12, 135, "立秋", "Start of Autumn")
    CHU_SHU = (13, 150, "处暑", "End of Heat")
    BAI_LU = (14, 165, "白露", "White Dew")
    QIU_FEN = (15, 180, "秋分", "Autumn Equinox")
    HAN_LU = (16, 195, "寒露", "Cold Dew")
    SHUANG_JIANG = (17, 210, "霜降", "Frost's Descent")
    LI_DONG = (18, 225, "立冬", "Start of Winter")
    XIAO_XUE = (19, 240, "小雪", "Minor Snow")
    DA_XUE = (20, 255, "大雪", "Major Snow")
    DONG_ZHI = (21, 270, "冬至", "Winter Solstice")
    XIAO_HAN = (22, 285, "小寒", "Minor Cold")
    DA_HAN = (23, 300, "大寒", "Major Cold")

    def __init__(self, index: int, longitude: float, hanzi: str, english: str):
        self._index = index
        self.longitude = longitude
        self.hanzi = hanzi
        self.english = english

    @property
    def is_major_term(self) -> bool:
        """Major terms (Jie) mark Bazi month boundaries. They're the odd-indexed terms."""
        # Li Chun (0), Jing Zhe (2), Qing Ming (4), etc.
        return self._index % 2 == 0

    @classmethod
    def from_longitude(cls, longitude: float) -> "SolarTerm":
        """Get the solar term for a given solar longitude."""
        # Normalize longitude
        longitude = longitude % 360

        # Find which term this longitude falls under
        for term in cls:
            term_start = term.longitude
            term_end = (term.longitude + 15) % 360

            # Handle wrap-around at 0°
            if term_start > term_end:  # Wraps around 360°
                if longitude >= term_start or longitude < term_end:
                    return term
            else:
                if term_start <= longitude < term_end:
                    return term

        return cls.DA_HAN  # Fallback


# Mapping of solar terms to Bazi months (only major terms / Jie)
# Month 1 (Tiger) starts at Li Chun (315°)
BAZI_MONTH_TERMS = {
    SolarTerm.LI_CHUN: 0,  # Month 1 - Tiger (寅)
    SolarTerm.JING_ZHE: 1,  # Month 2 - Rabbit (卯)
    SolarTerm.QING_MING: 2,  # Month 3 - Dragon (辰)
    SolarTerm.LI_XIA: 3,  # Month 4 - Snake (巳)
    SolarTerm.MANG_ZHONG: 4,  # Month 5 - Horse (午)
    SolarTerm.XIAO_SHU: 5,  # Month 6 - Goat (未)
    SolarTerm.LI_QIU: 6,  # Month 7 - Monkey (申)
    SolarTerm.BAI_LU: 7,  # Month 8 - Rooster (酉)
    SolarTerm.HAN_LU: 8,  # Month 9 - Dog (戌)
    SolarTerm.LI_DONG: 9,  # Month 10 - Pig (亥)
    SolarTerm.DA_XUE: 10,  # Month 11 - Rat (子)
    SolarTerm.XIAO_HAN: 11,  # Month 12 - Ox (丑)
}


@dataclass(frozen=True)
class SolarTermEvent:
    """A solar term occurrence at a specific moment in time."""

    term: SolarTerm
    datetime_utc: dt.datetime
    julian_day: float


class SolarTermEngine:
    """Calculates solar terms (Jie Qi) for Chinese calendar systems."""

    # Li Chun (Start of Spring) is ALWAYS 315 degrees tropical longitude
    LI_CHUN_DEGREE = 315.0

    @staticmethod
    def get_solar_longitude(jd: float) -> float:
        """Returns the Sun's tropical longitude for a given Julian Day."""
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        result = swe.calc_ut(jd, swe.SUN, flags)
        return result[0][0]  # Longitude

    @classmethod
    def get_current_term(cls, jd: float) -> SolarTerm:
        """Get the solar term that's currently active at this Julian Day."""
        sun_long = cls.get_solar_longitude(jd)
        return SolarTerm.from_longitude(sun_long)

    @classmethod
    def get_bazi_month_index(cls, jd: float) -> int:
        """Get the Bazi month index (0-11) for a given Julian Day.

        Month 0 = Tiger month (starts at Li Chun, 315°)
        Month 11 = Ox month (starts at Xiao Han, 285°)
        """
        sun_long = cls.get_solar_longitude(jd)

        # Normalize to degrees since Li Chun (315°)
        # 315° -> 0, 345° -> 30, 0° -> 45, etc.
        relative_deg = (sun_long - cls.LI_CHUN_DEGREE) % 360

        # Each month spans 30° (two solar terms)
        month_index = int(relative_deg // 30)

        return month_index

    @classmethod
    def find_term_crossing(
        cls,
        target_longitude: float,
        jd_start: float,
        direction: Literal["forward", "backward"] = "forward",
    ) -> float:
        """Find the exact Julian Day when the Sun crosses a specific longitude.

        Uses the existing search engine with hybrid Newton-Raphson / bisection.

        Args:
            target_longitude: The solar longitude to find (0-360)
            jd_start: Julian Day to start searching from
            direction: "forward" or "backward"

        Returns:
            Julian Day of the crossing
        """
        result = find_longitude_crossing(
            object_name="Sun",
            target_longitude=target_longitude,
            start=jd_start,
            direction=direction,
            max_days=400.0,
        )
        if result is None:
            raise ValueError(f"Could not find Sun crossing {target_longitude}°")
        return result.julian_day

    @classmethod
    def find_month_start(cls, jd: float) -> SolarTermEvent:
        """Find the exact moment the current Bazi month started.

        Returns the SolarTermEvent for the Jie (major term) that began this month.
        """
        month_index = cls.get_bazi_month_index(jd)

        # Calculate the target longitude for this month's start
        target_long = (cls.LI_CHUN_DEGREE + (month_index * 30)) % 360

        # Search backwards from current date to find when Sun crossed this degree
        crossing_jd = cls.find_term_crossing(target_long, jd, direction="backward")

        # Find which term this is
        for term, idx in BAZI_MONTH_TERMS.items():
            if idx == month_index:
                return SolarTermEvent(
                    term=term,
                    datetime_utc=julian_day_to_datetime(crossing_jd),
                    julian_day=crossing_jd,
                )

        raise ValueError(f"Could not find term for month index {month_index}")
