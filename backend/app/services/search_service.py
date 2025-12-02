"""
Search service that orchestrates scraping, extraction, and matching.
Implements end-to-end search functionality for events.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from app.models import (
    SearchQuery,
    SearchResponse,
    EventData,
    ArticleContent,
    SourceConfig
)
from app.services.config_manager import config_manager
from app.services.scraper_manager import scraper_manager
from app.services.entity_extractor import entity_extractor
from app.services.event_extractor import event_extractor
from app.services.query_matcher import query_matcher


class SessionStore:
    """
    Simple in-memory session store for search results.
    Stores search results by session ID for later retrieval/export.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("SessionStore initialized")
    
    def create_session(self, query: SearchQuery, results: List[EventData]) -> str:
        """
        Create a new session and store results.
        
        Args:
            query: Original search query
            results: List of matched events
        
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = {
            "query": query,
            "results": results,
            "created_at": datetime.now(),
            "result_count": len(results)
        }
        
        logger.info(f"Created session {session_id} with {len(results)} results")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data by ID.
        
        Args:
            session_id: Session ID to retrieve
        
        Returns:
            Session data dictionary or None if not found
        """
        return self._sessions.get(session_id)
    
    def get_results(self, session_id: str) -> Optional[List[EventData]]:
        """
        Get just the results from a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of EventData or None if session not found
        """
        session = self.get_session(session_id)
        return session["results"] if session else None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Remove sessions older than specified age.
        
        Args:
            max_age_hours: Maximum session age in hours
        """
        now = datetime.now()
        to_delete = []
        
        for session_id, data in self._sessions.items():
            age = (now - data["created_at"]).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old sessions")
    
    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self._sessions)


class SearchService:
    """
    Main search service that orchestrates the entire search pipeline:
    1. Scrape articles from configured sources
    2. Extract entities and events from articles
    3. Match and rank events by relevance to query
    4. Store results in session for later retrieval
    """
    
    def __init__(self):
        self.session_store = SessionStore()
        logger.info("SearchService initialized")
    
    async def search(
        self,
        query: SearchQuery,
        max_articles: int = 50,
        min_relevance_score: float = 0.1
    ) -> SearchResponse:
        """
        Execute complete search pipeline.
        
        Args:
            query: Search query with filters
            max_articles: Maximum articles to scrape per source
            min_relevance_score: Minimum relevance score to include in results
        
        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.now()
        logger.info(f"Starting search: '{query.phrase}'")
        
        try:
            # Step 1: Get enabled sources
            sources = config_manager.get_sources(enabled_only=True)
            
            if not sources:
                logger.warning("No enabled sources found")
                return SearchResponse(
                    session_id="",
                    events=[],
                    query=query,
                    total_events=0,
                    processing_time_seconds=0.0,
                    articles_scraped=0,
                    sources_scraped=0,
                    status="no_sources",
                    message="No enabled sources configured"
                )
            
            logger.info(f"Using {len(sources)} enabled sources")
            
            # Step 2: Scrape articles
            logger.info(f"Scraping articles (max {max_articles} per source)...")
            articles = await self._scrape_articles(sources, query.phrase, max_articles)
            
            if not articles:
                logger.warning("No articles scraped")
                return SearchResponse(
                    session_id="",
                    events=[],
                    query=query,
                    total_events=0,
                    processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                    articles_scraped=0,
                    sources_scraped=len(sources),
                    status="no_articles",
                    message="No articles could be scraped from sources"
                )
            
            logger.info(f"Scraped {len(articles)} articles")
            
            # Step 3: Extract events from articles
            logger.info("Extracting events from articles...")
            events = await self._extract_events(articles)
            
            if not events:
                logger.warning("No events extracted")
                return SearchResponse(
                    session_id="",
                    events=[],
                    query=query,
                    total_events=0,
                    processing_time_seconds=(datetime.now() - start_time).total_seconds(),
                    articles_scraped=len(articles),
                    sources_scraped=len(sources),
                    status="no_events",
                    message="No events could be extracted from articles"
                )
            
            logger.info(f"Extracted {len(events)} events")
            
            # Step 4: Match and rank events by relevance
            logger.info("Matching and ranking events...")
            matched_events = self._match_events(events, query, min_relevance_score)
            
            logger.info(f"Found {len(matched_events)} relevant events")
            
            # Step 5: Create session and store results
            session_id = self.session_store.create_session(query, matched_events)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Build response
            response = SearchResponse(
                session_id=session_id,
                events=matched_events,
                query=query,
                total_events=len(matched_events),
                processing_time_seconds=processing_time,
                articles_scraped=len(articles),
                sources_scraped=len(sources),
                status="success",
                message=f"Found {len(matched_events)} relevant events"
            )
            
            logger.info(f"Search completed in {processing_time:.2f}s - {len(matched_events)} events found")
            return response
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return SearchResponse(
                session_id="",
                events=[],
                query=query,
                total_events=0,
                processing_time_seconds=processing_time,
                articles_scraped=0,
                sources_scraped=0,
                status="error",
                message=f"Search failed: {str(e)}"
            )
    
    async def _scrape_articles(
        self,
        sources: List[SourceConfig],
        query: str,
        max_articles: int
    ) -> List[ArticleContent]:
        """
        Scrape articles from configured sources.
        
        Args:
            sources: List of source configurations
            query: Search query phrase
            max_articles: Maximum articles per source
        
        Returns:
            List of scraped articles
        """
        try:
            articles = await scraper_manager.scrape_sources(
                sources=sources,
                query=query,
                max_articles_per_source=max_articles
            )
            return articles
        except Exception as e:
            logger.error(f"Article scraping failed: {e}")
            return []
    
    async def _extract_events(
        self,
        articles: List[ArticleContent]
    ) -> List[EventData]:
        """
        Extract events from articles using NLP and LLM.
        
        Args:
            articles: List of articles to process
        
        Returns:
            List of extracted events
        """
        events = []
        
        for article in articles:
            try:
                # Extract event using event extractor
                event_data = await event_extractor.extract_from_article(article)
                
                if event_data:
                    events.append(event_data)
                    logger.debug(f"Extracted event: {event_data.title[:50]}")
                
            except Exception as e:
                logger.error(f"Failed to extract event from article '{article.title[:50]}': {e}")
                continue
        
        return events
    
    def _match_events(
        self,
        events: List[EventData],
        query: SearchQuery,
        min_score: float
    ) -> List[EventData]:
        """
        Match and rank events by relevance to query.
        
        Args:
            events: List of events to match
            query: Search query
            min_score: Minimum relevance score
        
        Returns:
            List of matched events sorted by relevance (highest first)
        """
        try:
            # Use query matcher to rank events
            matched = query_matcher.match_events(
                events=events,
                query=query,
                min_score=min_score
            )
            
            # Extract just the events (already sorted by score)
            return [match['event'] for match in matched]
            
        except Exception as e:
            logger.error(f"Event matching failed: {e}")
            return events  # Return unfiltered events as fallback
    
    def get_session_results(self, session_id: str) -> Optional[List[EventData]]:
        """
        Retrieve results from a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            List of events or None if session not found
        """
        return self.session_store.get_results(session_id)
    
    def cleanup_sessions(self):
        """Clean up old sessions (older than 24 hours)."""
        self.session_store.cleanup_old_sessions()


# Global search service instance
search_service = SearchService()
