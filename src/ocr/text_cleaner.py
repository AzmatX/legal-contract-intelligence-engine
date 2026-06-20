"""Text cleaning utilities for OCR output."""

import re
from typing import Optional


class TextCleaner:
    """Clean and normalize extracted text from OCR or PDF processing.
    
    This class provides methods to clean up text extracted from documents,
    removing artifacts from OCR processing and normalizing formatting.
    
    Attributes:
        remove_extra_whitespace: Whether to collapse multiple spaces.
        normalize_line_breaks: Whether to normalize line breaks.
        remove_hyphens: Whether to remove hyphenation from line breaks.
    """
    
    def __init__(
        self,
        remove_extra_whitespace: bool = True,
        normalize_line_breaks: bool = True,
        remove_hyphens: bool = True,
    ) -> None:
        """Initialize text cleaner.
        
        Args:
            remove_extra_whitespace: Collapse multiple whitespace to single space.
            normalize_line_breaks: Normalize various line break styles.
            remove_hyphens: Remove hyphens at line breaks (OCR artifacts).
        """
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_line_breaks = normalize_line_breaks
        self.remove_hyphens = remove_hyphens
    
    def clean(self, text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Raw text to clean.
            
        Returns:
            Cleaned and normalized text.
        """
        if not text:
            return ""
        
        cleaned = text
        
        # Remove hyphens at end of lines (OCR artifact)
        if self.remove_hyphens:
            cleaned = self._remove_hyphens(cleaned)
        
        # Normalize line breaks
        if self.normalize_line_breaks:
            cleaned = self._normalize_line_breaks(cleaned)
        
        # Remove extra whitespace
        if self.remove_extra_whitespace:
            cleaned = self._remove_extra_whitespace(cleaned)
        
        # Remove special characters that might be OCR artifacts
        cleaned = self._remove_artifacts(cleaned)
        
        return cleaned.strip()
    
    def _remove_hyphens(self, text: str) -> str:
        """Remove hyphens at line breaks (word continuation markers).
        
        Args:
            text: Text with potential hyphenated line breaks.
            
        Returns:
            Text with hyphens at line breaks removed.
        """
        # Pattern: word-hyphen-newline-word -> wordword
        pattern = r"(\w+)-\n(\w+)"
        return re.sub(pattern, r"\1\2", text)
    
    def _normalize_line_breaks(self, text: str) -> str:
        """Normalize various line break styles to Unix style.
        
        Args:
            text: Text with various line break styles.
            
        Returns:
            Text with normalized line breaks.
        """
        # Convert Windows and old Mac line breaks to Unix
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        
        # Remove excessive consecutive line breaks (more than 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """Collapse multiple whitespace characters to single space.
        
        Args:
            text: Text with extra whitespace.
            
        Returns:
            Text with normalized whitespace.
        """
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        
        # Collapse multiple spaces to single space (but preserve line breaks)
        text = re.sub(r"[^\S\n]+", " ", text)
        
        # Remove trailing whitespace on lines
        text = re.sub(r" +$", "", text, flags=re.MULTILINE)
        
        return text
    
    def _remove_artifacts(self, text: str) -> str:
        """Remove common OCR artifacts.
        
        Args:
            text: Text with potential OCR artifacts.
            
        Returns:
            Text with artifacts removed.
        """
        # Remove page numbers at start/end of lines (common OCR artifact)
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        
        # Remove isolated single characters (often OCR noise)
        # But keep 'I', 'A' as they might be legitimate
        text = re.sub(r"(?<!\w)[bcdefghjklmnopqrstuvwxyxzBCDEFGHJKLMNOPQRSTUVWXYXZ](?!\w)", "", text)
        
        # Remove repeated character sequences (e.g., "____", "====")
        text = re.sub(r"[_=]{3,}", "", text)
        
        return text
    
    def clean_for_nlp(self, text: str) -> str:
        """Clean text specifically for NLP processing.
        
        This method applies additional cleaning suitable for NLP tasks,
        preserving sentence structure while removing noise.
        
        Args:
            text: Raw text to clean.
            
        Returns:
            Text cleaned for NLP processing.
        """
        cleaned = self.clean(text)
        
        # Ensure single space after punctuation
        cleaned = re.sub(r"([.!?])([A-Z])", r"\1 \2", cleaned)
        
        # Remove URLs (they can interfere with NER)
        cleaned = re.sub(
            r"http[s]?://\S+|www\.\S+",
            "[URL]",
            cleaned
        )
        
        return cleaned
