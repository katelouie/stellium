"""
Notable births and events data package.

Provides access to curated birth and event data for famous individuals
and historical moments.
"""

from stellium.data.registry import NotableRegistry, get_notable_registry

__all__ = [
    "NotableRegistry",
    "get_notable_registry",
]
