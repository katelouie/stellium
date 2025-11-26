# Swiss Ephemeris Sidereal Implementation Guide for Stellium

## Overview

This document outlines the changes needed to support sidereal zodiac calculations throughout Stellium. Swiss Ephemeris handles sidereal calculations via global state flags, which requires careful management to avoid contaminating tropical calculations.

---

## Core Concept: How Sidereal Works in Swiss Ephemeris

### The Two-Step Process

```python
import swisseph as swe

# Step 1: Set the ayanamsa (sidereal mode)
swe.set_sid_mode(swe.SIDM_LAHIRI)  # Or any other ayanamsa

# Step 2: Add FLG_SIDEREAL to your calculation flags
flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
result = swe.calc_ut(julian_day, planet_id, flags)
```

### The Global State Problem

`swe.set_sid_mode()` sets *global* state. It persists until changed. This is dangerous:

```python
# Thread 1: Calculates sidereal chart
swe.set_sid_mode(swe.SIDM_LAHIRI)
result1 = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)

# Thread 2: Thinks it's calculating tropical, but sideral mode is still set!
# (Though without FLG_SIDEREAL flag, it should be okay...)
result2 = swe.calc_ut(jd, swe.SUN)  # This is fine, flag not passed

# BUT if thread 2 also uses FLG_SIDEREAL for some reason, it gets Lahiri
# even if it wanted Fagan-Bradley
```

### Safety Solution: Context Manager

```python
from contextlib import contextmanager
import swisseph as swe

@contextmanager
def sidereal_mode(ayanamsa: int):
    """
    Context manager for safe sidereal calculations.

    Usage:
        with sidereal_mode(swe.SIDM_LAHIRI) as flags:
            result = swe.calc_ut(jd, planet, flags)
    """
    try:
        swe.set_sid_mode(ayanamsa)
        yield swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
    finally:
        # Reset to a default state (Fagan-Bradley is arbitrary,
        # but the flag won't be used without FLG_SIDEREAL anyway)
        swe.set_sid_mode(swe.SIDM_FAGAN_BRADLEY)
```

---

## Available Ayanamsas

Swiss Ephemeris provides 30+ ayanamsas. The most commonly used:

| Constant | Name | Primary Use |
|----------|------|-------------|
| `SIDM_LAHIRI` | Lahiri (Chitrapaksha) | Indian government standard, most common in Vedic |
| `SIDM_FAGAN_BRADLEY` | Fagan-Bradley | Western sidereal |
| `SIDM_RAMAN` | B.V. Raman | Popular in South India |
| `SIDM_KRISHNAMURTI` | Krishnamurti | KP system |
| `SIDM_DELUCE` | De Luce | Western sidereal |
| `SIDM_YUKTESHWAR` | Sri Yukteshwar | Based on Holy Science |
| `SIDM_JN_BHASIN` | J.N. Bhasin | North Indian variant |
| `SIDM_TRUE_CITRA` | True Chitrapaksha | Spica at exactly 0° Libra |
| `SIDM_TRUE_REVATI` | True Revati | Revati at exactly 0° Aries |

### Ayanamsa Registry (suggested implementation)

```python
# New file: src/stellium/core/ayanamsa.py

from dataclasses import dataclass
from enum import Enum
import swisseph as swe

@dataclass
class AyanamsaInfo:
    name: str
    swe_constant: int
    description: str
    tradition: str  # "vedic", "western_sidereal", "other"

AYANAMSA_REGISTRY = {
    "lahiri": AyanamsaInfo(
        name="Lahiri",
        swe_constant=swe.SIDM_LAHIRI,
        description="Indian government standard, Chitrapaksha ayanamsa",
        tradition="vedic"
    ),
    "fagan_bradley": AyanamsaInfo(
        name="Fagan-Bradley",
        swe_constant=swe.SIDM_FAGAN_BRADLEY,
        description="Primary Western sidereal ayanamsa",
        tradition="western_sidereal"
    ),
    "raman": AyanamsaInfo(
        name="Raman",
        swe_constant=swe.SIDM_RAMAN,
        description="B.V. Raman's ayanamsa, popular in South India",
        tradition="vedic"
    ),
    "krishnamurti": AyanamsaInfo(
        name="Krishnamurti",
        swe_constant=swe.SIDM_KRISHNAMURTI,
        description="Used in KP (Krishnamurti Paddhati) system",
        tradition="vedic"
    ),
    # ... etc
}

def get_ayanamsa(name: str) -> AyanamsaInfo:
    """Get ayanamsa info by name (case-insensitive)."""
    key = name.lower().replace("-", "_").replace(" ", "_")
    if key not in AYANAMSA_REGISTRY:
        available = ", ".join(AYANAMSA_REGISTRY.keys())
        raise ValueError(f"Unknown ayanamsa '{name}'. Available: {available}")
    return AYANAMSA_REGISTRY[key]
```

---

## What Needs to Change: Component by Component

### 1. CalculationConfig

Add zodiac and ayanamsa settings:

```python
# In src/stellium/core/config.py

from enum import Enum
from typing import Optional

class ZodiacType(Enum):
    TROPICAL = "tropical"
    SIDEREAL = "sidereal"

@dataclass
class CalculationConfig:
    # Existing fields...
    house_systems: list[str] = field(default_factory=lambda: ["Placidus"])
    aspects: list[str] = field(default_factory=lambda: ["Conjunction", "Sextile", "Square", "Trine", "Opposition"])

    # New fields for sidereal
    zodiac_type: ZodiacType = ZodiacType.TROPICAL
    ayanamsa: Optional[str] = None  # Only used if zodiac_type is SIDEREAL

    def __post_init__(self):
        if self.zodiac_type == ZodiacType.SIDEREAL and self.ayanamsa is None:
            self.ayanamsa = "lahiri"  # Default ayanamsa
```

### 2. ChartBuilder API

Add fluent methods for sidereal:

```python
# In src/stellium/core/builder.py

class ChartBuilder:
    # ... existing methods ...

    def with_sidereal(self, ayanamsa: str = "lahiri") -> "ChartBuilder":
        """
        Use sidereal zodiac for calculations.

        Args:
            ayanamsa: The ayanamsa to use. Options include:
                - "lahiri" (default, most common for Vedic)
                - "fagan_bradley" (Western sidereal)
                - "raman", "krishnamurti", etc.

        Example:
            chart = (ChartBuilder.from_native(native)
                .with_sidereal("lahiri")
                .with_house_systems([WholeSignHouses()])
                .calculate())
        """
        self._config.zodiac_type = ZodiacType.SIDEREAL
        self._config.ayanamsa = ayanamsa
        return self

    def with_tropical(self) -> "ChartBuilder":
        """
        Use tropical zodiac for calculations (default).
        """
        self._config.zodiac_type = ZodiacType.TROPICAL
        self._config.ayanamsa = None
        return self
```

### 3. SwissEphemerisEngine

Modify to respect zodiac settings:

```python
# In src/stellium/engines/ephemeris.py

class SwissEphemerisEngine:
    def __init__(self, config: CalculationConfig):
        self.config = config
        self._base_flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    def _get_calculation_flags(self) -> int:
        """Get flags based on zodiac type."""
        flags = self._base_flags
        if self.config.zodiac_type == ZodiacType.SIDEREAL:
            flags |= swe.FLG_SIDEREAL
        return flags

    def _setup_sidereal_mode(self):
        """Set ayanamsa if using sidereal."""
        if self.config.zodiac_type == ZodiacType.SIDEREAL:
            ayanamsa_info = get_ayanamsa(self.config.ayanamsa)
            swe.set_sid_mode(ayanamsa_info.swe_constant)

    def calculate_planet_position(self, julian_day: float, planet_id: int) -> dict:
        """Calculate a single planet position."""
        self._setup_sidereal_mode()
        flags = self._get_calculation_flags()

        result = swe.calc_ut(julian_day, planet_id, flags)
        # ... rest of processing

    def calculate_all_positions(self, julian_day: float) -> list[CelestialPosition]:
        """Calculate all planet positions."""
        self._setup_sidereal_mode()
        flags = self._get_calculation_flags()

        positions = []
        for planet_id in self._get_planet_ids():
            result = swe.calc_ut(julian_day, planet_id, flags)
            # ... process result

        return positions
```

### 4. House Calculations

Houses also need sidereal support:

```python
# In src/stellium/engines/houses.py

class SwissHouseSystemBase:
    def calculate_cusps(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        config: CalculationConfig
    ) -> tuple[list[float], list[float]]:
        """Calculate house cusps, respecting zodiac type."""

        # Use houses_ex for sidereal support
        flags = 0
        if config.zodiac_type == ZodiacType.SIDEREAL:
            ayanamsa_info = get_ayanamsa(config.ayanamsa)
            swe.set_sid_mode(ayanamsa_info.swe_constant)
            flags = swe.FLG_SIDEREAL

        cusps, ascmc = swe.houses_ex(
            julian_day,
            latitude,
            longitude,
            self._house_system_byte,
            flags
        )

        return cusps, ascmc
```

**Important:** Use `swe.houses_ex()` instead of `swe.houses()` — the `_ex` version accepts flags including `FLG_SIDEREAL`.

### 5. CalculatedChart Model

Add zodiac metadata:

```python
# In src/stellium/core/models.py

@dataclass(frozen=True)
class CalculatedChart:
    # Existing fields...
    julian_day: float
    native: Native
    positions: list[CelestialPosition]
    house_cusps: dict[str, HouseCusps]
    aspects: list[Aspect]

    # New fields
    zodiac_type: ZodiacType = ZodiacType.TROPICAL
    ayanamsa: Optional[str] = None  # Name of ayanamsa if sidereal
    ayanamsa_value: Optional[float] = None  # Actual ayanamsa offset in degrees
```

### 6. Getting the Ayanamsa Value

Swiss Ephemeris can tell you the exact ayanamsa offset:

```python
def get_ayanamsa_value(julian_day: float, ayanamsa: str) -> float:
    """Get the ayanamsa value in degrees for a specific date."""
    ayanamsa_info = get_ayanamsa(ayanamsa)
    swe.set_sid_mode(ayanamsa_info.swe_constant)
    return swe.get_ayanamsa_ut(julian_day)
```

This is useful for display: "Lahiri Ayanamsa: 24°07'28""

---

## What Does NOT Change

### Sign Calculations

You do NOT need to change sign calculation logic. The longitude returned by `swe.calc_ut()` with `FLG_SIDEREAL` is *already* the sidereal longitude. Your existing `longitude_to_sign()` function works unchanged:

```python
def longitude_to_sign(longitude: float) -> tuple[str, int, int]:
    """Works for both tropical and sidereal longitudes."""
    sign_index = int(longitude // 30)
    degree = int(longitude % 30)
    minute = int((longitude % 1) * 60)
    return SIGNS[sign_index], degree, minute
```

The difference is in what longitude *means*:

- Tropical: degrees from vernal equinox (0° Aries = March equinox)
- Sidereal: degrees from a fixed star reference point (varies by ayanamsa)

### Aspect Calculations

Aspects are based on angular separation between planets. This is the *same* regardless of zodiac:

```python
# If Sun is at 100° and Moon is at 160°, they're 60° apart (sextile)
# This is true in both tropical and sidereal
```

No changes needed to aspect engines.

### Dignity Calculations?

**This is complicated.** Traditional dignities were developed for tropical OR sidereal depending on tradition:

- Western dignities (Ptolemaic) → designed for tropical
- Vedic dignities → designed for sidereal

For now, you could:

1. Apply existing dignity tables to sidereal positions (user interprets accordingly)
2. Add a warning when using Western dignities with sidereal
3. Later: implement separate Vedic dignity tables

---

## Visualization Changes

### Chart Info Display

Show zodiac type and ayanamsa:

```python
# In ChartInfoLayer or header
if chart.zodiac_type == ZodiacType.SIDEREAL:
    zodiac_text = f"Sidereal ({chart.ayanamsa})"
    ayanamsa_text = f"Ayanamsa: {format_degrees(chart.ayanamsa_value)}"
else:
    zodiac_text = "Tropical"
```

### Report Headers

```python
# In ChartOverviewSection
def render(self, chart: CalculatedChart) -> dict:
    overview = {
        "Name": chart.native.name,
        "Date": format_date(chart.native.datetime),
        # ... etc
        "Zodiac": chart.zodiac_type.value.title(),
    }

    if chart.zodiac_type == ZodiacType.SIDEREAL:
        overview["Ayanamsa"] = f"{chart.ayanamsa} ({format_degrees(chart.ayanamsa_value)})"

    return overview
```

---

## Comparison Charts (Synastry, Transits, etc.)

**Rule:** Both charts in a comparison must use the same zodiac type.

```python
# In ComparisonBuilder
def _validate_zodiac_compatibility(self, chart1: CalculatedChart, chart2: CalculatedChart):
    if chart1.zodiac_type != chart2.zodiac_type:
        raise ValueError(
            f"Cannot compare charts with different zodiac types: "
            f"{chart1.zodiac_type.value} vs {chart2.zodiac_type.value}"
        )

    if chart1.zodiac_type == ZodiacType.SIDEREAL:
        if chart1.ayanamsa != chart2.ayanamsa:
            raise ValueError(
                f"Cannot compare sidereal charts with different ayanamsas: "
                f"{chart1.ayanamsa} vs {chart2.ayanamsa}"
            )
```

---

## Testing Strategy

### Unit Tests

```python
def test_tropical_vs_sidereal_positions():
    """Sidereal positions should differ from tropical by ~24°."""
    native = Native("2000-01-01 12:00", "London, UK")

    tropical = ChartBuilder.from_native(native).calculate()
    sidereal = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()

    tropical_sun = tropical.get_object("Sun").longitude
    sidereal_sun = sidereal.get_object("Sun").longitude

    # Lahiri ayanamsa is ~24° in 2000
    difference = tropical_sun - sidereal_sun
    assert 23 < difference < 25

def test_ayanamsa_value_retrieved():
    """Chart should store the actual ayanamsa value."""
    native = Native("2000-01-01 12:00", "London, UK")
    chart = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()

    assert chart.ayanamsa == "lahiri"
    assert chart.ayanamsa_value is not None
    assert 23 < chart.ayanamsa_value < 25

def test_different_ayanamsas_give_different_results():
    """Different ayanamsas should produce different positions."""
    native = Native("2000-01-01 12:00", "London, UK")

    lahiri = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()
    raman = ChartBuilder.from_native(native).with_sidereal("raman").calculate()

    # Positions should differ slightly
    assert lahiri.get_object("Sun").longitude != raman.get_object("Sun").longitude
```

---

## Future: Tropical vs Sidereal Biwheel Comparison

One powerful use case for sidereal support is **comparing the same native's chart in both tropical and sidereal zodiacs** side-by-side. This allows astrologers to see how planetary positions shift between systems.

### Design Considerations

**Chart Independence:**
Each chart calculation is already independent with the builder pattern:
```python
tropical = ChartBuilder.from_native(native).with_tropical().calculate()
sidereal = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()
```

**Zodiac Metadata Storage:**
Each `CalculatedChart` stores its zodiac type and ayanamsa, enabling differentiation in visualization:
```python
assert tropical.zodiac_type == ZodiacType.TROPICAL
assert sidereal.zodiac_type == ZodiacType.SIDEREAL
assert sidereal.ayanamsa == "lahiri"
```

**Comparison Validation:**
When implementing biwheel/comparison features, validation should ALLOW tropical vs sidereal of the same native:
```python
def _validate_comparison_compatibility(chart1, chart2):
    # Different natives with different zodiacs = error
    if chart1.native != chart2.native:
        if chart1.zodiac_type != chart2.zodiac_type:
            raise ValueError("Cannot compare different people with different zodiacs")

    # SAME native with different zodiacs = ALLOWED
    # This enables tropical vs sidereal comparison charts
    # The visualization layer shows both zodiacs clearly
```

**Visualization Approach:**
- Inner wheel: Tropical positions
- Outer wheel: Sidereal positions
- Clear labeling: "Tropical" vs "Sidereal (Lahiri)"
- Show ayanamsa offset: "Ayanamsa: 24°07'48""
- Aspect lines connect same planets across zodiacs (shows shifts)

**Benefits:**
- Educational tool for understanding zodiac systems
- Helps astrologers transition between tropical and sidereal practice
- Demonstrates the ~24° shift visually
- Shows which planets change signs between systems

### Implementation Notes

This feature does NOT need to be implemented in Phase 1 (core sidereal support). It's a natural extension once the foundation is in place.

**Future tasks:**
- [ ] Update biwheel/comparison validation to allow same-native different-zodiac
- [ ] Add visualization support for dual-zodiac biwheels
- [ ] Create example showing tropical vs sidereal comparison
- [ ] Document this use case in user guide

---

## Summary Checklist

### Must Change

- [ ] Add `ZodiacType` enum and ayanamsa to `CalculationConfig`
- [ ] Add `with_sidereal()` / `with_tropical()` to `ChartBuilder`
- [ ] Modify `SwissEphemerisEngine` to set sidereal mode and flags
- [ ] Modify house calculations to use `houses_ex()` with flags
- [ ] Add zodiac metadata to `CalculatedChart`
- [ ] Update `ChartOverviewSection` to display zodiac/ayanamsa
- [ ] Update chart visualization to show zodiac type
- [ ] Add validation for comparison charts (same zodiac required for different natives)

### Nice to Have

- [ ] Ayanamsa registry with metadata
- [ ] `get_ayanamsa_value()` helper
- [ ] Context manager for thread-safe sidereal calculations
- [ ] Warning when using Western dignities with sidereal

### Does Not Change

- [ ] Sign calculation logic (longitude → sign)
- [ ] Aspect calculations (angular separation)
- [ ] Midpoint calculations (also angular)
- [ ] Visualization layout (only labels change)

---

## Example Usage (End Goal)

```python
from stellium import ChartBuilder, Native
from stellium.engines import WholeSignHouses

# Vedic-style chart
native = Native("1994-01-06 11:47", "Palo Alto, CA", name="Kate")

vedic_chart = (ChartBuilder.from_native(native)
    .with_sidereal("lahiri")
    .with_house_systems([WholeSignHouses()])
    .with_aspects()
    .calculate())

# Check the Sun
sun = vedic_chart.get_object("Sun")
print(f"Sun: {sun.sign} {sun.degree}°{sun.minute}'")
# Output: Sun: Sagittarius 22°16' (vs Capricorn 16°16' tropical)

# Chart knows its zodiac
print(f"Zodiac: {vedic_chart.zodiac_type.value}")  # "sidereal"
print(f"Ayanamsa: {vedic_chart.ayanamsa}")  # "lahiri"

# Visualization shows it
vedic_chart.draw("vedic_kate.svg").with_theme("midnight").save()
# Chart header: "Sidereal (Lahiri) | Whole Sign"
```
