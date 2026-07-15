# Spec: Font Provisioning & Chart-Wheel Localization

| | |
|---|---|
| **Status** | **Proposal.** Built on `feat/structure-first-sections` (it blocks the Chinese chart output). |
| **Created** | 2026-07-14 |
| **Owner** | Kate |
| **Type** | Spec-Driven Development (SDD) design doc |
| **Tracking** | Obsidian: "Chart wheel localization + non-Latin font provisioning" |
| **Depends on** | [STRUCTURE_FIRST_SECTIONS.md](./STRUCTURE_FIRST_SECTIONS.md) — reuses the catalog, `term()`/`t()`, and the format patterns. |

---

## 1. Summary

The report side now renders in an arbitrary language. The **chart wheel** — `chart.draw()`,
the `visualization/` pipeline — does not: it has no `with_locale()`, no i18n imports, and
none of the report work touches it. Worse, even once it *has* a locale, a Chinese wheel
**cannot render correctly as PNG or PDF**, because Stellium rasterizes those with only its
**bundled fonts** (by design, for reproducibility) and the bundle contains no CJK glyph.

This spec adds two things, in order, because the second is useless without the first:

1. **Font provisioning** — a "bring your own font, fetched on demand" system modelled on the
   existing ephemeris download: per-script font packs hosted outside the wheel, pulled by
   `stellium fonts download <script>` into `~/.stellium/fonts/` (sibling to `ephe/`),
   auto-discovered by the renderer, with a `with_font()` override and a tofu warning that
   names the fix.
2. **Chart-wheel localization** — `ChartDrawBuilder.with_locale()`, threading a locale into
   the header/info/table layers so their *words* (date, house system, zodiac, element and
   modality names) render through the catalog. The wheel body is already language-neutral.

---

## 2. Problem & Motivation

### 2.1 The wheel is a separate, un-localized pipeline

`ChartDrawBuilder` (`visualization/builder.py`) is standalone — it does not go through
`ReportBuilder`, so it gets none of the report side's locale plumbing. It has ~25 `with_*`
methods and not one is `with_locale()`. `visualization/` imports nothing from
`stellium.i18n`.

**What the wheel draws, by kind:**

- **Glyphs** — planets, signs, aspects, angles, degree ticks. These are **embedded SVG
  paths** (`glyph_svg_path`), not font characters, so they are font-independent *and*
  language-neutral. Nothing to do.
- **Words** — the header and info corners (`layers/info_corners.py`): the person's name
  (DNT), date, location (DNT), timezone (DNT), house system, zodiac (`Tropical`/`Sidereal`),
  moon phase; and, when enabled, the element/modality tables (`Fire`, `Cardinal`…), aspect
  counts and chart shape. **This is the whole localizable surface, and the catalog already
  holds almost all of it** (`sign.*`, `house_system.*`, `element.*`, `modality.*`, the
  format patterns).

### 2.2 Even with a locale, a CJK wheel is tofu — by design

`raster.py` is explicit and correct about this: a chart's text names a **font family**, and
every rasteriser (rsvg, cairosvg, browsers) resolves that family against available fonts.
To make a PNG reproducible everywhere — laptop, CI, a bare container — Stellium renders it
with **Typst using only the bundled fonts** (`font_paths()` → `data/fonts/`). The bundle is
Latin + astrological-symbol fonts; **no CJK, Arabic, Devanagari or Thai.**

So the property that makes PNG export robust is exactly what makes a Chinese wheel render as
tofu — *guaranteed*, not host-dependent. (SVG-in-a-browser escapes this only because the
browser silently falls back to a host CJK font.)

### 2.3 The two rejected options

- **Bundle a CJK font.** +10 MB to the wheel; solves *only* Chinese; leaves Arabic, Hindi,
  Thai users stuck; and even Noto SC doesn't fully cover traditional-only characters.
- **Pure BYO** (user must always pass a font path). No bloat, but every non-Latin chart is
  friction and easy to get wrong.

### 2.4 The precedent this follows

Stellium already solves "large data files that don't belong in the wheel" for the Swiss
Ephemeris: `cli/ephemeris_download.py` pulls the ~334 MB set via `urllib` into
`~/.stellium/ephe/`, and `data/paths.py` owns `USER_DATA_DIR = ~/.stellium`. Fonts get the
same treatment, one directory over.

---

## 3. Goals / Non-Goals

### Goals

1. A non-Latin chart renders correctly **as SVG, PNG and PDF** once the user has the font.
2. Getting the font is **one command** (`stellium fonts download zh`), not a manual hunt.
3. Font packs live **outside the wheel** — zero size cost for the Latin-only majority.
4. Once downloaded, fonts are **auto-discovered**; charts "just work" with no per-call flag.
5. `with_font(path)` for an explicit one-off font not in a pack.
6. A missing font **fails loud with the remedy**, never silent tofu.
7. Downloads are **integrity-checked** and carry their **licenses**.
8. The wheel's words localize through the **same catalog** as the report side.

### Non-Goals

1. **Bundling any non-Latin font in the package.** The whole point.
2. **Localizing the glyphs.** They are language-neutral SVG paths already.
3. **Translating the fonts' coverage of user data.** If a user's chart has a name in a
   script their chosen pack doesn't cover, that is on the pack; we surface it, not fix it.
4. **Shipping our own translations.** As on the report side: mechanism, not content.
5. **A font manager.** Download, verify, discover, warn. Not versioned rollback, not GUI.

---

## 4. Design — Part A: Font provisioning

### 4.1 Where fonts live

```
~/.stellium/
    ephe/          # existing — Swiss Ephemeris data
    fonts/         # NEW — downloaded font packs, one subdir per script
        zh/        NotoSansSC-Regular.ttf  OFL.txt
        zh-hant/   NotoSansTC-Regular.ttf  OFL.txt
        ...
```

`data/paths.py` gains `get_user_fonts_dir() -> ~/.stellium/fonts/`, mirroring
`get_user_ephe_dir()`. The cache stays out of `~/.stellium/`, as it already does.

### 4.2 Hosting — *not* in the package repo

The distributed font files must **not** be committed to the main repo tree — 10 MB+ binaries
in git history are paid by every clone forever (the same reason the ephemeris set isn't in
the repo). Two acceptable homes, both servable by **jsDelivr**:

- **GitHub Release assets** on this repo (`.../releases/download/fonts-v1/...`), or
- a **separate `stellium-fonts` repo** served at
  `cdn.jsdelivr.net/gh/katelouie/stellium-fonts@v1/zh/NotoSansSC-Regular.ttf`.

A staging `assets/fonts/` at the repo root is fine as the *source* the release is cut from,
as long as the shipped copy is a release/other-repo — not the package tree.

*(Decision deferred to §8; the downloader is written against a base URL either way.)*

### 4.3 The manifest, checksums and licenses

A small `font_packs.json` manifest (bundled in the package for offline CLI reads; its URLs
point at the release) declares each pack. A pack may carry **more than one font, each with
a role** — `sans` / `serif` / `mono` — so every Latin role gets a matching non-Latin
companion (the chart wheel's labels want the sans; a themed PDF's body wants the serif).
`scripts/build_font_manifest.py` generates this from a staging folder (§7, A2):

```json
{
  "version": "fonts-v1",
  "base_url": "https://github.com/katelouie/stellium/releases/download/fonts-v1",
  "packs": {
    "zh": {
      "covers": "Simplified Chinese",
      "fonts": [
        {"role": "sans",  "family": "Noto Sans SC",  "name": "NotoSansSC-Regular.ttf",
         "asset": "zh_NotoSansSC-Regular.ttf",  "sha256": "…", "bytes": 10485760},
        {"role": "serif", "family": "Noto Serif SC", "name": "NotoSerifSC-Regular.ttf",
         "asset": "zh_NotoSerifSC-Regular.ttf", "sha256": "…", "bytes": 11010048}
      ],
      "files": [{"name": "OFL.txt", "asset": "zh_OFL.txt", "sha256": "…", "bytes": 4096}]
    }
  }
}
```

`asset` is the (script-prefixed, collision-free) filename in the flat release; `name` is
how it installs, under `~/.stellium/fonts/<script>/`. Role and family are read from each
font (family from the `name` table, role from the family name), overridable per file via a
pack's optional `meta.json`.

- **Checksum.** Every file is verified against its `sha256` after download; a mismatch
  aborts and deletes the partial file. Fonts are binaries pulled over the network and font
  parsers have a CVE history — this is not optional. (The ephemeris downloader lacks this
  today; fonts start it right, and it can be retrofitted there later.)
- **License.** Each pack includes its `OFL.txt`; the downloader fetches it too. Noto/Source
  Han are OFL — redistributable, but the license must travel with the font.

### 4.4 Resolution and auto-discovery

Font resolution has to reach **both** render paths, and is **role-matched** — the CJK
`sans` slots into the sans stacks, the CJK `serif` into the serif/display stacks, so a
themed PDF's serif body gets a serif CJK companion rather than whatever fallback finds
first:

- **SVG** — the pack's `sans` family is prepended to `style["font_family_text"]` (and its
  `serif`, when present, to any serif stack the theme uses), so the SVG text names it first.
- **PNG/PDF** — the fonts' *directory* is appended to Typst's `font_paths()`; Typst then
  covers CJK codepoints, and naming the role-matched family in the document keeps sans-with-
  sans and serif-with-serif.

The single seam is `typst_runtime.font_paths()`, which today returns only the bundle. It
becomes:

```
font_paths() = [bundled data/fonts]
             + [~/.stellium/fonts/**]        # auto-discovered, all installed packs
             + [explicit with_font() paths]  # this render only
```

Auto-discovery means: after one `stellium fonts download zh`, every Chinese chart renders
correctly with no code change — exactly as a downloaded ephemeris "just works". The SVG
side needs the family *name*, which comes from the manifest (or is sniffed from the file).

### 4.5 `with_font()` — the explicit override

```python
chart.draw().with_font("~/fonts/MyBrand.ttf").preset_standard().save_png("chart.png")
```

Adds one font (file or directory) to *this* render: its directory to the Typst path, its
family to the SVG text stack. For a font not in a pack, or to force a specific face.

### 4.6 The warning that names the fix

The existing `MissingGlyphWarning` fires for missing *object-glyph SVGs* (Pholus, Sedna) —
a different failure. Non-Latin **text** with no covering font needs its own detection:
before rasterizing, if the text layers contain codepoints outside the bundled fonts' cover
and no user/pack font is active, warn:

> `MissingFontWarning: this chart's text contains characters no available font covers
> (likely CJK). PNG/PDF will render them as blank boxes. Run 'stellium fonts download zh',
> or pass .with_font(path). SVG in a browser may still work via system fonts.`

Fail loud, with the exact remedy. Never silent tofu.

### 4.7 The CLI

```
stellium fonts list                 # packs, which are installed, sizes, coverage
stellium fonts download zh          # fetch + verify + install a pack (with OFL)
stellium fonts download zh-hant
stellium fonts remove zh
stellium fonts path                 # print ~/.stellium/fonts/
```

Mirrors `stellium ephemeris download`: `urllib`, a progress line, checksum verification,
idempotent (`--force` to refetch).

---

## 5. Design — Part B: Chart-wheel localization

Small, and it depends on Part A only for *rendering* — the text can localize before the
font exists (it just won't rasterize to PNG without one).

### 5.1 `ChartDrawBuilder.with_locale(code)`

Stores a locale on the builder (default `"en"`). Because the wheel renders standalone
(outside `ReportBuilder`), it can't use the report's ambient-locale trick — it threads the
locale explicitly into the render config, and the layers pull it from the renderer.

### 5.2 The layers call the catalog

`info_corners.py` and the header layer build their word strings through `term()`/`t()` and
the format patterns, keyed off the renderer's locale — the same moves as the report
sections:

- date/time → `format_date`/`format_time`
- house system → `term(f"house_system.{name}")`, zodiac → `term`/`t`
- moon phase → `term(f"phase.{name}")`
- element/modality table headers and cells → `term(f"element.{x}")`, `term(f"modality.{x}")`
- name, location, timezone → **untouched** (DNT)

English output stays byte-identical (`t()`/`term()` are identity for `en`).

---

## 6. Public API surface

```python
# Chart drawing
chart.draw().with_locale("zh_CN")          # new
chart.draw().with_font(path_or_dir)        # new

# Paths
stellium.data.paths.get_user_fonts_dir()   # new -> ~/.stellium/fonts/

# Fonts module (new): stellium.fonts
list_packs() -> dict                       # manifest + installed state
download_pack(script, *, force=False)      # fetch + verify + install
remove_pack(script)
installed_font_dirs() -> list[Path]        # for font_paths() auto-discovery
missing_font_scripts(text) -> list[str]    # for the warning

# CLI
stellium fonts list | download <s> | remove <s> | path

# Warning
stellium.exceptions.MissingFontWarning     # new, distinct from MissingGlyphWarning
```

---

## 7. Migration plan

Each phase stands alone and leaves the tree working. All on `feat/structure-first-sections`.

| Phase | Scope | Done when |
|---|---|---|
| **A1 · Paths + resolution** | `get_user_fonts_dir()`; extend `font_paths()` to append `~/.stellium/fonts/**` and explicit paths. No downloader yet — a font dropped in by hand already works. | A font manually placed in `~/.stellium/fonts/zh/` makes a zh PNG render. |
| **A2 · CLI + manifest + checksums** | `stellium.fonts` module, `fonts.json`, `stellium fonts` commands, SHA-256 verification, OFL fetch. | `stellium fonts download zh` installs and verifies a pack. |
| **A3 · Warning** | `MissingFontWarning` + `missing_font_scripts()`; fire before rasterizing. | A zh chart with no font warns with the remedy instead of silent tofu. |
| **A4 · `with_font()`** | The explicit per-render override on `ChartDrawBuilder`. | `.with_font(path)` renders a PNG with that font. |
| **B1 · `with_locale()`** | Locale on `ChartDrawBuilder`, threaded to the renderer. No layer changes yet. | Locale is stored and reaches the layers; English unchanged. |
| **B2 · Localize the layers** | `info_corners.py` + header through catalog/format. | A zh chart (SVG) shows Chinese header/table text; English byte-identical. |

A1–A4 are usable without B; B1–B2 without a font just means "correct SVG, tofu PNG until you
download the pack" — which the warning explains.

---

## 8. Open questions

- **Hosting: GitHub Release vs. separate `stellium-fonts` repo** (§4.2). Release is fewer
  moving parts; a separate repo is cleaner for jsDelivr's `@version` pinning. Leaning
  Release.
- **Which packs at launch?** `zh` (Simplified) and `zh-hant` (Traditional, for the HK/TW
  work) are the immediate need. `ja`, `ar`, `hi` on request.
- **Font choice.** Noto Sans SC/TC are the safe OFL default and match the Latin stack's
  "Noto" feel. Source Han is the alternative. Regular weight only, to start.
- **Should the ephemeris downloader retrofit checksums** once the font one proves the
  pattern? Out of scope here, worth a follow-up.

---

## 9. Testing strategy

- **Resolution (no network).** Drop a fixture font in a temp `~/.stellium/fonts/`, assert
  `font_paths()` includes it and a PNG render picks it up. This is the load-bearing test;
  everything else is plumbing around it.
- **Checksum.** A corrupted download (wrong bytes) is rejected and cleaned up; a good one
  installs. Mock the fetch — no live network in the suite.
- **Warning.** A chart whose text needs CJK, with no font active, emits `MissingFontWarning`
  naming a pack; the same chart with a font active does not.
- **English byte-identical.** The wheel's English SVG is unchanged by `with_locale("en")` —
  the same invariant the report side holds, checked the same way.
- **No live downloads in CI.** The manifest's URLs are validated for shape, not fetched.

---

## 10. Acceptance criteria

- `get_user_fonts_dir()` returns `~/.stellium/fonts/`; a font placed there is found by
  `font_paths()` and renders in a PNG with **no** `with_font()` call.
- `stellium fonts download zh` fetches, **verifies the checksum**, installs the font **and
  its OFL**, and is idempotent.
- A zh chart with no font active raises `MissingFontWarning` whose message names
  `stellium fonts download zh`; with the font active it does not, and the PNG has no tofu.
- `chart.draw().with_locale("zh_CN")` renders the header/table words in Chinese (SVG);
  the same chart in `en` is byte-identical to before this spec.
- No non-Latin font is added to the wheel; `pip show`/wheel size is unchanged.
