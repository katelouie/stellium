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

# Save as a beautiful PDF
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="einstein_report.pdf",
    chart_svg_path="einstein_chart.svg"  # Optional: embed the chart wheel
)
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

chart = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

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
from stellium import ComparisonBuilder

# Create a synastry comparison
chart1 = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
chart2 = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()
comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()

# Show cross-chart aspects
ReportBuilder().from_chart(comparison).with_cross_aspects().render()

# Major aspects only
ReportBuilder().from_chart(comparison).with_cross_aspects(mode="major").render()
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
from stellium.components import AspectPatternAnalyzer

# Calculate chart with pattern analysis
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(AspectPatternAnalyzer())
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
from stellium.components import DignityComponent, AspectPatternAnalyzer, MidpointCalculator

# Calculate with all components
chart = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .add_component(AspectPatternAnalyzer())
    .add_component(MidpointCalculator())
    .calculate()
)

ReportBuilder().from_chart(chart).preset_full().render()
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
comparison = ComparisonBuilder.synastry(chart1, chart2).calculate()
ReportBuilder().from_chart(comparison).preset_synastry().render()
```

**Includes:** Chart Overview (both charts), Planet Positions (side-by-side), Cross-Chart Aspects (major), House Cusps (side-by-side)

---

### `preset_transit()`

Optimized for transit charts.

```python
transit = ComparisonBuilder.transit(natal_chart, transit_datetime).calculate()
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
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="report.pdf",
    chart_svg_path="chart.svg"
)

# Custom title
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="report.pdf",
    chart_svg_path="chart.svg",
    title="Albert Einstein — Natal Chart Analysis"
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
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="einstein_report.pdf",
    chart_svg_path="einstein_chart.svg",
    title="Albert Einstein — Natal Chart"
)
```

**Synastry report for two people:**

```python
from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder

# Calculate individual charts
einstein = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
curie = ChartBuilder.from_notable("Marie Curie").with_aspects().calculate()

# Create synastry comparison
comparison = (
    ComparisonBuilder.from_native(einstein, native_label="Albert Einstein")
    .with_partner(curie, partner_label="Marie Curie")
    .calculate()
)

# Generate biwheel chart
comparison.draw("synastry_chart.svg").with_theme("midnight").save()

# Generate synastry report
ReportBuilder().from_chart(comparison).preset_synastry().render(
    format="pdf",
    file="synastry_report.pdf",
    chart_svg_path="synastry_chart.svg",
    title="Einstein & Curie — Synastry Analysis"
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
ReportBuilder().from_chart(chart).preset_standard().render(
    format="html",
    file="report.html",
    chart_svg_path="chart.svg"
)
```

---

## Comparison Chart Reports

Stellium fully supports comparison charts (synastry, transits, composites) in reports.

### Side-by-Side Tables

When you pass a `Comparison` object to ReportBuilder, sections that show chart data automatically render as side-by-side tables:

- **Planet Positions:** Two tables, one for each chart
- **House Cusps:** Two tables, one for each chart

The tables are labeled with the chart labels you provide to ComparisonBuilder.

### Example: Complete Synastry Report

```python
from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder
from stellium.components import DignityComponent

# Calculate charts with dignities
chart1 = (
    ChartBuilder.from_notable("Albert Einstein")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

chart2 = (
    ChartBuilder.from_notable("Marie Curie")
    .with_aspects()
    .add_component(DignityComponent())
    .calculate()
)

# Create comparison with meaningful labels
comparison = (
    ComparisonBuilder.from_native(chart1, native_label="Albert")
    .with_partner(chart2, partner_label="Marie")
    .calculate()
)

# Build custom synastry report
ReportBuilder().from_chart(comparison) \
    .with_chart_overview() \
    .with_planet_positions(include_house=True) \
    .with_cross_aspects(mode="major", sort_by="orb") \
    .with_house_cusps() \
    .render(format="pdf", file="synastry.pdf")
```

### Example: Transit Report

```python
from datetime import datetime
from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder

# Natal chart
natal = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

# Current transits
transit_chart = (
    ChartBuilder.from_details(
        datetime.now(),
        natal.location.latitude,
        natal.location.longitude,
        natal.location.name,
    )
    .with_aspects()
    .calculate()
)

# Create transit comparison
transits = (
    ComparisonBuilder.from_native(natal, native_label="Natal")
    .with_partner(transit_chart, partner_label="Transits")
    .calculate()
)

# Generate transit report
ReportBuilder().from_chart(transits).preset_transit().render(
    format="pdf",
    file="transits.pdf",
    title="Current Transits for Albert Einstein"
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

### Example 2: Full PDF Report with Everything

```python
from stellium import ChartBuilder, ReportBuilder
from stellium.components import DignityComponent, AspectPatternAnalyzer, MidpointCalculator
from stellium.engines import PlacidusHouses, WholeSignHouses

# Calculate chart with all components and multiple house systems
chart = (
    ChartBuilder.from_notable("Carl Jung")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects()
    .add_component(DignityComponent())
    .add_component(AspectPatternAnalyzer())
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
ReportBuilder().from_chart(chart).preset_full().render(
    format="pdf",
    file="jung_report.pdf",
    chart_svg_path="jung_chart.svg",
    title="Carl Jung — Complete Natal Analysis"
)
```

### Example 3: Comparison Report (Synastry)

```python
from stellium import ChartBuilder, ComparisonBuilder, ReportBuilder

# Two charts
person1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
person2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

# Synastry comparison
synastry = (
    ComparisonBuilder.from_native(person1, native_label="John Lennon")
    .with_partner(person2, partner_label="Yoko Ono")
    .calculate()
)

# Generate biwheel
synastry.draw("lennon_ono_biwheel.svg").with_theme("celestial").save()

# Generate report
ReportBuilder().from_chart(synastry).preset_synastry().render(
    format="pdf",
    file="lennon_ono_synastry.pdf",
    chart_svg_path="lennon_ono_biwheel.svg",
    title="John Lennon & Yoko Ono — Synastry"
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
    ReportBuilder().from_chart(chart).preset_detailed().render(
        format="pdf",
        file=f"{filename}_report.pdf",
        chart_svg_path=f"{filename}_chart.svg",
        title=f"{name} — Natal Chart"
    )

    print(f"Generated report for {name}")
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
| `show` | `bool` | `True` | Display in terminal |
| `chart_svg_path` | `str \| None` | `None` | Chart SVG to embed (PDF/HTML) |
| `title` | `str \| None` | `None` | Report title (PDF) |

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
from stellium.components import DignityComponent, AspectPatternAnalyzer, MidpointCalculator

chart = (
    ChartBuilder.from_native(native)
    .with_aspects()
    .add_component(DignityComponent())        # For .with_dignities()
    .add_component(AspectPatternAnalyzer())   # For .with_aspect_patterns()
    .add_component(MidpointCalculator())      # For .with_midpoints()
    .calculate()
)
```

### PDF fonts look wrong

The Typst renderer uses Cinzel Decorative and Crimson Pro fonts. These are included in `assets/fonts/`. If fonts don't render correctly, ensure the font files are present.

---

Happy charting!
