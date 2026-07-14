:::{container} st-eyebrow
☾ Orientation map
:::

# For astrologers

:::{container} st-lede
Traditional and modern technique, real chart output, and sensible defaults — so
you can start reading, not configuring.
:::

This page is a **map** to the parts of the docs that matter to practice. No
programming background is assumed.

:::{container} st-panel st-panel-gold
**Prefer not to touch Python?**

The web app draws charts in your browser — roughly 50–60% of the library, with
nothing to install.

[Open the web app →](https://www.stelliumastro.app/){.st-btn .st-btn-gold}
:::

---

## Start reading charts

::::{container} st-grid

:::{container} st-cbcard
[Chart types](CHART_TYPES.md)

Natal, synastry, transits, composite, Davison, returns, progressions — what each
one is and how to draw it.
:::

:::{container} st-cbcard
[Unknown birth time](astrology/RECTIFICATION.md)

Read the layer that survives — honestly. Stellium recovers **sect** (day/night),
and deliberately refuses to invent a minute-level birth time it cannot know.
:::

:::{container} st-cbcard
[Reports](REPORTS.md)

Terminal, Markdown, HTML and typeset PDF — composed section by section.
:::

:::{container} st-cbcard
[Visualization](VISUALIZATION.md)

Wheels, dials, multiwheels; themes, palettes and presets.
:::

::::

## Techniques

Each of these is a cookbook: a page of worked recipes, every one executed at build
time and showing its real output.

:::{container} st-tags
- [Essential & accidental dignities](cookbooks/dignities.md){.st-tag}
- [Profections](cookbooks/profections.md){.st-tag}
- [Zodiacal Releasing](cookbooks/zodiacal_releasing.md){.st-tag}
- [Hellenistic & lots](cookbooks/hellenistic.md){.st-tag}
- [Electional](cookbooks/electional.md){.st-tag}
- [Returns](cookbooks/returns.md){.st-tag}
- [Progressions](cookbooks/progressions.md){.st-tag}
- [Solar arc directions](cookbooks/arc_directions.md){.st-tag}
- [Primary directions](cookbooks/directions.md){.st-tag}
- [Uranian dials](cookbooks/dial.md){.st-tag}
- [Transits](cookbooks/transit.md){.st-tag}
- [Synastry & comparison](cookbooks/comparison.md){.st-tag}
- [Aspects & orbs](cookbooks/aspects_and_orbs.md){.st-tag}
- [Graphic ephemeris](cookbooks/ephemeris.md){.st-tag}
:::

## Traditions

::::{container} st-grid

:::{container} st-cbcard
**Western**

Tropical, traditional and modern — the deepest coverage, and the default.

[Chart types](CHART_TYPES.md) · [Hellenistic](cookbooks/hellenistic.md)
:::

:::{container} st-cbcard
**Vedic**

Sidereal, nine ayanamsas, North and South Indian chart styles.

[Vedic cookbook](cookbooks/vedic.md) [{{ cb_vedic }}]{.st-n}
:::

:::{container} st-cbcard
**Chinese**

Ba Zi — Four Pillars, Ten Gods, hidden stems, element balance.

[BaZi cookbook](cookbooks/bazi.md) [{{ cb_bazi }}]{.st-n}
:::

::::

## On whose authority?

:::{container} st-panel st-panel-gold
Stellium takes sides on questions the tradition genuinely disagrees about — which
term bounds, which planetary years, whether Zodiacal Releasing loops. The
methodology pages say **what we compute, which source it comes from, and where the
authorities part ways** — citing Valens, Ptolemy, Firmicus and Houlding — so you can
check our defaults against your own practice rather than take them on faith.

[Read the methodology →](methodology/README.md){.st-btn .st-btn-gold}
:::

## Make it beautiful

::::{container} st-grid

:::{container} st-cbcard
[Theme Gallery](THEME_GALLERY.md)

All {{ n_themes }} chart themes, rendered.
:::

:::{container} st-cbcard
[Palette Gallery](PALETTE_GALLERY.md)

{{ n_palettes }} palettes for zodiac rings, aspect lines and planet glyphs.
:::

::::

---

:::{container} st-switch
**Building software with it?**
[Switch to the developer's map →](for-developers.md)
:::
