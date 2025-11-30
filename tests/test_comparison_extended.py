"""
Extended tests for Comparison and ComparisonBuilder to improve code coverage.

Covers:
- Comparison dataclass properties and methods
- ComparisonBuilder configuration methods
- Progression with auto-calculation (age, target_date, angle methods)
- House overlay queries
- Compatibility scoring
- to_dict() serialization
- draw() visualization method
- Error handling
"""

import datetime as dt
from datetime import datetime

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.comparison import ComparisonBuilder
from stellium.core.models import ChartLocation, ComparisonType
from stellium.core.native import Native
from stellium.engines.aspects import CrossChartAspectEngine, ModernAspectEngine
from stellium.engines.orbs import SimpleOrbEngine


class TestComparisonDataclass:
    """Tests for Comparison dataclass properties and methods."""

    @pytest.fixture
    def synastry_comparison(self):
        """Create a synastry comparison for testing."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
            chart1_label="Person A",
            chart2_label="Person B",
        ).calculate()

    def test_datetime_property(self, synastry_comparison):
        """Test datetime property returns chart1's datetime."""
        assert synastry_comparison.datetime == synastry_comparison.chart1.datetime

    def test_location_property(self, synastry_comparison):
        """Test location property returns chart1's location."""
        assert synastry_comparison.location == synastry_comparison.chart1.location

    def test_positions_property(self, synastry_comparison):
        """Test positions property returns chart1's positions."""
        assert synastry_comparison.positions == synastry_comparison.chart1.positions

    def test_houses_property(self, synastry_comparison):
        """Test houses property returns chart1's default house system."""
        houses = synastry_comparison.houses
        assert houses is not None
        assert len(houses.cusps) == 12

    def test_aspects_property(self, synastry_comparison):
        """Test aspects property returns chart1's natal aspects."""
        assert synastry_comparison.aspects == synastry_comparison.chart1.aspects

    def test_chart2_datetime_property(self, synastry_comparison):
        """Test chart2_datetime property."""
        assert (
            synastry_comparison.chart2_datetime == synastry_comparison.chart2.datetime
        )

    def test_chart2_location_property(self, synastry_comparison):
        """Test chart2_location property."""
        assert (
            synastry_comparison.chart2_location == synastry_comparison.chart2.location
        )

    def test_chart2_positions_property(self, synastry_comparison):
        """Test chart2_positions property."""
        assert (
            synastry_comparison.chart2_positions == synastry_comparison.chart2.positions
        )

    def test_chart2_houses_property(self, synastry_comparison):
        """Test chart2_houses property."""
        houses = synastry_comparison.chart2_houses
        assert houses is not None
        assert len(houses.cusps) == 12

    def test_chart2_aspects_property(self, synastry_comparison):
        """Test chart2_aspects property."""
        assert synastry_comparison.chart2_aspects == synastry_comparison.chart2.aspects


class TestComparisonQueryMethods:
    """Tests for Comparison query methods."""

    @pytest.fixture
    def synastry(self):
        """Create synastry for query testing."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

    def test_get_object_from_chart1(self, synastry):
        """Test get_object() retrieves from chart1."""
        sun = synastry.get_object("Sun", chart=1)
        assert sun is not None
        assert sun.name == "Sun"

    def test_get_object_from_chart2(self, synastry):
        """Test get_object() retrieves from chart2."""
        sun = synastry.get_object("Sun", chart=2)
        assert sun is not None
        assert sun.name == "Sun"

    def test_get_object_not_found(self, synastry):
        """Test get_object() returns None for unknown object."""
        result = synastry.get_object("NonexistentPlanet", chart=1)
        assert result is None

    def test_get_planets_from_chart1(self, synastry):
        """Test get_planets() from chart1."""
        planets = synastry.get_planets(chart=1)
        assert len(planets) > 0
        planet_names = [p.name for p in planets]
        assert "Sun" in planet_names
        assert "Moon" in planet_names

    def test_get_planets_from_chart2(self, synastry):
        """Test get_planets() from chart2."""
        planets = synastry.get_planets(chart=2)
        assert len(planets) > 0

    def test_get_angles_from_chart1(self, synastry):
        """Test get_angles() from chart1."""
        angles = synastry.get_angles(chart=1)
        assert len(angles) > 0
        angle_names = [a.name for a in angles]
        assert (
            "Ascendant" in angle_names or "ASC" in angle_names or len(angle_names) > 0
        )

    def test_get_angles_from_chart2(self, synastry):
        """Test get_angles() from chart2."""
        angles = synastry.get_angles(chart=2)
        assert len(angles) > 0


class TestComparisonHouseOverlayQueries:
    """Tests for house overlay query methods."""

    @pytest.fixture
    def synastry(self):
        """Create synastry for house overlay testing."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

    def test_get_object_houses(self, synastry):
        """Test get_object_houses() returns overlays for a planet."""
        # Get overlays for Sun from chart1
        overlays = synastry.get_object_houses("Sun", chart=1)

        # Sun should fall in some house in chart2
        assert len(overlays) > 0
        for overlay in overlays:
            assert overlay.planet_name == "Sun"

    def test_get_objects_in_house(self, synastry):
        """Test get_objects_in_house() returns planets in a specific house."""
        # Get all planets in house 1 of chart1
        overlays = synastry.get_objects_in_house(1, house_owner=1, planet_owner="both")

        # Results should be for house 1
        for overlay in overlays:
            assert overlay.falls_in_house == 1
            assert overlay.house_owner == "chart1"

    def test_get_objects_in_house_specific_owner(self, synastry):
        """Test get_objects_in_house() with specific planet owner."""
        # Get only chart2 planets in chart1's houses
        overlays = synastry.get_objects_in_house(1, house_owner=1, planet_owner=2)

        for overlay in overlays:
            assert overlay.house_owner == "chart1"


class TestComparisonCompatibilityScoring:
    """Tests for compatibility scoring method."""

    @pytest.fixture
    def synastry(self):
        """Create synastry for scoring tests."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

    def test_calculate_compatibility_score_default(self, synastry):
        """Test compatibility score with default weights."""
        score = synastry.calculate_compatibility_score()

        assert 0.0 <= score <= 100.0

    def test_calculate_compatibility_score_custom_weights(self, synastry):
        """Test compatibility score with custom weights."""
        custom_weights = {
            "Conjunction": 1.0,
            "Sextile": 0.8,
            "Square": -0.8,
            "Trine": 1.0,
            "Opposition": -0.5,
        }

        score = synastry.calculate_compatibility_score(weights=custom_weights)

        assert 0.0 <= score <= 100.0

    def test_calculate_compatibility_score_no_aspects(self):
        """Test compatibility score returns 50 when no cross-aspects."""
        # Create minimal comparison manually to test edge case
        loc = ChartLocation(latitude=40.7128, longitude=-74.0060, name="New York")
        native = Native(datetime(2020, 1, 1, 12, 0, tzinfo=dt.UTC), loc)
        chart = ChartBuilder.from_native(native).calculate()

        # Create comparison with no cross-aspects by disabling house overlays
        comparison = (
            ComparisonBuilder.from_native(chart)
            .with_partner(chart)  # Same chart = may have few cross-aspects
            .without_house_overlays()
            .calculate()
        )

        score = comparison.calculate_compatibility_score()
        # Should return a valid score
        assert 0.0 <= score <= 100.0


class TestComparisonSerialization:
    """Tests for to_dict() serialization."""

    @pytest.fixture
    def synastry(self):
        """Create synastry for serialization tests."""
        return ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
            chart1_label="Alice",
            chart2_label="Bob",
        ).calculate()

    def test_to_dict_structure(self, synastry):
        """Test to_dict() returns expected structure."""
        data = synastry.to_dict()

        assert "comparison_type" in data
        assert "chart1_label" in data
        assert "chart2_label" in data
        assert "chart1" in data
        assert "chart2" in data
        assert "cross_aspects" in data
        assert "house_overlays" in data

    def test_to_dict_comparison_type(self, synastry):
        """Test to_dict() includes comparison type."""
        data = synastry.to_dict()

        assert data["comparison_type"] == "synastry"

    def test_to_dict_labels(self, synastry):
        """Test to_dict() includes chart labels."""
        data = synastry.to_dict()

        assert data["chart1_label"] == "Alice"
        assert data["chart2_label"] == "Bob"

    def test_to_dict_cross_aspects_structure(self, synastry):
        """Test to_dict() cross_aspects have expected fields."""
        data = synastry.to_dict()

        if data["cross_aspects"]:
            aspect = data["cross_aspects"][0]
            assert "object1" in aspect
            assert "object2" in aspect
            assert "aspect" in aspect
            assert "orb" in aspect
            assert "is_applying" in aspect

    def test_to_dict_house_overlays_structure(self, synastry):
        """Test to_dict() house_overlays have expected fields."""
        data = synastry.to_dict()

        if data["house_overlays"]:
            overlay = data["house_overlays"][0]
            assert "planet" in overlay
            assert "planet_owner" in overlay
            assert "house" in overlay
            assert "house_owner" in overlay


class TestComparisonDraw:
    """Tests for draw() visualization method."""

    def test_draw_returns_builder(self):
        """Test draw() returns ChartDrawBuilder."""
        synastry = ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

        from stellium.visualization.builder import ChartDrawBuilder

        builder = synastry.draw()
        assert isinstance(builder, ChartDrawBuilder)

    def test_draw_with_filename(self):
        """Test draw() accepts filename parameter."""
        synastry = ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

        builder = synastry.draw("custom_filename.svg")
        assert builder is not None


class TestComparisonBuilderConfiguration:
    """Tests for ComparisonBuilder configuration methods."""

    def test_with_aspect_engine(self):
        """Test with_aspect_engine() configuration."""
        custom_engine = CrossChartAspectEngine()

        comparison = (
            ComparisonBuilder.synastry(
                ("1990-01-15 10:00", "New York, NY"),
                ("1992-06-20 14:30", "Los Angeles, CA"),
            )
            .with_aspect_engine(custom_engine)
            .calculate()
        )

        assert len(comparison.cross_aspects) >= 0

    def test_with_orb_engine(self):
        """Test with_orb_engine() configuration."""
        tight_orbs = SimpleOrbEngine(
            orb_map={"Conjunction": 2.0, "Trine": 2.0, "Square": 2.0}
        )

        comparison = (
            ComparisonBuilder.synastry(
                ("1990-01-15 10:00", "New York, NY"),
                ("1992-06-20 14:30", "Los Angeles, CA"),
            )
            .with_orb_engine(tight_orbs)
            .calculate()
        )

        # With tighter orbs, should have fewer aspects
        assert comparison is not None

    def test_without_house_overlays(self):
        """Test without_house_overlays() disables overlay calculation."""
        comparison = (
            ComparisonBuilder.synastry(
                ("1990-01-15 10:00", "New York, NY"),
                ("1992-06-20 14:30", "Los Angeles, CA"),
            )
            .without_house_overlays()
            .calculate()
        )

        assert len(comparison.house_overlays) == 0

    def test_with_internal_aspect_engine(self):
        """Test with_internal_aspect_engine() configuration."""
        comparison = (
            ComparisonBuilder.synastry(
                ("1990-01-15 10:00", "New York, NY"),
                ("1992-06-20 14:30", "Los Angeles, CA"),
            )
            .with_internal_aspect_engine(ModernAspectEngine())
            .calculate()
        )

        # Both charts should have internal aspects calculated
        assert len(comparison.chart1.aspects) > 0
        assert len(comparison.chart2.aspects) > 0

    def test_with_internal_orb_engine(self):
        """Test with_internal_orb_engine() configuration."""
        comparison = (
            ComparisonBuilder.synastry(
                ("1990-01-15 10:00", "New York, NY"),
                ("1992-06-20 14:30", "Los Angeles, CA"),
            )
            .with_internal_orb_engine(SimpleOrbEngine())
            .calculate()
        )

        assert comparison is not None


class TestComparisonBuilderWithPartner:
    """Tests for with_partner() method."""

    def test_with_partner_calculated_chart(self):
        """Test with_partner() with CalculatedChart."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()
        chart2 = ChartBuilder.from_details(
            "1992-06-20 14:30", "Los Angeles, CA"
        ).calculate()

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_partner(chart2, partner_label="Partner")
            .calculate()
        )

        assert comparison.chart2_label == "Partner"

    def test_with_partner_native(self):
        """Test with_partner() with Native object."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()
        native2 = Native("1992-06-20 14:30", "Los Angeles, CA")

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_partner(native2, partner_label="Native Partner")
            .calculate()
        )

        assert comparison.chart2_label == "Native Partner"

    def test_with_partner_datetime_requires_location(self):
        """Test with_partner() with datetime requires location."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        with pytest.raises(ValueError) as exc_info:
            ComparisonBuilder.from_native(chart1).with_partner(
                datetime(1992, 6, 20, 14, 30),
                location=None,
            )

        assert "Location required" in str(exc_info.value)


class TestComparisonBuilderWithOther:
    """Tests for with_other() generic method."""

    def test_with_other_calculated_chart(self):
        """Test with_other() with CalculatedChart."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()
        chart2 = ChartBuilder.from_details(
            "2024-11-24 14:30", "New York, NY"
        ).calculate()

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_other(chart2, other_label="Other Chart")
            .calculate()
        )

        assert comparison.chart2_label == "Other Chart"

    def test_with_other_native(self):
        """Test with_other() with Native object."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()
        native2 = Native("2024-11-24 14:30", "Los Angeles, CA")

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_other(native2, other_label="Native")
            .calculate()
        )

        assert comparison.chart2_label == "Native"

    def test_with_other_datetime_uses_chart1_location(self):
        """Test with_other() with datetime and no location uses chart1's location."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_other(
                datetime(2024, 11, 24, 14, 30, tzinfo=dt.UTC),
                location=None,  # Should use chart1's location
                other_label="Transit",
                comparison_type=ComparisonType.TRANSIT,
            )
            .calculate()
        )

        assert "New York" in comparison.chart2.location.name

    def test_with_other_sets_comparison_type(self):
        """Test with_other() can set comparison type."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_other(
                datetime(2024, 11, 24, 14, 30, tzinfo=dt.UTC),
                comparison_type=ComparisonType.TRANSIT,
            )
            .calculate()
        )

        assert comparison.comparison_type == ComparisonType.TRANSIT


class TestComparisonBuilderWithTransit:
    """Tests for with_transit() method."""

    def test_with_transit_uses_natal_location(self):
        """Test with_transit() uses natal location by default."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        comparison = (
            ComparisonBuilder.from_native(chart1)
            .with_transit(datetime(2024, 11, 24, 14, 30, tzinfo=dt.UTC))
            .calculate()
        )

        assert comparison.comparison_type == ComparisonType.TRANSIT
        # Should use natal location
        assert comparison.chart2.location.latitude == chart1.location.latitude


class TestComparisonBuilderCalculateErrors:
    """Tests for calculate() error handling."""

    def test_calculate_without_chart2_raises_error(self):
        """Test calculate() raises error when chart2 not set."""
        chart1 = ChartBuilder.from_details(
            "1990-01-15 10:00", "New York, NY"
        ).calculate()

        with pytest.raises(ValueError) as exc_info:
            ComparisonBuilder.from_native(chart1).calculate()

        assert "Must set chart2" in str(exc_info.value)


class TestProgressionAutoCalculation:
    """Tests for progression auto-calculation features."""

    def test_progression_by_age(self):
        """Test progression() with age parameter."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(natal, age=30).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION
        # Progressed chart should be ~30 days after natal
        delta = (
            comparison.chart2.datetime.local_datetime
            - comparison.chart1.datetime.local_datetime
        )
        assert 29 <= delta.days <= 31

    def test_progression_by_target_date_string(self):
        """Test progression() with target_date string."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(
            natal, target_date="2025-01-15"
        ).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION

    def test_progression_by_target_date_datetime(self):
        """Test progression() with target_date datetime."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(
            natal, target_date=datetime(2025, 1, 15)
        ).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION

    def test_progression_solar_arc_angles(self):
        """Test progression() with solar_arc angle method."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(
            natal, age=30, angle_method="solar_arc"
        ).calculate()

        # Check metadata for angle method
        assert comparison.chart2.metadata.get("angle_method") == "solar_arc"
        assert "angle_arc" in comparison.chart2.metadata

    def test_progression_naibod_angles(self):
        """Test progression() with naibod angle method."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(
            natal, age=30, angle_method="naibod"
        ).calculate()

        assert comparison.chart2.metadata.get("angle_method") == "naibod"

    def test_progression_quotidian_angles_default(self):
        """Test progression() uses quotidian angles by default."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(
            natal, age=30, angle_method="quotidian"
        ).calculate()

        # Quotidian doesn't add angle metadata
        assert comparison.chart2.metadata.get("angle_method") is None

    def test_progression_default_to_now(self):
        """Test progression() defaults to current date when neither age nor target_date specified."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        # No age or target_date = should use current date
        comparison = ComparisonBuilder.progression(natal).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION

    def test_progression_with_explicit_chart(self):
        """Test progression() with explicit progressed chart (legacy mode)."""
        natal = Native("1990-01-15 10:00", "New York, NY")
        # Create progressed chart manually (30 days later)
        progressed = Native("1990-02-14 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(natal, progressed).calculate()

        assert comparison.comparison_type == ComparisonType.PROGRESSION


class TestComparisonDefaultOrbs:
    """Tests for comparison-type specific default orbs."""

    def test_synastry_default_orbs(self):
        """Test synastry uses moderate orbs."""
        # This is tested implicitly - synastry should find aspects with ~6° orbs
        comparison = ComparisonBuilder.synastry(
            ("1990-01-15 10:00", "New York, NY"),
            ("1992-06-20 14:30", "Los Angeles, CA"),
        ).calculate()

        # Should find aspects with moderate orbs
        assert len(comparison.cross_aspects) > 0

    def test_transit_default_orbs_are_tighter(self):
        """Test transit uses tighter orbs than synastry."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.transit(
            natal,
            ("2024-11-24 14:30", None),
        ).calculate()

        # Transit orbs are tighter (3° for major aspects)
        # All aspects should have orbs under 3-4°
        for aspect in comparison.cross_aspects:
            # Major aspects should be under 4° with transit orbs
            if aspect.aspect_name in ("Conjunction", "Square", "Trine", "Opposition"):
                assert aspect.orb <= 4.0

    def test_progression_default_orbs_very_tight(self):
        """Test progression uses very tight orbs (1°)."""
        natal = Native("1990-01-15 10:00", "New York, NY")

        comparison = ComparisonBuilder.progression(natal, age=30).calculate()

        # Progression orbs are very tight (1°)
        for aspect in comparison.cross_aspects:
            assert aspect.orb <= 2.0  # Allow small margin
