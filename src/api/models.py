"""Pydantic models for API request/response in Contract Intelligence System."""

from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """Request model for contract analysis.
    
    Attributes:
        text: Contract text to analyze (if not uploading file).
        include_entities: Whether to include NER results.
        include_clauses: Whether to include clause detection.
        include_risk: Whether to include risk assessment.
    """
    
    text: Optional[str] = Field(default=None, description="Contract text")
    include_entities: bool = Field(default=True, description="Include NER results")
    include_clauses: bool = Field(default=True, description="Include clause detection")
    include_risk: bool = Field(default=True, description="Include risk assessment")
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "text": "This Agreement is entered into as of January 1, 2024...",
                "include_entities": True,
                "include_clauses": True,
                "include_risk": True,
            }
        }


class EntityResponse(BaseModel):
    """Response model for named entity.
    
    Attributes:
        text: Entity text.
        label: Entity type label.
        start: Start position.
        end: End position.
        confidence: Confidence score.
    """
    
    text: str
    label: str
    start: int
    end: int
    confidence: float


class ClauseResponse(BaseModel):
    """Response model for detected clause.
    
    Attributes:
        clause_type: Type of clause.
        text: Clause text snippet.
        confidence: Detection confidence.
        matched_patterns: Patterns that matched.
    """
    
    clause_type: str
    text: str
    confidence: float
    matched_patterns: list[str]


class RiskResponse(BaseModel):
    """Response model for risk assessment.
    
    Attributes:
        overall_score: Overall risk score (0-100).
        category: Risk category (Low, Medium, High).
        breakdown: Detailed breakdown by clause type.
        missing_clauses: List of missing important clauses.
        recommendations: List of recommendations.
    """
    
    overall_score: float
    category: str
    breakdown: dict
    missing_clauses: list[str]
    recommendations: list[str]


class AnalyzeResponse(BaseModel):
    """Complete response model for contract analysis.
    
    Attributes:
        success: Whether analysis was successful.
        extracted_text: Text extracted from document.
        ocr_confidence: OCR confidence score (if applicable).
        entities: List of detected entities.
        clauses: List of detected clauses.
        risk: Risk assessment result.
        error: Error message if analysis failed.
    """
    
    success: bool = True
    extracted_text: Optional[str] = None
    ocr_method: Optional[str] = None
    ocr_confidence: Optional[float] = None
    pages: Optional[int] = None
    entities: list[EntityResponse] = Field(default_factory=list)
    clauses: list[ClauseResponse] = Field(default_factory=list)
    risk: Optional[RiskResponse] = None
    error: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "success": True,
                "extracted_text": "This Agreement is entered into...",
                "ocr_method": "text",
                "ocr_confidence": 100.0,
                "pages": 5,
                "entities": [
                    {"text": "Acme Corp", "label": "ORG", "start": 0, "end": 9, "confidence": 1.0}
                ],
                "clauses": [
                    {"clause_type": "Confidentiality", "text": "...", "confidence": 0.85, "matched_patterns": ["confidential information"]}
                ],
                "risk": {
                    "overall_score": 25.5,
                    "category": "Low",
                    "breakdown": {},
                    "missing_clauses": [],
                    "recommendations": ["Low risk score - standard review process recommended"]
                },
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response model.
    
    Attributes:
        status: Service status (healthy, degraded, unhealthy).
        version: Application version.
        details: Additional health details.
    """
    
    status: str
    version: str
    details: dict = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "details": {
                    "spacy_model": "loaded",
                    "tesseract": "available"
                }
            }
        }
