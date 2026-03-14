"""Bank statement parser adapters for different bank formats."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseParser(ABC):
    """Abstract base class for bank statement parsers."""
    
    @property
    @abstractmethod
    def bank_name(self) -> str:
        """Return the bank name this parser supports."""
        pass
    
    @property
    @abstractmethod
    def header_columns(self) -> List[str]:
        """Return the column order for this bank's statement format."""
        pass
    
    @abstractmethod
    def parse(self, page_texts: List[str]) -> List[Dict[str, str]]:
        """Parse the extracted text into structured rows.
        
        Args:
            page_texts: List of text content from each PDF page
            
        Returns:
            List of dictionaries containing transaction data
        """
        pass
    
    def detect(self, sample_text: str) -> float:
        """Detect if this parser matches the given statement format.
        
        Args:
            sample_text: Sample text from the statement
            
        Returns:
            Confidence score (0.0 to 1.0) indicating match probability
        """
        return 0.0


class ICBCParser(BaseParser):
    """Parser for Industrial and Commercial Bank of China (ICBC) statements."""
    
    @property
    def bank_name(self) -> str:
        return "Industrial and Commercial Bank of China (ICBC)"
    
    @property
    def header_columns(self) -> List[str]:
        return [
            "交易日期", "账号", "储种", "序号", "币种", "钞汇",
            "摘要", "地区", "收入/支出金额", "余额", "对方户名", "对方账号", "渠道"
        ]
    
    def parse(self, page_texts: List[str]) -> List[Dict[str, str]]:
        # Import here to avoid circular imports
        from statement_structurer import StatementStructurer
        return StatementStructurer.parse(page_texts)
    
    def detect(self, sample_text: str) -> float:
        """Detect ICBC statement format based on keywords."""
        score = 0.0
        icbc_keywords = ["中国工商银行", "工商银行", "ICBC", "牡丹卡", "e时代"]
        for keyword in icbc_keywords:
            if keyword in sample_text:
                score += 0.2
        return min(score, 1.0)


class BOCParser(BaseParser):
    """Parser for Bank of China statements."""
    
    @property
    def bank_name(self) -> str:
        return "Bank of China (BOC)"
    
    @property
    def header_columns(self) -> List[str]:
        return [
            "交易日期", "交易时间", "交易类型", "支出", "存入", "余额", 
            "对方账户", "对方姓名", "备注"
        ]
    
    def parse(self, page_texts: List[str]) -> List[Dict[str, str]]:
        # TODO: Implement BOC-specific parsing
        # For now, return empty list as placeholder
        return []
    
    def detect(self, sample_text: str) -> float:
        """Detect BOC statement format."""
        score = 0.0
        boc_keywords = ["中国银行", "BOC", "长城卡", "中银卡"]
        for keyword in boc_keywords:
            if keyword in sample_text:
                score += 0.25
        return min(score, 1.0)


class ABCParser(BaseParser):
    """Parser for Agricultural Bank of China statements."""
    
    @property
    def bank_name(self) -> str:
        return "Agricultural Bank of China (ABC)"
    
    @property
    def header_columns(self) -> List[str]:
        return [
            "交易日期", "交易时间", "交易金额", "账户余额", 
            "对方账户", "对方姓名", "交易渠道", "交易类型"
        ]
    
    def parse(self, page_texts: List[str]) -> List[Dict[str, str]]:
        # TODO: Implement ABC-specific parsing
        return []
    
    def detect(self, sample_text: str) -> float:
        """Detect ABC statement format."""
        score = 0.0
        abc_keywords = ["中国农业银行", "农业银行", "ABC", "金穗卡"]
        for keyword in abc_keywords:
            if keyword in sample_text:
                score += 0.25
        return min(score, 1.0)


class CCBParser(BaseParser):
    """Parser for China Construction Bank statements."""
    
    @property
    def bank_name(self) -> str:
        return "China Construction Bank (CCB)"
    
    @property
    def header_columns(self) -> List[str]:
        return [
            "交易日期", "交易时间", "交易金额", "余额", 
            "对方账户", "对方姓名", "渠道", "种类"
        ]
    
    def parse(self, page_texts: List[str]) -> List[Dict[str, str]]:
        # TODO: Implement CCB-specific parsing
        return []
    
    def detect(self, sample_text: str) -> float:
        """Detect CCB statement format."""
        score = 0.0
        ccb_keywords = ["中国建设银行", "建设银行", "CCB", "龙卡"]
        for keyword in ccb_keywords:
            if keyword in sample_text:
                score += 0.25
        return min(score, 1.0)


# Registry of all available parsers
PARSERS: list[BaseParser] = [
    ICBCParser(),
    BOCParser(),
    ABCParser(),
    CCBParser(),
]


def detect_bank(sample_text: str) -> tuple[str, float]:
    """Detect which bank's statement format matches the sample text.
    
    Args:
        sample_text: Sample text from the statement
        
    Returns:
        Tuple of (bank_name, confidence_score)
    """
    best_match = ("Unknown", 0.0)
    
    for parser in PARSERS:
        score = parser.detect(sample_text)
        if score > best_match[1]:
            best_match = (parser.bank_name, score)
    
    return best_match


def get_parser(bank_name: str | None = None) -> BaseParser:
    """Get a parser instance for the specified bank or auto-detect.
    
    Args:
        bank_name: Optional bank name to get specific parser
        
    Returns:
        Parser instance
    """
    if bank_name:
        for parser in PARSERS:
            if bank_name.lower() in parser.bank_name.lower():
                return parser
    
    # Default to ICBC parser
    return ICBCParser()
