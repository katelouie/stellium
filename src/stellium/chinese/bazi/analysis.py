"""Ten Gods (十神) analysis for Bazi charts.

The Ten Gods represent the relationship between the Day Master (日主) and other
stems in the chart. Each relationship has both productive and challenging aspects.

The Ten Gods are determined by two factors:
1. Element relationship (same, produces, produced-by, controls, controlled-by)
2. Polarity match (same polarity = "indirect/偏", different polarity = "direct/正")

Note: The Day Master stem always has relationship "Self" (日主/我) with itself.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from stellium.chinese.core import Element, HeavenlyStem

if TYPE_CHECKING:
    from stellium.chinese.bazi.models import BaZiChart


class TenGod(Enum):
    """The Ten Gods (十神) relationship types.

    Each value contains: (english_name, chinese_name, hanzi, short_code)
    """

    # Self (日主)
    SELF = ("Self", "日主", "我", "DM")

    # Same element relationships (比劫)
    BI_JIAN = ("Friend", "比肩", "比", "BJ")  # Same polarity
    JIE_CAI = ("Rob Wealth", "劫财", "劫", "JC")  # Different polarity

    # Day Master produces (食伤) - "Output" stars
    SHI_SHEN = ("Eating God", "食神", "食", "SS")  # Same polarity
    SHANG_GUAN = ("Hurting Officer", "伤官", "伤", "SG")  # Different polarity

    # Day Master controls (财星) - "Wealth" stars
    PIAN_CAI = ("Indirect Wealth", "偏财", "偏财", "PC")  # Same polarity
    ZHENG_CAI = ("Direct Wealth", "正财", "正财", "ZC")  # Different polarity

    # Controls Day Master (官杀) - "Power" stars
    QI_SHA = ("Seven Killings", "七杀", "杀", "QS")  # Same polarity
    ZHENG_GUAN = ("Direct Officer", "正官", "官", "ZG")  # Different polarity

    # Produces Day Master (印星) - "Resource" stars
    PIAN_YIN = ("Indirect Seal", "偏印", "枭", "PY")  # Same polarity
    ZHENG_YIN = ("Direct Seal", "正印", "印", "ZY")  # Different polarity

    def __init__(self, english: str, chinese: str, hanzi: str, short_code: str):
        self.english = english
        self.chinese = chinese
        self.hanzi = hanzi
        self.short_code = short_code

    @property
    def category(self) -> str:
        """The category this god belongs to."""
        categories = {
            TenGod.SELF: "Self",
            TenGod.BI_JIAN: "Companion",
            TenGod.JIE_CAI: "Companion",
            TenGod.SHI_SHEN: "Output",
            TenGod.SHANG_GUAN: "Output",
            TenGod.PIAN_CAI: "Wealth",
            TenGod.ZHENG_CAI: "Wealth",
            TenGod.QI_SHA: "Power",
            TenGod.ZHENG_GUAN: "Power",
            TenGod.PIAN_YIN: "Resource",
            TenGod.ZHENG_YIN: "Resource",
        }
        return categories[self]

    @property
    def is_direct(self) -> bool:
        """Whether this is a 'direct/正' relationship (different polarities)."""
        return self in (
            TenGod.JIE_CAI,
            TenGod.SHANG_GUAN,
            TenGod.ZHENG_CAI,
            TenGod.ZHENG_GUAN,
            TenGod.ZHENG_YIN,
        )


@dataclass(frozen=True)
class TenGodRelation:
    """A Ten God relationship for a specific stem in the chart."""

    stem: HeavenlyStem
    ten_god: TenGod
    pillar_name: str  # "year", "month", "day", "hour", or "hidden_X"
    is_hidden: bool = False  # True if this is a hidden stem

    @property
    def display(self) -> str:
        """Human-readable display."""
        loc = f"({self.pillar_name})" if not self.is_hidden else f"[{self.pillar_name}]"
        return f"{self.stem.hanzi} {self.ten_god.hanzi} {loc}"


def get_element_relationship(
    day_master_element: Element, other_element: Element
) -> str:
    """Determine the Wu Xing relationship between Day Master and another element.

    Returns one of: "same", "produces", "produced_by", "controls", "controlled_by"
    """
    if day_master_element == other_element:
        return "same"
    elif day_master_element.produces == other_element:
        return "produces"
    elif other_element.produces == day_master_element:
        return "produced_by"
    elif day_master_element.controls == other_element:
        return "controls"
    elif other_element.controls == day_master_element:
        return "controlled_by"
    else:
        # This shouldn't happen with the five elements
        raise ValueError(
            f"Unknown relationship: {day_master_element} -> {other_element}"
        )


def calculate_ten_god(day_master: HeavenlyStem, other_stem: HeavenlyStem) -> TenGod:
    """Calculate the Ten God relationship between Day Master and another stem.

    Args:
        day_master: The Day Master (日主) stem
        other_stem: The stem to analyze

    Returns:
        The TenGod relationship
    """
    # Self check
    if day_master == other_stem:
        return TenGod.SELF

    dm_element = day_master.element
    other_element = other_stem.element
    same_polarity = day_master.polarity == other_stem.polarity

    relationship = get_element_relationship(dm_element, other_element)

    # Map relationship + polarity to Ten God
    mapping = {
        ("same", True): TenGod.BI_JIAN,
        ("same", False): TenGod.JIE_CAI,
        ("produces", True): TenGod.SHI_SHEN,
        ("produces", False): TenGod.SHANG_GUAN,
        ("controls", True): TenGod.PIAN_CAI,
        ("controls", False): TenGod.ZHENG_CAI,
        ("controlled_by", True): TenGod.QI_SHA,
        ("controlled_by", False): TenGod.ZHENG_GUAN,
        ("produced_by", True): TenGod.PIAN_YIN,
        ("produced_by", False): TenGod.ZHENG_YIN,
    }

    return mapping[(relationship, same_polarity)]


def analyze_ten_gods(
    chart: "BaZiChart", include_hidden: bool = True
) -> list[TenGodRelation]:
    """Analyze all Ten God relationships in a Bazi chart.

    Args:
        chart: The BaZiChart to analyze
        include_hidden: Whether to include hidden stems in the analysis

    Returns:
        List of TenGodRelation objects for all stems in the chart
    """
    day_master = chart.day_master
    relations: list[TenGodRelation] = []

    pillar_names = ["year", "month", "day", "hour"]

    # Analyze main stems
    for pillar, name in zip(chart.pillars, pillar_names, strict=False):
        ten_god = calculate_ten_god(day_master, pillar.stem)
        relations.append(
            TenGodRelation(
                stem=pillar.stem,
                ten_god=ten_god,
                pillar_name=name,
                is_hidden=False,
            )
        )

    # Analyze hidden stems if requested
    if include_hidden:
        for pillar, name in zip(chart.pillars, pillar_names, strict=False):
            hidden_stems = pillar.branch.get_hidden_stem_objects()
            for i, hidden_stem in enumerate(hidden_stems):
                ten_god = calculate_ten_god(day_master, hidden_stem)
                # Label hidden stems by position: main (本气), middle (中气), residual (余气)
                position_labels = ["main", "middle", "residual"]
                position = position_labels[i] if i < 3 else f"hidden_{i}"
                relations.append(
                    TenGodRelation(
                        stem=hidden_stem,
                        ten_god=ten_god,
                        pillar_name=f"{name}_{position}",
                        is_hidden=True,
                    )
                )

    return relations


def count_ten_gods(relations: list[TenGodRelation]) -> dict[TenGod, int]:
    """Count occurrences of each Ten God in the chart.

    Args:
        relations: List of TenGodRelation from analyze_ten_gods()

    Returns:
        Dictionary mapping TenGod to count
    """
    from collections import Counter

    return dict(Counter(r.ten_god for r in relations))


def count_ten_god_categories(relations: list[TenGodRelation]) -> dict[str, int]:
    """Count Ten Gods by category (Companion, Output, Wealth, Power, Resource).

    Args:
        relations: List of TenGodRelation from analyze_ten_gods()

    Returns:
        Dictionary mapping category name to count
    """
    from collections import Counter

    return dict(Counter(r.ten_god.category for r in relations))


def get_ten_gods_for_pillar(
    relations: list[TenGodRelation], pillar_name: str
) -> list[TenGodRelation]:
    """Get all Ten God relations for a specific pillar (including hidden stems).

    Args:
        relations: List of TenGodRelation from analyze_ten_gods()
        pillar_name: One of "year", "month", "day", "hour"

    Returns:
        List of TenGodRelation for that pillar
    """
    return [r for r in relations if r.pillar_name.startswith(pillar_name)]
