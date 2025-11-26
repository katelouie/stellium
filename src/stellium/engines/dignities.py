"""Dignity calculation engines.

This module provides comprehensive essential dignity calculations for both
traditional (pre-1781) and modern astrological systems. It evaluates planetary
strength through rulership, exaltation, detriment, fall, triplicity, terms/bounds,
faces/decans, and mutual reception.
"""

from typing import Any

from stellium.core.models import CelestialPosition

DIGNITIES = {
    "Aries": {
        "symbol": "♈︎",
        "element": "Fire",
        "modality": "Cardinal",
        "exaltation_degree": 19,
        "traditional": {
            "ruler": "Mars",
            "exaltation": "Sun",
            "detriment": "Venus",
            "fall": "Saturn",
        },
        "modern": {
            "ruler": "Mars",
            "exaltation": "Sun",
            "detriment": "Venus",
            "fall": "Saturn",
        },
        "decan_trip": ["Mars", "Sun", "Jupiter"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": {  # key is start of the planet's domicile degrees.
            0: "Jupiter",
            6: "Venus",
            12: "Mercury",
            20: "Mars",
            25: "Saturn",
        },
        "triplicity": {"day": "Sun", "night": "Jupiter", "coop": "Saturn"},
    },
    "Taurus": {
        "symbol": "♉︎",
        "element": "Earth",
        "modality": "Fixed",
        "exaltation_degree": 3,
        "traditional": {
            "ruler": "Venus",
            "exaltation": "Moon",
            "detriment": "Mars",
            "fall": None,
        },
        "modern": {
            "ruler": "Venus",
            "exaltation": "Moon",
            "detriment": "Pluto",
            "fall": "Uranus",
        },
        "decan_trip": ["Venus", "Mercury", "Saturn"],
        "decan_chaldean": ["Mecury", "Moon", "Saturn"],
        "bound_egypt": {  # key is start of the planet's domicile degrees.
            0: "Venus",
            8: "Mercury",
            14: "Jupiter",
            22: "Saturn",
            27: "Mars",
        },
        "triplicity": {"day": "Venus", "night": "Moon", "coop": "Mars"},
    },
    "Gemini": {
        "symbol": "♊︎",
        "element": "Air",
        "modality": "Mutable",
        "exaltation_degree": 3,
        "traditional": {
            "ruler": "Mercury",
            "exaltation": "North Node",
            "detriment": "Jupiter",
            "fall": "South Node",
        },
        "modern": {
            "ruler": "Mercury",
            "exaltation": "Mercury",
            "detriment": "Jupiter",
            "fall": "Venus",
        },
        "decan_trip": ["Mercury", "Venus", "Saturn"],
        "decan_chaldean": ["Jupiter", "Mars", "Sun"],
        "bound_egypt": {  # key is start of the planet's domicile degrees.
            0: "Mercury",
            6: "Jupiter",
            12: "Venus",
            17: "Mars",
            24: "Saturn",
        },
        "triplicity": {"day": "Saturn", "night": "Mercury", "coop": "Jupiter"},
    },
    "Cancer": {
        "symbol": "♋︎",
        "element": "Water",
        "modality": "Cardinal",
        "exaltation_degree": 15,
        "traditional": {
            "ruler": "Moon",
            "exaltation": "Jupiter",
            "detriment": "Saturn",
            "fall": "Mars",
        },
        "modern": {
            "ruler": "Moon",
            "exaltation": "Jupiter",
            "detriment": "Saturn",
            "fall": "Pluto",
        },
        "decan_trip": ["Moon", "Mars", "Jupiter"],
        "decan_chaldean": ["Venus", "Mercury", "Moon"],
        "bound_egypt": {
            0: "Mars",
            7: "Venus",
            13: "Mercury",
            19: "Jupiter",
            26: "Saturn",
        },
        "triplicity": {"day": "Mars", "night": "Venus", "coop": "Moon"},
    },
    "Leo": {
        "symbol": "♌︎",
        "element": "Fire",
        "modality": "Fixed",
        "exaltation_degree": None,
        "traditional": {
            "ruler": "Sun",
            "exaltation": "None",
            "detriment": "Saturn",
            "fall": "None",
        },
        "modern": {
            "ruler": "Sun",
            "exaltation": "Neptune",
            "detriment": "Uranus",
            "fall": "Pluto",
        },
        "decan_trip": ["Sun", "Jupiter", "Mars"],
        "decan_chaldean": ["Saturn", "Jupiter", "Mars"],
        "bound_egypt": {
            0: "Jupiter",
            6: "Venus",
            11: "Saturn",
            18: "Mercury",
            24: "Mars",
        },
        "triplicity": {"day": "Sun", "night": "Jupiter", "coop": "Saturn"},
    },
    "Virgo": {
        "symbol": "♍︎",
        "element": "Earth",
        "modality": "Mutable",
        "exaltation_degree": 15,
        "traditional": {
            "ruler": "Mercury",
            "exaltation": "Mercury",
            "detriment": "Jupiter",
            "fall": "Venus",
        },
        "modern": {
            "ruler": "Mercury",
            "exaltation": "Mercury",
            "detriment": "Neptune",
            "fall": "Venus",
        },
        "decan_trip": ["Mercury", "Saturn", "Venus"],
        "decan_chaldean": ["Sun", "Venus", "Mercury"],
        "bound_egypt": {
            0: "Mercury",
            7: "Venus",
            17: "Jupiter",
            21: "Mars",
            28: "Saturn",
        },
        "triplicity": {"day": "Venus", "night": "Moon", "coop": "Mars"},
    },
    "Libra": {
        "symbol": "♎︎",
        "element": "Air",
        "modality": "Cardinal",
        "exaltation_degree": 21,
        "traditional": {
            "ruler": "Venus",
            "exaltation": "Saturn",
            "detriment": "Mars",
            "fall": "Sun",
        },
        "modern": {
            "ruler": "Venus",
            "exaltation": "Saturn",
            "detriment": "Mars",
            "fall": "Sun",
        },
        "decan_trip": ["Venus", "Saturn", "Jupiter"],
        "decan_chaldean": ["Moon", "Saturn", "Jupiter"],
        "bound_egypt": {
            0: "Saturn",
            6: "Mercury",
            14: "Jupiter",
            21: "Venus",
            28: "Mars",
        },
        "triplicity": {"day": "Saturn", "night": "Mercury", "coop": "Jupiter"},
    },
    "Scorpio": {
        "symbol": "♏︎",
        "element": "Water",
        "modality": "Fixed",
        "exaltation_degree": None,
        "traditional": {
            "ruler": "Mars",
            "exaltation": "None",
            "detriment": "Venus",
            "fall": "Moon",
        },
        "modern": {
            "ruler": "Pluto",
            "exaltation": "Uranus",
            "detriment": "Venus",
            "fall": "Moon",
        },
        "decan_trip": ["Mars", "Sun", "Venus"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": {
            0: "Mars",
            7: "Venus",
            11: "Mercury",
            19: "Jupiter",
            24: "Saturn",
        },
        "triplicity": {"day": "Mars", "night": "Venus", "coop": "Moon"},
    },
    "Sagittarius": {
        "symbol": "♐︎",
        "element": "Fire",
        "modality": "Mutable",
        "exaltation_degree": 3,
        "traditional": {
            "ruler": "Jupiter",
            "exaltation": "South Node",
            "detriment": "Mercury",
            "fall": "North Node",
        },
        "modern": {
            "ruler": "Jupiter",
            "exaltation": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres",
        },
        "decan_trip": ["Jupiter", "Mars", "Sun"],
        "decan_chaldean": ["Mercury", "Moon", "Saturn"],
        "bound_egypt": {
            0: "Jupiter",
            12: "Venus",
            17: "Mercury",
            21: "Mars",
            26: "Saturn",
        },
        "triplicity": {"day": "Sun", "night": "Jupiter", "coop": "Saturn"},
    },
    "Capricorn": {
        "symbol": "♑︎",
        "element": "Earth",
        "modality": "Cardinal",
        "exaltation_degree": 27,
        "traditional": {
            "ruler": "Saturn",
            "exaltation": "Mars",
            "detriment": "Moon",
            "fall": "Jupiter",
        },
        "modern": {
            "ruler": "Saturn",
            "exaltation": "Mars",
            "detriment": "Moon",
            "fall": "Jupiter",
        },
        "decan_trip": ["Saturn", "Venus", "Mercury"],
        "decan_chaldean": ["Jupiter", "Mars", "Sun"],
        "bound_egypt": {
            0: "Mercury",
            7: "Jupiter",
            14: "Venus",
            22: "Saturn",
            26: "Mars",
        },
        "triplicity": {"day": "Venus", "night": "Moon", "coop": "Mars"},
    },
    "Aquarius": {
        "symbol": "♒︎",
        "element": "Air",
        "modality": "Fixed",
        "exaltation_degree": None,
        "traditional": {
            "ruler": "Saturn",
            "exaltation": "None",
            "detriment": "Sun",
            "fall": "None",
        },
        "modern": {
            "ruler": "Uranus",
            "exaltation": "Pluto",
            "detriment": "Sun",
            "fall": "Neptune",
        },
        "decan_trip": ["Saturn", "Mercury", "Venus"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": {
            0: "Mercury",
            7: "Venus",
            13: "Jupiter",
            20: "Saturn",
            25: "Mars",
        },
        "triplicity": {"day": "Saturn", "night": "Mercury", "coop": "Jupiter"},
    },
    "Pisces": {
        "symbol": "♓︎",
        "element": "Water",
        "modality": "Mutable",
        "exaltation_degree": 27,
        "traditional": {
            "ruler": "Jupiter",
            "exaltation": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres",
        },
        "modern": {
            "ruler": "Neptune",
            "exaltation": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres",
        },
        "decan_trip": ["Jupiter", "Mars", "Moon"],
        "decan_chaldean": ["Saturn", "Jupiter", "Mars"],
        "bound_egypt": {
            0: "Venus",
            12: "Jupiter",
            16: "Mercury",
            19: "Mars",
            28: "Saturn",
        },
        "triplicity": {"day": "Mars", "night": "Venus", "coop": "Moon"},
    },
}


class TraditionalDignityCalculator:
    """
    Traditional essential dignities calculator (pre-1781).

    Uses only the seven traditional planets (Sun through Saturn) and
    calculates dignities according to classical astrological principles.

    Scoring system:
    - Domicile/Rulership: +5 points
    - Exaltation: +4 points
    - Triplicity ruler: +3 points
    - Term/Bound ruler: +2 points
    - Face/Decan ruler: +1 point
    - Detriment: -5 points
    - Fall: -4 points
    - Peregrine (no dignities): 0 points
    """

    TRADITIONAL_PLANETS = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
    ]

    def __init__(self, decans: str = "chalean") -> None:
        """
        Initialize traditional dignity calculator.

        Args:
            decans: Can be either "chaldean" or "triplicity".
        """
        if decans not in ("chaldean", "triplicity"):
            raise ValueError(
                f"Decans must be either 'chaldean' or 'triplicity', got {decans}"
            )
        self.decans = decans

    @property
    def calculator_name(self) -> str:
        """Name of this calculator"""
        return "Traditional Essential Dignities"

    def calculate_dignities(
        self, position: CelestialPosition, sect: str | None = "day"
    ) -> dict[str, Any]:
        """Calculate traditional dignities for a position.

        Args:
            position: CelestialPosition to analyze
            sect: Chart sect. Can be "day" or "night" (defaults to day)

        Returns:
            Dictionary with comprehensive dignity information including:
            - dignities: List of dignity types held
            - score: Total dignity score
            - details: Breakdown of each dignity
            - is_peregrine: Whether planet is peregrine (no dignities)
            - reception_potential: Planets this one could have mutual reception with
        """
        if sect not in ("day", "night"):
            raise ValueError(f"Chart sect must be 'day' or 'night': Got {sect}")

        # Only traditional planets have dignities
        if position.name not in self.TRADITIONAL_PLANETS:
            return {
                "planet": position.name,
                "sign": position.sign,
                "system": "traditional",
                "note": "Not a traditional planet - no dignities calculated",
            }

        sign_data = DIGNITIES.get(position.sign, {})
        trad_data = sign_data.get("traditional", {})

        dignities = []
        score = 0
        details = {}

        # Rulership (+5)
        if trad_data.get("ruler") == position.name:
            dignities.append("domicile")
            score += 5
            details["domicile"] = {
                "value": 5,
                "description": f"{position.name} rules {position.sign}",
            }

        # 2. EXALTATION (+4)
        exaltation = trad_data.get("exaltation")
        if exaltation == position.name:
            dignities.append("exaltation")
            score += 4
            exalt_degree = sign_data.get("exaltation_degree")

            # Bonus if within 5° of exact exaltation degree
            exact_bonus = 0
            if exalt_degree is not None:
                distance = abs(position.sign_degree - exalt_degree)
                if distance <= 5:
                    exact_bonus = 1
                    score += 1
                    dignities.append("exaltation_exact")

            details["exaltation"] = {
                "value": 4 + exact_bonus,
                "description": f"{position.name} exalted in {position.sign}",
                "exact_degree": exalt_degree,
                "distance_from_exact": abs(position.sign_degree - exalt_degree)
                if exalt_degree
                else None,
            }

        # TRIPLICITY (+3)
        triplicity_data = sign_data.get("triplicity", {})
        triplicity_ruler = triplicity_data.get(sect)
        participating_ruler = triplicity_data.get("coop")

        if triplicity_ruler == position.name:
            dignities.append("triplicity_ruler")
            score += 3
            details["triplicity"] = {
                "value": 3,
                "description": f"{position.name} is {sect} triplicity ruler of {sign_data.get('element')} signs",
                "element": sign_data.get("element"),
            }
        elif participating_ruler == position.name:
            dignities.append("participating_ruler")
            score += 2
            details["triplicity"] = {
                "value": 2,
                "description": f"{position.name} is participating triplicity ruler of {sign_data.get('element')} signs",
                "element": sign_data.get("element"),
            }

        # TERMS/BOUNDS (+2)
        bounds = sign_data.get("bound_egypt", {})
        term_ruler = self._find_bound_ruler(position.sign_degree, bounds)

        if term_ruler == position.name:
            dignities.append("term")
            score += 2
            details["term"] = {
                "value": 2,
                "description": f"{position.name} rules the term/bound at {position.sign_degree:.1f}° {position.sign}",
            }

        # FACE/DECAN (+1)
        decan_key = f"decan_{self.decans}"
        decans = sign_data.get(decan_key, [])
        decan_index = int(
            position.sign_degree // 10
        )  # 0-9° = 0, 10-19° = 1, 20-29° = 2

        if 0 <= decan_index < len(decans):
            decan_ruler = decans[decan_index]
            if decan_ruler == position.name:
                dignities.append("decan")
                score += 1
                details["decan"] = {
                    "value": 1,
                    "description": f"{position.name} rules the {self.decans.title()} decan at {position.sign_degree:.1f}° {position.sign}",
                    "decan_number": decan_index + 1,
                }

        # DETRIMENT (-5)
        detriment = trad_data.get("detriment")
        if detriment == position.name:
            dignities.append("detriment")
            score -= 5
            details["detriment"] = {
                "value": -5,
                "description": f"{position.name} in detriment in {position.sign}",
            }

        # FALL (-4)
        fall = trad_data.get("fall")
        if fall == position.name:
            dignities.append("fall")
            score -= 4
            details["fall"] = {
                "value": -4,
                "description": f"{position.name} in fall in {position.sign}",
            }

        # PEREGRINE (0)
        positive_dignities = [d for d in dignities if d not in ["detriment", "fall"]]
        is_peregrine = len(positive_dignities) == 0

        if is_peregrine:
            dignities.append("peregrine")
            details["peregrine"] = {
                "value": 0,
                "description": f"{position.name} is peregrine (no essential dignities) in {position.sign}",
            }

        # MUTUAL RECEPTION POTENTIAL
        # Check which planets this one could have mutual reception with
        reception_potential = self._check_reception_potential(position, sign_data)

        return {
            "planet": position.name,
            "sign": position.sign,
            "degree": position.sign_degree,
            "dignities": dignities,
            "system": "traditional",
            "score": score,
            "details": details,
            "is_peregrine": is_peregrine,
            "receiption_potential": reception_potential,
            "interpretation": self._interpret_score(score, dignities),
        }

    def _find_bound_ruler(
        self, sign_degree: float, bounds: dict[int, str]
    ) -> str | None:
        """Find which planet rules the term/bound at a given degree."""
        sorted_bounds = sorted(bounds.items())

        for i, (start_degree, ruler) in enumerate(sorted_bounds):
            # Find the end of this bound
            if i < len(sorted_bounds) - 1:
                end_degree = sorted_bounds[i + 1][0]
            else:
                end_degree = 30  # End of sign

            if start_degree <= sign_degree < end_degree:
                return ruler

        return None

    def _check_reception_potential(
        self, position: CelestialPosition, sign_data: dict
    ) -> dict[str, list[str]]:
        """
        Check for mutual reception potential.

        A planet can have mutual reception by:
        - Rulership: Two planets in each other's domiciles
        - Exaltation: Two planets in each other's exaltation signs
        - Mixed: One planet in the other's domicile while that planet is in the first's exaltation
        """
        potential = {
            "by_domicile": [],
            "by_exaltation": [],
            "mixed": [],
        }

        traditional_data = sign_data.get("traditional", {})

        # Find which sign(s) this planet rules
        # my_domicile_signs = [
        #     sign
        #     for sign, data in DIGNITIES.items()
        #     if data.get("traditional", {}).get("ruler") == position.name
        # ]

        # # Find which sign(s) this planet is exalted in
        # my_exaltation_signs = [
        #     sign
        #     for sign, data in DIGNITIES.items()
        #     if data.get("traditional", {}).get("exaltation") == position.name
        # ]

        # Who rules/is exalted in my current sign?
        current_ruler = traditional_data.get("ruler")
        current_exaltation = traditional_data.get("exaltation")

        if current_ruler and current_ruler in self.TRADITIONAL_PLANETS:
            potential["by_domicile"].append(current_ruler)

        if current_exaltation and current_exaltation in self.TRADITIONAL_PLANETS:
            potential["by_exaltation"].append(current_exaltation)

            # Check for mixed reception
            if current_exaltation != current_ruler:
                potential["mixed"].append(current_exaltation)

        return potential

    def _interpret_score(self, score: int, dignities: list[str]) -> str:
        """Provide a human-readable interpretation of the dignity score."""
        if "peregrine" in dignities:
            return "Peregrine - planet lacks essential dignity and may be weakened"
        elif score >= 5:
            return "Very strong - planet has major essential dignity"
        elif score >= 3:
            return "Strong - planet has significant dignity"
        elif score >= 1:
            return "Moderately dignified - planet has minor dignity"
        elif score == 0:
            return "Neutral - no significant dignity or debility"
        elif score >= -3:
            return "Moderately challenged - planet has minor debility"
        else:
            return "Significantly challenged - planet has major debility"


class ModernDignityCalculator:
    """
    Modern essential dignities calculator (post-1781).

    Includes outer planets (Uranus, Neptune, Pluto) and uses modern
    rulership assignments. The scoring system is adapted for modern
    rulerships while maintaining traditional dignity principles.

    Scoring system:
    - Domicile/Rulership: +5 points (modern ruler), +3 points (traditional ruler)
    - Exaltation: +4 points
    - Triplicity ruler: +3 points
    - Term/Bound ruler: +2 points
    - Face/Decan ruler: +1 point
    - Detriment: -5 points (modern), -3 points (traditional)
    - Fall: -4 points
    """

    MODERN_PLANETS = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]

    def __init__(self, decans: str = "chalean") -> None:
        """
        Initialize modern dignity calculator.

        Args:
            decans: Can be either "chaldean" or "triplicity".
        """
        if decans not in ("chaldean", "triplicity"):
            raise ValueError(
                f"Decans must be either 'chaldean' or 'triplicity', got {decans}"
            )
        self.decans = decans

    @property
    def calculator_name(self) -> str:
        """Name of this calculator."""
        return "Modern Essential Dignities"

    def calculate_dignities(
        self,
        position: CelestialPosition,
        sect: str = "day",
    ) -> dict[str, Any]:
        """
        Calculate modern dignities for a position.

        Args:
            position: CelestialPosition to analyze
            is_day_chart: Whether this is a day chart (Sun above horizon).
                         Affects triplicity ruler selection.

        Returns:
            Dictionary with comprehensive dignity information.
        """
        if sect not in ("day", "night"):
            raise ValueError(f"Chart sect must be 'day' or 'night': Got {sect}")

        sign_data = DIGNITIES.get(position.sign, {})
        modern_data = sign_data.get("modern", {})
        traditional_data = sign_data.get("traditional", {})

        dignities = []
        score = 0
        details = {}

        # DOMICILE/RULERSHIP
        modern_ruler = modern_data.get("ruler")
        traditional_ruler = traditional_data.get("ruler")

        if modern_ruler == position.name:
            dignities.append("domicile_modern")
            score += 5
            details["domicile"] = {
                "value": 5,
                "description": f"{position.name} rules {position.sign} (modern rulership)",
                "type": "modern",
            }
        elif traditional_ruler == position.name and traditional_ruler != modern_ruler:
            # Traditional ruler gets partial credit in signs with modern rulers
            dignities.append("domicile_traditional")
            score += 3
            details["domicile"] = {
                "value": 3,
                "description": f"{position.name} rules {position.sign} (traditional co-ruler)",
                "type": "traditional",
            }

        # EXALTATION (+4)
        exaltation = modern_data.get("exaltation")
        if exaltation == position.name:
            dignities.append("exaltation")
            score += 4
            exalt_degree = sign_data.get("exaltation_degree")

            # Bonus if within 5 degrees of exact exaltation degree
            exact_bonus = 0
            if exalt_degree is not None:
                distance = abs(position.sign_degree - exalt_degree)
                if distance <= 5:
                    exact_bonus = 1
                    score += 1
                    dignities.append("exaltation_exact")

            details["exaltation"] = {
                "value": 4 + exact_bonus,
                "description": f"{position.name} exalted in {position.sign}",
                "exact_degree": exalt_degree,
                "distance_from_exact": abs(position.sign_degree - exalt_degree)
                if exalt_degree
                else None,
            }

        # TRIPLICITY (+3) - Uses traditional triplicity rulers
        triplicity_data = sign_data.get("triplicity", {})
        triplicity_ruler = triplicity_data.get(sect)
        participating_ruler = triplicity_data.get("coop")

        if triplicity_ruler == position.name:
            dignities.append("triplicity_ruler")
            score += 3
            details["triplicity"] = {
                "value": 3,
                "description": f"{position.name} is {sect} triplicity ruler of {sign_data.get('element')} signs",
                "element": sign_data.get("element"),
            }
        elif participating_ruler == position.name:
            dignities.append("triplicity_participating")
            score += 2
            details["triplicity"] = {
                "value": 2,
                "description": f"{position.name} is participating triplicity ruler of {sign_data.get('element')} signs",
                "element": sign_data.get("element"),
            }

        # TERM/BOUND (+2) - Only for traditional planets
        if position.name in TraditionalDignityCalculator.TRADITIONAL_PLANETS:
            bounds = sign_data.get("bound_egypt", {})
            term_ruler = self._find_bound_ruler(position.sign_degree, bounds)

            if term_ruler == position.name:
                dignities.append("term")
                score += 2
                details["term"] = {
                    "value": 2,
                    "description": f"{position.name} rules the term/bound at {position.sign_degree:.1f}° {position.sign}",
                }

        # FACE/DECAN (+1) - Only for traditional planets
        if position.name in TraditionalDignityCalculator.TRADITIONAL_PLANETS:
            decan_key = f"decan_{self.decans}"
            decans = sign_data.get(decan_key, [])
            decan_index = int(position.sign_degree // 10)

            if 0 <= decan_index < len(decans):
                decan_ruler = decans[decan_index]
                if decan_ruler == position.name:
                    dignities.append("face")
                    score += 1
                    details["face"] = {
                        "value": 1,
                        "description": f"{position.name} rules the {self.decans.title()} decan at {position.sign_degree:.1f}° {position.sign}",
                        "decan_number": decan_index + 1,
                    }

        # DETRIMENT
        modern_detriment = modern_data.get("detriment")
        traditional_detriment = traditional_data.get("detriment")

        if modern_detriment == position.name:
            dignities.append("detriment_modern")
            score -= 5
            details["detriment"] = {
                "value": -5,
                "description": f"{position.name} in detriment in {position.sign} (modern)",
                "type": "modern",
            }
        elif (
            traditional_detriment == position.name
            and traditional_detriment != modern_detriment
        ):
            dignities.append("detriment_traditional")
            score -= 3
            details["detriment"] = {
                "value": -3,
                "description": f"{position.name} in detriment in {position.sign} (traditional)",
                "type": "traditional",
            }

        # 7. FALL
        modern_fall = modern_data.get("fall")
        if modern_fall == position.name:
            dignities.append("fall")
            score -= 4
            details["fall"] = {
                "value": -4,
                "description": f"{position.name} in fall in {position.sign}",
            }

        # 8. PEREGRINE
        positive_dignities = [
            d for d in dignities if not d.startswith(("detriment", "fall"))
        ]
        is_peregrine = len(positive_dignities) == 0

        if is_peregrine:
            dignities.append("peregrine")
            details["peregrine"] = {
                "value": 0,
                "description": f"{position.name} is peregrine (no essential dignities) in {position.sign}",
            }

        # 9. MODERN CONSIDERATIONS
        # Outer planets get a dignity bonus for being in their traditional domains
        outer_planet_affinity = self._check_outer_planet_affinity(position)
        if outer_planet_affinity:
            dignities.append("generational_affinity")
            score += 1
            details["generational_affinity"] = outer_planet_affinity

        return {
            "planet": position.name,
            "sign": position.sign,
            "degree": position.sign_degree,
            "system": "modern",
            "dignities": dignities,
            "score": score,
            "details": details,
            "is_peregrine": is_peregrine,
            "interpretation": self._interpret_score(score, dignities, position.name),
        }

    def _find_bound_ruler(self, degree: float, bounds: dict[int, str]) -> str | None:
        """Find which planet rules the term/bound at a given degree."""
        sorted_bounds = sorted(bounds.items())

        for i, (start_degree, ruler) in enumerate(sorted_bounds):
            if i < len(sorted_bounds) - 1:
                end_degree = sorted_bounds[i + 1][0]
            else:
                end_degree = 30

            if start_degree <= degree < end_degree:
                return ruler

        return None

    def _check_outer_planet_affinity(
        self, position: CelestialPosition
    ) -> dict[str, Any] | None:
        """
        Check if outer planets have affinity with sign characteristics.

        Modern interpretation: outer planets express well in signs that
        share their archetypal qualities, even without formal dignity.
        """
        affinities = {
            "Uranus": {
                "signs": ["Aquarius", "Gemini", "Libra"],  # Air signs
                "reason": "Air signs support Uranian innovation and intellectual freedom",
            },
            "Neptune": {
                "signs": ["Pisces", "Cancer", "Scorpio"],  # Water signs
                "reason": "Water signs support Neptunian sensitivity and transcendence",
            },
            "Pluto": {
                "signs": ["Scorpio", "Capricorn"],  # Transformative signs
                "reason": "These signs support Plutonian depth and transformation",
            },
        }

        if position.name in affinities:
            affinity_data = affinities[position.name]
            if position.sign in affinity_data["signs"]:
                return {
                    "value": 1,
                    "description": affinity_data["reason"],
                }

        return None

    def _interpret_score(
        self, score: int, dignities: list[str], planet_name: str
    ) -> str:
        """Provide a human-readable interpretation of the dignity score."""
        is_outer = planet_name in ["Uranus", "Neptune", "Pluto"]

        if "peregrine" in dignities:
            if is_outer:
                return "Peregrine - outer planet operates through generational themes"
            return "Peregrine - planet lacks essential dignity and may be weakened"
        elif score >= 5:
            return "Very strong - planet has major essential dignity"
        elif score >= 3:
            return "Strong - planet has significant dignity"
        elif score >= 1:
            return "Moderately dignified - planet has minor dignity"
        elif score == 0:
            return "Neutral - no significant dignity or debility"
        elif score >= -3:
            return "Moderately challenged - planet has minor debility"
        else:
            return "Significantly challenged - planet has major debility"


class MutualReceptionAnalyzer:
    """
    Analyze mutual reception between planets in a chart.

    Mutual reception occurs when two planets are each in a sign ruled or
    exalted by the other. This creates a special bond and can modify the
    expression of both planets.
    """

    def __init__(self, system: str = "traditional"):
        """
        Initialize mutual reception analyzer.

        Args:
            system: Can be "modern" or "traditional"
        """
        if system not in ("modern", "traditional"):
            raise ValueError(
                f"Mutual reception system must be 'modern' or 'traditional': got {system}"
            )

        self.system = system

    def find_mutual_receptions(
        self, positions: list[CelestialPosition]
    ) -> list[dict[str, Any]]:
        """
        Find all mutual receptions in a set of positions.

        Args:
            positions: List of CelestialPosition objects to analyze

        Returns:
            List of mutual reception dictionaries with details
        """
        receptions = []

        # Check each pair of planets
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                # Check mutual reception by domicile
                sign1_data = DIGNITIES.get(pos1.sign, {})
                sign2_data = DIGNITIES.get(pos2.sign, {})

                ruler1 = sign1_data.get(self.system, {}).get("ruler")
                ruler2 = sign2_data.get(self.system, {}).get("ruler")

                if ruler1 == pos2.name and ruler2 == pos1.name:
                    receptions.append(
                        {
                            "type": "mutual_reception_domicile",
                            "planet1": pos1.name,
                            "planet2": pos2.name,
                            "planet1_sign": pos1.sign,
                            "planet2_sign": pos2.sign,
                            "strength": "strong",
                            "description": f"{pos1.name} in {pos1.sign} and {pos2.name} in {pos2.sign} are in mutual reception by domicile",
                        }
                    )

                # Check mutual reception by exaltation
                exalt1 = sign1_data.get(self.system, {}).get("exaltation")
                exalt2 = sign2_data.get(self.system, {}).get("exaltation")

                if exalt1 == pos2.name and exalt2 == pos1.name:
                    receptions.append(
                        {
                            "type": "mutual_reception_exaltation",
                            "planet1": pos1.name,
                            "planet2": pos2.name,
                            "planet1_sign": pos1.sign,
                            "planet2_sign": pos2.sign,
                            "strength": "moderate",
                            "description": f"{pos1.name} and {pos2.name} are in mutual reception by exaltation",
                        }
                    )

                # Check mixed reception (one by domicile, one by exaltation)
                if (ruler1 == pos2.name and exalt2 == pos1.name) or (
                    ruler2 == pos1.name and exalt1 == pos2.name
                ):
                    receptions.append(
                        {
                            "type": "mutual_reception_mixed",
                            "planet1": pos1.name,
                            "planet2": pos2.name,
                            "planet1_sign": pos1.sign,
                            "planet2_sign": pos2.sign,
                            "strength": "moderate",
                            "description": f"{pos1.name} and {pos2.name} are in mixed mutual reception",
                        }
                    )

        return receptions
