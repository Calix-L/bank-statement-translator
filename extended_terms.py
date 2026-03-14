"""Backward-compatible facade for structured term dictionaries."""

from __future__ import annotations

from terms import (
    BANKING_GLOSSARY_TERMS,
    EXTENDED_BANK_TERMS,
    PAYMENT_CHANNEL_TERMS,
    PAYMENT_INSTITUTION_TERMS,
    PAYMENT_TERMS,
    get_all_extended_terms,
)

__all__ = [
    "BANKING_GLOSSARY_TERMS",
    "EXTENDED_BANK_TERMS",
    "PAYMENT_CHANNEL_TERMS",
    "PAYMENT_INSTITUTION_TERMS",
    "PAYMENT_TERMS",
    "get_all_extended_terms",
]
