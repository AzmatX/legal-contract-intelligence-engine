"""Clause classifier for Contract Intelligence System."""

from typing import Optional

from src.clause_classification.rules import ClauseRules, ClauseMatch
from src.ocr.text_cleaner import TextCleaner
from src.utils.logging_config import logger


class ClauseClassifier:
    """Classify contract clauses using rule-based detection.
    
    This class provides a high-level interface for detecting and
    classifying different types of clauses in contract documents.
    
    Attributes:
        rules_engine: Rule-based clause detection engine.
        text_cleaner: Text cleaning utility.
        min_confidence: Minimum confidence threshold for reporting.
    """
    
    SUPPORTED_CLAUSE_TYPES = [
        "Termination",
        "Confidentiality",
        "Indemnification",
        "Limitation of Liability",
        "Governing Law",
    ]
    
    def __init__(
        self,
        min_confidence: float = 0.3,
        clean_text: bool = True,
    ) -> None:
        """Initialize clause classifier.
        
        Args:
            min_confidence: Minimum confidence for clause detection.
            clean_text: Whether to clean text before classification.
        """
        self.rules_engine = ClauseRules(min_confidence=min_confidence)
        self.text_cleaner = TextCleaner() if clean_text else None
        self.min_confidence = min_confidence
        logger.info(
            f"ClauseClassifier initialized with min_confidence={min_confidence}"
        )
    
    def classify(self, text: str) -> list[ClauseMatch]:
        """Detect and classify clauses in text.
        
        Args:
            text: Contract text to analyze.
            
        Returns:
            List of detected ClauseMatch objects.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for clause classification")
            return []
        
        try:
            # Clean text if requested
            if self.text_cleaner:
                text = self.text_cleaner.clean(text)
            
            # Detect clauses
            matches = self.rules_engine.detect(text)
            
            # Set clause type names properly
            for match in matches:
                if not match.clause_type:
                    # Infer from patterns if not set
                    match.clause_type = self._infer_clause_type(match.matched_patterns)
            
            logger.info(f"Detected {len(matches)} clauses")
            return matches
            
        except Exception as e:
            logger.exception(f"Error in clause classification: {e}")
            return []
    
    def _infer_clause_type(self, patterns: list[str]) -> str:
        """Infer clause type from matched patterns.
        
        Args:
            patterns: List of matched pattern strings.
            
        Returns:
            Inferred clause type.
        """
        pattern_text = " ".join(patterns).lower()
        
        if any(kw in pattern_text for kw in ["termination", "terminate", "expire"]):
            return "Termination"
        elif any(kw in pattern_text for kw in ["confidential", "disclosure", "proprietary"]):
            return "Confidentiality"
        elif any(kw in pattern_text for kw in ["indemnif", "hold harmless", "reimburse"]):
            return "Indemnification"
        elif any(kw in pattern_text for kw in ["limitation", "liability", "consequential"]):
            return "Limitation of Liability"
        elif any(kw in pattern_text for kw in ["governing", "law", "jurisdiction", "venue"]):
            return "Governing Law"
        
        return "Unknown"
    
    def classify_by_type(
        self,
        text: str,
        clause_type: str,
    ) -> list[ClauseMatch]:
        """Detect clauses of a specific type.
        
        Args:
            text: Contract text to analyze.
            clause_type: Specific clause type to detect.
            
        Returns:
            List of matching ClauseMatch objects.
        """
        if clause_type not in self.SUPPORTED_CLAUSE_TYPES:
            logger.warning(f"Unsupported clause type: {clause_type}")
            return []
        
        all_matches = self.classify(text)
        return [m for m in all_matches if m.clause_type == clause_type]
    
    def get_clause_summary(self, text: str) -> dict:
        """Get a summary of detected clauses by type.
        
        Args:
            text: Contract text to analyze.
            
        Returns:
            Dictionary with clause counts and details.
        """
        matches = self.classify(text)
        
        summary: dict = {
            "total_clauses": len(matches),
            "by_type": {},
            "high_confidence_count": 0,
        }
        
        for match in matches:
            clause_type = match.clause_type
            
            if clause_type not in summary["by_type"]:
                summary["by_type"][clause_type] = {
                    "count": 0,
                    "max_confidence": 0.0,
                    "samples": [],
                }
            
            summary["by_type"][clause_type]["count"] += 1
            summary["by_type"][clause_type]["max_confidence"] = max(
                summary["by_type"][clause_type]["max_confidence"],
                match.confidence,
            )
            
            if match.confidence >= 0.7:
                summary["high_confidence_count"] += 1
            
            # Keep up to 2 samples per type
            if len(summary["by_type"][clause_type]["samples"]) < 2:
                summary["by_type"][clause_type]["samples"].append(
                    match.text[:100] + "..." if len(match.text) > 100 else match.text
                )
        
        return summary
    
    def has_clause(self, text: str, clause_type: str) -> bool:
        """Check if a specific clause type exists in the text.
        
        Args:
            text: Contract text to analyze.
            clause_type: Clause type to check for.
            
        Returns:
            True if clause is detected, False otherwise.
        """
        matches = self.classify_by_type(text, clause_type)
        return len(matches) > 0
