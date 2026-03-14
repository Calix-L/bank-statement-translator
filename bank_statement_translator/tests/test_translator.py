"""Tests for translator module."""

import sys

sys.path.insert(0, ".")

import pandas as pd

from config import get_settings
from extended_terms import get_all_extended_terms
from translator import CHINESE_RE, TRANSLATABLE_COLUMNS, StatementTranslator


def test_term_lookup():
    """Test deterministic glossary hits for core banking terms."""
    translator = StatementTranslator(get_settings())

    test_cases = {
        "工资": "Salary",
        "消费": "Consumption",
        "转账": "Transfer",
        "利息": "Interest",
        "支付宝": "Alipay",
        "微信支付": "WeChat Pay",
        "短信验证码": "SMS Verification Code",
        "双因素认证": "Two-Factor Authentication",
    }

    for source, expected in test_cases.items():
        assert translator.translate_text(source) == expected


def test_chinese_detection():
    """Test Chinese text detection."""
    test_cases = [
        ("工资", True),
        ("Salary", False),
        ("工资转账", True),
        ("2024-01-01", False),
        ("", False),
    ]

    for text, expected in test_cases:
        assert bool(CHINESE_RE.search(text)) == expected


def test_extended_glossary_terms():
    """Test that extended banking glossary terms are available."""
    translator = StatementTranslator(get_settings())
    extended_terms = get_all_extended_terms()

    test_cases = {
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

    for source, expected in test_cases.items():
        assert extended_terms.get(source) == expected
        assert translator.translate_text(source) == expected


def test_translate_dataframe():
    """Test dataframe translation for deterministic glossary hits."""
    translator = StatementTranslator(get_settings())
    df = pd.DataFrame(
        {
            TRANSLATABLE_COLUMNS[0]: ["转账", "消费"],
            TRANSLATABLE_COLUMNS[1]: ["北京", "深圳"],
            TRANSLATABLE_COLUMNS[2]: ["电子回单", "交易明细"],
        }
    )

    result = translator.translate_dataframe(df)
    assert len(result) == 2
    assert "Transfer" in result[TRANSLATABLE_COLUMNS[0]].tolist()
    assert "Consumption" in result[TRANSLATABLE_COLUMNS[0]].tolist()


def test_statement_specific_terms():
    """Test statement-specific terms common in bank transaction histories."""
    translator = StatementTranslator(get_settings())

    test_cases = {
        "入账": "Posted",
        "出账": "Debited",
        "扣款": "Debit",
        "冲销": "Write-off",
        "退票": "Dishonored Bill",
        "收妥入账": "Posted upon Collection",
        "手续费减免": "Service Fee Waiver",
        "本息转存": "Principal and Interest Rollover",
    }

    for source, expected in test_cases.items():
        assert translator.translate_text(source) == expected


def test_payment_channel_terms():
    """Test payment channel and wallet-brand whitelist coverage."""
    translator = StatementTranslator(get_settings())

    test_cases = {
        "云闪付": "UnionPay QuickPass",
        "扫码收款": "Scan Collection",
        "付款码支付": "Payment Code Payment",
        "POS交易": "POS Transaction",
        "小程序支付": "Mini Program Payment",
        "免密支付": "Password-free Payment",
        "代扣签约": "Auto Debit Authorization",
    }

    for source, expected in test_cases.items():
        assert translator.translate_text(source) == expected
