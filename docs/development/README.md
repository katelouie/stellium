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
8. **[NOTABLES.md](./NOTABLES.md)** — the notables database: schema, what each
   provenance field means, Old Style (Julian) dates, and the rules for curating a
   record so it stays auditable.
9. **[EXTENDING.md](./EXTENDING.md)** — how to plug in every protocol
   (engines, components, analyzers, layers, themes, palettes, report sections).

## Design specs

Spec-Driven Development (SDD) design docs live in [`specs/`](./specs/) — see
**[specs/README.md](./specs/README.md)** for the index. Unlike the reference pages
above (which describe the code as it *is*), specs describe a change *before* it's
built — motivation, design, migration plan, and acceptance criteria.

- **Active:** [specs/STRUCTURED_LOGGING_SPEC.md](./specs/STRUCTURED_LOGGING_SPEC.md)
  — migrate the library's remaining bare `print()`s to stdlib `logging`/`warnings`
  (infrastructure landed; migration in progress).
- **Completed** (`specs/archive/`): Hellenistic periods (`core/planetary_years.py`
  + Firdaria engine) and length of life (hyleg → alcocoden years-table) — both
  shipped; specs kept for history.
- **Rectification** (`specs/rectification/`): the full computational birth-time
  rectification arc — theory, phased specs, the 63-person verified corpus + events,
  and the concluded empirical study. See
  **[specs/rectification/README.md](./specs/rectification/README.md)**; the capstone
  is [RECTIFICATION_REPORT.md](./specs/rectification/RECTIFICATION_REPORT.md). The
  validated result (sect recovery) shipped as the `stellium.rectification` subsystem
  — see [SUBSYSTEMS.md](./SUBSYSTEMS.md).

## How these docs are scoped

Depth is concentrated on the most-used path (chart building, engines,
components, visualization, reports); peripheral subsystems get lighter pointers
to the entry point + the file to read. When a doc and the source disagree, the
**source wins** — and please update the doc.

User-facing guides live one level up in [`docs/`](../) (e.g.
[`VISUALIZATION.md`](../VISUALIZATION.md), [`REPORTS.md`](../REPORTS.md),
[`CHART_TYPES.md`](../CHART_TYPES.md)). See the full
[documentation index](../DOCS_INDEX.md).
