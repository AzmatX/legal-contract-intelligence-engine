"""Tests for OCR module in Contract Intelligence System."""

import pytest
from pathlib import Path

from src.ocr.pdf_processor import PDFProcessor, OCRResult
from src.ocr.text_cleaner import TextCleaner


class TestTextCleaner:
    """Test cases for TextCleaner class."""
    
    def test_clean_removes_extra_whitespace(self) -> None:
        """Test that extra whitespace is removed."""
        cleaner = TextCleaner()
        text = "Hello    world   with   spaces"
        cleaned = cleaner.clean(text)
        assert "  " not in cleaned
        assert cleaned == "Hello world with spaces"
    
    def test_clean_normalizes_line_breaks(self) -> None:
        """Test that line breaks are normalized."""
        cleaner = TextCleaner()
        text = "Line1\r\nLine2\rLine3\nLine4"
        cleaned = cleaner.clean(text)
        assert "\r" not in cleaned
        assert cleaned.count("\n") <= 3
    
    def test_clean_removes_hyphens_at_line_breaks(self) -> None:
        """Test that hyphens at line breaks are removed."""
        cleaner = TextCleaner()
        text = "This is an exam-\nple of hyphenation"
        cleaned = cleaner.clean(text)
        assert "exam-\nple" not in cleaned
        assert "example" in cleaned
    
    def test_clean_empty_string(self) -> None:
        """Test cleaning empty string."""
        cleaner = TextCleaner()
        assert cleaner.clean("") == ""
        assert cleaner.clean("   ") == ""
    
    def test_clean_for_nlp(self) -> None:
        """Test NLP-specific cleaning."""
        cleaner = TextCleaner()
        text = "Visit http://example.com for more info."
        cleaned = cleaner.clean_for_nlp(text)
        assert "[URL]" in cleaned
        assert "http://" not in cleaned


class TestPDFProcessor:
    """Test cases for PDFProcessor class."""
    
    def test_processor_initialization(self) -> None:
        """Test PDF processor initialization."""
        processor = PDFProcessor()
        assert processor.ocr_lang == "eng"
        assert processor.ocr_psm == 3
    
    def test_process_nonexistent_file(self) -> None:
        """Test processing nonexistent file."""
        processor = PDFProcessor()
        result = processor.process_file("/nonexistent/path/file.pdf")
        assert result.error is not None
        assert "not found" in result.error.lower()
    
    def test_process_bytes_empty(self) -> None:
        """Test processing empty bytes."""
        processor = PDFProcessor()
        result = processor.process_bytes(b"")
        # Should not crash, may return error or empty result
        assert isinstance(result, OCRResult)
    
    def test_ocr_result_to_dict(self) -> None:
        """Test OCRResult to_dict method."""
        result = OCRResult(
            text="Sample text",
            confidence=95.0,
            pages=3,
            method="text",
        )
        result_dict = result.to_dict()
        assert result_dict["text"] == "Sample text"
        assert result_dict["confidence"] == 95.0
        assert result_dict["pages"] == 3
        assert result_dict["method"] == "text"
    
    def test_ocr_result_with_error(self) -> None:
        """Test OCRResult with error."""
        result = OCRResult(error="Test error message")
        assert result.error == "Test error message"
        assert result.text == ""
        assert result.confidence == 0.0
