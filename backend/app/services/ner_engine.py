# =============================================================================
# NAMED ENTITY RECOGNITION ENGINE
# =============================================================================
# Provides NER capabilities using spaCy with Sri Lankan context customization.
# Recognizes persons, locations, organizations with local adaptations.
# =============================================================================

"""
NER Engine Service

This module provides Named Entity Recognition using spaCy with custom
adaptations for Sri Lankan context:
- Custom Sri Lankan city recognition (Colombo, Kandy, Galle, etc.)
- Common Sri Lankan family names (Perera, Silva, Fernando, etc.)
- Sri Lankan organizations (Dialog, Mobitel, BOC, etc.)

The engine uses spaCy's en_core_web_sm model by default, with entity
ruler additions for Sri Lankan entities.

Example Usage:
    engine = NEREngine()
    results = engine.extract_entities("John Perera works at Dialog in Colombo")
    # Returns: {"persons": ["John Perera"], "locations": ["Colombo"], "organizations": ["Dialog"]}
"""

import spacy
from spacy.language import Language
from spacy.tokens import Doc
from typing import List, Dict, Optional
from app.core.config import settings


# =============================================================================
# GLOBAL NLP MODEL CACHE
# =============================================================================
# Cache the loaded model to avoid reloading on every request
# This significantly improves performance
# =============================================================================

_nlp_model: Optional[Language] = None


def preload_nlp_model() -> Language:
    """
    Preload and cache the spaCy NLP model.
    
    This function is called during application startup to ensure
    the model is loaded before handling requests, avoiding cold
    start delays.
    
    Returns:
        Language: Loaded spaCy language model
    
    Raises:
        OSError: If the spaCy model is not installed
    """
    global _nlp_model
    
    if _nlp_model is None:
        try:
            # Load the spaCy model
            _nlp_model = spacy.load(settings.SPACY_MODEL)
            
            # Add custom entity patterns for Sri Lankan context
            _add_sri_lankan_entities(_nlp_model)
            
            print(f"✓ Loaded spaCy model: {settings.SPACY_MODEL}")
        except OSError:
            # Model not installed - provide helpful error message
            raise OSError(
                f"spaCy model '{settings.SPACY_MODEL}' not found. "
                f"Install it with: python -m spacy download {settings.SPACY_MODEL}"
            )
    
    return _nlp_model


def _add_sri_lankan_entities(nlp: Language) -> None:
    """
    Add custom entity patterns for Sri Lankan recognition.
    
    Creates an EntityRuler with patterns for:
    - Sri Lankan cities as LOC (Location)
    - Sri Lankan family names as PERSON
    - Sri Lankan organizations as ORG
    
    Args:
        nlp: spaCy Language model to add patterns to
    """
    # Create entity ruler with patterns
    # overwrite_ents=False allows custom patterns to supplement, not replace
    ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": False})
    
    patterns = []
    
    # -------------------------------------------------------------------------
    # Sri Lankan Cities - Tagged as LOC (Location)
    # -------------------------------------------------------------------------
    for city in settings.SRI_LANKAN_CITIES:
        patterns.append({
            "label": "LOC",
            "pattern": city
        })
        # Also add lowercase version
        patterns.append({
            "label": "LOC",
            "pattern": city.lower()
        })
    
    # -------------------------------------------------------------------------
    # Sri Lankan Family Names - Tagged as PERSON
    # -------------------------------------------------------------------------
    # Note: These are family names, so they work as part of full names
    # The NER model will typically catch full names, but this helps
    # with standalone family name mentions
    # -------------------------------------------------------------------------
    for name in settings.SRI_LANKAN_NAMES:
        patterns.append({
            "label": "PERSON",
            "pattern": name
        })
    
    # -------------------------------------------------------------------------
    # Sri Lankan Organizations - Tagged as ORG
    # -------------------------------------------------------------------------
    for org in settings.SRI_LANKAN_ORGANIZATIONS:
        patterns.append({
            "label": "ORG",
            "pattern": org
        })
        # Handle multi-word organizations
        if " " in org:
            # Add pattern with different casing
            patterns.append({
                "label": "ORG",
                "pattern": org.lower()
            })
    
    ruler.add_patterns(patterns)


# =============================================================================
# NER ENGINE CLASS
# =============================================================================

class NEREngine:
    """
    Named Entity Recognition engine with Sri Lankan context.
    
    Provides methods to extract named entities from text, including:
    - PERSON: Names of people
    - LOC/GPE: Locations and geopolitical entities
    - ORG: Organizations and companies
    
    The engine is customized to recognize Sri Lankan specific entities
    that might not be in standard NER models.
    
    Attributes:
        nlp: spaCy Language model with custom entity patterns
    """
    
    def __init__(self):
        """
        Initialize the NER Engine.
        
        Loads the spaCy model with Sri Lankan entity customizations.
        Uses cached model if already loaded (via preload_nlp_model).
        """
        self.nlp = preload_nlp_model()
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Processes text through spaCy NER pipeline and categorizes
        entities into persons, locations, and organizations.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dict[str, List[str]]: Dictionary containing:
                - persons: List of person names
                - locations: List of location names
                - organizations: List of organization names
        
        Example:
            >>> engine.extract_entities("Nuwan Perera works at Dialog")
            {
                'persons': ['Nuwan Perera'],
                'locations': [],
                'organizations': ['Dialog']
            }
        """
        if not text or not text.strip():
            return {
                "persons": [],
                "locations": [],
                "organizations": []
            }
        
        # Process text through spaCy pipeline
        doc = self.nlp(text)
        
        # Initialize result containers
        persons = []
        locations = []
        organizations = []
        
        # Extract entities by label
        for ent in doc.ents:
            # -------------------------------------------------------------
            # PERSON entities - names of people
            # -------------------------------------------------------------
            if ent.label_ == "PERSON":
                persons.append(ent.text)
            
            # -------------------------------------------------------------
            # Location entities - LOC (natural locations) and 
            # GPE (geopolitical entities like cities, countries)
            # -------------------------------------------------------------
            elif ent.label_ in ["LOC", "GPE"]:
                locations.append(ent.text)
            
            # -------------------------------------------------------------
            # Organization entities
            # -------------------------------------------------------------
            elif ent.label_ == "ORG":
                organizations.append(ent.text)
        
        # Remove duplicates while preserving order
        return {
            "persons": list(dict.fromkeys(persons)),
            "locations": list(dict.fromkeys(locations)),
            "organizations": list(dict.fromkeys(organizations))
        }
    
    def extract_all_entities(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """
        Extract all entities with detailed information.
        
        Returns all recognized entities with their labels, positions,
        and confidence scores (where available).
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dict[str, List[Dict]]: Dictionary with 'entities' key containing
                                   list of entity details
        
        Example:
            >>> engine.extract_all_entities("Colombo is beautiful")
            {
                'entities': [
                    {
                        'text': 'Colombo',
                        'label': 'LOC',
                        'start': 0,
                        'end': 7
                    }
                ]
            }
        """
        if not text or not text.strip():
            return {"entities": []}
        
        doc = self.nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return {"entities": entities}
    
    def is_sri_lankan_name(self, text: str) -> bool:
        """
        Check if text contains a Sri Lankan family name.
        
        Useful for identifying potential Sri Lankan users based on
        their name patterns.
        
        Args:
            text: Text to check (typically a name)
        
        Returns:
            bool: True if text contains a known Sri Lankan family name
        
        Example:
            >>> engine.is_sri_lankan_name("John Perera")
            True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        return any(
            name.lower() in text_lower 
            for name in settings.SRI_LANKAN_NAMES
        )
    
    def is_sri_lankan_location(self, text: str) -> bool:
        """
        Check if text contains a Sri Lankan city.
        
        Args:
            text: Text to check
        
        Returns:
            bool: True if text contains a known Sri Lankan city
        
        Example:
            >>> engine.is_sri_lankan_location("Lives in Colombo")
            True
        """
        if not text:
            return False
        
        text_lower = text.lower()
        return any(
            city.lower() in text_lower 
            for city in settings.SRI_LANKAN_CITIES
        )


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Module-level convenience function for entity extraction.
    
    Args:
        text: Input text to analyze
    
    Returns:
        Dict[str, List[str]]: Extracted entities by category
    """
    engine = NEREngine()
    return engine.extract_entities(text)
