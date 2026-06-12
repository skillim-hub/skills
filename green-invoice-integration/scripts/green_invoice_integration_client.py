"""Typed Green Invoice API client with synchronous and asynchronous variants."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Mapping, MutableMapping, Optional

import httpx

PRODUCTION_BASE_URL = "https://api.greeninvoice.co.il/api/v1"
SANDBOX_BASE_URL = "https://sandbox.d.greeninvoice.co.il/api/v1"


class DocumentType(IntEnum):
    PRICE_QUOTE = 10
    ORDER = 100
    DELIVERY_NOTE = 200
    RETURN_NOTE = 210
    TRANSACTION_INVOICE = 300
    TAX_INVOICE = 305
    TAX_INVOICE_RECEIPT = 320
    CREDIT_NOTE = 330
    RECEIPT = 400
    DONATION_RECEIPT = 405
    PURCHASE_ORDER = 500
    DEPOSIT_RECEIPT = 600
    DEPOSIT_WITHDRAWAL = 610


DOCUMENT_TYPE_LABELS: dict[int, str] = {
    10: "Price Quote",
    100: "Order",
    200: "Delivery Note",
    210: "Return Note",
    300: "Transaction Invoice",
    305: "Tax Invoice",
    320: "Tax Invoice-Receipt",
    330: "Credit Note",
    400: "Receipt",
    405: "Donation Receipt",
    500: "Purchase Order",
    600: "Deposit Receipt",
    610: "Deposit Withdrawal",
}

PAYMENT_METHODS: dict[str, int] = {
    "cash": 1,
    "check": 2,
    "credit-card": 3,
    "wire-transfer": 4,
    "paypal": 5,
    "app": 10,
    "other": 11,
}


@dataclass(frozen=True)
class GreenInvoiceConfig:
    """Connection settings for Green Invoice."""

    environment: str = "production"
    base_url: str | None = None
    timeout_seconds: float = 30.0

    @property
    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.environment == "sandbox":
            return SANDBOX_BASE_URL
        if self.environment == "production":
            return PRODUCTION_BASE_URL
        raise ValueError("environment must be 'production' or 'sandbox'")


@dataclass
class AuthToken:
    """Bearer token returned by the API."""

    token: str
    raw: Mapping[str, Any] = field(default_factory=dict)


class GreenInvoiceError(RuntimeError):
    """API error with status and response details."""

    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class GreenInvoiceValidationError(ValueError):
    """Local payload validation error."""


def _extract_token(response: httpx.Response) -> AuthToken:
    payload: Mapping[str, Any]
    try:
        parsed = response.json()
        payload = parsed if isinstance(parsed, Mapping) else {}
    except ValueError:
        payload = {}

    token = (
        str(payload.get("token") or "")
        or str(payload.get("access_token") or "")
        or response.headers.get("X-Authorization-Bearer", "")
        or response.headers.get("Authorization", "").removeprefix("Bearer ")
    ).strip()
    if not token:
        raise GreenInvoiceError("Token response did not contain a bearer token", body=payload)
    return AuthToken(token=token, raw=payload)


def _raise_for_response(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    raise GreenInvoiceError(
        f"Green Invoice API returned HTTP {response.status_code}",
        status_code=response.status_code,
        body=body,
    )


def _normalise_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def validate_document_payload(payload: Mapping[str, Any]) -> None:
    if "type" not in payload:
        raise GreenInvoiceValidationError("Document payload must include 'type'")
    try:
        doc_type = int(payload["type"])
    except (TypeError, ValueError) as exc:
        raise GreenInvoiceValidationError("Document type must be an integer") from exc
    if doc_type not in DOCUMENT_TYPE_LABELS:
        raise GreenInvoiceValidationError(f"Unsupported document type: {doc_type}")
    if "client" not in payload:
        raise GreenInvoiceValidationError("Document payload must include 'client'")
    if "income" not in payload:
        raise GreenInvoiceValidationError("Document payload must include 'income'")


def build_simple_document_payload(
    *,
    document_type: int,
    client_name: str,
    client_email: str,
    description: str,
    amount: float,
    currency: str = "ILS",
    date: str | None = None,
    lang: str = "he",
    vat_rate: float = 0.18,
    payment_method: str | None = None,
    tax_included: bool = False,
) -> dict[str, Any]:
    if document_type not in DOCUMENT_TYPE_LABELS:
        raise GreenInvoiceValidationError(f"Unsupported document type: {document_type}")
    if not client_name:
        raise GreenInvoiceValidationError("client_name is required")
    if not client_email:
        raise GreenInvoiceValidationError("client_email is required")
    if amount <= 0:
        raise GreenInvoiceValidationError("amount must be positive")

    line: dict[str, Any] = {
        "description": description,
        "quantity": 1,
        "price": amount,
        "currency": currency,
        "vatRate": vat_rate,
    }
    if tax_included:
        line["taxIncludedInPrice"] = True

    payload: dict[str, Any] = {
        "type": document_type,
        "lang": lang,
        "currency": currency,
        "vatType": 0,
        "client": {"name": client_name, "emails": [client_email], "country": "IL"},
        "income": [line],
        "signed": True,
        "attachment": True,
    }
    if date:
        payload["date"] = date
    if payment_method:
        if payment_method not in PAYMENT_METHODS:
            raise GreenInvoiceValidationError(f"Unsupported payment method: {payment_method}")
        gross_amount = amount if tax_included else round(amount * (1 + vat_rate), 2)
        payload["payment"] = [
            {
                "type": PAYMENT_METHODS[payment_method],
                "price": gross_amount,
                "currency": currency,
                **({"date": date} if date else {}),
            }
        ]
    validate_document_payload(payload)
    return payload


def verify_webhook_hmac(
    *,
    secret: str,
    body: bytes,
    signature: str,
    algorithm: str = "sha256",
) -> bool:
    if algorithm != "sha256":
        raise GreenInvoiceValidationError("Only sha256 webhook verification is supported")
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    supplied = signature.removeprefix("sha256=").strip()
    return hmac.compare_digest(expected, supplied)


class GreenInvoiceClient:
    """Synchronous Green Invoice API client."""

    def __init__(
        self,
        token: str | None = None,
        config: GreenInvoiceConfig | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = config or GreenInvoiceConfig()
        self.token = token
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=self.config.resolved_base_url,
            timeout=self.config.timeout_seconds,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "GreenInvoiceClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def authenticate(self, key_id: str, key_secret: str) -> AuthToken:
        response = self._client.post(
            "/account/token",
            json={"id": key_id, "secret": key_secret, "grant_type": "client_credentials"},
        )
        _raise_for_response(response)
        token = _extract_token(response)
        self.token = token.token
        return token

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = self._client.request(
            method.upper(),
            _normalise_path(path),
            json=dict(json_body) if json_body is not None else None,
            params=params,
            headers=headers,
        )
        _raise_for_response(response)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def verify_credentials(self) -> Any:
        return self.request("GET", "/users/me")

    def create_client(self, payload: Mapping[str, Any]) -> Any:
        return self.request("POST", "/clients", json_body=payload)

    def search_clients(self, term: str | None = None, **filters: Any) -> Any:
        payload: dict[str, Any] = dict(filters)
        if term:
            payload["search"] = term
        return self.request("POST", "/clients/search", json_body=payload)

    def get_client(self, client_id: str) -> Any:
        return self.request("GET", f"/clients/{client_id}")

    def update_client(self, client_id: str, payload: Mapping[str, Any]) -> Any:
        return self.request("PUT", f"/clients/{client_id}", json_body=payload)

    def create_document(self, payload: Mapping[str, Any]) -> Any:
        validate_document_payload(payload)
        return self.request("POST", "/documents", json_body=payload)

    def list_documents(self, **filters: Any) -> Any:
        return self.request("POST", "/documents/search", json_body=filters)

    def get_document(self, document_id: str) -> Any:
        return self.request("GET", f"/documents/{document_id}")

    def cancel_document(self, document_id: str, reason: str | None = None, **extra: Any) -> Any:
        payload: MutableMapping[str, Any] = dict(extra)
        if reason:
            payload["reason"] = reason
        return self.request("POST", f"/documents/{document_id}/cancel", json_body=payload)

    def create_payment_link(self, payload: Mapping[str, Any], endpoint: str = "/payments/links") -> Any:
        return self.request("POST", endpoint, json_body=payload)


class AsyncGreenInvoiceClient:
    """Asynchronous Green Invoice API client."""

    def __init__(
        self,
        token: str | None = None,
        config: GreenInvoiceConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config or GreenInvoiceConfig()
        self.token = token
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(
            base_url=self.config.resolved_base_url,
            timeout=self.config.timeout_seconds,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncGreenInvoiceClient":
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.aclose()

    async def authenticate(self, key_id: str, key_secret: str) -> AuthToken:
        response = await self._client.post(
            "/account/token",
            json={"id": key_id, "secret": key_secret, "grant_type": "client_credentials"},
        )
        _raise_for_response(response)
        token = _extract_token(response)
        self.token = token.token
        return token

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = await self._client.request(
            method.upper(),
            _normalise_path(path),
            json=dict(json_body) if json_body is not None else None,
            params=params,
            headers=headers,
        )
        _raise_for_response(response)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    async def verify_credentials(self) -> Any:
        return await self.request("GET", "/users/me")

    async def create_client(self, payload: Mapping[str, Any]) -> Any:
        return await self.request("POST", "/clients", json_body=payload)

    async def search_clients(self, term: str | None = None, **filters: Any) -> Any:
        payload: dict[str, Any] = dict(filters)
        if term:
            payload["search"] = term
        return await self.request("POST", "/clients/search", json_body=payload)

    async def get_document(self, document_id: str) -> Any:
        return await self.request("GET", f"/documents/{document_id}")

    async def create_document(self, payload: Mapping[str, Any]) -> Any:
        validate_document_payload(payload)
        return await self.request("POST", "/documents", json_body=payload)
