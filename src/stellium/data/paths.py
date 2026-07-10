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
from pathlib import Path

import swisseph as swe

from stellium._logging import get_logger

log = get_logger("data.paths")

# User data directory
USER_DATA_DIR = Path.home() / ".stellium"
USER_EPHE_DIR = USER_DATA_DIR / "ephe"

# Environment variable that lets users override the ephemeris directory
# without touching code — handy for portable installs, read-only $HOME
# environments (Docker, Lambda, shared hosts), and for reusing an existing
# Swiss Ephemeris folder from another astrology tool.
ENV_EPHE_PATH = "STELLIUM_EPHE_PATH"

# Package data locations (using importlib.resources)
PACKAGE_DATA_MODULE = "stellium.data"

# Essential ephemeris files bundled with the package (covers 1800-2400 CE)
ESSENTIAL_EPHE_FILES = [
    "sepl_18.se1",  # Planets 1800-2399
    "sepl_24.se1",  # Planets 2400-2999
    "semo_18.se1",  # Moon 1800-2399
    "semo_24.se1",  # Moon 2400-2999
    "seas_12.se1",  # Asteroids (Chiron, Ceres, etc.) 1200-1799
    "seas_18.se1",  # Asteroids 1800-2399
    "seas_24.se1",  # Asteroids 2400-2999
    "sefstars.txt",  # Fixed stars catalog
]

# Track whether the ephemeris path has been initialized this session, and
# which directory is currently active. `_active_ephe_dir` is the source of
# truth once initialization has happened — it may differ from USER_EPHE_DIR
# when the user supplies a custom path.
_ephe_initialized = False
_active_ephe_dir: Path | None = None


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
                log.warning("Could not copy %s: %s", filename, e)

    return copied


def _resolve_ephe_path(ephe_path: str | Path | None) -> tuple[Path, bool]:
    """
    Resolve which ephemeris directory to use, following the precedence:

    1. Explicit ``ephe_path`` argument (highest priority)
    2. ``STELLIUM_EPHE_PATH`` environment variable
    3. Default ``~/.stellium/ephe/``

    Returns:
        A tuple of (resolved_path, is_custom). ``is_custom`` is True when the
        path came from an override — in that case we do not create the
        directory, copy bundled files into it, or otherwise touch its
        contents; we assume the caller already manages it.
    """
    if ephe_path is not None:
        return Path(ephe_path).expanduser(), True

    env_value = os.environ.get(ENV_EPHE_PATH, "").strip()
    if env_value:
        return Path(env_value).expanduser(), True

    return USER_EPHE_DIR, False


def initialize_ephemeris(ephe_path: str | Path | None = None) -> Path:
    """
    Initialize the ephemeris system.

    This function:
    1. Resolves which ephemeris directory to use (explicit arg >
       ``STELLIUM_EPHE_PATH`` env var > default ``~/.stellium/ephe/``)
    2. For the default location: ensures the directory exists and copies
       bundled ephemeris files to it (first run only)
    3. Sets the Swiss Ephemeris path via ``swe.set_ephe_path``

    When a custom path is supplied the directory is used as-is: Stellium
    will not create it or copy its bundled files into it. This makes it
    safe to point at an existing Swiss Ephemeris installation managed by
    another tool, or at a read-only folder.

    If ``initialize_ephemeris`` is called a second time with a different
    path, the ephemeris is re-initialized against the new location.

    Args:
        ephe_path: Optional override for the ephemeris directory. Accepts a
            ``str`` or ``pathlib.Path``. If omitted, falls back to the
            ``STELLIUM_EPHE_PATH`` environment variable, then to
            ``~/.stellium/ephe/``.

    Returns:
        Path to the ephemeris directory that is now active.
    """
    global _ephe_initialized, _active_ephe_dir

    resolved, is_custom = _resolve_ephe_path(ephe_path)

    # If already initialized against the same directory, nothing to do.
    if _ephe_initialized and _active_ephe_dir == resolved:
        return resolved

    if is_custom:
        # Custom path: use as-is. Do not create the directory, do not copy
        # bundled files — the caller is responsible for what lives there.
        # We still warn (not raise) if it doesn't exist so that misconfigured
        # paths fail loudly at the first calculation rather than silently.
        if not resolved.exists():
            log.warning(
                "Custom ephemeris path %s does not exist. Swiss Ephemeris "
                "calculations will fail until the directory is created and "
                "populated.",
                resolved,
            )
    else:
        # Default location: ensure the directory exists and populate it
        # with the essential bundled files on first run.
        resolved.mkdir(parents=True, exist_ok=True)
        copied = _copy_bundled_ephe_files()
        if copied > 0:
            log.info("Initialized %d ephemeris files in %s", copied, resolved)

    # Set Swiss Ephemeris path (trailing separator is required by the C lib).
    swe.set_ephe_path(str(resolved) + os.sep)

    _ephe_initialized = True
    _active_ephe_dir = resolved
    return resolved


def get_ephe_dir() -> Path:
    """
    Get the ephemeris directory, initializing if necessary.

    This is the main function that should be used throughout the codebase
    to get the ephemeris path. Respects any override previously set via
    :func:`initialize_ephemeris` or the ``STELLIUM_EPHE_PATH`` env var.

    Returns:
        Path to the ephemeris directory currently in use.
    """
    if not _ephe_initialized:
        initialize_ephemeris()
    assert _active_ephe_dir is not None  # just initialized
    return _active_ephe_dir


def reset_ephe_initialization() -> None:
    """
    Reset the ephemeris initialization flag.

    Useful for testing or if you need to reinitialize against a different
    directory.
    """
    global _ephe_initialized, _active_ephe_dir
    _ephe_initialized = False
    _active_ephe_dir = None


# Convenience function for checking if a specific ephemeris file exists
def has_ephe_file(filename: str) -> bool:
    """
    Check if a specific ephemeris file exists in the active directory.

    Args:
        filename: Name of the ephemeris file (e.g., "se136199.se1")

    Returns:
        True if the file exists in the directory currently being used.
    """
    return (get_ephe_dir() / filename).exists()
