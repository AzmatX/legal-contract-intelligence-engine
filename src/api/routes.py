"""API routes for Contract Intelligence System."""

import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional

from src.api.models import (
    AnalyzeResponse,
    HealthResponse,
    EntityResponse,
    ClauseResponse,
    RiskResponse,
)
from src.ocr.pdf_processor import PDFProcessor, OCRResult
from src.ner.entity_extractor import EntityExtractor
from src.clause_classification.classifier import ClauseClassifier
from src.risk_scoring.scorer import RiskScorer, RiskAssessment
from src.utils.logging_config import logger
from src.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Check API health status.
    
    Returns:
        HealthResponse with status and version information.
    """
    details = {
        "spacy_model": "loaded",
        "tesseract": "checking...",
    }
    
    # Check Tesseract availability
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        details["tesseract"] = "available"
    except Exception:
        details["tesseract"] = "not available"
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        details=details,
    )


@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_contract(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    include_entities: bool = Form(True),
    include_clauses: bool = Form(True),
    include_risk: bool = Form(True),
    background_tasks: BackgroundTasks = None,
) -> AnalyzeResponse:
    """Analyze a contract document.
    
    Accepts either a file upload (PDF) or raw text. Performs:
    - Text extraction (OCR if needed)
    - Named Entity Recognition
    - Clause classification
    - Risk scoring
    
    Args:
        file: PDF file to analyze.
        text: Raw contract text (alternative to file).
        include_entities: Whether to include NER results.
        include_clauses: Whether to include clause detection.
        include_risk: Whether to include risk assessment.
        background_tasks: FastAPI background tasks.
        
    Returns:
        AnalyzeResponse with analysis results.
    """
    try:
        extracted_text = ""
        ocr_result: Optional[OCRResult] = None
        
        # Extract text from file or use provided text
        if file:
            logger.info(f"Processing uploaded file: {file.filename}")
            
            # Read file content
            contents = await file.read()
            
            # Process with OCR module
            processor = PDFProcessor()
            ocr_result = processor.process_bytes(contents)
            
            if ocr_result.error:
                return AnalyzeResponse(
                    success=False,
                    error=f"OCR processing failed: {ocr_result.error}",
                )
            
            extracted_text = ocr_result.text
            
        elif text:
            logger.info("Processing provided text")
            extracted_text = text
            ocr_result = OCRResult(
                text=text,
                confidence=100.0,
                method="direct",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'file' or 'text' must be provided",
            )
        
        if not extracted_text or not extracted_text.strip():
            return AnalyzeResponse(
                success=False,
                error="No text could be extracted from the document",
            )
        
        # Initialize processors
        entity_extractor = EntityExtractor() if include_entities else None
        clause_classifier = ClauseClassifier() if include_clauses else None
        risk_scorer = RiskScorer() if include_risk else None
        
        # Perform analysis
        entities = []
        clauses = []
        risk = None
        
        if include_entities and entity_extractor:
            ner_entities = entity_extractor.extract(extracted_text)
            entities = [
                EntityResponse(
                    text=e.text,
                    label=e.label,
                    start=e.start,
                    end=e.end,
                    confidence=e.confidence,
                )
                for e in ner_entities
            ]
            logger.info(f"Extracted {len(entities)} entities")
        
        if include_clauses and clause_classifier:
            detected_clauses = clause_classifier.classify(extracted_text)
            clauses = [
                ClauseResponse(
                    clause_type=c.clause_type,
                    text=c.text,
                    confidence=c.confidence,
                    matched_patterns=c.matched_patterns,
                )
                for c in detected_clauses
            ]
            logger.info(f"Detected {len(clauses)} clauses")
        
        if include_risk and risk_scorer:
            assessment: RiskAssessment = risk_scorer.assess(extracted_text)
            risk = RiskResponse(
                overall_score=assessment.overall_score,
                category=assessment.category.value,
                breakdown=assessment.breakdown,
                missing_clauses=assessment.missing_clauses,
                recommendations=assessment.recommendations,
            )
            logger.info(f"Risk score: {assessment.overall_score}")
        
        return AnalyzeResponse(
            success=True,
            extracted_text=extracted_text[:5000],  # Limit response size
            ocr_method=ocr_result.method if ocr_result else None,
            ocr_confidence=ocr_result.confidence if ocr_result else None,
            pages=ocr_result.pages if ocr_result else None,
            entities=entities,
            clauses=clauses,
            risk=risk,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error analyzing contract: {e}")
        return AnalyzeResponse(
            success=False,
            error=f"Analysis failed: {str(e)}",
        )


@router.post("/analyze/text", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_text(
    text: str,
    include_entities: bool = True,
    include_clauses: bool = True,
    include_risk: bool = True,
) -> AnalyzeResponse:
    """Analyze contract text directly.
    
    This endpoint accepts raw text instead of a file upload.
    
    Args:
        text: Contract text to analyze.
        include_entities: Whether to include NER results.
        include_clauses: Whether to include clause detection.
        include_risk: Whether to include risk assessment.
        
    Returns:
        AnalyzeResponse with analysis results.
    """
    return await analyze_contract(
        file=None,
        text=text,
        include_entities=include_entities,
        include_clauses=include_clauses,
        include_risk=include_risk,
    )
