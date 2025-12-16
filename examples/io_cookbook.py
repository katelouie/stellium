#!/usr/bin/env python3
"""
I/O Cookbook - Examples for Importing and Exporting Birth Data

This cookbook demonstrates all the ways to import birth data into Stellium
from various file formats and data sources, as well as exporting data.

Supported formats:
- AAF (Astrodienst Astrological Format) - Export from astro.com
- CSV (Comma-Separated Values) - Universal spreadsheet format
- pandas DataFrame - In-memory data from any source

Run this script to see all I/O capabilities in action.

Usage:
    source ~/.zshrc && pyenv activate starlight
    python examples/io_cookbook.py

For full documentation, see the stellium.io module docstrings.
"""

import os
from pathlib import Path

# Check for pandas availability
try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Note: pandas not installed. DataFrame examples will be skipped.")

from stellium import ChartBuilder

# Import all I/O functions
from stellium.io import (
    CSVColumnMapping,
    parse_aaf,
    parse_csv,
    read_csv,
)

if HAS_PANDAS:
    from stellium.io import (
        dataframe_from_natives,
        parse_dataframe,
        read_dataframe,
    )

# Output directory for generated files
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "io_examples"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def subsection_header(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---\n")


# =============================================================================
# PART 1: CSV PARSING
# =============================================================================


def example_1_csv_auto_detection():
    """
    Example 1: CSV with Auto-Detection

    The simplest way to import CSV data. Column names are automatically
    detected based on common naming conventions.
    """
    section_header("Example 1: CSV with Auto-Detection")

    # Create a sample CSV with standard column names
    csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
Albert Einstein,1879-03-14,11:30,48.4011,9.9876
Marie Curie,1867-11-07,12:00,52.2297,21.0122
"""
    csv_path = OUTPUT_DIR / "sample_standard.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Parse with auto-detection
    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        print(f"  - {native.name}: {native.datetime.utc_datetime.date()}")

    # Calculate charts
    print("\nChart calculations:")
    for native in natives:
        chart = ChartBuilder.from_native(native).calculate()
        sun = chart.get_object("Sun")
        print(f"  {native.name}: Sun at {sun.sign} {sun.sign_degree:.1f}")


def example_2_csv_custom_columns():
    """
    Example 2: CSV with Custom Column Names

    Use read_csv() when your CSV has non-standard column names.
    """
    section_header("Example 2: CSV with Custom Column Names")

    # Create a CSV with non-standard column names
    csv_content = """Person,Birthday,Birth Time,Lat,Long,City
Kate Louie,1994-01-06,11:47,37.3861,-122.0839,Mountain View CA
Albert Einstein,1879-03-14,11:30,48.4011,9.9876,Ulm Germany
"""
    csv_path = OUTPUT_DIR / "sample_custom_columns.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Specify column names explicitly
    natives = read_csv(
        csv_path,
        name="Person",
        date="Birthday",
        time="Birth Time",
        latitude="Lat",
        longitude="Long",
        location="City",  # Will be used as display name
    )

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        print(f"  - {native.name} from {native.location.name}")


def example_3_csv_split_name():
    """
    Example 3: CSV with Split First/Last Name

    Handle CSVs where name is in separate first_name and last_name columns.
    """
    section_header("Example 3: CSV with Split First/Last Name")

    csv_content = """first_name,last_name,date,time,latitude,longitude
Kate,Louie,1994-01-06,11:47,37.3861,-122.0839
Albert,Einstein,1879-03-14,11:30,48.4011,9.9876
"""
    csv_path = OUTPUT_DIR / "sample_split_name.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Auto-detection handles first_name + last_name automatically
    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives (names combined automatically):")
    for native in natives:
        print(f"  - {native.name}")

    # Or specify explicitly with tuple (must also specify date/time columns)
    natives = read_csv(
        csv_path,
        name=("first_name", "last_name"),  # Tuple for first/last
        date="date",
        time="time",
        latitude="latitude",
        longitude="longitude",
    )

    print("\nWith explicit tuple mapping:")
    for native in natives:
        print(f"  - {native.name}")


def example_4_csv_date_formats():
    """
    Example 4: CSV with Various Date Formats

    Handle different date formats using format hints.
    """
    section_header("Example 4: CSV with Various Date Formats")

    # European date format (DD/MM/YYYY)
    csv_content = """name,date,time,latitude,longitude
Kate Louie,06/01/1994,11:47,37.3861,-122.0839
"""
    csv_path = OUTPUT_DIR / "sample_european_dates.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV with European dates: {csv_path}")

    # Without format hint - might be ambiguous
    print("\nWithout format hint (auto-detection):")
    natives = parse_csv(csv_path)
    for native in natives:
        print(f"  Parsed as: {native.datetime.utc_datetime.date()}")

    # With explicit format hint
    print("\nWith European format hint (%d/%m/%Y):")
    mapping = CSVColumnMapping(
        name="name",
        date="date",
        time="time",
        latitude="latitude",
        longitude="longitude",
        date_format="%d/%m/%Y",  # Day/Month/Year
    )
    natives = parse_csv(csv_path, mapping=mapping)
    for native in natives:
        print(f"  Parsed as: {native.datetime.utc_datetime.date()}")


def example_5_csv_12_hour_time():
    """
    Example 5: CSV with 12-Hour Time Format

    Handle AM/PM time formats.
    """
    section_header("Example 5: CSV with 12-Hour Time Format")

    csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47 AM,37.3861,-122.0839
Night Owl,1990-05-15,2:30 PM,40.7128,-74.0060
"""
    csv_path = OUTPUT_DIR / "sample_12hour.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Auto-detection handles AM/PM
    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        time = native.datetime.utc_datetime.strftime("%H:%M")
        print(f"  - {native.name}: {time} (24-hour)")


def example_6_csv_combined_datetime():
    """
    Example 6: CSV with Combined DateTime Column

    Handle CSVs where date and time are in a single column.
    """
    section_header("Example 6: CSV with Combined DateTime")

    csv_content = """name,datetime,latitude,longitude
Kate Louie,1994-01-06 11:47:00,37.3861,-122.0839
Albert Einstein,1879-03-14T11:30:00,48.4011,9.9876
"""
    csv_path = OUTPUT_DIR / "sample_combined_datetime.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Auto-detection finds "datetime" column
    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        dt = native.datetime.utc_datetime
        print(f"  - {native.name}: {dt.date()} {dt.strftime('%H:%M')}")


def example_7_csv_date_components():
    """
    Example 7: CSV with Separate Date/Time Components

    Handle CSVs where year, month, day, hour, minute are separate columns.
    """
    section_header("Example 7: CSV with Separate Date/Time Components")

    csv_content = """name,year,month,day,hour,minute,latitude,longitude
Kate Louie,1994,1,6,11,47,37.3861,-122.0839
Albert Einstein,1879,3,14,11,30,48.4011,9.9876
"""
    csv_path = OUTPUT_DIR / "sample_components.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Auto-detection handles separate components
    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        dt = native.datetime.utc_datetime
        print(
            f"  - {native.name}: {dt.year}-{dt.month:02d}-{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}"
        )


def example_8_csv_location_with_coords():
    """
    Example 8: CSV with Location Name AND Coordinates

    When you have both coordinates and a location name column,
    the coordinates are used for calculations and the name is preserved.
    """
    section_header("Example 8: Location Name with Coordinates")

    csv_content = """name,date,time,latitude,longitude,city
Kate Louie,1994-01-06,11:47,37.3861,-122.0839,Mountain View CA
Albert Einstein,1879-03-14,11:30,48.4011,9.9876,Ulm Germany
Marie Curie,1867-11-07,12:00,52.2297,21.0122,Warsaw Poland
"""
    csv_path = OUTPUT_DIR / "sample_location_name.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    natives = parse_csv(csv_path)

    print(f"\nParsed {len(natives)} natives with location names:")
    for native in natives:
        loc = native.location
        print(f"  - {native.name}")
        print(f"      Location: {loc.name}")
        print(f"      Coords: ({loc.latitude:.4f}, {loc.longitude:.4f})")


def example_9_csv_error_handling():
    """
    Example 9: CSV Error Handling

    Handle malformed rows gracefully or raise on errors.
    """
    section_header("Example 9: Error Handling")

    csv_content = """name,date,time,latitude,longitude
Valid Person,1994-01-06,11:47,37.3861,-122.0839
Bad Date,not-a-date,11:47,37.3861,-122.0839
Missing Coords,1994-01-06,11:47,,
Another Valid,1879-03-14,11:30,48.4011,9.9876
"""
    csv_path = OUTPUT_DIR / "sample_errors.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV with errors: {csv_path}")

    # Default: skip_errors=True - skips bad rows
    print("\nWith skip_errors=True (default):")
    natives = parse_csv(csv_path, skip_errors=True)
    print(f"  Parsed {len(natives)} valid rows")

    # Strict mode: raise on first error
    print("\nWith skip_errors=False:")
    try:
        natives = parse_csv(csv_path, skip_errors=False)
    except ValueError as e:
        print(f"  Raised error: {e}")


def example_10_csv_column_mapping_object():
    """
    Example 10: Using CSVColumnMapping Object

    For complex configurations, use CSVColumnMapping directly.
    """
    section_header("Example 10: CSVColumnMapping Object")

    csv_content = """Full Name,DOB,TOB,Birth Lat,Birth Lon,Place,TZ
Kate Louie,06.01.1994,11:47,37.3861,-122.0839,Mountain View,America/Los_Angeles
"""
    csv_path = OUTPUT_DIR / "sample_full_mapping.csv"
    csv_path.write_text(csv_content)
    print(f"Created sample CSV: {csv_path}")

    # Create detailed mapping
    mapping = CSVColumnMapping(
        name="Full Name",
        date="DOB",
        time="TOB",
        latitude="Birth Lat",
        longitude="Birth Lon",
        location="Place",
        timezone="TZ",
        date_format="%d.%m.%Y",  # European format
    )

    natives = parse_csv(csv_path, mapping=mapping)

    print("\nParsed with full mapping:")
    for native in natives:
        print(f"  - {native.name}")
        print(f"      Date: {native.datetime.utc_datetime.date()}")
        print(f"      Location: {native.location.name}")
        print(f"      Timezone: {native.location.timezone}")


# =============================================================================
# PART 2: DATAFRAME PARSING (requires pandas)
# =============================================================================


def example_11_dataframe_auto():
    """
    Example 11: DataFrame with Auto-Detection

    Parse a pandas DataFrame with automatic column detection.
    """
    if not HAS_PANDAS:
        print("\nSkipping DataFrame examples (pandas not installed)")
        return

    section_header("Example 11: DataFrame with Auto-Detection")

    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Albert Einstein", "Marie Curie"],
            "date": ["1994-01-06", "1879-03-14", "1867-11-07"],
            "time": ["11:47", "11:30", "12:00"],
            "latitude": [37.3861, 48.4011, 52.2297],
            "longitude": [-122.0839, 9.9876, 21.0122],
            "city": ["Mountain View CA", "Ulm Germany", "Warsaw Poland"],
        }
    )

    print("Input DataFrame:")
    print(df.to_string(index=False))

    natives = parse_dataframe(df)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        print(f"  - {native.name} from {native.location.name}")


def example_12_dataframe_custom():
    """
    Example 12: DataFrame with Custom Column Names

    Use read_dataframe() for non-standard column names.
    """
    if not HAS_PANDAS:
        return

    section_header("Example 12: DataFrame with Custom Columns")

    df = pd.DataFrame(
        {
            "Person": ["Kate Louie", "Albert Einstein"],
            "Birthday": ["1994-01-06", "1879-03-14"],
            "Birth Time": ["11:47", "11:30"],
            "Lat": [37.3861, 48.4011],
            "Long": [-122.0839, 9.9876],
        }
    )

    print("Input DataFrame:")
    print(df.to_string(index=False))

    natives = read_dataframe(
        df,
        name="Person",
        date="Birthday",
        time="Birth Time",
        latitude="Lat",
        longitude="Long",
    )

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        print(f"  - {native.name}")


def example_13_dataframe_from_excel():
    """
    Example 13: DataFrame from Excel File

    Load birth data from Excel via pandas.
    """
    if not HAS_PANDAS:
        return

    section_header("Example 13: DataFrame from Excel")

    # Check for openpyxl (required for Excel)
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        print("Skipping Excel example (openpyxl not installed)")
        print("Install with: pip install openpyxl")
        return

    # Create a sample Excel file
    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Albert Einstein"],
            "date": ["1994-01-06", "1879-03-14"],
            "time": ["11:47", "11:30"],
            "latitude": [37.3861, 48.4011],
            "longitude": [-122.0839, 9.9876],
        }
    )

    excel_path = OUTPUT_DIR / "sample_birth_data.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"Created sample Excel file: {excel_path}")

    # Load and parse
    df_loaded = pd.read_excel(excel_path)
    natives = parse_dataframe(df_loaded)

    print(f"\nParsed {len(natives)} natives from Excel:")
    for native in natives:
        print(f"  - {native.name}")


def example_14_dataframe_numeric_columns():
    """
    Example 14: DataFrame with Numeric Columns

    Handle DataFrames where date/time components are numeric (ints).
    """
    if not HAS_PANDAS:
        return

    section_header("Example 14: DataFrame with Numeric Columns")

    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Albert Einstein"],
            "year": [1994, 1879],  # int
            "month": [1, 3],  # int
            "day": [6, 14],  # int
            "hour": [11, 11],  # int
            "minute": [47, 30],  # int
            "latitude": [37.3861, 48.4011],  # float
            "longitude": [-122.0839, 9.9876],  # float
        }
    )

    print("Input DataFrame (numeric columns):")
    print(df.to_string(index=False))
    print(f"\nColumn types: {dict(df.dtypes)}")

    natives = parse_dataframe(df)

    print(f"\nParsed {len(natives)} natives:")
    for native in natives:
        dt = native.datetime.utc_datetime
        print(f"  - {native.name}: {dt.year}-{dt.month:02d}-{dt.day:02d}")


def example_15_dataframe_export():
    """
    Example 15: Export Natives to DataFrame

    Convert a list of Natives back to a pandas DataFrame.
    """
    if not HAS_PANDAS:
        return

    section_header("Example 15: Export to DataFrame")

    # Create some natives
    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Albert Einstein", "Marie Curie"],
            "date": ["1994-01-06", "1879-03-14", "1867-11-07"],
            "time": ["11:47", "11:30", "12:00"],
            "latitude": [37.3861, 48.4011, 52.2297],
            "longitude": [-122.0839, 9.9876, 21.0122],
            "city": ["Mountain View CA", "Ulm Germany", "Warsaw Poland"],
        }
    )
    natives = parse_dataframe(df)

    print(f"Parsed {len(natives)} natives")

    # Export back to DataFrame
    print("\nExported DataFrame (default):")
    result_df = dataframe_from_natives(natives)
    print(result_df.to_string(index=False))

    # Export with timezone
    print("\nExported DataFrame (with timezone):")
    result_df = dataframe_from_natives(natives, include_timezone=True)
    print(result_df.to_string(index=False))

    # Export without coordinates
    print("\nExported DataFrame (without coordinates):")
    result_df = dataframe_from_natives(natives, include_coords=False)
    print(result_df.to_string(index=False))


def example_16_dataframe_roundtrip():
    """
    Example 16: Round-Trip (Excel -> Natives -> Charts -> Excel)

    Complete workflow: load data, calculate charts, export results.
    """
    if not HAS_PANDAS:
        return

    section_header("Example 16: Complete Round-Trip Workflow")

    # Start with a DataFrame
    df = pd.DataFrame(
        {
            "name": ["Kate Louie", "Albert Einstein", "Marie Curie"],
            "date": ["1994-01-06", "1879-03-14", "1867-11-07"],
            "time": ["11:47", "11:30", "12:00"],
            "latitude": [37.3861, 48.4011, 52.2297],
            "longitude": [-122.0839, 9.9876, 21.0122],
        }
    )

    print("1. Input DataFrame:")
    print(df.to_string(index=False))

    # Parse to Natives
    natives = parse_dataframe(df)
    print(f"\n2. Parsed {len(natives)} natives")

    # Calculate charts and extract data
    results = []
    for native in natives:
        chart = ChartBuilder.from_native(native).calculate()
        sun = chart.get_object("Sun")
        moon = chart.get_object("Moon")
        asc = chart.get_object("ASC")

        results.append(
            {
                "name": native.name,
                "sun_sign": sun.sign,
                "sun_degree": round(sun.sign_degree, 1),
                "moon_sign": moon.sign,
                "moon_degree": round(moon.sign_degree, 1),
                "rising_sign": asc.sign if asc else "N/A",
            }
        )

    # Create results DataFrame
    results_df = pd.DataFrame(results)
    print("\n3. Chart calculation results:")
    print(results_df.to_string(index=False))

    # Export to CSV (always works) and Excel (if openpyxl available)
    csv_path = OUTPUT_DIR / "chart_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\n4. Exported to CSV: {csv_path}")

    try:
        import openpyxl  # noqa: F401

        xlsx_path = OUTPUT_DIR / "chart_results.xlsx"
        results_df.to_excel(xlsx_path, index=False)
        print(f"   Exported to Excel: {xlsx_path}")
    except ImportError:
        print("   (Excel export skipped - openpyxl not installed)")


# =============================================================================
# PART 3: AAF PARSING
# =============================================================================


def example_17_aaf_parsing():
    """
    Example 17: AAF File Parsing

    Parse AAF (Astrodienst Astrological Format) files exported from astro.com.
    """
    section_header("Example 17: AAF File Parsing")

    # Create a sample AAF file
    aaf_content = """#: Astrodienst Export File
#A93:Louie,Kate,f,6.1.1994,11:47,Mountain View (Santa Clara County),CA (US)
#B93:2449359.32431,37n23,122w05,8hw00,0
#A93:Einstein,Albert,m,14.3.1879,11:30,Ulm,Germany
#B93:2407851.97917,48n24,9e59,1he00,0
"""
    aaf_path = OUTPUT_DIR / "sample_charts.aaf"
    aaf_path.write_text(aaf_content)
    print(f"Created sample AAF file: {aaf_path}")

    # Parse AAF
    natives = parse_aaf(aaf_path)

    print(f"\nParsed {len(natives)} natives from AAF:")
    for native in natives:
        loc = native.location
        print(f"  - {native.name}")
        print(f"      Date: {native.datetime.utc_datetime.date()}")
        print(f"      Location: {loc.name}")
        print(f"      Coords: ({loc.latitude:.4f}, {loc.longitude:.4f})")

    # Calculate charts
    print("\nChart calculations:")
    for native in natives:
        chart = ChartBuilder.from_native(native).calculate()
        sun = chart.get_object("Sun")
        print(f"  {native.name}: Sun at {sun.sign} {sun.sign_degree:.1f}")


# =============================================================================
# PART 4: BATCH PROCESSING
# =============================================================================


def example_18_batch_chart_generation():
    """
    Example 18: Batch Chart Generation

    Generate multiple charts from imported data.
    """
    section_header("Example 18: Batch Chart Generation")

    csv_content = """name,date,time,latitude,longitude
Kate Louie,1994-01-06,11:47,37.3861,-122.0839
Albert Einstein,1879-03-14,11:30,48.4011,9.9876
Marie Curie,1867-11-07,12:00,52.2297,21.0122
Nikola Tesla,1856-07-10,00:00,44.5636,14.8456
"""
    csv_path = OUTPUT_DIR / "batch_data.csv"
    csv_path.write_text(csv_content)

    natives = parse_csv(csv_path)
    print(f"Loaded {len(natives)} natives from CSV")

    # Generate charts for all
    charts_dir = OUTPUT_DIR / "batch_charts"
    os.makedirs(charts_dir, exist_ok=True)

    print("\nGenerating charts:")
    for native in natives:
        chart = ChartBuilder.from_native(native).with_aspects().calculate()

        # Create safe filename
        safe_name = native.name.replace(" ", "_").lower()
        output_path = charts_dir / f"{safe_name}.svg"

        chart.draw(str(output_path)).preset_standard().save()
        print(f"  Created: {output_path}")

    print(f"\nGenerated {len(natives)} charts in {charts_dir}")


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all cookbook examples."""
    print("\n" + "=" * 70)
    print("  STELLIUM I/O COOKBOOK")
    print("  Examples for Importing and Exporting Birth Data")
    print("=" * 70)

    # CSV Examples
    example_1_csv_auto_detection()
    example_2_csv_custom_columns()
    example_3_csv_split_name()
    example_4_csv_date_formats()
    example_5_csv_12_hour_time()
    example_6_csv_combined_datetime()
    example_7_csv_date_components()
    example_8_csv_location_with_coords()
    example_9_csv_error_handling()
    example_10_csv_column_mapping_object()

    # DataFrame Examples (if pandas available)
    if HAS_PANDAS:
        example_11_dataframe_auto()
        example_12_dataframe_custom()
        example_13_dataframe_from_excel()
        example_14_dataframe_numeric_columns()
        example_15_dataframe_export()
        example_16_dataframe_roundtrip()

    # AAF Examples
    example_17_aaf_parsing()

    # Batch Processing
    example_18_batch_chart_generation()

    # Summary
    section_header("COOKBOOK COMPLETE")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        if f.is_file():
            print(f"  - {f.name}")
        elif f.is_dir():
            print(f"  - {f.name}/ ({len(list(f.iterdir()))} files)")


if __name__ == "__main__":
    main()
