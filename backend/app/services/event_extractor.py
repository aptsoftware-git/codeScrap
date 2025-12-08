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
    PerpetratorType,
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
        Create a production-grade prompt for comprehensive event extraction.
        
        Args:
            title: Article title
            content: Article content
            entities: Optional pre-extracted entities for context
            
        Returns:
            Formatted prompt for LLM
        """
        # Truncate content strategically - keep beginning (context) and end (conclusion)
        max_length = 2000
        if len(content) > max_length:
            # Take first 1500 chars and last 500 chars
            content_truncated = content[:1500] + "\n...\n" + content[-500:]
        else:
            content_truncated = content
        
        prompt = f"""You are a military intelligence analyst extracting structured event data from news articles.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content_truncated}

"""
        
        # Add entity context if available for better accuracy
        if entities and (entities.persons or entities.organizations or entities.locations):
            prompt += "DETECTED ENTITIES:\n"
            if entities.persons:
                prompt += f"- People: {', '.join(entities.persons[:8])}\n"
            if entities.organizations:
                prompt += f"- Organizations: {', '.join(entities.organizations[:8])}\n"
            if entities.locations:
                prompt += f"- Locations: {', '.join(entities.locations[:8])}\n"
            prompt += "\n"
        
        # Production-grade extraction instructions
        prompt += """EXTRACTION TASK:
Extract ALL available information in JSON format. Be thorough and accurate.

CRITICAL REQUIREMENTS:
1. Extract location components separately (city, region/state, country)
2. Identify perpetrator(s) for attacks/bombings (who did it)
3. Classify perpetrator type (terrorist group, state actor, individual, etc.)
4. Identify event sub-type for more specific classification
5. Parse date AND time separately if mentioned
6. Count casualties (killed, injured) if mentioned
7. List individuals and organizations separately
8. Assign appropriate event type
9. Provide confidence score (0.0-1.0)

EVENT TYPES (choose most specific):
- bombing, explosion, shooting, attack, kidnapping, theft
- terrorist_activity, cyber_attack, data_breach
- protest, demonstration, civil_unrest
- natural_disaster, accident
- conference, meeting, summit, election
- military_operation, political_event
- other (if none fit)

PERPETRATOR TYPES (choose one if perpetrator identified):
- terrorist_group: Known terrorist organizations
- state_actor: Government or military forces
- criminal_organization: Organized crime groups
- individual: Single person or small group
- multiple_parties: Multiple distinct groups involved
- unknown: Perpetrator not identified
- not_applicable: No perpetrator (e.g., natural disasters)

RESPOND WITH VALID JSON ONLY (no markdown, no explanations):
{
    "event_type": "bombing",
    "event_sub_type": "suicide bombing",
    "summary": "Brief 1-2 sentence summary of what happened",
    "perpetrator": "Islamic State",
    "perpetrator_type": "terrorist_group",
    "location": {
        "city": "Kabul",
        "region": "Kabul Province",
        "country": "Afghanistan"
    },
    "event_date": "2023-01-02",
    "event_time": "09:30",
    "individuals": ["Person A", "Person B"],
    "organizations": ["Taliban", "UN"],
    "casualties": {
        "killed": 5,
        "injured": 12
    },
    "confidence": 0.85
}

CRITICAL - JSON FORMATTING RULES:
- ONLY output valid JSON - NO explanatory text before or after
- Use null (not "null") for missing values
- Do NOT use 'or null' - just use null directly
- Do NOT add comments (no // or /* */)
- All string values must be in double quotes
- Numbers should NOT be in quotes
- event_date format: YYYY-MM-DD
- event_time format: HH:MM or descriptive text like "morning", "evening"
- event_sub_type: More specific classification (e.g., "suicide bombing", "mass shooting", "vehicle attack")
- perpetrator_type: One of: terrorist_group, state_actor, criminal_organization, individual, multiple_parties, unknown, not_applicable
- casualties: Use null if no casualties mentioned, otherwise {"killed": N, "injured": M}
- confidence: 0.9+ if very clear, 0.7-0.9 if mostly clear, <0.7 if uncertain

JSON OUTPUT:"""
        
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
            
            # Try to extract JSON from text if it's embedded
            # Look for { ... } pattern
            if not response.startswith("{"):
                json_start = response.find("{")
                if json_start != -1:
                    json_end = response.rfind("}")
                    if json_end != -1:
                        response = response[json_start:json_end+1]
            
            # Common fixes for LLM-generated JSON issues
            # Fix trailing commas before closing braces/brackets
            response = response.replace(",}", "}")
            response = response.replace(",]", "]")
            
            # Fix "or null" patterns that LLM might output
            import re
            # Replace patterns like: "value" or null -> null
            response = re.sub(r'"[^"]*"\s+or\s+null', 'null', response)
            # Replace patterns like: null or "value" -> null
            response = re.sub(r'null\s+or\s+"[^"]*"', 'null', response)
            # Replace patterns like: value or null (without quotes) -> null
            response = re.sub(r':\s*\w+\s+or\s+null', ': null', response)
            
            # Fix missing quotes around null values (some LLMs output 'null' as text)
            # response = response.replace(': null', ': null')  # Already correct
            
            # Parse JSON
            data = json.loads(response)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Full response was:\n{response}")
            # Try to salvage partial data by being more aggressive
            try:
                # Remove comments if any
                lines = response.split('\n')
                cleaned_lines = [line.split('//')[0] for line in lines]  # Remove // comments
                cleaned = '\n'.join(cleaned_lines)
                data = json.loads(cleaned)
                logger.info("Successfully parsed after removing comments")
                return data
            except:
                logger.error("Could not salvage JSON even after cleanup")
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
    
    def validate_perpetrator_type(self, perpetrator_type: str) -> Optional['PerpetratorType']:
        """
        Validate and normalize perpetrator type.
        
        Args:
            perpetrator_type: Perpetrator type string from LLM
            
        Returns:
            Valid PerpetratorType enum value or None
        """
        from app.models import PerpetratorType
        
        if not perpetrator_type:
            return None
        
        # Try exact match
        try:
            return PerpetratorType(perpetrator_type.lower())
        except ValueError:
            pass
        
        # Try fuzzy matching
        perp_type_lower = perpetrator_type.lower().replace("_", " ").replace("-", " ")
        
        # Check if enum value is contained in the input
        for pt in PerpetratorType:
            pt_value = pt.value.replace("_", " ").replace("-", " ")
            if pt_value in perp_type_lower or perp_type_lower in pt_value:
                return pt
        
        # Keyword-based matching
        if "terror" in perp_type_lower or "militant" in perp_type_lower:
            return PerpetratorType.TERRORIST_GROUP
        elif "state" in perp_type_lower or "government" in perp_type_lower or "military" in perp_type_lower:
            return PerpetratorType.STATE_ACTOR
        elif "criminal" in perp_type_lower or "gang" in perp_type_lower or "cartel" in perp_type_lower:
            return PerpetratorType.CRIMINAL_ORGANIZATION
        elif "person" in perp_type_lower or "individual" in perp_type_lower or "man" in perp_type_lower or "woman" in perp_type_lower:
            return PerpetratorType.INDIVIDUAL
        elif "multiple" in perp_type_lower or "several" in perp_type_lower:
            return PerpetratorType.MULTIPLE_PARTIES
        elif "unknown" in perp_type_lower or "unidentified" in perp_type_lower:
            return PerpetratorType.UNKNOWN
        
        # Default to unknown if can't determine
        logger.warning(f"Unknown perpetrator type '{perpetrator_type}', defaulting to 'unknown'")
        return PerpetratorType.UNKNOWN
    
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
        source_name: Optional[str] = None,
        article_published_date: Optional[datetime] = None,
        entities: Optional[ExtractedEntities] = None
    ) -> Optional[EventData]:
        """
        Extract comprehensive event data from an article.
        
        Args:
            title: Article title
            content: Article content
            url: Optional article URL
            source_name: Optional source name (e.g., "BBC News")
            article_published_date: Optional article publication date
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
            
            # Create production-grade prompt
            prompt = self.create_extraction_prompt(title, content, entities)
            
            # Get LLM response asynchronously
            response = await self.ollama.generate_async(
                prompt=prompt,
                model=None,  # Use default model
                max_tokens=500,  # Increased for comprehensive extraction
                temperature=0.2  # Low for consistent, accurate extraction
            )
            
            if not response or not response.strip():
                logger.error("Empty response from LLM")
                return None
            
            logger.debug(f"LLM response: {response[:300]}...")
            
            # Parse response
            parsed_data = self.parse_llm_response(response)
            if not parsed_data:
                return None
            
            # Extract location components
            location_data = parsed_data.get("location", {})
            location = Location(
                city=location_data.get("city"),
                region=location_data.get("region") or location_data.get("state"),
                country=location_data.get("country"),
                coordinates=None
            )
            
            # Parse event date
            event_date = None
            event_date_str = parsed_data.get("event_date")
            if event_date_str:
                try:
                    # Try parsing YYYY-MM-DD format
                    event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                except ValueError:
                    try:
                        # Try ISO format
                        event_date = datetime.fromisoformat(event_date_str)
                    except ValueError:
                        logger.warning(f"Could not parse event date: {event_date_str}")
            
            # If event_date is still None, use article_published_date as fallback
            if not event_date and article_published_date:
                event_date = article_published_date
                logger.debug("Using article publication date as event date fallback")
            
            # Extract event time (can be "09:30", "morning", etc.)
            event_time = parsed_data.get("event_time")
            
            # Extract participants and organizations
            individuals = parsed_data.get("individuals", []) or []
            organizations = parsed_data.get("organizations", []) or []
            
            # If we have entities, enrich the lists
            if entities:
                # Add entities not already in the lists
                for person in entities.persons[:10]:  # Limit to top 10
                    if person not in individuals:
                        individuals.append(person)
                
                for org in entities.organizations[:10]:
                    if org not in organizations:
                        organizations.append(org)
            
            # Extract casualties
            casualties_data = parsed_data.get("casualties")
            casualties = None
            if casualties_data and isinstance(casualties_data, dict):
                killed = casualties_data.get("killed", 0)
                injured = casualties_data.get("injured", 0)
                if killed or injured:
                    casualties = {"killed": killed, "injured": injured}
            
            # Extract perpetrator
            perpetrator = parsed_data.get("perpetrator")
            
            # Extract source name from URL if not provided
            if not source_name and url:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                # Extract readable source name from domain
                if "bbc" in domain:
                    source_name = "BBC News"
                elif "reuters" in domain:
                    source_name = "Reuters"
                elif "cnn" in domain:
                    source_name = "CNN"
                elif "aljazeera" in domain:
                    source_name = "Al Jazeera"
                elif "wikipedia" in domain:
                    source_name = "Wikipedia"
                elif "cbsnews" in domain:
                    source_name = "CBS News"
                elif "npr" in domain:
                    source_name = "NPR"
                elif "nypost" in domain:
                    source_name = "New York Post"
                elif "apnews" in domain:
                    source_name = "Associated Press"
                elif "alarabiya" in domain:
                    source_name = "Al Arabiya"
                elif "indiatvnews" in domain:
                    source_name = "India TV News"
                elif "thenationalnews" in domain:
                    source_name = "The National News"
                else:
                    # Use domain as source name
                    source_name = domain.replace("www.", "").split(".")[0].title()
            
            # Create comprehensive EventData object
            event_data = EventData(
                # Core information
                event_type=self.validate_event_type(parsed_data.get("event_type", "other")),
                event_sub_type=parsed_data.get("event_sub_type"),
                title=title,
                summary=parsed_data.get("summary", parsed_data.get("description", "")),
                
                # Perpetrator
                perpetrator=perpetrator,
                perpetrator_type=self.validate_perpetrator_type(parsed_data.get("perpetrator_type")),
                
                # Location (with parsed components)
                location=location,
                
                # Temporal information
                event_date=event_date,
                event_time=event_time,
                
                # People and organizations
                participants=individuals,
                organizations=organizations,
                
                # Impact
                casualties=casualties,
                impact=parsed_data.get("summary", parsed_data.get("description", "")),
                
                # Source metadata
                source_name=source_name,
                source_url=url,
                article_published_date=article_published_date or event_date,  # Fallback to event_date
                collection_timestamp=datetime.utcnow(),  # When the system collected this content
                
                # Quality
                confidence=max(0.0, min(1.0, parsed_data.get("confidence", 0.75))),
                
                # Raw content
                full_content=content
            )
            
            logger.info(
                f"✅ Extracted event: {event_data.event_type.value} | "
                f"{event_data.title[:40]}... | "
                f"Location: {event_data.location} | "
                f"Confidence: {event_data.confidence:.2f}"
            )
            
            return event_data
            
        except Exception as e:
            logger.error(f"Error extracting event: {e}", exc_info=True)
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
        # Extract entities if available
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
            source_name=article.source_name,
            article_published_date=article.published_date,
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
