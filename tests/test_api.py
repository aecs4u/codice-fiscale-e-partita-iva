"""Regression tests for the web app and its FastAPI endpoints."""

import asyncio
import json
import os
from dataclasses import dataclass
from urllib.parse import urlencode, urlsplit
from unittest.mock import patch

import pytest

# Keep app configuration deterministic even when a developer has Clerk settings
# in their shell or local .env file.
with patch.dict(
    os.environ,
    {
        "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "",
        "CLERK_PUBLISHABLE_KEY": "",
        "CLERK_SECRET_KEY": "",
    },
):
    import dotenv

    with patch.object(dotenv, "load_dotenv"):
        from codice_fiscale import main


@dataclass
class ASGIResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def text(self):
        return self.content.decode("utf-8")

    def json(self):
        return json.loads(self.content)


class ASGIClient:
    """Small in-process client that exercises the app without HTTPX adapters."""

    def request(self, method, path, *, json_body=None):
        body = b"" if json_body is None else json.dumps(json_body).encode("utf-8")
        parts = urlsplit(path)
        headers = [(b"host", b"testserver")]
        if json_body is not None:
            headers.append((b"content-type", b"application/json"))
        if body:
            headers.append((b"content-length", str(len(body)).encode("ascii")))

        async def send_request():
            request_sent = False
            disconnect = asyncio.Event()
            response_status = None
            response_headers = {}
            response_body = bytearray()
            scope = {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.3"},
                "http_version": "1.1",
                "method": method.upper(),
                "scheme": "http",
                "path": parts.path,
                "raw_path": parts.path.encode("utf-8"),
                "query_string": parts.query.encode("ascii"),
                "headers": headers,
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
                "root_path": "",
                "app": main.app,
            }

            async def receive():
                nonlocal request_sent
                if not request_sent:
                    request_sent = True
                    return {"type": "http.request", "body": body, "more_body": False}
                await disconnect.wait()
                return {"type": "http.disconnect"}

            async def send(message):
                nonlocal response_status, response_headers
                if message["type"] == "http.response.start":
                    response_status = message["status"]
                    response_headers = {
                        key.decode("latin-1"): value.decode("latin-1")
                        for key, value in message.get("headers", [])
                    }
                elif message["type"] == "http.response.body":
                    response_body.extend(message.get("body", b""))

            await asyncio.wait_for(main.app(scope, receive, send), timeout=10)
            return ASGIResponse(response_status, response_headers, bytes(response_body))

        return asyncio.run(send_request())

    def get(self, path, *, params=None):
        if params:
            query = urlencode(params)
            path = f"{path}?{query}"
        return self.request("GET", path)

    def post(self, path, *, json):
        return self.request("POST", path, json_body=json)


@pytest.fixture
def client(monkeypatch):
    async def no_auth_for_tests():
        return {}

    monkeypatch.setitem(main.app.dependency_overrides, main.no_auth, no_auth_for_tests)
    return ASGIClient()


@pytest.fixture
def birthplace_index(monkeypatch):
    """Use a small fixed index so search behavior stays fast and predictable."""
    places = (
        {
            "value": "Torino, TO",
            "label": "Torino (TO)",
            "code": "L219",
            "kind": "municipality",
            "active": True,
            "period": "",
            "search_terms": ("torino", "torino provincia"),
        },
        {
            "value": "Torino, TO",
            "label": "Torino (TO)",
            "code": "L219",
            "kind": "municipality",
            "active": False,
            "period": "1815–1861",
            "search_terms": ("torino",),
        },
        {
            "value": "Torino-centro, TO",
            "label": "Torino Centro (TO)",
            "code": "Z999",
            "kind": "municipality",
            "active": True,
            "period": "",
            "search_terms": ("torino centro",),
        },
        {
            "value": "Stati Uniti",
            "label": "Stati Uniti",
            "code": "Z404",
            "kind": "country",
            "active": True,
            "period": "",
            "search_terms": ("stati uniti", "united states"),
        },
    )
    monkeypatch.setattr(main, "_birthplace_search_index", lambda: places)
    return places


def test_root_serves_the_accessible_web_app(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="fiscalTab"' in response.text
    assert 'id="vatTab"' in response.text
    assert 'id="main-content"' in response.text
    assert "/static/aecs4u-theme/css/design-tokens.css" in response.text
    assert "/static/css/app.css" in response.text
    assert 'id="fiscal-validate"' in response.text
    assert 'role="combobox"' in response.text
    assert 'aria-live="polite"' in response.text
    assert 'id="birthplaceOptions" role="listbox"' in response.text
    assert "row.textContent = option.period" in response.text
    assert "row.innerHTML" not in response.text


def test_root_disables_protected_actions_when_auth_is_enabled(client, monkeypatch):
    monkeypatch.setattr(main, "AUTH_ENABLED", True)
    monkeypatch.setenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "pk_test_example")

    response = client.get("/")

    assert response.status_code == 200
    assert 'id="signInButton"' in response.text
    assert '<button class="btn btn-primary" type="submit" data-api-action data-i18n="validateButton" disabled>' in response.text


def test_api_discovery_lists_birthplace_search(client):
    response = client.get("/api")

    assert response.status_code == 200
    assert response.json()["endpoints"]["birthplaces"]["search"] == (
        "GET /birthplaces/search?q=<name>"
    )


def test_birthplace_search_matches_aliases_and_sorts_active_first(
    client, birthplace_index
):
    response = client.get("/birthplaces/search", params={"q": "TORINO"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert [result["code"] for result in results] == ["L219", "Z999", "L219"]
    assert [result["active"] for result in results] == [True, True, False]
    assert results[0]["value"] == "Torino, TO"
    assert results[0]["kind"] == "municipality"
    assert results[2]["period"] == "1815–1861"
    assert all("search_terms" not in result for result in results)


def test_birthplace_search_accepts_transliterated_queries(client, birthplace_index):
    response = client.get("/birthplaces/search", params={"q": "united"})

    assert response.status_code == 200
    assert response.json()["results"][0]["value"] == "Stati Uniti"


def test_birthplace_search_limits_results(client, birthplace_index):
    response = client.get(
        "/birthplaces/search", params={"q": "torino", "limit": 1}
    )

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"q": "a"},
        {"q": "t" * 81},
        {"q": "torino", "limit": 0},
        {"q": "torino", "limit": 21},
    ],
)
def test_birthplace_search_rejects_invalid_parameters(client, params):
    response = client.get("/birthplaces/search", params=params)

    assert response.status_code == 422


def test_birthplace_search_returns_empty_results_for_no_match(
    client, birthplace_index
):
    response = client.get("/birthplaces/search", params={"q": "xyz"})

    assert response.status_code == 200
    assert response.json() == {"results": []}


def test_birthplace_index_deduplicates_aliases_and_keeps_historic_periods(
    monkeypatch,
):
    record = {
        "name": "Torino",
        "name_trans": "Turin",
        "code": "L219",
        "province": "TO",
        "active": True,
    }
    historic_record = {
        "name": "Old Torino",
        "code": "X100",
        "province": "TO",
        "active": False,
        "date_created": "1815-01-01",
        "date_deleted": "1861-03-17",
    }
    monkeypatch.setattr(
        main.codice_fiscale,
        "_DATA",
        {
            "municipalities": {
                "Torino": [record],
                "Turin": [record],
                "Old Torino": [historic_record],
            },
            "countries": {
                "Italia": [
                    {
                        "name": "Italia",
                        "code": "Z100",
                        "active": True,
                    }
                ]
            },
        },
    )
    main._birthplace_search_index.cache_clear()
    try:
        places = main._birthplace_search_index()
    finally:
        main._birthplace_search_index.cache_clear()

    assert len(places) == 3
    torino = next(place for place in places if place["code"] == "L219")
    assert torino["value"] == "Turin, TO"
    assert set(torino["search_terms"]) == {"torino", "turin"}
    historic = next(place for place in places if place["code"] == "X100")
    assert historic["period"] == "1815–1861"
    assert historic["active"] is False
    country = next(place for place in places if place["code"] == "Z100")
    assert country["kind"] == "country"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_validate_fiscal_code_valid(client):
    response = client.post(
        "/fiscal-code/validate", json={"code": "CCCFBA85D03L219P"}
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["details"] is not None


def test_validate_fiscal_code_invalid(client):
    response = client.post("/fiscal-code/validate", json={"code": "INVALID123"})

    assert response.status_code == 200
    assert response.json() == {
        "valid": False,
        "code": "INVALID123",
        "details": None,
    }


def test_encode_and_decode_fiscal_code(client):
    response = client.post(
        "/fiscal-code/encode",
        json={
            "lastname": "Caccamo",
            "firstname": "Fabio",
            "gender": "M",
            "birthdate": "03/04/1985",
            "birthplace": "Torino, TO",
        },
    )

    assert response.status_code == 200
    code = response.json()["code"]
    assert len(code) == 16
    decoded = client.post("/fiscal-code/decode", json={"code": code})
    assert decoded.status_code == 200
    assert decoded.json()["birthplace"]["code"] == "L219"


def test_encode_fiscal_code_rejects_invalid_gender(client):
    response = client.post(
        "/fiscal-code/encode",
        json={
            "lastname": "Caccamo",
            "firstname": "Fabio",
            "gender": "X",
            "birthdate": "03/04/1985",
            "birthplace": "Torino, TO",
        },
    )

    assert response.status_code == 400


def test_vat_endpoints_round_trip(client):
    encoded = client.post("/vat/encode", json={"base_number": "0123456789"})

    assert encoded.status_code == 200
    vat_number = encoded.json()["partita_iva"]
    assert len(vat_number) == 11
    assert vat_number.startswith("0123456789")

    validated = client.post("/vat/validate", json={"partita_iva": vat_number})
    assert validated.status_code == 200
    assert validated.json()["valid"] is True
    decoded = client.post("/vat/decode", json={"partita_iva": vat_number})
    assert decoded.status_code == 200
    assert decoded.json()["base_number"] == "0123456789"


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/fiscal-code/validate", {}),
        ("/fiscal-code/encode", {"lastname": "Test"}),
        ("/vat/validate", {}),
        ("/vat/encode", {}),
    ],
)
def test_api_reports_missing_required_fields(client, path, payload):
    response = client.post(path, json=payload)
    assert response.status_code == 422
