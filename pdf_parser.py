"""PDF validation, text extraction and page rendering using cloud OCR API."""

from __future__ import annotations

import base64
import re
from typing import List, Tuple

import fitz
import requests

from config import Settings
from logger import get_logger


logger = get_logger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    pass


class PDFParser:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate_pdf(self, pdf_bytes: bytes) -> Tuple[bool, str]:
        """Validate PDF file before processing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        size_mb = len(pdf_bytes) / 1024 / 1024
        if size_mb > self.settings.max_file_size_mb:
            logger.warning(f"PDF too large: {size_mb:.1f}MB > {self.settings.max_file_size_mb}MB")
            return False, f"File size exceeds limit (>{self.settings.max_file_size_mb}MB)"

        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                if doc.page_count == 0:
                    logger.warning("PDF has no pages")
                    return False, "PDF has no pages"
                if doc.page_count > self.settings.max_pages:
                    logger.warning(f"PDF too many pages: {doc.page_count} > {self.settings.max_pages}")
                    return False, f"Page count exceeds limit (>{self.settings.max_pages})"
        except Exception as exc:
            logger.error(f"Cannot parse PDF: {exc}")
            return False, f"Cannot parse PDF: {exc}"

        logger.info(f"PDF validated: {size_mb:.1f}MB")
        return True, ""

    def extract_text_by_page(self, pdf_bytes: bytes) -> List[str]:
        """Extract text from PDF using cloud OCR API or PyMuPDF fallback."""
        
        # Check if OCR token is configured
        if not self.settings.ocr_token:
            logger.info("OCR_TOKEN not configured, using PyMuPDF fallback")
            return self._extract_with_pymupdf(pdf_bytes)
        
        # Try cloud OCR first
        try:
            logger.info("Attempting cloud OCR extraction...")
            return self._extract_with_cloud_ocr(pdf_bytes)
        except OCRError as e:
            logger.warning(f"Cloud OCR failed: {e}, falling back to PyMuPDF")
            return self._extract_with_pymupdf(pdf_bytes)
        except Exception as e:
            logger.error(f"OCR processing error: {e}, falling back to PyMuPDF")
            return self._extract_with_pymupdf(pdf_bytes)

    def _extract_with_pymupdf(self, pdf_bytes: bytes) -> List[str]:
        """Extract text using PyMuPDF (fallback)"""
        pages: List[str] = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                pages.append(page.get_text("text").strip())
        logger.info(f"Extracted {len(pages)} pages using PyMuPDF")
        return pages

    def _extract_with_cloud_ocr(self, pdf_bytes: bytes) -> List[str]:
        """Use Baidu AI Studio cloud OCR API"""
        
        # Convert PDF to base64
        file_data = base64.b64encode(pdf_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"token {self.settings.ocr_token}",
            "Content-Type": "application/json"
        }
        
        # Use layout-parsing API
        payload = {
            "file": file_data,
            "fileType": 0,  # PDF
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
        }
        
        logger.info("Submitting OCR job to cloud layout-parsing API...")
        
        # Use timeout from settings
        timeout = self.settings.request_timeout_sec
        
        try:
            response = requests.post(
                self.settings.ocr_api_url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.exceptions.Timeout:
            raise OCRError(
                f"OCR request timed out after {timeout}s. "
                "Please try again or increase REQUEST_TIMEOUT_SEC in .env"
            )
        except requests.exceptions.ConnectionError as e:
            raise OCRError(
                f"Cannot connect to OCR service. Check your network/proxy. Error: {e}"
            )
        
        # Check HTTP status
        if response.status_code == 401:
            raise OCRError(
                "OCR authentication failed. Please check your OCR_TOKEN is correct."
            )
        elif response.status_code == 403:
            raise OCRError(
                "OCR access denied. Your token may have insufficient permissions."
            )
        elif response.status_code == 429:
            raise OCRError(
                "OCR rate limit exceeded. Please wait and try again later."
            )
        elif response.status_code != 200:
            raise OCRError(
                f"OCR request failed with status {response.status_code}: {response.text[:200]}"
            )
        
        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            raise OCRError(f"Invalid OCR response (not JSON): {e}")
        
        # Check for API errors
        if "errorCode" in data and data.get("errorCode"):
            error_msg = data.get("errorMsg", "Unknown error")
            raise OCRError(f"OCR API error: {error_msg}")
        
        if "result" not in data:
            raise OCRError("OCR response missing 'result' field")
        
        result = data["result"]
        
        # Check if we got any results
        layout_results = result.get("layoutParsingResults", [])
        if not layout_results:
            raise OCRError(
                "OCR returned no content. The PDF may be empty or unreadable."
            )
        
        logger.info(f"OCR completed, layout results: {len(layout_results)}")
        
        # Parse results
        pages_text = []
        
        for res in layout_results:
            # Extract markdown text
            md_text = res.get("markdown", {}).get("text", "")
            
            # Clean markdown (remove HTML tags)
            clean_text = re.sub(r'<[^>]+>', '\n', md_text)
            clean_text = re.sub(r'\n+', '\n', clean_text)
            clean_text = clean_text.strip()
            
            pages_text.append(clean_text)
        
        return pages_text

    @staticmethod
    def is_text_sparse(page_texts: List[str], min_chars: int = 60) -> bool:
        total_chars = sum(len(t.strip()) for t in page_texts)
        return total_chars < min_chars
