from __future__ import annotations

import hashlib
import hmac
import json

import httpx
import pytest

from scripts.green_invoice_integration_client import (
    AsyncGreenInvoiceClient,
    GreenInvoiceClient,
    GreenInvoiceConfig,
    GreenInvoiceError,
    GreenInvoiceValidationError,
    build_simple_document_payload,
    verify_webhook_hmac,
)


def make_client(handler, token: str | None = "tok") -> GreenInvoiceClient:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.greeninvoice.co.il/api/v1")
    return GreenInvoiceClient(token=token, http_client=http_client)


def test_config_resolves_production_and_sandbox_urls() -> None:
    assert GreenInvoiceConfig(environment="production").resolved_base_url.endswith("api/v1")
    assert "sandbox" in GreenInvoiceConfig(environment="sandbox").resolved_base_url


def test_authenticate_sends_client_credentials_grant_type() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"access_token": "abc"})

    client = make_client(handler, token=None)
    token = client.authenticate("id", "secret")
    assert token.token == "abc"
    assert seen["path"] == "/api/v1/account/token"
    assert seen["body"] == {"id": "id", "secret": "secret", "grant_type": "client_credentials"}


def test_authenticate_reads_header_token_fallback() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={}, headers={"X-Authorization-Bearer": "header-token"})

    client = make_client(handler, token=None)
    assert client.authenticate("id", "secret").token == "header-token"


def test_request_adds_bearer_header() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler, token="secret-token")
    assert client.verify_credentials() == {"ok": True}
    assert seen["authorization"] == "Bearer secret-token"


def test_create_client_uses_clients_endpoint() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode())
        return httpx.Response(201, json={"id": "client-1"})

    client = make_client(handler)
    result = client.create_client({"name": "Demo", "emails": ["a@example.com"]})
    assert result["id"] == "client-1"
    assert seen == {
        "method": "POST",
        "path": "/api/v1/clients",
        "body": {"name": "Demo", "emails": ["a@example.com"]},
    }


def test_search_clients_adds_search_term() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/clients/search"
        assert json.loads(request.content.decode()) == {"active": True, "search": "demo"}
        return httpx.Response(200, json={"items": []})

    client = make_client(handler)
    assert client.search_clients("demo", active=True) == {"items": []}


def test_build_simple_document_payload_includes_payment_gross_amount() -> None:
    payload = build_simple_document_payload(
        document_type=320,
        client_name="Demo",
        client_email="a@example.com",
        description="Service",
        amount=1000,
        date="2026-06-05",
        payment_method="wire-transfer",
    )
    assert payload["type"] == 320
    assert payload["payment"][0]["type"] == 4
    assert payload["payment"][0]["price"] == 1180


def test_build_simple_document_payload_rejects_unknown_payment_method() -> None:
    with pytest.raises(GreenInvoiceValidationError):
        build_simple_document_payload(
            document_type=320,
            client_name="Demo",
            client_email="a@example.com",
            description="Service",
            amount=100,
            payment_method="barter",
        )


def test_create_document_validates_type() -> None:
    client = make_client(lambda _request: httpx.Response(200, json={}))
    with pytest.raises(GreenInvoiceValidationError):
        client.create_document({"type": 999, "client": {}, "income": []})


def test_list_documents_uses_search_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/documents/search"
        assert json.loads(request.content.decode()) == {"type": 320}
        return httpx.Response(200, json={"items": [{"id": "doc-1"}]})

    client = make_client(handler)
    assert client.list_documents(type=320)["items"][0]["id"] == "doc-1"


def test_cancel_document_uses_cancel_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/documents/doc-1/cancel"
        assert json.loads(request.content.decode()) == {"reason": "mistake"}
        return httpx.Response(200, json={"cancelled": True})

    client = make_client(handler)
    assert client.cancel_document("doc-1", reason="mistake") == {"cancelled": True}


def test_error_raises_with_status_and_body() -> None:
    client = make_client(lambda _request: httpx.Response(403, json={"error": "forbidden"}))
    with pytest.raises(GreenInvoiceError) as exc:
        client.verify_credentials()
    assert exc.value.status_code == 403
    assert exc.value.body == {"error": "forbidden"}


@pytest.mark.asyncio
async def test_async_client_authenticate_and_get_document() -> None:
    seen = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.url.path.endswith("/account/token"):
            return httpx.Response(200, json={"token": "async-token"})
        assert request.headers["Authorization"] == "Bearer async-token"
        return httpx.Response(200, json={"id": "doc-1"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.greeninvoice.co.il/api/v1"
    ) as http_client:
        client = AsyncGreenInvoiceClient(http_client=http_client)
        token = await client.authenticate("id", "secret")
        result = await client.get_document("doc-1")
    assert token.token == "async-token"
    assert result == {"id": "doc-1"}
    assert seen == [("POST", "/api/v1/account/token"), ("GET", "/api/v1/documents/doc-1")]


def test_verify_webhook_hmac_accepts_sha256_prefix() -> None:
    body = b'{"id":"evt-1"}'
    secret = "secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_webhook_hmac(secret=secret, body=body, signature=f"sha256={digest}")
    assert not verify_webhook_hmac(secret=secret, body=body, signature="sha256=bad")
