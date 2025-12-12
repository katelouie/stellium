# Stellium Examples

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
   ```

3. Check the output directories for generated files:
   - `examples/charts/` - SVG chart images
   - `examples/reports/` - PDF/TXT reports
   - `examples/comparisons/` - Comparison charts and reports
   - `examples/progressions/` - Progression bi-wheels
   - `examples/arc_directions/` - Arc direction charts

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
from stellium import ReportBuilder

# Terminal output
ReportBuilder().from_chart(chart).preset_standard().render()

# PDF output
ReportBuilder().from_chart(chart).preset_detailed().render(
    format="pdf",
    file="report.pdf",
    chart_svg_path="chart.svg"
)
```

### Create a Synastry Chart

```python
from stellium import MultiChartBuilder

chart1 = ChartBuilder.from_notable("John Lennon").with_aspects().calculate()
chart2 = ChartBuilder.from_notable("Yoko Ono").with_aspects().calculate()

synastry = MultiChartBuilder.synastry(chart1, chart2, label1="John", label2="Yoko") \
    .with_cross_aspects() \
    .calculate()

synastry.draw("synastry.svg").save()
```
