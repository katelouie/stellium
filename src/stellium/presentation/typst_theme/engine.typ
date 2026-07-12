// ============================================================================
// engine.typ — data-driven layout. Reads the report `data` (from JSON) and a
// bound component vocabulary `c` (make(theme)); dispatches each section by its
// `kind` to the right component. Known kinds get bespoke, section-aware
// components; anything else falls back to a themed generic table / kv / text.
//
// The engine holds ZERO visual literals — every colour, font and spacing value
// comes from `c`. Theme = swap `c`; the engine is identical.
// ============================================================================

// --- title page -------------------------------------------------------------
#let render-title(c, meta) = {
  (c.title-block)(meta)
  v(14pt)
  if meta.at("chart_svg", default: none) != none {
    align(center)[#image(meta.chart_svg, width: 46%)]
    v(10pt)
  }
  if meta.at("cards", default: ()).len() > 0 {
    (c.cards-row)(meta.cards)
    v(10pt)
  }
  if meta.at("metadata", default: ()).len() > 0 {
    (c.metadata-line)(meta.metadata)
  }
}

// --- snapshot body (stat cards + element/modality/polarity bars) ------------
#let snapshot-body(c, sec) = {
  let bars-for(group, tone) = {
    let mx = calc.max(..group.map(g => g.count), 1)
    stack(spacing: 9pt, ..group.map(g => {
      let fill = if tone == "element" {
        c.theme.element-colors.at(g.label, default: c.theme.accent)
      } else if tone == "gold" and g.label == "Mutable" {
        c.theme.gold
      } else { c.theme.accent }
      (c.bar-row)(g.label, g.count, mx, g.count, fill: fill)
    }))
  }

  if sec.at("cards", default: ()).len() > 0 {
    (c.cards-row)(sec.cards)
    v(16pt)
  }
  grid(
    columns: (1fr, 1fr),
    column-gutter: 28pt,
    [
      #(c.lbl)("Elements")
      #v(8pt)
      #bars-for(sec.elements, "element")
    ],
    [
      #(c.lbl)("Modalities")
      #v(8pt)
      #bars-for(sec.modalities, "gold")
      #if sec.at("polarity", default: none) != none [
        #v(12pt)
        #(c.lbl)("Polarity")
        #v(8pt)
        #let pol = sec.polarity
        #let total = calc.max(pol.yang + pol.yin, 1)
        #box(width: 100%, height: 9pt, radius: 4pt, clip: true, fill: c.theme.hair)[
          #box(width: (pol.yang / total) * 100%, height: 9pt, fill: c.theme.gold)
          #box(width: (pol.yin / total) * 100%, height: 9pt, fill: c.theme.accent)
        ]
      ]
    ],
  )
}

// --- inner content of a section, by kind (no panel wrapper) -----------------
#let body-of(c, sec) = {
  let kind = sec.at("kind", default: "table")
  if kind == "snapshot" {
    snapshot-body(c, sec)
  } else if kind == "chart_overview" or kind == "key_value" {
    (c.kv-grid)(sec.pairs)
  } else if kind == "moon_phase" {
    (c.moon-phase)(sec)
  } else if kind == "planet_positions" {
    (c.planet-table)(
      sec.planets,
      house-headers: sec.at("house_headers", default: ()),
      show-speed: sec.at("show_speed", default: true),
    )
  } else if kind == "table" {
    (c.generic-table)(sec.headers, sec.rows)
  } else if kind == "aspectarian" {
    stack(
      spacing: 14pt,
      (c.aspectarian)(sec.bodies, sec.cells),
      (c.aspect-legend)(),
    )
  } else if kind == "aspect_list" {
    (c.aspect-list)(sec.aspects)
  } else if kind == "svg" {
    if sec.at("svg_file", default: none) != none {
      align(center)[#image(sec.svg_file, width: 92%)]
    } else { [] }
  } else if kind == "side_by_side" {
    (c.side-by-side)(sec.tables)
  } else if kind == "compound" {
    stack(spacing: 16pt, ..sec.sections.map(sub =>
      (c.sub-block)(sub.at("title", default: ""), body-of(c, sub))))
  } else if kind == "text" {
    text(font: c.theme.body, size: 11pt, fill: c.theme.ink)[#sec.at("text", default: "")]
  } else {
    text(font: c.theme.body, size: 10pt, fill: c.theme.muted)[(unrenderable section: #kind)]
  }
}

// --- one top-level section (wrapped in a panel) -----------------------------
#let render-section(c, sec) = {
  (c.section)(
    sec.at("title", default: ""),
    body-of(c, sec),
    descriptor: sec.at("descriptor", default: none),
  )
}

// --- whole report body ------------------------------------------------------
#let render-body(c, sections) = {
  for (i, sec) in sections.enumerate() {
    if i > 0 { v(16pt) }
    render-section(c, sec)
  }
}
