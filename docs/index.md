# Computational astrology, composable by design.

:::{container} st-lede
Stellium is an extensible Python library for astrology — a fluent chart builder
you configure like Lego, spanning Western, Vedic and Chinese traditions with the
depth serious practitioners actually need.
:::

:::{container} st-cta
- [`pip install stellium`]{.st-cta-code}
- [Launch the web app →](https://www.stelliumastro.app/){.st-btn .st-btn-primary}
- [Open in Colab](https://colab.research.google.com/github/katelouie/stellium/blob/main/examples/stellium_sampler_colab.ipynb){.st-btn}
:::

:::{container} st-cta-note
No install required — the web app covers roughly 50–60% of the package, and Colab
runs the real thing.
:::

:::::{container} st-split

::::{container} st-split-code
:::{container} st-eyebrow
Two lines of code
:::

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
chart.draw("einstein.svg").save()
```
::::

::::{container} st-split-figure
```{image} images/examples/readme_einstein.svg
:alt: Albert Einstein's natal chart, drawn by Stellium
```
::::

:::::

---

## Where do you want to start?

Two honest paths through the same library — pick the one that sounds like you.
Both lead into the same documentation; they just order it differently.

::::{container} st-fork

:::{container} st-card st-card-dev
**⌘ I'm a developer first**

Typed, protocol-driven, composable. Feels familiar if you know React or PyTorch.

- [The developer's map](for-developers.md)
- [Install & first chart](README.md)
- [API Reference](api/index.md)
- [Options & objects](options_list.md)
:::

:::{container} st-card st-card-astro
**☾ I'm an astrologer first**

Traditional and modern techniques, real chart output, sensible defaults out of the box.

- [The astrologer's map](for-astrologers.md)
- [Chart types](CHART_TYPES.md)
- [Theme & palette galleries](THEME_GALLERY.md)
- [Traditional methods & sources](methodology/README.md)
:::

::::

---

## Composable, not hard-coded

Most astrology libraries hand you one rigid constructor. Stellium hands you a
builder: swap house systems, aspect engines and zodiacs, stack plugin components,
and evaluate lazily — all fully typed.

```python
from stellium import ChartBuilder
from stellium.engines import ModernAspectEngine, PlacidusHouses, WholeSignHouses
from stellium.components import ArabicPartsCalculator

chart = (ChartBuilder.from_details("2000-01-06 12:00", "Seattle, WA")
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])   # multiple at once
    .with_aspects(ModernAspectEngine())                          # swap the engine
    .add_component(ArabicPartsCalculator())                      # stack plugins
    .calculate())                                                # nothing ran until here
```

Positions come from Swiss Ephemeris. Every asteroid and trans-Neptunian body in the
registry is cross-checked against NASA JPL Horizons in the test suite, so a body
named Hygiea is *the* Hygiea. Output is portable SVG / PDF / PNG with every font
bundled, so charts render identically everywhere.

---

## Breadth most libraries skip

Three traditions, and the traditional timing techniques that are usually locked
inside desktop software — not scattered across half a dozen half-maintained packages.

:::{container} st-tags
- [Western]{.st-tag .st-tag-lead}
- [Vedic · 9 ayanamsas]{.st-tag .st-tag-lead}
- [Chinese · Ba Zi]{.st-tag .st-tag-lead}
- [Synastry]{.st-tag}
- [Transits]{.st-tag}
- [Composite & Davison]{.st-tag}
- [Returns]{.st-tag}
- [Progressions]{.st-tag}
- [Solar arc directions]{.st-tag}
- [Profections]{.st-tag}
- [Firdaria]{.st-tag}
- [Zodiacal Releasing]{.st-tag}
- [Essential & accidental dignities]{.st-tag}
- [Fixed stars]{.st-tag}
- [Arabic parts]{.st-tag}
- [Uranian dials]{.st-tag}
- [Declinations & OOB]{.st-tag}
- [Primary directions]{.st-tag}
- [Electional]{.st-tag}
- [Length of life (hyleg → alcocoden)]{.st-tag}
:::

See the [chart-type catalog](CHART_TYPES.md) and the [options reference](options_list.md)
for everything, with signatures.

---

## Learn by cookbook

{{ n_cookbooks }} runnable cookbooks holding **{{ n_recipes }} recipes** — each one a
focused mini-tutorial you can copy, run and adapt. Every recipe on those pages is a
real function in a real script, executed at build time, showing its **actual output**.

::::{container} st-grid

:::{container} st-cbcard
[Chart Visualization](cookbooks/chart.md) [{{ cb_chart }}]{.st-n}

Themes, palettes, house systems, tables.
:::

:::{container} st-cbcard
[Electional Astrology](cookbooks/electional.md) [{{ cb_electional }}]{.st-n}

Auspicious timing, predicates, planetary hours.
:::

:::{container} st-cbcard
[Profections](cookbooks/profections.md) [{{ cb_profections }}]{.st-n}

Annual and monthly profections for many points.
:::

:::{container} st-cbcard
[MultiChart](cookbooks/multichart.md) [{{ cb_multichart }}]{.st-n}

Synastry, transits, bi-, tri- and quad-wheels.
:::

:::{container} st-cbcard
[BaZi (Four Pillars)](cookbooks/bazi.md) [{{ cb_bazi }}]{.st-n}

Four Pillars, Ten Gods, hidden stems, elements.
:::

:::{container} st-cbcard
[Reports](cookbooks/report.md) [{{ cb_report }}]{.st-n}

Terminal reports, PDF generation, batches.
:::

::::

[Browse all {{ n_cookbooks }} cookbooks →](cookbooks/index.md)

---

## The complete API reference

:::{container} st-panel
Every class, method and signature — generated from source, so it is the single
source of truth for the whole package. If it isn't in a guide, it's here.

[Open the API Reference →](api/index.md){.st-btn .st-btn-primary}
:::

---

## One chart, {{ n_themes }} themes

Restyle a whole wheel by swapping one argument — `.with_theme(...)`. Backgrounds,
zodiac rings, aspect lines and glyphs all follow. There are {{ n_palettes }} palettes
on top of that.

::::{container} st-strip

:::{container} st-shot
![classic](images/gallery/classic_rainbow.svg)
[classic]{.st-shot-label}
:::

:::{container} st-shot
![midnight](images/gallery/midnight_rainbow_midnight.svg)
[midnight]{.st-shot-label}
:::

:::{container} st-shot
![celestial](images/gallery/celestial_rainbow_celestial.svg)
[celestial]{.st-shot-label}
:::

:::{container} st-shot
![sepia](images/gallery/sepia_elemental.svg)
[sepia]{.st-shot-label}
:::

::::

[See all themes & palettes →](THEME_GALLERY.md)

---

## Project links

- [**Contributing**](https://github.com/katelouie/stellium/blob/main/CONTRIBUTING.md) — how to work on Stellium
- [**Changelog**](https://github.com/katelouie/stellium/blob/main/CHANGELOG.md) — release history
- [**GitHub**](https://github.com/katelouie/stellium) — source and issues
- [**Colour & theme reference**](starlight_colors.html) — every theme, palette and hex value, in one interactive page

```{toctree}
:hidden:
:caption: Start Here
:maxdepth: 1

Overview <README>
For developers <for-developers>
For astrologers <for-astrologers>
```

```{toctree}
:hidden:
:caption: Guides
:maxdepth: 1

Visualization <VISUALIZATION>
Reports <REPORTS>
Chart Types <CHART_TYPES>
Rectification <astrology/RECTIFICATION>
Locations <LOCATIONS>
Diagnostics <DIAGNOSTICS>
```

```{toctree}
:hidden:
:caption: Cookbooks
:maxdepth: 1

cookbooks/index
```

```{toctree}
:hidden:
:caption: Reference
:maxdepth: 1

API Reference <api/index>
Options & Objects <options_list>
Accidental Dignity <api/accidental_dignity_structure>
```

```{toctree}
:hidden:
:caption: Methodology & Sources
:maxdepth: 1

Traditional Methods & Sources <methodology/README>
Planetary Years <methodology/research/planetary-years>
Zodiacal Releasing <methodology/research/zodiacal-releasing>
Firdaria <methodology/research/firdaria>
```

```{toctree}
:hidden:
:caption: Galleries
:maxdepth: 1

Themes <THEME_GALLERY>
Palettes <PALETTE_GALLERY>
```
