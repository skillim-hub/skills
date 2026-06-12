#!/usr/bin/env python3
"""Typed Green Invoice (Morning) API client.

The module provides a synchronous and asynchronous HTTP client with:
- JWT authentication and refresh.
- Retry with exponential backoff, jitter, and Retry-After support.
- TypedDict request and response shapes.
- Structured logging hooks.
- Webhook signature verification.

Install runtime dependency:

    python -m pip install httpx

Environment variables used by GreenInvoiceClient.from_env():

    GREEN_INVOICE_ENV=production|sandbox
    GREEN_INVOICE_BASE_URL=https://api.greeninvoice.co.il/api/v1
    GREEN_INVOICE_KEY_ID=replace-with-key-id
    GREEN_INVOICE_KEY_SECRET=replace-with-key-secret
"""

from __future__ import annotations

import asyncio
import base64
import email.utils
import hashlib
import hmac
import json
import logging
import os
import random
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Literal, Mapping, MutableMapping, Optional, Sequence, TypedDict, Union, cast

import httpx


PRODUCTION_BASE_URL = "https://api.greeninvoice.co.il/api/v1"
SANDBOX_BASE_URL = "https://sandbox.d.greeninvoice.co.il/api/v1"

DocumentType = Literal[10, 100, 200, 210, 300, 305, 320, 330, 400, 405, 500, 600, 610]
PaymentType = Literal[-1, 0, 1, 2, 3, 4, 5, 10, 11]
EnvironmentName = Literal["production", "sandbox"]

DOCUMENT_TYPES: Dict[int, str] = {
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

PAYMENT_TYPES: Dict[int, str] = {
    -1: "Unpaid",
    0: "Withholding Tax",
    1: "Cash",
    2: "Check",
    3: "Credit Card",
    4: "Bank Transfer",
    5: "PayPal",
    10: "Payment App",
    11: "Other",
}


class TokenResponse(TypedDict, total=False):
    """Authentication response."""

    token: str
    accessToken: str
    expires: int
    exp: int
    expiresIn: int
    tokenType: str


class ClientPayload(TypedDict, total=False):
    """Client create/update payload."""

    id: str
    name: str
    emails: List[str]
    active: bool
    department: str
    taxId: str
    accountingKey: str
    paymentTerms: int
    bankName: str
    bankBranch: str
    bankAccount: str
    address: str
    city: str
    zip: str
    country: str
    category: int
    subCategory: int
    phone: str
    fax: str
    mobile: str
    remarks: str
    contactPerson: str
    labels: List[str]
    add: bool
    self: bool


class DiscountPayload(TypedDict, total=False):
    """Document-level discount."""

    amount: float
    type: Literal["sum", "percentage"]


class IncomeLinePayload(TypedDict, total=False):
    """Income line item."""

    catalogNum: str
    description: str
    quantity: float
    price: float
    currency: str
    currencyRate: float
    vatRate: float
    vatType: int
    itemId: str


class PaymentPayload(TypedDict, total=False):
    """Payment row."""

    type: PaymentType
    subType: int
    date: str
    price: float
    currency: str
    currencyRate: float
    quantity: float
    bankName: str
    bankBranch: str
    bankAccount: str
    chequeNum: str
    cardType: int
    cardNum: str
    dealType: int
    numPayments: int
    firstPayment: float
    appType: int


class PaymentPluginPayload(TypedDict, total=False):
    """Payment plugin descriptor."""

    id: str
    group: int
    type: int


class PaymentRequestData(TypedDict, total=False):
    """Payment request configuration."""

    maxPayments: int
    plugins: List[PaymentPluginPayload]


class DocumentPayload(TypedDict, total=False):
    """Document creation payload."""

    description: str
    remarks: str
    footer: str
    emailContent: str
    type: DocumentType
    date: str
    dueDate: str
    lang: Literal["he", "en"]
    currency: str
    vatType: int
    discount: DiscountPayload
    rounding: bool
    signed: bool
    attachment: bool
    maxPayments: int
    client: ClientPayload
    income: List[IncomeLinePayload]
    payment: List[PaymentPayload]
    linkedDocumentIds: List[str]
    linkedPaymentId: str
    linkType: Literal["link", "cancel"]
    paymentRequestData: PaymentRequestData


class SearchPayload(TypedDict, total=False):
    """Generic search payload."""

    page: int
    pageSize: int
    number: int
    type: List[int]
    status: List[int]
    paymentTypes: List[int]
    fromDate: str
    toDate: str
    clientId: str
    clientName: str
    description: str
    download: bool
    sort: str
    name: str
    active: bool
    email: str
    contactPerson: str
    labels: List[str]
    taxId: str
    supplierName: str


class ItemPayload(TypedDict, total=False):
    """Catalog item payload."""

    id: str
    catalogNum: str
    description: str
    price: float
    currency: str
    vatType: int
    active: bool


class ExpensePayload(TypedDict, total=False):
    """Expense payload."""

    date: str
    description: str
    amount: float
    currency: str
    vat: float
    supplierName: str
    supplierTaxId: str
    category: int


class WebhookPayload(TypedDict, total=False):
    """Webhook registration payload."""

    url: str
    events: List[str]
    secret: str
    active: bool


JsonObject = Dict[str, Any]
JsonMapping = Mapping[str, Any]


class GreenInvoiceError(Exception):
    """Base exception for Green Invoice API failures."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, response: Optional[JsonObject] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class GreenInvoiceAuthenticationError(GreenInvoiceError):
    """Raised when authentication fails."""


class GreenInvoiceRateLimitError(GreenInvoiceError):
    """Raised when rate limit retries are exhausted."""


class JsonLogFormatter(logging.Formatter):
    """Small JSON log formatter for structured stdlib logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("method", "url", "status_code", "attempt", "elapsed_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _jwt_exp(token: str) -> Optional[int]:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload = json.loads(_base64url_decode(parts[1]).decode("utf-8"))
        exp = payload.get("exp")
        return int(exp) if exp is not None else None
    except Exception:
        return None


def _retry_after_seconds(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            parsed = email.utils.parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return max(0.0, (parsed - datetime.now(timezone.utc)).total_seconds())
        except Exception:
            return None


class GreenInvoiceClient:
    """Green Invoice API client with sync and async methods.

    Parameters:
        key_id: API key id for token acquisition.
        key_secret: API key secret for token acquisition.
        token: Existing bearer access token. If omitted, the client authenticates lazily.
        environment: `production` or `sandbox`.
        base_url: Explicit base URL. Overrides environment.
        timeout: HTTP timeout in seconds.
        max_retries: Retry count for 429 and 5xx responses.
        retry_base_delay: Base exponential backoff delay in seconds.
        token_refresh_margin: Refresh JWT this many seconds before expiry.
        transport: Optional httpx transport for tests.
        async_transport: Optional async httpx transport for tests.
        logger: Optional stdlib logger.
    """

    def __init__(
        self,
        *,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
        token: Optional[str] = None,
        environment: EnvironmentName = "production",
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_base_delay: float = 0.5,
        token_refresh_margin: int = 60,
        transport: Optional[httpx.BaseTransport] = None,
        async_transport: Optional[httpx.AsyncBaseTransport] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.key_id = key_id
        self.key_secret = key_secret
        self.token = token
        self.token_expiry = _jwt_exp(token) if token else None
        self.environment = environment
        self.base_url = (base_url or (SANDBOX_BASE_URL if environment == "sandbox" else PRODUCTION_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.token_refresh_margin = token_refresh_margin
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        self.logger = logger or logging.getLogger("green_invoice_client")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, transport=transport)
        self._async_client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout, transport=async_transport)

    @classmethod
    def from_env(cls) -> "GreenInvoiceClient":
        """Create a client from environment variables."""

        env = os.getenv("GREEN_INVOICE_ENV", "production").lower()
        environment: EnvironmentName = "sandbox" if env == "sandbox" else "production"
        return cls(
            key_id=os.getenv("GREEN_INVOICE_KEY_ID"),
            key_secret=os.getenv("GREEN_INVOICE_KEY_SECRET"),
            token=os.getenv("GREEN_INVOICE_TOKEN"),
            environment=environment,
            base_url=os.getenv("GREEN_INVOICE_BASE_URL"),
        )

    def close(self) -> None:
        """Close the underlying synchronous HTTP client."""

        self._client.close()

    async def aclose(self) -> None:
        """Close the underlying asynchronous HTTP client."""

        await self._async_client.aclose()

    def __enter__(self) -> "GreenInvoiceClient":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    async def __aenter__(self) -> "GreenInvoiceClient":
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.aclose()

    def _token_needs_refresh(self) -> bool:
        if not self.token:
            return True
        if self.token_expiry is None:
            return False
        return time.time() >= (self.token_expiry - self.token_refresh_margin)

    def _auth_payload(self) -> JsonObject:
        if not self.key_id or not self.key_secret:
            raise GreenInvoiceAuthenticationError("API key id and secret are required for authentication")
        return {"id": self.key_id, "secret": self.key_secret, "grant_type": "client_credentials"}

    def authenticate(self) -> TokenResponse:
        """Authenticate and store a bearer access token."""

        response = self._request("POST", "/account/token", json_body=self._auth_payload(), auth=False, allow_auth_retry=False)
        token = cast(Optional[str], response.get("accessToken") or response.get("token") or response.get("access_token"))
        if not token:
            raise GreenInvoiceAuthenticationError("Authentication response did not contain accessToken or token", response=response)
        with self._lock:
            self.token = token
            expires_in = response.get("expiresIn") or response.get("expires_in")
            if expires_in:
                self.token_expiry = int(time.time()) + int(expires_in)
            else:
                self.token_expiry = int(response.get("expires") or response.get("exp") or _jwt_exp(token) or 0) or _jwt_exp(token)
        return cast(TokenResponse, response)

    async def async_authenticate(self) -> TokenResponse:
        """Asynchronously authenticate and store a bearer access token."""

        response = await self._arequest("POST", "/account/token", json_body=self._auth_payload(), auth=False, allow_auth_retry=False)
        token = cast(Optional[str], response.get("accessToken") or response.get("token") or response.get("access_token"))
        if not token:
            raise GreenInvoiceAuthenticationError("Authentication response did not contain accessToken or token", response=response)
        self.token = token
        expires_in = response.get("expiresIn") or response.get("expires_in")
        if expires_in:
            self.token_expiry = int(time.time()) + int(expires_in)
        else:
            self.token_expiry = int(response.get("expires") or response.get("exp") or _jwt_exp(token) or 0) or _jwt_exp(token)
        return cast(TokenResponse, response)

    def _ensure_token(self) -> None:
        if not self._token_needs_refresh():
            return
        with self._lock:
            if self._token_needs_refresh():
                self.authenticate()

    async def _async_ensure_token(self) -> None:
        if not self._token_needs_refresh():
            return
        async with self._async_lock:
            if self._token_needs_refresh():
                await self.async_authenticate()

    def _headers(self, auth: bool) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth:
            self._ensure_token()
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _async_headers(self, auth: bool) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth:
            await self._async_ensure_token()
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _raise_for_response(self, response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        try:
            body = cast(JsonObject, response.json())
        except Exception:
            body = {"message": response.text}
        message = str(body.get("message") or body.get("error") or f"HTTP {response.status_code}")
        if response.status_code == 401:
            raise GreenInvoiceAuthenticationError(message, status_code=response.status_code, response=body)
        if response.status_code == 429:
            raise GreenInvoiceRateLimitError(message, status_code=response.status_code, response=body)
        raise GreenInvoiceError(message, status_code=response.status_code, response=body)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[JsonMapping] = None,
        auth: bool = True,
        allow_auth_retry: bool = True,
    ) -> JsonObject:
        last_response: Optional[httpx.Response] = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            headers = self._headers(auth)
            start = time.perf_counter()
            response = self._client.request(method, path, headers=headers, json=json_body)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.debug(
                "green_invoice_api_request",
                extra={"method": method, "url": str(response.request.url), "status_code": response.status_code, "attempt": attempt + 1, "elapsed_ms": elapsed_ms},
            )
            if response.status_code == 401 and auth and allow_auth_retry and self.key_id and self.key_secret:
                with self._lock:
                    self.token = None
                    self.token_expiry = None
                self.authenticate()
                allow_auth_retry = False
                continue
            if response.status_code == 429 or 500 <= response.status_code <= 599:
                last_response = response
                if attempt < attempts - 1:
                    retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
                    delay = retry_after if retry_after is not None else self.retry_base_delay * (2 ** attempt) + random.uniform(0, self.retry_base_delay)
                    time.sleep(delay)
                    continue
            self._raise_for_response(response)
            if not response.content:
                data: JsonObject = {}
            else:
                data = cast(JsonObject, response.json())
            header_token = response.headers.get("X-Authorization-Bearer") or response.headers.get("x-authorization-bearer")
            if header_token and "token" not in data:
                data["token"] = header_token
            return data
        assert last_response is not None
        self._raise_for_response(last_response)
        return {}

    async def _arequest(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[JsonMapping] = None,
        auth: bool = True,
        allow_auth_retry: bool = True,
    ) -> JsonObject:
        last_response: Optional[httpx.Response] = None
        attempts = self.max_retries + 1
        for attempt in range(attempts):
            headers = await self._async_headers(auth)
            start = time.perf_counter()
            response = await self._async_client.request(method, path, headers=headers, json=json_body)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.logger.debug(
                "green_invoice_api_request",
                extra={"method": method, "url": str(response.request.url), "status_code": response.status_code, "attempt": attempt + 1, "elapsed_ms": elapsed_ms},
            )
            if response.status_code == 401 and auth and allow_auth_retry and self.key_id and self.key_secret:
                async with self._async_lock:
                    self.token = None
                    self.token_expiry = None
                await self.async_authenticate()
                allow_auth_retry = False
                continue
            if response.status_code == 429 or 500 <= response.status_code <= 599:
                last_response = response
                if attempt < attempts - 1:
                    retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
                    delay = retry_after if retry_after is not None else self.retry_base_delay * (2 ** attempt) + random.uniform(0, self.retry_base_delay)
                    await asyncio.sleep(delay)
                    continue
            self._raise_for_response(response)
            if not response.content:
                data: JsonObject = {}
            else:
                data = cast(JsonObject, response.json())
            header_token = response.headers.get("X-Authorization-Bearer") or response.headers.get("x-authorization-bearer")
            if header_token and "token" not in data:
                data["token"] = header_token
            return data
        assert last_response is not None
        self._raise_for_response(last_response)
        return {}

    def verify_auth(self) -> JsonObject:
        """Return the authenticated user profile."""

        return self._request("GET", "/users/me")

    async def async_verify_auth(self) -> JsonObject:
        """Asynchronously return the authenticated user profile."""

        return await self._arequest("GET", "/users/me")

    def list_businesses(self) -> JsonObject:
        """List businesses available to the authenticated user."""

        return self._request("GET", "/businesses")

    async def async_list_businesses(self) -> JsonObject:
        """Asynchronously list businesses available to the authenticated user."""

        return await self._arequest("GET", "/businesses")

    def search_businesses(self, payload: SearchPayload) -> JsonObject:
        """Search businesses."""

        return self._request("POST", "/businesses/search", json_body=payload)

    async def async_search_businesses(self, payload: SearchPayload) -> JsonObject:
        """Asynchronously search businesses."""

        return await self._arequest("POST", "/businesses/search", json_body=payload)

    def create_document(self, payload: DocumentPayload) -> JsonObject:
        """Create and issue a document."""

        return self._request("POST", "/documents", json_body=payload)

    async def async_create_document(self, payload: DocumentPayload) -> JsonObject:
        """Asynchronously create and issue a document."""

        return await self._arequest("POST", "/documents", json_body=payload)

    def get_document(self, document_id: str) -> JsonObject:
        """Return a document by id."""

        return self._request("GET", f"/documents/{document_id}")

    async def async_get_document(self, document_id: str) -> JsonObject:
        """Asynchronously return a document by id."""

        return await self._arequest("GET", f"/documents/{document_id}")

    def search_documents(self, payload: SearchPayload) -> JsonObject:
        """Search documents with filters and pagination."""

        return self._request("POST", "/documents/search", json_body=payload)

    async def async_search_documents(self, payload: SearchPayload) -> JsonObject:
        """Asynchronously search documents with filters and pagination."""

        return await self._arequest("POST", "/documents/search", json_body=payload)

    def close_document(self, document_id: str, payload: Optional[JsonMapping] = None) -> JsonObject:
        """Close an open document."""

        return self._request("POST", f"/documents/{document_id}/close", json_body=payload or {})

    async def async_close_document(self, document_id: str, payload: Optional[JsonMapping] = None) -> JsonObject:
        """Asynchronously close an open document."""

        return await self._arequest("POST", f"/documents/{document_id}/close", json_body=payload or {})

    def get_document_download_links(self, document_id: str) -> JsonObject:
        """Return signed download links for a document."""

        return self._request("GET", f"/documents/{document_id}/download/links")

    async def async_get_document_download_links(self, document_id: str) -> JsonObject:
        """Asynchronously return signed download links for a document."""

        return await self._arequest("GET", f"/documents/{document_id}/download/links")

    def email_document(self, document_id: str, payload: JsonMapping) -> JsonObject:
        """Email a document to recipients."""

        return self._request("POST", f"/documents/{document_id}/email", json_body=payload)

    async def async_email_document(self, document_id: str, payload: JsonMapping) -> JsonObject:
        """Asynchronously email a document to recipients."""

        return await self._arequest("POST", f"/documents/{document_id}/email", json_body=payload)

    def create_client(self, payload: ClientPayload) -> JsonObject:
        """Create a client."""

        return self._request("POST", "/clients", json_body=payload)

    async def async_create_client(self, payload: ClientPayload) -> JsonObject:
        """Asynchronously create a client."""

        return await self._arequest("POST", "/clients", json_body=payload)

    def get_client(self, client_id: str) -> JsonObject:
        """Return a client by id."""

        return self._request("GET", f"/clients/{client_id}")

    async def async_get_client(self, client_id: str) -> JsonObject:
        """Asynchronously return a client by id."""

        return await self._arequest("GET", f"/clients/{client_id}")

    def update_client(self, client_id: str, payload: ClientPayload) -> JsonObject:
        """Update a client."""

        return self._request("PUT", f"/clients/{client_id}", json_body=payload)

    async def async_update_client(self, client_id: str, payload: ClientPayload) -> JsonObject:
        """Asynchronously update a client."""

        return await self._arequest("PUT", f"/clients/{client_id}", json_body=payload)

    def delete_client(self, client_id: str) -> JsonObject:
        """Delete or deactivate a client when the API permits it."""

        return self._request("DELETE", f"/clients/{client_id}")

    async def async_delete_client(self, client_id: str) -> JsonObject:
        """Asynchronously delete or deactivate a client when the API permits it."""

        return await self._arequest("DELETE", f"/clients/{client_id}")

    def search_clients(self, payload: SearchPayload) -> JsonObject:
        """Search clients."""

        return self._request("POST", "/clients/search", json_body=payload)

    async def async_search_clients(self, payload: SearchPayload) -> JsonObject:
        """Asynchronously search clients."""

        return await self._arequest("POST", "/clients/search", json_body=payload)

    def list_clients(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """List clients via the search endpoint."""

        return self.search_clients({"page": page, "pageSize": page_size})

    async def async_list_clients(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """Asynchronously list clients via the search endpoint."""

        return await self.async_search_clients({"page": page, "pageSize": page_size})

    def associate_client_documents(self, client_id: str, document_ids: Sequence[str]) -> JsonObject:
        """Associate documents with a client."""

        return self._request("POST", f"/clients/{client_id}/assoc", json_body={"documentIds": list(document_ids)})

    async def async_associate_client_documents(self, client_id: str, document_ids: Sequence[str]) -> JsonObject:
        """Asynchronously associate documents with a client."""

        return await self._arequest("POST", f"/clients/{client_id}/assoc", json_body={"documentIds": list(document_ids)})

    def create_item(self, payload: ItemPayload) -> JsonObject:
        """Create a catalog item."""

        return self._request("POST", "/items", json_body=payload)

    async def async_create_item(self, payload: ItemPayload) -> JsonObject:
        """Asynchronously create a catalog item."""

        return await self._arequest("POST", "/items", json_body=payload)

    def get_item(self, item_id: str) -> JsonObject:
        """Return a catalog item by id."""

        return self._request("GET", f"/items/{item_id}")

    async def async_get_item(self, item_id: str) -> JsonObject:
        """Asynchronously return a catalog item by id."""

        return await self._arequest("GET", f"/items/{item_id}")

    def update_item(self, item_id: str, payload: ItemPayload) -> JsonObject:
        """Update a catalog item."""

        return self._request("PUT", f"/items/{item_id}", json_body=payload)

    async def async_update_item(self, item_id: str, payload: ItemPayload) -> JsonObject:
        """Asynchronously update a catalog item."""

        return await self._arequest("PUT", f"/items/{item_id}", json_body=payload)

    def search_items(self, payload: SearchPayload) -> JsonObject:
        """Search catalog items."""

        return self._request("POST", "/items/search", json_body=payload)

    async def async_search_items(self, payload: SearchPayload) -> JsonObject:
        """Asynchronously search catalog items."""

        return await self._arequest("POST", "/items/search", json_body=payload)

    def list_items(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """List catalog items via the search endpoint."""

        return self.search_items({"page": page, "pageSize": page_size})

    async def async_list_items(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """Asynchronously list catalog items via the search endpoint."""

        return await self.async_search_items({"page": page, "pageSize": page_size})

    def list_webhooks(self) -> JsonObject:
        """List webhook registrations."""

        return self._request("GET", "/webhooks")

    async def async_list_webhooks(self) -> JsonObject:
        """Asynchronously list webhook registrations."""

        return await self._arequest("GET", "/webhooks")

    def register_webhook(self, payload: WebhookPayload) -> JsonObject:
        """Register a webhook endpoint."""

        return self._request("POST", "/webhooks", json_body=payload)

    async def async_register_webhook(self, payload: WebhookPayload) -> JsonObject:
        """Asynchronously register a webhook endpoint."""

        return await self._arequest("POST", "/webhooks", json_body=payload)

    def delete_webhook(self, webhook_id: str) -> JsonObject:
        """Delete a webhook registration."""

        return self._request("DELETE", f"/webhooks/{webhook_id}")

    async def async_delete_webhook(self, webhook_id: str) -> JsonObject:
        """Asynchronously delete a webhook registration."""

        return await self._arequest("DELETE", f"/webhooks/{webhook_id}")

    def create_expense(self, payload: ExpensePayload) -> JsonObject:
        """Create an expense."""

        return self._request("POST", "/expenses", json_body=payload)

    async def async_create_expense(self, payload: ExpensePayload) -> JsonObject:
        """Asynchronously create an expense."""

        return await self._arequest("POST", "/expenses", json_body=payload)

    def get_expense(self, expense_id: str) -> JsonObject:
        """Return an expense by id."""

        return self._request("GET", f"/expenses/{expense_id}")

    async def async_get_expense(self, expense_id: str) -> JsonObject:
        """Asynchronously return an expense by id."""

        return await self._arequest("GET", f"/expenses/{expense_id}")

    def search_expenses(self, payload: SearchPayload) -> JsonObject:
        """Search expenses."""

        return self._request("POST", "/expenses/search", json_body=payload)

    async def async_search_expenses(self, payload: SearchPayload) -> JsonObject:
        """Asynchronously search expenses."""

        return await self._arequest("POST", "/expenses/search", json_body=payload)

    def list_expenses(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """List expenses via the search endpoint."""

        return self.search_expenses({"page": page, "pageSize": page_size})

    async def async_list_expenses(self, page: int = 0, page_size: int = 25) -> JsonObject:
        """Asynchronously list expenses via the search endpoint."""

        return await self.async_search_expenses({"page": page, "pageSize": page_size})

    def record_payment(
        self,
        *,
        client: ClientPayload,
        payment: Sequence[PaymentPayload],
        date: str,
        currency: str = "ILS",
        linked_document_ids: Optional[Sequence[str]] = None,
        description: str = "Payment receipt",
        remarks: str = "",
    ) -> JsonObject:
        """Record a payment by creating a receipt document (`type` 400)."""

        payload: DocumentPayload = {
            "type": 400,
            "date": date,
            "lang": "he",
            "currency": currency,
            "client": client,
            "payment": list(payment),
            "linkedDocumentIds": list(linked_document_ids or []),
            "linkType": "link",
            "description": description,
            "remarks": remarks,
            "signed": True,
            "attachment": True,
        }
        return self.create_document(payload)

    async def async_record_payment(
        self,
        *,
        client: ClientPayload,
        payment: Sequence[PaymentPayload],
        date: str,
        currency: str = "ILS",
        linked_document_ids: Optional[Sequence[str]] = None,
        description: str = "Payment receipt",
        remarks: str = "",
    ) -> JsonObject:
        """Asynchronously record a payment by creating a receipt document (`type` 400)."""

        payload: DocumentPayload = {
            "type": 400,
            "date": date,
            "lang": "he",
            "currency": currency,
            "client": client,
            "payment": list(payment),
            "linkedDocumentIds": list(linked_document_ids or []),
            "linkType": "link",
            "description": description,
            "remarks": remarks,
            "signed": True,
            "attachment": True,
        }
        return await self.async_create_document(payload)

    @staticmethod
    def verify_webhook_signature(raw_body: Union[bytes, str], signature: str, secret: str) -> bool:
        """Verify a webhook HMAC-SHA256 signature.

        Args:
            raw_body: Exact raw request body bytes. A string is encoded as UTF-8.
            signature: Received signature. Plain hex and `sha256=<hex>` are accepted.
            secret: Shared webhook secret.

        Returns:
            True when the signature matches; otherwise False.
        """

        body_bytes = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
        received = signature.strip()
        if received.startswith("sha256="):
            received = received.split("=", 1)[1]
        expected = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, received)


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configure root logging with the JSON formatter."""

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers[:] = [handler]
    root_logger.setLevel(level)


__all__ = [
    "GreenInvoiceClient",
    "GreenInvoiceError",
    "GreenInvoiceAuthenticationError",
    "GreenInvoiceRateLimitError",
    "JsonLogFormatter",
    "configure_json_logging",
    "DOCUMENT_TYPES",
    "PAYMENT_TYPES",
    "DocumentPayload",
    "ClientPayload",
    "PaymentPayload",
    "IncomeLinePayload",
    "ItemPayload",
    "ExpensePayload",
    "WebhookPayload",
]
