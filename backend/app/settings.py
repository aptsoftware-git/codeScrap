"""
Production configuration loader with environment variable support.
"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Event Scraper API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 120  # Timeout per LLM call in seconds
    ollama_max_articles: int = 5  # Maximum articles to process with LLM per search
    ollama_total_timeout: int = 480  # Total timeout for all LLM processing (8 minutes)
    
    # Sources
    sources_config_path: str = "../config/sources.yaml"
    
    # Scraping
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    scraper_retry_delay: int = 2
    scraper_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    scraper_respect_robots: bool = False  # Set to True for production to respect robots.txt
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 60
    rate_limit_per_domain: bool = True
    
    # Session
    session_timeout: int = 3600
    session_max_size: int = 100
    
    # Logging
    log_dir: str = "logs"
    log_file: str = "app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"
    
    # Security
    enable_security_headers: bool = False
    api_key: str = ""
    
    # Performance
    max_concurrent_scrapes: int = 5
    max_events_per_search: int = 100
    
    # NLP
    spacy_model: str = "en_core_web_sm"
    ner_confidence_threshold: float = 0.5
    
    # Query Matching Weights
    weight_text: float = 0.4
    weight_location: float = 0.25
    weight_date: float = 0.2
    weight_event_type: float = 0.15
    
    # Export
    export_max_rows: int = 1000
    export_temp_dir: str = "temp"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def log_path(self) -> Path:
        """Get full log file path."""
        return Path(self.log_dir) / self.log_file
    
    @property
    def sources_config_full_path(self) -> Path:
        """Get full path to sources config."""
        return Path(__file__).parent.parent / self.sources_config_path
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
