"""
Test script for Increment 6: Query Matching & Relevance

Tests:
1. QueryMatcher initialization
2. Text normalization and keyword extraction
3. Text similarity calculation
4. Location matching
5. Date relevance scoring
6. Event type matching
7. Overall relevance scoring
8. Event filtering and ranking
9. Edge cases and boundary conditions
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.query_matcher import query_matcher
from app.models import EventData, SearchQuery, EventType, Location


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_initialization():
    """Test QueryMatcher initialization."""
    print_section("TEST 1: QueryMatcher Initialization")
    
    try:
        assert query_matcher is not None, "QueryMatcher not initialized"
        assert query_matcher.weights is not None, "Weights not set"
        
        # Check weights sum to 1.0
        total_weight = sum(query_matcher.weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weights don't sum to 1.0: {total_weight}"
        
        print(f"✓ QueryMatcher initialized")
        print(f"✓ Weights configured:")
        for key, value in query_matcher.weights.items():
            print(f"    {key}: {value:.2%}")
        print(f"✓ Total weight: {total_weight:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Initialization failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_text_normalization():
    """Test text normalization."""
    print_section("TEST 2: Text Normalization")
    
    try:
        # Test cases
        tests = [
            ("UPPERCASE TEXT", "uppercase text"),
            ("  Extra   Spaces  ", "extra spaces"),
            ("MiXeD CaSe", "mixed case"),
            ("", ""),
        ]
        
        for input_text, expected in tests:
            result = query_matcher.normalize_text(input_text)
            assert result == expected, f"Expected '{expected}', got '{result}'"
        
        print(f"✓ Text normalization works correctly")
        print(f"✓ Tested {len(tests)} cases")
        
        return True
    except AssertionError as e:
        print(f"✗ Normalization failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_keyword_extraction():
    """Test keyword extraction."""
    print_section("TEST 3: Keyword Extraction")
    
    try:
        text = "Major protest in Mumbai against new policies"
        keywords = query_matcher.extract_keywords(text)
        
        # Should include: major, protest, mumbai, against, new, policies
        # Should exclude: in (stop word)
        assert 'major' in keywords, "Missing 'major'"
        assert 'protest' in keywords, "Missing 'protest'"
        assert 'mumbai' in keywords, "Missing 'mumbai'"
        assert 'policies' in keywords, "Missing 'policies'"
        assert 'in' not in keywords, "Stop word 'in' not filtered"
        
        print(f"✓ Keyword extraction works")
        print(f"  Extracted keywords: {sorted(keywords)}")
        print(f"  Count: {len(keywords)}")
        
        return True
    except AssertionError as e:
        print(f"✗ Keyword extraction failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_text_similarity():
    """Test text similarity calculation."""
    print_section("TEST 4: Text Similarity")
    
    try:
        # Create sample event
        event = EventData(
            event_type=EventType.PROTEST,
            title="Large protest in Mumbai city center",
            summary="Thousands gathered to protest against new government policies",
            location=Location(city="Mumbai", country="India"),
            confidence=0.9
        )
        
        # Test cases (query, expected_high_score)
        tests = [
            ("protest in Mumbai", True),
            ("Mumbai protest", True),
            ("government policies protest", True),
            ("completely unrelated topic", False),
            ("cyber attack banking", False),
        ]
        
        for query_text, should_be_high in tests:
            score = query_matcher.calculate_text_similarity(query_text, event)
            
            if should_be_high:
                assert score > 0.15, f"Expected high score for '{query_text}', got {score:.2f}"
                print(f"✓ High similarity for '{query_text}': {score:.2f}")
            else:
                assert score < 0.3, f"Expected low score for '{query_text}', got {score:.2f}"
                print(f"✓ Low similarity for '{query_text}': {score:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Text similarity failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_location_matching():
    """Test location matching."""
    print_section("TEST 5: Location Matching")
    
    try:
        # Create locations
        location1 = Location(city="Mumbai", country="India", region="Maharashtra")
        location2 = Location(city="New York", country="USA", region="New York")
        location3 = Location(city=None, country="France", region=None)
        
        # Test cases (query, location, expected_high)
        tests = [
            ("Mumbai", location1, True),
            ("India", location1, True),
            ("Maharashtra", location1, True),
            ("New York", location2, True),
            ("USA", location2, True),
            ("France", location3, True),
            ("Mumbai", location2, False),
            ("Paris", location1, False),
        ]
        
        for query, location, should_be_high in tests:
            score = query_matcher.calculate_location_similarity(query, location)
            
            if should_be_high:
                assert score > 0.5, f"Expected high score for '{query}', got {score:.2f}"
                print(f"✓ Matched '{query}': {score:.2f}")
            else:
                assert score < 0.7, f"Expected low score for '{query}', got {score:.2f}"
                print(f"✓ No match '{query}': {score:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Location matching failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_date_relevance():
    """Test date relevance scoring."""
    print_section("TEST 6: Date Relevance")
    
    try:
        # Create event with date
        today = datetime.now()
        event_today = EventData(
            event_type=EventType.PROTEST,
            title="Today's event",
            summary="Event happening today",
            location=Location(city="City"),
            event_date=today,
            confidence=0.9
        )
        
        event_past = EventData(
            event_type=EventType.PROTEST,
            title="Past event",
            summary="Event from the past",
            location=Location(city="City"),
            event_date=today - timedelta(days=10),
            confidence=0.9
        )
        
        # Test: Event within range
        query = SearchQuery(
            phrase="test",
            date_from=today - timedelta(days=5),
            date_to=today + timedelta(days=5)
        )
        score = query_matcher.calculate_date_relevance(query, event_today)
        assert score == 1.0, f"Event within range should score 1.0, got {score:.2f}"
        print(f"✓ Event within range: {score:.2f}")
        
        # Test: Event outside range
        score = query_matcher.calculate_date_relevance(query, event_past)
        assert score < 1.0, f"Event outside range should score < 1.0, got {score:.2f}"
        print(f"✓ Event outside range: {score:.2f}")
        
        # Test: No date range specified
        query_no_date = SearchQuery(phrase="test")
        score = query_matcher.calculate_date_relevance(query_no_date, event_today)
        assert score == 0.5, f"No date range should score 0.5, got {score:.2f}"
        print(f"✓ No date range specified: {score:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Date relevance failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_event_type_matching():
    """Test event type matching."""
    print_section("TEST 7: Event Type Matching")
    
    try:
        # Test exact match
        score = query_matcher.calculate_event_type_match(EventType.PROTEST, EventType.PROTEST)
        assert score == 1.0, f"Exact match should score 1.0, got {score:.2f}"
        print(f"✓ Exact type match: {score:.2f}")
        
        # Test mismatch
        score = query_matcher.calculate_event_type_match(EventType.PROTEST, EventType.ATTACK)
        assert score == 0.0, f"Type mismatch should score 0.0, got {score:.2f}"
        print(f"✓ Type mismatch: {score:.2f}")
        
        # Test no type specified
        score = query_matcher.calculate_event_type_match(None, EventType.PROTEST)
        assert score == 0.5, f"No type specified should score 0.5, got {score:.2f}"
        print(f"✓ No type specified: {score:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Event type matching failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_overall_relevance():
    """Test overall relevance scoring."""
    print_section("TEST 8: Overall Relevance Scoring")
    
    try:
        # Create a well-matched event
        event = EventData(
            event_type=EventType.PROTEST,
            title="Major protest in Mumbai against government policies",
            summary="Thousands of people gathered in central Mumbai to protest new policies",
            location=Location(city="Mumbai", country="India"),
            event_date=datetime.now(),
            confidence=0.9
        )
        
        # Create a matching query
        query = SearchQuery(
            phrase="protest in Mumbai",
            location="Mumbai",
            event_type=EventType.PROTEST,
            date_from=datetime.now() - timedelta(days=1),
            date_to=datetime.now() + timedelta(days=1)
        )
        
        score = query_matcher.calculate_relevance_score(query, event)
        
        # Should be high since everything matches
        assert score > 0.5, f"Well-matched event should score > 0.5, got {score:.2f}"
        print(f"✓ Well-matched event scored: {score:.2f}")
        
        # Create a poorly-matched event
        poor_event = EventData(
            event_type=EventType.ACCIDENT,
            title="Accident in Paris",
            summary="A traffic accident occurred",
            location=Location(city="Paris", country="France"),
            event_date=datetime.now() - timedelta(days=30),
            confidence=0.8
        )
        
        poor_score = query_matcher.calculate_relevance_score(query, poor_event)
        
        # Should be low since nothing matches
        assert poor_score < score, f"Poorly-matched should score less than well-matched"
        print(f"✓ Poorly-matched event scored: {poor_score:.2f}")
        
        return True
    except AssertionError as e:
        print(f"✗ Overall relevance failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_event_matching():
    """Test event matching and ranking."""
    print_section("TEST 9: Event Matching & Ranking")
    
    try:
        # Create sample events
        events = [
            EventData(
                event_type=EventType.PROTEST,
                title="Protest in Mumbai city center",
                summary="Large protest against policies",
                location=Location(city="Mumbai", country="India"),
                event_date=datetime.now(),
                confidence=0.9
            ),
            EventData(
                event_type=EventType.PROTEST,
                title="Small protest in Delhi",
                summary="Group protests in Delhi",
                location=Location(city="Delhi", country="India"),
                event_date=datetime.now(),
                confidence=0.7
            ),
            EventData(
                event_type=EventType.ATTACK,
                title="Cyber attack on banks",
                summary="Sophisticated cyber attack",
                location=Location(city="New York", country="USA"),
                event_date=datetime.now() - timedelta(days=20),
                confidence=0.85
            ),
        ]
        
        # Create query
        query = SearchQuery(
            phrase="protest in Mumbai",
            location="Mumbai",
            event_type=EventType.PROTEST
        )
        
        # Match events
        matches = query_matcher.match_events(events, query, min_score=0.1)
        
        assert len(matches) > 0, "Should match at least one event"
        print(f"✓ Matched {len(matches)}/{len(events)} events")
        
        # Check ranking (first should be most relevant)
        for i, match in enumerate(matches):
            event = match['event']
            score = match['relevance_score']
            print(f"  {i+1}. '{event.title[:40]}...' - Score: {score:.3f}")
        
        # First match should be Mumbai protest
        assert "Mumbai" in matches[0]['event'].title, "Mumbai protest should rank first"
        print(f"✓ Ranking correct: Mumbai protest ranked first")
        
        # Scores should be descending
        for i in range(len(matches) - 1):
            assert matches[i]['relevance_score'] >= matches[i+1]['relevance_score'], \
                "Scores should be in descending order"
        print(f"✓ Scores in descending order")
        
        return True
    except AssertionError as e:
        print(f"✗ Event matching failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_filtering():
    """Test event filtering."""
    print_section("TEST 10: Event Filtering")
    
    try:
        # Create sample events
        today = datetime.now()
        events = [
            EventData(
                event_type=EventType.PROTEST,
                title="Event 1",
                summary="Protest event",
                location=Location(city="Mumbai", country="India"),
                event_date=today,
                confidence=0.9
            ),
            EventData(
                event_type=EventType.ATTACK,
                title="Event 2",
                summary="Attack event",
                location=Location(city="Delhi", country="India"),
                event_date=today - timedelta(days=10),
                confidence=0.9
            ),
            EventData(
                event_type=EventType.PROTEST,
                title="Event 3",
                summary="Another protest",
                location=Location(city="Paris", country="France"),
                event_date=today - timedelta(days=5),
                confidence=0.9
            ),
        ]
        
        # Test date filtering
        filtered = query_matcher.filter_by_date_range(
            events,
            date_from=today - timedelta(days=7),
            date_to=today + timedelta(days=1)
        )
        assert len(filtered) == 2, f"Expected 2 events in date range, got {len(filtered)}"
        print(f"✓ Date filtering: {len(filtered)}/{len(events)} events")
        
        # Test type filtering
        filtered = query_matcher.filter_by_event_type(events, EventType.PROTEST)
        assert len(filtered) == 2, f"Expected 2 protest events, got {len(filtered)}"
        print(f"✓ Type filtering: {len(filtered)}/{len(events)} events")
        
        # Test location filtering
        filtered = query_matcher.filter_by_location(events, "India")
        assert len(filtered) == 2, f"Expected 2 events in India, got {len(filtered)}"
        print(f"✓ Location filtering: {len(filtered)}/{len(events)} events")
        
        return True
    except AssertionError as e:
        print(f"✗ Filtering failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  INCREMENT 6: QUERY MATCHING & RELEVANCE - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Initialization", test_initialization),
        ("Text Normalization", test_text_normalization),
        ("Keyword Extraction", test_keyword_extraction),
        ("Text Similarity", test_text_similarity),
        ("Location Matching", test_location_matching),
        ("Date Relevance", test_date_relevance),
        ("Event Type Matching", test_event_type_matching),
        ("Overall Relevance", test_overall_relevance),
        ("Event Matching", test_event_matching),
        ("Filtering", test_filtering),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ INCREMENT 6 COMPLETE - ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
