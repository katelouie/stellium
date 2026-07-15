# Spec: Grammatical Inflection in the i18n layer

| | |
|---|---|
| **Status** | **Proposed.** Design under discussion; a **buy-vs-build** decision (§4) gates the rest. Not built. Blocks nothing near-term; it is the gate on shipping **Russian / Polish / Arabic** and any language with non-trivial plurals or case. |
| **Created** | 2026-07-15 |
| **Owner** | Kate |
| **Relates to** | Extends the i18n layer specified in [STRUCTURE_FIRST_SECTIONS.md](./STRUCTURE_FIRST_SECTIONS.md) §4. **Orthogonal** to [UNIFIED_RENDERER_CONTRACT.md](./UNIFIED_RENDERER_CONTRACT.md): inflection lives *below* the section→renderer contract — everything routes through `render()`, which is where form selection slots in. A `term()` stays a `term()`; it only gains the *ability* to inflect when a locale provides forms. |

---

## 1. Summary

The i18n layer was validated against English and Chinese — neither of which
**inflects**. `term("sign.Aries")` is one string; `msg("{planet} in {sign}")` fills a
slot by juxtaposition. That works because `火星在牡羊座` needs no agreement.

It breaks the moment a language conjugates, declines, genders, or pluralises with more
than two forms:

- **Russian** `Марс в Овне` — the *sign name itself* inflects (nominative `Овен` →
  prepositional `Овне`). One catalog string cannot serve both a table cell and a sentence.
- **Russian / Polish / Arabic plurals** — `1 год / 2 года / 5 лет`. Our `time_unit` group
  ships **two** forms (`year`/`years`); three-plus-form languages get **wrong output**,
  silently.
- **German** `im Widder` — `in dem` contracts under the dative; `in Widder` is simply
  wrong.

This spec makes the i18n layer handle grammatical form robustly, **without** disturbing
uninflected locales (English, Chinese stay exactly as they are) and **without** disturbing
the renderer contract. It first decides whether to **build** that onto our layer or **buy**
it by adopting Fluent (§4), then specifies the build path (§5) and states honestly what the
buy path would cost instead (§6).

---

## 2. Problem & Motivation — grounded in *our* content

The three inflection axes hit us very unevenly, because Stellium's strings are
overwhelmingly **labels, terms, and table cells** (noun phrases and juxtaposition), not
composed prose. Sizing this correctly is what keeps the design from over-buying.

### 2.1 Plurals — a concrete correctness bug, mandatory to fix

`time_unit` ships singular/plural **pairs** (`year`/`years`, `month`/`months`), consumed by
Zodiacal Releasing periods and profections ("3 years"). A two-form pair is a **category
error** in any language with more than two plural forms — Russian (3), Polish (3/4), Arabic
(6). This is not phraseable-around; it is a data-model defect. And the selection rule is the
one thing we must **not** hand-roll: CLDR plural rules are intricate and per-language.

### 2.2 Case — a handful of prepositional templates, bounded

Most composition is juxtaposition: the position cell is `{glyph} {sign} {deg}` — no
preposition, so no inflection. Case bites only where a template *governs* a slot:
`{ruler} (ruler of {sign})` wants the genitive in Russian (`управитель {sign:gen}`),
`in {sign}` wants the dative in German. Real, but **bounded** to a few templates, and
partly avoidable by phrasing.

### 2.3 Gender — nearly absent for us

Spanish/German gender agreement lives in **fixed phrases** ("Dignidades Esenciales") that a
translator writes already-agreed — no runtime agreement. We have almost no
`{article} {noun} is {adjective}` composition where an adjective must agree with a slot at
render time. **Spanish likely needs zero new machinery**, which is exactly why it is the
right first inflected language (§7): it proves the pipeline without forcing the hard case.

### 2.4 The one abstraction underneath all three

Case, plural, and gender are the same shape: **a term has multiple forms, and the correct
one is chosen by grammatical context** — the requesting slot's case, the count, or the
gender of the noun being agreed with. Our existing `term(key, short=True)` is a baby version
of exactly this (a "register" variant, `key.short`). The generalization is: a term is a
**form-set**, and the requester names the feature it needs.

---

## 3. Goals / Non-Goals

### Goals

- **Correct plurals** in any CLDR-covered language, via real plural rules (not a hand-rolled
  formula).
- A term can carry **named grammatical forms** (case, gender, number, register), and a
  message can **request** the form it needs — driven by the *target locale's* data.
- **Zero disturbance** to uninflected locales: English and Chinese stay plain strings; no
  annotations; byte-identical output.
- **Zero disturbance** to the renderer contract and to sections: a `term()`/`msg()` call is
  unchanged at the call site; the complexity lives in locale data and in `render()`.
- Preserve everything the current layer gives us — the **pseudolocale completeness oracle**,
  the catalog-from-registries, the format-last contract, the coverage tooling — or, if we
  buy (§4), consciously re-home them.

### Non-Goals

- **Full free-form sentence generation / agreement graphs.** We localize a bounded domain
  vocabulary, not arbitrary prose. Gender *agreement* (an adjective inflecting to match a
  slot at render time) is specified as an optional mechanism (§5.4) and **deferred** until a
  consumer needs it.
- **Conjugation of verbs.** Our strings have essentially no finite verbs to conjugate.
- Retrofitting inflection onto content that reads fine uninflected.

---

## 4. Buy vs Build — the decision that gates everything

There is a package that does almost exactly this design: **Fluent**
(Mozilla `project-fluent`, Python binding `fluent.runtime`). It is not a coincidence — Fluent
was built for *asymmetric localization*, "the translation is grammatically more complex than
the source," which is precisely our problem. This section gives it a fair hearing.

### 4.1 The landscape

| Option | Plurals | Reusable inflected terms | Case | Gender | Cost / shape |
|---|---|---|---|---|---|
| **gettext / babel** | ✅ CLDR | ❌ | ❌ | ❌ | Solves only the mandatory piece. babel is CLDR data + formatting; no term inflection, no case/gender. |
| **ICU MessageFormat** (PyICU) | ✅ | ❌ (inline per message) | ✅ via `select` | ✅ via `select` | Does it, but every message must **inline every form** — a shared `sign.Aries` used in 40 messages duplicates its cases 40×. Built for UI strings, not a term catalog. Heavy C dependency. |
| **Fluent** (`fluent.runtime`) | ✅ CLDR selectors | ✅ terms with variants/attributes | ✅ parameterized term refs `{ -sign(case: "gen") }` | ✅ term gender + select | Purpose-built for exactly this. New `.ftl` format; replaces our resolver. |

Fluent maps almost line-for-line onto the design I would otherwise build: reusable **terms**
with **attributes/variants**, **parameterized term references** (a message requests a term's
genitive), **CLDR plural selectors**, and asymmetric files (English trivial, Russian rich).

### 4.2 Why adopting Fluent is not free

Fluent replaces our resolver, and our resolver carries things Fluent does not provide:

- The **pseudolocale completeness oracle** — the mechanical "did every section stop
  stringifying English?" check the *entire* structure-first refactor leans on. Bespoke; we
  would rebuild it against Fluent's runtime.
- The **catalog derived from the registries** (add a body → get a key), the format-last
  contract, and the coverage tooling (`stellium i18n coverage/locales`).
- The **donated native-speaker content** — three Chinese locales in JSON — would migrate to
  `.ftl`.

And this lands **mid-refactor** (step 2 of 4 on the renderer contract), for a **narrow**
near-term need (plurals mandatory; case a handful of templates; gender barely present).

### 4.3 Recommendation

**Build now, keep Fluent on the table as a foundation question — do not swap engines
mid-refactor.**

- **Now:** adopt **babel** for CLDR plural rules (the one genuinely hard, mandatory piece),
  and add the term-form-set + slot-annotation extension onto the existing layer (§5). This is
  Fluent's *model*, borrowed, without Fluent's *migration*. It keeps the oracle, the
  contract, the content, and the tooling. Low-risk; unblocks Russian; does not touch the
  renderer work.
- **Later, deliberately:** revisit Fluent as a long-term foundation when (a) the renderer
  contract is done and (b) a second inflected language has exercised the build path. If the
  bespoke surface grows uncomfortable, migrate then, with eyes open. A **hybrid** is also
  viable — Fluent as the resolver with our JSON compiled into it and our oracle/tooling kept
  on top — and should be weighed at that point.

The rest of this spec assumes the build path. If the buy decision is ever taken, §6 is the
honest scope of that migration.

---

## 5. Design (build path)

Everything here is **opt-in per term and per locale** and **target-locale-driven**. Sections
and English/Chinese locales are untouched.

### 5.1 Terms become form-sets — generalizing `.short`

A catalog term's value in a locale is *either*:

- a **plain string** — `"sign.Aries": "Aries"` (en), `"牡羊座"` (zh). Unchanged. Or
- a **form-set** — a map of feature → form plus optional attributes:

  ```jsonc
  // ru/strings.json
  "sign.Aries": {
    "_": "Овен",           // base / nominative (what a bare term() returns)
    "gen": "Овна",
    "dat": "Овну",
    "prep": "Овне",
    "gender": "masc"       // an attribute, not a form — for agreement (§5.4)
  }
  ```

`render(term("sign.Aries"), "ru")` returns the base `_`; `render(term("sign.Aries",
case="prep"), "ru")` returns `Овне`; a requested form absent from the set **falls back to the
base**, never to the key. This is the exact widening of today's `term(key, short=True)` /
`key.short` mechanism — `short` becomes one member of an open set of named forms.

### 5.2 Target-locale templates annotate their slots

The **translated** template carries the grammar, because that is where the grammar is:

```jsonc
// en (unchanged — English has no case)
"{ruler} (ruler of {sign})": "{ruler} (ruler of {sign})",
// ru
"{ruler} (ruler of {sign})": "{ruler} (управитель {sign:gen})"
```

`render(Message)` parses the `:gen` annotation on the slot and requests that form when
rendering the slot's term. The English template has **no** annotations and behaves exactly
as today. Annotation syntax (`{sign:gen}` vs `{sign, case: gen}`) is an open question (§9).

### 5.3 Plurals via a CLDR primitive (babel)

A countable term carries per-category forms; a `plural` slot selects by count using babel's
CLDR rules:

```jsonc
// ru
"time_unit.year": { "one": "год", "few": "года", "many": "лет", "other": "года" }
```
```python
render(msg("{n} {unit}", n=5, unit=plural("time_unit.year", n=5)), "ru")  # → "5 лет"
```

`plural(key, n)` resolves the CLDR category for `n` in the active locale
(`babel.plural.PluralRule` off the locale's CLDR data) and picks that form; English's
one/other collapses to the existing singular/plural pair, byte-identical. **We never write a
plural formula by hand.** The `time_unit` group's current `year`/`years` pairs migrate to
`{one,other}` form-sets — English output unchanged.

### 5.4 Gender agreement — mechanism specified, use deferred

For the rare `{adjective}` that must agree with a slot noun: the noun term carries a
`gender` attribute (§5.1), the agreeing term carries per-gender forms, and the template
declares the agreement by referencing the controlling slot:

```jsonc
"motion.Retrograde": { "masc": "retrógrado", "fem": "retrógrada" }
// template: "{planet} está {motion:gender=planet}"
```

`render()` reads `planet`'s `gender` attribute and selects `motion`'s matching form. This is
specified so the data model is future-proof, but **not built** until a consumer needs it —
our content presently has none (§2.3).

### 5.5 What does *not* change

- **Section code** — a `term()`/`msg()` call site is identical. Inflection is invisible to it.
- **The renderer contract** — sections emit tokens, the resolve pass calls `render()`, form
  selection happens inside `render()`. Steps 3–4 of the contract are unaffected.
- **The pseudolocale oracle** — still brackets catalog-routed strings; a form-set term is
  still catalog-routed, so it still brackets. The oracle keeps working.
- **English / Chinese** — plain strings, no annotations, byte-identical output. The
  form-selection paths are simply never entered.

---

## 6. If we buy instead: the honest scope of a Fluent migration

Recorded so the decision in §4.3 can be revisited with the real cost, not a vibe:

1. **Content re-home** — the JSON locales (en template + three Chinese) become `.ftl`; the
   donated native content is re-expressed as Fluent messages/terms.
2. **Resolver swap** — `term()`/`msg()`/`render()` internals delegate to `fluent.runtime`;
   the catalog-from-registries feeds Fluent term definitions.
3. **Oracle rebuild** — the pseudolocale completeness check is re-implemented against
   Fluent's resolution (generate a pseudo bundle; assert no unbracketed Latin).
4. **Tooling rebuild** — `stellium i18n coverage/locales` reads Fluent bundles.
5. **Format patterns** — dates/coords/degrees move to Fluent + babel formatting functions.

Net: Fluent removes bespoke resolution logic and gives translators a friendlier format, at
the cost of migrating content and re-homing the oracle/tooling. Worth it if we expect many
inflected languages and a long maintenance horizon; over-bought if the language set stays
small.

---

## 7. Rollout — language order

Ordered so each language is a deliberate probe of the machinery, per the Deep Research
demand signal (astro.com ships 12 languages; Spanish/Portuguese/German lead the practitioner
base):

1. **Spanish** — first. Big practitioner base, settled Latin-derived vocabulary (lookup, not
   coinage), and — for *our* content — likely **zero new machinery** (gender lives in fixed
   phrases). Proves the pipeline end-to-end.
2. **German** — Hamburg-School bodies (Cupido/Hades/Zeus/…) and Ebertin midpoints are
   *native* German, not the low-confidence transliterations Chinese forced. Minor dative
   contraction is the first real case probe.
3. **Portuguese (pt-BR)** and **French** — cheap once the pattern holds; the fallback chain
   handles pt-PT as parent.
4. **Russian / Polish** — **gated on §5.3 (plurals) and §5.1–5.2 (case)**. Do not attempt
   until the plural primitive and form-sets exist; a two-form or nominative-only model
   produces silently wrong output.
5. **Japanese** — later; reuses the CJK format work, and katakana transliterates
   productively, so the unattested-body problem largely evaporates.

---

## 8. Testing

- **Uninflected locales unchanged** — the existing byte-identical guards (English report
  hash, Chinese render checks) must not move. Form-selection paths are never entered.
- **Plural correctness** — a table-driven test: for a locale with 3+ forms, assert
  `plural("time_unit.year", n)` picks the CLDR-correct category for representative `n`
  (1, 2, 5, 11, 21 in Russian). Sourced from babel's CLDR data, not our assertion of the
  rule.
- **Case selection** — a form-set term returns the requested form and falls back to the base
  when a form is absent (never to the key).
- **The pseudolocale oracle still holds** — a form-set term rendered in `qps` is still
  bracketed; a migrated section still shows zero leaks.
- **Coverage tooling** counts a form-set term as covered when its base form is present.

---

## 9. Open questions

- **Slot-annotation syntax.** `{sign:gen}` (compact) vs `{sign, case: gen}` (ICU-ish,
  extensible). The compact form is friendlier; the verbose form generalizes to multiple
  features per slot. Leaning compact with a documented grammar.
- **Where plural rules come from at runtime.** babel's `PluralRule` per locale — confirm the
  dependency weight and that it covers our target set (it covers all CLDR locales).
- **Form-set schema key for the base form.** `"_"`, `"base"`, or the nominative's own name?
  Leaning `"_"` — unambiguous, sorts first, never collides with a real feature name.
- **Whether short-form unifies into the form-set now.** `key.short` could become
  `{"_": …, "short": …}`. Tidy, but touches existing `house_system.*.short` and
  `motion.Retrograde.short` — do it as part of this, or leave `.short` as a flat special case
  and only widen for new features? Leaning: widen the *mechanism* but leave existing `.short`
  data in place (both resolve through the same selector).
- **Revisit Fluent when?** Concretely: after the renderer contract lands and Spanish +
  German ship on the build path. If bespoke maintenance bites, migrate then (or go hybrid).

---

## 10. Acceptance criteria

1. `plural(key, n)` selects the CLDR-correct category for the active locale, via babel; the
   English one/other case is byte-identical to today's singular/plural pair.
2. A term may be a form-set; `render(term(key, case=…))` returns the requested form and falls
   back to the base form, never the key.
3. A target-locale template may annotate a slot with a feature; `render()` applies it; the
   English template is annotation-free and byte-identical.
4. English and Chinese output does not move; the pseudolocale oracle and coverage tooling
   still work.
5. The renderer contract and section code are untouched by this change.
6. Gender-agreement *mechanism* is specified and the data model supports it, even if unused.
