"""
Entity extraction service using spaCy for Named Entity Recognition (NER).
"""

from typing import List, Set
from loguru import logger

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available - entity extraction will be limited")

from app.models import ExtractedEntities


class EntityExtractor:
    """
    Extracts named entities from text using spaCy NLP.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the entity extractor.
        
        Args:
            model_name: spaCy model to use (default: en_core_web_sm)
        """
        self.model_name = model_name
        self.nlp = None
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(
                    f"spaCy model '{model_name}' not found. "
                    f"Download it with: python -m spacy download {model_name}"
                )
            except Exception as e:
                logger.error(f"Error loading spaCy model: {e}")
        else:
            logger.warning("spaCy not installed - install with: pip install spacy")
    
    def is_available(self) -> bool:
        """Check if spaCy model is loaded and available."""
        return self.nlp is not None
    
    def extract_entities(self, text: str) -> ExtractedEntities:
        """
        Extract named entities from text.
        
        Args:
            text: Input text to process
        
        Returns:
            ExtractedEntities object with deduplicated entities
        """
        if not self.is_available():
            logger.warning("spaCy model not available, returning empty entities")
            return ExtractedEntities()
        
        if not text or len(text.strip()) == 0:
            return ExtractedEntities()
        
        try:
            # Process text with spaCy
            doc = self.nlp(text[:1000000])  # Limit to 1M chars for performance
            
            # Extract entities by type
            persons: Set[str] = set()
            organizations: Set[str] = set()
            locations: Set[str] = set()
            dates: Set[str] = set()
            events: Set[str] = set()
            products: Set[str] = set()
            
            for ent in doc.ents:
                # Clean entity text
                entity_text = ent.text.strip()
                if not entity_text or len(entity_text) < 2:
                    continue
                
                # Categorize by entity label
                if ent.label_ == "PERSON":
                    persons.add(entity_text)
                elif ent.label_ in ["ORG", "NORP"]:  # Organizations and nationalities
                    organizations.add(entity_text)
                elif ent.label_ in ["GPE", "LOC", "FAC"]:  # Locations
                    locations.add(entity_text)
                elif ent.label_ == "DATE":
                    dates.add(entity_text)
                elif ent.label_ == "EVENT":
                    events.add(entity_text)
                elif ent.label_ == "PRODUCT":
                    products.add(entity_text)
            
            # Create ExtractedEntities object
            entities = ExtractedEntities(
                persons=sorted(list(persons)),
                organizations=sorted(list(organizations)),
                locations=sorted(list(locations)),
                dates=sorted(list(dates)),
                events=sorted(list(events)),
                products=sorted(list(products))
            )
            
            logger.debug(
                f"Extracted entities: {len(persons)} persons, "
                f"{len(organizations)} orgs, {len(locations)} locations, "
                f"{len(dates)} dates"
            )
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return ExtractedEntities()
    
    def deduplicate_entities(self, entities_list: List[ExtractedEntities]) -> ExtractedEntities:
        """
        Merge and deduplicate entities from multiple sources.
        
        Args:
            entities_list: List of ExtractedEntities objects
        
        Returns:
            Single ExtractedEntities with deduplicated values
        """
        all_persons: Set[str] = set()
        all_organizations: Set[str] = set()
        all_locations: Set[str] = set()
        all_dates: Set[str] = set()
        all_events: Set[str] = set()
        all_products: Set[str] = set()
        
        for entities in entities_list:
            all_persons.update(entities.persons)
            all_organizations.update(entities.organizations)
            all_locations.update(entities.locations)
            all_dates.update(entities.dates)
            all_events.update(entities.events)
            all_products.update(entities.products)
        
        return ExtractedEntities(
            persons=sorted(list(all_persons)),
            organizations=sorted(list(all_organizations)),
            locations=sorted(list(all_locations)),
            dates=sorted(list(all_dates)),
            events=sorted(list(all_events)),
            products=sorted(list(all_products))
        )
    
    def extract_from_article(self, title: str, content: str) -> ExtractedEntities:
        """
        Extract entities from both title and content.
        
        Args:
            title: Article title
            content: Article content
        
        Returns:
            ExtractedEntities from combined text
        """
        # Combine title and content with proper spacing
        combined_text = f"{title}\n\n{content}"
        return self.extract_entities(combined_text)
    
    def get_top_entities(
        self,
        entities: ExtractedEntities,
        max_per_type: int = 10
    ) -> ExtractedEntities:
        """
        Get top N entities of each type.
        
        Args:
            entities: ExtractedEntities object
            max_per_type: Maximum entities to keep per type
        
        Returns:
            ExtractedEntities with limited items
        """
        return ExtractedEntities(
            persons=entities.persons[:max_per_type],
            organizations=entities.organizations[:max_per_type],
            locations=entities.locations[:max_per_type],
            dates=entities.dates[:max_per_type],
            events=entities.events[:max_per_type],
            products=entities.products[:max_per_type]
        )
    
    def count_entities(self, entities: ExtractedEntities) -> int:
        """
        Count total number of extracted entities.
        
        Args:
            entities: ExtractedEntities object
        
        Returns:
            Total count of all entities
        """
        return (
            len(entities.persons) +
            len(entities.organizations) +
            len(entities.locations) +
            len(entities.dates) +
            len(entities.events) +
            len(entities.products)
        )


# Global instance
entity_extractor = EntityExtractor()
