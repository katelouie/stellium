// ============================================================================
// glyphs.typ — the shared glyph system.
//
// All astrology symbols render in Noto Sans Symbols 2 forced to *text*
// presentation via the variation selector U+FE0E, so zodiac signs and planets
// never fall back to colour-emoji. The JSON content layer carries semantic
// NAMES ("Sun", "Pisces", "Trine"); mapping a name to its codepoint is a
// presentation concern and lives here, theme-independent.
// ============================================================================

#let symbol-font = "Noto Sans Symbols 2"

// Render an already-chosen glyph character in the symbol font, text-presentation.
#let glyph(ch, size: 1em, fill: none) = {
  let body = [#ch#"\u{FE0E}"]
  if fill == none {
    text(font: symbol-font, size: size)[#body]
  } else {
    text(font: symbol-font, size: size, fill: fill)[#body]
  }
}

// --- Name -> codepoint maps ---------------------------------------------------

#let planet-glyphs = (
  "Sun": "\u{2609}", "Moon": "\u{263D}", "Mercury": "\u{263F}",
  "Venus": "\u{2640}", "Mars": "\u{2642}", "Jupiter": "\u{2643}",
  "Saturn": "\u{2644}", "Uranus": "\u{2645}", "Neptune": "\u{2646}",
  "Pluto": "\u{2647}",
  "North Node": "\u{260A}", "South Node": "\u{260B}",
  "True Node": "\u{260A}", "Mean Node": "\u{260A}",
  "Chiron": "\u{26B7}", "Lilith": "\u{26B8}", "Mean Lilith": "\u{26B8}",
  "Black Moon Lilith": "\u{26B8}",
  "Ceres": "\u{26B3}", "Pallas": "\u{26B4}", "Juno": "\u{26B5}",
  "Vesta": "\u{26B6}",
  "Part of Fortune": "\u{2297}", "Part of Spirit": "\u{2297}",
)

#let sign-glyphs = (
  "Aries": "\u{2648}", "Taurus": "\u{2649}", "Gemini": "\u{264A}",
  "Cancer": "\u{264B}", "Leo": "\u{264C}", "Virgo": "\u{264D}",
  "Libra": "\u{264E}", "Scorpio": "\u{264F}", "Sagittarius": "\u{2650}",
  "Capricorn": "\u{2651}", "Aquarius": "\u{2652}", "Pisces": "\u{2653}",
)

#let aspect-glyphs = (
  "Conjunction": "\u{260C}", "Opposition": "\u{260D}",
  "Trine": "\u{25B3}", "Square": "\u{25A1}", "Sextile": "\u{26B9}",
  "Quincunx": "\u{26BB}", "Inconjunct": "\u{26BB}",
  "Semi-Sextile": "\u{26BA}", "Semisextile": "\u{26BA}",
)

// Aspect name -> colour key (into palettes.typ aspect-colors). Minor/hard
// aspects borrow the nearest major's colour family.
#let aspect-color-keys = (
  "Conjunction": "conjunction", "Opposition": "opposition",
  "Trine": "trine", "Square": "square", "Sextile": "sextile",
  "Quincunx": "square", "Inconjunct": "square",
  "Semi-Sextile": "sextile", "Semisextile": "sextile",
  "Semi-Square": "square", "Sesquiquadrate": "square",
)

// --- Safe lookups (fall back to the name if we have no glyph) ------------------
#let planet-glyph-of(name) = planet-glyphs.at(name, default: none)
#let sign-glyph-of(name) = sign-glyphs.at(name, default: none)
#let aspect-glyph-of(name) = aspect-glyphs.at(name, default: none)
#let aspect-key-of(name) = aspect-color-keys.at(name, default: "conjunction")
