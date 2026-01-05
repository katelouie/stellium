"""Bazi (Four Pillars) chart data models.

A Bazi chart consists of four pillars:
- Year Pillar (年柱) - represents ancestors, early childhood
- Month Pillar (月柱) - represents parents, career
- Day Pillar (日柱) - represents self, spouse
- Hour Pillar (时柱) - represents children, later life

Each pillar has a Heavenly Stem and an Earthly Branch.

Implements the ChineseChart protocol for interoperability with other systems.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from stellium.chinese.core import (
    EarthlyBranch,
    Element,
    HeavenlyStem,
    Polarity,
)


@dataclass(frozen=True)
class Pillar:
    """A single pillar (柱) consisting of a Stem and Branch."""

    stem: HeavenlyStem
    branch: EarthlyBranch

    @property
    def hanzi(self) -> str:
        """The two-character Chinese representation."""
        return f"{self.stem.hanzi}{self.branch.hanzi}"

    @property
    def pinyin(self) -> str:
        """Pinyin romanization."""
        return f"{self.stem.pinyin} {self.branch.pinyin}"

    @property
    def stem_element(self) -> Element:
        """The element of the stem (primary element of the pillar)."""
        return self.stem.element

    @property
    def branch_element(self) -> Element:
        """The element of the branch."""
        return self.branch.element

    @property
    def animal(self) -> str:
        """The zodiac animal of the branch."""
        return self.branch.animal

    @property
    def hidden_stems(self) -> list[HeavenlyStem]:
        """The hidden stems (藏干) within the branch."""
        return self.branch.get_hidden_stem_objects()

    def to_dict(self) -> dict[str, Any]:
        """Export pillar data as a dictionary."""
        return {
            "hanzi": self.hanzi,
            "pinyin": self.pinyin,
            "stem": {
                "name": self.stem.name,
                "hanzi": self.stem.hanzi,
                "pinyin": self.stem.pinyin,
                "element": self.stem.element.english,
                "polarity": self.stem.polarity.value,
            },
            "branch": {
                "name": self.branch.name,
                "hanzi": self.branch.hanzi,
                "pinyin": self.branch.pinyin,
                "animal": self.branch.animal,
                "element": self.branch.element.english,
                "polarity": self.branch.polarity.value,
                "hidden_stems": [
                    {"name": s.name, "hanzi": s.hanzi, "element": s.element.english}
                    for s in self.hidden_stems
                ],
            },
        }

    def __str__(self) -> str:
        return f"{self.hanzi} ({self.stem.pinyin} {self.branch.animal})"

    def __repr__(self) -> str:
        return f"Pillar({self.hanzi}, {self.stem.element.english} {self.branch.animal})"


@dataclass(frozen=True)
class BaZiChart:
    """A complete Four Pillars (Bazi / 八字) chart.

    The Day Stem represents the "Day Master" (日主), which is the self.

    Implements the ChineseChart protocol.
    """

    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar
    birth_datetime: datetime

    # =========================================================================
    # ChineseChart Protocol Implementation
    # =========================================================================

    @property
    def system_name(self) -> str:
        """The name of this system."""
        return "Bazi"

    def element_counts(self, include_hidden: bool = False) -> dict[Element, int]:
        """Count occurrences of each element across stems and branches.

        Args:
            include_hidden: If True, includes hidden stems in the count.
                           Hidden stems are weighted: main=1.0, middle=0.5, residual=0.3

        Note: For weighted hidden stem analysis, use element_strength() instead.
        """
        elements: list[Element] = []

        # Count stem elements
        for stem in self.all_stems:
            elements.append(stem.element)

        # Count branch elements
        for branch in self.all_branches:
            elements.append(branch.element)

        if include_hidden:
            # Add hidden stem elements
            for pillar in self.pillars:
                for hidden_stem in pillar.hidden_stems:
                    elements.append(hidden_stem.element)

        return dict(Counter(elements))

    def to_dict(self) -> dict[str, Any]:
        """Export chart data as a dictionary (JSON-serializable)."""
        return {
            "system": self.system_name,
            "birth_datetime": self.birth_datetime.isoformat(),
            "eight_characters": self.hanzi,
            "day_master": {
                "stem": self.day_master.name,
                "hanzi": self.day_master.hanzi,
                "element": self.day_master_element.english,
            },
            "pillars": {
                "year": self.year.to_dict(),
                "month": self.month.to_dict(),
                "day": self.day.to_dict(),
                "hour": self.hour.to_dict(),
            },
            "element_counts": {
                elem.english: count for elem, count in self.element_counts().items()
            },
            "polarity_counts": {
                pol.value: count for pol, count in self.polarity_counts().items()
            },
        }

    def display(self) -> str:
        """Human-readable prose display of the chart."""
        dm = self.day_master
        lines = [
            f"Bazi Chart: {self.hanzi}",
            f"Day Master: {dm.hanzi} ({dm.pinyin}) - {dm.element.english} {dm.polarity.value}",
            "",
            "Four Pillars:",
            f"  Year:  {self.year.hanzi} ({self.year.stem.element.english} {self.year.branch.animal})",
            f"  Month: {self.month.hanzi} ({self.month.stem.element.english} {self.month.branch.animal})",
            f"  Day:   {self.day.hanzi} ({self.day.stem.element.english} {self.day.branch.animal})",
            f"  Hour:  {self.hour.hanzi} ({self.hour.stem.element.english} {self.hour.branch.animal})",
        ]
        return "\n".join(lines)

    # =========================================================================
    # Bazi-Specific Properties and Methods
    # =========================================================================

    @property
    def day_master(self) -> HeavenlyStem:
        """The Day Master (日主) - the stem that represents the self."""
        return self.day.stem

    @property
    def day_master_element(self) -> Element:
        """The element of the Day Master."""
        return self.day_master.element

    @property
    def pillars(self) -> tuple[Pillar, Pillar, Pillar, Pillar]:
        """All four pillars in order: year, month, day, hour."""
        return (self.year, self.month, self.day, self.hour)

    @property
    def all_stems(self) -> tuple[HeavenlyStem, ...]:
        """All four heavenly stems."""
        return tuple(p.stem for p in self.pillars)

    @property
    def all_branches(self) -> tuple[EarthlyBranch, ...]:
        """All four earthly branches."""
        return tuple(p.branch for p in self.pillars)

    def polarity_counts(self) -> dict[Polarity, int]:
        """Count Yin vs Yang across all stems and branches."""
        polarities: list[Polarity] = []

        for stem in self.all_stems:
            polarities.append(stem.polarity)
        for branch in self.all_branches:
            polarities.append(branch.polarity)

        return dict(Counter(polarities))

    @property
    def hanzi(self) -> str:
        """The eight characters (八字) in Chinese."""
        return "".join(p.hanzi for p in self.pillars)

    @property
    def all_hidden_stems(self) -> list[HeavenlyStem]:
        """All hidden stems across all four pillars."""
        stems = []
        for pillar in self.pillars:
            stems.extend(pillar.hidden_stems)
        return stems

    def ten_gods(self, include_hidden: bool = True):
        """Analyze Ten Gods (十神) relationships in the chart.

        Args:
            include_hidden: Whether to include hidden stems in analysis

        Returns:
            List of TenGodRelation objects
        """
        from stellium.chinese.bazi.analysis import analyze_ten_gods

        return analyze_ten_gods(self, include_hidden=include_hidden)

    def display_detailed(self) -> str:
        """Detailed prose display including hidden stems and Ten Gods."""
        from stellium.chinese.bazi.analysis import calculate_ten_god

        dm = self.day_master
        pillar_names = ["Year", "Month", "Day", "Hour"]
        hidden_labels = ["main", "middle", "residual"]

        lines = [
            f"Bazi Chart: {self.hanzi}",
            f"Day Master: {dm.hanzi} ({dm.pinyin}) - {dm.element.english} {dm.polarity.value}",
            "",
            "Four Pillars with Ten Gods:",
        ]

        for name, pillar in zip(pillar_names, self.pillars, strict=True):
            god = calculate_ten_god(dm, pillar.stem)
            god_label = "Self" if god.hanzi == "我" else f"{god.english} ({god.hanzi})"
            lines.append(
                f"  {name}: {pillar.hanzi} - {pillar.stem.element.english} {pillar.branch.animal} "
                f"[{god_label}]"
            )

            # Hidden stems for this pillar
            if pillar.hidden_stems:
                hidden_parts = []
                for i, hs in enumerate(pillar.hidden_stems):
                    hs_god = calculate_ten_god(dm, hs)
                    label = (
                        hidden_labels[i] if i < len(hidden_labels) else f"hidden{i+1}"
                    )
                    hidden_parts.append(f"{hs.hanzi} {hs_god.hanzi} ({label})")
                lines.append(f"    Hidden: {', '.join(hidden_parts)}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.hanzi
