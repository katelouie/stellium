# Computational Birth-Time Rectification — An Empirical Study

*A rigorous negative result, one stubborn positive, and why the arithmetic beat
the symbolism.*

| | |
|---|---|
| **Status** | Complete write-up (exploration on `explore/rectification`) |
| **Date** | 2026-07-11 |
| **Owner** | Kate |
| **Companions** | [RECTIFICATION_THEORY.md](./RECTIFICATION_THEORY.md) · [RECTIFICATION_PHASE1_FINDINGS.md](./RECTIFICATION_PHASE1_FINDINGS.md) (raw lab log) · code in `rectification/` |

---

## Abstract

We asked whether a birth time can be recovered, automatically and at scale, from
a person's dated life events and temperament — the task astrologers call
*rectification*. We built a provenance-verified corpus of 63 historical and 20
modern birth-certificate-accurate (AA/A) charts, implemented the classical timing
techniques (firdaria, annual profection, primary directions) plus event- and
temperament-character signals, and tested each under a pre-registered success gate
with leave-one-out cross-validation, permutation-null de-confounding, and
confound checks.

**Minute-level time is not recoverable.** Every timing technique scored at chance
for localising the birth time. The only thing recoverable is **sect** (day/night),
at ~70% (cross-validated) — and that is carried mostly by a *geometric prior* (the
daylight fraction of the birth day) plus **one** traditional doctrine that showed
genuine, confound-robust signal: the **malefic contrary to sect** (Mars-flavoured
misfortune → day, Saturn-flavoured → night). We interpret the whole pattern
through the lens of **ill-posed inverse problems**: the forward map (time → chart →
life) is many-to-one, so its inverse is non-unique; when the likelihood is
uninformative the posterior collapses onto the prior — which is exactly why plain
astronomy (the daylight prior) outperformed every interpretive signal.

---

## 1. The task, and the honest bar

Rectification inverts astrology's usual direction. Normally: birth time → chart →
read the life. Rectification runs it backward: known life → infer the birth time.
The unknown is ~1-dimensional (a time within a day; the angles move ~1°/4 min, the
Moon ~1°/2 hr, the slower bodies barely at all), so in principle it is a small,
cheap inference. We did not demand minute precision — even landing the correct
**2-hour block / rising sign** (enough for whole-sign work) would be useful. The
question was simply: *does a life carry enough signal to recover the time, at all?*

## 2. The corpus

Ground truth requires known birth times **and** documented lives, which forces the
sample toward famous, birth-certificate-recorded, Western, 19th–20th-century
people (a selection bias we return to in §8 — it is structural to the whole
enterprise, not fixable).

- **Provenance first.** Candidate charts were verified against AstroDataBank
  source notes before entry: rectified times masquerading as AA (e.g. Feynman's
  Starkman rectification), uncited-biography times sold as A (e.g. Musk), and
  aggregator-sourced "AA" ratings were rejected. The pass corrected the notables
  DB itself (`apply_research_verdicts.py`).
- **Result:** **63 verified people** (48 AA + 15 A), **888 dated events** (median
  13 each) with an event taxonomy, plus ≥4 tagged temperament traits each; sect
  balance 34 day / 29 night. A separate **20-person post-1970 cohort** (17 AA) was
  held out as an out-of-sample validation set and never used for fitting.

## 3. Methodology — the discipline that makes the nulls trustworthy

The whole value of a negative result rests on not having fooled ourselves. So:

- **Pre-registered gate:** accuracy ≥ 65% **and** the 95% CI lower bound above the
  majority-class baseline (54%). Set before testing, never moved.
- **Leave-one-out cross-validation** on every fitted model — the headline numbers
  are LOO, not in-sample.
- **Permutation-null de-confounding.** Raw technique scores are confounded (some
  configurations light up for everyone); each signal was scored as its *excess
  over* a per-person label-shuffle null. This caught, and removed, a large
  spurious "night bias" in the first firdaria result.
- **Partial-correlation confound checks** (§7) against profession and sex.
- **Out-of-sample validation** on the 20-person modern holdout.
- **Every null documented**, and multiple-comparison risk explicitly tracked —
  with n=63, the danger is finding a spurious "hit" by trying enough features. The
  discipline above is what lets us tell signal from that.

## 4. Results — the full signal map

| channel | signal | result |
|---|---|---|
| geometry | daylight fraction (prior) | **works** — corr +0.40, 68% |
| event character | **malefic-of-sect** (misfortune flavour) | **works** — +0.35, independent |
| event character | benefic-of-sect (fortune flavour) | null (domain confound) |
| timing | firdaria time-lord × significators | null (corr −0.2) |
| timing | annual profection (rising-sign lords) | null (rising-sign recovery at chance) |
| timing | primary directions to the angles | null — sect **and** time |
| temperament | sect-light (Solar/Lunar) | null |
| natal dignity | diurnal/nocturnal balance; dignity-weighted malefic | null |
| prior | external birth-hour distribution | no improvement |

### 4.1 The one that worked, and the one that surprised

- **The daylight prior** — `P(day | date, latitude)` under uniform birth time,
  i.e. "longer day ⇒ more likely born by day." It uses no events, no chart, and it
  was the *single strongest* sect predictor (68%). This is not astrology losing to
  a sundial: sect *is* the Sun's position relative to the horizon, so the daylight
  fraction is the honest base rate of the very thing we predict.
- **Malefic contrary to sect** — the traditional doctrine that the out-of-sect
  malefic is the sharper destroyer (Mars out of sect by day, Saturn by night). A
  life's misfortunes should carry the flavour of its contrary-sect malefic:
  Mars-flavoured (violent, sudden, accidents) → day; Saturn-flavoured (chronic,
  loss, confinement) → night. This **worked**: corr +0.35 (p ≈ 0.005), the
  strongest-Saturn lives (Bundy, Arendt, Ali, Obama) classify night, the
  strongest-Mars lives (Hemingway, Kahlo, JFK, van Gogh, Plath) classify day. It
  is nearly independent of the daylight prior (partial corr +0.30), so the two
  **stack**.

### 4.2 The combined sect classifier

Daylight prior × malefic-of-sect, a 2-feature logistic:

| model | accuracy |
|---|---|
| majority baseline | 54.0% |
| daylight-alone | 68.3% |
| malefic-alone | 65.1% |
| **daylight + malefic (LOO-CV)** | **69.8%**, 95% CI [57.6%, 79.8%] |
| daylight + malefic (**out-of-sample**, modern cohort) | **70.6%** |

**Pre-registered gate: GO** — and it generalises to a completely different era.

### 4.3 What did *not* work — time

- **Firdaria** (near time-independent) — null, and slightly anti-correlated.
- **Profection** — rising-sign recovery at chance (exact 9.5% vs 8.3%), and its
  posterior was *worse* than uniform (it injected noise).
- **Primary directions to the angles** — the sharp technique, the one that *should*
  localise time. Time-recovery MAE 406 min (chance ~360), posterior mass within
  ±90 min of truth 0.138 (chance 0.125). Best-case retest (day-precision events,
  tight orb): still chance. **Directions do not localise the birth time.**
- **The verdict on the timing family (firdaria + profection + directions): all
  null.** Automated "sweep the time, match events to timing-technique activations
  via a significator table" carries no rectification signal, coarse or sharp.

### 4.4 The birth-hour prior — a clean lesson

An external, cited hourly birth distribution (population vital-statistics, no chart
samples) replaced the uniform-time assumption. It **did not help** — historical or
modern. The three priors produced `P(day)` values **0.997 rank-correlated** with
each other (they differ by a near-constant +0.076 shift, sd 0.007). A better
*prior* (marginal calibration) is not a better *classifier* (discrimination): the
curve reweights everyone almost identically, so it slides the decision threshold
without changing the ranking. For *hour* prediction it was the same — within a
sect window it added −6 min. All hour signal comes from sect narrowing the window
(~5.8 h → ~3.5 h with perfect sect); with our real 70%-accurate sect it collapses
back to ~noon (327 min), because a wrong sect call is a ~12-hour miss.

## 5. Why — rectification is an ill-posed inverse problem

The results are not a story of insufficient effort. They are the signature of a
**structurally ill-posed inverse**.

The forward map `birth time → chart → life` is **many-to-one**: orbs give slack, a
single event can be signified many ways (7th house *or* Venus *or* the Lot *or*
the ruler), and a dozen techniques each offer a "hook." So *many* birth times
produce a chart the rules cannot rule out for a given life. Inverting it therefore
yields not *the* time but a **set** — the preimage of a lossy map. (Knowing
`x² = 4` gives `{+2, −2}`, not because you are bad at algebra but because squaring
discarded the sign.)

In Hadamard's terms the problem is **ill-posed**: a true time *exists*, but the
solution is **not unique** (many times fit) and likely **unstable** (nudging an
event date can flip the answer). The standard remedy for an ill-posed inverse is
**regularisation with a prior**. And this is the punchline of the whole study:

> **When the likelihood is uninformative, the posterior collapses onto the prior.**
> That is *why the daylight prior won.* We observed it directly — a uniform-scorer
> control (zero event signal) sets `p_day` = the daylight fraction, and it *beat*
> every event-based signal. The prior dominating is not an embarrassment; it is the
> **defining behaviour of an ill-posed inverse**, and we measured its fingerprint.

**Sect survives because it is the gentlest possible ask** — recover *one bit*, the
coarsest coarsening of the 1-D unknown, partly anchored to geometry (the prior
itself). One bit you can sometimes pull from an ill-posed inverse. Nine hundred
minutes you cannot.

## 6. Dialogue with the tradition (Tebbs, Dobyns, Rodden)

This frame does not contradict expert practice — it *explains* it. Carol Tebbs'
*Complete Book of Chart Rectification* white-knuckles one rule (from Zip Dobyns):
an event must show in Secondary Progressions, Solar Arc, **and** Transits — *"if
systems are selectively mixed and matched, it is possible to make a case for most
any birth time."* That convergence requirement is, formally, **constraint
intersection**: each independent technique carves out its own consistent-set, and
the true time must lie in the intersection. It is the mathematically correct
response to non-uniqueness — the only lever there is.

But intersection only shrinks the set if the constraints are **informative** and
**independent**, and both fail: the techniques ride the same angles (not
independent), and each one's consistent-set is ≈ the whole day (not informative).
Tebbs is honest about the consequence — in her own Elizabeth Taylor example, the
rectification *software's* highest-confidence time (81%) was **~7 hours from
truth**, while the true time scored 50% and second. Her defence — *"the trained
astrologer's eye and judgment are still superior"* — is both the plausible signal
(connoisseurship the algorithm can't encode) and the unfalsifiable escape hatch
(the examples all recover a time already known going in). Rodden's own verdict
sits underneath it all: *"all rectified data are rated C … treat all rectified
data with caution."* The tradition's honest practitioners already said what we
measured.

Our null is therefore not a refutation of rectifiers; it is a **measurement of the
gap** between blind significator-matching and judgment-selected convergence — and a
demonstration that the gap is where all the work is being done.

### Does convergence stack? A direct test

Tebbs's rule predicts that combining independent techniques pushes the true time
toward the top of the ranking. We tested it by measuring the **percentile rank of
the true time** in each posterior (null = 50th; Tebbs's "2nd of 4" ≈ 75th):

| posterior | percentile of the true time |
|---|---|
| directions alone | 55th |
| profection alone | 59th |
| **profection + directions** (blind z-sum) | **51st** |
| + firdaria | 49th |
| + firdaria + the LOO sect prior | 49th |

A single technique places the truth at a faint ~57th percentile — a *whisper*
above chance, not "just under winning." But **blind combination cancels it**:
profection + directions lands at the 51st percentile, *worse than either alone*,
and adding firdaria or the sect prior makes it worse still. The techniques share
the angles (correlated structure) but their faint pulls point at *different* wrong
places (decorrelated error), so z-summing adds noise faster than signal and the
truth's rank regresses to the mean. (Weighting could recover the best single
technique's 59th percentile, but cannot exceed the information present, which tops
out at a whisper; the sect prior cannot narrow a set with no signal left to narrow.)

**This closes the loop with Tebbs.** If blind convergence *cancels*, then expert
convergence cannot be *combining* — it must be **selecting** the hooks where
techniques happen to agree. We have thus empirically separated the two:
**combination → chance; only human *selection* lifts the truth.** That selection is
simultaneously the trained eye's real contribution *and* its irreducible
unfalsifiability — selecting-on-agreement can surface a true time or manufacture a
false one, and the method itself cannot tell which. The whole lift lives in the one
step that is neither automatable nor falsifiable.

## 7. Confound & robustness checks

The one positive event signal (malefic-of-sect) is the most bias-vulnerable, so it
got the most scrutiny:

- **Category (profession):** malefic-sect corr +0.346 → partial +0.355. Category
  explains only 5% of sect variance.
- **Gender:** partial +0.349; gender explains **0%** of sect variance (women/men
  day-born at 52%/55%).
- Both together: +0.361. **Completely stable** — it strengthens slightly. Because
  sect is *birth time of day*, mechanistically independent of who you are, neither
  profession nor sex *can* confound it. The "criminals are violent and happened to
  be day-born" artifact is ruled out.
- **Out-of-sample:** daylight prior alone → 70.6% on 20 charts never used for
  fitting, matching its ~68% historical performance.

## 8. Limitations

- **Selection bias is structural and unfixable.** Validating rectification requires
  known-time + documented-events = famous + AA + Western + recent. There is no
  representative rectification corpus, because ordinary lives are not documented.
  This is a ceiling on the *entire enterprise*, inherited by anyone who attempts it.
  Our nulls are, if anything, *conservative* — famous dramatic lives are the
  best-case input; if timing signal isn't here, it isn't anywhere.
- **The malefic signal carries untestable caveats** — biographical-emphasis bias
  (biographers front-page violent deaths, under-report chronic decline) and
  unknown generalisation past famous lives. The *testable* confounds are clean; the
  untestable ones remain, and the classifier is validated **on this population, not
  claimed for humanity**.
- **n = 63** is small; the keyword lists carry researcher degrees-of-freedom (set a
  priori, but not cross-validated as features). LOO protects the *combination*, not
  the feature *design*.

## 9. Conclusion

We set out to build a rectifier and instead built an honest account of why one does
not easily exist, plus one real finding along the way.

- **Sect is recoverable** at ~70% (cross-validated, cross-era) — but mostly from
  the *geometry* (the daylight prior), with a genuine, confound-robust boost from
  **one** traditional doctrine (the malefic contrary to sect). That doctrine
  leaving a measurable fingerprint on real biography is a small, stubborn point in
  the tradition's favour that neither a believer nor a skeptic gets to wave away.
- **Time is not recoverable** by automated timing techniques — because the inverse
  is ill-posed, its solution non-unique, and the interpretive maps too weak and too
  redundant for convergence to rescue.
- **The arithmetic beating the symbolism is not astrology losing.** Sect is
  astronomy; the prior winning is the correct behaviour of a well-regularised
  ill-posed problem; and the tradition's own honest voices (Rodden, Dobyns, Tebbs)
  said as much before we ran a single test. What we added was the *measurement*.

The tooling (loader, harness, benchmark, permutation-null and confound machinery)
and two provenance-verified corpora are reusable. The map of where sect signal
lives — and where time signal does not — is the deliverable. Negative results
honestly won are worth as much as the positive one; they tell you where not to
spend the next effort.

*— and, for the record: we really did want the old techniques to work.*
