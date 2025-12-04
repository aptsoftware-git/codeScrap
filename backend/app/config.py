"""
Configuration management using pydantic-settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

# Get the root directory (two levels up from this file)
ROOT_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"  # Qwen 2.5 3B - Good balance of speed and quality
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Scraping Configuration
    default_rate_limit_seconds: int = 2
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    user_agent: str = "EventScraperBot/1.0"
    
    # Logging
    log_level: str = "DEBUG"  # Temporarily set to DEBUG for troubleshooting
    log_file: str = "logs/app.log"
    
    model_config = {
        "env_file": str(ROOT_DIR / "backend" / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
