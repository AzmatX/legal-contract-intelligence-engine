"""Tests for clause classification module in Contract Intelligence System."""

import pytest

from src.clause_classification.rules import ClauseRules, ClauseMatch
from src.clause_classification.classifier import ClauseClassifier


class TestClauseRules:
    """Test cases for ClauseRules class."""
    
    def test_rules_initialization(self) -> None:
        """Test ClauseRules initialization."""
        rules = ClauseRules()
        assert rules.min_confidence == 0.3
        assert "Termination" in rules.CLAUSE_PATTERNS
    
    def test_detect_termination_clause(self) -> None:
        """Test termination clause detection."""
        rules = ClauseRules()
        text = "Either party may terminate this agreement with 30 days written notice."
        matches = rules.detect(text, clause_type="Termination")
        
        assert len(matches) >= 1
        assert any("terminate" in m.text.lower() for m in matches)
    
    def test_detect_confidentiality_clause(self) -> None:
        """Test confidentiality clause detection."""
        rules = ClauseRules()
        text = "Both parties agree to maintain all confidential information in strict confidence."
        matches = rules.detect(text, clause_type="Confidentiality")
        
        assert len(matches) >= 1
        assert any("confidential" in m.text.lower() for m in matches)
    
    def test_detect_indemnification_clause(self) -> None:
        """Test indemnification clause detection."""
        rules = ClauseRules()
        text = "Provider shall indemnify and hold harmless Company from any third party claims."
        matches = rules.detect(text, clause_type="Indemnification")
        
        assert len(matches) >= 1
        assert any("indemnify" in m.text.lower() for m in matches)
    
    def test_detect_limitation_of_liability(self) -> None:
        """Test limitation of liability detection."""
        rules = ClauseRules()
        text = "In no event shall either party's total liability exceed $100,000."
        matches = rules.detect(text, clause_type="Limitation of Liability")
        
        assert len(matches) >= 1
        assert any("liability" in m.text.lower() for m in matches)
    
    def test_detect_governing_law(self) -> None:
        """Test governing law clause detection."""
        rules = ClauseRules()
        text = "This agreement shall be governed by the laws of the State of New York."
        matches = rules.detect(text, clause_type="Governing Law")
        
        assert len(matches) >= 1
        assert any("governed" in m.text.lower() or "laws" in m.text.lower() for m in matches)
    
    def test_detect_all_clauses(self) -> None:
        """Test detecting all clause types at once."""
        rules = ClauseRules()
        text = """
        Either party may terminate with notice.
        Confidential information shall not be disclosed.
        Provider shall indemnify Company.
        Liability is limited to $100,000.
        This agreement is governed by New York law.
        """
        matches = rules.detect(text)
        
        # Should detect multiple clause types
        clause_types = {m.clause_type for m in matches}
        assert len(clause_types) >= 3
    
    def test_empty_text(self) -> None:
        """Test detection with empty text."""
        rules = ClauseRules()
        matches = rules.detect("")
        assert matches == []
    
    def test_clause_match_to_dict(self) -> None:
        """Test ClauseMatch to_dict method."""
        match = ClauseMatch(
            clause_type="Termination",
            text="Sample termination clause",
            confidence=0.85,
            start=0,
            end=25,
            matched_patterns=["terminate"],
        )
        match_dict = match.to_dict()
        
        assert match_dict["clause_type"] == "Termination"
        assert match_dict["confidence"] == 0.85
        assert "terminate" in match_dict["matched_patterns"]


class TestClauseClassifier:
    """Test cases for ClauseClassifier class."""
    
    def test_classifier_initialization(self) -> None:
        """Test ClauseClassifier initialization."""
        classifier = ClauseClassifier()
        assert classifier.rules_engine is not None
        assert classifier.text_cleaner is not None
    
    def test_classify_sample_contract(self, sample_contract_text: str) -> None:
        """Test classification on sample contract."""
        classifier = ClauseClassifier()
        matches = classifier.classify(sample_contract_text)
        
        # Should detect multiple clauses
        assert len(matches) >= 3
        
        # Check structure
        for match in matches:
            assert isinstance(match.clause_type, str)
            assert 0 <= match.confidence <= 1
    
    def test_has_clause(self, sample_contract_text: str) -> None:
        """Test has_clause method."""
        classifier = ClauseClassifier()
        
        assert classifier.has_clause(sample_contract_text, "Termination")
        assert classifier.has_clause(sample_contract_text, "Confidentiality")
        assert classifier.has_clause(sample_contract_text, "Indemnification")
    
    def test_get_clause_summary(self, sample_contract_text: str) -> None:
        """Test clause summary generation."""
        classifier = ClauseClassifier()
        summary = classifier.get_clause_summary(sample_contract_text)
        
        assert isinstance(summary, dict)
        assert "total_clauses" in summary
        assert "by_type" in summary
    
    def test_classify_by_type(self, sample_contract_text: str) -> None:
        """Test classification by specific type."""
        classifier = ClauseClassifier()
        
        termination_clauses = classifier.classify_by_type(
            sample_contract_text, "Termination"
        )
        
        for clause in termination_clauses:
            assert clause.clause_type == "Termination"
    
    def test_unsupported_clause_type(self) -> None:
        """Test with unsupported clause type."""
        classifier = ClauseClassifier()
        matches = classifier.classify_by_type("Some text", "UnsupportedType")
        assert matches == []
