"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from loguru import logger

from app.config import settings
from app.utils.logger import setup_logging
from app.services.ollama_service import OllamaClient
from app.services.config_manager import config_manager
from app.services.event_extractor import event_extractor
from app.services.search_service import search_service
from app.services.excel_exporter import excel_exporter
from app.models import (
    SourcesListResponse,
    ArticleContent,
    EventData,
    ExtractedEntities,
    SearchQuery,
    SearchResponse
)

# Setup logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Event Scraper API",
    version="1.0.0",
    description="Web scraping tool for event extraction and summarization"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Ollama client
ollama_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global ollama_client
    
    logger.info("Starting Event Scraper API...")
    logger.info(f"Ollama URL: {settings.ollama_url}")
    logger.info(f"Ollama Model: {settings.ollama_model}")
    
    # Initialize Ollama client
    try:
        ollama_client = OllamaClient(
            base_url=settings.ollama_url,
            default_model=settings.ollama_model
        )
        logger.info("Ollama client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ollama client: {e}")
        logger.warning("API will start but Ollama features may not work")
    
    # Load source configurations
    try:
        sources = config_manager.load_sources()
        logger.info(f"Loaded {len(sources)} sources ({config_manager.get_enabled_count()} enabled)")
    except FileNotFoundError:
        logger.warning("sources.yaml not found - create it in config/ directory")
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Event Scraper API...")


# Health Check Endpoints

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dictionary with health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/v1/ollama/status")
async def ollama_status():
    """
    Check Ollama connection status.
    
    Returns:
        Dictionary with Ollama connection status and configuration
    """
    if ollama_client is None:
        return {
            "status": "not_initialized",
            "error": "Ollama client not initialized"
        }
    
    try:
        # Test connection
        is_connected = ollama_client.test_connection()
        
        return {
            "status": "connected" if is_connected else "disconnected",
            "model": ollama_client.default_model,
            "base_url": ollama_client.base_url,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ollama status check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "model": settings.ollama_model,
            "base_url": settings.ollama_url,
            "timestamp": datetime.now().isoformat()
        }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Dictionary with API information and available endpoints
    """
    return {
        "name": "Event Scraper API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/v1/health",
            "ollama_status": "/api/v1/ollama/status",
            "sources": "/api/v1/sources",
            "search": "/api/v1/search",
            "export_excel": "/api/v1/export/excel",
            "extract_event": "/api/v1/extract/event",
            "extract_event_simple": "/api/v1/extract/event/simple",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Configuration Endpoints

@app.get("/api/v1/sources", response_model=SourcesListResponse)
async def get_sources(enabled_only: bool = True):
    """
    Get list of configured news sources.
    
    Args:
        enabled_only: If True, return only enabled sources (default: True)
    
    Returns:
        SourcesListResponse with list of sources and counts
    """
    try:
        sources = config_manager.get_sources(enabled_only=enabled_only)
        
        return SourcesListResponse(
            sources=sources,
            total_count=config_manager.get_total_count(),
            enabled_count=config_manager.get_enabled_count()
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="sources.yaml configuration file not found. Please create config/sources.yaml"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Error retrieving sources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sources: {str(e)}")


# Search Endpoint

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_events(
    query: SearchQuery,
    max_articles: int = 50,
    min_relevance_score: float = 0.1
):
    """
    Execute end-to-end event search.
    
    This endpoint orchestrates the complete search pipeline:
    1. Scrapes articles from configured sources
    2. Extracts entities and events from articles
    3. Matches and ranks events by relevance to query
    4. Stores results in session for later retrieval/export
    
    Args:
        query: SearchQuery with phrase, filters, and date range
        max_articles: Maximum articles to scrape per source (default: 50)
        min_relevance_score: Minimum relevance score (0.0-1.0) to include results (default: 0.1)
    
    Returns:
        SearchResponse with matched events, session ID, and metadata
    
    Example:
        ```
        POST /api/v1/search
        {
            "phrase": "protest in Mumbai",
            "location": "India",
            "event_type": "protest",
            "date_from": "2025-11-01",
            "date_to": "2025-12-31"
        }
        ```
    """
    try:
        logger.info(f"Search request: '{query.phrase}' (max_articles={max_articles}, min_score={min_relevance_score})")
        
        # Execute search pipeline
        response = await search_service.search(
            query=query,
            max_articles=max_articles,
            min_relevance_score=min_relevance_score
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Search endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/api/v1/search/session/{session_id}")
async def get_session_results(session_id: str):
    """
    Retrieve results from a previous search session.
    
    Args:
        session_id: Session ID from search response
    
    Returns:
        List of events from the session
    """
    try:
        results = search_service.get_session_results(session_id)
        
        if results is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or expired"
            )
        
        return {
            "session_id": session_id,
            "events": results,
            "total_events": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session: {str(e)}"
        )


# Excel Export Endpoints

@app.post("/api/v1/export/excel")
async def export_events_to_excel(session_id: str, include_metadata: bool = True):
    """
    Export events from a session to Excel file.
    
    Args:
        session_id: Session ID from search response
        include_metadata: Whether to include summary/metadata sheet (default: True)
    
    Returns:
        Excel file download (streaming response)
    
    Example:
        ```
        POST /api/v1/export/excel?session_id=abc-123&include_metadata=true
        ```
    """
    try:
        # Retrieve events from session
        events = search_service.get_session_results(session_id)
        
        if events is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found or expired"
            )
        
        if not events:
            raise HTTPException(
                status_code=400,
                detail="Session has no events to export"
            )
        
        logger.info(f"Exporting {len(events)} events from session {session_id}")
        
        # Generate Excel file
        excel_bytes = excel_exporter.export_to_bytes(
            events=events,
            include_metadata=include_metadata
        )
        
        # Generate filename
        filename = excel_exporter.get_default_filename()
        
        # Return as streaming response
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Excel export failed: {str(e)}"
        )


@app.post("/api/v1/export/excel/custom")
async def export_custom_events_to_excel(
    events: list[EventData],
    include_metadata: bool = True
):
    """
    Export custom list of events to Excel file.
    
    This endpoint allows exporting a custom selection of events
    without requiring a session ID.
    
    Args:
        events: List of EventData objects to export
        include_metadata: Whether to include summary/metadata sheet (default: True)
    
    Returns:
        Excel file download (streaming response)
    
    Example:
        ```
        POST /api/v1/export/excel/custom
        {
            "events": [...],
            "include_metadata": true
        }
        ```
    """
    try:
        if not events:
            raise HTTPException(
                status_code=400,
                detail="No events provided for export"
            )
        
        logger.info(f"Exporting {len(events)} custom events")
        
        # Generate Excel file
        excel_bytes = excel_exporter.export_to_bytes(
            events=events,
            include_metadata=include_metadata
        )
        
        # Generate filename
        filename = excel_exporter.get_default_filename()
        
        # Return as streaming response
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom Excel export failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Excel export failed: {str(e)}"
        )


# Event Extraction Endpoints

@app.post("/api/v1/extract/event", response_model=EventData)
async def extract_event_from_text(article: ArticleContent):
    """
    Extract event data from article content using Ollama LLM.
    
    Args:
        article: ArticleContent object with title, content, url, etc.
    
    Returns:
        EventData object with extracted event information
    """
    if not event_extractor.is_available():
        raise HTTPException(
            status_code=503,
            detail="Event extraction service not available. Check Ollama connection."
        )
    
    try:
        logger.info(f"Extracting event from article: {article.title[:50]}...")
        
        event_data = await event_extractor.extract_from_article(article)
        
        if event_data is None:
            raise HTTPException(
                status_code=422,
                detail="Failed to extract event data. LLM may have returned invalid format."
            )
        
        return event_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event extraction failed: {str(e)}")


@app.post("/api/v1/extract/event/simple")
async def extract_event_simple(
    title: str,
    content: str,
    url: str = None
):
    """
    Extract event data from simple text inputs (convenience endpoint).
    
    Args:
        title: Article title
        content: Article content
        url: Optional article URL
    
    Returns:
        EventData object with extracted event information
    """
    if not event_extractor.is_available():
        raise HTTPException(
            status_code=503,
            detail="Event extraction service not available. Check Ollama connection."
        )
    
    try:
        logger.info(f"Extracting event from: {title[:50]}...")
        
        event_data = await event_extractor.extract_event(
            title=title,
            content=content,
            url=url
        )
        
        if event_data is None:
            raise HTTPException(
                status_code=422,
                detail="Failed to extract event data. LLM may have returned invalid format."
            )
        
        return event_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event extraction failed: {str(e)}")


# Development/Testing endpoint
@app.get("/api/v1/test/ollama")
async def test_ollama_generation():
    """
    Test Ollama generation with a simple prompt.
    
    Returns:
        Dictionary with test prompt and generated response
    """
    if ollama_client is None:
        raise HTTPException(status_code=503, detail="Ollama client not initialized")
    
    try:
        test_prompt = "Say 'Hello, World!' in a friendly way."
        response = ollama_client.generate(test_prompt)
        
        return {
            "status": "success",
            "model": ollama_client.default_model,
            "prompt": test_prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ollama test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
