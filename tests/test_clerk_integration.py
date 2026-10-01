#!/usr/bin/env python3
"""Test script to help with Clerk authentication integration."""

import base64
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_mock_jwt_token() -> str:
    """Create a mock JWT token for testing (DO NOT use in production)."""

    # JWT Header
    header = {
        "alg": "RS256",
        "typ": "JWT"
    }

    # JWT Payload
    instance_id = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "").split("_")[2] if os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY") else ""

    payload = {
        "sub": "user_test123456",  # User ID
        "iss": f"https://{instance_id}.clerk.accounts.dev" if instance_id else "https://test.clerk.accounts.dev",
        "aud": "test",
        "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now().timestamp()),
        "email": "test@example.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User"
    }

    # Base64 encode (without signature - FOR TESTING ONLY)
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

    # Create mock signature (DO NOT use in production)
    signature = "mock_signature_for_testing_only"

    return f"{header_b64}.{payload_b64}.{signature}"

def test_api_endpoints():
    """Test API endpoints with different authentication scenarios."""
    import subprocess

    base_url = "http://localhost:8000"

    print("🔗 Testing API Endpoints")
    print("=" * 50)

    # Test 1: Health endpoint (should always work)
    print("1. Testing health endpoint...")
    result = subprocess.run([
        "curl", "-s", f"{base_url}/health"
    ], capture_output=True, text=True)
    print(f"   Status: {'✅ OK' if 'healthy' in result.stdout else '❌ Error'}")

    # Test 2: Root endpoint without auth
    print("2. Testing root endpoint...")
    result = subprocess.run([
        "curl", "-s", f"{base_url}/"
    ], capture_output=True, text=True)
    print(f"   Status: {'✅ OK' if result.returncode == 0 else '❌ Error'}")

    # Test 3: Protected endpoint without token
    print("3. Testing protected endpoint without token...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", f"{base_url}/fiscal-code/validate",
        "-H", "Content-Type: application/json",
        "-d", '{"code": "CCCFBA85D03L219P"}'
    ], capture_output=True, text=True)

    if "Not authenticated" in result.stdout:
        print("   Status: ✅ Correctly protected")
    else:
        print(f"   Status: ❌ Unexpected response: {result.stdout[:100]}")

    # Test 4: Protected endpoint with invalid token
    print("4. Testing protected endpoint with invalid token...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", f"{base_url}/fiscal-code/validate",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer invalid_token",
        "-d", '{"code": "CCCFBA85D03L219P"}'
    ], capture_output=True, text=True)

    if "Not enough segments" in result.stdout:
        print("   Status: ✅ Correctly rejects invalid token (this is the error you saw)")
    else:
        print(f"   Status: ❌ Unexpected response: {result.stdout[:100]}")

    # Test 5: Protected endpoint with mock token (for testing only)
    print("5. Testing protected endpoint with mock token...")
    mock_token = create_mock_jwt_token()

    result = subprocess.run([
        "curl", "-s", "-X", "POST", f"{base_url}/fiscal-code/validate",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {mock_token}",
        "-d", '{"code": "CCCFBA85D03L219P"}'
    ], capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if "valid" in response:
            print("   Status: ✅ Successfully authenticated with mock token")
        else:
            print(f"   Status: ❌ Unexpected response: {response}")
    except json.JSONDecodeError:
        print(f"   Status: ❌ Invalid JSON response: {result.stdout[:100]}")

def get_clerk_setup_instructions():
    """Provide instructions for getting a real Clerk JWT token."""
    print("\n📋 How to Get a Real Clerk JWT Token")
    print("=" * 50)
    print("The error you're seeing occurs because you need a valid JWT token from Clerk.")
    print("Here are the steps to get one:\n")

    print("1. 🌐 Set up a Clerk application:")
    print("   - Go to https://clerk.com/")
    print("   - Sign up/log in to your Clerk dashboard")
    print("   - Create a new application or use existing one")
    print("")

    print("2. 🔧 Configure your application:")
    print("   - Copy your publishable key (starts with pk_test_)")
    print("   - Copy your secret key (starts with sk_test_)")
    print("   - Update your .env file with these keys")
    print("")

    print("3. 🔐 Get a JWT token (choose one method):")
    print("")
    print("   Method A - Using Clerk's JavaScript SDK:")
    print("   ```html")
    print("   <script src='https://clerk.com/clerk.js'></script>")
    print("   <script>")
    print("     Clerk.load()")
    print("     // After user signs in, get token:")
    print("     const token = await Clerk.session.getToken()")
    print("   </script>")
    print("   ```")
    print("")

    print("   Method B - Using curl (sign-in flow):")
    print("   ```bash")
    print("   # This is a simplified example - actual implementation")
    print("   # requires handling sign-in flow with your Clerk instance")
    print("   ```")
    print("")

    print("   Method C - Using Clerk's backend API:")
    print("   ```bash")
    print("   # Get session token for a specific user")
    print("   curl -X POST https://api.clerk.com/v1/sessions \\")
    print("     -H 'Authorization: Bearer YOUR_SECRET_KEY' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"user_id\": \"user_xxx\"}'")
    print("   ```")
    print("")

    print("4. 🧪 Test the API:")
    print("   ```bash")
    print("   curl -X POST http://localhost:8000/fiscal-code/validate \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("     -d '{\"code\": \"CCCFBA85D03L219P\"}'")
    print("   ```")
    print("")

    print("💡 For development/testing, you can also:")
    print("   - Disable authentication by removing the CLERK_* env vars")
    print("   - Use the mock token generated by this script (NOT for production)")

if __name__ == "__main__":
    print("🔐 Clerk Integration Test Tool")
    print("=" * 50)

    # Check environment
    pub_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    secret_key = os.getenv("CLERK_SECRET_KEY")

    print(f"Publishable Key: {'Set' if pub_key else 'Not set'}")
    print(f"Secret Key: {'Set' if secret_key else 'Not set'}")
    print("")

    # Test API endpoints
    test_api_endpoints()

    # Provide setup instructions
    get_clerk_setup_instructions()

    print("\n🎯 Summary:")
    print("The 'Not enough segments' error occurs when using invalid JWT tokens.")
    print("Follow the instructions above to get a proper Clerk JWT token.")
