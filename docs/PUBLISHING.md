# Publishing to PyPI

This guide covers how to publish Stellium to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/account/register/) and [TestPyPI](https://test.pypi.org/account/register/)

2. **Build Tools**: Install required tools (already in dev dependencies):
   ```bash
   pip install build twine
   ```

3. **GitHub Repository Secrets**: Configure trusted publishing (recommended) or API tokens:

### Option A: Trusted Publishing (Recommended)

Trusted publishing eliminates the need for API tokens by using GitHub's OIDC identity.

1. Go to your PyPI account settings
2. Navigate to "Publishing" → "Add a new pending publisher"
3. Fill in:
   - PyPI Project Name: `stellium`
   - Owner: `katelouie`
   - Repository name: `stellium`
   - Workflow name: `publish-to-pypi.yml`
   - Environment name: `pypi`

Do the same for TestPyPI if you want to test first.

### Option B: API Tokens (Alternative)

If not using trusted publishing:

1. Generate API tokens:
   - PyPI: Account Settings → API tokens → "Add API token"
   - TestPyPI: Same process on test.pypi.org

2. Add tokens to GitHub repository secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Add `PYPI_API_TOKEN` with your PyPI token
   - Add `TEST_PYPI_API_TOKEN` with your TestPyPI token

3. Update `.github/workflows/publish-to-pypi.yml` to use tokens instead of trusted publishing

## Publishing Process

### 1. Prepare for Release

Before publishing, ensure:

1. **All tests pass**:
   ```bash
   pytest
   ```

2. **Version is bumped** in `src/stellium/__init__.py`:
   ```python
   __version__ = "0.3.0"  # Update this
   ```

3. **CHANGELOG.md is updated** with release notes

4. **Build locally to test**:
   ```bash
   # Clean old builds
   rm -rf dist/ build/ *.egg-info src/*.egg-info

   # Build
   python -m build

   # Verify Swiss Ephemeris data is included
   tar -tzf dist/stellium-*.tar.gz | grep -E "\.se1"
   ```

### 2. Test on TestPyPI (Recommended First Time)

Test your package on TestPyPI before publishing to the real PyPI:

**Via GitHub Actions (Automatic)**:
1. Go to Actions → "Publish to PyPI" → "Run workflow"
2. Check "Publish to TestPyPI instead of PyPI"
3. Click "Run workflow"

**Manually**:
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation (in a clean virtual environment)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ stellium
```

Note: The `--extra-index-url` is needed because dependencies (like `pyswisseph`) are not on TestPyPI.

**Verify the test installation**:
```python
from stellium import ChartBuilder
from datetime import datetime

# Should work!
chart = ChartBuilder.from_native(
    datetime(2000, 1, 1, 12, 0),
    "New York, NY"
).build()
print(f"Sun: {chart.get_object('Sun').longitude:.2f}°")
```

### 3. Publish to PyPI

Once verified on TestPyPI, publish to the real PyPI:

**Via GitHub Release (Automatic - Recommended)**:
1. Create a new release on GitHub
2. Tag version: `v0.3.0` (must match `__version__`)
3. Release title: `v0.3.0` or "Stellium v0.3.0"
4. Description: Copy relevant section from CHANGELOG.md
5. Click "Publish release"

The GitHub Action will automatically:
- Build the package
- Verify Swiss Ephemeris data is included
- Publish to PyPI using trusted publishing

**Manually**:
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### 4. Verify Publication

1. Check PyPI page: https://pypi.org/project/stellium/

2. Test installation in a fresh virtual environment:
   ```bash
   python -m venv test_env
   source test_env/bin/activate
   pip install stellium
   python -c "from stellium import ChartBuilder; print('Success!')"
   ```

3. Verify Swiss Ephemeris data works:
   ```python
   from stellium import ChartBuilder
   from datetime import datetime

   chart = ChartBuilder.from_native(
       datetime(1994, 1, 6, 11, 47),
       "Palo Alto, CA"
   ).build()

   sun = chart.get_object("Sun")
   print(f"Sun at {sun.longitude:.2f}° in {sun.sign}")
   # Should output real astronomical data, not error!
   ```

## Package Structure

The package includes:

- **Python source code**: All modules in `src/stellium/`
- **Swiss Ephemeris data**: Essential data files (~3.7MB) for 1800-2400 CE
  - `data/swisseph/ephe/sepl_18.se1` (planets 1800-1999)
  - `data/swisseph/ephe/sepl_24.se1` (planets 2000-2399)
  - `data/swisseph/ephe/semo_18.se1` (moon 1800-1999)
  - `data/swisseph/ephe/semo_24.se1` (moon 2000-2399)
  - `data/swisseph/ephe/seas_18.se1` (asteroids 1800-1999)
  - `data/swisseph/ephe/seas_24.se1` (asteroids 2000-2399)
  - Additional ephemeris files can be downloaded via CLI: `stellium ephemeris download`
- **Notable births data**: Curated database of famous births with verified birth data
- **Metadata**: README.md, LICENSE, CHANGELOG.md
- **Tests**: All test files (users can run tests if desired)

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

Examples:
- `0.2.0` → `0.2.1`: Bug fix
- `0.2.1` → `0.3.0`: New house system added
- `0.3.0` → `1.0.0`: Stable API, ready for production

## Troubleshooting

### Swiss Ephemeris Data Not Included

Check MANIFEST.in:
```
recursive-include data/swisseph/ephe *.se1
```

Verify files are in distribution:
```bash
tar -tzf dist/stellium-*.tar.gz | grep -E "\.se1"
```

### Import Errors After Installation

If users report:
```
ModuleNotFoundError: No module named 'stellium.engines'
```

Ensure `pyproject.toml` has:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### License Warnings

Modern setuptools prefers SPDX license expressions:
```toml
license = "MIT"  # Not license = { text = "MIT" }
```

## Release Checklist

Before each release:

- [ ] All tests pass (`pytest`)
- [ ] Version bumped in `src/stellium/__init__.py`
- [ ] CHANGELOG.md updated with release notes
- [ ] Build locally and verify (`python -m build`)
- [ ] Check Swiss Ephemeris data included in tarball
- [ ] Test on TestPyPI first (optional but recommended)
- [ ] Create GitHub release with tag `vX.Y.Z`
- [ ] Verify publication on PyPI
- [ ] Test installation in clean environment

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions for PyPI](https://github.com/marketplace/actions/pypi-publish)
