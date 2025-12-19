"""
Atlas - Multi-chart PDF generation.

Generate PDF documents with multiple charts, one per page,
like an old-school astrologer's chart atlas.
"""

from stellium.visualization.atlas.builder import AtlasBuilder
from stellium.visualization.atlas.config import AtlasConfig, AtlasEntry

__all__ = ["AtlasBuilder", "AtlasConfig", "AtlasEntry"]
