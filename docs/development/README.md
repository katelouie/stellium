# Stellium Developer Docs (Agent Reference)

> 🤖 **These docs are primarily for coding agents. Hello, Claude!**
> This folder is written for AI coding agents (and human contributors) working
> on Stellium. If you're an agent: read the relevant page here **before**
> re-deriving the API from source — that's the whole point. When a doc disagrees
> with the code, **the code wins** — please update the doc as you go.

This folder is the durable reference for a coding agent working on Stellium —
so you don't have to re-learn the API and architecture each session. The hub is
[`/CLAUDE.md`](../../CLAUDE.md) (workflow, environment, conventions); these
spokes hold the technical detail.

## Read in this order

1. **[ARCHITECTURE.md](./ARCHITECTURE.md)** — the mental model, layer map,
   dependency rules, and what `.calculate()` does. **Start here.**
2. **[CHART_BUILDING.md](./CHART_BUILDING.md)** — `Native`/`Notable`,
   `ChartBuilder`, `CalculatedChart`, config, registries. The core path.
3. **[ENGINES.md](./ENGINES.md)** — ephemeris, houses, aspects, orbs,
   dignities, patterns, dispositors, profections, fixed stars, etc.
4. **[COMPONENTS_AND_ANALYSIS.md](./COMPONENTS_AND_ANALYSIS.md)** — optional
   components, the pandas analysis toolkit, file IO, caching, utils.
5. **[VISUALIZATION_INTERNALS.md](./VISUALIZATION_INTERNALS.md)** — SVG
   pipeline, coordinate system, layers, themes/palettes, dial/vedic/atlas.
6. **[PRESENTATION_INTERNALS.md](./PRESENTATION_INTERNALS.md)** —
   `ReportBuilder`, sections, renderers (rich/markdown/html/pdf/prose).
7. **[SUBSYSTEMS.md](./SUBSYSTEMS.md)** — pointers: multi-chart, returns,
   electional, planner, Chinese/BaZi, CLI, progressions.
8. **[EXTENDING.md](./EXTENDING.md)** — how to plug in every protocol
   (engines, components, analyzers, layers, themes, palettes, report sections).

## Design specs

Spec-Driven Development (SDD) design docs for planned work live in
[`specs/`](./specs/). Unlike the reference pages above (which describe the code
as it *is*), specs describe a change *before* it's built — motivation, design,
migration plan, and acceptance criteria.

- **[specs/STRUCTURED_LOGGING_SPEC.md](./specs/STRUCTURED_LOGGING_SPEC.md)** —
  replace bare `print()` in the package with stdlib `warnings`/`logging` (and
  `click.echo`/Rich for the CLI), plus a lint guard. *Status: Implemented.*
- **[specs/HELLENISTIC_PERIODS_SPEC.md](./specs/HELLENISTIC_PERIODS_SPEC.md)** —
  a canonical `core/planetary_years.py` primitive (least/mean/greater/greatest +
  Firdaria), ZR refactored onto it, and a new Firdaria time-lord engine. *Status:
  Draft.*
- **[specs/LENGTH_OF_LIFE_SPEC.md](./specs/LENGTH_OF_LIFE_SPEC.md)** — the
  classical length-of-life technique (hyleg → alcocoden → years-table, Lilly
  default) plus reusable almuten-of-a-degree and hyleg primitives. *Status:
  Draft.*
- **[specs/RECTIFICATION_THEORY.md](./specs/RECTIFICATION_THEORY.md)** &
  **[specs/RECTIFICATION_SPEC.md](./specs/RECTIFICATION_SPEC.md)** — computational
  birth-time rectification: a hierarchical Bayesian grid posterior over birth time
  with the astrology engine as an exact forward model, sect read off as a marginal,
  the likelihood calibrated on the AA-notables corpus. Theory doc explains the
  model; spec doc has the data models, API, and phased plan (companion research
  prompt: [specs/rectification-corpus-research-prompt.md](./specs/rectification-corpus-research-prompt.md)
  — a single-pass *verify-then-gather* prompt that provenance-checks every
  candidate from primary sources before it can enter the corpus, and returns its
  rejections so they back-correct our notables DB; roster:
  [specs/rectification-corpus-candidates.md](./specs/rectification-corpus-candidates.md)).
  *Status: Exploration.*

## How these docs are scoped

Depth is concentrated on the most-used path (chart building, engines,
components, visualization, reports); peripheral subsystems get lighter pointers
to the entry point + the file to read. When a doc and the source disagree, the
**source wins** — and please update the doc.

User-facing guides live one level up in [`docs/`](../) (e.g.
[`VISUALIZATION.md`](../VISUALIZATION.md), [`REPORTS.md`](../REPORTS.md),
[`CHART_TYPES.md`](../CHART_TYPES.md)). See the full
[documentation index](../DOCS_INDEX.md).
