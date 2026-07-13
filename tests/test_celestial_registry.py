"""Tests for the Celestial Objects Registry."""

from stellium.core.models import ObjectType
from stellium.core.registry import (
    CELESTIAL_REGISTRY,
    get_all_by_category,
    get_all_by_type,
    get_by_alias,
    get_object_info,
    search_objects,
)


class TestCelestialRegistryBasics:
    """Test basic registry lookups."""

    def test_registry_not_empty(self):
        """Registry should contain objects."""
        assert len(CELESTIAL_REGISTRY) > 0

    def test_get_object_info_sun(self):
        """Should retrieve Sun by name."""
        sun = get_object_info("Sun")
        assert sun is not None
        assert sun.name == "Sun"
        assert sun.display_name == "Sun"
        assert sun.object_type == ObjectType.PLANET
        assert sun.glyph == "☉"

    def test_get_object_info_nonexistent(self):
        """Should return None for nonexistent object."""
        result = get_object_info("Nonexistent Object")
        assert result is None

    def test_mean_apogee_display_name(self):
        """Mean Apogee should display as 'Black Moon Lilith'."""
        lilith = get_object_info("Mean Apogee")
        assert lilith is not None
        assert lilith.name == "Mean Apogee"
        assert lilith.display_name == "Black Moon Lilith"
        assert lilith.object_type == ObjectType.POINT


class TestCelestialRegistryAliases:
    """Test alias resolution."""

    def test_get_by_alias_lilith(self):
        """'Lilith' should resolve to Mean Apogee."""
        result = get_by_alias("Lilith")
        assert result is not None
        assert result.name == "Mean Apogee"
        assert result.display_name == "Black Moon Lilith"

    def test_get_by_alias_bml(self):
        """'BML' should resolve to Mean Apogee."""
        result = get_by_alias("BML")
        assert result is not None
        assert result.name == "Mean Apogee"

    def test_get_by_alias_sol(self):
        """'Sol' should resolve to Sun."""
        result = get_by_alias("Sol")
        assert result is not None
        assert result.name == "Sun"

    def test_get_by_alias_nonexistent(self):
        """Should return None for nonexistent alias."""
        result = get_by_alias("NonexistentAlias")
        assert result is None

    def test_get_by_alias_case_insensitive(self):
        """Alias lookup should be case-insensitive."""
        result = get_by_alias("lilith")  # lowercase
        assert result is not None
        assert result.name == "Mean Apogee"


class TestCelestialRegistryTypeFiltering:
    """Test filtering by ObjectType."""

    def test_get_all_planets(self):
        """Should retrieve all PLANET objects."""
        planets = get_all_by_type(ObjectType.PLANET)
        assert len(planets) == 11  # Sun through Pluto + Earth (for heliocentric)
        planet_names = [p.name for p in planets]
        assert "Sun" in planet_names
        assert "Moon" in planet_names
        assert "Pluto" in planet_names
        assert "Earth" in planet_names

    def test_get_all_nodes(self):
        """Should retrieve all NODE objects."""
        nodes = get_all_by_type(ObjectType.NODE)
        assert len(nodes) >= 2  # At least True Node and South Node
        node_names = [n.name for n in nodes]
        assert "True Node" in node_names
        assert "South Node" in node_names

    def test_get_all_points(self):
        """Should retrieve all POINT objects."""
        points = get_all_by_type(ObjectType.POINT)
        assert len(points) >= 3  # Vertex, Mean Apogee, True Apogee
        point_names = [p.name for p in points]
        assert "Vertex" in point_names
        assert "Mean Apogee" in point_names

    def test_get_all_asteroids(self):
        """Should retrieve all ASTEROID objects."""
        asteroids = get_all_by_type(ObjectType.ASTEROID)
        assert len(asteroids) >= 4  # At least the Big Four
        asteroid_names = [a.name for a in asteroids]
        assert "Ceres" in asteroid_names
        assert "Pallas" in asteroid_names
        assert "Juno" in asteroid_names
        assert "Vesta" in asteroid_names


class TestCelestialRegistryCategoryFiltering:
    """Test filtering by category."""

    def test_get_traditional_planets(self):
        """Should retrieve traditional planets (Sun-Saturn)."""
        traditional = get_all_by_category("Traditional Planet")
        assert len(traditional) == 7  # Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
        names = [p.name for p in traditional]
        assert "Sun" in names
        assert "Saturn" in names
        assert "Uranus" not in names  # Modern planet

    def test_get_centaurs(self):
        """Should retrieve Centaurs."""
        centaurs = get_all_by_category("Centaur")
        assert len(centaurs) >= 2  # At least Chiron and Pholus
        names = [c.name for c in centaurs]
        assert "Chiron" in names
        assert "Pholus" in names

    def test_get_fixed_stars(self):
        """Should retrieve Fixed Stars."""
        stars = get_all_by_category("Fixed Star")
        assert len(stars) >= 4  # At least the Four Royal Stars
        # Just verify we got some stars
        assert len(stars) > 0


class TestCelestialRegistrySearch:
    """Test search functionality."""

    def test_search_by_name(self):
        """Should find objects by name."""
        results = search_objects("Jupiter")
        assert len(results) >= 1
        assert any(obj.name == "Jupiter" for obj in results)

    def test_search_by_alias(self):
        """Should find objects by alias."""
        results = search_objects("Lilith")
        assert len(results) >= 1
        assert any(obj.name == "Mean Apogee" for obj in results)

    def test_search_by_description(self):
        """Should find objects by description keywords."""
        results = search_objects("communication")
        # Mercury's description mentions communication
        assert any(obj.name == "Mercury" for obj in results)

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        results_upper = search_objects("VENUS")
        results_lower = search_objects("venus")
        assert len(results_upper) == len(results_lower)
        assert len(results_upper) >= 1


class TestCelestialRegistryGlyphs:
    """Test glyph metadata."""

    def test_planets_have_glyphs(self):
        """All planets should have Unicode glyphs."""
        planets = get_all_by_type(ObjectType.PLANET)
        for planet in planets:
            assert planet.glyph != ""  # Should have a glyph
            assert len(planet.glyph) > 0

    def test_svg_glyph_paths_when_present(self):
        """Objects with SVG glyphs should have valid paths."""
        # Check objects that we know have SVG glyphs
        from stellium.data.paths import find_glyph_svg

        svg_objects = ["Nessus", "Pholus", "Eris"]
        for obj_name in svg_objects:
            obj = get_object_info(obj_name)
            if obj:  # Only test if object exists in registry
                assert obj.glyph_svg_path is not None
                assert obj.glyph_svg_path.endswith(".svg")
                # A bare filename, resolved against the *packaged* glyph directory.
                # It used to be the repo-relative "assets/glyphs/pholus.svg", which
                # pointed outside the wheel — so this test asserted the very format
                # that made 25 bodies render as tofu for everyone who pip-installed.
                assert "/" not in obj.glyph_svg_path
                assert find_glyph_svg(obj.glyph_svg_path) is not None


class TestCelestialRegistryMetadata:
    """Test metadata and special fields."""

    def test_swiss_ephemeris_ids(self):
        """Major objects should have Swiss Ephemeris IDs."""
        sun = get_object_info("Sun")
        assert sun.swiss_ephemeris_id == 0

        moon = get_object_info("Moon")
        assert moon.swiss_ephemeris_id == 1

    def test_object_with_metadata(self):
        """Some objects should have metadata dictionaries."""
        # Fixed stars might have magnitude in metadata
        regulus = get_object_info("Regulus")
        if regulus:
            assert isinstance(regulus.metadata, dict)


class TestEphemerisIdsAreConsistent:
    """Two tables name the same bodies, and they disagreed.

    `CELESTIAL_REGISTRY[x].swiss_ephemeris_id` and
    `engines.ephemeris.SWISS_EPHEMERIS_IDS[x]` are both consulted at runtime — the
    registry's by `utils/planetary_crossing.py` (so by `ReturnBuilder.planetary`), the
    engine's by `calculate_positions()`. For all six TNOs they differed by exactly
    AST_OFFSET (10000), because the registry stored the **MPC number** in a field named
    *swiss_ephemeris_id*.

    That is not a cosmetic mismatch: Swiss Ephemeris resolves id 136199 to the file
    `s126199s.se1` — a *different asteroid*. Asking for Eris's return raised a
    misleading "file not found", and anyone who happened to own that other asteroid's
    file would have silently got the wrong body.
    """

    def test_the_registry_and_the_engine_agree_on_every_shared_body(self):
        from stellium.core.registry import CELESTIAL_REGISTRY
        from stellium.engines.ephemeris import SWISS_EPHEMERIS_IDS

        disagreements = [
            f"{name}: registry {info.swiss_ephemeris_id} vs engine "
            f"{SWISS_EPHEMERIS_IDS[name]}"
            for name, info in CELESTIAL_REGISTRY.items()
            if info.swiss_ephemeris_id is not None
            and name in SWISS_EPHEMERIS_IDS
            and info.swiss_ephemeris_id != SWISS_EPHEMERIS_IDS[name]
        ]
        assert not disagreements, (
            "these bodies have two different Swiss Ephemeris ids, and both are used:\n  "
            + "\n  ".join(disagreements)
        )

    def test_every_body_the_registry_knows_can_actually_be_calculated(self):
        """`calculate_positions()` skips any name absent from SWISS_EPHEMERIS_IDS —
        silently. Hygiea, Nessus and Chariklo each had a registry entry and a
        hand-drawn glyph, and could never be computed: requesting one gave you a chart
        quietly missing that body.
        """
        from stellium.core.registry import CELESTIAL_REGISTRY
        from stellium.engines.ephemeris import SWISS_EPHEMERIS_IDS

        uncomputable = [
            name
            for name, info in CELESTIAL_REGISTRY.items()
            if info.swiss_ephemeris_id is not None and name not in SWISS_EPHEMERIS_IDS
        ]
        assert not uncomputable, (
            "the registry advertises these bodies but the ephemeris engine has no id "
            f"for them, so they are silently dropped from every chart: {uncomputable}"
        )

    def test_numbered_asteroids_carry_the_ast_offset(self):
        """Swiss Ephemeris addresses a numbered asteroid as MPC number + 10000.

        A raw MPC number in this field points at a completely different rock.
        """
        import swisseph as swe

        from stellium.core.registry import CELESTIAL_REGISTRY

        # Bodies addressed by MPC number, as opposed to swisseph's built-in ids
        # (Sun=0 … Pluto=9, Chiron=15, Ceres=17, …).
        numbered = {
            "Eris": 136199,
            "Sedna": 90377,
            "Quaoar": 50000,
            "Makemake": 136472,
            "Haumea": 136108,
            "Orcus": 90482,
            "Gonggong": 225088,
            "Hygiea": 10,
            "Nessus": 7066,
            "Chariklo": 10199,
        }
        for name, mpc in numbered.items():
            info = CELESTIAL_REGISTRY[name]
            assert info.swiss_ephemeris_id == mpc + swe.AST_OFFSET, (
                f"{name}: swiss_ephemeris_id should be MPC {mpc} + AST_OFFSET "
                f"({mpc + swe.AST_OFFSET}), got {info.swiss_ephemeris_id}"
            )


def test_gonggong_is_registered_with_its_glyph():
    """Its hand-drawn glyph sat unused in the package: a file with no registry entry."""
    from stellium.core.registry import CELESTIAL_REGISTRY
    from stellium.visualization.core import get_glyph

    gonggong = CELESTIAL_REGISTRY["Gonggong"]
    assert gonggong.glyph_svg_path == "gonggong.svg"
    assert get_glyph("Gonggong")["type"] == "svg"
