"""
Practical demo of Entity Extraction with real news-like content.
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.entity_extractor import entity_extractor


def demo_entity_extraction():
    """Demonstrate entity extraction with realistic news articles."""
    print("=" * 70)
    print("ENTITY EXTRACTION DEMO")
    print("=" * 70)
    
    # Sample news articles
    articles = [
        {
            "title": "Major Cyber Attack Targets Financial Institutions",
            "content": """
            A sophisticated cyber attack targeted several major banks including 
            JPMorgan Chase, Bank of America, and Wells Fargo on Tuesday. 
            The attack, which originated from servers in Russia, affected millions 
            of customers across the United States.
            
            FBI Director Christopher Wray announced an investigation into the 
            incident. Microsoft's security team is assisting with the response.
            The attack began at 3:00 AM EST and was contained by noon.
            """
        },
        {
            "title": "Climate Summit Concludes in Paris with Historic Agreement",
            "content": """
            World leaders including President Joe Biden, Chancellor Olaf Scholz, 
            and Prime Minister Rishi Sunak concluded the Climate Summit 2025 in 
            Paris, France on Friday. The three-day conference resulted in 
            unprecedented commitments to renewable energy.
            
            Major tech companies like Tesla, Apple, and Amazon pledged carbon 
            neutrality by 2030. The United Nations praised the agreement as a 
            "turning point" in the fight against climate change.
            """
        },
        {
            "title": "Tech Giants Announce AI Research Partnership",
            "content": """
            Google, Microsoft, and OpenAI announced a groundbreaking partnership 
            on Monday to advance artificial intelligence research. The collaboration, 
            based in Stanford University, will focus on developing safe and ethical AI.
            
            CEO Sundar Pichai and researchers from MIT will lead the initiative.
            The project launches January 15, 2026 with $10 billion in funding.
            """
        }
    ]
    
    print(f"\nProcessing {len(articles)} news articles...\n")
    
    for i, article in enumerate(articles, 1):
        print("=" * 70)
        print(f"ARTICLE {i}")
        print("=" * 70)
        
        print(f"\n📰 Title: {article['title']}")
        print(f"\n📄 Content Preview:")
        print(f"   {article['content'][:150].strip()}...")
        
        # Extract entities
        entities = entity_extractor.extract_from_article(
            title=article['title'],
            content=article['content']
        )
        
        # Display results
        print(f"\n✅ Entities Extracted:")
        
        if entities.persons:
            print(f"\n   👤 PERSONS ({len(entities.persons)}):")
            for person in entities.persons:
                print(f"      • {person}")
        
        if entities.organizations:
            print(f"\n   🏢 ORGANIZATIONS ({len(entities.organizations)}):")
            for org in entities.organizations:
                print(f"      • {org}")
        
        if entities.locations:
            print(f"\n   📍 LOCATIONS ({len(entities.locations)}):")
            for loc in entities.locations:
                print(f"      • {loc}")
        
        if entities.dates:
            print(f"\n   📅 DATES ({len(entities.dates)}):")
            for date in entities.dates:
                print(f"      • {date}")
        
        if entities.events:
            print(f"\n   🎯 EVENTS ({len(entities.events)}):")
            for event in entities.events:
                print(f"      • {event}")
        
        total = entity_extractor.count_entities(entities)
        print(f"\n   📊 TOTAL: {total} entities extracted")
        print()
    
    # Demonstrate deduplication
    print("=" * 70)
    print("DEDUPLICATION DEMO")
    print("=" * 70)
    
    print("\nExtracting entities from all articles...")
    all_entities = [
        entity_extractor.extract_from_article(a['title'], a['content'])
        for a in articles
    ]
    
    print(f"\nIndividual extraction counts:")
    for i, ent in enumerate(all_entities, 1):
        count = entity_extractor.count_entities(ent)
        print(f"  Article {i}: {count} entities")
    
    # Merge and deduplicate
    merged = entity_extractor.deduplicate_entities(all_entities)
    
    print(f"\n✅ After merging and deduplication:")
    print(f"   Persons: {len(merged.persons)}")
    print(f"   Organizations: {len(merged.organizations)}")
    print(f"   Locations: {len(merged.locations)}")
    print(f"   Dates: {len(merged.dates)}")
    print(f"   TOTAL: {entity_extractor.count_entities(merged)} unique entities")
    
    # Show top entities
    print("\n" + "=" * 70)
    print("TOP ENTITIES DEMO")
    print("=" * 70)
    
    top_5 = entity_extractor.get_top_entities(merged, max_per_type=5)
    
    print(f"\n📊 Top 5 Entities of Each Type:")
    
    if top_5.persons:
        print(f"\n   👤 Top Persons:")
        for person in top_5.persons:
            print(f"      {person}")
    
    if top_5.organizations:
        print(f"\n   🏢 Top Organizations:")
        for org in top_5.organizations:
            print(f"      {org}")
    
    if top_5.locations:
        print(f"\n   📍 Top Locations:")
        for loc in top_5.locations:
            print(f"      {loc}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    
    print("\nKey Features Demonstrated:")
    print("  ✓ Article title + content extraction")
    print("  ✓ Multiple entity types (6 categories)")
    print("  ✓ Automatic deduplication across articles")
    print("  ✓ Top N entity selection")
    print("  ✓ Entity counting and statistics")
    
    if entity_extractor.is_available():
        print("\nspaCy Status: ✅ Ready")
    else:
        print("\nspaCy Status: ⚠️ Not available")
        print("Install with: python -m spacy download en_core_web_sm")
    
    print("\nThe Entity Extractor is ready to process scraped articles!")
    print("=" * 70)


if __name__ == "__main__":
    demo_entity_extraction()
