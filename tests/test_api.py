
import os
from unittest.mock import patch

import pytest

try:
    from fastapi.testclient import TestClient

    # Import and configure app without authentication for testing
    # Clear Clerk environment variables to disable auth
    with patch.dict(os.environ, {
        'CLERK_PUBLISHABLE_KEY': '',
        'NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY': '',
        'CLERK_SECRET_KEY': ''
    }):
        with patch('codice_fiscale.app.load_dotenv'), patch('codice_fiscale.auth.load_dotenv'):
            import importlib

            import codice_fiscale.app
            import codice_fiscale.auth
            importlib.reload(codice_fiscale.auth)
            importlib.reload(codice_fiscale.app)

            from codice_fiscale.app import app

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI dependencies not available")
class TestAPI:
    """Test the FastAPI validation endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test the API info endpoint returns API information."""
        response = self.client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert "fiscal_code" in data["endpoints"]
        assert "vat" in data["endpoints"]

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_validate_fiscal_code_valid(self):
        """Test fiscal code validation with valid code."""
        # Use a known valid fiscal code from existing tests
        valid_code = "CCCFBA85D03L219P"

        response = self.client.post(
            "/fiscal-code/validate",
            json={"code": valid_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["code"] == valid_code
        assert "details" in data

    def test_validate_fiscal_code_invalid(self):
        """Test fiscal code validation with invalid code."""
        invalid_code = "INVALID123"

        response = self.client.post(
            "/fiscal-code/validate",
            json={"code": invalid_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["code"] == invalid_code
        assert data["details"] is None

    def test_encode_fiscal_code(self):
        """Test fiscal code encoding."""
        request_data = {
            "lastname": "Caccamo",
            "firstname": "Fabio",
            "gender": "M",
            "birthdate": "03/04/1985",
            "birthplace": "Torino"
        }

        response = self.client.post("/fiscal-code/encode", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert len(data["code"]) == 16

    def test_encode_fiscal_code_invalid_data(self):
        """Test fiscal code encoding with invalid data."""
        request_data = {
            "lastname": "Caccamo",
            "firstname": "Fabio",
            "gender": "X",  # Invalid gender should cause error
            "birthdate": "03/04/1985",
            "birthplace": "Torino"
        }

        response = self.client.post("/fiscal-code/encode", json=request_data)
        assert response.status_code == 400

    def test_decode_fiscal_code(self):
        """Test fiscal code decoding."""
        valid_code = "CCCFBA85D03L219P"

        response = self.client.post(
            "/fiscal-code/decode",
            json={"code": valid_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "gender" in data
        assert "birthdate" in data
        assert "birthplace" in data

    def test_validate_vat_valid(self):
        """Test VAT validation with valid number."""
        # Create a valid VAT number first
        from codice_fiscale import partitaiva
        valid_vat = partitaiva.encode("0123456789")

        response = self.client.post(
            "/vat/validate",
            json={"partita_iva": valid_vat}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["code"] == valid_vat
        assert "details" in data

    def test_validate_vat_invalid(self):
        """Test VAT validation with invalid number."""
        invalid_vat = "12345678999"  # Wrong check digit

        response = self.client.post(
            "/vat/validate",
            json={"partita_iva": invalid_vat}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["code"] == invalid_vat

    def test_encode_vat(self):
        """Test VAT encoding."""
        base_number = "0123456789"

        response = self.client.post(
            "/vat/encode",
            json={"base_number": base_number}
        )
        assert response.status_code == 200
        data = response.json()
        assert "partita_iva" in data
        assert len(data["partita_iva"]) == 11
        assert data["partita_iva"].startswith(base_number)

    def test_encode_vat_invalid_base(self):
        """Test VAT encoding with invalid base number."""
        invalid_base = "123456789"  # Too short

        response = self.client.post(
            "/vat/encode",
            json={"base_number": invalid_base}
        )
        assert response.status_code == 400

    def test_decode_vat(self):
        """Test VAT decoding."""
        from codice_fiscale import partitaiva
        valid_vat = partitaiva.encode("0123456789")

        response = self.client.post(
            "/vat/decode",
            json={"partita_iva": valid_vat}
        )
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert "valid" in data
        assert "base_number" in data
        assert "check_digit" in data
        assert data["valid"] is True

    def test_missing_request_fields(self):
        """Test API endpoints with missing required fields."""
        # Test fiscal code validation without code
        response = self.client.post("/fiscal-code/validate", json={})
        assert response.status_code == 422  # Validation error

        # Test VAT validation without partita_iva
        response = self.client.post("/vat/validate", json={})
        assert response.status_code == 422  # Validation error

        # Test fiscal code encoding with missing fields
        response = self.client.post("/fiscal-code/encode", json={"lastname": "Test"})
        assert response.status_code == 422  # Validation error

    def test_api_response_structure(self):
        """Test that API responses have correct structure."""
        from codice_fiscale import partitaiva
        valid_vat = partitaiva.encode("0123456789")

        response = self.client.post(
            "/vat/validate",
            json={"partita_iva": valid_vat}
        )
        assert response.status_code == 200
        data = response.json()

        # Check ValidationResponse structure
        required_fields = ["valid", "code"]
        for field in required_fields:
            assert field in data

        # Details should be present for valid codes
        assert "details" in data
        assert data["details"] is not None

