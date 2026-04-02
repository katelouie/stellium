"""
Orb Calculation Engines.

These engines implement the OrbEngine protocol to provide
different systems for calculating aspect orbs.
"""

from typing import Literal

from stellium.core.models import CelestialPosition
from stellium.core.registry import ASPECT_REGISTRY

# ── Moiety System Defaults ──────────────────────────────────────────────
# Full orbs (moiety = half). Effective orb = (full_A + full_B) / 2.

LILLY_FULL_ORBS: dict[str, float] = {
    # Septenary — William Lilly, Christian Astrology (1647) p.107
    # Matches Bonatti (1277), Al-Biruni (1029), Sahl (820 CE)
    "Sun": 15.0,
    "Moon": 12.0,
    "Saturn": 9.0,
    "Jupiter": 9.0,
    "Mars": 8.0,
    "Venus": 7.0,
    "Mercury": 7.0,
    # Outer planets — modern rulership analogy (no classical authority)
    "Uranus": 6.0,
    "Neptune": 6.0,
    "Pluto": 5.0,
    # Minor bodies
    "Chiron": 3.0,
    "True Node": 3.0,
    "Mean Node": 3.0,
}

PTOLEMY_FULL_ORBS: dict[str, float] = {
    # Ptolemy, Tetrabiblos (2nd century CE) — divergent, larger values
    "Sun": 17.0,
    "Moon": 12.5,
    "Jupiter": 12.0,
    "Saturn": 10.0,
    "Venus": 8.0,
    "Mars": 7.5,
    "Mercury": 7.5,
    # Outer planets — same conservative defaults
    "Uranus": 6.0,
    "Neptune": 6.0,
    "Pluto": 5.0,
    "Chiron": 3.0,
    "True Node": 3.0,
    "Mean Node": 3.0,
}

MOIETY_SYSTEMS: dict[str, dict[str, float]] = {
    "lilly": LILLY_FULL_ORBS,
    "ptolemy": PTOLEMY_FULL_ORBS,
}

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


# --- Engine 4: Traditional Moiety System ---


class MoietyOrbEngine:
    """
    Implements OrbEngine using the traditional moiety (half-orb) system.

    Each planet has its own full orb value. The effective orb for an aspect
    between two planets is the average of their full orbs:

        effective_orb = (full_orb_A + full_orb_B) / 2

    This is the universal formula across all traditional sources from
    Sahl ibn Bishr (820 CE) through William Lilly (1647).

    Supports named systems ("lilly", "ptolemy") for preset values,
    or custom orb maps for full control.

    Example::

        # Default (Lilly / medieval consensus)
        engine = MoietyOrbEngine()

        # Ptolemaic (larger orbs)
        engine = MoietyOrbEngine(system="ptolemy")

        # Custom values
        engine = MoietyOrbEngine(orb_map={"Sun": 15, "Moon": 12, "Mars": 7})

        # With tighter orbs for minor/harmonic aspects
        engine = MoietyOrbEngine(minor_aspect_multiplier=0.4)
    """

    def __init__(
        self,
        orb_map: dict[str, float] | None = None,
        system: Literal["lilly", "ptolemy"] | None = None,
        fallback_orb: float | None = None,
        minor_aspect_multiplier: float | None = None,
    ) -> None:
        """
        Args:
            orb_map: A dictionary of {planet_name: full_orb_value}. If None,
                uses the system defaults. If provided alongside system, orb_map
                values take precedence (merged on top of system defaults).
            system: Named moiety system ("lilly" or "ptolemy"). Defaults to
                "lilly" (medieval consensus: 15/12/9/9/8/7/7).
            fallback_orb: Full orb for planets not in the orb_map.
                Defaults to 3.0.
            minor_aspect_multiplier: If set, non-major aspects use
                effective_orb * multiplier. For example, 0.4 means minor
                aspects get 40% of the moiety-calculated orb. If None,
                all aspects use the full moiety calculation.
        """
        system = system or "lilly"
        base_orbs = MOIETY_SYSTEMS.get(system, LILLY_FULL_ORBS).copy()

        if orb_map:
            base_orbs.update(orb_map)

        self._orbs = base_orbs
        self._fallback_orb = fallback_orb or 3.0
        self._minor_multiplier = minor_aspect_multiplier

    def get_orb_allowance(
        self, obj1: CelestialPosition, obj2: CelestialPosition, aspect_name: str
    ) -> float:
        """Calculate effective orb as the average of both planets' full orbs."""
        full_orb_a = self._orbs.get(obj1.name, self._fallback_orb)
        full_orb_b = self._orbs.get(obj2.name, self._fallback_orb)
        effective_orb = (full_orb_a + full_orb_b) / 2.0

        if self._minor_multiplier is not None:
            aspect_info = ASPECT_REGISTRY.get(aspect_name)
            if aspect_info and aspect_info.category in ("Minor", "Harmonic"):
                effective_orb *= self._minor_multiplier

        return effective_orb
