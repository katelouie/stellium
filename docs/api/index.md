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

.. autoclass:: stellium.ReportBuilder
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

.. autoclass:: stellium.CelestialPosition
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

.. autoclass:: stellium.ComparisonType
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: stellium.SynthesisChart
   :members:
   :undoc-members:
   :show-inheritance:
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
```

---

## Protocols (`stellium.core.protocols`)

Interface definitions for extending Stellium.

```{eval-rst}
.. automodule:: stellium.core.protocols
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
```

---

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
