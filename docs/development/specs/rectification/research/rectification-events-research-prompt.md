# Rectification corpus — Phase 2 (events + temperament) research prompt

> Gathers the **life events** (hard data) and **temperament** (soft data) for the
> already-provenance-verified corpus. Workflow: paste one or more AstroDataBank
> pages (from the worklist URLs) into Claude Deep Research with this prompt; it
> treats the paste as a **seed**, verifies and **expands** it, and returns
> per-person YAML that drops straight into the rectifier's `LifeEvent`/`Evidence`
> models. Worklist + frozen birth data:
> [rectification-events-worklist.md](./rectification-events-worklist.md). Why the
> data is shaped this way: [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md).

---

## Prompt

**Role & goal.** You are enriching a *birth-time-rectification validation corpus*.
Each person's birth time has **already been provenance-verified** — that work is
done and is **not** up for revision here. Your job is to compile, for each person
I give you, (a) their major **dated life events** (hard data) and (b) their
**temperament** (soft data), each carefully sourced. These feed a system that
infers birth time from life events, so the events must be **real, well-dated
facts** and the temperament **well-attested**.

**What I will give you.** For each person: their **name and frozen birth data**
(date, time, place — already verified, do **not** change or re-litigate it), and
usually the **pasted text of their AstroDataBank page**, which often includes a
short "Events" list and a biography.

**How to treat the paste — seed, not ceiling.**
- The pasted **Events** list is a **starting point**. AstroDataBank event lists
  are typically short and astrologer-selected — take what's there, then
  **verify each date against independent biographical sources and EXPAND** with
  the major dated events the page omits.
- Extract the **factual event** (what happened, when), never AstroDataBank's
  astrological annotation of it (ignore any "chart", "Placidus", aspect, or
  transit commentary attached to an event).
- If no page was pasted for someone, gather from scratch from biographies.
- **Do not touch the birth data.** Echo it back verbatim for convenience.

**What makes a good event (optimize for this).** The rectifier keys on **major,
sharply-dateable turning points** that astrological timing techniques activate.
Favor high-signal events and record precision honestly:
- **Aim for ≥ 6 events per person**, spanning **different life stages** (youth →
  late life) and **different types** (don't return six of the same kind).
- Prize the **sharply dateable** and **high-severity**: marriages/divorces,
  sudden fame or a breakthrough, relocations/emigration/exile, bereavements,
  childbirth, accidents/health crises, imprisonment/trials, major windfalls or
  losses. A precisely-dated relocation is worth more than a fuzzy "career grew."
- Record a **precision** flag honestly: `day` (full date known), `month`, or
  `year`. **Never fabricate a precise date** — down-flag to `month`/`year` if
  that is all the record supports.
- If you genuinely cannot reach 6 well-dated events (e.g., a pre-modern figure),
  **say so and return what is solid** — do not pad with vague filler.

**Event-type taxonomy** (use these keys): `relationship` (marriage/partnership/
divorce), `career` (job start/change, founding, major work), `recognition`
(award, breakthrough, sudden fame), `relocation` (move/emigration/exile),
`bereavement_parent`, `bereavement_other`, `childbirth`, `health_crisis`,
`accident`, `windfall`, `financial_loss`, `legal` (arrest/trial/imprisonment),
`education` (graduation/major milestone), `spiritual` (conversion/turning point),
`other`.

**Temperament (soft data).** Provide **≥ 4** concise, well-attested character
descriptors — the kind a biographer or contemporaries would corroborate, not
pop-astrology. For each: a short **trait** phrase, 1–3 lowercase **tags**
(e.g. `disciplined`, `private`, `impulsive`, `ambitious`, `nurturing`,
`combative`, `optimistic`, `melancholic`), **how it's attested** (biographer,
contemporaries, self-description), and a **source**. Prefer widely-corroborated
traits over single anecdotes.

**Sourcing & honesty rules.**
- **Cite every event and every trait.** Prefer primary/biographical sources.
- Flag conflicts (disputed dates) rather than silently picking one.
- **Never invent a date or a trait.** Missing > fabricated.
- Quality over quantity: a tight set of well-dated, high-severity events beats a
  padded list.

**Output format.** Return a single **YAML** document — a list of people, each in
exactly this shape (this maps directly onto our data models, so keep the keys):

```yaml
- name: Albert Einstein
  birth_data:                          # ECHO verbatim from what I gave you; do not alter
    date: "1879-03-14"
    time: "11:30"
    place: "Ulm, Germany"
  events:
    - date: "1903-01-06"
      precision: "day"
      type: "relationship"
      description: "Married Mileva Marić"
      significance: "major"            # major | moderate | minor
      age_at_event: 23
      source: "Isaacson (2007), ch. 5"
    - date: "1905"
      precision: "year"
      type: "recognition"
      description: "Annus mirabilis — four landmark papers"
      significance: "major"
      age_at_event: 26
      source: "Isaacson (2007)"
    # ... aim for >= 6, mixed types and life stages
  temperament:
    - trait: "fiercely independent, rebellious toward authority"
      tags: ["independent", "rebellious"]
      evidence: "consistent across biographers and his own letters"
      source: "Isaacson, Einstein (2007)"
    # ... >= 4 traits
  notes: "any date conflicts, coverage gaps, or 'could not reach 6 events' flags"
```

**Deliverable.** The YAML for every person in the batch, plus a one-paragraph
summary: how many events per person you found, which people fell short of 6 (and
why), and any date conflicts you flagged.
