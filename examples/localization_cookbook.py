#!/usr/bin/env python3
"""
Localization Cookbook - Rendering Stellium in Other Languages

Localizing a chart or report is **two independent knobs**, and it helps to keep
them separate in your head:

1. **Locale** - *which words* appear. ``with_locale("zh_CN")`` translates the
   text: section names, headers, house-system names, dates, and known astrology
   terms (planets, signs, aspects). The wheel body itself - planet/sign/aspect
   *glyphs* - is language-neutral and never changes.

2. **Fonts** - *whether the words render*. A Latin-only machine has no glyph for
   Chinese characters, so a localized chart comes out as "tofu" boxes unless a
   font that covers the script is available. Stellium bundles Latin + the
   astrological symbols; other scripts ship as downloadable **font packs**
   (``stellium fonts download zh``). Once a pack is installed, setting a locale
   in that script wires the font in automatically - no code change.

So: locale picks the language; fonts make it legible. You can set a locale with
no font pack (a browser viewing the SVG will substitute its own system font, and
PNG/PDF will warn), but for portable PNGs and PDFs you want the matching pack.

Run this script to generate example output in examples/localization/

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/localization_cookbook.py

For full documentation, see docs/VISUALIZATION.md and docs/REPORTS.md.

Note: PDF/PNG generation requires Typst (brew install typst or https://typst.app).
"""

import os
from pathlib import Path

from stellium import ChartBuilder, ReportBuilder, fonts
from stellium.i18n import get_available_locales

SCRIPT_DIR = Path(__file__).resolve().parent
# Overridable so a test-suite / docs-build run does not rewrite committed artifacts.
OUTPUT_ROOT = Path(os.environ.get("STELLIUM_EXAMPLE_OUTPUT", SCRIPT_DIR))
OUTPUT_DIR = OUTPUT_ROOT / "localization"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# The locale we demonstrate throughout. Simplified Chinese ("zh_CN") is covered by
# the "zh" font pack; Traditional ("zh_Hant_TW") by "zh-hant".
LOCALE = "zh_CN"


def section_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


# =============================================================================
# PART 1: THE LOCALE METHOD - which words appear
# =============================================================================


def example_1_available_locales():
    """
    Example 1: What locales exist?

    ``get_available_locales()`` lists the locale codes with a translation file.
    Anything not listed falls back to English term by term (never an error).
    """
    section_header("Example 1: Available Locales")
    print("Locales with translations:", get_available_locales())
    print("\nPass any of these to .with_locale(...) on a chart or a report.")


def example_2_localized_chart_svg():
    """
    Example 2: A localized chart SVG

    ``with_locale`` translates the header/info words; the wheel glyphs are
    language-neutral. An SVG is happy in a browser even without a font pack
    (the browser substitutes a system CJK font).
    """
    section_header("Example 2: Localized Chart SVG")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    svg_file = OUTPUT_DIR / f"einstein_{LOCALE}.svg"
    (
        chart.draw()
        .preset_detailed()  # wheel + header + info corners + moon phase
        .with_locale(LOCALE)
        .with_filename(str(svg_file))
        .save()
    )
    print(f"Wrote {svg_file}")
    print("Open it in a browser - the labels are localized, the glyphs unchanged.")


def example_3_localized_chart_png():
    """
    Example 3: A localized chart PNG

    PNG is rasterized by Typst using *only* bundled + installed-pack fonts (never
    the host's), so the image is identical on every machine. That is exactly why
    the font pack matters here: no covering pack -> tofu (and a warning).
    """
    section_header("Example 3: Localized Chart PNG")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    png_file = OUTPUT_DIR / f"einstein_{LOCALE}.png"
    (
        chart.draw()
        .preset_detailed()
        .with_locale(LOCALE)
        .with_filename(str(png_file.with_suffix(".svg")))
        .save_png(str(png_file), scale=2.0, background="white")
    )
    print(f"Wrote {png_file}")

    script = fonts.locale_script(LOCALE)
    if script and not fonts.is_installed(script):
        print(
            f"\nNote: font pack '{script}' is not installed, so the CJK text may be "
            f"tofu. See Part 2 / `stellium fonts download {script}`."
        )


def example_4_localized_report_pdf():
    """
    Example 4: A localized report PDF

    The same ``with_locale`` on ``ReportBuilder``. The embedded chart image is
    localized to match. The bundled font stack + any installed pack travels
    inside the PDF, so it renders the same anywhere.
    """
    section_header("Example 4: Localized Report PDF")

    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()

    pdf_file = OUTPUT_DIR / f"einstein_report_{LOCALE}.pdf"
    (
        ReportBuilder()
        .from_chart(chart)
        .with_chart_image()
        .with_chart_overview()
        .with_planet_positions(include_house=True)
        .with_aspects(mode="major")
        .with_locale(LOCALE)
        .render(format="pdf", file=str(pdf_file))
    )
    print(f"Wrote {pdf_file}")


# =============================================================================
# PART 2: THE FONTS METHOD - whether the words render
# =============================================================================


def example_5_inspect_font_packs():
    """
    Example 5: What font packs exist, and what's installed?

    All read-only - no network. ``list_packs()`` describes each pack (the scripts
    it covers, the faces it carries) and whether it is already installed.
    """
    section_header("Example 5: Inspect Font Packs")

    for script, info in fonts.list_packs().items():
        state = "installed" if info["installed"] else "not installed"
        print(f"  {script:8s} [{state}]  covers: {info['covers']}")

    print("\nCLI equivalents:")
    print("  stellium fonts list")
    print("  stellium fonts download zh")


def example_6_download_a_pack():
    """
    Example 6: Install the pack a locale needs

    ``locale_script`` maps a locale to the pack that covers it; ``download_pack``
    fetches it into ~/.stellium/fonts/ (auto-discovered thereafter). This recipe
    only downloads if the pack is missing AND you opt in via
    STELLIUM_DOWNLOAD_FONTS=1, so the cookbook stays offline-friendly by default.
    """
    section_header("Example 6: Download a Font Pack")

    script = fonts.locale_script(LOCALE)
    print(f"Locale {LOCALE!r} needs font pack: {script!r}")

    if script is None:
        print("This locale's script is covered by the bundled fonts - nothing to do.")
        return

    if fonts.is_installed(script):
        print(f"Pack '{script}' is already installed. Nothing to do.")
        return

    if os.environ.get("STELLIUM_DOWNLOAD_FONTS") == "1":
        print(f"Downloading '{script}' ...")
        target = fonts.download_pack(script, on_progress=lambda msg: print(f"  {msg}"))
        print(f"Installed to {target}")
    else:
        print(
            f"Not installed. Run `stellium fonts download {script}` (or set "
            f"STELLIUM_DOWNLOAD_FONTS=1 and re-run) to fetch it."
        )


def example_7_detect_missing_fonts():
    """
    Example 7: Will this text render? (pre-flight check)

    ``missing_font_packs(text, locale)`` returns the packs you'd need to render a
    given string - a cheap pre-flight before committing to a PNG/PDF, so you can
    prompt the user to install rather than silently ship tofu.
    """
    section_header("Example 7: Detect Missing Fonts")

    sample = "太阳在双子座"  # "Sun in Gemini" (zh_CN)
    missing = fonts.missing_font_packs(sample, locale=LOCALE)
    if missing:
        print(f"To render this text you still need pack(s): {missing}")
        print(
            "Install with:  "
            + "  ".join(f"stellium fonts download {m}" for m in missing)
        )
    else:
        print("All fonts needed for this text are available - safe to render.")


def example_8_explicit_font():
    """
    Example 8: Force a specific font (bypass the packs)

    For a face you keep outside the pack system, ``with_font(path)`` points the
    chart at a file or a directory directly - its family leads the SVG text stack
    and its directory joins the PNG/PDF font search path.
    """
    section_header("Example 8: Explicit Font Override")

    print("Illustrative - point with_font() at a real .ttf/.otf or a font directory:")
    print(
        """
    (chart.draw()
        .preset_detailed()
        .with_locale("zh_CN")
        .with_font("/path/to/NotoSansSC-Regular.otf")
        .with_filename("chart.svg")
        .save_png("chart.png"))
    """
    )


def main():
    """Run the cookbook."""
    print("\n" + "=" * 60)
    print("  STELLIUM LOCALIZATION COOKBOOK")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Demonstrating locale: {LOCALE}\n")

    # --- Part 1: The locale method (which words) ---
    example_1_available_locales()
    example_2_localized_chart_svg()
    example_3_localized_chart_png()
    example_4_localized_report_pdf()

    # --- Part 2: The fonts method (whether they render) ---
    example_5_inspect_font_packs()
    example_6_download_a_pack()
    example_7_detect_missing_fonts()
    example_8_explicit_font()

    print("\n" + "=" * 60)
    print("  COOKBOOK COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files are in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
