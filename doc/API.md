# Event Scraper API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Production URL:** `https://api.yourdomain.com/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## Authentication

Currently, the API does not require authentication for most endpoints. If `API_KEY` is set in the backend configuration, include it in requests:

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T18:30:00Z"
}
```

---

### Ollama Status

**GET** `/ollama/status`

Check Ollama connection and model status.

**Response:**
```json
{
  "status": "connected",
  "model": "llama3.1:8b",
  "base_url": "http://localhost:11434"
}
```

---

### Get Sources

**GET** `/sources`

Retrieve configured news sources.

**Response:**
```json
{
  "sources": [
    {
      "name": "Example News",
      "base_url": "https://example.com",
      "enabled": true,
      "category": "general"
    }
  ],
  "total": 5,
  "enabled": 3
}
```

---

### Search Events

**POST** `/search`

Search for events based on query parameters.

**Request Body:**
```json
{
  "phrase": "protest in Mumbai",
  "location": "India",
  "event_type": "protest",
  "date_from": "2025-01-01",
  "date_to": "2025-12-31"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phrase | string | Yes | Search phrase/keywords |
| location | string | No | Location filter (city, country, etc.) |
| event_type | string | No | Event type (see EventType enum) |
| date_from | string | No | Start date (ISO 8601: YYYY-MM-DD) |
| date_to | string | No | End date (ISO 8601: YYYY-MM-DD) |

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": {
    "phrase": "protest in Mumbai",
    "location": "India",
    "event_type": "protest"
  },
  "events": [
    {
      "title": "Protest near refinery in Mumbai",
      "date": "2025-03-15",
      "location": {
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India"
      },
      "description": "Large demonstration organized...",
      "event_type": "protest",
      "organizer": "Workers Union",
      "relevance_score": 0.87,
      "source_url": "https://example.com/article/12345",
      "url": "https://example.com/article/12345"
    }
  ],
  "total_scraped": 25,
  "total_extracted": 18,
  "total_matched": 5,
  "processing_time": 45.32,
  "sources_scraped": ["Example News", "Another Source"]
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `500 Internal Server Error` - Server error

---

### Get Session

**GET** `/search/session/{session_id}`

Retrieve results from a previous search session.

**Parameters:**
- `session_id` (path): Session UUID

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": {...},
  "events": [...],
  "total_scraped": 25,
  "total_extracted": 18,
  "total_matched": 5,
  "processing_time": 45.32,
  "sources_scraped": ["..."],
  "timestamp": "2025-12-02T18:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Session not found or expired

---

### Export to Excel (Session)

**POST** `/export/excel`

Export events from a session to Excel.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- File download with name: `events_{timestamp}.xlsx`

**Status Codes:**
- `200 OK` - File download
- `404 Not Found` - Session not found
- `500 Internal Server Error` - Export error

---

### Export to Excel (Custom)

**POST** `/export/excel/custom`

Export custom selection of events to Excel.

**Request Body:**
```json
{
  "events": [
    {
      "title": "Event 1",
      "date": "2025-03-15",
      "location": {...},
      "description": "...",
      "event_type": "protest"
    }
  ],
  "query": {
    "phrase": "protest in Mumbai"
  }
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- File download

**Status Codes:**
- `200 OK` - File download
- `400 Bad Request` - Invalid events data
- `500 Internal Server Error` - Export error

---

## Data Models

### EventType Enum

```python
class EventType(str, Enum):
    # Violence & Security
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
```

### Location

```json
{
  "city": "string",
  "state": "string",
  "country": "string",
  "region": "string"
}
```

### EventData

```json
{
  "title": "string",
  "date": "string (ISO 8601 date)",
  "location": "Location object",
  "description": "string",
  "url": "string (URL)",
  "event_type": "string (EventType enum)",
  "organizer": "string",
  "relevance_score": "float (0.0-1.0)",
  "source_url": "string (URL)"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

**400 Bad Request:**
```json
{
  "detail": "Search phrase is required"
}
```

**404 Not Found:**
```json
{
  "detail": "Session not found or expired"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error occurred. Please check logs."
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Ollama service is not available"
}
```

---

## Rate Limiting

**Default limits:**
- 10 requests per minute per IP
- Search endpoint: 5 requests per minute
- Export endpoint: 10 requests per minute

**Rate limit headers:**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1638360000
```

**Rate limit exceeded response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds."
}
```

---

## Examples

### Example 1: Search for Protests

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "phrase": "protest refinery",
    "location": "India",
    "event_type": "protest",
    "date_from": "2025-01-01"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123",
  "events": [
    {
      "title": "Workers protest at refinery",
      "date": "2025-03-15",
      "location": {
        "city": "Jamnagar",
        "state": "Gujarat",
        "country": "India"
      },
      "description": "Labor union organized protest...",
      "event_type": "protest",
      "relevance_score": 0.92
    }
  ],
  "total_matched": 1,
  "processing_time": 32.5
}
```

### Example 2: Search for Cyber Incidents

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "phrase": "data breach bank",
    "event_type": "data_breach",
    "date_from": "2025-01-01",
    "date_to": "2025-06-30"
  }'
```

### Example 3: Export Results

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/export/excel \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123"}' \
  --output events.xlsx
```

### Example 4: Get Session Results

**Request:**
```bash
curl http://localhost:8000/api/v1/search/session/abc-123
```

---

## Interactive API Documentation

The API provides interactive Swagger UI documentation:

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- Try API calls interactively
- See request/response schemas
- Download OpenAPI specification

---

## SDK Examples

### Python

```python
import requests

# Search for events
response = requests.post(
    'http://localhost:8000/api/v1/search',
    json={
        'phrase': 'protest in Mumbai',
        'event_type': 'protest'
    }
)

data = response.json()
print(f"Found {data['total_matched']} events")

# Export to Excel
session_id = data['session_id']
response = requests.post(
    'http://localhost:8000/api/v1/export/excel',
    json={'session_id': session_id}
)

with open('events.xlsx', 'wb') as f:
    f.write(response.content)
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const fs = require('fs');

// Search for events
async function searchEvents() {
  const response = await axios.post('http://localhost:8000/api/v1/search', {
    phrase: 'protest in Mumbai',
    event_type: 'protest'
  });
  
  console.log(`Found ${response.data.total_matched} events`);
  return response.data.session_id;
}

// Export to Excel
async function exportToExcel(sessionId) {
  const response = await axios.post(
    'http://localhost:8000/api/v1/export/excel',
    { session_id: sessionId },
    { responseType: 'arraybuffer' }
  );
  
  fs.writeFileSync('events.xlsx', response.data);
}

// Run
searchEvents().then(exportToExcel);
```

### cURL

```bash
# Complete workflow
SESSION_ID=$(curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"phrase":"protest"}' \
  | jq -r '.session_id')

curl -X POST http://localhost:8000/api/v1/export/excel \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\"}" \
  --output events.xlsx
```

---

## Changelog

### Version 1.0.0 (2025-12-02)
- Initial release
- Search endpoint with filtering
- Excel export functionality
- Session management
- Health checks

---

## Support

For API support:
- Documentation: http://localhost:8000/docs
- GitHub Issues: https://github.com/yourusername/event-scraper/issues
- Email: api-support@yourdomain.com

---

**End of API Documentation**
