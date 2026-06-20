"""PDF processing and OCR functionality for Contract Intelligence System."""

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

from src.config import settings
from src.utils.logging_config import logger


@dataclass
class OCRResult:
    """Result of OCR processing.
    
    Attributes:
        text: Extracted text content.
        confidence: OCR confidence score (0-100).
        pages: Number of pages processed.
        method: Extraction method used ('text', 'ocr', 'hybrid').
        error: Error message if processing failed.
    """
    
    text: str = ""
    confidence: float = 0.0
    pages: int = 0
    method: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with OCR result data.
        """
        return {
            "text": self.text,
            "confidence": self.confidence,
            "pages": self.pages,
            "method": self.method,
            "error": self.error,
        }


class PDFProcessor:
    """Process PDF files for text extraction using OCR or direct extraction.
    
    This class handles both text-based PDFs (extracting embedded text) and
    image-based PDFs (using Tesseract OCR). It automatically detects the
    best extraction method based on content analysis.
    
    Attributes:
        tesseract_cmd: Path to Tesseract executable.
        ocr_lang: Language(s) for OCR.
        ocr_psm: Page segmentation mode for Tesseract.
    """
    
    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        ocr_lang: str = "eng",
        ocr_psm: int = 3,
    ) -> None:
        """Initialize PDF processor.
        
        Args:
            tesseract_cmd: Path to Tesseract executable. If None, uses system default.
            ocr_lang: Language(s) for OCR processing.
            ocr_psm: Page segmentation mode for Tesseract.
        """
        self.tesseract_cmd = tesseract_cmd or settings.tesseract_cmd
        self.ocr_lang = ocr_lang
        self.ocr_psm = ocr_psm
        
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        
        logger.info(
            f"PDFProcessor initialized with lang={ocr_lang}, psm={ocr_psm}"
        )
    
    def process_file(self, file_path: Path | str) -> OCRResult:
        """Process a PDF file and extract text.
        
        Args:
            file_path: Path to the PDF file.
            
        Returns:
            OCRResult containing extracted text and metadata.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return OCRResult(error=f"File not found: {file_path}")
        
        try:
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            return self.process_bytes(pdf_bytes)
        except Exception as e:
            logger.exception(f"Error reading file {file_path}: {e}")
            return OCRResult(error=str(e))
    
    def process_bytes(self, pdf_bytes: bytes) -> OCRResult:
        """Process PDF bytes and extract text.
        
        Args:
            pdf_bytes: Raw PDF file bytes.
            
        Returns:
            OCRResult containing extracted text and metadata.
        """
        try:
            # First, try to extract text directly from PDF
            text_result = self._extract_text_directly(pdf_bytes)
            
            if text_result and text_result.text.strip():
                logger.info("Direct text extraction successful")
                text_result.method = "text"
                text_result.confidence = 100.0  # High confidence for embedded text
                return text_result
            
            # Fall back to OCR if no embedded text
            logger.info("Falling back to OCR processing")
            ocr_result = self._process_with_ocr(pdf_bytes)
            ocr_result.method = "ocr"
            return ocr_result
            
        except Exception as e:
            logger.exception(f"Error processing PDF: {e}")
            return OCRResult(error=str(e))
    
    def _extract_text_directly(self, pdf_bytes: bytes) -> Optional[OCRResult]:
        """Extract text directly from PDF if available.
        
        Args:
            pdf_bytes: Raw PDF file bytes.
            
        Returns:
            OCRResult with extracted text, or None if no text found.
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages = len(pdf.pages)
                if pages == 0:
                    return None
                
                full_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text.append(text)
                
                if not full_text:
                    return None
                
                extracted_text = "\n".join(full_text)
                
                # Check if extracted text is meaningful
                if len(extracted_text.strip()) < 50:
                    return None
                
                return OCRResult(
                    text=extracted_text,
                    confidence=95.0,
                    pages=pages,
                )
        except Exception as e:
            logger.warning(f"Direct text extraction failed: {e}")
            return None
    
    def _process_with_ocr(self, pdf_bytes: bytes) -> OCRResult:
        """Process PDF using Tesseract OCR.
        
        Args:
            pdf_bytes: Raw PDF file bytes.
            
        Returns:
            OCRResult with OCR-extracted text.
        """
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes)
            
            if not images:
                return OCRResult(error="No pages found in PDF")
            
            full_text = []
            total_confidence = 0.0
            
            for i, image in enumerate(images):
                # Perform OCR on each page
                ocr_data = pytesseract.image_to_data(
                    image,
                    lang=self.ocr_lang,
                    output_type=pytesseract.Output.DICT,
                )
                
                # Calculate average confidence for this page
                confidences = [
                    int(c) for c in ocr_data["conf"] if int(c) > -1
                ]
                if confidences:
                    page_confidence = sum(confidences) / len(confidences)
                    total_confidence += page_confidence
                
                # Extract text
                page_text = pytesseract.image_to_string(
                    image,
                    lang=self.ocr_lang,
                )
                full_text.append(page_text)
            
            avg_confidence = (
                total_confidence / len(images) if images else 0.0
            )
            
            return OCRResult(
                text="\n".join(full_text),
                confidence=avg_confidence,
                pages=len(images),
            )
            
        except Exception as e:
            logger.exception(f"OCR processing failed: {e}")
            return OCRResult(error=str(e))
