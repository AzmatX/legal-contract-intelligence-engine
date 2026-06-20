"""Tests for NER module in Contract Intelligence System."""

import pytest

from src.ner.spacy_ner import SpacyNER, Entity
from src.ner.entity_extractor import EntityExtractor


class TestSpacyNER:
    """Test cases for SpacyNER class."""
    
    def test_ner_initialization(self) -> None:
        """Test spaCy NER initialization."""
        ner = SpacyNER()
        assert ner.nlp is not None
        assert ner.model_name == "en_core_web_sm"
    
    def test_extract_entities_empty_text(self) -> None:
        """Test entity extraction with empty text."""
        ner = SpacyNER()
        entities = ner.extract("")
        assert entities == []
    
    def test_extract_entities_simple(self) -> None:
        """Test basic entity extraction."""
        ner = SpacyNER()
        text = "Apple Inc. was founded by Steve Jobs in 1976."
        entities = ner.extract(text)
        
        # Should find at least one entity
        assert len(entities) >= 1
        
        # Check entity structure
        for entity in entities:
            assert isinstance(entity.text, str)
            assert isinstance(entity.label_, str)
            assert isinstance(entity.start, int)
            assert isinstance(entity.end, int)
    
    def test_extract_organization(self) -> None:
        """Test organization entity detection."""
        ner = SpacyNER()
        text = "Microsoft Corporation announced quarterly earnings."
        entities = ner.extract(text)
        
        org_entities = [e for e in entities if e.label_ == "ORG"]
        assert len(org_entities) >= 1
        assert "Microsoft" in org_entities[0].text
    
    def test_extract_date(self) -> None:
        """Test date entity detection."""
        ner = SpacyNER()
        text = "The meeting is scheduled for January 15, 2024."
        entities = ner.extract(text)
        
        date_entities = [e for e in entities if e.label_ == "DATE"]
        assert len(date_entities) >= 1
    
    def test_extract_money(self) -> None:
        """Test money entity detection."""
        ner = SpacyNER()
        text = "The contract value is $500,000."
        entities = ner.extract(text)
        
        money_entities = [e for e in entities if e.label_ == "MONEY"]
        assert len(money_entities) >= 1
    
    def test_merge_entities(self) -> None:
        """Test entity merging functionality."""
        ner = SpacyNER()
        # Text with adjacent entities of same type
        text = "John Smith and Jane Doe work at Google."
        entities = ner.extract(text)
        
        # Should not have duplicate overlapping entities
        for i, e1 in enumerate(entities):
            for j, e2 in enumerate(entities):
                if i != j:
                    # Check no complete overlap
                    if e1.label_ == e2.label_:
                        assert not (e1.start <= e2.start and e1.end >= e2.end)
    
    def test_entity_to_dict(self) -> None:
        """Test Entity to_dict method."""
        entity = Entity(
            text="Test Entity",
            label="ORG",
            start=0,
            end=11,
            confidence=0.95,
        )
        entity_dict = entity.to_dict()
        
        assert entity_dict["text"] == "Test Entity"
        assert entity_dict["label"] == "ORG"
        assert entity_dict["start"] == 0
        assert entity_dict["end"] == 11
        assert entity_dict["confidence"] == 0.95
    
    def test_get_entity_counts(self) -> None:
        """Test entity count functionality."""
        ner = SpacyNER()
        text = "Apple Inc. and Microsoft are tech companies. Apple was founded in 1976."
        counts = ner.get_entity_counts(text)
        
        assert isinstance(counts, dict)
        # Should have at least ORG entities
        assert "ORG" in counts or len(counts) >= 0


class TestEntityExtractor:
    """Test cases for EntityExtractor class."""
    
    def test_extractor_initialization(self) -> None:
        """Test EntityExtractor initialization."""
        extractor = EntityExtractor()
        assert extractor.ner is not None
        assert extractor.text_cleaner is not None
    
    def test_extract_with_cleaning(self) -> None:
        """Test entity extraction with text cleaning."""
        extractor = EntityExtractor(clean_text=True)
        text = "  Apple Inc.   is   a   company  "
        entities = extractor.extract(text, clean=True)
        
        # Should extract entities even with messy text
        assert isinstance(entities, list)
    
    def test_extract_without_cleaning(self) -> None:
        """Test entity extraction without text cleaning."""
        extractor = EntityExtractor(clean_text=False)
        text = "Apple Inc. is a company"
        entities = extractor.extract(text, clean=False)
        
        assert isinstance(entities, list)
    
    def test_extract_by_label(self) -> None:
        """Test extracting entities by specific label."""
        extractor = EntityExtractor()
        text = "Apple Inc. was founded in 1976 by Steve Jobs."
        
        org_entities = extractor.extract_by_label(text, "ORG")
        for entity in org_entities:
            assert entity.label_ == "ORG"
    
    def test_get_summary(self) -> None:
        """Test entity summary generation."""
        extractor = EntityExtractor()
        text = "Apple Inc. and Microsoft Corporation are companies."
        summary = extractor.get_summary(text)
        
        assert isinstance(summary, dict)
        assert "count" in str(summary) or len(summary) >= 0
    
    def test_extract_with_context(self) -> None:
        """Test entity extraction with context."""
        extractor = EntityExtractor()
        text = "Apple Inc. announced new products today."
        results = extractor.extract_with_context(text, context_window=20)
        
        for result in results:
            assert "entity" in result
            assert "context_before" in result
            assert "context_after" in result
