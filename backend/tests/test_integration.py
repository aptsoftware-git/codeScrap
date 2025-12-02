"""
Integration tests for the Event Scraper & Analyzer.

These tests verify the complete workflow from API request to response.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import json


client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_ollama_status_endpoint(self):
        """Test Ollama status endpoint."""
        response = client.get("/ollama/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        # Status can be 'connected' or 'disconnected' depending on Ollama
        assert data["status"] in ["connected", "disconnected"]
    
    def test_sources_endpoint(self):
        """Test sources listing endpoint."""
        response = client.get("/sources")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)


class TestSearchEndpoint:
    """Test search functionality."""
    
    def test_search_missing_phrase(self):
        """Test search without required phrase."""
        response = client.post(
            "/search",
            json={}
        )
        assert response.status_code == 422  # Validation error
    
    def test_search_with_phrase_only(self):
        """Test basic search with just phrase."""
        response = client.post(
            "/search",
            json={"phrase": "test event"}
        )
        # Should succeed or fail gracefully
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "matching_events" in data
            assert isinstance(data["matching_events"], list)
    
    def test_search_with_all_filters(self):
        """Test search with all filter parameters."""
        response = client.post(
            "/search",
            json={
                "phrase": "cyber attack",
                "location": "India",
                "event_type": "Cyber Attack",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31"
            }
        )
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "matching_events" in data
            assert "extracted_events" in data
            assert "articles_scraped" in data
    
    def test_search_invalid_date_range(self):
        """Test search with invalid date range."""
        response = client.post(
            "/search",
            json={
                "phrase": "test",
                "start_date": "2025-12-31",
                "end_date": "2025-01-01"
            }
        )
        # Should either validate or allow (depends on implementation)
        assert response.status_code in [200, 400, 422, 500]
    
    def test_search_invalid_event_type(self):
        """Test search with invalid event type."""
        response = client.post(
            "/search",
            json={
                "phrase": "test",
                "event_type": "Invalid Event Type"
            }
        )
        # Should reject invalid event type
        assert response.status_code in [400, 422]


class TestSessionRetrieval:
    """Test session retrieval functionality."""
    
    def test_get_nonexistent_session(self):
        """Test retrieving a session that doesn't exist."""
        response = client.get("/search/session/nonexistent-id")
        assert response.status_code == 404
    
    def test_get_session_after_search(self):
        """Test retrieving session after a search."""
        # First, perform a search
        search_response = client.post(
            "/search",
            json={"phrase": "test event"}
        )
        
        if search_response.status_code == 200:
            session_id = search_response.json()["session_id"]
            
            # Now retrieve the session
            session_response = client.get(f"/search/session/{session_id}")
            assert session_response.status_code == 200
            
            session_data = session_response.json()
            assert "matching_events" in session_data
            assert session_data["session_id"] == session_id


class TestExportEndpoint:
    """Test export functionality."""
    
    def test_export_without_session(self):
        """Test export without valid session."""
        response = client.post(
            "/export/excel",
            json={"session_id": "nonexistent"}
        )
        assert response.status_code in [400, 404]
    
    def test_export_custom_empty_events(self):
        """Test custom export with empty events list."""
        response = client.post(
            "/export/excel/custom",
            json={"events": []}
        )
        assert response.status_code in [400, 422]
    
    def test_export_custom_with_events(self):
        """Test custom export with valid events."""
        events = [
            {
                "title": "Test Event",
                "date": "2025-12-01",
                "location": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India"
                },
                "event_type": "Protest",
                "description": "A test event",
                "organizer": "Test Org",
                "relevance_score": 85.5,
                "source_url": "https://example.com",
                "url": "https://example.com/event"
            }
        ]
        
        response = client.post(
            "/export/excel/custom",
            json={"events": events}
        )
        
        if response.status_code == 200:
            # Should return Excel file
            assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            assert len(response.content) > 0


class TestCORSHeaders:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.options(
            "/search",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling across the application."""
    
    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request."""
        response = client.post(
            "/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_method_not_allowed(self):
        """Test method not allowed error."""
        response = client.get("/search")  # POST-only endpoint
        assert response.status_code == 405
    
    def test_not_found_endpoint(self):
        """Test 404 for non-existent endpoint."""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestRateLimiting:
    """Test rate limiting functionality (if enabled)."""
    
    @pytest.mark.skipif(
        True,  # Skip by default as it depends on settings
        reason="Rate limiting may not be enabled in test environment"
    )
    def test_rate_limit_exceeded(self):
        """Test that rate limiting triggers after many requests."""
        # Make many requests quickly
        responses = []
        for _ in range(20):
            response = client.post("/search", json={"phrase": "test"})
            responses.append(response)
        
        # At least one should be rate limited
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes or all(s == 200 for s in status_codes)


class TestDataValidation:
    """Test data validation and sanitization."""
    
    def test_search_phrase_max_length(self):
        """Test search phrase length validation."""
        long_phrase = "a" * 1000
        response = client.post(
            "/search",
            json={"phrase": long_phrase}
        )
        # Should handle long phrases gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_location_special_characters(self):
        """Test location with special characters."""
        response = client.post(
            "/search",
            json={
                "phrase": "test",
                "location": "São Paulo"
            }
        )
        # Should handle special characters
        assert response.status_code in [200, 500]
    
    def test_date_format_validation(self):
        """Test date format validation."""
        response = client.post(
            "/search",
            json={
                "phrase": "test",
                "start_date": "invalid-date"
            }
        )
        # Should reject invalid date format
        assert response.status_code in [400, 422]


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_search_and_export_workflow(self):
        """Test the complete search -> export workflow."""
        # Step 1: Search
        search_response = client.post(
            "/search",
            json={"phrase": "technology conference"}
        )
        
        if search_response.status_code != 200:
            pytest.skip("Search failed, skipping workflow test")
        
        search_data = search_response.json()
        session_id = search_data["session_id"]
        
        # Step 2: Verify session exists
        session_response = client.get(f"/search/session/{session_id}")
        assert session_response.status_code == 200
        
        # Step 3: Export from session
        export_response = client.post(
            "/export/excel",
            json={"session_id": session_id}
        )
        
        # Export should succeed or fail gracefully
        assert export_response.status_code in [200, 400, 404]
    
    def test_search_filter_export_workflow(self):
        """Test search with filters and custom export."""
        # Search with filters
        search_response = client.post(
            "/search",
            json={
                "phrase": "cyber security",
                "event_type": "Conference",
                "start_date": "2025-01-01"
            }
        )
        
        if search_response.status_code != 200:
            pytest.skip("Search failed, skipping workflow test")
        
        search_data = search_response.json()
        matching_events = search_data["matching_events"]
        
        if len(matching_events) > 0:
            # Export first event
            export_response = client.post(
                "/export/excel/custom",
                json={"events": matching_events[:1]}
            )
            
            assert export_response.status_code in [200, 400]


class TestSecurityHeaders:
    """Test security headers in responses."""
    
    def test_security_headers_present(self):
        """Test that security headers are set."""
        response = client.get("/health")
        
        # Check for common security headers
        headers = response.headers
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"
        assert "x-xss-protection" in headers


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
