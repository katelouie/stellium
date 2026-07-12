// ============================================================================
// components.typ — the shared COMPOSITION layer.
//
// make(theme) binds the whole component vocabulary to one resolved theme and
// returns it as a dict. Destructure it in the engine:
//
//   #let c = make(resolve-theme("house"))
//   #let (title-block, section, planet-table, ..rest) = c
//
// (Typst won't call dict-stored functions with method syntax — destructure.)
//
// Every visual literal lives here or in palettes.typ; the engine/content layer
// carries none. Swapping the theme swaps every colour, font and the laser flag.
// ============================================================================

#import "glyphs.typ": glyph, symbol-font, planet-glyph-of, sign-glyph-of, aspect-glyph-of, aspect-key-of

#let make(t) = {
  // --- token shorthands ------------------------------------------------------
  let bg = t.bg
  let ink = t.ink
  let accent = t.accent
  let gold = t.gold
  let muted = t.muted
  let rule = t.rule
  let hair = t.hair
  let panel = t.panel
  let laser = t.laser
  let display = t.display
  let body = t.body
  let mono-font = t.mono
  let sign-tints = t.sign-tints
  let sign-order = t.sign-order
  let aspect-colors = t.aspect-colors

  // --- tiny text primitives --------------------------------------------------
  // Tracked uppercase label (field labels, running header).
  let lbl(s, fill: muted, size: 8pt, tracking: 0.16em) = {
    text(font: body, size: size, tracking: tracking, fill: fill)[#upper(s)]
  }
  // Display-face title text.
  let disp(s, size: 17pt, fill: ink, tracking: t.display-tracking) = {
    text(font: display, weight: t.display-weight, size: size, fill: fill, tracking: tracking)[#s]
  }
  // Monospace tabular figures.
  let mono(s, size: 9pt, fill: ink) = text(font: mono-font, size: size, fill: fill)[#s]
  let hairline(w: 100%, stroke-w: 0.75pt, color: rule) = line(length: w, stroke: stroke-w + color)

  // sign name -> tint colour
  let tint-of(sign) = {
    let i = sign-order.position(x => x == sign)
    if i == none { hair } else { sign-tints.at(i) }
  }

  // --- disc: tinted circle carrying a planet glyph or a short text label ------
  let disc(sign: none, glyph-name: none, label: none, size: 34pt) = {
    let inner = if glyph-name != none and planet-glyph-of(glyph-name) != none {
      glyph(planet-glyph-of(glyph-name), size: size * 0.5, fill: ink)
    } else if label != none {
      text(font: body, size: size * 0.34, fill: ink)[#label]
    } else { [] }
    let fill-c = if laser { none } else { tint-of(sign) }
    let stroke-c = if laser { 1.4pt + ink } else { none }
    box(
      width: size, height: size, radius: 50%,
      fill: fill-c, stroke: stroke-c,
      align(center + horizon)[#inner],
    )
  }

  // --- house badge: small pill ------------------------------------------------
  let badge(n) = {
    let fill-c = if laser { none } else { accent }
    let stroke-c = if laser { 1.4pt + ink } else { none }
    let txt-c = if laser { ink } else { bg }
    box(
      inset: (x: 7pt, y: 3pt), radius: 8pt,
      fill: fill-c, stroke: stroke-c,
      text(font: body, size: 9pt, fill: txt-c)[#n],
    )
  }

  // --- aspect glyph in its type colour ---------------------------------------
  let aspect-mark(name, size: 11pt) = {
    let ch = aspect-glyph-of(name)
    let col = aspect-colors.at(aspect-key-of(name))
    if ch == none { text(font: body, size: size, fill: col)[#name] }
    else { glyph(ch, size: size, fill: col) }
  }

  // --- running header / footer (splat into set page) -------------------------
  let header(left-text, right-text) = context {
    if counter(page).get().first() > 1 {
      grid(
        columns: (1fr, auto, 1fr),
        align: (left, center, right),
        lbl(left-text, size: 7.5pt),
        glyph("\u{2605}", size: 8pt, fill: gold),
        lbl(right-text, size: 7.5pt),
      )
    }
  }
  let footer(center-text) = align(center)[
    #text(font: body, size: 7.5pt, tracking: 0.12em, fill: muted)[
      #upper[Generated with Stellium] #h(4pt) #glyph("\u{2726}", size: 7pt, fill: gold) #h(4pt) #upper[#center-text]
    ]
  ]

  // --- section: star + tracked-caps title + hairline + optional descriptor ----
  // Wrapped in a full-width rounded panel (radius 12, 1px hair border).
  let section(title, body-content, descriptor: none) = {
    block(
      width: 100%, breakable: true,
      fill: panel, radius: 12pt,
      stroke: 1pt + hair,
      inset: (x: 18pt, y: 16pt),
    )[
      #grid(
        columns: (auto, auto, 1fr, auto),
        align: (left + horizon, left + horizon, center + horizon, right + horizon),
        column-gutter: 10pt,
        glyph("\u{2606}", size: 12pt, fill: gold),
        text(font: display, weight: t.display-weight, size: 14pt, tracking: 0.2em, fill: accent)[#upper(title)],
        hairline(stroke-w: 0.75pt, color: hair),
        if descriptor != none { text(font: body, size: 10pt, style: "italic", fill: muted)[#descriptor] } else { [] },
      )
      #v(12pt)
      #body-content
    ]
  }

  // --- stat card (snapshot) ---------------------------------------------------
  let stat-card(label, value, sub) = {
    block(
      width: 100%, radius: 8pt, stroke: 1pt + hair, inset: (x: 14pt, y: 10pt),
    )[
      #lbl(label, size: 8pt)
      #v(3pt)
      #disp(value, size: 22pt, fill: ink)
      #v(1pt)
      #text(font: body, size: 10pt, fill: muted)[#sub]
    ]
  }
  let cards-row(cards) = grid(
    columns: cards.map(_ => 1fr),
    column-gutter: 12pt,
    ..cards.map(c => stat-card(c.label, c.value, c.at("sub", default: ""))),
  )

  // --- key/value grid (chart overview) ---------------------------------------
  // pairs: array of (label, value). Rendered two logical columns wide.
  let kv-grid(pairs, columns: 2) = {
    let cell(p) = [
      #lbl(p.at(0), size: 8pt)
      #v(2pt)
      #text(font: body, size: 12pt, fill: ink)[#p.at(1)]
    ]
    grid(
      columns: (1fr,) * columns,
      column-gutter: 24pt,
      row-gutter: 12pt,
      ..pairs.map(cell),
    )
  }

  // --- labeled progress bar (elements / modalities / polarity) ---------------
  let bar-row(label, value, max, count, fill: none) = {
    let frac = if max == 0 { 0 } else { calc.min(value / max, 1) }
    let fill-c = if fill != none { fill } else { accent }
    grid(
      columns: (58pt, 1fr, 24pt),
      align: (left + horizon, left + horizon, right + horizon),
      column-gutter: 10pt,
      text(font: body, size: 11pt, fill: ink)[#label],
      box(width: 100%, height: 9pt, radius: 4pt, fill: hair)[
        #box(width: frac * 100%, height: 9pt, radius: 4pt, fill: (if laser { muted } else { fill-c }))
      ],
      mono(str(count), size: 10pt, fill: muted),
    )
  }

  // --- moon phase block -------------------------------------------------------
  let moon-phase(data) = {
    grid(
      columns: (120pt, 1fr),
      column-gutter: 20pt,
      align: (center, left),
      [
        #box(width: 100pt, height: 100pt, radius: 50%, stroke: 1pt + hair)
        #v(6pt)
        #text(font: body, size: 13pt, weight: "medium", fill: ink)[#data.phase]
      ],
      [
        #grid(
          columns: (1fr, 1fr, 1fr),
          row-gutter: 12pt, column-gutter: 14pt,
          ..data.fields.map(f => [
            #lbl(f.at(0), size: 8pt)
            #v(3pt)
            #(if f.len() >= 3 and f.at(2) == true { disp(f.at(1), size: 22pt, fill: ink) } else { mono(f.at(1), size: 11pt, fill: ink) })
          ]),
        )
      ],
    )
  }

  // --- planet positions table -------------------------------------------------
  // planets: array of (name, glyph, sign, sign_glyph, degree, houses:(..), speed, retro)
  // columns: which house-system column headers to show.
  let planet-table(planets, house-headers: (), show-speed: true) = {
    let head-cells = (
      lbl("Planet", size: 7.5pt), lbl("Position", size: 7.5pt),
    )
    head-cells += house-headers.map(h => align(center)[#lbl(h, size: 7.5pt)])
    if show-speed {
      head-cells += (align(right)[#lbl("Speed", size: 7.5pt)], align(right)[#lbl("Motion", size: 7.5pt)])
    }
    let ncol = 2 + house-headers.len() + (if show-speed { 2 } else { 0 })

    let rows = ()
    for p in planets {
      let cells = (
        // disc + name
        grid(columns: (auto, auto), column-gutter: 8pt, align: horizon,
          disc(sign: p.sign, glyph-name: p.name, size: 26pt),
          disp(p.at("label", default: p.name), size: 13pt, fill: ink)),
        // position: sign glyph + sign + mono degree
        {
          let sg = sign-glyph-of(p.sign)
          box[#(if sg != none { glyph(sg, size: 11pt, fill: accent) }) #text(font: body, size: 11pt, fill: muted)[#p.sign] #h(3pt) #mono(p.degree, size: 11pt, fill: ink)]
        },
      )
      cells += p.houses.map(h => align(center + horizon)[#badge(h)])
      if show-speed {
        cells += (
          align(right + horizon)[#mono(p.speed, size: 9.5pt, fill: muted)],
          align(right + horizon)[#(if p.retro { text(font: body, size: 10pt, fill: aspect-colors.square)[Retro] } else { text(font: body, size: 10pt, fill: muted)[Direct] })],
        )
      }
      rows.push(cells)
    }

    table(
      columns: ncol,
      stroke: none,
      inset: (x: 4pt, y: 7pt),
      fill: (col, row) => if row == 0 { none } else if calc.odd(row) { hair.lighten(55%) } else { none },
      table.header(..head-cells),
      ..rows.flatten(),
    )
  }

  // --- themed generic fallback table (long-tail sections) --------------------
  let generic-table(headers, rows) = {
    let ncol = headers.len()
    table(
      columns: ncol,
      stroke: none,
      inset: (x: 8pt, y: 7pt),
      align: (col, row) => if col == 0 { left + horizon } else { center + horizon },
      fill: (col, row) => if row == 0 { none } else if calc.odd(row) { hair.lighten(55%) } else { none },
      table.header(..headers.map(h => lbl(h, size: 7.5pt))),
      ..rows.map(r => r.map(cell => text(font: (body, symbol-font), size: 10.5pt, fill: ink)[#cell])).flatten(),
    )
  }

  // --- aspectarian: lower-triangular aspect matrix ---------------------------
  // bodies: ordered canonical names. cells: (p1, p2, aspect) dicts.
  let aspectarian(bodies, cells) = {
    let n = bodies.len()
    if n == 0 { return [] }
    // aspect lookup keyed by hi_lo body indices
    let amap = (:)
    for cel in cells {
      let i = bodies.position(x => x == cel.p1)
      let j = bodies.position(x => x == cel.p2)
      if i != none and j != none and i != j {
        let hi = calc.max(i, j)
        let lo = calc.min(i, j)
        amap.insert(str(hi) + "_" + str(lo), cel.aspect)
      }
    }
    let cs = 21pt
    let cell(i, j) = {
      if j == i {
        let g = planet-glyph-of(bodies.at(i))
        box(width: cs, height: cs, radius: 3pt, fill: hair.lighten(35%))[
          #align(center + horizon)[#(
            if g != none { glyph(g, size: 11pt, fill: ink) } else {
              text(font: body, size: 7pt, fill: ink)[#bodies.at(i)]
            }
          )]
        ]
      } else if j < i {
        let asp = amap.at(str(i) + "_" + str(j), default: none)
        box(width: cs, height: cs, stroke: 0.5pt + hair)[
          #align(center + horizon)[#(if asp != none { aspect-mark(asp, size: 11pt) })]
        ]
      } else {
        box(width: cs, height: cs)
      }
    }
    let items = ()
    for i in range(n) {
      for j in range(n) {
        items.push(cell(i, j))
      }
    }
    grid(columns: (cs,) * n, ..items)
  }

  // --- aspect colour-code legend ---------------------------------------------
  let aspect-legend() = {
    let items = (
      ("Conjunction", "Conj"), ("Sextile", "Sextile"), ("Square", "Square"),
      ("Trine", "Trine"), ("Opposition", "Opp"),
    )
    grid(
      columns: items.len() * (auto,),
      column-gutter: 16pt,
      ..items.map(it => box[
        #aspect-mark(it.at(0), size: 11pt) #h(3pt) #text(font: body, size: 9pt, fill: muted)[#it.at(1)]
      ]),
    )
  }

  // --- aspect list: structured rows with design-system glyphs ----------------
  let aspect-list(aspects) = {
    let planet-cell(nm) = {
      let g = planet-glyph-of(nm)
      box[#(if g != none { glyph(g, size: 11pt, fill: ink) }) #text(font: body, size: 10.5pt, fill: ink)[ #nm]]
    }
    let applying-cell(ap) = {
      if ap == true { text(font: body, size: 10pt, fill: muted)[Applying] }
      else if ap == false { text(font: body, size: 10pt, fill: muted)[Separating] }
      else { text(font: body, size: 10pt, fill: muted)[—] }
    }
    table(
      columns: (1.4fr, 1fr, 1.4fr, auto, auto),
      stroke: none,
      inset: (x: 6pt, y: 6pt),
      align: (col, row) => if col >= 3 { right + horizon } else { left + horizon },
      fill: (col, row) => if row == 0 { none } else if calc.odd(row) { hair.lighten(55%) } else { none },
      table.header(
        lbl("Planet 1", size: 7.5pt), lbl("Aspect", size: 7.5pt),
        lbl("Planet 2", size: 7.5pt),
        align(right)[#lbl("Orb", size: 7.5pt)],
        align(right)[#lbl("Applying", size: 7.5pt)],
      ),
      ..aspects.map(a => (
        planet-cell(a.p1),
        box[#aspect-mark(a.aspect, size: 11pt) #text(font: body, size: 10.5pt, fill: ink)[ #a.aspect]],
        planet-cell(a.p2),
        mono(a.at("orb", default: ""), size: 9.5pt, fill: muted),
        applying-cell(a.at("applying", default: none)),
      )).flatten(),
    )
  }

  // --- two tables side by side (comparison / multichart) ---------------------
  let side-by-side(tables) = grid(
    columns: tables.map(_ => 1fr),
    column-gutter: 20pt,
    ..tables.map(tb => [
      #(if tb.at("title", default: "") != "" [ #lbl(tb.title, size: 8pt) #v(6pt) ])
      #generic-table(tb.headers, tb.rows)
    ]),
  )

  // --- sub-block: a titled sub-unit inside a compound section ----------------
  let sub-block(title, body-content) = [
    #(if title != "" [
      #text(font: display, weight: t.display-weight, size: 11pt, tracking: 0.14em, fill: accent)[#upper(title)]
      #v(2pt)
      #hairline(w: 100%, stroke-w: 0.5pt, color: hair)
      #v(8pt)
    ])
    #body-content
  ]

  // --- title page block -------------------------------------------------------
  let star-ornament() = align(center)[
    #glyph("\u{2605}", size: 10pt, fill: gold) #h(8pt)
    #glyph("\u{2606}", size: 10pt, fill: gold) #h(8pt)
    #glyph("\u{2605}", size: 10pt, fill: gold)
  ]
  let metadata-line(items) = align(center)[
    #text(font: body, size: 11pt, tracking: 0.18em, fill: gold)[
      #upper(items.join("  \u{00B7}  "))
    ]
  ]
  let title-block(meta) = align(center)[
    #disp("Stellium", size: 16pt, fill: accent, tracking: 0.3em)
    #v(6pt)
    #star-ornament()
    #v(10pt)
    #lbl(meta.kicker, size: 10pt, fill: muted, tracking: 0.22em)
    #v(6pt)
    #disp(meta.name, size: 37pt, fill: accent)
    #v(4pt)
    #text(font: body, size: 13pt, style: "italic", fill: muted)[#meta.subtitle]
  ]

  // return the vocabulary
  (
    theme: t,
    lbl: lbl, disp: disp, mono: mono, hairline: hairline,
    disc: disc, badge: badge, aspect-mark: aspect-mark,
    header: header, footer: footer,
    section: section, stat-card: stat-card, cards-row: cards-row,
    kv-grid: kv-grid, bar-row: bar-row, moon-phase: moon-phase,
    planet-table: planet-table, generic-table: generic-table,
    side-by-side: side-by-side, sub-block: sub-block,
    aspectarian: aspectarian, aspect-legend: aspect-legend,
    aspect-list: aspect-list,
    star-ornament: star-ornament, metadata-line: metadata-line,
    title-block: title-block,
  )
}
