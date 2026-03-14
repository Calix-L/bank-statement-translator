"""ICBC-focused PDF translation pipeline for dense-layout output."""

from __future__ import annotations

import re
from typing import Callable, Optional, Sequence

import fitz
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas

from config import Settings, get_settings
from statement_structurer import StatementStructurer
from translator import StatementTranslator
from word_layout import (
    IMAGE_RENDER_SCALE,
    QR_BOUNDS,
    STAMP_PADDING,
    ImageCrop,
    PageAssets,
    PageMetadata,
    RectGrid,
    cluster_positions,
    draw_page,
    render_page_image,
    transform_rotated_rect,
)


def translate_pdf_in_place(
    input_pdf_path: str,
    output_pdf_path: str,
    settings: Optional[Settings] = None,
    translate_fn: Optional[Callable[[str], str]] = None,
) -> str:
    """Render a translated ICBC statement while preserving the original 25-row page count."""
    active_settings = settings or get_settings()
    translator = translate_fn or _build_translator(active_settings)
    statement_translator = StatementTranslator(active_settings)

    with fitz.open(input_pdf_path) as doc:
        page_texts = [page.get_text("text") for page in doc]
        translated_pages = _translate_pages(page_texts, statement_translator)
        output = canvas.Canvas(output_pdf_path)

        for page_index, page in enumerate(doc):
            width = float(page.rect.width)
            height = float(page.rect.height)
            output.setPageSize((width, height))

            assets = _collect_page_assets(page, page_texts[page_index])
            draw_page(
                output=output,
                width=width,
                height=height,
                metadata=assets.metadata,
                translated_df=translated_pages[page_index],
                grid=assets.grid,
                qr_crop=assets.qr_crop,
                stamp_crop=assets.stamp_crop,
                translator=translator,
            )
            output.showPage()

        output.save()

    return output_pdf_path


def _translate_pages(page_texts: Sequence[str], translator: StatementTranslator):
    page_rows = [StatementStructurer.parse([page_text]) for page_text in page_texts]
    return [
        translator.translate_dataframe(StatementStructurer.to_dataframe(rows))
        for rows in page_rows
    ]


def _collect_page_assets(page: fitz.Page, page_text: str) -> PageAssets:
    return PageAssets(
        metadata=_extract_page_metadata(page_text),
        grid=_extract_table_grid(page),
        qr_crop=_extract_qr_code(page, scale=IMAGE_RENDER_SCALE),
        stamp_crop=_extract_red_stamp(page, scale=IMAGE_RENDER_SCALE),
    )


def _extract_qr_code(page: fitz.Page, scale: int = 2) -> Optional[ImageCrop]:
    image = render_page_image(page, scale)
    left, top, right, bottom = (value * scale for value in QR_BOUNDS)
    crop = image.crop((left, top, right, bottom))
    return crop, fitz.Rect(left / scale, top / scale, right / scale, bottom / scale)


def _extract_red_stamp(page: fitz.Page, scale: int = 2) -> Optional[ImageCrop]:
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    mask = (arr[:, :, 0] > 180) & (arr[:, :, 1] < 120) & (arr[:, :, 2] < 120)
    ys, xs = np.where(mask)
    if xs.size == 0:
        return None

    pad = STAMP_PADDING * scale
    left = max(0, int(xs.min()) - pad)
    top = max(0, int(ys.min()) - pad)
    right = min(image.width, int(xs.max()) + pad)
    bottom = min(image.height, int(ys.max()) + pad)

    crop = image.crop((left, top, right, bottom)).convert("RGBA")
    crop_arr = np.array(crop)
    red_mask = (crop_arr[:, :, 0] > 160) & (crop_arr[:, :, 1] < 150) & (crop_arr[:, :, 2] < 150)
    crop_arr[:, :, 3] = np.where(red_mask, 255, 0).astype(np.uint8)
    crop = Image.fromarray(crop_arr, mode="RGBA")

    return crop, fitz.Rect(left / scale, top / scale, right / scale, bottom / scale)


def _extract_table_grid(page: fitz.Page) -> RectGrid:
    page_width = float(page.rect.width)
    rects: list[fitz.Rect] = []

    for drawing in page.get_drawings():
        if drawing.get("type") != "s":
            continue
        if drawing.get("color") != (0.0, 0.0, 0.0):
            continue
        if abs(float(drawing.get("width", 0.0)) - 0.5) > 0.1:
            continue

        rect = drawing.get("rect")
        if rect is None or rect.width < 10 or rect.height < 10:
            continue
        rects.append(transform_rotated_rect(rect, page_width))

    rows = cluster_positions(sorted({round(rect.y0, 1) for rect in rects}))
    cols = cluster_positions(sorted({round(rect.x0, 1) for rect in rects}))

    grid: RectGrid = []
    for row_y in rows:
        row_rects = [rect for rect in rects if abs(rect.y0 - row_y) <= 1.5]
        row_rects = sorted(row_rects, key=lambda item: item.x0)
        if len(row_rects) == len(cols):
            grid.append(row_rects)
    return grid


def _extract_page_metadata(page_text: str) -> PageMetadata:
    return PageMetadata(
        card_number=_search(page_text, r"鍗″彿\s*([0-9*]+)"),
        account_name=_search(page_text, r"鎴峰悕锛?([^\n]+)"),
        date_range=_search(page_text, r"璧锋鏃ユ湡锛?([^\n]+)"),
        total_pages=_search(page_text, r"鍏盶s*(\d+)\s*椤?"),
        page_number=_search(page_text, r"绗琝s*(\d+)\s*椤?"),
        order_time=_search(page_text, r"涓嬪崟鏃堕棿锛?([0-9:\- ]+)"),
        page_income=_search(page_text, r"鏈〉鏀跺叆绠楁湳鍚堣锛?([0-9,.\-+]+)"),
        page_expenditure=_search(page_text, r"鏈〉鏀嚭绠楁湳鍚堣锛?([0-9,.\-+]+)"),
        transaction_count=_search(page_text, r"鏈〉浜ゆ槗绗旀暟锛?(\d+)"),
    )


def _search(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _build_translator(settings: Settings) -> Callable[[str], str]:
    statement_translator = StatementTranslator(settings)

    def translate(text: str) -> str:
        translated = statement_translator.translate_text(text)
        return translated if translated else text

    return translate


def pdf_to_word(pdf_path: str, word_path: str) -> str:
    raise NotImplementedError(
        "DOCX conversion is not supported. Use translate_pdf_in_place(input_pdf, output_pdf) instead."
    )


def translate_word(
    input_docx_path: str,
    output_docx_path: str,
    settings: Optional[Settings] = None,
    translate_fn: Optional[Callable[[str], str]] = None,
) -> str:
    return translate_pdf_in_place(
        input_docx_path,
        output_docx_path,
        settings=settings,
        translate_fn=translate_fn,
    )


def word_to_pdf(word_path: str, pdf_path: str) -> str:
    raise NotImplementedError(
        "DOCX conversion is not supported. Use translate_pdf_in_place(input_pdf, output_pdf) instead."
    )
