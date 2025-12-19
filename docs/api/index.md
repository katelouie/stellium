# API Reference

Complete auto-generated API documentation from docstrings.

---

## Main Package

The main `stellium` package exports the most commonly used classes and functions.

### Builders

```{eval-rst}
.. autoclass:: stellium.ChartBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ComparisonBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ReturnBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.SynthesisBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.MultiChartBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ReportBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.PlannerBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ElectionalSearch
   :members:
   :undoc-members:
   :show-inheritance:
```

### Input Data

```{eval-rst}
.. autoclass:: stellium.Native
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.Notable
   :members:
   :undoc-members:
   :show-inheritance:
```

### Data Models

```{eval-rst}
.. autoclass:: stellium.CalculatedChart
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.core.models.UnknownTimeChart
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.CelestialPosition
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.core.models.MidpointPosition
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.FixedStarPosition
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.Aspect
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.core.models.AspectPattern
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.HouseCusps
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ChartDateTime
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ChartLocation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.PhaseData
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.MultiChart
   :members:
   :undoc-members:
   :show-inheritance:
```

### Enums

```{eval-rst}
.. autoclass:: stellium.core.models.ObjectType
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.core.models.ComparisonType
   :members:
   :undoc-members:
   :show-inheritance:
```

### Comparison Types

```{eval-rst}
.. autoclass:: stellium.Comparison
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ComparisonAspect
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.HouseOverlay
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.SynthesisChart
   :members:
   :undoc-members:
   :show-inheritance:
```

### Profections & Time Lord Techniques

```{eval-rst}
.. autoclass:: stellium.ProfectionEngine
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ProfectionResult
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.MultiProfectionResult
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.ProfectionTimeline
   :members:
   :undoc-members:
   :show-inheritance:
```

### I/O Functions

```{eval-rst}
.. autofunction:: stellium.parse_aaf
.. autofunction:: stellium.parse_csv
.. autofunction:: stellium.read_csv
.. autofunction:: stellium.parse_dataframe
.. autofunction:: stellium.read_dataframe
.. autofunction:: stellium.dataframe_from_natives
```

### Registry Functions

```{eval-rst}
.. autofunction:: stellium.get_object_info
.. autofunction:: stellium.get_aspect_info
.. autofunction:: stellium.get_fixed_star_info
.. autofunction:: stellium.get_royal_stars
.. autofunction:: stellium.get_stars_by_tier
.. autofunction:: stellium.get_notable_registry
```

---

## Core (`stellium.core`)

Core abstractions, data models, protocols, and configuration.

### Models (`stellium.core.models`)

```{eval-rst}
.. automodule:: stellium.core.models
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Native & Notable (`stellium.core.native`)

```{eval-rst}
.. automodule:: stellium.core.native
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Registry (`stellium.core.registry`)

```{eval-rst}
.. automodule:: stellium.core.registry
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Comparison (`stellium.core.comparison`)

```{eval-rst}
.. automodule:: stellium.core.comparison
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### MultiChart (`stellium.core.multichart`)

```{eval-rst}
.. automodule:: stellium.core.multichart
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Synthesis (`stellium.core.synthesis`)

```{eval-rst}
.. automodule:: stellium.core.synthesis
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Configuration (`stellium.core.config`)

```{eval-rst}
.. automodule:: stellium.core.config
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Ayanamsa (`stellium.core.ayanamsa`)

```{eval-rst}
.. automodule:: stellium.core.ayanamsa
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Chart Utilities (`stellium.core.chart_utils`)

```{eval-rst}
.. automodule:: stellium.core.chart_utils
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Protocols (`stellium.core.protocols`)

Interface definitions for extending Stellium.

```{eval-rst}
.. automodule:: stellium.core.protocols
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Engines (`stellium.engines`)

Calculation engines for ephemeris, houses, aspects, orbs, dignities, and fixed stars.

```{eval-rst}
.. automodule:: stellium.engines.ephemeris
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.houses
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.aspects
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.orbs
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.dignities
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.fixed_stars
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.patterns
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.profections
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.dispositors
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.voc
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.search
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.directions
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.engines.releasing
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Components (`stellium.components`)

Optional calculation components that can be added to charts.

```{eval-rst}
.. automodule:: stellium.components.arabic_parts
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.components.midpoints
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.components.dignity
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.components.fixed_stars
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.components.antiscia
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Presentation (`stellium.presentation`)

Report building and rendering.

```{eval-rst}
.. automodule:: stellium.presentation.sections
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.presentation.renderers
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Visualization (`stellium.visualization`)

Chart rendering and SVG generation.

```{eval-rst}
.. automodule:: stellium.visualization.core
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. autoclass:: stellium.ChartRenderer
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.builder
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.themes
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.palettes
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.layers
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.extended_canvas
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.moon_phase
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.grid
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.reference_sheet
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.ephemeris
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Atlas PDF Generation (`stellium.visualization.atlas`)

Generate multi-page PDF chart atlases.

```{eval-rst}
.. automodule:: stellium.visualization.atlas.builder
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.atlas.config
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.atlas.renderer
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

### Dial Charts (`stellium.visualization.dial`)

Uranian dial chart visualization.

```{eval-rst}
.. automodule:: stellium.visualization.dial.builder
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.dial.renderer
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.visualization.dial.config
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Returns (`stellium.returns`)

Solar, lunar, and planetary return calculations.

```{eval-rst}
.. automodule:: stellium.returns.builder
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Utilities (`stellium.utils`)

Utility functions and helpers.

```{eval-rst}
.. automodule:: stellium.utils.cache
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.time
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.chart_shape
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.progressions
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.chart_ruler
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.houses
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.utils.planetary_crossing
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Data (`stellium.data`)

Data access and notable births registry.

```{eval-rst}
.. autofunction:: stellium.data.get_notable_registry
.. autofunction:: stellium.data.get_ephe_dir
.. autofunction:: stellium.data.get_user_data_dir
.. autofunction:: stellium.data.get_user_ephe_dir
.. autofunction:: stellium.data.has_ephe_file
.. autofunction:: stellium.data.initialize_ephemeris
```

### Notable Registry (`stellium.data.registry`)

```{eval-rst}
.. automodule:: stellium.data.registry
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Planner (`stellium.planner`)

PDF planner generation with astrological data.

```{eval-rst}
.. automodule:: stellium.planner.builder
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.planner.renderer
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.planner.events
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Electional (`stellium.electional`)

Electional astrology tools for finding optimal times.

```{eval-rst}
.. automodule:: stellium.electional.intervals
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.electional.planetary_hours
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.electional.predicates
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Analysis (`stellium.analysis`)

Batch chart analysis and data processing.

```{eval-rst}
.. automodule:: stellium.analysis.batch
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.analysis.frames
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.analysis.queries
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.analysis.stats
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.analysis.export
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## I/O (`stellium.io`)

Input/output formats for chart data.

```{eval-rst}
.. automodule:: stellium.io.aaf
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.io.csv
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: stellium.io.dataframe
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
