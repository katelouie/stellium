"""Caching utilities for expensive operations like Swiss Ephemeris and geocoding."""

import hashlib
import json
import pickle
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any


class Cache:
    """File-based cache for expensive operations."""

    def __init__(
        self,
        cache_dir: str = ".cache",
        max_age_seconds: int = 86400,
        enabled: bool = True,
    ):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            max_age_seconds: Maximum age of cache entries in seconds (default: 24 hours)
            enabled: Whether caching is enabled (useful for debugging)
        """
        self.cache_dir = Path(cache_dir)
        self.max_age = max_age_seconds
        self.enabled = enabled

        self.cache_dir.mkdir(exist_ok=True)

        # Create subdirectories for different types of cache
        (self.cache_dir / "ephemeris").mkdir(exist_ok=True)
        (self.cache_dir / "geocoding").mkdir(exist_ok=True)
        (self.cache_dir / "general").mkdir(exist_ok=True)

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a cache key from function name and arguments."""
        # Create a deterministic string from the arguments
        key_data = {"func": func_name, "args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
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
        cache_path = self._get_cache_path(cache_type, key)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"Warning: Could not write to cache: {e}")

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


# Create a default global instance (for backward compatibility)
_default_cache = Cache()


def cached(
    cache_type: str = "general",
    max_age_seconds: int = 86400,
    cache_instance: Cache | None = None,
):
    """Decorator to cache function results.

    Args:
        cache_type: Type of cache ('ephemeris', 'geocoding', 'general')
        max_age_seconds: Maximum age of cache entries in seconds
        cache_instance: Custom cache instance (uses global if None)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use provided cache instance or fall back to default
            cache = cache_instance or _default_cache

            if not cache.enabled:
                # Cache disabled - just execute function
                return func(*args, **kwargs)

            # Create cache key
            key = cache._make_key(func.__name__, args, kwargs)

            # Try to get from cache
            cached_result = cache.get(cache_type, key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_type, key, result)

            return result

        # Add cache management methods to the function
        wrapper.clear_cache = lambda: (_default_cache.clear(cache_type))
        wrapper.cache_size = lambda: (_default_cache.size(cache_type))

        return wrapper

    return decorator


def clear_cache(cache_type: str | None = None) -> int:
    """Clear cache entries. Returns number of files removed."""
    return _default_cache.clear(cache_type)


def cache_size(cache_type: str | None = None) -> dict[str, int]:
    """Get cache size information."""
    return _default_cache.size(cache_type)


def cache_info() -> dict[str, Any]:
    """Get comprehensive cache information."""
    return _default_cache.get_stats()


def get_default_cache() -> Cache:
    """Get the default global cache instance."""
    return _default_cache
