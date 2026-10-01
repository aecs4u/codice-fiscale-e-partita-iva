#!/usr/bin/env python3
"""
Test script for Clerk authentication integration.

This script helps verify that:
1. Environment variables are loaded correctly
2. Authentication is enabled/disabled appropriately
3. API endpoints work with and without authentication
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    print("🔧 Environment Configuration:")
    print("-" * 40)

    # Check for Clerk environment variables
    next_public_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    clerk_key = os.getenv("CLERK_PUBLISHABLE_KEY")
    secret_key = os.getenv("CLERK_SECRET_KEY")

    print(f"NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: {'✅ Set' if next_public_key else '❌ Not set'}")
    print(f"CLERK_PUBLISHABLE_KEY: {'✅ Set' if clerk_key else '❌ Not set'}")
    print(f"CLERK_SECRET_KEY: {'✅ Set' if secret_key else '❌ Not set'}")

    publishable_key = next_public_key or clerk_key

    if publishable_key:
        print("\n📋 Publishable Key Details:")
        print(f"Key: {publishable_key[:20]}...")

        # Parse the key to extract instance info
        parts = publishable_key.split("_")
        if len(parts) >= 3:
            key_type = parts[1]  # test or live
            instance_id = parts[2]
            print(f"Type: {key_type}")
            print(f"Instance ID: {instance_id}")
            print(f"JWKS URL: https://{instance_id}.clerk.accounts.dev/.well-known/jwks.json")
        else:
            print("⚠️  Invalid key format")

    print("\n🔐 Authentication Status:")
    print("-" * 40)

    # Test authentication module
    try:
        from codice_fiscale.auth import ClerkAuth

        if publishable_key:
            clerk_auth = ClerkAuth()
            print("✅ ClerkAuth initialized successfully")
            print(f"Instance ID: {clerk_auth.instance_id}")
            print(f"JWKS URL: {clerk_auth.jwks_url}")
        else:
            print("❌ No publishable key found - authentication disabled")

    except ImportError as e:
        print(f"❌ Authentication module import failed: {e}")
        print("💡 Install API dependencies: pip install 'python-codice_fiscale[api]'")
    except ValueError as e:
        print(f"❌ Authentication configuration error: {e}")

    print("\n🌐 FastAPI Application:")
    print("-" * 40)

    # Test FastAPI app
    try:
        from codice_fiscale.app import AUTH_ENABLED, app

        print(f"Authentication enabled: {'✅ Yes' if AUTH_ENABLED else '❌ No'}")

        if AUTH_ENABLED:
            print("\n📝 To test authenticated endpoints:")
            print("1. Start the server: python -m codice_fiscale.__main_api__")
            print("2. Get a JWT token from your Clerk application")
            print("3. Make requests with Authorization header:")
            print("   curl -H 'Authorization: Bearer <token>' http://localhost:8000/fiscal-code/validate")
        else:
            print("\n📝 Authentication is disabled. All endpoints are public.")
            print("To enable authentication, ensure CLERK_PUBLISHABLE_KEY is set.")

    except ImportError as e:
        print(f"❌ FastAPI app import failed: {e}")

    print("\n🧪 Quick API Test:")
    print("-" * 40)

    # Quick test of the API
    try:
        from fastapi.testclient import TestClient

        from codice_fiscale.app import app

        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint accessible")
            print(f"Authentication: {data['authentication']['type']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")

        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")

        # Test protected endpoint without auth
        response = client.post("/fiscal-code/validate", json={"code": "TEST"})
        if AUTH_ENABLED:
            if response.status_code == 401:
                print("✅ Protected endpoint correctly requires authentication")
            else:
                print(f"❌ Protected endpoint should return 401, got {response.status_code}")
        else:
            print("ℹ️  All endpoints are public (authentication disabled)")

    except ImportError:
        print("❌ TestClient not available - install httpx for testing")
    except Exception as e:
        print(f"❌ API test failed: {e}")

except ImportError:
    print("❌ Missing dependencies. Install with: pip install 'python-codice_fiscale[api]'")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print(f"\n{'='*40}")
print("🎯 Next Steps:")
print("1. Start the API server: python -m codice_fiscale.__main_api__")
print("2. Visit http://localhost:8000/docs for API documentation")
print("3. Create a JWT token in your Clerk dashboard to test authentication")
print("4. Use the token in API requests: Authorization: Bearer <token>")
