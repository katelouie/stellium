# Claude Development Instructions for Stellium

**Stellium** is a modern, extensible Python library for computational astrology built on Swiss Ephemeris for NASA-grade astronomical accuracy.

---

## 📍 Documentation Map (read this first)

This file is the **hub**: environment, workflow, conventions, and anti-patterns.
The **technical API/architecture reference** lives in
[`docs/development/`](docs/development/README.md) — read those instead of
re-deriving the API from source each session:

| Need | Go to |
|---|---|
| How the codebase fits together, dependency rules, `.calculate()` flow | [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md) |
| `ChartBuilder`, `CalculatedChart`, `Native`, config, registries | [docs/development/CHART_BUILDING.md](docs/development/CHART_BUILDING.md) |
| Ephemeris, houses, aspects, orbs, dignities, patterns, profections | [docs/development/ENGINES.md](docs/development/ENGINES.md) |
| Components, analysis/DataFrames, IO, caching, utils | [docs/development/COMPONENTS_AND_ANALYSIS.md](docs/development/COMPONENTS_AND_ANALYSIS.md) |
| SVG rendering internals, layers, themes/palettes, dial/vedic/atlas | [docs/development/VISUALIZATION_INTERNALS.md](docs/development/VISUALIZATION_INTERNALS.md) |
| `ReportBuilder`, sections, renderers | [docs/development/PRESENTATION_INTERNALS.md](docs/development/PRESENTATION_INTERNALS.md) |
| Multi-chart, returns, electional, planner, Chinese/BaZi, CLI | [docs/development/SUBSYSTEMS.md](docs/development/SUBSYSTEMS.md) |
| The notables database — schema, provenance, Old Style dates, curation | [docs/development/NOTABLES.md](docs/development/NOTABLES.md) |
| Adding an engine / component / analyzer / layer / theme / section | [docs/development/EXTENDING.md](docs/development/EXTENDING.md) |
| Full doc index (incl. user-facing guides) | [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md) |

> When a doc disagrees with the source, **the source wins** — fix the doc.

---

## Table of Contents

- [Documentation Map](#-documentation-map-read-this-first)
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

> **Environment note.** The `pyenv activate starlight` step is the *local*
> workflow. CI and any clean environment (containers, fresh checkouts) instead
> do `pip install -e ".[dev]"` then run `pytest` / `ruff check .` /
> `ruff format --check .` directly — no pyenv. Use whichever matches where you
> are; the goal is just an interpreter with the package + dev deps installed.
> CI runs on Python 3.11–3.13 across Linux/macOS/Windows (`.github/workflows/tests.yml`).

---

## Documentation Organization

All project documentation lives under `docs/`:

- **`docs/development/`** — **Agent/contributor API & architecture reference**
  (the spokes linked in the [Documentation Map](#-documentation-map-read-this-first)).
  Keep this current with the code.
- **`docs/`** (root) — User-facing guides (`VISUALIZATION.md`, `REPORTS.md`,
  `CHART_TYPES.md`, gallery pages, `options_list.md`, the Sphinx site).
- **`docs/ARCHITECTURE.md`** — superseded historical doc (kept for concepts;
  see the redirect banner at its top).

**Index:** See [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md) for the complete list
with status.

**When adding new docs:**
- Technical reference / how a subsystem works? Add or extend a file in
  `docs/development/` and link it from `docs/development/README.md`,
  `docs/DOCS_INDEX.md`, and the Documentation Map above.
- User-facing guide? Add to `docs/` (root) and list it in `docs/DOCS_INDEX.md`.
- Planning/archive folders are not currently used — create `docs/planning/`
  only if a longer-lived design doc is needed.

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
Native/Notable (birth data)
    ↓
ChartBuilder (API layer) — fluent, lazy configuration
    ↓  .calculate()
Engines (calculation layer)
    ├── EphemerisEngine    → CelestialPosition[]   (positions + declination + phase)
    ├── HouseSystemEngine  → HouseCusps + angles   (per system)
    ├── AspectEngine       → Aspect[]              (+ declination aspects)
    └── OrbEngine          → orb allowances
    ↓
Components (add positions)        Analyzers (add metadata)
    ├── ArabicPartsCalculator         ├── AspectPatternAnalyzer
    ├── MidpointCalculator            └── ZodiacalReleasingAnalyzer
    ├── DignityComponent
    └── FixedStarsComponent
    ↓
CalculatedChart (immutable result) ──► transforms: profection(), zodiacal_releasing(),
    ↓                                              draconic(), voc_moon(), returns
Presentation / Visualization / Export / Analysis
    ├── ReportBuilder  → rich / plain / markdown / html / pdf / prose
    ├── chart.draw()   → SVG (wheel, dial, vedic, multiwheel, atlas PDF)
    ├── to_dict()      → JSON  ·  to_prompt_text() → LLM context
    └── analysis.* / io.* → pandas DataFrames, CSV/AAF import
```

> Full detail: [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md).

---

## Directory Structure

> Per-subsystem API detail is in [docs/development/](docs/development/README.md).
> This is the high-level layout only.

```
stellium/
├── src/stellium/              # Main package
│   ├── __init__.py            # Public API exports (the canonical surface)
│   ├── core/                  # Abstractions — NEVER imports from higher layers
│   │   ├── models.py          #   CelestialPosition, Aspect, CalculatedChart, MultiChart, …
│   │   ├── protocols.py       #   engine/component/section Protocols (NOT layers:
│   │   │                      #   IRenderLayer lives in visualization/layer_factory.py)
│   │   ├── builder.py         #   ChartBuilder (main entry point)
│   │   ├── native.py          #   Native, Notable (parsing/geocoding/timezone)
│   │   ├── config.py          #   CalculationConfig, AspectConfig
│   │   ├── ayanamsa.py        #   ZodiacType + ayanamsa registry
│   │   ├── registry.py        #   CELESTIAL_/ASPECT_/FIXED_STARS_REGISTRY
│   │   ├── comparison.py multichart.py multiwheel.py synthesis.py  # multi-chart
│   │   └── chart_utils.py     #   duck-typed chart-type helpers (avoids cycles)
│   ├── engines/               # Calculation (ephemeris, houses, aspects, orbs,
│   │                          #   dignities, patterns, dispositors, profections,
│   │                          #   releasing, directions, voc, fixed_stars, search)
│   ├── components/            # Optional add-ons (arabic_parts, midpoints,
│   │                          #   dignity, fixed_stars, antiscia)
│   ├── analysis/             # Batch + pandas (batch, frames, stats, queries, vector, export)
│   ├── io/                    # Import natives (csv, aaf, dataframe)
│   ├── electional/           # Time search (predicates, intervals, planetary_hours)
│   ├── returns/              # Solar/lunar/planetary returns (ReturnBuilder)
│   ├── planner/             # Personalized PDF planners (Typst)
│   ├── chinese/             # BaZi / Four Pillars (+ ziwei: planned)
│   ├── presentation/        # ReportBuilder, sections/, renderers (rich/md/html/pdf/prose)
│   ├── visualization/       # SVG: builder→composer→layers/, themes, palettes,
│   │                          #   dial/, vedic/, atlas/, layout/
│   ├── data/                # Registries + notables YAML + bundled ephemeris
│   ├── utils/               # cache, time/JD, chart_shape, chart_ruler, progressions
│   └── cli/                 # `stellium` CLI (chart, ephemeris, cache)
│
├── tests/                   # fast tier via `-m "not slow"`; conftest.py fixtures
├── examples/                # *_cookbook.py per subsystem + notebooks
├── docs/                    # Docs (see docs/DOCS_INDEX.md)
│   └── development/         # ← Agent API/architecture reference (this set)
├── web/                     # NiceGUI web app (optional)
├── pyproject.toml  README.md  CONTRIBUTING.md  CHANGELOG.md  TODO.md  CLAUDE.md
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
# The protocol, as it actually is (src/stellium/core/protocols.py):
class EphemerisEngine(Protocol):
    def calculate_positions(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
        objects: list[str] | None = None,
        config: CalculationConfig | None = None,
    ) -> list[CelestialPosition]:
        ...

# Implement without inheritance — match the signature and you ARE one.
class MyCustomEngine:
    def calculate_positions(self, datetime, location, objects=None, config=None):
        return [...]  # list[CelestialPosition]

chart = ChartBuilder.from_native(native).with_ephemeris(MyCustomEngine()).calculate()
```

**Key Protocols** (signatures verified against the source — do not paraphrase them
from memory, read `protocols.py`):

| Protocol | Method(s) | Lives in |
|---|---|---|
| `EphemerisEngine` | `calculate_positions(datetime, location, objects, config)` | `core/protocols.py` |
| `HouseSystemEngine` | `system_name`, `calculate_house_data(datetime, location, config)`, `assign_houses(positions, cusps)` | `core/protocols.py` |
| `AspectEngine` | `calculate_aspects(...)` | `core/protocols.py` |
| `OrbEngine` | `get_orb_allowance(...)` | `core/protocols.py` |
| `ChartComponent` | `component_name`, `metadata_name`, `calculate(datetime, location, positions, house_systems_map, house_placements_map)` | `core/protocols.py` |
| `ReportSection` | `section_name`, `generate_data(chart)` | `core/protocols.py` |
| `IRenderLayer` | `render(renderer, dwg, chart)` | **`visualization/layer_factory.py`** — *not* `core/protocols.py` |

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

### Fast vs Slow Tests

Tests are split into two tiers using the `@pytest.mark.slow` marker:

**Fast tests (`-m "not slow"`):** ~719 tests in ~2.4 seconds
- Pure logic: aspects, dignities, chart shapes, models, registries, patterns
- No ephemeris calls, no chart calculation
- **Use this for TDD and rapid iteration**

**Full suite (default `pytest`):** ~1938 tests in ~30 seconds
- Includes chart calculations, electional search, I/O parsing, visualization
- **Run before commits and releases**

```bash
# Fast TDD loop (2.4s)
source ~/.zshrc && pyenv activate starlight && pytest -m "not slow"

# Full suite (30s)
source ~/.zshrc && pyenv activate starlight && pytest

# Full with coverage
source ~/.zshrc && pyenv activate starlight && pytest --cov=src --cov-report=term-missing
```

To mark a new test file as slow, add near the top (after imports):
```python
pytestmark = pytest.mark.slow
```

### Test Organization

- Place tests in `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<what_you're_testing>()`
- Use descriptive names that explain what's being tested

### Test Types

**Unit Tests:**
```python
from stellium.core.models import CelestialPosition, ObjectType


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
    assert pos.sign_degree == 15.5              # NOT `degree_in_sign` — no such field
    assert pos.sign_position == "15°30' Taurus"


test_celestial_position_sign_calculation()
print("ok")
```

<!--pytest-codeblocks:expected-output-->

```
ok
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

<!--pytest.mark.skip-->
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

<!--pytest.mark.skip-->
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

Implement the `HouseSystemEngine` protocol. **Two methods, not one** — the builder
calls `calculate_house_data` and then `assign_houses`, and an engine missing the second
raises `AttributeError` deep inside `.calculate()`.

```python
# In src/stellium/engines/houses.py

from stellium import ChartBuilder
from stellium.core.models import HouseCusps


class EqualFromMC:
    """Twelve equal houses, measured from the Midheaven."""

    @property
    def system_name(self) -> str:
        return "Equal from MC"

    def calculate_house_data(self, datetime, location, config=None):
        # -> (HouseCusps, list[CelestialPosition] of the angles)
        cusps = tuple((30.0 * i) % 360.0 for i in range(12))
        return HouseCusps(system=self.system_name, cusps=cusps), []

    def assign_houses(self, positions, cusps):
        # -> dict[object_name, house_number]
        return {p.name: int(p.longitude // 30) + 1 for p in positions}


chart = (
    ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([EqualFromMC()])
    .calculate()
)
print(f"Sun is in house {chart.get_house('Sun', 'Equal from MC')}")
```

<!--pytest-codeblocks:expected-output-->

```
Sun is in house 10
```

Note `HouseCusps(system=...)` — **not** `system_name=`, and the cusps are a **tuple**.

### Task 2: Add a New Component

Implement the `ChartComponent` protocol. `calculate()` receives the chart's parts as
**five arguments** — there is no `chart_data` dict.

```python
# In src/stellium/components/my_component.py

from stellium import ChartBuilder
from stellium.core.models import CelestialPosition, ObjectType


class SolarAntiscion:
    """A component: the Sun reflected across the Cancer–Capricorn axis."""

    @property
    def component_name(self) -> str:
        return "Solar Antiscion"

    @property
    def metadata_name(self) -> str:
        return "solar_antiscion"

    def calculate(
        self,
        datetime,
        location,
        positions,             # list[CelestialPosition] computed so far
        house_systems_map,     # dict[str, HouseCusps]
        house_placements_map,  # dict[str, dict[str, int]]
    ) -> list[CelestialPosition]:
        sun = next(p for p in positions if p.name == "Sun")
        return [
            CelestialPosition(
                name="Antiscion:Sun",
                object_type=ObjectType.POINT,
                longitude=(180.0 - sun.longitude) % 360.0,
                latitude=0.0,
                distance=0.0,
            )
        ]


chart = (
    ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .add_component(SolarAntiscion())
    .calculate()
)
pt = chart.get_object("Antiscion:Sun")
print(f"{pt.name}: {pt.sign_position}")
```

<!--pytest-codeblocks:expected-output-->

```
Antiscion:Sun: 14°11' Sagittarius
```

The positions a component returns are merged into `chart.positions`. Anything it wants
to put in `chart.metadata` goes under its `metadata_name`.

### Task 3: Add a New Visualization Layer

Implement the `IRenderLayer` protocol — which lives in
`stellium/visualization/layer_factory.py`, **not** in `core/protocols.py`.

```python
# In src/stellium/visualization/layers/my_layer.py

import svgwrite

from stellium import ChartBuilder
from stellium.visualization.core import ChartRenderer


class SunMarkerLayer:
    """A render layer: put a mark on the Sun's degree."""

    def render(self, renderer, dwg, chart) -> None:
        sun = chart.get_object("Sun")
        # longitude -> (x, y). The renderer owns the geometry; ask it.
        x, y = renderer.polar_to_cartesian(sun.longitude, radius=280)
        dwg.add(dwg.text("★", insert=(x, y), font_size="14px", text_anchor="middle"))


chart = ChartBuilder.from_notable("Albert Einstein").calculate()
renderer = ChartRenderer(size=600, rotation=0)
dwg = svgwrite.Drawing("chart.svg", size=(renderer.size, renderer.size))

SunMarkerLayer().render(renderer, dwg, chart)
dwg.save()
print("★" in open("chart.svg").read())
```

<!--pytest-codeblocks:expected-output-->

```
True
```

The renderer's geometry API is exactly two methods: `polar_to_cartesian(astro_deg,
radius)` and `astrological_to_svg_angle(astro_deg)`. It does **not** create the
drawing for you — `svgwrite.Drawing` does. In real use `LayerFactory` builds the layer
list from the config; you rarely assemble one by hand.

### Task 4: Add Caching — and when not to

**Do not disk-cache a calculation.** This section used to recommend exactly that,
with `@cached(cache_type="ephemeris")` on a method, and called it "20× faster". It
was never measured. It was **13× slower** — a `swe.calc_ut` takes microseconds and a
pickle round-trip does not — and because `@cached` on a *method* puts `self` in the
key, and `self`'s repr contains a memory address, no entry could ever be found
again. Every call missed, every call wrote a file, nothing was ever read back. It
reached **18.5 million files** before anyone looked. See CHANGELOG 0.21.1.

Cache a **network call**, keyed on a plain string. That is the case the mechanism
was always right for, and the only remaining `@cached` in the library:

```python
# src/stellium/core/native.py — geocoding: a slow network round-trip, stable key
@cached(cache_type="geocoding", max_age_seconds=604800)
def geocode_location(location: str) -> tuple[float, float, str]:
    ...
```

Two rules, both now enforced rather than advised:

- **Never on a method.** `self` becomes part of the key. `_make_key()` now raises
  `UnstableCacheKey` on any argument whose repr embeds a memory address, and
  `@cached` degrades to an uncached call with a warning rather than silently
  poisoning the cache.
- **Measure before you cache.** If the work is cheaper than the pickle, caching it
  is a pessimisation that also fills the user's disk.

### Task 5: Working with the Notable Database

```python
from stellium import ChartBuilder
from stellium.data import get_notable_registry

registry = get_notable_registry()

# The registry's real surface: get_all / get_births / get_events / get_by_name /
# get_by_category / get_by_event_type / search(**filters).
# There is NO `list_notable_names()`.
print(len(registry.get_all()), "records:",
      len(registry.get_births()), "births +",
      len(registry.get_events()), "events")
print(registry.get_by_name("Albert Einstein").name)

# Create a chart for a notable
chart = ChartBuilder.from_notable("Albert Einstein").calculate()

# Add a new notable: edit src/stellium/data/notables/births/*.yaml
# Schema, provenance fields, Old Style dates: docs/development/NOTABLES.md
```

<!--pytest-codeblocks:expected-output-->

```
211 records: 190 births + 21 events
Albert Einstein
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

Celestial objects and aspects are defined in registries. **The registries are plain
`dict`s** — there is no `.get_object()` / `.get_aspect()` method. Subscript them, or
use the module-level lookup helpers (which also resolve aliases).

```python
from stellium.core.registry import (
    CELESTIAL_REGISTRY,
    ASPECT_REGISTRY,
    get_object_info,
    get_aspect_info,
)

sun_info = get_object_info("Sun")          # or CELESTIAL_REGISTRY["Sun"]
trine_info = get_aspect_info("Trine")      # or ASPECT_REGISTRY["Trine"]

print(sun_info.glyph, trine_info.glyph, trine_info.angle)
print(len(CELESTIAL_REGISTRY), "objects;", len(ASPECT_REGISTRY), "aspects")
```

<!--pytest-codeblocks:expected-output-->

```
☉ △ 120.0
83 objects; 19 aspects
```

The field is `.glyph`, **not** `.symbol` — `CelestialObjectInfo` and `AspectInfo` have
no `symbol` attribute at all.

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

<!--pytest.mark.skip-->
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

# ✅ DO: Make caching explicit at function level — and only for a network call,
# never for a computation, and never on a method (`self` poisons the key).
@cached(cache_type="geocoding")
def geocode_location(location: str):
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
<!--pytest-codeblocks:expected-output-->
```
Sun: 285.81° Capricorn
Sun Conjunction Moon
Sun Conjunction Mercury
Sun Trine Saturn
Sun Conjunction MC
Sun Square Vertex

Chart Overview
──────────────
Date: January 06, 2000
Time: 12:00 PM
Timezone: America/Los_Angeles
Location: Seattle, King County, Washington, United States
Coordinates: 47.6038°, -122.3301°
House System: Placidus, Whole Sign
Zodiac: Tropical
Chart Ruler: Mars (Aries Rising)

Planet Positions
────────────────
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Planet              ┃ Position              ┃ House (Pl) ┃ House (WS) ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ ☉ Sun               │ ♑︎ Capricorn 15°48'   │ 10         │ 10         │
│ ☽ Moon              │ ♑︎ Capricorn 16°36'   │ 10         │ 10         │
│ ☿ Mercury           │ ♑︎ Capricorn 10°16'   │ 9          │ 10         │
│ ♀ Venus             │ ♐︎ Sagittarius 8°01'  │ 8          │ 9          │
│ ♂ Mars              │ ♓︎ Pisces 2°06'       │ 11         │ 12         │
│ ♃ Jupiter           │ ♈︎ Aries 25°31'       │ 12         │ 1          │
│ ♄ Saturn            │ ♉︎ Taurus 10°18'      │ 1          │ 2          │
│ ♅ Uranus            │ ♒︎ Aquarius 15°05'    │ 11         │ 11         │
│ ♆ Neptune           │ ♒︎ Aquarius 3°23'     │ 10         │ 11         │
│ ♇ Pluto             │ ♐︎ Sagittarius 11°38' │ 8          │ 9          │
│ ☊ North Node        │ ♌︎ Leo 3°40'          │ 5          │ 5          │
│ ☋ South Node        │ ♒︎ Aquarius 3°40'     │ 11         │ 11         │
│ ⚸ Black Moon Lilith │ ♐︎ Sagittarius 24°03' │ 9          │ 9          │
│ 🜊 Vertex            │ ♎︎ Libra 10°26'       │ 6          │ 7          │
│ ⚷ Chiron            │ ♐︎ Sagittarius 12°13' │ 8          │ 9          │
└─────────────────────┴───────────────────────┴────────────┴────────────┘

Major Aspects
─────────────

  Aspectarian
[SVG: 404x404px - use HTML/PDF output to view]

  Aspect List
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Planet 1            ┃ Aspect        ┃ Planet 2            ┃ Orb   ┃ Applying ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ ☿ Mercury           │ △ Trine       │ ♄ Saturn            │ 0.05° │ A→       │
│ ☿ Mercury           │ □ Square      │ 🜊 Vertex            │ 0.18° │ —        │
│ ♆ Neptune           │ ☌ Conjunction │ ☋ South Node        │ 0.28° │ A→       │
│ ♆ Neptune           │ ☍ Opposition  │ ☊ North Node        │ 0.28° │ A→       │
│ ♇ Pluto             │ ☌ Conjunction │ ⚷ Chiron            │ 0.58° │ ←S       │
│ ☉ Sun               │ ☌ Conjunction │ ☽ Moon              │ 0.80° │ ←S       │
│ ♇ Pluto             │ ⚹ Sextile     │ 🜊 Vertex            │ 1.19° │ —        │
│ ♃ Jupiter           │ ☌ Conjunction │ ASC                 │ 1.35° │ —        │
│ ♃ Jupiter           │ △ Trine       │ ⚸ Black Moon Lilith │ 1.46° │ A→       │
│ ⚷ Chiron            │ ⚹ Sextile     │ 🜊 Vertex            │ 1.77° │ —        │
│ MC                  │ □ Square      │ 🜊 Vertex            │ 1.87° │ —        │
│ ♄ Saturn            │ △ Trine       │ MC                  │ 2.00° │ —        │
│ ☿ Mercury           │ ☌ Conjunction │ MC                  │ 2.05° │ —        │
│ ♀ Venus             │ ⚹ Sextile     │ 🜊 Vertex            │ 2.42° │ —        │
│ ⚸ Black Moon Lilith │ △ Trine       │ ASC                 │ 2.81° │ —        │
│ ♅ Uranus            │ ⚹ Sextile     │ ⚷ Chiron            │ 2.87° │ A→       │
│ ♅ Uranus            │ ⚹ Sextile     │ ♇ Pluto             │ 3.45° │ ←S       │
│ ☉ Sun               │ ☌ Conjunction │ MC                  │ 3.49° │ —        │
│ ♀ Venus             │ ☌ Conjunction │ ♇ Pluto             │ 3.61° │ A→       │
│ ♀ Venus             │ ☌ Conjunction │ ⚷ Chiron            │ 4.19° │ A→       │
│ ☽ Moon              │ ☌ Conjunction │ MC                  │ 4.30° │ —        │
│ ♀ Venus             │ ⚹ Sextile     │ ☋ South Node        │ 4.36° │ ←S       │
│ ♀ Venus             │ △ Trine       │ ☊ North Node        │ 4.36° │ ←S       │
│ ♅ Uranus            │ △ Trine       │ 🜊 Vertex            │ 4.64° │ —        │
│ ♀ Venus             │ ⚹ Sextile     │ ♆ Neptune           │ 4.64° │ ←S       │
│ ♄ Saturn            │ □ Square      │ ♅ Uranus            │ 4.77° │ ←S       │
│ ♂ Mars              │ ⚹ Sextile     │ ASC                 │ 5.23° │ —        │
│ ☉ Sun               │ □ Square      │ 🜊 Vertex            │ 5.36° │ —        │
│ ☉ Sun               │ △ Trine       │ ♄ Saturn            │ 5.49° │ ←S       │
│ ☉ Sun               │ ☌ Conjunction │ ☿ Mercury           │ 5.54° │ A→       │
│ ♀ Venus             │ □ Square      │ ♂ Mars              │ 5.93° │ ←S       │
│ ☽ Moon              │ □ Square      │ 🜊 Vertex            │ 6.17° │ —        │
│ ☽ Moon              │ △ Trine       │ ♄ Saturn            │ 6.30° │ ←S       │
│ ☽ Moon              │ ☌ Conjunction │ ☿ Mercury           │ 6.34° │ ←S       │
│ ♆ Neptune           │ □ Square      │ ASC                 │ 6.52° │ —        │
│ ♄ Saturn            │ □ Square      │ ☋ South Node        │ 6.65° │ A→       │
│ ♄ Saturn            │ □ Square      │ ☊ North Node        │ 6.65° │ ←S       │
│ ☋ South Node        │ △ Trine       │ 🜊 Vertex            │ 6.78° │ —        │
│ ☋ South Node        │ □ Square      │ ASC                 │ 6.80° │ —        │
│ ☊ North Node        │ □ Square      │ ASC                 │ 6.80° │ —        │
│ ♄ Saturn            │ □ Square      │ ♆ Neptune           │ 6.93° │ A→       │
│ ♆ Neptune           │ △ Trine       │ 🜊 Vertex            │ 7.06° │ —        │
│ ♃ Jupiter           │ □ Square      │ ♆ Neptune           │ 7.87° │ A→       │
│ ♇ Pluto             │ △ Trine       │ ☊ North Node        │ 7.97° │ ←S       │
└─────────────────────┴───────────────┴─────────────────────┴───────┴──────────┘
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

1. **Do not disk-cache ephemeris or house calculations.** They are microseconds; a
   pickle round-trip is not. Caching them measured 13× *slower*. (`enable_cache()`
   does not exist — this list used to recommend it.)
2. Cache **network** calls only, keyed on a plain string — see geocoding.
3. Never put `@cached` on a method: `self` lands in the key and the entry is
   unfindable forever after.
4. Batch ephemeris calls when possible.
5. Use MockEphemerisEngine for tests that don't need real calculations.

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
