"""Streamlit entrypoint for bank statement translator - with batch processing support."""

from __future__ import annotations

import json
import os
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import streamlit as st

from cache import get_cache
from config import get_settings
from config_validator import ConfigValidator
from excel_generator import ExcelGenerator
from logger import setup_logger
from pdf_parser import PDFParser
from statement_structurer import StatementStructurer
from translator import StatementTranslator


# Setup logging
logger = setup_logger("bank_statement_translator")


class _HealthHandler(BaseHTTPRequestHandler):
    """Minimal health endpoint handler."""

    def do_GET(self):
        if self.path == "/health":
            payload = {"status": "ok"}
            self._write_json(200, payload)
            return

        if self.path == "/metrics":
            payload = get_cache().get_translation_stats()
            self._write_json(200, payload)
            return

        self._write_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/clear-cache":
            deleted = get_cache().clear("translation")
            payload = {"status": "ok", "deleted_files": deleted}
            self._write_json(200, payload)
            return

        self._write_json(404, {"error": "not found"})

    def _write_json(self, status: int, payload_obj: dict):
        payload = json.dumps(payload_obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        # Keep endpoint logs out of Streamlit output.
        return


@st.cache_resource
def start_health_server():
    """Start a lightweight health endpoint server once per Streamlit process."""
    host = os.getenv("HEALTH_CHECK_HOST", "0.0.0.0")
    port = int(os.getenv("HEALTH_CHECK_PORT", "8502"))

    try:
        server = ThreadingHTTPServer((host, port), _HealthHandler)
    except OSError as e:
        logger.warning(f"Health server not started on {host}:{port}: {e}")
        return None

    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"Health endpoint available at http://{host}:{port}/health")
    return server


@st.cache_resource
def get_pdf_parser():
    settings = get_settings()
    return PDFParser(settings)


def process_single_file(pdf_bytes: bytes, filename: str, parser, settings, translator, progress_bar, status_text, progress_start: int, progress_end: int) -> dict:
    """Process a single PDF file.
    
    Returns:
        dict with keys: name, translated_df, raw_df, row_count, error
    """
    import math
    
    step = (progress_end - progress_start) // 3
    
    # Validate
    status_text.text(f"Validating {filename}...")
    progress_bar.progress(progress_start)
    ok, msg = parser.validate_pdf(pdf_bytes)
    if not ok:
        logger.error(f"PDF validation failed for {filename}: {msg}")
        return {"name": filename, "translated_df": None, "raw_df": None, "row_count": 0, "error": msg}
    
    # Extract
    status_text.text(f"Extracting text from {filename}...")
    progress_bar.progress(progress_start + step)
    page_texts = parser.extract_text_by_page(pdf_bytes)
    logger.info(f"Extracted {len(page_texts)} pages from {filename}")
    
    # Parse
    status_text.text(f"Parsing transactions from {filename}...")
    progress_bar.progress(progress_start + step * 2)
    rows = StatementStructurer.parse(page_texts)
    
    if not rows:
        logger.warning(f"No transactions found in {filename}")
        return {"name": filename, "translated_df": None, "raw_df": None, "row_count": 0, "error": "No transactions found"}
    
    df = StatementStructurer.to_dataframe(rows)
    logger.info(f"Parsed {len(df)} transactions from {filename}")
    
    # Translate
    status_text.text(f"Translating {filename}...")
    progress_bar.progress(progress_end - step // 2)
    translated_df = translator.translate_dataframe(df)
    logger.info(f"Translation completed for {filename}")
    
    progress_bar.progress(progress_end)
    
    return {
        "name": filename,
        "translated_df": translated_df,
        "raw_df": df,
        "row_count": len(df),
        "error": None
    }


def main():
    start_health_server()

    st.set_page_config(
        page_title="Bank Statement Translator",
        page_icon="🏦",
        layout="wide",
    )

    st.title("🏦 Bank Statement Translator")
    st.markdown("Convert Chinese bank statements to English Excel files")
    
    # Sidebar with config info
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        settings = get_settings()
        
        # Check config status
        if not settings.zhipu_api_key:
            st.error("⚠️ ZHIPU_API_KEY not configured")
            st.info("Translation requires API key. Please set ZHIPU_API_KEY in .env")
        else:
            st.success("✅ Translation API configured")
        
        if not settings.ocr_token:
            st.warning("⚠️ OCR_TOKEN not configured")
            st.info("Will use PyMuPDF fallback (may miss text in scanned PDFs)")
        else:
            st.success("✅ OCR configured")
        
        st.divider()
        st.markdown("**Limits:**")
        st.markdown(f"- Max file size: {settings.max_file_size_mb}MB")
        st.markdown(f"- Max pages: {settings.max_pages}")
        st.markdown(f"- Timeout: {settings.request_timeout_sec}s")
    
    # Main content
    # File upload - support multiple files
    uploaded_files = st.file_uploader(
        "Upload PDF bank statement(s)",
        type=["pdf"],
        help="Upload one or more Chinese bank statement PDFs",
        accept_multiple_files=True,
    )

    if uploaded_files:
        # Settings
        parser = get_pdf_parser()
        settings = get_settings()
        translator = StatementTranslator(settings)
        
        # Process mode
        if len(uploaded_files) == 1:
            # Single file mode
            pdf_bytes = uploaded_files[0].read()
            logger.info(f"Processing single file: {uploaded_files[0].name}")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            result = process_single_file(
                pdf_bytes, uploaded_files[0].name, 
                parser, settings, translator,
                progress_bar, status_text, 0, 100
            )
            
            if result["error"]:
                st.error(f"Error: {result['error']}")
                return
            
            st.success(f"✅ Done! Found {result['row_count']} transactions")
            
            # Preview
            st.subheader("Preview")
            st.dataframe(result["translated_df"].head(10), use_container_width=True)
            
            # Generate Excel
            excel_bytes = ExcelGenerator.generate(
                translated_df=result["translated_df"], 
                raw_df=result["raw_df"]
            )
            
            st.download_button(
                label="Download Excel",
                data=excel_bytes,
                file_name="translated_statement.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            
        else:
            # Batch mode
            st.info(f"📂 Batch mode: {len(uploaded_files)} files selected")
            
            results = []
            total = len(uploaded_files)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                pdf_bytes = uploaded_file.read()
                filename = uploaded_file.name
                
                progress_start = int(i * 100 / total)
                progress_end = int((i + 1) * 100 / total)
                
                status_text.text(f"Processing {i+1}/{total}: {filename}")
                
                result = process_single_file(
                    pdf_bytes, filename,
                    parser, settings, translator,
                    progress_bar, status_text,
                    progress_start, progress_end
                )
                
                results.append(result)
                
                if result["error"]:
                    st.warning(f"⚠️ {filename}: {result['error']}")
                else:
                    st.success(f"✅ {filename}: {result['row_count']} transactions")
            
            # Generate combined Excel
            status_text.text("Generating combined Excel...")
            excel_bytes = ExcelGenerator.generate_batch(results)
            logger.info(f"Batch Excel generated: {len(excel_bytes)} bytes")
            
            progress_bar.progress(100)
            status_text.text("Done!")
            
            # Summary
            successful = sum(1 for r in results if r["error"] is None)
            total_rows = sum(r["row_count"] for r in results)
            st.info(f"📊 Summary: {successful}/{total} files processed, {total_rows} total transactions")
            
            # Download
            st.download_button(
                label="Download Combined Excel",
                data=excel_bytes,
                file_name="batch_translated_statements.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            
            logger.info(f"User downloaded batch result: {successful}/{total} files")


if __name__ == "__main__":
    main()
