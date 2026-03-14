"""Statistics and reporting utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import pandas as pd


@dataclass
class ProcessingStats:
    """Statistics for a processing run."""
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    
    # File counts
    files_processed: int = 0
    files_failed: int = 0
    total_pages: int = 0
    total_transactions: int = 0
    
    # Translation stats
    translation_cache_hits: int = 0
    translation_api_calls: int = 0
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    
    def finish(self) -> None:
        """Mark processing as finished."""
        self.end_time = datetime.now()
    
    @property
    def duration_seconds(self) -> float:
        """Get processing duration in seconds."""
        if self.end_time is None:
            end = datetime.now()
        else:
            end = self.end_time
        return (end - self.start_time).total_seconds()
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        total = self.files_processed + self.files_failed
        if total == 0:
            return 0.0
        return (self.files_processed / total) * 100
    
    @property
    def cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage."""
        total = self.translation_cache_hits + self.translation_api_calls
        if total == 0:
            return 0.0
        return (self.translation_cache_hits / total) * 100
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "files_processed": self.files_processed,
            "files_failed": self.files_failed,
            "success_rate": self.success_rate,
            "total_pages": self.total_pages,
            "total_transactions": self.total_transactions,
            "translation_cache_hits": self.translation_cache_hits,
            "translation_api_calls": self.translation_api_calls,
            "cache_hit_rate": self.cache_hit_rate,
            "errors": self.errors,
        }


def generate_summary(df: pd.DataFrame) -> Dict:
    """Generate summary statistics from transaction dataframe.
    
    Args:
        df: Transaction dataframe
        
    Returns:
        Dictionary of summary statistics
    """
    summary = {
        "total_transactions": len(df),
    }
    
    # Amount statistics if available
    if "收入/支出金额" in df.columns:
        try:
            # Convert to numeric, handling any formatting
            amounts = pd.to_numeric(
                df["收入/支出金额"].astype(str).str.replace(",", ""),
                errors="coerce"
            )
            
            summary["total_income"] = float(amounts[amounts > 0].sum()) if amounts.sum() else 0
            summary["total_expenditure"] = float(amounts[amounts < 0].sum()) if amounts.sum() else 0
            summary["net_change"] = summary["total_income"] + summary["total_expenditure"]
        except Exception:
            pass
    
    # Date range if available
    if "交易日期" in df.columns:
        try:
            dates = pd.to_datetime(df["交易日期"], errors="coerce")
            summary["date_range"] = {
                "start": dates.min().isoformat() if dates.min() else None,
                "end": dates.max().isoformat() if dates.max() else None,
            }
        except Exception:
            pass
    
    return summary


def print_processing_report(stats: ProcessingStats) -> None:
    """Print a formatted processing report.
    
    Args:
        stats: Processing statistics
    """
    print("\n" + "=" * 50)
    print("Processing Report")
    print("=" * 50)
    print(f"Duration: {stats.duration_seconds:.1f} seconds")
    print(f"Files processed: {stats.files_processed}")
    print(f"Files failed: {stats.files_failed}")
    print(f"Success rate: {stats.success_rate:.1f}%")
    print(f"Total pages: {stats.total_pages}")
    print(f"Total transactions: {stats.total_transactions}")
    print(f"Translation API calls: {stats.translation_api_calls}")
    print(f"Cache hits: {stats.translation_cache_hits}")
    print(f"Cache hit rate: {stats.cache_hit_rate:.1f}%")
    
    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for error in stats.errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more")
    
    print("=" * 50)