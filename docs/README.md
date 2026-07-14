# Install & first chart

Stellium is a Python library for computational astrology, built on
[Swiss Ephemeris](https://www.astro.com/swisseph/) for astronomical accuracy. It
spans Western, Vedic and Chinese traditions, draws its own charts, and typesets
its own reports.

This page gets you from nothing to a chart. Once you have one, take
[the developer's map](for-developers.md) or [the astrologer's map](for-astrologers.md)
depending on what you came for.

## Install

Stellium needs **Python 3.11 or newer**.

```bash
pip install stellium
```

That is the whole install. The ephemeris data and every font the PDF and SVG
renderers need are bundled in the package — there is no separate download, and no
system dependency to install first.

:::{note}
Not ready to install anything? The [web app](https://www.stelliumastro.app/) draws
charts in your browser (roughly 50–60% of the library), and the
[Colab notebook](https://colab.research.google.com/github/katelouie/stellium/blob/main/examples/stellium_sampler_colab.ipynb)
runs the real package with nothing to set up.
:::

## Your first chart

Stellium ships a database of {{ n_notables }} notable birth and event charts, which
means you can draw something real before you have typed in any birth data:

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

sun = chart.get_object("Sun")
print(f"{sun.name}: {sun.sign_position}")
```

<!--pytest-codeblocks:expected-output-->

```
Sun: 23°30' Pisces
```

Then draw it:

```python
chart.draw("einstein.svg").preset_standard().save()
```

## Your own birth data

`from_details` takes a date-time and a place, and does the geocoding and timezone
lookup for you:

```python
chart = ChartBuilder.from_details("1994-01-06 11:47", "Palo Alto, CA").calculate()
```

If you would rather not depend on a geocoder — or you are charting a place that no
longer exists — pass coordinates directly with `Native`. See
[Locations & time](LOCATIONS.md), which also covers the two traps that quietly ruin
historical charts: the **Julian calendar**, and **Local Mean Time** before
standardised time zones.

:::{warning}
A birth time you are not sure of is not a birth time. Stellium will tell you when a
chart's time is unreliable rather than silently drawing houses on top of it — see
[Unknown birth time](astrology/RECTIFICATION.md).
:::

## Configure it

Nothing above was a special case: the two-line version is just the builder with its
defaults. Every part of it can be swapped, and nothing is computed until
`.calculate()`.

```python
from stellium import ChartBuilder
from stellium.engines import PlacidusHouses, WholeSignHouses, ModernAspectEngine
from stellium.components import ArabicPartsCalculator

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(ModernAspectEngine())
    .add_component(ArabicPartsCalculator())
    .calculate())
```

## Where to go next

| If you want to… | Go to |
|---|---|
| Get oriented as a programmer | [The developer's map](for-developers.md) |
| Get oriented as an astrologer | [The astrologer's map](for-astrologers.md) |
| Do a specific thing, with runnable code | [Cookbooks](cookbooks/index.md) — {{ n_recipes }} recipes |
| Draw and style charts | [Visualization](VISUALIZATION.md) |
| Generate reports and PDFs | [Reports](REPORTS.md) |
| Look up a class or a method | [API Reference](api/index.md) |
| Know **which sources** a technique comes from | [Methodology](methodology/README.md) |
