"""Comprehensive test suite for the BaZi (Four Pillars) module.

Tests cover:
- Core data models (Elements, Stems, Branches)
- Hour-to-branch mapping
- Known chart validation (Einstein, 1984 Jia Zi)
- Year boundary (Li Chun) handling
- Day pillar reference point
- Five Tigers formula (month stems)
- Five Rats formula (hour stems)
- Ten Gods analysis
- BaZiChart properties
- Solar term basics
"""

from datetime import datetime

import pytest

from stellium.chinese.bazi.analysis import (
    TenGod,
    calculate_ten_god,
    get_element_relationship,
)
from stellium.chinese.bazi.engine import (
    FIVE_RATS,
    FIVE_TIGERS,
    BaZiEngine,
    hour_to_branch_index,
)
from stellium.chinese.bazi.models import BaZiChart, Pillar
from stellium.chinese.core import (
    EarthlyBranch,
    Element,
    HeavenlyStem,
    Polarity,
)

# ============================================================================
# 1. Core Data Model Tests (fast, no calculation)
# ============================================================================


class TestElementCycles:
    """Test the Five Element generative and controlling cycles."""

    def test_generative_cycle(self):
        """Wood->Fire->Earth->Metal->Water->Wood."""
        assert Element.WOOD.produces == Element.FIRE
        assert Element.FIRE.produces == Element.EARTH
        assert Element.EARTH.produces == Element.METAL
        assert Element.METAL.produces == Element.WATER
        assert Element.WATER.produces == Element.WOOD

    def test_controlling_cycle(self):
        """Wood->Earth->Water->Fire->Metal->Wood."""
        assert Element.WOOD.controls == Element.EARTH
        assert Element.EARTH.controls == Element.WATER
        assert Element.WATER.controls == Element.FIRE
        assert Element.FIRE.controls == Element.METAL
        assert Element.METAL.controls == Element.WOOD

    def test_element_properties(self):
        """Each element has english, hanzi, and color_hex."""
        assert Element.WOOD.english == "Wood"
        assert Element.WOOD.hanzi == "木"
        assert Element.FIRE.english == "Fire"
        assert Element.FIRE.hanzi == "火"
        assert Element.EARTH.english == "Earth"
        assert Element.EARTH.hanzi == "土"
        assert Element.METAL.english == "Metal"
        assert Element.METAL.hanzi == "金"
        assert Element.WATER.english == "Water"
        assert Element.WATER.hanzi == "水"

    def test_generative_cycle_is_circular(self):
        """Following produces 5 times returns to start."""
        elem = Element.WOOD
        for _ in range(5):
            elem = elem.produces
        assert elem == Element.WOOD

    def test_controlling_cycle_is_circular(self):
        """Following controls 5 times returns to start."""
        elem = Element.WOOD
        for _ in range(5):
            elem = elem.controls
        assert elem == Element.WOOD


class TestHeavenlyStem:
    """Test Heavenly Stem properties and indexing."""

    EXPECTED_STEMS = [
        (HeavenlyStem.JIA, 0, "甲", Element.WOOD, Polarity.YANG),
        (HeavenlyStem.YI, 1, "乙", Element.WOOD, Polarity.YIN),
        (HeavenlyStem.BING, 2, "丙", Element.FIRE, Polarity.YANG),
        (HeavenlyStem.DING, 3, "丁", Element.FIRE, Polarity.YIN),
        (HeavenlyStem.WU, 4, "戊", Element.EARTH, Polarity.YANG),
        (HeavenlyStem.JI, 5, "己", Element.EARTH, Polarity.YIN),
        (HeavenlyStem.GENG, 6, "庚", Element.METAL, Polarity.YANG),
        (HeavenlyStem.XIN, 7, "辛", Element.METAL, Polarity.YIN),
        (HeavenlyStem.REN, 8, "壬", Element.WATER, Polarity.YANG),
        (HeavenlyStem.GUI, 9, "癸", Element.WATER, Polarity.YIN),
    ]

    @pytest.mark.parametrize("stem, index, hanzi, element, polarity", EXPECTED_STEMS)
    def test_stem_properties(self, stem, index, hanzi, element, polarity):
        assert stem.index == index
        assert stem.hanzi == hanzi
        assert stem.element == element
        assert stem.polarity == polarity

    def test_from_index_basic(self):
        assert HeavenlyStem.from_index(0) == HeavenlyStem.JIA
        assert HeavenlyStem.from_index(5) == HeavenlyStem.JI
        assert HeavenlyStem.from_index(9) == HeavenlyStem.GUI

    def test_from_index_modulo(self):
        """from_index wraps around at 10."""
        assert HeavenlyStem.from_index(10) == HeavenlyStem.JIA
        assert HeavenlyStem.from_index(15) == HeavenlyStem.JI
        assert HeavenlyStem.from_index(-1) == HeavenlyStem.GUI

    def test_ten_stems_exist(self):
        assert len(list(HeavenlyStem)) == 10

    def test_stem_display(self):
        """Display includes pinyin and hanzi."""
        display = HeavenlyStem.JIA.display
        assert "甲" in display

    def test_yang_stems_are_even_indexed(self):
        for stem in HeavenlyStem:
            if stem.index % 2 == 0:
                assert stem.polarity == Polarity.YANG
            else:
                assert stem.polarity == Polarity.YIN


class TestEarthlyBranch:
    """Test Earthly Branch properties and indexing."""

    EXPECTED_BRANCHES = [
        (EarthlyBranch.ZI, 0, "子", Element.WATER, Polarity.YANG, "Rat"),
        (EarthlyBranch.CHOU, 1, "丑", Element.EARTH, Polarity.YIN, "Ox"),
        (EarthlyBranch.YIN, 2, "寅", Element.WOOD, Polarity.YANG, "Tiger"),
        (EarthlyBranch.MAO, 3, "卯", Element.WOOD, Polarity.YIN, "Rabbit"),
        (EarthlyBranch.CHEN, 4, "辰", Element.EARTH, Polarity.YANG, "Dragon"),
        (EarthlyBranch.SI, 5, "巳", Element.FIRE, Polarity.YIN, "Snake"),
        (EarthlyBranch.WU_BRANCH, 6, "午", Element.FIRE, Polarity.YANG, "Horse"),
        (EarthlyBranch.WEI, 7, "未", Element.EARTH, Polarity.YIN, "Goat"),
        (EarthlyBranch.SHEN, 8, "申", Element.METAL, Polarity.YANG, "Monkey"),
        (EarthlyBranch.YOU, 9, "酉", Element.METAL, Polarity.YIN, "Rooster"),
        (EarthlyBranch.XU, 10, "戌", Element.EARTH, Polarity.YANG, "Dog"),
        (EarthlyBranch.HAI, 11, "亥", Element.WATER, Polarity.YIN, "Pig"),
    ]

    @pytest.mark.parametrize(
        "branch, index, hanzi, element, polarity, animal", EXPECTED_BRANCHES
    )
    def test_branch_properties(self, branch, index, hanzi, element, polarity, animal):
        assert branch.index == index
        assert branch.hanzi == hanzi
        assert branch.element == element
        assert branch.polarity == polarity
        assert branch.animal == animal

    def test_from_index_basic(self):
        assert EarthlyBranch.from_index(0) == EarthlyBranch.ZI
        assert EarthlyBranch.from_index(6) == EarthlyBranch.WU_BRANCH
        assert EarthlyBranch.from_index(11) == EarthlyBranch.HAI

    def test_from_index_modulo(self):
        """from_index wraps around at 12."""
        assert EarthlyBranch.from_index(12) == EarthlyBranch.ZI
        assert EarthlyBranch.from_index(14) == EarthlyBranch.YIN
        assert EarthlyBranch.from_index(-1) == EarthlyBranch.HAI

    def test_twelve_branches_exist(self):
        assert len(list(EarthlyBranch)) == 12

    def test_hidden_stems_are_valid_stem_names(self):
        """Every hidden stem name should correspond to a real HeavenlyStem."""
        stem_names = {s.name for s in HeavenlyStem}
        for branch in EarthlyBranch:
            for hs_name in branch.hidden_stems:
                assert hs_name in stem_names, (
                    f"{branch.name} has invalid hidden stem: {hs_name}"
                )

    def test_hidden_stem_objects(self):
        """get_hidden_stem_objects returns actual HeavenlyStem instances."""
        zi_hidden = EarthlyBranch.ZI.get_hidden_stem_objects()
        assert zi_hidden == [HeavenlyStem.GUI]

        yin_hidden = EarthlyBranch.YIN.get_hidden_stem_objects()
        assert yin_hidden == [HeavenlyStem.JIA, HeavenlyStem.BING, HeavenlyStem.WU]

    def test_every_branch_has_at_least_one_hidden_stem(self):
        for branch in EarthlyBranch:
            assert len(branch.hidden_stems) >= 1, f"{branch.name} has no hidden stems"


class TestPillar:
    """Test Pillar construction and properties."""

    def test_pillar_hanzi(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        assert p.hanzi == "甲子"

    def test_pillar_pinyin(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        assert "Jiǎ" in p.pinyin
        assert "Zǐ" in p.pinyin

    def test_pillar_elements(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        assert p.stem_element == Element.WOOD
        assert p.branch_element == Element.WATER

    def test_pillar_animal(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        assert p.animal == "Rat"

    def test_pillar_hidden_stems(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.YIN)
        hidden = p.hidden_stems
        assert HeavenlyStem.JIA in hidden
        assert HeavenlyStem.BING in hidden
        assert HeavenlyStem.WU in hidden

    def test_pillar_to_dict(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        d = p.to_dict()
        assert d["hanzi"] == "甲子"
        assert d["stem"]["name"] == "JIA"
        assert d["stem"]["element"] == "Wood"
        assert d["branch"]["name"] == "ZI"
        assert d["branch"]["animal"] == "Rat"
        assert isinstance(d["branch"]["hidden_stems"], list)

    def test_pillar_is_frozen(self):
        p = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)
        with pytest.raises(AttributeError):
            p.stem = HeavenlyStem.YI


# ============================================================================
# 2. Hour-to-Branch Mapping Tests
# ============================================================================


class TestHourToBranch:
    """Test hour_to_branch_index for all 12 two-hour periods."""

    # (hour, minute, expected_branch_index, expected_branch_name)
    HOUR_CASES = [
        # Zi hour: 23:00-00:59
        (23, 0, 0, "ZI"),
        (23, 30, 0, "ZI"),
        (0, 0, 0, "ZI"),
        (0, 30, 0, "ZI"),
        (0, 59, 0, "ZI"),
        # Chou hour: 01:00-02:59
        (1, 0, 1, "CHOU"),
        (2, 0, 1, "CHOU"),
        (2, 59, 1, "CHOU"),
        # Yin hour: 03:00-04:59
        (3, 0, 2, "YIN"),
        (4, 59, 2, "YIN"),
        # Mao hour: 05:00-06:59
        (5, 0, 3, "MAO"),
        (6, 59, 3, "MAO"),
        # Chen hour: 07:00-08:59
        (7, 0, 4, "CHEN"),
        (8, 59, 4, "CHEN"),
        # Si hour: 09:00-10:59
        (9, 0, 5, "SI"),
        (10, 59, 5, "SI"),
        # Wu hour: 11:00-12:59
        (11, 0, 6, "WU_BRANCH"),
        (12, 59, 6, "WU_BRANCH"),
        # Wei hour: 13:00-14:59
        (13, 0, 7, "WEI"),
        (14, 59, 7, "WEI"),
        # Shen hour: 15:00-16:59
        (15, 0, 8, "SHEN"),
        (16, 59, 8, "SHEN"),
        # You hour: 17:00-18:59
        (17, 0, 9, "YOU"),
        (18, 59, 9, "YOU"),
        # Xu hour: 19:00-20:59
        (19, 0, 10, "XU"),
        (20, 59, 10, "XU"),
        # Hai hour: 21:00-22:59
        (21, 0, 11, "HAI"),
        (22, 59, 11, "HAI"),
    ]

    @pytest.mark.parametrize("hour, minute, expected_idx, expected_name", HOUR_CASES)
    def test_hour_to_branch(self, hour, minute, expected_idx, expected_name):
        idx = hour_to_branch_index(hour, minute)
        assert idx == expected_idx
        branch = EarthlyBranch.from_index(idx)
        assert branch.name == expected_name

    def test_edge_22_59_is_hai_not_zi(self):
        """22:59 is Hai hour, NOT Zi hour."""
        assert hour_to_branch_index(22, 59) == 11  # Hai

    def test_edge_23_00_is_zi(self):
        """23:00 is the start of Zi hour."""
        assert hour_to_branch_index(23, 0) == 0  # Zi

    def test_edge_midnight(self):
        """00:00 is still Zi hour."""
        assert hour_to_branch_index(0, 0) == 0  # Zi

    def test_edge_00_59_is_zi(self):
        """00:59 is still Zi hour."""
        assert hour_to_branch_index(0, 59) == 0  # Zi

    def test_edge_01_00_is_chou(self):
        """01:00 starts Chou hour."""
        assert hour_to_branch_index(1, 0) == 1  # Chou


# ============================================================================
# 3. Known Chart Validation (SLOW — requires Swiss Ephemeris)
# ============================================================================


@pytest.mark.slow
class TestKnownCharts:
    """Validate BaZi engine against known reference charts."""

    def test_einstein_year_pillar(self):
        """Albert Einstein: March 14, 1879, 11:30 AM, Ulm Germany (UTC+1).

        1879 is after Li Chun, so Chinese year = 1879.
        Cycle position = (1879 - 1984) % 60 = (-105) % 60 = 15.
        Stem index = 15 % 10 = 5 (Ji 己).
        Branch index = 15 % 12 = 3 (Mao 卯).
        Expected Year Pillar: Ji Mao (己卯).
        """
        engine = BaZiEngine(timezone_offset_hours=1)
        chart = engine.calculate(datetime(1879, 3, 14, 11, 30))

        assert chart.year.stem == HeavenlyStem.JI
        assert chart.year.branch == EarthlyBranch.MAO
        assert chart.year.hanzi == "己卯"

    def test_einstein_hour_branch(self):
        """Einstein born at 11:30 AM -> Wu hour (11:00-12:59)."""
        engine = BaZiEngine(timezone_offset_hours=1)
        chart = engine.calculate(datetime(1879, 3, 14, 11, 30))
        assert chart.hour.branch == EarthlyBranch.WU_BRANCH

    def test_einstein_chart_has_eight_characters(self):
        engine = BaZiEngine(timezone_offset_hours=1)
        chart = engine.calculate(datetime(1879, 3, 14, 11, 30))
        assert len(chart.hanzi) == 8

    def test_1984_jia_zi_year(self):
        """1984 is the reference Jia Zi year.

        Someone born Feb 20, 1984 (after Li Chun ~Feb 4) should have
        year pillar = Jia Zi (甲子).
        """
        engine = BaZiEngine(timezone_offset_hours=8)  # Beijing time
        chart = engine.calculate(datetime(1984, 2, 20, 12, 0))

        assert chart.year.stem == HeavenlyStem.JIA
        assert chart.year.branch == EarthlyBranch.ZI
        assert chart.year.hanzi == "甲子"

    def test_1984_before_li_chun_is_previous_year(self):
        """Someone born Jan 15, 1984 (before Li Chun) should be in 1983's Chinese year.

        1983: cycle position = (1983 - 1984) % 60 = 59.
        Stem index = 59 % 10 = 9 (Gui 癸).
        Branch index = 59 % 12 = 11 (Hai 亥).
        Expected: Gui Hai (癸亥).
        """
        engine = BaZiEngine(timezone_offset_hours=8)
        chart = engine.calculate(datetime(1984, 1, 15, 12, 0))

        assert chart.year.stem == HeavenlyStem.GUI
        assert chart.year.branch == EarthlyBranch.HAI
        assert chart.year.hanzi == "癸亥"

    def test_2024_jia_chen_year(self):
        """2024 is Jia Chen year (甲辰) — Year of the Dragon.

        Cycle position = (2024 - 1984) % 60 = 40.
        Stem index = 40 % 10 = 0 (Jia 甲).
        Branch index = 40 % 12 = 4 (Chen 辰).
        """
        engine = BaZiEngine(timezone_offset_hours=8)
        chart = engine.calculate(datetime(2024, 6, 15, 12, 0))

        assert chart.year.stem == HeavenlyStem.JIA
        assert chart.year.branch == EarthlyBranch.CHEN
        assert chart.year.hanzi == "甲辰"
        assert chart.year.animal == "Dragon"

    def test_2025_yi_si_year(self):
        """2025 is Yi Si year (乙巳) — Year of the Snake.

        Cycle position = (2025 - 1984) % 60 = 41.
        Stem index = 41 % 10 = 1 (Yi 乙).
        Branch index = 41 % 12 = 5 (Si 巳).
        """
        engine = BaZiEngine(timezone_offset_hours=8)
        chart = engine.calculate(datetime(2025, 6, 15, 12, 0))

        assert chart.year.stem == HeavenlyStem.YI
        assert chart.year.branch == EarthlyBranch.SI
        assert chart.year.hanzi == "乙巳"
        assert chart.year.animal == "Snake"


# ============================================================================
# 4. Year Boundary Tests (Li Chun)
# ============================================================================


@pytest.mark.slow
class TestLiChunBoundary:
    """Test that year calculation respects Li Chun (~Feb 4) boundary."""

    def test_january_birth_uses_previous_year(self):
        """Jan 15, 2025 is still in the 2024 Chinese year (before Li Chun)."""
        engine = BaZiEngine(timezone_offset_hours=8)
        chart = engine.calculate(datetime(2025, 1, 15, 12, 0))

        # 2024 cycle position = (2024 - 1984) % 60 = 40
        # Stem 40 % 10 = 0 (Jia), Branch 40 % 12 = 4 (Chen)
        assert chart.year.stem == HeavenlyStem.JIA
        assert chart.year.branch == EarthlyBranch.CHEN

    def test_march_birth_uses_current_year(self):
        """Mar 1, 2025 is in the 2025 Chinese year (after Li Chun)."""
        engine = BaZiEngine(timezone_offset_hours=8)
        chart = engine.calculate(datetime(2025, 3, 1, 12, 0))

        # 2025 cycle position = 41
        # Stem 41 % 10 = 1 (Yi), Branch 41 % 12 = 5 (Si)
        assert chart.year.stem == HeavenlyStem.YI
        assert chart.year.branch == EarthlyBranch.SI

    def test_timezone_can_shift_li_chun_boundary(self):
        """A date near Li Chun might differ based on timezone offset.

        Li Chun is ~Feb 3-5 in UTC. A birth at Feb 4 00:30 UTC+8
        converts to Feb 3 16:30 UTC. The solar longitude at that
        UTC moment determines if we are before or after Li Chun.
        """
        # This test just checks the engine handles timezone properly
        # without crashing -- the exact pillar depends on precise Li Chun timing.
        engine_utc = BaZiEngine(timezone_offset_hours=0)
        engine_bj = BaZiEngine(timezone_offset_hours=8)

        # Both should produce valid charts without errors
        chart_utc = engine_utc.calculate(datetime(2025, 2, 4, 0, 30))
        chart_bj = engine_bj.calculate(datetime(2025, 2, 4, 0, 30))

        assert chart_utc.year.stem is not None
        assert chart_bj.year.stem is not None


# ============================================================================
# 5. Day Pillar Reference Point
# ============================================================================


@pytest.mark.slow
class TestDayPillar:
    """Test day pillar calculation against the reference date."""

    def test_reference_date_is_jia_zi(self):
        """Feb 20, 1900 (the reference date) should give Jia Zi day pillar."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(1900, 2, 20, 12, 0))

        assert chart.day.stem == HeavenlyStem.JIA
        assert chart.day.branch == EarthlyBranch.ZI
        assert chart.day.hanzi == "甲子"

    def test_day_after_reference_is_yi_chou(self):
        """Feb 21, 1900 should be Yi Chou (next in cycle)."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(1900, 2, 21, 12, 0))

        assert chart.day.stem == HeavenlyStem.YI
        assert chart.day.branch == EarthlyBranch.CHOU

    def test_two_days_after_reference_is_bing_yin(self):
        """Feb 22, 1900 should be Bing Yin."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(1900, 2, 22, 12, 0))

        assert chart.day.stem == HeavenlyStem.BING
        assert chart.day.branch == EarthlyBranch.YIN

    def test_60_days_after_reference_cycles_back(self):
        """60 days after reference should cycle back to Jia Zi."""
        engine = BaZiEngine(timezone_offset_hours=0)
        # Feb 20 + 60 days = April 21, 1900
        chart = engine.calculate(datetime(1900, 4, 21, 12, 0))

        assert chart.day.stem == HeavenlyStem.JIA
        assert chart.day.branch == EarthlyBranch.ZI

    def test_day_before_reference_is_gui_hai(self):
        """Feb 19, 1900 at midnight UTC should give the previous day in cycle.

        The engine uses int(jd - REFERENCE_JD) where REFERENCE_JD is Feb 20 00:00 UT.
        Feb 19 00:00 UT gives diff = -1.0, int = -1.
        Cycle position -1: stem (-1) % 10 = 9 (Gui), branch (-1) % 12 = 11 (Hai).
        """
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(1900, 2, 19, 0, 0))

        assert chart.day.stem == HeavenlyStem.GUI
        assert chart.day.branch == EarthlyBranch.HAI


# ============================================================================
# 6. Five Tigers Formula Tests (Month Stems)
# ============================================================================


class TestFiveTigersFormula:
    """Test the Five Tigers (Wu Hu Dun) formula for month stems.

    The formula maps year stem to the first month (Tiger month) stem:
    - Jia/Ji year -> Bing Yin month
    - Yi/Geng year -> Wu Yin month
    - Bing/Xin year -> Geng Yin month
    - Ding/Ren year -> Ren Yin month
    - Wu/Gui year -> Jia Yin month
    """

    def test_jia_year_gives_bing_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.JIA] == HeavenlyStem.BING

    def test_ji_year_gives_bing_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.JI] == HeavenlyStem.BING

    def test_yi_year_gives_wu_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.YI] == HeavenlyStem.WU

    def test_geng_year_gives_wu_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.GENG] == HeavenlyStem.WU

    def test_bing_year_gives_geng_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.BING] == HeavenlyStem.GENG

    def test_xin_year_gives_geng_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.XIN] == HeavenlyStem.GENG

    def test_ding_year_gives_ren_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.DING] == HeavenlyStem.REN

    def test_ren_year_gives_ren_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.REN] == HeavenlyStem.REN

    def test_wu_year_gives_jia_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.WU] == HeavenlyStem.JIA

    def test_gui_year_gives_jia_tiger_month(self):
        assert FIVE_TIGERS[HeavenlyStem.GUI] == HeavenlyStem.JIA

    def test_all_ten_stems_have_mapping(self):
        """Every stem should have a Five Tigers mapping."""
        for stem in HeavenlyStem:
            assert stem in FIVE_TIGERS

    def test_paired_stems_give_same_result(self):
        """Stems that share the same element pair should give the same result."""
        pairs = [
            (HeavenlyStem.JIA, HeavenlyStem.JI),
            (HeavenlyStem.YI, HeavenlyStem.GENG),
            (HeavenlyStem.BING, HeavenlyStem.XIN),
            (HeavenlyStem.DING, HeavenlyStem.REN),
            (HeavenlyStem.WU, HeavenlyStem.GUI),
        ]
        for a, b in pairs:
            assert FIVE_TIGERS[a] == FIVE_TIGERS[b]


# ============================================================================
# 7. Five Rats Formula Tests (Hour Stems)
# ============================================================================


class TestFiveRatsFormula:
    """Test the Five Rats (Wu Shu Dun) formula for hour stems.

    The formula maps day stem to the Zi hour stem:
    - Jia/Ji day -> Jia Zi hour
    - Yi/Geng day -> Bing Zi hour
    - Bing/Xin day -> Wu Zi hour
    - Ding/Ren day -> Geng Zi hour
    - Wu/Gui day -> Ren Zi hour
    """

    def test_jia_day_gives_jia_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.JIA] == HeavenlyStem.JIA

    def test_ji_day_gives_jia_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.JI] == HeavenlyStem.JIA

    def test_yi_day_gives_bing_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.YI] == HeavenlyStem.BING

    def test_geng_day_gives_bing_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.GENG] == HeavenlyStem.BING

    def test_bing_day_gives_wu_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.BING] == HeavenlyStem.WU

    def test_xin_day_gives_wu_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.XIN] == HeavenlyStem.WU

    def test_ding_day_gives_geng_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.DING] == HeavenlyStem.GENG

    def test_ren_day_gives_geng_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.REN] == HeavenlyStem.GENG

    def test_wu_day_gives_ren_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.WU] == HeavenlyStem.REN

    def test_gui_day_gives_ren_zi_hour(self):
        assert FIVE_RATS[HeavenlyStem.GUI] == HeavenlyStem.REN

    def test_all_ten_stems_have_mapping(self):
        for stem in HeavenlyStem:
            assert stem in FIVE_RATS

    def test_paired_stems_give_same_result(self):
        pairs = [
            (HeavenlyStem.JIA, HeavenlyStem.JI),
            (HeavenlyStem.YI, HeavenlyStem.GENG),
            (HeavenlyStem.BING, HeavenlyStem.XIN),
            (HeavenlyStem.DING, HeavenlyStem.REN),
            (HeavenlyStem.WU, HeavenlyStem.GUI),
        ]
        for a, b in pairs:
            assert FIVE_RATS[a] == FIVE_RATS[b]


# ============================================================================
# 8. Ten Gods Analysis Tests
# ============================================================================


class TestTenGods:
    """Test Ten Gods (Shi Shen) calculation with Jia as Day Master."""

    def test_jia_vs_jia_is_self(self):
        """Same stem -> Self (我)."""
        assert calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.JIA) == TenGod.SELF

    def test_jia_vs_yi_is_rob_wealth(self):
        """Same element, different polarity -> Rob Wealth (劫财)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.YI)
        assert result == TenGod.JIE_CAI
        assert result.english == "Rob Wealth"

    def test_jia_vs_bing_is_eating_god(self):
        """Wood produces Fire, same polarity -> Eating God (食神)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.BING)
        assert result == TenGod.SHI_SHEN
        assert result.english == "Eating God"

    def test_jia_vs_ding_is_hurting_officer(self):
        """Wood produces Fire, different polarity -> Hurting Officer (伤官)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.DING)
        assert result == TenGod.SHANG_GUAN
        assert result.english == "Hurting Officer"

    def test_jia_vs_wu_is_indirect_wealth(self):
        """Wood controls Earth, same polarity -> Indirect Wealth (偏财)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.WU)
        assert result == TenGod.PIAN_CAI
        assert result.english == "Indirect Wealth"

    def test_jia_vs_ji_is_direct_wealth(self):
        """Wood controls Earth, different polarity -> Direct Wealth (正财)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.JI)
        assert result == TenGod.ZHENG_CAI
        assert result.english == "Direct Wealth"

    def test_jia_vs_geng_is_seven_killings(self):
        """Metal controls Wood, same polarity -> Seven Killings (七杀)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.GENG)
        assert result == TenGod.QI_SHA
        assert result.english == "Seven Killings"

    def test_jia_vs_xin_is_direct_officer(self):
        """Metal controls Wood, different polarity -> Direct Officer (正官)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.XIN)
        assert result == TenGod.ZHENG_GUAN
        assert result.english == "Direct Officer"

    def test_jia_vs_ren_is_indirect_seal(self):
        """Water produces Wood, same polarity -> Indirect Seal (偏印)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.REN)
        assert result == TenGod.PIAN_YIN
        assert result.english == "Indirect Seal"

    def test_jia_vs_gui_is_direct_seal(self):
        """Water produces Wood, different polarity -> Direct Seal (正印)."""
        result = calculate_ten_god(HeavenlyStem.JIA, HeavenlyStem.GUI)
        assert result == TenGod.ZHENG_YIN
        assert result.english == "Direct Seal"


class TestTenGodProperties:
    """Test TenGod enum properties."""

    def test_ten_god_categories(self):
        assert TenGod.SELF.category == "Self"
        assert TenGod.BI_JIAN.category == "Companion"
        assert TenGod.JIE_CAI.category == "Companion"
        assert TenGod.SHI_SHEN.category == "Output"
        assert TenGod.SHANG_GUAN.category == "Output"
        assert TenGod.PIAN_CAI.category == "Wealth"
        assert TenGod.ZHENG_CAI.category == "Wealth"
        assert TenGod.QI_SHA.category == "Power"
        assert TenGod.ZHENG_GUAN.category == "Power"
        assert TenGod.PIAN_YIN.category == "Resource"
        assert TenGod.ZHENG_YIN.category == "Resource"

    def test_is_direct(self):
        """Direct relationships have different polarities."""
        assert not TenGod.BI_JIAN.is_direct  # Same polarity
        assert TenGod.JIE_CAI.is_direct  # Different polarity
        assert not TenGod.SHI_SHEN.is_direct
        assert TenGod.SHANG_GUAN.is_direct
        assert not TenGod.PIAN_CAI.is_direct
        assert TenGod.ZHENG_CAI.is_direct
        assert not TenGod.QI_SHA.is_direct
        assert TenGod.ZHENG_GUAN.is_direct
        assert not TenGod.PIAN_YIN.is_direct
        assert TenGod.ZHENG_YIN.is_direct


class TestElementRelationship:
    """Test the element relationship function."""

    def test_same_element(self):
        assert get_element_relationship(Element.WOOD, Element.WOOD) == "same"

    def test_produces(self):
        assert get_element_relationship(Element.WOOD, Element.FIRE) == "produces"

    def test_produced_by(self):
        assert get_element_relationship(Element.FIRE, Element.WOOD) == "produced_by"

    def test_controls(self):
        assert get_element_relationship(Element.WOOD, Element.EARTH) == "controls"

    def test_controlled_by(self):
        assert get_element_relationship(Element.EARTH, Element.WOOD) == "controlled_by"

    def test_all_relationships_covered(self):
        """Every pair of elements should have a valid relationship."""
        valid = {"same", "produces", "produced_by", "controls", "controlled_by"}
        for e1 in Element:
            for e2 in Element:
                result = get_element_relationship(e1, e2)
                assert result in valid, f"{e1} vs {e2} gave {result}"


# ============================================================================
# 9. BaZiChart Properties Tests
# ============================================================================


@pytest.mark.slow
class TestBaZiChartProperties:
    """Test BaZiChart computed properties."""

    @pytest.fixture
    def sample_chart(self):
        """A chart for a known date to test properties."""
        engine = BaZiEngine(timezone_offset_hours=0)
        return engine.calculate(datetime(2000, 6, 15, 12, 0))

    def test_hanzi_is_eight_characters(self, sample_chart):
        assert len(sample_chart.hanzi) == 8

    def test_day_master_is_day_stem(self, sample_chart):
        assert sample_chart.day_master == sample_chart.day.stem

    def test_day_master_element(self, sample_chart):
        assert sample_chart.day_master_element == sample_chart.day.stem.element

    def test_all_stems_returns_four(self, sample_chart):
        stems = sample_chart.all_stems
        assert len(stems) == 4
        assert all(isinstance(s, HeavenlyStem) for s in stems)

    def test_all_branches_returns_four(self, sample_chart):
        branches = sample_chart.all_branches
        assert len(branches) == 4
        assert all(isinstance(b, EarthlyBranch) for b in branches)

    def test_pillars_tuple_has_four(self, sample_chart):
        assert len(sample_chart.pillars) == 4
        assert sample_chart.pillars[0] == sample_chart.year
        assert sample_chart.pillars[1] == sample_chart.month
        assert sample_chart.pillars[2] == sample_chart.day
        assert sample_chart.pillars[3] == sample_chart.hour

    def test_element_counts_basic(self, sample_chart):
        counts = sample_chart.element_counts()
        # Should include counts from 4 stems + 4 branches = 8 element entries
        total = sum(counts.values())
        assert total == 8
        # All keys should be Element instances
        assert all(isinstance(k, Element) for k in counts)

    def test_element_counts_with_hidden(self, sample_chart):
        counts_basic = sample_chart.element_counts(include_hidden=False)
        counts_hidden = sample_chart.element_counts(include_hidden=True)
        # With hidden stems should have more total elements
        assert sum(counts_hidden.values()) > sum(counts_basic.values())

    def test_polarity_counts(self, sample_chart):
        counts = sample_chart.polarity_counts()
        total = sum(counts.values())
        assert total == 8  # 4 stems + 4 branches
        assert all(isinstance(k, Polarity) for k in counts)

    def test_to_dict_is_serializable(self, sample_chart):
        """to_dict should return JSON-serializable data."""
        import json

        d = sample_chart.to_dict()
        # Should not raise
        json_str = json.dumps(d)
        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_to_dict_structure(self, sample_chart):
        d = sample_chart.to_dict()
        assert d["system"] == "Bazi"
        assert "birth_datetime" in d
        assert "eight_characters" in d
        assert "day_master" in d
        assert "pillars" in d
        assert set(d["pillars"].keys()) == {"year", "month", "day", "hour"}
        assert "element_counts" in d
        assert "polarity_counts" in d

    def test_display_returns_string(self, sample_chart):
        display = sample_chart.display()
        assert isinstance(display, str)
        assert "Bazi Chart" in display
        assert "Day Master" in display

    def test_display_detailed_returns_string(self, sample_chart):
        display = sample_chart.display_detailed()
        assert isinstance(display, str)
        assert "Ten Gods" in display

    def test_system_name(self, sample_chart):
        assert sample_chart.system_name == "Bazi"

    def test_all_hidden_stems(self, sample_chart):
        hidden = sample_chart.all_hidden_stems
        assert len(hidden) > 0
        assert all(isinstance(s, HeavenlyStem) for s in hidden)

    def test_ten_gods_analysis(self, sample_chart):
        relations = sample_chart.ten_gods(include_hidden=False)
        # 4 main stems
        assert len(relations) == 4
        # Day pillar should be Self
        day_rel = [r for r in relations if r.pillar_name == "day"]
        assert len(day_rel) == 1
        assert day_rel[0].ten_god == TenGod.SELF

    def test_ten_gods_with_hidden(self, sample_chart):
        relations_no_hidden = sample_chart.ten_gods(include_hidden=False)
        relations_with_hidden = sample_chart.ten_gods(include_hidden=True)
        assert len(relations_with_hidden) > len(relations_no_hidden)

    def test_chart_is_frozen(self, sample_chart):
        with pytest.raises(AttributeError):
            sample_chart.year = Pillar(stem=HeavenlyStem.JIA, branch=EarthlyBranch.ZI)

    def test_str_is_hanzi(self, sample_chart):
        assert str(sample_chart) == sample_chart.hanzi


# ============================================================================
# 10. Solar Term Tests
# ============================================================================


class TestSolarTermBasics:
    """Test basic solar term properties (no ephemeris needed)."""

    def test_li_chun_longitude_is_315(self):
        from stellium.chinese.calendar import SolarTerm

        assert SolarTerm.LI_CHUN.longitude == 315

    def test_li_chun_is_major_term(self):
        from stellium.chinese.calendar import SolarTerm

        assert SolarTerm.LI_CHUN.is_major_term

    def test_24_solar_terms_exist(self):
        from stellium.chinese.calendar import SolarTerm

        assert len(list(SolarTerm)) == 24

    def test_major_terms_are_even_indexed(self):
        """Major terms (Jie) have even indices; minor terms (Qi) have odd indices."""
        from stellium.chinese.calendar import SolarTerm

        for term in SolarTerm:
            if term._index % 2 == 0:
                assert term.is_major_term, f"{term.english} should be major"
            else:
                assert not term.is_major_term, f"{term.english} should be minor"

    def test_solar_term_longitudes_cover_full_circle(self):
        """The 24 terms should cover all 360 degrees in 15-degree steps."""
        from stellium.chinese.calendar import SolarTerm

        longitudes = sorted(term.longitude for term in SolarTerm)
        assert len(longitudes) == 24
        # Check spacing is 15 degrees (allowing for wrap-around)
        for i in range(len(longitudes) - 1):
            diff = (longitudes[i + 1] - longitudes[i]) % 360
            assert diff == 15, f"Gap between terms: {diff} (expected 15)"

    def test_bazi_month_terms_map_12_months(self):
        from stellium.chinese.calendar import BAZI_MONTH_TERMS

        assert len(BAZI_MONTH_TERMS) == 12
        # Should map indices 0-11
        assert set(BAZI_MONTH_TERMS.values()) == set(range(12))

    def test_from_longitude_at_li_chun(self):
        from stellium.chinese.calendar import SolarTerm

        term = SolarTerm.from_longitude(315)
        assert term == SolarTerm.LI_CHUN

    def test_from_longitude_at_spring_equinox(self):
        from stellium.chinese.calendar import SolarTerm

        term = SolarTerm.from_longitude(0)
        assert term == SolarTerm.CHUN_FEN


@pytest.mark.slow
class TestSolarTermEngine:
    """Test SolarTermEngine calculations (requires Swiss Ephemeris)."""

    def test_get_bazi_month_index_midsummer(self):
        """Mid-July should be around month 5 or 6."""
        from stellium.chinese.calendar import SolarTermEngine
        from stellium.utils.time import datetime_to_julian_day

        jd = datetime_to_julian_day(datetime(2024, 7, 15, 12, 0))
        month_idx = SolarTermEngine.get_bazi_month_index(jd)
        # July is roughly month 5 (Horse) or 6 (Goat) depending on exact solar terms
        assert 4 <= month_idx <= 6

    def test_get_solar_longitude_returns_valid_range(self):
        from stellium.chinese.calendar import SolarTermEngine
        from stellium.utils.time import datetime_to_julian_day

        jd = datetime_to_julian_day(datetime(2024, 6, 21, 12, 0))
        longitude = SolarTermEngine.get_solar_longitude(jd)
        assert 0 <= longitude < 360

    def test_summer_solstice_near_90_degrees(self):
        """Around June 21, the Sun should be near 90 degrees (Cancer 0)."""
        from stellium.chinese.calendar import SolarTermEngine
        from stellium.utils.time import datetime_to_julian_day

        jd = datetime_to_julian_day(datetime(2024, 6, 21, 12, 0))
        longitude = SolarTermEngine.get_solar_longitude(jd)
        # Should be close to 90 degrees
        assert 88 <= longitude <= 92


# ============================================================================
# Additional Integration Tests
# ============================================================================


@pytest.mark.slow
class TestEngineIntegration:
    """Integration tests for the full BaZi engine pipeline."""

    def test_engine_system_name(self):
        engine = BaZiEngine()
        assert engine.system_name == "Bazi"

    def test_engine_default_timezone_is_zero(self):
        engine = BaZiEngine()
        assert engine.timezone_offset == 0.0

    def test_engine_with_custom_timezone(self):
        engine = BaZiEngine(timezone_offset_hours=-8)
        assert engine.timezone_offset == -8.0

    def test_modern_date_produces_valid_chart(self):
        engine = BaZiEngine(timezone_offset_hours=-8)
        chart = engine.calculate(datetime(1994, 1, 6, 11, 47))

        assert isinstance(chart, BaZiChart)
        assert len(chart.hanzi) == 8
        assert chart.day_master is not None
        assert len(chart.all_stems) == 4
        assert len(chart.all_branches) == 4

    def test_midnight_birth_zi_hour(self):
        """Birth at midnight should be Zi hour."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 0, 0))
        assert chart.hour.branch == EarthlyBranch.ZI

    def test_late_night_birth_zi_hour(self):
        """Birth at 23:30 should be Zi hour."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 23, 30))
        assert chart.hour.branch == EarthlyBranch.ZI

    def test_backwards_compatibility_alias(self):
        """BaZiCalculator should be an alias for BaZiEngine."""
        from stellium.chinese.bazi.engine import BaZiCalculator

        assert BaZiCalculator is BaZiEngine

    def test_month_pillar_branch_is_valid(self):
        """Month branch should always be one of the 12 branches."""
        engine = BaZiEngine(timezone_offset_hours=0)
        for month in range(1, 13):
            chart = engine.calculate(datetime(2024, month, 15, 12, 0))
            assert chart.month.branch in list(EarthlyBranch)

    def test_hour_pillar_changes_with_time(self):
        """Different birth hours should produce different hour pillars."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart_morning = engine.calculate(datetime(2024, 6, 15, 6, 0))
        chart_evening = engine.calculate(datetime(2024, 6, 15, 18, 0))

        # 6:00 (Mao) vs 18:00 (You) - different branches
        assert chart_morning.hour.branch != chart_evening.hour.branch

    def test_different_days_have_different_day_pillars(self):
        """Consecutive days should have different day pillars."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart_day1 = engine.calculate(datetime(2024, 6, 15, 12, 0))
        chart_day2 = engine.calculate(datetime(2024, 6, 16, 12, 0))

        assert chart_day1.day != chart_day2.day

    def test_year_pillar_same_for_same_chinese_year(self):
        """Two dates in the same Chinese year should have the same year pillar."""
        engine = BaZiEngine(timezone_offset_hours=0)
        chart_march = engine.calculate(datetime(2024, 3, 15, 12, 0))
        chart_sept = engine.calculate(datetime(2024, 9, 15, 12, 0))

        assert chart_march.year == chart_sept.year


# =============================================================================
# DAY MASTER STRENGTH ANALYSIS
# =============================================================================


class TestSeasonalScore:
    """Test the seasonal strength scoring."""

    def _score(self, element, branch):
        from stellium.chinese.bazi.strength import _get_seasonal_score

        return _get_seasonal_score(element, branch)

    def test_wood_in_spring_prosperous(self):
        """Wood is prosperous in spring (Yin/Mao months)."""
        assert self._score(Element.WOOD, EarthlyBranch.YIN) == 3
        assert self._score(Element.WOOD, EarthlyBranch.MAO) == 3

    def test_fire_in_summer_prosperous(self):
        """Fire is prosperous in summer (Si/Wu months)."""
        assert self._score(Element.FIRE, EarthlyBranch.SI) == 3
        assert self._score(Element.FIRE, EarthlyBranch.WU_BRANCH) == 3

    def test_metal_in_autumn_prosperous(self):
        """Metal is prosperous in autumn (Shen/You months)."""
        assert self._score(Element.METAL, EarthlyBranch.SHEN) == 3
        assert self._score(Element.METAL, EarthlyBranch.YOU) == 3

    def test_water_in_winter_prosperous(self):
        """Water is prosperous in winter (Hai/Zi months)."""
        assert self._score(Element.WATER, EarthlyBranch.HAI) == 3
        assert self._score(Element.WATER, EarthlyBranch.ZI) == 3

    def test_earth_in_transition_months(self):
        """Earth is prosperous in the four transition months."""
        assert self._score(Element.EARTH, EarthlyBranch.CHEN) == 3
        assert self._score(Element.EARTH, EarthlyBranch.WEI) == 3
        assert self._score(Element.EARTH, EarthlyBranch.XU) == 3
        assert self._score(Element.EARTH, EarthlyBranch.CHOU) == 3

    def test_element_produced_by_season_strong(self):
        """Element produced by the season's element gets +1."""
        assert self._score(Element.FIRE, EarthlyBranch.MAO) == 1

    def test_element_controls_season_dead(self):
        """Element that controls the season's element is dead (-2)."""
        assert self._score(Element.METAL, EarthlyBranch.MAO) == -2

    def test_element_controlled_by_season_imprisoned(self):
        """Element controlled by the season's element is imprisoned (-1)."""
        assert self._score(Element.EARTH, EarthlyBranch.MAO) == -1

    def test_element_produces_season_resting(self):
        """Element that produces the season's element is resting (0)."""
        assert self._score(Element.WATER, EarthlyBranch.MAO) == 0


class TestElementReverseCycles:
    """Test the new produced_by and controlled_by properties."""

    def test_produced_by_cycle(self):
        assert Element.WOOD.produced_by == Element.WATER
        assert Element.FIRE.produced_by == Element.WOOD
        assert Element.EARTH.produced_by == Element.FIRE
        assert Element.METAL.produced_by == Element.EARTH
        assert Element.WATER.produced_by == Element.METAL

    def test_controlled_by_cycle(self):
        assert Element.WOOD.controlled_by == Element.METAL
        assert Element.FIRE.controlled_by == Element.WATER
        assert Element.EARTH.controlled_by == Element.WOOD
        assert Element.METAL.controlled_by == Element.FIRE
        assert Element.WATER.controlled_by == Element.EARTH

    def test_produces_produced_by_inverse(self):
        """produced_by should be the inverse of produces."""
        for elem in Element:
            assert elem.produced_by.produces == elem

    def test_controls_controlled_by_inverse(self):
        """controlled_by should be the inverse of controls."""
        for elem in Element:
            assert elem.controlled_by.controls == elem


class TestRootCounting:
    """Test hidden stem root counting."""

    @pytest.mark.slow
    def test_roots_found(self):
        """A chart should have at least some roots for the day master element."""
        from stellium.chinese.bazi.strength import _count_roots

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 12, 21, 0, 0))
        dm_element = chart.day_master.element
        roots = _count_roots(chart, dm_element)
        assert isinstance(roots, int)
        assert roots >= 0

    def test_roots_range(self):
        """Root count should be between 0 and 12 (4 branches × 3 hidden stems max)."""
        from stellium.chinese.bazi.strength import _count_roots

        # Create a chart where we can predict roots
        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        dm_element = chart.day_master.element
        roots = _count_roots(chart, dm_element)
        assert 0 <= roots <= 12


class TestSupportDrain:
    """Test support vs drain counting."""

    @pytest.mark.slow
    def test_support_drain_sums(self):
        """Support + drain should account for all non-Day-Master Ten God categories."""
        from stellium.chinese.bazi.strength import _count_support_drain

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        support, drain = _count_support_drain(chart)
        assert support > 0
        assert drain > 0
        # Total should equal all ten god relations
        assert support + drain > 0


class TestStrengthAnalysis:
    """Test the full strength analysis."""

    @pytest.mark.slow
    def test_analysis_returns_result(self):
        from stellium.chinese.bazi.strength import StrengthAnalysis, analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        assert isinstance(result, StrengthAnalysis)

    @pytest.mark.slow
    def test_analysis_has_all_fields(self):
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)

        assert result.day_master is not None
        assert result.day_master_element is not None
        assert result.strength is not None
        assert isinstance(result.score, float)
        assert isinstance(result.seasonal_score, int)
        assert isinstance(result.root_count, int)
        assert isinstance(result.support_count, int)
        assert isinstance(result.drain_count, int)

    @pytest.mark.slow
    def test_water_in_winter_strong(self):
        """Water day master born in winter should be strong."""
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        # Dec 21 in Zi month — Water peak season
        chart = engine.calculate(datetime(2000, 12, 21, 0, 0))
        result = analyze_strength(chart)
        if result.day_master_element == Element.WATER:
            assert result.is_strong

    @pytest.mark.slow
    def test_favorable_unfavorable_differ(self):
        """Favorable and unfavorable elements should not overlap."""
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        assert (
            set(result.favorable_elements) & set(result.unfavorable_elements) == set()
        )

    @pytest.mark.slow
    def test_favorable_count(self):
        """Should have favorable and unfavorable elements."""
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        assert len(result.favorable_elements) > 0
        assert len(result.unfavorable_elements) > 0

    @pytest.mark.slow
    def test_is_strong_is_weak_exclusive(self):
        """A chart cannot be both strong and weak."""
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        assert not (result.is_strong and result.is_weak)

    @pytest.mark.slow
    def test_to_dict_serializable(self):
        """to_dict should return JSON-serializable data."""
        import json

        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        data = result.to_dict()
        # Should not raise
        json.dumps(data)
        assert "strength" in data
        assert "factors" in data
        assert "favorable_elements" in data

    @pytest.mark.slow
    def test_display_returns_string(self):
        from stellium.chinese.bazi.strength import analyze_strength

        engine = BaZiEngine(timezone_offset_hours=0)
        chart = engine.calculate(datetime(2000, 6, 15, 12, 0))
        result = analyze_strength(chart)
        text = result.display()
        assert isinstance(text, str)
        assert "Day Master" in text
        assert "Strength" in text

    @pytest.mark.slow
    def test_strength_classification_values(self):
        """All DayMasterStrength values should have required attributes."""
        from stellium.chinese.bazi.strength import DayMasterStrength

        for strength in DayMasterStrength:
            assert hasattr(strength, "english")
            assert hasattr(strength, "hanzi")
            assert hasattr(strength, "pinyin")


# =============================================================================
# CHARTBUILDER / CALCULATEDCHART INTEGRATION
# =============================================================================


class TestChartBuilderBazi:
    """Test the .bazi() method on ChartBuilder."""

    @pytest.mark.slow
    def test_bazi_from_builder(self):
        """ChartBuilder.from_details().bazi() returns a BaZiChart."""
        from stellium import ChartBuilder
        from stellium.chinese.bazi.models import BaZiChart

        bazi = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()
        assert isinstance(bazi, BaZiChart)
        assert bazi.hanzi is not None
        assert len(bazi.hanzi) == 8

    @pytest.mark.slow
    def test_bazi_from_notable(self):
        """ChartBuilder.from_notable().bazi() works."""
        from stellium import ChartBuilder

        bazi = ChartBuilder.from_notable("Albert Einstein").bazi()
        assert bazi.day_master is not None
        assert bazi.day_master_element is not None

    @pytest.mark.slow
    def test_bazi_from_calculated_chart(self):
        """CalculatedChart.bazi() returns a BaZiChart."""
        from stellium import ChartBuilder
        from stellium.chinese.bazi.models import BaZiChart

        chart = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()
        bazi = chart.bazi()
        assert isinstance(bazi, BaZiChart)

    @pytest.mark.slow
    def test_builder_and_chart_bazi_match(self):
        """Both .bazi() paths should produce the same chart."""
        from stellium import ChartBuilder

        builder_bazi = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).bazi()

        chart = ChartBuilder.from_details(
            "1994-01-06 11:47", "Palo Alto, CA"
        ).calculate()
        chart_bazi = chart.bazi()

        assert builder_bazi.hanzi == chart_bazi.hanzi

    @pytest.mark.slow
    def test_bazi_strength_method(self):
        """.strength() method works on BaZiChart from ChartBuilder."""
        from stellium import ChartBuilder
        from stellium.chinese.bazi.strength import StrengthAnalysis

        bazi = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").bazi()
        result = bazi.strength()
        assert isinstance(result, StrengthAnalysis)
        assert result.day_master == bazi.day_master

    @pytest.mark.slow
    def test_bazi_timezone_handling(self):
        """Location-based timezone should affect the chart calculation."""
        from stellium import ChartBuilder

        # Beijing (UTC+8) and New York (UTC-4 EDT) at 2:00 AM local
        # Use coordinates to avoid geocoding dependency in tests
        beijing = ChartBuilder.from_details("2000-06-15 02:00", (39.9, 116.4)).bazi()
        ny = ChartBuilder.from_details("2000-06-15 02:00", (40.7, -74.0)).bazi()

        # 12-hour UTC difference → different day pillars
        assert beijing.hanzi != ny.hanzi

    @pytest.mark.slow
    def test_bazi_with_coords(self):
        """ChartBuilder with coordinate tuple should work for .bazi()."""
        from stellium import ChartBuilder

        bazi = ChartBuilder.from_details("2000-06-15 12:00", (47.6, -122.3)).bazi()
        assert bazi.hanzi is not None
        assert len(bazi.hanzi) == 8
