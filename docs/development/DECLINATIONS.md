Good question—let me clarify because it's confusingly named.

**What `calc_ut()` returns by default:**

```python
result = swe.calc_ut(julian_day, planet_id)
# Returns: (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)
```

That `latitude` is **ecliptic latitude**—how far above or below the ecliptic plane the planet is. NOT declination.

- **Ecliptic latitude**: angle from the ecliptic (the Sun's apparent path)
- **Declination**: angle from the celestial equator (Earth's equator projected onto the sky)

They're different coordinate systems:

```
                    Celestial North Pole
                           ★
                          /|\
                         / | \
                        /  |  \
    Ecliptic plane ----/---+---\---- (zodiac lives here)
                      /    |    \
                     /     |     \
    Celestial equator -----+------ (declination measured from here)
                           |
                           ★
                    Celestial South Pole
```

The ecliptic is tilted ~23.4° from the equator. So a planet at 0° ecliptic latitude could have significant declination.

---

**To get declination, you need `FLG_EQUATORIAL`:**

```python
import swisseph as swe

# Default: ecliptic coordinates
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
result = swe.calc_ut(jd, swe.SUN, flags)
longitude, latitude, distance, *speeds = result[0]
# latitude here is ECLIPTIC latitude

# With equatorial flag: equatorial coordinates
flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
result = swe.calc_ut(jd, swe.SUN, flags)
right_ascension, declination, distance, *speeds = result[0]
# NOW we get declination
```

**The return values swap meaning:**

| Flag | Position 0 | Position 1 |
|------|-----------|-----------|
| Default | Ecliptic longitude | Ecliptic latitude |
| `FLG_EQUATORIAL` | Right ascension | **Declination** |

---

**Implementation approach:**

You probably want BOTH coordinate systems—ecliptic for normal chart work, equatorial for declination features. Two options:

### Option A: Call `calc_ut()` twice

```python
def calculate_position(self, jd: float, planet_id: int) -> CelestialPosition:
    # Get ecliptic coordinates (for zodiac position)
    ecl_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    ecl_result = swe.calc_ut(jd, planet_id, ecl_flags)
    longitude = ecl_result[0][0]
    ecl_latitude = ecl_result[0][1]
    speed = ecl_result[0][3]

    # Get equatorial coordinates (for declination)
    equ_flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL
    equ_result = swe.calc_ut(jd, planet_id, equ_flags)
    right_ascension = equ_result[0][0]
    declination = equ_result[0][1]

    return CelestialPosition(
        name=get_planet_name(planet_id),
        longitude=longitude,
        latitude=ecl_latitude,
        speed=speed,
        declination=declination,  # NEW FIELD
        right_ascension=right_ascension,  # Optional, might be useful
    )
```

### Option B: Use `swe.cotrans()` to convert

Swiss Ephemeris has a coordinate transformation function:

```python
def ecliptic_to_equatorial(longitude: float, latitude: float, obliquity: float) -> tuple[float, float]:
    """Convert ecliptic coordinates to equatorial."""
    # swe.cotrans converts between coordinate systems
    # Input: (longitude, latitude, distance)
    # Output: (right_ascension, declination, distance)
    result = swe.cotrans([longitude, latitude, 1.0], -obliquity)
    return result[0], result[1]  # RA, Dec

# Get obliquity (Earth's axial tilt) for the date
obliquity = swe.calc_ut(jd, swe.ECL_NUT)[0][0]  # True obliquity
```

This saves an API call if you're already doing the ecliptic calculation anyway.

---

**My recommendation: Option A (two calls)**

It's simpler, more explicit, and the performance difference is negligible. You're already caching, right?

---

**Updating `CelestialPosition`:**

```python
@dataclass(frozen=True)
class CelestialPosition:
    name: str
    longitude: float
    latitude: float  # Ecliptic latitude
    distance: float
    speed: float

    # Derived
    sign: str
    degrees: int
    minutes: int
    retrograde: bool

    # NEW: Equatorial coordinates
    declination: float | None = None
    right_ascension: float | None = None

    # NEW: Declination helpers
    @property
    def is_out_of_bounds(self) -> bool:
        """Planet is beyond the Sun's maximum declination (~23.4°)."""
        if self.declination is None:
            return False
        return abs(self.declination) > 23.4367  # Max solar declination

    @property
    def declination_direction(self) -> str:
        """North or South declination."""
        if self.declination is None:
            return "unknown"
        return "north" if self.declination >= 0 else "south"
```

---

**Declination aspects (parallels):**

Once you have declination, you can calculate:

```python
def calculate_parallel_aspects(positions: list[CelestialPosition], orb: float = 1.0) -> list[Aspect]:
    """
    Calculate parallel and contraparallel aspects.

    Parallel: Same declination (like a conjunction)
    Contraparallel: Opposite declination (like an opposition)
    """
    aspects = []

    for i, pos1 in enumerate(positions):
        for pos2 in positions[i+1:]:
            if pos1.declination is None or pos2.declination is None:
                continue

            dec1, dec2 = pos1.declination, pos2.declination

            # Parallel: same declination (both north or both south, same degrees)
            if abs(dec1 - dec2) <= orb:
                aspects.append(Aspect(
                    object1=pos1.name,
                    object2=pos2.name,
                    aspect_name="Parallel",
                    angle=0,  # Not really applicable
                    orb=abs(dec1 - dec2),
                ))

            # Contraparallel: opposite declination (one north, one south, same degrees)
            if abs(dec1 + dec2) <= orb:  # Note: PLUS, because opposite signs
                aspects.append(Aspect(
                    object1=pos1.name,
                    object2=pos2.name,
                    aspect_name="Contraparallel",
                    angle=180,
                    orb=abs(dec1 + dec2),
                ))

    return aspects
```

---

**Out-of-bounds planets:**

This is an interesting astrological concept. The Sun's declination varies between ~+23.4° and ~-23.4° (the tropics). When a planet's declination exceeds this, it's "out of bounds"—considered to have extra intensity, unpredictability, or genius-level expression.

```python
def find_out_of_bounds_planets(positions: list[CelestialPosition]) -> list[CelestialPosition]:
    """Find planets with declination beyond the Sun's maximum."""
    return [p for p in positions if p.is_out_of_bounds]
```

Moon, Mercury, Mars, and Venus can all go out of bounds. Jupiter, Saturn, and the outer planets basically never do.

---

**Summary checklist:**

1. [ ] Add `FLG_EQUATORIAL` call in ephemeris engine
2. [ ] Add `declination` and `right_ascension` to `CelestialPosition`
3. [ ] Add `is_out_of_bounds` property
4. [ ] Add parallel/contraparallel aspect calculation
5. [ ] Add to report sections (planet positions table, new "Declinations" section?)
6. [ ] Maybe add to visualization? (A separate declination graph is traditional)

Want me to draft any of these in more detail?
