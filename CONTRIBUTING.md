# Contributing to Stellium 🌟

Thank you for your interest in contributing to Stellium! We welcome contributions from developers and astrologers of all experience levels. Whether you're fixing a typo, adding a feature, or proposing a major architectural change, your contributions help make Stellium better for everyone.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Philosophy](#architecture-philosophy)
- [How to Contribute](#how-to-contribute)
- [Testing](#testing)
- [Code Style](#code-style)
- [Creating Extensions](#creating-extensions)
- [Documentation](#documentation)
- [Publishing to PyPI](#publishing-to-pypi)
- [Pull Request Process](#pull-request-process)
- [Getting Help](#getting-help)

---

## Code of Conduct

This project follows a simple principle: **be respectful and constructive**. We're building a tool that serves both developers and astrologers, so diverse perspectives are valued. Keep discussions focused on technical merit and improving the library.

---

## Getting Started

### Prerequisites

- **Python 3.11 or higher** (required for modern type hints and features)
- **Git** for version control
- **Basic understanding** of either Python or astrology (or both!)

### Quick Start

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/stellium.git
cd stellium

# 3. Install in development mode with all dev dependencies
pip install -e ".[dev]"

# 4. Set up pre-commit hooks (automatic code formatting)
pre-commit install

# 5. Run tests to ensure everything works
pytest

# 6. Create a branch for your work
git checkout -b feature/your-feature-name
```

You're ready to start contributing! 🎉

---

## Development Setup

### Installing Dependencies

Stellium uses `setuptools` for package management. Development dependencies include testing, formatting, and type-checking tools.

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - pytest, pytest-cov (testing)
# - black, ruff, isort (code formatting)
# - mypy (type checking)
# - pre-commit (git hooks)
```

### Pre-commit Hooks

Pre-commit hooks automatically format your code and run basic checks before each commit:

```bash
# Install hooks (one-time setup)
pre-commit install

# Manually run hooks on all files
pre-commit run --all-files
```

The hooks will:

- Format code with `black`
- Sort imports with `isort`
- Lint with `ruff`
- Check type hints with `mypy`
- Validate YAML and JSON files

**Note**: If hooks fail, they'll auto-fix most issues. Just `git add` the changes and commit again.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_chart_builder.py

# Run tests matching a pattern
pytest -k "test_aspect"

# Run with verbose output
pytest -v
```

### Type Checking

Stellium uses full type hints. Check your types with:

```bash
mypy src/stellium
```

---

## Architecture Philosophy

Understanding Stellium's architecture is key to contributing effectively. The library is built on three core principles that make it extensible, maintainable, and performant.

### 1. **Protocols over Inheritance**

Instead of rigid class hierarchies, Stellium uses **protocols** (structural typing) for extensibility.

#### ❌ Traditional Approach (Inheritance)

```python
class BaseEngine(ABC):
    @abstractmethod
    def calculate(self):
        pass

class MyEngine(BaseEngine):  # Must inherit
    def calculate(self):
        return "result"
```

**Problems:**

- Tight coupling to base class
- Hard to test (need to mock inheritance chain)
- Limits composition

#### ✅ Stellium Approach (Protocols)

```python
# In core/protocols.py
class EphemerisEngine(Protocol):
    """Any class with this method signature works."""
    def calculate_position(self, jd: float, obj_id: int) -> tuple[float, ...]:
        ...

# Your implementation - no inheritance needed!
class MyEphemerisEngine:
    def calculate_position(self, jd: float, obj_id: int) -> tuple[float, ...]:
        # Your custom logic
        return (longitude, latitude, distance, ...)

# It just works - duck typing with type safety!
builder = ChartBuilder.from_native(native).with_ephemeris(MyEphemerisEngine())
```

**Benefits:**

- No inheritance required
- Easy to test (just implement the interface)
- Compose engines freely
- Type-safe (mypy validates protocols)

**Key Protocols in Stellium:**

- `EphemerisEngine` - Calculate celestial positions
- `HouseSystemEngine` - Calculate house cusps
- `AspectEngine` - Find aspects between objects
- `OrbEngine` - Calculate orb allowances
- `ChartComponent` - Add custom calculations
- `ReportSection` - Add report sections
- `ReportRenderer` - Render reports to different formats

### 2. **Composability**

Every piece of Stellium is designed to work independently and be combined freely.

```python
# Mix and match - everything is optional
chart = (ChartBuilder.from_native(native)
    .with_ephemeris(CustomEphemeris())           # Custom ephemeris
    .with_house_systems([
        PlacidusHouses(),
        WholeSignHouses(),
        MyCustomHouses()                         # Your house system
    ])
    .with_aspects(HarmonicAspectEngine(7))       # Septile aspects
    .with_orbs(LuminariesOrbEngine())            # Custom orb rules
    .add_component(ArabicPartsCalculator())      # Arabic parts
    .add_component(MidpointCalculator())         # Midpoints
    .add_component(MyCustomComponent())          # Your component
    .calculate())
```

**Design Pattern: Builder:**

The `ChartBuilder` orchestrates all calculations:

1. Accepts configuration via fluent methods (`.with_X()`, `.add_Y()`)
2. Stores configuration (doesn't calculate yet - lazy evaluation)
3. Calls `.calculate()` to run the calculation pipeline
4. Returns immutable `CalculatedChart`

**Benefits:**

- Clear, readable API
- Testable (configure without calculating)
- Extensible (add new methods without breaking existing code)

### 3. **Immutability**

All data models are **frozen dataclasses** - they cannot be modified after creation.

```python
@dataclass(frozen=True)
class CelestialPosition:
    name: str
    longitude: float
    # ... other fields

# Usage
sun = chart.get_object("Sun")
sun.longitude = 100  # ❌ FrozenInstanceError!

# To "modify", create a new instance
from dataclasses import replace
new_sun = replace(sun, longitude=100)  # ✅ Creates new object
```

**Benefits:**

- **Thread-safe**: Multiple threads can read without locks
- **Cacheable**: Safe to cache and reuse (no accidental mutations)
- **Predictable**: Data can't change unexpectedly
- **Easier debugging**: If data is wrong, it was wrong from the start

**What's immutable:**

- `CelestialPosition` - Planetary positions
- `Aspect` - Aspect relationships
- `HouseCusps` - House cusp data
- `CalculatedChart` - Entire chart result
- All models in `core/models.py`

---

## How to Contribute

### Types of Contributions

We welcome:

1. **Bug Fixes** - Found a calculation error? Fix it!
2. **New Features** - Add new engines, components, or chart types
3. **Documentation** - Improve examples, guides, or docstrings
4. **Tests** - Increase test coverage
5. **Performance** - Optimize slow calculations
6. **Refactoring** - Improve code quality (without changing behavior)

### Contribution Workflow

1. **Check existing issues** - Is someone already working on this?
   - If yes, comment to collaborate
   - If no, create an issue to discuss (for large changes)

2. **Create a branch** with a descriptive name:

   ```bash
   git checkout -b feature/add-vedic-houses
   git checkout -b fix/aspect-orb-calculation
   git checkout -b docs/improve-readme-examples
   ```

3. **Make your changes**
   - Write code following the [Code Style](#code-style)
   - Add tests for new functionality
   - Update documentation if needed

4. **Test your changes**

   ```bash
   pytest                    # All tests must pass
   pytest --cov=src          # Check coverage
   mypy src/stellium        # Type check
   ```

5. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add Vedic house system engine"
   ```

   **Commit Message Guidelines:**
   - Use present tense ("Add feature" not "Added feature")
   - Be specific ("Fix aspect orb calculation for Moon" not "Fix bug")
   - Reference issues ("Fix #123: aspect orb calculation")

6. **Push to your fork**

   ```bash
   git push origin feature/add-vedic-houses
   ```

7. **Open a Pull Request** on GitHub
   - Describe what you changed and why
   - Link to related issues
   - Add screenshots for visual changes

---

## Testing

### Test Requirements

**All contributions must include tests.** Tests ensure code quality and prevent regressions.

#### For Bug Fixes

Write a test that **fails** on the current code and **passes** with your fix:

```python
def test_aspect_orb_calculation_for_moon():
    """Regression test for issue #123."""
    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).calculate()

    moon_aspects = [a for a in chart.aspects if a.object1.name == "Moon"]

    # Bug: Moon-Sun conjunction had wrong orb
    moon_sun = next(a for a in moon_aspects if a.object2.name == "Sun")
    assert moon_sun.orb < 8.0  # Should be within orb
```

#### For New Features

Write tests covering:

- **Happy path**: Feature works as expected
- **Edge cases**: Boundary conditions, unusual inputs
- **Integration**: Feature works with other components

```python
def test_vedic_houses_basic():
    """Test Vedic house system calculates correctly."""
    native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")
    chart = ChartBuilder.from_native(native).with_house_systems([VedicHouses()]).calculate()

    cusps = chart.get_house_cusps("Vedic")
    assert len(cusps.cusps) == 12
    assert 0 <= cusps.cusps[0] < 360

def test_vedic_houses_integration():
    """Test Vedic houses work with multiple house systems."""
    chart = ChartBuilder.from_native(native).with_house_systems([
        PlacidusHouses(),
        VedicHouses()
    ]).calculate()

    sun = chart.get_object("Sun")
    assert sun.house is not None  # Placidus house (default)
    assert sun.house_placements.get("Vedic") is not None
```

### Test Organization

- Place tests in `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<what_you're_testing>()`
- Group related tests in classes (optional)

```sh
tests/
├── test_chart_builder.py     # Builder pattern tests
├── test_ephemeris_engine.py  # Ephemeris calculations
├── test_houses.py             # House system tests
├── test_aspects.py            # Aspect calculations
└── test_integration.py        # End-to-end tests
```

### Running Your Tests

```bash
# Run just your new test
pytest tests/test_vedic_houses.py -v

# Run with coverage to see what you're testing
pytest tests/test_vedic_houses.py --cov=src/stellium/engines/houses

# Run all tests to ensure you didn't break anything
pytest
```

---

## Code Style

Stellium follows standard Python conventions with strict type checking.

### Formatting

We use **Black** for code formatting (enforced by pre-commit):

- 88 character line length
- Double quotes for strings
- Trailing commas in multi-line structures

```python
# ✅ Good
def calculate_position(
    julian_day: float,
    object_id: int,
    flags: int = 0,
) -> tuple[float, float, float]:
    """Calculate celestial object position."""
    return (longitude, latitude, distance)

# ❌ Bad (will be auto-fixed)
def calculate_position(julian_day: float, object_id: int, flags: int = 0) -> tuple[float, float, float]:
    return (longitude, latitude, distance)
```

### Type Hints

**All functions must have type hints** (enforced by mypy):

```python
# ✅ Good
def get_object(self, name: str) -> CelestialPosition | None:
    """Get a celestial object by name."""
    return self._positions.get(name)

# ❌ Bad - missing type hints
def get_object(self, name):
    return self._positions.get(name)
```

**Use modern Python 3.11+ syntax:**

- `X | Y` instead of `Union[X, Y]`
- `list[str]` instead of `List[str]`
- `dict[str, int]` instead of `Dict[str, int]`

### Imports

Use **isort** for import ordering (enforced by pre-commit):

```python
# Standard library
from datetime import datetime
from typing import Protocol

# Third-party
import pytz
from geopy.geocoders import Nominatim

# Local
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
- **Private**: Prefix with `_` (e.g., `_cached_calc_ut`)

---

## Creating Extensions

One of Stellium's strengths is extensibility. Here's how to add new functionality:

### Creating a Custom House System

Implement the `HouseSystemEngine` protocol:

```python
# In src/stellium/engines/houses.py (or your own module)

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
        """Calculate Vedic house cusps.

        Vedic houses are whole sign houses starting from the Moon's sign.
        """
        # Your calculation logic here
        cusps = [...]  # List of 12 cusp longitudes

        return HouseCusps(
            system_name=self.system_name,
            cusps=cusps,
        )

# Usage
chart = ChartBuilder.from_native(native).with_house_systems([VedicHouses()]).calculate()
```

**Key Points:**

- Implement `system_name` property
- Implement `calculate_houses()` method
- Return `HouseCusps` dataclass
- No inheritance needed!

### Creating a Custom Component

Implement the `ChartComponent` protocol:

```python
# In src/stellium/components/your_component.py

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
        """Calculate fixed star positions.

        Args:
            chart_data: Dict with chart calculation context
            config: Calculation configuration

        Returns:
            List of CelestialPosition objects for fixed stars
        """
        julian_day = chart_data["julian_day"]
        stars = []

        for star_name, star_id in FIXED_STARS.items():
            # Calculate position using Swiss Ephemeris
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

### Creating a Custom Report Section

Implement the `ReportSection` protocol:

```python
# In src/stellium/presentation/sections.py

from stellium.core.protocols import ReportSection
from rich.table import Table

class FixedStarsSection:
    """Report section for fixed stars."""

    @property
    def section_name(self) -> str:
        return "Fixed Stars"

    def build_section(self, chart: CalculatedChart) -> dict:
        """Build section data.

        Returns:
            Dict with data for rendering
        """
        stars = chart.get_component_result("Fixed Stars")

        return {
            "title": "Fixed Stars",
            "data": [
                {
                    "name": star.name,
                    "longitude": star.longitude,
                    "sign": star.sign,
                }
                for star in stars
            ]
        }

# Usage
report = (ReportBuilder()
    .from_chart(chart)
    .add_section(FixedStarsSection())
    .render(format="rich_table"))
```

### Creating a Custom Visualization Layer

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
        """Render fixed stars.

        Args:
            renderer: Chart renderer with coordinate utilities
            dwg: SVG drawing object
            chart: Calculated chart with data
        """
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

layers = [
    ZodiacLayer(),
    HouseCuspLayer(),
    PlanetLayer(),
    FixedStarsLayer(),  # Your custom layer
]

for layer in layers:
    layer.render(renderer, dwg, chart)

dwg.save()
```

---

## Documentation

### Code Documentation

- **Docstrings**: All public functions, classes, and methods must have docstrings
- **Type hints**: All function signatures must have type hints
- **Comments**: Explain *why*, not *what* (code should be self-explanatory)

```python
# ❌ Bad comment - explains what (obvious from code)
# Add 1 to the house number
house_num = house_num + 1

# ✅ Good comment - explains why
# Houses are 1-indexed in astrological tradition, but 0-indexed in our arrays
house_num = house_num + 1
```

### Examples

Add examples to the `/examples` directory:

```python
# examples/my_custom_feature.py
"""
Example demonstrating the new Fixed Stars component.
"""

from stellium import ChartBuilder, Native
from stellium.components import FixedStarsCalculator
from datetime import datetime

native = Native(datetime(1994, 1, 6, 11, 47), "Palo Alto, CA")

chart = (ChartBuilder.from_native(native)
    .add_component(FixedStarsCalculator())
    .calculate())

# Print fixed stars
stars = chart.get_component_result("Fixed Stars")
for star in stars:
    print(f"{star.name}: {star.longitude:.2f}° {star.sign}")
```

### README Updates

If your contribution adds a major feature, update the README:

- Add to feature list
- Add a progressive example
- Update comparison table if relevant

---

## Publishing to PyPI

**For maintainers only**: Instructions for publishing new releases to PyPI can be found in [docs/PUBLISHING.md](docs/PUBLISHING.md).

Key points:
- Version is defined in `src/stellium/__init__.py`
- Releases are automated via GitHub Actions
- Swiss Ephemeris data files (~3.5MB) are automatically included
- Always test on TestPyPI first for major releases

---

## Pull Request Process

### Before Submitting

Checklist:

- [ ] All tests pass (`pytest`)
- [ ] New features have tests
- [ ] Type checking passes (`mypy src/stellium`)
- [ ] Code is formatted (`pre-commit run --all-files`)
- [ ] Documentation is updated (if applicable)
- [ ] Examples are added (if applicable)

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes
- Bullet list of specific changes
- Be concise but complete

## Testing
How did you test this? What test cases did you add?

## Related Issues
Fixes #123
Related to #456

## Screenshots (if applicable)
For visual changes, add before/after screenshots.
```

### Review Process

1. **Automated checks**: CI will run tests and linting
2. **Code review**: Maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

**Review criteria:**

- Code quality and style
- Test coverage
- Documentation completeness
- Backward compatibility (breaking changes need discussion)

### After Merging

Your contribution will be included in the next release! We'll:

- Add you to the contributors list
- Credit you in the changelog
- Celebrate your contribution! 🎉

---

## Getting Help

### Questions About Contributing?

- **Architecture questions**: Read [ARCHITECTURE_QUICK_REFERENCE.md](docs/development/ARCHITECTURE_QUICK_REFERENCE.md)
- **GitHub Discussions**: Ask questions in [Discussions](https://github.com/katelouie/stellium/discussions)
- **Issues**: For bugs or feature requests, open an [issue](https://github.com/katelouie/stellium/issues)
- **Email**: Reach out to <katehlouie@gmail.com>

### Learning Resources

**Python Best Practices:**

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Protocols](https://peps.python.org/pep-0544/)
- [Dataclasses](https://docs.python.org/3/library/dataclasses.html)

**Astrology Resources:**

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/swephinfo_e.htm)
- [PySwissEph API](https://astrorigin.com/pyswisseph/sphinx/)

**Stellium Docs:**

- [USER_GUIDE.md](docs/USER_GUIDE.md) - How to use Stellium
- [ARCHITECTURE_QUICK_REFERENCE.md](docs/development/ARCHITECTURE_QUICK_REFERENCE.md) - System design

---

## Recognition

All contributors are recognized in:

- The [Contributors](https://github.com/katelouie/stellium/graphs/contributors) page
- The [CHANGELOG.md](CHANGELOG.md) for each release
- A heartfelt thank you! ❤️

---

## Final Notes

### Be Patient and Kind

- First PR? We'll help you through the process
- English not your first language? We understand
- New to astrology or Python? We're here to learn together

### Stay Curious

Contributing to open source is a learning opportunity. Don't be afraid to:

- Ask questions
- Propose ideas
- Experiment with new approaches
- Make mistakes (that's how we learn!)

### Have Fun

Building Stellium should be enjoyable. If you're stuck or frustrated, reach out. We're all in this together to create something amazing.

---

**Thank you for contributing to Stellium!** ✨

Your contributions help make computational astrology accessible to everyone. Whether you're adding a feature, fixing a bug, or improving documentation—you're making a difference.

*Happy coding, and clear skies!* 🌟
