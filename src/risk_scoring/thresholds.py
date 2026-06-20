"""Risk thresholds and categories for Contract Intelligence System."""

from dataclasses import dataclass
from enum import Enum


class RiskCategory(str, Enum):
    """Risk category enumeration.
    
    Categories:
        LOW: Low risk (0-30)
        MEDIUM: Medium risk (31-60)
        HIGH: High risk (61-100)
    """
    
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class RiskThresholds:
    """Configurable risk thresholds.
    
    Attributes:
        low_max: Maximum score for Low category (inclusive).
        medium_max: Maximum score for Medium category (inclusive).
        # Scores above medium_max are High risk.
    """
    
    low_max: float = 30.0
    medium_max: float = 60.0
    
    def get_category(self, score: float) -> RiskCategory:
        """Get risk category for a score.
        
        Args:
            score: Risk score (0-100).
            
        Returns:
            RiskCategory enum value.
        """
        if score <= self.low_max:
            return RiskCategory.LOW
        elif score <= self.medium_max:
            return RiskCategory.MEDIUM
        else:
            return RiskCategory.HIGH
    
    def validate(self) -> bool:
        """Validate threshold configuration.
        
        Returns:
            True if thresholds are valid.
            
        Raises:
            ValueError: If thresholds are invalid.
        """
        if not (0 <= self.low_max <= 100):
            raise ValueError("low_max must be between 0 and 100")
        if not (self.low_max < self.medium_max <= 100):
            raise ValueError("medium_max must be greater than low_max and <= 100")
        return True
