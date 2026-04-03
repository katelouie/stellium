"""Day Master Strength Analysis (日主强弱) for BaZi charts.

Determines whether the Day Master (日主) is strong (旺) or weak (弱)
by analyzing four traditional factors:

1. **Seasonal strength (令)** — Is the Day Master's element in season?
   The month branch determines which element is prosperous, resting,
   imprisoned, or dead.

2. **Root strength (根/禄)** — Does the Day Master have roots in
   the branches? Hidden stems matching the Day Master's element
   provide grounding and stability.

3. **Support count** — How many chart elements support the Day Master?
   Companion (比劫) and Resource (印星) elements help.

4. **Drain count** — How many chart elements drain or control the
   Day Master? Output (食伤), Wealth (财星), and Power (官杀)
   elements weaken it.

The weighted score determines strength classification:
- Very Strong (极旺): dominant element, seasonal support, many roots
- Strong (旺): favorable balance of support vs drain
- Moderate (中和): roughly balanced
- Weak (弱): unfavorable balance
- Very Weak (极弱): no seasonal support, no roots, heavy drain

References:
- Traditional seasonal strength tables (十二长生 / Twelve Growth Stages)
- Joey Yap, "BaZi — The Destiny Code"
- Lily Chung, "The Path to Good Fortune"
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from stellium.chinese.bazi.analysis import (
    analyze_ten_gods,
    count_ten_god_categories,
)
from stellium.chinese.core import EarthlyBranch, Element, HeavenlyStem

if TYPE_CHECKING:
    from stellium.chinese.bazi.models import BaZiChart


class DayMasterStrength(Enum):
    """Classification of Day Master strength."""

    VERY_STRONG = ("Very Strong", "极旺", "jí wàng")
    STRONG = ("Strong", "旺", "wàng")
    MODERATE = ("Moderate", "中和", "zhōng hé")
    WEAK = ("Weak", "弱", "ruò")
    VERY_WEAK = ("Very Weak", "极弱", "jí ruò")

    def __init__(self, english: str, hanzi: str, pinyin: str):
        self.english = english
        self.hanzi = hanzi
        self.pinyin = pinyin


# ── Seasonal Strength Tables ────────────────────────────────────────────
#
# Each element has a seasonal relationship with each month branch.
# The month branch represents the dominant energy of the season.
#
# Stages (traditional 十二长生 simplified to 4 levels):
#   PROSPEROUS (旺) = element is in season, strongest (+3)
#   STRONG (相)     = element is supported by the season (+1)
#   RESTING (休)    = element is neutral, resting (0)
#   IMPRISONED (囚) = element is weakened (-1)
#   DEAD (死)       = element is at its weakest (-2)

# Map: month branch → which element is prosperous (旺) in that month
# Spring (Yin/Mao/Chen) → Wood prospers
# Summer (Si/Wu/Wei) → Fire prospers
# Late Summer (transition months Chen/Wei/Xu/Chou) → Earth prospers
# Autumn (Shen/You/Xu) → Metal prospers
# Winter (Hai/Zi/Chou) → Water prospers

MONTH_PROSPEROUS_ELEMENT: dict[EarthlyBranch, Element] = {
    EarthlyBranch.YIN: Element.WOOD,  # Early spring
    EarthlyBranch.MAO: Element.WOOD,  # Mid spring
    EarthlyBranch.CHEN: Element.EARTH,  # Late spring (Earth transition)
    EarthlyBranch.SI: Element.FIRE,  # Early summer
    EarthlyBranch.WU_BRANCH: Element.FIRE,  # Mid summer (午 Horse)
    EarthlyBranch.WEI: Element.EARTH,  # Late summer (Earth transition)
    EarthlyBranch.SHEN: Element.METAL,  # Early autumn
    EarthlyBranch.YOU: Element.METAL,  # Mid autumn
    EarthlyBranch.XU: Element.EARTH,  # Late autumn (Earth transition)
    EarthlyBranch.HAI: Element.WATER,  # Early winter
    EarthlyBranch.ZI: Element.WATER,  # Mid winter
    EarthlyBranch.CHOU: Element.EARTH,  # Late winter (Earth transition)
}


def _get_seasonal_score(element: Element, month_branch: EarthlyBranch) -> int:
    """Get the seasonal strength score for an element in a given month.

    Uses the Wu Xing cycle relationships:
    - Same as prosperous element → PROSPEROUS (+3)
    - Produced by prosperous element → STRONG (+1)
    - Produces prosperous element (drained) → RESTING (0)
    - Controlled by prosperous element → IMPRISONED (-1)
    - Controls prosperous element (exhausting) → DEAD (-2)

    Args:
        element: The element to evaluate
        month_branch: The month branch (determines the season)

    Returns:
        Score from -2 to +3
    """
    prosperous = MONTH_PROSPEROUS_ELEMENT[month_branch]

    if element == prosperous:
        return 3  # PROSPEROUS — in season
    elif prosperous.produces == element:
        return 1  # STRONG — produced by season
    elif element.produces == prosperous:
        return 0  # RESTING — drained by season
    elif prosperous.controls == element:
        return -1  # IMPRISONED — controlled by season
    elif element.controls == prosperous:
        return -2  # DEAD — exhausting to fight the season

    # Should never reach here with 5 elements
    return 0


def _count_roots(chart: "BaZiChart", day_master_element: Element) -> float:
    """Calculate weighted root strength from branch hidden stems.

    A "root" (根) is when the Day Master's element appears as a hidden
    stem in any of the four branches. Root position matters:

    - Day branch (坐下, "sitting beneath"): weight 1.5 — YOUR branch,
      the strongest possible root
    - Month branch (月支, "command"): weight 1.2 — seasonal authority
    - Hour branch (时支): weight 0.8 — children/future pillar
    - Year branch (年支): weight 0.6 — ancestors/distant pillar

    Within each branch, the hidden stem position also matters:
    - Main qi (本气): full weight — primary energy
    - Middle qi (中气): 60% weight — secondary
    - Residual qi (余气): 30% weight — trace energy

    Args:
        chart: The BaZi chart
        day_master_element: The Day Master's element

    Returns:
        Weighted root score (typically 0-6)
    """
    # Pillar weights by position (Day is most significant)
    pillar_weights = [0.6, 1.2, 1.5, 0.8]  # year, month, day, hour

    # Hidden stem position weights (main > middle > residual)
    position_weights = [1.0, 0.6, 0.3]

    total = 0.0
    for pillar, p_weight in zip(chart.pillars, pillar_weights, strict=True):
        hidden_stems = pillar.branch.get_hidden_stem_objects()
        for i, hidden_stem in enumerate(hidden_stems):
            if hidden_stem.element == day_master_element:
                h_weight = position_weights[i] if i < len(position_weights) else 0.2
                total += p_weight * h_weight

    return total


def _count_support_drain(
    chart: "BaZiChart",
) -> tuple[int, int]:
    """Count supporting vs draining elements in the chart.

    Supporting categories (help the Day Master):
    - Self/Companion (比劫) — same element
    - Resource (印星) — produces the Day Master

    Draining categories (weaken the Day Master):
    - Output (食伤) — Day Master produces (energy flows out)
    - Wealth (财星) — Day Master controls (effort to control)
    - Power (官杀) — controls Day Master (pressure)

    Args:
        chart: The BaZi chart

    Returns:
        Tuple of (support_count, drain_count) from Ten Gods analysis
    """
    relations = analyze_ten_gods(chart, include_hidden=True)
    categories = count_ten_god_categories(relations)

    support = (
        categories.get("Self", 0)
        + categories.get("Companion", 0)
        + categories.get("Resource", 0)
    )
    drain = (
        categories.get("Output", 0)
        + categories.get("Wealth", 0)
        + categories.get("Power", 0)
    )

    return support, drain


@dataclass(frozen=True)
class StrengthAnalysis:
    """Complete Day Master strength analysis result."""

    day_master: HeavenlyStem
    day_master_element: Element
    strength: DayMasterStrength
    score: float

    # Component scores
    seasonal_score: int
    root_count: float
    support_count: int
    drain_count: int
    month_branch: EarthlyBranch

    @property
    def is_strong(self) -> bool:
        """Whether the Day Master is considered strong (旺 or 极旺)."""
        return self.strength in (
            DayMasterStrength.VERY_STRONG,
            DayMasterStrength.STRONG,
        )

    @property
    def is_weak(self) -> bool:
        """Whether the Day Master is considered weak (弱 or 极弱)."""
        return self.strength in (DayMasterStrength.VERY_WEAK, DayMasterStrength.WEAK)

    @property
    def favorable_elements(self) -> list[Element]:
        """Elements that are favorable for this Day Master.

        If strong: needs Output, Wealth, Power to drain excess
        If weak: needs Companion, Resource to build strength
        """
        dm = self.day_master_element
        if self.is_strong:
            # Strong DM benefits from being drained/controlled
            return [dm.produces, dm.controls, dm.controlled_by]
        else:
            # Weak DM benefits from support
            return [dm, dm.produced_by]

    @property
    def unfavorable_elements(self) -> list[Element]:
        """Elements that are unfavorable for this Day Master.

        Opposite of favorable.
        """
        dm = self.day_master_element
        if self.is_strong:
            return [dm, dm.produced_by]
        else:
            return [dm.produces, dm.controls, dm.controlled_by]

    def to_dict(self) -> dict:
        """Export to JSON-serializable dictionary."""
        return {
            "day_master": {
                "stem": self.day_master.hanzi,
                "element": self.day_master_element.english,
                "pinyin": self.day_master.pinyin,
            },
            "strength": {
                "classification": self.strength.english,
                "hanzi": self.strength.hanzi,
                "score": round(self.score, 2),
            },
            "factors": {
                "seasonal_score": self.seasonal_score,
                "root_count": round(self.root_count, 2),
                "support_count": self.support_count,
                "drain_count": self.drain_count,
            },
            "is_strong": self.is_strong,
            "favorable_elements": [e.english for e in self.favorable_elements],
            "unfavorable_elements": [e.english for e in self.unfavorable_elements],
        }

    def display(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Day Master: {self.day_master.hanzi} ({self.day_master_element.english} "
            f"{self.day_master.polarity.value})",
            f"Strength: {self.strength.hanzi} ({self.strength.english}) "
            f"[score: {self.score:.1f}]",
            "",
            "Factors:",
            f"  Seasonal: {self.seasonal_score:+d} "
            f"({self.day_master_element.english} in "
            f"{self.month_branch.pinyin} month)",
            f"  Roots: {self.root_count:.1f} "
            f"(weighted hidden stems matching {self.day_master_element.english})",
            f"  Support: {self.support_count} (Self + Companion + Resource)",
            f"  Drain: {self.drain_count} (Output + Wealth + Power)",
            "",
            f"Favorable: {', '.join(e.english for e in self.favorable_elements)}",
            f"Unfavorable: {', '.join(e.english for e in self.unfavorable_elements)}",
        ]
        return "\n".join(lines)


def analyze_strength(chart: "BaZiChart") -> StrengthAnalysis:
    """Analyze the Day Master's strength in the chart.

    This is the main entry point for strength analysis.

    Args:
        chart: A calculated BaZiChart

    Returns:
        Complete StrengthAnalysis with classification and component scores

    Example:
        >>> from stellium.chinese import BaZiEngine
        >>> engine = BaZiEngine(timezone_offset_hours=8)
        >>> chart = engine.calculate(datetime(1990, 5, 15, 10, 30))
        >>> result = analyze_strength(chart)
        >>> print(result.display())
    """
    day_master = chart.day_master
    dm_element = day_master.element
    month_branch = chart.month.branch

    # Factor 1: Seasonal strength
    seasonal = _get_seasonal_score(dm_element, month_branch)

    # Factor 2: Root count
    roots = _count_roots(chart, dm_element)

    # Factor 3 & 4: Support vs drain
    support, drain = _count_support_drain(chart)

    # Calculate weighted score
    # Seasonal is most important (traditional weighting)
    # Roots provide stability
    # Net support/drain is the balance
    score = (
        seasonal * 2.0  # Season is weighted double
        + roots * 1.5  # Each root is significant
        + (support - drain) * 0.5  # Net balance
    )

    # Classify
    if score >= 6.0:
        strength = DayMasterStrength.VERY_STRONG
    elif score >= 2.0:
        strength = DayMasterStrength.STRONG
    elif score >= -2.0:
        strength = DayMasterStrength.MODERATE
    elif score >= -6.0:
        strength = DayMasterStrength.WEAK
    else:
        strength = DayMasterStrength.VERY_WEAK

    return StrengthAnalysis(
        day_master=day_master,
        day_master_element=dm_element,
        strength=strength,
        score=score,
        seasonal_score=seasonal,
        root_count=roots,
        support_count=support,
        drain_count=drain,
        month_branch=month_branch,
    )
