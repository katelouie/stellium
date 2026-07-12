// ============================================================================
// planner_components.typ — the calendar surfaces.
//
// The report's component vocabulary (components.typ) already covers everything
// the planner's *reference* pages need: cards, key-value grids, tables, planet
// tables, embedded SVGs. What it has no analogue for is the planner's reason to
// exist — the calendar itself. Three components live here:
//
//   month-grid     a month as a 7-column calendar, events packed into day cells
//   week-page      a week as seven writable day boxes
//   year-overview  twelve mini-months, for "where am I in the year"
//
// Same factory pattern as components.typ: `make-planner(c)` closes over the
// bound report vocabulary (and therefore the theme) and returns the planner's
// additions. Typst can't call dict-stored functions with method syntax, so
// callers destructure.
// ============================================================================

#import "glyphs.typ": aspect-glyph-of, planet-glyph-of, sign-glyph-of

#let make-planner(c) = {
  let t = c.theme

  // Laser themes get outlines instead of ink fills, so the calendar stays
  // printable on a home laser printer — which is where planners actually end up.
  let laser = t.at("laser", default: false)
  let zebra = t.at("zebra", default: t.panel)
  let gridline = t.at("grid", default: t.rule)

  // --- weekday header band --------------------------------------------------
  let weekday-cell(name) = block(
    width: 100%,
    inset: (x: 4pt, y: 3.5pt),
    fill: if laser { none } else { t.accent },
    stroke: if laser { 0.5pt + t.ink } else { none },
    align(
      center,
      text(
        font: t.display,
        size: 8pt,
        weight: 600,
        tracking: 0.08em,
        fill: if laser { t.ink } else { t.bg },
        upper(name),
      ),
    ),
  )

  // --- how much is this event about *you*? ----------------------------------
  // A packed day is unreadable when every line is the same ink. Colour encodes
  // relevance, not category, so the eye can trkiage a cell without reading it:
  // what touches your natal chart pops in the theme's accent, sky landmarks
  // (eclipses, stations, lunations) take gold, plain sky events sit in ink, and
  // the Moon's constant housekeeping recedes into muted grey.
  //
  // Comes from the theme's own event palette (palettes.typ). It deliberately does
  // NOT reuse accent/ink: in most themes those are neighbouring dark tones, so a
  // natal transit would not separate from a plain sky event — which is the whole
  // job. `natal` gets a real hue shift away from the body text.
  let ec = t.at(
    "event-colors",
    default: (natal: t.accent, notable: t.gold, mundane: t.ink, lunar: t.muted),
  )
  let event-color(cls) = ec.at(cls, default: ec.mundane)

  // --- one event line inside a month cell -----------------------------------
  // Tight by necessity: a busy day can carry eight of these. Time is muted so
  // the glyph — the thing you scan for — carries the contrast.
  let month-event(ev) = block(
    width: 100%,
    spacing: 0pt,
    text(size: 5.5pt, fill: event-color(ev.at("class", default: "mundane")))[
      #text(fill: t.muted)[#ev.at("time", default: "")]
      #h(2pt)
      #ev.at("symbol", default: "")
    ],
  )

  // --- one day cell in the month grid ---------------------------------------
  let month-cell(day) = {
    let in-month = day.at("in_month", default: true)
    let events = day.at("events", default: ())
    let marked = day.at("mark", default: none)

    block(
      width: 100%,
      height: 100%,
      inset: 4pt,
      fill: if not in-month { zebra } else { none },
      stack(
        spacing: 2pt,
        // Day number, with an accent disc when something big lands here
        // (an eclipse, a station) so the eye finds it without reading.
        if marked != none and not laser {
          box(
            fill: t.gold,
            radius: 50%,
            inset: (x: 3.5pt, y: 1.5pt),
            text(font: t.display, size: 8.5pt, weight: 700, fill: t.bg)[#day.day],
          )
        } else {
          text(
            font: t.display,
            size: 9pt,
            weight: if marked != none { 700 } else { 500 },
            fill: if in-month { t.ink } else { t.muted },
          )[#day.day]
        },
        ..events.map(month-event),
      ),
    )
  }

  // --- a month as a calendar page -------------------------------------------
  // Laid out as a grid, not a stack: the week rows are `1fr` so they divide the
  // page evenly, and `1fr` only resolves against a parent with a known height. In
  // a stack it has nothing to divide and the table runs off the page.
  let month-grid(month) = {
    let weeks = month.at("weeks", default: ())

    block(
      width: 100%,
      height: 100%,
      grid(
        rows: (auto, 1fr),
        row-gutter: 10pt,
        align(
          center,
          text(
            font: t.display,
            size: 20pt,
            weight: t.at("display-weight", default: 600),
            tracking: 0.06em,
            fill: t.accent,
          )[#upper(month.name) #month.at("year", default: "")],
        ),
        table(
          columns: (1fr,) * 7,
          rows: (auto, ..(1fr,) * weeks.len()),
          stroke: 0.4pt + gridline,
          inset: 0pt,
          align: left + top,
          ..month.at("weekdays", default: ()).map(weekday-cell),
          ..weeks.flatten().map(month-cell),
        ),
      ),
    )
  }

  // --- one day box on a week page -------------------------------------------
  // Unlike the month cell, this is meant to be *written in*: the events sit at
  // the top and the rest of the box is deliberately empty space.
  let week-day-box(day) = {
    let events = day.at("events", default: ())
    let is-past = not day.at("in_range", default: true)

    block(
      width: 100%,
      height: 1fr,
      inset: (x: 8pt, y: 6pt),
      fill: if is-past { zebra } else { none },
      stroke: 0.5pt + t.rule,
      radius: 2pt,
      stack(
        spacing: 4pt,
        // weekday | day number
        grid(
          columns: (1fr, auto),
          align: (left + horizon, right + horizon),
          text(
            font: t.display,
            size: 10pt,
            weight: 500,
            tracking: 0.1em,
            fill: t.muted,
          )[#upper(day.weekday)],
          text(font: t.display, size: 13pt, weight: 700, fill: t.accent)[#day.day],
        ),
        line(length: 100%, stroke: 0.4pt + t.hair),
        if events.len() == 0 {
          text(size: 7pt, style: "italic", fill: t.muted)[No events]
        } else {
          stack(
            spacing: 2.5pt,
            ..events.map(ev => text(
              size: 7pt,
              fill: event-color(ev.at("class", default: "mundane")),
            )[
              #text(fill: t.muted, size: 6.5pt)[#ev.at("time", default: "")]
              #h(4pt)
              #ev.at("description", default: "")
            ]),
          )
        },
      ),
    )
  }

  // --- a week as a page of writable day boxes -------------------------------
  // Same reason as month-grid: the seven boxes share the page height via `1fr`,
  // which needs a parent that knows how tall it is.
  let week-page(week) = {
    let days = week.at("days", default: ())

    block(
      width: 100%,
      height: 100%,
      grid(
        rows: (auto, 1fr),
        row-gutter: 8pt,
        align(
          center,
          text(
            font: t.display,
            size: 13pt,
            weight: 600,
            tracking: 0.08em,
            fill: t.accent,
          )[#upper(week.label)],
        ),
        grid(
          rows: (1fr,) * days.len(),
          row-gutter: 5pt,
          ..days.map(week-day-box),
        ),
      ),
    )
  }

  // --- a mini month, for the year overview ----------------------------------
  let mini-month(month) = {
    let marks = month.at("marks", default: (:))

    let mini-day(day) = {
      if day == 0 {
        // padding cell outside the month
        text(size: 5.5pt)[ ]
      } else {
        let key = str(day)
        let marked = marks.at(key, default: none)
        align(
          center,
          if marked != none {
            box(
              fill: if laser { none } else { t.gold },
              stroke: if laser { 0.4pt + t.ink } else { none },
              radius: 50%,
              inset: (x: 1.6pt, y: 0.8pt),
              text(
                size: 5.5pt,
                weight: 700,
                fill: if laser { t.ink } else { t.bg },
              )[#day],
            )
          } else {
            text(size: 5.5pt, fill: t.ink)[#day]
          },
        )
      }
    }

    block(
      width: 100%,
      inset: 5pt,
      stack(
        spacing: 3pt,
        align(
          center,
          text(font: t.display, size: 8.5pt, weight: 600, fill: t.accent)[
            #upper(month.name)
          ],
        ),
        table(
          columns: (1fr,) * 7,
          stroke: none,
          inset: 1pt,
          align: center,
          ..month
            .at("weekday_initials", default: ())
            .map(d => text(size: 5pt, fill: t.muted, weight: 600)[#d]),
          ..month.at("weeks", default: ()).flatten().map(mini-day),
        ),
      ),
    )
  }

  // --- the whole year, twelve mini-months ------------------------------------
  let year-overview(months) = table(
    columns: (1fr,) * 3,
    stroke: 0.4pt + t.hair,
    inset: 2pt,
    ..months.map(mini-month),
  )

  // --- glyph key ------------------------------------------------------------
  // A report spells things out in prose and never needs this. A planner's daily
  // pages are dense glyph shorthand, so the key is load-bearing.
  let glyph-key(groups) = {
    // Wide enough for a word-shaped key like "VOC", not just a single glyph.
    let entry(item) = grid(
      columns: (30pt, 1fr),
      column-gutter: 4pt,
      align: (center + horizon, left + horizon),
      text(size: 10pt, fill: t.accent)[#item.at("glyph", default: "")],
      text(size: 8pt, fill: t.ink)[#item.at("label", default: "")],
    )

    // The colour code needs a *coloured* sample, not a glyph — showing the ink
    // itself is the whole point of that group.
    let swatch-entry(item) = {
      let c = event-color(item.at("class", default: "mundane"))
      grid(
        columns: (30pt, 1fr),
        column-gutter: 4pt,
        align: (center + horizon, left + horizon),
        text(size: 9pt, fill: c)[#sym.circle.filled],
        text(size: 8pt, fill: c)[#item.at("label", default: "")],
      )
    }

    let group(g) = block(
      width: 100%,
      breakable: false,
      stack(
        spacing: 5pt,
        text(
          font: t.display,
          size: 9pt,
          weight: 600,
          tracking: 0.1em,
          fill: t.muted,
        )[#upper(g.at("title", default: ""))],
        line(length: 100%, stroke: 0.4pt + t.hair),
        ..g
          .at("items", default: ())
          .map(item => if g.at("swatches", default: false) {
            swatch-entry(item)
          } else {
            entry(item)
          }),
      ),
    )

    grid(
      columns: (1fr,) * 3,
      column-gutter: 14pt,
      row-gutter: 14pt,
      ..groups.map(group),
    )
  }

  (
    month-grid: month-grid,
    week-page: week-page,
    year-overview: year-overview,
    glyph-key: glyph-key,
  )
}
