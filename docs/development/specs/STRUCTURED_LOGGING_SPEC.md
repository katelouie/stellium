# Spec: Structured Diagnostics & Logging

| | |
|---|---|
| **Status** | **Implemented** — Phases 0–5 shipped. Only Phase 6 (web app) is open. |
| **Created** | 2026-07-09 |
| **Verified against the tree** | 2026-07-14 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Tracking** | Obsidian: "Introduce a structured logging system" |

> ### What actually happened
>
> Everything in the migration plan below is **done except Phase 6**, which the spec
> itself scopes to `web/` rather than the library. Measured against the tree:
>
> | The plan | Then | Now |
> |---|---|---|
> | Library-proper `print()` → warnings/logging | 20 | **0** |
> | CLI `print()` → `click.echo` / Rich | 32 | **0** |
> | `render()` product output (deliberately kept) | 3 | 3 |
> | `ruff` `T20` guard, with the single allow-list | — | **on, and the tree is clean** |
> | `_logging.py`, `configure_logging`, `NullHandler` | — | shipped, silent on import |
> | Typed warning classes | — | **7** |
>
> Two warnings have joined the taxonomy since this was written, and both are the
> decision rule in section 4 working as designed — a condition the *caller* must see,
> not an operational trace the app opts into:
>
> - **`MissingGlyphWarning`** — a glyph SVG is missing from the installation, so the
>   chart silently falls back to a Unicode codepoint that most fonts do not contain.
> - **`TimeZoneWarning`** — a birth predates standard time and no longitude was given,
>   so Local Mean Time cannot be resolved from the birthplace and the zone's own LMT
>   is used instead. Costs a degree or more of Ascendant.
>
> **The one thing that did not survive contact:** the originating Obsidian task's
> "167 bare prints" was a `grep` count, inflated by docstring examples and Rich's
> `console.print`. Section 2.1 already corrected it to 55 by AST scan — but the *task*
> still says 167, and should be closed rather than worked. There is no print problem
> left to solve.

---

## 1. Summary

Stellium has **no logging system** and emits diagnostics by `print()`-ing to
stdout from deep inside library code. This spec defines a disciplined,
**stdlib-only** diagnostics architecture on three cleanly separated channels —
`warnings`, `logging`, and (for the CLI) Click/Rich — plus a lint guard that
bans bare `print()` in the package.

Small surface area, real defect: a library must never write to a caller's
stdout uninvited, and a CLI should route output through its framework, not
bare `print()`.

---

## 2. Problem & Motivation

### 2.1 The real numbers (measured, not estimated)

The originating task said "167 bare prints." That counts `grep 'print('`, which
is inflated by **docstring examples** (`>>> print`, Sphinx `Example::` blocks)
and **Rich `console.print()`** (intentional rendering). An AST scan of actual
`print()` call nodes gives the truth:

| Measure | Count |
|---|---|
| `grep 'print('` raw matches | 183 |
| **Actual runtime `print()` calls (AST)** | **55** |
| — Library-proper (→ warnings / logging) | 20 |
| — CLI / tooling (→ `click.echo` / Rich) | 32 |
| — `render()` product output (kept) | 3 |

So the actionable scope is **52 conversions across ~14 modules**, not 167.
Full inventory in [Appendix A](#appendix-a-full-inventory).

### 2.2 Why bare `print()` is a defect

**In library code**, every site has ≥1 of these problems:

1. **Pollutes the caller's stdout** — a web app (NiceGUI), notebook, or importing
   library gets `Warning: …` lines with no opt-out.
2. **Unsuppressable & unfilterable** — no severity, no category, no
   `filterwarnings`, no level.
3. **Uncapturable in tests** — asserting "this degraded path warned" means
   scraping stdout.
4. **No structure** — no timestamp, module, or severity.
5. **Wrong stream** — diagnostics go to stdout, mixing with data output (only
   `data/paths.py:138` uses stderr).

**In CLI code**, bare `print()` is less wrong (writing to the terminal *is* the
CLI's job) but still suboptimal: no stderr routing, no `--quiet`, harder to test,
and no pipe/encoding safety. The CLI is built on **Click**, whose `click.echo()`
is the idiomatic primitive for exactly this.

### 2.3 What already exists (the precedent to extend)

`engines/ephemeris.py` already does the warnings pattern correctly:

```python
class MissingEphemerisWarning(UserWarning): ...
warnings.warn(" ".join(parts), MissingEphemerisWarning, stacklevel=2)
```

This spec generalizes it, adds a logging channel for the cases warnings don't
fit, migrates the CLI to `click.echo`/Rich, and adds a guard so it stays clean.

---

## 3. Goals / Non-Goals

### Goals

- **G1** — No package code writes via bare `print()`. Library diagnostics flow
  through `warnings`/`logging`; CLI output flows through `click.echo`/Rich.
- **G2** — `import stellium` + normal calculation emit **zero** output on their
  own (a `NullHandler` absorbs logs; warnings fire only on real conditions).
- **G3** — Every diagnostic is **capturable and testable** (`pytest.warns`,
  `caplog`, Click `CliRunner`).
- **G4** — A **CI lint guard** (`ruff` `T20`) fails on any new bare `print()` in
  `src/stellium`, with essentially no allow-list.
- **G5** — Apps opt into library verbosity with one call and route it anywhere.
- **G6** — **Zero new runtime dependencies** (stdlib `logging` + `warnings`;
  Click/Rich already present).

### Non-Goals

- **N1** — No third-party logging framework (`loguru`, `structlog`) — see
  [§4.1](#41-why-stdlib-logging-and-not-loguru).
- **N2** — No change to *what* the CLI prints, only *how* (mechanism →
  `click.echo`/Rich).
- **N3** — No change to `ReportBuilder.render()`'s documented "print to stdout"
  default; `to_string()` already covers redirection.
- **N4** — No request-id / correlation / async-context machinery. Stellium is a
  computational library, not a service.
- **N5** — Docstring `print()` examples are documentation; untouched.

---

## 4. Background: channels & the decision rule

Stellium produces three fundamentally different kinds of text. Conflating them is
the root cause of the current mess.

| Channel | For | Mechanism | Default visibility |
|---|---|---|---|
| **Product output** | The thing the user asked to see — a rendered report, a CLI table | `click.echo` / Rich `Console` (CLI), `render()` (library) | Always shown |
| **Warnings** | "You (the caller) should know — your input or result is degraded; act or suppress" | `warnings.warn(msg, StelliumWarning)` | Shown once per site; filterable |
| **Logs** | Internal operational diagnostics — cache/file IO, "here's what I did" | `logging` on the `stellium` logger | **Silent** unless the app configures a handler |

### The decision rule

```
Is this the product the user explicitly requested (report / CLI output)?
    → click.echo / Rich Console (CLI) or render() (library) — presentation only.

Else, is it about the CALLER's input or a degraded result they'd want to
know about and could act on or suppress?
    → warnings.warn(..., <StelliumWarning subclass>)

Else (internal operational diagnostic, not the caller's fault to fix):
    → logger.<level>(...)
```

### 4.1 Why stdlib `logging` and not loguru

For a **library**, loguru/structlog are anti-patterns:

- They are **hard dependencies forced on every downstream consumer**, who may
  already use their own stack.
- loguru **hijacks the root logger** and is opinionated about global state — a
  library has no business dictating the app's logging.

Stdlib `logging` lets the *application* choose its stack (which might be loguru,
structlog, or plain logging). The library's only job is to (a) log to a named
logger and (b) attach a `NullHandler` so it's silent by default. Same reasoning
as not shipping our own `Console`.

### 4.2 Why warnings AND logging (not one or the other)

The split is about **audience and default visibility**, not severity:

| | `warnings.warn` | `logging` |
|---|---|---|
| Default visibility | **On** (once, to stderr) | **Off** (NullHandler; app opts in) |
| Audience | the **caller** — "you gave me questionable input / your result is degraded" | the **app operator** debugging Stellium |
| Example | "3 CSV rows skipped", geocoding failed | cache write failed, ephemeris init |

**The trap:** converting the *user-data* cases to `logging` would silently
swallow them (no handler by default) — worse than today's print. "Your data had
problems" must be visible without setup → `warnings`. "My cache write failed" is
an internal diagnostic the app opts into → `logging`. This is exactly how
numpy / pandas / requests split it.

---

## 5. Requirements

- **R1** — A private `stellium._logging` exposes `get_logger(name)` returning a
  child of the `stellium` root logger.
- **R2** — At import, the `stellium` root logger gets a `NullHandler` (standard
  library-author pattern) so unconfigured use is silent.
- **R3** — A public `configure_logging(...)` convenience attaches a
  `StreamHandler` at a chosen level.
- **R4** — A warnings hierarchy rooted at `StelliumWarning(UserWarning)` with
  purpose-specific subclasses; `MissingEphemerisWarning` reparented under it
  (kept importable from `stellium.engines` for back-compat).
- **R5** — All 20 library print sites converted per [§6.3](#63-per-site-classification).
- **R6** — All 32 CLI/tooling print sites converted to `click.echo`/Rich
  `Console`.
- **R7** — `ruff` `T20` bans `print()` in `src/stellium` with an allow-list of
  exactly one file (`presentation/builder.py`, the `render()` product path).
- **R8** — Each converted site has coverage (`pytest.warns`, `caplog`, or Click
  `CliRunner`).

---

## 6. Design

### 6.1 Logging infrastructure

New module **`src/stellium/_logging.py`** (underscore avoids shadowing stdlib
`logging` on relative imports):

```python
import logging

_ROOT = "stellium"

def get_logger(name: str) -> logging.Logger:
    """Return the `stellium.<name>` logger. Library code logs through this."""
    return logging.getLogger(f"{_ROOT}.{name}" if name else _ROOT)

# NullHandler once, at import, so unconfigured use is silent.
logging.getLogger(_ROOT).addHandler(logging.NullHandler())
```

Usage:

```python
from stellium._logging import get_logger
log = get_logger(__name__.removeprefix("stellium."))  # e.g. "utils.cache"
log.warning("Could not write to cache: %s", exc)       # lazy %-formatting
```

Public convenience (top-level re-export):

```python
def configure_logging(level="INFO", *, stream=None, fmt=None) -> None:
    """One-call setup for apps/scripts that want Stellium's logs on screen."""
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt or "%(name)s %(levelname)s %(message)s"))
    root = logging.getLogger(_ROOT)
    root.addHandler(handler)
    root.setLevel(level)
```

Rules: library code never calls `basicConfig`, sets levels, or adds non-null
handlers — that's the app's job. Hot paths use lazy `log.debug("x=%s", v)`.

### 6.2 Warnings hierarchy

New module **`src/stellium/exceptions.py`** (warnings now, custom exceptions
later; avoids shadowing stdlib `warnings`):

```python
class StelliumWarning(UserWarning):
    """Base class for all Stellium warnings — filter this to silence them all."""

class DataQualityWarning(StelliumWarning):
    """Input data is malformed, incomplete, or was skipped (I/O, registry)."""

class GeocodingWarning(StelliumWarning):
    """A location could not be geocoded / the geocoding service failed."""

class ConfigurationWarning(StelliumWarning):
    """A config value was invalid and ignored (e.g. a bad orb 'by_pair' key)."""

class MissingEphemerisWarning(StelliumWarning):
    """Ephemeris file(s) unavailable; affected bodies were skipped."""
```

`engines/ephemeris.py` re-imports `MissingEphemerisWarning` from here and keeps
its export, so `from stellium.engines import MissingEphemerisWarning` still
works. One filter silences everything:
`warnings.filterwarnings("ignore", category=StelliumWarning)`.

### 6.3 Per-site classification

**Library (20 sites) → warnings/logging:**

| Sites | Channel | Class / Level | Rationale |
|---|---|---|---|
| `io/csv.py` (3), `io/dataframe.py` (3), `io/aaf.py` (1) | **warn** | `DataQualityWarning` | Caller's import data has bad rows. |
| `data/registry.py` (3) | **warn** | `DataQualityWarning` | Malformed notable YAML. |
| `core/native.py` (2) | **warn** | `GeocodingWarning` | Geocoding failure, often actionable. |
| `engines/orbs.py` (1) | **warn** | `ConfigurationWarning` | Invalid orb-config key from caller. |
| `components/arabic_parts.py` (1) | **warn** | `DataQualityWarning` | A requested part couldn't be computed. |
| `visualization/layers/houses.py` (2) | **warn** | `ConfigurationWarning` | Asked to draw a house system the chart lacks. |
| `utils/cache.py` (1) | **log** | `warning` | Cache-write failure is internal/recoverable. |
| `data/paths.py:138` | **log** | `warning` | Ephemeris file-copy failure — operational. |
| `data/paths.py:209,221` | **log** | `info` | One-time setup progress. |

→ **17 warnings, 3 logs.**

**CLI / tooling (32 sites) → `click.echo` / Rich:**

| Sites | Target | Notes |
|---|---|---|
| `cli/ephemeris_download.py` (16) | `click.echo` (+ `err=True` for diagnostics) | Already inside Click commands. |
| `utils/cache_utils.py` (13) | **relocate** → `cli/` + Rich `Console` | ✅ **Done.** It is now `cli/cache.py`, rebuilt on Rich. The file no longer exists under `utils/`, which is the spec working, not the spec rotting. |
| `data/notables/generate_index.py` (3) | `click.echo` | `click.echo` needs no command context; works in a plain script. |

**Kept (3 sites):** `presentation/builder.py:2094,2101,2107` — this is
`render()`'s product output. Retained; the sole lint allow-list.

### 6.4 Enforcement (lint guard)

`pyproject.toml`:

```toml
[tool.ruff.lint]
extend-select = ["T20"]          # T201 print, T203 pprint

[tool.ruff.lint.per-file-ignores]
"src/stellium/presentation/builder.py" = ["T20"]  # render() product output
"tests/**"                             = ["T20"]
"examples/**"                          = ["T20"]
```

One allow-listed file. Any new bare `print()` in the library or CLI fails
`ruff check` in CI — the invariant is self-enforcing.

---

## 7. Public API surface

Added to the top-level `stellium` namespace:

| Symbol | Purpose |
|---|---|
| `configure_logging(level="INFO", *, stream=None, fmt=None)` | One-call log setup. |
| `StelliumWarning` | Base warning — filter to silence all Stellium warnings. |
| `DataQualityWarning`, `GeocodingWarning`, `ConfigurationWarning`, `MissingEphemerisWarning` | Targeted filtering. |

`get_logger` stays private (`stellium._logging`).

---

## 8. Migration plan (phased, each independently shippable)

- **Phase 0 — Infrastructure (no behavior change).** `_logging.py`,
  `exceptions.py`, `configure_logging`, `NullHandler`; reparent
  `MissingEphemerisWarning`; export public symbols. Tests: import silence,
  handler attach, warning `issubclass` checks.
- **Phase 1 — Library warnings (17).** io/native/orbs/houses/arabic_parts/
  registry → typed warnings with `stacklevel=2`. Test each with `pytest.warns`.
- **Phase 2 — Library logs (3).** cache + ephemeris-copy → `log.warning`;
  ephemeris-init → `log.info`. Test with `caplog`.
- **Phase 3 — CLI / tooling (32).** `cli/` + `cache_utils` + `generate_index` →
  `click.echo`/Rich. Test representative commands with Click `CliRunner`.
- **Phase 4 — Enforce.** Turn on `ruff` `T20` with the single allow-list; fix any
  stragglers surfaced.
- **Phase 5 — Docs.** User guide "Diagnostics & Logging"; `CONTRIBUTING.md` rule
  ("library code must not `print`; CLI uses `click.echo`/Rich"); link this spec
  from `docs/development/README.md`.
- **Phase 6 — Web app adoption.** The NiceGUI app calls `configure_logging()` at
  startup and installs a `warnings` capture (`warnings.showwarning` override, or
  `logging.captureWarnings(True)` routed to a UI/notification sink) so Stellium
  `StelliumWarning`s and logs surface in the app rather than the server console.
  Lives in `web/`, not the library.

Phases 1–3 can be split further per module for smaller PRs; the lint guard
(Phase 4) lands only once the tree is clean. Phase 6 depends on Phase 0's public
API (`configure_logging`, the warning classes) but is otherwise independent.

---

## 9. Testing strategy

- **Silence-on-import:** capture stdout/stderr around `import stellium` + a chart
  calc; assert empty.
- **Warnings:** per site, `with pytest.warns(<Subclass>): …`; assert message and
  that `stacklevel` blames the caller frame.
- **Logs:** `caplog.at_level("INFO", logger="stellium")`; assert level/name/
  message; assert nothing logs above the set level.
- **CLI:** Click `CliRunner`; assert `result.output` / `result.stderr` and exit
  code.
- **Filtering:** assert `filterwarnings("ignore", category=StelliumWarning)`
  silences a subclass.
- **Lint:** CI `ruff check` is the regression test for G4.

---

## 10. Resolved decisions

All open questions were resolved in review (2026-07-09):

- **Q1 — Module names → split.** `_logging.py` (logging setup) + `exceptions.py`
  (warning hierarchy) as separate concerns.
- **Q2 — `configure_logging` → yes**, shipped in v1.
- **Q3 — Warning granularity → four subclasses** (`DataQuality`, `Geocoding`,
  `Configuration`, `MissingEphemeris`) under `StelliumWarning`.
- **Q4 — `cache_utils` → relocate + redesign.** The cache-info display is
  CLI-presentation logic mis-filed in `utils/`; move it under `cli/` (e.g.
  `cli/_display.py` or fold into `cli/cache.py`) and rebuild it on Rich `Console`
  rather than converting print-by-print in place. `utils/cache.py` (the actual
  cache engine) stays put and keeps only its one `log.warning`.
- **Q5 — Web app adoption → in scope.** The NiceGUI app calls
  `configure_logging()` at startup and installs a `warnings` capture so Stellium
  diagnostics surface in the UI (or the app's log), not the server console. See
  Phase 6.
- **Spec home → `docs/development/specs/`** (tracked); **loguru rejected** for
  stdlib logging (§4.1); **CLI cleanup in scope** (§6.3, Phase 3).

---

## 11. Acceptance criteria

- [ ] AST scan finds **zero** bare `print()` in `src/stellium` except
      `presentation/builder.py` (render product output).
- [ ] `ruff check` fails on a newly introduced `print()` anywhere else.
- [ ] `import stellium` + a chart calculation emit nothing to stdout/stderr.
- [ ] Every converted site is covered by `pytest.warns`, `caplog`, or `CliRunner`.
- [ ] `warnings.filterwarnings("ignore", category=StelliumWarning)` silences all
      Stellium warnings in one line.
- [ ] `configure_logging("DEBUG")` surfaces library logs; default stays silent.
- [ ] `MissingEphemerisWarning` still importable from `stellium.engines`.
- [ ] CLI output unchanged in content; now via `click.echo`/Rich and testable
      with `CliRunner`. Cache-info display relocated out of `utils/` into `cli/`.
- [ ] Web app surfaces Stellium warnings/logs in the UI (or app log) via
      `configure_logging()` + a warnings capture, not the server console.
- [ ] `CONTRIBUTING.md` documents the decision rule; a user guide covers
      `configure_logging` and the warning classes; this spec is linked from
      `docs/development/README.md`.

---

## Appendix A: Full inventory

**55 runtime `print()` calls** (AST-verified). **20 library** + **32 CLI/tooling**
convert; **3 render** kept.

**Library (→ warnings/logging):**

| File:line | Current | → Target |
|---|---|---|
| `components/arabic_parts.py:258` | `Warning: Could not calculate {part}` | `DataQualityWarning` |
| `core/native.py:571,574` | geocoding unavailable / error | `GeocodingWarning` |
| `data/paths.py:138` | `Could not copy {filename}` (stderr) | `log.warning` |
| `data/paths.py:209,221` | ephemeris-init banner / count | `log.info` |
| `data/registry.py:80,88,119` | failed read / no location / load fail | `DataQualityWarning` |
| `engines/orbs.py:194` | `Invalid 'by_pair' key` | `ConfigurationWarning` |
| `io/aaf.py:248` | `Skipping malformed record` | `DataQualityWarning` |
| `io/csv.py:605-609` | `Skipped N row(s)` (+detail) | `DataQualityWarning` |
| `io/dataframe.py:139-143` | `Skipped N row(s)` (+detail) | `DataQualityWarning` |
| `utils/cache.py:82` | `Could not write to cache` | `log.warning` |
| `visualization/layers/houses.py:93,254` | `House system … not found` | `ConfigurationWarning` |

**CLI / tooling (→ `click.echo` / Rich):**

| File | Count | Target |
|---|---|---|
| `cli/ephemeris_download.py` | 16 | `click.echo` (`err=True` for diagnostics) |
| ~~`utils/cache_utils.py`~~ → `cli/cache.py` | 13 | Rich `Console` ✅ |
| `data/notables/generate_index.py` | 3 | `click.echo` |

**Kept (render product output):** `presentation/builder.py:2094,2101,2107`.

*The 128 non-runtime `print(` matches* are docstring examples (`>>> print`,
`Example::`) and Rich `console.print()` — documentation and product output,
out of scope.
