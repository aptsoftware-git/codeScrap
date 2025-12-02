"""
Query Matching and Relevance Scoring Service.

This service filters and ranks events based on user queries.
It considers text similarity, location matching, date ranges, and event types.
"""

from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
import re
from difflib import SequenceMatcher

from app.models import (
    EventData,
    SearchQuery,
    EventType,
    Location
)
from app.utils.logger import logger


class QueryMatcher:
    """
    Matches and ranks events based on search queries.
    
    Features:
    - Text similarity matching (title, summary)
    - Location matching (city, country, region)
    - Date range filtering
    - Event type filtering
    - Weighted relevance scoring
    """
    
    def __init__(self):
        """Initialize the query matcher."""
        self.weights = {
            'text': 0.40,      # 40% weight for text matching
            'location': 0.25,  # 25% weight for location matching
            'date': 0.20,      # 20% weight for date relevance
            'event_type': 0.15 # 15% weight for event type matching
        }
        logger.info("QueryMatcher initialized with weights: {}", self.weights)
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text (lowercase, no extra spaces)
        """
        if not text:
            return ""
        # Convert to lowercase, remove extra whitespace
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            Set of keywords
        """
        if not text:
            return set()
        
        # Normalize text
        text = self.normalize_text(text)
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'it', 'its', 'they', 'them', 'their'
        }
        
        # Split into words and filter
        words = text.split()
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return keywords
    
    def calculate_text_similarity(self, query_text: str, event: EventData) -> float:
        """
        Calculate text similarity between query and event.
        
        Args:
            query_text: Query text
            event: Event to compare
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not query_text:
            return 0.0
        
        # Combine event title and summary
        event_text = f"{event.title} {event.summary}".lower()
        query_text = query_text.lower()
        
        # Method 1: Keyword overlap
        query_keywords = self.extract_keywords(query_text)
        event_keywords = self.extract_keywords(event_text)
        
        if not query_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = query_keywords.intersection(event_keywords)
        union = query_keywords.union(event_keywords)
        
        keyword_score = len(intersection) / len(union) if union else 0.0
        
        # Method 2: Sequence matching (for phrases)
        sequence_score = SequenceMatcher(None, query_text, event_text).ratio()
        
        # Combine scores (weighted toward keyword matching)
        combined_score = (keyword_score * 0.7) + (sequence_score * 0.3)
        
        return min(1.0, combined_score)
    
    def calculate_location_similarity(
        self,
        query_location: Optional[str],
        event_location: Optional[Location]
    ) -> float:
        """
        Calculate location similarity.
        
        Args:
            query_location: Query location string
            event_location: Event location object
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not query_location or not event_location:
            return 0.0
        
        query_location = self.normalize_text(query_location)
        
        # Check each location component
        scores = []
        
        if event_location.city:
            city = self.normalize_text(event_location.city)
            if city in query_location or query_location in city:
                scores.append(1.0)
            else:
                scores.append(SequenceMatcher(None, query_location, city).ratio())
        
        if event_location.country:
            country = self.normalize_text(event_location.country)
            if country in query_location or query_location in country:
                scores.append(1.0)
            else:
                scores.append(SequenceMatcher(None, query_location, country).ratio())
        
        if event_location.region:
            region = self.normalize_text(event_location.region)
            if region in query_location or query_location in region:
                scores.append(1.0)
            else:
                scores.append(SequenceMatcher(None, query_location, region).ratio())
        
        # Return max score from all components
        return max(scores) if scores else 0.0
    
    def calculate_date_relevance(
        self,
        query: SearchQuery,
        event: EventData
    ) -> float:
        """
        Calculate date relevance score.
        
        Args:
            query: Search query with date range
            event: Event to evaluate
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # If no date range specified, give neutral score
        if not query.date_from and not query.date_to:
            return 0.5
        
        # If event has no date, give low score if date range specified
        if not event.event_date:
            return 0.3
        
        event_date = event.event_date
        
        # Check if event is within range
        if query.date_from and event_date < query.date_from:
            # Event is before range - calculate how far
            days_before = (query.date_from - event_date).days
            if days_before > 30:
                return 0.0
            else:
                return 1.0 - (days_before / 30.0)
        
        if query.date_to and event_date > query.date_to:
            # Event is after range - calculate how far
            days_after = (event_date - query.date_to).days
            if days_after > 30:
                return 0.0
            else:
                return 1.0 - (days_after / 30.0)
        
        # Event is within range
        return 1.0
    
    def calculate_event_type_match(
        self,
        query_type: Optional[EventType],
        event_type: EventType
    ) -> float:
        """
        Calculate event type match score.
        
        Args:
            query_type: Requested event type
            event_type: Event's actual type
            
        Returns:
            Match score (0.0 or 1.0)
        """
        if not query_type:
            return 0.5  # Neutral score if no type specified
        
        return 1.0 if query_type == event_type else 0.0
    
    def calculate_relevance_score(
        self,
        query: SearchQuery,
        event: EventData
    ) -> float:
        """
        Calculate overall relevance score for an event.
        
        Args:
            query: Search query
            event: Event to score
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Calculate individual scores
        text_score = self.calculate_text_similarity(query.phrase, event)
        location_score = self.calculate_location_similarity(query.location, event.location)
        date_score = self.calculate_date_relevance(query, event)
        type_score = self.calculate_event_type_match(query.event_type, event.event_type)
        
        # Apply weights
        weighted_score = (
            text_score * self.weights['text'] +
            location_score * self.weights['location'] +
            date_score * self.weights['date'] +
            type_score * self.weights['event_type']
        )
        
        # Adjust by event confidence
        final_score = weighted_score * event.confidence
        
        logger.debug(
            f"Relevance scores for '{event.title[:30]}...': "
            f"text={text_score:.2f}, loc={location_score:.2f}, "
            f"date={date_score:.2f}, type={type_score:.2f}, "
            f"weighted={weighted_score:.2f}, final={final_score:.2f}"
        )
        
        return final_score
    
    def match_events(
        self,
        events: List[EventData],
        query: SearchQuery,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        Match and rank events based on query.
        
        Args:
            events: List of events to match
            query: Search query
            min_score: Minimum relevance score threshold
            
        Returns:
            List of dicts with event and relevance_score, sorted by score
        """
        logger.info(f"Matching {len(events)} events against query: '{query.phrase}'")
        
        # Calculate relevance for each event
        scored_events = []
        for event in events:
            score = self.calculate_relevance_score(query, event)
            
            if score >= min_score:
                scored_events.append({
                    'event': event,
                    'relevance_score': score
                })
        
        # Sort by relevance score (descending)
        scored_events.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(
            f"Matched {len(scored_events)}/{len(events)} events "
            f"(min_score={min_score})"
        )
        
        return scored_events
    
    def filter_by_date_range(
        self,
        events: List[EventData],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[EventData]:
        """
        Filter events by date range.
        
        Args:
            events: Events to filter
            date_from: Start date (inclusive)
            date_to: End date (inclusive)
            
        Returns:
            Filtered events
        """
        if not date_from and not date_to:
            return events
        
        filtered = []
        for event in events:
            if not event.event_date:
                continue
            
            if date_from and event.event_date < date_from:
                continue
            
            if date_to and event.event_date > date_to:
                continue
            
            filtered.append(event)
        
        logger.debug(f"Date filter: {len(filtered)}/{len(events)} events")
        return filtered
    
    def filter_by_event_type(
        self,
        events: List[EventData],
        event_type: EventType
    ) -> List[EventData]:
        """
        Filter events by type.
        
        Args:
            events: Events to filter
            event_type: Event type to match
            
        Returns:
            Filtered events
        """
        filtered = [e for e in events if e.event_type == event_type]
        logger.debug(f"Type filter: {len(filtered)}/{len(events)} events")
        return filtered
    
    def filter_by_location(
        self,
        events: List[EventData],
        location: str
    ) -> List[EventData]:
        """
        Filter events by location keyword.
        
        Args:
            events: Events to filter
            location: Location keyword
            
        Returns:
            Filtered events
        """
        location_lower = location.lower()
        filtered = []
        
        for event in events:
            if not event.location:
                continue
            
            if (
                (event.location.city and location_lower in event.location.city.lower()) or
                (event.location.country and location_lower in event.location.country.lower()) or
                (event.location.region and location_lower in event.location.region.lower())
            ):
                filtered.append(event)
        
        logger.debug(f"Location filter: {len(filtered)}/{len(events)} events")
        return filtered


# Global instance
query_matcher = QueryMatcher()
