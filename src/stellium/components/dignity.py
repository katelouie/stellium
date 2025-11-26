"""
Dignity component for ChartBuilder.

Calculates essential and accidental dignities for all planets in a chart.
Integrates seamlessly with the ChartBuilder component system.
"""

from typing import Any

from stellium.core.models import (
    CelestialPosition,
    ChartDateTime,
    ChartLocation,
    HouseCusps,
)
from stellium.engines.dignities import (
    ModernDignityCalculator,
    MutualReceptionAnalyzer,
    TraditionalDignityCalculator,
)


def determine_sect(positions: list[CelestialPosition]) -> str:
    """Determines if a day or night chart. Returns 'day' or 'night.'

    Day chart = Sun above the horizon, between ASC and DSC (going through MC).
    """
    # Find Sun and ASC
    sun = None
    asc = None

    for pos in positions:
        if pos.name == "Sun":
            sun = pos
        elif pos.name == "ASC":
            asc = pos

        if sun and asc:
            break

    if not sun or not asc:
        return "day"  # Default to day chart if we can't determine.

    # Calculate DSC (opposite of ASC)
    dsc_long = (asc.longitude + 180) % 360

    # Check if sun is above the horizon
    if asc.longitude < dsc_long:
        # Normal case: ASC at 0°, DSC at 180°
        is_day = asc.longitude <= sun.longitude < dsc_long
    else:
        # Wrapped case: ASC at 270°, DSC at 90°
        is_day = sun.longitude >= asc.longitude or sun.longitude < dsc_long

    return "day" if is_day else "night"


class DignityComponent:
    """
    Chart component that calculates dignities for all planets.

    This follows the ChartComponent protocol and can be added to
    ChartBuilder like any other component.

    Usage:
        chart = ChartBuilder.from_native(native) \
            .add_component(DignityComponent()) \
            .calculate()

        # Access dignities
        dignities = chart.metadata.get('dignities', {})
    """

    metadata_name = "dignities"

    def __init__(
        self,
        traditional: bool = True,
        modern: bool = True,
        receptions: bool = True,
        decans: str = "triplicity",
    ) -> None:
        """
        Initialize dignity component.

        Args:
            traditional: Calculate traditional dignities
            modern: Calculate modern dignities
            receptions: Find mutual receptions
            decans: Use "chaldean" or "triplicity" decan order
        """
        self.use_traditional = traditional
        self.use_modern = modern
        self.calculate_receptions = receptions

        # Initialize calculators
        self.traditional_calc = TraditionalDignityCalculator(decans=decans)
        self.modern_calc = ModernDignityCalculator(decans=decans)
        self.traditional_reception = MutualReceptionAnalyzer(system="traditional")
        self.modern_reception = MutualReceptionAnalyzer(system="modern")

    @property
    def component_name(self) -> str:
        """Name of this component."""
        return "Essential Dignities"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate dignities for all positions.

        Note: This component doesn't return new positions - instead it
        returns an empty list and stores dignity data in metadata that
        will be attached to the CalculatedChart.

        Args:
            datetime: Chart datetime
            location: Chart location
            positions: Already calculated positions
            house_systems_map: All calculated house systems
            house_placements_map: House placements for all systems

        Returns:
            Empty list (dignities stored in metadata)
        """

        # Determine if this is a day or night chart (sect) for triplicity rulers
        sect = determine_sect(positions)

        # Calculate dignities for each planet
        dignity_results = {}

        for position in positions:
            # Skip non-planet objects
            if position.object_type.value not in ["planet", "asteroid"]:
                continue
            planet_dignities = {
                "planet": position.name,
                "sign": position.sign,
                "degree": position.sign_degree,
            }

            # Traditional dignities
            if self.use_traditional:
                trad_result = self.traditional_calc.calculate_dignities(position, sect)
                planet_dignities["traditional"] = trad_result

            # Modern dignities
            if self.use_modern:
                modern_result = self.modern_calc.calculate_dignities(position, sect)
                planet_dignities["modern"] = modern_result

            dignity_results[position.name] = planet_dignities

        # Calculate mutual receptions
        receptions = {}
        if self.calculate_receptions:
            if self.use_traditional:
                receptions["traditional"] = (
                    self.traditional_reception.find_mutual_receptions(positions)
                )
            if self.use_modern:
                receptions["modern"] = self.modern_reception.find_mutual_receptions(
                    positions
                )

        # Store results in a way that CalculatedChart can access
        # We'll attach this to the chart metadata
        self._dignity_data = {
            "planet_dignities": dignity_results,
            "mutual_receptions": receptions,
            "sect": sect,
        }

        # Components return additional positions, but dignities are metadata
        return []

    def get_metadata(self) -> dict[str, Any]:
        """
        Get calculated dignity data.

        This should be called after calculate() to retrieve results.
        """
        return getattr(self, "_dignity_data", {})


class AccidentalDignityComponent:
    """
    Chart component that calculates accidental dignities (house placement, etc).

    This should be added AFTER house systems are calculated.

    Handles multiple house systems by calculating house-dependent
    conditions for each system separately, while universal conditions
    (retrograde, cazimi, etc.) are calculated once.

    Usage:
        chart = ChartBuilder.from_native(native) \
            .add_component(AccidentalDignityComponent()) \
            .calculate()

        # Access for specific system
        sun_acc = chart.get_planet_accidental("Sun", system="Placidus")

        # Or get all systems
        sun_all = chart.get_planet_accidental("Sun")
    """

    # Angular houses (strongest)
    ANGULAR_HOUSES = [1, 10, 7, 4]

    # Succedent houses (moderate)
    SUCCEDENT_HOUSES = [2, 11, 8, 5]

    # Cadent houses (weakest)
    CADENT_HOUSES = [3, 12, 9, 6]

    # Joy placements (planet in its favored house)
    JOY_PLACEMENTS = {
        "Mercury": 1,
        "Moon": 3,
        "Venus": 5,
        "Mars": 6,
        "Sun": 9,
        "Jupiter": 11,
        "Saturn": 12,
    }

    metadata_name = "accidental_dignities"

    def __init__(self, house_system: str = "Placidus"):
        """
        Initialize accidental dignity component.

        Args:
            house_system: Which house system to use for placements
        """
        self.house_system = house_system

    @property
    def component_name(self) -> str:
        """Name of this component."""
        return "Accidental Dignities"

    def calculate(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        positions: list[CelestialPosition],
        house_systems_map: dict[str, HouseCusps],
        house_placements_map: dict[str, dict[str, int]],
    ) -> list[CelestialPosition]:
        """
        Calculate accidental dignities based on house position.

        Args:
            datetime: Chart datetime
            location: Chart location
            positions: Already calculated positions
            house_systems_map: All calculated house systems

        Returns:
            Empty list (accidental dignities stored in metadata)
        """
        accidental_results = {}

        # Find Sun for cazimi/combust calculations
        sun = next((p for p in positions if p.name == "Sun"), None)

        for position in positions:
            if position.object_type.value not in ["planet", "asteroid"]:
                continue

            planet_name = position.name

            # Structure for this planet
            planet_data = {
                "planet": planet_name,
                "score": 0,
                "by_system": {},  # House-dependent conditions per system
                "universal": {  # Conditions same for all systems
                    "score": 0,
                    "conditions": [],
                },
            }

            # HOUSE POSITION
            for system, position_map in house_placements_map.items():
                system_data = self._calculate_house_conditions(
                    position, system, position_map
                )
                planet_data["by_system"][system] = system_data

            # Calculate universal conditions (not house-dependent)
            universal = self._calculate_universal_conditions(position, sun)
            planet_data["universal"] = universal

            accidental_results[planet_name] = planet_data

        # Store results
        self._accidental_data = accidental_results

        return []

    def get_metadata(self) -> dict[str, Any]:
        """Get calculated accidental dignity data."""
        return getattr(self, "_accidental_data", {})

    def _calculate_house_conditions(
        self, position: CelestialPosition, system: str, position_map: dict[str, int]
    ) -> dict[str, Any]:
        """
        Calculate house-dependent conditions for one system.

        Args:
            position: Planet position
            system_name: House system name
            position_map: Position house mapping for this system

        Returns:
            Dict with score and conditions for this system
        """
        result = {"score": 0, "house": None, "conditions": []}

        planet_name = position.name
        house = position_map[planet_name]
        result["house"] = house

        if house:
            # Angluar/Succeedent/Cadent
            if house in self.ANGULAR_HOUSES:
                result["score"] += 5
                result["conditions"].append(
                    {
                        "type": "angular_house",
                        "value": 5,
                        "description": f"In angular house {house} ({system})",
                        "house": house,
                    }
                )
            elif house in self.SUCCEDENT_HOUSES:
                result["score"] += 3
                result["conditions"].append(
                    {
                        "type": "succedent_house",
                        "value": 3,
                        "description": f"In succedent house {house} ({system})",
                        "house": house,
                    }
                )
            else:  # Cadent
                result["score"] += 1
                result["conditions"].append(
                    {
                        "type": "cadent_house",
                        "value": 1,
                        "description": f"In cadent house {house} ({system})",
                        "house": house,
                    }
                )

            # Joy placement
            if planet_name in self.JOY_PLACEMENTS:
                joy_house = self.JOY_PLACEMENTS[planet_name]
                if house == joy_house:
                    result["score"] += 5
                    result["conditions"].append(
                        {
                            "type": "joy",
                            "value": 5,
                            "description": f"{planet_name} in its joy (house {joy_house}, {system})",
                            "house": joy_house,
                        }
                    )

        return result

    def _calculate_universal_conditions(
        self, position: CelestialPosition, sun: CelestialPosition | None
    ) -> dict[str, Any]:
        """
        Calculate universal conditions (same regardless of house system).

        Args:
            position: Planet position
            sun: Sun position (for cazimi/combust)

        Returns:
            Dict with score and conditions
        """
        result = {
            "score": 0,
            "conditions": [],
        }

        planet_name = position.name

        # Retrograde status
        if position.is_retrograde:
            result["score"] -= 5
            result["conditions"].append(
                {
                    "type": "retrograde",
                    "value": -5,
                    "description": f"{planet_name} is retrograde",
                }
            )
        else:
            result["score"] += 4
            result["conditions"].append(
                {
                    "type": "direct",
                    "value": 4,
                    "description": f"{planet_name} is direct",
                }
            )

        # CAZIMI / COMBUST / UNDER THE BEAMS (only for non-Sun planets)
        if planet_name != "Sun" and sun:
            distance_from_sun = abs(position.longitude - sun.longitude)
            if distance_from_sun > 180:
                distance_from_sun = 360 - distance_from_sun

            if distance_from_sun <= (17 / 60):  # Within 17 arc-minutes
                result["score"] += 5
                result["conditions"].append(
                    {
                        "type": "cazimi",
                        "value": 5,
                        "description": f"{planet_name} is cazimi (in heart of Sun)",
                        "distance_from_sun": distance_from_sun,
                    }
                )
            elif distance_from_sun <= 8:  # Within 8°
                result["score"] -= 4
                result["conditions"].append(
                    {
                        "type": "combust",
                        "value": -4,
                        "description": f"{planet_name} is combust ({distance_from_sun:.1f}° from Sun)",
                        "distance_from_sun": distance_from_sun,
                    }
                )
            elif distance_from_sun <= 15:  # Within 15°
                result["score"] -= 5
                result["conditions"].append(
                    {
                        "type": "under_beams",
                        "value": -5,
                        "description": f"{planet_name} is under the beams ({distance_from_sun:.1f}° from Sun)",
                        "distance_from_sun": distance_from_sun,
                    }
                )

        # SPEED (relative to average)
        speed = abs(position.speed_longitude)

        average_speeds = {
            "Moon": 13.17,  # Average is ~13° 10'
            "Sun": 0.983,  # Average is ~0° 59' (often rounded to 1.0)
            "Mercury": 1.38,  # Average is ~1° 23'
            "Venus": 1.2,  # Average is ~1° 12'
            "Mars": 0.517,  # Average is ~0° 31'
            "Jupiter": 0.083,  # Average is ~0° 05'
            "Saturn": 0.033,  # Average is ~0° 02'
            "Uranus": 0.023,  # (approx 84-year orbit)
            "Neptune": 0.017,  # (approx 165-year orbit)
            "Pluto": 0.008,  # (approx 248-year orbit)
        }

        if planet_name in average_speeds:
            avg_speed = average_speeds[planet_name]

            if speed > avg_speed * 1.2 and not position.is_retrograde:  # 20% faster
                result["score"] += 2
                result["conditions"].append(
                    {
                        "type": "swift",
                        "value": 2,
                        "description": f"{planet_name} is swift in motion ({speed:.2f}°/day)",
                        "speed": speed,
                    }
                )
            elif speed < avg_speed * 0.3 and not position.is_retrograde:  # Very slow
                result["score"] -= 2
                result["conditions"].append(
                    {
                        "type": "slow",
                        "value": -2,
                        "description": f"{planet_name} is slow in motion, possibly stationing ({speed:.2f}°/day)",
                        "speed": speed,
                    }
                )

        return result
