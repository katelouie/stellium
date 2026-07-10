# Rectification corpus — Claude Deep Research prompt

> Reusable prompt for building the birth-time-rectification **validation /
> calibration corpus** in a **single authoritative pass**. It is designed to
> *terminate the verify-reject loop*: Deep Research independently establishes
> each candidate's birth-time provenance from primary sources and only then
> gathers events — so nothing enters the corpus on the strength of a rating we
> merely asserted. Companion candidate roster:
> [rectification-corpus-candidates.md](./rectification-corpus-candidates.md).
> Why the data is shaped this way: [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md).

---

## Prompt

**Role & goal.** You are assembling *and independently verifying* a research
dataset for validating a **computational birth-time rectification** system. The
system infers an unknown birth **time** from a person's dated life events and
temperament. To test it we need people whose **true birth time is provably
documented**, so we can blank the time, feed the system their life events, and
check whether it recovers the truth.

**Read this first — the trust rule that governs everything.** You will be given
a roster of candidate **names**, possibly with birth dates/times/places and
"ratings" attached. **Treat every one of those fields as an UNVERIFIED HINT and
nothing more.** They come from a database whose birth-time ratings have
repeatedly proven wrong — rectified (astrologically *computed*) times sold as
birth-certificate "AA", uncited biography quotes sold as "A", aggregator guesses
sold as documented. **You must independently re-establish every birth time from
its source.** A person enters the corpus only when you can quote a primary /
AstroDataBank source note that proves a real record. When in doubt, reject.

This is a **two-phase** job. Do Phase 1 (verify) for a candidate before you spend
any effort on Phase 2 (gather). Rejected candidates cost you nothing further.

---

### Phase 1 — Provenance verification (the gate)

For each candidate, find the **AstroDataBank** entry
(`astro.com/astro-databank/...`) and read its **birth-data source note** and
**Rodden rating**. Then classify the **time's** provenance into exactly one
bucket and **quote the source note verbatim** as evidence:

| Bucket | What the source note shows | Verdict |
|---|---|---|
| `document` | birth certificate, civil/hospital register, or contemporaneous family record | **ACCEPT** (AA) |
| `memory` | quoted "from memory" by the person / family / close associate | **ACCEPT (soft)** (A — real but less sharp) |
| `biography` | a book/author states a time **without citing where they got it** | **REJECT** for ground truth (usable only as soft personality data) |
| `rectified` | time was astrologically **computed** (Starkman, Marr, "rectified", "speculative", "quoted nativity") | **HARD REJECT** |
| `aggregator` | the only trail is Astro-Seek, Astrotheme, AstroSage, Astro-Charts, Astrologify, Wikidata, etc. | **HARD REJECT** |
| `unknown` / `noon` | no recorded time, or a 12:00 / 00:00 placeholder | **HARD REJECT** |

**`rectified` is the single most dangerous class and an automatic reject:** a
time produced by rectification cannot be used to validate a rectifier — it would
grade our system against another astrologer's guess and look like agreement.

**Red flags — do NOT accept on face value; confirm the document:**
- **Suspiciously precise times** (e.g. `14:49:20`). Precision usually signals
  **rectification**, not a record. (This is exactly how Richard Feynman's
  "AA" turned out to be an Isaac Starkman rectification.) Confirm it traces to a
  document; if it traces to a rectifier, `rectified` → reject.
- **Round-hour AAs** (`03:00`, `18:00`) — many are aggregator fakes. Require an
  actual certificate note.
- **Non-US/UK certificates** (Brazil, India, …) where civil registration often
  lagged the birth by days: **accept the date, treat the minute as soft** —
  still `document`, but note the softness.
- **Entertainers & politicians self-reporting.** Per Rodden's own warning they
  misreport freely; require an independent document, distrust the self-report.
- Any "AA" whose only citation is an aggregator site → it is really `unverified`;
  reject until an ADB document note is sighted.

**Phase-1 output per candidate** (you will place these under `accepted:` or
`rejected:` in the final YAML):
```yaml
name: ...
adb_url: ...
rodden_rating_verified: "AA" | "A" | "B" | "C" | "DD" | "X"
provenance_bucket: document | memory | biography | rectified | aggregator | unknown
source_note_quote: "…verbatim ADB / primary source note…"   # REQUIRED to accept
verdict: accept | accept_soft | reject
reason: "one line"
```

Prefer to also draw candidates from **known-clean AA collections** (Rodden's own
published AA data, the Astrological Association AA chart database) — not only the
supplied roster.

---

### Phase 2 — Gather (ACCEPTED candidates only)

Only for people who passed Phase 1, collect:

1. **Birth data** — the **verified** date, local clock time, timezone, place
   (city/region/country), latitude/longitude — **exactly as the document gives
   it**, re-derived, not copied from the hint. Carry the `rodden_rating_verified`
   and `source_note_quote` from Phase 1.

2. **Life events** — **at least 6** major, dated events across **different life
   stages** and **types**. For each: the **date** (as precise as the record
   allows), a **precision** flag (`day` / `month` / `year`), an **event type**
   from the taxonomy below, a one-line **description**, a **significance**
   (`major` / `moderate` / `minor`), the **age** at the event if computable, and
   a **source**. **Never fabricate a precise date** — mark it `year` precision if
   that is all that is known.

   **Event-type taxonomy** (use these keys): `relationship`, `career`,
   `recognition`, `relocation`, `bereavement_parent`, `bereavement_other`,
   `childbirth`, `health_crisis`, `accident`, `windfall`, `financial_loss`,
   `legal`, `education`, `spiritual`, `other`.

3. **Temperament** — **at least 4** concise, well-attested character descriptors,
   each with **how it's attested** (biographer, contemporaries, self-description)
   and a **source**. Prefer widely-corroborated traits over pop-psych labels.

---

### Sourcing & honesty rules

- **Cite every datum.** A person is accepted **only** with a verbatim source-note
  quote proving `document` or `memory`.
- **Never reuse the hint data as if verified.** Re-derive it.
- **If AstroDataBank is inaccessible or silent, reject** (`unknown`) — do not
  guess a rating.
- **A smaller bulletproof corpus beats a larger shaky one. 15 airtight > 30
  dubious.** Do not pad.
- Flag uncertainty (conflicting dates/times) explicitly.

---

### Output format

Return a **single YAML document** with **two** top-level lists:

```yaml
accepted:
  - name: Albert Einstein
    adb_url: "https://www.astro.com/astro-databank/Einstein,_Albert"
    rodden_rating_verified: "AA"
    provenance_bucket: "document"
    source_note_quote: "Birth certificate in hand (quoted on AstroDataBank)."
    birth_data:
      date: "1879-03-14"
      time: "11:30"                 # local, 24-hour, from the document
      timezone: "Europe/Berlin"
      place: "Ulm, Germany"
      latitude: 48.4011
      longitude: 9.9876
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
      # ... >= 6 events, mixed types and life stages

rejected:
  - name: Richard Feynman
    adb_url: "https://www.astro.com/astro-databank/Feynman,_Richard"
    rodden_rating_verified: "C"
    provenance_bucket: "rectified"
    source_note_quote: "Time rectified by Isaac Starkman to 14:49:20 EWT; birth time otherwise unknown."
    verdict: "reject"
    reason: "Rectified time — cannot validate a rectifier. Not a certificate."
```

The `rejected:` list is **not** waste — it is how we **permanently correct our
own database** (fixing the bad `data_quality` / `has_reliable_time` values that
caused this), so this loop does not have to run again.

---

### Deliverable

The two-section YAML, plus a short prose summary: how many candidates you
verified, the accept/reject counts by `provenance_bucket`, the final corpus size,
and any notable figures you had to reject (with the source-note quote that
condemned them).
