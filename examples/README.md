# Stellium Examples

> ## 📖 Read these on the documentation site instead
>
> **[stellium.readthedocs.io → Cookbooks](https://stellium.readthedocs.io/en/latest/cookbooks/index.html)**
>
> Every recipe below is rendered there with **its real output** — the printed tables and
> the charts it draws — captured by *running* the code at build time. Same recipes, but
> you can see what they produce without running anything.
>
> This directory is the source those pages are generated from.

This directory contains runnable example scripts demonstrating Stellium's capabilities.

## Cookbooks

Each cookbook is a self-contained Python script with numbered examples you can run individually or all at once.

### Chart Visualization (`chart_cookbook.py`)

Learn how to create beautiful natal chart visualizations:

- Basic charts and sizing
- Presets (minimal, standard, detailed)
- Themes (classic, dark, midnight, celestial, neon, etc.)
- Scientific colormap themes (viridis, plasma, inferno, etc.)
- Zodiac palettes (rainbow, elemental, cardinality)
- Info corners (chart info, moon phase, aspect counts)
- Multiple house systems
- Tables (positions, aspectarian)
- Headers
- Full-featured professional charts

**Output directory:** `examples/charts/`

```bash
python examples/chart_cookbook.py
```

### Reports (`report_cookbook.py`)

Learn how to generate reports in various formats:

- Terminal reports (Rich formatting)
- PDF reports with Typst
- Reports with embedded chart wheels
- Custom section selection
- Synastry and transit reports
- Plain text output
- Batch report generation

**Output directory:** `examples/reports/`

```bash
python examples/report_cookbook.py
```

### Comparison Charts (`comparison_cookbook.py`)

Learn how to create synastry, transit, and bi-wheel charts:

- Basic synastry between two people
- Styled synastry with themes
- Synastry with position tables
- House overlays analysis
- Compatibility scoring
- Transit charts
- Custom aspect configurations
- PDF reports for comparisons
- Batch synastry generation

**Output directory:** `examples/comparisons/`

```bash
python examples/comparison_cookbook.py
```

### Progressions (`progressions_cookbook.py`)

Learn secondary progressions for internal development timing:

- Simple progressions by age
- Progressions to target dates
- Progressed Sun/Moon motion
- Angle progression methods (quotidian, solar arc, naibod)
- Progressed-to-natal aspects

**Output directory:** `examples/progressions/`

```bash
python examples/progressions_cookbook.py
```

### Arc Directions (`arc_directions_cookbook.py`)

Explore arc direction techniques:

- Solar arc directions
- Naibod arc directions
- Lunar arc directions
- Sect-based arc (day/night)
- Chart ruler arc
- Planetary arcs (Mars, Venus, Jupiter, Saturn)

**Output directory:** `examples/arc_directions/`

```bash
python examples/arc_directions_cookbook.py
```

### Electional Astrology (`electional_cookbook.py`)

Find auspicious times matching astrological criteria:

- Basic searches with lambda conditions
- Helper predicates (is_waxing, not_voc, on_angle, etc.)
- Moon conditions (phase, VOC, sign, aspects)
- Planetary conditions (retrograde, dignity, combust)
- Aspect requirements and avoidance
- House and angle placements
- Boolean composition (AND, OR, NOT)
- Complex nested queries
- Practical elections (business, relationships, Mercury/Mars/Jupiter matters)
- Advanced usage (generators, counting, export)

**Output directory:** `examples/elections/`

```bash
python examples/electional_cookbook.py
```

### File I/O (`io_cookbook.py`)

Learn how to import birth data from various file formats:

- CSV parsing with auto-detection
- Custom column name mapping
- Split first/last name columns
- Date format hints (US, European, ISO)
- 12-hour time (AM/PM) support
- Combined datetime columns
- Separate date/time components
- Location names with coordinates
- Error handling options
- pandas DataFrame parsing
- Excel file import
- AAF (astro.com) file import
- Batch chart generation
- Round-trip export

**Output directory:** `examples/io_examples/`

```bash
python examples/io_cookbook.py
```

### Data Analysis (`analysis_cookbook.ipynb`)

Research tools for large-scale astrological data analysis (Jupyter notebook):

- Batch chart calculation
- DataFrame export and manipulation
- Research queries (filter by sign, house, aspect, pattern)
- Statistical aggregation
- CSV/JSON/Parquet export

**Requirements:** `pip install stellium[analysis]`

```bash
jupyter notebook examples/analysis_cookbook.ipynb
```

## Running Examples

1. Activate the Python environment:
   ```bash
   source ~/.zshrc && pyenv activate starlight
   ```

2. Run any cookbook:
   ```bash
   python examples/chart_cookbook.py
   python examples/report_cookbook.py
   python examples/comparison_cookbook.py
   python examples/progressions_cookbook.py
   python examples/arc_directions_cookbook.py
   python examples/electional_cookbook.py
   python examples/io_cookbook.py
   ```

3. Check the output directories for generated files:
   - `examples/charts/` - SVG chart images
   - `examples/reports/` - PDF/TXT reports
   - `examples/comparisons/` - Comparison charts and reports
   - `examples/progressions/` - Progression bi-wheels
   - `examples/arc_directions/` - Arc direction charts
   - `examples/elections/` - Election search results
   - `examples/io_examples/` - Sample CSV/AAF files and batch charts

## Customizing Examples

Each cookbook has a `main()` function at the bottom where you can comment/uncomment specific examples:

```python
def main():
    # Uncomment the examples you want to run:

    # --- Part 1: Basic Charts ---
    example_1_simplest_chart()
    example_2_with_size()
    # example_3_presets()  # Commented out
    ...
```

## Documentation

For comprehensive documentation, see:

- [docs/VISUALIZATION.md](../docs/VISUALIZATION.md) - Chart visualization guide
- [docs/REPORTS.md](../docs/REPORTS.md) - Report generation guide
- [docs/CHART_TYPES.md](../docs/CHART_TYPES.md) - Chart types and comparisons
- [docs/THEME_GALLERY.md](../docs/THEME_GALLERY.md) - Visual theme gallery
- [docs/PALETTE_GALLERY.md](../docs/PALETTE_GALLERY.md) - Zodiac palette gallery

## Quick Reference

### Calculate a Chart

```python
from stellium import ChartBuilder

# From a notable person
chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

# From birth details
chart = ChartBuilder.from_details(
    "1994-01-06 11:47",
    "Palo Alto, CA",
    name="Kate"
).with_aspects().calculate()
```
### Draw a Chart

```python
# Simple
chart.draw("chart.svg").save()

# With styling
chart.draw("chart.svg") \
    .with_theme("celestial") \
    .with_zodiac_palette("rainbow_celestial") \
    .with_moon_phase() \
    .with_chart_info() \
    .save()
```

### Generate a Report

```python
from stellium import ChartBuilder, ReportBuilder

chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

# Terminal output
ReportBuilder().from_chart(chart).preset_standard().render()

# PDF output
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="report.pdf",
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

### Create a Synastry Chart

```python
from stellium import ChartBuilder, MultiChartBuilder

chart1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
chart2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

synastry = MultiChartBuilder.synastry(chart1, chart2, label1="John", label2="Yoko") \
    .with_cross_aspects() \
    .calculate()

synastry.draw("synastry.svg").save()
```
