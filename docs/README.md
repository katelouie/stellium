# Stellium Documentation

Welcome to the Stellium documentation! This directory contains comprehensive guides, references, and galleries for the Stellium astrology library.

## Getting Started

New to Stellium? Start with the [**main README**](../README.md) for installation, quick start, and progressive examples.

## User Guides

| Document | Description |
|----------|-------------|
| [**VISUALIZATION.md**](VISUALIZATION.md) | Complete guide to chart drawing: themes, palettes, presets, tables, and the fluent API |
| [**REPORTS.md**](REPORTS.md) | Report generation guide: sections, presets, PDF output with Typst, comparison reports |
| [**CHART_TYPES.md**](CHART_TYPES.md) | Chart types: natal, synastry, transit, composite, Davison, unknown time |

## Visual Galleries

| Gallery | Description |
|---------|-------------|
| [**THEME_GALLERY.md**](THEME_GALLERY.md) | Visual showcase of all 13+ chart themes (classic, dark, midnight, celestial, neon, etc.) |
| [**PALETTE_GALLERY.md**](PALETTE_GALLERY.md) | Zodiac ring color palettes: rainbow, elemental, scientific colormaps |

## Technical Documentation

The full developer reference lives in [**`development/`**](development/README.md)
— a per-subsystem API/architecture guide written primarily for coding agents
(and handy for contributors). See the complete map in
[**DOCS_INDEX.md**](DOCS_INDEX.md).

| Document | Description |
|----------|-------------|
| [**development/**](development/README.md) | Architecture + API reference (chart building, engines, components, visualization, reports, extending) |
| [**DOCS_INDEX.md**](DOCS_INDEX.md) | Complete index of all documentation |
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | ⚠️ Superseded historical architecture doc (kept for concepts only) |

> Package publishing is maintainer-only and documented in
> [`CONTRIBUTING.md`](../CONTRIBUTING.md#publishing).

## Example Cookbooks

Runnable Python scripts in [`/examples`](../examples/):

| Cookbook | Description |
|----------|-------------|
| [**chart_cookbook.py**](../examples/chart_cookbook.py) | 21 examples: basic charts, themes, palettes, house systems, tables |
| [**report_cookbook.py**](../examples/report_cookbook.py) | 15 examples: terminal reports, PDF generation, synastry reports |
| [**comparison_cookbook.py**](../examples/comparison_cookbook.py) | 13 examples: synastry, transits, bi-wheels, compatibility scoring |

```bash
# Run any cookbook
python examples/chart_cookbook.py
python examples/report_cookbook.py
python examples/comparison_cookbook.py
```

## Developer Reference (`/development/`)

The durable architecture + API reference, written primarily for coding agents
(see each file's "Hello, Claude!" callout) but useful to any contributor.

| Document | Description |
|----------|-------------|
| [README.md](development/README.md) | Reading order and scope of the developer docs |
| [ARCHITECTURE.md](development/ARCHITECTURE.md) | Mental model, layer map, dependency rules, `.calculate()` flow |
| [CHART_BUILDING.md](development/CHART_BUILDING.md) | `Native`/`Notable`, `ChartBuilder`, `CalculatedChart`, config, registries |
| [ENGINES.md](development/ENGINES.md) | Ephemeris, houses, aspects, orbs, dignities, patterns, profections |
| [COMPONENTS_AND_ANALYSIS.md](development/COMPONENTS_AND_ANALYSIS.md) | Components, analysis/DataFrames, IO, caching, utils |
| [VISUALIZATION_INTERNALS.md](development/VISUALIZATION_INTERNALS.md) | SVG pipeline, layers, themes/palettes, dial/vedic/atlas |
| [PRESENTATION_INTERNALS.md](development/PRESENTATION_INTERNALS.md) | `ReportBuilder`, sections, renderers |
| [SUBSYSTEMS.md](development/SUBSYSTEMS.md) | Multi-chart, returns, electional, planner, Chinese/BaZi, CLI |
| [EXTENDING.md](development/EXTENDING.md) | Adding engines/components/analyzers/layers/themes/sections |

### `/scripts/`

| Script | Description |
|--------|-------------|
| [chart_visualization_doc_examples.py](scripts/chart_visualization_doc_examples.py) | Generates all chart images for documentation |

## Quick Links

- [**Main README**](../README.md) - Project overview, installation, quick start
- [**CONTRIBUTING.md**](../CONTRIBUTING.md) - How to contribute
- [**CHANGELOG.md**](../CHANGELOG.md) - Release history
- [**TODO.md**](../TODO.md) - Development roadmap

## Project Structure

```
stellium/
├── README.md                 # Main project documentation
├── CONTRIBUTING.md           # Contribution guidelines
├── CHANGELOG.md              # Release history
├── TODO.md                   # Development roadmap
│
├── docs/                     # This documentation directory
│   ├── VISUALIZATION.md      # Chart drawing guide
│   ├── REPORTS.md            # Report generation guide
│   ├── CHART_TYPES.md        # Chart types guide
│   ├── THEME_GALLERY.md      # Visual theme gallery
│   ├── PALETTE_GALLERY.md    # Zodiac palette gallery
│   ├── ARCHITECTURE.md       # Superseded architecture doc (historical)
│   ├── DOCS_INDEX.md         # Index of all documentation
│   ├── development/          # Developer/agent API & architecture reference
│   ├── scripts/              # Doc generation scripts
│   └── images/               # Documentation images
│
├── examples/                 # Runnable example scripts
│   ├── chart_cookbook.py     # Chart visualization examples
│   ├── report_cookbook.py    # Report generation examples
│   ├── comparison_cookbook.py # Synastry/transit examples
│   ├── charts/               # Generated chart output
│   ├── reports/              # Generated report output
│   └── comparisons/          # Generated comparison output
│
├── src/stellium/             # Core library code
│   ├── core/                 # Core models and builders
│   ├── engines/              # Calculation engines
│   ├── components/           # Optional components
│   ├── visualization/        # Chart rendering
│   └── presentation/         # Report generation
│
└── tests/                    # Test suite
```

---

*For the latest updates, see the main [README.md](../README.md)*
