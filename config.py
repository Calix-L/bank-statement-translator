"""Project configuration and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict

from dotenv import load_dotenv


load_dotenv()


def _get_env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw.strip())
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


def _get_env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _default_glossary() -> Dict[str, str]:
    # Keep critical banking terms deterministic before LLM fallback.
    return {
        "转入": "Transfer In",
        "转出": "Transfer Out",
        "收入": "Income",
        "支出": "Expenditure",
        "手续费": "Service Fee",
        "工资": "Salary",
        "交易日期": "Transaction Date",
        "交易时间": "Transaction Time",
        "交易类型": "Transaction Type",
        "交易金额": "Amount",
        "余额": "Balance",
        "对方账户": "Counterparty",
        "对方户名": "Counterparty",
        "摘要": "Description",
    }


@dataclass
class Settings:
    """Runtime settings loaded from environment variables."""

    # 翻译API配置
    api_key: str = field(default_factory=lambda: _get_env_str("ZHIPU_API_KEY", ""))
    model_name: str = field(default_factory=lambda: _get_env_str("ZHIPU_MODEL", "glm-4-flash"))
    api_url: str = field(
        default_factory=lambda: _get_env_str(
            "ZHIPU_API_URL",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        )
    )

    # OCR API配置 (百度AI Studio云端OCR)
    ocr_api_url: str = field(
        default_factory=lambda: _get_env_str(
            "OCR_API_URL",
            "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs",
        )
    )
    ocr_token: str = field(
        default_factory=lambda: _get_env_str(
            "OCR_TOKEN",
            "",  # No default OCR token - must be configured
        )
    )

    # File processing limits
    max_file_size_mb: int = field(default_factory=lambda: _get_env_int("MAX_FILE_SIZE_MB", 10))
    max_pages: int = field(default_factory=lambda: _get_env_int("MAX_PDF_PAGES", 30))
    target_language: str = field(default_factory=lambda: _get_env_str("TARGET_LANGUAGE", "English"))

    # API settings
    request_timeout_sec: int = field(default_factory=lambda: _get_env_int("REQUEST_TIMEOUT_SEC", 30))
    retry_times: int = field(default_factory=lambda: _get_env_int("RETRY_TIMES", 2))
    max_retries: int = field(default_factory=lambda: _get_env_int("MAX_RETRIES", 3))

    # Performance settings
    enable_cache: bool = field(default_factory=lambda: _get_env_bool("ENABLE_CACHE", True))
    cache_dir: str = field(default_factory=lambda: _get_env_str("CACHE_DIR", ".cache"))
    batch_size: int = field(default_factory=lambda: _get_env_int("BATCH_SIZE", 10))

    # Output settings
    include_raw_sheet: bool = field(default_factory=lambda: _get_env_bool("INCLUDE_RAW_SHEET", True))
    output_format: str = field(default_factory=lambda: _get_env_str("OUTPUT_FORMAT", "xlsx"))

    # Logging
    log_level: str = field(default_factory=lambda: _get_env_str("LOG_LEVEL", "INFO"))
    log_file: str = field(default_factory=lambda: _get_env_str("LOG_FILE", ""))

    glossary: Dict[str, str] = field(default_factory=_default_glossary)

    @property
    def zhipu_api_key(self) -> str:
        """Backward-compatible alias used by older entrypoints."""
        return self.api_key


def get_settings() -> Settings:
    return Settings()
