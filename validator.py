"""Data validation utilities for processed statements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd


@dataclass
class ValidationIssue:
    """A validation issue found in the data."""
    row: int
    column: str
    severity: str  # "error", "warning", "info"
    message: str


class DataValidator:
    """Validate processed statement data."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.issues: List[ValidationIssue] = []
    
    def validate_all(self) -> List[ValidationIssue]:
        """Run all validation checks.
        
        Returns:
            List of validation issues found
        """
        self.issues = []
        
        self._check_missing_values()
        self._check_date_formats()
        self._check_amount_formats()
        self._check_duplicates()
        self._check_balance_consistency()
        
        return self.issues
    
    def _check_missing_values(self) -> None:
        """Check for missing critical values."""
        critical_columns = ["交易日期", "摘要"]
        
        for col in critical_columns:
            if col in self.df.columns:
                missing = self.df[col].isna() | (self.df[col].astype(str).str.strip() == "")
                if missing.any():
                    for idx in self.df[missing].index:
                        self.issues.append(ValidationIssue(
                            row=idx,
                            column=col,
                            severity="warning",
                            message=f"Missing value in {col}"
                        ))
    
    def _check_date_formats(self) -> None:
        """Check date column formats."""
        if "交易日期" not in self.df.columns:
            return
        
        dates = pd.to_datetime(self.df["交易日期"], errors="coerce")
        invalid = dates.isna() & ~self.df["交易日期"].isna()
        
        if invalid.any():
            for idx in self.df[invalid].index:
                self.issues.append(ValidationIssue(
                    row=idx,
                    column="交易日期",
                    severity="error",
                    message=f"Invalid date format: {self.df.loc[idx, '交易日期']}"
                ))
    
    def _check_amount_formats(self) -> None:
        """Check amount column formats."""
        amount_columns = ["收入/支出金额", "余额"]
        
        for col in amount_columns:
            if col not in self.df.columns:
                continue
            
            # Try to convert to numeric
            amounts = pd.to_numeric(
                self.df[col].astype(str).str.replace(",", ""),
                errors="coerce"
            )
            
            invalid = amounts.isna() & ~self.df[col].isna() & (self.df[col].astype(str).str.strip() != "")
            
            if invalid.any():
                for idx in self.df[invalid].index:
                    self.issues.append(ValidationIssue(
                        row=idx,
                        column=col,
                        severity="error",
                        message=f"Invalid amount format: {self.df.loc[idx, col]}"
                    ))
    
    def _check_duplicates(self) -> None:
        """Check for duplicate transactions."""
        if "交易日期" not in self.df.columns or "收入/支出金额" not in self.df.columns:
            return
        
        # Look for exact duplicates
        duplicates = self.df.duplicated(subset=["交易日期", "收入/支出金额"], keep=False)
        
        if duplicates.any():
            for idx in self.df[duplicates].index:
                self.issues.append(ValidationIssue(
                    row=idx,
                    column="",
                    severity="info",
                    message="Possible duplicate transaction"
                ))
    
    def _check_balance_consistency(self) -> None:
        """Check if running balance is consistent."""
        if "余额" not in self.df.columns or "收入/支出金额" not in self.df.columns:
            return
        
        try:
            amounts = pd.to_numeric(
                self.df["收入/支出金额"].astype(str).str.replace(",", ""),
                errors="coerce"
            ).fillna(0)
            
            balances = pd.to_numeric(
                self.df["余额"].astype(str).str.replace(",", ""),
                errors="coerce"
            )
            
            # Calculate expected balance
            running = balances.iloc[0] - amounts.cumsum()
            running = running.shift(1).fillna(balances.iloc[0])
            
            # Check if balances match (with small tolerance for rounding)
            diff = abs(balances - running)
            inconsistent = (diff > 0.01) & ~balances.isna() & ~running.isna()
            
            if inconsistent.any():
                for idx in self.df[inconsistent].index:
                    self.issues.append(ValidationIssue(
                        row=idx,
                        column="余额",
                        severity="warning",
                        message=f"Balance inconsistency detected (expected {running.iloc[idx]:.2f})"
                    ))
        except Exception:
            pass  # Skip if calculation fails
    
    def get_summary(self) -> dict:
        """Get validation summary."""
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        infos = [i for i in self.issues if i.severity == "info"]
        
        return {
            "total_issues": len(self.issues),
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "is_valid": len(errors) == 0,
        }


def validate_dataframe(df: pd.DataFrame) -> dict:
    """Quick validation of a dataframe.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Validation summary dict
    """
    validator = DataValidator(df)
    validator.validate_all()
    return validator.get_summary()
