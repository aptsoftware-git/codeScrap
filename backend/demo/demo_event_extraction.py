"""
Visual demo of complete Increment 5: Event Extraction with Ollama
Shows the full pipeline from article to structured event data.
"""

import sys
from pathlib import Path
import asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.event_extractor import event_extractor
from app.services.entity_extractor import entity_extractor


async def demo_complete_pipeline():
    """Demonstrate the complete event extraction pipeline."""
    
    print("\n" + "=" * 80)
    print("  INCREMENT 5: EVENT EXTRACTION WITH OLLAMA - VISUAL DEMO")
    print("=" * 80)
    
    # Sample news article
    article = {
        "title": "Major Cyber Attack Disrupts Banking Services Nationwide",
        "content": """
        A sophisticated cyber attack targeted multiple major financial institutions 
        on Tuesday morning, causing widespread disruption to banking services across 
        the United States. The attack, which security experts believe originated from 
        servers in Eastern Europe, compromised the systems of JPMorgan Chase, Bank of 
        America, and Wells Fargo.
        
        The FBI, led by Director Christopher Wray, has launched an immediate 
        investigation into the incident. Microsoft's cybersecurity team has been 
        brought in to assist with the response and system recovery.
        
        The attack began at approximately 3:00 AM EST and affected an estimated 
        2.5 million customers who were unable to access online banking services. 
        By noon, most services had been restored, though investigations continue.
        
        "This appears to be a coordinated and highly sophisticated attack," said 
        Wray in a press conference. "We are working with international partners 
        to identify and apprehend those responsible."
        
        Security analysts warn that this incident highlights the growing threat of 
        cyber attacks against critical infrastructure. The attack did not result in 
        any known data breaches, but officials caution customers to monitor their 
        accounts for suspicious activity.
        """,
        "url": "https://example.com/cyber-attack-banking-2025"
    }
    
    print("\n📰 ARTICLE INPUT")
    print("=" * 80)
    print(f"Title: {article['title']}")
    print(f"\nContent Preview:")
    print(f"{article['content'][:200].strip()}...")
    print(f"\n[Full content: {len(article['content'])} characters]")
    
    # Step 1: Entity Extraction
    print("\n\n" + "=" * 80)
    print("  STEP 1: ENTITY EXTRACTION (spaCy NER)")
    print("=" * 80)
    
    if entity_extractor.is_available():
        entities = entity_extractor.extract_from_article(
            article['title'],
            article['content']
        )
        
        print(f"\n✓ Extracted {entity_extractor.count_entities(entities)} entities:")
        
        if entities.persons:
            print(f"\n  👤 PERSONS ({len(entities.persons)}):")
            for person in entities.persons[:5]:
                print(f"     • {person}")
        
        if entities.organizations:
            print(f"\n  🏢 ORGANIZATIONS ({len(entities.organizations)}):")
            for org in entities.organizations[:5]:
                print(f"     • {org}")
        
        if entities.locations:
            print(f"\n  📍 LOCATIONS ({len(entities.locations)}):")
            for loc in entities.locations[:5]:
                print(f"     • {loc}")
        
        if entities.dates:
            print(f"\n  📅 DATES ({len(entities.dates)}):")
            for date in entities.dates[:5]:
                print(f"     • {date}")
    else:
        print("\n⚠️  spaCy not available - skipping entity extraction")
        entities = None
    
    # Step 2: LLM Event Extraction
    print("\n\n" + "=" * 80)
    print("  STEP 2: EVENT EXTRACTION (Ollama LLM)")
    print("=" * 80)
    
    if not event_extractor.is_available():
        print("\n⚠️  Ollama not available - cannot extract events")
        return
    
    print("\n🤖 Sending article to Ollama (llama3.1:8b)...")
    print("   This may take 60-90 seconds...\n")
    
    try:
        event_data = await event_extractor.extract_event(
            title=article['title'],
            content=article['content'],
            url=article['url'],
            entities=entities
        )
        
        if event_data is None:
            print("✗ Event extraction failed (LLM returned invalid response)")
            return
        
        # Display extracted event
        print("\n✅ EVENT SUCCESSFULLY EXTRACTED!")
        print("=" * 80)
        
        print(f"\n📋 EVENT DETAILS")
        print("-" * 80)
        print(f"  Event Type:     {event_data.event_type.value.upper().replace('_', ' ')}")
        print(f"  Title:          {event_data.title}")
        print(f"  Confidence:     {event_data.confidence:.0%}")
        
        print(f"\n📝 SUMMARY")
        print("-" * 80)
        print(f"  {event_data.summary}")
        
        if event_data.location:
            print(f"\n📍 LOCATION")
            print("-" * 80)
            if event_data.location.city:
                print(f"  City:     {event_data.location.city}")
            if event_data.location.country:
                print(f"  Country:  {event_data.location.country}")
            if event_data.location.region:
                print(f"  Region:   {event_data.location.region}")
        
        if event_data.participants:
            print(f"\n👤 PARTICIPANTS ({len(event_data.participants)})")
            print("-" * 80)
            for participant in event_data.participants:
                print(f"  • {participant}")
        
        if event_data.organizations:
            print(f"\n🏢 ORGANIZATIONS ({len(event_data.organizations)})")
            print("-" * 80)
            for org in event_data.organizations:
                print(f"  • {org}")
        
        # Show JSON output
        print(f"\n\n" + "=" * 80)
        print("  STRUCTURED JSON OUTPUT")
        print("=" * 80)
        
        import json
        output = {
            "event_type": event_data.event_type.value,
            "title": event_data.title,
            "summary": event_data.summary,
            "location": {
                "city": event_data.location.city if event_data.location else None,
                "country": event_data.location.country if event_data.location else None,
                "region": event_data.location.region if event_data.location else None,
            },
            "participants": event_data.participants,
            "organizations": event_data.organizations,
            "confidence": event_data.confidence
        }
        
        print(f"\n{json.dumps(output, indent=2)}")
        
        # Summary
        print(f"\n\n" + "=" * 80)
        print("  ✅ DEMO COMPLETE")
        print("=" * 80)
        
        print("\nWhat Just Happened:")
        print("  1. ✓ Article text provided as input")
        print("  2. ✓ Entities extracted using spaCy (NER)")
        print("  3. ✓ Structured prompt created with context")
        print("  4. ✓ Ollama LLM generated JSON response")
        print("  5. ✓ Event type validated and normalized")
        print("  6. ✓ Structured EventData object created")
        
        print(f"\nPerformance:")
        print(f"  • Input:  {len(article['content'])} characters")
        print(f"  • Output: Structured event data")
        print(f"  • Model:  llama3.1:8b")
        print(f"  • Type:   {event_data.event_type.value}")
        
        print(f"\nThe event extraction system is working perfectly! 🎉")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error during extraction: {e}")
        print(f"  This may happen if Ollama is not running properly")


if __name__ == "__main__":
    asyncio.run(demo_complete_pipeline())
