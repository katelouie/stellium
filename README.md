# 🌟 Starlight

**A modern, extensible Python library for computational astrology**

Built on Swiss Ephemeris for NASA-grade astronomical accuracy, Starlight brings professional astrological calculations to Python with a clean, composable architecture that works for everyone, from quick scripts to production applications.

[![PyPI version](https://badge.fury.io/py/starlight-astro.svg)](https://badge.fury.io/py/starlight-astro)
[![Python Version](https://img.shields.io/pypi/pyversions/starlight-astro.svg)](https://pypi.org/project/starlight-astro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Active Development](https://img.shields.io/badge/status-active%20development-brightgreen.svg)]()
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/katelouie/starlight)

---

## ✨ Why Starlight?

### **For Python Developers**

- **Fully typed** with modern type hints for excellent IDE support
- **Protocol-driven architecture** - extend with custom engines, no inheritance required
- **Fluent builder pattern** - chainable, readable, intuitive API
- **Modular & composable** - mix and match components as needed
- **Production-ready** with comprehensive test coverage

### **For Astrologers**

- **23+ house systems** including Placidus, Whole Sign, Koch, Equal, Regiomontanus, and more
- **Sect-aware calculations** with proper day/night chart handling
- **25+ Arabic Parts** with traditional formulas
- **Essential & accidental dignity scoring** for both traditional and modern rulerships
- **Beautiful visualizations** with professional SVG chart rendering
- **Notable births and events database** for quick exploration and learning

### Visual Chart Example

![Example Round Chart](docs/images/examples/readme_first.svg)
![Example Extended Chart](docs/images/examples/readme_extended_detailed.svg)

### **What Makes Starlight Different**

Unlike other Python astrology libraries, Starlight is designed for **extensibility**:

```python
# Other libraries: rigid, hard-coded calculations
chart = AstrologyLibrary(date, location)  # That's all you can do

# Starlight: composable, configurable, extensible
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])  # Multiple systems!
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
pip install starlight-astro
```

### Requirements

- Python 3.11 or higher
- All dependencies installed automatically (pyswisseph, pytz, geopy, rich, svgwrite)

---

## Quick Start

### Your First Chart (2 Lines of Code)

```python
from starlight import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
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
from starlight import ChartBuilder, Native

# Create a Native (birth data container)
native = Native(
    datetime_input="2000-01-06 12:00",  # Naive or timezone-aware
    location_input="Seattle, WA" # City name or (lat, lon)
)

# Build and calculate the chart
chart = ChartBuilder.from_native(native).calculate()

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

- Automatic geocoding (city name → coordinates)
- Automatic timezone handling (naive datetimes converted to UTC)
- Default house system is Placidus, default aspects are major (Ptolemaic)

---

## Progressive Examples

### Level 1: Exploring Chart Data

```python
from starlight import ChartBuilder, Native
from datetime import datetime

chart = ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA").calculate()

# Get all planets
for planet in chart.get_planets():
    print(planet)

# Get aspects
for aspect in chart.aspects:
    print(aspect)

# Get house cusps
houses = chart.get_houses()  # Returns HouseCusps for default (or first) system
print(houses)
```

### Level 2: Custom House Systems & Aspects

```python
from starlight import ChartBuilder, Native
from starlight.engines import WholeSignHouses, ModernAspectEngine, SimpleOrbEngine
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 00), "Seattle, WA")

chart = (ChartBuilder.from_native(native)
    .with_house_systems([WholeSignHouses()])  # Use Whole Sign houses
    .with_aspects(ModernAspectEngine())       # Explicit aspect engine
    .with_orbs(SimpleOrbEngine())             # Simple orb rules
    .calculate())

print(f"House System: {chart.default_house_system}")

# Access house cusps for the specific system
whole_sign_cusps = chart.get_house_cusps("Whole Sign")
print(whole_sign_cusps.get_description(1)) # First House
```

**Available House Systems:**
Placidus (default), Whole Sign, Koch, Equal, Regiomontanus, Campanus, Porphyry, Alcabitius, Equal (MC), Vehlow Equal, Topocentric, Morinus, and 11+ more.

### Level 3: Multiple House Systems

```python
from starlight import ChartBuilder
from starlight.engines import PlacidusHouses, WholeSignHouses, KochHouses

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
from starlight import ChartBuilder, Native
from starlight.components import ArabicPartsCalculator, MidpointCalculator
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 00), "Seattle, WA")

chart = (ChartBuilder.from_native(native)
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
- `AccidentalDignityComponent` - House-based accidental dignities

### Level 5: Terminal Reports with Rich

```python
from starlight import ChartBuilder, Native, ReportBuilder
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 00), "Seattle, WA")
chart = ChartBuilder.from_native(native).calculate()

# Build a beautiful terminal report
report = (ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()           # Chart metadata (date, location, etc.)
    .with_planet_positions()         # Planetary positions table
    .with_aspects(mode="major"))     # Major aspects table

report.render(format="rich_table") # Rich terminal formatting

report.render(format="plain_table", file="my_chart.txt") # Export to file
```

### Level 6: Advanced - Custom Visualization

```python
from starlight import ChartBuilder, Native, ChartRenderer
from starlight.visualization.layers import (
    ZodiacLayer, HouseCuspLayer, PlanetLayer,
    AspectLayer, AngleLayer
)
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 00), "Seattle, WA")
chart = ChartBuilder.from_native(native).calculate()

# Manual layer assembly for custom charts
rotation = chart.get_object("ASC").longitude
renderer = ChartRenderer(size=800, rotation=rotation)
dwg = renderer.create_svg_drawing("custom_chart.svg")

# Add layers in order (bottom to top)
layers = [
    ZodiacLayer(),
    HouseCuspLayer(house_system_name="Placidus"),
    AngleLayer(),
    AspectLayer(),
    PlanetLayer()
]

for layer in layers:
    layer.render(renderer, dwg, chart)

dwg.save()
```

**Use Cases for Custom Layers:**

- Synastry (bi-wheel) charts
- Transit overlays
- Custom styling and colors
- Educational diagrams
- Research visualizations

---

## Command-Line Interface

Starlight includes a CLI for quick chart generation:

```bash
# Generate a chart from the notable database
starlight chart notable "Albert Einstein" --output einstein.svg

# Manage ephemeris data
starlight ephemeris download --years 1000-3000

# Clear calculation cache
starlight cache clear
```

See `starlight --help` for full CLI documentation.

---

## 🔍 Feature Highlights

### Celestial Objects

Calculate positions for 50+ celestial objects:

- **Planets**: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- **Asteroids**: Chiron, Ceres, Pallas, Juno, Vesta
- **Lunar Nodes**: North Node, South Node, True Node, Mean Node
- **Lunar Apogee**: Lilith (Mean, True, Osculating, Interpolated)
- **Chart Points**: Ascendant, Midheaven, Descendant, IC, Vertex, East Point

### Aspect Calculations

- **Major Aspects** (Ptolemaic): Conjunction (0°), Opposition (180°), Square (90°), Trine (120°), Sextile (60°)
- **Minor Aspects**: Semi-sextile (30°), Semi-square (45°), Sesquiquadrate (135°), Quincunx (150°)
- **Harmonic Aspects**: Quintile (72°), Bi-quintile (144°), Septile (51.43°), Novile (40°), and more
- **Configurable Orbs**: Simple, Luminaries-specific, or Complex (aspect-and-planet-pair-specific) orb engines

### Dignities

- **Essential Dignities**: Ruler, Exaltation, Triplicity (by sect), Bound, Decan, Detriment, Fall
- **Accidental Dignities**: House placement, angular/succedent/cadent, joy
- **Both Traditional & Modern** rulerships supported

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
from starlight.utils.cache import enable_cache, get_cache_stats

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

### Examples

The `/examples` directory contains runnable code:

- `viz_examples.py` - Chart visualization techniques
- `report_examples.py` - Terminal report generation
- `chart_examples/` - Gallery of generated charts

### Additional Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute (development guide)
- **[CHANGELOG.md](CHANGELOG.md)** - Release history

### Interactive Learning

```bash
# Install with examples
git clone https://github.com/katelouie/starlight.git
cd starlight
pip install -e .

# Run examples
python examples/viz_examples.py
python examples/report_examples.py
```

## Architecture Philosophy

Starlight is built on three core principles:

### 1. **Protocols over Inheritance**

Extend functionality by implementing protocols, not subclassing:

```python
from starlight.core.protocols import ChartComponent
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

Starlight has comprehensive test coverage:

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

### Coming Soon

- **Synastry Charts**: Bi-wheel visualizations and inter-chart aspects
- **Transit Calculations**: Current planetary positions against natal chart
- **Progressions**: Secondary progressions and solar arc directions
- **Additional Chart Types**: Returns, composites, and harmonic charts
- **Sidereal Support**: Sidereal zodiac calculations
- **Enhanced Visualizations**: More chart styles and customization options

See [TODO.md](TODO.md) for the full development roadmap.

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
git clone https://github.com/katelouie/starlight.git
cd starlight
pip install -e ".[dev]"  # Install with dev dependencies
pre-commit install       # Set up pre-commit hooks
pytest                   # Run tests
```

---

## License

Starlight is released under the **MIT License**. See [LICENSE](LICENSE) for details.

**Note on Swiss Ephemeris**: This library uses the Swiss Ephemeris, which has its own licensing terms for commercial use. See the [Swiss Ephemeris website](https://www.astro.com/swisseph/) for details.

---

## Acknowledgments

- **[Swiss Ephemeris](https://www.astro.com/swisseph/)** - Astronomical calculations of exceptional accuracy
- **[Astro.com](https://www.astro.com/)** - Ephemeris data and astrological resources
- **[PySwissEph](https://astrorigin.com/pyswisseph/)** - Python bindings for Swiss Ephemeris

---

## Community & Support

- **Issues**: [GitHub Issues](https://github.com/katelouie/starlight/issues)
- **Discussions**: [GitHub Discussions](https://github.com/katelouie/starlight/discussions)
- **Email**: <katehlouie@gmail.com>

---

**Built with precision, designed for everyone** ✨

Whether you're building a professional astrology application, researching astrological patterns, or learning computational astrology—Starlight provides the tools you need with a modern, extensible architecture.

*Star the repo if you find it useful!* ⭐
