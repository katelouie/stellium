"""
Centralized data path management for Stellium.

This module handles:
1. User data directory (~/.stellium/) for ephemeris files and user data
2. Bundled package data (notables, essential ephemeris files)
3. First-run initialization (copying bundled ephemeris to user directory)

The user directory structure:
    ~/.stellium/
    ├── ephe/           # Swiss Ephemeris files (copied from package + user downloads)
    │   ├── sepl_18.se1
    │   ├── semo_18.se1
    │   └── ...
    └── cache/          # Future: cache files
"""

import importlib.resources
import os
import shutil
import sys
from pathlib import Path

import swisseph as swe

# User data directory
USER_DATA_DIR = Path.home() / ".stellium"
USER_EPHE_DIR = USER_DATA_DIR / "ephe"

# Package data locations (using importlib.resources)
PACKAGE_DATA_MODULE = "stellium.data"

# Essential ephemeris files bundled with the package (covers 1800-2400 CE)
ESSENTIAL_EPHE_FILES = [
    "sepl_18.se1",  # Planets 1800-2399
    "sepl_24.se1",  # Planets 2400-2999
    "semo_18.se1",  # Moon 1800-2399
    "semo_24.se1",  # Moon 2400-2999
    "seas_18.se1",  # Asteroids 1800-2399
    "seas_24.se1",  # Asteroids 2400-2999
    "sefstars.txt",  # Fixed stars catalog
]

# Track whether ephemeris path has been initialized this session
_ephe_initialized = False


def get_user_data_dir() -> Path:
    """
    Get the user data directory, creating it if necessary.

    Returns:
        Path to ~/.stellium/
    """
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return USER_DATA_DIR


def get_user_ephe_dir() -> Path:
    """
    Get the user ephemeris directory, creating it if necessary.

    Returns:
        Path to ~/.stellium/ephe/
    """
    USER_EPHE_DIR.mkdir(parents=True, exist_ok=True)
    return USER_EPHE_DIR


def _get_bundled_ephe_path() -> Path | None:
    """
    Get the path to bundled ephemeris files in the package.

    Returns:
        Path to bundled swisseph/ephe/ directory, or None if not found
    """
    try:
        # Use importlib.resources to find the package data
        # For Python 3.9+, we use files() which returns a Traversable
        files = importlib.resources.files(PACKAGE_DATA_MODULE)
        ephe_path = files / "swisseph" / "ephe"

        # Check if it exists and has files
        # We need to convert to a real path for checking
        if hasattr(ephe_path, "_path"):
            # It's a real filesystem path
            real_path = Path(ephe_path._path)
            if real_path.exists():
                return real_path
        else:
            # Try to get a path via as_file context manager
            # This works for both filesystem and zip-packaged resources
            with importlib.resources.as_file(ephe_path) as path:
                if path.exists():
                    return path

        return None
    except (TypeError, FileNotFoundError, AttributeError):
        return None


def _copy_bundled_ephe_files() -> int:
    """
    Copy bundled ephemeris files to the user directory.

    Only copies files that don't already exist in the user directory.

    Returns:
        Number of files copied
    """
    bundled_path = _get_bundled_ephe_path()
    if bundled_path is None:
        return 0

    user_ephe = get_user_ephe_dir()
    copied = 0

    for filename in ESSENTIAL_EPHE_FILES:
        src = bundled_path / filename
        dst = user_ephe / filename

        if src.exists() and not dst.exists():
            try:
                shutil.copy2(src, dst)
                copied += 1
            except OSError as e:
                print(f"Warning: Could not copy {filename}: {e}", file=sys.stderr)

    return copied


def initialize_ephemeris() -> Path:
    """
    Initialize the ephemeris system.

    This function:
    1. Ensures the user ephe directory exists
    2. Copies bundled ephemeris files to user directory (first run only)
    3. Sets the Swiss Ephemeris path

    Call this once at startup or before any ephemeris calculations.

    Returns:
        Path to the ephemeris directory being used
    """
    global _ephe_initialized

    if _ephe_initialized:
        return USER_EPHE_DIR

    # Ensure user directory exists
    ephe_dir = get_user_ephe_dir()

    # Copy bundled files if needed (idempotent - skips existing)
    copied = _copy_bundled_ephe_files()
    if copied > 0:
        print(f"Stellium: Initialized {copied} ephemeris files in {ephe_dir}")

    # Set Swiss Ephemeris path
    swe.set_ephe_path(str(ephe_dir) + os.sep)

    _ephe_initialized = True
    return ephe_dir


def get_ephe_dir() -> Path:
    """
    Get the ephemeris directory, initializing if necessary.

    This is the main function that should be used throughout the codebase
    to get the ephemeris path.

    Returns:
        Path to the ephemeris directory
    """
    if not _ephe_initialized:
        initialize_ephemeris()
    return USER_EPHE_DIR


def reset_ephe_initialization() -> None:
    """
    Reset the ephemeris initialization flag.

    Useful for testing or if you need to reinitialize.
    """
    global _ephe_initialized
    _ephe_initialized = False


# Convenience function for checking if a specific ephemeris file exists
def has_ephe_file(filename: str) -> bool:
    """
    Check if a specific ephemeris file exists in the user directory.

    Args:
        filename: Name of the ephemeris file (e.g., "se136199.se1")

    Returns:
        True if the file exists
    """
    return (get_user_ephe_dir() / filename).exists()
