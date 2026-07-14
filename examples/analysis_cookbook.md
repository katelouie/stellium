---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  display_name: starlight
  language: python
  name: python3
---

# Statistical Analysis

Calculate hundreds of charts at once, convert them to pandas DataFrames, query them by
astrological criteria, and run statistics across the whole set.

The analysis module provides tools for:
- **Batch chart calculation** - Calculate 100s-1000s of charts efficiently
- **DataFrame conversion** - Export charts to pandas DataFrames
- **Research queries** - Filter charts by astrological criteria
- **Statistical analysis** - Aggregate statistics across chart collections
- **Export utilities** - Save to CSV, JSON, Parquet

## Installation

The analysis module requires pandas (optional dependency):

```bash
pip install stellium[analysis]
```

```{code-cell} ipython3
# Imports
import pandas as pd

from stellium.analysis import (
    BatchCalculator,
    ChartQuery,
    ChartStats,
    aspects_to_dataframe,
    charts_to_dataframe,
    export_csv,
    export_json,
    positions_to_dataframe,
)
from stellium.core.native import Native
from stellium.engines.patterns import AspectPatternAnalyzer
```

---

## 1. BatchCalculator

Efficiently calculate many charts at once. `BatchCalculator` supports:
- Loading from the NotableRegistry (with filters)
- Loading from a list of Native objects
- Generator-based calculation (memory efficient)
- Progress callbacks

+++

### 1.1 From NotableRegistry

Load charts from the built-in database of notable births and events.

```{code-cell} ipython3
# Calculate charts for all notables in the registry
all_charts = BatchCalculator.from_registry().calculate_all()
print(f"Calculated {len(all_charts)} charts")
```

```{code-cell} ipython3
# Filter by category
scientist_charts = BatchCalculator.from_registry(category="scientist").calculate_all()
print(f"Calculated {len(scientist_charts)} scientist charts")
```

```{code-cell} ipython3
# Multiple filters: verified high-quality data only
verified_charts = BatchCalculator.from_registry(
    verified=True, data_quality="AA"
).calculate_all()
print(f"Calculated {len(verified_charts)} verified AA-quality charts")
```

### 1.2 From Native Objects

Calculate charts from your own data.

```{code-cell} ipython3
# Create sample Native objects
sample_natives = [
    Native("2000-01-01 12:00", "New York, NY", name="Person A"),
    Native("1995-06-21 08:30", "Los Angeles, CA", name="Person B"),
    Native("1988-12-15 22:00", "Chicago, IL", name="Person C"),
    Native("1975-03-20 06:00", "Seattle, WA", name="Person D"),
    Native("1960-09-10 14:30", "Miami, FL", name="Person E"),
]

# Calculate charts
custom_charts = BatchCalculator.from_natives(sample_natives).calculate_all()
print(f"Calculated {len(custom_charts)} custom charts")
```

### 1.3 With Aspects and Analyzers

Configure the calculation with aspect detection and pattern analysis.

```{code-cell} ipython3
# Calculate with aspects and pattern detection
charts_with_aspects = (
    BatchCalculator.from_natives(sample_natives)
    .with_aspects()  # Enable aspect calculation
    .add_analyzer(AspectPatternAnalyzer())  # Detect Grand Trines, T-Squares, etc.
    .calculate_all()
)

# Check aspects for first chart
print(f"First chart has {len(charts_with_aspects[0].aspects)} aspects")
```

### 1.4 Progress Tracking

Track progress for long-running batch calculations.

```{code-cell} ipython3
# Define a progress callback
def show_progress(current, total, name):
    print(f"  [{current}/{total}] Calculating: {name}")


# Calculate with progress tracking
print("Calculating charts with progress:")
charts = (
    BatchCalculator.from_natives(sample_natives[:3])  # Just first 3 for demo
    .with_progress(show_progress)
    .calculate_all()
)
```

### 1.5 Generator Mode (Memory Efficient)

For very large datasets, use the generator to process one chart at a time.

```{code-cell} ipython3
# Process charts one at a time (memory efficient)
batch = BatchCalculator.from_natives(sample_natives)

sun_signs = []
for chart in batch.calculate():
    sun = chart.get_object("Sun")
    sun_signs.append(sun.sign)

print(f"Sun signs: {sun_signs}")
```

---

## 2. DataFrame Conversion

Convert charts to pandas DataFrames for analysis. Three schemas are available:
- **charts_to_dataframe**: One row per chart (chart-level data)
- **positions_to_dataframe**: One row per position (planet positions)
- **aspects_to_dataframe**: One row per aspect

+++

### 2.1 Chart-Level DataFrame

One row per chart with summary data.

```{code-cell} ipython3
# Convert charts to DataFrame
df = charts_to_dataframe(custom_charts)
print(f"DataFrame shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")
```

```{code-cell} ipython3
# View the data
df[
    [
        "name",
        "sun_sign",
        "moon_sign",
        "asc_sign",
        "fire_count",
        "earth_count",
        "air_count",
        "water_count",
    ]
]
```

```{code-cell} ipython3
# Sun sign distribution
df["sun_sign"].value_counts()
```

### 2.2 Position-Level DataFrame

One row per celestial position - useful for analyzing specific planets across many charts.

```{code-cell} ipython3
# Convert to positions DataFrame
positions_df = positions_to_dataframe(custom_charts)
print(f"DataFrame shape: {positions_df.shape}")
positions_df.head(10)
```

```{code-cell} ipython3
# Filter to planets only
planets_df = positions_df[positions_df["object_type"] == "planet"]
print(f"Planet positions: {len(planets_df)}")

# Sign distribution for all planets
planets_df["sign"].value_counts()
```

```{code-cell} ipython3
# Retrograde analysis
retrograde_df = planets_df[planets_df["is_retrograde"]]
print(f"Retrograde positions: {len(retrograde_df)}")
retrograde_df[["chart_name", "object_name", "sign", "is_retrograde"]]
```

### 2.3 Aspect-Level DataFrame

One row per aspect - useful for aspect frequency analysis.

```{code-cell} ipython3
# Convert to aspects DataFrame
aspects_df = aspects_to_dataframe(charts_with_aspects)
print(f"DataFrame shape: {aspects_df.shape}")
aspects_df.head(10)
```

```{code-cell} ipython3
# Most common aspects
aspects_df["aspect_name"].value_counts()
```

```{code-cell} ipython3
# Sun-Moon aspects
sun_moon = aspects_df[
    ((aspects_df["object1"] == "Sun") & (aspects_df["object2"] == "Moon"))
    | ((aspects_df["object1"] == "Moon") & (aspects_df["object2"] == "Sun"))
]
print(f"Sun-Moon aspects: {len(sun_moon)}")
sun_moon[["chart_name", "aspect_name", "orb"]]
```

---

## 3. ChartQuery

Filter chart collections by astrological criteria using a fluent API.

Query methods include:
- `where_sun()`, `where_moon()`, `where_planet()`, `where_angle()`
- `where_aspect()`, `where_pattern()`
- `where_element_dominant()`, `where_modality_dominant()`
- `where_sect()`, `where_custom()`

+++

### 3.1 Basic Filtering

```{code-cell} ipython3
# Find charts with Sun in fire signs
fire_sun_charts = (
    ChartQuery(custom_charts).where_sun(sign=["Aries", "Leo", "Sagittarius"]).results()
)
print(f"Charts with Sun in fire signs: {len(fire_sun_charts)}")
for chart in fire_sun_charts:
    print(f"  - {chart.metadata.get('name')}: Sun in {chart.get_object('Sun').sign}")
```

```{code-cell} ipython3
# Find charts with Mercury retrograde
mercury_rx = (
    ChartQuery(custom_charts).where_planet("Mercury", retrograde=True).results()
)
print(f"Charts with Mercury retrograde: {len(mercury_rx)}")
```

### 3.2 Chained Filters

Combine multiple criteria for complex queries.

```{code-cell} ipython3
# Find day charts with Sun in earth signs
results = (
    ChartQuery(custom_charts)
    .where_sun(sign=["Taurus", "Virgo", "Capricorn"])
    .where_sect("day")
    .results()
)
print(f"Day charts with Sun in earth signs: {len(results)}")
```

```{code-cell} ipython3
# Find charts with Sun-Moon conjunction
conjunctions = (
    ChartQuery(charts_with_aspects)
    .where_aspect("Sun", "Moon", aspect="Conjunction", orb_max=10)
    .results()
)
print(f"Charts with Sun-Moon conjunction: {len(conjunctions)}")
```

### 3.3 Element and Modality Dominance

```{code-cell} ipython3
# Find charts with dominant fire element (4+ planets)
fire_dominant = (
    ChartQuery(custom_charts).where_element_dominant("fire", min_count=4).results()
)
print(f"Charts with fire dominance: {len(fire_dominant)}")

# Find charts with dominant cardinal modality
cardinal_dominant = (
    ChartQuery(custom_charts).where_modality_dominant("cardinal", min_count=4).results()
)
print(f"Charts with cardinal dominance: {len(cardinal_dominant)}")
```

### 3.4 Custom Predicates

Use any custom function to filter charts.

```{code-cell} ipython3
# Find charts with more than 5 aspects
many_aspects = (
    ChartQuery(charts_with_aspects).where_custom(lambda c: len(c.aspects) > 5).results()
)
print(f"Charts with > 5 aspects: {len(many_aspects)}")
```

```{code-cell} ipython3
# Find charts where Moon is in the same sign as Sun
sun_moon_same = (
    ChartQuery(custom_charts)
    .where_custom(
        lambda c: (
            (s := c.get_object("Sun"))
            and (m := c.get_object("Moon"))
            and s.sign == m.sign
        )
    )
    .results()
)
print(f"Charts with Sun and Moon in same sign: {len(sun_moon_same)}")
for chart in sun_moon_same:
    if sun := chart.get_object("Sun"):
        print(f"  - {chart.metadata.get('name')}: both in {sun.sign}")
```

### 3.5 Result Methods

```{code-cell} ipython3
query = ChartQuery(custom_charts).where_sun(
    sign=["Aries", "Taurus", "Gemini", "Cancer"]
)

# Get count
print(f"Count: {query.count()}")

# Get first result
first = query.first()
if first:
    print(f"First match: {first.metadata.get('name')}")

# Convert to DataFrame
df = query.to_dataframe()
df[["name", "sun_sign", "moon_sign"]]
```

---

## 4. ChartStats

Compute aggregate statistics across chart collections.

```{code-cell} ipython3
# Create stats object
stats = ChartStats(custom_charts)
print(f"Analyzing {stats.chart_count} charts")
```

### 4.1 Element and Modality Distribution

```{code-cell} ipython3
# Element distribution (normalized proportions)
elements = stats.element_distribution()
print("Element Distribution:")
for element, proportion in elements.items():
    print(f"  {element.title()}: {proportion:.1%}")
```

```{code-cell} ipython3
# Modality distribution
modalities = stats.modality_distribution()
print("Modality Distribution:")
for modality, proportion in modalities.items():
    print(f"  {modality.title()}: {proportion:.1%}")
```

### 4.2 Sign Distribution

```{code-cell} ipython3
# Sun sign distribution
sun_signs = stats.sign_distribution("Sun")
print("Sun Sign Distribution:")
for sign, count in sun_signs.items():
    if count > 0:
        print(f"  {sign}: {count}")
```

```{code-cell} ipython3
# Moon sign distribution
moon_signs = stats.sign_distribution("Moon")
print("Moon Sign Distribution:")
for sign, count in moon_signs.items():
    if count > 0:
        print(f"  {sign}: {count}")
```

### 4.3 House Distribution

```{code-cell} ipython3
# Sun house distribution
sun_houses = stats.house_distribution("Sun")
print("Sun House Distribution:")
for house, count in sun_houses.items():
    if count > 0:
        print(f"  House {house}: {count}")
```

### 4.4 Aspect Frequency

```{code-cell} ipython3
# Create stats from charts with aspects
stats_aspects = ChartStats(charts_with_aspects)

# Overall aspect frequency
aspect_freq = stats_aspects.aspect_frequency()
print("Aspect Frequency:")
for aspect, count in list(aspect_freq.items())[:5]:
    print(f"  {aspect}: {count}")
```

```{code-cell} ipython3
# Aspect frequency between specific planets
sun_moon_aspects = stats_aspects.aspect_pair_frequency("Sun", "Moon")
print("Sun-Moon Aspect Frequency:")
for aspect, count in sun_moon_aspects.items():
    print(f"  {aspect}: {count}")
```

### 4.5 Retrograde Frequency

```{code-cell} ipython3
# Retrograde frequency by planet
retro_freq = stats.retrograde_frequency()
print("Retrograde Counts by Planet:")
for planet, count in retro_freq.items():
    print(f"  {planet}: {count}")
```

```{code-cell} ipython3
# Retrograde rate (normalized)
retro_rate = stats.retrograde_frequency(normalize=True)
print("Retrograde Rate by Planet:")
for planet, rate in retro_rate.items():
    print(f"  {planet}: {rate:.1%}")
```

### 4.6 Sect Distribution

```{code-cell} ipython3
# Day vs night charts
sect_dist = stats.sect_distribution()
print("Sect Distribution:")
for sect, count in sect_dist.items():
    print(f"  {sect.title()}: {count}")
```

### 4.7 Cross-Tabulation

Create contingency tables to analyze relationships between variables.

```{code-cell} ipython3
# Sun sign vs Moon sign cross-tabulation
crosstab = stats.cross_tab("sun_sign", "moon_sign")
print("Sun Sign vs Moon Sign:")
crosstab
```

```{code-cell} ipython3
# Sun sign vs sect
sun_sect = stats.cross_tab("sun_sign", "sect")
print("Sun Sign vs Sect:")
sun_sect
```

### 4.8 Summary Report

```{code-cell} ipython3
# Get comprehensive summary
summary = stats.summary()

print(f"Chart Count: {summary['chart_count']}")
print(f"\nElement Distribution: {summary['element_distribution']}")
print(f"\nModality Distribution: {summary['modality_distribution']}")
print(f"\nSect Distribution: {summary['sect_distribution']}")
```

---

## 5. Export Utilities

Save chart data to files for external analysis.

(Examples in this notebook use `tempfile` for cookbook purposes; replace with the actual directory you want.)

+++

### 5.1 CSV Export

```{code-cell} ipython3
import tempfile
from pathlib import Path

# Export chart-level data
with tempfile.TemporaryDirectory() as tmpdir:
    # Charts CSV
    charts_path = Path(tmpdir) / "charts.csv"
    export_csv(custom_charts, charts_path, schema="charts")
    print(f"Exported charts to {charts_path}")

    # Read back and display
    df = pd.read_csv(charts_path)
    print(f"Shape: {df.shape}")
    df.head()
```

```{code-cell} ipython3
# Export positions
with tempfile.TemporaryDirectory() as tmpdir:
    positions_path = Path(tmpdir) / "positions.csv"
    export_csv(custom_charts, positions_path, schema="positions")

    df = pd.read_csv(positions_path)
    print(f"Positions CSV shape: {df.shape}")
    df.head()
```

### 5.2 JSON Export

```{code-cell} ipython3
import json

with tempfile.TemporaryDirectory() as tmpdir:
    # Standard JSON array
    json_path = Path(tmpdir) / "charts.json"
    export_json(custom_charts, json_path)

    with open(json_path) as f:
        data = json.load(f)

    print(f"Exported {len(data)} charts to JSON")
    print(f"Keys in first chart: {list(data[0].keys())[:10]}...")
```

```{code-cell} ipython3
# JSON Lines format (for streaming large datasets)
with tempfile.TemporaryDirectory() as tmpdir:
    jsonl_path = Path(tmpdir) / "charts.jsonl"
    export_json(custom_charts, jsonl_path, lines=True)

    with open(jsonl_path) as f:
        lines = f.readlines()

    print(f"Exported {len(lines)} lines to JSONL")
    print(f"First line preview: {lines[0][:100]}...")
```

---

## 6. Full Workflow Examples

Complete research workflows combining multiple features.

+++

### 6.1 Research Question: Element Distribution in Scientists vs Artists

Compare element distributions between different categories.

```{code-cell} ipython3
# Calculate charts for scientists and artists
scientists = BatchCalculator.from_registry(category="scientist").calculate_all()
artists = BatchCalculator.from_registry(category="artist").calculate_all()

print(f"Scientists: {len(scientists)}")
print(f"Artists: {len(artists)}")

# Compare element distributions
if scientists and artists:
    sci_stats = ChartStats(scientists)
    art_stats = ChartStats(artists)

    print("\nElement Distribution Comparison:")
    print(f"{'Element':<12} {'Scientists':<15} {'Artists':<15}")
    print("-" * 42)

    sci_elements = sci_stats.element_distribution()
    art_elements = art_stats.element_distribution()

    for element in ["fire", "earth", "air", "water"]:
        sci_pct = sci_elements.get(element, 0)
        art_pct = art_elements.get(element, 0)
        print(f"{element.title():<12} {sci_pct:>12.1%}   {art_pct:>12.1%}")
```

### 6.2 Research Question: Mercury Retrograde Frequency

Analyze how often Mercury is retrograde in a collection.

```{code-cell} ipython3
# Get all charts
all_charts = BatchCalculator.from_registry().calculate_all()

if all_charts:
    # Query for Mercury retrograde
    mercury_rx_charts = (
        ChartQuery(all_charts).where_planet("Mercury", retrograde=True).results()
    )

    total = len(all_charts)
    rx_count = len(mercury_rx_charts)

    print(f"Total charts: {total}")
    print(f"Mercury Rx charts: {rx_count}")
    print(f"Mercury Rx rate: {rx_count / total:.1%}")
    print("\n(Expected astronomical rate is ~19%)")
```

### 6.3 Research Question: Sun-Moon Aspect Distribution

Analyze the distribution of aspects between Sun and Moon.

```{code-cell} ipython3
# Calculate charts with aspects
charts = BatchCalculator.from_registry().with_aspects().calculate_all()

if charts:
    stats = ChartStats(charts)
    sun_moon_aspects = stats.aspect_pair_frequency("Sun", "Moon")

    print("Sun-Moon Aspect Distribution:")
    total_aspects = sum(sun_moon_aspects.values())
    for aspect, count in sorted(sun_moon_aspects.items(), key=lambda x: -x[1]):
        pct = count / total_aspects if total_aspects > 0 else 0
        print(f"  {aspect}: {count} ({pct:.1%})")
```

### 6.4 Pipeline: Filter, Analyze, Export

A complete data pipeline example.

```{code-cell} ipython3
# 1. Calculate all charts with aspects
charts = (
    BatchCalculator.from_registry()
    .with_aspects()
    .add_analyzer(AspectPatternAnalyzer())
    .calculate_all()
)

print(f"Step 1: Calculated {len(charts)} charts")

# 2. Filter to fire-dominant charts
fire_charts = ChartQuery(charts).where_element_dominant("fire", min_count=4).results()

print(f"Step 2: Found {len(fire_charts)} fire-dominant charts")

# 3. Analyze the subset
if fire_charts:
    fire_stats = ChartStats(fire_charts)
    print("\nStep 3: Analysis of fire-dominant charts:")
    print(f"  Element distribution: {fire_stats.element_distribution()}")
    print(f"  Sect distribution: {fire_stats.sect_distribution()}")

# 4. Convert to DataFrame for further analysis
if fire_charts:
    df = charts_to_dataframe(fire_charts)
    print(f"\nStep 4: DataFrame created with {len(df)} rows")
    display(df[["name", "sun_sign", "fire_count", "sect"]].head())
```

---

## 7. Statistical Analysis Patterns

Stellium prepares your data for analysis. For hypothesis testing and statistical inference, use standard libraries like **scipy** and **statsmodels**.

This section demonstrates the handoff pattern: Stellium extracts astrological data -> you apply statistical methods.

```{code-cell} ipython3
# Calculate all charts from the registry for statistical analysis
from scipy import stats as scipy_stats

all_charts = (
    BatchCalculator.from_registry(event_type="birth")
    .with_aspects()
    .add_analyzer(AspectPatternAnalyzer())
    .calculate_all()
)
print(f"Loaded {len(all_charts)} charts from NotableRegistry")
```

### 7.1 Chi-Square Test: Sun Sign Distribution

Test whether Sun signs are uniformly distributed (null hypothesis: each sign has equal probability of 1/12).

```{code-cell} ipython3
# Get Sun sign distribution from Stellium
chart_stats = ChartStats(all_charts)
sun_dist = chart_stats.sign_distribution("Sun")

# Observed counts (in zodiac order)
zodiac_order = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
observed = [sun_dist[sign] for sign in zodiac_order]

# Expected counts under uniform distribution
n_charts = len(all_charts)
expected = [n_charts / 12] * 12

# Chi-square goodness-of-fit test
chi2, p_value = scipy_stats.chisquare(observed, expected)

print("Sun Sign Distribution Test (H₀: uniform distribution)")
print("=" * 55)
print(f"\n{'Sign':<12} {'Observed':>10} {'Expected':>10}")
print("-" * 34)
for sign, obs, exp in zip(zodiac_order, observed, expected, strict=False):
    print(f"{sign:<12} {obs:>10} {exp:>10.1f}")

print(f"\nχ² = {chi2:.3f}")
print(f"p-value = {p_value:.4f}")
print(
    f"\nConclusion: {'Reject H₀ (p < 0.05)' if p_value < 0.05 else 'Cannot reject H₀ (p ≥ 0.05)'}"
)
```

### 7.2 Chi-Square Test of Independence: Sun Sign vs Moon Sign

Test whether Sun sign and Moon sign placements are independent of each other.

```{code-cell} ipython3
# Get cross-tabulation from Stellium
crosstab = chart_stats.cross_tab("sun_sign", "moon_sign")

# Reindex to ensure all signs are present
crosstab = crosstab.reindex(index=zodiac_order, columns=zodiac_order, fill_value=0)

print("Sun Sign x Moon Sign Contingency Table:")
display(crosstab)

# Chi-square test of independence
chi2, p_value, dof, expected_freq = scipy_stats.chi2_contingency(crosstab)

print(f"\nχ² = {chi2:.3f}")
print(f"Degrees of freedom = {dof}")
print(f"p-value = {p_value:.4f}")
print(
    f"\nConclusion: {'Reject H₀ - signs may be dependent' if p_value < 0.05 else 'Cannot reject H₀ - signs appear independent'}"
)
```

### 7.3 Binomial Test: Mercury Retrograde Rate

Test whether Mercury retrograde frequency in our sample differs from the astronomical baseline (~19% of the time).

```{code-cell} ipython3
# Query for Mercury retrograde charts
mercury_rx_charts = (
    ChartQuery(all_charts).where_planet("Mercury", retrograde=True).results()
)

n_total = len(all_charts)
n_rx = len(mercury_rx_charts)
observed_rate = n_rx / n_total
expected_rate = 0.19  # Astronomical baseline

# Binomial test (two-sided)
result = scipy_stats.binomtest(n_rx, n_total, expected_rate, alternative="two-sided")

print("Mercury Retrograde Frequency Test")
print("=" * 45)
print(f"\nTotal charts: {n_total}")
print(f"Mercury Rx charts: {n_rx}")
print(f"Observed rate: {observed_rate:.1%}")
print(f"Expected rate (astronomical): {expected_rate:.1%}")
print(f"\np-value = {result.pvalue:.4f}")
print(f"95% CI: ({result.proportion_ci().low:.1%}, {result.proportion_ci().high:.1%})")
print(
    f"\nConclusion: {'Sample differs from baseline' if result.pvalue < 0.05 else 'Sample consistent with baseline'}"
)
```

### 7.4 Correlation: Element Counts

Test whether element counts are correlated (e.g., do charts high in fire tend to be low in water?).

```{code-cell} ipython3
# Get chart DataFrame with element counts
df = charts_to_dataframe(all_charts)

# Extract element columns
elements = ["fire_count", "earth_count", "air_count", "water_count"]
element_df = df[elements]

# Correlation matrix
corr_matrix = element_df.corr()

print("Element Count Correlation Matrix:")
print("(Negative correlations expected since planets sum to ~10)")
display(corr_matrix.round(3))

# Test significance of fire-water correlation
fire = df["fire_count"].values
water = df["water_count"].values
r, p_value = scipy_stats.pearsonr(fire, water)

print("\nFire-Water Correlation:")
print(f"  Pearson r = {r:.3f}")
print(f"  p-value = {p_value:.4f}")
print(f"  {'Significant' if p_value < 0.05 else 'Not significant'} at α=0.05")
```

### 7.5 Comparing Groups: Scientists vs Artists

Use a Mann-Whitney U test to compare element distributions between categories.

```{code-cell} ipython3
# Calculate charts by category
scientists = BatchCalculator.from_registry(category="scientist").calculate_all()
artists = BatchCalculator.from_registry(category="artist").calculate_all()

# Convert to DataFrames
sci_df = charts_to_dataframe(scientists)
art_df = charts_to_dataframe(artists)

print(f"Scientists: n={len(sci_df)}")
print(f"Artists: n={len(art_df)}")

# Compare water element counts between groups
print("\n" + "=" * 50)
print("Water Element Comparison: Scientists vs Artists")
print("=" * 50)

sci_water = sci_df["water_count"].values
art_water = art_df["water_count"].values

print(
    f"\nScientists - Water count: mean={sci_water.mean():.2f}, median={pd.Series(sci_water).median():.1f}"
)
print(
    f"Artists - Water count: mean={art_water.mean():.2f}, median={pd.Series(art_water).median():.1f}"
)

# Mann-Whitney U test (non-parametric, doesn't assume normal distribution)
stat, p_value = scipy_stats.mannwhitneyu(sci_water, art_water, alternative="two-sided")

print("\nMann-Whitney U test:")
print(f"  U statistic = {stat:.1f}")
print(f"  p-value = {p_value:.4f}")
print(
    f"  {'Groups differ significantly' if p_value < 0.05 else 'No significant difference'}"
)
```

### 7.6 Pattern: Full Statistical Workflow

A complete example combining Stellium data extraction with statistical analysis.

```{code-cell} ipython3
# Research question: Do people with Grand Trines have different element distributions?

# Step 1: Stellium - Query charts with Grand Trines
grand_trine_charts = ChartQuery(all_charts).where_pattern("Grand Trine").results()

no_grand_trine_charts = (
    ChartQuery(all_charts)
    .where_custom(
        lambda c: (
            not any(
                p.name == "Grand Trine" for p in c.metadata.get("aspect_patterns", [])
            )
        )
    )
    .results()
)

print(f"Charts with Grand Trine: {len(grand_trine_charts)}")
print(f"Charts without Grand Trine: {len(no_grand_trine_charts)}")

# Step 2: Stellium - Convert to DataFrames
gt_df = charts_to_dataframe(grand_trine_charts)
no_gt_df = charts_to_dataframe(no_grand_trine_charts)

# Step 3: scipy - Statistical comparison
print("\n" + "=" * 60)
print("Element Distribution: Grand Trine vs No Grand Trine")
print("=" * 60)

for element in ["fire", "earth", "air", "water"]:
    col = f"{element}_count"
    gt_vals = gt_df[col].values
    no_gt_vals = no_gt_df[col].values

    gt_mean = gt_vals.mean()
    no_gt_mean = no_gt_vals.mean()

    stat, p = scipy_stats.mannwhitneyu(gt_vals, no_gt_vals, alternative="two-sided")
    sig = "*" if p < 0.05 else ""

    print(f"\n{element.title()}:")
    print(f"  Grand Trine: mean={gt_mean:.2f}")
    print(f"  No Grand Trine: mean={no_gt_mean:.2f}")
    print(f"  p-value = {p:.4f} {sig}")
```

---

## Summary

The `stellium.analysis` module provides a complete toolkit for large-scale astrological data analysis:

| Component | Purpose |
|-----------|--------|
| `BatchCalculator` | Efficiently calculate many charts at once |
| `charts_to_dataframe()` | Convert to chart-level DataFrame |
| `positions_to_dataframe()` | Convert to position-level DataFrame |
| `aspects_to_dataframe()` | Convert to aspect-level DataFrame |
| `ChartQuery` | Filter charts by astrological criteria |
| `ChartStats` | Compute aggregate statistics |
| `export_csv()` | Export to CSV files |
| `export_json()` | Export to JSON or JSONL |

**Statistical analysis** is handled by external libraries:

| Library | Use Case |
|---------|----------|
| `scipy.stats` | Hypothesis testing (chi-square, t-tests, Mann-Whitney) |
| `statsmodels` | Regression, ANOVA, more advanced tests |
| `pingouin` | User-friendly statistical tests |

Stellium prepares the data; you choose the statistical methodology appropriate for your research question.

For more information, see the [Stellium documentation](https://stellium.readthedocs.io/).
