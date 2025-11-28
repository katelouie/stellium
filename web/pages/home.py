"""
Stellium Web - Home/Landing Page
"""

from components.header import create_header, create_nav
from config import COLORS
from nicegui import ui


def create_home_page():
    """Create the home/landing page."""

    create_header()
    create_nav()

    # Hero section
    with (
        ui.element("section")
        .classes("w-full py-20 px-6")
        .style(f"background-color: {COLORS['cream_dark']};")
    ):
        with ui.element("div").classes("w-full max-w-4xl mx-auto text-center"):
            # Star divider
            ui.label("★  ☆  ★").classes("text-xl mb-6").style(
                f"color: {COLORS['gold']}"
            )

            # Headline
            ui.label("Computational Astrology").classes(
                "font-display text-4xl md:text-5xl lg:text-6xl tracking-wide mb-2"
            ).style(f"color: {COLORS['text']}")
            ui.label("for the Modern Era").classes(
                "font-display text-3xl md:text-4xl lg:text-5xl tracking-wide mb-8"
            ).style(f"color: {COLORS['secondary']}")

            # Subtitle
            ui.label(
                "Professional-grade astrological calculations with NASA-level accuracy. "
                "Beautiful visualizations. Completely free."
            ).classes("text-xl max-w-2xl mx-auto mb-10 leading-relaxed").style(
                f"color: {COLORS['text_muted']}"
            )

            # CTA buttons
            with ui.row().classes("gap-4 justify-center"):
                ui.button(
                    "Create Your Chart", on_click=lambda: ui.navigate.to("/natal")
                ).classes("px-8 py-4 text-base tracking-wide rounded").style(
                    f"background-color: {COLORS['primary']} !important; color: white !important;"
                )

                ui.button(
                    "Explore Celebrity Charts",
                    on_click=lambda: ui.navigate.to("/explore"),
                ).classes("px-8 py-4 text-base tracking-wide rounded").props("outline").style(
                    f"color: {COLORS['primary']} !important; border-color: {COLORS['primary']} !important;"
                )

    # Features section
    with (
        ui.element("section")
        .classes("w-full py-16 px-6")
        .style(f"background-color: {COLORS['cream']}")
    ):
        with ui.element("div").classes("w-full max-w-5xl mx-auto"):
            # Section header
            with (
                ui.element("div")
                .classes("mb-12 py-4 px-6 text-center rounded")
                .style(f"background-color: {COLORS['primary']}; color: white;")
            ):
                ui.label("☆  FEATURES").classes(
                    "font-display text-base tracking-[0.15em]"
                ).style("color: white; font-weight: 700;")

            # Feature cards - CSS Grid for multi-column layout
            ui.add_head_html("""
                <style>
                    .feature-grid {
                        display: grid !important;
                        grid-template-columns: repeat(1, 1fr);
                        gap: 1.5rem;
                    }
                    @media (min-width: 768px) {
                        .feature-grid {
                            grid-template-columns: repeat(2, 1fr);
                        }
                    }
                    @media (min-width: 1024px) {
                        .feature-grid {
                            grid-template-columns: repeat(3, 1fr);
                        }
                    }
                </style>
            """)

            with ui.element("div").classes("feature-grid"):
                features = [
                    # Row 1: Core chart features
                    (
                        "★",
                        "23+ House Systems",
                        "Placidus, Whole Sign, Koch, Equal, and more. Calculate multiple systems simultaneously.",
                    ),
                    (
                        "★",
                        "Sidereal & Tropical",
                        "Both zodiac systems with 9 ayanamsas for Vedic astrology including Lahiri and Raman.",
                    ),
                    (
                        "★",
                        "Essential Dignities",
                        "Traditional and modern rulerships, exaltations, triplicities, terms, and faces.",
                    ),
                    # Row 2: Predictive techniques
                    (
                        "★",
                        "Synastry & Bi-Wheels",
                        "Relationship charts, transits, progressions, composite, and Davison charts.",
                    ),
                    (
                        "★",
                        "Solar & Lunar Returns",
                        "Birthday charts, monthly lunar returns, Saturn returns. Relocate to any city.",
                    ),
                    (
                        "★",
                        "Secondary Progressions",
                        "Day-for-a-year timing with quotidian, solar arc, and Naibod angle methods.",
                    ),
                    # Row 3: Advanced features
                    (
                        "★",
                        "Fixed Stars",
                        "26 stars including the Royal Stars of Persia: Aldebaran, Regulus, Antares, Fomalhaut.",
                    ),
                    (
                        "★",
                        "Declinations & OOB",
                        "Equatorial coordinates with automatic out-of-bounds planet detection.",
                    ),
                    (
                        "★",
                        "Aspect Patterns",
                        "Grand Trines, T-Squares, Yods, Stelliums, Grand Crosses, and more.",
                    ),
                    # Row 4: Output & extras
                    (
                        "★",
                        "Arabic Parts",
                        "25+ traditional lots including Fortune, Spirit, and Love. Sect-aware calculations.",
                    ),
                    (
                        "★",
                        "Midpoints",
                        "Full midpoint analysis for Cosmobiology and Uranian astrology techniques.",
                    ),
                    (
                        "★",
                        "Beautiful Reports",
                        "Export professional PDF reports and SVG charts with 13 gorgeous themes.",
                    ),
                ]

                for star, title, desc in features:
                    with (
                        ui.element("div")
                        .classes("p-6 text-center")
                        .style(
                            f"border: 1px solid {COLORS['border']}; border-radius: 0.5rem;"
                        )
                    ):
                        ui.label(star).classes("text-2xl mb-3").style(
                            f"color: {COLORS['gold']}"
                        )
                        ui.label(title).classes("font-display text-lg mb-2").style(
                            f"color: {COLORS['text']}"
                        )
                        ui.label(desc).classes("text-base leading-relaxed").style(
                            f"color: {COLORS['text_muted']}"
                        )

    # Powered by section
    with (
        ui.element("section")
        .classes("w-full py-12 px-6")
        .style(f"background-color: {COLORS['cream_dark']};")
    ):
        with ui.element("div").classes("w-full max-w-3xl mx-auto text-center"):
            ui.label("Powered by the Stellium Python Library").classes(
                "font-display text-xl mb-4"
            ).style(f"color: {COLORS['text']}")

            ui.label(
                "Everything you see here is built on Stellium, a free and open-source "
                "Python library for computational astrology. Use it in your own projects!"
            ).classes("text-base mb-6").style(f"color: {COLORS['text_muted']}")

            ui.link(
                "View on GitHub →",
                "https://github.com/katelouie/stellium",
                new_tab=True,
            ).classes("text-base no-underline").style(f"color: {COLORS['gold']}")

    # Footer
    with (
        ui.element("footer")
        .classes("w-full py-6 px-6 border-t")
        .style(
            f"border-color: {COLORS['border']}; background-color: {COLORS['cream']};"
        )
    ):
        with ui.element("div").classes("w-full max-w-5xl mx-auto text-center"):
            ui.label("★  Generated with Stellium  ★").classes("text-sm").style(
                f"color: {COLORS['text_muted']}"
            )
