# Rectification — Methodology & Theory Overview

| | |
|---|---|
| **Status** | Exploration / draft |
| **Created** | 2026-07-10 |
| **Owner** | Kate |
| **Type** | Theory & methodology (companion to `RECTIFICATION_SPEC.md`) |

This document explains **how the rectifier works conceptually** — the statistical
model and its astrological grounding — independent of implementation. The build
plan is in [`RECTIFICATION_SPEC.md`](./RECTIFICATION_SPEC.md).

---

## 1. The problem

**Rectification** = inferring an unknown or uncertain birth *time* from what is
known about a life: dated events (marriage, career turns, relocations,
bereavements, accidents, public recognition) and, more softly, temperament.
Traditionally a laborious manual craft; we want a **computational, honest, and
explainable** version.

## 2. The core insight

Birth *time* maps almost entirely onto the **angles** (Ascendant / Midheaven and
the house cusps) and, weakly, onto the Moon (~0.5°/hr). Planetary longitudes
barely move across a birth-day. Two consequences drive the entire design:

1. **The unknown is effectively 1-dimensional** — a time within a day (latitude/
   longitude are normally known). This is tiny.
2. **The forward model is known, exact, and cheap.** Given a candidate time `t`,
   Stellium computes *exactly* what every timing technique says — there is
   nothing to *learn* about the map `t → activations`; it is astrology's math.

A third, practical fact: over a birth-day the **slow** bodies are ~fixed, so a
candidate sweep does **not** need a full ephemeris recompute per candidate —
compute them once and **re-cast only the angles** (cheap trig from sidereal time
+ latitude). The **Moon is the exception** (~0.5°/hr ≈ 13°/day) and must be
recomputed or interpolated per candidate; it feeds the Moon significators and the
sect-dependent **Lot of Fortune/Spirit**. (Build detail: build spec §4.1.)

## 3. The model

> A **hierarchical Bayesian model with a simulation-based forward model**: the
> astrology engine is the exact simulator, birth time is inferred by **grid
> evaluation over the 1-D window**, and the likelihood is **empirically
> calibrated** on a corpus of known-time charts.

### 3.1 Prior — `P(t)`

- **Naive:** uniform over the candidate window (the whole day if fully unknown,
  or ±N hours around a stated time).
- **Informed (optional):** a soft bump around any recorded/approximate time, and
  **birth-hour base rates** (births genuinely cluster by hour — early-morning
  peaks, weekday-morning C-section humps).

### 3.2 Likelihood — `L(events | t)`

Each `(event_i × technique_j)` pair contributes `L_ij(t)` = how strongly
technique `j` lights event `i`'s significators *around its date*, for a chart
cast at `t`. Conditional on `t` and treating contributions as (approximately)
independent:

```
log P(t | events) = log P(t) + Σ_i Σ_j w_j · log L_ij(t) + const
```

The `w_j` are per-technique weights (§7). The shape of each `L_ij` matters: a
technique that activates at a precise instant (a directed MC→Venus arc exact at
one minute) contributes a **narrow** bump; a coarse technique (profection, which
depends only on the rising *sign*) contributes a **broad plateau**. This
**multi-resolution** behaviour is a feature — see §4.

### 3.3 Posterior — grid evaluation

Because `t` is 1-D and the forward model is cheap, evaluate the un-normalised
log-posterior on a grid of candidate times and normalise. **No MCMC, no
variational inference, no sampling** — grid evaluation *is* the correct and exact
method at this dimensionality. The rigorous label for "known simulator, invert to
a posterior, likelihood not written analytically" is **simulation-based
(likelihood-free) inference**; in 1-D it collapses to exactly this grid.

### 3.4 Why not deep learning

The core is the wrong shape for DL, for concrete reasons:
- It would try to **learn a forward model we already know exactly** — discarding
  perfect information and demanding data we don't have.
- **Per-person data is tiny** (a handful of events); DL needs volume.
- The inference is **1-D**; DL's high-dimensional strength is irrelevant.
- **Interpretability is mandatory** (the practitioner must see *why*).

Learning has exactly one legitimate home here: **calibrating the likelihood**
(§7), a small tabular problem best handled by classical methods.

## 4. Coarse-to-fine, and sect as a marginal

Techniques constrain at different **resolutions**, and the model exploits this:

- **Coarse** (broad likelihoods): firdaria **sect** (flips at the horizon →
  constrains AM/PM), profection (rising *sign* only → ~2-hour plateau).
- **Sharp** (narrow likelihoods): directions/transits to the exact angle,
  progressed-Moon aspects — minute-level.

Multiplied together, coarse likelihoods carve the plausible band and sharp ones
resolve within it — exactly how a human rectifier works (AM/PM and rising sign
first, then fine-tune). Critically, **sect requires no separate model**: it is
the **marginal** of the same posterior,

```
P(day) = Σ over the day-cells of the grid,   P(night) = Σ over the night-cells,
```

so one model yields both the robust binary answer *and* the fine posterior. Note
the Sun crosses the horizon **twice** across a day, so the night-cells are **two
disjoint intervals** (pre-dawn + post-dusk) and `P(night)` sums both — sect is a
three-region step function of `t`, not a single midpoint split (build spec §4.2).
Sect is still the safest thing to report because it is a *coarsening* of `t`
(hard to overfit), which is why it is the natural **first deliverable** (§ spec).

## 5. Evidence: hard-data, soft-data, and the information budget

Two evidence streams:

- **Hard data** — *dated events*. Each event → significators (§6) → activation
  under the timing techniques → a likelihood over `t`. These are the strong,
  time-sharp constraints.
- **Soft data** — *temperament/personality*. Maps to sect-role assignments
  (sect light; benefic/malefic **of** the sect) and dignity emphasis. Broad,
  subjective; contributes mainly to the **sect** marginal, and is treated as the
  least-rigorous channel (optionally human-in-the-loop or LLM-elicited, always
  flagged and calibrated).

**The information budget (a genuinely useful lens).** Borrowing the actuarial
*frequency × severity* decomposition — but applied to the *evidence*, not the
parameter:

- **Frequency** = how many usable events you have.
- **Severity** = each event's **discriminating power** — how sharply its
  likelihood constrains `t` (a precisely-dated angular direction is high-severity;
  "she's rather Venusian" is low-severity).

Their aggregate ≈ the total constraining information ≈ **how tight a posterior you
can even hope for**. This gives the tool a principled way to say *"your facts can
support roughly a ±90-minute answer"* and to **elicit the highest-severity
evidence next**.

## 6. The event → significator model (the conceptual crux)

The hardest, fuzziest part is turning *"married 1998"* into *"the 7th house /
Venus / the Lot of Marriage should be activated around 1998."* We define a small
**event taxonomy**, each type mapping to significators (houses, planets, lots)
and the techniques best suited to catch it:

| Event type | Typical significators |
|---|---|
| Relationship / marriage | 7th house, Venus, Lot of Marriage, ruler of 7th |
| Career / public recognition | 10th house, MC, Sun, Lot of Spirit, ruler of 10th |
| Relocation / emigration | 4th/9th houses, Moon, ruler of 4th |
| Bereavement (parent) | 4th/10th (parents), 8th, Saturn |
| Childbirth | 5th house, Jupiter, Lot of Children |
| Health crisis / accident | 1st/6th/8th, the malefics, Lot of Fortune |
| Windfall / loss | 2nd/8th, Lot of Fortune, Jupiter/Saturn |
| Legal / imprisonment | 12th, Saturn, ruler of 12th |

The mapping is uncertain, so significators are best treated as a (small) set with
weights and, ideally, **marginalised over** rather than fixed. This taxonomy is
also what the **data-collection prompt** must target.

## 7. Correlation, calibration, and honesty

The independence assumption in §3.2 is *false*: ZR, profections, and directions
all ride the **same angles**, so naively multiplying their likelihoods
**double-counts** and yields an overconfident, too-narrow posterior. This cannot
be fixed from first principles — the correlation structure is messy. So we fix it
**empirically**:

- Introduce per-technique weights `w_j` and an overall **temperature**.
- **Calibrate on a known-time corpus** (§8) so the posterior is *properly
  calibrated* — its 68% credible interval actually contains the true time ~68% of
  the time on held-out charts (temperature scaling / conformal calibration).

This calibration is what turns a *score* into an *honest probability*. Formally
this is the **hierarchical** layer: **global** parameters (per-technique
reliability/orb, temperature) shared across everyone and fit once on the corpus;
a **per-person** parameter (`t`) inferred from that person's events.

For the combiner itself, in ascending complexity (use the simplest that passes
validation): **(1)** expert-prior weights + a light global calibration;
**(2)** regularised logistic regression over per-technique activation features;
**(3)** gradient-boosted trees only if 1–2 underperform. Deep nets: no.

## 8. Validation — the notables benchmark

Stellium ships hundreds of **AA-rated** (birth-certificate-accurate) charts, so
we **know the true time**. That makes an honest benchmark almost free:

- **Blind test:** blank the time, feed documented events (+traits), run the
  rectifier, compare to truth.
- **Sect first:** a clean **binary classification accuracy** — the most
  interpretable early signal (does the approach beat chance, and by how much?).
- **Then time:** median absolute error, and — crucially — **calibration**
  (are the credible intervals honest?).

The corpus is *both* the training set for the calibration layer *and* the test
set (held-out). This self-validation is the spine that separates this from vibes.

## 9. Optional extensions

- **Prenatal epoch / Trutine of Hermes** — the classical rule relating the birth
  Moon/Ascendant to the pre-natal lunation. Stellium's bidirectional lunation
  finder makes it computable, and it can enter as one more likelihood
  contributor.
- **LLM as a soft-evidence elicitor** — for the personality channel only:
  *"these traits — more consistent with the day role-assignment or the night
  one?"* → a soft `P(day)`. Appropriate use of an LLM (structured judgment over
  fuzzy text); never the inference engine; calibrated like everything else.

## 10. Framing & ethics

- A **computed indicator, not an oracle.** The output is a distribution with an
  explicit uncertainty, always **human-in-the-loop** for the final call.
- **Explainable by construction** — the posterior is a sum of per-event, per-
  technique contributions, so the tool can always show *why* a window scores well
  ("your 1998 marriage pulls toward 14:20–14:50 via the ZR Spirit peak and a
  directed MC→Venus").
- **Honest about uncertainty** — report the full distribution (often multi-modal)
  and the information budget, never a false-precision timestamp.

## 11. One-sentence summary

A hierarchical Bayesian model with the astrology engine as an exact
simulation-based forward model, birth time inferred by grid evaluation over the
1-D window, **sect read off as a marginal**, the likelihood **empirically
calibrated on the known-time notables corpus** so its credible intervals are
honest — classical (not deep) learning reserved for the calibration layer, an
optional LLM only for the soft personality channel.
