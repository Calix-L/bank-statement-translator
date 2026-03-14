import argparse
from pathlib import Path

from word_translator import translate_pdf_in_place


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate Chinese text in a PDF while preserving the original page appearance.",
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF file path. Defaults to <input>_translated.pdf",
    )
    args = parser.parse_args()

    input_pdf = args.input_pdf
    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")

    output_pdf = args.output or input_pdf.with_name(f"{input_pdf.stem}_translated.pdf")

    translate_pdf_in_place(str(input_pdf), str(output_pdf))
    print(f"Generated: {output_pdf}")


if __name__ == "__main__":
    main()
