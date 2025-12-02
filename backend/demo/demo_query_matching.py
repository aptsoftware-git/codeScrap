"""
Visual demo of Increment 6: Query Matching & Relevance
Shows how events are matched and ranked based on search queries.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.query_matcher import query_matcher
from app.models import EventData, SearchQuery, EventType, Location


def demo_query_matching():
    """Demonstrate query matching and ranking."""
    
    print("\n" + "=" * 80)
    print("  INCREMENT 6: QUERY MATCHING & RELEVANCE - VISUAL DEMO")
    print("=" * 80)
    
    # Create sample events
    today = datetime.now()
    
    events = [
        EventData(
            event_type=EventType.PROTEST,
            title="Massive Protest in Mumbai Against New Policies",
            summary="Over 10,000 people gathered in central Mumbai to protest against new government policies. The peaceful demonstration lasted for several hours.",
            location=Location(city="Mumbai", country="India", region="Maharashtra"),
            event_date=today,
            participants=["protesters", "police"],
            organizations=["Citizens' Coalition", "Workers Union"],
            confidence=0.92
        ),
        EventData(
            event_type=EventType.PROTEST,
            title="Small Protest Rally in Delhi",
            summary="A group of activists held a small protest rally in Delhi demanding policy changes.",
            location=Location(city="Delhi", country="India", region="Delhi"),
            event_date=today - timedelta(days=2),
            participants=["activists"],
            organizations=["Activist Group"],
            confidence=0.75
        ),
        EventData(
            event_type=EventType.CYBER_ATTACK,
            title="Major Cyber Attack Hits Banking Sector",
            summary="Sophisticated cyber attack targeted major banks in the United States, affecting millions of customers.",
            location=Location(city="New York", country="USA", region="New York"),
            event_date=today - timedelta(days=5),
            organizations=["JPMorgan", "Bank of America"],
            confidence=0.88
        ),
        EventData(
            event_type=EventType.PROTEST,
            title="Climate Protest in Paris Blocks Major Roads",
            summary="Environmental activists blocked major roads in Paris to protest climate change policies.",
            location=Location(city="Paris", country="France", region="Île-de-France"),
            event_date=today - timedelta(days=10),
            participants=["environmental activists"],
            organizations=["Green Earth"],
            confidence=0.81
        ),
        EventData(
            event_type=EventType.ATTACK,
            title="Terrorist Attack in Middle East",
            summary="A terrorist attack occurred in a public area, resulting in casualties.",
            location=Location(city="Baghdad", country="Iraq", region="Baghdad"),
            event_date=today - timedelta(days=15),
            confidence=0.85
        ),
    ]
    
    print(f"\n📚 SAMPLE DATABASE")
    print("=" * 80)
    print(f"Total Events: {len(events)}\n")
    
    for i, event in enumerate(events, 1):
        print(f"{i}. [{event.event_type.value.upper()}] {event.title}")
        print(f"   Location: {event.location.city}, {event.location.country}")
        print(f"   Date: {event.event_date.strftime('%Y-%m-%d')}")
        print(f"   Confidence: {event.confidence:.0%}\n")
    
    # Test Query 1: Specific protest in Mumbai
    print("\n" + "=" * 80)
    print("  QUERY 1: Protest in Mumbai")
    print("=" * 80)
    
    query1 = SearchQuery(
        phrase="protest in Mumbai",
        location="Mumbai",
        event_type=EventType.PROTEST
    )
    
    print(f"\n🔍 Search Parameters:")
    print(f"   Phrase: '{query1.phrase}'")
    print(f"   Location: {query1.location}")
    print(f"   Event Type: {query1.event_type.value if query1.event_type else 'Any'}")
    
    matches1 = query_matcher.match_events(events, query1, min_score=0.1)
    
    print(f"\n📊 Results: {len(matches1)} events matched\n")
    
    for i, match in enumerate(matches1, 1):
        event = match['event']
        score = match['relevance_score']
        
        print(f"{i}. [{score:.3f}] {event.title}")
        print(f"   Type: {event.event_type.value}")
        print(f"   Location: {event.location.city}, {event.location.country}")
        
        # Show score breakdown
        text_score = query_matcher.calculate_text_similarity(query1.phrase, event)
        loc_score = query_matcher.calculate_location_similarity(query1.location, event.location)
        date_score = query_matcher.calculate_date_relevance(query1, event)
        type_score = query_matcher.calculate_event_type_match(query1.event_type, event.event_type)
        
        print(f"   Scores: Text={text_score:.2f}, Loc={loc_score:.2f}, Date={date_score:.2f}, Type={type_score:.2f}")
        print()
    
    # Test Query 2: Recent events in India
    print("\n" + "=" * 80)
    print("  QUERY 2: Recent Events in India")
    print("=" * 80)
    
    query2 = SearchQuery(
        phrase="protest policy",
        location="India",
        date_from=today - timedelta(days=7),
        date_to=today + timedelta(days=1)
    )
    
    print(f"\n🔍 Search Parameters:")
    print(f"   Phrase: '{query2.phrase}'")
    print(f"   Location: {query2.location}")
    print(f"   Date Range: {query2.date_from.strftime('%Y-%m-%d')} to {query2.date_to.strftime('%Y-%m-%d')}")
    print(f"   Event Type: Any")
    
    matches2 = query_matcher.match_events(events, query2, min_score=0.2)
    
    print(f"\n📊 Results: {len(matches2)} events matched\n")
    
    for i, match in enumerate(matches2, 1):
        event = match['event']
        score = match['relevance_score']
        
        print(f"{i}. [{score:.3f}] {event.title}")
        print(f"   Location: {event.location.city}, {event.location.country}")
        print(f"   Date: {event.event_date.strftime('%Y-%m-%d')}")
        print()
    
    # Test Query 3: Cyber attacks
    print("\n" + "=" * 80)
    print("  QUERY 3: Cyber Attacks")
    print("=" * 80)
    
    query3 = SearchQuery(
        phrase="cyber attack banking",
        event_type=EventType.CYBER_ATTACK
    )
    
    print(f"\n🔍 Search Parameters:")
    print(f"   Phrase: '{query3.phrase}'")
    print(f"   Event Type: {query3.event_type.value}")
    
    matches3 = query_matcher.match_events(events, query3, min_score=0.3)
    
    print(f"\n📊 Results: {len(matches3)} events matched\n")
    
    for i, match in enumerate(matches3, 1):
        event = match['event']
        score = match['relevance_score']
        
        print(f"{i}. [{score:.3f}] {event.title}")
        print(f"   Summary: {event.summary[:80]}...")
        print(f"   Location: {event.location.city}, {event.location.country}")
        print()
    
    # Demonstrate filtering
    print("\n" + "=" * 80)
    print("  FILTERING DEMONSTRATIONS")
    print("=" * 80)
    
    # Filter by date
    print(f"\n📅 Filter: Events from last 7 days")
    recent = query_matcher.filter_by_date_range(
        events,
        date_from=today - timedelta(days=7),
        date_to=today + timedelta(days=1)
    )
    print(f"   Result: {len(recent)}/{len(events)} events")
    for event in recent:
        print(f"   - {event.title} ({event.event_date.strftime('%Y-%m-%d')})")
    
    # Filter by type
    print(f"\n🏷️  Filter: Protest events only")
    protests = query_matcher.filter_by_event_type(events, EventType.PROTEST)
    print(f"   Result: {len(protests)}/{len(events)} events")
    for event in protests:
        print(f"   - {event.title}")
    
    # Filter by location
    print(f"\n📍 Filter: Events in India")
    india = query_matcher.filter_by_location(events, "India")
    print(f"   Result: {len(india)}/{len(events)} events")
    for event in india:
        print(f"   - {event.title} ({event.location.city})")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("  ✅ DEMO COMPLETE")
    print("=" * 80)
    
    print("\nKey Features Demonstrated:")
    print("  ✓ Multi-dimensional relevance scoring")
    print("  ✓ Text similarity (keyword + sequence matching)")
    print("  ✓ Location matching (city/country/region)")
    print("  ✓ Date range filtering with proximity")
    print("  ✓ Event type filtering")
    print("  ✓ Weighted scoring algorithm")
    print("  ✓ Automatic ranking by relevance")
    
    print("\nScoring Weights:")
    for key, value in query_matcher.weights.items():
        print(f"  • {key.capitalize()}: {value:.0%}")
    
    print("\nThe query matching system intelligently ranks events based on")
    print("multiple factors to provide the most relevant results! 🎯")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_query_matching()
