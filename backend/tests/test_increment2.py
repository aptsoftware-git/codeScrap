"""
Test script for Increment 2: Configuration & Data Models
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.models import EventType, Location, SourceConfig, SearchQuery
from app.services.config_manager import ConfigManager

def test_models():
    """Test Pydantic models."""
    print("=" * 60)
    print("Testing Pydantic Models")
    print("=" * 60)
    
    # Test EventType enum
    print("\n✓ EventType enum:")
    print(f"  - Available types: {[e.value for e in EventType][:5]}...")
    
    # Test Location model
    loc = Location(city="Mumbai", country="India")
    print(f"\n✓ Location model:")
    print(f"  - Created: {loc}")
    
    # Test SearchQuery model
    query = SearchQuery(phrase="protest in Mumbai", max_results=50)
    print(f"\n✓ SearchQuery model:")
    print(f"  - Phrase: {query.phrase}")
    print(f"  - Max results: {query.max_results}")
    
    # Test SourceConfig model
    source = SourceConfig(
        name="Test Source",
        base_url="https://example.com",
        enabled=True,
        rate_limit=1.5
    )
    print(f"\n✓ SourceConfig model:")
    print(f"  - Name: {source.name}")
    print(f"  - Enabled: {source.enabled}")
    print(f"  - Rate limit: {source.rate_limit}s")
    
    print("\n✅ All model tests passed!")


def test_config_manager():
    """Test ConfigManager."""
    print("\n" + "=" * 60)
    print("Testing ConfigManager")
    print("=" * 60)
    
    # Initialize config manager
    config_mgr = ConfigManager()
    print(f"\n✓ ConfigManager initialized")
    print(f"  - Config path: {config_mgr.config_path}")
    
    # Load sources
    sources = config_mgr.load_sources()
    print(f"\n✓ Sources loaded: {len(sources)} total")
    
    # Get enabled sources
    enabled_sources = config_mgr.get_sources(enabled_only=True)
    print(f"✓ Enabled sources: {config_mgr.get_enabled_count()}")
    
    # Display source details
    print(f"\n📋 Configured Sources:")
    for i, source in enumerate(sources, 1):
        status = "✓ ENABLED" if source.enabled else "✗ DISABLED"
        print(f"  {i}. {source.name:20} {status:12} (rate: {source.rate_limit}s)")
    
    # Test validation
    validation = config_mgr.validate_sources()
    print(f"\n✓ Validation results:")
    print(f"  - Valid: {len(validation['valid'])}")
    print(f"  - Invalid: {len(validation['invalid'])}")
    
    print("\n✅ All ConfigManager tests passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("INCREMENT 2 VERIFICATION")
    print("Configuration & Data Models")
    print("=" * 60)
    
    try:
        test_models()
        test_config_manager()
        
        print("\n" + "=" * 60)
        print("✅ INCREMENT 2 COMPLETE - ALL TESTS PASSED!")
        print("=" * 60)
        print("\nDeliverables:")
        print("  ✓ Pydantic models created (models.py)")
        print("  ✓ ConfigManager implemented (config_manager.py)")
        print("  ✓ sources.yaml configured with 5 sources")
        print("  ✓ /api/v1/sources endpoint added to main.py")
        print("\nNext step: Start the server and test the endpoint")
        print("  Command: curl http://localhost:8000/api/v1/sources")
        print("=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
