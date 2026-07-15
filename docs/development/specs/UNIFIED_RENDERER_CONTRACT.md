# Spec: Unified Section → Renderer Contract

| | |
|---|---|
| **Status** | **In progress.** Steps 1–2 landed (dispatch + planet table); the **`Gloss`** primitive (§4) is built and spiked. The resolve-pass reshape onto `Gloss` (steps 3–5) is next. |
| **Created** | 2026-07-15 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Relates to** | Completes the *renderer half* of [STRUCTURE_FIRST_SECTIONS.md](./STRUCTURE_FIRST_SECTIONS.md). That spec made sections emit structure and text renderers compose last; this one makes **every** renderer — the Typst/PDF one included — consume that structure through a single contract. **Grammatical inflection** (plurals, case, gender for languages like Russian/German) is handled *below* this contract, inside `render()` — see [I18N_GRAMMATICAL_INFLECTION.md](./I18N_GRAMMATICAL_INFLECTION.md). A `term()` stays a `term()` here; it only gains the ability to inflect when a locale provides forms, so this contract is unaffected by that work. |

---

## 1. Summary

The structure-first refactor gave the **text** renderers (markdown, rich, plain, HTML,
prose) a clean, agnostic contract: dispatch on `type`, read the container keys for that
type (`table` → `headers`/`rows`, `key_value` → `data`, …), and lay out already-localized
strings. One resolve pass (`_resolve_structured`) localizes everything they read before
they see it. They share one contract and do layout only.

The **Typst/PDF** renderer never joined that contract. It reads a second, *raw*
representation the sections emit specifically for it (`planets`, `aspect_pairs`, `graph`),
which the resolve pass never touches; it hardcodes column headers in the `.typ` templates;
and it routes on English section-title substrings. The result: a localized report renders
correctly as markdown and leaks English across most sections as a PDF (planet names, sign
names, motion, aspect names, `PLANET`/`SPEED`/`ELEMENTS`/`POLARITY`/`Yang`/`Yin` …).

This spec **unifies the section → renderer boundary** so there is one localization system
and one dispatch mechanism for all renderers:

1. **One localization pass** over the *entire* section dict — rich payloads included — not
   just the table-shaped keys.
2. **A stable `section_key`** for behind-the-scenes dispatch, split from the **localized
   display name**, so translating a title can never break routing.
3. **Plain-string cells** for text renderers (unchanged); **localized structured payloads**
   for the few sections whose layout is genuinely bespoke.
4. **Chrome moved out of the templates** into section-declared labels the resolve pass
   localizes.

---

## 2. Problem & Motivation

### 2.1 The agnostic contract already exists — for text renderers

Every text renderer (`renderers.py`: `RichTableRenderer`, `PlainTextRenderer`,
`MarkdownRenderer`, `HTMLRenderer`, `ProseRenderer`) dispatches on `data["type"]` and reads
**only** the container keys for that type:

| `type` | keys read |
|---|---|
| `table` | `headers`, `rows` |
| `key_value` | `data` |
| `text` | `text` / `content` |
| `compound` | `sections` |
| `side_by_side_tables` | `tables[].{title, headers, rows}` |
| `svg` | `content` / `path` |

`_resolve_structured` (`builder.py:184`) guarantees that by the time a renderer sees a
section, every string in those keys — section name, headers, key-value keys, table titles,
and all cells — is already a **localized plain string**. The text renderers know nothing
about i18n; they `str()` cells and lay them out. This is the "single system, agnostic
renderers" shape we want to preserve.

### 2.2 The Typst renderer diverges on three axes

The survey (§2.4) found the PDF path breaks that contract in three ways:

1. **It reads raw parallel payloads the resolve pass never localizes.**
   `_planet_positions` (`typst_render.py:297`) reads `d["planets"]`; `_generic` reads
   `d["graph"]` / `d["aspectarian"]` / `d["aspect_pairs"]`; `_moon_phase` reads `d["data"]`
   and rebuilds its own field list. `_resolve_structured.walk()` only recurses into
   `headers`/`rows`/`data`/`tables`/`sections`; every other key rides through untouched via
   `**data` + `return data` (`builder.py:262`). So those payloads reach Typst in raw
   English.

2. **It hardcodes chrome in the `.typ` templates.** `components.typ:224–229` (`Planet`,
   `Position`, `Speed`, `Motion`), `components.typ:455–467` (`Applying`, `Separating`,
   `Planet 1`, `Aspect`, `Planet 2`, `Orb`), `engine.typ:50–79` (`Elements`, `Modalities`,
   `Polarity`, `Yang`, `Yin`). No data value can change these.

3. **It routes on localized titles.** `_map_section` (`typst_render.py:428`) matches
   `name.lower() == "chart overview"` / `"moon phase"` / `"dispositor"`. Localize the title
   and the special-casing silently stops firing.

### 2.3 The duplication is at the source

Three sections build the same data **twice** — once as tokenized `rows` (for text
renderers) and again as a raw-English payload (for Typst):

| Section | tokenized `rows` | raw payload |
|---|---|---|
| `PlanetPositionSection` (`core.py:390`) | yes | `planets` |
| `AspectSection` (`aspects.py:372`) | yes | `bodies`, `aspect_pairs`, `aspectarian` |
| `TransitListSection` (`transit_periods.py:485`) | no (fully raw) | `periods` |

That per-section duplication — the same fact emitted in two shapes, only one of them
localized — is the root of the divergence.

### 2.4 Survey (the measured surface)

Full findings from the four-part read are recorded in the branch history; the load-bearing
facts are §2.1–2.3 above, plus:

- **Only ~4 sections need bespoke Typst layout** (planet positions, aspect list,
  aspectarian, snapshot). Every other section is a plain `table` / `key_value` / `text` /
  `compound` that Typst can render generically from the resolved contract.
- **`_moon_phase` is the one place Typst fully re-derives a section** with its own
  hardcoded English field labels (`Illumination`, `Phase Angle`, `Sun–Moon Sep.`, …,
  `typst_render.py:333–340`).
- A separate, **broader** gap exists: several sections are only *partially* tokenized even
  in `rows` (Fixed Stars' *Nature/Keywords*, Arabic Parts' *Formula/Description*, ZR's
  *ruler*, the rectification sections at zero tokens). The substring bridge half-catches
  these for text output; Typst won't. **This is a different axis (finish tokenizing
  sections) and is out of scope here** — see §3 Non-Goals.

---

## 3. Goals / Non-Goals

### Goals

- One localization pass covers **every** value a renderer might read, in any section
  shape, including rich payloads. No renderer localizes.
- Robust dispatch: renderers key off a **stable identifier**, never a localized string.
- The Typst PDF, in a non-English locale, contains **no English** outside the
  do-not-translate set (proper nouns, IANA zones, brand). Provable by the pseudolocale
  oracle extended to the PDF-JSON path (§7).
- English output — markdown **and** PDF — is **byte-identical** to before.
- Text renderers flatten at their **display edge** (a single `unmask()`); their internal
  cell handling stays string-based (a `Gloss` is its English string to everything but the
  final `.loc` read).

### Non-Goals

- **Finishing per-cell tokenization** of the partially-migrated sections (§2.4). Real, but
  a separate axis tracked under STRUCTURE_FIRST_SECTIONS.
- **SVG-baked sections** (dispositor graph, ZR/profection/gantt/midpoint-tree). They draw
  text into SVG at generate-time and localize via the ambient-default-locale mechanism;
  this spec does not disturb that path.
- The **planner** product (`planner.typ`, `planner_components.typ`). Different product,
  separate labels.
- Interactive HTML sort/filter (a downstream beneficiary of the same structure, not built
  here).

---

## 4. Design — Gloss: identity coupled to presentation

The unifying primitive is **`Gloss`** (`stellium/i18n/gloss.py`): a concept resolved for a
locale that carries *both* dimensions at once, so nothing downstream has to choose between
matching and displaying.

### 4.1 The `Gloss` object

```python
class Gloss:            # not a str subclass — see below
    en:  str            # identity — the internal language every machine op matches on
    loc: str            # presentation — the mask a renderer flips on at the display edge
    key: str | None     # finest identity ("sign.Aries") for glyph/colour lookup

    __eq__/__hash__  → delegate to .en   # a Gloss IS its English string as a dict key
    __str__          → .en               # a forgotten .loc leaks visible English
```

`gloss(term_or_message, locale)` produces one by rendering the token twice — once in `"en"`,
once in `locale` — so a Message's slots and a list join localize consistently in each
dimension for free.

Three properties earn it its place:

1. **Machinery is locale-invariant.** `==` and `hash` go by `.en`, so `data["Illumination"]`
   finds a `Gloss` key in *any* locale. This is the direct kill for the entire "lookup
   breaks under localization" bug class (§2.2/§2.3): the cover scrape, the moon `get()`, the
   dispatch match — all were machinery keyed on a string the resolve pass had translated out
   from under them. A `Gloss` key can't be translated out from under anything.
2. **It fails safe, not silent.** Deliberately **not** a `str` subclass. `==`/`hash` make it
   a drop-in dict key, but a string *operation* (`.upper()`, slicing, `+`) raises instead of
   silently returning English and dropping the mask. And `__str__` returns `.en`, so a
   renderer that forgets `.loc` prints **visible English** — which the pseudolocale
   completeness oracle catches mechanically. Silent-wrong output is impossible.
3. **It is where inflection lives** (see I18N_GRAMMATICAL_INFLECTION.md). `.en` is always
   plain identity; all grammar happens when computing `.loc`. The two designs compose.

### 4.2 The resolve pass produces `Gloss`, not flat strings

`_resolve_structured` stops flattening a `Term`/`Message` to a bare localized string and
instead produces a `Gloss(en, loc)` in its place, everywhere in the section dict (labels,
cells, and rich-payload display fields alike). A plain string with no token passes through
unchanged (the substring bridge still handles un-migrated sections; it **skips** `Gloss`
values, which are already resolved). One pass, one primitive, every shape — and the
structure that flows out still *looks* like its English self to every machine that reads it.

### 4.3 Rich payloads: `Gloss` collapses the canonical/display split

The `name`-vs-`label` duality §2's planet payload needed is now one field. A `Gloss` label
carries the display in `.loc` **and** the canonical identity in `.en`/`.key`:

```python
planet = {
    "label": term(f"body.{pos.name}"),   # → Gloss: .loc "太阳" prints, .en "Sun" looks up the glyph
    "glyph": glyph,                       # language-neutral
    "sign":  term(f"sign.{pos.sign}"),    # → Gloss: .loc "双鱼座", .en "Pisces" tints the disc
    "degree": deg_str, "houses": houses, "retro": pos.is_retrograde,
}
rows = [compose_row(p) for p in planets]  # derived — the same Glosses, one construction
```

Built once, `rows` derived. (During migration a raw canonical field may stay alongside for a
step; the endpoint is the single `Gloss`.)

### 4.4 The JSON boundary — encoder emits the mask; identity travels beside it

A `Gloss` isn't JSON-serializable. The encoder emits its **`.loc`** (the display string), so
the `.typ` templates receive plain localized strings and need *no change* on the generic
paths. Where a template genuinely needs identity (the planet disc's glyph/colour lookup), the
payload carries the canonical field explicitly, or the encoder emits `{en, loc}` for that
field and the `.typ` reads `.en`. The spike proved both shapes clean.

### 4.5 Renderer behaviour after the change

- **Text renderers** — call `unmask()` (`.loc` for a `Gloss`, the value unchanged otherwise)
  at their **display edge**. Their internals stay string-based; it is a one-line flatten at
  the boundary, after any machinery, not a rewrite of cell handling.
- **Typst mappers** — read `.en` for identity (dispatch, the moon field ID, glyph lookup)
  and let `.loc` flow to the `.typ` via the encoder. `_moon_phase` stops re-deriving hardcoded
  English fields — it iterates the glossed key/value, IDs fields by `.en`, prints `.loc`.
  `_generic` uses `unmask` instead of `str()` (which would print `.en`).
- **The `.typ`** — generic paths unchanged (they get `.loc` strings); hardcoded chrome moves
  to section-declared labels (also Glosses → `.loc`).

### 4.6 What `Gloss` subsumes

Three things this spec earlier built by hand collapse into the one primitive:

- **`section_key`** (§ was 4.1) — the section name is a `Gloss`; `.en` dispatches, `.loc`
  displays. (`section_key` may stay as an explicit belt-and-braces slug, but is no longer
  load-bearing.)
- **The payload canonical/display split** (§4.3) — one `Gloss` field, not `name` + `label`.
- **The labels-map / per-structure identity schemes** — never built; `Gloss` is the identity
  everywhere.

---

## 5. Design decision: a `Gloss` object, not a string and not a parallel map

The primitive went through three shapes before landing on `Gloss`; recording the path so it
is not re-litigated:

1. **Per-cell rich object `RenderedCell(text, glyph, key)`** — rejected: it made every cell a
   non-string and forced every renderer to learn a new cell type, and it restated the column
   role on every row.
2. **Parallel `labels` map + stable `section_key`** — workable but *per-structure*: every
   section shape needed its own identity-beside-display scheme, kept in sync by hand. Identity
   and display living in two structures is the thing that drifts.
3. **`RosettaStr(str)`** — a `str` subclass with `.trans`. Elegant (machinery transparent)
   but a **footgun**: every `str` method (`.upper()`, `+`, an f-string) silently returns the
   English content and *drops the translation*, and JSON serializes the English. Silent
   failures.

**`Gloss` keeps the good part of each and drops the traps.** Like `RosettaStr` it couples the
two dimensions in one value, so there is no parallel structure to sync and machinery reads
identity transparently via `==`/`hash`. Unlike `RosettaStr` it is **not** a `str`, so string
operations fail *loudly* rather than silently masking-then-dropping — and `__str__ = .en`
plus the completeness oracle means the one residual failure mode (a forgotten `.loc`) is
caught mechanically as visible English. One primitive, universal, safe by construction.

---

## 6. Migration plan

Each step ends green with English byte-identical (markdown hash **and** PDF text) before
the next begins. Steps 1–2 landed under the pre-Gloss design; step 2b re-homes them on
`Gloss` and the rest follows almost for free.

1. **Contract + resolve.** ✅ Landed. `section_key` dispatch; deep-resolve token values
   anywhere. Byte-identical.
2. **Planet positions.** ✅ Landed. Payload with tokens, rows derived, section-declared
   labels, Typst planet table reads localized payload. Byte-identical English; zh planet
   table localized.
2b. **`Gloss` foundation.** ✅ Landed (additive). The `Gloss` primitive + `gloss()`/`unmask()`,
   spiked end-to-end on moon-phase data.
3. **Resolve pass → `Gloss`.** The reshape. `_resolve_structured` produces `Gloss` for
   tokens; the substring bridge skips `Gloss`; text renderers `unmask()` at their edge; the
   Typst JSON encoder emits `.loc`. English stays byte-identical (`.loc == .en` in English,
   and `__str__` is `.en` regardless); a missed `unmask()` shows English, not a crash or a
   wrong lookup. Prove text + PDF byte-identical English; zh unchanged from step 2.
4. **Moon phase on `Gloss`.** `_moon_phase` iterates the glossed key/value, IDs fields by
   `.en`, prints `.loc` — deleting every hardcoded English field label and the broken
   English-key lookup. First section the reshape *fixes*.
5. **Aspects + generic chrome.** Aspect list + aspectarian via the same read-`.en`/print-`.loc`
   pattern; `_generic` uses `unmask` not `str()`; snapshot chrome (`Elements`/`Polarity`/…)
   moves to section-declared label Glosses. Delete the dead mappers and the hardcoded `.typ`
   chrome.

---

## 7. Testing strategy

- **Byte-identical English, both paths.** The existing markdown-hash guard stays. Add a
  PDF-path check: the report-JSON built by `build_report_data(...)` in English is unchanged
  (assert against a captured baseline of the JSON, which is cheaper and more legible than
  hashing the PDF binary).
- **The pseudolocale reaches the PDF path.** Today the completeness oracle certifies
  migrated sections in the *markdown* output. Extend it: render `build_report_data(chart,
  section_data, …, locale=PSEUDO_LOCALE)` and assert **no unbracketed Latin** in the
  emitted JSON's display fields outside the do-not-translate set. This is the mechanical
  answer to "did the whole PDF path stop stringifying English?" — the same trick the parent
  spec used for text, now covering Typst.
- **Per-locale render smoke.** `generate_review.py` (renders `zh_CN` + `zh_Hant_TW`, chart
  + PDF) is the human-review artifact; a small automated version asserts a handful of known
  strings (`行星`, `太陽`, `北緯…`) appear and known leaks do not.

---

## 8. Acceptance criteria

1. `_resolve_structured` localizes token values at any depth; a payload's `label`/`sign`
   tokens come out localized while its `glyph`/`name` stay raw.
2. Typst dispatch is entirely on `section_key`; no renderer branches on a localized string.
3. A `zh_CN` / `zh_Hant_TW` PDF has no English outside the do-not-translate set — planet
   names, sign names, motion, aspect names, and all column headers localized. Verified by
   the extended pseudolocale oracle.
4. English markdown and English PDF are byte-identical to pre-change.
5. The `planets`/`aspect_pairs` payloads and the flat `rows` are built from **one**
   construction (rows derived), and no section emits the same data twice by hand.
6. `_moon_phase`'s hardcoded English field labels and all List A `.typ` chrome literals are
   gone; the templates read declared, localized labels.
7. The resolve pass produces `Gloss`; machinery reads `.en`, renderers `unmask()` to `.loc`
   at their edge; a forgotten `.loc` surfaces as oracle-caught English, never a wrong lookup.

---

## 9. Open questions

- **Column-role vocabulary.** Minimal set to start (`body`, `position`, `house`, `numeric`,
  `motion`, `sign`)? Roles are additive — start with what the bespoke tables need and grow.
- **Where the labels block lives.** Per-section in its data dict (localized by the resolve
  pass) vs. a single shared labels dict on `meta`. Leaning per-section: it keeps a
  section's chrome with the section and localizes through the existing path.
- **`TransitListSection`.** It is fully raw (no tokens at all) and emits a `periods`
  payload; it needs tokenizing *and* the payload treatment. Fold into step 3, or defer with
  the other partially-tokenized sections (§3 Non-Goals)? Leaning defer — it is the
  tokenization axis, not the contract axis.
