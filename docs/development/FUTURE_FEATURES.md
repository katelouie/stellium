# Future Features: An Astrologer's Perspective

This document outlines features that would meaningfully expand Stellium's capabilities, written from the perspective of professional astrological practice. Each section explains what the technique is, why it matters, and how it could integrate with the existing architecture.

---

## High-Impact Features

These are techniques used daily by professional astrologers. Their absence is noticeable.

---

### 1. Solar and Lunar Returns

#### What It Is

A **return chart** is cast for the exact moment a planet returns to its natal position. The most common:

- **Solar Return**: When the transiting Sun returns to your natal Sun position (once per year, around your birthday). The chart for that moment, cast for your current location, is read as a "year ahead" forecast.
- **Lunar Return**: When the transiting Moon returns to its natal position (every ~27.3 days). Used for monthly forecasting.
- **Planetary Returns**: Saturn return (~29 years), Jupiter return (~12 years), etc. Major life milestones.

#### Why It Matters

Solar returns are arguably the **most-used predictive technique** after transits. Every astrologer does them. Every client expects them. Professional software without solar returns is incomplete.

Lunar returns are popular for monthly planning, especially in horary/electional practices.

Saturn and Jupiter returns mark major life chapters - these are the "milestone birthday" charts that even casual astrology enthusiasts know about.

#### Implementation Approach

**New Builder Methods:**

```python
# Solar return for a specific year
solar_return = ChartBuilder.solar_return(natal_chart, year=2025).calculate()

# Solar return at a specific location (precessed)
solar_return = ChartBuilder.solar_return(
    natal_chart,
    year=2025,
    location="Seattle, WA"  # Where you'll be on your birthday
).calculate()

# Lunar return nearest to a date
lunar_return = ChartBuilder.lunar_return(natal_chart, near_date="2025-02-15").calculate()

# Saturn return
saturn_return = ChartBuilder.planetary_return(natal_chart, planet="Saturn", occurrence=1).calculate()
```

**Core Calculation:**

1. Get natal planet longitude
2. Search forward in time for when transiting planet reaches that exact longitude
3. Cast a chart for that moment at the specified location

**Swiss Ephemeris Support:**

Use `swe_solcross_ut()` or iterative search with `swe_calc_ut()`. The ephemeris can find exact crossing times.

**Architecture Fit:**

- Returns are just specialized `CalculatedChart` objects
- Could add `ChartBuilder.solar_return()`, `.lunar_return()`, `.planetary_return()` factory methods
- Return charts can use all existing visualization and reporting
- Comparison with natal via existing `ComparisonBuilder`

**Visualization:**

Return charts are typically shown as:
1. Standalone wheel (current support works)
2. Bi-wheel with natal inside, return outside (existing comparison support)
3. Tri-wheel with natal, return, and current transits (would need new layer)

---

### 2. Secondary Progressions

#### What It Is

**Secondary progressions** use the symbolic equation "one day = one year." To find your progressed positions at age 30, look at where the planets were 30 days after your birth.

The progressed chart moves slowly:
- Progressed Sun: ~1° per year
- Progressed Moon: ~12-13° per year (completes the zodiac in ~27 years)
- Progressed angles: vary by latitude, can move 1° per year or more

#### Why It Matters

Progressions show **internal psychological development** and **unfolding potential**. While transits are external events happening to you, progressions are you becoming who you're meant to be.

Key progressed events:
- Progressed Moon changing signs (~2.5 years): emotional tone shifts
- Progressed Sun changing signs (~30 years): identity evolution
- Progressed planets making aspects to natal: developmental milestones

This completes the "predictive trinity": **Transits** (external events), **Progressions** (internal development), **Returns** (annual themes).

#### Implementation Approach

**New Builder Methods:**

```python
# Progressed chart for a specific date
progressed = ChartBuilder.secondary_progression(
    natal_chart,
    progressed_to="2025-06-15"
).calculate()

# Progressed chart for current moment
progressed = ChartBuilder.secondary_progression(natal_chart).calculate()
```

**Core Calculation:**

1. Calculate days elapsed: `(target_date - natal_date).days / 365.25` = years
2. Progressed date = `natal_date + timedelta(days=years)`
3. Cast chart for progressed date at natal location
4. Optionally: calculate progressed angles using solar arc or Naibod rate

**Angle Progression Methods:**

Several schools exist:
- **Solar Arc**: All angles progress at the rate of the progressed Sun
- **Naibod**: Use mean Sun rate (59'08" per year)
- **Quotidian**: Actual daily motion (most accurate, most complex)

Could offer as configuration option.

**Architecture Fit:**

- Progressed charts are `CalculatedChart` objects with metadata indicating progression type
- Factory method on `ChartBuilder`
- Natural integration with `ComparisonBuilder` for progressed-to-natal comparisons
- Could add `ProgressionType` enum for different angle calculation methods

**Visualization:**

Typically shown as bi-wheel (natal inner, progressed outer) or tri-wheel with transits.

---

### 3. Fixed Stars

#### What It Is

**Fixed stars** are distant stars that appear stationary relative to the zodiac (unlike planets). Major fixed stars have been tracked for millennia and carry specific meanings:

- **Regulus** (29° Leo): Royal star, success through nobility
- **Spica** (23° Libra): Gifts, talent, brilliance
- **Algol** (26° Taurus): Intensity, danger, transformation (the "Demon Star")
- **Antares** (9° Sagittarius): Royal star, success through intensity
- **Fomalhaut** (3° Pisces): Royal star, success through idealism

#### Why It Matters

Fixed star conjunctions add **depth and specificity** to chart interpretation. A planet at 29° Leo isn't just "late Leo" - it's conjunct Regulus, one of the four royal stars.

Traditional astrology weighted fixed stars heavily. Modern astrology rediscovered them. Clients with prominent fixed star placements often have dramatic, notable lives.

#### Implementation Approach

**Access Pattern:**

```python
# Get fixed stars near chart points
stars = chart.get_fixed_stars(orb=1.0)  # Within 1° of any planet/angle

# Check specific conjunctions
regulus_conjunctions = chart.get_star_conjunctions("Regulus", orb=1.0)

# List all stars with positions
all_stars = chart.get_all_fixed_stars()
```

**Core Calculation:**

Swiss Ephemeris has full fixed star support via `swe_fixstar_ut()`. We just need to wrap it.

**Data Model:**

```python
@dataclass(frozen=True)
class FixedStarPosition:
    name: str
    longitude: float
    latitude: float
    magnitude: float  # Brightness (lower = brighter)
    nature: str  # Traditional planetary nature (e.g., "Mars-Jupiter")
    meaning: str  # Brief interpretation
```

**Star Registry:**

Create `FIXED_STAR_REGISTRY` similar to `CELESTIAL_REGISTRY`:

```python
FIXED_STAR_REGISTRY = {
    "Regulus": FixedStarInfo(
        swe_id="Regulus",
        display_name="Regulus",
        nature="Mars-Jupiter",
        meaning="Success, nobility, leadership",
        magnitude=1.35,
    ),
    # ... more stars
}
```

**Architecture Fit:**

- New `FixedStarsCalculator` component (optional, like Arabic Parts)
- Results stored in chart metadata or as component result
- Could add to visualization as small markers on zodiac ring
- Report section for fixed star conjunctions

**Scope Consideration:**

Start with the ~20-30 major stars (magnitude < 2.5), expandable later.

---

### 4. Eclipses

#### What It Is

**Eclipses** are lunations (New/Full Moons) that occur near the lunar nodes, causing the Sun or Moon to be obscured:

- **Solar Eclipse**: New Moon near a node (Moon blocks Sun)
- **Lunar Eclipse**: Full Moon near a node (Earth's shadow on Moon)

Key eclipse concepts:
- **Prenatal Eclipse**: The eclipse before your birth (considered karmic/fated)
- **Eclipse Contacts**: When an eclipse hits a natal planet/angle
- **Eclipse Cycles**: Saros series (similar eclipses every 18 years)

#### Why It Matters

Eclipses are **high-intensity lunations** that mark significant life chapters. An eclipse conjunct your natal Sun or Ascendant often correlates with major life changes.

Professional astrologers:
1. Track upcoming eclipses for client forecasting
2. Look at prenatal eclipse for natal chart depth
3. Compare eclipse degrees to natal charts

#### Implementation Approach

**Access Pattern:**

```python
# Find eclipses in a date range
eclipses = Eclipse.find_between("2025-01-01", "2025-12-31")

# Get prenatal eclipse for a chart
prenatal = chart.get_prenatal_eclipse()

# Check if any natal points are eclipse-sensitive this year
contacts = chart.get_eclipse_contacts(year=2025, orb=2.0)
```

**Core Calculation:**

1. Find New/Full Moons in date range (Swiss Ephemeris)
2. Check if Moon is within ~18° of a node (eclipse condition)
3. Calculate eclipse type (total, partial, annular) based on geometry
4. Store eclipse data with Saros series number

**Data Model:**

```python
@dataclass(frozen=True)
class Eclipse:
    datetime: ChartDateTime
    type: EclipseType  # SOLAR_TOTAL, SOLAR_PARTIAL, LUNAR_TOTAL, etc.
    longitude: float  # Zodiac position
    saros_series: int
    magnitude: float  # How much is eclipsed

@dataclass(frozen=True)
class EclipseContact:
    eclipse: Eclipse
    natal_object: str
    orb: float
    applying: bool
```

**Architecture Fit:**

- New `Eclipse` model and finder utilities
- `ChartBuilder` could have `.with_prenatal_eclipse()`
- Component for calculating eclipse contacts
- Report section for eclipse analysis

---

## Medium-Impact Features

These serve specific astrological traditions or use cases. Valuable but more niche.

---

### 5. Planetary Hours and Days

#### What It Is

The **planetary hours** system divides each day into 24 unequal hours, each ruled by a planet in Chaldean order (Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon).

- Day hours: Sunrise to sunset, divided by 12
- Night hours: Sunset to sunrise, divided by 12
- Hours are longer in summer days, shorter in winter days

The **planetary day** is ruled by the planet of its first hour (Sunday = Sun, Monday = Moon, etc.).

#### Why It Matters

Primarily used in **electional astrology** (choosing auspicious times) and **horary astrology**. Also part of magical/talismanic traditions.

"Start your business venture in a Jupiter hour on a Thursday" is practical electional advice.

#### Implementation Approach

```python
# Get current planetary hour
hour = PlanetaryHour.now(location="Seattle, WA")
print(f"Current hour ruled by: {hour.ruler}")

# Get all hours for a day
hours = PlanetaryHour.for_date("2025-01-15", location="Seattle, WA")

# Find next Venus hour
next_venus = PlanetaryHour.next(ruler="Venus", location="Seattle, WA")
```

**Core Calculation:**

1. Calculate sunrise/sunset for date and location (Swiss Ephemeris)
2. Divide daylight period by 12 → day hour length
3. Divide night period by 12 → night hour length
4. Assign rulers starting from the day's ruler in Chaldean order

**Architecture Fit:**

- Standalone utility class (doesn't need to be part of chart)
- Could add to chart metadata: "Chart cast during Mercury hour"
- Simple addition, low complexity

---

### 6. Profections

#### What It Is

**Annual profections** are a traditional timing technique where each year of life activates a different house and its ruler:

- Age 0, 12, 24, 36...: 1st house (self)
- Age 1, 13, 25, 37...: 2nd house (resources)
- Age 2, 14, 26, 38...: 3rd house (communication)
- ... and so on, cycling through all 12 houses

The **Lord of the Year** is the ruler of the profected house.

#### Why It Matters

Profections provide a simple **annual theme** framework. They've experienced a major revival in traditional astrology circles.

"You're in a 10th house year with Saturn as Lord of the Year" immediately frames the year's themes (career focus, Saturn-related challenges/maturation).

#### Implementation Approach

```python
# Get current profection
profection = chart.get_profection(age=32)
print(f"Profected house: {profection.house}")
print(f"Lord of the Year: {profection.lord}")

# Or by date
profection = chart.get_profection(date="2025-06-15")
```

**Core Calculation:**

1. Calculate age at target date
2. `profected_house = (age % 12) + 1`
3. Find ruler of that house in the natal chart

**Data Model:**

```python
@dataclass(frozen=True)
class Profection:
    age: int
    house: int
    lord: str  # Planet ruling that house
    lord_natal_house: int  # Where the lord is natally
    lord_natal_sign: str
```

**Architecture Fit:**

- Method on `CalculatedChart`: `chart.get_profection()`
- Very simple calculation, high value
- Natural addition to yearly forecast reports

---

### 7. Firdaria (Western Time Lords)

#### What It Is

**Firdaria** is a Persian time-lord system assigning planetary periods across the lifespan:

- Each planet rules a period of years
- Day charts and night charts have different sequences
- Periods subdivide into sub-periods ruled by other planets

Example (day chart): Sun (10 years) → Venus (8 years) → Mercury (13 years) → Moon (9 years) → Saturn (11 years) → Jupiter (12 years) → Mars (7 years) → North Node (3 years) → South Node (2 years)

#### Why It Matters

Firdaria provides **long-range timing** - knowing you're in a Saturn period (ages 38-49 for day charts) frames an entire decade. Combined with sub-periods, it offers remarkable timing precision.

Popular in traditional astrology revival. Simpler than Vedic dashas but similar concept.

#### Implementation Approach

```python
# Get current firdaria period
firdaria = chart.get_firdaria(date="2025-01-15")
print(f"Major period: {firdaria.major_lord} ({firdaria.major_start} - {firdaria.major_end})")
print(f"Sub-period: {firdaria.sub_lord}")
```

**Core Calculation:**

1. Determine if day or night chart
2. Apply appropriate sequence and durations
3. Calculate which major period contains the target date
4. Subdivide for sub-period

**Architecture Fit:**

- Method on `CalculatedChart`
- Uses existing sect calculation
- Could integrate with reporting for lifetime timeline

---

### 8. Vimshottari Dasha (Vedic Time Lords)

#### What It Is

The **Vimshottari Dasha** is the primary timing system in Vedic (Jyotish) astrology. It's a 120-year cycle of planetary periods based on the Moon's nakshatra (lunar mansion) at birth.

Periods and durations:
- Ketu: 7 years
- Venus: 20 years
- Sun: 6 years
- Moon: 10 years
- Mars: 7 years
- Rahu: 18 years
- Jupiter: 16 years
- Saturn: 19 years
- Mercury: 17 years

Each period (dasha) subdivides into sub-periods (bhukti), sub-sub-periods (antardasha), etc.

#### Why It Matters

You already support sidereal zodiac and have Vedic users in mind. Vimshottari Dasha is **essential** for Vedic astrology - it's how timing predictions are made.

Without dashas, sidereal support is incomplete for serious Vedic practice.

#### Implementation Approach

```python
# Get current dasha periods
dasha = chart.get_vimshottari_dasha(date="2025-01-15")
print(f"Mahadasha: {dasha.major_lord}")
print(f"Bhukti: {dasha.sub_lord}")
print(f"Antardasha: {dasha.sub_sub_lord}")
```

**Core Calculation:**

1. Get Moon's sidereal longitude
2. Determine nakshatra (27 lunar mansions, 13°20' each)
3. Each nakshatra has a ruling planet - this starts the cycle
4. Calculate elapsed portion of first dasha based on Moon's position within nakshatra
5. Build timeline of all dashas from birth

**Architecture Fit:**

- New component: `VimshottariDashaCalculator`
- Requires `NAKSHATRA_REGISTRY` with rulerships
- Only meaningful for sidereal charts (could warn/error on tropical)
- Report section for dasha timeline

**Complexity Note:**

This is more complex than Western techniques - nakshatras, lordships, and the subdivision math require careful implementation. But it's well-documented and deterministic.

---

### 9. Custom Arabic Parts/Lots

#### What It Is

Arabic Parts (Lots) are calculated points using the formula:

```
Part = Ascendant + Planet A - Planet B
```

You already have 25+ built-in parts. Some astrologers want to:
- Define custom lots from historical texts
- Create research lots for experimentation
- Use tradition-specific variants

#### Why It Matters

The 25 lots you have cover the common ones, but serious traditional practitioners use dozens more. Academic/research users might want to test historical lots.

#### Implementation Approach

```python
# Define a custom lot
custom_lot = ArabicPart(
    name="Part of Cats",
    formula=("ASC", "+", "Moon", "-", "Venus"),
    reverse_by_sect=True  # Flip formula for night charts
)

# Add to calculator
calculator = ArabicPartsCalculator(additional_parts=[custom_lot])

# Or define inline
chart = ChartBuilder.from_native(native) \
    .add_component(ArabicPartsCalculator(
        include_standard=True,
        custom_parts=[
            ("Part of Surgery", "ASC", "+", "Saturn", "-", "Mars"),
        ]
    )) \
    .calculate()
```

**Architecture Fit:**

- Extend existing `ArabicPartsCalculator` to accept custom definitions
- Could load from YAML/JSON for large custom sets
- Low complexity, high flexibility

---

### 10. Antiscia and Contra-Antiscia

#### What It Is

**Antiscia** are mirror points across the Cancer-Capricorn axis (the solstice points):

```
Antiscion of X° = 360° - X° (adjusted to 0-30° scale)
More precisely: Antiscion = Cancer 0° + (Cancer 0° - position)
```

A planet at 10° Taurus has its antiscion at 20° Leo.

**Contra-antiscia** mirror across the Aries-Libra axis (equinox points).

These are "shadow" or "hidden" connections between planets.

#### Why It Matters

Classical technique experiencing revival. Antiscia connections are considered "hidden" relationships - planets in antiscia aspect each other secretly.

Some astrologers find antiscia more reliable than minor aspects.

#### Implementation Approach

```python
# Get antiscia for all planets
antiscia = chart.get_antiscia()
for point in antiscia:
    print(f"{point.planet} antiscion at {point.antiscion_longitude}°")
    if point.conjunct_planet:
        print(f"  → Conjunct {point.conjunct_planet}")

# Check antiscia aspects with orbs
antiscia_aspects = chart.get_antiscia_aspects(orb=1.0)
```

**Core Calculation:**

```python
def calculate_antiscion(longitude: float) -> float:
    """Mirror across Cancer 0° (90°)."""
    return (180 - longitude) % 360

def calculate_contra_antiscion(longitude: float) -> float:
    """Mirror across Aries 0° (0°)."""
    return (360 - longitude) % 360
```

**Architecture Fit:**

- New component: `AntisciaCalculator`
- Simple math, well-defined
- Could add to visualization as dotted aspect lines
- Report section for antiscia connections

---

## Implementation Priority Recommendation

Based on user demand, implementation complexity, and architectural fit:

### Tier 1: Implement First
1. **Solar/Lunar Returns** - Most requested, builds on existing infrastructure
2. **Secondary Progressions** - Completes predictive toolkit
3. **Fixed Stars** - Swiss Ephemeris already supports it

### Tier 2: High Value, Moderate Effort
4. **Profections** - Simple calculation, high value for traditional users
5. **Eclipses** - Important for prediction, well-defined calculations
6. **Planetary Hours** - Simple, useful for electional work

### Tier 3: Specialized Audiences
7. **Antiscia** - Niche but simple to implement
8. **Custom Arabic Parts** - Extend existing component
9. **Firdaria** - Traditional astrology audience

### Tier 4: Complex but Valuable
10. **Vimshottari Dasha** - Complex but essential for Vedic users

---

## Architecture Patterns

All of these features fit cleanly into the existing architecture:

### Factory Methods on ChartBuilder

```python
ChartBuilder.solar_return(natal, year=2025)
ChartBuilder.lunar_return(natal, near_date="2025-01-15")
ChartBuilder.secondary_progression(natal, to_date="2025-06-01")
```

### New Components

```python
.add_component(FixedStarsCalculator())
.add_component(AntisciaCalculator())
.add_component(VimshottariDashaCalculator())
```

### Methods on CalculatedChart

```python
chart.get_profection(age=32)
chart.get_firdaria(date="2025-01-15")
chart.get_prenatal_eclipse()
chart.get_antiscia()
```

### Standalone Utilities

```python
PlanetaryHour.now(location="Seattle, WA")
Eclipse.find_between("2025-01-01", "2025-12-31")
```

The protocol-based architecture makes all of this extensible without breaking changes.

---

*Document written November 2025*
