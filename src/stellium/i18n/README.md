# Library localization (`stellium.i18n`)

This translates **report and chart content** — planets, signs, aspects, the report
itself. It is separate from `web/i18n/`, which translates the web app's UI chrome. The
boundary and design rationale live in
[`docs/development/specs/STRUCTURE_FIRST_SECTIONS.md`](../../../docs/development/specs/STRUCTURE_FIRST_SECTIONS.md).

## Add a language

1. Copy the template to a new locale directory:

   ```bash
   cp locales/_TEMPLATE.json locales/<code>/strings.json   # e.g. es, fr, ja, zh_Hant
   ```

2. Open `strings.json` and translate the **values** (the English source text). Set
   `metadata.language` to your code. Delete any group you don't translate — missing keys
   fall back to English, so a partial file is valid and safe to ship.

3. Check your progress:

   ```bash
   stellium i18n coverage <code>
   ```

`_TEMPLATE.json` is **generated** — regenerate it (e.g. after the object registry grows)
with `python scripts/build_i18n_template.py`. It is a file, not a locale directory, so it
never appears as a selectable language.

## The file shape

Grouped by namespace; the loader flattens to dotted keys (`body.Sun`,
`house_system.Placidus.short`, `format.date`).

| Tier | Groups | What |
|---|---|---|
| **catalog** | `body`, `sign`, `aspect`, `house_system`, `phase`, `element`, `modality`, `motion`, `aspect_motion`, `dignity`, `sect`, `star` | Core closed vocabulary. Generated from the registries. |
| **extended** | `month`, `weekday`, `pattern`, `condition`, `chart_type`, `house_topic`, `direction`, `time_unit`, `polarity`, `nakshatra`, `wuxing`, `heavenly_stem`, `earthly_branch`, `zodiac_animal` | Forward-looking astrology vocabulary (Vedic, BaZi, traditional conditions). Optional. |
| **message** | `message` | Report/UI strings looked up by English text, plus `{slot}` templates. |
| **format** | `format` | Date / time / number / degree patterns. |

Rules a translator needs:

- **Keep `{slots}` intact**, but reorder them freely — that is the whole point.
  `"House ({system})"` → `"宫位（{system}）"`.
- **`house_system.<name>.short`** is the two-or-so-character column abbreviation. Give it
  a short form that fits a narrow table cell.
- **`format.date`** exposes both `{month}` (name) and `{month_num}` (number) — use
  whichever your language wants. `format.time` on a 24-hour clock just omits `{ampm}`.
- **Proper nouns are never keys** — a person's name, a place, a timezone are passed
  through as data and are never translated.

## Fallback chain

`zh_Hant_TW` → `zh_Hant` → `zh` → `en`, so a regional locale inherits from its parent and
overrides only what differs. Declare a non-obvious parent via `metadata.fallback`.
