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

| Document | Description |
|----------|-------------|
| [**ARCHITECTURE.md**](ARCHITECTURE.md) | System architecture, design patterns, and extension points |
| [**PUBLISHING.md**](PUBLISHING.md) | Package publishing guide for maintainers |

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

## Planning & Development

Internal documentation for contributors:

### `/planning/`

| Document | Description |
|----------|-------------|
| [VISION_ARCHITECTURE.md](planning/VISION_ARCHITECTURE.md) | High-level project vision and architectural decisions |
| [LIBRARY_COMPARISON.md](planning/LIBRARY_COMPARISON.md) | Comparison with other Python astrology libraries |
| [NEXT_FEATURES.md](planning/NEXT_FEATURES.md) | Planned features and development roadmap |
| [TRANSITS_SYNASTRY_COMPOSITE_PLAN.md](planning/TRANSITS_SYNASTRY_COMPOSITE_PLAN.md) | Design for comparison chart types |
| [SYNTHESIS_CHARTS_DESIGN.md](planning/SYNTHESIS_CHARTS_DESIGN.md) | Composite and Davison chart implementation |
| [UNKNOWN_TIME_CHARTS_DESIGN.md](planning/UNKNOWN_TIME_CHARTS_DESIGN.md) | Charts without birth time |
| [INTERACTIVE_HTML_REPORTS.md](planning/INTERACTIVE_HTML_REPORTS.md) | Future interactive report plans |

### `/development/`

| Document | Description |
|----------|-------------|
| [ARCHITECTURE_QUICK_REFERENCE.md](development/ARCHITECTURE_QUICK_REFERENCE.md) | Quick reference for the codebase architecture |
| [VIZ_ARCHITECTURE.md](development/VIZ_ARCHITECTURE.md) | Visualization system architecture |
| [SIDEREAL_IMPLEMENTATION.md](development/SIDEREAL_IMPLEMENTATION.md) | Sidereal zodiac implementation notes |
| [DECLINATIONS.md](development/DECLINATIONS.md) | Declination calculations design |
| [VEDIC_DIGNITIES.md](development/VEDIC_DIGNITIES.md) | Vedic dignity system notes |
| [BIWHEEL_USAGE.md](development/BIWHEEL_USAGE.md) | Bi-wheel chart usage guide |

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
│   ├── ARCHITECTURE.md       # System architecture
│   ├── planning/             # Planning documents
│   ├── development/          # Development docs
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
