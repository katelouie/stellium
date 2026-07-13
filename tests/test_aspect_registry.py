"""Tests for the Aspect Registry."""

from datetime import datetime

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


class TestAspectRegistryViews:
    """The ecliptic / declination derived views.

    Declination aspects live in ASPECT_REGISTRY alongside the ecliptic ones so that
    looking an aspect up *by name* stays uniform — a caller holding an Aspect with
    aspect_name="Parallel" wants its glyph and should not have to know its family.

    But they are recorded at 0° and 180° purely by analogy with Conjunction and
    Opposition, so angle is NOT a unique key across the whole registry. Anything
    keying on angle must build over the ecliptic view.
    """

    def test_views_partition_the_registry(self):
        from stellium.core.registry import (
            ASPECT_REGISTRY,
            DECLINATION_ASPECT_REGISTRY,
            ECLIPTIC_ASPECT_REGISTRY,
        )

        assert set(ECLIPTIC_ASPECT_REGISTRY) | set(DECLINATION_ASPECT_REGISTRY) == set(
            ASPECT_REGISTRY
        )
        assert not set(ECLIPTIC_ASPECT_REGISTRY) & set(DECLINATION_ASPECT_REGISTRY)

    def test_declination_view_holds_exactly_the_declination_aspects(self):
        from stellium.core.registry import DECLINATION_ASPECT_REGISTRY

        assert set(DECLINATION_ASPECT_REGISTRY) == {"Parallel", "Contraparallel"}

    def test_angle_is_a_unique_key_within_the_ecliptic_view(self):
        """The invariant that makes angle-keyed lookups safe.

        Across the FULL registry it does not hold: Parallel collides with
        Conjunction at 0°, Contraparallel with Opposition at 180°.
        """
        from stellium.core.registry import (
            ASPECT_REGISTRY,
            ECLIPTIC_ASPECT_REGISTRY,
        )

        ecliptic_angles = [info.angle for info in ECLIPTIC_ASPECT_REGISTRY.values()]
        assert len(ecliptic_angles) == len(set(ecliptic_angles))

        # ...and demonstrate the collision the view exists to prevent.
        all_angles = [info.angle for info in ASPECT_REGISTRY.values()]
        assert len(all_angles) != len(set(all_angles))

    def test_name_lookup_stays_uniform_across_both_families(self):
        """Declination aspects must remain resolvable through the shared registry.

        The report's DeclinationAspectSection does exactly this to get their glyph.
        """
        from stellium.core.registry import get_aspect_info

        assert get_aspect_info("Parallel").glyph == "∥"
        assert get_aspect_info("Contraparallel").glyph == "⋕"
        assert get_aspect_info("Conjunction").glyph == "☌"


class TestDeclinationAspectsAreNotEclipticAspects:
    """Declination aspects must never be computed from ecliptic longitude.

    Parallel and Contraparallel live in ASPECT_REGISTRY at 0° and 180° purely by
    analogy with Conjunction and Opposition. An ecliptic engine that trusts that
    angle measures the wrong thing entirely: it will report an *opposition* as a
    contraparallel, because the two longitudes happen to be 180° apart.
    """

    def test_ecliptic_engine_refuses_declination_aspects(self):
        import warnings

        from stellium import ChartBuilder, Native
        from stellium.core.config import AspectConfig
        from stellium.engines.aspects import ModernAspectEngine

        native = Native("1990-05-15 14:30", "San Francisco, CA")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            chart = (
                ChartBuilder.from_native(native)
                .with_aspects(
                    ModernAspectEngine(
                        AspectConfig(aspects=["Parallel", "Contraparallel"])
                    )
                )
                .calculate()
            )

        # Nothing fabricated from longitude...
        assert len(chart.aspects) == 0
        # ...and the user is told why, and what to use instead.
        messages = " ".join(str(w.message) for w in caught)
        assert "declination aspect" in messages
        assert "with_declination_aspects" in messages

    def test_real_ecliptic_aspects_still_compute(self):
        from stellium import ChartBuilder, Native
        from stellium.core.config import AspectConfig
        from stellium.engines.aspects import ModernAspectEngine

        native = Native("1990-05-15 14:30", "San Francisco, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_aspects(ModernAspectEngine(AspectConfig(aspects=["Conjunction"])))
            .calculate()
        )
        assert len(chart.aspects) > 0
        assert all(a.aspect_name == "Conjunction" for a in chart.aspects)


class TestDignityTablesUseRealNone:
    """DIGNITIES stored "no exaltation lord" as the literal string "None"."""

    def test_absent_lords_are_none_not_the_string(self):
        from stellium.engines.dignities import DIGNITIES

        # No planet is exalted in Leo, Scorpio or Aquarius; none falls in Leo,
        # Taurus or Aquarius.
        assert DIGNITIES["Leo"]["traditional"]["exaltation"] is None
        assert DIGNITIES["Aquarius"]["traditional"]["exaltation"] is None
        assert DIGNITIES["Scorpio"]["traditional"]["exaltation"] is None

        for sign, data in DIGNITIES.items():
            for system in ("traditional", "modern"):
                for key in ("ruler", "exaltation", "detriment", "fall"):
                    assert data[system].get(key) != "None", f"{sign}.{system}.{key}"

    def test_reception_potential_key_is_spelled_correctly(self):
        """The docstring, the local var and the method all say "reception"."""
        from stellium import ChartBuilder, Native
        from stellium.engines.dignities import TraditionalDignityCalculator

        chart = ChartBuilder.from_native(
            Native("1990-05-15 14:30", "San Francisco, CA")
        ).calculate()
        result = TraditionalDignityCalculator().calculate_dignities(
            chart.get_object("Sun"), sect="day"
        )
        assert "reception_potential" in result
        # The historical typo is kept as an alias so existing callers keep working.
        assert result["receiption_potential"] == result["reception_potential"]


class TestAspectExactitudeSearch:
    """Regression tests for find_aspect_exact / find_all_aspect_exacts.

    Three bugs, all found by wiring up the planner's mundane-transit collector:

    1. `aspect_angle % 180` — and 180 % 180 == 0, so EVERY opposition search was
       silently a conjunction search. Oppositions could not be found at all, and the
       conjunction it found instead was returned labelled as the opposition.
    2. Separation is measured 0-180, so at both 0 deg and 180 deg the error only
       *touches* zero rather than crossing it. Only the conjunction half of that had
       extremum detection, so nothing could bracket an opposition either.
    3. Refinement used Newton-Raphson, which does not converge on the folded
       separation (its derivative flips where it folds). On failure the old code
       returned its last guess as though it were the answer.
    """

    START = datetime(2026, 1, 1)
    END = datetime(2026, 12, 31)

    @staticmethod
    def _separation(name1: str, name2: str, julian_day: float) -> float:
        from stellium.engines.search import (
            SWISS_EPHEMERIS_IDS,
            _get_position_and_speed,
        )

        a, _ = _get_position_and_speed(SWISS_EPHEMERIS_IDS[name1], julian_day)
        b, _ = _get_position_and_speed(SWISS_EPHEMERIS_IDS[name2], julian_day)
        return abs((a - b + 180) % 360 - 180)

    def test_venus_can_never_oppose_the_sun(self):
        """Venus strays at most ~47 deg from the Sun. An opposition is impossible."""
        from stellium.engines.search import find_all_aspect_exacts

        assert find_all_aspect_exacts("Sun", "Venus", 180.0, self.START, self.END) == []
        assert (
            find_all_aspect_exacts("Sun", "Mercury", 180.0, self.START, self.END) == []
        )
        # Nor can it trine or square it.
        assert find_all_aspect_exacts("Sun", "Venus", 120.0, self.START, self.END) == []

    def test_oppositions_are_actually_found(self):
        """The outer planets each oppose the Sun once a year."""
        from stellium.engines.search import find_all_aspect_exacts

        for planet in ("Jupiter", "Saturn", "Uranus", "Neptune"):
            hits = find_all_aspect_exacts("Sun", planet, 180.0, self.START, self.END)
            assert len(hits) == 1, planet
            separation = self._separation("Sun", planet, hits[0].julian_day)
            assert abs(separation - 180.0) < 0.01, planet

    def test_lunations(self):
        """A year holds 12-13 new and full Moons."""
        from stellium.engines.search import find_all_aspect_exacts

        new = find_all_aspect_exacts("Sun", "Moon", 0.0, self.START, self.END)
        full = find_all_aspect_exacts("Sun", "Moon", 180.0, self.START, self.END)
        assert 12 <= len(new) <= 13
        assert 12 <= len(full) <= 13

    def test_fast_recurring_aspects_are_not_dropped(self):
        """The Moon trines Jupiter about twice a month. This used to return zero."""
        from stellium.engines.search import find_all_aspect_exacts

        hits = find_all_aspect_exacts("Moon", "Jupiter", 120.0, self.START, self.END)
        assert len(hits) >= 20

    def test_every_returned_aspect_is_actually_exact(self):
        """The heart of it: never return a moment that is not the aspect."""
        from stellium.engines.search import find_all_aspect_exacts

        cases = [
            ("Sun", "Mars", 90.0),
            ("Jupiter", "Saturn", 120.0),
            ("Mars", "Saturn", 90.0),
            ("Venus", "Mars", 0.0),
            ("Sun", "Jupiter", 180.0),
            ("Moon", "Mars", 90.0),
        ]
        for name1, name2, angle in cases:
            for hit in find_all_aspect_exacts(
                name1, name2, angle, self.START, self.END
            ):
                separation = self._separation(name1, name2, hit.julian_day)
                assert abs(separation - angle) < 0.01, (
                    f"{name1} {angle} {name2} at {hit.datetime_utc}: separation is "
                    f"{separation:.4f}, not {angle}"
                )
