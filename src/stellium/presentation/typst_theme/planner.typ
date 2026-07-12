// ============================================================================
// planner.typ — entry point for the planner, sibling to report.typ.
//
// Reads `theme` and `data` (a JSON path) from sys.inputs, resolves the theme,
// binds both component vocabularies (the shared report one + the planner's
// calendar additions), and lays out: title, front matter, then the year.
//
//   typst compile planner.typ --input theme=house --input data=data.json out.pdf
//
// The front matter reuses the report's section kinds wholesale — a planner's
// reference pages are tables, key-value grids, planet tables and embedded SVGs,
// which components.typ already speaks. Only `year_overview` and `glyph_key` are
// planner-native. Pagination is driven from the data (`new_page`), so Python can
// pack the reference pages densely rather than spending a sheet per chart.
// ============================================================================

#import "palettes.typ": resolve-theme
#import "components.typ": make
#import "planner_components.typ": make-planner
#import "engine.typ": body-of

#let theme-name = sys.inputs.at("theme", default: "house")
#let data-path = sys.inputs.at("data", default: "data.json")
#let data = json(data-path)

#let c = make(resolve-theme(theme-name))
#let p = make-planner(c)
#let meta = data.meta

// Blueprint / graph-paper page background, for themes that opt in.
#let pg = c.theme.at("page-grid", default: none)
#let page-background = if pg != none {
  let gc = rgb(pg)
  rect(
    width: 100%,
    height: 100%,
    stroke: none,
    fill: tiling(size: (16pt, 16pt))[
      #place(line(start: (0pt, 0pt), end: (16pt, 0pt), stroke: 0.35pt + gc))
      #place(line(start: (0pt, 0pt), end: (0pt, 16pt), stroke: 0.35pt + gc))
    ],
  )
} else { none }

// A planner is printed and bound, so the gutter is a real margin, not decoration.
#let bind-margin = meta.at("binding_margin", default: 0.0)
#let page-margin = if bind-margin > 0.0 {
  (inside: (0.7 + bind-margin) * 1in, outside: 0.6in, y: 0.6in)
} else {
  (x: 0.6in, y: 0.6in)
}

#set page(
  paper: meta.at("page_size", default: "us-letter"),
  margin: page-margin,
  binding: if bind-margin > 0.0 { left } else { auto },
  fill: c.theme.bg,
  background: page-background,
  header: (c.header)(
    meta.at("running_left", default: ""),
    meta.at("running_right", default: ""),
  ),
  footer: (c.footer)(meta.at("footer", default: c.theme.label)),
)

#set text(
  font: (c.theme.body, "Noto Sans Symbols", "Noto Sans Symbols 2"),
  size: 10pt,
  fill: c.theme.ink,
)
#set par(leading: 0.7em)

// --- dispatch ---------------------------------------------------------------
// The planner's own kinds first, then fall through to the shared report engine.

#let planner-body-of(sec) = {
  let kind = sec.at("kind", default: "table")
  if kind == "year_overview" {
    (p.year-overview)(sec.at("months", default: ()))
  } else if kind == "glyph_key" {
    (p.glyph-key)(sec.at("groups", default: ()))
  } else {
    body-of(c, sec)
  }
}

#let render-front-section(sec) = (c.section)(
  sec.at("title", default: ""),
  planner-body-of(sec),
  descriptor: sec.at("descriptor", default: none),
)

// --- title page -------------------------------------------------------------

#align(center + horizon)[
  #(c.star-ornament)()
  #v(10pt)
  #text(
    font: c.theme.display,
    size: 34pt,
    weight: c.theme.at("display-weight", default: 600),
    tracking: c.theme.at("display-tracking", default: 0pt) + 0.04em,
    fill: c.theme.accent,
  )[#meta.at("name", default: "Astrological Planner")]

  #v(4pt)
  #text(
    font: c.theme.display,
    size: 15pt,
    tracking: 0.22em,
    fill: c.theme.muted,
  )[#upper(str(meta.at("year", default: "")))]

  #v(12pt)
  #(c.metadata-line)(meta.at("metadata", default: ()))
  #v(14pt)
  #(c.star-ornament)()
]

// --- front matter -----------------------------------------------------------
// The reference section. Ordered "this year -> your chart -> how to read it",
// which is the order a planner is actually consulted in.

#for sec in data.at("front", default: ()) {
  if sec.at("new_page", default: true) { pagebreak() } else { v(14pt) }
  render-front-section(sec)
}

// --- the year ---------------------------------------------------------------
// Each month: a calendar grid, then that month's weeks as writable day pages.

#for month in data.at("months", default: ()) {
  pagebreak()
  (p.month-grid)(month)

  for week in month.at("weeks_detail", default: ()) {
    pagebreak()
    (p.week-page)(week)
  }
}
