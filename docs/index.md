# Stellium Documentation

A modern Python library for computational astrology, built on Swiss Ephemeris for
NASA-grade astronomical accuracy.

```python
from stellium import ChartBuilder

chart = ChartBuilder.from_notable("Carl Jung").calculate()
chart.draw("jung.svg").preset_standard().save()
```

---

## Where to start

| If you want to… | Go to |
|---|---|
| Install it and draw your first chart | [Overview](README.md) |
| Do a specific thing, with runnable code | [Cookbooks](cookbooks/index.md) — **357 recipes** |
| Understand a subsystem in depth | [Guides](VISUALIZATION.md) |
| Look up a class or a method | [API Reference](api/index.md) |
| See what the charts actually look like | [Theme Gallery](THEME_GALLERY.md) · [Palette Gallery](PALETTE_GALLERY.md) |

---

```{toctree}
:hidden:
:caption: Start Here
:maxdepth: 1

README
```

```{toctree}
:hidden:
:caption: Guides
:maxdepth: 1

VISUALIZATION
REPORTS
CHART_TYPES
astrology/RECTIFICATION
LOCATIONS
DIAGNOSTICS
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

api/index
options_list
api/accidental_dignity_structure
```

```{toctree}
:hidden:
:caption: Galleries
:maxdepth: 1

THEME_GALLERY
PALETTE_GALLERY
```

```{toctree}
:hidden:
:caption: Contributing
:maxdepth: 1

PUBLISHING
```

## Project links

- [**Contributing**](https://github.com/katelouie/stellium/blob/main/CONTRIBUTING.md) — how to work on Stellium
- [**Changelog**](https://github.com/katelouie/stellium/blob/main/CHANGELOG.md) — release history
- [**GitHub**](https://github.com/katelouie/stellium) — source and issues
- [**Colour & theme reference**](starlight_colors.html) — every theme, palette and hex value, in one interactive page

## Indices

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
