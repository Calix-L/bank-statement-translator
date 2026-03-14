"""CLI entry point for bank statement translator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import get_settings
from config_validator import ConfigValidator
from excel_generator import ExcelGenerator
from logger import setup_logger
from pdf_parser import PDFParser
from statement_structurer import StatementStructurer
from translator import StatementTranslator


logger = setup_logger("bank_statement_translator.cli")


def validate_config() -> bool:
    """Validate configuration before running."""
    return ConfigValidator.print_report()


def _build_services() -> tuple[PDFParser, StatementTranslator]:
    settings = get_settings()
    return PDFParser(settings), StatementTranslator(settings)


def _process_pdf(
    pdf_path: Path,
    parser: PDFParser,
    translator: StatementTranslator,
):
    """Parse and translate a single PDF into raw and translated dataframes."""
    pdf_bytes = pdf_path.read_bytes()
    ok, message = parser.validate_pdf(pdf_bytes)
    if not ok:
        return None, None, message

    page_texts = parser.extract_text_by_page(pdf_bytes)
    rows = StatementStructurer.parse(page_texts)
    if not rows:
        return None, None, "No transactions found in PDF"

    raw_df = StatementStructurer.to_dataframe(rows)
    translated_df = translator.translate_dataframe(raw_df)
    return raw_df, translated_df, None


def process_single_file(
    pdf_path: Path,
    output_path: Path | None = None,
    include_raw: bool = True,
) -> bool:
    """Process a single PDF file."""
    parser, translator = _build_services()

    print(f"Reading {pdf_path}...")
    print("Validating, parsing, and translating...")
    raw_df, translated_df, error = _process_pdf(pdf_path, parser, translator)
    if error:
        print(f"Error: {error}")
        return False

    print(f"  Found {len(raw_df)} transactions")
    print("Generating Excel...")
    excel_bytes = ExcelGenerator.generate(translated_df, raw_df if include_raw else None)

    final_output = output_path or pdf_path.with_suffix(".xlsx")
    final_output.write_bytes(excel_bytes)
    print(f"Saved to {final_output}")
    return True


def process_batch(
    pdf_files: list[Path],
    output_dir: Path | None = None,
) -> bool:
    """Process multiple PDF files."""
    parser, translator = _build_services()
    final_output_dir = output_dir or Path(".")
    final_output_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, bool]] = []

    for index, pdf_path in enumerate(pdf_files, start=1):
        print(f"\n[{index}/{len(pdf_files)}] Processing {pdf_path.name}...")
        try:
            raw_df, translated_df, error = _process_pdf(pdf_path, parser, translator)
            if error:
                print(f"  Error: {error}")
                results.append((pdf_path.name, False))
                continue

            output_path = final_output_dir / f"{pdf_path.stem}_translated.xlsx"
            excel_bytes = ExcelGenerator.generate(translated_df, raw_df)
            output_path.write_bytes(excel_bytes)
            print(f"  OK: {len(raw_df)} transactions -> {output_path.name}")
            results.append((pdf_path.name, True))
        except Exception as exc:
            print(f"  Error: {exc}")
            results.append((pdf_path.name, False))

    print("\n" + "=" * 50)
    print("Batch Processing Summary")
    print("=" * 50)

    successful = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print(f"{'OK' if ok else 'FAILED'} {name}")

    print(f"\nTotal: {successful}/{len(results)} files processed successfully")
    return successful == len(results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bank Statement Translator - Convert Chinese bank PDFs to English Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m bank_statement_translator validate
  python -m bank_statement_translator process statement.pdf
  python -m bank_statement_translator process statement.pdf -o output.xlsx
  python -m bank_statement_translator batch file1.pdf file2.pdf file3.pdf
  python -m bank_statement_translator batch *.pdf
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("validate", help="Validate configuration")

    process_parser = subparsers.add_parser("process", help="Process a single PDF file")
    process_parser.add_argument("input", type=Path, help="Input PDF file")
    process_parser.add_argument("-o", "--output", type=Path, help="Output Excel file")
    process_parser.add_argument("--no-raw", action="store_true", help="Exclude raw data sheet")

    batch_parser = subparsers.add_parser("batch", help="Process multiple PDF files")
    batch_parser.add_argument("inputs", type=Path, nargs="+", help="Input PDF files")
    batch_parser.add_argument("-o", "--output-dir", type=Path, help="Output directory")
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1
    if args.command == "validate":
        return 0 if validate_config() else 1
    if args.command == "process":
        success = process_single_file(args.input, args.output, include_raw=not args.no_raw)
        return 0 if success else 1
    if args.command == "batch":
        return 0 if process_batch(args.inputs, args.output_dir) else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
