import os
from unittest.mock import patch

import pytest

try:
    from fastapi import HTTPException
    from fastapi.testclient import TestClient

    from codice_fiscale.app import app
    from codice_fiscale.auth import ClerkAuth
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI dependencies not available")
class TestClerkAuth:
    """Test Clerk authentication functionality."""

    def test_clerk_auth_missing_key(self):
        """Test ClerkAuth raises error when publishable key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Clerk publishable key not found"):
                ClerkAuth()

    def test_clerk_auth_invalid_key_format(self):
        """Test ClerkAuth raises error for invalid key format."""
        with pytest.raises(ValueError, match="Invalid Clerk publishable key format"):
            ClerkAuth("invalid_key")

    def test_clerk_auth_valid_key(self):
        """Test ClerkAuth initializes correctly with valid key."""
        test_key = "pk_test_instance123_randomstring"
        clerk_auth = ClerkAuth(test_key)
        assert clerk_auth.publishable_key == test_key
        assert clerk_auth.instance_id == "instance123"
        assert "instance123" in clerk_auth.jwks_url

    def test_verify_token_missing_claims(self):
        """Test token verification fails for tokens missing required claims."""
        test_key = "pk_test_instance123_randomstring"
        clerk_auth = ClerkAuth(test_key)

        # Mock jwt.decode to return token without required claims
        with patch("codice_fiscale.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {"exp": 1234567890}  # Missing 'sub' and 'iss'

            with pytest.raises(HTTPException) as exc_info:
                clerk_auth.verify_token("fake_token")

            assert exc_info.value.status_code == 401
            assert "Token missing subject claim" in str(exc_info.value.detail)

    def test_verify_token_invalid_issuer(self):
        """Test token verification fails for invalid issuer."""
        test_key = "pk_test_instance123_randomstring"
        clerk_auth = ClerkAuth(test_key)

        with patch("codice_fiscale.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "user_123",
                "iss": "https://wrong-instance.clerk.accounts.dev"
            }

            with pytest.raises(HTTPException) as exc_info:
                clerk_auth.verify_token("fake_token")

            assert exc_info.value.status_code == 401
            assert "Invalid issuer" in str(exc_info.value.detail)

    def test_verify_token_valid(self):
        """Test successful token verification."""
        test_key = "pk_test_instance123_randomstring"
        clerk_auth = ClerkAuth(test_key)

        expected_payload = {
            "sub": "user_123",
            "iss": "https://instance123.clerk.accounts.dev",
            "email": "test@example.com",
            "name": "Test User"
        }

        with patch("codice_fiscale.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = expected_payload

            result = clerk_auth.verify_token("valid_token")
            assert result == expected_payload


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI dependencies not available")
class TestAuthenticatedAPI:
    """Test API with authentication enabled."""

    def test_api_without_auth_env(self):
        """Test API works without authentication when env var not set."""
        # Clear all Clerk-related env vars and avoid loading .env
        env_patch = {
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "",
            "CLERK_PUBLISHABLE_KEY": "",
            "CLERK_SECRET_KEY": ""
        }
        with patch.dict(os.environ, env_patch, clear=False):
            # Mock dotenv load_dotenv to do nothing
            with patch("codice_fiscale.auth.load_dotenv"):
                with patch("codice_fiscale.app.load_dotenv"):
                    # Need to reload modules to pick up env changes
                    import importlib

                    from codice_fiscale import app as app_module
                    from codice_fiscale import auth as auth_module
                    importlib.reload(auth_module)
                    importlib.reload(app_module)

                    client = TestClient(app_module.app)
                    response = client.get("/api")
                    assert response.status_code == 200

                    data = response.json()
                    assert data["authentication"]["enabled"] is False
                    assert data["authentication"]["type"] == "None"

    def test_api_with_auth_env_but_no_token(self):
        """Test API requires auth when env var is set."""
        test_key = "pk_test_instance123_randomstring"

        with patch.dict(os.environ, {"CLERK_PUBLISHABLE_KEY": test_key}):
            # Need to reload both auth and app modules to pick up the env var
            import importlib

            from codice_fiscale import app as app_module
            from codice_fiscale import auth as auth_module
            importlib.reload(auth_module)
            importlib.reload(app_module)

            client = TestClient(app_module.app)

            # API endpoint should work (optional auth)
            response = client.get("/api")
            assert response.status_code == 200

            data = response.json()
            assert data["authentication"]["enabled"] is True
            assert data["authentication"]["type"] == "Clerk JWT Bearer Token"

            # Protected endpoint should fail without token (403 or 401)
            response = client.post("/fiscal-code/validate", json={"code": "TEST"})
            assert response.status_code in [401, 403]

    def test_api_with_valid_token(self):
        """Test API works with valid authentication token."""
        test_key = "pk_test_instance123_randomstring"

        with patch.dict(os.environ, {"NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": test_key}):
            # Mock dotenv to avoid loading real .env
            with patch("codice_fiscale.auth.load_dotenv"):
                with patch("codice_fiscale.app.load_dotenv"):
                    import importlib

                    from codice_fiscale import app as app_module
                    from codice_fiscale import auth as auth_module
                    importlib.reload(auth_module)
                    importlib.reload(app_module)

                    client = TestClient(app_module.app)

                    # Mock the JWT verification
                    with patch("codice_fiscale.auth.jwt.decode") as mock_decode:
                        mock_decode.return_value = {
                            "sub": "user_123",
                            "iss": "https://instance123.clerk.accounts.dev",
                            "email": "test@example.com"
                        }

                        headers = {"Authorization": "Bearer valid_token"}
                        response = client.post(
                            "/fiscal-code/validate",
                            json={"code": "CCCFBA85D03L219P"},
                            headers=headers
                        )

                        # Should succeed (token is valid, fiscal code is valid)
                        assert response.status_code == 200

    def test_health_endpoint_no_auth_required(self):
        """Test health endpoint doesn't require authentication."""
        test_key = "pk_test_instance123_randomstring"

        with patch.dict(os.environ, {"CLERK_PUBLISHABLE_KEY": test_key}):
            import importlib

            from codice_fiscale import app as app_module
            from codice_fiscale import auth as auth_module
            importlib.reload(auth_module)
            importlib.reload(app_module)

            client = TestClient(app_module.app)

            # Health endpoint should work without authentication
            response = client.get("/health")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "healthy"


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI dependencies not available")
class TestAuthUtilities:
    """Test authentication utility functions."""

    def test_get_user_id(self):
        """Test extracting user ID from auth data."""
        from codice_fiscale.auth import get_user_id

        auth_data = {"sub": "user_123", "email": "test@example.com"}
        assert get_user_id(auth_data) == "user_123"

        assert get_user_id({}) is None

    def test_get_user_email(self):
        """Test extracting user email from auth data."""
        from codice_fiscale.auth import get_user_email

        auth_data = {"sub": "user_123", "email": "test@example.com"}
        assert get_user_email(auth_data) == "test@example.com"

        assert get_user_email({}) is None

    def test_get_user_metadata(self):
        """Test extracting user metadata from auth data."""
        from codice_fiscale.auth import get_user_metadata

        auth_data = {
            "sub": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "created_at": 1234567890,
            "updated_at": 1234567891
        }

        metadata = get_user_metadata(auth_data)
        assert metadata["user_id"] == "user_123"
        assert metadata["email"] == "test@example.com"
        assert metadata["name"] == "Test User"
        assert metadata["given_name"] == "Test"
        assert metadata["family_name"] == "User"
        assert metadata["created_at"] == 1234567890
        assert metadata["updated_at"] == 1234567891
