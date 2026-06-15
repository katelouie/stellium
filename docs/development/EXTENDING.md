# Extending Stellium

> 🤖 **Primarily for coding agents. Hello, Claude!** Read this before
> re-deriving the API from source. If it disagrees with the code, the code wins
> — please update the doc.

> Part of the [developer docs](./README.md). Background: [ARCHITECTURE](./ARCHITECTURE.md).

Everything pluggable is a **Protocol** in `core/protocols.py` (or the
visualization `IRenderLayer` / presentation `ReportSection`). You implement the
methods — **no base class, no inheritance** — and inject the object. Match the
signature exactly; type hints are enforced by mypy.

---

## Add a house system  (`HouseSystemEngine`)
```python
class VedicHouses:
    @property
    def system_name(self) -> str: return "Vedic"
    def calculate_house_data(self, datetime, location, config) -> tuple[HouseCusps, list[CelestialPosition]]:
        ...  # return (HouseCusps(system_name=..., cusps=[...12...]), [angles])
    def assign_houses(self, positions, cusps) -> dict[str, int]:
        ...
chart = ChartBuilder.from_native(n).with_house_systems([VedicHouses()]).calculate()
```
Most built-ins extend `SwissHouseSystemBase` (`engines/houses.py`) — start there.

## Add an orb engine  (`OrbEngine`)
```python
class MyOrbs:
    def get_orb_allowance(self, obj1, obj2, aspect_name) -> float: ...
ChartBuilder...with_orbs(MyOrbs())
```

## Add an aspect engine  (`AspectEngine`)
```python
class MyAspects:
    def calculate_aspects(self, positions, orb_engine) -> list[Aspect]: ...
ChartBuilder...with_aspects(MyAspects())
```

## Add a component  (`ChartComponent`) — adds positions/metadata
```python
class FixedStarsCalculator:
    @property
    def component_name(self) -> str: return "Fixed Stars"
    def calculate(self, datetime, location, positions, house_systems_map, house_placements_map) -> list[CelestialPosition]:
        ...
chart = ChartBuilder...add_component(FixedStarsCalculator()).calculate()
chart.get_component_result("Fixed Stars")
```
Return appended `CelestialPosition`s, **or** write to a metadata key and return
`[]` (then read via `chart.metadata[...]`).

## Add an analyzer  (`ChartAnalyzer`) — adds metadata
```python
class MyAnalyzer:
    @property
    def analyzer_name(self) -> str: return "My Analysis"
    @property
    def metadata_name(self) -> str: return "my_analysis"
    def analyze(self, chart) -> list | dict: ...
ChartBuilder...add_analyzer(MyAnalyzer())
```

## Add an ephemeris engine  (`EphemerisEngine`)
```python
class MyEphemeris:
    def calculate_positions(self, datetime, location, objects, config) -> list[CelestialPosition]: ...
ChartBuilder...with_ephemeris(MyEphemeris())
```
For tests, reuse `MockEphemerisEngine` from `engines/ephemeris.py`.

## Add a visualization layer  (`IRenderLayer`)
```python
class CustomLayer:
    def render(self, renderer, dwg, chart) -> None:
        x, y = renderer.polar_to_cartesian(chart.get_object("Sun").longitude, radius=350)
        dwg.add(dwg.text("★", insert=(x, y), text_anchor="middle"))
```
Then register it in `visualization/layer_factory.py::create_layers` at the right
spot in the bottom→top order, and expose a `ChartDrawBuilder.with_*` toggle.
Use `renderer.style[...]` for theme colors. See
[VISUALIZATION_INTERNALS](./VISUALIZATION_INTERNALS.md).

## Add a theme / palette
- **Theme** (`visualization/themes.py`): add a `ChartTheme` enum value, a
  `_get_<name>_theme()` returning the style dict, wire it into
  `get_theme_style()`, and add defaults to the `THEME_DEFAULT_*` maps.
- **Zodiac palette** (`visualization/palettes.py`): add a `ZodiacPalette` value
  and a branch in `get_palette_colors()` returning 12 hex colors (Aries first).
- **Aspect / planet-glyph palette**: same pattern in
  `get_aspect_palette_colors()` / `get_planet_glyph_color()`.

## Add a report section  (`ReportSection`)
```python
class MySection:
    @property
    def section_name(self) -> str: return "My Section"
    def generate_data(self, chart) -> dict:
        return {"type": "table", "headers": [...], "rows": [[...]]}
report.with_section(MySection())
```
Valid `"type"` values: `table`, `key_value`, `text`, `side_by_side_tables`,
`compound`, `svg`. See [PRESENTATION_INTERNALS](./PRESENTATION_INTERNALS.md).

---

## Checklist for any extension
1. Implement the protocol's exact signatures (mypy-clean, full type hints).
2. Keep result objects **frozen / immutable**.
3. Respect dependency direction — `core/` imports nothing internal.
4. Add tests (a failing-then-passing test for fixes; happy path + edges for
   features). Use the fast tier (`-m "not slow"`) where possible; reuse
   fixtures from `tests/conftest.py`.
5. Run `pytest`, `ruff check .`, `ruff format --check .` before committing.
