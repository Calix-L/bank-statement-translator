# Bank Statement Translator

[English](README.md) | [简体中文](README.zh-CN.md)

Translate Chinese bank statement PDFs into clean English outputs.

This project focuses on a practical workflow:

- Input: Chinese bank statement PDF
- Output: English PDF with the original layout preserved as closely as possible
- Optional output: structured English Excel workbook

It is intentionally small, local-first, and optimized for real statement translation rather than generic document conversion.

## Current Scope

- Supported bank: Industrial and Commercial Bank of China (ICBC) only
- Primary use case: preparing English bank statements for visa applications
- OCR provider: Baidu PaddleOCR API
- Translation provider: Zhipu GLM API

At the moment, the parsing and dense PDF reconstruction logic are tuned specifically for ICBC statement layouts. Other banks are not officially supported yet.

## Features

- Focused on the real-world visa application workflow where applicants need an English version of a Chinese bank statement
- Rebuilds dense statement pages while keeping stamps, QR codes, and key page assets
- Uses a layered translation strategy: exact overrides, glossary terms, cache, then API
- Includes banking and payment terminology tailored to statement data
- Supports both PDF output and structured Excel export
- Ships with tests for parsing, translation, and Excel generation

## Quick Start

1. Create an environment.
2. Install dependencies.
3. Copy `.env.example` to `.env`.
4. Fill in your API credentials.

```bash
pip install -r requirements.txt
```

Required settings in `.env`:

- `ZHIPU_API_KEY`
- `OCR_TOKEN`

Provider details:

- `OCR_TOKEN` is the access token for the Baidu PaddleOCR API
- `ZHIPU_API_KEY` is used for glossary fallback and long-form translation through Zhipu GLM

Translate a PDF directly:

```bash
python run_word_translator_pipeline.py "input.pdf" -o "output_translated.pdf"
```

If `-o` is omitted, the output defaults to `<input>_translated.pdf`.

## Usage

Run the PDF pipeline:

```bash
python run_word_translator_pipeline.py "statement.pdf"
```

Run the Streamlit UI:

```bash
streamlit run app.py
```

Run the CLI:

```bash
python cli.py --help
```

Run tests:

```bash
pytest tests -v
```

Typical visa-material workflow:

1. Export the original ICBC statement PDF
2. Configure `.env` with Baidu PaddleOCR and Zhipu API credentials
3. Run `python run_word_translator_pipeline.py "statement.pdf"`
4. Review the generated English PDF before submission

## Project Structure

```text
app.py                          Streamlit UI
cli.py                          CLI entry point
run_word_translator_pipeline.py Simplest PDF-to-PDF command
word_translator.py              Translation pipeline orchestration
word_layout.py                  PDF layout and rendering helpers
translator.py                   Text and DataFrame translation logic
glossary.py                     Main glossary builder
terms/                          Banking and payment term dictionaries
pdf_parser.py                   PDF text extraction
statement_structurer.py         Statement row parsing
excel_generator.py              Excel export
tests/                          Test suite
```

## Design Notes

- `word_translator.py` drives the pipeline.
- `word_layout.py` owns page composition and table rendering.
- `translator.py` handles text translation using glossary rules and API fallback.
- `terms/` keeps readable term dictionaries separate from legacy compatibility mappings.

Some compatibility dictionaries still contain historical garbled keys because certain PDFs produce the same mojibake during extraction. Those mappings are isolated on purpose so the readable glossary stays maintainable.

## Development

Helpful local commands:

```bash
make install
make test
make lint
make format
make check
make run
make translate
```

The repository is intentionally minimal. Old Docker files and extra demo scripts were removed to keep the codebase easier to read and maintain.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the local workflow and project conventions.
