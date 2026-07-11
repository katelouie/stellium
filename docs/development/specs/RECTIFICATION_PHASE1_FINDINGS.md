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

**Recommended next step:** add the **symmetric benefic-of-sect mirror** — Jupiter
is benefic *of sect* by day, Venus by night, so Jupiter-flavoured good fortune →
day, Venus-flavoured → night. Combining the malefic (misfortune) and benefic
(fortune) channels uses more of each life, should shrink the 14 keyword-silent
undecideds, and — if the effect is real — sharpen the signal. Optionally weight by
the malefics'/benefics' time-independent **sign dignity**.
