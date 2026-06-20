"""spaCy-based Named Entity Recognition for Contract Intelligence System."""

from dataclasses import dataclass
from typing import Optional

import spacy
from spacy.tokens import Doc

from src.config import settings
from src.utils.logging_config import logger


@dataclass
class Entity:
    """Represents a named entity extracted from text.
    
    Attributes:
        text: The entity text.
        label: Entity type label (e.g., ORG, DATE, MONEY).
        start: Start character index in the original text.
        end: End character index in the original text.
        confidence: Confidence score (0-1).
    """
    
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with entity data.
        """
        return {
            "text": self.text,
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }


class SpacyNER:
    """Named Entity Recognition using spaCy.
    
    This class wraps spaCy's NER functionality to extract entities
    from contract text. It supports multiple entity types relevant
    to legal documents.
    
    Attributes:
        model_name: Name of the spaCy model to use.
        nlp: Loaded spaCy language model.
        target_labels: Entity labels to extract.
    """
    
    TARGET_LABELS = {"ORG", "DATE", "MONEY", "PERSON", "GPE", "LAW", "TIME", "PERCENT"}
    
    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize spaCy NER processor.
        
        Args:
            model_name: Name of spaCy model. If None, uses settings default.
        """
        self.model_name = model_name or settings.spacy_model
        
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.warning(
                f"Model {self.model_name} not found. Downloading..."
            )
            spacy.cli.download(self.model_name)
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Downloaded and loaded spaCy model: {self.model_name}")
        
        # Disable unnecessary pipeline components for speed
        self.nlp.disable_pipes("parser")
    
    def extract(self, text: str) -> list[Entity]:
        """Extract named entities from text.
        
        Args:
            text: Input text to process.
            
        Returns:
            List of extracted Entity objects.
        """
        if not text or not text.strip():
            return []
        
        try:
            doc: Doc = self.nlp(text)
            entities: list[Entity] = []
            
            for ent in doc.ents:
                if ent.label_ in self.TARGET_LABELS:
                    entity = Entity(
                        text=ent.text,
                        label=ent.label_,
                        start=ent.start_char,
                        end=ent.end_char,
                    )
                    entities.append(entity)
            
            # Post-process to merge overlapping entities
            entities = self._merge_entities(entities)
            
            logger.debug(f"Extracted {len(entities)} entities")
            return entities
            
        except Exception as e:
            logger.exception(f"Error extracting entities: {e}")
            return []
    
    def _merge_entities(self, entities: list[Entity]) -> list[Entity]:
        """Merge overlapping or adjacent entities of the same type.
        
        Args:
            entities: List of entities to merge.
            
        Returns:
            List of merged entities.
        """
        if not entities:
            return []
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.start)
        merged: list[Entity] = [sorted_entities[0]]
        
        for current in sorted_entities[1:]:
            last = merged[-1]
            
            # Check if entities overlap or are adjacent and have same label
            if (
                current.label_ == last.label_
                and current.start <= last.end + 1
            ):
                # Merge entities
                merged_text = last.text + " " + current.text
                merged[-1] = Entity(
                    text=merged_text.strip(),
                    label=last.label_,
                    start=last.start,
                    end=max(last.end, current.end),
                )
            else:
                merged.append(current)
        
        return merged
    
    def get_entity_counts(self, text: str) -> dict[str, int]:
        """Get count of entities by label.
        
        Args:
            text: Input text to process.
            
        Returns:
            Dictionary mapping entity labels to counts.
        """
        entities = self.extract(text)
        counts: dict[str, int] = {}
        
        for entity in entities:
            counts[entity.label_] = counts.get(entity.label_, 0) + 1
        
        return counts
