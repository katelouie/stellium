# Changes to Refactoring Guide

## Support Multiple House Systems

This is an excellent catch and a classic architectural pivot. Your foresight here will save you a *massive* headache later.

You are correct: the original plan creates a 1-to-1 relationship between a chart and a house system, baking the house number *into* the `CelestialPosition` object. This is inflexible.

Here is the pivot. We need to **decouple house placement from celestial position**. A planet's longitude is absolute; its house number is a relative, interpretive layer.

### The Pivot: Change Your Data Models

Your `HouseSystemEngine` protocol is actually very close. The problem is in your **`core/models.py`** and **`core/builder.py`** plans.

Here are the changes, starting from your `HouseSystemEngine` protocol:

-----

#### 1\. Modify `core/protocols.py` (Your Protocol)

Your protocol is almost perfect, but `assign_houses` should return a simple data dictionary, **not** a new list of `CelestialPosition` objects.

```python
class HouseSystemEngine(Protocol):
    # ... (system_name and calculate_cusps are perfect) ...

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> Dict[str, int]:  # <-- PIVOT 1: Change return type
        """
        Assign house numbers to celestial positions.

        Args:
            positions: Celestial objects to assign houses
            cusps: House cusps to use for assignment

        Returns:
            A dictionary of {object_name: house_number}
        """
        ...
```

-----

#### 2\. Modify `core/models.py` (The Core Data)

This is the most important change. The `CalculatedChart` will hold *all* house data, and the `CelestialPosition` will hold *none* of it.

* **In `CelestialPosition`:**

  * **Remove** the `house: Optional[int] = None` attribute. A position object no longer knows what house it's in.

* **In `CalculatedChart`:**

  * **Change** `houses: HouseCusps` to `house_systems: Dict[str, HouseCusps] = field(default_factory=dict)`. This will store the cusp data for *all* calculated systems, keyed by name (e.g., "Placidus").
  * **Add** a new field: `house_placements: Dict[str, Dict[str, int]] = field(default_factory=dict)`. This will store the final house numbers, keyed by system name, then object name (e.g., `chart.placements["Placidus"]["Sun"]` -\> `10`).
  * **Add** a helper method for easy access:

    <!-- end list -->

    ```python
    @dataclass(frozen=True)
    class CalculatedChart:
        # ... (datetime, location, positions) ...
        # aspects: tuple[Aspect, ...] = ()

        # PIVOT 2: Store multiple house systems and their placements
        house_systems: Dict[str, HouseCusps] = field(default_factory=dict)
        house_placements: Dict[str, Dict[str, int]] = field(default_factory=dict)

        # ... (metadata) ...

        def get_house(self, object_name: str, system_name: str) -> Optional[int]:
            """
            Helper method to get the house number for a specific object
            in a specific system.
            """
            return self.house_placements.get(system_name, {}).get(object_name)

    # ... (rest of your models) ...
    ```

-----

#### 3\. Modify `core/builder.py` (The "How")

Your `ChartBuilder` will now manage a *list* of house engines instead of just one.

* **In `ChartBuilder.__init__`:**

  * **Change** `self._houses = PlacidusHouses()` to `self._house_engines: List[HouseSystemEngine] = [PlacidusHouses()]`. (It's now a list with one default).

* **In `ChartBuilder`'s fluent methods:**

  * **Change** `with_houses(self, engine)` to *replace* the default list:

    ```python
    def with_house_systems(self, engines: List[HouseSystemEngine]) -> 'ChartBuilder':
        """Set the house system(s) to be calculated."""
        if not engines:
            raise ValueError("House engine list cannot be empty.")
        self._house_engines = engines
        return self
    ```

  * *Alternatively*, you could keep `with_houses` (for the *primary* system) and add an `add_house_system` method. Your call, but the list approach is cleaner.

* **In `ChartBuilder.calculate()`:**

  * **Replace** "Step 2" and "Step 3" from your plan with this new logic:

    <!-- end list -->

    ```python
    # ... (Step 1: Calculate positions) ...

    # Step 2: Calculate all house systems
    house_systems_map: Dict[str, HouseCusps] = {}
    for engine in self._house_engines:
        system_name = engine.system_name
        if system_name in house_systems_map:
            continue # Avoid duplicate calculations
        house_systems_map[system_name] = engine.calculate_cusps(
            self._datetime, self._location
        )

    # ... (Step 4: Add angles, Step 5: Run components) ...
    # Now the 'positions' list is complete.

    # Step 6 (New): Assign houses for all systems
    house_placements_map: Dict[str, Dict[str, int]] = {}
    for engine in self._house_engines:
        system_name = engine.system_name
        cusps = house_systems_map[system_name]

        # Call the protocol method to get the {object_name: house_num} dict
        placements = engine.assign_houses(positions, cusps)
        house_placements_map[system_name] = placements

    # ... (Step 7: Calculate aspects) ...

    # Step 8 (Final): Build the chart
    return CalculatedChart(
        datetime=self._datetime,
        location=self._location,
        positions=tuple(positions),
        aspects=tuple(aspects),
        house_systems=house_systems_map,       # <-- Pass the map of cusps
        house_placements=house_placements_map, # <-- Pass the map of placements
    )
    ```

### Summary of Your Pivot

1. **`CelestialPosition`** no longer stores a `house`.
2. **`HouseSystemEngine.assign_houses`** now returns a `Dict[str, int]` (a simple lookup map) instead of a modified list.
3. **`CalculatedChart`** now stores a `Dict` of all house cusps and a `Dict` of all house placements.
4. **`ChartBuilder`** now loops through a *list* of `HouseSystemEngine`s to populate these dictionaries.

This makes your architecture far more flexible and robust. You can now calculate Placidus, Whole Sign, and Koch all in one go and store them cleanly in a single, immutable `CalculatedChart` object.

Does this pivot make sense? We can move on to the `engines/houses.py` (Day 4) implementation if you're ready.

This is a fantastic question, and you've hit on two key areas.

No, the previous answer wasn't *quite* everything. The pivot we discussed for the **protocol** (Day 2) has a direct impact on the **implementation** (Day 4) that's worth showing you.

And your quibble about `AspectEngine` is 100% correct. A simple `dict` is not powerful enough. This is a brilliant and necessary pivot.

Let's solve both.

## 1\. The Final Piece of the House Pivot

You are correct, the protocol and model changes are the hard part. The last step is seeing how that pivot simplifies your *implementation* from the Day 4 plan (`src/stellium/engines/houses.py`).

Your `assign_houses` methods no longer need to create new `CelestialPosition` objects. They just run a simple loop and return a dictionary. It's much cleaner.

Here is the "after" picture for your house engines:

**File**: `src/stellium/engines/houses.py`

```python
# ... (imports, including 'replace' from dataclasses) ...

# --- PlacidusHouses ---
class PlacidusHouses:
    @property
    def system_name(self) -> str:
        return "Placidus"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        # ... (your swe.houses() logic is perfect here) ...
        # [Implementation from your Day 4 plan is unchanged]

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> Dict[str, int]:
        """
        NEW IMPLEMENTATION: Returns a simple {name: house} dictionary.
        """
        placements = {}
        for pos in positions:
            house_num = self._find_house(pos.longitude, cusps.cusps)
            placements[pos.name] = house_num
        return placements

    def _find_house(self, longitude: float, cusps: tuple) -> int:
        """Find which house a longitude falls in."""
        cusp_list = list(cusps)

        for i in range(12):
            cusp1 = cusp_list[i]
            cusp2 = cusp_list[(i + 1) % 12]

            # Handle wrapping around 360°
            if cusp2 < cusp1:
                cusp2 += 360
                test_long = longitude if longitude >= cusp1 else longitude + 360
            else:
                test_long = longitude

            if cusp1 <= test_long < cusp2:
                return i + 1
        return 1  # Fallback


# --- WholeSignHouses ---
class WholeSignHouses:
    @property
    def system_name(self) -> str:
        return "Whole Sign"

    def calculate_cusps(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> HouseCusps:
        # ... (your Day 4 logic for this is perfect) ...
        # [Implementation from your Day 4 plan is unchanged]

    def assign_houses(
        self,
        positions: List[CelestialPosition],
        cusps: HouseCusps,
    ) -> Dict[str, int]:
        """
        NEW IMPLEMENTATION: Also returns a simple {name: house} dictionary.
        This logic is now much simpler.
        """
        placements = {}

        # Get the sign of the 1st house cusp
        cusp0_sign = int(cusps.cusps[0] // 30)

        for pos in positions:
            # The sign of the planet determines its house
            planet_sign = int(pos.longitude // 30)
            house_num = ((planet_sign - cusp0_sign) % 12) + 1
            placements[pos.name] = house_num

        return placements
```

**Now** you have everything for the house pivot. It's a much more robust design.

-----

## 2\. Your Aspect Orb "Quibble" (Pivot 3)

You are absolutely right. This is a critical insight. Real-world orb calculation is complex, and your protocol should support it.

The solution is to use the same pattern you've applied everywhere else: **if the logic is complex, encapsulate it in an engine.**

Instead of a simple `dict`, your `AspectEngine` should accept an `OrbEngine`.

### Step 1: Add a New `OrbEngine` Protocol

Add this to `src/stellium/core/protocols.py`.

```python
class OrbEngine(Protocol):
    """
    Protocol for orb calculation.

    Encapsulates logic for determining orb allowance,
    which can be simple (by aspect) or complex (by planet,
    by planet pair, by day/night, etc.).
    """

    def get_orb_allowance(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str,
    ) -> float:
        """
        Get the allowed orb for a specific aspect between two objects.

        Args:
            obj1: The first celestial object.
            obj2: The second celestial object.
            aspect_name: The name of the aspect (e.g., "Square").

        Returns:
            The maximum allowed orb in degrees.
        """
        ...
```

### Step 2: Update Your `AspectEngine` Protocol

In `src/stellium/core/protocols.py`, change the `calculate_aspects` signature.

* **From this:**

    ```python
    def calculate_aspects(
        self,
        positions: List[CelestialPosition],
        orb_config: Optional[Dict[str, float]] = None,
    ) -> List[Aspect]:
    ```

* **To this:**

    ```python
    def calculate_aspects(
        self,
        positions: List[CelestialPosition],
        orb_engine: OrbEngine,  # <-- PIVOT: Pass an engine, not a dict
    ) -> List[Aspect]:
    ```

### Step 3: Update `ChartBuilder` (Day 5)

Your `ChartBuilder` will need to be aware of this. It will hold a default `OrbEngine` and pass it to the `AspectEngine`.

* **In `ChartBuilder.__init__`:**
  * Add `self._orb_engine: OrbEngine = SimpleOrbEngine()` (We'll define `SimpleOrbEngine` below).
* **Add a new `with_orbs` method:**

    ```python
    def with_orbs(self, engine: OrbEngine) -> 'ChartBuilder':
        """Set the orb calculation engine."""
        self._orb_engine = engine
        return self
    ```

* **In `ChartBuilder.calculate()` (Step 6):**
  * Change the aspect calculation to pass the orb engine.
    <!-- end list -->
    ```python
    # Step 6: Calculate aspects (if engine provided)
    aspects = []
    if self._aspect_engine:
        aspects = self._aspect_engine.calculate_aspects(
            positions,
            self._orb_engine,  # <-- Pass the configured orb engine
        )
    ```

### Step 4: Create Orb Engine Implementations

Now for the fun part. You can create different orb engines. These would live in a new file, `src/stellium/engines/orbs.py`.

```python
# File: src/stellium/engines/orbs.py

from stellium.core.models import CelestialPosition

class SimpleOrbEngine:
    """
    Implements OrbEngine for simple aspect-based orbs.
    This matches the functionality of your original plan.
    """
    def __init__(self, orb_map: Optional[Dict[str, float]] = None):
        self._orbs = orb_map or {
            'Conjunction': 8.0,
            'Sextile': 6.0,
            'Square': 8.0,
            'Trine': 8.0,
            'Opposition': 8.0,
        }
        self._default_orb = 8.0

    def get_orb_allowance(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str,
    ) -> float:
        return self._orbs.get(aspect_name, self._default_orb)


class MatrixOrbEngine:
    """
    Implements OrbEngine for complex, planet-pair-based orbs.
    This solves your "quibble" directly.
    """
    def __init__(self, orb_matrix: Dict[str, Dict[str, float]]):
        # A complex matrix, e.g.:
        # {
        #   "Sun-Moon": {"Square": 10.0, "Trine": 10.0, "default": 8.0},
        #   "Sun-Mars": {"default": 7.0},
        #   "default": {"Square": 6.0, "default": 5.0}
        # }
        self._matrix = orb_matrix

    def get_orb_allowance(
        self,
        obj1: CelestialPosition,
        obj2: CelestialPosition,
        aspect_name: str,
    ) -> float:
        # Create sorted key for pairs, e.g., "Moon-Sun"
        key = "-".join(sorted([obj1.name, obj2.name]))

        # 1. Check for specific pair rule (e.g., "Moon-Sun")
        if key in self._matrix:
            pair_rules = self._matrix[key]
            return pair_rules.get(aspect_name, pair_rules.get("default", 5.0))

        # 2. No specific pair? Check for default aspect rule
        default_rules = self._matrix.get("default", {})
        return default_rules.get(aspect_name, default_rules.get("default", 5.0))
```

This pivot makes your `AspectEngine` protocol incredibly powerful and flexible, allowing a user to define any orb system they want—from simple to ridiculously complex—just by passing in a different `OrbEngine`.

---

Yes, you absolutely need to adjust this file. Your pivots for **House Systems** and **Orb Engines** have made parts of this config file obsolete.

This is a great cleanup step that will make your architecture much cleaner.

Here’s the breakdown of what to change and why.

-----

### 1\. `AspectConfig` Pivot

Your `AspectConfig` is trying to do two jobs:

1. Define *which* aspects to find (e.g., 'Square' = 90°).
2. Define the *orbs* for those aspects (e.g., 'Square' = 8.0°).

You correctly identified that the orb logic is complex and should be in a separate `OrbEngine`. Therefore, this config should *only* do job \#1.

**BEFORE:**

```python
@dataclass
class AspectConfig:
    aspects: Dict[str, int] = ...
    orbs: Dict[str, float] = ... # <-- Problem
    include_angles: bool = True
    include_asteroids: bool = True

    @classmethod
    def tight(cls) -> 'AspectConfig': ... # <-- Obsolete
    @classmethod
    def wide(cls) -> 'AspectConfig': ... # <-- Obsolete
```

**AFTER (Your New `config.py`):**

```python
@dataclass
class AspectConfig:
    """
    Configuration for *which* aspects to find.
    This is passed to an AspectEngine.
    """

    # Which aspects to calculate and their angles
    aspects: Dict[str, int] = field(default_factory=lambda: {
        'Conjunction': 0,
        'Sextile': 60,
        'Square': 90,
        'Trine': 120,
        'Opposition': 180,
    })

    # Which object types to include in aspect calculations
    # (The AspectEngine will use this to filter pairs)
    include_angles: bool = True
    include_asteroids: bool = True

    # --- REMOVED orbs, tight(), and wide() ---
    # REASON: Orb logic is now handled by the swappable OrbEngine
    # passed to the ChartBuilder.
```

-----

### 2\. `CalculationConfig` Pivot

This class has two fields that are now obsolete because of your pivots.

1. `aspect_config: AspectConfig`: This is now a bit "clunky." It's cleaner to pass the `AspectConfig` directly into the `ModernAspectEngine`'s constructor, not bundle it with the general calculation config.
2. `house_system: str = "Placidus"`: This is **definitely obsolete**. Your `ChartBuilder` now takes a *list of house engines*, not a single string.

**BEFORE:**

```python
@dataclass
class CalculationConfig:
    include_planets: List[str] = ...
    # ... other includes
    aspect_config: AspectConfig = ... # <-- Clunky
    house_system: str = "Placidus"  # <-- Obsolete
```

**AFTER (Your New `config.py`):**

```python
@dataclass
class CalculationConfig:
    """
    Overall configuration for *which data to calculate*.
    This is passed to the ChartBuilder with .with_config()
    """

    # Which objects to calculate
    include_planets: List[str] = field(default_factory=lambda: [
        'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
        'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
    ])
    include_nodes: bool = True
    include_chiron: bool = True
    include_asteroids: List[str] = field(default_factory=list) # Default empty

    # --- REMOVED aspect_config ---
    # REASON: AspectConfig is now passed directly to the
    # AspectEngine's constructor, not here.

    # --- REMOVED house_system ---
    # REASON: House systems are now engines configured on the
    # ChartBuilder with .with_house_systems()

    @classmethod
    def minimal(cls) -> 'CalculationConfig':
        """Minimal calculation - planets only."""
        return cls(
            include_nodes=False,
            include_chiron=False,
            include_asteroids=[],
        )

    @classmethod
    def comprehensive(cls) -> 'CalculationConfig':
        """Comprehensive calculation - everything."""
        return cls(
            include_nodes=True,
            include_chiron=True,
            include_asteroids=['Chiron', 'Pholus', 'Ceres', 'Pallas', 'Juno', 'Vesta'],
        )
```

### How to Use These New Configs

This new structure is much cleaner and enforces the **Separation of Concerns** principle from your philosophy.

1. **`CalculationConfig`** is passed to the builder. The builder uses it to tell the `EphemerisEngine` what objects to calculate.

    ```python
    # User wants a minimal chart
    minimal_config = CalculationConfig.minimal()

    builder = ChartBuilder.from_datetime(dt, loc) \
                   .with_config(minimal_config)
    ```

2. **`AspectConfig`** is passed directly to the `AspectEngine` that needs it (like your `ModernAspectEngine` from Day 6).

    ```python
    # User wants to include minor aspects
    minor_aspects = AspectConfig(aspects={
        'Conjunction': 0, 'Sextile': 60, 'Square': 90,
        'Trine': 120, 'Opposition': 180, 'Quincunx': 150
    })

    builder.with_aspects(ModernAspectEngine(config=minor_aspects))
    ```

This approach is far more flexible and solves all the issues you raised.

---

You are absolutely right. That's a key piece of data that was completely missed in the Day 5 plan for the `ChartBuilder`.

My recommendation is to include the "big three": **Ascendant**, **MC**, and **Vertex**. You can then derive the Descendant and IC from the ASC/MC, giving you the five most common angles.

This is a great catch, and it requires a small architectural pivot to be efficient.

### The Architectural Pivot 💡

Your idea to add a `calculate_angles` method is correct, but it would be inefficient. The `swe.houses()` function returns *both* cusps and angles in a single call.

* `calculate_cusps()` would call `swe.houses()` and *only* use the cusps.
* `calculate_angles()` would call `swe.houses()` *again* and *only* use the angles.

**The Solution:** Change the `HouseSystemEngine` protocol to use a single, more efficient method that returns *both* pieces of data from the one `swe.houses()` call.

-----

### 1\. Update Your Protocol (`core/protocols.py`)

Replace the `calculate_cusps` method on your `HouseSystemEngine` protocol with this:

```python
from typing import Tuple, List
# ... other imports

class HouseSystemEngine(Protocol):
    # ... (system_name property is the same) ...

    # PIVOT: This method replaces calculate_cusps
    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> Tuple[HouseCusps, List[CelestialPosition]]:
        """
        Calculates both house cusps AND chart angles.
        This is the primary data generation method for a house system.

        Args:
            datetime: Chart datetime
            location: Chart location

        Returns:
            A tuple containing:
            1. A HouseCusps object (for this specific system)
            2. A List of CelestialPosition objects for the primary angles
               (ASC, MC, DSC, IC, Vertex)
        """
        ...

    # ... (assign_houses method is the same) ...
```

-----

### 2\. Update Your Implementation (`engines/houses.py`)

Now, your `PlacidusHouses` (and other engines) will implement this new method. They will call `swe.houses()` *once* and use all the data.

```python
# In src/stellium/engines/houses.py

import swisseph as swe
from stellium.core.models import (
    HouseCusps,
    CelestialPosition,
    ObjectType,
    # ... etc
)

class PlacidusHouses:
    @property
    def system_name(self) -> str:
        return "Placidus"

    # This is the new, combined method
    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> Tuple[HouseCusps, List[CelestialPosition]]:

        # 1. Call swe.houses() ONE time
        julian_day = datetime.julian_day
        lat = location.latitude
        lon = location.longitude

        # Call with Placidus code (b'P')
        cusps_list, ascmc = swe.houses(julian_day, lat, lon, hsys=b'P')

        # 2. Create the HouseCusps object
        house_cusps = HouseCusps(
            system=self.system_name,
            cusps=tuple(cusps_list)
        )

        # 3. Create the CelestialPosition objects for angles
        asc = ascmc[0]
        mc = ascmc[1]
        vertex = ascmc[3]

        angles = [
            CelestialPosition(
                name='ASC',
                object_type=ObjectType.ANGLE,
                longitude=asc,
            ),
            CelestialPosition(
                name='MC',
                object_type=ObjectType.ANGLE,
                longitude=mc,
            ),
            # As you planned, derive the DSC and IC
            CelestialPosition(
                name='DSC',
                object_type=ObjectType.ANGLE,
                longitude=(asc + 180) % 360,
            ),
            CelestialPosition(
                name='IC',
                object_type=ObjectType.ANGLE,
                longitude=(mc + 180) % 360,
            ),
            # And include the Vertex
            CelestialPosition(
                name='Vertex',
                object_type=ObjectType.ANGLE,
                longitude=vertex,
            ),
        ]

        return (house_cusps, angles)

    # ... (assign_houses method is unchanged) ...


class WholeSignHouses:
    @property
    def system_name(self) -> str:
        return "Whole Sign"

    def calculate_house_data(
        self,
        datetime: ChartDateTime,
        location: ChartLocation,
    ) -> Tuple[HouseCusps, List[CelestialPosition]]:

        # 1. Call swe.houses() to get angles
        # NOTE: We still need the ASC/MC from Placidus (or any)
        # to calculate Whole Sign cusps and find the angles.
        julian_day = datetime.julian_day
        lat = location.latitude
        lon = location.longitude

        # We use 'P' just to get the ascmc data
        _, ascmc = swe.houses(julian_day, lat, lon, hsys=b'P')

        # 2. Create Whole Sign cusps
        asc_long = ascmc[0]
        asc_sign_start = (asc_long // 30) * 30

        whole_sign_cusps = tuple(
            (asc_sign_start + (i * 30)) % 360 for i in range(12)
        )

        house_cusps = HouseCusps(
            system=self.system_name,
            cusps=whole_sign_cusps
        )

        # 3. Create angles (same as Placidus)
        asc = ascmc[0]
        mc = ascmc[1]
        vertex = ascmc[3]

        angles = [
            CelestialPosition(name='ASC', object_type=ObjectType.ANGLE, longitude=asc),
            CelestialPosition(name='MC', object_type=ObjectType.ANGLE, longitude=mc),
            CelestialPosition(name='DSC', object_type=ObjectType.ANGLE, longitude=(asc + 180) % 360),
            CelestialPosition(name='IC', object_type=ObjectType.ANGLE, longitude=(mc + 180) % 360),
            CelestialPosition(name='Vertex', object_type=ObjectType.ANGLE, longitude=vertex),
        ]

        return (house_cusps, angles)

    # ... (assign_houses method is unchanged) ...
```

-----

### 3\. Update Your `ChartBuilder` (`core/builder.py`)

Finally, update your `calculate` method in `ChartBuilder` to use this new protocol.

```python
# In ChartBuilder.calculate() method:

    # ... (Step 1: Calculate planetary positions is the same) ...
    # positions = self._ephemeris.calculate_positions(...)

    # Step 2: Calculate all house systems AND angles
    house_systems_map: Dict[str, HouseCusps] = {}
    calculated_angles: List[CelestialPosition] = [] # Store angles here

    for engine in self._house_engines:
        system_name = engine.system_name
        if system_name in house_systems_map:
            continue # Already calculated

        # Call the new, efficient protocol method
        cusps, angles = engine.calculate_house_data(
            self._datetime, self._location
        )

        house_systems_map[system_name] = cusps

        # Only add the angles ONCE
        # (ASC is the same regardless of house system)
        if not calculated_angles:
            calculated_angles = angles

    # Step 3: Add chart angles to the main positions list
    # (This replaces the old, forgotten "Step 4" from the plan)
    positions.extend(calculated_angles)

    # Step 4: Run additional components (Arabic parts, etc.)
    # (This was Step 5 in the old plan)
    for component in self._components:
        # ... (this logic is unchanged) ...

    # Step 5: Assign houses for all systems
    # (This was Step 6 in the old plan)
    house_placements_map: Dict[str, Dict[str, int]] = {}
    # ... (this logic is unchanged) ...

    # Step 6: Calculate aspects
    # (This was Step 7 in the old plan)
    # ... (this logic is unchanged) ...

    # Step 7: Build final chart
    # (This was Step 8 in the old plan)
    return CalculatedChart(
        # ...
        positions=tuple(positions),
        house_systems=house_systems_map,
        house_placements=house_placements_map,
        aspects=tuple(aspects),
    )
```

This pivot is more efficient, solves the missing angles problem, and keeps your `HouseSystemEngine` as the single source of truth for all house and angle data.
