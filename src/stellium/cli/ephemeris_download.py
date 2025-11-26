"""
Download full Swiss Ephemeris dataset for extended date ranges.

This script downloads the complete Swiss Ephemeris dataset (~334MB) which covers
the period from 13201 BCE to 17191 CE. The basic Stellium installation includes
only essential files covering 1800-2400 CE (~7.8MB).
"""

import urllib.error
import urllib.request
from pathlib import Path

# Swiss Ephemeris official download URLs
EPHEMERIS_BASE_URL = "https://www.astro.com/ftp/swisseph/ephe/"
DROPBOX_BASE_URL = "https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/ephe/"

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
    """Get the ephemeris data directory."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data" / "swisseph" / "ephe"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


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


def download_file(url: str, filepath: Path, force: bool = False) -> bool:
    """Download a single ephemeris file."""
    if filepath.exists() and not force:
        print(f"⏭️  Skipping {filepath.name} (already exists)")
        return True

    print(f"📥 Downloading {filepath.name}...")

    try:
        # Try primary URL first
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"✅ Downloaded {filepath.name}")
            return True
        except urllib.error.URLError:
            # Try dropbox URL as fallback
            dropbox_url = url.replace(EPHEMERIS_BASE_URL, DROPBOX_BASE_URL) + "?dl=1"
            urllib.request.urlretrieve(dropbox_url, filepath)
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
