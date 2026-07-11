# Birth-hour distribution — Claude Deep Research prompt

> Gathers an **external, cited hourly distribution of human birth times** to
> replace the uniform-birth-time assumption in the rectification sect prior. It
> must be population-level published data — NOT anyone's chart sample — so it can
> serve as an honest prior without leaking. Plugs into
> `sect_classifier.daylight_fraction` as an `f(h)`-weighted `P(day)`.

---

## Prompt

**Goal.** Compile a **distribution of the time of day at which human births
occur** — ideally hour-by-hour (0–23 local time) relative frequencies — from
**published, citable sources** (national vital-statistics offices, demographic /
epidemiological studies, e.g. NBER, CDC/NCHS, ONS, INSEE, historical parish-record
studies). This is population base-rate data; do **not** use astrological chart
collections or birth-time databases.

**Why the shape matters (collect enough to distinguish these):**
- **Spontaneous / non-intervened births** cluster in the **early morning**
  (roughly 01:00–06:00, peak ~04:00) — the "natural" nocturnal-labour pattern.
- **Scheduled / induced / C-section births** cluster on **weekday mornings**
  (~08:00–12:00). This share has risen steeply over the 20th century, so the
  aggregate distribution is **era-dependent**.
- So please break the data down, where available, by:
  - **era** (pre-1950 / "natural" vs. modern medicalized — most important),
  - **delivery mode** (spontaneous vs. induced/caesarean),
  - **region / country**, and **season** if any source reports it.

**Why era matters for us:** our target charts span ~1450–1980 but concentrate in
1850–1970 and are international — so a **spontaneous / pre-medicalization** hourly
curve is the most useful single distribution, with a modern curve as a secondary.

**For each distribution collected, report:**
1. A **table of hour → relative frequency** (24 rows, or as fine as the source
   gives; normalise to sum 1 if you can, else give raw counts).
2. The **source** (author/agency, year, title, link), the **population** (country,
   years covered, sample size), and the **delivery-mode / era** it represents.
3. Any stated **caveats** (local vs. standard time, rounding to the hour, hospital
   vs. home births).

**Deliverable.** A short set of **named hourly distributions** (e.g.
`spontaneous_prewar`, `all_modern_us`, …), each as a 24-value table with its
citation and population note, plus a one-paragraph summary of how they differ and
which is the best default for a historical, international cohort. Prefer 2–4
well-sourced curves over many shaky ones. YAML or a markdown table is fine.
