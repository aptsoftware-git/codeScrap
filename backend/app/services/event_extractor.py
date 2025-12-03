"""
Event Extraction Service using Ollama LLM.

This service uses the Ollama LLM to extract structured event data from article content.
It identifies event type, location, date, description, severity, and other details.
"""

from typing import Dict, List, Optional
import json
from datetime import datetime

from app.models import (
    EventData,
    EventType,
    Location,
    ExtractedEntities,
    ArticleContent
)
from app.services.ollama_service import OllamaClient
from app.services.entity_extractor import entity_extractor
from app.config import settings
from app.utils.logger import logger


class EventExtractor:
    """
    Extracts structured event data from article content using Ollama LLM.
    
    Features:
    - Extracts event type, location, date, severity
    - Combines LLM output with NLP entities for enrichment
    - Validates and normalizes event data
    - Provides confidence scores
    """
    
    def __init__(self):
        """Initialize the event extractor."""
        try:
            self.ollama = OllamaClient(
                base_url=settings.ollama_url,
                default_model=settings.ollama_model
            )
            logger.info("EventExtractor initialized with Ollama client")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama client: {e}")
            self.ollama = None
    
    def create_extraction_prompt(
        self,
        title: str,
        content: str,
        entities: Optional[ExtractedEntities] = None
    ) -> str:
        """
        Create a prompt for event extraction.
        
        Args:
            title: Article title
            content: Article content
            entities: Optional pre-extracted entities for context
            
        Returns:
            Formatted prompt for LLM
        """
        # Truncate content to first 1500 characters to speed up processing
        content_truncated = content[:1500] if len(content) > 1500 else content
        
        prompt = f"""Extract event info from this news article. Respond ONLY with JSON.

Title: {title}

Content: {content_truncated}

"""
        
        if entities and (entities.persons or entities.organizations or entities.locations):
            prompt += f"""Entities: """
            entity_parts = []
            if entities.persons:
                entity_parts.append(f"People: {', '.join(entities.persons[:5])}")
            if entities.organizations:
                entity_parts.append(f"Orgs: {', '.join(entities.organizations[:5])}")
            if entities.locations:
                entity_parts.append(f"Places: {', '.join(entities.locations[:5])}")
            prompt += '; '.join(entity_parts) + "\n\n"
        
        prompt += f"""JSON format (respond with ONLY this, no other text):
{{
    "event_type": "{EventType.PROTEST.value}|{EventType.ATTACK.value}|{EventType.CYBER_ATTACK.value}|{EventType.NATURAL_DISASTER.value}|{EventType.ACCIDENT.value}|{EventType.ELECTION.value}|{EventType.CONFERENCE.value}|{EventType.OTHER.value}",
    "description": "1-2 sentence summary",
    "location": {{"city": "city or null", "country": "country or null", "region": "region or null"}},
    "date_text": "when it occurred",
    "severity": 5,
    "people_affected": 0,
    "key_actors": ["actor1", "actor2"],
    "confidence": 0.85
}}"""
        
        return prompt
    
    def parse_llm_response(self, response: str) -> Optional[Dict]:
        """
        Parse the LLM response to extract JSON data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            # Try to find JSON in the response
            response = response.strip()
            
            # If response starts with ```json, extract the JSON block
            if response.startswith("```json"):
                response = response.split("```json")[1].split("```")[0].strip()
            elif response.startswith("```"):
                response = response.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None
    
    def validate_event_type(self, event_type: str) -> EventType:
        """
        Validate and normalize event type.
        
        Args:
            event_type: Event type string from LLM
            
        Returns:
            Valid EventType enum value
        """
        # Try exact match
        try:
            return EventType(event_type.lower())
        except ValueError:
            pass
        
        # Try fuzzy matching - prefer longer/more specific matches
        event_type_lower = event_type.lower().replace("_", " ").replace("-", " ")
        
        # First, try finding enum values contained in the event_type
        matches = []
        for et in EventType:
            et_value = et.value.replace("_", " ").replace("-", " ")
            if et_value in event_type_lower:
                matches.append((et, len(et_value)))  # Store with length for ranking
        
        # Sort by length (prefer longer/more specific matches)
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        # Try the reverse - event_type contained in enum value
        for et in EventType:
            et_value = et.value.replace("_", " ").replace("-", " ")
            if event_type_lower in et_value:
                return et
        
        # Check individual words (excluding common words like "event", "type", "other")
        common_words = {"event", "type", "other", "a", "an", "the"}
        event_words = [w for w in event_type_lower.split() if w not in common_words]
        
        if event_words:  # Only try if we have meaningful words
            for et in EventType:
                et_words = et.value.replace("_", " ").replace("-", " ").split()
                et_words = [w for w in et_words if w not in common_words]
                if any(word in et_words for word in event_words):
                    return et
        
        # Default to other
        logger.warning(f"Unknown event type '{event_type}', defaulting to 'other'")
        return EventType.OTHER
    
    def create_location(self, location_data: Dict) -> Location:
        """
        Create a Location object from parsed data.
        
        Args:
            location_data: Dictionary with city, country, region
            
        Returns:
            Location object
        """
        return Location(
            city=location_data.get("city"),
            country=location_data.get("country"),
            region=location_data.get("region"),
            coordinates=None  # Can be added later with geocoding
        )
    
    async def extract_event(
        self,
        title: str,
        content: str,
        url: Optional[str] = None,
        entities: Optional[ExtractedEntities] = None
    ) -> Optional[EventData]:
        """
        Extract event data from an article.
        
        Args:
            title: Article title
            content: Article content
            url: Optional article URL
            entities: Optional pre-extracted entities
            
        Returns:
            EventData object or None if extraction fails
        """
        try:
            logger.info(f"Extracting event from article: {title[:50]}...")
            
            # If entities not provided, extract them
            if entities is None and entity_extractor.is_available():
                entities = entity_extractor.extract_from_article(title, content)
                logger.debug(f"Extracted {entity_extractor.count_entities(entities)} entities")
            
            # Create prompt
            prompt = self.create_extraction_prompt(title, content, entities)
            
            # Get LLM response with aggressive optimization for speed
            response = self.ollama.generate(
                prompt=prompt,
                model=None,  # Use default model
                max_tokens=300,  # Reduced from 500 to 300 for faster generation
                temperature=0.1  # Very low temperature for focused/deterministic output
            )
            
            if not response or not response.strip():
                logger.error("Empty response from LLM")
                return None
            
            logger.debug(f"LLM response: {response[:200]}...")
            
            # Parse response
            parsed_data = self.parse_llm_response(response)
            if not parsed_data:
                return None
            
            # Extract location
            location = self.create_location(parsed_data.get("location", {}))
            
            # Extract participants and organizations from key_actors
            key_actors = parsed_data.get("key_actors", [])
            participants = []
            organizations = []
            
            # If we have entities, use them to categorize actors
            if entities:
                for actor in key_actors:
                    if actor in entities.persons:
                        participants.append(actor)
                    elif actor in entities.organizations:
                        organizations.append(actor)
                    else:
                        # Default to participant if unclear
                        participants.append(actor)
            else:
                participants = key_actors
            
            # Create EventData object matching the model schema
            event_data = EventData(
                event_type=self.validate_event_type(parsed_data.get("event_type", "other")),
                title=title,  # Use article title
                summary=parsed_data.get("description", ""),
                location=location,
                event_date=None,  # Parse from date_text if needed
                participants=participants,
                organizations=organizations,
                casualties=None,  # Can be extracted if mentioned
                impact=parsed_data.get("description", ""),  # Use description as impact
                confidence=max(0.0, min(1.0, parsed_data.get("confidence", 0.7))),
                source_url=url  # Add source URL
            )
            
            logger.info(
                f"✅ Extracted event: {event_data.event_type.value} "
                f"({event_data.title[:30]}..., confidence: {event_data.confidence:.2f})"
            )
            
            return event_data
            
        except Exception as e:
            logger.error(f"Error extracting event: {e}")
            return None
    
    async def extract_from_article(
        self,
        article: ArticleContent
    ) -> Optional[EventData]:
        """
        Extract event data from an ArticleContent object.
        
        Args:
            article: ArticleContent object with title, content, url, etc.
            
        Returns:
            EventData object or None if extraction fails
        """
        # ArticleContent doesn't have entities attribute - extract them
        entities = None
        if entity_extractor.is_available():
            entities = entity_extractor.extract_from_article(
                article.title or "",
                article.content
            )
        
        return await self.extract_event(
            title=article.title or "Untitled",
            content=article.content,
            url=article.url,
            entities=entities
        )
    
    async def extract_batch(
        self,
        articles: List[ArticleContent]
    ) -> List[EventData]:
        """
        Extract events from multiple articles.
        
        Args:
            articles: List of ArticleContent objects
            
        Returns:
            List of EventData objects (successful extractions only)
        """
        logger.info(f"Extracting events from {len(articles)} articles...")
        
        events = []
        for i, article in enumerate(articles, 1):
            logger.debug(f"Processing article {i}/{len(articles)}")
            
            event = await self.extract_from_article(article)
            if event:
                events.append(event)
        
        logger.info(f"✅ Successfully extracted {len(events)}/{len(articles)} events")
        return events
    
    def is_available(self) -> bool:
        """
        Check if the event extractor is available.
        
        Returns:
            True if Ollama service is available
        """
        return self.ollama is not None


# Global instance
event_extractor = EventExtractor()
