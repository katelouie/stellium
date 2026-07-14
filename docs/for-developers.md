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
building software with Stellium. Everything linked here lives in the shared guides
and reference; this page just orders it for you.

```{code-block} python
:caption: the whole idea, in one block

from stellium import ChartBuilder
from stellium.engines import ModernAspectEngine, PlacidusHouses, WholeSignHouses
from stellium.components import ArabicPartsCalculator

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .calculate())   # lazy · fully typed · nothing runs until here
```

---

## Install & set up

Install from PyPI to use it, or clone for an editable environment with the test suite.

```{code-block} bash
:caption: shell

# use it
pip install stellium

# hack on it
git clone https://github.com/katelouie/stellium && cd stellium
pip install -e ".[dev]"
pytest
```

:::{container} st-pills
- Python 3.11+
- macOS · Linux · Windows
- fully type-hinted
- ephemeris bundled
- no API keys
:::

:::{note}
**Offline, with one asterisk.** The Swiss Ephemeris data ships inside the wheel, so
the *astronomy* needs no network. But `from_details("...", "Seattle, WA")` geocodes
the place name over the network (Nominatim). Pass coordinates via
{py:class}`~stellium.core.native.Native` and the library never reaches out at all —
which is what you want in a container, a Lambda, or a test.
:::

---

## The mental model

Data flows one direction. You parse a birth into a `Native`, configure a
`ChartBuilder`, call `.calculate()` to get an **immutable** chart, then hand that to
a renderer or a report.

::::{container} st-flow

:::{container} st-step
[☽]{.st-glyph}

**Native**

time + place
:::

:::{container} st-step
[⚙]{.st-glyph}

**ChartBuilder**

configure
:::

:::{container} st-step
[☉]{.st-glyph}

**CalculatedChart**

immutable
:::

:::{container} st-step
[✦]{.st-glyph}

**Renderer / Report**

SVG · PDF · dict
:::

::::

The arrow between the last two is the one that matters: **nothing before
`.calculate()` computes anything, and nothing after it can mutate the result.**

## Core concepts

Three ideas carry the whole design, and they are worth naming before you read
anything else:

Protocols, not inheritance
: An engine is anything with the right method signature. To add a house system you
  write a class with `calculate_house_data(...)` and `assign_houses(...)` — you do not
  subclass anything, and nothing in the library needs to know your type exists.

Immutability
: Every result object is a frozen dataclass. A `CalculatedChart` cannot be mutated
  after it is built, which is what makes it safe to share, cache and thread. Use
  `dataclasses.replace()` to derive a changed copy.

Lazy configuration
: `ChartBuilder` accumulates configuration and computes nothing. The work happens in
  `.calculate()`, once, and hands back the immutable result above.

---

## Extending with your own engine

There is no base class to inherit and no registry to sign up with. Match the
signature and the builder will take it.

```{code-block} python
:caption: my_engine.py

from stellium import ChartBuilder
from stellium.core.models import HouseCusps


class EqualFromMC:
    """A house system: twelve equal houses, measured from the Midheaven."""

    @property
    def system_name(self) -> str:
        return "Equal from MC"

    def calculate_house_data(self, datetime, location, config=None):
        cusps = tuple((30.0 * i) % 360.0 for i in range(12))   # your real maths here
        return HouseCusps(system=self.system_name, cusps=cusps), []

    def assign_houses(self, positions, cusps):
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

No import of ours appears in that class, and no base class. `EqualFromMC` satisfies
{py:class}`~stellium.core.protocols.HouseSystemEngine` because it has the right two
methods — that is the entire contract.

The same shape works for `AspectEngine`, `OrbEngine`, `EphemerisEngine`, chart
components, report sections and render layers. All of them are in
[Core → Protocols](api/core.md).

---

## Get running

::::{container} st-grid

:::{container} st-cbcard
[Install & first chart](README.md)

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

## From the command line

A CLI ships with the package, for quick charts and for managing ephemeris data — no
script needed.

```{code-block} bash
:caption: shell

# draw a chart straight from the notables database
stellium chart from-registry "Albert Einstein" -o einstein.svg

# ...or print it to the terminal instead
stellium chart from-registry "Carl Jung" --format terminal --house-system "Whole Sign"

# ephemeris data, and where everything lives
stellium ephemeris download --years 1000-3000
stellium ephemeris list
stellium cache info
```

`stellium cache info` is the one to reach for when something is not where you expect:
it prints the resolved cache and ephemeris directories and which environment variable,
if any, set them.

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

:::{container} st-cbcard
[Notable datasets](api/data.md)

{{ n_notables }} charts, plus **{{ n_life_events }} taxonomy-tagged life events** for
{{ n_notables_with_events }} of them — `get_notable_life_events()`.
:::

:::{container} st-cbcard
[Exceptions & warnings](api/exceptions.md)

Escalate the whole `StelliumWarning` family in one line, so a data problem cannot
pass silently through a pipeline.
:::

::::

:::{container} st-callout
[Honest]{.st-callout-label}

**The biography data is interpretive, and the library says so.** Life events are
provenance-graded, but temperament descriptors are distilled from biographies rather
than measured — so reading them raises a `DataQualityWarning` rather than handing you
a number that looks as solid as a planet's longitude. Treat them as a research
convenience, not as ground truth.
:::

## Understand the internals

The architecture reference is written for contributors and lives on GitHub, next to
the code it describes — deliberately not duplicated into this site, so it cannot
drift from the source.

- [**Architecture & protocols**](https://github.com/katelouie/stellium/blob/main/docs/development/ARCHITECTURE.md) — the layer map, the dependency rules, and what `.calculate()` actually does
- [**Chart building**](https://github.com/katelouie/stellium/blob/main/docs/development/CHART_BUILDING.md) — `Native`, `Notable`, `ChartBuilder`, `CalculatedChart`, config, registries
- [**Engines**](https://github.com/katelouie/stellium/blob/main/docs/development/ENGINES.md) — ephemeris, houses, aspects, orbs, dignities, patterns, profections
- [**Extending**](https://github.com/katelouie/stellium/blob/main/docs/development/EXTENDING.md) — adding engines, components, analyzers, layers, themes and sections

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
