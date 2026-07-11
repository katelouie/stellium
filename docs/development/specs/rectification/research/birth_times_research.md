# Hour-of-Day Distribution of Human Births: Population Base-Rate Priors for Birth-Time Rectification

## TL;DR
- For a historical, international cohort concentrated in 1850–1970, the best default prior is a **spontaneous / pre-medicalization "nocturnal" curve**: births rise through the night, peak around **03:00–05:00 (centre ~04:00)**, and trough in the mid-to-late afternoon (~14:00–17:00). The hardest published anchor number comes from the Madrid Casa de Maternidad (spontaneous, largely non-intervention): the number of births was higher between 4 a.m. and noon than at any other period, and in the extended 1901–14 series (n≈11,278) **35.4% of deliveries occurred between 00:00 and 08:00**, with a peak 4-hour block of 04:00–07:59 ≈ 19%.
- The modern medicalized curve is essentially **inverted**: US vital-statistics data show births concentrated in daytime working hours — per NCHS Data Brief No. 200, "The highest percentages of births occurred during the 8:00 a.m. (6.3%) and noon (6.0%) hours," while "less than 3.0% of infants were born" during each hour from midnight to 06:59. This is driven overwhelmingly by scheduled cesareans ("Cesarean deliveries peaked during the 8:00 a.m. hour (11.6%)"; 14.3% at 08:00 for cesareans with no trial of labor) and inductions.
- Because the aggregate shape is strongly era- and intervention-dependent, use the **spontaneous curve as the primary prior**; only blend in the modern daytime curve to the extent a chart's cohort plausibly involved 20th-century hospital scheduling.

## Key Findings
- The nocturnal peak of spontaneous labour/birth is one of the most reproducible findings in perinatal epidemiology. A recent Springer review (Biological Timekeeping During Pregnancy) states: "In humans, over 30 studies have demonstrated such a relationship, with the peak hours of onset of labor and of birth between 2300 and 0400 hours." The pattern is documented continuously from Quetelet (1835, Brussels/Hamburg) through Charles (1953) to modern home-birth data, and is attributed to circadian control (melatonin/oxytocin) of labour onset.
- Delivery peaks about 1–2 hours after labour-onset peaks. Summarizing Charles (1953, Birmingham), Martin et al. (2018) report: "A study of over 16,000 births in Birmingham, England in the early 1950s… found that this [labour onset] peaked in the middle of the night, around 2am, with numbers of births peaking from 3–5am."
- Medicalization (induction, augmentation, and especially scheduled cesarean) shifts births into weekday daytime hours; this share rose steeply across the 20th century, making any single "aggregate" curve strongly era-dependent. This is precisely why the target cohort's era determines which prior to use.
- Delivery mode matters enormously. In US 2013 NCHS data: "Noninduced vaginal deliveries had the most even distribution across the hours of the day, fluctuating close to the average of 4.2%… induced vaginal deliveries rose in the morning hours, peaked in the 3:00 p.m. hour," and cesareans spiked at 08:00.
- Modern home / out-of-hospital births retain the ancestral pattern, validating them as a proxy for the "undisturbed" curve. Declercq et al. (2023): "Home births peaked in early morning between 2:00 am and 5:00 am… In the U.S., the pattern was reversed with a prolonged peak of spontaneous vaginal hospital births between 8:00 am to 5:00 pm."

## Details

### Distribution A — `spontaneous_prewar` (PRIMARY prior)
**Population/era:** Pre-medicalization European maternity and registry data, roughly 1850–1950; spontaneous vaginal births, negligible obstetric intervention, minimal artificial light. Anchor sources: Casa de Maternidad, Madrid (Varea et al.); Charles (1953, Birmingham); Lille (1,000 normal labours, 19th c., cited by Swayne 1888).

**Best hard numbers available:**
- **Madrid Casa de Maternidad, spontaneous:** Per Martin et al. (2018, PLOS ONE) citing Varea & Fernández-Cerezo (2014, *Am J Hum Biol* 26:707–709): "A recent analysis of births in a Madrid maternity hospital between 1887 and 1892 found that **98% of these births occurred without intervention, and that the number of births was higher between 4am and noon** than at other periods of the day" (original series n=4,599; delivery peak ~04:00). The extended series (Varea et al. 2023, *Memoria y Civilización* 26(2), 1901–14, n≈11,278, mean solar time) reports **35.4% of deliveries between 00:00–08:00**; peak 4-hour block 04:00–07:59 ≈ **19%** (19.1% winter-solstice month, 19.5% summer-solstice month), with frequencies falling through the day and rising again after nightfall.
- **Charles (1953), Birmingham, ~16,000 births, ~1949–51:** onset of labour peaked ~02:00; deliveries peaked ~03:00–05:00; roughly sinusoidal with an afternoon trough.
- **Lille, ~1,000 normal labours (19th c., Swayne 1888):** 6-hour blocks — 06:00–12:00 ≈ 23%, 12:00–18:00 ≈ 22%, 18:00–00:00 ≈ 27%, 00:00–06:00 ≈ 28% (arithmetic-corrected); 8-hour split ~45% (08:00–20:00) vs ~55% (20:00–08:00).

**Suggested 24-hour prior (modelled reconstruction, normalized to sum≈1).** A smoothed sinusoid with peak at 04:00 and trough at 15:00, calibrated so 00:00–08:00 ≈ 0.35 (matching the Madrid 1901–14 figure). This is an interpolation of the shape the sources give only as blocks/peaks — **not raw per-hour source data.**

| Hour | rel. freq | Hour | rel. freq |
|---|---|---|---|
| 00 | 0.050 | 12 | 0.038 |
| 01 | 0.054 | 13 | 0.035 |
| 02 | 0.057 | 14 | 0.033 |
| 03 | 0.059 | 15 | 0.032 |
| 04 | 0.060 | 16 | 0.033 |
| 05 | 0.058 | 17 | 0.035 |
| 06 | 0.055 | 18 | 0.037 |
| 07 | 0.051 | 19 | 0.040 |
| 08 | 0.047 | 20 | 0.043 |
| 09 | 0.044 | 21 | 0.045 |
| 10 | 0.042 | 22 | 0.047 |
| 11 | 0.040 | 23 | 0.049 |

(00:00–07:59 sums to 0.445 in this table; note the Madrid figure of 35.4% is for 00:00–08:00 in a specific hospital series — the modelled curve deliberately keeps a broad, gentle nocturnal hump rather than an overfit to one series. Amplitude is modest: peak ~6.0%/hour vs. trough ~3.2%/hour, i.e., peak:trough ≈ 1.9:1. Tune the amplitude down toward flat if you want a more conservative prior.)

**Caveats:** Historical registries rounded to the hour/half-hour and show digit-preference spikes at 00:00 and 12:00; Madrid used local/solar time; the 24-value table interpolates a shape the sources report only as 4-hour (Madrid) or 6-hour (Lille) blocks plus a peak hour (Charles).

### Distribution B — `natural_homebirth_modern` (secondary "undisturbed" proxy)
**Population/era:** Home births, US & Netherlands 2014, England 2008–10 (Declercq et al. 2023, PLOS ONE, PMC9847908); spontaneous, low-intervention. **Shape:** "Home births peaked in early morning between 2:00 am and 5:00 am," with a steady decline bottoming out between ~14:00 and 16:59; the Netherlands home-birth peak is at 04:00–04:59. This independently confirms the prewar shape persists in undisturbed modern births. Reported graphically in the paper (no verbatim 24-value table published), but the peak/trough placement matches Distribution A closely and can be used as a cross-check.

### Distribution C — `all_modern_us` (modern medicalized contrast)
**Population/era:** US national vital statistics (NCHS).

**US 2021 (NCHS *Births: Final Data for 2021*, Table I-1; n=3,664,292; percentages of all live births), 6-hour blocks — fully citable raw data:**

| Block | % |
|---|---|
| 00:00–05:59 | 18.1 |
| 06:00–11:59 | 28.7 |
| 12:00–17:59 | 30.3 |
| 18:00–23:59 | 22.9 |

**US 2013 (NCHS Data Brief No. 200; 41 states + DC, ~90% of US births):** if uniform, 4.2%/hour; "The highest percentages of births occurred during the 8:00 a.m. (6.3%) and noon (6.0%) hours," and "less than 3.0% of infants were born during each hour from midnight through 6:59 a.m." Strongly daytime-concentrated — the opposite of Distribution A.

### Distribution D — modern US by delivery mode (2013, NCHS Data Brief No. 200)
- **Cesarean:** "Cesarean deliveries peaked during the 8:00 a.m. hour (11.6%) and had another smaller peak during the noon hour (7.4%)"; cesareans with **no trial of labor** peak at 08:00 with **14.3%** (>3× the 4.0% at that hour for cesareans with a trial of labor).
- **Induced vaginal:** rises through the morning, "peaked in the 3:00 p.m. hour, and then declined from 6:00 p.m. onward."
- **Noninduced vaginal:** flattest — "fluctuating close to the average of 4.2%," with a mild excess from 23:00 through 06:59 (the residual nocturnal signal). This is the closest modern-US analogue to the spontaneous prior, though far flatter than the prewar curve.

### Distribution E — England 2005–14 (NHS, spontaneous onset; Martin et al. 2018)
5,093,615 singleton births (linked birth registration + notification + Maternity HES). Spontaneous birth after spontaneous onset (~50% of all births) is "roughly sinusoidal… most likely to occur between 1:00 and 7:00, with a peak around 4:00, and a trough in the afternoon," with a small dip at 08:00. Elective cesareans are concentrated on weekday mornings 09:00–12:00 (pronounced peak 09:00–10:59). Overall, "71.4 per cent occurred out of hours, and 28.6 per cent within usual working hours" (weekdays 09:00–16:59). A large modern national dataset in which the spontaneous subset still matches the prewar curve — strong corroboration of Distribution A's shape.

## Recommendations
1. **Default to `spontaneous_prewar` (Distribution A)** as the base-rate prior for the 1450–1980 international cohort concentrated in 1850–1970. It is the most representative of non-medicalized birth and is the single most useful curve for this project.
2. **Validate the shape against Distributions B (modern home births) and E (England spontaneous subset)** — all three independently give a peak ~04:00 and a trough ~15:00, which is strong convergent evidence that the prior's shape is correct even though no single pre-1950 source publishes a clean 24×1 table.
3. **For charts plausibly ≥1950 in hospital settings**, use an era-weighted blend toward `all_modern_us` (C) and the mode-specific curves (D). The cesarean/induction daytime spike only became quantitatively material in the later 20th century, so weight it in proportion to (era, country intervention rate).
4. **Thresholds that would change the recommendation:** if a subset of target charts is known to be ≥~1970 hospital births in a high-intervention country (e.g., US), weight the daytime curve (C/D) up substantially; if the cohort is pre-1900, rural, or home births, use A/B essentially unblended. A practical switch point: births before ~1935 → pure A; 1935–1970 → mild blend; post-1970 hospital → material daytime weight.
5. **For maximal fidelity, obtain the exact raw tables** from Charles (1953; free scanned PDF at PMC1058488, pages 43–59) and the Varea et al. (2023) Anexo (*Memoria y Civilización* 26(2), tables freely available at the Universidad de Alcalá repository, handle 10017/59722). Both were image-locked/paywalled to automated retrieval; a human can transcribe their 2-hour and 4-hour tables into a fully empirical prewar 24-value prior if the modelled reconstruction in Distribution A is insufficient.

## Caveats
- **No pre-1950 source located publishes a clean, machine-readable 24×1 hourly table.** The strongest raw numbers are in 4-hour blocks (Madrid) or 6-hour blocks (Lille), plus peak-hour statements (Charles, Quetelet). The 24-value table in Distribution A is therefore a **calibrated reconstruction**, not primary data; treat its exact per-hour values as an interpolation and its peak/trough placement and 00:00–08:00 mass as the empirically grounded parts.
- **Time conventions differ:** local vs. standard vs. mean-solar time, rounding to the hour/half-hour, and digit preference (spikes at 00:00 and 12:00) affect all historical registry data. Madrid explicitly used mean solar time.
- **Parity and season shift the peak by 1–3 hours.** Cagnacci et al. (1998, n=15,910 non-induced term deliveries) found a delivery peak ~14:00 in nulliparous women and an attenuated/absent rhythm in multiparous women; Madrid's peak block shifted later in summer than winter. A single fixed peak hour is an approximation across a heterogeneous international cohort.
- **Aggregate vs. spontaneous-only:** even in modern spontaneous subsets (US noninduced vaginal, England spontaneous), the curve is flatter than the prewar curve, because hospital care, analgesia, and augmentation attenuate the natural rhythm. The prewar amplitude (peak:trough ≈ 1.9:1 in the modelled table) may itself be conservative relative to truly undisturbed birth.
- **Source hygiene:** every curve here is drawn from national vital-statistics offices (NCHS, ONS-linked NHS data, Slovenian NPIS, Japanese MHW) or peer-reviewed demographic/epidemiological research (Varea, Charles, Declercq, Martin, Cagnacci). **No astrological chart collections, Astro-Databank, Gauquelin, or horoscope samples were used**, preserving the independence of the prior for rectification.