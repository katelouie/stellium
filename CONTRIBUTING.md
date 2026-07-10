# Contributing to Stellium

Hi, I'm Kate, and I maintain Stellium. Thanks for considering a contribution. Whether it's a bug fix, a new feature, a documentation improvement, or just a question, I'm open to just about anything.

Stellium sits at the intersection of software engineering and astrology, so contributors come from different backgrounds and that's completely okay. You don't need to know both, just be interested in learning!

## Getting Started

**Prerequisites:** Python 3.11+, Git

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/stellium.git
cd stellium
pip install -e ".[dev]"
pre-commit install
pytest
```

If the tests pass, you're good to go.

## How to Contribute

**Bug reports and feature requests** go through [GitHub Issues](https://github.com/katelouie/stellium/issues). There are templates that will ask you for the right information (Stellium version, Python version, OS, reproduction code). Please use them so it saves us both time.

**Code contributions** follow the usual fork-and-PR workflow:

1. Check existing issues first. If it's a big change, open an issue to discuss before writing code.
2. Create a branch on your fork (`feature/your-thing` or `fix/the-bug`).
3. Write your code, write tests, update the changelog if it's user-facing.
4. Open a PR. There's a template with a checklist.
5. I'll review it, we'll iterate if needed, and then it gets merged.

I'm a solo maintainer, so reviews might take a little while. I'll get to it, but don't be afraid to ping me if you're wondering where I am after a bit. Sometimes life just gets crazy.

## Development

### Running Tests

```bash
# Fast tests only (pure logic, no ephemeris calls, ~2 seconds)
pytest -m "not slow"

# Full suite (~30 seconds)
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific file or pattern
pytest tests/test_chart_builder.py
pytest -k "test_aspect"
```

All contributions need tests. Bug fixes need a regression test that fails without the fix. New features need happy-path and edge-case coverage.

### Code Style

Pre-commit hooks handle most of this automatically. The short version:

- **Black** for formatting (88 char line length)
- **isort** for import ordering
- **ruff** for linting
- **mypy** for type checking
- **Google-style docstrings** for public APIs
- **Modern type syntax:** `X | Y` not `Union[X, Y]`, `list[str]` not `List[str]`

If hooks fail, they usually auto-fix things. Just `git add` the changes and commit again.

### Diagnostics: no bare `print()`

Library code must **not** `print()` — it's banned by ruff (`T20`) everywhere
under `src/stellium/` except `ReportBuilder.render()`. A library writing to a
caller's stdout can't be silenced, filtered, or captured. Route diagnostics by
audience:

- **The caller should see it** (their input or a result is degraded — bad import
  rows, a geocoding failure, an invalid config value) → `warnings.warn(msg,
  <StelliumWarning subclass>, stacklevel=2)`. On by default; filterable.
- **Internal operational detail** (cache/file IO, "here's what I did") →
  `from stellium._logging import get_logger; log = get_logger("module.name")`
  then `log.info/warning(...)`. Silent by default (NullHandler); the app opts in.
- **The user asked to see it** (a rendered report, CLI output) → `render()`, or
  `click.echo()` / Rich `Console` in the `cli/` layer.

Full rationale and the site-by-site map: [`docs/development/specs/STRUCTURED_LOGGING_SPEC.md`](docs/development/specs/STRUCTURED_LOGGING_SPEC.md).

### Type Hints

All functions need type hints. This is enforced by mypy. Stellium is a typed codebase and I'd like to keep that coverage comprehensive.

```python
# Yes
def get_object(self, name: str) -> CelestialPosition | None:
    return self._positions.get(name)

# No
def get_object(self, name):
    return self._positions.get(name)
```

## Architecture

> 📚 **Deeper reference lives in [`docs/development/`](docs/development/README.md)
> (indexed in [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md)).** Those docs are a
> per-subsystem API/architecture reference written **primarily for coding agents**
> (e.g. Claude Code) so they don't have to re-learn the codebase each session —
> but they're a handy map for human contributors too. The summary below is the
> short version.

If you're adding a feature (rather than fixing a bug), understanding the architecture will save you time. Stellium is built on three ideas:

### Protocols over Inheritance

Stellium uses Python's `Protocol` for extensibility instead of abstract base classes. You don't inherit from anything. You just implement the right method signatures, and it works.

```python
# Define the interface
class EphemerisEngine(Protocol):
    def calculate_positions(self, datetime, location, objects, config) -> list: ...

# Implement it (no base class needed)
class MyEngine:
    def calculate_positions(self, datetime, location, objects=None, config=None):
        # Your custom logic
        return [...]

# Use it
chart = ChartBuilder.from_native(native).with_ephemeris(MyEngine()).calculate()
```

Key protocols: `EphemerisEngine`, `HouseSystemEngine`, `AspectEngine`, `OrbEngine`, `ChartComponent`, `ReportSection`, `ReportRenderer`. They're all in `core/protocols.py`.

### Composability

Everything is optional and combinable. The `ChartBuilder` uses a fluent API with lazy evaluation: you configure first, calculate once.

```python
chart = (ChartBuilder.from_native(native)
    .with_house_systems([PlacidusHouses(), WholeSignHouses()])
    .with_aspects(HarmonicAspectEngine(7))
    .add_component(ArabicPartsCalculator())
    .calculate())
```

### Immutability

All result objects are frozen dataclasses. They can't be modified after creation, which makes them thread-safe, cacheable, and predictable. Use `dataclasses.replace()` if you need a modified copy.

### Dependency Rules

The import hierarchy is strict and one-directional:

```text
core/           <- No imports from engines, components, or visualization
  ^
engines/        <- Imports from core only
  ^
components/     <- Imports from core, engines
  ^
presentation/   <- Imports from core, engines, components
visualization/  <- Imports from core, engines, components
```

Circular imports will break things. If you find yourself wanting to import from a higher-level module in a lower-level one, that's a design signal to rethink the approach.

## Creating Extensions

The protocol-based architecture means you can add things without touching existing code:

- **New house system:** Implement `HouseSystemEngine` (see `engines/houses.py` for examples)
- **New component:** Implement `ChartComponent` (see `components/` for examples)
- **New report section:** Implement `ReportSection` (see `presentation/sections/` for examples)
- **New renderer:** Implement `ReportRenderer` (see `presentation/renderers.py` for examples). The reporting layer uses a Strategy pattern: sections produce typed data dicts, renderers consume them, and neither knows about the other. Adding a renderer means handling the data types (`table`, `key_value`, `text`, `compound`, `side_by_side_tables`), not learning any astrology.
- **New visualization layer:** Implement `IRenderLayer` (see `visualization/layer_factory.py` for the protocol and `visualization/layers/` for examples)

The cookbook files in `examples/` are the best way to see (and show) how all the pieces fit together.

## Documentation

- Public APIs need docstrings (Google style)
- Comments should explain *why*, not *what*
- If you add a major feature, add a cookbook example in `examples/`
- If you change the public API, update the README

## Publishing

Releases are automated via GitHub Actions on tagged commits. Version is defined in `src/stellium/__init__.py`. This is maintainer-only.

## Getting Help

- **API and usage:** See the [documentation](https://stellium.readthedocs.io/en/latest/) and the developer reference in [`docs/development/`](docs/development/README.md)
- **General questions:** Open a [Discussion](https://github.com/katelouie/stellium/discussions)
- **Bugs or feature requests:** Open an [Issue](https://github.com/katelouie/stellium/issues)

## Recognition

Contributors are credited in the changelog and on the [Contributors page](https://github.com/katelouie/stellium/graphs/contributors). Special thanks to Zhao Xin and Zhanran Astrology for the simplified Chinese localization, and to bkermott for the sect determination fix.

Thanks for reading this far, and I'm looking forward to your contribution!
