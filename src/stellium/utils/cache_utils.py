"""Cache utilities for easy access from within stellium package."""

from .cache import cache_info, cache_size, clear_cache


def print_cache_info():
    """Print detailed cache information."""
    info = cache_info()
    print("🗂️  Stellium Cache Information")
    print("=" * 40)
    print(f"Cache Directory: {info['cache_directory']}")
    print(
        f"Max Age: {info['max_age_seconds']} seconds ({info['max_age_seconds'] / 3600:.1f} hours)"
    )
    print(f"Total Files: {info['total_cached_files']}")
    print(f"Total Size: {info['cache_size_mb']} MB")
    print()
    print("By Type:")
    for cache_type, count in info["by_type"].items():
        print(f"  {cache_type}: {count} files")
    print()


def clear_ephemeris_cache():
    """Clear only the ephemeris cache."""
    removed = clear_cache("ephemeris")
    print(f"🗑️  Cleared {removed} ephemeris cache files")
    return removed


def clear_geocoding_cache():
    """Clear only the geocoding cache."""
    removed = clear_cache("geocoding")
    print(f"🗑️  Cleared {removed} geocoding cache files")
    return removed


def clear_all_cache():
    """Clear all cache files."""
    removed = clear_cache()
    print(f"🗑️  Cleared {removed} total cache files")
    return removed


def get_cache_stats():
    """Get cache statistics as a dictionary."""
    return {"info": cache_info(), "sizes": cache_size()}
