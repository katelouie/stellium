# 🌟 Stellium

**A modern, extensible Python library for computational astrology**

Built on Swiss Ephemeris for NASA-grade astronomical accuracy, Stellium brings professional astrological calculations to Python with a clean, composable architecture that works for everyone, from quick scripts to production applications.

[![PyPI version](https://badge.fury.io/py/stellium.svg)](https://badge.fury.io/py/stellium)
[![Python Version](https://img.shields.io/pypi/pyversions/stellium.svg)](https://pypi.org/project/stellium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/status-active%20development-brightgreen.svg)]()
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/katelouie/stellium)

---

## ✨ Why Stellium?

### **For Python Developers**

- **Fully typed** with modern type hints for excellent IDE support
- **Protocol-driven architecture** - extend with custom engines, no inheritance required
- **Fluent builder pattern** - chainable, readable, intuitive API
- **Flexible input formats** - accepts datetime strings, city names, or precise coordinates
- **Modular & composable** - mix and match components as needed
- **Production-ready** with comprehensive test coverage

### **For Astrologers**

- **Both tropical and sidereal zodiacs** with 9 ayanamsa systems for Vedic astrology
- **23+ house systems** including Placidus, Whole Sign, Koch, Equal, Regiomontanus, and more
- **Declination calculations** with out-of-bounds planet detection
- **Bi-wheel charts** for synastry, transits, progressions, and composite analysis
- **Sect-aware calculations** with proper day/night chart handling
- **25+ Arabic Parts** with traditional formulas
- **Essential & accidental dignity scoring** for both traditional and modern rulerships
- **Aspect pattern detection** - Grand Trines, T-Squares, Yods, Stelliums, and more
- **Beautiful visualizations** with professional SVG chart rendering and 13 themes
- **Notable births database** for quick exploration and learning

### Visual Chart Example

![Example Round Chart](docs/images/examples/readme_first.svg)
![Example Extended Chart](docs/images/examples/readme_extended_detailed.svg)

### **What Makes Stellium Different**

Unlike other Python astrology libraries, Stellium is designed for **extensibility**:

```python
# Other libraries: rigid, hard-coded calculations
chart = AstrologyLibrary(date, location)  # That's all you can do

# Stellium: composable, configurable, extensible
chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])  # Multiple systems!
    .with_sidereal("lahiri")                                    # Sidereal zodiac option
    .with_aspects(ModernAspectEngine())                         # Swap aspect engines
    .with_orbs(LuminariesOrbEngine())                          # Custom orb rules
    .add_component(ArabicPartsCalculator())                    # Plugin-style components
    .add_component(MidpointCalculator())                       # Stack as many as you want
    .calculate())                                              # Lazy evaluation
```

- **Performance** - Advanced caching system makes repeated calculations fast
- **Flexibility** - Calculate multiple house systems simultaneously
- **Accuracy** - Swiss Ephemeris provides planetary positions accurate to fractions of an arc-second
- **Modern Python** - Takes full advantage of Python 3.11+ features

---

## Installation

```bash
pip install stellium
```

### Requirements

- Python 3.11 or higher
- All dependencies installed automatically (pyswisseph, pytz, geopy, rich, svgwrite)

---

## Quick Start

### Your First Chart (2 Lines of Code)

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").calculate()
chart.draw("einstein.svg").save()
```

![Einstein - Plain](docs/images/examples/readme_einstein.svg)

**That's it!** You now have a beautiful natal chart SVG for Einstein.

The `from_notable()` factory method uses our curated database of famous births. Other notables include: "Carl Jung", "Frida Kahlo", "Marie Curie", and more.

### Beautiful Visualizations, Zero Config

Want to customize your chart? The fluent `.draw()` API makes it effortless:

```python
# Apply a preset for instant results
chart.draw("detailed.svg").preset_detailed().save()

# Choose a theme
chart.draw("midnight.svg").with_theme("midnight").save()

# Full customization
chart.draw("custom.svg") \
    .with_theme("celestial") \
    .with_zodiac_palette("rainbow_celestial") \
    .with_moon_phase(position="bottom-left", show_label=True) \
    .with_chart_info(position="top-left") \
    .save()
```

![Einstein - Celestial](docs/images/examples/readme_einstein_celestial.svg)

**Discover features through autocomplete!** Type `chart.draw().` and your IDE will show you everything available.

📚 **See the [Visualization Guide](docs/VISUALIZATION.md) for complete documentation, theme gallery, and examples.**

### Your Own Chart

```python
from stellium import ChartBuilder

# Quick method: just pass datetime string and location
chart = ChartBuilder.from_details(
    "2000-01-06 12:00",  # ISO format, US format, or European format
    "Seattle, WA"        # City name or (lat, lon) tuple
).calculate()

# Access planetary positions
sun = chart.get_object("Sun")
print(sun)

moon = chart.get_object("Moon")
print(moon)
print(moon.phase)
```

```sh
Sun: 0°0' Libra (180°)
Moon: 0°0' Aries (0°)
Phase: Full (100% illuminated)
```

**Key Features:**

- **Flexible datetime parsing**: ISO 8601, US format, European format, or date-only
- **Automatic geocoding**: City name → coordinates
- **Automatic timezone handling**: Naive datetimes converted to UTC
- **Smart defaults**: Placidus houses, major (Ptolemaic) aspects, tropical zodiac

---

## Progressive Examples

### Level 1: Exploring Chart Data

```python
from stellium import ChartBuilder

# Modern convenience method - accepts datetime strings!
chart = ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA").calculate()

# Get all planets
for planet in chart.get_planets():
    print(f"{planet.name}: {planet.longitude:.2f}° {planet.sign}")

# Get aspects
for aspect in chart.aspects:
    print(f"{aspect.object1.name} {aspect.aspect_name} {aspect.object2.name} (orb: {aspect.orb:.2f}°)")

# Get house cusps
houses = chart.get_houses()  # Returns HouseCusps for default (or first) system
for i, cusp in enumerate(houses.cusps, 1):
    print(f"House {i}: {cusp:.2f}°")
```

### Level 2: Custom House Systems & Aspects

```python
from stellium import ChartBuilder
from stellium.engines import WholeSignHouses, ModernAspectEngine, SimpleOrbEngine

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([WholeSignHouses()])  # Use Whole Sign houses
    .with_aspects(ModernAspectEngine())       # Explicit aspect engine
    .with_orbs(SimpleOrbEngine())             # Simple orb rules
    .calculate())

print(f"House System: {chart.default_house_system}")

# Access house cusps for the specific system
whole_sign_cusps = chart.get_house_cusps("Whole Sign")
print(whole_sign_cusps.get_description(1))  # First House
```

**Available House Systems:**
Placidus (default), Whole Sign, Koch, Equal, Regiomontanus, Campanus, Porphyry, Alcabitius, Equal (MC), Vehlow Equal, Topocentric, Morinus, and 11+ more.

### Level 3: Multiple House Systems

```python
from stellium import ChartBuilder
from stellium.engines import PlacidusHouses, WholeSignHouses, KochHouses

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([
        PlacidusHouses(),
        WholeSignHouses(),
        KochHouses()
    ])
    .calculate())

# Access each system independently
sun = chart.get_object("Sun")
print(f"Sun in Placidus House: {sun.house}")

# House placements are tracked per-system
sun_ws_house = sun.house_placements.get("Whole Sign")
print(f"Sun in Whole Sign House: {sun_ws_house}")

sun_koch_house = sun.house_placements.get("Koch")
print(f"Sun in Koch House: {sun_koch_house}")
```

### Level 4: Arabic Parts & Components

```python
from stellium import ChartBuilder
from stellium.components import ArabicPartsCalculator, MidpointCalculator

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .add_component(ArabicPartsCalculator())
    .add_component(MidpointCalculator())
    .calculate())

# Arabic Parts (automatically sect-aware)
arabic_parts = chart.get_component_result("Arabic Parts")
for part in arabic_parts:
    print(f"{part.name:25} {part.longitude:6.2f}° {part.sign:12} House {part.house}")

# Midpoints
midpoints = chart.get_component_result("Midpoints")
for mp in midpoints[:5]:  # First 5 midpoints
    print(f"{mp.object1.name}/{mp.object2.name} midpoint: {mp.longitude:.2f}°")
```

**Available Components:**

- `ArabicPartsCalculator` - 25+ traditional lots (Part of Fortune, Spirit, Love, etc.)
- `MidpointCalculator` - Direct midpoints for all planet pairs
- `DignityComponent` - Essential dignities (rulership, exaltation, triplicity, etc.)
- `AspectPatternAnalyzer` - Detect Grand Trines, T-Squares, Yods, Stelliums, etc.

### Level 5: Terminal Reports with Rich

```python
from stellium import ChartBuilder, Native, ReportBuilder
from stellium.components import DignityComponent, AspectPatternAnalyzer
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 00), "Seattle, WA")
chart = (ChartBuilder.from_native(native)
    .add_component(DignityComponent())
    .add_component(AspectPatternAnalyzer())
    .calculate())

# Build a comprehensive terminal report
report = (ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()                    # Chart metadata (date, location, zodiac system)
    .with_planet_positions(house_systems="all")  # Positions with ALL house systems
    .with_declinations()                      # Declination table with OOB detection
    .with_house_cusps(systems="all")          # House cusps for all systems
    .with_aspects(mode="major")               # Major aspects table
    .with_aspect_patterns()                   # Grand Trines, T-Squares, Yods, etc.
    .with_dignities(essential="both"))        # Essential dignities (traditional + modern)

report.render(format="rich_table")  # Beautiful terminal output

# Export to file
report.render(format="plain_table", file="my_chart.txt")
report.render(format="pdf", file="my_chart.pdf")  # PDF with Typst
```

### Level 6: Advanced - Bi-Wheel Charts

```python
from stellium import ComparisonBuilder

# Synastry chart (relationship analysis)
synastry = ComparisonBuilder.synastry(
    ("1994-01-06 11:47", "Palo Alto, CA", "Kate"),
    ("1995-06-15 14:30", "Seattle, WA", "Alex")
).calculate()

# Draw bi-wheel with both charts
synastry.draw("synastry_biwheel.svg") \
    .preset_detailed() \
    .save()

# Access inner and outer charts separately
inner_chart = synastry.inner_chart
outer_chart = synastry.outer_chart

# Get aspects between the two charts
interaspects = synastry.interaspects
for aspect in interaspects[:10]:
    print(f"{aspect.object1.name} ({inner_chart.name}) "
          f"{aspect.aspect_name} "
          f"{aspect.object2.name} ({outer_chart.name})")
```

**Comparison Chart Types:**

- **Synastry**: Relationship compatibility and dynamics
- **Transit**: Current planetary influences on natal chart
- **Progression**: Secondary progressions for timing
- **Composite**: Relationship midpoint chart (synthesis)
- **Davison**: Relationship chart with actual location

---

## Command-Line Interface

Stellium includes a CLI for quick chart generation:

```bash
# Generate a chart from the notable database
stellium chart notable "Albert Einstein" --output einstein.svg

# Manage ephemeris data
stellium ephemeris download --years 1000-3000

# Clear calculation cache
stellium cache clear
```

See `stellium --help` for full CLI documentation.

---

## 🔍 Feature Highlights

### Zodiac Systems

- **Tropical Zodiac** (Western astrology) - default
- **Sidereal Zodiac** (Vedic/Hindu astrology) with 9 ayanamsa systems:
  - Lahiri (default for sidereal)
  - Fagan-Bradley
  - Raman
  - Krishnamurti
  - Yukteshwar
  - J.N. Bhasin
  - True Chitrapaksha
  - True Revati
  - De Luce

```python
# Tropical (default)
chart = ChartBuilder.from_native(native).calculate()

# Sidereal with Lahiri ayanamsa
chart = ChartBuilder.from_native(native).with_sidereal("lahiri").calculate()

# Sidereal with custom ayanamsa
chart = ChartBuilder.from_native(native).with_sidereal("fagan_bradley").calculate()
```

### Celestial Objects

Calculate positions for 50+ celestial objects:

- **Planets**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- **Asteroids**: Chiron, Ceres, Pallas, Juno, Vesta
- **Lunar Nodes**: North Node, South Node, True Node, Mean Node
- **Lunar Apogee**: Lilith (Mean, True, Osculating, Interpolated)
- **Chart Points**: Ascendant, Midheaven, Descendant, IC, Vertex, East Point

### Coordinate Systems

- **Ecliptic Coordinates**: Longitude, latitude (distance from ecliptic)
- **Equatorial Coordinates**: Right ascension, declination (distance from celestial equator)
- **Out-of-Bounds Detection**: Automatically identifies planets with extreme declinations (>23°27')

```python
sun = chart.get_object("Sun")
print(f"Ecliptic: {sun.longitude:.2f}° longitude, {sun.latitude:.2f}° latitude")
print(f"Equatorial: {sun.right_ascension:.2f}° RA, {sun.declination:.2f}° declination")
if sun.is_out_of_bounds:
    print(f"⚠ Sun is out of bounds!")
```

### Aspect Calculations

- **Major Aspects** (Ptolemaic): Conjunction (0°), Opposition (180°), Square (90°), Trine (120°), Sextile (60°)
- **Minor Aspects**: Semi-sextile (30°), Semi-square (45°), Sesquiquadrate (135°), Quincunx (150°)
- **Harmonic Aspects**: Quintile (72°), Bi-quintile (144°), Septile (51.43°), Novile (40°), and more
- **Configurable Orbs**: Simple, Luminaries-specific, or Complex (aspect-and-planet-pair-specific) orb engines

### Dignities

- **Essential Dignities**: Ruler, Exaltation, Triplicity (by sect), Bound, Decan, Detriment, Fall
- **Accidental Dignities**: House placement, angular/succedent/cadent, joy
- **Both Traditional & Modern** rulerships supported

### Comparison Charts (Bi-Wheels)

Create relationship, timing, and synthesis charts:

```python
from stellium import ComparisonBuilder

# Synastry (relationship analysis)
synastry = ComparisonBuilder.synastry(
    ("1994-01-06 11:47", "Palo Alto, CA", "Person A"),
    ("1995-06-15 14:30", "Seattle, WA", "Person B")
).calculate()
synastry.draw("synastry.svg").save()

# Transits (timing analysis)
transits = ComparisonBuilder.transit(
    natal_data=("1994-01-06 11:47", "Palo Alto, CA"),
    transit_data=("2025-11-26 12:00", "Palo Alto, CA")
).calculate()

# Composite (relationship midpoint chart)
composite = ComparisonBuilder.composite(
    ("1994-01-06 11:47", "Palo Alto, CA"),
    ("1995-06-15 14:30", "Seattle, WA")
).calculate()

# Davison (relationship midpoint chart with actual location)
davison = ComparisonBuilder.davison(
    ("1994-01-06 11:47", "Palo Alto, CA"),
    ("1995-06-15 14:30", "Seattle, WA")
).calculate()
```

**Comparison Types:**
- **Synastry**: Two natal charts overlaid (bi-wheel)
- **Transit**: Natal chart + current/future planets
- **Progression**: Natal chart + progressed positions
- **Composite**: Midpoint chart (mathematical average)
- **Davison**: Midpoint chart with actual geographic location

### Unknown Birth Time Charts

Handle charts when birth time is unknown:

```python
# Create chart with unknown time (defaults to noon, skips houses/angles)
chart = ChartBuilder.from_details(
    "1994-01-06",  # Date only
    "Palo Alto, CA",
    time_unknown=True
).calculate()

# Visualize with Moon's daily arc
chart.draw("unknown_time.svg").save()  # Shows Moon's possible range
```

### Data Export

```python
# Export to dictionary for JSON serialization
data = chart.to_dict()

# Includes:
# - All planetary positions with coordinates
# - House cusps for all calculated systems
# - All aspects with orbs
# - Component results (Arabic Parts, midpoints, etc.)
# - Chart metadata (date, location, timezone)
```

### Performance

```python
from stellium.utils.cache import enable_cache, get_cache_stats

enable_cache(max_age_seconds=604800)  # 1 week cache

# First calculation: ~200ms
chart1 = ChartBuilder.from_native(native).calculate()

# Subsequent calculations: ~10ms (20x faster!)
chart2 = ChartBuilder.from_native(native).calculate()

stats = get_cache_stats()
print(f"Cache hits: {stats['hits']}, misses: {stats['misses']}")
```

---

## 📖 Documentation & Learning

### Example Cookbooks

The `/examples` directory contains comprehensive, runnable cookbooks:

| Cookbook | Description |
|----------|-------------|
| **[chart_cookbook.py](examples/chart_cookbook.py)** | 21 examples: themes, palettes, house systems, tables, and more |
| **[report_cookbook.py](examples/report_cookbook.py)** | 15 examples: terminal reports, PDF generation, batch processing |
| **[comparison_cookbook.py](examples/comparison_cookbook.py)** | 13 examples: synastry, transits, bi-wheels, compatibility |

```bash
# Run any cookbook
python examples/chart_cookbook.py
python examples/report_cookbook.py
python examples/comparison_cookbook.py
```

### User Guides

| Guide | Description |
|-------|-------------|
| **[VISUALIZATION.md](docs/VISUALIZATION.md)** | Complete chart drawing guide with fluent API reference |
| **[REPORTS.md](docs/REPORTS.md)** | Report generation guide: sections, presets, PDF output |
| **[CHART_TYPES.md](docs/CHART_TYPES.md)** | Chart types: natal, synastry, transit, composite, Davison |
| **[USER_GUIDE.md](docs/USER_GUIDE.md)** | Getting started guide for new users |

### Visual Galleries

| Gallery | Description |
|---------|-------------|
| **[THEME_GALLERY.md](docs/THEME_GALLERY.md)** | Visual showcase of all 13+ chart themes |
| **[PALETTE_GALLERY.md](docs/PALETTE_GALLERY.md)** | Zodiac ring color palettes with previews |

### Technical Documentation

| Document | Description |
|----------|-------------|
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture and design patterns |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | How to contribute (development setup) |
| **[CHANGELOG.md](CHANGELOG.md)** | Release history and version notes |
| **[PUBLISHING.md](docs/PUBLISHING.md)** | Package publishing guide |

### Quick Start

```bash
# Clone and install
git clone https://github.com/katelouie/stellium.git
cd stellium
pip install -e .

# Run example cookbooks
python examples/chart_cookbook.py      # Generate chart SVGs
python examples/report_cookbook.py     # Generate PDF reports
python examples/comparison_cookbook.py # Generate synastry charts
```

## Architecture Philosophy

Stellium is built on three core principles:

### 1. **Protocols over Inheritance**

Extend functionality by implementing protocols, not subclassing:

```python
from stellium.core.protocols import ChartComponent
from typing import Protocol

class MyCustomComponent:
    """Add custom calculations without inheritance."""

    @property
    def component_name(self) -> str:
        return "My Feature"

    def calculate(self, chart_data, config):
        # Your calculations here
        return results

# Use it:
chart = ChartBuilder.from_native(native).add_component(MyCustomComponent()).calculate()
```

### 2. **Composability**

Mix and match components freely:

```python
# Every piece is optional and interchangeable
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])  # Multiple systems
    .with_aspects(ModernAspectEngine())      # Choose aspect engine
    .with_orbs(LuminariesOrbEngine())        # Choose orb calculator
    .add_component(ArabicPartsCalculator())  # Add components
    .add_component(MidpointCalculator())     # Stack them up
    .calculate())
```

### 3. **Immutability**

All calculation results are immutable dataclasses:

```python
# Results are frozen - safe to cache and share
sun = chart.get_object("Sun")
sun.longitude = 100  # ❌ Error: frozen dataclass

# This makes caching safe and reliable
cached_chart = chart  # Safe to reuse
```

**Benefits:**

- Thread-safe calculations
- Reliable caching
- No accidental mutations
- Easy to reason about

## Testing

Stellium has comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test categories
pytest tests/test_chart_builder.py
pytest tests/test_integration.py
```

---

## 🗺️ Roadmap

See [TODO.md](TODO.md) for the full development roadmap.

### Recently Added

- ✅ **Sidereal Zodiac Support** - 9 ayanamsa systems (Lahiri, Fagan-Bradley, Raman, etc.)
- ✅ **Declination Calculations** - Out-of-bounds detection, equatorial coordinates
- ✅ **Bi-Wheel Charts** - Synastry, transits, progressions, composite charts
- ✅ **Enhanced Reports** - Dignities, aspect patterns, house cusps, declinations
- ✅ **Unknown Time Charts** - Moon arc visualization for charts without birth time

---

## Contributing

We welcome contributions from both Python developers and astrologers! Whether you want to:

- Add new calculation engines
- Improve documentation
- Fix bugs
- Add new features
- Share examples

Please see **[CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

**Quick Start for Contributors:**

```bash
git clone https://github.com/katelouie/stellium.git
cd stellium
pip install -e ".[dev]"  # Install with dev dependencies
pre-commit install       # Set up pre-commit hooks
pytest                   # Run tests
```

---

## License

Stellium is released under the **MIT License**. See [LICENSE](LICENSE) for details.

**Note on Swiss Ephemeris**: This library uses the Swiss Ephemeris, which has its own licensing terms for commercial use. See the [Swiss Ephemeris website](https://www.astro.com/swisseph/) for details.

---

## Acknowledgments

- **[Swiss Ephemeris](https://www.astro.com/swisseph/)** - Astronomical calculations of exceptional accuracy
- **[Astro.com](https://www.astro.com/)** - Ephemeris data and astrological resources
- **[PySwissEph](https://astrorigin.com/pyswisseph/)** - Python bindings for Swiss Ephemeris

---

## Community & Support

- **Issues**: [GitHub Issues](https://github.com/katelouie/stellium/issues)
- **Discussions**: [GitHub Discussions](https://github.com/katelouie/stellium/discussions)
- **Email**: <katehlouie@gmail.com>

---

**Built with precision, designed for everyone** ✨

Whether you're building a professional astrology application, researching astrological patterns, or learning computational astrology: Stellium provides the tools you need with a modern, extensible architecture.

*Star the repo if you find it useful!* ⭐
