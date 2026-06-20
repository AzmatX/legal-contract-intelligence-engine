"""Rule-based clause detection for Contract Intelligence System."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClauseMatch:
    """Represents a detected clause match.
    
    Attributes:
        clause_type: Type of clause (e.g., 'Termination', 'Confidentiality').
        text: The matched text snippet.
        confidence: Confidence score (0-1).
        start: Start position in original text.
        end: End position in original text.
        matched_patterns: List of patterns that matched.
    """
    
    clause_type: str
    text: str
    confidence: float
    start: int
    end: int
    matched_patterns: list[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with clause match data.
        """
        return {
            "clause_type": self.clause_type,
            "text": self.text,
            "confidence": self.confidence,
            "start": self.start,
            "end": self.end,
            "matched_patterns": self.matched_patterns,
        }


class ClauseRules:
    """Rule-based clause detection using keyword patterns.
    
    This class defines patterns and keywords for detecting various
    contract clause types. It uses a combination of exact matches,
    phrase matching, and context-aware pattern detection.
    
    Supported clause types:
        - Termination
        - Confidentiality
        - Indemnification
        - Limitation of Liability
        - Governing Law
    """
    
    # Pattern definitions for each clause type
    CLAUSE_PATTERNS = {
        "Termination": {
            "keywords": [
                r"\btermination\b",
                r"\bterminate\b",
                r"\bterminated\b",
                r"\bterminating\b",
                r"\bexpire\b",
                r"\bexpiration\b",
                r"\bend of term\b",
                r"\bnotice period\b",
                r"\bcure period\b",
                r"\bmaterial breach\b",
            ],
            "phrases": [
                r"either party may terminate",
                r"this agreement shall terminate",
                r"termination for convenience",
                r"termination for cause",
                r"immediate termination",
                r"prior written notice",
                r"days? written notice",
            ],
            "weight": 1.0,
        },
        "Confidentiality": {
            "keywords": [
                r"\bconfidential\b",
                r"\bconfidentiality\b",
                r"\bnon[- ]?disclosure\b",
                r"\bproprietary\b",
                r"\btrade secret\b",
                r"\bdisclose\b",
                r"\bdisclosure\b",
            ],
            "phrases": [
                r"confidential information",
                r"shall not disclose",
                r"maintain in confidence",
                r"confidential and proprietary",
                r"publicly available",
                r"obligation of confidentiality",
                r"return of confidential",
            ],
            "weight": 1.0,
        },
        "Indemnification": {
            "keywords": [
                r"\bindemnif[y|ication|iable]\b",
                r"\bhold harmless\b",
                r"\breimburse\b",
                r"\breimbursement\b",
                r"\bdefend\b",
                r"\bdefense\b",
                r"\bliability\b",
                r"\blosses?\b",
                r"\bdamages?\b",
            ],
            "phrases": [
                r"indemnify and hold harmless",
                r"shall indemnify",
                r"indemnification obligation",
                r"third party claims",
                r"arising out of or relating to",
                r"costs and expenses",
                r"legal fees",
            ],
            "weight": 1.0,
        },
        "Limitation of Liability": {
            "keywords": [
                r"\blimitation\b",
                r"\blimit\b",
                r"\blimited\b",
                r"\bexclude\b",
                r"\bexclusion\b",
                r"\bconsequential\b",
                r"\bincidental\b",
                r"\bpunitive\b",
                r"\bspecial damages?\b",
                r"\bcap\b",
            ],
            "phrases": [
                r"limitation of liability",
                r"in no event shall",
                r"total liability shall not exceed",
                r"consequential or incidental damages",
                r"indirect damages",
                r"maximum liability",
                r"aggregate liability",
            ],
            "weight": 1.0,
        },
        "Governing Law": {
            "keywords": [
                r"\bgoverning\b",
                r"\blaw\b",
                r"\bjurisdiction\b",
                r"\bvenue\b",
                r"\bforum\b",
                r"\barbitration\b",
                r"\bdispute\b",
                r"\bstate of\b",
            ],
            "phrases": [
                r"governed by the laws of",
                r"laws of the state of",
                r"subject to the exclusive jurisdiction",
                r"courts of",
                r"venue shall lie in",
                r"arbitration shall be conducted",
                r"binding arbitration",
                r"dispute resolution",
            ],
            "weight": 1.0,
        },
    }
    
    def __init__(self, min_confidence: float = 0.3) -> None:
        """Initialize clause rules engine.
        
        Args:
            min_confidence: Minimum confidence threshold for matches.
        """
        self.min_confidence = min_confidence
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for efficiency."""
        for clause_type, config in self.CLAUSE_PATTERNS.items():
            config["compiled_keywords"] = [
                re.compile(p, re.IGNORECASE) for p in config["keywords"]
            ]
            config["compiled_phrases"] = [
                re.compile(p, re.IGNORECASE) for p in config["phrases"]
            ]
    
    def detect(
        self,
        text: str,
        clause_type: Optional[str] = None,
        context_chars: int = 200,
    ) -> list[ClauseMatch]:
        """Detect clauses in text.
        
        Args:
            text: Input text to analyze.
            clause_type: Specific clause type to detect. If None, detects all.
            context_chars: Number of characters to include around matches.
            
        Returns:
            List of ClauseMatch objects for detected clauses.
        """
        if not text or not text.strip():
            return []
        
        clause_types = (
            [clause_type] if clause_type else list(self.CLAUSE_PATTERNS.keys())
        )
        
        all_matches: list[ClauseMatch] = []
        
        for ct in clause_types:
            if ct not in self.CLAUSE_PATTERNS:
                continue
            
            config = self.CLAUSE_PATTERNS[ct]
            matches = self._find_matches(text, config, context_chars)
            all_matches.extend(matches)
        
        # Sort by confidence descending
        all_matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return all_matches
    
    def _find_matches(
        self,
        text: str,
        config: dict,
        context_chars: int,
    ) -> list[ClauseMatch]:
        """Find matches for a specific clause type.
        
        Args:
            text: Input text to search.
            config: Configuration for the clause type.
            context_chars: Context window size.
            
        Returns:
            List of ClauseMatch objects.
        """
        matches: list[tuple[int, int, float, list[str]]] = []
        
        # Find keyword matches
        for pattern in config["compiled_keywords"]:
            for match in pattern.finditer(text):
                start, end = match.span()
                matches.append((start, end, 0.3 * config["weight"], [match.group()]))
        
        # Find phrase matches (higher weight)
        for pattern in config["compiled_phrases"]:
            for match in pattern.finditer(text):
                start, end = match.span()
                matches.append((start, end, 0.6 * config["weight"], [match.group()]))
        
        # Merge overlapping matches and calculate final confidence
        merged = self._merge_matches(matches, text, context_chars)
        
        # Create ClauseMatch objects
        results: list[ClauseMatch] = []
        for start, end, confidence, patterns in merged:
            if confidence >= self.min_confidence:
                # Cap confidence at 1.0
                confidence = min(confidence, 1.0)
                
                # Extract text snippet
                snippet_start = max(0, start - context_chars // 2)
                snippet_end = min(len(text), end + context_chars // 2)
                snippet = text[snippet_start:snippet_end].strip()
                
                results.append(
                    ClauseMatch(
                        clause_type=config.get("name", ""),
                        text=snippet,
                        confidence=confidence,
                        start=start,
                        end=end,
                        matched_patterns=patterns,
                    )
                )
        
        return results
    
    def _merge_matches(
        self,
        matches: list[tuple[int, int, float, list[str]]],
        text: str,
        context_chars: int,
    ) -> list[tuple[int, int, float, list[str]]]:
        """Merge overlapping or nearby matches.
        
        Args:
            matches: List of match tuples (start, end, confidence, patterns).
            text: Original text.
            context_chars: Context window size.
            
        Returns:
            List of merged match tuples.
        """
        if not matches:
            return []
        
        # Sort by start position
        sorted_matches = sorted(matches, key=lambda m: m[0])
        merged: list[tuple[int, int, float, list[str]]] = [sorted_matches[0]]
        
        for current in sorted_matches[1:]:
            last = merged[-1]
            
            # Check if matches overlap or are close (within context window)
            if current[0] <= last[1] + context_chars:
                # Merge: extend end, sum confidence, combine patterns
                new_end = max(last[1], current[1])
                new_confidence = min(
                    last[2] + current[2] * 0.5,  # Diminishing returns
                    1.0,
                )
                new_patterns = list(set(last[3] + current[3]))
                
                merged[-1] = (last[0], new_end, new_confidence, new_patterns)
            else:
                merged.append(current)
        
        return merged
