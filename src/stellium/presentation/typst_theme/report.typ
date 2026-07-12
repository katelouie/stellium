// ============================================================================
// report.typ — entry point. Reads `theme` and `data` (a JSON path) from
// sys.inputs, resolves the theme, binds the component vocabulary, sets the page
// frame + base text, and lays out the report.
//
//   typst compile report.typ --input theme=house --input data=data.json out.pdf
// ============================================================================

#import "palettes.typ": resolve-theme
#import "components.typ": make
#import "engine.typ": render-title, render-body

#let theme-name = sys.inputs.at("theme", default: "house")
#let data-path = sys.inputs.at("data", default: "data.json")
#let data = json(data-path)
#let c = make(resolve-theme(theme-name))

// Optional blueprint / graph-paper grid on the page background (visible only
// where the opaque section panels don't cover it). Themes opt in via `page-grid`.
#let pg = c.theme.at("page-grid", default: none)
#let page-background = if pg != none {
  let gc = rgb(pg)
  rect(
    width: 100%, height: 100%, stroke: none,
    fill: tiling(size: (16pt, 16pt))[
      #place(line(start: (0pt, 0pt), end: (16pt, 0pt), stroke: 0.35pt + gc))
      #place(line(start: (0pt, 0pt), end: (0pt, 16pt), stroke: 0.35pt + gc))
    ],
  )
} else { none }

#set page(
  paper: "us-letter",
  margin: (x: 0.7in, y: 0.7in),
  fill: c.theme.bg,
  background: page-background,
  header: (c.header)(
    data.meta.at("running_left", default: ""),
    data.meta.at("running_right", default: ""),
  ),
  footer: (c.footer)(data.meta.at("footer", default: c.theme.label)),
)

#set text(
  font: (c.theme.body, "Noto Sans Symbols", "Noto Sans Symbols 2"),
  size: 11pt,
  fill: c.theme.ink,
)
#set par(leading: 0.72em)

#render-title(c, data.meta)
#pagebreak()
#render-body(c, data.sections)
