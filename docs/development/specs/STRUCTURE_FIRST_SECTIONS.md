# Spec: Structure-First Section Contract

| | |
|---|---|
| **Status** | **In progress.** Phase 0 (inventory) and Phase 1 (foundations) landed — §2.4, §7. Phase 2 next. |
| **Created** | 2026-07-14 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Tracking** | Obsidian: "Structure-first section contract" · "Integrate Simplified Chinese translation strings into main library and web" |
| **Supersedes** | The i18n work is folded in here — it is the same change (§2.2) |

---

## 1. Summary

`ReportSection.generate_data()` returns **display strings**. A planet's position leaves
the section as `"♋︎ Cancer 3°12'"` — the sign, the degree and the glyph fused into one
flat string — and every consumer downstream has to either accept it as-is or
reverse-engineer it.

That single decision blocks three separate roadmap items, which are not three problems:

- **The Typst PDF design system** can only style what it can see. It already reads a
  structured payload — but for exactly one section, and re-parses strings for the rest.
- **Interactive HTML reports** want filterable aspects and sortable tables. **You cannot
  sort a string.**
- **Internationalization** cannot translate a string that was composed in English.

This spec makes **structured data the section contract**: sections emit semantic values
with canonical keys, and *renderers* compose the display strings — last, and in a locale.

The i18n layer (a catalog derived from the registries, message templates, locale format
patterns) is specified here too, because it is what the renderers compose *with*. And it
pays for itself twice: a **pseudolocale** turns "did every section stop stringifying?" —
a question you cannot answer by inspection — into a mechanical check (§9).

---

## 2. Problem & Motivation

### 2.1 The contract today

A section flattens semantics into strings, then hands them on:

```python
# sections/core.py — PlanetPositionSection (the one section that has been migrated)
planets.append({
    "name":  pos.name,              # canonical  ← semantic
    "label": display_name,          # display
    "glyph": glyph,                 # language-neutral
    "sign":  pos.sign,              # canonical  ← semantic
    "degree": deg_str,
    "retro": bool(pos.is_retrograde),   # a BOOL, not "Retrograde"
})
rows.append([f"{glyph} {display_name}", f"{sign_glyph} {pos.sign} {deg_str}", ...])
#            ^^^^ the derived strings, which are what most renderers actually eat
```

This is the pattern we want, and it already exists — `planets` is the source of truth and
`rows` is derived from it. `typst_render.py:244` reads `planets`; the Rich, HTML,
markdown and plain renderers read `rows`. `DispositorSection` has a structured `graph`
payload on the same principle.

**Thirteen of fourteen section files have not been migrated.** They emit `rows` only.

### 2.2 Three consumers, one defect

| Consumer | Status | What it needs | What it gets |
|---|---|---|---|
| **Typst PDF design system** | Shipped, partially blocked | Semantic fields, so a theme can decide that retrograde is *red* and a sign glyph is *display-weight* | `"♋︎ Cancer 3°12' ℞"` — one string, no seams |
| **Interactive HTML reports** | Planned, 0/5 phases | Sortable/filterable columns; a degree that is a *number* | A string. `sort()` on `"3°12'"` is lexicographic nonsense |
| **Internationalization** | 1 locale, 4 leaks | Canonical keys to look up, and slots to reorder | A sentence already committed to English word order |

They are the same request. The PDF theme wants `retro: True` so it can colour it; i18n
wants `retro: True` so it can render it as `逆行`; the HTML report wants `retro: True` so
it can filter on it. **Nobody wants the string `"Retrograde"`.** It is a lossy projection
that every consumer has to undo.

### 2.3 Why i18n cannot simply be bolted on

Today translation runs *after* formatting: sections build English strings, and
`_translate_section_data()` (`builder.py:178`) walks the finished output and does
word-boundary substring replacement against ~90 hand-listed terms
(`_get_translatable_terms()`, `builder.py:49`).

Four assumptions are welded into that, and each is false somewhere:

- **English word order is preserved.** `1879年3月14日` is a *reorder*. Substring
  replacement cannot reorder.
- **Latin word boundaries exist.** The matcher is literally `(?<![A-Za-z])term(?![A-Za-z])`.
  It is meaningless in a script without spaces.
- **No grammatical agreement.** Russian, Polish, Arabic and Hebrew inflect for case,
  gender and number. A flat `str → str` map cannot express *Aries* taking one ending in
  "Moon in Aries" and another in "ruler of Aries".
- **One word, one meaning.** The term list is **context-free**: `Fixed` is a modality
  *and* a star classification; `Square` is an aspect *and* a shape. A translator handed a
  flat list of English words cannot disambiguate. **This is the worst one**, because the
  output is confidently wrong rather than visibly missing.

The four leaks in a `zh_CN` report today are just the symptoms that surface first:

| Leak | Source | Why the swapper can't fix it |
|---|---|---|
| `March`, `AM` | `core.py:88` `strftime("%B %d, %Y")` | A date is not a word |
| `Rising)` | `core.py:131` `f"{ruler} ({asc_sign} Rising)"` | Composed; the parts translate, the frame doesn't |
| `House (Pl)` | `core.py:321` `f"House ({abbrev})"` | A **header** — headers get exact-match only, never the substring pass. Permanently untranslatable. |
| `Day Chart` | `core.py:126` `f"{sect.title()} Chart"` | Composed. Also in the term list but *not* in `strings.json` — the two have already drifted. |

### 2.4 Phase 0 — the measured surface

`scripts/i18n_surface.py` renders every section against a fully-populated chart and
captures the strings that actually reach the output, tagged by role. Ground truth, not a
grep:

**937 strings captured, 644 distinct, 452 needing translation.** By role:

| Role | Count | Fate under this spec |
|---|---|---|
| **cell** | **327** | **Evaporates.** The renderer composes it from canonical parts. |
| header | 43 | Becomes a message template (`House ({system})`) |
| section_name | 38 | Catalog / message |
| kv_key | 22 | Message |
| prose | 12 | Mostly developer hints ("Add `DignityComponent()` to…") — see §3 |
| svg_text | 10 | The chart's handful of real words |

**72% of the translation surface is not a translation problem.** `"0°♋︎Cancer 57'"`
does not need translating; it needs *not being a string in the first place*. Do
structure-first, and the i18n surface drops from **452 strings to ~125**.

That is the argument for doing these together, in this order. Doing i18n first would mean
hand-translating 327 strings that are about to stop existing.

---

## 3. Goals / Non-Goals

### Goals

1. **Structured payload is the single source of truth** for every section. Renderers
   derive strings from it; no renderer parses another renderer's output.
2. A consumer can **sort, filter, colour and re-order** on semantic fields.
3. A contributor can add a language by writing **one JSON file** — no Python.
4. Composed output (`House (Pl)`, `Mars (ruler of Aries)`) localizes correctly,
   **including reordering**.
5. Dates, times, numbers and coordinates follow **locale conventions**.
6. The vocabulary is **derived from the registries**, so a new body or aspect cannot
   silently become untranslatable.
7. A partially-translated locale degrades to **correct English** — never a raw key, never
   a crash.
8. "Has every section stopped stringifying?" is answerable **mechanically** (§9).
9. Locale is **passed, not ambient**.

### Non-Goals

1. **Grammatical agreement engines** (ICU MessageFormat, gender/plural selection). The
   design must not *preclude* them — slot values stay structured, so a future
   `{sign:genitive}` is a formatter change rather than a rewrite — but nothing we target
   needs it yet.
2. **Translating the prose renderer.** It generates natural-language sentences;
   templating those reads as stilted in every language, including English. English-only,
   documented. (The 12 "prose" strings in §2.4 are mostly *developer hints* — those
   become messages; the narrative prose does not.)
3. **Supplying translations ourselves.** We supply the mechanism and the English source;
   native speakers supply the content.
4. **Translating proper nouns** — names, geocoded places, IANA timezone identifiers.
5. **Bundling fonts for every script.** See §8.
6. **Changing what the reports say.** Rendered English output is byte-identical when this
   lands, or it is a bug.

---

## 4. Design

### 4.1 The section contract

`generate_data()` returns a **structured payload** as the source of truth. Semantic
fields keep canonical keys (`"Sun"`, `"Cancer"`, `"Placidus"`) and native types (a degree
is a `float`, retrograde is a `bool`), because canonical keys are what the catalog looks
up and native types are what a UI sorts on.

During migration each section *also* emits the derived `rows` (§7.1), so unmigrated
renderers keep working. Phase 3 drops `rows` once every renderer reads structure.

### 4.2 Catalog — the closed vocabulary

Bodies, signs, aspects, house systems, moon phases, elements, modalities, dignities,
motion states. **Derived from the registries at import**, not hand-listed, so it cannot
drift from `CELESTIAL_REGISTRY` / `ASPECT_REGISTRY` / `HOUSE_SYSTEM_CODES`.

Keys are **namespaced**, and the namespace is what buys back the context the flat term
list threw away:

```
body.Sun               sign.Cancer            aspect.Square
house_system.Placidus  phase.WaningGibbous    modality.Fixed
star.Fixed             motion.Retrograde      dignity.Exaltation
```

`modality.Fixed` and `star.Fixed` are now separable, and a translator sees the namespace
and knows what they are translating.

A term may carry a **short form** (`house_system.Placidus.short` → `Pl` / `普`), so the
narrow-column case lives in the catalog instead of a lookup table bolted on the side.
This subsumes the four disagreeing house-abbreviation implementations (§10).

### 4.3 Messages — templates with named slots

For the *chrome*: section names, headers, key-value labels, developer hints. **A message
key is its English template.** Slots are named, and slot values are themselves renderable.

```python
msg("House ({system})", system=term("house_system.Placidus", short=True))
msg("{ruler} (ruler of {sign})", ruler=term("body.Mars"), sign=term("sign.Aries"))
```

Translation replaces the **template**, so the target language picks its own word order and
punctuation. English is the identity locale: an untranslated key formats to correct
English for free — which is both the fallback and the reason a half-finished locale is a
usable state.

### 4.4 Formats — patterns, not vocabulary

Dates, times, numbers, degrees and coordinates are locale **data**:

```json
"format.date":        "{year}年{month_num}月{day}日",
"format.time":        "{hour24}:{minute}",
"format.decimal_sep": ".",
"format.degrees":     "{deg}°{min}'"
```

The English default (`"{month} {day}, {year}"`) is the fallback pattern. Both `month`
(name) and `month_num` are always supplied, so a locale takes whichever it needs. This is
what makes `March 14, 1879 → 1879年3月14日` a **config change rather than a code change**.

### 4.5 Renderers compose

A renderer receives structure and builds the display string last:

```python
# what every renderer does today, in English, inside the section:
f"{sign_glyph} {pos.sign} {deg_str}"

# what a renderer does under this spec:
render(msg("{glyph} {sign} {degrees}",
           glyph=p["sign_glyph"],                        # DNT: not a key
           sign=term(f"sign.{p['sign']}"),               # catalog
           degrees=fmt_degrees(p["lon"])),               # locale pattern
       locale)
```

Same output in English, byte for byte. Correct output in any locale. And the Typst theme
gets `p["retro"]` as a bool it can colour, instead of a `℞` it has to find in a string.

### 4.6 Three properties that fall out for free

- **Do-not-translate becomes structural.** A person's name, a geocoded place, an IANA
  timezone are slot *values*, never keys — so they can never be translated by accident.
  Today the only thing protecting `Ulm, Germany` is that nobody put "Germany" in the term
  list.
- **A real fallback chain.** `zh_Hant_TW → zh_Hant → zh → en`, so a regional locale
  inherits and overrides only what differs. Today lookup is exact-locale-or-English.
- **The HTML report becomes possible.** Sorting, filtering and tabbing are all trivial
  once the data is data.

---

## 5. Public API surface

```python
# stellium.i18n
t(key, locale=None)                       # exists; gains namespacing + fallback chain
term(key, *, short=False) -> Term         # new: a catalog reference
msg(template, **slots)     -> Message     # new: a template + named slots
render(value, locale)      -> str         # new: the formatter. Term | Message | str -> str
locale_chain(locale)       -> list[str]   # new: "zh_Hant_TW" -> [..., "zh", "en"]

set_default_locale(locale)                # exists; now only sets a default *argument*
get_available_locales()                   # exists

# Builders
ReportBuilder().with_locale("zh_CN")      # exists
ChartDrawBuilder().with_locale("zh_CN")   # new (Phase 4)
ChartDrawBuilder().with_font(path)        # new (Phase 4) — see §8

# CLI
stellium i18n coverage zh_CN              # new: a translator's worklist
stellium i18n extract                     # new: dump every key as a template locale file
```

`Term` and `Message` are frozen dataclasses, consistent with the library. `render()`
accepts a plain `str` and returns it unchanged — that is the migration bridge (§7.1).

### Module layout

```
src/stellium/i18n/
    __init__.py       # public surface
    loader.py         # exists: locale file loading, cache, t()
    catalog.py        # new: build the term catalog from the registries
    message.py        # new: Term, Message, render()
    formats.py        # new: date/time/number/degree pattern application
    pseudo.py         # new: the pseudolocale generator
    locales/zh_CN/strings.json
```

---

## 6. Locale file schema

One file per locale. `metadata` is informational; `strings` is a flat namespaced map.

```json
{
  "metadata": { "language": "zh-CN", "status": "draft", "fallback": "zh" },
  "strings": {
    "body.Sun": "太阳",
    "house_system.Placidus": "普拉西度斯",
    "house_system.Placidus.short": "普",
    "House ({system})": "宫位（{system}）",
    "format.date": "{year}年{month_num}月{day}日"
  }
}
```

Rules:

- A missing key falls back down the chain, ending at English (the key itself, or the
  English template).
- A **message** key is the English template verbatim — self-documenting, and the
  translator can see the slots they must preserve.
- Slot names in a translated template **must be a subset** of the English template's
  slots. Violations are *reported* by `stellium i18n coverage`, never raised: a bad
  translation should degrade, not crash a chart.

---

## 7. Migration plan

| Phase | Scope | Done when |
|---|---|---|
| **0 · Inventory** ✅ | `scripts/i18n_surface.py`: render every section, capture what reaches the output, classify. | Done — §2.4. 452 strings, 327 of them cells that evaporate. |
| **1 · Foundations** ✅ | `catalog.py`, `message.py`, `formats.py`, `pseudo.py`; fallback chain; `stellium i18n` CLI. The old substring translator stays and keeps working. | Done (`e4c206c`). `en`/`zh_CN` output byte-identical (pinned test); pseudolocale flags the unmigrated sections. Coverage: zh_CN 48%. |
| **2 · Sections** | The 13 unmigrated section files emit structured payloads, following `PlanetPositionSection`. `rows` still derived alongside. | Every section has a structured payload; the Typst theme reads structure for all of them. |
| **3 · Renderers** | Rich / HTML / markdown / plain renderers compose from structure via `render()`. Drop the derived `rows`. Delete `_get_translatable_terms()` and `_translate_section_data()` (~200 lines). | English output byte-identical. `zh_CN` report has zero leaks. Pseudolocale has zero unmarked strings outside the DNT set. |
| **4 · Charts** | `ChartDrawBuilder.with_locale()`; thread locale through renderer → layers. Small — 6 text elements per wheel. | Chart SVG renders in `zh_CN`. **Gated on §8.** |
| **5 · The rest** | CLI output; planner (Typst templates carry their own strings — a separate catalog); electional; and, with some irony, `chinese/` BaZi, which is entirely English. | Each its own PR. |

Phases 1–3 are what this spec commits to. 4–5 re-scope once 3 lands.

### 7.1 The bridge

Phase 1 adds machinery without removing anything. Through Phases 2–3, `render()` passes
plain strings through untouched and sections keep emitting `rows` — so **a section or
renderer that has not been migrated yet still works**, and the old substring translator
still covers it. One file at a time, and the pseudolocale reports the shrinking leak set
as a progress meter.

### 7.2 The `zh_CN` data

231 contributed strings, marked `status: draft`. Migrating to namespaced keys is a
mechanical transform — `"Sun"` → `"body.Sun"` — driven by the catalog, since the catalog
knows which namespace each English term belongs to. The ambiguous ones (the very terms
that motivated namespacing: `Fixed`, `Square`) are the only ones needing a human, and
there are few. The content deserves a review pass at the same time (§11).

---

## 8. Open decision: fonts (gates Phase 4)

We bundle 20 fonts. **None contains a CJK glyph** — the stack is Latin text plus Noto
Sans Symbols/Math for astrological glyphs.

- **SVG in a browser** — fine. `font-family` falls back to system fonts.
- **PDF (Typst) and PNG export** — Typst *also* searches system fonts
  (`typst_runtime.py:97`; `ignore_system_fonts` stays False), so a Chinese PDF renders
  correctly on a typical desktop and renders **tofu in a container or in CI**. Silently.

| Option | Cost | Verdict |
|---|---|---|
| Bundle Noto Sans SC | ~10 MB+ on the wheel; solves exactly one language | Arbitrary favouritism |
| **Don't bundle. Add `with_font()`, warn on missing glyphs** | Small; `MissingGlyphWarning` already exists for this class of problem | **Recommended** |
| Bundle a subset covering only the ~250 chars our locale data uses | ~100 KB | **A trap** — breaks the moment a user's chart has a Chinese *name* in it, the one input we cannot enumerate |

The recommendation is the only option that generalizes to Arabic, Devanagari or Thai.

---

## 9. Testing strategy

**One mechanism**, and it replaces per-string tests rather than adding to them.

### The pseudolocale is a completeness oracle

This is the part worth reading twice. "Has every section stopped stringifying?" is not
answerable by inspection — a leftover `f"{sign} {deg}"` in one branch of one section
looks exactly like correct code, and no linter will find it.

But render the report in a **pseudolocale** — a synthetic locale (`qps`) generated at
runtime from the catalog and message keys, so it can never go stale — where every key
maps to a marked, padded, deliberately-reordered value:

```
body.Sun         →  ⟦Ṡüṅ·······⟧
House ({system}) →  ⟦Ħöüṡé ({system})·······⟧
format.date      →  ⟦{day}/{month_num}/{year}⟧        (reordered on purpose)
```

Now **every string that went through the contract is bracketed**, and therefore any
*unbracketed* Latin text is, by construction, a string some section composed behind the
contract's back. The i18n leak test and the structure-first completeness test are **the
same test**. That is the strongest argument for doing these together.

Two more properties fall out of the same artifact:

- **Expansion safety.** The padding simulates the ~35% growth of German and Russian.
  Layout that breaks — a clipped SVG label, an overflowing PDF cell — breaks *here*,
  before a translator ever sees it.
- **Order safety.** The reordered date pattern proves nothing downstream assumes English
  word order.

The do-not-translate set (name, place, timezone) is small and enumerable, so it is
allow-listed rather than being a source of false positives.

### Byte-identical English

Every phase asserts the English report is unchanged. This is a refactor; if the output
moves, it is a bug. Cheap to check and it is the whole safety net for Phases 2–3.

### Coverage reporting — a tool, not a gate

`stellium i18n coverage zh_CN` reports what fraction of keys a locale defines, by
namespace, and what is missing: a **worklist for a translator**. Deliberately *not* a CI
check — an incomplete locale is a valid state that degrades to English, and gating on it
would mean a contributor cannot land a partial language.

---

## 10. Cleanups this subsumes

- **Four house-abbreviation implementations that disagree** (`Pl` vs `Plac`):
  `sections/_utils.py`, `sections/misc.py:755`, `visualization/extended_canvas.py:443`
  and `:1004`. The catalog's short forms replace all four.
- **Term-list ↔ `strings.json` drift** (`Day Chart` is in one, not the other). Deriving
  the catalog from the registries removes the class.
- **Renderers re-deriving what a section already knew.** The `℞` marker, the sign glyph,
  the retrograde flag are each recovered from strings today.

*(`Equal (MC)` and `Equal (Vertex)` both abbreviating to `Equa` — a collision from a
4-character truncating fallback — was fixed ahead of this spec in `3b61ea5`.)*

---

## 11. Open questions

- **`Topocentric` = 地心制.** 地心 means *geocentric*, the opposite; the astronomy term is
  站心. Needs a native speaker. (Separately: `Tropical` = 热带黄道 is **correct** —
  zh-wiki uses it.)
- Does the **web app** consume section data directly? Phase 3 changes its shape.
- Should `Message` support pluralization (`{n} aspects`) now, or wait for a language that
  needs it? Leaning wait; the design does not preclude it.
- Six sections need constructor arguments and were not surveyed in Phase 0 (transits,
  eclipses, ingresses, stations, profections). They are unlikely to change the shape of
  the problem, but they are not in the 452.

---

## 12. Acceptance criteria

**Phase 1**

- `t()` resolves through the fallback chain: `zh_Hant_TW` finds a `zh` string.
- The catalog builds from the registries — adding a body to `CELESTIAL_REGISTRY` adds a
  catalog key with no other edit.
- `render(msg("House ({system})", system=term("house_system.Placidus", short=True)), "zh_CN")`
  → `宫位（普）`; the same call with `"en"` → `House (Pl)`, **with no locale file present**.
- The pseudolocale renders the existing report and the four known leaks appear unbracketed.
- `en` and `zh_CN` output byte-identical to before the phase.

**Phase 2**

- Every section emits a structured payload; `typst_render.py` reads structure for all of
  them, parsing no strings.
- English output byte-identical.

**Phase 3**

- No renderer consumes `rows`; `rows` is gone.
- `_get_translatable_terms()` and `_translate_section_data()` are gone.
- The `zh_CN` report contains no English outside the DNT set.
- The pseudolocale report contains **no unbracketed string** outside the DNT set — which
  is to say: no section is stringifying behind the contract's back.
- A locale file containing **one** key still renders a complete, correct, mostly-English
  report.
