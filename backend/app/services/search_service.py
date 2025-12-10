"""
Search service that orchestrates scraping, extraction, and matching.
Implements end-to-end search functionality for events.
"""

import uuid
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from app.models import (
    SearchQuery,
    SearchResponse,
    EventData,
    ArticleContent,
    SourceConfig,
    SearchStatus,
    ProgressUpdate
)
from app.settings import settings
from app.services.config_manager import config_manager
from app.services.scraper_manager import scraper_manager
from app.services.entity_extractor import entity_extractor
from app.services.event_extractor import event_extractor
from app.services.query_matcher import query_matcher


class SessionStore:
    """
    In-memory session store for search results with streaming support.
    Stores search results, status, and supports cancellation.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._cancelled_sessions: set = set()  # Track cancelled sessions
        logger.info("SessionStore initialized")
    
    def create_session(
        self,
        query: SearchQuery,
        results: Optional[List[EventData]] = None,
        status: SearchStatus = SearchStatus.PENDING
    ) -> str:
        """
        Create a new session.
        
        Args:
            query: Original search query
            results: Initial list of events (empty for streaming)
            status: Initial session status
        
        Returns:
            Session ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = {
            "query": query,
            "results": results or [],
            "created_at": datetime.now(),
            "result_count": len(results) if results else 0,
            "status": status,
            "progress": {
                "current": 0,
                "total": 0,
                "percentage": 0.0,
                "message": "Initializing..."
            }
        }
        
        logger.info(f"Created session {session_id} with status {status}")
        return session_id
    
    def update_progress(
        self,
        session_id: str,
        current: int,
        total: int,
        message: str = ""
    ):
        """
        Update session progress.
        
        Args:
            session_id: Session ID
            current: Current item being processed
            total: Total items to process
            message: Status message
        """
        session = self._sessions.get(session_id)
        if session:
            percentage = (current / total * 100) if total > 0 else 0
            session["progress"] = {
                "current": current,
                "total": total,
                "percentage": round(percentage, 1),
                "message": message
            }
            logger.debug(f"Session {session_id}: {current}/{total} - {message}")
    
    def add_result(self, session_id: str, event: EventData):
        """
        Add a single result to session (for streaming).
        
        Args:
            session_id: Session ID
            event: EventData to add
        """
        session = self._sessions.get(session_id)
        if session:
            session["results"].append(event)
            session["result_count"] = len(session["results"])
            logger.debug(f"Added event to session {session_id}, total: {session['result_count']}")
    
    def update_status(self, session_id: str, status: SearchStatus):
        """
        Update session status.
        
        Args:
            session_id: Session ID
            status: New status
        """
        session = self._sessions.get(session_id)
        if session:
            session["status"] = status
            logger.info(f"Session {session_id} status: {status}")
    
    def cancel_session(self, session_id: str):
        """
        Mark session as cancelled.
        
        Args:
            session_id: Session ID to cancel
        """
        logger.info(f"[SESSION-STORE] Cancelling session {session_id}")
        logger.info(f"[SESSION-STORE] Cancelled sessions before: {self._cancelled_sessions}")
        self._cancelled_sessions.add(session_id)
        logger.info(f"[SESSION-STORE] Cancelled sessions after: {self._cancelled_sessions}")
        self.update_status(session_id, SearchStatus.CANCELLED)
        logger.warning(f"[SESSION-STORE] Session {session_id} marked as cancelled")
    
    def is_cancelled(self, session_id: str) -> bool:
        """
        Check if session is cancelled.
        
        Args:
            session_id: Session ID to check
        
        Returns:
            True if cancelled
        """
        is_cancelled = session_id in self._cancelled_sessions
        # Only log occasionally to avoid spam
        return is_cancelled
    
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
    
    def get_progress(self, session_id: str) -> Optional[ProgressUpdate]:
        """
        Get session progress.
        
        Args:
            session_id: Session ID
        
        Returns:
            ProgressUpdate or None
        """
        session = self.get_session(session_id)
        if session and "progress" in session:
            prog = session["progress"]
            return ProgressUpdate(
                current=prog["current"],
                total=prog["total"],
                status=prog["message"],
                percentage=prog["percentage"]
            )
        return None
    
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
            self._cancelled_sessions.discard(session_id)
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
        max_articles_to_process: int = 50,
        min_relevance_score: float = 0.1
    ) -> SearchResponse:
        """
        Execute complete search pipeline.
        
        Args:
            query: Search query with filters
            max_articles_to_process: Maximum articles to process per source (DEPRECATED - use global/source config)
            min_relevance_score: Minimum relevance score to include in results
        
        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.now()
        
        # Enhance search phrase with date context for better relevance
        search_phrase = query.phrase
        if query.date_from or query.date_to:
            if query.date_from and query.date_to:
                # Format: "bombing in kabul January 2023 to February 2023"
                date_from_str = query.date_from.strftime('%B %Y') if isinstance(query.date_from, datetime) else str(query.date_from)
                date_to_str = query.date_to.strftime('%B %Y') if isinstance(query.date_to, datetime) else str(query.date_to)
                if date_from_str == date_to_str:
                    search_phrase = f"{query.phrase} {date_from_str}"
                else:
                    search_phrase = f"{query.phrase} {date_from_str} to {date_to_str}"
            elif query.date_from:
                date_from_str = query.date_from.strftime('%B %Y') if isinstance(query.date_from, datetime) else str(query.date_from)
                search_phrase = f"{query.phrase} after {date_from_str}"
            elif query.date_to:
                date_to_str = query.date_to.strftime('%B %Y') if isinstance(query.date_to, datetime) else str(query.date_to)
                search_phrase = f"{query.phrase} before {date_to_str}"
        else:
            # No date specified - add "recent" for more relevant results
            search_phrase = f"{query.phrase} recent"
        
        logger.info(f"Starting search: '{search_phrase}' (original: '{query.phrase}')")
        
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
            
            # Step 2: Scrape articles (uses global/source config)
            logger.info(f"Scraping articles...")
            articles = await self._scrape_articles(sources, search_phrase, max_articles_to_process)
            
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
        max_articles_to_process: int,
        session_id: Optional[str] = None
    ) -> List[ArticleContent]:
        """
        Scrape articles from configured sources with cancellation support.
        
        Args:
            sources: List of source configurations
            query: Search query phrase
            max_articles_to_process: Maximum articles to process per source (can be overridden by source config)
            session_id: Optional session ID for cancellation checks
        
        Returns:
            List of scraped articles
        """
        all_articles = []
        seen_urls = set()  # Track URLs to avoid duplicates
        
        try:
            logger.info(f"[SCRAPING] Starting scraping from {len(sources)} sources for query: '{query}' - Session: {session_id}")
            
            for idx, source in enumerate(sources, 1):
                # Check for cancellation before each source
                logger.info(f"[CANCEL-CHECK] Before source {idx}/{len(sources)} ({source.name}) - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id) if session_id else False}")
                if session_id and self.session_store.is_cancelled(session_id):
                    logger.warning(f"[CANCELLED] Search cancelled for session {session_id} during scraping at source {source.name}")
                    return all_articles  # Return articles collected so far
                
                if not source.enabled:
                    logger.debug(f"Skipping disabled source: {source.name}")
                    continue
                
                try:
                    logger.info(f"[SCRAPING] Starting source {idx}/{len(sources)}: {source.name} - Session {session_id}")
                    # Scrape from this source (pass None to use source config or global defaults)
                    articles = await scraper_manager.scrape_search_results(
                        source,
                        query,
                        max_search_results=None,  # Use source config or global default
                        max_articles_to_process=None,  # Use source config or global default
                        cancellation_check=lambda: self.session_store.is_cancelled(session_id) if session_id else False
                    )
                    
                    # Filter out duplicate URLs
                    unique_articles = []
                    duplicate_count = 0
                    for article in articles:
                        if article.url not in seen_urls:
                            seen_urls.add(article.url)
                            unique_articles.append(article)
                        else:
                            duplicate_count += 1
                            logger.debug(f"Skipping duplicate URL from {source.name}: {article.url}")
                    
                    if duplicate_count > 0:
                        logger.info(f"[DUPLICATE-FILTER] Filtered {duplicate_count} duplicate URL(s) from {source.name}")
                    
                    all_articles.extend(unique_articles)
                    logger.info(f"[SCRAPING] Got {len(unique_articles)} unique articles from {source.name} ({duplicate_count} duplicates filtered) - Session {session_id}")
                    
                    # Check for cancellation after each source
                    logger.info(f"[CANCEL-CHECK] After source {idx}/{len(sources)} ({source.name}) - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id) if session_id else False}")
                    if session_id and self.session_store.is_cancelled(session_id):
                        logger.warning(f"[CANCELLED] Search cancelled for session {session_id} after scraping {source.name}")
                        return all_articles  # Return articles collected so far
                    
                except Exception as e:
                    logger.error(f"Error scraping {source.name}: {e}")
                    continue
            
            logger.info(f"[SCRAPING] Total unique articles scraped: {len(all_articles)} (from {len(seen_urls)} unique URLs) - Session {session_id}")
            return all_articles
            
        except Exception as e:
            logger.error(f"Article scraping failed: {e}")
            return all_articles  # Return what we have so far
    
    async def _extract_events(
        self,
        articles: List[ArticleContent]
    ) -> List[EventData]:
        """
        Extract events from articles using NLP and LLM with timeout protection.
        
        Args:
            articles: List of articles to process
        
        Returns:
            List of extracted events
        """
        events = []
        
        # Limit articles processed by LLM to improve performance
        max_articles_to_process = settings.max_articles_to_process
        articles_to_process = articles[:max_articles_to_process]
        
        if len(articles) > max_articles_to_process:
            logger.info(f"Processing top {max_articles_to_process} of {len(articles)} articles with LLM")
        
        # Set overall timeout for LLM processing
        total_timeout = settings.ollama_total_timeout
        start_time = datetime.now()
        
        logger.info(f"Starting parallel LLM extraction with {total_timeout}s total timeout, max {settings.max_concurrent_llm} concurrent")
        
        # Process articles in parallel batches for better CPU utilization
        async def process_article_with_timeout(article, index):
            """Process a single article with timeout."""
            try:
                elapsed = (datetime.now() - start_time).total_seconds()
                remaining = total_timeout - elapsed
                
                if remaining <= 0:
                    logger.warning(f"Total timeout reached for article {index}")
                    return None
                
                article_timeout = min(remaining, settings.ollama_timeout)
                logger.debug(f"Processing article {index}/{len(articles_to_process)} with {article_timeout:.0f}s timeout")
                
                event_data = await asyncio.wait_for(
                    event_extractor.extract_from_article(article),
                    timeout=article_timeout
                )
                
                if event_data:
                    logger.debug(f"Extracted event {index}: {event_data.title[:50]}")
                return event_data
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout extracting event from article '{article.title[:50]}' after {article_timeout:.0f}s")
                return None
            except Exception as e:
                logger.error(f"Failed to extract event from article '{article.title[:50]}': {e}")
                return None
        
        # Process articles in batches to limit concurrency
        batch_size = settings.max_concurrent_llm
        for batch_start in range(0, len(articles_to_process), batch_size):
            batch_end = min(batch_start + batch_size, len(articles_to_process))
            batch = articles_to_process[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: articles {batch_start+1}-{batch_end}/{len(articles_to_process)}")
            
            # Process batch in parallel
            tasks = [
                process_article_with_timeout(article, batch_start + i + 1)
                for i, article in enumerate(batch)
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful extractions
            for result in batch_results:
                if isinstance(result, EventData):
                    events.append(result)
        
        elapsed_total = (datetime.now() - start_time).total_seconds()
        logger.info(f"LLM extraction completed: {len(events)} events from {len(articles_to_process)} articles in {elapsed_total:.1f}s")
        
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
    
    async def search_stream(
        self,
        query: SearchQuery,
        session_id: str,
        max_articles_to_process: int = 50,
        min_relevance_score: float = 0.1,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ):
        """
        Execute search pipeline with real-time streaming updates.
        Yields events as they are extracted (for SSE).
        
        Args:
            query: Search query with filters
            session_id: Pre-created session ID
            max_articles_to_process: Maximum articles to process (DEPRECATED - use global/source config)
            min_relevance_score: Minimum relevance score
        
        Yields:
            Dict with event_type and data for SSE streaming
        """
        start_time = datetime.now()
        
        # Enhance search phrase with date context for better relevance
        search_phrase = query.phrase
        if query.date_from or query.date_to:
            if query.date_from and query.date_to:
                date_from_str = query.date_from.strftime('%B %Y') if isinstance(query.date_from, datetime) else str(query.date_from)
                date_to_str = query.date_to.strftime('%B %Y') if isinstance(query.date_to, datetime) else str(query.date_to)
                if date_from_str == date_to_str:
                    search_phrase = f"{query.phrase} {date_from_str}"
                else:
                    search_phrase = f"{query.phrase} {date_from_str} to {date_to_str}"
            elif query.date_from:
                date_from_str = query.date_from.strftime('%B %Y') if isinstance(query.date_from, datetime) else str(query.date_from)
                search_phrase = f"{query.phrase} after {date_from_str}"
            elif query.date_to:
                date_to_str = query.date_to.strftime('%B %Y') if isinstance(query.date_to, datetime) else str(query.date_to)
                search_phrase = f"{query.phrase} before {date_to_str}"
        else:
            # No date specified - add "recent" for more relevant results
            search_phrase = f"{query.phrase} recent"
        
        logger.info(f"Starting streaming search for session {session_id}: '{search_phrase}' (original: '{query.phrase}')")
        
        try:
            # Update status to processing
            self.session_store.update_status(session_id, SearchStatus.PROCESSING)
            
            # Step 1: Get enabled sources
            yield {
                "event_type": "progress",
                "data": {"message": "Loading sources...", "current": 0, "total": 100, "percentage": 0}
            }
            
            sources = config_manager.get_sources(enabled_only=True)
            
            if not sources:
                self.session_store.update_status(session_id, SearchStatus.ERROR)
                yield {
                    "event_type": "error",
                    "data": {"message": "No enabled sources configured"}
                }
                return
            
            # Step 2: Scrape articles
            yield {
                "event_type": "progress",
                "data": {"message": f"Scraping articles from {len(sources)} source(s)...", "current": 10, "total": 100, "percentage": 10}
            }
            
            # Check for cancellation before starting scraping (can be slow)
            logger.info(f"[CANCEL-CHECK] Before scraping - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id)}")
            if self.session_store.is_cancelled(session_id):
                logger.warning(f"[CANCELLED] Search cancelled for session {session_id} before scraping")
                yield {
                    "event_type": "cancelled",
                    "data": {"message": "Search cancelled by user"}
                }
                return
            
            logger.info(f"[SCRAPING] Starting scraping for session {session_id}")
            articles = await self._scrape_articles(sources, search_phrase, max_articles_to_process, session_id)
            logger.info(f"[SCRAPING] Completed scraping for session {session_id} - Got {len(articles)} articles")
            
            # Check for cancellation after scraping
            logger.info(f"[CANCEL-CHECK] After scraping - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id)}")
            if self.session_store.is_cancelled(session_id):
                logger.warning(f"[CANCELLED] Search cancelled for session {session_id} after scraping")
                yield {
                    "event_type": "cancelled",
                    "data": {"message": "Search cancelled by user"}
                }
                return
            
            if not articles:
                self.session_store.update_status(session_id, SearchStatus.COMPLETED)
                yield {
                    "event_type": "complete",
                    "data": {
                        "message": "No articles found",
                        "total_events": 0,
                        "processing_time": (datetime.now() - start_time).total_seconds()
                    }
                }
                return
            
            total_articles = len(articles)
            logger.info(f"Scraped {total_articles} articles for session {session_id}")
            
            # Step 3: Extract events from articles ONE BY ONE (streaming)
            yield {
                "event_type": "progress",
                "data": {
                    "message": f"Processing {total_articles} article(s)...",
                    "current": 20,
                    "total": 100,
                    "percentage": 20
                }
            }
            
            extracted_count = 0
            
            for idx, article in enumerate(articles, 1):
                # Check for cancellation before each article
                logger.info(f"[CANCEL-CHECK] Before article {idx}/{total_articles} - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id)}")
                if self.session_store.is_cancelled(session_id):
                    logger.warning(f"[CANCELLED] Search cancelled for session {session_id} at article {idx}/{total_articles}")
                    yield {
                        "event_type": "cancelled",
                        "data": {
                            "message": f"Search cancelled. Extracted {extracted_count} event(s).",
                            "total_events": extracted_count
                        }
                    }
                    return
                
                # Update progress
                progress_percentage = 20 + (idx / total_articles * 70)  # 20-90%
                self.session_store.update_progress(
                    session_id,
                    current=idx,
                    total=total_articles,
                    message=f"Processing article {idx}/{total_articles}..."
                )
                
                yield {
                    "event_type": "progress",
                    "data": {
                        "message": f"Processing article {idx}/{total_articles}: {article.title[:50]}...",
                        "current": idx,
                        "total": total_articles,
                        "percentage": round(progress_percentage, 1)
                    }
                }
                
                # Extract event from article
                try:
                    # Check cancellation BEFORE starting LLM extraction (expensive operation)
                    logger.info(f"[CANCEL-CHECK] Before LLM extraction article {idx} - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id)}")
                    if self.session_store.is_cancelled(session_id):
                        logger.warning(f"[CANCELLED] Search cancelled for session {session_id} before extracting article {idx}")
                        yield {
                            "event_type": "cancelled",
                            "data": {
                                "message": f"Search cancelled. Extracted {extracted_count} event(s).",
                                "total_events": extracted_count
                            }
                        }
                        return
                    
                    logger.info(f"[LLM] Starting extraction for article {idx}/{total_articles} - Session {session_id}")
                    event, metadata = await event_extractor.extract_from_article(
                        article,
                        llm_provider=llm_provider,
                        llm_model=llm_model
                    )
                    logger.info(f"[LLM] Completed extraction for article {idx}/{total_articles} - Session {session_id} - Provider: {metadata.get('provider', 'unknown')}")
                    
                    # Check cancellation AFTER extraction completes (in case it was cancelled during LLM call)
                    logger.info(f"[CANCEL-CHECK] After LLM extraction article {idx} - Session {session_id} cancelled: {self.session_store.is_cancelled(session_id)}")
                    if self.session_store.is_cancelled(session_id):
                        logger.warning(f"[CANCELLED] Search cancelled for session {session_id} after extracting article {idx}")
                        yield {
                            "event_type": "cancelled",
                            "data": {
                                "message": f"Search cancelled. Extracted {extracted_count} event(s).",
                                "total_events": extracted_count
                            }
                        }
                        return
                    
                    if event:
                        # Match event against query
                        matched_events = self._match_events([event], query, min_relevance_score)
                        
                        if matched_events:
                            # Event is relevant - add to session and stream it
                            self.session_store.add_result(session_id, matched_events[0])
                            extracted_count += 1
                            
                            # Stream the event to frontend immediately
                            # Use model_dump(mode='json') to properly serialize datetime objects
                            yield {
                                "event_type": "event",
                                "data": {
                                    "event": matched_events[0].model_dump(mode='json'),
                                    "index": extracted_count,
                                    "article_index": idx,
                                    "total_articles": total_articles
                                }
                            }
                            
                            logger.info(f"✅ Session {session_id}: Extracted event {extracted_count} from article {idx}/{total_articles}")
                        else:
                            logger.debug(f"Event from article {idx} not relevant enough (score < {min_relevance_score})")
                    else:
                        logger.warning(f"Failed to extract event from article {idx}")
                        
                except Exception as e:
                    logger.error(f"Error extracting event from article {idx}: {e}")
                    # Continue with next article
                    continue
            
            # Step 4: Complete
            processing_time = (datetime.now() - start_time).total_seconds()
            self.session_store.update_status(session_id, SearchStatus.COMPLETED)
            self.session_store.update_progress(
                session_id,
                current=total_articles,
                total=total_articles,
                message=f"Completed! Found {extracted_count} event(s)."
            )
            
            yield {
                "event_type": "complete",
                "data": {
                    "message": f"Search completed. Found {extracted_count} event(s).",
                    "total_events": extracted_count,
                    "articles_processed": total_articles,
                    "processing_time": round(processing_time, 2)
                }
            }
            
            logger.info(f"✅ Streaming search completed for session {session_id}: {extracted_count} events in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Streaming search failed for session {session_id}: {e}", exc_info=True)
            self.session_store.update_status(session_id, SearchStatus.ERROR)
            yield {
                "event_type": "error",
                "data": {"message": f"Search failed: {str(e)}"}
            }
    
    def cleanup_sessions(self):
        """Clean up old sessions (older than 24 hours)."""
        self.session_store.cleanup_old_sessions()


# Global search service instance
search_service = SearchService()
