"""Translation module for bank statements with deterministic glossary fallback."""

from __future__ import annotations

import re
import time
from typing import Dict, Iterable

import pandas as pd
import requests

from cache import get_cache
from config import Settings
from glossary import BANK_TERMS, BRAND_FIXUPS, build_glossary
from logger import get_logger


logger = get_logger(__name__)

TRANSLATABLE_COLUMNS = (
    "鎽樿",
    "鍦板尯",
    "瀵规柟鎴峰悕",
    "瀵规柟璐﹀彿",
    "娓犻亾",
    "鍌ㄧ",
    "甯佺",
    "閽炴眹",
)

CHINESE_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
CHINESE_BLOCK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
WHITESPACE_RE = re.compile(r"\s+")
TEXT_REPLACEMENTS = (
    ("\u3000", " "),
    ("锛?", "("),
    ("锛?", ")"),
    ("锛?", ","),
    ("锛?", ":"),
    ("锛?", ";"),
    ("銆?", "."),
    ("銆?", "/"),
    ("鈥?", '"'),
    ("鈥?", '"'),
    ("鈥?", "'"),
    ("鈥?", "'"),
)


class StatementTranslator:
    """Translate bank statement fields and remove all Chinese characters."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.cache: Dict[str, str] = {}
        self._session = requests.Session()
        self._glossary = build_glossary(settings.glossary)
        self._phrase_glossary = dict(
            sorted(self._glossary.items(), key=lambda item: len(item[0]), reverse=True)
        )

    def translate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        out = df.copy()
        for column in TRANSLATABLE_COLUMNS:
            if column not in out.columns:
                continue

            series = out[column].fillna("").astype(str)
            mapping = self._build_translation_map(series.unique().tolist())
            out[column] = series.map(lambda value: mapping.get(value, self._finalize_text(value)))
            out[column] = out[column].map(self._finalize_text)

        return out

    def translate_text(self, text: str) -> str:
        normalized = self._normalize_text(text)
        if not normalized:
            return ""
        return self._finalize_text(self._translate_text(normalized))

    def _build_translation_map(self, texts: Iterable[str]) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for original in texts:
            normalized = self._normalize_text(original)
            if not normalized:
                mapping[original] = ""
                continue

            if normalized not in self.cache:
                self.cache[normalized] = self._finalize_text(self._translate_text(normalized))
            mapping[original] = self.cache[normalized]

        return mapping

    def _translate_text(self, text: str) -> str:
        exact_match = self._glossary.get(text)
        if exact_match is not None:
            get_cache().set_translation(text, exact_match)
            return exact_match

        cache = get_cache()
        cached = cache.get_translation(text)
        if cached is not None:
            logger.debug("Cache hit for: %s...", text[:30])
            return cached

        replaced = self._replace_known_terms(text)
        if not self._contains_chinese(replaced):
            cache.set_translation(text, replaced)
            return replaced

        translated = self._call_glm_strict(replaced)
        translated = self._replace_known_terms(translated)

        if self._contains_chinese(translated):
            translated = self._translate_residual_blocks(translated)
        if self._contains_chinese(translated):
            translated = self._strip_or_mark_residual(translated)

        cache.set_translation(text, translated)
        return translated

    def _replace_known_terms(self, text: str) -> str:
        replaced = self._normalize_text(text)
        exact_match = self._glossary.get(replaced)
        if exact_match is not None:
            return exact_match

        for source, target in self._phrase_glossary.items():
            if source and source in replaced:
                replaced = replaced.replace(source, target)

        return self._normalize_spacing(replaced)

    def _translate_residual_blocks(self, text: str) -> str:
        result = text
        blocks = sorted(set(CHINESE_BLOCK_RE.findall(text)), key=len, reverse=True)
        for block in blocks:
            if not block.strip():
                continue
            translated = self._call_glm_strict(block)
            translated = self._replace_known_terms(translated)
            translated = self._strip_or_mark_residual(translated)
            result = result.replace(block, translated)
        return result

    def _strip_or_mark_residual(self, text: str) -> str:
        if not text:
            return text

        replaced = self._replace_known_terms(text)
        if not self._contains_chinese(replaced):
            return replaced

        sanitized = self._normalize_spacing(CHINESE_BLOCK_RE.sub(" ", replaced))
        if sanitized and sanitized != "[Untranslated]":
            return sanitized

        cleaned = "".join(
            char if ord(char) < 128 or char in " ,.()[]{}" else " "
            for char in replaced
        )
        cleaned = self._normalize_spacing(cleaned)
        return cleaned if cleaned else ""

    def _finalize_text(self, text: str) -> str:
        cleaned = self._replace_known_terms(self._normalize_text(text))
        if self._contains_chinese(cleaned):
            cleaned = self._translate_residual_blocks(cleaned)
        if self._contains_chinese(cleaned):
            cleaned = self._strip_or_mark_residual(cleaned)
        return self._normalize_spacing(cleaned)

    def _normalize_text(self, text: object) -> str:
        if text is None:
            return ""

        value = str(text).strip()
        if not value:
            return ""

        for source, target in TEXT_REPLACEMENTS:
            value = value.replace(source, target)
        return self._normalize_spacing(value)

    def _normalize_spacing(self, text: str) -> str:
        text = WHITESPACE_RE.sub(" ", text).strip()
        text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
        text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", text)
        text = re.sub(r"\s+([,;:/)])", r"\1", text)
        text = re.sub(r"([(])\s+", r"\1", text)
        text = text.strip("[]{}\"'")
        for source, target in BRAND_FIXUPS.items():
            text = text.replace(source, target)
        return text

    def _contains_chinese(self, text: str) -> bool:
        return bool(CHINESE_RE.search(text))

    def _call_glm_strict(self, text: str) -> str:
        if not text or not self.settings.api_key:
            return text

        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Translate the user text into concise natural English for a bank statement. "
                        "Return only English text. Never output Chinese characters. "
                        "Preserve numbers, masked account numbers, dates, and merchant identity."
                    ),
                },
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,
        }

        for attempt in range(3):
            try:
                response = self._session.post(
                    self.settings.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.settings.request_timeout_sec,
                )
                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue

                response.raise_for_status()
                content = self._extract_response_text(response)
                if content:
                    cleaned = self._normalize_spacing(content)
                    if cleaned:
                        return cleaned
            except Exception:
                pass

            if attempt < 2:
                time.sleep(1)

        return text

    @staticmethod
    def _extract_response_text(response: requests.Response) -> str:
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return str(message.get("content", "")).strip()
