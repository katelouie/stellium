"""
Arabic Parts calculator component.

Arabic Parts (also called Lots) are calculated points based on
the distances between three chart objects. They represent themes
or areas of life.

Formula: Lot = Asc + Point2 - Point1

Many lots are "sect-aware" - they flip the formula for day vs night charts:
- Day Chart: Asc + Point2 - Point1
- Night Chart: Asc + Point1 - Point2
"""

from stellium.components.dignity import determine_sect
from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
    ObjectType,
)

# Arabic parts catalog
# Each entry defines: which points to use, whether to flip for sect
ARABIC_PARTS_CATALOG = {
    # === The 7 Hermetic / Core Hellenistic Lots ===
    "Part of Fortune": {
        "points": ["ASC", "Moon", "Sun"],
        "sect_flip": True,
        "description": "The primary lot. Body, health, material wellbeing, possessions, and the Moon's expression.",
    },
    "Part of Spirit": {
        "points": ["ASC", "Sun", "Moon"],
        "sect_flip": True,
        "description": "The inverse of Fortune. The soul, intellect, purpose, career, and the Sun's expression.",
    },
    "Part of Eros (Love)": {
        "points": ["ASC", "Venus", "Part of Spirit"],
        "sect_flip": True,
        "description": "Love, desire, affection, and sensual/romantic expression. (Note: This requires calculating Spirit first).",
    },
    "Part of Eros (Planetary)": {
        "points": ["ASC", "Venus", "Sun"],
        "sect_flip": False,
        "description": "Alternative (Ptolemaic) Lot of Love. (This was your 'Part of Love' and is a valid, non-flipping alternative).",
    },
    "Part of Necessity (Ananke)": {
        "points": ["ASC", "Mercury", "Part of Fortune"],
        "sect_flip": True,
        "description": "Constraints, fate, necessity, enemies, and struggles. (Note: Requires calculating Fortune first).",
    },
    "Part of Courage (Tolma)": {
        "points": ["ASC", "Mars", "Part of Fortune"],
        "sect_flip": True,
        "description": "Courage, boldness, action, violence, and treachery. (Note: Requires calculating Fortune first).",
    },
    "Part of Victory (Nike)": {
        "points": ["ASC", "Jupiter", "Part of Fortune"],
        "sect_flip": True,
        "description": "Victory, faith, success, honors, and associates. (Note: Requires calculating Fortune first).",
    },
    "Part of Nemesis": {
        "points": ["ASC", "Saturn", "Part of Fortune"],
        "sect_flip": True,
        "description": "Subconscious, illness, endings, debts, and that which is hidden or karmic. (Note: Requires calculating Fortune first).",
    },
    # === Family & Relationship Lots (Classical) ===
    "Part of Father": {
        "points": ["ASC", "Sun", "Saturn"],
        "sect_flip": True,
        "description": "Relationship with the father figure. (CORRECTED: Your points were right, but this lot classically flips).",
    },
    "Part of Mother": {
        "points": ["ASC", "Moon", "Venus"],
        "sect_flip": True,
        "description": "Relationship with the mother figure. (CORRECTED: Your points were ['ASC', 'Venus', 'Moon'] and sect_flip was False. This is the standard classical order).",
    },
    "Part of Marriage": {
        "points": ["ASC", "Venus", "Saturn"],
        "sect_flip": True,
        "description": "Partnership, marriage, and committed relationships. (CORRECTED: Your points were ['ASC', 'Venus', 'Jupiter']. This is the more common classical formulation).",
    },
    "Part of Children": {
        "points": ["ASC", "Jupiter", "Saturn"],
        "sect_flip": True,
        "description": "Fertility and relationship with children. (CORRECTED: Your points were ['ASC', 'Jupiter', 'Moon']. This is the standard classical formulation).",
    },
    "Part of Siblings": {
        "points": ["ASC", "Mercury", "Saturn"],
        "sect_flip": True,
        "description": "Relationship with brothers, sisters, and close kin.",
    },
    # === Life Topic Lots ===
    "Part of Action (Praxis)": {
        "points": ["ASC", "Mars", "Sun"],
        "sect_flip": True,
        "description": "Career, action, vocation, and how one's will is asserted in the world.",
    },
    "Part of Profession (User)": {
        "points": ["ASC", "MC", "Sun"],
        "sect_flip": False,
        "description": "Career, vocation, public standing. (This was your 'Part of Profession', a valid Medieval/Modern lot. Kept for posterity).",
    },
    "Part of Passion / Lust": {
        "points": ["ASC", "Venus", "Mars"],
        "sect_flip": False,
        "description": "Passion, sexual attraction, and impulse. (This was your 'Part of Eros', a common modern variant).",
    },
    "Part of Illness / Disease": {
        "points": ["ASC", "Mars", "Saturn"],
        "sect_flip": True,
        "description": "Chronic and acute health issues, matters of bodily harm.",
    },
    "Part of Death": {
        "points": ["ASC", "Saturn", "Moon"],
        "sect_flip": True,
        "description": "Matters of endings, loss, and the nature of one's death. (CORRECTED: Your points were right, but this lot classically flips).",
    },
    "Part of Debt / Bondage": {
        "points": ["ASC", "Mercury", "Saturn"],
        "sect_flip": True,
        "description": "Debts, obligations, and areas of subservience or being tied down. (Note: Identical to Part of Siblings in this formulation).",
    },
    "Part of Travel": {
        "points": ["ASC", "Mars", "Mercury"],
        "sect_flip": True,
        "description": "Journeys, movement, and travel, especially over land.",
    },
    "Part of Friends / Associates": {
        "points": ["ASC", "Mercury", "Moon"],
        "sect_flip": True,
        "description": "Friendships, alliances, and helpful associates.",
    },
    # === Planetary Lots (Exaltation-Based) ===
    # These show where a planet's "joy" or "exaltation" is rooted.
    "Part of the Sun (Exaltation)": {
        "points": ["ASC", "Sun", "Mars"],  # Sun exalted in Aries (Mars-ruled)
        "sect_flip": True,
        "description": "Glory, recognition, and public honor.",
    },
    "Part of the Moon (Exaltation)": {
        "points": ["ASC", "Moon", "Venus"],  # Moon exalted in Taurus (Venus-ruled)
        "sect_flip": True,
        "description": "Nurturing, protection, and emotional expression. (Note: Identical to Part of Mother).",
    },
    "Part of Mercury (Exaltation)": {
        "points": [
            "ASC",
            "Mercury",
            "Mercury",
        ],  # Mercury exalted in Virgo (Mercury-ruled)
        "sect_flip": False,  # Cannot flip
        "description": "Intellect, writing, speech, and technical skill.",
    },
    "Part of Venus (Exaltation)": {
        "points": [
            "ASC",
            "Venus",
            "Jupiter",
        ],  # Venus exalted in Pisces (Jupiter-ruled)
        "sect_flip": True,
        "description": "Beauty, art, grace, and refined pleasure.",
    },
    "Part of Mars (Exaltation)": {
        "points": ["ASC", "Mars", "Saturn"],  # Mars exalted in Capricorn (Saturn-ruled)
        "sect_flip": True,
        "description": "Strategy, endurance, ambition, and directed force. (Note: Identical to Part of Illness).",
    },
    "Part of Jupiter (Exaltation)": {
        "points": ["ASC", "Jupiter", "Moon"],  # Jupiter exalted in Cancer (Moon-ruled)
        "sect_flip": True,
        "description": "Growth, generosity, faith, and good fortune.",
    },
    "Part of Saturn (Exaltation)": {
        "points": ["ASC", "Saturn", "Venus"],  # Saturn exalted in Libra (Venus-ruled)
        "sect_flip": True,
        "description": "Structure, justice, discipline, and tangible results. (Note: Inverse of Part of Marriage).",
    },
}


class ArabicPartsCalculator:
    """
    Calculate Arabic Parts (Lots) for a chart.

    Arabic Parts are senstitive points calculated from the distances between three
    chart objects. They represent specific life themes.
    """

    def __init__(
        self,
        parts_to_calculate: list[str] | None = None,
        custom_parts: dict | None = None,
    ) -> None:
        """
        Initialize Arabic Parts calculator.

        Args:
            parts_to_calculate: Which parts to calculate (None=all)
            custom_parts: Additional custom parts definitions
        """
        self._catalog = ARABIC_PARTS_CATALOG.copy()
        if custom_parts:
            self._catalog.update(custom_parts)

        self._parts_to_calculate = parts_to_calculate

    @property
    def component_name(self) -> str:
        return "Arabic Parts"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate Arabic Parts.

        Args:
            datetime: Chart datetime (unused, required by protocol)
            location: Chart location (unused, required by protocol)
            positions: Already-calculated positions
            house_systems_map: House systems and House cusps
            house_placements_map: Object placement by house system

        Returns:
            List of CelestialPosition objects for each part
        """
        # Build position lookup
        pos_dict = {p.name: p for p in positions}

        # Determine chart sect
        sect = determine_sect(positions)

        # Calculate each part
        parts = []

        if self._parts_to_calculate:
            catalog_to_use = {
                k: v for k, v in self._catalog.items() if k in self._parts_to_calculate
            }
        else:
            catalog_to_use = self._catalog

        for part_name, part_config in catalog_to_use.items():
            try:
                part_position = self._calculate_single_part(
                    part_name, part_config, pos_dict, sect, parts
                )
                parts.append(part_position)
            except KeyError as e:
                # Missing required position
                print(f"Warning: Could not calculate {part_name}: missing ({e})")
                continue

        return parts

    def _calculate_single_part(
        self,
        part_name: str,
        part_config: dict,
        positions: dict[str, CelestialPosition],
        sect: str,
        parts: list[CelestialPosition],
    ) -> CelestialPosition:
        """
        Calculate a single Arabic Part.

        Args:
            part_name: Name of the part
            part_config: Configuration (points, sect_flip)
            positions: Position lookup
            sect: Chart sect ("day" or "night")
            parts: Already-calculated parts, for parts that depend on other parts

        Returns:
            CelestialPosition for the calculated part
        """
        point_names = part_config["points"]
        sect_flip = part_config["sect_flip"]

        parts_lookup = {p.name: p for p in parts}

        # Get the three points
        asc = positions.get(point_names[0]) or parts_lookup.get(point_names[0])
        point2 = positions.get(point_names[1]) or parts_lookup.get(point_names[1])
        point3 = positions.get(point_names[2]) or parts_lookup.get(point_names[2])

        if asc is None or point2 is None or point3 is None:
            raise ValueError(
                f"All points specified must already exist: {asc}, {point2}, {point3}"
            )

        # Calculate longitude based on formula and sect
        if sect == "day" or not sect_flip:
            # Day formula: ASC + Point2 - Point3
            longitude = (asc.longitude + point2.longitude - point3.longitude) % 360
        else:
            # Night formula (flipped): ASC + Point3 - Point2
            longitude = (asc.longitude + point3.longitude - point2.longitude) % 360

        # Create CelestialPosition for this part
        return CelestialPosition(
            name=part_name,
            object_type=ObjectType.ARABIC_PART,
            longitude=longitude,
        )


class PartOfFortuneCalculator:
    """
    Simplified calculator for just Part of Fortune.

    This is useful for when you only need Fortune and don't want to calculate all
    Arabic Parts.
    """

    @property
    def component_name(self) -> str:
        return "Part of Fortune"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """Calculate only Part of Fortune."""
        calculator = ArabicPartsCalculator(parts_to_calculate=["Part of Fortune"])
        return calculator.calculate(
            datetime, location, positions, house_systems_map, house_placements_map
        )
