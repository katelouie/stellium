# Design specs

Spec-Driven Development (SDD) design docs: a change described *before* it's built —
motivation, design, migration plan, acceptance criteria. (The reference pages in
[`../`](../README.md) describe the code as it *is*; specs describe what it *should
become*.)

## Active

- **[STRUCTURE_FIRST_SECTIONS.md](./STRUCTURE_FIRST_SECTIONS.md)** — sections stringify
  too early, which blocks three roadmap items at once: the Typst PDF theme can't style
  what it can't see, interactive HTML reports can't sort a string, and i18n can't
  translate one that was already composed in English. Makes the structured payload the
  section contract and moves composition into the renderers, where a locale can apply.
  Folds in the Chinese-translation task. The pseudolocale doubles as a completeness
  oracle for the refactor. Phase 0 done; Phase 1 approved.

- **[STRUCTURED_LOGGING_SPEC.md](./STRUCTURED_LOGGING_SPEC.md)** — migrate the
  library's remaining bare `print()`s to stdlib `logging`/`warnings` (and
  `click.echo`/Rich for the CLI), with a lint guard. The infrastructure
  (`configure_logging`, `stellium._logging`) has landed; the `print()` migration is
  still in progress.

## [`rectification/`](./rectification/) — the rectification arc

The full computational birth-time rectification research: theory, phased specs, the
63-person verified corpus + events, tooling, and the concluded empirical study. The
validated result (sect recovery) shipped as the `stellium.rectification` subsystem.
See **[rectification/README.md](./rectification/README.md)**.

## [`archive/`](./archive/) — completed specs

Specs for features that have since shipped, kept for historical context:

- **HELLENISTIC_PERIODS_SPEC.md** — `core/planetary_years.py` primitive + the
  Firdaria time-lord engine (shipped).
- **LENGTH_OF_LIFE_SPEC.md** — the hyleg → alcocoden years-table technique (shipped
  as `engines/length_of_life.py`).
