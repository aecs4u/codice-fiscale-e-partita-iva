#!/usr/bin/env python3
"""Debug script for Clerk authentication issues."""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_clerk_keys():
    """Check Clerk key configuration."""
    print("🔍 Checking Clerk Configuration")
    print("=" * 50)

    # Check publishable key
    pub_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY") or os.getenv("CLERK_PUBLISHABLE_KEY")
    secret_key = os.getenv("CLERK_SECRET_KEY")

    print(f"Publishable Key: {pub_key[:20]}...{pub_key[-10:] if pub_key and len(pub_key) > 30 else pub_key}")
    print(f"Secret Key: {'Set' if secret_key else 'Not set'}")
    print()

    if not pub_key:
        print("❌ ERROR: No publishable key found!")
        print("   Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY or CLERK_PUBLISHABLE_KEY")
        return False

    # Check key format
    if not pub_key.startswith(("pk_test_", "pk_live_")):
        print("❌ ERROR: Invalid publishable key format!")
        print("   Should start with pk_test_ or pk_live_")
        return False

    parts = pub_key.split("_")
    if len(parts) < 3:
        print("❌ ERROR: Incomplete publishable key!")
        print(f"   Key has {len(parts)} parts, expected at least 3")
        print("   Format should be: pk_test_{instance_id}_{random}")
        return False

    instance_id = parts[2]
    print(f"✅ Instance ID extracted: {instance_id}")

    # Check if instance_id looks valid
    if not instance_id or len(instance_id) < 10:
        print("⚠️  WARNING: Instance ID looks suspicious (too short)")

    # Check JWKS URL construction
    jwks_url = f"https://{instance_id}.clerk.accounts.dev/.well-known/jwks.json"
    print(f"📍 JWKS URL: {jwks_url}")

    return True

def test_jwt_token():
    """Test JWT token parsing with a sample token."""
    print("\n🧪 Testing JWT Token Parsing")
    print("=" * 50)

    # Sample invalid JWT (intentionally malformed)
    invalid_tokens = [
        "",  # Empty
        "invalid",  # No segments
        "header.payload",  # Missing signature
        "not.a.valid.jwt.token",  # Too many segments
    ]

    try:
        import jwt

        for token in invalid_tokens:
            print(f"Testing token: '{token[:20]}...' ", end="")
            try:
                decoded = jwt.decode(
                    token,
                    options={"verify_signature": False},
                    algorithms=["RS256"]
                )
                print("✅ Parsed successfully")
            except jwt.InvalidTokenError as e:
                print(f"❌ {e!s}")

    except ImportError:
        print("❌ PyJWT not available for testing")

if __name__ == "__main__":
    print("🔐 Clerk Authentication Debug Tool")
    print("=" * 50)

    success = check_clerk_keys()
    test_jwt_token()

    if not success:
        print("\n💡 To fix:")
        print("1. Check your Clerk dashboard for the correct publishable key")
        print("2. Ensure the key is completely copied (no truncation)")
        print("3. Verify the key format: pk_test_{{instance}}_{{random}}")
        print("4. Update your .env file with the correct key")
