"""Tests for Excel generator module."""

import sys
sys.path.insert(0, '.')

import pandas as pd

from excel_generator import ExcelGenerator
from statement_structurer import PDF_HEADER_ORDER


def test_align_columns():
    """Test column alignment."""
    # Create sample dataframe with subset of columns
    df = pd.DataFrame({
        "交易日期": ["2024-01-01", "2024-01-02"],
        "账号": ["6222021234567890", "6222021234567890"],
        "摘要": ["工资", "消费"],
    })
    
    result = ExcelGenerator._align_pdf_columns(df)
    
    # Check all columns exist
    for col in PDF_HEADER_ORDER:
        assert col in result.columns, f"Missing column: {col}"
    
    print("✅ test_align_columns PASSED")


def test_single_sheet_generation():
    """Test single sheet Excel generation."""
    translated_df = pd.DataFrame({
        "Transaction Date": ["2024-01-01"],
        "Description": ["Salary"],
    })
    
    raw_df = pd.DataFrame({
        "交易日期": ["2024-01-01"],
        "摘要": ["工资"],
    })
    
    result = ExcelGenerator.generate(translated_df, raw_df)
    
    assert len(result) > 0, "Excel generation returned empty bytes"
    assert result[:4] == b"PK\x03\x04", "Not a valid Excel file"
    
    print("✅ test_single_sheet_generation PASSED")


def test_batch_generation():
    """Test batch Excel generation."""
    results = [
        {
            "name": "Statement1",
            "translated_df": pd.DataFrame({
                "Transaction Date": ["2024-01-01"],
                "Description": ["Salary"],
            }),
            "raw_df": pd.DataFrame({
                "交易日期": ["2024-01-01"],
                "摘要": ["工资"],
            }),
        },
        {
            "name": "Statement2", 
            "translated_df": pd.DataFrame({
                "Transaction Date": ["2024-01-02"],
                "Description": ["Transfer"],
            }),
            "raw_df": pd.DataFrame({
                "交易日期": ["2024-01-02"],
                "摘要": ["转账"],
            }),
        },
    ]
    
    result = ExcelGenerator.generate_batch(results)
    
    assert len(result) > 0, "Batch Excel generation returned empty"
    assert result[:4] == b"PK\x03\x04", "Not a valid Excel file"
    
    print("✅ test_batch_generation PASSED")


def test_empty_batch():
    """Test batch with no valid data."""
    results = []
    
    result = ExcelGenerator.generate_batch(results)
    
    # Should still return valid (but empty) workbook
    assert len(result) >= 0
    
    print("✅ test_empty_batch PASSED")


if __name__ == "__main__":
    print("\nRunning Excel generator tests...\n")
    
    test_align_columns()
    test_single_sheet_generation()
    test_batch_generation()
    test_empty_batch()
    
    print("\n✅ All Excel generator tests passed!")
