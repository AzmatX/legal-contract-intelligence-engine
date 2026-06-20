"""Configuration module for Contract Intelligence System."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Attributes:
        app_name: Name of the application
        app_version: Version of the application
        debug: Debug mode flag
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
        # OCR Settings
        tesseract_cmd: Path to Tesseract executable
        ocr_lang: OCR language(s)
        ocr_psm: Page segmentation mode for Tesseract
        
        # NER Settings
        spacy_model: spaCy model name to use
        
        # Risk Scoring Settings
        risk_threshold_low: Upper bound for Low risk category
        risk_threshold_medium: Upper bound for Medium risk category
        
        # API Settings
        api_host: Host to bind the API server
        api_port: Port to bind the API server
        api_workers: Number of worker processes
        
        # Paths
        data_dir: Directory for data files
        temp_dir: Directory for temporary files
    """
    
    # App Settings
    app_name: str = Field(default="Contract Intelligence Engine", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # OCR Settings
    tesseract_cmd: Optional[str] = Field(default=None, description="Path to Tesseract executable")
    ocr_lang: str = Field(default="eng", description="OCR language(s)")
    ocr_psm: int = Field(default=3, description="Page segmentation mode for Tesseract")
    
    # NER Settings
    spacy_model: str = Field(default="en_core_web_sm", description="spaCy model name")
    
    # Risk Scoring Settings
    risk_threshold_low: float = Field(default=30.0, description="Upper bound for Low risk")
    risk_threshold_medium: float = Field(default=60.0, description="Upper bound for Medium risk")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of workers")
    
    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent, description="Base directory")
    data_dir: Path = Field(default=Path(__file__).parent.parent / "data", description="Data directory")
    temp_dir: Path = Field(default=Path(__file__).parent.parent / "temp", description="Temp directory")
    
    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
