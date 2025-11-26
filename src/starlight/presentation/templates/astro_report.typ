// Starlight Astrology Report Template
// Beautiful typography for professional-quality PDF output

// ============================================================================
// PAGE SETUP
// ============================================================================
#set page(
  paper: "us-letter",
  margin: (top: 1in, bottom: 1in, left: 1in, right: 1in),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 9pt, fill: rgb("#666666"))
      #h(1fr)
      _Astrological Report_
      #h(1fr)
    ]
  },
  footer: context {
    set text(size: 9pt, fill: rgb("#666666"))
    h(1fr)
    counter(page).display("1")
    h(1fr)
  },
)

// ============================================================================
// TYPOGRAPHY
// ============================================================================
#set text(
  font: "New Computer Modern",
  size: 11pt,
  hyphenate: true,
)

#set par(
  justify: true,
  leading: 0.8em,
)

// Headings
#show heading.where(level: 1): it => {
  set text(size: 24pt, weight: "bold", fill: rgb("#1a365d"))
  set par(justify: false)
  v(0.5em)
  it.body
  v(0.3em)
  line(length: 100%, stroke: 1pt + rgb("#3182ce"))
  v(0.5em)
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "semibold", fill: rgb("#2d3748"))
  set par(justify: false)
  v(1em)
  it.body
  v(0.3em)
}

// ============================================================================
// TABLE STYLING
// ============================================================================
#let styled-table(headers, rows) = {
  table(
    columns: headers.len(),
    stroke: none,
    align: (col, row) => if col == 0 { left } else { center },
    inset: (x: 8pt, y: 6pt),
    fill: (col, row) => {
      if row == 0 { rgb("#edf2f7") }
      else if calc.odd(row) { rgb("#f7fafc") }
      else { white }
    },
    // Header row
    ..headers.map(h => [*#h*]),
    // Data rows
    ..rows.flatten(),
  )
}

// ============================================================================
// KEY-VALUE STYLING
// ============================================================================
#let styled-kv(data) = {
  set text(size: 10.5pt)
  for (key, value) in data {
    grid(
      columns: (120pt, 1fr),
      gutter: 8pt,
      [*#key:*], [#value]
    )
    v(2pt)
  }
}

// ============================================================================
// CHART SVG DISPLAY
// ============================================================================
#let chart-display(svg-path) = {
  align(center)[
    #box(
      stroke: 1pt + rgb("#e2e8f0"),
      radius: 4pt,
      clip: true,
      image(svg-path, width: 85%)
    )
  ]
}

// ============================================================================
// TEMPLATE VARIABLES (replaced at render time)
// ============================================================================
// These get replaced by the Python renderer:
// {{TITLE}} - Report title
// {{CHART_SVG}} - Path to chart SVG or "none"
// {{SECTIONS}} - Generated section content
