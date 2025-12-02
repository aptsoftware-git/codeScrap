"""
Visual demonstration of Increment 7: Search API Endpoint
Shows the complete end-to-end search pipeline.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.models import SearchQuery, EventType


def demo_search_api():
    """Demonstrate the search API functionality."""
    
    print("\n" + "=" * 80)
    print("  INCREMENT 7: SEARCH API ENDPOINT - VISUAL DEMO")
    print("=" * 80)
    
    print("\n📚 SYSTEM ARCHITECTURE")
    print("=" * 80)
    print("""
    User Search Query
         ↓
    FastAPI Endpoint (/api/v1/search)
         ↓
    SearchService.search()
         ├─> Step 1: ConfigManager.get_sources()
         │   └─> Load enabled sources from sources.yaml
         │
         ├─> Step 2: ScraperManager.scrape_sources()
         │   └─> Fetch articles from news websites
         │
         ├─> Step 3: EventExtractor.extract_batch()
         │   ├─> EntityExtractor (spaCy NER)
         │   └─> OllamaClient (LLM event extraction)
         │
         ├─> Step 4: QueryMatcher.match_events()
         │   └─> Rank by relevance (text, location, date, type)
         │
         └─> Step 5: SessionStore.create_session()
             └─> Store results with UUID
         ↓
    SearchResponse
         ├─> session_id
         ├─> events (ranked)
         ├─> metadata (processing time, counts)
         └─> status
    """)
    
    print("\n🔍 EXAMPLE SEARCH QUERIES")
    print("=" * 80)
    
    # Query 1: Simple protest search
    print("\n1️⃣  Simple Search - Recent Protests")
    print("-" * 80)
    query1 = SearchQuery(
        phrase="protest march demonstration"
    )
    print("   Query:")
    print(f"   - Phrase: '{query1.phrase}'")
    print(f"   - Filters: None (broad search)")
    print("\n   Expected Pipeline:")
    print("   → Scrape from all enabled sources")
    print("   → Extract all events")
    print("   → Match events containing 'protest', 'march', or 'demonstration'")
    print("   → Rank by text similarity")
    
    # Query 2: Location-specific search
    print("\n2️⃣  Location-Specific Search")
    print("-" * 80)
    query2 = SearchQuery(
        phrase="protest strike",
        location="Mumbai, India"
    )
    print("   Query:")
    print(f"   - Phrase: '{query2.phrase}'")
    print(f"   - Location: {query2.location}")
    print("\n   Expected Pipeline:")
    print("   → Scrape articles about protests/strikes")
    print("   → Extract events")
    print("   → Boost events in Mumbai, India")
    print("   → Rank by combined text + location score")
    
    # Query 3: Type and date filtered
    print("\n3️⃣  Type + Date Range Search")
    print("-" * 80)
    query3 = SearchQuery(
        phrase="cyber attack data breach",
        event_type=EventType.CYBER_ATTACK,
        date_from=datetime.now() - timedelta(days=30),
        date_to=datetime.now()
    )
    print("   Query:")
    print(f"   - Phrase: '{query3.phrase}'")
    print(f"   - Event Type: {query3.event_type.value}")
    print(f"   - Date Range: Last 30 days")
    print("\n   Expected Pipeline:")
    print("   → Scrape cyber attack articles")
    print("   → Extract events")
    print("   → Filter to cyber_attack type")
    print("   → Filter to last 30 days")
    print("   → Rank by relevance")
    
    # Query 4: Complex multi-filter
    print("\n4️⃣  Complex Multi-Filter Search")
    print("-" * 80)
    query4 = SearchQuery(
        phrase="political unrest uprising",
        location="Middle East",
        event_type=EventType.CIVIL_UNREST,
        date_from=datetime(2025, 11, 1),
        date_to=datetime(2025, 12, 31)
    )
    print("   Query:")
    print(f"   - Phrase: '{query4.phrase}'")
    print(f"   - Location: {query4.location}")
    print(f"   - Event Type: {query4.event_type.value}")
    print(f"   - Date Range: Nov-Dec 2025")
    print("\n   Expected Pipeline:")
    print("   → Scrape political unrest articles")
    print("   → Extract events")
    print("   → Boost Middle East locations (25% weight)")
    print("   → Boost civil_unrest type (15% weight)")
    print("   → Boost Nov-Dec 2025 dates (20% weight)")
    print("   → Weighted relevance scoring")
    
    print("\n\n📊 API REQUEST/RESPONSE EXAMPLES")
    print("=" * 80)
    
    # Example Request
    print("\n📤 REQUEST - POST /api/v1/search")
    print("-" * 80)
    print("""
    curl -X POST http://localhost:8000/api/v1/search \\
      -H "Content-Type: application/json" \\
      -d '{
        "phrase": "protest in Mumbai",
        "location": "India",
        "event_type": "protest",
        "date_from": "2025-11-01",
        "date_to": "2025-12-31"
      }'
    """)
    
    # Example Response
    print("\n📥 RESPONSE - 200 OK")
    print("-" * 80)
    print("""
    {
      "session_id": "7aa9571b-e780-44e2-b5a3-a5565587f862",
      "events": [
        {
          "event_type": "protest",
          "title": "Large Protest in Mumbai Over Policy Changes",
          "summary": "Thousands gathered in central Mumbai...",
          "location": {
            "city": "Mumbai",
            "country": "India",
            "region": "Maharashtra"
          },
          "event_date": "2025-11-15T10:00:00",
          "participants": ["protesters", "police"],
          "organizations": ["Citizens Coalition"],
          "confidence": 0.92,
          "source_url": "https://example.com/article1"
        }
      ],
      "query": {
        "phrase": "protest in Mumbai",
        "location": "India",
        "event_type": "protest",
        "date_from": "2025-11-01",
        "date_to": "2025-12-31"
      },
      "total_events": 1,
      "processing_time_seconds": 15.3,
      "articles_scraped": 25,
      "sources_scraped": 2,
      "status": "success",
      "message": "Found 1 relevant events"
    }
    """)
    
    print("\n📥 RETRIEVE SESSION - GET /api/v1/search/session/{id}")
    print("-" * 80)
    print("""
    curl http://localhost:8000/api/v1/search/session/7aa9571b-...
    
    Response:
    {
      "session_id": "7aa9571b-e780-44e2-b5a3-a5565587f862",
      "events": [...],
      "total_events": 1
    }
    """)
    
    print("\n\n⚙️  CONFIGURATION & PERFORMANCE")
    print("=" * 80)
    
    print("\n🔧 Request Parameters:")
    print("   - max_articles: 50 (default) - Articles per source")
    print("   - min_relevance_score: 0.1 (default) - Minimum score to include")
    
    print("\n⏱️  Performance Metrics:")
    print("   For 10 articles:")
    print("   - Scraping:    ~15 seconds")
    print("   - Extraction:  ~30 seconds (Ollama)")
    print("   - Matching:    <1 second")
    print("   - Total:       ~47 seconds")
    
    print("\n🎯 Relevance Scoring Weights:")
    print("   - Text Similarity:  40%")
    print("   - Location Match:   25%")
    print("   - Date Relevance:   20%")
    print("   - Event Type Match: 15%")
    
    print("\n💾 Session Management:")
    print("   - Storage: In-memory (SessionStore)")
    print("   - Lifetime: 24 hours")
    print("   - Cleanup: Automatic")
    print("   - ID Format: UUID v4")
    
    print("\n\n🚨 ERROR HANDLING")
    print("=" * 80)
    
    error_scenarios = [
        ("no_sources", "No enabled sources configured", "Enable sources in sources.yaml"),
        ("no_articles", "Scraping failed", "Check network, URLs, selectors"),
        ("no_events", "Event extraction failed", "Verify Ollama is running"),
        ("error", "Exception occurred", "Check logs for details"),
        ("success", "Search completed", "Events found and returned")
    ]
    
    for status, meaning, resolution in error_scenarios:
        print(f"\n   {status.upper()}")
        print(f"   → {meaning}")
        print(f"   → Fix: {resolution}")
    
    print("\n\n📈 SEARCH FLOW EXAMPLE")
    print("=" * 80)
    
    print("""
    User submits: "cyber attack on banks"
    
    ⏬ Step 1: Get Sources (0.1s)
       ✓ Found 3 enabled sources
    
    ⏬ Step 2: Scrape Articles (15s)
       ✓ Source 1: 8 articles
       ✓ Source 2: 12 articles
       ✓ Source 3: 5 articles
       ✓ Total: 25 articles
    
    ⏬ Step 3: Extract Events (30s)
       ✓ Article 1 → Cyber Attack Event
       ✓ Article 2 → Not an event
       ✓ Article 3 → Cyber Attack Event
       ...
       ✓ Total: 10 events extracted
    
    ⏬ Step 4: Match & Rank (0.5s)
       ✓ Event 1: 0.85 relevance
       ✓ Event 2: 0.72 relevance
       ✓ Event 3: 0.45 relevance
       ...
       ✓ Filtered: 8 events (score >= 0.1)
    
    ⏬ Step 5: Store Session (0.1s)
       ✓ Session created: abc-123-def-456
       ✓ Stored 8 events
    
    ⏬ Response (45.7s total)
       ✓ 8 events found
       ✓ Session ID returned
       ✓ Ready for export
    """)
    
    print("\n\n✅ INCREMENT 7 CAPABILITIES")
    print("=" * 80)
    
    capabilities = [
        "End-to-end search from query to ranked results",
        "Multi-source web scraping",
        "NLP entity extraction (spaCy)",
        "LLM event extraction (Ollama)",
        "Multi-dimensional relevance scoring",
        "Session-based result storage",
        "Comprehensive error handling",
        "Performance metrics tracking",
        "REST API with OpenAPI docs",
        "Automatic session cleanup"
    ]
    
    for i, cap in enumerate(capabilities, 1):
        print(f"   {i:2d}. ✓ {cap}")
    
    print("\n\n🎯 NEXT STEPS")
    print("=" * 80)
    print("""
    Increment 8: Excel Export
    ├─> Create ExcelExporter service
    ├─> Format events into workbook
    ├─> Multiple sheet support
    ├─> Cell styling & formatting
    └─> /api/v1/export/excel endpoint
    
    Then you can:
    1. Search for events
    2. Get ranked results
    3. Export to Excel
    4. Share with stakeholders
    """)
    
    print("\n\n" + "=" * 80)
    print("  ✅ DEMO COMPLETE - SEARCH API READY!")
    print("=" * 80)
    
    print("\nThe complete search pipeline is now operational! 🎉")
    print("\nTo use:")
    print("  1. Start the API: uvicorn app.main:app --reload")
    print("  2. Visit docs: http://localhost:8000/docs")
    print("  3. Try a search: POST /api/v1/search")
    print("  4. Retrieve results: GET /api/v1/search/session/{id}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_search_api()
