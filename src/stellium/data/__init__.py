"""
Stellium data package.

Provides:
- Notable births and events registry
- Ephemeris path management
- Package data access
"""

# Import paths module directly (no circular dependencies)
from stellium.data.paths import (
    get_ephe_dir,
    get_user_data_dir,
    get_user_ephe_dir,
    has_ephe_file,
    initialize_ephemeris,
)


# Lazy import for registry to avoid circular imports
# (registry imports from core.native which imports from engines)
def get_notable_registry():
    """Get the global notable registry instance (lazy import)."""
    from stellium.data.registry import get_notable_registry as _get_registry

    return _get_registry()


def __getattr__(name: str):
    """Lazy import for NotableRegistry class."""
    if name == "NotableRegistry":
        from stellium.data.registry import NotableRegistry

        return NotableRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Notables
    "NotableRegistry",
    "get_notable_registry",
    # Paths
    "get_ephe_dir",
    "get_user_data_dir",
    "get_user_ephe_dir",
    "has_ephe_file",
    "initialize_ephemeris",
]
