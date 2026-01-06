# Todo

## Reports

- [ ] Add "text" option to presentation reports that outputs sentences of information.
- [x] Midpoint trees
- [ ] Uranian: Modulus 90 sort

## Time Handling

- [ ] LMT (Local Mean Time) support for historical charts
  - Add `use_lmt` parameter to Native (True/False/None for auto-detect)
  - LMT offset formula: longitude / 15 hours from UTC
  - Auto-detect based on country + date (requires standardization date lookup)
  - Country standardization dates: US (1883-11-18), UK (1880), France (1891), Germany (1893), etc.
  - For raw lat/lon input: default to modern timezone with warning if date < 1900
  - Store country in ChartLocation from geocoding result

## Chart Visualization

- [ ] Add vedic square-type charts
- [ ] Update chart grid to take in *arbitrary wheel-only charts*

## Core Functions

- [x] Primary Directions
- [ ] Orb moieties (sum orb of two planets and get average)
- [x] Heliocentric calculations
- [x] Draconic charts (nodal)
- [ ] Topocentric parallax corrections for planet coordinates
- [x] Uranian degree dial chart
- [ ] Add chart info overview (header) to Uranian dial viz
- [ ] Uranian-style midpoint calculation (A + B - C = D)
- [x] Add Aries Point to objects (uranian)

## Chinese Astrology

### Bazi (Four Pillars) - In Progress
- [x] Core primitives (stems, branches, elements, polarity)
- [x] Solar term calculations
- [x] Five Tigers / Five Rats formulas
- [x] Basic BaZiChart and Pillar models
- [x] Hidden stems (藏干) with position labels (本气/中气/余气)
- [x] Ten Gods (十神) analysis module
- [x] Rich table renderer (BaziRichRenderer)
- [x] Prose renderer for conversations (BaziProseRenderer)
- [x] SVG visual chart renderer (BaziSVGRenderer)
- [ ] Clashes, combinations, and penalties (刑冲合害)
- [ ] Luck pillars (大运) calculation
- [ ] Annual pillars (流年)
- [ ] Day Master strength analysis

### Zi Wei Dou Shu (Purple Star) - Planned
- [ ] Define star enums and metadata (14 main stars + auxiliaries)
- [ ] Implement 12 palace system
- [ ] Calculate main star positions
- [ ] Calculate auxiliary stars
- [ ] Implement transformations (四化)
- [ ] Support decade/annual charts

## Testing
