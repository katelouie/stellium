# 🏗️ Stellium Architecture Quick Reference

A one-page reference for key architectural patterns and decisions.

---

## Core Principles

```python
# ✅ DO: Immutable data
@dataclass(frozen=True)
class CelestialPosition:
    longitude: float
    # Once created, can't be modified

# ❌ DON'T: Mutable state
class CelestialPosition:
    def __init__(self):
        self.longitude = 0  # Can be changed later
```

```python
# ✅ DO: Dependency injection
chart = ChartBuilder.from_datetime(dt, loc) \
    .with_ephemeris(SwissEphemerisEngine()) \
    .with_houses(PlacidusHouses()) \
    .calculate()

# ❌ DON'T: Hidden dependencies
class Chart:
    def __init__(self):
        self.ephemeris = SwissEphemerisEngine()  # Hardcoded
```

```python
# ✅ DO: Protocol-based interfaces
class EphemerisEngine(Protocol):
    def calculate_positions(...) -> List[CelestialPosition]: ...

# ❌ DON'T: Abstract base classes (unless needed)
class EphemerisEngine(ABC):
    @abstractmethod
    def calculate_positions(...): ...
```

---

## Data Flow

```
User Request
    ↓
ChartBuilder (API layer)
    ↓
Engines (calculation layer)
    ├── EphemerisEngine → CelestialPosition[]
    ├── HouseSystemEngine → HouseCusps
    └── AspectEngine → Aspect[]
    ↓
CalculatedChart (immutable result)
    ↓
Presentation/Drawing/Export
```

---

## Directory Structure

```
src/stellium/
├── core/                    # Core abstractions
│   ├── models.py           # Data classes (immutable)
│   ├── protocols.py        # Interfaces (Protocol)
│   ├── builder.py          # ChartBuilder (API)
│   └── config.py           # Configuration
│
├── engines/                 # Calculation engines
│   ├── ephemeris.py        # Planet positions
│   ├── houses.py           # House systems
│   ├── aspects.py          # Aspect calculation
│   └── dignities.py        # Dignity calculation
│
├── components/              # Optional components
│   ├── arabic_parts.py     # Arabic parts
│   ├── midpoints.py        # Midpoints
│   └── patterns.py         # Pattern detection
│
└── utils/                   # Utilities
    ├── cache.py            # Caching
    └── coordinates.py      # Location/timezone
```

---

## Key Patterns

### 1. Builder Pattern

```python
# Fluent interface for construction
chart = ChartBuilder.from_datetime(dt, location) \
    .with_houses(PlacidusHouses()) \
    .with_aspects(ModernAspectEngine()) \
    .with_config(CalculationConfig.minimal()) \
    .add_component(ArabicPartsCalculator()) \
    .calculate()
```

### 2. Protocol-Based Polymorphism

```python
# Any class matching this signature works
class EphemerisEngine(Protocol):
    def calculate_positions(...) -> List[CelestialPosition]: ...

# Concrete implementations
class SwissEphemerisEngine: ...
class MockEphemerisEngine: ...
class JPLEphemerisEngine: ...  # Future

# All work the same way
builder.with_ephemeris(SwissEphemerisEngine())
builder.with_ephemeris(MockEphemerisEngine())
```

### 3. Immutable Results

```python
# Results can't be modified
chart = builder.calculate()

# This fails:
chart.positions[0].longitude = 999  # FrozenInstanceError

# Instead, create new objects:
new_pos = replace(chart.positions[0], longitude=999)
```

### 4. Type Safety

```python
# Use type hints everywhere
def calculate_positions(
    self,
    datetime: ChartDateTime,  # Not just 'datetime'
    location: ChartLocation,  # Not tuple
) -> List[CelestialPosition]:  # Not list
    ...
```

---

## Common Code Patterns

### Creating a New Engine

```python
# 1. Define what it does
class MyHouseSystemEngine:
    @property
    def system_name(self) -> str:
        return "My System"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        # Your calculation logic
        cusps = [...]
        return HouseCusps(system=self.system_name, cusps=tuple(cusps))

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> List[CelestialPosition]:
        # Your assignment logic
        ...

# 2. Use it
chart = ChartBuilder.from_datetime(dt, loc) \
    .with_houses(MyHouseSystemEngine()) \
    .calculate()
```

### Working with Immutable Data

```python
# Can't modify, must create new
from dataclasses import replace

old_pos = CelestialPosition(name="Sun", longitude=30.0, ...)

# Create modified copy
new_pos = replace(old_pos, longitude=45.0)

# Original unchanged
assert old_pos.longitude == 30.0
assert new_pos.longitude == 45.0
```

### Adding Caching

```python
from stellium.cache import cached

class MyEngine:
    @cached(cache_type="ephemeris", max_age_seconds=86400)
    def expensive_calculation(self, param1, param2):
        # Expensive work here
        return result

# First call: calculates and caches
# Second call with same params: returns cached result
```

---

## Testing Patterns

### Unit Test

```python
def test_celestial_position():
    pos = CelestialPosition(
        name="Sun",
        object_type=ObjectType.PLANET,
        longitude=45.5,
    )
    assert pos.sign == "Taurus"
    assert pos.is_retrograde == False
```

### Integration Test

```python
def test_full_chart():
    chart = ChartBuilder.from_datetime(dt, loc).calculate()
    assert len(chart.positions) > 10
    assert chart.get_object('Sun') is not None
```

### Using Mock Engine

```python
def test_aspect_calculation():
    # Don't calculate real positions, use mock
    engine = MockEphemerisEngine({
        'Sun': 0.0,
        'Moon': 120.0,  # Trine to Sun
    })

    chart = ChartBuilder.from_datetime(dt, loc) \
        .with_ephemeris(engine) \
        .with_aspects(ModernAspectEngine()) \
        .calculate()

    # Test aspect logic without ephemeris complexity
    assert len(chart.aspects) > 0
```

---

## Anti-Patterns to Avoid

### ❌ Modifying After Creation

```python
# DON'T
chart = builder.calculate()
chart.positions[0].longitude = 999  # Fails (frozen)

# DO
# Create new chart with different configuration
```

### ❌ Circular Dependencies

```python
# DON'T
# core/models.py
from stellium.engines.ephemeris import SwissEphemeris  # ❌

# DO
# core/models.py has no engine imports
# engines/ephemeris.py imports from core.models  # ✅
```

### ❌ Hidden State

```python
# DON'T
class ChartBuilder:
    _cache = {}  # Class-level cache
    def calculate(self):
        if self._datetime in self._cache:  # Hidden behavior
            return self._cache[self._datetime]

# DO
# Make caching explicit in the engine layer
@cached(cache_type="ephemeris")
def calculate_positions(...):
    ...
```

### ❌ Tight Coupling

```python
# DON'T
class Chart:
    def __init__(self):
        self.ephemeris = SwissEphemerisEngine()  # Hardcoded

# DO
class ChartBuilder:
    def with_ephemeris(self, engine):  # Injectable
        self._ephemeris = engine
```

---

## Quick Decision Guide

### "Should I create a new Protocol?"

**Yes** if:
- Multiple implementations will exist
- You want to allow user extensions
- Different algorithms for same task

**No** if:
- Only one implementation
- Internal utility
- Tightly coupled to specific engine

### "Should this be immutable?"

**Yes** if:
- It's a result/output
- It's shared between components
- It represents a point-in-time snapshot

**No** if:
- It's a builder
- It's internal state
- It's a cache

### "Should I use the Builder?"

**Yes** for:
- Chart construction
- Complex objects with many options
- Fluent configuration

**No** for:
- Simple data classes
- Engine internals
- Utility functions

---

## Performance Tips

1. **Cache expensive operations**
   ```python
   @cached(cache_type="ephemeris")
   def calculate_positions(...):
   ```

2. **Use MockEphemerisEngine for non-calculation tests**
   ```python
   .with_ephemeris(MockEphemerisEngine())
   ```

3. **Minimize Swiss Ephemeris calls**
   ```python
   # ✅ One call per object (cached)
   @cached(...)
   def _calculate_single_position(...):

   # ❌ Multiple calls for same object
   def calculate_positions(...):
       for obj in objects:
           result1 = swe.calc_ut(...)
           result2 = swe.calc_ut(...)  # Duplicate
   ```

4. **Batch when possible**
   ```python
   # ✅ Calculate all at once
   positions = ephemeris.calculate_positions(dt, loc, ['Sun', 'Moon', ...])

   # ❌ One at a time
   sun = ephemeris.calculate_positions(dt, loc, ['Sun'])
   moon = ephemeris.calculate_positions(dt, loc, ['Moon'])
   ```

---

## Debugging Tips

```python
# Print chart structure
chart = builder.calculate()
print(chart.to_dict())

# Check what's being calculated
import logging
logging.basicConfig(level=logging.DEBUG)

# Verify immutability
from dataclasses import fields
print(fields(CelestialPosition))

# Test caching
from stellium.cache import cache_info
print(cache_info())
```

---

## Common Gotchas

1. **Datetime must be timezone-aware**
   ```python
   # ❌ Naive datetime
   dt = datetime(2000, 1, 1, 12, 0)

   # ✅ Timezone-aware
   dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
   ```

2. **Dataclass frozen means ALL fields**
   ```python
   @dataclass(frozen=True)
   class Foo:
       x: int
       y: List[int]  # Still frozen, but list contents can change!

   # Use tuple instead
   y: tuple[int, ...]  # Truly immutable
   ```

3. **Protocol doesn't enforce implementation**
   ```python
   # Protocol defines interface
   class MyEngine(Protocol):
       def calculate(...): ...

   # But this "implements" it without inheriting
   class ConcreteEngine:  # No (MyEngine) needed
       def calculate(...):  # Just match signature
           ...
   ```

---

## Reference Links

- Vision: `docs/planning/VISION_ARCHITECTURE.md`
- Tutorial: `docs/development/REFACTORING_GUIDE.md`
- Checklist: `docs/development/REFACTOR_CHECKLIST.md`
- Migration: `docs/development/MIGRATION.md`

---

**Keep this handy while coding!** 📖
