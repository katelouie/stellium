"""Core primitives for Chinese astrology systems.

This module contains the fundamental building blocks shared across
different Chinese astrology systems (Bazi, Zi Wei Dou Shu, etc.):
- Polarity (Yin/Yang)
- Five Elements (Wu Xing)
- Ten Heavenly Stems (Tian Gan)
- Twelve Earthly Branches (Di Zhi)
"""

from dataclasses import dataclass
from enum import Enum


class Polarity(Enum):
    """Yin and Yang polarities."""

    YANG = "Yang"
    YIN = "Yin"

    @property
    def hanzi(self) -> str:
        return "陽" if self == Polarity.YANG else "陰"


class Element(Enum):
    """The Five Elements (Wu Xing / 五行)."""

    WOOD = ("Wood", "木", "#4caf50")
    FIRE = ("Fire", "火", "#f44336")
    EARTH = ("Earth", "土", "#795548")
    METAL = ("Metal", "金", "#9e9e9e")
    WATER = ("Water", "水", "#2196f3")

    def __init__(self, english: str, hanzi: str, color_hex: str):
        self.english = english
        self.hanzi = hanzi
        self.color_hex = color_hex

    @property
    def produces(self) -> "Element":
        """What this element produces in the generative cycle (生)."""
        cycle = {
            Element.WOOD: Element.FIRE,
            Element.FIRE: Element.EARTH,
            Element.EARTH: Element.METAL,
            Element.METAL: Element.WATER,
            Element.WATER: Element.WOOD,
        }
        return cycle[self]

    @property
    def controls(self) -> "Element":
        """What this element controls/overcomes in the controlling cycle (克)."""
        cycle = {
            Element.WOOD: Element.EARTH,
            Element.FIRE: Element.METAL,
            Element.EARTH: Element.WATER,
            Element.METAL: Element.WOOD,
            Element.WATER: Element.FIRE,
        }
        return cycle[self]


@dataclass(frozen=True)
class StemMeta:
    """Metadata for a Heavenly Stem."""

    index: int  # 0-9
    hanzi: str
    pinyin: str
    jyutping: str
    element: Element
    polarity: Polarity


class HeavenlyStem(Enum):
    """The Ten Heavenly Stems (Tian Gan / 天干)."""

    JIA = StemMeta(0, "甲", "Jiǎ", "Gaap3", Element.WOOD, Polarity.YANG)
    YI = StemMeta(1, "乙", "Yǐ", "Jyut6", Element.WOOD, Polarity.YIN)
    BING = StemMeta(2, "丙", "Bǐng", "Bing2", Element.FIRE, Polarity.YANG)
    DING = StemMeta(3, "丁", "Dīng", "Ding1", Element.FIRE, Polarity.YIN)
    WU = StemMeta(4, "戊", "Wù", "Mou6", Element.EARTH, Polarity.YANG)
    JI = StemMeta(5, "己", "Jǐ", "Gei2", Element.EARTH, Polarity.YIN)
    GENG = StemMeta(6, "庚", "Gēng", "Gang1", Element.METAL, Polarity.YANG)
    XIN = StemMeta(7, "辛", "Xīn", "San1", Element.METAL, Polarity.YIN)
    REN = StemMeta(8, "壬", "Rén", "Jam4", Element.WATER, Polarity.YANG)
    GUI = StemMeta(9, "癸", "Guǐ", "Gwai3", Element.WATER, Polarity.YIN)

    @property
    def index(self) -> int:
        return self.value.index

    @property
    def hanzi(self) -> str:
        return self.value.hanzi

    @property
    def pinyin(self) -> str:
        return self.value.pinyin

    @property
    def jyutping(self) -> str:
        return self.value.jyutping

    @property
    def element(self) -> Element:
        return self.value.element

    @property
    def polarity(self) -> Polarity:
        return self.value.polarity

    @property
    def display(self) -> str:
        """Human-readable display string."""
        return f"{self.pinyin} ({self.hanzi})"

    @property
    def display_canto(self) -> str:
        """Display string with Cantonese romanization."""
        return f"{self.pinyin}/{self.jyutping} ({self.hanzi})"

    @classmethod
    def from_index(cls, index: int) -> "HeavenlyStem":
        """Get stem by 0-9 index (modulo safe for cyclic calculations)."""
        return list(cls)[index % 10]


@dataclass(frozen=True)
class BranchMeta:
    """Metadata for an Earthly Branch."""

    index: int  # 0-11
    hanzi: str
    pinyin: str
    jyutping: str
    animal: str
    element: Element
    polarity: Polarity
    # Hidden stems within this branch (important for Bazi analysis)
    # Format: tuple of HeavenlyStem names, e.g., ("JIA", "BING", "WU")
    hidden_stems: tuple[str, ...] = ()


class EarthlyBranch(Enum):
    """The Twelve Earthly Branches (Di Zhi / 地支)."""

    ZI = BranchMeta(0, "子", "Zǐ", "Zi2", "Rat", Element.WATER, Polarity.YANG, ("GUI",))
    CHOU = BranchMeta(
        1, "丑", "Chǒu", "Cau2", "Ox", Element.EARTH, Polarity.YIN, ("JI", "GUI", "XIN")
    )
    YIN = BranchMeta(
        2,
        "寅",
        "Yín",
        "Jan4",
        "Tiger",
        Element.WOOD,
        Polarity.YANG,
        ("JIA", "BING", "WU"),
    )
    MAO = BranchMeta(
        3, "卯", "Mǎo", "Maau5", "Rabbit", Element.WOOD, Polarity.YIN, ("YI",)
    )
    CHEN = BranchMeta(
        4,
        "辰",
        "Chén",
        "San4",
        "Dragon",
        Element.EARTH,
        Polarity.YANG,
        ("WU", "YI", "GUI"),
    )
    SI = BranchMeta(
        5,
        "巳",
        "Sì",
        "Zi6",
        "Snake",
        Element.FIRE,
        Polarity.YIN,
        ("BING", "WU", "GENG"),
    )
    WU_BRANCH = BranchMeta(
        6, "午", "Wǔ", "Ng5", "Horse", Element.FIRE, Polarity.YANG, ("DING", "JI")
    )
    WEI = BranchMeta(
        7,
        "未",
        "Wèi",
        "Mei6",
        "Goat",
        Element.EARTH,
        Polarity.YIN,
        ("JI", "DING", "YI"),
    )
    SHEN = BranchMeta(
        8,
        "申",
        "Shēn",
        "San1",
        "Monkey",
        Element.METAL,
        Polarity.YANG,
        ("GENG", "REN", "WU"),
    )
    YOU = BranchMeta(
        9, "酉", "Yǒu", "Jau5", "Rooster", Element.METAL, Polarity.YIN, ("XIN",)
    )
    XU = BranchMeta(
        10,
        "戌",
        "Xū",
        "Seot1",
        "Dog",
        Element.EARTH,
        Polarity.YANG,
        ("WU", "XIN", "DING"),
    )
    HAI = BranchMeta(
        11, "亥", "Hài", "Hoi6", "Pig", Element.WATER, Polarity.YIN, ("REN", "JIA")
    )

    @property
    def index(self) -> int:
        return self.value.index

    @property
    def hanzi(self) -> str:
        return self.value.hanzi

    @property
    def pinyin(self) -> str:
        return self.value.pinyin

    @property
    def jyutping(self) -> str:
        return self.value.jyutping

    @property
    def animal(self) -> str:
        return self.value.animal

    @property
    def element(self) -> Element:
        return self.value.element

    @property
    def polarity(self) -> Polarity:
        return self.value.polarity

    @property
    def hidden_stems(self) -> tuple[str, ...]:
        return self.value.hidden_stems

    @property
    def display(self) -> str:
        """Human-readable display string."""
        return f"{self.pinyin} ({self.hanzi}) - {self.animal}"

    @classmethod
    def from_index(cls, index: int) -> "EarthlyBranch":
        """Get branch by 0-11 index (modulo safe for cyclic calculations)."""
        return list(cls)[index % 12]

    def get_hidden_stem_objects(self) -> list[HeavenlyStem]:
        """Get the actual HeavenlyStem objects for this branch's hidden stems."""
        return [HeavenlyStem[name] for name in self.hidden_stems]
