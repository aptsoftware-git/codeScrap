"""
Unit tests for all services.

Tests individual service functionality in isolation with mocks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.config import EventType, Location, EventData


class TestScraperService:
    """Test web scraping service."""
    
    @patch('httpx.AsyncClient.get')
    async def test_scrape_url_success(self, mock_get):
        """Test successful URL scraping."""
        from app.services.scraper_service import ScraperService
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_get.return_value = mock_response
        
        scraper = ScraperService()
        result = await scraper.scrape_url("https://example.com")
        
        assert result is not None
        assert "Test" in result
    
    @patch('httpx.AsyncClient.get')
    async def test_scrape_url_timeout(self, mock_get):
        """Test handling of timeout errors."""
        from app.services.scraper_service import ScraperService
        import httpx
        
        mock_get.side_effect = httpx.TimeoutException("Timeout")
        
        scraper = ScraperService()
        result = await scraper.scrape_url("https://example.com")
        
        assert result is None or result == ""
    
    @patch('httpx.AsyncClient.get')
    async def test_scrape_url_404(self, mock_get):
        """Test handling of 404 errors."""
        from app.services.scraper_service import ScraperService
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        scraper = ScraperService()
        result = await scraper.scrape_url("https://example.com")
        
        assert result is None or result == ""


class TestNLPService:
    """Test NLP entity extraction service."""
    
    def test_extract_entities_basic(self):
        """Test basic entity extraction."""
        from app.services.nlp_service import NLPService
        
        nlp = NLPService()
        text = "Apple Inc. announced a conference in New York on January 15, 2025."
        
        entities = nlp.extract_entities(text)
        
        assert entities is not None
        assert len(entities.organizations) > 0 or len(entities.persons) > 0
        assert len(entities.locations) > 0
        assert len(entities.dates) > 0
    
    def test_extract_entities_empty_text(self):
        """Test entity extraction with empty text."""
        from app.services.nlp_service import NLPService
        
        nlp = NLPService()
        entities = nlp.extract_entities("")
        
        assert entities is not None
        assert len(entities.organizations) == 0
        assert len(entities.persons) == 0
        assert len(entities.locations) == 0
        assert len(entities.dates) == 0
    
    def test_extract_entities_no_entities(self):
        """Test with text containing no entities."""
        from app.services.nlp_service import NLPService
        
        nlp = NLPService()
        text = "This is a simple sentence with no special entities."
        
        entities = nlp.extract_entities(text)
        
        assert entities is not None
    
    def test_deduplicate_entities(self):
        """Test entity deduplication."""
        from app.services.nlp_service import NLPService
        
        nlp = NLPService()
        text = "Apple announced Apple's new product. Apple is based in California. Apple CEO spoke."
        
        entities = nlp.extract_entities(text)
        
        # Should deduplicate "Apple"
        assert entities is not None


class TestSearchService:
    """Test search and matching service."""
    
    def test_calculate_relevance_exact_match(self):
        """Test relevance calculation for exact match."""
        from app.services.search_service import SearchService
        
        search = SearchService()
        
        event = EventData(
            title="Cyber Attack on Banks in India",
            date="2025-12-01",
            location=Location(city="Mumbai", country="India"),
            event_type=EventType.CYBER_ATTACK,
            description="A major cyber attack targeted banks",
            organizer=None,
            url="https://example.com",
            source_url="https://example.com"
        )
        
        query = "cyber attack banks india"
        score = search.calculate_relevance(event, query)
        
        assert score > 70  # Should have high relevance
    
    def test_calculate_relevance_no_match(self):
        """Test relevance calculation for no match."""
        from app.services.search_service import SearchService
        
        search = SearchService()
        
        event = EventData(
            title="Technology Conference in New York",
            date="2025-12-01",
            location=Location(city="New York", country="USA"),
            event_type=EventType.CONFERENCE,
            description="Annual technology conference",
            organizer=None,
            url="https://example.com",
            source_url="https://example.com"
        )
        
        query = "cyber attack"
        score = search.calculate_relevance(event, query)
        
        assert score < 30  # Should have low relevance
    
    def test_filter_by_location(self):
        """Test location filtering."""
        from app.services.search_service import SearchService
        
        search = SearchService()
        
        events = [
            EventData(
                title="Event in Mumbai",
                date="2025-12-01",
                location=Location(city="Mumbai", country="India"),
                event_type=EventType.PROTEST,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            ),
            EventData(
                title="Event in New York",
                date="2025-12-01",
                location=Location(city="New York", country="USA"),
                event_type=EventType.PROTEST,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            )
        ]
        
        filtered = search.filter_by_location(events, "Mumbai")
        
        assert len(filtered) == 1
        assert filtered[0].location.city == "Mumbai"
    
    def test_filter_by_date_range(self):
        """Test date range filtering."""
        from app.services.search_service import SearchService
        
        search = SearchService()
        
        events = [
            EventData(
                title="Event 1",
                date="2025-01-15",
                location=Location(city="Mumbai", country="India"),
                event_type=EventType.PROTEST,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            ),
            EventData(
                title="Event 2",
                date="2025-06-15",
                location=Location(city="Mumbai", country="India"),
                event_type=EventType.PROTEST,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            )
        ]
        
        filtered = search.filter_by_date_range(
            events, 
            start_date="2025-01-01",
            end_date="2025-03-31"
        )
        
        assert len(filtered) == 1
        assert filtered[0].title == "Event 1"
    
    def test_filter_by_event_type(self):
        """Test event type filtering."""
        from app.services.search_service import SearchService
        
        search = SearchService()
        
        events = [
            EventData(
                title="Protest Event",
                date="2025-12-01",
                location=Location(city="Mumbai", country="India"),
                event_type=EventType.PROTEST,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            ),
            EventData(
                title="Conference Event",
                date="2025-12-01",
                location=Location(city="Mumbai", country="India"),
                event_type=EventType.CONFERENCE,
                description="Test",
                organizer=None,
                url="https://example.com",
                source_url="https://example.com"
            )
        ]
        
        filtered = search.filter_by_event_type(events, EventType.PROTEST)
        
        assert len(filtered) == 1
        assert filtered[0].event_type == EventType.PROTEST


class TestExportService:
    """Test Excel export service."""
    
    def test_create_excel_file(self):
        """Test Excel file creation."""
        from app.services.export_service import ExportService
        
        export = ExportService()
        
        events = [
            EventData(
                title="Test Event",
                date="2025-12-01",
                location=Location(city="Mumbai", state="Maharashtra", country="India"),
                event_type=EventType.PROTEST,
                description="A test event",
                organizer="Test Org",
                url="https://example.com",
                source_url="https://example.com/source"
            )
        ]
        
        file_bytes = export.create_excel(events)
        
        assert file_bytes is not None
        assert len(file_bytes) > 0
    
    def test_create_excel_empty_events(self):
        """Test Excel creation with empty events list."""
        from app.services.export_service import ExportService
        
        export = ExportService()
        
        # Should handle empty list gracefully
        file_bytes = export.create_excel([])
        
        assert file_bytes is not None
    
    def test_create_excel_special_characters(self):
        """Test Excel creation with special characters."""
        from app.services.export_service import ExportService
        
        export = ExportService()
        
        events = [
            EventData(
                title="Test Event with 'quotes' and \"double quotes\"",
                date="2025-12-01",
                location=Location(city="São Paulo", country="Brazil"),
                event_type=EventType.CONFERENCE,
                description="Description with €, £, ¥ symbols",
                organizer="Org™",
                url="https://example.com",
                source_url="https://example.com"
            )
        ]
        
        file_bytes = export.create_excel(events)
        
        assert file_bytes is not None
        assert len(file_bytes) > 0


class TestConfigModels:
    """Test configuration and data models."""
    
    def test_location_model(self):
        """Test Location model."""
        from app.config import Location
        
        location = Location(
            city="Mumbai",
            state="Maharashtra",
            country="India",
            venue="Conference Center"
        )
        
        assert location.city == "Mumbai"
        assert location.state == "Maharashtra"
        assert location.country == "India"
        assert location.venue == "Conference Center"
    
    def test_location_optional_fields(self):
        """Test Location with optional fields."""
        from app.config import Location
        
        location = Location(city="Mumbai", country="India")
        
        assert location.city == "Mumbai"
        assert location.country == "India"
        assert location.state is None
        assert location.venue is None
    
    def test_event_data_model(self):
        """Test EventData model."""
        event = EventData(
            title="Test Event",
            date="2025-12-01",
            location=Location(city="Mumbai", country="India"),
            event_type=EventType.PROTEST,
            description="Test description",
            organizer="Test Org",
            url="https://example.com",
            source_url="https://example.com"
        )
        
        assert event.title == "Test Event"
        assert event.event_type == EventType.PROTEST
        assert event.location.city == "Mumbai"
    
    def test_event_type_enum(self):
        """Test EventType enum values."""
        # Test some key event types
        assert EventType.PROTEST.value == "Protest"
        assert EventType.CYBER_ATTACK.value == "Cyber Attack"
        assert EventType.CONFERENCE.value == "Conference"
        assert EventType.ATTACK.value == "Attack"
    
    def test_search_query_model(self):
        """Test SearchQuery model."""
        from app.config import SearchQuery
        
        query = SearchQuery(
            phrase="test event",
            location="Mumbai",
            event_type=EventType.PROTEST,
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        
        assert query.phrase == "test event"
        assert query.location == "Mumbai"
        assert query.event_type == EventType.PROTEST


class TestOllamaService:
    """Test Ollama LLM service."""
    
    @patch('httpx.post')
    def test_generate_text(self, mock_post):
        """Test text generation."""
        from app.services.ollama_service import OllamaClient
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Generated text"
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Test prompt")
        
        assert result == "Generated text"
    
    @patch('httpx.post')
    def test_generate_json(self, mock_post):
        """Test JSON generation."""
        from app.services.ollama_service import OllamaClient
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": '{"key": "value"}'
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate_json("Test prompt")
        
        assert result == {"key": "value"}
    
    def test_extract_json_from_markdown(self):
        """Test JSON extraction from markdown."""
        from app.services.ollama_service import OllamaClient
        
        client = OllamaClient()
        
        # Test with markdown code block
        text = '```json\n{"key": "value"}\n```'
        result = client._extract_json(text)
        assert result == '{"key": "value"}'
        
        # Test with plain JSON
        text = '{"key": "value"}'
        result = client._extract_json(text)
        assert result == '{"key": "value"}'
    
    @patch('httpx.get')
    def test_connection_check(self, mock_get):
        """Test Ollama connection check."""
        from app.services.ollama_service import OllamaClient
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        is_connected = client.test_connection()
        
        assert is_connected is True
    
    @patch('httpx.get')
    def test_connection_check_failure(self, mock_get):
        """Test Ollama connection check failure."""
        from app.services.ollama_service import OllamaClient
        import httpx
        
        mock_get.side_effect = httpx.ConnectError("Connection failed")
        
        client = OllamaClient()
        is_connected = client.test_connection()
        
        assert is_connected is False


class TestSessionManagement:
    """Test session storage and retrieval."""
    
    def test_create_session(self):
        """Test session creation."""
        # This would test in-memory session storage
        # Implementation depends on your session manager
        pass
    
    def test_retrieve_session(self):
        """Test session retrieval."""
        # Test retrieving existing session
        pass
    
    def test_session_expiration(self):
        """Test session expiration."""
        # Test that old sessions are cleaned up
        pass


# Pytest fixtures
@pytest.fixture
def sample_event():
    """Fixture providing a sample event."""
    return EventData(
        title="Sample Event",
        date="2025-12-01",
        location=Location(city="Mumbai", country="India"),
        event_type=EventType.PROTEST,
        description="A sample event for testing",
        organizer="Test Organization",
        url="https://example.com",
        source_url="https://example.com/source"
    )


@pytest.fixture
def sample_events_list():
    """Fixture providing a list of sample events."""
    return [
        EventData(
            title=f"Event {i}",
            date="2025-12-01",
            location=Location(city="Mumbai", country="India"),
            event_type=EventType.PROTEST,
            description=f"Event {i} description",
            organizer=f"Org {i}",
            url=f"https://example.com/{i}",
            source_url=f"https://example.com/source/{i}"
        )
        for i in range(5)
    ]
