# Todo

## Reports

- [ ] Add "text" option to presentation reports that outputs sentences of information.
- [x] Add PDF and HTML report options.
- [x] Add house cusp section
- [x] Add dignity report section (with essential and accidental modes).
- [ ] Add midpoint aspect report section.
- [x] Add aspect pattern report section.
- [x] Add Comparison chart sections (synastry, transit, progression)
- [x] Add Synthesis chart sections (composite, davison)

## Chart Visualization

- [x] Transfer over moon phase rendering code from old files.
- [x] Add chart type with more info (such as positions, native info, aspect triangle chart).
- [ ] Add option to render aspect triangle aspectarian charts separately.
- [ ] Add vedic square-type charts
- [x] Synastry square aspect table
- [x] Declinations
- [x] Add bi-wheel charts for Comparison charts
- [ ] Update chart grid to take in *arbitrary wheel-only charts*
- [x] Make aspect palettes better (more different colors, line styles)
  - [x] Maybe add a legend with the aspect count corner info?

### Fixes

- [x] Fix element-modality table to be properly aligned
- [x] On shrink (with >2 corners full of info): Chart AND OUTER BORDER need to shrink
- [x] Update chart themes to have better default zodiac etc. palettes

## Core Functions

- [x] Add synastry
- [x] Add composite
- [x] Add transits
- [ ] Add progressions
- [x] Add returns
- [x] Add sidereal
- [x] Add Vedic dignities
- [x] Declinations
- [x] Add more notable people and events to data registry
- [x] Add "name" parameter to ChartBuilder, that the chart drawer then uses for chart_info in larger font on top
- [ ] Add fixed stars
- [ ] Add progressions to ComparisonChart

### Fixes

- [x] Nudge planets outwards and house numbers inwards for natal charts
- [x] Don't calculate aspects for known things like: AC/DSC, MC/IC, NN/SN
  - [x] Don't calculate aspects between the 4 main angles in general
- [x] DO calculate aspects between Angles and other things
- [x] Make all aspect lines slightly transparent (alpha < 1)
- [x] When moon in is center of chart and aspects are displayed/present, move the moon to the corner
- [x] Make moon phase name use the same font and size and styling as the chart info corner section -- also make corner moon smaller, and make sure its label text has enough padding from the edge of the canvas (curerntly hits it)
- [x] Make sure default corner-moon has a label (default label to On)

## Testing

- [x] Look at coverage report and add more tests...
