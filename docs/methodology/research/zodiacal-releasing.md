> **Preserved research report.** This is the source-verification investigation
> behind Stellium's implementation of this technique, kept verbatim as
> provenance. For the curated summary of *what Stellium actually implements*
> (defaults, chosen forks, simplifications) and how these sources map to the
> code, see [../README.md](../README.md).

---

# Zodiacal Releasing (ZR): A Fully-Parameterized Implementation & Documentation Supplement

## TL;DR
- **Zodiacal Releasing derives entirely from one source — Vettius Valens' *Anthology*, Book IV (Ch. 4–10 in Riley's numbering) — and every "standard" convention traces to how Robert Schmidt (Project Hindsight, 1990s) and Chris Brennan (2005–present) reconstructed and popularized it; the modern default is: release from the Lot of Spirit for career and Lot of Fortune for body, using whole-sign tropical signs, 360-day years, and the loosing-of-the-bond jump to the opposite sign after a full 12-sign subperiod circuit.**
- **The genuinely contested implementation forks are: (a) whether to reverse the Fortune/Spirit formula by sect (Valens/Schmidt/Brennan say YES; Ptolemy/Lilly say NO); (b) 360-day "ideal" year vs 365.25-day year for converting periods to dates (Valens/Brennan use 360; a minority use 365.25); (c) Capricorn = 27 vs 30 years; and (d) whether the loosing of the bond triggers on "12 subperiods completed" jumping opposite the parent sign.**
- **A robust implementation should expose 16 toggles and ship four presets — "Brennan/Modern Standard" (the recommended out-of-the-box default), "Valens Purist," "Schmidt/Project Hindsight," and "Fractal/Experimental" — with the Brennan preset as default because it is the most tested, most documented, and matches the free calculators (Astro-Seek, zodiacalreleasing.net) most users will cross-check against.**

## Key Findings

### The single source and its two translations
ZR survives only in **Vettius Valens, *Anthology*, Book IV** (2nd c. CE, Alexandria). Valens gives the technique no name; he describes it as a "releasing" (Greek *aphesis*) that proceeds zodiacally. It appears in Book IV chapters titled (Riley numbering): Ch. 1 "The Divisions of Periods," Ch. 2 "Concerning Releasing," Ch. 4 "Concerning the Division of the Times from the Lot of Fortune and Spirit," Ch. 5 "Concerning the Loosing of the Bond and the Reciprocal Handing Over of the Stars," Ch. 6 "How Many Years Each Zoidion Divides." Brennan cites the core as **Anthology Book 4, chapters 4–10**. (Note: older editions/Schmidt number this as Book V in some references; Riley's is Book IV.)

Two English translations exist and diverge in terminology:
- **Robert Schmidt / Project Hindsight** (*The Anthology, Book IV*, trans. Schmidt, ed. Robert Hand, Golden Hind Press, ©1996, Greek Track Vol. XI). Schmidt **coined the English name "Zodiacal Releasing"** and the term "loosing of the bond." He uses Greek planet names (Kronos, Zeus, Ares, Aphrodite, Hermes), retains "zoidion" for sign, "Lot" (Greek *klēros*), and calls the solar lot "**Spirit**." He renders the handover as "**Reciprocal Handing Over**" / "Giving Over" (Greek *parodosis kai paralepsis*). He translates *chrematistikos* as "**busy**" or "**speaking**."
- **Mark Riley** (free PDF, "Vettius Valens entire.pdf," CSU Sacramento; also published in print, ed. Brennan, 2022). Riley uses English planet/sign names and frequently transliterates the solar lot as "**Daimon**" — e.g., Riley's verbatim: *"I will now append this truly powerful method: to begin the vital sector with the Lot of Fortune and with Daimon (which signify the moon and the sun)."* Both translations title Book IV Ch. 5 and Ch. 6 identically.

Only one or two other ancient sources mention it: **Rhetorius** (6th c.) references it because he read Valens. **Hephaistio of Thebes** (*Apotelesmatika*, c. 415 CE) preserves parallel time-lord material (decennials etc.) but is chiefly a compiler of Ptolemy and Dorotheus; his relevance to ZR proper is limited. Valens attributes the origin of the technique to an earlier astrologer writing under the name **"Abraham"** (a text on lots). Modern popularization: **Schmidt** (translation + reconstruction), **Chris Brennan** (*Hellenistic Astrology: The Study of Fate and Fortune*, 2017, Ch. 18; Astrology Podcast ep. 192, 2019; 18-hour course), **Leisa Schaim**, **Patrick Watson**, **Demetra George** (*Ancient Astrology in Theory and Practice* Vol. II, Rubedo Press, 2022 — covers ZR from Spirit), and **Curtis Manwaring** (Delphic Oracle software; also the freeware "Aphesis").

### 1. Lots / Starting Point
- **Lot of Fortune** (lunar; body, health, material circumstances, "that which befalls you") vs **Lot of Spirit / Daimon** (solar; career, action, deliberate choice, eudaimonia). Valens' own duo. **Lot of Eros** (relationships) was **Brennan's own modification** (November 2005, using Paulus Alexandrinus' calculation) — explicitly not in Valens. Brennan also experimented with **Nemesis** (Saturn lot) and **Necessity**; **Patrick Watson** published a Nemesis case study. Brennan considers releasing from lots beyond Spirit/Fortune/Eros an open research area.
- **Formulas (day):** Fortune = Asc + Moon − Sun; Spirit = Asc + Sun − Moon. **Night: reverse both** (Fortune = Asc + Sun − Moon; Spirit = Asc + Moon − Sun).
- **The reversal disagreement:** Valens, Schmidt, and Brennan **always reverse by sect**. **Ptolemy** (*Tetrabiblos* III.10/11) treats Fortune as functioning "like the horoskopos of the Moon... at all times, by day or by night" and does **not reverse** by night — used only the day formula; **William Lilly** followed Ptolemy. Wade Caves, in "Finding Fortuna: Should the Lot of Fortune calculation be reversed?" (skyscript.co.uk, Oct. 2025), argues Ptolemy's non-reversal is the original definition and that the early authors who reverse "are missing a compelling rationale as to why we are adding and subtracting longitudes between luminaries and the ascendant." The controversy predates Valens: the anonymous author of **P. Lond. 130** (81 CE; chart No. 81 in Neugebauer–van Hoesen's *Greek Horoscopes*) insists on the non-reversed Fortune and calls the reversed placement the mark of "an ignorant astrologer." **For ZR specifically, the reversal is standard** because Spirit must be the sect-reversed mirror of Fortune for the technique to work as Valens intends.
- **Default lot:** Brennan/modern practice most often starts from **Spirit for career** questions, but **Fortune is described as the more common/archetypal anchor** and is always used to define the peak-period angles regardless of which lot you release from. The four-lot system (Fortune/Spirit/Eros/Necessity) maps to body/career/love/constraint.

### 2. Period Lengths (planetary "Lesser/Minor Years")
Confirmed across all sources (planet → years → sign):
- Saturn 30 → **Aquarius 30**; **Capricorn 27** (see below)
- Jupiter 12 → Sagittarius, Pisces
- Mars 15 → Aries, Scorpio
- Sun 19 → Leo
- Venus 8 → Taurus, Libra
- Mercury 20 → Gemini, Virgo
- Moon 25 → Cancer

Sum of minor years = 129 (this is also the L1 length in the equal Decennials system). Note an OCR artifact in some scanned Schmidt text shows "Moon 23" — this is an error; the correct value is **25** (required for the 129 sum).

- **Cancer/Leo question:** Cancer gets the Moon's full 25 and Leo gets the Sun's full 19 — there is **no special reduction** for the luminaries' own signs. The only sign that deviates from its ruler's minor years is **Capricorn**.
- **The Capricorn Controversy (27 vs 30):** Saturn rules both Capricorn and Aquarius with a 30-year minor period. Aquarius gets 30, but **Capricorn is reduced to 27**. Valens' rationale (per Manwaring's summary of Book IV / "Capricorn Controversy"): Capricorn, being opposite Cancer, should get ¼ of the **greater years** of Cancer, while Aquarius, opposite Leo, gets ¼ of the greater years of Leo — producing the asymmetry. The alternative (rejected by Valens) was to use the minor years strictly, giving Capricorn 30 too. **27 is the standard/default.** A handful of tools let the user toggle Capricorn = 30.

### 3. The Four Levels and Time Scaling
- **L1 = years, L2 = months (1/12 of L1), L3 ≈ 2.5-day "weeks" (1/12 of L2), L4 ≈ 5-hour "days" (1/12 of L3).** Each level is exactly 1/12 of its parent. Brennan/Watson note L3 increment = 2.5 days, L4 = 5 hours; labeling them "weeks/days" is loose but reflects lived experience (L3 = weeks-to-a-couple-months, L4 = a handful of days).
- Worked scaling (per hand-calc guides): Cancer L1 = 25 years; L2 = 2 years 1 month; L3 = 2 months 2 days 12 hours; L4 = 5 days 4 hours 48 minutes. Mercury (20): L3 = 50 days, L4 ≈ 4 days 4 hours. Saturn/Aquarius (30): L3 = 75 days, L4 = 6 days 6 hours. Saturn/Capricorn (27): L3 = 67.5 days, L4 = 5 days 15 hours.
- **360 vs 365.25 day year — the MAJOR implementation fork.** Valens explicitly used a **360-day "ideal" year** for the distribution while noting the civil year is 365¼: *"Since the universal year has 365 1/4 days, while the year with respect to the distribution has 360, we subtract the 5 intercalary days and the one-fourth of a day, then we find the number of years."* Brennan confirms the convention (Astrology Podcast Ep. 192, Feb. 5, 2019): *"for the purpose of calculation, the technique uses 360-day years and 30-day months... it's not using a 365-day year, it's using a 360-day year in order to divide up the entire year and in order to make the months exactly 1/12th of the year."* The compounding effect: a period nominally 25 "years" ends ~25×360/365.25 ≈ 24.64 civil years later; the drift is ~1 month per 5 years 10 months, ~1 year per ~70 years. A minority of practitioners prefer 365.25 — Aswin Subramanyan reports, verbatim: *"Earlier, I tested with the 360 day format which did not seem to match with the events of some of the charts I tested. After sometime, I switched to 365.25 day method of calculating the zodiacal releasing periods and it started working."* Software (AstroApp, Delphic Oracle) exposes the year-length as a parameter; the "most common practice is to use the 360-day conversion." **Default: 360.**

### 4. Loosing of the Bond (lusis / λύσις desmou)
- **Trigger (canonical):** After a full circuit of **12 subperiods** has been distributed within a parent period long enough to complete one (only signs with periods > ~17.5 years: Cancer 25, Leo 19, Gemini/Virgo 20, Capricorn 27, Aquarius 30 — i.e., signs of Moon, Sun, Mercury, Saturn), instead of returning to the parent sign for the 13th subperiod, **the sequence jumps to the sign OPPOSITE the parent sign** and continues from there. Riley (via Louis/Cosmoazul), verbatim: *"after twelve subperiods have been completed, instead of with the sign that served to initiate the subperiod, the releasing jumps to the opposite sign and continues from there. For example, when Cancer as a major period is subdivided, the first subperiod is Cancer and the twelfth subperiod is Gemini. The thirteenth subperiod instead of going back to Cancer is, instead, the opposite sign Capricorn."*
- **On the "signs_processed == 12" question:** The current code trigger ("12 signs processed, jump to opposite") is **essentially correct** but must be precise: the jump target is the sign **opposite the PARENT (Level-above) sign**, which equals the sign *following* the one where the 12-sign circuit ended (12th subperiod = sign before parent; opposite-of-parent = sign after that). Al Gore worked example (Brennan): Capricorn L1; L2 circuit ends on Sagittarius (12th); 13th jumps to **Cancer** (opposite Capricorn), not back to Capricorn.
- **~17.5 year timing:** Because the 12 subperiods sum to 129 months ≈ 17 years 7 months (in 360-day terms, ~17.5 years), the L2 loosing always falls ~17.5 years into any qualifying L1.
- **Does it happen at all levels?** YES — the loosing occurs on **any** level whose parent is long enough for a full sub-circuit (L2 within long L1; also L3 and L4). Brennan and Manwaring confirm L3/L4 loosings. It does **not** occur in short signs (Venus/Mars/Jupiter-ruled) because the circuit never completes.
- **Truncation of remaining subperiods:** After the loosing, the opposite sign takes over distributing the **remaining** time; each subperiod runs and hands over, and **the final subperiod is truncated at the parent boundary**. Ellen Loehr Black (co-founder of Project Hindsight), in "Zodiacal Releasing from Spirit: The Tsunami Effect in the Life of John Kerry" (projecthindsight.com), on Valens' procedure: *"Each profection breaks off when its time is over and the new profection begins immediately."* (Her worked Kerry example locates key turns at "the LOOSING OF THE BOND AT LEVEL THREE" and the "LOOSING OF THE BOND AT LEVEL ONE in Kerry's 10th House Virgo major profection.") This is truncation, not overflow — matching Delphic Oracle, Solar Fire, and Astro-Seek. See §5.
- **Three types of loosing** (Valens, per Manwaring/Delphic Oracle help): (a) **Darkness → Light** (best/propitious): Capricorn or Aquarius → Cancer or Leo; (b) **Light → Darkness** (danger/trouble): Cancer or Leo → Capricorn or Aquarius; (c) **Middling/"innovative"** (Mercury → Jupiter, many changes): Gemini → Sagittarius, Virgo → Pisces. Specific loosings: Cancer→Capricorn, Leo→Aquarius, Virgo→Pisces, Gemini→Sagittarius, Capricorn→Cancer, Aquarius→Leo.
- **Trine vs opposition disagreement:** Valens says the bond looses to the **opposite** sign; he reports that **some of his contemporaries loosed to the trine** instead, but Valens preferred the opposition on grounds of "elemental commixture" (Manwaring). **Opposition is standard.**
- **L1 (major-period) loosing / 12-major-period cycle:** After 12 *major* periods (~210 years) a major-level loosing would theoretically occur, but Manwaring notes "it is not known what happens" and no human lifespan reaches it — so it is irrelevant for natal work (relevant only to mundane/long-run charts). Total of all L1 minor years (208–210 depending on Capricorn 27/30) approximates this.
- **Foreshadowing:** Brennan's observation — the loosing sign is activated ~8 years earlier (its first pass in the circuit) as a "preview"/rehearsal; the person often "almost does something but doesn't follow through," then follows through at the actual loosing.

### 5. Sub-period Overflow / Truncation vs Continuation
- **Truncation is standard.** When L2/L3/L4 subperiods don't evenly fill the parent, the **last subperiod is cut off at the parent boundary**; the parent then advances and subperiods **restart from the parent's own sign** (Brennan: "whatever level one you're starting out with, the first level two within that level one will always be the same sign"). Valens/Black: "Each profection breaks off when its time is over." No overflow past the parent boundary. This is the near-universal software behavior.
- **Sub-periods restart from the parent sign** (not a fixed point), then proceed in zodiacal order, subject to the loosing-of-the-bond jump if the circuit completes.

### 6. Where Periods Start
- **L1 begins from the sign of the Lot** you're releasing from. **Each sub-level begins from the sign of its immediate parent period** (confirmed Brennan, Kerykeion, Celesian).
- **Same-sign rule (Fortune & Spirit in same sign):** Valens' special rule — if Spirit and Fortune occupy the **same sign**, move **Spirit forward one sign** and release Spirit from there; leave Fortune in place. Manwaring's gloss: we rely on the mother's sustenance (Fortune) at birth but don't develop reputation until later (maturation = next sign). This happens near New/Full Moon births. **Eros is NOT moved** if it coincides with Fortune/Spirit (Brennan). Some calculators don't auto-apply this — a known "gotcha."

### 7. Peak / Angular Periods and Interpretive Conventions
- **Peak periods = signs angular to the Lot of FORTUNE** (1st/4th/7th/10th from Fortune), regardless of which lot you release from — Fortune is the archetypal anchor. When releasing from Spirit and the sequence reaches a Fortune-angle, it's a **peak period of "heightened importance and activity"** (not necessarily positive).
- **Peak rank:** 1st and 10th from Fortune = **major peaks**; 7th = moderate; 4th = minor (traditional order of angles). Valens specifically flags Spirit reaching the **10th from Fortune** as a time of eminence/leadership. Brennan's George W. Bush example, verbatim ("Annual Profections, Lots, and Zodiacal Releasing," astro.com / *The Mountain Astrologer*): *"With his Lot of Fortune in Scorpio, he reached his peak period when the releasing from Spirit reached Leo, the 10th sign from Fortune, beginning in 1998, shortly before he first ran for president."*
- **Angular triad** (Schmidt's term): each peak sits in a 3-sign sequence — the cadent sign *before* (build-up/preparatory), the angle itself (peak), the succedent sign *after* (carry-forward/completion). Cadent-from-Lot signs (3/6/9/12) = quieter; succedent (2/5/8/11) = stabilizing.
- **Quality of a period** judged by three factors: (1) natal planets *in* the activated sign (esp. benefics/malefics); (2) planets *aspecting* it by square/opposition; (3) condition of the sign's ruler. **Valens' text initially emphasizes the ruler, but his examples emphasize planets in/aspecting the sign; Brennan follows the latter.** **Sect is essential**: day chart → Jupiter most positive, Mars most difficult; night chart → Venus most positive, Saturn most difficult. Aversion (2/6/8/12, inconjunct) between major and sub-period signs = difficulty/inability to "see" each other. *Chrematistikos* ("busy/speaking") periods say more; cadent periods may be "mute" unless a malefic is involved (Valens: malefics more potent than benefics).
- **Fortune vs Spirit domains:** Fortune for health/body/accidents (Brennan/Schaim note it's more hit-or-miss and best for charts already predisposed to health issues; also legal-liability caution); Spirit for career/action; Eros for relationships.

### 8. Fractal vs Valens methods
- The **"Valens" method** (loosing of the bond + truncation) is the authentic, universally-used approach. A **pure "fractal" recursive subdivision** (each parent simply subdivides into 12 proportional children in fixed zodiacal order from the parent sign, **without** the loosing jump) is **NOT a recognized traditional method** and **no named practitioner uses it**. It is a simplification/computational convenience. Some casual descriptions loosely call the nesting "fractal," but every serious source (Valens, Schmidt, Brennan, George, Manwaring) includes the loosing of the bond. **Recommendation: expose "fractal" only as an explicitly-labeled experimental/non-canonical mode.**

### 9. Other Gotchas
- **Tropical zodiac, whole-sign only.** ZR is **tropical** (no ayanamsha/precession) in the Brennan/Schmidt standard. (Aswin Subramanyan idiosyncratically used sidereal in one worked example, but this is non-standard.) Whole-sign houses/aspects throughout; the Lot's *degree* is used only to fix the sign, then the whole sign carries the topic.
- **Birth-time sensitivity:** Because lots depend on the Asc, small time errors can shift a lot across a sign boundary and throw L1 periods off by up to ~30 years; ZR doubles as a rectification tool.
- **Edge cases at L4:** increments of ~5 hours make L4 highly time-sensitive; most practitioners stop at L2 (L3 for precision, L4 research-only).
- **Very long lifespans / total sum:** L1 minor-years sum ≈ 208–210; the 12-major-period loosing (~210 yrs) never occurs in a lifetime.
- **Leap-year handling** when converting 360-day periods to civil dates requires care (subtract accumulated leap days), a common source of small date discrepancies between calculators.

## Details: Documentation citations for each decision point
- **Name/aphesis translation:** Schmidt, intro to Valens Book I/IV (1996); Brennan ep. 192 transcript (defends "releasing" over transliteration "aphesis"; notes other academics rendered *aphesis* as "starter/starting point").
- **360-day year:** Valens Book IV Ch. 9 ("Concerning the Cosmic Year and the Year Relative to Division"); quoted via Seven Stars Astrology. Brennan ep. 192 (Feb. 5, 2019).
- **Loosing trigger & opposite-sign jump:** Valens Book IV Ch. 5 (Riley/Schmidt); Riley text via Louis/Cosmoazul; Brennan astro.com/TMA (Apr/May 2012 article, "Annual Profections, Lots, and Zodiacal Releasing"); Manwaring Delphic Oracle help.
- **Capricorn 27:** Valens Book IV Ch. 6; Manwaring "Capricorn Controversy."
- **Same-sign Spirit rule:** Valens Book IV; Manwaring "Fortune/Spirit in same Sign"; Brennan ep. 192.
- **Peak/10th-from-Fortune:** Valens Book IV Ch. 7; Manwaring x-files; Brennan ep. 192.
- **Truncation:** Ellen Loehr Black, Project Hindsight, "Zodiacal Releasing from Spirit: The Tsunami Effect in the Life of John Kerry."
- **Three types of loosing:** Manwaring, Delphic Oracle "Loosing the Bond" help; Cosmoazul/Riley.

## Recommendations

### (a) Parameters/toggles a robust implementation should expose (16 total)
1. `lot` — which lot to release from: Fortune | Spirit | Eros | Necessity | custom-degree. (default Spirit for career module; Fortune for health module)
2. `sect_reversal` — reverse Fortune/Spirit formula by night: True | False. (default True)
3. `eros_formula` — Paulus/Brennan | Astrodienst-variant. (default Paulus/Brennan)
4. `capricorn_years` — 27 | 30. (default 27)
5. `year_length_days` — 360 | 365.25 | 365.2422. (default 360)
6. `month_definition` — 1/12-of-year (30 ideal days) | civil. (default 1/12 ideal)
7. `levels` — max depth 1–4. (default 4, display 2)
8. `loosing_of_bond` — enabled | disabled. (default enabled)
9. `loosing_target` — opposite | trine. (default opposite)
10. `loosing_trigger` — "12 subperiods completed" (canonical). (fixed)
11. `subperiod_boundary` — truncate | overflow. (default truncate)
12. `same_sign_spirit_rule` — apply +1 sign to Spirit if coincident with Fortune. (default True; never for Eros)
13. `peak_anchor_lot` — always Fortune | same-as-release. (default Fortune)
14. `zodiac` — tropical | sidereal(+ayanamsha). (default tropical)
15. `sect_light_edge_rule` — handling Sun exactly on horizon (modified day/night). (default: below-horizon = night)
16. `leap_day_handling` — accumulate/subtract leap days in civil conversion. (default on)

### (b) Preset modes
- **"Brennan / Modern Standard" (DEFAULT):** sect_reversal=True, capricorn=27, year=360, loosing=enabled/opposite/12-subperiod, boundary=truncate, same_sign_rule=True, peak_anchor=Fortune, zodiac=tropical, lots=Fortune/Spirit/Eros. *Why:* most tested, matches Astro-Seek & zodiacalreleasing.net & Solar Fire; the configuration in Brennan's book and ep. 192.
- **"Valens Purist":** identical mechanics (reversal, 360, Cap 27, opposite, truncate, same-sign rule) but **lots limited to Fortune & Spirit only** (no Eros), ruler-of-sign weighted equally with in-sign planets for interpretation, no modern peak-rank overlay. *Why:* strict to Book IV.
- **"Schmidt / Project Hindsight":** as Valens Purist + Schmidt terminology (Spirit not Daimon, "Reciprocal Handing Over," *chrematistikos*="busy/speaking"), angular-triad interpretive framing emphasized, Greek planet names optional. *Why:* reflects the reconstruction lineage.
- **"Fractal / Experimental":** loosing_of_bond=disabled (pure recursive 1/12 subdivision from parent sign), optionally year=365.25. **Clearly labeled non-canonical.** *Why:* for comparison/experimentation only; no traditional authority.

### (c) Out-of-the-box default
Ship **"Brennan / Modern Standard"** as default: sect-reversed lots, Spirit for career / Fortune for body + peaks-from-Fortune, 360-day year, Capricorn 27, loosing-of-the-bond enabled (opposite-sign jump on 12-subperiod completion), truncation at parent boundaries, same-sign Spirit rule applied, tropical whole-sign. **Justification:** it is the most extensively tested and documented configuration, it is what every free public calculator and the major paid software (Solar Fire, Delphic Oracle) produce, so users cross-checking results will match; and it is faithful to Valens on every mechanical point while incorporating only the well-validated modern addition (Eros) as an optional extra.

### Thresholds that would change the recommendation
- If you require civil-date precision validated against a large event database and testing shows 365.25 aligns better, switch `year_length_days` to 365.25 (some practitioners already report this).
- If building for a strictly scholarly/reconstruction audience, default to "Valens Purist" (drop Eros).
- If a future consensus emerges that Capricorn=30 (strict minor years) performs better, expose it prominently rather than as an edge toggle.

## Caveats
- ZR rests on a **single ancient source** (Valens Book IV); much interpretive practice is 21st-century reconstruction by Schmidt and Brennan, who themselves stress that parts remain incompletely understood.
- The exact verbatim Riley Book IV wording for the loosing trigger and truncation could not be lifted directly from the primary PDF in this research (the fetch truncated to Book I); the quotes used come from Riley-via-secondary-citation (Louis/Cosmoazul), Schmidt/Ellen Black, and Brennan. Verify against Riley PDF pp. ~71–82 before publishing the documentation supplement.
- The 360 vs 365.25 fork is genuinely unsettled in practice; treat as a first-class user choice, not a hidden constant.
- The Lot-of-Fortune reversal debate is live (Wade Caves, Oct. 2025), but for ZR specifically the sect-reversed convention is near-universal.
- "Fractal" pure subdivision has no traditional authority; do not present it as equivalent to the Valens method.
- Interpretive claims (peak = eminence, loosing = major transition) are correlational observations from practitioners, not deterministic guarantees; the technique shows tone/intensity, not specific events.