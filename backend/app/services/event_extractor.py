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
from app.services.llm_router import llm_router
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
        logger.info("EventExtractor initialized with LLM router")
    
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
Read the article carefully and extract ONLY information that is explicitly stated. Do NOT make up or assume information.

STEP 1: Determine the MAIN event type from this article
STEP 2: Extract ONLY facts that are clearly stated in the article
STEP 3: Use null for ANY field where information is not explicitly mentioned
STEP 4: Write a concise summary (3-4 sentences maximum, capturing the key points)

EVENT TYPES (choose the ONE that best matches THIS article):
- meeting, summit, conference: Diplomatic meetings, trade talks, official visits, state visits
- political_event, election: Political activities, campaigns, government actions
- bombing, explosion, shooting, attack: Violent incidents (ONLY if this article is about such an incident)
- terrorist_activity: Terror-related acts
- protest, demonstration, civil_unrest: Public protests or unrest
- natural_disaster, accident: Natural catastrophes or accidents
- cyber_attack, data_breach: Cyber security incidents
- kidnapping, theft: Crimes
- military_operation: Military actions
- other: If none of the above fit

CRITICAL RULES - READ CAREFULLY:
1. ONLY extract event_type that matches THIS article's main topic
2. Extract perpetrator/casualties if mentioned OR claimed in THIS article (including claims by groups)
3. Do NOT mix information from different articles or examples
4. If a field is not mentioned in the article, use null
5. Summary must be 3-4 sentences maximum, concise and factual
6. Perpetrator is for violent events where someone carried out or claimed an attack
7. Casualties: Extract if deaths/injuries are mentioned, claimed, or reported in THIS article
8. Location should be where THIS event takes place
9. Date should be when THIS event happened (not the article date)
10. If event doesn't clearly fit a category, use "other"
11. Individuals: List ONLY actual person names (e.g., "Narendra Modi", "Vladimir Putin") - exclude place names, abbreviations, or non-person entities

PERPETRATOR TYPES (ONLY if this is a violent attack with identified perpetrator):
- terrorist_group, state_actor, criminal_organization, individual, multiple_parties, unknown, not_applicable

INDIVIDUALS FIELD INSTRUCTIONS:
- Include ONLY actual human names (first name + last name or full names)
- EXCLUDE: Place names (Tamil Nadu, Tai Po), abbreviations (RADS, DMU), organization names, medical terms
- EXCLUDE: Single-word names without context (Kurnool, Vishnu without surname could be a place)
- Include: Political leaders, officials, victims with full names, witnesses with full names
- Examples of VALID individuals: "Narendra Modi", "Revanth Reddy", "Vladimir Putin", "M Lakshmaiah"
- Examples of INVALID (do not include): "Tamil Nadu", "RADS", "Kurnool", "Tai Po", "DMU"

EXAMPLE - Meeting/Summit Article:
{
    "event_type": "meeting",
    "event_sub_type": "bilateral summit",
    "summary": "Russian President Putin visited India for the 23rd Russia-India Summit. He held talks with PM Modi focusing on economic cooperation and energy ties. The two leaders agreed to boost bilateral trade to $100 billion by 2030.",
    "perpetrator": null,
    "perpetrator_type": null,
    "location": {
        "city": "New Delhi",
        "region": null,
        "country": "India"
    },
    "event_date": "2025-12-05",
    "event_time": null,
    "individuals": ["Vladimir Putin", "Narendra Modi"],
    "organizations": ["Kremlin", "Indian Government"],
    "casualties": null,
    "confidence": 0.9
}

EXAMPLE - Attack Article:
{
    "event_type": "bombing",
    "event_sub_type": "suicide bombing",
    "summary": "A suicide bomber attacked a checkpoint in Kabul. The Islamic State claimed responsibility for the attack, claiming to have killed 20 people and injured 30. Taliban authorities disputed the casualty figures.",
    "perpetrator": "Islamic State",
    "perpetrator_type": "terrorist_group",
    "location": {
        "city": "Kabul",
        "region": null,
        "country": "Afghanistan"
    },
    "event_date": "2023-01-01",
    "event_time": null,
    "individuals": [],
    "organizations": ["Islamic State", "Taliban"],
    "casualties": {
        "killed": 20,
        "injured": 30
    },
    "confidence": 0.85
}

JSON FORMATTING RULES:
- Output ONLY valid JSON - no explanations before or after
- Use null for missing/unavailable information
- All strings in double quotes
- Numbers without quotes
- event_date format: YYYY-MM-DD (null if not mentioned)
- confidence: 0.9+ very clear, 0.7-0.9 mostly clear, 0.5-0.7 uncertain, <0.5 very uncertain

JSON OUTPUT (extract from THIS article):"""
        
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
        
        # Try fuzzy matching with keyword mapping
        event_type_lower = event_type.lower().replace("_", " ").replace("-", " ")
        
        # Keyword-based mapping for common variations
        if "visit" in event_type_lower or "diplomatic" in event_type_lower:
            return EventType.MEETING
        elif "summit" in event_type_lower or "bilateral" in event_type_lower:
            return EventType.SUMMIT
        elif "conference" in event_type_lower:
            return EventType.CONFERENCE
        
        # Try finding enum values contained in the event_type
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
        entities: Optional[ExtractedEntities] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ) -> tuple[Optional[EventData], Optional[Dict]]:
        """
        Extract comprehensive event data from an article.
        
        Args:
            title: Article title
            content: Article content
            url: Optional article URL
            source_name: Optional source name (e.g., "BBC News")
            article_published_date: Optional article publication date
            entities: Optional pre-extracted entities
            llm_provider: Optional LLM provider ("ollama" or "claude")
            llm_model: Optional model name
            
        Returns:
            Tuple of (EventData object or None, usage metadata dict)
        """
        try:
            logger.info(f"Extracting event from article: {title[:50]}...")
            
            # If entities not provided, extract them
            if entities is None and entity_extractor.is_available():
                entities = entity_extractor.extract_from_article(title, content)
                logger.debug(f"Extracted {entity_extractor.count_entities(entities)} entities")
            
            # Create production-grade prompt
            prompt = self.create_extraction_prompt(title, content, entities)
            
            # Build system prompt for Claude caching (if using Claude)
            system_prompt = """You are an expert event extraction AI. Extract event details ONLY from the provided article. 
Be precise and conservative - only extract information that is clearly stated in the article.
Extract event type, location, date, participants, organizations, and provide a concise 3-4 sentence summary.
Return ONLY valid JSON matching the schema provided."""
            
            # Get LLM response via router
            response, metadata = await llm_router.generate(
                prompt=prompt,
                provider=llm_provider,
                model=llm_model,
                max_tokens=500,
                temperature=0.2,
                system_prompt=system_prompt
            )
            
            if not response or not response.strip():
                logger.error("Empty response from LLM")
                return None, metadata
            
            logger.debug(f"LLM response: {response[:300]}...")
            
            # Parse response
            parsed_data = self.parse_llm_response(response)
            if not parsed_data or not isinstance(parsed_data, dict):
                logger.error(f"Invalid parsed data (type: {type(parsed_data)}): {parsed_data}")
                return None, metadata
            
            # VALIDATION: Check if extraction makes sense for this article
            event_type_str = parsed_data.get("event_type", "").lower()
            summary = parsed_data.get("summary", "").lower()
            title_lower = title.lower()
            content_lower = content[:1000].lower()  # Check first 1000 chars
            
            # Check if violent event type matches article content
            # If event_type is violent but article has no violence keywords, change to "other"
            if event_type_str in ["bombing", "explosion", "attack", "shooting", "terrorist_activity", "kidnapping"]:
                violence_keywords = ["bomb", "explosion", "attack", "shoot", "terror", "killed", "dead", "casualt", "injur", "blast", "kidnap", "abduct"]
                has_violence_mention = any(keyword in title_lower or keyword in content_lower for keyword in violence_keywords)
                
                if not has_violence_mention:
                    logger.warning(f"⚠️ Event type '{event_type_str}' doesn't match article content. Changing to 'other' for: {title[:60]}")
                    parsed_data["event_type"] = "other"
                    # Clear violence-related fields
                    parsed_data["perpetrator"] = None
                    parsed_data["perpetrator_type"] = None
                    parsed_data["casualties"] = None
            
            # Validate confidence score - reject ONLY if extremely low
            confidence = parsed_data.get("confidence", 0.0)
            if confidence < 0.3:
                logger.warning(f"❌ Rejecting extraction: confidence too low ({confidence:.2f}) for: {title[:60]}")
                return None, metadata
            
            # Extract location components
            location_data = parsed_data.get("location", {})
            
            # Handle country - convert list to string if needed (for cross-border events)
            country_value = location_data.get("country")
            if isinstance(country_value, list):
                # Join multiple countries with "/" for cross-border events (e.g., "India/Pakistan")
                country_str = "/".join(country_value) if country_value else None
                logger.debug(f"Converted country list to string: {country_value} -> {country_str}")
            else:
                country_str = country_value
            
            # Handle city - convert list to string if needed (for multi-city events)
            city_value = location_data.get("city")
            if isinstance(city_value, list):
                # Join multiple cities with "/" for multi-city events
                city_str = "/".join(city_value) if city_value else None
                logger.debug(f"Converted city list to string: {city_value} -> {city_str}")
            else:
                city_str = city_value
            
            location = Location(
                city=city_str,
                region=location_data.get("region") or location_data.get("state"),
                country=country_str,
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
                # Ensure values are integers, not None
                killed = casualties_data.get("killed") or 0
                injured = casualties_data.get("injured") or 0
                # Convert to int if they're strings
                if isinstance(killed, str):
                    killed = int(killed) if killed.isdigit() else 0
                if isinstance(injured, str):
                    injured = int(injured) if injured.isdigit() else 0
                # Only create casualties dict if we have actual numbers
                if killed > 0 or injured > 0:
                    casualties = {"killed": int(killed), "injured": int(injured)}
            
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
                f"Confidence: {event_data.confidence:.2f} | "
                f"Provider: {metadata.get('provider', 'unknown')}"
            )
            
            return event_data, metadata
            
        except ValueError as e:
            logger.error(f"Validation error creating EventData: {e}", exc_info=True)
            return None, {"error": str(e)}
        except Exception as e:
            logger.error(f"Error extracting event from '{title[:50]}...': {e}", exc_info=True)
            return None, {"error": str(e)}
    
    async def extract_from_article(
        self,
        article: ArticleContent,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ) -> tuple[Optional[EventData], Optional[Dict]]:
        """
        Extract event data from an ArticleContent object.
        
        Args:
            article: ArticleContent object with title, content, url, etc.
            llm_provider: Optional LLM provider
            llm_model: Optional model name
            
        Returns:
            Tuple of (EventData object or None, usage metadata)
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
            entities=entities,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
    
    async def extract_batch(
        self,
        articles: List[ArticleContent],
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ) -> tuple[List[EventData], List[Dict]]:
        """
        Extract events from multiple articles.
        
        Args:
            articles: List of ArticleContent objects
            llm_provider: Optional LLM provider
            llm_model: Optional model name
            
        Returns:
            Tuple of (List of EventData objects, List of usage metadata)
        """
        logger.info(f"Extracting events from {len(articles)} articles...")
        
        events = []
        metadata_list = []
        for i, article in enumerate(articles, 1):
            logger.debug(f"Processing article {i}/{len(articles)}")
            
            event, metadata = await self.extract_from_article(
                article,
                llm_provider=llm_provider,
                llm_model=llm_model
            )
            if event:
                events.append(event)
                metadata_list.append(metadata)
        
        logger.info(f"✅ Successfully extracted {len(events)}/{len(articles)} events")
        return events, metadata_list
    
    def is_available(self) -> bool:
        """
        Check if the event extractor is available.
        
        Returns:
            True if any LLM service is available
        """
        status = llm_router.get_provider_status()
        return any(
            provider_info.get("available", False)
            for provider_info in status.get("providers", {}).values()
        )


# Global instance
event_extractor = EventExtractor()
