# Claude Development Instructions for Stellium

**Stellium** is a modern, extensible Python library for computational astrology built on Swiss Ephemeris for NASA-grade astronomical accuracy.

---

## Table of Contents

- [Environment Setup Requirements](#environment-setup-requirements)
- [Codebase Architecture](#codebase-architecture)
- [Directory Structure](#directory-structure)
- [Core Principles](#core-principles)
- [Development Workflows](#development-workflows)
- [Testing Conventions](#testing-conventions)
- [Code Style & Conventions](#code-style--conventions)
- [Common Tasks](#common-tasks)
- [Important Patterns](#important-patterns)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Quick Reference](#quick-reference)

---

## Environment Setup Requirements

**CRITICAL: Always run these commands before executing any Python code that uses Swiss Ephemeris:**

```bash
source ~/.zshrc
pyenv activate starlight
```

### Why This Matters

The Swiss Ephemeris dependency (`pyswisseph`) requires specific environment setup:
- The `starlight` pyenv environment contains the correct Python version (3.11+) and dependencies
- Swiss Ephemeris data files are configured for this specific environment in `data/swisseph/ephe/`
- Without proper activation, imports will fail or calculations will be incorrect

### Required Environment Commands

**Before running Python files:**
```bash
source ~/.zshrc && pyenv activate starlight && python [file]
```

**Before running tests:**
```bash
source ~/.zshrc && pyenv activate starlight && pytest
source ~/.zshrc && pyenv activate starlight && python tests/test_chart_generation.py
source ~/.zshrc && pyenv activate starlight && python tests/moon_phase_tester.py
```

**Before running examples:**
```bash
source ~/.zshrc && pyenv activate starlight && python examples/usage.py
source ~/.zshrc && pyenv activate starlight && python examples/viz_examples.py
```

### Development Setup

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks (automatic code formatting)
pre-commit install

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

---

## Codebase Architecture

Stellium is built on three foundational principles that enable extensibility, maintainability, and performance:

### 1. **Protocols over Inheritance**
- Uses structural typing (Protocols) instead of class hierarchies
- Enables "duck typing" with type safety
- Components implement interfaces without inheritance
- Easy to test and compose

### 2. **Composability**
- All components work independently and can be freely combined
- Builder pattern for fluent configuration
- Lazy evaluation (configure first, calculate when ready)
- Mix-and-match engines and components

### 3. **Immutability**
- All data models are frozen dataclasses (cannot be modified after creation)
- Thread-safe by design
- Safe to cache and share
- Predictable behavior

### Data Flow

```
User Request
    ↓
ChartBuilder (API layer) - Fluent interface for configuration
    ↓
Engines (calculation layer)
    ├── EphemerisEngine → CelestialPosition[]  (planetary positions)
    ├── HouseSystemEngine → HouseCusps          (house systems)
    ├── AspectEngine → Aspect[]                 (aspects)
    └── OrbEngine → orb calculations
    ↓
Components (optional calculations)
    ├── ArabicPartsCalculator → Arabic Parts
    ├── MidpointCalculator → Midpoints
    ├── DignityComponent → Essential/Accidental Dignities
    └── PatternAnalysisEngine → Aspect Patterns
    ↓
CalculatedChart (immutable result)
    ↓
Presentation/Visualization/Export
    ├── ReportBuilder → Terminal reports (Rich)
    ├── ChartRenderer → SVG charts
    └── to_dict() → JSON export
```

---

## Directory Structure

```
/home/user/stellium/
├── src/stellium/              # Main package source code
│   ├── __init__.py            # Public API exports
│   ├── core/                  # Core abstractions (NEVER import from engines here)
│   │   ├── models.py         # Immutable data classes (CelestialPosition, Aspect, etc.)
│   │   ├── protocols.py      # Interface definitions (Protocol classes)
│   │   ├── builder.py        # ChartBuilder (main API entry point)
│   │   ├── native.py         # Native, Notable (birth data containers)
│   │   ├── config.py         # CalculationConfig
│   │   └── registry.py       # CELESTIAL_REGISTRY, ASPECT_REGISTRY
│   │
│   ├── engines/               # Calculation engines
│   │   ├── ephemeris.py      # SwissEphemerisEngine (planet positions)
│   │   ├── houses.py         # House systems (Placidus, Whole Sign, Koch, etc.)
│   │   ├── aspects.py        # Aspect engines (Modern, Traditional, Harmonic)
│   │   ├── orbs.py           # Orb calculation engines
│   │   ├── dignities.py      # Essential & Accidental dignity engines
│   │   └── patterns.py       # Aspect pattern detection
│   │
│   ├── components/            # Optional calculation components
│   │   ├── arabic_parts.py   # ArabicPartsCalculator (25+ lots)
│   │   ├── midpoints.py      # MidpointCalculator
│   │   ├── dignity.py        # DignityComponent
│   │   └── patterns.py       # PatternAnalysisEngine
│   │
│   ├── presentation/          # Terminal reports and formatting
│   │   ├── builder.py        # ReportBuilder
│   │   ├── sections.py       # Report sections
│   │   └── renderers.py      # Rich/plain text renderers
│   │
│   ├── visualization/         # SVG chart rendering
│   │   ├── core.py           # ChartRenderer
│   │   ├── builder.py        # ChartDrawBuilder (fluent API)
│   │   ├── composer.py       # ChartComposer (orchestrator)
│   │   └── layers.py         # Chart layers (Zodiac, Houses, Planets, etc.)
│   │
│   ├── data/                  # Data registries and notables database
│   │   └── notables/         # Notable births YAML files
│   │
│   ├── utils/                 # Utilities
│   │   ├── cache.py          # Caching decorators and utilities
│   │   └── cache_utils.py    # Cache management
│   │
│   └── cli/                   # Command-line interface
│
├── tests/                     # Test suite
│   ├── test_chart_builder.py
│   ├── test_integration.py
│   ├── test_ephemeris_engine.py
│   ├── test_aspect_engine.py
│   ├── test_arabic_parts.py
│   ├── test_midpoints.py
│   ├── test_celestial_registry.py
│   ├── test_aspect_registry.py
│   ├── test_notables.py
│   ├── test_core_models.py
│   └── benchmark_performance.py
│
├── examples/                  # Usage examples
│   ├── viz_examples.py       # Visualization examples
│   ├── report_examples.py    # Report generation examples
│   └── chart_examples/       # Generated chart SVGs
│
├── data/                      # Swiss Ephemeris data files
│   └── swisseph/ephe/        # Ephemeris data (1800-2400 CE)
│
├── docs/                      # Documentation
│   ├── USER_GUIDE.md
│   ├── development/
│   │   ├── ARCHITECTURE_QUICK_REFERENCE.md
│   │   ├── CONTRIBUTING.md
│   │   └── REFACTORING_GUIDE.md
│   └── planning/
│
├── pyproject.toml            # Package configuration
├── README.md                 # User-facing documentation
├── CONTRIBUTING.md           # Contribution guidelines
├── TODO.md                   # Development roadmap
└── CLAUDE.md                 # This file
```

---

## Core Principles

### Immutable Data

All result objects are frozen dataclasses:

```python
# ✅ DO: All models are frozen
@dataclass(frozen=True)
class CelestialPosition:
    name: str
    longitude: float
    # Cannot be modified after creation

# Usage
sun = chart.get_object("Sun")
sun.longitude = 100  # ❌ FrozenInstanceError!

# To modify, create new instance
from dataclasses import replace
new_sun = replace(sun, longitude=100)  # ✅ Creates new object
```

**Benefits:**
- Thread-safe
- Safe to cache and share
- Predictable behavior
- No accidental mutations

### Protocol-Based Interfaces

Instead of inheritance, use Protocols for extensibility:

```python
# ✅ DO: Define interfaces with Protocol
class EphemerisEngine(Protocol):
    def calculate_position(self, jd: float, obj_id: int) -> tuple[float, ...]:
        ...

# Implement without inheritance
class MyCustomEngine:
    def calculate_position(self, jd: float, obj_id: int) -> tuple[float, ...]:
        # Your implementation
        return (longitude, latitude, distance, ...)

# It just works!
chart = ChartBuilder.from_native(native).with_ephemeris(MyCustomEngine()).calculate()
```

**Key Protocols:**
- `EphemerisEngine` - Calculate celestial positions
- `HouseSystemEngine` - Calculate house cusps
- `AspectEngine` - Find aspects
- `OrbEngine` - Calculate orb allowances
- `ChartComponent` - Add custom calculations
- `ReportSection` - Add report sections
- `IRenderLayer` - Add visualization layers

### Dependency Injection

Configuration is injected via the builder:

```python
# ✅ DO: Inject dependencies
chart = (ChartBuilder.from_native(native)
    .with_ephemeris(SwissEphemerisEngine())
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .with_orbs(LuminariesOrbEngine())
    .add_component(ArabicPartsCalculator())
    .calculate())

# ❌ DON'T: Hardcode dependencies
class Chart:
    def __init__(self):
        self.ephemeris = SwissEphemerisEngine()  # Hardcoded!
```

---

## Development Workflows

### 1. Development Setup

```bash
# Clone and setup
git clone https://github.com/katelouie/stellium.git
cd stellium

# Activate environment
source ~/.zshrc
pyenv activate starlight

# Install with dev dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### 2. Running Tests

**Always activate environment first!**

```bash
# Activate environment
source ~/.zshrc && pyenv activate starlight

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_chart_builder.py

# Run tests matching a pattern
pytest -k "test_aspect"

# Run with verbose output
pytest -v
```

### 3. Running Examples

```bash
# Always activate environment first
source ~/.zshrc && pyenv activate starlight

# Run visualization examples
python examples/viz_examples.py

# Run report examples
python examples/report_examples.py
```

### 4. Type Checking

```bash
# Run mypy on source code
mypy src/stellium
```

### 5. Code Formatting

Pre-commit hooks handle this automatically, but you can run manually:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Format with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with ruff
ruff check src/ tests/
```

### 6. Making Changes

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, run tests
source ~/.zshrc && pyenv activate starlight && pytest

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "Add feature: description"

# Push and create PR
git push origin feature/your-feature-name
```

---

## Testing Conventions

### Test Organization

- Place tests in `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<what_you're_testing>()`
- Use descriptive names that explain what's being tested

### Test Types

**Unit Tests:**
```python
def test_celestial_position_sign_calculation():
    """Test that longitude correctly converts to zodiac sign."""
    pos = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=45.5,  # Mid-Taurus
        latitude=0.0,
        distance=1.0,
    )
    assert pos.sign == "Taurus"
    assert pos.degree_in_sign == 15.5
```

**Integration Tests:**
```python
def test_full_chart_calculation():
    """Test end-to-end chart calculation."""
    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    assert len(chart.get_planets()) == 10
    assert chart.get_object("Sun") is not None
    assert chart.get_houses() is not None
    assert len(chart.aspects) > 0
```

**Regression Tests:**
```python
def test_moon_aspect_orb_calculation():
    """Regression test for issue #123: Moon orb calculation was incorrect."""
    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    moon_aspects = [a for a in chart.aspects if a.object1.name == "Moon"]
    moon_sun = next(a for a in moon_aspects if a.object2.name == "Sun")

    # Bug was that orb was > 10°, should be < 8°
    assert moon_sun.orb < 8.0
```

### Test Requirements

**All contributions must include tests:**
- Bug fixes: Write a test that fails before fix, passes after
- New features: Test happy path + edge cases + integration
- Refactoring: Ensure existing tests still pass

### Test Files That Require Environment

**IMPORTANT:** All tests that import from `stellium.*` require the pyenv environment to be activated:

```bash
source ~/.zshrc && pyenv activate starlight && pytest
```

Test files:
- `tests/test_chart_builder.py` - ChartBuilder tests
- `tests/test_integration.py` - End-to-end integration tests
- `tests/test_ephemeris_engine.py` - Ephemeris calculations
- `tests/test_aspect_engine.py` - Aspect calculations
- `tests/test_arabic_parts.py` - Arabic parts
- `tests/test_midpoints.py` - Midpoint calculations
- `tests/test_celestial_registry.py` - Celestial object registry
- `tests/test_aspect_registry.py` - Aspect registry
- `tests/test_notables.py` - Notable births database
- `tests/test_core_models.py` - Core data models
- `tests/benchmark_performance.py` - Performance benchmarks

---

## Code Style & Conventions

### Python Version & Type Hints

- **Python 3.11+** required (uses modern type hints)
- **All functions must have type hints** (enforced by mypy)
- Use modern syntax: `X | Y` instead of `Union[X, Y]`
- Use `list[str]` instead of `List[str]`

```python
# ✅ Good
def get_object(self, name: str) -> CelestialPosition | None:
    """Get celestial object by name."""
    return self._positions.get(name)

# ❌ Bad - missing type hints
def get_object(self, name):
    return self._positions.get(name)
```

### Formatting

Uses **Black** (88 character line length, enforced by pre-commit):

```python
# ✅ Good
def calculate_position(
    julian_day: float,
    object_id: int,
    flags: int = 0,
) -> tuple[float, float, float]:
    """Calculate celestial object position."""
    return (longitude, latitude, distance)
```

### Imports

Use **isort** (enforced by pre-commit):

```python
# Standard library
from datetime import datetime
from typing import Protocol

# Third-party
import pytz
from geopy.geocoders import Nominatim

# Local - group by module
from stellium.core.models import CelestialPosition
from stellium.engines.ephemeris import SwissEphemerisEngine
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_aspect_orb(
    obj1: CelestialPosition,
    obj2: CelestialPosition,
    aspect_angle: float,
) -> float:
    """Calculate the orb (deviation) for an aspect between two objects.

    Args:
        obj1: First celestial object
        obj2: Second celestial object
        aspect_angle: The ideal aspect angle (e.g., 120° for trine)

    Returns:
        The orb in degrees (absolute value)

    Example:
        >>> sun = chart.get_object("Sun")
        >>> moon = chart.get_object("Moon")
        >>> orb = calculate_aspect_orb(sun, moon, 120.0)
        >>> print(f"Trine orb: {orb:.2f}°")
    """
    actual_angle = calculate_angle(obj1.longitude, obj2.longitude)
    return abs(actual_angle - aspect_angle)
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ChartBuilder`, `SwissEphemerisEngine`)
- **Functions/Methods**: `snake_case` (e.g., `calculate_position`, `get_house_cusps`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CELESTIAL_REGISTRY`, `DEFAULT_ORB`)
- **Private**: Prefix with `_` (e.g., `_cached_calc_ut`, `_normalize_angle`)

### Dependency Rules

**CRITICAL: Avoid circular dependencies**

```python
# ❌ DON'T: core/ should NEVER import from engines/
# In core/models.py
from stellium.engines.ephemeris import SwissEphemeris  # ❌ WRONG

# ✅ DO: engines/ can import from core/
# In engines/ephemeris.py
from stellium.core.models import CelestialPosition  # ✅ CORRECT
```

**Import hierarchy:**
```
core/           # No imports from engines, components, visualization
  ↑
engines/        # Imports from core only
  ↑
components/     # Imports from core, engines
  ↑
presentation/   # Imports from core, engines, components
visualization/  # Imports from core, engines, components
```

---

## Common Tasks

### Task 1: Add a New House System

Implement the `HouseSystemEngine` protocol:

```python
# In src/stellium/engines/houses.py

from stellium.core.protocols import HouseSystemEngine
from stellium.core.models import HouseCusps

class VedicHouses:
    """Vedic/Hindu house system (whole sign from Moon)."""

    @property
    def system_name(self) -> str:
        return "Vedic"

    def calculate_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        asc_longitude: float | None = None,
    ) -> HouseCusps:
        """Calculate Vedic house cusps."""
        # Your calculation logic here
        cusps = [...]  # List of 12 cusp longitudes

        return HouseCusps(
            system_name=self.system_name,
            cusps=cusps,
        )

# Usage
chart = ChartBuilder.from_native(native).with_house_systems([VedicHouses()]).calculate()
```

### Task 2: Add a New Component

Implement the `ChartComponent` protocol:

```python
# In src/stellium/components/fixed_stars.py

from stellium.core.protocols import ChartComponent
from stellium.core.models import CelestialPosition

class FixedStarsCalculator:
    """Calculate positions of fixed stars."""

    @property
    def component_name(self) -> str:
        return "Fixed Stars"

    def calculate(
        self,
        chart_data: dict,  # Contains julian_day, positions, etc.
        config: CalculationConfig,
    ) -> list[CelestialPosition]:
        """Calculate fixed star positions."""
        julian_day = chart_data["julian_day"]
        stars = []

        for star_name, star_id in FIXED_STARS.items():
            pos = calculate_fixed_star_position(julian_day, star_id)
            stars.append(CelestialPosition(
                name=star_name,
                longitude=pos[0],
                # ... other fields
            ))

        return stars

# Usage
chart = ChartBuilder.from_native(native).add_component(FixedStarsCalculator()).calculate()
fixed_stars = chart.get_component_result("Fixed Stars")
```

### Task 3: Add a New Visualization Layer

Implement the `IRenderLayer` protocol:

```python
# In src/stellium/visualization/layers.py

from stellium.core.protocols import IRenderLayer
from stellium.visualization.core import ChartRenderer

class FixedStarsLayer:
    """Render fixed stars on the chart."""

    def render(
        self,
        renderer: ChartRenderer,
        dwg,  # SVG drawing object
        chart: CalculatedChart,
    ) -> None:
        """Render fixed stars."""
        stars = chart.get_component_result("Fixed Stars")

        for star in stars:
            # Convert longitude to (x, y) coordinates
            x, y = renderer.get_zodiac_point(star.longitude, radius=350)

            # Draw star symbol
            dwg.add(dwg.text(
                "⭐",
                insert=(x, y),
                font_size="12px",
                text_anchor="middle",
            ))

# Usage
renderer = ChartRenderer(size=800, rotation=0)
dwg = renderer.create_svg_drawing("chart.svg")

layers = [ZodiacLayer(), HouseCuspLayer(), PlanetLayer(), FixedStarsLayer()]
for layer in layers:
    layer.render(renderer, dwg, chart)

dwg.save()
```

### Task 4: Add Caching to Expensive Calculations

```python
from stellium.utils.cache import cached

class MyEngine:
    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def expensive_calculation(self, param1: str, param2: float) -> dict:
        """Expensive calculation that benefits from caching."""
        # Expensive work here
        result = ...
        return result

# First call: calculates and caches
# Second call with same params: returns cached result (20x faster!)
```

### Task 5: Working with the Notable Database

```python
# List available notables
from stellium.data import get_notable_registry
registry = get_notable_registry()
for name in registry.list_notable_names():
    print(name)

# Create chart for a notable
chart = ChartBuilder.from_notable("Albert Einstein").calculate()

# Add a new notable (edit data/notables/births/*.yaml)
# Format: YAML file with name, datetime, location
```

### Task 6: Export Chart Data to JSON

```python
chart = ChartBuilder.from_native(native).calculate()

# Export to dictionary (JSON-serializable)
data = chart.to_dict()

# Includes:
# - All planetary positions with coordinates
# - House cusps for all calculated systems
# - All aspects with orbs
# - Component results (Arabic Parts, midpoints, etc.)
# - Chart metadata (date, location, timezone)

import json
json.dump(data, open("chart.json", "w"), indent=2)
```

---

## Important Patterns

### Pattern 1: Builder Pattern

The primary API uses the builder pattern for fluent configuration:

```python
# Fluent interface - chain configuration methods
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .with_orbs(LuminariesOrbEngine())
    .add_component(ArabicPartsCalculator())
    .add_component(MidpointCalculator())
    .calculate())  # Only calculates at the end

# Each .with_X() and .add_X() returns self for chaining
# .calculate() returns immutable CalculatedChart
```

### Pattern 2: Frozen Dataclasses

All result objects are immutable:

```python
@dataclass(frozen=True)
class CelestialPosition:
    name: str
    longitude: float
    # ... other fields

# Cannot modify
sun = chart.get_object("Sun")
sun.longitude = 100  # ❌ FrozenInstanceError

# To modify, create new instance
from dataclasses import replace
new_sun = replace(sun, longitude=100)  # ✅ Creates new object

# Original unchanged
assert sun.longitude != 100
assert new_sun.longitude == 100
```

### Pattern 3: Registry Pattern

Celestial objects and aspects are defined in registries:

```python
from stellium.core.registry import CELESTIAL_REGISTRY, ASPECT_REGISTRY

# Get object info
sun_info = CELESTIAL_REGISTRY.get_object("Sun")
print(sun_info.symbol)  # ☉
print(sun_info.glyph)   # Unicode glyph

# Get aspect info
trine_info = ASPECT_REGISTRY.get_aspect("Trine")
print(trine_info.angle)  # 120.0
print(trine_info.symbol) # △
```

### Pattern 4: Protocol-Based Extension

Instead of inheritance, use protocols for flexibility:

```python
# Define interface
class MyEngine(Protocol):
    def calculate(self, data: dict) -> list[Result]:
        ...

# Implement without inheritance
class ConcreteEngine:
    def calculate(self, data: dict) -> list[Result]:
        # Implementation
        return results

# Use it
engine = ConcreteEngine()  # No base class needed!
results = engine.calculate(data)
```

### Pattern 5: Lazy Evaluation

ChartBuilder doesn't calculate until you call `.calculate()`:

```python
# Configure (fast, no calculation yet)
builder = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses()])
    .with_aspects(ModernAspectEngine()))

# Can inspect configuration
print(builder._house_systems)
print(builder._aspect_engine)

# Calculate when ready
chart = builder.calculate()  # NOW it calculates
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Modifying Frozen Objects

```python
# ❌ DON'T: Try to modify frozen dataclasses
chart = builder.calculate()
chart.positions[0].longitude = 999  # FrozenInstanceError!

# ✅ DO: Create new objects with replace()
from dataclasses import replace
new_pos = replace(chart.positions[0], longitude=999)
```

### Anti-Pattern 2: Circular Dependencies

```python
# ❌ DON'T: Import from higher-level modules in core
# In core/models.py
from stellium.engines.ephemeris import SwissEphemeris  # ❌ WRONG

# ✅ DO: Only import from same level or lower
# In engines/ephemeris.py
from stellium.core.models import CelestialPosition  # ✅ CORRECT
```

### Anti-Pattern 3: Hidden State

```python
# ❌ DON'T: Hidden class-level state
class ChartBuilder:
    _cache = {}  # Class-level cache (shared between instances!)

    def calculate(self):
        if self._datetime in self._cache:
            return self._cache[self._datetime]

# ✅ DO: Make caching explicit at function level
@cached(cache_type="ephemeris")
def calculate_positions(...):
    ...
```

### Anti-Pattern 4: Hardcoded Dependencies

```python
# ❌ DON'T: Hardcode engines
class Chart:
    def __init__(self):
        self.ephemeris = SwissEphemerisEngine()  # Hardcoded!

# ✅ DO: Inject dependencies via builder
chart = (ChartBuilder.from_native(native)
    .with_ephemeris(SwissEphemerisEngine())  # Injected
    .calculate())
```

### Anti-Pattern 5: Running Python Without Environment

```python
# ❌ DON'T: Run bare python commands
$ python tests/test_chart_builder.py  # Will fail with import errors!

# ✅ DO: Always activate environment first
$ source ~/.zshrc && pyenv activate starlight && python tests/test_chart_builder.py
```

---

## Quick Reference

### Essential Commands

```bash
# Activate environment (ALWAYS DO THIS FIRST!)
source ~/.zshrc && pyenv activate starlight

# Run tests
pytest
pytest --cov=src --cov-report=term-missing
pytest tests/test_chart_builder.py -v

# Type checking
mypy src/stellium

# Code formatting (auto-run by pre-commit)
pre-commit run --all-files
black src/ tests/
isort src/ tests/
ruff check src/ tests/

# Run examples
python examples/viz_examples.py
python examples/report_examples.py
```

### Quick API Examples

```python
# Simple chart
from stellium import ChartBuilder
chart = ChartBuilder.from_notable("Albert Einstein").calculate()

# Custom chart
from stellium import ChartBuilder, Native
from datetime import datetime

native = Native(datetime(2000, 1, 6, 12, 0), "Seattle, WA")
chart = ChartBuilder.from_native(native).calculate()

# Advanced configuration
from stellium.engines import PlacidusHouses, WholeSignHouses, ModernAspectEngine
from stellium.components import ArabicPartsCalculator

chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .calculate())

# Access results
sun = chart.get_object("Sun")
print(f"{sun.name}: {sun.longitude:.2f}° {sun.sign}")

aspects = chart.aspects
for aspect in aspects[:5]:
    print(f"{aspect.object1.name} {aspect.aspect_name} {aspect.object2.name}")

# Generate report
from stellium import ReportBuilder
report = (ReportBuilder()
    .from_chart(chart)
    .with_chart_overview()
    .with_planet_positions()
    .with_aspects(mode="major"))
report.render(format="rich_table")

# Draw chart
chart.draw("chart.svg").save()
```

### Key Files to Know

- `src/stellium/__init__.py` - Public API exports
- `src/stellium/core/builder.py` - ChartBuilder (main entry point)
- `src/stellium/core/models.py` - All data models
- `src/stellium/core/protocols.py` - All interface definitions
- `src/stellium/core/registry.py` - CELESTIAL_REGISTRY, ASPECT_REGISTRY
- `src/stellium/engines/ephemeris.py` - SwissEphemerisEngine
- `src/stellium/engines/houses.py` - House system engines
- `src/stellium/engines/aspects.py` - Aspect engines
- `pyproject.toml` - Package configuration, dependencies, tool config

### Common Gotchas

1. **Always activate pyenv environment before running Python code**
2. **All data models are frozen** - use `replace()` to modify
3. **Protocols don't require inheritance** - just match the signature
4. **Builder returns self until `.calculate()`** - lazy evaluation
5. **Avoid circular imports** - core → engines → components (one direction only)
6. **Type hints are required** - mypy enforces this
7. **Pre-commit hooks auto-format** - don't worry about manual formatting

### Performance Tips

1. Use caching for expensive operations: `@cached(cache_type="ephemeris")`
2. Batch ephemeris calls when possible
3. Use MockEphemerisEngine for tests that don't need real calculations
4. Enable cache: `from stellium.utils.cache import enable_cache; enable_cache()`

### Decision Guide

**Should I create a new Protocol?**
- Yes: Multiple implementations will exist, want extensibility
- No: Only one implementation, internal utility

**Should this be immutable?**
- Yes: It's a result/output, shared between components, represents point-in-time
- No: It's a builder, internal state, cache

**Should I use the Builder?**
- Yes: Chart construction, complex configuration
- No: Simple data classes, engine internals, utilities

---

## Additional Resources

- **README.md** - User-facing documentation and examples
- **CONTRIBUTING.md** - Detailed contribution guidelines
- **docs/development/ARCHITECTURE_QUICK_REFERENCE.md** - Architecture patterns
- **docs/USER_GUIDE.md** - Comprehensive user guide
- **TODO.md** - Development roadmap
- **CHANGELOG.md** - Release history

---

**Remember:** Always activate the pyenv environment before running any Python code!

```bash
source ~/.zshrc && pyenv activate starlight
```

This is the most important rule for working with Stellium. Without the environment activated, Swiss Ephemeris imports will fail and calculations will be incorrect.
