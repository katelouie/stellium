# API Reference

Generated from the source docstrings — the single source of truth for the whole
package. Every object is documented **once**, on the page for the module that defines
it, and linked from here.

:::{container} st-panel
New to the library? Start with {py:class}`~stellium.core.builder.ChartBuilder`. Almost
everything else is something you hand to it, or something it hands back.
:::

## The public surface

These are the names exported from the top-level `stellium` package — what
`from stellium import ...` gives you.

### Builders

| Class | What it builds |
|---|---|
| {py:class}`~stellium.core.builder.ChartBuilder` | A single chart — the main entry point |
| {py:class}`~stellium.core.comparison.ComparisonBuilder` | Synastry, transits, composite, Davison |
| {py:class}`~stellium.returns.builder.ReturnBuilder` | Solar, lunar and planetary returns |
| {py:class}`~stellium.core.multichart.MultiChartBuilder` | Bi-, tri- and quad-wheels |
| {py:class}`~stellium.core.synthesis.SynthesisBuilder` | A synthesised chart from several |
| {py:class}`~stellium.presentation.builder.ReportBuilder` | Terminal, Markdown, HTML and PDF reports |
| {py:class}`~stellium.planner.builder.PlannerBuilder` | Personalized PDF planners |
| {py:class}`~stellium.electional.ElectionalSearch` | A time that satisfies your predicates |

### Input

| Object | Use it for |
|---|---|
| {py:class}`~stellium.core.native.Native` | Birth data you supply — datetime, place or coordinates |
| {py:class}`~stellium.core.native.Notable` | One of the {{ n_notables }} charts in the bundled database |

### Results

Every one of these is a **frozen dataclass**: it cannot be mutated after it is built,
which is what makes it safe to cache, share and thread.

| Object | Is |
|---|---|
| {py:class}`~stellium.core.models.CalculatedChart` | The result of `.calculate()` |
| {py:class}`~stellium.core.models.UnknownTimeChart` | The same, for a chart with no usable birth time |
| {py:class}`~stellium.core.models.CelestialPosition` | One body, at one moment |
| {py:class}`~stellium.core.models.Aspect` | One relationship between two of them |
| {py:class}`~stellium.core.models.HouseCusps` | The twelve cusps of one house system |
| {py:class}`~stellium.core.multichart.MultiChart` | Several charts, and the aspects between them |

### Warnings

Stellium warns rather than fails when the *data* is the problem — an unrecorded birth
time, a place no geocoder knows, a missing ephemeris file. All of them descend from
{py:class}`~stellium.exceptions.StelliumWarning`, so you can escalate the whole family
in one line: see [Exceptions & Warnings](exceptions.md).

---

## By module

```{toctree}
:maxdepth: 1

core
engines
components
presentation
visualization
returns
electional
rectification
planner
analysis
io
chinese
data
utils
exceptions
cli
accidental_dignity_structure
```

## Indices

- {ref}`genindex` — every documented object, alphabetically
- {ref}`modindex` — every module
- {ref}`search`
