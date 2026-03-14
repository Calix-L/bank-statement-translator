"""Configuration validator - check environment setup before running."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List

from config import get_settings


@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    passed: bool
    message: str
    is_critical: bool = True


class ConfigValidator:
    """Validate configuration before running the application."""
    
    @staticmethod
    def validate() -> List[ValidationResult]:
        """Run all validation checks.
        
        Returns:
            List of validation results
        """
        results = []
        
        # Check required environment variables
        results.append(ConfigValidator._check_zhipu_api_key())
        results.append(ConfigValidator._check_ocr_token())
        
        # Check optional settings
        results.append(ConfigValidator._check_timeout())
        results.append(ConfigValidator._check_file_limits())
        results.append(ConfigValidator._check_performance_settings())
        results.append(ConfigValidator._check_log_settings())
        
        return results
    
    @staticmethod
    def _check_zhipu_api_key() -> ValidationResult:
        """Check if ZHIPU_API_KEY is configured."""
        settings = get_settings()
        
        if not settings.zhipu_api_key:
            return ValidationResult(
                name="ZHIPU_API_KEY",
                passed=False,
                message="ZHIPU_API_KEY not configured. Translation will not work.",
                is_critical=True,
            )
        
        if len(settings.zhipu_api_key) < 10:
            return ValidationResult(
                name="ZHIPU_API_KEY",
                passed=False,
                message="ZHIPU_API_KEY seems invalid (too short).",
                is_critical=True,
            )
        
        return ValidationResult(
            name="ZHIPU_API_KEY",
            passed=True,
            message="ZHIPU_API_KEY is configured",
            is_critical=True,
        )
    
    @staticmethod
    def _check_ocr_token() -> ValidationResult:
        """Check if OCR_TOKEN is configured."""
        settings = get_settings()
        
        if not settings.ocr_token:
            return ValidationResult(
                name="OCR_TOKEN",
                passed=False,
                message="OCR_TOKEN not configured. Will use PyMuPDF fallback (may lose text in scanned PDFs).",
                is_critical=False,  # Not critical - has fallback
            )
        
        return ValidationResult(
            name="OCR_TOKEN",
            passed=True,
            message="OCR_TOKEN is configured",
            is_critical=False,
        )
    
    @staticmethod
    def _check_timeout() -> ValidationResult:
        """Check if timeout settings are reasonable."""
        settings = get_settings()
        
        if settings.request_timeout_sec < 10:
            return ValidationResult(
                name="REQUEST_TIMEOUT_SEC",
                passed=False,
                message=f"Timeout too short ({settings.request_timeout_sec}s). Recommend >= 30s.",
                is_critical=False,
            )
        
        if settings.request_timeout_sec > 300:
            return ValidationResult(
                name="REQUEST_TIMEOUT_SEC",
                passed=False,
                message=f"Timeout very long ({settings.request_timeout_sec}s). May cause long waits.",
                is_critical=False,
            )
        
        return ValidationResult(
            name="REQUEST_TIMEOUT_SEC",
            passed=True,
            message=f"Timeout set to {settings.request_timeout_sec}s",
            is_critical=False,
        )
    
    @staticmethod
    def _check_file_limits() -> ValidationResult:
        """Check if file size limits are reasonable."""
        settings = get_settings()
        
        if settings.max_file_size_mb < 1:
            return ValidationResult(
                name="MAX_FILE_SIZE_MB",
                passed=False,
                message=f"Max file size too small ({settings.max_file_size_mb}MB).",
                is_critical=False,
            )
        
        if settings.max_pages < 1:
            return ValidationResult(
                name="MAX_PDF_PAGES",
                passed=False,
                message=f"Max pages too small ({settings.max_pages}).",
                is_critical=False,
            )
        
        return ValidationResult(
            name="File Limits",
            passed=True,
            message=f"Max file: {settings.max_file_size_mb}MB, Max pages: {settings.max_pages}",
            is_critical=False,
        )
    
    @staticmethod
    def _check_performance_settings() -> ValidationResult:
        """Check performance-related settings."""
        settings = get_settings()
        
        if settings.batch_size < 1:
            return ValidationResult(
                name="BATCH_SIZE",
                passed=False,
                message=f"Batch size too small ({settings.batch_size}).",
                is_critical=False,
            )
        
        if settings.max_retries < 0:
            return ValidationResult(
                name="MAX_RETRIES",
                passed=False,
                message=f"Max retries cannot be negative ({settings.max_retries}).",
                is_critical=False,
            )
        
        return ValidationResult(
            name="Performance",
            passed=True,
            message=f"Batch: {settings.batch_size}, Retries: {settings.max_retries}, Cache: {settings.enable_cache}",
            is_critical=False,
        )
    
    @staticmethod
    def _check_log_settings() -> ValidationResult:
        """Check logging settings."""
        settings = get_settings()
        
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if settings.log_level.upper() not in valid_levels:
            return ValidationResult(
                name="LOG_LEVEL",
                passed=False,
                message=f"Invalid log level: {settings.log_level}. Must be one of: {valid_levels}",
                is_critical=False,
            )
        
        return ValidationResult(
            name="Logging",
            passed=True,
            message=f"Level: {settings.log_level}, File: {settings.log_file or 'stdout'}",
            is_critical=False,
        )
    
    @staticmethod
    def print_report() -> bool:
        """Print validation report and return True if all critical checks pass.
        
        Returns:
            True if all critical validations pass
        """
        results = ConfigValidator.validate()
        
        print("\n" + "=" * 50)
        print("Configuration Validation Report")
        print("=" * 50)
        
        all_passed = True
        critical_passed = True
        
        for result in results:
            status = "✅" if result.passed else "❌"
            critical_marker = " [CRITICAL]" if result.is_critical else ""
            
            print(f"{status} {result.name}: {result.message}{critical_marker}")
            
            if not result.passed and result.is_critical:
                critical_passed = False
                all_passed = False
            elif not result.passed:
                all_passed = False
        
        print("=" * 50)
        
        if critical_passed:
            print("✅ All critical checks passed! Application can run.")
        else:
            print("❌ Some critical checks failed. Please fix the issues above.")
            print("\nTo configure, create a .env file based on .env.example")
        
        print()
        return critical_passed


def main():
    """CLI entry point for validation."""
    ConfigValidator.print_report()


if __name__ == "__main__":
    main()
