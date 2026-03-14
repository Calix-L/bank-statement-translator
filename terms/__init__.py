"""Structured term dictionaries for bank statement translation."""

from __future__ import annotations

from typing import Dict

from .banking_terms import BANKING_GLOSSARY_TERMS, EXTENDED_BANK_TERMS
from .garbled_terms import GARBLED_BANK_TERMS, GARBLED_EXACT_TERM_OVERRIDES
from .payment_terms import PAYMENT_CHANNEL_TERMS, PAYMENT_INSTITUTION_TERMS, PAYMENT_TERMS
from .readable_terms import (
    READABLE_BANKING_GLOSSARY_TERMS,
    READABLE_PAYMENT_CHANNEL_TERMS,
    READABLE_PAYMENT_INSTITUTION_TERMS,
)

READABLE_TERM_ALIASES: Dict[str, str] = {
    "交易明细": "Transaction Details",
    "电子回单": "Electronic Receipt",
    "手机银行": "Mobile Banking",
    "跨行转账": "Interbank Transfer",
    "收款人": "Payee",
    "电子结单": "e-Statement",
    "购汇": "FX Purchase",
    "授信额度": "Credit Line",
    "结算": "Settlement",
    "冲正": "Reversal",
    "批量代发": "Bulk Payroll",
    "待入账": "Pending Posting",
    "支付宝（中国）网络技术有限公司": "Alipay (China) Network Technology Co Ltd",
    "深圳市财付通支付科技有限公司": "Shenzhen Tenpay Payment Technology Co Ltd",
    "网银在线（北京）科技有限公司": "NetBank Online (Beijing) Technology Co Ltd",
    "京东支付": "JD Pay",
    "拉卡拉支付股份有限公司": "Lakala Payment Corporation",
}


def get_all_extended_terms() -> Dict[str, str]:
    """Get all extended terms combined."""
    combined = READABLE_PAYMENT_INSTITUTION_TERMS.copy()
    combined.update(READABLE_PAYMENT_CHANNEL_TERMS)
    combined.update(READABLE_BANKING_GLOSSARY_TERMS)
    combined.update(PAYMENT_INSTITUTION_TERMS)
    combined.update(PAYMENT_CHANNEL_TERMS)
    combined.update(BANKING_GLOSSARY_TERMS)
    combined.update(EXTENDED_BANK_TERMS)
    combined.update(PAYMENT_TERMS)
    combined.update(READABLE_TERM_ALIASES)
    return combined


__all__ = [
    "BANKING_GLOSSARY_TERMS",
    "EXTENDED_BANK_TERMS",
    "GARBLED_BANK_TERMS",
    "GARBLED_EXACT_TERM_OVERRIDES",
    "READABLE_BANKING_GLOSSARY_TERMS",
    "READABLE_PAYMENT_CHANNEL_TERMS",
    "READABLE_PAYMENT_INSTITUTION_TERMS",
    "PAYMENT_CHANNEL_TERMS",
    "PAYMENT_INSTITUTION_TERMS",
    "PAYMENT_TERMS",
    "READABLE_TERM_ALIASES",
    "get_all_extended_terms",
]
