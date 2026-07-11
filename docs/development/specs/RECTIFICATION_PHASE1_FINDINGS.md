# Phase 1 findings — sect classifier v0 (firdaria × significators)

| | |
|---|---|
| **Date** | 2026-07-11 |
| **Verdict** | **NO-GO** — firdaria-lord matching does not recover sect |
| **Code** | `docs/development/specs/rectification/` (sect.py, run_benchmark.py) |
| **Spec** | [RECTIFICATION_PHASE0_SPEC.md](./RECTIFICATION_PHASE0_SPEC.md) §5–6 |

## The experiment

Blank each of the 63 corpus people's birth time; predict day vs night from their
dated events alone, by matching the active firdaria time-lord (day-order vs
night-order) to each event's natural planetary significators (theory §6). This is
the pre-registered proving experiment: does the approach beat chance?

## Result

| Variant | Accuracy | Notes |
|---|---|---|
| Raw day-vs-night sums | 49.2% | strong **night bias** (predicted night 43/63) |
| Permutation-null de-confounded | 41.3% | bias gone, balanced confusion, still chance |
| Best achievable (any threshold, any ablation) | **54.0%** | = majority class ("always day") |

- 95% CI (de-confounded) = [30%, 54%] — **straddles 50%**.
- corr(continuous signal, true sect) = **−0.17 to −0.22** across all variants —
  slightly *negative*, ≈ 1.7 SE from zero at n=63, i.e. **indistinguishable from
  no signal**.
- Ablations (major-lord-only, major-events-only, ± sub-lord) all land at the
  majority-class 54%. The null is robust.

**Pre-registered gate (acc ≥ 65% AND CI-low > majority): NO-GO.**

## What we learned (the diagnosis)

1. **The raw comparison is confounded.** The night firdaria order front-loads
   Saturn/Jupiter/Mars in the event-dense early decades, and those are the
   *generically-significant* planets (Saturn signifies 8/15 event types). So the
   night ordering scores higher for *anyone*, regardless of true sect — a nuisance
   factor, not sect signal. A per-person permutation null removes it cleanly.
2. **De-confounded, there is simply no signal.** Firdaria periods are long
   (7–13 yr), so a documented life samples only ~5–7 distinct major lords — very
   few "measurements" of a type↔lord association that is itself weak. Firdaria
   lacks the resolution to fix sect.
3. This is a *clean, cheap* result: the shortcut of reading sect off firdaria
   alone — appealing because it's near time-independent — does not work. Better to
   know before building a posterior on it.

## Options from here (a genuine fork)

- **A — Sharp techniques, not coarse firdaria.** The theory's real claim is sect
  as the *marginal of the full event-posterior*. Firdaria was a hopeful shortcut;
  the signal may live in the **sharp, angle-tied techniques** (directions/transits
  to the angles, ZR peaks, profected-year lords) that the shortcut skipped. This
  is bigger (needs the candidate grid + more engines) but is the theoretically
  grounded path.
- **B — The sect-dependent dignity/lots channel** (spec §5.1 fallback): benefic/
  malefic *of the sect*, the sect light, and the Lot of Fortune/Spirit formula
  flip. Fuzzier and more temperament-linked (leans on the soft channel we
  deferred).
- **C — Reconsider whether events-only can fix sect at all**, vs. needing the
  temperament/chart-coherence signal a human rectifier actually uses.

The machinery (loader, harness, significators, benchmark, contrastive report) is
built, tested, and reusable for whichever direction we take.

---

## Phase 1B — malefic-contrary-to-sect probe (option B) — **SIGNAL**

`probe_malefic_sect.py`. Doctrine: the malefic *out of sect* is the sharper
destroyer — **Mars out of sect by day, Saturn out of sect by night** — so a life's
misfortunes should carry the flavour of its contrary-sect malefic. Prediction:
Mars-flavoured hardship → **day**, Saturn-flavoured → **night**. Nearly chart-free
(reads the *character* of the misfortunes via a priori Mars/Saturn keyword lists),
and a completely different mechanism from firdaria.

| metric | value |
|---|---|
| accuracy | **65.1%** (41/63) |
| decided-only (drop 14 keyword-silent ties) | 65.3% (32/49) |
| **corr(mars−saturn, day)** | **+0.346** — ≈ 2.9 SE from 0, **p ≈ 0.005** |
| 95% CI | [52.8%, 75.7%] (lower bound just under the 54% majority) |
| confusion | both diagonals dominant (day 22/12, night 10/19) |

**Pre-registered gate: still NO-GO** (CI-low 52.8% < majority 54%) — but this is a
*genuine, directionally-correct effect*, not the firdaria null. The extremes are
convincing: strongest-Saturn lives (Ted Bundy, Hannah Arendt, Ali, Obama) classify
night; strongest-Mars (Hemingway, Frida Kahlo, JFK, van Gogh, Plath) classify day.

**Interpretation:** events *do* carry sect information — via the malefic-of-sect
character of misfortune, **not** via the firdaria time-lord sequence. Modest
(65%), needs development, and the keyword lists carry some researcher DOF (set a
priori, but worth a holdout).

### Phase 1C — benefic-of-sect mirror + combination — **benefic is NULL**

`sect_signals.py`, `probe_sect_combined.py`. Symmetric hypothesis: Jupiter is
benefic *of sect* by day, Venus by night → Jupiter-flavoured fortune → day,
Venus-flavoured → night.

| signal | accuracy | corr(score, day) |
|---|---|---|
| malefic-only | 65.1% | **+0.346** |
| benefic-only | 52.4% | **+0.021** (null) |
| combined | 52.4% | +0.169 (diluted) |

The benefic mirror carries **no signal**, and combining it *dilutes* the malefic
(+0.35 → +0.17). Diagnosis: **fortune-character is domain-linked, not sect-linked**
— artists accumulate Venus-flavoured fortune (art/exhibitions), scientists and
politicians Jupiter-flavoured (awards/office), independent of sect — so the
benefic channel injects profession noise. Misfortune-character (sudden/violent vs
slow/chronic) is far more universal, which is why the malefic side works and the
benefic doesn't.

**Conclusion:** keep **malefic-only** (corr +0.346, p ≈ 0.005) as a real but
modest sect *prior*; drop the benefic. The cheap event-character approach tops out
≈ 65% — useful as one evidence stream, not a decisive classifier.

## Where things stand (post-B)

- Two mechanisms tried from events alone: firdaria timing = **null**;
  malefic-of-sect character = **real but modest** (65%, p≈0.005, doesn't clear the
  strict gate); benefic-of-sect = **null** (domain confound).
- Events *do* carry sect signal, but weakly and only through misfortune character.
  A decisive sect read likely needs the chart itself (option A: the sharp,
  angle-tied techniques → full posterior, sect as the marginal), which is the
  larger build we deferred.

---

## Phase A — time-posterior + the daylight prior — **first GO**

`posterior.py`, `profection.py`, `sect_classifier.py`, `run_sect_benchmark.py`.

Built the technique-agnostic pipeline (candidate grid → per-candidate likelihood →
posterior → sect marginal) and drove it with **annual profection** (year-lord
depends on the rising sign → time-dependent, unlike firdaria). Then the control
that reframed everything.

**Profection is null (and harmful).** Rising-sign recovery is at chance (exact
9.5% vs 8.3%; mean sign-distance 2.95 vs 3.0), and the profection posterior's sect
marginal (65%) is *worse* than a uniform posterior. Coarse lord-matching carries
no time signal — consistent with the firdaria null.

**The control that mattered — the daylight prior.** A *uniform* posterior (zero
technique signal) sets `p_day` = the **daylight fraction of the birth day**
(longer day ⇒ more likely born by day = `P(day | date, lat)`). Alone it scores
**68.3%, corr +0.40** — beating every event-based signal. The strongest sect
predictor is a free geometric prior that uses no events at all.

**But events add real independent value.** The malefic-of-sect signal is only
mildly correlated with the daylight prior (+0.19), and its **partial correlation
with sect controlling for daylight is +0.30** — genuinely independent evidence.
Combining them (informed prior × event likelihood — the theory's exact structure)
via a 2-feature logistic:

| model | accuracy |
|---|---|
| majority baseline | 54.0% |
| malefic-alone | 65.1% |
| daylight-alone | 68.3% |
| **daylight + malefic (LOO-CV)** | **69.8%**, CI [57.6%, 79.8%] |
| daylight + malefic (in-sample) | 73.0% |

**Pre-registered gate (LOO acc ≥ 65% AND CI-low > majority): GO.** Cross-validated,
so not overfit; fitted weights daylight +0.80 / malefic +0.72 (both real).

**Takeaways:**
1. A calibrated **sect classifier at ~70% (LOO) exists** — daylight prior + the
   malefic-of-sect event evidence. First result to clear the bar.
2. Most of the strength is the *free geometric prior*; the event evidence adds a
   real but modest independent boost. This is honest and defensible, not a
   dramatic rectification win.
3. **Profection (coarse timing) is null** — the remaining upside for *time* (not
   just sect) is the **sharp** angle-tied techniques (directions to angles,
   ZR-from-Fortune peaks), still untested. Those are the real rectification signal
   if it exists; the pipeline (`posterior.py`) is built and ready to host them.

---

## Phase A2 — primary directions (the sharp technique) — **null for time**

`directions.py`, `run_directions_benchmark.py`. For each candidate time, direct the
seven planets to the four angles (`DirectionsEngine`) — hits land at ages that move
strongly with birth time — and score whether directed hits whose promissor
signifies an event fall near that event's age (de-confounded).

| metric | directions | chance |
|---|---|---|
| **time** median \|Δ\| (MAP vs truth) | 406 min | ~360 min |
| mean posterior mass ±90 min of truth | 0.138 | 0.125 |
| mean posterior mass ±180 min of truth | 0.258 | 0.25 |
| sect marginal | 68.3% | (= daylight leaking through) |

**Directions does not localize time** — mass-near-truth is at chance and median
error is *worse* than chance. Best-case retest (day-precision events only, tight
0.5-yr orb): median \|Δ\| 320 min, mass ±90 min 0.132 — still chance. The sect 68%
is just the daylight fraction showing through a near-uniform posterior, redundant
with the classifier.

## Verdict on the timing-technique family (firdaria + profection + directions)

**All three are null.** Automated rectification by "sweep the birth time, match
events to timing-technique activations via a significator table" **does not carry
signal** — coarse or sharp. Expert rectification works because a human *selects*
meaningful event↔direction correspondences with judgment; the blind, all-events,
significator-table version loses exactly that.

**What actually works, and all that works:**
1. the **daylight-fraction geometric prior** (68%, no events), and
2. the **malefic-of-sect event character** (adds independent value → **70% LOO**).

Neither is a timing technique. **Minute-level time rectification is not achievable
with this automated approach; the deliverable is the ~70% sect classifier** (to be
strengthened by an external birth-hour prior — research pending). This is the
central, rigorously-established result of the investigation.

---

## Temperament / personality — **null for sect** (`probe_temperament_sect.py`)

Tested the soft channel now that full charts are available. Sect-light doctrine:
Sun-led (Solar) character → day, Moon-led (Lunar) → night; Solar/Lunar keywords a
priori.

| | value |
|---|---|
| corr(temperament, sect) | +0.03 (null) |
| corr(temperament, malefic) | −0.03 (independent, but of noise) |
| **partial corr(temperament, sect \| daylight, malefic)** | **+0.11** (n.s. at n=63) |
| LOO: daylight+malefic | 69.8% |
| LOO: daylight+malefic+**temperament** | **68.3%** (no gain — slightly worse) |

Temperament is null and adds nothing (it slightly *hurts* LOO). This also settles
the chart-contextualised version without building it: "does temperament match the
chart's sect-role assignment" decomposes into the **sect light** (Solar/Lunar —
just tested null) and the **benefic of sect** (Jovial/Venusian — = the null
benefic-events probe). Both building blocks are null.

**Why temperament fails where malefic-of-sect works:** the malefic signal rides a
*specific, clean* axis — the *character of misfortune* (violent/Mars vs
chronic/Saturn) maps directly onto the out-of-sect-malefic doctrine. General
temperament is swamped by the far larger non-sect determinants (Sun sign, Moon
sign, dominant planet, Ascendant); the sect overlay is too faint to detect against
that. Fittingly, sect shows up in the **character of harm**, not in general
personality — consistent with the tradition emphasising sect most for the
malefics' operation.

---

## Natal dignities / placements — **null for sect** (`probe_dignity_sect.py`)

Tested planetary sign-dignities two ways: (1) a **diurnal-vs-nocturnal dignity
balance** (new channel), and (2) **dignity-weighting the malefic** (enrich what
works — scale hardship by the natal condition of Mars vs Saturn).

| model | LOO-CV |
|---|---|
| daylight + malefic | 69.8% |
| daylight + malefic + dignity-balance | 68.3% (worse) |
| daylight + malefic(dignity-weighted) | 65.1% (worse) |

Both fail. The dignity-balance's in-sample partial corr looks sizable (−0.32) but
**does not survive LOO** — textbook noise-as-signal, and a reminder of why every
signal is cross-validated. Expected: sect is a horizon fact, ~orthogonal to which
signs the planets occupy. Dignity-weighting the malefic *degrades* it — natal
malefic condition is noise for the misfortune-character signal.

## Signals tested — the full map

| channel | signal | result |
|---|---|---|
| geometry | daylight fraction (prior) | **+0.40 — works (68%)** |
| event character | malefic-of-sect (misfortune flavour) | **+0.35 — works, independent (→70%)** |
| event character | benefic-of-sect (fortune flavour) | null (domain confound) |
| timing | firdaria time-lord × significators | null |
| timing | annual profection (rising-sign lords) | null |
| timing | primary directions to angles | null (sect *and* time) |
| temperament | sect-light (Solar/Lunar) | null |
| natal dignity | diurnal/nocturnal balance; dignity-weighted malefic | null |

**Bottom line.** Feature space for an *automated, corpus-scale* rectifier is
thoroughly explored. Only **daylight prior × malefic-of-sect** survives (LOO
69.8%, GO). Minute-level **time** is null across every timing technique. The lone
remaining lever with real upside is an **external birth-hour prior** (research
pending) to sharpen the daylight term. Further feature-hunting on n=63 has
negative expected value (multiple-comparisons risk — the dignity −0.32 that
vanished under LOO is the warning).
