# zh-CN translation notes

Audited and expanded from the donation by Zhanran Astrology / 湛然星座.
**579/717 template keys (80.8%)**, plus the 80-key `legacy` group preserved.

The 138 gaps are deliberate. Only HIGH-confidence, mainland-attested terms were
added; everything else falls back to English rather than shipping a plausible
guess.

## The policy I applied

Auditing a native speaker's donation needs a line, so:

- **REPLACE** — confirmed machine-translation calques and concept errors. 16 values.
- **PRESERVE** — the donor's stylistic choices, even where a more common form
  exists. Flagged below, not overwritten.
- **ADD** — HIGH confidence only.
- **OMIT** — everything else.

The suspicion that prompted this was correct, and the diagnosis was exact:
`热带黄道` is what you get when a machine translates "tropical" without knowing
the domain. It is dictionary-correct and astrologically wrong. Four more of the
same kind turned up.

## 1. Confirmed calques (replaced)

| Key | Was | Now | Why |
|---|---|---|---|
| `message.Tropical` | 热带黄道 | **回归黄道** | 热带 is climate-tropical. Native astrology writing uses 回归黄道 universally. 热带黄道 appears mainly in bilingual dictionary glosses. |
| `message.Essential Dignities` | 必要尊贵 | **必然尊贵** | "Essential" rendered as 必要 "necessary/required". The established term is 必然尊贵, paired with 必然无力 for debility. |
| `message.Apparent Magnitude` | 视星光度 | **视星等** | 视星光度 is not a real term. 视星等 is the standard astronomical one (symbol m). |
| `message.Harmonic Aspects` | 和弦相位 | **泛音相位** | 和弦 is a musical *chord*. Harmonic in the overtone sense is 泛音. |
| `message.Cross-Chart Aspects (Harmonic)` | 跨盘和弦相位 | **跨盘泛音相位** | Same calque. |

## 2. Concept and register errors (replaced)

| Key | Was | Now | Why |
|---|---|---|---|
| `house_system.Topocentric` | 地心制 | **锥心制** | The real error of the set. 地心 means **geocentric** — a different concept entirely. Topocentric is observer-on-the-surface. The attested mainland astrology term is 锥心（分宫）制. Note: 站心制 is the *astronomy* term and is not used in astrology. |
| `house_system.Topocentric.short` | 站 | **锥** | Follows the corrected long form. |
| `modality.Cardinal/Fixed/Mutable` | 基本宫/固定宫/变动宫 | **基本/固定/变动** | 宫 means *house*. Modality qualifies **signs**, not houses. The suffix is a category error and would read wrong in a modality column. |
| `message.Planets` | 涉及行星 | **行星** | 涉及行星 means "involved planets" — correct for an aspect-pattern member list, wrong as a generic column header. |
| `body.Mean Apogee` | 黑月莉莉斯 | **黑月莉莉丝** | Character. Standard transliteration is 莉莉丝 (丝), not 斯. |
| `phase.Waxing Crescent` | 娥眉月 | **蛾眉月** | Character. Mainland astronomy/geography standard uses 蛾 (moth radical). |
| `body.Eris` | 厄里斯 | **阋神星** | 天文学名词审定委员会 settled 阋神星 by vote at the Yangzhou meeting, 2007-06-16. 厄里斯 is a minority transliteration. |
| `message.Generated with Stellium` | 由 群星 生成 | **由 Stellium 生成** | See the note below — this is a taste call, not a donor error. |

### On 群星 → Stellium (the brand name)

The donor was not wrong here, and an earlier draft of these notes misstated why
this changed. Correcting the record:

**群星 is not the name of the Stellium aspect pattern.** That term is **星群**,
confirmed identically in mainland (知乎, 豆瓣: 「也就是星群格局」) and Taiwanese
(vocus.cc: 「星群 Stelliums」) sources. 群星 appears essentially only inside
compounds — 群星汇聚, 群星云集 — where a verb carries the phrase. The grammar
explains it: 星群 is 星+群 (noun-noun, "star-cluster"), a countable thing you can
have one of; 群星 is 群+星 ("a multitude of stars"), a quantified mass that wants
a verb. A table label needs the countable noun.

So the donor's 群星 for the *product* was a separate, defensible choice — it
carries the 群星璀璨 "galaxy of stars" connotation, which is warmer and more
evocative than the clinical 星群. It was taste, not error.

The change to Latin rests on narrower grounds:
1. The package name is Latin and immutable (`pip install stellium`); docs,
   imports, repo and stelliumastro.app all say Stellium. A Chinese name living in
   one locale string and nowhere else is orphaned.
2. 星群 (pattern table) and 群星 (footer) in the same report is a reversal pair —
   not a collision, but the kind Chinese readers parse twice (蜂蜜/蜜蜂,
   故事/事故) for no benefit.
3. Dev-tool register: Python, pandas, Django all stay Latin in Chinese writing.

If a Chinese brand name for the *webapp* is ever wanted, 群星 is the right
instinct and the donor's ear is better than mine. It just needs to be a
deliberate, site-wide brand decision rather than one string.

**Footnote:** a third form exists. Formal glossaries list Stellium as
**众星云集** (「Stellium（Satellitium）眾星雲集〔相位組〕」; mainland sources echo
「这在占星专用词汇上叫"众星云集"」). Idiom-flavored and four characters, so wrong
for a narrow table cell, but worth a parenthetical if prose docs ever discuss the
pattern.

### One judgment call you should review

`message.Chart Ruler`: 星盘主星 → **命主星**.

This one is not an error, and I want to be explicit that I overrode a native
speaker on a term they may have chosen deliberately. My reasoning: 命主星 (lord
of the Ascendant) is the HIGH-confidence standard, and 星盘主星 risks being read
as **盘主星**, which means the *strongest planet in the chart* — Almuten
Figuris. That is a genuinely different concept, and your template exposes it
separately (`message.Almuten of the Chart`). Two adjacent labels that could both
be parsed as "the chart's ruling planet" is a real collision in an app that
computes both. If the donor had a reason for 星盘主星, revert it.

## 3. Preserved (donor's call, flagged not overwritten)

These are all intelligible and defensible. A more common mainland form exists
for each, listed for the donor's consideration:

| Key | Donor's | More common | Note |
|---|---|---|---|
| `message.Cusp` | 宫尖 | 宫头 | 宫头 dominates; 宫始点 also seen. Not wrong. |
| `message.House Cusp/Cusps` | 宫位分界 | 宫头 | Descriptive but clear. |
| `aspect.Parallel` / `Contraparallel` | 合纬 / 对纬 | 平行 / 逆平行 | **Could not confirm 合纬/对纬 in native prose.** Possibly a deliberate compact coinage. Not a calque. Worth asking. |
| `message.Bi-Quintile` | 双五分相 | 倍五分相 | 倍五分相 is the attested form. |
| `aspect.Semisextile` | 半六分相 | 十二分相 / 半六合 | Donor's form reused in the catalog for consistency. |
| `message.Illumination` | 照明度 | 照亮比例 | 照明度 reads as engineering "illuminance". Register, not error. |
| `message.Eclipses` | 食相 | 日月食 | Both used. |
| `message.Sign Ingresses` | 星座换座 | 星座进入 | Both intelligible. |
| `message.Ayanamsa` | 阿亚南萨 | 岁差校正值 | Transliteration fine in 印占 context. |
| `house_system.Axial Rotation` | 轴向旋转制 | — | Rare system, no attested standard found. Cannot confirm or refute. |
| `sect.Day/Night` | 日 / 夜 | 昼 / 夜 | **Kept deliberately** — `"{sect} Chart"` composes to 日间盘/夜间盘, which is correct. 昼 would produce 昼间盘, which is wrong. |
| `message.Aspectarian` | 相位网格 | — | No settled mainland term. Reasonable coinage. |
| `message.Quality` | 性质 | 模式 | If this slot means modality, 模式 is tighter. |

## 4. Deliberate omissions (English fallback)

**`nakshatra` — entire group omitted (0/27).** This is the significant one.
Mainland usage is genuinely split: the 宿曜 tradition supplies indigenous mansion
names (娄宿, 胃宿, 昴宿…), but mainland 印度占星 writing predominantly uses
Sanskrit transliterations (阿斯维尼, 婆罗尼…). No single form dominates, and I
could not verify a transliteration set. Note this diverges from the zh_Hant_TW
and zh_Hant_HK files, where the 宿曜 mansion names *are* the attested choice —
that asymmetry is real, not an oversight. Reviewer decision, not a gap to fill
by analogy.

**`body` — 31 omitted.** Amor, Asbolus, Bacchus, Bienor, Chaos, Deucalion,
Diana, Echeclus, Elatus, Hidalgo, Hylonome, Icarus, Logos, Nessus, Okyrhoe,
Pandora, Sappho, Toro, Typhon, Altjira, Aries Point, True Apogee — no attested
mainland astrology usage. Plus specifically:
- **Metis** — the astronomy name 忑神星 collides with 智神星 usage. Left English.
- **Salacia** — 蟹神星/漾神星 unstable.
- **Fortuna** — 幸运星/命神星, two competing forms.
- **Astraea** — mainland sources give 司理星, but my zh_Hant research gave 司法星.
  Unresolved discrepancy, so omitted from zh-CN rather than guessed.
- **Varuna, Pholus, Chariklo** — MED only.

**`aspect` — 4 omitted.** Binovile, Biseptile, Triseptile, Quadnovile. Systematic
calques exist (倍九分相 etc.) but attestation is MED-to-LOW.

**`condition` — 5 omitted.** Halb (no mainland term at all), Hayz, In Sect, Out
of Sect, Free of the Sun. All MED.

**`pattern` — 3 omitted.** Wedge, Thor's Hammer, Hourglass. MED.

**`chart_type` — 1 omitted.** Draconic (龙盘, MED).

**`message` — 67 omitted.** Mostly `{slot}` templates not in the donation, plus:
- **Almuten / Almuten Figuris / Almuten of the Chart** — 宫神星 vs 盘主星
  unresolved. Do *not* use the transliteration 阿慕田; it is unattested.
- **Pada** — no settled mainland term.
- **Nakshatra** — see above.

Terms to avoid if anyone proposes them later: **阿慕田** (Almuten), **菲尔达**
(Firdaria — use 法达), **哈伊兹** (Hayz). All unattested transliterations.

## 5. Additions worth noting

**Dignities (8/8, HIGH).** 入庙 / 擢升 / 失势 / 落陷 / 三分性 / 界 / 外观 / 游走.
The Detriment=失势 vs Fall=落陷 split is mainland-standard, though the bare
characters 陷/弱 get swapped casually in practice.

**Fixed stars (26/26, HIGH).** Indigenous 星官 names throughout — 天狼星, 轩辕十四,
心宿二, 毕宿五, 角宿一, 北落师门, 大陵五. Mainland astrological writing uses these,
not transliterations. Where a folk name competes I took the source's primary:
Altair 河鼓二 (folk 牛郎星), Vega 织女星 (astronomical 织女一), Polaris 勾陈一
(folk 北极星). If you'd rather lead with the folk names for recognizability, those
three are the ones to flip.

**Uranian planets (8/8).** 丘比特, 哈迪斯, 宙斯, 克洛诺斯, 阿波罗, 阿德门图斯,
弗卡奴斯, 波塞东 — from 爱星盘's 汉堡学派虚星 list. Note **Apollo** (asteroid
1862) = 阿波罗神星 is deliberately distinct from **Apollon** (Uranian) = 阿波罗.

**`house_topic` (12/12).** The English source strings are modern descriptors
("Self & Identity", "Money & Values"), not classical palace names, so these
mirror the English: 自我与身份, 金钱与价值, 沟通与手足… The classical set
(命宫/财帛宫/兄弟宫/田宅宫/子女宫/奴仆宫/夫妻宫/疾厄宫/迁移宫/官禄宫/福德宫/玄秘宫)
is the alternative if you ever ship a 古典-oriented UI. Flagged because this is
a fork, not a lookup.

**`format`.** Added `decimal_sep` = "." and `degrees` = `{deg}°{min:02d}′`
(mainland software uses the symbol form). The donor's `{hour24}:{minute}` for
`time` is **correct** — mainland astrology software is 24-hour, so `{hour12}`
and `{ampm}` go unused. 上午/下午 are supplied as message keys for anywhere
12-hour display is needed.

## 6. Template drift (preserved, not dropped)

Two donated keys are not in `_TEMPLATE.json`:
- `format.date_short`
- `message.{ruler} ({sign} Rising)` — the template has `{ruler} (ruler of {sign})`,
  a different string.

Both are kept. If the renderer still emits them, dropping them would break output.
Worth reconciling which direction is authoritative when you next regenerate the
template.

## 7. The legacy group

Not in the template, but your pre-Phase-3 renderer looks up bare catalog terms by
English string, so dropping it would break things. Preserved at 80 keys and
**regenerated with the corrections applied** (蛾眉月, 阋神星, 锥心制, 基本/固定/变动,
黑月莉莉丝) so it cannot drift from the catalog it mirrors. It disappears on its
own at Phase 3.

## Rebuilding

`build_zh_cn.py` regenerates the file from `_TEMPLATE.json` + the donation. It
asserts the expected old value before every replacement and aborts if the
donation changes underneath it, so a re-run can't silently clobber donor edits.


## Three-locale validation pass (July 2026)

A sourced pass re-validated the terms this project added or left open, across all
three Chinese locales (mainland Simplified plus HK/TW Traditional) and two
registers (software UI vs scholarly prose). For zh-CN specifically:

### Corrections to earlier additions

| Key | Was | Now | Why |
|---|---|---|---|
| `message.Polarity` | 极性 | **阴阳** | Calque. 极性 reads as electrical/magnetic polarity. Chinese astrology owns the concept natively as 阴阳 (二分法 in scholarly prose; 阳性/阴性星座 for the values). Sourced: Zhihu, Sina, freehoro — HIGH. |
| `polarity.Balanced` | 平衡 | **均衡** | Bare 平衡 collides with the "Element Balance" section (元素平衡). 均衡 keeps the "roughly equal" sense without the section-name ambiguity. |
| `format.latitude` / `format.longitude` | `{hemisphere}{value}°` (北48.40°) | **`{hemisphere}纬{value}°` / `{hemisphere}经{value}°`** (北纬48.40° / 东经114.17°) | The compact 北48.40° is unattested and non-native: 北 as a coordinate prefix is bound to 纬 (北纬), and dropping 纬 is ungrammatical. Latitude takes 纬, longitude takes 经. Sourced: HKO. **This reverses the earlier compact-form choice.** |

### New UI terms (previously English fallback)

| Key | Value | Note |
|---|---|---|
| `message.Snapshot` | 概览 | NOT 快照 (that is the computing/filesystem sense). 星盘总览 for a more writerly tone. |
| `message.distribution & balance` | 分布与平衡 | Mainland uses 分布 (HK/TW use 分佈). |
| `message.Dominant Element` | 主导元素 | 优势元素 an accepted synonym. |
| `message.Dominant Modality` | 主导模式 | Modern/lay choice. Classical synonym **四正** (paired with element = 三方); scholarly prose also uses **性质** / 三态. |
| `message.{ruler}-ruled` | {ruler}守护 | 守护 = rulership. The chart-ruler concept itself is 命主星 (= 上升守护星). |
| `message.{count} of {total}` | {count}/{total} | Bare fraction; locale-neutral, no wordier form is standard. |
| `body.Ascendant` | 上升点 | The point — distinct from 上升星座 (the sign) and 命宫 (the first house). |
| `message.{name} (Inner Wheel)` / `(Outer Wheel)` | {name}（内圈）/（外圈） | 内盘/外盘 an accepted synonym. |
| `message.{name} Houses` | {name}的宫位 | |
| `message.Chart 1` / `Chart 2` | 星盘一 / 星盘二 | Biwheel default labels (when no chart name is given). |

### Kept Latin (project decision)

The angle abbreviations **ASC / MC / IC / DSC** stay Latin in the narrow position-table
columns — 爱星盘 translates them (上升/中天/下降/天底) but keeping Latin in tight columns
is standard and attested. If ever translated, **MC = 中天** (天顶 an accepted synonym) and
**IC = 天底**. Caveat flagged by the pass: the attested Latin abbreviation for the
descendant is **DES**, not DSC; DSC is kept here by project decision.

### Long-tail section pass (moon, declination, placements, aspect patterns, dispositors, ZR)

Tokenizing report sections that still fell back to English. Confident terms:

| Key | Value | Note |
|---|---|---|
| `message.Phase Angle` | 相位角 | Moon phase. |
| `message.Sun-Moon Separation` | 日月角距 | Angular separation Moon−Sun. |
| `message.OOB` | 出界 | Declination out-of-bounds (越界/超界 also seen). |
| `direction.North/South/East/West` | 北/南/东/西 | Full-word directions (declination column); the single letters N/S/E/W already existed. |
| `pattern.Mixed` | 混合 | Multi-element/quality aspect pattern qualifier. |
| `message.{n} planets` / `Apex: {planet}` | {n}颗行星 / 顶点：{planet} | Aspect-pattern Details column. |
| `message.Dispositors` (+ Planetary/House/Graph) | 定位星 … | 定位星 is the standard term for dispositor. |
| `message.Mutual Receptions:` / `Disposition Chains:` | 互容： / 定位链： | |
| `message.House {n}` | 第{n}宫 | |
| ZR labels (`Current State`, `Major Periods`, `L3/L4 Context`, `Active Rulers`, …) | 当前状态 / 主要时期 / L3 背景 … | |
| `message.{month} {year}` / `{month} {day}` | {year}年{month} / {month}{day}日 | Date-order overrides so partial dates read natively (1920年三月). |
| `message.{v} rad` / `{v}°/day` | {v} 弧度 / {v}°/天 | Units. |

**FLAGGED FOR EXPERT REVIEW — Hellenistic ZR jargon (conservative best-effort, low confidence):**

| Key | Value | Note |
|---|---|---|
| `message.S.Ben / C.Ben` | 宗吉 / 逆吉 | sect / contrary benefic. "sect" (of/contrary to the sect) has no settled Chinese rendering; 宗 vs 逆 is a guess. |
| `message.S.Mal / C.Mal` | 宗凶 / 逆凶 | sect / contrary malefic. |
| `message.S.Lgt / C.Lgt` | 宗光 / 逆光 | sect / contrary light (luminary). |
| `message.★ Peak (10th)` / `Angular` | ★ 巅峰（第10宫） / 角宫 | ZR period status. |
| `message.Loosing of Bond` | 松绑 | 解绑 also plausible; astrology-specific (λύσις). |

These six role codes and the ZR status markers need a Hellenistic-astrology-literate
reviewer; they were tokenized (so they *can* be fixed in the JSON) but the Chinese is
not attested. Until reviewed, treat as provisional.

### Bridge migration: midpoint pairs, fixed-star nature & constellations

Migrating sections off the legacy substring bridge (bare-name lookups) onto catalog
`term()`s — so they localize through the catalog, the pseudolocale oracle tracks them, and
they survive the eventual `legacy`-namespace removal.

| Namespace / key | Value | Note |
|---|---|---|
| `constellation.*` (new namespace, 21) | 白羊座 / 英仙座 / 室女座 … | Standard IAU Chinese names. **Distinct from signs**: Virgo the constellation is 室女座, but Virgo the *sign* is 处女座 — so constellations get their own namespace, not sign.*. |
| `message.Star / Constellation / Mag / Nature / Keywords` | 恒星 / 星座 / 星等 / 性质 / 关键词 | Fixed-stars table headers. |

Midpoint pair names (`太阳/金星`) and fixed-star planetary natures (`火星/土星`) now build from
`body.*` terms (no new data — planet names were already translated). Fixed-star **keyword**
strings remain English (free-form interpretive text, per-star; a separate translation-data
task, not a tokenization one).

### Compound dignities + fixed-star keyword plumbing

| Key | Value | Note |
|---|---|---|
| `dignity.Exaltation_Exact` | 擢升（精确） | The planet at its exact exaltation degree. English display fixed from the raw `Exaltation_Exact` to `Exaltation (exact)`. |
| `dignity.Detriment_Modern` | 失势（现代） | Detriment by modern rulership. |
| `dignity.Participating_Ruler` | 参与主星 | Participating triplicity ruler. |
| `dignity.Triplicity_Participating` | 三分性（参与） | |

(zh_Hant uses its own dignity tradition — 入旺/落陷, not 擢升/失势 — so its compound forms differ: 入旺（精確）, 落陷（現代）.)

**Fixed-star keywords — DATA-SOURCING RUN NEEDED.** The 91 interpretive keywords (independence,
cruelty, "the weeping sisters", "changing evil to good", …) are now catalog terms
(`star_keyword.*`, derived from the fixed-star registry) — tokenized and translatable, but
**not yet translated**; they still render English in zh. Worklist:
`~/Downloads/stellium-i18n-review/star_keyword_worklist.json` (91 empty values to fill).
This is a translation-*data* task, not a plumbing one.

---

## RESOLVED via research (2026-07): fixed-star keywords + ZR jargon

Two Deep Research reports came back and were integrated wholesale, superseding the
best-effort/flagged values above. Reports archived at
`~/Downloads/stellium-i18n-review/{fixed_star,zr}_research_report.md`.

### Fixed-star keywords (`star_keyword.*`, all 91)

Sourced primarily from 魯道夫《恆星占星全書》(春光/城邦, 2021, ISBN 9789865543433 — the first
Chinese fixed-star book), Robson-derived mainland glossaries (ixingpan/12sign/Douban — note
these are all Robson translations, *shared ancestry not independent corroboration*), and the
Taiwan schools (智者星象學院, SATA). Findings applied:

- **HK == TW at the word level** — divergence is Simplified↔Traditional conversion only. One
  Traditional list (`zh_Hant`) serves both HK and TW; no HK/TW overrides for keywords.
- **Three accepted collisions** (Chinese makes no distinction — do not force one): wealth =
  riches = 财富; martial honors = military honors = 军事荣誉; sickness = ill health = 疾病.
- **Register traps fixed** (dictionary-default would be wrong): activity → 活跃 (not 活动),
  negative → 凶, malevolent → 凶险, brilliance → 才华洋溢 (intellectual, not literal bright),
  gifts → 天赋, integrity → 正直, falsity → 虚假, craftiness → 狡猾, harvest → 丰收.
- **Tradition-bound epithets:** the weeping sisters → 哭泣的姊妹 (Pleiades/昴宿星團); burning →
  燃烧 (resonates with Antares = 大火 "the Great Fire" / 心宿二 in the native 星官 system);
  widowhood → 丧偶; changing evil to good → 化恶为善.
- **Native-resonance blending (documentation note):** Chinese fixed-star writing keeps the
  indigenous 星官 names and layers Robson's keywords on top, and several align strikingly —
  Algol/death ↔ 大陵 (tomb), Regulus/royalty ↔ 軒轅 (Yellow Emperor), Antares/burning ↔ 大火,
  Pleiades ↔ 昴宿. So these keywords read as continuous with the native lore, not foreign.
- **Two LOW-confidence keys, deviating from the report's TABLE toward its PROSE:**
  - `losing one's head` → **斩首** (literal only). The report's table showed 斩首／失去理智,
    but its own Section A2 + recommendations say the figurative sense is unattested and "do
    not invent a figurative rendering" — so the invented 失去理智 was dropped.
  - `pathfinding` → 探路 (LOW; a Brady-ism that collapses toward navigation).
- **Verify-before-final:** the coined phrases 化恶为善, 艺术中的不朽, 另辟蹊径 rest on
  attribution that could not be quoted online; check against 魯道夫's book. `changing evil to
  good`'s source star (Nashira/Deneb Algedi) is absent from our star list — effectively orphaned.

### Zodiacal Releasing jargon (`message.*`) — the machine values were REPLACED

The earlier 宗/逆 prefix system was **wrong and shipped-blocked**: 宗 is the religious-sect
sense of "sect"; 逆 collides with 逆行 (retrograde) and **逆光 literally means photographic
"backlight."** Replaced with the transparent 區分內 / 區分外 (in-sect / out-of-sect) family that
matches this project's existing 区分 choice for "sect" (占星之門/astrodoor + SATA standard).

| key | was (machine) | now | why |
|---|---|---|---|
| `S.Ben` / `C.Ben` | 宗吉 / 逆吉 | 区分内吉星 / 区分外吉星 | 宗/逆 wrong; 吉星 = benefic is universal |
| `S.Mal` / `C.Mal` | 宗凶 / 逆凶 | 区分内凶星 / 区分外凶星 | |
| `S.Lgt` / `C.Lgt` | 宗光 / 逆光 | 区分内发光体 / 区分外发光体 | 逆光 = "backlight"; 发光体 = luminary |
| `Loosing of Bond` | 松绑 | 联结释放 | 松绑 = "deregulate/untie" (SOE-reform register). 易简观星 uses 联结释放 |
| `★ Peak Period` / `Peak (10th)` | 巅峰… | 高峰期 / 高峰期（第10宫） | 高峰期 is the published Brennan-translation term |
| `Quality Score` | 性质评分 | 质量评分 | 性质 = "nature," not "quality" |
| `Angular` | 角宫 | 角宫 (kept) | matches this project's `condition.Angular` = 角宫; 尖轴 is the book's alt |
| `Current` | 当前 | 当前 (kept) | correct as-is |

Deviations from the report, for the record:
- **No "(LB)" suffix** on 联结释放. The report suggests appending "(LB)" for standalone prose,
  but this UI already surfaces the "LB" marker separately (period-status cell) and expands it
  in the legend ("LB = 联结释放"), so the suffix would be redundant.
- **S./C. abbreviations use full terms**, not invented compact forms (the report says no
  settled Chinese abbreviation exists and not to fabricate one). This widens the Quality
  column in Chinese ("−4 ✗（区分内凶星）"); keeping the English S.Ben/C.Mal is the report's
  sanctioned alternative if that width is a problem.
- **Book-alignment alternative** (not taken): to mirror the authoritative Brennan translation
  《希臘占星學》(商周 2023) instead of teaching-site usage, the sect family would be 區間 /
  區間光體 / 最大吉星, Loosing of Bond → 跳轉, Angular → 尖軸. We chose the 區分 family for
  consistency with the existing `sect`/角宫 vocabulary.
