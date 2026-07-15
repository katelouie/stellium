# Spec: Unified Section → Renderer Contract

| | |
|---|---|
| **Status** | **Proposed.** Design approved (see §5). Not yet built. Survey complete (§2). |
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
- Text renderers are **untouched**: cells stay plain strings.

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

## 4. Design

### 4.1 Two names: stable `section_key` + localized display name

A section carries a **stable internal identity** distinct from its **display title**:

- **`section_key`** — a fixed English-ish slug (`"planet_positions"`, `"chart_overview"`,
  `"moon_phase"`). Never localized. Emitted in the section dict. Drives all
  behind-the-scenes handling: Typst dispatch, special-payload selection, any table-family
  logic-gating.
- **display name** — the tuple's `name`, localized by the resolve pass exactly as today,
  used for the rendered header.

This directly replaces the fragile `name.lower() == "chart overview"` routing
(`typst_render.py:428`) with `section_key == "chart_overview"`. It composes with the
existing `type` field: `type` is the **shape** (table / key_value), `section_key` is the
**identity** (planet_positions vs house_cusps — both `type: table`).

> Why not one field? `type` says how to lay it out generically; `section_key` says whether
> a renderer has a bespoke treatment for *this specific* section. Most sections need only
> `type`; the ~4 rich ones are found by `section_key`.

### 4.2 The unified resolve pass

Extend `_resolve_structured` so it **deep-resolves token values anywhere in the dict**, not
only inside `headers`/`rows`/`data`/`tables`. The rule stays type-correct:

- **Label positions** (section name, `headers`, `key_value` keys, table `title`) — wrapped
  as `msg(...)` so a bare string routes through the catalog (unchanged behavior).
- **Every other value, at any depth** — resolved as a *plain value*: a `Term`/`Message`/
  `date` renders to a localized string; a plain `str`, `int`, `float`, or `bool` passes
  through untouched.

Because raw strings pass through, the language-neutral bits of a payload — the glyph char,
the canonical `name` used for color/matching — survive verbatim, while the display fields
(which the section now emits as tokens) get localized. One pass, every shape.

### 4.3 Rich payloads carry tokens; build once, derive rows

The bespoke sections stop emitting raw English in their payloads. The payload's **display**
fields become tokens; only the **language-neutral** fields stay raw:

```python
# PlanetPositionSection, per planet — the SINGLE source of truth
planet = {
    "name":  pos.name,                       # canonical, raw — color/matching/glyph key
    "label": term(f"body.{pos.name}"),       # display  → localized by the resolve pass
    "glyph": glyph,                           # language-neutral
    "sign":  term(f"sign.{pos.sign}"),        # display  → localized
    "sign_glyph": sign_glyph,                 # language-neutral
    "degree": deg_str, "houses": houses,      # neutral
    "speed": speed_str, "retro": pos.is_retrograde,
}
```

The flat `rows` are then **derived** from the payload rather than hand-built a second time:

```python
rows = [ compose_row(p) for p in planets ]   # the flat view, for text renderers
```

One data construction; two views (flat rows for text renderers, structured payload for
Typst). This kills the "build it twice" smell §2.3 identified.

### 4.4 Column metadata (optional, section-level)

Structural hints about columns are declared **once per section**, never per cell:

```python
"columns": [
    {"role": "body",     "align": "left"},
    {"role": "position", "align": "left"},
    {"role": "house",    "align": "right"},
    {"role": "numeric",  "align": "right"},   # speed
    {"role": "motion"},
]
```

Roles let generic Typst tables get consistent treatment (numeric right-alignment,
emphasis) without per-section code. They are **not** where glyph identity lives — that
stays in the payload's canonical `name` (glyphs need the canonical key, which a localized
cell has lost). Column metadata is a convenience for the generic path; the bespoke path
uses the payload.

### 4.5 Chrome moves from `.typ` into section-declared labels

Every hardcoded display label in the templates (§2.2 item 2) becomes a **section-declared,
localized label** passed through the JSON. The `.typ` reads the value instead of a literal:

```typst
// before
lbl("Planet", size: 7.5pt)
// after
lbl(headers.planet, size: 7.5pt)   // headers.planet already localized in the data
```

The section provides a small labels block (`planet`, `position`, `speed`, `motion` for the
planet table; `elements`, `modalities`, `polarity`, `yang`, `yin` for the snapshot). The
resolve pass localizes them like any other label. `List B` from the survey — the glyph and
palette maps keyed by `"Sun"`/`"Trine"` — **stays untouched**; those keys are never
displayed.

### 4.6 Renderer behavior after the change

- **Text renderers** — unchanged. Read `type` + container keys, `str()` the cells, use the
  localized display name.
- **Typst renderer** — dispatch on `section_key`. For the ~4 bespoke sections, lay out from
  the (now localized) payload + declared labels. For everything else, render a **generic**
  table/key_value/text/compound from the resolved `headers`/`rows`/`data` — the same keys
  the text renderers read. Delete `_planet_positions`/`_moon_phase` raw re-derivation, the
  title-substring routing, and the hardcoded `.typ` chrome.

---

## 5. Design decision: payload + dispatch, not per-cell enrichment

An alternative was considered and **rejected**: making each resolved cell a rich object
(`RenderedCell(text, glyph, key)`, `__str__` → text) so any renderer could pull glyph and
identity from any cell.

Rejected because:

1. **It touches every renderer.** A cell that is secretly an object breaks any renderer
   doing `.upper()`, slicing, or `len()` on it — and the survey shows they treat cells as
   real strings. Plain-string cells keep the text renderers literally unchanged.
2. **It duplicates the column role on every row.** "Column 0 is a body" is one fact;
   per-cell `key` restates it once per planet. Section-level column metadata states it
   once.
3. **It pays for generality nobody uses.** Enriching all cells would let *any* table render
   glyphs — but most sections are plain flat tables wanting no special handling, and the
   few bespoke ones want hand-built layout regardless. Enriching every cell to serve four
   sections is the wrong trade.

The chosen model — **plain-string cells + a stable `section_key` + section-level metadata +
localized payloads** — confines the complexity to exactly the sections that have it, and
keeps the common path (a flat table) trivial.

---

## 6. Migration plan

Each step ends green with English byte-identical (markdown hash **and** PDF text) before
the next begins.

1. **Contract + resolve.** Add `section_key` to the section dicts; swap `_map_section`
   routing from title-substring to `section_key`; extend `_resolve_structured` to
   deep-resolve token values anywhere. Prove: text output unchanged, English PDF unchanged
   (the payloads are still raw English at this point, so nothing moves yet).
2. **Planet positions.** Emit the `planets` payload with tokens; derive `rows` from it; add
   the labels block; rewrite the Typst planet table to read localized payload + labels.
   Prove English unchanged, `zh_CN`/`zh_Hant` planet names + headers localized.
3. **Aspects + moon.** Same treatment for the aspect list, the aspectarian, and the
   moon-phase key/value (drop `_moon_phase`'s hardcoded fields — it becomes an ordinary
   localized `key_value`).
4. **Snapshot chrome + cleanup.** Move `engine.typ`'s `Elements`/`Modalities`/`Polarity`/
   `Yang`/`Yin` to declared labels; delete the dead Typst mappers, the substring routing,
   and every hardcoded `.typ` chrome literal from List A.

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
7. Text renderers are unchanged (no diff to their cell handling).

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
