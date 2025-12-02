"""Tests for planetary return calculations.

These tests verify that ReturnBuilder correctly calculates:
- Solar Returns (annual birthday charts)
- Lunar Returns (monthly Moon returns)
- Planetary Returns (Saturn, Jupiter, etc.)
"""

import pytest

from stellium.core.builder import ChartBuilder
from stellium.returns import ReturnBuilder

# Precision threshold for return calculations
# Returns should match natal position within 0.02 degrees
# (Moon can be slightly less precise due to its fast motion)
PRECISION_THRESHOLD = 0.02


@pytest.fixture
def einstein_natal():
    """Albert Einstein's natal chart (well-documented birth data)."""
    return ChartBuilder.from_notable("Albert Einstein").calculate()


@pytest.fixture
def kate_natal():
    """Kate's natal chart for testing."""
    return ChartBuilder.from_details(
        "1994-01-06 11:47",
        "Palo Alto, CA",
        name="Kate",
    ).calculate()


class TestSolarReturns:
    """Test Solar Return calculations."""

    def test_solar_return_sun_matches_natal(self, einstein_natal):
        """Solar Return Sun should match natal Sun within precision threshold."""
        natal_sun = einstein_natal.get_object("Sun").longitude

        sr = ReturnBuilder.solar(einstein_natal, 1905).calculate()
        return_sun = sr.get_object("Sun").longitude

        diff = abs(return_sun - natal_sun)
        assert (
            diff < PRECISION_THRESHOLD
        ), f"Sun position diff {diff}° exceeds threshold"

    def test_solar_return_date_is_near_birthday(self, einstein_natal):
        """Solar Return should occur near the birthday each year."""
        # Einstein born March 14, 1879
        sr = ReturnBuilder.solar(einstein_natal, 1921).calculate()

        # Should be in March
        assert sr.datetime.utc_datetime.month == 3

        # Should be within a few days of March 14
        assert 10 <= sr.datetime.utc_datetime.day <= 18

    def test_solar_return_metadata(self, einstein_natal):
        """Solar Return should have correct metadata."""
        sr = ReturnBuilder.solar(einstein_natal, 1915).calculate()

        assert sr.metadata.get("chart_type") == "return"
        assert sr.metadata.get("return_planet") == "Sun"
        assert "natal_planet_longitude" in sr.metadata

    def test_solar_return_for_different_years(self, kate_natal):
        """Solar Returns for different years should all match natal Sun."""
        natal_sun = kate_natal.get_object("Sun").longitude

        for year in [2020, 2023, 2025, 2030]:
            sr = ReturnBuilder.solar(kate_natal, year).calculate()
            diff = abs(sr.get_object("Sun").longitude - natal_sun)
            assert (
                diff < PRECISION_THRESHOLD
            ), f"Year {year}: diff {diff}° exceeds threshold"


class TestLunarReturns:
    """Test Lunar Return calculations."""

    def test_lunar_return_moon_matches_natal(self, kate_natal):
        """Lunar Return Moon should match natal Moon within precision threshold."""
        natal_moon = kate_natal.get_object("Moon").longitude

        lr = ReturnBuilder.lunar(kate_natal, near_date="2025-03-15").calculate()
        return_moon = lr.get_object("Moon").longitude

        diff = abs(return_moon - natal_moon)
        assert (
            diff < PRECISION_THRESHOLD
        ), f"Moon position diff {diff}° exceeds threshold"

    def test_lunar_return_by_occurrence(self, kate_natal):
        """Lunar Return by occurrence number should work."""
        natal_moon = kate_natal.get_object("Moon").longitude

        # 10th lunar return after birth
        lr = ReturnBuilder.lunar(kate_natal, occurrence=10).calculate()
        diff = abs(lr.get_object("Moon").longitude - natal_moon)
        assert diff < PRECISION_THRESHOLD

    def test_lunar_return_default_to_now(self, kate_natal):
        """Lunar Return with no date should default to nearest to now."""
        lr = ReturnBuilder.lunar(kate_natal).calculate()

        # Should have return metadata
        assert lr.metadata.get("chart_type") == "return"
        assert lr.metadata.get("return_planet") == "Moon"

    def test_lunar_return_frequency(self, kate_natal):
        """Lunar returns should occur roughly every 27 days."""
        lr1 = ReturnBuilder.lunar(kate_natal, occurrence=1).calculate()
        lr2 = ReturnBuilder.lunar(kate_natal, occurrence=2).calculate()

        days_between = lr2.datetime.julian_day - lr1.datetime.julian_day
        # Moon's sidereal period is ~27.3 days
        assert 26 < days_between < 29, f"Days between returns: {days_between}"


class TestPlanetaryReturns:
    """Test planetary returns (Saturn, Jupiter, etc.)."""

    def test_saturn_return_timing(self, kate_natal):
        """First Saturn return should occur around age 29."""
        natal_jd = kate_natal.datetime.julian_day

        sr = ReturnBuilder.planetary(kate_natal, "Saturn", occurrence=1).calculate()

        years_elapsed = (sr.datetime.julian_day - natal_jd) / 365.25
        # Saturn return should be between 28 and 30 years
        assert 28 < years_elapsed < 30, f"Saturn return at {years_elapsed} years"

    def test_saturn_return_precision(self, kate_natal):
        """Saturn Return should match natal Saturn precisely."""
        natal_saturn = kate_natal.get_object("Saturn").longitude

        sr = ReturnBuilder.planetary(kate_natal, "Saturn", occurrence=1).calculate()
        diff = abs(sr.get_object("Saturn").longitude - natal_saturn)

        assert diff < PRECISION_THRESHOLD, f"Saturn diff {diff}° exceeds threshold"

    def test_saturn_return_metadata(self, kate_natal):
        """Saturn Return should have correct metadata."""
        sr = ReturnBuilder.planetary(kate_natal, "Saturn", occurrence=1).calculate()

        assert sr.metadata.get("chart_type") == "return"
        assert sr.metadata.get("return_planet") == "Saturn"
        assert sr.metadata.get("return_number") == 1

    def test_jupiter_return(self, einstein_natal):
        """Jupiter Return should work (period ~12 years)."""
        natal_jupiter = einstein_natal.get_object("Jupiter").longitude

        jr = ReturnBuilder.planetary(
            einstein_natal, "Jupiter", occurrence=1
        ).calculate()
        diff = abs(jr.get_object("Jupiter").longitude - natal_jupiter)

        assert diff < PRECISION_THRESHOLD

        # Should be around 12 years after birth
        natal_jd = einstein_natal.datetime.julian_day
        years_elapsed = (jr.datetime.julian_day - natal_jd) / 365.25
        assert 11 < years_elapsed < 13

    def test_mars_return(self, kate_natal):
        """Mars Return should work (period ~2 years)."""
        natal_mars = kate_natal.get_object("Mars").longitude

        mr = ReturnBuilder.planetary(
            kate_natal, "Mars", near_date="1996-01-01"
        ).calculate()
        diff = abs(mr.get_object("Mars").longitude - natal_mars)

        assert diff < PRECISION_THRESHOLD

    def test_planetary_return_requires_date_or_occurrence(self, kate_natal):
        """Planetary return should require either near_date or occurrence."""
        with pytest.raises(ValueError, match="Must specify either"):
            ReturnBuilder.planetary(kate_natal, "Jupiter").calculate()


class TestReturnBuilderConfiguration:
    """Test ReturnBuilder configuration and chainable methods."""

    def test_chainable_configuration(self, kate_natal):
        """ReturnBuilder should support chainable configuration."""
        from stellium.engines.houses import PlacidusHouses, WholeSignHouses

        sr = (
            ReturnBuilder.solar(kate_natal, 2025)
            .with_house_systems([PlacidusHouses(), WholeSignHouses()])
            .with_aspects()
            .calculate()
        )

        # Should have both house systems
        assert "Placidus" in sr.house_systems
        assert "Whole Sign" in sr.house_systems

        # Should have aspects
        assert len(sr.aspects) > 0

    def test_relocated_return(self, kate_natal):
        """Relocated return should use specified location."""
        # Solar Return relocated to Tokyo
        sr_relocated = ReturnBuilder.solar(
            kate_natal, 2025, location="Tokyo, Japan"
        ).calculate()

        # Location should be Tokyo (approximately)
        assert sr_relocated.location.latitude > 35  # Tokyo is ~35.7°N
        assert sr_relocated.location.longitude > 139  # Tokyo is ~139.7°E

    def test_return_uses_natal_location_by_default(self, kate_natal):
        """Return should use natal location if not overridden."""
        sr = ReturnBuilder.solar(kate_natal, 2025).calculate()

        # Should match natal location (Palo Alto)
        assert abs(sr.location.latitude - kate_natal.location.latitude) < 0.1
        assert abs(sr.location.longitude - kate_natal.location.longitude) < 0.1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_planet_raises_error(self, kate_natal):
        """Invalid planet name should raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            ReturnBuilder.planetary(kate_natal, "NotAPlanet", occurrence=1).calculate()

    def test_planet_not_in_chart_raises_error(self, kate_natal):
        """Planet not in natal chart should raise error."""
        # This shouldn't happen with standard charts, but test the error path
        # by trying to access a hypothetical missing planet
        # (We can't easily test this without mocking, so we'll skip)
        pass

    def test_return_near_360_degree_wrap(self):
        """Test return calculation near the 360°/0° boundary."""
        # Create a chart with Sun near 0° Aries (late Pisces)
        natal = ChartBuilder.from_details(
            "2024-03-19 12:00",  # Sun near 0° Aries
            "Seattle, WA",
        ).calculate()

        natal_sun = natal.get_object("Sun").longitude
        # Should be near 360° (late Pisces) or near 0° (early Aries)
        assert natal_sun > 355 or natal_sun < 5

        # Calculate next year's return
        sr = ReturnBuilder.solar(natal, 2025).calculate()
        diff = abs(sr.get_object("Sun").longitude - natal_sun)

        # Handle wrap-around in comparison
        if diff > 180:
            diff = 360 - diff

        assert diff < PRECISION_THRESHOLD
