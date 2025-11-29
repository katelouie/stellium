# The Complete Guide to Profections

## Basic Concept

Profections are a Hellenistic timing technique where the Ascendant (and other points) "move forward" one sign per year, activating houses and their rulers.

---

## Annual Profections (The Foundation)

### The Core Rule

- Age 0: 1st house activated
- Age 1: 2nd house activated
- Age 2: 3rd house activated
- ...
- Age 12: 1st house again (cycle repeats)

**Formula:**

```python
profected_house = (age % 12) + 1
```

### The Time Lord

The **Lord of the Year** = the planet ruling the sign of the profected house.

```python
# Example: Cancer rising, age 30
# 30 % 12 = 6, so 7th house
# 7th house = Capricorn (opposite Cancer)
# Ruler of Capricorn = Saturn
# Saturn is the Lord of the Year
```

### When Does the Profection Year Start?

**Solar return** — not January 1st, not calendar birthday at midnight. The profection year begins at the *exact* moment the Sun returns to its natal position.

(You already have solar returns! This connects nicely.)

---

## Monthly Profections

The year is divided into 12 parts. Each month, the profected point moves forward one sign.

### Method 1: Equal Months (Simple)

- Divide the solar return year into 12 equal periods (~30.4 days each)
- Each period, advance one sign

### Method 2: Solar Ingresses (Traditional)

- Month changes when the Sun ingresses into a new sign
- More astronomically grounded
- Unequal month lengths

### Method 3: Lunar Months (Valens)

Some Hellenistic astrologers used lunations:

- Each New Moon or Full Moon advances the monthly profection

**Monthly Lord:** The ruler of the current monthly sign becomes the **Lord of the Month**.

---

## Daily Profections (For the Obsessive)

### Method 1: Equal Days

- Divide the monthly period by 30
- Each ~1 day, advance by 1°

### Method 2: Subdivide Further

- Each day = 2.5 hours per degree
- This gets VERY granular

Honestly, daily profections are rarely used. Monthly is usually the floor.

---

## Profections from Other Points

Here's where it gets spicy. You can profect from **any point**, not just the Ascendant:

| Profected Point | What It Times |
|-----------------|---------------|
| **Ascendant** | Body, vitality, self, general life direction |
| **Sun** | Career, fame, father, authority, vitality (day charts) |
| **Moon** | Body, mother, emotions, daily life (night charts) |
| **MC** | Career, public life, reputation, achievement |
| **Part of Fortune** | Material fortune, prosperity, body |
| **Part of Spirit** | Mind, intellect, career, actions |
| **Lot of Eros** | Love, desire, relationships |
| **Prenatal Syzygy** | Soul, deeper purpose (per Valens) |

### Sect Consideration

Some astrologers prioritize:

- **Day charts:** Profect from Sun and Fortune
- **Night charts:** Profect from Moon and Spirit

---

## The Activated Planets

It's not just the Lord of the Year. **Any planet in the profected house is also activated.**

```python
def get_activated_planets(chart, age: int) -> list[Planet]:
    profected_house = (age % 12) + 1

    activated = []

    # The ruler is always activated
    house_sign = chart.houses[profected_house].sign
    activated.append(get_ruler(house_sign))

    # Any planet IN that house is also activated
    for planet in chart.planets:
        if planet.house == profected_house:
            activated.append(planet)

    return activated
```

---

## Transmission and Reception (Advanced)

When the **Lord of the Year** makes transits or progressions, they hit harder. But also:

### Transmission

The transiting planets "transmit" their energy to the Lord of the Year. If Mars transits your Lord of the Year, Mars themes activate that year.

### Reception

The Lord of the Year "receives" aspects from transiting planets. A transit to the natal position of your Lord of the Year is particularly significant.

**The profected house is "turned on."** Transits through it are stronger. Transits FROM its ruler are stronger. It's a sensitivity amplifier.

---

## Whole Sign vs Quadrant Houses

**Important debate:**

### Whole Sign (Traditional)

Profections were designed for Whole Sign houses. The 7th house = the 7th sign from the rising sign. Clean, simple.

### Quadrant Houses (Modern Adaptation)

Some modern traditional astrologers profect using Placidus/etc house cusps. This creates edge cases where a planet might be in the 6th house by quadrant but 7th by sign.

**Recommendation:** Offer both. Let the user choose. But default to Whole Sign for profections specifically since that's historically accurate.

---

## Decennials / 10-Year Profections (Rare)

Some systems profect by 10-year periods instead of 1-year:

| Age | House |
|-----|-------|
| 0-9 | 1st |
| 10-19 | 2nd |
| 20-29 | 3rd |
| ... | ... |

These give the "decade lord" — the overarching theme of a 10-year period. The annual profection then operates *within* that context.

---

## Peak Periods (Alfirdaria Intersection)

When the Lord of the Year is ALSO:

- The Firdaria lord
- Activated by Zodiacal Releasing
- Receiving major transits

...that's a **peak period**. Some astrologers track convergences across multiple time-lord systems.

(This is future Stellium work — a "convergence finder.")

---

## Circumambulations (Related Technique)

A circumambulation is when a profected point "walks" through houses and encounters natal planets or points.

**Example:** You're in a 7th house profection year. As the year progresses (monthly profections), the point walks through houses 7 → 8 → 9 → etc. When it crosses your natal Saturn at age 30, month 4, that month is Saturn-flavored.

This is basically monthly/daily profections with an awareness of what natal planets they're passing over.

---

## Implementation Spec for Stellium

### Data Model

```python
@dataclass
class ProfectionResult:
    # Annual
    age: int
    annual_house: int  # 1-12
    annual_sign: Sign
    lord_of_year: Planet

    # Planets activated by presence in house
    activated_planets: list[Planet]

    # Optional: monthly
    monthly_house: int | None
    monthly_sign: Sign | None
    lord_of_month: Planet | None

    # Optional: which point was profected
    profected_point: str  # "ASC", "Sun", "Moon", "MC", "Fortune", etc.

    # Metadata
    solar_return_date: datetime  # When this profection year started
    house_system: str  # "whole_sign" recommended
```

### API Ideas

```python
# Basic
chart.profection(age=30)  # Returns ProfectionResult from ASC

# From different points
chart.profection(age=30, point="MC")
chart.profection(age=30, point="Fortune")

# With monthly
chart.profection(age=30, include_monthly=True, date="2025-06-15")

# Multiple points at once
chart.profections(age=30, points=["ASC", "Sun", "Moon", "MC", "Fortune"])

# Range (for timeline visualization)
chart.profection_timeline(start_age=25, end_age=35)
```

### Report Section

```
☆ PROFECTIONS (Age 30)

Annual Profection:
  Profected House:     7th House (Capricorn)
  Lord of the Year:    ♄ Saturn
  Saturn's Condition:  Fall, Peregrine, 10th House, Direct

Activated Planets:
  ♄ Saturn (by rulership)
  ♂ Mars (in 7th house natally)

Monthly Profection (as of June 2025):
  Profected House:     11th House (Taurus)
  Lord of the Month:   ♀ Venus

Key Transits to Lord of Year:
  ♄ Saturn is currently at 14° Pisces
  Transiting ♃ Jupiter will conjoin natal ♄ Saturn in August 2025
```

---

### Visualization Ideas

**The Profection Wheel:**
A simplified wheel showing just the 12 houses with the current profected house highlighted. Maybe with the Lord of Year glyph in the center.

**Timeline View:**

```
Age 28  │ 5th House │ ♂ Mars      │ 2022-2023
Age 29  │ 6th House │ ♃ Jupiter   │ 2023-2024
Age 30  │ 7th House │ ♄ Saturn    │ 2024-2025  ← Current
Age 31  │ 8th House │ ♄ Saturn    │ 2025-2026
Age 32  │ 9th House │ ♃ Jupiter   │ 2026-2027
```

---

## Edge Cases

| Case | How to Handle |
|------|---------------|
| **Traditional vs modern rulers** | Offer both; default traditional for profections |
| **Whole sign vs quadrant** | Default whole sign; option for quadrant |
| **What if birth time unknown?** | Can't profect (ASC unknown), or profect from Sun only |
| **Leap years / solar return precision** | Use actual solar return moment, not calendar birthday |
| **Age 0 = 1st house or starts at age 1?** | Age 0 = 1st house (you're IN your first year of life) |

---

## Testing Checklist

- [ ] Age 0 → 1st house
- [ ] Age 11 → 12th house
- [ ] Age 12 → 1st house (cycle)
- [ ] Age 30 → 7th house (30 % 12 = 6, + 1 = 7)
- [ ] Correct lord for each sign
- [ ] Traditional vs modern ruler toggle
- [ ] Planets in profected house are found
- [ ] Monthly profections advance correctly
- [ ] Works from different points (MC, Sun, etc.)
- [ ] Whole sign vs quadrant house option

---

## Priority Implementation Order

1. **Annual profection from ASC** — the core feature
2. **Lord of the Year with dignity info** — what condition is the lord in?
3. **Activated natal planets** — what else is in that house?
4. **Profection from other points** — MC, Sun, Moon, Fortune
5. **Monthly profections** — with both equal and ingress methods
6. **Profection timeline/range** — for visualization
7. **Convergence detection** — when Lord of Year is also getting major transits

---
---

# Progressive Profection Implementation Strategy

## The Core Insight

A profection is fundamentally:

> **"Take a point. Move it forward N signs. Find what's there."**

Everything else — annual, monthly, Lord of the Year, activated planets — is just *asking questions* about that result.

---

## Layer 0: The Primitive

One tiny function that does the actual math:

```python
def profect_position(
    starting_sign_index: int,  # 0-11 (Aries=0 or house 1=0, depending on use)
    units: int,                # How many signs to move forward
) -> int:
    """Returns the sign/house index after profecting forward N units."""
    return (starting_sign_index + units) % 12
```

That's it. That's the atom everything else is built on.

---

## Layer 1: The Profection Engine

A general-purpose profection calculator that doesn't assume *what* you're profecting or *why*:

```python
@dataclass
class ProfectionResult:
    """The result of profecting any point by any amount."""

    # What was profected
    source_point: str                    # "ASC", "Sun", "MC", "Fortune", etc.
    source_sign: Sign
    source_house: int                    # 1-12

    # The profection parameters
    units: int                           # How many signs forward
    unit_type: str                       # "year", "month", "day", "decade"

    # The result
    profected_sign: Sign
    profected_house: int                 # 1-12 (which house from the natal ASC)

    # What rules this profected sign
    ruler: Planet                        # Traditional ruler
    ruler_modern: Planet | None          # Modern ruler (if different)

    # What natal planets are activated
    planets_in_sign: list[CelestialPosition]   # Natal planets in profected sign
    planets_in_house: list[CelestialPosition]  # Natal planets in profected house


class ProfectionEngine:
    """General-purpose profection calculator."""

    def __init__(
        self,
        chart: Chart,
        house_system: str = "whole_sign",      # Which houses to use
        rulership_scheme: str = "traditional",  # "traditional" | "modern"
    ):
        self.chart = chart
        self.house_system = house_system
        self.rulership_scheme = rulership_scheme

    def profect(
        self,
        point: str,              # What to profect: "ASC", "Sun", "Moon", "MC", "Fortune", etc.
        units: int,              # How many signs to move
        unit_type: str = "year", # Label for metadata
    ) -> ProfectionResult:
        """
        The core profection operation.

        Profects any point forward by N signs and returns
        everything you'd want to know about the result.
        """
        # Get starting position
        source = self._get_point_position(point)
        source_sign_index = self._sign_to_index(source.sign)

        # Do the profection
        profected_sign_index = (source_sign_index + units) % 12
        profected_sign = self._index_to_sign(profected_sign_index)

        # Find the house (from natal ASC perspective)
        profected_house = self._sign_to_house(profected_sign)

        # Get rulers
        ruler = self._get_ruler(profected_sign, "traditional")
        ruler_modern = self._get_ruler(profected_sign, "modern")
        if ruler == ruler_modern:
            ruler_modern = None

        # Find activated planets
        planets_in_sign = self._get_planets_in_sign(profected_sign)
        planets_in_house = self._get_planets_in_house(profected_house)

        return ProfectionResult(
            source_point=point,
            source_sign=source.sign,
            source_house=source.house,
            units=units,
            unit_type=unit_type,
            profected_sign=profected_sign,
            profected_house=profected_house,
            ruler=ruler,
            ruler_modern=ruler_modern,
            planets_in_sign=planets_in_sign,
            planets_in_house=planets_in_house,
        )
```

**Notice:** This doesn't know about "age" or "years" or "months" yet. It just profects a point by N signs. The semantics come later.

---

## Layer 2: Convenience Methods

Now we add the human-friendly wrappers that know about years, months, ages:

```python
class ProfectionEngine:
    # ... Layer 1 code above ...

    # === ANNUAL PROFECTIONS ===

    def annual(
        self,
        age: int,
        point: str = "ASC",
    ) -> ProfectionResult:
        """
        Annual profection for a given age.

        Age 0 = 1st house, Age 1 = 2nd house, etc.
        """
        return self.profect(point=point, units=age, unit_type="year")

    def lord_of_year(self, age: int) -> Planet:
        """Convenience: just get the Lord of the Year."""
        return self.annual(age).ruler

    # === MONTHLY PROFECTIONS ===

    def monthly(
        self,
        age: int,
        month: int,  # 0-11 within the year
        point: str = "ASC",
    ) -> ProfectionResult:
        """
        Monthly profection.

        Month 0 = same as annual sign, Month 1 = next sign, etc.
        """
        total_units = age + month  # or age * 1 + month, conceptually
        # Wait, actually monthly is WITHIN the year, so:
        annual_result = self.annual(age, point)

        # Monthly profects forward from the annual position
        return self.profect(
            point=point,
            units=age,  # Get to the year
            unit_type="month",
            # Hmm, we need to rethink this...
        )
```

Actually, let me reconsider the monthly model:

```python
    def monthly(
        self,
        age: int,
        month: int,  # 0-11 (month within the profection year)
        point: str = "ASC",
    ) -> ProfectionResult:
        """
        Monthly profection within a given year.

        The annual profection sets the starting sign for the year.
        Each month advances one more sign.
        """
        total_signs = age + month
        return self.profect(point=point, units=total_signs, unit_type="month")

    def lord_of_month(self, age: int, month: int) -> Planet:
        """Convenience: just get the Lord of the Month."""
        return self.monthly(age, month).ruler
```

---

## Layer 3: Date-Aware Methods

Now we add methods that figure out age/month from actual dates:

```python
class ProfectionEngine:
    # ... Layers 1-2 above ...

    def for_date(
        self,
        date: datetime,
        point: str = "ASC",
        include_monthly: bool = False,
    ) -> ProfectionResult | tuple[ProfectionResult, ProfectionResult]:
        """
        Calculate profections for a specific date.

        Automatically determines:
        - Current age
        - Current month within profection year
        """
        # Get exact solar return to determine profection year
        age = self._calculate_age_at_date(date)

        annual = self.annual(age, point)

        if not include_monthly:
            return annual

        month = self._calculate_month_in_profection_year(date)
        monthly = self.monthly(age, month, point)

        return annual, monthly

    def _calculate_age_at_date(self, date: datetime) -> int:
        """Calculate completed years since birth."""
        birth = self.chart.native.datetime
        # Account for whether birthday has passed this year
        age = date.year - birth.year
        if (date.month, date.day) < (birth.month, birth.day):
            age -= 1
        return age

    def _calculate_month_in_profection_year(self, date: datetime) -> int:
        """
        Calculate which month (0-11) within the current profection year.

        Options:
        - Equal division (year / 12)
        - Solar ingresses
        - Lunar months
        """
        # Default: equal division from solar return
        solar_return = self._get_solar_return_for_year(date.year)
        days_since_return = (date - solar_return).days
        month = int(days_since_return / (365.25 / 12))
        return min(month, 11)  # Clamp to 0-11
```

---

## Layer 4: Multi-Point Profections

Profect multiple points at once:

```python
@dataclass
class MultiProfectionResult:
    """Profections from multiple points for the same time period."""
    age: int
    date: datetime | None
    results: dict[str, ProfectionResult]  # keyed by point name

    @property
    def lords(self) -> dict[str, Planet]:
        """All the lords, by point."""
        return {point: r.ruler for point, r in self.results.items()}


class ProfectionEngine:
    # ... Layers 1-3 above ...

    def multi(
        self,
        age: int,
        points: list[str] = ["ASC", "Sun", "Moon", "MC", "Fortune"],
    ) -> MultiProfectionResult:
        """Profect multiple points at once."""
        results = {
            point: self.annual(age, point)
            for point in points
        }
        return MultiProfectionResult(age=age, date=None, results=results)

    def multi_for_date(
        self,
        date: datetime,
        points: list[str] = ["ASC", "Sun", "Moon", "MC", "Fortune"],
    ) -> MultiProfectionResult:
        """Profect multiple points for a specific date."""
        age = self._calculate_age_at_date(date)
        result = self.multi(age, points)
        result.date = date
        return result
```

---

## Layer 5: Timeline / Range

For visualizations and analysis:

```python
@dataclass
class ProfectionTimeline:
    """A range of profections over time."""
    point: str
    entries: list[ProfectionResult]

    def lords_sequence(self) -> list[Planet]:
        return [e.ruler for e in self.entries]


class ProfectionEngine:
    # ... Layers 1-4 above ...

    def timeline(
        self,
        start_age: int,
        end_age: int,
        point: str = "ASC",
    ) -> ProfectionTimeline:
        """Generate profections for a range of ages."""
        entries = [
            self.annual(age, point)
            for age in range(start_age, end_age + 1)
        ]
        return ProfectionTimeline(point=point, entries=entries)
```

---

## Layer 6: Integration with Chart API

Finally, wire it into `Chart` for easy access:

```python
class Chart:
    # ... existing code ...

    def profection(
        self,
        age: int | None = None,
        date: datetime | None = None,
        point: str = "ASC",
        include_monthly: bool = False,
        house_system: str = "whole_sign",
        rulership: str = "traditional",
    ) -> ProfectionResult:
        """
        Calculate profections for this chart.

        Either age or date must be provided.
        """
        engine = ProfectionEngine(
            self,
            house_system=house_system,
            rulership_scheme=rulership,
        )

        if date:
            return engine.for_date(date, point, include_monthly)
        elif age is not None:
            if include_monthly:
                raise ValueError("Monthly profections require a date, not just age")
            return engine.annual(age, point)
        else:
            raise ValueError("Either age or date must be provided")

    def profections(
        self,
        age: int | None = None,
        date: datetime | None = None,
        points: list[str] = ["ASC", "Sun", "Moon", "MC", "Fortune"],
        **kwargs,
    ) -> MultiProfectionResult:
        """Profect multiple points at once."""
        engine = ProfectionEngine(self, **kwargs)

        if date:
            return engine.multi_for_date(date, points)
        elif age is not None:
            return engine.multi(age, points)
        else:
            raise ValueError("Either age or date must be provided")

    def profection_timeline(
        self,
        start_age: int,
        end_age: int,
        point: str = "ASC",
        **kwargs,
    ) -> ProfectionTimeline:
        """Generate a range of annual profections."""
        engine = ProfectionEngine(self, **kwargs)
        return engine.timeline(start_age, end_age, point)
```

---

## The Architecture Recap

```
┌─────────────────────────────────────────────────────────────┐
│                      Chart API (Layer 6)                     │
│         .profection()  .profections()  .profection_timeline()│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ProfectionEngine (Layers 1-5)              │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: .timeline()         Range/visualization             │
│ Layer 4: .multi()            Multiple points                 │
│ Layer 3: .for_date()         Date-aware calculation          │
│ Layer 2: .annual() .monthly()   Human-friendly wrappers      │
│ Layer 1: .profect()          Core engine (point + N signs)   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              profect_position() (Layer 0)                    │
│                   (index + units) % 12                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

| Phase | What | Time |
|-------|------|------|
| **1** | Layer 0 + Layer 1: `profect()` core | 1-2 hours |
| **2** | Layer 2: `.annual()`, `.lord_of_year()` | 30 min |
| **3** | Tests for annual profections | 30 min |
| **4** | Layer 6: Wire into `Chart` | 30 min |
| **CHECKPOINT** | *You now have shippable annual profections* | |
| **5** | Layer 2 continued: `.monthly()` | 1 hour |
| **6** | Layer 3: `.for_date()` | 1 hour |
| **7** | Layer 4: `.multi()` | 30 min |
| **8** | Layer 5: `.timeline()` | 30 min |
| **9** | Report section | 1 hour |

---

## Future Extensions (No Refactoring Needed)

Because the core `profect()` is generic, adding these later is easy:

| Feature | How |
|---------|-----|
| **Daily profections** | `.daily(age, month, day)` → calls `profect(units=age*12*30 + month*30 + day)` |
| **Decennial profections** | `.decennial(age)` → calls `profect(units=age // 10)` |
| **Custom sub-periods** | Just pass different unit counts to `profect()` |
| **Different month methods** | Add a `month_method` param to `monthly()` |
| **Profected angles** | Already works — just pass `point="MC"` |
| **Profected lots** | Add lot positions to `_get_point_position()` |

---

This is the Stellium way: **general engine, specific conveniences**.

Ready to start with Layer 0 + 1? 🚀
