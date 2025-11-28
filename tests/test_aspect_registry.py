"""Tests for the Aspect Registry."""

from stellium.core.registry import (
    ASPECT_REGISTRY,
    get_aspect_by_alias,
    get_aspect_info,
    get_aspects_by_category,
    get_aspects_by_family,
    search_aspects,
)


class TestAspectRegistryBasics:
    """Test basic registry lookups."""

    def test_registry_not_empty(self):
        """Registry should contain aspects."""
        assert len(ASPECT_REGISTRY) > 0
        assert len(ASPECT_REGISTRY) >= 17  # At least the ones we defined

    def test_get_aspect_info_conjunction(self):
        """Should retrieve Conjunction by name."""
        conjunction = get_aspect_info("Conjunction")
        assert conjunction is not None
        assert conjunction.name == "Conjunction"
        assert conjunction.angle == 0.0
        assert conjunction.category == "Major"
        assert conjunction.family == "Ptolemaic"
        assert conjunction.glyph == "☌"

    def test_get_aspect_info_trine(self):
        """Should retrieve Trine by name."""
        trine = get_aspect_info("Trine")
        assert trine is not None
        assert trine.angle == 120.0
        assert trine.category == "Major"
        assert trine.glyph == "△"

    def test_get_aspect_info_nonexistent(self):
        """Should return None for nonexistent aspect."""
        result = get_aspect_info("NonexistentAspect")
        assert result is None


class TestAspectRegistryAliases:
    """Test alias resolution."""

    def test_get_by_alias_conjunct(self):
        """'Conjunct' should resolve to Conjunction."""
        result = get_aspect_by_alias("Conjunct")
        assert result is not None
        assert result.name == "Conjunction"
        assert result.angle == 0.0

    def test_get_by_alias_inconjunct(self):
        """'Inconjunct' should resolve to Quincunx."""
        result = get_aspect_by_alias("Inconjunct")
        assert result is not None
        assert result.name == "Quincunx"
        assert result.angle == 150.0

    def test_get_by_alias_hyphenated(self):
        """Hyphenated variants should work as aliases."""
        result = get_aspect_by_alias("Semi-Sextile")
        assert result is not None
        assert result.name == "Semisextile"
        assert result.angle == 30.0

    def test_get_by_alias_sesquiquadrate(self):
        """'Sesquiquadrate' should resolve to Sesquisquare."""
        result = get_aspect_by_alias("Sesquiquadrate")
        assert result is not None
        assert result.name == "Sesquisquare"
        assert result.angle == 135.0

    def test_get_by_alias_case_insensitive(self):
        """Alias lookup should be case-insensitive."""
        result = get_aspect_by_alias("conjunct")  # lowercase
        assert result is not None
        assert result.name == "Conjunction"

    def test_get_by_alias_nonexistent(self):
        """Should return None for nonexistent alias."""
        result = get_aspect_by_alias("NonexistentAlias")
        assert result is None


class TestAspectRegistryAngles:
    """Test that aspect angles are correct."""

    def test_ptolemaic_angles(self):
        """Major Ptolemaic aspects should have correct angles."""
        angles = {
            "Conjunction": 0.0,
            "Sextile": 60.0,
            "Square": 90.0,
            "Trine": 120.0,
            "Opposition": 180.0,
        }

        for name, expected_angle in angles.items():
            aspect = get_aspect_info(name)
            assert aspect is not None
            assert aspect.angle == expected_angle

    def test_minor_aspect_angles(self):
        """Minor aspects should have correct angles."""
        angles = {
            "Semisextile": 30.0,
            "Semisquare": 45.0,
            "Sesquisquare": 135.0,
            "Quincunx": 150.0,
        }

        for name, expected_angle in angles.items():
            aspect = get_aspect_info(name)
            assert aspect is not None
            assert aspect.angle == expected_angle

    def test_quintile_angles(self):
        """Quintile family should have correct angles."""
        quintile = get_aspect_info("Quintile")
        assert quintile is not None
        assert quintile.angle == 72.0

        biquintile = get_aspect_info("Biquintile")
        assert biquintile is not None
        assert biquintile.angle == 144.0

    def test_harmonic_septile_angles(self):
        """Septile family angles should be correct divisions of 360."""
        septile = get_aspect_info("Septile")
        assert septile is not None
        assert abs(septile.angle - (360 / 7)) < 0.01  # Within rounding

        biseptile = get_aspect_info("Biseptile")
        assert biseptile is not None
        assert abs(biseptile.angle - (360 * 2 / 7)) < 0.01


class TestAspectRegistryCategoryFiltering:
    """Test filtering by category."""

    def test_get_major_aspects(self):
        """Should retrieve all Major aspects."""
        major = get_aspects_by_category("Major")
        assert len(major) == 5  # The 5 Ptolemaic aspects
        names = [a.name for a in major]
        assert "Conjunction" in names
        assert "Opposition" in names
        assert "Trine" in names
        assert "Square" in names
        assert "Sextile" in names

    def test_get_minor_aspects(self):
        """Should retrieve all Minor aspects."""
        minor = get_aspects_by_category("Minor")
        assert len(minor) >= 4
        names = [a.name for a in minor]
        assert "Quincunx" in names
        assert "Semisextile" in names
        assert "Semisquare" in names
        assert "Sesquisquare" in names

    def test_get_harmonic_aspects(self):
        """Should retrieve all Harmonic aspects."""
        harmonic = get_aspects_by_category("Harmonic")
        assert len(harmonic) >= 8  # Quintile + Septile + Novile families
        # Should include aspects from different harmonic families
        names = [a.name for a in harmonic]
        assert "Quintile" in names
        assert "Septile" in names
        assert "Novile" in names


class TestAspectRegistryFamilyFiltering:
    """Test filtering by family."""

    def test_get_ptolemaic_family(self):
        """Should retrieve Ptolemaic family."""
        ptolemaic = get_aspects_by_family("Ptolemaic")
        assert len(ptolemaic) == 5
        names = [a.name for a in ptolemaic]
        assert all(
            name in names
            for name in ["Conjunction", "Sextile", "Square", "Trine", "Opposition"]
        )

    def test_get_quintile_series(self):
        """Should retrieve Quintile Series."""
        quintiles = get_aspects_by_family("Quintile Series")
        assert len(quintiles) >= 2
        names = [a.name for a in quintiles]
        assert "Quintile" in names
        assert "Biquintile" in names

    def test_get_septile_series(self):
        """Should retrieve Septile Series."""
        septiles = get_aspects_by_family("Septile Series")
        assert len(septiles) >= 3
        names = [a.name for a in septiles]
        assert "Septile" in names
        assert "Biseptile" in names
        assert "Triseptile" in names

    def test_get_novile_series(self):
        """Should retrieve Novile Series."""
        noviles = get_aspects_by_family("Novile Series")
        assert len(noviles) >= 3
        names = [a.name for a in noviles]
        assert "Novile" in names
        assert "Binovile" in names
        assert "Quadnovile" in names


class TestAspectRegistryGlyphs:
    """Test glyph metadata."""

    def test_major_aspects_have_glyphs(self):
        """Major aspects should all have Unicode glyphs."""
        major = get_aspects_by_category("Major")
        for aspect in major:
            assert aspect.glyph != ""
            assert len(aspect.glyph) > 0

    def test_minor_aspects_have_glyphs(self):
        """Minor aspects should have Unicode glyphs."""
        minor = get_aspects_by_category("Minor")
        for aspect in minor:
            assert aspect.glyph != ""
            assert len(aspect.glyph) > 0


class TestAspectRegistryDefaultOrbs:
    """Test default orb values."""

    def test_major_aspects_larger_orbs(self):
        """Major aspects should have larger default orbs."""
        conjunction = get_aspect_info("Conjunction")
        assert conjunction.default_orb >= 6.0  # Major aspects have wide orbs

        trine = get_aspect_info("Trine")
        assert trine.default_orb >= 6.0

    def test_minor_aspects_smaller_orbs(self):
        """Minor aspects should have smaller default orbs."""
        quincunx = get_aspect_info("Quincunx")
        assert quincunx.default_orb <= 3.0  # Minor aspects have tight orbs

        semisquare = get_aspect_info("Semisquare")
        assert semisquare.default_orb <= 3.0

    def test_harmonic_aspects_tight_orbs(self):
        """Harmonic aspects should have very tight orbs."""
        quintile = get_aspect_info("Quintile")
        assert quintile.default_orb <= 2.0  # Harmonics are precise

        septile = get_aspect_info("Septile")
        assert septile.default_orb <= 2.0


class TestAspectRegistryMetadata:
    """Test visualization metadata."""

    def test_aspects_have_colors(self):
        """All aspects should have color metadata."""
        for aspect_info in ASPECT_REGISTRY.values():
            assert aspect_info.color.startswith("#")  # Hex color
            assert len(aspect_info.color) == 7  # #RRGGBB format

    def test_major_aspects_have_line_metadata(self):
        """Major aspects should have line width and dash pattern in metadata."""
        major = get_aspects_by_category("Major")
        for aspect in major:
            assert "line_width" in aspect.metadata
            assert "dash_pattern" in aspect.metadata
            assert isinstance(aspect.metadata["line_width"], int | float)
            assert isinstance(aspect.metadata["dash_pattern"], str)


class TestAspectRegistrySearch:
    """Test search functionality."""

    def test_search_by_name(self):
        """Should find aspects by name."""
        results = search_aspects("Trine")
        assert len(results) >= 1
        assert any(a.name == "Trine" for a in results)

    def test_search_by_alias(self):
        """Should find aspects by alias in results."""
        results = search_aspects("Conjunct")
        # Should find Conjunction since it has "Conjunct" as an alias
        assert len(results) >= 1

    def test_search_by_description(self):
        """Should find aspects by description keywords."""
        results = search_aspects("harmony")
        # Trine and Sextile both mention "harmony" or "harmonious"
        assert len(results) >= 1

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        results_upper = search_aspects("SQUARE")
        results_lower = search_aspects("square")
        assert len(results_upper) == len(results_lower)
        assert len(results_upper) >= 1
