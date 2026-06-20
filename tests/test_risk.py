"""Tests for risk scoring module in Contract Intelligence System."""

import pytest

from src.risk_scoring.scorer import RiskScorer, RiskAssessment
from src.risk_scoring.thresholds import RiskThresholds, RiskCategory


class TestRiskThresholds:
    """Test cases for RiskThresholds class."""
    
    def test_default_thresholds(self) -> None:
        """Test default threshold values."""
        thresholds = RiskThresholds()
        assert thresholds.low_max == 30.0
        assert thresholds.medium_max == 60.0
    
    def test_get_category_low(self) -> None:
        """Test low risk category."""
        thresholds = RiskThresholds()
        assert thresholds.get_category(25.0) == RiskCategory.LOW
        assert thresholds.get_category(30.0) == RiskCategory.LOW
    
    def test_get_category_medium(self) -> None:
        """Test medium risk category."""
        thresholds = RiskThresholds()
        assert thresholds.get_category(45.0) == RiskCategory.MEDIUM
        assert thresholds.get_category(60.0) == RiskCategory.MEDIUM
    
    def test_get_category_high(self) -> None:
        """Test high risk category."""
        thresholds = RiskThresholds()
        assert thresholds.get_category(75.0) == RiskCategory.HIGH
        assert thresholds.get_category(100.0) == RiskCategory.HIGH
    
    def test_validate_valid(self) -> None:
        """Test validation with valid thresholds."""
        thresholds = RiskThresholds(low_max=25.0, medium_max=50.0)
        assert thresholds.validate() is True
    
    def test_validate_invalid(self) -> None:
        """Test validation with invalid thresholds."""
        thresholds = RiskThresholds(low_max=50.0, medium_max=30.0)
        with pytest.raises(ValueError):
            thresholds.validate()


class TestRiskAssessment:
    """Test cases for RiskAssessment class."""
    
    def test_assessment_to_dict(self) -> None:
        """Test RiskAssessment to_dict method."""
        assessment = RiskAssessment(
            overall_score=45.5,
            category=RiskCategory.MEDIUM,
            breakdown={"Termination": {"present": True}},
            missing_clauses=["Confidentiality"],
            recommendations=["Review contract"],
        )
        result = assessment.to_dict()
        
        assert result["overall_score"] == 45.5
        assert result["category"] == "Medium"
        assert "Termination" in result["breakdown"]
        assert "Confidentiality" in result["missing_clauses"]


class TestRiskScorer:
    """Test cases for RiskScorer class."""
    
    def test_scorer_initialization(self) -> None:
        """Test RiskScorer initialization."""
        scorer = RiskScorer()
        assert scorer.classifier is not None
        assert scorer.thresholds is not None
    
    def test_assess_empty_text(self) -> None:
        """Test risk assessment with empty text."""
        scorer = RiskScorer()
        assessment = scorer.assess("")
        
        assert assessment.overall_score == 100.0
        assert assessment.category == RiskCategory.HIGH
        assert len(assessment.recommendations) > 0
    
    def test_assess_sample_contract(self, sample_contract_text: str) -> None:
        """Test risk assessment on sample contract."""
        scorer = RiskScorer()
        assessment = scorer.assess(sample_contract_text)
        
        # Should produce a valid assessment
        assert 0 <= assessment.overall_score <= 100
        assert isinstance(assessment.category, RiskCategory)
        assert isinstance(assessment.breakdown, dict)
    
    def test_assess_with_all_clauses(self) -> None:
        """Test assessment with comprehensive contract text."""
        scorer = RiskScorer()
        text = """
        This agreement may be terminated by either party.
        All confidential information shall be protected.
        Provider agrees to indemnify Company.
        Liability is limited to contract value.
        This agreement is governed by California law.
        """
        assessment = scorer.assess(text)
        
        # With all clauses present, risk should be lower
        assert assessment.overall_score < 80
    
    def test_assess_missing_clauses(self) -> None:
        """Test assessment with missing clauses."""
        scorer = RiskScorer()
        text = "This is a simple agreement without specific clauses."
        assessment = scorer.assess(text)
        
        # Missing clauses should increase risk
        assert len(assessment.missing_clauses) > 0
        assert assessment.overall_score > 30
    
    def test_calculate_score(self) -> None:
        """Test score calculation logic."""
        scorer = RiskScorer()
        matches = scorer.classifier.classify("Terminate this agreement now")
        
        score, breakdown = scorer._calculate_score(matches)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert isinstance(breakdown, dict)
    
    def test_generate_recommendations(self) -> None:
        """Test recommendation generation."""
        scorer = RiskScorer()
        matches = scorer.classifier.classify("Sample text")
        
        recommendations = scorer._generate_recommendations(
            matches, ["MissingClause"], 50.0
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
