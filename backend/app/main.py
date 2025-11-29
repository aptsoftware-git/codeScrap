"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from loguru import logger

from app.config import settings
from app.utils.logger import setup_logging
from app.services.ollama_service import OllamaClient

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
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


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
