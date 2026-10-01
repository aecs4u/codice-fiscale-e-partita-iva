"""Tests for the Clerk dependency adapters used by the FastAPI app."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

pytest.importorskip("aecs4u_auth")

from codice_fiscale import auth


def clerk_user():
    return SimpleNamespace(
        id="user_123",
        email="person@example.com",
        full_name="Test Person",
        first_name="Test",
        last_name="Person",
    )


def test_required_clerk_dependency_maps_user_fields(monkeypatch):
    async def get_user(request):
        return clerk_user()

    monkeypatch.setattr(auth, "get_current_clerk_user", get_user)

    result = asyncio.run(auth.clerk_auth(object()))

    assert result == {
        "sub": "user_123",
        "email": "person@example.com",
        "name": "Test Person",
        "given_name": "Test",
        "family_name": "Person",
    }


def test_required_clerk_dependency_preserves_auth_errors(monkeypatch):
    async def reject_user(request):
        raise HTTPException(status_code=401, detail="Invalid token")

    monkeypatch.setattr(auth, "get_current_clerk_user", reject_user)

    with pytest.raises(HTTPException) as error:
        asyncio.run(auth.clerk_auth(object()))
    assert error.value.status_code == 401
    assert error.value.detail == "Invalid token"


def test_optional_clerk_dependency_returns_empty_mapping_without_user(monkeypatch):
    async def no_user(request):
        return None

    monkeypatch.setattr(auth, "get_current_clerk_user_optional", no_user)

    assert asyncio.run(auth.optional_clerk_auth(object())) == {}


def test_optional_clerk_dependency_maps_authenticated_user(monkeypatch):
    async def get_user(request):
        return clerk_user()

    monkeypatch.setattr(auth, "get_current_clerk_user_optional", get_user)

    result = asyncio.run(auth.optional_clerk_auth(object()))

    assert result["sub"] == "user_123"
    assert result["email"] == "person@example.com"


def test_user_metadata_includes_optional_profile_fields():
    result = auth.get_user_metadata(
        {
            "sub": "user_123",
            "email": "person@example.com",
            "name": "Test Person",
            "given_name": "Test",
            "family_name": "Person",
        }
    )

    assert result == {
        "user_id": "user_123",
        "email": "person@example.com",
        "name": "Test Person",
        "given_name": "Test",
        "family_name": "Person",
        "created_at": None,
        "updated_at": None,
    }


def test_user_metadata_handles_missing_claims():
    result = auth.get_user_metadata({})

    assert result["user_id"] is None
    assert result["email"] is None
    assert result["name"] is None
    assert result["created_at"] is None
    assert result["updated_at"] is None
