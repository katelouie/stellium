"""
Orb Calculation Engines.

These engines implement the OrbEngine protocol to provide
different systems for calculating aspect orbs.
"""

from stellium.core.models import CelestialPosition
from stellium.core.registry import ASPECT_REGISTRY

# --- Engine 1: The Simple Default ---


class SimpleOrbEngine:
    """
    Implements OrbEngine for simple, aspect-based orbs.

    This engine uses a single dictionary mapping an aspect name to an orb value,
    regardless of the planets involved.

    This is the default engine used by ChartBuilder.
    """

    def __init__(
        self, orb_map: dict[str, float] | None = None, fallback_orb: float | None = None
    ) -> None:
        """
        Args:
            orb_map: A dictionary of {aspect_name: orb_value}. If None, uses
                default orbs from the aspect registry.
            fallback_orb: Configurable default orb for unmapped aspects
        """
        # Use registry default orbs if no custom map provided
        self._orbs = orb_map or {
            aspect_info.name: aspect_info.default_orb
            for aspect_info in ASPECT_REGISTRY.values()
        }
        self._default_orb = fallback_orb or 2.0  # Fallback for unlisted aspects

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """Gets the orb for the given aspect name. Ignores the planets."""
        return self._orbs.get(aspect_name, self._default_orb)


# --- Engine 2: An Advanced Example ---


class LuminariesOrbEngine:
    """
    Implements OrbEngine with special rules for Luminaries.

    This is a common system where aspects to the Sun or Moon
    are given a wider orb than aspects to other planets.
    """

    def __init__(
        self,
        luminary_orbs: dict[str, float] | None = None,
        default_orbs: dict[str, float] | None = None,
        fallback_orb: int | None = None,
    ) -> None:
        self._luminary_orbs = luminary_orbs or {
            "Conjunction": 10.0,
            "Sextile": 8.0,
            "Square": 10.0,
            "Trine": 10.0,
            "Opposition": 10.0,
        }
        self._default_orbs = default_orbs or {
            "Conjunction": 8.0,
            "Sextile": 6.0,
            "Square": 8.0,
            "Trine": 8.0,
            "Opposition": 8.0,
        }
        self._default_orb = fallback_orb or 2.0

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """Gets the orb, checking if a luminary is involved."""
        lum_names = ("Sun", "Moon")
        is_luminary = obj1.name in lum_names or obj2.name in lum_names

        if is_luminary:
            return self._luminary_orbs.get(aspect_name, self._default_orb)

        return self._default_orbs.get(aspect_name, self._default_orb)


# --- Engine 3: The "Full Complexity" Solution ---
class ComplexOrbEngine:
    """
    Implements OrbEngine with a cascading priority matrix.

    This engine can handle the most complex traditions by allowing
    orbs to be defined by pair, by single planet, or by aspect.

    The config is a nested dictionary defining the priority.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config: A nested dict defining orb priorities.
            Example:
            {
                "by_pair": {
                    "Sun-Moon": {"Square": 10.0, "default": 8.0},
                    "Mars-Saturn": {"Square": 6.0, "default": 5.0}
                },
                "by_planet": {
                    "Sun": {"default": 8.0},
                    "Moon": {"default": 8.0},
                    "Saturn": {"Square": 5.0, "default": 4.0}
                },
                "by_aspect": {
                    "Square": 7.0,
                    "Trine": 7.0
                },
                "default": 3.0
            }
        """
        self._config = config
        self._fallback_default_orb = 2.0

    def _normalize_pair_keys(self) -> None:
        """Normalizes the 'by_pair' keys to be sorted alphabetically. Ensures 'Sun-Moon'
        and 'Moon-Sun' are treated as the same. This is called once at init to make lookups fast.
        """
        if "by_pair" not in self._config:
            return

        normalized_pairs = {}
        for key, rules in self._config["by_pair"].items():
            try:
                # Split the key
                obj1, obj2 = key.split("-")
                # Create the new, sorted key
                new_key = self._get_pair_key(obj1, obj2)
                normalized_pairs[new_key] = rules
            except ValueError:
                # Handle invalid keys gracefully, e.g., "Sun" or "Sun-Moon-Mars"
                print(f"Warning: Invalid 'by_pair' key format '{key}'. Skipping.")

    def _get_pair_key(self, obj1_name: str, obj2_name: str) -> str:
        """Creates a consistent, sorted key (e.g., "Moon-Sun")"""
        return "-".join(sorted([obj1_name, obj2_name]))

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """Finds the most specific orb available based on priority."""

        # This key is now guaranteed to match the normalized config keys
        pair_key = self._get_pair_key(obj1.name, obj2.name)

        # 1. Check for specific pair + specific aspect
        # This lookup is now safe, "Sun-Moon" and "Moon-Sun" both work.
        pair_rules = self._config.get("by_pair", {}).get(pair_key)
        if pair_rules:
            if aspect_name in pair_rules:
                return pair_rules[aspect_name]
            if "default" in pair_rules:
                return pair_rules["default"]

        # 2. Check for single planet rules (highest priority wins)
        # (e.g., if Sun has 8° and Saturn has 4°, use 8°)
        orb = -1.0  # Start with an invalid orb
        planet_rules_o1 = self._config.get("by_planet", {}).get(obj1.name)
        planet_rules_o2 = self._config.get("by_planet", {}).get(obj2.name)

        if planet_rules_o1:
            orb = max(orb, planet_rules_o1.get(aspect_name, -1.0))
            orb = max(orb, planet_rules_o1.get("default", -1.0))

        if planet_rules_o2:
            orb = max(orb, planet_rules_o2.get(aspect_name, -1.0))
            orb = max(orb, planet_rules_o2.get("default", -1.0))

        if orb > -1.0:
            return orb  # We found a planet-specific rule

        # 3. Check for default aspect rule
        aspect_orb = self._config.get("by_aspect", {}).get(aspect_name)
        if aspect_orb:
            return aspect_orb

        # 4. Return the final fallback
        return self._config.get("default", self._fallback_default_orb)
