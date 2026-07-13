"""Caching utilities for expensive operations.

**This is a cache for things that are slow because they leave the process** —
geocoding, which is a network call. It is emphatically *not* for Swiss Ephemeris
positions: a `swe.calc_ut` is microseconds, and a pickle round-trip costs more than
the calculation it replaces. Caching them to disk measured **13x slower** than just
recomputing, so the ephemeris engines memoize in process instead (see
`engines/ephemeris.py`). If you are about to add `@cached` to something, first check
that the thing you are caching is slower than a file read.

Two rules this module learned the hard way:

1. **The cache directory is absolute, and it lives under the Stellium home.**
   ``~/.stellium/cache/``, beside ``~/.stellium/ephe/``, overridable with
   ``STELLIUM_CACHE_DIR`` exactly as the ephemeris is with ``STELLIUM_EPHE_PATH`` —
   so a portable install redirects *one* home, not two unrelated platform
   directories. It used to default to the *relative* `".cache"`, which
   `Path.mkdir()` resolves against the current working directory, so the cache
   materialised wherever you happened to launch Python. Eight of them accumulated
   across the repo, including one *inside the package*.
2. **Nothing is created at import.** The default instance is now built lazily; the
   directories are made on first write. Importing a library must not touch the disk.
"""

import hashlib
import json
import pickle
import re
import time
import warnings
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from stellium._logging import get_logger

log = get_logger("utils.cache")

CACHE_TYPES = ("ephemeris", "geocoding", "general")

# CPython's default repr, e.g. "<SwissEphemerisEngine object at 0x104f2a390>". The
# hex is the object's address: unstable across instances and across processes.
# Match on the address suffix alone — the qualname in front may itself contain '>'
# (a class defined inside a function reprs as "...<locals>.Engine object at 0x...").
_IDENTITY_REPR = re.compile(r" object at 0x[0-9a-fA-F]+>")


class UnstableCacheKey(TypeError):
    """An argument has no stable textual form, so it cannot be part of a cache key.

    Almost always means `@cached` was put on a *method*, making `self` part of the
    key. Cache a module-level function of plain values instead, or memoize in memory.
    """


def _stable_repr(obj: Any) -> str:
    """Fallback stringifier for `json.dumps`, minus the footguns."""
    text = repr(obj)
    if _IDENTITY_REPR.search(text):
        raise UnstableCacheKey(
            f"{type(obj).__name__} has no stable repr — its default repr embeds a "
            f"memory address ({text!r}), which would change every run and make the "
            f"cache entry unfindable. Do not apply @cached to a method (`self` is "
            f"args[0]); cache a function of plain values, or memoize in process."
        )
    return text


def default_cache_dir() -> Path:
    """The cache directory, as an absolute path: ``~/.stellium/cache/``.

    Set ``STELLIUM_CACHE_DIR`` to move it — the same shape as ``STELLIUM_EPHE_PATH``,
    so a portable install redirects one Stellium home rather than two unrelated
    platform directories. See :func:`stellium.data.paths.resolve_cache_dir`.

    Imported lazily to keep `utils` free of an import-time dependency on `data`.
    """
    from stellium.data.paths import resolve_cache_dir

    return resolve_cache_dir()


class Cache:
    """File-based cache for operations that are slower than touching the disk."""

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        max_age_seconds: int = 86400,
        enabled: bool = True,
    ):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to the per-user
                cache directory (see :func:`default_cache_dir`). A *relative* path
                is resolved against the current working directory, which is almost
                never what you want — pass an absolute path.
            max_age_seconds: Maximum age of cache entries in seconds (default: 24 hours)
            enabled: Whether caching is enabled (useful for debugging)
        """
        self.cache_dir = (
            default_cache_dir() if cache_dir is None else Path(cache_dir).expanduser()
        )
        self.max_age = max_age_seconds
        self.enabled = enabled

        # NOT created here. Constructing a Cache — which importing stellium used to
        # do at module scope — must not create directories on someone's disk.

    def _ensure_dir(self, cache_type: str) -> Path:
        """Create the cache directory on first write, not before."""
        subdir = self.cache_dir / cache_type
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a cache key from function name and arguments.

        Every argument must have a *stable* textual form. `json.dumps(default=str)`
        will happily stringify an object with no `__repr__` as
        ``<Foo object at 0x104f2a390>`` — embedding its **memory address** in the
        key, so the entry can never be found again by any other instance or process.
        That is exactly what happened when `@cached` was applied to *methods*: `self`
        was `args[0]`, every lookup missed, every call wrote a new file, and the
        cache grew without bound while never once being read. Refuse such arguments
        rather than silently poisoning the key.
        """
        key_data = {"func": func_name, "args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=_stable_repr)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / cache_type / f"{key}.pickle"

    def get(self, cache_type: str, key: str) -> Any | None:
        """Get a value from cache if it exists and is not expired."""
        cache_path = self._get_cache_path(cache_type, key)

        if not cache_path.exists():
            return None

        try:
            # Check if cache is expired
            if time.time() - cache_path.stat().st_mtime > self.max_age:
                cache_path.unlink()  # Remove expired cache
                return None

            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            # If there's any error reading cache, remove it
            try:
                cache_path.unlink()
            except Exception:
                pass
            return None

    def set(self, cache_type: str, key: str, value: Any) -> None:
        """Store a value in cache."""
        try:
            self._ensure_dir(cache_type)
            cache_path = self._get_cache_path(cache_type, key)
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)
        except Exception as e:
            log.warning("Could not write to cache: %s", e)

    def clear(self, cache_type: str | None = None) -> int:
        """Clear cache entries. Returns number of files removed."""
        removed = 0

        if cache_type:
            cache_subdir = self.cache_dir / cache_type
            if cache_subdir.exists():
                for cache_file in cache_subdir.glob("*.pickle"):
                    try:
                        cache_file.unlink()
                        removed += 1
                    except Exception:
                        pass
        else:
            # Clear all cache
            for cache_file in self.cache_dir.rglob("*.pickle"):
                try:
                    cache_file.unlink()
                    removed += 1
                except Exception:
                    pass

        return removed

    def size(self, cache_type: str | None = None) -> dict[str, int]:
        """Get cache size information."""
        sizes = {}

        if cache_type:
            cache_subdir = self.cache_dir / cache_type
            if cache_subdir.exists():
                sizes[cache_type] = len(list(cache_subdir.glob("*.pickle")))
        else:
            for subdir in ["ephemeris", "geocoding", "general"]:
                cache_subdir = self.cache_dir / subdir
                if cache_subdir.exists():
                    sizes[subdir] = len(list(cache_subdir.glob("*.pickle")))

        return sizes

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics including:
            - total_files: Number of cached files
            - total_size_bytes: Total cache size
            - by_type: Breakdown by cache type
            - hit_rate: Cache hit rate (if tracking enabled)
        """
        if not self.enabled:
            return {"enabled": False}

        sizes = self.size()
        total_files = sum(sizes.values())

        # Calculate total size
        cache_dir_size = 0
        for cache_file in self.cache_dir.rglob("*.pickle"):
            try:
                cache_dir_size += cache_file.stat().st_size
            except Exception:
                pass

        return {
            "enabled": True,
            "cache_directory": str(self.cache_dir),
            "max_age_seconds": self.max_age,
            "total_cached_files": total_files,
            "cache_size_bytes": cache_dir_size,
            "cache_size_mb": round(cache_dir_size / (1024 * 1024), 2),
            "by_type": sizes,
        }


# The default instance is built on first use, NOT at import. `_default_cache = Cache()`
# at module scope used to run `mkdir(".cache/ephemeris")` relative to the current
# working directory the moment anyone imported stellium — which is how eight stray
# cache directories, one of them 145 MB inside the package itself, came to exist.
_default_cache: Cache | None = None


def get_default_cache() -> Cache:
    """Get the default global cache instance, creating it on first use."""
    global _default_cache
    if _default_cache is None:
        _default_cache = Cache()
    return _default_cache


def set_default_cache(cache: Cache | None) -> None:
    """Replace the default cache (pass None to reset). Mainly for tests."""
    global _default_cache
    _default_cache = cache


def cached(
    cache_type: str = "general",
    max_age_seconds: int = 86400,
    cache_instance: Cache | None = None,
):
    """Decorator to cache function results **to disk**.

    Only worth it when the call is slower than a file read — a network round-trip,
    say. It is *not* worth it for arithmetic: caching Swiss Ephemeris positions this
    way measured 13x slower than recomputing them.

    Decorate a **module-level function of plain values**. Decorating a method makes
    `self` part of the key, and `self`'s default repr contains its memory address —
    the entry could then never be found again, so every call would miss and write a
    new file forever. That is now refused loudly rather than done silently.

    Args:
        cache_type: Type of cache ('ephemeris', 'geocoding', 'general')
        max_age_seconds: Maximum age of cache entries in seconds
        cache_instance: Custom cache instance (uses global if None)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_instance or get_default_cache()

            if not cache.enabled:
                return func(*args, **kwargs)

            try:
                key = cache._make_key(func.__name__, args, kwargs)
            except UnstableCacheKey as exc:
                # Degrade to an uncached call rather than crashing the caller — but
                # say so, because a silently-poisoned key is what caused the mess.
                warnings.warn(
                    f"{func.__qualname__} cannot be disk-cached: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                return func(*args, **kwargs)

            cached_result = cache.get(cache_type, key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_type, key, result)

            return result

        wrapper.clear_cache = lambda: get_default_cache().clear(cache_type)
        wrapper.cache_size = lambda: get_default_cache().size(cache_type)

        return wrapper

    return decorator


def clear_cache(cache_type: str | None = None) -> int:
    """Clear cache entries. Returns number of files removed."""
    return get_default_cache().clear(cache_type)


def cache_size(cache_type: str | None = None) -> dict[str, int]:
    """Get cache size information."""
    return get_default_cache().size(cache_type)


def cache_info() -> dict[str, Any]:
    """Get comprehensive cache information."""
    return get_default_cache().get_stats()
