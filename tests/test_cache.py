"""Tests for the disk cache — mostly guards against the ways it went wrong.

The cache accumulated **18.5 million files** in one directory, and eight stray
`.cache/` directories across the repo, one of them 145 MB *inside the installed
package*. Three independent defects, each of which has a test here:

1. The default directory was the **relative** `".cache"`, which `Path.mkdir()`
   resolves against the current working directory — so the cache appeared wherever
   Python happened to be launched.
2. The default instance was constructed **at import**, so merely importing stellium
   created directories on disk.
3. `@cached` was applied to **methods**, so `self` was `args[0]` and its default repr
   — containing its **memory address** — went into the key. Every lookup missed,
   every call wrote a new file, and nothing was ever read back. The "cache" was a
   write-only log that grew forever, and it made chart building 13x *slower*.
"""

import subprocess
import sys

import pytest

from stellium.utils.cache import (
    Cache,
    UnstableCacheKey,
    cached,
    default_cache_dir,
)


class TestNoFilesystemSideEffectsAtImport:
    """Importing a library must not touch the disk."""

    def test_importing_stellium_creates_no_cache_directory(self, tmp_path):
        """`_default_cache = Cache()` at module scope used to mkdir on import.

        Run in a subprocess with cwd set to an empty directory: the only way to
        observe an import-time side effect honestly.
        """
        result = subprocess.run(
            [sys.executable, "-c", "import stellium"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

        created = [p.name for p in tmp_path.iterdir()]
        assert created == [], f"importing stellium created {created} in the cwd"

    def test_constructing_a_cache_creates_no_directory(self, tmp_path):
        target = tmp_path / "nope"
        Cache(cache_dir=target)
        assert not target.exists(), "Cache.__init__ created its directory eagerly"

    def test_directory_appears_only_on_first_write(self, tmp_path):
        target = tmp_path / "lazy"
        cache = Cache(cache_dir=target)

        assert cache.get("general", "missing") is None
        assert not target.exists(), "a cache *miss* created the directory"

        cache.set("general", "k", {"value": 1})
        assert (target / "general").is_dir()
        assert cache.get("general", "k") == {"value": 1}


class TestCacheDirectoryIsAbsolute:
    """The cache must not follow you around the filesystem."""

    def test_default_cache_dir_is_absolute(self):
        assert default_cache_dir().is_absolute()

    def test_default_cache_dir_does_not_depend_on_cwd(self, tmp_path, monkeypatch):
        before = default_cache_dir()
        monkeypatch.chdir(tmp_path)
        assert default_cache_dir() == before

    def test_default_cache_dir_is_not_the_current_directory(
        self, tmp_path, monkeypatch
    ):
        """The original bug, stated directly: `.cache` relative to wherever you are."""
        monkeypatch.chdir(tmp_path)
        assert default_cache_dir() != (tmp_path / ".cache")
        assert tmp_path not in default_cache_dir().parents

    def test_env_var_overrides_the_location(self, tmp_path, monkeypatch):
        monkeypatch.setenv("STELLIUM_CACHE_DIR", str(tmp_path / "custom"))
        assert default_cache_dir() == (tmp_path / "custom").resolve()


class TestCacheKeysMustBeStable:
    """A key that embeds a memory address can never be found again."""

    def test_key_is_stable_for_plain_values(self):
        cache = Cache()
        first = cache._make_key("f", ("Boston, MA", 42), {"x": 1.5})
        second = cache._make_key("f", ("Boston, MA", 42), {"x": 1.5})
        assert first == second

    def test_key_refuses_an_object_with_an_identity_repr(self):
        """This is the bug. json.dumps(default=str) rendered `self` as
        '<SwissEphemerisEngine object at 0x104f2a390>' — a *different key every run*.
        """

        class Engine:  # no __repr__, so it gets the default identity one
            pass

        cache = Cache()
        with pytest.raises(UnstableCacheKey, match="memory address"):
            cache._make_key("_calculate_single_position", (Engine(), 2451545.0), {})

    def test_two_instances_of_a_stable_type_agree(self):
        """A type with a real __repr__ is fine — it is identity that poisons keys."""

        class Config:
            def __repr__(self) -> str:
                return "Config(tropical)"

        cache = Cache()
        assert cache._make_key("f", (Config(),), {}) == cache._make_key(
            "f", (Config(),), {}
        )

    def test_cached_on_a_method_degrades_loudly_instead_of_growing_forever(
        self, tmp_path
    ):
        """It must warn and simply not cache — never silently write unfindable files."""
        cache = Cache(cache_dir=tmp_path)
        calls = []

        class Engine:
            @cached(cache_type="general", cache_instance=cache)
            def compute(self, x):
                calls.append(x)
                return x * 2

        engine = Engine()
        with pytest.warns(RuntimeWarning, match="cannot be disk-cached"):
            assert engine.compute(21) == 42

        assert list(tmp_path.rglob("*.pickle")) == [], (
            "an unstable key still wrote a file — this is the unbounded-growth bug"
        )


class TestCachedStillWorksForWhatItIsFor:
    """Geocoding — a network call keyed on a plain string — is the real use case."""

    def test_a_module_level_function_of_plain_values_caches_and_hits(self, tmp_path):
        cache = Cache(cache_dir=tmp_path)
        calls = []

        @cached(cache_type="geocoding", cache_instance=cache)
        def geocode(place: str) -> dict:
            calls.append(place)
            return {"lat": 42.36, "lon": -71.06}

        assert geocode("Boston, MA") == {"lat": 42.36, "lon": -71.06}
        assert geocode("Boston, MA") == {"lat": 42.36, "lon": -71.06}

        assert calls == ["Boston, MA"], "second call should have hit the cache"

    def test_the_hit_survives_a_fresh_cache_object(self, tmp_path):
        """The whole point: a *later process* must find what an earlier one wrote.

        The ephemeris cache never could, because its keys held a memory address.
        """
        calls = []

        def make():
            @cached(cache_type="geocoding", cache_instance=Cache(cache_dir=tmp_path))
            def geocode(place: str) -> dict:
                calls.append(place)
                return {"lat": 42.36}

            return geocode

        make()("Boston, MA")
        make()("Boston, MA")  # brand-new Cache instance, as a new process would have

        assert calls == ["Boston, MA"], (
            "a new Cache instance could not find the existing entry"
        )
