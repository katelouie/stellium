# Where Stellium Reads and Writes

Stellium touches exactly two directories, and they are kept apart on purpose.

| | Default (macOS / Linux) | Default (Windows) | Override with |
|---|---|---|---|
| **Ephemeris** — *data; keep it* | `~/.stellium/ephe/` | `C:\Users\<you>\.stellium\ephe\` | `STELLIUM_EPHE_PATH` |
| **Cache** — *disposable* | `~/.cache/stellium/` | `%LOCALAPPDATA%\stellium\cache\` | `STELLIUM_CACHE_DIR` |

**Nothing else is written anywhere.** In particular Stellium does not create a
`.cache/` in your working directory, and importing it does not touch the disk at
all.

To see where those two actually resolved on *your* machine — and whether an
environment variable or the default put them there:

```bash
stellium cache info
```

```
🗂️  Stellium paths
============================================================
Cache (disposable):  /home/you/.cache/stellium
                     default — override with STELLIUM_CACHE_DIR
Ephemeris (data):    /home/you/.stellium/ephe
                     default — override with STELLIUM_EPHE_PATH
```

---

## The ephemeris directory — *data*

Stellium bundles enough Swiss Ephemeris data to cover **1800–2999 CE** and copies
it to `~/.stellium/ephe/` on first use, so most users never need to download
anything. Reach for `stellium ephemeris download` only if you need coverage
outside that range, and `stellium ephemeris download-asteroid` for extra asteroid
or TNO files.

Keep this directory. Anything **you** downloaded into it — asteroids, TNOs, a
wider date range — is slow to fetch again and is not re-created for you.

### Pointing at an existing ephemeris folder

Useful for portable installs, read-only home directories (Docker, Lambda, shared
hosts), or reusing a folder you already maintain for another astrology tool.
In order of precedence:

```python
# 1. Explicit argument — wins over everything else
from stellium import ChartBuilder
from stellium.engines.ephemeris import SwissEphemerisEngine

chart = (ChartBuilder.from_native(native)
    .with_ephemeris(SwissEphemerisEngine(ephe_path=r"D:\swisseph\ephe"))
    .calculate())
```

```bash
# 2. Environment variable — no code changes required
export STELLIUM_EPHE_PATH=/opt/swisseph/ephe       # macOS / Linux
set STELLIUM_EPHE_PATH=D:\swisseph\ephe            # Windows (cmd)
$env:STELLIUM_EPHE_PATH = "D:\swisseph\ephe"       # Windows (PowerShell)
```

> ⚠️ **A custom ephemeris folder is used _as-is_.** Stellium will not create it,
> and will **not** copy the bundled `.se1` files into it. Populate it first —
> either copy `~/.stellium/ephe/` across, or run `stellium ephemeris download`
> *after* setting the variable. Otherwise you will get
> `MissingEphemerisWarning` for objects whose files aren't there (a missing
> `se00015.se1` means no Chiron, for instance).

---

## The cache directory — *disposable*

Holds pickled **geocoding** lookups: the results of turning `"Palo Alto, CA"` into
coordinates, so the same place is not looked up over the network twice. That is
all that is cached.

**It is safe to delete at any time.** Nothing in it is precious, and everything in
it can be regenerated.

```bash
stellium cache clear
```

Chart calculation is **not** cached. Swiss Ephemeris positions are computed in
microseconds — faster than reading a cached copy back from disk — so caching them
would make Stellium *slower*.

### Why it does not live in `~/.stellium/`

Because a cache and your ephemeris deserve opposite treatment. `~/.cache` is the
directory the wider ecosystem already agrees is disposable: backup tools skip it,
cleaners empty it, CI images mount it. Keeping the two apart means "clear
Stellium's junk" can never point at asteroid files you spent time downloading.

`XDG_CACHE_HOME` is honoured if you set it. On macOS the default is `~/.cache`
rather than `~/Library/Caches`, because Stellium is a developer-facing library and
that is where its users look — set `XDG_CACHE_HOME` if you prefer otherwise.

---

## Portable installs, and read-only home directories

If you run a portable or embedded Python, or `$HOME` is read-only (Docker, Lambda,
shared hosts), set **both** variables and Stellium will never write to your home
drive.

### Windows — portable Python, project on `D:`

```powershell
# PowerShell — keep everything on D:, next to the project
$env:STELLIUM_EPHE_PATH = "D:\Astrology\Stellium\ephe"
$env:STELLIUM_CACHE_DIR = "D:\Astrology\Stellium\cache"

# Make it stick across sessions (current user; no admin needed):
[Environment]::SetEnvironmentVariable("STELLIUM_EPHE_PATH", "D:\Astrology\Stellium\ephe",  "User")
[Environment]::SetEnvironmentVariable("STELLIUM_CACHE_DIR", "D:\Astrology\Stellium\cache", "User")

# Verify — prints both paths and where each one came from:
stellium cache info
```

Then populate the ephemeris folder once (it is used as-is, remember):

```powershell
# Either copy what Stellium already unpacked...
Copy-Item "$env:USERPROFILE\.stellium\ephe\*" "D:\Astrology\Stellium\ephe\"

# ...or download fresh, now that the variable points where you want it:
stellium ephemeris download
```

### macOS / Linux

```bash
export STELLIUM_EPHE_PATH=/opt/stellium/ephe
export STELLIUM_CACHE_DIR=/opt/stellium/cache
```

The cache directory **is** created for you on first write. The ephemeris directory
is not — see the warning above.

---

## Troubleshooting

**"Stellium can't find my ephemeris file / I get a `MissingEphemerisWarning`."**
Run `stellium cache info` and check the ephemeris path is the folder you think it
is. If an environment variable is redirecting it, that folder is used *as-is* — the
file has to actually be in it. Then:

```python
from stellium.data.paths import get_ephe_dir, has_ephe_file
print(get_ephe_dir())
print(has_ephe_file("se00015.se1"))   # Chiron
```

**"A `.cache/` folder appeared in my project directory."**
That was a bug in Stellium ≤ 0.21.0: the cache defaulted to a *relative* path, so it
was created wherever you happened to launch Python — and it grew without bound. Fixed;
the directory is now absolute. Any stray `.cache/` folders left behind by an older
version are safe to delete.
