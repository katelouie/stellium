# Stellium Report Generation Guide

This guide covers everything you need to know about generating professional astrological reports with Stellium, from simple terminal output to beautiful PDF documents.

## Table of Contents

- [Quick Start](#quick-start)
- [The ReportBuilder Pattern](#the-reportbuilder-pattern)
- [Report Sections](#report-sections)
  - [Chart Overview](#chart-overview)
  - [Planet Positions](#planet-positions)
  - [Aspects](#aspects)
  - [Cross-Chart Aspects](#cross-chart-aspects)
  - [House Cusps](#house-cusps)
  - [Declinations](#declinations)
  - [Moon Phase](#moon-phase)
  - [Essential Dignities](#essential-dignities)
  - [Aspect Patterns](#aspect-patterns)
  - [Midpoints](#midpoints)
  - [Transit Timeline (Natal Transits)](#transit-timeline-natal-transits)
- [Presets](#presets)
- [Output Formats](#output-formats)
  - [Terminal Output (Rich)](#terminal-output-rich)
  - [Plain Text](#plain-text)
  - [PDF with Typst](#pdf-with-typst)
  - [HTML](#html)
- [Comparison Chart Reports](#comparison-chart-reports)
- [Custom Sections](#custom-sections)
- [Complete Examples](#complete-examples)

---

## Quick Start

```python
from stellium import ChartBuilder, ReportBuilder

# Calculate a chart
chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

# Generate a report and display in terminal
ReportBuilder().from_chart(chart).preset_standard().render()

# Generate chart SVG, then create a PDF report with the chart embedded
chart.draw("einstein_chart.svg").save()
ReportBuilder().from_chart(chart).preset_detailed().with_chart_image("einstein_chart.svg").render(
    format="pdf",
    file="einstein_report.pdf",
)
```
<!--pytest-codeblocks:expected-output-->
```

Chart Overview
──────────────
Name: Albert Einstein
Date: March 14, 1879
Time: 11:30 AM
Timezone: Europe/Berlin
Location: Ulm, Germany
Coordinates: 48.3984°, 9.9916°
House System: Placidus
Zodiac: Tropical
Chart Ruler: Moon (Cancer Rising)

Planet Positions
────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Planet              ┃ Position              ┃ House (Pl) ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ☉ Sun               │ ♓︎ Pisces 23°30'      │ 10         │
│ ☽ Moon              │ ♐︎ Sagittarius 14°31' │ 6          │
│ ☿ Mercury           │ ♈︎ Aries 3°08'        │ 10         │
│ ♀ Venus             │ ♈︎ Aries 16°59'       │ 10         │
│ ♂ Mars              │ ♑︎ Capricorn 26°54'   │ 7          │
│ ♃ Jupiter           │ ♒︎ Aquarius 27°29'    │ 9          │
│ ♄ Saturn            │ ♈︎ Aries 4°11'        │ 10         │
│ ♅ Uranus            │ ♍︎ Virgo 1°17'        │ 3          │
│ ♆ Neptune           │ ♉︎ Taurus 7°52'       │ 11         │
│ ♇ Pluto             │ ♉︎ Taurus 24°43'      │ 11         │
│ ☊ North Node        │ ♒︎ Aquarius 2°43'     │ 8          │
│ ☋ South Node        │ ♌︎ Leo 2°43'          │ 2          │
│ ⚸ Black Moon Lilith │ ♈︎ Aries 27°58'       │ 11         │
│ 🜊 Vertex            │ ♏︎ Scorpio 27°54'     │ 5          │
│ ⚷ Chiron            │ ♉︎ Taurus 5°32'       │ 11         │
└─────────────────────┴───────────────────────┴────────────┘

Major Aspects
─────────────

  Aspectarian
[SVG: 404x404px - use HTML/PDF output to view]

  Aspect List
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Planet 1            ┃ Aspect        ┃ Planet 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☿ Mercury           │ ⚹ Sextile     │ ☊ North Node        │ 0.41° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ ☋ South Node        │ 0.41° │ ←S       │
│ ♃ Jupiter           │ □ Square      │ 🜊 Vertex            │ 0.42° │ —        │
│ ♃ Jupiter           │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 0.49° │ A→       │
│ ♂ Mars              │ ⚹ Sextile     │ 🜊 Vertex            │ 0.99° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ♄ Saturn            │ 1.05° │ A→       │
│ ♂ Mars              │ □ Square      │ ⚸ Black Moon Lilith │ 1.06° │ A→       │
│ ☉ Sun               │ ⚹ Sextile     │ ♇ Pluto             │ 1.22° │ A→       │
│ ♄ Saturn            │ ⚹ Sextile     │ ☊ North Node        │ 1.46° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ☋ South Node        │ 1.46° │ ←S       │
│ ☽ Moon              │ □ Square      │ MC                  │ 1.69° │ —        │
│ ♂ Mars              │ △ Trine       │ ♇ Pluto             │ 2.19° │ ←S       │
│ ♆ Neptune           │ ☌ Conjunction │ ⚷ Chiron            │ 2.33° │ A→       │
│ ☽ Moon              │ △ Trine       │ ♀ Venus             │ 2.46° │ A→       │
│ ♃ Jupiter           │ □ Square      │ ♇ Pluto             │ 2.76° │ ←S       │
│ ⚷ Chiron            │ □ Square      │ ☋ South Node        │ 2.81° │ ←S       │
│ ☊ North Node        │ □ Square      │ ⚷ Chiron            │ 2.81° │ ←S       │
│ ♇ Pluto             │ ☍ Opposition  │ 🜊 Vertex            │ 3.18° │ —        │
│ ♅ Uranus            │ △ Trine       │ ⚸ Black Moon Lilith │ 3.31° │ A→       │
│ ♅ Uranus            │ □ Square      │ 🜊 Vertex            │ 3.38° │ —        │
│ ☉ Sun               │ ⚹ Sextile     │ ♂ Mars              │ 3.41° │ A→       │
│ ♆ Neptune           │ ⚹ Sextile     │ ASC                 │ 3.77° │ —        │
│ ♃ Jupiter           │ ☍ Opposition  │ ♅ Uranus            │ 3.80° │ A→       │
│ ♅ Uranus            │ △ Trine       │ ⚷ Chiron            │ 4.26° │ ←S       │
│ ☉ Sun               │ △ Trine       │ 🜊 Vertex            │ 4.40° │ —        │
│ ⚸ Black Moon Lilith │ □ Square      │ ☋ South Node        │ 4.75° │ A→       │
│ ☊ North Node        │ □ Square      │ ⚸ Black Moon Lilith │ 4.75° │ A→       │
│ ☋ South Node        │ △ Trine       │ 🜊 Vertex            │ 4.83° │ —        │
│ ☊ North Node        │ ⚹ Sextile     │ 🜊 Vertex            │ 4.83° │ —        │
│ ♆ Neptune           │ ⚹ Sextile     │ MC                  │ 4.97° │ —        │
│ ♆ Neptune           │ □ Square      │ ☋ South Node        │ 5.14° │ ←S       │
│ ♆ Neptune           │ □ Square      │ ☊ North Node        │ 5.14° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ 🜊 Vertex            │ 5.24° │ —        │
│ ♀ Venus             │ □ Square      │ ASC                 │ 5.34° │ —        │
│ ♂ Mars              │ ☌ Conjunction │ ☊ North Node        │ 5.82° │ A→       │
│ ♂ Mars              │ ☍ Opposition  │ ☋ South Node        │ 5.82° │ A→       │
│ ♄ Saturn            │ △ Trine       │ 🜊 Vertex            │ 6.29° │ —        │
│ ♅ Uranus            │ □ Square      │ ♇ Pluto             │ 6.56° │ A→       │
│ ♅ Uranus            │ △ Trine       │ ♆ Neptune           │ 6.58° │ ←S       │
│ ♄ Saturn            │ □ Square      │ ASC                 │ 7.46° │ —        │
│ ⚷ Chiron            │ ☌ Conjunction │ ⚸ Black Moon Lilith │ 7.57° │ A→       │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘

House Cusps
───────────
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ House ┃ Cusp (Pl)  ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ 11° ♋︎ 38' │
│ 2     │ 28° ♋︎ 36' │
│ 3     │ 17° ♌︎ 48' │
│ 4     │ 12° ♍︎ 50' │
│ 5     │ 18° ♎︎ 19' │
│ 6     │ 3° ♐︎ 06'  │
│ 7     │ 11° ♑︎ 38' │
│ 8     │ 28° ♑︎ 36' │
│ 9     │ 17° ♒︎ 48' │
│ 10    │ 12° ♓︎ 50' │
│ 11    │ 18° ♈︎ 19' │
│ 12    │ 3° ♊︎ 06'  │
└───────┴────────────┘
```

---

## The ReportBuilder Pattern

ReportBuilder uses a fluent interface (method chaining) to construct reports. The pattern is:

1. **Create** a ReportBuilder
2. **Set** the chart with `.from_chart()`
3. **Add** sections with `.with_*()` methods (or use a preset)
4. **Render** with `.render()`

```python
from stellium import ChartBuilder, ReportBuilder

chart = ChartBuilder.from_notable("Ada Lovelace").with_aspects().calculate()

# Build a custom report
report = (
    ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions(include_speed=True)
    .with_aspects(mode="major")
    .with_house_cusps()
    .render(format="rich_table")
)
```
<!--pytest-codeblocks:expected-output-->
```

Chart Overview
──────────────
Name: Ada Lovelace
Date: December 10, 1815
Time: 01:00 PM
Timezone: Europe/London
Location: London, England
Coordinates: 51.5000°, -0.1667°
House System: Placidus
Zodiac: Tropical
Chart Ruler: Mars (Aries Rising)

Planet Positions
────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Planet              ┃ Position              ┃ House (Pl) ┃ Speed        ┃ Motion     ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ☉ Sun               │ ♐︎ Sagittarius 17°40' │ 9          │ 1.0168°/day  │ Direct     │
│ ☽ Moon              │ ♈︎ Aries 5°39'        │ 12         │ 12.1330°/day │ Direct     │
│ ☿ Mercury           │ ♐︎ Sagittarius 0°31'  │ 8          │ 1.4360°/day  │ Direct     │
│ ♀ Venus             │ ♏︎ Scorpio 1°32'      │ 7          │ 0.9000°/day  │ Direct     │
│ ♂ Mars              │ ♈︎ Aries 20°23'       │ 1          │ 0.2565°/day  │ Direct     │
│ ♃ Jupiter           │ ♏︎ Scorpio 2°14'      │ 7          │ 0.1818°/day  │ Direct     │
│ ♄ Saturn            │ ♒︎ Aquarius 8°34'     │ 11         │ 0.0895°/day  │ Direct     │
│ ♅ Uranus            │ ♐︎ Sagittarius 7°48'  │ 8          │ 0.0608°/day  │ Direct     │
│ ♆ Neptune           │ ♐︎ Sagittarius 19°34' │ 9          │ 0.0378°/day  │ Direct     │
│ ♇ Pluto             │ ♓︎ Pisces 20°53'      │ 12         │ 0.0019°/day  │ Direct     │
│ ☊ North Node        │ ♊︎ Gemini 24°46'      │ 3          │ -0.0095°/day │ Retrograde │
│ ☋ South Node        │ ♐︎ Sagittarius 24°46' │ 9          │ 0.0095°/day  │ Direct     │
│ ⚸ Black Moon Lilith │ ♓︎ Pisces 3°54'       │ 12         │ 0.1119°/day  │ Direct     │
│ 🜊 Vertex            │ ♎︎ Libra 2°44'        │ 6          │ 0.0000°/day  │ Direct     │
│ ⚷ Chiron            │ ♓︎ Pisces 9°23'       │ 12         │ 0.0193°/day  │ Direct     │
└─────────────────────┴───────────────────────┴────────────┴──────────────┴────────────┘

Major Aspects
─────────────

  Aspectarian
[SVG: 404x404px - use HTML/PDF output to view]

  Aspect List
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Planet 1            ┃ Aspect        ┃ Planet 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ♅ Uranus            │ △ Trine       │ ASC                 │ 0.29° │ —        │
│ MC                  │ □ Square      │ 🜊 Vertex            │ 0.36° │ —        │
│ ♄ Saturn            │ ⚹ Sextile     │ ASC                 │ 0.49° │ —        │
│ ♀ Venus             │ ☌ Conjunction │ ♃ Jupiter           │ 0.71° │ A→       │
│ ♄ Saturn            │ ⚹ Sextile     │ ♅ Uranus            │ 0.78° │ ←S       │
│ ⚸ Black Moon Lilith │ ⚹ Sextile     │ MC                  │ 0.81° │ —        │
│ ♂ Mars              │ △ Trine       │ ♆ Neptune           │ 0.82° │ ←S       │
│ ♃ Jupiter           │ ⚹ Sextile     │ MC                  │ 0.86° │ —        │
│ ♆ Neptune           │ □ Square      │ ♇ Pluto             │ 1.31° │ —        │
│ ♀ Venus             │ ⚹ Sextile     │ MC                  │ 1.57° │ —        │
│ ♅ Uranus            │ □ Square      │ ⚷ Chiron            │ 1.59° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ⚸ Black Moon Lilith │ 1.67° │ A→       │
│ ☉ Sun               │ ☌ Conjunction │ ♆ Neptune           │ 1.90° │ A→       │
│ ☽ Moon              │ △ Trine       │ ♅ Uranus            │ 2.14° │ A→       │
│ ☿ Mercury           │ ⚹ Sextile     │ 🜊 Vertex            │ 2.21° │ —        │
│ ♀ Venus             │ △ Trine       │ ⚸ Black Moon Lilith │ 2.38° │ A→       │
│ ☽ Moon              │ ☌ Conjunction │ ASC                 │ 2.43° │ —        │
│ ☽ Moon              │ □ Square      │ MC                  │ 2.55° │ —        │
│ ☉ Sun               │ △ Trine       │ ♂ Mars              │ 2.72° │ A→       │
│ ☽ Moon              │ ☍ Opposition  │ 🜊 Vertex            │ 2.92° │ —        │
│ ☽ Moon              │ ⚹ Sextile     │ ♄ Saturn            │ 2.92° │ A→       │
│ ☉ Sun               │ □ Square      │ ♇ Pluto             │ 3.21° │ —        │
│ ☿ Mercury           │ □ Square      │ ⚸ Black Moon Lilith │ 3.38° │ A→       │
│ ♅ Uranus            │ □ Square      │ ⚸ Black Moon Lilith │ 3.88° │ A→       │
│ ♇ Pluto             │ □ Square      │ ☋ South Node        │ 3.90° │ —        │
│ ♇ Pluto             │ □ Square      │ ☊ North Node        │ 3.90° │ —        │
│ ♂ Mars              │ ⚹ Sextile     │ ☊ North Node        │ 4.39° │ A→       │
│ ♂ Mars              │ △ Trine       │ ☋ South Node        │ 4.39° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ 🜊 Vertex            │ 5.06° │ —        │
│ ☽ Moon              │ △ Trine       │ ☿ Mercury           │ 5.13° │ ←S       │
│ ♆ Neptune           │ ☌ Conjunction │ ☋ South Node        │ 5.21° │ A→       │
│ ♆ Neptune           │ ☍ Opposition  │ ☊ North Node        │ 5.21° │ A→       │
│ ASC                 │ ☍ Opposition  │ 🜊 Vertex            │ 5.35° │ —        │
│ ⚷ Chiron            │ ☌ Conjunction │ ⚸ Black Moon Lilith │ 5.47° │ A→       │
│ ♄ Saturn            │ △ Trine       │ 🜊 Vertex            │ 5.84° │ —        │
│ ♃ Jupiter           │ □ Square      │ ♄ Saturn            │ 6.33° │ A→       │
│ ♀ Venus             │ △ Trine       │ ☊ North Node        │ 6.76° │ ←S       │
│ ♀ Venus             │ □ Square      │ ♄ Saturn            │ 7.04° │ A→       │
│ ☉ Sun               │ ☌ Conjunction │ ☋ South Node        │ 7.11° │ A→       │
│ ☉ Sun               │ ☍ Opposition  │ ☊ North Node        │ 7.11° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ⚷ Chiron            │ 7.14° │ A→       │
│ ☿ Mercury           │ ☌ Conjunction │ ♅ Uranus            │ 7.27° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ☊ North Node        │ 7.46° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ ASC                 │ 7.56° │ —        │
│ ♀ Venus             │ △ Trine       │ ⚷ Chiron            │ 7.85° │ A→       │
│ ☋ South Node        │ □ Square      │ 🜊 Vertex            │ 7.96° │ —        │
│ ☊ North Node        │ □ Square      │ 🜊 Vertex            │ 7.96° │ —        │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘

House Cusps
───────────
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ House ┃ Cusp (Pl)  ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ 8° ♈︎ 05'  │
│ 2     │ 22° ♉︎ 13' │
│ 3     │ 15° ♊︎ 11' │
│ 4     │ 3° ♋︎ 06'  │
│ 5     │ 21° ♋︎ 36' │
│ 6     │ 17° ♌︎ 06' │
│ 7     │ 8° ♎︎ 05'  │
│ 8     │ 22° ♏︎ 13' │
│ 9     │ 15° ♐︎ 11' │
│ 10    │ 3° ♑︎ 06'  │
│ 11    │ 21° ♑︎ 36' │
│ 12    │ 17° ♒︎ 06' │
└───────┴────────────┘
```

### Method Chaining

Every `.with_*()` method returns `self`, so you can chain them:

```python
# These are equivalent:
builder = ReportBuilder()
builder.from_chart(chart)
builder.with_chart_overview()
builder.with_planet_positions()
builder.render()

# Chained (preferred style):
ReportBuilder().from_chart(chart).with_chart_overview().with_planet_positions().render()
```

---

## Report Sections

### Chart Overview

Basic information about the chart: name, date, time, location, house system, zodiac type.

```python
ReportBuilder().from_chart(chart).with_chart_overview().render()
```

**Output includes:**
- Name (if available)
- Date and time
- Timezone
- Location and coordinates
- House system(s)
- Zodiac type (Tropical/Sidereal)
- Ayanamsa (for sidereal charts)
- Chart sect (day/night, if dignities calculated)

For **comparison charts**, shows information for both charts plus the comparison type.

---

### Planet Positions

Table of planetary positions with sign, degree, and optional house placement.

```python
# Basic: just positions
ReportBuilder().from_chart(chart).with_planet_positions().render()

# With speed (shows retrograde status)
ReportBuilder().from_chart(chart).with_planet_positions(include_speed=True).render()

# With house placements
ReportBuilder().from_chart(chart).with_planet_positions(include_house=True).render()

# Specific house systems only
ReportBuilder().from_chart(chart).with_planet_positions(
    include_house=True,
    house_systems=["Placidus", "Whole Sign"]
).render()

# All options
ReportBuilder().from_chart(chart).with_planet_positions(
    include_speed=True,
    include_house=True,
    house_systems="all"  # Show all calculated systems
).render()
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_speed` | `bool` | `False` | Show speed in longitude and retrograde status |
| `include_house` | `bool` | `True` | Show house placement |
| `house_systems` | `str \| list[str]` | `"all"` | Which house systems: `"all"`, specific list, or `None` for default only |

**Output columns:**
- Planet (with glyph)
- Position (sign glyph + degree°minute')
- House (one column per system, if enabled)
- Speed (degrees/day, if enabled)
- Motion (Direct/Retrograde, if enabled)

---

### Aspects

Table of aspects between planets.

```python
# All aspects, sorted by orb (tightest first)
ReportBuilder().from_chart(chart).with_aspects().render()

# Major aspects only (conjunction, sextile, square, trine, opposition)
ReportBuilder().from_chart(chart).with_aspects(mode="major").render()

# Minor aspects only
ReportBuilder().from_chart(chart).with_aspects(mode="minor").render()

# Harmonic aspects only
ReportBuilder().from_chart(chart).with_aspects(mode="harmonic").render()

# Sort by planet instead of orb
ReportBuilder().from_chart(chart).with_aspects(sort_by="planet").render()

# Sort by aspect type
ReportBuilder().from_chart(chart).with_aspects(sort_by="aspect_type").render()

# Hide orb column
ReportBuilder().from_chart(chart).with_aspects(orbs=False).render()
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `str` | `"all"` | Filter: `"all"`, `"major"`, `"minor"`, `"harmonic"` |
| `orbs` | `bool` | `True` | Show orb and applying/separating indicator |
| `sort_by` | `str` | `"orb"` | Sort order: `"orb"`, `"planet"`, `"aspect_type"` |

**Output columns:**
- Planet 1 (with glyph)
- Aspect (with glyph)
- Planet 2 (with glyph)
- Orb (if enabled)
- Applying (A→ or ←S, if enabled)

---

### Cross-Chart Aspects

For comparison charts (synastry, transits), shows aspects between the two charts.

```python
from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder

# Create a synastry comparison
chart1 = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
chart2 = ChartBuilder.from_notable("Ada Lovelace").with_aspects().calculate()
multichart = MultiChartBuilder.synastry(chart1, chart2).calculate()

# Show cross-chart aspects
ReportBuilder().from_chart(multichart).with_cross_aspects().render()

# Major aspects only
ReportBuilder().from_chart(multichart).with_cross_aspects(mode="major").render()
```
<!--pytest-codeblocks:expected-output-->
```

Cross-Chart Aspects
───────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Person 1            ┃ Aspect        ┃ Person 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☋ South Node        │ ⚹ Sextile     │ 🜊 Vertex            │ 0.01° │ —        │
│ ☊ North Node        │ △ Trine       │ 🜊 Vertex            │ 0.01° │ —        │
│ ☿ Mercury           │ □ Square      │ IC                  │ 0.04° │ —        │
│ ☿ Mercury           │ □ Square      │ MC                  │ 0.04° │ —        │
│ ♅ Uranus            │ ⚹ Sextile     │ ♀ Venus             │ 0.25° │ ←S       │
│ ☿ Mercury           │ ☍ Opposition  │ 🜊 Vertex            │ 0.40° │ —        │
│ ☋ South Node        │ □ Square      │ ♃ Jupiter           │ 0.49° │ A→       │
│ ☊ North Node        │ □ Square      │ ♃ Jupiter           │ 0.49° │ A→       │
│ ♀ Venus             │ △ Trine       │ ☉ Sun               │ 0.69° │ A→       │
│ ♆ Neptune           │ □ Square      │ ♄ Saturn            │ 0.71° │ ←S       │
│ ♅ Uranus            │ □ Square      │ ☿ Mercury           │ 0.76° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ ♃ Jupiter           │ 0.96° │ ←S       │
│ ♄ Saturn            │ □ Square      │ IC                  │ 1.09° │ —        │
│ ♄ Saturn            │ □ Square      │ MC                  │ 1.09° │ —        │
│ ☋ South Node        │ □ Square      │ ♀ Venus             │ 1.19° │ A→       │
│ ☊ North Node        │ □ Square      │ ♀ Venus             │ 1.19° │ A→       │
│ ☉ Sun               │ □ Square      │ ☋ South Node        │ 1.27° │ A→       │
│ ☉ Sun               │ □ Square      │ ☊ North Node        │ 1.27° │ A→       │
│ ♄ Saturn            │ ☍ Opposition  │ 🜊 Vertex            │ 1.45° │ —        │
│ ♄ Saturn            │ ☌ Conjunction │ ☽ Moon              │ 1.47° │ ←S       │
│ ♆ Neptune           │ ⚹ Sextile     │ ⚷ Chiron            │ 1.52° │ A→       │
│ ⚷ Chiron            │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 1.63° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ IC                  │ 1.82° │ —        │
│ ♅ Uranus            │ △ Trine       │ MC                  │ 1.82° │ —        │
│ ☋ South Node        │ △ Trine       │ ☿ Mercury           │ 2.20° │ A→       │
│ ☊ North Node        │ ⚹ Sextile     │ ☿ Mercury           │ 2.20° │ A→       │
│ ASC                 │ △ Trine       │ ⚷ Chiron            │ 2.26° │ —        │
│ DSC                 │ ⚹ Sextile     │ ⚷ Chiron            │ 2.26° │ —        │
│ ⚷ Chiron            │ ⚹ Sextile     │ IC                  │ 2.44° │ —        │
│ ⚷ Chiron            │ △ Trine       │ MC                  │ 2.44° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ☽ Moon              │ 2.52° │ ←S       │
│ ♀ Venus             │ △ Trine       │ ♆ Neptune           │ 2.59° │ A→       │
│ ☿ Mercury           │ △ Trine       │ ☿ Mercury           │ 2.61° │ ←S       │
│ ☉ Sun               │ ☌ Conjunction │ ♇ Pluto             │ 2.62° │ —        │
│ 🜊 Vertex            │ ☌ Conjunction │ ☿ Mercury           │ 2.63° │ —        │
│ ♅ Uranus            │ ☍ Opposition  │ ⚸ Black Moon Lilith │ 2.63° │ ←S       │
│ ♃ Jupiter           │ ⚹ Sextile     │ ☋ South Node        │ 2.70° │ ←S       │
│ ♃ Jupiter           │ △ Trine       │ ☊ North Node        │ 2.70° │ ←S       │
│ ☋ South Node        │ △ Trine       │ ☽ Moon              │ 2.93° │ ←S       │
│ ☊ North Node        │ ⚹ Sextile     │ ☽ Moon              │ 2.93° │ ←S       │
│ ⚷ Chiron            │ □ Square      │ ♄ Saturn            │ 3.03° │ ←S       │
│ ♃ Jupiter           │ □ Square      │ ☿ Mercury           │ 3.05° │ ←S       │
│ ☽ Moon              │ ☌ Conjunction │ ☉ Sun               │ 3.15° │ A→       │
│ ⚸ Black Moon Lilith │ ⚹ Sextile     │ ☊ North Node        │ 3.20° │ ←S       │
│ ⚸ Black Moon Lilith │ △ Trine       │ ☋ South Node        │ 3.20° │ ←S       │
│ ⚷ Chiron            │ ☍ Opposition  │ ♃ Jupiter           │ 3.30° │ A→       │
│ ♀ Venus             │ ☌ Conjunction │ ♂ Mars              │ 3.40° │ A→       │
│ IC                  │ ☍ Opposition  │ ⚷ Chiron            │ 3.45° │ —        │
│ MC                  │ ☌ Conjunction │ ⚷ Chiron            │ 3.45° │ —        │
│ ASC                 │ □ Square      │ ASC                 │ 3.55° │ —        │
│ ASC                 │ □ Square      │ DSC                 │ 3.55° │ —        │
│ DSC                 │ □ Square      │ ASC                 │ 3.55° │ —        │
│ DSC                 │ □ Square      │ DSC                 │ 3.55° │ —        │
│ ⚸ Black Moon Lilith │ ☍ Opposition  │ ♀ Venus             │ 3.56° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ♅ Uranus            │ 3.61° │ A→       │
│ ♂ Mars              │ ⚹ Sextile     │ ☿ Mercury           │ 3.62° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ☿ Mercury           │ 3.66° │ A→       │
│ ♇ Pluto             │ ⚹ Sextile     │ ♇ Pluto             │ 3.84° │ —        │
│ ⚷ Chiron            │ ⚹ Sextile     │ ⚷ Chiron            │ 3.84° │ A→       │
│ ♄ Saturn            │ ☌ Conjunction │ ASC                 │ 3.90° │ —        │
│ ♄ Saturn            │ ☍ Opposition  │ DSC                 │ 3.90° │ —        │
│ ☉ Sun               │ □ Square      │ ♆ Neptune           │ 3.94° │ ←S       │
│ ♆ Neptune           │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 3.96° │ A→       │
│ ⚷ Chiron            │ ☍ Opposition  │ ♀ Venus             │ 4.01° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ♀ Venus             │ 4.06° │ ←S       │
│ ⚸ Black Moon Lilith │ ☍ Opposition  │ ♃ Jupiter           │ 4.27° │ ←S       │
│ ♂ Mars              │ □ Square      │ ♀ Venus             │ 4.63° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ ♅ Uranus            │ 4.66° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ♃ Jupiter           │ 4.76° │ A→       │
│ ♆ Neptune           │ △ Trine       │ MC                  │ 4.77° │ —        │
│ IC                  │ □ Square      │ ☉ Sun               │ 4.83° │ —        │
│ MC                  │ □ Square      │ ☉ Sun               │ 4.83° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ASC                 │ 4.95° │ —        │
│ ☿ Mercury           │ ☍ Opposition  │ DSC                 │ 4.95° │ —        │
│ IC                  │ □ Square      │ ♅ Uranus            │ 5.04° │ —        │
│ MC                  │ □ Square      │ ♅ Uranus            │ 5.04° │ —        │
│ ☽ Moon              │ ☌ Conjunction │ ♆ Neptune           │ 5.05° │ A→       │
│ ☋ South Node        │ △ Trine       │ ♅ Uranus            │ 5.07° │ ←S       │
│ ⚸ Black Moon Lilith │ △ Trine       │ MC                  │ 5.13° │ —        │
│ ☽ Moon              │ □ Square      │ ⚷ Chiron            │ 5.14° │ ←S       │
│ ♂ Mars              │ □ Square      │ ♃ Jupiter           │ 5.33° │ A→       │
│ ☋ South Node        │ △ Trine       │ ASC                 │ 5.36° │ —        │
│ ☊ North Node        │ △ Trine       │ DSC                 │ 5.36° │ —        │
│ ♃ Jupiter           │ △ Trine       │ IC                  │ 5.62° │ —        │
│ ♆ Neptune           │ ☍ Opposition  │ ♃ Jupiter           │ 5.63° │ A→       │
│ ♇ Pluto             │ ☍ Opposition  │ ☿ Mercury           │ 5.81° │ ←S       │
│ ♂ Mars              │ △ Trine       │ 🜊 Vertex            │ 5.83° │ —        │
│ ☉ Sun               │ □ Square      │ ☉ Sun               │ 5.84° │ A→       │
│ ☋ South Node        │ ☍ Opposition  │ ♄ Saturn            │ 5.85° │ ←S       │
│ ☊ North Node        │ ☌ Conjunction │ ♄ Saturn            │ 5.85° │ ←S       │
│ ☽ Moon              │ △ Trine       │ ♂ Mars              │ 5.86° │ A→       │
│ ASC                 │ □ Square      │ ☽ Moon              │ 5.99° │ —        │
│ DSC                 │ □ Square      │ ☽ Moon              │ 5.99° │ —        │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘

Cross-Chart Aspects (Major)
───────────────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Person 1            ┃ Aspect        ┃ Person 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☋ South Node        │ ⚹ Sextile     │ 🜊 Vertex            │ 0.01° │ —        │
│ ☊ North Node        │ △ Trine       │ 🜊 Vertex            │ 0.01° │ —        │
│ ☿ Mercury           │ □ Square      │ IC                  │ 0.04° │ —        │
│ ☿ Mercury           │ □ Square      │ MC                  │ 0.04° │ —        │
│ ♅ Uranus            │ ⚹ Sextile     │ ♀ Venus             │ 0.25° │ ←S       │
│ ☿ Mercury           │ ☍ Opposition  │ 🜊 Vertex            │ 0.40° │ —        │
│ ☋ South Node        │ □ Square      │ ♃ Jupiter           │ 0.49° │ A→       │
│ ☊ North Node        │ □ Square      │ ♃ Jupiter           │ 0.49° │ A→       │
│ ♀ Venus             │ △ Trine       │ ☉ Sun               │ 0.69° │ A→       │
│ ♆ Neptune           │ □ Square      │ ♄ Saturn            │ 0.71° │ ←S       │
│ ♅ Uranus            │ □ Square      │ ☿ Mercury           │ 0.76° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ ♃ Jupiter           │ 0.96° │ ←S       │
│ ♄ Saturn            │ □ Square      │ IC                  │ 1.09° │ —        │
│ ♄ Saturn            │ □ Square      │ MC                  │ 1.09° │ —        │
│ ☋ South Node        │ □ Square      │ ♀ Venus             │ 1.19° │ A→       │
│ ☊ North Node        │ □ Square      │ ♀ Venus             │ 1.19° │ A→       │
│ ☉ Sun               │ □ Square      │ ☋ South Node        │ 1.27° │ A→       │
│ ☉ Sun               │ □ Square      │ ☊ North Node        │ 1.27° │ A→       │
│ ♄ Saturn            │ ☍ Opposition  │ 🜊 Vertex            │ 1.45° │ —        │
│ ♄ Saturn            │ ☌ Conjunction │ ☽ Moon              │ 1.47° │ ←S       │
│ ♆ Neptune           │ ⚹ Sextile     │ ⚷ Chiron            │ 1.52° │ A→       │
│ ⚷ Chiron            │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 1.63° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ IC                  │ 1.82° │ —        │
│ ♅ Uranus            │ △ Trine       │ MC                  │ 1.82° │ —        │
│ ☋ South Node        │ △ Trine       │ ☿ Mercury           │ 2.20° │ A→       │
│ ☊ North Node        │ ⚹ Sextile     │ ☿ Mercury           │ 2.20° │ A→       │
│ ASC                 │ △ Trine       │ ⚷ Chiron            │ 2.26° │ —        │
│ DSC                 │ ⚹ Sextile     │ ⚷ Chiron            │ 2.26° │ —        │
│ ⚷ Chiron            │ ⚹ Sextile     │ IC                  │ 2.44° │ —        │
│ ⚷ Chiron            │ △ Trine       │ MC                  │ 2.44° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ☽ Moon              │ 2.52° │ ←S       │
│ ♀ Venus             │ △ Trine       │ ♆ Neptune           │ 2.59° │ A→       │
│ ☿ Mercury           │ △ Trine       │ ☿ Mercury           │ 2.61° │ ←S       │
│ ☉ Sun               │ ☌ Conjunction │ ♇ Pluto             │ 2.62° │ —        │
│ 🜊 Vertex            │ ☌ Conjunction │ ☿ Mercury           │ 2.63° │ —        │
│ ♅ Uranus            │ ☍ Opposition  │ ⚸ Black Moon Lilith │ 2.63° │ ←S       │
│ ♃ Jupiter           │ ⚹ Sextile     │ ☋ South Node        │ 2.70° │ ←S       │
│ ♃ Jupiter           │ △ Trine       │ ☊ North Node        │ 2.70° │ ←S       │
│ ☋ South Node        │ △ Trine       │ ☽ Moon              │ 2.93° │ ←S       │
│ ☊ North Node        │ ⚹ Sextile     │ ☽ Moon              │ 2.93° │ ←S       │
│ ⚷ Chiron            │ □ Square      │ ♄ Saturn            │ 3.03° │ ←S       │
│ ♃ Jupiter           │ □ Square      │ ☿ Mercury           │ 3.05° │ ←S       │
│ ☽ Moon              │ ☌ Conjunction │ ☉ Sun               │ 3.15° │ A→       │
│ ⚸ Black Moon Lilith │ ⚹ Sextile     │ ☊ North Node        │ 3.20° │ ←S       │
│ ⚸ Black Moon Lilith │ △ Trine       │ ☋ South Node        │ 3.20° │ ←S       │
│ ⚷ Chiron            │ ☍ Opposition  │ ♃ Jupiter           │ 3.30° │ A→       │
│ ♀ Venus             │ ☌ Conjunction │ ♂ Mars              │ 3.40° │ A→       │
│ IC                  │ ☍ Opposition  │ ⚷ Chiron            │ 3.45° │ —        │
│ MC                  │ ☌ Conjunction │ ⚷ Chiron            │ 3.45° │ —        │
│ ASC                 │ □ Square      │ ASC                 │ 3.55° │ —        │
│ ASC                 │ □ Square      │ DSC                 │ 3.55° │ —        │
│ DSC                 │ □ Square      │ ASC                 │ 3.55° │ —        │
│ DSC                 │ □ Square      │ DSC                 │ 3.55° │ —        │
│ ⚸ Black Moon Lilith │ ☍ Opposition  │ ♀ Venus             │ 3.56° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ♅ Uranus            │ 3.61° │ A→       │
│ ♂ Mars              │ ⚹ Sextile     │ ☿ Mercury           │ 3.62° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ☿ Mercury           │ 3.66° │ A→       │
│ ♇ Pluto             │ ⚹ Sextile     │ ♇ Pluto             │ 3.84° │ —        │
│ ⚷ Chiron            │ ⚹ Sextile     │ ⚷ Chiron            │ 3.84° │ A→       │
│ ♄ Saturn            │ ☌ Conjunction │ ASC                 │ 3.90° │ —        │
│ ♄ Saturn            │ ☍ Opposition  │ DSC                 │ 3.90° │ —        │
│ ☉ Sun               │ □ Square      │ ♆ Neptune           │ 3.94° │ ←S       │
│ ♆ Neptune           │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 3.96° │ A→       │
│ ⚷ Chiron            │ ☍ Opposition  │ ♀ Venus             │ 4.01° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ♀ Venus             │ 4.06° │ ←S       │
│ ⚸ Black Moon Lilith │ ☍ Opposition  │ ♃ Jupiter           │ 4.27° │ ←S       │
│ ♂ Mars              │ □ Square      │ ♀ Venus             │ 4.63° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ ♅ Uranus            │ 4.66° │ A→       │
│ ♃ Jupiter           │ △ Trine       │ ♃ Jupiter           │ 4.76° │ A→       │
│ ♆ Neptune           │ △ Trine       │ MC                  │ 4.77° │ —        │
│ IC                  │ □ Square      │ ☉ Sun               │ 4.83° │ —        │
│ MC                  │ □ Square      │ ☉ Sun               │ 4.83° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ASC                 │ 4.95° │ —        │
│ ☿ Mercury           │ ☍ Opposition  │ DSC                 │ 4.95° │ —        │
│ IC                  │ □ Square      │ ♅ Uranus            │ 5.04° │ —        │
│ MC                  │ □ Square      │ ♅ Uranus            │ 5.04° │ —        │
│ ☽ Moon              │ ☌ Conjunction │ ♆ Neptune           │ 5.05° │ A→       │
│ ☋ South Node        │ △ Trine       │ ♅ Uranus            │ 5.07° │ ←S       │
│ ⚸ Black Moon Lilith │ △ Trine       │ MC                  │ 5.13° │ —        │
│ ☽ Moon              │ □ Square      │ ⚷ Chiron            │ 5.14° │ ←S       │
│ ♂ Mars              │ □ Square      │ ♃ Jupiter           │ 5.33° │ A→       │
│ ☋ South Node        │ △ Trine       │ ASC                 │ 5.36° │ —        │
│ ☊ North Node        │ △ Trine       │ DSC                 │ 5.36° │ —        │
│ ♃ Jupiter           │ △ Trine       │ IC                  │ 5.62° │ —        │
│ ♆ Neptune           │ ☍ Opposition  │ ♃ Jupiter           │ 5.63° │ A→       │
│ ♇ Pluto             │ ☍ Opposition  │ ☿ Mercury           │ 5.81° │ ←S       │
│ ♂ Mars              │ △ Trine       │ 🜊 Vertex            │ 5.83° │ —        │
│ ☉ Sun               │ □ Square      │ ☉ Sun               │ 5.84° │ A→       │
│ ☋ South Node        │ ☍ Opposition  │ ♄ Saturn            │ 5.85° │ ←S       │
│ ☊ North Node        │ ☌ Conjunction │ ♄ Saturn            │ 5.85° │ ←S       │
│ ☽ Moon              │ △ Trine       │ ♂ Mars              │ 5.86° │ A→       │
│ ASC                 │ □ Square      │ ☽ Moon              │ 5.99° │ —        │
│ DSC                 │ □ Square      │ ☽ Moon              │ 5.99° │ —        │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘
```

**Parameters:** Same as `with_aspects()`

**Output columns:**
- Chart 1 Planet (uses chart1_label)
- Aspect
- Chart 2 Planet (uses chart2_label)
- Orb
- Applying

---

### House Cusps

Table of house cusp positions for each house system.

```python
# All calculated house systems
ReportBuilder().from_chart(chart).with_house_cusps().render()

# Specific systems only
ReportBuilder().from_chart(chart).with_house_cusps(systems=["Placidus"]).render()

# Multiple specific systems
ReportBuilder().from_chart(chart).with_house_cusps(
    systems=["Placidus", "Whole Sign", "Koch"]
).render()
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `systems` | `str \| list[str]` | `"all"` | Which house systems to show |

**Output:** 12 rows (houses 1-12), one column per house system showing degree + sign.

---

### Declinations

Table showing planetary declinations (distance from the celestial equator).

```python
ReportBuilder().from_chart(chart).with_declinations().render()
```

**Output columns:**
- Planet (with glyph)
- Declination (degrees)
- Direction (North/South)
- Out of Bounds (Yes/No - planets beyond ~23°27')

Out-of-bounds planets are considered to have intensified or unconventional expression.

---

### Moon Phase

Information about the lunar phase at the chart time.

```python
ReportBuilder().from_chart(chart).with_moon_phase().render()
```

**Output:**
- Phase name (New Moon, Waxing Crescent, First Quarter, etc.)
- Phase angle
- Illumination percentage
- Days since/until new moon

---

### Essential Dignities

Table of planetary dignities (requires `DignityComponent`).

```python
from stellium.components import DignityComponent

# Calculate chart with dignities
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

# Show dignities
ReportBuilder().from_chart(chart).with_dignities().render()

# Traditional dignities only
ReportBuilder().from_chart(chart).with_dignities(essential="traditional").render()

# Modern dignities only
ReportBuilder().from_chart(chart).with_dignities(essential="modern").render()

# Show dignity names instead of just scores
ReportBuilder().from_chart(chart).with_dignities(show_details=True).render()
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `essential` | `str` | `"both"` | Which system: `"traditional"`, `"modern"`, `"both"`, `"none"` |
| `show_details` | `bool` | `False` | Show dignity names (Domicile, Exaltation, etc.) |

---

### Aspect Patterns

Table of detected aspect patterns (requires `AspectPatternAnalyzer`).

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.engines.patterns import AspectPatternAnalyzer

# Calculate chart with pattern analysis
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_analyzer(AspectPatternAnalyzer())
    .calculate()
)

# Show all patterns
ReportBuilder().from_chart(chart).with_aspect_patterns().render()

# Specific pattern types
ReportBuilder().from_chart(chart).with_aspect_patterns(
    pattern_types=["Grand Trine", "T-Square"]
).render()

# Sort by element
ReportBuilder().from_chart(chart).with_aspect_patterns(sort_by="element").render()
```
<!--pytest-codeblocks:expected-output-->
```

Aspect Patterns
───────────────
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern     ┃ Planets                             ┃ Element/Quality ┃ Details                    ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Grand Cross │ ♃ Jupiter, ♅ Uranus, ♇ Pluto, 🜊     │ Mixed           │ 4 planets                  │
│             │ Vertex                              │                 │                            │
│ Stellium    │ ☿ Mercury, ♀ Venus, ♄ Saturn        │ Fire / Cardinal │ 3 planets                  │
│ T-Square    │ ♃ Jupiter, ♅ Uranus, ♇ Pluto        │ Mixed           │ 3 planets, Apex: ♇ Pluto   │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♃ Jupiter        │ Fixed           │ 3 planets, Apex: ♃ Jupiter │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♅ Uranus         │ Mixed           │ 3 planets, Apex: ♅ Uranus  │
└─────────────┴─────────────────────────────────────┴─────────────────┴────────────────────────────┘

Aspect Patterns
───────────────
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern  ┃ Planets                      ┃ Element/Quality ┃ Details                    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ T-Square │ ♃ Jupiter, ♅ Uranus, ♇ Pluto │ Mixed           │ 3 planets, Apex: ♇ Pluto   │
│ T-Square │ ♇ Pluto, 🜊 Vertex, ♃ Jupiter │ Fixed           │ 3 planets, Apex: ♃ Jupiter │
│ T-Square │ ♇ Pluto, 🜊 Vertex, ♅ Uranus  │ Mixed           │ 3 planets, Apex: ♅ Uranus  │
└──────────┴──────────────────────────────┴─────────────────┴────────────────────────────┘

Aspect Patterns
───────────────
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern     ┃ Planets                             ┃ Element/Quality ┃ Details                    ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Stellium    │ ☿ Mercury, ♀ Venus, ♄ Saturn        │ Fire / Cardinal │ 3 planets                  │
│ Grand Cross │ ♃ Jupiter, ♅ Uranus, ♇ Pluto, 🜊     │ Mixed           │ 4 planets                  │
│             │ Vertex                              │                 │                            │
│ T-Square    │ ♃ Jupiter, ♅ Uranus, ♇ Pluto        │ Mixed           │ 3 planets, Apex: ♇ Pluto   │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♃ Jupiter        │ Fixed           │ 3 planets, Apex: ♃ Jupiter │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♅ Uranus         │ Mixed           │ 3 planets, Apex: ♅ Uranus  │
└─────────────┴─────────────────────────────────────┴─────────────────┴────────────────────────────┘
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pattern_types` | `str \| list[str]` | `"all"` | Which patterns to show |
| `sort_by` | `str` | `"type"` | Sort: `"type"`, `"element"`, `"count"` |

**Detected patterns:** Grand Trine, Grand Cross, T-Square, Yod, Kite, Mystic Rectangle, Stellium

---

### Midpoints

Table of planetary midpoints (requires `MidpointCalculator`).

```python
from stellium.components import MidpointCalculator

# Calculate chart with midpoints
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(MidpointCalculator())
    .calculate()
)

# All midpoints
ReportBuilder().from_chart(chart).with_midpoints().render()

# Core midpoints only (Sun/Moon/ASC/MC)
ReportBuilder().from_chart(chart).with_midpoints(mode="core").render()

# Limit to top N midpoints
ReportBuilder().from_chart(chart).with_midpoints(threshold=20).render()
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | `str` | `"all"` | Filter: `"all"` or `"core"` (Sun/Moon/ASC/MC) |
| `threshold` | `int \| None` | `None` | Limit to top N midpoints |

---

### Transit Timeline (Natal Transits)

Show when transiting planets form aspects to natal positions, with orb entry/exit
dates and multi-pass handling for retrograde transits. Two output modes:

- **`TransitListSection`** — plain-text rows, one per transit event
- **`TransitGanttSection`** — SVG horizontal bar chart (Gantt style), grouped by planet

Both sections are used via `.with_section()` since they require an explicit date range.

#### Plain-Text List

```python
import datetime as dt
from stellium import ChartBuilder, ReportBuilder
from stellium.presentation.sections import TransitListSection

natal_chart = ChartBuilder.from_notable("Albert Einstein").calculate()

section = TransitListSection(
    start=dt.datetime(2025, 12, 1),
    end=dt.datetime(2026, 6, 1),
)

ReportBuilder().from_chart(natal_chart).with_section(section).render()
```
<!--pytest-codeblocks:expected-output-->
```

Natal Transits
──────────────
23 Sep – 8 Jun '26 — Jupiter △ natal Sun (2x: 13 Dec, 29 May '26)
17 Nov – 5 Mar '26 — Pluto ⚹ natal Mercury
20 Nov – 16 Apr '26 — Uranus □ natal Jupiter (2x: 27 Jan '26, 11 Feb '26)
30 Nov – 3 Dec — Venus □ natal Uranus
30 Nov – 14 May '26 — Moon △ natal Moon (7x: 1 Dec, 28 Dec, 24 Jan '26, 20 Feb '26, 20 Mar '26, 16 
Apr '26, 14 May '26)
1 Dec – 14 May '26 — Moon ☌ natal Venus (7x: 1 Dec, 28 Dec, 24 Jan '26, 21 Feb '26, 20 Mar '26, 16 
Apr '26, 14 May '26)
1 Dec – 4 Dec — Venus △ natal Mercury
1 Dec – 15 May '26 — Moon □ natal Mars (7x: 1 Dec, 29 Dec, 25 Jan '26, 21 Feb '26, 21 Mar '26, 17 
Apr '26, 14 May '26)
1 Dec – 15 May '26 — Moon ⚹ natal Jupiter (7x: 1 Dec, 29 Dec, 25 Jan '26, 21 Feb '26, 21 Mar '26, 17
Apr '26, 14 May '26)
2 Dec – 15 May '26 — Moon △ natal Uranus (7x: 2 Dec, 29 Dec, 25 Jan '26, 22 Feb '26, 21 Mar '26, 17 
Apr '26, 15 May '26)
2 Dec – 15 May '26 — Moon ☌ natal Neptune (7x: 2 Dec, 30 Dec, 26 Jan '26, 22 Feb '26, 21 Mar '26, 18
Apr '26, 15 May '26)
2 Dec – 5 Dec — Venus △ natal Saturn
2 Dec – 7 Dec — Mercury △ natal Sun
3 Dec – 16 May '26 — Moon ⚹ natal Sun (7x: 3 Dec, 31 Dec, 27 Jan '26, 23 Feb '26, 22 Mar '26, 19 Apr
'26, 16 May '26)
3 Dec – 16 May '26 — Moon ☌ natal Pluto (7x: 3 Dec, 31 Dec, 27 Jan '26, 23 Feb '26, 22 Mar '26, 19 
Apr '26, 16 May '26)
3 Dec – 17 May '26 — Moon △ natal Mars (7x: 3 Dec, 31 Dec, 27 Jan '26, 23 Feb '26, 23 Mar '26, 19 
Apr '26, 16 May '26)
3 Dec – 17 May '26 — Moon □ natal Jupiter (7x: 3 Dec, 31 Dec, 27 Jan '26, 23 Feb '26, 23 Mar '26, 19
Apr '26, 16 May '26)
3 Dec – 9 Dec — Mars □ natal Sun
4 Dec – 17 May '26 — Moon □ natal Uranus (7x: 4 Dec, 31 Dec, 27 Jan '26, 24 Feb '26, 23 Mar '26, 19 
Apr '26, 17 May '26)
4 Dec – 17 May '26 — Moon ⚹ natal Mercury (7x: 4 Dec, 31 Dec, 28 Jan '26, 24 Feb '26, 23 Mar '26, 19
Apr '26, 17 May '26)
4 Dec – 17 May '26 — Moon ⚹ natal Saturn (7x: 4 Dec, 31 Dec, 28 Jan '26, 24 Feb '26, 23 Mar '26, 19 
Apr '26, 17 May '26)
4 Dec – 8 Dec — Sun ☌ natal Moon
4 Dec – 9 Dec — Mercury ☍ natal Pluto
4 Dec – 18 May '26 — Moon ☍ natal Moon (7x: 5 Dec, 1 Jan '26, 28 Jan '26, 25 Feb '26, 24 Mar '26, 20
Apr '26, 18 May '26)
5 Dec – 18 May '26 — Moon ⚹ natal Venus (7x: 5 Dec, 1 Jan '26, 29 Jan '26, 25 Feb '26, 24 Mar '26, 
20 Apr '26, 18 May '26)
5 Dec – 18 May '26 — Moon □ natal Sun (7x: 5 Dec, 2 Jan '26, 29 Jan '26, 25 Feb '26, 24 Mar '26, 21 
Apr '26, 18 May '26)
5 Dec – 19 May '26 — Moon △ natal Jupiter (7x: 5 Dec, 2 Jan '26, 29 Jan '26, 26 Feb '26, 25 Mar '26,
21 Apr '26, 18 May '26)
6 Dec – 19 May '26 — Moon ⚹ natal Uranus (7x: 6 Dec, 2 Jan '26, 30 Jan '26, 26 Feb '26, 25 Mar '26, 
21 Apr '26, 19 May '26)
6 Dec – 19 May '26 — Moon □ natal Mercury (7x: 6 Dec, 2 Jan '26, 30 Jan '26, 26 Feb '26, 25 Mar '26,
21 Apr '26, 19 May '26)
6 Dec – 19 May '26 — Moon □ natal Saturn (7x: 6 Dec, 2 Jan '26, 30 Jan '26, 26 Feb '26, 25 Mar '26, 
21 Apr '26, 19 May '26)
6 Dec – 19 May '26 — Moon ⚹ natal Neptune (7x: 6 Dec, 3 Jan '26, 30 Jan '26, 26 Feb '26, 25 Mar '26,
22 Apr '26, 19 May '26)
6 Dec – 10 Dec — Sun △ natal Venus
7 Dec – 20 May '26 — Moon □ natal Venus (7x: 7 Dec, 3 Jan '26, 31 Jan '26, 27 Feb '26, 26 Mar '26, 
22 Apr '26, 20 May '26)
7 Dec – 20 May '26 — Moon △ natal Sun (7x: 7 Dec, 4 Jan '26, 31 Jan '26, 27 Feb '26, 27 Mar '26, 23 
Apr '26, 20 May '26)
7 Dec – 20 May '26 — Moon ⚹ natal Pluto (7x: 7 Dec, 4 Jan '26, 31 Jan '26, 27 Feb '26, 27 Mar '26, 
23 Apr '26, 20 May '26)
7 Dec – 21 May '26 — Moon ☍ natal Mars (7x: 7 Dec, 4 Jan '26, 31 Jan '26, 28 Feb '26, 27 Mar '26, 23
Apr '26, 20 May '26)
7 Dec – 10 Dec — Mercury ⚹ natal Mars
7 Dec – 11 Dec — Mercury □ natal Jupiter
8 Dec – 21 May '26 — Moon △ natal Mercury (7x: 8 Dec, 4 Jan '26, 1 Feb '26, 28 Feb '26, 27 Mar '26, 
24 Apr '26, 21 May '26)
8 Dec – 21 May '26 — Moon △ natal Saturn (7x: 8 Dec, 4 Jan '26, 1 Feb '26, 28 Feb '26, 27 Mar '26, 
24 Apr '26, 21 May '26)
8 Dec – 21 May '26 — Moon □ natal Neptune (7x: 8 Dec, 5 Jan '26, 1 Feb '26, 28 Feb '26, 28 Mar '26, 
24 Apr '26, 21 May '26)
9 Dec – 22 May '26 — Moon △ natal Moon (7x: 9 Dec, 5 Jan '26, 2 Feb '26, 1 Mar '26, 28 Mar '26, 24 
Apr '26, 22 May '26)
9 Dec – 22 May '26 — Moon △ natal Venus (7x: 9 Dec, 5 Jan '26, 2 Feb '26, 1 Mar '26, 28 Mar '26, 25 
Apr '26, 22 May '26)
9 Dec – 23 May '26 — Moon □ natal Pluto (7x: 9 Dec, 6 Jan '26, 2 Feb '26, 2 Mar '26, 29 Mar '26, 25 
Apr '26, 22 May '26)
9 Dec – 23 May '26 — Moon ☍ natal Jupiter (7x: 10 Dec, 6 Jan '26, 2 Feb '26, 2 Mar '26, 29 Mar '26, 
25 Apr '26, 23 May '26)
9 Dec – 13 Dec — Mars ⚹ natal Jupiter
10 Dec – 23 May '26 — Moon ☌ natal Uranus (7x: 10 Dec, 6 Jan '26, 3 Feb '26, 2 Mar '26, 29 Mar '26, 
26 Apr '26, 23 May '26)
10 Dec – 24 May '26 — Moon △ natal Neptune (7x: 10 Dec, 7 Jan '26, 3 Feb '26, 3 Mar '26, 30 Mar '26,
26 Apr '26, 23 May '26)
10 Dec – 13 Dec — Venus ☌ natal Moon
11 Dec – 24 May '26 — Moon □ natal Moon (7x: 11 Dec, 7 Jan '26, 4 Feb '26, 3 Mar '26, 30 Mar '26, 27
Apr '26, 24 May '26)
11 Dec – 14 Dec — Mercury □ natal Uranus
11 Dec – 25 May '26 — Moon ☍ natal Sun (7x: 12 Dec, 8 Jan '26, 4 Feb '26, 4 Mar '26, 31 Mar '26, 27 
Apr '26, 25 May '26)
12 Dec – 25 May '26 — Moon △ natal Pluto (7x: 12 Dec, 8 Jan '26, 4 Feb '26, 4 Mar '26, 31 Mar '26, 
27 Apr '26, 25 May '26)
12 Dec – 25 May '26 — Moon △ natal Mars (7x: 12 Dec, 8 Jan '26, 5 Feb '26, 4 Mar '26, 31 Mar '26, 28
Apr '26, 25 May '26)
12 Dec – 15 Dec — Venus △ natal Venus
12 Dec – 26 May '26 — Moon ☍ natal Mercury (7x: 12 Dec, 9 Jan '26, 5 Feb '26, 5 Mar '26, 1 Apr '26, 
28 Apr '26, 25 May '26)
12 Dec – 26 May '26 — Moon ☍ natal Saturn (7x: 13 Dec, 9 Jan '26, 5 Feb '26, 5 Mar '26, 1 Apr '26, 
28 Apr '26, 25 May '26)
12 Dec – 15 Dec — Mercury △ natal Mercury
13 Dec – 17 Dec — Sun □ natal Sun
13 Dec – 16 Dec — Mercury △ natal Saturn
13 Dec – 26 May '26 — Moon ⚹ natal Moon (7x: 13 Dec, 10 Jan '26, 6 Feb '26, 5 Mar '26, 2 Apr '26, 29
Apr '26, 26 May '26)
13 Dec – 27 May '26 — Moon ☍ natal Venus (7x: 14 Dec, 10 Jan '26, 6 Feb '26, 6 Mar '26, 2 Apr '26, 
29 Apr '26, 26 May '26)
14 Dec – 19 Dec — Mars △ natal Uranus
14 Dec – 27 May '26 — Moon □ natal Mars (7x: 14 Dec, 11 Jan '26, 7 Feb '26, 6 Mar '26, 3 Apr '26, 30
Apr '26, 27 May '26)
14 Dec – 27 May '26 — Moon △ natal Jupiter (7x: 14 Dec, 11 Jan '26, 7 Feb '26, 6 Mar '26, 3 Apr '26,
30 Apr '26, 27 May '26)
15 Dec – 29 Jan '26 — Saturn ⚹ natal Mars
15 Dec – 28 May '26 — Moon ⚹ natal Uranus (7x: 15 Dec, 11 Jan '26, 7 Feb '26, 7 Mar '26, 3 Apr '26, 
30 Apr '26, 28 May '26)
15 Dec – 28 May '26 — Moon ☍ natal Neptune (7x: 15 Dec, 12 Jan '26, 8 Feb '26, 7 Mar '26, 4 Apr '26,
1 May '26, 28 May '26)
16 Dec – 22 Dec — Mars □ natal Mercury
16 Dec – 30 May '26 — Moon △ natal Sun (7x: 17 Dec, 13 Jan '26, 9 Feb '26, 9 Mar '26, 5 Apr '26, 2 
May '26, 29 May '26)
17 Dec – 30 May '26 — Moon ☍ natal Pluto (7x: 17 Dec, 13 Jan '26, 9 Feb '26, 9 Mar '26, 5 Apr '26, 2
May '26, 30 May '26)
17 Dec – 30 May '26 — Moon ⚹ natal Mars (7x: 17 Dec, 13 Jan '26, 10 Feb '26, 9 Mar '26, 5 Apr '26, 3
May '26, 30 May '26)
17 Dec – 30 May '26 — Moon □ natal Jupiter (7x: 17 Dec, 13 Jan '26, 10 Feb '26, 9 Mar '26, 5 Apr 
'26, 3 May '26, 30 May '26)
17 Dec – 30 May '26 — Moon □ natal Uranus (7x: 17 Dec, 14 Jan '26, 10 Feb '26, 9 Mar '26, 6 Apr '26,
3 May '26, 30 May '26)
17 Dec – 20 Dec — Sun ⚹ natal Jupiter
17 Dec – 30 May '26 — Moon △ natal Mercury (7x: 17 Dec, 14 Jan '26, 10 Feb '26, 9 Mar '26, 6 Apr 
'26, 3 May '26, 30 May '26)
17 Dec – 31 May '26 — Moon △ natal Saturn (7x: 18 Dec, 14 Jan '26, 10 Feb '26, 10 Mar '26, 6 Apr 
'26, 3 May '26, 30 May '26)
17 Dec – 21 Dec — Venus □ natal Sun
18 Dec – 23 Dec — Mars □ natal Saturn
18 Dec – 31 May '26 — Moon ☌ natal Moon (7x: 18 Dec, 15 Jan '26, 11 Feb '26, 10 Mar '26, 7 Apr '26, 
4 May '26, 31 May '26)
18 Dec – 1 Jun '26 — Moon △ natal Venus (7x: 19 Dec, 15 Jan '26, 11 Feb '26, 11 Mar '26, 7 Apr '26, 
4 May '26, 31 May '26)
19 Dec – 5 May '26 — Moon □ natal Sun (6x: 19 Dec, 15 Jan '26, 12 Feb '26, 11 Mar '26, 7 Apr '26, 5 
May '26)
19 Dec – 5 May '26 — Moon ⚹ natal Jupiter (6x: 19 Dec, 16 Jan '26, 12 Feb '26, 11 Mar '26, 8 Apr 
'26, 5 May '26)
20 Dec – 6 May '26 — Moon △ natal Uranus (6x: 20 Dec, 16 Jan '26, 12 Feb '26, 12 Mar '26, 8 Apr '26,
5 May '26)
20 Dec – 6 May '26 — Moon □ natal Mercury (6x: 20 Dec, 16 Jan '26, 13 Feb '26, 12 Mar '26, 8 Apr 
'26, 6 May '26)
20 Dec – 6 May '26 — Moon □ natal Saturn (6x: 20 Dec, 16 Jan '26, 13 Feb '26, 12 Mar '26, 8 Apr '26,
6 May '26)
20 Dec – 6 May '26 — Moon △ natal Neptune (6x: 20 Dec, 17 Jan '26, 13 Feb '26, 12 Mar '26, 9 Apr 
'26, 6 May '26)
20 Dec – 24 Dec — Sun △ natal Uranus
21 Dec – 23 Dec — Mercury ☌ natal Moon
21 Dec – 7 May '26 — Moon □ natal Venus (6x: 21 Dec, 17 Jan '26, 14 Feb '26, 13 Mar '26, 9 Apr '26, 
7 May '26)
21 Dec – 23 Dec — Venus ⚹ natal Jupiter
22 Dec – 7 May '26 — Moon ⚹ natal Sun (6x: 22 Dec, 18 Jan '26, 14 Feb '26, 14 Mar '26, 10 Apr '26, 7
May '26)
22 Dec – 8 May '26 — Moon △ natal Pluto (6x: 22 Dec, 18 Jan '26, 14 Feb '26, 14 Mar '26, 10 Apr '26,
7 May '26)
22 Dec – 8 May '26 — Moon ☌ natal Mars (6x: 22 Dec, 18 Jan '26, 15 Feb '26, 14 Mar '26, 10 Apr '26, 
8 May '26)
22 Dec – 26 Dec — Sun □ natal Mercury
22 Dec – 8 May '26 — Moon ⚹ natal Mercury (6x: 22 Dec, 19 Jan '26, 15 Feb '26, 14 Mar '26, 11 Apr 
'26, 8 May '26)
22 Dec – 25 Dec — Mercury △ natal Venus
22 Dec – 8 May '26 — Moon ⚹ natal Saturn (6x: 22 Dec, 19 Jan '26, 15 Feb '26, 14 Mar '26, 11 Apr 
'26, 8 May '26)
23 Dec – 28 Dec — Mars △ natal Neptune
23 Dec – 9 May '26 — Moon □ natal Neptune (6x: 23 Dec, 19 Jan '26, 15 Feb '26, 15 Mar '26, 11 Apr 
'26, 8 May '26)
23 Dec – 9 May '26 — Moon ⚹ natal Moon (6x: 23 Dec, 20 Jan '26, 16 Feb '26, 15 Mar '26, 12 Apr '26, 
9 May '26)
23 Dec – 27 Dec — Sun □ natal Saturn
23 Dec – 9 May '26 — Moon ⚹ natal Venus (6x: 24 Dec, 20 Jan '26, 16 Feb '26, 15 Mar '26, 12 Apr '26,
9 May '26)
24 Dec – 27 Dec — Venus △ natal Uranus
24 Dec – 10 May '26 — Moon □ natal Pluto (6x: 24 Dec, 20 Jan '26, 17 Feb '26, 16 Mar '26, 12 Apr 
'26, 10 May '26)
24 Dec – 10 May '26 — Moon ☌ natal Jupiter (6x: 24 Dec, 21 Jan '26, 17 Feb '26, 16 Mar '26, 13 Apr 
'26, 10 May '26)
24 Dec – 10 May '26 — Moon ☍ natal Uranus (6x: 25 Dec, 21 Jan '26, 17 Feb '26, 17 Mar '26, 13 Apr 
'26, 10 May '26)
25 Dec – 11 May '26 — Moon ⚹ natal Neptune (6x: 25 Dec, 21 Jan '26, 18 Feb '26, 17 Mar '26, 13 Apr 
'26, 11 May '26)
25 Dec – 28 Dec — Venus □ natal Mercury
26 Dec – 12 May '26 — Moon □ natal Moon (6x: 26 Dec, 22 Jan '26, 18 Feb '26, 18 Mar '26, 14 Apr '26,
11 May '26)
26 Dec – 29 Dec — Venus □ natal Saturn
26 Dec – 12 May '26 — Moon ☌ natal Sun (6x: 26 Dec, 23 Jan '26, 19 Feb '26, 18 Mar '26, 15 Apr '26, 
12 May '26)
26 Dec – 12 May '26 — Moon ⚹ natal Pluto (6x: 26 Dec, 23 Jan '26, 19 Feb '26, 18 Mar '26, 15 Apr 
'26, 12 May '26)
26 Dec – 12 May '26 — Moon ⚹ natal Mars (6x: 27 Dec, 23 Jan '26, 19 Feb '26, 18 Mar '26, 15 Apr '26,
12 May '26)
27 Dec – 29 Dec — Mercury □ natal Sun
27 Dec – 31 Dec — Sun △ natal Neptune
27 Dec – 13 May '26 — Moon ☌ natal Mercury (6x: 27 Dec, 23 Jan '26, 20 Feb '26, 19 Mar '26, 15 Apr 
'26, 13 May '26)
27 Dec – 13 May '26 — Moon ☌ natal Saturn (6x: 27 Dec, 23 Jan '26, 20 Feb '26, 19 Mar '26, 15 Apr 
'26, 13 May '26)
29 Dec – 1 Jan '26 — Venus △ natal Neptune
30 Dec – 1 Jan '26 — Mercury ⚹ natal Jupiter
16 Feb '26 — Pluto ⚹ natal Saturn
1 Jan '26 – 4 Jan '26 — Mercury △ natal Uranus
2 Jan '26 – 5 Jan '26 — Mercury □ natal Mercury
3 Jan '26 – 5 Jan '26 — Mercury □ natal Saturn
3 Jan '26 – 9 Jan '26 — Mars □ natal Venus
5 Jan '26 – 9 Jan '26 — Sun □ natal Venus
5 Jan '26 – 8 Jan '26 — Venus □ natal Venus
5 Jan '26 – 8 Jan '26 — Mercury △ natal Neptune
11 Jan '26 – 13 Jan '26 — Venus ⚹ natal Sun
11 Jan '26 – 13 Jan '26 — Mercury □ natal Venus
11 Jan '26 – 14 Jan '26 — Venus △ natal Pluto
12 Jan '26 – 15 Jan '26 — Sun ⚹ natal Sun
12 Jan '26 – 16 Jan '26 — Sun △ natal Pluto
13 Jan '26 – 16 Jan '26 — Mars ⚹ natal Sun
13 Jan '26 – 16 Jan '26 — Venus ☌ natal Mars
14 Jan '26 – 19 Jan '26 — Mars △ natal Pluto
15 Jan '26 – 19 Jan '26 — Sun ☌ natal Mars
15 Jan '26 – 17 Jan '26 — Mercury ⚹ natal Sun
16 Jan '26 – 18 Jan '26 — Mercury △ natal Pluto
16 Jan '26 – 21 Jan '26 — Mars ☌ natal Mars
17 Jan '26 – 20 Jan '26 — Mercury ☌ natal Mars
18 Jan '26 – 1 May '26 — Jupiter □ natal Venus (2x: 4 Feb '26, 15 Apr '26)
18 Jan '26 – 21 Jan '26 — Venus ⚹ natal Mercury
19 Jan '26 – 22 Jan '26 — Venus ⚹ natal Saturn
21 Jan '26 – 23 Jan '26 — Mercury ⚹ natal Mercury
21 Jan '26 – 24 Jan '26 — Sun ⚹ natal Mercury
22 Jan '26 – 25 Jan '26 — Venus □ natal Neptune
22 Jan '26 – 24 Jan '26 — Mercury ⚹ natal Saturn
22 Jan '26 – 25 Jan '26 — Sun ⚹ natal Saturn
24 Jan '26 – 26 Jan '26 — Mercury □ natal Neptune
25 Jan '26 – 29 Jan '26 — Mars ⚹ natal Mercury
25 Jan '26 – 29 Jan '26 — Sun □ natal Neptune
26 Jan '26 – 30 Jan '26 — Mars ⚹ natal Saturn
27 Jan '26 – 30 Jan '26 — Venus ⚹ natal Moon
28 Jan '26 – 30 Jan '26 — Mercury ⚹ natal Moon
28 Jan '26 – 4 May '26 — True Node ⚹ natal Neptune
29 Jan '26 – 31 Jan '26 — Mercury ⚹ natal Venus
29 Jan '26 – 1 Feb '26 — Venus ⚹ natal Venus
30 Jan '26 – 5 Feb '26 — Mars □ natal Neptune
1 Feb '26 – 4 Feb '26 — Sun ⚹ natal Moon
2 Feb '26 – 5 Feb '26 — Mercury □ natal Pluto
4 Feb '26 – 7 Feb '26 — Sun ⚹ natal Venus
4 Feb '26 – 6 Feb '26 — Mercury ☌ natal Jupiter
4 Feb '26 – 7 Feb '26 — Venus □ natal Pluto
6 Feb '26 – 8 Feb '26 — Mercury ☍ natal Uranus
6 Feb '26 – 10 Feb '26 — Venus ☌ natal Jupiter
9 Feb '26 – 12 Feb '26 — Mars ⚹ natal Moon
9 Feb '26 – 13 Feb '26 — Venus ☍ natal Uranus
10 Feb '26 – 12 Feb '26 — Mercury ⚹ natal Neptune
11 Feb '26 – 15 Feb '26 — Sun □ natal Pluto
12 Feb '26 – 15 Feb '26 — Mars ⚹ natal Venus
14 Feb '26 – 18 Feb '26 — Sun ☌ natal Jupiter
14 Feb '26 – 4 Apr '26 — Mercury □ natal Moon (3x: 15 Feb '26, 9 Mar '26, 1 Apr '26)
15 Feb '26 – 17 Feb '26 — Venus ⚹ natal Neptune
17 Feb '26 – 21 Feb '26 — Sun ☍ natal Uranus
20 Feb '26 – 23 Feb '26 — Venus □ natal Moon
21 Feb '26 – 26 Feb '26 — Mars □ natal Pluto
24 Feb '26 – 28 Mar '26 — Saturn ☌ natal Mercury
24 Feb '26 – 1 Mar '26 — Mars ☌ natal Jupiter
24 Feb '26 – 27 Feb '26 — Sun ⚹ natal Neptune
27 Feb '26 – 2 Mar '26 — Venus ☌ natal Sun
1 Mar '26 – 3 Mar '26 — Venus ⚹ natal Pluto
1 Mar '26 – 6 Mar '26 — Mars ☍ natal Uranus
2 Mar '26 – 5 Mar '26 — Venus ⚹ natal Mars
3 Mar '26 – 7 Mar '26 — Sun □ natal Moon
27 Apr '26 — Neptune ☌ natal Mercury
4 Mar '26 – 6 Apr '26 — Saturn ☌ natal Saturn
7 Mar '26 – 10 Mar '26 — Venus ☌ natal Mercury
8 Mar '26 – 11 Mar '26 — Venus ☌ natal Saturn
10 Mar '26 – 14 Mar '26 — Mars ⚹ natal Neptune
12 Mar '26 – 16 Mar '26 — Sun ☌ natal Sun
13 Mar '26 – 16 Mar '26 — Sun ⚹ natal Pluto
16 Mar '26 – 19 Mar '26 — Sun ⚹ natal Mars
16 Mar '26 – 19 Mar '26 — Venus △ natal Moon
18 Mar '26 – 26 May '26 — Chiron □ natal Mars
18 Mar '26 – 23 Mar '26 — Mars □ natal Moon
18 Mar '26 – 21 Mar '26 — Venus ☌ natal Venus
21 Mar '26 – 25 Mar '26 — Sun ☌ natal Mercury
22 Mar '26 – 26 Mar '26 — Sun ☌ natal Saturn
26 Mar '26 – 29 Mar '26 — Venus □ natal Mars
27 Mar '26 – 29 Mar '26 — Venus ⚹ natal Jupiter
29 Mar '26 – 4 Apr '26 — Mars ☌ natal Sun
30 Mar '26 – 2 Apr '26 — Venus △ natal Uranus
1 Apr '26 – 4 Apr '26 — Mars ⚹ natal Pluto
2 Apr '26 – 6 Apr '26 — Sun △ natal Moon
3 Apr '26 – 7 Apr '26 — Mars ⚹ natal Mars
4 Apr '26 – 7 Apr '26 — Venus ☌ natal Neptune
4 Apr '26 – 8 Apr '26 — Sun ☌ natal Venus
5 Apr '26 – 27 May '26 — Chiron ⚹ natal Jupiter
8 Apr '26 – 11 Apr '26 — Mercury ☌ natal Sun
10 Apr '26 – 12 Apr '26 — Mercury ⚹ natal Pluto
11 Apr '26 – 16 Apr '26 — Mars ☌ natal Mercury
11 Apr '26 – 13 Apr '26 — Mercury ⚹ natal Mars
12 Apr '26 – 22 Jun '26 — Uranus □ natal Uranus
12 Apr '26 – 17 Apr '26 — Mars ☌ natal Saturn
14 Apr '26 – 18 Apr '26 — Sun □ natal Mars
15 Apr '26 – 18 Apr '26 — Mercury ☌ natal Mercury
15 Apr '26 – 19 Apr '26 — Sun ⚹ natal Jupiter
16 Apr '26 – 19 Apr '26 — Mercury ☌ natal Saturn
17 Apr '26 – 20 Apr '26 — Venus ⚹ natal Sun
18 Apr '26 – 21 Apr '26 — Venus ☌ natal Pluto
19 Apr '26 – 23 Apr '26 — Sun △ natal Uranus
19 Apr '26 – 23 Apr '26 — Venus △ natal Mars
20 Apr '26 – 23 Apr '26 — Venus □ natal Jupiter
23 Apr '26 – 25 Apr '26 — Mercury △ natal Moon
23 Apr '26 – 26 Apr '26 — Venus □ natal Uranus
24 Apr '26 – 27 Apr '26 — Mercury ☌ natal Venus
25 Apr '26 – 27 Apr '26 — Venus ⚹ natal Mercury
25 Apr '26 – 1 May '26 — Mars △ natal Moon
26 Apr '26 – 30 Apr '26 — Sun ☌ natal Neptune
26 Apr '26 – 28 Apr '26 — Venus ⚹ natal Saturn
29 Apr '26 – 4 May '26 — Mars ☌ natal Venus
30 Apr '26 – 2 May '26 — Mercury □ natal Mars
1 May '26 – 2 May '26 — Mercury ⚹ natal Jupiter
2 May '26 – 4 May '26 — Mercury △ natal Uranus
4 May '26 – 7 May '26 — Venus ☍ natal Moon
6 May '26 – 8 May '26 — Mercury ☌ natal Neptune
6 May '26 – 9 May '26 — Venus ⚹ natal Venus
11 May '26 – 15 May '26 — Venus □ natal Sun
12 May '26 – 17 May '26 — Mars □ natal Mars
12 May '26 – 15 May '26 — Sun ⚹ natal Sun
13 May '26 – 17 May '26 — Sun ☌ natal Pluto
13 May '26 – 17 May '26 — Mars ⚹ natal Jupiter
13 May '26 – 15 May '26 — Mercury ⚹ natal Sun
14 May '26 – 15 May '26 — Mercury ☌ natal Pluto
15 May '26 – 16 May '26 — Mercury △ natal Mars
15 May '26 – 18 May '26 — Venus △ natal Jupiter
15 May '26 – 17 May '26 — Mercury □ natal Jupiter
15 May '26 – 19 May '26 — Sun △ natal Mars
16 May '26 – 20 May '26 — Sun □ natal Jupiter
17 May '26 – 18 May '26 — Mercury □ natal Uranus
17 May '26 – 23 May '26 — Mars △ natal Uranus
18 May '26 – 19 May '26 — Mercury ⚹ natal Mercury
18 May '26 – 20 May '26 — Mercury ⚹ natal Saturn
18 May '26 – 21 May '26 — Venus ⚹ natal Uranus
20 May '26 – 23 May '26 — Venus □ natal Mercury
20 May '26 – 24 May '26 — Sun □ natal Uranus
20 May '26 – 24 May '26 — Venus □ natal Saturn
22 May '26 – 25 May '26 — Sun ⚹ natal Mercury
23 May '26 – 25 May '26 — Mercury ☍ natal Moon
23 May '26 – 26 May '26 — Sun ⚹ natal Saturn
24 May '26 – 26 May '26 — Venus ⚹ natal Neptune
24 May '26 – 26 May '26 — Mercury ⚹ natal Venus
26 May '26 – 1 Jun '26 — Mars ☌ natal Neptune
27 May '26 – 29 May '26 — Mercury □ natal Sun
29 May '26 – 1 Jun '26 — Mercury △ natal Jupiter
```

**Example output:**

```
Dec 2 – Mar 2 '26 — Jupiter △ natal Chiron
Dec 4 — Mercury □ natal Jupiter
Jan 8 – Feb 6 '26 — Uranus △ natal Neptune (2x: Jan 15, Feb 1)
Feb 10 – May 18 '26 — Saturn ☌ natal Moon
```

Multi-pass transits (retrograde creating 2–3 exact crossings) show all exact dates in
parentheses.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `datetime` | required | Start of transit window (UTC) |
| `end` | `datetime` | required | End of transit window (UTC) |
| `transit_planets` | `list[str] \| None` | All 12 | Planets to use as transits |
| `aspects` | `dict[str, float] \| None` | 5 major + orbs | `{aspect_name: orb_degrees}` |
| `include_natal_points` | `list[str] \| None` | All planets | Limit which natal points to check |
| `exclude_fast_planets` | `bool` | `False` | Skip Sun, Moon, Mercury, Venus, Mars |

#### Gantt Chart (SVG)

```python
from stellium.presentation.sections import TransitGanttSection

section = TransitGanttSection(
    start=dt.datetime(2025, 12, 1),
    end=dt.datetime(2026, 6, 1),
    # By default, excludes fast planets (Sun/Moon/Mercury/Venus/Mars)
    # for a readable chart. Set exclude_fast_planets=False to include them.
)

ReportBuilder().from_chart(natal_chart).with_section(section).render(
    format="pdf", file="transits.pdf"
)
```

The SVG Gantt chart shows:
- Each row = one transit event (aspect glyph + natal planet name)
- Colored bars = orb window (color varies by aspect type)
- White tick marks = exact date(s) within the bar
- Rows grouped by transiting planet
- Month grid lines and a dashed "today" marker

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | `datetime` | required | Start of transit window (UTC) |
| `end` | `datetime` | required | End of transit window (UTC) |
| `transit_planets` | `list[str] \| None` | All 12 | Planets to use as transits |
| `aspects` | `dict[str, float] \| None` | 5 major + orbs | `{aspect_name: orb_degrees}` |
| `include_natal_points` | `list[str] \| None` | All planets | Limit which natal points to check |
| `width` | `int` | `900` | SVG width in pixels |
| `row_height` | `int` | `14` | Height of each row in pixels |
| `exclude_fast_planets` | `bool` | `True` | Skip fast planets (default `True` — they produce too many rows for a readable chart) |

#### Custom Aspects and Orbs

```python
# Only outer planet transits, conjunctions and squares, tighter orbs
section = TransitListSection(
    start=dt.datetime(2025, 12, 1),
    end=dt.datetime(2026, 12, 31),
    transit_planets=["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
    aspects={"Conjunction": 1.0, "Square": 1.5, "Opposition": 1.5},
    exclude_fast_planets=True,
)
```

#### Accessing Structured Data

`generate_data()` returns both a formatted text string and a `"periods"` list of dicts
for custom rendering:

```python
data = section.generate_data(natal_chart)

print(data["text"])            # Plain-text output
print(data["total_transits"])  # Count of transit events found

for period in data["periods"]:
    print(period["transit_planet"], period["aspect_name"], period["natal_planet"])
    print("  Start:", period["start"])
    print("  End:",   period["end"])
    print("  Exact:", period["exact_dates"])
    print("  Multi-pass:", period["is_multi_pass"])
```

#### Using `calculate_transit_periods()` Directly

For full control, call the core function directly:

```python
from stellium.presentation.sections import calculate_transit_periods, TransitPeriod

periods: list[TransitPeriod] = calculate_transit_periods(
    natal_chart=chart,
    start=dt.datetime(2025, 12, 1),
    end=dt.datetime(2026, 6, 1),
    transit_planets=["Jupiter", "Saturn"],
    aspects={"Trine": 2.0, "Square": 2.0},
)

for p in periods:
    print(f"{p.transit_planet} {p.aspect_name} natal {p.natal_planet}")
    print(f"  In orb: {p.start} → {p.end}")
    print(f"  Exact: {', '.join(str(d.date()) for d in p.exact_dates)}")
    print(f"  Multi-pass: {p.is_multi_pass}")
```

---

## Presets

Presets bundle common section combinations for convenience.

### `preset_minimal()`

Just the basics: overview and positions.

```python
ReportBuilder().from_chart(chart).preset_minimal().render()
```

**Includes:** Chart Overview, Planet Positions

---

### `preset_standard()`

Common sections for everyday use.

```python
ReportBuilder().from_chart(chart).preset_standard().render()
```

**Includes:** Chart Overview, Planet Positions (with houses), Major Aspects, House Cusps

---

### `preset_detailed()`

Comprehensive report with all major sections.

```python
ReportBuilder().from_chart(chart).preset_detailed().render()
```

**Includes:** Chart Overview, Moon Phase, Planet Positions (with speed and houses), Declinations, All Aspects, House Cusps, Dignities

---

### `preset_full()`

Everything available.

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.components import DignityComponent, MidpointCalculator
from stellium.engines.patterns import AspectPatternAnalyzer

# Calculate with all components
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .add_analyzer(AspectPatternAnalyzer())
    .add_component(MidpointCalculator())
    .calculate()
)

ReportBuilder().from_chart(chart).preset_full().render()
```
<!--pytest-codeblocks:expected-output-->
```

Chart Overview
──────────────
Name: Albert Einstein
Date: March 14, 1879
Time: 11:30 AM
Timezone: Europe/Berlin
Location: Ulm, Germany
Coordinates: 48.3984°, 9.9916°
House System: Placidus
Zodiac: Tropical
Chart Sect: Day Chart
Chart Ruler: Moon (Cancer Rising)

Moon Phase
──────────
Phase Name: Waning Gibbous (261°)
Illumination: 57.9%
Phase Angle: 80.9°
Direction: Waning
Apparent Magnitude: -10.52
Apparent Diameter: 0.5″
Geocentric Parallax: 0.9796 rad
Sun-Moon Separation: 261.0°

Planet Positions
────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Planet              ┃ Position              ┃ House (Pl) ┃ Speed        ┃ Motion     ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ☉ Sun               │ ♓︎ Pisces 23°30'      │ 10         │ 0.9960°/day  │ Direct     │
│ ☽ Moon              │ ♐︎ Sagittarius 14°31' │ 6          │ 13.9189°/day │ Direct     │
│ ☿ Mercury           │ ♈︎ Aries 3°08'        │ 10         │ 1.9519°/day  │ Direct     │
│ ♀ Venus             │ ♈︎ Aries 16°59'       │ 10         │ 1.2318°/day  │ Direct     │
│ ♂ Mars              │ ♑︎ Capricorn 26°54'   │ 7          │ 0.7287°/day  │ Direct     │
│ ♃ Jupiter           │ ♒︎ Aquarius 27°29'    │ 9          │ 0.2274°/day  │ Direct     │
│ ♄ Saturn            │ ♈︎ Aries 4°11'        │ 10         │ 0.1236°/day  │ Direct     │
│ ♅ Uranus            │ ♍︎ Virgo 1°17'        │ 3          │ -0.0396°/day │ Retrograde │
│ ♆ Neptune           │ ♉︎ Taurus 7°52'       │ 11         │ 0.0288°/day  │ Direct     │
│ ♇ Pluto             │ ♉︎ Taurus 24°43'      │ 11         │ 0.0121°/day  │ Direct     │
│ ☊ North Node        │ ♒︎ Aquarius 2°43'     │ 8          │ -0.0193°/day │ Retrograde │
│ ☋ South Node        │ ♌︎ Leo 2°43'          │ 2          │ 0.0193°/day  │ Direct     │
│ ⚸ Black Moon Lilith │ ♈︎ Aries 27°58'       │ 11         │ 0.1121°/day  │ Direct     │
│ 🜊 Vertex            │ ♏︎ Scorpio 27°54'     │ 5          │ 0.0000°/day  │ Direct     │
│ ⚷ Chiron            │ ♉︎ Taurus 5°32'       │ 11         │ 0.0525°/day  │ Direct     │
└─────────────────────┴───────────────────────┴────────────┴──────────────┴────────────┘

Aspects
───────

  Aspectarian
[SVG: 404x404px - use HTML/PDF output to view]

  Aspect List
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Planet 1            ┃ Aspect        ┃ Planet 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☿ Mercury           │ ⚹ Sextile     │ ☊ North Node        │ 0.41° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ ☋ South Node        │ 0.41° │ ←S       │
│ ♃ Jupiter           │ □ Square      │ 🜊 Vertex            │ 0.42° │ —        │
│ ♃ Jupiter           │ ⚹ Sextile     │ ⚸ Black Moon Lilith │ 0.49° │ A→       │
│ ♂ Mars              │ ⚹ Sextile     │ 🜊 Vertex            │ 0.99° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ ♄ Saturn            │ 1.05° │ A→       │
│ ♂ Mars              │ □ Square      │ ⚸ Black Moon Lilith │ 1.06° │ A→       │
│ ☉ Sun               │ ⚹ Sextile     │ ♇ Pluto             │ 1.22° │ A→       │
│ ♄ Saturn            │ ⚹ Sextile     │ ☊ North Node        │ 1.46° │ ←S       │
│ ♄ Saturn            │ △ Trine       │ ☋ South Node        │ 1.46° │ ←S       │
│ ☽ Moon              │ □ Square      │ MC                  │ 1.69° │ —        │
│ ♂ Mars              │ △ Trine       │ ♇ Pluto             │ 2.19° │ ←S       │
│ ♆ Neptune           │ ☌ Conjunction │ ⚷ Chiron            │ 2.33° │ A→       │
│ ☽ Moon              │ △ Trine       │ ♀ Venus             │ 2.46° │ A→       │
│ ♃ Jupiter           │ □ Square      │ ♇ Pluto             │ 2.76° │ ←S       │
│ ⚷ Chiron            │ □ Square      │ ☋ South Node        │ 2.81° │ ←S       │
│ ☊ North Node        │ □ Square      │ ⚷ Chiron            │ 2.81° │ ←S       │
│ ♇ Pluto             │ ☍ Opposition  │ 🜊 Vertex            │ 3.18° │ —        │
│ ♅ Uranus            │ △ Trine       │ ⚸ Black Moon Lilith │ 3.31° │ A→       │
│ ♅ Uranus            │ □ Square      │ 🜊 Vertex            │ 3.38° │ —        │
│ ☉ Sun               │ ⚹ Sextile     │ ♂ Mars              │ 3.41° │ A→       │
│ ♆ Neptune           │ ⚹ Sextile     │ ASC                 │ 3.77° │ —        │
│ ♃ Jupiter           │ ☍ Opposition  │ ♅ Uranus            │ 3.80° │ A→       │
│ ♅ Uranus            │ △ Trine       │ ⚷ Chiron            │ 4.26° │ ←S       │
│ ☉ Sun               │ △ Trine       │ 🜊 Vertex            │ 4.40° │ —        │
│ ⚸ Black Moon Lilith │ □ Square      │ ☋ South Node        │ 4.75° │ A→       │
│ ☊ North Node        │ □ Square      │ ⚸ Black Moon Lilith │ 4.75° │ A→       │
│ ☋ South Node        │ △ Trine       │ 🜊 Vertex            │ 4.83° │ —        │
│ ☊ North Node        │ ⚹ Sextile     │ 🜊 Vertex            │ 4.83° │ —        │
│ ♆ Neptune           │ ⚹ Sextile     │ MC                  │ 4.97° │ —        │
│ ♆ Neptune           │ □ Square      │ ☋ South Node        │ 5.14° │ ←S       │
│ ♆ Neptune           │ □ Square      │ ☊ North Node        │ 5.14° │ ←S       │
│ ☿ Mercury           │ △ Trine       │ 🜊 Vertex            │ 5.24° │ —        │
│ ♀ Venus             │ □ Square      │ ASC                 │ 5.34° │ —        │
│ ♂ Mars              │ ☌ Conjunction │ ☊ North Node        │ 5.82° │ A→       │
│ ♂ Mars              │ ☍ Opposition  │ ☋ South Node        │ 5.82° │ A→       │
│ ♄ Saturn            │ △ Trine       │ 🜊 Vertex            │ 6.29° │ —        │
│ ♅ Uranus            │ □ Square      │ ♇ Pluto             │ 6.56° │ A→       │
│ ♅ Uranus            │ △ Trine       │ ♆ Neptune           │ 6.58° │ ←S       │
│ ♄ Saturn            │ □ Square      │ ASC                 │ 7.46° │ —        │
│ ⚷ Chiron            │ ☌ Conjunction │ ⚸ Black Moon Lilith │ 7.57° │ A→       │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘

Aspect Patterns
───────────────
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern     ┃ Planets                             ┃ Element/Quality ┃ Details                    ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Grand Cross │ ♃ Jupiter, ♅ Uranus, ♇ Pluto, 🜊     │ Mixed           │ 4 planets                  │
│             │ Vertex                              │                 │                            │
│ Stellium    │ ☿ Mercury, ♀ Venus, ♄ Saturn        │ Fire / Cardinal │ 3 planets                  │
│ T-Square    │ ♃ Jupiter, ♅ Uranus, ♇ Pluto        │ Mixed           │ 3 planets, Apex: ♇ Pluto   │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♃ Jupiter        │ Fixed           │ 3 planets, Apex: ♃ Jupiter │
│ T-Square    │ ♇ Pluto, 🜊 Vertex, ♅ Uranus         │ Mixed           │ 3 planets, Apex: ♅ Uranus  │
└─────────────┴─────────────────────────────────────┴─────────────────┴────────────────────────────┘

Declinations
────────────
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ Planet       ┃ Declination ┃ Direction ┃ Status ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ ☉ Sun        │ 2°34'       │ South     │        │
│ ☽ Moon       │ 26°21'      │ South     │ OOB ⚠  │
│ ☿ Mercury    │ 0°53'       │ North     │        │
│ ♀ Venus      │ 6°02'       │ North     │        │
│ ♂ Mars       │ 21°37'      │ South     │        │
│ ♃ Jupiter    │ 13°04'      │ South     │        │
│ ♄ Saturn     │ 0°18'       │ South     │        │
│ ♅ Uranus     │ 11°46'      │ North     │        │
│ ♆ Neptune    │ 12°29'      │ North     │        │
│ ♇ Pluto      │ 5°39'       │ North     │        │
│ ☊ North Node │ 19°33'      │ South     │        │
└──────────────┴─────────────┴───────────┴────────┘

Declination Aspects
───────────────────
No declination aspects calculated. Enable with:

  chart = (ChartBuilder.from_native(native)
      .with_aspects()
      .with_declination_aspects(orb=1.0)
      .calculate())

Midpoints
─────────
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Midpoint       ┃ Position          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Sun/Moon       │ 4° Aquarius 01'   │
│ Sun/Mercury    │ 28° Pisces 19'    │
│ Sun/Venus      │ 5° Aries 14'      │
│ Sun/Mars       │ 25° Aquarius 12'  │
│ Sun/Jupiter    │ 10° Pisces 29'    │
│ Sun/Saturn     │ 28° Pisces 50'    │
│ Sun/ASC        │ 17° Taurus 34'    │
│ Sun/MC         │ 18° Pisces 10'    │
│ Moon/Mercury   │ 8° Aquarius 50'   │
│ Moon/Venus     │ 15° Aquarius 45'  │
│ Moon/Mars      │ 5° Capricorn 43'  │
│ Moon/Jupiter   │ 21° Capricorn 00' │
│ Moon/Saturn    │ 9° Aquarius 21'   │
│ Moon/ASC       │ 28° Virgo 05'     │
│ Moon/MC        │ 28° Capricorn 40' │
│ Mercury/Venus  │ 10° Aries 03'     │
│ Mercury/Mars   │ 0° Pisces 01'     │
│ Venus/Mars     │ 6° Pisces 56'     │
│ Venus/Jupiter  │ 22° Pisces 14'    │
│ Mars/Jupiter   │ 12° Aquarius 11'  │
│ Mars/Saturn    │ 0° Pisces 33'     │
│ Jupiter/Saturn │ 15° Pisces 50'    │
│ ASC/MC         │ 12° Taurus 14'    │
└────────────────┴───────────────────┘

Planets Conjunct Midpoints
──────────────────────────
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Planet       ┃ Aspect        ┃ Midpoint      ┃ Orb   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━┩
│ ♄ Saturn     │ ☌ Conjunction │ Sun/Venus     │ 1.06° │
│ ☉ Sun        │ ☌ Conjunction │ Venus/Jupiter │ 1.27° │
│ ☊ North Node │ ☌ Conjunction │ Sun/Moon      │ 1.29° │
└──────────────┴───────────────┴───────────────┴───────┘

Fixed Stars
───────────
No fixed stars calculated. Add FixedStarsComponent() to include them:

    from stellium.components import FixedStarsComponent

    chart = (
        ChartBuilder.from_native(native)
        .add_component(FixedStarsComponent())
        .calculate()
    )

House Cusps
───────────
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ House ┃ Cusp (Pl)  ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ 11° ♋︎ 38' │
│ 2     │ 28° ♋︎ 36' │
│ 3     │ 17° ♌︎ 48' │
│ 4     │ 12° ♍︎ 50' │
│ 5     │ 18° ♎︎ 19' │
│ 6     │ 3° ♐︎ 06'  │
│ 7     │ 11° ♑︎ 38' │
│ 8     │ 28° ♑︎ 36' │
│ 9     │ 17° ♒︎ 48' │
│ 10    │ 12° ♓︎ 50' │
│ 11    │ 18° ♈︎ 19' │
│ 12    │ 3° ♊︎ 06'  │
└───────┴────────────┘

Essential Dignities
───────────────────
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Planet    ┃ Traditional Dignities                     ┃ Modern Dignities                         ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ☉ Sun     │ Peregrine                                 │ Peregrine                                │
│ ☽ Moon    │ Peregrine                                 │ Peregrine                                │
│ ☿ Mercury │ Peregrine                                 │ Peregrine                                │
│ ♀ Venus   │ Detriment, Peregrine                      │ Detriment (modern), Peregrine            │
│ ♂ Mars    │ Exaltation, Exaltation (exact),           │ Exaltation, Exaltation (exact),          │
│           │ Participating Ruler, Term                 │ Triplicity (participating), Term         │
│ ♃ Jupiter │ Participating Ruler                       │ Triplicity (participating)               │
│ ♄ Saturn  │ Participating Ruler, Fall                 │ Triplicity (participating), Fall         │
│ ♅ Uranus  │ —                                         │ Peregrine                                │
│ ♆ Neptune │ —                                         │ Peregrine                                │
│ ♇ Pluto   │ —                                         │ Detriment (modern), Peregrine            │
│ ⚷ Chiron  │ —                                         │ Peregrine                                │
└───────────┴───────────────────────────────────────────┴──────────────────────────────────────────┘

Dispositors
───────────

  Dispositor Graph
[SVG: 806x272px - use HTML/PDF output to view]

  Planetary Dispositors
  Final Dispositor: ♂ Mars ↔ ♄ Saturn (mutual reception)

Mutual Receptions:
  ♂ Mars ↔ ♄ Saturn

Disposition Chains:
  ♃ → ♄ → ♂ → ♄
  ♂ → ♄ → ♂
  ☿ → ♂ → ♄ → ♂
  ☽ → ♃ → ♄ → ♂ → ♄
  ♄ → ♂ → ♄
  ☉ → ♃ → ♄ → ♂ → ♄
  ♀ → ♂ → ♄ → ♂

  House-Based Dispositors
  Final Dispositor: House 10 ↔ House 9 (mutual reception)

Mutual Receptions:
  House 9 (♄ Saturn) ↔ House 10 (♃ Jupiter)

Disposition Chains:
  1 → 6 → 9 → 10 → 9
  10 → 9 → 10
  11 → 7 → 10 → 9 → 10
  12 → 10 → 9 → 10
  2 → 6 → 9 → 10 → 9
  3 → 10 → 9 → 10
  4 → 10 → 9 → 10
  5 → 10 → 9 → 10
  6 → 9 → 10 → 9
  7 → 10 → 9 → 10
  8 → 10 → 9 → 10
  9 → 10 → 9

Zodiacal Releasing
──────────────────
Zodiacal Releasing not calculated. Add ZodiacalReleasingAnalyzer:

  from stellium.engines.releasing import ZodiacalReleasingAnalyzer

  chart = (
      ChartBuilder.from_native(native)
      .add_analyzer(ZodiacalReleasingAnalyzer(['Part of Fortune']))
      .calculate()
  )
```

**Includes:** Everything in `preset_detailed()` plus Aspect Patterns and Midpoints

---

### `preset_positions_only()`

Focus on planetary placements, no aspects.

```python
ReportBuilder().from_chart(chart).preset_positions_only().render()
```

**Includes:** Chart Overview, Planet Positions (with speed and houses), Declinations, House Cusps

---

### `preset_aspects_only()`

Focus on planetary relationships.

```python
ReportBuilder().from_chart(chart).preset_aspects_only().render()
```

**Includes:** Chart Overview, All Aspects, Aspect Patterns

---

### `preset_synastry()`

Optimized for relationship comparison charts.

```python
multichart = MultiChartBuilder.synastry(chart1, chart2).calculate()
ReportBuilder().from_chart(multichart).preset_synastry().render()
```

**Includes:** Chart Overview (both charts), Planet Positions (side-by-side), Cross-Chart Aspects (major), House Cusps (side-by-side)

---

### `preset_transit()`

Optimized for transit charts.

```python
transit = MultiChartBuilder.transit(natal_chart, transit_datetime).calculate()
ReportBuilder().from_chart(transit).preset_transit().render()
```

**Includes:** Chart Overview, Planet Positions (side-by-side), Cross-Chart Aspects (all), House Cusps (side-by-side)

---

## Output Formats

### Terminal Output (Rich)

Beautiful colored tables in your terminal using the [Rich](https://rich.readthedocs.io/) library.

```python
# Display in terminal (default)
ReportBuilder().from_chart(chart).preset_standard().render()

# Same as:
ReportBuilder().from_chart(chart).preset_standard().render(format="rich_table")

# Save to file AND display in terminal
ReportBuilder().from_chart(chart).preset_standard().render(
    format="rich_table",
    file="report.txt"
)

# Save to file without terminal display
ReportBuilder().from_chart(chart).preset_standard().render(
    format="rich_table",
    file="report.txt",
    show=False
)
```

---

### Plain Text

ASCII tables suitable for logs, emails, or systems without Rich.

```python
ReportBuilder().from_chart(chart).preset_standard().render(format="plain_table")

# Save to file
ReportBuilder().from_chart(chart).preset_standard().render(
    format="plain_table",
    file="report.txt"
)
```

---

### PDF with Typst

**This is the star feature!** Generate beautiful, professional-quality PDF reports using [Typst](https://typst.app/).

```python
# Basic PDF
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="report.pdf"
)

# PDF with embedded chart wheel
chart.draw("chart.svg").save()  # First, save the chart as SVG
ReportBuilder().from_chart(chart).preset_detailed().with_chart_image("chart.svg").render(
    format="pdf",
    file="report.pdf",
)

# Custom title
ReportBuilder().from_chart(chart).preset_detailed().with_chart_image("chart.svg").with_title("Albert Einstein — Natal Chart Analysis").render(
    format="pdf",
    file="report.pdf",
)
```

#### Typst PDF Features

- **Professional typography:** Proper kerning, ligatures, and hyphenation
- **Beautiful fonts:** Cinzel Decorative for headings, Crimson Pro for body text
- **Warm color palette:** Deep purple headers, cream backgrounds, gold accents
- **Elegant design:** Star dividers, rounded table corners, alternating row colors
- **Chart embedding:** SVG chart wheels displayed on the title page
- **Page headers/footers:** Automatic page numbering

#### Installing Typst

```bash
pip install typst
```

#### PDF Examples

**Full natal chart report with chart wheel:**

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.components import DignityComponent

# Calculate chart
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

# Generate chart wheel
chart.draw("einstein_chart.svg").with_theme("celestial").save()

# Generate PDF report
ReportBuilder().from_chart(chart).preset_detailed().with_chart_image("einstein_chart.svg").with_title("Albert Einstein — Natal Chart").render(
    format="pdf",
    file="einstein_report.pdf",
)
```
**Synastry report for two people:**

```python
from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder

# Calculate individual charts
einstein = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
lovelace = ChartBuilder.from_notable("Ada Lovelace").with_aspects().calculate()

# Create synastry comparison
synastry = MultiChartBuilder.synastry(
    einstein, lovelace, label1="Albert Einstein", label2="Ada Lovelace"
).calculate()

# Generate biwheel chart
synastry.draw("synastry_chart.svg").with_theme("midnight").save()

# Generate synastry report
ReportBuilder().from_chart(synastry).preset_synastry().with_chart_image("synastry_chart.svg").with_title("Einstein & Lovelace — Synastry Analysis").render(
    format="pdf",
    file="synastry_report.pdf",
)
```
---

### HTML

Generate HTML reports (useful for web applications).

```python
ReportBuilder().from_chart(chart).preset_standard().render(
    format="html",
    file="report.html"
)

# With embedded chart
ReportBuilder().from_chart(chart).preset_standard().with_chart_image("chart.svg").render(
    format="html",
    file="report.html",
)
```

---

## Comparison Chart Reports

Stellium fully supports comparison charts (synastry, transits, composites) in reports.

### Side-by-Side Tables

When you pass a `MultiChart` object to ReportBuilder, sections that show chart data automatically render as side-by-side tables:

- **Planet Positions:** Two tables, one for each chart
- **House Cusps:** Two tables, one for each chart

The tables are labeled with the chart labels you provide to MultiChartBuilder.

### Example: Complete Synastry Report

```python
from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder
from stellium.components import DignityComponent

# Calculate charts with dignities
chart1 = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

chart2 = (
    ChartBuilder.from_notable("Ada Lovelace")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

# Create multichart with meaningful labels
multichart = MultiChartBuilder.synastry(
    chart1, chart2, label1="Albert", label2="Ada"
).calculate()

# Build custom synastry report
ReportBuilder().from_chart(multichart) \
    .with_chart_overview() \
    .with_planet_positions(include_house=True) \
    .with_cross_aspects(mode="major", sort_by="orb") \
    .with_house_cusps() \
    .render(format="pdf", file="synastry.pdf")
```
### Example: Transit Report

```python
from datetime import datetime
from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder

# Natal chart
natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

# Create transit comparison (uses natal chart's location automatically)
transits = MultiChartBuilder.transit(natal, datetime.now()).calculate()

# Generate transit report
ReportBuilder().from_chart(transits).preset_transit().with_title("Current Transits for Albert Einstein").render(
    format="pdf",
    file="transits.pdf",
)
```
---

## Custom Sections

You can create custom sections by implementing the `ReportSection` protocol.

### The Protocol

```python
from typing import Any
from stellium.core.models import CalculatedChart

class ReportSection:
    @property
    def section_name(self) -> str:
        """Return the section title."""
        ...

    def generate_data(self, chart: CalculatedChart) -> dict[str, Any]:
        """Generate section data from the chart."""
        ...
```
### Data Types

Your `generate_data()` method should return a dictionary with a `type` key:

**Table:**
```python
{
    "type": "table",
    "headers": ["Column 1", "Column 2", "Column 3"],
    "rows": [
        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
    ]
}
```

**Key-Value:**
```python
{
    "type": "key_value",
    "data": {
        "Key 1": "Value 1",
        "Key 2": "Value 2",
    }
}
```

**Text:**
```python
{
    "type": "text",
    "text": "Plain text content here."
}
```

**Side-by-Side Tables (for comparisons):**
```python
{
    "type": "side_by_side_tables",
    "tables": [
        {
            "title": "Table 1 Title",
            "headers": ["Col 1", "Col 2"],
            "rows": [["A", "B"], ["C", "D"]]
        },
        {
            "title": "Table 2 Title",
            "headers": ["Col 1", "Col 2"],
            "rows": [["E", "F"], ["G", "H"]]
        }
    ]
}
```

### Example: Custom Section

```python
from stellium.core.models import CalculatedChart, ObjectType

class ElementBalanceSection:
    """Custom section showing element distribution."""

    @property
    def section_name(self) -> str:
        return "Element Balance"

    def generate_data(self, chart: CalculatedChart) -> dict:
        # Count planets in each element
        elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
        element_signs = {
            "Fire": ["Aries", "Leo", "Sagittarius"],
            "Earth": ["Taurus", "Virgo", "Capricorn"],
            "Air": ["Gemini", "Libra", "Aquarius"],
            "Water": ["Cancer", "Scorpio", "Pisces"],
        }

        for pos in chart.positions:
            if pos.object_type == ObjectType.PLANET:
                for element, signs in element_signs.items():
                    if pos.sign in signs:
                        elements[element] += 1
                        break

        return {
            "type": "key_value",
            "data": {
                f"{element}": f"{count} planets"
                for element, count in elements.items()
            }
        }

# Use it
ReportBuilder().from_chart(chart) \
    .with_chart_overview() \
    .with_section(ElementBalanceSection()) \
    .render()
```

---

## Complete Examples

### Example 1: Quick Terminal Report

```python
from stellium import ChartBuilder, ReportBuilder

chart = ChartBuilder.from_notable("Frida Kahlo").with_aspects().calculate()
ReportBuilder().from_chart(chart).preset_standard().render()
```
<!--pytest-codeblocks:expected-output-->
```

Chart Overview
──────────────
Name: Frida Kahlo
Date: July 06, 1907
Time: 08:30 AM
Timezone: America/Mexico_City
Location: Coyoacán, Mexico
Coordinates: 19.3467°, -99.1618°
House System: Placidus
Zodiac: Tropical
Chart Ruler: Sun (Leo Rising)

Planet Positions
────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Planet              ┃ Position            ┃ House (Pl) ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ☉ Sun               │ ♋︎ Cancer 13°22'    │ 11         │
│ ☽ Moon              │ ♉︎ Taurus 29°42'    │ 10         │
│ ☿ Mercury           │ ♌︎ Leo 6°20'        │ 12         │
│ ♀ Venus             │ ♊︎ Gemini 24°20'    │ 10         │
│ ♂ Mars              │ ♑︎ Capricorn 13°23' │ 5          │
│ ♃ Jupiter           │ ♋︎ Cancer 20°26'    │ 11         │
│ ♄ Saturn            │ ♓︎ Pisces 27°26'    │ 8          │
│ ♅ Uranus            │ ♑︎ Capricorn 10°36' │ 5          │
│ ♆ Neptune           │ ♋︎ Cancer 12°23'    │ 11         │
│ ♇ Pluto             │ ♊︎ Gemini 23°44'    │ 10         │
│ ☊ North Node        │ ♋︎ Cancer 23°24'    │ 11         │
│ ☋ South Node        │ ♑︎ Capricorn 23°24' │ 5          │
│ ⚸ Black Moon Lilith │ ♋︎ Cancer 9°58'     │ 11         │
│ 🜊 Vertex            │ ♏︎ Scorpio 26°14'   │ 4          │
│ ⚷ Chiron            │ ♒︎ Aquarius 17°17'  │ 6          │
└─────────────────────┴─────────────────────┴────────────┘

Major Aspects
─────────────

  Aspectarian
[SVG: 404x404px - use HTML/PDF output to view]

  Aspect List
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Planet 1     ┃ Aspect        ┃ Planet 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☉ Sun        │ ☍ Opposition  │ ♂ Mars              │ 0.02° │ A→       │
│ ☋ South Node │ △ Trine       │ MC                  │ 0.07° │ —        │
│ ☊ North Node │ ⚹ Sextile     │ MC                  │ 0.07° │ —        │
│ ♇ Pluto      │ ⚹ Sextile     │ ASC                 │ 0.22° │ —        │
│ ♀ Venus      │ ☌ Conjunction │ ♇ Pluto             │ 0.59° │ ←S       │
│ ♅ Uranus     │ ☍ Opposition  │ ⚸ Black Moon Lilith │ 0.64° │ A→       │
│ ♀ Venus      │ ⚹ Sextile     │ ASC                 │ 0.82° │ —        │
│ ☉ Sun        │ ☌ Conjunction │ ♆ Neptune           │ 0.98° │ ←S       │
│ ♂ Mars       │ ☍ Opposition  │ ♆ Neptune           │ 1.00° │ A→       │
│ ♄ Saturn     │ △ Trine       │ 🜊 Vertex            │ 1.20° │ —        │
│ ♅ Uranus     │ ☍ Opposition  │ ♆ Neptune           │ 1.78° │ ←S       │
│ ☽ Moon       │ ⚹ Sextile     │ ♄ Saturn            │ 2.27° │ ←S       │
│ ♆ Neptune    │ ☌ Conjunction │ ⚸ Black Moon Lilith │ 2.42° │ A→       │
│ ASC          │ □ Square      │ 🜊 Vertex            │ 2.73° │ —        │
│ ☉ Sun        │ ☍ Opposition  │ ♅ Uranus            │ 2.76° │ ←S       │
│ ♂ Mars       │ ☌ Conjunction │ ♅ Uranus            │ 2.78° │ A→       │
│ ☋ South Node │ ⚹ Sextile     │ 🜊 Vertex            │ 2.84° │ —        │
│ ☊ North Node │ △ Trine       │ 🜊 Vertex            │ 2.84° │ —        │
│ ♃ Jupiter    │ ⚹ Sextile     │ MC                  │ 2.90° │ —        │
│ MC           │ ☍ Opposition  │ 🜊 Vertex            │ 2.91° │ —        │
│ ♃ Jupiter    │ ☌ Conjunction │ ☊ North Node        │ 2.98° │ A→       │
│ ♃ Jupiter    │ ☍ Opposition  │ ☋ South Node        │ 2.98° │ A→       │
│ ♀ Venus      │ □ Square      │ ♄ Saturn            │ 3.11° │ A→       │
│ ☉ Sun        │ ☌ Conjunction │ ⚸ Black Moon Lilith │ 3.40° │ ←S       │
│ ♂ Mars       │ ☍ Opposition  │ ⚸ Black Moon Lilith │ 3.42° │ A→       │
│ ☽ Moon       │ ☍ Opposition  │ 🜊 Vertex            │ 3.46° │ —        │
│ ♄ Saturn     │ □ Square      │ ♇ Pluto             │ 3.70° │ A→       │
│ ♄ Saturn     │ ⚹ Sextile     │ ☋ South Node        │ 4.03° │ A→       │
│ ♄ Saturn     │ △ Trine       │ ☊ North Node        │ 4.03° │ ←S       │
│ ♄ Saturn     │ ⚹ Sextile     │ MC                  │ 4.11° │ —        │
│ ♃ Jupiter    │ △ Trine       │ 🜊 Vertex            │ 5.81° │ —        │
│ ⚷ Chiron     │ □ Square      │ MC                  │ 6.04° │ —        │
│ ☽ Moon       │ □ Square      │ ASC                 │ 6.19° │ —        │
│ ⚷ Chiron     │ ☍ Opposition  │ ASC                 │ 6.23° │ —        │
│ ☽ Moon       │ △ Trine       │ ☋ South Node        │ 6.30° │ ←S       │
│ ☽ Moon       │ ☌ Conjunction │ MC                  │ 6.37° │ —        │
│ ♇ Pluto      │ △ Trine       │ ⚷ Chiron            │ 6.45° │ ←S       │
│ ♃ Jupiter    │ △ Trine       │ ♄ Saturn            │ 7.01° │ A→       │
│ ♂ Mars       │ ☍ Opposition  │ ♃ Jupiter           │ 7.04° │ ←S       │
│ ♀ Venus      │ △ Trine       │ ⚷ Chiron            │ 7.05° │ ←S       │
│ ☉ Sun        │ ☌ Conjunction │ ♃ Jupiter           │ 7.06° │ A→       │
└──────────────┴───────────────┴─────────────────────┴───────┴──────────┘

House Cusps
───────────
┏━━━━━━━┳━━━━━━━━━━━━┓
┃ House ┃ Cusp (Pl)  ┃
┡━━━━━━━╇━━━━━━━━━━━━┩
│ 1     │ 23° ♌︎ 31' │
│ 2     │ 21° ♍︎ 02' │
│ 3     │ 21° ♎︎ 35' │
│ 4     │ 23° ♏︎ 20' │
│ 5     │ 24° ♐︎ 21' │
│ 6     │ 24° ♑︎ 16' │
│ 7     │ 23° ♒︎ 31' │
│ 8     │ 21° ♓︎ 02' │
│ 9     │ 21° ♈︎ 35' │
│ 10    │ 23° ♉︎ 20' │
│ 11    │ 24° ♊︎ 21' │
│ 12    │ 24° ♋︎ 16' │
└───────┴────────────┘
```

### Example 2: Full PDF Report with Everything

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.components import DignityComponent, MidpointCalculator
from stellium.engines import PlacidusHouses, WholeSignHouses
from stellium.engines.patterns import AspectPatternAnalyzer

# Calculate chart with all components and multiple house systems
chart = (
    ChartBuilder.from_notable("Carl Jung")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects()
    .add_component(DignityComponent())
    .add_analyzer(AspectPatternAnalyzer())
    .add_component(MidpointCalculator())
    .calculate()
)

# Generate chart wheel with styling
chart.draw("jung_chart.svg") \
    .with_theme("midnight") \
    .with_zodiac_palette("rainbow_midnight") \
    .with_moon_phase(position="bottom-left") \
    .with_chart_info(position="top-left") \
    .save()

# Generate comprehensive PDF report
ReportBuilder().from_chart(chart).preset_full().with_chart_image("jung_chart.svg").with_title("Carl Jung — Complete Natal Analysis").render(
    format="pdf",
    file="jung_report.pdf",
)
```
### Example 3: Comparison Report (Synastry)

```python
from stellium import ChartBuilder, MultiChartBuilder, ReportBuilder

# Two charts
person1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
person2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

# Synastry comparison
synastry = MultiChartBuilder.synastry(
    person1, person2, label1="John Lennon", label2="Yoko Ono"
).calculate()

# Generate biwheel
synastry.draw("lennon_ono_biwheel.svg").with_theme("celestial").save()

# Generate report
ReportBuilder().from_chart(synastry).preset_synastry().with_chart_image("lennon_ono_biwheel.svg").with_title("John Lennon & Yoko Ono — Synastry").render(
    format="pdf",
    file="lennon_ono_synastry.pdf",
)
```
### Example 4: Custom Report with Selected Sections

```python
from stellium import ChartBuilder, ReportBuilder

chart = ChartBuilder.from_notable("Nikola Tesla").with_aspects().calculate()

# Pick exactly what you want
ReportBuilder().from_chart(chart) \
    .with_chart_overview() \
    .with_planet_positions(include_speed=True, include_house=True) \
    .with_declinations() \
    .with_aspects(mode="major", sort_by="planet") \
    .render(format="pdf", file="tesla_custom.pdf")
```
### Example 5: Batch Report Generation

```python
from stellium import ChartBuilder, ReportBuilder

notables = ["Albert Einstein", "Marie Curie", "Nikola Tesla", "Frida Kahlo"]

for name in notables:
    chart = ChartBuilder.from_notable(name).with_aspects().calculate()

    # Safe filename
    filename = name.lower().replace(" ", "_")

    # Generate chart
    chart.draw(f"{filename}_chart.svg").with_theme("celestial").save()

    # Generate report
    ReportBuilder().from_chart(chart).preset_detailed().with_chart_image(f"{filename}_chart.svg").with_title(f"{name} — Natal Chart").render(
        format="pdf",
        file=f"{filename}_report.pdf",
    )

    print(f"Generated report for {name}")
```
<!--pytest-codeblocks:expected-output-->
```
Generated report for Albert Einstein
Generated report for Marie Curie
Generated report for Nikola Tesla
Generated report for Frida Kahlo
```

---

## API Reference

### ReportBuilder Methods

| Method | Description |
|--------|-------------|
| `.from_chart(chart)` | Set the chart to report on |
| `.with_chart_overview()` | Add chart info section |
| `.with_planet_positions(...)` | Add planet positions table |
| `.with_aspects(...)` | Add aspects table |
| `.with_cross_aspects(...)` | Add cross-chart aspects (comparisons) |
| `.with_house_cusps(...)` | Add house cusps table |
| `.with_declinations()` | Add declinations table |
| `.with_moon_phase()` | Add moon phase info |
| `.with_dignities(...)` | Add essential dignities |
| `.with_aspect_patterns(...)` | Add aspect patterns |
| `.with_midpoints(...)` | Add midpoints table |
| `.with_section(section)` | Add custom section |
| `.preset_minimal()` | Apply minimal preset |
| `.preset_standard()` | Apply standard preset |
| `.preset_detailed()` | Apply detailed preset |
| `.preset_full()` | Apply full preset |
| `.preset_positions_only()` | Apply positions-only preset |
| `.preset_aspects_only()` | Apply aspects-only preset |
| `.preset_synastry()` | Apply synastry preset |
| `.preset_transit()` | Apply transit preset |
| `.render(...)` | Generate output |

### render() Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | `str` | `"rich_table"` | Output format |
| `file` | `str \| None` | `None` | Save to file |
| `show` | `bool \| None` | `None` | Display in terminal (defaults to `True` for terminal formats, `False` for file formats) |

> **Note:** Chart images and titles are configured via builder methods (`.with_chart_image(path)` and `.with_title(title)`), not as `render()` parameters.

### Output Formats

| Format | Description | Terminal | File |
|--------|-------------|----------|------|
| `"rich_table"` | Colored terminal tables | Yes | .txt |
| `"plain_table"` | ASCII tables | Yes | .txt |
| `"text"` | Plain text | Yes | .txt |
| `"pdf"` | Typst PDF | No | .pdf |
| `"html"` | HTML document | No | .html |

---

## Troubleshooting

### "Typst library not available"

Install Typst:
```bash
pip install typst
```

### "No chart set"

You must call `.from_chart(chart)` before `.render()`:
```python
# Wrong
ReportBuilder().preset_standard().render()

# Right
ReportBuilder().from_chart(chart).preset_standard().render()
```

### Missing dignities/patterns/midpoints

These sections require components to be added during chart calculation:
```python
from stellium.components import DignityComponent, MidpointCalculator
from stellium.engines.patterns import AspectPatternAnalyzer

chart = (
    ChartBuilder.from_native(native)
    .with_aspects()
    .add_component(DignityComponent())        # For .with_dignities()
    .add_analyzer(AspectPatternAnalyzer())    # For .with_aspect_patterns()
    .add_component(MidpointCalculator())      # For .with_midpoints()
    .calculate()
)
```

### PDF fonts look wrong

The Typst renderer bundles its complete font stack — the display/body/mono faces
each theme uses (Cinzel, Cormorant Garamond, EB Garamond, Newsreader, Spectral,
Space Grotesk, IBM Plex Serif/Mono) plus the `Noto Sans Symbols` glyph fonts —
inside the package at `stellium/data/fonts/` (all SIL Open Font License; see
`LICENSE-FONTS.txt` there). They ship in the wheel and are passed to the Typst
compile automatically, so PDFs render identically on any machine with no host
fonts required. If glyphs still look wrong, confirm the package data installed
(`pip install --force-reinstall stellium`).

---

Happy charting!
