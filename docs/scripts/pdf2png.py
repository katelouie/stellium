import argparse
import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError
except ImportError:
    print("❌ Error: 'pdf2image' is not installed.")
    print("Please run: pip install pdf2image")
    sys.exit(1)


def convert_pdf(input_path: str, dpi: int = 300, output_dir: str = None):
    """
    Converts a PDF to a series of PNG images.
    """
    input_file = Path(input_path)

    # 1. Validation
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_path}")
        return

    # 2. Setup Output Directory
    if output_dir:
        out_path = Path(output_dir)
    else:
        # Default: Create a folder named after the PDF (e.g., "chart_report_images/")
        out_path = input_file.parent / f"{input_file.stem}_images"

    out_path.mkdir(parents=True, exist_ok=True)

    print(f"📄 Processing: {input_file.name}")
    print(f"✨ Quality: {dpi} DPI")
    print(f"📂 Output: {out_path}")

    try:
        # 3. The Conversion
        # fmt="png" speeds up the process slightly by not converting to ppm first
        images = convert_from_path(str(input_file), dpi=dpi, fmt="png")

        # 4. Save Images
        for i, image in enumerate(images):
            # Naming: originalname_page_1.png
            page_num = i + 1
            filename = f"{input_file.stem}_page_{page_num}.png"
            save_path = out_path / filename

            image.save(save_path, "PNG")
            print(f"   ✅ Saved Page {page_num}: {filename}")

        print(f"\n🚀 Done! {len(images)} images saved to: {out_path}")

    except PDFInfoNotInstalledError:
        print("\n❌ Error: Poppler is not installed or not in PATH.")
        print("   'pdf2image' requires the poppler system library.")
        print("   -> Mac: brew install poppler")
        print("   -> Windows: Download binary, extract, add 'bin' to PATH.")
        print("   -> Linux: sudo apt-get install poppler-utils")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF pages to HQ PNG images")

    parser.add_argument("file", help="Path to the PDF file")

    parser.add_argument(
        "--dpi",
        "-d",
        type=int,
        default=300,
        help="DPI resolution (default: 300). Use 600 for ultra-high quality.",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output directory (optional). Defaults to a new folder named after the PDF.",
    )

    args = parser.parse_args()
    convert_pdf(args.file, args.dpi, args.output)
