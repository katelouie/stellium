"""
Aspect Pattern Analyzer Engine.

Finds major aspect patterns like Grand Trines, T-Squares, Yods, Kites,
Grand Crosses, and Stelliums.
This module implements the "Analyzer" protocol.
"""

from itertools import combinations

from stellium.core.models import (
    Aspect,
    AspectPattern,
    CalculatedChart,
    CelestialPosition,
    ObjectType,
)
from stellium.engines.dignities import DIGNITIES


class AspectPatternAnalyzer:
    """
    Implements the Analyzer protocol to find major aspect patterns.
    The results are stored in chart.metadata['aspect_patterns']
    """

    def __init__(self, stellium_min: int = 3) -> None:
        """
        Create a chart analyzer to find aspect patterns.

        Args:
            stellium_min: Minimum number of planets/angles to count as a stellium (3).
        """
        self.stellium_min = stellium_min

    @property
    def analyzer_name(self) -> str:
        return "Aspect Patterns"

    @property
    def metadata_name(self) -> str:
        return "aspect_patterns"

    def analyze(self, chart: CalculatedChart) -> list[AspectPattern]:
        """
        Runs all pattern detectors and returns a list of findings
        serialized as dictionaries for metadata.
        """
        # Get the lists we'll be working with
        planets = [
            p
            for p in chart.positions
            if p.object_type in (ObjectType.PLANET, ObjectType.ANGLE)
        ]
        aspects = list(chart.aspects)

        found_patterns: list[AspectPattern] = []

        # Find all pattern types
        found_patterns.extend(self._find_grand_trines(planets, aspects))
        found_patterns.extend(self._find_t_squares(planets, aspects))
        found_patterns.extend(self._find_yods(planets, aspects))
        found_patterns.extend(self._find_grand_crosses(planets, aspects))
        found_patterns.extend(
            self._find_stelliums(planets, min_planets=self.stellium_min)
        )
        found_patterns.extend(self._find_mystic_rectangles(planets, aspects))
        found_patterns.extend(self._find_kites(planets, aspects, found_patterns))

        return found_patterns

    def _get_aspect(
        self, aspect_list: list[Aspect], p1: CelestialPosition, p2: CelestialPosition
    ) -> Aspect | None:
        """Helper to find an aspect between two specific planets."""
        for a in aspect_list:
            if (a.object1 == p1 and a.object2 == p2) or (
                a.object1 == p2 and a.object2 == p1
            ):
                return a
        return None

    def _get_element(self, sign: str) -> str | None:
        """Get the element for a sign from DIGNITIES."""
        sign_data = DIGNITIES.get(sign)
        return sign_data.get("element") if sign_data else None

    def _get_modality(self, sign: str) -> str | None:
        """Get the modality (quality) for a sign from DIGNITIES."""
        sign_data = DIGNITIES.get(sign)
        return sign_data.get("modality") if sign_data else None

    def _find_grand_trines(
        self, planets: list[CelestialPosition], aspects: list[Aspect]
    ) -> list[AspectPattern]:
        """Finds all Grand Trines (3 planets, 3 Trines)."""
        patterns = []
        trines = [a for a in aspects if a.aspect_name == "Trine"]

        for p1, p2, p3 in combinations(planets, 3):
            a1 = self._get_aspect(trines, p1, p2)
            a2 = self._get_aspect(trines, p2, p3)
            a3 = self._get_aspect(trines, p3, p1)

            if a1 and a2 and a3:
                involved_planets = [p1, p2, p3]

                # Determine element using DIGNITIES
                elements = {
                    self._get_element(p.sign)
                    for p in involved_planets
                    if self._get_element(p.sign)
                }
                element = elements.pop() if len(elements) == 1 else "Mixed"

                pattern = AspectPattern(
                    name="Grand Trine",
                    planets=involved_planets,
                    aspects=[a1, a2, a3],
                    element=element,
                    quality=None,
                )
                patterns.append(pattern)

        return patterns

    def _find_t_squares(
        self, planets: list[CelestialPosition], aspects: list[Aspect]
    ) -> list[AspectPattern]:
        """Finds all T-Squares (2 planets in Opposition, 1 Apex square to both)."""
        patterns = []
        oppositions = [a for a in aspects if a.aspect_name == "Opposition"]
        squares = [a for a in aspects if a.aspect_name == "Square"]

        for opp in oppositions:
            p1, p2 = opp.object1, opp.object2

            for apex in planets:
                if apex == p1 or apex == p2:
                    continue

                s1 = self._get_aspect(squares, apex, p1)
                s2 = self._get_aspect(squares, apex, p2)

                if s1 and s2:
                    involved_planets = [p1, p2, apex]

                    # Determine quality/modality
                    qualities = {
                        self._get_modality(p.sign)
                        for p in involved_planets
                        if self._get_modality(p.sign)
                    }
                    quality = qualities.pop() if len(qualities) == 1 else "Mixed"

                    pattern = AspectPattern(
                        name="T-Square",
                        planets=involved_planets,  # p1/p2 are opposition, apex is focal
                        aspects=[opp, s1, s2],
                        element=None,
                        quality=quality,
                    )
                    patterns.append(pattern)

        return patterns

    def _find_yods(
        self, planets: list[CelestialPosition], aspects: list[Aspect]
    ) -> list[AspectPattern]:
        """
        Finds all Yods (Finger of God): 2 planets in sextile,
        both quincunx to a third (apex) planet.
        """
        patterns = []
        sextiles = [a for a in aspects if a.aspect_name == "Sextile"]
        quincunxes = [a for a in aspects if a.aspect_name == "Quincunx"]

        for sextile in sextiles:
            p1, p2 = sextile.object1, sextile.object2

            for apex in planets:
                if apex == p1 or apex == p2:
                    continue

                q1 = self._get_aspect(quincunxes, apex, p1)
                q2 = self._get_aspect(quincunxes, apex, p2)

                if q1 and q2:
                    pattern = AspectPattern(
                        name="Yod",
                        planets=[p1, p2, apex],  # apex is the focal point
                        aspects=[sextile, q1, q2],
                        element=None,
                        quality=None,
                    )
                    patterns.append(pattern)
        return patterns

    def _find_kites(
        self,
        planets: list[CelestialPosition],
        aspects: list[Aspect],
        found_patterns: list[AspectPattern],
    ) -> list[AspectPattern]:
        """
        Finds all Kites: A Grand Trine with a 4th planet opposite one point
        and sextile to the other two.
        """
        patterns = []
        grand_trines = [p for p in found_patterns if p.name == "Grand Trine"]
        oppositions = [a for a in aspects if a.aspect_name == "Opposition"]
        sextiles = [a for a in aspects if a.aspect_name == "Sextile"]

        for gt in grand_trines:
            gt_planets = gt.planets

            # Try each planet in the Grand Trine as the opposition point
            for i, opp_point in enumerate(gt_planets):
                other_planets = [p for j, p in enumerate(gt_planets) if j != i]

                # Look for a 4th planet opposite to opp_point
                for focal in planets:
                    if focal in gt_planets:
                        continue

                    opp = self._get_aspect(oppositions, focal, opp_point)
                    if not opp:
                        continue

                    # Check if focal is sextile to the other two GT planets
                    s1 = self._get_aspect(sextiles, focal, other_planets[0])
                    s2 = self._get_aspect(sextiles, focal, other_planets[1])

                    if s1 and s2:
                        # Get element from the Grand Trine
                        element = gt.element

                        pattern = AspectPattern(
                            name="Kite",
                            planets=gt_planets + [focal],
                            aspects=gt.aspects + [opp, s1, s2],
                            element=element,
                            quality=None,
                        )
                        patterns.append(pattern)
        return patterns

    def _find_grand_crosses(
        self, planets: list[CelestialPosition], aspects: list[Aspect]
    ) -> list[AspectPattern]:
        """
        Finds all Grand Crosses: 4 planets forming 2 oppositions
        and 4 squares (all square each other).
        """
        patterns = []
        oppositions = [a for a in aspects if a.aspect_name == "Opposition"]
        squares = [a for a in aspects if a.aspect_name == "Square"]

        # Need at least 2 oppositions for a Grand Cross
        for opp1, opp2 in combinations(oppositions, 2):
            planets_set = {opp1.object1, opp1.object2, opp2.object1, opp2.object2}

            # Grand Cross needs exactly 4 planets
            if len(planets_set) != 4:
                continue

            planets_list = list(planets_set)

            # Check that all 4 planets square each other appropriately
            # There should be 4 squares total
            found_squares = []
            for p1, p2 in combinations(planets_list, 2):
                sq = self._get_aspect(squares, p1, p2)
                if sq:
                    found_squares.append(sq)

            if len(found_squares) == 4:
                # Determine quality/modality
                qualities = {
                    self._get_modality(p.sign)
                    for p in planets_list
                    if self._get_modality(p.sign)
                }
                quality = qualities.pop() if len(qualities) == 1 else "Mixed"

                pattern = AspectPattern(
                    name="Grand Cross",
                    planets=planets_list,
                    aspects=[opp1, opp2] + found_squares,
                    element=None,
                    quality=quality,
                )
                patterns.append(pattern)
        return patterns

    def _find_mystic_rectangles(
        self, planets: list[CelestialPosition], aspects: list[Aspect]
    ) -> list[AspectPattern]:
        """
        Finds all Mystic Rectangles: 2 oppositions connected by 4 trines and 2 sextiles,
        forming a rectangle.
        """
        patterns = []
        oppositions = [a for a in aspects if a.aspect_name == "Opposition"]
        trines = [a for a in aspects if a.aspect_name == "Trine"]
        sextiles = [a for a in aspects if a.aspect_name == "Sextile"]

        for opp1, opp2 in combinations(oppositions, 2):
            planets_set = {opp1.object1, opp1.object2, opp2.object1, opp2.object2}

            # Mystic Rectangle needs exactly 4 planets
            if len(planets_set) != 4:
                continue

            planets_list = list(planets_set)

            # Check for the required sextiles and trines
            found_sextiles = []
            found_trines = []

            for p1, p2 in combinations(planets_list, 2):
                sext = self._get_aspect(sextiles, p1, p2)
                if sext:
                    found_sextiles.append(sext)

                trine = self._get_aspect(trines, p1, p2)
                if trine:
                    found_trines.append(trine)

            # Mystic Rectangle should have 2 sextiles and 2 trines
            if len(found_sextiles) == 2 and len(found_trines) == 2:
                pattern = AspectPattern(
                    name="Mystic Rectangle",
                    planets=planets_list,
                    aspects=[opp1, opp2] + found_sextiles + found_trines,
                    element=None,
                    quality=None,
                )
                patterns.append(pattern)
        return patterns

    def _find_stelliums(
        self, planets: list[CelestialPosition], min_planets: int = 3
    ) -> list[AspectPattern]:
        """
        Finds all Stelliums: 3+ planets in the same sign.
        You can adjust min_planets for stricter definitions.
        """
        patterns = []

        # Group planets by sign
        sign_groups: dict[str, list[CelestialPosition]] = {}
        for planet in planets:
            if planet.sign not in sign_groups:
                sign_groups[planet.sign] = []
            sign_groups[planet.sign].append(planet)

        # Find groups with min_planets or more
        for sign, group in sign_groups.items():
            if len(group) >= min_planets:
                element = self._get_element(sign)
                quality = self._get_modality(sign)

                pattern = AspectPattern(
                    name="Stellium",
                    planets=group,
                    aspects=[],  # Stelliums are based on sign, not aspects
                    element=element,
                    quality=quality,
                )
                patterns.append(pattern)
        return patterns
