"""
Pydantic models for the Event Scraper API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID, uuid4


class EventType(str, Enum):
    """Enumeration of event types as per requirement document."""
    # Violence & Security Events
    PROTEST = "protest"
    DEMONSTRATION = "demonstration"
    ATTACK = "attack"
    EXPLOSION = "explosion"
    BOMBING = "bombing"
    SHOOTING = "shooting"
    THEFT = "theft"
    KIDNAPPING = "kidnapping"
    
    # Cyber Events
    CYBER_ATTACK = "cyber_attack"
    CYBER_INCIDENT = "cyber_incident"
    DATA_BREACH = "data_breach"
    
    # Meetings & Conferences
    CONFERENCE = "conference"
    MEETING = "meeting"
    SUMMIT = "summit"
    
    # Disasters & Accidents
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    
    # Political & Military
    ELECTION = "election"
    POLITICAL_EVENT = "political_event"
    MILITARY_OPERATION = "military_operation"
    
    # Crisis Events
    TERRORIST_ACTIVITY = "terrorist_activity"
    CIVIL_UNREST = "civil_unrest"
    HUMANITARIAN_CRISIS = "humanitarian_crisis"
    
    # Other
    OTHER = "other"


class Location(BaseModel):
    """Location information."""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": float, "lon": float}
    
    def __str__(self) -> str:
        """Return human-readable location string."""
        parts = [p for p in [self.city, self.state, self.country] if p]
        return ", ".join(parts) if parts else "Unknown"


class ExtractedEntities(BaseModel):
    """Named entities extracted from text using spaCy."""
    persons: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)


class ArticleContent(BaseModel):
    """Raw article content from web scraping."""
    id: UUID = Field(default_factory=uuid4)
    url: str
    title: Optional[str] = None
    content: str
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    source_name: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class EventData(BaseModel):
    """Structured event data extracted from article."""
    event_type: EventType
    title: str
    summary: str
    location: Location
    event_date: Optional[datetime] = None
    participants: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    casualties: Optional[Dict[str, int]] = None  # {"killed": int, "injured": int}
    impact: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)  # Extraction confidence score
    source_url: Optional[str] = None  # URL of the source article
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Event(BaseModel):
    """Complete event with source article and extracted data."""
    id: UUID = Field(default_factory=uuid4)
    article: ArticleContent
    entities: ExtractedEntities
    event_data: EventData
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class SearchQuery(BaseModel):
    """User search query parameters."""
    phrase: str = Field(..., min_length=1, description="Search phrase or keywords")
    location: Optional[str] = Field(None, description="Location filter (city, country, region)")
    event_type: Optional[EventType] = Field(None, description="Filter by event type")
    date_from: Optional[Union[datetime, date, str]] = Field(None, description="Start date filter (YYYY-MM-DD or ISO datetime)")
    date_to: Optional[Union[datetime, date, str]] = Field(None, description="End date filter (YYYY-MM-DD or ISO datetime)")
    max_results: int = Field(default=50, ge=1, le=500, description="Maximum results to return")
    
    @field_validator('date_from', 'date_to', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date string to datetime object."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            # Convert date to datetime at start of day
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            # Try to parse date-only string (YYYY-MM-DD)
            try:
                parsed_date = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return parsed_date
            except ValueError:
                # Try date-only format
                try:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                except ValueError:
                    raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD or ISO datetime")
        return v
    
    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure date_to is after date_from."""
        if v and info.data.get('date_from') and v < info.data['date_from']:
            raise ValueError('date_to must be after date_from')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SourceConfig(BaseModel):
    """Configuration for a single news source."""
    name: str
    base_url: str
    enabled: bool = True
    search_url_template: Optional[str] = None  # URL template with {query} placeholder
    rate_limit: float = Field(default=1.0, ge=0.1, description="Minimum seconds between requests")
    selectors: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # Selectors that might be in the config
    # {
    #   "article_links": "a.article-link",
    #   "title": "h1.article-title",
    #   "content": "div.article-body",
    #   "date": "time.publish-date",
    #   "author": "span.author-name"
    # }


class SearchResponse(BaseModel):
    """Response from search API."""
    session_id: str  # UUID as string
    events: List[EventData]
    query: SearchQuery
    total_events: int
    processing_time_seconds: float
    articles_scraped: int = 0
    sources_scraped: int = 0
    status: str = "success"  # success, no_sources, no_articles, no_events, error
    message: str = ""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class SourcesListResponse(BaseModel):
    """Response for listing configured sources."""
    sources: List[SourceConfig]
    total_count: int
    enabled_count: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    ollama_status: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OllamaStatusResponse(BaseModel):
    """Ollama service status response."""
    status: str
    model: str
    available_models: List[str] = Field(default_factory=list)
    base_url: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ExportRequest(BaseModel):
    """Request to export events to Excel."""
    event_ids: List[str] = Field(..., min_length=1, description="List of event IDs to export")
    session_id: UUID = Field(..., description="Session ID from search response")
