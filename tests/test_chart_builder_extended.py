"""
Extended tests for ChartBuilder to improve code coverage.

Covers:
- from_notable() factory method
- with_sidereal() and with_tropical() methods
- with_name() method
- with_house_systems() validation
- add_house_system() method
- with_unknown_time() and unknown time chart calculation
- with_cache() configuration
- _get_cache() method
- Components and analyzers
- Sidereal zodiac calculations
"""

import pytest

from stellium.components import MidpointCalculator
from stellium.core.builder import ChartBuilder
from stellium.core.config import CalculationConfig
from stellium.core.models import UnknownTimeChart
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.houses import (
    EqualHouses,
    KochHouses,
    PlacidusHouses,
    WholeSignHouses,
)
from stellium.engines.orbs import SimpleOrbEngine
from stellium.engines.patterns import AspectPatternAnalyzer
from stellium.utils.cache import Cache

pytestmark = pytest.mark.slow


class TestChartBuilderFromNotable:
    """Tests for ChartBuilder.from_notable() factory method."""

    def test_from_notable_valid_name(self):
        """Test from_notable with a valid notable name."""
        chart = ChartBuilder.from_notable("Albert Einstein").calculate()

        assert chart is not None
        assert len(chart.positions) > 0
        assert chart.metadata.get("name") == "Albert Einstein"

    def test_from_notable_case_insensitive(self):
        """Test from_notable is case-insensitive."""
        chart1 = ChartBuilder.from_notable("Albert Einstein").calculate()
        chart2 = ChartBuilder.from_notable("albert einstein").calculate()

        # Should produce same chart
        assert chart1.datetime.julian_day == chart2.datetime.julian_day

    def test_from_notable_invalid_name(self):
        """Test from_notable raises ValueError for unknown name."""
        with pytest.raises(ValueError) as exc_info:
            ChartBuilder.from_notable("Nonexistent Person XYZ123")

        assert "No notable found" in str(exc_info.value)
        assert "Registry contains" in str(exc_info.value)

    def test_from_notable_sets_name_on_chart(self):
        """Test that from_notable automatically sets the chart name."""
        builder = ChartBuilder.from_notable("Albert Einstein")
        chart = builder.calculate()

        assert chart.metadata.get("name") == "Albert Einstein"


class TestChartBuilderZodiacMethods:
    """Tests for sidereal and tropical zodiac methods."""

    def test_with_sidereal_default_lahiri(self):
        """Test with_sidereal() uses Lahiri ayanamsa by default."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_sidereal().calculate()

        assert chart.zodiac_type.value == "sidereal"
        assert chart.ayanamsa == "lahiri"
        assert chart.ayanamsa_value is not None
        assert chart.ayanamsa_value > 0  # Should be positive offset

    def test_with_sidereal_fagan_bradley(self):
        """Test with_sidereal() with Fagan-Bradley ayanamsa."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native).with_sidereal("fagan_bradley").calculate()
        )

        assert chart.zodiac_type.value == "sidereal"
        assert chart.ayanamsa == "fagan_bradley"

    def test_with_tropical_resets_sidereal(self):
        """Test with_tropical() resets a previous with_sidereal() call."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_sidereal("lahiri")
            .with_tropical()  # Reset to tropical
            .calculate()
        )

        assert chart.zodiac_type.value == "tropical"
        assert chart.ayanamsa is None
        assert chart.ayanamsa_value is None

    def test_with_tropical_default(self):
        """Test that tropical is the default zodiac."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).calculate()

        assert chart.zodiac_type.value == "tropical"


class TestChartBuilderNameMethod:
    """Tests for with_name() method."""

    def test_with_name_sets_metadata(self):
        """Test with_name() sets name in chart metadata."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_name("Kate Louie").calculate()

        assert chart.metadata.get("name") == "Kate Louie"

    def test_with_name_overrides_native_name(self):
        """Test with_name() can override name from Native."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA", name="Original Name")
        chart = ChartBuilder.from_native(native).with_name("New Name").calculate()

        assert chart.metadata.get("name") == "New Name"

    def test_with_name_chainable(self):
        """Test with_name() returns builder for chaining."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native).with_name("Test")

        assert isinstance(builder, ChartBuilder)


class TestChartBuilderHouseSystems:
    """Tests for house system configuration methods."""

    def test_with_house_systems_replaces_all(self):
        """Test with_house_systems() replaces all house systems."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_house_systems([WholeSignHouses(), KochHouses()])
            .calculate()
        )

        assert "Whole Sign" in chart.house_systems
        assert "Koch" in chart.house_systems
        # Default Placidus should be replaced
        assert len(chart.house_systems) == 2

    def test_with_house_systems_empty_raises_error(self):
        """Test with_house_systems() with empty list raises ValueError."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")

        with pytest.raises(ValueError) as exc_info:
            ChartBuilder.from_native(native).with_house_systems([])

        assert "cannot be empty" in str(exc_info.value)

    def test_add_house_system_appends(self):
        """Test add_house_system() appends to existing systems."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .add_house_system(WholeSignHouses())
            .calculate()
        )

        # Should have default Placidus plus added Whole Sign
        assert "Placidus" in chart.house_systems
        assert "Whole Sign" in chart.house_systems

    def test_add_house_system_chainable(self):
        """Test add_house_system() returns builder for chaining."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = (
            ChartBuilder.from_native(native)
            .add_house_system(WholeSignHouses())
            .add_house_system(EqualHouses())
        )

        assert isinstance(builder, ChartBuilder)


class TestChartBuilderUnknownTime:
    """Tests for unknown birth time handling."""

    def test_with_unknown_time_returns_unknown_time_chart(self):
        """Test with_unknown_time() returns UnknownTimeChart."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_unknown_time().calculate()

        assert isinstance(chart, UnknownTimeChart)

    def test_unknown_time_chart_has_no_houses(self):
        """Test UnknownTimeChart has empty house systems."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_unknown_time().calculate()

        assert chart.house_systems == {}
        assert chart.house_placements == {}

    def test_unknown_time_chart_has_moon_range(self):
        """Test UnknownTimeChart includes moon_range."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_unknown_time().calculate()

        assert chart.moon_range is not None
        assert chart.moon_range.start_longitude is not None
        assert chart.moon_range.end_longitude is not None
        assert chart.moon_range.noon_longitude is not None

    def test_unknown_time_metadata_flag(self):
        """Test UnknownTimeChart has time_unknown flag in metadata."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_unknown_time().calculate()

        assert chart.metadata.get("time_unknown") is True

    def test_unknown_time_with_aspects(self):
        """Test UnknownTimeChart can calculate aspects."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_unknown_time()
            .with_aspects()
            .calculate()
        )

        # Should have aspects calculated using noon positions
        assert len(chart.aspects) > 0

    def test_unknown_time_moon_crosses_boundary(self):
        """Test moon_range correctly detects sign boundary crossing."""
        # Find a date where Moon might cross sign boundary
        # Moon travels ~13 degrees per day
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_unknown_time().calculate()

        # Check that crosses_sign_boundary is a boolean
        assert isinstance(chart.moon_range.crosses_sign_boundary, bool)

    def test_from_details_with_time_unknown_flag(self):
        """Test from_details with time_unknown parameter."""
        chart = ChartBuilder.from_details(
            "1994-01-06",
            "Palo Alto, CA",
            time_unknown=True,
        ).calculate()

        assert isinstance(chart, UnknownTimeChart)

    # ------------------------------------------------------------------
    # Regression: unknown-time charts share the main calculate() pipeline.
    # These previously failed because the no-time path was a separate fork
    # that silently dropped config, analyzers, the manifest, and metadata.
    # ------------------------------------------------------------------

    def test_unknown_time_respects_sidereal_config(self):
        """Unknown-time charts must honor .with_sidereal().

        The old fork called the ephemeris without the config, so a sidereal
        request silently produced tropical positions and dropped the zodiac
        metadata. Positions must match a sidereal known-time (noon) chart and
        differ from a tropical one; the zodiac metadata must survive.
        """
        known_sid = (
            ChartBuilder.from_details("1994-01-06 12:00", "Palo Alto, CA")
            .with_sidereal("lahiri")
            .calculate()
        )
        unknown_sid = (
            ChartBuilder.from_details("1994-01-06 12:00", "Palo Alto, CA")
            .with_sidereal("lahiri")
            .with_unknown_time()
            .calculate()
        )
        unknown_trop = ChartBuilder.from_details(
            "1994-01-06 12:00", "Palo Alto, CA", time_unknown=True
        ).calculate()

        sun_sid = unknown_sid.get_object("Sun").longitude
        # Matches the sidereal known chart (same instant)...
        assert abs(sun_sid - known_sid.get_object("Sun").longitude) < 0.01
        # ...and is shifted from tropical by roughly the ayanamsa (~24 deg).
        assert abs(sun_sid - unknown_trop.get_object("Sun").longitude) > 1.0

        # Zodiac metadata must survive on the frozen model (gap F).
        assert unknown_sid.zodiac_type == known_sid.zodiac_type
        assert unknown_sid.ayanamsa == "lahiri"
        assert unknown_sid.ayanamsa_value is not None

    def test_unknown_time_runs_analyzers(self):
        """add_analyzer() must run on unknown-time charts (gap C)."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_aspects()
            .with_unknown_time()
            .add_analyzer(AspectPatternAnalyzer())
            .calculate()
        )
        assert "aspect_patterns" in chart.metadata

    def test_unknown_time_builds_component_manifest(self):
        """Component manifest must be populated on unknown charts (gap D)."""
        native = Native("1994-01-06", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_unknown_time()
            .add_component(MidpointCalculator(calculate_all=True))
            .calculate()
        )
        assert "Midpoints" in chart.available_components()

    def test_unknown_time_injects_extra_metadata(self):
        """External _extra_metadata must be injected, e.g. ReturnBuilder (gap E)."""
        native = Native("1994-01-06", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native).with_unknown_time()
        builder._extra_metadata = {"return_number": 7}
        chart = builder.calculate()
        assert chart.metadata.get("return_number") == 7

    def test_known_and_unknown_share_pipeline(self):
        """Structural anti-drift guard: an unknown-time chart must carry the
        same computed data as its known-time (noon) twin -- components,
        analyzers, declination aspects, and zodiac metadata -- differing only
        in houses/angles. If the two calculate paths ever fork again, this
        test fails.
        """

        def build(unknown: bool):
            b = (
                ChartBuilder.from_details("1994-01-06 12:00", "Palo Alto, CA")
                .with_sidereal("lahiri")
                .with_aspects()
                .with_declination_aspects(orb=1.0)
                .add_component(MidpointCalculator(calculate_all=True))
                .add_analyzer(AspectPatternAnalyzer())
            )
            if unknown:
                b = b.with_unknown_time()
            return b.calculate()

        known = build(False)
        unknown = build(True)

        # Same optional data present on both.
        assert unknown.available_components() == known.available_components()
        assert "aspect_patterns" in unknown.metadata
        assert len(unknown.declination_aspects) == len(known.declination_aspects)
        assert len(unknown.declination_aspects) > 0
        # Same zodiac metadata (gaps A + F).
        assert unknown.zodiac_type == known.zodiac_type
        assert unknown.ayanamsa == known.ayanamsa
        assert unknown.ayanamsa_value is not None

        # Differ only in houses/angles + type.
        assert known.get_houses() is not None
        assert unknown.get_houses() is None
        assert known.is_time_unknown is False
        assert unknown.is_time_unknown is True

    def test_unknown_time_entry_points_agree(self):
        """with_unknown_time() and from_details(time_unknown=True) must produce
        identical positions -- they share one noon-normalizer.
        """
        via_method = (
            ChartBuilder.from_details("1994-01-06 03:15", "Palo Alto, CA")
            .with_unknown_time()
            .calculate()
        )
        via_ctor = ChartBuilder.from_details(
            "1994-01-06 03:15", "Palo Alto, CA", time_unknown=True
        ).calculate()
        for name in ("Sun", "Moon", "Mars"):
            assert (
                abs(
                    via_method.get_object(name).longitude
                    - via_ctor.get_object(name).longitude
                )
                < 1e-9
            )

    def test_component_failure_propagates_on_known_but_not_unknown(self):
        """House-dependent components must fail-soft only on unknown-time charts.

        On a known-time chart a component failure is a genuine bug and must
        propagate; on an unknown-time chart it is expected (no houses) and is
        skipped so the chart still builds.
        """

        class ExplodingComponent:
            component_name = "Exploder"

            def calculate(self, datetime, location, positions, houses, placements):
                raise RuntimeError("boom")

        native = Native("1994-01-06", "Palo Alto, CA")

        # Known-time: the error must surface.
        with pytest.raises(RuntimeError, match="boom"):
            ChartBuilder.from_native(native).add_component(
                ExplodingComponent()
            ).calculate()

        # Unknown-time: swallowed; the chart still builds.
        chart = (
            ChartBuilder.from_native(native)
            .with_unknown_time()
            .add_component(ExplodingComponent())
            .calculate()
        )
        assert isinstance(chart, UnknownTimeChart)


class TestChartBuilderCacheConfiguration:
    """Tests for cache configuration methods."""

    def test_with_cache_custom_instance(self):
        """Test with_cache() with custom Cache instance."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            custom_cache = Cache(cache_dir=tmpdir, max_age_seconds=3600)

            native = Native("1994-01-06 11:47", "Palo Alto, CA")
            builder = ChartBuilder.from_native(native).with_cache(cache=custom_cache)

            assert builder._cache is custom_cache

    def test_with_cache_creates_new_cache(self):
        """Test with_cache() creates new Cache when none provided."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            native = Native("1994-01-06 11:47", "Palo Alto, CA")
            builder = ChartBuilder.from_native(native).with_cache(
                cache_dir=tmpdir,
                max_age_seconds=7200,
            )

            assert builder._cache is not None
            assert builder._cache.max_age == 7200

    def test_with_cache_disabled(self):
        """Test with_cache() can disable caching."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native).with_cache(enabled=False)

        assert builder._cache is not None
        assert builder._cache.enabled is False

    def test_get_cache_returns_default_when_none_set(self):
        """Test _get_cache() returns default cache when none configured."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native)

        cache = builder._get_cache()
        assert cache is not None


class TestChartBuilderWithConfig:
    """Tests for with_config() method."""

    def test_with_config_custom_config(self):
        """Test with_config() accepts custom CalculationConfig."""
        config = CalculationConfig(
            include_chiron=False,
            include_nodes=False,
        )

        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_config(config).calculate()

        # Chiron and True Node should not be in positions
        position_names = [p.name for p in chart.positions]
        assert "Chiron" not in position_names
        assert "True Node" not in position_names


class TestChartBuilderAspectsAndOrbs:
    """Tests for aspect and orb configuration."""

    def test_with_aspects_default_engine(self):
        """Test with_aspects() with no argument uses ModernAspectEngine."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = ChartBuilder.from_native(native).with_aspects().calculate()

        assert len(chart.aspects) > 0

    def test_with_aspects_custom_engine(self):
        """Test with_aspects() with custom engine."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        custom_engine = ModernAspectEngine()
        chart = ChartBuilder.from_native(native).with_aspects(custom_engine).calculate()

        assert len(chart.aspects) > 0

    def test_with_orbs_default_engine(self):
        """Test with_orbs() with no argument uses SimpleOrbEngine."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native).with_orbs()

        assert builder._orb_engine is not None

    def test_with_orbs_custom_engine(self):
        """Test with_orbs() with custom orb engine."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        custom_orbs = SimpleOrbEngine(orb_map={"Conjunction": 10.0, "Trine": 8.0})
        builder = ChartBuilder.from_native(native).with_aspects().with_orbs(custom_orbs)

        assert builder._orb_engine is custom_orbs


class TestChartBuilderComponents:
    """Tests for add_component() method."""

    def test_add_component_arabic_parts(self):
        """Test add_component() with ArabicPartsCalculator."""
        from stellium.components.arabic_parts import ArabicPartsCalculator

        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .add_component(ArabicPartsCalculator())
            .calculate()
        )

        # Arabic parts should be in positions
        position_names = [p.name for p in chart.positions]
        assert "Part of Fortune" in position_names

    def test_add_component_chainable(self):
        """Test add_component() returns builder for chaining."""
        from stellium.components.arabic_parts import ArabicPartsCalculator

        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = ChartBuilder.from_native(native).add_component(
            ArabicPartsCalculator()
        )

        assert isinstance(builder, ChartBuilder)


class TestChartBuilderAnalyzers:
    """Tests for add_analyzer() method."""

    def test_add_analyzer_patterns(self):
        """Test add_analyzer() with AspectPatternAnalyzer."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_aspects()
            .add_analyzer(AspectPatternAnalyzer())
            .calculate()
        )

        # Pattern analysis should be in metadata
        assert "aspect_patterns" in chart.metadata

    def test_add_analyzer_chainable(self):
        """Test add_analyzer() returns builder for chaining."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        builder = (
            ChartBuilder.from_native(native)
            .with_aspects()
            .add_analyzer(AspectPatternAnalyzer())
        )

        assert isinstance(builder, ChartBuilder)


class TestChartBuilderNativeTimeUnknownPropagation:
    """Test that time_unknown flag propagates from Native to ChartBuilder."""

    def test_native_time_unknown_propagates(self):
        """Test Native with time_unknown creates UnknownTimeChart."""
        native = Native("1994-01-06", "Palo Alto, CA", time_unknown=True)
        chart = ChartBuilder.from_native(native).calculate()

        assert isinstance(chart, UnknownTimeChart)

    def test_native_time_unknown_sets_builder_flag(self):
        """Test Native with time_unknown sets builder _time_unknown flag."""
        native = Native("1994-01-06", "Palo Alto, CA", time_unknown=True)
        builder = ChartBuilder.from_native(native)

        assert builder._time_unknown is True


class TestChartBuilderDuplicateHouseSystems:
    """Test handling of duplicate house systems."""

    def test_duplicate_house_system_not_calculated_twice(self):
        """Test that duplicate house systems are only calculated once."""
        native = Native("1994-01-06 11:47", "Palo Alto, CA")
        chart = (
            ChartBuilder.from_native(native)
            .with_house_systems([PlacidusHouses(), PlacidusHouses()])
            .calculate()
        )

        # Should only have one Placidus entry
        assert list(chart.house_systems.keys()).count("Placidus") == 1
