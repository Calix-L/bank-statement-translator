"""Caching utilities for improved performance."""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path
from threading import Lock
from typing import Any, Callable, TypeVar

from config import get_settings


T = TypeVar("T")


class Cache:
    """Simple file-based cache for translation and OCR results."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for different cache types
        self.translation_dir = self.cache_dir / "translations"
        self.ocr_dir = self.cache_dir / "ocr"
        self.parsed_dir = self.cache_dir / "parsed"
        
        for d in [self.translation_dir, self.ocr_dir, self.parsed_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self._metrics_lock = Lock()
        self._translation_hit_count = 0
        self._translation_miss_count = 0
    
    def _get_hash(self, data: str | bytes) -> str:
        """Generate hash key from data."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """Get cache file path."""
        return getattr(self, f"{cache_type}_dir") / f"{key}.pkl"
    
    def get(self, cache_type: str, key: str, track_translation_metrics: bool = False) -> Any | None:
        """Get cached value."""
        settings = get_settings()
        if not settings.enable_cache:
            if track_translation_metrics:
                self._record_translation_miss()
            return None
        
        cache_path = self._get_cache_path(cache_type, key)
        if not cache_path.exists():
            if track_translation_metrics:
                self._record_translation_miss()
            return None
        
        try:
            with open(cache_path, "rb") as f:
                value = pickle.load(f)
                if track_translation_metrics:
                    self._record_translation_hit()
                return value
        except Exception:
            if track_translation_metrics:
                self._record_translation_miss()
            return None
    
    def set(self, cache_type: str, key: str, value: Any) -> None:
        """Set cached value."""
        settings = get_settings()
        if not settings.enable_cache:
            return
        
        cache_path = self._get_cache_path(cache_type, key)
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(value, f)
        except Exception:
            pass
    
    def get_translation(self, text: str) -> str | None:
        """Get cached translation."""
        key = self._get_hash(text)
        return self.get("translation", key, track_translation_metrics=True)
    
    def set_translation(self, text: str, translation: str) -> None:
        """Cache translation."""
        key = self._get_hash(text)
        self.set("translation", key, translation)
    
    def get_ocr(self, pdf_hash: str) -> list | None:
        """Get cached OCR result."""
        return self.get("ocr", pdf_hash)
    
    def set_ocr(self, pdf_hash: str, result: list) -> None:
        """Cache OCR result."""
        self.set("ocr", pdf_hash, result)
    
    def get_parsed(self, text_hash: str) -> list | None:
        """Get cached parsed result."""
        return self.get("parsed", text_hash)
    
    def set_parsed(self, text_hash: str, result: list) -> None:
        """Cache parsed result."""
        self.set("parsed", text_hash, result)
    
    def clear(self, cache_type: str | None = None) -> int:
        """Clear cache. Returns number of files deleted."""
        settings = get_settings()
        if not settings.enable_cache:
            return 0
        
        deleted = 0
        
        if cache_type:
            dirs = [getattr(self, f"{cache_type}_dir")]
        else:
            dirs = [self.translation_dir, self.ocr_dir, self.parsed_dir]
        
        for d in dirs:
            if d.exists():
                for f in d.glob("*.pkl"):
                    try:
                        f.unlink()
                        deleted += 1
                    except Exception:
                        pass
        
        return deleted
    
    def get_size(self) -> int:
        """Get total cache size in bytes."""
        total = 0
        for d in [self.translation_dir, self.ocr_dir, self.parsed_dir]:
            if d.exists():
                for f in d.glob("*.pkl"):
                    try:
                        total += f.stat().st_size
                    except Exception:
                        pass
        return total

    def get_translation_stats(self) -> dict[str, int]:
        """Get translation cache hit/miss counters."""
        with self._metrics_lock:
            return {
                "hit_count": self._translation_hit_count,
                "miss_count": self._translation_miss_count,
            }

    def _record_translation_hit(self) -> None:
        with self._metrics_lock:
            self._translation_hit_count += 1

    def _record_translation_miss(self) -> None:
        with self._metrics_lock:
            self._translation_miss_count += 1


# Global cache instance
_cache: Cache | None = None


def get_cache() -> Cache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        settings = get_settings()
        _cache = Cache(settings.cache_dir)
    return _cache


def cached_translation(func: Callable[[str], T]) -> Callable[[str], T]:
    """Decorator for caching translation results."""
    def wrapper(text: str) -> T:
        cache = get_cache()
        cached = cache.get_translation(text)
        if cached is not None:
            return cached
        
        result = func(text)
        cache.set_translation(text, result)
        return result
    
    return wrapper
