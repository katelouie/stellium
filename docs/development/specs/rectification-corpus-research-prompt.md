# Rectification corpus — Claude Deep Research prompt

> Reusable prompt for gathering the birth-time-rectification **validation /
> calibration corpus**: accurate-time notables with dated life events (hard data)
> and temperament notes (soft data). Copy the block below into Claude Deep
> Research. Context for *why* this data is shaped the way it is:
> [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md).

---

## Prompt

**Role & goal.** You are assembling a research dataset for validating a
*computational birth-time rectification* system. Rectification infers an unknown
birth **time** from a person's dated life events and temperament. To test the
system we need people whose **true birth time is well documented**, so we can
blank the time, feed the system their life events, and check whether it recovers
the truth. Your job is to compile, for a set of such people, (a) their verified
birth data, (b) major **dated life events**, and (c) **temperament** notes — all
carefully sourced.

**Why the data must be shaped this way (optimize for this):**
- We need the **true time** to grade against → prefer people with a **Rodden
  rating of AA** (birth certificate / recorded) or at least **A** (from the
  person/family). Record the rating and its source. Skip anyone whose time is
  only speculative/rectified (DD/X) — they can't validate anything.
- The system detects **major, dateable turning points** that astrological timing
  techniques would activate. So collect **significant, well-dated events**, not
  trivia — and record the date **precision** honestly.
- Temperament feeds a separate "day-vs-night chart" signal, so a few **well-
  attested character descriptors** per person are valuable.

**Who to include.** Aim for **~25 people** (minimum 15 if quality is scarce),
**diverse** across era, gender, culture, and life-shape. Favor lives with
**dramatic, dateable pivots** (marriages, sudden fame, imprisonments, exiles,
accidents, bereavements) — these are the most informative. Well-documented
20th-century figures with AstroDatabank AA ratings are ideal, but historical
figures with reliable recorded times are welcome.

**For each person, collect:**

1. **Birth data** — date, local clock time, timezone, place (city/region/
   country), latitude/longitude, **Rodden rating**, and a **citation** for the
   birth data (AstroDatabank entry, birth certificate, biography). This is
   ground truth; do not guess it — omit the person if it isn't solid.

2. **Life events** — **at least 6** major, dated events, spanning **different
   life stages** and **different types**. For each: the **date** (as precise as
   the record allows), a **precision** flag (`day` / `month` / `year`), an
   **event type** from the taxonomy below, a one-line **description**, a
   **significance** rating (`major` / `moderate` / `minor`), the person's
   **age** at the event if computable, and a **source**. **Never fabricate a
   precise date** — mark it `year` precision if that's all that's known.

   **Event-type taxonomy** (use these keys): `relationship` (marriage/partnership
   /divorce), `career` (job start/change, founding, major work), `recognition`
   (award, breakthrough, sudden fame), `relocation` (move/emigration/exile),
   `bereavement_parent`, `bereavement_other`, `childbirth`, `health_crisis`
   (illness/surgery), `accident`, `windfall` (wealth/inheritance), `financial_loss`
   /bankruptcy, `legal` (arrest/trial/imprisonment), `education` (graduation/major
   milestone), `spiritual` (conversion/turning point), `other`.

3. **Temperament** — **at least 4** concise, well-attested character descriptors
   (e.g. "intensely private and disciplined"; "impulsive risk-taker"), each with
   **how it's attested** (biographer, contemporaries, self-description) and a
   **source**. Prefer widely-corroborated traits over pop-psych labels.

**Sourcing & honesty rules.**
- Cite **every** datum. Prefer primary/biographical sources; AstroDatabank for
  birth data + Rodden rating.
- Flag uncertainty explicitly (conflicting dates, disputed times) rather than
  papering over it.
- If you cannot find a solid true birth time, **drop that person** — an
  unverifiable time is worse than useless here.
- Do not pad with minor events to hit the count; quality and datedness over
  quantity.

**Output format.** Return a single **YAML** document: a list of people, each in
exactly this shape (fields may repeat; omit a field only if genuinely unknown):

```yaml
- name: Albert Einstein
  aliases: []
  birth_data:
    date: "1879-03-14"
    time: "11:30"                     # local, 24-hour
    timezone: "Europe/Berlin"         # IANA name (or UTC offset)
    place: "Ulm, Germany"
    latitude: 48.4011
    longitude: 9.9876
    rodden_rating: "AA"
    source: "AstroDatabank: birth certificate in hand"
  temperament:
    - trait: "fiercely independent, rebellious toward authority"
      evidence: "consistent across biographers and his own letters"
      source: "Isaacson, Einstein (2007)"
  events:
    - date: "1903-01-06"
      precision: "day"
      type: "relationship"
      description: "Married Mileva Marić"
      significance: "major"
      age_at_event: 23
      source: "Isaacson (2007), ch. 5"
    - date: "1905"
      precision: "year"
      type: "recognition"
      description: "Annus mirabilis — four landmark papers"
      significance: "major"
      age_at_event: 26
      source: "..."
    # ... >= 6 events, mixed types and life stages
```

**Deliverable.** The YAML dataset plus a short prose summary: how many people you
included, the distribution of Rodden ratings and event types, and any figures
you considered but dropped for lack of a reliable birth time (and why).
