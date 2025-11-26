# 🌟 Stellium Refactor Checklist

Track your progress through the architectural overhaul.

---

## Week 1: Core Architecture

### Day 1: Project Structure & Data Model

- [ ] Create new directory structure (`core/`, `engines/`, `components/`)
- [ ] Write `src/stellium/core/models.py`
  - [ ] ChartLocation
  - [ ] ChartDateTime
  - [ ] CelestialPosition
  - [ ] HouseCusps
  - [ ] Aspect
  - [ ] CalculatedChart
- [ ] Write `tests/test_core_models.py`
- [ ] Run tests - all passing? ✓

**Time estimate: 4-6 hours**

---

### Day 2: Core Protocols

- [ ] Write `src/stellium/core/protocols.py`
  - [ ] EphemerisEngine protocol
  - [ ] HouseSystemEngine protocol
  - [ ] AspectEngine protocol
  - [ ] DignityCalculator protocol
  - [ ] ChartComponent protocol
- [ ] Write `src/stellium/core/config.py`
  - [ ] AspectConfig
  - [ ] CalculationConfig
  - [ ] Configuration presets

**Time estimate: 3-4 hours**

---

### Day 3: Ephemeris Engine

- [ ] Write `src/stellium/engines/ephemeris.py`
  - [ ] SwissEphemerisEngine
  - [ ] MockEphemerisEngine (for testing)
  - [ ] Swiss Ephemeris path setup
- [ ] Write `tests/test_ephemeris_engine.py`
- [ ] Test with real data (Einstein's chart)
- [ ] Verify caching is working ✓

**Time estimate: 4-5 hours**

---

### Day 4: House Systems

- [ ] Write `src/stellium/engines/houses.py`
  - [ ] PlacidusHouses
  - [ ] WholeSignHouses
  - [ ] EqualHouses
  - [ ] House assignment logic
- [ ] Write `tests/test_houses.py`
- [ ] Compare outputs with old implementation
- [ ] All tests passing? ✓

**Time estimate: 4-6 hours**

---

### Day 5: Chart Builder

- [ ] Write `src/stellium/core/builder.py`
  - [ ] ChartBuilder class
  - [ ] Fluent API methods (`.with_*()`)
  - [ ] `from_datetime()` constructor
  - [ ] `from_location_name()` with geocoding
  - [ ] `calculate()` orchestration
- [ ] Write `tests/test_chart_builder.py`
- [ ] Create end-to-end test script
- [ ] Verify complete workflow works ✓

**Time estimate: 5-7 hours**

---

### Week 1 Checkpoint

**Before moving to Week 2:**

- [ ] All Week 1 tests passing
- [ ] Can calculate a complete natal chart
- [ ] Can swap house systems easily
- [ ] Geocoding works
- [ ] Create `test_week1.py` and verify output
- [ ] Architecture feels solid ✓

**Take a break! Celebrate progress!** 🎉

---

## Week 2: Components & Validation

### Day 6: Aspect Engine

- [ ] Write `src/stellium/engines/aspects.py`
  - [ ] ModernAspectEngine
  - [ ] HarmonicAspectEngine
  - [ ] Applying/separating calculation
  - [ ] Angular distance utilities
- [ ] Write `tests/test_aspect_engine.py`
  - [ ] Test conjunctions
  - [ ] Test trines, squares, etc.
  - [ ] Test harmonic aspects
- [ ] Integrate with ChartBuilder
- [ ] Verify aspect calculations match old system ✓

**Time estimate: 5-6 hours**

---

### Day 7: Dignity Calculator

- [ ] Write `src/stellium/engines/dignities.py`
  - [ ] TraditionalDignityCalculator
  - [ ] Dignity data (ruler, exaltation, etc.)
  - [ ] Scoring system
- [ ] Write `tests/test_dignities.py`
- [ ] Compare with old dignity system
- [ ] All tests passing? ✓

**Time estimate: 3-4 hours**

---

### Day 8: Test & Validate

- [ ] Write `tests/test_integration.py`
  - [ ] Einstein's chart end-to-end
  - [ ] JSON export test
  - [ ] Multiple house systems test
  - [ ] Immutability test
- [ ] Write `tests/benchmark_performance.py`
- [ ] Run benchmarks - under 500ms per chart? ✓
- [ ] Calculate 10 famous people's charts
- [ ] Compare all results with old system
- [ ] Fix any discrepancies ✓

**Time estimate: 4-6 hours**

---

### Day 9: Migration Tools

- [ ] Write `docs/development/MIGRATION.md`
  - [ ] Side-by-side API comparison
  - [ ] Migration examples
  - [ ] Common patterns
- [ ] Write `src/stellium/legacy.py` (optional wrapper)
- [ ] Create migration script for existing code
- [ ] Test legacy compatibility ✓

**Time estimate: 3-4 hours**

---

### Day 10: Documentation

- [ ] Write `docs/USER_GUIDE.md`
  - [ ] Quick start guide
  - [ ] Common use cases
  - [ ] Advanced features
  - [ ] Code examples
- [ ] Write `docs/API_REFERENCE.md` (or use docstrings)
- [ ] Update main `README.md`
- [ ] Create example scripts in `examples/new_api/`
- [ ] Documentation is clear and complete ✓

**Time estimate: 4-5 hours**

---

### Week 2 Checkpoint

**Before declaring victory:**

- [ ] All tests passing (Weeks 1 & 2)
- [ ] Can calculate natal charts with new API
- [ ] Can swap house systems
- [ ] Can calculate aspects
- [ ] JSON export works
- [ ] Performance is acceptable (<500ms/chart)
- [ ] Migration guide is clear
- [ ] User guide exists
- [ ] Run `test_week2_complete.py` successfully ✓

**Refactor complete!** 🎉✨

---

## Post-Refactor Tasks (Week 3+)

### Update Existing Components

- [ ] Update `drawing.py` to use new data models
- [ ] Update chart visualization
- [ ] Test SVG generation with new API

### Add Missing Features

- [ ] Arabic Parts component
- [ ] Midpoints component
- [ ] Fixed stars (if desired)

### Polish

- [ ] Update all examples to use new API
- [ ] Archive old code in `legacy/` folder
- [ ] Clean up imports in `__init__.py`
- [ ] Update pyproject.toml/setup.py

### Release Prep

- [ ] Bump version to 2.0.0
- [ ] Write CHANGELOG.md
- [ ] Update documentation
- [ ] Create migration guide for users
- [ ] Prepare release notes

---

## Daily Workflow

### Start of day:
```bash
# Activate environment
source ~/.zshrc && pyenv activate stellium

# Pull latest changes (if working across machines)
git pull origin claude/architecture-overhaul-planning-*

# Review checklist for today
```

### During work:
```bash
# Run tests frequently
python -m pytest tests/ -v

# Run specific test file
python tests/test_core_models.py

# Check progress
git status
```

### End of day:
```bash
# Run all tests
python -m pytest tests/ -v

# Commit progress
git add .
git commit -m "Day X: [what you accomplished]"
git push -u origin claude/architecture-overhaul-planning-*

# Update this checklist
```

---

## Troubleshooting

### Tests failing?
1. Check that pyenv environment is activated
2. Verify Swiss Ephemeris path is correct
3. Check for import errors
4. Read error messages carefully

### Imports not working?
```bash
# Reinstall in development mode
pip install -e .
```

### Performance issues?
- Check if caching is working
- Use MockEphemerisEngine for non-calculation tests
- Profile with `python -m cProfile`

---

## Resources

- Main guide: `docs/development/REFACTORING_GUIDE.md`
- Old codebase: `src/stellium/chart.py` (reference)
- Vision doc: `docs/planning/VISION_ARCHITECTURE.md`

---

## Notes & Reflections

Use this space to track insights, challenges, or ideas:

```
Day 1:
-

Day 2:
-

Day 3:
-

...
```

---

**Remember: This is a ground-up rebuild. Take your time, test thoroughly, and build it right!** 🌟
