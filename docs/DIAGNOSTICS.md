# Diagnostics: Logging & Warnings

Stellium is **silent by default** — importing it and calculating charts writes
nothing to your stdout. Diagnostics reach you through two standard Python
channels you fully control: `warnings` and `logging`.

## Warnings — "something about your input or result is off"

When Stellium can still proceed but something is degraded — a bad row in a CSV
import, a geocoding failure, an invalid orb configuration — it raises a typed
warning. These show once by default (to stderr) and are easy to filter.

All Stellium warnings derive from `StelliumWarning`, so one filter silences them
all:

```python
import warnings
from stellium import StelliumWarning

warnings.filterwarnings("ignore", category=StelliumWarning)
```

Or target a specific kind:

| Warning | Raised when |
|---|---|
| `DataQualityWarning` | An import row / registry entry / requested part was malformed or skipped |
| `GeocodingWarning` | A location couldn't be geocoded, or the geocoder was unavailable |
| `ConfigurationWarning` | A config value was invalid and ignored (e.g. a bad orb key, a missing house system) |
| `MissingEphemerisWarning` | A body was skipped because its ephemeris file isn't installed |

```python
from stellium import DataQualityWarning
warnings.filterwarnings("ignore", category=DataQualityWarning)
```

To **capture** warnings instead of printing them (e.g. to report skipped rows):

```python
import warnings
from stellium import DataQualityWarning, ChartBuilder
from stellium.io import parse_csv

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    natives = parse_csv("births.csv")

skipped = [w for w in caught if issubclass(w.category, DataQualityWarning)]
```

## Logging — internal operational detail

Operational diagnostics (cache writes, ephemeris setup) go to the `stellium`
logger, which has a `NullHandler` and is **off by default**. Turn it on with one
call:

```python
import stellium
stellium.configure_logging("INFO")     # or "DEBUG", "WARNING", ...
```

`configure_logging` attaches a stream handler and sets the level. You can point
it anywhere and customize the format:

```python
import sys
stellium.configure_logging("DEBUG", stream=sys.stdout, fmt="%(levelname)s: %(message)s")
```

Prefer to wire it into your own logging setup? Just configure the `stellium`
logger directly — Stellium never adds handlers of its own beyond the
`NullHandler`:

```python
import logging
logging.getLogger("stellium").setLevel(logging.DEBUG)
logging.basicConfig()  # your application's handlers
```

## Which is which?

- **Warning** = "you (the caller) should know — act on it or suppress it." On by
  default.
- **Log** = "what Stellium did internally, for when you're debugging." Off by
  default; opt in with `configure_logging`.

Contributors: the rule that keeps this consistent (and the ban on bare `print`)
is in [`CONTRIBUTING.md`](../CONTRIBUTING.md#diagnostics-no-bare-print); the full
design is in
[`docs/development/specs/STRUCTURED_LOGGING_SPEC.md`](development/specs/STRUCTURED_LOGGING_SPEC.md).
