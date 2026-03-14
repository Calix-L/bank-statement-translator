"""Layout and rendering helpers for dense ICBC PDF output."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, List, Optional

import fitz
from PIL import Image
from pypinyin import lazy_pinyin
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from statement_structurer import PDF_HEADER_ORDER


TITLE_EN = "ICBC Debit Account Historical Statement (Electronic Version)"
HEADER_LABELS = [
    "Transaction\nDate",
    "Account\nNo.",
    "Savings\nType",
    "Sequence\nNumber",
    "Currency",
    "Cash /\nTransfer",
    "Description",
    "Region",
    "Income /\nExpenditure\nAmount",
    "Balance",
    "Counterparty\nName",
    "Counterparty\nAccount",
    "Channel",
]
CHANNEL_COLUMN_INDEX = 12
COUNTERPARTY_NAME_COLUMN_INDEX = 10
COUNTERPARTY_ACCOUNT_COLUMN_INDEX = 11
DESCRIPTION_COLUMN_INDEX = 6
QR_BOUNDS = (714, 2, 770, 56)
STAMP_PADDING = 6
IMAGE_RENDER_SCALE = 4
FONT_LIMITS = {
    "header": (4.2, 2.7),
    CHANNEL_COLUMN_INDEX: (4.2, 2.4),
    COUNTERPARTY_NAME_COLUMN_INDEX: (4.5, 2.4),
    COUNTERPARTY_ACCOUNT_COLUMN_INDEX: (4.8, 2.8),
    DESCRIPTION_COLUMN_INDEX: (4.8, 2.8),
    "default": (5.4, 3.0),
}

RectGrid = List[List[fitz.Rect]]
ImageCrop = tuple[Image.Image, fitz.Rect]


@dataclass(frozen=True)
class PageMetadata:
    card_number: str = ""
    account_name: str = ""
    date_range: str = ""
    total_pages: str = ""
    page_number: str = ""
    order_time: str = ""
    page_income: str = ""
    page_expenditure: str = ""
    transaction_count: str = ""


@dataclass(frozen=True)
class PageAssets:
    metadata: PageMetadata
    grid: RectGrid
    qr_crop: Optional[ImageCrop]
    stamp_crop: Optional[ImageCrop]


def draw_page(
    output: canvas.Canvas,
    width: float,
    height: float,
    metadata: PageMetadata,
    translated_df,
    grid: RectGrid,
    qr_crop: Optional[ImageCrop],
    stamp_crop: Optional[ImageCrop],
    translator: Callable[[str], str],
) -> None:
    output.setFillColorRGB(1, 1, 1)
    output.rect(0, 0, width, height, fill=1, stroke=0)

    _draw_overlay_image(output, page_height=height, crop=qr_crop)
    _draw_header(output, width, height, metadata, translator)
    _draw_table(output, height, translated_df, grid, stamp_crop[1] if stamp_crop else None)
    _draw_footer(output, metadata)
    _draw_overlay_image(output, page_height=height, crop=stamp_crop)


def build_table_rows(translated_df) -> list[list[str]]:
    data_rows = translated_df[PDF_HEADER_ORDER].fillna("").astype(str).values.tolist()
    body_rows = [
        [_format_cell(PDF_HEADER_ORDER[index], value) for index, value in enumerate(row)]
        for row in data_rows
    ]
    return [HEADER_LABELS] + body_rows


def ascii_safe(text: str) -> str:
    cleaned = "".join(char for char in text if ord(char) < 128)
    return re.sub(r"\s+", " ", cleaned).strip()


def romanize_name(name: str, translator: Callable[[str], str]) -> str:
    translated = ascii_safe(translator(name)) if name else ""
    if translated:
        return translated
    if not name:
        return ""
    return " ".join(part.capitalize() for part in lazy_pinyin(name))


def sanitize_date_range(text: str) -> str:
    cleaned = text.replace("鈥?", "-").replace("鈥?", "-").replace("斜泻", "-")
    cleaned = "".join(char for char in cleaned if ord(char) < 128 or char == "-")
    return re.sub(r"\s+", " ", cleaned).strip()


def draw_rect(output: canvas.Canvas, rect: fitz.Rect, page_height: float) -> None:
    output.rect(rect.x0, page_height - rect.y1, rect.width, rect.height, fill=0, stroke=1)


def render_page_image(page: fitz.Page, scale: int) -> Image.Image:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def cluster_positions(values: list[float], tolerance: float = 2.0) -> list[float]:
    clusters: list[float] = []
    for value in values:
        if not clusters or abs(value - clusters[-1]) > tolerance:
            clusters.append(value)
    return clusters


def transform_rotated_rect(rect: fitz.Rect, page_width: float) -> fitz.Rect:
    return fitz.Rect(page_width - rect.y1, rect.x0, page_width - rect.y0, rect.x1)


def _draw_header(
    output: canvas.Canvas,
    width: float,
    height: float,
    metadata: PageMetadata,
    translator: Callable[[str], str],
) -> None:
    output.setFillColorRGB(0, 0, 0)
    output.setFont("Helvetica-Bold", 12)
    output.drawCentredString(width / 2, height - 22, TITLE_EN)

    output.setFont("Helvetica", 9)
    output.drawString(82, height - 46, f"Card No. {metadata.card_number}")
    display_name = romanize_name(metadata.account_name, translator) or ascii_safe(metadata.account_name)
    output.drawString(256, height - 46, f"Name: {display_name}")
    output.drawString(500, height - 46, f"Date Range: {sanitize_date_range(metadata.date_range)}")


def _draw_table(
    output: canvas.Canvas,
    page_height: float,
    translated_df,
    grid: RectGrid,
    avoid_rect: Optional[fitz.Rect],
) -> None:
    if not grid:
        return

    rows = build_table_rows(translated_df)
    output.setStrokeColorRGB(0, 0, 0)
    output.setLineWidth(0.5)

    for row_index, rects in enumerate(grid):
        values = rows[row_index] if row_index < len(rows) else [""] * len(rects)
        for col_index, rect in enumerate(rects):
            draw_rect(output, rect, page_height)
            text = values[col_index] if col_index < len(values) else ""
            _draw_cell_text(
                output=output,
                rect=rect,
                page_height=page_height,
                text=text,
                column_index=col_index,
                bold=(row_index == 0),
                avoid_rect=avoid_rect,
            )


def _draw_footer(output: canvas.Canvas, metadata: PageMetadata) -> None:
    output.setFillColorRGB(0, 0, 0)
    output.setFont("Helvetica", 9)
    output.drawString(31, 28, f"Page Expenditure Total: {metadata.page_expenditure}")
    output.drawString(31, 13, f"Transactions on Page: {metadata.transaction_count}")
    output.drawString(444, 28, f"Page Income Total: {metadata.page_income}")
    output.drawString(676, 28, f"Generated At: {metadata.order_time}")
    output.drawString(742, 13, f"Page {metadata.page_number} / {metadata.total_pages}")


def _draw_overlay_image(
    output: canvas.Canvas,
    page_height: float,
    crop: Optional[ImageCrop],
) -> None:
    if crop is None:
        return

    image, rect = crop
    output.drawImage(
        ImageReader(image),
        rect.x0,
        page_height - rect.y1,
        width=rect.width,
        height=rect.height,
        preserveAspectRatio=False,
        mask="auto",
    )


def _draw_cell_text(
    output: canvas.Canvas,
    rect: fitz.Rect,
    page_height: float,
    text: str,
    column_index: int,
    bold: bool = False,
    avoid_rect: Optional[fitz.Rect] = None,
) -> None:
    if not text:
        return

    text_rect = fitz.Rect(rect)
    if avoid_rect is not None and text_rect.intersects(avoid_rect):
        overlap = fitz.Rect(text_rect)
        overlap.intersect(avoid_rect)
        if overlap.height > 0:
            text_rect.y1 = max(text_rect.y0 + 6, avoid_rect.y0 - 1.0)

    font_name = "Helvetica-Bold" if bold else "Helvetica"
    font_size = _fit_font_size(text, text_rect.width - 4, text_rect.height - 4, font_name, bold, column_index)
    lines = _wrap_text(text, text_rect.width - 4, font_name, font_size)
    line_height = font_size * 0.98
    total_height = line_height * len(lines)
    top_padding = max(0, (text_rect.height - 4 - total_height) / 2)
    first_baseline = page_height - text_rect.y0 - 2 - top_padding - font_size * 0.82

    output.setFont(font_name, font_size)
    for index, line in enumerate(lines):
        y = first_baseline - index * line_height
        text_width = pdfmetrics.stringWidth(line, font_name, font_size)
        x = text_rect.x0 + max(0.8, (text_rect.width - text_width) / 2)
        output.drawString(x, y, line)


def _fit_font_size(
    text: str,
    width: float,
    height: float,
    font_name: str,
    bold: bool,
    column_index: int,
) -> float:
    max_size, min_size = _column_font_limits(column_index, bold)

    size = max_size
    while size >= min_size:
        lines = _wrap_text(text, width, font_name, size)
        if len(lines) * size <= height:
            return size
        size -= 0.2
    return min_size


def _column_font_limits(column_index: int, bold: bool) -> tuple[float, float]:
    if bold:
        return FONT_LIMITS["header"]
    return FONT_LIMITS.get(column_index, FONT_LIMITS["default"])


def _wrap_text(text: str, width: float, font_name: str, font_size: float) -> List[str]:
    lines: List[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue

        current = _split_long_token(words[0], width, font_name, font_size, lines)
        for word in words[1:]:
            word = _split_long_token(word, width, font_name, font_size, lines)
            candidate = f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def _split_long_token(token: str, width: float, font_name: str, font_size: float, lines: List[str]) -> str:
    if pdfmetrics.stringWidth(token, font_name, font_size) <= width:
        return token

    current = ""
    chunks: List[str] = []
    for char in token:
        candidate = current + char
        if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > width:
            chunks.append(current)
            current = char
        else:
            current = candidate
    if current:
        chunks.append(current)

    if len(chunks) == 1:
        return chunks[0]

    lines.extend(chunks[:-1])
    return chunks[-1]


def _format_cell(column: str, value: str) -> str:
    text = str(value or "")
    text = text.replace("()", "").replace("锛堢┖锛?", "").replace("(绌?", "")
    if column == "娓犻亾":
        text = text.replace("Quick Payment", "Quick\nPayment")
        text = text.replace("Online Banking", "Online\nBanking")
        text = text.replace("Batch Service", "Batch\nService")
    if column == "鎽樿":
        text = text.replace("Cardless Payment", "Cardless\nPayment")
        text = text.replace("Incoming Remittance", "Incoming\nRemittance")
    if column == "瀵规柟鎴峰悕":
        text = text.replace("Payment Technology Co Ltd", "Payment Tech Co Ltd")
        text = text.replace("Network Technology Co Ltd", "Network Tech Co Ltd")
        text = text.replace("Convenience Store", "Convenience\nStore")
        text = text.replace("Platform Merchant", "Platform\nMerchant")
        text = text.replace("Metro C Exit Supermarket", "Metro C Exit\nSupermarket")
    return text
