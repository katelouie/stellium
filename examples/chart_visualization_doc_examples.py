"""Code to generate the charts for docs/VISUALIZATION.md"""

import os

from starlight import ChartBuilder, ComparisonBuilder, ComparisonType
from starlight.engines import PlacidusHouses, WholeSignHouses

FILEDIR = "docs/images"

# Registry for chart functions
_chart_functions = []


def chart(func):
    """Decorator to register chart generation functions"""
    _chart_functions.append(func)
    return func


@chart
def readme_top_chart():
    filename = "examples/readme_first.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing = (
        drawing.with_zodiac_palette("rainbow")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
    )
    drawing.save()


@chart
def readme_chart():
    filename = "examples/readme_einstein.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.save()


@chart
def readme_chart_2():
    filename = "examples/readme_einstein_celestial.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing = (
        drawing.with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
    )
    drawing.save()


@chart
def readme_chart_3():
    filename = "examples/readme_extended_detailed.svg"
    chart = (
        ChartBuilder.from_notable("Albert Einstein")
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .with_aspects()
        .calculate()
    )
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing = (
        drawing.with_theme("midnight")
        .preset_detailed()
        .with_house_systems("all")
        .with_tables()
        .save()
    )


@chart
def viz_chart_minimal():
    filename = "examples/viz_minimal.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_minimal().save()


@chart
def viz_chart_standard():
    filename = "examples/viz_standard.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_standard().save()


@chart
def viz_chart_detailed():
    filename = "examples/viz_detailed.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.preset_detailed().save()


@chart
def viz_chart_midnight():
    filename = "examples/viz_midnight.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("midnight").save()


@chart
def viz_chart_celestial():
    filename = "examples/viz_celestial.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("celestial").save()


@chart
def viz_chart_neon():
    filename = "examples/viz_neon.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("neon").save()


@chart
def viz_chart_celestial_more():
    filename = "examples/viz_celestial_more.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    (
        drawing.with_theme("celestial")
        .with_zodiac_palette("rainbow_celestial")
        .with_moon_phase(position="bottom-left", show_label=True)
        .with_chart_info(position="top-left")
        .with_aspect_counts(position="top-right")
        .save()
    )


@chart
def gallery_chart_classic_grey():
    filename = "gallery/classic_grey.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("classic").save()


@chart
def gallery_chart_classic_rainbow():
    filename = "gallery/classic_rainbow.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("classic").with_zodiac_palette("rainbow").save()


@chart
def gallery_chart_classic_elemental():
    filename = "gallery/classic_elemental.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("classic").with_zodiac_palette("elemental").save()


@chart
def gallery_chart_dark_grey():
    filename = "gallery/dark_grey.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("dark").save()


@chart
def gallery_chart_dark_rainbow():
    filename = "gallery/dark_rainbow.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("dark").with_zodiac_palette("rainbow").save()


@chart
def gallery_chart_dark_viridis():
    filename = "gallery/dark_viridis.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("dark").with_zodiac_palette("viridis").save()


@chart
def gallery_chart_midnight_rainbow_midnight():
    filename = "gallery/midnight_rainbow_midnight.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("midnight").with_zodiac_palette("rainbow_midnight").save()


@chart
def gallery_chart_midnight_grey():
    filename = "gallery/midnight_grey.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("midnight").save()


@chart
def gallery_chart_celestial_rainbow_celestial():
    filename = "gallery/celestial_rainbow_celestial.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("celestial").with_zodiac_palette("rainbow_celestial").save()


@chart
def gallery_chart_celestial_magma():
    filename = "gallery/celestial_magma.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("celestial").with_zodiac_palette("magma").save()


@chart
def gallery_chart_neon_rainbow_neon():
    filename = "gallery/neon_rainbow_neon.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("neon").with_zodiac_palette("rainbow_neon").save()


@chart
def gallery_chart_neon_turbo():
    filename = "gallery/neon_turbo.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("neon").with_zodiac_palette("turbo").save()


@chart
def gallery_chart_sepia_grey():
    filename = "gallery/sepia_grey.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("sepia").save()


@chart
def gallery_chart_sepia_elemental():
    filename = "gallery/sepia_elemental.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("sepia").with_zodiac_palette("rainbow_sepia").save()


@chart
def gallery_chart_pastel_grey():
    filename = "gallery/pastel_grey.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("pastel").with_zodiac_palette("grey").save()


@chart
def gallery_chart_pastel_rainbow():
    filename = "gallery/pastel_rainbow.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("pastel").with_zodiac_palette("rainbow").save()


@chart
def gallery_chart_viridis():
    filename = "gallery/viridis.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("viridis").save()


@chart
def gallery_chart_plasma():
    filename = "gallery/plasma.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("plasma").save()


@chart
def gallery_chart_inferno():
    filename = "gallery/inferno.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("inferno").save()


@chart
def gallery_chart_magma():
    filename = "gallery/magma.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("magma").save()


@chart
def gallery_chart_cividis():
    filename = "gallery/cividis.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("cividis").save()


@chart
def gallery_chart_turbo():
    filename = "gallery/turbo.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("turbo").save()


# @chart
def viz_synastry_1():
    filename = "examples/synastry_1.svg"
    chart1 = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    chart2 = ChartBuilder.from_notable("Oprah Winfrey").with_aspects().calculate()
    comparison = (
        ComparisonBuilder.from_native(chart1, native_label="Albert Einstein")
        .with_partner(chart2, partner_label="Oprah Winfrey")
        .calculate()
    )
    drawing = comparison.draw(os.path.join(FILEDIR, filename))
    drawing.preset_synastry().with_theme("celestial").save()


@chart
def examples_chart_extended():
    filename = "examples/extended.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_tables().save()


@chart
def examples_chart_extended_left_midnight():
    filename = "examples/extended_left_midnight.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("midnight").with_tables("left").save()


@chart
def examples_chart_extended_below_no_aspect():
    filename = "examples/extended_below_no_aspect.svg"
    chart = ChartBuilder.from_notable("Albert Einstein").with_aspects().calculate()
    drawing = chart.draw(os.path.join(FILEDIR, filename))
    drawing.with_theme("celestial").with_tables("below", show_aspectarian=False).save()


def main():
    """Execute all registered chart functions"""
    for func in _chart_functions:
        print(f"Generating {func.__name__}...")
        func()


if __name__ == "__main__":
    main()
