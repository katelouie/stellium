:::{container} st-eyebrow
⌘ Orientation map
:::

# For developers

:::{container} st-lede
A typed, protocol-driven library with a fluent builder at its core. If you know
React's composability or PyTorch's lazy, progressive API, you already know the
shape of this one.
:::

This page is a **map, not a wall** — the fastest routes through the docs for
building software with Stellium. Everything linked here lives in the shared
guides and reference; this page just orders it for you.

:::{container} st-eyebrow
The whole idea, in one block
:::

```python
from stellium import ChartBuilder
from stellium.engines import ModernAspectEngine, PlacidusHouses, WholeSignHouses
from stellium.components import ArabicPartsCalculator

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .calculate())   # lazy · fully typed · nothing runs until here
```

Three ideas carry the whole design, and they are worth naming before you read
anything else:

Protocols, not inheritance
: An engine is anything with the right method signature. To add a house system you
  write a class with `calculate_houses(...)` — you do not subclass anything, and
  nothing in the library needs to know your type exists.

Immutability
: Every result object is a frozen dataclass. A `CalculatedChart` cannot be mutated
  after it is built, which is what makes it safe to share, cache and thread.

Lazy configuration
: `ChartBuilder` accumulates configuration and computes nothing. The work happens
  in `.calculate()`, once, and hands back the immutable result above.

---

## Get running

::::{container} st-grid

:::{container} st-cbcard
[Overview: install & first chart](README.md)

`pip install stellium`, then a chart in two lines.
:::

:::{container} st-cbcard
[Options & objects](options_list.md)

Every house system, aspect, body, lot and ayanamsa the builder accepts.
:::

:::{container} st-cbcard
[Locations & time](LOCATIONS.md)

Geocoding, timezones, and the historical-calendar traps that break old charts.
:::

:::{container} st-cbcard
[Diagnostics](DIAGNOSTICS.md)

What the library warns about, and how to make it tell you more.
:::

::::

## Understand the design

The architecture reference is written for contributors and lives on GitHub, next
to the code it describes — it is deliberately not duplicated into this site, so it
cannot drift from the source.

- [**Architecture & protocols**](https://github.com/katelouie/stellium/blob/main/docs/development/ARCHITECTURE.md) — the layer map, the dependency rules, and what `.calculate()` actually does
- [**Chart building**](https://github.com/katelouie/stellium/blob/main/docs/development/CHART_BUILDING.md) — `Native`, `Notable`, `ChartBuilder`, `CalculatedChart`, config, registries
- [**Engines**](https://github.com/katelouie/stellium/blob/main/docs/development/ENGINES.md) — ephemeris, houses, aspects, orbs, dignities, patterns, profections
- [**Extending**](https://github.com/katelouie/stellium/blob/main/docs/development/EXTENDING.md) — write a custom house / aspect / orb engine, with no inheritance

## Data & integration

::::{container} st-grid

:::{container} st-cbcard
[Analysis & DataFrames](cookbooks/analysis.md) [{{ cb_analysis }}]{.st-n}

Calculate hundreds of charts into a pandas DataFrame. Executed at build time, so
every number on that page was computed by the commit you are reading.
:::

:::{container} st-cbcard
[I/O](cookbooks/io.md) [{{ cb_io }}]{.st-n}

Import natives from CSV and AAF; export charts to JSON and to LLM prompt text.
:::

::::

## Reference

:::{container} st-panel
Every class, method and signature, generated from the source docstrings.

[Open the API Reference →](api/index.md){.st-btn .st-btn-primary}
:::

---

:::{container} st-switch
**Here for the astrology, not the code?**
[Switch to the astrologer's map →](for-astrologers.md)
:::
