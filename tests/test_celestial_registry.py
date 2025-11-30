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
        svg_objects = ["Nessus", "Pholus", "Eris"]
        for obj_name in svg_objects:
            obj = get_object_info(obj_name)
            if obj:  # Only test if object exists in registry
                assert obj.glyph_svg_path is not None
                assert "assets/glyphs/" in obj.glyph_svg_path
                assert obj.glyph_svg_path.endswith(".svg")


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
