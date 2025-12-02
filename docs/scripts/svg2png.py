import argparse
import sys
from pathlib import Path

# Try to import the converter
try:
    import cairosvg
except ImportError:
    print("❌ Error: 'cairosvg' is not installed.")
    print("Please run: pip install cairosvg")
    sys.exit(1)


def convert_image(input_path: str, scale: float, output_path: str = None):
    """
    Converts an SVG to PNG with a specific scale factor.
    """
    input_file = Path(input_path)

    # Validate input exists
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_path}")
        return

    # Determine output path if not provided
    if output_path:
        output_file = Path(output_path)
    else:
        # Default: image.svg -> image.png
        output_file = input_file.with_suffix(".png")

    print(f"🎨 Converting: {input_file.name}")
    print(f"   Scale: {scale}x")

    try:
        # The conversion magic
        cairosvg.svg2png(url=str(input_file), write_to=str(output_file), scale=scale)
        print(f"✅ Saved to: {output_file}")

    except Exception as e:
        print(f"❌ Conversion failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert SVG to HQ PNG")

    # The file argument
    parser.add_argument("file", help="Path to the SVG file")

    # Optional scale argument (default to 3x for high quality)
    parser.add_argument(
        "--scale",
        "-s",
        type=float,
        default=3.0,
        help="Zoom factor (default: 3.0). Higher = bigger/sharper image.",
    )

    # Optional output argument
    parser.add_argument("--output", "-o", help="Specific output filename (optional)")

    args = parser.parse_args()
    convert_image(args.file, args.scale, args.output)
