"""
Test the /api/v1/sources endpoint
"""

import requests
import json

def test_sources_endpoint():
    """Test the GET /api/v1/sources endpoint."""
    url = "http://localhost:8000/api/v1/sources"
    
    print("=" * 70)
    print("Testing /api/v1/sources endpoint")
    print("=" * 70)
    
    try:
        # Test with enabled_only=True (default)
        print("\n1. Testing with enabled_only=True (default):")
        print(f"   GET {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        print(f"\n   Status Code: {response.status_code}")
        print(f"   Total Sources: {data['total_count']}")
        print(f"   Enabled Sources: {data['enabled_count']}")
        print(f"\n   Enabled Sources List:")
        for i, source in enumerate(data['sources'], 1):
            print(f"     {i}. {source['name']}")
            print(f"        Base URL: {source['base_url']}")
            print(f"        Rate Limit: {source['rate_limit']}s")
            print(f"        Search Template: {source.get('search_url_template', 'N/A')}")
        
        # Test with enabled_only=False
        print(f"\n2. Testing with enabled_only=False:")
        print(f"   GET {url}?enabled_only=false")
        response = requests.get(f"{url}?enabled_only=false")
        response.raise_for_status()
        
        data = response.json()
        print(f"\n   Status Code: {response.status_code}")
        print(f"   Total Sources: {data['total_count']}")
        print(f"\n   All Sources List:")
        for i, source in enumerate(data['sources'], 1):
            status = "✓ ENABLED" if source['enabled'] else "✗ DISABLED"
            print(f"     {i}. {source['name']:20} {status}")
        
        print("\n" + "=" * 70)
        print("✅ /api/v1/sources endpoint is working correctly!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to http://localhost:8000")
        print("   Make sure the server is running:")
        print("   cd backend && venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sources_endpoint()
