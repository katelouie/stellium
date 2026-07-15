# zh_Hant_TW / zh_Hant_HK translation notes

Two locale files, built from two rounds of sourced research. Both sit at
**696/717 keys (97.1%)**. The 21 gaps are deliberate: they are keys with no
attested traditional-Chinese astrological usage, and they fall back to English
rather than shipping an invented term that looks authoritative.

## Why two files and not one zh_Hant

13 keys genuinely diverge. That is a small number, but the divergences are not
cosmetic and would be silently wrong in a merged file:

| Key | TW | HK |
|---|---|---|
| `sign.Aries` | 牡羊座 | 白羊座 |
| `message.Aries` | 牡羊座 | 白羊座 |
| `body.Aries Point` | 牡羊點 | 白羊點 |
| `star.Altair` | 牛郎星 | 河鼓二 |
| `star.Vega` | 織女星 | 織女一 |
| `phase.Waxing Crescent` | 眉月 | 蛾眉月 |
| `time_unit.week` / `weeks` | 週 | 星期 |
| `house_system.Regiomontanus` | 芮吉歐蒙塔那制 | 芮氏制 |
| `house_system.Campanus` | 坎帕納斯制 | 坎氏制 |
| `house_system.Morinus` | 莫里努斯制 | 莫氏制 |
| `message.Planet Positions` | 行星位置 | 星體位置 |
| `message.Generated with Stellium` | 由 Stellium 產生 | 由 Stellium 生成 |

The star split is the most defensible: HK's authority is the 香港太空館
亮星中英對照表, which uses the indigenous 星官 names (河鼓二, 織女一). Taiwanese
astrological writing prefers the folk forms (牛郎星, 織女星). Both are understood
in both places, so this is a *source-authority* split more than a
comprehension split — but it maps cleanly and is worth keeping.

The house-system split is a style convention: TW spells eponymous systems out,
HK abbreviates to 一字 + 氏制.

**Do not generate either file by OpenCC-converting the mainland `zh-CN` file.**
Several of these are word choices, not glyph choices, and character conversion
erases them.

## Deliberate gaps (fall back to English)

| Group | Keys | Why |
|---|---|---|
| `aspect` | Binovile, Quadnovile, Biseptile, Triseptile | Proposed calques only. The base terms (九分相/七分相) are themselves only weakly attested; the compounds are not attested at all. |
| `condition` | Halb, Hayz, Feral, Culminating | Arabic-derived traditional conditions with no settled TW/HK rendering found. |
| `pattern` | Cradle, Hourglass, Rectangle, Thor's Hammer, Wedge | Minor Jones/aspect patterns; no attested Chinese names. |
| `message` | Almuten, Almuten Figuris, Almuten of the Chart, Decile, + 4 | Almuten has no settled Chinese term; Decile is unattested. |

## Bodies carrying English + parenthetical transliteration

These are in the files with values like `"Sappho": "Sappho（莎孚）"`. The
parenthetical is a **good-faith Mandarin transliteration, not attested usage** —
it is there so a reader gets a pronunciation handle, not so the term looks
official. Flagged for native review:

- Minor asteroids: Sappho, Amor, Icarus, Metis, Diana, Urania, Fortuna, Bacchus, Pandora
- Centaurs: Asbolus, Hylonome, Elatus, Bienor, Okyrhoe, Echeclus
- Other: Altjira, Hidalgo, Toro

(Pholus 人龍星, Nessus 毒龍星, Chariklo 查理洛 are weakly attested and shipped as
real values, not parentheticals.)

## Confidence tiers

**High — ship as-is.** Signs, core aspects, aspect motion, modality, elements,
motion, sect, dignities, moon phases, core planets/points, the four asteroid
goddesses + Chiron, dwarf planets/TNOs (harmonized cross-strait by the
天文學名詞審定委員會, Yangzhou 2007-06-16), fixed stars, chart types, conditions,
house topics, directions, time units, polarity, months, weekdays, wuxing, stems,
branches, zodiac animals, and the bulk of the message tier.

**Medium — sound, but worth a reviewer's eye.** Uranian/Hamburg hypotheticals
(漢堡學派虛星 — software and practitioner blogs only), the centaur trio, minor
aspects, Ayanamsa, Nakshatra/Pada.

**Low — proposed, review before release.** Hemisphere Emphasis, Transit
Timeline, Cross-Chart Aspects, Aspectarian, Core Midpoints, Hard Aspects to
Midpoints, Planets Conjunct Midpoints, Illumination, and every parenthetical
transliteration above.

## Decisions baked in

- **Elements vs. wuxing.** Western Air is 風象, using the compound `元素+象` form
  throughout, so `element` never collides with `wuxing`.
- **Tropical/Sidereal** are 回歸黃道 / 恆星黃道. Not 熱帶黃道 — that calque appears
  only in bilingual dictionary glosses, never in native astrology writing.
- **Stellium stays Latin.** The mainland file rendered it 群星, which collides
  with `pattern.Stellium` = 星群 (the same two characters, reversed) and erases
  the brand. Chinese software convention leaves product names in Latin.
- **Dates are Gregorian.** TW uses 西元, not 民國 — every TW astrology tool
  surveyed collects and prints Gregorian years. HK uses 公曆.
- **`format.date` uses `{month_num}`, not `{month}`.** Chinese wants
  2026年7月14日, not 2026年七月14日. The README sanctions this choice explicitly.
  Same call the donated mainland file made.
- **12-hour clock, ampm first.** `{ampm}{hour12}:{minute}` → 上午9:30. Chinese
  puts the marker before the time. Never 午前/午後 (Japanese).
- **Degrees use symbols**, `{deg}°{min:02d}′`, matching both chart software and
  HKO's own 東經114°10'27.6'' style.
- **Hemisphere words lead**: `{hemisphere}{value}°` → 北緯22°18'. Not N/S/E/W.
- **Houses use Arabic numerals**: 第1宮…第12宮, matching live generator output.
  Not 第一宮.
- **`time_unit` singular == plural.** Chinese does not inflect for number.

## Open question for a specialist

`nakshatra.Shravana` is set to **女宿**, following the 27-mansion 宿曜 count
(which drops 牛宿 from the 28). If you are matching by determinative star
instead, it should be **牛宿**. This wants a 宿曜/Vedic specialist, not a
generalist — flagging rather than quietly picking.

## Known soft spots

- HK chart-table headers (行星位置/星體位置/相位表) are **not natively attested**.
  HK astrologer sites outsource chart generation to Taiwan's 占星之門, so these
  are TW conventions applied to HK. A native HK reviewer should confirm.
- House-system short forms: only 普 / 整 / 柯 / 等 are attested (from mainland
  software). The other 13 follow the same single-character convention but are
  my construction. They are the weakest tier in the catalog.
- HK numeric dates are conventionally DD/MM/YYYY, but `format.date` here uses
  the Chinese prose 年月日 order, which is identical to TW. If you add a
  numeric/short date format later, that is where HK and TW must split.

## Rebuilding

`build.py` regenerates both files from `_TEMPLATE.json`. If the registry grows
and the template is regenerated, re-run it — new keys will simply be absent from
both locales (falling back to English) until values are added to the script.
