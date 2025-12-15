"""
Download full Swiss Ephemeris dataset for extended date ranges.

This script downloads the complete Swiss Ephemeris dataset (~334MB) which covers
the period from 13201 BCE to 17191 CE. The basic Stellium installation includes
only essential files covering 1800-2400 CE (~7.8MB).

Asteroid files are stored separately in ast0/, ast1/, etc. folders, where:
- ast0/ contains asteroids 0-999
- ast1/ contains asteroids 1000-1999
- etc.

Common asteroid numbers:
- Eris: 136199 (ast136/)
- Sedna: 90377 (ast90/)
- Makemake: 136472 (ast136/)
- Haumea: 136108 (ast136/)
- Orcus: 90482 (ast90/)
- Quaoar: 50000 (ast50/)
"""

import urllib.error
import urllib.request
from pathlib import Path

# Swiss Ephemeris official download URLs
EPHEMERIS_BASE_URL = "https://www.astro.com/ftp/swisseph/ephe/"
DROPBOX_BASE_URL = "https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/ephe/"

# Asteroid ephemeris download server (thanks to scryr.io for hosting!)
# Contains long-range asteroid files (6000 year coverage)
ASTEROID_BASE_URL = "https://ephe.scryr.io/ephe2/"

# Common TNO and dwarf planet asteroid numbers for easy reference
COMMON_ASTEROIDS = {
    "Eris": 136199,
    "Sedna": 90377,
    "Makemake": 136472,
    "Haumea": 136108,
    "Orcus": 90482,
    "Quaoar": 50000,
}

# File patterns and their descriptions
FILE_PATTERNS = {
    "planets": {
        "prefix": "sepl",
        "description": "Planetary ephemeris files (~473KB each)",
        "size_kb": 473,
    },
    "moon": {
        "prefix": "semo",
        "description": "Lunar ephemeris files (~1.2MB each)",
        "size_kb": 1200,
    },
    "asteroids": {
        "prefix": "seas",
        "description": "Asteroid ephemeris files (~220KB each)",
        "size_kb": 220,
    },
}

# Year ranges for ephemeris files (each file covers 600 years)
YEAR_RANGES = [
    # BCE files (negative years, 'm' prefix)
    ("seplm54.se1", -5400, -4801),
    ("seplm48.se1", -4800, -4201),
    ("seplm42.se1", -4200, -3601),
    ("seplm36.se1", -3600, -3001),
    ("seplm30.se1", -3000, -2401),
    ("seplm24.se1", -2400, -1801),
    ("seplm18.se1", -1800, -1201),
    ("seplm12.se1", -1200, -601),
    ("seplm06.se1", -600, -1),
    # CE files (positive years, '_' prefix)
    ("sepl_00.se1", 0, 599),
    ("sepl_06.se1", 600, 1199),
    ("sepl_12.se1", 1200, 1799),
    ("sepl_18.se1", 1800, 2399),  # ✅ Essential (included)
    ("sepl_24.se1", 2400, 2999),
    ("sepl_30.se1", 3000, 3599),
    ("sepl_36.se1", 3600, 4199),
    ("sepl_42.se1", 4200, 4799),
    ("sepl_48.se1", 4800, 5399),
    ("sepl_54.se1", 5400, 5999),
    ("sepl_60.se1", 6000, 6599),
    ("sepl_66.se1", 6600, 7199),
    ("sepl_72.se1", 7200, 7799),
    ("sepl_78.se1", 7800, 8399),
    ("sepl_84.se1", 8400, 8999),
    ("sepl_90.se1", 9000, 9599),
    ("sepl_96.se1", 9600, 10199),
    ("sepl_102.se1", 10200, 10799),
    ("sepl_108.se1", 10800, 11399),
    ("sepl_114.se1", 11400, 11999),
    ("sepl_120.se1", 12000, 12599),
    ("sepl_126.se1", 12600, 13199),
    ("sepl_132.se1", 13200, 13799),
    ("sepl_138.se1", 13800, 14399),
    ("sepl_144.se1", 14400, 14999),
    ("sepl_150.se1", 15000, 15599),
    ("sepl_156.se1", 15600, 16199),
    ("sepl_162.se1", 16200, 16799),
]


def get_data_directory() -> Path:
    """Get the user ephemeris data directory.

    Ephemeris files are stored in the user's home directory:
    ~/.stellium/ephe/

    This allows users to add their own asteroid files and persists
    across package upgrades.
    """
    from stellium.data.paths import get_user_ephe_dir

    return get_user_ephe_dir()


def get_required_files(
    start_year: int | None = None, end_year: int | None = None
) -> list[str]:
    """Get list of required ephemeris files for given year range."""
    if start_year is None:
        start_year = -5400
    if end_year is None:
        end_year = 16799

    required_files = []

    for _file_type, config in FILE_PATTERNS.items():
        prefix = config["prefix"]

        # Generate file names for the year range
        for filename, file_start, file_end in YEAR_RANGES:
            # Replace 'sepl' with current prefix
            filename = filename.replace("sepl", prefix)

            # Check if this file overlaps with requested range
            if file_end >= start_year and file_start <= end_year:
                required_files.append(filename)

    return sorted(set(required_files))


def download_file(
    url: str, filepath: Path, force: bool = False, quiet: bool = False
) -> bool:
    """Download a single ephemeris file."""
    if filepath.exists() and not force:
        if not quiet:
            print(f"⏭️  Skipping {filepath.name} (already exists)")
        return True

    if not quiet:
        print(f"📥 Downloading {filepath.name}...")

    try:
        # Try primary URL first
        try:
            urllib.request.urlretrieve(url, filepath)
            if not quiet:
                print(f"✅ Downloaded {filepath.name}")
            return True
        except urllib.error.URLError:
            # Try dropbox URL as fallback
            dropbox_url = url.replace(EPHEMERIS_BASE_URL, DROPBOX_BASE_URL) + "?dl=1"
            urllib.request.urlretrieve(dropbox_url, filepath)
            if not quiet:
                print(f"✅ Downloaded {filepath.name} (via dropbox)")
            return True

    except Exception as e:
        print(f"❌ Failed to download {filepath.name}: {e}")
        return False


def calculate_download_size(files: list[str]) -> float:
    """Calculate total download size in MB."""
    total_kb = 0
    for filename in files:
        for _file_type, config in FILE_PATTERNS.items():
            if filename.startswith(config["prefix"]):
                total_kb += config["size_kb"]
                break
    return total_kb / 1024  # Convert to MB


# =============================================================================
# ASTEROID FILE FUNCTIONS
# =============================================================================


def get_asteroid_filename(asteroid_number: int) -> str:
    """
    Get the Swiss Ephemeris filename for an asteroid number.

    Long-range asteroid files (6000 year coverage) follow the pattern:
    - For numbers < 100000: se{number}.se1 (5-digit zero-padded)
    - For numbers >= 100000: s{number}.se1 (no zero-padding)

    Note: Short-range files have an 's' suffix (e.g., s136199s.se1) but
    we download long-range files for better coverage.

    Args:
        asteroid_number: The MPC (Minor Planet Center) number

    Returns:
        Filename like "se00005.se1" or "s136199.se1"
    """
    # Long-range files (no 's' suffix)
    if asteroid_number < 100000:
        return f"se{asteroid_number:05d}.se1"
    else:
        return f"s{asteroid_number}.se1"


def get_asteroid_folder(asteroid_number: int) -> str:
    """
    Get the folder name for an asteroid number.

    Asteroids are grouped in folders: ast0 (0-999), ast1 (1000-1999), etc.

    Args:
        asteroid_number: The MPC number

    Returns:
        Folder name like "ast0", "ast136", etc.
    """
    return f"ast{asteroid_number // 1000}"


def download_asteroid_file(
    asteroid_number: int, force: bool = False, quiet: bool = False
) -> bool:
    """
    Download an asteroid ephemeris file.

    Downloads long-range ephemeris files (6000 year coverage) from
    ephe.scryr.io.

    Args:
        asteroid_number: The MPC (Minor Planet Center) number
        force: Overwrite existing file
        quiet: Suppress output

    Returns:
        True if download succeeded, False otherwise
    """
    data_dir = get_data_directory()
    filename = get_asteroid_filename(asteroid_number)
    folder = get_asteroid_folder(asteroid_number)
    filepath = data_dir / filename

    if filepath.exists() and not force:
        if not quiet:
            print(f"⏭️  Skipping {filename} (already exists)")
        return True

    if not quiet:
        print(f"📥 Downloading {filename} from {folder}/...")

    # Download from ephe.scryr.io (primary source for asteroid files)
    url = f"{ASTEROID_BASE_URL}{folder}/{filename}"

    try:
        urllib.request.urlretrieve(url, filepath)
        # Verify we got actual data, not an error page
        if filepath.stat().st_size < 1000:
            with open(filepath, "rb") as f:
                header = f.read(50)
                if b"<!DOCTYPE" in header or b"<html" in header:
                    filepath.unlink()
                    raise ValueError("Downloaded HTML instead of ephemeris data")
        if not quiet:
            print(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        if filepath.exists():
            filepath.unlink()  # Remove partial/invalid file
        print(f"❌ Failed to download {filename}: {e}")
        return False


def download_common_asteroids(force: bool = False, quiet: bool = False) -> int:
    """
    Download ephemeris files for common TNOs and dwarf planets.

    Downloads: Eris, Sedna, Makemake, Haumea, Orcus, Quaoar

    Args:
        force: Overwrite existing files
        quiet: Suppress output

    Returns:
        Number of successfully downloaded files
    """
    success_count = 0
    if not quiet:
        print("🌟 Downloading common TNO/dwarf planet ephemeris files...")
        print("-" * 50)

    for name, number in COMMON_ASTEROIDS.items():
        if not quiet:
            print(f"   {name} (#{number})...")
        if download_asteroid_file(number, force=force, quiet=True):
            success_count += 1
            if not quiet:
                print(f"   ✅ {name}")
        else:
            if not quiet:
                print(f"   ❌ {name} (failed)")

    if not quiet:
        print("-" * 50)
        print(f"✅ Downloaded {success_count}/{len(COMMON_ASTEROIDS)} files")

    return success_count


def resolve_asteroid_input(input_str: str) -> list[int]:
    """
    Resolve asteroid input to a list of asteroid numbers.

    Accepts:
    - Single number: "136199"
    - Comma-separated: "136199,90377,50000"
    - Named asteroids: "eris", "sedna", "makemake"
    - Special keywords: "tnos", "all-common"

    Args:
        input_str: User input string

    Returns:
        List of asteroid numbers
    """
    input_str = input_str.strip().lower()

    # Special keywords
    if input_str in ("tnos", "all-common", "common"):
        return list(COMMON_ASTEROIDS.values())

    # Check if it's a named asteroid
    for name, number in COMMON_ASTEROIDS.items():
        if input_str == name.lower():
            return [number]

    # Parse as numbers (comma-separated)
    numbers = []
    for part in input_str.split(","):
        part = part.strip()
        try:
            numbers.append(int(part))
        except ValueError:
            # Try as a name again
            for name, number in COMMON_ASTEROIDS.items():
                if part == name.lower():
                    numbers.append(number)
                    break

    return numbers
