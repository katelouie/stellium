"""Render a planner to PDF via the bundled Typst design system.

The planner used to build its Typst as Python f-strings with a hardcoded purple
palette. It now does what the report does: serialise to a JSON contract and let
the design system (``presentation/typst_theme/``) decide how it looks. Colour,
type and layout live in the ``.typ`` files; Python supplies structured data and a
theme name.

That buys the planner all five themes, the bundled font stack (so a plain
``pip install`` renders identical PDFs — the old renderer pointed at repo-root
fonts that never shipped in the wheel), and the shared glyph/component vocabulary.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import date

from stellium.planner.almanac import (
    build_year_almanac,
    find_chart_condition,
    find_natal_transits,
)
from stellium.planner.contract import build_planner_data
from stellium.planner.events import DailyEventCollector
from stellium.presentation.typst_runtime import TypstDocument, require_typst


@dataclass
class _Svgs:
    """SVG markup for the front matter's chart slots."""

    natal: str | None = None
    ephemeris: str | None = None
    solar_return: str | None = None
    profections: str | None = None
    zr: str | None = None

    def as_dict(self) -> dict[str, str]:
        slots = {
            "natal": self.natal,
            "ephemeris": self.ephemeris,
            "solar_return": self.solar_return,
            "profections": self.profections,
            "zr": self.zr,
        }
        return {key: value for key, value in slots.items() if value}


class PlannerRenderer:
    """Turns a PlannerConfig into PDF bytes."""

    def __init__(self, config) -> None:
        self.config = config

    # -- lifecycle ----------------------------------------------------------

    def render(self) -> bytes:
        """Build the planner and compile it to PDF bytes."""
        require_typst()  # fail before building charts, not after

        theme = getattr(self.config, "theme", "house")
        start, end = self._date_range()

        # One chart, built once, carrying everything downstream needs. The old
        # renderer built the natal chart three separate times.
        natal_chart = self._build_natal_chart()

        # One transit search, shared by the daily pages and the year's summary.
        transits = find_natal_transits(
            natal_chart,
            start,
            end,
            self.config.timezone,
            transit_planets=self.config.natal_transit_planets,
        )

        events_by_date = self._collect_events(natal_chart, start, end)
        almanac = build_year_almanac(
            natal_chart,
            start,
            end,
            self.config.timezone,
            lot=self.config.zr_lot,
            transits=transits,
        )

        svgs = self._generate_svgs(natal_chart, theme, start)

        data = build_planner_data(
            natal_chart,
            almanac,
            events_by_date,
            name=self._name(natal_chart),
            theme=theme,
            page_size=self.config.page_size,
            binding_margin=self.config.binding_margin,
            week_starts_on=self.config.week_starts_on,
            weekly_starts_on=getattr(self.config, "weekly_starts_on", None),
            time_format=getattr(self.config, "time_format", "12h"),
            location_label=self._location_label(natal_chart),
            include_natal=self.config.include_natal_chart,
            svgs=svgs.as_dict(),
            transit_planets=self._legend_planets(),
            condition=find_chart_condition(natal_chart),
        )

        return self._compile(data, theme)

    def _location_label(self, natal_chart) -> str | None:
        """Where the planner's event times are local to.

        A planner is used where you *live*, which need not be where you were born,
        so ``.location()`` overrides the birth place for this line (and for casting
        the solar return). Falls back to the birth location.
        """
        location = self.config.location
        if isinstance(location, str) and location.strip():
            return location.strip()
        if isinstance(location, tuple):
            return f"{location[0]:.4f}, {location[1]:.4f}"
        return getattr(natal_chart.location, "name", None) or None

    # -- inputs -------------------------------------------------------------

    def _date_range(self) -> tuple[date, date]:
        if self.config.start_date and self.config.end_date:
            return self.config.start_date, self.config.end_date
        year = self.config.year or date.today().year
        return date(year, 1, 1), date(year, 12, 31)

    def _name(self, natal_chart) -> str:
        name = natal_chart.metadata.get("name")
        if name:
            return str(name)
        native_name = getattr(self.config.native, "name", None)
        return str(native_name) if native_name else "Astrological Planner"

    def _legend_planets(self) -> list[str]:
        """Everything that can appear on a daily page, so the key covers it."""
        return [
            "Sun",
            "Moon",
            "Mercury",
            "Venus",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
            "Pluto",
        ]

    def _build_natal_chart(self):
        """The natal chart, with the analyzers the front matter needs."""
        from stellium.core.builder import ChartBuilder
        from stellium.engines.releasing import ZodiacalReleasingAnalyzer

        builder = ChartBuilder.from_native(self.config.native)
        if self.config.include_zr_timeline:
            # ZR lives in analyzer metadata; without this the timeline is absent.
            builder = builder.add_analyzer(
                ZodiacalReleasingAnalyzer([self.config.zr_lot])
            )
        return builder.calculate()

    def _collect_events(self, natal_chart, start: date, end: date) -> dict[date, list]:
        collector = DailyEventCollector(
            natal_chart=natal_chart,
            start=start,
            end=end,
            timezone=self.config.timezone,
        )
        collector.collect_all(
            transit_planets=self.config.natal_transit_planets,
            # This flag existed on PlannerConfig from the start but was never
            # honoured — there was no mundane collector for it to switch on.
            mundane_transits=self.config.include_mundane_transits,
            ingress_planets=self.config.ingress_planets,
            station_planets=self.config.station_planets,
            moon_phases=self.config.include_moon_phases,
            voc=self.config.include_voc,
            voc_mode=self.config.voc_mode,
        )

        events: dict[date, list] = {}
        for event in collector.get_all_events():
            events.setdefault(event.time.date(), []).append(event)
        return events

    # -- drawings -----------------------------------------------------------

    def _themed(self, draw, theme: str):
        """Apply the report's themed-wheel treatment.

        The old planner embedded wheels with their own headers, info corners and
        opaque white backgrounds, then framed them in a hardcoded gold box. Here
        they get stripped and composited onto the themed panel, exactly as the
        report's wheels are.
        """
        from stellium.presentation.typst_render import THEME_WHEEL

        # The moon-phase corner is a portrait flourish; in a planner the Moon's
        # phase is already on every daily page where it actually matters.
        draw = (
            draw.without_header()
            .without_chart_info()
            .without_moon_phase()
            .with_transparent_background()
        )

        viz_theme, zodiac_palette, aspect_palette = THEME_WHEEL.get(
            theme, (None, None, None)
        )
        if viz_theme is not None:
            draw = draw.with_theme(viz_theme).with_zodiac_palette(zodiac_palette)
            if aspect_palette is not None:
                draw = draw.with_aspect_palette(aspect_palette)
        return draw

    def _generate_svgs(self, natal_chart, theme: str, start: date) -> _Svgs:
        svgs = _Svgs()

        if self.config.include_natal_chart:
            svgs.natal = self._safe_svg(
                lambda: self._wheel_svg(natal_chart, theme),
                "natal chart",
            )

        if self.config.include_solar_return:
            svgs.solar_return = self._safe_svg(
                lambda: self._solar_return_svg(natal_chart, theme, start),
                "solar return",
            )

        if self.config.include_profections:
            svgs.profections = self._safe_svg(
                lambda: self._section_svg("profections", natal_chart),
                "profections",
            )

        if self.config.include_zr_timeline:
            svgs.zr = self._safe_svg(
                lambda: self._section_svg("zr", natal_chart),
                "zodiacal releasing",
            )

        if self.config.include_graphic_ephemeris:
            svgs.ephemeris = self._safe_svg(
                lambda: self._ephemeris_svg(natal_chart, start),
                "graphic ephemeris",
            )

        return svgs

    def _safe_svg(self, make, what: str) -> str | None:
        """A drawing that fails must not take the whole planner down with it.

        It must not fail *silently* either — a missing page should say so.
        """
        import warnings

        try:
            return make()
        except Exception as exc:
            warnings.warn(
                f"Planner: could not draw the {what} page ({exc}); skipping it.",
                RuntimeWarning,
                stacklevel=2,
            )
            return None

    def _wheel_svg(self, chart, theme: str) -> str:
        import tempfile as _tf

        with _tf.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "wheel.svg")
            self._themed(chart.draw(path).preset_standard(), theme).save()
            with open(path, encoding="utf-8") as fh:
                return fh.read()

    def _solar_return_svg(self, natal_chart, theme: str, start: date) -> str:
        from stellium.returns import ReturnBuilder

        # A relocated solar return: cast for where the native will *be*, if they
        # said. `ReturnBuilder.solar` has always taken this; the planner just never
        # passed it, so `.location()` was silently doing nothing.
        chart = ReturnBuilder.solar(
            natal_chart, year=start.year, location=self.config.location
        ).calculate()
        return self._wheel_svg(chart, theme)

    def _section_svg(self, which: str, natal_chart) -> str:
        """Reuse the presentation layer's visualization sections for SVG markup."""
        if which == "zr":
            from stellium.presentation.sections.zr_visualization import (
                ZRVisualizationSection,
            )

            section = ZRVisualizationSection(lot=self.config.zr_lot)
        else:
            from stellium.presentation.sections.profection_visualization import (
                ProfectionVisualizationSection,
            )

            section = ProfectionVisualizationSection()

        svg = self._first_svg(section.generate_data(natal_chart))
        if not svg:
            raise ValueError(f"the {which} section produced no SVG")
        return svg

    def _first_svg(self, payload) -> str | None:
        """Pull SVG markup out of a section payload.

        These sections return either a bare ``{"type": "svg", "content": ...}`` or a
        compound of ``(name, payload)`` pairs, so walk whichever arrived.
        """
        if isinstance(payload, dict):
            if payload.get("type") == "svg" and payload.get("content"):
                return payload["content"]
            for _name, sub in payload.get("sections", []):
                found = self._first_svg(sub)
                if found:
                    return found
        return None

    def _ephemeris_svg(self, natal_chart, start: date) -> str:
        from stellium.visualization.ephemeris import GraphicEphemeris

        harmonic = self.config.graphic_ephemeris_harmonic
        if harmonic not in (360, 90, 45):
            harmonic = 90

        ephemeris = GraphicEphemeris(
            start_date=date(start.year, 1, 1),
            end_date=date(start.year, 12, 31),
            harmonic=harmonic,
            natal_chart=natal_chart,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ephemeris.svg")
            ephemeris.draw(path).save()
            with open(path, encoding="utf-8") as fh:
                return fh.read()

    # -- compile ------------------------------------------------------------

    def _compile(self, data: dict, theme: str) -> bytes:
        """Hand the contract to the shared Typst runtime.

        The temp-dir/copy-design-system/materialise-SVGs/compile dance is identical
        to the report's, so it lives in one place now (typst_runtime.TypstDocument).
        The planner only has to name the extra component module it brings.
        """
        with TypstDocument(
            "planner.typ",
            theme,
            extra_templates=("planner_components.typ",),
            prefix="stellium_planner_",
        ) as doc:
            return doc.render(data, svg_sections=data.get("front", []))
