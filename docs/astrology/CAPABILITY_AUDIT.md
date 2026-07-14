# Stellium Capability Audit (Astrology)

*What techniques, traditions, and schools of astrology does Stellium actually
implement? This is the topic-and-capability map, written for the astrology side
rather than the code side. For the "how do I call it in Python" version, every
row here points at a cookbook in [`examples/`](../../examples/) or a guide
chapter in [`guide/`](./guide/).*

Last audited against source: see `git log`. When this disagrees with the code,
the code wins.

---

## How to read this

Astrology isn't one thing. It's a stack of traditions built over ~2,500 years,
each with its own zodiac, its own chart factors, and its own idea of what a
chart is *for*. Stellium leans Western/Hellenistic in its depth, covers Vedic
and Chinese as first-class but narrower traditions, and stays neutral about
which framework is "right" (it computes; you interpret).

Coverage is marked three ways:

- **Full** — the technique is implemented as a first-class feature with its own
  engine/component/builder.
- **Partial** — the pieces exist but the named technique isn't packaged as one
  workflow (e.g. horary: the machinery is all there, the "judge a question
  chart" wrapper isn't).
- **Not covered** — genuinely absent as of this audit. Listed honestly so nobody
  builds on a feature that isn't there.

---

## 1. Western astrology (the deep end)

This is where Stellium is most complete. It spans three eras that often get
treated as separate schools: **Hellenistic/traditional** (roughly 150 BCE–1700
CE), **modern/psychological** (20th century), and **contemporary computational**
(now).

### 1.1 Zodiac frameworks

| Capability | Coverage | Where |
|---|---|---|
| Tropical zodiac (season-anchored, Western default) | Full | core config |
| Sidereal zodiac (star-anchored) with 9 ayanamsas | Full | `with_sidereal(...)` |
| Draconic zodiac (re-cast from the lunar node) | Full | `chart.draconic()` |
| Heliocentric positions (Sun-centered) | Full | `with_heliocentric()` |

Tropical and sidereal are **parallel interpretive frameworks**, not competing
accuracy claims. The ~24° gap between them is the ayanamsa. Stellium lets you
run either, or both, on the same birth data.

### 1.2 Chart factors (what goes in the chart)

| Factor group | Count | Coverage |
|---|---|---|
| Classical planets (Sun–Saturn, the "seven") | 7 | Full |
| Modern outer planets (Uranus, Neptune, Pluto) | 3 | Full |
| Lunar nodes (True/Mean North, South = Rahu/Ketu) | 3 | Full |
| Lunar apogee / Black Moon Lilith (mean/true/osc./interp.) | 4 | Full |
| Chart points (ASC, MC, DSC, IC, Vertex, East Point) | 6 | Full |
| Main-belt asteroids (Ceres, Pallas, Juno, Vesta, Hygiea) | 5 | Full |
| Centaurs (Chiron, Pholus, Nessus, Chariklo) | 4 | Full |
| Trans-Neptunian objects (Eris, Sedna, Makemake, Haumea, Orcus, Quaoar) | 6 | Full |
| Uranian/Hamburg hypotheticals (Cupido…Poseidon) | 8 | Full |

**37 selectable objects** total. Defaults are sane (traditional + modern planets,
nodes, Chiron); everything else is opt-in.

### 1.3 Houses

| Capability | Coverage |
|---|---|
| 18 house systems (Placidus, Whole Sign, Koch, Equal, Porphyry, Regiomontanus, Campanus, Alcabitius, Topocentric, Morinus, Krusinski, Equal-MC, Vehlow, Equal-Vertex, Gauquelin, Horizontal, Axial Rotation, APC) | Full |
| **Multiple house systems on one chart, simultaneously** | Full (a genuine differentiator) |
| Angles computed per system (ASC/MC/DSC/IC/Vertex) | Full |

### 1.4 Aspects

| Capability | Coverage |
|---|---|
| Major/Ptolemaic (conjunction, sextile, square, trine, opposition) | Full |
| Minor (semisextile, semisquare, sesquisquare, quincunx) | Full |
| Harmonic families — quintile (H5), septile (H7), novile (H9) | Full |
| Declination aspects (parallel, contraparallel) | Full |
| Applying vs separating (from relative velocity) | Full |
| Configurable orbs: Simple, Luminaries, Complex, **Moiety** (Lilly/Ptolemy) | Full |
| Aspect patterns: Grand Trine, T-Square, Yod, Grand Cross, Mystic Rectangle, Kite, Stellium | Full |

### 1.5 Traditional / Hellenistic technique

This is the part most Python astrology libraries skip. Stellium takes it
seriously.

| Capability | Coverage |
|---|---|
| **Sect** (day/night chart) and sect-aware calculation throughout | Full |
| Essential dignity: domicile, exaltation, triplicity (by sect), bounds/terms (Egyptian), decans/faces (Chaldean *or* triplicity), detriment, fall | Full, with scoring |
| Accidental dignity: angularity, planetary joys, retrograde, cazimi/combustion | Full |
| Traditional **and** modern rulership schemes | Full |
| Peregrine, mutual reception | Full |
| Dispositor chains/graphs (planetary + house-based), final dispositor | Full |
| Arabic Parts / Lots — 28, sect-aware (Hermetic, family, life-topic, planetary) | Full |
| Chart ruler | Full |

### 1.6 Timing & prediction

| Technique | Era | Coverage |
|---|---|---|
| Transits (transit-to-natal timeline, orb entry/exit, retrograde multi-pass, Gantt) | modern | Full |
| Secondary progressions (+ tertiary, minor) | modern | Full |
| Solar arc directions (+ Naibod, lunar, chart-ruler, sect, planetary arcs) | modern/trad | Full |
| **Primary directions** (with 3D modeling, distribution across bounds) | traditional | Full |
| Zodiacal (in-zodiaco) directions | traditional | Full |
| **Annual & monthly profections** + lord of the year (Whole Sign) | Hellenistic | Full |
| **Zodiacal Releasing** (from Fortune/Spirit + 25 lots; peaks, Loosing of the Bond, fractal mode) | Hellenistic (Valens) | Full |
| Returns: solar, lunar, planetary (+ relocated) | trad/modern | Full |
| Graphic ephemeris (incl. harmonic) | modern | Full |

### 1.7 Electional, horary, and time-lord adjacent

| Technique | Coverage |
|---|---|
| Electional search (30+ predicates, interval optimization) | Full |
| Planetary hours (Chaldean order) | Full |
| Void-of-course Moon (traditional + modern definitions) | Full |
| Horary (judging a question chart as a named workflow) | **Partial** — all the parts exist (dignity, reception, VOC, applying aspects, planetary hours); no dedicated "horary judgment" wrapper |

### 1.8 Uranian / cosmobiology

| Capability | Coverage |
|---|---|
| Uranian / Hamburg School (8 hypothetical TNPs) | Full |
| Dials: 90° / 45° / 360°, with pointers and transits | Full |
| Midpoints (direct, indirect, midpoint trees, midpoint aspects) | Full |
| Antiscia & contra-antiscia (solstice points) | Full |

### 1.9 Fixed stars & declination

| Capability | Coverage |
|---|---|
| 26 fixed stars in 3 tiers (Royal Stars of Persia → major → extended) | Full |
| Star-to-planet conjunctions by longitude | Full |
| Out-of-bounds detection (declination > 23°27′) | Full |
| Parallels / contraparallels | Full |
| **Parans** (mundane rising/culminating star relationships) | **Not covered** |

### 1.10 Relationship astrology

| Technique | Coverage |
|---|---|
| Synastry (cross-aspects, house overlays, compatibility scoring) | Full |
| Composite (midpoint) charts | Full |
| Davison (time-space midpoint) charts | Full |
| Bi-/tri-/quad-wheel rendering | Full |

### 1.11 Chart-level structure

| Capability | Coverage |
|---|---|
| Chart shapes (Bundle, Bowl, Bucket, Locomotive, Seesaw, Splay, Splash) | Full |
| Harmonic **aspects** + draconic (a 1st-harmonic-of-the-node recast) | Full |
| Full harmonic **chart recasting** as a distinct chart type (Addey Nth-harmonic) | **Partial** — harmonic aspects and graphic ephemeris yes; a standalone "5th harmonic chart" object, no |
| Unknown-birth-time handling (Moon range, no houses/angles) | Full |
| Relocated charts | Full |
| Astrocartography / ACG line maps | **Not covered** (relocation charts yes; world map lines no) |

---

## 2. Vedic astrology (Jyotish) — real but bounded

Stellium's Vedic support is **sidereal calculation + traditional chart
rendering**, not the full Jyotish predictive apparatus. Be honest with users
about this boundary; it's the most likely place to disappoint a serious Vedic
astrologer.

| Capability | Coverage |
|---|---|
| Sidereal zodiac with 9 ayanamsas (Lahiri, Raman, Krishnamurti/KP, Yukteshwar, JN Bhasin, True Chitra, True Revati, Fagan-Bradley, De Luce) | Full |
| North Indian & South Indian chart rendering (3 themes, 4 label styles) | Full |
| Rahu / Ketu | Full |
| **Nakshatras** (27 lunar mansions) | **Not covered** |
| **Dashas** (Vimshottari and other planetary periods) | **Not covered** |
| **Vargas / divisional charts** (D9 Navamsa, D10, etc.) | **Not covered** |
| **Ashtakavarga**, **yogas**, Jaimini technique | **Not covered** |

Framing for docs: Stellium renders a rigorous sidereal chart in authentic Vedic
formats. The predictive layer (dashas, nakshatras, vargas) is where a dedicated
Jyotish tool still wins.

---

## 3. Chinese astrology (BaZi / Four Pillars)

| Capability | Coverage |
|---|---|
| BaZi / Four Pillars (Year/Month/Day/Hour) | Full |
| Ten Gods (十神) | Full |
| Hidden Stems | Full |
| Day Master strength | Full |
| Wu Xing / Five Elements with generation & control cycles | Full |
| Heavenly Stems (10) & Earthly Branches (12) | Full |
| Solar terms (year begins at Li Chun, 315°, not Jan 1) | Full |
| **Zi Wei Dou Shu** (Purple Star) | **Planned, not implemented** |

---

## 4. Cross-cutting / computational

The "modern astrology meets data science" layer. Rare in astrology software.

| Capability | Coverage |
|---|---|
| Batch calculation over hundreds of charts | Full |
| pandas DataFrame export (charts, positions, aspects) | Full |
| Statistical aggregation (element/sign/aspect distributions) | Full |
| Chart vectorization + cosine similarity | Full |
| Research query DSL (filter by sign/house/aspect/pattern/sect) | Full |
| LLM-ready export (`to_prompt_text()`, prose renderer) | Full |
| Notable-births database with Rodden ratings | Full |
| Import: CSV, AAF (astro.com), DataFrame | Full |

---

## 5. Coverage boundaries at a glance (the honest list)

Not-yet-covered techniques, gathered in one place so they're easy to find and
easy to turn into a roadmap:

- **Vedic predictive stack:** nakshatras, dashas (Vimshottari et al.), vargas
  (divisional charts), ashtakavarga, yogas, Jaimini.
- **Firdaria** (Persian/medieval time-lord periods).
- **Fixed-star parans** (mundane rising/culminating relationships).
- **Astrocartography / ACG** world-map relocation lines.
- **Full harmonic-chart recasting** (Addey) as a distinct chart object.
- **Horary judgment** as a packaged workflow (the ingredients are all present).
- **Zi Wei Dou Shu** (planned).

None of these are load-bearing gaps for the library's core promise. They're the
natural next frontier, and worth stating plainly so contributors and users
aren't surprised.

---

## 6. Traditions × depth summary

| Tradition | Calculation | Interpretation scaffolding | Prediction | Verdict |
|---|---|---|---|---|
| Western — Hellenistic/traditional | Deep | Deep (sect, dignity, lots, dispositors) | Deep (profections, ZR, directions, primary) | **Flagship** |
| Western — modern/psychological | Deep | Deep (aspects, patterns, outer planets, asteroids) | Deep (transits, progressions, solar arc, returns) | **Flagship** |
| Western — Uranian/cosmobiology | Deep | Deep (dials, midpoints, antiscia) | Partial (transit dials) | **Strong** |
| Vedic / Jyotish | Deep (sidereal) | Rendering only | None yet | **Chart-rendering tier** |
| Chinese / BaZi | Deep | Deep (Ten Gods, elements, strength) | Via luck pillars (partial) | **Strong, self-contained** |
| Computational / research | Deep | n/a | n/a | **Distinctive** |

---

*This audit is the blueprint for the [Astrology Guide](./guide/). Each guide
chapter takes one row (or cluster of rows) and gives it the full treatment:
history, theory, how practitioners actually use it, and the Stellium code to
reproduce it.*
