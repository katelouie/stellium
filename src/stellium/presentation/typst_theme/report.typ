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

#set page(
  paper: "us-letter",
  margin: (x: 0.7in, y: 0.7in),
  fill: c.theme.bg,
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
