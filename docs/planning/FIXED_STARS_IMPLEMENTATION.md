# Fixed Stars Implementation Plan

## Overview

Add fixed star calculations to Stellium using Swiss Ephemeris `swe.fixstar_ut()`. Stars will be calculated for a given Julian Day and can be included in chart output, aspect calculations, and reports.

## Swiss Ephemeris API

```python
import swisseph as swe

# Calculate fixed star position
result = swe.fixstar_ut(star_name, julian_day, flag=0)
# Returns: ((longitude, latitude, distance, speed_lon, speed_lat, speed_dist), star_name, retflag)

# Get magnitude
mag = swe.fixstar_mag(star_name)
```

**Key observations:**
- Swiss Ephemeris handles precession automatically
- Stars are identified by name (e.g., "Regulus", "Algol")
- Returns ecliptic longitude/latitude (not equatorial)
- Longitude is what we need for zodiacal position and aspects

## Data Model

### New Dataclass: `FixedStarPosition`

```python
@dataclass(frozen=True)
class FixedStarPosition:
    """Position of a fixed star at a specific time."""
    name: str                    # Display name (e.g., "Regulus")
    swe_name: str               # Swiss Ephemeris lookup name
    longitude: float            # Ecliptic longitude (0-360)
    latitude: float             # Ecliptic latitude
    magnitude: float            # Apparent magnitude (brightness)
    constellation: str          # Traditional constellation
    nature: str                 # Traditional planetary nature (e.g., "Mars/Jupiter")
    keywords: list[str]         # Interpretive keywords

    @property
    def sign(self) -> str:
        """Zodiac sign the star is in."""
        # Same logic as CelestialPosition

    @property
    def degree_in_sign(self) -> float:
        """Degree within the sign (0-30)."""
```

## Star Registry

**Important:** Follow existing pattern in `core/registry.py`. Fixed stars already exist there partially - extend with full `FixedStarInfo` dataclass.

### FixedStarInfo Dataclass (add to registry.py)

```python
@dataclass(frozen=True)
class FixedStarInfo:
    """Complete metadata for a fixed star."""

    # Core Identity
    name: str                      # Display name (e.g., "Regulus")
    swe_name: str                  # Swiss Ephemeris lookup name

    # Visual
    glyph: str = "★"              # Unicode glyph

    # Classification
    constellation: str = ""        # Traditional constellation (e.g., "Leo")
    bayer: str = ""               # Bayer designation (e.g., "Alpha Leonis")
    tier: int = 2                 # 1=Royal, 2=Major, 3=Extended
    is_royal: bool = False        # One of the four Royal Stars

    # Physical Properties
    magnitude: float = 0.0        # Apparent magnitude (brightness)

    # Astrological Properties
    nature: str = ""              # Planetary nature (e.g., "Mars/Jupiter")
    keywords: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name} ({self.constellation})"
```

### Add to FIXED_STARS_REGISTRY (in registry.py)

```python
FIXED_STARS_REGISTRY: dict[str, FixedStarInfo] = {
    # TIER 1: ROYAL STARS
    "Regulus": FixedStarInfo(
        name="Regulus",
        swe_name="Regulus",
        constellation="Leo",
        bayer="Alpha Leonis",
        tier=1,
        is_royal=True,
        magnitude=1.35,
        nature="Mars/Jupiter",
        keywords=("royalty", "success", "fame", "leadership"),
        description="The Heart of the Lion. Most royal fixed star.",
    ),
    # ... etc (see data/fixed_stars.yaml for full list)
}
```

### Helper Functions

```python
def get_fixed_star_info(name: str) -> FixedStarInfo | None:
    """Get fixed star by name."""
    return FIXED_STARS_REGISTRY.get(name)

def get_royal_stars() -> list[FixedStarInfo]:
    """Get the four Royal Stars of Persia."""
    return [s for s in FIXED_STARS_REGISTRY.values() if s.is_royal]

def get_stars_by_tier(tier: int) -> list[FixedStarInfo]:
    """Get stars by tier (1=Royal, 2=Major, 3=Extended)."""
    return [s for s in FIXED_STARS_REGISTRY.values() if s.tier == tier]
```

**Note:** The `data/fixed_stars.yaml` file serves as a human-readable reference and data source. The actual registry is in Python code for consistency with `CELESTIAL_REGISTRY` and `ASPECT_REGISTRY`.

## Engine Design

### `FixedStarsEngine` (Protocol)

```python
class FixedStarsEngine(Protocol):
    """Protocol for fixed star calculation engines."""

    def calculate_stars(
        self,
        julian_day: float,
        stars: list[str] | None = None,  # None = all registered stars
    ) -> list[FixedStarPosition]:
        """Calculate positions for specified fixed stars."""
        ...
```

### `SwissEphemerisFixedStarsEngine` (Implementation)

```python
class SwissEphemerisFixedStarsEngine:
    """Swiss Ephemeris implementation of fixed star calculations."""

    def __init__(self, registry: dict = FIXED_STARS_REGISTRY):
        self.registry = registry

    def calculate_stars(
        self,
        julian_day: float,
        stars: list[str] | None = None,
    ) -> list[FixedStarPosition]:
        if stars is None:
            stars = list(self.registry.keys())

        results = []
        for star_name in stars:
            meta = self.registry.get(star_name, {})
            swe_name = meta.get("swe_name", star_name)

            result = swe.fixstar_ut(swe_name, julian_day)
            lon, lat = result[0][0], result[0][1]

            results.append(FixedStarPosition(
                name=star_name,
                swe_name=swe_name,
                longitude=lon,
                latitude=lat,
                magnitude=meta.get("magnitude", 0.0),
                constellation=meta.get("constellation", ""),
                nature=meta.get("nature", ""),
                keywords=meta.get("keywords", []),
            ))

        return results
```

## ChartBuilder Integration

### Option A: As a Component (Recommended)

```python
# Usage
chart = (ChartBuilder.from_native(native)
    .add_component(FixedStarsComponent())  # Add all stars
    .add_component(FixedStarsComponent(stars=["Regulus", "Algol"]))  # Specific stars
    .calculate())

# Access results
stars = chart.get_component_result("Fixed Stars")
regulus = next(s for s in stars if s.name == "Regulus")
```

### Option B: Direct Builder Method

```python
# Usage
chart = (ChartBuilder.from_native(native)
    .with_fixed_stars()  # All stars
    .with_fixed_stars(["Regulus", "Algol"])  # Specific stars
    .calculate())

# Access via chart property
chart.fixed_stars  # -> list[FixedStarPosition]
```

**Recommendation:** Option A (Component) fits existing architecture better.

## Aspect Integration

Fixed stars should be aspectable to planets:

```python
# In AspectEngine, extend to check star-planet aspects
# Typically only conjunctions are used (orb 1-2°)

# Could add to existing aspect output or separate:
chart.fixed_star_conjunctions  # Stars conjunct planets
```

**Default behavior:** Only calculate conjunctions with tight orbs (1°).

## File Structure

```
src/stellium/
├── core/
│   └── fixed_stars_registry.py   # FIXED_STARS_REGISTRY dict
├── engines/
│   └── fixed_stars.py            # SwissEphemerisFixedStarsEngine
├── components/
│   └── fixed_stars.py            # FixedStarsComponent
└── data/
    └── fixed_stars.yaml          # Star metadata (source of truth)
```

## Implementation Order

1. **Create `data/fixed_stars.yaml`** - Star metadata (done in this session)
2. **Create `FixedStarPosition` model** - Add to `core/models.py`
3. **Create `FixedStarsEngine`** - In `engines/fixed_stars.py`
4. **Create `FixedStarsComponent`** - In `components/fixed_stars.py`
5. **Add tests** - `tests/test_fixed_stars.py`
6. **Update `__init__.py`** - Export public API
7. **Add to ChartBuilder** - Optional convenience method

## Star Selection

### Tier 1: Royal Stars (Always include)
- **Aldebaran** (Watcher of the East) - 10° Gemini
- **Regulus** (Watcher of the North) - 0° Virgo
- **Antares** (Watcher of the West) - 10° Sagittarius
- **Fomalhaut** (Watcher of the South) - 4° Pisces

### Tier 2: Major Stars (Default)
- Algol, Sirius, Spica, Arcturus, Vega, Capella, Rigel, Betelgeuse, Procyon, Pollux

### Tier 3: Extended (Optional)
- Castor, Deneb, Altair, Canopus, Polaris, Achernar, Hamal, etc.

## Precession Note

Swiss Ephemeris handles precession automatically. The longitudes returned are for the epoch of the Julian Day provided. No manual precession calculation needed.

## References

- Swiss Ephemeris documentation: https://www.astro.com/swisseph/
- Bernadette Brady, "Fixed Stars" (1998)
- Vivian Robson, "Fixed Stars and Constellations in Astrology" (1923)
