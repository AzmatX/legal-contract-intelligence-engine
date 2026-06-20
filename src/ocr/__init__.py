"""OCR module for Contract Intelligence System."""

from src.ocr.pdf_processor import PDFProcessor, OCRResult
from src.ocr.text_cleaner import TextCleaner

__all__ = ["PDFProcessor", "OCRResult", "TextCleaner"]
