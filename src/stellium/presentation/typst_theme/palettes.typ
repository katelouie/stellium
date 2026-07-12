// ============================================================================
// palettes.typ — the VALUE layer of the Stellium PDF design system.
//
// One report architecture, five interchangeable themes. A theme is nothing but
// data: 8 colour tokens + a display/body/mono font trio + a sign-tint palette +
// a `laser` boolean. Layout, glyphs and components (components.typ) are shared
// across every theme — nothing structural changes between them.
//
// Escalation ladder (see the mockup-to-typst skill): every theme difference here
// is a scalar token or a boolean, never a structural skin. `laser` is the one
// boolean branch — it flips discs/chips/badges from filled to 1.4pt outlines.
// ============================================================================

// --- Global constants: SHARED by every theme (not theme tokens) --------------

// Aspect colour code — keyed to each theme so the PDF aspect glyphs match the
// chart wheel's aspect palette (values mirror visualization/palettes.py:
// classic/sepia/celestial/midnight/greyscale).
#let theme-aspect-colors = (
  house: (conjunction: "#34495E", sextile: "#27AE60", square: "#F39C12", trine: "#3498DB", opposition: "#E74C3C"),
  sepia: (conjunction: "#654321", sextile: "#D2691E", square: "#8B4513", trine: "#CD853F", opposition: "#A0522D"),
  celestial: (conjunction: "#FFD700", sextile: "#DDA0DD", square: "#BA55D3", trine: "#9370DB", opposition: "#DA70D6"),
  blues: (conjunction: "#FFD700", sextile: "#00CED1", square: "#FFA500", trine: "#4169E1", opposition: "#DC143C"),
  greyscale: (conjunction: "#333333", sextile: "#666666", square: "#555555", trine: "#777777", opposition: "#444444"),
)

// Calendar event colours, keyed by how much the event is about *you*:
//
//   natal    touches your natal chart — the reason you own the planner
//   notable  a landmark in the sky (eclipse, station, lunation)
//   mundane  everything else happening in the sky
//   lunar    the Moon's housekeeping (ingresses, void-of-course) — recedes
//
// These cannot just reuse `accent` / `ink`: in most themes those are neighbouring
// dark tones, so `natal` would not separate from `mundane` — which is the entire
// job. `natal` therefore gets a deliberate *hue* shift away from the body text,
// the way a good almanac prints your transits in blue against the sky's black.
// Greyscale has no hue to spend, so it separates by value and nothing else.
#let theme-event-colors = (
  house: (natal: "#1F6F8B", notable: "#B0872F", mundane: "#3A2233", lunar: "#A08A72"),
  sepia: (natal: "#2E6171", notable: "#9B7343", mundane: "#3A2A1A", lunar: "#9A7A52"),
  celestial: (natal: "#7FC7D9", notable: "#FFD700", mundane: "#D8D3E0", lunar: "#8A82A0"),
  blues: (natal: "#7FE3D4", notable: "#FFD700", mundane: "#CFE3F2", lunar: "#6E8FA8"),
  greyscale: (natal: "#111111", notable: "#444444", mundane: "#777777", lunar: "#AAAAAA"),
)

// Polarity bar: a warm (yang) / cool (yin) pair that stays distinct in every
// theme (gold==accent in Celestial, so we can't reuse those). laser -> greys.
#let polarity-colors = (yang: rgb("#CE9A34"), yin: rgb("#5E7E9C"))

// Element / modality bar colours — semantic constants shared across colour
// themes (laser mode overrides bars to muted grey in components.typ).
#let element-colors = (
  Fire: rgb("#C6612F"), Earth: rgb("#B0872F"),
  Air: rgb("#9B8BC4"), Water: rgb("#5B9BB5"),
)

// Modalities get their own three distinct hues (cardinal = initiating warm,
// fixed = steady deep, mutable = adaptable green).
#let modality-colors = (
  Cardinal: rgb("#BC5A46"), Fixed: rgb("#6B4C7A"), Mutable: rgb("#4A9B6E"),
)

// Zodiac order — structural (theme-independent). Used to index a sign-tint
// palette by sign name.
#let sign-order = (
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

// --- Sign-tint palettes: one 12-colour ramp per wheel palette -----------------
// The disc behind a planet glyph is tinted by the planet's sign.
#let sign-palettes = (
  rainbow: (
    "#E8B4B8", "#E8C4B8", "#E8D8B8", "#E8E8B8", "#D8E8B8", "#C4E8B8",
    "#B8E8C4", "#B8E8D8", "#B8D8E8", "#B8C4E8", "#C4B8E8", "#D8B8E8",
  ),
  sepia: (
    "#eadfc8", "#e3d4ba", "#dccaad", "#d4bf9f", "#cdb592", "#c6aa84",
    "#bfa077", "#b89569", "#b18b5c", "#a9804e", "#a27641", "#9b6b33",
  ),
  celestial: (
    "#e3d6f5", "#dacbef", "#d0c0e8", "#c7b6e2", "#bdabdc", "#b4a0d5",
    "#aa95cf", "#a18ac8", "#977fc2", "#8e75bc", "#846ab5", "#7b5faf",
  ),
  blues: (
    "#d6e9fa", "#c7dcf0", "#b7d0e7", "#a8c3dd", "#99b7d3", "#8aaac9",
    "#7a9ec0", "#6b91b6", "#5c85ac", "#4d78a2", "#3d6c99", "#2e5f8f",
  ),
  greyscale: (
    "#ededed", "#e9e9e9", "#e5e5e5", "#e1e1e1", "#dddddd", "#d9d9d9",
    "#d4d4d4", "#d0d0d0", "#cccccc", "#c8c8c8", "#c4c4c4", "#c0c0c0",
  ),
)

// --- Themes: 8 tokens + fonts + sign palette + laser flag ---------------------
// Colours are hex strings here; resolve-theme() lifts them to rgb() and attaches
// the shared constants. Every theme declares the SAME keys (schema discipline):
// a missing key in one theme is a bug, not a default to paper over.
// `zebra` = the alternating table-row shade, keyed to each theme: a subtle
// variant of the panel (a touch darker on light panels, a touch lighter on dark).
// `grid` = the aspectarian cell-stroke, a mid-tone visible on light AND dark.
#let themes = (
  house: (
    bg: "#FAF8F6", ink: "#3A2233", accent: "#47283F", gold: "#B0872F",
    muted: "#A08A72", rule: "#D8CBB6", hair: "#ECE4D6", panel: "#FFFFFF",
    zebra: "#F4EFE7", grid: "#C9B79E",
    display: "Cormorant Garamond", body: "EB Garamond", mono: "IBM Plex Mono",
    display-tracking: 0pt, display-weight: 600,
    signs: "rainbow", laser: false, label: "House Style",
  ),
  sepia: (
    bg: "#F2E8D5", ink: "#3A2A1A", accent: "#8B5A2B", gold: "#9B7343",
    muted: "#9A7A52", rule: "#B8A07A", hair: "#DDCEB0", panel: "#FBF5E9",
    zebra: "#F3E9D3", grid: "#B49A72",
    display: "Newsreader", body: "EB Garamond", mono: "IBM Plex Mono",
    display-tracking: 0pt, display-weight: 600,
    signs: "sepia", laser: false, label: "Sepia",
  ),
  celestial: (
    bg: "#17111F", ink: "#D9C9F2", accent: "#E8B44A", gold: "#E8B44A",
    muted: "#8B7BB0", rule: "#E8B44A", hair: "#3A2A55", panel: "#1F1730",
    zebra: "#2A2142", grid: "#4E3F68",
    display: "Cinzel", body: "Spectral", mono: "IBM Plex Mono",
    display-tracking: 0.06em, display-weight: 600,
    signs: "celestial", laser: false, label: "Celestial",
  ),
  blues: (
    bg: "#0A2A44", ink: "#DCEFFF", accent: "#BFE3FF", gold: "#8FC3EE",
    muted: "#7FB2D8", rule: "#BFE3FF", hair: "#123A5A", panel: "#10375A",
    zebra: "#16466E", grid: "#3E6E96",
    display: "Space Grotesk", body: "Space Grotesk", mono: "IBM Plex Mono",
    display-tracking: 0pt, display-weight: 600,
    signs: "blues", laser: false, label: "Blues", page-grid: "#123A5A",
  ),
  greyscale: (
    bg: "#FFFFFF", ink: "#1B1B1B", accent: "#1B1B1B", gold: "#6A6A6A",
    muted: "#8A8A8A", rule: "#1B1B1B", hair: "#DDD8CF", panel: "#FFFFFF",
    zebra: "#EFEFEF", grid: "#B8B8B8",
    display: "IBM Plex Serif", body: "IBM Plex Serif", mono: "IBM Plex Mono",
    display-tracking: 0pt, display-weight: 600,
    signs: "greyscale", laser: true, label: "Greyscale",
  ),
)

// resolve-theme(name) -> a ready-to-use theme dict with rgb() colours, the
// resolved sign-tint ramp, and the theme's aspect + polarity + bar colours.
#let resolve-theme(name) = {
  let t = themes.at(name, default: themes.house)
  let color-keys = (
    "bg", "ink", "accent", "gold", "muted", "rule", "hair", "panel", "zebra", "grid",
  )
  let out = (:)
  for (k, v) in t {
    out.insert(k, if color-keys.contains(k) { rgb(v) } else { v })
  }
  let asp = theme-aspect-colors.at(name, default: theme-aspect-colors.house)
  out.insert("sign-tints", sign-palettes.at(t.signs).map(rgb))
  out.insert(
    "aspect-colors",
    (
      conjunction: rgb(asp.conjunction), sextile: rgb(asp.sextile),
      square: rgb(asp.square), trine: rgb(asp.trine), opposition: rgb(asp.opposition),
    ),
  )
  let ev = theme-event-colors.at(name, default: theme-event-colors.house)
  out.insert(
    "event-colors",
    (
      natal: rgb(ev.natal), notable: rgb(ev.notable),
      mundane: rgb(ev.mundane), lunar: rgb(ev.lunar),
    ),
  )
  out.insert("polarity-colors", polarity-colors)
  out.insert("element-colors", element-colors)
  out.insert("modality-colors", modality-colors)
  out.insert("sign-order", sign-order)
  out
}
