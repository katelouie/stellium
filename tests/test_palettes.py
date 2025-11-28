"""
Comprehensive tests for visualization palette system.

This test suite covers:
- ZodiacPalette: Zodiac wheel color palettes (12 colors per sign)
- AspectPalette: Aspect line color palettes
- PlanetGlyphPalette: Planet glyph color palettes
- Color utilities: hex conversion, luminance, contrast ratio, adaptive coloring
"""

import pytest

from stellium.visualization.palettes import (
    PLANET_ELEMENTS,
    PLANET_TYPES,
    SIGN_ELEMENTS,
    SIGN_MODALITIES,
    AspectPalette,
    PlanetGlyphPalette,
    ZodiacPalette,
    adjust_color_for_contrast,
    get_aspect_palette_colors,
    get_aspect_palette_description,
    get_contrast_ratio,
    get_luminance,
    get_palette_colors,
    get_palette_description,
    get_planet_glyph_color,
    get_planet_glyph_palette_description,
    get_sign_info_color,
    hex_to_rgb,
    rgb_to_hex,
)

# ============================================================================
# ZODIAC PALETTE TESTS
# ============================================================================


class TestZodiacPalette:
    """Tests for ZodiacPalette enum and get_palette_colors()."""

    def test_zodiac_palette_enum_values(self):
        """Test that all zodiac palette enum values exist."""
        # Base palettes
        assert ZodiacPalette.GREY == "grey"
        assert ZodiacPalette.RAINBOW == "rainbow"
        assert ZodiacPalette.ELEMENTAL == "elemental"
        assert ZodiacPalette.CARDINALITY == "cardinality"

        # Data science palettes
        assert ZodiacPalette.VIRIDIS == "viridis"
        assert ZodiacPalette.PLASMA == "plasma"
        assert ZodiacPalette.INFERNO == "inferno"

    def test_get_palette_colors_returns_12_colors(self):
        """Test that all palettes return exactly 12 colors."""
        for palette in ZodiacPalette:
            colors = get_palette_colors(palette)
            assert len(colors) == 12, f"{palette} should return 12 colors"

    def test_get_palette_colors_returns_hex_strings(self):
        """Test that all colors are valid hex strings."""
        colors = get_palette_colors(ZodiacPalette.RAINBOW)
        for color in colors:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB

    def test_grey_palette_all_same(self):
        """Test that grey palette returns same color for all signs."""
        colors = get_palette_colors(ZodiacPalette.GREY)
        assert all(c == colors[0] for c in colors)
        assert colors[0] == "#EEEEEE"

    def test_elemental_palette_4_colors(self):
        """Test that elemental palette uses 4 distinct colors."""
        colors = get_palette_colors(ZodiacPalette.ELEMENTAL)
        unique_colors = set(colors)
        assert len(unique_colors) == 4  # Fire, Earth, Air, Water

    def test_elemental_palette_matches_sign_elements(self):
        """Test that elemental palette correctly maps signs to elements."""
        colors = get_palette_colors(ZodiacPalette.ELEMENTAL)

        # Fire signs should have same color (Aries, Leo, Sagittarius)
        assert colors[0] == colors[4] == colors[8]  # Fire

        # Earth signs should have same color (Taurus, Virgo, Capricorn)
        assert colors[1] == colors[5] == colors[9]  # Earth

        # Air signs should have same color (Gemini, Libra, Aquarius)
        assert colors[2] == colors[6] == colors[10]  # Air

        # Water signs should have same color (Cancer, Scorpio, Pisces)
        assert colors[3] == colors[7] == colors[11]  # Water

    def test_cardinality_palette_3_colors(self):
        """Test that cardinality palette uses 3 distinct colors."""
        colors = get_palette_colors(ZodiacPalette.CARDINALITY)
        unique_colors = set(colors)
        assert len(unique_colors) == 3  # Cardinal, Fixed, Mutable

    def test_rainbow_palette_all_different(self):
        """Test that rainbow palette has 12 distinct colors."""
        colors = get_palette_colors(ZodiacPalette.RAINBOW)
        assert len(set(colors)) == 12

    def test_palette_caching(self):
        """Test that palette colors are cached (same instance returned)."""
        colors1 = get_palette_colors(ZodiacPalette.VIRIDIS)
        colors2 = get_palette_colors(ZodiacPalette.VIRIDIS)
        # Since it's cached, should be same object
        assert colors1 is colors2

    def test_get_palette_description(self):
        """Test palette description strings."""
        desc = get_palette_description(ZodiacPalette.GREY)
        assert isinstance(desc, str)
        assert len(desc) > 0
        assert "grey" in desc.lower() or "gray" in desc.lower()

    def test_all_palettes_have_descriptions(self):
        """Test that all palettes have descriptions."""
        for palette in ZodiacPalette:
            desc = get_palette_description(palette)
            assert isinstance(desc, str)
            assert len(desc) > 0
            assert desc != "Unknown palette"


# ============================================================================
# ASPECT PALETTE TESTS
# ============================================================================


class TestAspectPalette:
    """Tests for AspectPalette enum and get_aspect_palette_colors()."""

    def test_aspect_palette_enum_values(self):
        """Test that all aspect palette enum values exist."""
        assert AspectPalette.CLASSIC == "classic"
        assert AspectPalette.DARK == "dark"
        assert AspectPalette.NEON == "neon"
        assert AspectPalette.GREYSCALE == "greyscale"

    def test_get_aspect_palette_colors_returns_dict(self):
        """Test that aspect palette returns a dictionary."""
        colors = get_aspect_palette_colors(AspectPalette.CLASSIC)
        assert isinstance(colors, dict)

    def test_aspect_palette_contains_major_aspects(self):
        """Test that all major aspects are in the palette."""
        colors = get_aspect_palette_colors(AspectPalette.CLASSIC)

        # Major aspects
        assert "Conjunction" in colors
        assert "Sextile" in colors
        assert "Square" in colors
        assert "Trine" in colors
        assert "Opposition" in colors

    def test_aspect_palette_contains_minor_aspects(self):
        """Test that minor aspects are in the palette."""
        colors = get_aspect_palette_colors(AspectPalette.CLASSIC)

        # Minor aspects
        assert "Semisextile" in colors
        assert "Semisquare" in colors
        assert "Sesquisquare" in colors
        assert "Quincunx" in colors

    def test_aspect_colors_are_hex_strings(self):
        """Test that all aspect colors are valid hex strings."""
        colors = get_aspect_palette_colors(AspectPalette.CLASSIC)
        for _aspect_name, color in colors.items():
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB

    def test_classic_palette_matches_registry(self):
        """Test that classic palette has expected registry colors."""
        colors = get_aspect_palette_colors(AspectPalette.CLASSIC)

        # Check a few known registry colors
        assert colors["Conjunction"] == "#34495E"
        assert colors["Trine"] == "#3498DB"
        assert colors["Opposition"] == "#E74C3C"

    def test_aspect_palette_caching(self):
        """Test that aspect palette colors are cached."""
        colors1 = get_aspect_palette_colors(AspectPalette.VIRIDIS)
        colors2 = get_aspect_palette_colors(AspectPalette.VIRIDIS)
        assert colors1 is colors2

    def test_get_aspect_palette_description(self):
        """Test aspect palette description strings."""
        desc = get_aspect_palette_description(AspectPalette.CLASSIC)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_all_aspect_palettes_have_descriptions(self):
        """Test that all aspect palettes have descriptions."""
        for palette in AspectPalette:
            desc = get_aspect_palette_description(palette)
            assert isinstance(desc, str)
            assert len(desc) > 0
            assert desc != "Unknown palette"

    def test_greyscale_palette_uses_greys(self):
        """Test that greyscale palette uses only grey colors."""
        colors = get_aspect_palette_colors(AspectPalette.GREYSCALE)

        # All colors should have equal R, G, B values (greyscale)
        for color in colors.values():
            r, g, b = hex_to_rgb(color)
            # For greyscale, R == G == B
            # Allow small tolerance for rounding
            assert abs(r - g) <= 1
            assert abs(g - b) <= 1


# ============================================================================
# PLANET GLYPH PALETTE TESTS
# ============================================================================


class TestPlanetGlyphPalette:
    """Tests for PlanetGlyphPalette enum and get_planet_glyph_color()."""

    def test_planet_palette_enum_values(self):
        """Test that all planet glyph palette enum values exist."""
        assert PlanetGlyphPalette.DEFAULT == "default"
        assert PlanetGlyphPalette.ELEMENT == "element"
        assert PlanetGlyphPalette.RAINBOW == "rainbow"
        assert PlanetGlyphPalette.CHAKRA == "chakra"

    def test_get_planet_glyph_color_default_returns_theme_color(self):
        """Test that DEFAULT palette returns the theme default color."""
        color = get_planet_glyph_color("Sun", PlanetGlyphPalette.DEFAULT, "#ABCDEF")
        assert color == "#ABCDEF"

    def test_get_planet_glyph_color_returns_hex_string(self):
        """Test that planet glyph colors are valid hex strings."""
        color = get_planet_glyph_color("Sun", PlanetGlyphPalette.RAINBOW)
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 7

    def test_element_palette_groups_by_element(self):
        """Test that element palette groups planets by element."""
        # Fire planets: Sun, Mars, Jupiter
        sun_color = get_planet_glyph_color("Sun", PlanetGlyphPalette.ELEMENT)
        mars_color = get_planet_glyph_color("Mars", PlanetGlyphPalette.ELEMENT)
        jupiter_color = get_planet_glyph_color("Jupiter", PlanetGlyphPalette.ELEMENT)
        assert sun_color == mars_color == jupiter_color

        # Water planets: Moon, Neptune, Pluto
        moon_color = get_planet_glyph_color("Moon", PlanetGlyphPalette.ELEMENT)
        neptune_color = get_planet_glyph_color("Neptune", PlanetGlyphPalette.ELEMENT)
        pluto_color = get_planet_glyph_color("Pluto", PlanetGlyphPalette.ELEMENT)
        assert moon_color == neptune_color == pluto_color

    def test_luminaries_palette_special_sun_moon(self):
        """Test that luminaries palette treats Sun and Moon specially."""
        sun_color = get_planet_glyph_color("Sun", PlanetGlyphPalette.LUMINARIES)
        moon_color = get_planet_glyph_color("Moon", PlanetGlyphPalette.LUMINARIES)
        mars_color = get_planet_glyph_color(
            "Mars", PlanetGlyphPalette.LUMINARIES, "#222222"
        )

        # Sun should be gold
        assert sun_color == "#FFD700"

        # Moon should be silver
        assert moon_color == "#C0C0C0"

        # Others should use theme default
        assert mars_color == "#222222"

    def test_rainbow_palette_all_different(self):
        """Test that rainbow palette gives each planet a different color."""
        planets = [
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

        colors = [
            get_planet_glyph_color(p, PlanetGlyphPalette.RAINBOW) for p in planets
        ]

        # All should be different
        assert len(set(colors)) == len(planets)

    def test_planet_type_palette_groups_by_type(self):
        """Test that planet type palette groups by planet type."""
        # Luminaries
        sun_color = get_planet_glyph_color("Sun", PlanetGlyphPalette.PLANET_TYPE)
        moon_color = get_planet_glyph_color("Moon", PlanetGlyphPalette.PLANET_TYPE)
        assert sun_color == moon_color

        # Traditional planets
        mercury_color = get_planet_glyph_color(
            "Mercury", PlanetGlyphPalette.PLANET_TYPE
        )
        venus_color = get_planet_glyph_color("Venus", PlanetGlyphPalette.PLANET_TYPE)
        assert mercury_color == venus_color

        # Modern planets
        uranus_color = get_planet_glyph_color("Uranus", PlanetGlyphPalette.PLANET_TYPE)
        neptune_color = get_planet_glyph_color(
            "Neptune", PlanetGlyphPalette.PLANET_TYPE
        )
        assert uranus_color == neptune_color

    def test_unknown_planet_returns_theme_default(self):
        """Test that unknown planets return theme default color."""
        color = get_planet_glyph_color(
            "UnknownPlanet", PlanetGlyphPalette.ELEMENT, "#123456"
        )
        assert color == "#123456"

    def test_get_planet_glyph_palette_description(self):
        """Test planet glyph palette description strings."""
        desc = get_planet_glyph_palette_description(PlanetGlyphPalette.DEFAULT)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_all_planet_palettes_have_descriptions(self):
        """Test that all planet glyph palettes have descriptions."""
        for palette in PlanetGlyphPalette:
            desc = get_planet_glyph_palette_description(palette)
            assert isinstance(desc, str)
            assert len(desc) > 0
            assert desc != "Unknown palette"


# ============================================================================
# COLOR UTILITY TESTS
# ============================================================================


class TestColorUtilities:
    """Tests for color conversion and manipulation utilities."""

    def test_hex_to_rgb_basic(self):
        """Test hex to RGB conversion."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("#000000") == (0, 0, 0)
        assert hex_to_rgb("#FF0000") == (255, 0, 0)
        assert hex_to_rgb("#00FF00") == (0, 255, 0)
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_hex_to_rgb_without_hash(self):
        """Test hex to RGB conversion without # prefix."""
        assert hex_to_rgb("FFFFFF") == (255, 255, 255)
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_rgb_to_hex_basic(self):
        """Test RGB to hex conversion."""
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"
        assert rgb_to_hex(0, 0, 0) == "#000000"
        assert rgb_to_hex(255, 0, 0) == "#FF0000"
        assert rgb_to_hex(0, 255, 0) == "#00FF00"
        assert rgb_to_hex(0, 0, 255) == "#0000FF"

    def test_hex_rgb_round_trip(self):
        """Test that hex -> RGB -> hex is consistent."""
        test_colors = ["#ABCDEF", "#123456", "#FF00AA", "#888888"]
        for color in test_colors:
            rgb = hex_to_rgb(color)
            hex_result = rgb_to_hex(*rgb)
            assert hex_result.upper() == color.upper()

    def test_get_luminance_extremes(self):
        """Test luminance calculation for black and white."""
        black_lum = get_luminance("#000000")
        white_lum = get_luminance("#FFFFFF")

        assert black_lum == 0.0
        assert white_lum == 1.0

    def test_get_luminance_range(self):
        """Test that luminance is always in 0-1 range."""
        test_colors = ["#FF0000", "#00FF00", "#0000FF", "#808080", "#ABCDEF"]
        for color in test_colors:
            lum = get_luminance(color)
            assert 0.0 <= lum <= 1.0

    def test_get_contrast_ratio_identical_colors(self):
        """Test contrast ratio of identical colors is 1.0."""
        ratio = get_contrast_ratio("#ABCDEF", "#ABCDEF")
        assert ratio == 1.0

    def test_get_contrast_ratio_black_white(self):
        """Test contrast ratio of black and white is 21.0."""
        ratio = get_contrast_ratio("#000000", "#FFFFFF")
        assert abs(ratio - 21.0) < 0.01  # Allow small floating point error

    def test_get_contrast_ratio_symmetric(self):
        """Test that contrast ratio is symmetric."""
        ratio1 = get_contrast_ratio("#FF0000", "#0000FF")
        ratio2 = get_contrast_ratio("#0000FF", "#FF0000")
        assert abs(ratio1 - ratio2) < 0.01

    def test_get_contrast_ratio_range(self):
        """Test that contrast ratio is always >= 1.0."""
        test_pairs = [
            ("#FF0000", "#00FF00"),
            ("#123456", "#ABCDEF"),
            ("#888888", "#444444"),
        ]
        for color1, color2 in test_pairs:
            ratio = get_contrast_ratio(color1, color2)
            assert ratio >= 1.0

    def test_adjust_color_for_contrast_already_sufficient(self):
        """Test that sufficient contrast color is not changed."""
        # Black on white has excellent contrast
        result = adjust_color_for_contrast("#000000", "#FFFFFF", min_contrast=4.5)
        assert result == "#000000"

    def test_adjust_color_for_contrast_light_background(self):
        """Test color adjustment on light background."""
        # Light grey on white has poor contrast, should darken
        result = adjust_color_for_contrast("#CCCCCC", "#FFFFFF", min_contrast=4.5)
        assert result != "#CCCCCC"

        # Result should be darker
        original_lum = get_luminance("#CCCCCC")
        result_lum = get_luminance(result)
        assert result_lum < original_lum

        # Should meet contrast requirement
        ratio = get_contrast_ratio(result, "#FFFFFF")
        assert ratio >= 4.5

    def test_adjust_color_for_contrast_dark_background(self):
        """Test color adjustment on dark background."""
        # Dark grey on black has poor contrast, should lighten
        result = adjust_color_for_contrast("#333333", "#000000", min_contrast=4.5)
        assert result != "#333333"

        # Result should be lighter
        original_lum = get_luminance("#333333")
        result_lum = get_luminance(result)
        assert result_lum > original_lum

        # Should meet contrast requirement
        ratio = get_contrast_ratio(result, "#000000")
        assert ratio >= 4.5

    def test_adjust_color_extreme_fallback(self):
        """Test that extreme adjustment falls back to black or white."""
        # If contrast can't be achieved, should return pure black or white
        result = adjust_color_for_contrast("#808080", "#808080", min_contrast=20.0)
        assert result in ("#000000", "#FFFFFF")

    def test_get_sign_info_color_returns_hex(self):
        """Test that get_sign_info_color returns a hex color."""
        color = get_sign_info_color(0, ZodiacPalette.RAINBOW, "#FFFFFF")
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 7

    def test_get_sign_info_color_meets_contrast(self):
        """Test that sign info color meets contrast requirement."""
        # White background
        color = get_sign_info_color(
            0, ZodiacPalette.RAINBOW, "#FFFFFF", min_contrast=4.5
        )
        ratio = get_contrast_ratio(color, "#FFFFFF")
        assert ratio >= 4.5

        # Black background
        color = get_sign_info_color(
            6, ZodiacPalette.ELEMENTAL, "#000000", min_contrast=4.5
        )
        ratio = get_contrast_ratio(color, "#000000")
        assert ratio >= 4.5

    def test_get_sign_info_color_all_signs(self):
        """Test that get_sign_info_color works for all 12 signs."""
        for sign_index in range(12):
            color = get_sign_info_color(sign_index, ZodiacPalette.RAINBOW, "#FFFFFF")
            assert isinstance(color, str)
            assert color.startswith("#")


# ============================================================================
# SIGN AND PLANET MAPPING TESTS
# ============================================================================


class TestSignAndPlanetMappings:
    """Tests for sign element/modality and planet categorizations."""

    def test_sign_elements_complete(self):
        """Test that all 12 signs have element mappings."""
        assert len(SIGN_ELEMENTS) == 12
        for i in range(12):
            assert i in SIGN_ELEMENTS
            assert SIGN_ELEMENTS[i] in ("fire", "earth", "air", "water")

    def test_sign_elements_pattern(self):
        """Test that sign elements follow the correct pattern."""
        # Fire, Earth, Air, Water repeating pattern
        expected_pattern = ["fire", "earth", "air", "water"] * 3
        actual_pattern = [SIGN_ELEMENTS[i] for i in range(12)]
        assert actual_pattern == expected_pattern

    def test_sign_modalities_complete(self):
        """Test that all 12 signs have modality mappings."""
        assert len(SIGN_MODALITIES) == 12
        for i in range(12):
            assert i in SIGN_MODALITIES
            assert SIGN_MODALITIES[i] in ("cardinal", "fixed", "mutable")

    def test_sign_modalities_pattern(self):
        """Test that sign modalities follow the correct pattern."""
        # Cardinal, Fixed, Mutable repeating pattern
        expected_pattern = ["cardinal", "fixed", "mutable"] * 4
        actual_pattern = [SIGN_MODALITIES[i] for i in range(12)]
        assert actual_pattern == expected_pattern

    def test_planet_elements_has_major_planets(self):
        """Test that planet elements includes all major planets."""
        major_planets = [
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
        for planet in major_planets:
            assert planet in PLANET_ELEMENTS
            assert PLANET_ELEMENTS[planet] in ("fire", "earth", "air", "water")

    def test_planet_types_has_major_planets(self):
        """Test that planet types includes all major planets."""
        major_planets = [
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
        for planet in major_planets:
            assert planet in PLANET_TYPES

    def test_planet_types_categories(self):
        """Test that planet types uses valid categories."""
        valid_types = {
            "luminary",
            "traditional",
            "modern",
            "centaur",
            "asteroid",
            "node",
            "point",
        }
        for planet_type in PLANET_TYPES.values():
            assert planet_type in valid_types

    def test_planet_types_luminaries(self):
        """Test that Sun and Moon are categorized as luminaries."""
        assert PLANET_TYPES["Sun"] == "luminary"
        assert PLANET_TYPES["Moon"] == "luminary"

    def test_planet_types_traditional(self):
        """Test traditional planets categorization."""
        traditional = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for planet in traditional:
            assert PLANET_TYPES[planet] == "traditional"

    def test_planet_types_modern(self):
        """Test modern planets categorization."""
        modern = ["Uranus", "Neptune", "Pluto"]
        for planet in modern:
            assert PLANET_TYPES[planet] == "modern"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestPaletteEdgeCases:
    """Edge case tests for palette system."""

    def test_palette_with_invalid_enum(self):
        """Test behavior with invalid palette enum value."""
        # This should fall back to grey
        with pytest.raises(ValueError, match="not a valid"):
            get_palette_colors("invalid_palette")  # type: ignore

    def test_aspect_palette_fallback(self):
        """Test aspect palette fallback behavior."""
        # Invalid palette should fall back to classic
        colors = get_aspect_palette_colors("invalid")  # type: ignore
        classic_colors = get_aspect_palette_colors(AspectPalette.CLASSIC)
        # Should be same as classic
        assert colors == classic_colors

    def test_color_utilities_with_lowercase_hex(self):
        """Test color utilities work with lowercase hex."""
        assert hex_to_rgb("#ffffff") == (255, 255, 255)
        assert hex_to_rgb("#abcdef") == (171, 205, 239)

    def test_contrast_adjustment_with_custom_min_contrast(self):
        """Test contrast adjustment with various minimum contrast values."""
        # WCAG AA (4.5)
        result_aa = adjust_color_for_contrast("#888888", "#FFFFFF", min_contrast=4.5)
        ratio_aa = get_contrast_ratio(result_aa, "#FFFFFF")
        assert ratio_aa >= 4.5

        # WCAG AAA (7.0)
        result_aaa = adjust_color_for_contrast("#888888", "#FFFFFF", min_contrast=7.0)
        ratio_aaa = get_contrast_ratio(result_aaa, "#FFFFFF")
        assert ratio_aaa >= 7.0

        # AAA should be darker than AA
        assert get_luminance(result_aaa) < get_luminance(result_aa)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPalettePerformance:
    """Performance tests for palette caching."""

    def test_palette_colors_caching_works(self):
        """Test that LRU cache works for palette colors."""
        # First call should cache
        colors1 = get_palette_colors(ZodiacPalette.VIRIDIS)

        # Second call should return cached result (same object)
        colors2 = get_palette_colors(ZodiacPalette.VIRIDIS)

        # Should be same object reference (cached)
        assert colors1 is colors2

    def test_aspect_palette_caching_works(self):
        """Test that LRU cache works for aspect palettes."""
        # First call should cache
        colors1 = get_aspect_palette_colors(AspectPalette.PLASMA)

        # Second call should return cached result
        colors2 = get_aspect_palette_colors(AspectPalette.PLASMA)

        # Should be same object reference (cached)
        assert colors1 is colors2


# ============================================================================
# REGRESSION TESTS
# ============================================================================


def test_all_zodiac_palettes_valid():
    """Regression test: Ensure all zodiac palettes return valid colors."""
    for palette in ZodiacPalette:
        colors = get_palette_colors(palette)
        assert len(colors) == 12
        for color in colors:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7


def test_all_aspect_palettes_valid():
    """Regression test: Ensure all aspect palettes return valid colors."""
    for palette in AspectPalette:
        colors = get_aspect_palette_colors(palette)
        assert isinstance(colors, dict)
        assert len(colors) >= 5  # At least the 5 major aspects
        for color in colors.values():
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7


def test_all_planet_palettes_valid():
    """Regression test: Ensure all planet palettes return valid colors."""
    test_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]

    for palette in PlanetGlyphPalette:
        for planet in test_planets:
            color = get_planet_glyph_color(planet, palette)
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7


def test_color_contrast_wcag_aa_compliance():
    """Regression test: Ensure adjusted colors meet WCAG AA standard."""
    # Test on white background
    light_colors = ["#CCCCCC", "#DDDDDD", "#EEEEEE", "#F0F0F0"]
    for color in light_colors:
        adjusted = adjust_color_for_contrast(color, "#FFFFFF", min_contrast=4.5)
        ratio = get_contrast_ratio(adjusted, "#FFFFFF")
        assert ratio >= 4.5, f"Failed for {color}: ratio={ratio}"

    # Test on black background
    dark_colors = ["#333333", "#222222", "#111111", "#0F0F0F"]
    for color in dark_colors:
        adjusted = adjust_color_for_contrast(color, "#000000", min_contrast=4.5)
        ratio = get_contrast_ratio(adjusted, "#000000")
        assert ratio >= 4.5, f"Failed for {color}: ratio={ratio}"
