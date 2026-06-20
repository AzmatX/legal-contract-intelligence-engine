"""Entity extraction pipeline for Contract Intelligence System."""

from typing import Optional

from src.ner.spacy_ner import SpacyNER, Entity
from src.ocr.text_cleaner import TextCleaner
from src.utils.logging_config import logger


class EntityExtractor:
    """High-level entity extraction pipeline.
    
    This class orchestrates the full entity extraction process,
    including text cleaning and NER processing.
    
    Attributes:
        ner: spaCy NER processor.
        text_cleaner: Text cleaning utility.
    """
    
    def __init__(
        self,
        spacy_model: Optional[str] = None,
        clean_text: bool = True,
    ) -> None:
        """Initialize entity extractor.
        
        Args:
            spacy_model: Name of spaCy model to use.
            clean_text: Whether to clean text before NER.
        """
        self.ner = SpacyNER(model_name=spacy_model)
        self.text_cleaner = TextCleaner() if clean_text else None
        logger.info("EntityExtractor initialized")
    
    def extract(self, text: str, clean: bool = True) -> list[Entity]:
        """Extract entities from text.
        
        Args:
            text: Input text to process.
            clean: Whether to clean text before extraction.
            
        Returns:
            List of extracted Entity objects.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for entity extraction")
            return []
        
        try:
            # Clean text if requested
            if clean and self.text_cleaner:
                text = self.text_cleaner.clean_for_nlp(text)
            
            # Extract entities
            entities = self.ner.extract(text)
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.exception(f"Error in entity extraction: {e}")
            return []
    
    def extract_with_context(
        self,
        text: str,
        context_window: int = 50,
    ) -> list[dict]:
        """Extract entities with surrounding context.
        
        Args:
            text: Input text to process.
            context_window: Number of characters to include before and after.
            
        Returns:
            List of dictionaries with entity and context.
        """
        entities = self.extract(text)
        results: list[dict] = []
        
        for entity in entities:
            start = max(0, entity.start - context_window)
            end = min(len(text), entity.end + context_window)
            
            context_before = text[start:entity.start].strip()
            context_after = text[entity.end:end].strip()
            
            results.append({
                "entity": entity.to_dict(),
                "context_before": context_before,
                "context_after": context_after,
            })
        
        return results
    
    def extract_by_label(
        self,
        text: str,
        label: str,
    ) -> list[Entity]:
        """Extract entities of a specific label.
        
        Args:
            text: Input text to process.
            label: Entity label to filter by (e.g., 'ORG', 'DATE').
            
        Returns:
            List of matching Entity objects.
        """
        entities = self.extract(text)
        return [e for e in entities if e.label_ == label]
    
    def get_summary(self, text: str) -> dict:
        """Get a summary of entities by type.
        
        Args:
            text: Input text to process.
            
        Returns:
            Dictionary with entity counts and samples.
        """
        entities = self.extract(text)
        
        summary: dict[str, dict] = {}
        for entity in entities:
            if entity.label_ not in summary:
                summary[entity.label_] = {
                    "count": 0,
                    "samples": [],
                }
            
            summary[entity.label_]["count"] += 1
            
            # Keep up to 5 samples per label
            if len(summary[entity.label_]["samples"]) < 5:
                summary[entity.label_]["samples"].append(entity.text)
        
        return summary
