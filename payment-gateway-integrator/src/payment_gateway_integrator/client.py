"""Typed sync and async client for neutral Israeli payment gateway orchestration."""

from __future__ import annotations

import asyncio
import dataclasses
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
import hashlib
import hmac
import json
import time
from typing import Any, Awaitable, Callable, Dict, Mapping, MutableMapping, Protocol, Sequence, Set, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest


SUPPORTED_GATEWAYS = {"cardcom", "tranzila", "meshulam", "pelecard", "grow"}
SAFE_FALLBACK_REASONS = {"network_timeout", "network_error", "gateway_unavailable", "malformed_response"}
DEFAULT_TIMEOUT_SECONDS = 20
__version__ = "2.2.0"


class PaymentStatus(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    PENDING = "pending"
    REQUIRES_ACTION = "requires_action"
    ERROR = "error"
    REFUNDED = "refunded"
    VOIDED = "voided"
    UNKNOWN = "unknown"


class PaymentGatewayError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "gateway_error",
        gateway: str | None = None,
        retryable: bool = False,
        transaction_id: str | None = None,
        raw: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.gateway = gateway
        self.retryable = retryable
        self.transaction_id = transaction_id
        self.raw = dict(raw or {})


@dataclass(frozen=True)
class Customer:
    name: str = ""
    email: str = ""
    phone: str = ""
    national_id: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "national_id": self.national_id,
        }


@dataclass(frozen=True)
class GatewayConfig:
    name: str
    endpoint_url: str
    api_key: str
    terminal_id: str
    secret: str = ""
    sandbox: bool = True
    enabled: bool = True
    priority: int = 100
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    capabilities: Set[str] = field(default_factory=lambda: {"hosted_checkout"})
    max_installments: int = 1
    supported_currencies: Set[str] = field(default_factory=lambda: {"ILS"})
    extra: Mapping[str, Any] = field(default_factory=dict)

    def normalized_name(self) -> str:
        return normalize_gateway_name(self.name)

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class OrchestrationPolicy:
    allow_fallback: bool = True
    prefer_tokenization: bool = False
    idempotency_ttl_seconds: int = 60 * 60 * 24
    fallback_reasons: Set[str] = field(default_factory=lambda: set(SAFE_FALLBACK_REASONS))
    max_attempts: int = 3
    require_hosted_for_card_entry: bool = True


@dataclass(frozen=True)
class PaymentRequest:
    order_id: str
    amount_agorot: int
    currency: str = "ILS"
    description: str = ""
    customer: Customer = field(default_factory=Customer)
    installments: int = 1
    capture: bool = True
    return_url: str = ""
    notify_url: str = ""
    tokenize: bool = False
    payment_method_token: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    preferred_gateway: str = ""

    def validate(self) -> None:
        if not self.order_id or not self.order_id.strip():
            raise PaymentGatewayError("order_id is required", code="order_id_required")
        if not isinstance(self.amount_agorot, int) or self.amount_agorot < 1:
            raise PaymentGatewayError("amount_agorot must be a positive integer", code="amount_invalid")
        if not self.currency or len(self.currency) != 3:
            raise PaymentGatewayError("currency must be a 3-letter ISO code", code="currency_invalid")
        if self.installments < 1:
            raise PaymentGatewayError("installments must be at least 1", code="installments_invalid")
        if self.tokenize and self.payment_method_token:
            raise PaymentGatewayError("tokenize cannot be combined with payment_method_token", code="token_conflict")
        if self.preferred_gateway and normalize_gateway_name(self.preferred_gateway) not in SUPPORTED_GATEWAYS:
            raise PaymentGatewayError("preferred gateway is not supported", code="gateway_unsupported")

    @property
    def amount_nis(self) -> Decimal:
        return (Decimal(self.amount_agorot) / Decimal(100)).quantize(Decimal("0.01"))


@dataclass(frozen=True)
class PaymentResponse:
    gateway: str
    status: PaymentStatus
    transaction_id: str = ""
    order_id: str = ""
    amount_agorot: int = 0
    currency: str = "ILS"
    approval_code: str = ""
    redirect_url: str = ""
    failure_code: str = ""
    failure_message: str = ""
    token: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict)

    @property
    def approved(self) -> bool:
        return self.status == PaymentStatus.APPROVED

    @property
    def requires_action(self) -> bool:
        return self.status == PaymentStatus.REQUIRES_ACTION


@dataclass(frozen=True)
class RefundRequest:
    transaction_id: str
    amount_agorot: int
    reason: str = ""
    order_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.transaction_id:
            raise PaymentGatewayError("transaction_id is required", code="transaction_id_required")
        if not isinstance(self.amount_agorot, int) or self.amount_agorot < 1:
            raise PaymentGatewayError("amount_agorot must be a positive integer", code="amount_invalid")


@dataclass(frozen=True)
class RefundResponse:
    gateway: str
    status: PaymentStatus
    refund_id: str = ""
    transaction_id: str = ""
    amount_agorot: int = 0
    failure_code: str = ""
    failure_message: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict)


class SyncTransport(Protocol):
    def __call__(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        json_body: Mapping[str, Any] | None,
        timeout: int,
    ) -> Mapping[str, Any]:
        ...


class AsyncTransport(Protocol):
    def __call__(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        json_body: Mapping[str, Any] | None,
        timeout: int,
    ) -> Awaitable[Mapping[str, Any]]:
        ...


def normalize_gateway_name(name: str) -> str:
    value = name.strip().lower().replace("_", "-")
    aliases = {
        "card-com": "cardcom",
        "cardcom": "cardcom",
        "tranzila": "tranzila",
        "meshulam": "meshulam",
        "pele-card": "pelecard",
        "pelecard": "pelecard",
        "grow": "grow",
    }
    if value not in aliases:
        raise PaymentGatewayError(f"unsupported gateway: {name}", code="gateway_unsupported", gateway=name)
    return aliases[value]


def nis_to_agorot(amount: str | Decimal | float | int) -> int:
    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise PaymentGatewayError("amount is not a valid decimal", code="amount_invalid") from exc
    if decimal_amount <= 0:
        raise PaymentGatewayError("amount must be positive", code="amount_invalid")
    quantized = decimal_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if quantized != decimal_amount:
        raise PaymentGatewayError("amount must not have more than two decimal places", code="amount_precision_invalid")
    return int(quantized * 100)


def agorot_to_nis(amount_agorot: int) -> str:
    if amount_agorot < 0:
        raise PaymentGatewayError("amount cannot be negative", code="amount_invalid")
    return f"{Decimal(amount_agorot) / Decimal(100):.2f}"


def format_ils(amount_agorot: int) -> str:
    return f"₪{agorot_to_nis(amount_agorot)}"


def _json_dumps(data: Mapping[str, Any]) -> bytes:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def default_sync_transport(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str],
    json_body: Mapping[str, Any] | None,
    timeout: int,
) -> Mapping[str, Any]:
    body = _json_dumps(json_body or {}) if json_body is not None else None
    request = urlrequest.Request(url=url, data=body, method=method.upper(), headers=dict(headers))
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlrequest.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urlerror.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": raw, "status": exc.code}
        raise PaymentGatewayError("gateway returned HTTP error", code="gateway_http_error", retryable=500 <= exc.code < 600, raw=parsed) from exc
    except TimeoutError as exc:
        raise PaymentGatewayError("network timeout", code="network_timeout", retryable=True) from exc
    except OSError as exc:
        raise PaymentGatewayError("network error", code="network_error", retryable=True) from exc


async def default_async_transport(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str],
    json_body: Mapping[str, Any] | None,
    timeout: int,
) -> Mapping[str, Any]:
    return await asyncio.to_thread(default_sync_transport, method, url, headers=headers, json_body=json_body, timeout=timeout)


class IsraeliPaymentOrchestrator:
    """Synchronous payment orchestrator."""

    def __init__(
        self,
        gateways: Sequence[GatewayConfig],
        *,
        policy: OrchestrationPolicy | None = None,
        transport: SyncTransport | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if not gateways:
            raise PaymentGatewayError("at least one gateway is required", code="gateway_required")
        self.gateways = {config.normalized_name(): config for config in gateways}
        self.policy = policy or OrchestrationPolicy()
        self.transport = transport or default_sync_transport
        self.clock = clock
        self._idempotency_cache: MutableMapping[str, Tuple[float, PaymentResponse]] = {}

    def charge(self, request: PaymentRequest) -> PaymentResponse:
        request.validate()
        key = self.idempotency_key("charge", request)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        attempts = 0
        last_error: PaymentGatewayError | None = None
        for config in self.choose_gateways(request):
            attempts += 1
            if attempts > self.policy.max_attempts:
                break
            try:
                raw = self.transport(
                    "POST",
                    self.endpoint_for(config, "charge"),
                    headers=self.headers_for(config),
                    json_body=self.build_payment_payload(config, request),
                    timeout=config.timeout_seconds,
                )
                response = self.parse_payment_response(config, request, raw)
                self._store_cache(key, response)
                if response.status == PaymentStatus.ERROR and self._can_fallback(response.failure_code, response.transaction_id):
                    last_error = PaymentGatewayError(response.failure_message or "gateway error", code=response.failure_code or "gateway_error", gateway=config.name, retryable=True, transaction_id=response.transaction_id, raw=response.raw)
                    continue
                return response
            except PaymentGatewayError as exc:
                exc.gateway = exc.gateway or config.name
                last_error = exc
                if not self._should_try_next(exc):
                    raise
                continue
        if last_error:
            return PaymentResponse(gateway=last_error.gateway or "", status=PaymentStatus.ERROR, order_id=request.order_id, amount_agorot=request.amount_agorot, currency=request.currency, transaction_id=last_error.transaction_id or "", failure_code=last_error.code, failure_message=str(last_error), raw=last_error.raw)
        raise PaymentGatewayError("no eligible gateway found", code="no_eligible_gateway")

    def authorize(self, request: PaymentRequest) -> PaymentResponse:
        return self.charge(dataclasses.replace(request, capture=False))

    def capture(self, gateway: str, transaction_id: str, amount_agorot: int) -> PaymentResponse:
        if amount_agorot < 1:
            raise PaymentGatewayError("capture amount must be positive", code="amount_invalid")
        config = self.gateways[normalize_gateway_name(gateway)]
        if not config.supports("capture"):
            raise PaymentGatewayError("gateway does not support capture", code="capture_unsupported", gateway=config.name)
        payload = {"transaction_id": transaction_id, "amount_agorot": amount_agorot, "amount": agorot_to_nis(amount_agorot)}
        raw = self.transport("POST", self.endpoint_for(config, "capture"), headers=self.headers_for(config), json_body=payload, timeout=config.timeout_seconds)
        return self.parse_payment_response(config, PaymentRequest(order_id=transaction_id, amount_agorot=amount_agorot), raw)

    def refund(self, gateway: str, request: RefundRequest) -> RefundResponse:
        request.validate()
        config = self.gateways[normalize_gateway_name(gateway)]
        if not config.supports("refund"):
            raise PaymentGatewayError("gateway does not support refund", code="refund_unsupported", gateway=config.name)
        raw = self.transport("POST", self.endpoint_for(config, "refund"), headers=self.headers_for(config), json_body=self.build_refund_payload(config, request), timeout=config.timeout_seconds)
        return self.parse_refund_response(config, request, raw)

    def status(self, gateway: str, transaction_id: str) -> PaymentResponse:
        config = self.gateways[normalize_gateway_name(gateway)]
        if not transaction_id:
            raise PaymentGatewayError("transaction_id is required", code="transaction_id_required", gateway=config.name)
        raw = self.transport("GET", self.endpoint_for(config, "status", transaction_id=transaction_id), headers=self.headers_for(config), json_body=None, timeout=config.timeout_seconds)
        request = PaymentRequest(order_id=transaction_id, amount_agorot=int(raw.get("amount_agorot") or 1))
        return self.parse_payment_response(config, request, raw)

    def choose_gateways(self, request: PaymentRequest) -> list[GatewayConfig]:
        required = self.required_capabilities(request)
        configs = list(self.gateways.values())
        if request.preferred_gateway:
            configs = [self.gateways[normalize_gateway_name(request.preferred_gateway)]]
        eligible = []
        for config in configs:
            if not config.enabled:
                continue
            if request.currency not in config.supported_currencies:
                continue
            if request.installments > 1 and request.installments > config.max_installments:
                continue
            if any(capability not in config.capabilities for capability in required):
                continue
            eligible.append(config)
        if not eligible:
            raise PaymentGatewayError("no eligible gateway found", code="no_eligible_gateway")
        return sorted(eligible, key=lambda item: item.priority)

    def required_capabilities(self, request: PaymentRequest) -> Set[str]:
        required: Set[str] = set()
        if self.policy.require_hosted_for_card_entry and not request.payment_method_token:
            required.add("hosted_checkout")
        if request.installments > 1:
            required.add("installments")
        if request.tokenize:
            required.add("tokenization")
        if request.payment_method_token:
            required.add("token_charge")
        if not request.capture:
            required.add("authorize")
        return required

    def endpoint_for(self, config: GatewayConfig, operation: str, *, transaction_id: str = "") -> str:
        base = config.endpoint_url.rstrip("/")
        gateway = config.normalized_name()
        paths = {
            "cardcom": {"charge": "/api/checkout", "refund": "/api/refund", "status": f"/api/status/{transaction_id}", "capture": "/api/capture"},
            "tranzila": {"charge": "/api/charge", "refund": "/api/refund", "status": f"/api/status/{transaction_id}", "capture": "/api/capture"},
            "meshulam": {"charge": "/api/payment/create", "refund": "/api/payment/refund", "status": f"/api/payment/status/{transaction_id}", "capture": "/api/payment/capture"},
            "pelecard": {"charge": "/PaymentGW/init", "refund": "/PaymentGW/refund", "status": f"/PaymentGW/status/{transaction_id}", "capture": "/PaymentGW/capture"},
            "grow": {"charge": "/api/payments", "refund": "/api/refunds", "status": f"/api/payments/{transaction_id}", "capture": "/api/captures"},
        }
        return base + paths[gateway][operation]

    def headers_for(self, config: GatewayConfig) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "payment-gateway-integrator/2.0.0",
            "Authorization": f"Bearer {config.api_key}",
            "X-Terminal-Id": config.terminal_id,
            "X-Sandbox": "true" if config.sandbox else "false",
        }

    def build_payment_payload(self, config: GatewayConfig, request: PaymentRequest) -> Dict[str, Any]:
        gateway = config.normalized_name()
        customer = request.customer.to_dict()
        amount = agorot_to_nis(request.amount_agorot)
        if gateway == "cardcom":
            return {"TerminalNumber": config.terminal_id, "ApiName": config.api_key, "Amount": amount, "CoinID": "1" if request.currency == "ILS" else request.currency, "ReturnValue": request.order_id, "ProductName": request.description, "SuccessRedirectUrl": request.return_url, "ErrorRedirectUrl": request.return_url, "IndicatorUrl": request.notify_url, "NumOfPayments": request.installments, "CreateToken": request.tokenize, "Token": request.payment_method_token, "Capture": request.capture, "Customer": customer, "Metadata": dict(request.metadata)}
        if gateway == "tranzila":
            return {"terminal_name": config.terminal_id, "api_key": config.api_key, "sum": amount, "currency": "1" if request.currency == "ILS" else request.currency, "order_id": request.order_id, "contact": request.customer.name, "email": request.customer.email, "phone": request.customer.phone, "cred_type": "1" if request.capture else "J2", "npay": request.installments, "notify_url": request.notify_url, "return_url": request.return_url, "tokenize": request.tokenize, "token": request.payment_method_token, "metadata": dict(request.metadata)}
        if gateway == "meshulam":
            return {"pageCode": config.terminal_id, "apiKey": config.api_key, "sum": amount, "description": request.description, "transactionId": request.order_id, "fullName": request.customer.name, "email": request.customer.email, "phone": request.customer.phone, "successUrl": request.return_url, "notifyUrl": request.notify_url, "maxPayments": request.installments, "tokenize": request.tokenize, "token": request.payment_method_token, "capture": request.capture, "metadata": dict(request.metadata)}
        if gateway == "pelecard":
            return {"Terminal": config.terminal_id, "User": config.extra.get("user", config.api_key), "Password": config.extra.get("password", config.secret), "Total": str(request.amount_agorot), "Currency": "1" if request.currency == "ILS" else request.currency, "OrderId": request.order_id, "ParamX": request.description, "GoodURL": request.return_url, "ErrorURL": request.return_url, "NotifyURL": request.notify_url, "MaxPayments": request.installments, "CreateToken": request.tokenize, "Token": request.payment_method_token, "J2": not request.capture, "Customer": customer, "Metadata": dict(request.metadata)}
        if gateway == "grow":
            return {"terminal_id": config.terminal_id, "api_key": config.api_key, "amount": amount, "currency": request.currency, "order_id": request.order_id, "description": request.description, "customer": customer, "installments": request.installments, "success_url": request.return_url, "cancel_url": request.return_url, "webhook_url": request.notify_url, "tokenize": request.tokenize, "payment_token": request.payment_method_token, "capture": request.capture, "metadata": dict(request.metadata)}
        raise PaymentGatewayError("unsupported gateway", code="gateway_unsupported", gateway=config.name)

    def build_refund_payload(self, config: GatewayConfig, request: RefundRequest) -> Dict[str, Any]:
        gateway = config.normalized_name()
        amount = agorot_to_nis(request.amount_agorot)
        if gateway == "cardcom":
            return {"TerminalNumber": config.terminal_id, "ApiName": config.api_key, "TransactionId": request.transaction_id, "Amount": amount, "Reason": request.reason}
        if gateway == "tranzila":
            return {"terminal_name": config.terminal_id, "transaction_id": request.transaction_id, "sum": amount, "reason": request.reason}
        if gateway == "meshulam":
            return {"pageCode": config.terminal_id, "processId": request.transaction_id, "sum": amount, "reason": request.reason}
        if gateway == "pelecard":
            return {"Terminal": config.terminal_id, "TransactionId": request.transaction_id, "Total": str(request.amount_agorot), "Reason": request.reason}
        if gateway == "grow":
            return {"payment_id": request.transaction_id, "amount": amount, "reason": request.reason, "order_id": request.order_id}
        raise PaymentGatewayError("unsupported gateway", code="gateway_unsupported", gateway=config.name)

    def parse_payment_response(self, config: GatewayConfig, request: PaymentRequest, raw: Mapping[str, Any]) -> PaymentResponse:
        gateway = config.normalized_name()
        data = dict(raw)
        transaction_id = first_string(data, "transaction_id", "TransactionId", "LowProfileId", "PelecardTransactionId", "payment_id", "processId", "index", "id")
        redirect_url = first_string(data, "redirect_url", "Url", "URL", "url", "checkout_url", "payment_url")
        approval_code = first_string(data, "approval_code", "ApprovalCode", "authnr", "AuthNumber")
        token = first_string(data, "token", "Token", "cardToken", "payment_token")
        failure_code = first_string(data, "failure_code", "error_code", "ResponseCode", "Response", "StatusCode", "ResultCode", "code")
        failure_message = first_string(data, "failure_message", "Description", "message", "error", "ErrorMessage", "result")
        status = self.normalize_status(gateway, data, redirect_url=redirect_url)
        if status in {PaymentStatus.APPROVED, PaymentStatus.REQUIRES_ACTION, PaymentStatus.PENDING}:
            failure_code = ""
            failure_message = ""
        return PaymentResponse(gateway=gateway, status=status, transaction_id=transaction_id, order_id=request.order_id, amount_agorot=request.amount_agorot, currency=request.currency, approval_code=approval_code, redirect_url=redirect_url, failure_code=failure_code, failure_message=failure_message, token=token, raw=data)

    def parse_refund_response(self, config: GatewayConfig, request: RefundRequest, raw: Mapping[str, Any]) -> RefundResponse:
        data = dict(raw)
        gateway = config.normalized_name()
        status = self.normalize_status(gateway, data)
        if status == PaymentStatus.APPROVED:
            status = PaymentStatus.REFUNDED
        refund_id = first_string(data, "refund_id", "RefundId", "credit_transaction_id", "id")
        failure_code = "" if status in {PaymentStatus.REFUNDED, PaymentStatus.APPROVED} else first_string(data, "failure_code", "error_code", "ResponseCode", "StatusCode", "code")
        failure_message = "" if status in {PaymentStatus.REFUNDED, PaymentStatus.APPROVED} else first_string(data, "failure_message", "message", "Description", "error")
        return RefundResponse(gateway=gateway, status=status, refund_id=refund_id, transaction_id=request.transaction_id, amount_agorot=request.amount_agorot, failure_code=failure_code, failure_message=failure_message, raw=data)

    def normalize_status(self, gateway: str, raw: Mapping[str, Any], *, redirect_url: str = "") -> PaymentStatus:
        lowered = {str(key).lower(): value for key, value in raw.items()}
        status_value = str(lowered.get("status", lowered.get("payment_status", ""))).lower()
        success_value = lowered.get("success")
        if redirect_url and status_value not in {"approved", "paid", "success"}:
            return PaymentStatus.REQUIRES_ACTION
        if success_value is True:
            if status_value in {"pending", "created", "open"}:
                return PaymentStatus.REQUIRES_ACTION if redirect_url else PaymentStatus.PENDING
            return PaymentStatus.APPROVED
        if success_value is False:
            return PaymentStatus.ERROR
        success_codes = {"0", "000", "approved", "paid", "success", "ok", "authorized", "captured", "1"}
        decline_codes = {"declined", "denied", "failed", "rejected", "issuer_declined", "insufficient_funds"}
        pending_codes = {"pending", "created", "open", "processing", "in_process"}
        refund_codes = {"refunded", "refund", "credited"}
        code_values = [lowered.get("responsecode"), lowered.get("response"), lowered.get("statuscode"), lowered.get("resultcode"), lowered.get("code"), lowered.get("status"), lowered.get("payment_status")]
        normalized = {str(value).lower() for value in code_values if value is not None and str(value) != ""}
        if normalized & refund_codes:
            return PaymentStatus.REFUNDED
        if normalized & pending_codes:
            return PaymentStatus.PENDING
        if normalized & decline_codes:
            return PaymentStatus.DECLINED
        if normalized & success_codes:
            return PaymentStatus.APPROVED
        return PaymentStatus.ERROR

    def verify_webhook(self, gateway: str, payload: bytes, signature_header: str, *, timestamp: str = "") -> bool:
        config = self.gateways[normalize_gateway_name(gateway)]
        if not config.secret:
            raise PaymentGatewayError("webhook secret is required", code="webhook_secret_required", gateway=config.name)
        signed_payload = payload if not timestamp else f"{timestamp}.".encode("utf-8") + payload
        expected = hmac.new(config.secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        received = signature_header.strip()
        if received.startswith("sha256="):
            received = received.split("=", 1)[1]
        return hmac.compare_digest(received, expected)

    def sign_webhook_payload(self, gateway: str, payload: bytes, *, timestamp: str = "") -> str:
        config = self.gateways[normalize_gateway_name(gateway)]
        signed_payload = payload if not timestamp else f"{timestamp}.".encode("utf-8") + payload
        digest = hmac.new(config.secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def idempotency_key(self, operation: str, request: PaymentRequest) -> str:
        raw = "|".join([operation, request.order_id, str(request.amount_agorot), request.currency, str(request.installments), request.payment_method_token, request.preferred_gateway])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _get_cached(self, key: str) -> PaymentResponse | None:
        item = self._idempotency_cache.get(key)
        if not item:
            return None
        created_at, response = item
        if self.clock() - created_at > self.policy.idempotency_ttl_seconds:
            self._idempotency_cache.pop(key, None)
            return None
        return response

    def _store_cache(self, key: str, response: PaymentResponse) -> None:
        self._idempotency_cache[key] = (self.clock(), response)

    def _should_try_next(self, exc: PaymentGatewayError) -> bool:
        if not self.policy.allow_fallback or exc.transaction_id or not exc.retryable:
            return False
        return exc.code in self.policy.fallback_reasons

    def _can_fallback(self, code: str, transaction_id: str) -> bool:
        if not self.policy.allow_fallback or transaction_id:
            return False
        return code in self.policy.fallback_reasons


class AsyncIsraeliPaymentOrchestrator:
    """Asynchronous payment orchestrator with the same canonical behavior."""

    def __init__(self, gateways: Sequence[GatewayConfig], *, policy: OrchestrationPolicy | None = None, transport: AsyncTransport | None = None, clock: Callable[[], float] = time.time) -> None:
        self._sync = IsraeliPaymentOrchestrator(gateways, policy=policy, transport=lambda *args, **kwargs: {}, clock=clock)
        self.gateways = self._sync.gateways
        self.policy = self._sync.policy
        self.transport = transport or default_async_transport
        self.clock = clock
        self._idempotency_cache: MutableMapping[str, Tuple[float, PaymentResponse]] = {}

    async def charge(self, request: PaymentRequest) -> PaymentResponse:
        request.validate()
        key = self._sync.idempotency_key("charge", request)
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        attempts = 0
        last_error: PaymentGatewayError | None = None
        for config in self._sync.choose_gateways(request):
            attempts += 1
            if attempts > self.policy.max_attempts:
                break
            try:
                raw = await self.transport("POST", self._sync.endpoint_for(config, "charge"), headers=self._sync.headers_for(config), json_body=self._sync.build_payment_payload(config, request), timeout=config.timeout_seconds)
                response = self._sync.parse_payment_response(config, request, raw)
                self._store_cache(key, response)
                if response.status == PaymentStatus.ERROR and self._sync._can_fallback(response.failure_code, response.transaction_id):
                    last_error = PaymentGatewayError(response.failure_message or "gateway error", code=response.failure_code, gateway=config.name, retryable=True, raw=response.raw)
                    continue
                return response
            except PaymentGatewayError as exc:
                exc.gateway = exc.gateway or config.name
                last_error = exc
                if not self._sync._should_try_next(exc):
                    raise
                continue
        if last_error:
            return PaymentResponse(gateway=last_error.gateway or "", status=PaymentStatus.ERROR, order_id=request.order_id, amount_agorot=request.amount_agorot, currency=request.currency, transaction_id=last_error.transaction_id or "", failure_code=last_error.code, failure_message=str(last_error), raw=last_error.raw)
        raise PaymentGatewayError("no eligible gateway found", code="no_eligible_gateway")

    async def authorize(self, request: PaymentRequest) -> PaymentResponse:
        return await self.charge(dataclasses.replace(request, capture=False))

    async def refund(self, gateway: str, request: RefundRequest) -> RefundResponse:
        request.validate()
        config = self.gateways[normalize_gateway_name(gateway)]
        if not config.supports("refund"):
            raise PaymentGatewayError("gateway does not support refund", code="refund_unsupported", gateway=config.name)
        raw = await self.transport("POST", self._sync.endpoint_for(config, "refund"), headers=self._sync.headers_for(config), json_body=self._sync.build_refund_payload(config, request), timeout=config.timeout_seconds)
        return self._sync.parse_refund_response(config, request, raw)

    async def status(self, gateway: str, transaction_id: str) -> PaymentResponse:
        config = self.gateways[normalize_gateway_name(gateway)]
        raw = await self.transport("GET", self._sync.endpoint_for(config, "status", transaction_id=transaction_id), headers=self._sync.headers_for(config), json_body=None, timeout=config.timeout_seconds)
        request = PaymentRequest(order_id=transaction_id, amount_agorot=int(raw.get("amount_agorot") or 1))
        return self._sync.parse_payment_response(config, request, raw)

    def verify_webhook(self, gateway: str, payload: bytes, signature_header: str, *, timestamp: str = "") -> bool:
        return self._sync.verify_webhook(gateway, payload, signature_header, timestamp=timestamp)

    def sign_webhook_payload(self, gateway: str, payload: bytes, *, timestamp: str = "") -> str:
        return self._sync.sign_webhook_payload(gateway, payload, timestamp=timestamp)

    def _get_cached(self, key: str) -> PaymentResponse | None:
        item = self._idempotency_cache.get(key)
        if not item:
            return None
        created_at, response = item
        if self.clock() - created_at > self.policy.idempotency_ttl_seconds:
            self._idempotency_cache.pop(key, None)
            return None
        return response

    def _store_cache(self, key: str, response: PaymentResponse) -> None:
        self._idempotency_cache[key] = (self.clock(), response)


def first_string(data: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        if key in data and data[key] is not None:
            value = data[key]
            if not isinstance(value, (dict, list)):
                return str(value)
    nested = data.get("data")
    if isinstance(nested, Mapping):
        for key in keys:
            if key in nested and nested[key] is not None:
                value = nested[key]
                if not isinstance(value, (dict, list)):
                    return str(value)
    return ""


def config_from_dict(data: Mapping[str, Any]) -> GatewayConfig:
    return GatewayConfig(
        name=str(data["name"]),
        endpoint_url=str(data["endpoint_url"]),
        api_key=str(data.get("api_key", "")),
        terminal_id=str(data.get("terminal_id", "")),
        secret=str(data.get("secret", "")),
        sandbox=bool(data.get("sandbox", True)),
        enabled=bool(data.get("enabled", True)),
        priority=int(data.get("priority", 100)),
        timeout_seconds=int(data.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)),
        capabilities=set(data.get("capabilities", ["hosted_checkout"])),
        max_installments=int(data.get("max_installments", 1)),
        supported_currencies=set(data.get("supported_currencies", ["ILS"])),
        extra=dict(data.get("extra", {})),
    )


def request_from_dict(data: Mapping[str, Any]) -> PaymentRequest:
    customer_data = data.get("customer", {})
    if not isinstance(customer_data, Mapping):
        raise PaymentGatewayError("customer must be an object", code="customer_invalid")
    amount_agorot = data.get("amount_agorot")
    if amount_agorot is None and "amount" in data:
        amount_agorot = nis_to_agorot(data["amount"])
    return PaymentRequest(
        order_id=str(data["order_id"]),
        amount_agorot=int(amount_agorot),
        currency=str(data.get("currency", "ILS")).upper(),
        description=str(data.get("description", "")),
        customer=Customer(name=str(customer_data.get("name", "")), email=str(customer_data.get("email", "")), phone=str(customer_data.get("phone", "")), national_id=str(customer_data.get("national_id", ""))),
        installments=int(data.get("installments", 1)),
        capture=bool(data.get("capture", True)),
        return_url=str(data.get("return_url", "")),
        notify_url=str(data.get("notify_url", "")),
        tokenize=bool(data.get("tokenize", False)),
        payment_method_token=str(data.get("payment_method_token", "")),
        metadata=dict(data.get("metadata", {})),
        preferred_gateway=str(data.get("preferred_gateway", "")),
    )


def response_to_dict(response: PaymentResponse | RefundResponse) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for field_info in dataclasses.fields(response):
        value = getattr(response, field_info.name)
        result[field_info.name] = value.value if isinstance(value, Enum) else value
    return result


def load_gateway_config_file(path: str) -> list[GatewayConfig]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    gateways = data.get("gateways", data if isinstance(data, list) else [])
    if not isinstance(gateways, list):
        raise PaymentGatewayError("config must contain a gateways list", code="config_invalid")
    return [config_from_dict(item) for item in gateways]


def redact_mapping(data: Mapping[str, Any]) -> Dict[str, Any]:
    sensitive = {"api_key", "secret", "password", "token", "payment_method_token", "cvv", "card_number"}
    redacted: Dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in sensitive:
            redacted[key] = "***REDACTED***"
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted
