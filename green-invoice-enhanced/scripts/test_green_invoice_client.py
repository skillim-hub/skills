from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Callable, Dict, List

import httpx
import pytest

from green_invoice_client import (
    DOCUMENT_TYPES,
    GreenInvoiceAuthenticationError,
    GreenInvoiceClient,
    GreenInvoiceError,
    GreenInvoiceRateLimitError,
)


def make_jwt(exp: int | None = None) -> str:
    header = {"alg": "none", "typ": "JWT"}
    payload: Dict[str, Any] = {}
    if exp is not None:
        payload["exp"] = exp

    def enc(obj: Dict[str, Any]) -> str:
        raw = json.dumps(obj, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{enc(header)}.{enc(payload)}.signature"


def mock_client(handler: Callable[[httpx.Request], httpx.Response], **kwargs: Any) -> Any:
    return GreenInvoiceClient(
        token=kwargs.pop("token", "static-token"),
        key_id=kwargs.pop("key_id", None),
        key_secret=kwargs.pop("key_secret", None),
        base_url="https://api.test.local/api/v1",
        transport=httpx.MockTransport(handler),
        async_transport=httpx.MockTransport(handler),
        retry_base_delay=0,
        max_retries=kwargs.pop("max_retries", 1),
        **kwargs,
    )


def response(status: int = 200, body: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status, json=body if body is not None else {}, headers=headers)


def test_production_and_sandbox_base_urls() -> None:
    prod = GreenInvoiceClient(token="x", environment="production")
    sandbox = GreenInvoiceClient(token="x", environment="sandbox")
    try:
        assert "api.greeninvoice.co.il" in prod.base_url
        assert "sandbox.d.greeninvoice.co.il" in sandbox.base_url
    finally:
        prod.close()
        sandbox.close()


def test_authenticate_from_body_token() -> None:
    token = make_jwt(int(time.time()) + 3600)

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/account/token")
        assert json.loads(request.content) == {"id": "id", "secret": "secret", "grant_type": "client_credentials"}
        return response(200, {"token": token})

    client = mock_client(handler, token=None, key_id="id", key_secret="secret")
    try:
        result = client.authenticate()
        assert result["token"] == token
        assert client.token == token
    finally:
        client.close()


def test_authenticate_from_access_token_field() -> None:
    token = make_jwt(int(time.time()) + 3600)

    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content)["grant_type"] == "client_credentials"
        return response(200, {"accessToken": token, "expiresIn": 3600, "tokenType": "Bearer"})

    client = mock_client(handler, token=None, key_id="id", key_secret="secret")
    try:
        assert client.authenticate()["accessToken"] == token
        assert client.token == token
    finally:
        client.close()


def test_auto_refresh_expired_token() -> None:
    old = make_jwt(int(time.time()) - 10)
    new = make_jwt(int(time.time()) + 3600)
    paths: List[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path.endswith("/account/token"):
            return response(200, {"accessToken": new, "expiresIn": 3600})
        return response(200, {"ok": True, "authorization": request.headers.get("Authorization")})

    client = mock_client(handler, token=old, key_id="id", key_secret="secret")
    try:
        result = client.verify_auth()
        assert result["ok"] is True
        assert client.token == new
        assert paths[0].endswith("/account/token")
        assert paths[1].endswith("/users/me")
    finally:
        client.close()


def test_refresh_once_after_401() -> None:
    new = make_jwt(int(time.time()) + 3600)
    calls = {"me": 0, "auth": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/account/token"):
            calls["auth"] += 1
            return response(200, {"accessToken": new, "expiresIn": 3600})
        calls["me"] += 1
        if calls["me"] == 1:
            return response(401, {"message": "expired"})
        return response(200, {"id": "user"})

    client = mock_client(handler, token="bad", key_id="id", key_secret="secret")
    try:
        assert client.verify_auth()["id"] == "user"
        assert calls == {"me": 2, "auth": 1}
    finally:
        client.close()


@pytest.mark.parametrize("doc_type", sorted(DOCUMENT_TYPES))
def test_each_document_type_create_get_round_trip(doc_type: int) -> None:
    created = {"id": f"doc-{doc_type}", "type": doc_type, "number": 1000 + doc_type}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path.endswith("/documents"):
            payload = json.loads(request.content.decode())
            assert payload["type"] == doc_type
            return response(200, created)
        if request.method == "GET" and request.url.path.endswith(f"/documents/doc-{doc_type}"):
            return response(200, created)
        return response(404, {"message": "not found"})

    client = mock_client(handler)
    try:
        doc = client.create_document({"type": doc_type, "date": "2026-05-31", "client": {"name": "A"}, "income": []})
        assert doc["id"] == f"doc-{doc_type}"
        assert client.get_document(doc["id"])["number"] == 1000 + doc_type
    finally:
        client.close()


def test_search_documents_pagination_payload() -> None:
    requests: List[Dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode()))
        return response(200, {"items": [{"id": "doc1"}], "page": requests[-1]["page"], "pageSize": requests[-1]["pageSize"], "total": 1})

    client = mock_client(handler)
    try:
        result = client.search_documents({"page": 1, "pageSize": 50})
        assert result["page"] == 1
        assert requests[0]["pageSize"] == 50
    finally:
        client.close()


@pytest.mark.parametrize("method_name,path", [
    ("list_businesses", "/businesses"),
    ("search_businesses", "/businesses/search"),
    ("create_client", "/clients"),
    ("get_client", "/clients/cli1"),
    ("update_client", "/clients/cli1"),
    ("delete_client", "/clients/cli1"),
    ("search_clients", "/clients/search"),
    ("create_item", "/items"),
    ("get_item", "/items/item1"),
    ("update_item", "/items/item1"),
    ("search_items", "/items/search"),
    ("list_webhooks", "/webhooks"),
    ("register_webhook", "/webhooks"),
    ("delete_webhook", "/webhooks/wh1"),
    ("create_expense", "/expenses"),
    ("get_expense", "/expenses/exp1"),
    ("search_expenses", "/expenses/search"),
])
def test_endpoint_method_paths(method_name: str, path: str) -> None:
    seen: List[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return response(200, {"ok": True})

    client = mock_client(handler)
    try:
        if method_name.startswith("search_"):
            getattr(client, method_name)({"page": 0})
        elif method_name.startswith("create_") or method_name == "register_webhook":
            getattr(client, method_name)({"name": "x", "url": "https://example.test/hook"})
        elif method_name.startswith("update_client"):
            getattr(client, method_name)("cli1", {"name": "x"})
        elif method_name.startswith("update_item"):
            getattr(client, method_name)("item1", {"description": "x"})
        elif method_name == "get_client":
            getattr(client, method_name)("cli1")
        elif method_name == "get_item":
            getattr(client, method_name)("item1")
        elif method_name == "delete_client":
            getattr(client, method_name)("cli1")
        elif method_name == "delete_webhook":
            getattr(client, method_name)("wh1")
        elif method_name == "get_expense":
            getattr(client, method_name)("exp1")
        else:
            getattr(client, method_name)()
        assert seen[0].endswith(path)
    finally:
        client.close()


@pytest.mark.parametrize("status,exc_type", [
    (400, GreenInvoiceError),
    (401, GreenInvoiceAuthenticationError),
    (403, GreenInvoiceError),
    (404, GreenInvoiceError),
    (409, GreenInvoiceError),
    (422, GreenInvoiceError),
    (429, GreenInvoiceRateLimitError),
    (500, GreenInvoiceError),
])
def test_error_handling_per_status_code(status: int, exc_type: type[Exception]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return response(status, {"message": f"status {status}"})

    client = mock_client(handler, max_retries=0)
    try:
        with pytest.raises(exc_type):
            client.verify_auth()
    finally:
        client.close()


def test_rate_limit_retry_behavior() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return response(429, {"message": "rate"}, {"Retry-After": "0"})
        return response(200, {"ok": True})

    client = mock_client(handler, max_retries=2)
    try:
        assert client.verify_auth()["ok"] is True
        assert calls["count"] == 2
    finally:
        client.close()


def test_5xx_retry_behavior() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return response(502, {"message": "bad gateway"})
        return response(200, {"items": []})

    client = mock_client(handler, max_retries=2)
    try:
        assert client.search_documents({"page": 0})["items"] == []
        assert calls["count"] == 2
    finally:
        client.close()


def test_webhook_signature_verification_plain_hex() -> None:
    body = b'{"event":"document.created","id":"evt1"}'
    secret = "shared"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert GreenInvoiceClient.verify_webhook_signature(body, signature, secret)


def test_webhook_signature_verification_prefixed() -> None:
    body = b'{"event":"document.created","id":"evt1"}'
    secret = "shared"
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert GreenInvoiceClient.verify_webhook_signature(body, signature, secret)


def test_webhook_signature_verification_rejects_modified_body() -> None:
    body = b'{"event":"document.created","id":"evt1"}'
    secret = "shared"
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert not GreenInvoiceClient.verify_webhook_signature(body + b" ", signature, secret)


def test_record_payment_creates_receipt_document() -> None:
    captured: Dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content.decode()))
        return response(200, {"id": "receipt1", "type": 400})

    client = mock_client(handler)
    try:
        result = client.record_payment(
            client={"id": "cli1", "name": "Client"},
            payment=[{"type": 4, "date": "2026-05-31", "price": 100, "currency": "ILS"}],
            date="2026-05-31",
            linked_document_ids=["doc1"],
        )
        assert result["type"] == 400
        assert captured["linkedDocumentIds"] == ["doc1"]
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_verify_auth() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return response(200, {"id": "async-user"})

    client = mock_client(handler)
    try:
        assert (await client.async_verify_auth())["id"] == "async-user"
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_async_create_document() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode())
        return response(200, {"id": "doc-async", "type": payload["type"]})

    client = mock_client(handler)
    try:
        result = await client.async_create_document({"type": 320, "date": "2026-05-31", "client": {"name": "A"}, "income": []})
        assert result == {"id": "doc-async", "type": 320}
    finally:
        await client.aclose()
