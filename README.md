# 🏦 Bank Statement Translator

[English](README.md) | [简体中文](README.zh-CN.md)

Translate Chinese bank statement PDFs into clean English outputs — perfect for visa applications and international financial workflows.

---

## Overview

A local-first Python toolkit that converts Chinese bank statement PDFs into polished English documents while preserving the original layout as closely as possible.

- **Input**: Chinese bank statement PDF (ICBC supported)
- **Output**: English PDF (layout-preserved) or structured Excel

This project focuses on real-world statement translation, optimized specifically for banking documents rather than generic PDF conversion.

### Current Scope

- **Supported Bank**: Industrial and Commercial Bank of China (ICBC) only
- **Primary Use Case**: Visa application preparation
- **OCR Provider**: Baidu PaddleOCR API
- **Translation Provider**: Zhipu GLM API

---

## Features

- 🎨 **Layout Preservation** — Keeps stamps, QR codes, tables, and formatting
- 🔍 **Smart OCR** — Baidu PaddleOCR for scanned documents
- 📦 **Dual Output** — Both PDF and Excel formats
- 💾 **Caching** — Built-in translation cache for faster repeated processing
- ⚡ **Rate Limiting** — Smart API rate limiting to prevent throttling
- ✅ **Well Tested** — Comprehensive test suite

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with:
#   - ZHIPU_API_KEY (from https://open.bigmodel.cn/)
#   - OCR_TOKEN (from https://aistudio.baidu.com/)

# 3. Translate a PDF
python run_word_translator_pipeline.py "statement.pdf" -o "statement_en.pdf"
```

---

## Usage

```bash
# PDF translation
python run_word_translator_pipeline.py "input.pdf" -o "output.pdf"

# Streamlit UI
streamlit run app.py

# CLI
python cli.py --help

# Run tests
pytest tests -v
```

---

## Project Structure

```
app.py                          Streamlit UI
cli.py                          CLI entry point
run_word_translator_pipeline.py Simplest PDF-to-PDF command
word_translator.py              Translation pipeline orchestration
word_layout.py                  PDF layout and rendering helpers
translator.py                   Text and DataFrame translation logic
glossary.py                     Main glossary builder
terms/                          Banking and payment term dictionaries
    banking_terms.py           # Banking terminology
    payment_terms.py           # Payment platforms
    readable_terms.py          # Readability improvements
    garbled_terms.py          # OCR garble mappings
pdf_parser.py                   PDF text extraction
statement_structurer.py         Statement row parsing
excel_generator.py              Excel export
config.py                       Configuration
cache.py                        Translation caching
rate_limiter.py                 API rate limiting
tests/                          Test suite
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZHIPU_API_KEY` | ✅ | Zhipu GLM API key |
| `OCR_TOKEN` | ✅ | Baidu PaddleOCR token |
| `ZHIPU_MODEL` | ❌ | Model (default: glm-4-flash) |
| `TARGET_LANGUAGE` | ❌ | Target language (default: English) |
| `ENABLE_CACHE` | ❌ | Enable caching (default: true) |

---

## Development

```bash
make install    # Install dependencies
make test       # Run tests
make lint       # Lint code
make format     # Format code
make check      # Full check
make run        # Run Streamlit
make translate  # Quick translate
make clean      # Clean temp files
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
