"""Parse extracted text into structured ICBC statement rows."""

from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd

from logger import get_logger


logger = get_logger(__name__)

PDF_HEADER_ORDER = [
    "交易日期",
    "账号",
    "储种",
    "序号",
    "币种",
    "钞汇",
    "摘要",
    "地区",
    "收入/支出金额",
    "余额",
    "对方户名",
    "对方账号",
    "渠道",
]

PDF_HEADER_MAP_EN = {
    "交易日期": "Transaction Date",
    "账号": "Account Number",
    "储种": "Savings Type",
    "序号": "Sequence Number",
    "币种": "Currency",
    "钞汇": "Cash/Transfer",
    "摘要": "Description",
    "地区": "Region",
    "收入/支出金额": "Income/Expenditure Amount",
    "余额": "Balance",
    "对方户名": "Counterparty Name",
    "对方账号": "Counterparty Account",
    "渠道": "Channel",
}

PDF_HEADER_ORDER_EN = [PDF_HEADER_MAP_EN[col] for col in PDF_HEADER_ORDER]


DATE_ONLY_RE = re.compile(r"^\d{4}[/-]\d{1,2}[/-]\d{1,2}$")
TIME_ONLY_RE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
AMOUNT_ONLY_RE = re.compile(r"^[+-]?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})$")
COUNTERPARTY_ACCOUNT_RE = re.compile(r"^(?:\d{4}\*{2,}\d{4}|\d{8,}|（空）|\(空\))$")

FOOTER_PREFIXES = (
    "本页支出算术合计",
    "本页交易笔数",
    "本页收入算术合计",
    "下单时间",
    "第 ",
    "共 ",
    "中国工商银行 ",
)


class StatementStructurer:
    @staticmethod
    def parse(page_texts: List[str]) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        for i, page_text in enumerate(page_texts):
            page_rows = StatementStructurer._parse_icbc_page(page_text)
            logger.debug(f"Page {i+1}: parsed {len(page_rows)} rows")
            rows.extend(page_rows)
        logger.info(f"Total rows parsed: {len(rows)}")
        return rows

    @staticmethod
    def to_dataframe(rows: List[Dict[str, str]]) -> pd.DataFrame:
        return pd.DataFrame(rows, columns=PDF_HEADER_ORDER)

    @staticmethod
    def _parse_icbc_page(page_text: str) -> List[Dict[str, str]]:
        lines = [StatementStructurer._normalize_line(line) for line in page_text.splitlines()]
        lines = [line for line in lines if line]
        rows: List[Dict[str, str]] = []

        idx = 0
        while idx < len(lines):
            if not StatementStructurer._is_date_line(lines[idx]):
                idx += 1
                continue

            if idx + 10 >= len(lines):
                break

            time_raw = lines[idx + 1]
            amount_raw = lines[idx + 9]
            balance_raw = lines[idx + 10]
            if (
                not TIME_ONLY_RE.match(time_raw)
                or not AMOUNT_ONLY_RE.match(amount_raw)
                or not AMOUNT_ONLY_RE.match(balance_raw)
            ):
                idx += 1
                continue

            transaction_date = StatementStructurer._normalize_date(lines[idx])
            account = lines[idx + 2]
            savings_type = lines[idx + 3]
            sequence = lines[idx + 4]
            currency = lines[idx + 5]
            cash_or_transfer = lines[idx + 6]
            summary = lines[idx + 7]
            area = lines[idx + 8]
            amount = amount_raw.replace(",", "")
            balance = balance_raw.replace(",", "")

            detail_start = idx + 11
            detail_end = detail_start
            while detail_end < len(lines):
                line = lines[detail_end]
                if StatementStructurer._is_date_line(line) or StatementStructurer._is_footer_line(line):
                    break
                detail_end += 1

            counterparty, counterparty_account, channel = StatementStructurer._parse_counterparty_and_channel(
                lines[detail_start:detail_end]
            )

            rows.append(
                {
                    "交易日期": transaction_date,
                    "账号": account,
                    "储种": savings_type,
                    "序号": sequence,
                    "币种": currency,
                    "钞汇": cash_or_transfer,
                    "摘要": summary,
                    "地区": area,
                    "收入/支出金额": amount,
                    "余额": balance,
                    "对方户名": counterparty,
                    "对方账号": counterparty_account,
                    "渠道": channel,
                }
            )
            idx = detail_end

        return rows

    @staticmethod
    def _parse_counterparty_and_channel(detail_lines: List[str]) -> tuple[str, str, str]:
        if not detail_lines:
            return "", "", ""

        channel = detail_lines[-1]
        account_idx = -1
        for i in range(len(detail_lines) - 1, -1, -1):
            if COUNTERPARTY_ACCOUNT_RE.match(detail_lines[i]):
                account_idx = i
                break

        counterparty_account = ""
        if account_idx == -1:
            name_parts = detail_lines[:-1] if len(detail_lines) > 1 else detail_lines
        else:
            counterparty_account = detail_lines[account_idx]
            name_parts = detail_lines[:account_idx]

        counterparty = "".join(part for part in name_parts if part not in {"（空）", "(空)"}).strip()
        return counterparty, counterparty_account, channel

    @staticmethod
    def _normalize_line(line: str) -> str:
        return re.sub(r"\s+", " ", line).strip()

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        y, m, d = [int(part) for part in date_str.replace("/", "-").split("-")]
        return f"{y:04d}-{m:02d}-{d:02d}"

    @staticmethod
    def _is_date_line(line: str) -> bool:
        return bool(DATE_ONLY_RE.match(line))

    @staticmethod
    def _is_footer_line(line: str) -> bool:
        return line.startswith(FOOTER_PREFIXES)
