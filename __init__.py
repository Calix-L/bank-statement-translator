"""Bank Statement Translator - Convert Chinese bank PDFs to English PDF and Excel."""

__version__ = "1.0.0"
__author__ = "Calix"
__description__ = "A toolkit for converting Chinese bank statement PDFs to English PDF and Excel"

from cache import Cache, get_cache
from config import get_settings
from config_validator import ConfigValidator
from excel_generator import ExcelGenerator
from exceptions import (
    BankStatementError,
    ConfigurationError,
    OCRError,
    ParseError,
    RateLimitError,
    TranslationError,
    ValidationError,
)
from pdf_parser import PDFParser
from progress import Progress, ProgressBar, Stage
from statement_structurer import StatementStructurer
from translator import StatementTranslator
from word_translator import pdf_to_word, translate_word, word_to_pdf

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__description__",
    # Core
    "get_settings",
    "ConfigValidator",
    "ExcelGenerator",
    "PDFParser",
    "StatementStructurer",
    "StatementTranslator",
    "pdf_to_word",
    "translate_word",
    "word_to_pdf",
    # Cache
    "Cache",
    "get_cache",
    # Progress
    "Progress",
    "ProgressBar",
    "Stage",
    # Exceptions
    "BankStatementError",
    "ConfigurationError",
    "OCRError",
    "ParseError",
    "RateLimitError",
    "TranslationError",
    "ValidationError",
]
