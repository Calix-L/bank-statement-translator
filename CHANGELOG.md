# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Batch processing support for multiple PDF files
- CLI interface (`python -m bank_statement_translator`)
- Configuration validator (`config_validator.py`)
- Makefile for common development tasks
- GitHub Actions CI workflow
- Extended banking terminology dictionary
- Bank format adapter framework (ICBC, BOC, ABC, CCB)
- Progress bar for Streamlit UI
- Logging system with configurable levels

### Changed
- Removed hardcoded API keys (now requires .env configuration)
- Improved error handling and logging
- Better Streamlit sidebar with config status
- Refined glossary structure with readable terms and compatibility mappings
- Split PDF layout logic from translation orchestration
- Simplified repository structure and developer workflow

### Fixed
- Various bug fixes and improvements

## [1.0.0] - 2026-03-14

### Added
- Initial release
- PDF text extraction (PyMuPDF + cloud OCR fallback)
- Bank statement parsing (ICBC format)
- Translation using Zhipu GLM API
- Excel export with translated and raw sheets
- Streamlit web interface

### Features
- Support for Chinese bank statements
- Translation of transaction descriptions, regions, counterparties
- Configurable via environment variables
- Batch processing support
- Multiple output format support
