# Starlight User Guide - WORK IN PROGRESS

## Installation

```bash
pip install starlight-astro
```

## Quick Start

### Calculate a Natal Chart

```python
from datetime import datetime
import pytz
from starlight.core.builder import ChartBuilder
from starlight.core.native import Native

# Create a native
birthday = datetime(1994, 1, 6, 19, 47)
location = "San Francisco, CA"
native = Native(birthday, location)

# Create a chart
chart = ChartBuilder.from_native(native).calculate()

# Access planetary positions
for planet in chart.get_planets():
    print(f"{planet.name}: {planet.sign_position} in House {planet.house}")

# Access aspects
for aspect in chart.aspects:
    print(aspect.description)
```

### Custom House Systems

```python
from starlight.engines.houses import WholeSignHouses

chart = (
    ChartBuilder.from_native(native)
    .with_houses(WholeSignHouses())
    .calculate()
)

print(f"Using {chart.default_house_system} houses")
```

### Export to JSON

```python
import json

data = chart.to_dict()
with open('chart.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Advanced Usage

### Custom Aspect Calculations

```python
from starlight.engines.aspects import ModernAspectEngine, HarmonicAspectEngine
from starlight.engines.orbs import SimpleOrbEngine

# Traditional aspects
chart = ChartBuilder.from_native(native) \
    .with_aspects(ModernAspectEngine()) \
    .with_orbs(SimpleOrbEngine())
    .calculate()

# Harmonic aspects (septiles, noviles, etc.)
chart = ChartBuilder.from_native(native) \
    .with_aspects(HarmonicAspectEngine(harmonic=7)) \
    .with_orbs(SimpleOrbEngine())
    .calculate()
```

### Configuration Presets

```python
from starlight.core.config import CalculationConfig

# Minimal calculation (faster)
config = CalculationConfig.minimal()

chart = ChartBuilder.from_native(native) \
    .with_config(config) \
    .calculate()
```

## Working with Results

### Finding Specific Objects

```python
sun = chart.get_object('Sun')
print(f"Sun: {sun.longitude}° {sun.sign}")
print(f"Retrograde: {sun.is_retrograde}")
```

### Filtering by Type

```python
# Just planets
planets = chart.get_planets()

# Just angles
angles = chart.get_angles()
```

## Next Steps

- See [API Reference] for complete documentation
- See [Examples] for more use cases
- See [Developer Guide] to extend Starlight
