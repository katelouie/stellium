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
  // glyph-char is the registry glyph (e.g. "⚸"); falls back to an abbreviation
  // of the label when there is no glyph (e.g. angles / points without one).
  let disc(sign: none, glyph-char: none, label: none, size: 34pt) = {
    let inner = if glyph-char != none and glyph-char != "" {
      glyph(glyph-char, size: size * 0.5, fill: ink)
    } else if label != none {
      text(font: body, size: size * 0.3, fill: ink)[#label.slice(0, calc.min(2, label.len()))]
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
  // Boxed at a fixed height with vertical centring so ☌ ⚹ ☍ (which sit high in
  // the font) line up with □ △ everywhere they appear.
  let aspect-mark(name, size: 11pt) = {
    let ch = aspect-glyph-of(name)
    let col = aspect-colors.at(aspect-key-of(name))
    let g = if ch == none { text(font: body, size: size, fill: col)[#name] } else {
      glyph(ch, size: size, fill: col)
    }
    box(height: size, align(center + horizon)[#g])
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
        #(if data.at("moon_svg", default: none) != none {
          image(data.moon_svg, width: 100pt)
        } else {
          box(width: 100pt, height: 100pt, radius: 50%, stroke: 1pt + hair)
        })
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
    // Fill the panel width: name auto, position stretches, the rest hug right.
    let col-spec = (auto, 1fr)
    for _ in house-headers { col-spec.push(auto) }
    if show-speed { col-spec.push(auto); col-spec.push(auto) }

    let rows = ()
    for p in planets {
      let cells = (
        // disc + name
        grid(columns: (auto, auto), column-gutter: 8pt, align: horizon,
          disc(sign: p.sign, glyph-char: p.at("glyph", default: ""), label: p.at("label", default: p.name), size: 26pt),
          disp(p.at("label", default: p.name), size: 13pt, fill: ink)),
        // position: sign glyph + sign + mono degree
        {
          let sg = p.at("sign_glyph", default: sign-glyph-of(p.sign))
          box[#(if sg != none and sg != "" { glyph(sg, size: 11pt, fill: accent) }) #text(font: body, size: 11pt, fill: muted)[#p.sign] #h(3pt) #mono(p.degree, size: 11pt, fill: ink)]
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
      columns: col-spec,
      stroke: none,
      inset: (x: 4pt, y: 7pt),
      fill: (col, row) => if row == 0 { none } else if calc.odd(row) { hair.lighten(55%) } else { none },
      table.header(..head-cells),
      ..rows.flatten(),
    )
  }

  // --- themed generic fallback table (long-tail sections) --------------------
  // full-width: true stretches the first column so the table spans the panel
  // (good for wide tables); false leaves it natural width, centred in the panel.
  let generic-table(headers, rows, full-width: true) = {
    let ncol = headers.len()
    // Column sizing: narrow tables get a flexible first column so they fill the
    // panel; wide tables (>=4 cols, often with a long text column) share the
    // width equally so no column collapses to zero and the table can't overflow.
    let col-spec = if not full-width or ncol <= 1 {
      (auto,) * ncol
    } else if ncol <= 3 {
      (1fr,) + (auto,) * (ncol - 1)
    } else {
      (1fr,) * ncol
    }
    let tbl = table(
      columns: col-spec,
      stroke: none,
      inset: (x: 8pt, y: 7pt),
      align: (col, row) => if col == 0 { left + horizon } else { center + horizon },
      fill: (col, row) => if row == 0 { none } else if calc.odd(row) { hair.lighten(55%) } else { none },
      table.header(..headers.map(h => lbl(h, size: 7.5pt))),
      ..rows.map(r => r.map(cell => text(font: (body, ..symbol-font), size: 10.5pt, fill: ink)[#cell])).flatten(),
    )
    if full-width { tbl } else { align(center)[#tbl] }
  }

  // --- aspectarian: lower-triangular aspect matrix ---------------------------
  // bodies: ordered canonical names. cells: (p1, p2, aspect) dicts.
  let aspectarian(bodies, cells) = {
    let n = bodies.len()
    if n == 0 { return [] }
    let name-of(b) = if type(b) == dictionary { b.name } else { b }
    // aspect lookup keyed by hi_lo body indices
    let amap = (:)
    for cel in cells {
      let i = bodies.position(x => name-of(x) == cel.p1)
      let j = bodies.position(x => name-of(x) == cel.p2)
      if i != none and j != none and i != j {
        let hi = calc.max(i, j)
        let lo = calc.min(i, j)
        amap.insert(str(hi) + "_" + str(lo), cel.aspect)
      }
    }
    let cs = 21pt
    let cell(i, j) = {
      if j == i {
        let b = bodies.at(i)
        let gch = if type(b) == dictionary { b.at("glyph", default: "") } else { "" }
        let lbl-txt = if type(b) == dictionary { b.at("label", default: b.name) } else { b }
        box(width: cs, height: cs, radius: 3pt, fill: hair.lighten(35%))[
          #align(center + horizon)[#(
            if gch != "" { glyph(gch, size: 11pt, fill: ink) } else {
              text(font: body, size: 6pt, fill: ink)[#lbl-txt.slice(0, calc.min(2, lbl-txt.len()))]
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

  // --- dispositor graph: native layered node-and-arrow diagram ---------------
  // Drawn from structured layout data (no graphviz / no external Typst package),
  // so it's portable, themed, and glyph-correct. positions are plain pt floats.
  let one-graph(g, gw) = {
    let R = 15.0
    let gap = 56.0
    let maxr = g.at("max_rank")
    let H = 2.0 * R + 16.0 + maxr * gap
    let edge-c = muted
    let nmap = (:)
    for n in g.nodes { nmap.insert(n.id, n) }
    let posof(n) = {
      let x = if n.ncols <= 1 { gw / 2.0 } else { gw * (n.col + 0.5) / n.ncols }
      let y = R + 8.0 + (maxr - n.rank) * gap
      (x, y)
    }
    let arrowhead(ex, ey, ux, uy, col) = {
      let px = -uy
      let py = ux
      place(polygon(
        fill: col,
        (ex * 1pt, ey * 1pt),
        ((ex - ux * 8.0 + px * 4.0) * 1pt, (ey - uy * 8.0 + py * 4.0) * 1pt),
        ((ex - ux * 8.0 - px * 4.0) * 1pt, (ey - uy * 8.0 - py * 4.0) * 1pt),
      ))
    }
    box(width: gw * 1pt, height: H * 1pt)[
      // edges (behind nodes)
      #for e in g.edges {
        let a = nmap.at(e.at("from"))
        let b = nmap.at(e.at("to"))
        let (ax, ay) = posof(a)
        let (bx, by) = posof(b)
        let dx = bx - ax
        let dy = by - ay
        let L = calc.max(calc.sqrt(dx * dx + dy * dy), 0.001)
        let ux = dx / L
        let uy = dy / L
        let sx = ax + ux * R
        let sy = ay + uy * R
        let ex = bx - ux * R
        let ey = by - uy * R
        let ec = if e.mutual { accent } else { edge-c }
        place(line(
          start: (sx * 1pt, sy * 1pt),
          end: (ex * 1pt, ey * 1pt),
          stroke: 1pt + ec,
        ))
        arrowhead(ex, ey, ux, uy, ec)
        if e.mutual { arrowhead(sx, sy, -ux, -uy, ec) }
      }
      // nodes
      #for n in g.nodes {
        let (x, y) = posof(n)
        let fill-c = if n.final { gold } else if laser { panel } else { hair.lighten(20%) }
        let txt-c = if n.final and not laser { bg } else { ink }
        place(
          dx: (x - R) * 1pt,
          dy: (y - R) * 1pt,
          box(
            width: 2.0 * R * 1pt, height: 2.0 * R * 1pt, radius: 50%,
            fill: fill-c, stroke: 0.8pt + (if n.final { gold.darken(15%) } else { rule }),
          )[#align(center + horizon)[#(
              if n.glyph != "" { glyph(n.glyph, size: 13pt, fill: txt-c) } else {
                text(font: body, size: 10pt, fill: txt-c)[#n.label]
              }
            )]],
        )
      }
    ]
  }

  let dispositor-graph(graphs) = {
    let n = graphs.len()
    let gw = if n >= 2 { 190.0 } else { 300.0 }
    grid(
      columns: (1fr,) * n,
      column-gutter: 16pt,
      ..graphs.map(g => block(
        stroke: 1pt + hair, radius: 8pt, inset: 10pt, width: 100%,
      )[
        #align(center)[#text(font: display, weight: t.display-weight, size: 10pt, tracking: 0.14em, fill: accent)[#upper(g.title)]]
        #v(10pt)
        #align(center)[#one-graph(g, gw)]
      ]),
    )
  }

  // --- aspect list: structured rows with design-system glyphs ----------------
  let aspect-list(aspects) = {
    let planet-cell(gch, lbl-txt) = {
      box[#(if gch != none and gch != "" { glyph(gch, size: 11pt, fill: ink) }) #text(font: body, size: 10.5pt, fill: ink)[ #lbl-txt]]
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
        planet-cell(a.at("p1_glyph", default: ""), a.at("p1_label", default: a.p1)),
        box[#aspect-mark(a.aspect, size: 11pt) #text(font: body, size: 10.5pt, fill: ink)[ #a.aspect]],
        planet-cell(a.at("p2_glyph", default: ""), a.at("p2_label", default: a.p2)),
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
    aspect-list: aspect-list, dispositor-graph: dispositor-graph,
    star-ornament: star-ornament, metadata-line: metadata-line,
    title-block: title-block,
  )
}
