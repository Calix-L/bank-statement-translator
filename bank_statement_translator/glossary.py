"""Central glossary data and helpers for deterministic translation."""

from __future__ import annotations

from typing import Dict, Mapping

from extended_terms import get_all_extended_terms
from terms.garbled_terms import GARBLED_BANK_TERMS, GARBLED_EXACT_TERM_OVERRIDES


BRAND_FIXUPS: Dict[str, str] = {
    "We Chat": "WeChat",
    "Union Pay": "UnionPay",
    "Quick Pass": "QuickPass",
    "Net Bank": "NetBank",
    "e Statement": "e-Statement",
}


READABLE_BANK_TERMS: Dict[str, str] = {
    "工资": "Salary",
    "消费": "Consumption",
    "转账": "Transfer",
    "支付宝": "Alipay",
    "微信支付": "WeChat Pay",
}


READABLE_EXACT_TERM_OVERRIDES: Dict[str, str] = {
    "支付宝（中国）网络技术有限公司": "Alipay (China) Network Technology Co Ltd",
    "网银在线（北京）科技有限公司": "NetBank Online (Beijing) Technology Co Ltd",
    "网银在线(北京)科技有限公司": "NetBank Online (Beijing) Technology Co Ltd",
    "光谷广场地铁C出口便利超市": "Guanggu Plaza Metro C Exit Convenience Store",
    "京东商城业务": "JD Mall Services",
    "汪晶": "Wang Jing",
    "武汉中百便利店": "Wuhan Zhongbai Convenience Store",
    "深圳市财付通支付科技有限公司": "Shenzhen Tenpay Payment Technology Co Ltd",
}


BANK_TERMS: Dict[str, str] = {
    **READABLE_BANK_TERMS,
    **GARBLED_BANK_TERMS,
}

EXACT_TERM_OVERRIDES: Dict[str, str] = {
    **READABLE_EXACT_TERM_OVERRIDES,
    **GARBLED_EXACT_TERM_OVERRIDES,
}


def build_glossary(custom_terms: Mapping[str, str] | None = None) -> Dict[str, str]:
    """Build the complete deterministic glossary used before model fallback."""
    glossary = dict(BANK_TERMS)
    glossary.update(get_all_extended_terms())
    glossary.update(EXACT_TERM_OVERRIDES)
    if custom_terms:
        glossary.update(custom_terms)
    return glossary
