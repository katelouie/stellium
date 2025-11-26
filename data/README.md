# Swiss Ephemeris Data

This directory contains astronomical calculation data from the Swiss Ephemeris, the most accurate ephemeris available for astrological calculations.

## 📁 What's Included

### Essential Files (Included in Repository)
Stellium includes **essential ephemeris files** covering **1800-2400 CE** (~7.8MB total):

```
data/swisseph/ephe/
├── sepl_18.se1    # Planets 1800-2399 CE (~473KB)
├── sepl_24.se1    # Planets 2400-2999 CE (~473KB)
├── semo_18.se1    # Moon 1800-2399 CE (~1.2MB)
├── semo_24.se1    # Moon 2400-2999 CE (~1.2MB)
└── seas_18.se1    # Asteroids 1800-2399 CE (~220KB)
```

**Coverage:** This provides accurate calculations for **99% of common use cases** including:
- All modern natal charts (1800-present)
- Future transits and progressions through 2400 CE
- Historical charts back to 1800 CE

### Full Dataset (Optional Download)
The complete Swiss Ephemeris dataset covers **13201 BCE to 17191 CE** (~334MB total):
- **50 planetary files** (sepl*.se1)
- **50 lunar files** (semo*.se1)
- **50 asteroid files** (seas*.se1)
- Additional fixed star and theoretical object data

## 🚀 Quick Start

### Using Essential Files Only
The included files work immediately:

```python
from stellium.chart import Chart
from datetime import datetime
import pytz

# Works out of the box for dates 1800-2400 CE
chart = Chart(
    datetime_utc=datetime(1994, 1, 6, 19, 47, tzinfo=pytz.UTC),
    loc_name="San Francisco, CA"
)
```

### Download Full Dataset

For **extended date ranges** or **ancient astrology**, download the full dataset:

```bash
# Download all files (~334MB)
python scripts/download_ephemeris.py

# Download specific year range
python scripts/download_ephemeris.py --years 1000-3000

# List available files without downloading
python scripts/download_ephemeris.py --list --years 0-1000
```

## 📅 File Coverage by Year Range

Each ephemeris file covers **600 years**:

| File Pattern | Years Covered | Description |
|--------------|---------------|-------------|
| `sepl_00.se1` | 0-599 CE | Planets: Ancient era |
| `sepl_06.se1` | 600-1199 CE | Planets: Medieval era |
| `sepl_12.se1` | 1200-1799 CE | Planets: Renaissance era |
| **`sepl_18.se1`** | **1800-2399 CE** | **✅ Planets: Modern era (INCLUDED)** |
| **`sepl_24.se1`** | **2400-2999 CE** | **✅ Planets: Future era (INCLUDED)** |

*Moon (semo) and asteroid (seas) files follow the same pattern*

### BCE Files
Files with 'm' prefix cover BCE years:
- `seplm06.se1`: 600-1 BCE
- `seplm12.se1`: 1200-601 BCE
- `seplm18.se1`: 1800-1201 BCE
- etc.

## 🔍 File Types Explained

### Planetary Files (sepl*.se1)
- **Size:** ~473KB each
- **Content:** Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- **Precision:** Positions accurate to 0.001 arcseconds

### Lunar Files (semo*.se1)
- **Size:** ~1.2MB each
- **Content:** Detailed lunar calculations including:
  - Precise lunar positions
  - Moon phases and libration
  - Lunar nodes and apogee/perigee
  - Tidal acceleration

### Asteroid Files (seas*.se1)
- **Size:** ~220KB each
- **Content:** Main asteroids including:
  - Ceres, Pallas, Juno, Vesta
  - Chiron and other centaurs
  - Major numbered asteroids

## 📖 Usage Examples

### Check Available Date Range
```python
# Test if a date is covered by current data
def is_date_covered(year):
    return 1800 <= year <= 2400

print(is_date_covered(1994))  # True
print(is_date_covered(500))   # False - need sepl_00.se1
```

### Download for Specific Use Cases
```bash
# Ancient astrology (need BCE files)
python scripts/download_ephemeris.py --years -500-500

# Medieval astrology
python scripts/download_ephemeris.py --years 1000-1500

# Far future projections
python scripts/download_ephemeris.py --years 3000-4000
```

## ⚖️ Licensing

The Swiss Ephemeris is available under **dual licensing**:

### AGPL License (Free)
- ✅ **Stellium uses this license**
- ✅ Free for open-source projects
- ⚠️ Requires AGPL compliance for derivative works

### Professional License (Commercial)
- For commercial/proprietary software
- Contact: https://www.astro.com/swisseph/
- License fee: CHF 750 (first license)

### Copyright Notice
**Required by license:**
```
Swiss Ephemeris. Copyright 1997-2023 Astrodienst AG, Switzerland.
All rights reserved.
```

## 🔗 Official Resources

- **Main Website:** https://www.astro.com/swisseph/
- **Documentation:** https://www.astro.com/swisseph/swisseph.htm
- **Downloads:** https://github.com/aloistr/swisseph
- **Support:** https://groups.io/g/swisseph

## 🛠️ Technical Notes

### Performance Tips
- Keep only files you need to reduce disk usage
- Essential files provide 99% coverage at 2% of size
- Full dataset recommended for research or historical work

### File Organization
Files must be in the exact directory structure:
```
data/swisseph/ephe/ephe/
├── sepl*.se1    # Planetary files
├── semo*.se1    # Lunar files
└── seas*.se1    # Asteroid files
```

### Troubleshooting
**Common Issues:**
- `SwissEph file not found`: Download required year range
- `Invalid date range`: Check file coverage table above
- `Permission denied`: Run download script with proper permissions

---

*The Swiss Ephemeris provides the astronomical foundation for accurate astrological calculations. Thank you to Astrodienst AG for maintaining this invaluable resource.* ✨