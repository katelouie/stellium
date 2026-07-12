# TODO

*43 open tasks (synced from Obsidian)*

## High

- Fix broad exception swallowing (30+ bare except clauses)
- Resolve Comparison vs MultiChart API duality
- Zodiacal Releasing engine rewrite (parameterized, preset-based) `in-progress`

## Normal

- Add cities gazetteer to webapp for geocoding reliability and autocomplete
- Add eclipse Saros series and prenatal eclipse lookup
- Aspects on by default in ChartBuilder (fix empty-aspects footgun). DECIDED approach A: ChartBuilder.calculate() computes aspects by default via a default aspect engine (ModernAspectEngine), with an opt-out (e.g. .with_aspects(enabled=False) or a calculate flag) for batch/analysis where aspects aren't needed. Today calculate() without an explicit .with_aspects(engine) yields chart.aspects==[] silently, so report AspectSection/aspectarian/cross-aspects/aspect-patterns render nothing. Own branch off main. Watch for tests that assume empty aspects; run full suite. Surfaced during the PDF Typst revamp.
- BaZi Annual pillars (流年)
- BaZi Luck pillars calculation
- BaZi: Clashes, combinations, and penalties
- Build plugin ecosystem architecture (Phase 3 of VISION)
- DX: surface silent None returns from component-dependent accessors
- Dispositor graph in PDF: fix residual glyph tofu + make themeable. (1) A few planet glyphs (e.g. Mercury U+263F) still tofu in the embedded graphviz SVG when rendered inside the full report, though the SAME glyphs render fine in the main PDF (Typst-native) and when the dispositor SVG is compiled bare. Diagnosis: a Typst quirk resolving certain glyph codepoints from an embedded <text> SVG inside a multi-font document — NOT a font-coverage issue (bundled Noto Sans Symbols has them). Options: rasterize the dispositor to PNG at generation (graphviz cairo bakes glyphs, Typst embeds pixels, no font resolution) OR redraw the graph natively in the Typst design system. (2) Themeable (#10): render_dispositor_graph hardcodes a cream/beige/gold palette (bgcolor #F5F0E6 etc.) so it clashes on the dark Celestial/Blues PDF themes — parametrize colors or draw in-PDF. The in-PDF redraw would solve both at once but needs graph layout. File: src/stellium/engines/dispositors.py render_dispositor_graph.
- Evaluate component/analyzer support for non-ChartBuilder chart types
- Fix aspect-pattern over-counting on conjunct points
- Gauquelin sectors as an analysis primitive (gauquelin_sector) + Mars-effect study on notables DB
- Implement Firdaria timing technique
- Implement Vedic dignities engine (moolatrikona, Dig Bala, Navamsa)
- Implement Vimshottari Dasha system
- Implement interactive HTML reports (Jinja2 + Pico.css)
- Integrate Simplified Chinese translation strings into main library and web
- LMT (Local Mean Time) support for historical charts
- Optimize 'stellium cache info' — get_stats() walks the whole cache dir (slow/hangs on large caches)
- Structure-first section contract
- Update ARCHITECTURE.md directory structure to match codebase
- Update COMPETITIVE_ANALYSIS.md — house exports done, re-evaluate gaps
- Update chart grid to accept arbitrary wheel-only charts
- Uranian dial chart info header
- Uranian midpoint calculation (planetary pictures)

## Low

- AI tool definitions for LLM function-calling integration
- Add OFL license file for bundled Noto fonts. assets/fonts/ now bundles NotoSansSymbols-Regular + NotoSansSymbols2-Regular (Open Font License). Add the OFL.txt / license text alongside them for compliance. Also decide whether to keep or remove the extra untracked Noto weight variants + variable font Kate dropped in (only the two Regulars are used/committed).
- Astrological weather API (daily dignities, VOC Moon, planetary hours)
- Build research platform (hypothesis testing, batch analysis)
- Cross-tradition chart synthesis (Western + Vedic + Chinese unified view)
- Hygiea silently absent from CalculationConfig.comprehensive()
- Reconcile Carl Jung notable record (time + data quality)
- Refactor SectionData to sealed dataclass hierarchy
- Topocentric parallax corrections
- Update ARCHITECTURE.md — significantly out of date
- Uranian: Modulus 90 sort for reports
- Zi Wei Dou Shu - 12 palace system
- Zi Wei Dou Shu - Star enums and metadata
- Zi Wei Dou Shu - Star position calculations
- Zi Wei Dou Shu - Transformations and timing charts
