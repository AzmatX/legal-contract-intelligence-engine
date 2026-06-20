"""Risk scoring engine for Contract Intelligence System."""

from dataclasses import dataclass, field
from typing import Optional

from src.clause_classification.classifier import ClauseClassifier, ClauseMatch
from src.config import settings
from src.risk_scoring.thresholds import RiskThresholds, RiskCategory
from src.utils.logging_config import logger


@dataclass
class RiskAssessment:
    """Complete risk assessment result.
    
    Attributes:
        overall_score: Overall risk score (0-100).
        category: Risk category (Low, Medium, High).
        breakdown: Detailed breakdown of risk contributors.
        missing_clauses: List of important clauses not found.
        recommendations: List of recommendations based on analysis.
    """
    
    overall_score: float = 0.0
    category: RiskCategory = RiskCategory.LOW
    breakdown: dict = field(default_factory=dict)
    missing_clauses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with risk assessment data.
        """
        return {
            "overall_score": self.overall_score,
            "category": self.category.value,
            "breakdown": self.breakdown,
            "missing_clauses": self.missing_clauses,
            "recommendations": self.recommendations,
        }


class RiskScorer:
    """Calculate risk scores for contracts based on clause analysis.
    
    This class computes an overall risk score based on:
    - Presence/absence of key clauses
    - Confidence levels of detected clauses
    - Specific risk factors in each clause type
    
    Attributes:
        classifier: Clause classifier instance.
        thresholds: Risk threshold configuration.
        clause_weights: Weights for each clause type.
    """
    
    # Clause types and their importance weights
    CLAUSE_WEIGHTS = {
        "Termination": 0.20,
        "Confidentiality": 0.25,
        "Indemnification": 0.25,
        "Limitation of Liability": 0.15,
        "Governing Law": 0.15,
    }
    
    # Base risk scores for missing clauses
    MISSING_CLAUSE_PENALTY = 15.0
    
    def __init__(
        self,
        thresholds: Optional[RiskThresholds] = None,
        min_confidence: float = 0.3,
    ) -> None:
        """Initialize risk scorer.
        
        Args:
            thresholds: Risk threshold configuration. If None, uses defaults.
            min_confidence: Minimum confidence for clause detection.
        """
        self.classifier = ClauseClassifier(min_confidence=min_confidence)
        self.thresholds = thresholds or RiskThresholds(
            low_max=settings.risk_threshold_low,
            medium_max=settings.risk_threshold_medium,
        )
        logger.info("RiskScorer initialized")
    
    def assess(self, text: str) -> RiskAssessment:
        """Perform complete risk assessment on contract text.
        
        Args:
            text: Contract text to analyze.
            
        Returns:
            RiskAssessment with score, category, and details.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for risk assessment")
            return RiskAssessment(
                overall_score=100.0,  # Maximum risk for empty contract
                category=RiskCategory.HIGH,
                recommendations=["Provide valid contract text for analysis"],
            )
        
        try:
            # Detect clauses
            matches = self.classifier.classify(text)
            
            # Calculate score
            score, breakdown = self._calculate_score(matches)
            
            # Determine category
            category = self.thresholds.get_category(score)
            
            # Identify missing clauses
            missing = self._identify_missing_clauses(matches)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                matches, missing, score
            )
            
            assessment = RiskAssessment(
                overall_score=round(score, 2),
                category=category,
                breakdown=breakdown,
                missing_clauses=missing,
                recommendations=recommendations,
            )
            
            logger.info(
                f"Risk assessment complete: score={score}, category={category.value}"
            )
            return assessment
            
        except Exception as e:
            logger.exception(f"Error in risk assessment: {e}")
            return RiskAssessment(
                overall_score=50.0,  # Default to medium risk on error
                category=RiskCategory.MEDIUM,
                recommendations=["Error during analysis - manual review recommended"],
            )
    
    def _calculate_score(
        self,
        matches: list[ClauseMatch],
    ) -> tuple[float, dict]:
        """Calculate risk score from detected clauses.
        
        Args:
            matches: List of detected clause matches.
            
        Returns:
            Tuple of (score, breakdown dict).
        """
        score = 0.0
        breakdown: dict = {}
        
        # Group matches by clause type
        by_type: dict[str, list[ClauseMatch]] = {}
        for match in matches:
            clause_type = match.clause_type
            if clause_type not in by_type:
                by_type[clause_type] = []
            by_type[clause_type].append(match)
        
        # Calculate contribution from each clause type
        for clause_type, weight in self.CLAUSE_WEIGHTS.items():
            type_matches = by_type.get(clause_type, [])
            
            if not type_matches:
                # Missing clause adds to risk
                type_score = self.MISSING_CLAUSE_PENALTY * weight
                breakdown[clause_type] = {
                    "present": False,
                    "score_contribution": round(type_score, 2),
                    "confidence": 0.0,
                }
            else:
                # Use best match confidence
                best_match = max(type_matches, key=lambda m: m.confidence)
                
                # Higher confidence = lower risk for that clause
                # Invert confidence: (1 - confidence) gives risk portion
                confidence_risk = (1 - best_match.confidence) * 100
                
                # Scale by weight
                type_score = confidence_risk * weight * 0.5  # Reduce impact if present
                
                breakdown[clause_type] = {
                    "present": True,
                    "score_contribution": round(type_score, 2),
                    "confidence": round(best_match.confidence, 2),
                    "match_count": len(type_matches),
                }
            
            score += type_score
        
        # Cap score at 100
        score = min(score, 100.0)
        
        return score, breakdown
    
    def _identify_missing_clauses(
        self,
        matches: list[ClauseMatch],
    ) -> list[str]:
        """Identify important clauses that are missing.
        
        Args:
            matches: List of detected clause matches.
            
        Returns:
            List of missing clause type names.
        """
        present_types = {m.clause_type for m in matches}
        missing = []
        
        for clause_type in self.CLAUSE_WEIGHTS.keys():
            if clause_type not in present_types:
                missing.append(clause_type)
        
        return missing
    
    def _generate_recommendations(
        self,
        matches: list[ClauseMatch],
        missing: list[str],
        score: float,
    ) -> list[str]:
        """Generate recommendations based on analysis.
        
        Args:
            matches: List of detected clause matches.
            missing: List of missing clause types.
            score: Overall risk score.
            
        Returns:
            List of recommendation strings.
        """
        recommendations: list[str] = []
        
        # Recommendations for missing clauses
        for clause_type in missing:
            recommendations.append(
                f"Add a clear '{clause_type}' clause to the contract"
            )
        
        # Recommendations for low-confidence matches
        for match in matches:
            if match.confidence < 0.5:
                recommendations.append(
                    f"Review '{match.clause_type}' clause - detection confidence is low"
                )
        
        # General recommendations based on score
        if score > 70:
            recommendations.append(
                "High risk score - recommend thorough legal review before signing"
            )
        elif score > 40:
            recommendations.append(
                "Medium risk score - consider negotiating key terms"
            )
        else:
            recommendations.append(
                "Low risk score - standard review process recommended"
            )
        
        return recommendations
