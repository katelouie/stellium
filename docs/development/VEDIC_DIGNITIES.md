# Vedic Dignities Implementation Guide for Stellium

## Overview

Vedic astrology (Jyotish) has its own dignity system that differs significantly from Western astrology. This guide explains the Vedic dignity concepts and how to implement them in Stellium.

---

## Key Differences: Western vs Vedic Dignities

| Concept | Western | Vedic |
|---------|---------|-------|
| Zodiac | Tropical | Sidereal |
| Rulerships | Same base, but outers assigned | Traditional 7 planets only |
| Exaltation degrees | Sign-based (whole sign) | Exact degrees matter |
| Debilitation | "Fall" (opposite exaltation sign) | "Neecha" (specific degrees) |
| Detriment | Opposite rulership sign | Not used in same way |
| Triplicity | Element-based rulers | Not used |
| Terms/Bounds | Egyptian or Ptolemaic divisions | Not used |
| Face/Decan | 10° divisions | "Drekkana" (different rulers) |
| **Unique to Vedic** | — | Moolatrikona, Dig Bala, Shadbala |

---

## Vedic Dignity Categories

### 1. Planetary Rulership (Graha + Rashi)

Same as traditional Western, using only the 7 classical planets:

```python
VEDIC_RULERSHIPS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
```

**Note:** Rahu and Ketu (the nodes) are sometimes given co-rulership:

- Rahu → Aquarius (some traditions)
- Ketu → Scorpio (some traditions)

But this is not universally accepted.

---

### 2. Exaltation (Uccha) & Debilitation (Neecha)

Vedic uses **exact degrees** for maximum exaltation, not just signs:

```python
VEDIC_EXALTATION = {
    # Planet: (sign, exact_degree)
    "Sun": ("Aries", 10),        # Deep exaltation at 10° Aries
    "Moon": ("Taurus", 3),       # Deep exaltation at 3° Taurus
    "Mars": ("Capricorn", 28),   # Deep exaltation at 28° Capricorn
    "Mercury": ("Virgo", 15),    # Deep exaltation at 15° Virgo
    "Jupiter": ("Cancer", 5),    # Deep exaltation at 5° Cancer
    "Venus": ("Pisces", 27),     # Deep exaltation at 27° Pisces
    "Saturn": ("Libra", 20),     # Deep exaltation at 20° Libra
}

VEDIC_DEBILITATION = {
    # Exactly opposite the exaltation point (same degree, opposite sign)
    "Sun": ("Libra", 10),
    "Moon": ("Scorpio", 3),
    "Mars": ("Cancer", 28),
    "Mercury": ("Pisces", 15),
    "Jupiter": ("Capricorn", 5),
    "Venus": ("Virgo", 27),
    "Saturn": ("Aries", 20),
}
```

**Important:** The *strength* of exaltation/debilitation varies based on distance from the exact degree. A planet at 10° Aries (Sun's exact exaltation point) is more exalted than at 25° Aries.

---

### 3. Moolatrikona (Root Trine) ⭐ UNIQUE TO VEDIC

Moolatrikona is a dignity between rulership and exaltation—a planet's "office" or "headquarters." Each planet has a specific degree range in one of its own signs:

```python
MOOLATRIKONA = {
    # Planet: (sign, start_degree, end_degree)
    "Sun": ("Leo", 0, 20),           # 0-20° Leo is Moolatrikona, 20-30° is just rulership
    "Moon": ("Taurus", 3, 30),       # 3-30° Taurus (0-3° is exaltation zone)
    "Mars": ("Aries", 0, 12),        # 0-12° Aries
    "Mercury": ("Virgo", 15, 20),    # 15-20° Virgo only (narrow band)
    "Jupiter": ("Sagittarius", 0, 10), # 0-10° Sagittarius
    "Venus": ("Libra", 0, 15),       # 0-15° Libra
    "Saturn": ("Aquarius", 0, 20),   # 0-20° Aquarius
}
```

**Dignity hierarchy:**

1. Exaltation (Uccha) — highest
2. Moolatrikona — very strong
3. Own sign (Swakshetra) — strong
4. Friendly sign — moderate
5. Neutral sign — neutral
6. Enemy sign — weak
7. Debilitation (Neecha) — weakest

---

### 4. Planetary Relationships (Naisargika Sambandha)

Vedic astrology has a **permanent relationship** system between planets:

```python
# Natural (permanent) planetary relationships
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],  # Moon has no natural enemies
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

# Neutral = everyone not in friends or enemies list
def get_natural_relationship(planet1: str, planet2: str) -> str:
    if planet2 in NATURAL_FRIENDS.get(planet1, []):
        return "friend"
    elif planet2 in NATURAL_ENEMIES.get(planet1, []):
        return "enemy"
    else:
        return "neutral"
```

**A planet in a friend's sign is strengthened; in an enemy's sign, weakened.**

---

### 5. Temporary Relationships (Tatkalika Sambandha)

Based on **actual chart positions**, not just nature:

```python
def get_temporary_relationship(planet1_sign_index: int, planet2_sign_index: int) -> str:
    """
    Planets within 2-4 houses of each other are temporary friends.
    Planets 5+ houses apart are temporary enemies.

    Sign index is 0-11 (Aries=0, Taurus=1, etc.)
    """
    distance = abs(planet1_sign_index - planet2_sign_index)
    # Adjust for circular zodiac
    if distance > 6:
        distance = 12 - distance

    # 2nd, 3rd, 4th, 10th, 11th, 12th from each other = temporary friends
    # (These are houses 2,3,4 on one side and 10,11,12 on other = within 4 signs)
    if distance in [1, 2, 3]:  # 2nd, 3rd, 4th house
        return "friend"
    else:  # 5th through 9th (distance 4, 5, 6)
        return "enemy"
```

---

### 6. Compound Relationships (Panchada Sambandha)

Combine natural + temporary relationships:

| Natural | Temporary | Compound Result |
|---------|-----------|-----------------|
| Friend | Friend | **Intimate Friend (Adhi Mitra)** |
| Friend | Enemy | Neutral |
| Neutral | Friend | Friend |
| Neutral | Enemy | Enemy |
| Enemy | Friend | Neutral |
| Enemy | Enemy | **Bitter Enemy (Adhi Shatru)** |

```python
def get_compound_relationship(natural: str, temporary: str) -> str:
    """Combine natural and temporary relationships."""
    if natural == "friend" and temporary == "friend":
        return "intimate_friend"  # Adhi Mitra
    elif natural == "enemy" and temporary == "enemy":
        return "bitter_enemy"  # Adhi Shatru
    elif natural == "friend" and temporary == "enemy":
        return "neutral"
    elif natural == "enemy" and temporary == "friend":
        return "neutral"
    elif natural == "neutral" and temporary == "friend":
        return "friend"
    elif natural == "neutral" and temporary == "enemy":
        return "enemy"
    else:
        return "neutral"
```

---

### 7. Dig Bala (Directional Strength) ⭐ UNIQUE TO VEDIC

Planets gain strength in specific **houses** (not signs):

```python
DIG_BALA = {
    # Planet: house where it has full directional strength
    "Sun": 10,      # Strongest in 10th house (zenith, noon)
    "Moon": 4,      # Strongest in 4th house (nadir, midnight)
    "Mars": 10,     # Strongest in 10th house
    "Mercury": 1,   # Strongest in 1st house (Ascendant)
    "Jupiter": 1,   # Strongest in 1st house
    "Venus": 4,     # Strongest in 4th house
    "Saturn": 7,    # Strongest in 7th house (Descendant)
    "Rahu": 10,     # Some traditions
    "Ketu": 4,      # Some traditions
}

def calculate_dig_bala(planet: str, house: int) -> float:
    """
    Calculate directional strength (0-60 virupas).

    Full strength at dig bala house, zero at opposite house.
    Linear interpolation between.
    """
    ideal_house = DIG_BALA.get(planet)
    if ideal_house is None:
        return 30  # Neutral for planets without dig bala

    # Calculate house distance (1-6)
    distance = abs(house - ideal_house)
    if distance > 6:
        distance = 12 - distance

    # Full strength (60) at ideal, zero at opposite (distance=6)
    # Linear: 60 - (distance * 10)
    return max(0, 60 - (distance * 10))
```

---

### 8. Drekkana (Vedic Decans)

Unlike Western decans (ruled by same element), Vedic uses a different system:

```python
def get_drekkana_ruler(sign: str, degree: float) -> str:
    """
    Vedic decans (Drekkana):
    - 0-10°: Ruled by the sign itself
    - 10-20°: Ruled by the 5th sign from it
    - 20-30°: Ruled by the 9th sign from it
    """
    sign_index = SIGN_ORDER.index(sign)

    if degree < 10:
        ruler_sign_index = sign_index
    elif degree < 20:
        ruler_sign_index = (sign_index + 4) % 12  # 5th sign
    else:
        ruler_sign_index = (sign_index + 8) % 12  # 9th sign

    ruler_sign = SIGN_ORDER[ruler_sign_index]
    return VEDIC_RULERSHIPS[ruler_sign]
```

---

### 9. Navamsa (9th Harmonic Division) ⭐ UNIQUE TO VEDIC

The Navamsa is a critical divisional chart (D9). Each sign is divided into 9 parts of 3°20' each:

```python
def get_navamsa_sign(sign: str, degree: float) -> str:
    """
    Calculate Navamsa position.

    Each sign has 9 navamsas of 3°20' (3.333°) each.
    Starting point depends on element:
    - Fire signs (Aries, Leo, Sag): Start from Aries
    - Earth signs (Taurus, Virgo, Cap): Start from Capricorn
    - Air signs (Gemini, Libra, Aqua): Start from Libra
    - Water signs (Cancer, Scorpio, Pisces): Start from Cancer
    """
    sign_index = SIGN_ORDER.index(sign)
    element = sign_index % 4  # 0=fire, 1=earth, 2=air, 3=water

    # Starting sign for navamsa calculation
    start_signs = [0, 9, 6, 3]  # Aries, Capricorn, Libra, Cancer
    start_index = start_signs[element]

    # Which navamsa (0-8)?
    navamsa_number = int(degree / (30/9))  # 3.333° each

    # Final navamsa sign
    navamsa_sign_index = (start_index + navamsa_number) % 12
    return SIGN_ORDER[navamsa_sign_index]


def is_vargottama(rashi_sign: str, navamsa_sign: str) -> bool:
    """
    Vargottama: Planet in same sign in both Rashi and Navamsa.
    This is considered very auspicious and strengthening.
    """
    return rashi_sign == navamsa_sign
```

---

## Implementation Architecture

### VedicDignityEngine Class

```python
# New file: src/stellium/engines/dignities/vedic.py

from dataclasses import dataclass
from typing import Any

from stellium.core.models import CelestialPosition
from stellium.core.protocols import DignityCalculator


@dataclass
class VedicDignityResult:
    """Complete Vedic dignity analysis for a planet."""
    planet: str
    sign: str
    degree: float

    # Basic dignities
    rulership: str | None           # "own_sign" if in own sign
    exaltation: str | None          # "exalted" + strength percentage
    debilitation: str | None        # "debilitated" + strength percentage
    moolatrikona: bool              # True if in moolatrikona zone

    # Relationships
    sign_lord: str                  # Who rules the sign the planet is in
    natural_relationship: str       # friend/neutral/enemy to sign lord
    temporary_relationship: str     # Based on chart positions
    compound_relationship: str      # Combined relationship

    # Directional strength
    house: int | None
    dig_bala: float | None          # 0-60 virupas

    # Divisional dignity
    drekkana_lord: str
    navamsa_sign: str
    navamsa_lord: str
    is_vargottama: bool

    # Overall assessment
    dignity_score: int              # Numerical score for comparison
    dignity_name: str               # Human readable: "Exalted", "Own Sign", etc.


class VedicDignityEngine:
    """
    Vedic (Jyotish) dignity calculator.

    Implements traditional Vedic dignity calculations including:
    - Uccha (Exaltation) and Neecha (Debilitation)
    - Moolatrikona
    - Planetary relationships (natural, temporary, compound)
    - Dig Bala (directional strength)
    - Drekkana and Navamsa dignities
    """

    def __init__(self, include_dig_bala: bool = True, include_navamsa: bool = True):
        self.include_dig_bala = include_dig_bala
        self.include_navamsa = include_navamsa

    def calculate_dignities(
        self,
        position: CelestialPosition,
        all_positions: list[CelestialPosition] | None = None,
        house: int | None = None,
    ) -> VedicDignityResult:
        """
        Calculate complete Vedic dignities for a position.

        Args:
            position: The planet position to analyze
            all_positions: All chart positions (needed for temporary relationships)
            house: House placement (needed for dig bala)
        """
        planet = position.name
        sign = position.sign
        degree = position.degrees + (position.minutes / 60)

        # Skip non-classical planets
        if planet not in VEDIC_PLANETS:
            return self._empty_result(planet, sign, degree)

        # Calculate each dignity type
        rulership = self._check_rulership(planet, sign)
        exaltation = self._check_exaltation(planet, sign, degree)
        debilitation = self._check_debilitation(planet, sign, degree)
        moolatrikona = self._check_moolatrikona(planet, sign, degree)

        # Sign lord and relationships
        sign_lord = VEDIC_RULERSHIPS[sign]
        natural_rel = get_natural_relationship(planet, sign_lord)

        # Temporary relationship needs all positions
        temp_rel = "neutral"
        if all_positions:
            temp_rel = self._calculate_temporary_relationship(position, sign_lord, all_positions)

        compound_rel = get_compound_relationship(natural_rel, temp_rel)

        # Dig Bala
        dig_bala = None
        if self.include_dig_bala and house:
            dig_bala = calculate_dig_bala(planet, house)

        # Drekkana
        drekkana_lord = get_drekkana_ruler(sign, degree)

        # Navamsa
        navamsa_sign = get_navamsa_sign(sign, degree)
        navamsa_lord = VEDIC_RULERSHIPS[navamsa_sign]
        is_vargottama = sign == navamsa_sign

        # Calculate overall score and name
        score, name = self._calculate_overall_dignity(
            rulership, exaltation, debilitation, moolatrikona, compound_rel
        )

        return VedicDignityResult(
            planet=planet,
            sign=sign,
            degree=degree,
            rulership=rulership,
            exaltation=exaltation,
            debilitation=debilitation,
            moolatrikona=moolatrikona,
            sign_lord=sign_lord,
            natural_relationship=natural_rel,
            temporary_relationship=temp_rel,
            compound_relationship=compound_rel,
            house=house,
            dig_bala=dig_bala,
            drekkana_lord=drekkana_lord,
            navamsa_sign=navamsa_sign,
            navamsa_lord=navamsa_lord,
            is_vargottama=is_vargottama,
            dignity_score=score,
            dignity_name=name,
        )

    def _check_exaltation(self, planet: str, sign: str, degree: float) -> str | None:
        """Check exaltation with strength based on distance from exact degree."""
        if planet not in VEDIC_EXALTATION:
            return None

        ex_sign, ex_degree = VEDIC_EXALTATION[planet]
        if sign != ex_sign:
            return None

        # Calculate strength based on distance from exact degree
        distance = abs(degree - ex_degree)
        strength = max(0, 100 - (distance * (100/30)))  # Linear falloff across sign

        return f"exalted ({strength:.0f}%)"

    def _check_debilitation(self, planet: str, sign: str, degree: float) -> str | None:
        """Check debilitation with weakness based on distance from exact degree."""
        if planet not in VEDIC_DEBILITATION:
            return None

        deb_sign, deb_degree = VEDIC_DEBILITATION[planet]
        if sign != deb_sign:
            return None

        # Calculate weakness based on distance from exact degree
        distance = abs(degree - deb_degree)
        weakness = max(0, 100 - (distance * (100/30)))

        return f"debilitated ({weakness:.0f}%)"

    def _check_moolatrikona(self, planet: str, sign: str, degree: float) -> bool:
        """Check if planet is in its moolatrikona zone."""
        if planet not in MOOLATRIKONA:
            return False

        mt_sign, start_deg, end_deg = MOOLATRIKONA[planet]
        return sign == mt_sign and start_deg <= degree < end_deg

    def _check_rulership(self, planet: str, sign: str) -> str | None:
        """Check if planet rules this sign."""
        if VEDIC_RULERSHIPS.get(sign) == planet:
            return "own_sign"
        return None

    def _calculate_overall_dignity(
        self,
        rulership: str | None,
        exaltation: str | None,
        debilitation: str | None,
        moolatrikona: bool,
        compound_relationship: str,
    ) -> tuple[int, str]:
        """Calculate overall dignity score and name."""

        # Hierarchy with scores
        if exaltation:
            return (5, "Exalted (Uccha)")
        if moolatrikona:
            return (4, "Moolatrikona")
        if rulership:
            return (3, "Own Sign (Swakshetra)")
        if compound_relationship == "intimate_friend":
            return (2, "Intimate Friend's Sign")
        if compound_relationship == "friend":
            return (1, "Friend's Sign")
        if compound_relationship == "neutral":
            return (0, "Neutral Sign")
        if compound_relationship == "enemy":
            return (-1, "Enemy's Sign")
        if compound_relationship == "bitter_enemy":
            return (-2, "Bitter Enemy's Sign")
        if debilitation:
            return (-3, "Debilitated (Neecha)")

        return (0, "Neutral")
```

---

## Data Tables

### Complete Reference Tables

```python
# src/stellium/data/vedic_dignities.py

SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

VEDIC_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

VEDIC_RULERSHIPS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Exaltation: (sign, exact_degree)
VEDIC_EXALTATION = {
    "Sun": ("Aries", 10),
    "Moon": ("Taurus", 3),
    "Mars": ("Capricorn", 28),
    "Mercury": ("Virgo", 15),
    "Jupiter": ("Cancer", 5),
    "Venus": ("Pisces", 27),
    "Saturn": ("Libra", 20),
}

# Debilitation: (sign, exact_degree) - opposite exaltation
VEDIC_DEBILITATION = {
    "Sun": ("Libra", 10),
    "Moon": ("Scorpio", 3),
    "Mars": ("Cancer", 28),
    "Mercury": ("Pisces", 15),
    "Jupiter": ("Capricorn", 5),
    "Venus": ("Virgo", 27),
    "Saturn": ("Aries", 20),
}

# Moolatrikona: (sign, start_degree, end_degree)
MOOLATRIKONA = {
    "Sun": ("Leo", 0, 20),
    "Moon": ("Taurus", 3, 30),
    "Mars": ("Aries", 0, 12),
    "Mercury": ("Virgo", 15, 20),
    "Jupiter": ("Sagittarius", 0, 10),
    "Venus": ("Libra", 0, 15),
    "Saturn": ("Aquarius", 0, 20),
}

# Natural friendships
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}

NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

# Dig Bala (directional strength) houses
DIG_BALA_HOUSES = {
    "Sun": 10,
    "Moon": 4,
    "Mars": 10,
    "Mercury": 1,
    "Jupiter": 1,
    "Venus": 4,
    "Saturn": 7,
}
```

---

## Integration with Existing Code

### Adding to ChartBuilder

```python
# Usage example
chart = (ChartBuilder.from_native(native)
    .with_sidereal("lahiri")
    .with_house_systems([WholeSignHouses()])
    .add_component(VedicDignityComponent())  # New component
    .calculate())

# Access dignities
dignities = chart.metadata.get("vedic_dignities")
for planet, dignity in dignities.items():
    print(f"{planet}: {dignity.dignity_name}")
```

### Report Section

```python
class VedicDignitySection(ReportSection):
    """Report section for Vedic dignities."""

    @property
    def section_name(self) -> str:
        return "Vedic Dignities"

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        dignities = chart.metadata.get("vedic_dignities", {})

        rows = []
        for planet in VEDIC_PLANETS:
            if planet in dignities:
                d = dignities[planet]
                rows.append([
                    planet,
                    f"{d.sign} {d.degree:.0f}°",
                    d.dignity_name,
                    d.compound_relationship,
                    f"{d.dig_bala:.0f}" if d.dig_bala else "—",
                    "✓" if d.is_vargottama else "",
                ])

        return {
            "type": "table",
            "headers": ["Planet", "Position", "Dignity", "Relationship", "Dig Bala", "Vargottama"],
            "rows": rows,
        }
```

---

## Testing

```python
def test_sun_exaltation():
    """Sun at 10° Aries should be fully exalted."""
    pos = CelestialPosition(name="Sun", sign="Aries", degrees=10, minutes=0, ...)
    engine = VedicDignityEngine()
    result = engine.calculate_dignities(pos)

    assert "exalted" in result.exaltation
    assert "100%" in result.exaltation
    assert result.dignity_name == "Exalted (Uccha)"

def test_sun_debilitation():
    """Sun at 10° Libra should be fully debilitated."""
    pos = CelestialPosition(name="Sun", sign="Libra", degrees=10, minutes=0, ...)
    engine = VedicDignityEngine()
    result = engine.calculate_dignities(pos)

    assert "debilitated" in result.debilitation
    assert result.dignity_name == "Debilitated (Neecha)"

def test_moolatrikona():
    """Sun at 15° Leo should be in moolatrikona."""
    pos = CelestialPosition(name="Sun", sign="Leo", degrees=15, minutes=0, ...)
    engine = VedicDignityEngine()
    result = engine.calculate_dignities(pos)

    assert result.moolatrikona is True
    assert result.dignity_name == "Moolatrikona"

def test_vargottama():
    """Planet in same sign in rashi and navamsa."""
    # 0-3°20' of Aries = Aries navamsa (fire sign starts from Aries)
    pos = CelestialPosition(name="Mars", sign="Aries", degrees=2, minutes=0, ...)
    engine = VedicDignityEngine()
    result = engine.calculate_dignities(pos)

    assert result.navamsa_sign == "Aries"
    assert result.is_vargottama is True
```

---

## Summary

### What to Implement (Priority Order)

1. **Core dignities** (essential)
   - Rulership (same as Western)
   - Exaltation with degree-based strength
   - Debilitation with degree-based weakness
   - Moolatrikona

2. **Relationships** (important)
   - Natural relationships table
   - Temporary relationship calculation
   - Compound relationship logic

3. **Directional strength** (nice to have)
   - Dig Bala by house

4. **Divisional charts** (advanced)
   - Navamsa calculation
   - Vargottama detection
   - Drekkana

### Files to Create

```
src/stellium/
├── data/
│   └── vedic_dignities.py      # All the tables
├── engines/
│   └── dignities/
│       ├── traditional.py       # Existing Western
│       ├── modern.py            # Existing Western
│       └── vedic.py             # NEW: Vedic engine
└── components/
    └── vedic_dignity.py         # ChartComponent wrapper
```
